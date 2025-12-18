"""
Journal Operations

Convert, categorize, and merge journal results.
"""
from typing import Dict, List, Optional, Set

from app.models.journal import Journal, JournalMetrics, JournalCategory
from .client import get_client
from .config import get_min_journal_works


def convert_to_journal(source: dict) -> Optional[Journal]:
    """
    Convert OpenAlex source to Journal model.

    Args:
        source: OpenAlex source dictionary.

    Returns:
        Journal model or None on error.
    """
    try:
        issns = source.get("issn", []) or []
        issn = issns[0] if issns else None

        topics = []
        for topic in (source.get("topics", []) or [])[:5]:
            if isinstance(topic, dict) and "display_name" in topic:
                topics.append(topic["display_name"])

        summary_stats = source.get("summary_stats", {}) or {}
        metrics = JournalMetrics(
            cited_by_count=source.get("cited_by_count"),
            works_count=source.get("works_count"),
            h_index=summary_stats.get("h_index"),
            i10_index=summary_stats.get("i10_index"),
            two_yr_mean_citedness=summary_stats.get("2yr_mean_citedness"),
        )

        return Journal(
            id=source.get("id", ""),
            name=source.get("display_name", "Unknown"),
            issn=issn,
            issn_l=source.get("issn_l"),
            publisher=source.get("host_organization_name"),
            homepage_url=source.get("homepage_url"),
            type=source.get("type"),
            is_oa=source.get("is_oa", False),
            is_in_doaj=source.get("is_in_doaj", False),  # DOAJ verification from OpenAlex
            apc_usd=source.get("apc_usd"),
            metrics=metrics,
            topics=topics,
        )
    except Exception as e:
        print(f"Error converting source: {e}")
        return None


def categorize_journals(journals: List[Journal]) -> List[Journal]:
    """
    Categorize journals by tier based on metrics.

    Categories:
    - TOP_TIER: h_index > 100 or works > 50000
    - BROAD_AUDIENCE: works > 10000
    - NICHE: works > 1000
    - EMERGING: everything else

    Args:
        journals: List of journals to categorize.

    Returns:
        Same list with category field populated.
    """
    for journal in journals:
        works = journal.metrics.works_count or 0
        h_index = journal.metrics.h_index or 0

        if h_index > 100 or works > 50000:
            journal.category = JournalCategory.TOP_TIER
            if not journal.match_reason or "Specialized" in journal.match_reason:
                journal.match_reason = "High impact journal"
        elif works > 10000:
            journal.category = JournalCategory.BROAD_AUDIENCE
            if not journal.match_reason or "Specialized" in journal.match_reason:
                journal.match_reason = "Wide readership"
        elif works > 1000:
            journal.category = JournalCategory.NICHE
            if not journal.match_reason or "Specialized" in journal.match_reason:
                journal.match_reason = "Specialized focus"
        else:
            journal.category = JournalCategory.EMERGING
            if not journal.match_reason:
                journal.match_reason = "Growing journal"

    return journals


def merge_journal_results(
    keyword_journals: Dict[str, Journal],
    topic_journals: Dict[str, dict],
) -> List[Journal]:
    """
    Merge results from keyword and topic searches.

    Journals appearing in both get a significant boost.

    Args:
        keyword_journals: Dict of journal_id -> Journal from keyword search.
        topic_journals: Dict of source_id -> {count, reason} from topic search.

    Returns:
        Merged and sorted list of journals.
    """
    client = get_client()
    min_works = get_min_journal_works()
    merged: Dict[str, Journal] = {}

    # Add journals from keyword search
    for jid, journal in keyword_journals.items():
        journal.relevance_score = 1.0
        merged[jid] = journal

    # Add/boost journals from topic search
    for source_id, data in topic_journals.items():
        if source_id in merged:
            # Appears in both - boost!
            merged[source_id].relevance_score += 2.0
            merged[source_id].match_reason = "Found in both keyword and topic search"
        else:
            # New from topics - load full details
            full_source = client.get_source_by_id(source_id)
            if full_source:
                works_count = full_source.get("works_count", 0)
                if works_count >= min_works:
                    journal = convert_to_journal(full_source)
                    if journal:
                        journal.relevance_score = 0.8
                        journal.match_reason = data.get("reason", "Topic match")
                        merged[source_id] = journal

    # Sort by relevance_score
    return sorted(merged.values(), key=lambda j: j.relevance_score, reverse=True)
