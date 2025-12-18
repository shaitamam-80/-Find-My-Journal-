"""
Behavioral Heuristics for Journal Risk Detection.

Analyzes journal metrics to detect suspicious patterns that may indicate
low-quality or predatory behavior.

Heuristics:
1. Volume Spike - Abnormal growth in publication count
2. Impact Ratio - Low citations relative to output
3. Self-Citation - Excessive self-citation rate (future)
4. Processing Time - Unrealistically fast publication (future)

IMPORTANT: These are indicators, not proof. Use with other signals.
"""

import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass

from app.models.journal import (
    JournalMetrics,
    BadgeColor,
    VerificationSource,
    VerificationFlag,
)

logger = logging.getLogger(__name__)


@dataclass
class HeuristicConfig:
    """Configuration thresholds for heuristic checks."""
    # Volume Spike thresholds
    volume_spike_warning: float = 2.0  # >200% growth = warning
    volume_spike_critical: float = 5.0  # >500% growth = critical
    volume_spike_min_papers: int = 50  # Minimum papers to trigger warning
    volume_spike_critical_min: int = 100  # Minimum papers for critical

    # Impact Ratio thresholds
    impact_ratio_warning: float = 0.5  # <0.5 citations/paper = warning
    impact_ratio_critical: float = 0.1  # <0.1 citations/paper = critical
    impact_ratio_min_works: int = 500  # Minimum works to evaluate

    # Self-Citation thresholds (future implementation)
    self_citation_warning: float = 0.30  # >30% self-citation = warning
    self_citation_critical: float = 0.50  # >50% = critical


# Global config
CONFIG = HeuristicConfig()


def check_volume_spike(
    counts_by_year: Optional[dict] = None,
    current_year_count: Optional[int] = None,
    works_count: Optional[int] = None,
) -> Optional[VerificationFlag]:
    """
    Check for abnormal publication volume growth.

    A sudden spike in publication volume can indicate:
    - Lowered quality standards
    - Pay-to-publish model without proper review
    - Journal mill behavior

    Args:
        counts_by_year: Dict of {year: count} publication counts
        current_year_count: Publications in the most recent year
        works_count: Total works count (fallback)

    Returns:
        VerificationFlag if suspicious, None otherwise
    """
    if not counts_by_year or len(counts_by_year) < 2:
        return None

    # Sort years and calculate year-over-year growth
    sorted_years = sorted(counts_by_year.keys())
    max_spike = 0.0
    spike_year = None

    for i in range(1, len(sorted_years)):
        prev_year = sorted_years[i - 1]
        curr_year = sorted_years[i]
        prev_count = counts_by_year.get(prev_year, 0)
        curr_count = counts_by_year.get(curr_year, 0)

        if prev_count > 0:
            spike = (curr_count - prev_count) / prev_count
            if spike > max_spike:
                max_spike = spike
                spike_year = curr_year

    # Get current year count for threshold check
    if current_year_count is None:
        latest_year = max(sorted_years)
        current_year_count = counts_by_year.get(latest_year, 0)

    # Check thresholds
    if max_spike >= CONFIG.volume_spike_critical and current_year_count >= CONFIG.volume_spike_critical_min:
        return VerificationFlag(
            source=VerificationSource.HEURISTIC,
            reason=f"Critical publication volume increase ({int(max_spike * 100)}% growth in {spike_year})",
            severity="critical",
        )
    elif max_spike >= CONFIG.volume_spike_warning and current_year_count >= CONFIG.volume_spike_min_papers:
        return VerificationFlag(
            source=VerificationSource.HEURISTIC,
            reason=f"Abnormal publication volume increase ({int(max_spike * 100)}% growth in {spike_year})",
            severity="medium",
        )

    return None


def check_impact_ratio(
    works_count: Optional[int],
    cited_by_count: Optional[int],
) -> Optional[VerificationFlag]:
    """
    Check citation impact relative to publication volume.

    Low impact ratio can indicate:
    - Papers not being read or cited
    - Low-quality content
    - Isolated from academic community

    Args:
        works_count: Total number of publications
        cited_by_count: Total citations received

    Returns:
        VerificationFlag if suspicious, None otherwise
    """
    if not works_count or works_count < CONFIG.impact_ratio_min_works:
        return None

    cited_by = cited_by_count or 0
    ratio = cited_by / works_count

    if ratio < CONFIG.impact_ratio_critical:
        return VerificationFlag(
            source=VerificationSource.HEURISTIC,
            reason=f"Very low citation impact ({ratio:.2f} citations per paper)",
            severity="high",
        )
    elif ratio < CONFIG.impact_ratio_warning:
        return VerificationFlag(
            source=VerificationSource.HEURISTIC,
            reason=f"Low citation impact ({ratio:.2f} citations per paper)",
            severity="medium",
        )

    return None


def check_metrics_consistency(
    metrics: JournalMetrics,
) -> Optional[VerificationFlag]:
    """
    Check for inconsistencies in reported metrics.

    Inconsistencies can indicate:
    - Data manipulation
    - Gaming of metrics
    - Technical errors

    Args:
        metrics: JournalMetrics object

    Returns:
        VerificationFlag if inconsistent, None otherwise
    """
    # H-index should be <= works_count
    if metrics.h_index and metrics.works_count:
        if metrics.h_index > metrics.works_count:
            return VerificationFlag(
                source=VerificationSource.HEURISTIC,
                reason="Inconsistent metrics: H-index exceeds publication count",
                severity="medium",
            )

    # i10-index should be <= works_count
    if metrics.i10_index and metrics.works_count:
        if metrics.i10_index > metrics.works_count:
            return VerificationFlag(
                source=VerificationSource.HEURISTIC,
                reason="Inconsistent metrics: i10-index exceeds publication count",
                severity="medium",
            )

    return None


def run_all_heuristics(
    metrics: JournalMetrics,
    counts_by_year: Optional[dict] = None,
) -> List[VerificationFlag]:
    """
    Run all heuristic checks on a journal.

    Args:
        metrics: JournalMetrics object
        counts_by_year: Optional publication counts by year

    Returns:
        List of triggered VerificationFlags
    """
    flags = []

    # Volume spike check
    volume_flag = check_volume_spike(
        counts_by_year=counts_by_year,
        works_count=metrics.works_count,
    )
    if volume_flag:
        flags.append(volume_flag)

    # Impact ratio check
    impact_flag = check_impact_ratio(
        works_count=metrics.works_count,
        cited_by_count=metrics.cited_by_count,
    )
    if impact_flag:
        flags.append(impact_flag)

    # Metrics consistency check
    consistency_flag = check_metrics_consistency(metrics)
    if consistency_flag:
        flags.append(consistency_flag)

    return flags


def aggregate_flags(
    flags: List[VerificationFlag],
) -> Tuple[BadgeColor, str]:
    """
    Aggregate multiple flags into a single badge status.

    Logic:
    - 0 flags: GRAY (unverified)
    - 1 flag (low/medium): YELLOW (caution)
    - 1 flag (high/critical): RED (high risk)
    - 2+ flags: RED (high risk)

    Args:
        flags: List of VerificationFlags

    Returns:
        Tuple of (BadgeColor, status_text)
    """
    if not flags:
        return BadgeColor.GRAY, "Unverified Source"

    # Count severity levels
    high_severity = sum(
        1 for f in flags if f.severity in ("high", "critical")
    )

    if len(flags) >= 2 or high_severity >= 1:
        return BadgeColor.RED, "Publication Risk Detected"
    else:
        return BadgeColor.YELLOW, "Exercise Caution"


def get_severity_score(flags: List[VerificationFlag]) -> int:
    """
    Calculate a numeric severity score from flags.

    Useful for sorting/ranking journals by risk level.

    Scoring:
    - low: 1 point
    - medium: 2 points
    - high: 4 points
    - critical: 8 points

    Args:
        flags: List of VerificationFlags

    Returns:
        Total severity score
    """
    severity_scores = {
        "low": 1,
        "medium": 2,
        "high": 4,
        "critical": 8,
    }

    return sum(severity_scores.get(f.severity, 0) for f in flags)
