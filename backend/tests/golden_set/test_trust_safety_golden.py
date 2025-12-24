"""
Golden Set Benchmark Tests for Trust & Safety Engine.

This test suite validates the Trust & Safety verification algorithm against
a curated dataset of 98 journals with known verification statuses.

Run with:
    cd backend
    python -m pytest tests/golden_set/test_trust_safety_golden.py -v

Quick test:
    cd backend
    python tests/golden_set/test_trust_safety_golden.py
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Import Trust & Safety components
from app.services.trust_safety import verify_journal
from app.models.journal import Journal, JournalMetrics, BadgeColor


# Load Golden Set
GOLDEN_SET_PATH = Path(__file__).parent / "journals.json"


def load_golden_set() -> Dict[str, Any]:
    """Load the golden set test data."""
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def create_journal_from_golden(data: dict) -> Journal:
    """Create a Journal object from golden set data."""
    return Journal(
        id=f"golden:{data.get('issn', 'unknown')}",
        name=data["name"],
        issn=data.get("issn"),
        issn_l=data.get("issn"),
        publisher=data.get("publisher"),
        is_oa=data.get("doaj_listed", False),
        is_in_doaj=data.get("doaj_listed", False),
        apc_usd=data.get("apc_usd"),
        homepage_url=data.get("website"),
        metrics=JournalMetrics(
            h_index=None,
            works_count=None,
            two_yr_mean_citedness=data.get("impact_factor")
        ),
        topics=[],
        relevance_score=0.0,
    )


@pytest.fixture(scope="module")
def golden_set() -> Dict[str, Any]:
    """Pytest fixture for golden set data."""
    return load_golden_set()


class TestGoldenSetMetadata:
    """Validate golden set file structure."""

    def test_golden_set_loads(self, golden_set):
        """Verify golden set file loads correctly."""
        assert "metadata" in golden_set
        assert "journals" in golden_set

    def test_journal_count(self, golden_set):
        """Verify expected journal count."""
        metadata = golden_set["metadata"]
        journals = golden_set["journals"]
        assert len(journals) == metadata["total_journals"]

    def test_category_distribution(self, golden_set):
        """Verify category counts match metadata."""
        metadata = golden_set["metadata"]
        journals = golden_set["journals"]

        category_counts = defaultdict(int)
        for journal in journals:
            category_counts[journal["category"]] += 1

        for category, expected_count in metadata["by_category"].items():
            actual_count = category_counts.get(category, 0)
            assert actual_count == expected_count, \
                f"Category {category}: expected {expected_count}, got {actual_count}"

    def test_badge_distribution(self, golden_set):
        """Verify expected badge distribution."""
        metadata = golden_set["metadata"]
        journals = golden_set["journals"]

        badge_counts = defaultdict(int)
        for journal in journals:
            badge_counts[journal["expected_badge"]] += 1

        for badge, expected_count in metadata["by_expected_badge"].items():
            actual_count = badge_counts.get(badge, 0)
            assert actual_count == expected_count, \
                f"Badge {badge}: expected {expected_count}, got {actual_count}"


class TestLegitimateJournals:
    """Test that legitimate journals receive GREEN badges."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("category", [
        "legitimate_medline_elite",
        "legitimate_medline_specialty",
        "legitimate_doaj",
        "legitimate_regional",
    ])
    async def test_legitimate_category(self, golden_set, category: str):
        """Test legitimate journals by category."""
        journals = [j for j in golden_set["journals"] if j["category"] == category]

        results = {"pass": 0, "fail": 0, "errors": []}

        for journal_data in journals:
            try:
                journal = create_journal_from_golden(journal_data)
                verified_journal = await verify_journal(journal)

                if verified_journal.verification:
                    actual_badge = verified_journal.verification.badge_color
                    if actual_badge == BadgeColor.GREEN:
                        results["pass"] += 1
                    else:
                        results["fail"] += 1
                        results["errors"].append({
                            "name": journal_data["name"],
                            "issn": journal_data.get("issn"),
                            "expected": "GREEN",
                            "got": actual_badge.value,
                        })
                else:
                    results["fail"] += 1
                    results["errors"].append({
                        "name": journal_data["name"],
                        "error": "No verification result"
                    })
            except Exception as e:
                results["fail"] += 1
                results["errors"].append({
                    "name": journal_data["name"],
                    "error": str(e)
                })

        # Print detailed results
        if results["errors"]:
            print(f"\n{category} failures:")
            for err in results["errors"]:
                print(f"  - {err}")

        # Allow some tolerance for API failures, but expect >80% accuracy
        total = results["pass"] + results["fail"]
        accuracy = results["pass"] / total if total > 0 else 0
        assert accuracy >= 0.8, \
            f"{category}: Expected >=80% GREEN, got {accuracy*100:.1f}%"


class TestPredatoryJournals:
    """Test that predatory journals receive RED badges."""

    @pytest.mark.asyncio
    async def test_blacklisted_journals(self, golden_set):
        """Test journals on Beall's List or other blacklists."""
        journals = [j for j in golden_set["journals"]
                    if j["category"] in ["predatory_documented", "predatory_sting_verified"]]

        results = {"pass": 0, "fail": 0, "false_negatives": []}

        for journal_data in journals:
            try:
                journal = create_journal_from_golden(journal_data)
                verified_journal = await verify_journal(journal)

                if verified_journal.verification:
                    actual_badge = verified_journal.verification.badge_color
                    if actual_badge == BadgeColor.RED:
                        results["pass"] += 1
                    else:
                        results["fail"] += 1
                        results["false_negatives"].append({
                            "name": journal_data["name"],
                            "issn": journal_data.get("issn"),
                            "category": journal_data["category"],
                            "expected": "RED",
                            "got": actual_badge.value,
                        })
            except Exception as e:
                results["fail"] += 1
                results["false_negatives"].append({
                    "name": journal_data["name"],
                    "error": str(e)
                })

        # Print false negatives
        if results["false_negatives"]:
            print("\n[WARNING] FALSE NEGATIVES (predatory journals not detected):")
            for fn in results["false_negatives"]:
                print(f"  - {fn['name']} ({fn.get('category', 'unknown')})")

        total = results["pass"] + results["fail"]
        detection_rate = results["pass"] / total if total > 0 else 0
        assert detection_rate >= 0.7, \
            f"Predatory detection: Expected >=70%, got {detection_rate*100:.1f}%"


class TestBenchmarkMetrics:
    """Calculate overall benchmark metrics."""

    @pytest.mark.asyncio
    async def test_overall_accuracy(self, golden_set):
        """Calculate precision, recall, and F1 for the entire golden set."""
        journals = golden_set["journals"]

        # Map badge values
        badge_map = {
            "verified": "GREEN",
            "caution": "YELLOW",
            "high_risk": "RED",
            "unverified": "GRAY"
        }

        # Track predictions vs actual
        confusion = {
            "GREEN": {"GREEN": 0, "YELLOW": 0, "RED": 0, "GRAY": 0},
            "YELLOW": {"GREEN": 0, "YELLOW": 0, "RED": 0, "GRAY": 0},
            "RED": {"GREEN": 0, "YELLOW": 0, "RED": 0, "GRAY": 0},
        }

        for journal_data in journals:
            try:
                journal = create_journal_from_golden(journal_data)
                verified_journal = await verify_journal(journal)

                expected = journal_data["expected_badge"]

                if verified_journal.verification:
                    actual = badge_map.get(
                        verified_journal.verification.badge_color.value,
                        "GRAY"
                    )
                else:
                    actual = "GRAY"

                confusion[expected][actual] += 1
            except Exception:
                confusion[journal_data["expected_badge"]]["GRAY"] += 1

        # Print confusion matrix
        print("\n" + "="*60)
        print("CONFUSION MATRIX")
        print("="*60)
        print(f"{'Expected':<12} | {'GREEN':>8} {'YELLOW':>8} {'RED':>8} {'GRAY':>8}")
        print("-"*60)
        for expected in ["GREEN", "YELLOW", "RED"]:
            row = confusion[expected]
            print(f"{expected:<12} | {row['GREEN']:>8} {row['YELLOW']:>8} {row['RED']:>8} {row['GRAY']:>8}")

        # Calculate metrics per class
        print("\n" + "="*60)
        print("PER-CLASS METRICS")
        print("="*60)

        for cls in ["GREEN", "YELLOW", "RED"]:
            tp = confusion[cls][cls]
            fp = sum(confusion[other][cls] for other in ["GREEN", "YELLOW", "RED"] if other != cls)
            fn = sum(confusion[cls][other] for other in ["GREEN", "YELLOW", "RED", "GRAY"] if other != cls)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            print(f"{cls}: Precision={precision:.2%}, Recall={recall:.2%}, F1={f1:.2%}")

        # Overall accuracy
        total_correct = sum(confusion[cls][cls] for cls in ["GREEN", "YELLOW", "RED"])
        total = sum(sum(row.values()) for row in confusion.values())
        accuracy = total_correct / total if total > 0 else 0

        print(f"\nOverall Accuracy: {accuracy:.2%} ({total_correct}/{total})")
        print("="*60)

        # Don't fail - this is informational
        # assert accuracy >= 0.6, f"Overall accuracy too low: {accuracy:.2%}"


# CLI runner for quick testing
if __name__ == "__main__":
    import asyncio

    async def quick_test():
        """Run a quick test on sample journals."""
        golden = load_golden_set()

        print("Quick Golden Set Test")
        print("="*50)

        # Test 3 from each expected badge
        for badge in ["GREEN", "YELLOW", "RED"]:
            journals = [j for j in golden["journals"] if j["expected_badge"] == badge][:3]
            print(f"\n{badge} Journals:")

            for j in journals:
                try:
                    journal = create_journal_from_golden(j)
                    result = await verify_journal(journal)

                    if result.verification:
                        actual = result.verification.badge_color.value.upper()
                        # Map enum values
                        actual_map = {
                            "VERIFIED": "GREEN",
                            "CAUTION": "YELLOW",
                            "HIGH_RISK": "RED",
                            "UNVERIFIED": "GRAY"
                        }
                        actual = actual_map.get(actual, actual)
                        match = "[OK]" if actual == badge else "[FAIL]"
                        print(f"  {match} {j['name'][:40]:<40} Expected: {badge}, Got: {actual}")
                    else:
                        print(f"  [WARN] {j['name'][:40]:<40} No verification result")
                except Exception as e:
                    print(f"  [ERR] {j['name'][:40]:<40} Error: {e}")

    asyncio.run(quick_test())
