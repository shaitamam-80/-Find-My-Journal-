"""
Journal Search Operations

Hybrid search combining keywords and topic matching.
Enhanced with multi-discipline detection, article type awareness, and topic validation.

Phase 4: Now uses SmartAnalyzer for orchestrated paper analysis.
"""
import logging
from collections import Counter
from typing import Dict, List, Optional, Tuple, Set

from app.models.journal import Journal
from .client import get_client
from .config import get_min_journal_works
from .constants import load_core_journals
from .utils import extract_search_terms
from .scoring import (
    calculate_relevance_score,
    generate_match_details,
    EnhancedJournalScorer,
    ScoringContext,
)
from .journals import convert_to_journal, categorize_journals, merge_journal_results

# Import analysis modules - using lazy imports for SmartAnalyzer to avoid circular imports
from app.services.analysis import (
    ArticleTypeDetector,
    TopicRelevanceValidator,
)

# TYPE_CHECKING for type hints without runtime import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.services.analysis import get_smart_analyzer, AnalysisResult

logger = logging.getLogger(__name__)


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


def get_topics_from_similar_works(search_query: str) -> Tuple[List[str], str, str, Optional[int], float]:
    """
    Extract Topic IDs and subfield/field from similar papers.

    Uses the Topics API to get both topic IDs for journal search
    AND the subfield/field hierarchy for discipline detection.

    Args:
        search_query: Combined title and abstract text.

    Returns:
        Tuple of:
        - Top 5 most frequent topic IDs
        - Most common subfield name (e.g., "Endocrinology, Diabetes and Metabolism")
        - Most common field name (e.g., "Medicine")
        - Most common subfield ID for accurate filtering (e.g., 2713)
        - Confidence score (0-1) based on consensus among works
    """
    client = get_client()
    topic_ids: Counter = Counter()
    subfield_scores: Counter = Counter()  # Track by ID for accuracy
    subfield_names: Dict[int, str] = {}   # Map ID -> display name
    fields: Counter = Counter()
    total_topic_score = 0.0

    works = client.search_works(search_query, per_page=50)
    works_count = len(works)

    for work in works:
        topics = work.get("topics") or []
        for topic in topics:
            topic_id = topic.get("id")
            if topic_id:
                # Weight by score if available
                score = topic.get("score", 1.0)
                topic_ids[topic_id] += score
                total_topic_score += score

                # Extract subfield and field from OpenAlex hierarchy
                subfield = topic.get("subfield", {})
                field = topic.get("field", {})

                # Track subfield by ID (more accurate than name)
                if subfield:
                    sf_id = subfield.get("id")
                    sf_name = subfield.get("display_name")
                    if sf_id and sf_name:
                        subfield_scores[sf_id] += score
                        subfield_names[sf_id] = sf_name

                if field and field.get("display_name"):
                    fields[field["display_name"]] += score

    top_topic_ids = [tid for tid, _ in topic_ids.most_common(5)]

    # Get top subfield by ID, then lookup name
    top_subfield_id: Optional[int] = None
    top_subfield = ""
    top_subfield_score = 0.0
    if subfield_scores:
        top_subfield_id, top_subfield_score = subfield_scores.most_common(1)[0]
        top_subfield = subfield_names.get(top_subfield_id, "")

    top_field = fields.most_common(1)[0][0] if fields else ""

    # Calculate confidence score (Story 2.1)
    # Based on: (1) how dominant the top subfield is, (2) number of works found
    confidence = 0.0
    if works_count > 0 and total_topic_score > 0:
        # Dominance: what fraction of total score goes to top subfield
        dominance = top_subfield_score / total_topic_score if total_topic_score > 0 else 0
        # Coverage: did we find enough works? (50 is max)
        coverage = min(works_count / 30, 1.0)  # 30+ works = full coverage
        # Combine: dominance weighted more heavily
        confidence = (dominance * 0.7) + (coverage * 0.3)
        confidence = min(max(confidence, 0.0), 1.0)  # Clamp to 0-1

    return top_topic_ids, top_subfield, top_field, top_subfield_id, confidence


def get_topic_ids_from_similar_works(search_query: str) -> List[str]:
    """
    Extract Topic IDs from similar papers (legacy wrapper).

    Kept for backward compatibility.
    """
    topic_ids, _, _, _, _ = get_topics_from_similar_works(search_query)
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


def find_journals_by_subfield(
    subfield: str,
    search_terms: List[str] = None,
) -> Dict[str, dict]:
    """
    Find journals by searching for the subfield name directly.

    This catches specialized journals that may not appear in topic search
    but have the subfield name in their title (e.g., "Infancy" journal).

    Args:
        subfield: OpenAlex subfield name (e.g., "Developmental and Educational Psychology").
        search_terms: Optional search terms to also search for specialized journals.

    Returns:
        Dict of source_id -> {reason}.
    """
    if not subfield:
        return {}

    client = get_client()
    journals: Dict[str, dict] = {}

    # Search for journals by subfield name
    sources = client.search_sources(subfield, per_page=20)

    for source in sources:
        source_id = source.get("id", "")
        if source_id:
            journals[source_id] = {
                "source": source,
                "reason": f"Specialized journal for {subfield}",
            }

    # Also search for key terms from the subfield
    # e.g., "Developmental and Educational Psychology" -> search "developmental", "psychology"
    subfield_words = [
        w.strip() for w in subfield.lower().replace(",", " ").split()
        if len(w.strip()) > 5  # Only significant words
    ]

    for word in subfield_words[:2]:  # Limit to 2 key terms
        sources = client.search_sources(word, per_page=10)
        for source in sources:
            source_id = source.get("id", "")
            if source_id and source_id not in journals:
                journals[source_id] = {
                    "source": source,
                    "reason": f"Related to {subfield}",
                }

    # Search for specialized journals based on key search terms
    # This catches journals like "Infancy" for infant-related searches
    if search_terms:
        specialized_terms = [
            t for t in search_terms
            if t.lower() in ["infancy", "infant", "toddler", "child", "developmental",
                            "endocrine", "hormone", "diabetes", "metabolism"]
        ]
        for term in specialized_terms[:3]:
            sources = client.search_sources(term, per_page=10)
            for source in sources:
                source_id = source.get("id", "")
                if source_id and source_id not in journals:
                    journals[source_id] = {
                        "source": source,
                        "reason": f"Specialized journal matching '{term}'",
                    }

    return journals


def find_journals_by_subfield_id(subfield_id: Optional[int]) -> Dict[str, dict]:
    """
    Find journals by subfield ID using OpenAlex structured filtering.

    This is more accurate than text-based search because it uses
    the OpenAlex topic hierarchy directly.

    Args:
        subfield_id: OpenAlex subfield ID (e.g., 2713 for Epidemiology).

    Returns:
        Dict of source_id -> {count, reason}.
    """
    if not subfield_id:
        return {}

    client = get_client()
    journals: Dict[str, dict] = {}

    # Use ID-based filter for accurate results
    results = client.find_sources_by_subfield_id(subfield_id)

    for entry in results:
        source_id = entry.get("key")
        count = entry.get("count", 0)
        if source_id and count > 0:
            journals[source_id] = {
                "count": count,
                "reason": "Active in this research subfield",
            }

    return journals


def is_journal_relevant_to_subfield(
    journal: Journal, subfield: str, field: str
) -> bool:
    """
    Check if a journal is relevant to the detected subfield/field.

    Uses journal topics to determine relevance.
    Journals with no topic overlap are filtered out.

    Args:
        journal: Journal to check.
        subfield: Detected OpenAlex subfield.
        field: Detected OpenAlex field.

    Returns:
        True if journal is relevant, False otherwise.
    """
    if not subfield and not field:
        return True  # No filter if no subfield detected

    journal_name_lower = journal.name.lower()
    journal_topics_lower = [t.lower() for t in journal.topics]

    # Extract keywords from subfield/field
    subfield_words = set()
    if subfield:
        subfield_words.update(
            w.strip() for w in subfield.lower().replace(",", " ").split()
            if len(w.strip()) > 3
        )
    if field:
        subfield_words.update(
            w.strip() for w in field.lower().replace(",", " ").split()
            if len(w.strip()) > 3
        )

    # Check if journal name contains any subfield/field words
    for word in subfield_words:
        if word in journal_name_lower:
            return True

    # Check if journal topics contain any subfield/field words
    for topic in journal_topics_lower:
        for word in subfield_words:
            if word in topic:
                return True

    # Also check for common related terms in psychology/development
    related_terms = {
        "developmental": ["child", "infant", "adolescent", "pediatric", "youth"],
        "psychology": ["psychological", "cogniti", "behavior", "mental", "emotion"],
        "educational": ["education", "learning", "school", "teaching"],
    }

    for base_word, related in related_terms.items():
        if base_word in subfield_words:
            for rel_term in related:
                if rel_term in journal_name_lower:
                    return True
                for topic in journal_topics_lower:
                    if rel_term in topic:
                        return True

    return False


def is_journal_relevant_to_any_discipline(
    journal: Journal, detected_disciplines: List[dict]
) -> bool:
    """
    Check if a journal is relevant to ANY of the detected disciplines.

    This is important for multi-discipline papers where secondary disciplines
    may have relevant journals that don't match the primary discipline.

    Args:
        journal: Journal to check.
        detected_disciplines: List of detected discipline dicts with subfield/field info.

    Returns:
        True if journal is relevant to any discipline, False otherwise.
    """
    if not detected_disciplines:
        return True  # No filter if no disciplines detected

    # Check against each detected discipline using OpenAlex subfield/field directly
    for disc in detected_disciplines:
        # Get subfield and field from the discipline dict (from OpenAlex)
        subfield = disc.get("name", "")  # OpenAlex subfield name
        field = disc.get("field", "")    # OpenAlex field name

        # If journal is relevant to this discipline, keep it
        if is_journal_relevant_to_subfield(journal, subfield, field):
            return True

    return False


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


def search_journals_by_text(
    title: str,
    abstract: str,
    keywords: List[str] = None,
    prefer_open_access: bool = False,
    enable_llm: bool = False,
) -> Tuple[List[Journal], str, str, float, List[Dict], Optional[Dict], Optional[Dict]]:
    """
    Search for journals based on article title and abstract.

    Uses HYBRID approach: Keywords + Topics.
    Enhanced with SmartAnalyzer for orchestrated paper analysis.

    Args:
        title: Article title.
        abstract: Article abstract.
        keywords: Optional additional keywords.
        prefer_open_access: Prioritize OA journals.
        enable_llm: Enable LLM enrichment for complex cases.

    Returns:
        Tuple of:
        - journals list
        - detected subfield from OpenAlex (primary discipline)
        - parent field name
        - confidence score (0-1) for discipline detection
        - detected_disciplines: List of all detected disciplines with confidence
        - article_type: Detected article type info
        - analysis_metadata: SmartAnalyzer metadata (NEW)
    """
    core_journals = load_core_journals()

    # === SMART ANALYSIS (Phase 4) ===
    # Lazy import to avoid circular imports
    from app.services.analysis import get_smart_analyzer, AnalysisResult

    # Use SmartAnalyzer for orchestrated paper analysis
    smart_analyzer = get_smart_analyzer(enable_llm=enable_llm)
    analysis_result: AnalysisResult = smart_analyzer.analyze(
        title=title,
        abstract=abstract,
        user_keywords=keywords,
    )

    # Extract search terms from analysis result
    search_terms = analysis_result.search_terms or extract_search_terms(
        f"{title} {abstract}", keywords or []
    )

    # Extract discipline info from SmartAnalyzer
    subfield = analysis_result.primary_discipline or ""
    field = analysis_result.primary_field or ""
    confidence = analysis_result.discipline_confidence

    # Get topic IDs for journal search
    topic_ids = analysis_result.topic_ids

    # 1. TOPIC-BASED SEARCH using SmartAnalyzer's topic IDs
    topic_journals = find_journals_by_topics(topic_ids)

    # Get subfield_id from disciplines if available
    subfield_id: Optional[int] = None
    if analysis_result.disciplines:
        primary = analysis_result.disciplines[0]
        # Extract numeric ID from subfield_id string (e.g., "https://openalex.org/subfields/1234" -> 1234)
        if primary.subfield_id and primary.subfield_id != "llm-detected":
            try:
                subfield_id = int(primary.subfield_id.split("/")[-1])
            except (ValueError, AttributeError):
                pass

    # 2. MULTI-DISCIPLINE DETECTION from SmartAnalyzer
    detected_disciplines_dicts: List[Dict] = []
    for disc in analysis_result.disciplines:
        detected_disciplines_dicts.append({
            "name": disc.subfield_name,
            "confidence": disc.confidence,
            "field": disc.field_name,
            "domain": disc.domain_name or None,
            "numeric_id": None,  # Will be extracted if needed
            "openalex_subfield_id": disc.subfield_id if disc.subfield_id != "llm-detected" else None,
            "source": "smart_analyzer",
        })

    # Log detection results
    if detected_disciplines_dicts:
        disc_summary = [(d["name"], f"{d['confidence']:.0%}") for d in detected_disciplines_dicts[:5]]
        logger.info(f"Detected disciplines (smart_analyzer): {disc_summary}")
    else:
        logger.warning("No disciplines detected from SmartAnalyzer")

    # 3. ARTICLE TYPE DETECTION
    article_type_detector = ArticleTypeDetector()
    detected_article_type = article_type_detector.detect(abstract, title)
    article_type_dict = article_type_detector.to_dict(detected_article_type)

    logger.info(f"Detected article type: {detected_article_type.display_name} ({detected_article_type.confidence:.0%})")

    # Use OpenAlex subfield as discipline (for backward compatibility)
    if subfield:
        discipline = subfield
    elif field:
        discipline = field
    elif detected_disciplines_dicts:
        discipline = detected_disciplines_dicts[0].get("name", "")
    else:
        discipline = "general"  # Fallback when OpenAlex detection fails

    # 4. SUBFIELD-BASED SEARCH - Find specialized journals
    # Search for ALL detected disciplines (not just primary)
    if subfield_id:
        subfield_journals = find_journals_by_subfield_id(subfield_id)
    else:
        subfield_journals = find_journals_by_subfield(subfield, search_terms)

    # Also search for secondary disciplines using numeric IDs for accurate filtering
    for disc in detected_disciplines_dicts[1:5]:  # Top 4 secondary disciplines (expand coverage)
        # Use numeric ID if available (more accurate), fall back to name search
        numeric_id = disc.get("numeric_id") or disc.get("openalex_subfield_id")
        subfield_name = disc.get("name", "")

        if numeric_id and isinstance(numeric_id, int):
            secondary_journals = find_journals_by_subfield_id(numeric_id)
        elif subfield_name:
            secondary_journals = find_journals_by_subfield(subfield_name, search_terms)
        else:
            continue

        for source_id, data in secondary_journals.items():
            if source_id not in subfield_journals:
                subfield_journals[source_id] = data

    # Merge subfield journals into topic_journals
    for source_id, data in subfield_journals.items():
        if source_id not in topic_journals:
            topic_journals[source_id] = data

    # 5. KEYWORD-BASED SEARCH
    keyword_journals_list = search_journals_by_keywords(
        search_terms,
        prefer_open_access=prefer_open_access,
        discipline=discipline,
        core_journals=core_journals,
    )
    keyword_journals: Dict[str, Journal] = {j.id: j for j in keyword_journals_list}

    # 6. MERGE RESULTS - journals in both lists get boosted
    merged_journals = merge_journal_results(keyword_journals, topic_journals)

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

    # 7. FILTER IRRELEVANT JOURNALS
    # CHANGED: Check relevance to ANY detected discipline (not just primary)
    # This allows secondary disciplines like Gynecology to contribute journals
    if detected_disciplines_dicts:
        filtered = [
            j for j in categorized
            if is_journal_relevant_to_any_discipline(j, detected_disciplines_dicts)
        ]
        if len(filtered) >= 3:
            categorized = filtered
    elif subfield or field:
        # Fallback to single discipline check if no multi-discipline detected
        filtered = [
            j for j in categorized
            if is_journal_relevant_to_subfield(j, subfield, field)
        ]
        if len(filtered) >= 3:
            categorized = filtered

    # === ENHANCED SCORING ===

    # Create scoring context with multi-discipline and article type info
    scoring_context = ScoringContext(
        detected_disciplines=detected_disciplines_dicts,
        article_type=article_type_dict,
        keywords=keywords or [],
        prefer_open_access=prefer_open_access,
    )

    # Initialize enhanced scorer
    enhanced_scorer = EnhancedJournalScorer()

    # Identify sources for score recalculation
    keyword_ids = set(keyword_journals.keys())
    topic_id_set = set(topic_journals.keys())

    # Recalculate scores with Enhanced Scoring
    for journal in categorized:
        is_keyword = journal.id in keyword_ids
        is_topic = journal.id in topic_id_set

        # Preserve existing merge bonus
        merge_bonus = journal.relevance_score if journal.relevance_score else 0

        # Use enhanced scorer with multi-discipline awareness
        journal.relevance_score = enhanced_scorer.score_journal(
            journal=journal,
            context=scoring_context,
            is_topic_match=is_topic,
            is_keyword_match=is_keyword,
            search_terms=search_terms,
        ) + (merge_bonus * 10)  # Amplify merge bonus

        # Generate match details (Story 1.1 - Why it's a good fit)
        details, matched = generate_match_details(
            journal=journal,
            discipline=discipline,
            is_topic_match=is_topic,
            is_keyword_match=is_keyword,
            search_terms=search_terms,
        )
        journal.match_details = details
        journal.matched_topics = matched

    # === TOPIC VALIDATION ===

    # Add topic validation warnings (NEW)
    topic_validator = TopicRelevanceValidator()
    for journal in categorized:
        # Convert journal to dict format for validator
        journal_dict = {
            "topics": [{"display_name": t} for t in journal.topics],
        }
        validation = topic_validator.validate_journal_topics(
            journal_dict,
            detected_disciplines_dicts,
            keywords or [],
        )
        # Store validation warning if present
        if validation.get("warning"):
            if not journal.match_details:
                journal.match_details = []
            journal.match_details.append(f"Note: {validation['warning']}")

    # Final sort: prioritize by Weighted relevance_score
    categorized.sort(
        key=lambda j: (
            j.is_oa if prefer_open_access else False,
            j.relevance_score,
            j.metrics.h_index or 0,
        ),
        reverse=True,
    )

    # Normalize relevance_score to 0-1 range for frontend display
    if categorized:
        max_score = max(j.relevance_score for j in categorized)
        if max_score > 0:
            for journal in categorized:
                journal.relevance_score = journal.relevance_score / max_score

    # Fallback: ONLY add more if <3 results
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

    # Build analysis metadata from SmartAnalyzer result
    analysis_metadata: Optional[Dict] = None
    if analysis_result:
        # Extract confidence factors by name from the list
        factors_dict = {}
        if analysis_result.confidence and analysis_result.confidence.factors:
            for factor in analysis_result.confidence.factors:
                factors_dict[factor.name] = factor.score

        analysis_metadata = {
            "confidence_score": analysis_result.confidence.overall if analysis_result.confidence else 0,
            "confidence_factors": {
                "topics": factors_dict.get("topics_found", 0),
                "works": factors_dict.get("works_count", 0),
                "keywords": factors_dict.get("keywords_quality", 0),
                "discipline": factors_dict.get("discipline_clarity", 0),
                "diversity": factors_dict.get("keyword_diversity", 0),
            },
            "works_analyzed": analysis_result.works_analyzed,
            "topics_found": analysis_result.topics_found,
            "keywords_extracted": [k.keyword for k in analysis_result.keywords[:10]],
            "discipline_hints": analysis_result.discipline_hints,
            "methodology_hints": analysis_result.methodology_hints,
            "needs_llm_enrichment": analysis_result.needs_llm_enrichment,
            "enrichment_reasons": analysis_result.enrichment_reasons,
            "llm_enriched": analysis_result.llm_enriched,
            "llm_additions": analysis_result.llm_additions if analysis_result.llm_enriched else None,
        }

    return (
        categorized[:15],
        discipline,
        field,
        confidence,
        detected_disciplines_dicts,
        article_type_dict,
        analysis_metadata,
    )
