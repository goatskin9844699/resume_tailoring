"""
Resume Tailor - A tool for tailoring resumes to job descriptions.
"""

__version__ = "0.1.0"

from .scraper import JobDescriptionScraper
from .parser import ResumeParser
from .tailor import ResumeTailor

__all__ = ["JobDescriptionScraper", "ResumeParser", "ResumeTailor"] 