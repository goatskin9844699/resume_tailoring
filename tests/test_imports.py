"""Test that all package components can be imported."""

import pytest


def test_version():
    """Test that version is a string."""
    import resume_tailor
    assert hasattr(resume_tailor, "__version__")
    assert isinstance(resume_tailor.__version__, str)


def test_imports():
    """Test that all main classes can be imported."""
    from resume_tailor.extractor.extractor import JobDescriptionExtractor
    from resume_tailor.parser import ResumeParser
    from resume_tailor.tailor.tailor import ResumeTailor
    
    assert JobDescriptionExtractor
    assert ResumeParser
    assert ResumeTailor 