"""Tests for the LLM-based scoring component."""

import pytest
from unittest.mock import Mock

from resume_tailor.scoring.llm_scorer import LLMScorer
from resume_tailor.scoring.models import SectionScore, ScoringResult


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = Mock()
    return client


@pytest.fixture
def sample_job_description():
    """Create a sample job description."""
    return """Senior Software Engineer
    - 5+ years Python experience
    - Strong system design skills
    - Experience with cloud technologies
    """


@pytest.fixture
def sample_resume_content():
    """Create sample resume content."""
    return {
        "experience1": {
            "company": "Tech Corp",
            "highlights": ["Led development of Python-based microservices", "Designed and implemented cloud architecture"],
            "title": "Senior Software Engineer"
        },
        "experience2": {
            "highlights": ["Developed web applications using Python", "Implemented CI/CD pipelines"],
            "title": "Software Engineer"
        }
    }


def test_score_content_success(mock_llm_client, sample_job_description, sample_resume_content):
    """Test successful scoring of resume content."""
    # Mock LLM response
    mock_response = {
        "sections": [
            {
                "section_id": "experience1",
                "score": 0.9,
                "confidence": 0.95,
                "matched_keywords": ["Python", "cloud", "system design"],
                "explanation": "Strong match with required skills",
                "entries": [
                    {
                        "entry_id": "exp1_1",
                        "entry_type": "experience",
                        "score": 0.9,
                        "confidence": 0.95,
                        "matched_keywords": ["Python", "cloud"],
                        "explanation": "Strong technical match",
                        "bullets": [
                            {
                                "content": "Led development of Python-based microservices",
                                "score": 0.9,
                                "confidence": 0.95,
                                "matched_keywords": ["Python"],
                                "explanation": "Direct skill match"
                            }
                        ]
                    }
                ]
            },
            {
                "section_id": "experience2",
                "score": 0.7,
                "confidence": 0.85,
                "matched_keywords": ["Python", "CI/CD"],
                "explanation": "Good match with some requirements",
                "entries": [
                    {
                        "entry_id": "exp2_1",
                        "entry_type": "experience",
                        "score": 0.7,
                        "confidence": 0.85,
                        "matched_keywords": ["Python"],
                        "explanation": "Good technical match",
                        "bullets": [
                            {
                                "content": "Developed web applications using Python",
                                "score": 0.8,
                                "confidence": 0.85,
                                "matched_keywords": ["Python"],
                                "explanation": "Skill match"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    mock_llm_client.generate.return_value = mock_response

    # Initialize scorer
    scorer = LLMScorer(mock_llm_client)

    # Score content
    result = scorer.score_content(
        sample_job_description,
        sample_resume_content
    )

    # Verify result
    assert isinstance(result, ScoringResult)
    assert result.component_name == "llm_scorer"
    assert len(result.section_scores) == 2
    assert "experience1" in result.section_scores
    assert "experience2" in result.section_scores
    assert result.section_scores["experience1"].score == 0.9
    assert result.section_scores["experience2"].score == 0.7


def test_score_content_empty_sections(mock_llm_client, sample_job_description):
    """Test scoring with empty sections."""
    result = LLMScorer(mock_llm_client).score_content(
        sample_job_description,
        {}
    )
    assert isinstance(result, ScoringResult)
    assert result.section_scores == {}
    assert result.overall_score == 0.0


def test_score_content_invalid_response(mock_llm_client, sample_job_description, sample_resume_content):
    """Test handling of invalid LLM response."""
    mock_llm_client.generate.return_value = {"invalid": "response"}
    result = LLMScorer(mock_llm_client).score_content(
        sample_job_description,
        sample_resume_content
    )
    assert isinstance(result, ScoringResult)
    assert result.section_scores == {}
    assert "error" in result.metadata


def test_score_content_section_truncation(mock_llm_client, sample_job_description):
    """Test section text truncation."""
    # Create resume with long section
    long_resume = {
        "experience1": {
            "highlights": ["x" * 1000]  # Very long text
        }
    }

    # Mock LLM response
    mock_llm_client.generate.return_value = {
        "sections": [
            {
                "section_id": "experience1",
                "score": 0.8,
                "confidence": 0.9,
                "matched_keywords": ["test"],
                "explanation": "Test",
                "entries": [
                    {
                        "entry_id": "exp1_1",
                        "entry_type": "experience",
                        "score": 0.8,
                        "confidence": 0.9,
                        "matched_keywords": ["test"],
                        "explanation": "Test",
                        "bullets": [
                            {
                                "content": "x" * 100,
                                "score": 0.8,
                                "confidence": 0.9,
                                "matched_keywords": ["test"],
                                "explanation": "Test"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    scorer = LLMScorer(mock_llm_client)
    result = scorer.score_content(
        sample_job_description,
        long_resume,
        max_chars_per_section=100
    )

    assert isinstance(result, ScoringResult)
    assert len(result.section_scores) == 1
    assert result.section_scores["experience1"].score == 0.8


def test_score_content_specific_sections(mock_llm_client, sample_job_description, sample_resume_content):
    """Test scoring specific sections only."""
    # Mock LLM response
    mock_llm_client.generate.return_value = {
        "sections": [
            {
                "section_id": "experience1",
                "score": 0.9,
                "confidence": 0.95,
                "matched_keywords": ["Python"],
                "explanation": "Test",
                "entries": [
                    {
                        "entry_id": "exp1_1",
                        "entry_type": "experience",
                        "score": 0.9,
                        "confidence": 0.95,
                        "matched_keywords": ["Python"],
                        "explanation": "Test",
                        "bullets": [
                            {
                                "content": "Test bullet",
                                "score": 0.9,
                                "confidence": 0.95,
                                "matched_keywords": ["Python"],
                                "explanation": "Test"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    scorer = LLMScorer(mock_llm_client)
    result = scorer.score_content(
        sample_job_description,
        sample_resume_content,
        sections=["experience1"]
    )

    assert isinstance(result, ScoringResult)
    assert len(result.section_scores) == 1
    assert "experience1" in result.section_scores 