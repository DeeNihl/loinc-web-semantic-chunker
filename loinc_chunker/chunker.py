"""Content chunking module for LOINC web pages."""

from typing import List, Dict
from bs4 import BeautifulSoup, Tag, NavigableString


class ContentChunker:
    """Chunks LOINC web content based on structural elements."""

    def __init__(self):
        """Initialize the content chunker."""
        # Structural elements that define content sections
        self.section_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'article']

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
