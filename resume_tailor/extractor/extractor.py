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
        return f"""You are a job description parser. Your task is to extract structured information from the job posting content below.
You MUST respond with ONLY a valid JSON object, no other text. The response must be a single JSON object that can be parsed by json.loads().

Job Posting Content:
{content}

Required JSON format:
{{
    "company": "Company name (required)",
    "title": "Job title (required)",
    "summary": "Brief job summary (required)",
    "responsibilities": ["List of key responsibilities (at least 2)"],
    "requirements": ["List of key requirements (at least 2)"],
    "technical_skills": ["List of specific technical skills mentioned"],
    "non_technical_skills": ["List of soft skills and non-technical requirements"],
    "ats_keywords": ["Keywords optimized for ATS systems"]
}}

Important rules:
1. Respond with ONLY the JSON object, no other text
2. All fields are required
3. Lists must contain at least 2 items
4. Use exact phrases from the job posting where possible
5. Format must be valid JSON that can be parsed by json.loads()
6. Do not include any explanatory text or markdown formatting
7. Do not include any line breaks or extra whitespace in the JSON"""

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
            "ats_keywords"
        ]
        
        # Check all required fields exist
        if not all(field in data for field in required_fields):
            return False
            
        # Check all fields have non-empty values
        if any(not data[field] for field in required_fields):
            return False
            
        # Check lists have at least 2 items
        list_fields = ["responsibilities", "requirements", "technical_skills", 
                      "non_technical_skills", "ats_keywords"]
        if any(not isinstance(data[field], list) or len(data[field]) < 2 
               for field in list_fields):
            return False
            
        return True 