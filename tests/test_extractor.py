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


@pytest.fixture
def mock_content():
    """Create mock job posting content."""
    return """
    Job Title: Software Engineer
    Company: Test Company
    
    Summary:
    We are looking for a talented software engineer...
    
    Responsibilities:
    - Task 1
    - Task 2
    
    Requirements:
    - Req 1
    - Req 2
    """


def test_init(extractor, mock_llm):
    """Test extractor initialization."""
    assert extractor.llm == mock_llm
    assert extractor.scraper is not None


def test_extract_success(extractor, mock_llm, mock_job_data, mock_content):
    """Test successful job description extraction."""
    # Mock the scraper to return our test content
    with patch.object(extractor.scraper, 'fetch_content', return_value=mock_content):
        mock_llm.generate.return_value = mock_job_data
        
        result = extractor.extract("https://example.com/job")
        
        assert result == mock_job_data
        mock_llm.generate.assert_called_once()


def test_extract_scraper_error(extractor, mock_llm):
    """Test error handling when scraper fails."""
    with patch.object(extractor.scraper, 'fetch_content', side_effect=ExtractorError("Scraping failed")):
        with pytest.raises(ExtractorError, match="Failed to extract job description"):
            extractor.extract("https://example.com/job")


def test_extract_llm_error(extractor, mock_llm, mock_content):
    """Test error handling when LLM fails."""
    with patch.object(extractor.scraper, 'fetch_content', return_value=mock_content):
        mock_llm.generate.side_effect = Exception("LLM error")
        
        with pytest.raises(ExtractorError, match="Failed to extract job description"):
            extractor.extract("https://example.com/job")


def test_extract_invalid_url(extractor):
    """Test error handling for invalid URL."""
    with pytest.raises(ExtractorError, match="Invalid URL"):
        extractor.extract("not-a-url")


def test_extract_empty_response(extractor, mock_llm, mock_content):
    """Test error handling for empty LLM response."""
    with patch.object(extractor.scraper, 'fetch_content', return_value=mock_content):
        mock_llm.generate.return_value = {}
        
        with pytest.raises(ExtractorError, match="Invalid or incomplete job description data"):
            extractor.extract("https://example.com/job")


def test_extract_wrapped_json_response(extractor, mock_llm, mock_content):
    """Test handling of wrapped JSON responses."""
    wrapped_response = {
        "response": '{"company": "Test Corp", "title": "Developer", "summary": "Test role", '
                   '"responsibilities": ["Task 1", "Task 2"], "requirements": ["Req 1", "Req 2"], '
                   '"technical_skills": ["Skill 1", "Skill 2"], '
                   '"non_technical_skills": ["Soft 1", "Soft 2"], '
                   '"ats_keywords": ["Key 1", "Key 2"]}'
    }
    
    with patch.object(extractor.scraper, 'fetch_content', return_value=mock_content):
        mock_llm.generate.return_value = wrapped_response
        
        result = extractor.extract("https://example.com/job")
        
        assert result["company"] == "Test Corp"
        assert result["title"] == "Developer"
        assert len(result["responsibilities"]) >= 2
        assert len(result["requirements"]) >= 2


def test_extract_invalid_wrapped_json(extractor, mock_llm, mock_content):
    """Test handling of invalid wrapped JSON responses."""
    wrapped_response = {
        "response": "Not a valid JSON string"
    }
    
    with patch.object(extractor.scraper, 'fetch_content', return_value=mock_content):
        mock_llm.generate.return_value = wrapped_response
        
        with pytest.raises(ExtractorError, match="Invalid JSON response from LLM"):
            extractor.extract("https://example.com/job")


def test_extract_incomplete_data(extractor, mock_llm, mock_content):
    """Test handling of incomplete job data."""
    incomplete_data = {
        "company": "Test Corp",
        "title": "Developer"
        # Missing other required fields
    }
    
    with patch.object(extractor.scraper, 'fetch_content', return_value=mock_content):
        mock_llm.generate.return_value = incomplete_data
        
        with pytest.raises(ExtractorError, match="Invalid or incomplete job description data"):
            extractor.extract("https://example.com/job")


def test_extract_with_real_content(extractor, mock_llm):
    """Test extraction with realistic job posting content."""
    real_content = """
    Software Engineer Position at TechCorp
    
    We are seeking a talented Software Engineer to join our team.
    
    Key Responsibilities:
    - Develop and maintain web applications
    - Write clean, efficient code
    - Collaborate with team members
    
    Requirements:
    - 3+ years of Python experience
    - Strong problem-solving skills
    - Experience with web frameworks
    
    Technical Skills:
    - Python, Django, Flask
    - SQL, PostgreSQL
    - Git, Docker
    
    Soft Skills:
    - Communication
    - Teamwork
    - Leadership
    """
    
    mock_response = {
        "company": "TechCorp",
        "title": "Software Engineer",
        "summary": "We are seeking a talented Software Engineer to join our team.",
        "responsibilities": [
            "Develop and maintain web applications",
            "Write clean, efficient code",
            "Collaborate with team members"
        ],
        "requirements": [
            "3+ years of Python experience",
            "Strong problem-solving skills",
            "Experience with web frameworks"
        ],
        "technical_skills": [
            "Python",
            "Django",
            "Flask",
            "SQL",
            "PostgreSQL",
            "Git",
            "Docker"
        ],
        "non_technical_skills": [
            "Communication",
            "Teamwork",
            "Leadership"
        ],
        "ats_keywords": [
            "python",
            "django",
            "flask",
            "sql",
            "postgresql",
            "git",
            "docker",
            "software engineer",
            "web development"
        ]
    }
    
    with patch.object(extractor.scraper, 'fetch_content', return_value=real_content):
        mock_llm.generate.return_value = mock_response
        
        result = extractor.extract("https://example.com/job")
        
        assert result == mock_response
        assert len(result["responsibilities"]) >= 2
        assert len(result["requirements"]) >= 2
        assert len(result["technical_skills"]) >= 2
        assert len(result["non_technical_skills"]) >= 2
        assert len(result["ats_keywords"]) >= 2


def test_extract_with_minimal_content(extractor, mock_llm):
    """Test extraction with minimal job posting content."""
    minimal_content = """
    Job: Junior Developer
    Company: StartUp Inc
    
    We need a junior developer.
    
    Must know Python and Git.
    """
    
    mock_response = {
        "company": "StartUp Inc",
        "title": "Junior Developer",
        "summary": "We need a junior developer.",
        "responsibilities": [
            "Develop software applications",
            "Write and maintain code"
        ],
        "requirements": [
            "Python knowledge",
            "Git experience"
        ],
        "technical_skills": [
            "Python",
            "Git"
        ],
        "non_technical_skills": [
            "Communication",
            "Teamwork"
        ],
        "ats_keywords": [
            "python",
            "git",
            "junior developer",
            "software development"
        ]
    }
    
    with patch.object(extractor.scraper, 'fetch_content', return_value=minimal_content):
        mock_llm.generate.return_value = mock_response
        
        result = extractor.extract("https://example.com/job")
        
        assert result == mock_response
        assert len(result["responsibilities"]) >= 2
        assert len(result["requirements"]) >= 2
        assert len(result["technical_skills"]) >= 2
        assert len(result["non_technical_skills"]) >= 2
        assert len(result["ats_keywords"]) >= 2 