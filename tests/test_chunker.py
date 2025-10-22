"""Tests for the LOINC Web Semantic Chunker"""

import unittest
import tempfile
import os
import sqlite3
import csv
from pathlib import Path

from loinc_chunker.chunker import StructuralChunker
from loinc_chunker.storage import DatabaseHandler, CSVExporter


# Mock HTML content for testing
MOCK_HTML_SIMPLE = """
<!DOCTYPE html>
<html>
<head><title>Test LOINC</title></head>
<body>
    <section id="test">
        <h1>Test Section</h1>
        <p>Test content</p>
    </section>
</body>
</html>
"""

MOCK_HTML_COMPLEX = """
<!DOCTYPE html>
<html>
<head><title>LOINC 2093-3</title></head>
<body>
    <main>
        <section id="overview">
            <h1>LOINC Code: 2093-3</h1>
            <p>Cholesterol [Mass/volume] in Serum or Plasma</p>
        </section>
        <article id="attributes">
            <h2>Basic Attributes</h2>
            <p>Component: Cholesterol</p>
        </article>
    </main>
</body>
</html>
"""


class TestStructuralChunker(unittest.TestCase):
    """Test the StructuralChunker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.chunker = StructuralChunker()
    
    def test_chunk_simple_html(self):
        """Test chunking simple HTML content."""
        chunks = self.chunker.chunk(MOCK_HTML_SIMPLE, "TEST-1", "http://test.com")
        
        self.assertGreater(len(chunks), 0, "Should create at least one chunk")
        
        # Check chunk structure
        for chunk in chunks:
            self.assertIn('loinc_code', chunk)
            self.assertIn('url', chunk)
            self.assertIn('content_section', chunk)
            self.assertIn('content', chunk)
            self.assertIn('date', chunk)
            
            self.assertEqual(chunk['loinc_code'], "TEST-1")
            self.assertEqual(chunk['url'], "http://test.com")
    
    def test_chunk_complex_html(self):
        """Test chunking complex HTML with multiple sections."""
        chunks = self.chunker.chunk(MOCK_HTML_COMPLEX, "2093-3", "http://test.com")
        
        self.assertGreater(len(chunks), 1, "Should create multiple chunks")
        
        # Verify all chunks have the correct LOINC code
        for chunk in chunks:
            self.assertEqual(chunk['loinc_code'], "2093-3")
    
    def test_chunk_removes_script_tags(self):
        """Test that script tags are removed from content."""
        html_with_script = """
        <html><body>
            <section><p>Content</p><script>alert('test')</script></section>
        </body></html>
        """
        chunks = self.chunker.chunk(html_with_script, "TEST-2", "http://test.com")
        
        # Check that script content is not in any chunk
        for chunk in chunks:
            self.assertNotIn('alert', chunk['content'])


class TestDatabaseHandler(unittest.TestCase):
    """Test the DatabaseHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_create_table(self):
        """Test that the database table is created correctly."""
        with DatabaseHandler(self.db_path) as db:
            pass
        
        # Verify table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='loinc_chunks'")
        result = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(result, "Table should be created")
    
    def test_insert_chunks(self):
        """Test inserting chunks into the database."""
        chunks = [
            {
                'loinc_code': 'TEST-1',
                'url': 'http://test.com',
                'content_section': 'section_1',
                'content': 'Test content',
                'date': '2025-01-01T00:00:00'
            }
        ]
        
        with DatabaseHandler(self.db_path) as db:
            db.insert_chunks(chunks)
        
        # Verify data was inserted
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM loinc_chunks")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1, "Should insert one record")


class TestCSVExporter(unittest.TestCase):
    """Test the CSVExporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary CSV file
        self.temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w')
        self.temp_csv.close()
        self.csv_path = self.temp_csv.name
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.csv_path):
            os.unlink(self.csv_path)
    
    def test_export_chunks(self):
        """Test exporting chunks to CSV."""
        chunks = [
            {
                'loinc_code': 'TEST-1',
                'url': 'http://test.com',
                'content_section': 'section_1',
                'content': 'Test content',
                'date': '2025-01-01T00:00:00'
            },
            {
                'loinc_code': 'TEST-2',
                'url': 'http://test2.com',
                'content_section': 'section_2',
                'content': 'Test content 2',
                'date': '2025-01-02T00:00:00'
            }
        ]
        
        CSVExporter.export_chunks(chunks, self.csv_path)
        
        # Verify CSV was created and has correct content
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2, "Should have 2 rows")
        self.assertEqual(rows[0]['loinc_code'], 'TEST-1')
        self.assertEqual(rows[1]['loinc_code'], 'TEST-2')
    
    def test_export_empty_chunks(self):
        """Test exporting empty chunks list."""
        CSVExporter.export_chunks([], self.csv_path)
        # Should not create file or should create empty file
        # This test just ensures no exception is raised


if __name__ == '__main__':
    unittest.main()
