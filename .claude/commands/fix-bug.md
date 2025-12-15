---
description: Structured workflow for debugging and fixing bugs with root cause analysis
allowed_tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Bug Fix Workflow

## Bug Report
$ARGUMENTS

---

## Phase 1: Understanding (think harder)

```
think harder about this bug:

1. SYMPTOM ANALYSIS
   - What is the observed behavior?
   - What is the expected behavior?
   - When does it occur? (always/sometimes/specific conditions)
   - Who reported it? (user/QA/monitoring)

2. IMPACT ASSESSMENT
   - Severity: Critical/High/Medium/Low
   - Users affected: All/Some/Edge case
   - Data at risk: Yes/No
   - Workaround exists: Yes/No

3. REPRODUCTION
   - Can I reproduce it?
   - Steps to reproduce
   - Environment details
```

**Output:** Write analysis to `.claude/logs/bug-analysis-{timestamp}.md`

---

## Phase 2: Investigation

### 2.1 Locate the Bug

```bash
# Search for relevant code
grep -r "relevant_term" backend/
grep -r "relevant_term" frontend/

# Check recent changes that might have caused it
git log --oneline -20
git log --oneline --all -- path/to/suspected/file
```

### 2.2 Trace the Flow

```
think harder about the code path:

1. Entry point: Where does the request/action start?
2. Data flow: How does data move through the system?
3. Transformation points: Where is data modified?
4. Exit point: Where does the response/result come from?
5. Failure point: Where does the expected flow break?
```

### 2.3 Root Cause Analysis

```
think harder about WHY this bug exists:

1. WHAT broke: {specific code/logic}
2. WHY it broke: {the actual cause}
3. WHEN it broke: {recent change? always broken? edge case?}
4. WHY it wasn't caught: {missing test? unclear requirement?}
```

**Document root cause in thinking log.**

---

## Phase 3: Planning the Fix

### 3.1 Fix Strategy

```
Options:
A) Quick fix: Address symptom only
   - Pros: Fast
   - Cons: May not prevent recurrence
   - Use when: Urgent, root cause unclear

B) Proper fix: Address root cause
   - Pros: Prevents recurrence
   - Cons: Takes longer
   - Use when: Root cause is clear

C) Comprehensive fix: Root cause + prevention
   - Pros: Best long-term
   - Cons: Most time
   - Use when: Critical path, recurring issue
```

**Choose strategy and document reasoning.**

### 3.2 Change Scope

```markdown
## Planned Changes

### Files to Modify
| File | Change | Risk |
|------|--------|------|
| {path} | {description} | {low/medium/high} |

### Files NOT to Touch
- {file}: {reason - out of scope}

### Tests to Add/Update
- {test description}

### Rollback Plan
If fix causes new issues:
1. {rollback step}
2. {rollback step}
```

---

## Phase 4: Implementation

### 4.1 Create Fix Branch

```bash
git checkout develop
git pull origin develop
git checkout -b fix/{bug-name}
```

### 4.2 Make Minimal Changes

**Principle:** Fix the bug with the smallest possible change.

```
For each change:
1. Make the change
2. Verify it addresses the symptom
3. Verify it doesn't break anything else
4. Document in thinking log
```

**Do NOT:**
- Refactor unrelated code
- Add features
- Change formatting elsewhere
- "Improve" things while you're there

### 4.3 Verify the Fix

```bash
# Backend
cd backend
python -m py_compile {modified_file}
pytest {related_tests} -v

# Frontend
cd frontend
npx tsc --noEmit
npm run build
```

### 4.4 Test Edge Cases

```
think about edge cases:

- What if input is empty?
- What if input is very large?
- What if user is not authenticated?
- What if network fails mid-operation?
- What if database returns unexpected data?
```

---

## Phase 5: Validation

### 5.1 Self-Review

```
Review my changes:

- [ ] Fix addresses the root cause
- [ ] No unintended side effects
- [ ] Error handling is proper
- [ ] Code follows project patterns
- [ ] No debug code left behind
```

### 5.2 Agent Review

Call @qa-agent:

```
Review bug fix:

Bug: {description}
Root cause: {cause}
Fix: {description}
Files changed: {list}
```

**Iterate until @qa-agent approves.**

---

## Phase 6: Documentation

### 6.1 Update Thinking Log

Complete the bug analysis document with:
- Root cause found
- Fix implemented
- Verification results

### 6.2 Update CLAUDE.md

Call @docs-agent only if:
- Bug revealed undocumented behavior
- Fix changed documented behavior
- Workaround should be removed from docs

### 6.3 Add to Recent Changes Log

```markdown
### {YYYY-MM-DD} - Bug Fix: {Brief Title}

**Problem**: {What was broken}

**Root Cause**: {Why it happened}

**Solution**: {What was changed}

**Files Modified**:
- `{path}` - {change description}

**Prevention**: {How to prevent recurrence, if applicable}
```

---

## Phase 7: Merge

```bash
# Ensure up to date
git checkout develop
git pull origin develop

# Merge fix
git merge fix/{bug-name}

# Push
git push origin develop

# Cleanup
git branch -d fix/{bug-name}
```

---

## Phase 8: Post-Fix Verification

```
Verify on develop branch:

1. [ ] Bug no longer reproduces
2. [ ] Related functionality still works
3. [ ] No new errors in logs
4. [ ] Build succeeds
```

---

## Thinking Log Template for This Command

```markdown
# Bug Fix Log
# Bug: {brief description}
# Started: {timestamp}
# Severity: {Critical/High/Medium/Low}
# Command: /project:fix-bug {arguments}

## Phase 1: Understanding
### Timestamp: {time}

### Symptom
{observed behavior}

### Expected
{expected behavior}

### Reproduction Steps
1. {step}
2. {step}

### Impact
- Severity: {level}
- Users affected: {scope}
- Data risk: {yes/no}

## Phase 2: Investigation
### Timestamp: {time}

### Code Path Traced
```
{entry} → {step} → {step} → {failure point} → {exit}
```

### Root Cause
**WHAT:** {specific code/logic that's broken}
**WHY:** {underlying reason}
**WHEN:** {when it started/was introduced}

### Evidence
- File: {path}, Line: {number}
- Code: {problematic code}
- Issue: {explanation}

## Phase 3: Planning
### Timestamp: {time}

### Strategy Chosen: {A/B/C}
### Reasoning: {why this strategy}

### Planned Changes
| File | Change | Risk |
|------|--------|------|
| {path} | {change} | {risk} |

## Phase 4: Implementation
### Timestamp: {time}

### Changes Made
#### File: {path}
- Before: {code}
- After: {code}
- Reason: {why}

### Verification
- Syntax check: {pass/fail}
- Type check: {pass/fail}
- Tests: {pass/fail}

## Phase 5: Validation
### Timestamp: {time}

### Self-Review
- [x] Fix addresses root cause
- [x] No side effects
- [x] Proper error handling

### @qa-agent Review
- Status: {pending/approved}
- Issues found: {none/list}
- Iterations: {count}

## Phase 6: Documentation
### Timestamp: {time}

- CLAUDE.md update needed: {yes/no}
- Recent Changes Log: {added}

## Phase 7: Merge
### Timestamp: {time}

- Branch: fix/{name}
- Merged to: develop
- Conflicts: {none/resolved}

## Phase 8: Post-Fix
### Timestamp: {time}

- Bug reproduction test: {no longer reproduces}
- Related functionality: {works}
- Build status: {pass}

## Summary
### Total Time: {duration}
### Difficulty: {easy/medium/hard}
### Lessons Learned: {notes}
```

---

## Emergency Hotfix Variant

For critical production bugs:

```
1. Skip planning documentation
2. Create branch from main: git checkout -b hotfix/{name} main
3. Minimal fix only
4. @qa-agent quick review
5. Merge to main immediately
6. Then merge main to develop
7. Document after the fact
```

