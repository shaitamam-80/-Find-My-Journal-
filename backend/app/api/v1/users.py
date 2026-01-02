"""
User management endpoints.
Handles profile updates, settings, and account management.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.core.logging import get_logger
from app.services.db_service import db_service
from app.models.user import (
    UserProfile,
    ProfileUpdateRequest,
    ProfileResponse,
    UsageStatsResponse,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


# =============================================================================
# Profile Endpoints
# =============================================================================

@router.get("/me/profile", response_model=ProfileResponse)
async def get_my_profile(user: UserProfile = Depends(get_current_user)):
    """
    Get current user's full profile.

    Returns all profile fields including usage stats and timestamps.
    """
    profile = await db_service.get_profile_by_id(user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Add computed fields
    profile["has_unlimited_searches"] = user.has_unlimited_searches

    return profile


@router.patch("/me/profile", response_model=ProfileResponse)
async def update_my_profile(
    updates: ProfileUpdateRequest,
    user: UserProfile = Depends(get_current_user)
):
    """
    Update current user's profile.

    Only provided fields will be updated. Omitted fields remain unchanged.
    """
    update_data = updates.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )

    updated = await db_service.update_profile(user.id, update_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Add computed fields
    updated["has_unlimited_searches"] = user.has_unlimited_searches

    logger.info(f"Profile updated for user {user.id}")
    return updated


# =============================================================================
# Usage & Statistics
# =============================================================================

@router.get("/me/usage", response_model=UsageStatsResponse)
async def get_my_usage(user: UserProfile = Depends(get_current_user)):
    """
    Get detailed usage statistics for current user.

    Returns search counts, saved items, and activity history.
    """
    usage = await db_service.get_user_usage_stats(user.id)
    return usage


# =============================================================================
# Account Management
# =============================================================================

@router.post("/me/deactivate")
async def deactivate_my_account(user: UserProfile = Depends(get_current_user)):
    """
    Deactivate current user's account (soft delete).

    The account can be reactivated by contacting support.
    User data is preserved.
    """
    success = await db_service.deactivate_user(user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account"
        )

    logger.info(f"Account deactivated for user {user.id}")
    return {"message": "Account deactivated successfully"}


@router.delete("/me")
async def delete_my_account(user: UserProfile = Depends(get_current_user)):
    """
    Permanently delete current user's account and all associated data.

    This action is irreversible and will delete:
    - All search history
    - All saved searches
    - All feedback
    - Profile information

    Note: The Supabase auth account needs to be deleted separately.
    """
    await db_service.delete_user_data(user.id)

    logger.info(f"Account deleted for user {user.id}")
    return {
        "message": "Account and all associated data deleted successfully",
        "note": "Please sign out to complete the process"
    }


# =============================================================================
# Notification Preferences
# =============================================================================

@router.patch("/me/notifications")
async def update_notification_preferences(
    email_notifications: bool,
    user: UserProfile = Depends(get_current_user)
):
    """Update email notification preferences."""
    await db_service.update_profile(user.id, {
        "email_notifications": email_notifications
    })

    return {"email_notifications": email_notifications}
