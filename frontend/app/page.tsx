"use client"

import { useQuery } from "@tanstack/react-query"
import { workflowsApi } from "@/lib/api-client"
import { WorkflowCard } from "@/components/workflow-card"
import { WorkflowListSkeleton } from "@/components/workflow-list-skeleton"
import { EmptyState } from "@/components/empty-state"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import Link from "next/link"

export default function Home() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["workflows"],
    queryFn: workflowsApi.list,
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workflows</h1>
          <p className="text-muted-foreground">
            Manage and monitor your AI workflows
          </p>
        </div>
        <Link href="/workflows/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Workflow
          </Button>
        </Link>
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
          description="Get started by creating your first AI workflow. Define steps, add AI generation, and orchestrate complex processes with ease."
          actionLabel="Create your first workflow"
          actionHref="/workflows/new"
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
