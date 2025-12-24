# API Patterns Reference

## RESTful Endpoint Conventions

### URL Structure

```
GET    /api/resources          # List all
GET    /api/resources/{id}     # Get one
POST   /api/resources          # Create
PUT    /api/resources/{id}     # Update (full)
PATCH  /api/resources/{id}     # Update (partial)
DELETE /api/resources/{id}     # Delete
```

### Query Parameters

```python
@router.get("/journals")
async def list_journals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    search: str = Query(None),
    discipline: str = Query(None),
):
    # Build query based on parameters
    pass
```

### Response Structure

```python
# Standard success response
{
    "data": [...],
    "meta": {
        "page": 1,
        "limit": 20,
        "total": 150,
        "total_pages": 8
    }
}

# Error response
{
    "detail": "Resource not found",
    "code": "NOT_FOUND",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Pagination Pattern

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

async def paginate(
    query,  # Supabase query
    page: int,
    limit: int
) -> PaginatedResponse:
    offset = (page - 1) * limit
    
    # Get total count
    count_response = query.count().execute()
    total = count_response.count
    
    # Get paginated data
    data_response = query \
        .range(offset, offset + limit - 1) \
        .execute()
    
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        data=data_response.data,
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
```

## Dependency Injection

### Service Dependencies

```python
# app/dependencies.py
from functools import lru_cache
from app.services.search import SearchService
from app.services.supabase import get_supabase_client

@lru_cache()
def get_search_service() -> SearchService:
    return SearchService(get_supabase_client())

# Usage in router
@router.post("/search")
async def search(
    request: SearchRequest,
    service: SearchService = Depends(get_search_service)
):
    return await service.search(request)
```

### Database Session

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db():
    client = get_supabase_client()
    try:
        yield client
    finally:
        # Cleanup if needed
        pass

# Usage
async def get_user(user_id: str):
    async with get_db() as db:
        return db.table("users").select("*").eq("id", user_id).single().execute()
```

## File Upload

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    # Validate file type
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, "File type not allowed")
    
    # Validate file size (5MB)
    max_size = 5 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(400, "File too large")
    
    # Upload to Supabase Storage
    supabase = get_supabase_client()
    path = f"{user.id}/{file.filename}"
    
    response = supabase.storage \
        .from_("uploads") \
        .upload(path, content, {"content-type": file.content_type})
    
    return {"path": path, "size": len(content)}
```

## Caching

```python
from functools import lru_cache
import time

# Simple in-memory cache
_cache = {}
_cache_ttl = {}

def cache_get(key: str):
    if key in _cache:
        if time.time() < _cache_ttl[key]:
            return _cache[key]
        else:
            del _cache[key]
            del _cache_ttl[key]
    return None

def cache_set(key: str, value, ttl_seconds: int = 300):
    _cache[key] = value
    _cache_ttl[key] = time.time() + ttl_seconds

# Usage
async def get_journal(journal_id: str):
    cache_key = f"journal:{journal_id}"
    
    # Try cache first
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    # Fetch from database
    result = await fetch_journal_from_db(journal_id)
    
    # Cache for 5 minutes
    cache_set(cache_key, result, ttl_seconds=300)
    
    return result
```

## Webhooks

```python
import hmac
import hashlib

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    payload = await request.body()
    
    # Verify signature
    expected_sig = hmac.new(
        settings.STRIPE_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(stripe_signature, f"sha256={expected_sig}"):
        raise HTTPException(400, "Invalid signature")
    
    # Process webhook
    event = json.loads(payload)
    
    if event["type"] == "checkout.session.completed":
        await handle_checkout_completed(event["data"]["object"])
    
    return {"received": True}
```

## API Versioning

```python
# Option 1: URL versioning
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

# Option 2: Header versioning
@router.get("/resource")
async def get_resource(
    api_version: str = Header(default="1", alias="X-API-Version")
):
    if api_version == "2":
        return get_resource_v2()
    return get_resource_v1()
```

## Streaming Responses

```python
from fastapi.responses import StreamingResponse

async def generate_csv(data: list):
    """Generate CSV content line by line."""
    yield "id,name,value\n"
    for item in data:
        yield f"{item['id']},{item['name']},{item['value']}\n"

@router.get("/export/csv")
async def export_csv():
    data = await get_all_data()
    return StreamingResponse(
        generate_csv(data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"}
    )
```

## Long-Running Tasks

```python
from uuid import uuid4

# In-memory task storage (use Redis in production)
tasks = {}

@router.post("/tasks")
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid4())
    tasks[task_id] = {"status": "pending", "result": None}
    
    background_tasks.add_task(run_long_task, task_id, request)
    
    return {"task_id": task_id, "status_url": f"/tasks/{task_id}"}

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    return tasks[task_id]

async def run_long_task(task_id: str, request: TaskRequest):
    try:
        tasks[task_id]["status"] = "running"
        result = await perform_heavy_computation(request)
        tasks[task_id] = {"status": "completed", "result": result}
    except Exception as e:
        tasks[task_id] = {"status": "failed", "error": str(e)}
```
