"""Unit tests for the Resume Parser module."""

import pytest
from pathlib import Path

from resume_tailor import (
    InvalidYAMLError,
    MissingRequiredFieldError,
    ResumeParser,
    ResumeParserError,
)


@pytest.fixture
def test_resume_path(tmp_path):
    """Create a temporary test resume file."""
    resume_path = tmp_path / "test_resume.yaml"
    resume_path.write_text(
        """
basic:
  name: John Doe
  email: john@example.com
education:
  - name: MSc
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
"""
    )
    return str(resume_path)


def test_parse_valid_resume(test_resume_path):
    """Test parsing a valid resume file."""
    parser = ResumeParser(test_resume_path)
    data = parser.parse()
    assert data["basic"]["name"] == "John Doe"
    assert data["basic"]["email"] == "john@example.com"
    assert len(data["education"]) == 1
    assert len(data["experiences"]) == 1


def test_parse_nonexistent_file():
    """Test parsing a nonexistent file."""
    with pytest.raises(FileNotFoundError):
        ResumeParser("nonexistent.yaml")


def test_parse_invalid_yaml(tmp_path):
    """Test parsing an invalid YAML file."""
    invalid_path = tmp_path / "invalid.yaml"
    invalid_path.write_text("invalid: yaml: content: -")
    parser = ResumeParser(str(invalid_path))
    with pytest.raises(InvalidYAMLError):
        parser.parse()


def test_parse_missing_required_field(tmp_path):
    """Test parsing a resume with missing required fields."""
    invalid_path = tmp_path / "invalid_resume.yaml"
    invalid_path.write_text(
        """
basic:
  name: John Doe
education:
  - name: MSc
    school: Example University
    startdate: 09/2015
experiences:
  - company: TechCorp
    titles:
      - name: Senior Engineer
    highlights:
      - Led development team
"""
    )
    parser = ResumeParser(str(invalid_path))
    with pytest.raises(MissingRequiredFieldError) as exc_info:
        parser.parse()
    assert "Missing required field 'email'" in str(exc_info.value)


def test_parse_invalid_experiences_structure(tmp_path):
    """Test parsing a resume with invalid experiences structure."""
    invalid_path = tmp_path / "invalid_experiences.yaml"
    invalid_path.write_text(
        """
basic:
  name: John Doe
  email: john@example.com
education:
  - name: MSc
    school: Example University
    startdate: 09/2015
    enddate: 06/2017
experiences: invalid
"""
    )
    parser = ResumeParser(str(invalid_path))
    with pytest.raises(InvalidYAMLError) as exc_info:
        parser.parse()
    assert "'experiences' must be a list" in str(exc_info.value) 