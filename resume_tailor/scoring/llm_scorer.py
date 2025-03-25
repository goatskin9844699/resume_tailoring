"""LLM-based scoring component for resume content."""

import json
import time
from typing import Dict, List, Optional, Tuple

from .models import SectionScore, ScoringResult


class LLMScorer:
    """Scores resume content using LLM for deeper semantic understanding."""

    SCORING_PROMPT = """You are an expert resume analyzer. Your task is to score multiple sections of a resume against a job description.

Job Description:
{job_description}

Resume Sections:
{section_texts}

Please analyze each section and provide scores in this JSON format:
{{
    "sections": [
        {{
            "section_id": "section1",
            "score": float,
            "confidence": float,
            "matched_keywords": [str],
            "explanation": str
        }},
        ...
    ]
}}

Focus on:
- Technical skills match
- Experience relevance
- Achievement alignment
- Industry context

Ensure all scores are between 0 and 1, and provide clear explanations for each score.
"""

    def __init__(self, llm_client, max_tokens: int = 4000):
        """Initialize the LLM scorer.

        Args:
            llm_client: LLM client instance for making API calls.
            max_tokens: Maximum number of tokens to use in the prompt.
        """
        self.llm_client = llm_client
        self.max_tokens = max_tokens

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

    def _prepare_sections(
        self,
        sections: List[Tuple[str, Dict]],
        max_chars_per_section: int = 500
    ) -> str:
        """Prepare sections for LLM processing with length limits.

        Args:
            sections: List of (section_id, section) tuples.
            max_chars_per_section: Maximum characters per section.

        Returns:
            Formatted section text.
        """
        prepared_sections = []
        for section_id, section in sections:
            text = self._get_section_text(section)
            if text:
                # Truncate text if needed
                if len(text) > max_chars_per_section:
                    text = text[:max_chars_per_section] + "..."
                prepared_sections.append(f"Section {section_id}:\n{text}")
        return "\n\n".join(prepared_sections)

    def _validate_llm_response(self, response: Dict) -> bool:
        """Validate LLM response structure.

        Args:
            response: Response from LLM.

        Returns:
            True if response is valid, False otherwise.
        """
        if not isinstance(response, dict):
            return False
        if "sections" not in response:
            return False
        if not isinstance(response["sections"], list):
            return False

        required_fields = {"section_id", "score", "confidence"}
        for section in response["sections"]:
            if not isinstance(section, dict):
                return False
            if not all(field in section for field in required_fields):
                return False
            if not isinstance(section["score"], (int, float)):
                return False
            if not isinstance(section["confidence"], (int, float)):
                return False
            if not 0 <= section["score"] <= 1:
                return False
            if not 0 <= section["confidence"] <= 1:
                return False

        return True

    def score_content(
        self,
        job_description: str,
        resume_content: Dict,
        sections: Optional[List[str]] = None,
        max_chars_per_section: int = 500
    ) -> ScoringResult:
        """Score resume content against job description.

        Args:
            job_description: Job description text.
            resume_content: Resume content dictionary.
            sections: List of sections to score. If None, scores all sections.
            max_chars_per_section: Maximum characters per section.

        Returns:
            ScoringResult containing section scores.

        Raises:
            ValueError: If LLM response is invalid.
        """
        start_time = time.time()

        # Prepare sections to process
        sections_to_process = [
            (section_id, section)
            for section_id, section in resume_content.items()
            if not sections or section_id in sections
        ]

        if not sections_to_process:
            return ScoringResult(
                component_name="llm_scorer",
                section_scores={},
                overall_score=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": "No sections to process"}
            )

        # Prepare prompt
        section_texts = self._prepare_sections(
            sections_to_process,
            max_chars_per_section
        )
        prompt = self.SCORING_PROMPT.format(
            job_description=job_description,
            section_texts=section_texts
        )

        try:
            # Get LLM response
            response = self.llm_client.generate(prompt)
            
            # Parse and validate response
            if not self._validate_llm_response(response):
                raise ValueError("Invalid LLM response format")

            # Convert response to section scores
            section_scores = {}
            total_score = 0.0
            section_count = 0

            for section_data in response["sections"]:
                section_id = section_data["section_id"]
                section_scores[section_id] = SectionScore(
                    section_id=section_id,
                    score=float(section_data["score"]),
                    confidence=float(section_data["confidence"]),
                    matched_keywords=section_data.get("matched_keywords", []),
                    relevance_explanation=section_data.get("explanation")
                )
                total_score += section_scores[section_id].score
                section_count += 1

            # Calculate overall score
            overall_score = total_score / section_count if section_count > 0 else 0.0

            return ScoringResult(
                component_name="llm_scorer",
                section_scores=section_scores,
                overall_score=overall_score,
                processing_time=time.time() - start_time,
                metadata={
                    "section_count": section_count,
                    "max_chars_per_section": max_chars_per_section
                }
            )

        except Exception as e:
            return ScoringResult(
                component_name="llm_scorer",
                section_scores={},
                overall_score=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            ) 