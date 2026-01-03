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

    # Match Details (Story 1.1 - Why it's a good fit)
    match_details: List[str] = Field(
        default_factory=list,
        description="Detailed reasons why this journal matches the search"
    )
    matched_topics: List[str] = Field(
        default_factory=list,
        description="Topics that matched between the paper and journal"
    )


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


class DisciplineDetection(BaseModel):
    """Auto-detected discipline with confidence (Story 2.1)."""
    name: str = Field(..., description="Detected discipline/subfield name")
    field: Optional[str] = Field(None, description="Parent field (e.g., Medicine)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    source: str = Field(default="openalex", description="Detection source")


class DetectedDisciplineInfo(BaseModel):
    """Multi-discipline detection result."""
    name: str = Field(..., description="Discipline name (e.g., 'Urology')")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    evidence: List[str] = Field(default_factory=list, description="Keywords that led to detection")
    openalex_field_id: Optional[str] = None
    openalex_subfield_id: Optional[str] = None


class ArticleTypeInfo(BaseModel):
    """Detected article type information."""
    type: str = Field(..., description="Article type ID (e.g., 'systematic_review')")
    display_name: str = Field(..., description="Human-readable type name")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    evidence: List[str] = Field(default_factory=list, description="Patterns that matched")
    preferred_journal_types: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Response from journal search."""

    query: str
    discipline: Optional[str] = None
    discipline_detection: Optional[DisciplineDetection] = None  # Story 2.1 (backward compat)
    detected_disciplines: List[DetectedDisciplineInfo] = Field(
        default_factory=list,
        description="All detected disciplines with confidence scores"
    )
    article_type: Optional[ArticleTypeInfo] = Field(
        None,
        description="Detected article type (SR, RCT, cohort, etc.)"
    )
    total_found: int
    journals: List[Journal]
    search_id: Optional[str] = None  # For logging


# =============================================================================
# Saved Searches (Story 4.1)
# =============================================================================

class SavedSearch(BaseModel):
    """A saved search for quick access (Story 4.1)."""
    id: str = Field(..., description="UUID of the saved search")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="User-given name for this search")
    title: str = Field(..., description="Original article title")
    abstract: str = Field(..., description="Original abstract")
    keywords: List[str] = Field(default_factory=list)
    discipline: Optional[str] = None
    results_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SaveSearchRequest(BaseModel):
    """Request to save a search (Story 4.1)."""
    name: str = Field(..., min_length=1, max_length=100, description="Name for this search")
    title: str = Field(..., description="Article title from the search")
    abstract: str = Field(..., description="Abstract from the search")
    keywords: List[str] = Field(default_factory=list)
    discipline: Optional[str] = None
    results_count: int = 0


class SavedSearchResponse(BaseModel):
    """Response with saved search data (Story 4.1)."""
    id: str
    name: str
    title: str
    discipline: Optional[str]
    results_count: int
    created_at: str


# =============================================================================
# Feedback Rating (Story 5.1)
# =============================================================================

class FeedbackRating(str, Enum):
    """Thumbs up/down feedback rating."""
    UP = "up"
    DOWN = "down"


class FeedbackRequest(BaseModel):
    """Request to submit feedback on a journal recommendation (Story 5.1)."""
    journal_id: str = Field(..., description="OpenAlex journal ID")
    rating: FeedbackRating = Field(..., description="Thumbs up or down")
    search_id: Optional[str] = Field(None, description="Search ID for context")


class FeedbackResponse(BaseModel):
    """Response after submitting feedback (Story 5.1)."""
    id: str
    journal_id: str
    rating: str
    created_at: str
