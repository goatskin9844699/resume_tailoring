"""Test that all package components can be imported."""

import pytest
from resume_tailor import (
    JobDescriptionExtractor,
    ResumeParser,
    ResumeTailor,
    __version__,
)


def test_version():
    """Test that version is a string."""
    assert isinstance(__version__, str)


def test_imports():
    """Test that all main classes can be imported."""
    assert JobDescriptionExtractor
    assert ResumeParser
    assert ResumeTailor 