"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle2, XCircle } from "lucide-react"

interface ApprovalSuccessProps {
  decision: "approve" | "reject"
  message?: string
}

export function ApprovalSuccess({ decision, message }: ApprovalSuccessProps) {
  const isApproved = decision === "approve"

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {isApproved ? (
            <>
              <CheckCircle2 className="h-6 w-6 text-green-600" />
              Approval Submitted
            </>
          ) : (
            <>
              <XCircle className="h-6 w-6 text-red-600" />
              Rejection Submitted
            </>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-muted-foreground">
          {message ||
            `Your ${decision === "approve" ? "approval" : "rejection"} has been recorded. You can close this page.`}
        </p>
      </CardContent>
    </Card>
  )
}
