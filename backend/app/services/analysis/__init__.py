"""
Analysis Services for Find My Journal

Article type detection, topic validation, dynamic statistics,
and smart analysis orchestration.
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

# Smart Analyzer (Phase 2)
from .smart_analyzer import (
    SmartAnalyzer,
    AnalysisResult,
    get_smart_analyzer,
    analyze_paper,
)

# Confidence Scoring (Phase 2)
from .confidence import (
    ConfidenceScorer,
    ConfidenceScore,
    ConfidenceFactor,
    get_confidence_scorer,
    calculate_confidence,
)

# LLM Trigger Detection (Phase 2)
from .triggers import (
    LLMTriggerDetector,
    TriggerResult,
    TriggerType,
    get_trigger_detector,
    should_use_llm,
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
    # Smart Analyzer (Phase 2)
    "SmartAnalyzer",
    "AnalysisResult",
    "get_smart_analyzer",
    "analyze_paper",
    # Confidence Scoring (Phase 2)
    "ConfidenceScorer",
    "ConfidenceScore",
    "ConfidenceFactor",
    "get_confidence_scorer",
    "calculate_confidence",
    # LLM Trigger Detection (Phase 2)
    "LLMTriggerDetector",
    "TriggerResult",
    "TriggerType",
    "get_trigger_detector",
    "should_use_llm",
]
