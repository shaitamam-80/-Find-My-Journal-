---
description: Complete workflow for developing a new feature with parallel execution support
allowed_tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# New Feature Development Workflow

## Feature Request
$ARGUMENTS

---

## Phase 1: Analysis (ultrathink)

Before ANY code:

```
ultrathink about this feature request:

1. SCOPE ANALYSIS
   - What tool does this affect? (Define/Query/Review)
   - Is this a new capability or enhancement?
   - What's the minimum viable implementation?

2. ARCHITECTURE IMPACT
   - Database changes required?
   - New API endpoints needed?
   - Frontend components required?
   - External service integrations?

3. DEPENDENCY MAPPING
   - What must be built first?
   - What can be built in parallel?
   - What existing code is affected?

4. RISK ASSESSMENT
   - What could go wrong?
   - What's the rollback plan?
   - Are there security implications?
```

**Output:** Write analysis to `.claude/logs/feature-analysis-{timestamp}.md`

---

## Phase 2: Planning

Create a feature plan document:

**File:** `docs/plans/feature-{name}-{date}.md`

```markdown
# Feature Plan: {Feature Name}

## Summary
{One paragraph description}

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Technical Design

### Database Changes
- [ ] New table: {name}
- [ ] New column: {table}.{column}
- [ ] Migration script needed: Yes/No

### Backend Changes
- [ ] New endpoint: {method} {path}
- [ ] Modified endpoint: {method} {path}
- [ ] New schema: {name}
- [ ] Service changes: {description}

### Frontend Changes
- [ ] New page: {path}
- [ ] New component: {name}
- [ ] API client method: {name}
- [ ] State management: {changes}

## Implementation Order
1. {Step 1} - Can parallel: Yes/No
2. {Step 2} - Can parallel: Yes/No
3. {Step 3} - Depends on: {steps}

## Testing Plan
- [ ] Unit tests for: {components}
- [ ] Integration tests for: {flows}
- [ ] Manual testing: {scenarios}

## Rollback Plan
{How to undo if problems occur}
```

**Wait for human approval before proceeding.**

---

## Phase 3: Setup

### If Parallel Development Possible:

Call @parallel-work-agent:

```
Set up parallel development for this feature:

Tasks that can run in parallel:
1. {Backend task description}
2. {Frontend task description}
3. {Other task description}

Dependencies:
- Task 3 depends on Task 1 completion
```

### If Sequential Development:

Create single feature branch:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/{feature-name}
```

---

## Phase 4: Implementation

### 4.1 Database Changes (if needed)

Call @db-migration-agent:

```
Create migration for:
- {table/column changes}

Risk level: {LOW/MEDIUM/HIGH}
```

**Wait for migration completion before backend work.**

### 4.2 Backend Implementation

For each backend component:

```
think hard about the implementation:

1. Read existing related code
2. Follow project patterns from CLAUDE.md
3. Implement with proper error handling
4. Use service layer (ai_service, db_service)
5. Add authentication where needed
```

**After each significant change:**
- Write to thinking log
- Run syntax check: `python -m py_compile {file}`

### 4.3 Frontend Implementation

For each frontend component:

```
think hard about the implementation:

1. Read existing related components
2. Follow project patterns
3. Use TypeScript properly
4. Handle loading/error states
5. Use API client from lib/api.ts
```

**After each significant change:**
- Write to thinking log
- Run type check: `npx tsc --noEmit`

---

## Phase 5: Validation Loop

After implementation:

```
┌─────────────────────────────────────────┐
│  Call @qa-agent                         │
├─────────────────────────────────────────┤
│  If issues found:                       │
│  → Fix issues                           │
│  → Return to @qa-agent                  │
│  → Repeat until APPROVED                │
├─────────────────────────────────────────┤
│  Call @api-sync-agent                   │
│  → Verify backend/frontend sync         │
│  → Fix any mismatches                   │
├─────────────────────────────────────────┤
│  Call @hebrew-validator (if Query tool) │
│  → Verify no Hebrew in queries          │
└─────────────────────────────────────────┘
```

---

## Phase 6: Documentation

Call @docs-agent:

```
Update documentation for new feature:

Feature: {name}

API Changes:
- {new/modified endpoints}

Database Changes:
- {new/modified tables}

Files Created:
- {list of new files}

Files Modified:
- {list of modified files}
```

---

## Phase 7: Pre-Merge Verification

Call @deploy-checker:

```
Verify deployment readiness for feature branch:
- Branch: feature/{feature-name}
- Target: develop
```

---

## Phase 8: Merge and Cleanup

### If Using Worktrees (Parallel Development):

Coordinate with @parallel-work-agent for merge sequence.

### If Single Branch:

```bash
# Ensure up to date
git checkout develop
git pull origin develop

# Merge feature
git merge feature/{feature-name}

# If conflicts, resolve and commit
# Then push
git push origin develop

# Cleanup
git branch -d feature/{feature-name}
```

---

## Phase 9: Post-Merge

1. **Verify on develop:**
   - Backend health check
   - Frontend builds
   - Key flows work

2. **Update thinking log:**
   - Final summary
   - Lessons learned
   - Time spent

3. **Close the loop:**
   - Mark plan document as completed
   - Archive thinking logs if needed

---

## Thinking Log Template for This Command

```markdown
# Feature Development Log
# Feature: {name}
# Started: {timestamp}
# Command: /project:new-feature {arguments}

## Phase 1: Analysis
### Timestamp: {time}
{ultrathink output}

## Phase 2: Planning
### Timestamp: {time}
- Plan document created: {path}
- Human approval: {pending/approved}

## Phase 3: Setup
### Timestamp: {time}
- Development mode: {parallel/sequential}
- Worktrees created: {list if parallel}
- Branch: {branch name}

## Phase 4: Implementation
### Timestamp: {time}

#### Database
- Migration: {status}
- Files: {list}

#### Backend
- Components implemented: {list}
- Issues encountered: {list}

#### Frontend
- Components implemented: {list}
- Issues encountered: {list}

## Phase 5: Validation
### Timestamp: {time}
- @qa-agent: {status}
- @api-sync-agent: {status}
- @hebrew-validator: {status if applicable}

## Phase 6: Documentation
### Timestamp: {time}
- @docs-agent: {status}
- CLAUDE.md updated: {yes/no}

## Phase 7: Pre-Merge
### Timestamp: {time}
- @deploy-checker: {status}

## Phase 8: Merge
### Timestamp: {time}
- Merged to: {branch}
- Conflicts: {none/resolved}
- Worktrees cleaned: {yes/no/na}

## Phase 9: Post-Merge
### Timestamp: {time}
- Verification: {pass/fail}
- Total time: {duration}
- Lessons learned: {notes}
```

