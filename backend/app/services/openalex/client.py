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
        """
        Search for sources (journals) directly by name/query.

        Args:
            query: Search query string.
            per_page: Number of results per page.

        Returns:
            List of source dictionaries.
        """
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
        """
        Search for works (papers) on a topic.

        Args:
            query: Search query string.
            per_page: Number of results per page.
            page: Page number.
            from_date: Filter works from this date.

        Returns:
            List of work dictionaries.
        """
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
        """
        Get full details for a source/journal by ID.

        Args:
            source_id: OpenAlex source ID or URL.

        Returns:
            Source dictionary or None on error.
        """
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

        Args:
            topic_ids: List of OpenAlex topic IDs.
            from_date: Filter works from this date.

        Returns:
            List of aggregation results with source counts.
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
