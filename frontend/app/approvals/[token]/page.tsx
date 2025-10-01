"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { useApprovalDetails, useSubmitApproval } from "@/lib/hooks/use-approval"
import { ApprovalCard } from "@/components/approval/approval-card"
import { ApproveRejectForm } from "@/components/approval/approve-reject-form"
import { ApprovalSuccess } from "@/components/approval/approval-success"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function ApprovalPage() {
  const params = useParams()
  const token = params.token as string
  const [submitted, setSubmitted] = useState(false)
  const [submittedDecision, setSubmittedDecision] = useState<"approve" | "reject" | null>(null)

  const { data: approval, isLoading, error } = useApprovalDetails(token)
  const submitMutation = useSubmitApproval(token)

  const handleSubmit = async (decision: "approve" | "reject", comment?: string) => {
    try {
      await submitMutation.mutateAsync({ decision, comment })
      setSubmitted(true)
      setSubmittedDecision(decision)
    } catch (err) {
      console.error("Failed to submit approval:", err)
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/20 p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32 mt-2" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-10 w-full" />
            <div className="flex gap-3">
              <Skeleton className="h-12 flex-1" />
              <Skeleton className="h-12 flex-1" />
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Error state - 404 or expired token
  if (error) {
    const errorResponse = error as { message?: string }
    const is410 = errorResponse.message?.includes("410")

    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/20 p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-6 w-6 text-destructive" />
              {is410 ? "Already Processed" : "Invalid Token"}
            </CardTitle>
            <CardDescription>
              {is410
                ? "This approval has already been submitted."
                : "The approval link is invalid or has expired."}
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  // No approval data
  if (!approval) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/20 p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-6 w-6 text-destructive" />
              Approval Not Found
            </CardTitle>
            <CardDescription>
              Unable to load approval details. Please check your link and try again.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  // Success state
  if (submitted && submittedDecision) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/20 p-4">
        <ApprovalSuccess decision={submittedDecision} />
      </div>
    )
  }

  // Active approval state
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/20 p-4">
      <div className="w-full max-w-2xl space-y-6">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold mb-2">Approval Request</h1>
          <p className="text-muted-foreground">
            Review the details below and submit your decision
          </p>
        </div>

        <ApprovalCard approval={approval} />

        <Card>
          <CardHeader>
            <CardTitle>Your Decision</CardTitle>
            <CardDescription>
              Approve or reject this workflow step. Optionally add a comment to explain your
              decision.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {submitMutation.isError && (
              <Alert variant="destructive" className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>
                  Failed to submit approval. Please try again.
                </AlertDescription>
              </Alert>
            )}
            <ApproveRejectForm onSubmit={handleSubmit} isSubmitting={submitMutation.isPending} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
