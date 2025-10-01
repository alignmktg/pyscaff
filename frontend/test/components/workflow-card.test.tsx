import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { WorkflowCard } from "@/components/workflow-card"
import { Workflow } from "@/lib/types"

const mockWorkflow: Workflow = {
  id: "wf-test",
  version: 1,
  name: "Test Workflow",
  definition: {},
  start_step: "step1",
  steps: [
    {
      id: "step1",
      type: "form",
      name: "Step 1",
      next: null,
      config: {},
    },
  ],
  updated_at: "2025-10-01T00:00:00Z",
}

describe("WorkflowCard", () => {
  it("renders workflow name", () => {
    render(<WorkflowCard workflow={mockWorkflow} />)
    expect(screen.getByText("Test Workflow")).toBeInTheDocument()
  })

  it("renders version badge", () => {
    render(<WorkflowCard workflow={mockWorkflow} />)
    expect(screen.getByText("Version 1")).toBeInTheDocument()
    expect(screen.getByText("v1")).toBeInTheDocument()
  })

  it("renders step count", () => {
    render(<WorkflowCard workflow={mockWorkflow} />)
    expect(screen.getByText("1 steps")).toBeInTheDocument()
  })

  it("renders updated date", () => {
    render(<WorkflowCard workflow={mockWorkflow} />)
    expect(screen.getByText(/Updated/)).toBeInTheDocument()
  })
})
