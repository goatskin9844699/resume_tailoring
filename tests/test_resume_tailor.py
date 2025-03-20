"""Unit tests for the Resume Tailor module."""

import pytest
from pathlib import Path

from resume_tailor import ResumeTailor, InvalidOutputError


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


def test_tailor_resume(sample_job_description, sample_resume_yaml):
    """Test tailoring a resume with a job description."""
    tailor = ResumeTailor()
    with pytest.raises(NotImplementedError):
        tailor.tailor(sample_job_description, sample_resume_yaml) 