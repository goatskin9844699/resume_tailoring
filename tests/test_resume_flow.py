"""Unit tests for the resume tailoring flow.

This module contains tests for the complete resume tailoring workflow,
including job description extraction, resume parsing, and resume tailoring.
"""

import json
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import yaml

from resume_tailor.models import Resume
from resume_tailor.extractor.extractor import JobDescriptionExtractor
from resume_tailor.resume_tailor import ResumeTailor
from resume_tailor.llm.client import OpenRouterLLMClient
from resume_tailor.exceptions import ExtractorError, TailorError, InvalidOutputError
from resume_tailor.extractor.scraper import WebScraper

@pytest.fixture
def mock_job_url():
    """Fixture providing a mock job posting URL."""
    return "https://example.com/job"

@pytest.fixture
def mock_resume_yaml(tmp_path):
    """Fixture providing a temporary YAML file with mock resume data."""
    resume_data = {
        "basic": {
            "name": "Test User",
            "email": "test@example.com"
        },
        "education": [{
            "name": "Test Degree",
            "school": "Test University",
            "startdate": "2020",
            "enddate": "2024",
            "highlights": []
        }],
        "experiences": [{
            "company": "Test Company",
            "location": "",
            "skip_name": False,
            "highlights": [
                "Test highlight"
            ],
            "titles": [{
                "name": "Test Role",
                "startdate": "2020",
                "enddate": "Present"
            }]
        }],
        "skills": [
            {
                "category": "Technical",
                "skills": ["Python", "Django"]
            },
            {
                "category": "Non-Technical",
                "skills": ["Communication"]
            }
        ],
        "objective": "",
        "projects": [],
        "publications": [],
        "editing": False,
        "debug": False
    }
    
    resume_file = tmp_path / "test_resume.yaml"
    with open(resume_file, "w") as f:
        yaml.dump(resume_data, f)
    
    return str(resume_file)

@pytest.fixture
def mock_job_data():
    """Fixture providing mock job description data."""
    return {
        "company": "Test Company",
        "title": "Test Role",
        "summary": "Test job summary",
        "responsibilities": [
            "Test responsibility 1",
            "Test responsibility 2",
            "Test responsibility 3"
        ],
        "requirements": [
            "Test requirement 1",
            "Test requirement 2",
            "Test requirement 3"
        ],
        "technical_skills": [
            "Python",
            "Django",
            "PostgreSQL"
        ],
        "non_technical_skills": [
            "Communication",
            "Leadership",
            "Problem Solving"
        ],
        "ats_keywords": [
            "python",
            "django",
            "leadership",
            "problem solving"
        ]
    }

@pytest.fixture
def mock_llm_response():
    """Fixture providing mock resume data in the correct format."""
    return {
        "basic": {
            "name": "Test User",
            "email": "test@example.com"
        },
        "education": [{
            "name": "Test Degree",
            "school": "Test University",
            "startdate": "2020",
            "enddate": "2024",
            "highlights": []
        }],
        "experiences": [{
            "company": "Test Company",
            "location": "",
            "skip_name": False,
            "highlights": [
                "Test highlight 1",
                "Test highlight 2"
            ],
            "titles": [{
                "name": "Test Role",
                "startdate": "2020",
                "enddate": "Present"
            }]
        }],
        "skills": [
            {
                "category": "Technical",
                "skills": ["Python", "Django", "PostgreSQL"]
            },
            {
                "category": "Non-Technical",
                "skills": ["Communication", "Leadership"]
            }
        ],
        "objective": "",
        "projects": [],
        "publications": [],
        "editing": False,
        "debug": False
    }

@pytest.fixture
def mock_llm_client(mock_job_data, mock_llm_response):
    """Fixture providing a mocked LLM client."""
    mock_client = Mock(spec=OpenRouterLLMClient)
    
    # Set up responses for the complete flow:
    # 1. First call returns job data (for extraction)
    # 2. Second call returns tailored content (for tailoring step 1)
    # 3. Third call returns formatted YAML (for tailoring step 2)
    mock_client.generate.side_effect = [
        {"content": json.dumps(mock_job_data)},  # For job extraction
        {"content": "Tailored content in any format"},  # For tailoring step 1
        {"content": yaml.dump(mock_llm_response)}  # For tailoring step 2
    ]
    return mock_client

@pytest.fixture
def mock_scraper():
    """Fixture providing a mocked web scraper."""
    mock_scraper = Mock(spec=WebScraper)
    mock_scraper.fetch_content.return_value = "Test job description content"
    return mock_scraper

class TestResumeTailoringFlow:
    """Test class for the complete resume tailoring workflow."""
    
    def test_complete_flow_success(self, mock_job_url, mock_resume_yaml, mock_llm_client, mock_scraper):
        """Test successful completion of the complete resume tailoring workflow."""
        # 1. Extract job description
        extractor = JobDescriptionExtractor(llm_client=mock_llm_client)
        extractor.scraper = mock_scraper
        job_data = extractor.extract(mock_job_url)

        # 2. Load resume YAML
        with open(mock_resume_yaml) as f:
            resume_yaml = f.read()

        # 3. Tailor resume
        tailor = ResumeTailor(llm_client=mock_llm_client)
        tailored_resume = tailor.tailor(job_data, resume_yaml)

        # 4. Verify final output
        assert tailored_resume is not None
        assert isinstance(tailored_resume, Resume)
        assert tailored_resume.basic["name"] == "Test User"
        assert len(tailored_resume.experiences) == 1
        assert len(tailored_resume.education) == 1
        assert len(tailored_resume.skills) == 2
        assert mock_scraper.fetch_content.called
        assert mock_scraper.fetch_content.call_args[0][0] == mock_job_url

    def test_complete_flow_job_extraction_error(self, mock_job_url, mock_resume_yaml, mock_llm_client, mock_scraper):
        """Test error handling when job extraction fails."""
        with patch("requests.Session.get") as mock_get:
            # Set up mock response for job posting URL with error
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_get.return_value = mock_response
            
            # Mock scraper to raise error
            mock_scraper.fetch_content.side_effect = Exception("Failed to fetch content")
            
            # Attempt to extract job description
            extractor = JobDescriptionExtractor(llm_client=mock_llm_client)
            extractor.scraper = mock_scraper
            with pytest.raises(ExtractorError):
                extractor.extract(mock_job_url)
    
    def test_complete_flow_resume_parsing_error(self, mock_job_url, mock_llm_client, mock_scraper):
        """Test error handling when resume parsing fails."""
        # Extract job description
        extractor = JobDescriptionExtractor(llm_client=mock_llm_client)
        extractor.scraper = mock_scraper
        job_data = extractor.extract(mock_job_url)

        # Attempt to tailor with invalid resume
        tailor = ResumeTailor(llm_client=mock_llm_client)
        with pytest.raises(InvalidOutputError) as exc_info:
            tailor.tailor(job_data, "invalid: yaml: content")
        assert "Invalid YAML syntax" in str(exc_info.value)
    
    def test_complete_flow_tailoring_error(self, mock_job_url, mock_resume_yaml, mock_llm_client, mock_scraper):
        """Test error handling when resume tailoring fails."""
        # Extract job description
        extractor = JobDescriptionExtractor(llm_client=mock_llm_client)
        extractor.scraper = mock_scraper
        job_data = extractor.extract(mock_job_url)

        # Load resume YAML
        with open(mock_resume_yaml) as f:
            resume_yaml = f.read()

        # Mock LLM to raise error during tailoring
        mock_llm_client.generate.side_effect = Exception("LLM Error")
        tailor = ResumeTailor(llm_client=mock_llm_client)
        with pytest.raises(InvalidOutputError) as exc_info:
            tailor.tailor(job_data, resume_yaml)
        assert "Failed to generate tailored resume" in str(exc_info.value) 