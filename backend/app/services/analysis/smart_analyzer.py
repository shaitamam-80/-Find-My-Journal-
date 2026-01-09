"""
Smart Analyzer - Main Orchestrator for Paper Analysis

Combines OpenAlex analysis with optional LLM enrichment.
This is the main entry point for enhanced paper analysis.

Phase 3: Now includes Gemini LLM integration for complex cases.
"""
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from app.services.openalex.topics import (
    TopicsService,
    TopicsAnalysisResult,
    DetectedSubfield,
    get_topics_service,
)
from app.services.openalex.keywords import (
    KeywordsExtractor,
    RankedKeyword,
    get_keywords_extractor,
)
from app.services.openalex.concepts import (
    ConceptsAnalyzer,
    get_concepts_analyzer,
)
from app.services.openalex.utils import extract_search_terms

from .confidence import ConfidenceScorer, ConfidenceScore, get_confidence_scorer
from .triggers import LLMTriggerDetector, TriggerResult, TriggerType, get_trigger_detector

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """
    Complete result of paper analysis.

    Contains all extracted information plus metadata about analysis quality.
    """

    # Extracted data
    keywords: List[RankedKeyword] = field(default_factory=list)
    search_terms: List[str] = field(default_factory=list)
    disciplines: List[DetectedSubfield] = field(default_factory=list)
    topic_ids: List[str] = field(default_factory=list)

    # Primary discipline (backward compat)
    primary_discipline: Optional[str] = None
    primary_field: Optional[str] = None
    discipline_confidence: float = 0.0

    # Concept hints
    discipline_hints: List[str] = field(default_factory=list)
    methodology_hints: List[str] = field(default_factory=list)

    # Quality metrics
    confidence: ConfidenceScore = None
    works_analyzed: int = 0
    topics_found: int = 0

    # LLM enrichment
    needs_llm_enrichment: bool = False
    enrichment_reasons: List[str] = field(default_factory=list)
    llm_enriched: bool = False
    llm_additions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "keywords": [k.keyword for k in self.keywords[:10]],
            "search_terms": self.search_terms[:10],
            "disciplines": [
                {
                    "name": d.subfield_name,
                    "field": d.field_name,
                    "confidence": d.confidence,
                }
                for d in self.disciplines[:5]
            ],
            "primary_discipline": self.primary_discipline,
            "primary_field": self.primary_field,
            "discipline_confidence": self.discipline_confidence,
            "confidence_score": self.confidence.overall if self.confidence else 0,
            "needs_llm_enrichment": self.needs_llm_enrichment,
            "enrichment_reasons": self.enrichment_reasons,
            "llm_enriched": self.llm_enriched,
        }


class SmartAnalyzer:
    """
    Main orchestrator for paper analysis.

    Combines:
    - OpenAlex Topics API for discipline detection
    - OpenAlex Keywords extraction
    - OpenAlex Concepts for additional signals
    - Confidence scoring
    - LLM trigger detection
    - Optional Gemini enrichment (Phase 3)
    """

    def __init__(
        self,
        enable_llm: bool = False,
        llm_provider: str = "gemini",
    ):
        """
        Initialize the SmartAnalyzer.

        Args:
            enable_llm: Whether to use LLM enrichment when triggered.
            llm_provider: Which LLM to use ("gemini", "openai", etc.).
        """
        self.enable_llm = enable_llm
        self.llm_provider = llm_provider

        # Services
        self.topics_service = get_topics_service()
        self.keywords_extractor = get_keywords_extractor()
        self.concepts_analyzer = get_concepts_analyzer()
        self.confidence_scorer = get_confidence_scorer()
        self.trigger_detector = get_trigger_detector()

    def analyze(
        self,
        title: str,
        abstract: str,
        user_keywords: List[str] = None,
        skip_llm: bool = False,
    ) -> AnalysisResult:
        """
        Analyze a paper to extract disciplines, keywords, and topics.

        This is the main entry point for paper analysis.

        Args:
            title: Paper title.
            abstract: Paper abstract.
            user_keywords: Optional user-provided keywords.
            skip_llm: Force skip LLM enrichment even if triggered.

        Returns:
            AnalysisResult with all extracted information.
        """
        result = AnalysisResult()
        combined_text = f"{title} {abstract}"

        # Step 1: Extract search terms
        user_kw = user_keywords or []
        result.search_terms = extract_search_terms(combined_text, user_kw)

        # Step 2: OpenAlex Topics analysis
        search_query = " ".join(result.search_terms[:8])
        topics_result = self.topics_service.analyze_topics_from_query(search_query)

        result.disciplines = topics_result.all_subfields
        result.topic_ids = topics_result.topic_ids
        result.works_analyzed = topics_result.works_analyzed
        result.topics_found = topics_result.total_topics_found

        # Set primary discipline
        if topics_result.primary_subfield:
            primary = topics_result.primary_subfield
            result.primary_discipline = primary.subfield_name
            result.primary_field = primary.field_name
            result.discipline_confidence = primary.confidence

        # Step 3: Keywords extraction
        ranked_keywords = self.keywords_extractor.extract_from_works(
            search_query, max_works=30
        )
        if user_kw:
            ranked_keywords = self.keywords_extractor.merge_with_user_keywords(
                ranked_keywords, user_kw
            )
        result.keywords = self.keywords_extractor.rank_keywords(ranked_keywords)

        # Step 4: Concepts analysis for additional hints
        result.discipline_hints = self.concepts_analyzer.get_discipline_hints(search_query)
        result.methodology_hints = self.concepts_analyzer.get_methodology_hints(search_query)

        # Step 5: Confidence scoring
        keyword_strings = [k.keyword for k in result.keywords]
        result.confidence = self.confidence_scorer.score(
            topics_count=result.topics_found,
            works_count=result.works_analyzed,
            keywords=keyword_strings,
            discipline_confidence=result.discipline_confidence,
            detected_disciplines_count=len(result.disciplines),
        )

        # Step 6: LLM trigger detection (get full results for enrichment)
        trigger_results = self.trigger_detector.detect_all(
            text=combined_text,
            title=title,
            confidence_score=result.confidence.overall,
            topics_count=result.topics_found,
            disciplines_count=len(result.disciplines),
        )

        # Determine if LLM should be used
        activated = [r for r in trigger_results if r.activated]
        high_priority = {TriggerType.LOW_CONFIDENCE, TriggerType.NON_ENGLISH}
        has_high_priority = any(r.trigger_type in high_priority for r in activated)
        should_llm = len(activated) >= 2 or has_high_priority

        result.needs_llm_enrichment = should_llm
        result.enrichment_reasons = [r.details for r in activated]

        # Step 7: LLM enrichment (if enabled and triggered)
        if self.enable_llm and should_llm and not skip_llm:
            result = self._enrich_with_llm(
                result, title, abstract, user_kw, trigger_results
            )

        # Log summary
        logger.info(
            f"Analysis complete: "
            f"discipline={result.primary_discipline}, "
            f"confidence={result.confidence.overall:.0%}, "
            f"keywords={len(result.keywords)}, "
            f"needs_llm={result.needs_llm_enrichment}"
        )

        return result

    def _enrich_with_llm(
        self,
        result: AnalysisResult,
        title: str,
        abstract: str,
        user_keywords: List[str],
        trigger_results: List[TriggerResult] = None,
    ) -> AnalysisResult:
        """
        Enrich analysis with LLM via Gemini.

        Phase 3: Full implementation with GeminiAnalysisService.

        Args:
            result: Current analysis result.
            title: Paper title.
            abstract: Paper abstract.
            user_keywords: User keywords.
            trigger_results: Detailed trigger detection results.

        Returns:
            Enriched AnalysisResult.
        """
        # Import here to avoid circular imports
        from app.services.gemini import (
            get_gemini_analysis_service,
            LLMEnrichmentResult,
        )

        analysis_service = get_gemini_analysis_service()

        if not analysis_service.is_configured:
            logger.warning("Gemini not configured, skipping LLM enrichment")
            result.llm_enriched = False
            result.llm_additions = {
                "note": "Gemini API not configured",
                "would_address": result.enrichment_reasons,
            }
            return result

        # Determine which enrichments to run based on triggers
        trigger_results = trigger_results or []
        activated_triggers = {r.trigger_type for r in trigger_results if r.activated}

        # Extract abbreviations from trigger results
        abbreviations = []
        for tr in trigger_results:
            if tr.trigger_type == TriggerType.ABBREVIATIONS and tr.extracted_items:
                abbreviations = tr.extracted_items
                break

        # Check for Hebrew/non-English
        has_hebrew = TriggerType.NON_ENGLISH in activated_triggers

        # Check for cross-disciplinary
        is_cross = TriggerType.CROSS_DISCIPLINARY in activated_triggers

        # Run async enrichment in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            enrichment: LLMEnrichmentResult = loop.run_until_complete(
                analysis_service.enrich_analysis(
                    title=title,
                    abstract=abstract,
                    discipline=result.primary_discipline or "Unknown",
                    confidence=result.confidence.overall if result.confidence else 0.0,
                    keywords=[k.keyword for k in result.keywords],
                    topics_count=result.topics_found,
                    abbreviations=abbreviations,
                    has_hebrew=has_hebrew,
                    is_cross_disciplinary=is_cross,
                )
            )

            # Apply enrichment to result
            result.llm_enriched = True
            result.llm_additions = enrichment.to_dict()

            # Merge additional keywords
            if enrichment.additional_keywords:
                existing_kw = {k.keyword.lower() for k in result.keywords}
                for kw in enrichment.additional_keywords:
                    if kw.lower() not in existing_kw:
                        result.keywords.append(
                            RankedKeyword(
                                keyword=kw,
                                score=0.5,  # Medium score for LLM keywords
                                frequency=1,
                                source="llm",
                            )
                        )

            # Update confidence if LLM provided boost
            if enrichment.confidence_boost > 0 and result.confidence:
                result.confidence.overall = min(
                    1.0, result.confidence.overall + enrichment.confidence_boost
                )

            # Add cross-discipline info
            if enrichment.cross_disciplines:
                for cd in enrichment.cross_disciplines:
                    if cd.level == "primary" and cd.name != result.primary_discipline:
                        # Add as secondary discipline
                        result.disciplines.append(
                            DetectedSubfield(
                                subfield_name=cd.name,
                                subfield_id="llm-detected",
                                field_name=cd.name,
                                field_id="llm-detected",
                                domain_name="",
                                domain_id="",
                                confidence=0.6,
                                works_count=0,
                            )
                        )

            logger.info(
                f"LLM enrichment complete: {len(enrichment.enrichment_sources)} sources, "
                f"{len(enrichment.additional_keywords)} new keywords"
            )

        except Exception as e:
            logger.error(f"LLM enrichment failed: {e}")
            result.llm_enriched = False
            result.llm_additions = {
                "error": str(e),
                "would_address": result.enrichment_reasons,
            }

        return result

    def get_analysis_summary(self, result: AnalysisResult) -> str:
        """
        Generate human-readable summary of analysis.

        Args:
            result: Analysis result.

        Returns:
            Summary string.
        """
        lines = [
            f"Discipline: {result.primary_discipline or 'Unknown'}",
            f"Field: {result.primary_field or 'Unknown'}",
            f"Confidence: {result.confidence.overall:.0%}" if result.confidence else "N/A",
            f"Keywords: {', '.join(k.keyword for k in result.keywords[:5])}",
        ]

        if result.disciplines and len(result.disciplines) > 1:
            secondary = [d.subfield_name for d in result.disciplines[1:3]]
            lines.append(f"Secondary disciplines: {', '.join(secondary)}")

        if result.needs_llm_enrichment:
            lines.append(f"LLM enrichment recommended: {', '.join(result.enrichment_reasons)}")

        return "\n".join(lines)


# Global instance
_smart_analyzer: Optional[SmartAnalyzer] = None


def get_smart_analyzer(enable_llm: bool = False) -> SmartAnalyzer:
    """Get or create global smart analyzer instance."""
    global _smart_analyzer
    if _smart_analyzer is None:
        _smart_analyzer = SmartAnalyzer(enable_llm=enable_llm)
    return _smart_analyzer


def analyze_paper(
    title: str,
    abstract: str,
    keywords: List[str] = None,
) -> AnalysisResult:
    """
    Analyze a paper using the SmartAnalyzer.

    Convenience function for SmartAnalyzer.analyze.

    Args:
        title: Paper title.
        abstract: Paper abstract.
        keywords: Optional user keywords.

    Returns:
        AnalysisResult.
    """
    return get_smart_analyzer().analyze(title, abstract, keywords)
