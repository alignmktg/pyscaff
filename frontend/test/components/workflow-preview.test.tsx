import { describe, it, expect, vi } from "vitest"
import { render } from "@testing-library/react"
import { WorkflowPreview } from "@/components/workflow-preview"

// Mock ReactFlow CSS import
vi.mock("@xyflow/react/dist/style.css", () => ({}))

// Mock ReactFlow since it requires complex DOM setup
vi.mock("@xyflow/react", () => ({
  ReactFlow: ({ nodes }: { nodes: unknown[] }) => (
    <div data-testid="react-flow">
      {nodes.length} nodes rendered
    </div>
  ),
  Background: () => <div />,
  Controls: () => <div />,
  MiniMap: () => <div />,
  useNodesState: (initial: unknown[]) => [initial, vi.fn(), vi.fn()],
  useEdgesState: (initial: unknown[]) => [initial, vi.fn(), vi.fn()],
  Position: { Top: "top", Bottom: "bottom" },
}))

describe("WorkflowPreview", () => {
  it("renders ReactFlow component", () => {
    const yamlContent = `
      name: Test Workflow
      steps:
        - id: step1
          type: form
          name: Step 1
          next: step2
        - id: step2
          type: api_call
          name: Step 2
          next: null
    `

    const { getByTestId } = render(<WorkflowPreview yamlContent={yamlContent} />)

    expect(getByTestId("react-flow")).toBeInTheDocument()
  })

  it("handles empty YAML gracefully", () => {
    const { getByTestId } = render(<WorkflowPreview yamlContent="" />)

    expect(getByTestId("react-flow")).toBeInTheDocument()
  })

  it("handles invalid YAML gracefully", () => {
    const { getByTestId } = render(
      <WorkflowPreview yamlContent="invalid: [yaml" />
    )

    expect(getByTestId("react-flow")).toBeInTheDocument()
  })
})
