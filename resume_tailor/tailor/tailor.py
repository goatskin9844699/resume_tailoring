"""Resume tailoring module."""

from typing import Dict
from ..llm.client import LLMClient
from ..parser import Resume


class ResumeTailor:
    """Creates tailored resumes based on job descriptions."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the tailor.

        Args:
            llm_client: LLM client for tailoring resumes
        """
        self.llm = llm_client

    def tailor_resume(self, job_desc: Dict, master_resume: Resume) -> Resume:
        """
        Create a tailored resume for a specific job.

        Args:
            job_desc: Structured job description data
            master_resume: Master resume to tailor

        Returns:
            Tailored resume

        Raises:
            TailorError: If there's an error tailoring the resume
        """
        pass 