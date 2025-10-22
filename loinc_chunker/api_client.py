"""API client module for accessing LOINC content."""

import requests
from typing import Optional, Dict, Any
from enum import Enum
import os


class LoincAPIType(Enum):
    """Supported LOINC API types."""
    FHIR = "fhir"
    SEARCH = "search"
    NLM = "nlm"


class LoincAPIClient:
    """Client for LOINC API access."""

    FHIR_BASE_URL = "https://fhir.loinc.org"
    SEARCH_BASE_URL = "https://loinc.regenstrief.org/searchapi"
    NLM_BASE_URL = "https://clinicaltables.nlm.nih.gov/api/loinc_items/v3"
    WEB_BASE_URL = "https://loinc.org"

    def __init__(self,
                 api_type: str = "fhir",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: int = 30):
        """Initialize the LOINC API client.

        Args:
            api_type: API type to use ('fhir', 'search', or 'nlm')
            username: LOINC username (required for FHIR and Search APIs)
            password: LOINC password (required for FHIR and Search APIs)
            timeout: Request timeout in seconds
        """
        self.api_type = LoincAPIType(api_type.lower())
        self.timeout = timeout
        self.session = requests.Session()

        # Set up authentication if provided
        if username and password:
            self.session.auth = (username, password)

        # Try to get credentials from environment if not provided
        if not username and (self.api_type == LoincAPIType.FHIR or
                            self.api_type == LoincAPIType.SEARCH):
            env_user = os.environ.get('LOINC_USERNAME')
            env_pass = os.environ.get('LOINC_PASSWORD')
            if env_user and env_pass:
                self.session.auth = (env_user, env_pass)

        self.session.headers.update({
            'User-Agent': 'LOINC-Web-Semantic-Chunker/0.1.0',
            'Accept': 'application/json'
        })

    def get_loinc_data(self, loinc_code: str) -> Optional[Dict[str, Any]]:
        """Get LOINC data for a code using the configured API.

        Args:
            loinc_code: The LOINC code to retrieve

        Returns:
            Dictionary with LOINC data, or None if failed
        """
        if self.api_type == LoincAPIType.FHIR:
            return self._get_fhir_data(loinc_code)
        elif self.api_type == LoincAPIType.SEARCH:
            return self._get_search_data(loinc_code)
        elif self.api_type == LoincAPIType.NLM:
            return self._get_nlm_data(loinc_code)
        return None

    def _get_fhir_data(self, loinc_code: str) -> Optional[Dict[str, Any]]:
        """Get data from LOINC FHIR API.

        Args:
            loinc_code: The LOINC code

        Returns:
            FHIR resource data or None
        """
        # Use CodeSystem $lookup operation
        url = f"{self.FHIR_BASE_URL}/CodeSystem/$lookup"
        params = {
            'system': 'http://loinc.org',
            'code': loinc_code
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from FHIR API for {loinc_code}: {e}")
            return None

    def _get_search_data(self, loinc_code: str) -> Optional[Dict[str, Any]]:
        """Get data from LOINC Search API.

        Args:
            loinc_code: The LOINC code

        Returns:
            Search API data or None
        """
        url = f"{self.SEARCH_BASE_URL}/loincs/{loinc_code}"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Search API for {loinc_code}: {e}")
            return None

    def _get_nlm_data(self, loinc_code: str) -> Optional[Dict[str, Any]]:
        """Get data from NLM Clinical Tables API.

        Args:
            loinc_code: The LOINC code

        Returns:
            NLM API data or None
        """
        url = f"{self.NLM_BASE_URL}/search"
        params = {
            'terms': loinc_code,
            'sf': 'LOINC_NUM,COMPONENT,SYSTEM,SCALE_TYP,METHOD_TYP,TIME_ASPCT,PROPERTY,CLASS',
            'df': 'LOINC_NUM,COMPONENT,SYSTEM,SCALE_TYP,METHOD_TYP,TIME_ASPCT,PROPERTY,CLASS,LONG_COMMON_NAME,SHORTNAME,STATUS',
            'maxList': '1'
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # NLM returns [total, [results], None, [field_names]]
            if len(data) >= 2 and data[1]:
                return {
                    'code': loinc_code,
                    'data': data[1][0] if data[1] else None,
                    'fields': data[3] if len(data) > 3 else None
                }
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from NLM API for {loinc_code}: {e}")
            return None

    def get_url_for_code(self, loinc_code: str) -> str:
        """Get the web URL for a LOINC code.

        Args:
            loinc_code: The LOINC code

        Returns:
            Full URL string
        """
        return f"{self.WEB_BASE_URL}/{loinc_code}"

    def close(self):
        """Close the session."""
        self.session.close()
