"""
OpenAlex Service Facade

Maintains backward compatibility with existing code.
This class wraps the modular functions for users who prefer
the object-oriented interface.
"""
from typing import List, Optional, Set, Tuple, Dict

from app.models.journal import Journal
from .constants import load_core_journals
from .search import search_journals_by_keywords, search_journals_by_text


class OpenAlexService:
    """
    Service for searching journals via OpenAlex API.

    This is a facade that maintains backward compatibility.
    For new code, prefer using the module functions directly:

        from app.services.openalex import search_journals_by_text

    Instead of:

        from app.services.openalex import openalex_service
        openalex_service.search_journals_by_text(...)
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
        enable_llm: bool = False,
    ) -> Tuple[List[Journal], str, str, float, List[Dict], Optional[Dict], Optional[Dict]]:
        """
        Search for journals based on article title and abstract.

        Uses HYBRID approach: Keywords + Topics for best results.
        Enhanced with multi-discipline detection, article type awareness,
        and SmartAnalyzer integration (Phase 4).

        Args:
            title: Article title.
            abstract: Article abstract.
            keywords: Optional additional keywords.
            prefer_open_access: Prioritize OA journals.
            enable_llm: Enable LLM enrichment for complex cases.

        Returns:
            Tuple of:
            - journals list
            - detected discipline (primary)
            - field name
            - confidence score
            - detected_disciplines: List of all detected disciplines
            - article_type: Detected article type info
            - analysis_metadata: SmartAnalyzer metadata (Phase 4)
        """
        return search_journals_by_text(
            title=title,
            abstract=abstract,
            keywords=keywords,
            prefer_open_access=prefer_open_access,
            enable_llm=enable_llm,
        )


# Global instance for backward compatibility
openalex_service = OpenAlexService()
