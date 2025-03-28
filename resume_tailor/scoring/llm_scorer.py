"""Scoring component using LLM for deeper semantic understanding."""

import time
from typing import Dict, List, Optional, Any, Tuple

from resume_tailor.llm import LLMClient, LLMError
from .models import (
    SectionScore,
    ScoringResult,
    ScoredEntry,
    ScoredBullet
)


class LLMScorer:
    """Scores resume content using LLM for deeper semantic understanding."""

    SCORING_PROMPT = """Analyze the following resume sections against the job description and provide detailed scoring.

Job Description:
{job_description}

Resume Sections:
{section_texts}

For each section, provide:
1. Overall section score (0-1)
2. Confidence in the score (0-1)
3. Matched keywords
4. Brief explanation of relevance
5. For each entry in the section:
   - Entry score (0-1)
   - Confidence (0-1)
   - Matched keywords
   - Brief explanation
   - For each bullet point:
     * Score (0-1)
     * Confidence (0-1)
     * Matched keywords
     * Brief explanation

Format your response as a JSON object with the following structure:
{{
    "sections": [
        {{
            "section_id": "string",
            "score": float,
            "confidence": float,
            "matched_keywords": ["string"],
            "explanation": "string",
            "entries": [
                {{
                    "entry_id": "string",
                    "entry_type": "string",
                    "score": float,
                    "confidence": float,
                    "matched_keywords": ["string"],
                    "explanation": "string",
                    "bullets": [
                        {{
                            "content": "string",
                            "score": float,
                            "confidence": float,
                            "matched_keywords": ["string"],
                            "explanation": "string"
                        }}
                    ]
                }}
            ]
        }}
    ]
}}"""

    def __init__(self, llm_client: LLMClient):
        """Initialize the LLM scorer.

        Args:
            llm_client: LLM client instance.
        """
        self.llm_client = llm_client

    def _prepare_sections(
        self,
        sections: List[Tuple[str, Dict]],
        max_chars_per_section: int
    ) -> str:
        """Prepare sections for LLM processing.

        Args:
            sections: List of (section_id, section) tuples.
            max_chars_per_section: Maximum characters per section.

        Returns:
            Formatted section text.
        """
        formatted_sections = []
        for section_id, section in sections:
            section_text = f"Section: {section_id}\n"
            
            # Add section highlights if present
            if "highlights" in section:
                section_text += "Highlights:\n"
                for highlight in section["highlights"]:
                    section_text += f"- {highlight}\n"
            
            # Add section description if present
            if "description" in section:
                section_text += f"Description: {section['description']}\n"
            
            # Add entries if present
            if "entries" in section:
                section_text += "Entries:\n"
                for i, entry in enumerate(section["entries"]):
                    section_text += f"\nEntry {i+1}:\n"
                    
                    # Add entry highlights
                    if "highlights" in entry:
                        section_text += "Highlights:\n"
                        for highlight in entry["highlights"]:
                            section_text += f"- {highlight}\n"
                    
                    # Add entry description
                    if "description" in entry:
                        section_text += f"Description: {entry['description']}\n"
                    
                    # Add bullets if present
                    if "bullets" in entry:
                        section_text += "Bullets:\n"
                        for bullet in entry["bullets"]:
                            section_text += f"- {bullet}\n"
            
            formatted_sections.append(section_text)
        
        return "\n\n".join(formatted_sections)

    def _validate_llm_response(self, response: Dict) -> bool:
        """Validate LLM response format.

        Args:
            response: LLM response dictionary.

        Returns:
            True if response is valid, False otherwise.
        """
        if not isinstance(response, dict):
            return False
        if "sections" not in response:
            return False
        if not isinstance(response["sections"], list):
            return False
        
        for section in response["sections"]:
            required_fields = ["section_id", "score", "confidence", "entries"]
            if not all(field in section for field in required_fields):
                return False
            
            for entry in section["entries"]:
                required_fields = ["entry_id", "entry_type", "score", "confidence", "bullets"]
                if not all(field in entry for field in required_fields):
                    return False
                
                for bullet in entry["bullets"]:
                    required_fields = ["content", "score", "confidence"]
                    if not all(field in bullet for field in required_fields):
                        return False
        
        return True

    def _create_scored_bullet(self, bullet_data: Dict) -> ScoredBullet:
        """Create a ScoredBullet from LLM response data.

        Args:
            bullet_data: Bullet data from LLM response.

        Returns:
            ScoredBullet instance.
        """
        return ScoredBullet(
            content=bullet_data["content"],
            score=float(bullet_data["score"]),
            confidence=float(bullet_data["confidence"]),
            matched_keywords=bullet_data.get("matched_keywords", []),
            relevance_explanation=bullet_data.get("explanation")
        )

    def _create_scored_entry(self, entry_data: Dict) -> ScoredEntry:
        """Create a ScoredEntry from LLM response data.

        Args:
            entry_data: Entry data from LLM response.

        Returns:
            ScoredEntry instance.
        """
        return ScoredEntry(
            entry_id=entry_data["entry_id"],
            entry_type=entry_data["entry_type"],
            score=float(entry_data["score"]),
            confidence=float(entry_data["confidence"]),
            matched_keywords=entry_data.get("matched_keywords", []),
            relevance_explanation=entry_data.get("explanation"),
            bullets=[
                self._create_scored_bullet(bullet)
                for bullet in entry_data["bullets"]
            ]
        )

    def _create_section_score(self, section_data: Dict) -> SectionScore:
        """Create a SectionScore from LLM response data.

        Args:
            section_data: Section data from LLM response.

        Returns:
            SectionScore instance.
        """
        return SectionScore(
            section_id=section_data["section_id"],
            score=float(section_data["score"]),
            confidence=float(section_data["confidence"]),
            matched_keywords=section_data.get("matched_keywords", []),
            relevance_explanation=section_data.get("explanation"),
            entries=[
                self._create_scored_entry(entry)
                for entry in section_data["entries"]
            ]
        )

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
                section_score = self._create_section_score(section_data)
                section_scores[section_data["section_id"]] = section_score
                total_score += section_score.score
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