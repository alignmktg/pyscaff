import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { EmptyState } from "@/components/empty-state"

describe("EmptyState", () => {
  it("renders title and description", () => {
    render(
      <EmptyState
        title="No items"
        description="Create your first item"
        actionLabel="Create"
        actionHref="/create"
      />
    )

    expect(screen.getByText("No items")).toBeInTheDocument()
    expect(screen.getByText("Create your first item")).toBeInTheDocument()
  })

  it("renders action button with correct href", () => {
    render(
      <EmptyState
        title="No items"
        description="Create your first item"
        actionLabel="Create Item"
        actionHref="/create"
      />
    )

    const link = screen.getByRole("link")
    expect(link).toHaveAttribute("href", "/create")
    expect(screen.getByText("Create Item")).toBeInTheDocument()
  })
})
