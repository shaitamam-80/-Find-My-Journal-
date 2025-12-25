"""
Dashboard endpoints for user statistics and recent activity.
"""
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.core.security import get_current_user
from app.core.logging import get_logger
from app.models.user import UserProfile
from app.services.db_service import db_service

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    """User dashboard statistics."""
    searches_today: int
    searches_total: int
    saved_searches_count: int
    daily_limit: Optional[int]
    tier: str


class RecentActivity(BaseModel):
    """Single activity item."""
    id: str
    type: str  # 'search', 'save', 'feedback'
    description: str
    created_at: datetime
    metadata: Optional[dict] = None


class RecentActivityResponse(BaseModel):
    """Response for recent activity endpoint."""
    activities: List[RecentActivity]
    total: int


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user: UserProfile = Depends(get_current_user),
):
    """
    Get user dashboard statistics.

    Returns:
        - searches_today: Number of searches performed today
        - searches_total: Total searches ever performed
        - saved_searches_count: Number of saved searches
        - daily_limit: Daily search limit (null for paid users)
        - tier: User tier (free/paid/admin)
    """
    try:
        # Get profile for today's count
        profile = db_service.get_profile_by_id(user.id)
        searches_today = 0
        if profile:
            last_search_date = profile.get("last_search_date")
            if last_search_date and str(last_search_date) == str(date.today()):
                searches_today = profile.get("credits_used_today", 0)

        # Count total searches from search_logs
        total_result = db_service.client.table("search_logs") \
            .select("id", count="exact") \
            .eq("user_id", user.id) \
            .execute()
        searches_total = total_result.count or 0

        # Count saved searches
        saved_result = db_service.client.table("saved_searches") \
            .select("id", count="exact") \
            .eq("user_id", user.id) \
            .execute()
        saved_searches_count = saved_result.count or 0

        # Determine daily limit based on tier
        from app.core.config import get_settings
        settings = get_settings()
        daily_limit = None if user.tier != "free" else settings.free_user_daily_limit

        return DashboardStats(
            searches_today=searches_today,
            searches_total=searches_total,
            saved_searches_count=saved_searches_count,
            daily_limit=daily_limit,
            tier=user.tier,
        )

    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard stats")


@router.get("/recent-activity", response_model=RecentActivityResponse)
async def get_recent_activity(
    user: UserProfile = Depends(get_current_user),
    limit: int = 10,
):
    """
    Get user's recent activity.

    Args:
        limit: Maximum number of activities to return (default 10)

    Returns:
        List of recent activities (searches, saves, feedback)
    """
    try:
        activities: List[RecentActivity] = []

        # Get recent searches
        searches = db_service.client.table("search_logs") \
            .select("id, discipline, results_count, created_at") \
            .eq("user_id", user.id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        for search in searches.data or []:
            activities.append(RecentActivity(
                id=search["id"],
                type="search",
                description=f"Searched in {search.get('discipline', 'Unknown')} ({search.get('results_count', 0)} results)",
                created_at=datetime.fromisoformat(search["created_at"].replace("Z", "+00:00")),
                metadata={"discipline": search.get("discipline"), "results_count": search.get("results_count")},
            ))

        # Get recent saved searches
        saved = db_service.client.table("saved_searches") \
            .select("id, name, discipline, created_at") \
            .eq("user_id", user.id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        for save in saved.data or []:
            activities.append(RecentActivity(
                id=save["id"],
                type="save",
                description=f"Saved search: {save.get('name', 'Untitled')}",
                created_at=datetime.fromisoformat(save["created_at"].replace("Z", "+00:00")),
                metadata={"name": save.get("name"), "discipline": save.get("discipline")},
            ))

        # Get recent feedback
        feedback = db_service.client.table("journal_feedback") \
            .select("id, journal_id, rating, created_at") \
            .eq("user_id", user.id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        for fb in feedback.data or []:
            rating_text = "thumbs up" if fb.get("rating") == "up" else "thumbs down"
            activities.append(RecentActivity(
                id=fb["id"],
                type="feedback",
                description=f"Gave {rating_text} to a journal",
                created_at=datetime.fromisoformat(fb["created_at"].replace("Z", "+00:00")),
                metadata={"journal_id": fb.get("journal_id"), "rating": fb.get("rating")},
            ))

        # Sort all activities by date and take top N
        activities.sort(key=lambda x: x.created_at, reverse=True)
        activities = activities[:limit]

        return RecentActivityResponse(
            activities=activities,
            total=len(activities),
        )

    except Exception as e:
        logger.error(f"Error fetching recent activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent activity")
