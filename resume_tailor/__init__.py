"""
Resume Tailor - A tool for tailoring resumes to job descriptions.
"""

__version__ = "0.1.0"

from resume_tailor.core import (
    ResumeParser,
    ResumeParserError,
    InvalidYAMLError,
    MissingRequiredFieldError,
    ResumeTailor,
    ResumeTailorError,
    InvalidOutputError,
    LLMClient,
)
from resume_tailor.extractor import JobDescriptionExtractor

__all__ = [
    'ResumeParser',
    'ResumeParserError',
    'InvalidYAMLError',
    'MissingRequiredFieldError',
    'ResumeTailor',
    'ResumeTailorError',
    'InvalidOutputError',
    'LLMClient',
    'JobDescriptionExtractor',
] 