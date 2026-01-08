"""
LLM Trigger Detection

Detects when LLM enrichment is needed for paper analysis.
"""
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of triggers that can activate LLM enrichment."""

    LOW_CONFIDENCE = "low_confidence"
    ABBREVIATIONS = "abbreviations_detected"
    CROSS_DISCIPLINARY = "cross_disciplinary"
    NON_ENGLISH = "non_english"
    FEW_TOPICS = "few_topics"
    AMBIGUOUS_TERMS = "ambiguous_terms"
    SHORT_TEXT = "short_text"
    TECHNICAL_JARGON = "technical_jargon"


@dataclass
class TriggerResult:
    """Result of a trigger detection."""

    trigger_type: TriggerType
    activated: bool
    confidence: float  # How confident we are this trigger applies
    details: str
    extracted_items: List[str] = None  # e.g., detected abbreviations

    def __post_init__(self):
        if self.extracted_items is None:
            self.extracted_items = []


class LLMTriggerDetector:
    """
    Detect when LLM enrichment is needed.

    Triggers are conditions that suggest OpenAlex results alone
    may not be sufficient for accurate analysis.
    """

    # Common academic abbreviations that may need expansion
    KNOWN_ABBREVIATIONS: Set[str] = {
        # Medical
        "COPD", "HIV", "AIDS", "COVID", "MRI", "CT", "ECG", "EEG",
        "DNA", "RNA", "PCR", "ELISA", "BMI", "BP", "HR", "ICU",
        "ED", "ER", "OR", "OCD", "PTSD", "ADHD", "ASD", "MS",
        # Technology
        "AI", "ML", "DL", "NLP", "CNN", "RNN", "GAN", "BERT",
        "GPT", "LLM", "API", "CPU", "GPU", "RAM", "IoT", "VR", "AR",
        # Research
        "RCT", "RQ", "IRB", "ANOVA", "SEM", "CFA", "EFA", "IRT",
        "MCAR", "MAR", "MNAR", "ICC", "ROC", "AUC", "CI", "SD",
        # Organizations
        "WHO", "CDC", "FDA", "NIH", "NSF", "EU", "UN", "OECD",
    }

    # Patterns for detecting unknown abbreviations
    ABBREVIATION_PATTERN = re.compile(r"\b[A-Z]{2,6}\b")

    # Hebrew/Arabic character ranges for non-English detection
    NON_ENGLISH_PATTERNS = [
        re.compile(r"[\u0590-\u05FF]"),  # Hebrew
        re.compile(r"[\u0600-\u06FF]"),  # Arabic
        re.compile(r"[\u4E00-\u9FFF]"),  # Chinese
        re.compile(r"[\u3040-\u309F\u30A0-\u30FF]"),  # Japanese
        re.compile(r"[\uAC00-\uD7AF]"),  # Korean
    ]

    # Ambiguous terms that may have multiple meanings
    AMBIGUOUS_TERMS: Set[str] = {
        "cell", "culture", "model", "network", "agent", "field",
        "domain", "system", "process", "function", "structure",
        "pattern", "learning", "memory", "attention", "control",
        "development", "growth", "expression", "signal", "channel",
    }

    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the trigger detector.

        Args:
            confidence_threshold: Threshold for LOW_CONFIDENCE trigger.
        """
        self.confidence_threshold = confidence_threshold

    def detect_all(
        self,
        text: str,
        title: str = "",
        confidence_score: float = 1.0,
        topics_count: int = 10,
        disciplines_count: int = 1,
    ) -> List[TriggerResult]:
        """
        Run all trigger detections on input text.

        Args:
            text: Combined title and abstract text.
            title: Paper title (for specific checks).
            confidence_score: Overall confidence from ConfidenceScorer.
            topics_count: Number of topics detected.
            disciplines_count: Number of disciplines detected.

        Returns:
            List of TriggerResult for each trigger type.
        """
        results: List[TriggerResult] = []

        # 1. Low confidence
        results.append(self.detect_low_confidence(confidence_score))

        # 2. Abbreviations
        results.append(self.detect_abbreviations(text))

        # 3. Cross-disciplinary
        results.append(self.detect_cross_disciplinary(disciplines_count))

        # 4. Non-English
        results.append(self.detect_non_english(text))

        # 5. Few topics
        results.append(self.detect_few_topics(topics_count))

        # 6. Ambiguous terms
        results.append(self.detect_ambiguous_terms(text))

        # 7. Short text
        results.append(self.detect_short_text(text))

        # Log activated triggers
        activated = [r for r in results if r.activated]
        if activated:
            trigger_names = [r.trigger_type.value for r in activated]
            logger.info(f"LLM triggers activated: {trigger_names}")

        return results

    def should_use_llm(
        self,
        text: str,
        confidence_score: float,
        topics_count: int = 10,
        disciplines_count: int = 1,
    ) -> tuple[bool, List[str]]:
        """
        Quick check if LLM enrichment should be used.

        Args:
            text: Combined title and abstract.
            confidence_score: Overall confidence score.
            topics_count: Number of topics found.
            disciplines_count: Number of disciplines.

        Returns:
            (should_use: bool, reasons: List[str])
        """
        results = self.detect_all(
            text=text,
            confidence_score=confidence_score,
            topics_count=topics_count,
            disciplines_count=disciplines_count,
        )

        activated = [r for r in results if r.activated]
        reasons = [r.details for r in activated]

        # Use LLM if 2+ triggers activated or any high-priority trigger
        high_priority = {TriggerType.LOW_CONFIDENCE, TriggerType.NON_ENGLISH}
        has_high_priority = any(r.trigger_type in high_priority for r in activated)

        should_use = len(activated) >= 2 or has_high_priority

        return should_use, reasons

    def detect_low_confidence(self, confidence_score: float) -> TriggerResult:
        """Detect if overall confidence is below threshold."""
        activated = confidence_score < self.confidence_threshold
        return TriggerResult(
            trigger_type=TriggerType.LOW_CONFIDENCE,
            activated=activated,
            confidence=1.0 - confidence_score,  # Higher when confidence is lower
            details=f"Overall confidence {confidence_score:.0%} < {self.confidence_threshold:.0%}",
        )

    def detect_abbreviations(self, text: str) -> TriggerResult:
        """Detect abbreviations that may need expansion."""
        matches = self.ABBREVIATION_PATTERN.findall(text)

        # Filter out known common abbreviations
        unknown = [m for m in matches if m not in self.KNOWN_ABBREVIATIONS]

        # Also check for abbreviations in parentheses like "(SERT)"
        parens_pattern = re.compile(r"\(([A-Z]{2,})\)")
        parens_matches = parens_pattern.findall(text)
        for m in parens_matches:
            if m not in unknown and m not in self.KNOWN_ABBREVIATIONS:
                unknown.append(m)

        activated = len(unknown) >= 2
        return TriggerResult(
            trigger_type=TriggerType.ABBREVIATIONS,
            activated=activated,
            confidence=min(len(unknown) / 5, 1.0),
            details=f"Found {len(unknown)} unknown abbreviations",
            extracted_items=unknown[:10],  # Limit to 10
        )

    def detect_cross_disciplinary(self, disciplines_count: int) -> TriggerResult:
        """Detect interdisciplinary papers."""
        activated = disciplines_count >= 2
        return TriggerResult(
            trigger_type=TriggerType.CROSS_DISCIPLINARY,
            activated=activated,
            confidence=min(disciplines_count / 3, 1.0),
            details=f"Paper spans {disciplines_count} disciplines",
        )

    def detect_non_english(self, text: str) -> TriggerResult:
        """Detect non-English text content."""
        non_english_chars = 0
        detected_scripts: List[str] = []

        for i, pattern in enumerate(self.NON_ENGLISH_PATTERNS):
            matches = pattern.findall(text)
            if matches:
                non_english_chars += len(matches)
                scripts = ["Hebrew", "Arabic", "Chinese", "Japanese", "Korean"]
                if i < len(scripts):
                    detected_scripts.append(scripts[i])

        # Activate if more than 10 non-English characters
        activated = non_english_chars > 10
        return TriggerResult(
            trigger_type=TriggerType.NON_ENGLISH,
            activated=activated,
            confidence=min(non_english_chars / 50, 1.0),
            details=f"Detected {non_english_chars} non-English characters ({', '.join(detected_scripts)})",
            extracted_items=detected_scripts,
        )

    def detect_few_topics(self, topics_count: int) -> TriggerResult:
        """Detect when too few topics are found."""
        activated = topics_count < 3
        return TriggerResult(
            trigger_type=TriggerType.FEW_TOPICS,
            activated=activated,
            confidence=1.0 if topics_count == 0 else (3 - topics_count) / 3,
            details=f"Only {topics_count} topics found",
        )

    def detect_ambiguous_terms(self, text: str) -> TriggerResult:
        """Detect ambiguous terms that may have multiple meanings."""
        text_lower = text.lower()
        found = [term for term in self.AMBIGUOUS_TERMS if term in text_lower]

        # Only activate if multiple ambiguous terms found
        activated = len(found) >= 3
        return TriggerResult(
            trigger_type=TriggerType.AMBIGUOUS_TERMS,
            activated=activated,
            confidence=min(len(found) / 5, 1.0),
            details=f"Found {len(found)} potentially ambiguous terms",
            extracted_items=found[:5],
        )

    def detect_short_text(self, text: str) -> TriggerResult:
        """Detect if input text is too short for reliable analysis."""
        word_count = len(text.split())
        activated = word_count < 50

        return TriggerResult(
            trigger_type=TriggerType.SHORT_TEXT,
            activated=activated,
            confidence=1.0 if word_count < 20 else (50 - word_count) / 30,
            details=f"Text has only {word_count} words",
        )


# Global instance
_trigger_detector: Optional[LLMTriggerDetector] = None


def get_trigger_detector() -> LLMTriggerDetector:
    """Get or create global trigger detector instance."""
    global _trigger_detector
    if _trigger_detector is None:
        _trigger_detector = LLMTriggerDetector()
    return _trigger_detector


def should_use_llm(
    text: str,
    confidence_score: float,
    topics_count: int = 10,
    disciplines_count: int = 1,
) -> tuple[bool, List[str]]:
    """
    Quick check if LLM enrichment should be used.

    Convenience function for LLMTriggerDetector.should_use_llm.
    """
    return get_trigger_detector().should_use_llm(
        text=text,
        confidence_score=confidence_score,
        topics_count=topics_count,
        disciplines_count=disciplines_count,
    )
