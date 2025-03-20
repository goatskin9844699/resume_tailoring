"""Unit tests for the Resume Tailor module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from resume_tailor import ResumeTailor, InvalidOutputError


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = MagicMock()
    client.generate.return_value = {"content": "basic:\n  name: John Doe\n  email: john@example.com"}
    return client


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
Senior Software Engineer - Python Backend

We are looking for a Senior Software Engineer with strong Python experience to join our backend team. The ideal candidate will have:

- 5+ years of experience in Python development
- Experience with microservices architecture
- Strong background in API development
- Experience with AWS and cloud infrastructure
- Track record of mentoring junior developers
- Experience with automated testing and CI/CD

Responsibilities:
- Design and implement scalable backend services
- Lead technical projects and mentor team members
- Improve system reliability and performance
- Implement automated testing and deployment
- Collaborate with cross-functional teams
"""


@pytest.fixture
def sample_resume_yaml():
    """Sample resume YAML for testing."""
    return """
basic:
  name: John Doe
  email: john@example.com
education:
  - name: MSc Computer Science
    school: Example University
    startdate: 09/2015
    enddate: 06/2017
experiences:
  - company: TechCorp
    titles:
      - name: Senior Engineer
        startdate: 01/2020
        enddate: present
    highlights:
      - Led development team
      - Implemented CI/CD pipeline
      - Optimized database performance
"""


def test_tailor_resume(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test tailoring a resume with a job description."""
    tailor = ResumeTailor(mock_llm_client)
    result = tailor.tailor(sample_job_description, sample_resume_yaml)
    assert isinstance(result, dict)
    assert "basic" in result
    assert result["basic"]["name"] == "John Doe"


def test_tailor_resume_invalid_yaml(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test handling invalid YAML from LLM."""
    mock_llm_client.generate.return_value = {"content": "invalid: yaml: content: -"}
    tailor = ResumeTailor(mock_llm_client)
    with pytest.raises(InvalidOutputError, match="Invalid YAML in LLM response"):
        tailor.tailor(sample_job_description, sample_resume_yaml)


def test_tailor_resume_llm_error(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test handling LLM error."""
    mock_llm_client.generate.side_effect = Exception("LLM error")
    tailor = ResumeTailor(mock_llm_client)
    with pytest.raises(InvalidOutputError, match="Failed to generate tailored resume"):
        tailor.tailor(sample_job_description, sample_resume_yaml) 