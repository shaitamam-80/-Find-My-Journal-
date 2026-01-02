"""
Admin endpoints for user and platform management.
Requires super_admin tier.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.core.security import get_current_user, require_admin
from app.core.logging import get_logger
from app.services.db_service import db_service
from app.models.user import (
    UserProfile,
    UserListResponse,
    ProfileResponse,
    AdminUserUpdateRequest,
    PlatformStatsResponse,
    UsageStatsResponse,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# User Management
# =============================================================================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    search: Optional[str] = Query(None, description="Search by email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    admin: UserProfile = Depends(require_admin)
):
    """
    List all users with pagination and filtering.

    Admin only. Returns paginated list of users with basic info.
    """
    result = await db_service.list_users(
        page=page,
        limit=limit,
        tier_filter=tier,
        search=search,
        is_active=is_active,
    )
    return result


@router.get("/users/{user_id}", response_model=ProfileResponse)
async def get_user(
    user_id: str,
    admin: UserProfile = Depends(require_admin)
):
    """
    Get a specific user's full profile.

    Admin only.
    """
    profile = await db_service.get_profile_by_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Add computed fields
    tier = profile.get("tier", "free")
    profile["has_unlimited_searches"] = tier in ["paid", "super_admin"]

    return profile


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    updates: AdminUserUpdateRequest,
    admin: UserProfile = Depends(require_admin)
):
    """
    Update a user's account settings.

    Admin only. Can update tier, active status, and unlimited searches flag.
    """
    # Prevent self-modification for critical fields
    if user_id == admin.id and updates.tier is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own tier"
        )

    update_data = updates.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )

    # Validate tier if provided
    if "tier" in update_data and update_data["tier"] not in ["free", "paid", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tier. Must be 'free', 'paid', or 'super_admin'"
        )

    updated = await db_service.update_profile(user_id, update_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    logger.info(f"Admin {admin.id} updated user {user_id}: {update_data}")
    return updated


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin: UserProfile = Depends(require_admin)
):
    """Reactivate a deactivated user account."""
    updated = await db_service.update_profile(user_id, {"is_active": True})

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    logger.info(f"Admin {admin.id} activated user {user_id}")
    return {"message": "User activated successfully"}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    admin: UserProfile = Depends(require_admin)
):
    """Deactivate a user account."""
    # Prevent self-deactivation
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    success = await db_service.deactivate_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )

    logger.info(f"Admin {admin.id} deactivated user {user_id}")
    return {"message": "User deactivated successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: UserProfile = Depends(require_admin)
):
    """
    Permanently delete a user and all their data.

    This action is irreversible.
    """
    # Prevent self-deletion
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Check if user exists first
    profile = await db_service.get_profile_by_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await db_service.delete_user_data(user_id)

    logger.info(f"Admin {admin.id} deleted user {user_id}")
    return {"message": "User and all associated data deleted successfully"}


# =============================================================================
# Platform Statistics
# =============================================================================

@router.get("/stats", response_model=PlatformStatsResponse)
async def get_platform_stats(admin: UserProfile = Depends(require_admin)):
    """
    Get platform-wide statistics.

    Admin only. Returns user counts, activity metrics, and growth data.
    """
    stats = await db_service.get_platform_stats()
    return stats


@router.get("/users/{user_id}/usage", response_model=UsageStatsResponse)
async def get_user_usage(
    user_id: str,
    admin: UserProfile = Depends(require_admin)
):
    """Get detailed usage statistics for a specific user."""
    # First check user exists
    profile = await db_service.get_profile_by_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    usage = await db_service.get_user_usage_stats(user_id)
    return usage
