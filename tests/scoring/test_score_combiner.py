"""Tests for the score combination component."""

import pytest
from resume_tailor.scoring.score_combiner import ScoreCombiner
from resume_tailor.scoring.models import SectionScore, ScoringResult, CombinedScore


@pytest.fixture
def combiner():
    """Create a ScoreCombiner instance."""
    return ScoreCombiner()


@pytest.fixture
def sample_section_scores():
    """Create sample section scores for testing."""
    return {
        "skills": SectionScore(
            section_id="skills",
            score=0.8,
            confidence=0.9,
            matched_keywords=["Python", "JavaScript"],
            relevance_explanation="Strong match"
        ),
        "experience": SectionScore(
            section_id="experience",
            score=0.6,
            confidence=0.7,
            matched_keywords=["5 years"],
            relevance_explanation="Good match"
        )
    }


@pytest.fixture
def sample_results(sample_section_scores):
    """Create sample scoring results for testing."""
    return [
        ScoringResult(
            component_name="component1",
            section_scores=sample_section_scores,
            overall_score=0.7,
            processing_time=0.1,
            metadata={"test": "data1"}
        ),
        ScoringResult(
            component_name="component2",
            section_scores=sample_section_scores,
            overall_score=0.7,
            processing_time=0.2,
            metadata={"test": "data2"}
        )
    ]


def test_init_default_weights(combiner):
    """Test initialization with default weights."""
    assert combiner.weights == {}
    assert combiner.normalize_scores is True


def test_init_custom_weights():
    """Test initialization with custom weights."""
    weights = {"component1": 0.7, "component2": 0.3}
    combiner = ScoreCombiner(weights=weights)
    assert combiner.weights == weights


def test_normalize_scores(combiner):
    """Test score normalization."""
    scores = {"a": 1.0, "b": 0.5, "c": 0.0}
    normalized = combiner._normalize_scores(scores)
    assert normalized["a"] == 1.0
    assert normalized["b"] == 0.5
    assert normalized["c"] == 0.0


def test_normalize_scores_empty(combiner):
    """Test normalization of empty scores."""
    assert combiner._normalize_scores({}) == {}


def test_normalize_scores_single_value(combiner):
    """Test normalization with single value."""
    scores = {"a": 0.5}
    normalized = combiner._normalize_scores(scores)
    assert normalized["a"] == 0.5


def test_combine_section_scores(combiner, sample_section_scores):
    """Test combining section scores."""
    component_scores = {
        "component1": sample_section_scores,
        "component2": sample_section_scores
    }
    weights = {"component1": 0.7, "component2": 0.3}
    
    combined = combiner._combine_section_scores(component_scores, weights)
    
    assert len(combined) == 2
    assert all(isinstance(score, SectionScore) for score in combined.values())
    assert "skills" in combined
    assert "experience" in combined


def test_combine_results_empty(combiner):
    """Test combining empty results."""
    result = combiner.combine_results([])
    assert isinstance(result, CombinedScore)
    assert result.overall_score == 0.0
    assert not result.section_scores


def test_combine_results_with_default_weights(combiner, sample_results):
    """Test combining results with default weights."""
    result = combiner.combine_results(sample_results)
    
    assert isinstance(result, CombinedScore)
    assert len(result.section_scores) == 2
    assert result.overall_score > 0
    assert "component_weights" in result.metadata
    assert "component_processing_times" in result.metadata


def test_combine_results_with_custom_weights(combiner, sample_results):
    """Test combining results with custom weights."""
    custom_weights = {"component1": 0.7, "component2": 0.3}
    result = combiner.combine_results(sample_results, custom_weights)
    
    assert result.component_weights == custom_weights
    assert result.metadata["component_weights"] == custom_weights


def test_combine_results_weight_normalization(combiner, sample_results):
    """Test weight normalization in results combination."""
    custom_weights = {"component1": 7.0, "component2": 3.0}
    result = combiner.combine_results(sample_results, custom_weights)
    
    # Weights should be normalized to sum to 1
    assert sum(result.component_weights.values()) == pytest.approx(1.0)
    assert result.component_weights["component1"] == pytest.approx(0.7)
    assert result.component_weights["component2"] == pytest.approx(0.3)


def test_combine_results_metadata(combiner, sample_results):
    """Test metadata preservation in combined results."""
    result = combiner.combine_results(sample_results)
    
    assert "component_processing_times" in result.metadata
    assert result.metadata["component_processing_times"]["component1"] == 0.1
    assert result.metadata["component_processing_times"]["component2"] == 0.2 