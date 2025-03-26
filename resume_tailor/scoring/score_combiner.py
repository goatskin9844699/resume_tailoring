"""Score combiner for combining results from multiple scoring components."""

import time
from typing import Dict, List

from .models import (
    SectionScore,
    ScoringResult,
    CombinedScore,
    ScoredEntry,
    ScoredBullet
)


class ScoreCombiner:
    """Combines scores from multiple scoring components."""

    def __init__(
        self,
        weights: Dict[str, float] = None,
        normalize_scores: bool = True
    ):
        """Initialize the score combiner.

        Args:
            weights: Dictionary mapping component names to their weights.
                    Defaults to equal weights if not provided.
            normalize_scores: Whether to normalize scores before combining.
        """
        self.weights = weights or {}
        self.normalize_scores = normalize_scores

    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to [0,1] range.

        Args:
            scores: Dictionary of scores to normalize.

        Returns:
            Normalized scores.
        """
        if not scores:
            return scores

        min_score = min(scores.values())
        max_score = max(scores.values())
        score_range = max_score - min_score

        if score_range == 0:
            return {k: 0.5 for k in scores}

        return {
            k: (v - min_score) / score_range
            for k, v in scores.items()
        }

    def _combine_bullet_scores(
        self,
        component_bullets: Dict[str, List[ScoredBullet]]
    ) -> List[ScoredBullet]:
        """Combine bullet scores from multiple components.

        Args:
            component_bullets: Dictionary mapping component names to their bullet scores.

        Returns:
            Combined bullet scores.
        """
        if not component_bullets:
            return []

        # Group bullets by content
        bullets_by_content = {}
        for component_name, bullets in component_bullets.items():
            for bullet in bullets:
                if bullet.content not in bullets_by_content:
                    bullets_by_content[bullet.content] = []
                bullets_by_content[bullet.content].append(bullet)

        # Combine scores for each bullet
        combined_bullets = []
        for content, bullets in bullets_by_content.items():
            scores = [bullet.score for bullet in bullets]
            confidences = [bullet.confidence for bullet in bullets]
            keywords = set()
            explanations = []

            for bullet in bullets:
                keywords.update(bullet.matched_keywords)
                if bullet.relevance_explanation:
                    explanations.append(bullet.relevance_explanation)

            combined_bullets.append(ScoredBullet(
                content=content,
                score=sum(scores) / len(scores),
                confidence=sum(confidences) / len(confidences),
                matched_keywords=list(keywords),
                relevance_explanation=" | ".join(explanations) if explanations else None
            ))

        return combined_bullets

    def _combine_entry_scores(
        self,
        component_entries: Dict[str, List[ScoredEntry]]
    ) -> List[ScoredEntry]:
        """Combine entry scores from multiple components.

        Args:
            component_entries: Dictionary mapping component names to their entry scores.

        Returns:
            Combined entry scores.
        """
        if not component_entries:
            return []

        # Group entries by ID
        entries_by_id = {}
        for component_name, entries in component_entries.items():
            for entry in entries:
                if entry.entry_id not in entries_by_id:
                    entries_by_id[entry.entry_id] = []
                entries_by_id[entry.entry_id].append(entry)

        # Combine scores for each entry
        combined_entries = []
        for entry_id, entries in entries_by_id.items():
            scores = [entry.score for entry in entries]
            confidences = [entry.confidence for entry in entries]
            keywords = set()
            explanations = []
            bullets_by_component = {}

            for entry in entries:
                keywords.update(entry.matched_keywords)
                if entry.relevance_explanation:
                    explanations.append(entry.relevance_explanation)
                bullets_by_component[entry.entry_id] = entry.bullets

            combined_entries.append(ScoredEntry(
                entry_id=entry_id,
                entry_type=entries[0].entry_type,  # Use type from first entry
                score=sum(scores) / len(scores),
                confidence=sum(confidences) / len(confidences),
                matched_keywords=list(keywords),
                relevance_explanation=" | ".join(explanations) if explanations else None,
                bullets=self._combine_bullet_scores(bullets_by_component)
            ))

        return combined_entries

    def _combine_section_scores(
        self,
        component_scores: Dict[str, Dict[str, SectionScore]],
        weights: Dict[str, float]
    ) -> Dict[str, SectionScore]:
        """Combine section scores from multiple components.

        Args:
            component_scores: Dictionary mapping component names to their section scores.
            weights: Dictionary mapping component names to their weights.

        Returns:
            Combined section scores.
        """
        combined_scores = {}
        section_ids = set()

        # Get all section IDs
        for scores in component_scores.values():
            section_ids.update(scores.keys())

        # Combine scores for each section
        for section_id in section_ids:
            section_scores = []
            section_confidences = []
            section_keywords = set()
            section_explanations = []
            entries_by_component = {}

            # Collect scores from each component
            for component_name, scores in component_scores.items():
                if section_id in scores:
                    score = scores[section_id]
                    weight = weights.get(component_name, 1.0)
                    
                    section_scores.append(score.score * weight)
                    section_confidences.append(score.confidence)
                    section_keywords.update(score.matched_keywords)
                    if score.relevance_explanation:
                        section_explanations.append(score.relevance_explanation)
                    entries_by_component[component_name] = score.entries

            if section_scores:
                # Calculate combined score
                total_weight = sum(weights.values())
                combined_score = sum(section_scores) / total_weight if total_weight > 0 else 0.0
                
                # Calculate average confidence
                avg_confidence = sum(section_confidences) / len(section_confidences)
                
                # Combine explanations
                combined_explanation = " | ".join(section_explanations) if section_explanations else None

                combined_scores[section_id] = SectionScore(
                    section_id=section_id,
                    score=combined_score,
                    confidence=avg_confidence,
                    matched_keywords=list(section_keywords),
                    relevance_explanation=combined_explanation,
                    entries=self._combine_entry_scores(entries_by_component)
                )

        return combined_scores

    def combine_results(
        self,
        results: List[ScoringResult],
        custom_weights: Dict[str, float] = None
    ) -> CombinedScore:
        """Combine results from multiple scoring components.

        Args:
            results: List of ScoringResult objects from different components.
            custom_weights: Optional custom weights to override default weights.

        Returns:
            CombinedScore containing the combined results.
        """
        start_time = time.time()

        # Use custom weights if provided, otherwise use default weights
        weights = custom_weights or self.weights

        # If no weights provided, use equal weights
        if not weights:
            weights = {
                result.component_name: 1.0
                for result in results
            }

        # Normalize weights
        total_weight = sum(weights.values())
        weights = {
            k: v / total_weight
            for k, v in weights.items()
        }

        # Combine section scores
        component_scores = {
            result.component_name: result.section_scores
            for result in results
        }
        combined_sections = self._combine_section_scores(component_scores, weights)

        # Calculate overall score
        if combined_sections:
            overall_score = sum(score.score for score in combined_sections.values()) / len(combined_sections)
        else:
            overall_score = 0.0

        # Collect metadata
        metadata = {
            "component_weights": weights,
            "component_processing_times": {
                result.component_name: result.processing_time
                for result in results
            }
        }

        return CombinedScore(
            section_scores=combined_sections,
            overall_score=overall_score,
            component_weights=weights,
            processing_time=time.time() - start_time,
            metadata=metadata
        ) 