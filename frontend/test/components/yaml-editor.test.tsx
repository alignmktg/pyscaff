import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { YamlEditor } from "@/components/yaml-editor"

// Mock Monaco Editor since it requires DOM APIs
vi.mock("@monaco-editor/react", () => ({
  default: ({ value, onChange }: { value: string; onChange: (val: string) => void }) => (
    <textarea
      data-testid="monaco-editor"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}))

describe("YamlEditor", () => {
  it("renders with initial value", () => {
    const mockOnChange = vi.fn()
    render(<YamlEditor value="test: value" onChange={mockOnChange} />)

    expect(screen.getByTestId("monaco-editor")).toHaveValue("test: value")
  })

  it("shows validate button", () => {
    const mockOnChange = vi.fn()
    render(<YamlEditor value="test: value" onChange={mockOnChange} />)

    expect(screen.getByText("Validate")).toBeInTheDocument()
  })

  it("validates valid YAML successfully", () => {
    const mockOnChange = vi.fn()
    const mockOnValidate = vi.fn()
    const validYaml = `name: Test
steps: []`

    render(
      <YamlEditor
        value={validYaml}
        onChange={mockOnChange}
        onValidate={mockOnValidate}
      />
    )

    fireEvent.click(screen.getByText("Validate"))

    expect(mockOnValidate).toHaveBeenCalledWith(true)
    expect(screen.getByText("Valid YAML")).toBeInTheDocument()
  })

  it("shows error for invalid YAML", () => {
    const mockOnChange = vi.fn()
    const mockOnValidate = vi.fn()
    const invalidYaml = "test: [invalid"

    render(
      <YamlEditor
        value={invalidYaml}
        onChange={mockOnChange}
        onValidate={mockOnValidate}
      />
    )

    fireEvent.click(screen.getByText("Validate"))

    expect(mockOnValidate).toHaveBeenCalledWith(false, expect.any(String))
    expect(screen.getByText("Invalid YAML")).toBeInTheDocument()
  })
})
