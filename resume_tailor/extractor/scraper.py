"""Web scraping module for job description extraction."""

from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup, Tag
from ..exceptions import ExtractorError


class WebScraper:
    """Handles web scraping for job descriptions."""

    def __init__(self):
        """Initialize the web scraper."""
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_content(self, url: str) -> str:
        """
        Fetch and clean content from a URL.

        Args:
            url: URL to fetch content from

        Returns:
            Cleaned text content from the page

        Raises:
            ExtractorError: If there's an error fetching or processing the content
        """
        try:
            # Fetch the page
            response = self.session.get(url)
            response.raise_for_status()

            # Try different parsers in order of preference
            parsers = ['lxml', 'html.parser']
            soup = None
            last_error = None

            for parser in parsers:
                try:
                    soup = BeautifulSoup(response.text, parser)
                    break
                except Exception as e:
                    last_error = e
                    continue

            if soup is None:
                raise ExtractorError(f"Failed to parse HTML with any parser. Last error: {str(last_error)}")

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Extract structured content
            content = self._extract_structured_content(soup)
            return content

        except requests.RequestException as e:
            raise ExtractorError(f"Failed to fetch content from URL: {str(e)}")
        except Exception as e:
            raise ExtractorError(f"Error processing content: {str(e)}")

    def _extract_structured_content(self, soup: BeautifulSoup) -> str:
        """
        Extract structured content from the HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Structured text content
        """
        # Find main content area
        main_content = self._find_main_content(soup)
        if not main_content:
            main_content = soup

        # Extract sections
        sections = []
        
        # Process headings and their content
        for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            section = self._process_section(heading)
            if section:
                sections.append(section)

        # Process lists
        for ul in main_content.find_all('ul'):
            section = self._process_list(ul)
            if section:
                sections.append(section)

        # Process paragraphs
        for p in main_content.find_all('p'):
            if p.get_text(strip=True):
                sections.append(p.get_text(strip=True))

        return '\n\n'.join(sections)

    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """
        Find the main content area of the page.

        Args:
            soup: BeautifulSoup object

        Returns:
            Main content tag or None
        """
        # Common main content selectors
        selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '#main-content',
            '.job-description',
            '#job-description'
        ]

        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                return content

        return None

    def _process_section(self, heading: Tag) -> str:
        """
        Process a section with a heading.

        Args:
            heading: Heading tag

        Returns:
            Formatted section text
        """
        # Get heading text
        heading_text = heading.get_text(strip=True)
        
        # Get content until next heading
        content = []
        current = heading.next_sibling
        
        while current and not current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if current.name == 'p':
                text = current.get_text(strip=True)
                if text:
                    content.append(text)
            elif current.name == 'ul':
                items = self._process_list(current)
                if items:
                    content.append(items)
            current = current.next_sibling

        # Format section
        if content:
            return f"{heading_text}\n" + "\n".join(content)
        return heading_text

    def _process_list(self, ul: Tag) -> str:
        """
        Process an unordered list.

        Args:
            ul: List tag

        Returns:
            Formatted list text
        """
        items = []
        for li in ul.find_all('li', recursive=False):
            text = li.get_text(strip=True)
            if text:
                items.append(f"- {text}")
        
        return "\n".join(items) if items else "" 