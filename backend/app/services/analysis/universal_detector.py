"""
Universal Discipline Detection using OpenAlex's ML Classification.

OpenAlex uses Specter 2 (SciBERT-based) + Citation Clustering to classify
every work into ~4,500 topics mapped to 252 subfields across 26 fields
and 4 domains.

This module leverages that system by finding similar works and aggregating
their classifications - works for ANY academic field!

Benefits:
- Works for ALL 252 subfields across all academic domains
- No manual keyword maintenance required
- Leverages Specter 2 ML + citation clustering
- Subfield IDs ready for direct API queries
"""

from typing import List, Dict, Optional
from collections import Counter
from dataclasses import dataclass, field
import logging
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class DetectedSubfield:
    """A detected academic subfield with OpenAlex metadata."""
    name: str                    # e.g., "Obstetrics and Gynecology"
    subfield_id: str            # e.g., "https://openalex.org/subfields/2729"
    numeric_id: int             # e.g., 2729
    confidence: float           # 0.0 - 1.0
    vote_count: int             # Raw vote count
    field_name: str             # e.g., "Medicine"
    field_id: str               # e.g., "https://openalex.org/fields/27"
    domain_name: str            # e.g., "Health Sciences"
    domain_id: str              # e.g., "https://openalex.org/domains/1"


@dataclass
class UniversalDetectionResult:
    """Complete result from universal detection."""
    subfields: List[DetectedSubfield] = field(default_factory=list)
    primary_domain: str = "Unknown"
    primary_field: str = "Unknown"
    similar_works_analyzed: int = 0
    detection_method: str = "openalex_ml"


class UniversalDisciplineDetector:
    """
    Detects academic disciplines using OpenAlex's ML classification system.

    How it works:
    1. Search OpenAlex for works similar to user's abstract
    2. Each work in OpenAlex has a primary_topic with subfield classification
    3. Aggregate subfields across similar works (voting)
    4. Return top subfields with full OpenAlex IDs

    Advantages:
    - Works for ALL 252 subfields across all academic domains
    - No manual keyword maintenance required
    - Leverages Specter 2 ML + citation clustering
    - Subfield IDs ready for direct API queries
    """

    def __init__(self):
        self._cache: Dict[str, UniversalDetectionResult] = {}

    def detect(
        self,
        title: str,
        abstract: str,
        keywords: Optional[List[str]] = None,
        top_n: int = 5,
        min_confidence: float = 0.05,
    ) -> UniversalDetectionResult:
        """
        Detect disciplines for any academic text (synchronous version).

        Args:
            title: Paper title
            abstract: Paper abstract
            keywords: Optional keywords
            top_n: Number of top subfields to return
            min_confidence: Minimum confidence threshold

        Returns:
            UniversalDetectionResult with detected subfields and metadata
        """
        # Build search query
        search_text = self._build_search_text(title, abstract, keywords)

        # Check cache
        cache_key = self._generate_cache_key(search_text)
        if cache_key in self._cache:
            logger.debug("Using cached detection result")
            return self._cache[cache_key]

        # Search for similar works (synchronous)
        similar_works = self._find_similar_works_sync(search_text)

        if not similar_works:
            logger.warning("No similar works found, returning empty result")
            return UniversalDetectionResult()

        # Aggregate subfields from similar works
        subfields = self._aggregate_subfields(similar_works, top_n, min_confidence)

        # Determine primary domain and field
        primary_domain = subfields[0].domain_name if subfields else "Unknown"
        primary_field = subfields[0].field_name if subfields else "Unknown"

        result = UniversalDetectionResult(
            subfields=subfields,
            primary_domain=primary_domain,
            primary_field=primary_field,
            similar_works_analyzed=len(similar_works),
        )

        # Cache result
        self._cache[cache_key] = result

        logger.info(
            f"Universal detection: {len(subfields)} subfields from {len(similar_works)} works. "
            f"Primary: {primary_field} ({primary_domain})"
        )

        return result

    def _build_search_text(
        self,
        title: str,
        abstract: str,
        keywords: Optional[List[str]] = None,
    ) -> str:
        """Build optimized search text for OpenAlex."""
        parts = [title, abstract]
        if keywords:
            parts.append(" ".join(keywords))

        search_text = " ".join(parts)

        # OpenAlex search limit is ~1000 chars for best results
        return search_text[:1000]

    def _generate_cache_key(self, text: str) -> str:
        """Generate a cache key from input text."""
        return hashlib.md5(text[:500].encode()).hexdigest()

    def _find_similar_works_sync(
        self,
        search_text: str,
        per_page: int = 50,
    ) -> List[Dict]:
        """
        Find similar works in OpenAlex (synchronous).

        Uses OpenAlex's semantic search which leverages the same
        embeddings used for classification.
        """
        import pyalex

        # Ensure pyalex is configured with email (required for polite pool)
        # This must be called before any pyalex operations
        from app.services.openalex.config import get_config
        get_config()

        try:
            # Use pyalex to search for works
            works = pyalex.Works().search(search_text).get(per_page=per_page)
            return works
        except Exception as e:
            logger.error(f"OpenAlex search failed: {e}")
            return []

    def _aggregate_subfields(
        self,
        works: List[Dict],
        top_n: int,
        min_confidence: float,
    ) -> List[DetectedSubfield]:
        """
        Aggregate subfield classifications from multiple works.

        Voting system:
        - Primary topic: 2 votes
        - Secondary topics (top 3): 1 vote each
        """
        subfield_votes: Counter = Counter()
        subfield_metadata: Dict[str, Dict] = {}

        for work in works:
            # Process primary topic (double weight)
            primary = work.get("primary_topic") or {}
            self._process_topic(primary, subfield_votes, subfield_metadata, weight=2)

            # Process secondary topics
            topics = work.get("topics") or []
            for topic in topics[:3]:  # Top 3 secondary topics
                self._process_topic(topic, subfield_votes, subfield_metadata, weight=1)

        # Calculate total votes for confidence
        total_votes = sum(subfield_votes.values()) or 1

        # Build result list
        results = []
        for subfield_id, votes in subfield_votes.most_common(top_n * 2):  # Get extra, filter later
            metadata = subfield_metadata.get(subfield_id, {})
            confidence = votes / total_votes

            if confidence < min_confidence:
                continue

            # Extract numeric ID
            numeric_id = self._extract_numeric_id(subfield_id)

            results.append(DetectedSubfield(
                name=metadata.get("display_name", "Unknown"),
                subfield_id=subfield_id,
                numeric_id=numeric_id,
                confidence=round(confidence, 3),
                vote_count=votes,
                field_name=metadata.get("field_name", "Unknown"),
                field_id=metadata.get("field_id", ""),
                domain_name=metadata.get("domain_name", "Unknown"),
                domain_id=metadata.get("domain_id", ""),
            ))

        return results[:top_n]

    def _process_topic(
        self,
        topic: Dict,
        votes: Counter,
        metadata: Dict[str, Dict],
        weight: int,
    ) -> None:
        """Process a single topic and update vote counts."""
        subfield = topic.get("subfield") or {}
        subfield_id = subfield.get("id")

        if not subfield_id:
            return

        votes[subfield_id] += weight

        if subfield_id not in metadata:
            field_data = topic.get("field") or {}
            domain = topic.get("domain") or {}

            metadata[subfield_id] = {
                "display_name": subfield.get("display_name", "Unknown"),
                "field_name": field_data.get("display_name", "Unknown"),
                "field_id": field_data.get("id", ""),
                "domain_name": domain.get("display_name", "Unknown"),
                "domain_id": domain.get("id", ""),
            }

    def _extract_numeric_id(self, openalex_id: str) -> int:
        """Extract numeric ID from OpenAlex URL."""
        # "https://openalex.org/subfields/2729" -> 2729
        try:
            return int(openalex_id.split("/")[-1])
        except (ValueError, IndexError):
            return 0


# Convenience function for quick detection
def detect_disciplines_universal(
    title: str,
    abstract: str,
    keywords: Optional[List[str]] = None,
    top_n: int = 5,
) -> List[Dict]:
    """
    Convenience function for universal discipline detection.

    Returns list of dicts for backward compatibility with existing code.

    Args:
        title: Paper title
        abstract: Paper abstract
        keywords: Optional keywords
        top_n: Number of subfields to return

    Returns:
        List of discipline dicts with OpenAlex metadata
    """
    detector = UniversalDisciplineDetector()
    result = detector.detect(title, abstract, keywords, top_n)

    return [
        {
            "name": sf.name,
            "subfield_id": sf.subfield_id,
            "numeric_id": sf.numeric_id,
            "openalex_subfield_id": sf.numeric_id,  # Backward compat
            "confidence": sf.confidence,
            "field": sf.field_name,
            "domain": sf.domain_name,
            "source": "openalex_ml",
        }
        for sf in result.subfields
    ]
