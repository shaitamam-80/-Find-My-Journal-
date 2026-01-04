"""
Analysis Services for Find My Journal

Multi-discipline detection, article type detection, and topic validation.
Includes Universal Mode detection using OpenAlex ML classification.
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

# Universal Mode (OpenAlex ML-based detection)
from .universal_detector import (
    UniversalDisciplineDetector,
    DetectedSubfield,
    UniversalDetectionResult,
    detect_disciplines_universal,
)

from .hybrid_detector import (
    HybridDisciplineDetector,
    detect_disciplines_hybrid,
    detect_disciplines_merged,
)

__all__ = [
    # Discipline detection (keyword-based)
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
    # Universal Mode (OpenAlex ML-based)
    "UniversalDisciplineDetector",
    "DetectedSubfield",
    "UniversalDetectionResult",
    "detect_disciplines_universal",
    # Hybrid detection
    "HybridDisciplineDetector",
    "detect_disciplines_hybrid",
    "detect_disciplines_merged",
]
