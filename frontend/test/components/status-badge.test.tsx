import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { StatusBadge } from "@/components/run/status-badge"

describe("StatusBadge", () => {
  it("renders queued status with correct styling", () => {
    render(<StatusBadge status="queued" />)
    expect(screen.getByText("Queued")).toBeInTheDocument()
  })

  it("renders running status with correct styling", () => {
    render(<StatusBadge status="running" />)
    expect(screen.getByText("Running")).toBeInTheDocument()
  })

  it("renders waiting status with correct styling", () => {
    render(<StatusBadge status="waiting" />)
    expect(screen.getByText("Waiting")).toBeInTheDocument()
  })

  it("renders completed status with correct styling", () => {
    render(<StatusBadge status="completed" />)
    expect(screen.getByText("Completed")).toBeInTheDocument()
  })

  it("renders failed status with correct styling", () => {
    render(<StatusBadge status="failed" />)
    expect(screen.getByText("Failed")).toBeInTheDocument()
  })

  it("renders canceled status with correct styling", () => {
    render(<StatusBadge status="canceled" />)
    expect(screen.getByText("Canceled")).toBeInTheDocument()
  })
})
