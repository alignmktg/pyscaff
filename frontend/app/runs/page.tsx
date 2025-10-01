"use client"

import { useRuns } from "@/lib/hooks/useRuns"
import { RunList } from "@/components/run/run-list"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/empty-state"
import { AlertCircle } from "lucide-react"

export default function RunsPage() {
  const { data, isLoading, error } = useRuns()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workflow Runs</h1>
          <p className="text-muted-foreground">
            Monitor and manage workflow execution history
          </p>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
          <div>
            <p className="font-semibold text-destructive">Error loading runs</p>
            <p className="text-sm text-destructive/80 mt-1">
              {(error as Error).message}
            </p>
          </div>
        </div>
      )}

      {data && data.runs.length === 0 && (
        <EmptyState
          title="No workflow runs yet"
          description="Workflow runs will appear here once you start executing workflows. Each run represents a single execution instance of a workflow."
          actionLabel="View Workflows"
          actionHref="/workflows"
        />
      )}

      {data && data.runs.length > 0 && <RunList runs={data.runs} />}
    </div>
  )
}
