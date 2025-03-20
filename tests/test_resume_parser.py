"""Unit tests for the Resume Parser module."""

import pytest
import yaml
from pathlib import Path

from resume_tailor.core.resume_parser import (
    InvalidYAMLError,
    MissingRequiredFieldError,
    ResumeParser,
    ResumeParserError,
)


@pytest.fixture
def sample_resume_data():
    """Create sample resume data for testing."""
    return {
        "basic": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890"
        },
        "objective": "Software Engineer position",
        "education": [
            {
                "name": "Computer Science",
                "school": "University of Example",
                "startdate": "2015",
                "enddate": "2019",
                "highlights": ["GPA: 3.8", "Dean's List"]
            }
        ],
        "experiences": [
            {
                "company": "Tech Corp",
                "titles": [
                    {
                        "name": "Software Engineer",
                        "startdate": "2019",
                        "enddate": "Present"
                    }
                ],
                "highlights": ["Led development of key features"]
            }
        ]
    }


@pytest.fixture
def sample_resume_file(tmp_path, sample_resume_data):
    """Create a temporary YAML file with sample resume data."""
    file_path = tmp_path / "test_resume.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(sample_resume_data, f)
    return str(file_path)


def test_parse_valid_resume(sample_resume_file):
    """Test parsing a valid resume file."""
    parser = ResumeParser(sample_resume_file)
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


def test_parse_missing_experience_fields(tmp_path):
    """Test parsing a resume with missing experience fields."""
    invalid_path = tmp_path / "invalid_experience.yaml"
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
experiences:
  - company: TechCorp
    # Missing titles and highlights
"""
    )
    parser = ResumeParser(str(invalid_path))
    with pytest.raises(MissingRequiredFieldError) as exc_info:
        parser.parse()
    assert "Missing required field 'titles' in experience entry" in str(exc_info.value)


def test_parse_missing_education_fields(tmp_path):
    """Test parsing a resume with missing education fields."""
    invalid_path = tmp_path / "invalid_education.yaml"
    invalid_path.write_text(
        """
basic:
  name: John Doe
  email: john@example.com
education:
  - name: MSc
    school: Example University
    # Missing startdate and enddate
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
    assert "Missing required field 'startdate' in education entry" in str(exc_info.value)


def test_parse_invalid_titles_structure(tmp_path):
    """Test parsing a resume with invalid titles structure."""
    invalid_path = tmp_path / "invalid_titles.yaml"
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
experiences:
  - company: TechCorp
    titles: "not a list"
    highlights:
      - Led development team
"""
    )
    parser = ResumeParser(str(invalid_path))
    with pytest.raises(InvalidYAMLError) as exc_info:
        parser.parse()
    assert "'titles' must be a list" in str(exc_info.value)


def test_parse_invalid_highlights_structure(tmp_path):
    """Test parsing a resume with invalid highlights structure."""
    invalid_path = tmp_path / "invalid_highlights.yaml"
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
experiences:
  - company: TechCorp
    titles:
      - name: Senior Engineer
    highlights: "not a list"
"""
    )
    parser = ResumeParser(str(invalid_path))
    with pytest.raises(InvalidYAMLError) as exc_info:
        parser.parse()
    assert "'highlights' must be a list" in str(exc_info.value) 