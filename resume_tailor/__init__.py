"""
Resume Tailor - A tool for tailoring resumes to job descriptions.
"""

__version__ = "0.1.0"

from resume_tailor.resume_parser import (
    ResumeParser,
    ResumeParserError,
    InvalidYAMLError,
    MissingRequiredFieldError,
)
from resume_tailor.resume_tailor import (
    ResumeTailor,
    ResumeTailorError,
    InvalidOutputError,
    LLMClient,
)
from resume_tailor.extractor import JobDescriptionExtractor
from resume_tailor.scoring import (
    EmbeddingScorer,
    LLMScorer,
    ScoreCombiner,
    SectionScore,
    ScoringResult,
    CombinedScore,
)

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
    'EmbeddingScorer',
    'LLMScorer',
    'ScoreCombiner',
    'SectionScore',
    'ScoringResult',
    'CombinedScore',
] 