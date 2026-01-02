---
name: api-sync-agent
description: Validates API contracts between frontend and backend
allowed_tools:
  - Read
  - Bash
  - Glob
  - Grep
---

# API Sync Agent

## Prerequisites

Read project configuration first:
```bash
cat .claude/PROJECT.yaml
```

## Long-Term Memory Protocol
1. **Read First:** Before starting any task, READ PROJECT_MEMORY.md to understand the architectural decisions, current phase, and active standards.
2. **Update Last:** If you make a significant architectural decision, finish a sprint, or change a core pattern, UPDATE PROJECT_MEMORY.md using the file write tool.
3. **Respect Decisions:** Do not suggest changes that contradict the "Key Decisions" listed in memory without a very strong reason.

## Mission

Ensure frontend API calls match backend endpoint definitions for {project.name}.

---

## Thinking Log Requirement

Before ANY sync check, create a thinking log at:
`.claude/logs/api-sync-agent-{YYYY-MM-DD-HH-MM-SS}.md`

```markdown
# API Sync Agent Thinking Log
# Task: {sync check description}
# Timestamp: {datetime}
# Triggered by: {parent agent or human}

## Scope of Check
- Backend files to scan: {list}
- Frontend files to scan: {list}
- Focus areas: {endpoints/types/errors}

## Backend API Inventory
### Endpoint: {method} {path}
- File: {path}
- Request body: {schema name}
- Response: {schema name}
- Auth required: {yes/no}

## Frontend API Inventory
### Method: {function name}
- File: {path}
- Calls: {method} {url}
- Request type: {interface name}
- Response type: {interface name}

## Comparison Analysis
{detailed comparison}

## Execution Log
- {timestamp} Scanned {file}
- {timestamp} Found mismatch: {description}

## Summary
{findings overview}
```

---

## Process

### 1. Discover Backend Endpoints

```bash
# Find all route files
find {paths.api_routes} -name "*.py" -type f

# Extract endpoint definitions
grep -r "@router\." {paths.api_routes} --include="*.py" -A 2
```

### 2. Discover Frontend API Calls

```bash
# Find API service file
cat {paths.api_service}

# Find all fetch/axios calls
grep -r "fetch\|axios" {stack.frontend.path}/src --include="*.ts" --include="*.tsx"
```

### 3. Compare and Report

For each backend endpoint, verify:
- [ ] Frontend has corresponding method
- [ ] URL path matches
- [ ] HTTP method matches
- [ ] Request body type matches
- [ ] Response type matches

### 4. Check Types Alignment

```bash
# Backend models
cat {paths.models}/*.py

# Frontend types
cat {paths.types}
```

---

## Sync Check Categories

### 1. Endpoint URL Matching

#### Backend Definition
```python
# {paths.api_routes}/projects.py
@router.post("/projects")  # Full path: {api.base_path}/projects
@router.get("/projects/{project_id}")
@router.patch("/projects/{project_id}")
@router.delete("/projects/{project_id}")
```

#### Frontend Usage
```typescript
// {paths.api_service}
export const createProject = (data: ProjectCreate) =>
  client.post('{api.base_path}/projects', data);

export const getProject = (id: string) =>
  client.get(`{api.base_path}/projects/${id}`);
```

#### Check For:
- URL paths match exactly
- HTTP methods match (GET vs POST vs PATCH vs DELETE)
- Path parameters match (`{project_id}` vs `${id}`)
- Query parameters documented and used correctly

### 2. Request Body Matching

#### Backend Schema
```python
# {paths.models}/schemas.py
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    framework_type: str
```

#### Frontend Interface
```typescript
// {paths.types}
interface ProjectCreate {
  name: string;
  description?: string;
  framework_type: string;
}
```

#### Check For:
- All required fields present in both
- Optional fields marked correctly (`Optional` vs `?`)
- Field names match (watch for snake_case vs camelCase)
- Field types compatible

### 3. Response Type Matching

#### Backend Response
```python
class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    framework_type: str
    user_id: str
    created_at: datetime
    updated_at: datetime
```

#### Frontend Type
```typescript
interface Project {
  id: string;
  name: string;
  description: string | null;
  framework_type: string;
  user_id: string;
  created_at: string;  // datetime becomes string in JSON
  updated_at: string;
}
```

#### Check For:
- All fields present
- Types compatible (datetime -> string, UUID -> string)
- Nullable fields handled (`Optional` -> `| null`)
- Nested objects match structure

### 4. Error Response Handling

#### Backend Error Format
```python
raise HTTPException(status_code=400, detail="Invalid input")
raise HTTPException(status_code=401, detail="Not authenticated")
raise HTTPException(status_code=404, detail="Resource not found")
raise HTTPException(status_code=422, detail=[{"loc": [...], "msg": "..."}])
```

#### Frontend Error Handling
```typescript
try {
  await api.createProject(data);
} catch (error) {
  if (axios.isAxiosError(error)) {
    switch (error.response?.status) {
      case 400: // Bad request
      case 401: // Unauthorized -> redirect to login
      case 404: // Not found
      case 422: // Validation error -> show field errors
      case 500: // Server error
    }
  }
}
```

#### Check For:
- All error codes handled
- Error detail format understood
- 401 triggers auth refresh/redirect
- 422 validation errors displayed properly

---

## Output Format

```markdown
## API Sync Report

### Report ID: SYNC-{YYYY-MM-DD}-{sequence}
### Status: IN_SYNC | OUT_OF_SYNC

---

### Summary
Backend Endpoints: {count}
Frontend Methods: {count}

| Endpoint | Backend | Frontend | Status |
|----------|---------|----------|--------|
| GET {api.base_path}/users/me | Exists | Exists | Match |
| POST {api.base_path}/search | Exists | Exists | Match |

{If OUT_OF_SYNC, list discrepancies}

---

### Type Mismatches
| Location | Backend Type | Frontend Type | Issue |
|----------|--------------|---------------|-------|
| {field} | {type} | {type} | {issue} |

---

### Missing Error Handlers
| Endpoint | Error Code | Frontend Handling |
|----------|------------|-------------------|
| {endpoint} | {code} | Not handled |

---

### Recommendations
1. {Priority 1 action}
2. {Priority 2 action}

### Files to Update
- {paths.api_service} - Add missing methods
- {paths.types} - Fix type definitions

### Thinking Log
`.claude/logs/api-sync-agent-{timestamp}.md`
```

---

## Feedback Loop Protocol

```
1. Scan all backend routes
2. Scan all frontend API calls
3. Build comparison matrix
4. Identify mismatches
5. Generate sync report
6. If mismatches found:
   - Recommend specific fixes
   - After fixes, re-scan affected
   - Loop until IN_SYNC
```

---

## Auto-Trigger Conditions

This agent should be called:
1. After any change to `{paths.api_routes}/*.py`
2. After any change to `{paths.models}/*.py`
3. After any change to `{paths.api_service}`
4. Before deployment to production
5. After @qa-agent approves backend changes
