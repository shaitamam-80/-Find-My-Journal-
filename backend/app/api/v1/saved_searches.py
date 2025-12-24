"""
Saved Searches endpoints for user profile (Story 4.1).
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.core.security import check_search_limit
from app.models.user import UserProfile
from app.models.journal import SaveSearchRequest, SavedSearchResponse
from app.services.db_service import db_service

router = APIRouter(prefix="/saved-searches", tags=["Saved Searches"])


@router.post("", response_model=SavedSearchResponse)
async def save_search(
    request: SaveSearchRequest,
    user: UserProfile = Depends(check_search_limit),
):
    """
    Save a search to the user's profile (Story 4.1).

    - Requires authentication
    - Limited to 20 saved searches per user

    Args:
        request: Search data to save

    Returns:
        SavedSearchResponse with the saved search ID
    """
    # Check current count
    existing = await db_service.get_saved_searches(user.id, limit=20)
    if len(existing) >= 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum of 20 saved searches reached. Delete some to save new ones."
        )

    search_id = await db_service.save_search(
        user_id=user.id,
        name=request.name,
        title=request.title,
        abstract=request.abstract,
        keywords=request.keywords,
        discipline=request.discipline,
        results_count=request.results_count,
    )

    if not search_id:
        raise HTTPException(
            status_code=500,
            detail="Failed to save search"
        )

    return SavedSearchResponse(
        id=search_id,
        name=request.name,
        title=request.title,
        discipline=request.discipline,
        results_count=request.results_count,
        created_at="just now",
    )


@router.get("", response_model=List[SavedSearchResponse])
async def get_saved_searches(
    user: UserProfile = Depends(check_search_limit),
    limit: int = 20,
):
    """
    Get user's saved searches (Story 4.1).

    Args:
        limit: Maximum number of results (default 20)

    Returns:
        List of saved searches
    """
    searches = await db_service.get_saved_searches(user.id, limit=limit)

    return [
        SavedSearchResponse(
            id=s["id"],
            name=s["name"],
            title=s["title"],
            discipline=s.get("discipline"),
            results_count=s.get("results_count", 0),
            created_at=s["created_at"],
        )
        for s in searches
    ]


@router.get("/{search_id}")
async def get_saved_search(
    search_id: str,
    user: UserProfile = Depends(check_search_limit),
):
    """
    Get a specific saved search with full details (Story 4.1).

    Args:
        search_id: UUID of the saved search

    Returns:
        Full saved search data including abstract
    """
    search = await db_service.get_saved_search(user.id, search_id)

    if not search:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found"
        )

    return {
        "id": search["id"],
        "name": search["name"],
        "title": search["title"],
        "abstract": search["abstract"],
        "keywords": search.get("keywords", []),
        "discipline": search.get("discipline"),
        "results_count": search.get("results_count", 0),
        "created_at": search["created_at"],
    }


@router.delete("/{search_id}")
async def delete_saved_search(
    search_id: str,
    user: UserProfile = Depends(check_search_limit),
):
    """
    Delete a saved search (Story 4.1).

    Args:
        search_id: UUID of the saved search to delete

    Returns:
        Success message
    """
    success = await db_service.delete_saved_search(user.id, search_id)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete saved search"
        )

    return {"message": "Saved search deleted"}
