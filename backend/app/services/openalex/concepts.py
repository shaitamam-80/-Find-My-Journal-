"""
Concepts Analyzer Module

Analyzes OpenAlex concepts from works for additional discipline signals.

Note: OpenAlex is transitioning from Concepts to Topics.
Concepts are still useful for backward compatibility and as
additional signals for discipline detection.
"""
import logging
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .client import get_client

logger = logging.getLogger(__name__)


@dataclass
class Concept:
    """Represents an OpenAlex concept."""

    concept_id: str
    display_name: str
    level: int  # 0 = most general, 5 = most specific
    score: float
    frequency: int = 1
    wikidata_id: Optional[str] = None


@dataclass
class ConceptsAnalysisResult:
    """Result of analyzing concepts from works."""

    # High-level concepts (level 0-1)
    high_level_concepts: List[Concept]

    # Specific concepts (level 2+)
    specific_concepts: List[Concept]

    # All concepts sorted by relevance
    all_concepts: List[Concept]

    # Works analyzed
    works_count: int = 0


class ConceptsAnalyzer:
    """
    Analyzes concepts from OpenAlex works.

    Useful for:
    - Cross-referencing discipline detection
    - Finding interdisciplinary connections
    - Identifying specific methodological approaches
    """

    def __init__(self):
        self.client = get_client()

    def aggregate_concepts(
        self,
        search_query: str,
        max_works: int = 50,
    ) -> ConceptsAnalysisResult:
        """
        Aggregate concepts from similar works.

        Args:
            search_query: Search query to find similar works.
            max_works: Maximum number of works to analyze.

        Returns:
            ConceptsAnalysisResult with aggregated concepts.
        """
        concept_scores: Counter = Counter()
        concept_data: Dict[str, Dict] = {}

        # Search for similar works
        works = self.client.search_works(search_query, per_page=max_works)

        if not works:
            logger.warning(f"No works found for concept analysis: {search_query[:50]}...")
            return ConceptsAnalysisResult(
                high_level_concepts=[],
                specific_concepts=[],
                all_concepts=[],
            )

        for work in works:
            # Extract concepts
            for concept in work.get("concepts", []):
                cid = concept.get("id")
                if not cid:
                    continue

                score = concept.get("score", 0.5)
                concept_scores[cid] += score

                # Store metadata
                if cid not in concept_data:
                    concept_data[cid] = {
                        "display_name": concept.get("display_name", ""),
                        "level": concept.get("level", 0),
                        "wikidata": concept.get("wikidata"),
                        "frequency": 0,
                    }
                concept_data[cid]["frequency"] += 1

        # Convert to Concept objects
        all_concepts: List[Concept] = []
        for cid, total_score in concept_scores.most_common(30):
            if cid not in concept_data:
                continue

            data = concept_data[cid]
            all_concepts.append(Concept(
                concept_id=cid,
                display_name=data["display_name"],
                level=data["level"],
                score=total_score / len(works),  # Normalize by works count
                frequency=data["frequency"],
                wikidata_id=data["wikidata"],
            ))

        # Separate by level
        high_level = [c for c in all_concepts if c.level <= 1]
        specific = [c for c in all_concepts if c.level >= 2]

        logger.info(
            f"Analyzed {len(works)} works: "
            f"{len(high_level)} high-level, {len(specific)} specific concepts"
        )

        return ConceptsAnalysisResult(
            high_level_concepts=high_level,
            specific_concepts=specific,
            all_concepts=all_concepts,
            works_count=len(works),
        )

    def filter_by_relevance(
        self,
        concepts: List[Concept],
        min_score: float = 0.3,
        min_frequency: int = 2,
    ) -> List[Concept]:
        """
        Filter concepts by relevance thresholds.

        Args:
            concepts: List of concepts to filter.
            min_score: Minimum score threshold.
            min_frequency: Minimum frequency threshold.

        Returns:
            Filtered list of concepts.
        """
        return [
            c for c in concepts
            if c.score >= min_score and c.frequency >= min_frequency
        ]

    def get_discipline_hints(
        self,
        search_query: str,
    ) -> List[str]:
        """
        Get discipline hints from high-level concepts.

        Useful as additional signals for discipline detection.

        Args:
            search_query: Search query.

        Returns:
            List of discipline/field names from concepts.
        """
        result = self.aggregate_concepts(search_query, max_works=30)

        # Filter high-level concepts
        relevant = self.filter_by_relevance(
            result.high_level_concepts,
            min_score=0.2,
            min_frequency=3,
        )

        return [c.display_name for c in relevant[:5]]

    def get_methodology_hints(
        self,
        search_query: str,
    ) -> List[str]:
        """
        Get methodology hints from specific concepts.

        Identifies methodological approaches used in similar works.

        Args:
            search_query: Search query.

        Returns:
            List of methodology/technique names.
        """
        result = self.aggregate_concepts(search_query, max_works=30)

        # Focus on specific concepts (level 3+) which often indicate methods
        method_concepts = [c for c in result.specific_concepts if c.level >= 3]
        relevant = self.filter_by_relevance(
            method_concepts,
            min_score=0.15,
            min_frequency=2,
        )

        return [c.display_name for c in relevant[:5]]


# Global service instance
_concepts_analyzer: Optional[ConceptsAnalyzer] = None


def get_concepts_analyzer() -> ConceptsAnalyzer:
    """Get or create global concepts analyzer instance."""
    global _concepts_analyzer
    if _concepts_analyzer is None:
        _concepts_analyzer = ConceptsAnalyzer()
    return _concepts_analyzer


# Convenience functions


def analyze_concepts(
    search_query: str,
    max_works: int = 50,
) -> ConceptsAnalysisResult:
    """
    Analyze concepts from similar works.

    Convenience function for ConceptsAnalyzer.aggregate_concepts.
    """
    return get_concepts_analyzer().aggregate_concepts(search_query, max_works)


def get_discipline_hints(search_query: str) -> List[str]:
    """
    Get discipline hints from concepts.

    Convenience function for ConceptsAnalyzer.get_discipline_hints.
    """
    return get_concepts_analyzer().get_discipline_hints(search_query)
