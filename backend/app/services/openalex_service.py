"""
OpenAlex service for finding academic journals.
Uses the pyalex library to interact with OpenAlex API.

Strategy: Hybrid approach combining:
1. Works-based search: Find papers on the topic and identify publishing journals
2. Source-based search: Find specialized journals in the detected discipline
3. Topic filtering: Ensure journals are relevant to the field
"""

import pyalex
from typing import List, Optional, Dict, Set
from collections import Counter
import json
from pathlib import Path

from app.core.config import get_settings
from app.models.journal import Journal, JournalMetrics, JournalCategory

# Configure pyalex with email and API key for polite pool
settings = get_settings()
if settings.openalex_email:
    pyalex.config.email = settings.openalex_email
if settings.openalex_api_key:
    pyalex.config.api_key = settings.openalex_api_key


# Topics that indicate relevance for filtering (lowercase)
# Note: These are used for soft-boosting, not hard filtering
RELEVANT_TOPIC_KEYWORDS = {
    "psychology": [
        "psychology",
        "child",
        "infant",
        "development",
        "emotion",
        "cognitive",
        "social",
        "mental",
    ],
    "medicine": [
        "medicine",
        "medical",
        "clinical",
        "health",
        "disease",
        "therapy",
        "diagnosis",
        "patient",
        "treatment",
        "surgery",
        "cardiology",
        "neurology",
        "oncology",
        "gastroenterology",
        "urology",
        "rheumatology",
        "epidemiology",
        "pharmacology",
        "pathology",
        "radiology",
        "internal medicine",
        "general practice",
        "vaccine",
    ],
    "computer_science": [
        "computer",
        "machine learning",
        "artificial intelligence",
        "software",
        "neural",
        "deep learning",
    ],
    "biology": [
        "biology",
        "molecular",
        "cell",
        "gene",
        "organism",
        "genetic",
        "crispr",
        "biotechnology",
    ],
    "physics": [
        "physics",
        "quantum",
        "particle",
        "optics",
        "condensed matter",
        "superconductor",
        "qubit",
    ],
    "chemistry": [
        "chemistry",
        "chemical",
        "catalyst",
        "synthesis",
        "electrochemical",
        "molecular",
        "compound",
    ],
    "economics": [
        "economics",
        "economic",
        "market",
        "financial",
        "monetary",
        "fiscal",
        "trade",
    ],
    "engineering": [
        "engineering",
        "structural",
        "civil",
        "mechanical",
        "construction",
        "seismic",
    ],
    "law": ["law", "legal", "court", "judicial", "statute", "rights", "constitutional"],
    "literature": [
        "literature",
        "literary",
        "fiction",
        "novel",
        "postcolonial",
        "narrative",
        "poetry",
    ],
    "environmental_science": [
        "environmental",
        "climate",
        "ecology",
        "sustainability",
        "pollution",
        "carbon",
    ],
}


class OpenAlexService:
    """Service for searching journals via OpenAlex API."""

    def __init__(self):
        self.max_results = 25
        self.min_journal_works = 500  # Lowered to include niche journals

        # Load core journals for safety net boosting
        self.core_journals: Set[str] = set()
        self._load_core_journals()

    def _load_core_journals(self):
        """Load core journals list from JSON file."""
        try:
            data_path = Path(__file__).parent.parent / "data" / "core_journals.json"
            if data_path.exists():
                with open(data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for discipline in data.get("disciplines", []):
                        for journal in discipline.get("journals", []):
                            # Store normalized names (lowercase, alphanumeric only)
                            name = journal.get("title", "")
                            normalized = "".join(
                                c.lower() for c in name if c.isalnum() or c.isspace()
                            )
                            self.core_journals.add(" ".join(normalized.split()))
            print(f"Loaded {len(self.core_journals)} core journals for boosting.")
        except Exception as e:
            print(f"Warning: Failed to load core journals: {e}")

    def _search_sources_directly(self, query: str) -> List[dict]:
        """
        Search for sources (journals) directly by name/query.
        Useful for retrieving journals that might not surface in works-based search.
        """
        try:
            return pyalex.Sources().search(query).get(per_page=25)
        except Exception as e:
            print(f"Error searching sources directly: {e}")
            return []

    def _find_journals_from_works(
        self,
        search_query: str,
        prefer_open_access: bool = False,
    ) -> Dict[str, dict]:
        """
        Find journals by searching for papers on the topic.
        Returns dict of source_id -> source data with frequency count.
        Fetches up to 2 pages (400 works) for better coverage.
        """
        journal_counts: Dict[str, dict] = {}

        try:
            # Search for recent works on this topic (page 1)
            works_page1 = (
                pyalex.Works()
                .search(search_query)
                .filter(
                    type="article",
                    from_publication_date="2019-01-01",
                )
                .get(per_page=200)
            )

            # Process first page
            for work in works_page1:
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

            # Fetch second page if first page returned full results
            if len(works_page1) == 200:
                try:
                    works_page2 = (
                        pyalex.Works()
                        .search(search_query)
                        .filter(
                            type="article",
                            from_publication_date="2019-01-01",
                        )
                        .get(per_page=200, page=2)
                    )

                    # Process second page
                    for work in works_page2:
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

                except Exception as e:
                    print(f"OpenAlex works search page 2 error: {e}")

        except Exception as e:
            print(f"OpenAlex works search error: {e}")

        return journal_counts

    def _calculate_relevance_score(
        self,
        journal: Journal,
        discipline: str,
        is_topic_match: bool,
        is_keyword_match: bool,
        search_terms: List[str],
    ) -> float:
        """
        Calculate weighted relevance score based on:
        1. Base Score: 0.0
        2. Topic Match: +20
        3. Keyword Match: +10
        4. Exact Title Match: +50 (if journal name matches search terms)
        5. Quality Boost: + (H-index * 0.05)
        6. Discipline Boost: +15
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
        # We only check terms length > 4 to avoid generic matches like "The", "Acta"
        for term in search_terms:
            if len(term) > 4 and term.lower() in journal_name_lower:
                score += 50.0
                break

        # 5. Quality Boost (+ H-index * 0.05)
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

        # 7. Core Journal Safety Net (+100)
        # Massive boost for top 20 journals in each field to fix ranking issues
        # Normalize journal name for comparison
        journal_name_norm = "".join(
            c.lower() for c in journal.name if c.isalnum() or c.isspace()
        )
        journal_name_norm = " ".join(journal_name_norm.split())

        if journal_name_norm in self.core_journals:
            score += 100.0

        return score

    def _get_full_source_details(self, source_id: str) -> Optional[dict]:
        """Get full details for a source/journal by ID."""
        try:
            if source_id.startswith("https://"):
                source_id = source_id.split("/")[-1]
            source = pyalex.Sources()[source_id]
            return source
        except Exception as e:
            print(f"Error fetching source {source_id}: {e}")
            return None

    def _get_topic_ids_from_similar_works(self, search_query: str) -> List[str]:
        """
        Search for similar papers and extract their Topic IDs.
        Uses the new Topics API (not deprecated Concepts).

        Args:
            search_query: Combined title and abstract text.

        Returns:
            List of top 5 most frequent Topic IDs.
        """
        topic_ids: Counter = Counter()

        try:
            works = (
                pyalex.Works()
                .search(search_query)
                .filter(type="article", from_publication_date="2019-01-01")
                .get(per_page=50)
            )

            for work in works:
                topics = work.get("topics", [])
                for topic in topics:
                    topic_id = topic.get("id")
                    if topic_id:
                        # Weight by score if available
                        score = topic.get("score", 1.0)
                        topic_ids[topic_id] += score

        except Exception as e:
            print(f"Topic extraction error: {e}")

        # Return top 5 most frequent topics
        return [tid for tid, _ in topic_ids.most_common(5)]

    def _find_journals_by_topics(self, topic_ids: List[str]) -> Dict[str, dict]:
        """
        Find top journals across all identified topics in one efficient query.
        Uses group_by for server-side aggregation.

        Args:
            topic_ids: List of OpenAlex Topic IDs.

        Returns:
            Dict of source_id -> {count, reason}.
        """
        if not topic_ids:
            return {}

        try:
            # Single API call with OR logic on all topics
            # + group_by for efficient server-side aggregation
            res = (
                pyalex.Works()
                .filter(
                    topics={"id": topic_ids},  # List = automatic OR
                    type="article",
                    from_publication_date="2019-01-01",
                )
                .group_by("primary_location.source.id")
                .get()
            )

            # Convert to dict format
            journals = {}
            for entry in res:
                source_id = entry.get("key")
                count = entry.get("count", 0)
                if source_id and count > 0:
                    journals[source_id] = {
                        "count": count,
                        "reason": "High activity in relevant research topics",
                    }

            return journals

        except Exception as e:
            print(f"Error searching by topics: {e}")
            return {}

    def _merge_journal_results(
        self,
        keyword_journals: Dict[str, Journal],
        topic_journals: Dict[str, dict],
    ) -> List[Journal]:
        """
        Merge results from keyword search and topic search.
        Journals appearing in both get a significant boost.

        Args:
            keyword_journals: Dict of journal_id -> Journal from keyword search.
            topic_journals: Dict of source_id -> {count, reason} from topic search.

        Returns:
            Merged and sorted list of journals.
        """
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
                merged[source_id].match_reason = (
                    "Found in both keyword and topic search"
                )
            else:
                # New from topics - need to load full details
                full_source = self._get_full_source_details(source_id)
                if full_source:
                    works_count = full_source.get("works_count", 0)
                    if works_count >= self.min_journal_works:
                        journal = self._convert_to_journal(full_source)
                        if journal:
                            journal.relevance_score = 0.8
                            journal.match_reason = data.get("reason", "Topic match")
                            merged[source_id] = journal

        # Sort by relevance_score
        return sorted(merged.values(), key=lambda j: j.relevance_score, reverse=True)

    def search_journals_by_keywords(
        self,
        keywords: List[str],
        prefer_open_access: bool = False,
        min_works_count: Optional[int] = None,
        discipline: str = "general",
    ) -> List[Journal]:
        """
        Search for journals matching given keywords.
        Uses hybrid approach: Works-based + Specialized journal discovery.

        Args:
            keywords: List of search terms.
            prefer_open_access: Prioritize OA journals.
            min_works_count: Minimum number of works.
            discipline: Detected discipline for filtering.

        Returns:
            List of matching journals.
        """
        if not keywords:
            return []

        all_journals: Dict[str, Journal] = {}

        # 1. WORKS Search (papers that match the topic)
        search_query = " ".join(keywords[:5])
        journal_data = self._find_journals_from_works(search_query, prefer_open_access)

        # 2. DIRECT SOURCES Search (journals with matching names)
        # This fixes the "Cell" / "Science" retrieval bottleneck
        direct_sources = self._search_sources_directly(search_query)
        for source in direct_sources:
            source_id = source.get("id", "")
            if source_id and source_id not in journal_data:
                # Add to journal_data with dummy count so it gets processed
                journal_data[source_id] = {
                    "source": source,
                    "count": 0,  # Will be boosted by Name Match score
                    "is_oa": source.get("is_oa", False),
                }

        # Sort by frequency and get details for top candidates
        # Increased limit from 20 to 50 for "Wide Net"
        sorted_sources = sorted(
            journal_data.items(), key=lambda x: x[1]["count"], reverse=True
        )[:50]

        for source_id, data in sorted_sources:
            # Check if we already have the full source object
            full_source = data.get("source")
            # If "source" in data is just a summary (from works), fetch full
            # But if it came from direct_sources, it might be full enough?
            # OpenAlex source objects from "works" are usually summarized.
            # Best to always fetch full unless we are sure.
            # Optimization: If it came from direct search, it is effectively full.
            # But let's rely on _get_full_source_details for consistency and caching (if we had it)
            if not full_source or "works_count" not in full_source:
                full_source = self._get_full_source_details(source_id)

            if not full_source:
                continue

            works_count = full_source.get("works_count", 0)
            if works_count < self.min_journal_works:
                continue

            journal = self._convert_to_journal(full_source)
            if not journal:
                continue

            if journal.id not in all_journals:
                # Calculate initial relevance score
                # Note: Final score is recalculated in search_journals_by_text with full context
                score = self._calculate_relevance_score(
                    journal=journal,
                    discipline=discipline,
                    is_topic_match=False,
                    is_keyword_match=True,  # This is keyword search
                    search_terms=keywords,
                )

                # Match reason
                if data["count"] > 0:
                    journal.match_reason = (
                        f"Published {data['count']} papers on this topic"
                    )
                else:
                    journal.match_reason = "Direct name match"

                # Add small boost for paper count (0.01 per paper) to break ties
                journal.relevance_score = score + (data["count"] / 100.0)
                all_journals[journal.id] = journal

        journals = list(all_journals.values())

        # Sort by relevance_score (soft-boost) and quality metrics
        journals.sort(
            key=lambda j: (
                j.is_oa if prefer_open_access else False,
                j.relevance_score,  # Use calculated relevance score
                # Prioritize journals with topic match over generic ones
                1 if "papers on this topic" in (j.match_reason or "") else 0,
                j.metrics.h_index or 0,
            ),
            reverse=True,
        )

        return journals[:15]  # Return more candidates for hybrid merge

    def search_journals_by_text(
        self,
        title: str,
        abstract: str,
        keywords: List[str] = None,
        prefer_open_access: bool = False,
    ) -> tuple[List[Journal], str]:
        """
        Search for journals based on article title and abstract.
        Uses HYBRID approach: Keywords + Topics for best results.

        Args:
            title: Article title.
            abstract: Article abstract.
            keywords: Optional additional keywords.
            prefer_open_access: Prioritize OA journals.

        Returns:
            Tuple of (journals list, detected discipline).
        """
        combined_text = f"{title} {abstract}"
        search_terms = self._extract_search_terms(combined_text, keywords or [])

        # Detect discipline from text
        discipline = self._detect_discipline(combined_text)

        # === HYBRID APPROACH ===

        # 1. KEYWORD-BASED SEARCH (existing approach)
        keyword_journals_list = self.search_journals_by_keywords(
            search_terms, prefer_open_access=prefer_open_access, discipline=discipline
        )

        # Convert to dict for merging
        keyword_journals: Dict[str, Journal] = {j.id: j for j in keyword_journals_list}

        # 2. TOPIC-BASED SEARCH (new ML-based approach)
        topic_ids = self._get_topic_ids_from_similar_works(combined_text)
        topic_journals = self._find_journals_by_topics(topic_ids)

        # 3. MERGE RESULTS - journals in both lists get boosted
        merged_journals = self._merge_journal_results(keyword_journals, topic_journals)

        # If no results from hybrid, try broader search
        if not merged_journals:
            merged_journals = self.search_journals_by_keywords(
                search_terms[:3],
                prefer_open_access=prefer_open_access,
                discipline="general",
            )

        # Categorize journals
        categorized = self._categorize_journals(merged_journals)

        # Merged journals contains Keyword Match + Topic Match
        # Identify sources
        keyword_ids = set(keyword_journals.keys())
        topic_ids = set(topic_journals.keys())

        # Recalculate scores with Weighted Scoring
        # Keep merge bonus from _merge_journal_results
        for journal in categorized:
            is_keyword = journal.id in keyword_ids
            is_topic = journal.id in topic_ids

            # Preserve existing merge bonus (journals in both searches get boost)
            merge_bonus = journal.relevance_score if journal.relevance_score else 0

            journal.relevance_score = self._calculate_relevance_score(
                journal=journal,
                discipline=discipline,
                is_topic_match=is_topic,
                is_keyword_match=is_keyword,
                search_terms=search_terms,
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

        # Fallback: if too few results, do broader search
        if len(categorized) < 5:
            fallback_journals = self.search_journals_by_keywords(
                search_terms[:2],  # Use only top 2 terms
                prefer_open_access=prefer_open_access,
                discipline="general",
            )
            # Add fallback journals that aren't already in results
            existing_ids = {j.id for j in categorized}
            for j in fallback_journals:
                if j.id not in existing_ids and len(categorized) < 10:
                    j.match_reason = "Broader search result"
                    categorized.append(j)

        return categorized[:15], discipline

    def _convert_to_journal(self, source: dict) -> Optional[Journal]:
        """Convert OpenAlex source to Journal model."""
        try:
            issns = source.get("issn", []) or []
            issn = issns[0] if issns else None

            topics = []
            for topic in (source.get("topics", []) or [])[:5]:
                if isinstance(topic, dict) and "display_name" in topic:
                    topics.append(topic["display_name"])

            metrics = JournalMetrics(
                cited_by_count=source.get("cited_by_count"),
                works_count=source.get("works_count"),
                h_index=(
                    source.get("summary_stats", {}).get("h_index")
                    if source.get("summary_stats")
                    else None
                ),
                i10_index=(
                    source.get("summary_stats", {}).get("i10_index")
                    if source.get("summary_stats")
                    else None
                ),
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
                apc_usd=source.get("apc_usd"),
                metrics=metrics,
                topics=topics,
            )
        except Exception as e:
            print(f"Error converting source: {e}")
            return None

    def _extract_search_terms(self, text: str, keywords: List[str]) -> List[str]:
        """Extract important search terms from text."""
        terms = list(keywords)
        words = text.lower().split()

        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "need",
            "dare",
            "ought",
            "used",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "and",
            "but",
            "if",
            "or",
            "because",
            "until",
            "while",
            "this",
            "that",
            "these",
            "those",
            "we",
            "our",
            "their",
            "its",
            "it",
            "they",
            "them",
            "i",
            "you",
            "he",
            "she",
            "study",
            "research",
            "paper",
            "article",
            "analysis",
            "findings",
            "results",
            "data",
            "method",
            "using",
            "based",
        }

        for word in words:
            clean = "".join(c for c in word if c.isalnum())
            if len(clean) > 3 and clean not in stopwords and clean not in terms:
                terms.append(clean)
                if len(terms) >= 10:
                    break

        return terms[:10]

    def _detect_discipline(self, text: str) -> str:
        """Detect academic discipline from text."""
        text_lower = text.lower()

        # Extended keyword-based detection with more specificity
        # Note: Removed generic words like "behavior", "analysis", "system", "model"
        # that cause false positives across disciplines
        disciplines = {
            "psychology": [
                # Removed "behavior" - too generic, conflicts with physics/biology
                "cognitive",
                "mental health",
                "psychological",
                "emotion",
                "perception",
                "child development",
                "infant",
                "toddler",
                "empathy",
                "kindness",
                "prosocial",
                "emotional regulation",
                "social-emotional",
                "developmental psychology",
                "psychometric",
                "validation study",
                "questionnaire",
                "therapy session",
                "counseling",
                "psychotherapy",
                "anxiety disorder",
                "depression",
                "ptsd",
                "personality",
                "social psychology",
            ],
            "medicine": [
                # Clinical terms
                "clinical",
                "patient",
                "treatment",
                "disease",
                "diagnosis",
                "medical",
                "health",
                "therapy",
                "cancer",
                "tumor",
                "CT scan",
                # Study types
                "meta-analysis",
                "systematic review",
                "randomized controlled",
                "cohort study",
                "case-control",
                "clinical trial",
                "retrospective",
                # Conditions and syndromes
                "syndrome",
                "fibromyalgia",
                "chronic pain",
                "arthritis",
                "diabetes",
                "hypertension",
                "cardiovascular",
                "stroke",
                "obesity",
                "inflammation",
                "autoimmune",
                # Body systems and organs
                "bladder",
                "urinary",
                "kidney",
                "renal",
                "liver",
                "hepatic",
                "cardiac",
                "heart",
                "lung",
                "pulmonary",
                "gastrointestinal",
                "neurological",
                "musculoskeletal",
                "endocrine",
                # Epidemiology
                "prevalence",
                "incidence",
                "association",
                "comorbidity",
                "epidemiology",
                "mortality",
                "morbidity",
                "risk factor",
                # Medications and procedures
                "drug",
                "medication",
                "pharmaceutical",
                "surgery",
                "surgical",
                "transplant",
                "chemotherapy",
                "radiotherapy",
                "vaccine",
                "mrna",
                "immunization",
                "antibody",
            ],
            "computer_science": [
                # Removed generic "algorithm" - conflicts with other fields
                "machine learning",
                "neural network",
                "software",
                "database",
                "deep learning",
                "convolutional neural",
                "artificial intelligence",
                "natural language processing",
                "computer vision",
                "reinforcement learning",
                "transformer model",
                "bert",
                "gpt",
                "classification model",
                "prediction model",
                "cnn",
                "image recognition",
                "object detection",
                "nlp",
                "programming",
                "code",
                "api",
                "computing",
            ],
            "biology": [
                "cell",
                "gene",
                "protein",
                "organism",
                "species",
                "evolution",
                "molecular biology",
                "dna",
                "rna",
                "genomic",
                "transcriptome",
                "crispr",
                "genome editing",
                "genetic",
                "plant biology",
                "microbiome",
                "microbial",
                "bacteria",
                "virus",
                "ecosystem",
                "biodiversity",
                "ecology",
                "biotechnology",
                "bioinformatics",
            ],
            "physics": [
                # Significantly expanded physics keywords
                "quantum",
                "particle physics",
                "electron",
                "photon",
                "quantum mechanics",
                "quantum entanglement",
                "superconducting",
                "qubit",
                "magnetic field",
                "electromagnetic",
                "optics",
                "thermodynamics",
                "relativity",
                "gravitational",
                "nuclear",
                "plasma",
                "condensed matter",
                "semiconductor",
                "laser",
                "wave function",
                "schrödinger",
                "heisenberg",
                "boson",
                "fermion",
                "atomic",
                "subatomic",
                "hadron",
                "collider",
                "accelerator",
                "topological",
                "insulator",
                "superconductor",
                "cryogenic",
            ],
            "chemistry": [
                "chemical reaction",
                "compound",
                "molecule",
                "synthesis",
                "catalyst",
                "electrochemical",
                "organic chemistry",
                "inorganic",
                "polymer",
                "spectroscopy",
                "chromatography",
                "oxidation",
                "reduction",
                "catalysis",
                "nanomaterial",
                "graphene",
                "carbon nanotube",
                "electrochemistry",
                "photochemistry",
                "biochemistry",
                "co2 reduction",
                "carbon dioxide",
                "electrolysis",
            ],
            "economics": [
                "market",
                "economic",
                "financial",
                "trade",
                "investment",
                "monetary policy",
                "inflation",
                "gdp",
                "fiscal",
                "macroeconomic",
                "microeconomic",
                "econometric",
                "price",
                "supply demand",
                "banking",
                "currency",
                "stock market",
                "cost-effectiveness",
                "health economics",
                "welfare",
            ],
            "engineering": [
                # Expanded engineering with sub-disciplines
                "mechanical engineering",
                "electrical engineering",
                "structural",
                "civil engineering",
                "earthquake",
                "seismic",
                "bridge",
                "construction",
                "building materials",
                "concrete",
                "steel",
                "composite material",
                "aerodynamic",
                "thermodynamic",
                "robotics",
                "automation",
                "control system",
                "manufacturing",
                "sustainable materials",
                "earthquake-resistant",
            ],
            "law": [
                # New discipline
                "legal",
                "law",
                "jurisprudence",
                "court",
                "statute",
                "judicial",
                "constitutional",
                "legislation",
                "rights",
                "attorney",
                "lawsuit",
                "litigation",
                "contract law",
                "criminal law",
                "civil law",
                "privacy law",
                "regulation",
                "compliance",
                "intellectual property",
                "patent",
                "harvard law",
                "stanford law",
                "yale law",
            ],
            "literature": [
                # New discipline
                "literature",
                "fiction",
                "novel",
                "poetry",
                "narrative",
                "postcolonial",
                "literary",
                "prose",
                "drama",
                "playwright",
                "african fiction",
                "modernist",
                "postmodernist",
                "feminist",
                "comparative literature",
                "literary criticism",
                "author",
                "pmla",
                "novel",
                "short story",
                "memoir",
            ],
            "environmental_science": [
                # New discipline
                "climate",
                "pollution",
                "carbon capture",
                "environmental",
                "sustainability",
                "ecology",
                "conservation",
                "renewable",
                "emission",
                "greenhouse",
                "carbon footprint",
                "biodegradable",
                "recycling",
                "waste management",
                "air quality",
                "water quality",
                "deforestation",
                "ecosystem",
                "climate change",
                "global warming",
            ],
        }

        scores = Counter()
        for discipline, keywords in disciplines.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Give extra weight to longer/more specific keywords
                    weight = 2 if len(keyword) > 15 else 1
                    scores[discipline] += weight

        if scores:
            return scores.most_common(1)[0][0]
        return "general"

    def _categorize_journals(self, journals: List[Journal]) -> List[Journal]:
        """Categorize journals by tier."""
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


# Global instance
openalex_service = OpenAlexService()
