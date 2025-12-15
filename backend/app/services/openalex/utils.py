"""
OpenAlex Utility Functions

Shared helpers for text processing and discipline detection.
"""
from collections import Counter
from typing import List, Set

from .constants import DISCIPLINE_KEYWORDS


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
    scores: Counter = Counter()

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
