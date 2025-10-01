"use client"

import { Run } from "@/lib/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { StatusBadge } from "./status-badge"
import { Badge } from "@/components/ui/badge"
import {
  Calendar,
  GitBranch,
  Activity,
  RefreshCw,
  XCircle,
  Clock,
  CheckCircle2,
} from "lucide-react"
import Link from "next/link"

interface RunDetailProps {
  run: Run
  onResume?: () => void
  onCancel?: () => void
  isResuming?: boolean
  isCanceling?: boolean
}

export function RunDetail({
  run,
  onResume,
  onCancel,
  isResuming = false,
  isCanceling = false,
}: RunDetailProps) {
  const formatDuration = (start: string, end: string) => {
    const durationMs = new Date(end).getTime() - new Date(start).getTime()
    const seconds = Math.floor(durationMs / 1000)

    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }

  const duration = run.status === "completed" || run.status === "failed" || run.status === "canceled"
    ? formatDuration(run.started_at, run.updated_at)
    : null

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <CardTitle className="font-mono text-2xl">{run.id}</CardTitle>
              <StatusBadge status={run.status} />
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <GitBranch className="h-4 w-4" />
                <Link
                  href={`/workflows/${run.workflow_id}`}
                  className="font-mono hover:text-primary transition-colors"
                >
                  {run.workflow_id}
                </Link>
                <Badge variant="outline" className="text-xs">
                  v{run.workflow_version}
                </Badge>
              </div>

              {run.current_step && (
                <div className="flex items-center gap-1.5">
                  <Activity className="h-4 w-4" />
                  <span className="font-medium">Current step:</span>
                  <span className="font-mono">{run.current_step}</span>
                </div>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-2">
            {run.status === "waiting" && onResume && (
              <Button
                onClick={onResume}
                disabled={isResuming}
                size="sm"
              >
                {isResuming ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Resuming...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Resume
                  </>
                )}
              </Button>
            )}

            {(run.status === "running" || run.status === "waiting") && onCancel && (
              <Button
                onClick={onCancel}
                disabled={isCanceling}
                variant="destructive"
                size="sm"
              >
                {isCanceling ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Canceling...
                  </>
                ) : (
                  <>
                    <XCircle className="mr-2 h-4 w-4" />
                    Cancel
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Metadata Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              Started
            </div>
            <p className="text-sm font-medium">
              {new Date(run.started_at).toLocaleString()}
            </p>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              Updated
            </div>
            <p className="text-sm font-medium">
              {new Date(run.updated_at).toLocaleString()}
            </p>
          </div>

          {duration && (
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                Duration
              </div>
              <p className="text-sm font-medium">{duration}</p>
            </div>
          )}

          {run.status === "completed" && (
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <CheckCircle2 className="h-3 w-3" />
                Result
              </div>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                Success
              </Badge>
            </div>
          )}
        </div>

        {/* Idempotency Key */}
        {run.idempotency_key && (
          <div className="rounded-lg border bg-muted/50 p-3">
            <div className="text-xs text-muted-foreground mb-1">Idempotency Key</div>
            <code className="text-xs font-mono">{run.idempotency_key}</code>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
