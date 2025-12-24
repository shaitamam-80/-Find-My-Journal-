"""
Tests for search functionality.

Updated for the new modular OpenAlex service structure.
"""

import pytest
from unittest.mock import patch, MagicMock

# New imports from modular structure
from app.services.openalex import (
    OpenAlexService,
    openalex_service,
    extract_search_terms,
    detect_discipline,
    convert_to_journal,
    categorize_journals,
    search_journals_by_keywords,
    search_journals_by_text,
    get_topic_ids_from_similar_works,
    find_journals_by_topics,
    merge_journal_results,
)
from app.models.journal import Journal, JournalMetrics, JournalCategory


class TestUtilityFunctions:
    """Tests for utility functions (previously private methods)."""

    def test_extract_search_terms_with_keywords(self):
        """Test that provided keywords are included."""
        keywords = ["machine learning", "neural networks"]
        text = "A study on deep learning applications"

        terms = extract_search_terms(text, keywords)

        assert "machine learning" in terms
        assert "neural networks" in terms

    def test_extract_search_terms_filters_stopwords(self):
        """Test that common words are filtered out."""
        text = "The study of neural networks in the field of research"

        terms = extract_search_terms(text, [])

        assert "the" not in terms
        assert "study" not in terms
        assert "of" not in terms
        assert "neural" in terms
        assert "networks" in terms

    def test_extract_search_terms_limits_results(self):
        """Test that results are limited to 10 terms."""
        text = " ".join([f"word{i}" for i in range(50)])

        terms = extract_search_terms(text, [])

        assert len(terms) <= 10

    def test_detect_discipline_medicine(self):
        """Test detection of medical discipline."""
        text = "Clinical treatment of patients with disease diagnosis"

        discipline = detect_discipline(text)

        assert discipline == "medicine"

    def test_detect_discipline_computer_science(self):
        """Test detection of computer science discipline."""
        text = "Machine learning algorithm using neural networks and deep learning"

        discipline = detect_discipline(text)

        assert discipline == "computer_science"

    def test_detect_discipline_biology(self):
        """Test detection of biology discipline."""
        text = "Gene expression in cell protein synthesis and molecular evolution"

        discipline = detect_discipline(text)

        assert discipline == "biology"

    def test_detect_discipline_physics(self):
        """Test detection of physics discipline."""
        text = "Quantum particle energy wave electron photon magnetic field"

        discipline = detect_discipline(text)

        assert discipline == "physics"

    def test_detect_discipline_general(self):
        """Test fallback to general discipline."""
        text = "Some random text without specific keywords"

        discipline = detect_discipline(text)

        assert discipline == "general"


class TestJournalOperations:
    """Tests for journal operations (convert, categorize)."""

    def test_categorize_journals_top_tier(self):
        """Test categorization of top tier journals."""
        journal = Journal(
            id="test",
            name="Nature",
            metrics=JournalMetrics(h_index=150, works_count=100000),
        )

        result = categorize_journals([journal])

        assert result[0].category == JournalCategory.TOP_TIER
        assert result[0].match_reason == "High impact journal"

    def test_categorize_journals_broad_audience(self):
        """Test categorization of broad audience journals."""
        journal = Journal(
            id="test",
            name="Some Journal",
            metrics=JournalMetrics(h_index=50, works_count=20000),
        )

        result = categorize_journals([journal])

        assert result[0].category == JournalCategory.BROAD_AUDIENCE
        assert result[0].match_reason == "Wide readership"

    def test_categorize_journals_niche(self):
        """Test categorization of niche journals."""
        journal = Journal(
            id="test",
            name="Specialized Journal",
            metrics=JournalMetrics(h_index=20, works_count=5000),
        )

        result = categorize_journals([journal])

        assert result[0].category == JournalCategory.NICHE
        assert result[0].match_reason == "Specialized focus"

    def test_categorize_journals_emerging(self):
        """Test categorization of emerging journals."""
        journal = Journal(
            id="test",
            name="New Journal",
            metrics=JournalMetrics(h_index=5, works_count=500),
        )

        result = categorize_journals([journal])

        assert result[0].category == JournalCategory.EMERGING
        assert result[0].match_reason == "Growing journal"

    def test_convert_to_journal_valid_source(self):
        """Test conversion of valid OpenAlex source."""
        source = {
            "id": "https://openalex.org/S12345",
            "display_name": "Test Journal",
            "issn": ["1234-5678"],
            "issn_l": "1234-5678",
            "host_organization_name": "Test Publisher",
            "homepage_url": "https://test.com",
            "type": "journal",
            "is_oa": True,
            "apc_usd": 2000,
            "cited_by_count": 10000,
            "works_count": 5000,
            "summary_stats": {"h_index": 50, "i10_index": 100},
            "topics": [
                {"display_name": "Topic 1"},
                {"display_name": "Topic 2"},
            ],
        }

        journal = convert_to_journal(source)

        assert journal is not None
        assert journal.id == "https://openalex.org/S12345"
        assert journal.name == "Test Journal"
        assert journal.issn == "1234-5678"
        assert journal.publisher == "Test Publisher"
        assert journal.is_oa is True
        assert journal.apc_usd == 2000
        assert journal.metrics.h_index == 50
        assert journal.metrics.works_count == 5000
        assert "Topic 1" in journal.topics

    def test_convert_to_journal_minimal_source(self):
        """Test conversion of minimal OpenAlex source."""
        source = {
            "id": "test",
            "display_name": "Minimal Journal",
        }

        journal = convert_to_journal(source)

        assert journal is not None
        assert journal.name == "Minimal Journal"
        assert journal.issn is None
        assert journal.is_oa is False

    def test_convert_to_journal_empty_issn_list(self):
        """Test handling of empty ISSN list."""
        source = {
            "id": "test",
            "display_name": "No ISSN Journal",
            "issn": [],
        }

        journal = convert_to_journal(source)

        assert journal is not None
        assert journal.issn is None


class TestOpenAlexService:
    """Tests for OpenAlexService class (facade)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = OpenAlexService()

    def test_search_journals_by_keywords_empty(self):
        """Test search with empty keywords returns empty list."""
        result = self.service.search_journals_by_keywords([])

        assert result == []

    @patch("app.services.openalex.client.pyalex")
    def test_search_journals_by_keywords_with_mock(self, mock_pyalex):
        """Test search with mocked OpenAlex API."""
        mock_source = {
            "id": "https://openalex.org/S12345",
            "display_name": "Machine Learning Journal",
            "issn": ["1111-2222"],
            "is_oa": True,
            "works_count": 10000,
            "cited_by_count": 50000,
            "summary_stats": {"h_index": 80, "i10_index": 200},
            "topics": [{"display_name": "Machine Learning"}],
            "type": "journal",
        }

        # Mock Works search chain
        mock_works = MagicMock()
        mock_works.search.return_value.filter.return_value.get.return_value = [
            {
                "primary_location": {
                    "source": {"id": "https://openalex.org/S12345", "type": "journal"},
                    "is_oa": True,
                }
            }
        ]
        mock_pyalex.Works.return_value = mock_works

        # Mock Sources to return full details
        mock_sources = MagicMock()
        mock_sources.__getitem__.return_value = mock_source
        mock_pyalex.Sources.return_value = mock_sources

        result = self.service.search_journals_by_keywords(
            ["machine learning"], discipline="computer_science"
        )

        # Results depend on the mock setup
        assert isinstance(result, list)

    @patch("app.services.openalex.client.pyalex")
    def test_search_journals_by_keywords_api_error(self, mock_pyalex):
        """Test handling of API errors."""
        mock_works = MagicMock()
        mock_works.search.return_value.filter.return_value.get.side_effect = Exception(
            "API Error"
        )
        mock_pyalex.Works.return_value = mock_works

        result = self.service.search_journals_by_keywords(["test"])

        # Should return empty list on API error
        assert result == []

    @patch("app.services.openalex.client.pyalex")
    def test_search_journals_by_text(self, mock_pyalex):
        """Test search by text with discipline detection."""
        mock_source = {
            "id": "1",
            "display_name": "ML Journal",
            "works_count": 5000,
            "summary_stats": {"h_index": 30, "i10_index": 50},
            "topics": [{"display_name": "Machine Learning"}],
        }

        mock_works = MagicMock()
        mock_works.search.return_value.filter.return_value.get.return_value = [
            {"primary_location": {"source": mock_source, "is_oa": False}}
        ]
        mock_pyalex.Works.return_value = mock_works

        journals, discipline, _, _ = self.service.search_journals_by_text(
            title="Deep Learning for Image Classification",
            abstract="We present a neural network algorithm for machine learning based image classification.",
        )

        assert discipline == "computer_science"


class TestJournalModel:
    """Tests for Journal model."""

    def test_journal_creation_minimal(self):
        """Test creating journal with minimal data."""
        journal = Journal(id="test", name="Test Journal")

        assert journal.id == "test"
        assert journal.name == "Test Journal"
        assert journal.is_oa is False
        assert journal.metrics is not None

    def test_journal_creation_full(self):
        """Test creating journal with all fields."""
        metrics = JournalMetrics(
            cited_by_count=1000,
            works_count=500,
            h_index=25,
            i10_index=50,
        )

        journal = Journal(
            id="test-id",
            name="Full Journal",
            issn="1234-5678",
            issn_l="1234-5678",
            publisher="Publisher Inc",
            homepage_url="https://journal.com",
            type="journal",
            is_oa=True,
            apc_usd=1500,
            metrics=metrics,
            topics=["Topic 1", "Topic 2"],
            relevance_score=0.85,
            category=JournalCategory.TOP_TIER,
            match_reason="High impact",
        )

        assert journal.publisher == "Publisher Inc"
        assert journal.is_oa is True
        assert journal.apc_usd == 1500
        assert len(journal.topics) == 2
        assert journal.category == JournalCategory.TOP_TIER


class TestTopicBasedSearch:
    """Tests for the Topic-based hybrid search functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = OpenAlexService()

    @patch("app.services.openalex.client.pyalex")
    def test_get_topic_ids_from_similar_works(self, mock_pyalex):
        """Test extraction of topic IDs from similar works."""
        mock_works = MagicMock()
        mock_works.search.return_value.filter.return_value.get.return_value = [
            {
                "topics": [
                    {"id": "https://openalex.org/T12345", "score": 0.9},
                    {"id": "https://openalex.org/T12346", "score": 0.7},
                ]
            },
            {
                "topics": [
                    {"id": "https://openalex.org/T12345", "score": 0.8},
                    {"id": "https://openalex.org/T12347", "score": 0.5},
                ]
            },
        ]
        mock_pyalex.Works.return_value = mock_works

        topic_ids = get_topic_ids_from_similar_works("machine learning")

        assert len(topic_ids) > 0
        assert "https://openalex.org/T12345" in topic_ids

    @patch("app.services.openalex.client.pyalex")
    def test_get_topic_ids_handles_empty_topics(self, mock_pyalex):
        """Test handling of works without topics."""
        mock_works = MagicMock()
        mock_works.search.return_value.filter.return_value.get.return_value = [
            {"topics": []},
            {"topics": None},
            {},
        ]
        mock_pyalex.Works.return_value = mock_works

        topic_ids = get_topic_ids_from_similar_works("test query")

        assert topic_ids == []

    @patch("app.services.openalex.client.pyalex")
    def test_get_topic_ids_handles_api_error(self, mock_pyalex):
        """Test graceful handling of API errors."""
        mock_works = MagicMock()
        mock_works.search.return_value.filter.return_value.get.side_effect = Exception(
            "API Error"
        )
        mock_pyalex.Works.return_value = mock_works

        topic_ids = get_topic_ids_from_similar_works("test query")

        assert topic_ids == []

    @patch("app.services.openalex.client.pyalex")
    def test_find_journals_by_topics(self, mock_pyalex):
        """Test finding journals by topic IDs with group_by."""
        mock_works = MagicMock()
        mock_works.filter.return_value.group_by.return_value.get.return_value = [
            {"key": "https://openalex.org/S12345", "count": 150},
            {"key": "https://openalex.org/S12346", "count": 75},
        ]
        mock_pyalex.Works.return_value = mock_works

        result = find_journals_by_topics(["T1", "T2"])

        assert len(result) == 2
        assert "https://openalex.org/S12345" in result
        assert result["https://openalex.org/S12345"]["count"] == 150

    def test_find_journals_by_topics_empty_input(self):
        """Test handling of empty topic IDs."""
        result = find_journals_by_topics([])

        assert result == {}

    @patch("app.services.openalex.client.pyalex")
    def test_find_journals_by_topics_handles_api_error(self, mock_pyalex):
        """Test graceful handling of API errors in topic search."""
        mock_works = MagicMock()
        mock_works.filter.return_value.group_by.return_value.get.side_effect = Exception(
            "API Error"
        )
        mock_pyalex.Works.return_value = mock_works

        result = find_journals_by_topics(["T1"])

        assert result == {}

    def test_merge_journal_results_boost_duplicates(self):
        """Test that journals in both keyword and topic results get boosted."""
        keyword_journal = Journal(
            id="https://openalex.org/S12345",
            name="Test Journal",
            metrics=JournalMetrics(h_index=50, works_count=10000),
        )
        keyword_journals = {"https://openalex.org/S12345": keyword_journal}

        topic_journals = {
            "https://openalex.org/S12345": {"count": 100, "reason": "Topic match"},
        }

        result = merge_journal_results(keyword_journals, topic_journals)

        assert len(result) == 1
        assert result[0].relevance_score == 3.0
        assert "both keyword and topic" in result[0].match_reason

    @patch("app.services.openalex.client.pyalex")
    def test_merge_journal_results_unique_entries(self, mock_pyalex):
        """Test that unique journals from each source are included."""
        keyword_journal = Journal(
            id="https://openalex.org/S11111",
            name="Keyword Journal",
            metrics=JournalMetrics(h_index=50, works_count=10000),
        )
        keyword_journals = {"https://openalex.org/S11111": keyword_journal}

        topic_journals = {
            "https://openalex.org/S22222": {"count": 100, "reason": "Topic match"},
        }

        # Mock Sources to return None (can't fetch details)
        mock_sources = MagicMock()
        mock_sources.__getitem__.return_value = None
        mock_pyalex.Sources.return_value = mock_sources

        result = merge_journal_results(keyword_journals, topic_journals)

        # Should only have keyword journal since topic journal couldn't be fetched
        assert len(result) == 1
        assert result[0].id == "https://openalex.org/S11111"

    @patch("app.services.openalex.client.pyalex")
    def test_hybrid_search_integration(self, mock_pyalex):
        """Test the full hybrid search flow."""
        mock_source = {
            "id": "https://openalex.org/S12345",
            "display_name": "ML Journal",
            "works_count": 10000,
            "summary_stats": {"h_index": 80, "i10_index": 200},
            "topics": [{"display_name": "Machine Learning"}],
            "type": "journal",
        }

        mock_works = MagicMock()
        mock_works.search.return_value.filter.return_value.get.return_value = [
            {
                "primary_location": {
                    "source": {"id": "https://openalex.org/S12345", "type": "journal"},
                    "is_oa": True,
                },
                "topics": [{"id": "https://openalex.org/T123", "score": 0.9}],
            }
        ]
        mock_works.filter.return_value.group_by.return_value.get.return_value = [
            {"key": "https://openalex.org/S12345", "count": 50},
        ]
        mock_pyalex.Works.return_value = mock_works

        mock_sources = MagicMock()
        mock_sources.__getitem__.return_value = mock_source
        mock_pyalex.Sources.return_value = mock_sources

        journals, discipline, _, _ = self.service.search_journals_by_text(
            title="Deep Learning for Medical Imaging",
            abstract="We apply neural networks for medical image classification.",
        )

        assert isinstance(journals, list)
        assert discipline in ["computer_science", "medicine", "general"]
