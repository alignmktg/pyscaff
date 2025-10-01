import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { DynamicForm } from "@/components/form/dynamic-form"
import type { FormField } from "@/lib/schemas/field-to-zod"

// Mock the useResumeRun hook
vi.mock("@/lib/hooks/use-resume-run", () => ({
  useResumeRun: () => ({
    mutateAsync: vi.fn().mockResolvedValue({ id: "run_123", status: "completed" }),
    isPending: false,
    error: null,
  }),
}))

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
  Wrapper.displayName = "QueryClientWrapper"
  return Wrapper
}

describe("DynamicForm", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("should render text field", () => {
    const fields: FormField[] = [
      { key: "name", type: "text", label: "Name", required: true },
    ]

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    expect(screen.getByLabelText(/Name/)).toBeInTheDocument()
  })

  it("should render email field", () => {
    const fields: FormField[] = [
      { key: "email", type: "email", label: "Email", required: true },
    ]

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    expect(screen.getByLabelText(/Email/)).toBeInTheDocument()
  })

  it("should render multiple fields", () => {
    const fields: FormField[] = [
      { key: "name", type: "text", label: "Name", required: true },
      { key: "email", type: "email", label: "Email", required: true },
      { key: "age", type: "number", label: "Age", required: true },
    ]

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    expect(screen.getByLabelText(/Name/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Email/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Age/)).toBeInTheDocument()
  })

  it("should show required indicator", () => {
    const fields: FormField[] = [
      { key: "name", type: "text", label: "Name", required: true },
    ]

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    // Check for asterisk
    expect(screen.getByText("*")).toBeInTheDocument()
  })

  it("should show field description", () => {
    const fields: FormField[] = [
      {
        key: "name",
        type: "text",
        label: "Name",
        description: "Enter your full name",
      },
    ]

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    expect(screen.getByText("Enter your full name")).toBeInTheDocument()
  })

  it("should show validation error for required field", async () => {
    const user = userEvent.setup()
    const fields: FormField[] = [
      { key: "name", type: "text", label: "Name", required: true },
    ]

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    const submitButton = screen.getByRole("button", { name: /Submit/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/Name is required/)).toBeInTheDocument()
    })
  })

  it("should show validation error for invalid email", async () => {
    const user = userEvent.setup()
    const fields: FormField[] = [
      { key: "email", type: "email", label: "Email", required: true },
    ]

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    const emailInput = screen.getByLabelText(/Email/)
    await user.type(emailInput, "invalid-email")

    const submitButton = screen.getByRole("button", { name: /Submit/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/must be a valid email/)).toBeInTheDocument()
    })
  })

  it("should disable submit button during submission", async () => {
    const fields: FormField[] = [
      { key: "name", type: "text", label: "Name", required: true },
    ]

    const { useResumeRun } = await import("@/lib/hooks/use-resume-run")
    vi.mocked(useResumeRun).mockReturnValue({
      mutateAsync: vi.fn().mockImplementation(() => new Promise(() => {})), // Never resolves
      isPending: true,
      error: null,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any)

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    const submitButton = screen.getByRole("button")
    expect(submitButton).toBeDisabled()
    expect(screen.getByText("Submitting...")).toBeInTheDocument()
  })

  it("should call onSuccess when form is submitted successfully", async () => {
    const user = userEvent.setup()
    const onSuccess = vi.fn()
    const fields: FormField[] = [
      { key: "name", type: "text", label: "Name", required: true },
    ]

    render(
      <DynamicForm runId="run_123" fields={fields} onSuccess={onSuccess} />,
      { wrapper: createWrapper() }
    )

    const nameInput = screen.getByLabelText(/Name/)
    await user.type(nameInput, "John Doe")

    const submitButton = screen.getByRole("button", { name: /Submit/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled()
    })
  })

  it("should call onError when form submission fails", async () => {
    const user = userEvent.setup()
    const onError = vi.fn()
    const fields: FormField[] = [
      { key: "name", type: "text", label: "Name", required: true },
    ]

    const { useResumeRun } = await import("@/lib/hooks/use-resume-run")
    const mockError = new Error("Network error")
    vi.mocked(useResumeRun).mockReturnValue({
      mutateAsync: vi.fn().mockRejectedValue(mockError),
      isPending: false,
      error: null,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any)

    render(
      <DynamicForm runId="run_123" fields={fields} onError={onError} />,
      { wrapper: createWrapper() }
    )

    const nameInput = screen.getByLabelText(/Name/)
    await user.type(nameInput, "John Doe")

    const submitButton = screen.getByRole("button", { name: /Submit/ })
    await user.click(submitButton)

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(mockError)
    })
  })

  it("should display error alert when mutation fails", async () => {
    const fields: FormField[] = [
      { key: "name", type: "text", label: "Name", required: true },
    ]

    const { useResumeRun } = await import("@/lib/hooks/use-resume-run")
    vi.mocked(useResumeRun).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
      error: new Error("API error"),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any)

    render(
      <DynamicForm runId="run_123" fields={fields} />,
      { wrapper: createWrapper() }
    )

    expect(screen.getByText("API error")).toBeInTheDocument()
  })
})
