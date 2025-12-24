# Backend Security Reference

## API Key Management

### Environment Variables

```python
# ✅ Correct - from environment
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_SERVICE_ROLE_KEY: str
    OPENAI_API_KEY: str
    
    class Config:
        env_file = ".env"

# ❌ NEVER do this
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### .env.example Template

```bash
# .env.example (commit this)
APP_NAME=MyApp
DEBUG=false

# Supabase (get from dashboard)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# External APIs
OPENAI_API_KEY=sk-...
```

### .gitignore

```gitignore
# Always include
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

## Input Validation

### Pydantic Sanitization

```python
from pydantic import BaseModel, field_validator
import re

class UserInput(BaseModel):
    title: str
    content: str
    
    @field_validator('title', 'content')
    @classmethod
    def sanitize(cls, v: str) -> str:
        # Remove HTML tags
        v = re.sub(r'<[^>]+>', '', v)
        # Remove SQL injection patterns
        dangerous = ['--', ';--', '/*', '*/', 'xp_', 'UNION', 'SELECT']
        for pattern in dangerous:
            v = v.replace(pattern, '')
        return v.strip()
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError('Title too short')
        if len(v) > 500:
            raise ValueError('Title too long')
        return v
```

### Path Parameter Validation

```python
from fastapi import Path
import re

@router.get("/users/{user_id}")
async def get_user(
    user_id: str = Path(..., pattern=r'^[a-f0-9-]{36}$')  # UUID only
):
    # user_id is guaranteed to be UUID format
    pass

@router.get("/files/{filename}")
async def get_file(
    filename: str = Path(..., pattern=r'^[\w\-\.]+$')  # Safe filename
):
    # Prevent path traversal
    if '..' in filename or '/' in filename:
        raise HTTPException(400, "Invalid filename")
    pass
```

## Authentication

### JWT Verification

```python
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Supabase verifies JWT automatically
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
```

### Role-Based Access

```python
from enum import Enum
from functools import wraps

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"

def require_role(required_role: Role):
    async def dependency(user = Depends(get_current_user)):
        if user.role != required_role and user.role != Role.ADMIN:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return dependency

# Usage
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin = Depends(require_role(Role.ADMIN))
):
    pass
```

## Rate Limiting

### IP-Based Limiting

```python
from collections import defaultdict
import time
from fastapi import Request, HTTPException

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    async def check(
        self, 
        request: Request, 
        limit: int = 60, 
        window: int = 60
    ):
        client_ip = request.client.host
        now = time.time()
        window_start = now - window
        
        # Clean old requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if t > window_start
        ]
        
        if len(self.requests[client_ip]) >= limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(window)}
            )
        
        self.requests[client_ip].append(now)

limiter = RateLimiter()

# Usage
@router.post("/search")
async def search(request: Request):
    await limiter.check(request, limit=10, window=60)  # 10 per minute
    pass
```

### User-Based Limiting

```python
async def check_user_quota(user_id: str, action: str):
    """Check if user has remaining quota."""
    supabase = get_supabase_client()
    
    # Get user's plan
    user = supabase.table("users") \
        .select("plan, daily_searches") \
        .eq("id", user_id) \
        .single() \
        .execute()
    
    limits = {
        "free": 5,
        "premium": 100,
        "admin": float("inf")
    }
    
    if user.data["daily_searches"] >= limits[user.data["plan"]]:
        raise HTTPException(429, "Daily quota exceeded")
    
    # Increment counter
    supabase.table("users") \
        .update({"daily_searches": user.data["daily_searches"] + 1}) \
        .eq("id", user_id) \
        .execute()
```

## CORS Security

```python
from fastapi.middleware.cors import CORSMiddleware

# Production settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.vercel.app",
        "https://www.myapp.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,  # Cache preflight for 10 minutes
)

# ❌ NEVER in production
allow_origins=["*"]
```

## Security Headers

```python
from fastapi import Response

@app.middleware("http")
async def add_security_headers(request, call_next):
    response: Response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response
```

## Logging Security Events

```python
import logging
from datetime import datetime

# Security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

async def log_security_event(
    event_type: str,
    user_id: str = None,
    ip: str = None,
    details: dict = None
):
    security_logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "user_id": user_id,
        "ip": ip,
        "details": details
    })

# Usage
@router.post("/auth/login")
async def login(request: Request, credentials: LoginRequest):
    try:
        user = await authenticate(credentials)
        await log_security_event(
            "LOGIN_SUCCESS",
            user_id=user.id,
            ip=request.client.host
        )
        return user
    except AuthError:
        await log_security_event(
            "LOGIN_FAILED",
            ip=request.client.host,
            details={"email": credentials.email}
        )
        raise HTTPException(401, "Invalid credentials")
```

## Secrets in Responses

```python
from pydantic import BaseModel, field_serializer

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    password_hash: str = None  # Exclude from response
    
    class Config:
        # Exclude sensitive fields
        fields = {
            'password_hash': {'exclude': True}
        }

# Or use separate models
class UserInDB(BaseModel):
    id: str
    email: str
    password_hash: str

class UserPublic(BaseModel):
    id: str
    email: str
    name: str

# Convert before returning
@router.get("/users/{id}")
async def get_user(id: str) -> UserPublic:
    user_db = await get_user_from_db(id)
    return UserPublic(**user_db.dict())
```

## Security Checklist

### Before Deployment

- [ ] All secrets in environment variables
- [ ] `.env` in `.gitignore`
- [ ] CORS configured for specific origins
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] JWT verification working
- [ ] No sensitive data in responses
- [ ] Security headers added
- [ ] Logging for auth events
- [ ] HTTPS enforced (via Railway/Vercel)

### Code Review

- [ ] No hardcoded secrets
- [ ] No `allow_origins=["*"]` in production
- [ ] All user input sanitized
- [ ] SQL queries parameterized (Supabase handles this)
- [ ] File uploads validated
- [ ] Path parameters validated
