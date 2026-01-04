"""
Local test of Phase 1 improvements using golden set case shai_001.
Tests the OAB + Fibromyalgia paper to see if IJGO appears and NEJM is not #1.
"""
import json
from pathlib import Path

# Import the search function
from app.services.openalex.search import search_journals_by_text

# Load golden set
GOLDEN_SET_PATH = Path(__file__).parent / "tests" / "golden_set" / "search-golden-set.json"

with open(GOLDEN_SET_PATH) as f:
    golden_data = json.load(f)

# Get shai_001 test case
test_case = next(c for c in golden_data["test_cases"] if c["id"] == "shai_001")

print("=" * 80)
print("TESTING PHASE 1 IMPROVEMENTS")
print("=" * 80)
print(f"\nTest Case: {test_case['id']}")
print(f"Title: {test_case['title'][:60]}...")
print(f"Expected in top 10: {test_case['must_appear_top_10']}")
print(f"Should NOT be #1: {test_case['should_not_be_first']}")
print("\n" + "=" * 80)


def run_test():
    """Run the search test."""
    print("\nSearching for journals...")

    # search_journals_by_text returns 6 values:
    # (journals, subfield, field, confidence, detected_disciplines, article_type)
    journals, subfield, field, confidence, detected_disciplines, article_type = search_journals_by_text(
        title=test_case["title"],
        abstract=test_case["abstract"],
        keywords=test_case.get("keywords", []),
    )

    # Create a results object similar to SearchResponse
    class Results:
        def __init__(self):
            self.journals = journals
            self.detected_disciplines = detected_disciplines or []
            self.article_type = article_type

    results = Results()

    print(f"\nSUCCESS: Found {len(results.journals)} journals")
    # Handle both dict and object formats
    if results.detected_disciplines:
        disc_names = [d.get('name') if isinstance(d, dict) else getattr(d, 'name', str(d)) for d in results.detected_disciplines]
        print(f"Detected disciplines: {disc_names}")
    if results.article_type:
        article_name = results.article_type.get('display_name') if isinstance(results.article_type, dict) else getattr(results.article_type, 'display_name', str(results.article_type))
        print(f"Article type: {article_name}")

    print("\n" + "=" * 80)
    print("TOP 10 RESULTS")
    print("=" * 80)

    for i, journal in enumerate(results.journals[:10], 1):
        # Normalize score to 0-100 range for display
        max_score = results.journals[0].relevance_score if results.journals else 1
        normalized_score = (journal.relevance_score / max_score * 100) if max_score > 0 else 0

        print(f"\n{i}. {journal.name}")
        print(f"   Score: {normalized_score:.1f}% (raw: {journal.relevance_score:.2f})")
        print(f"   H-index: {journal.metrics.h_index or 0}")
        print(f"   Citedness: {journal.metrics.two_yr_mean_citedness or 0:.2f}")

    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    # Check if IJGO or similar appears in top 10
    top_10_names = [j.name.lower() for j in results.journals[:10]]
    ijgo_found = any(
        "gynaecol" in name or "ijgo" in name or "gynecol" in name
        for name in top_10_names
    )

    # Check if NEJM is #1
    first_journal = results.journals[0].name if results.journals else ""
    nejm_is_first = "new england" in first_journal.lower() or "nejm" in first_journal.lower()

    print(f"\n✓ IJGO in top 10: {'YES SUCCESS:' if ijgo_found else 'NO FAIL:'}")
    print(f"✓ NEJM is NOT #1: {'YES SUCCESS:' if not nejm_is_first else 'NO FAIL: (NEJM is #1)'}")

    if ijgo_found and not nejm_is_first:
        print("\n🎉 SUCCESS! Phase 1 improvements are working!")
    else:
        print("\nWARNING:  Phase 1 needs more work. Consider Phase 2 (Normalized Impact).")

    return results


if __name__ == "__main__":
    run_test()
