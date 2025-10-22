"""Module for database operations"""

import sqlite3
import csv
from typing import List, Dict
from pathlib import Path


class DatabaseHandler:
    """Handles SQLite database operations for LOINC chunks."""
    
    def __init__(self, db_path: str = "loinc_chunks.db"):
        """
        Initialize database handler.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Establish database connection and create table if needed."""
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()
        
    def _create_table(self):
        """Create the chunks table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loinc_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loinc_code TEXT NOT NULL,
                url TEXT NOT NULL,
                content_section TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        
        # Create index on loinc_code for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_loinc_code 
            ON loinc_chunks(loinc_code)
        ''')
        
        self.conn.commit()
    
    def insert_chunks(self, chunks: List[Dict[str, str]]):
        """
        Insert chunks into the database.
        
        Args:
            chunks: List of chunk dictionaries
        """
        if not self.conn:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        cursor = self.conn.cursor()
        
        for chunk in chunks:
            cursor.execute('''
                INSERT INTO loinc_chunks (loinc_code, url, content_section, content, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                chunk['loinc_code'],
                chunk['url'],
                chunk['content_section'],
                chunk['content'],
                chunk['date']
            ))
        
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class CSVExporter:
    """Handles CSV export operations for LOINC chunks."""
    
    @staticmethod
    def export_chunks(chunks: List[Dict[str, str]], csv_path: str):
        """
        Export chunks to a CSV file.
        
        Args:
            chunks: List of chunk dictionaries
            csv_path: Path to output CSV file
        """
        if not chunks:
            return
        
        # Ensure parent directory exists
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['loinc_code', 'url', 'content_section', 'content', 'date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for chunk in chunks:
                writer.writerow(chunk)
