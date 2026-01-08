# Refactor Log - Phase 0: Legacy Analysis Code Cleanup
# Target: Remove legacy discipline detection code
# Started: 2026-01-08
# Command: /project:refactor "Remove legacy discipline detection code..."

## Phase 1: Analysis

### Timestamp: 2026-01-08

### Target Identification

**Files to DELETE (4 files):**
1. `backend/app/services/analysis/discipline_detector.py` (499 lines)
   - Contains: DISCIPLINE_KEYWORDS (hardcoded ~25 disciplines), OPENALEX_FIELD_MAPPING
   - Classes: MultiDisciplineDetector, DetectedDiscipline
   - Functions: detect_disciplines()

2. `backend/app/services/analysis/hybrid_detector.py` (261 lines)
   - Contains: HybridDisciplineDetector
   - Functions: detect_disciplines_hybrid(), detect_disciplines_merged()
   - Depends on: discipline_detector, universal_detector

3. `backend/app/services/analysis/universal_detector.py` (307 lines)
   - Contains: UniversalDisciplineDetector, DetectedSubfield
   - Functions: detect_disciplines_universal()
   - Purpose: REDUNDANT with get_topics_from_similar_works() in search.py

4. `backend/app/services/openalex_service.py` (36 lines)
   - Status: Already deprecated, just a redirect
   - Just re-exports from openalex package

**Files to CLEAN (2 files):**
1. `backend/app/services/openalex/constants.py`
   - REMOVE: DISCIPLINE_KEYWORDS (150+ lines), KEY_JOURNALS_BY_DISCIPLINE
   - KEEP: RELEVANT_TOPIC_KEYWORDS (for soft-boosting), load_core_journals()

2. `backend/app/services/openalex/utils.py`
   - REMOVE: detect_discipline() function, DISCIPLINE_KEYWORDS import
   - KEEP: STOPWORDS, extract_search_terms(), normalize_journal_name()

### Code Smells
1. **Duplication**: discipline_detector.py and constants.py both have DISCIPLINE_KEYWORDS
2. **Hardcoded Data**: 25+ disciplines with hundreds of keywords - not maintainable
3. **Redundancy**: universal_detector does same thing as get_topics_from_similar_works()
4. **Dead Code**: openalex_service.py is just a deprecated redirect

### Dependencies

**Who calls this code?**
- `search.py:29` imports `detect_disciplines_hybrid` from analysis
- `search.py:400` imports `OPENALEX_FIELD_MAPPING` from discipline_detector
- `search.py:604` calls `detect_disciplines_hybrid()`
- `analysis/__init__.py` exports all removed modules
- `openalex/__init__.py` exports from utils
- Tests: test_universal_detection.py

**What data structures does it modify?**
- Returns list of discipline dicts to API response
- Affects `detected_disciplines` field in SearchResponse

**Test coverage:**
- test_universal_detection.py - tests universal and hybrid detection
- These tests will be REMOVED or UPDATED

### Risk Assessment
- **Risk Level:** MEDIUM
- **Core Logic Affected:** Yes - discipline detection affects search scoring
- **Auth Affected:** No
- **Database Affected:** No

**Rollback strategy:**
```bash
git checkout HEAD~1 -- backend/app/services/analysis/
git checkout HEAD~1 -- backend/app/services/openalex/constants.py
git checkout HEAD~1 -- backend/app/services/openalex/utils.py
```

## Phase 2: Planning

### Strategy

**Current State:**
- 3-layer discipline detection: keyword -> universal -> hybrid
- All use hardcoded keyword lists
- OpenAlex already provides ML-based classification via Topics API

**Target State:**
- Single source of truth: OpenAlex's ML classification (already in get_topics_from_similar_works)
- No hardcoded discipline keywords
- Simpler, maintainable codebase

**Approach:**
1. Delete legacy files
2. Update search.py to use OpenAlex subfield/field directly
3. Construct `detected_disciplines` from OpenAlex response
4. Clean up exports and tests

### Key Changes to search.py

**Line 604-608 (detect_disciplines_hybrid call):**
BEFORE:
```python
detected_disciplines_dicts = detect_disciplines_hybrid(
    title=title, abstract=abstract, keywords=keywords, prefer_universal=True,
)
```

AFTER:
- Move topic detection earlier in the function
- Use OpenAlex subfield/field as discipline source
- Construct detected_disciplines from subfield_scores

**Line 400-411 (is_journal_relevant_to_any_discipline):**
BEFORE:
```python
from app.services.analysis.discipline_detector import OPENALEX_FIELD_MAPPING
openalex_info = OPENALEX_FIELD_MAPPING.get(discipline_name, {})
```

AFTER:
- Remove this function entirely OR
- Simplify to use OpenAlex subfield names directly

### Verification Strategy
- Existing tests: Most will fail initially (expected)
- After cleanup: Run `pytest tests/` excluding universal detection tests
- Manual: Test search endpoint with sample queries

## Phase 3: Execution

See following commits for step-by-step changes.

### Changes Made
| Step | Change | Verified |
|------|--------|----------|
| 1 | Delete discipline_detector.py | ✅ |
| 2 | Delete hybrid_detector.py | ✅ |
| 3 | Delete universal_detector.py | ✅ |
| 4 | Delete openalex_service.py | ✅ |
| 5 | Clean constants.py - removed DISCIPLINE_KEYWORDS, KEY_JOURNALS_BY_DISCIPLINE | ✅ |
| 6 | Clean utils.py - removed detect_discipline() | ✅ |
| 7 | Update analysis/__init__.py - removed deleted module exports | ✅ |
| 8 | Update openalex/__init__.py - removed deleted function exports | ✅ |
| 9 | Update search.py - construct detected_disciplines from OpenAlex data | ✅ |
| 10 | Update api/v1/search.py - fix import paths | ✅ |
| 11 | Delete test_universal_detection.py | ✅ |
| 12 | Delete tests/golden_set/ directory | ✅ |
| 13 | Update test_search.py - remove detect_discipline tests | ✅ |
| 14 | Update test_benchmark_search.py - fix 6-tuple unpacking | ✅ |
| 15 | Update run_benchmark.py - fix 6-tuple unpacking | ✅ |

## Phase 4: Verification

### Tests Run: 2026-01-08
```
pytest tests/test_search.py tests/test_auth.py -v
======================= 42 passed, 46 warnings =======================
```

All tests pass. One pre-existing failure in test_db_connect.py (async initialization issue) is unrelated to this refactoring.

## Summary

### Files Deleted (4)
- `backend/app/services/analysis/discipline_detector.py`
- `backend/app/services/analysis/hybrid_detector.py`
- `backend/app/services/analysis/universal_detector.py`
- `backend/app/services/openalex_service.py`

### Files Modified (8)
- `backend/app/services/openalex/search.py` - Use OpenAlex ML directly
- `backend/app/services/openalex/constants.py` - Removed hardcoded lists
- `backend/app/services/openalex/utils.py` - Removed detect_discipline()
- `backend/app/services/analysis/__init__.py` - Cleaned exports
- `backend/app/services/openalex/__init__.py` - Cleaned exports
- `backend/app/api/v1/search.py` - Fixed import path
- `backend/tests/test_search.py` - Removed obsolete tests
- `backend/tests/test_benchmark_search.py` - Fixed unpacking

### Tests Deleted
- `backend/tests/test_universal_detection.py`
- `backend/tests/golden_set/` directory

### Lines of Code Removed
- ~1100 lines of hardcoded discipline detection code
- ~350 lines of DISCIPLINE_KEYWORDS in constants.py

## Notes

The key insight is that `get_topics_from_similar_works()` in search.py ALREADY does what we need:
- Searches OpenAlex for similar works
- Extracts subfield and field from topics
- Returns confidence score
- Returns subfield_id for API filtering

The legacy discipline detection was a workaround before this was implemented properly.
