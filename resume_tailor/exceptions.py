"""Custom exceptions for the resume-tailor package."""

class ResumeTailorError(Exception):
    """Base exception for all resume-tailor errors."""
    pass

class ParserError(ResumeTailorError):
    """Raised when there's an error parsing YAML data."""
    pass

class ExtractorError(ResumeTailorError):
    """Raised when there's an error extracting job description data."""
    pass

class TailorError(ResumeTailorError):
    """Raised when there's an error tailoring the resume."""
    pass

class InvalidOutputError(ResumeTailorError):
    """Raised when the LLM output is invalid."""
    pass

__all__ = [
    'ResumeTailorError',
    'ParserError',
    'ExtractorError',
    'TailorError',
    'InvalidOutputError',
] 