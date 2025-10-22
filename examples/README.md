# Examples

This directory contains example scripts demonstrating the functionality of the LOINC Web Semantic Chunker.

## demo.py

A comprehensive demonstration script that shows how to use the chunker with mock HTML content.

### Running the Demo

```bash
python examples/demo.py
```

This will:
1. Process example LOINC HTML content (2093-3 - Cholesterol)
2. Chunk the content based on structural elements
3. Save chunks to SQLite database (`example_loinc_chunks.db`)
4. Export chunks to CSV (`example_loinc_chunks.csv`)
5. Display summary information

### What You'll See

The demo creates 7 chunks from the example HTML, showing:
- How sections and articles are identified
- Content extraction and cleaning
- Database schema and storage
- CSV export format

### Output Files

After running the demo, you'll have:
- `example_loinc_chunks.db` - SQLite database with all chunks
- `example_loinc_chunks.csv` - CSV file with the same data

You can inspect these with:
```bash
# View database
sqlite3 example_loinc_chunks.db "SELECT * FROM loinc_chunks;"

# View CSV
cat example_loinc_chunks.csv
```

### Using with Real Data

To use the CLI tool with real LOINC codes (requires internet access):
```bash
loinc-chunker 2093-3 --verbose
```
