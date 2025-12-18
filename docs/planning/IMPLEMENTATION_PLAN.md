# 📋 תכנית הטמעה - OpenAlex Refactoring
## From God File → Clean Architecture

---

## 📊 סיכום מצב נוכחי

| מדד | ערך נוכחי |
|-----|-----------|
| קובץ | `backend/app/services/openalex_service.py` |
| גודל | **1,231 שורות** |
| ספריית HTTP | `pyalex` (לא httpx) |
| מחלקה ראשית | `OpenAlexService` |
| מתודות | 15 מתודות |
| קבועים | `RELEVANT_TOPIC_KEYWORDS` (~120 שורות) |
| תיקיית יעד | `openalex/` - **לא קיימת עדיין** |

---

## 🎯 מבנה יעד

```
backend/app/services/openalex/
├── __init__.py       # ~80 שורות  - Public API, re-exports
├── config.py         # ~50 שורות  - קונפיגורציה + pyalex setup
├── constants.py      # ~150 שורות - RELEVANT_TOPIC_KEYWORDS + core journals
├── models.py         # ~60 שורות  - Type hints, data classes (אם נדרש)
├── utils.py          # ~120 שורות - עזר: extract_terms, detect_discipline
├── client.py         # ~100 שורות - pyalex wrapper + caching
├── scoring.py        # ~80 שורות  - calculate_relevance_score
├── journals.py       # ~180 שורות - journal operations
├── search.py         # ~250 שורות - search_journals_by_text, hybrid search
└── service.py        # ~80 שורות  - OpenAlexService facade (backward compat)

Total: ~1,150 שורות (vs 1,231 מקורי)
Max per file: ~250 שורות ✓
```

---

## ⏱️ הערכת זמנים

| שלב | משך | תלוי ב | סוג |
|-----|-----|--------|-----|
| **Phase 0**: ניתוח מעמיק | 30 דק | - | סדרתי |
| **Phase 1**: יצירת מבנה | 10 דק | Phase 0 | סדרתי |
| **Phase 2**: Foundation | 60 דק | Phase 1 | סדרתי |
| **Phase 3**: Core Logic | 90 דק | Phase 2 | חלקית מקבילי |
| **Phase 4**: Backward Compat | 20 דק | Phase 3 | סדרתי |
| **Phase 5**: Testing | 60 דק | Phase 4 | מקבילי |
| **Phase 6**: Documentation | 20 דק | Phase 5 | מקבילי |
|---------|----------|-----------|-------|
| **סה"כ (סדרתי)** | **~5 שעות** | | |
| **סה"כ (מקבילי)** | **~3 שעות** | | |

---

# 📋 PHASE 0: ניתוח מעמיק
## משך: 30 דקות | תלוי ב: אין

### מטרה
לפני כל שינוי קוד - להבין את המבנה המלא.

### פעולות

```yaml
task: "ניתוח מלא של openalex_service.py"

1. מיפוי מתודות:
   □ _search_sources_directly (170-179)
   □ _find_journals_from_works (181-256)
   □ _calculate_relevance_score (258-329)
   □ _get_full_source_details (331-340)
   □ _get_topic_ids_from_similar_works (342-376)
   □ _find_journals_by_topics (378-421)
   □ _merge_journal_results (423-467)
   □ search_journals_by_keywords (469-577)
   □ search_journals_by_text (579-679)
   □ _convert_to_journal (681-722)
   □ _extract_search_terms (724-849)
   □ _detect_discipline (851-1201)
   □ _categorize_journals (1203-1226)

2. זיהוי תלויות:
   □ pyalex (ספריית HTTP ראשית)
   □ app.core.config (הגדרות)
   □ app.models.journal (Journal, JournalMetrics, JournalCategory)

3. זיהוי קבועים:
   □ RELEVANT_TOPIC_KEYWORDS (שורות 28-137)
   □ core_journals.json (קובץ חיצוני)

4. זיהוי state:
   □ self.max_results = 25
   □ self.min_journal_works = 500
   □ self.core_journals: Set[str]

output:
   Create: OPENALEX_ANALYSIS.md
```

### תוצר
קובץ `OPENALEX_ANALYSIS.md` עם:
- מיפוי מלא של כל המתודות
- גרף תלויות
- סדר חילוץ מומלץ

---

# 📋 PHASE 1: יצירת מבנה תיקיות
## משך: 10 דקות | תלוי ב: Phase 0

### פעולות

```bash
# יצירת תיקיית הפקג'
mkdir -p backend/app/services/openalex

# יצירת קבצי המודולים
touch backend/app/services/openalex/__init__.py
touch backend/app/services/openalex/config.py
touch backend/app/services/openalex/constants.py
touch backend/app/services/openalex/utils.py
touch backend/app/services/openalex/client.py
touch backend/app/services/openalex/scoring.py
touch backend/app/services/openalex/journals.py
touch backend/app/services/openalex/search.py
touch backend/app/services/openalex/service.py

# יצירת תיקיית טסטים
mkdir -p backend/tests/services/openalex
touch backend/tests/services/openalex/__init__.py
touch backend/tests/services/openalex/conftest.py

# וידוא מבנה
tree backend/app/services/openalex/
```

### מבנה צפוי
```
backend/app/services/openalex/
├── __init__.py
├── config.py
├── constants.py
├── utils.py
├── client.py
├── scoring.py
├── journals.py
├── search.py
└── service.py
```

---

# 📋 PHASE 2: חילוץ Foundation Modules
## משך: 60 דקות | תלוי ב: Phase 1
## סדר: config → constants → utils (סדרתי)

---

### Step 2.1: config.py (~50 שורות)

```python
# File: backend/app/services/openalex/config.py
"""
OpenAlex Service Configuration

Sets up pyalex library with email and API key for polite pool.
"""
import pyalex
from functools import lru_cache
from typing import Optional

from app.core.config import get_settings as get_app_settings


class OpenAlexConfig:
    """OpenAlex-specific configuration."""

    # Default values
    MAX_RESULTS: int = 25
    MIN_JOURNAL_WORKS: int = 500
    WORKS_PER_PAGE: int = 200
    MAX_SEARCH_TERMS: int = 10

    def __init__(self):
        self._configure_pyalex()

    def _configure_pyalex(self) -> None:
        """Configure pyalex with credentials from app settings."""
        settings = get_app_settings()
        if settings.openalex_email:
            pyalex.config.email = settings.openalex_email
        if settings.openalex_api_key:
            pyalex.config.api_key = settings.openalex_api_key


@lru_cache
def get_config() -> OpenAlexConfig:
    """Get cached OpenAlex configuration."""
    return OpenAlexConfig()


def get_max_results() -> int:
    return get_config().MAX_RESULTS


def get_min_journal_works() -> int:
    return get_config().MIN_JOURNAL_WORKS
```

---

### Step 2.2: constants.py (~150 שורות)

```python
# File: backend/app/services/openalex/constants.py
"""
OpenAlex Constants and Domain Knowledge

Contains:
- RELEVANT_TOPIC_KEYWORDS: Keywords for soft-boosting by discipline
- Core journals loading functionality
"""
import json
from pathlib import Path
from typing import Dict, List, Set

# Topics that indicate relevance for filtering (lowercase)
# Used for soft-boosting, not hard filtering
RELEVANT_TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "psychology": [
        "psychology", "child", "infant", "development", "emotion",
        "cognitive", "social", "mental",
    ],
    "medicine": [
        "medicine", "medical", "clinical", "health", "disease",
        "therapy", "diagnosis", "patient", "treatment", "surgery",
        "cardiology", "neurology", "oncology", "gastroenterology",
        "urology", "rheumatology", "epidemiology", "pharmacology",
        "pathology", "radiology", "internal medicine", "vaccine",
    ],
    "computer_science": [
        "computer", "machine learning", "artificial intelligence",
        "software", "neural", "deep learning",
    ],
    "biology": [
        "biology", "molecular", "cell", "gene", "organism",
        "genetic", "crispr", "biotechnology",
    ],
    "physics": [
        "physics", "quantum", "particle", "optics",
        "condensed matter", "superconductor", "qubit",
    ],
    "chemistry": [
        "chemistry", "chemical", "catalyst", "synthesis",
        "electrochemical", "molecular", "compound",
    ],
    "economics": [
        "economics", "economic", "market", "financial",
        "monetary", "fiscal", "trade",
    ],
    "engineering": [
        "engineering", "structural", "civil", "mechanical",
        "construction", "seismic",
    ],
    "law": [
        "law", "legal", "court", "judicial", "statute",
        "rights", "constitutional",
    ],
    "literature": [
        "literature", "literary", "fiction", "novel",
        "postcolonial", "narrative", "poetry",
    ],
    "environmental_science": [
        "environmental", "climate", "ecology", "sustainability",
        "pollution", "carbon",
    ],
}


def load_core_journals() -> Set[str]:
    """
    Load core journals list from JSON file.

    Returns:
        Set of normalized journal names for boosting.
    """
    core_journals: Set[str] = set()

    try:
        data_path = Path(__file__).parent.parent.parent / "data" / "core_journals.json"
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for discipline in data.get("disciplines", []):
                    for journal in discipline.get("journals", []):
                        name = journal.get("title", "")
                        # Normalize: lowercase, alphanumeric only
                        normalized = "".join(
                            c.lower() for c in name if c.isalnum() or c.isspace()
                        )
                        core_journals.add(" ".join(normalized.split()))
        print(f"Loaded {len(core_journals)} core journals for boosting.")
    except Exception as e:
        print(f"Warning: Failed to load core journals: {e}")

    return core_journals


# Discipline detection keywords - moved from _detect_discipline method
DISCIPLINE_KEYWORDS: Dict[str, List[str]] = {
    "psychology": [
        "cognitive", "mental health", "psychological", "emotion",
        "perception", "child development", "infant", "toddler",
        "empathy", "prosocial", "developmental psychology",
        # ... (rest from original, lines 859-886)
    ],
    "medicine": [
        "clinical", "patient", "treatment", "disease", "diagnosis",
        "medical", "health", "therapy", "cancer", "tumor",
        # ... (rest from original, lines 888-957)
    ],
    # ... (remaining disciplines)
}
```

---

### Step 2.3: utils.py (~120 שורות)

```python
# File: backend/app/services/openalex/utils.py
"""
OpenAlex Utility Functions

Shared helpers for text processing and discipline detection.
"""
from collections import Counter
from typing import List, Set

from .constants import DISCIPLINE_KEYWORDS


# Stopwords for search term extraction
STOPWORDS: Set[str] = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "just", "and", "but",
    "if", "or", "because", "until", "while", "this", "that", "these",
    "those", "we", "our", "their", "its", "it", "they", "them", "i",
    "you", "he", "she", "study", "research", "paper", "article",
    "analysis", "findings", "results", "data", "method", "using", "based",
}


def extract_search_terms(text: str, keywords: List[str], max_terms: int = 10) -> List[str]:
    """
    Extract important search terms from text.

    Args:
        text: Combined title and abstract text.
        keywords: User-provided keywords to prioritize.
        max_terms: Maximum number of terms to return.

    Returns:
        List of search terms, keywords first.
    """
    terms = list(keywords)
    words = text.lower().split()

    for word in words:
        clean = "".join(c for c in word if c.isalnum())
        if len(clean) > 3 and clean not in STOPWORDS and clean not in terms:
            terms.append(clean)
            if len(terms) >= max_terms:
                break

    return terms[:max_terms]


def detect_discipline(text: str) -> str:
    """
    Detect academic discipline from text.

    Args:
        text: Combined title and abstract text.

    Returns:
        Detected discipline name or "general".
    """
    text_lower = text.lower()
    scores = Counter()

    for discipline, keywords in DISCIPLINE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Extra weight for longer/more specific keywords
                weight = 2 if len(keyword) > 15 else 1
                scores[discipline] += weight

    if scores:
        return scores.most_common(1)[0][0]
    return "general"


def normalize_journal_name(name: str) -> str:
    """
    Normalize journal name for comparison.

    Args:
        name: Journal display name.

    Returns:
        Lowercase, alphanumeric only, single spaces.
    """
    normalized = "".join(c.lower() for c in name if c.isalnum() or c.isspace())
    return " ".join(normalized.split())
```

---

# 📋 PHASE 3: חילוץ Core Logic
## משך: 90 דקות | תלוי ב: Phase 2
## סדר: client → scoring → journals → search

---

### Step 3.1: client.py (~100 שורות)

```python
# File: backend/app/services/openalex/client.py
"""
OpenAlex API Client

Wraps pyalex library with error handling and logging.
"""
import pyalex
from typing import List, Dict, Optional, Any
import logging

from .config import get_config

logger = logging.getLogger(__name__)


class OpenAlexClient:
    """
    Client for OpenAlex API operations.

    Wraps pyalex with consistent error handling.
    """

    def __init__(self):
        self.config = get_config()

    def search_sources(self, query: str, per_page: int = 25) -> List[dict]:
        """Search for sources (journals) directly by name/query."""
        try:
            return pyalex.Sources().search(query).get(per_page=per_page)
        except Exception as e:
            logger.error(f"Error searching sources directly: {e}")
            return []

    def search_works(
        self,
        query: str,
        per_page: int = 200,
        page: int = 1,
        from_date: str = "2019-01-01",
    ) -> List[dict]:
        """Search for works (papers) on a topic."""
        try:
            return (
                pyalex.Works()
                .search(query)
                .filter(type="article", from_publication_date=from_date)
                .get(per_page=per_page, page=page)
            )
        except Exception as e:
            logger.error(f"Error searching works: {e}")
            return []

    def get_source_by_id(self, source_id: str) -> Optional[dict]:
        """Get full details for a source/journal by ID."""
        try:
            if source_id.startswith("https://"):
                source_id = source_id.split("/")[-1]
            return pyalex.Sources()[source_id]
        except Exception as e:
            logger.error(f"Error fetching source {source_id}: {e}")
            return None

    def group_works_by_source(
        self,
        topic_ids: List[str],
        from_date: str = "2019-01-01",
    ) -> List[dict]:
        """
        Group works by source ID for topic-based search.

        Uses server-side aggregation for efficiency.
        """
        if not topic_ids:
            return []

        try:
            return (
                pyalex.Works()
                .filter(
                    topics={"id": topic_ids},
                    type="article",
                    from_publication_date=from_date,
                )
                .group_by("primary_location.source.id")
                .get()
            )
        except Exception as e:
            logger.error(f"Error grouping works by source: {e}")
            return []


# Global client instance
_client: Optional[OpenAlexClient] = None


def get_client() -> OpenAlexClient:
    """Get or create global client instance."""
    global _client
    if _client is None:
        _client = OpenAlexClient()
    return _client
```

---

### Step 3.2: scoring.py (~80 שורות)

```python
# File: backend/app/services/openalex/scoring.py
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
    4. Exact Title Match: +50
    5. Quality Boost: H-index * 0.05
    6. Discipline Boost: +15
    7. Core Journal Safety Net: +100

    Args:
        journal: Journal to score.
        discipline: Detected discipline.
        is_topic_match: Found via topic search.
        is_keyword_match: Found via keyword search.
        search_terms: Original search terms.
        core_journals: Set of core journal names.

    Returns:
        Relevance score (higher = more relevant).
    """
    score = 0.0
    journal_name_lower = journal.name.lower()

    # Topic Match (+20)
    if is_topic_match:
        score += 20.0

    # Keyword Match (+10)
    if is_keyword_match:
        score += 10.0

    # Exact Title Match (+50)
    for term in search_terms:
        if len(term) > 4 and term.lower() in journal_name_lower:
            score += 50.0
            break

    # Quality Boost (H-index * 0.05)
    h_index = journal.metrics.h_index or 0
    score += h_index * 0.05

    # Discipline Boost (+15)
    relevant_keywords = RELEVANT_TOPIC_KEYWORDS.get(discipline, [])
    is_discipline_relevant = any(k in journal_name_lower for k in relevant_keywords)

    if not is_discipline_relevant:
        for topic in journal.topics:
            if any(k in topic.lower() for k in relevant_keywords):
                is_discipline_relevant = True
                break

    if is_discipline_relevant:
        score += 15.0

    # Core Journal Safety Net (+100)
    journal_name_norm = normalize_journal_name(journal.name)
    if journal_name_norm in core_journals:
        score += 100.0

    return score
```

---

### Step 3.3: journals.py (~180 שורות)

```python
# File: backend/app/services/openalex/journals.py
"""
Journal Operations

Convert, categorize, and merge journal results.
"""
from typing import Dict, List, Optional, Set
from collections import Counter

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


def categorize_journals(journals: List[Journal]) -> List[Journal]:
    """
    Categorize journals by tier based on metrics.

    Categories:
    - TOP_TIER: h_index > 100 or works > 50000
    - BROAD_AUDIENCE: works > 10000
    - NICHE: works > 1000
    - EMERGING: everything else
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

    return sorted(merged.values(), key=lambda j: j.relevance_score, reverse=True)
```

---

### Step 3.4: search.py (~250 שורות)

```python
# File: backend/app/services/openalex/search.py
"""
Journal Search Operations

Hybrid search combining keywords and topic matching.
"""
from collections import Counter
from typing import Dict, List, Optional, Tuple, Set

from app.models.journal import Journal
from .client import get_client
from .config import get_min_journal_works
from .constants import load_core_journals
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


def get_topic_ids_from_similar_works(search_query: str) -> List[str]:
    """
    Extract Topic IDs from similar papers.

    Returns top 5 most frequent topic IDs.
    """
    client = get_client()
    topic_ids: Counter = Counter()

    works = client.search_works(search_query, per_page=50)

    for work in works:
        for topic in work.get("topics", []):
            topic_id = topic.get("id")
            if topic_id:
                score = topic.get("score", 1.0)
                topic_ids[topic_id] += score

    return [tid for tid, _ in topic_ids.most_common(5)]


def find_journals_by_topics(topic_ids: List[str]) -> Dict[str, dict]:
    """
    Find top journals across all identified topics.
    """
    if not topic_ids:
        return {}

    client = get_client()
    journals = {}

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
    """
    if not keywords:
        return []

    if core_journals is None:
        core_journals = load_core_journals()

    client = get_client()
    min_works = min_works_count or get_min_journal_works()
    all_journals: Dict[str, Journal] = {}

    # 1. Works search
    search_query = " ".join(keywords[:5])
    journal_data = find_journals_from_works(search_query, prefer_open_access)

    # 2. Direct sources search
    direct_sources = client.search_sources(search_query)
    for source in direct_sources:
        source_id = source.get("id", "")
        if source_id and source_id not in journal_data:
            journal_data[source_id] = {
                "source": source,
                "count": 0,
                "is_oa": source.get("is_oa", False),
            }

    # Sort and process top 50
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

        score = calculate_relevance_score(
            journal=journal,
            discipline=discipline,
            is_topic_match=False,
            is_keyword_match=True,
            search_terms=keywords,
            core_journals=core_journals,
        )

        if data["count"] > 0:
            journal.match_reason = f"Published {data['count']} papers on this topic"
        else:
            journal.match_reason = "Direct name match"

        journal.relevance_score = score + (data["count"] / 100.0)
        all_journals[journal.id] = journal

    # Sort and return top 15
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

    return journals[:15]


def search_journals_by_text(
    title: str,
    abstract: str,
    keywords: List[str] = None,
    prefer_open_access: bool = False,
) -> Tuple[List[Journal], str]:
    """
    Search for journals based on article title and abstract.

    Uses HYBRID approach: Keywords + Topics for best results.

    Returns:
        Tuple of (journals list, detected discipline).
    """
    core_journals = load_core_journals()
    combined_text = f"{title} {abstract}"
    search_terms = extract_search_terms(combined_text, keywords or [])
    discipline = detect_discipline(combined_text)

    # 1. Keyword-based search
    keyword_journals_list = search_journals_by_keywords(
        search_terms,
        prefer_open_access=prefer_open_access,
        discipline=discipline,
        core_journals=core_journals,
    )
    keyword_journals: Dict[str, Journal] = {j.id: j for j in keyword_journals_list}

    # 2. Topic-based search
    topic_ids = get_topic_ids_from_similar_works(combined_text)
    topic_journals = find_journals_by_topics(topic_ids)

    # 3. Merge results
    merged_journals = merge_journal_results(keyword_journals, topic_journals)

    # Fallback if no results
    if not merged_journals:
        merged_journals = search_journals_by_keywords(
            search_terms[:3],
            prefer_open_access=prefer_open_access,
            discipline="general",
            core_journals=core_journals,
        )

    # Categorize and recalculate scores
    categorized = categorize_journals(merged_journals)

    keyword_ids = set(keyword_journals.keys())
    topic_id_set = set(topic_journals.keys())

    for journal in categorized:
        is_keyword = journal.id in keyword_ids
        is_topic = journal.id in topic_id_set
        merge_bonus = journal.relevance_score or 0

        journal.relevance_score = calculate_relevance_score(
            journal=journal,
            discipline=discipline,
            is_topic_match=is_topic,
            is_keyword_match=is_keyword,
            search_terms=search_terms,
            core_journals=core_journals,
        ) + (merge_bonus * 10)

    # Final sort
    categorized.sort(
        key=lambda j: (
            j.is_oa if prefer_open_access else False,
            j.relevance_score,
            j.metrics.h_index or 0,
        ),
        reverse=True,
    )

    # Add fallback if too few results
    if len(categorized) < 5:
        fallback = search_journals_by_keywords(
            search_terms[:2],
            prefer_open_access=prefer_open_access,
            discipline="general",
            core_journals=core_journals,
        )
        existing_ids = {j.id for j in categorized}
        for j in fallback:
            if j.id not in existing_ids and len(categorized) < 10:
                j.match_reason = "Broader search result"
                categorized.append(j)

    return categorized[:15], discipline
```

---

# 📋 PHASE 4: Backward Compatibility
## משך: 20 דקות | תלוי ב: Phase 3

---

### Step 4.1: service.py - Facade (~80 שורות)

```python
# File: backend/app/services/openalex/service.py
"""
OpenAlex Service Facade

Maintains backward compatibility with existing code.
"""
from typing import List, Optional, Set

from app.models.journal import Journal
from .constants import load_core_journals
from .search import search_journals_by_keywords, search_journals_by_text


class OpenAlexService:
    """
    Service for searching journals via OpenAlex API.

    This is a facade that maintains backward compatibility.
    For new code, prefer using the module functions directly.
    """

    def __init__(self):
        self.max_results = 25
        self.min_journal_works = 500
        self.core_journals: Set[str] = load_core_journals()

    def search_journals_by_keywords(
        self,
        keywords: List[str],
        prefer_open_access: bool = False,
        min_works_count: Optional[int] = None,
        discipline: str = "general",
    ) -> List[Journal]:
        """Search for journals matching given keywords."""
        return search_journals_by_keywords(
            keywords=keywords,
            prefer_open_access=prefer_open_access,
            min_works_count=min_works_count,
            discipline=discipline,
            core_journals=self.core_journals,
        )

    def search_journals_by_text(
        self,
        title: str,
        abstract: str,
        keywords: List[str] = None,
        prefer_open_access: bool = False,
    ) -> tuple[List[Journal], str]:
        """Search for journals based on article title and abstract."""
        return search_journals_by_text(
            title=title,
            abstract=abstract,
            keywords=keywords,
            prefer_open_access=prefer_open_access,
        )


# Global instance for backward compatibility
openalex_service = OpenAlexService()
```

---

### Step 4.2: __init__.py - Public API (~80 שורות)

```python
# File: backend/app/services/openalex/__init__.py
"""
OpenAlex Service Package

Integration with the OpenAlex API for journal discovery.

Usage:
    # Recommended - direct function import
    from app.services.openalex import search_journals_by_text

    # Or use the service class
    from app.services.openalex import openalex_service

    # Legacy import still works
    from app.services.openalex_service import openalex_service
"""

__version__ = "2.0.0"

# Public API - functions
from .search import (
    search_journals_by_text,
    search_journals_by_keywords,
    find_journals_from_works,
    get_topic_ids_from_similar_works,
    find_journals_by_topics,
)

from .journals import (
    convert_to_journal,
    categorize_journals,
    merge_journal_results,
)

from .scoring import calculate_relevance_score

from .utils import (
    extract_search_terms,
    detect_discipline,
    normalize_journal_name,
)

from .client import (
    OpenAlexClient,
    get_client,
)

from .config import (
    OpenAlexConfig,
    get_config,
)

from .constants import (
    RELEVANT_TOPIC_KEYWORDS,
    DISCIPLINE_KEYWORDS,
    load_core_journals,
)

# Service class and global instance
from .service import OpenAlexService, openalex_service


__all__ = [
    # Version
    "__version__",
    # Main search functions
    "search_journals_by_text",
    "search_journals_by_keywords",
    # Journal operations
    "convert_to_journal",
    "categorize_journals",
    "merge_journal_results",
    # Scoring
    "calculate_relevance_score",
    # Utils
    "extract_search_terms",
    "detect_discipline",
    "normalize_journal_name",
    # Client
    "OpenAlexClient",
    "get_client",
    # Config
    "OpenAlexConfig",
    "get_config",
    # Constants
    "RELEVANT_TOPIC_KEYWORDS",
    "DISCIPLINE_KEYWORDS",
    "load_core_journals",
    # Service (backward compat)
    "OpenAlexService",
    "openalex_service",
]
```

---

### Step 4.3: Update openalex_service.py (Deprecated Facade)

```python
# File: backend/app/services/openalex_service.py
"""
DEPRECATED: Import from app.services.openalex instead

This file exists for backward compatibility only.

Migration:
    # Old (deprecated):
    from app.services.openalex_service import openalex_service

    # New (recommended):
    from app.services.openalex import openalex_service
"""
import warnings

warnings.warn(
    "openalex_service is deprecated. "
    "Import from app.services.openalex instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
from .openalex import *  # noqa: F401, F403
from .openalex import openalex_service  # noqa: F401
```

---

# 📋 PHASE 5: Testing
## משך: 60 דקות | תלוי ב: Phase 4

### קבצי בדיקות

```
backend/tests/services/openalex/
├── __init__.py
├── conftest.py         # Fixtures משותפים
├── test_config.py      # בדיקות קונפיגורציה
├── test_utils.py       # בדיקות utils
├── test_scoring.py     # בדיקות scoring
├── test_client.py      # בדיקות client (mocked)
├── test_journals.py    # בדיקות journal operations
├── test_search.py      # בדיקות search
└── test_integration.py # בדיקות אינטגרציה
```

### פקודות הרצה

```bash
# Run all openalex tests
cd backend && python -m pytest tests/services/openalex/ -v

# Run with coverage
cd backend && python -m pytest tests/services/openalex/ -v --cov=app.services.openalex

# Run existing tests to verify backward compat
cd backend && python -m pytest tests/ -v -k "openalex"
```

---

# 📋 PHASE 6: Documentation
## משך: 20 דקות | תלוי ב: Phase 5

### פעולות

1. עדכון `CLAUDE.md` עם מבנה חדש
2. יצירת `backend/app/services/openalex/README.md`
3. עדכון `PROJECT_MEMORY.md`

---

# ✅ קריטריונים להצלחה

- [ ] קובץ מקורי פוצל ל-9 מודולים
- [ ] כל מודול < 250 שורות
- [ ] כל הבדיקות הקיימות עוברות
- [ ] בדיקות יחידה חדשות לכל מודול
- [ ] אין שינויים שוברים ל-API
- [ ] הפרדת אחריות ברורה
- [ ] תיעוד מלא
- [ ] Backward compatibility עובד

---

# 🔄 Rollback Plan

```bash
# אם יש בעיות:
git checkout main -- backend/app/services/openalex_service.py
rm -rf backend/app/services/openalex/
```

---

# 🚀 פקודת הרצה

```bash
# Option 1: Sequential execution
git checkout -b refactor/openalex-service

# Execute phases
# Phase 0: Analysis (manual)
# Phase 1-4: Code changes
# Phase 5: Testing
# Phase 6: Documentation

git add .
git commit -m "refactor(openalex): split 1,231-line monolith into clean modules"
```
