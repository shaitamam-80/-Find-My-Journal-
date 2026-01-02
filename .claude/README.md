# Claude Code Agent System

This directory contains a reusable, configurable agent system for Claude Code. All agents read their configuration from `PROJECT.yaml` and use variable references instead of hardcoded values.

## Quick Start

1. **Configure your project** by editing `.claude/PROJECT.yaml`
2. **Use agents** by referencing them with `@agent-name`
3. **Run workflows** using the commands in `.claude/commands/`

## Directory Structure

```
.claude/
├── PROJECT.yaml          # Central configuration file
├── PROJECT_MEMORY.md     # Long-term project memory
├── README.md             # This file
├── agents/               # Specialized agent definitions
│   ├── orchestrator.md       # Master coordinator
│   ├── backend-agent.md      # Backend development
│   ├── frontend-agent.md     # Frontend development
│   ├── ui-ux-agent.md        # UI/UX design
│   ├── qa-agent.md           # Quality assurance
│   ├── api-sync-agent.md     # API contract validation
│   ├── db-migration-agent.md # Database migrations
│   ├── docs-agent.md         # Documentation
│   ├── deploy-checker.md     # Deployment readiness
│   ├── devops-agent.md       # CI/CD & infrastructure
│   ├── parallel-work-agent.md# Parallel development
│   └── hebrew-validator.md   # RTL/Hebrew validation
├── commands/             # Workflow commands
│   ├── new-feature.md
│   ├── fix-bug.md
│   ├── refactor.md
│   ├── add-endpoint.md
│   └── pre-deploy.md
├── lib/                  # Shared utilities
│   └── config-reader.md  # Configuration reader instructions
└── logs/                 # Agent thinking logs
```

## Configuration (PROJECT.yaml)

The `PROJECT.yaml` file contains all project-specific settings:

```yaml
project:
  name: "Your Project Name"
  slug: "your-project-slug"
  description: "Project description"

stack:
  backend:
    framework: "fastapi"      # or express, django, etc.
    language: "python"
    version: "3.11"
    path: "backend"
    entry_point: "app.main:app"
    port: 8000
    health_endpoint: "/health"
    test_command: "pytest"
    lint_command: "ruff check ."

  frontend:
    framework: "vite"         # or next, create-react-app
    ui_library: "react"
    language: "typescript"
    path: "frontend"
    port: 5173
    env_prefix: "VITE_"       # or NEXT_PUBLIC_, REACT_APP_
    build_command: "npm run build"
    test_command: "npm run test"
    lint_command: "npm run lint"

  database:
    provider: "supabase"      # or postgres, mysql, mongodb
    type: "postgresql"
    migrations_path: "supabase/migrations"
    schema_file: "supabase/schema.sql"

deployment:
  backend:
    platform: "railway"       # or vercel, heroku, aws
    auto_deploy_branch: "main"
  frontend:
    platform: "vercel"
    auto_deploy_branch: "main"

paths:
  api_routes: "backend/app/api"
  models: "backend/app/models"
  services: "backend/app/services"
  components: "frontend/src/components"
  pages: "frontend/src/pages"
  types: "frontend/src/types/index.ts"
  api_service: "frontend/src/services/api.ts"

conventions:
  primary_language: "english"  # or hebrew, spanish, etc.
  rtl_support: false
```

## Variable References

Agents use variable references in the format `{path.to.value}`:

| Reference | Example Value |
|-----------|---------------|
| `{project.name}` | Find My Journal |
| `{project.slug}` | find-my-journal |
| `{stack.backend.path}` | backend |
| `{stack.frontend.path}` | frontend |
| `{stack.frontend.env_prefix}` | VITE_ |
| `{deployment.backend.platform}` | railway |
| `{paths.api_routes}` | backend/app/api |

## Available Agents

### Core Agents

| Agent | Purpose |
|-------|---------|
| `@orchestrator` | Coordinates complex workflows across agents |
| `@backend-agent` | Backend development specialist |
| `@frontend-agent` | Frontend development specialist |
| `@qa-agent` | Code quality, testing, and review |

### Specialized Agents

| Agent | Purpose |
|-------|---------|
| `@ui-ux-agent` | User interface and experience design |
| `@api-sync-agent` | Validates backend/frontend API contracts |
| `@db-migration-agent` | Safe database schema changes |
| `@docs-agent` | Documentation maintenance |
| `@deploy-checker` | Pre-deployment readiness verification |
| `@devops-agent` | CI/CD and infrastructure operations |
| `@parallel-work-agent` | Concurrent development via Git worktrees |
| `@hebrew-validator` | RTL and Hebrew content validation |

## Using Agents

### Direct Agent Invocation

```
@backend-agent Create a new API endpoint for user preferences
```

### Orchestrated Workflows

```
@orchestrator Implement a new feature for exporting search results
```

### Workflow Commands

```
/project:new-feature
/project:fix-bug
/project:add-endpoint
/project:pre-deploy
```

## Long-Term Memory

The `PROJECT_MEMORY.md` file stores architectural decisions and project state. All agents follow the memory protocol:

1. **Read First**: Before any task, read PROJECT_MEMORY.md
2. **Update Last**: After significant changes, update PROJECT_MEMORY.md
3. **Respect Decisions**: Follow established patterns unless there's a strong reason not to

## Thinking Logs

Agents create thinking logs in `.claude/logs/` before complex operations:

```
.claude/logs/
├── orchestrator-2024-12-17-10-30-00.md
├── backend-agent-2024-12-17-10-35-00.md
└── qa-agent-2024-12-17-11-00-00.md
```

These logs document reasoning, decisions, and execution steps.

## Adapting for New Projects

1. Copy the `.claude/` directory to your new project
2. Edit `PROJECT.yaml` with your project's configuration
3. Update `PROJECT_MEMORY.md` with initial architectural decisions
4. Remove or adapt agents not relevant to your stack (e.g., `hebrew-validator` if not needed)

## Agent Prerequisites

Every agent starts with:

```markdown
## Prerequisites

Read project configuration first:

```bash
cat .claude/PROJECT.yaml
```
```

This ensures agents always have access to current configuration before starting work.

## Best Practices

1. **Keep PROJECT.yaml updated** when infrastructure changes
2. **Review thinking logs** for complex operations
3. **Use the orchestrator** for multi-system changes
4. **Run deploy-checker** before production deployments
5. **Keep PROJECT_MEMORY.md current** with key decisions
