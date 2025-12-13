"""Web scraper module for downloading LOINC content."""

import requests
from typing import Optional
from bs4 import BeautifulSoup


class LoincScraper:
    """Scraper for LOINC.org web content."""

    BASE_URL = "https://loinc.org"

    def __init__(self, timeout: int = 30):
        """Initialize the LOINC scraper.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def download_loinc_page(self, loinc_code: str) -> Optional[BeautifulSoup]:
        """Download and parse a LOINC page.

        Args:
            loinc_code: The LOINC code to download

        Returns:
            BeautifulSoup object with parsed HTML, or None if failed
        """
        url = f"{self.BASE_URL}/{loinc_code}"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'lxml')
            return soup

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return None

    def get_url_for_code(self, loinc_code: str) -> str:
        """Get the full URL for a LOINC code.

        Args:
            loinc_code: The LOINC code

        Returns:
            Full URL string
        """
        return f"{self.BASE_URL}/{loinc_code}"

    def close(self):
        """Close the session."""
        self.session.close()
