import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { Markdown } from "@/components/ui/markdown"

describe("Markdown", () => {
  it("renders headings correctly", () => {
    render(
      <Markdown>
        {`# Heading 1
## Heading 2
### Heading 3`}
      </Markdown>
    )
    expect(screen.getByText("Heading 1")).toBeInTheDocument()
    expect(screen.getByText("Heading 2")).toBeInTheDocument()
    expect(screen.getByText("Heading 3")).toBeInTheDocument()
  })

  it("renders lists correctly", () => {
    render(
      <Markdown>
        {`- Item 1
- Item 2
- Item 3`}
      </Markdown>
    )
    expect(screen.getByText("Item 1")).toBeInTheDocument()
    expect(screen.getByText("Item 2")).toBeInTheDocument()
    expect(screen.getByText("Item 3")).toBeInTheDocument()
  })

  it("renders bold and italic text", () => {
    render(<Markdown>{`**Bold text** and *italic text*`}</Markdown>)
    expect(screen.getByText(/Bold text/)).toBeInTheDocument()
    expect(screen.getByText(/italic text/)).toBeInTheDocument()
  })

  it("renders code blocks", () => {
    render(
      <Markdown>
        {`Inline \`code\` and:

\`\`\`javascript
const x = 42;
\`\`\``}
      </Markdown>
    )
    expect(screen.getByText(/Inline/)).toBeInTheDocument()
    expect(screen.getByText(/code/)).toBeInTheDocument()
    expect(screen.getByText(/const x = 42;/)).toBeInTheDocument()
  })

  it("renders tables (GitHub-flavored markdown)", () => {
    render(
      <Markdown>
        {`| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |`}
      </Markdown>
    )
    expect(screen.getByText("Header 1")).toBeInTheDocument()
    expect(screen.getByText("Header 2")).toBeInTheDocument()
    expect(screen.getByText("Cell 1")).toBeInTheDocument()
    expect(screen.getByText("Cell 4")).toBeInTheDocument()
  })

  it("renders strikethrough text (GitHub-flavored markdown)", () => {
    render(<Markdown>{`~~Strikethrough text~~`}</Markdown>)
    expect(screen.getByText("Strikethrough text")).toBeInTheDocument()
  })

  it("renders task lists (GitHub-flavored markdown)", () => {
    render(
      <Markdown>
        {`- [x] Completed task
- [ ] Incomplete task`}
      </Markdown>
    )
    expect(screen.getByText("Completed task")).toBeInTheDocument()
    expect(screen.getByText("Incomplete task")).toBeInTheDocument()

    const checkboxes = screen.getAllByRole("checkbox")
    expect(checkboxes).toHaveLength(2)
    expect(checkboxes[0]).toBeChecked()
    expect(checkboxes[0]).toBeDisabled()
    expect(checkboxes[1]).not.toBeChecked()
    expect(checkboxes[1]).toBeDisabled()
  })

  it("preserves newlines and whitespace", () => {
    render(
      <Markdown>
        {`Line 1

Line 2 with space after newline

Line 3`}
      </Markdown>
    )
    expect(screen.getByText(/Line 1/)).toBeInTheDocument()
    expect(screen.getByText(/Line 2 with space after newline/)).toBeInTheDocument()
    expect(screen.getByText(/Line 3/)).toBeInTheDocument()
  })

  it("renders links correctly", () => {
    render(<Markdown>{`[Link text](https://example.com)`}</Markdown>)
    const link = screen.getByRole("link", { name: "Link text" })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute("href", "https://example.com")
  })

  it("renders blockquotes", () => {
    render(<Markdown>{`> This is a quote`}</Markdown>)
    expect(screen.getByText("This is a quote")).toBeInTheDocument()
  })
})
