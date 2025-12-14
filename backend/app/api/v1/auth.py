"""
Authentication endpoints for testing auth flow.
"""
from fastapi import APIRouter, Depends
from app.core.security import (
    get_current_user,
    check_search_limit,
    require_admin,
    increment_search_count,
    FREE_USER_DAILY_LIMIT,
)
from app.models.user import UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
async def get_me(user: UserProfile = Depends(get_current_user)):
    """
    Get current user's profile.

    Returns:
        User profile information.
    """
    return {
        "id": user.id,
        "email": user.email,
        "tier": user.tier.value,
        "credits_used_today": user.credits_used_today,
        "last_search_date": str(user.last_search_date) if user.last_search_date else None,
        "has_unlimited_searches": user.has_unlimited_searches,
        "is_admin": user.is_admin,
    }


@router.get("/limits")
async def get_limits(user: UserProfile = Depends(get_current_user)):
    """
    Get user's current usage limits.

    Returns:
        Current usage and limits.
    """
    return {
        "tier": user.tier.value,
        "daily_limit": None if user.has_unlimited_searches else FREE_USER_DAILY_LIMIT,
        "used_today": user.credits_used_today,
        "remaining": None if user.has_unlimited_searches else max(0, FREE_USER_DAILY_LIMIT - user.credits_used_today),
        "can_search": user.can_search(FREE_USER_DAILY_LIMIT),
    }


@router.post("/test-search")
async def test_search(user: UserProfile = Depends(check_search_limit)):
    """
    Test endpoint that simulates a search (uses rate limit).

    This endpoint:
    1. Checks if user can search (rate limit)
    2. Increments the search counter
    3. Returns success

    Raises:
        HTTPException 429: If daily limit reached.
    """
    # Increment search count
    await increment_search_count(user.id)

    return {
        "message": "Search performed successfully",
        "user_id": user.id,
        "tier": user.tier.value,
        "searches_used": user.credits_used_today + 1,
        "limit": None if user.has_unlimited_searches else FREE_USER_DAILY_LIMIT,
    }


@router.get("/admin-only")
async def admin_only(user: UserProfile = Depends(require_admin)):
    """
    Test endpoint that requires admin privileges.

    Raises:
        HTTPException 403: If user is not admin.
    """
    return {
        "message": "Welcome, admin!",
        "user_id": user.id,
        "email": user.email,
    }
