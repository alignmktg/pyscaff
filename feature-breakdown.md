# PyScaff MVID Feature Breakdown
## Priority Analysis for Minimum Viable Internal Dogfooding

**Document Purpose:** Technical lead's analysis of feature priorities for MVID scope definition
**Author Role:** Technical Lead & Product Guardrails Keeper
**Last Updated:** September 30, 2025

---

## Executive Summary

### MVID Hypothesis to Prove
**Core Value Proposition:** Schema-enforced AI workflows with human-in-the-loop primitives deliver reliable, auditable AI automation.

**Must Prove:**
1. ✅ AI outputs can be constrained by JSON Schema with automatic retries
2. ✅ Workflows can pause for human input (forms) and validation (approvals)
3. ✅ Durable state persistence enables multi-day workflows
4. ✅ YAML-based workflow definitions are intuitive for developers

### Feature Count Summary
- **P0 (Must-Have):** 45 features - Core functionality to prove hypothesis
- **P1 (Strongly Recommended):** 38 features - Production best practices, valuable for dogfooding
- **P2 (Ask User):** 14 features - Context-dependent, need user input
- **P3 (Not MVID):** 22 features - Future releases, optimization, ecosystem

**Total Features Identified:** 119

### Recommended MVID Scope
**Conservative (P0 only):** 8-10 weeks, 2-3 engineers
**Recommended (P0 + selected P1):** 12-14 weeks, 2.5-3 engineers
**Aggressive (P0 + P1 + some P2):** 16-18 weeks, 3-4 engineers

---

## Priority Definitions

### P0 - Must-Have
Features absolutely required to validate the core hypothesis. Without these, MVID cannot demonstrate product value.
- **Criteria:** Directly proves schema-enforced AI workflows or human-in-the-loop
- **Risk of cutting:** MVID doesn't prove concept, dogfooding impossible
- **Example:** AI schema validation with retries

### P1 - Strongly Recommended
Important features for production-quality dogfooding or industry best practices.
- **Criteria:** Significantly improves UX, prevents tech debt, or enables debugging
- **Risk of cutting:** Painful dogfooding experience, technical debt in production
- **Example:** OpenAPI documentation, idempotency

### P2 - Ask User
Features where business context determines priority. May depend on migration needs, team constraints, or timeline.
- **Criteria:** Value depends on specific circumstances (migration, team size, compliance)
- **Risk of cutting:** Depends on context
- **Example:** Dual-run parity harness (only needed if migrating from TS)

### P3 - Definitely Not MVID
Features for future releases, optimizations, or ecosystem plays.
- **Criteria:** Nice-to-have, optimization, or requires mature product
- **Risk of cutting:** None for MVID, plan for post-launch
- **Example:** Visual workflow builder, workflow templates

---

## Feature Categories

### 1. Workflow Management

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Create workflow from YAML** | P0 | M | Medium | Core functionality. Must parse YAML, validate structure, store definition. |
| **Get workflow by ID** | P0 | XS | Low | Read operation. Needed to verify workflows were created correctly. |
| **Update workflow (new version)** | P1 | S | Medium | Versioning is best practice. Prevents breaking running workflows. Can work around by creating new workflow ID for MVID. |
| **Delete workflow** | P2 | XS | Low | Nice UX, but can leave orphaned workflows for dogfooding. Ask: cleanup important? |
| **List workflows** | P1 | S | Low | Discoverability. Without this, need to remember workflow IDs. Valuable for multi-user dogfooding. |
| **Validate workflow endpoint** | P1 | S | Medium | Catches invalid YAML before saving. Prevents runtime errors. POST /workflows/{id}/validate |
| **YAML schema versioning** | P3 | L | High | Premature. No breaking changes expected during MVID. Defer to post-launch. |
| **Upgrade CLI (YAML migration)** | P3 | M | Medium | Depends on versioning. Not needed until schema changes. |

**Category Total:** 8 features (3 P0, 3 P1, 1 P2, 1 P3)

---

### 2. Step Executors

#### Form Executor
| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Basic form rendering** | P0 | M | Medium | Core wait-state primitive. Pauses workflow, collects input. |
| **Field validation (required, type)** | P0 | S | Low | Prevents invalid inputs. Pydantic handles most of this. |
| **Advanced validation (regex, enum, min/max)** | P1 | S | Low | Better UX, prevents errors downstream. Example: email regex, age 18-100. |
| **Multi-file uploads** | P3 | L | High | Complex (S3 integration, virus scanning). Not needed for text-based workflows. |

#### AI Generate Executor
| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Basic AI provider abstraction** | P0 | M | Medium | Interface for Mock, OpenAI, Anthropic. Decouples executor from provider. |
| **JSON Schema validation** | P0 | L | High | **THE differentiator.** Must validate AI output against schema. |
| **Retry on schema failure (max 2)** | P0 | M | High | **THE differentiator.** Automatic retry with error feedback. |
| **Template interpolation (variables)** | P0 | S | Medium | Inject context into prompts: "Write about {{topic}} for {{audience}}". Uses Jinja2. |
| **Template ID system** | P1 | S | Low | Organize prompts by ID. Better than inlining prompts in YAML. Enables template versioning later. |
| **Template versioning** | P3 | M | Medium | Track prompt changes. A/B testing. Premature for MVID. |

#### Conditional Executor
| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Sandboxed expression evaluation** | P0 | M | High | Security-critical. Prevents code injection. Whitelist AST nodes (BoolOp, Compare, etc.). |
| **Basic conditionals (>, <, ==, and, or)** | P0 | S | Medium | Routing logic. Example: `runtime.score > 80` → approve, else → reject. |
| **Complex expressions (len, any, all)** | P1 | S | Medium | More powerful routing. Example: `len(runtime.tags) > 0 and 'urgent' in runtime.tags`. |

#### API Call Executor
| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **HTTP methods (GET/POST/PUT/PATCH/DELETE)** | P1 | M | Medium | Integration capability. Not unique to PyScaff, but valuable for real workflows. |
| **URL/header/body templating** | P1 | S | Medium | Inject context: `https://api.example.com/posts/{{runtime.post_id}}`. |
| **Timeout handling** | P1 | XS | Low | Prevents hanging. Default 30s. |
| **Retry on 5xx errors** | P2 | S | Medium | Robustness. Exponential backoff (3x max). Ask: critical for MVID? |

#### Approval Executor
| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Basic approval pause/resume** | P0 | M | Medium | Second wait-state primitive. Proves multi-stage human validation. |
| **Email notification** | P1 | S | Low | UX improvement. Simple SMTP or transactional email (SendGrid). Without this, approvers don't know to act. |
| **Approval tracking (approved/rejected/comment)** | P0 | S | Low | Audit trail. Need to know who approved and why. |
| **Timeout & reminders** | P2 | M | Medium | Nice UX. Example: remind after 12h, reject after 24h. Ask: needed for MVID? |

**Category Total:** 18 features (10 P0, 6 P1, 2 P2, 0 P3)

**Key Insight:** Form, ai_generate, approval are P0 (proves core hypothesis). Conditional and api_call are P1 (valuable but not critical for first demo workflow).

---

### 3. Execution Lifecycle

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Start execution** | P0 | M | Medium | POST /v1/executions. Core functionality. Accepts workflow_id + inputs. |
| **Get execution status** | P0 | XS | Low | GET /v1/executions/{run_id}. Must know if workflow is running, waiting, completed, failed. |
| **Resume execution** | P0 | M | High | POST /v1/executions/{run_id}/resume. Critical for wait-states. Validates token, continues from current_step. |
| **Cancel execution** | P2 | S | Medium | POST /v1/executions/{run_id}/cancel. Nice to have for cleanup. Ask: needed for dogfooding? Can let workflows complete or fail naturally. |
| **Get execution history** | P1 | M | Medium | GET /v1/executions/{run_id}/history. Returns all completed steps. Critical for debugging "why did this fail?". |
| **Get execution context** | P1 | S | Low | GET /v1/executions/{run_id}/context. Shows {static, profile, runtime} snapshot. Debugging tool. |
| **List executions** | P2 | M | Low | GET /v1/executions?workflow_id=X. Discoverability. Can track run_ids manually for MVID. Ask: multi-user dogfooding? |

**Category Total:** 7 features (3 P0, 2 P1, 2 P2)

---

### 4. Wait-States & Resume Mechanism

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Basic wait-state (pause workflow)** | P0 | M | High | State machine transition: running → waiting. Stores current_step in DB. |
| **Resume token generation** | P0 | S | Medium | JWT with {run_id, step_id, exp}. Returned in wait-state response. |
| **Resume token validation** | P0 | S | Medium | Verify signature, check expiry, prevent replay attacks. |
| **Resume token expiry** | P1 | XS | Low | Default 7 days. Security hardening. Can set long expiry (30 days) for MVID if needed. |
| **Multiple wait-states in workflow** | P0 | M | Medium | Example: form → ai_generate → approval = 2 wait-states. Engine must handle sequential waits. |

**Category Total:** 5 features (4 P0, 1 P1)

**Key Insight:** Wait-states are the core UX innovation. Must work reliably.

---

### 5. Context Management

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Static context** | P1 | S | Low | Workflow-level constants. Example: {env: "production", company: "Acme"}. Nice to have, but can hardcode for MVID. |
| **Profile context** | P2 | M | Medium | User-specific data. Example: {user_email, user_role}. Ask: single-user dogfooding or multi-user? |
| **Runtime context** | P0 | M | Medium | Step outputs accumulate here. **This is how data flows through workflow.** Critical. |
| **Context interpolation (Jinja2)** | P0 | S | Medium | Template variables: `{{runtime.topic}}`. Used in AI prompts, API URLs, conditionals. |
| **Context validation** | P1 | S | Low | Type checking. Prevents errors like accessing undefined keys. Pydantic models help. |

**Category Total:** 5 features (2 P0, 2 P1, 1 P2)

---

### 6. AI Integration

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Mock AI provider** | P0 | M | Medium | Deterministic outputs for testing. No API costs. Returns valid JSON matching schema. |
| **OpenAI integration** | P0 | M | Medium | Real AI provider. Proves concept with actual LLM. Use GPT-4 or GPT-3.5. |
| **Anthropic integration** | P2 | S | Low | Second provider. Nice for comparison, but one provider enough for MVID. Ask: needed? |
| **JSON Schema validation (jsonschema lib)** | P0 | S | Medium | Core feature. Validate AI output against schema. Detailed error messages. |
| **Retry with error feedback** | P0 | M | High | On validation failure, retry with error in prompt: "Previous output failed: missing 'title' field". |
| **Max retry count (2)** | P0 | XS | Low | Prevent infinite loops. After 2 retries, fail run with clear error. |
| **AI telemetry (tokens, latency)** | P1 | M | Medium | Events: ai.request, ai.response with {provider, template_id, tokens_prompt, tokens_output, latency_ms, retry_count}. Valuable for cost tracking. |
| **Mock provider modes** | P1 | M | Medium | success, schema_violation, timeout, transient_error. Test error paths. Nice for comprehensive testing. |
| **Deterministic seeding (mock)** | P1 | S | Low | MOCK_AI_SEED=42 for reproducible tests. Valuable for CI stability. |
| **AI provider timeout** | P1 | XS | Low | Prevent hanging on slow API calls. Default 60s for AI (slower than HTTP 30s). |
| **Cost tracking aggregation** | P3 | L | Medium | Dashboard showing AI spend by workflow. Post-launch analytics. |

**Category Total:** 11 features (6 P0, 4 P1, 1 P2, 0 P3)

**Key Insight:** AI integration is the highest complexity area. Schema validation + retries is novel, requires careful design.

---

### 7. Idempotency

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Idempotency key on start** | P1 | S | Medium | Client supplies key in POST /v1/executions. Best practice for production APIs. Prevents duplicate workflows from network retries. |
| **Hash-based deduplication** | P1 | S | Low | SHA256(workflow_id + JSON(inputs)) → check DB for existing run. |
| **Return existing run on duplicate** | P1 | XS | Low | If key exists, return run_id with 200 (not 202). Idempotent contract. |

**Category Total:** 3 features (0 P0, 3 P1)

**Key Insight:** PRD lists idempotency as exit criteria, so P1 at minimum. Critical for production but can dogfood without initially.

---

### 8. Transactional Boundaries

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **SQLAlchemy transaction per step** | P0 | M | High | Wrap step execution in `async with session.begin()`. Rollback on failure. Data integrity critical. |
| **Rollback on step failure** | P0 | S | Medium | If step errors, rollback DB changes. Run reverts to last known good state. |
| **Row-level locking (FOR UPDATE)** | P1 | S | Medium | Prevent race conditions on resume. SELECT FOR UPDATE when reading run. Best practice. |
| **At-least-once semantics** | P0 | - | - | Inherent to design. Steps may execute multiple times on retry. Document in ADR. |

**Category Total:** 4 features (3 P0, 1 P1)

**Key Insight:** Transactional integrity is not negotiable. One of the hardest technical challenges.

---

### 9. Observability

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Structured logging (JSON)** | P1 | S | Low | Better than print statements. Queryable logs. Example: `{"level": "info", "run_id": "xyz", "msg": "Step started"}`. |
| **OpenTelemetry SDK setup** | P1 | M | Medium | Install OTEL instrumentation. Export traces. Valuable for debugging, but can start with logs. |
| **Run ID / Step ID propagation** | P1 | S | Medium | Attach run_id, step_id to all spans and logs. Enables correlation. |
| **Jaeger integration** | P2 | S | Low | Trace visualization. Nice UX, but can export to console for MVID. Ask: critical? |
| **Lifecycle events** | P1 | M | Medium | Emit events: run.created, run.started, run.waiting, run.resumed, run.completed, run.failed. Audit trail. |
| **Step events** | P1 | S | Low | step.started, step.completed, step.failed. Granular execution tracking. |
| **AI events** | P1 | M | Medium | ai.request, ai.response with telemetry. Cost tracking foundation. |
| **Performance metrics (RED)** | P3 | M | Medium | Rate, Errors, Duration. Optimization, not needed for MVID. |

**Category Total:** 8 features (0 P0, 6 P1, 1 P2, 1 P3)

**Key Insight:** Observability is valuable but can start minimal (structured logs). Add OTEL in Batch 5.

---

### 10. Security

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **API key authentication** | P1 | S | Low | Basic security. Header: `Authorization: Bearer {key}`. Good enough for internal dogfooding. |
| **JWT authentication** | P2 | M | Medium | More complex. API key simpler for MVID. Ask: multi-user auth needed? |
| **PII redaction in logs** | P2 | M | Medium | Regex patterns for emails, SSNs, credit cards. Compliance. Ask: critical for internal dogfooding? |
| **Sandboxed conditional eval** | P0 | M | High | Security-critical. Prevents code injection in conditional expressions. Whitelist AST nodes. |
| **Secrets encryption at rest** | P3 | L | High | Encrypt AI keys, API tokens in DB. Can use env vars for MVID. Production feature. |
| **OAuth 2.0 / RBAC** | P3 | XL | High | Explicitly out of scope per PRD. Enterprise feature. |

**Category Total:** 6 features (1 P0, 1 P1, 2 P2, 2 P3)

**Key Insight:** Sandboxed conditionals are P0 (security critical). Other security can be basic for MVID.

---

### 11. Database & Persistence

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Workflows table** | P0 | S | Low | Store workflow definitions. Schema: id, version, name, definition (JSONB), start_step. |
| **Runs table** | P0 | S | Low | Track executions. Schema: id, workflow_id, status, current_step, context (JSONB), timestamps, idempotency_key. |
| **Run_steps table** | P0 | S | Low | Execution history. Schema: id, run_id, step_id, type, status, output (JSONB), error, timestamps. |
| **Alembic migrations** | P1 | M | Low | Version control schema. First migration creates tables. Best practice, prevents manual SQL. |
| **PostgreSQL support** | P0 | S | Low | Production database. JSONB support, ACID transactions. |
| **SQLite support** | P1 | S | Low | Easier local dev (no Docker). Can use Postgres in docker-compose, so optional. |
| **JSONB for flexibility** | P0 | - | - | Store definition, context, output as JSONB. Schema evolves without migrations. |
| **Indexes on common queries** | P1 | S | Low | workflow_id, status, created_at. Performance optimization. Quick wins. |
| **Foreign key constraints** | P1 | XS | Low | Referential integrity. CASCADE on delete. Prevents orphaned data. |

**Category Total:** 9 features (5 P0, 4 P1)

---

### 12. Testing

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Unit tests (executors, models)** | P0 | L | Medium | Test each executor in isolation. Mock dependencies. 80%+ coverage target. |
| **Integration tests (API endpoints)** | P0 | L | Medium | End-to-end API tests. Spin up test DB. Validate request/response. |
| **BDD/Gherkin features** | P1 | M | Medium | Living documentation. Example: "Given run is waiting on form, When I resume...". Valuable but can test without. |
| **Contract testing (Spectral)** | P1 | S | Low | Lint OpenAPI spec. Catches breaking changes. CI gate. |
| **Security audit (pip-audit)** | P1 | XS | Low | Check for vulnerable dependencies. Run in CI. Easy win. |
| **Storybook components** | P3 | L | High | Frontend testing. No UI in MVID, so N/A. |
| **MSW handlers** | P3 | M | Medium | Mock Service Worker. Goes with Storybook. N/A for MVID. |
| **Performance testing (Locust)** | P2 | M | Medium | Load testing. p95 < 150ms target. Ask: critical for MVID or optimize later? |

**Category Total:** 8 features (2 P0, 3 P1, 1 P2, 2 P3)

**Key Insight:** Unit + integration tests are non-negotiable (P0). BDD is valuable (P1). Storybook is N/A (P3).

---

### 13. DevOps & Infrastructure

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Docker-compose for local dev** | P0 | S | Low | API + Postgres + OTEL collector. Makes setup trivial. |
| **Dockerfile for API** | P0 | S | Low | Containerize FastAPI app. Standard pattern. |
| **GitHub Actions CI** | P1 | M | Low | Automates lint, type, test, audit. Quality gate. Copy-paste from template. |
| **.env for configuration** | P0 | XS | Low | DATABASE_URL, AI_PROVIDER, OPENAI_API_KEY, etc. Standard practice. |
| **Health check endpoint** | P1 | XS | Low | GET /health returns 200. Monitoring, load balancer readiness checks. |
| **Kubernetes manifests** | P3 | L | High | Overkill for MVID. Docker-compose enough. Production deployment feature. |
| **Graceful shutdown** | P2 | S | Medium | Handle SIGTERM, finish in-flight requests. Best practice. Ask: needed for dogfooding? |

**Category Total:** 7 features (3 P0, 2 P1, 1 P2, 1 P3)

---

### 14. API Documentation

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **OpenAPI 3.1 spec** | P1 | S | Low | Auto-generated from Pydantic models. FastAPI does this. Should have for API contract. |
| **Swagger UI** | P1 | XS | Low | Interactive docs at /docs. FastAPI includes this. Zero effort. |
| **README with setup** | P0 | S | Low | How to run locally. Docker commands, env vars. Others need this to dogfood. |
| **Endpoint documentation** | P1 | - | - | Covered by OpenAPI. Docstrings in code → OpenAPI descriptions. |
| **Postman collection** | P3 | S | Low | Nice to have, but OpenAPI + Swagger UI is enough. |

**Category Total:** 5 features (1 P0, 3 P1, 0 P2, 1 P3)

---

### 15. Migration Tooling (TS → PY)

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **/v1/dev/dual-run endpoint** | P2 | M | High | Only needed if migrating from TS. Executes workflow in both engines, compares outputs. Ask: is this greenfield or migration? |
| **Normalization rules** | P2 | M | Medium | Sort keys, trim whitespace, numeric tolerance 1e-6. Semantic comparison. |
| **Diff reporting** | P2 | S | Low | Show differences between TS and PY outputs. Highlights regressions. |
| **95% parity target** | P2 | - | - | Exit criteria if migrating. Not applicable for greenfield. |

**Category Total:** 4 features (0 P0, 0 P1, 4 P2, 0 P3)

**Key Decision:** If greenfield, all P2 → P3. If migration, all P2 → P1.

---

### 16. Additional Features

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Seed workflows script** | P1 | S | Low | scripts/seed_workflows.py. Example workflows for testing, demos. Valuable for dogfooding. |
| **Workflow templates/library** | P3 | XL | High | Marketplace of pre-built workflows. Ecosystem feature, post-launch. |
| **Visual workflow builder** | P3 | XL | High | Explicitly in backlog per PRD. Phase 2 feature. |
| **Parallel step execution** | P3 | L | High | Execute multiple steps concurrently. Adds complexity. DAG is sequential for MVID. |
| **Step retries (generic)** | P2 | M | Medium | Beyond AI schema retries. Retry any step on transient failure. Ask: needed for robustness? |
| **Nested workflows** | P3 | L | High | Sub-workflows as reusable components. Advanced feature. |
| **Workflow scheduling (cron)** | P3 | M | Medium | Trigger workflows on schedule. Out of scope per PRD. |
| **Webhook triggers** | P3 | M | Medium | Start workflow from external event. Out of scope per PRD. |
| **A/B testing workflows** | P3 | L | High | Route traffic between variants. Analytics feature, post-launch. |

**Category Total:** 9 features (0 P0, 1 P1, 1 P2, 7 P3)

---

### 17. Error Handling

| Feature | Priority | LOE | Difficulty | Rationale |
|---------|----------|-----|------------|-----------|
| **Validation errors (detailed)** | P0 | S | Low | Pydantic gives detailed errors. Example: "start_step: field required". UX critical. |
| **Step failure capture** | P0 | S | Low | Store error message in run_steps.error. Debugging essential. |
| **Run failure status** | P0 | XS | Low | Transition to "failed" on unrecoverable error. Client needs to know. |
| **Error propagation to client** | P0 | S | Low | Return error in API response. Status 4xx/5xx with message. |
| **Retry logic (transient errors)** | P1 | M | Medium | Exponential backoff for API calls, DB connections. Robustness. |
| **Circuit breakers** | P3 | M | High | Advanced resilience. Overkill for MVID. |

**Category Total:** 6 features (4 P0, 1 P1, 0 P2, 1 P3)

---

## Decision Framework

### How to Use Priority Levels

**When to move P1 → P0:**
- Feature is blocking dogfooding (can't test workflows without it)
- Technical dependency for P0 feature (e.g., API key auth if multi-user dogfooding)
- User explicitly requires for MVID timeline

**When to move P2 → P3:**
- User confirms not applicable (e.g., dual-run if greenfield)
- Timeline requires cuts, and feature has workaround

**When to move P2 → P1 or P0:**
- User confirms context makes it critical (e.g., email notifications if approvers are remote)

### Trade-Off Guidelines

**Speed vs Quality:**
- P0 must be high quality (core hypothesis)
- P1 can be "good enough" (MVP quality)
- P2/P3 can be rough (spike quality)

**Complexity vs Value:**
- High complexity P1 → consider deferring to P2 if timeline tight
- Low complexity P2 → consider promoting to P1 if valuable

---

## Questions for User

### Migration Context
**Q1:** Is this a greenfield implementation or migration from existing TypeScript system?
- **If greenfield:** Dual-run features (P2) → P3
- **If migration:** Dual-run features (P2) → P1

### Dogfooding Scope
**Q2:** How many internal users will dogfood, and how will they collaborate?
- **If single user:** Profile context (P2) → P3, JWT auth (P2) → P3
- **If multi-user:** List workflows/executions (P2) → P1, API key auth (P1) → P0

**Q3:** What's the target timeline for MVID launch?
- **If 8-10 weeks:** Stick to P0 only
- **If 12-14 weeks:** Add selected P1 (recommended)
- **If 16+ weeks:** Can consider P2 features

### Risk Tolerance
**Q4:** How important is production-readiness vs proving concept quickly?
- **If concept proof:** Observability (P1) → P2, Idempotency (P1) → P2
- **If production-ready:** Keep P1 as-is, consider some P2 → P1

**Q5:** Are approvers co-located or remote?
- **If co-located:** Email notifications (P1) → P2 (can walk over)
- **If remote:** Email notifications (P1) → P0 (critical UX)

---

## Recommended MVID Scope

### Conservative (P0 Only)
**Features:** 45
**Timeline:** 8-10 weeks
**Team:** 2-3 engineers
**Risk:** Minimal scope, barebones UX, technical debt

**Includes:**
- Workflow CRUD (create, get)
- 3 executors: form, ai_generate, approval
- Execution lifecycle: start, get status, resume
- Wait-states with resume tokens
- Runtime context + interpolation
- AI schema validation + retries (Mock + OpenAI)
- Transactional step boundaries
- Basic database (3 tables, Postgres)
- Unit + integration tests
- Docker-compose
- README

**Excludes:**
- Conditional, api_call executors
- Idempotency
- Observability (beyond basic logs)
- API documentation (beyond README)
- Any P1/P2/P3

**Dogfooding capability:** Can run simple workflows (form → AI → approval). Painful debugging (no traces). Manual workflow creation (no validation endpoint).

---

### Recommended (P0 + Selected P1)
**Features:** 45 P0 + ~20 P1 = 65
**Timeline:** 12-14 weeks
**Team:** 2.5-3 engineers
**Risk:** Balanced scope, good UX, manageable debt

**Adds to Conservative:**
- Conditional executor (branching logic)
- API call executor (integrations)
- Idempotency (production best practice)
- Observability: structured logs, lifecycle events, OTEL setup
- API documentation: OpenAPI spec, Swagger UI
- Advanced form validation (regex, enums)
- AI telemetry (cost tracking foundation)
- Alembic migrations (schema versioning)
- Indexes, foreign keys (performance, integrity)
- GitHub Actions CI (quality gate)
- Security: API key auth, sandboxed conditionals
- Seed workflows script

**Dogfooding capability:** Can run complex workflows (branching, API calls). Good debugging (events, traces). Self-service workflow creation (validation endpoint). Production-quality (idempotency, migrations).

**This is the recommended scope for MVID.**

---

### Aggressive (P0 + P1 + Selected P2)
**Features:** 45 P0 + 38 P1 + ~8 P2 = 91
**Timeline:** 16-18 weeks
**Team:** 3-4 engineers
**Risk:** Feature creep, delays, over-engineering

**Adds to Recommended:**
- Profile context (multi-user data)
- JWT authentication (advanced auth)
- PII redaction (compliance)
- Dual-run parity harness (if migrating)
- Performance testing (Locust)
- List workflows/executions (UX)
- Cancel execution (UX)
- Step retries (robustness)

**Dogfooding capability:** Feature-complete, production-ready, compliant.

**Caution:** Risk of never shipping. Only pursue if timeline allows and team has spare capacity.

---

## Critical Path Dependencies

### Must Complete in Order

**Week 1-2: Foundation**
1. Database schema (workflows, runs, run_steps) → P0
2. FastAPI app skeleton → P0
3. Workflow CRUD → P0

**Week 3-4: Simple Executors**
4. Form executor → P0 (depends on: wait-states)
5. Wait-state mechanism → P0 (depends on: resume tokens)
6. Resume tokens → P0 (depends on: JWT generation)

**Week 5-7: AI Integration**
7. AI provider abstraction → P0 (depends on: none)
8. Mock AI provider → P0 (depends on: abstraction)
9. OpenAI integration → P0 (depends on: abstraction)
10. JSON Schema validation → P0 (depends on: none)
11. Retry logic → P0 (depends on: validation)

**Week 8-9: Approval & Conditionals**
12. Approval executor → P0 (depends on: wait-states, email)
13. Conditional executor → P0 (depends on: sandboxed eval)
14. Sandboxed evaluation → P0 (depends on: none, security-critical)

**Week 10-12: Production Hardening (P1)**
15. Idempotency → P1 (depends on: none)
16. Observability (OTEL) → P1 (depends on: none)
17. CI/CD → P1 (depends on: tests)
18. API documentation → P1 (depends on: OpenAPI)

**Parallelizable:**
- Testing can happen concurrently with feature dev
- Documentation can happen concurrently with feature dev
- DevOps (Docker, CI) can happen early or late

---

## Summary & Recommendation

**Total Features Analyzed:** 119
- **P0 (Must-Have):** 45 features
- **P1 (Strongly Recommended):** 38 features
- **P2 (Ask User):** 14 features
- **P3 (Not MVID):** 22 features

**Recommended Action:**
1. **Answer 5 decision questions** to clarify P2 features
2. **Commit to Recommended scope** (P0 + selected P1 = 65 features)
3. **Target 12-14 week timeline** with 2.5-3 engineers
4. **Use small-batch approach** (2-week sprints, ship working software)

**This produces a production-quality MVID that:**
- ✅ Proves core hypothesis (schema-enforced AI workflows)
- ✅ Delivers good dogfooding UX (debugging, validation)
- ✅ Minimizes technical debt (migrations, idempotency, tests)
- ✅ Ships in reasonable timeline (3 months)

**Next Steps:**
1. User answers 5 questions
2. Finalize feature list
3. Write MVID specification document
4. Begin Batch 1 (Foundation)

---

**Document Status:** Ready for user review
**Next Document:** `mvid-spec.md` (detailed specification based on finalized scope)