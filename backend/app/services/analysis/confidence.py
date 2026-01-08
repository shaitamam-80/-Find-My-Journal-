"""
Confidence Scoring System

Calculates confidence in analysis results to decide if LLM enrichment is needed.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceFactor:
    """A single factor contributing to confidence score."""

    name: str
    score: float  # 0.0 to 1.0
    weight: float  # Importance of this factor
    passed: bool  # Whether this factor meets threshold
    details: str = ""


@dataclass
class ConfidenceScore:
    """Overall confidence score with breakdown."""

    overall: float  # 0.0 to 1.0
    factors: List[ConfidenceFactor] = field(default_factory=list)
    needs_llm: bool = False
    llm_reasons: List[str] = field(default_factory=list)

    @property
    def is_high(self) -> bool:
        """Check if confidence is high enough (>= 0.7)."""
        return self.overall >= 0.7

    @property
    def is_medium(self) -> bool:
        """Check if confidence is medium (0.4 - 0.7)."""
        return 0.4 <= self.overall < 0.7

    @property
    def is_low(self) -> bool:
        """Check if confidence is low (< 0.4)."""
        return self.overall < 0.4


class ConfidenceScorer:
    """
    Calculate confidence in analysis results.

    Used to decide if LLM enrichment is needed.
    Higher confidence = OpenAlex results are sufficient.
    Lower confidence = LLM enrichment recommended.
    """

    # Thresholds for each factor
    THRESHOLDS = {
        "min_topics": 3,           # Minimum topics to consider reliable
        "min_works": 20,           # Minimum similar works found
        "min_keywords": 5,         # Minimum quality keywords extracted
        "discipline_confidence": 0.4,  # Minimum discipline detection confidence
        "keyword_min_length": 4,   # Minimum keyword length to count as quality
    }

    # Weights for combining factors (should sum to ~1.0)
    WEIGHTS = {
        "topics_found": 0.25,
        "works_count": 0.20,
        "keywords_quality": 0.20,
        "discipline_clarity": 0.25,
        "keyword_diversity": 0.10,
    }

    def score(
        self,
        topics_count: int,
        works_count: int,
        keywords: List[str],
        discipline_confidence: float,
        detected_disciplines_count: int = 1,
    ) -> ConfidenceScore:
        """
        Calculate confidence score from analysis results.

        Args:
            topics_count: Number of topics detected.
            works_count: Number of similar works found.
            keywords: List of extracted keywords.
            discipline_confidence: Confidence in top discipline (0-1).
            detected_disciplines_count: Number of disciplines detected.

        Returns:
            ConfidenceScore with overall score and breakdown.
        """
        factors: List[ConfidenceFactor] = []
        llm_reasons: List[str] = []

        # Factor 1: Topics found
        topics_score = min(topics_count / self.THRESHOLDS["min_topics"], 1.0)
        topics_passed = topics_count >= self.THRESHOLDS["min_topics"]
        factors.append(ConfidenceFactor(
            name="topics_found",
            score=topics_score,
            weight=self.WEIGHTS["topics_found"],
            passed=topics_passed,
            details=f"Found {topics_count} topics (threshold: {self.THRESHOLDS['min_topics']})",
        ))
        if not topics_passed:
            llm_reasons.append(f"Few topics found ({topics_count})")

        # Factor 2: Works count
        works_score = min(works_count / self.THRESHOLDS["min_works"], 1.0)
        works_passed = works_count >= self.THRESHOLDS["min_works"]
        factors.append(ConfidenceFactor(
            name="works_count",
            score=works_score,
            weight=self.WEIGHTS["works_count"],
            passed=works_passed,
            details=f"Found {works_count} similar works (threshold: {self.THRESHOLDS['min_works']})",
        ))
        if not works_passed:
            llm_reasons.append(f"Few similar works ({works_count})")

        # Factor 3: Keywords quality
        quality_keywords = [
            k for k in keywords
            if len(k) >= self.THRESHOLDS["keyword_min_length"]
        ]
        keywords_score = min(len(quality_keywords) / self.THRESHOLDS["min_keywords"], 1.0)
        keywords_passed = len(quality_keywords) >= self.THRESHOLDS["min_keywords"]
        factors.append(ConfidenceFactor(
            name="keywords_quality",
            score=keywords_score,
            weight=self.WEIGHTS["keywords_quality"],
            passed=keywords_passed,
            details=f"Found {len(quality_keywords)} quality keywords",
        ))
        if not keywords_passed:
            llm_reasons.append(f"Few quality keywords ({len(quality_keywords)})")

        # Factor 4: Discipline clarity
        discipline_passed = discipline_confidence >= self.THRESHOLDS["discipline_confidence"]
        factors.append(ConfidenceFactor(
            name="discipline_clarity",
            score=discipline_confidence,
            weight=self.WEIGHTS["discipline_clarity"],
            passed=discipline_passed,
            details=f"Discipline confidence: {discipline_confidence:.0%}",
        ))
        if not discipline_passed:
            llm_reasons.append(f"Low discipline confidence ({discipline_confidence:.0%})")

        # Factor 5: Keyword diversity (unique first letters as proxy)
        if keywords:
            first_letters = set(k[0].lower() for k in keywords if k)
            diversity_score = min(len(first_letters) / 5, 1.0)
        else:
            diversity_score = 0.0
        factors.append(ConfidenceFactor(
            name="keyword_diversity",
            score=diversity_score,
            weight=self.WEIGHTS["keyword_diversity"],
            passed=diversity_score >= 0.4,
            details=f"Keyword diversity score: {diversity_score:.0%}",
        ))

        # Check for interdisciplinary (multiple disciplines detected)
        if detected_disciplines_count >= 2:
            llm_reasons.append(f"Interdisciplinary paper ({detected_disciplines_count} disciplines)")

        # Calculate weighted overall score
        overall = sum(f.score * f.weight for f in factors)

        # Determine if LLM is needed
        needs_llm = overall < 0.5 or len(llm_reasons) >= 2

        result = ConfidenceScore(
            overall=overall,
            factors=factors,
            needs_llm=needs_llm,
            llm_reasons=llm_reasons,
        )

        logger.info(
            f"Confidence score: {overall:.0%}, "
            f"needs_llm: {needs_llm}, "
            f"reasons: {llm_reasons}"
        )

        return result

    def score_from_openalex_result(
        self,
        topics_result,  # TopicsAnalysisResult
        keywords: List[str],
    ) -> ConfidenceScore:
        """
        Calculate confidence from TopicsAnalysisResult.

        Convenience method for integration with topics.py.

        Args:
            topics_result: Result from TopicsService.analyze_topics_from_query.
            keywords: Extracted keywords.

        Returns:
            ConfidenceScore.
        """
        primary = topics_result.primary_subfield
        discipline_confidence = primary.confidence if primary else 0.0

        return self.score(
            topics_count=topics_result.total_topics_found,
            works_count=topics_result.works_analyzed,
            keywords=keywords,
            discipline_confidence=discipline_confidence,
            detected_disciplines_count=len(topics_result.all_subfields),
        )


# Global instance
_confidence_scorer: Optional[ConfidenceScorer] = None


def get_confidence_scorer() -> ConfidenceScorer:
    """Get or create global confidence scorer instance."""
    global _confidence_scorer
    if _confidence_scorer is None:
        _confidence_scorer = ConfidenceScorer()
    return _confidence_scorer


def calculate_confidence(
    topics_count: int,
    works_count: int,
    keywords: List[str],
    discipline_confidence: float,
) -> ConfidenceScore:
    """
    Calculate confidence score.

    Convenience function for ConfidenceScorer.score.
    """
    return get_confidence_scorer().score(
        topics_count=topics_count,
        works_count=works_count,
        keywords=keywords,
        discipline_confidence=discipline_confidence,
    )
