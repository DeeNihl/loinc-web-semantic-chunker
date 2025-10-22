"""Command-line interface for LOINC content downloader and chunker."""

import click
import sys
from pathlib import Path
from typing import List

from .scraper import LoincScraper
from .chunker import ContentChunker
from .storage import StorageManager


@click.group()
@click.version_option(version='0.1.0')
def main():
    """LOINC Web Semantic Chunker - Download and chunk LOINC web content.

    This tool downloads content from loinc.org, chunks it based on
    structural elements, and stores it in both SQLite database and CSV format.
    """
    pass


@main.command()
@click.argument('loinc_codes', nargs=-1, required=True)
@click.option('--db', default='loinc_content.db', help='SQLite database file path')
@click.option('--csv', default='loinc_content.csv', help='CSV output file path')
@click.option('--timeout', default=30, type=int, help='Request timeout in seconds')
@click.option('--skip-csv', is_flag=True, help='Skip CSV export')
@click.option('--skip-db', is_flag=True, help='Skip database storage')
@click.option('--force', is_flag=True, help='Re-download even if code exists in database')
def download(loinc_codes: tuple, db: str, csv: str, timeout: int, skip_csv: bool, skip_db: bool, force: bool):
    """Download and chunk LOINC content for one or more codes.

    Examples:
        loinc-chunker download 2160-0
        loinc-chunker download 2160-0 2339-0 2345-7
        loinc-chunker download 2160-0 --db custom.db --csv custom.csv
    """
    if skip_csv and skip_db:
        click.echo("Error: Cannot skip both CSV and database storage", err=True)
        sys.exit(1)

    # Initialize components
    scraper = LoincScraper(timeout=timeout)
    chunker = ContentChunker()
    storage = StorageManager(db_path=db, csv_path=csv)

    # Check for existing codes
    if not force:
        existing_codes = set(storage.get_stored_codes())
        codes_to_download = [code for code in loinc_codes if code not in existing_codes]
        skipped = [code for code in loinc_codes if code in existing_codes]

        if skipped:
            click.echo(f"Skipping {len(skipped)} code(s) already in database: {', '.join(skipped)}")
            click.echo("Use --force to re-download existing codes")

        if not codes_to_download:
            click.echo("All codes already exist in database. Nothing to download.")
            return
    else:
        codes_to_download = list(loinc_codes)

    total_chunks = 0
    successful = 0
    failed = []

    with click.progressbar(codes_to_download, label='Downloading LOINC codes') as bar:
        for loinc_code in bar:
            # Download content
            soup = scraper.download_loinc_page(loinc_code)

            if not soup:
                failed.append(loinc_code)
                continue

            # Get URL
            url = scraper.get_url_for_code(loinc_code)

            # Chunk content
            chunks = chunker.chunk_content(soup, loinc_code, url)

            if not chunks:
                click.echo(f"\nWarning: No content chunks extracted for {loinc_code}", err=True)
                failed.append(loinc_code)
                continue

            # Store chunks
            try:
                if not skip_db:
                    storage.save_to_database(chunks)

                if not skip_csv:
                    storage.save_to_csv(chunks, append=True)

                total_chunks += len(chunks)
                successful += 1

            except Exception as e:
                click.echo(f"\nError storing {loinc_code}: {e}", err=True)
                failed.append(loinc_code)

    # Cleanup
    scraper.close()

    # Summary
    click.echo(f"\n{'='*50}")
    click.echo(f"Download complete!")
    click.echo(f"Successful: {successful}/{len(codes_to_download)}")
    click.echo(f"Total chunks extracted: {total_chunks}")

    if not skip_db:
        click.echo(f"Database: {db}")
    if not skip_csv:
        click.echo(f"CSV file: {csv}")

    if failed:
        click.echo(f"\nFailed codes ({len(failed)}): {', '.join(failed)}", err=True)


@main.command()
@click.argument('loinc_code')
@click.option('--db', default='loinc_content.db', help='SQLite database file path')
def query(loinc_code: str, db: str):
    """Query stored content for a LOINC code.

    Example:
        loinc-chunker query 2160-0
    """
    storage = StorageManager(db_path=db)
    results = storage.query_by_code(loinc_code)

    if not results:
        click.echo(f"No data found for LOINC code: {loinc_code}", err=True)
        sys.exit(1)

    click.echo(f"\n{'='*50}")
    click.echo(f"LOINC Code: {loinc_code}")
    click.echo(f"URL: {results[0]['url']}")
    click.echo(f"Total sections: {len(results)}")
    click.echo(f"{'='*50}\n")

    for i, chunk in enumerate(results, 1):
        click.echo(f"Section {i}: {chunk['content_section']}")
        click.echo(f"Content: {chunk['content'][:200]}..." if len(chunk['content']) > 200 else f"Content: {chunk['content']}")
        click.echo(f"Date: {chunk['date']}")
        click.echo("-" * 50)


@main.command()
@click.option('--db', default='loinc_content.db', help='SQLite database file path')
def list_codes(db: str):
    """List all LOINC codes stored in the database.

    Example:
        loinc-chunker list-codes
    """
    storage = StorageManager(db_path=db)
    codes = storage.get_stored_codes()

    if not codes:
        click.echo("No LOINC codes found in database.")
        return

    click.echo(f"\nStored LOINC codes ({len(codes)}):")
    click.echo("-" * 50)
    for code in sorted(codes):
        click.echo(code)


@main.command()
@click.argument('loinc_code')
@click.option('--db', default='loinc_content.db', help='SQLite database file path')
@click.confirmation_option(prompt='Are you sure you want to delete this code?')
def delete(loinc_code: str, db: str):
    """Delete a LOINC code from the database.

    Example:
        loinc-chunker delete 2160-0
    """
    storage = StorageManager(db_path=db)
    rows_deleted = storage.delete_code(loinc_code)

    if rows_deleted > 0:
        click.echo(f"Deleted {rows_deleted} record(s) for LOINC code: {loinc_code}")
    else:
        click.echo(f"No records found for LOINC code: {loinc_code}", err=True)


@main.command()
@click.argument('input_file', type=click.File('r'))
@click.option('--db', default='loinc_content.db', help='SQLite database file path')
@click.option('--csv', default='loinc_content.csv', help='CSV output file path')
@click.option('--timeout', default=30, type=int, help='Request timeout in seconds')
def batch(input_file, db: str, csv: str, timeout: int):
    """Download LOINC codes from a file (one code per line).

    Example:
        loinc-chunker batch codes.txt
    """
    # Read codes from file
    codes = [line.strip() for line in input_file if line.strip()]

    if not codes:
        click.echo("No codes found in input file", err=True)
        sys.exit(1)

    click.echo(f"Found {len(codes)} codes in input file")

    # Use the download command logic
    ctx = click.get_current_context()
    ctx.invoke(download, loinc_codes=tuple(codes), db=db, csv=csv, timeout=timeout,
               skip_csv=False, skip_db=False, force=False)


if __name__ == '__main__':
    main()
