"""
OpenAlex API Client

Wraps pyalex library with error handling and logging.
Also provides async methods using httpx for better performance.

NOTE: This client uses synchronous pyalex library for most operations.
FastAPI automatically runs sync functions in a threadpool.
Async methods (search_works_async, get_sources_async) use httpx directly
for Universal Mode operations.
"""
import pyalex
from typing import List, Dict, Optional, Any
import logging

from .config import get_config

logger = logging.getLogger(__name__)

# OpenAlex API base URL for async operations
OPENALEX_API_BASE = "https://api.openalex.org"


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

    def find_sources_by_subfield_id(
        self,
        subfield_id: int,
        from_date: str = "2019-01-01",
        per_page: int = 25,
    ) -> List[dict]:
        """
        Find top journals that publish in a specific subfield.

        Uses ID-based filtering for accurate results (not text search).

        Args:
            subfield_id: OpenAlex subfield ID (e.g., 2713 for Epidemiology).
            from_date: Filter works from this date.
            per_page: Number of sources to return.

        Returns:
            List of aggregation results with source IDs and counts.
        """
        if not subfield_id:
            return []

        try:
            return (
                pyalex.Works()
                .filter(
                    topics={"subfield": {"id": subfield_id}},
                    type="article",
                    from_publication_date=from_date,
                )
                .group_by("primary_location.source.id")
                .get(per_page=per_page)
            )
        except Exception as e:
            logger.error(f"Error finding sources by subfield {subfield_id}: {e}")
            return []

    # ==================== ASYNC METHODS FOR UNIVERSAL MODE ====================

    async def search_works_async(
        self,
        search: str,
        per_page: int = 50,
        select: Optional[str] = None,
    ) -> List[Dict]:
        """
        Async search for works in OpenAlex.

        Uses httpx for non-blocking HTTP requests.

        Args:
            search: Search query text
            per_page: Number of results
            select: Comma-separated fields to return (reduces payload)

        Returns:
            List of work objects
        """
        import httpx

        params = {
            "search": search,
            "per_page": per_page,
        }
        if select:
            params["select"] = select

        # Add email for polite pool (faster rate limits)
        email = self.config.email if hasattr(self.config, 'email') else None
        if email:
            params["mailto"] = email

        url = f"{OPENALEX_API_BASE}/works"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"OpenAlex API error: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Async OpenAlex search failed: {e}")
            return []

    async def get_sources_async(
        self,
        filter_str: Optional[str] = None,
        sort: str = "cited_by_count:desc",
        per_page: int = 50,
        select: Optional[str] = None,
    ) -> List[Dict]:
        """
        Async get sources (journals) from OpenAlex.

        Args:
            filter_str: OpenAlex filter string
            sort: Sort parameter
            per_page: Number of results
            select: Comma-separated fields to return

        Returns:
            List of source objects
        """
        import httpx

        params = {
            "per_page": per_page,
            "sort": sort,
        }
        if filter_str:
            params["filter"] = filter_str
        if select:
            params["select"] = select

        # Add email for polite pool
        email = self.config.email if hasattr(self.config, 'email') else None
        if email:
            params["mailto"] = email

        url = f"{OPENALEX_API_BASE}/sources"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"OpenAlex Sources API error: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Async OpenAlex sources failed: {e}")
            return []

    async def get_sources_by_subfield_async(
        self,
        subfield_id: int,
        per_page: int = 30,
    ) -> List[Dict]:
        """
        Async get journals filtered by subfield ID.

        Args:
            subfield_id: OpenAlex numeric subfield ID
            per_page: Number of results

        Returns:
            List of source/journal objects
        """
        filter_str = f"topics.subfield.id:https://openalex.org/subfields/{subfield_id}"
        return await self.get_sources_async(
            filter_str=filter_str,
            per_page=per_page,
            select="id,display_name,h_index,summary_stats,topics,type,is_oa",
        )


# Global client instance
_client: Optional[OpenAlexClient] = None


def get_client() -> OpenAlexClient:
    """Get or create global client instance."""
    global _client
    if _client is None:
        _client = OpenAlexClient()
    return _client
