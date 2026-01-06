"""
Dynamic Subfield Statistics Calculator.

Instead of hardcoded statistics for each discipline, this module
queries OpenAlex to calculate real-time statistics for ANY subfield.

Results are cached in-memory to minimize API calls.

Benefits:
- Works for ALL 252 subfields automatically
- Always up-to-date (no manual maintenance)
- Enables accurate field normalization for any discipline
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from statistics import median, quantiles
import time
import logging

from app.services.openalex.client import get_client

logger = logging.getLogger(__name__)


@dataclass
class SubfieldStats:
    """Statistics for a subfield, calculated from OpenAlex data."""
    subfield_id: int
    subfield_name: str
    journal_count: int

    # H-index statistics
    median_h_index: float
    p25_h_index: float
    p75_h_index: float
    p90_h_index: float

    # Citation statistics (2-year mean citedness)
    median_citedness: float
    p25_citedness: float
    p75_citedness: float
    p90_citedness: float

    # Metadata
    calculated_at: float  # Unix timestamp
    source: str = "openalex_dynamic"


class DynamicStatsCalculator:
    """
    Calculates field-specific statistics dynamically from OpenAlex.

    Benefits:
    - Works for ALL 252 subfields automatically
    - Always up-to-date (no manual maintenance)
    - Enables accurate field normalization for any discipline
    """

    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialize the calculator.

        Args:
            cache_ttl_hours: How long to cache statistics (in hours)
        """
        self.cache_ttl_hours = cache_ttl_hours
        self._cache: Dict[int, SubfieldStats] = {}

    def get_subfield_stats(
        self,
        subfield_id: int,
        subfield_name: str = "",
    ) -> SubfieldStats:
        """
        Get statistics for a subfield.

        Checks cache first, calculates if needed.

        Args:
            subfield_id: OpenAlex numeric subfield ID
            subfield_name: Display name of the subfield

        Returns:
            SubfieldStats with calculated statistics
        """
        # Check cache
        if subfield_id in self._cache:
            cached = self._cache[subfield_id]
            cache_age = time.time() - cached.calculated_at
            if cache_age < self.cache_ttl_hours * 3600:
                logger.debug(f"Using cached stats for subfield {subfield_id}")
                return cached

        # Calculate fresh stats
        logger.info(f"Calculating stats for subfield {subfield_id}")
        stats = self._calculate_stats(subfield_id, subfield_name)

        # Cache result
        self._cache[subfield_id] = stats

        return stats

    def _calculate_stats(
        self,
        subfield_id: int,
        subfield_name: str,
    ) -> SubfieldStats:
        """Calculate statistics by querying OpenAlex."""
        # Query journals in this subfield
        journals = self._get_journals_in_subfield(subfield_id)

        if not journals:
            logger.warning(f"No journals found for subfield {subfield_id}")
            return self._default_stats(subfield_id, subfield_name)

        # Extract metrics
        h_indices = []
        citedness_values = []

        for journal in journals:
            h_index = journal.get("h_index")
            if h_index and h_index > 0:
                h_indices.append(h_index)

            summary_stats = journal.get("summary_stats") or {}
            citedness = summary_stats.get("2yr_mean_citedness")
            if citedness and citedness > 0:
                citedness_values.append(citedness)

        # Ensure we have enough data
        if len(h_indices) < 3:
            h_indices = [0]
        if len(citedness_values) < 3:
            citedness_values = [0]

        # Calculate percentiles
        h_quantiles = self._safe_quantiles(h_indices)
        c_quantiles = self._safe_quantiles(citedness_values)

        return SubfieldStats(
            subfield_id=subfield_id,
            subfield_name=subfield_name,
            journal_count=len(journals),
            median_h_index=h_quantiles[1],
            p25_h_index=h_quantiles[0],
            p75_h_index=h_quantiles[2],
            p90_h_index=h_quantiles[3],
            median_citedness=c_quantiles[1],
            p25_citedness=c_quantiles[0],
            p75_citedness=c_quantiles[2],
            p90_citedness=c_quantiles[3],
            calculated_at=time.time(),
        )

    def _get_journals_in_subfield(
        self,
        subfield_id: int,
        max_journals: int = 100,
    ) -> List[Dict]:
        """
        Query OpenAlex for journals in a subfield.

        Uses the existing synchronous client.
        """
        client = get_client()

        try:
            # Use the existing method that groups works by source
            results = client.find_sources_by_subfield_id(
                subfield_id=subfield_id,
                per_page=max_journals,
            )

            # Get full journal details for each source
            journals = []
            for entry in results[:max_journals]:
                source_id = entry.get("key")
                if source_id:
                    source = client.get_source_by_id(source_id)
                    if source:
                        journals.append(source)

                # Limit API calls
                if len(journals) >= 50:
                    break

            return journals
        except Exception as e:
            logger.error(f"Failed to get journals for subfield {subfield_id}: {e}")
            return []

    def _safe_quantiles(self, values: List[float]) -> tuple:
        """Calculate quantiles safely."""
        if len(values) < 4:
            # Not enough data for quantiles
            m = median(values) if values else 0
            return (m * 0.5, m, m * 1.5, m * 2)

        try:
            qs = quantiles(values, n=4)  # Quartiles
            # Calculate 90th percentile
            sorted_values = sorted(values)
            p90_index = int(len(sorted_values) * 0.9)
            p90 = sorted_values[min(p90_index, len(sorted_values) - 1)]
            return (qs[0], qs[1], qs[2], p90)
        except Exception:
            m = median(values)
            return (m * 0.5, m, m * 1.5, m * 2)

    def _default_stats(self, subfield_id: int, name: str) -> SubfieldStats:
        """Return default stats when calculation fails."""
        return SubfieldStats(
            subfield_id=subfield_id,
            subfield_name=name,
            journal_count=0,
            median_h_index=50,
            p25_h_index=25,
            p75_h_index=90,
            p90_h_index=150,
            median_citedness=3.0,
            p25_citedness=1.5,
            p75_citedness=5.0,
            p90_citedness=8.0,
            calculated_at=time.time(),
            source="default_fallback",
        )

    def clear_cache(self) -> None:
        """Clear the statistics cache."""
        self._cache.clear()
        logger.info("Dynamic stats cache cleared")


# Global instance with caching
_stats_calculator: Optional[DynamicStatsCalculator] = None


def get_stats_calculator() -> DynamicStatsCalculator:
    """Get or create global stats calculator."""
    global _stats_calculator
    if _stats_calculator is None:
        _stats_calculator = DynamicStatsCalculator()
    return _stats_calculator


def get_subfield_stats(subfield_id: int, name: str = "") -> SubfieldStats:
    """Convenience function to get subfield stats."""
    calculator = get_stats_calculator()
    return calculator.get_subfield_stats(subfield_id, name)


def calculate_percentile_score(
    value: float,
    median_val: float,
    p75_val: float,
    p90_val: float,
) -> float:
    """
    Calculate a percentile-based score for a value.

    Maps the value to a 0-100 scale based on the field's distribution.

    Args:
        value: The value to score (e.g., h-index)
        median_val: The median for this field
        p75_val: The 75th percentile
        p90_val: The 90th percentile

    Returns:
        Score from 0-100
    """
    if value <= 0:
        return 0

    if median_val <= 0:
        return 50  # No data, return neutral

    if value <= median_val:
        # Below median: 0-50
        return (value / median_val) * 50
    elif value <= p75_val:
        # Median to 75th: 50-75
        range_size = p75_val - median_val
        if range_size > 0:
            return 50 + ((value - median_val) / range_size) * 25
        return 62.5
    elif value <= p90_val:
        # 75th to 90th: 75-90
        range_size = p90_val - p75_val
        if range_size > 0:
            return 75 + ((value - p75_val) / range_size) * 15
        return 82.5
    else:
        # Above 90th: 90-100
        overshoot = value / p90_val
        return min(90 + (overshoot - 1) * 10, 100)
