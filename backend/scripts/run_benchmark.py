#!/usr/bin/env python
"""
Benchmark script for evaluating OpenAlexService journal recommendations.

This script tests the journal recommendation algorithm against a ground truth
dataset to measure accuracy at different ranking positions (Hit@1, Hit@5, Hit@10).

Usage:
    cd backend
    python scripts/run_benchmark.py
"""

import json
import sys
import time
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.openalex_service import openalex_service


@dataclass
class BenchmarkResult:
    """Result for a single benchmark test case."""
    test_case: dict
    returned_journals: List[str]
    position: int  # -1 if not found
    match_type: str  # "exact", "fuzzy", or "miss"
    matched_name: str = ""


@dataclass
class BenchmarkSummary:
    """Summary statistics for benchmark run."""
    total: int = 0
    hit_at_1: int = 0
    hit_at_5: int = 0
    hit_at_10: int = 0
    hit_at_15: int = 0
    misses: int = 0

    # By type
    standard_total: int = 0
    standard_hits: int = 0
    edge_total: int = 0
    edge_hits: int = 0

    results: List[BenchmarkResult] = field(default_factory=list)


def normalize_journal_name(name: str) -> str:
    """Normalize journal name for comparison."""
    # Lowercase
    name = name.lower()
    # Remove common prefixes/suffixes
    prefixes = ["the ", "a "]
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    # Remove punctuation and extra spaces
    name = "".join(c if c.isalnum() or c.isspace() else " " for c in name)
    name = " ".join(name.split())
    return name


def fuzzy_match(target: str, candidate: str) -> bool:
    """
    Check if candidate journal name matches target using fuzzy logic.

    Handles cases like:
    - "Nature Biotechnology" vs "Nature Biotechnology Journal"
    - "IEEE TPAMI" vs "IEEE Transactions on Pattern Analysis..."
    - Partial matches for long journal names
    """
    target_norm = normalize_journal_name(target)
    candidate_norm = normalize_journal_name(candidate)

    # Exact match after normalization
    if target_norm == candidate_norm:
        return True

    # One contains the other
    if target_norm in candidate_norm or candidate_norm in target_norm:
        return True

    # Check for significant word overlap (at least 60% of target words)
    target_words = set(target_norm.split())
    candidate_words = set(candidate_norm.split())

    if len(target_words) == 0:
        return False

    overlap = len(target_words & candidate_words)
    overlap_ratio = overlap / len(target_words)

    if overlap_ratio >= 0.6 and overlap >= 2:
        return True

    # Special handling for abbreviations
    # "NEJM" -> "New England Journal of Medicine"
    # "JACS" -> "Journal of the American Chemical Society"
    abbreviation_map = {
        "nejm": "new england journal medicine",
        "jacs": "journal american chemical society",
        "pnas": "proceedings national academy sciences",
        "bmj": "british medical journal",
        "prl": "physical review letters",
    }

    for abbrev, full in abbreviation_map.items():
        if abbrev in target_norm or abbrev in candidate_norm:
            if full in target_norm or full in candidate_norm:
                return True

    return False


def find_journal_position(target: str, journals: List[str]) -> Tuple[int, str, str]:
    """
    Find the position of target journal in results list.

    Returns:
        (position, match_type, matched_name)
        position: 0-indexed position, or -1 if not found
        match_type: "exact", "fuzzy", or "miss"
        matched_name: the actual journal name that matched
    """
    target_norm = normalize_journal_name(target)

    # First pass: exact matches
    for i, journal in enumerate(journals):
        if normalize_journal_name(journal) == target_norm:
            return i, "exact", journal

    # Second pass: fuzzy matches
    for i, journal in enumerate(journals):
        if fuzzy_match(target, journal):
            return i, "fuzzy", journal

    return -1, "miss", ""


def run_benchmark(data_path: str = None) -> BenchmarkSummary:
    """
    Run the benchmark against the ground truth dataset.

    Args:
        data_path: Path to benchmark JSON file. Defaults to tests/data/benchmark_journals.json

    Returns:
        BenchmarkSummary with all results and statistics
    """
    if data_path is None:
        data_path = Path(__file__).parent.parent / "tests" / "data" / "benchmark_journals.json"

    with open(data_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    summary = BenchmarkSummary()

    print("=" * 80)
    print("JOURNAL RECOMMENDATION BENCHMARK")
    print("=" * 80)
    print(f"\nRunning {len(test_cases)} test cases...\n")

    for i, case in enumerate(test_cases):
        print(f"[{i+1}/{len(test_cases)}] {case['discipline']}: {case['title'][:50]}...")

        # Call the service
        start_time = time.time()
        try:
            journals, discipline = openalex_service.search_journals_by_text(
                title=case["title"],
                abstract=case["abstract"],
                keywords=case.get("keywords", []),
            )
            elapsed = time.time() - start_time
        except Exception as e:
            print(f"  ERROR: {e}")
            summary.misses += 1
            summary.total += 1
            continue

        # Get journal names
        journal_names = [j.name for j in journals]

        # Find target position
        target = case["correct_journal"]
        position, match_type, matched_name = find_journal_position(target, journal_names)

        # Record result
        result = BenchmarkResult(
            test_case=case,
            returned_journals=journal_names[:10],  # Store top 10
            position=position,
            match_type=match_type,
            matched_name=matched_name,
        )
        summary.results.append(result)
        summary.total += 1

        # Update statistics
        if position >= 0:
            if position == 0:
                summary.hit_at_1 += 1
            if position < 5:
                summary.hit_at_5 += 1
            if position < 10:
                summary.hit_at_10 += 1
            if position < 15:
                summary.hit_at_15 += 1

            status = f"HIT @{position+1}"
            if match_type == "fuzzy":
                status += f" (fuzzy: '{matched_name}')"
        else:
            summary.misses += 1
            status = "MISS"

        # Track by type
        if case["type"] == "Standard":
            summary.standard_total += 1
            if position >= 0 and position < 10:
                summary.standard_hits += 1
        else:
            summary.edge_total += 1
            if position >= 0 and position < 10:
                summary.edge_hits += 1

        print(f"  Target: {target}")
        print(f"  Result: {status} | Detected: {discipline} | Time: {elapsed:.2f}s")
        if position < 0:
            print(f"  Top 3 returned: {journal_names[:3]}")
        print()

    return summary


def print_summary(summary: BenchmarkSummary):
    """Print formatted benchmark summary."""
    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 80)

    # Overall accuracy
    print(f"\n{'Metric':<25} {'Count':>10} {'Percentage':>15}")
    print("-" * 50)
    print(f"{'Total Test Cases':<25} {summary.total:>10}")
    print(f"{'Hit @ 1':<25} {summary.hit_at_1:>10} {summary.hit_at_1/summary.total*100:>14.1f}%")
    print(f"{'Hit @ 5':<25} {summary.hit_at_5:>10} {summary.hit_at_5/summary.total*100:>14.1f}%")
    print(f"{'Hit @ 10':<25} {summary.hit_at_10:>10} {summary.hit_at_10/summary.total*100:>14.1f}%")
    print(f"{'Hit @ 15':<25} {summary.hit_at_15:>10} {summary.hit_at_15/summary.total*100:>14.1f}%")
    print(f"{'Misses':<25} {summary.misses:>10} {summary.misses/summary.total*100:>14.1f}%")

    # By type
    print("\n" + "-" * 50)
    print("BY TEST TYPE:")
    print("-" * 50)

    if summary.standard_total > 0:
        std_pct = summary.standard_hits / summary.standard_total * 100
        print(f"{'Standard Cases':<25} {summary.standard_hits:>3}/{summary.standard_total:<6} {std_pct:>14.1f}%")

    if summary.edge_total > 0:
        edge_pct = summary.edge_hits / summary.edge_total * 100
        print(f"{'Edge Cases (Interdiscip.)':<25} {summary.edge_hits:>3}/{summary.edge_total:<6} {edge_pct:>14.1f}%")

    # Failed cases detail
    misses = [r for r in summary.results if r.position < 0]
    if misses:
        print("\n" + "-" * 50)
        print("FAILED CASES (MISSES):")
        print("-" * 50)
        for r in misses:
            print(f"\n  [{r.test_case['type']}] {r.test_case['discipline']}")
            print(f"  Title: {r.test_case['title'][:60]}...")
            print(f"  Expected: {r.test_case['correct_journal']}")
            print(f"  Got: {r.returned_journals[:3] if r.returned_journals else 'No results'}")

    # Overall grade
    print("\n" + "=" * 80)
    hit_rate = summary.hit_at_10 / summary.total * 100
    if hit_rate >= 80:
        grade = "EXCELLENT"
    elif hit_rate >= 60:
        grade = "GOOD"
    elif hit_rate >= 40:
        grade = "FAIR"
    else:
        grade = "NEEDS IMPROVEMENT"

    print(f"OVERALL GRADE: {grade} ({hit_rate:.1f}% Hit@10)")
    print("=" * 80)


if __name__ == "__main__":
    summary = run_benchmark()
    print_summary(summary)
