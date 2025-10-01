"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { CheckCircle2, XCircle } from "lucide-react"

interface ApproveRejectFormProps {
  onSubmit: (decision: "approve" | "reject", comment?: string) => void
  isSubmitting?: boolean
}

export function ApproveRejectForm({ onSubmit, isSubmitting = false }: ApproveRejectFormProps) {
  const [comment, setComment] = useState("")

  const handleApprove = () => {
    onSubmit("approve", comment || undefined)
  }

  const handleReject = () => {
    onSubmit("reject", comment || undefined)
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="comment">Comment (optional)</Label>
        <Textarea
          id="comment"
          placeholder="Add a comment..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          disabled={isSubmitting}
          rows={3}
        />
      </div>
      <div className="flex gap-3">
        <Button
          onClick={handleApprove}
          disabled={isSubmitting}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white"
          size="lg"
        >
          <CheckCircle2 className="mr-2 h-5 w-5" />
          Approve
        </Button>
        <Button
          onClick={handleReject}
          disabled={isSubmitting}
          variant="destructive"
          className="flex-1"
          size="lg"
        >
          <XCircle className="mr-2 h-5 w-5" />
          Reject
        </Button>
      </div>
    </div>
  )
}
