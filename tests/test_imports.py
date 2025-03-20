"""Test imports."""

from resume_tailor.extractor.extractor import JobDescriptionExtractor
from resume_tailor.core.resume_parser import ResumeParser
from resume_tailor.core.resume_tailor import ResumeTailor
from resume_tailor.llm.client import LLMClient


def test_version():
    """Test that version can be imported."""
    from resume_tailor import __version__
    assert __version__


def test_imports():
    """Test that all main classes can be imported."""
    assert JobDescriptionExtractor
    assert ResumeParser
    assert ResumeTailor
    assert LLMClient 