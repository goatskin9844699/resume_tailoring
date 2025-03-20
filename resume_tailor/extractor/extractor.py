"""Job description extraction module."""

from typing import Dict
from ..llm.client import LLMClient


class JobDescriptionExtractor:
    """Extracts structured data from job descriptions."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the extractor.

        Args:
            llm_client: LLM client for processing job descriptions
        """
        self.llm = llm_client

    def extract(self, url: str) -> Dict:
        """
        Extract structured data from a job description URL.

        Args:
            url: URL of the job posting

        Returns:
            Structured job description data

        Raises:
            ExtractorError: If there's an error extracting the data
        """
        pass 