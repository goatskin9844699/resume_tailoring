"""Test module for resume tailoring functionality.

This module contains tests for the ResumeTailor class and related functionality.
"""

from typing import Dict, Any
import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError

from resume_tailor.resume_tailor import ResumeTailor, InvalidOutputError
from resume_tailor.models import Resume


class MockLLMClient:
    """Mock LLM client for testing."""
    
    def generate(self, prompt: str) -> Dict[str, str]:
        """Mock generate function that returns valid YAML.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Dict containing the mock response
        """
        return {
            "content": """
basic:
  name: John Doe
  email: john@example.com
objective: "Senior Software Engineer with 8+ years of experience"
education:
  - name: Computer Science
    school: Example University
    startdate: "2018"
    enddate: "2022"
    highlights:
      - "Thesis: Distributed Systems"
experiences:
  - company: Example Corp
    title: Software Engineer
    startdate: "2022"
    enddate: "Present"
    location: "San Francisco"
    highlights:
      - "Led development of key features"
skills:
  - category: Technical
    skills:
      - Python
      - Django
"""
        }


@pytest.fixture
def mock_llm_client() -> MockLLMClient:
    """Create a mock LLM client.
    
    Returns:
        MockLLMClient: A mock LLM client instance
    """
    return MockLLMClient()


@pytest.fixture
def sample_job_description() -> str:
    """Create a sample job description.
    
    Returns:
        str: Sample job description
    """
    return """
Senior Software Engineer - Python Backend

We are looking for a Senior Software Engineer with strong Python experience.
"""


@pytest.fixture
def sample_resume_yaml() -> str:
    """Create a sample resume in YAML format.
    
    Returns:
        str: Sample resume YAML
    """
    return """
basic:
  name: John Doe
  email: john@example.com
objective: "Senior Software Engineer with 8+ years of experience"
education:
  - name: Computer Science
    school: Example University
    startdate: "2018"
    enddate: "2022"
    highlights:
      - "Thesis: Distributed Systems"
experiences:
  - company: Example Corp
    title: Software Engineer
    startdate: "2022"
    enddate: "Present"
    location: "San Francisco"
    highlights:
      - "Led development of key features"
skills:
  - category: Technical
    skills:
      - Python
      - Django
"""


def test_tailor_resume_success(mock_llm_client: MockLLMClient, sample_job_description: str, sample_resume_yaml: str) -> None:
    """Test successful resume tailoring.
    
    Args:
        mock_llm_client: Mock LLM client fixture
        sample_job_description: Sample job description fixture
        sample_resume_yaml: Sample resume YAML fixture
        
    Verifies that resume tailoring works correctly with valid input.
    """
    tailor = ResumeTailor(mock_llm_client)
    result = tailor.tailor(sample_job_description, sample_resume_yaml)
    assert isinstance(result, Resume)
    assert result.basic["name"] == "John Doe"
    assert result.basic["email"] == "john@example.com"
    assert len(result.experiences) == 1
    assert result.experiences[0].company == "Example Corp"


def test_clean_yaml_with_code_blocks(mock_llm_client: MockLLMClient) -> None:
    """Test YAML cleaning with code blocks.
    
    Args:
        mock_llm_client: Mock LLM client fixture
        
    Verifies that code blocks are properly removed from YAML.
    """
    yaml_with_blocks = '''```yaml
basic:
  name: John Doe
```'''
    tailor = ResumeTailor(mock_llm_client)
    cleaned = tailor._clean_yaml(yaml_with_blocks)
    assert cleaned.strip() == 'basic:\n  name: John Doe'


def test_clean_yaml_with_empty_lines(mock_llm_client: MockLLMClient) -> None:
    """Test YAML cleaning with empty lines.
    
    Args:
        mock_llm_client: Mock LLM client fixture
        
    Verifies that empty lines are properly handled.
    """
    yaml_with_empty_lines = '\n\nbasic:\n  name: John Doe\n\n'
    tailor = ResumeTailor(mock_llm_client)
    cleaned = tailor._clean_yaml(yaml_with_empty_lines)
    assert cleaned.strip() == 'basic:\n  name: John Doe'


def test_validate_yaml_success(mock_llm_client: MockLLMClient, sample_resume_yaml: str) -> None:
    """Test successful YAML validation.
    
    Args:
        mock_llm_client: Mock LLM client fixture
        sample_resume_yaml: Sample resume YAML fixture
        
    Verifies that valid YAML is properly validated.
    """
    tailor = ResumeTailor(mock_llm_client)
    result = tailor._validate_yaml(sample_resume_yaml)
    assert isinstance(result, Resume)
    assert result.basic["name"] == "John Doe"
    assert result.basic["email"] == "john@example.com"
    assert len(result.experiences) == 1
    assert result.experiences[0].company == "Example Corp"


def test_validate_yaml_invalid_format(mock_llm_client: MockLLMClient) -> None:
    """Test YAML validation with invalid format.
    
    Args:
        mock_llm_client: Mock LLM client fixture
        
    Raises:
        InvalidOutputError: Expected when YAML format is invalid
    """
    invalid_yaml = "invalid: [yaml: content"
    tailor = ResumeTailor(mock_llm_client)
    with pytest.raises(InvalidOutputError, match="Invalid YAML syntax"):
        tailor._validate_yaml(invalid_yaml)


def test_validate_yaml_missing_required_fields(mock_llm_client: MockLLMClient) -> None:
    """Test YAML validation with missing required fields.
    
    Args:
        mock_llm_client: Mock LLM client fixture
        
    Raises:
        InvalidOutputError: Expected when required fields are missing
    """
    incomplete_yaml = """
basic:
  name: John Doe
"""
    tailor = ResumeTailor(mock_llm_client)
    with pytest.raises(InvalidOutputError, match="Invalid resume format"):
        tailor._validate_yaml(incomplete_yaml)


def test_save_tailored_resume(mock_llm_client: MockLLMClient, sample_resume_yaml: str, tmp_path: Path) -> None:
    """Test saving tailored resume to file.
    
    Args:
        mock_llm_client: Mock LLM client fixture
        sample_resume_yaml: Sample resume YAML fixture
        tmp_path: pytest fixture for temporary directory
        
    Verifies that resume is properly saved to file.
    """
    tailor = ResumeTailor(mock_llm_client)
    resume = tailor._validate_yaml(sample_resume_yaml)
    output_file = tmp_path / "output.yaml"
    
    tailor.save_tailored_resume(resume, str(output_file))
    
    assert output_file.exists()
    with open(output_file) as f:
        saved_yaml = yaml.safe_load(f)
    assert saved_yaml["basic"]["name"] == "John Doe"
    assert saved_yaml["basic"]["email"] == "john@example.com"


def test_tailor_resume_invalid_llm_response(mock_llm_client: MockLLMClient, sample_job_description: str, sample_resume_yaml: str) -> None:
    """Test handling of invalid LLM response.
    
    Args:
        mock_llm_client: Mock LLM client fixture
        sample_job_description: Sample job description fixture
        sample_resume_yaml: Sample resume YAML fixture
        
    Raises:
        InvalidOutputError: Expected when LLM response is invalid
    """
    # Mock LLM client that returns invalid YAML
    mock_llm_client.generate = lambda prompt: {"content": "invalid: [yaml: content"}
    
    tailor = ResumeTailor(mock_llm_client)
    with pytest.raises(InvalidOutputError, match="Failed to generate valid YAML"):
        tailor.tailor(sample_job_description, sample_resume_yaml) 