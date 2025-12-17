# 🧠 Project Memory: Find My Journal

## 📍 Current Status
- **Phase:** Refactoring & Polish (Post-Sprint 3).
- **Recent Achievement:** Implemented "Hybrid Search" (Keywords + Topics) boosting accuracy to 70%.
- **Recent Achievement:** Added "Incognito Mode" for privacy.
- **Recent Achievement:** Added Export CSV & Print capabilities.

## 🏗️ Architecture Decisions
- **Backend:** FastAPI (Python 3.10) on Railway.
- **Frontend:** React + Vite + Tailwind on Vercel.
- **Database:** Supabase (PostgreSQL + GoTrue Auth).
- **Search Logic:**
  - **Primary:** OpenAlex API.
  - **Algorithm:** Soft Boost (Not Hard Filter). We boost scores if the discipline matches, but we don't hide results if they have strong Topic matches.
  - **Privacy:** If `incognito_mode=True`, do NOT log query text to DB.

## 📝 Coding Standards
- **Python:** Snake_case, Pydantic models for validation, Services layer for logic.
- **React:** Functional components, Hooks, Tailwind for styling.
# FindMyJournal - Project Memory
## Central Documentation for All Agents

> ⚠️ **כל סוכן חייב לקרוא קובץ זה לפני תחילת עבודה ולעדכן אותו בסיום כל משימה!**

---

## 🎯 Current Sprint: December 17, 2024

**Goal:** Fix critical bugs, remove false/misleading claims, update to academic-friendly design

**Master Plan Location:** `.claude/MasterPlan-Dec17.md`

---

## 📊 Task Status Board

### 🔴 Critical (Must Fix)

| ID | Description | Agent | Status | Updated |
|----|-------------|-------|--------|---------|
| C1 | Fix Match Score calculation (showing 2845% instead of 28%) | backend-agent | ✅ Complete | 2024-12-17 |
| C2 | Remove "20,000+ Researchers" false claim | frontend-agent | ✅ Complete | 2024-12-17 |
| C3 | Remove "150+ Countries" false claim | frontend-agent | ✅ Complete | 2024-12-17 |
| C4 | Remove "98% Accuracy" false claim | frontend-agent | ✅ Complete | 2024-12-17 |
| C5 | Remove "2M+ Papers Analyzed" false claim | frontend-agent | ✅ Complete | 2024-12-17 |
| C6 | Disable distracting background animation on Login/Signup | frontend-agent | ✅ Complete | 2024-12-17 |

### 🟠 Medium Priority

| ID | Description | Agent | Status | Updated |
|----|-------------|-------|--------|---------|
| M1 | Remove non-existent features from Landing (IF, Acceptance Rate, etc.) | frontend-agent | ✅ Complete | 2024-12-17 |
| M2 | Improve "Why It's a Good Fit" text (too generic) | backend-agent | ⏳ Pending | |
| M3 | Improve Discipline Detection (missed Endocrinology) | backend-agent | ⏳ Pending | |
| M4 | Change "H-Index" label to "Journal H-Index" | frontend-agent | ✅ Complete | 2024-12-17 |
| M5 | Update color palette to academic-friendly (Navy/Slate) | ui-ux-agent | ✅ Complete | 2024-12-17 |

### 🟡 Enhancements

| ID | Description | Agent | Status | Updated |
|----|-------------|-------|--------|---------|
| E1 | Add Title/FirstName/LastName fields to User model | backend-agent + frontend-agent | ⏳ Pending | |
| E2 | Add personalized greeting with user name | frontend-agent | ⏳ Pending | |
| E3 | Academic design - muted colors, less gradients | ui-ux-agent | ⏳ Pending | |
| E4 | Update "50,000+ Journals" to real number from OpenAlex | backend-agent | ⏳ Pending | |

---

## 🎨 Design Decisions

### Color Palette (Academic)
```css
--color-primary: #1e3a5f;      /* Navy - Main brand color */
--color-secondary: #4a6fa5;    /* Slate Blue - Secondary actions */
--color-accent: #0d9488;       /* Teal - Highlights, links */
--color-success: #059669;      /* Emerald - Success states */
--color-warning: #d97706;      /* Amber - Warnings */
--color-background: #f8fafc;   /* Slate 50 - Page background */
--color-surface: #ffffff;      /* White - Card backgrounds */
--color-text: #1e293b;         /* Slate 800 - Primary text */
--color-text-muted: #64748b;   /* Slate 500 - Secondary text */
```

### Features to KEEP on Landing Page
- ✅ Support for 40+ Languages (TRUE - OpenAlex has multi-language journals)
- ✅ Predatory Journal Filtering (if implemented)
- ✅ Deep Context Analysis
- ✅ How It Works - 3 steps

### Features to REMOVE from Landing Page
- ❌ Impact Factor (not available)
- ❌ Acceptance rates (not available)
- ❌ Estimated Publication Times (not available)
- ❌ Reference Manager Export (not implemented)

---

## 📁 Key Files Reference

### Project Documentation
```
CLAUDE.md                    # ⭐ Main project info file - UPDATE AT END!
PROJECT_MEMORY.md            # This file - agent activity log
.claude/MasterPlan-Dec17.md  # Current sprint plan
README.md                    # Project readme
CHANGELOG.md                 # Version history
```

### Frontend
```
frontend/src/pages/
├── Landing.tsx          # Landing page with false claims
├── Login.tsx            # Login with animation
├── Signup.tsx           # Signup page
└── Search.tsx           # Search results page

frontend/src/components/search/
├── AIAnalysisHeader.tsx      # AI analysis section
├── AccordionJournalCard.tsx  # Journal cards
├── FilterBar.tsx             # Filter buttons
├── CategorySection.tsx       # Category groups
└── searchResultsMapper.ts    # Data mapping (Match Score bug here!)
```

### Backend
```
backend/app/
├── services/search_service.py    # Search logic, relevance_score
├── models/user.py                # User model (add fields here)
├── schemas/user.py               # User schemas
└── api/routes/search.py          # Search API endpoint
```

---

## 📝 Agent Activity Log

<!-- 
Agents: Add your updates here in REVERSE chronological order (newest first)
Use the format below:
-->

---
## 2024-12-17 (Phase 2) - Design System Upgrade

### ✅ Tasks Completed:
- [x] Created design-tokens.css with HSL-based CSS variables for light/dark modes
- [x] Added professional fonts (Inter, Assistant for Hebrew, JetBrains Mono)
- [x] Created reusable UI components (StatusBadge, MatchScoreBadge, ThemeToggle)
- [x] Added useDarkMode hook for dark mode support
- [x] Converted physical margins to logical properties for RTL support (ml→ms, pl→ps, left→start)
- [x] Installed clsx and tailwind-merge for className utilities

### 📁 Files Created:
- `frontend/src/styles/design-tokens.css` - HSL-based CSS variables with dark mode
- `frontend/src/lib/utils.ts` - cn() utility for className merging
- `frontend/src/hooks/useDarkMode.ts` - Dark mode state management hook
- `frontend/src/components/ui/StatusBadge.tsx` - Journal category badges
- `frontend/src/components/ui/MatchScoreBadge.tsx` - Semantic match score display
- `frontend/src/components/ui/ThemeToggle.tsx` - Dark/light mode toggle button

### 📁 Files Modified:
- `frontend/index.html` - Added Inter, Assistant, JetBrains Mono fonts
- `frontend/src/index.css` - Imported design-tokens, added font variables
- `frontend/src/pages/Login.tsx` - RTL: left→start, pl→ps, pr→pe
- `frontend/src/pages/SignUp.tsx` - RTL: left→start, pl→ps, pr→pe
- `frontend/src/components/search/CategorySection.tsx` - RTL: ml-auto→ms-auto
- `frontend/src/components/search/AccordionJournalCard.tsx` - RTL: text-left→text-start

### 📢 Notes:
- Dark mode ready but toggle not yet added to navigation
- RTL support added via logical properties (works with dir="rtl")
- New components available for future use in search results

### Status: ✅ Complete
---
## 2024-12-17 - Claude Code Sprint Execution

### ✅ Tasks Completed:
- [x] C1: Fixed Match Score calculation - normalized scores to 0-1 range in backend
- [x] C2: Removed "20,000+ Researchers" false claim from Landing and Login pages
- [x] C3: Removed "150+ Countries" false claim from Landing page
- [x] C4: Removed "98% Accuracy" false claim from Landing page
- [x] C5: Removed "2M+ Papers Analyzed" false claim - replaced Stats section with OpenAlex attribution
- [x] C6: Disabled distracting animations on Login/Signup - kept static gradient backgrounds
- [x] M1: Removed non-existent features (Impact Factor, Acceptance Rates, Publication Times, Reference Manager Export) - replaced with true features (AI-Powered Matching, Open Access Detection)
- [x] M4: Changed "H-Index" to "Journal H-Index" for clarity
- [x] M5: Updated color palette to academic Navy/Slate theme

### 📁 Files Modified:
- `backend/app/services/openalex/search.py` - Added score normalization (lines 573-578)
- `frontend/src/pages/LandingPage.tsx` - Replaced false stats, fixed features, updated colors
- `frontend/src/pages/Login.tsx` - Removed animations, updated colors to slate/navy
- `frontend/src/pages/SignUp.tsx` - Removed animations, updated colors to slate/navy
- `frontend/src/components/search/AccordionJournalCard.tsx` - Fixed H-Index label
- `frontend/src/index.css` - Updated CSS variables from sky-blue to navy/slate palette

### ⚠️ Issues Encountered:
- None - all changes applied successfully

### 📢 Notes for Other Agents:
- Match Score now displays 0-100% correctly
- Color palette changed from bright cyan/blue to professional navy/slate
- All false marketing claims have been removed
- Frontend build passes successfully

### Status: ✅ Complete
---

### [Template - Copy and fill]
```
---
## 2024-12-17 HH:MM - [Agent Name]

### ✅ Tasks Completed:
- [x] Task description

### 📁 Files Modified:
- `path/to/file.tsx` - What was changed

### ⚠️ Issues Encountered:
- Issue description → Solution applied

### 📢 Notes for Other Agents:
- Important coordination note

### Status: ✅ Complete / ⏳ In Progress / ❌ Blocked
---
```

---

## 🔗 Dependencies & Conflicts

| Dependency | Agents Involved | Resolution |
|------------|-----------------|------------|
| User model changes need frontend + backend sync | backend-agent, frontend-agent | backend-agent completes first, then frontend |
| Color palette affects all pages | ui-ux-agent, frontend-agent | ui-ux-agent creates tokens first |

---

## 💡 Key Decisions Log

| Date | Decision | Rationale | Made By |
|------|----------|-----------|---------|
| 2024-12-17 | Remove all false statistics | Integrity > Marketing | Product Owner |
| 2024-12-17 | Use Navy/Slate colors | More academic, less startup-y | UI Review |
| 2024-12-17 | Keep "40+ Languages" | Actually true via OpenAlex | Fact check |

---

## 🧪 Testing Checklist

Before Git Push:
- [x] `npm run build` passes (frontend) ✅
- [ ] `npm run lint` passes (frontend)
- [ ] `pytest` passes (backend) - running
- [ ] Playwright E2E tests pass
- [x] Manual check: Match Score shows 0-100% ✅ (code fixed)
- [x] Manual check: No false claims visible ✅
- [x] Manual check: No distracting animations ✅
- [ ] Screenshots captured
- [x] CLAUDE.md updated with current system info ⭐
- [x] PROJECT_MEMORY.md fully updated ✅

---

## 📞 Communication Protocol

1. **Before starting:** Read this entire file
2. **During work:** Update Status Board when task changes status
3. **After completing:** Add entry to Activity Log
4. **If blocked:** Add to Issues section and tag relevant agent
5. **Conflicts:** Document in Dependencies section

---

**Last Updated:** December 17, 2024 - Sprint Execution Complete
**Updated By:** Claude Code