# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Find My Journal is a SaaS application that helps researchers discover academic journals for their papers. It uses a hybrid search algorithm combining keywords and topic matching via the OpenAlex API.

## Available Skills

Before starting work, read the relevant skill for best practices:

- **product-manager**: PRD templates, personas, competitive analysis → `.claude/skills/product-manager/SKILL.md`
- **frontend-dev**: React/TypeScript patterns, Tailwind, components → `.claude/skills/frontend-dev/SKILL.md`
- **backend-dev**: FastAPI, Python patterns, API design → `.claude/skills/backend-dev/SKILL.md`
- **database**: PostgreSQL, Supabase, data modeling → `.claude/skills/database/SKILL.md`
- **security-specialist**: Security best practices, vulnerability detection → `.claude/skills/security-specialist/SKILL.md`

### How to Use Skills

1. Read the SKILL.md file for the relevant task
2. Follow the patterns and best practices described
3. Check the `references/` folder for detailed examples

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

**Core directories:**
- `pages/` - Login, SignUp, Search pages
- `components/` - Reusable UI components
- `contexts/` - React Context providers (Auth, Theme)
- `services/` - API client services
- `lib/` - Utility functions
- `types/` - TypeScript type definitions
- `tests/e2e/` - Playwright E2E tests

**Feature modules (recommended structure):**

- `features/search/` - Search functionality
  - `SearchForm.tsx` - Abstract input + submit button
  - `AbstractValidator.tsx` - Word count/quality feedback before submission
- `features/results/` - Results display
  - `JournalCard.tsx` - Individual journal result card
  - `ResultsFeed.tsx` - List of journal results
  - `FilterSidebar.tsx` - Faceted filters (Open Access, etc.)
  - `MatchScore.tsx` - Visual match score indicator (ring/bar)

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
- **Google OAuth only**: All users must sign in with their Google account
- No email/password authentication available
- Supabase handles user auth via JWT tokens
- Backend validates tokens for protected endpoints
- Role-based access: free, paid, admin tiers
- Free users have rate limiting (5 searches/day)

**Google OAuth:**
- Users sign in/up exclusively with their Google account
- OAuth callback redirects to `/search` after successful authentication
- User metadata (name, email, picture) automatically populated from Google
- Simplified, secure authentication with no password management needed
- See "Google OAuth Configuration" section below for setup instructions

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

### Target User Persona: "The Stressed Scholar"

- **Profile:** Post-doc researcher, high anxiety regarding career, often working late
- **Cognitive State:** Expert in their field, novice in journal selection
- **Psychological Needs:**
  - **Reduction of Uncertainty:** Immediate validation that the system understood their abstract
  - **Efficiency:** Cannot waste time deciphering complex UI

### UX Principles

- **"Don't Make Me Think" (Krug):** Search interface must be simple - one box, one button
- **"Aesthetic-Usability Effect":** Clean, academic aesthetic increases trust in algorithm accuracy
- **"Defensive Design":** Handle bad input gracefully without shaming the user

### Design Tokens (HSL-based)
Located at `frontend/src/styles/design-tokens.css` - supports light/dark modes.

### Academic Color Palette (Navy/Slate)
```css
/* Primary: Navy/Slate (Academic) */
--color-primary-50: #f8fafc;      /* Slate 50 - Background */
--color-primary-500: #4a6fa5;     /* Slate Blue - Secondary */
--color-primary-600: #1e3a5f;     /* Navy - Main brand */
--color-primary-700: #1a324f;     /* Dark Navy */

/* Accent: Teal */
--color-info: #0d9488;            /* Teal - Links, highlights */

/* Journal Category Status Colors */
--status-top-tier: emerald        /* Green - Top journals */
--status-niche: blue              /* Blue - Niche specialists */
--status-methodology: purple      /* Purple - Methods focused */
--status-broad: amber             /* Amber - Broad scope */

/* Feedback Colors */
--color-success: #22c55e;         /* High Match / Good */
--color-warning: #f59e0b;         /* Medium Match / Check */
--color-destructive: #ef4444;     /* Predatory Flag / Error */
```

### Dark Mode Tokens
```css
.dark {
  --color-background: #0f172a;    /* Slate 900 */
  --color-foreground: #f8fafc;    /* Slate 50 */
  --color-surface: #1e293b;       /* Slate 800 */
  --color-border: #334155;        /* Slate 700 */
  --color-muted: #334155;         /* Slate 700 */
  --color-muted-foreground: #94a3b8; /* Slate 400 */
}
```

### MedAI Hub Visual Principles
- **ALL pages**: White (#FFFFFF) or Slate-50 (#F8FAFC) backgrounds only
- **ALL cards**: White with border (#E2E8F0), NO colored backgrounds
- **ONE accent color**: Teal-600 (#0D9488) for links and highlights
- **Primary buttons**: Slate-900 (#0F172A), solid color, NO gradients
- **NO cyan/blue gradients anywhere**

### Key UI Classes
- Page backgrounds: `bg-white` or `bg-slate-50`
- Buttons: `bg-slate-900 hover:bg-slate-800` (solid, no gradients)
- Links: `text-teal-600 hover:text-teal-700`
- Inputs: `bg-white border-slate-200 focus:border-teal-600 focus:ring-teal-100`
- Cards: `bg-white border border-slate-200 shadow-sm`
- Nav: `bg-white border-b border-slate-200`

### Typography
- **English:** Inter (400-700)
- **Hebrew:** Assistant (400-700)
- **Code:** JetBrains Mono (400-500)

### RTL Support (MANDATORY)

**All layout must use Tailwind logical properties for Hebrew/English support:**

- `ms-*` / `me-*` instead of `ml-*` / `mr-*` (margin)
- `ps-*` / `pe-*` instead of `pl-*` / `pr-*` (padding)
- `start-*` / `end-*` instead of `left-*` / `right-*` (positioning)
- `text-start` / `text-end` instead of `text-left` / `text-right`
- `rounded-s-*` / `rounded-e-*` instead of `rounded-l-*` / `rounded-r-*`
- `border-s-*` / `border-e-*` instead of `border-l-*` / `border-r-*`

**NEVER use directional classes** (`ml-`, `mr-`, `pl-`, `pr-`, `left-`, `right-`, `text-left`, `text-right`)

### Touch Targets & Accessibility

- **Minimum touch target:** 44px for all interactive elements
- **Spacing:** Generous density for scanning (comfortable, not compact)
- **Focus states:** Visible focus rings on all interactive elements

### Loading States

- Use `Skeleton` components during API processing
- Staggered fade-in for result lists (use `motion-safe:` wrapper)
- Pulse animation on submit button during loading

### Error UX Tone
**Use encouraging, helpful messages - not technical jargon:**

| Bad | Good |
| --- | --- |
| "Invalid Input" | "נדרש עוד טקסט לניתוח מדויק (מינימום 50 מילים)" |
| "Error 400" | "משהו השתבש. נסה שוב?" |
| "Rate limit exceeded" | "הגעת למגבלת החיפושים היומית. חזור מחר או שדרג לחשבון פרימיום" |
| "Network error" | "בעיית חיבור. בדוק את האינטרנט ונסה שוב" |

### Reusable Components
- `StatusBadge` - Journal category badges (top-tier, niche, methodology, broad)
- `MatchScoreBadge` - Color-coded match score display (high/medium/low)
- `ThemeToggle` - Dark/light mode toggle button
- `useDarkMode` hook - Dark mode state management
- `Skeleton` - Loading placeholder components

## Coding Conventions

### Python (Backend)
- snake_case for variables and functions
- Pydantic models for request/response validation
- Services layer contains business logic separate from API routes

### TypeScript/React (Frontend)
- Functional components with hooks
- Tailwind CSS for styling
- React Router for navigation

## Security Rules - NEVER BYPASS

### Database Security (Supabase)
- RLS is enabled on all tables - NEVER disable it
- Always add RLS policies when creating new tables
- Use `auth.uid()` for user-scoped queries
- NEVER expose `service_role` key in frontend code
- NEVER use `service_role` key for client-side operations

### API Keys & Secrets
- All secrets must be in environment variables
- Frontend: Use `VITE_` prefix (e.g., `VITE_SUPABASE_ANON_KEY`)
- Backend: Use `os.getenv()` or config module
- NEVER hardcode API keys in source code
- NEVER commit `.env` files to Git

### Safe Keys (OK to expose in frontend):
- `VITE_SUPABASE_URL` - Public project URL
- `VITE_SUPABASE_ANON_KEY` - Public anonymous key (RLS protects data)

### Secret Keys (Backend ONLY):
- `SUPABASE_SERVICE_ROLE_KEY` - Full database access
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` - AI service keys
- Any key starting with `sk-` or containing `secret`

### Input Validation
- Always validate user input with Pydantic (backend)
- Sanitize text inputs before database operations
- Use parameterized queries (Supabase client handles this)
- NEVER trust user input directly

### Before Every Commit
```bash
# Check for exposed secrets
grep -rn "eyJ\|sk-\|service_role" --include="*.ts" --include="*.tsx" --include="*.py" .
```

### Current Security Status
- [x] .gitignore excludes .env files
- [x] Frontend uses VITE_SUPABASE_ANON_KEY only
- [x] Backend keeps service_role in env vars
- [x] RLS policies implemented on user tables
- [x] Privacy-enhanced logging (query_hash instead of raw text)
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

### MedAI Hub Visual Consistency (Phase 3)
- Login/SignUp pages: Changed from dark slate gradients to light Slate-50 backgrounds
- Landing page: Removed ALL cyan/blue gradients, white cards with borders
- Goals section: Changed from dark blue gradient to Slate-50 background
- Standardized accent color to Teal-600 across all components
- Standardized primary buttons to Slate-900 (solid, no gradients)

### Google OAuth Integration (January 2026)
- **Exclusive authentication method**: Google OAuth only
- **Email/password removed**: All traditional email/password forms removed from UI
- **UI simplification**: Login/SignUp pages now show only "Continue with Google" button
- **Implementation**: Added `signInWithGoogle()` to AuthContext
- **User experience**: All users redirected to `/search` after Google authentication
- **Security benefit**: No password management, reduced attack surface

---

## Google OAuth Configuration

### Prerequisites
Before Google OAuth will work, you must configure it in both Google Cloud Console and Supabase Dashboard.

### Step 1: Google Cloud Console Setup

1. **Create/Select Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one

2. **Enable Google+ API**
   - Navigate to **APIs & Services** > **Library**
   - Search for "Google+ API" and click **Enable**

3. **Create OAuth Credentials**
   - Go to **APIs & Services** > **Credentials**
   - Click **+ CREATE CREDENTIALS** > **OAuth client ID**
   - Choose **Web application** as the application type

4. **Configure Authorized Redirect URIs**

   Add the following URIs:
   ```
   # Production
   https://<YOUR_SUPABASE_PROJECT_REF>.supabase.co/auth/v1/callback

   # Development (optional)
   http://localhost:54321/auth/v1/callback
   ```

   **To find your Supabase Project URL:**
   - Go to Supabase Dashboard > Settings > API
   - Copy the **Project URL** (e.g., `https://abcdefghijklmnop.supabase.co`)
   - The callback URL is: `https://abcdefghijklmnop.supabase.co/auth/v1/callback`

5. **Save Credentials**
   - After saving, you'll receive:
     - **Client ID** (e.g., `123456789-abc.apps.googleusercontent.com`)
     - **Client Secret** (e.g., `GOCSPX-xxxxxxxxxxxxx`)
   - **IMPORTANT**: Store these securely! You'll need them in the next step.

### Step 2: Supabase Dashboard Configuration

1. **Enable Google Provider**
   - Go to [Supabase Dashboard](https://app.supabase.com)
   - Select your project
   - Navigate to **Authentication** > **Providers**
   - Find **Google** in the list

2. **Add Credentials**
   - Toggle **Google enabled** to ON
   - Enter the **Client ID** from Google Cloud Console
   - Enter the **Client Secret** from Google Cloud Console
   - (Optional) Leave **Skip nonce check** disabled for better security
   - Click **Save**

3. **Verify Callback URL**
   - Confirm the **Callback URL (for OAuth)** matches what you entered in Google Console:
     ```
     https://<YOUR_PROJECT>.supabase.co/auth/v1/callback
     ```

### Step 3: Verify Implementation

The code is already implemented! Here's what was added:

**AuthContext** (`frontend/src/contexts/AuthContext.tsx:151-163`):
```typescript
const signInWithGoogle = async () => {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/search`,
      queryParams: {
        access_type: 'offline',
        prompt: 'consent',
      },
    },
  })
  return { error }
}
```

**Login/SignUp Pages**: Both pages now display "Continue with Google" as the primary authentication method, with email/password as a fallback.

### Step 4: Testing

1. **Local Testing** (optional):
   - Ensure `http://localhost:54321/auth/v1/callback` is in Google Console
   - Run `cd frontend && npm run dev`
   - Click "Continue with Google" on Login/SignUp page

2. **Production Testing**:
   - Deploy to Vercel/Railway
   - Click "Continue with Google"
   - Verify user appears in Supabase Dashboard > Authentication > Users

### Security Checklist

✅ **NEVER** commit Client Secret to Git
✅ **NEVER** expose Client Secret in frontend code
✅ **ALWAYS** use environment variables for secrets
✅ **VERIFY** redirect URIs match exactly between Google Console and Supabase
✅ **ENABLE** RLS policies on all database tables

### Troubleshooting

**Error: "redirect_uri_mismatch"**
- Solution: Ensure the callback URL in Google Console exactly matches your Supabase callback URL

**Error: "Access blocked: This app's request is invalid"**
- Solution: Verify the Client ID and Client Secret are correct in Supabase Dashboard

**User not created in database after OAuth**
- Solution: Check that your backend's `/auth/me` endpoint handles new OAuth users correctly