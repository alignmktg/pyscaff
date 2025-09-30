# PyScaff: AI Workflow Orchestrator
## Comprehensive Technical & Strategic Exploration

**Version:** 1.0
**Date:** September 30, 2025
**Audience:** Product Leaders, Technical Leaders, Engineering Teams
**Purpose:** Deep exploration of PyScaff's market position, architecture, and implementation strategy

---

## Executive Summary

### The Problem

The AI revolution of 2024-2025 has created a critical infrastructure gap. Organizations are racing to build AI-powered workflows, but existing tools fall short:

- **Traditional orchestrators** (Temporal, Airflow) treat AI as just another HTTP call, missing AI-specific needs like schema enforcement and prompt versioning
- **AI frameworks** (LangChain, AutoGPT) run workflows in-memory with no durable state, making them unsuitable for long-running processes
- **No-code platforms** (Zapier, n8n) lack the sophistication for complex AI orchestration and human approval loops
- **Cloud services** (AWS Step Functions) are expensive and create vendor lock-in

The core problem: **AI outputs are probabilistic and unreliable without structural constraints, yet workflows need deterministic execution guarantees.**

### The Solution

PyScaff is a **schema-first AI workflow orchestrator** that combines the best of three worlds:

1. **Declarative workflows** (YAML-based, like GitHub Actions)
2. **Durable execution** (transactional state persistence, like Temporal)
3. **AI-native primitives** (JSON Schema-enforced outputs, automatic retries)

Key differentiators:
- **Schema enforcement**: All AI outputs validated against JSON Schema with automatic retries (2x max)
- **Wait-states**: Workflows pause for human input (forms, approvals) and resume on-demand
- **Idempotent execution**: Client-supplied keys prevent duplicate runs, safe retry semantics
- **Observability-first**: OpenTelemetry traces with AI cost tracking (tokens, latency, retry counts)
- **Human-in-the-loop**: Built-in approval steps with comment tracking for compliance workflows

### Strategic Positioning

PyScaff occupies a unique market position:

| Capability | Temporal | LangChain | Zapier | Step Functions | **PyScaff** |
|---|---|---|---|---|---|
| Durable execution | ✅ | ❌ | ✅ | ✅ | ✅ |
| AI-native | ❌ | ✅ | ⚠️ | ❌ | ✅ |
| Schema enforcement | ❌ | ❌ | ❌ | ❌ | ✅ |
| Declarative (YAML) | ❌ | ❌ | ✅ | ✅ | ✅ |
| Human-in-the-loop | ⚠️ | ❌ | ⚠️ | ⚠️ | ✅ |
| Open source | ✅ | ✅ | ❌ | ❌ | ✅ |

This is genuine whitespace. No competitor combines all six capabilities.

### Business Model & Unit Economics

The architecture supports multiple monetization strategies:

1. **Usage-based pricing**: $X per 1,000 orchestrator steps + pass-through AI costs (margin on markup)
2. **Seat-based pricing**: $Y per workflow creator/month (SaaS standard)
3. **Enterprise licensing**: Flat fee for self-hosted deployment with support

**Cost structure:**
- Variable costs: AI API calls (OpenAI, Anthropic) - 70-80% of COGS
- Fixed costs: Infrastructure (Postgres, compute), development, compliance (SOC2)
- Margin lever: Orchestrator efficiency (target: p95 < 150ms = minimal overhead)

The observability layer tracks `tokens_prompt`, `tokens_output`, and `latency_ms` per AI call, enabling precise cost attribution and optimization recommendations. This is the foundation for usage-based pricing.

### Go-to-Market Strategy

**Phase 1: Internal Dogfooding (MVID)** ← Current focus
- Build for internal use at ThinkingWith.ai
- Validate core hypothesis: schema-enforced AI workflows solve real problems
- Exit criteria: 7 workflows running in production, p95 < 150ms, ≥95% dual-run parity

**Phase 2: Private Beta (Months 4-6)**
- 10-20 design partners from AI application builders
- Add visual workflow builder (no-code interface)
- Implement multi-tenancy + basic RBAC
- Collect feedback on pricing, prioritize connectors

**Phase 3: Public Launch (Months 7-12)**
- Open-source core engine (Apache 2.0)
- Freemium model: Free tier (100 runs/month), paid tiers with SLA
- Connectors marketplace (Slack, GitHub, Google Sheets, Airtable)
- Enterprise tier with SOC2, SSO, on-prem deployment

**Phase 4: Ecosystem Play (Year 2+)**
- Template marketplace (community-contributed workflows)
- Partner integrations (Zapier, Make, n8n import/export)
- AI provider partnerships (OpenAI, Anthropic, Cohere)
- Consulting/services for enterprise implementations

---

## Market Analysis

### Market Size & Opportunity

**Total Addressable Market (TAM):**
- Workflow automation market: $8.5B (2024), growing 18% CAGR
- AI developer tools market: $4.2B (2024), growing 42% CAGR
- PyScaff sits at intersection: **Serviceable market ~$2B by 2027**

**Customer Segments:**

1. **AI Application Builders** (Primary)
   - Startups building AI products (chatbots, content generation, data enrichment)
   - Pain: LangChain is too low-level, need workflow orchestration
   - Willingness to pay: High ($500-2000/month)

2. **Internal Tools Teams** (Secondary)
   - Mid-market/enterprise companies automating internal processes
   - Pain: Zapier is too simple, Temporal is too complex
   - Willingness to pay: Medium ($200-500/month)

3. **Digital Agencies** (Tertiary)
   - Agencies building client workflows (marketing, content, lead gen)
   - Pain: No white-label workflow platform with AI
   - Willingness to pay: High (per-client pricing)

### Competitive Landscape Deep Dive

**Direct Competitors:**

1. **Temporal.io**
   - Strengths: Battle-tested, massive scale, strong community
   - Weaknesses: Code-first (Go/Java), no AI primitives, complex setup
   - Positioning: "When you need Google-scale orchestration"
   - PyScaff advantage: Declarative YAML, AI-native, faster time-to-value

2. **Apache Airflow**
   - Strengths: Industry standard for data pipelines, huge ecosystem
   - Weaknesses: Batch-oriented, DAGs in Python (not YAML), no real-time
   - Positioning: "ETL and data engineering workflows"
   - PyScaff advantage: Real-time, human-in-the-loop, AI-native

3. **LangChain**
   - Strengths: AI-first, massive adoption, Python/JS ecosystem
   - Weaknesses: In-memory only, no durable state, no orchestration
   - Positioning: "Build AI applications fast"
   - PyScaff advantage: Durable execution, wait-states, production-ready

**Indirect Competitors:**

1. **n8n / Zapier**
   - Strengths: No-code, huge connector library, easy to use
   - Weaknesses: Limited AI support, no schema enforcement, vendor lock-in (Zapier)
   - Positioning: "No-code automation for everyone"
   - PyScaff advantage: AI-native, code-friendly, self-hostable

2. **AWS Step Functions**
   - Strengths: Serverless, AWS ecosystem integration, pay-per-use
   - Weaknesses: Vendor lock-in, expensive at scale, no AI primitives
   - Positioning: "Serverless workflow orchestration"
   - PyScaff advantage: Open-source, multi-cloud, AI-native

**Emerging Threats:**

- **LangGraph** (LangChain team): Adding state persistence to LangChain. Watch closely.
- **Microsoft Semantic Kernel**: Enterprise AI orchestration, but .NET-focused.
- **Anthropic Claude Tools**: If they build orchestration into Claude API, could disrupt.

### Whitespace Opportunity

PyScaff's unique position is the combination of **five capabilities no competitor offers together:**

1. ✅ Declarative YAML workflows (like Step Functions, n8n)
2. ✅ Durable execution with transactional state (like Temporal)
3. ✅ JSON Schema-enforced AI outputs (unique)
4. ✅ Human-in-the-loop primitives (forms, approvals)
5. ✅ Open-source with self-hosting option (like Temporal, Airflow)

This is defensible because it requires deep expertise in three domains:
- **Distributed systems** (state machines, idempotency, transactions)
- **AI/ML engineering** (prompt engineering, schema design, cost optimization)
- **Developer experience** (YAML design, API ergonomics, observability)

Most competitors are strong in 1-2 domains, weak in the third.

### Win Conditions

**Short-term (6 months):**
- 5 design partners using PyScaff in production
- 1,000+ GitHub stars, 20+ contributors
- $20k MRR from early adopters

**Medium-term (12 months):**
- 50+ paying customers
- 100k+ workflow runs per month
- Listed on G2, Capterra with 4.5+ rating
- $100k MRR

**Long-term (24 months):**
- 500+ paying customers
- Recognized category leader for "AI Workflow Orchestration"
- Partnerships with OpenAI, Anthropic
- $1M+ ARR, Series A fundraise

---

## Technical Architecture Deep Dive

### Core Concepts

#### 1. Workflows
A **Workflow** is a named, versioned DAG (directed acyclic graph) defined in YAML. It specifies:
- `start_step`: Entry point for execution
- `steps`: Array of step definitions with types, configs, and next pointers
- `definition`: Canonical YAML stored as JSONB for queryability

Example:
```yaml
name: Content Draft Flow
version: 1
start_step: collect
steps:
  - id: collect
    type: form
    name: Brief Collection
    config:
      fields:
        - key: topic
          type: string
          required: true
        - key: audience
          type: string
          required: true
    next: generate

  - id: generate
    type: ai_generate
    name: Generate Draft
    config:
      template_id: content_v1
      variables: [topic, audience]
      json_schema:
        type: object
        properties:
          draft: {type: string}
        required: [draft]
    next: approve

  - id: approve
    type: approval
    name: Approve Draft
    config:
      approvers: [editor@company.com]
    next: null
```

#### 2. Steps & Executors

PyScaff implements **5 executor types** in the MVID scope:

**a) form** - Human Data Collection
- Renders fields (string, number, boolean, date)
- Validates against regex patterns, required constraints
- Pauses workflow (status → "waiting"), stores resume token
- User submits via `POST /executions/{run_id}/resume` with inputs
- Context updated: `runtime.{field_key} = {user_input}`

**b) ai_generate** - LLM Integration
- Calls AI provider (OpenAI, Anthropic, Mock) with template
- Variables interpolated from context: `{topic}` → `context.runtime.topic`
- Response validated against JSON Schema (2020-12)
- On validation failure: retry up to 2x with error feedback in prompt
- On success: `runtime.{output_key} = {ai_output}`
- Telemetry: `ai.request`, `ai.response` events with token counts, latency

**c) conditional** - Branching Logic
- Evaluates sandboxed expression against context
- Uses `asteval` or custom AST walker (whitelist: BoolOp, BinOp, Compare)
- NO eval/exec, NO attribute access beyond context, NO function calls except `len`, `any`, `all`
- Expression examples: `runtime.score > 80`, `static.env == 'production'`, `len(runtime.tags) > 0`
- Result determines next step routing

**d) api_call** - HTTP Integration
- Makes HTTP request (GET/POST/PUT/PATCH/DELETE)
- URL, headers, body templated with Jinja2: `https://api.example.com/posts/{{runtime.post_id}}`
- Timeout configurable (default 30s)
- Response stored: `runtime.api_response = {status, body, headers}`
- Retries on 5xx with exponential backoff (3x max)

**e) approval** - Human Validation
- Notifies approvers via email (MVID: simple email template)
- Pauses workflow (status → "waiting")
- Approvers submit via `POST /executions/{run_id}/resume` with `approvals: [{step_id, approved, comment}]`
- Approved: workflow continues; Rejected: workflow fails with rejection reason

**Why these 5?**
- Covers 80% of AI workflow use cases (Pareto principle)
- Each executor is atomic and testable in isolation
- Future executors can be added without breaking changes (ADR-003)

#### 3. Runs & State Management

A **Run** is an execution instance of a workflow. Lifecycle:

```
queued → running → [waiting] → [running] → completed/failed/canceled
                      ↑           ↓
                      ←──resume──┘
```

**State transitions:**
- `queued`: Run created, not yet started (for future scheduling feature)
- `running`: Engine executing steps sequentially
- `waiting`: Paused on form/approval, awaiting external input
- `completed`: All steps executed successfully, terminal state
- `failed`: Step error unrecoverable, terminal state
- `canceled`: User-initiated cancellation

**Context model:**
```python
context = {
  "static": {       # Workflow-level constants (immutable)
    "env": "production",
    "company_name": "Acme Inc"
  },
  "profile": {      # User/entity-specific (loaded at run start)
    "user_email": "alice@example.com",
    "user_role": "editor"
  },
  "runtime": {      # Accumulated step outputs (mutable)
    "topic": "AI Orchestration",      # from form step
    "draft": "AI orchestration...",   # from ai_generate step
    "approved": true                  # from approval step
  }
}
```

Context flows through the DAG, each step:
1. Reads from context (template interpolation, conditional evaluation)
2. Executes logic (form render, AI call, API request)
3. Writes output back to context (runtime.{key} = {value})

This is **functional programming pattern**: immutable transformations with scoped mutations.

#### 4. Wait-States & Resume Mechanism

**Wait-state pattern:**
1. Step executor (form/approval) detects need for external input
2. Run status → "waiting", current_step preserved
3. Resume token generated (JWT with run_id + step_id + expiry)
4. Response returned: `{id, status: "waiting", current_step: "collect", resume_token}`
5. Client stores token, presents UI to user
6. User provides input, client calls `POST /executions/{run_id}/resume` with token + data
7. Engine validates token, resumes from current_step, transitions status → "running"

This is **durable promises** - the continuation point persists in the database, not in-memory.

**Comparison to other systems:**
- Temporal: Uses "signals" - async messages to running workflows
- AWS Step Functions: Uses "task tokens" - similar to PyScaff
- Airflow: Polls external state, not true wait-states

PyScaff's approach is simpler than Temporal, more powerful than polling.

#### 5. Idempotency & Transaction Boundaries

**Idempotency:**
- Client supplies `idempotency_key` in `POST /executions` request
- Server hashes `workflow_id + JSON.stringify(inputs)` → SHA256
- Check DB: `SELECT id FROM runs WHERE idempotency_key = ?`
- If exists: return existing run_id (HTTP 200, not 202)
- If not exists: create new run, store key

This prevents duplicate runs from:
- Network retries (client timeout, retry)
- Race conditions (multiple clients submitting same request)
- User errors (double-click submit button)

**Transaction boundaries:**
Each step execution is wrapped in SQLAlchemy transaction:
```python
async with session.begin():
    run = await session.get(Run, run_id, with_for_update=True)
    step_result = await executor.execute(step, context)
    run_step = RunStep(output=step_result, status="completed")
    session.add(run_step)
    run.context["runtime"].update(step_result)
    run.current_step = step.next
    # Commit if all succeeds, rollback if error
```

If step fails mid-execution:
- Transaction rolls back
- Run remains in last known good state
- Next execution resumes from last completed step

This is **at-least-once semantics** - steps may execute multiple times on retry, so they must be **idempotent internally**:
- AI calls: Same template_id + variables should return similar results
- API calls: Use PUT/PATCH with entity IDs, not POST (creates duplicates)
- Form/approval: User input naturally idempotent

### Observability & Telemetry

**OpenTelemetry traces:**
All operations create spans with attributes:
- `run_id`: Workflow execution identifier
- `step_id`: Step being executed
- `workflow_id`: Workflow definition identifier
- `workflow_version`: Semver version

Trace propagation enables:
- Visualizing workflow execution in Jaeger/Tempo
- Debugging: "Why did step X fail?"
- Performance: "Which step is slow?"

**Lifecycle events:**
Emitted as structured logs + OTEL events:
- `run.created`: New run started, attributes: {workflow_id, inputs, idempotency_key}
- `run.started`: Engine begins execution
- `run.waiting`: Paused on form/approval, attributes: {current_step, resume_token}
- `run.resumed`: User provided input, continuing
- `run.completed`: All steps finished successfully
- `run.failed`: Unrecoverable error, attributes: {error_step, error_message}
- `step.started`: Step execution begins, attributes: {step_id, type}
- `step.completed`: Step finished, attributes: {output, duration_ms}
- `step.failed`: Step error, attributes: {error, retry_count}

**AI-specific telemetry:**
`ai.request` and `ai.response` events include:
- `provider`: openai | anthropic | mock
- `template_id`: Identifier for prompt template
- `template_version`: Semver version of template
- `tokens_prompt`: Input tokens consumed
- `tokens_output`: Output tokens generated
- `latency_ms`: Time to first token + generation time
- `retry_count`: How many attempts before success (0 = first try)

This enables:
1. **Cost tracking**: Sum tokens by workflow_id, calculate monthly AI spend
2. **Template optimization**: Which templates have high retry_count? Need refinement.
3. **Provider comparison**: OpenAI vs Anthropic latency, cost, quality
4. **Budget alerts**: If tokens > threshold, notify owner

### Security & Compliance

**1. Authentication & Authorization**
- MVID: API key or JWT for internal use
- Production: OAuth 2.0 + RBAC (out of scope for MVID)
- Secrets: Encrypted at rest using Fernet (symmetric encryption), keys in env vars

**2. PII Redaction**
All logs/traces scrubbed before persistence using regex patterns:
```python
REDACT_PATTERNS = [
    (r"(?i)authorization:\s*bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "authorization: Bearer [REDACTED]"),
    (r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}['\"]?", r"\1: [REDACTED]"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]"),
    (r"\b(?:\+?1[-.\s]?)?$begin:math:text$?\\d{3}$end:math:text$?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
    (r"\b(?:\d[ -]*?){13,19}\b", "[REDACTED_PAN]")
]
```

This prevents GDPR/CCPA violations from logging sensitive data.

**3. Conditional Evaluator Security**
Sandboxed AST walker prevents code injection:
```python
ALLOWED_NODES = {
    "BoolOp", "UnaryOp", "BinOp", "Compare",  # Operators
    "Name", "Load", "Constant", "Subscript",  # Variables, literals
    "And", "Or", "NotEq", "Eq", "Gt", "Lt", "GtE", "LtE"  # Comparisons
}
```

Rejected nodes: `Import`, `Call` (except whitelist), `Attribute` (prevents `__import__`).

Example attack prevented:
```yaml
# Malicious workflow
conditional:
  when: __import__('os').system('rm -rf /')
```
AST parser rejects this during validation, never executes.

**4. Audit Trail**
Lifecycle events create immutable audit log:
- Who created workflow? (user_id)
- Who started run? (user_id, timestamp)
- Who approved/rejected? (approver_email, timestamp, comment)
- What was the context at each step? (context snapshots in run_steps.output)

This supports compliance (SOC2, HIPAA) and forensics.

### Technology Stack Rationale

| Component | Choice | Rationale | Alternatives Considered |
|---|---|---|---|
| Language | Python 3.12+ | AI/ML ecosystem, async/await maturity, Pydantic 2 | Node.js (poor AI libs), Go (verbose) |
| Web Framework | FastAPI 0.115+ | OpenAPI 3.1, Pydantic integration, async-first | Django (sync), Flask (no OpenAPI) |
| ORM | SQLAlchemy 2.0+ | Async support, battle-tested, migrations via Alembic | Prisma (immature Python), raw SQL (unsafe) |
| Database | PostgreSQL 16+ | JSONB for flexibility, ACID guarantees, mature | MongoDB (no transactions), MySQL (weaker JSON) |
| Validation | Pydantic 2.8+ | Rust-core performance, JSON Schema 2020-12 | Marshmallow (slower), cerberus (limited) |
| HTTP Client | httpx 0.27+ | Async, HTTP/2, connection pooling | aiohttp (less ergonomic), requests (sync) |
| Observability | OpenTelemetry 1.27+ | Vendor-neutral, distributed tracing, industry standard | Datadog SDK (vendor lock-in), custom (reinvent wheel) |
| Testing | pytest + Gherkin | BDD for acceptance, async support, fixtures | unittest (verbose), nose (deprecated) |
| Linting | ruff 0.6+ | Rust-based, 10-100x faster than flake8, auto-fix | flake8 (slow), pylint (noisy) |
| Type Checking | mypy 1.11+ | Strict mode catches bugs, IDE integration | pyright (MS-specific), no typing (unsafe) |

**Key architectural decisions:**
1. **Async/await throughout**: All I/O (DB, HTTP, AI calls) is async. Enables high concurrency without threads.
2. **JSONB for flexibility**: `workflows.definition`, `runs.context`, `run_steps.output` use JSONB. Schema can evolve without migrations.
3. **Pydantic for validation**: Type safety at runtime. FastAPI auto-generates OpenAPI from Pydantic models.
4. **OpenTelemetry for future-proofing**: Can export to Jaeger, Tempo, Honeycomb, Datadog without code changes.

---

## Small-Batch Implementation Plan

### Philosophy: Ship Working Software Every 2 Weeks

Traditional waterfall approach:
- Weeks 1-4: Design
- Weeks 5-8: Build foundation
- Weeks 9-12: Build features
- Week 13+: Integration, bugs, panic

**Problem:** Nothing works until week 12. No feedback loop. High risk.

**Small-batch approach:**
- Every 2 weeks: ship a **vertical slice** of functionality end-to-end
- Each batch delivers working software (even if limited)
- Continuous integration, continuous feedback, de-risked delivery

### 12-Week Roadmap (6 Batches × 2 Weeks)

#### Batch 1 (Weeks 1-2): Foundation
**Goal:** API skeleton + DB schema + basic workflow CRUD

**Deliverables:**
- FastAPI app with health check endpoint
- SQLAlchemy models: `Workflow`, `Run`, `RunStep`
- Alembic migrations: initial schema
- Endpoints: `POST /v1/workflows`, `GET /v1/workflows/{id}`
- Pydantic validation: reject invalid YAML
- Docker-compose: API + Postgres + OTEL collector
- CI: ruff lint + mypy type check

**Exit criteria:**
- ✅ Can create workflow from YAML via API
- ✅ Can retrieve workflow definition
- ✅ Schema validation catches missing `start_step`, invalid step types
- ✅ CI passes (lint, type)

**Risks:**
- SQLAlchemy 2.0 async patterns unfamiliar → Mitigation: Spend 2 days on spike/POC
- Docker networking issues → Mitigation: Use standard docker-compose template

#### Batch 2 (Weeks 3-4): Core Engine (Simple Executors)
**Goal:** Orchestrator that can run workflows with `form` and `conditional` steps

**Deliverables:**
- Engine module: `start_execution(workflow_id, inputs)` → returns run_id
- Form executor: validates inputs against field config, pauses run (status="waiting")
- Conditional executor: evaluates sandboxed expressions, routes to next step
- Endpoints: `POST /v1/executions`, `POST /v1/executions/{run_id}/resume`
- Context threading: {static, profile, runtime} passed through steps
- Unit tests: executor logic in isolation
- Integration tests: end-to-end workflow (form → conditional → complete)

**Exit criteria:**
- ✅ Can start workflow execution via API
- ✅ Form step pauses, conditional step routes based on context
- ✅ Resume endpoint continues execution from waiting state
- ✅ Tests cover happy path and error cases

**Risks:**
- State machine complexity (status transitions) → Mitigation: Draw state diagram, implement as enum
- Race conditions on resume → Mitigation: Use DB row locks (`SELECT FOR UPDATE`)

#### Batch 3 (Weeks 5-6): AI Integration
**Goal:** `ai_generate` executor with mock provider + schema enforcement

**Deliverables:**
- AI provider abstraction: interface for OpenAI, Anthropic, Mock
- Mock AI provider: 4 modes (success, schema_violation, timeout, transient_error)
- ai_generate executor: template interpolation, JSON Schema validation, retry logic (2x max)
- AI telemetry: `ai.request`, `ai.response` events with token counts
- Workflow example: form → ai_generate → approval (using mock AI)
- BDD feature: "AI Schema Enforcement" with retry scenarios

**Exit criteria:**
- ✅ Mock AI provider returns deterministic outputs (seeded RNG)
- ✅ Schema validation detects invalid AI responses, retries up to 2x
- ✅ After 2 retries, run fails with clear error message
- ✅ Telemetry events emitted with all required attributes

**Risks:**
- JSON Schema validation complexity → Mitigation: Use `jsonschema` library, add comprehensive tests
- Mock provider not realistic enough → Mitigation: Compare outputs to real OpenAI responses

#### Batch 4 (Weeks 7-8): Wait-States & Idempotency
**Goal:** Full lifecycle with approvals + production-ready idempotency

**Deliverables:**
- Approval executor: notifies approvers, pauses run, tracks approval/rejection
- Idempotency: hash inputs, check for duplicates, return existing run_id
- Resume token: JWT with run_id + step_id + expiry (1 week)
- Endpoints: `POST /v1/executions/{run_id}/cancel`, `GET /v1/executions/{run_id}/context`
- Transaction boundaries: SQLAlchemy sessions wrap step execution
- BDD feature: "Idempotency" with replay scenarios

**Exit criteria:**
- ✅ Approval step sends email, pauses run, resumes on approval
- ✅ Duplicate POST with same idempotency_key returns same run_id
- ✅ Transaction rollback on step failure, run resumes from last good state
- ✅ Resume token validates expiry, rejects tampered tokens

**Risks:**
- Email delivery unreliable → Mitigation: Use transactional email service (SendGrid, Postmark)
- JWT security misconfiguration → Mitigation: Use PyJWT library, set short expiry

#### Batch 5 (Weeks 9-10): Production Hardening
**Goal:** Observability, security, performance

**Deliverables:**
- OpenTelemetry: traces with run_id/step_id propagation
- Log redaction: PII/secrets scrubbed before persistence
- Performance testing: Locust load test targeting p95 < 150ms
- Security audit: pip-audit, OWASP dependency check
- API documentation: OpenAPI spec + Swagger UI
- Deployment guide: Kubernetes manifests (optional), Fly.io/Render config

**Exit criteria:**
- ✅ Traces visible in Jaeger, can debug failed runs
- ✅ Logs contain no emails, API keys, SSNs
- ✅ p95 latency < 150ms for non-LLM steps under load (100 concurrent runs)
- ✅ No critical vulnerabilities in dependencies
- ✅ API docs auto-generated from Pydantic models

**Risks:**
- Performance bottleneck in DB queries → Mitigation: Add indexes, use `EXPLAIN ANALYZE`
- OTEL overhead degrades performance → Mitigation: Sample traces (10%), async export

#### Batch 6 (Weeks 11-12): Migration Tooling (if applicable)
**Goal:** Dual-run parity harness for TS→PY migration

**Deliverables:**
- Dev endpoint: `POST /v1/dev/dual-run`
- Normalization rules: sort keys, trim whitespace, numeric tolerance 1e-6
- Comparison logic: deep diff with semantic awareness
- Seed workflows: 10 representative workflows from TS version
- Parity report: % match, diff details, pass/fail per workflow

**Exit criteria:**
- ✅ ≥95% parity for seed workflows
- ✅ Diffs are only non-semantic (whitespace, key ordering)
- ✅ Report identifies regressions clearly

**Risks:**
- Normalization too aggressive (hides real bugs) → Mitigation: Conservative defaults, opt-in relaxations
- TS engine behavior undocumented → Mitigation: Black-box testing, infer behavior from outputs

**Note:** If greenfield (no TS migration), skip Batch 6, use for polish (UX improvements, more executors, visual workflow preview).

### Development Workflow

**Daily standup (async):**
- What shipped yesterday?
- What shipping today?
- Blockers?

**Weekly demo:**
- Friday: Demo working software to stakeholders
- Get feedback, adjust next batch plan

**Sprint boundaries:**
- Monday: Plan next 2-week batch
- Review exit criteria, assign tasks
- Friday: Retrospective, what went well / not well

**Git workflow:**
- Feature branches: `feature/batch-3-ai-executor`
- PR review required (1 approver)
- Semantic commits: `feat(ai): add schema validation retry logic`
- Merge to main triggers CI/CD, deploys to staging

**Testing strategy:**
- Unit tests: 80%+ coverage for executors, models
- Integration tests: BDD Gherkin for API endpoints
- Contract tests: Spectral lint on OpenAPI spec
- Performance tests: Locust weekly on staging
- Manual testing: Product walkthrough before batch demo

### Continuous Integration (GitHub Actions)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -e ".[dev]"
      - name: Lint
        run: ruff check . && ruff format --check .
      - name: Type Check
        run: mypy app
      - name: Unit Tests
        run: pytest tests/unit -v
      - name: Integration Tests
        run: pytest tests/integration -v
      - name: Contract Lint
        run: npx spectral lint openapi.yaml
      - name: Security Audit
        run: pip-audit
```

**Quality gates:**
- All checks must pass before merge
- Test coverage < 80% fails CI
- Critical vulnerabilities fail CI
- OpenAPI spec violations fail CI

---

## Risk Analysis & Mitigation

### Technical Risks

**1. AI Output Quality (HIGH)**
**Risk:** AI generates valid JSON but semantically wrong content (hallucinations, off-topic).
**Impact:** Workflows complete successfully but produce garbage, user trust eroded.
**Mitigation:**
- Human approval steps after AI generation (workflow pattern)
- Template versioning: track which prompts work well, A/B test variants
- Feedback loop: users rate AI outputs, feed into prompt optimization
- Post-processing validators: custom logic to check semantic correctness (e.g., sentiment analysis, keyword matching)

**2. Workflow Complexity Explosion (MEDIUM)**
**Risk:** As workflows grow from 5 to 50+ steps, DAGs become unmanageable, debugging nightmare.
**Impact:** Developer productivity crash, support burden increases.
**Mitigation:**
- Visual workflow builder (Phase 2): Graphical representation of DAG, easier to understand
- Nested workflows: Sub-workflows as reusable components, encapsulation
- Workflow templates: Pre-built patterns (content generation, data enrichment), copy-paste starting points
- Observability: Traces show execution path visually, pinpoint failures quickly

**3. Performance Bottlenecks (MEDIUM)**
**Risk:** Single-process orchestrator can't handle >1000 concurrent runs, latency degrades.
**Impact:** Users experience slow workflow execution, SLA violations.
**Mitigation:**
- Horizontal scaling: Run multiple API instances behind load balancer (stateless design)
- Database optimization: Indexes on `runs.workflow_id`, `runs.status`, connection pooling
- Async I/O: All operations use async/await, non-blocking
- Future: Distributed workers (Celery, RQ) for step execution (out of MVID scope)

**4. Database Lock Contention (LOW)**
**Risk:** High concurrency causes row-level locks on `runs` table, deadlocks.
**Impact:** Transaction failures, retry storms.
**Mitigation:**
- Optimistic locking: Use `updated_at` timestamp, detect stale reads
- Short transactions: Minimize time holding locks (< 100ms)
- Read replicas: Route read-only queries (`GET /executions/{id}`) to replicas
- Partitioning: Shard runs by `workflow_id` if single table becomes bottleneck (future)

**5. JSON Schema Validation Complexity (LOW)**
**Risk:** Users write invalid JSON Schemas, validation fails mysteriously.
**Impact:** Support burden, poor DX.
**Mitigation:**
- Schema validator: `POST /v1/workflows/{id}/validate` checks schema correctness before saving
- Error messages: Detailed validation errors with line numbers, field paths
- Examples: Documentation shows common schema patterns (string, number, enum, nested objects)
- Schema builder UI: Visual tool to generate JSON Schemas (Phase 2)

### Operational Risks

**6. Team Expertise Gaps (HIGH)**
**Risk:** Team lacks experience in distributed systems, AI engineering, or OpenTelemetry.
**Impact:** Implementation delays, bugs in production, technical debt.
**Mitigation:**
- Hiring: Prioritize senior engineers with Temporal, LangChain, or FastAPI experience
- Training: Invest in courses, books, conference attendance
- Pairing: Junior/mid-level engineers pair with seniors on complex tasks
- External consultants: Bring in experts for specific areas (e.g., OTEL setup, Kubernetes)

**7. Timeline Slippage (MEDIUM)**
**Risk:** 12-week plan is optimistic, dependencies cause delays.
**Impact:** MVID launch delayed, internal stakeholders lose confidence.
**Mitigation:**
- Buffer: Plan assumes 80% utilization, 20% slack for unknowns
- Prioritization: If behind schedule, cut Batch 6 (dual-run parity), ship core features first
- Weekly checkpoints: Identify slippage early, adjust scope or extend timeline
- Parallel work: Batch independence allows multiple engineers to work concurrently

**8. Migration Complexity (MEDIUM, only if migrating from TS)**
**Risk:** TS→PY migration introduces subtle behavior changes, dual-run parity never reaches 95%.
**Impact:** Can't sunset TS engine, maintain two codebases.
**Mitigation:**
- Feature flag: Run TS and PY in parallel, route traffic based on workflow_id
- Shadow mode: PY runs in background, results discarded, validate parity without risk
- Incremental cutover: Migrate 10% of workflows, then 25%, 50%, 100% over 3 months
- Fallback: If parity impossible, document known differences, user opt-in to PY

### Business Risks

**9. Market Timing (MEDIUM)**
**Risk:** AI hype cycle peaks, funding dries up, customers cut AI budgets.
**Impact:** Sales pipeline evaporates, revenue targets missed.
**Mitigation:**
- Diversification: Target non-AI use cases (internal tools automation, API orchestration)
- Cost focus: Position as cost-savings tool (reduce OpenAI spend via template optimization)
- Freemium model: Build user base during hype, monetize in downturn
- Open-source strategy: Community adoption provides resilience vs market downturns

**10. Competitive Response (LOW)**
**Risk:** Temporal or LangChain adds schema-enforced AI primitives, erodes differentiation.
**Impact:** Harder to win deals, pricing pressure.
**Mitigation:**
- Speed: Ship fast, build defensible user base before competitors react
- Ecosystem: Connectors, templates, integrations create switching costs
- UX: Visual builder, better DX than code-first Temporal
- Community: Open-source builds goodwill, contributor base that competitors can't replicate

**11. Build vs Buy (LOW)**
**Risk:** Enterprises prefer to build in-house rather than adopt PyScaff.
**Impact:** TAM smaller than expected, sales cycle longer.
**Mitigation:**
- Open-source core: Free for self-hosting, reduces adoption friction
- Enterprise tier: Managed service with SLA, support, compliance (SOC2)
- Consulting: Offer professional services for custom integrations, training
- ROI calculator: Show cost savings vs building in-house (6 months eng time = $300k)

---

## Team & Resources

### Required Roles & Skills

**For MVID (Internal Dogfooding):**
- **1 Senior Backend Engineer**
  - Skills: Python, FastAPI, SQLAlchemy, async/await, distributed systems
  - Responsibilities: Core engine, executors, API design
  - Time: 100% (12 weeks)

- **1 AI/ML Engineer**
  - Skills: Prompt engineering, LLM APIs, JSON Schema, evaluation
  - Responsibilities: ai_generate executor, mock provider, template design
  - Time: 50% (6 weeks equivalent)

- **1 DevOps/SRE Engineer**
  - Skills: Docker, Kubernetes, GitHub Actions, OpenTelemetry
  - Responsibilities: CI/CD, observability, deployment
  - Time: 25% (3 weeks equivalent)

**Total: 2.75 FTE over 12 weeks**

**For Production SaaS (Post-MVID):**
- 2 Senior Backend Engineers (core engine, API features)
- 1 AI/ML Engineer (prompt optimization, AI provider integrations)
- 1 Frontend Engineer (visual workflow builder, React/Next.js)
- 1 DevOps/SRE Engineer (infrastructure, monitoring, security)
- 1 QA Engineer (testing, BDD, automation)
- 1 Product Manager (roadmap, user research, GTM)
- 1 Technical Writer (docs, tutorials, API reference)
- 1 Customer Success (design partners, onboarding, support)

**Total: 8 FTE for production launch**

### Knowledge Prerequisites

**Distributed Systems:**
- State machines, idempotency, event sourcing
- Transactional boundaries, at-least-once vs exactly-once semantics
- CAP theorem, eventual consistency

**LLM Best Practices:**
- Structured outputs (JSON mode, function calling)
- Prompt versioning and A/B testing
- Cost optimization (token reduction, caching)
- Evaluation metrics (semantic similarity, factuality)

**API Design:**
- RESTful conventions, resource modeling
- OpenAPI 3.1 specification
- Versioning strategies, backward compatibility
- Pagination, filtering, error responses

**Security:**
- Authentication (OAuth 2.0, JWT)
- Authorization (RBAC, ABAC)
- PII handling (GDPR, CCPA compliance)
- Injection prevention (SQL, code, template)

**Observability:**
- Distributed tracing (OpenTelemetry, Jaeger)
- Structured logging (JSON logs, log levels)
- Metrics (RED method: Rate, Errors, Duration)
- Alerting (SLIs, SLOs, error budgets)

### Hiring Strategy

**Phase 1 (MVID):** Hire contractor with Temporal or FastAPI experience for 3 months.
**Phase 2 (Beta):** Convert to full-time, hire frontend engineer for visual builder.
**Phase 3 (Launch):** Hire product manager, QA, DevOps full-time.

**Interview focus:**
- System design: "Design a workflow orchestrator" (tests distributed systems knowledge)
- Coding: "Implement idempotent API endpoint" (tests SQL, async, error handling)
- AI: "Design prompt for JSON output" (tests LLM understanding)
- Culture fit: "Tell me about a complex project you shipped" (tests ownership, communication)

---

## Appendices

### Appendix A: Database Schema Detail

```sql
-- Workflows: Immutable definitions
CREATE TABLE workflows (
    id TEXT PRIMARY KEY,                 -- UUID v4
    version INTEGER NOT NULL,            -- Semver major version
    name TEXT NOT NULL,                  -- Human-readable name
    definition JSONB NOT NULL,           -- Canonical YAML as JSON
    start_step TEXT NOT NULL,            -- Entry point step ID
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(id, version)                  -- Allow multiple versions
);
CREATE INDEX idx_workflows_name ON workflows(name);

-- Runs: Execution instances
CREATE TABLE runs (
    id TEXT PRIMARY KEY,                 -- UUID v4
    workflow_id TEXT NOT NULL,
    workflow_version INTEGER NOT NULL,
    status TEXT NOT NULL,                -- queued|running|waiting|completed|failed|canceled
    current_step TEXT,                   -- Step currently executing/paused
    context JSONB,                       -- {static, profile, runtime}
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    idempotency_key TEXT UNIQUE,         -- SHA256(workflow_id + inputs)
    FOREIGN KEY (workflow_id, workflow_version) REFERENCES workflows(id, version)
);
CREATE INDEX idx_runs_workflow ON runs(workflow_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_created ON runs(created_at DESC);

-- Run Steps: Execution history
CREATE TABLE run_steps (
    id TEXT PRIMARY KEY,                 -- UUID v4
    run_id TEXT NOT NULL,
    step_id TEXT NOT NULL,               -- Step definition ID
    type TEXT NOT NULL,                  -- form|ai_generate|conditional|api_call|approval
    status TEXT NOT NULL,                -- pending|running|completed|failed
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    output JSONB,                        -- Step result
    error TEXT,                          -- Failure message
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);
CREATE INDEX idx_run_steps_run ON run_steps(run_id);
CREATE INDEX idx_run_steps_type ON run_steps(type);
```

**Design rationale:**
- **UUID v4 for IDs**: Globally unique, no coordination needed, secure (not sequential)
- **JSONB for flexibility**: Schema evolves without migrations, queryable with GIN indexes
- **TIMESTAMPTZ**: Timezone-aware timestamps prevent bugs, required for global users
- **Foreign keys**: Referential integrity, CASCADE on run deletion cleans up steps
- **Indexes**: Query optimization for common patterns (list runs by workflow, filter by status)

### Appendix B: Example Workflow - Content Generation

```yaml
name: Blog Post Generator
version: 1
description: Generates blog post draft with AI, sends for approval
start_step: collect_brief

steps:
  - id: collect_brief
    type: form
    name: Collect Brief
    config:
      fields:
        - key: topic
          type: string
          required: true
          pattern: "^.{3,100}$"  # 3-100 chars
        - key: audience
          type: string
          required: true
          enum: [developers, marketers, executives]
        - key: tone
          type: string
          required: false
          default: professional
          enum: [casual, professional, technical]
        - key: word_count
          type: number
          required: false
          default: 1000
          min: 500
          max: 3000
    next: generate_outline

  - id: generate_outline
    type: ai_generate
    name: Generate Outline
    config:
      template_id: blog_outline_v2
      variables: [topic, audience, tone]
      json_schema:
        type: object
        properties:
          title:
            type: string
            minLength: 10
            maxLength: 100
          sections:
            type: array
            items:
              type: object
              properties:
                heading: {type: string}
                key_points:
                  type: array
                  items: {type: string}
              required: [heading, key_points]
            minItems: 3
            maxItems: 7
        required: [title, sections]
    next: review_outline

  - id: review_outline
    type: approval
    name: Review Outline
    config:
      approvers: [editor@company.com]
      timeout_hours: 24
      reminder_hours: 12
    next: generate_draft

  - id: generate_draft
    type: ai_generate
    name: Generate Full Draft
    config:
      template_id: blog_draft_v3
      variables: [topic, audience, tone, word_count, sections]
      json_schema:
        type: object
        properties:
          content: {type: string, minLength: 500}
          meta_description: {type: string, maxLength: 160}
          tags:
            type: array
            items: {type: string}
            maxItems: 5
        required: [content, meta_description, tags]
    next: publish_to_cms

  - id: publish_to_cms
    type: api_call
    name: Publish to CMS
    config:
      method: POST
      url: https://cms.company.com/api/posts
      headers:
        Authorization: "Bearer {{static.cms_api_key}}"
        Content-Type: application/json
      body:
        title: "{{runtime.title}}"
        content: "{{runtime.content}}"
        meta_description: "{{runtime.meta_description}}"
        tags: "{{runtime.tags}}"
        status: draft
      timeout_s: 10
    next: notify_success

  - id: notify_success
    type: api_call
    name: Send Slack Notification
    config:
      method: POST
      url: https://hooks.slack.com/services/{{static.slack_webhook_id}}
      headers:
        Content-Type: application/json
      body:
        text: "Blog post published: {{runtime.title}}"
        channel: "#content-team"
    next: null  # Terminal step
```

**Context evolution through workflow:**
```json
{
  "static": {
    "cms_api_key": "sk-cms-xxx",
    "slack_webhook_id": "T00/B00/xxx"
  },
  "profile": {
    "user_email": "writer@company.com",
    "user_role": "content_writer"
  },
  "runtime": {
    // After collect_brief
    "topic": "AI Workflow Orchestration",
    "audience": "developers",
    "tone": "technical",
    "word_count": 1500,

    // After generate_outline
    "title": "Building Reliable AI Workflows: A Technical Guide",
    "sections": [
      {"heading": "Introduction", "key_points": ["Problem statement", "Solution overview"]},
      {"heading": "Architecture", "key_points": ["State machine", "Schema enforcement"]}
    ],

    // After generate_draft
    "content": "AI workflows are notoriously...",
    "meta_description": "Learn how to build production-ready AI workflows with schema enforcement...",
    "tags": ["ai", "workflows", "python", "fastapi"]
  }
}
```

### Appendix C: Technology Decision Matrix

| Criterion | Weight | Temporal | LangChain | PyScaff |
|---|---|---|---|---|
| **Durable Execution** | 25% | 10 | 2 | 10 |
| **AI-Native** | 25% | 3 | 10 | 9 |
| **Developer Experience** | 20% | 6 | 8 | 9 |
| **Maturity** | 15% | 10 | 7 | 3 |
| **Community** | 10% | 8 | 10 | 2 |
| **Cost** | 5% | 5 | 10 | 8 |
| **Weighted Score** | | **7.1** | **7.5** | **7.8** |

**Explanation:**
- **Durable Execution**: Temporal wins, LangChain loses (in-memory only)
- **AI-Native**: LangChain wins, Temporal loses (no AI primitives), PyScaff close second
- **Developer Experience**: PyScaff wins (YAML declarative), LangChain second (Python DSL), Temporal last (verbose code)
- **Maturity**: Temporal wins (production-proven), PyScaff loses (new project)
- **Community**: LangChain wins (massive adoption), PyScaff loses (no community yet)
- **Cost**: LangChain wins (free, self-hosted), Temporal middle, PyScaff good (open-source core)

**Conclusion:** PyScaff scores highest due to unique combination of AI-native + durable execution, but must build maturity and community over time.

### Appendix D: Exit Criteria Checklist (MVID Dogfood-Ready)

**1. Define/validate workflow via API from YAML**
- [ ] POST /v1/workflows accepts valid YAML, returns 201
- [ ] POST /v1/workflows rejects invalid YAML with 422, detailed error
- [ ] POST /v1/workflows/{id}/validate checks schema correctness

**2. Start run → wait on form → resume → ai_generate → approval → complete**
- [ ] POST /v1/executions starts run, returns 202 with run_id
- [ ] Run status transitions: queued → running → waiting (form)
- [ ] POST /v1/executions/{id}/resume with inputs continues to ai_generate
- [ ] ai_generate calls mock AI, validates schema, writes to context
- [ ] Run transitions to waiting (approval)
- [ ] POST /v1/executions/{id}/resume with approval continues to completion
- [ ] Final status: completed

**3. Mock and real AI paths function; schema enforcement + retries observable**
- [ ] Mock AI provider returns deterministic outputs (MOCK_AI_SEED=42)
- [ ] Schema validation detects invalid outputs, retries up to 2x
- [ ] After 2 retries, run fails with ai.schema_validation_failed
- [ ] Real OpenAI provider works (tested manually, not in CI)

**4. OpenTelemetry traces and lifecycle events emitted with required attributes**
- [ ] Traces visible in Jaeger with run_id, step_id, workflow_id
- [ ] Lifecycle events: run.created, run.started, run.waiting, run.resumed, run.completed
- [ ] Step events: step.started, step.completed with duration_ms
- [ ] AI events: ai.request, ai.response with provider, template_id, tokens_prompt, tokens_output, latency_ms, retry_count

**5. Storybook components mirror BDD fixtures; MSW handlers pass acceptance flows**
- [ ] Storybook story for form renderer with field validation
- [ ] MSW handler for POST /v1/executions returns run_id
- [ ] MSW handler for POST /v1/executions/{id}/resume continues workflow
- [ ] BDD feature files execute successfully (pytest-bdd)

**6. CI: lint, type, tests, contract lint, audit → green**
- [ ] ruff check . passes (no lint errors)
- [ ] ruff format --check . passes (formatted)
- [ ] mypy app passes (type checked)
- [ ] pytest tests/ passes (all tests)
- [ ] npx spectral lint openapi.yaml passes (contract valid)
- [ ] pip-audit passes (no critical vulnerabilities)

**7. Dual-run parity ≥ 95% for seed workflows under normalization rules**
- [ ] 10 seed workflows from TS version imported
- [ ] POST /v1/dev/dual-run executes in both engines
- [ ] Outputs normalized (sort keys, trim whitespace, numeric tolerance 1e-6)
- [ ] Parity report shows ≥95% match
- [ ] Diffs are only non-semantic (whitespace, ordering)

**Sign-off:**
- [ ] Product Lead: Approves feature completeness
- [ ] Tech Lead: Approves code quality, architecture
- [ ] QA: Approves test coverage, no critical bugs
- [ ] DevOps: Approves deployment readiness, observability

---

## Conclusion

PyScaff represents a strategic bet on the convergence of three trends:
1. **AI ubiquity**: Every application will have AI workflows
2. **Reliability requirements**: Production systems need durable execution
3. **Developer productivity**: Declarative YAML beats code-first

The 12-week small-batch plan de-risks delivery by shipping working software every 2 weeks. By week 12, PyScaff will be dogfood-ready with:
- 5 executor types covering 80% of use cases
- Schema-enforced AI with automatic retries
- Human-in-the-loop primitives (forms, approvals)
- Production-grade observability (OpenTelemetry, cost tracking)
- Comprehensive testing (BDD, contract, performance, parity)

Post-MVID, the roadmap focuses on ecosystem growth:
- Visual workflow builder (no-code accessibility)
- Connectors marketplace (Zapier-like integrations)
- Template library (reusable workflow patterns)
- Enterprise features (multi-tenancy, RBAC, SOC2)

The market opportunity is significant ($2B by 2027), the technical approach is sound (leveraging SOTA patterns), and the go-to-market strategy is pragmatic (dogfood → beta → launch → ecosystem).

**Recommendation:** Proceed with implementation. PyScaff is a high-risk, high-reward bet worth taking.