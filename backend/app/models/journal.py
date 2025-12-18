"""
Journal models for search results.
"""
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime


class JournalCategory(str, Enum):
    """Journal categorization for recommendations."""
    TOP_TIER = "top_tier"
    BROAD_AUDIENCE = "broad_audience"
    NICHE = "niche"
    EMERGING = "emerging"


# =============================================================================
# Trust & Safety Verification Models
# =============================================================================

class BadgeColor(str, Enum):
    """Visual badge color for verification status."""
    GREEN = "verified"       # MEDLINE/DOAJ verified - safe to publish
    YELLOW = "caution"       # PMC only / 1 warning flag - proceed with care
    RED = "high_risk"        # Blacklist match / 2+ flags - avoid
    GRAY = "unverified"      # No data available - do your own research


class VerificationSource(str, Enum):
    """Source of verification data."""
    MEDLINE = "medline"      # NLM Catalog - Currently Indexed
    DOAJ = "doaj"            # Directory of Open Access Journals
    COPE = "cope"            # Committee on Publication Ethics
    OASPA = "oaspa"          # Open Access Scholarly Publishers Association
    PMC = "pmc"              # PubMed Central (archive only)
    BLACKLIST = "blacklist"  # Community watchlists (Stop Predatory Journals)
    HEURISTIC = "heuristic"  # Behavioral analysis (volume spike, etc.)


class VerificationFlag(BaseModel):
    """A specific warning or verification flag."""
    source: VerificationSource
    reason: str  # Human-readable explanation
    severity: str = "medium"  # low, medium, high, critical


class VerificationStatus(BaseModel):
    """
    Journal verification status from Trust & Safety Engine.

    Uses factual, non-defamatory language:
    - GREEN: "Verified Source" (not "Safe" or "Good")
    - YELLOW: "Exercise Caution" or "Limited Indexing"
    - RED: "Publication Risk Detected" (not "Predatory" or "Scam")
    - GRAY: "Unverified Source"
    """
    badge_color: BadgeColor = BadgeColor.GRAY
    status_text: str = "Unverified Source"
    subtitle: Optional[str] = None  # e.g., "MEDLINE" or "PMC Only"
    reasons: List[str] = Field(default_factory=list)
    flags: List[VerificationFlag] = Field(default_factory=list)
    sources_checked: List[VerificationSource] = Field(default_factory=list)
    verified_by: Optional[VerificationSource] = None
    checked_at: Optional[datetime] = None
    cache_valid_until: Optional[datetime] = None


class JournalMetrics(BaseModel):
    """Quality metrics for a journal."""
    cited_by_count: Optional[int] = None
    works_count: Optional[int] = None
    h_index: Optional[int] = None
    i10_index: Optional[int] = None
    two_yr_mean_citedness: Optional[float] = None  # Similar to Impact Factor


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
    is_in_doaj: bool = False  # DOAJ verified (from OpenAlex)
    apc_usd: Optional[int] = None  # Article Processing Charge

    # Metrics
    metrics: JournalMetrics = Field(default_factory=JournalMetrics)

    # Trust & Safety Verification
    verification: Optional[VerificationStatus] = None

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

    # Privacy
    incognito_mode: bool = Field(
        default=False,
        description="When enabled, search history is not saved"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Deep Learning for Medical Image Analysis",
                "abstract": "This study explores the application of convolutional neural networks for automated detection of abnormalities in chest X-rays...",
                "keywords": ["deep learning", "medical imaging", "CNN"],
                "prefer_open_access": True,
                "incognito_mode": False
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
