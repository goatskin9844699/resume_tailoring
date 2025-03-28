"""Tests for the embedding-based scoring component."""

import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch
from sentence_transformers import SentenceTransformer

from resume_tailor.scoring.embedding_scorer import EmbeddingScorer
from resume_tailor.scoring.models import SectionScore, ScoringResult


@pytest.fixture
def mock_transformer():
    """Create a mock sentence transformer."""
    with patch('resume_tailor.scoring.embedding_scorer.SentenceTransformer') as mock:
        # Create a mock instance
        instance = Mock()
        # Return a proper tensor for encode method
        instance.encode.return_value = torch.tensor([[0.5, 0.5]], dtype=torch.float32)
        mock.return_value = instance
        yield instance


@pytest.fixture
def scorer(mock_transformer):
    """Create an EmbeddingScorer instance with mocked transformer."""
    return EmbeddingScorer(model_name="all-MiniLM-L6-v2")


def test_init(scorer):
    """Test initialization of EmbeddingScorer."""
    assert scorer.model_name == "all-MiniLM-L6-v2"


def test_prepare_text(scorer):
    """Test text preparation."""
    text = "  Hello World!  "
    prepared = scorer._prepare_text(text)
    assert prepared == "hello world!"


def test_get_section_text_with_highlights(scorer):
    """Test section text extraction with highlights."""
    section = {
        "highlights": ["Skill 1", "Skill 2"]
    }
    text = scorer._get_section_text(section)
    assert text == "Skill 1 Skill 2"


def test_get_section_text_without_highlights(scorer):
    """Test section text extraction without highlights."""
    section = {
        "content": "Some content"
    }
    text = scorer._get_section_text(section)
    assert text == "Some content"


def test_score_content_empty_sections(scorer):
    """Test scoring with empty sections."""
    sections = {}
    result = scorer.score_content(sections)
    assert isinstance(result, ScoringResult)
    assert result.section_scores == {}


def test_score_content_with_sections(scorer):
    """Test scoring with sections."""
    sections = {
        "skills": {
            "highlights": ["Python", "JavaScript"]
        },
        "experience": {
            "highlights": ["Software Engineer", "Full Stack"]
        }
    }
    result = scorer.score_content(sections)
    assert isinstance(result, ScoringResult)
    assert len(result.section_scores) == 2
    assert all(isinstance(score, SectionScore) for score in result.section_scores.values())


def test_score_content_with_specific_sections(scorer):
    """Test scoring with specific sections."""
    sections = {
        "skills": {
            "highlights": ["Python", "JavaScript"]
        },
        "experience": {
            "highlights": ["Software Engineer", "Full Stack"]
        }
    }
    result = scorer.score_content(sections, sections_to_score=["skills"])
    assert isinstance(result, ScoringResult)
    assert len(result.section_scores) == 1
    assert "skills" in result.section_scores
    assert "experience" not in result.section_scores


def test_score_content_normalization(scorer):
    """Test score normalization."""
    sections = {
        "skills": {
            "highlights": ["Python", "JavaScript"]
        },
        "experience": {
            "highlights": ["Software Engineer", "Full Stack"]
        }
    }
    result = scorer.score_content(sections)
    assert isinstance(result, ScoringResult)
    assert all(0 <= score.score <= 1 for score in result.section_scores.values()) 