"""
Journal Relevance Scoring

Weighted scoring algorithm for ranking journals.
Includes enhanced scoring with multi-discipline and article type awareness.
"""
from typing import List, Set, Tuple, Dict, Optional
from dataclasses import dataclass, field

from app.models.journal import Journal
from .constants import RELEVANT_TOPIC_KEYWORDS
from .utils import normalize_journal_name


# =============================================================================
# Enhanced Scoring Context and Scorer
# =============================================================================

@dataclass
class ScoringContext:
    """
    Context for enhanced scoring with multi-discipline and article type info.
    """
    detected_disciplines: List[Dict] = field(default_factory=list)
    article_type: Optional[Dict] = None
    keywords: List[str] = field(default_factory=list)
    prefer_open_access: bool = False


class EnhancedJournalScorer:
    """
    Enhanced scoring with multi-discipline and article type awareness.

    New scoring factors:
    1. Multi-discipline match bonus
    2. Cross-discipline coverage bonus
    3. Article type fit bonus
    4. Topic relevance validation
    """

    # Scoring weights
    WEIGHTS = {
        # Existing base weights
        "topic_match": 20,
        "keyword_match": 10,
        "journal_name_match": 50,
        "h_index_factor": 0.05,
        "citation_rate_factor": 1.5,

        # NEW: Multi-discipline scoring
        "primary_discipline_match": 30,
        "secondary_discipline_match": 15,
        "cross_discipline_coverage": 35,  # Journal covers multiple detected disciplines

        # NEW: Article type scoring
        "article_type_fit": 20,

        # NEW: Topic relevance
        "topic_relevance_penalty": -30,  # Penalty for irrelevant topics
    }

    def score_journal(
        self,
        journal: Journal,
        context: ScoringContext,
        is_topic_match: bool = False,
        is_keyword_match: bool = False,
        search_terms: Optional[List[str]] = None,
    ) -> float:
        """
        Calculate enhanced relevance score for a journal.

        Args:
            journal: Journal to score.
            context: Scoring context with detected disciplines and article type.
            is_topic_match: Found via topic search.
            is_keyword_match: Found via keyword search.
            search_terms: Original search terms.

        Returns:
            Relevance score (will be normalized later).
        """
        score = 0.0
        journal_name_lower = journal.name.lower()
        search_terms = search_terms or context.keywords

        # 1. Base scoring factors (existing)
        if is_topic_match:
            score += self.WEIGHTS["topic_match"]

        if is_keyword_match:
            score += self.WEIGHTS["keyword_match"]

        # Exact title match
        for term in search_terms:
            if len(term) > 4 and term.lower() in journal_name_lower:
                score += self.WEIGHTS["journal_name_match"]
                break

        # H-index quality
        h_index = journal.metrics.h_index or 0
        score += h_index * self.WEIGHTS["h_index_factor"]

        # Citation rate
        citation_rate = journal.metrics.two_yr_mean_citedness or 0
        score += citation_rate * self.WEIGHTS["citation_rate_factor"]

        # 2. NEW: Multi-discipline matching
        score += self._score_discipline_match(journal, context.detected_disciplines)

        # 3. NEW: Cross-discipline coverage
        score += self._score_cross_discipline(journal, context.detected_disciplines)

        # 4. NEW: Article type fit
        score += self._score_article_type_fit(journal, context.article_type)

        # 5. NEW: Topic relevance validation
        score += self._validate_topic_relevance(journal, context)

        # 6. Open access preference
        if context.prefer_open_access and journal.is_oa:
            score += 15

        return max(score, 0)  # Don't go negative

    def _score_discipline_match(
        self,
        journal: Journal,
        disciplines: List[Dict]
    ) -> float:
        """Score based on matching detected disciplines."""
        score = 0.0
        journal_subfields = self._get_journal_subfields(journal)
        journal_name_lower = journal.name.lower()

        for i, disc in enumerate(disciplines):
            subfield = disc.get("openalex_subfield_id", "")
            name = disc.get("name", "").lower()

            # Check if journal publishes in this subfield
            subfield_match = subfield and subfield.lower() in journal_subfields

            # Check if discipline name appears in journal name/topics
            name_match = name and (
                name in journal_name_lower or
                any(name in t.lower() for t in journal.topics)
            )

            if subfield_match or name_match:
                if i == 0:  # Primary discipline
                    score += self.WEIGHTS["primary_discipline_match"]
                else:  # Secondary disciplines
                    score += self.WEIGHTS["secondary_discipline_match"]

        return score

    def _score_cross_discipline(
        self,
        journal: Journal,
        disciplines: List[Dict]
    ) -> float:
        """
        Bonus for journals that cover multiple detected disciplines.

        A journal that publishes on BOTH urology AND rheumatology
        is more relevant for an OAB + fibromyalgia paper.
        """
        if len(disciplines) < 2:
            return 0.0

        journal_subfields = self._get_journal_subfields(journal)
        journal_name_lower = journal.name.lower()

        overlap_count = 0
        for disc in disciplines[:3]:  # Check top 3 disciplines
            subfield = disc.get("openalex_subfield_id", "")
            name = disc.get("name", "").lower()
            evidence = disc.get("evidence", [])

            # Check for subfield match
            if subfield and subfield.lower() in journal_subfields:
                overlap_count += 1
                continue

            # Check for evidence keywords in journal topics
            for kw in evidence[:3]:  # Top 3 evidence keywords
                if kw.lower() in journal_name_lower:
                    overlap_count += 1
                    break
                for topic in journal.topics:
                    if kw.lower() in topic.lower():
                        overlap_count += 1
                        break

        # Give full bonus if journal covers 2+ disciplines
        if overlap_count >= 2:
            return self.WEIGHTS["cross_discipline_coverage"]
        elif overlap_count == 1:
            return self.WEIGHTS["cross_discipline_coverage"] * 0.3

        return 0.0

    def _score_article_type_fit(
        self,
        journal: Journal,
        article_type: Optional[Dict]
    ) -> float:
        """Score based on article type fit with journal profile."""
        if not article_type:
            return 0.0

        type_id = article_type.get("type", "")
        journal_name_lower = journal.name.lower()

        # Check for review-focused journals
        if type_id in ["systematic_review", "systematic_review_meta_analysis", "meta_analysis"]:
            review_terms = ["review", "systematic", "evidence", "synthesis"]
            if any(term in journal_name_lower for term in review_terms):
                return self.WEIGHTS["article_type_fit"]
            # High-impact journals also good for major reviews
            if (journal.metrics.h_index or 0) > 100:
                return self.WEIGHTS["article_type_fit"] * 0.5

        # Check for case report journals
        if type_id == "case_report":
            if "case" in journal_name_lower:
                return self.WEIGHTS["article_type_fit"]

        # Check for RCT - prefer clinical/trials journals
        if type_id == "randomized_controlled_trial":
            trial_terms = ["clinical", "trial", "controlled"]
            if any(term in journal_name_lower for term in trial_terms):
                return self.WEIGHTS["article_type_fit"] * 0.5

        return 0.0

    def _validate_topic_relevance(
        self,
        journal: Journal,
        context: ScoringContext
    ) -> float:
        """
        Validate that journal topics are actually relevant.
        Apply penalty for clearly irrelevant topics.
        """
        if not journal.topics:
            return 0.0

        # Build expected keywords from context
        expected_keywords = set()
        for disc in context.detected_disciplines:
            evidence = disc.get("evidence", [])
            expected_keywords.update(e.lower() for e in evidence)
        expected_keywords.update(kw.lower() for kw in context.keywords)

        if not expected_keywords:
            return 0.0

        # Check top 5 journal topics for relevance
        topic_names = [t.lower() for t in journal.topics[:5]]

        relevant_count = 0
        for topic in topic_names:
            for kw in expected_keywords:
                if kw in topic or topic in kw:
                    relevant_count += 1
                    break

        # If majority of top topics are irrelevant, apply penalty
        if len(topic_names) > 0:
            relevance_ratio = relevant_count / len(topic_names)
            if relevance_ratio < 0.2:
                return self.WEIGHTS["topic_relevance_penalty"]

        return 0.0

    def _get_journal_subfields(self, journal: Journal) -> set:
        """Extract subfield names from journal topics (lowercase)."""
        subfields = set()
        for topic in journal.topics:
            # Topics might contain subfield info
            subfields.add(topic.lower())
        return subfields


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
