"""
Resume Tailor - A tool for tailoring resumes to job descriptions.
"""

__version__ = "0.1.0"

from .extractor.extractor import JobDescriptionExtractor
from .parser import ResumeParser
from .tailor.tailor import ResumeTailor

__all__ = ["JobDescriptionExtractor", "ResumeParser", "ResumeTailor"] 