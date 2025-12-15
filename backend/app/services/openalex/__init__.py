"""
OpenAlex Service Package

Integration with the OpenAlex API for journal discovery
and bibliometric data retrieval.

Usage:
    # Recommended - direct function import
    from app.services.openalex import search_journals_by_text

    journals, discipline = search_journals_by_text(
        title="Machine Learning in Healthcare",
        abstract="This paper explores...",
    )

    # Or use the service class (backward compatible)
    from app.services.openalex import openalex_service

    journals, discipline = openalex_service.search_journals_by_text(
        title="...", abstract="..."
    )

Modules:
    - search: Main search functionality
    - journals: Journal operations (convert, categorize)
    - scoring: Relevance scoring algorithm
    - client: OpenAlex API client
    - config: Configuration
    - constants: Domain knowledge (keywords, disciplines)
    - utils: Utility functions
    - service: Service facade (backward compat)
"""

__version__ = "2.0.0"

# === Public API ===

# Main search functions
from .search import (
    search_journals_by_text,
    search_journals_by_keywords,
    find_journals_from_works,
    get_topic_ids_from_similar_works,
    find_journals_by_topics,
)

# Journal operations
from .journals import (
    convert_to_journal,
    categorize_journals,
    merge_journal_results,
)

# Scoring
from .scoring import calculate_relevance_score

# Utilities
from .utils import (
    extract_search_terms,
    detect_discipline,
    normalize_journal_name,
)

# Client
from .client import (
    OpenAlexClient,
    get_client,
)

# Configuration
from .config import (
    OpenAlexConfig,
    get_config,
    get_max_results,
    get_min_journal_works,
)

# Constants
from .constants import (
    RELEVANT_TOPIC_KEYWORDS,
    DISCIPLINE_KEYWORDS,
    load_core_journals,
)

# Service class and global instance (backward compat)
from .service import OpenAlexService, openalex_service


__all__ = [
    # Version
    "__version__",
    # Main search functions
    "search_journals_by_text",
    "search_journals_by_keywords",
    "find_journals_from_works",
    "get_topic_ids_from_similar_works",
    "find_journals_by_topics",
    # Journal operations
    "convert_to_journal",
    "categorize_journals",
    "merge_journal_results",
    # Scoring
    "calculate_relevance_score",
    # Utilities
    "extract_search_terms",
    "detect_discipline",
    "normalize_journal_name",
    # Client
    "OpenAlexClient",
    "get_client",
    # Configuration
    "OpenAlexConfig",
    "get_config",
    "get_max_results",
    "get_min_journal_works",
    # Constants
    "RELEVANT_TOPIC_KEYWORDS",
    "DISCIPLINE_KEYWORDS",
    "load_core_journals",
    # Service (backward compat)
    "OpenAlexService",
    "openalex_service",
]
