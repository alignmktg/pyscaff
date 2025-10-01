"use client"

import Link from "next/link"
import { Run, RunStatus } from "@/lib/types"
import { Card, CardContent } from "@/components/ui/card"
import { StatusBadge } from "./status-badge"
import { Calendar, Activity, GitBranch } from "lucide-react"
import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

interface RunListProps {
  runs: Run[]
}

export function RunList({ runs }: RunListProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<RunStatus | "all">("all")

  const filteredRuns = runs.filter((run) => {
    const matchesSearch = run.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      run.workflow_id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || run.status === statusFilter

    return matchesSearch && matchesStatus
  })

  const statusOptions: Array<RunStatus | "all"> = [
    "all",
    "queued",
    "running",
    "waiting",
    "completed",
    "failed",
    "canceled",
  ]

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Input
          placeholder="Search by run ID or workflow ID..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="sm:max-w-xs"
        />
        <div className="flex gap-2 overflow-x-auto pb-2">
          {statusOptions.map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? "default" : "outline"}
              size="sm"
              onClick={() => setStatusFilter(status)}
              className="whitespace-nowrap"
            >
              {status === "all" ? "All" : status.charAt(0).toUpperCase() + status.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Run List */}
      {filteredRuns.length === 0 ? (
        <div className="rounded-lg border border-dashed p-8 text-center">
          <p className="text-sm text-muted-foreground">
            No runs found matching your filters.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredRuns.map((run) => (
            <Link key={run.id} href={`/runs/${run.id}`}>
              <Card className="transition-all hover:border-primary hover:shadow-md">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-mono text-sm font-semibold">{run.id}</h3>
                        <StatusBadge status={run.status} />
                      </div>

                      <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <GitBranch className="h-3 w-3" />
                          <span className="font-mono">{run.workflow_id}</span>
                          <span className="text-muted-foreground/60">v{run.workflow_version}</span>
                        </div>

                        {run.current_step && (
                          <div className="flex items-center gap-1">
                            <Activity className="h-3 w-3" />
                            <span>{run.current_step}</span>
                          </div>
                        )}

                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          <span>
                            Started {new Date(run.started_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
