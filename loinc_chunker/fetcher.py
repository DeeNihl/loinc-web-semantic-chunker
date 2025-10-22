"""Module for fetching web content from LOINC.org"""

import requests
from typing import Optional


class LoincFetcher:
    """Fetches web content from LOINC.org for a given LOINC code."""
    
    BASE_URL = "https://loinc.org"
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the LOINC fetcher.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch(self, loinc_code: str) -> tuple[str, str]:
        """
        Fetch content from LOINC.org for the given LOINC code.
        
        Args:
            loinc_code: The LOINC code to fetch (e.g., "2093-3")
            
        Returns:
            Tuple of (url, html_content)
            
        Raises:
            requests.RequestException: If the request fails
        """
        # Clean the LOINC code (remove any whitespace)
        loinc_code = loinc_code.strip()
        
        # Construct URL
        url = f"{self.BASE_URL}/{loinc_code}/"
        
        # Fetch content
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return url, response.text
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
