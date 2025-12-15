---
description: Execute multiple tasks in parallel using Task Tool with proper coordination
allowed_tools:
  - Read
  - Write
  - Bash
  - Glob
---

# Parallel Task Execution

## Tasks to Execute
$ARGUMENTS

---

## Phase 1: Task Analysis (think hard)

```
think hard about these tasks:

1. INDEPENDENCE CHECK
   - Are these tasks truly independent?
   - Do they modify the same files?
   - Do they have shared dependencies?

2. RESOURCE CONFLICTS
   - Same database tables?
   - Same API endpoints?
   - Same configuration files?

3. ORDER DEPENDENCIES
   - Must any task complete before another starts?
   - Are there logical dependencies?

4. INTEGRATION POINTS
   - How will results be combined?
   - What happens after all complete?
```

**Decision Matrix:**

| Task A | Task B | Can Parallelize? |
|--------|--------|------------------|
| Modifies X | Reads X | ⚠️ Maybe (if read-only is fine with changes) |
| Modifies X | Modifies X | ❌ No |
| Modifies X | Modifies Y | ✅ Yes |
| Modifies API | Modifies UI | ✅ Yes (usually) |
| Schema change | Uses schema | ❌ No (schema first) |

---

## Phase 2: Strategy Selection

### Strategy A: Pure Parallel (No Conflicts)

All tasks are independent. Execute simultaneously.

```
Run the following tasks in parallel using task tool:

Task 1: {description}
- Write thinking log: .claude/logs/task1-{timestamp}.md
- Call @qa-agent when done
- Report: files modified, issues found

Task 2: {description}
- Write thinking log: .claude/logs/task2-{timestamp}.md
- Call @qa-agent when done
- Report: files modified, issues found

Task 3: {description}
- Write thinking log: .claude/logs/task3-{timestamp}.md
- Call @qa-agent when done
- Report: files modified, issues found
```

### Strategy B: Parallel with Worktrees (File Conflicts)

Tasks modify overlapping files. Use Git Worktrees.

```
First, set up worktrees:

git worktree add ../medai-hub-task1 -b task/task1
git worktree add ../medai-hub-task2 -b task/task2
git worktree add ../medai-hub-task3 -b task/task3

Then run in parallel using task tool:

Task 1:
- Working directory: ../medai-hub-task1
- Branch: task/task1
- {task description}
- Write thinking log: .claude/logs/task1-{timestamp}.md

Task 2:
- Working directory: ../medai-hub-task2
- Branch: task/task2
- {task description}
- Write thinking log: .claude/logs/task2-{timestamp}.md

Task 3:
- Working directory: ../medai-hub-task3
- Branch: task/task3
- {task description}
- Write thinking log: .claude/logs/task3-{timestamp}.md
```

### Strategy C: Phased Execution (Dependencies)

Some tasks depend on others.

```
Phase 1 - Run in parallel using task tool:
- Task A: {independent task}
- Task B: {independent task}

[Wait for Phase 1 completion]

Phase 2 - Run in parallel using task tool:
- Task C: {depends on A}
- Task D: {depends on B}

[Wait for Phase 2 completion]

Phase 3 - Sequential:
- Task E: {depends on C and D}
```

### Strategy D: Sequential (Many Dependencies)

Tasks have complex dependencies. Execute one at a time.

```
Execute sequentially with checkpoints:

1. Task A
   - Complete and verify
   - Checkpoint: {state to verify}

2. Task B (uses output of A)
   - Complete and verify
   - Checkpoint: {state to verify}

3. Task C (uses output of B)
   - Complete and verify
```

---

## Phase 3: Execution

### Standard Parallel Execution Format

```
Run the following tasks in parallel using task tool:

===== TASK 1: {Name} =====
Description: {what to do}
Working Directory: {path}
Branch: {branch if using worktrees}

Instructions:
1. {Step 1}
2. {Step 2}
3. {Step 3}

Requirements:
- Write thinking log to: .claude/logs/task1-{timestamp}.md
- Follow project patterns in CLAUDE.md
- Handle errors gracefully

On Completion:
- Call @qa-agent for review
- Report status to orchestrator
- List all files modified

===== TASK 2: {Name} =====
[Same format...]

===== TASK 3: {Name} =====
[Same format...]
```

### Thinking Log Format for Each Task

Each parallel task must write:

```markdown
# Parallel Task Log
# Task: {name}
# Part of: /project:parallel-tasks execution
# Started: {timestamp}

## Task Assignment
{What I was asked to do}

## My Understanding
{How I interpret this task}

## Execution Plan
1. {Step}
2. {Step}

## Execution Log
- {timestamp} Started: {action}
- {timestamp} Completed: {action}
- {timestamp} Issue: {description} - Resolution: {how fixed}

## Files Modified
| File | Change Type | Description |
|------|-------------|-------------|
| {path} | Created | {description} |
| {path} | Modified | {description} |

## Issues Encountered
| Issue | Severity | Resolution |
|-------|----------|------------|
| {issue} | {level} | {how resolved} |

## QA Review
- Called @qa-agent: {yes/no}
- Result: {approved/needs fixes}

## Completion Report
- Status: Complete/Partial/Failed
- Time taken: {duration}
- Handoff notes: {anything next task needs to know}
```

---

## Phase 4: Collection and Integration

After all tasks complete:

```
Collect results from all tasks:

Task 1: {status}
- Files: {list}
- Issues: {list}
- QA: {status}

Task 2: {status}
- Files: {list}
- Issues: {list}
- QA: {status}

Task 3: {status}
- Files: {list}
- Issues: {list}
- QA: {status}
```

### If Using Worktrees, Merge:

```bash
# Merge in dependency order
cd ../medai-hub
git merge task/task1
git merge task/task2
git merge task/task3

# Resolve any conflicts
# Then cleanup
git worktree remove ../medai-hub-task1
git worktree remove ../medai-hub-task2
git worktree remove ../medai-hub-task3
git branch -d task/task1 task/task2 task/task3
```

---

## Phase 5: Post-Parallel Validation

```
After all tasks complete and merge (if applicable):

1. Call @qa-agent for combined review
2. Call @api-sync-agent if API changes
3. Call @hebrew-validator if Query-related
4. Call @docs-agent for documentation updates
```

---

## Phase 6: Report

```markdown
## Parallel Execution Report

### Execution ID: PARALLEL-{timestamp}
### Strategy Used: {A/B/C/D}
### Overall Status: ✅ Complete / ⚠️ Partial / ❌ Failed

### Task Summary
| Task | Status | Duration | Files Changed |
|------|--------|----------|---------------|
| Task 1 | ✅ | 5m | 3 |
| Task 2 | ✅ | 8m | 2 |
| Task 3 | ✅ | 4m | 4 |

### Integration Results
- Worktrees merged: {yes/no/na}
- Conflicts: {none/list}
- Post-merge QA: {status}

### Thinking Logs
- Orchestrator: .claude/logs/parallel-tasks-{timestamp}.md
- Task 1: .claude/logs/task1-{timestamp}.md
- Task 2: .claude/logs/task2-{timestamp}.md
- Task 3: .claude/logs/task3-{timestamp}.md

### Total Duration: {time}
### Speedup vs Sequential: {estimate}
```

---

## Quick Reference: Task Tool Syntax

### Basic Parallel
```
Run the following tasks in parallel using task tool:

Task 1: Do X
Task 2: Do Y
```

### With Details
```
Run the following tasks in parallel using task tool:

Task 1 (Backend):
- Working in: backend/
- Action: Create new service
- Output: Report when done

Task 2 (Frontend):
- Working in: frontend/
- Action: Create new component
- Output: Report when done
```

### With Sub-Agents
```
Run the following tasks in parallel using task tool:

Task 1:
- Implement feature A
- When done, call @qa-agent

Task 2:
- Implement feature B
- When done, call @qa-agent

After both complete:
- Call @api-sync-agent
- Call @docs-agent
```

---

## Error Handling

### If a Task Fails:

```
Task {N} failed:
- Error: {description}
- Files modified before failure: {list}

Recovery options:
A) Retry task with fixes
B) Rollback task changes, continue others
C) Abort all, rollback everything

Chosen: {A/B/C}
```

### If Integration Fails:

```
Integration failed:
- Conflict in: {file}
- Task 1 change: {description}
- Task 2 change: {description}

Resolution:
{How conflict was resolved}
```

