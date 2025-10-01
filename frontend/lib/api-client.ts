import { Workflow, Run, RunStep, ApprovalDetails, ApprovalDecision } from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "sk_internal_dogfood_dev"

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }

  return response.json()
}

export const workflowsApi = {
  list: () => fetchAPI<{ workflows: Workflow[]; total: number }>("/v1/workflows"),
  get: (id: string) => fetchAPI<Workflow>(`/v1/workflows/${id}`),
  create: (workflow: Partial<Workflow>) =>
    fetchAPI<Workflow>("/v1/workflows", {
      method: "POST",
      body: JSON.stringify(workflow),
    }),
}

export const executionsApi = {
  list: () => fetchAPI<{ runs: Run[]; total: number }>("/v1/executions"),
  get: (id: string) => fetchAPI<Run>(`/v1/executions/${id}`),
  getHistory: (id: string) => fetchAPI<{ steps: RunStep[] }>(`/v1/executions/${id}/history`),
  getContext: (id: string) => fetchAPI<Run["context"]>(`/v1/executions/${id}/context`),
  start: (workflowId: string, inputs?: Record<string, unknown>, idempotencyKey?: string) =>
    fetchAPI<Run>("/v1/executions", {
      method: "POST",
      body: JSON.stringify({
        workflow_id: workflowId,
        inputs,
        idempotency_key: idempotencyKey,
      }),
    }),
  resume: (id: string, inputs: Record<string, unknown>) =>
    fetchAPI<Run>(`/v1/executions/${id}/resume`, {
      method: "POST",
      body: JSON.stringify({ inputs }),
    }),
  cancel: (id: string) =>
    fetchAPI<Run>(`/v1/executions/${id}/cancel`, {
      method: "POST",
    }),
}

export const approvalsApi = {
  getDetails: (token: string) => fetchAPI<ApprovalDetails>(`/v1/approvals/${token}`),
  submit: (token: string, decision: ApprovalDecision) =>
    fetchAPI<{ status: string; message: string }>(`/v1/approvals/${token}/submit`, {
      method: "POST",
      body: JSON.stringify(decision),
    }),
}
