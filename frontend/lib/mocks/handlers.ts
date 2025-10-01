import { http, HttpResponse } from "msw"
import { mockWorkflows, mockRuns, mockRunSteps, mockApprovals } from "../mock-data"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export const handlers = [
  // GET /v1/workflows - List all workflows
  http.get(`${API_URL}/v1/workflows`, () => {
    return HttpResponse.json({
      workflows: mockWorkflows,
      total: mockWorkflows.length,
    })
  }),

  // GET /v1/workflows/:id - Get workflow by ID
  http.get(`${API_URL}/v1/workflows/:id`, ({ params }) => {
    const { id } = params
    const workflow = mockWorkflows.find((w) => w.id === id)

    if (!workflow) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(workflow)
  }),

  // POST /v1/workflows - Create workflow (not implemented yet)
  http.post(`${API_URL}/v1/workflows`, () => {
    return new HttpResponse(null, {
      status: 501,
      statusText: "Not Implemented - Backend API pending",
    })
  }),

  // GET /v1/executions - List all runs
  http.get(`${API_URL}/v1/executions`, () => {
    return HttpResponse.json({
      runs: mockRuns,
      total: mockRuns.length,
    })
  }),

  // GET /v1/executions/:id - Get run by ID
  http.get(`${API_URL}/v1/executions/:id`, ({ params }) => {
    const { id } = params
    const run = mockRuns.find((r) => r.id === id)

    if (!run) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(run)
  }),

  // GET /v1/executions/:id/history - Get run execution history
  http.get(`${API_URL}/v1/executions/:id/history`, ({ params }) => {
    const { id } = params
    const steps = mockRunSteps[id as string] || []

    return HttpResponse.json({ steps })
  }),

  // GET /v1/executions/:id/context - Get run context
  http.get(`${API_URL}/v1/executions/:id/context`, ({ params }) => {
    const { id } = params
    const run = mockRuns.find((r) => r.id === id)

    if (!run) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(run.context)
  }),

  // POST /v1/executions - Start run (not implemented yet)
  http.post(`${API_URL}/v1/executions`, () => {
    return new HttpResponse(null, {
      status: 501,
      statusText: "Not Implemented - Backend API pending",
    })
  }),

  // POST /v1/executions/:id/resume - Resume run (not implemented yet)
  http.post(`${API_URL}/v1/executions/:id/resume`, () => {
    return new HttpResponse(null, {
      status: 501,
      statusText: "Not Implemented - Backend API pending",
    })
  }),

  // POST /v1/executions/:id/cancel - Cancel run (not implemented yet)
  http.post(`${API_URL}/v1/executions/:id/cancel`, () => {
    return new HttpResponse(null, {
      status: 501,
      statusText: "Not Implemented - Backend API pending",
    })
  }),

  // GET /v1/approvals/:token - Get approval details
  http.get(`${API_URL}/v1/approvals/:token`, ({ params }) => {
    const { token } = params
    const approval = mockApprovals[token as string]

    if (!approval) {
      return new HttpResponse(null, {
        status: 404,
        statusText: "Approval not found or token expired",
      })
    }

    if (approval.status !== "pending") {
      return new HttpResponse(
        JSON.stringify({
          error: "Approval already processed",
          status: approval.status,
        }),
        {
          status: 410,
          statusText: "Gone",
          headers: { "Content-Type": "application/json" },
        }
      )
    }

    return HttpResponse.json(approval)
  }),

  // POST /v1/approvals/:token/submit - Submit approval decision
  http.post(`${API_URL}/v1/approvals/:token/submit`, async ({ params, request }) => {
    const { token } = params
    const approval = mockApprovals[token as string]

    if (!approval) {
      return new HttpResponse(null, {
        status: 404,
        statusText: "Approval not found or token expired",
      })
    }

    if (approval.status !== "pending") {
      return new HttpResponse(
        JSON.stringify({
          error: "Approval already processed",
          status: approval.status,
        }),
        {
          status: 410,
          statusText: "Gone",
          headers: { "Content-Type": "application/json" },
        }
      )
    }

    const body = (await request.json()) as { decision: "approve" | "reject"; comment?: string }

    // Simulate processing
    approval.status = body.decision === "approve" ? "approved" : "rejected"

    return HttpResponse.json({
      status: "success",
      message: `Approval ${body.decision === "approve" ? "approved" : "rejected"} successfully`,
    })
  }),
]
