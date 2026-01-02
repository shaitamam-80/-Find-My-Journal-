---
description: Add a new API endpoint with synchronized backend and frontend implementation
allowed_tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Add API Endpoint Workflow

## Prerequisites

Read project configuration:

```bash
cat .claude/PROJECT.yaml
```

Use configuration values throughout this command.

## Endpoint Specification

$ARGUMENTS

---

## Phase 1: Specification (think hard)

```
think hard about this endpoint:

1. ENDPOINT DETAILS
   - HTTP Method: GET/POST/PATCH/DELETE
   - Path: /api/v1/{resource}/{action}
   - Authentication: Required/Optional
   - Purpose: {what it does}

2. REQUEST SPECIFICATION
   - Path parameters: {list}
   - Query parameters: {list}
   - Request body: {schema}

3. RESPONSE SPECIFICATION
   - Success response: {schema}
   - Success status code: 200/201/204
   - Error responses: {codes and when}

4. BUSINESS LOGIC
   - Validation rules
   - Data transformations
   - Side effects (emails, logs, etc.)

5. DATABASE INTERACTION
   - Tables involved
   - Operations: SELECT/INSERT/UPDATE/DELETE
   - Transactions needed?
```

**Output:** Document specification in thinking log.

---

## Phase 2: Database (if needed)

If new tables/columns required, call @db-migration-agent:

```
Create database changes for new endpoint:
- Table: {name}
- Columns: {list}
- Indexes: {list}
- Constraints: {list}
```

**Wait for migration completion.**

---

## Phase 3: Backend Implementation

### 3.1 Create/Update Pydantic Schemas

**File:** `{paths.models}/schemas.py`

```python
# Request model
class {Name}Request(BaseModel):
    """Request body for {endpoint description}."""
    field1: str = Field(..., description="Description")
    field2: Optional[int] = Field(None, description="Optional field")

    class Config:
        json_schema_extra = {
            "example": {
                "field1": "example value",
                "field2": 123
            }
        }

# Response model
class {Name}Response(BaseModel):
    """Response for {endpoint description}."""
    id: str
    field1: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### 3.2 Create Route Handler

**File:** `{paths.api_routes}/{resource}.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.services.database import db_service
from app.api.models.schemas import {Name}Request, {Name}Response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{path}", response_model={Name}Response)
async def {function_name}(
    request: {Name}Request,
    current_user: dict = Depends(get_current_user)
) -> {Name}Response:
    """
    {Endpoint description}.

    - **request.field1**: Description of field1
    - **request.field2**: Description of field2

    Returns the created/retrieved resource.

    Raises:
        HTTPException 400: If validation fails
        HTTPException 401: If not authenticated
        HTTPException 404: If resource not found
    """
    try:
        # Validate input
        if not request.field1:
            raise HTTPException(status_code=400, detail="field1 is required")

        # Business logic
        result = await db_service.{operation}(
            user_id=current_user["id"],
            data=request.model_dump()
        )

        if not result:
            raise HTTPException(status_code=404, detail="Resource not found")

        return {Name}Response(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"{function_name} failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 3.3 Register Route (if new router)

**File:** `{stack.backend.path}/app/main.py`

```python
from app.api.routes.{resource} import router as {resource}_router

app.include_router({resource}_router, prefix="/api/v1", tags=["{Resource}"])
```

### 3.4 Add Service Method (if needed)

**File:** `{paths.services}/{service}.py`

```python
async def {operation}(self, user_id: str, data: dict) -> dict:
    """
    {Description of what this does}.

    Args:
        user_id: The authenticated user's ID
        data: The request data

    Returns:
        The created/retrieved record

    Raises:
        Exception: If database operation fails
    """
    result = await self.client.table("{table}").{operation}(data).execute()
    return result.data[0] if result.data else None
```

### 3.5 Verify Backend

```bash
cd {stack.backend.path}
python -m py_compile app/api/routes/{resource}.py
python -m py_compile app/api/models/schemas.py
uvicorn {stack.backend.entry_point} --reload --port {stack.backend.port}  # Start and test
```

---

## Phase 4: Frontend Implementation

### 4.1 Add TypeScript Interfaces

**File:** `{paths.types}` or `{paths.api_service}`

```typescript
// Request type
export interface {Name}Request {
  field1: string;
  field2?: number;
}

// Response type
export interface {Name}Response {
  id: string;
  field1: string;
  created_at: string;
}
```

### 4.2 Add API Client Method

**File:** `{paths.api_service}`

```typescript
/**
 * {Description of what this does}
 * @param data - The request payload
 * @returns The response data
 * @throws AxiosError if request fails
 */
export const {functionName} = async (data: {Name}Request): Promise<{Name}Response> => {
  const response = await client.post<{Name}Response>('/api/v1/{path}', data);
  return response.data;
};

// For GET with path param
export const get{Name} = async (id: string): Promise<{Name}Response> => {
  const response = await client.get<{Name}Response>(`/api/v1/{path}/${id}`);
  return response.data;
};

// For GET with query params
export const list{Name} = async (params?: { status?: string }): Promise<{Name}Response[]> => {
  const response = await client.get<{Name}Response[]>('/api/v1/{path}', { params });
  return response.data;
};
```

### 4.3 Add Error Handling in UI Component

**File:** Relevant page in `{paths.pages}` or component in `{paths.components}`

```typescript
import { {functionName} } from '{paths.api_service}';
import { useState } from 'react';

const Component = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: {Name}Request) => {
    setLoading(true);
    setError(null);

    try {
      const result = await {functionName}(data);
      // Handle success
    } catch (err) {
      if (axios.isAxiosError(err)) {
        switch (err.response?.status) {
          case 400:
            setError('Invalid input: ' + err.response.data.detail);
            break;
          case 401:
            // Redirect to login handled by interceptor
            break;
          case 404:
            setError('Resource not found');
            break;
          default:
            setError('Something went wrong. Please try again.');
        }
      } else {
        setError('Network error. Please check your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  // ... rest of component
};
```

### 4.4 Verify Frontend

```bash
cd {stack.frontend.path}
npx tsc --noEmit  # Type check
{stack.frontend.build_command}  # Build check
```

---

## Phase 5: Validation

### 5.1 Call @api-sync-agent

```
Verify sync for new endpoint:
- Method: {method}
- Path: /api/v1/{path}
- Backend file: {paths.api_routes}/{resource}.py
- Frontend file: {paths.api_service}
```

### 5.2 Call @qa-agent

```
Review new endpoint:
- Endpoint: {method} /api/v1/{path}
- Purpose: {description}
- Files: {list}
```

### 5.3 Call @hebrew-validator (if Query-related and conventions.primary_language == hebrew)

```
Validate endpoint for content:
- Endpoint: {path}
- Type: {input/output}
```

---

## Phase 6: Documentation

Call @docs-agent:

```
Add documentation for new endpoint:

## API Reference Addition

### {METHOD} /api/v1/{path}

{Description}

**Authentication:** Required

**Request Body:**
```json
{example}
```

**Response ({status}):**
```json
{example}
```

**Errors:**
- `400` - {when}
- `401` - Not authenticated
- `404` - {when}
```

---

## Phase 7: Integration Test

```
Test the full flow:

1. Start backend: cd {stack.backend.path} && uvicorn {stack.backend.entry_point} --reload --port {stack.backend.port}
2. Start frontend: cd {stack.frontend.path} && npm run dev
3. Test endpoint via UI or curl
4. Verify response matches specification
5. Test error cases
```

---

## Thinking Log Template for This Command

```markdown
# Add Endpoint Log
# Endpoint: {METHOD} /api/v1/{path}
# Started: {timestamp}
# Command: /project:add-endpoint {arguments}

## Phase 1: Specification
### Timestamp: {time}

### Endpoint Details
- Method: {GET/POST/PATCH/DELETE}
- Path: /api/v1/{path}
- Auth: {Required/Optional}
- Purpose: {description}

### Request Schema
```json
{schema}
```

### Response Schema
```json
{schema}
```

### Error Codes
- 400: {when}
- 401: {when}
- 404: {when}
- 500: {when}

## Phase 2: Database
### Timestamp: {time}

- Changes needed: {yes/no}
- Migration: {file path if created}

## Phase 3: Backend
### Timestamp: {time}

### Files Created/Modified
- schemas.py: {changes}
- {resource}.py: {changes}
- main.py: {changes if router added}
- {service}.py: {changes if needed}

### Verification
- Syntax check: {pass/fail}
- Server starts: {pass/fail}

## Phase 4: Frontend
### Timestamp: {time}

### Files Created/Modified
- {paths.api_service}: Added {functionName}
- {paths.types}: Added {interface names}
- Component: {changes if made}

### Verification
- Type check: {pass/fail}
- Build: {pass/fail}

## Phase 5: Validation
### Timestamp: {time}

- @api-sync-agent: {status}
- @qa-agent: {status}
- @hebrew-validator: {status/na}

## Phase 6: Documentation
### Timestamp: {time}

- @docs-agent: {status}
- CLAUDE.md updated: {yes/no}

## Phase 7: Testing
### Timestamp: {time}

### Test Results
| Test | Result |
|------|--------|
| Success case | {pass/fail} |
| 400 error | {pass/fail} |
| 401 error | {pass/fail} |
| 404 error | {pass/fail} |

## Summary
### Total Time: {duration}
### Files Changed: {count}
### Ready for Merge: {yes/no}
```
