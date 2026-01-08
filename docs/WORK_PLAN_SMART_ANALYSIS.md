# תוכנית עבודה: שיפור מנגנון ניתוח וזיהוי מונחים

## 🎯 מטרה
שדרוג מנגנון הניתוח והזיהוי של מונחי מפתח ונושאים ממאמרים אקדמיים, תוך שילוב OpenAlex משופר + Gemini LLM למקרים מורכבים.

---

## 📊 מצב נוכחי vs מצב רצוי

| היבט | מצב נוכחי | מצב רצוי |
|------|-----------|----------|
| חילוץ מונחים | Stopwords + 20 ביטויים קבועים | Keywords דינמיים מ-OpenAlex + LLM |
| זיהוי תחומים | 12 תחומים hardcoded | 252 subfields דינמיים |
| ראשי תיבות | לא מזוהים | Gemini מפענח |
| מאמרים בין-תחומיים | זיהוי חלקי | זיהוי מלא + cross-discipline |
| שפות אחרות | אנגלית בלבד | תמיכה בעברית + שפות נוספות |

---

## 🏗️ ארכיטקטורה חדשה

```
┌─────────────────────────────────────────────────────────────────┐
│                        Smart Analysis Engine                     │
└─────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Layer 1     │    │    Layer 2      │    │    Layer 3      │
│  OpenAlex     │───►│   Analysis      │───►│   Gemini LLM    │
│  Enhanced     │    │   Orchestrator  │    │   Enrichment    │
└───────────────┘    └─────────────────┘    └─────────────────┘
       │                     │                      │
       ▼                     ▼                      ▼
  • Topics API          • Confidence           • Abbreviations
  • Keywords from         scoring              • Missing terms
    Works               • Trigger              • Cross-discipline
  • Concepts              detection            • Language support
```

---

## 📅 שלבי ביצוע

### Phase 1: OpenAlex Enhanced (שבוע 1-2)
**מטרה:** לשפר את חילוץ המונחים והנושאים ישירות מ-OpenAlex

#### Task 1.1: Topics API Direct Integration
**קבצים:** `backend/app/services/openalex/topics.py` (חדש)

```python
# יצירת מודול חדש לעבודה ישירה עם Topics API
class TopicsService:
    async def search_topics(query: str) -> List[Topic]
    async def get_topic_hierarchy(topic_id: str) -> TopicHierarchy
    async def find_related_topics(topic_ids: List[str]) -> List[Topic]
```

**פעולות:**
- [ ] יצירת `topics.py` עם פונקציות לעבודה ישירה עם Topics API
- [ ] הוספת חיפוש Topics לפי טקסט
- [ ] שליפת היררכיית Topics (Domain → Field → Subfield → Topic)
- [ ] בדיקות יחידה

#### Task 1.2: Keywords Extraction from Works
**קבצים:** `backend/app/services/openalex/keywords.py` (חדש)

```python
# חילוץ Keywords מ-Works שחזרו מ-OpenAlex
class KeywordsExtractor:
    def extract_from_works(works: List[dict]) -> List[Keyword]
    def merge_with_user_keywords(extracted: List, user: List) -> List
    def rank_keywords(keywords: List) -> List[RankedKeyword]
```

**פעולות:**
- [ ] יצירת `keywords.py` לחילוץ keywords מ-Works
- [ ] שקלול keywords לפי score ותדירות
- [ ] מיזוג עם מילות המפתח של המשתמש
- [ ] בדיקות יחידה

#### Task 1.3: Concepts Integration
**קבצים:** `backend/app/services/openalex/concepts.py` (חדש)

```python
# שימוש ב-x_concepts מ-Works לשיפור הדיוק
class ConceptsAnalyzer:
    def aggregate_concepts(works: List[dict]) -> List[Concept]
    def filter_by_relevance(concepts: List, threshold: float) -> List
```

**פעולות:**
- [ ] יצירת `concepts.py` לניתוח concepts
- [ ] אגרגציה של concepts מ-Works דומים
- [ ] סינון לפי relevance score
- [ ] בדיקות יחידה

#### Task 1.4: Refactor Search Terms Extraction
**קבצים:** `backend/app/services/openalex/utils.py`

**פעולות:**
- [ ] הסרת stopwords בעייתיים ("analysis", "method", "results")
- [ ] הוספת זיהוי bigrams/trigrams אוטומטי
- [ ] שילוב keywords מ-OpenAlex
- [ ] עדכון בדיקות

---

### Phase 2: Analysis Orchestrator (שבוע 2-3)
**מטרה:** בניית מנגנון תזמור שמחליט מתי להפעיל LLM

#### Task 2.1: Create SmartAnalyzer Class
**קבצים:** `backend/app/services/analysis/smart_analyzer.py` (חדש)

```python
@dataclass
class AnalysisResult:
    keywords: List[RankedKeyword]
    topics: List[DetectedTopic]
    disciplines: List[DetectedDiscipline]
    confidence: float
    needs_llm_enrichment: bool
    enrichment_reasons: List[str]

class SmartAnalyzer:
    """
    Main orchestrator for paper analysis.
    Combines OpenAlex + optional Gemini enrichment.
    """

    async def analyze(
        self,
        title: str,
        abstract: str,
        user_keywords: List[str] = None,
    ) -> AnalysisResult:
        # Step 1: OpenAlex analysis
        # Step 2: Confidence scoring
        # Step 3: LLM trigger detection
        # Step 4: Optional Gemini enrichment
        pass
```

**פעולות:**
- [ ] יצירת `smart_analyzer.py`
- [ ] הגדרת `AnalysisResult` dataclass
- [ ] מימוש לוגיקת התזמור
- [ ] בדיקות יחידה

#### Task 2.2: Confidence Scoring System
**קבצים:** `backend/app/services/analysis/confidence.py` (חדש)

```python
class ConfidenceScorer:
    """
    Calculate confidence in analysis results.
    Used to decide if LLM enrichment is needed.
    """

    def score(self, result: OpenAlexResult) -> ConfidenceScore:
        factors = {
            "topics_found": len(result.topics) >= 3,
            "keywords_quality": self._assess_keyword_quality(result.keywords),
            "discipline_clarity": result.top_discipline_confidence > 0.4,
            "works_found": result.similar_works_count >= 20,
        }
        return ConfidenceScore(...)
```

**פעולות:**
- [ ] יצירת `confidence.py`
- [ ] הגדרת קריטריונים לביטחון
- [ ] מימוש חישוב confidence score
- [ ] בדיקות יחידה

#### Task 2.3: LLM Trigger Detection
**קבצים:** `backend/app/services/analysis/triggers.py` (חדש)

```python
class LLMTriggerDetector:
    """
    Detect when LLM enrichment is needed.
    """

    TRIGGERS = [
        "low_confidence",           # confidence < 0.5
        "abbreviations_detected",   # OAB, COPD, etc.
        "cross_disciplinary",       # Multiple distinct fields
        "non_english",              # Hebrew, Arabic, etc.
        "few_topics",               # < 2 topics found
        "ambiguous_terms",          # Terms with multiple meanings
    ]

    def detect(
        self,
        text: str,
        openalex_result: OpenAlexResult,
    ) -> List[TriggerResult]:
        pass
```

**פעולות:**
- [ ] יצירת `triggers.py`
- [ ] מימוש כל trigger בנפרד
- [ ] בדיקות לכל trigger

---

### Phase 3: Gemini LLM Enrichment (שבוע 3-4)
**מטרה:** הוספת שכבת Gemini לניתוח מתקדם

#### Task 3.1: Paper Analysis Prompt
**קבצים:** `backend/app/services/gemini/prompts.py`

```python
PAPER_ANALYSIS_PROMPT = """
You are an academic paper analyzer. Extract key information from this paper.

TITLE: {title}
ABSTRACT: {abstract}

Respond with valid JSON only:
{{
  "primary_field": "string - main academic field",
  "subfields": ["array of specific subfields"],
  "key_terms": ["max 10 important technical terms"],
  "methodology": "RCT|cohort|meta-analysis|qualitative|case-study|review|other",
  "abbreviations": {{"abbr": "full form"}},
  "cross_disciplinary": boolean,
  "cross_disciplines": ["if cross_disciplinary, list the fields"],
  "language_detected": "en|he|ar|...",
  "suggested_search_queries": ["2-3 optimized search queries for finding journals"]
}}

Rules:
1. Only extract what's explicitly stated or clearly implied
2. Do NOT hallucinate or invent terms
3. Expand ALL abbreviations you recognize
4. Be concise and precise
"""
```

**פעולות:**
- [ ] הוספת `PAPER_ANALYSIS_PROMPT`
- [ ] הוספת `ABBREVIATION_EXPANSION_PROMPT` (קצר יותר, זול יותר)
- [ ] בדיקות עם מאמרים לדוגמה

#### Task 3.2: Gemini Analysis Service
**קבצים:** `backend/app/services/gemini/analysis.py` (חדש)

```python
class GeminiAnalysisService:
    """
    Gemini-based paper analysis for complex cases.
    """

    async def analyze_paper(
        self,
        title: str,
        abstract: str,
    ) -> GeminiAnalysisResult:
        """Full paper analysis - use sparingly."""
        pass

    async def expand_abbreviations(
        self,
        text: str,
        abbreviations: List[str],
    ) -> Dict[str, str]:
        """Lightweight abbreviation expansion."""
        pass

    async def detect_cross_disciplines(
        self,
        title: str,
        abstract: str,
        detected_disciplines: List[str],
    ) -> List[CrossDisciplineResult]:
        """Identify cross-disciplinary aspects."""
        pass
```

**פעולות:**
- [ ] יצירת `analysis.py` תחת gemini
- [ ] מימוש `analyze_paper`
- [ ] מימוש `expand_abbreviations`
- [ ] מימוש `detect_cross_disciplines`
- [ ] הוספת caching (כמו ב-explanation)
- [ ] בדיקות יחידה

#### Task 3.3: Abbreviation Detection
**קבצים:** `backend/app/services/analysis/abbreviations.py` (חדש)

```python
class AbbreviationDetector:
    """
    Detect academic abbreviations that need expansion.
    """

    # Common patterns: ALL CAPS 2-6 letters
    PATTERN = r'\b[A-Z]{2,6}\b'

    # Known abbreviations (no need for LLM)
    KNOWN = {
        "RCT": "Randomized Controlled Trial",
        "COPD": "Chronic Obstructive Pulmonary Disease",
        "BMI": "Body Mass Index",
        # ... more
    }

    def detect(self, text: str) -> List[Abbreviation]:
        """Find abbreviations in text."""
        pass

    def expand_known(self, abbrs: List[str]) -> Dict[str, str]:
        """Expand known abbreviations without LLM."""
        pass

    def get_unknown(self, abbrs: List[str]) -> List[str]:
        """Get abbreviations that need LLM expansion."""
        pass
```

**פעולות:**
- [ ] יצירת `abbreviations.py`
- [ ] בניית מאגר ראשי תיבות נפוצים
- [ ] מימוש זיהוי ומיון
- [ ] בדיקות יחידה

---

### Phase 4: Integration & Testing (שבוע 4-5)
**מטרה:** שילוב כל הרכיבים ובדיקות מקיפות

#### Task 4.1: Update Search Flow
**קבצים:** `backend/app/services/openalex/search.py`

```python
# עדכון search_journals_by_text להשתמש ב-SmartAnalyzer
async def search_journals_by_text(
    title: str,
    abstract: str,
    keywords: List[str] = None,
    prefer_open_access: bool = False,
) -> SearchResult:
    # Step 1: Smart Analysis (OpenAlex + optional Gemini)
    analyzer = SmartAnalyzer()
    analysis = await analyzer.analyze(title, abstract, keywords)

    # Step 2: Use enriched data for journal search
    # ...
```

**פעולות:**
- [ ] עדכון `search_journals_by_text`
- [ ] שילוב `SmartAnalyzer`
- [ ] עדכון Response model עם מידע נוסף
- [ ] בדיקות אינטגרציה

#### Task 4.2: API Response Enhancement
**קבצים:** `backend/app/models/journal.py`

```python
class AnalysisMetadata(BaseModel):
    """Metadata about the analysis process."""
    keywords_extracted: List[str]
    topics_detected: List[str]
    disciplines: List[DetectedDisciplineInfo]
    confidence_score: float
    llm_used: bool
    llm_triggers: List[str] = []
    abbreviations_expanded: Dict[str, str] = {}
    processing_time_ms: int
```

**פעולות:**
- [ ] הוספת `AnalysisMetadata` model
- [ ] עדכון `SearchResponse` לכלול metadata
- [ ] עדכון API endpoint
- [ ] עדכון תיעוד API

#### Task 4.3: Comprehensive Testing
**קבצים:** `backend/tests/test_smart_analysis.py` (חדש)

```python
# Test cases:
# 1. Simple English paper - OpenAlex only
# 2. Paper with abbreviations - LLM triggered
# 3. Cross-disciplinary paper - LLM triggered
# 4. Hebrew abstract - LLM triggered
# 5. High confidence - no LLM
# 6. Low confidence - LLM triggered
# 7. Performance benchmark
```

**פעולות:**
- [ ] יצירת test suite מקיף
- [ ] בדיקות לכל trigger
- [ ] בדיקות ביצועים
- [ ] בדיקות עלות (mock Gemini calls)

---

### Phase 5: Monitoring & Optimization (שבוע 5-6)
**מטרה:** מעקב, אופטימיזציה ושיפור מתמיד

#### Task 5.1: Analytics & Logging
**קבצים:** `backend/app/services/analysis/analytics.py` (חדש)

```python
class AnalysisAnalytics:
    """Track analysis performance and costs."""

    async def log_analysis(
        self,
        result: AnalysisResult,
        processing_time: float,
        llm_used: bool,
    ):
        pass

    async def get_stats(self, days: int = 7) -> AnalyticsReport:
        """Get usage statistics."""
        pass
```

**פעולות:**
- [ ] יצירת טבלת analytics ב-Supabase
- [ ] מימוש logging
- [ ] דשבורד סטטיסטיקות

#### Task 5.2: Cost Monitoring
**קבצים:** `backend/app/services/gemini/cost_tracker.py` (חדש)

```python
class GeminiCostTracker:
    """Track Gemini API usage and costs."""

    # Gemini Flash pricing (as of Jan 2025)
    COST_PER_1K_INPUT_TOKENS = 0.000075
    COST_PER_1K_OUTPUT_TOKENS = 0.0003

    async def track_call(self, input_tokens: int, output_tokens: int):
        pass

    async def get_daily_cost(self) -> float:
        pass

    async def check_budget(self, daily_limit: float = 10.0) -> bool:
        pass
```

**פעולות:**
- [ ] מימוש מעקב עלויות
- [ ] הגדרת התראות על חריגה
- [ ] דשבורד עלויות

#### Task 5.3: Feature Flags
**קבצים:** `backend/app/core/config.py`

```python
# הוספה ל-Settings
class Settings(BaseSettings):
    # ... existing

    # Smart Analysis settings
    smart_analysis_enabled: bool = True
    smart_analysis_llm_enabled: bool = True
    smart_analysis_confidence_threshold: float = 0.5
    smart_analysis_daily_llm_budget: float = 10.0  # USD
```

**פעולות:**
- [ ] הוספת feature flags
- [ ] מימוש on/off לכל רכיב
- [ ] תיעוד

---

## 📁 מבנה קבצים חדש

```
backend/app/services/
├── analysis/
│   ├── __init__.py
│   ├── smart_analyzer.py      # NEW - Main orchestrator
│   ├── confidence.py          # NEW - Confidence scoring
│   ├── triggers.py            # NEW - LLM trigger detection
│   ├── abbreviations.py       # NEW - Abbreviation handling
│   ├── analytics.py           # NEW - Usage analytics
│   ├── article_type_detector.py
│   ├── discipline_detector.py
│   ├── hybrid_detector.py
│   ├── topic_validator.py
│   └── universal_detector.py
│
├── gemini/
│   ├── __init__.py
│   ├── service.py             # Existing - explanations
│   ├── analysis.py            # NEW - Paper analysis
│   ├── prompts.py             # Updated - new prompts
│   └── cost_tracker.py        # NEW - Cost monitoring
│
├── openalex/
│   ├── __init__.py
│   ├── client.py
│   ├── config.py
│   ├── constants.py
│   ├── journals.py
│   ├── scoring.py
│   ├── search.py              # Updated - use SmartAnalyzer
│   ├── service.py
│   ├── universal_search.py
│   ├── utils.py               # Updated - better term extraction
│   ├── topics.py              # NEW - Direct Topics API
│   ├── keywords.py            # NEW - Keywords extraction
│   └── concepts.py            # NEW - Concepts analysis
```

---

## 📊 מטריקות הצלחה

| מטריקה | יעד | איך נמדוד |
|--------|-----|-----------|
| דיוק זיהוי תחומים | >85% | בדיקה ידנית על 100 מאמרים |
| כיסוי תחומים | 252 subfields | בדיקת תמיכה בכל התחומים |
| זמן תגובה (בלי LLM) | <2 שניות | מדידת p95 |
| זמן תגובה (עם LLM) | <5 שניות | מדידת p95 |
| אחוז קריאות LLM | <25% | מעקב analytics |
| עלות LLM יומית | <$5 | מעקב cost tracker |
| שביעות רצון | >4/5 | feedback מהמשתמשים |

---

## ⚠️ סיכונים ומיטיגציה

| סיכון | הסתברות | השפעה | מיטיגציה |
|-------|---------|--------|----------|
| עלויות Gemini גבוהות | בינונית | גבוהה | Budget limits + triggers חכמים |
| Latency גבוה | בינונית | בינונית | Caching + async |
| OpenAlex downtime | נמוכה | גבוהה | Fallback ל-keyword detection |
| Gemini hallucinations | בינונית | בינונית | Validation + temperature נמוך |
| שינויי API | נמוכה | בינונית | Version pinning + monitoring |

---

## 🚀 לוח זמנים מסכם

| שבוע | Phase | משימות עיקריות |
|------|-------|-----------------|
| 1-2 | Phase 1 | OpenAlex Enhanced (Topics, Keywords, Concepts) |
| 2-3 | Phase 2 | Analysis Orchestrator (SmartAnalyzer, Confidence, Triggers) |
| 3-4 | Phase 3 | Gemini LLM Enrichment |
| 4-5 | Phase 4 | Integration & Testing |
| 5-6 | Phase 5 | Monitoring & Optimization |

---

## 🗑️ Phase 0: ניקוי קוד ישן (לפני התחלת הפיתוח!)

**חשוב מאוד:** לפני שמתחילים לבנות את הארכיטקטורה החדשה, יש למחוק את הקוד הישן כדי למנוע כפילויות ובלבול.

### קבצים למחיקה מלאה

| קובץ | סיבה למחיקה |
|------|-------------|
| `backend/app/services/openalex_service.py` | Deprecated wrapper - מוחלף ב-SmartAnalyzer |
| `backend/app/services/analysis/discipline_detector.py` | רשימות hardcoded - מוחלף ב-OpenAlex Topics API |
| `backend/app/services/analysis/hybrid_detector.py` | לוגיקה ישנה - מוחלף ב-SmartAnalyzer |
| `backend/app/services/analysis/universal_detector.py` | מוחלף ב-Topics API ישיר |
| `backend/app/services/analysis/dynamic_stats.py` | לבדוק אם בשימוש - אם לא, למחוק |

### קבצים לעדכון (הסרת קוד מת)

| קובץ | מה להסיר |
|------|----------|
| `backend/app/services/openalex/constants.py` | `DISCIPLINE_KEYWORDS` - רשימות hardcoded של 12 תחומים |
| `backend/app/services/openalex/constants.py` | `RELEVANT_TOPIC_KEYWORDS` - רשימות סטטיות |
| `backend/app/services/openalex/constants.py` | `KEY_JOURNALS_BY_DISCIPLINE` - רשימות כ"ע קבועות |
| `backend/app/services/openalex/utils.py` | `STOPWORDS` - להחליף ברשימה חכמה יותר |
| `backend/app/services/openalex/utils.py` | `important_phrases` - רשימת 20 ביטויים קבועים |
| `backend/app/services/openalex/utils.py` | `detect_discipline()` - פונקציה ישנה |

### קבצים לשמירה (בשימוש פעיל)

| קובץ | סיבה לשמירה |
|------|-------------|
| `backend/app/services/openalex/client.py` | ✅ OpenAlex API client - בסיס טוב |
| `backend/app/services/openalex/search.py` | ✅ לוגיקת חיפוש כ"ע - לעדכן לשימוש ב-SmartAnalyzer |
| `backend/app/services/openalex/scoring.py` | ✅ אלגוריתם דירוג - לשמור ולשפר |
| `backend/app/services/openalex/journals.py` | ✅ המרת נתונים - בסדר |
| `backend/app/services/analysis/article_type_detector.py` | ✅ זיהוי סוג מאמר - שימושי |
| `backend/app/services/analysis/topic_validator.py` | ✅ ולידציה - שימושי |
| `backend/app/services/gemini/service.py` | ✅ Gemini explanations - קיים ועובד |

### תהליך הניקוי

```
שלב 0.1: גיבוי
├── ליצור branch חדש: feature/smart-analysis
├── לתעד את מבנה הקבצים הנוכחי
└── לוודא שיש גיבוי מלא

שלב 0.2: מחיקת קבצים
├── למחוק את הקבצים המיועדים למחיקה
├── להסיר imports מיותרים
└── לעדכן __init__.py files

שלב 0.3: עדכון references
├── לחפש את כל ה-imports של הקבצים שנמחקו
├── לעדכן או להסיר references
└── לוודא שהקוד עדיין מתקמפל

שלב 0.4: ניקוי קוד מת בקבצים קיימים
├── להסיר פונקציות שלא בשימוש
├── להסיר constants מיותרים
└── להסיר comments על קוד ישן

שלב 0.5: בדיקות
├── להריץ את כל הטסטים
├── לתקן טסטים שנשברו
└── למחוק טסטים של קוד שנמחק
```

### Checklist לניקוי

- [ ] גיבוי הקוד הנוכחי (branch/tag)
- [ ] מחיקת `openalex_service.py`
- [ ] מחיקת `discipline_detector.py`
- [ ] מחיקת `hybrid_detector.py`
- [ ] מחיקת `universal_detector.py`
- [ ] בדיקה ומחיקת `dynamic_stats.py` (אם לא בשימוש)
- [ ] ניקוי `constants.py` מרשימות hardcoded
- [ ] ניקוי `utils.py` מפונקציות ישנות
- [ ] עדכון כל ה-imports בפרויקט
- [ ] עדכון `__init__.py` files
- [ ] הרצת טסטים ותיקון שבירות
- [ ] מחיקת טסטים של קוד שנמחק
- [ ] Code review לוודא שלא נשאר קוד מת

### ⚠️ אזהרות חשובות

1. **לא למחוק לפני שיש תחליף עובד** - Phase 0 מתבצע במקביל ל-Phase 1
2. **לשמור על backward compatibility ב-API** - רק הקוד הפנימי משתנה
3. **לתעד כל שינוי** - להוסיף הערות ב-commit messages
4. **לבדוק תלויות** - לוודא שאף קובץ אחר לא תלוי בקוד שנמחק

---

## 📁 מבנה קבצים - לפני ואחרי

### לפני (מצב נוכחי)
```
backend/app/services/
├── analysis/
│   ├── __init__.py
│   ├── article_type_detector.py  ✅ נשאר
│   ├── discipline_detector.py    ❌ נמחק
│   ├── dynamic_stats.py          ❓ לבדוק
│   ├── hybrid_detector.py        ❌ נמחק
│   ├── topic_validator.py        ✅ נשאר
│   └── universal_detector.py     ❌ נמחק
│
├── openalex/
│   ├── __init__.py
│   ├── client.py                 ✅ נשאר
│   ├── config.py                 ✅ נשאר
│   ├── constants.py              🔄 מנוקה
│   ├── journals.py               ✅ נשאר
│   ├── scoring.py                ✅ נשאר
│   ├── search.py                 🔄 מעודכן
│   ├── service.py                ✅ נשאר
│   ├── universal_search.py       ❓ לבדוק
│   └── utils.py                  🔄 מנוקה
│
├── openalex_service.py           ❌ נמחק
└── ...
```

### אחרי (מצב סופי)
```
backend/app/services/
├── analysis/
│   ├── __init__.py
│   ├── smart_analyzer.py         🆕 חדש - Main orchestrator
│   ├── confidence.py             🆕 חדש
│   ├── triggers.py               🆕 חדש
│   ├── abbreviations.py          🆕 חדש
│   ├── analytics.py              🆕 חדש
│   ├── article_type_detector.py  ✅ קיים
│   └── topic_validator.py        ✅ קיים
│
├── openalex/
│   ├── __init__.py
│   ├── client.py                 ✅ קיים
│   ├── config.py                 ✅ קיים
│   ├── constants.py              🔄 מנוקה (רק קבועים הכרחיים)
│   ├── journals.py               ✅ קיים
│   ├── scoring.py                ✅ קיים
│   ├── search.py                 🔄 מעודכן (משתמש ב-SmartAnalyzer)
│   ├── service.py                ✅ קיים
│   ├── utils.py                  🔄 מנוקה
│   ├── topics.py                 🆕 חדש - Topics API
│   ├── keywords.py               🆕 חדש - Keywords extraction
│   └── concepts.py               🆕 חדש - Concepts analysis
│
├── gemini/
│   ├── __init__.py
│   ├── service.py                ✅ קיים
│   ├── analysis.py               🆕 חדש
│   ├── prompts.py                🔄 מעודכן
│   └── cost_tracker.py           🆕 חדש
```

---

## 📝 הערות נוספות

1. **NO Backwards Compatibility בקוד פנימי** - מחליפים לגמרי, לא שומרים קוד ישן
2. **API Backwards Compatibility** - ה-API החיצוני נשאר תואם, רק מוסיפים שדות
3. **Gradual Rollout** - Feature flag למעבר הדרגתי
4. **Documentation** - לעדכן API docs עם כל שינוי
5. **Clean Code** - אין קוד מת, אין כפילויות, אין רשימות hardcoded

---

## 🤖 מיפוי סוכנים ופקודות לביצוע

### סוכנים זמינים בפרויקט

| סוכן | תפקיד | מיקום |
|------|-------|-------|
| **@orchestrator** | תזמור ראשי וניהול workflow | `.claude/agents/orchestrator.md` |
| **@parallel-work-agent** | עבודה מקבילית עם Git Worktrees | `.claude/agents/parallel-work-agent.md` |
| **@backend-agent** | פיתוח Backend (FastAPI/Python) | `.claude/agents/backend-agent.md` |
| **@qa-agent** | בדיקות איכות וקוד | `.claude/agents/qa-agent.md` |
| **@docs-agent** | עדכון תיעוד | `.claude/agents/docs-agent.md` |
| **@api-sync-agent** | סנכרון Backend/Frontend | `.claude/agents/api-sync-agent.md` |
| **@deploy-checker** | בדיקות טרום-פריסה | `.claude/agents/deploy-checker.md` |

### פקודות זמינות

| פקודה | תיאור | מיקום |
|-------|-------|-------|
| `/project:refactor` | ריפקטורינג קוד | `.claude/commands/refactor.md` |
| `/project:new-feature` | פיתוח פיצ'ר חדש | `.claude/commands/new-feature.md` |
| `/project:fix-bug` | תיקון באגים | `.claude/commands/fix-bug.md` |
| `/project:pre-deploy` | בדיקות טרום-פריסה | `.claude/commands/pre-deploy.md` |
| `/project:parallel-tasks` | הרצת משימות במקביל | `.claude/commands/parallel-tasks.md` |

---

## 🎭 תוכנית ביצוע עם סוכנים

### Phase 0: ניקוי קוד ישן

```
@orchestrator
    │
    ├── פקודה: /project:refactor "ניקוי ארכיטקטורת ניתוח ישנה"
    │
    ├── @backend-agent: מחיקת קבצים
    │   ├── discipline_detector.py
    │   ├── hybrid_detector.py
    │   ├── universal_detector.py
    │   └── openalex_service.py
    │
    ├── @backend-agent: ניקוי קוד מת
    │   ├── constants.py (הסרת DISCIPLINE_KEYWORDS)
    │   └── utils.py (הסרת detect_discipline)
    │
    └── @qa-agent: וידוא קומפילציה ובדיקות
```

### Phase 1-2: בניית רכיבים (עבודה מקבילית)

```
@orchestrator → @parallel-work-agent
    │
    ├── 📁 Worktree A: feature/openalex-enhanced
    │   │
    │   └── @backend-agent:
    │       ├── topics.py (Topics API)
    │       ├── keywords.py (Keywords extraction)
    │       └── concepts.py (Concepts analysis)
    │
    ├── 📁 Worktree B: feature/smart-analyzer
    │   │
    │   └── @backend-agent:
    │       ├── smart_analyzer.py
    │       ├── confidence.py
    │       └── triggers.py
    │
    ├── @qa-agent: בדיקה לכל worktree בנפרד
    │
    └── Merge: @parallel-work-agent מאחד את ה-branches
```

### Phase 3: Gemini Integration

```
@orchestrator
    │
    ├── @backend-agent:
    │   ├── prompts.py (עדכון)
    │   ├── analysis.py (חדש)
    │   ├── abbreviations.py (חדש)
    │   └── cost_tracker.py (חדש)
    │
    └── @qa-agent: בדיקות אבטחה (API keys, secrets)
```

### Phase 4: אינטגרציה

```
@orchestrator
    │
    ├── @backend-agent: עדכון search.py
    │
    ├── @api-sync-agent: וידוא API תקין
    │
    ├── @qa-agent: בדיקות מקיפות
    │   ├── Unit tests
    │   ├── Integration tests
    │   └── Performance tests
    │
    └── פקודה: /project:pre-deploy
```

### Phase 5: סיום ותיעוד

```
@orchestrator
    │
    ├── @docs-agent:
    │   ├── עדכון CLAUDE.md
    │   ├── עדכון API documentation
    │   └── עדכון PROJECT_MEMORY.md
    │
    ├── @deploy-checker: בדיקות סופיות
    │
    └── סיכום ו-merge ל-main
```

---

## 🔄 תרשים זרימה מלא

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              START                                           │
│                    git checkout -b feature/smart-analysis                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 0: ניקוי                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ @orchestrator → /project:refactor                                    │    │
│  │     │                                                                │    │
│  │     ├── @backend-agent: מחיקת קבצים ישנים                           │    │
│  │     └── @qa-agent: וידוא קומפילציה                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  📋 Commit: "refactor: remove legacy analysis code"                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1-2: בנייה (PARALLEL)                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ @parallel-work-agent                                                 │    │
│  │     │                                                                │    │
│  │     ├── Worktree A ──► @backend-agent ──► topics.py, keywords.py    │    │
│  │     │                                                                │    │
│  │     └── Worktree B ──► @backend-agent ──► smart_analyzer.py         │    │
│  │                                                                      │    │
│  │     @qa-agent: בדיקות לכל worktree                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  📋 Commits: "feat: add OpenAlex Topics API", "feat: add SmartAnalyzer"     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: Gemini                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ @backend-agent: analysis.py, abbreviations.py, cost_tracker.py      │    │
│  │ @qa-agent: security review                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  📋 Commit: "feat: add Gemini LLM enrichment for paper analysis"            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: אינטגרציה                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ @backend-agent: עדכון search.py                                     │    │
│  │ @api-sync-agent: וידוא API                                          │    │
│  │ @qa-agent: full test suite                                          │    │
│  │ /project:pre-deploy                                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  📋 Commit: "feat: integrate SmartAnalyzer into search flow"                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 5: סיום                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ @docs-agent: עדכון תיעוד                                            │    │
│  │ @deploy-checker: final checks                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  📋 Commit: "docs: update documentation for Smart Analysis Engine"          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MERGE TO MAIN                                   │
│                         Create Pull Request                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 פקודות להפעלה

### התחלת העבודה

```bash
# 1. יצירת branch ראשי
git checkout -b feature/smart-analysis

# 2. הפעלת Phase 0
# Call @orchestrator with:
# "התחל Phase 0 מתוכנית WORK_PLAN_SMART_ANALYSIS.md - ניקוי קוד ישן"

# 3. הפעלת Phase 1-2 (מקביל)
# Call @parallel-work-agent with:
# "הגדר worktrees לפי תוכנית WORK_PLAN_SMART_ANALYSIS.md Phase 1-2"
```

### בדיקת התקדמות

```bash
# רשימת worktrees פעילים
git worktree list

# סטטוס בכל worktree
cd ../find-my-journal-openalex && git status
cd ../find-my-journal-analyzer && git status
```

### סיום וניקוי

```bash
# מיזוג worktrees
git checkout feature/smart-analysis
git merge feature/openalex-enhanced
git merge feature/smart-analyzer

# ניקוי worktrees
git worktree remove ../find-my-journal-openalex
git worktree remove ../find-my-journal-analyzer
git worktree prune
```

---

*נוצר: ינואר 2026*
*גרסה: 1.2 - נוסף מיפוי סוכנים ופקודות*
