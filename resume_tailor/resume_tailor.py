"""Resume Tailor module for customizing resumes based on job descriptions."""

from pathlib import Path
from typing import Any, Dict, Protocol

import yaml
from pydantic import ValidationError
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
5. Creates a compelling objective statement that aligns with the job requirements
6. Reflects the original writing style of the master resume while honoring all other requirements

IMPORTANT FORMAT REQUIREMENTS:
- All highlights MUST be simple strings, not dictionaries
- For education highlights, include thesis and coursework into single strings but separate bullet points
- For experience highlights, combine all details into single strings
- Do not use nested structures in highlights
- Include an objective statement that summarizes the candidate's fit for the role

OBJECTIVE STATEMENT REQUIREMENTS:
- Should be 2-3 sentences long
- Must highlight relevant experience and skills
- Should align with the job requirements if applicable, but must be true to the content in the master resume
- Must be specific to the role and company but true to the nature of the master resume
- Should demonstrate value proposition
- Must be professional and engaging
- Should include relevant keywords from the job description if applicable
- Should be written in the similar style as the master resume

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

Example of correct highlight format:
basic:
  name: John Doe
  email: john@example.com
objective: "Senior Software Engineer with 8+ years of experience in full-stack development, specializing in Python and cloud technologies. Proven track record of building scalable applications and leading development teams. Passionate about creating efficient, maintainable code and mentoring junior developers."

education:
  - name: Computer Science
    school: Example University
    startdate: "2018"
    enddate: "2022"
    highlights:
      - "Thesis: Distributed Systems in Cloud Computing. Coursework: algorithms, distributed systems"
      - "Relevant coursework: algorithms, distributed systems"

experiences:
  - company: Example Corp
    location: San Francisco
    title: Software Engineer
    startdate: "2022"
    enddate: "Present"
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

    FORMAT_PROMPT = """You are a YAML formatting expert. Your task is to format the provided resume content into proper YAML structure. Do not change the content of the resume, only format it into proper YAML structure.

The output MUST follow these requirements:
1. Be valid YAML syntax
2. Have these fields at the root level:
   - basic: Dictionary containing basic information
   - objective: String containing the career objective
   - education: List of education entries
   - experiences: List of work experiences
   - skills: List of skill categories (each with category and skills fields)
   - publications: List of publication entries (each with authors, title, location, and date)
3. NOT start with a list item (-)
4. NOT use a root-level key (like 'resume:')
5. NOT use markdown formatting (no ```yaml or ```)
6. Use proper indentation (2 spaces)
7. All dates must be strings (e.g., "2023" not 2023)
8. All lists must be properly indented under their parent key

SECTION REQUIREMENTS:
1. Basic Section:
   - Must contain basic information
   - Example format:
     basic:
       name: "John Doe"
       email: "john@example.com"

2. Objective Section:
   - Must be a single string
   - Should be 2-3 sentences
   - Example format:
     objective: "Senior Software Engineer with 8+ years of experience in full-stack development, specializing in Python and cloud technologies. Proven track record of building scalable applications and leading development teams."

3. Education Section:
   - Must contain only education entries
   - Each entry MUST have: name, school, startdate, enddate
   - Optional: highlights
   - Example format:
     education:
       - name: "Computer Science"
         school: "Example University"
         startdate: "2018"
         enddate: "2022"
         highlights:
           - "Thesis: Distributed Systems"

4. Experiences Section:
   - Must contain only work experience entries
   - Each entry MUST have: company, title, startdate, enddate, highlights
   - Optional: location
   - Example format:
     experiences:
       - company: "Example Corp"
         title: "Software Engineer"
         startdate: "2022"
         enddate: "Present"
         highlights:
           - "Led development of key features"

5. Skills Section:
   - Must contain only skill categories
   - Each category MUST have: category, skills
   - Example format:
     skills:
       - category: "Technical"
         skills:
           - "Python"
           - "Django"

6. Publications Section:
   - Must contain only publication entries
   - Each entry MUST have: authors, title, location, date
   - Example format:
     publications:
       - authors: "John Doe, Jane Smith"
         title: "Modern Web Development"
         location: "Conference 2023"
         date: "2023"

IMPORTANT STRUCTURE RULES:
- The root level must be a dictionary (no list items at root)
- Each section (education, experiences, etc.) must be a list
- List items must be indented with 2 spaces from their parent
- All dates must be in quotes
- All highlights must be strings, not dictionaries
- DO NOT mix entries between sections (e.g., don't put experiences in education)

Example of correct structure:
basic:
  name: John Doe
  email: john@example.com
objective: "Senior Software Engineer with 8+ years of experience in full-stack development, specializing in Python and cloud technologies. Proven track record of building scalable applications and leading development teams."
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
      - "Led development of key features and implemented CI/CD pipeline"
skills:
  - category: "Technical"
    skills:
      - "Python"
      - "Django"
      - "PostgreSQL"
  - category: "Non-Technical"
    skills:
      - "Communication"
      - "Leadership"
publications:
  - authors: "John Doe, Jane Smith"
    title: "Modern Web Development Practices"
    location: "Conference: WebDev Conference 2023, San Francisco, USA"
    date: "2023"

Resume Content to Format:
{content}

Return ONLY the raw YAML content, no markdown formatting or other text. Make sure to follow the structure exactly as shown in the example.
"""

    def __init__(self, llm_client: LLMClient) -> None:
        """Initialize the Resume Tailor.

        Args:
            llm_client: LLM client to use for generating content.
        """
        self.llm_client = llm_client

    def _clean_yaml(self, yaml_str: str) -> str:
        """Clean YAML string by removing code blocks and extra whitespace.

        Args:
            yaml_str: YAML string to clean.

        Returns:
            Cleaned YAML string.
        """
        # Remove markdown code blocks if present
        if yaml_str.startswith('```'):
            # Remove opening code block
            yaml_str = yaml_str.split('\n', 1)[1]
            # Remove closing code block if present
            if yaml_str.endswith('```'):
                yaml_str = yaml_str[:-3]
            # Remove language identifier if present
            if yaml_str.startswith('yaml'):
                yaml_str = yaml_str[4:]
            yaml_str = yaml_str.strip()

        return yaml_str

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

            # Validate skills structure
            if "skills" in data and not isinstance(data["skills"], list):
                raise InvalidOutputError("'skills' must be a list of skill categories")

            try:
                return Resume(**data)
            except ValidationError as e:
                raise InvalidOutputError("Invalid resume format")

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
        """Save the tailored resume to a file.

        Args:
            resume: Resume object to save.
            file_path: Path to save the resume to.
        """
        # Convert resume to dictionary
        resume_dict = resume.model_dump()

        # Save to file
        with open(file_path, 'w') as f:
            yaml.dump(resume_dict, f, sort_keys=False)


__all__ = [
    'LLMClient',
    'ResumeTailor',
    'ResumeTailorError',
    'InvalidOutputError',
] 