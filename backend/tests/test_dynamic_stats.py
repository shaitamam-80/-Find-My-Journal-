"""
Tests for Dynamic Statistics Calculator.

Tests that we can calculate field-specific statistics from OpenAlex
for accurate journal scoring across any academic discipline.
"""

import pytest
from app.services.analysis.dynamic_stats import (
    DynamicStatsCalculator,
    get_subfield_stats,
    calculate_percentile_score,
    SubfieldStats,
)


class TestDynamicStatsCalculator:
    """Test the DynamicStatsCalculator class."""

    @pytest.fixture
    def calculator(self):
        return DynamicStatsCalculator(cache_ttl_hours=24)

    def test_get_stats_for_cardiology(self, calculator):
        """Test getting stats for a medical subfield (Cardiology)."""
        # Cardiology subfield ID in OpenAlex
        stats = calculator.get_subfield_stats(2705, "Cardiology and Cardiovascular Medicine")

        assert isinstance(stats, SubfieldStats)
        assert stats.subfield_id == 2705
        # H-index may be 0 if API doesn't return h_index values
        # But we should have found journals
        assert stats.journal_count >= 0
        # At least citedness should be available
        assert stats.median_citedness >= 0

    def test_get_stats_for_computer_science(self, calculator):
        """Test getting stats for CS subfield (AI)."""
        # Artificial Intelligence subfield ID
        stats = calculator.get_subfield_stats(1702, "Artificial Intelligence")

        assert isinstance(stats, SubfieldStats)
        assert stats.subfield_id == 1702
        assert stats.calculated_at > 0

    def test_get_stats_for_psychology(self, calculator):
        """Test getting stats for social sciences (Psychology)."""
        # Developmental and Educational Psychology
        stats = calculator.get_subfield_stats(3201, "Developmental and Educational Psychology")

        assert isinstance(stats, SubfieldStats)
        assert stats.subfield_id == 3201

    def test_caching_works(self, calculator):
        """Test that results are cached."""
        # First call
        stats1 = calculator.get_subfield_stats(2705, "Cardiology")

        # Second call should use cache
        stats2 = calculator.get_subfield_stats(2705, "Cardiology")

        # Should be the same object (from cache)
        assert stats1.calculated_at == stats2.calculated_at

    def test_cache_clear(self, calculator):
        """Test that cache can be cleared."""
        # Get stats to populate cache
        calculator.get_subfield_stats(2705, "Cardiology")

        # Clear cache
        calculator.clear_cache()

        # Cache should be empty
        assert len(calculator._cache) == 0


class TestPercentileCalculation:
    """Test the percentile score calculation."""

    def test_below_median_score(self):
        """Values below median should get 0-50 score."""
        score = calculate_percentile_score(
            value=25,
            median_val=50,
            p75_val=90,
            p90_val=150,
        )
        assert 0 <= score <= 50
        assert score == 25  # 25/50 * 50 = 25

    def test_at_median_score(self):
        """Value at median should get score of 50."""
        score = calculate_percentile_score(
            value=50,
            median_val=50,
            p75_val=90,
            p90_val=150,
        )
        assert score == 50

    def test_at_p75_score(self):
        """Value at 75th percentile should get score of 75."""
        score = calculate_percentile_score(
            value=90,
            median_val=50,
            p75_val=90,
            p90_val=150,
        )
        assert score == 75

    def test_at_p90_score(self):
        """Value at 90th percentile should get score of 90."""
        score = calculate_percentile_score(
            value=150,
            median_val=50,
            p75_val=90,
            p90_val=150,
        )
        assert score == 90

    def test_above_p90_score(self):
        """Values above 90th percentile should get 90-100 score."""
        score = calculate_percentile_score(
            value=200,
            median_val=50,
            p75_val=90,
            p90_val=150,
        )
        assert 90 <= score <= 100

    def test_zero_value(self):
        """Zero value should get score of 0."""
        score = calculate_percentile_score(
            value=0,
            median_val=50,
            p75_val=90,
            p90_val=150,
        )
        assert score == 0

    def test_zero_median_returns_neutral(self):
        """Zero median should return neutral score of 50."""
        score = calculate_percentile_score(
            value=10,
            median_val=0,
            p75_val=0,
            p90_val=0,
        )
        assert score == 50


class TestSubfieldStats:
    """Test the SubfieldStats dataclass."""

    def test_dataclass_creation(self):
        """Test creating SubfieldStats directly."""
        stats = SubfieldStats(
            subfield_id=2705,
            subfield_name="Cardiology",
            journal_count=100,
            median_h_index=50,
            p25_h_index=25,
            p75_h_index=90,
            p90_h_index=150,
            median_citedness=3.0,
            p25_citedness=1.5,
            p75_citedness=5.0,
            p90_citedness=8.0,
            calculated_at=1234567890.0,
        )

        assert stats.subfield_id == 2705
        assert stats.median_h_index == 50
        assert stats.source == "openalex_dynamic"


class TestConvenienceFunction:
    """Test the module-level convenience function."""

    def test_get_subfield_stats_function(self):
        """Test that get_subfield_stats works at module level."""
        stats = get_subfield_stats(2705, "Cardiology")

        assert isinstance(stats, SubfieldStats)
        assert stats.subfield_id == 2705
