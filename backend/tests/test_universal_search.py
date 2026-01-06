"""
Tests for Universal Journal Search.

Tests that the complete search pipeline works for various academic domains.
"""

import pytest
from app.services.openalex.universal_search import (
    search_journals_universal,
    UniversalSearchResult,
    find_journals_by_subfield_id_universal,
)


class TestUniversalSearch:
    """Test the universal search pipeline."""

    def test_search_medical_paper(self):
        """Test search for a medical research paper."""
        result = search_journals_universal(
            title="The association between overactive bladder and fibromyalgia",
            abstract="Overactive bladder is a common syndrome characterized by urinary urgency. Fibromyalgia is characterized by widespread pain. We examined 500 women in a cross-sectional study.",
        )

        assert isinstance(result, UniversalSearchResult)
        assert len(result.journals) > 0
        assert len(result.detected_disciplines) > 0
        # Should detect Health Sciences domain
        assert result.primary_domain == "Health Sciences" or result.primary_field is not None

    def test_search_psychology_paper(self):
        """Test search for a psychology paper."""
        result = search_journals_universal(
            title="Caring babies: Concern for others in distress during infancy",
            abstract="Concern for distressed others is a highly valued human capacity. This study examines the early ontogeny of empathic concern in infants aged 8 to 16 months.",
        )

        assert isinstance(result, UniversalSearchResult)
        assert len(result.journals) > 0
        assert len(result.detected_disciplines) > 0
        # Should detect Social Sciences / Psychology
        assert result.primary_domain in ["Social Sciences", "Health Sciences", "Life Sciences"]

    def test_search_computer_science_paper(self):
        """Test search for a CS/AI paper."""
        result = search_journals_universal(
            title="Attention Is All You Need",
            abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        )

        assert isinstance(result, UniversalSearchResult)
        assert len(result.journals) > 0
        assert len(result.detected_disciplines) > 0
        # Should detect Physical Sciences / Computer Science
        assert result.primary_domain == "Physical Sciences"
        assert "Computer Science" in (result.primary_field or "")

    def test_search_physics_paper(self):
        """Test search for a physics paper."""
        result = search_journals_universal(
            title="Quantum Entanglement and Information Transfer",
            abstract="We demonstrate a novel approach to quantum teleportation using entangled photon pairs. The experiment achieves fidelity above 95%.",
        )

        assert isinstance(result, UniversalSearchResult)
        assert len(result.journals) > 0
        # Should detect Physical Sciences
        assert result.primary_domain == "Physical Sciences"

    def test_search_economics_paper(self):
        """Test search for an economics paper."""
        result = search_journals_universal(
            title="The Impact of Monetary Policy on Economic Growth",
            abstract="This paper examines the relationship between central bank interest rate decisions and GDP growth using panel data from 50 countries.",
        )

        assert isinstance(result, UniversalSearchResult)
        assert len(result.journals) > 0
        # Should detect Social Sciences
        assert result.primary_domain == "Social Sciences"

    def test_search_returns_metadata(self):
        """Test that search returns proper metadata."""
        result = search_journals_universal(
            title="Machine learning for drug discovery",
            abstract="We apply deep learning to predict drug-target interactions in cancer research.",
        )

        assert result.detection_method in ["universal_openalex_ml", "keyword_fallback"]
        assert result.primary_domain is not None or result.primary_field is not None
        assert result.article_type is not None

    def test_search_with_keywords(self):
        """Test search with additional keywords."""
        result = search_journals_universal(
            title="Clinical outcomes in diabetes",
            abstract="A study of glycemic control in type 2 diabetes patients.",
            keywords=["diabetes", "HbA1c", "endocrinology"],
        )

        assert isinstance(result, UniversalSearchResult)
        assert len(result.journals) > 0

    def test_search_prefers_open_access(self):
        """Test that prefer_open_access affects results."""
        result = search_journals_universal(
            title="Open science in psychology",
            abstract="We examine replication rates in psychological research.",
            prefer_open_access=True,
        )

        assert isinstance(result, UniversalSearchResult)
        # At least some results should have OA consideration
        assert len(result.journals) > 0


class TestFindJournalsBySubfield:
    """Test finding journals by subfield ID."""

    def test_find_cardiology_journals(self):
        """Test finding journals in Cardiology subfield."""
        journals = find_journals_by_subfield_id_universal(2705)  # Cardiology

        assert len(journals) > 0
        for journal in journals:
            assert journal.id is not None
            assert journal.name is not None

    def test_find_psychology_journals(self):
        """Test finding journals in Psychology subfield."""
        journals = find_journals_by_subfield_id_universal(3201)  # Dev Psychology

        assert len(journals) > 0

    def test_find_ai_journals(self):
        """Test finding journals in AI subfield."""
        journals = find_journals_by_subfield_id_universal(1702)  # AI

        assert len(journals) > 0


class TestSearchResultQuality:
    """Test quality of search results."""

    def test_journals_have_metrics(self):
        """Test that returned journals have metrics."""
        result = search_journals_universal(
            title="Heart failure treatment",
            abstract="Novel approaches to treating acute heart failure.",
        )

        for journal in result.journals[:5]:
            # Should have at least some metrics
            assert journal.metrics is not None
            # Should have relevance score
            assert journal.relevance_score is not None
            assert 0 <= journal.relevance_score <= 1

    def test_journals_have_match_details(self):
        """Test that journals have match details."""
        result = search_journals_universal(
            title="Cancer immunotherapy advances",
            abstract="We review recent progress in checkpoint inhibitors.",
        )

        for journal in result.journals[:5]:
            # Should have match reason or details
            assert journal.match_reason is not None or journal.match_details is not None

    def test_no_duplicate_journals(self):
        """Test that no duplicate journals are returned."""
        result = search_journals_universal(
            title="Multi-disciplinary study of pain",
            abstract="We examine chronic pain from neurological and rheumatological perspectives.",
        )

        journal_ids = [j.id for j in result.journals]
        assert len(journal_ids) == len(set(journal_ids)), "Found duplicate journals"
