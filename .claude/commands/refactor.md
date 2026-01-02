---
description: Structured workflow for code refactoring and technical debt reduction
allowed_tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Refactor Workflow

## Prerequisites

Read project configuration:

```bash
cat .claude/PROJECT.yaml
```

Use configuration values throughout this command.

## Request

$ARGUMENTS

---

## Phase 1: Analysis & Diagnosis

Before ANY code changes, analyze the target code.

```
ultrathink about this refactor request:

1. TARGET IDENTIFICATION
   - Which files are affected?
   - What are the code smells? (Duplication, Complexity, Coupling, etc.)
   - What is the current behavior that MUST be preserved?

2. DEPENDENCY MAPPING
   - Who calls this code?
   - What data structures does it modify?
   - Are there tests covering this code?

3. RISK ASSESSMENT
   - High risk: Core logic, Auth, Database
   - Low risk: UI styling, internal comments
   - Rollback strategy: How to revert?
```

**Output:** Write analysis to `.claude/logs/refactor-analysis-{timestamp}.md`

---

## Phase 2: Refactoring Plan

Create a plan document: `docs/plans/refactor-{name}-{date}.md`

```markdown
# Refactoring Plan: {Name}

## Goal
{What are we improving? Performance? Readability? Maintainability?}

## Scope
- [ ] File A in {stack.backend.path}/
- [ ] File B in {stack.frontend.path}/

## Strategy
1. **Current State:** {Description of mess}
2. **Target State:** {Description of clean code}
3. **Approach:** {Extract Method / Rename / Pattern / etc.}

## Verification Strategy
- Existing tests to run: {list}
- New tests to write: {list}
```

**Wait for human approval if the refactor is large.**

---

## Phase 3: Execution

Call appropriate agents based on the code type.

### Backend Refactor

Call @backend-agent:

```
Refactor task:
- Target: {file in {stack.backend.path}}
- Goal: {improvement}
- Constraint: Preserve existing behavior (Public API)
```

### Frontend Refactor

Call @frontend-agent:

```
Refactor task:
- Target: {component in {stack.frontend.path}}
- Goal: {improvement}
- Constraint: Visual regression check
```

**Rules for Refactoring:**

1. **Small Steps:** Change one thing at a time.
2. **Run Tests:** Run related tests after EVERY step.
3. **No Behavior Changes:** Do not add features while refactoring.

---

## Phase 4: Verification

### 4.1 Automated Testing

Run the test suite.

```bash
# Backend
cd {stack.backend.path}
{stack.backend.test_command} {test_file}

# Frontend
cd {stack.frontend.path}
{stack.frontend.test_command} {component}
```

### 4.2 Lint Check

```bash
# Backend
cd {stack.backend.path}
{stack.backend.lint_command}

# Frontend
cd {stack.frontend.path}
{stack.frontend.lint_command}
```

### 4.3 Build Verification

```bash
# Frontend
cd {stack.frontend.path}
{stack.frontend.build_command}
```

### 4.4 Manual Verification

Call @qa-agent:

```
Verify refactor of {component/service}:
- Check for regression
- Verify code quality metrics
```

---

## Phase 5: Documentation

Call @docs-agent:

```
Update documentation if refactor changed:
- Function signatures
- Class structures
- File locations
```

---

## Completion Report

```markdown
# Refactor Complete

## Summary
- Target: {files}
- Improvement: {description}
- Verification: {tests passed}

## Files Modified
| File | Change |
|------|--------|
| {path} | {description} |

## Metrics (if applicable)
- Lines of code: {before} → {after}
- Complexity: {before} → {after}
- Test coverage: {maintained/improved}

## Thinking Log
`.claude/logs/refactor-analysis-{timestamp}.md`
```

---

## Thinking Log Template for This Command

```markdown
# Refactor Log
# Target: {description}
# Started: {timestamp}
# Command: /project:refactor {arguments}

## Phase 1: Analysis
### Timestamp: {time}

### Target Identification
- Files affected: {list}
- Code smells: {list}
- Behavior to preserve: {description}

### Dependencies
- Called by: {list}
- Modifies: {data structures}
- Test coverage: {yes/no/partial}

### Risk Assessment
- Risk level: {low/medium/high}
- Rollback: {strategy}

## Phase 2: Planning
### Timestamp: {time}

- Plan document: {path}
- Approval: {pending/approved}

## Phase 3: Execution
### Timestamp: {time}

### Changes Made
| Step | Change | Verified |
|------|--------|----------|
| 1 | {change} | {yes/no} |
| 2 | {change} | {yes/no} |

### Agent Used
- Backend: @backend-agent
- Frontend: @frontend-agent

## Phase 4: Verification
### Timestamp: {time}

- Tests: {pass/fail}
- Lint: {pass/fail}
- Build: {pass/fail}
- @qa-agent: {status}

## Phase 5: Documentation
### Timestamp: {time}

- @docs-agent: {status}
- CLAUDE.md update: {yes/no}

## Summary
- Total time: {duration}
- Files changed: {count}
- Improvement achieved: {description}
```
