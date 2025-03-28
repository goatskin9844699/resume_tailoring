"""Models for the resume scoring system."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ScoredBullet(BaseModel):
    """Score for a specific bullet point in a resume entry."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    content: str
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    matched_keywords: List[str] = []
    relevance_explanation: Optional[str] = None


class ScoredEntry(BaseModel):
    """Score for a specific entry (experience, education, project, etc.) in a section."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    entry_id: str
    entry_type: str  # e.g., "experience", "education", "project"
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    matched_keywords: List[str] = []
    relevance_explanation: Optional[str] = None
    bullets: List[ScoredBullet] = []


class SectionScore(BaseModel):
    """Score for a specific resume section."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    section_id: str
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    matched_keywords: List[str] = []
    relevance_explanation: Optional[str] = None
    entries: List[ScoredEntry] = []


class ScoringResult(BaseModel):
    """Result from a scoring component."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    component_name: str
    section_scores: Dict[str, SectionScore]
    overall_score: float = Field(ge=0.0, le=1.0)
    processing_time: float
    metadata: Dict[str, Any] = {}


class CombinedScore(BaseModel):
    """Combined scores from multiple scoring components."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    section_scores: Dict[str, SectionScore]
    overall_score: float = Field(ge=0.0, le=1.0)
    component_weights: Dict[str, float]
    processing_time: float
    metadata: Dict[str, Any] = {}


class ContentSelection(BaseModel):
    """Result of content selection based on scores."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    selected_sections: Dict[str, List[str]]
    section_order: List[str]
    relevance_scores: Dict[str, float]
    metadata: Dict[str, Any] = {} 