"""
Explanation endpoint for AI-powered journal fit explanations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from app.core.security import (
    check_explanation_limit,
    increment_explanation_count,
    FREE_USER_EXPLANATION_LIMIT,
)
from app.models.user import UserProfile
from app.services.gemini import get_gemini_service

router = APIRouter(prefix="/explain", tags=["Explain"])


class ExplanationRequest(BaseModel):
    """Request model for journal explanation."""

    abstract: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="User's article abstract",
    )
    journal_id: str = Field(..., min_length=1, description="Journal ID from OpenAlex")
    journal_title: str = Field(..., min_length=1, description="Journal name")
    journal_topics: list[str] = Field(
        default_factory=list, description="Journal's research topics"
    )
    journal_metrics: dict = Field(
        default_factory=dict, description="Journal metrics (h_index, citations, etc.)"
    )


class ExplanationResponse(BaseModel):
    """Response model with AI explanation."""

    explanation: str = Field(..., description="AI-generated explanation text")
    is_ai_generated: bool = Field(
        ..., description="True if from LLM, False if fallback text"
    )
    remaining_today: Optional[int] = Field(
        None, description="Remaining explanations today (for free users)"
    )


@router.post("", response_model=ExplanationResponse)
async def get_explanation(
    request: ExplanationRequest,
    user: UserProfile = Depends(check_explanation_limit),
) -> ExplanationResponse:
    """
    Generate AI explanation for why a journal matches the user's abstract.

    This endpoint uses Google Gemini to generate personalized explanations
    that connect the user's research to the journal's scope.

    Rate limits:
    - Free users: 15 explanations/day
    - Paid/Admin: Unlimited

    Returns:
        ExplanationResponse with explanation text and metadata.

    Raises:
        HTTPException 401: If not authenticated.
        HTTPException 422: If abstract is too short.
        HTTPException 429: If daily limit reached.
    """
    gemini = get_gemini_service()

    # Build journal dict for the service
    journal_data = {
        "id": request.journal_id,
        "title": request.journal_title,
        "topics": request.journal_topics,
        "metrics": request.journal_metrics,
    }

    # Generate explanation
    explanation, is_ai = await gemini.generate_explanation(
        abstract=request.abstract,
        journal=journal_data,
    )

    # Increment usage counter (only after successful generation)
    await increment_explanation_count(user.id)

    # Calculate remaining for free users
    remaining = None
    if not user.has_unlimited_searches:
        remaining = max(
            0, FREE_USER_EXPLANATION_LIMIT - user.explanations_used_today - 1
        )

    return ExplanationResponse(
        explanation=explanation,
        is_ai_generated=is_ai,
        remaining_today=remaining,
    )
