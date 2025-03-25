"""Embedding-based scoring component for resume content."""

import time
from typing import Dict, List

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
        return str(section)

    def score_content(
        self,
        job_description: str,
        resume_content: Dict,
        sections: List[str] = None
    ) -> ScoringResult:
        """Score resume content against job description.

        Args:
            job_description: Job description text.
            resume_content: Resume content dictionary.
            sections: List of sections to score. If None, scores all sections.

        Returns:
            ScoringResult containing section scores.
        """
        start_time = time.time()

        # Prepare job description
        job_embedding = self.model.encode(
            self._prepare_text(job_description),
            convert_to_tensor=True
        )

        # Initialize results
        section_scores = {}
        total_score = 0.0
        section_count = 0

        # Score each section
        for section_id, section in resume_content.items():
            if sections and section_id not in sections:
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
            similarity = cos_sim(job_embedding, section_embedding).item()
            
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