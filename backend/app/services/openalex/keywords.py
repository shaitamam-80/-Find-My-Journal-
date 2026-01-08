"""
Keywords Extraction Module

Extracts and ranks keywords from OpenAlex Works data.
Provides methods to:
- Extract keywords from similar works
- Merge with user-provided keywords
- Rank keywords by relevance and frequency
"""
import logging
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .client import get_client

logger = logging.getLogger(__name__)


@dataclass
class RankedKeyword:
    """A keyword with ranking information."""

    keyword: str
    score: float
    frequency: int
    source: str  # "openalex", "user", "topic", "concept"

    def __hash__(self):
        return hash(self.keyword.lower())

    def __eq__(self, other):
        if isinstance(other, RankedKeyword):
            return self.keyword.lower() == other.keyword.lower()
        return False


class KeywordsExtractor:
    """
    Extracts and ranks keywords from OpenAlex Works.

    Keywords are extracted from:
    - Work titles
    - Work topics (display names)
    - Work keywords field (when available)
    - Concept display names
    """

    def __init__(self):
        self.client = get_client()

        # Common academic stopwords to filter out
        self.stopwords: Set[str] = {
            "study", "research", "analysis", "method", "methods", "results",
            "conclusion", "introduction", "background", "approach", "using",
            "based", "new", "novel", "role", "effect", "effects", "impact",
            "case", "review", "systematic", "evidence", "data", "model",
            "models", "system", "systems", "paper", "article", "findings",
            "implications", "future", "current", "recent", "proposed",
            "application", "applications", "development", "evaluation",
            "assessment", "investigation", "understanding", "exploring",
            "examining", "investigating", "determining", "identifying",
            "examining", "comparing", "evaluating", "assessing", "analyzing",
        }

    def extract_from_works(
        self,
        search_query: str,
        max_works: int = 50,
        min_frequency: int = 2,
    ) -> List[RankedKeyword]:
        """
        Extract keywords from similar works.

        Args:
            search_query: Search query to find similar works.
            max_works: Maximum number of works to analyze.
            min_frequency: Minimum frequency for keyword inclusion.

        Returns:
            List of ranked keywords sorted by score.
        """
        keyword_counts: Counter = Counter()
        keyword_sources: Dict[str, Set[str]] = {}

        # Search for similar works
        works = self.client.search_works(search_query, per_page=max_works)

        if not works:
            logger.warning(f"No works found for keyword extraction: {search_query[:50]}...")
            return []

        for work in works:
            # Extract from topics
            for topic in work.get("topics", []):
                topic_name = topic.get("display_name", "")
                if topic_name:
                    self._add_keyword(
                        topic_name, topic.get("score", 1.0), "topic",
                        keyword_counts, keyword_sources
                    )

            # Extract from keywords field (OpenAlex specific)
            for kw in work.get("keywords", []):
                kw_text = kw.get("keyword") or kw.get("display_name", "")
                if kw_text:
                    score = kw.get("score", 0.8)
                    self._add_keyword(
                        kw_text, score, "openalex",
                        keyword_counts, keyword_sources
                    )

            # Extract from concepts (legacy, being phased out but still useful)
            for concept in work.get("concepts", []):
                concept_name = concept.get("display_name", "")
                if concept_name:
                    score = concept.get("score", 0.5)
                    self._add_keyword(
                        concept_name, score, "concept",
                        keyword_counts, keyword_sources
                    )

        # Convert to RankedKeyword objects
        ranked: List[RankedKeyword] = []
        for keyword, count in keyword_counts.most_common(50):
            if count < min_frequency:
                continue

            # Calculate score based on frequency and source
            base_score = count / len(works) if works else 0
            source_bonus = 0.2 if "topic" in keyword_sources.get(keyword, set()) else 0
            score = min(base_score + source_bonus, 1.0)

            # Get primary source
            sources = keyword_sources.get(keyword, {"openalex"})
            primary_source = "topic" if "topic" in sources else list(sources)[0]

            ranked.append(RankedKeyword(
                keyword=keyword,
                score=score,
                frequency=count,
                source=primary_source,
            ))

        # Sort by score
        ranked.sort(key=lambda k: k.score, reverse=True)

        logger.info(f"Extracted {len(ranked)} keywords from {len(works)} works")
        return ranked

    def merge_with_user_keywords(
        self,
        extracted: List[RankedKeyword],
        user_keywords: List[str],
        user_boost: float = 0.3,
    ) -> List[RankedKeyword]:
        """
        Merge extracted keywords with user-provided keywords.

        User keywords get a boost since they're explicitly specified.

        Args:
            extracted: Keywords extracted from works.
            user_keywords: Keywords provided by the user.
            user_boost: Score boost for user keywords.

        Returns:
            Merged and re-ranked keyword list.
        """
        # Create lookup for extracted keywords
        keyword_map: Dict[str, RankedKeyword] = {
            k.keyword.lower(): k for k in extracted
        }

        # Add/boost user keywords
        for kw in user_keywords:
            kw_lower = kw.lower().strip()
            if not kw_lower:
                continue

            if kw_lower in keyword_map:
                # Boost existing keyword
                existing = keyword_map[kw_lower]
                existing.score = min(existing.score + user_boost, 1.0)
                existing.source = "user"
            else:
                # Add new user keyword
                keyword_map[kw_lower] = RankedKeyword(
                    keyword=kw,
                    score=0.9,  # High score for user-specified
                    frequency=1,
                    source="user",
                )

        # Re-sort by score
        merged = list(keyword_map.values())
        merged.sort(key=lambda k: k.score, reverse=True)

        return merged

    def rank_keywords(
        self,
        keywords: List[RankedKeyword],
        top_n: int = 15,
    ) -> List[RankedKeyword]:
        """
        Re-rank and filter keywords for search optimization.

        Filters out generic terms and limits to top N.

        Args:
            keywords: List of keywords to rank.
            top_n: Maximum number of keywords to return.

        Returns:
            Top ranked keywords.
        """
        # Filter out generic terms
        filtered = [
            k for k in keywords
            if k.keyword.lower() not in self.stopwords
            and len(k.keyword) > 2
        ]

        # Return top N
        return filtered[:top_n]

    def get_search_keywords(
        self,
        search_query: str,
        user_keywords: List[str] = None,
        max_keywords: int = 10,
    ) -> List[str]:
        """
        Convenience method to get optimized search keywords.

        Combines extraction, merging, and ranking.

        Args:
            search_query: Initial search query.
            user_keywords: Optional user-provided keywords.
            max_keywords: Maximum keywords to return.

        Returns:
            List of keyword strings for search.
        """
        # Extract from works
        extracted = self.extract_from_works(search_query, max_works=30)

        # Merge with user keywords if provided
        if user_keywords:
            extracted = self.merge_with_user_keywords(extracted, user_keywords)

        # Rank and filter
        ranked = self.rank_keywords(extracted, top_n=max_keywords)

        return [k.keyword for k in ranked]

    def _add_keyword(
        self,
        text: str,
        score: float,
        source: str,
        counts: Counter,
        sources: Dict[str, Set[str]],
    ) -> None:
        """
        Add a keyword to the tracking counters.

        Normalizes and filters keywords.
        """
        # Normalize
        text = text.strip()
        if not text or len(text) < 3:
            return

        # Skip stopwords
        if text.lower() in self.stopwords:
            return

        # Update counts
        counts[text] += 1

        # Track sources
        if text not in sources:
            sources[text] = set()
        sources[text].add(source)


# Global service instance
_keywords_extractor: Optional[KeywordsExtractor] = None


def get_keywords_extractor() -> KeywordsExtractor:
    """Get or create global keywords extractor instance."""
    global _keywords_extractor
    if _keywords_extractor is None:
        _keywords_extractor = KeywordsExtractor()
    return _keywords_extractor


# Convenience functions


def extract_keywords(
    search_query: str,
    user_keywords: List[str] = None,
    max_keywords: int = 10,
) -> List[str]:
    """
    Extract optimized keywords from a search query.

    Convenience function for KeywordsExtractor.get_search_keywords.
    """
    return get_keywords_extractor().get_search_keywords(
        search_query, user_keywords, max_keywords
    )


def get_ranked_keywords(
    search_query: str,
    max_works: int = 50,
) -> List[RankedKeyword]:
    """
    Get ranked keywords from similar works.

    Returns full RankedKeyword objects with scores.
    """
    return get_keywords_extractor().extract_from_works(
        search_query, max_works
    )
