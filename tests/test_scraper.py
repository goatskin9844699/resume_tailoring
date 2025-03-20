"""Tests for web scraper module."""

import pytest
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
        assert content == ''  # Should handle invalid HTML gracefully


def test_fetch_content_parser_fallback(scraper, mock_response):
    """Test parser fallback functionality."""
    with patch('requests.Session.get', return_value=mock_response):
        # Mock BeautifulSoup to fail with lxml but succeed with html.parser
        with patch('bs4.BeautifulSoup', side_effect=[
            Exception('lxml error'),
            BeautifulSoup(mock_response.text, 'html.parser')
        ]):
            content = scraper.fetch_content('https://example.com/job')
            assert 'Job Title' in content
            assert 'Job Description' in content
            assert 'Requirements' in content


def test_fetch_content_all_parsers_fail(scraper):
    """Test handling when all parsers fail."""
    mock_response = MagicMock()
    mock_response.text = '<html><body>Test</body></html>'
    
    with patch('requests.Session.get', return_value=mock_response):
        with patch('bs4.BeautifulSoup', side_effect=Exception('Parser error')):
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
        assert 'Job Title' in content
        assert 'Job Description' in content
        assert 'Requirements' in content
        assert '- Requirement 1' in content
        assert '- Requirement 2' in content 