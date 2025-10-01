import { render, screen, fireEvent } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { describe, it, expect, beforeEach, vi } from "vitest"
import { ApprovalCard } from "@/components/approval/approval-card"
import { ApproveRejectForm } from "@/components/approval/approve-reject-form"
import { ApprovalSuccess } from "@/components/approval/approval-success"
import type { ApprovalDetails } from "@/lib/types"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
})

function Wrapper({ children }: { children: React.ReactNode }) {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}

describe("Approval Components", () => {
  const mockApproval: ApprovalDetails = {
    run_id: "run-1",
    workflow_id: "wf-1",
    workflow_name: "Lead Qualification",
    step_id: "approval_step",
    step_name: "Sales Manager Approval",
    context_excerpt: {
      lead_name: "Acme Corp",
      score: 85,
      source: "Inbound",
    },
    status: "pending",
  }

  beforeEach(() => {
    queryClient.clear()
  })

  describe("ApprovalCard", () => {
    it("renders approval details correctly", () => {
      render(<ApprovalCard approval={mockApproval} />, { wrapper: Wrapper })

      expect(screen.getByText("Lead Qualification")).toBeInTheDocument()
      expect(screen.getByText("Step: Sales Manager Approval")).toBeInTheDocument()
      expect(screen.getByText("pending")).toBeInTheDocument()
      expect(screen.getByText(/Acme Corp/i)).toBeInTheDocument()
      expect(screen.getByText(/85/i)).toBeInTheDocument()
      expect(screen.getByText(/Inbound/i)).toBeInTheDocument()
    })

    it("displays context excerpt as key-value pairs", () => {
      render(<ApprovalCard approval={mockApproval} />, { wrapper: Wrapper })

      expect(screen.getByText(/lead name/i)).toBeInTheDocument()
      expect(screen.getByText(/score/i)).toBeInTheDocument()
      expect(screen.getByText(/source/i)).toBeInTheDocument()
    })
  })

  describe("ApproveRejectForm", () => {
    it("renders approve and reject buttons", () => {
      const onSubmit = vi.fn()
      render(<ApproveRejectForm onSubmit={onSubmit} />, { wrapper: Wrapper })

      expect(screen.getByRole("button", { name: /approve/i })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /reject/i })).toBeInTheDocument()
    })

    it("calls onSubmit with approve decision when approve is clicked", () => {
      const onSubmit = vi.fn()
      render(<ApproveRejectForm onSubmit={onSubmit} />, { wrapper: Wrapper })

      fireEvent.click(screen.getByRole("button", { name: /approve/i }))

      expect(onSubmit).toHaveBeenCalledWith("approve", undefined)
    })

    it("calls onSubmit with reject decision when reject is clicked", () => {
      const onSubmit = vi.fn()
      render(<ApproveRejectForm onSubmit={onSubmit} />, { wrapper: Wrapper })

      fireEvent.click(screen.getByRole("button", { name: /reject/i }))

      expect(onSubmit).toHaveBeenCalledWith("reject", undefined)
    })

    it("includes comment when provided", () => {
      const onSubmit = vi.fn()
      render(<ApproveRejectForm onSubmit={onSubmit} />, { wrapper: Wrapper })

      const textarea = screen.getByPlaceholderText(/add a comment/i)
      fireEvent.change(textarea, { target: { value: "LGTM" } })
      fireEvent.click(screen.getByRole("button", { name: /approve/i }))

      expect(onSubmit).toHaveBeenCalledWith("approve", "LGTM")
    })

    it("disables buttons when isSubmitting is true", () => {
      const onSubmit = vi.fn()
      render(<ApproveRejectForm onSubmit={onSubmit} isSubmitting={true} />, { wrapper: Wrapper })

      expect(screen.getByRole("button", { name: /approve/i })).toBeDisabled()
      expect(screen.getByRole("button", { name: /reject/i })).toBeDisabled()
    })
  })

  describe("ApprovalSuccess", () => {
    it("renders success message for approval", () => {
      render(<ApprovalSuccess decision="approve" />, { wrapper: Wrapper })

      expect(screen.getByText(/approval submitted/i)).toBeInTheDocument()
      expect(screen.getByText(/approval has been recorded/i)).toBeInTheDocument()
    })

    it("renders success message for rejection", () => {
      render(<ApprovalSuccess decision="reject" />, { wrapper: Wrapper })

      expect(screen.getByText(/rejection submitted/i)).toBeInTheDocument()
      expect(screen.getByText(/rejection has been recorded/i)).toBeInTheDocument()
    })

    it("displays custom message when provided", () => {
      render(<ApprovalSuccess decision="approve" message="Custom message" />, {
        wrapper: Wrapper,
      })

      expect(screen.getByText("Custom message")).toBeInTheDocument()
    })
  })
})
