"""
OpenAlex Service Package

Integration with the OpenAlex API for journal discovery
and bibliometric data retrieval.

Usage:
    # Recommended - direct function import
    from app.services.openalex import search_journals_by_text

    journals, discipline, field, confidence, disciplines, article_type = search_journals_by_text(
        title="Machine Learning in Healthcare",
        abstract="This paper explores...",
    )

    # Or use the service class (backward compatible)
    from app.services.openalex import openalex_service

    journals, discipline, field, confidence, disciplines, article_type = openalex_service.search_journals_by_text(
        title="...", abstract="..."
    )

Modules:
    - search: Main search functionality with OpenAlex ML discipline detection
    - journals: Journal operations (convert, categorize)
    - scoring: Relevance scoring algorithm
    - client: OpenAlex API client
    - config: Configuration
    - constants: Soft-boost keywords for scoring
    - utils: Utility functions
    - service: Service facade (backward compat)
"""

__version__ = "2.2.0"

# === Public API ===

# Topics API (Phase 1 enhancement)
from .topics import (
    TopicsService,
    TopicsAnalysisResult,
    DetectedSubfield,
    TopicHierarchy,
    get_topics_service,
    analyze_topics,
    get_multi_subfields,
)

# Keywords extraction (Phase 1 enhancement)
from .keywords import (
    KeywordsExtractor,
    RankedKeyword,
    get_keywords_extractor,
    extract_keywords,
    get_ranked_keywords,
)

# Concepts analysis (Phase 1 enhancement)
from .concepts import (
    ConceptsAnalyzer,
    Concept,
    ConceptsAnalysisResult,
    get_concepts_analyzer,
    analyze_concepts,
    get_discipline_hints,
)

# Main search functions
from .search import (
    search_journals_by_text,
    search_journals_by_keywords,
    find_journals_from_works,
    get_topic_ids_from_similar_works,
    find_journals_by_topics,
)

# Universal Mode search (works for ALL academic disciplines)
from .universal_search import (
    search_journals_universal,
    UniversalSearchResult,
    find_journals_by_subfield_id_universal,
    get_search_metadata,
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
    extract_search_terms_enhanced,
    extract_bigrams,
    extract_trigrams,
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

# Constants (soft-boost keywords for scoring)
from .constants import (
    RELEVANT_TOPIC_KEYWORDS,
    load_core_journals,
)

# Service class and global instance (backward compat)
from .service import OpenAlexService, openalex_service


__all__ = [
    # Version
    "__version__",
    # Topics API (Phase 1)
    "TopicsService",
    "TopicsAnalysisResult",
    "DetectedSubfield",
    "TopicHierarchy",
    "get_topics_service",
    "analyze_topics",
    "get_multi_subfields",
    # Keywords extraction (Phase 1)
    "KeywordsExtractor",
    "RankedKeyword",
    "get_keywords_extractor",
    "extract_keywords",
    "get_ranked_keywords",
    # Concepts analysis (Phase 1)
    "ConceptsAnalyzer",
    "Concept",
    "ConceptsAnalysisResult",
    "get_concepts_analyzer",
    "analyze_concepts",
    "get_discipline_hints",
    # Main search functions
    "search_journals_by_text",
    "search_journals_by_keywords",
    "find_journals_from_works",
    "get_topic_ids_from_similar_works",
    "find_journals_by_topics",
    # Universal Mode search
    "search_journals_universal",
    "UniversalSearchResult",
    "find_journals_by_subfield_id_universal",
    "get_search_metadata",
    # Journal operations
    "convert_to_journal",
    "categorize_journals",
    "merge_journal_results",
    # Scoring
    "calculate_relevance_score",
    # Utilities
    "extract_search_terms",
    "extract_search_terms_enhanced",
    "extract_bigrams",
    "extract_trigrams",
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
    "load_core_journals",
    # Service (backward compat)
    "OpenAlexService",
    "openalex_service",
]
