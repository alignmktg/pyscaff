"use client"

import { useQuery } from "@tanstack/react-query"
import { workflowsApi } from "@/lib/api-client"
import { WorkflowCard } from "@/components/workflow-card"
import { WorkflowListSkeleton } from "@/components/workflow-list-skeleton"
import { EmptyState } from "@/components/empty-state"

export default function Home() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["workflows"],
    queryFn: workflowsApi.list,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Workflows</h1>
        <p className="text-muted-foreground">
          Manage and monitor your AI workflows
        </p>
      </div>

      {isLoading && <WorkflowListSkeleton />}

      {error && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-center">
          <p className="text-sm text-destructive">
            Error loading workflows: {(error as Error).message}
          </p>
        </div>
      )}

      {data && data.workflows.length === 0 && (
        <EmptyState
          title="No workflows yet"
          description="Create workflows by adding YAML files to the /workflows directory in your codebase. Define steps, add AI generation, and orchestrate complex processes."
        />
      )}

      {data && data.workflows.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data.workflows.map((workflow) => (
            <WorkflowCard key={workflow.id} workflow={workflow} />
          ))}
        </div>
      )}
    </div>
  )
}
