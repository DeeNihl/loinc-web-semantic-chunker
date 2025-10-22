# loinc-web-semantic-chunker

Chunks a LOINC code's webpage using a combination of structural and Semantic chunking

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

The CLI tool downloads web content from loinc.org and chunks it based on structural elements:

```bash
# Basic usage
loinc-chunker <loinc_code>

# With custom output paths
loinc-chunker 2093-3 --db-path my_chunks.db --csv-path my_chunks.csv

# With verbose output
loinc-chunker 2093-3 --verbose
```

### Options

- `loinc_code` - Required: The LOINC code to fetch and chunk (e.g., 2093-3)
- `--db-path` - SQLite database file path (default: loinc_chunks.db)
- `--csv-path` - CSV output file path (default: loinc_chunks.csv)
- `--timeout` - Request timeout in seconds (default: 30)
- `--verbose, -v` - Enable verbose output

### Output Format

The tool generates two outputs:

1. **SQLite Database** with schema:
   - `loinc_code` - The LOINC code
   - `url` - The source URL
   - `content_section` - The section identifier
   - `content` - The text content
   - `date` - Timestamp when chunked

2. **CSV File** with the same columns

## How It Works

1. **Fetches** web content from https://loinc.org/<loinc_code>/
2. **Chunks** the content using structural HTML elements (sections, articles, headings)
3. **Stores** the chunks in both SQLite database and CSV file

The chunker prioritizes structural elements in this order:
- Main content sections (`<section>`, `<article>`, `<main>`)
- Heading-based sections (`<h1>` through `<h6>`)
- Body content as fallback

## Example

```bash
$ loinc-chunker 2093-3 --verbose

Fetching content for LOINC code: 2093-3
Successfully fetched content from: https://loinc.org/2093-3/
Chunking content using structural elements...
Created 6 chunks
Saving chunks to database: loinc_chunks.db
Successfully saved 6 chunks to database
Exporting chunks to CSV: loinc_chunks.csv
Successfully exported 6 chunks to CSV

Successfully processed LOINC code: 2093-3
  URL: https://loinc.org/2093-3/
  Chunks created: 6
  Database: loinc_chunks.db
  CSV file: loinc_chunks.csv
```
