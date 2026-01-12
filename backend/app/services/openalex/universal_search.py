"""
Universal Journal Search

Works for ANY academic discipline (252 subfields) by leveraging
OpenAlex's ML-based classification system.

Pipeline:
1. Universal discipline detection (OpenAlex ML via Specter 2)
2. Article type detection
3. Journal search per subfield (using numeric IDs)
4. Dynamic normalized scoring
5. Merge with cross-discipline representation
"""

import logging
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from app.models.journal import Journal
from .client import get_client
from .journals import convert_to_journal, categorize_journals
from .scoring import EnhancedJournalScorer, ScoringContext

logger = logging.getLogger(__name__)


# Lazy imports to avoid circular dependency with app.services.analysis
def _get_analysis_imports():
    """Lazy import analysis modules to break circular import."""
    from app.services.analysis import (
        ArticleTypeDetector,
        get_smart_analyzer,
    )
    from app.services.analysis.dynamic_stats import (
        get_subfield_stats,
        calculate_percentile_score,
    )
    return get_smart_analyzer, ArticleTypeDetector, get_subfield_stats, calculate_percentile_score


class UniversalSearchResult:
    """Result from universal journal search."""

    def __init__(
        self,
        journals: List[Journal],
        detected_disciplines: List[Dict],
        article_type: Optional[Dict] = None,
        detection_method: str = "universal_openalex_ml",
        primary_domain: Optional[str] = None,
        primary_field: Optional[str] = None,
    ):
        self.journals = journals
        self.detected_disciplines = detected_disciplines
        self.article_type = article_type
        self.detection_method = detection_method
        self.primary_domain = primary_domain
        self.primary_field = primary_field


def search_journals_universal(
    title: str,
    abstract: str,
    keywords: Optional[List[str]] = None,
    prefer_open_access: bool = False,
    max_results: int = 15,
) -> UniversalSearchResult:
    """
    Universal journal search - works for ANY academic discipline.

    Pipeline:
    1. Universal discipline detection (OpenAlex ML)
    2. Article type detection
    3. Journal search per subfield (using subfield IDs)
    4. Dynamic normalized scoring
    5. Merge with cross-discipline representation

    Args:
        title: Paper title
        abstract: Paper abstract
        keywords: Optional keywords
        prefer_open_access: Prioritize OA journals
        max_results: Maximum journals to return

    Returns:
        UniversalSearchResult with journals and metadata
    """
    # Lazy imports to avoid circular dependency
    get_smart_analyzer, ArticleTypeDetector, get_subfield_stats, calculate_percentile_score = _get_analysis_imports()

    # 1. Use SmartAnalyzer for discipline detection (Phase 4)
    smart_analyzer = get_smart_analyzer(enable_llm=False)
    analysis_result = smart_analyzer.analyze(
        title=title,
        abstract=abstract,
        user_keywords=keywords,
    )

    # Convert SmartAnalyzer disciplines to dict format
    detected_disciplines = []
    for disc in analysis_result.disciplines:
        # Extract numeric ID from subfield_id string if possible
        numeric_id = None
        if disc.subfield_id and disc.subfield_id != "llm-detected":
            try:
                numeric_id = int(disc.subfield_id.split("/")[-1])
            except (ValueError, AttributeError):
                pass

        detected_disciplines.append({
            "name": disc.subfield_name,
            "confidence": disc.confidence,
            "field": disc.field_name,
            "domain": disc.domain_name,
            "numeric_id": numeric_id,
            "openalex_subfield_id": disc.subfield_id if disc.subfield_id != "llm-detected" else None,
            "source": "smart_analyzer",
        })

    if not detected_disciplines:
        logger.warning("No disciplines detected")
        return UniversalSearchResult(
            journals=[],
            detected_disciplines=[],
        )

    primary_domain = detected_disciplines[0].get("domain")
    primary_field = detected_disciplines[0].get("field")

    logger.info(
        f"Universal detection: {len(detected_disciplines)} disciplines. "
        f"Primary: {detected_disciplines[0].get('name')} ({primary_domain})"
    )

    # 2. Detect article type (existing logic)
    article_type_detector = ArticleTypeDetector()
    detected_article_type = article_type_detector.detect(abstract, title)
    article_type_dict = article_type_detector.to_dict(detected_article_type)

    # 3. Search journals for each detected subfield
    all_journals: Dict[str, List[Journal]] = {}

    for disc in detected_disciplines[:5]:  # Top 5 disciplines
        subfield_id = disc.get("numeric_id") or disc.get("openalex_subfield_id")
        subfield_name = disc.get("name", "")

        if not subfield_id:
            continue

        # Get journals in this subfield
        journals = find_journals_by_subfield_id_universal(subfield_id)

        if journals:
            # Get dynamic stats for scoring
            stats = get_subfield_stats(subfield_id, subfield_name)

            # Score journals relative to their subfield
            scored_journals = score_journals_universal(
                journals=journals,
                subfield_id=subfield_id,
                subfield_name=subfield_name,
                article_type=article_type_dict,
                detected_disciplines=detected_disciplines,
                prefer_open_access=prefer_open_access,
            )

            all_journals[subfield_name] = scored_journals
            logger.info(f"Found {len(scored_journals)} journals for {subfield_name}")

    # 4. Merge results ensuring representation from each discipline
    merged = merge_journal_results_universal(
        discipline_results=all_journals,
        detected_disciplines=detected_disciplines,
        max_results=max_results,
    )

    # Categorize journals
    categorized = categorize_journals(merged)

    # Normalize scores to 0-1 range
    if categorized:
        max_score = max(j.relevance_score for j in categorized)
        if max_score > 0:
            for journal in categorized:
                journal.relevance_score = journal.relevance_score / max_score

    return UniversalSearchResult(
        journals=categorized[:max_results],
        detected_disciplines=detected_disciplines,
        article_type=article_type_dict,
        detection_method="universal_openalex_ml" if detected_disciplines[0].get("source") == "openalex_ml" else "keyword_fallback",
        primary_domain=primary_domain,
        primary_field=primary_field,
    )


def find_journals_by_subfield_id_universal(
    subfield_id: int,
    max_results: int = 30,
) -> List[Journal]:
    """
    Find journals by OpenAlex subfield ID.

    Works for ANY of the 252 subfields.

    Args:
        subfield_id: OpenAlex numeric subfield ID
        max_results: Maximum journals to return

    Returns:
        List of Journal objects
    """
    client = get_client()

    try:
        # Get top journals publishing in this subfield
        results = client.find_sources_by_subfield_id(
            subfield_id=subfield_id,
            per_page=max_results,
        )

        journals = []
        for entry in results[:max_results]:
            source_id = entry.get("key")
            count = entry.get("count", 0)

            if source_id and count > 0:
                full_source = client.get_source_by_id(source_id)
                if full_source:
                    journal = convert_to_journal(full_source)
                    if journal:
                        journal.match_reason = f"Active in this subfield ({count} recent works)"
                        journals.append(journal)

        return journals
    except Exception as e:
        logger.error(f"Failed to find journals for subfield {subfield_id}: {e}")
        return []


def score_journals_universal(
    journals: List[Journal],
    subfield_id: int,
    subfield_name: str,
    article_type: Optional[Dict],
    detected_disciplines: List[Dict],
    prefer_open_access: bool = False,
) -> List[Journal]:
    """
    Score journals using dynamic field-specific statistics.

    Args:
        journals: List of journals to score
        subfield_id: The subfield these journals belong to
        subfield_name: Display name of the subfield
        article_type: Detected article type
        detected_disciplines: All detected disciplines
        prefer_open_access: Prioritize OA journals

    Returns:
        List of scored journals
    """
    # Lazy imports to avoid circular dependency
    _, _, get_subfield_stats, calculate_percentile_score = _get_analysis_imports()

    # Get dynamic stats for this subfield
    stats = get_subfield_stats(subfield_id, subfield_name)

    # Create scoring context
    scoring_context = ScoringContext(
        detected_disciplines=detected_disciplines,
        article_type=article_type,
        keywords=[],
        prefer_open_access=prefer_open_access,
    )

    scorer = EnhancedJournalScorer()

    for journal in journals:
        # Calculate normalized scores based on field statistics
        h_index = journal.metrics.h_index or 0
        citedness = journal.metrics.two_yr_mean_citedness or 0

        # Calculate percentile scores
        h_percentile = calculate_percentile_score(
            h_index,
            stats.median_h_index,
            stats.p75_h_index,
            stats.p90_h_index,
        )

        citedness_percentile = calculate_percentile_score(
            citedness,
            stats.median_citedness,
            stats.p75_citedness,
            stats.p90_citedness,
        )

        # Combined score (citedness weighted more for research impact)
        field_normalized_score = (h_percentile * 0.3) + (citedness_percentile * 0.7)

        # Add OA bonus if preferred
        oa_bonus = 10 if prefer_open_access and journal.is_oa else 0

        journal.relevance_score = field_normalized_score + oa_bonus

        # Generate match details
        journal.match_details = [
            f"Field-normalized score: {field_normalized_score:.0f}/100",
            f"H-index percentile: {h_percentile:.0f}%",
            f"Citation percentile: {citedness_percentile:.0f}%",
        ]

    # Sort by score
    journals.sort(key=lambda j: j.relevance_score, reverse=True)

    return journals


def merge_journal_results_universal(
    discipline_results: Dict[str, List[Journal]],
    detected_disciplines: List[Dict],
    max_results: int = 15,
) -> List[Journal]:
    """
    Merge journals ensuring representation from each detected discipline.

    Strategy:
    - Primary discipline: 5 journals
    - Each secondary discipline: 2-3 journals
    - Fill remaining with best overall scores

    Args:
        discipline_results: Dict of discipline_name -> journals
        detected_disciplines: List of detected disciplines
        max_results: Maximum journals to return

    Returns:
        Merged list of journals
    """
    merged = []
    seen_ids = set()

    # Slots per discipline
    primary_slots = 5
    secondary_slots = 3

    # Process each discipline in order
    for i, disc in enumerate(detected_disciplines):
        disc_name = disc.get("name", "")
        journals = discipline_results.get(disc_name, [])

        slots = primary_slots if i == 0 else secondary_slots
        added = 0

        for journal in journals:
            if journal.id not in seen_ids and added < slots:
                # Tag with discipline info
                if i == 0:
                    journal.match_reason = f"Primary field: {disc_name}"
                else:
                    journal.match_reason = f"Cross-discipline: {disc_name}"

                merged.append(journal)
                seen_ids.add(journal.id)
                added += 1

    # Fill remaining slots with best overall
    all_journals = [j for js in discipline_results.values() for j in js]
    all_journals.sort(key=lambda j: j.relevance_score, reverse=True)

    for journal in all_journals:
        if len(merged) >= max_results:
            break
        if journal.id not in seen_ids:
            merged.append(journal)
            seen_ids.add(journal.id)

    # Final sort by score
    merged.sort(key=lambda j: j.relevance_score, reverse=True)

    return merged[:max_results]


def get_search_metadata(result: UniversalSearchResult) -> Dict:
    """
    Get metadata about the search for API response.

    Args:
        result: The search result

    Returns:
        Dict with metadata
    """
    return {
        "detection_method": result.detection_method,
        "primary_domain": result.primary_domain,
        "primary_field": result.primary_field,
        "discipline_count": len(result.detected_disciplines),
        "journal_count": len(result.journals),
        "article_type": result.article_type.get("type") if result.article_type else None,
    }
