"""
OpenAlex Utility Functions

Shared helpers for text processing.

Note: Discipline detection now uses OpenAlex's ML classification directly
via get_topics_from_similar_works() in search.py.
"""
from typing import List, Set


# Stopwords for search term extraction
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
}


def extract_search_terms(
    text: str, keywords: List[str], max_terms: int = 10
) -> List[str]:
    """
    Extract important search terms from text.

    Includes bigrams and trigrams for better phrase matching.

    Args:
        text: Combined title and abstract text.
        keywords: User-provided keywords to prioritize.
        max_terms: Maximum number of terms to return.

    Returns:
        List of search terms, keywords first.
    """
    terms = list(keywords)
    text_lower = text.lower()
    words = text_lower.split()

    # Important academic phrases to look for (bigrams/trigrams)
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
        "clinical trial",
        "randomized controlled",
        "systematic review",
        "meta analysis",
        "confirmatory factor",
        "structural equation",
        "factor analysis",
        "psychometric properties",
        "validation study",
        "internal consistency",
        "construct validity",
    ]

    # First, extract important phrases
    for phrase in important_phrases:
        if phrase in text_lower and phrase not in terms:
            terms.append(phrase)

    # Then add individual important words
    for word in words:
        clean = "".join(c for c in word if c.isalnum())
        if len(clean) > 3 and clean not in STOPWORDS and clean not in terms:
            terms.append(clean)
            if len(terms) >= max_terms:
                break

    return terms[:max_terms]


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
