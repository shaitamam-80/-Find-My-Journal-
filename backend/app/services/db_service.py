"""
Database service for Supabase operations.
Provides a singleton async client for database access.
"""
from datetime import datetime, timedelta
from typing import Optional
from supabase import acreate_client, AsyncClient
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.exceptions import DatabaseError

logger = get_logger(__name__)


class DBService:
    """
    Async singleton service for Supabase database operations.
    Must call await db_service.initialize() before use.
    """

    _instance: Optional["DBService"] = None
    _client: Optional[AsyncClient] = None
    _initialized: bool = False

    def __new__(cls) -> "DBService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self) -> None:
        """Initialize the async Supabase client. Call once at startup."""
        if self._initialized:
            return

        settings = get_settings()
        # Use service role key if available (bypasses RLS), otherwise use regular key
        key = settings.supabase_service_role_key or settings.supabase_key

        self._client = await acreate_client(
            settings.supabase_url,
            key
        )
        self._initialized = True
        logger.info("Supabase async client initialized")

    @property
    def client(self) -> AsyncClient:
        """Get the Supabase client instance."""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized. Call await db_service.initialize() first.")
        return self._client

    async def check_connection(self) -> bool:
        """
        Check if the database connection is working.
        Attempts to query the profiles table.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            # Try to select from profiles table (may be empty, that's ok)
            response = await self.client.table("profiles").select("id").limit(1).execute()
            # If we get here without exception, connection works
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False

    async def get_profile_by_id(self, user_id: str) -> dict | None:
        """
        Get a user profile by ID.

        Args:
            user_id: The UUID of the user.

        Returns:
            Profile dict or None if not found.
        """
        try:
            response = await self.client.table("profiles").select("*").eq("id", user_id).single().execute()
            return response.data
        except Exception as e:
            logger.warning(f"Profile not found or error for {user_id}: {e}")
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
            await self.client.table("search_logs").insert({
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
            await self.client.table("shared_results").insert({
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
            response = await self.client.table("shared_results") \
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
            await self.client.table("saved_searches").insert({
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
            response = await self.client.table("saved_searches") \
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
            response = await self.client.table("saved_searches") \
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
            await self.client.table("saved_searches") \
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
            await self.client.table("journal_feedback").upsert({
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
            response = await self.client.table("journal_feedback") \
                .select("journal_id, rating") \
                .eq("user_id", user_id) \
                .in_("journal_id", journal_ids) \
                .execute()

            return {row["journal_id"]: row["rating"] for row in (response.data or [])}
        except Exception as e:
            logger.error(f"Error fetching feedback: {e}")
            return {}

    # =========================================================================
    # User Profile Management
    # =========================================================================

    async def update_profile(self, user_id: str, updates: dict) -> dict | None:
        """
        Update a user's profile.

        Args:
            user_id: The user's ID
            updates: Dictionary of fields to update

        Returns:
            Updated profile data or None if not found
        """
        try:
            # Remove None values
            clean_updates = {k: v for k, v in updates.items() if v is not None}

            if not clean_updates:
                return await self.get_profile_by_id(user_id)

            response = await self.client.table("profiles")\
                .update(clean_updates)\
                .eq("id", user_id)\
                .execute()

            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating profile {user_id}: {e}")
            raise DatabaseError(f"Failed to update profile: {e}")

    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp."""
        try:
            await self.client.table("profiles")\
                .update({"last_login_at": datetime.utcnow().isoformat()})\
                .eq("id", user_id)\
                .execute()
        except Exception as e:
            logger.warning(f"Failed to update last login for {user_id}: {e}")

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account (soft delete)."""
        try:
            await self.client.table("profiles")\
                .update({"is_active": False})\
                .eq("id", user_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False

    async def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all user data (GDPR compliance).
        Note: This doesn't delete from auth.users - that requires Supabase Admin API.

        Args:
            user_id: The user's ID

        Returns:
            True if successful
        """
        try:
            # Delete in order to respect foreign key constraints
            tables_to_clear = [
                "journal_feedback",
                "saved_searches",
                "search_logs",
                "shared_results",
                "user_activity_log",
            ]

            for table in tables_to_clear:
                try:
                    await self.client.table(table)\
                        .delete()\
                        .eq("user_id", user_id)\
                        .execute()
                except Exception as e:
                    logger.warning(f"Error deleting from {table}: {e}")

            # Finally delete profile
            await self.client.table("profiles")\
                .delete()\
                .eq("id", user_id)\
                .execute()

            logger.info(f"Deleted all data for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user data {user_id}: {e}")
            raise DatabaseError(f"Failed to delete user data: {e}")

    # =========================================================================
    # User Statistics
    # =========================================================================

    async def get_user_usage_stats(self, user_id: str) -> dict:
        """Get detailed usage statistics for a user."""
        try:
            # Get profile for member_since
            profile = await self.get_profile_by_id(user_id)

            # Total searches
            searches_result = await self.client.table("search_logs")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()

            # Searches this month
            month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
            searches_month = await self.client.table("search_logs")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .gte("created_at", month_ago)\
                .execute()

            # Last search
            last_search = await self.client.table("search_logs")\
                .select("created_at")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()

            # Saved searches count
            saved_result = await self.client.table("saved_searches")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()

            # Feedback count
            feedback_result = await self.client.table("journal_feedback")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()

            return {
                "total_searches": searches_result.count or 0,
                "total_saved_searches": saved_result.count or 0,
                "total_feedback_given": feedback_result.count or 0,
                "searches_this_month": searches_month.count or 0,
                "member_since": profile.get("created_at") if profile else None,
                "last_search_at": last_search.data[0]["created_at"] if last_search.data else None,
            }
        except Exception as e:
            logger.error(f"Error getting usage stats for {user_id}: {e}")
            return {
                "total_searches": 0,
                "total_saved_searches": 0,
                "total_feedback_given": 0,
                "searches_this_month": 0,
                "member_since": None,
                "last_search_at": None,
            }

    # =========================================================================
    # Admin Operations
    # =========================================================================

    async def list_users(
        self,
        page: int = 1,
        limit: int = 20,
        tier_filter: str | None = None,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> dict:
        """
        List users with pagination and filtering (admin only).

        Args:
            page: Page number (1-indexed)
            limit: Items per page
            tier_filter: Filter by tier
            search: Search by email
            is_active: Filter by active status

        Returns:
            Dict with users list and pagination info
        """
        try:
            query = self.client.table("profiles")\
                .select("id, email, display_name, tier, is_active, credits_used_today, created_at, last_login_at", count="exact")

            if tier_filter:
                query = query.eq("tier", tier_filter)

            if search:
                query = query.ilike("email", f"%{search}%")

            if is_active is not None:
                query = query.eq("is_active", is_active)

            # Pagination
            offset = (page - 1) * limit
            query = query.order("created_at", desc=True)\
                .range(offset, offset + limit - 1)

            result = await query.execute()
            total = result.count or 0

            return {
                "users": result.data or [],
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            }
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise DatabaseError(f"Failed to list users: {e}")

    async def get_platform_stats(self) -> dict:
        """Get platform-wide statistics (admin only)."""
        try:
            now = datetime.utcnow()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)

            # Total users
            total_users = await self.client.table("profiles")\
                .select("id", count="exact")\
                .execute()

            # Users by tier
            free_users = await self.client.table("profiles")\
                .select("id", count="exact")\
                .eq("tier", "free")\
                .execute()

            paid_users = await self.client.table("profiles")\
                .select("id", count="exact")\
                .eq("tier", "paid")\
                .execute()

            admin_users = await self.client.table("profiles")\
                .select("id", count="exact")\
                .eq("tier", "super_admin")\
                .execute()

            # Active users (by last_login_at)
            active_today = await self.client.table("profiles")\
                .select("id", count="exact")\
                .gte("last_login_at", today.isoformat())\
                .execute()

            active_week = await self.client.table("profiles")\
                .select("id", count="exact")\
                .gte("last_login_at", week_ago.isoformat())\
                .execute()

            active_month = await self.client.table("profiles")\
                .select("id", count="exact")\
                .gte("last_login_at", month_ago.isoformat())\
                .execute()

            # New users
            new_today = await self.client.table("profiles")\
                .select("id", count="exact")\
                .gte("created_at", today.isoformat())\
                .execute()

            new_week = await self.client.table("profiles")\
                .select("id", count="exact")\
                .gte("created_at", week_ago.isoformat())\
                .execute()

            new_month = await self.client.table("profiles")\
                .select("id", count="exact")\
                .gte("created_at", month_ago.isoformat())\
                .execute()

            # Searches
            searches_today = await self.client.table("search_logs")\
                .select("id", count="exact")\
                .gte("created_at", today.isoformat())\
                .execute()

            searches_week = await self.client.table("search_logs")\
                .select("id", count="exact")\
                .gte("created_at", week_ago.isoformat())\
                .execute()

            searches_month = await self.client.table("search_logs")\
                .select("id", count="exact")\
                .gte("created_at", month_ago.isoformat())\
                .execute()

            return {
                "total_users": total_users.count or 0,
                "active_users_today": active_today.count or 0,
                "active_users_week": active_week.count or 0,
                "active_users_month": active_month.count or 0,
                "users_by_tier": {
                    "free": free_users.count or 0,
                    "paid": paid_users.count or 0,
                    "super_admin": admin_users.count or 0,
                },
                "total_searches_today": searches_today.count or 0,
                "total_searches_week": searches_week.count or 0,
                "total_searches_month": searches_month.count or 0,
                "new_users_today": new_today.count or 0,
                "new_users_week": new_week.count or 0,
                "new_users_month": new_month.count or 0,
            }
        except Exception as e:
            logger.error(f"Error getting platform stats: {e}")
            raise DatabaseError(f"Failed to get platform stats: {e}")

    async def log_activity(
        self,
        user_id: str,
        activity_type: str,
        metadata: dict | None = None
    ) -> None:
        """Log user activity for analytics."""
        try:
            await self.client.table("user_activity_log").insert({
                "user_id": user_id,
                "activity_type": activity_type,
                "metadata": metadata or {},
            }).execute()
        except Exception as e:
            # Don't fail on activity logging errors
            logger.warning(f"Failed to log activity: {e}")


# Global instance for convenience
db_service = DBService()
