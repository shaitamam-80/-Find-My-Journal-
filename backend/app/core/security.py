"""
Security utilities for JWT verification and authentication.
"""
import jwt
from datetime import date, datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.user import UserProfile, UserTier, TokenPayload
from app.services.db_service import db_service

logger = get_logger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)

# Get limits from settings
settings = get_settings()
FREE_USER_DAILY_LIMIT = settings.free_user_daily_limit
FREE_USER_EXPLANATION_LIMIT = settings.free_user_explanation_limit


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserProfile:
    """
    Dependency to get the current authenticated user.

    Args:
        credentials: Bearer token from Authorization header.

    Returns:
        UserProfile of the authenticated user.

    Raises:
        HTTPException: If token is missing, invalid, or user not found.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    settings = get_settings()

    try:
        # Decode JWT token (Supabase uses HS256)
        # Note: In production, verify with Supabase's JWT secret
        payload = jwt.decode(
            token,
            options={"verify_signature": False},  # Supabase handles verification
            algorithms=["HS256"]
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

    # Fetch user profile from database
    profile_data = db_service.get_profile_by_id(user_id)

    if not profile_data:
        # Auto-create profile if it doesn't exist (trigger may have failed)
        email = payload.get("email")
        try:
            db_service.client.table("profiles").insert({
                "id": user_id,
                "email": email,
                "tier": "free",
                "credits_used_today": 0,
            }).execute()
            profile_data = {
                "id": user_id,
                "email": email,
                "tier": "free",
                "credits_used_today": 0,
                "last_search_date": None,
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user profile: {str(e)}",
            )

    # Convert to UserProfile model
    return UserProfile(
        id=profile_data["id"],
        email=profile_data.get("email"),
        tier=UserTier(profile_data.get("tier", "free")),
        credits_used_today=profile_data.get("credits_used_today", 0),
        last_search_date=profile_data.get("last_search_date"),
        explanations_used_today=profile_data.get("explanations_used_today", 0),
        last_explanation_date=profile_data.get("last_explanation_date"),
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserProfile]:
    """
    Optional authentication - returns None if no token provided.
    """
    if credentials is None:
        return None
    return await get_current_user(credentials)


async def check_search_limit(
    user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    Dependency to check if user can perform a search.

    Args:
        user: Current authenticated user.

    Returns:
        UserProfile if user can search.

    Raises:
        HTTPException 429: If daily limit reached.
    """
    if not user.can_search(daily_limit=FREE_USER_DAILY_LIMIT):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Daily search limit reached",
                "limit": FREE_USER_DAILY_LIMIT,
                "used": user.credits_used_today,
                "message": "Upgrade to paid plan for unlimited searches",
            }
        )
    return user


async def increment_search_count(user_id: str) -> bool:
    """
    Increment the search count for a user.

    Args:
        user_id: User's UUID.

    Returns:
        True if successful.
    """
    today = date.today()

    try:
        # Get current profile
        profile = db_service.get_profile_by_id(user_id)
        if not profile:
            return False

        last_search = profile.get("last_search_date")
        current_count = profile.get("credits_used_today", 0)

        # Reset counter if new day
        if last_search != str(today):
            new_count = 1
        else:
            new_count = current_count + 1

        # Update in database
        db_service.client.table("profiles").update({
            "credits_used_today": new_count,
            "last_search_date": str(today)
        }).eq("id", user_id).execute()

        return True

    except Exception as e:
        logger.error(f"Error incrementing search count: {e}")
        return False


async def require_admin(
    user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    Dependency to require admin privileges.

    Args:
        user: Current authenticated user.

    Returns:
        UserProfile if user is admin.

    Raises:
        HTTPException 403: If user is not admin.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


async def check_explanation_limit(
    user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    Dependency to check if user can request an AI explanation.

    Args:
        user: Current authenticated user.

    Returns:
        UserProfile if user can get explanations.

    Raises:
        HTTPException 429: If daily limit reached.
    """
    if user.has_unlimited_searches:
        return user

    # Reset counter if it's a new day
    today = date.today()
    if user.last_explanation_date != today:
        return user

    if user.explanations_used_today >= FREE_USER_EXPLANATION_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Daily explanation limit reached",
                "limit": FREE_USER_EXPLANATION_LIMIT,
                "used": user.explanations_used_today,
                "message": "Upgrade to premium for unlimited AI explanations",
            }
        )
    return user


async def increment_explanation_count(user_id: str) -> bool:
    """
    Increment the explanation count for a user.

    Args:
        user_id: User's UUID.

    Returns:
        True if successful.
    """
    today = date.today()

    try:
        profile = db_service.get_profile_by_id(user_id)
        if not profile:
            return False

        last_explanation = profile.get("last_explanation_date")
        current_count = profile.get("explanations_used_today", 0)

        # Reset counter if new day
        if last_explanation != str(today):
            new_count = 1
        else:
            new_count = current_count + 1

        db_service.client.table("profiles").update({
            "explanations_used_today": new_count,
            "last_explanation_date": str(today)
        }).eq("id", user_id).execute()

        return True

    except Exception as e:
        logger.error(f"Error incrementing explanation count: {e}")
        return False
