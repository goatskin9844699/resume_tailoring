"""Test that all package components can be imported."""

import pytest


def test_version():
    """Test that version is a string."""
    from resume_tailor import __version__
    assert isinstance(__version__, str)


def test_imports():
    """Test that all main classes can be imported."""
    from resume_tailor import JobDescriptionExtractor
    from resume_tailor import ResumeParser
    from resume_tailor import ResumeTailor
    
    assert JobDescriptionExtractor
    assert ResumeParser
    assert ResumeTailor 