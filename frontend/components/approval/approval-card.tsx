"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Markdown } from "@/components/ui/markdown"
import type { ApprovalDetails } from "@/lib/types"

interface ApprovalCardProps {
  approval: ApprovalDetails
}

export function ApprovalCard({ approval }: ApprovalCardProps) {
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{approval.workflow_name}</CardTitle>
          <Badge variant="outline" className="ml-2">
            {approval.status}
          </Badge>
        </div>
        <CardDescription>Step: {approval.step_name}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="text-sm font-medium mb-2">Context</h3>
          <div className="bg-muted rounded-md p-4 space-y-4">
            {Object.entries(approval.context_excerpt).map(([key, value]) => (
              <div key={key} className="space-y-1">
                <span className="text-sm font-medium capitalize">{key.replace(/_/g, " ")}</span>
                <div className="text-sm text-muted-foreground">
                  {typeof value === "string" && value.includes("\n") ? (
                    // Render multi-line strings as markdown
                    <Markdown>{value}</Markdown>
                  ) : typeof value === "object" ? (
                    <pre className="text-xs overflow-x-auto">
                      {JSON.stringify(value, null, 2)}
                    </pre>
                  ) : (
                    <span>{String(value)}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
