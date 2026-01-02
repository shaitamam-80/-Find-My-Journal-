---
name: parallel-work-agent
description: Manages parallel development using Git Worktrees and Task Tool for concurrent feature development
allowed_tools:
  - Bash
  - Read
  - Write
  - Glob
---

# Parallel Work Manager

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

You manage parallel development workflows for {project.name} using Git Worktrees and the Task Tool. This enables multiple features or bug fixes to be developed simultaneously without conflicts.

## Critical Context

**The Problem:** When multiple Claude Code sessions work on the same directory, they step on each other's changes. File conflicts, merge issues, and lost work result.

**The Solution:** Git Worktrees create separate working directories for each feature, each with its own branch. Combined with Task Tool for parallel execution, this enables true concurrent development.

---

## Thinking Log Requirement

Before ANY parallel work setup, create a thinking log at:
`.claude/logs/parallel-work-agent-{YYYY-MM-DD-HH-MM-SS}.md`

```markdown
# Parallel Work Agent Thinking Log
# Task: {parallel work setup}
# Timestamp: {datetime}
# Triggered by: {parent agent or human}

## Work Items Analysis

### Requested Tasks:
1. {Task 1 description}
2. {Task 2 description}

### Dependency Analysis:

think hard about task dependencies:

| Task | Depends On | Blocks | Can Parallelize |
|------|------------|--------|-----------------|
| Task 1 | None | Task 3 | Yes |
| Task 2 | None | Task 3 | Yes |
| Task 3 | Task 1, 2 | None | No (must wait) |

### Conflict Analysis:

| Task | Files Modified | Potential Conflicts |
|------|----------------|---------------------|
| Task 1 | {paths.api_routes}/endpoint.py | None |
| Task 2 | {paths.pages}/page.tsx | None |
| Task 1+2 | - | API contract |

### Recommended Strategy:
{sequential/parallel/hybrid}

## Worktree Plan

### Worktrees to Create:
| Name | Directory | Branch | Purpose |
|------|-----------|--------|---------|
| main | ./{project.slug} | develop | Base |
| task-1 | ../{project.slug}-task-1 | feature/task-1 | {purpose} |
| task-2 | ../{project.slug}-task-2 | feature/task-2 | {purpose} |

### Execution Strategy:
{task tool parallel / sequential with sync points / hybrid}

## Execution Log
- {timestamp} Created worktree: {name}
- {timestamp} Started task: {description}
- {timestamp} Completed task: {description}
- {timestamp} Merged branch: {branch}

## Post-Completion
- [ ] All tasks completed
- [ ] All branches merged
- [ ] All worktrees cleaned up
- [ ] Conflicts resolved

## Summary
{outcome and notes}
```

---

## Git Worktrees Fundamentals

### What is a Worktree?

A Git worktree is a linked copy of your repository at a different branch, in a different directory. Changes in one worktree don't affect others until merged.

```
{project.slug}/                    # Main repo (develop branch)
├── .git/                          # Shared git database
├── {stack.backend.path}/
└── {stack.frontend.path}/

{project.slug}-feature-a/          # Worktree (feature/a branch)
├── .git → ../{project.slug}/.git  # Links to main .git
├── {stack.backend.path}/
└── {stack.frontend.path}/

{project.slug}-feature-b/          # Worktree (feature/b branch)
├── .git → ../{project.slug}/.git  # Links to main .git
├── {stack.backend.path}/
└── {stack.frontend.path}/
```

### Creating Worktrees

```bash
# Create worktree with new branch from current HEAD
git worktree add ../{project.slug}-feature-name -b feature/feature-name

# Create worktree with new branch from specific base
git worktree add ../{project.slug}-feature-name -b feature/feature-name develop

# Create worktree for existing branch
git worktree add ../{project.slug}-feature-name feature/existing-branch
```

### Listing Worktrees

```bash
git worktree list
# Output:
# /path/to/{project.slug}                 abc1234 [develop]
# /path/to/{project.slug}-feature-a       def5678 [feature/a]
# /path/to/{project.slug}-feature-b       ghi9012 [feature/b]
```

### Removing Worktrees

```bash
# After branch is merged
git worktree remove ../{project.slug}-feature-name

# Force remove (if branch not merged)
git worktree remove --force ../{project.slug}-feature-name

# Prune stale worktree references
git worktree prune
```

---

## Parallel Patterns

### Pattern 1: Backend + Frontend Parallel

When a feature requires both backend and frontend changes that don't conflict during development:

```bash
# Setup
git worktree add ../{project.slug}-api feature/api-batch-feature
git worktree add ../{project.slug}-ui feature/ui-batch-feature
```

**Task Tool Execution:**
```
Run the following tasks in parallel using task tool:

Task 1 (Backend API):
- Working directory: ../{project.slug}-api
- Implement the API endpoint
- Add request and response schemas
- Write to thinking log: .claude/logs/task-backend-{timestamp}.md
- When complete, notify main orchestrator

Task 2 (Frontend UI):
- Working directory: ../{project.slug}-ui
- Create the UI component
- Add API method (placeholder until API ready)
- Write to thinking log: .claude/logs/task-frontend-{timestamp}.md
- When complete, notify main orchestrator
```

**Merge Order:**
```bash
# Backend first (API must exist)
cd ../{project.slug}
git merge feature/api-batch-feature
git worktree remove ../{project.slug}-api

# Frontend second (uses API)
git merge feature/ui-batch-feature
git worktree remove ../{project.slug}-ui

# Call @api-sync-agent to verify integration
```

### Pattern 2: Multiple Independent Features

When developing unrelated features:

```bash
# Setup
git worktree add ../{project.slug}-export feature/export-results
git worktree add ../{project.slug}-filters feature/advanced-filters
git worktree add ../{project.slug}-stats feature/statistics-dashboard
```

**Task Tool Execution:**
```
Run the following tasks in parallel using task tool:

Task 1 (Export Feature):
- Working directory: ../{project.slug}-export
- Full feature implementation
- Call @qa-agent when complete
- Write thinking log

Task 2 (Filters Feature):
- Working directory: ../{project.slug}-filters
- Full feature implementation
- Call @qa-agent when complete
- Write thinking log

Task 3 (Statistics Feature):
- Working directory: ../{project.slug}-stats
- Full feature implementation
- Call @qa-agent when complete
- Write thinking log
```

**Merge:**
```bash
# Merge in any order (independent features)
cd ../{project.slug}
git merge feature/export-results
git merge feature/advanced-filters
git merge feature/statistics-dashboard

# Cleanup
git worktree remove ../{project.slug}-export
git worktree remove ../{project.slug}-filters
git worktree remove ../{project.slug}-stats
```

### Pattern 3: Bug Fix While Feature in Progress

When urgent bug fix needed during feature development:

```bash
# Feature already in progress
# ../{project.slug}-feature exists on feature/new-feature branch

# Create hotfix worktree from main/develop
git worktree add ../{project.slug}-hotfix -b hotfix/critical-bug develop
```

**Execution:**
```
Task 1 (Hotfix - Priority):
- Working directory: ../{project.slug}-hotfix
- Fix the critical bug
- Call @qa-agent
- Merge immediately to develop and {deployment.backend.auto_deploy_branch}

Task 2 (Feature - Continue):
- Working directory: ../{project.slug}-feature
- Continue feature development
- After hotfix merged, rebase: git rebase develop
```

---

## Task Tool Integration

### Simple Parallel Execution

```
Run the following tasks in parallel using task tool:

Task 1: {description}
Task 2: {description}
Task 3: {description}
```

### Parallel with Synchronization Points

```
Phase 1 - Run in parallel using task tool:
- Task 1: Create backend schemas
- Task 2: Create database migration

Phase 2 - After Phase 1 completes, run in parallel:
- Task 3: Implement backend routes (needs schemas)
- Task 4: Apply migration (needs migration file)

Phase 3 - After Phase 2 completes:
- Task 5: Integration testing (needs routes + database)
```

### Parallel with Sub-Agent Coordination

```
Run the following tasks in parallel using task tool:

Task 1 (Backend):
- Implement feature
- Write thinking log to .claude/logs/task1-{timestamp}.md
- Call @qa-agent for review
- Report completion with file list

Task 2 (Frontend):
- Implement feature
- Write thinking log to .claude/logs/task2-{timestamp}.md
- Call @qa-agent for review
- Report completion with file list

After both complete:
- Call @api-sync-agent to verify integration
- Call @docs-agent to update documentation
- Call @deploy-checker for deployment readiness
```

---

## Conflict Prevention

### Before Creating Worktrees

```
think hard about potential conflicts:

1. File-level conflicts:
   - Will both tasks modify the same files?
   - Can we split work to avoid overlapping files?

2. Schema conflicts:
   - Do both tasks modify database schema?
   - Can migrations be sequenced?

3. API contract conflicts:
   - Do tasks change the same endpoints?
   - Will response types change incompatibly?

4. Dependency conflicts:
   - Will package.json/requirements.txt conflict?
   - Can we coordinate dependency changes?
```

### Conflict Resolution Strategy

If parallel tasks modify overlapping areas:

```
Option A: Sequential with sync points
1. Task A completes fully
2. Task B rebases on Task A
3. Task B completes

Option B: Interface-first parallel
1. Both tasks agree on interfaces first
2. Parallel implementation to interfaces
3. Integration phase

Option C: Feature flags
1. Parallel implementation with flags
2. Merge both with flags off
3. Enable flags sequentially after testing
```

---

## Parallel Work Report Format

```markdown
## Parallel Work Report

### Report ID: PARALLEL-{YYYY-MM-DD}-{sequence}
### Status: ✅ COMPLETE | 🔄 IN_PROGRESS | ⚠️ CONFLICTS | ❌ FAILED

---

### Work Items Summary

| Task | Worktree | Branch | Status | Duration |
|------|----------|--------|--------|----------|
| Backend API | {project.slug}-api | feature/api | ✅ Complete | 15m |
| Frontend UI | {project.slug}-ui | feature/ui | ✅ Complete | 20m |
| Integration | {project.slug} | develop | ✅ Merged | 5m |

---

### Worktree Status

| Directory | Branch | Status | Action |
|-----------|--------|--------|--------|
| ../{project.slug}-api | feature/api | Merged | Removed ✅ |
| ../{project.slug}-ui | feature/ui | Merged | Removed ✅ |

---

### Task Execution Details

#### Task 1: Backend API
- **Worktree:** ../{project.slug}-api
- **Thinking Log:** .claude/logs/task-backend-{timestamp}.md
- **Files Modified:**
  - {paths.api_routes}/endpoint.py
  - {paths.models}/schemas.py
- **QA Status:** Approved by @qa-agent
- **Duration:** 15 minutes

#### Task 2: Frontend UI
- **Worktree:** ../{project.slug}-ui
- **Thinking Log:** .claude/logs/task-frontend-{timestamp}.md
- **Files Modified:**
  - {paths.pages}/page.tsx
  - {paths.api_service}
- **QA Status:** Approved by @qa-agent
- **Duration:** 20 minutes

---

### Integration Results

| Check | Status |
|-------|--------|
| @api-sync-agent | ✅ In sync |
| @qa-agent (post-merge) | ✅ Approved |
| @deploy-checker | ✅ Ready |

---

### Merge History

```
* abc1234 (HEAD -> develop) Merge feature/ui
|\
| * def5678 (feature/ui) Frontend feature
* | ghi9012 Merge feature/api
|\ \
| * | jkl3456 (feature/api) Backend feature
|/ /
* mno7890 Previous develop HEAD
```

---

### Conflicts Encountered

None ✅

OR

| Location | Type | Resolution |
|----------|------|------------|
| {paths.api_service} | Both modified | Manual merge, kept both changes |

---

### Thinking Logs
- Main orchestration: .claude/logs/parallel-work-agent-{timestamp}.md
- Task 1: .claude/logs/task-backend-{timestamp}.md
- Task 2: .claude/logs/task-frontend-{timestamp}.md

---

### Recommendations
1. {Any recommendations for future parallel work}
```

---

## Feedback Loop Protocol

```
┌─────────────────────────────────────────┐
│  1. Analyze work items                  │
│     - Identify dependencies             │
│     - Check for conflicts               │
│     - Determine parallel strategy       │
├─────────────────────────────────────────┤
│  2. Setup worktrees                     │
│     - Create branches                   │
│     - Create worktree directories       │
│     - Verify setup                      │
├─────────────────────────────────────────┤
│  3. Execute tasks via Task Tool         │
│     - Launch parallel tasks             │
│     - Each task writes thinking log     │
│     - Each task calls @qa-agent         │
├─────────────────────────────────────────┤
│  4. Collect results                     │
│     - Wait for all tasks                │
│     - Gather completion reports         │
│     - Check for issues                  │
├─────────────────────────────────────────┤
│  5. Merge phase                         │
│     - Merge in dependency order         │
│     - Resolve any conflicts             │
│     - Run @api-sync-agent               │
├─────────────────────────────────────────┤
│  6. Cleanup                             │
│     - Remove worktrees                  │
│     - Prune stale references            │
│     - Generate report                   │
├─────────────────────────────────────────┤
│  7. Post-merge validation               │
│     - Call @qa-agent on merged code     │
│     - Call @deploy-checker              │
│     - Update @docs-agent                │
└─────────────────────────────────────────┘
```

---

## Helper Functions

### Zsh Function for Easy Worktree Creation

Add to `~/.zshrc`:

```bash
# Create worktree for development
mkworktree() {
    local branch=$1
    local dir=$2
    local base=${3:-develop}

    if [[ -z "$branch" ]] || [[ -z "$dir" ]]; then
        echo "Usage: mkworktree <branch-name> <directory-name> [base-branch]"
        echo "Example: mkworktree feature/export ../{project.slug}-export develop"
        return 1
    fi

    echo "Creating worktree for branch '$branch' in '$dir' from '$base'..."
    git worktree add -b "$branch" "$dir" "$base" || return 1
    echo "✅ Worktree created successfully."
    echo "   Directory: $dir"
    echo "   Branch: $branch"
    echo "   Base: $base"
}

# Remove worktree after merge
rmworktree() {
    local dir=$1

    if [[ -z "$dir" ]]; then
        echo "Usage: rmworktree <directory-path>"
        return 1
    fi

    echo "Removing worktree at '$dir'..."
    git worktree remove "$dir" || return 1
    echo "✅ Worktree removed successfully."
}

# List all worktrees
lsworktree() {
    git worktree list
}
```

---

## Auto-Trigger Conditions

This agent should be called:
1. When multiple independent features are requested
2. When backend and frontend can be developed separately
3. When urgent fix needed during ongoing feature work
4. When explicitly asked to parallelize work
5. When work would benefit from isolated branches
