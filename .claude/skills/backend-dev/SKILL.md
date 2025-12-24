---
name: backend-dev
description: FastAPI + Python backend development specialist. Use when building APIs, endpoints, database integration, authentication, background tasks, or debugging Python backends. Includes Supabase server-side patterns, Pydantic validation, async operations, and Railway/Vercel deployment.
---

# Backend Dev Skill

FastAPI + Python specialist for modern API development.

## Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| Language | Python 3.11+ |
| Validation | Pydantic v2 |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth + JWT |
| Deployment | Railway / Vercel |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings & env vars
│   ├── dependencies.py      # Dependency injection
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── search.py        # /api/search endpoints
│   │   ├── auth.py          # /api/auth endpoints
│   │   └── users.py         # /api/users endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Pydantic request models
│   │   └── responses.py     # Pydantic response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── supabase.py      # Supabase client
│   │   ├── search.py        # Search business logic
│   │   └── external_api.py  # External API calls
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── requirements.txt
├── .env                     # NEVER commit!
└── .env.example
```

## FastAPI Basics

### App Setup

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import search, auth, users

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "My API"
    DEBUG: bool = False
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str  # Backend only!
    
    # External APIs
    OPENAI_API_KEY: str = ""
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### Router Pattern

```python
# app/routers/search.py
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.requests import SearchRequest
from app.models.responses import SearchResponse, JournalResult
from app.services.search import SearchService
from app.dependencies import get_current_user, get_search_service

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search_journals(
    request: SearchRequest,
    service: SearchService = Depends(get_search_service),
    user = Depends(get_current_user)  # Optional: remove if public
):
    """Search for matching journals based on title and abstract."""
    try:
        results = await service.search(request.title, request.abstract)
        return SearchResponse(results=results, count=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{search_id}")
async def get_search(search_id: str):
    """Get a previous search by ID."""
    # Implementation
    pass
```

## Pydantic Models

### Request Models

```python
# app/models/requests.py
from pydantic import BaseModel, Field, field_validator

class SearchRequest(BaseModel):
    title: str = Field(..., min_length=10, max_length=500)
    abstract: str = Field(..., min_length=50, max_length=5000)
    disciplines: list[str] = Field(default=[])
    
    @field_validator('title', 'abstract')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        # Remove potentially dangerous characters
        dangerous = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        for char in dangerous:
            v = v.replace(char, '')
        return v.strip()

class UserCreate(BaseModel):
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)
```

### Response Models

```python
# app/models/responses.py
from pydantic import BaseModel
from datetime import datetime

class JournalResult(BaseModel):
    id: str
    title: str
    publisher: str | None = None
    relevance_score: float
    explanation: str | None = None

class SearchResponse(BaseModel):
    results: list[JournalResult]
    count: int
    search_id: str | None = None

class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

## Supabase Integration

### Client Setup

```python
# app/services/supabase.py
from supabase import create_client, Client
from app.config import settings

def get_supabase_client() -> Client:
    """Get Supabase client with service role (full access)."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY  # Backend only!
    )

def get_supabase_anon_client() -> Client:
    """Get Supabase client with anon key (RLS enforced)."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )
```

### Database Operations

```python
# app/services/database.py
from app.services.supabase import get_supabase_client

async def get_user_searches(user_id: str, limit: int = 10):
    supabase = get_supabase_client()
    
    response = supabase.table("search_history") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()
    
    return response.data

async def save_search(user_id: str, query: str, results: list):
    supabase = get_supabase_client()
    
    response = supabase.table("search_history") \
        .insert({
            "user_id": user_id,
            "query": query,
            "results_count": len(results)
        }) \
        .execute()
    
    return response.data[0] if response.data else None
```

### Auth Verification

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, Header
from app.services.supabase import get_supabase_client

async def get_current_user(authorization: str = Header(...)):
    """Verify JWT and return user."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    
    token = authorization.replace("Bearer ", "")
    supabase = get_supabase_client()
    
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_optional_user(authorization: str = Header(default=None)):
    """Get user if authenticated, None otherwise."""
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
```

## Async Patterns

### External API Calls

```python
# app/services/external_api.py
import httpx
from app.config import settings

async def fetch_openalex_data(query: str) -> dict:
    """Fetch data from OpenAlex API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.openalex.org/works",
            params={"search": query, "per_page": 20},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

async def call_openai(prompt: str) -> str:
    """Call OpenAI API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            },
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
```

### Parallel Requests

```python
import asyncio

async def fetch_multiple_sources(query: str):
    """Fetch from multiple sources in parallel."""
    results = await asyncio.gather(
        fetch_openalex_data(query),
        fetch_other_source(query),
        return_exceptions=True  # Don't fail if one source fails
    )
    
    # Filter out exceptions
    valid_results = [r for r in results if not isinstance(r, Exception)]
    return valid_results
```

## Error Handling

### Exception Handlers

```python
# app/main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path,
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error (but don't expose details in production)
    print(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### Custom Exceptions

```python
# app/exceptions.py
class AppException(Exception):
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code

class NotFoundError(AppException):
    pass

class ValidationError(AppException):
    pass

class RateLimitError(AppException):
    pass
```

## Rate Limiting

```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def check(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > minute_ago
        ]
        
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Too many requests")
        
        self.requests[client_ip].append(now)

rate_limiter = RateLimiter(requests_per_minute=60)

# Usage in router
@router.post("/search")
async def search(request: Request):
    await rate_limiter.check(request)
    # ... rest of handler
```

## Background Tasks

```python
from fastapi import BackgroundTasks

async def log_search(user_id: str, query: str):
    """Background task to log search."""
    # This runs after response is sent
    await save_search_log(user_id, query)

@router.post("/search")
async def search(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    results = await perform_search(request)
    
    # Add background task
    background_tasks.add_task(log_search, user.id, request.title)
    
    return results
```

## Environment Variables

```bash
# .env.example
APP_NAME=My API
DEBUG=false

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # Keep secret!

# External APIs
OPENAI_API_KEY=sk-...

# CORS
ALLOWED_ORIGINS=["https://myapp.vercel.app"]
```

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| CORS errors | Check ALLOWED_ORIGINS includes frontend URL |
| 422 Validation Error | Check Pydantic model matches request body |
| Import errors | Use absolute imports: `from app.services...` |
| Async not working | Use `async def` + `await` consistently |
| Supabase RLS blocking | Use service_role key for backend |
| Timeout on external API | Add timeout parameter to httpx |

## Deployment

### Railway

```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
```

### Requirements

```txt
# requirements.txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
supabase>=2.0.0
httpx>=0.26.0
python-multipart>=0.0.6
```

## File References

- **API Patterns**: See `references/api-patterns.md`
- **Testing**: See `references/testing.md`
- **Security**: See `references/security.md`

## Quick Commands

```bash
# Run locally
uvicorn app.main:app --reload --port 8000

# Install dependencies
pip install -r requirements.txt

# Freeze dependencies
pip freeze > requirements.txt

# Type check
mypy app/

# Format
black app/
```
