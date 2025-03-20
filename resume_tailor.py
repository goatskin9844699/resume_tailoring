"""Resume Tailor module for customizing resumes based on job descriptions."""

from typing import Any, Dict

from resume_parser import ResumeParser


class ResumeTailorError(Exception):
    """Base exception for Resume Tailor errors."""

    pass


class InvalidOutputError(ResumeTailorError):
    """Raised when the LLM output is invalid."""

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

    def __init__(self) -> None:
        """Initialize the Resume Tailor."""
        self.parser = ResumeParser("dummy.yaml")  # For validation only

    def tailor(self, job_description: str, resume_yaml: str) -> Dict[str, Any]:
        """Tailor the resume for a specific job description.

        Args:
            job_description: The job description text.
            resume_yaml: The master resume in YAML format.

        Returns:
            Dict containing the tailored resume data.

        Raises:
            InvalidOutputError: If the LLM output is invalid.
        """
        # Prepare the prompt
        prompt = self.PROMPT_TEMPLATE.format(
            job_description=job_description,
            resume_yaml=resume_yaml,
        )

        # TODO: Call LLM API with prompt
        # For now, we'll raise NotImplementedError
        raise NotImplementedError("LLM integration not implemented yet")

        # TODO: Parse and validate the LLM output
        # output_yaml = llm_response
        # try:
        #     return self.parser.parse(output_yaml)
        # except Exception as e:
        #     raise InvalidOutputError(f"Invalid LLM output: {str(e)}") 