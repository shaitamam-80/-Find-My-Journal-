"""
Gemini LLM Services for Find My Journal.

Services:
- GeminiService: Journal explanation generation
- GeminiAnalysisService: Paper analysis enrichment (Phase 3)
"""
from .service import GeminiService, get_gemini_service
from .prompts import (
    generate_explanation_prompt,
    get_static_fallback,
    # Phase 3 prompt generators
    generate_paper_analysis_prompt,
    generate_abbreviation_prompt,
    generate_cross_discipline_prompt,
    generate_hebrew_analysis_prompt,
    generate_keyword_enhancement_prompt,
)
from .analysis_service import (
    GeminiAnalysisService,
    get_gemini_analysis_service,
    LLMEnrichmentResult,
    AbbreviationExpansion,
    CrossDiscipline,
    EnhancedKeyword,
)

__all__ = [
    # Original service
    "GeminiService",
    "get_gemini_service",
    "generate_explanation_prompt",
    "get_static_fallback",
    # Phase 3: Analysis service
    "GeminiAnalysisService",
    "get_gemini_analysis_service",
    "LLMEnrichmentResult",
    "AbbreviationExpansion",
    "CrossDiscipline",
    "EnhancedKeyword",
    # Phase 3: Prompt generators
    "generate_paper_analysis_prompt",
    "generate_abbreviation_prompt",
    "generate_cross_discipline_prompt",
    "generate_hebrew_analysis_prompt",
    "generate_keyword_enhancement_prompt",
]
