"""
Feedback endpoints for rating journal recommendations (Story 5.1).
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.core.security import check_search_limit
from app.models.user import UserProfile
from app.models.journal import FeedbackRequest, FeedbackResponse
from app.services.db_service import db_service

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    user: UserProfile = Depends(check_search_limit),
):
    """
    Submit feedback (thumbs up/down) for a journal recommendation (Story 5.1).

    - Requires authentication
    - Upserts: updates existing feedback if already rated

    Args:
        request: Feedback data with journal_id and rating

    Returns:
        FeedbackResponse with confirmation
    """
    feedback_id = await db_service.submit_feedback(
        user_id=user.id,
        journal_id=request.journal_id,
        rating=request.rating.value,
        search_id=request.search_id,
    )

    if not feedback_id:
        raise HTTPException(
            status_code=500,
            detail="Failed to submit feedback"
        )

    return FeedbackResponse(
        id=feedback_id,
        journal_id=request.journal_id,
        rating=request.rating.value,
        created_at="just now",
    )


@router.get("")
async def get_user_feedback(
    journal_ids: str,
    user: UserProfile = Depends(check_search_limit),
):
    """
    Get user's feedback for multiple journals (Story 5.1).

    Args:
        journal_ids: Comma-separated list of journal IDs

    Returns:
        Dict mapping journal_id -> rating
    """
    ids = [j.strip() for j in journal_ids.split(",") if j.strip()]

    if not ids:
        return {"feedback": {}}

    feedback = await db_service.get_user_feedback(user.id, ids)

    return {"feedback": feedback}
