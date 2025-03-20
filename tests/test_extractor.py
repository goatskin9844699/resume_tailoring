"""Tests for job description extractor module."""

import pytest
from unittest.mock import patch, MagicMock
from resume_tailor.extractor.extractor import JobDescriptionExtractor
from resume_tailor.exceptions import ExtractorError
from resume_tailor.llm.client import LLMClient


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    return MagicMock(spec=LLMClient)


@pytest.fixture
def extractor(mock_llm):
    """Create a test extractor with mock LLM."""
    return JobDescriptionExtractor(llm_client=mock_llm)


@pytest.fixture
def mock_job_data():
    """Create mock job description data."""
    return {
        "company": "Test Company",
        "title": "Software Engineer",
        "summary": "Test job summary",
        "responsibilities": ["Task 1", "Task 2"],
        "requirements": ["Req 1", "Req 2"],
        "technical_skills": ["Python", "Docker"],
        "non_technical_skills": ["Communication", "Leadership"],
        "ats_keywords": ["python", "docker", "agile"]
    }


def test_init(extractor, mock_llm):
    """Test extractor initialization."""
    assert extractor.llm == mock_llm


def test_extract_success(extractor, mock_llm, mock_job_data):
    """Test successful job description extraction."""
    mock_llm.generate.return_value = mock_job_data
    
    result = extractor.extract("https://example.com/job")
    
    assert result == mock_job_data
    mock_llm.generate.assert_called_once()


def test_extract_llm_error(extractor, mock_llm):
    """Test error handling when LLM fails."""
    mock_llm.generate.side_effect = Exception("LLM error")
    
    with pytest.raises(ExtractorError, match="Failed to extract job description"):
        extractor.extract("https://example.com/job")


def test_extract_invalid_url(extractor):
    """Test error handling for invalid URL."""
    with pytest.raises(ExtractorError, match="Invalid URL"):
        extractor.extract("not-a-url")


def test_extract_empty_response(extractor, mock_llm):
    """Test error handling for empty LLM response."""
    mock_llm.generate.return_value = {}
    
    with pytest.raises(ExtractorError, match="Empty job description data"):
        extractor.extract("https://example.com/job") 