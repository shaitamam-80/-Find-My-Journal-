"""
Analysis Services for Find My Journal

Article type detection, topic validation, and dynamic statistics.
Discipline detection now uses OpenAlex ML directly via openalex.search module.
"""

from .article_type_detector import (
    ArticleTypeDetector,
    DetectedArticleType,
    detect_article_type,
    ARTICLE_TYPE_PATTERNS,
)

from .topic_validator import (
    TopicRelevanceValidator,
    validate_topics,
)

# Dynamic Statistics (Phase U2)
from .dynamic_stats import (
    DynamicStatsCalculator,
    SubfieldStats,
    get_stats_calculator,
    get_subfield_stats,
    calculate_percentile_score,
)

__all__ = [
    # Article type detection
    "ArticleTypeDetector",
    "DetectedArticleType",
    "detect_article_type",
    "ARTICLE_TYPE_PATTERNS",
    # Topic validation
    "TopicRelevanceValidator",
    "validate_topics",
    # Dynamic Statistics
    "DynamicStatsCalculator",
    "SubfieldStats",
    "get_stats_calculator",
    "get_subfield_stats",
    "calculate_percentile_score",
]
