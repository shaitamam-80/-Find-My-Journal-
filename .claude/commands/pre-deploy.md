---
description: Complete pre-deployment verification checklist
allowed_tools:
  - Read
  - Bash
  - Glob
  - Grep
---

# Pre-Deployment Verification

## Prerequisites

Read project configuration:

```bash
cat .claude/PROJECT.yaml
```

Use configuration values throughout this command.

## Deployment Target

$ARGUMENTS

Default: Production ({deployment.backend.platform} + {deployment.frontend.platform})

---

## Phase 1: Preparation

```
think about deployment context:

1. What has changed since last deployment?
2. Are there database migrations to apply?
3. Are there new environment variables?
4. Is this a hotfix or regular release?
```

### Gather Deployment Info

```bash
# Current branch
git branch --show-current

# Changes since last deploy (compare with {deployment.backend.auto_deploy_branch})
git log {deployment.backend.auto_deploy_branch}..HEAD --oneline

# Files changed
git diff {deployment.backend.auto_deploy_branch} --name-only
```

**Document in thinking log.**

---

## Phase 2: Run Full Agent Suite

### 2.1 Quality Assurance

Call @qa-agent:

```
Full QA review for deployment:
- Branch: {current branch}
- Target: {production/staging}
- Focus: All changes since last deploy
```

**Must pass before continuing.**

### 2.2 API Synchronization

Call @api-sync-agent:

```
Verify API sync for deployment:
- Check all endpoints
- Verify request/response types
- Confirm error handling
```

**Must show IN_SYNC before continuing.**

### 2.3 Content Validation (if conventions.primary_language requires)

Call @hebrew-validator (if applicable):

```
Validate all query-related code for content:
- Query generation endpoints
- Framework data handling
- Response content
```

**Must show CLEAN before continuing.**

### 2.4 Documentation Currency

Call @docs-agent:

```
Verify documentation is current:
- CLAUDE.md matches code
- Recent Changes Log updated
- API Reference accurate
```

---

## Phase 3: Build Verification

### 3.1 Backend Build Test

```bash
cd {stack.backend.path}

# Syntax check all Python files
find . -name "*.py" -exec python -m py_compile {} \;

# Check for common issues
grep -r "DEBUG = True" . --include="*.py" && echo "⚠️ DEBUG=True found!"
grep -r "localhost" . --include="*.py" | grep -v "# " | grep -v "0.0.0.0"

# Verify Dockerfile (if exists)
if [ -f Dockerfile ]; then
  cat Dockerfile
  docker build -t {project.slug}-backend-test . 2>&1 | tail -20
fi
```

### 3.2 Frontend Build Test

```bash
cd {stack.frontend.path}

# Type check
npx tsc --noEmit

# Production build
{stack.frontend.build_command}

# Check for issues
grep -r "localhost" . --include="*.ts" --include="*.tsx" | grep -v node_modules
grep -r "console.log" . --include="*.ts" --include="*.tsx" | grep -v node_modules
```

---

## Phase 4: Environment Verification

### 4.1 Backend Environment Variables

**Required in {deployment.backend.platform}:**

```
Variable                    Status    Notes
─────────────────────────────────────────────────
{environment.backend.required variables}
DEBUG                      [ ]       Must be False
```

**Verification:**
```python
# Check config defaults
# DEBUG should default to False
# No hardcoded keys
```

### 4.2 Frontend Environment Variables

**Required in {deployment.frontend.platform}:**

```
Variable                        Status    Notes
─────────────────────────────────────────────────────
{stack.frontend.env_prefix}API_URL            [ ]       Production backend URL
{stack.frontend.env_prefix}SUPABASE_URL       [ ]       Database project URL
{stack.frontend.env_prefix}SUPABASE_ANON_KEY  [ ]       Database anon key
```

---

## Phase 5: Database Verification

### 5.1 Schema Check

```bash
# Compare local schema with docs
ls -la {stack.database.migrations_path}/
```

### 5.2 Migration Status

```
Check:
- [ ] All migrations in {stack.database.migrations_path}/ have been applied
- [ ] Schema matches production
- [ ] No pending migrations
```

### 5.3 Data Integrity

```
Check:
- [ ] Foreign key constraints valid
- [ ] Required indexes exist
- [ ] No orphaned records (if possible to check)
```

---

## Phase 6: Full Deployment Checker

Call @deploy-checker:

```
Run complete deployment readiness check:
- Environment: production
- Backend: {deployment.backend.platform}
- Frontend: {deployment.frontend.platform}
- Database: {stack.database.provider}
```

**Review report and address any issues.**

---

## Phase 7: Pre-Deployment Checklist

### Mandatory (All Must Pass)

```
Backend:
- [ ] Python syntax check passes
- [ ] No DEBUG=True in production code
- [ ] No hardcoded secrets
- [ ] Dockerfile builds successfully (if applicable)
- [ ] Health endpoint exists and works
- [ ] CORS allows production frontend domain

Frontend:
- [ ] TypeScript check passes
- [ ] Production build succeeds
- [ ] No localhost URLs
- [ ] API URL from environment variable

Database:
- [ ] Schema is current
- [ ] Migrations applied
- [ ] Indexes exist

Integration:
- [ ] @api-sync-agent shows IN_SYNC
- [ ] @qa-agent shows APPROVED
- [ ] Content validation shows CLEAN (if applicable)

Documentation:
- [ ] CLAUDE.md updated
- [ ] Recent Changes Log entry added
```

### Recommended (Should Pass)

```
- [ ] No console.log in frontend
- [ ] No print() in backend (use logging)
- [ ] All new endpoints documented
- [ ] Test coverage maintained
```

---

## Phase 8: Deployment Decision

### GO Decision

All mandatory checks pass. Proceed with deployment.

```
Deployment Plan:
1. Merge to {deployment.backend.auto_deploy_branch}
2. {deployment.backend.platform} auto-deploys backend
3. {deployment.frontend.platform} auto-deploys frontend
4. Verify health endpoints
5. Test key user flows
6. Monitor for errors
```

### NO-GO Decision

Some checks failed. Address issues.

```
Blocking Issues:
1. {Issue 1} - {How to fix}
2. {Issue 2} - {How to fix}

Action:
- Fix issues
- Re-run /project:pre-deploy
```

---

## Phase 9: Deployment Execution

If GO decision:

### 9.1 Merge

```bash
# Ensure up to date
git checkout develop
git pull origin develop

# If feature branch, merge
git merge feature/{name}

# Push to trigger deployment
git push origin develop

# For production
git checkout {deployment.backend.auto_deploy_branch}
git merge develop
git push origin {deployment.backend.auto_deploy_branch}
```

### 9.2 Monitor Deployment

```
{deployment.backend.platform}:
- Watch build logs
- Verify deployment completes
- Check health endpoint: {production_backend_url}{stack.backend.health_endpoint}

{deployment.frontend.platform}:
- Watch build logs
- Verify deployment completes
- Check site loads: {production_frontend_url}
```

### 9.3 Post-Deployment Verification

```
Test critical flows:
1. [ ] Homepage loads
2. [ ] Login works
3. [ ] Core functionality works
4. [ ] Key user flows complete successfully
```

---

## Phase 10: Rollback Plan

If issues occur post-deployment:

### Backend Rollback ({deployment.backend.platform})

```
1. Go to {deployment.backend.platform} dashboard
2. Select {project.slug}-backend service
3. Go to Deployments
4. Click "Rollback" on previous working deployment
```

### Frontend Rollback ({deployment.frontend.platform})

```
1. Go to {deployment.frontend.platform} dashboard
2. Select {project.slug} project
3. Go to Deployments
4. Click "..." on previous deployment
5. Select "Promote to Production"
```

### Database Rollback (if migration was applied)

```
1. Run rollback script: {stack.database.migrations_path}/{date}_{name}_rollback.sql
2. Verify data integrity
3. Update schema file to previous state
```

---

## Thinking Log Template for This Command

```markdown
# Pre-Deployment Log
# Target: {production/staging}
# Started: {timestamp}
# Branch: {branch name}

## Phase 1: Preparation
- Changes since last deploy: {summary}
- Migration needed: {yes/no}
- New env vars: {list or none}

## Phase 2: Agent Suite
| Agent | Status | Notes |
|-------|--------|-------|
| @qa-agent | | |
| @api-sync-agent | | |
| @hebrew-validator | | |
| @docs-agent | | |

## Phase 3: Build Verification
### Backend
- Syntax check: {pass/fail}
- Docker build: {pass/fail}
- Issues found: {list}

### Frontend
- Type check: {pass/fail}
- Build: {pass/fail}
- Issues found: {list}

## Phase 4: Environment
### Backend Env Vars
- [ ] All required variables configured
- [ ] DEBUG=False

### Frontend Env Vars
- [ ] {stack.frontend.env_prefix}API_URL
- [ ] {stack.frontend.env_prefix}SUPABASE_URL
- [ ] {stack.frontend.env_prefix}SUPABASE_ANON_KEY

## Phase 5: Database
- Schema current: {yes/no}
- Migrations applied: {yes/no}
- Indexes verified: {yes/no}

## Phase 6: Deploy Checker
- Overall status: {ready/not ready}
- Issues: {list}

## Phase 7: Checklist
### Mandatory
[Copy checklist with marks]

### Recommended
[Copy checklist with marks]

## Phase 8: Decision
**DECISION: {GO / NO-GO}**

### If NO-GO:
- Blocking issues: {list}
- Actions needed: {list}

### If GO:
- Deployment plan: {confirmed}

## Phase 9: Deployment
- Merge completed: {timestamp}
- {deployment.backend.platform} deployment: {status}
- {deployment.frontend.platform} deployment: {status}

## Phase 10: Post-Deployment
- Health check: {pass/fail}
- User flows tested: {pass/fail}
- Issues found: {none/list}

## Summary
- Total time: {duration}
- Deployment successful: {yes/no}
- Notes: {any important observations}
```
