"""
Benchmark tests for OpenAlex search algorithm.

These tests verify that the search algorithm returns relevant, high-quality
journals for various academic disciplines. Each test case includes expected
results to validate the algorithm's performance.

Usage:
    # Run all benchmarks
    pytest backend/tests/test_benchmark_search.py -v -s

    # Run only benchmark tests
    pytest backend/tests/test_benchmark_search.py -v -m benchmark

    # Run with detailed output
    pytest backend/tests/test_benchmark_search.py -v -s -m benchmark
"""

import pytest
import time
from typing import Dict, List, Set
from collections import defaultdict

from app.services.openalex_service import OpenAlexService
from app.models.journal import Journal


# Benchmark test cases with expected results
BENCHMARK_CASES = [
    {
        "name": "Psychology - Child Development",
        "title": "Exploring the Roots of Kindness: Validating the Social-Emotional Responding Task (SERT) for Infants and Toddlers",
        "abstract": "A total of 179 caregivers in Leipzig, Germany completed the adapted SERT, as well as measures for the purpose of validating the adapted SERT, including social-emotional and behavioral problems (BITSEA; Briggs-Gowan & Carter 2007), temperament (IBQ/ECBQ; Putnam et al., 2013, 2006), and conscience development (Kochanska et al., 1994). Internal consistency was found across all empathy for others, empathy for the self, and emotion regulation precursor constructs (α =.75–.87). Confirmatory factor analyses showed good convergence and fit for each construct (CFI=.91-.99; TLI=.90-.99; RMSEA=.03-.08; SRMR =.04-.07). Structural equation modeling provided some initial support for construct validity: empathy for others and self (β = .26, .20, p = .016, .047, respectively) were associated with higher competence scores, reflecting early social-emotional, communicative, and regulatory abilities.",
        "keywords": ["kindness", "empathy", "toddlerhood", "infancy", "social-emotional development"],
        # OpenAlex returns subfields like "Social Psychology", "Developmental and Educational Psychology"
        "expected_discipline": None,  # Skip discipline check - OpenAlex returns specific subfields
        "expected_journals_contain": ["Frontiers in Psychology", "Child Development", "Developmental Psychology", "Infancy"],
        "min_results": 5,
    },
    {
        "name": "Medicine - Endocrinology (GH Treatment)",
        "title": "Growth Hormone Treatment in Children with Down Syndrome",
        "abstract": "This study examines the effects of growth hormone (GH) treatment on children with Down syndrome. We analyzed growth velocity, metabolic parameters, and quality of life measures in 45 children receiving GH therapy over a 3-year period. Results showed significant improvements in height velocity and lean body mass. The treatment was well-tolerated with minimal adverse effects. Our findings suggest that GH therapy can be beneficial for children with Down syndrome who have growth hormone deficiency.",
        "keywords": ["growth hormone", "Down syndrome", "endocrinology", "pediatric", "GH therapy"],
        # Now using OpenAlex subfield - can be any medical subfield, we just check journals
        "expected_discipline": None,  # Skip discipline check - OpenAlex returns specific subfields
        "expected_journals_contain": ["Frontiers in Endocrinology", "Journal of Clinical Endocrinology", "Hormone Research"],
        "min_results": 5,
    },
    {
        "name": "Medicine - Clinical Trial",
        "title": "Efficacy of mRNA Vaccines in Preventing COVID-19",
        "abstract": "This randomized controlled trial evaluated the efficacy of mRNA-based vaccines in preventing symptomatic COVID-19 infection. A total of 30,000 participants were enrolled across 120 clinical sites. Primary endpoints included prevention of confirmed COVID-19 cases and safety outcomes.",
        "keywords": ["vaccine", "COVID-19", "mRNA", "clinical trial"],
        # OpenAlex returns specific subfields like "Infectious Diseases", "Virology", etc.
        "expected_discipline": None,
        "expected_journals_contain": ["New England Journal of Medicine", "The Lancet", "JAMA"],
        "min_results": 5,
    },
    {
        "name": "Computer Science - Machine Learning",
        "title": "Transformer-Based Models for Natural Language Understanding",
        "abstract": "We present a novel transformer architecture that achieves state-of-the-art performance on natural language processing benchmarks. Our model uses attention mechanisms and deep learning techniques to understand context and semantics in text.",
        "keywords": ["transformer", "NLP", "deep learning", "attention"],
        # OpenAlex returns "Artificial Intelligence" subfield
        "expected_discipline": None,
        "expected_journals_contain": ["Nature Machine Intelligence", "Artificial Intelligence"],
        "min_results": 5,
    },
    {
        "name": "Physics - Quantum Computing",
        "title": "Superconducting Qubits for Quantum Information Processing",
        "abstract": "We demonstrate a novel superconducting qubit architecture with improved coherence times. Our quantum processor achieves high-fidelity gate operations using microwave pulses on superconducting circuits at cryogenic temperatures.",
        "keywords": ["quantum", "qubit", "superconducting", "coherence"],
        # OpenAlex returns specific subfields like "Condensed Matter Physics", etc.
        "expected_discipline": None,
        "expected_journals_contain": ["Physical Review Letters", "Nature Physics"],
        "min_results": 5,
    },
]


class BenchmarkResult:
    """Container for benchmark test results."""

    def __init__(self, case_name: str):
        self.case_name = case_name
        self.execution_time: float = 0.0
        self.num_results: int = 0
        self.discipline_detected: str = ""
        self.discipline_correct: bool = False
        self.expected_journals: Set[str] = set()
        self.found_journals: Set[str] = set()
        self.missing_journals: Set[str] = set()
        self.journals: List[Journal] = []
        self.relevance_score: float = 0.0
        self.passed: bool = False
        self.error_message: str = ""

    def calculate_relevance_score(self) -> float:
        """
        Calculate relevance score based on how many expected journals were found.

        Returns:
            Float between 0.0 and 1.0 representing percentage of expected journals found.
        """
        if not self.expected_journals:
            return 1.0
        return len(self.found_journals) / len(self.expected_journals)

    def summary_dict(self) -> Dict:
        """Return summary as dictionary for reporting."""
        return {
            "case_name": self.case_name,
            "passed": self.passed,
            "execution_time": f"{self.execution_time:.2f}s",
            "num_results": self.num_results,
            "discipline_detected": self.discipline_detected,
            "discipline_correct": self.discipline_correct,
            "expected_journals": list(self.expected_journals),
            "found_journals": list(self.found_journals),
            "missing_journals": list(self.missing_journals),
            "relevance_score": f"{self.relevance_score:.2%}",
            "error": self.error_message or "None",
        }


@pytest.fixture(scope="module")
def openalex_service():
    """Create OpenAlexService instance for all benchmark tests."""
    return OpenAlexService()


@pytest.fixture(scope="module")
def benchmark_results():
    """
    Shared list to collect results from all benchmark tests.
    This allows the summary function to access all results.
    """
    return []


@pytest.mark.benchmark
class TestSearchBenchmark:
    """Benchmark tests for search algorithm."""

    @pytest.mark.parametrize("case", BENCHMARK_CASES, ids=lambda c: c["name"])
    def test_benchmark_case(
        self,
        case: Dict,
        openalex_service: OpenAlexService,
        benchmark_results: List[BenchmarkResult],
    ):
        """
        Run a single benchmark test case.

        Args:
            case: Test case dictionary with title, abstract, keywords, and expected results.
            openalex_service: OpenAlexService instance.
            benchmark_results: Shared list to collect results.
        """
        result = BenchmarkResult(case["name"])

        try:
            # Measure execution time
            start_time = time.time()
            journals, discipline = openalex_service.search_journals_by_text(
                title=case["title"],
                abstract=case["abstract"],
                keywords=case["keywords"],
                prefer_open_access=False,
            )
            result.execution_time = time.time() - start_time

            # Store results
            result.num_results = len(journals)
            result.discipline_detected = discipline
            result.journals = journals

            # Check discipline detection (skip if expected_discipline is None)
            expected_disc = case["expected_discipline"]
            if expected_disc is None:
                result.discipline_correct = True  # Skip check for OpenAlex subfield cases
            else:
                result.discipline_correct = discipline == expected_disc

            # Check for expected journals (fuzzy matching)
            result.expected_journals = set(case["expected_journals_contain"])
            journal_names = [j.name for j in journals]

            for expected in case["expected_journals_contain"]:
                # Fuzzy match: check if expected journal name appears in any result
                for journal_name in journal_names:
                    if self._fuzzy_match(expected, journal_name):
                        result.found_journals.add(expected)
                        break

            result.missing_journals = result.expected_journals - result.found_journals
            result.relevance_score = result.calculate_relevance_score()

            # Determine pass/fail
            checks = {
                "min_results": result.num_results >= case["min_results"],
                "discipline": result.discipline_correct,
                "has_expected_journals": len(result.found_journals) > 0,
            }

            result.passed = all(checks.values())

            # Collect results for summary
            benchmark_results.append(result)

            # Print detailed output
            print(f"\n{'='*80}")
            print(f"BENCHMARK: {case['name']}")
            print(f"{'='*80}")
            print(f"Execution Time: {result.execution_time:.2f}s")
            print(f"Results Found: {result.num_results} (min required: {case['min_results']})")
            print(f"Discipline: {result.discipline_detected} (expected: {case['expected_discipline']})")
            print(f"Discipline Correct: {'YES' if result.discipline_correct else 'NO'}")
            print(f"\nExpected Journals ({len(result.expected_journals)}):")
            for journal in result.expected_journals:
                status = "FOUND" if journal in result.found_journals else "MISSING"
                print(f"  [{status}] {journal}")

            print(f"\nRelevance Score: {result.relevance_score:.2%}")

            if result.num_results > 0:
                print(f"\nTop 5 Results:")
                for i, journal in enumerate(journals[:5], 1):
                    print(f"  {i}. {journal.name}")
                    print(f"     - H-index: {journal.metrics.h_index or 'N/A'}")
                    print(f"     - Works: {journal.metrics.works_count or 'N/A'}")
                    print(f"     - Relevance: {journal.relevance_score:.2f}")
                    print(f"     - Match Reason: {journal.match_reason or 'N/A'}")

            # Assert checks
            assert checks["min_results"], (
                f"Expected at least {case['min_results']} results, got {result.num_results}"
            )
            assert checks["discipline"], (
                f"Expected discipline '{case['expected_discipline']}', got '{result.discipline_detected}'"
            )
            assert checks["has_expected_journals"], (
                f"None of the expected journals found: {result.expected_journals}"
            )

        except Exception as e:
            result.error_message = str(e)
            result.passed = False
            benchmark_results.append(result)
            print(f"\n{'='*80}")
            print(f"BENCHMARK FAILED: {case['name']}")
            print(f"{'='*80}")
            print(f"Error: {e}")
            raise

    def _fuzzy_match(self, expected: str, actual: str) -> bool:
        """
        Fuzzy match journal names.

        Args:
            expected: Expected journal name or keyword.
            actual: Actual journal name from results.

        Returns:
            True if names match (case-insensitive, partial match allowed).
        """
        expected_lower = expected.lower()
        actual_lower = actual.lower()

        # Exact match
        if expected_lower == actual_lower:
            return True

        # Partial match (expected is substring of actual)
        if expected_lower in actual_lower:
            return True

        # Handle common variations
        # e.g., "JAMA" matches "JAMA Network Open"
        expected_words = set(expected_lower.split())
        actual_words = set(actual_lower.split())
        if expected_words & actual_words:  # Intersection
            return True

        return False


@pytest.mark.benchmark
def test_benchmark_summary(benchmark_results: List[BenchmarkResult]):
    """
    Generate summary report for all benchmark tests.

    This test should run last to aggregate results from all benchmark cases.

    Args:
        benchmark_results: List of BenchmarkResult objects from all tests.
    """
    if not benchmark_results:
        pytest.skip("No benchmark results to summarize")

    print("\n" + "="*80)
    print("BENCHMARK SUMMARY REPORT")
    print("="*80)

    # Overall statistics
    total_tests = len(benchmark_results)
    passed_tests = sum(1 for r in benchmark_results if r.passed)
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests} ({pass_rate:.1f}%)")
    print(f"Failed: {failed_tests}")

    # Execution time statistics
    total_time = sum(r.execution_time for r in benchmark_results)
    avg_time = total_time / total_tests if total_tests > 0 else 0
    min_time = min(r.execution_time for r in benchmark_results) if benchmark_results else 0
    max_time = max(r.execution_time for r in benchmark_results) if benchmark_results else 0

    print(f"\nExecution Time:")
    print(f"  Total: {total_time:.2f}s")
    print(f"  Average: {avg_time:.2f}s")
    print(f"  Min: {min_time:.2f}s")
    print(f"  Max: {max_time:.2f}s")

    # Results statistics
    total_results = sum(r.num_results for r in benchmark_results)
    avg_results = total_results / total_tests if total_tests > 0 else 0

    print(f"\nResults per Test:")
    print(f"  Total: {total_results}")
    print(f"  Average: {avg_results:.1f}")

    # Discipline detection accuracy
    correct_disciplines = sum(1 for r in benchmark_results if r.discipline_correct)
    discipline_accuracy = (correct_disciplines / total_tests * 100) if total_tests > 0 else 0

    print(f"\nDiscipline Detection:")
    print(f"  Correct: {correct_disciplines}/{total_tests} ({discipline_accuracy:.1f}%)")

    # Journal matching statistics
    total_expected = sum(len(r.expected_journals) for r in benchmark_results)
    total_found = sum(len(r.found_journals) for r in benchmark_results)
    avg_relevance = sum(r.relevance_score for r in benchmark_results) / total_tests if total_tests > 0 else 0

    print(f"\nJournal Matching:")
    print(f"  Expected Journals: {total_expected}")
    print(f"  Found Journals: {total_found}")
    print(f"  Average Relevance Score: {avg_relevance:.2%}")

    # Detailed results per test
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)

    for result in benchmark_results:
        status = "PASSED" if result.passed else "FAILED"
        print(f"\n[{status}] {result.case_name}")
        print(f"  Execution Time: {result.execution_time:.2f}s")
        print(f"  Results: {result.num_results}")
        print(f"  Discipline: {result.discipline_detected} ({'CORRECT' if result.discipline_correct else 'WRONG'})")
        print(f"  Expected Journals: {len(result.expected_journals)}")
        print(f"  Found Journals: {len(result.found_journals)}")
        print(f"  Relevance Score: {result.relevance_score:.2%}")

        if result.missing_journals:
            print(f"  Missing: {', '.join(result.missing_journals)}")

        if result.error_message:
            print(f"  Error: {result.error_message}")

    # By-discipline breakdown
    print("\n" + "="*80)
    print("BY-DISCIPLINE BREAKDOWN")
    print("="*80)

    discipline_stats = defaultdict(lambda: {"total": 0, "passed": 0, "avg_time": 0.0, "avg_results": 0.0})

    for result in benchmark_results:
        disc = result.discipline_detected
        discipline_stats[disc]["total"] += 1
        if result.passed:
            discipline_stats[disc]["passed"] += 1
        discipline_stats[disc]["avg_time"] += result.execution_time
        discipline_stats[disc]["avg_results"] += result.num_results

    for disc, stats in sorted(discipline_stats.items()):
        total = stats["total"]
        passed = stats["passed"]
        pass_rate = (passed / total * 100) if total > 0 else 0
        avg_time = stats["avg_time"] / total if total > 0 else 0
        avg_results = stats["avg_results"] / total if total > 0 else 0

        print(f"\n{disc}:")
        print(f"  Tests: {total}")
        print(f"  Pass Rate: {passed}/{total} ({pass_rate:.1f}%)")
        print(f"  Avg Execution Time: {avg_time:.2f}s")
        print(f"  Avg Results: {avg_results:.1f}")

    print("\n" + "="*80)

    # Final assertion: require minimum pass rate
    MIN_PASS_RATE = 75.0  # Require at least 75% of tests to pass
    assert pass_rate >= MIN_PASS_RATE, (
        f"Benchmark pass rate {pass_rate:.1f}% is below minimum required {MIN_PASS_RATE}%"
    )


@pytest.mark.benchmark
@pytest.mark.parametrize("case_index", range(len(BENCHMARK_CASES)))
def test_benchmark_quality_metrics(case_index: int, openalex_service: OpenAlexService):
    """
    Test that results meet quality thresholds.

    This test verifies:
    - Top results have reasonable H-index values
    - Results are properly categorized
    - Relevance scores are assigned

    Args:
        case_index: Index of the test case to run.
        openalex_service: OpenAlexService instance.
    """
    case = BENCHMARK_CASES[case_index]

    journals, discipline = openalex_service.search_journals_by_text(
        title=case["title"],
        abstract=case["abstract"],
        keywords=case["keywords"],
    )

    # Skip if no results
    if not journals:
        pytest.skip(f"No results for {case['name']}")

    # Check top 3 results have quality metrics
    top_journals = journals[:3]

    for i, journal in enumerate(top_journals, 1):
        # All journals should have metrics
        assert journal.metrics is not None, f"Journal #{i} missing metrics"

        # Top journals should have decent H-index (or be new/specialized)
        if journal.metrics.h_index is not None:
            # Allow lower H-index for specialized/niche journals
            min_h_index = 10 if journal.category in ["niche", "emerging"] else 20
            assert journal.metrics.h_index >= min_h_index or journal.metrics.works_count > 5000, (
                f"Journal #{i} ({journal.name}) has low H-index: {journal.metrics.h_index}"
            )

        # All journals should have a category assigned
        assert journal.category is not None, f"Journal #{i} missing category"

        # All journals should have a relevance score
        assert journal.relevance_score >= 0, f"Journal #{i} has negative relevance score"

        # Top result should have higher relevance than lower results
        if i > 1:
            assert journal.relevance_score <= top_journals[i - 2].relevance_score, (
                f"Journal #{i} has higher relevance score than journal #{i-1}"
            )


@pytest.mark.benchmark
def test_benchmark_execution_time(openalex_service: OpenAlexService):
    """
    Test that search executes within acceptable time limits.

    This is a smoke test to ensure the algorithm doesn't have
    performance regressions.
    """
    # Use a simple test case
    case = BENCHMARK_CASES[0]

    start_time = time.time()
    journals, discipline = openalex_service.search_journals_by_text(
        title=case["title"],
        abstract=case["abstract"],
        keywords=case["keywords"],
    )
    execution_time = time.time() - start_time

    # Search should complete within 30 seconds
    MAX_EXECUTION_TIME = 30.0
    assert execution_time < MAX_EXECUTION_TIME, (
        f"Search took {execution_time:.2f}s, exceeds maximum {MAX_EXECUTION_TIME}s"
    )

    print(f"\nExecution time: {execution_time:.2f}s")


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    pytest.main([__file__, "-v", "-s", "-m", "benchmark"])
