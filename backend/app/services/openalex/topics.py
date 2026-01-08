"""
Topics Service Module

Direct integration with OpenAlex Topics API for discipline detection
and topic hierarchy retrieval.

The Topics API provides:
- 4,500+ research topics organized into 252 subfields
- Each topic has: domain -> field -> subfield hierarchy
- ML-based classification using Specter 2 embeddings
"""
import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .client import get_client

logger = logging.getLogger(__name__)


@dataclass
class TopicHierarchy:
    """Represents the OpenAlex topic hierarchy."""

    domain_id: Optional[str] = None
    domain_name: Optional[str] = None
    field_id: Optional[str] = None
    field_name: Optional[str] = None
    subfield_id: Optional[int] = None
    subfield_name: Optional[str] = None
    topic_id: Optional[str] = None
    topic_name: Optional[str] = None


@dataclass
class DetectedSubfield:
    """A detected subfield with confidence score."""

    subfield_id: int
    subfield_name: str
    field_name: str
    domain_name: Optional[str]
    score: float
    confidence: float
    work_count: int = 0


@dataclass
class TopicsAnalysisResult:
    """Result of analyzing topics from similar works."""

    # Primary detection (backward compatible)
    primary_subfield: Optional[DetectedSubfield] = None

    # Multi-subfield detection (new)
    all_subfields: List[DetectedSubfield] = field(default_factory=list)

    # Raw topic IDs for journal filtering
    topic_ids: List[str] = field(default_factory=list)

    # Metadata
    works_analyzed: int = 0
    total_topics_found: int = 0


class TopicsService:
    """
    Service for working with OpenAlex Topics API.

    Provides methods for:
    - Searching topics from similar works
    - Getting topic hierarchy
    - Multi-subfield detection for interdisciplinary papers
    """

    def __init__(self):
        self.client = get_client()

    def analyze_topics_from_query(
        self,
        search_query: str,
        max_works: int = 50,
        min_confidence: float = 0.1,
    ) -> TopicsAnalysisResult:
        """
        Analyze topics from similar works to detect subfields.

        This is the main entry point for discipline detection.
        Returns multiple subfields for interdisciplinary papers.

        Args:
            search_query: Search query (typically extracted keywords from paper).
            max_works: Maximum number of works to analyze.
            min_confidence: Minimum confidence threshold for including subfields.

        Returns:
            TopicsAnalysisResult with detected subfields and topic IDs.
        """
        result = TopicsAnalysisResult()

        # Track scores by subfield ID for accuracy
        subfield_scores: Counter = Counter()
        subfield_data: Dict[int, Dict] = {}  # ID -> metadata
        topic_ids: Counter = Counter()
        total_score = 0.0

        # Search for similar works
        works = self.client.search_works(search_query, per_page=max_works)
        result.works_analyzed = len(works)

        if not works:
            logger.warning(f"No works found for query: {search_query[:50]}...")
            return result

        # Aggregate topics from all works
        for work in works:
            topics = work.get("topics") or []
            for topic in topics:
                topic_id = topic.get("id")
                if not topic_id:
                    continue

                # Weight by score
                score = topic.get("score", 1.0)
                topic_ids[topic_id] += score
                total_score += score
                result.total_topics_found += 1

                # Extract hierarchy
                subfield = topic.get("subfield", {})
                field_data = topic.get("field", {})
                domain = topic.get("domain", {})

                if subfield:
                    sf_id = self._extract_id(subfield.get("id"))
                    sf_name = subfield.get("display_name")

                    if sf_id and sf_name:
                        subfield_scores[sf_id] += score

                        # Store metadata for later
                        if sf_id not in subfield_data:
                            subfield_data[sf_id] = {
                                "name": sf_name,
                                "field": field_data.get("display_name", ""),
                                "domain": domain.get("display_name"),
                                "work_count": 0,
                            }
                        subfield_data[sf_id]["work_count"] += 1

        # Convert to DetectedSubfield objects
        all_subfields: List[DetectedSubfield] = []
        for sf_id, score in subfield_scores.most_common(10):
            if sf_id not in subfield_data:
                continue

            data = subfield_data[sf_id]
            confidence = score / total_score if total_score > 0 else 0

            # Apply minimum threshold
            if confidence < min_confidence:
                continue

            detected = DetectedSubfield(
                subfield_id=sf_id,
                subfield_name=data["name"],
                field_name=data["field"],
                domain_name=data["domain"],
                score=score,
                confidence=confidence,
                work_count=data["work_count"],
            )
            all_subfields.append(detected)

        result.all_subfields = all_subfields
        result.primary_subfield = all_subfields[0] if all_subfields else None
        result.topic_ids = [tid for tid, _ in topic_ids.most_common(10)]

        # Log results
        if all_subfields:
            summary = [(sf.subfield_name, f"{sf.confidence:.0%}") for sf in all_subfields[:5]]
            logger.info(f"Detected subfields: {summary}")
        else:
            logger.warning("No subfields detected from topics")

        return result

    def get_topic_hierarchy(self, topic_id: str) -> Optional[TopicHierarchy]:
        """
        Get full hierarchy for a topic ID.

        Note: OpenAlex Topics API doesn't have a direct endpoint for this.
        We extract hierarchy from works that have this topic.

        Args:
            topic_id: OpenAlex topic ID (full URL or short form).

        Returns:
            TopicHierarchy or None if not found.
        """
        # Normalize topic ID
        if not topic_id.startswith("https://"):
            topic_id = f"https://openalex.org/{topic_id}"

        # Search for a work with this topic
        try:
            import pyalex
            works = (
                pyalex.Works()
                .filter(topics={"id": topic_id})
                .get(per_page=1)
            )

            if not works:
                return None

            # Extract hierarchy from first work
            for topic in works[0].get("topics", []):
                if topic.get("id") == topic_id:
                    subfield = topic.get("subfield", {})
                    field_data = topic.get("field", {})
                    domain = topic.get("domain", {})

                    return TopicHierarchy(
                        domain_id=domain.get("id"),
                        domain_name=domain.get("display_name"),
                        field_id=field_data.get("id"),
                        field_name=field_data.get("display_name"),
                        subfield_id=self._extract_id(subfield.get("id")),
                        subfield_name=subfield.get("display_name"),
                        topic_id=topic_id,
                        topic_name=topic.get("display_name"),
                    )

            return None

        except Exception as e:
            logger.error(f"Error getting topic hierarchy for {topic_id}: {e}")
            return None

    def find_related_topics(
        self,
        topic_ids: List[str],
        limit: int = 10,
    ) -> List[str]:
        """
        Find topics related to the given topic IDs.

        Uses co-occurrence in works to find related topics.

        Args:
            topic_ids: List of topic IDs to find relations for.
            limit: Maximum number of related topics to return.

        Returns:
            List of related topic IDs.
        """
        if not topic_ids:
            return []

        related: Counter = Counter()

        # Search for works with these topics
        try:
            import pyalex
            works = (
                pyalex.Works()
                .filter(topics={"id": topic_ids[:5]})  # Limit to avoid long query
                .get(per_page=30)
            )

            # Collect co-occurring topics
            topic_id_set = set(topic_ids)
            for work in works:
                for topic in work.get("topics", []):
                    tid = topic.get("id")
                    if tid and tid not in topic_id_set:
                        score = topic.get("score", 1.0)
                        related[tid] += score

            return [tid for tid, _ in related.most_common(limit)]

        except Exception as e:
            logger.error(f"Error finding related topics: {e}")
            return []

    def _extract_id(self, openalex_url: Optional[str]) -> Optional[int]:
        """
        Extract numeric ID from OpenAlex URL.

        Args:
            openalex_url: Full OpenAlex URL like "https://openalex.org/subfields/1234"

        Returns:
            Numeric ID or None.
        """
        if not openalex_url:
            return None

        try:
            # Handle both full URL and short form
            parts = openalex_url.rstrip("/").split("/")
            return int(parts[-1])
        except (ValueError, IndexError):
            return None


# Global service instance
_topics_service: Optional[TopicsService] = None


def get_topics_service() -> TopicsService:
    """Get or create global topics service instance."""
    global _topics_service
    if _topics_service is None:
        _topics_service = TopicsService()
    return _topics_service


# Convenience functions for direct use


def analyze_topics(
    search_query: str,
    max_works: int = 50,
    min_confidence: float = 0.1,
) -> TopicsAnalysisResult:
    """
    Analyze topics from similar works.

    Convenience function for TopicsService.analyze_topics_from_query.
    """
    return get_topics_service().analyze_topics_from_query(
        search_query, max_works, min_confidence
    )


def get_multi_subfields(
    search_query: str,
    max_subfields: int = 5,
) -> List[DetectedSubfield]:
    """
    Get multiple detected subfields for interdisciplinary papers.

    Args:
        search_query: Search query from paper keywords/title.
        max_subfields: Maximum number of subfields to return.

    Returns:
        List of detected subfields sorted by confidence.
    """
    result = analyze_topics(search_query)
    return result.all_subfields[:max_subfields]
