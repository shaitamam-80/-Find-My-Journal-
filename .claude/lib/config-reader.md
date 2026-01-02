# Configuration Reader

## How to Use Project Configuration

At the start of every task, read the project configuration:

```bash
cat .claude/PROJECT.yaml
```

## Variable Reference

Use these patterns to reference configuration values:

| Reference | Example Value |
|-----------|---------------|
| project.name | Find My Journal |
| project.slug | find-my-journal |
| stack.backend.path | backend |
| stack.frontend.path | frontend |
| stack.frontend.env_prefix | VITE_ |
| deployment.backend.platform | railway |
| deployment.frontend.platform | vercel |

## Common Commands by Stack

### FastAPI Backend
```bash
cd {stack.backend.path}
uvicorn {stack.backend.entry_point} --reload --port {stack.backend.port}
```

### Vite Frontend
```bash
cd {stack.frontend.path}
npm run dev
```

### Next.js Frontend
```bash
cd {stack.frontend.path}
npm run dev
```

## Environment Variable Patterns

- Vite: VITE_*
- Next.js: NEXT_PUBLIC_*
- Create React App: REACT_APP_*

## Path References

When working with files, use paths from PROJECT.yaml:

| Reference | Purpose |
|-----------|---------|
| paths.api_routes | Backend API route files |
| paths.models | Backend data models |
| paths.services | Backend service layer |
| paths.components | Frontend React components |
| paths.pages | Frontend page components |
| paths.types | Frontend TypeScript types |
| paths.api_service | Frontend API client |

## Stack-Specific Patterns

### Backend Commands
```bash
# Run tests
cd {stack.backend.path} && {stack.backend.test_command}

# Run linter
cd {stack.backend.path} && {stack.backend.lint_command}

# Start server
cd {stack.backend.path} && uvicorn {stack.backend.entry_point} --reload --port {stack.backend.port}
```

### Frontend Commands
```bash
# Build
cd {stack.frontend.path} && {stack.frontend.build_command}

# Test
cd {stack.frontend.path} && {stack.frontend.test_command}

# Lint
cd {stack.frontend.path} && {stack.frontend.lint_command}
```

## Database Commands

```bash
# Check migrations
ls -la {stack.database.migrations_path}/

# View schema
cat {stack.database.schema_file}
```

## Deployment Information

| Component | Platform | Branch |
|-----------|----------|--------|
| Backend | {deployment.backend.platform} | {deployment.backend.auto_deploy_branch} |
| Frontend | {deployment.frontend.platform} | {deployment.frontend.auto_deploy_branch} |
