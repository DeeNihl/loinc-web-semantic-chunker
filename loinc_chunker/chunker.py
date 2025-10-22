"""Module for chunking HTML content using structural elements"""

from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime


class StructuralChunker:
    """Chunks HTML content based on structural elements."""
    
    def __init__(self):
        """Initialize the structural chunker."""
        pass
    
    def chunk(self, html_content: str, loinc_code: str, url: str) -> List[Dict[str, str]]:
        """
        Chunk HTML content based on structural elements.
        
        Args:
            html_content: The HTML content to chunk
            loinc_code: The LOINC code
            url: The source URL
            
        Returns:
            List of chunks, where each chunk is a dict with:
                - loinc_code: The LOINC code
                - url: The source URL
                - content_section: The section identifier
                - content: The text content
                - date: Timestamp when chunked
        """
        soup = BeautifulSoup(html_content, 'lxml')
        chunks = []
        timestamp = datetime.now().isoformat()
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        
        # Strategy: Extract content by major structural elements
        # Priority order: sections, articles, divs with meaningful classes/ids
        
        # Try to find main content sections
        sections = soup.find_all(['section', 'article', 'main'])
        
        if sections:
            for idx, section in enumerate(sections):
                section_id = self._get_section_identifier(section, idx)
                text_content = self._extract_text(section)
                
                if text_content.strip():
                    chunks.append({
                        'loinc_code': loinc_code,
                        'url': url,
                        'content_section': section_id,
                        'content': text_content,
                        'date': timestamp
                    })
        else:
            # Fallback: chunk by heading-based sections
            chunks.extend(self._chunk_by_headings(soup, loinc_code, url, timestamp))
        
        # If still no chunks, create a single chunk with body content
        if not chunks:
            body = soup.find('body')
            if body:
                text_content = self._extract_text(body)
                if text_content.strip():
                    chunks.append({
                        'loinc_code': loinc_code,
                        'url': url,
                        'content_section': 'body',
                        'content': text_content,
                        'date': timestamp
                    })
        
        return chunks
    
    def _get_section_identifier(self, element, idx: int) -> str:
        """
        Get a meaningful identifier for a section.
        
        Args:
            element: BeautifulSoup element
            idx: Index of the element
            
        Returns:
            Section identifier string
        """
        # Try to get id
        if element.get('id'):
            return f"{element.name}_{element.get('id')}"
        
        # Try to get meaningful class
        classes = element.get('class', [])
        if classes:
            return f"{element.name}_{classes[0]}"
        
        # Fall back to element type and index
        return f"{element.name}_{idx}"
    
    def _extract_text(self, element) -> str:
        """
        Extract clean text from an element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Cleaned text content
        """
        # Get text and clean it up
        text = element.get_text(separator=' ', strip=True)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text
    
    def _chunk_by_headings(self, soup: BeautifulSoup, loinc_code: str, 
                           url: str, timestamp: str) -> List[Dict[str, str]]:
        """
        Chunk content by heading elements (h1, h2, h3, etc).
        
        Args:
            soup: BeautifulSoup object
            loinc_code: The LOINC code
            url: The source URL
            timestamp: Current timestamp
            
        Returns:
            List of chunks
        """
        chunks = []
        
        # Find all headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            # Get heading text as section identifier
            section_id = self._extract_text(heading)
            if not section_id:
                continue
            
            # Collect content until next heading of same or higher level
            content_parts = []
            current = heading.next_sibling
            
            while current:
                if hasattr(current, 'name') and current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # Stop if we hit another heading at same or higher level
                    current_level = int(current.name[1])
                    heading_level = int(heading.name[1])
                    if current_level <= heading_level:
                        break
                
                if hasattr(current, 'get_text'):
                    text = self._extract_text(current)
                    if text:
                        content_parts.append(text)
                
                current = current.next_sibling
            
            content = ' '.join(content_parts)
            
            if content.strip():
                chunks.append({
                    'loinc_code': loinc_code,
                    'url': url,
                    'content_section': section_id[:200],  # Limit section name length
                    'content': content,
                    'date': timestamp
                })
        
        return chunks
