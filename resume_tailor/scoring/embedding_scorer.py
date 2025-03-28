"""Scoring component using sentence embeddings for semantic similarity."""

import time
from typing import Dict, List, Optional, Tuple

import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from .models import (
    SectionScore,
    ScoringResult,
    ScoredEntry,
    ScoredBullet
)


class EmbeddingScorer:
    """Scores resume content using sentence embeddings."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None
    ):
        """Initialize the embedding scorer.

        Args:
            model_name: Name of the sentence transformer model to use.
            device: Device to run the model on. If None, uses CUDA if available.
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SentenceTransformer(model_name, device=self.device)

    def _prepare_text(self, text: str) -> str:
        """Prepare text for embedding.

        Args:
            text: Text to prepare.

        Returns:
            Prepared text.
        """
        return text.strip().lower()

    def _get_section_text(self, section: Dict) -> str:
        """Extract text from a section.

        Args:
            section: Section dictionary.

        Returns:
            Extracted text.
        """
        if not section:
            return ""

        text_parts = []
        if "highlights" in section:
            text_parts.extend(section["highlights"])
        if "description" in section:
            text_parts.append(section["description"])
        if "content" in section:
            text_parts.append(section["content"])
        return " ".join(text_parts)

    def _score_text(
        self,
        text: str,
        reference_embedding: torch.Tensor
    ) -> Tuple[float, float]:
        """Score text against a reference embedding.

        Args:
            text: Text to score.
            reference_embedding: Reference embedding to score against.

        Returns:
            Tuple of (score, confidence).
        """
        if not text:
            return 0.0, 0.0

        text_embedding = self.model.encode(
            self._prepare_text(text),
            convert_to_tensor=True
        )
        similarity = cos_sim(reference_embedding, text_embedding).item()
        return max(0.0, min(1.0, similarity)), similarity

    def _score_bullets(
        self,
        bullets: List[str],
        reference_embedding: torch.Tensor
    ) -> List[ScoredBullet]:
        """Score a list of bullet points.

        Args:
            bullets: List of bullet point texts.
            reference_embedding: Reference embedding to score against.

        Returns:
            List of scored bullets.
        """
        scored_bullets = []
        for bullet in bullets:
            score, confidence = self._score_text(bullet, reference_embedding)
            scored_bullets.append(ScoredBullet(
                content=bullet,
                score=score,
                confidence=confidence,
                matched_keywords=[],  # TODO: Implement keyword matching
                relevance_explanation=None  # TODO: Implement explanation generation
            ))
        return scored_bullets

    def _score_entries(
        self,
        entries: List[Dict],
        entry_type: str,
        reference_embedding: torch.Tensor
    ) -> List[ScoredEntry]:
        """Score a list of entries.

        Args:
            entries: List of entry dictionaries.
            entry_type: Type of entries (e.g., "experience", "education").
            reference_embedding: Reference embedding to score against.

        Returns:
            List of scored entries.
        """
        scored_entries = []
        for i, entry in enumerate(entries):
            # Get entry text
            entry_text = self._get_section_text(entry)
            score, confidence = self._score_text(entry_text, reference_embedding)
            
            # Score bullets if present
            bullets = []
            if "bullets" in entry:
                bullets = self._score_bullets(entry["bullets"], reference_embedding)
            
            scored_entries.append(ScoredEntry(
                entry_id=f"{entry_type}_{i}",
                entry_type=entry_type,
                score=score,
                confidence=confidence,
                matched_keywords=[],  # TODO: Implement keyword matching
                relevance_explanation=None,  # TODO: Implement explanation generation
                bullets=bullets
            ))
        return scored_entries

    def score_content(
        self,
        sections: Dict[str, Dict],
        sections_to_score: Optional[List[str]] = None,
        job_description: Optional[str] = None
    ) -> ScoringResult:
        """Score resume content sections.

        Args:
            sections: Dictionary of resume sections to score.
            sections_to_score: Optional list of section IDs to score. If None, scores all sections.
            job_description: Optional job description to score against. If None, uses a neutral baseline.

        Returns:
            ScoringResult containing section scores.
        """
        start_time = time.time()

        # Use job description if provided, otherwise use a neutral baseline
        if job_description:
            reference_text = job_description
        else:
            # Use a neutral baseline that will give moderate scores
            reference_text = "professional experience skills achievements"

        reference_embedding = self.model.encode(
            self._prepare_text(reference_text),
            convert_to_tensor=True
        )

        # Initialize results
        section_scores = {}
        total_score = 0.0
        section_count = 0

        # Score each section
        for section_id, section in sections.items():
            if sections_to_score and section_id not in sections_to_score:
                continue

            # Get section text
            section_text = self._get_section_text(section)
            if not section_text:
                continue

            # Get section embedding
            section_embedding = self.model.encode(
                self._prepare_text(section_text),
                convert_to_tensor=True
            )

            # Calculate similarity score
            similarity = cos_sim(reference_embedding, section_embedding).item()
            
            # Score entries if present
            entries = []
            if "entries" in section:
                entries = self._score_entries(
                    section["entries"],
                    section_id,
                    reference_embedding
                )
            
            # Create section score
            section_scores[section_id] = SectionScore(
                section_id=section_id,
                score=max(0.0, min(1.0, similarity)),  # Normalize to [0,1]
                confidence=similarity,
                matched_keywords=[],  # TODO: Implement keyword matching
                relevance_explanation=None,  # TODO: Implement explanation generation
                entries=entries
            )

            total_score += section_scores[section_id].score
            section_count += 1

        # Calculate overall score
        overall_score = total_score / section_count if section_count > 0 else 0.0

        return ScoringResult(
            component_name=f"embedding_{self.model_name}",
            section_scores=section_scores,
            overall_score=overall_score,
            processing_time=time.time() - start_time,
            metadata={
                "model_name": self.model_name,
                "section_count": section_count
            }
        ) 