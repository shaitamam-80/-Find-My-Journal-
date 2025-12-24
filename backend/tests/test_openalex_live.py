"""
Live integration test for OpenAlex API.
Run this manually to verify real API connectivity.

Usage: pytest tests/test_openalex_live.py -v -s
"""
import pytest
from app.services.openalex_service import OpenAlexService


class TestOpenAlexLiveAPI:
    """Live tests against real OpenAlex API."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = OpenAlexService()

    @pytest.mark.live
    def test_search_machine_learning_journals(self):
        """Test real search for machine learning journals."""
        journals = self.service.search_journals_by_keywords(["machine learning"])

        print(f"\nFound {len(journals)} journals for 'machine learning':")
        for j in journals[:5]:
            print(f"  - {j.name} (OA: {j.is_oa}, works: {j.metrics.works_count})")

        assert len(journals) > 0
        assert all(j.name for j in journals)

    @pytest.mark.live
    def test_search_by_abstract(self):
        """Test real search with title and abstract."""
        title = "Deep Learning Approaches for Medical Image Analysis"
        abstract = """
        We present a novel deep learning framework for automated analysis of
        medical images. Our approach uses convolutional neural networks to
        detect abnormalities in chest X-rays with high accuracy. The model
        was trained on a large dataset of annotated radiographs and achieves
        state-of-the-art performance in detecting pneumonia and other
        pulmonary conditions.
        """

        journals, discipline, _, _ = self.service.search_journals_by_text(
            title=title,
            abstract=abstract,
            prefer_open_access=True,
        )

        print(f"\nDetected discipline: {discipline}")
        print(f"Found {len(journals)} journals:")
        for j in journals[:5]:
            print(f"  - {j.name}")
            print(f"    Category: {j.category.value if j.category else 'N/A'}")
            print(f"    OA: {j.is_oa}, H-Index: {j.metrics.h_index}")
            print(f"    Topics: {', '.join(j.topics[:3]) if j.topics else 'N/A'}")

        assert len(journals) > 0
        # Should detect medicine or computer science
        assert discipline in ["medicine", "computer_science"]

    @pytest.mark.live
    def test_search_biology_journals(self):
        """Test real search for biology journals."""
        title = "Molecular Biology of Gene Expression"
        abstract = """
        This study investigates the molecular mechanisms of gene expression
        and protein synthesis in living cells. We examine how genes are
        transcribed and translated, focusing on the role of RNA polymerase
        and ribosomes in the cellular machinery. Our results demonstrate
        new insights into the regulation of gene expression.
        """

        journals, discipline, _, _ = self.service.search_journals_by_text(
            title=title,
            abstract=abstract,
        )

        print(f"\nDetected discipline: {discipline}")
        print(f"Found {len(journals)} journals for biology topic")
        for j in journals[:3]:
            print(f"  - {j.name}")

        assert len(journals) > 0
        assert discipline == "biology"

    @pytest.mark.live
    def test_open_access_preference(self):
        """Test that OA preference affects results."""
        journals_no_pref = self.service.search_journals_by_keywords(
            ["artificial intelligence"],
            prefer_open_access=False,
        )

        journals_oa_pref = self.service.search_journals_by_keywords(
            ["artificial intelligence"],
            prefer_open_access=True,
        )

        print(f"\nWithout OA preference:")
        for j in journals_no_pref[:3]:
            print(f"  - {j.name} (OA: {j.is_oa})")

        print(f"\nWith OA preference:")
        for j in journals_oa_pref[:3]:
            print(f"  - {j.name} (OA: {j.is_oa})")

        # Both should have results
        assert len(journals_no_pref) > 0
        assert len(journals_oa_pref) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "live"])
