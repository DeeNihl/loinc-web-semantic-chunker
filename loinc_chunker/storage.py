"""Storage module for saving chunked content to database and CSV."""

import sqlite3
import csv
from datetime import datetime
from typing import List, Dict
from pathlib import Path


class StorageManager:
    """Manages storage of chunked content to SQLite and CSV."""

    def __init__(self, db_path: str = "loinc_content.db", csv_path: str = "loinc_content.csv"):
        """Initialize the storage manager.

        Args:
            db_path: Path to SQLite database file
            csv_path: Path to CSV output file
        """
        self.db_path = db_path
        self.csv_path = csv_path
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database with required schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loinc_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loinc_code TEXT NOT NULL,
                url TEXT NOT NULL,
                content_section TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create index on loinc_code for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_loinc_code
            ON loinc_content(loinc_code)
        ''')

        conn.commit()
        conn.close()

    def save_to_database(self, chunks: List[Dict[str, str]]) -> int:
        """Save chunks to SQLite database.

        Args:
            chunks: List of content chunks

        Returns:
            Number of records inserted
        """
        if not chunks:
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Add date to each chunk
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        records = [
            (
                chunk['loinc_code'],
                chunk['url'],
                chunk['content_section'],
                chunk['content'],
                current_date
            )
            for chunk in chunks
        ]

        cursor.executemany('''
            INSERT INTO loinc_content (loinc_code, url, content_section, content, date)
            VALUES (?, ?, ?, ?, ?)
        ''', records)

        conn.commit()
        rows_inserted = cursor.rowcount
        conn.close()

        return rows_inserted

    def save_to_csv(self, chunks: List[Dict[str, str]], append: bool = True):
        """Save chunks to CSV file.

        Args:
            chunks: List of content chunks
            append: Whether to append to existing file or overwrite
        """
        if not chunks:
            return

        # Add date to each chunk
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if file exists to determine if we need to write headers
        file_exists = Path(self.csv_path).exists()
        mode = 'a' if (append and file_exists) else 'w'

        with open(self.csv_path, mode, newline='', encoding='utf-8') as csvfile:
            fieldnames = ['loinc_code', 'url', 'content_section', 'content', 'date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header if file is new or we're overwriting
            if not file_exists or not append:
                writer.writeheader()

            # Write data
            for chunk in chunks:
                writer.writerow({
                    'loinc_code': chunk['loinc_code'],
                    'url': chunk['url'],
                    'content_section': chunk['content_section'],
                    'content': chunk['content'],
                    'date': current_date
                })

    def get_stored_codes(self) -> List[str]:
        """Get list of LOINC codes already in database.

        Returns:
            List of unique LOINC codes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT DISTINCT loinc_code FROM loinc_content')
        codes = [row[0] for row in cursor.fetchall()]

        conn.close()
        return codes

    def delete_code(self, loinc_code: str) -> int:
        """Delete all entries for a LOINC code from database.

        Args:
            loinc_code: The LOINC code to delete

        Returns:
            Number of rows deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM loinc_content WHERE loinc_code = ?', (loinc_code,))
        conn.commit()
        rows_deleted = cursor.rowcount
        conn.close()

        return rows_deleted

    def query_by_code(self, loinc_code: str) -> List[Dict[str, str]]:
        """Query all chunks for a specific LOINC code.

        Args:
            loinc_code: The LOINC code to query

        Returns:
            List of chunks as dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT loinc_code, url, content_section, content, date
            FROM loinc_content
            WHERE loinc_code = ?
            ORDER BY id
        ''', (loinc_code,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results
