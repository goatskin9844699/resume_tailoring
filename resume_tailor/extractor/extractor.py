"""Job description extraction module."""

from typing import Dict, Optional
from urllib.parse import urlparse
from ..llm.client import LLMClient
from ..exceptions import ExtractorError
from .scraper import WebScraper
import json


class JobDescriptionExtractor:
    """Extracts structured data from job descriptions."""

    def __init__(self, llm_client: LLMClient, scraper: Optional[WebScraper] = None):
        """
        Initialize the extractor.

        Args:
            llm_client: LLM client for extracting structured data
            scraper: Optional WebScraper instance for fetching content
        """
        self.llm = llm_client
        self.scraper = scraper or WebScraper()

    def extract(self, url: str) -> Dict:
        """
        Extract structured data from a job description URL.

        Args:
            url: URL of the job posting

        Returns:
            Structured job description data containing:
            - company: Company name
            - title: Job title
            - summary: Job summary
            - responsibilities: List of responsibilities
            - requirements: List of requirements
            - technical_skills: List of technical skills
            - non_technical_skills: List of non-technical skills
            - ats_keywords: List of ATS-optimized keywords

        Raises:
            ExtractorError: If there's an error extracting the data
        """
        if not self._is_valid_url(url):
            raise ExtractorError("Invalid URL")

        try:
            # Fetch and clean content
            content = self.scraper.fetch_content(url)
            
            # Generate prompt for LLM
            prompt = self._generate_prompt(content)
            
            # Get structured data from LLM
            llm_response = self.llm.generate(prompt)
            print(f"LLM response: {llm_response}")
            
            # Handle both wrapped and unwrapped responses
            if isinstance(llm_response, dict):
                if "content" in llm_response and isinstance(llm_response["content"], str):
                    try:
                        job_data = json.loads(llm_response["content"])
                    except json.JSONDecodeError:
                        raise ExtractorError("Invalid JSON response from LLM")
                elif "response" in llm_response and isinstance(llm_response["response"], str):
                    try:
                        job_data = json.loads(llm_response["response"])
                    except json.JSONDecodeError:
                        raise ExtractorError("Invalid JSON response from LLM")
                else:
                    job_data = llm_response
            else:
                raise ExtractorError("Invalid response format from LLM")
            
            # Validate response
            if not job_data or not self._validate_job_data(job_data):
                print(f"Invalid job data: {job_data}")
                raise ExtractorError("Invalid or incomplete job description data")
                
            return job_data
            
        except Exception as e:
            raise ExtractorError(f"Failed to extract job description: {str(e)}")

    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if the given string is a valid URL.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _generate_prompt(self, content: str) -> str:
        """
        Generate the prompt for the LLM.

        Args:
            content: Cleaned job posting content

        Returns:
            Formatted prompt for the LLM
        """
        return f"""You are a precise job description parser. Your task is to extract and structure all information from the job posting while maintaining perfect accuracy and completeness.

Think of yourself as a high-precision scanner that:
- Captures every detail exactly as written
- Preserves all technical specifications precisely
- Maintains the original context and relationships
- Includes every requirement and qualification

Job Posting Content:
{content}

Your goal is to create a complete, accurate representation of this job posting. When extracting information:
- Keep every technical detail exactly as written (e.g., "Python 3.8+" not just "Python")
- Preserve all version numbers, frameworks, and specifications
- Include every requirement, even if it seems redundant
- Maintain the exact wording of all qualifications
- Keep all bullet points and nested information

Output Format:
{{
    "company": "Company name",
    "title": "Job title",
    "summary": "Complete job summary",
    "responsibilities": ["List of responsibilities"],
    "requirements": ["List of requirements"],
    "technical_skills": ["List of technical skills"],
    "non_technical_skills": ["List of non-technical skills"],
    "ats_keywords": ["Keywords for ATS"],
    "is_complete": boolean,  # Set to false if content appears truncated
    "truncation_note": "string"  # Describe what appears to be missing
}}

Examples of Good Extraction (Complete Content):

Good:
Original: "Must have 5+ years of experience with Python 3.8+ and Django 4.2+, including experience with Django REST framework and PostgreSQL 14+"
Extracted: "5+ years of experience with Python 3.8+ and Django 4.2+, including experience with Django REST framework and PostgreSQL 14+"

Bad:
Original: "Must have 5+ years of experience with Python 3.8+ and Django 4.2+, including experience with Django REST framework and PostgreSQL 14+"
Extracted: "Python and Django experience"  # Lost critical version information

Good:
Original: "Experience with microservices architecture, including containerization (Docker) and orchestration (Kubernetes)"
Extracted: "Experience with microservices architecture, including containerization (Docker) and orchestration (Kubernetes)"

Bad:
Original: "Experience with microservices architecture, including containerization (Docker) and orchestration (Kubernetes)"
Extracted: "Microservices experience"  # Lost specific technologies

Example of Good Extraction (Truncated Content):
Original: "As a Senior Developer, you'll be responsible for... [content ends abruptly]"
Extracted: {{
    "title": "Senior Developer",
    "summary": "Role description appears truncated",
    "responsibilities": ["Content appears truncated"],
    "requirements": ["Must infer from available content"],
    "is_complete": false,
    "truncation_note": "Content ends abruptly after initial role description. Missing detailed responsibilities and requirements."
}}

Remember:
- Extract all available information even if content is truncated
- Set is_complete to false if you detect any truncation
- Describe missing sections in truncation_note
- Provide as much detail as possible from available content
- Never make up or infer missing information
- You are a precision tool - accuracy is everything
- Include everything you see, even if it seems redundant
- If content appears truncated, note what might be missing
- Preserve the exact wording of all technical specifications
- Maintain the original context of all requirements"""

    def _validate_job_data(self, data: Dict) -> bool:
        """
        Validate the structure and content of job data.

        Args:
            data: Job data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "company", "title", "summary",
            "responsibilities", "requirements",
            "technical_skills", "non_technical_skills",
            "ats_keywords", "is_complete", "truncation_note"
        ]
        
        # Check all required fields exist
        if not all(field in data for field in required_fields):
            return False
            
        # Check all fields have non-empty values
        if any(not data[field] for field in required_fields if field not in ["is_complete", "truncation_note"]):
            return False
            
        # Check lists have at least 2 items
        list_fields = ["responsibilities", "requirements", "technical_skills", 
                      "non_technical_skills", "ats_keywords"]
        if any(not isinstance(data[field], list) or len(data[field]) < 2 
               for field in list_fields):
            return False
            
        # Check is_complete is boolean
        if not isinstance(data["is_complete"], bool):
            return False
            
        # Check truncation_note is string
        if not isinstance(data["truncation_note"], str):
            return False
            
        return True 