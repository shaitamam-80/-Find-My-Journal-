"""
Database service for Supabase operations.
Provides a singleton client for database access.
"""
from supabase import create_client, Client
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DBService:
    """
    Singleton service for Supabase database operations.
    """

    _instance: "DBService | None" = None
    _client: Client | None = None

    def __new__(cls) -> "DBService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._client is None:
            settings = get_settings()
            # Use service role key if available (bypasses RLS), otherwise use regular key
            key = settings.supabase_service_role_key or settings.supabase_key
            self._client = create_client(
                settings.supabase_url,
                key
            )

    @property
    def client(self) -> Client:
        """Get the Supabase client instance."""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client

    def check_connection(self) -> bool:
        """
        Check if the database connection is working.
        Attempts to query the profiles table.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            # Try to select from profiles table (may be empty, that's ok)
            response = self.client.table("profiles").select("id").limit(1).execute()
            # If we get here without exception, connection works
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False

    def get_profile_by_id(self, user_id: str) -> dict | None:
        """
        Get a user profile by ID.

        Args:
            user_id: The UUID of the user.

        Returns:
            Profile dict or None if not found.
        """
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).single().execute()
            return response.data
        except Exception:
            return None

    async def log_search(
        self,
        user_id: str,
        discipline: str | None = None,
        query_hash: str | None = None,
        is_incognito: bool = False,
        results_count: int = 0,
    ) -> bool:
        """
        Log a search to the database (privacy-focused).

        Args:
            user_id: The UUID of the user.
            discipline: The detected academic discipline (e.g., "Medicine").
            query_hash: SHA-256 hash of the abstract for duplicate detection.
            is_incognito: Whether the user opted for incognito mode.
            results_count: Number of results returned.

        Returns:
            True if logging was successful.
        """
        try:
            self.client.table("search_logs").insert({
                "user_id": user_id,
                "discipline": discipline,
                "query_hash": query_hash,
                "is_incognito": is_incognito,
                "results_count": results_count,
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error logging search: {e}")
            return False


    # ==========================================================================
    # Share Results (Story 3.1)
    # ==========================================================================

    async def create_shared_result(
        self,
        user_id: str,
        search_query: str,
        discipline: str | None,
        journals_data: list[dict],
    ) -> str | None:
        """
        Create a shareable link for search results.

        Args:
            user_id: The UUID of the user who created the share.
            search_query: Summary of the search query.
            discipline: Detected discipline.
            journals_data: List of journal dicts to share.

        Returns:
            share_id (UUID) if successful, None otherwise.
        """
        import uuid
        from datetime import datetime, timedelta

        share_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=7)

        try:
            self.client.table("shared_results").insert({
                "id": share_id,
                "user_id": user_id,
                "search_query": search_query,
                "discipline": discipline,
                "journals_data": journals_data,
                "expires_at": expires_at.isoformat(),
            }).execute()
            return share_id
        except Exception as e:
            logger.error(f"Error creating shared result: {e}")
            return None

    async def get_shared_result(self, share_id: str) -> dict | None:
        """
        Get a shared search result by ID.

        Args:
            share_id: The UUID of the shared result.

        Returns:
            Shared result dict or None if not found/expired.
        """
        from datetime import datetime

        try:
            response = self.client.table("shared_results") \
                .select("*") \
                .eq("id", share_id) \
                .single() \
                .execute()

            if not response.data:
                return None

            # Check expiration
            expires_at = datetime.fromisoformat(response.data["expires_at"].replace("Z", "+00:00"))
            if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
                return None

            return response.data
        except Exception:
            return None


    # ==========================================================================
    # Saved Searches (Story 4.1)
    # ==========================================================================

    async def save_search(
        self,
        user_id: str,
        name: str,
        title: str,
        abstract: str,
        keywords: list[str],
        discipline: str | None,
        results_count: int,
    ) -> str | None:
        """
        Save a search to user's profile.

        Args:
            user_id: The UUID of the user.
            name: User-given name for this search.
            title: Original article title.
            abstract: Original abstract.
            keywords: Keywords used in search.
            discipline: Detected discipline.
            results_count: Number of results from search.

        Returns:
            saved_search_id (UUID) if successful, None otherwise.
        """
        import uuid

        search_id = str(uuid.uuid4())

        try:
            self.client.table("saved_searches").insert({
                "id": search_id,
                "user_id": user_id,
                "name": name,
                "title": title,
                "abstract": abstract,
                "keywords": keywords,
                "discipline": discipline,
                "results_count": results_count,
            }).execute()
            return search_id
        except Exception as e:
            logger.error(f"Error saving search: {e}")
            return None

    async def get_saved_searches(self, user_id: str, limit: int = 20) -> list[dict]:
        """
        Get user's saved searches.

        Args:
            user_id: The UUID of the user.
            limit: Maximum number of results.

        Returns:
            List of saved search dicts.
        """
        try:
            response = self.client.table("saved_searches") \
                .select("id, name, title, discipline, results_count, created_at") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching saved searches: {e}")
            return []

    async def get_saved_search(self, user_id: str, search_id: str) -> dict | None:
        """
        Get a specific saved search.

        Args:
            user_id: The UUID of the user.
            search_id: The UUID of the saved search.

        Returns:
            Saved search dict or None if not found.
        """
        try:
            response = self.client.table("saved_searches") \
                .select("*") \
                .eq("id", search_id) \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            return response.data
        except Exception:
            return None

    async def delete_saved_search(self, user_id: str, search_id: str) -> bool:
        """
        Delete a saved search.

        Args:
            user_id: The UUID of the user.
            search_id: The UUID of the saved search.

        Returns:
            True if deletion was successful.
        """
        try:
            self.client.table("saved_searches") \
                .delete() \
                .eq("id", search_id) \
                .eq("user_id", user_id) \
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting saved search: {e}")
            return False

    # ==========================================================================
    # Feedback Rating (Story 5.1)
    # ==========================================================================

    async def submit_feedback(
        self,
        user_id: str,
        journal_id: str,
        rating: str,
        search_id: str | None = None,
    ) -> str | None:
        """
        Submit feedback rating for a journal recommendation.

        Args:
            user_id: The UUID of the user.
            journal_id: OpenAlex journal ID.
            rating: "up" or "down".
            search_id: Optional search ID for context.

        Returns:
            feedback_id (UUID) if successful, None otherwise.
        """
        import uuid

        feedback_id = str(uuid.uuid4())

        try:
            # Upsert: update if exists, insert if new
            self.client.table("journal_feedback").upsert({
                "id": feedback_id,
                "user_id": user_id,
                "journal_id": journal_id,
                "rating": rating,
                "search_id": search_id,
            }, on_conflict="user_id,journal_id").execute()
            return feedback_id
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return None

    async def get_user_feedback(self, user_id: str, journal_ids: list[str]) -> dict[str, str]:
        """
        Get user's feedback for a list of journals.

        Args:
            user_id: The UUID of the user.
            journal_ids: List of journal IDs to check.

        Returns:
            Dict mapping journal_id -> rating ("up" or "down")
        """
        if not journal_ids:
            return {}

        try:
            response = self.client.table("journal_feedback") \
                .select("journal_id, rating") \
                .eq("user_id", user_id) \
                .in_("journal_id", journal_ids) \
                .execute()

            return {row["journal_id"]: row["rating"] for row in (response.data or [])}
        except Exception as e:
            logger.error(f"Error fetching feedback: {e}")
            return {}


# Global instance for convenience
db_service = DBService()
