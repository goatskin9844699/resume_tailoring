"""YAML parsing module for resume-tailor."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import yaml
from pathlib import Path


class Title(BaseModel):
    """Job title information."""
    name: str
    startdate: str
    enddate: str


class Experience(BaseModel):
    """Work experience information."""
    company: str
    skip_name: bool
    location: str
    titles: List[Title]
    highlights: List[str]


class Education(BaseModel):
    """Education information."""
    name: str
    school: str
    startdate: str
    enddate: str
    highlights: List[str]


class Publication(BaseModel):
    """Publication information."""
    authors: str
    title: str
    conference: str
    location: str
    date: str


class SkillCategory(BaseModel):
    """Skill category information."""
    category: str
    skills: List[str]


class Resume(BaseModel):
    """Resume data model."""
    editing: bool
    debug: bool
    basic: Dict[str, Any]
    objective: str
    education: List[Education]
    experiences: List[Experience]
    projects: List[Any]
    publications: List[Publication]
    skills: List[SkillCategory]


class ResumeParser:
    """Parser for resume YAML files."""

    def load_master_resume(self, file_path: str) -> Resume:
        """
        Load and parse a master resume from a YAML file.

        Args:
            file_path: Path to the YAML file

        Returns:
            Resume object containing the parsed data

        Raises:
            ParserError: If there's an error parsing the file
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            return Resume(**data)
        except Exception as e:
            raise Exception(f"Failed to parse resume: {str(e)}")

    def save_tailored_resume(self, resume: Resume, file_path: str) -> None:
        """
        Save a tailored resume to a YAML file.

        Args:
            resume: Resume object to save
            file_path: Path where to save the YAML file

        Raises:
            ParserError: If there's an error saving the file
        """
        try:
            with open(file_path, 'w') as f:
                yaml.dump(resume.model_dump(), f, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to save resume: {str(e)}") 