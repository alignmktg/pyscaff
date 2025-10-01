import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { RunList } from "@/components/run/run-list"
import { Run } from "@/lib/types"

const mockRuns: Run[] = [
  {
    id: "run-1",
    workflow_id: "wf-1",
    workflow_version: 1,
    status: "completed",
    context: { static: {}, profile: {}, runtime: {} },
    started_at: "2025-10-01T10:00:00Z",
    updated_at: "2025-10-01T10:30:00Z",
  },
  {
    id: "run-2",
    workflow_id: "wf-2",
    workflow_version: 2,
    status: "running",
    current_step: "generate_content",
    context: { static: {}, profile: {}, runtime: {} },
    started_at: "2025-10-01T11:00:00Z",
    updated_at: "2025-10-01T11:15:00Z",
  },
  {
    id: "run-3",
    workflow_id: "wf-1",
    workflow_version: 1,
    status: "failed",
    context: { static: {}, profile: {}, runtime: {} },
    started_at: "2025-10-01T09:00:00Z",
    updated_at: "2025-10-01T09:05:00Z",
  },
]

describe("RunList", () => {
  it("renders all runs", () => {
    render(<RunList runs={mockRuns} />)
    expect(screen.getByText("run-1")).toBeInTheDocument()
    expect(screen.getByText("run-2")).toBeInTheDocument()
    expect(screen.getByText("run-3")).toBeInTheDocument()
  })

  it("displays status badges", () => {
    render(<RunList runs={mockRuns} />)
    // Use getAllByText since these words appear in both filter buttons and status badges
    expect(screen.getAllByText("Completed").length).toBeGreaterThan(0)
    expect(screen.getAllByText("Running").length).toBeGreaterThan(0)
    expect(screen.getAllByText("Failed").length).toBeGreaterThan(0)
  })

  it("displays current step for running runs", () => {
    render(<RunList runs={mockRuns} />)
    expect(screen.getByText("generate_content")).toBeInTheDocument()
  })

  it("filters runs by search term", async () => {
    const user = userEvent.setup()
    render(<RunList runs={mockRuns} />)

    const searchInput = screen.getByPlaceholderText(/Search by run ID/)
    await user.type(searchInput, "run-1")

    expect(screen.getByText("run-1")).toBeInTheDocument()
    expect(screen.queryByText("run-2")).not.toBeInTheDocument()
    expect(screen.queryByText("run-3")).not.toBeInTheDocument()
  })

  it("filters runs by status", async () => {
    const user = userEvent.setup()
    render(<RunList runs={mockRuns} />)

    const runningButton = screen.getByRole("button", { name: /Running/i })
    await user.click(runningButton)

    expect(screen.queryByText("run-1")).not.toBeInTheDocument()
    expect(screen.getByText("run-2")).toBeInTheDocument()
    expect(screen.queryByText("run-3")).not.toBeInTheDocument()
  })

  it("shows empty state when no runs match filters", async () => {
    const user = userEvent.setup()
    render(<RunList runs={mockRuns} />)

    const searchInput = screen.getByPlaceholderText(/Search by run ID/)
    await user.type(searchInput, "nonexistent")

    expect(screen.getByText(/No runs found matching your filters/)).toBeInTheDocument()
  })
})
