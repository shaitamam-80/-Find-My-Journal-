"""
Search endpoints for finding academic journals.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import uuid
import hashlib

from app.core.security import check_search_limit, increment_search_count
from app.core.config import get_settings
from app.models.user import UserProfile
from app.models.journal import SearchRequest, SearchResponse
from app.services.openalex_service import openalex_service
from app.services.db_service import db_service
from app.services.trust_safety import verify_journals_batch

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

    # Debug logging
    print(f"[DEBUG] Search returned {len(journals)} journals for discipline: {discipline}")
    for j in journals[:5]:
        print(f"  - {j.name} (category: {j.category})")

    # Trust & Safety verification (async, concurrent)
    settings = get_settings()
    if settings.trust_safety_enabled and journals:
        try:
            journals = await verify_journals_batch(journals)
            print(f"[DEBUG] Verification completed for {len(journals)} journals")
        except Exception as e:
            # Don't fail search if verification fails
            print(f"Warning: Verification failed, continuing without: {e}")

    # Generate search ID for logging
    search_id = str(uuid.uuid4())

    # Build query summary for response (no raw content)
    query_summary = f"Search in {discipline or 'unknown field'}"

    # Handle search logging (async, non-blocking failure)
    await _handle_search_logging(
        user_id=user.id,
        discipline=discipline,
        abstract=request.abstract,
        results_count=len(journals),
        incognito=request.incognito_mode,
    )

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
        result = (
            db_service.client.table("search_logs")
            .select("id, query, results_count, created_at")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {
            "searches": result.data,
            "total": len(result.data),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch search history: {str(e)}"
        )


async def _handle_search_logging(
    user_id: str, discipline: str, abstract: str, results_count: int, incognito: bool
):
    """
    Handle privacy-preserving search logging.
    Separated to maintain Single Responsibility Principle in the endpoint.
    """
    # Generate SHA-256 hash of abstract for duplicate detection (privacy-preserving)
    query_hash = hashlib.sha256(abstract.encode("utf-8")).hexdigest()

    try:
        await db_service.log_search(
            user_id=user_id,
            discipline=discipline,
            query_hash=query_hash,
            is_incognito=incognito,
            results_count=results_count,
        )
    except Exception as e:
        # Don't fail the search if logging fails
        print(f"Warning: Failed to log search: {e}")
