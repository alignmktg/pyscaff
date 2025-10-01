// API types matching backend schemas from CLAUDE.md

export interface Step {
  id: string
  type: "form" | "ai_generate" | "conditional" | "api_call" | "approval"
  name: string
  next: string | null
  config: Record<string, unknown>
}

export interface Workflow {
  id: string
  version: number
  name: string
  definition: Record<string, unknown>
  start_step: string
  steps: Step[]
  created_at?: string
  updated_at?: string
}

export type RunStatus =
  | "queued"
  | "running"
  | "waiting"
  | "completed"
  | "failed"
  | "canceled"

export interface Run {
  id: string
  workflow_id: string
  workflow_version: number
  status: RunStatus
  current_step?: string
  context: {
    static?: Record<string, unknown>
    profile?: Record<string, unknown>
    runtime?: Record<string, unknown>
  }
  started_at: string
  updated_at: string
  idempotency_key?: string
}

export interface RunStep {
  id: string
  run_id: string
  step_id: string
  type: string
  status: "pending" | "running" | "completed" | "failed"
  started_at: string
  ended_at?: string
  output?: Record<string, unknown>
  error?: string
}

export interface ApprovalDetails {
  run_id: string
  workflow_id: string
  workflow_name: string
  step_id: string
  step_name: string
  context_excerpt: Record<string, unknown>
  status: "pending" | "approved" | "rejected"
}

export interface ApprovalDecision {
  decision: "approve" | "reject"
  comment?: string
}
