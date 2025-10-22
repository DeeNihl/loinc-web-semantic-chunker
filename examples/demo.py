#!/usr/bin/env python3
"""
Example demonstration script for LOINC Web Semantic Chunker

This script demonstrates the functionality of the chunker using mock HTML content
since network access may not be available in all environments.
"""

import os
import sys
from datetime import datetime

from loinc_chunker.chunker import StructuralChunker
from loinc_chunker.storage import DatabaseHandler, CSVExporter


# Example LOINC HTML content (simplified representation)
EXAMPLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>2093-3 - Cholesterol [Mass/volume] in Serum or Plasma - LOINC</title>
</head>
<body>
    <header>
        <nav>Navigation menu here</nav>
    </header>
    
    <main>
        <section id="overview">
            <h1>LOINC Code: 2093-3</h1>
            <p class="long-name">Cholesterol [Mass/volume] in Serum or Plasma</p>
            <p>Status: ACTIVE</p>
        </section>
        
        <section id="basic-attributes">
            <h2>Basic Attributes</h2>
            <div class="attribute">
                <strong>Component:</strong> Cholesterol
            </div>
            <div class="attribute">
                <strong>Property:</strong> MCnc (Mass concentration)
            </div>
            <div class="attribute">
                <strong>System:</strong> Ser/Plas (Serum or Plasma)
            </div>
            <div class="attribute">
                <strong>Scale:</strong> Qn (Quantitative)
            </div>
            <div class="attribute">
                <strong>Method:</strong> (No method specified)
            </div>
        </section>
        
        <section id="names">
            <h2>Names</h2>
            <h3>Long Common Name</h3>
            <p>Cholesterol [Mass/volume] in Serum or Plasma</p>
            
            <h3>Short Name</h3>
            <p>Cholest SerPl-mCnc</p>
            
            <h3>Display Name</h3>
            <p>Cholesterol (Ser/Plas) [Mass/Vol]</p>
        </section>
        
        <article id="clinical-information">
            <h2>Clinical Information</h2>
            <p>
                Cholesterol is a lipid (fat) that is essential for normal body function. 
                It is a component of cell membranes and is used to make certain hormones 
                and bile acids.
            </p>
            <p>
                High levels of cholesterol in the blood can increase the risk of 
                cardiovascular disease, including heart attack and stroke. The total 
                cholesterol measurement includes both HDL (good) and LDL (bad) cholesterol.
            </p>
            <p>
                Normal total cholesterol levels are generally considered to be less than 
                200 mg/dL (5.2 mmol/L). Levels between 200-239 mg/dL are considered 
                borderline high, and levels of 240 mg/dL and above are considered high.
            </p>
        </article>
        
        <section id="related-codes">
            <h2>Related LOINC Codes</h2>
            <ul>
                <li>2085-9 - Cholesterol in HDL [Mass/volume] in Serum or Plasma</li>
                <li>2089-1 - Cholesterol in LDL [Mass/volume] in Serum or Plasma</li>
                <li>13457-7 - Cholesterol in LDL [Mass/volume] in Serum or Plasma by calculation</li>
                <li>2571-8 - Triglyceride [Mass/volume] in Serum or Plasma</li>
            </ul>
        </section>
        
        <section id="example-units">
            <h2>Example Units</h2>
            <ul>
                <li>mg/dL</li>
                <li>mmol/L</li>
            </ul>
        </section>
    </main>
    
    <footer>
        <p>Copyright LOINC</p>
    </footer>
    
    <script>
        // This script should be removed during chunking
        console.log("Analytics code");
    </script>
</body>
</html>
"""


def print_section(title, width=80):
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(f" {title}")
    print("=" * width)


def print_chunk_summary(chunk, index):
    """Print a summary of a chunk."""
    print(f"\n📄 Chunk {index}:")
    print(f"   Section ID: {chunk['content_section']}")
    print(f"   Length: {len(chunk['content'])} characters")
    
    # Print first 150 characters of content
    preview = chunk['content'][:150].replace('\n', ' ')
    if len(chunk['content']) > 150:
        preview += "..."
    print(f"   Preview: {preview}")


def main():
    """Run the example demonstration."""
    print_section("LOINC Web Semantic Chunker - Example Demonstration")
    
    # Configuration
    loinc_code = "2093-3"
    url = "https://loinc.org/2093-3/"
    db_path = "example_loinc_chunks.db"
    csv_path = "example_loinc_chunks.csv"
    
    print(f"\n📋 Configuration:")
    print(f"   LOINC Code: {loinc_code}")
    print(f"   Source URL: {url}")
    print(f"   Database: {db_path}")
    print(f"   CSV File: {csv_path}")
    
    try:
        # Step 1: Chunk the content
        print_section("Step 1: Chunking HTML Content")
        print("\nProcessing HTML content with structural chunker...")
        
        chunker = StructuralChunker()
        chunks = chunker.chunk(EXAMPLE_HTML, loinc_code, url)
        
        print(f"\n✓ Successfully created {len(chunks)} chunks")
        
        # Display each chunk
        for i, chunk in enumerate(chunks, 1):
            print_chunk_summary(chunk, i)
        
        # Step 2: Save to database
        print_section("Step 2: Saving to SQLite Database")
        print(f"\nCreating database: {db_path}")
        
        with DatabaseHandler(db_path) as db:
            db.insert_chunks(chunks)
        
        print(f"✓ Successfully saved {len(chunks)} chunks to database")
        
        # Verify database content
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM loinc_chunks WHERE loinc_code = ?", (loinc_code,))
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✓ Verified: Database contains {count} records for LOINC code {loinc_code}")
        
        # Step 3: Export to CSV
        print_section("Step 3: Exporting to CSV")
        print(f"\nCreating CSV file: {csv_path}")
        
        CSVExporter.export_chunks(chunks, csv_path)
        
        print(f"✓ Successfully exported {len(chunks)} chunks to CSV")
        
        # Display CSV preview
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"✓ Verified: CSV contains {len(rows)} rows")
        
        # Step 4: Display sample data
        print_section("Step 4: Sample Output Data")
        
        if rows:
            print("\n📊 First row from CSV:")
            first_row = rows[0]
            for key, value in first_row.items():
                if key == 'content':
                    # Truncate content for display
                    display_value = value[:100] + "..." if len(value) > 100 else value
                else:
                    display_value = value
                print(f"   {key}: {display_value}")
        
        # Success summary
        print_section("✅ SUCCESS - All Operations Completed")
        
        print(f"\n📁 Output Files Created:")
        print(f"   • {db_path} ({os.path.getsize(db_path)} bytes)")
        print(f"   • {csv_path} ({os.path.getsize(csv_path)} bytes)")
        
        print(f"\n📊 Summary:")
        print(f"   • LOINC Code: {loinc_code}")
        print(f"   • Total Chunks: {len(chunks)}")
        print(f"   • Database Records: {count}")
        print(f"   • CSV Rows: {len(rows)}")
        
        print("\n💡 Next Steps:")
        print("   1. View the database: sqlite3 example_loinc_chunks.db")
        print("   2. Query chunks: SELECT * FROM loinc_chunks;")
        print("   3. Open CSV file: cat example_loinc_chunks.csv")
        print("   4. Try with real LOINC code: loinc-chunker <loinc_code>")
        
        print("\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
