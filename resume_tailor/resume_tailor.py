"""Resume Tailor module for customizing resumes based on job descriptions."""

import logging
from pathlib import Path
from typing import Any, Dict, Protocol

import yaml
from resume_tailor.resume_parser import ResumeParser
from resume_tailor.models import Resume
from resume_tailor.exceptions import InvalidOutputError

# Set up logging
logger = logging.getLogger(__name__)


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
2. Uses professional language
3. Optimizes content for ATS systems

BULLET POINT CRITERIA:
- Each highlight must be based on what is mentioned in the original resume
- Include how that experience demonstrates ability to perform job duties
- Ensure ATS screening compatibility by including relevant keywords
- Distinguish the resume by citing accomplishments and measurements of impact
- Statements should not be too long and wordy, and SHOULD NOT repeat action verbs
- Grammar, spelling, and sentence structure must be correct

FRAMEWORK FOR EXPERIENCE HIGHLIGHTS:
- Describe the SITUATION/TASK as a problem encountered
- Describe the ACTION taken
- Include analysis of opportunity, planning, preparation, and resources
- Use action words and avoid words like "participated in" or "monitored"
- Describe the RESULTS obtained
- State if results were presented to clients or senior management

ACTION VERB RULES:
- Planning skills: Conceived, Formed, Planned, Created, Formulated, Projected, Designed, Initiated, Revised, Developed, Innovated, Scheduled, Devised, Instituted, Solved, Engineered, Invented, Systemized, Established, Justified, Tailored, Estimated, Organized, Transformed, Experimented, Originated
- Directing employees: Administered, Determined, Ordered, Approved, Directed, Oversaw, Authorized, Guided, Prescribed, Conducted, Headed, Regulated, Controlled, Instructed, Specified, Decided, Led, Supervised, Delegated, Managed, Trained
- Assuming responsibility: Achieved, Developed, Operated, Adopted, Doubled, Overcome, Arranged, Established, Performed, Assembled, Evaluated, Prepared, Assumed, Experienced, Produced, Attended, Gathered, Received, Audited, Halted, Reduced, Built, Handled, Reviewed, Checked, Improved, Simplified, Classified, Implemented, Sold, Collected, Initiated, Transacted, Compiled, Installed, Tripled, Constructed, Integrated

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

Return the tailored content in any format that clearly shows the changes. Focus on content only, not structure.
"""

    FORMAT_PROMPT = """You are a YAML formatting expert. Your task is to format the provided resume content into proper YAML structure.

The output MUST follow these requirements:
1. Be valid YAML syntax
2. Use proper indentation (2 spaces)
3. All dates must be strings (e.g., "2023" not 2023)
4. All text values must be in quotes
5. All lists must be properly indented under their parent key

SECTION STRUCTURE:
1. Basic Information (REQUIRED):
   - name (REQUIRED)
   - email (REQUIRED)
   - phone (optional)
   - location (optional)

2. Education (REQUIRED, can be empty list):
   - name (REQUIRED)
   - school (REQUIRED)
   - startdate (REQUIRED)
   - enddate (REQUIRED)
   - highlights (optional)

3. Experiences (REQUIRED, can be empty list):
   - company (REQUIRED)
   - title (REQUIRED)
   - startdate (REQUIRED)
   - enddate (REQUIRED)
   - highlights (REQUIRED)
   - location (optional)

4. Skills (optional):
   - category (REQUIRED)
   - skills (REQUIRED)

5. Publications (optional):
   - authors (REQUIRED)
   - title (REQUIRED)
   - location (REQUIRED)
   - date (REQUIRED)

IMPORTANT RULES:
- The root level must be a dictionary
- Basic, education, and experiences sections are REQUIRED
- Include only the sections and fields that are present in the input
- Use proper indentation (2 spaces)
- All text values must be in quotes
- All dates must be in quotes
- All highlights must be strings, not dictionaries

Example of correct structure:
basic:
  name: "John Doe"
  email: "john@example.com"
education:
  - name: "Computer Science"
    school: "Example University"
    startdate: "2018"
    enddate: "2022"
experiences:
  - company: "Example Corp"
    location: "San Francisco"
    title: "Software Engineer"
    startdate: "2022"
    enddate: "Present"
    highlights:
      - "Led development of key features"
skills:
  - category: "Technical"
    skills:
      - "Python"
      - "Django"

Resume Content to Format:
{content}

Return ONLY the raw YAML content, no markdown formatting or other text. Include only the sections and fields that are present in the input.
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
            
            # Validate required fields
            if "basic" not in data or not isinstance(data["basic"], dict):
                raise InvalidOutputError("'basic' section is required and must be a dictionary")
            if "education" not in data:
                raise InvalidOutputError("'education' section is required")
            if not isinstance(data["education"], list):
                raise InvalidOutputError("'education' section must be a list")
            if "experiences" not in data:
                raise InvalidOutputError("'experiences' section is required")
            if not isinstance(data["experiences"], list):
                raise InvalidOutputError("'experiences' section must be a list")
            
            # Log warnings for missing optional fields
            if "skills" not in data:
                logger.warning("Missing skills section")
            if "publications" not in data:
                logger.warning("Missing publications section")
            
            # Validate skills structure if present
            if "skills" in data and not isinstance(data["skills"], list):
                raise InvalidOutputError("'skills' must be a list of skill categories")
            
            # Convert any integer dates to strings
            for section in ["education", "experiences"]:
                if section in data:
                    for entry in data[section]:
                        if "startdate" in entry and isinstance(entry["startdate"], int):
                            entry["startdate"] = str(entry["startdate"])
                        if "enddate" in entry and isinstance(entry["enddate"], int):
                            entry["enddate"] = str(entry["enddate"])
            
            # Ensure basic section has required fields
            required_basic_fields = ["name", "email"]
            for field in required_basic_fields:
                if field not in data["basic"]:
                    raise InvalidOutputError(f"Missing required field '{field}' in basic section")
            
            # Ensure education entries have required fields if not empty
            for entry in data["education"]:
                required_edu_fields = ["name", "school", "startdate", "enddate"]
                for field in required_edu_fields:
                    if field not in entry:
                        raise InvalidOutputError(f"Missing required field '{field}' in education entry")
            
            # Ensure experience entries have required fields if not empty
            for entry in data["experiences"]:
                required_exp_fields = ["company", "title", "startdate", "enddate", "highlights"]
                for field in required_exp_fields:
                    if field not in entry:
                        raise InvalidOutputError(f"Missing required field '{field}' in experience entry")
                if not isinstance(entry["highlights"], list):
                    raise InvalidOutputError("'highlights' must be a list in experience entry")
            
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