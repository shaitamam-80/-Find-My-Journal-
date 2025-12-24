"""
Journal Relevance Scoring

Weighted scoring algorithm for ranking journals.
"""
from typing import List, Set, Tuple

from app.models.journal import Journal
from .constants import RELEVANT_TOPIC_KEYWORDS
from .utils import normalize_journal_name


def generate_match_details(
    journal: Journal,
    discipline: str,
    is_topic_match: bool,
    is_keyword_match: bool,
    search_terms: List[str],
) -> Tuple[List[str], List[str]]:
    """
    Generate human-readable match details for a journal.

    This explains WHY this journal is a good fit (Story 1.1).

    Args:
        journal: Journal to analyze.
        discipline: Detected discipline/subfield.
        is_topic_match: Found via topic search.
        is_keyword_match: Found via keyword search.
        search_terms: Original search terms.

    Returns:
        Tuple of (match_details list, matched_topics list).
    """
    details: List[str] = []
    matched_topics: List[str] = []
    journal_name_lower = journal.name.lower()

    # 1. Topic/Keyword match explanation
    if is_topic_match and is_keyword_match:
        details.append("Strong match: Found via both topic analysis and keyword search")
    elif is_topic_match:
        details.append("Topic match: Similar papers are published here")
    elif is_keyword_match:
        details.append("Keyword match: Journal covers your research terms")

    # 2. Name match with search terms
    matching_terms = [
        term for term in search_terms
        if len(term) > 4 and term.lower() in journal_name_lower
    ]
    if matching_terms:
        terms_str = ", ".join(matching_terms[:3])
        details.append(f"Direct relevance: Journal name includes '{terms_str}'")

    # 3. Discipline/subfield relevance
    discipline_lower = discipline.lower() if discipline else ""
    discipline_words = [
        w.strip() for w in discipline_lower.replace(",", " ").split()
        if len(w.strip()) > 3
    ]

    # Check journal name for discipline words
    for word in discipline_words:
        if word in journal_name_lower:
            details.append(f"Specialized in {discipline}")
            break

    # 4. Quality indicators
    h_index = journal.metrics.h_index or 0
    if h_index >= 200:
        details.append(f"High-impact journal (H-index: {h_index})")
    elif h_index >= 50:
        details.append(f"Established journal (H-index: {h_index})")

    citation_rate = journal.metrics.two_yr_mean_citedness or 0
    if citation_rate >= 10:
        details.append(f"High citation rate ({citation_rate:.1f} avg citations)")

    # 5. Open Access
    if journal.is_oa:
        details.append("Open Access: Free to read and share")
    if journal.is_in_doaj:
        details.append("DOAJ verified: Quality open access journal")

    # 6. Find matching topics
    journal_topics_lower = [t.lower() for t in journal.topics]
    for term in search_terms:
        term_lower = term.lower()
        for topic in journal.topics:
            if term_lower in topic.lower():
                if topic not in matched_topics:
                    matched_topics.append(topic)

    # Also check discipline words against topics
    for word in discipline_words:
        for topic in journal.topics:
            if word in topic.lower():
                if topic not in matched_topics:
                    matched_topics.append(topic)

    # Limit to top 5 matched topics
    matched_topics = matched_topics[:5]

    # Ensure at least one detail if nothing found
    if not details:
        details.append("General match based on research area")

    return details, matched_topics


def calculate_relevance_score(
    journal: Journal,
    discipline: str,
    is_topic_match: bool,
    is_keyword_match: bool,
    search_terms: List[str],
    core_journals: Set[str],
) -> float:
    """
    Calculate weighted relevance score.

    Scoring breakdown:
    1. Base Score: 0.0
    2. Topic Match: +20
    3. Keyword Match: +10
    4. Exact Title Match: +50 (if journal name matches search terms)
    5. Quality Boost: H-index * 0.05
    5b. Citation Rate Boost: 2yr_mean_citedness * 1.5
    6. Discipline Boost: +15 to +25
    7. Core Journal Safety Net: +100 (DISABLED)

    Args:
        journal: Journal to score.
        discipline: Detected discipline.
        is_topic_match: Found via topic search.
        is_keyword_match: Found via keyword search.
        search_terms: Original search terms.
        core_journals: Set of core journal names (normalized).

    Returns:
        Relevance score (higher = more relevant).
    """
    score = 0.0
    journal_name_lower = journal.name.lower()

    # 2. Topic Match (+20)
    if is_topic_match:
        score += 20.0

    # 3. Keyword Match (+10)
    if is_keyword_match:
        score += 10.0

    # 4. Exact Title Match (+50)
    # Check if any strong search term is part of the journal name
    # Only check terms length > 4 to avoid generic matches
    for term in search_terms:
        if len(term) > 4 and term.lower() in journal_name_lower:
            score += 50.0
            break

    # 5. Quality Boost (H-index * 0.05)
    # Example: Nature (H~1300) -> +65 points
    h_index = journal.metrics.h_index or 0
    score += h_index * 0.05

    # 5b. Citation Rate Boost (2yr_mean_citedness * 1.5)
    # Similar to Impact Factor - higher means more citations per paper
    # Example: Nature (citedness ~45) -> +67.5 points
    citation_rate = journal.metrics.two_yr_mean_citedness or 0
    score += citation_rate * 1.5

    # 6. Discipline/Subfield Boost (+15 to +25)
    # Now discipline can be an OpenAlex subfield like "Endocrinology, Diabetes and Metabolism"
    # We check if the journal name or topics contain words from the subfield
    discipline_lower = discipline.lower() if discipline else ""
    is_discipline_relevant = False

    # Extract key words from the discipline/subfield (split on commas and spaces)
    discipline_words = [
        w.strip() for w in discipline_lower.replace(",", " ").split()
        if len(w.strip()) > 3
    ]

    # Check if journal name contains discipline words
    for word in discipline_words:
        if word in journal_name_lower:
            is_discipline_relevant = True
            score += 25.0  # Higher boost for name match
            break

    # Also check journal topics against discipline words
    if not is_discipline_relevant:
        for topic in journal.topics:
            topic_lower = topic.lower()
            for word in discipline_words:
                if word in topic_lower:
                    is_discipline_relevant = True
                    score += 15.0  # Standard boost for topic match
                    break
            if is_discipline_relevant:
                break

    # Fallback: use static keywords for legacy disciplines
    if not is_discipline_relevant and discipline in RELEVANT_TOPIC_KEYWORDS:
        relevant_keywords = RELEVANT_TOPIC_KEYWORDS.get(discipline, [])
        if any(k in journal_name_lower for k in relevant_keywords):
            is_discipline_relevant = True
            score += 15.0
        else:
            for topic in journal.topics:
                if any(k in topic.lower() for k in relevant_keywords):
                    is_discipline_relevant = True
                    score += 15.0
                    break

    # 7. Core Journal Safety Net - DISABLED
    # Was giving +100 to generic prestigious journals (NEJM, Lancet)
    # causing them to rank above topic-relevant journals
    # journal_name_norm = normalize_journal_name(journal.name)
    # if journal_name_norm in core_journals:
    #     score += 100.0

    return score
