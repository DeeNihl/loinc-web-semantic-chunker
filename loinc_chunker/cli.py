"""Command-line interface for LOINC Web Semantic Chunker"""

import argparse
import sys
from pathlib import Path

from .fetcher import LoincFetcher
from .chunker import StructuralChunker
from .storage import DatabaseHandler, CSVExporter


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Download and chunk LOINC web content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s 2093-3
  %(prog)s 2093-3 --output chunks.csv
  %(prog)s 2093-3 --db-path custom.db --csv-path output.csv
        '''
    )
    
    parser.add_argument(
        'loinc_code',
        help='LOINC code to fetch and chunk (e.g., 2093-3)'
    )
    
    parser.add_argument(
        '--db-path',
        default='loinc_chunks.db',
        help='Path to SQLite database file (default: loinc_chunks.db)'
    )
    
    parser.add_argument(
        '--csv-path',
        default='loinc_chunks.csv',
        help='Path to output CSV file (default: loinc_chunks.csv)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Fetch content
        if args.verbose:
            print(f"Fetching content for LOINC code: {args.loinc_code}")
        
        with LoincFetcher(timeout=args.timeout) as fetcher:
            url, html_content = fetcher.fetch(args.loinc_code)
        
        if args.verbose:
            print(f"Successfully fetched content from: {url}")
            print(f"Content size: {len(html_content)} bytes")
        
        # Step 2: Chunk content
        if args.verbose:
            print("Chunking content using structural elements...")
        
        chunker = StructuralChunker()
        chunks = chunker.chunk(html_content, args.loinc_code, url)
        
        if args.verbose:
            print(f"Created {len(chunks)} chunks")
        
        if not chunks:
            print("Warning: No chunks were created from the content", file=sys.stderr)
            return 1
        
        # Step 3: Save to database
        if args.verbose:
            print(f"Saving chunks to database: {args.db_path}")
        
        with DatabaseHandler(args.db_path) as db:
            db.insert_chunks(chunks)
        
        if args.verbose:
            print(f"Successfully saved {len(chunks)} chunks to database")
        
        # Step 4: Export to CSV
        if args.verbose:
            print(f"Exporting chunks to CSV: {args.csv_path}")
        
        CSVExporter.export_chunks(chunks, args.csv_path)
        
        if args.verbose:
            print(f"Successfully exported {len(chunks)} chunks to CSV")
        
        # Summary
        print(f"\nSuccessfully processed LOINC code: {args.loinc_code}")
        print(f"  URL: {url}")
        print(f"  Chunks created: {len(chunks)}")
        print(f"  Database: {args.db_path}")
        print(f"  CSV file: {args.csv_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
