"""
Search endpoints for finding academic journals.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import uuid
import hashlib

from app.core.security import check_search_limit, increment_search_count
from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.user import UserProfile
from app.models.journal import (
    SearchRequest,
    SearchResponse,
    DisciplineDetection,
    DetectedDisciplineInfo,
    ArticleTypeInfo,
    AnalysisMetadata,
    ConfidenceFactors,
)
from app.services.openalex import openalex_service
from app.services.db_service import db_service
from app.services.trust_safety import verify_journals_batch

logger = get_logger(__name__)

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
    # Search for journals (enhanced with SmartAnalyzer - Phase 4)
    (
        journals,
        discipline,
        field,
        confidence,
        detected_disciplines_raw,
        article_type_raw,
        analysis_metadata,
    ) = openalex_service.search_journals_by_text(
        title=request.title,
        abstract=request.abstract,
        keywords=request.keywords,
        prefer_open_access=request.prefer_open_access,
        enable_llm=request.enable_llm if hasattr(request, 'enable_llm') else False,
    )

    # Build discipline detection object (Story 2.1 - backward compatibility)
    discipline_detection = None
    if discipline:
        discipline_detection = DisciplineDetection(
            name=discipline,
            field=field if field else None,
            confidence=round(confidence, 2),
            source="openalex",
        )

    # Build multi-discipline detection list (NEW)
    detected_disciplines = [
        DetectedDisciplineInfo(
            name=d["name"],
            confidence=d["confidence"],
            evidence=d.get("evidence", []),
            openalex_field_id=str(d["openalex_field_id"]) if d.get("openalex_field_id") else None,
            openalex_subfield_id=str(d["openalex_subfield_id"]) if d.get("openalex_subfield_id") else None,
        )
        for d in detected_disciplines_raw
    ] if detected_disciplines_raw else []

    # Build article type info (NEW)
    article_type = None
    if article_type_raw:
        article_type = ArticleTypeInfo(
            type=article_type_raw.get("type", ""),
            display_name=article_type_raw.get("display_name", ""),
            confidence=article_type_raw.get("confidence", 0),
            evidence=article_type_raw.get("evidence", []),
            preferred_journal_types=article_type_raw.get("preferred_journal_types", []),
        )

    # Debug logging
    logger.debug(f"Search returned {len(journals)} journals for discipline: {discipline} (confidence: {confidence:.2f})")
    for j in journals[:5]:
        logger.debug(f"  - {j.name} (category: {j.category})")

    # Trust & Safety verification (async, concurrent)
    settings = get_settings()
    if settings.trust_safety_enabled and journals:
        try:
            journals = await verify_journals_batch(journals)
            logger.debug(f"Verification completed for {len(journals)} journals")
        except Exception as e:
            # Don't fail search if verification fails
            logger.warning(f"Verification failed, continuing without: {e}")

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

    # Build analysis metadata from raw dict (Phase 4)
    analysis_meta = None
    if analysis_metadata:
        analysis_meta = AnalysisMetadata(
            confidence_score=analysis_metadata.get("confidence_score", 0),
            confidence_factors=ConfidenceFactors(
                topics=analysis_metadata.get("confidence_factors", {}).get("topics", 0),
                works=analysis_metadata.get("confidence_factors", {}).get("works", 0),
                keywords=analysis_metadata.get("confidence_factors", {}).get("keywords", 0),
                discipline=analysis_metadata.get("confidence_factors", {}).get("discipline", 0),
                diversity=analysis_metadata.get("confidence_factors", {}).get("diversity", 0),
            ),
            works_analyzed=analysis_metadata.get("works_analyzed", 0),
            topics_found=analysis_metadata.get("topics_found", 0),
            keywords_extracted=analysis_metadata.get("keywords_extracted", []),
            discipline_hints=analysis_metadata.get("discipline_hints", []),
            methodology_hints=analysis_metadata.get("methodology_hints", []),
            needs_llm_enrichment=analysis_metadata.get("needs_llm_enrichment", False),
            enrichment_reasons=analysis_metadata.get("enrichment_reasons", []),
            llm_enriched=analysis_metadata.get("llm_enriched", False),
            llm_additions=analysis_metadata.get("llm_additions"),
        )

    return SearchResponse(
        query=query_summary,
        discipline=discipline,
        discipline_detection=discipline_detection,  # Story 2.1 (backward compat)
        detected_disciplines=detected_disciplines,  # All detected disciplines
        article_type=article_type,  # Detected article type
        analysis_metadata=analysis_meta,  # Phase 4: SmartAnalyzer metadata
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
        result = await (
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
        logger.warning(f"Failed to log search: {e}")
