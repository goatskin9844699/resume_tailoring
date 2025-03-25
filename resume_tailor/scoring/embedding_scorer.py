"""Embedding-based scoring component for resume content."""

import time
from typing import Dict, List, Optional

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from .models import SectionScore, ScoringResult


class EmbeddingScorer:
    """Scores resume content using sentence embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding scorer.

        Args:
            model_name: Name of the sentence transformer model to use.
        """
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def _prepare_text(self, text: str) -> str:
        """Prepare text for embedding.

        Args:
            text: Input text to prepare.

        Returns:
            Prepared text.
        """
        # Basic text cleaning
        return text.strip().lower()

    def _get_section_text(self, section: Dict) -> str:
        """Extract text content from a resume section.

        Args:
            section: Resume section dictionary.

        Returns:
            Combined text content.
        """
        if "highlights" in section:
            return " ".join(section["highlights"])
        if "content" in section:
            return section["content"]
        return ""

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
            
            # Create section score
            section_scores[section_id] = SectionScore(
                section_id=section_id,
                score=max(0.0, min(1.0, similarity)),  # Normalize to [0,1]
                confidence=similarity,
                matched_keywords=[],  # TODO: Implement keyword matching
                relevance_explanation=None  # TODO: Implement explanation generation
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