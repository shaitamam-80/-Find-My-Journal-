"""
Article Type Detector

Detects the type of academic article from abstract text.
Supports: systematic review, meta-analysis, RCT, cohort study, case-control,
cross-sectional, case report, narrative review, original research.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class DetectedArticleType:
    """A detected article type with confidence score."""
    type_id: str
    display_name: str
    confidence: float  # 0.0 to 1.0
    evidence: List[str]  # Patterns that matched
    preferred_journal_types: List[str]  # Types of journals that typically publish this


# Article type patterns with regex matching
ARTICLE_TYPE_PATTERNS: Dict[str, Dict] = {
    "systematic_review": {
        "display_name": "Systematic Review",
        "patterns": [
            r"systematic review",
            r"systematic search",
            r"systematic literature",
            r"prisma",
            r"prisma guidelines",
            r"searched.{1,30}databases?",
            r"electronic databases?",
            r"inclusion criteria",
            r"exclusion criteria",
            r"quality assessment",
            r"risk of bias",
            r"eligib\w+\s+criteria",
            r"screened\s+(?:for\s+)?eligibility",
            r"data\s+extraction",
        ],
        "required_count": 2,  # Need at least 2 matches
        "preferred_journals": ["review_journals", "methodology_journals"],
    },
    "meta_analysis": {
        "display_name": "Meta-Analysis",
        "patterns": [
            r"meta-analysis",
            r"meta analysis",
            r"pooled analysis",
            r"effect size",
            r"heterogeneity",
            r"i-squared|i²|i2\s*=",
            r"forest plot",
            r"random.?effects?\s+model",
            r"fixed.?effects?\s+model",
            r"publication bias",
            r"funnel plot",
            r"pooled.{1,20}(?:or|rr|hr|smd|md)",
            r"dersimonian",
            r"mantel.?haenszel",
        ],
        "required_count": 1,
        "preferred_journals": ["review_journals", "high_impact"],
    },
    "randomized_controlled_trial": {
        "display_name": "Randomized Controlled Trial",
        "patterns": [
            r"randomized controlled",
            r"randomised controlled",
            r"rct\b",
            r"double.?blind",
            r"single.?blind",
            r"triple.?blind",
            r"placebo.?controlled",
            r"randomly\s+(?:assigned|allocated)",
            r"randomization",
            r"randomisation",
            r"intention.?to.?treat",
            r"per.?protocol",
            r"block\s+randomization",
            r"stratified\s+randomization",
            r"clinical\s+trial\s+registration",
        ],
        "required_count": 2,
        "preferred_journals": ["clinical_journals", "high_impact"],
    },
    "cohort_study": {
        "display_name": "Cohort Study",
        "patterns": [
            r"cohort study",
            r"cohort\s+of",
            r"prospective study",
            r"retrospective study",
            r"retrospective cohort",
            r"prospective cohort",
            r"follow.?up",
            r"followed\s+(?:up\s+)?for",
            r"longitudinal",
            r"hazard ratio",
            r"cox\s+(?:proportional\s+)?(?:hazard|regression)",
            r"kaplan.?meier",
            r"survival analysis",
            r"time.?to.?event",
        ],
        "required_count": 2,
        "preferred_journals": ["epidemiology_journals", "clinical_journals"],
    },
    "case_control": {
        "display_name": "Case-Control Study",
        "patterns": [
            r"case.?control\s+study",
            r"case.?control\s+design",
            r"cases?\s+and\s+controls?",
            r"matched\s+controls?",
            r"odds\s+ratio",
            r"nested\s+case.?control",
        ],
        "required_count": 1,
        "preferred_journals": ["epidemiology_journals"],
    },
    "cross_sectional": {
        "display_name": "Cross-Sectional Study",
        "patterns": [
            r"cross.?sectional",
            r"prevalence\s+study",
            r"survey\s+study",
            r"point\s+prevalence",
            r"questionnaire.?based",
            r"national\s+survey",
        ],
        "required_count": 1,
        "preferred_journals": ["clinical_journals", "epidemiology_journals"],
    },
    "case_report": {
        "display_name": "Case Report",
        "patterns": [
            r"case\s+report",
            r"case\s+presentation",
            r"we\s+present\s+a\s+case",
            r"we\s+report\s+a\s+case",
            r"rare\s+case",
            r"unusual\s+case",
            r"case\s+of\s+a\s+\d+.?year.?old",
            r"presented\s+with",
        ],
        "required_count": 1,
        "preferred_journals": ["case_report_journals"],
    },
    "case_series": {
        "display_name": "Case Series",
        "patterns": [
            r"case\s+series",
            r"series\s+of\s+\d+\s+(?:patients?|cases?)",
            r"consecutive\s+(?:patients?|cases?)",
            r"retrospective\s+review\s+of",
        ],
        "required_count": 1,
        "preferred_journals": ["clinical_journals", "case_report_journals"],
    },
    "narrative_review": {
        "display_name": "Narrative Review",
        "patterns": [
            r"narrative\s+review",
            r"literature\s+review",
            r"review\s+article",
            r"overview\s+of",
            r"current\s+state\s+of",
            r"state\s+of\s+the\s+art",
            r"comprehensive\s+review",
            r"critical\s+review",
        ],
        "required_count": 1,
        "preferred_journals": ["review_journals"],
    },
    "scoping_review": {
        "display_name": "Scoping Review",
        "patterns": [
            r"scoping\s+review",
            r"scoping\s+study",
            r"mapping\s+review",
        ],
        "required_count": 1,
        "preferred_journals": ["review_journals", "methodology_journals"],
    },
    "diagnostic_accuracy": {
        "display_name": "Diagnostic Accuracy Study",
        "patterns": [
            r"diagnostic\s+accuracy",
            r"sensitivity\s+and\s+specificity",
            r"roc\s+(?:curve|analysis)",
            r"area\s+under\s+(?:the\s+)?curve|auc",
            r"gold\s+standard",
            r"reference\s+standard",
            r"positive\s+predictive\s+value",
            r"negative\s+predictive\s+value",
        ],
        "required_count": 2,
        "preferred_journals": ["clinical_journals", "methodology_journals"],
    },
    "qualitative_study": {
        "display_name": "Qualitative Study",
        "patterns": [
            r"qualitative\s+study",
            r"qualitative\s+research",
            r"thematic\s+analysis",
            r"grounded\s+theory",
            r"phenomenolog",
            r"focus\s+group",
            r"in.?depth\s+interview",
            r"semi.?structured\s+interview",
        ],
        "required_count": 2,
        "preferred_journals": ["qualitative_journals", "social_science_journals"],
    },
    "original_research": {
        "display_name": "Original Research",
        "patterns": [
            r"we\s+conducted",
            r"we\s+performed",
            r"we\s+analyzed",
            r"we\s+analysed",
            r"our\s+study",
            r"this\s+study\s+aims",
            r"patients?\s+were\s+enrolled",
            r"subjects?\s+were\s+recruited",
            r"participants?\s+were\s+(?:recruited|enrolled)",
            r"we\s+investigated",
            r"we\s+examined",
            r"we\s+evaluated",
        ],
        "required_count": 1,
        "preferred_journals": ["all"],
    },
}


# Journal type definitions for reference
JOURNAL_TYPE_EXAMPLES: Dict[str, List[str]] = {
    "review_journals": [
        "Cochrane Database of Systematic Reviews",
        "Systematic Reviews",
        "JBI Evidence Synthesis",
        "Research Synthesis Methods",
    ],
    "methodology_journals": [
        "BMC Medical Research Methodology",
        "Journal of Clinical Epidemiology",
        "Statistics in Medicine",
    ],
    "case_report_journals": [
        "BMJ Case Reports",
        "Journal of Medical Case Reports",
        "Case Reports in Medicine",
    ],
    "epidemiology_journals": [
        "American Journal of Epidemiology",
        "International Journal of Epidemiology",
        "Epidemiology",
    ],
    "high_impact": [
        "The Lancet",
        "NEJM",
        "JAMA",
        "BMJ",
    ],
    "clinical_journals": [
        "Clinical trials",
        "Specialty-specific clinical journals",
    ],
    "qualitative_journals": [
        "Qualitative Health Research",
        "Social Science & Medicine",
    ],
}


class ArticleTypeDetector:
    """Detects academic article type from text."""

    def detect(self, abstract: str, title: str = "") -> DetectedArticleType:
        """
        Detect the article type from abstract and title.

        Args:
            abstract: Article abstract text.
            title: Optional article title.

        Returns:
            The most likely article type with confidence score.
        """
        text = f"{title} {abstract}".lower()

        matches: List[DetectedArticleType] = []

        for type_id, config in ARTICLE_TYPE_PATTERNS.items():
            evidence: List[str] = []

            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    evidence.append(pattern)

            if len(evidence) >= config["required_count"]:
                # Calculate confidence based on pattern matches
                confidence = min(len(evidence) / len(config["patterns"]) * 2, 1.0)
                matches.append(DetectedArticleType(
                    type_id=type_id,
                    display_name=config["display_name"],
                    confidence=confidence,
                    evidence=evidence,
                    preferred_journal_types=config["preferred_journals"],
                ))

        # Sort by confidence descending
        matches.sort(key=lambda x: x.confidence, reverse=True)

        # Handle combined types (e.g., Systematic Review AND Meta-Analysis)
        if matches:
            best = matches[0]

            # Check for systematic review + meta-analysis combo
            # Lower threshold (0.1) since meta-analysis often has few patterns matched
            type_ids = {m.type_id for m in matches if m.confidence > 0.1}

            if "systematic_review" in type_ids and "meta_analysis" in type_ids:
                # Find both types to combine evidence
                sr_match = next((m for m in matches if m.type_id == "systematic_review"), None)
                ma_match = next((m for m in matches if m.type_id == "meta_analysis"), None)

                combined_evidence = list(set(
                    (sr_match.evidence if sr_match else []) +
                    (ma_match.evidence if ma_match else [])
                ))

                return DetectedArticleType(
                    type_id="systematic_review_meta_analysis",
                    display_name="Systematic Review & Meta-Analysis",
                    confidence=max(m.confidence for m in matches if m.type_id in type_ids),
                    evidence=combined_evidence,
                    preferred_journal_types=["review_journals", "high_impact", "methodology_journals"],
                )

            return best

        # Default to original research if nothing specific found
        return DetectedArticleType(
            type_id="original_research",
            display_name="Original Research",
            confidence=0.5,
            evidence=[],
            preferred_journal_types=["all"],
        )

    def detect_all(self, abstract: str, title: str = "") -> List[DetectedArticleType]:
        """
        Detect all matching article types (not just the best one).

        Useful for debugging or showing secondary classifications.

        Args:
            abstract: Article abstract text.
            title: Optional article title.

        Returns:
            List of all matching article types, sorted by confidence.
        """
        text = f"{title} {abstract}".lower()

        matches: List[DetectedArticleType] = []

        for type_id, config in ARTICLE_TYPE_PATTERNS.items():
            evidence: List[str] = []

            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    evidence.append(pattern)

            if len(evidence) >= config["required_count"]:
                confidence = min(len(evidence) / len(config["patterns"]) * 2, 1.0)
                matches.append(DetectedArticleType(
                    type_id=type_id,
                    display_name=config["display_name"],
                    confidence=confidence,
                    evidence=evidence,
                    preferred_journal_types=config["preferred_journals"],
                ))

        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches

    def to_dict(self, article_type: DetectedArticleType) -> Dict:
        """
        Convert detected article type to dictionary format for API response.

        Args:
            article_type: Detected article type.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        return {
            "type": article_type.type_id,
            "display_name": article_type.display_name,
            "confidence": round(article_type.confidence, 2),
            "evidence": article_type.evidence[:5],  # Limit for cleaner response
            "preferred_journal_types": article_type.preferred_journal_types,
        }


# Convenience function for quick detection
def detect_article_type(abstract: str, title: str = "") -> DetectedArticleType:
    """
    Quick function to detect article type from text.

    Args:
        abstract: Article abstract.
        title: Optional article title.

    Returns:
        The detected article type.
    """
    detector = ArticleTypeDetector()
    return detector.detect(abstract, title)
