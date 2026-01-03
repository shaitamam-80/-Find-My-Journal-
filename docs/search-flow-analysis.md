# Search Flow Analysis

## Overview

This document details the current search implementation in Find My Journal, identifying key areas for improvement through multi-discipline detection, article type awareness, and enhanced scoring.

## Current Architecture

```
                    User Input (Title + Abstract + Keywords)
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │        API Endpoint                  │
                    │   backend/app/api/v1/search.py:24   │
                    └─────────────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │    search_journals_by_text()         │
                    │   backend/app/services/openalex/    │
                    │   search.py:514-680                 │
                    └─────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │  Topic-Based  │      │ Subfield-Based│      │ Keyword-Based │
    │    Search     │      │    Search     │      │    Search     │
    │  lines 545-549│      │  lines 560-570│      │  lines 572-578│
    └───────────────┘      └───────────────┘      └───────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    ▼
                    ┌─────────────────────────────────────┐
                    │      Merge & Score Results          │
                    │      lines 581-646                  │
                    └─────────────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │     Normalize & Return Top 15       │
                    │     lines 648-680                   │
                    └─────────────────────────────────────┘
```

## Key Files and Functions

### 1. API Entry Point
**File:** `backend/app/api/v1/search.py:24-107`

```python
@router.post("", response_model=SearchResponse)
async def search_journals(request: SearchRequest, user: UserProfile = Depends(check_search_limit)):
    # Calls openalex_service.search_journals_by_text()
    # Returns: journals list + discipline + field + confidence
```

### 2. Main Search Function
**File:** `backend/app/services/openalex/search.py:514-680`

```python
def search_journals_by_text(title, abstract, keywords, prefer_open_access):
    # 4-step hybrid search:
    # 1. Topic-based search (ML approach)
    # 2. Subfield-based search (ID filtering)
    # 3. Keyword-based search
    # 4. Merge and score results
```

### 3. Discipline Detection (CURRENT)
**File:** `backend/app/services/openalex/search.py:65-142`

```python
def get_topics_from_similar_works(search_query):
    # 1. Search for 50 similar works via OpenAlex
    # 2. Extract topic IDs with frequency scoring
    # 3. Extract subfield/field hierarchy
    # 4. Calculate confidence score
    # Returns: (topic_ids, subfield, field, subfield_id, confidence)
```

**LIMITATION:** Only returns ONE subfield (the most common). Does not detect multiple disciplines.

### 4. Scoring Algorithm (CURRENT)
**File:** `backend/app/services/openalex/scoring.py:112-225`

```python
def calculate_relevance_score(journal, discipline, is_topic_match, is_keyword_match, search_terms, core_journals):
    # Current scoring weights:
    score = 0.0
    if is_topic_match: score += 20.0
    if is_keyword_match: score += 10.0
    # Exact title match: +50
    # H-index: h_index * 0.05
    # Citation rate: 2yr_mean_citedness * 1.5
    # Discipline boost: +15 to +25
    return score
```

**LIMITATIONS:**
- No multi-discipline bonus
- No cross-discipline coverage bonus
- No article type fit bonus
- No topic relevance penalty

## Current Discipline Detection Flow

```
search_query = "OAB fibromyalgia systematic review"
          │
          ▼
┌────────────────────────────────────────┐
│  get_topics_from_similar_works()       │
│  - Searches 50 similar works           │
│  - Counts subfield frequencies         │
│  - Returns ONLY top subfield           │
└────────────────────────────────────────┘
          │
          ▼
Returns: ("Urology", "Medicine", 2713, 0.44)
          │
          ▼
PROBLEM: Misses Gynecology, Rheumatology, Pain Medicine
```

## Current Scoring Formula

| Factor | Weight | Description |
|--------|--------|-------------|
| Topic Match | +20 | Found via topic search |
| Keyword Match | +10 | Found via keyword search |
| Title Match | +50 | Journal name contains search term |
| H-Index | h * 0.05 | Quality indicator |
| Citation Rate | rate * 1.5 | 2-year mean citedness |
| Discipline Boost | +15-25 | Name/topic matches discipline |
| Merge Bonus | x10 amplifier | Found in both keyword AND topic |

## Identified Gaps

### Gap 1: Single Discipline Detection
**Current:** Only detects "Urology" for OAB + Fibromyalgia paper
**Target:** Detect Urology, Gynecology, Rheumatology, Pain Medicine

### Gap 2: No Article Type Detection
**Current:** No distinction between systematic review, RCT, case report
**Target:** Detect article type and match with appropriate journals

### Gap 3: No Cross-Discipline Scoring
**Current:** Journals covering multiple detected disciplines get no bonus
**Target:** Bonus for journals that publish on BOTH urology AND rheumatology

### Gap 4: No Topic Relevance Validation
**Current:** Journals with irrelevant topics (e.g., COVID) can appear
**Target:** Filter or warn on journals with irrelevant main topics

## Data Models

### Current SearchResponse
**File:** `backend/app/models/journal.py:163-171`

```python
class SearchResponse(BaseModel):
    query: str
    discipline: Optional[str] = None
    discipline_detection: Optional[DisciplineDetection] = None
    total_found: int
    journals: List[Journal]
    search_id: Optional[str] = None
```

### Current DisciplineDetection
**File:** `backend/app/models/journal.py:155-160`

```python
class DisciplineDetection(BaseModel):
    name: str  # Single discipline only
    field: Optional[str]
    confidence: float
    source: str = "openalex"
```

## Improvement Plan Summary

1. **Multi-Discipline Detector** - Detect 3-4 relevant disciplines
2. **Article Type Detector** - Identify systematic review, RCT, etc.
3. **Enhanced Scoring** - Add multi-discipline bonus, cross-discipline coverage
4. **Topic Validator** - Filter irrelevant journals, add warnings
5. **Updated Response** - Include all detected disciplines and article type

## Files to Create

- `backend/app/services/analysis/__init__.py`
- `backend/app/services/analysis/discipline_detector.py`
- `backend/app/services/analysis/article_type_detector.py`
- `backend/app/services/analysis/topic_validator.py`
- `backend/tests/test_search_cases.py`

## Files to Modify

- `backend/app/services/openalex/search.py` - Integrate new detectors
- `backend/app/services/openalex/scoring.py` - Add new scoring factors
- `backend/app/models/journal.py` - Update response models
- `frontend/src/types/index.ts` - Add new types
- `frontend/src/components/SearchResults.tsx` - Display improvements
