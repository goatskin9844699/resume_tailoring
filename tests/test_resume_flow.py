"""Unit tests for the resume tailoring flow.

This module contains tests for the complete resume tailoring workflow,
including job description extraction, resume parsing, and resume tailoring.
"""

import json
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import yaml
import os

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
    """Create a mock resume YAML file."""
    resume_data = {
        "basic": {
            "name": "Test User",
            "email": "test@example.com",
        },
        "education": [
            {
                "name": "Computer Science",
                "school": "Test University",
                "startdate": "2020",
                "enddate": "2024",
            }
        ],
        "experiences": [
            {
                "company": "Test Company",
                "location": "Test Location",
                "title": "Test Role",
                "startdate": "2020",
                "enddate": "Present",
                "highlights": ["Test highlight 1", "Test highlight 2"],
            }
        ],
        "skills": [
            {
                "category": "Technical",
                "skills": ["Python", "Django"],
            },
            {
                "category": "Non-Technical",
                "skills": ["Communication"],
            },
        ],
    }

    file_path = os.path.join(tmp_path, "test_resume.yaml")
    with open(file_path, "w") as f:
        yaml.dump(resume_data, f)
    return file_path

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
        ],
        "is_complete": True,
        "truncation_note": ""
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
    """Create a mock web scraper."""
    mock = Mock(spec=WebScraper)
    mock.scrape = Mock(return_value="Test job posting content")
    return mock

class TestResumeTailoringFlow:
    """Test the complete resume tailoring workflow."""

    def test_complete_flow_success(self, mock_job_url, mock_resume_yaml, mock_llm_client, mock_scraper):
        """Test successful completion of the complete resume tailoring workflow."""
        # Mock job description extraction response
        mock_job_response = {
            "content": json.dumps({
                "company": "Test Company",
                "title": "Test Role",
                "summary": "Test job summary",
                "responsibilities": ["Test responsibility 1", "Test responsibility 2", "Test responsibility 3"],
                "requirements": ["Test requirement 1", "Test requirement 2", "Test requirement 3"],
                "technical_skills": ["Python", "Django", "PostgreSQL"],
                "non_technical_skills": ["Communication", "Leadership", "Problem Solving"],
                "ats_keywords": ["python", "django", "leadership", "problem solving"],
                "is_complete": True,
                "truncation_note": "",
            })
        }

        # Mock resume tailoring responses
        mock_tailor_response = {
            "content": """
            Basic Information:
            - Name: Test User
            - Email: test@example.com

            Education:
            - Computer Science at Test University (2020 - 2024)
              * Relevant coursework in Python and Django development

            Experience:
            - Test Company
              * Test Role (2020 - Present)
              * Implemented key features using Python and Django
              * Led team initiatives and improved processes
            """
        }

        mock_format_response = {
            "content": yaml.dump({
                "basic": {
                    "name": "Test User",
                    "email": "test@example.com",
                },
                "education": [
                    {
                        "name": "Computer Science",
                        "school": "Test University",
                        "startdate": "2020",
                        "enddate": "2024",
                        "highlights": ["Relevant coursework in Python and Django development"],
                    }
                ],
                "experiences": [
                    {
                        "company": "Test Company",
                        "location": "Test Location",
                        "title": "Test Role",
                        "startdate": "2020",
                        "enddate": "Present",
                        "highlights": [
                            "Implemented key features using Python and Django",
                            "Led team initiatives and improved processes",
                        ],
                    }
                ],
                "skills": [
                    {
                        "category": "Technical",
                        "skills": ["Python", "Django", "PostgreSQL"],
                    },
                    {
                        "category": "Non-Technical",
                        "skills": ["Communication", "Leadership"],
                    },
                ],
            })
        }

        # Set up mock responses
        mock_llm_client.generate.side_effect = [
            mock_job_response,  # First call: job description extraction
            mock_tailor_response,  # Second call: resume tailoring
            mock_format_response,  # Third call: YAML formatting
        ]

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

        # Verify the result
        assert tailored_resume.basic["name"] == "Test User"
        assert tailored_resume.basic["email"] == "test@example.com"
        assert len(tailored_resume.experiences) == 1
        assert tailored_resume.experiences[0].company == "Test Company"
        assert tailored_resume.experiences[0].title == "Test Role"
        assert len(tailored_resume.experiences[0].highlights) == 2

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