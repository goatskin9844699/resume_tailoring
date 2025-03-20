"""Tests for web scraper module."""

import pytest
from unittest.mock import patch, MagicMock
from resume_tailor.extractor.scraper import WebScraper
from resume_tailor.exceptions import ExtractorError


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
            <h1>Job Title</h1>
            <p>Job Description</p>
            <div>Requirements:</div>
            <ul>
                <li>Requirement 1</li>
                <li>Requirement 2</li>
            </ul>
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
        
        # Check that content is cleaned
        assert 'Job Title' in content
        assert 'Job Description' in content
        assert 'Requirement 1' in content
        assert 'Requirement 2' in content
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