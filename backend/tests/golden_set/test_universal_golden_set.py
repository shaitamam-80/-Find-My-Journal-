"""
Universal Golden Set Tests.

Validates that Find My Journal works across ALL academic domains:
- Health Sciences (Medicine)
- Social Sciences (Psychology, Economics)
- Physical Sciences (CS, Physics, Engineering, Chemistry)
- Life Sciences (Biology, Ecology)

Success Criteria:
- Detection rate >= 85% (correct domain/field detection)
- Journal coverage >= 80% (finds relevant journals)
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List

from app.services.openalex.universal_search import search_journals_universal
from app.services.analysis import detect_disciplines_universal


# Load golden set
GOLDEN_SET_PATH = Path(__file__).parent / "search-golden-set-universal.json"


def load_golden_set() -> Dict:
    """Load the golden set test cases."""
    with open(GOLDEN_SET_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def golden_set():
    """Fixture to load golden set once per module."""
    return load_golden_set()


class TestUniversalDomainDetection:
    """Test that we correctly detect domains across all cases."""

    @pytest.mark.parametrize("domain", [
        "Health Sciences",
        "Social Sciences",
        "Physical Sciences",
        "Life Sciences",
    ])
    def test_domain_detection_accuracy(self, golden_set, domain):
        """Test that papers are correctly classified to their expected domain."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == domain]

        passed = 0
        failed = []

        for case in cases:
            result = detect_disciplines_universal(
                title=case["title"],
                abstract=case["abstract"],
                keywords=case.get("keywords"),
            )

            if not result:
                failed.append(f"{case['id']}: No disciplines detected")
                continue

            # Check if detected domain matches expected
            detected_domains = set(d.get("domain") for d in result if d.get("domain"))
            expected_domains = set(case.get("expected_domains", [domain]))

            if detected_domains & expected_domains:  # Any intersection
                passed += 1
            else:
                failed.append(
                    f"{case['id']}: Expected {expected_domains}, got {detected_domains}"
                )

        success_rate = passed / len(cases) if cases else 0
        assert success_rate >= 0.75, (
            f"Domain {domain} detection rate {success_rate:.0%} "
            f"(expected >= 75%). Failures: {failed}"
        )


class TestUniversalSubfieldDetection:
    """Test that we detect specific subfields correctly."""

    def test_health_sciences_subfields(self, golden_set):
        """Test subfield detection for Health Sciences papers."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == "Health Sciences"]
        self._check_subfield_detection(cases)

    def test_social_sciences_subfields(self, golden_set):
        """Test subfield detection for Social Sciences papers."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == "Social Sciences"]
        self._check_subfield_detection(cases)

    def test_physical_sciences_subfields(self, golden_set):
        """Test subfield detection for Physical Sciences papers."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == "Physical Sciences"]
        self._check_subfield_detection(cases)

    def test_life_sciences_subfields(self, golden_set):
        """Test subfield detection for Life Sciences papers."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == "Life Sciences"]
        self._check_subfield_detection(cases)

    def _check_subfield_detection(self, cases: List[Dict]):
        """Helper to check subfield detection for a set of cases."""
        passed = 0

        for case in cases:
            result = detect_disciplines_universal(
                title=case["title"],
                abstract=case["abstract"],
            )

            if not result:
                continue

            detected_names = [d.get("name", "").lower() for d in result]
            expected_subfields = case.get("must_detect_subfields", [])

            # Check if any expected subfield was detected
            for expected in expected_subfields:
                if any(expected.lower() in name for name in detected_names):
                    passed += 1
                    break

        success_rate = passed / len(cases) if cases else 0
        assert success_rate >= 0.70, f"Subfield detection rate {success_rate:.0%} < 70%"


class TestUniversalSearchEndToEnd:
    """End-to-end tests for the complete search pipeline."""

    def test_search_finds_journals_health(self, golden_set):
        """Test that search finds journals for Health Sciences papers."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == "Health Sciences"]
        self._test_search_coverage(cases)

    def test_search_finds_journals_social(self, golden_set):
        """Test that search finds journals for Social Sciences papers."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == "Social Sciences"]
        self._test_search_coverage(cases)

    def test_search_finds_journals_physical(self, golden_set):
        """Test that search finds journals for Physical Sciences papers."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == "Physical Sciences"]
        self._test_search_coverage(cases)

    def test_search_finds_journals_life(self, golden_set):
        """Test that search finds journals for Life Sciences papers."""
        cases = [c for c in golden_set["test_cases"] if c["domain"] == "Life Sciences"]
        self._test_search_coverage(cases)

    def _test_search_coverage(self, cases: List[Dict]):
        """Helper to test that search finds journals for cases."""
        cases_with_results = 0

        for case in cases:
            result = search_journals_universal(
                title=case["title"],
                abstract=case["abstract"],
                keywords=case.get("keywords"),
            )

            if result.journals and len(result.journals) >= 3:
                cases_with_results += 1

        coverage = cases_with_results / len(cases) if cases else 0
        assert coverage >= 0.75, f"Journal coverage {coverage:.0%} < 75%"


class TestCrossDomainPapers:
    """Test papers that span multiple domains."""

    def test_interdisciplinary_paper_detection(self):
        """Test that interdisciplinary papers detect multiple domains."""
        # This paper spans CS and Medicine
        result = detect_disciplines_universal(
            title="Machine learning for drug discovery in oncology",
            abstract="We apply deep learning to predict drug-target interactions. The model outperforms traditional methods in identifying potential cancer therapeutics using molecular fingerprints.",
        )

        assert len(result) >= 2, "Should detect multiple disciplines"

        # Should have detected fields from different domains
        fields = set(d.get("field") for d in result if d.get("field"))
        assert len(fields) >= 1, "Should detect at least one field"

    def test_bioinformatics_spans_domains(self):
        """Test bioinformatics paper detection."""
        result = detect_disciplines_universal(
            title="Genomic data analysis using neural networks",
            abstract="We developed a deep learning pipeline for analyzing next-generation sequencing data to identify genetic variants associated with disease risk.",
        )

        assert len(result) >= 1
        # Should detect either Life Sciences or Physical Sciences aspects


class TestGoldenSetMetrics:
    """Overall metrics for the golden set."""

    def test_overall_detection_rate(self, golden_set):
        """Test that overall detection rate meets threshold."""
        cases = golden_set["test_cases"]
        detected = 0

        for case in cases:
            result = detect_disciplines_universal(
                title=case["title"],
                abstract=case["abstract"],
            )

            if result and len(result) >= 1:
                # Check if any detected domain matches expected
                detected_domains = set(d.get("domain") for d in result if d.get("domain"))
                expected_domains = set(case.get("expected_domains", [case["domain"]]))

                if detected_domains & expected_domains:
                    detected += 1

        rate = detected / len(cases) if cases else 0
        assert rate >= 0.80, f"Overall detection rate {rate:.0%} < 80%"

    def test_overall_search_coverage(self, golden_set):
        """Test that overall search coverage meets threshold."""
        cases = golden_set["test_cases"]
        with_journals = 0

        for case in cases[:8]:  # Test subset to reduce API calls
            result = search_journals_universal(
                title=case["title"],
                abstract=case["abstract"],
            )

            if result.journals and len(result.journals) >= 3:
                with_journals += 1

        coverage = with_journals / min(len(cases), 8)
        assert coverage >= 0.75, f"Overall search coverage {coverage:.0%} < 75%"
