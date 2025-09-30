# PyScaff: AI Workflow Orchestrator (MVID, Python + FastAPI)

## 0. Purpose
- Canonical, executable specification for the internal dogfooding (MVID) release.
- Aligns product intent, architecture, APIs, data contracts, validation rules, security, and observability.
- Ships with BDD (Gherkin), Storybook wiring, CI gates, repo bootstrap, and performance/load test recipes.
- Enforces SOTA agentic coding practices (schema-constrained AI, idempotent orchestration, structured telemetry).

## 1. Scope (MVID)
- YAML → validated Pydantic models.
- Executors: form, ai_generate, conditional, api_call, approval.
- Async orchestrator: idempotent step boundaries, auto-continuation, explicit wait-states.
- Persistence: Postgres (SQLite dev).
- APIs: workflow CRUD/validate; executions (start/resume/cancel/status); state (history/context); AI proxy.
- Observability: OpenTelemetry traces, structured logs, lifecycle events.

## 2. Out of Scope (Backlog)
- Visual builder, multi-tenancy, RBAC, SOC 2, connectors marketplace, advanced analytics, A/B testing, scheduling/webhooks, distributed workers, SSO.

## 3. Canonical Definitions
- Workflow: Named, DAG-like YAML with one start_step.
- Step: Typed unit (form, ai_generate, conditional, api_call, approval) with config.
- Run: Execution instance with evolving context/history and current status.
- Context: {static, profile, runtime} composite map.
- Wait-state: Paused run requiring external input (form/approval) with resume token.
- Idempotency key: Client-supplied key for safe replays of mutating ops.

## 4. Non-Functional Requirements
- Performance: p95 orchestrator overhead per non-LLM step < 150 ms; AI call success rate > 97%.
- Reliability: At-least-once step execution; transactional persistence; deterministic resumes.
- Security: API key/JWT (internal), secrets encryption at rest, log redaction of PII/secrets.
- Observability: Trace propagation (run_id, step_id); event log (run.*, step.*, ai.*); token/cost counters.
- Testability: Mock AI provider (deterministic), fixture workflows, dual-run parity harness.

## 5. API Surface (OpenAPI 3.1 — Authoritative Excerpt)
- Endpoints:
	- Workflows: POST /v1/workflows, GET/PUT/DELETE /v1/workflows/{id}, POST /v1/workflows/{id}/validate
	- Executions: POST /v1/executions, GET /v1/executions/{run_id}, POST /v1/executions/{run_id}/resume, POST /v1/executions/{run_id}/cancel
	- State: GET /v1/executions/{run_id}/history, GET /v1/executions/{run_id}/context
	- AI (internal): POST /v1/ai/infer

\```yaml
openapi: 3.1.0
info:
	title: Workflow Orchestrator (MVID)
	version: 0.2.0
paths:
	/v1/executions:
		post:
			summary: Start execution
			requestBody:
				required: true
				content:
					application/json:
						schema:
							$ref: '#/components/schemas/StartExecutionRequest'
			responses:
				'202':
					description: Accepted
					content:
						application/json:
							schema: { $ref: '#/components/schemas/Run' }
	/v1/executions/{run_id}/resume:
		post:
			parameters:
				- in: path
				  name: run_id
				  required: true
				  schema: { type: string }
			requestBody:
				required: true
				content:
					application/json:
						schema: { $ref: '#/components/schemas/ResumeRequest' }
			responses:
				'200':
					description: Resumed
					content:
						application/json:
							schema: { $ref: '#/components/schemas/Run' }
components:
	schemas:
		Workflow:
			type: object
			required: [id, version, name, definition, start_step, steps]
			properties:
				id: { type: string }
				version: { type: integer, minimum: 1 }
				name: { type: string, minLength: 1 }
				definition: { type: object, additionalProperties: true }
				start_step: { type: string }
				steps:
					type: array
					items: { $ref: '#/components/schemas/Step' }
		Step:
			type: object
			required: [id, type, name]
			properties:
				id: { type: string }
				type:
					type: string
					enum: [form, ai_generate, conditional, api_call, approval]
				name: { type: string }
				next: { type: string, nullable: true }
				config: { type: object, additionalProperties: true }
		StartExecutionRequest:
			type: object
			required: [workflow_id]
			properties:
				workflow_id: { type: string }
				inputs: { type: object, additionalProperties: true }
				run_opts:
					type: object
					properties:
						idempotency_key: { type: string }
						mock_ai: { type: boolean, default: false }
		Run:
			type: object
			required: [id, status, started_at, updated_at]
			properties:
				id: { type: string }
				status: { type: string, enum: [queued, running, waiting, completed, failed, canceled] }
				current_step: { type: string, nullable: true }
				started_at: { type: string, format: date-time }
				updated_at: { type: string, format: date-time }
		ResumeRequest:
			type: object
			properties:
				inputs: { type: object, additionalProperties: true }
				approvals:
					type: array
					items:
						type: object
						required: [step_id, approved]
						properties:
							step_id: { type: string }
							approved: { type: boolean }
							comment: { type: string }
\```

## 6. Data Contracts (Canonical)
- Workflow: id, version, name, definition (canonicalized YAML), start_step, steps[Step].
- Step (per type minimal):
	- form: config.fields [{key, type, required, pattern?}]
	- ai_generate: config.template_id (str), variables (str[]), json_schema (JSON Schema 2020-12)
	- conditional: config.when (sandboxed expr)
	- api_call: config.url (templated), method (GET|POST|PUT|PATCH|DELETE), headers?, body?, timeout_s?
	- approval: config.approvers (emails[])
- Run: id, workflow_id, workflow_version, status, current_step?, context (obj), started_at/updated_at, idempotency_key?.
- RunStep: id, run_id, step_id, type, status, started_at, ended_at?, output (obj), error?.

## 7. Event & Telemetry (Authoritative)
- Events:
	- run.created, run.started, run.waiting, run.resumed, run.completed, run.failed
	- step.started, step.completed, step.failed
	- ai.request, ai.response
- ai.response attributes (required): provider, template_id, template_version, tokens_prompt, tokens_output, latency_ms, retry_count.

## 8. Repo Bootstrap (Canon)
- Directory layout:
\```text
/workflow-orchestrator-py
	/app
		/main.py
		/routers
		/models
		/engine
		/executors
		/agent
		/db
			/migrations
				/versions
		/observability
	/tests
		/unit
		/integration
	/.github/workflows
	/scripts
pyproject.toml
Makefile
docker-compose.yml
.env.example
README.md
\```

- pyproject.toml (minimal, pinned where prudent):
\```toml
[project]
name = "workflow-orchestrator-py"
version = "0.2.0"
requires-python = ">=3.12"
dependencies = [
	"fastapi>=0.115.0",
	"uvicorn[standard]>=0.30.0",
	"pydantic>=2.8.0",
	"httpx>=0.27.0",
	"SQLAlchemy>=2.0.32",
	"alembic>=1.13.2",
	"psycopg[binary]>=3.2.1",
	"jinja2>=3.1.4",
	"opentelemetry-api>=1.27.0",
	"opentelemetry-sdk>=1.27.0",
	"opentelemetry-instrumentation-fastapi>=0.48b0",
	"python-dotenv>=1.0.1"
]

[project.optional-dependencies]
dev = ["pytest>=8.3.2","anyio>=4.4.0","ruff>=0.6.5","mypy>=1.11.1","pip-audit>=2.7.3","locust>=2.31.3","schemathesis>=3.35.6","speccy>=0.11.0"]

[tool.ruff]
line-length = 100
select = ["E","F","I","UP","B"]
\```

- Makefile:
\```make
.PHONY: dev lint type test migrate seed audit spec-check perf

dev:
	uvicorn app.main:app --reload --port 8000

lint:
	ruff check .
	ruff format --check .

type:
	mypy app

test:
	pytest -q

migrate:
	alembic upgrade head

seed:
	python scripts/seed_workflows.py

audit:
	pip-audit -s

spec-check:
	npx spectral lint openapi.yaml || true

perf:
	locust -f tests/perf/locustfile.py
\```

- docker-compose.yml (dev):
\```yaml
version: "3.9"
services:
	api:
		build: .
		environment:
			- DATABASE_URL=postgresql+psycopg://app:app@db:5432/app
			- AI_PROVIDER=mock
			- OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
		ports:
			- "8000:8000"
		depends_on: [db]
	db:
		image: postgres:16
		environment:
			- POSTGRES_USER=app
			- POSTGRES_PASSWORD=app
			- POSTGRES_DB=app
		ports:
			- "5432:5432"
	otel-collector:
		image: otel/opentelemetry-collector:0.99.0
		command: ["--config=/etc/otel-collector-config.yaml"]
		volumes:
			- ./infra/otel-collector-config.yaml:/etc/otel-collector-config.yaml
\```

- .env.example:
\```dotenv
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app
AI_PROVIDER=mock
OPENAI_API_KEY=replace-me-for-real-provider
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
JWT_SECRET=dev-only-not-for-prod
LOG_LEVEL=INFO
\```

## 9. CI Workflow (GitHub Actions)
\```yaml
name: ci
on: [push, pull_request]
jobs:
	build-test:
		runs-on: ubuntu-latest
		steps:
			- uses: actions/checkout@v4
			- uses: actions/setup-python@v5
			  with: { python-version: "3.12" }
			- run: pip install -U pip
			- run: pip install -e ".[dev]"
			- name: Lint
			  run: make lint
			- name: Type-check
			  run: make type
			- name: Unit/Integration Tests
			  run: make test
			- name: API Contract Lint (Spectral)
			  run: make spec-check
			- name: Security Audit
			  run: make audit
\```

## 10. Migration & Versioning Rules (YAML)
- Canonical YAML schema uses semver (major.minor.patch).
- Breaking changes require major bump; engine rejects workflows tagged with future-major versions.
- Provide upgrade CLI:
	- `scripts/upgrade_yaml.py --from 0.1 --to 0.2 --in workflow.yml --out workflow.v0.2.yml`

## 11. Deterministic Mock AI Provider
- Modes: success (default), schema_violation, timeout, transient_error.
- Config via env: `MOCK_AI_MODE=success|schema_violation|timeout|transient_error`; `MOCK_AI_SEED=42`.
- Sample outputs:
\```json
{ "subject": "Test Subject", "body": "Hello World" }
\```
- Behavior:
	- schema_violation: drop required key.
	- timeout: sleep > configured timeout.
	- transient_error: fail once, succeed on retry.

## 12. Dual-Run Parity Harness (Old TS ↔ New PY)
- Endpoint (dev-only): POST /v1/dev/dual-run
- Request:
	- { workflow_id: string, inputs?: object, run_opts?: { mock_ai?: boolean } }
- Response:
	- { match: boolean, diffs: Diff[], normalization: { ordering: "stable", whitespace: "trim+single-space", numeric_tolerance: 1e-6 }, run_ids: { old: string, new: string } }
- Normalization rules:
	1. Sort object keys; stable sort arrays unless order is semantically meaningful (declare exceptions by path).
	2. Trim whitespace; collapse multi-space to single; normalize newlines to `\n`.
	3. Compare numeric fields with absolute tolerance 1e-6.
- Pass criteria:
	- `match == true` or `diffs.length == 0`.
	- If only non-semantic diffs remain (whitespace/order-only), treat as pass.

## 13. Storybook ↔ API Wiring (MSW)
- Handlers aligned to Gherkin fixtures; lives in `/stories/mocks/handlers.ts`.
- Example MSW handlers:
\```ts
import { http, HttpResponse } from 'msw';

export const handlers = [
	http.post('/v1/executions', async ({ request }) => {
		return HttpResponse.json({ id: 'run_123', status: 'waiting', current_step: 'form', started_at: new Date().toISOString(), updated_at: new Date().toISOString() }, { status: 202 });
	}),
	http.post('/v1/executions/run_123/resume', async ({ request }) => {
		const body = await request.json();
		if (body.inputs) {
			return HttpResponse.json({ id: 'run_123', status: 'waiting', current_step: 'approval', started_at: '2025-01-01T00:00:00Z', updated_at: new Date().toISOString() });
		}
		if (body.approvals) {
			return HttpResponse.json({ id: 'run_123', status: 'completed', current_step: null, started_at: '2025-01-01T00:00:00Z', updated_at: new Date().toISOString() });
		}
		return HttpResponse.json({ message: 'Bad Request' }, { status: 400 });
	}),
];
\```

- Fixture JSON (aligns to Gherkin):
\```json
{
	"valid_workflow": {
		"name": "Content Draft Flow",
		"start_step": "collect",
		"steps": [
			{ "id": "collect", "type": "form", "name": "Brief", "next": "generate", "config": { "fields": [ { "key": "topic", "type": "string", "required": true }, { "key": "audience", "type": "string", "required": true } ] } },
			{ "id": "generate", "type": "ai_generate", "name": "Generate Draft", "next": "approve", "config": { "template_id": "content_v1", "variables": ["topic","audience"], "json_schema": { "type": "object", "properties": { "draft": { "type": "string" } }, "required": ["draft"] } } },
			{ "id": "approve", "type": "approval", "name": "Approve", "config": { "approvers": ["dev-internal@example.com"] } }
		]
	}
}
\```

## 14. Performance SLOs & Load Test Recipe
- Tool: Locust; target endpoints: /v1/executions (start), /v1/executions/{id}/resume (form → approval).
- Success conditions:
	- p95 latency for non-LLM steps < 150 ms.
	- Error rate < 1% over 10-minute ramp.
- Locust file:
\```python
from locust import HttpUser, task, between
class OrchestratorUser(HttpUser):
	wait_time = between(0.1, 0.5)

	@task
	def start_and_resume(self):
		r = self.client.post("/v1/executions", json={"workflow_id": "content_draft_flow"})
		assert r.status_code in (202, 200)
		run = r.json()
		if run.get("status") == "waiting" and run.get("current_step") == "form":
			resume = self.client.post(f"/v1/executions/{run['id']}/resume", json={"inputs": {"topic":"Launch","audience":"SMB"}})
			assert resume.status_code == 200
\```

## 15. DB Schema Snapshot (Alembic #0001 + DDL)
- Alembic migration file `/app/db/migrations/versions/0001_init.py`:
\```python
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
	op.create_table(
		"workflows",
		sa.Column("id", sa.Text, primary_key=True),
		sa.Column("version", sa.Integer, nullable=False),
		sa.Column("name", sa.Text, nullable=False),
		sa.Column("definition", sa.JSON, nullable=False),
		sa.Column("start_step", sa.Text, nullable=False),
	)
	op.create_table(
		"runs",
		sa.Column("id", sa.Text, primary_key=True),
		sa.Column("workflow_id", sa.Text, nullable=False),
		sa.Column("workflow_version", sa.Integer, nullable=False),
		sa.Column("status", sa.Text, nullable=False),
		sa.Column("current_step", sa.Text, nullable=True),
		sa.Column("context", sa.JSON, nullable=True),
		sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
		sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
		sa.Column("idempotency_key", sa.Text, nullable=True),
	)
	op.create_table(
		"run_steps",
		sa.Column("id", sa.Text, primary_key=True),
		sa.Column("run_id", sa.Text, sa.ForeignKey("runs.id"), nullable=False),
		sa.Column("step_id", sa.Text, nullable=False),
		sa.Column("type", sa.Text, nullable=False),
		sa.Column("status", sa.Text, nullable=False),
		sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
		sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
		sa.Column("output", sa.JSON, nullable=True),
		sa.Column("error", sa.Text, nullable=True),
	)

def downgrade():
	op.drop_table("run_steps")
	op.drop_table("runs")
	op.drop_table("workflows")
\```

- SQL DDL (for quick bootstrap):
\```sql
CREATE TABLE IF NOT EXISTS workflows (
	id TEXT PRIMARY KEY,
	version INT NOT NULL,
	name TEXT NOT NULL,
	definition JSONB NOT NULL,
	start_step TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
	id TEXT PRIMARY KEY,
	workflow_id TEXT NOT NULL,
	workflow_version INT NOT NULL,
	status TEXT NOT NULL,
	current_step TEXT,
	context JSONB,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	idempotency_key TEXT
);
CREATE TABLE IF NOT EXISTS run_steps (
	id TEXT PRIMARY KEY,
	run_id TEXT NOT NULL REFERENCES runs(id),
	step_id TEXT NOT NULL,
	type TEXT NOT NULL,
	status TEXT NOT NULL,
	started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	ended_at TIMESTAMPTZ,
	output JSONB,
	error TEXT
);
\```

## 16. Security & Redaction Rules (Executable Guidance)
- Redaction targets: API keys, bearer tokens, emails, phone numbers, SSNs, access tokens, secrets, credit cards.
- Pseudocode (middleware):
\```python
REDACT_PATTERNS = [
	(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "authorization: Bearer [REDACTED]"),
	(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}['\"]?", r"\1: [REDACTED]"),
	(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]"),
	(r"\b(?:\+?1[-.\s]?)?$begin:math:text$?\\d{3}$end:math:text$?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
	(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
	(r"\b(?:\d[ -]*?){13,19}\b", "[REDACTED_PAN]")
]
def redact(s: str) -> str:
	for pat, repl in REDACT_PATTERNS:
		s = re.sub(pat, repl, s)
	return s
\```
- Logging guideline: never log request/response bodies for `ai.infer` or `api_call` without redaction; attach hashes or IDs instead.

## 17. Conditional Evaluator (Safe)
- Allowed operations: boolean, comparison, numeric ops; no attribute access beyond provided context; whitelisted functions only (e.g., `len`, `any`, `all`).
- Sandbox selection: `asteval` in restricted mode or custom AST walker.
- Rule: expressions evaluated against a **frozen** copy of context; no side effects.
- Example safe evaluation:
\```python
ALLOWED_NODES = {"BoolOp","UnaryOp","BinOp","Compare","Name","Load","Constant","Subscript","And","Or","NotEq","Eq","Gt","Lt","GtE","LtE"}
\```

## 18. BDD — Gherkin (Executable)
\```gherkin
Feature: Workflow Creation
	Scenario: Create valid workflow
		Given a valid YAML workflow
		When I POST it to /v1/workflows
		Then status 201
		And body includes id, version

	Scenario: Reject invalid workflow
		Given a YAML missing start_step
		When I POST it
		Then status 422
		And error mentions "start_step"
\```

\```gherkin
Feature: Run Execution
	Scenario: Start to waiting on form
		When I POST /v1/executions
		Then status 202
		And run status "waiting"
		And current_step "form"

	Scenario: Resume with inputs to approval
		Given run is waiting on "form"
		When I POST /v1/executions/{run}/resume with inputs
		Then run status "waiting"
		And current_step "approval"
\```

\```gherkin
Feature: AI Schema Enforcement
	Scenario: AI returns invalid
		Given ai_generate expects {subject, body}
		And provider returns only body
		When executed
		Then retried up to 2
		And if still invalid run fails
\```

\```gherkin
Feature: Idempotency
	Scenario: Replay with same key
		When I POST /v1/executions with key=abc123 twice
		Then both return same run_id
		And only one run created
\```

## 19. Storybook Example (Parity with BDD)
\```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { FormRenderer } from './FormRenderer';
import { setupWorker } from 'msw/browser';
import { handlers } from './mocks/handlers';

const meta: Meta<typeof FormRenderer> = { title: 'MVID/FormRenderer', component: FormRenderer };
export default meta;

const worker = setupWorker(...handlers);
worker.start();

export const Default: StoryObj<typeof FormRenderer> = {
	args: {
		fields: [
			{ key: 'topic', type: 'string', required: true },
			{ key: 'audience', type: 'string', required: true }
		]
	}
};
\```

## 20. Governance & Versioning
- SSOT version: v0.3.0 (this document).
- Any change requires synchronized updates to:
	1. SSOT (this doc)
	2. OpenAPI + Pydantic models
	3. Gherkin feature files
	4. Storybook mocks/stories
	5. CI gates if applicable
- ADRs maintained in `/docs/adr`:
	- ADR-001: Python/FastAPI greenfield core
	- ADR-002: JSON-schema-enforced AI outputs
	- ADR-003: Minimal executor set for MVID
	- ADR-004: BDD + Storybook required for merge
	- ADR-005: Dual-run parity normalization rules

## 21. Ready-to-Dogfood Exit Criteria
1. Define/validate workflow via API from YAML.
2. Start run → wait on form → resume → ai_generate → approval → complete.
3. Mock and real AI paths function; schema enforcement active; retries observable.
4. OpenTelemetry traces and lifecycle events emitted with required attributes.
5. Storybook components mirror BDD fixtures; MSW handlers pass acceptance flows.
6. CI: lint, type, tests, contract lint, audit → green.
7. Dual-run parity ≥ 95% for seed workflows under normalization rules.