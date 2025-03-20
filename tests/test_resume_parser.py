"""Unit tests for the Resume Parser module."""

import os
import pytest
import yaml
from pathlib import Path

from resume_tailor.resume_parser import (
    InvalidYAMLError,
    MissingRequiredFieldError,
    ResumeParser,
    ResumeParserError,
)


@pytest.fixture
def sample_resume_file(tmp_path):
    """Create a sample resume file for testing."""
    resume_data = {
        "basic": {
            "name": "John Doe",
            "email": "john@example.com",
        },
        "education": [
            {
                "name": "Computer Science",
                "school": "Example University",
                "startdate": "2015",
                "enddate": "2019",
            }
        ],
        "experiences": [
            {
                "company": "Tech Corp",
                "titles": [
                    {
                        "name": "Software Engineer",
                        "startdate": "2019",
                        "enddate": "Present",
                    }
                ],
                "highlights": ["Developed features", "Fixed bugs"],
            }
        ],
    }

    file_path = os.path.join(tmp_path, "test_resume.yaml")
    with open(file_path, "w") as f:
        yaml.dump(resume_data, f)
    return file_path


def test_parse_valid_resume(sample_resume_file):
    """Test parsing a valid resume file."""
    parser = ResumeParser(sample_resume_file)
    data = parser.parse()
    assert data.basic["name"] == "John Doe"
    assert data.basic["email"] == "john@example.com"
    assert len(data.education) == 1
    assert data.education[0].name == "Computer Science"
    assert len(data.experiences) == 1
    assert data.experiences[0].company == "Tech Corp"


def test_parse_nonexistent_file():
    """Test parsing a nonexistent file."""
    with pytest.raises(FileNotFoundError):
        ResumeParser("nonexistent.yaml")


def test_parse_invalid_yaml(tmp_path):
    """Test parsing invalid YAML."""
    file_path = os.path.join(tmp_path, "invalid.yaml")
    with open(file_path, "w") as f:
        f.write("invalid: yaml: content: -")

    parser = ResumeParser(file_path)
    with pytest.raises(InvalidYAMLError):
        parser.parse()


def test_parse_missing_required_field(tmp_path):
    """Test parsing YAML with missing required field."""
    resume_data = {
        "basic": {
            "name": "John Doe",
            # Missing email
        },
        "education": [
            {
                "name": "Computer Science",
                "school": "Example University",
                "startdate": "2015",
                "enddate": "2019",
            }
        ],
        "experiences": [
            {
                "company": "Tech Corp",
                "titles": [
                    {
                        "name": "Software Engineer",
                        "startdate": "2019",
                        "enddate": "Present",
                    }
                ],
                "highlights": ["Developed features"],
            }
        ],
    }

    file_path = os.path.join(tmp_path, "missing_field.yaml")
    with open(file_path, "w") as f:
        yaml.dump(resume_data, f)

    parser = ResumeParser(file_path)
    with pytest.raises(MissingRequiredFieldError):
        parser.parse()


def test_parse_invalid_experiences_structure(tmp_path):
    """Test parsing YAML with invalid experiences structure."""
    resume_data = {
        "basic": {"name": "John Doe", "email": "john@example.com"},
        "education": [
            {
                "name": "Computer Science",
                "school": "Example University",
                "startdate": "2015",
                "enddate": "2019",
            }
        ],
        "experiences": "not a list",  # Invalid structure
    }

    file_path = os.path.join(tmp_path, "invalid_structure.yaml")
    with open(file_path, "w") as f:
        yaml.dump(resume_data, f)

    parser = ResumeParser(file_path)
    with pytest.raises(InvalidYAMLError):
        parser.parse()


def test_parse_missing_experience_fields(tmp_path):
    """Test parsing YAML with missing experience fields."""
    resume_data = {
        "basic": {"name": "John Doe", "email": "john@example.com"},
        "education": [
            {
                "name": "Computer Science",
                "school": "Example University",
                "startdate": "2015",
                "enddate": "2019",
            }
        ],
        "experiences": [
            {
                "company": "Tech Corp",
                # Missing titles and highlights
            }
        ],
    }

    file_path = os.path.join(tmp_path, "missing_exp_fields.yaml")
    with open(file_path, "w") as f:
        yaml.dump(resume_data, f)

    parser = ResumeParser(file_path)
    with pytest.raises(MissingRequiredFieldError):
        parser.parse()


def test_parse_missing_education_fields(tmp_path):
    """Test parsing YAML with missing education fields."""
    resume_data = {
        "basic": {"name": "John Doe", "email": "john@example.com"},
        "education": [
            {
                "name": "Computer Science",
                "school": "Example University",
                # Missing dates
            }
        ],
        "experiences": [
            {
                "company": "Tech Corp",
                "titles": [
                    {
                        "name": "Software Engineer",
                        "startdate": "2019",
                        "enddate": "Present",
                    }
                ],
                "highlights": ["Developed features"],
            }
        ],
    }

    file_path = os.path.join(tmp_path, "missing_edu_fields.yaml")
    with open(file_path, "w") as f:
        yaml.dump(resume_data, f)

    parser = ResumeParser(file_path)
    with pytest.raises(MissingRequiredFieldError):
        parser.parse()


def test_parse_invalid_titles_structure(tmp_path):
    """Test parsing YAML with invalid titles structure."""
    resume_data = {
        "basic": {"name": "John Doe", "email": "john@example.com"},
        "education": [
            {
                "name": "Computer Science",
                "school": "Example University",
                "startdate": "2015",
                "enddate": "2019",
            }
        ],
        "experiences": [
            {
                "company": "Tech Corp",
                "titles": "not a list",  # Invalid structure
                "highlights": ["Developed features"],
            }
        ],
    }

    file_path = os.path.join(tmp_path, "invalid_titles.yaml")
    with open(file_path, "w") as f:
        yaml.dump(resume_data, f)

    parser = ResumeParser(file_path)
    with pytest.raises(InvalidYAMLError):
        parser.parse()


def test_parse_invalid_highlights_structure(tmp_path):
    """Test parsing YAML with invalid highlights structure."""
    resume_data = {
        "basic": {"name": "John Doe", "email": "john@example.com"},
        "education": [
            {
                "name": "Computer Science",
                "school": "Example University",
                "startdate": "2015",
                "enddate": "2019",
            }
        ],
        "experiences": [
            {
                "company": "Tech Corp",
                "titles": [
                    {
                        "name": "Software Engineer",
                        "startdate": "2019",
                        "enddate": "Present",
                    }
                ],
                "highlights": "not a list",  # Invalid structure
            }
        ],
    }

    file_path = os.path.join(tmp_path, "invalid_highlights.yaml")
    with open(file_path, "w") as f:
        yaml.dump(resume_data, f)

    parser = ResumeParser(file_path)
    with pytest.raises(InvalidYAMLError):
        parser.parse() 