"""
Analysis Services for Find My Journal

Multi-discipline detection, article type detection, and topic validation.
"""

from .discipline_detector import (
    MultiDisciplineDetector,
    DetectedDiscipline,
    detect_disciplines,
    DISCIPLINE_KEYWORDS,
    OPENALEX_FIELD_MAPPING,
)

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

__all__ = [
    # Discipline detection
    "MultiDisciplineDetector",
    "DetectedDiscipline",
    "detect_disciplines",
    "DISCIPLINE_KEYWORDS",
    "OPENALEX_FIELD_MAPPING",
    # Article type detection
    "ArticleTypeDetector",
    "DetectedArticleType",
    "detect_article_type",
    "ARTICLE_TYPE_PATTERNS",
    # Topic validation
    "TopicRelevanceValidator",
    "validate_topics",
]
