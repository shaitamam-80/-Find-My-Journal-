"""
Journal Relevance Scoring

Weighted scoring algorithm for ranking journals.
"""
from typing import List, Set

from app.models.journal import Journal
from .constants import RELEVANT_TOPIC_KEYWORDS
from .utils import normalize_journal_name


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
    6. Discipline Boost: +15
    7. Core Journal Safety Net: +100

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

    # 6. Discipline Boost (+15)
    # Check if journal topics match the discipline
    relevant_keywords = RELEVANT_TOPIC_KEYWORDS.get(discipline, [])
    is_discipline_relevant = False

    # Check journal name
    if any(k in journal_name_lower for k in relevant_keywords):
        is_discipline_relevant = True

    # Check topics
    if not is_discipline_relevant:
        for topic in journal.topics:
            if any(k in topic.lower() for k in relevant_keywords):
                is_discipline_relevant = True
                break

    if is_discipline_relevant:
        score += 15.0

    # 7. Core Journal Safety Net - DISABLED
    # Was giving +100 to generic prestigious journals (NEJM, Lancet)
    # causing them to rank above topic-relevant journals
    # journal_name_norm = normalize_journal_name(journal.name)
    # if journal_name_norm in core_journals:
    #     score += 100.0

    return score
