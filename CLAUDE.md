# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyScaff is an AI workflow orchestrator built with Python + FastAPI. This is the MVID (Minimum Viable Internal Dogfood) release - a canonical, executable specification designed for internal use.

**Core Purpose**: Orchestrate multi-step workflows with YAML definitions, async execution, wait-states, and AI integration. Think GitHub Actions + Temporal + LangChain, but optimized for agentic AI coding patterns.

## Tech Stack

- **Runtime**: Python 3.12+
- **Framework**: FastAPI + Uvicorn
- **Validation**: Pydantic 2.8+
- **Database**: PostgreSQL (production), SQLite (dev)
- **ORM**: SQLAlchemy 2.0 + Alembic migrations
- **HTTP Client**: httpx
- **Observability**: OpenTelemetry (traces, structured logs)
- **Testing**: pytest, Locust (perf), schemathesis (contract)
- **Linting**: ruff + mypy
- **AI Provider**: OpenAI (production) / Mock (dev/test)

## Development Commands

```bash
# Install dependencies (editable mode with dev extras)
pip install -e ".[dev]"

# Run dev server with hot reload
make dev
# OR: uvicorn app.main:app --reload --port 8000

# Linting & formatting
make lint         # ruff check + format check
ruff check .      # lint only
ruff format .     # auto-format

# Type checking
make type         # mypy app

# Testing
make test         # pytest all tests
pytest -q         # quick mode
pytest tests/unit/test_engine.py::test_idempotent_step  # single test
pytest -k "workflow"  # pattern match

# Database migrations
make migrate      # alembic upgrade head
alembic revision --autogenerate -m "add_new_column"  # create migration
alembic downgrade -1  # rollback one migration

# Seed workflows for testing
make seed         # python scripts/seed_workflows.py

# Security audit
make audit        # pip-audit

# API contract validation
make spec-check   # spectral lint openapi.yaml

# Performance/load testing
make perf         # locust -f tests/perf/locustfile.py
```

## Docker Development

```bash
# Start full stack (API + Postgres + OTEL collector)
docker-compose up

# Database only (for local API dev)
docker-compose up db

# Clean restart
docker-compose down -v && docker-compose up
```

## Architecture Overview

### Core Concepts

1. **Workflow**: Named DAG defined in YAML/JSON. Contains steps and start_step.
2. **Step**: Typed execution unit (form, ai_generate, conditional, api_call, approval).
3. **Run**: Execution instance tracking status, context, current_step, history.
4. **Context**: Composite map of {static, profile, runtime} data passed between steps.
5. **Wait-state**: Paused run requiring external input (form/approval) with resume token.
6. **Idempotency**: Client-supplied key ensures safe replays of mutating operations.

### Step Types (Executors)

- **form**: Collect user input via fields config; validates against schema; pauses run.
- **ai_generate**: Call AI with template + variables + json_schema; retries on schema violations (max 2).
- **conditional**: Evaluate sandboxed expression (`asteval`) against context; route to next step.
- **api_call**: HTTP request (GET/POST/PUT/PATCH/DELETE) with templated URL/headers/body.
- **approval**: Notify approvers (emails); pause run; track approval/rejection + comments.

### Directory Structure

```
/workflow-orchestrator-py
  /app
    main.py                # FastAPI app entry
    /routers               # API route handlers (workflows, executions, state, ai)
    /models                # Pydantic schemas (Workflow, Run, Step, etc.)
    /engine                # Orchestration logic (start, resume, step execution)
    /executors             # Step type implementations (form, ai_generate, etc.)
    /agent                 # AI provider abstraction (OpenAI, Mock)
    /db
      /migrations          # Alembic migration files
        /versions
    /observability         # OpenTelemetry setup, log redaction
  /tests
    /unit                  # Unit tests (executors, models, engine)
    /integration           # API integration tests (workflows, runs)
    /perf                  # Locust load tests
  /.github/workflows       # CI (lint, type, test, audit, spec-check)
  /scripts                 # Seed data, YAML upgrade tools
  /docs/adr                # Architecture Decision Records
  pyproject.toml           # Dependencies + tooling config
  Makefile                 # Dev commands
  docker-compose.yml       # Local stack
  .env.example             # Environment template
```

### Key Architectural Patterns

**1. Async Orchestration**
- Engine runs steps sequentially per run; uses async/await for I/O (DB, HTTP, AI).
- Steps are idempotent boundaries; failures roll back to last completed step.
- Auto-continuation: engine polls waiting runs and resumes when inputs arrive.

**2. Schema-Constrained AI**
- All `ai_generate` steps declare JSON Schema (2020-12) in config.
- Engine validates AI response; retries up to 2x on schema violations.
- Mock AI provider (deterministic) for dev/test; real OpenAI for production.

**3. Observability**
- OpenTelemetry traces: run_id, step_id propagated to all spans.
- Lifecycle events: `run.created`, `run.started`, `run.waiting`, `run.resumed`, `run.completed`, `run.failed`, `step.started`, `step.completed`, `step.failed`, `ai.request`, `ai.response`.
- Required `ai.response` attributes: provider, template_id, template_version, tokens_prompt, tokens_output, latency_ms, retry_count.
- Log redaction: strips API keys, tokens, emails, SSNs, credit cards before persistence.

**4. Transactional Persistence**
- SQLAlchemy sessions wrap step execution; rollback on error.
- Idempotency keys (SHA256 of workflow_id + inputs) dedupe start requests.
- `runs` table tracks status, current_step, context; `run_steps` logs execution history.

**5. Security**
- API key/JWT auth (internal only for MVID).
- Secrets encrypted at rest (planned; not in MVID).
- Conditional evaluator uses sandboxed AST walker (whitelist: boolean, comparison, numeric ops; no attribute access).

## API Endpoints

### Workflows
- `POST /v1/workflows` - Create workflow from YAML/JSON
- `GET /v1/workflows/{id}` - Retrieve workflow definition
- `PUT /v1/workflows/{id}` - Update workflow (creates new version)
- `DELETE /v1/workflows/{id}` - Delete workflow
- `POST /v1/workflows/{id}/validate` - Validate YAML structure

### Executions
- `POST /v1/executions` - Start workflow run (returns 202 Accepted)
- `GET /v1/executions/{run_id}` - Get run status
- `POST /v1/executions/{run_id}/resume` - Resume waiting run with inputs/approvals
- `POST /v1/executions/{run_id}/cancel` - Cancel running/waiting run

### State
- `GET /v1/executions/{run_id}/history` - Step execution history
- `GET /v1/executions/{run_id}/context` - Current context snapshot

### AI (Internal)
- `POST /v1/ai/infer` - Direct AI inference (internal dev tool)

### Dev-Only
- `POST /v1/dev/dual-run` - Run workflow in old TS + new PY, compare outputs

## Data Models

### Workflow
```python
{
  "id": str,              # unique identifier
  "version": int,         # semver major.minor.patch
  "name": str,            # human-readable name
  "definition": dict,     # canonical YAML as JSON
  "start_step": str,      # ID of first step
  "steps": [Step]         # step definitions
}
```

### Step
```python
{
  "id": str,              # step identifier
  "type": str,            # form | ai_generate | conditional | api_call | approval
  "name": str,            # display name
  "next": str | None,     # next step ID (None = terminal)
  "config": dict          # type-specific configuration
}
```

**Step Config Schemas**:
- **form**: `{"fields": [{"key": str, "type": str, "required": bool, "pattern": str?}]}`
- **ai_generate**: `{"template_id": str, "variables": [str], "json_schema": {...}}`
- **conditional**: `{"when": str}`  # sandboxed expression
- **api_call**: `{"url": str, "method": str, "headers": dict?, "body": dict?, "timeout_s": int?}`
- **approval**: `{"approvers": [str]}`  # emails

### Run
```python
{
  "id": str,              # run identifier (uuid)
  "workflow_id": str,     # workflow reference
  "workflow_version": int,
  "status": str,          # queued | running | waiting | completed | failed | canceled
  "current_step": str?,   # step currently executing/waiting
  "context": dict,        # {static, profile, runtime}
  "started_at": datetime,
  "updated_at": datetime,
  "idempotency_key": str? # client-supplied dedup key
}
```

### RunStep
```python
{
  "id": str,              # step execution ID
  "run_id": str,          # parent run
  "step_id": str,         # step definition reference
  "type": str,            # step type
  "status": str,          # pending | running | completed | failed
  "started_at": datetime,
  "ended_at": datetime?,
  "output": dict?,        # step result
  "error": str?           # failure message
}
```

## Testing Strategy

### BDD (Gherkin)
Feature files in `/tests/features/` drive acceptance tests:
- Workflow creation/validation
- Run execution (start → waiting → resume → complete)
- AI schema enforcement + retries
- Idempotency key deduplication

### Storybook Mocks (MSW)
Mock Service Worker handlers in `/stories/mocks/handlers.ts` align with Gherkin fixtures.
Must be updated in lockstep with API changes.

### Performance SLOs
- **p95 orchestrator overhead per non-LLM step**: < 150ms
- **AI call success rate**: > 97%
- **Error rate**: < 1% over 10-minute ramp
- **Tool**: Locust (`make perf`)

### Dual-Run Parity Harness
- Dev endpoint: `POST /v1/dev/dual-run`
- Runs workflow in old TS engine + new PY engine; compares outputs.
- Normalization rules: sort keys, trim whitespace, numeric tolerance 1e-6.
- **Pass criteria**: `match == true` or only non-semantic diffs (whitespace/order).

## Environment Variables

See `.env.example` for full list:

```bash
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app  # or sqlite:///./app.db
AI_PROVIDER=mock                    # mock | openai
OPENAI_API_KEY=sk-...               # required if AI_PROVIDER=openai
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
JWT_SECRET=dev-only-not-for-prod    # use secure random in prod
LOG_LEVEL=INFO                      # DEBUG | INFO | WARNING | ERROR
MOCK_AI_MODE=success                # success | schema_violation | timeout | transient_error
MOCK_AI_SEED=42                     # deterministic RNG seed for mock
```

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):
1. Lint (ruff)
2. Type-check (mypy)
3. Unit + integration tests (pytest)
4. API contract lint (spectral)
5. Security audit (pip-audit)

**Merge criteria**: All checks green + Gherkin coverage for new endpoints.

## Migration & Versioning

- Workflow YAML schema uses semver (major.minor.patch).
- Breaking changes require major version bump.
- Upgrade tool: `scripts/upgrade_yaml.py --from 0.1 --to 0.2 --in workflow.yml --out workflow.v0.2.yml`
- Engine rejects workflows tagged with future-major versions.

## Mock AI Provider Modes

Controlled via `MOCK_AI_MODE` env var:
- **success**: Returns valid JSON matching schema (default)
- **schema_violation**: Drops required key; triggers retry logic
- **timeout**: Sleeps beyond configured timeout
- **transient_error**: Fails once, succeeds on retry (tests backoff)

Seed determinism: `MOCK_AI_SEED=42` for reproducible outputs.

## Security & Redaction

**Log Redaction Patterns** (applied before persistence):
- Authorization headers: `authorization: Bearer [REDACTED]`
- API keys/tokens/secrets: `api_key: [REDACTED]`
- Emails: `[REDACTED_EMAIL]`
- Phone numbers: `[REDACTED_PHONE]`
- SSNs: `[REDACTED_SSN]`
- Credit cards: `[REDACTED_PAN]`

**Never log**:
- Raw request/response bodies for `ai.infer` or `api_call` without redaction
- Use hashes or IDs instead

## Common Pitfalls

1. **Forgetting to run migrations**: `make migrate` before starting API.
2. **Database connection errors**: Ensure Postgres is running (`docker-compose up db`).
3. **AI provider not set**: Default is `AI_PROVIDER=mock`; set `OPENAI_API_KEY` for real calls.
4. **Step config validation**: Each step type has strict Pydantic schema; check error messages.
5. **Idempotency keys**: Must be unique per workflow_id + inputs combo; reuse returns existing run.
6. **Conditional expressions**: Use sandboxed syntax only (no attribute access, limited functions).
7. **OTEL not collecting**: Check `OTEL_EXPORTER_OTLP_ENDPOINT` and collector is running.

## Work Management Strategy

### GitHub-First Workflow (REQUIRED)

**Source of Truth Hierarchy:**
1. **GitHub Issues** - All active work packages, bugs, features
2. **GitHub Projects** - Sprint planning, milestones, progress tracking
3. **Local markdown** - Ephemeral planning, AI context, completed summaries

**Work Package Lifecycle:**
```bash
# 1. Create GitHub issue FIRST
gh issue create --title "WP-XXX: [Task]" --label "P0,sprint-1"

# 2. Create feature branch
git checkout -b feature/WP-XXX-description

# 3. Work locally, commit references issue
git commit -m "feat: implement X

Fixes #123"

# 4. PR auto-closes issue on merge
gh pr create --title "WP-XXX: [Task]" --body "Fixes #123"
```

**Local Markdown Usage:**
- ✅ `CLAUDE.md` - AI session context (this file)
- ✅ `docs/adr/ADR-XXX.md` - Architecture decisions (permanent)
- ✅ `docs/work-package-wrapups/WP-XXX-completion.md` - Post-work summaries (optional)
- ✅ `docs/scratch/YYYYMMDD-*.md` - Session brainstorming (ephemeral, gitignored)
- ❌ `todo.md` or local task lists (use GitHub issues instead)

**Why GitHub-First:**
- Searchable history across context resets
- Links commits → PRs → issues → milestones
- Industry standard (portable knowledge)
- Audit trail for decisions
- Survives AI session resets

## Governance

**Single Source of Truth**: `pyscaff-prd.md` (v0.3.0)

Any change requires synchronized updates to:
1. PRD (this document)
2. OpenAPI spec + Pydantic models
3. Gherkin feature files
4. Storybook mocks/stories
5. CI gates (if applicable)
6. **GitHub issue tracking the work**

**Architecture Decision Records** in `/docs/adr`:
- ADR-001: Python/FastAPI greenfield core
- ADR-002: JSON-schema-enforced AI outputs
- ADR-003: Minimal executor set for MVID
- ADR-004: BDD + Storybook required for merge
- ADR-005: Dual-run parity normalization rules

## Exit Criteria (Dogfood-Ready)

1. ✅ Define/validate workflow via API from YAML
2. ✅ Start run → wait on form → resume → ai_generate → approval → complete
3. ✅ Mock and real AI paths; schema enforcement + retries observable
4. ✅ OpenTelemetry traces + lifecycle events with required attributes
5. ✅ Storybook components mirror BDD fixtures; MSW handlers pass acceptance
6. ✅ CI green: lint, type, tests, contract lint, audit
7. ✅ Dual-run parity ≥ 95% for seed workflows under normalization rules
