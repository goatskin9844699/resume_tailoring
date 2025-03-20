"""Web scraping module for job description extraction."""

from typing import Optional
import requests
from bs4 import BeautifulSoup
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

            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()

            # Get text content
            text = soup.get_text(separator='\n', strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return '\n'.join(lines)

        except requests.RequestException as e:
            raise ExtractorError(f"Failed to fetch content from URL: {str(e)}")
        except Exception as e:
            raise ExtractorError(f"Error processing content: {str(e)}") 