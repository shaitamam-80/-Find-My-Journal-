"""
Journal models for search results.
"""
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List
from enum import Enum


class JournalCategory(str, Enum):
    """Journal categorization for recommendations."""
    TOP_TIER = "top_tier"
    BROAD_AUDIENCE = "broad_audience"
    NICHE = "niche"
    EMERGING = "emerging"


class JournalMetrics(BaseModel):
    """Quality metrics for a journal."""
    cited_by_count: Optional[int] = None
    works_count: Optional[int] = None
    h_index: Optional[int] = None
    i10_index: Optional[int] = None


class Journal(BaseModel):
    """Academic journal information from OpenAlex."""

    # Basic info
    id: str = Field(..., description="OpenAlex ID")
    name: str = Field(..., description="Journal display name")
    issn: Optional[str] = Field(None, description="Print ISSN")
    issn_l: Optional[str] = Field(None, description="Linking ISSN")

    # Publisher info
    publisher: Optional[str] = None
    homepage_url: Optional[str] = None

    # Scope
    type: Optional[str] = None  # journal, repository, etc.
    is_oa: bool = False  # Open Access
    apc_usd: Optional[int] = None  # Article Processing Charge

    # Metrics
    metrics: JournalMetrics = Field(default_factory=JournalMetrics)

    # Concepts/Topics
    topics: List[str] = Field(default_factory=list)

    # Recommendation
    relevance_score: float = 0.0
    category: Optional[JournalCategory] = None
    match_reason: Optional[str] = None


class SearchRequest(BaseModel):
    """User's search request for finding journals."""

    # Required
    title: str = Field(..., min_length=5, description="Article title")
    abstract: str = Field(..., min_length=50, description="Article abstract")

    # Optional
    keywords: List[str] = Field(default_factory=list, max_length=10)

    # Preferences
    prefer_open_access: bool = False
    min_works_count: Optional[int] = Field(None, ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Deep Learning for Medical Image Analysis",
                "abstract": "This study explores the application of convolutional neural networks for automated detection of abnormalities in chest X-rays...",
                "keywords": ["deep learning", "medical imaging", "CNN"],
                "prefer_open_access": True
            }
        }
    )


class SearchResponse(BaseModel):
    """Response from journal search."""

    query: str
    discipline: Optional[str] = None
    total_found: int
    journals: List[Journal]
    search_id: Optional[str] = None  # For logging
