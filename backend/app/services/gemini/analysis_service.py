"""
Gemini Analysis Service - LLM enrichment for paper analysis.

Phase 3: Provides intelligent enrichment when OpenAlex results
need additional processing (low confidence, abbreviations, etc.)
"""
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from app.core.config import get_settings
from .prompts import (
    generate_paper_analysis_prompt,
    generate_abbreviation_prompt,
    generate_cross_discipline_prompt,
    generate_hebrew_analysis_prompt,
    generate_keyword_enhancement_prompt,
)

logger = logging.getLogger(__name__)


@dataclass
class AbbreviationExpansion:
    """Expanded abbreviation with context."""

    abbreviation: str
    expansion: str
    field: str = ""
    definition: str = ""


@dataclass
class CrossDiscipline:
    """Detected cross-discipline connection."""

    name: str
    level: str  # primary, secondary, tertiary
    connection: str
    journal_types: List[str] = field(default_factory=list)


@dataclass
class EnhancedKeyword:
    """Enhanced keyword with metadata."""

    term: str
    keyword_type: str  # synonym, broader, narrower, methodology
    rationale: str = ""


@dataclass
class LLMEnrichmentResult:
    """Result of LLM enrichment analysis."""

    # From paper analysis
    additional_keywords: List[str] = field(default_factory=list)
    methodology_type: str = ""
    specific_methods: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=list)
    confidence_boost: float = 0.0

    # From abbreviation expansion
    abbreviation_expansions: List[AbbreviationExpansion] = field(default_factory=list)

    # From cross-discipline detection
    cross_disciplines: List[CrossDiscipline] = field(default_factory=list)
    is_interdisciplinary: bool = False
    recommended_primary_field: str = ""

    # From Hebrew analysis
    translated_title: str = ""
    translated_abstract: str = ""
    hebrew_keywords: List[str] = field(default_factory=list)
    has_israel_context: bool = False

    # From keyword enhancement
    enhanced_keywords: List[EnhancedKeyword] = field(default_factory=list)
    suggested_search_query: str = ""

    # Metadata
    enrichment_sources: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "additional_keywords": self.additional_keywords,
            "methodology": {
                "type": self.methodology_type,
                "specific_methods": self.specific_methods,
            },
            "target_audience": self.target_audience,
            "confidence_boost": self.confidence_boost,
            "abbreviations": [
                {
                    "abbr": a.abbreviation,
                    "expansion": a.expansion,
                    "field": a.field,
                }
                for a in self.abbreviation_expansions
            ],
            "cross_disciplines": [
                {
                    "name": d.name,
                    "level": d.level,
                    "connection": d.connection,
                }
                for d in self.cross_disciplines
            ],
            "is_interdisciplinary": self.is_interdisciplinary,
            "translation": {
                "title": self.translated_title,
                "has_translation": bool(self.translated_title),
            },
            "enhanced_keywords": [k.term for k in self.enhanced_keywords],
            "enrichment_sources": self.enrichment_sources,
        }


class GeminiAnalysisService:
    """
    Service for LLM-based paper analysis enrichment.

    Uses Gemini to enhance OpenAlex results when:
    - Confidence is low
    - Unknown abbreviations detected
    - Cross-disciplinary paper suspected
    - Non-English text (Hebrew, etc.) detected
    - Keywords need enhancement
    """

    _instance: Optional["GeminiAnalysisService"] = None
    _model = None
    _initialized: bool = False

    def __new__(cls) -> "GeminiAnalysisService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            settings = get_settings()
            if settings.gemini_api_key:
                try:
                    import google.generativeai as genai

                    genai.configure(api_key=settings.gemini_api_key)
                    # Use flash model for faster, cheaper analysis
                    self._model = genai.GenerativeModel("gemini-2.0-flash")
                    logger.info("GeminiAnalysisService initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini: {e}")
                    self._model = None
            else:
                logger.warning("Gemini API key not configured")
            self._initialized = True

    @property
    def is_configured(self) -> bool:
        """Check if Gemini is properly configured."""
        return self._model is not None

    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """
        Parse JSON from LLM response, handling markdown code blocks.

        Args:
            text: Raw LLM response text.

        Returns:
            Parsed JSON dict or None if parsing fails.
        """
        # Try to extract JSON from markdown code block
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if json_match:
            text = json_match.group(1)

        # Clean up and parse
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}")
            return None

    async def analyze_paper(
        self,
        title: str,
        abstract: str,
        discipline: str = "Unknown",
        confidence: float = 0.0,
        keywords: List[str] = None,
        topics_count: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """
        Comprehensive paper analysis via LLM.

        Args:
            title: Paper title.
            abstract: Paper abstract.
            discipline: Detected discipline from OpenAlex.
            confidence: Confidence score.
            keywords: Current keywords.
            topics_count: Number of topics found.

        Returns:
            Analysis result dict or None on error.
        """
        if not self.is_configured:
            return None

        prompt = generate_paper_analysis_prompt(
            title=title,
            abstract=abstract,
            discipline=discipline,
            confidence=confidence,
            keywords=keywords or [],
            topics_count=topics_count,
        )

        try:
            response = await self._model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 1000,
                    "top_p": 0.95,
                },
            )

            result = self._parse_json_response(response.text)
            if result:
                logger.info("Paper analysis completed via Gemini")
            return result

        except Exception as e:
            logger.error(f"Paper analysis error: {e}")
            return None

    async def expand_abbreviations(
        self,
        title: str,
        abstract: str,
        discipline: str,
        abbreviations: List[str],
    ) -> List[AbbreviationExpansion]:
        """
        Expand unknown abbreviations via LLM.

        Args:
            title: Paper title.
            abstract: Paper abstract.
            discipline: Detected discipline.
            abbreviations: List of unknown abbreviations to expand.

        Returns:
            List of AbbreviationExpansion objects.
        """
        if not self.is_configured or not abbreviations:
            return []

        prompt = generate_abbreviation_prompt(
            title=title,
            abstract=abstract,
            discipline=discipline,
            abbreviations=abbreviations,
        )

        try:
            response = await self._model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.1,  # Low temp for accuracy
                    "max_output_tokens": 800,
                },
            )

            result = self._parse_json_response(response.text)
            if result and "expansions" in result:
                expansions = []
                for exp in result["expansions"]:
                    expansions.append(
                        AbbreviationExpansion(
                            abbreviation=exp.get("abbreviation", ""),
                            expansion=exp.get("expansion", ""),
                            field=exp.get("field", ""),
                            definition=exp.get("definition", ""),
                        )
                    )
                logger.info(f"Expanded {len(expansions)} abbreviations")
                return expansions

        except Exception as e:
            logger.error(f"Abbreviation expansion error: {e}")

        return []

    async def detect_cross_disciplines(
        self,
        title: str,
        abstract: str,
        primary_discipline: str,
        confidence: float,
    ) -> tuple[List[CrossDiscipline], bool, str]:
        """
        Detect cross-disciplinary connections via LLM.

        Args:
            title: Paper title.
            abstract: Paper abstract.
            primary_discipline: Primary discipline from OpenAlex.
            confidence: Confidence in primary discipline.

        Returns:
            Tuple of (disciplines list, is_interdisciplinary, recommended_field)
        """
        if not self.is_configured:
            return [], False, ""

        prompt = generate_cross_discipline_prompt(
            title=title,
            abstract=abstract,
            primary_discipline=primary_discipline,
            confidence=confidence,
        )

        try:
            response = await self._model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 800,
                },
            )

            result = self._parse_json_response(response.text)
            if result:
                disciplines = []
                for d in result.get("disciplines", []):
                    disciplines.append(
                        CrossDiscipline(
                            name=d.get("name", ""),
                            level=d.get("level", ""),
                            connection=d.get("connection", ""),
                            journal_types=d.get("journal_types", []),
                        )
                    )

                is_inter = result.get("is_truly_interdisciplinary", False)
                recommended = result.get("recommended_primary_field", "")

                logger.info(
                    f"Cross-discipline detection: {len(disciplines)} fields, "
                    f"interdisciplinary={is_inter}"
                )
                return disciplines, is_inter, recommended

        except Exception as e:
            logger.error(f"Cross-discipline detection error: {e}")

        return [], False, ""

    async def analyze_hebrew_text(
        self,
        title: str,
        abstract: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze Hebrew/bilingual text via LLM.

        Args:
            title: Paper title (may contain Hebrew).
            abstract: Paper abstract (may contain Hebrew).

        Returns:
            Analysis result with translations and keywords.
        """
        if not self.is_configured:
            return None

        prompt = generate_hebrew_analysis_prompt(title=title, abstract=abstract)

        try:
            response = await self._model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 1200,
                },
            )

            result = self._parse_json_response(response.text)
            if result:
                logger.info("Hebrew text analysis completed")
            return result

        except Exception as e:
            logger.error(f"Hebrew analysis error: {e}")
            return None

    async def enhance_keywords(
        self,
        title: str,
        abstract: str,
        discipline: str,
        current_keywords: List[str],
        query: str = "",
    ) -> tuple[List[EnhancedKeyword], str]:
        """
        Enhance keywords via LLM for better search.

        Args:
            title: Paper title.
            abstract: Paper abstract.
            discipline: Detected discipline.
            current_keywords: Current keyword list.
            query: Current search query.

        Returns:
            Tuple of (enhanced keywords list, suggested query)
        """
        if not self.is_configured or not current_keywords:
            return [], ""

        prompt = generate_keyword_enhancement_prompt(
            title=title,
            abstract=abstract,
            discipline=discipline,
            current_keywords=current_keywords,
            query=query,
        )

        try:
            response = await self._model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 800,
                },
            )

            result = self._parse_json_response(response.text)
            if result:
                keywords = []
                for kw in result.get("enhanced_keywords", []):
                    keywords.append(
                        EnhancedKeyword(
                            term=kw.get("term", ""),
                            keyword_type=kw.get("type", ""),
                            rationale=kw.get("rationale", ""),
                        )
                    )

                suggested_query = result.get("suggested_search_query", "")
                logger.info(f"Enhanced keywords: {len(keywords)} suggestions")
                return keywords, suggested_query

        except Exception as e:
            logger.error(f"Keyword enhancement error: {e}")

        return [], ""

    async def enrich_analysis(
        self,
        title: str,
        abstract: str,
        discipline: str = "Unknown",
        confidence: float = 0.0,
        keywords: List[str] = None,
        topics_count: int = 0,
        abbreviations: List[str] = None,
        has_hebrew: bool = False,
        is_cross_disciplinary: bool = False,
    ) -> LLMEnrichmentResult:
        """
        Full enrichment pipeline based on triggers.

        Runs only the necessary LLM calls based on detected triggers.

        Args:
            title: Paper title.
            abstract: Paper abstract.
            discipline: Primary discipline.
            confidence: Confidence score.
            keywords: Current keywords.
            topics_count: Topics found.
            abbreviations: Unknown abbreviations to expand.
            has_hebrew: Whether Hebrew text was detected.
            is_cross_disciplinary: Whether cross-discipline was detected.

        Returns:
            LLMEnrichmentResult with all enrichment data.
        """
        result = LLMEnrichmentResult()
        keywords = keywords or []

        # 1. Paper analysis (if low confidence or few topics)
        if confidence < 0.5 or topics_count < 3:
            analysis = await self.analyze_paper(
                title=title,
                abstract=abstract,
                discipline=discipline,
                confidence=confidence,
                keywords=keywords,
                topics_count=topics_count,
            )
            if analysis:
                result.additional_keywords = analysis.get("additional_keywords", [])
                methodology = analysis.get("methodology", {})
                result.methodology_type = methodology.get("type", "")
                result.specific_methods = methodology.get("specific_methods", [])
                result.target_audience = analysis.get("target_audience", [])
                result.confidence_boost = analysis.get("confidence_boost", 0)
                result.enrichment_sources.append("paper_analysis")

        # 2. Abbreviation expansion
        if abbreviations:
            expansions = await self.expand_abbreviations(
                title=title,
                abstract=abstract,
                discipline=discipline,
                abbreviations=abbreviations,
            )
            result.abbreviation_expansions = expansions
            if expansions:
                result.enrichment_sources.append("abbreviation_expansion")

        # 3. Cross-discipline detection
        if is_cross_disciplinary or confidence < 0.6:
            disciplines, is_inter, recommended = await self.detect_cross_disciplines(
                title=title,
                abstract=abstract,
                primary_discipline=discipline,
                confidence=confidence,
            )
            result.cross_disciplines = disciplines
            result.is_interdisciplinary = is_inter
            result.recommended_primary_field = recommended
            if disciplines:
                result.enrichment_sources.append("cross_discipline")

        # 4. Hebrew text analysis
        if has_hebrew:
            hebrew_result = await self.analyze_hebrew_text(
                title=title,
                abstract=abstract,
            )
            if hebrew_result:
                translation = hebrew_result.get("translation", {})
                result.translated_title = translation.get("title_en", "")
                result.translated_abstract = translation.get("abstract_en", "")
                kw = hebrew_result.get("keywords", {})
                result.hebrew_keywords = kw.get("hebrew", [])
                # Add English keywords to additional
                result.additional_keywords.extend(kw.get("english", []))
                israel = hebrew_result.get("israel_context", {})
                result.has_israel_context = israel.get("has_local_context", False)
                result.enrichment_sources.append("hebrew_analysis")

        # 5. Keyword enhancement (if still low confidence)
        if confidence < 0.5 and len(keywords) < 5:
            enhanced, suggested = await self.enhance_keywords(
                title=title,
                abstract=abstract,
                discipline=discipline,
                current_keywords=keywords,
            )
            result.enhanced_keywords = enhanced
            result.suggested_search_query = suggested
            if enhanced:
                result.enrichment_sources.append("keyword_enhancement")

        logger.info(
            f"Enrichment complete: {len(result.enrichment_sources)} sources used"
        )
        return result


# Global instance
_analysis_service: Optional[GeminiAnalysisService] = None


def get_gemini_analysis_service() -> GeminiAnalysisService:
    """Get or create global GeminiAnalysisService instance."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = GeminiAnalysisService()
    return _analysis_service
