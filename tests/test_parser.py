"""Unit tests for the ResumeParser module."""

import os
import pytest
import yaml
from pathlib import Path
from resume_tailor.parser import ResumeParser, Resume, Experience, Title, Education, Publication, SkillCategory


@pytest.fixture
def sample_resume_data():
    """Create sample resume data for testing."""
    return {
        "editing": False,
        "debug": False,
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
                "skip_name": False,
                "location": "San Francisco, CA",
                "titles": [
                    {
                        "name": "Software Engineer",
                        "startdate": "2019",
                        "enddate": "Present"
                    }
                ],
                "highlights": ["Led development of key features"]
            }
        ],
        "projects": [],
        "publications": [
            {
                "authors": "John Doe",
                "title": "Example Paper",
                "conference": "Example Conf",
                "location": "Virtual",
                "date": "2020"
            }
        ],
        "skills": [
            {
                "category": "Programming",
                "skills": ["Python", "JavaScript"]
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


def test_load_master_resume(sample_resume_file):
    """Test loading a master resume from YAML file."""
    parser = ResumeParser()
    resume = parser.load_master_resume(sample_resume_file)
    
    assert isinstance(resume, Resume)
    assert resume.editing is False
    assert resume.debug is False
    assert resume.basic["name"] == "John Doe"
    assert resume.objective == "Software Engineer position"
    assert len(resume.education) == 1
    assert len(resume.experiences) == 1
    assert len(resume.publications) == 1
    assert len(resume.skills) == 1


def test_load_master_resume_invalid_file():
    """Test loading resume from non-existent file."""
    parser = ResumeParser()
    with pytest.raises(Exception) as exc_info:
        parser.load_master_resume("nonexistent.yaml")
    assert "Failed to parse resume" in str(exc_info.value)


def test_load_master_resume_invalid_yaml(tmp_path):
    """Test loading resume from invalid YAML file."""
    parser = ResumeParser()
    invalid_file = tmp_path / "invalid.yaml"
    with open(invalid_file, 'w') as f:
        f.write("invalid: yaml: content: -")
    
    with pytest.raises(Exception) as exc_info:
        parser.load_master_resume(str(invalid_file))
    assert "Failed to parse resume" in str(exc_info.value)


def test_save_tailored_resume(tmp_path, sample_resume_data):
    """Test saving a tailored resume to YAML file."""
    parser = ResumeParser()
    resume = Resume(**sample_resume_data)
    output_file = tmp_path / "output.yaml"
    
    parser.save_tailored_resume(resume, str(output_file))
    
    assert output_file.exists()
    with open(output_file, 'r') as f:
        saved_data = yaml.safe_load(f)
    assert saved_data == sample_resume_data


def test_save_tailored_resume_invalid_path(sample_resume_data):
    """Test saving resume to invalid path."""
    parser = ResumeParser()
    resume = Resume(**sample_resume_data)
    
    with pytest.raises(Exception) as exc_info:
        parser.save_tailored_resume(resume, "/invalid/path/resume.yaml")
    assert "Failed to save resume" in str(exc_info.value)


def test_resume_model_validation():
    """Test Resume model validation."""
    # Test missing required field
    invalid_data = {
        "editing": False,
        "debug": False,
        "basic": {"name": "John Doe"},
        "objective": "Test",
        "education": [],
        "experiences": [],
        "projects": [],
        "publications": [],
        "skills": []
    }
    
    # Test with invalid type for basic field
    invalid_data["basic"] = "not a dict"
    with pytest.raises(Exception):
        Resume(**invalid_data) 