import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { RunTimeline } from "@/components/run/run-timeline"
import { RunStep } from "@/lib/types"

const mockSteps: RunStep[] = [
  {
    id: "step-1",
    run_id: "run-1",
    step_id: "collect_data",
    type: "form",
    status: "completed",
    started_at: "2025-10-01T10:00:00Z",
    ended_at: "2025-10-01T10:05:00Z",
    output: { field1: "value1" },
  },
  {
    id: "step-2",
    run_id: "run-1",
    step_id: "generate_content",
    type: "ai_generate",
    status: "running",
    started_at: "2025-10-01T10:05:00Z",
  },
  {
    id: "step-3",
    run_id: "run-1",
    step_id: "failed_step",
    type: "conditional",
    status: "failed",
    started_at: "2025-10-01T10:10:00Z",
    ended_at: "2025-10-01T10:10:30Z",
    error: "Condition evaluation failed",
  },
]

describe("RunTimeline", () => {
  it("renders all steps", () => {
    render(<RunTimeline steps={mockSteps} />)
    expect(screen.getByText("collect_data")).toBeInTheDocument()
    expect(screen.getByText("generate_content")).toBeInTheDocument()
    expect(screen.getByText("failed_step")).toBeInTheDocument()
  })

  it("shows step types", () => {
    render(<RunTimeline steps={mockSteps} />)
    expect(screen.getByText("form")).toBeInTheDocument()
    expect(screen.getByText("ai_generate")).toBeInTheDocument()
    expect(screen.getByText("conditional")).toBeInTheDocument()
  })

  it("shows step status badges", () => {
    render(<RunTimeline steps={mockSteps} />)
    expect(screen.getByText("completed")).toBeInTheDocument()
    expect(screen.getByText("running")).toBeInTheDocument()
    expect(screen.getByText("failed")).toBeInTheDocument()
  })

  it("displays error message for failed steps", () => {
    render(<RunTimeline steps={mockSteps} />)
    expect(screen.getByText("Condition evaluation failed")).toBeInTheDocument()
  })

  it("shows empty state when no steps", () => {
    render(<RunTimeline steps={[]} />)
    expect(screen.getByText("No steps executed yet")).toBeInTheDocument()
  })

  it("displays timestamps", () => {
    render(<RunTimeline steps={mockSteps} />)
    expect(screen.getAllByText(/Started:/)).toHaveLength(3)
  })
})
