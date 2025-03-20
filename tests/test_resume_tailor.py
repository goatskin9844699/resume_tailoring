"""Test resume tailor."""

import pytest
import yaml
from unittest.mock import patch

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
    """Fixture providing sample resume YAML content."""
    return """
basic:
  email: john@example.com
  name: John Doe
education:
- enddate: 06/2017
  name: MSc Computer Science
  school: Example University
  startdate: 09/2015
  highlights:
  - 'GPA: 3.8'
experiences:
- company: TechCorp
  location: San Francisco
  title: Senior Engineer
  startdate: 01/2018
  enddate: Present
  highlights:
  - Led Python development team
  - Implemented automated testing
  - Optimized backend services
skills:
- category: Technical
  skills:
  - Python
  - Django
- category: Non-Technical
  skills:
  - Communication
"""


def test_tailor_resume(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test tailoring a resume with a job description."""
    # Create mock responses for both steps
    tailored_content = """
    Basic Information:
    - Name: John Doe
    - Email: john@example.com

    Education:
    - MSc Computer Science at Example University (09/2015 - 06/2017)
      * GPA: 3.8

    Experience:
    - TechCorp (San Francisco)
      * Senior Engineer (01/2018 - Present)
      * Led Python development team
      * Implemented automated testing
      * Optimized backend services
    """

    formatted_yaml = {
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
                "location": "San Francisco",
                "title": "Senior Engineer",
                "startdate": "01/2018",
                "enddate": "Present",
                "highlights": [
                    "Led Python development team",
                    "Implemented automated testing",
                    "Optimized backend services",
                ],
            }
        ],
    }

    # Set up mock responses for both steps
    mock_llm_client.generate.side_effect = [
        {"content": tailored_content},  # First call: tailoring
        {"content": yaml.dump(formatted_yaml)}  # Second call: formatting
    ]

    tailor = ResumeTailor(mock_llm_client)
    result = tailor.tailor(sample_job_description, sample_resume_yaml)

    # Verify the result
    assert result.basic["name"] == "John Doe"
    assert result.basic["email"] == "john@example.com"
    assert len(result.experiences) == 1
    assert result.experiences[0].company == "TechCorp"
    assert result.experiences[0].title == "Senior Engineer"
    assert len(result.experiences[0].highlights) == 3
    
    # Verify both steps were called
    assert mock_llm_client.generate.call_count == 2


def test_tailor_resume_invalid_yaml(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test handling invalid YAML from LLM."""
    # First call succeeds, second call returns invalid YAML
    mock_llm_client.generate.side_effect = [
        {"content": "Some tailored content"},  # First call: tailoring
        {"content": "invalid: yaml: content: -"}  # Second call: formatting
    ]
    
    tailor = ResumeTailor(mock_llm_client)
    with pytest.raises(InvalidOutputError, match="Failed to generate valid YAML"):
        tailor.tailor(sample_job_description, sample_resume_yaml)


def test_tailor_resume_llm_error(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test handling LLM error."""
    mock_llm_client.generate.side_effect = Exception("LLM error")
    tailor = ResumeTailor(mock_llm_client)
    with pytest.raises(InvalidOutputError, match="Failed to generate tailored resume"):
        tailor.tailor(sample_job_description, sample_resume_yaml)


def test_tailor_resume_with_missing_sections(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test tailoring a resume with missing sections."""
    # Create mock responses for both steps
    tailored_content = """
    Basic Information:
    - Name: John Doe
    - Email: john@example.com

    Experience:
    - TechCorp (San Francisco)
      * Senior Engineer (01/2018 - Present)
      * Led Python development team
      * Implemented automated testing
      * Optimized backend services
    """

    formatted_yaml = {
        "basic": {
            "name": "John Doe",
            "email": "john@example.com",
        },
        "education": [],  # Required but empty
        "experiences": [
            {
                "company": "TechCorp",
                "location": "San Francisco",
                "title": "Senior Engineer",
                "startdate": "01/2018",
                "enddate": "Present",
                "highlights": [
                    "Led Python development team",
                    "Implemented automated testing",
                    "Optimized backend services",
                ],
            }
        ],
    }

    # Set up mock responses for both steps
    mock_llm_client.generate.side_effect = [
        {"content": tailored_content},  # First call: tailoring
        {"content": yaml.dump(formatted_yaml)}  # Second call: formatting
    ]

    # Test with logging capture
    with patch('resume_tailor.resume_tailor.logger') as mock_logger:
        tailor = ResumeTailor(mock_llm_client)
        result = tailor.tailor(sample_job_description, sample_resume_yaml)

        # Verify the result
        assert result.basic["name"] == "John Doe"
        assert result.basic["email"] == "john@example.com"
        assert len(result.experiences) == 1
        assert result.experiences[0].company == "TechCorp"
        assert result.experiences[0].title == "Senior Engineer"
        assert len(result.experiences[0].highlights) == 3
        
        # Verify warnings were logged for missing optional sections
        mock_logger.warning.assert_any_call("Missing skills section")
        mock_logger.warning.assert_any_call("Missing publications section")
        
        # Verify both steps were called
        assert mock_llm_client.generate.call_count == 2


def test_tailor_resume_with_integer_dates(mock_llm_client, sample_job_description, sample_resume_yaml):
    """Test tailoring a resume with integer dates."""
    # Create mock responses for both steps
    tailored_content = """
    Basic Information:
    - Name: John Doe
    - Email: john@example.com

    Education:
    - MSc Computer Science at Example University (2015 - 2017)
      * GPA: 3.8
    """

    formatted_yaml = {
        "basic": {
            "name": "John Doe",
            "email": "john@example.com",
        },
        "education": [
            {
                "name": "MSc Computer Science",
                "school": "Example University",
                "startdate": 2015,
                "enddate": 2017,
                "highlights": ["GPA: 3.8"],
            }
        ],
        "experiences": [],  # Required but empty
    }

    # Set up mock responses for both steps
    mock_llm_client.generate.side_effect = [
        {"content": tailored_content},  # First call: tailoring
        {"content": yaml.dump(formatted_yaml)}  # Second call: formatting
    ]

    tailor = ResumeTailor(mock_llm_client)
    result = tailor.tailor(sample_job_description, sample_resume_yaml)

    # Verify the result
    assert result.basic["name"] == "John Doe"
    assert result.basic["email"] == "john@example.com"
    assert len(result.education) == 1
    assert result.education[0].name == "MSc Computer Science"
    assert result.education[0].startdate == "2015"
    assert result.education[0].enddate == "2017"
    assert len(result.experiences) == 0  # Verify empty experiences list
    
    # Verify both steps were called
    assert mock_llm_client.generate.call_count == 2 