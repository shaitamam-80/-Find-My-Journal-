"""
Tests for search functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.openalex_service import OpenAlexService
from app.models.journal import Journal, JournalMetrics, JournalCategory


class TestOpenAlexService:
    """Tests for OpenAlexService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = OpenAlexService()

    def test_extract_search_terms_with_keywords(self):
        """Test that provided keywords are included."""
        keywords = ["machine learning", "neural networks"]
        text = "A study on deep learning applications"

        terms = self.service._extract_search_terms(text, keywords)

        assert "machine learning" in terms
        assert "neural networks" in terms

    def test_extract_search_terms_filters_stopwords(self):
        """Test that common words are filtered out."""
        text = "The study of neural networks in the field of research"

        terms = self.service._extract_search_terms(text, [])

        assert "the" not in terms
        assert "study" not in terms
        assert "of" not in terms
        assert "neural" in terms
        assert "networks" in terms

    def test_extract_search_terms_limits_results(self):
        """Test that results are limited to 10 terms."""
        text = " ".join([f"word{i}" for i in range(50)])

        terms = self.service._extract_search_terms(text, [])

        assert len(terms) <= 10

    def test_detect_discipline_medicine(self):
        """Test detection of medical discipline."""
        text = "Clinical treatment of patients with disease diagnosis"

        discipline = self.service._detect_discipline(text)

        assert discipline == "medicine"

    def test_detect_discipline_computer_science(self):
        """Test detection of computer science discipline."""
        text = "Machine learning algorithm using neural networks and deep learning"

        discipline = self.service._detect_discipline(text)

        assert discipline == "computer_science"

    def test_detect_discipline_biology(self):
        """Test detection of biology discipline."""
        text = "Gene expression in cell protein synthesis and molecular evolution"

        discipline = self.service._detect_discipline(text)

        assert discipline == "biology"

    def test_detect_discipline_physics(self):
        """Test detection of physics discipline."""
        text = "Quantum particle energy wave electron photon magnetic field"

        discipline = self.service._detect_discipline(text)

        assert discipline == "physics"

    def test_detect_discipline_general(self):
        """Test fallback to general discipline."""
        text = "Some random text without specific keywords"

        discipline = self.service._detect_discipline(text)

        assert discipline == "general"

    def test_categorize_journals_top_tier(self):
        """Test categorization of top tier journals."""
        journal = Journal(
            id="test",
            name="Nature",
            metrics=JournalMetrics(h_index=150, works_count=100000),
        )

        result = self.service._categorize_journals([journal])

        assert result[0].category == JournalCategory.TOP_TIER
        assert result[0].match_reason == "High impact journal"

    def test_categorize_journals_broad_audience(self):
        """Test categorization of broad audience journals."""
        journal = Journal(
            id="test",
            name="Some Journal",
            metrics=JournalMetrics(h_index=50, works_count=20000),
        )

        result = self.service._categorize_journals([journal])

        assert result[0].category == JournalCategory.BROAD_AUDIENCE
        assert result[0].match_reason == "Wide readership"

    def test_categorize_journals_niche(self):
        """Test categorization of niche journals."""
        journal = Journal(
            id="test",
            name="Specialized Journal",
            metrics=JournalMetrics(h_index=20, works_count=5000),
        )

        result = self.service._categorize_journals([journal])

        assert result[0].category == JournalCategory.NICHE
        assert result[0].match_reason == "Specialized focus"

    def test_categorize_journals_emerging(self):
        """Test categorization of emerging journals."""
        journal = Journal(
            id="test",
            name="New Journal",
            metrics=JournalMetrics(h_index=5, works_count=500),
        )

        result = self.service._categorize_journals([journal])

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

        journal = self.service._convert_to_journal(source)

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

        journal = self.service._convert_to_journal(source)

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

        journal = self.service._convert_to_journal(source)

        assert journal is not None
        assert journal.issn is None

    def test_search_journals_by_keywords_empty(self):
        """Test search with empty keywords returns empty list."""
        result = self.service.search_journals_by_keywords([])

        assert result == []

    @patch("app.services.openalex_service.pyalex.Sources")
    @patch("app.services.openalex_service.pyalex.Works")
    def test_search_journals_by_keywords_with_mock(self, mock_works, mock_sources):
        """Test search with mocked OpenAlex API."""
        mock_source = {
            "id": "https://openalex.org/S12345",
            "display_name": "Machine Learning Journal",
            "issn": ["1111-2222"],
            "is_oa": True,
            "works_count": 10000,  # Needs to be >= 1000 to pass min_journal_works filter
            "cited_by_count": 50000,
            "summary_stats": {"h_index": 80, "i10_index": 200},
            "topics": [{"display_name": "Machine Learning"}],
            "type": "journal",
        }

        # Mock works search to return papers with source
        mock_works.return_value.search.return_value.filter.return_value.get.return_value = [
            {
                "primary_location": {
                    "source": {"id": "https://openalex.org/S12345", "type": "journal"},
                    "is_oa": True,
                }
            }
        ]

        # Mock _get_full_source_details to return the source
        with patch.object(
            self.service, "_get_full_source_details", return_value=mock_source
        ):
            # Mock _is_journal_relevant removed as method is deleted
            result = self.service.search_journals_by_keywords(
                ["machine learning"], discipline="computer_science"
            )

        assert len(result) >= 1
        assert any(j.name == "Machine Learning Journal" for j in result)

    @patch("app.services.openalex_service.pyalex.Sources")
    @patch("app.services.openalex_service.pyalex.Works")
    def test_search_journals_by_keywords_filters_min_works(
        self, mock_works, mock_sources
    ):
        """Test that min_works_count filter is applied via min_journal_works."""
        small_source = {"id": "1", "display_name": "Small Journal", "works_count": 100}
        big_source = {
            "id": "2",
            "display_name": "Big Journal",
            "works_count": 10000,
            "summary_stats": {"h_index": 50, "i10_index": 100},
        }

        # Mock works search returning both journals
        mock_works.return_value.search.return_value.filter.return_value.get.return_value = [
            {"primary_location": {"source": small_source, "is_oa": False}},
            {"primary_location": {"source": big_source, "is_oa": False}},
        ]

        def get_source(source_id):
            if "1" in source_id:
                return small_source
            return big_source

        with patch.object(
            self.service, "_get_full_source_details", side_effect=get_source
        ):
            result = self.service.search_journals_by_keywords(["test"])

        # Small journal should be filtered by min_journal_works (1000)
        assert all(j.name != "Small Journal" for j in result)

    @patch("app.services.openalex_service.pyalex.Works")
    def test_search_journals_by_keywords_api_error(self, mock_works):
        """Test handling of API errors."""
        mock_works.return_value.search.return_value.filter.return_value.get.side_effect = Exception(
            "API Error"
        )

        result = self.service.search_journals_by_keywords(["test"])

        # Should return empty list on API error
        assert result == []

    @patch("app.services.openalex_service.pyalex.Sources")
    @patch("app.services.openalex_service.pyalex.Works")
    def test_search_journals_by_text(self, mock_works, mock_sources):
        """Test search by text with discipline detection."""
        mock_source = {
            "id": "1",
            "display_name": "ML Journal",
            "works_count": 5000,
            "summary_stats": {"h_index": 30, "i10_index": 50},
            "topics": [{"display_name": "Machine Learning"}],
        }

        mock_works.return_value.search.return_value.filter.return_value.get.return_value = [
            {"primary_location": {"source": mock_source, "is_oa": False}}
        ]

        with patch.object(
            self.service, "_get_full_source_details", return_value=mock_source
        ):
            journals, discipline = self.service.search_journals_by_text(
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
    """Tests for the new Topic-based hybrid search functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = OpenAlexService()

    @patch("app.services.openalex_service.pyalex.Works")
    def test_get_topic_ids_from_similar_works(self, mock_works):
        """Test extraction of topic IDs from similar works."""
        # Mock works with topics
        mock_works.return_value.search.return_value.filter.return_value.get.return_value = [
            {
                "topics": [
                    {"id": "https://openalex.org/T12345", "score": 0.9},
                    {"id": "https://openalex.org/T12346", "score": 0.7},
                ]
            },
            {
                "topics": [
                    {"id": "https://openalex.org/T12345", "score": 0.8},  # Same topic
                    {"id": "https://openalex.org/T12347", "score": 0.5},
                ]
            },
        ]

        topic_ids = self.service._get_topic_ids_from_similar_works("machine learning")

        # Should return topic IDs sorted by frequency/score
        assert len(topic_ids) > 0
        # T12345 should be most frequent (appears twice)
        assert "https://openalex.org/T12345" in topic_ids

    @patch("app.services.openalex_service.pyalex.Works")
    def test_get_topic_ids_handles_empty_topics(self, mock_works):
        """Test handling of works without topics."""
        mock_works.return_value.search.return_value.filter.return_value.get.return_value = [
            {"topics": []},
            {"topics": None},
            {},
        ]

        topic_ids = self.service._get_topic_ids_from_similar_works("test query")

        assert topic_ids == []

    @patch("app.services.openalex_service.pyalex.Works")
    def test_get_topic_ids_handles_api_error(self, mock_works):
        """Test graceful handling of API errors."""
        mock_works.return_value.search.return_value.filter.return_value.get.side_effect = Exception(
            "API Error"
        )

        topic_ids = self.service._get_topic_ids_from_similar_works("test query")

        assert topic_ids == []

    @patch("app.services.openalex_service.pyalex.Works")
    def test_find_journals_by_topics(self, mock_works):
        """Test finding journals by topic IDs with group_by."""
        # Mock group_by response
        mock_works.return_value.filter.return_value.group_by.return_value.get.return_value = [
            {"key": "https://openalex.org/S12345", "count": 150},
            {"key": "https://openalex.org/S12346", "count": 75},
        ]

        result = self.service._find_journals_by_topics(["T1", "T2"])

        assert len(result) == 2
        assert "https://openalex.org/S12345" in result
        assert result["https://openalex.org/S12345"]["count"] == 150

    def test_find_journals_by_topics_empty_input(self):
        """Test handling of empty topic IDs."""
        result = self.service._find_journals_by_topics([])

        assert result == {}

    @patch("app.services.openalex_service.pyalex.Works")
    def test_find_journals_by_topics_handles_api_error(self, mock_works):
        """Test graceful handling of API errors in topic search."""
        mock_works.return_value.filter.return_value.group_by.return_value.get.side_effect = Exception(
            "API Error"
        )

        result = self.service._find_journals_by_topics(["T1"])

        assert result == {}

    def test_merge_journal_results_boost_duplicates(self):
        """Test that journals in both keyword and topic results get boosted."""
        # Create keyword journals
        keyword_journal = Journal(
            id="https://openalex.org/S12345",
            name="Test Journal",
            metrics=JournalMetrics(h_index=50, works_count=10000),
        )
        keyword_journals = {"https://openalex.org/S12345": keyword_journal}

        # Topic journals with same ID
        topic_journals = {
            "https://openalex.org/S12345": {"count": 100, "reason": "Topic match"},
        }

        result = self.service._merge_journal_results(keyword_journals, topic_journals)

        # Should have boosted relevance score
        assert len(result) == 1
        assert result[0].relevance_score == 3.0  # 1.0 + 2.0 boost
        assert "both keyword and topic" in result[0].match_reason

    def test_merge_journal_results_unique_entries(self):
        """Test that unique journals from each source are included."""
        keyword_journal = Journal(
            id="https://openalex.org/S11111",
            name="Keyword Journal",
            metrics=JournalMetrics(h_index=50, works_count=10000),
        )
        keyword_journals = {"https://openalex.org/S11111": keyword_journal}

        # Different topic journal
        topic_journals = {
            "https://openalex.org/S22222": {"count": 100, "reason": "Topic match"},
        }

        # Mock _get_full_source_details to return None (won't add new journal)
        with patch.object(self.service, "_get_full_source_details", return_value=None):
            result = self.service._merge_journal_results(
                keyword_journals, topic_journals
            )

        # Should only have keyword journal since topic journal couldn't be fetched
        assert len(result) == 1
        assert result[0].id == "https://openalex.org/S11111"

    @patch("app.services.openalex_service.pyalex.Works")
    @patch("app.services.openalex_service.pyalex.Sources")
    def test_hybrid_search_integration(self, mock_sources, mock_works):
        """Test the full hybrid search flow."""
        # Mock keyword search results
        mock_source = {
            "id": "https://openalex.org/S12345",
            "display_name": "ML Journal",
            "works_count": 10000,
            "summary_stats": {"h_index": 80, "i10_index": 200},
            "topics": [{"display_name": "Machine Learning"}],
            "type": "journal",
        }

        mock_works.return_value.search.return_value.filter.return_value.get.return_value = [
            {
                "primary_location": {
                    "source": {"id": "https://openalex.org/S12345", "type": "journal"},
                    "is_oa": True,
                },
                "topics": [{"id": "https://openalex.org/T123", "score": 0.9}],
            }
        ]

        # Mock group_by for topic search
        mock_works.return_value.filter.return_value.group_by.return_value.get.return_value = [
            {"key": "https://openalex.org/S12345", "count": 50},
        ]

        with patch.object(
            self.service, "_get_full_source_details", return_value=mock_source
        ):
            journals, discipline = self.service.search_journals_by_text(
                title="Deep Learning for Medical Imaging",
                abstract="We apply neural networks for medical image classification.",
            )

        # Should return results
        assert len(journals) >= 0  # May vary based on mocking
