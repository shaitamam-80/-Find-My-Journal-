# User Stories - Find My Journal MVP

## Overview
מסמך זה מכיל User Stories מפורטות עבור הפיצ'רים בעדיפות גבוהה שזוהו ב-PM Report.
כל Story כולל Acceptance Criteria, Technical Notes, ו-Definition of Done.

---

## Epic 1: Why It's a Good Fit (RICE Score: 6.4) ⭐ Priority 1 - COMPLETED

### Story 1.1: Display Match Reasoning - DONE
**As a** researcher searching for journals
**I want to** see why each journal was recommended to me
**So that** I can trust the results and make informed decisions

#### Acceptance Criteria
- [x] Each journal card shows 2-3 bullet points explaining the match
- [x] Explanations reference specific topics/keywords from user's input
- [x] Explanations are displayed in a collapsible section
- [x] Loading state shows skeleton while generating explanations

#### Technical Notes
- **Backend**: Added `match_details` and `matched_topics` to Journal model
- **Backend**: Created `generate_match_details()` in `scoring.py`
- **Frontend**: Updated `JournalCard.tsx` and `AccordionJournalCard.tsx`
- **Skills**: `backend-dev`, `frontend-dev`

#### Definition of Done
- [x] Unit tests pass for match reason generation
- [x] Frontend build passes
- [x] Hebrew RTL layout works correctly
- [x] Performance: explanations don't add >500ms to response

---

### Story 1.2: Topic Match Highlighting - DONE
**As a** researcher reviewing results
**I want to** see which topics matched between my paper and the journal
**So that** I can quickly assess relevance

#### Acceptance Criteria
- [x] Matching topics are displayed as colored badges
- [x] Topics shown with green checkmark indicating match
- [x] Maximum 5 topics shown
- [x] Integrated into JournalCard and AccordionJournalCard

#### Technical Notes
- **Backend**: Return `matched_topics` in search response
- **Frontend**: Green topic badges with checkmark in both card components
- **Skills**: `frontend-dev` (component patterns), `backend-dev`

#### Definition of Done
- [x] Frontend build passes
- [x] Visual design consistent with existing UI

---

## Epic 2: Discipline Detection Improvement (RICE Score: 2.9) ⭐ Priority 2

### Story 2.1: Auto-Detect Primary Discipline
**As a** researcher
**I want** the system to automatically detect my paper's discipline
**So that** I get better journal matches without manual selection

#### Acceptance Criteria
- [ ] System analyzes title + abstract to detect discipline
- [ ] Detected discipline shown with confidence score
- [ ] User can override detection with manual selection
- [ ] Detection runs automatically on form blur

#### Technical Notes
- **Backend**: Use OpenAlex concepts API for classification
- **Frontend**: Auto-populate discipline dropdown
- **Skills**: `backend-dev` (async patterns), `frontend-dev`

#### Definition of Done
- [ ] Accuracy >80% on test set of 50 papers
- [ ] Response time <2 seconds
- [ ] Manual override persists in session

---

### Story 2.2: Sub-discipline Refinement
**As a** researcher in a specialized field
**I want to** refine my discipline to sub-field level
**So that** I get more targeted journal recommendations

#### Acceptance Criteria
- [ ] After main discipline selected, show relevant sub-disciplines
- [ ] Sub-disciplines fetched from OpenAlex hierarchy
- [ ] Search results weighted by sub-discipline match
- [ ] "All sub-disciplines" option available

#### Technical Notes
- **Backend**: Implement discipline hierarchy lookup
- **Frontend**: Cascading dropdown component
- **Skills**: `database` (caching), `frontend-dev`

#### Definition of Done
- [ ] Sub-discipline data cached in Supabase
- [ ] UI responsive on mobile
- [ ] Tests cover all major disciplines

---

## Epic 3: Share Results (RICE Score: 4.0) ⭐ Quick Win - COMPLETED

### Story 3.1: Copy Results Link - DONE
**As a** researcher
**I want to** share my search results with colleagues
**So that** they can see my journal recommendations

#### Acceptance Criteria
- [x] "Share" button generates unique link
- [x] Link opens search results without requiring login
- [x] Shared results expire after 7 days
- [x] Copy-to-clipboard with success feedback

#### Technical Notes
- **Backend**: Created `/api/v1/share` endpoint in `share.py`
- **Database**: Created `shared_results` table migration
- **Frontend**: Added Share button to Search.tsx with copy feedback
- **Skills**: `backend-dev`, `database`, `frontend-dev`

#### Definition of Done
- [x] Backend endpoint created and tested
- [x] Migration file created (004_shared_results.sql)
- [x] RLS policy for shared results included
- [x] Frontend build passes

---

### Story 3.2: Export to PDF
**As a** researcher
**I want to** download my results as a PDF
**So that** I can share offline or include in my notes

#### Acceptance Criteria
- [ ] "Download PDF" button on results page
- [ ] PDF includes: search query, top 10 results, match scores
- [ ] Branded header with Find My Journal logo
- [ ] File named with timestamp

#### Technical Notes
- **Frontend**: Use browser print-to-PDF or jsPDF library
- **Skills**: `frontend-dev`

#### Definition of Done
- [ ] PDF renders correctly
- [ ] Hebrew text displays properly in PDF
- [ ] File size <2MB

---

## Epic 4: Saved Searches (RICE Score: 3.6) ⭐ Priority 3

### Story 4.1: Save Search to Profile
**As a** logged-in researcher
**I want to** save my searches
**So that** I can revisit them later

#### Acceptance Criteria
- [ ] "Save" button appears after search completes
- [ ] Saved searches appear in user profile/dashboard
- [ ] Maximum 20 saved searches for free users
- [ ] Duplicate detection prevents saving same search twice

#### Technical Notes
- **Database**: Create `saved_searches` table
- **Backend**: CRUD endpoints for saved searches
- **Frontend**: Save button + My Searches page
- **Skills**: `database`, `backend-dev`, `frontend-dev`

#### Definition of Done
- [ ] RLS policies protect user data
- [ ] Pagination for saved searches list
- [ ] Delete functionality works
- [ ] Tests cover all CRUD operations

---

### Story 4.2: Re-run Saved Search
**As a** researcher with saved searches
**I want to** re-run a previous search
**So that** I can see updated results

#### Acceptance Criteria
- [ ] "Run Again" button on each saved search
- [ ] Results compared to previous run (new/removed journals highlighted)
- [ ] Option to update saved results or keep original

#### Technical Notes
- **Backend**: Compare current vs saved results
- **Frontend**: Diff visualization component
- **Skills**: `backend-dev`, `frontend-dev`

#### Definition of Done
- [ ] Comparison logic tested
- [ ] UI clearly shows changes
- [ ] Performance acceptable (<3s)

---

## Epic 5: Feedback Widget (RICE Score: 3.2)

### Story 5.1: Rate Search Results
**As a** researcher
**I want to** rate how helpful the results were
**So that** I can help improve the system

#### Acceptance Criteria
- [ ] 1-5 star rating appears after viewing results
- [ ] Optional text feedback field
- [ ] Rating submits without page reload
- [ ] Thank you message displayed

#### Technical Notes
- **Database**: `feedback` table
- **Backend**: POST `/api/v1/feedback` endpoint
- **Frontend**: Star rating component
- **Skills**: `database`, `backend-dev`, `frontend-dev`

#### Definition of Done
- [ ] Anonymous feedback allowed
- [ ] Rate limiting prevents spam
- [ ] Admin can view feedback (future)

---

### Story 5.2: Report Incorrect Match
**As a** researcher
**I want to** report when a journal doesn't match my paper
**So that** the algorithm can be improved

#### Acceptance Criteria
- [ ] "Report Issue" link on each journal card
- [ ] Dropdown: "Not relevant", "Wrong discipline", "Other"
- [ ] Report includes journal ID and search context
- [ ] Confirmation toast after submit

#### Technical Notes
- **Database**: `match_reports` table
- **Backend**: POST `/api/v1/report` endpoint
- **Skills**: `database`, `backend-dev`, `frontend-dev`

#### Definition of Done
- [ ] Reports stored with full context
- [ ] No PII logged (privacy)
- [ ] Admin notification (future)

---

## Development Tracks

### Track A: Backend (Stories 1.1, 2.1, 3.1, 4.1, 5.1)
**Owner**: Backend Agent
**Skills**: `backend-dev`, `database`

### Track B: Frontend (Stories 1.2, 2.2, 3.2, 4.2, 5.2)
**Owner**: Frontend Agent
**Skills**: `frontend-dev`

### Track C: Infrastructure
**Owner**: DevOps Agent
**Tasks**: Analytics setup, monitoring, deployment pipeline

---

## Sprint Plan

### Sprint 1 (Week 1-2)
| Track | Stories | Points |
|-------|---------|--------|
| A | 1.1, 3.1 | 8 |
| B | 1.2, 3.2 | 5 |
| C | Analytics Setup | 3 |

### Sprint 2 (Week 3-4)
| Track | Stories | Points |
|-------|---------|--------|
| A | 2.1, 4.1 | 8 |
| B | 2.2, 4.2 | 5 |
| C | Monitoring | 3 |

### Sprint 3 (Week 5-6)
| Track | Stories | Points |
|-------|---------|--------|
| A | 5.1 | 3 |
| B | 5.2 | 3 |
| C | Performance optimization | 5 |

---

## Acceptance Criteria Legend
- [ ] Not started
- [x] Completed
- [~] In progress

## Story Points (Fibonacci)
- 1: Trivial change
- 2: Small task, no unknowns
- 3: Medium task, some complexity
- 5: Large task, multiple components
- 8: Very large, consider splitting

---

*Document created: December 24, 2024*
*Last updated: December 24, 2024*
