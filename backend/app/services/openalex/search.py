"""
Journal Search Operations

Hybrid search combining keywords and topic matching.
"""
from collections import Counter
from typing import Dict, List, Optional, Tuple, Set

from app.models.journal import Journal
from .client import get_client
from .config import get_min_journal_works
from .constants import load_core_journals, get_key_journals_for_discipline
from .utils import extract_search_terms, detect_discipline
from .scoring import calculate_relevance_score
from .journals import convert_to_journal, categorize_journals, merge_journal_results


def find_journals_from_works(
    search_query: str,
    prefer_open_access: bool = False,
) -> Dict[str, dict]:
    """
    Find journals by searching for papers on the topic.

    Fetches up to 2 pages (400 works) for better coverage.

    Args:
        search_query: Combined search terms.
        prefer_open_access: Prioritize OA journals.

    Returns:
        Dict of source_id -> source data with frequency count.
    """
    client = get_client()
    journal_counts: Dict[str, dict] = {}

    def process_works(works: List[dict]) -> None:
        for work in works:
            primary_location = work.get("primary_location", {})
            source = primary_location.get("source") if primary_location else None

            if source and source.get("type") == "journal":
                source_id = source.get("id", "")
                if source_id:
                    if source_id not in journal_counts:
                        journal_counts[source_id] = {
                            "source": source,
                            "count": 0,
                            "is_oa": primary_location.get("is_oa", False),
                        }
                    journal_counts[source_id]["count"] += 1

    # Page 1
    works_page1 = client.search_works(search_query, per_page=200, page=1)
    process_works(works_page1)

    # Page 2 if first was full
    if len(works_page1) == 200:
        works_page2 = client.search_works(search_query, per_page=200, page=2)
        process_works(works_page2)

    return journal_counts


def get_topics_from_similar_works(search_query: str) -> Tuple[List[str], str, str]:
    """
    Extract Topic IDs and subfield/field from similar papers.

    Uses the Topics API to get both topic IDs for journal search
    AND the subfield/field hierarchy for discipline detection.

    Args:
        search_query: Combined title and abstract text.

    Returns:
        Tuple of:
        - Top 5 most frequent topic IDs
        - Most common subfield (e.g., "Endocrinology, Diabetes and Metabolism")
        - Most common field (e.g., "Medicine")
    """
    client = get_client()
    topic_ids: Counter = Counter()
    subfields: Counter = Counter()
    fields: Counter = Counter()

    works = client.search_works(search_query, per_page=50)

    for work in works:
        topics = work.get("topics") or []
        for topic in topics:
            topic_id = topic.get("id")
            if topic_id:
                # Weight by score if available
                score = topic.get("score", 1.0)
                topic_ids[topic_id] += score

                # Extract subfield and field from OpenAlex hierarchy
                subfield = topic.get("subfield", {})
                field = topic.get("field", {})

                if subfield and subfield.get("display_name"):
                    subfields[subfield["display_name"]] += score
                if field and field.get("display_name"):
                    fields[field["display_name"]] += score

    top_topic_ids = [tid for tid, _ in topic_ids.most_common(5)]
    top_subfield = subfields.most_common(1)[0][0] if subfields else ""
    top_field = fields.most_common(1)[0][0] if fields else ""

    return top_topic_ids, top_subfield, top_field


def get_topic_ids_from_similar_works(search_query: str) -> List[str]:
    """
    Extract Topic IDs from similar papers (legacy wrapper).

    Kept for backward compatibility.
    """
    topic_ids, _, _ = get_topics_from_similar_works(search_query)
    return topic_ids


def find_journals_by_topics(topic_ids: List[str]) -> Dict[str, dict]:
    """
    Find top journals across all identified topics.

    Uses group_by for server-side aggregation.

    Args:
        topic_ids: List of OpenAlex Topic IDs.

    Returns:
        Dict of source_id -> {count, reason}.
    """
    if not topic_ids:
        return {}

    client = get_client()
    journals: Dict[str, dict] = {}

    results = client.group_works_by_source(topic_ids)

    for entry in results:
        source_id = entry.get("key")
        count = entry.get("count", 0)
        if source_id and count > 0:
            journals[source_id] = {
                "count": count,
                "reason": "High activity in relevant research topics",
            }

    return journals


def search_journals_by_keywords(
    keywords: List[str],
    prefer_open_access: bool = False,
    min_works_count: Optional[int] = None,
    discipline: str = "general",
    core_journals: Optional[Set[str]] = None,
) -> List[Journal]:
    """
    Search for journals matching given keywords.

    Uses hybrid approach: Works-based + Direct source search.

    Args:
        keywords: List of search terms.
        prefer_open_access: Prioritize OA journals.
        min_works_count: Minimum number of works.
        discipline: Detected discipline for filtering.
        core_journals: Set of core journal names for boosting.

    Returns:
        List of matching journals.
    """
    if not keywords:
        return []

    if core_journals is None:
        core_journals = load_core_journals()

    client = get_client()
    min_works = min_works_count or get_min_journal_works()
    all_journals: Dict[str, Journal] = {}

    # 1. WORKS Search (papers that match the topic)
    search_query = " ".join(keywords[:5])
    journal_data = find_journals_from_works(search_query, prefer_open_access)

    # 2. DIRECT SOURCES Search (journals with matching names)
    direct_sources = client.search_sources(search_query)
    for source in direct_sources:
        source_id = source.get("id", "")
        if source_id and source_id not in journal_data:
            journal_data[source_id] = {
                "source": source,
                "count": 0,  # Will be boosted by Name Match score
                "is_oa": source.get("is_oa", False),
            }

    # Sort by frequency and get details for top 50 candidates
    sorted_sources = sorted(
        journal_data.items(), key=lambda x: x[1]["count"], reverse=True
    )[:50]

    for source_id, data in sorted_sources:
        full_source = data.get("source")
        if not full_source or "works_count" not in full_source:
            full_source = client.get_source_by_id(source_id)

        if not full_source:
            continue

        works_count = full_source.get("works_count", 0)
        if works_count < min_works:
            continue

        journal = convert_to_journal(full_source)
        if not journal or journal.id in all_journals:
            continue

        # Calculate initial relevance score
        score = calculate_relevance_score(
            journal=journal,
            discipline=discipline,
            is_topic_match=False,
            is_keyword_match=True,
            search_terms=keywords,
            core_journals=core_journals,
        )

        # Match reason
        if data["count"] > 0:
            journal.match_reason = f"Published {data['count']} papers on this topic"
        else:
            journal.match_reason = "Direct name match"

        # Add small boost for paper count to break ties
        journal.relevance_score = score + (data["count"] / 100.0)
        all_journals[journal.id] = journal

    # Sort by relevance_score and quality metrics
    journals = sorted(
        all_journals.values(),
        key=lambda j: (
            j.is_oa if prefer_open_access else False,
            j.relevance_score,
            1 if "papers on this topic" in (j.match_reason or "") else 0,
            j.metrics.h_index or 0,
        ),
        reverse=True,
    )

    return journals[:15]  # Return more candidates for hybrid merge


def inject_key_journals(
    discipline: str,
    existing_journals: Dict[str, Journal],
    core_journals: Set[str],
    search_terms: List[str],
) -> Dict[str, Journal]:
    """
    Proactively inject key journals for a discipline that may be missed by search.

    This ensures important discipline-specific journals always appear.

    Args:
        discipline: Detected discipline.
        existing_journals: Already found journals.
        core_journals: Set of core journal names.
        search_terms: Search terms for scoring.

    Returns:
        Updated journal dict with injected journals.
    """
    client = get_client()
    key_journal_names = get_key_journals_for_discipline(discipline)

    for journal_name in key_journal_names:
        # Search for journal by name
        sources = client.search_sources(journal_name, per_page=5)

        for source in sources:
            source_id = source.get("id", "")
            display_name = source.get("display_name", "")

            # Check if name matches closely
            if journal_name.lower() in display_name.lower():
                if source_id and source_id not in existing_journals:
                    journal = convert_to_journal(source)
                    if journal:
                        journal.match_reason = f"Key journal for {discipline.replace('_', ' ')}"
                        # Calculate score with discipline boost
                        journal.relevance_score = calculate_relevance_score(
                            journal=journal,
                            discipline=discipline,
                            is_topic_match=True,  # Treat as topic match
                            is_keyword_match=True,
                            search_terms=search_terms,
                            core_journals=core_journals,
                        )
                        existing_journals[source_id] = journal
                break  # Found the journal

    return existing_journals


def search_journals_by_text(
    title: str,
    abstract: str,
    keywords: List[str] = None,
    prefer_open_access: bool = False,
) -> Tuple[List[Journal], str]:
    """
    Search for journals based on article title and abstract.

    Uses HYBRID approach: Keywords + Topics.
    Now uses OpenAlex subfield/field for discipline instead of static keywords.

    Args:
        title: Article title.
        abstract: Article abstract.
        keywords: Optional additional keywords.
        prefer_open_access: Prioritize OA journals.

    Returns:
        Tuple of (journals list, detected subfield from OpenAlex).
    """
    core_journals = load_core_journals()
    combined_text = f"{title} {abstract}"
    search_terms = extract_search_terms(combined_text, keywords or [])

    # === HYBRID APPROACH ===

    # 1. TOPIC-BASED SEARCH (ML-based approach) - Do this FIRST to get subfield
    topic_ids, subfield, field = get_topics_from_similar_works(combined_text)
    topic_journals = find_journals_by_topics(topic_ids)

    # Use OpenAlex subfield as discipline (e.g., "Endocrinology, Diabetes and Metabolism")
    # Fall back to field if no subfield, or static detection as last resort
    if subfield:
        discipline = subfield
    elif field:
        discipline = field
    else:
        discipline = detect_discipline(combined_text)

    # 2. KEYWORD-BASED SEARCH
    keyword_journals_list = search_journals_by_keywords(
        search_terms,
        prefer_open_access=prefer_open_access,
        discipline=discipline,
        core_journals=core_journals,
    )
    keyword_journals: Dict[str, Journal] = {j.id: j for j in keyword_journals_list}

    # 3. MERGE RESULTS - journals in both lists get boosted
    merged_journals = merge_journal_results(keyword_journals, topic_journals)

    # 4. INJECT KEY JOURNALS - DISABLED
    # Was forcing generic "important" journals (NEJM, Lancet) into results
    # even when not relevant to the specific research topic
    # all_journals: Dict[str, Journal] = {j.id: j for j in merged_journals}
    # all_journals = inject_key_journals(
    #     discipline, all_journals, core_journals, search_terms
    # )
    # merged_journals = list(all_journals.values())

    # If no results from hybrid, try broader search
    if not merged_journals:
        merged_journals = search_journals_by_keywords(
            search_terms[:3],
            prefer_open_access=prefer_open_access,
            discipline="general",
            core_journals=core_journals,
        )

    # Categorize journals
    categorized = categorize_journals(merged_journals)

    # Identify sources for score recalculation
    keyword_ids = set(keyword_journals.keys())
    topic_id_set = set(topic_journals.keys())

    # Recalculate scores with Weighted Scoring
    for journal in categorized:
        is_keyword = journal.id in keyword_ids
        is_topic = journal.id in topic_id_set

        # Preserve existing merge bonus
        merge_bonus = journal.relevance_score if journal.relevance_score else 0

        journal.relevance_score = calculate_relevance_score(
            journal=journal,
            discipline=discipline,
            is_topic_match=is_topic,
            is_keyword_match=is_keyword,
            search_terms=search_terms,
            core_journals=core_journals,
        ) + (merge_bonus * 10)  # Amplify merge bonus

    # Final sort: prioritize by Weighted relevance_score
    categorized.sort(
        key=lambda j: (
            j.is_oa if prefer_open_access else False,
            j.relevance_score,
            j.metrics.h_index or 0,
        ),
        reverse=True,
    )

    # Fallback: ONLY add more if <3 results (reduced from 5)
    # This prevents irrelevant journals from appearing
    if len(categorized) < 3:
        fallback_journals = search_journals_by_keywords(
            search_terms[:2],
            prefer_open_access=prefer_open_access,
            discipline="general",
            core_journals=core_journals,
        )
        existing_ids = {j.id for j in categorized}
        for j in fallback_journals:
            if j.id not in existing_ids and len(categorized) < 7:
                j.match_reason = "Broader search result"
                categorized.append(j)

    return categorized[:15], discipline
