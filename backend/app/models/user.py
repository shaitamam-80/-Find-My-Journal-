"""
User models for authentication and authorization.
"""
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Literal


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


# =============================================================================
# Profile Management Models
# =============================================================================

class ProfileBase(BaseModel):
    """Base profile fields that can be updated by users."""
    display_name: Optional[str] = Field(None, max_length=100)
    institution: Optional[str] = Field(None, max_length=200)
    research_field: Optional[str] = Field(None, max_length=100)
    orcid_id: Optional[str] = Field(None, pattern=r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
    country: Optional[str] = Field(None, max_length=100)
    language_preference: Optional[str] = Field("en", max_length=10)
    email_notifications: Optional[bool] = True


class ProfileUpdateRequest(ProfileBase):
    """Request model for updating profile. All fields optional."""
    pass


class ProfileResponse(ProfileBase):
    """Full profile response with all user data."""
    id: str
    email: str
    tier: str
    credits_used_today: int = 0
    explanations_used_today: int = 0
    has_unlimited_searches: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =============================================================================
# Usage Statistics Models
# =============================================================================

class UsageStatsResponse(BaseModel):
    """User usage statistics."""
    total_searches: int = 0
    total_saved_searches: int = 0
    total_feedback_given: int = 0
    searches_this_month: int = 0
    member_since: Optional[datetime] = None
    last_search_at: Optional[datetime] = None


# =============================================================================
# Admin Models
# =============================================================================

class AdminUserUpdateRequest(BaseModel):
    """Request model for admin to update user."""
    tier: Optional[Literal["free", "paid", "super_admin"]] = None
    is_active: Optional[bool] = None
    has_unlimited_searches: Optional[bool] = None


class UserListItem(BaseModel):
    """User item in admin list."""
    id: str
    email: str
    display_name: Optional[str] = None
    tier: str
    is_active: bool = True
    credits_used_today: int = 0
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    """Paginated user list response."""
    users: list[UserListItem]
    total: int
    page: int
    limit: int
    total_pages: int


class PlatformStatsResponse(BaseModel):
    """Platform-wide statistics for admins."""
    total_users: int = 0
    active_users_today: int = 0
    active_users_week: int = 0
    active_users_month: int = 0
    users_by_tier: dict[str, int] = {}
    total_searches_today: int = 0
    total_searches_week: int = 0
    total_searches_month: int = 0
    new_users_today: int = 0
    new_users_week: int = 0
    new_users_month: int = 0
