"""Job description extraction module."""

from typing import Dict
from urllib.parse import urlparse
from ..llm.client import LLMClient
from ..exceptions import ExtractorError
from .scraper import WebScraper


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
            
            # Validate response
            if not job_data:
                raise ExtractorError("Empty job description data")
                
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
        return f"""Extract structured information from this job posting content:

{content}

Please provide the information in the following JSON format:
{{
    "company": "Company name",
    "title": "Job title",
    "summary": "Brief job summary",
    "responsibilities": ["List of responsibilities"],
    "requirements": ["List of requirements"],
    "technical_skills": ["List of technical skills"],
    "non_technical_skills": ["List of non-technical skills"],
    "ats_keywords": ["List of ATS-optimized keywords"]
}}

Focus on extracting:
1. Clear job title and company name
2. Key responsibilities and requirements
3. Technical and non-technical skills
4. ATS-optimized keywords that match the job requirements

Ensure all lists are non-empty and contain relevant information.""" 