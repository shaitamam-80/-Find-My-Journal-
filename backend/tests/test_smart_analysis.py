"""
Tests for Smart Analysis Engine (Phase 4).

Tests the SmartAnalyzer integration with the search pipeline.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.services.analysis import (
    SmartAnalyzer,
    AnalysisResult,
    get_smart_analyzer,
    ConfidenceScore,
    ConfidenceFactor,
)
from app.services.openalex.keywords import RankedKeyword
from app.services.openalex.topics import DetectedSubfield


class TestSmartAnalyzer:
    """Tests for SmartAnalyzer class."""

    def setup_method(self):
        """Reset global instance before each test."""
        import app.services.analysis.smart_analyzer as sa_module
        sa_module._smart_analyzer = None

    @patch("app.services.analysis.smart_analyzer.get_topics_service")
    @patch("app.services.analysis.smart_analyzer.get_keywords_extractor")
    @patch("app.services.analysis.smart_analyzer.get_concepts_analyzer")
    def test_analyze_returns_result(
        self, mock_concepts, mock_keywords, mock_topics
    ):
        """Test that analyze returns an AnalysisResult."""
        # Setup mocks
        mock_topics_service = MagicMock()
        mock_topics_result = MagicMock()
        mock_topics_result.all_subfields = []
        mock_topics_result.topic_ids = []
        mock_topics_result.works_analyzed = 10
        mock_topics_result.total_topics_found = 3
        mock_topics_result.primary_subfield = None
        mock_topics_service.analyze_topics_from_query.return_value = mock_topics_result
        mock_topics.return_value = mock_topics_service

        mock_kw_extractor = MagicMock()
        mock_kw_extractor.extract_from_works.return_value = []
        mock_kw_extractor.merge_with_user_keywords.return_value = []
        mock_kw_extractor.rank_keywords.return_value = []
        mock_keywords.return_value = mock_kw_extractor

        mock_concepts_analyzer = MagicMock()
        mock_concepts_analyzer.get_discipline_hints.return_value = []
        mock_concepts_analyzer.get_methodology_hints.return_value = []
        mock_concepts.return_value = mock_concepts_analyzer

        # Create analyzer and run
        analyzer = SmartAnalyzer(enable_llm=False)
        result = analyzer.analyze(
            title="Test Title",
            abstract="Test abstract about machine learning.",
        )

        assert isinstance(result, AnalysisResult)
        assert result.search_terms is not None
        assert result.confidence is not None

    @patch("app.services.analysis.smart_analyzer.get_topics_service")
    @patch("app.services.analysis.smart_analyzer.get_keywords_extractor")
    @patch("app.services.analysis.smart_analyzer.get_concepts_analyzer")
    def test_analyze_with_keywords(
        self, mock_concepts, mock_keywords, mock_topics
    ):
        """Test analyze with user-provided keywords."""
        # Setup mocks
        mock_topics_service = MagicMock()
        mock_topics_result = MagicMock()
        mock_topics_result.all_subfields = []
        mock_topics_result.topic_ids = []
        mock_topics_result.works_analyzed = 10
        mock_topics_result.total_topics_found = 3
        mock_topics_result.primary_subfield = None
        mock_topics_service.analyze_topics_from_query.return_value = mock_topics_result
        mock_topics.return_value = mock_topics_service

        mock_kw_extractor = MagicMock()
        mock_kw_extractor.extract_from_works.return_value = []
        mock_kw_extractor.merge_with_user_keywords.return_value = [
            RankedKeyword(keyword="test", score=1.0, frequency=1, source="user")
        ]
        mock_kw_extractor.rank_keywords.return_value = [
            RankedKeyword(keyword="test", score=1.0, frequency=1, source="user")
        ]
        mock_keywords.return_value = mock_kw_extractor

        mock_concepts_analyzer = MagicMock()
        mock_concepts_analyzer.get_discipline_hints.return_value = []
        mock_concepts_analyzer.get_methodology_hints.return_value = []
        mock_concepts.return_value = mock_concepts_analyzer

        # Create analyzer and run
        analyzer = SmartAnalyzer(enable_llm=False)
        result = analyzer.analyze(
            title="Test Title",
            abstract="Test abstract.",
            user_keywords=["machine learning", "AI"],
        )

        assert isinstance(result, AnalysisResult)
        # Verify merge was called with user keywords
        mock_kw_extractor.merge_with_user_keywords.assert_called_once()


class TestConfidenceScore:
    """Tests for ConfidenceScore dataclass."""

    def test_confidence_score_high(self):
        """Test high confidence detection."""
        score = ConfidenceScore(overall=0.8, factors=[])
        assert score.is_high
        assert not score.is_medium
        assert not score.is_low

    def test_confidence_score_medium(self):
        """Test medium confidence detection."""
        score = ConfidenceScore(overall=0.5, factors=[])
        assert not score.is_high
        assert score.is_medium
        assert not score.is_low

    def test_confidence_score_low(self):
        """Test low confidence detection."""
        score = ConfidenceScore(overall=0.3, factors=[])
        assert not score.is_high
        assert not score.is_medium
        assert score.is_low


class TestAnalysisResultToDict:
    """Tests for AnalysisResult.to_dict() method."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        result = AnalysisResult(
            keywords=[
                RankedKeyword(keyword="test", score=1.0, frequency=1, source="api")
            ],
            search_terms=["test", "search"],
            disciplines=[],
            primary_discipline="Psychology",
            primary_field="Social Sciences",
            discipline_confidence=0.7,
            confidence=ConfidenceScore(overall=0.7, factors=[]),
        )

        d = result.to_dict()

        assert d["keywords"] == ["test"]
        assert d["search_terms"] == ["test", "search"]
        assert d["primary_discipline"] == "Psychology"
        assert d["primary_field"] == "Social Sciences"
        assert d["discipline_confidence"] == 0.7
        assert d["confidence_score"] == 0.7


class TestSearchIntegration:
    """Tests for search.py integration with SmartAnalyzer."""

    def test_search_returns_seven_values(self):
        """Test that search_journals_by_text returns 7 values including metadata."""
        from unittest.mock import patch, MagicMock

        # We need to patch inside the function scope since it uses lazy import
        with patch("app.services.openalex.search.find_journals_by_topics") as mock_topics, \
             patch("app.services.openalex.search.find_journals_by_subfield_id") as mock_subfield, \
             patch("app.services.openalex.search.find_journals_by_subfield") as mock_subfield2, \
             patch("app.services.openalex.search.search_journals_by_keywords") as mock_kw:

            mock_topics.return_value = {}
            mock_subfield.return_value = {}
            mock_subfield2.return_value = {}
            mock_kw.return_value = []

            from app.services.openalex.search import search_journals_by_text

            result = search_journals_by_text(
                title="Test Title About Psychology",
                abstract="A comprehensive study examining the psychological effects of various treatments on patient outcomes using randomized controlled trials.",
            )

            # Verify 7 values returned
            assert len(result) == 7
            journals, discipline, field, confidence, disciplines, article_type, metadata = result

            # Verify metadata structure
            assert metadata is not None
            assert "confidence_score" in metadata
            assert "confidence_factors" in metadata
            assert "works_analyzed" in metadata
            assert "topics_found" in metadata


class TestLLMTriggerDetection:
    """Tests for LLM trigger detection logic."""

    def test_low_confidence_triggers_llm(self):
        """Test that low confidence triggers LLM enrichment."""
        from app.services.analysis.triggers import should_use_llm

        result, reasons = should_use_llm(
            text="Short text",
            confidence_score=0.3,  # Low confidence
            topics_count=2,
            disciplines_count=1,
        )

        assert result is True
        assert len(reasons) > 0

    def test_high_confidence_no_llm(self):
        """Test that high confidence doesn't trigger LLM."""
        from app.services.analysis.triggers import should_use_llm

        result, reasons = should_use_llm(
            text="A comprehensive abstract about machine learning techniques for medical imaging analysis.",
            confidence_score=0.9,  # High confidence
            topics_count=10,
            disciplines_count=1,
        )

        assert result is False

    def test_cross_disciplinary_triggers_llm(self):
        """Test that cross-disciplinary papers may trigger LLM."""
        from app.services.analysis.triggers import get_trigger_detector

        detector = get_trigger_detector()
        results = detector.detect_all(
            text="Combining neuroscience and economics.",
            title="Neuroeconomics Study",
            confidence_score=0.6,
            topics_count=5,
            disciplines_count=3,  # Multiple disciplines
        )

        # Find cross_disciplinary trigger
        cross_trigger = next(
            (r for r in results if r.trigger_type.name == "CROSS_DISCIPLINARY"),
            None,
        )

        assert cross_trigger is not None
        assert cross_trigger.activated is True
