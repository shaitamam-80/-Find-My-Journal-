"""
User models for authentication and authorization.
"""
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class UserTier(str, Enum):
    """User subscription tiers."""
    FREE = "free"
    PAID = "paid"
    SUPER_ADMIN = "super_admin"


class UserProfile(BaseModel):
    """User profile from Supabase."""
    id: str
    email: Optional[str] = None
    tier: UserTier = UserTier.FREE
    credits_used_today: int = 0
    last_search_date: Optional[date] = None
    # AI explanation tracking
    explanations_used_today: int = 0
    last_explanation_date: Optional[date] = None

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.tier == UserTier.SUPER_ADMIN

    @property
    def has_unlimited_searches(self) -> bool:
        """Check if user has unlimited searches."""
        return self.tier in [UserTier.PAID, UserTier.SUPER_ADMIN]

    def can_search(self, daily_limit: int = 2) -> bool:
        """
        Check if user can perform a search.

        Args:
            daily_limit: Maximum searches per day for free users.

        Returns:
            True if user can search.
        """
        if self.has_unlimited_searches:
            return True

        # Reset counter if it's a new day
        today = date.today()
        if self.last_search_date != today:
            return True

        return self.credits_used_today < daily_limit


class TokenPayload(BaseModel):
    """JWT token payload from Supabase."""
    sub: str  # User ID
    email: Optional[str] = None
    exp: int  # Expiration timestamp
    aud: Optional[str] = None
    role: Optional[str] = None
