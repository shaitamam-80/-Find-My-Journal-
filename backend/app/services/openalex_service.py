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

from app.core.config import get_settings
from app.models.journal import Journal, JournalMetrics, JournalCategory

# Configure pyalex with email and API key for polite pool
settings = get_settings()
if settings.openalex_email:
    pyalex.config.email = settings.openalex_email
if settings.openalex_api_key:
    pyalex.config.api_key = settings.openalex_api_key


# Discipline to search terms mapping for specialized journal discovery
DISCIPLINE_SEARCH_TERMS = {
    "psychology": [
        "child development",
        "developmental psychology",
        "infant development",
        "social development",
        "emotional development",
        "clinical psychology",
        "cognitive psychology",
    ],
    "medicine": [
        "clinical medicine",
        "internal medicine",
        "medical research",
        "systematic review",
        "meta-analysis",
        "clinical trial",
        "epidemiology",
        "public health",
    ],
    "gynecology": [
        "gynecology obstetrics",
        "women's health",
        "reproductive medicine",
        "maternal health",
        "urogynecology",
    ],
    "urology": [
        "urology",
        "bladder research",
        "urinary tract",
        "nephrology",
    ],
    "urogynecology": [
        "urogynecology",
        "female pelvic medicine",
        "pelvic floor disorders",
        "international urogynecology",
    ],
    "rheumatology": [
        "rheumatology",
        "fibromyalgia research",
        "chronic pain",
        "pain medicine",
    ],
    "computer_science": [
        "machine learning",
        "artificial intelligence",
        "deep learning",
        "neural networks",
        "pattern recognition",
    ],
    "biology": [
        "molecular biology",
        "genetics",
        "cell biology",
        "biotechnology",
        "nature biotechnology",
    ],
    "physics": [
        "physical review",
        "quantum physics",
        "condensed matter",
        "applied physics",
        "optics",
    ],
    "chemistry": [
        "chemical society",
        "organic chemistry",
        "analytical chemistry",
        "electrochemistry",
    ],
    "economics": [
        "economic review",
        "monetary economics",
        "finance economics",
        "econometrics",
    ],
    "engineering": [
        "structural engineering",
        "civil engineering",
        "mechanical engineering",
        "construction materials",
    ],
    "law": [
        "law review",
        "legal studies",
        "jurisprudence",
        "constitutional law",
    ],
    "literature": [
        "literary studies",
        "comparative literature",
        "modern fiction",
        "postcolonial studies",
    ],
    "environmental_science": [
        "environmental science",
        "sustainability",
        "climate research",
        "ecology",
    ],
}

# Sub-discipline detection based on keywords
SUB_DISCIPLINE_KEYWORDS = {
    "gynecology": [
        "gynecology", "obstetrics", "women's health", "pregnancy", "menstrual",
        "uterus", "ovary", "cervical", "vaginal", "pelvic floor", "menopause",
        "maternal", "fetal", "reproductive", "fertility", "contraception",
    ],
    "urology": [
        "urology", "bladder", "urinary", "kidney", "renal", "prostate",
        "incontinence", "overactive bladder", "urination", "voiding",
        "nephrology", "ureter", "urethra", "oab",
    ],
    "urogynecology": [
        "urogynecology", "pelvic floor", "urinary incontinence", "bladder",
        "overactive bladder", "women", "female", "pelvic organ prolapse",
    ],
    "rheumatology": [
        "rheumatology", "fibromyalgia", "arthritis", "lupus", "chronic pain",
        "autoimmune", "connective tissue", "joint pain", "inflammation",
    ],
    "cardiology": [
        "cardiology", "cardiac", "heart", "cardiovascular", "coronary",
        "arrhythmia", "hypertension", "myocardial",
    ],
    "oncology": [
        "oncology", "cancer", "tumor", "malignant", "metastasis",
        "chemotherapy", "radiotherapy", "carcinoma",
    ],
    "neurology": [
        "neurology", "neurological", "brain", "stroke", "epilepsy",
        "parkinson", "alzheimer", "multiple sclerosis", "neuropathy",
    ],
    "gastroenterology": [
        "gastroenterology", "gastrointestinal", "liver", "hepatic",
        "digestive", "intestinal", "colon", "stomach",
    ],
}

# Topics that indicate relevance for filtering (lowercase)
# Note: These are used for soft-boosting, not hard filtering
RELEVANT_TOPIC_KEYWORDS = {
    "psychology": ["psychology", "child", "infant", "development", "emotion", "cognitive", "social", "mental"],
    "medicine": [
        "medicine", "medical", "clinical", "health", "disease", "therapy", "diagnosis",
        "patient", "treatment", "surgery", "cardiology", "neurology", "oncology",
        "gastroenterology", "urology", "rheumatology", "epidemiology", "pharmacology",
        "pathology", "radiology", "internal medicine", "general practice", "vaccine",
    ],
    "computer_science": ["computer", "machine learning", "artificial intelligence", "software", "neural", "deep learning"],
    "biology": ["biology", "molecular", "cell", "gene", "organism", "genetic", "crispr", "biotechnology"],
    "physics": ["physics", "quantum", "particle", "optics", "condensed matter", "superconductor", "qubit"],
    "chemistry": ["chemistry", "chemical", "catalyst", "synthesis", "electrochemical", "molecular", "compound"],
    "economics": ["economics", "economic", "market", "financial", "monetary", "fiscal", "trade"],
    "engineering": ["engineering", "structural", "civil", "mechanical", "construction", "seismic"],
    "law": ["law", "legal", "court", "judicial", "statute", "rights", "constitutional"],
    "literature": ["literature", "literary", "fiction", "novel", "postcolonial", "narrative", "poetry"],
    "environmental_science": ["environmental", "climate", "ecology", "sustainability", "pollution", "carbon"],
}


class OpenAlexService:
    """Service for searching journals via OpenAlex API."""

    def __init__(self):
        self.max_results = 25
        self.min_journal_works = 1000  # Only recommend established journals

    def _detect_sub_disciplines(self, text: str) -> List[str]:
        """
        Detect medical sub-disciplines from text.
        Returns list of detected sub-disciplines (e.g., ['gynecology', 'urology']).
        """
        text_lower = text.lower()
        detected = []

        for sub_discipline, keywords in SUB_DISCIPLINE_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches >= 2:  # Require at least 2 keyword matches
                detected.append(sub_discipline)

        return detected

    def _find_journals_from_works(
        self,
        search_query: str,
        prefer_open_access: bool = False,
    ) -> Dict[str, dict]:
        """
        Find journals by searching for papers on the topic.
        Returns dict of source_id -> source data with frequency count.
        """
        journal_counts: Dict[str, dict] = {}

        try:
            # Search for recent works on this topic
            works = pyalex.Works().search(search_query).filter(
                type="article",
                from_publication_date="2018-01-01",
            ).get(per_page=200)

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

        except Exception as e:
            print(f"OpenAlex works search error: {e}")

        return journal_counts

    def _find_specialized_journals(
        self,
        discipline: str,
        keywords: List[str],
    ) -> List[dict]:
        """
        Find specialized journals in a discipline using direct source search.
        This finds journals like 'Infancy', 'Child Development', etc.
        """
        specialized_journals = []
        seen_ids: Set[str] = set()

        # Get discipline-specific search terms
        search_terms = DISCIPLINE_SEARCH_TERMS.get(discipline, [])

        # Add user keywords that might be good journal name matches
        search_terms = search_terms + [k for k in keywords[:3] if len(k) > 4]

        for term in search_terms[:5]:  # Try up to 5 terms
            try:
                sources = pyalex.Sources().search(term).filter(
                    type="journal"
                ).get(per_page=10)

                for source in sources:
                    source_id = source.get("id", "")
                    works_count = source.get("works_count", 0)

                    # Only include established journals we haven't seen
                    if source_id and source_id not in seen_ids and works_count >= self.min_journal_works:
                        # Check if journal is relevant to the discipline
                        if self._is_journal_relevant(source, discipline):
                            seen_ids.add(source_id)
                            specialized_journals.append(source)

            except Exception as e:
                print(f"Specialized journal search error for '{term}': {e}")
                continue

        return specialized_journals

    def _get_journal_relevance_score(self, source: dict, discipline: str) -> float:
        """
        Calculate a relevance score for a journal based on discipline match.
        Returns a score from 0.0 to 1.0 (higher = more relevant).

        IMPORTANT: This is a SOFT-BOOST, not a hard filter.
        Even journals with low scores are kept - they just rank lower.
        """
        relevant_keywords = RELEVANT_TOPIC_KEYWORDS.get(discipline, [])
        if not relevant_keywords:
            return 0.5  # Neutral score for unknown disciplines

        score = 0.0
        journal_name = source.get("display_name", "").lower()

        # Check journal name for relevant keywords (strong signal)
        for keyword in relevant_keywords:
            if keyword in journal_name:
                score += 0.4
                break

        # Check journal topics for relevance
        topics = source.get("topics", []) or []
        relevant_topic_count = 0

        for topic in topics[:5]:
            if isinstance(topic, dict):
                topic_name = topic.get("display_name", "").lower()
                field_name = topic.get("field", {}).get("display_name", "").lower() if topic.get("field") else ""

                for keyword in relevant_keywords:
                    if keyword in topic_name or keyword in field_name:
                        relevant_topic_count += 1
                        break

        # Add score based on topic matches (up to 0.6 for 3+ matches)
        score += min(relevant_topic_count * 0.2, 0.6)

        return min(score, 1.0)

    def _is_journal_relevant(self, source: dict, discipline: str) -> bool:
        """
        DEPRECATED: Kept for backward compatibility but now always returns True.
        Use _get_journal_relevance_score() for soft-boosting instead.
        """
        # Always return True - we use soft-boost scoring instead of hard filtering
        return True

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
            works = pyalex.Works().search(search_query).filter(
                type="article",
                from_publication_date="2020-01-01"
            ).get(per_page=50)

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
                    from_publication_date="2020-01-01",
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
                        "reason": "High activity in relevant research topics"
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
                merged[source_id].match_reason = "Found in both keyword and topic search"
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

        # 1. Find journals through works search (papers that match the topic)
        search_query = " ".join(keywords[:5])
        journal_data = self._find_journals_from_works(search_query, prefer_open_access)

        # Sort by frequency and get details for top candidates
        sorted_sources = sorted(
            journal_data.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:20]

        for source_id, data in sorted_sources:
            full_source = self._get_full_source_details(source_id)
            if not full_source:
                continue

            works_count = full_source.get("works_count", 0)
            if works_count < self.min_journal_works:
                continue

            # SOFT-BOOST: Calculate relevance score instead of filtering
            # This ensures Topic-based journals aren't filtered out due to wrong discipline detection
            relevance_boost = self._get_journal_relevance_score(full_source, discipline)

            journal = self._convert_to_journal(full_source)
            if journal and journal.id not in all_journals:
                journal.match_reason = f"Published {data['count']} papers on this topic"
                journal.relevance_score = relevance_boost + (data['count'] / 100.0)  # Boost by paper count
                all_journals[journal.id] = journal

        # 2. Find specialized journals in the discipline
        if discipline != "general":
            specialized = self._find_specialized_journals(discipline, keywords)
            for source in specialized:
                source_id = source.get("id", "")
                if source_id not in all_journals:
                    full_source = self._get_full_source_details(source_id)
                    if full_source:
                        journal = self._convert_to_journal(full_source)
                        if journal:
                            journal.match_reason = "Specialized journal in this field"
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
            reverse=True
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
        sub_disciplines = self._detect_sub_disciplines(combined_text)

        # === HYBRID APPROACH ===

        # 1. KEYWORD-BASED SEARCH (existing approach)
        keyword_journals_list = self.search_journals_by_keywords(
            search_terms,
            prefer_open_access=prefer_open_access,
            discipline=discipline
        )

        # Add specialized journals from sub-disciplines
        all_journal_ids = {j.id for j in keyword_journals_list}
        for sub_disc in sub_disciplines:
            specialized = self._find_specialized_journals(sub_disc, keywords or [])
            for source in specialized:
                source_id = source.get("id", "")
                if source_id and source_id not in all_journal_ids:
                    full_source = self._get_full_source_details(source_id)
                    if full_source:
                        journal = self._convert_to_journal(full_source)
                        if journal:
                            journal.match_reason = f"Specialized {sub_disc} journal"
                            keyword_journals_list.append(journal)
                            all_journal_ids.add(journal.id)

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
                discipline="general"
            )

        # Categorize journals
        categorized = self._categorize_journals(merged_journals)

        # Final sort: prioritize by relevance_score, then h_index
        categorized.sort(
            key=lambda j: (
                j.is_oa if prefer_open_access else False,
                j.relevance_score,
                # Boost journals found in both keyword and topic search
                3 if "both keyword and topic" in (j.match_reason or "") else (
                    2 if "Specialized" in (j.match_reason or "") else (
                        1 if "papers on this topic" in (j.match_reason or "") else 0
                    )
                ),
                j.metrics.h_index or 0,
            ),
            reverse=True
        )

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
                h_index=source.get("summary_stats", {}).get("h_index") if source.get("summary_stats") else None,
                i10_index=source.get("summary_stats", {}).get("i10_index") if source.get("summary_stats") else None,
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
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all",
            "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "just", "and", "but", "if", "or", "because",
            "until", "while", "this", "that", "these", "those", "we",
            "our", "their", "its", "it", "they", "them", "i", "you",
            "he", "she", "study", "research", "paper", "article", "analysis",
            "findings", "results", "data", "method", "using", "based",
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
                "cognitive", "mental health", "psychological", "emotion",
                "perception", "child development", "infant", "toddler", "empathy",
                "kindness", "prosocial", "emotional regulation", "social-emotional",
                "developmental psychology", "psychometric", "validation study", "questionnaire",
                "therapy session", "counseling", "psychotherapy", "anxiety disorder",
                "depression", "ptsd", "personality", "social psychology",
            ],
            "medicine": [
                # Clinical terms
                "clinical", "patient", "treatment", "disease", "diagnosis",
                "medical", "health", "therapy", "cancer", "tumor", "CT scan",
                # Study types
                "meta-analysis", "systematic review", "randomized controlled",
                "cohort study", "case-control", "clinical trial", "retrospective",
                # Conditions and syndromes
                "syndrome", "fibromyalgia", "chronic pain", "arthritis",
                "diabetes", "hypertension", "cardiovascular", "stroke",
                "obesity", "inflammation", "autoimmune",
                # Body systems and organs
                "bladder", "urinary", "kidney", "renal", "liver", "hepatic",
                "cardiac", "heart", "lung", "pulmonary", "gastrointestinal",
                "neurological", "musculoskeletal", "endocrine",
                # Epidemiology
                "prevalence", "incidence", "association", "comorbidity",
                "epidemiology", "mortality", "morbidity", "risk factor",
                # Medications and procedures
                "drug", "medication", "pharmaceutical", "surgery", "surgical",
                "transplant", "chemotherapy", "radiotherapy",
                "vaccine", "mrna", "immunization", "antibody",
            ],
            "computer_science": [
                # Removed generic "algorithm" - conflicts with other fields
                "machine learning", "neural network", "software",
                "database", "deep learning", "convolutional neural",
                "artificial intelligence", "natural language processing",
                "computer vision", "reinforcement learning", "transformer model",
                "bert", "gpt", "classification model", "prediction model",
                "cnn", "image recognition", "object detection", "nlp",
                "programming", "code", "api", "computing",
            ],
            "biology": [
                "cell", "gene", "protein", "organism", "species", "evolution",
                "molecular biology", "dna", "rna", "genomic", "transcriptome",
                "crispr", "genome editing", "genetic", "plant biology",
                "microbiome", "microbial", "bacteria", "virus", "ecosystem",
                "biodiversity", "ecology", "biotechnology", "bioinformatics",
            ],
            "physics": [
                # Significantly expanded physics keywords
                "quantum", "particle physics", "electron", "photon",
                "quantum mechanics", "quantum entanglement", "superconducting",
                "qubit", "magnetic field", "electromagnetic", "optics",
                "thermodynamics", "relativity", "gravitational", "nuclear",
                "plasma", "condensed matter", "semiconductor", "laser",
                "wave function", "schrödinger", "heisenberg", "boson", "fermion",
                "atomic", "subatomic", "hadron", "collider", "accelerator",
                "topological", "insulator", "superconductor", "cryogenic",
            ],
            "chemistry": [
                "chemical reaction", "compound", "molecule", "synthesis", "catalyst",
                "electrochemical", "organic chemistry", "inorganic", "polymer",
                "spectroscopy", "chromatography", "oxidation", "reduction",
                "catalysis", "nanomaterial", "graphene", "carbon nanotube",
                "electrochemistry", "photochemistry", "biochemistry",
                "co2 reduction", "carbon dioxide", "electrolysis",
            ],
            "economics": [
                "market", "economic", "financial", "trade", "investment",
                "monetary policy", "inflation", "gdp", "fiscal",
                "macroeconomic", "microeconomic", "econometric", "price",
                "supply demand", "banking", "currency", "stock market",
                "cost-effectiveness", "health economics", "welfare",
            ],
            "engineering": [
                # Expanded engineering with sub-disciplines
                "mechanical engineering", "electrical engineering", "structural",
                "civil engineering", "earthquake", "seismic", "bridge",
                "construction", "building materials", "concrete", "steel",
                "composite material", "aerodynamic", "thermodynamic",
                "robotics", "automation", "control system", "manufacturing",
                "sustainable materials", "earthquake-resistant",
            ],
            "law": [
                # New discipline
                "legal", "law", "jurisprudence", "court", "statute",
                "judicial", "constitutional", "legislation", "rights",
                "attorney", "lawsuit", "litigation", "contract law",
                "criminal law", "civil law", "privacy law", "regulation",
                "compliance", "intellectual property", "patent",
                "harvard law", "stanford law", "yale law",
            ],
            "literature": [
                # New discipline
                "literature", "fiction", "novel", "poetry", "narrative",
                "postcolonial", "literary", "prose", "drama", "playwright",
                "african fiction", "modernist", "postmodernist", "feminist",
                "comparative literature", "literary criticism", "author",
                "pmla", "novel", "short story", "memoir",
            ],
            "environmental_science": [
                # New discipline
                "climate", "pollution", "carbon capture", "environmental",
                "sustainability", "ecology", "conservation", "renewable",
                "emission", "greenhouse", "carbon footprint", "biodegradable",
                "recycling", "waste management", "air quality", "water quality",
                "deforestation", "ecosystem", "climate change", "global warming",
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
