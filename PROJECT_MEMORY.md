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
