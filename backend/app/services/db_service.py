"""
Database service for Supabase operations.
Provides a singleton client for database access.
"""
from supabase import create_client, Client
from app.core.config import get_settings


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
            print(f"Database connection error: {e}")
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
            print(f"Error logging search: {e}")
            return False


# Global instance for convenience
db_service = DBService()
