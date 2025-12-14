"""
Search endpoints for finding academic journals.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import uuid

from app.core.security import check_search_limit, increment_search_count
from app.models.user import UserProfile
from app.models.journal import SearchRequest, SearchResponse
from app.services.openalex_service import openalex_service
from app.services.db_service import db_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("", response_model=SearchResponse)
async def search_journals(
    request: SearchRequest,
    user: UserProfile = Depends(check_search_limit),
):
    """
    Search for suitable journals based on article title and abstract.

    This endpoint:
    1. Validates user has search credits available
    2. Searches OpenAlex for matching journals
    3. Categorizes results by tier (top, broad, niche, emerging)
    4. Logs the search
    5. Increments user's search counter

    Args:
        request: Search parameters (title, abstract, keywords)

    Returns:
        SearchResponse with matching journals and detected discipline

    Raises:
        HTTPException 429: If daily limit reached (free users)
        HTTPException 401: If not authenticated
    """
    # Search for journals
    journals, discipline = openalex_service.search_journals_by_text(
        title=request.title,
        abstract=request.abstract,
        keywords=request.keywords,
        prefer_open_access=request.prefer_open_access,
    )

    # Generate search ID for logging
    search_id = str(uuid.uuid4())

    # Build query summary for logging
    query_summary = f"{request.title[:50]}..."

    # Log search to database
    try:
        await db_service.log_search(
            user_id=user.id,
            query={
                "title": request.title[:100],
                "abstract": request.abstract[:200],
                "keywords": request.keywords,
                "prefer_open_access": request.prefer_open_access,
            },
            results_count=len(journals),
        )
    except Exception as e:
        # Don't fail the search if logging fails
        print(f"Warning: Failed to log search: {e}")

    # Increment search counter
    await increment_search_count(user.id)

    return SearchResponse(
        query=query_summary,
        discipline=discipline,
        total_found=len(journals),
        journals=journals,
        search_id=search_id,
    )


@router.get("/history")
async def get_search_history(
    user: UserProfile = Depends(check_search_limit),
    limit: int = 10,
):
    """
    Get user's recent search history.

    Args:
        limit: Maximum number of results (default 10)

    Returns:
        List of recent searches
    """
    try:
        result = db_service.client.table("search_logs").select(
            "id, query, results_count, created_at"
        ).eq(
            "user_id", user.id
        ).order(
            "created_at", desc=True
        ).limit(limit).execute()

        return {
            "searches": result.data,
            "total": len(result.data),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch search history: {str(e)}"
        )
