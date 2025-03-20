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

    TAILOR_PROMPT = """You are an expert resume writer. Your task is to tailor a resume for a specific job description.
You will be provided with a master resume in YAML format and a job description.
Your goal is to create a tailored version of the resume that:
1. Highlights experiences and skills most relevant to the job
2. Preserves all required fields (basic info, education, etc.)
3. Uses professional language
4. Optimizes content for ATS systems

IMPORTANT FORMAT REQUIREMENTS:
- All highlights MUST be simple strings, not dictionaries
- For education highlights, combine thesis and coursework into single strings
- For experience highlights, combine all details into single strings
- Do not use nested structures in highlights

Example of correct highlight format:
education:
  - name: Computer Science
    school: Example University
    startdate: 2018
    enddate: 2022
    highlights:
      - "Thesis: Distributed Systems in Cloud Computing. Coursework: algorithms, distributed systems"
      - "GPA: 3.8"

experiences:
  - company: Example Corp
    location: San Francisco
    title: Software Engineer
    startdate: 2022
    enddate: Present
    highlights:
      - "Led development of key features and implemented CI/CD pipeline"
      - "Optimized database performance by 40%"

Job Description:
{job_description}

Master Resume (YAML):
{resume_yaml}

Instructions:
1. Analyze the job requirements
2. Select and prioritize relevant experiences
3. Adjust highlight points to match job requirements
4. Keep all dates, contact info, and education details unchanged
5. Only modify the content of highlights and skills to match the job
6. Ensure all highlights are simple strings, not dictionaries

Return the tailored content in any format that clearly shows the changes.
"""

    FORMAT_PROMPT = """You are a YAML formatting expert. Your task is to format the provided resume content into proper YAML structure.

The output MUST follow these requirements:
1. Be valid YAML syntax
2. Have these fields at the root level:
   - basic: Dictionary containing basic information
   - education: List of education entries
   - experiences: List of work experiences
3. NOT start with a list item (-)
4. NOT use a root-level key (like 'resume:')
5. NOT use markdown formatting (no ```yaml or ```)

Example of correct structure:
basic:
  name: John Doe
  email: john@example.com
education:
  - name: Computer Science
    school: Example University
    startdate: 2018
    enddate: 2022
experiences:
  - company: Example Corp
    location: San Francisco
    title: Software Engineer
    startdate: 2022
    enddate: Present
    highlights:
      - "Led development of key features and implemented CI/CD pipeline"

Resume Content to Format:
{content}

Return ONLY the raw YAML content, no markdown formatting or other text.
"""

    def __init__(self, llm_client: LLMClient) -> None:
        """Initialize the Resume Tailor.

        Args:
            llm_client: The LLM client to use for generating responses.
        """
        self.llm_client = llm_client

    def _clean_yaml(self, yaml_str: str) -> str:
        """Clean YAML string by removing markdown formatting.

        Args:
            yaml_str: YAML string that might contain markdown formatting.

        Returns:
            Cleaned YAML string.
        """
        # Remove markdown code block markers
        lines = yaml_str.strip().split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines[-1].startswith('```'):
            lines = lines[:-1]
        
        # Remove language identifier if present
        if lines[0].strip() in ['yaml', 'YAML']:
            lines = lines[1:]
            
        return '\n'.join(lines).strip()

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
            # Clean the YAML string first
            cleaned_yaml = self._clean_yaml(yaml_str)
            data = yaml.safe_load(cleaned_yaml)
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

        try:
            # Step 1: Get tailored content
            tailor_prompt = self.TAILOR_PROMPT.format(
                job_description=job_description,
                resume_yaml=resume_yaml,
            )
            tailor_response = self.llm_client.generate(tailor_prompt)
            tailored_content = tailor_response["content"]

            # Step 2: Format the content into proper YAML
            format_prompt = self.FORMAT_PROMPT.format(
                content=tailored_content
            )
            format_response = self.llm_client.generate(format_prompt)
            
            # Parse and validate the formatted YAML
            return self._validate_yaml(format_response["content"])

        except (yaml.YAMLError, KeyError, InvalidOutputError) as e:
            raise InvalidOutputError("Failed to generate valid YAML")
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