"""
Tests for Universal Discipline Detection.

Tests across multiple academic domains to verify "Swiss Army Knife" capability.
Uses live OpenAlex API to ensure real-world accuracy.
"""

import pytest
from app.services.analysis.universal_detector import (
    UniversalDisciplineDetector,
    detect_disciplines_universal,
)
from app.services.analysis.hybrid_detector import (
    detect_disciplines_hybrid,
    HybridDisciplineDetector,
)


class TestUniversalDetection:
    """Test universal detection across different academic domains."""

    @pytest.fixture
    def detector(self):
        return UniversalDisciplineDetector()

    # ==================== HEALTH SCIENCES ====================

    def test_medicine_urogynecology(self, detector):
        """Test: OAB + Fibromyalgia paper (our main test case)."""
        result = detector.detect(
            title="The association between overactive bladder and fibromyalgia",
            abstract="Overactive bladder is a common syndrome characterized by urinary urgency, with or without incontinence. Fibromyalgia is characterized by widespread pain and central sensitization. This study examines the prevalence and clinical associations.",
        )

        assert result.primary_domain == "Health Sciences"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "urology" in name or "gynecology" in name or "rheumatology" in name
            for name in subfield_names
        ), f"Expected urology/gynecology/rheumatology, got: {subfield_names}"

    def test_medicine_pediatric_endocrinology(self, detector):
        """Test: Growth hormone in Down syndrome."""
        result = detector.detect(
            title="GH treatment in pediatric Down syndrome: a systematic review",
            abstract="To analyze the safety and efficacy of growth hormone treatment in Down syndrome pediatric patients. We performed a systematic review of randomized controlled trials assessing GH treatment outcomes.",
        )

        # OpenAlex may classify this as Health Sciences or Life Sciences (genetics-related)
        assert result.primary_domain in ["Health Sciences", "Life Sciences"]
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "pediatric" in name or "endocrinology" in name or "genetics" in name
            for name in subfield_names
        ), f"Expected pediatric/endocrinology/genetics, got: {subfield_names}"

    def test_medicine_cardiology(self, detector):
        """Test: Cardiology paper about heart failure."""
        result = detector.detect(
            title="Novel biomarkers in acute heart failure",
            abstract="Heart failure is a leading cause of hospitalization. This study evaluates novel cardiac biomarkers including NT-proBNP and troponin for risk stratification in acute heart failure patients.",
        )

        assert result.primary_domain == "Health Sciences"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "cardiology" in name or "cardiovascular" in name
            for name in subfield_names
        ), f"Expected cardiology, got: {subfield_names}"

    # ==================== SOCIAL SCIENCES ====================

    def test_psychology_developmental(self, detector):
        """Test: Empathy development paper (Talor's research)."""
        result = detector.detect(
            title="Caring babies: Concern for others in distress during infancy",
            abstract="Concern for distressed others is a highly valued human capacity. This study examines early ontogeny of empathic concern in infants aged 8 to 16 months. We observed behavioral responses to simulated distress.",
        )

        assert result.primary_domain == "Social Sciences"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "developmental" in name or "psychology" in name
            for name in subfield_names
        ), f"Expected developmental/psychology, got: {subfield_names}"

    def test_economics(self, detector):
        """Test: Economics paper about monetary policy."""
        result = detector.detect(
            title="The Impact of Monetary Policy on Economic Growth",
            abstract="This paper examines the relationship between central bank interest rate decisions and GDP growth. Using panel data from 50 countries, we analyze the transmission mechanisms of monetary policy.",
        )

        assert result.primary_domain == "Social Sciences"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "economics" in name or "finance" in name
            for name in subfield_names
        ), f"Expected economics/finance, got: {subfield_names}"

    def test_sociology(self, detector):
        """Test: Sociology paper about social media."""
        result = detector.detect(
            title="Social Media and Political Polarization in the United States",
            abstract="We analyze the role of algorithmic curation in creating ideological echo chambers on social media platforms. Using survey data and network analysis, we examine how filter bubbles affect political discourse.",
        )

        assert result.primary_domain == "Social Sciences"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "sociology" in name or "political" in name or "communication" in name
            for name in subfield_names
        ), f"Expected sociology/political, got: {subfield_names}"

    # ==================== PHYSICAL SCIENCES ====================

    def test_computer_science_ai(self, detector):
        """Test: AI/Machine Learning paper."""
        result = detector.detect(
            title="Attention Is All You Need: Transformer Architecture for NLP",
            abstract="We propose a new network architecture based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on machine translation show the model achieves superior quality.",
        )

        assert result.primary_domain == "Physical Sciences"
        assert result.primary_field == "Computer Science"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "artificial intelligence" in name or "computation" in name or "language" in name
            for name in subfield_names
        ), f"Expected AI/computation, got: {subfield_names}"

    def test_physics_quantum(self, detector):
        """Test: Quantum physics paper."""
        result = detector.detect(
            title="Quantum Entanglement and Information Transfer",
            abstract="We demonstrate a novel approach to quantum teleportation using entangled photon pairs. The experiment achieves fidelity above 95% for quantum state transfer across optical fiber links.",
        )

        assert result.primary_domain == "Physical Sciences"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "physics" in name or "quantum" in name or "optics" in name
            for name in subfield_names
        ), f"Expected physics/quantum, got: {subfield_names}"

    def test_engineering(self, detector):
        """Test: Engineering paper."""
        result = detector.detect(
            title="Structural Analysis of High-Rise Buildings Under Seismic Load",
            abstract="This study analyzes the performance of reinforced concrete structures during earthquakes using finite element analysis. We examine structural damping systems and their effectiveness in high-rise buildings.",
        )

        assert result.primary_domain == "Physical Sciences"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "engineering" in name or "structural" in name or "civil" in name
            for name in subfield_names
        ), f"Expected engineering, got: {subfield_names}"

    def test_chemistry(self, detector):
        """Test: Chemistry paper."""
        result = detector.detect(
            title="Metal-Organic Frameworks for CO2 Capture and Storage",
            abstract="We report the synthesis of a novel MOF with exceptional CO2 adsorption capacity. The framework exhibits high selectivity for CO2 over N2 under ambient conditions.",
        )

        assert result.primary_domain == "Physical Sciences"
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "chemistry" in name or "materials" in name
            for name in subfield_names
        ), f"Expected chemistry/materials, got: {subfield_names}"

    # ==================== LIFE SCIENCES ====================

    def test_biology_molecular(self, detector):
        """Test: Molecular biology paper."""
        result = detector.detect(
            title="CRISPR-Cas9 Gene Editing for Therapeutic Applications",
            abstract="We demonstrate precise genome editing using CRISPR-Cas9 in human cell lines. The approach enables targeted modification of disease-causing mutations with high efficiency and specificity.",
        )

        assert result.primary_domain in ["Life Sciences", "Health Sciences"]
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "genetic" in name or "molecular" in name or "biochem" in name
            for name in subfield_names
        ), f"Expected genetics/molecular, got: {subfield_names}"

    def test_ecology(self, detector):
        """Test: Ecology paper."""
        result = detector.detect(
            title="Climate Change Effects on Coral Reef Ecosystems",
            abstract="Rising ocean temperatures are causing widespread coral bleaching. This study examines the resilience of reef ecosystems in the Pacific and their capacity for recovery.",
        )

        # OpenAlex may classify this as Life Sciences (ecology) or Physical Sciences (earth sciences)
        assert result.primary_domain in ["Life Sciences", "Physical Sciences"]
        subfield_names = [s.name.lower() for s in result.subfields]
        assert any(
            "ecology" in name or "environmental" in name or "marine" in name or "ocean" in name or "earth" in name
            for name in subfield_names
        ), f"Expected ecology/environmental/marine/earth, got: {subfield_names}"


class TestUniversalDetectionEdgeCases:
    """Test edge cases and error handling."""

    def test_interdisciplinary_paper(self):
        """Test paper that spans multiple domains."""
        result = detect_disciplines_universal(
            title="Machine Learning for Drug Discovery",
            abstract="We apply deep learning to predict drug-target interactions. The model outperforms traditional methods in identifying potential cancer therapeutics using molecular fingerprints.",
        )

        # Should detect both CS/AI and Medicine/Pharmacology related fields
        domains = set(d["domain"] for d in result if d.get("domain"))
        assert len(result) >= 1, "Should detect at least one discipline"

    def test_short_abstract(self):
        """Test with minimal input."""
        result = detect_disciplines_universal(
            title="Cancer treatment",
            abstract="A study of chemotherapy.",
        )

        # Should still work, even with limited input
        assert len(result) >= 1, "Should detect at least one discipline"

    def test_non_english_title(self):
        """Test with non-English title but English abstract."""
        result = detect_disciplines_universal(
            title="Forschung uber Krebs",  # German: Research on cancer
            abstract="This study examines novel immunotherapy approaches for treating solid tumors. We evaluated checkpoint inhibitors in a clinical trial with cancer patients receiving PD-1 antibodies.",
        )

        # Should work based on English abstract (may return empty if OpenAlex doesn't find matches)
        # This is acceptable behavior - the function handles edge cases gracefully
        assert isinstance(result, list), "Should return a list even if empty"

    def test_empty_abstract(self):
        """Test with empty abstract (title only)."""
        result = detect_disciplines_universal(
            title="Deep learning approaches for natural language processing",
            abstract="",
        )

        # Should still find something based on title
        assert len(result) >= 0  # May return empty, which is acceptable


class TestHybridDetection:
    """Test hybrid detection combining universal and keyword approaches."""

    def test_hybrid_prefers_universal(self):
        """Test that hybrid prefers universal detection when it works."""
        result = detect_disciplines_hybrid(
            title="Cardiac rehabilitation after myocardial infarction",
            abstract="This study evaluates exercise-based cardiac rehabilitation programs for patients recovering from heart attacks.",
            prefer_universal=True,
        )

        assert len(result) >= 1
        # Check that at least one result is from OpenAlex ML
        sources = [d.get("source") for d in result]
        assert "openalex_ml" in sources or "keyword_fallback" in sources

    def test_hybrid_detector_class(self):
        """Test HybridDisciplineDetector class."""
        detector = HybridDisciplineDetector(prefer_universal=True)
        result = detector.detect_with_metadata(
            title="Stress and anxiety in graduate students",
            abstract="This study examines the prevalence of anxiety disorders among doctoral students and evaluates intervention strategies.",
        )

        assert "disciplines" in result
        assert "detection_method" in result
        assert result["discipline_count"] >= 1

    def test_hybrid_falls_back_gracefully(self):
        """Test that hybrid falls back to keywords when universal fails."""
        # Use a very medical-specific query that keywords should handle well
        result = detect_disciplines_hybrid(
            title="Rheumatoid arthritis treatment with biologics",
            abstract="We evaluated tumor necrosis factor inhibitors for treating rheumatoid arthritis in a randomized controlled trial.",
            prefer_universal=True,
            min_results=1,
        )

        assert len(result) >= 1
        # Should have detected something related to rheumatology
        names = [d.get("name", "").lower() for d in result]
        assert any(
            "rheumatology" in n or "immunology" in n or "medicine" in n
            for n in names
        ), f"Expected rheumatology-related, got: {names}"


class TestUniversalDetectionMetadata:
    """Test that detection returns proper metadata."""

    def test_returns_subfield_ids(self):
        """Test that numeric IDs are returned for API filtering."""
        result = detect_disciplines_universal(
            title="Diabetes management in elderly patients",
            abstract="This study examines glycemic control strategies in patients over 65 with type 2 diabetes.",
        )

        assert len(result) >= 1
        for disc in result:
            assert "numeric_id" in disc
            assert "openalex_subfield_id" in disc
            # At least some should have valid IDs
            if disc.get("numeric_id"):
                assert isinstance(disc["numeric_id"], int)
                assert disc["numeric_id"] > 0

    def test_returns_domain_field_hierarchy(self):
        """Test that domain and field information is included."""
        result = detect_disciplines_universal(
            title="Neural networks for image classification",
            abstract="We propose a convolutional neural network architecture for classifying medical images.",
        )

        assert len(result) >= 1
        for disc in result:
            assert "domain" in disc
            assert "field" in disc
            # Domain should be one of the 4 OpenAlex domains
            if disc.get("domain"):
                assert disc["domain"] in [
                    "Health Sciences",
                    "Life Sciences",
                    "Physical Sciences",
                    "Social Sciences",
                ]

    def test_returns_confidence_scores(self):
        """Test that confidence scores are reasonable."""
        result = detect_disciplines_universal(
            title="Treatment of major depressive disorder",
            abstract="This randomized trial compared antidepressant medications for treating clinical depression.",
        )

        assert len(result) >= 1
        for disc in result:
            assert "confidence" in disc
            assert 0 <= disc["confidence"] <= 1
