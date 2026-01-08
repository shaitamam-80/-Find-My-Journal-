"""
OpenAlex Utility Functions

Shared helpers for text processing.

Note: Discipline detection now uses OpenAlex's ML classification directly
via get_topics_from_similar_works() in search.py.
"""
import re
from typing import List, Set, Tuple


# Stopwords for search term extraction
# Includes common English stopwords + generic academic terms
STOPWORDS: Set[str] = {
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
    # Additional generic academic terms to filter
    "approach",
    "methods",
    "methodology",
    "introduction",
    "background",
    "conclusion",
    "discussion",
    "objective",
    "objectives",
    "aim",
    "aims",
    "purpose",
    "review",
    "systematic",
    "evidence",
    "model",
    "models",
    "system",
    "systems",
    "novel",
    "new",
    "proposed",
    "effect",
    "effects",
    "impact",
    "role",
    "case",
    "implications",
    "future",
    "current",
    "recent",
    "application",
    "applications",
    "development",
    "evaluation",
    "assessment",
    "investigation",
    "understanding",
    "exploring",
    "examining",
    "investigating",
    "determining",
    "identifying",
    "comparing",
    "evaluating",
    "assessing",
    "analyzing",
    "present",
    "presents",
    "presented",
    "show",
    "shows",
    "showed",
    "demonstrate",
    "demonstrates",
    "demonstrated",
    "report",
    "reports",
    "reported",
    "focus",
    "focuses",
    "focused",
    "examine",
    "examines",
    "examined",
    "investigate",
    "investigates",
    "investigated",
}


def extract_bigrams(words: List[str]) -> List[str]:
    """
    Extract meaningful bigrams from word list.

    Args:
        words: List of cleaned words.

    Returns:
        List of bigrams that appear meaningful.
    """
    if len(words) < 2:
        return []

    bigrams = []
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        # Skip if either is a stopword
        if w1 in STOPWORDS or w2 in STOPWORDS:
            continue
        # Skip if either is too short
        if len(w1) < 3 or len(w2) < 3:
            continue
        bigrams.append(f"{w1} {w2}")

    return bigrams


def extract_trigrams(words: List[str]) -> List[str]:
    """
    Extract meaningful trigrams from word list.

    Args:
        words: List of cleaned words.

    Returns:
        List of trigrams that appear meaningful.
    """
    if len(words) < 3:
        return []

    trigrams = []
    for i in range(len(words) - 2):
        w1, w2, w3 = words[i], words[i + 1], words[i + 2]
        # Middle word can be a stopword (e.g., "machine for learning")
        # but first and last should be meaningful
        if w1 in STOPWORDS or w3 in STOPWORDS:
            continue
        if len(w1) < 3 or len(w3) < 3:
            continue
        trigrams.append(f"{w1} {w2} {w3}")

    return trigrams


def extract_search_terms(
    text: str,
    keywords: List[str],
    max_terms: int = 10,
    include_ngrams: bool = True,
) -> List[str]:
    """
    Extract important search terms from text.

    Includes bigrams and trigrams for better phrase matching.
    Automatically detects n-grams from the text.

    Args:
        text: Combined title and abstract text.
        keywords: User-provided keywords to prioritize.
        max_terms: Maximum number of terms to return.
        include_ngrams: Whether to include auto-detected bigrams/trigrams.

    Returns:
        List of search terms, keywords first.
    """
    terms: List[str] = []
    terms_lower: Set[str] = set()

    # Add user keywords first (highest priority)
    for kw in keywords:
        kw_clean = kw.strip()
        if kw_clean and kw_clean.lower() not in terms_lower:
            terms.append(kw_clean)
            terms_lower.add(kw_clean.lower())

    text_lower = text.lower()

    # Clean text: remove special chars but keep spaces
    clean_text = re.sub(r"[^\w\s-]", " ", text_lower)
    words = [w for w in clean_text.split() if len(w) > 2]

    # Important academic phrases to look for (known high-value phrases)
    important_phrases = [
        "child development",
        "infant development",
        "social emotional",
        "social-emotional",
        "emotion regulation",
        "emotional regulation",
        "machine learning",
        "deep learning",
        "neural network",
        "artificial intelligence",
        "natural language processing",
        "clinical trial",
        "randomized controlled",
        "systematic review",
        "meta analysis",
        "meta-analysis",
        "confirmatory factor",
        "structural equation",
        "factor analysis",
        "psychometric properties",
        "validation study",
        "internal consistency",
        "construct validity",
        "content analysis",
        "thematic analysis",
        "grounded theory",
        "qualitative research",
        "quantitative research",
        "mixed methods",
        "cross sectional",
        "longitudinal study",
        "cohort study",
        "case control",
        "public health",
        "health care",
        "health policy",
        "climate change",
        "renewable energy",
        "supply chain",
        "decision making",
        "risk assessment",
        "data analysis",
        "statistical analysis",
    ]

    # Add known important phrases found in text
    for phrase in important_phrases:
        if phrase in text_lower and phrase.lower() not in terms_lower:
            terms.append(phrase)
            terms_lower.add(phrase.lower())
            if len(terms) >= max_terms:
                return terms

    # Auto-detect bigrams and trigrams from text
    if include_ngrams:
        # Get auto-detected n-grams
        bigrams = extract_bigrams(words)
        trigrams = extract_trigrams(words)

        # Add most promising trigrams first (longer = more specific)
        for trigram in trigrams[:3]:
            if trigram not in terms_lower:
                terms.append(trigram)
                terms_lower.add(trigram.lower())
                if len(terms) >= max_terms:
                    return terms

        # Then bigrams
        for bigram in bigrams[:3]:
            if bigram not in terms_lower:
                terms.append(bigram)
                terms_lower.add(bigram.lower())
                if len(terms) >= max_terms:
                    return terms

    # Add individual important words
    for word in words:
        clean = word.strip("-")
        if (
            len(clean) > 3
            and clean not in STOPWORDS
            and clean not in terms_lower
        ):
            terms.append(clean)
            terms_lower.add(clean.lower())
            if len(terms) >= max_terms:
                break

    return terms[:max_terms]


def extract_search_terms_enhanced(
    text: str,
    keywords: List[str],
    openalex_keywords: List[str] = None,
    max_terms: int = 12,
) -> List[str]:
    """
    Enhanced search term extraction with OpenAlex keywords integration.

    Args:
        text: Combined title and abstract text.
        keywords: User-provided keywords.
        openalex_keywords: Keywords extracted from OpenAlex similar works.
        max_terms: Maximum number of terms to return.

    Returns:
        List of optimized search terms.
    """
    # Combine user keywords with OpenAlex keywords
    all_keywords = list(keywords)
    if openalex_keywords:
        for kw in openalex_keywords:
            if kw.lower() not in {k.lower() for k in all_keywords}:
                all_keywords.append(kw)

    return extract_search_terms(text, all_keywords, max_terms)


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
