import { Workflow, Run, RunStep, ApprovalDetails } from "./types"

export const mockWorkflows: Workflow[] = [
  {
    id: "wf-1",
    version: 1,
    name: "Blog Post Generator",
    definition: {
      name: "Blog Post Generator",
      steps: [],
    },
    start_step: "collect_topic",
    steps: [
      {
        id: "collect_topic",
        type: "form",
        name: "Collect Topic",
        next: "generate_outline",
        config: {
          fields: [
            { key: "topic", type: "text", required: true },
            { key: "audience", type: "select", options: ["developers", "marketers"] },
          ],
        },
      },
      {
        id: "generate_outline",
        type: "ai_generate",
        name: "Generate Outline",
        next: "approval",
        config: {
          template_id: "blog_outline",
          variables: ["topic", "audience"],
          json_schema: {
            type: "object",
            properties: {
              sections: {
                type: "array",
                items: { type: "string" },
              },
            },
          },
        },
      },
      {
        id: "approval",
        type: "approval",
        name: "Approve Outline",
        next: null,
        config: {
          approvers: ["editor@example.com"],
        },
      },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "wf-2",
    version: 1,
    name: "Customer Onboarding",
    definition: {
      name: "Customer Onboarding",
      steps: [],
    },
    start_step: "collect_info",
    steps: [
      {
        id: "collect_info",
        type: "form",
        name: "Collect Customer Info",
        next: "create_account",
        config: {
          fields: [
            { key: "company_name", type: "text", required: true },
            { key: "industry", type: "select", options: ["tech", "finance", "healthcare"] },
          ],
        },
      },
      {
        id: "create_account",
        type: "api_call",
        name: "Create Account",
        next: "send_welcome",
        config: {
          url: "https://api.example.com/accounts",
          method: "POST",
          headers: { "Content-Type": "application/json" },
        },
      },
      {
        id: "send_welcome",
        type: "ai_generate",
        name: "Generate Welcome Email",
        next: null,
        config: {
          template_id: "welcome_email",
          variables: ["company_name"],
          json_schema: {
            type: "object",
            properties: {
              subject: { type: "string" },
              body: { type: "string" },
            },
          },
        },
      },
    ],
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: "wf-3",
    version: 2,
    name: "Support Ticket Triage",
    definition: {
      name: "Support Ticket Triage",
      steps: [],
    },
    start_step: "analyze_ticket",
    steps: [
      {
        id: "analyze_ticket",
        type: "ai_generate",
        name: "Analyze Ticket",
        next: "route_ticket",
        config: {
          template_id: "ticket_analysis",
          variables: ["ticket_content"],
          json_schema: {
            type: "object",
            properties: {
              category: { type: "string" },
              priority: { type: "string" },
              suggested_team: { type: "string" },
            },
          },
        },
      },
      {
        id: "route_ticket",
        type: "conditional",
        name: "Route to Team",
        next: null,
        config: {
          when: "priority == 'high'",
        },
      },
    ],
    created_at: new Date(Date.now() - 172800000).toISOString(),
    updated_at: new Date(Date.now() - 3600000).toISOString(),
  },
]

export const mockRuns: Run[] = [
  {
    id: "run-1",
    workflow_id: "wf-1",
    workflow_version: 1,
    status: "completed",
    current_step: undefined,
    context: {
      static: {},
      profile: {},
      runtime: {
        topic: "React Server Components",
        audience: "developers",
        sections: ["Introduction", "Benefits", "Implementation", "Best Practices"],
      },
    },
    started_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: "run-2",
    workflow_id: "wf-1",
    workflow_version: 1,
    status: "waiting",
    current_step: "approval",
    context: {
      static: {},
      profile: {},
      runtime: {
        topic: "Next.js 15 Features",
        audience: "developers",
        sections: ["App Router", "Server Actions", "Turbopack", "Caching"],
      },
    },
    started_at: new Date(Date.now() - 1800000).toISOString(),
    updated_at: new Date(Date.now() - 900000).toISOString(),
  },
  {
    id: "run-3",
    workflow_id: "wf-2",
    workflow_version: 1,
    status: "running",
    current_step: "send_welcome",
    context: {
      static: {},
      profile: {},
      runtime: {
        company_name: "Acme Corp",
        industry: "tech",
        account_id: "acc-123",
      },
    },
    started_at: new Date(Date.now() - 300000).toISOString(),
    updated_at: new Date(Date.now() - 60000).toISOString(),
  },
  {
    id: "run-4",
    workflow_id: "wf-3",
    workflow_version: 2,
    status: "failed",
    current_step: "route_ticket",
    context: {
      static: {},
      profile: {},
      runtime: {
        ticket_content: "Cannot access dashboard",
        category: "technical",
        priority: "high",
      },
    },
    started_at: new Date(Date.now() - 7200000).toISOString(),
    updated_at: new Date(Date.now() - 7140000).toISOString(),
  },
  {
    id: "run-5",
    workflow_id: "wf-1",
    workflow_version: 1,
    status: "queued",
    current_step: undefined,
    context: {
      static: {},
      profile: {},
      runtime: {},
    },
    started_at: new Date(Date.now() - 60000).toISOString(),
    updated_at: new Date(Date.now() - 60000).toISOString(),
  },
]

export const mockRunSteps: Record<string, RunStep[]> = {
  "run-1": [
    {
      id: "step-1-1",
      run_id: "run-1",
      step_id: "collect_topic",
      type: "form",
      status: "completed",
      started_at: new Date(Date.now() - 3600000).toISOString(),
      ended_at: new Date(Date.now() - 3540000).toISOString(),
      output: {
        topic: "React Server Components",
        audience: "developers",
      },
    },
    {
      id: "step-1-2",
      run_id: "run-1",
      step_id: "generate_outline",
      type: "ai_generate",
      status: "completed",
      started_at: new Date(Date.now() - 3540000).toISOString(),
      ended_at: new Date(Date.now() - 3480000).toISOString(),
      output: {
        sections: ["Introduction", "Benefits", "Implementation", "Best Practices"],
      },
    },
    {
      id: "step-1-3",
      run_id: "run-1",
      step_id: "approval",
      type: "approval",
      status: "completed",
      started_at: new Date(Date.now() - 3480000).toISOString(),
      ended_at: new Date(Date.now() - 1800000).toISOString(),
      output: {
        approved: true,
        approver: "editor@example.com",
      },
    },
  ],
  "run-2": [
    {
      id: "step-2-1",
      run_id: "run-2",
      step_id: "collect_topic",
      type: "form",
      status: "completed",
      started_at: new Date(Date.now() - 1800000).toISOString(),
      ended_at: new Date(Date.now() - 1740000).toISOString(),
      output: {
        topic: "Next.js 15 Features",
        audience: "developers",
      },
    },
    {
      id: "step-2-2",
      run_id: "run-2",
      step_id: "generate_outline",
      type: "ai_generate",
      status: "completed",
      started_at: new Date(Date.now() - 1740000).toISOString(),
      ended_at: new Date(Date.now() - 1680000).toISOString(),
      output: {
        sections: ["App Router", "Server Actions", "Turbopack", "Caching"],
      },
    },
    {
      id: "step-2-3",
      run_id: "run-2",
      step_id: "approval",
      type: "approval",
      status: "running",
      started_at: new Date(Date.now() - 1680000).toISOString(),
    },
  ],
  "run-3": [
    {
      id: "step-3-1",
      run_id: "run-3",
      step_id: "collect_info",
      type: "form",
      status: "completed",
      started_at: new Date(Date.now() - 300000).toISOString(),
      ended_at: new Date(Date.now() - 240000).toISOString(),
      output: {
        company_name: "Acme Corp",
        industry: "tech",
      },
    },
    {
      id: "step-3-2",
      run_id: "run-3",
      step_id: "create_account",
      type: "api_call",
      status: "completed",
      started_at: new Date(Date.now() - 240000).toISOString(),
      ended_at: new Date(Date.now() - 180000).toISOString(),
      output: {
        account_id: "acc-123",
      },
    },
    {
      id: "step-3-3",
      run_id: "run-3",
      step_id: "send_welcome",
      type: "ai_generate",
      status: "running",
      started_at: new Date(Date.now() - 180000).toISOString(),
    },
  ],
  "run-4": [
    {
      id: "step-4-1",
      run_id: "run-4",
      step_id: "analyze_ticket",
      type: "ai_generate",
      status: "completed",
      started_at: new Date(Date.now() - 7200000).toISOString(),
      ended_at: new Date(Date.now() - 7140000).toISOString(),
      output: {
        category: "technical",
        priority: "high",
        suggested_team: "engineering",
      },
    },
    {
      id: "step-4-2",
      run_id: "run-4",
      step_id: "route_ticket",
      type: "conditional",
      status: "failed",
      started_at: new Date(Date.now() - 7140000).toISOString(),
      ended_at: new Date(Date.now() - 7140000).toISOString(),
      error: "Failed to evaluate condition: missing required variable",
    },
  ],
  "run-5": [],
}

export const mockApprovals: Record<string, ApprovalDetails> = {
  "abc123xyz": {
    run_id: "run-1",
    workflow_id: "wf-1",
    workflow_name: "Lead Qualification",
    step_id: "approval_step",
    step_name: "Sales Manager Approval",
    context_excerpt: {
      lead_name: "Acme Corp",
      score: 85,
      source: "Inbound",
      contact_email: "john@acme.com",
    },
    status: "pending",
  },
  "def456uvw": {
    run_id: "run-2",
    workflow_id: "wf-1",
    workflow_name: "Blog Post Generator",
    step_id: "approval",
    step_name: "Approve Outline",
    context_excerpt: {
      topic: "AI in Marketing",
      audience: "marketers",
      outline_sections: ["Introduction", "Use Cases", "Best Practices", "Conclusion"],
    },
    status: "pending",
  },
  "expired123": {
    run_id: "run-3",
    workflow_id: "wf-2",
    workflow_name: "Customer Onboarding",
    step_id: "final_approval",
    step_name: "Manager Approval",
    context_excerpt: {
      company_name: "TechStart Inc",
      industry: "tech",
    },
    status: "approved",
  },
}
