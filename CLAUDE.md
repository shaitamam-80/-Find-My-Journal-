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
The search uses a "Soft Boost" approach - journals matching the user's discipline get boosted scores but results with strong topic matches are never hidden. This is implemented in `openalex_service.py`.

### Authentication Flow
- Supabase handles user auth via JWT tokens
- Backend validates tokens for protected endpoints
- Role-based access: free, paid, admin tiers
- Free users have rate limiting (5 searches/day)

### Privacy Feature
When `incognito_mode=True`, query text is NOT logged to the database.

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