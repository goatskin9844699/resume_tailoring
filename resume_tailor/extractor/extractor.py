"""Job description extraction module."""

from typing import Dict, Optional
from urllib.parse import urlparse
from ..llm.client import LLMClient
from ..exceptions import ExtractorError
from .scraper import WebScraper
import json
import logging

logger = logging.getLogger(__name__)

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
            logger.debug(f"Raw LLM response: {llm_response}")
            
            # Parse and validate JSON response
            job_data = self._parse_llm_response(llm_response)
            
            # Validate the structure and content
            if not self._validate_job_data(job_data):
                logger.error(f"Invalid job data structure: {job_data}")
                raise ExtractorError("Invalid or incomplete job description data")
                
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job description: {str(e)}")
            raise ExtractorError(f"Failed to extract job description: {str(e)}")

    def _parse_llm_response(self, response: Dict) -> Dict:
        """
        Parse and validate the LLM response to ensure proper JSON format.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Parsed and validated JSON data
            
        Raises:
            ExtractorError: If response cannot be parsed as valid JSON
        """
        try:
            # Handle different response formats
            if isinstance(response, dict):
                if "content" in response and isinstance(response["content"], str):
                    return json.loads(response["content"])
                elif "response" in response and isinstance(response["response"], str):
                    return json.loads(response["response"])
                elif all(key in response for key in ["company", "title", "summary"]):
                    return response
                    
            logger.error(f"Unexpected response format: {response}")
            raise ExtractorError("Invalid response format from LLM")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ExtractorError(f"Invalid JSON response from LLM: {str(e)}")

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
        return f"""You are a precise job description parser. Your task is to extract and structure all information from the job posting into VALID JSON format. Accuracy and proper JSON formatting are critical.

Think of yourself as a high-precision scanner that:
- Captures every detail exactly as written
- Preserves all technical specifications precisely
- Maintains the original context and relationships
- Includes every requirement and qualification

Job Posting Content:
{content}

Your goal is to create a complete, accurate representation of this job posting in valid JSON format. When extracting information:
- Keep every technical detail exactly as written (e.g., "Python 3.8+" not just "Python")
- Preserve all version numbers, frameworks, and specifications
- Include every requirement, even if it seems redundant
- Maintain the exact wording of all qualifications
- Keep all bullet points and nested information
- Ensure the output is valid JSON that can be parsed by json.loads()

Required JSON Format:
{{
    "company": "Company name",
    "title": "Job title",
    "summary": "Complete job summary",
    "responsibilities": ["List of responsibilities"],
    "requirements": ["List of requirements"],
    "technical_skills": ["List of technical skills"],
    "non_technical_skills": ["List of non-technical skills"],
    "ats_keywords": ["Keywords for ATS"],
    "is_complete": boolean,
    "truncation_note": "string or null"
}}

Examples of Good JSON Extraction:

Good (Valid JSON):
{{
    "company": "TechCorp",
    "title": "Senior Python Developer",
    "summary": "Looking for an experienced Python developer...",
    "responsibilities": [
        "Lead Python application development",
        "Design system architecture"
    ],
    "requirements": [
        "5+ years Python experience",
        "Strong system design skills"
    ],
    "technical_skills": [
        "Python 3.8+",
        "Django 4.2+"
    ],
    "non_technical_skills": [
        "Leadership",
        "Communication"
    ],
    "ats_keywords": [
        "python",
        "django",
        "senior developer"
    ],
    "is_complete": true,
    "truncation_note": null
}}

Bad (Invalid JSON):
{{
    'company': 'TechCorp',  # Single quotes are not valid JSON
    title: "Senior Developer",  # Missing quotes around key
    "requirements": ["Python" "Django"]  # Missing comma in array
}}

Remember:
- Output MUST be valid JSON that can be parsed by json.loads()
- Use double quotes for strings, not single quotes
- Include commas between array items and object properties
- Boolean values must be lowercase (true/false)
- null must be lowercase
- Don't include comments in the JSON
- Don't include trailing commas
- Ensure all required fields are present
- Arrays and strings must be properly quoted and escaped"""

    def _validate_job_data(self, data: Dict) -> bool:
        """
        Validate the structure and content of job data.

        Args:
            data: Job data to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Required fields with their types
            field_types = {
                "company": str,
                "title": str,
                "summary": str,
                "responsibilities": list,
                "requirements": list,
                "technical_skills": list,
                "non_technical_skills": list,
                "ats_keywords": list,
                "is_complete": bool,
                "truncation_note": (str, type(None))
            }
            
            # Check all required fields exist and have correct types
            for field, expected_type in field_types.items():
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
                    
                if not isinstance(data[field], expected_type):
                    if not (field == "truncation_note" and data[field] is None):
                        logger.error(f"Invalid type for {field}: expected {expected_type}, got {type(data[field])}")
                        return False
            
            # Check lists have at least 1 item and contain only strings
            list_fields = ["responsibilities", "requirements", "technical_skills", 
                          "non_technical_skills", "ats_keywords"]
            for field in list_fields:
                if not data[field] or not all(isinstance(item, str) for item in data[field]):
                    logger.error(f"Invalid list content in {field}")
                    return False
            
            # Check essential fields are non-empty strings
            for field in ["company", "title", "summary"]:
                if not data[field].strip():
                    logger.error(f"Empty string in required field: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False 