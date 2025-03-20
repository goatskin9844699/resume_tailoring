"""Tests for web scraper module."""

import pytest
import requests
from unittest.mock import patch, MagicMock
from resume_tailor.extractor.scraper import WebScraper
from resume_tailor.exceptions import ExtractorError
from bs4 import BeautifulSoup


@pytest.fixture
def scraper():
    """Create a test scraper."""
    return WebScraper()


@pytest.fixture
def mock_response():
    """Create a mock response with HTML content."""
    response = MagicMock()
    response.text = """
    <html>
        <head>
            <script>console.log('test');</script>
            <style>body { color: red; }</style>
        </head>
        <body>
            <main>
                <h1>Job Title</h1>
                <p>Job Description</p>
                <h2>Requirements</h2>
                <ul>
                    <li>Requirement 1</li>
                    <li>Requirement 2</li>
                </ul>
                <h2>Responsibilities</h2>
                <p>Main responsibilities:</p>
                <ul>
                    <li>Responsibility 1</li>
                    <li>Responsibility 2</li>
                </ul>
            </main>
        </body>
    </html>
    """
    return response


def test_init(scraper):
    """Test scraper initialization."""
    assert scraper.session is not None
    assert 'User-Agent' in scraper.session.headers


def test_fetch_content_success(scraper, mock_response):
    """Test successful content fetching."""
    with patch('requests.Session.get', return_value=mock_response):
        content = scraper.fetch_content('https://example.com/job')
        
        # Check that content is not empty
        assert content, "Content should not be empty"
        
        # Check that content is structured
        assert 'Job Title' in content
        assert 'Job Description' in content
        assert 'Requirements' in content
        assert 'Responsibilities' in content
        assert '- Requirement 1' in content
        assert '- Requirement 2' in content
        assert '- Responsibility 1' in content
        assert '- Responsibility 2' in content
        assert 'Main responsibilities:' in content
        
        # Check that script and style are removed
        assert 'console.log' not in content
        assert 'color: red' not in content


def test_fetch_content_empty_page(scraper):
    """Test handling of empty page content."""
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <main>
                <p></p>
                <ul></ul>
            </main>
        </body>
    </html>
    """
    
    with patch('requests.Session.get', return_value=mock_response):
        content = scraper.fetch_content('https://example.com/job')
        assert content == '', "Content should be empty for empty page"


def test_fetch_content_no_content(scraper):
    """Test handling of page with no content."""
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <main>
                <script>console.log('test');</script>
                <style>body { color: red; }</style>
            </main>
        </body>
    </html>
    """
    
    with patch('requests.Session.get', return_value=mock_response):
        content = scraper.fetch_content('https://example.com/job')
        assert content == '', "Content should be empty when no text content"


def test_fetch_content_network_error(scraper):
    """Test handling of network errors."""
    with patch('requests.Session.get', side_effect=requests.RequestException('Network error')):
        with pytest.raises(ExtractorError, match="Failed to fetch content from URL"):
            scraper.fetch_content('https://example.com/job')


def test_fetch_content_invalid_html(scraper):
    """Test handling of invalid HTML."""
    mock_response = MagicMock()
    mock_response.text = '<invalid>html'
    
    with patch('requests.Session.get', return_value=mock_response):
        content = scraper.fetch_content('https://example.com/job')
        assert content == '', "Content should be empty for invalid HTML"


def test_fetch_content_parser_fallback(scraper, mock_response):
    """Test parser fallback functionality."""
    with patch('requests.Session.get', return_value=mock_response):
        # Create a mock BeautifulSoup instance
        mock_soup = BeautifulSoup(mock_response.text, 'html.parser')
        
        # Mock BeautifulSoup constructor to fail with lxml but succeed with html.parser
        def mock_bs_side_effect(markup, parser):
            if parser == 'lxml':
                raise Exception('lxml error')
            return mock_soup

        with patch('resume_tailor.extractor.scraper.BeautifulSoup', side_effect=mock_bs_side_effect) as mock_bs:
            content = scraper.fetch_content('https://example.com/job')
            assert content, "Content should not be empty"
            assert 'Job Title' in content
            assert 'Job Description' in content
            assert 'Requirements' in content
            # The BeautifulSoup constructor is called:
            # 1. Initial check with html.parser
            # 2. First attempt with lxml (fails)
            # 3. Second attempt with html.parser (succeeds)
            assert mock_bs.call_count == 3  # Update expected call count


def test_fetch_content_all_parsers_fail(scraper):
    """Test handling when all parsers fail."""
    mock_response = MagicMock()
    mock_response.text = '<html><body>Test</body></html>'
    
    with patch('requests.Session.get', return_value=mock_response):
        def mock_bs_side_effect(markup, parser):
            raise Exception('Parser error')
            
        with patch('resume_tailor.extractor.scraper.BeautifulSoup', side_effect=mock_bs_side_effect):
            with pytest.raises(ExtractorError, match="Failed to parse HTML with any parser"):
                scraper.fetch_content('https://example.com/job')


def test_fetch_content_without_main_tag(scraper):
    """Test content extraction without main tag."""
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <h1>Job Title</h1>
            <p>Job Description</p>
            <h2>Requirements</h2>
            <ul>
                <li>Requirement 1</li>
                <li>Requirement 2</li>
            </ul>
        </body>
    </html>
    """
    
    with patch('requests.Session.get', return_value=mock_response):
        content = scraper.fetch_content('https://example.com/job')
        assert content, "Content should not be empty"
        assert 'Job Title' in content
        assert 'Job Description' in content
        assert 'Requirements' in content
        assert '- Requirement 1' in content
        assert '- Requirement 2' in content


def test_fetch_content_js_rendered(scraper):
    """Test fetching JavaScript-rendered content."""
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <div id="app">
                <script>
                    // Simulate JavaScript rendering
                    document.getElementById('app').innerHTML = `
                        <main>
                            <h1>Job Title</h1>
                            <p>Job Description</p>
                            <h2>Requirements</h2>
                            <ul>
                                <li>Requirement 1</li>
                                <li>Requirement 2</li>
                            </ul>
                        </main>
                    `;
                </script>
            </div>
        </body>
    </html>
    """
    
    with patch('requests.Session.get', return_value=mock_response):
        # Mock Playwright to return rendered content
        async def mock_playwright_fetch(url):
            return """
            <html>
                <body>
                    <main>
                        <h1>Job Title</h1>
                        <p>Job Description</p>
                        <h2>Requirements</h2>
                        <ul>
                            <li>Requirement 1</li>
                            <li>Requirement 2</li>
                        </ul>
                    </main>
                </body>
            </html>
            """
        
        with patch('resume_tailor.extractor.scraper.WebScraper._fetch_with_playwright', side_effect=mock_playwright_fetch):
            content = scraper.fetch_content('https://example.com/job')
            assert content, "Content should not be empty"
            assert 'Job Title' in content
            assert 'Job Description' in content
            assert 'Requirements' in content
            assert '- Requirement 1' in content
            assert '- Requirement 2' in content


def test_fetch_content_js_rendered_error(scraper):
    """Test handling of JavaScript rendering errors."""
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <div id="app">
                <script>
                    // Simulate JavaScript rendering
                    document.getElementById('app').innerHTML = `
                        <main>
                            <h1>Job Title</h1>
                            <p>Job Description</p>
                        </main>
                    `;
                </script>
            </div>
        </body>
    </html>
    """
    
    with patch('requests.Session.get', return_value=mock_response):
        # Mock Playwright to raise an error
        async def mock_playwright_fetch(url):
            raise Exception('JavaScript rendering failed')
        
        with patch('resume_tailor.extractor.scraper.WebScraper._fetch_with_playwright', side_effect=mock_playwright_fetch):
            # Should fall back to static content
            content = scraper.fetch_content('https://example.com/job')
            assert content == '', "Content should be empty when JavaScript rendering fails and static content is empty" 