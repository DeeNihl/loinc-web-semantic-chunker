"""Content chunking module for LOINC web pages and API responses."""

from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
import json


class ContentChunker:
    """Chunks LOINC web content from HTML or API responses."""

    def __init__(self):
        """Initialize the content chunker."""
        # Structural elements that define content sections
        self.section_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'article']

    def chunk_api_data(self, api_data: Dict[str, Any], loinc_code: str, url: str,
                       api_type: str = "fhir") -> List[Dict[str, str]]:
        """Chunk content from LOINC API response.

        Args:
            api_data: API response data
            loinc_code: The LOINC code
            url: The source URL
            api_type: Type of API ('fhir', 'search', or 'nlm')

        Returns:
            List of dictionaries with chunked content
        """
        if api_type == "fhir":
            return self._chunk_fhir_data(api_data, loinc_code, url)
        elif api_type == "search":
            return self._chunk_search_data(api_data, loinc_code, url)
        elif api_type == "nlm":
            return self._chunk_nlm_data(api_data, loinc_code, url)
        else:
            # Generic JSON chunking
            return self._chunk_generic_json(api_data, loinc_code, url)

    def _chunk_fhir_data(self, data: Dict[str, Any], loinc_code: str, url: str) -> List[Dict[str, str]]:
        """Chunk FHIR API response data.

        Args:
            data: FHIR response
            loinc_code: The LOINC code
            url: The source URL

        Returns:
            List of content chunks
        """
        chunks = []

        # Extract basic information
        if 'parameter' in data:
            for param in data['parameter']:
                param_name = param.get('name', 'Unknown')

                # Handle different value types
                if 'valueString' in param:
                    chunks.append({
                        'loinc_code': loinc_code,
                        'url': url,
                        'content_section': param_name,
                        'content': param['valueString']
                    })
                elif 'valueCoding' in param:
                    coding = param['valueCoding']
                    content_parts = []
                    if 'display' in coding:
                        content_parts.append(f"Display: {coding['display']}")
                    if 'code' in coding:
                        content_parts.append(f"Code: {coding['code']}")
                    if 'system' in coding:
                        content_parts.append(f"System: {coding['system']}")

                    chunks.append({
                        'loinc_code': loinc_code,
                        'url': url,
                        'content_section': param_name,
                        'content': ' | '.join(content_parts)
                    })
                elif 'part' in param:
                    # Handle nested parameters
                    parts_content = []
                    for part in param['part']:
                        part_name = part.get('name', 'Unknown')
                        if 'valueString' in part:
                            parts_content.append(f"{part_name}: {part['valueString']}")
                        elif 'valueCoding' in part:
                            parts_content.append(f"{part_name}: {part['valueCoding'].get('display', '')}")

                    if parts_content:
                        chunks.append({
                            'loinc_code': loinc_code,
                            'url': url,
                            'content_section': param_name,
                            'content': ' | '.join(parts_content)
                        })

        # If no chunks were created, store the full response
        if not chunks:
            chunks.append({
                'loinc_code': loinc_code,
                'url': url,
                'content_section': 'FHIR Response',
                'content': json.dumps(data, indent=2)
            })

        return chunks

    def _chunk_search_data(self, data: Dict[str, Any], loinc_code: str, url: str) -> List[Dict[str, str]]:
        """Chunk Search API response data.

        Args:
            data: Search API response
            loinc_code: The LOINC code
            url: The source URL

        Returns:
            List of content chunks
        """
        chunks = []

        # Define standard LOINC fields to extract
        field_groups = {
            'Basic Information': ['COMPONENT', 'PROPERTY', 'TIME_ASPCT', 'SYSTEM', 'SCALE_TYP', 'METHOD_TYP'],
            'Names': ['LONG_COMMON_NAME', 'SHORTNAME', 'DisplayName'],
            'Classification': ['CLASS', 'CLASSTYPE'],
            'Status': ['STATUS', 'VersionLastChanged', 'VersionFirstReleased'],
            'Additional Details': ['FORMULA', 'EXAMPLE_UCUM_UNITS', 'EXAMPLE_UNITS', 'ORDER_OBS', 'HL7_FIELD_SUBFIELD_ID']
        }

        for section_name, fields in field_groups.items():
            content_parts = []
            for field in fields:
                if field in data:
                    value = data[field]
                    if value:
                        content_parts.append(f"{field}: {value}")

            if content_parts:
                chunks.append({
                    'loinc_code': loinc_code,
                    'url': url,
                    'content_section': section_name,
                    'content': ' | '.join(content_parts)
                })

        # If no chunks were created, store important fields
        if not chunks:
            chunks.append({
                'loinc_code': loinc_code,
                'url': url,
                'content_section': 'Search API Response',
                'content': json.dumps(data, indent=2)
            })

        return chunks

    def _chunk_nlm_data(self, data: Dict[str, Any], loinc_code: str, url: str) -> List[Dict[str, str]]:
        """Chunk NLM API response data.

        Args:
            data: NLM API response
            loinc_code: The LOINC code
            url: The source URL

        Returns:
            List of content chunks
        """
        chunks = []

        if 'data' in data and data['data']:
            result = data['data']
            fields = data.get('fields', [])

            # Create chunks based on field groups
            if isinstance(result, list) and fields:
                # Map indices to field names
                field_map = {i: field for i, field in enumerate(fields)}

                # Group related fields
                basic_info = []
                technical_info = []

                for i, value in enumerate(result):
                    if value and i in field_map:
                        field_name = field_map[i]
                        entry = f"{field_name}: {value}"

                        if field_name in ['COMPONENT', 'SYSTEM', 'PROPERTY', 'LONG_COMMON_NAME', 'SHORTNAME']:
                            basic_info.append(entry)
                        else:
                            technical_info.append(entry)

                if basic_info:
                    chunks.append({
                        'loinc_code': loinc_code,
                        'url': url,
                        'content_section': 'Basic Information',
                        'content': ' | '.join(basic_info)
                    })

                if technical_info:
                    chunks.append({
                        'loinc_code': loinc_code,
                        'url': url,
                        'content_section': 'Technical Details',
                        'content': ' | '.join(technical_info)
                    })

        # If no chunks were created, store the full response
        if not chunks:
            chunks.append({
                'loinc_code': loinc_code,
                'url': url,
                'content_section': 'NLM API Response',
                'content': json.dumps(data, indent=2)
            })

        return chunks

    def _chunk_generic_json(self, data: Dict[str, Any], loinc_code: str, url: str) -> List[Dict[str, str]]:
        """Chunk generic JSON data.

        Args:
            data: JSON data
            loinc_code: The LOINC code
            url: The source URL

        Returns:
            List of content chunks
        """
        chunks = []

        # Flatten the JSON into sections
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                content = json.dumps(value, indent=2)
            else:
                content = str(value)

            chunks.append({
                'loinc_code': loinc_code,
                'url': url,
                'content_section': key,
                'content': content
            })

        return chunks if chunks else [{
            'loinc_code': loinc_code,
            'url': url,
            'content_section': 'Full Response',
            'content': json.dumps(data, indent=2)
        }]

    def chunk_content(self, soup: BeautifulSoup, loinc_code: str, url: str) -> List[Dict[str, str]]:
        """Chunk the content based on structural elements.

        Args:
            soup: BeautifulSoup object with parsed HTML
            loinc_code: The LOINC code
            url: The source URL

        Returns:
            List of dictionaries with chunked content
        """
        chunks = []

        # Try to find the main content area
        main_content = self._find_main_content(soup)

        if not main_content:
            # Fallback to body if main content not found
            main_content = soup.body if soup.body else soup

        # Extract chunks based on headings and sections
        current_section = "Main Content"
        current_content = []

        for element in main_content.descendants:
            # Skip if not a tag or is a script/style tag
            if not isinstance(element, Tag):
                continue

            if element.name in ['script', 'style', 'noscript']:
                continue

            # Check if this is a section header
            if element.name in self.section_tags:
                # Save the previous section if it has content
                if current_content:
                    content_text = self._clean_text(' '.join(current_content))
                    if content_text.strip():
                        chunks.append({
                            'loinc_code': loinc_code,
                            'url': url,
                            'content_section': current_section,
                            'content': content_text
                        })
                    current_content = []

                # Start new section
                current_section = self._clean_text(element.get_text())

            # Extract text content from meaningful elements
            elif element.name in ['p', 'li', 'td', 'th', 'span', 'div', 'dd', 'dt']:
                # Only get direct text, avoid duplicating nested elements
                text = self._get_direct_text(element)
                if text:
                    current_content.append(text)

            # Handle tables specially
            elif element.name == 'table':
                table_text = self._extract_table_content(element)
                if table_text:
                    current_content.append(table_text)

        # Add the last section
        if current_content:
            content_text = self._clean_text(' '.join(current_content))
            if content_text.strip():
                chunks.append({
                    'loinc_code': loinc_code,
                    'url': url,
                    'content_section': current_section,
                    'content': content_text
                })

        # If no chunks were created, create a single chunk with all text
        if not chunks:
            all_text = self._clean_text(main_content.get_text())
            if all_text.strip():
                chunks.append({
                    'loinc_code': loinc_code,
                    'url': url,
                    'content_section': 'Full Content',
                    'content': all_text
                })

        return chunks

    def _find_main_content(self, soup: BeautifulSoup) -> Tag:
        """Find the main content area of the page.

        Args:
            soup: BeautifulSoup object

        Returns:
            Main content tag or None
        """
        # Try common main content selectors
        selectors = [
            'main',
            '[role="main"]',
            '#main-content',
            '#content',
            '.main-content',
            '.content',
            'article'
        ]

        for selector in selectors:
            main = soup.select_one(selector)
            if main:
                return main

        return None

    def _get_direct_text(self, element: Tag) -> str:
        """Get direct text content from element, excluding nested tags.

        Args:
            element: BeautifulSoup Tag

        Returns:
            Direct text content
        """
        texts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    texts.append(text)

        return ' '.join(texts)

    def _extract_table_content(self, table: Tag) -> str:
        """Extract content from a table element.

        Args:
            table: Table tag

        Returns:
            Formatted table content
        """
        rows = []
        for row in table.find_all('tr'):
            cells = []
            for cell in row.find_all(['td', 'th']):
                cell_text = self._clean_text(cell.get_text())
                if cell_text:
                    cells.append(cell_text)
            if cells:
                rows.append(' | '.join(cells))

        return ' ; '.join(rows) if rows else ''

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
