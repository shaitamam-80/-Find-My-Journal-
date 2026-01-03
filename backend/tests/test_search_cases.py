"""
Search Test Cases for Find My Journal

Real-world test cases to validate search accuracy improvements:
- Multi-discipline detection
- Article type detection
- Journal ranking accuracy
- Irrelevant result filtering

Run with: cd backend && python -m pytest tests/test_search_cases.py -v
"""
import pytest
from typing import List, Dict, Any

# Test cases with expected results
TEST_CASES: List[Dict[str, Any]] = [
    {
        "name": "OAB_Fibromyalgia_Systematic_Review",
        "title": "The association between overactive bladder and fibromyalgia: A systematic review and meta-analysis",
        "abstract": """Background: Overactive bladder is a common syndrome that significantly affects the quality of life. Fibromyalgia is characterized by widespread pain, impacting patients' lives. The exact mechanisms of the two syndromes remain unknown, but there is an overlap between the suspected pathophysiologies.
Objective: To present an overview of the current research on the association between overactive bladder (OAB) and fibromyalgia.
Search strategy: A systematic search of four electronic databases was conducted.
Data collection and analysis: Two reviewers screened the studies for eligibility. Eligible studies were screened for quality. A meta-analysis was performed for eligible studies.
Main results: Seven studies were included in the final review, of which six presented a positive association between the syndromes.""",
        "keywords": ["fibromyalgia", "overactive bladder", "urinary urgency"],
        "expected_disciplines": ["Urology", "Gynecology", "Rheumatology", "Pain Medicine"],
        "expected_article_type": "systematic_review_meta_analysis",
        "must_include_journals": [
            "International Journal of Gynecology & Obstetrics",
            "Neurourology and Urodynamics",
        ],
        "should_warn_or_exclude": [
            "Journal of Clinical Medicine",  # Too generic with irrelevant topics
        ],
    },
    {
        "name": "Cardiology_RCT",
        "title": "Effect of SGLT2 inhibitors on heart failure outcomes: A randomized controlled trial",
        "abstract": """Background: SGLT2 inhibitors have shown promising results in heart failure management. This study evaluates the efficacy of empagliflozin in patients with heart failure with reduced ejection fraction.
Methods: A randomized, double-blind, placebo-controlled trial was conducted across 40 centers. 500 patients were randomly assigned to receive empagliflozin or placebo for 12 months.
Results: The primary endpoint of cardiovascular death or hospitalization for heart failure occurred in 15% of the empagliflozin group versus 25% in the placebo group (HR 0.58, 95% CI 0.42-0.80, p<0.001).
Conclusion: Empagliflozin significantly reduced cardiovascular outcomes in heart failure patients.""",
        "keywords": ["SGLT2", "heart failure", "empagliflozin", "cardiology"],
        "expected_disciplines": ["Cardiology", "Internal Medicine", "Pharmacology"],
        "expected_article_type": "randomized_controlled_trial",
        "must_include_journals": [
            "European Heart Journal",
            "JACC",
            "Circulation",
        ],
        "should_warn_or_exclude": [],
    },
    {
        "name": "Pediatric_Diabetes_Cohort",
        "title": "Long-term outcomes of pediatric type 1 diabetes: A 20-year cohort study",
        "abstract": """Objective: To assess long-term complications and quality of life in adults diagnosed with type 1 diabetes in childhood.
Design: Prospective cohort study with 20-year follow-up.
Setting: Three tertiary pediatric diabetes centers.
Participants: 450 children diagnosed with T1D between 1995-2000, followed until 2020.
Main outcomes: Diabetic retinopathy, nephropathy, neuropathy, and quality of life scores.
Results: At 20-year follow-up, 35% developed retinopathy, 18% nephropathy, and 22% neuropathy. HbA1c trajectories during adolescence strongly predicted complications.""",
        "keywords": ["type 1 diabetes", "pediatric", "complications", "long-term outcomes"],
        "expected_disciplines": ["Endocrinology", "Pediatrics", "Internal Medicine"],
        "expected_article_type": "cohort_study",
        "must_include_journals": [
            "Diabetes Care",
            "Diabetologia",
            "Pediatric Diabetes",
        ],
        "should_warn_or_exclude": [],
    },
    {
        "name": "Neurology_Case_Report",
        "title": "A rare case of autoimmune encephalitis presenting with isolated psychiatric symptoms",
        "abstract": """We present a case of a 32-year-old woman who presented with acute psychosis and was initially diagnosed with schizophrenia. After failing to respond to antipsychotics, further workup revealed anti-NMDA receptor antibodies. MRI showed subtle temporal lobe changes. The patient was treated with immunotherapy including IVIG and rituximab with significant improvement.
This case highlights the importance of considering autoimmune etiologies in new-onset psychiatric symptoms, especially in young patients.""",
        "keywords": ["autoimmune encephalitis", "anti-NMDA receptor", "psychosis", "case report"],
        "expected_disciplines": ["Neurology", "Psychiatry", "Immunology"],
        "expected_article_type": "case_report",
        "must_include_journals": [
            "Journal of Neurology",
            "BMJ Case Reports",
        ],
        "should_warn_or_exclude": [],
    },
    {
        "name": "Oncology_Meta_Analysis",
        "title": "Immunotherapy versus chemotherapy in advanced non-small cell lung cancer: A meta-analysis",
        "abstract": """Background: Immune checkpoint inhibitors have revolutionized lung cancer treatment. This meta-analysis compares outcomes of immunotherapy versus chemotherapy in advanced NSCLC.
Methods: We searched PubMed, EMBASE, and Cochrane databases for randomized controlled trials. Two reviewers independently extracted data. Random-effects models were used for pooled analyses.
Results: 15 trials with 12,000 patients were included. Immunotherapy showed significant improvement in overall survival (HR 0.75, 95% CI 0.68-0.83). Subgroup analysis showed greater benefit in PD-L1 high expressors.
Conclusions: Immunotherapy provides survival benefit in advanced NSCLC, particularly in PD-L1 positive tumors.""",
        "keywords": ["lung cancer", "immunotherapy", "checkpoint inhibitors", "meta-analysis"],
        "expected_disciplines": ["Oncology", "Pulmonology", "Immunology"],
        "expected_article_type": "meta_analysis",
        "must_include_journals": [
            "Journal of Clinical Oncology",
            "Lancet Oncology",
            "Annals of Oncology",
        ],
        "should_warn_or_exclude": [],
    },
    {
        "name": "Cross_Specialty_Review",
        "title": "Cardiovascular manifestations of COVID-19: A comprehensive narrative review",
        "abstract": """The COVID-19 pandemic has revealed significant cardiovascular complications beyond respiratory disease. This narrative review examines the pathophysiology of cardiac injury in COVID-19, including myocarditis, arrhythmias, and thromboembolic events.
We discuss mechanisms including direct viral injury, cytokine storm, and ACE2-mediated effects. Clinical management strategies and long-term cardiovascular sequelae are reviewed.
Key findings suggest that cardiac involvement occurs in 20-40% of hospitalized patients and is associated with increased mortality.""",
        "keywords": ["COVID-19", "cardiovascular", "myocarditis", "review"],
        "expected_disciplines": ["Cardiology", "Infectious Disease", "Internal Medicine"],
        "expected_article_type": "narrative_review",
        "must_include_journals": [
            "European Heart Journal",
            "Nature Reviews Cardiology",
        ],
        "should_warn_or_exclude": [],
    },
]


class TestMultiDisciplineDetection:
    """Test that multiple disciplines are correctly detected."""

    @pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda x: x["name"])
    def test_primary_discipline_detected(self, test_case):
        """Test that the primary (most relevant) discipline is detected."""
        # This test will be enabled after implementing discipline_detector
        pytest.skip("Discipline detector not yet implemented")

        from app.services.analysis.discipline_detector import MultiDisciplineDetector

        detector = MultiDisciplineDetector()
        result = detector.detect(
            title=test_case["title"],
            abstract=test_case["abstract"],
            keywords=test_case.get("keywords", [])
        )

        # Primary discipline should be in expected list
        assert len(result) > 0, "At least one discipline should be detected"
        primary = result[0]
        assert primary.name in test_case["expected_disciplines"], \
            f"Primary discipline '{primary.name}' not in expected: {test_case['expected_disciplines']}"

    @pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda x: x["name"])
    def test_multiple_disciplines_detected(self, test_case):
        """Test that multiple relevant disciplines are detected."""
        pytest.skip("Discipline detector not yet implemented")

        from app.services.analysis.discipline_detector import MultiDisciplineDetector

        detector = MultiDisciplineDetector()
        result = detector.detect(
            title=test_case["title"],
            abstract=test_case["abstract"],
            keywords=test_case.get("keywords", [])
        )

        detected_names = {d.name for d in result}
        expected = set(test_case["expected_disciplines"])

        # At least 2 expected disciplines should be detected
        overlap = detected_names & expected
        assert len(overlap) >= 2, \
            f"Expected at least 2 disciplines from {expected}, got {detected_names}"


class TestArticleTypeDetection:
    """Test article type detection accuracy."""

    @pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda x: x["name"])
    def test_article_type_detection(self, test_case):
        """Test that article type is correctly detected."""
        pytest.skip("Article type detector not yet implemented")

        from app.services.analysis.article_type_detector import ArticleTypeDetector

        detector = ArticleTypeDetector()
        result = detector.detect(
            abstract=test_case["abstract"],
            title=test_case["title"]
        )

        expected_type = test_case["expected_article_type"]
        # Handle combined types (systematic_review_meta_analysis matches both)
        if expected_type == "systematic_review_meta_analysis":
            valid_types = ["systematic_review_meta_analysis", "systematic_review", "meta_analysis"]
        else:
            valid_types = [expected_type]

        assert result.type_id in valid_types, \
            f"Expected article type '{expected_type}', got '{result.type_id}'"


class TestJournalRanking:
    """Test that expected journals appear in results."""

    @pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda x: x["name"])
    @pytest.mark.asyncio
    async def test_must_include_journals(self, test_case):
        """Test that expected journals appear in top results."""
        pytest.skip("Full integration test - run manually")

        from app.services.openalex.search import search_journals_by_text

        journals, discipline, field, confidence = search_journals_by_text(
            title=test_case["title"],
            abstract=test_case["abstract"],
            keywords=test_case.get("keywords", []),
        )

        journal_names = [j.name.lower() for j in journals[:15]]

        for expected_name in test_case["must_include_journals"]:
            found = any(expected_name.lower() in name for name in journal_names)
            assert found, f"Expected '{expected_name}' in top 15 results"

    @pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda x: x["name"])
    @pytest.mark.asyncio
    async def test_should_warn_or_exclude(self, test_case):
        """Test that irrelevant journals are filtered or warned."""
        if not test_case.get("should_warn_or_exclude"):
            pytest.skip("No journals to exclude for this test case")

        pytest.skip("Topic validator not yet implemented")


class TestTopicRelevanceValidation:
    """Test topic relevance validation."""

    @pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda x: x["name"])
    def test_topic_validation(self, test_case):
        """Test that topic validation correctly identifies relevance."""
        pytest.skip("Topic validator not yet implemented")

        from app.services.analysis.topic_validator import TopicRelevanceValidator

        validator = TopicRelevanceValidator()

        # Create mock journal with topics
        mock_journal = {
            "display_name": "Journal of Clinical Medicine",
            "topics": [
                {"display_name": "COVID-19"},
                {"display_name": "Clinical Research"},
                {"display_name": "General Medicine"},
            ]
        }

        # For OAB/Fibromyalgia test, this journal should have low relevance
        if test_case["name"] == "OAB_Fibromyalgia_Systematic_Review":
            from app.services.analysis.discipline_detector import MultiDisciplineDetector
            detector = MultiDisciplineDetector()
            disciplines = detector.detect(
                title=test_case["title"],
                abstract=test_case["abstract"],
                keywords=test_case.get("keywords", [])
            )

            validation = validator.validate_journal_topics(
                journal=mock_journal,
                detected_disciplines=[{"name": d.name, "evidence": d.evidence} for d in disciplines],
                keywords=test_case.get("keywords", [])
            )

            assert validation["relevance_score"] < 0.3, \
                "Journal of Clinical Medicine should have low relevance for OAB/Fibromyalgia search"


class TestEnhancedScoring:
    """Test enhanced scoring with multi-discipline bonus."""

    def test_cross_discipline_bonus(self):
        """Test that journals covering multiple disciplines get bonus."""
        pytest.skip("Enhanced scoring not yet implemented")

        from app.services.openalex.scoring import EnhancedJournalScorer, ScoringContext

        scorer = EnhancedJournalScorer()

        # Mock journal that covers both urology and gynecology
        mock_journal = {
            "display_name": "International Journal of Gynecology & Obstetrics",
            "topics": [
                {"subfield": {"display_name": "Obstetrics and Gynecology"}},
                {"subfield": {"display_name": "Urology"}},
            ]
        }

        context = ScoringContext(
            detected_disciplines=[
                {"name": "Urology", "openalex_subfield_id": "Urology"},
                {"name": "Gynecology", "openalex_subfield_id": "Obstetrics and Gynecology"},
            ],
            article_type={"type": "systematic_review"},
            keywords=["OAB", "fibromyalgia"],
        )

        score = scorer.score_journal(mock_journal, context, [])

        # Journal should have cross-discipline bonus
        assert score > 50, "Cross-discipline journal should have high score"


# =============================================================================
# Quick Validation Tests (can run without full API access)
# =============================================================================

class TestDisciplineKeywords:
    """Test discipline keyword matching logic."""

    def test_urology_keywords(self):
        """Test urology keyword detection."""
        text = "overactive bladder urinary urgency incontinence"
        urology_keywords = ["bladder", "urinary", "incontinence", "overactive"]

        matches = [kw for kw in urology_keywords if kw in text.lower()]
        assert len(matches) >= 3, f"Should match multiple urology keywords, got {matches}"

    def test_rheumatology_keywords(self):
        """Test rheumatology keyword detection."""
        text = "fibromyalgia chronic pain musculoskeletal"
        rheumatology_keywords = ["fibromyalgia", "chronic pain", "musculoskeletal"]

        matches = [kw for kw in rheumatology_keywords if kw in text.lower()]
        assert len(matches) >= 2, f"Should match rheumatology keywords, got {matches}"

    def test_systematic_review_patterns(self):
        """Test systematic review pattern detection."""
        import re

        text = "A systematic search of four electronic databases was conducted. A meta-analysis was performed."
        patterns = [
            r"systematic review",
            r"systematic search",
            r"meta-analysis",
            r"electronic databases",
        ]

        matches = [p for p in patterns if re.search(p, text, re.IGNORECASE)]
        assert len(matches) >= 3, f"Should match SR/MA patterns, got {matches}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
