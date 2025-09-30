# PyScaff MVID Feature Breakdown
## For Product People (Plain English Edition)

**What This Document Does:** Breaks down every feature into "must-have," "should-have," "maybe," and "not now" for our first internal release.

**Who This Is For:** Product managers, business stakeholders, anyone who doesn't write code.

**Last Updated:** September 30, 2025

---

## The Big Picture: What Are We Building?

**Imagine this workflow:**
1. Sarah fills out a form: "Write a blog post about AI for developers"
2. AI generates a draft automatically
3. Sarah's manager gets an email to approve or reject it
4. If approved, the post gets published to the CMS

**That's PyScaff.** It's a system that runs multi-step workflows where:
- ✅ AI does creative work (write content, analyze data, generate code)
- ✅ Humans provide input and approval (forms, reviews)
- ✅ Everything is reliable (workflows don't break, data doesn't get lost)
- ✅ AI outputs are validated (no garbage responses)

**Our Unique Value:** We're the only platform that automatically fixes bad AI outputs (if AI forgets a field, we retry automatically) AND lets workflows pause for human approval.

---

## What Does "MVID" Mean?

**M**inimum **V**iable **I**nternal **D**ogfooding

Translation: The smallest version we can build that our own team can actually use daily to prove this works.

**Success = Our team runs 5-10 workflows internally, finds it useful, and we learn what to build next.**

---

## How to Read This Document

### Priority Levels (The Traffic Light System)

🔴 **P0 - Must Have**
- Without this, we can't dogfood at all
- Example: Being able to create and run workflows
- Risk of cutting: Can't prove the concept works

🟡 **P1 - Should Have**
- Makes dogfooding pleasant instead of painful
- Example: Being able to debug why a workflow failed
- Risk of cutting: Frustrating user experience, technical debt

🟠 **P2 - Maybe?**
- Depends on our specific situation
- Example: Migration tools (only if we're migrating from old system)
- Risk of cutting: Depends on context

⚪ **P3 - Not Now**
- Future releases, optimizations, nice-to-haves
- Example: Visual workflow builder, marketplace
- Risk of cutting: None for MVID

### Effort & Complexity

**Effort (How long it takes):**
- XS = Few hours
- S = 1-2 days
- M = 3-5 days
- L = 1-2 weeks
- XL = Months

**Difficulty (How hard it is):**
- Low = Standard stuff, lots of examples
- Medium = Some tricky parts, need to think
- High = Novel, complex, requires expertise

---

## Feature Walkthrough (By Category)

---

## 1. Creating & Managing Workflows

**What is a workflow?** A YAML file that defines the steps. Like a recipe.

Example:
```yaml
name: Blog Post Generator
steps:
  - Get topic from user (form)
  - Have AI write draft (ai_generate)
  - Manager approves (approval)
```

### Features

#### 🔴 P0: Create workflow from YAML file
**What it does:** Upload a YAML file, system saves it.
**User story:** "As a workflow creator, I want to define my workflow in a text file so I can version control it in Git."
**What this looks like:**
```bash
curl -X POST /api/workflows \
  -H "Content-Type: application/json" \
  -d '{"name": "Blog Generator", "yaml": "..."}'

Response: {"id": "wf_123", "status": "created"}
```
**Why P0:** Can't do anything without creating workflows.
**Effort:** Medium (3-5 days) | **Difficulty:** Medium
**If we skip this:** Can't dogfood at all.

---

#### 🔴 P0: Get workflow details
**What it does:** Look up a workflow you created.
**User story:** "As a user, I want to see what my workflow looks like after I created it."
**What this looks like:**
```bash
GET /api/workflows/wf_123

Response: {
  "id": "wf_123",
  "name": "Blog Generator",
  "steps": [...]
}
```
**Why P0:** Need to verify workflows were created correctly.
**Effort:** Extra Small (few hours) | **Difficulty:** Low
**If we skip this:** Blind - can't tell if creation worked.

---

#### 🟡 P1: Update workflow (creates new version)
**What it does:** Edit an existing workflow without breaking currently running ones.
**User story:** "As a workflow creator, I want to fix a typo in my workflow without breaking the 5 workflows currently running."
**Why P1:** Best practice for production systems. Without it, every edit breaks running workflows.
**Workaround for MVID:** Just create a new workflow with a different ID. Manual but works.
**Effort:** Small (1-2 days) | **Difficulty:** Medium
**If we skip this:** Annoying but manageable for dogfooding.

---

#### 🟠 P2: Delete workflow
**What it does:** Remove a workflow you don't want anymore.
**User story:** "As a workflow creator, I want to clean up test workflows."
**Why P2:** Nice UX, but we can leave old workflows around during dogfooding.
**Question:** Is cleanup important to you, or can we leave orphaned workflows?
**Effort:** Extra Small (few hours) | **Difficulty:** Low
**If we skip this:** Database gets messy, but doesn't break anything.

---

#### 🟡 P1: List all workflows
**What it does:** See all workflows you've created.
**What this looks like:**
```bash
GET /api/workflows

Response: {
  "workflows": [
    {"id": "wf_123", "name": "Blog Generator"},
    {"id": "wf_456", "name": "Customer Onboarding"}
  ]
}
```
**Why P1:** Discoverability. Without this, you have to remember workflow IDs.
**Workaround for MVID:** Keep a spreadsheet of workflow IDs.
**Effort:** Small (1-2 days) | **Difficulty:** Low
**If we skip this:** Painful for multi-user dogfooding.

---

#### 🟡 P1: Validate workflow before saving
**What it does:** Check if YAML is valid before creating workflow.
**What this looks like:**
```bash
POST /api/workflows/validate
{"yaml": "..."}

Response: {
  "valid": false,
  "errors": ["Missing start_step", "Step 'approval' has invalid config"]
}
```
**User story:** "As a workflow creator, I want to know if my YAML is wrong BEFORE I try to run it."
**Why P1:** Prevents runtime errors. Without it, you only discover problems when workflow fails.
**Effort:** Small (1-2 days) | **Difficulty:** Medium
**If we skip this:** Lots of failed workflows from typos.

---

#### ⚪ P3: YAML versioning & auto-migration
**What it does:** When we change YAML format, automatically upgrade old workflows.
**Why P3:** Premature. We won't change YAML format during MVID.
**When we'll need this:** Post-launch, when we add new features that change schema.

---

**Category Summary:**
- **Must Have (P0):** Create workflow, Get workflow (2 features)
- **Should Have (P1):** Update, List, Validate (3 features)
- **Maybe (P2):** Delete (1 feature)
- **Not Now (P3):** Versioning (1 feature)

---

## 2. Running Workflows (The Core Stuff)

### What does "running a workflow" mean?

Think of it like pressing "Start" on a dishwasher:
1. You start the workflow (press start)
2. It runs each step in order (wash, rinse, dry)
3. It might pause and ask for input ("Add detergent")
4. Eventually it finishes (clean dishes) or fails (error code)

### Features

#### 🔴 P0: Start a workflow
**What it does:** Kick off a workflow execution.
**What this looks like:**
```bash
POST /api/executions
{
  "workflow_id": "wf_123",
  "inputs": {
    "topic": "AI Workflows",
    "audience": "developers"
  }
}

Response: {
  "run_id": "run_789",
  "status": "running"
}
```
**User story:** "As a user, I want to start my workflow with initial inputs."
**Why P0:** This is literally the product. Can't dogfood without it.
**Effort:** Medium (3-5 days) | **Difficulty:** Medium
**If we skip this:** No product.

---

#### 🔴 P0: Check workflow status
**What it does:** See if workflow is still running, paused, done, or failed.
**What this looks like:**
```bash
GET /api/executions/run_789

Response: {
  "run_id": "run_789",
  "status": "waiting",  // Paused, waiting for human input
  "current_step": "collect_topic"
}
```
**User story:** "As a user, I want to know what's happening with my workflow."
**Why P0:** Without this, workflows are a black box.
**Effort:** Extra Small (few hours) | **Difficulty:** Low
**If we skip this:** Can't tell if workflows are working.

---

#### 🔴 P0: Resume a paused workflow
**What it does:** Provide input to continue a paused workflow.
**What this looks like:**

**Step 1:** Workflow pauses on form step
```bash
GET /api/executions/run_789

Response: {
  "status": "waiting",
  "current_step": "collect_topic",
  "resume_token": "eyJhbGc..." // Security token
}
```

**Step 2:** User submits form
```bash
POST /api/executions/run_789/resume
{
  "resume_token": "eyJhbGc...",
  "inputs": {
    "topic": "Cloud Computing",
    "audience": "CTOs"
  }
}

Response: {
  "status": "running"  // Continues to next step
}
```

**User story:** "As a user, I want to provide information when the workflow asks for it."
**Why P0:** This is our core differentiator. Workflows that pause for human input.
**Effort:** Medium (3-5 days) | **Difficulty:** High (complex state management)
**If we skip this:** We're just another automation tool.

---

#### 🟠 P2: Cancel a running workflow
**What it does:** Stop a workflow mid-execution.
**What this looks like:**
```bash
POST /api/executions/run_789/cancel

Response: {"status": "canceled"}
```
**User story:** "As a user, I want to stop a workflow I started by mistake."
**Why P2:** Nice UX, but we can just let workflows complete or fail naturally during dogfooding.
**Question:** How important is cleanup to you?
**Effort:** Small (1-2 days) | **Difficulty:** Medium
**If we skip this:** Annoying but workable.

---

#### 🟡 P1: View workflow execution history
**What it does:** See what steps executed and their outputs.
**What this looks like:**
```bash
GET /api/executions/run_789/history

Response: {
  "steps": [
    {
      "step_id": "collect_topic",
      "status": "completed",
      "output": {"topic": "AI", "audience": "developers"},
      "started_at": "2025-09-30T10:00:00Z",
      "ended_at": "2025-09-30T10:05:00Z"
    },
    {
      "step_id": "generate_draft",
      "status": "completed",
      "output": {"draft": "AI workflows are..."},
      "started_at": "2025-09-30T10:05:00Z",
      "ended_at": "2025-09-30T10:05:30Z"
    }
  ]
}
```
**User story:** "As a user, when my workflow fails, I want to see which step broke and why."
**Why P1:** Critical for debugging. Without this, you can't figure out what went wrong.
**Effort:** Medium (3-5 days) | **Difficulty:** Medium
**If we skip this:** Extremely painful debugging.

---

#### 🟡 P1: View current workflow data
**What it does:** See all the data flowing through the workflow.
**What this looks like:**
```bash
GET /api/executions/run_789/context

Response: {
  "static": {"env": "production", "company": "Acme"},
  "runtime": {
    "topic": "AI Workflows",
    "audience": "developers",
    "draft": "AI workflows are powerful..."
  }
}
```
**User story:** "As a user, I want to see what data is available to the AI prompt."
**Why P1:** Debugging tool. Helps understand why AI generated certain output.
**Effort:** Small (1-2 days) | **Difficulty:** Low
**If we skip this:** Harder to debug AI issues.

---

#### 🟠 P2: List all workflow runs
**What it does:** See all executions of a workflow.
**What this looks like:**
```bash
GET /api/executions?workflow_id=wf_123

Response: {
  "runs": [
    {"run_id": "run_789", "status": "completed", "started_at": "..."},
    {"run_id": "run_790", "status": "failed", "started_at": "..."}
  ]
}
```
**User story:** "As a user, I want to see all the times I ran this workflow."
**Why P2:** Discoverability. Can track run IDs manually for single-user dogfooding.
**Question:** Will multiple people be dogfooding at once?
**Effort:** Medium (3-5 days) | **Difficulty:** Low
**If we skip this:** Keep a spreadsheet of run IDs.

---

**Category Summary:**
- **Must Have (P0):** Start, Check status, Resume (3 features)
- **Should Have (P1):** History, Context view (2 features)
- **Maybe (P2):** Cancel, List runs (2 features)

---

## 3. The Five Step Types (What Workflows Can Do)

Think of these as the building blocks of workflows. Like Lego pieces.

---

### 🔴 Step Type 1: Forms (Collect Human Input)

**What it does:** Shows a form to the user, waits for submission.

**Real Example:**
```yaml
- id: collect_brief
  type: form
  fields:
    - name: topic
      type: text
      required: true
    - name: audience
      type: dropdown
      options: [developers, marketers, executives]
```

**What user sees:**
```
┌─ Blog Post Brief ─────────────┐
│ Topic: [____________]          │
│ Audience: [developers ▼]      │
│ [Submit]                       │
└───────────────────────────────┘
```

**After submission:**
- Workflow pauses, stores data: `{topic: "AI", audience: "developers"}`
- User gets resume token
- When they submit, workflow continues

#### Features:

**🔴 P0: Basic form rendering**
- Display fields, collect input, pause workflow
- **Effort:** Medium (3-5 days) | **Difficulty:** Medium

**🔴 P0: Field validation (required fields, data types)**
- Prevent submission if topic is blank
- Ensure audience is one of the 3 options
- **Effort:** Small (1-2 days) | **Difficulty:** Low

**🟡 P1: Advanced validation (regex, min/max length)**
- Example: Email must match `@` pattern
- Example: Age must be 18-100
- **Effort:** Small (1-2 days) | **Difficulty:** Low
- **If we skip:** Can add validation in later steps, just less user-friendly

**⚪ P3: Multi-file uploads**
- Upload PDFs, images, etc.
- **Why P3:** Adds S3 integration, virus scanning - very complex
- **When we'll need:** Post-launch for document workflows

---

### 🔴 Step Type 2: AI Generation (The Magic)

**What it does:** Calls AI (OpenAI, Anthropic) with a prompt, validates output.

**Real Example:**
```yaml
- id: generate_draft
  type: ai_generate
  prompt: |
    Write a blog post about {{topic}} for {{audience}}.
    Must be 1000 words.
  output_schema:
    type: object
    properties:
      title: {type: string}
      body: {type: string}
    required: [title, body]
```

**What happens:**
1. System builds prompt: "Write a blog post about AI for developers..."
2. Calls OpenAI GPT-4
3. Gets response: `{"title": "AI Workflows 101", "body": "..."}`
4. **Validates against schema:** Must have title AND body
5. If invalid (e.g., AI forgot body), **automatically retries** with error feedback
6. After 2 retries, fail workflow with clear error

**This is our unique value proposition.** No other platform does automatic schema enforcement + retries.

#### Features:

**🔴 P0: AI provider abstraction**
- Support multiple providers (OpenAI, Mock)
- Mock = fake AI for testing without burning API credits
- **Effort:** Medium (3-5 days) | **Difficulty:** Medium

**🔴 P0: JSON Schema validation**
- Check AI output matches required structure
- **Effort:** Large (1-2 weeks) | **Difficulty:** High (novel feature)

**🔴 P0: Automatic retry on validation failure (max 2)**
- First try: AI forgets `title` → Retry with error feedback
- Second try: Still missing `title` → Retry again
- Third failure: Give up, fail workflow
- **Effort:** Medium (3-5 days) | **Difficulty:** High

**🔴 P0: Variable interpolation (Jinja templates)**
- Replace `{{topic}}` with actual data from context
- **Effort:** Small (1-2 days) | **Difficulty:** Medium

**🟡 P1: Template ID system**
- Store prompts separately from workflows
- Reference by ID: `template_id: "blog_draft_v1"`
- **Why P1:** Cleaner than embedding prompts in YAML. Enables versioning later.
- **Effort:** Small (1-2 days) | **Difficulty:** Low
- **If we skip:** Prompts embedded in YAML (messier but works)

**⚪ P3: Template versioning & A/B testing**
- Track which prompts perform best
- **Why P3:** Optimization feature, not needed for dogfooding

---

### 🔴 Step Type 3: Conditionals (Branching Logic)

**What it does:** Route to different steps based on data.

**Real Example:**
```yaml
- id: check_score
  type: conditional
  condition: runtime.quality_score > 80
  if_true: auto_publish
  if_false: manual_review
```

**What happens:**
- If quality score > 80 → Skip to publishing
- If quality score ≤ 80 → Go to manual review

**Security note:** Expressions are sandboxed (no code injection). Only safe operations allowed.

#### Features:

**🔴 P0: Sandboxed expression evaluation**
- Parse expressions safely (no `eval()` hacks)
- **Why P0:** Security critical. Prevents malicious workflows.
- **Effort:** Medium (3-5 days) | **Difficulty:** High

**🔴 P0: Basic comparisons (>, <, ==, and, or)**
- Examples: `score > 80`, `status == "approved"`, `count > 0 and urgent == true`
- **Effort:** Small (1-2 days) | **Difficulty:** Medium

**🟡 P1: Advanced expressions (len, any, all)**
- Examples: `len(tags) > 0`, `any(x > 10 for x in scores)`
- **Effort:** Small (1-2 days) | **Difficulty:** Medium
- **If we skip:** Can use basic comparisons, just less powerful

---

### 🟡 Step Type 4: API Calls (External Integrations)

**What it does:** Make HTTP requests to external services.

**Real Example:**
```yaml
- id: publish_to_cms
  type: api_call
  method: POST
  url: https://cms.company.com/api/posts
  headers:
    Authorization: "Bearer {{env.CMS_API_KEY}}"
  body:
    title: "{{runtime.title}}"
    content: "{{runtime.body}}"
```

**What happens:**
- Builds POST request with data from workflow
- Calls CMS API to publish post
- Stores response in context

**Why P1 not P0:** Proves integration capability, but not unique to PyScaff. Can demo without this.

#### Features:

**🟡 P1: HTTP methods (GET/POST/PUT/PATCH/DELETE)**
- **Effort:** Medium (3-5 days) | **Difficulty:** Medium

**🟡 P1: URL/header/body templating**
- **Effort:** Small (1-2 days) | **Difficulty:** Medium

**🟡 P1: Timeout handling (default 30s)**
- **Effort:** Extra Small | **Difficulty:** Low

**🟠 P2: Retry on 5xx errors (exponential backoff)**
- **Question:** How important is robustness vs speed?
- **Effort:** Small (1-2 days) | **Difficulty:** Medium

---

### 🔴 Step Type 5: Approvals (Human Validation)

**What it does:** Send email to approvers, pause workflow, wait for approval.

**Real Example:**
```yaml
- id: manager_approval
  type: approval
  approvers:
    - manager@company.com
    - editor@company.com
```

**What happens:**
1. Workflow pauses
2. Emails sent to manager and editor:
   ```
   Subject: Approval Required - Blog Post Draft

   A blog post is waiting for approval:
   Title: AI Workflows 101

   [Approve] [Reject]
   ```
3. Manager clicks Approve
4. Workflow continues

#### Features:

**🔴 P0: Basic approval pause/resume**
- Pause workflow, track who approved
- **Effort:** Medium (3-5 days) | **Difficulty:** Medium

**🟡 P1: Email notifications**
- Send email when approval is needed
- **Why P1:** Without this, approvers don't know to act
- **If remote team:** Promote to P0
- **If co-located:** Can tap on shoulder, keep as P1
- **Question:** Are your approvers remote or in-office?
- **Effort:** Small (1-2 days) | **Difficulty:** Low

**🔴 P0: Approval tracking (who, when, comment)**
- Store: "Jane approved at 2PM on 9/30 with comment 'Looks good'"
- **Why P0:** Audit trail, compliance
- **Effort:** Small (1-2 days) | **Difficulty:** Low

**🟠 P2: Timeout & reminders**
- Remind after 12h, auto-reject after 24h
- **Question:** Needed for dogfooding or nice-to-have?
- **Effort:** Medium (3-5 days) | **Difficulty:** Medium

---

**Step Types Summary:**
- **Must Build (P0):** Form (basic), AI (full feature set), Conditional (security), Approval (basic)
- **Should Build (P1):** API call executor, email notifications, advanced validations
- **Context-Dependent (P2):** Timeouts, retries, reminders
- **Later (P3):** File uploads, template versioning

---

## 4. Under the Hood (Technical Stuff That Matters)

These are invisible to users but critical for reliability.

### 🔴 Preventing Data Corruption

**What it does:** If a step fails halfway, don't leave database in broken state.

**Real-world analogy:** Bank transfers
- Deduct $100 from your account
- Server crashes before adding to recipient
- **Without transactions:** You lost $100, recipient got nothing
- **With transactions:** Entire operation rolls back, money stays in your account

**In PyScaff:**
- Step 1: Save form data to database
- Step 2: Call AI (server crashes)
- **Without this feature:** Form data saved but workflow stuck
- **With this feature:** Form data rolled back, workflow restarts from beginning

#### Features:

**🔴 P0: Transaction per step**
- Each step is atomic (all-or-nothing)
- **Effort:** Medium (3-5 days) | **Difficulty:** High
- **If we skip:** Data corruption, very bad

**🔴 P0: Rollback on failure**
- Undo changes if step fails
- **Effort:** Small (1-2 days) | **Difficulty:** Medium
- **If we skip:** Broken workflows everywhere

**🟡 P1: Prevent race conditions**
- Two users can't resume same workflow simultaneously
- **Effort:** Small (1-2 days) | **Difficulty:** Medium
- **If we skip:** Rare bugs, but annoying

---

### 🟡 Preventing Duplicate Workflows

**What it does:** If you click "Submit" twice, don't create two workflows.

**Real-world analogy:** Online shopping
- Click "Buy Now"
- Network slow, click again
- **Without idempotency:** Charged twice
- **With idempotency:** Second click ignored

**In PyScaff:**
```bash
# First request
POST /api/executions {"workflow_id": "wf_123", ...}
Response: {"run_id": "run_789"}

# Accidental duplicate (same inputs)
POST /api/executions {"workflow_id": "wf_123", ...}
Response: {"run_id": "run_789"}  // Same ID, not duplicate
```

#### Features:

**🟡 P1: Idempotency keys**
- Detect duplicate requests
- **Why P1:** Production best practice. PRD lists as exit criteria.
- **Can dogfood without:** Yes, just be careful not to double-click
- **Effort:** Small (1-2 days) | **Difficulty:** Medium

---

### 🟡 Debugging & Monitoring

**What it does:** See what's happening inside workflows.

**Without debugging tools:**
- Workflow fails
- You stare at "Status: failed"
- No idea which step broke or why

**With debugging tools:**
```bash
GET /api/executions/run_789/history

{
  "steps": [
    {"step": "form", "status": "completed", "duration": "5s"},
    {"step": "ai_generate", "status": "failed", "error": "OpenAI timeout"},
    // ^ This step broke!
  ]
}
```

**Even better: Visual traces**
```
Form (5s) → AI Generate (FAILED after 60s timeout) ✗
```

#### Features:

**🟡 P1: Structured logs (JSON)**
- Every event logged in queryable format
- **Effort:** Small (1-2 days) | **Difficulty:** Low

**🟡 P1: Trace every workflow execution**
- See timeline of what happened when
- **Effort:** Medium (3-5 days) | **Difficulty:** Medium

**🟠 P2: Visual trace viewer (Jaeger)**
- Pretty graphs instead of raw logs
- **Question:** Critical for dogfooding or can use terminal logs?
- **Effort:** Small (1-2 days) | **Difficulty:** Low

**🟡 P1: Track AI costs**
- How many tokens did this workflow use?
- **Why P1:** Foundation for cost optimization
- **Effort:** Medium (3-5 days) | **Difficulty:** Medium

---

### 🟡 Security Basics

#### Features:

**🟡 P1: API key authentication**
- Require secret key to use API
- **Why P1:** Prevents random internet users from starting workflows
- **Effort:** Small (1-2 days) | **Difficulty:** Low

**🔴 P0: Sandboxed conditionals**
- Prevent code injection attacks
- **Why P0:** Security critical (covered above)

**🟠 P2: Redact sensitive data from logs**
- Don't log emails, SSNs, credit cards
- **Why P2:** Compliance. Ask: Are we handling customer data in MVID?
- **Effort:** Medium (3-5 days) | **Difficulty:** Medium

---

## 5. Setup & Infrastructure

These make it easy to run locally and deploy.

### 🔴 Local Development

**What it does:** Run entire system on your laptop with one command.

#### Features:

**🔴 P0: Docker setup**
- `docker-compose up` → everything runs
- **Why P0:** Others need to dogfood, can't troubleshoot setup for everyone
- **Effort:** Small (1-2 days) | **Difficulty:** Low

**🔴 P0: README with setup instructions**
- How to install, run tests, start workflows
- **Why P0:** Documentation for other team members
- **Effort:** Small (1-2 days) | **Difficulty:** Low

**🟡 P1: Automated testing in CI**
- Every code change runs tests automatically
- **Why P1:** Catches bugs before they reach dogfooding
- **Effort:** Medium (3-5 days) | **Difficulty:** Low

---

### 🟡 API Documentation

**What it does:** Explain how to use the API.

#### Features:

**🟡 P1: Interactive API docs (Swagger)**
- Web UI at `/docs` lets you try API calls
- **Why P1:** Self-service, don't need to ask devs how to use API
- **Effort:** Extra Small (Swagger auto-generated) | **Difficulty:** Low

**🔴 P0: README**
- Quick start guide
- **Effort:** Small | **Difficulty:** Low

---

## 6. Migration Tools (Only If Applicable)

**These are only needed if you're migrating from an old TypeScript system to new Python system.**

### 🟠 P2: Dual-Run Parity Harness

**What it does:** Run same workflow in old and new system, compare outputs.

**Use case:**
- You have 100 workflows running in old system
- Building new system in Python
- Need to prove new system produces same results

**How it works:**
```bash
POST /api/dev/dual-run {"workflow_id": "wf_123"}

Response: {
  "match": true,  // Outputs are identical (or close enough)
  "old_output": {...},
  "new_output": {...},
  "diffs": []  // What's different
}
```

#### Features:

**🟠 P2: Dual-run endpoint**
- **Question:** Is this a greenfield project or migration?
- **If greenfield:** Skip entirely (P3)
- **If migration:** Promote to P1
- **Effort:** Medium (3-5 days) | **Difficulty:** High

---

## 7. Future Features (Explicitly Not MVID)

These are great ideas for later. **Do not build for MVID.**

⚪ **Visual workflow builder** (drag-drop UI)
- Why not now: Very complex, YAML is fine for technical users

⚪ **Workflow templates marketplace**
- Why not now: Need users first, then they can share templates

⚪ **Multi-user permissions (RBAC)**
- Why not now: Single team dogfooding, everyone trusts everyone

⚪ **SOC 2 compliance**
- Why not now: Not selling to enterprises yet

⚪ **Workflow scheduling (cron jobs)**
- Why not now: Can trigger manually for MVID

⚪ **Webhook triggers**
- Why not now: Can use API calls for now

---

## Decision Time: 5 Questions to Answer

These will finalize what we build.

### Question 1: Migration or Greenfield?
**Are we migrating from an existing TypeScript system?**
- ✅ **If NO (greenfield):** Skip all migration tools (P2 → P3)
- ✅ **If YES (migration):** Dual-run harness is critical (P2 → P1)

---

### Question 2: How Many Dogfooders?
**How many people will use this internally?**
- ✅ **If 1-2 people:** Skip user management (Profile context P2 → P3, JWT auth P2 → P3)
- ✅ **If 5+ people:** Need discoverability (List workflows/runs P2 → P1, API auth P1 → P0)

---

### Question 3: Timeline Pressure?
**How fast do we need this?**
- ✅ **If 8-10 weeks:** P0 only (Conservative scope)
- ✅ **If 12-14 weeks:** P0 + selected P1 (Recommended scope) ← **Best choice**
- ✅ **If 16+ weeks:** Can add some P2 features

---

### Question 4: Concept Proof or Production-Ready?
**Are we just proving this works, or building for real use?**
- ✅ **If concept proof:** Can skip observability (P1 → P2), idempotency (P1 → P2)
- ✅ **If production-ready:** Keep P1 as-is, maybe promote some P2 → P1

---

### Question 5: Team Setup?
**Are approvers remote or co-located?**
- ✅ **If remote:** Email notifications are critical (P1 → P0)
- ✅ **If co-located:** Can tap on shoulder (P1 stays P1)

---

## Three Scope Options

### Option A: Conservative (P0 Only)
**Timeline:** 8-10 weeks | **Team:** 2-3 engineers

**What you get:**
- ✅ Create and run workflows
- ✅ Form, AI, Approval steps (no Conditional or API call)
- ✅ AI schema validation with retries (the core innovation)
- ✅ Pause/resume workflows
- ✅ Basic error handling

**What you DON'T get:**
- ❌ Branching logic (conditionals)
- ❌ External integrations (API calls)
- ❌ Nice debugging (just basic logs)
- ❌ Idempotency (can create duplicates)
- ❌ API docs (just README)

**Can you dogfood?** Yes, but painfully. Limited to simple linear workflows.

**Recommendation:** Only if timeline is extremely tight.

---

### Option B: Recommended (P0 + Selected P1) ⭐
**Timeline:** 12-14 weeks | **Team:** 2.5-3 engineers

**What you get (everything in A plus):**
- ✅ Conditional logic (branching workflows)
- ✅ API call executor (external integrations)
- ✅ Idempotency (no duplicate workflows)
- ✅ Good debugging (structured logs, execution history, traces)
- ✅ API documentation (Swagger UI)
- ✅ Email notifications for approvals
- ✅ Automated testing (CI/CD)
- ✅ Security basics (API keys)

**Can you dogfood?** Yes, comfortably. Can build real workflows, debug issues, iterate quickly.

**Recommendation:** ⭐ This is the sweet spot. Proves concept AND feels production-quality.

---

### Option C: Aggressive (P0 + P1 + Selected P2)
**Timeline:** 16-18 weeks | **Team:** 3-4 engineers

**What you get (everything in B plus):**
- ✅ Multi-user features (list workflows/runs)
- ✅ Migration tools (dual-run parity)
- ✅ Advanced security (PII redaction)
- ✅ Performance testing
- ✅ Advanced UX (cancel workflows, JWT auth)

**Can you dogfood?** Yes, enterprise-grade.

**Recommendation:** ⚠️ Risk of feature creep. Only if you have 4 months and large team.

---

## What Happens Next

### Step 1: Answer the 5 questions
- Migration or greenfield?
- How many dogfooders?
- Timeline?
- Concept vs production?
- Remote vs co-located?

### Step 2: Pick a scope
- Conservative (fast but limited)
- **Recommended** (balanced) ← **Pick this**
- Aggressive (comprehensive but slow)

### Step 3: Finalize feature list
- Based on your answers, move P2 features to P1/P3
- Lock down final scope

### Step 4: Write detailed spec
- Create `mvid-spec.md` with technical requirements
- Use for engineering kickoff

### Step 5: Start building
- Week 1-2: Foundation (database, API skeleton)
- Week 3-4: Simple executors (form, conditional)
- Week 5-7: AI integration (the hard part)
- Week 8-9: Approval + production hardening
- Week 10-12: Polish, testing, docs

---

## Summary for Executives

**What we're building:** A system that runs AI workflows with human approval steps.

**Our unique value:** Automatically fixes bad AI outputs (schema validation + retries).

**MVID goal:** Prove this works with 5-10 internal workflows.

**Recommended scope:** 65 features over 12-14 weeks with 3 engineers.

**Cost:** ~$60k-80k in engineering time (3 people × 3 months × $80k/yr avg salary).

**Risk if we cut too much:** Can't prove the concept works, wasted effort.

**Risk if we build too much:** Takes 6 months, market moves on, we're too late.

**Recommendation:** Build Option B (Recommended scope). Delivers production-quality MVID in 3 months.

---

## Questions?

**This document is a conversation starter.** I've tried to explain everything in plain English, but I'm sure things are unclear.

**Please ask:**
- "What does X mean?"
- "Why is Y only P1 instead of P0?"
- "Can we cut Z to ship faster?"
- "What if we want to [use case]?"

**I'm here to help you make the right scope decisions for MVID.**

---

**Document Status:** Ready for product review
**Next Step:** Answer 5 decision questions → Finalize scope → Write detailed spec