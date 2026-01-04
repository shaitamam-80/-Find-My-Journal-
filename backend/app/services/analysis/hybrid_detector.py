"""
Hybrid Discipline Detector

Combines Universal (OpenAlex ML) with keyword-based fallback for reliability.

Strategy:
1. Try Universal detection first (leverages OpenAlex Specter 2 ML)
2. If Universal fails or returns insufficient results, fall back to keywords
3. Optionally merge results from both approaches
"""

from typing import List, Dict, Optional
import logging

from .universal_detector import detect_disciplines_universal, UniversalDisciplineDetector
from .discipline_detector import MultiDisciplineDetector, OPENALEX_FIELD_MAPPING

logger = logging.getLogger(__name__)


def detect_disciplines_hybrid(
    title: str,
    abstract: str,
    keywords: Optional[List[str]] = None,
    prefer_universal: bool = True,
    min_results: int = 2,
) -> List[Dict]:
    """
    Hybrid detection: tries Universal first, falls back to keywords.

    Args:
        title: Paper title
        abstract: Paper abstract
        keywords: Optional keywords
        prefer_universal: If True, use OpenAlex ML first
        min_results: Minimum results needed before trying fallback

    Returns:
        List of detected disciplines
    """
    if prefer_universal:
        try:
            # Try Universal (OpenAlex ML) first
            result = detect_disciplines_universal(title, abstract, keywords)

            if result and len(result) >= min_results:
                logger.info(f"Universal detection succeeded: {len(result)} disciplines")
                return result
            else:
                logger.warning(
                    f"Universal detection returned only {len(result) if result else 0} results, "
                    f"trying fallback"
                )
        except Exception as e:
            logger.error(f"Universal detection failed: {e}")

    # Fallback to keyword-based detection
    logger.info("Using keyword-based fallback detection")
    return _keyword_fallback_detection(title, abstract, keywords)


def _keyword_fallback_detection(
    title: str,
    abstract: str,
    keywords: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Keyword-based detection fallback.

    Args:
        title: Paper title
        abstract: Paper abstract
        keywords: Optional keywords

    Returns:
        List of detected disciplines in universal format
    """
    detector = MultiDisciplineDetector()
    keyword_result = detector.detect(title, abstract, keywords or [])

    # Convert to universal format
    return [
        {
            "name": d.openalex_subfield_id or d.name,  # Use subfield name if available
            "subfield_id": None,
            "numeric_id": d.openalex_subfield_numeric_id,
            "openalex_subfield_id": d.openalex_subfield_numeric_id,
            "confidence": d.confidence,
            "field": d.openalex_field_id or "Medicine",  # Default to Medicine for backward compat
            "domain": "Health Sciences" if d.openalex_field_id == "Medicine" else None,
            "source": "keyword_fallback",
        }
        for d in keyword_result
    ]


def detect_disciplines_merged(
    title: str,
    abstract: str,
    keywords: Optional[List[str]] = None,
    universal_weight: float = 0.7,
    keyword_weight: float = 0.3,
) -> List[Dict]:
    """
    Merge results from both Universal and Keyword detection.

    Useful when you want comprehensive coverage across both ML-detected
    and keyword-detected disciplines.

    Args:
        title: Paper title
        abstract: Paper abstract
        keywords: Optional keywords
        universal_weight: Weight for universal detection results
        keyword_weight: Weight for keyword detection results

    Returns:
        Merged list of detected disciplines
    """
    # Get results from both methods
    universal_results = []
    keyword_results = []

    try:
        universal_results = detect_disciplines_universal(title, abstract, keywords)
        for r in universal_results:
            r["weight"] = universal_weight
    except Exception as e:
        logger.warning(f"Universal detection failed in merge: {e}")

    try:
        keyword_results = _keyword_fallback_detection(title, abstract, keywords)
        for r in keyword_results:
            r["weight"] = keyword_weight
    except Exception as e:
        logger.warning(f"Keyword detection failed in merge: {e}")

    # Merge by subfield ID (prefer universal results for same subfield)
    merged: Dict[int, Dict] = {}

    # Add universal results first (higher priority)
    for r in universal_results:
        numeric_id = r.get("numeric_id") or r.get("openalex_subfield_id")
        if numeric_id:
            merged[numeric_id] = r

    # Add keyword results (only if not already present)
    for r in keyword_results:
        numeric_id = r.get("numeric_id") or r.get("openalex_subfield_id")
        if numeric_id and numeric_id not in merged:
            merged[numeric_id] = r
        elif numeric_id and numeric_id in merged:
            # Boost confidence for results found by both methods
            merged[numeric_id]["confidence"] = min(
                merged[numeric_id]["confidence"] * 1.2, 1.0
            )

    # Sort by weighted confidence
    results = list(merged.values())
    results.sort(
        key=lambda x: x.get("confidence", 0) * x.get("weight", 1.0),
        reverse=True,
    )

    # Remove weight field from output
    for r in results:
        r.pop("weight", None)

    return results


class HybridDisciplineDetector:
    """
    Class-based hybrid detector for more control over detection process.
    """

    def __init__(
        self,
        prefer_universal: bool = True,
        min_universal_results: int = 2,
    ):
        """
        Initialize hybrid detector.

        Args:
            prefer_universal: Whether to try universal detection first
            min_universal_results: Minimum results before trying fallback
        """
        self.prefer_universal = prefer_universal
        self.min_universal_results = min_universal_results
        self._universal_detector = UniversalDisciplineDetector()
        self._keyword_detector = MultiDisciplineDetector()

    def detect(
        self,
        title: str,
        abstract: str,
        keywords: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Detect disciplines using hybrid approach.

        Args:
            title: Paper title
            abstract: Paper abstract
            keywords: Optional keywords

        Returns:
            List of detected disciplines
        """
        return detect_disciplines_hybrid(
            title=title,
            abstract=abstract,
            keywords=keywords,
            prefer_universal=self.prefer_universal,
            min_results=self.min_universal_results,
        )

    def detect_with_metadata(
        self,
        title: str,
        abstract: str,
        keywords: Optional[List[str]] = None,
    ) -> Dict:
        """
        Detect disciplines and return with metadata about detection method.

        Args:
            title: Paper title
            abstract: Paper abstract
            keywords: Optional keywords

        Returns:
            Dict with disciplines and detection metadata
        """
        disciplines = self.detect(title, abstract, keywords)

        # Determine which method was used
        detection_method = "hybrid"
        if disciplines:
            sources = set(d.get("source") for d in disciplines)
            if sources == {"openalex_ml"}:
                detection_method = "openalex_ml"
            elif sources == {"keyword_fallback"}:
                detection_method = "keyword_fallback"

        # Get primary domain/field
        primary_domain = None
        primary_field = None
        if disciplines:
            primary_domain = disciplines[0].get("domain")
            primary_field = disciplines[0].get("field")

        return {
            "disciplines": disciplines,
            "detection_method": detection_method,
            "primary_domain": primary_domain,
            "primary_field": primary_field,
            "discipline_count": len(disciplines),
        }
