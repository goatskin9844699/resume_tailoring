"""Job description extraction module."""

from typing import Dict
from urllib.parse import urlparse
from ..llm.client import LLMClient
from ..exceptions import ExtractorError
from .scraper import WebScraper
import json


class JobDescriptionExtractor:
    """Extracts structured data from job descriptions."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the extractor.

        Args:
            llm_client: LLM client for processing job descriptions
        """
        self.llm = llm_client
        self.scraper = WebScraper()

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
            job_data = self.llm.generate(prompt)
            
            # Handle wrapped response format
            if "response" in job_data and isinstance(job_data["response"], str):
                try:
                    job_data = json.loads(job_data["response"])
                except json.JSONDecodeError:
                    raise ExtractorError("Invalid JSON response from LLM")
            
            # Validate response
            if not job_data or not self._validate_job_data(job_data):
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
You MUST respond with ONLY a valid JSON object, no other text.

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
5. Format must be valid JSON"""

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