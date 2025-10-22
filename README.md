# LOINC Web Semantic Chunker

A CLI tool that downloads LOINC content via official APIs, chunks it based on structured fields, and stores the data in both SQLite database and CSV format.

## Features

- **Multiple API Support**: Access LOINC data through three different APIs
  - NLM Clinical Tables API (no authentication required)
  - LOINC FHIR API (requires LOINC credentials)
  - LOINC Search API (requires LOINC credentials)
- **Intelligent Chunking**: Organized content extraction based on structured field groups
- **Dual Storage**: SQLite database and CSV export
- **Batch Processing**: Process multiple codes from file
- **Query Management**: Search and manage stored content
- **Progress Tracking**: Visual progress bars and detailed error reporting

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
- Dependencies: requests, beautifulsoup4, click, lxml

## API Options

### NLM Clinical Tables API (Default)
- **Authentication**: None required
- **Best for**: Quick access without credentials
- **Usage**: `--api nlm` (default)

### LOINC FHIR API
- **Authentication**: LOINC username/password required
- **Best for**: HL7 FHIR-compliant access
- **Usage**: `--api fhir -u <username> -p <password>`
- **URL**: https://fhir.loinc.org

### LOINC Search API
- **Authentication**: LOINC username/password required
- **Best for**: Comprehensive LOINC database fields
- **Usage**: `--api search -u <username> -p <password>`
- **URL**: https://loinc.regenstrief.org/searchapi

## Usage

Once installed, the `loinc-chunker` command will be available.

### Download LOINC Content

Download content for one or more LOINC codes:

```bash
# Single code using NLM API (default, no auth required)
loinc-chunker download 2160-0

# Multiple codes
loinc-chunker download 2160-0 2339-0 2345-7

# Using FHIR API with credentials
loinc-chunker download 2160-0 --api fhir -u myuser -p mypass

# Using Search API
loinc-chunker download 2160-0 --api search -u myuser -p mypass

# Custom database and CSV paths
loinc-chunker download 2160-0 --db custom.db --csv custom.csv

# Force re-download existing codes
loinc-chunker download 2160-0 --force

# Skip CSV export (database only)
loinc-chunker download 2160-0 --skip-csv

# Skip database storage (CSV only)
loinc-chunker download 2160-0 --skip-db
```

### Authentication with Environment Variables

Instead of passing credentials on command line, set environment variables:

```bash
export LOINC_USERNAME="your_username"
export LOINC_PASSWORD="your_password"

# Now you can use FHIR or Search API without -u and -p
loinc-chunker download 2160-0 --api fhir
```

### Batch Processing

Download multiple codes from a text file (one code per line):

```bash
# Using default NLM API
loinc-chunker batch codes.txt

# Using FHIR API with credentials
loinc-chunker batch codes.txt --api fhir -u myuser -p mypass
```

Example `codes.txt`:
```
2160-0
2339-0
2345-7
718-7
2093-3
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
2160-0,https://loinc.org/2160-0,Basic Information,"COMPONENT: Creatinine | PROPERTY: Mass concentration...",2025-10-22 12:34:56
```

## How It Works

1. **API Access**: Connects to selected LOINC API (NLM, FHIR, or Search)
2. **Data Retrieval**: Fetches structured LOINC data for each code
3. **Content Chunking**:
   - **FHIR API**: Organizes by FHIR parameters (name, display, coding, etc.)
   - **Search API**: Groups by field categories (Basic Info, Names, Classification, Status)
   - **NLM API**: Separates into Basic Information and Technical Details
   - Each chunk represents a logical grouping of related LOINC fields
4. **Storage**:
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
- `--api TYPE`: API type: fhir, search, or nlm (default: nlm)
- `--username, -u`: LOINC username (for FHIR/Search APIs)
- `--password, -p`: LOINC password (for FHIR/Search APIs)
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
- `--api TYPE`: API type: fhir, search, or nlm (default: nlm)
- `--username, -u`: LOINC username (for FHIR/Search APIs)
- `--password, -p`: LOINC password (for FHIR/Search APIs)
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
# Use different APIs for comparison
loinc-chunker download 2160-0 --api nlm --db nlm.db
loinc-chunker download 2160-0 --api fhir -u user -p pass --db fhir.db

# Use custom database location
loinc-chunker download 2160-0 --db ./data/loinc.db --csv ./data/loinc.csv

# Only save to database, skip CSV
loinc-chunker download 2160-0 --skip-csv

# Re-download and update existing code
loinc-chunker download 2160-0 --force

# Longer timeout for slow connections
loinc-chunker download 2160-0 --timeout 60

# Use environment variables for authentication
export LOINC_USERNAME="myuser"
export LOINC_PASSWORD="mypass"
loinc-chunker download 2160-0 --api search
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

If no content is extracted:
1. Verify the LOINC code exists by checking https://loinc.org/<your-code>
2. Try a different API: `--api nlm`, `--api fhir`, or `--api search`
3. Check if authentication is required for your chosen API

### Authentication Errors

If you get 401/403 errors with FHIR or Search API:
1. Verify your LOINC credentials are correct
2. Check if your LOINC account has API access enabled
3. Try the NLM API which doesn't require authentication: `--api nlm`

## Development

### Project Structure

```
loinc-web-semantic-chunker/
├── loinc_chunker/
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # CLI interface with Click
│   ├── api_client.py     # API client for LOINC APIs
│   ├── chunker.py        # Content chunking for API responses
│   ├── storage.py        # SQLite and CSV storage
│   └── scraper.py        # (Legacy) Web scraping functionality
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Modern package configuration
├── setup.py             # Legacy package setup
├── example_codes.txt    # Sample LOINC codes for testing
└── README.md            # This file
```

### Running Tests

```bash
# Test with a known LOINC code using NLM API (no auth needed)
loinc-chunker download 2160-0

# Verify the output
loinc-chunker query 2160-0

# Test batch processing
loinc-chunker batch example_codes.txt
```

## License

[Your License Here]

## Contributing

Contributions are welcome! Please submit issues and pull requests.

## Acknowledgments

- LOINC® is a registered trademark of Regenstrief Institute, Inc.
- This tool is for educational and research purposes
