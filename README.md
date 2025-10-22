# LOINC Web Semantic Chunker

A CLI tool that downloads web content from LOINC.org, chunks it using structural elements, and stores the data in both SQLite database and CSV format.

## Features

- Download content from LOINC.org for any LOINC code
- Intelligent chunking based on structural HTML elements (headings, sections, tables)
- Dual storage: SQLite database and CSV export
- Batch processing from file
- Query and manage stored content
- Progress tracking and error handling

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd loinc-web-semantic-chunker

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Usage

Once installed, the `loinc-chunker` command will be available.

### Download LOINC Content

Download content for one or more LOINC codes:

```bash
# Single code
loinc-chunker download 2160-0

# Multiple codes
loinc-chunker download 2160-0 2339-0 2345-7

# Custom database and CSV paths
loinc-chunker download 2160-0 --db custom.db --csv custom.csv

# Force re-download existing codes
loinc-chunker download 2160-0 --force

# Skip CSV export (database only)
loinc-chunker download 2160-0 --skip-csv

# Skip database storage (CSV only)
loinc-chunker download 2160-0 --skip-db
```

### Batch Processing

Download multiple codes from a text file (one code per line):

```bash
loinc-chunker batch codes.txt
```

Example `codes.txt`:
```
2160-0
2339-0
2345-7
```

### Query Stored Content

View stored content for a specific LOINC code:

```bash
loinc-chunker query 2160-0
```

### List Stored Codes

See all LOINC codes in the database:

```bash
loinc-chunker list-codes
```

### Delete a Code

Remove all data for a specific LOINC code:

```bash
loinc-chunker delete 2160-0
```

## Data Structure

### SQLite Database Schema

The tool creates a table `loinc_content` with the following columns:

- `id`: Auto-incrementing primary key
- `loinc_code`: The LOINC code (indexed)
- `url`: Source URL (https://loinc.org/<loinc_code>)
- `content_section`: Section name (from HTML headings/structure)
- `content`: Text content of the section
- `date`: Timestamp when downloaded
- `created_at`: Row creation timestamp

### CSV Format

The CSV file contains the same fields (except `id` and `created_at`):

```csv
loinc_code,url,content_section,content,date
2160-0,https://loinc.org/2160-0,Main Content,"...",2025-10-22 12:34:56
```

## How It Works

1. **Web Scraping**: Downloads HTML content from `https://loinc.org/<loinc_code>`
2. **Content Chunking**:
   - Identifies structural elements (h1-h6, sections, articles)
   - Chunks content based on these elements
   - Extracts text from paragraphs, lists, tables, and divs
   - Cleans and normalizes text
3. **Storage**:
   - Saves chunks to SQLite database with timestamps
   - Exports to CSV format
   - Prevents duplicate downloads (unless `--force` is used)

## Command Reference

### Global Options

- `--help`: Show help message
- `--version`: Show version

### Commands

#### `download`
Download and chunk LOINC content

Options:
- `--db PATH`: SQLite database file (default: loinc_content.db)
- `--csv PATH`: CSV output file (default: loinc_content.csv)
- `--timeout SECONDS`: Request timeout (default: 30)
- `--skip-csv`: Skip CSV export
- `--skip-db`: Skip database storage
- `--force`: Re-download existing codes

#### `query`
Query stored content for a LOINC code

Options:
- `--db PATH`: SQLite database file (default: loinc_content.db)

#### `list-codes`
List all stored LOINC codes

Options:
- `--db PATH`: SQLite database file (default: loinc_content.db)

#### `delete`
Delete a LOINC code from database

Options:
- `--db PATH`: SQLite database file (default: loinc_content.db)

#### `batch`
Download codes from a file

Options:
- `--db PATH`: SQLite database file (default: loinc_content.db)
- `--csv PATH`: CSV output file (default: loinc_content.csv)
- `--timeout SECONDS`: Request timeout (default: 30)

## Examples

### Complete Workflow

```bash
# 1. Download some LOINC codes
loinc-chunker download 2160-0 2339-0 2345-7

# 2. List what's stored
loinc-chunker list-codes

# 3. Query specific code
loinc-chunker query 2160-0

# 4. Batch download from file
echo -e "2160-0\n2339-0\n2345-7" > codes.txt
loinc-chunker batch codes.txt

# 5. Delete a code
loinc-chunker delete 2160-0
```

### Advanced Usage

```bash
# Use custom database location
loinc-chunker download 2160-0 --db ./data/loinc.db --csv ./data/loinc.csv

# Only save to database, skip CSV
loinc-chunker download 2160-0 --skip-csv

# Re-download and update existing code
loinc-chunker download 2160-0 --force

# Longer timeout for slow connections
loinc-chunker download 2160-0 --timeout 60
```

## Troubleshooting

### Network Issues

If downloads fail due to network issues, try increasing the timeout:

```bash
loinc-chunker download 2160-0 --timeout 60
```

### Database Locked

If you get a "database is locked" error, make sure no other process is accessing the database file.

### No Content Extracted

If no content is extracted, the LOINC code might not exist or the page structure might have changed. Check the URL manually: `https://loinc.org/<your-code>`

## Development

### Project Structure

```
loinc-web-semantic-chunker/
├── loinc_chunker/
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # CLI interface
│   ├── scraper.py        # Web scraping functionality
│   ├── chunker.py        # Content chunking logic
│   └── storage.py        # Database and CSV storage
├── requirements.txt      # Python dependencies
├── setup.py             # Package setup
└── README.md            # This file
```

### Running Tests

```bash
# Test with a known LOINC code
loinc-chunker download 2160-0

# Verify the output
loinc-chunker query 2160-0
```

## License

[Your License Here]

## Contributing

Contributions are welcome! Please submit issues and pull requests.

## Acknowledgments

- LOINC® is a registered trademark of Regenstrief Institute, Inc.
- This tool is for educational and research purposes
