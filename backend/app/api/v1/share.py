"""
Share endpoints for sharing search results (Story 3.1).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.security import check_search_limit
from app.models.user import UserProfile
from app.models.journal import Journal
from app.services.db_service import db_service

router = APIRouter(prefix="/share", tags=["Share"])


class ShareRequest(BaseModel):
    """Request to create a shareable link."""
    search_query: str = Field(..., description="Search query summary")
    discipline: Optional[str] = Field(None, description="Detected discipline")
    journals: List[dict] = Field(..., description="Journal results to share")


class ShareResponse(BaseModel):
    """Response with share link."""
    share_id: str
    share_url: str
    expires_in_days: int = 7


class SharedResultResponse(BaseModel):
    """Response for viewing shared results."""
    search_query: str
    discipline: Optional[str]
    journals: List[dict]
    created_at: str


@router.post("", response_model=ShareResponse)
async def create_share_link(
    request: ShareRequest,
    user: UserProfile = Depends(check_search_limit),
):
    """
    Create a shareable link for search results.

    - Requires authentication
    - Link expires after 7 days
    - Returns a unique share URL

    Args:
        request: Share request with journals to share

    Returns:
        ShareResponse with share_id and URL
    """
    # Limit to top 10 journals
    journals_to_share = request.journals[:10]

    share_id = await db_service.create_shared_result(
        user_id=user.id,
        search_query=request.search_query,
        discipline=request.discipline,
        journals_data=journals_to_share,
    )

    if not share_id:
        raise HTTPException(
            status_code=500,
            detail="Failed to create share link"
        )

    # Build share URL (frontend will handle this path)
    share_url = f"/shared/{share_id}"

    return ShareResponse(
        share_id=share_id,
        share_url=share_url,
        expires_in_days=7,
    )


@router.get("/{share_id}", response_model=SharedResultResponse)
async def get_shared_result(share_id: str):
    """
    Get shared search results (public endpoint).

    - Does NOT require authentication
    - Returns 404 if expired or not found

    Args:
        share_id: UUID of the shared result

    Returns:
        SharedResultResponse with journals
    """
    result = await db_service.get_shared_result(share_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Shared result not found or expired"
        )

    return SharedResultResponse(
        search_query=result["search_query"],
        discipline=result.get("discipline"),
        journals=result["journals_data"],
        created_at=result["created_at"],
    )
