import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { ContextExplorer } from "@/components/run/context-explorer"

describe("ContextExplorer", () => {
  it("shows empty state when no context data", () => {
    render(<ContextExplorer context={{ static: {}, profile: {}, runtime: {} }} />)
    expect(screen.getByText("No context data available")).toBeInTheDocument()
  })

  it("renders static context section", () => {
    const context = {
      static: { config: "value" },
      profile: {},
      runtime: {},
    }
    render(<ContextExplorer context={context} />)
    expect(screen.getByText("Static")).toBeInTheDocument()
  })

  it("renders profile context section", () => {
    const context = {
      static: {},
      profile: { userId: "123" },
      runtime: {},
    }
    render(<ContextExplorer context={context} />)
    expect(screen.getByText("Profile")).toBeInTheDocument()
  })

  it("renders runtime context section", () => {
    const context = {
      static: {},
      profile: {},
      runtime: { topic: "AI" },
    }
    render(<ContextExplorer context={context} />)
    expect(screen.getByText("Runtime")).toBeInTheDocument()
  })

  it("displays key count badges", () => {
    const context = {
      static: { key1: "val1", key2: "val2" },
      profile: {},
      runtime: {},
    }
    render(<ContextExplorer context={context} />)
    expect(screen.getByText("2 keys")).toBeInTheDocument()
  })

  it("renders string values correctly", () => {
    const context = {
      static: {},
      profile: {},
      runtime: { topic: "React" },
    }
    render(<ContextExplorer context={context} />)
    expect(screen.getByText("topic:")).toBeInTheDocument()
    expect(screen.getByText('"React"')).toBeInTheDocument()
  })

  it("renders number values correctly", () => {
    const context = {
      static: {},
      profile: {},
      runtime: { count: 42 },
    }
    render(<ContextExplorer context={context} />)
    expect(screen.getByText("count:")).toBeInTheDocument()
    expect(screen.getByText("42")).toBeInTheDocument()
  })

  it("renders boolean values correctly", () => {
    const context = {
      static: {},
      profile: {},
      runtime: { isActive: true },
    }
    render(<ContextExplorer context={context} />)
    expect(screen.getByText("isActive:")).toBeInTheDocument()
    expect(screen.getByText("true")).toBeInTheDocument()
  })

  it("expands and collapses nested objects", async () => {
    const user = userEvent.setup()
    const context = {
      static: {},
      profile: {},
      runtime: {
        nested: {
          key: "value",
        },
      },
    }
    render(<ContextExplorer context={context} />)

    // Should be expanded by default (depth < 2)
    expect(screen.getByText("key:")).toBeInTheDocument()

    // Click to collapse
    const nestedNode = screen.getByText("nested")
    await user.click(nestedNode)

    // Should show collapsed indicator
    expect(screen.getByText("{...}")).toBeInTheDocument()
  })
})
