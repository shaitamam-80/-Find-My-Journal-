# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Find My Journal is a SaaS application that helps researchers discover academic journals for their papers. It uses a hybrid search algorithm combining keywords and topic matching via the OpenAlex API.

## Development Commands

### Backend (FastAPI + Python)

```bash
# Activate virtual environment (from project root)
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Install dependencies
pip install -r backend/requirements.txt

# Run backend server
cd backend && uvicorn app.main:app --reload --port 8000

# Run all backend tests
cd backend && ../venv/Scripts/python.exe -m pytest tests/ -v

# Run specific test file
cd backend && ../venv/Scripts/python.exe -m pytest tests/test_search.py -v

# Run live OpenAlex API tests
cd backend && ../venv/Scripts/python.exe -m pytest tests/test_openalex_live.py -v -s
```

### Frontend (React + Vite + TypeScript)

```bash
# Install dependencies (from frontend directory)
cd frontend && npm install

# Run dev server (port 3000, proxies /api to localhost:8000)
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Lint
cd frontend && npm run lint

# Run E2E tests with Playwright
cd frontend && npx playwright test

# Run E2E tests with browser visible
cd frontend && npx playwright test --headed
```

## Architecture

### Backend Structure (`backend/`)
- `app/main.py` - FastAPI app entry point with CORS and router setup
- `app/api/v1/` - API endpoints (auth.py, search.py)
- `app/services/` - Business logic
  - `openalex_service.py` - Core search algorithm using OpenAlex API
  - `db_service.py` - Supabase database operations
- `app/core/` - Configuration and settings
- `app/models/` - Pydantic models
- `tests/` - pytest test suite

### Frontend Structure (`frontend/src/`)
- `pages/` - Login, SignUp, Search pages
- `components/` - Reusable components (JournalCard, ProtectedRoute)
- `contexts/` - React context providers
- `services/` - API client services
- `lib/` - Utility functions
- `types/` - TypeScript type definitions
- `tests/e2e/` - Playwright E2E tests

### External Services
- **Supabase**: PostgreSQL database + GoTrue authentication
- **OpenAlex API**: Academic journal and works data source
- **Railway**: Backend deployment
- **Vercel**: Frontend deployment

## Key Technical Details

### Search Algorithm
The search uses a "Soft Boost" approach - journals matching the user's discipline get boosted scores but results with strong topic matches are never hidden. This is implemented in `backend/app/services/openalex/search.py`.

**Score Normalization:** Relevance scores are normalized to 0-1 range before being sent to the frontend, which displays them as percentages (0-100%).

### Authentication Flow
- Supabase handles user auth via JWT tokens
- Backend validates tokens for protected endpoints
- Role-based access: free, paid, admin tiers
- Free users have rate limiting (5 searches/day)

### Privacy Feature
When `incognito_mode=True`, query text is NOT logged to the database.

## Current Features (What Actually Works)

### Data Source: OpenAlex API
- **Journal Discovery**: Search across academic journals indexed by OpenAlex
- **Topic Matching**: AI-powered matching based on research topics
- **Discipline Detection**: Automatic field/subfield detection using OpenAlex hierarchy
- **Multi-Language Support**: 40+ languages via OpenAlex's international coverage

### Available Journal Metrics
- **Journal H-Index**: Available from OpenAlex
- **Works Count**: Total publications in the journal
- **APC (Article Processing Charges)**: When available
- **Open Access Status**: OA detection

### Features NOT Available (Removed from UI)
- Impact Factor (requires Clarivate subscription)
- Acceptance Rates (not available via API)
- Estimated Publication Times (not available via API)
- Reference Manager Export (not implemented)

## Design System

### Academic Color Palette (Navy/Slate)
```css
/* Primary: Navy/Slate (Academic) */
--color-primary-50: #f8fafc;      /* Slate 50 - Background */
--color-primary-500: #4a6fa5;     /* Slate Blue - Secondary */
--color-primary-600: #1e3a5f;     /* Navy - Main brand */
--color-primary-700: #1a324f;     /* Dark Navy */

/* Accent: Teal */
--color-info: #0d9488;            /* Teal - Links, highlights */

/* Shadows */
--shadow-glow: 0 0 40px -10px var(--color-primary-600);
--shadow-navy: 0 4px 20px -5px rgba(30, 58, 95, 0.4);
```

### Key UI Classes
- Buttons: `bg-gradient-to-r from-slate-700 to-slate-800`
- Links: `text-teal-600 hover:text-teal-700`
- Inputs: `bg-slate-50 border-slate-200 focus:border-teal-500`
- Cards: `bg-white border-slate-200 shadow-slate-300`

## Coding Conventions

### Python (Backend)
- snake_case for variables and functions
- Pydantic models for request/response validation
- Services layer contains business logic separate from API routes

### TypeScript/React (Frontend)
- Functional components with hooks
- Tailwind CSS for styling
- React Router for navigation
## 🧠 Memory
- **Knowledge Base:** `PROJECT_MEMORY.md` (Read this first!)

## 🤖 Agents (Roles)
- **@orchestrator**: Project Lead & Coordinator (`.claude/agents/orchestrator.md`)
- **@backend-agent**: Python/FastAPI Specialist (`.claude/agents/backend-agent.md`)
- **@frontend-agent**: React/Vite Specialist (`.claude/agents/frontend-agent.md`)
- **@qa-agent**: Testing Specialist (`.claude/agents/qa-agent.md`)
- **@docs-agent**: Documentation (`.claude/agents/docs-agent.md`)
- **@devops-agent**: Deployment (`.claude/agents/devops-agent.md`)

## ⚡ Workflow Commands
- **/project:new-feature**: End-to-end feature build (`.claude/commands/new-feature.md`)
- **/project:refactor**: Clean up code debt (`.claude/commands/refactor.md`)
- **/project:fix-bug**: Structured debugging (`.claude/commands/fix-bug.md`)
- **/project:add-endpoint**: Add API endpoint with full stack sync (`.claude/commands/add-endpoint.md`)
- **/project:pre-deploy**: Deployment checklist (`.claude/commands/pre-deploy.md`)

## Recent Changes (December 17, 2024 Sprint)

### Bug Fixes
- **Match Score Bug (C1)**: Fixed display showing 2845% instead of 28%. Added score normalization to 0-1 range in backend.

### Removed False Claims
- "20,000+ Researchers" - replaced with "Powered by OpenAlex"
- "150+ Countries" - replaced with "40+ Languages Supported"
- "98% Accuracy" - replaced with "Instant Results"
- "2M+ Papers Analyzed" - replaced with OpenAlex attribution section

### UI/UX Updates
- Disabled distracting animated backgrounds on Login/SignUp pages
- Changed "H-Index" label to "Journal H-Index" for clarity
- Updated color palette from bright cyan/blue to academic navy/slate
- Removed non-existent features from landing page (Impact Factor, Publication Times, Reference Manager)