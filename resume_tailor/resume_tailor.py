"""Resume Tailor module for customizing resumes based on job descriptions."""

from pathlib import Path
from typing import Any, Dict, Protocol

import yaml
from resume_tailor.resume_parser import ResumeParser
from resume_tailor.models import Resume
from resume_tailor.exceptions import InvalidOutputError


class LLMClient(Protocol):
    """Protocol for LLM clients."""

    def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            Dict containing the LLM's response.
        """
        ...


class ResumeTailorError(Exception):
    """Base exception for Resume Tailor errors."""

    pass


class ResumeTailor:
    """Tailor resumes based on job descriptions using LLM."""

    PROMPT_TEMPLATE = """You are an expert resume writer. Your task is to tailor a resume for a specific job description.
You will be provided with a master resume in YAML format and a job description.
Your goal is to create a tailored version of the resume that:
1. Highlights experiences and skills most relevant to the job
2. Maintains the exact same YAML structure as the input
3. Preserves all required fields (basic info, education, etc.)
4. Uses professional language
5. Optimizes content for ATS systems

The output MUST be valid YAML and follow the exact same structure as the input resume.

Job Description:
{job_description}

Master Resume (YAML):
{resume_yaml}

Instructions:
1. Analyze the job requirements
2. Select and prioritize relevant experiences
3. Adjust highlight points to match job requirements
4. Return a complete YAML resume with the same structure
5. Ensure all dates, contact info, and education details remain unchanged
6. Only modify the content of highlights and skills to match the job

Return ONLY the YAML content, no other text.
"""

    def __init__(self, llm_client: LLMClient) -> None:
        """Initialize the Resume Tailor.

        Args:
            llm_client: The LLM client to use for generating responses.
        """
        self.llm_client = llm_client

    def _validate_yaml(self, yaml_str: str) -> Resume:
        """Validate YAML content.

        Args:
            yaml_str: YAML content to validate.

        Returns:
            Resume object containing the parsed data.

        Raises:
            InvalidOutputError: If the YAML is invalid.
        """
        try:
            data = yaml.safe_load(yaml_str)
            if not isinstance(data, dict):
                raise InvalidOutputError("YAML must contain a dictionary at the root level")
            return Resume(**data)
        except yaml.YAMLError as e:
            raise InvalidOutputError(f"Invalid YAML syntax: {str(e)}")

    def tailor(self, job_description: str, resume_yaml: str) -> Resume:
        """Tailor the resume for a specific job description.

        Args:
            job_description: The job description text.
            resume_yaml: The master resume in YAML format.

        Returns:
            Resume object containing the tailored resume data.

        Raises:
            InvalidOutputError: If the LLM output is invalid.
        """
        # Validate input resume YAML
        self._validate_yaml(resume_yaml)

        # Prepare the prompt
        prompt = self.PROMPT_TEMPLATE.format(
            job_description=job_description,
            resume_yaml=resume_yaml,
        )

        try:
            # Get response from LLM
            response = self.llm_client.generate(prompt)

            # Parse and validate the response
            try:
                return self._validate_yaml(response["content"])
            except (yaml.YAMLError, KeyError, InvalidOutputError) as e:
                raise InvalidOutputError("Invalid YAML in LLM response")
        except InvalidOutputError:
            raise
        except Exception as e:
            raise InvalidOutputError("Failed to generate tailored resume")

    def save_tailored_resume(self, resume: Resume, file_path: str) -> None:
        """Save a tailored resume to a YAML file.

        Args:
            resume: Resume object to save
            file_path: Path where to save the YAML file

        Raises:
            InvalidOutputError: If there's an error saving the file
        """
        try:
            with open(file_path, 'w') as f:
                yaml.dump(resume.model_dump(), f, default_flow_style=False)
        except Exception as e:
            raise InvalidOutputError(f"Failed to save resume: {str(e)}")


__all__ = [
    'LLMClient',
    'ResumeTailor',
    'ResumeTailorError',
    'InvalidOutputError',
] 