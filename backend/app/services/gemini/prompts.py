"""
Prompt templates for Gemini LLM service.

Phase 3 additions:
- Paper analysis prompts for enrichment
- Abbreviation expansion prompts
- Cross-discipline detection prompts
- Hebrew/multilingual support prompts
"""
from typing import List, Dict, Any


# =============================================================================
# PHASE 3: Paper Analysis Prompts
# =============================================================================

PAPER_ANALYSIS_PROMPT = """You are an academic research analyst. Analyze this paper and extract structured information.

**Paper Title:**
{title}

**Abstract:**
{abstract}

**Current Analysis (from OpenAlex):**
- Detected Discipline: {discipline} (confidence: {confidence:.0%})
- Keywords found: {keywords}
- Topics found: {topics_count}

**Your Task:**
Provide additional insights that OpenAlex may have missed:

1. **Additional Keywords** (5-10 specific terms):
   - Focus on methodology, techniques, specific concepts
   - Include field-specific terminology
   - Avoid generic academic terms

2. **Cross-disciplinary Connections**:
   - If this paper bridges multiple fields, list them
   - Explain why each field is relevant

3. **Methodology Type**:
   - Empirical/Theoretical/Review/Meta-analysis/Case Study/Other
   - Specific methods used (e.g., "randomized controlled trial", "machine learning")

4. **Target Audience**:
   - Which researcher communities would benefit?
   - Any niche specializations?

**Output Format (JSON):**
```json
{{
  "additional_keywords": ["keyword1", "keyword2", ...],
  "cross_disciplines": [
    {{"field": "Psychology", "reason": "Uses cognitive models"}}
  ],
  "methodology": {{
    "type": "empirical",
    "specific_methods": ["survey", "factor analysis"]
  }},
  "target_audience": ["developmental psychologists", "education researchers"],
  "confidence_boost": 0.1
}}
```
"""


ABBREVIATION_EXPANSION_PROMPT = """You are an academic terminology expert. Expand these abbreviations in context.

**Paper Title:**
{title}

**Abstract:**
{abstract}

**Detected Discipline:**
{discipline}

**Unknown Abbreviations Found:**
{abbreviations}

**Your Task:**
For each abbreviation, provide:
1. Full expansion
2. Field/context where this term is used
3. Brief definition (1 sentence)

**Output Format (JSON):**
```json
{{
  "expansions": [
    {{
      "abbreviation": "SERT",
      "expansion": "Serotonin Transporter",
      "field": "Neuroscience/Pharmacology",
      "definition": "A protein that transports serotonin from synaptic spaces into presynaptic neurons."
    }}
  ]
}}
```

Only include abbreviations you are confident about. Skip if unsure.
"""


CROSS_DISCIPLINE_PROMPT = """You are an interdisciplinary research analyst. Identify the academic fields this paper spans.

**Paper Title:**
{title}

**Abstract:**
{abstract}

**Primary Discipline Detected:**
{primary_discipline} (confidence: {confidence:.0%})

**Your Task:**
1. List ALL academic disciplines this paper relates to
2. For each, explain the connection and relevance level (primary/secondary/tertiary)
3. Suggest which discipline's journals would be most receptive

**Output Format (JSON):**
```json
{{
  "disciplines": [
    {{
      "name": "Developmental Psychology",
      "level": "primary",
      "connection": "Core focus on child emotional development",
      "journal_types": ["developmental psychology", "child development"]
    }},
    {{
      "name": "Neuroscience",
      "level": "secondary",
      "connection": "Uses fMRI methodology",
      "journal_types": ["cognitive neuroscience", "neuroimaging"]
    }}
  ],
  "is_truly_interdisciplinary": true,
  "recommended_primary_field": "Developmental Psychology"
}}
```
"""


HEBREW_ANALYSIS_PROMPT = """You are a bilingual (Hebrew-English) academic analyst. This paper contains Hebrew text.

**Paper Title:**
{title}

**Abstract (may contain Hebrew):**
{abstract}

**Your Task:**
1. Translate Hebrew portions to English (academic style)
2. Extract keywords in BOTH languages
3. Identify the academic discipline
4. Note any Israel-specific contexts (institutions, regulations, etc.)

**Output Format (JSON):**
```json
{{
  "translation": {{
    "title_en": "English title",
    "abstract_en": "English abstract"
  }},
  "keywords": {{
    "hebrew": ["מילת מפתח1", "מילת מפתח2"],
    "english": ["keyword1", "keyword2"]
  }},
  "discipline": {{
    "name": "Psychology",
    "subfield": "Clinical Psychology"
  }},
  "israel_context": {{
    "has_local_context": true,
    "details": "Mentions Israeli healthcare system regulations"
  }}
}}
```
"""


KEYWORD_ENHANCEMENT_PROMPT = """You are a search optimization expert for academic databases.

**Current Search Query:**
{query}

**Paper Title:**
{title}

**Abstract:**
{abstract}

**Detected Discipline:**
{discipline}

**Current Keywords:**
{current_keywords}

**Your Task:**
Suggest additional search terms that would help find relevant journals. Focus on:
1. Synonyms and related terms
2. Broader/narrower terms (for hierarchical searching)
3. Methodology-specific terms
4. Field-specific jargon

**Output Format (JSON):**
```json
{{
  "enhanced_keywords": [
    {{
      "term": "emotion regulation",
      "type": "synonym",
      "rationale": "Alternative phrasing commonly used"
    }},
    {{
      "term": "affective development",
      "type": "broader",
      "rationale": "Umbrella term that encompasses the topic"
    }}
  ],
  "suggested_search_query": "improved query string",
  "discipline_specific_terms": ["term1", "term2"]
}}
```
"""


# =============================================================================
# Helper Functions for Phase 3 Prompts
# =============================================================================

def generate_paper_analysis_prompt(
    title: str,
    abstract: str,
    discipline: str = "Unknown",
    confidence: float = 0.0,
    keywords: List[str] = None,
    topics_count: int = 0,
) -> str:
    """Generate prompt for comprehensive paper analysis."""
    keywords_str = ", ".join(keywords[:10]) if keywords else "None found"

    return PAPER_ANALYSIS_PROMPT.format(
        title=title[:500],
        abstract=abstract[:2000],
        discipline=discipline,
        confidence=confidence,
        keywords=keywords_str,
        topics_count=topics_count,
    )


def generate_abbreviation_prompt(
    title: str,
    abstract: str,
    discipline: str,
    abbreviations: List[str],
) -> str:
    """Generate prompt for abbreviation expansion."""
    abbrev_str = ", ".join(abbreviations[:15])

    return ABBREVIATION_EXPANSION_PROMPT.format(
        title=title[:500],
        abstract=abstract[:2000],
        discipline=discipline,
        abbreviations=abbrev_str,
    )


def generate_cross_discipline_prompt(
    title: str,
    abstract: str,
    primary_discipline: str,
    confidence: float,
) -> str:
    """Generate prompt for cross-discipline detection."""
    return CROSS_DISCIPLINE_PROMPT.format(
        title=title[:500],
        abstract=abstract[:2000],
        primary_discipline=primary_discipline,
        confidence=confidence,
    )


def generate_hebrew_analysis_prompt(
    title: str,
    abstract: str,
) -> str:
    """Generate prompt for Hebrew text analysis."""
    return HEBREW_ANALYSIS_PROMPT.format(
        title=title[:500],
        abstract=abstract[:2000],
    )


def generate_keyword_enhancement_prompt(
    title: str,
    abstract: str,
    discipline: str,
    current_keywords: List[str],
    query: str = "",
) -> str:
    """Generate prompt for keyword enhancement."""
    keywords_str = ", ".join(current_keywords[:15])

    return KEYWORD_ENHANCEMENT_PROMPT.format(
        query=query or " ".join(current_keywords[:5]),
        title=title[:500],
        abstract=abstract[:2000],
        discipline=discipline,
        current_keywords=keywords_str,
    )


# =============================================================================
# Original Prompts (Journal Explanation)
# =============================================================================

def generate_explanation_prompt(abstract: str, journal: dict) -> str:
    """
    Generate the prompt for Gemini to explain journal fit.

    Args:
        abstract: User's article abstract
        journal: Journal data dict with title, topics, metrics

    Returns:
        Formatted prompt string
    """
    journal_title = journal.get("title", "Unknown Journal")
    topics = ", ".join(journal.get("topics", [])[:5])
    metrics = journal.get("metrics", {})

    impact_info = ""
    if metrics.get("two_yr_mean_citedness"):
        citation_rate = metrics["two_yr_mean_citedness"]
        impact_info = (
            f"- 2-Year Citation Rate: {citation_rate:.1f} (Indicates expected impact)"
        )

    return f"""Act as a senior academic editor assisting a researcher.

**Goal:** Explain briefly and professionally why the journal "{journal_title}" is a strong candidate for the provided abstract.

**Researcher's Abstract:**
"{abstract[:2000]}"

**Journal Data:**
- Core Topics: {topics}
{impact_info}

**Instructions:**
1. Output Language: **English only**.
2. Format: Provide **2-3 concise bullet points**.
3. Content:
   - Connect specific themes/keywords from the abstract directly to the journal's scope.
   - If metrics are high, mention visibility/impact.
   - If it's a specialized journal, mention the fit for niche audiences.
4. Tone: Objective, professional, and helpful. Avoid generic phrases like "I think" or "As an AI".
"""


def get_static_fallback(journal: dict) -> str:
    """
    Generate static fallback explanation when Gemini API fails.

    Args:
        journal: Journal data dict

    Returns:
        Professional static explanation
    """
    topics = ", ".join(journal.get("topics", [])[:3])
    journal_name = journal.get("title", "This journal")

    return (
        f"**Thematic Fit:** {journal_name} publishes extensively on topics matching "
        f"your abstract, specifically: {topics}.\n\n"
        f"**Relevance:** Based on our algorithm, this venue shows high alignment "
        f"with your research keywords."
    )
