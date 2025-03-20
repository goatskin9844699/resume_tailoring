"""Test resume tailor."""

import pytest
import yaml

from resume_tailor.resume_tailor import ResumeTailor, InvalidOutputError


@pytest.fixture
def mock_llm_client(mocker):
    """Create a mock LLM client."""
    return mocker.Mock()


@pytest.fixture
def sample_job_description():
    """Create a sample job description."""
    return """
Senior Software Engineer - Python Backend

We are looking for a Senior Software Engineer with strong Python experience to join our team.

Requirements:
- 5+ years of Python development
- Experience with web frameworks
- Strong understanding of software design patterns
- Focus on code quality and testing

Responsibilities:
- Design and implement backend services
- Optimize for reliability and performance
- Implement automated testing and deployment
- Collaborate with cross-functional teams
"""


@pytest.fixture
def sample_resume_yaml():
    """Create a sample resume in YAML format."""
    resume_data = {
        "basic": {
            "name": "John Doe",
            "email": "john@example.com",
        },
        "education": [
            {
                "name": "MSc Computer Science",
                "school": "Example University",
                "startdate": "09/2015",
                "enddate": "06/2017",
                "highlights": ["GPA: 3.8"],
            }
        ],
        "experiences": [
            {
                "company": "TechCorp",
                "skip_name": False,
                "location": "San Francisco",
                "titles": [
                    {
                        "name": "Senior Engineer",
                        "startdate": "01/2018",
                        "enddate": "Present",
                    }
                ],
                "highlights": [
                    "Led development team",
                    "Implemented CI/CD pipeline",
                    "Optimized database performance",
                ],
            }
        ],
    }
    return yaml.dump(resume_data)


def test_tailor_resume(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test tailoring a resume with a job description."""
    # Create mock response
    mock_response = {
        "basic": {
            "name": "John Doe",
            "email": "john@example.com",
        },
        "education": [
            {
                "name": "MSc Computer Science",
                "school": "Example University",
                "startdate": "09/2015",
                "enddate": "06/2017",
                "highlights": ["GPA: 3.8"],
            }
        ],
        "experiences": [
            {
                "company": "TechCorp",
                "skip_name": False,
                "location": "San Francisco",
                "titles": [
                    {
                        "name": "Senior Engineer",
                        "startdate": "01/2018",
                        "enddate": "Present",
                    }
                ],
                "highlights": [
                    "Led Python development team",
                    "Implemented automated testing",
                    "Optimized backend services",
                ],
            }
        ],
    }
    mock_llm_client.generate.return_value = {"content": yaml.dump(mock_response)}

    tailor = ResumeTailor(mock_llm_client)
    result = tailor.tailor(sample_job_description, sample_resume_yaml)

    assert result.basic["name"] == "John Doe"
    assert len(result.experiences) == 1
    assert "Python" in result.experiences[0].highlights[0]


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