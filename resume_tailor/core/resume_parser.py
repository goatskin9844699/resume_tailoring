"""Resume Parser module for reading and validating YAML-formatted resume data."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from .models import Resume


class ResumeParserError(Exception):
    """Base exception for Resume Parser errors."""

    pass


class InvalidYAMLError(ResumeParserError):
    """Raised when YAML syntax is invalid."""

    pass


class MissingRequiredFieldError(ResumeParserError):
    """Raised when a required field is missing."""

    pass


class ResumeParser:
    """Parser for YAML-formatted resume data."""

    REQUIRED_FIELDS = {
        "basic": ["name", "email"],
        "education": ["name", "school", "startdate", "enddate"],
        "experiences": ["company", "titles", "highlights"],
    }

    def __init__(self, file_path: str) -> None:
        """Initialize the Resume Parser.

        Args:
            file_path: Path to the YAML resume file.

        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")

    def parse(self) -> Resume:
        """Parse and validate the resume YAML file.

        Returns:
            Resume object containing the parsed resume data.

        Raises:
            InvalidYAMLError: If YAML syntax is invalid.
            MissingRequiredFieldError: If required fields are missing.
        """
        try:
            with open(self.file_path, "r") as f:
                data = yaml.safe_load(f)
        except (ParserError, ScannerError) as e:
            raise InvalidYAMLError(f"Invalid YAML syntax: {str(e)}") from e

        if not isinstance(data, dict):
            raise InvalidYAMLError("YAML must contain a dictionary at the root level")

        self._validate_required_fields(data)
        return Resume(**data)

    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """Validate that all required fields are present.

        Args:
            data: The parsed YAML data.

        Raises:
            MissingRequiredFieldError: If required fields are missing.
        """
        for section, required in self.REQUIRED_FIELDS.items():
            if section not in data:
                raise MissingRequiredFieldError(f"Missing required section: {section}")

            if section == "experiences":
                if not isinstance(data[section], list):
                    raise InvalidYAMLError("'experiences' must be a list")
                for exp in data[section]:
                    self._validate_experience_fields(exp)
            elif section == "education":
                if not isinstance(data[section], list):
                    raise InvalidYAMLError("'education' must be a list")
                for edu in data[section]:
                    self._validate_education_fields(edu)
            else:
                for field in required:
                    if field not in data[section]:
                        raise MissingRequiredFieldError(
                            f"Missing required field '{field}' in section '{section}'"
                        )

    def _validate_experience_fields(self, experience: Dict[str, Any]) -> None:
        """Validate required fields in an experience entry.

        Args:
            experience: A single experience entry.

        Raises:
            MissingRequiredFieldError: If required fields are missing.
        """
        for field in self.REQUIRED_FIELDS["experiences"]:
            if field not in experience:
                raise MissingRequiredFieldError(
                    f"Missing required field '{field}' in experience entry"
                )
            if field == "titles" and not isinstance(experience[field], list):
                raise InvalidYAMLError("'titles' must be a list")
            if field == "highlights" and not isinstance(experience[field], list):
                raise InvalidYAMLError("'highlights' must be a list")

    def _validate_education_fields(self, education: Dict[str, Any]) -> None:
        """Validate required fields in an education entry.

        Args:
            education: A single education entry.

        Raises:
            MissingRequiredFieldError: If required fields are missing.
        """
        for field in self.REQUIRED_FIELDS["education"]:
            if field not in education:
                raise MissingRequiredFieldError(
                    f"Missing required field '{field}' in education entry"
                ) 