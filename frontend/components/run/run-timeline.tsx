"use client"

import { RunStep } from "@/lib/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  CheckCircle2,
  Circle,
  AlertCircle,
  Clock,
  ChevronRight
} from "lucide-react"
import { cn } from "@/lib/utils"

interface RunTimelineProps {
  steps: RunStep[]
}

const stepTypeIcons = {
  form: "📝",
  ai_generate: "🤖",
  conditional: "🔀",
  api_call: "🌐",
  approval: "✅",
}

const statusIcons = {
  pending: <Circle className="h-5 w-5 text-gray-400" />,
  running: <Clock className="h-5 w-5 text-yellow-500 animate-pulse" />,
  completed: <CheckCircle2 className="h-5 w-5 text-green-500" />,
  failed: <AlertCircle className="h-5 w-5 text-red-500" />,
}

export function RunTimeline({ steps }: RunTimelineProps) {
  if (steps.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Execution Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No steps executed yet
          </p>
        </CardContent>
      </Card>
    )
  }

  const formatDuration = (start: string, end?: string) => {
    if (!end) return "In progress..."

    const durationMs = new Date(end).getTime() - new Date(start).getTime()
    const seconds = Math.floor(durationMs / 1000)

    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Execution Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={step.id} className="relative">
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="absolute left-[10px] top-[28px] w-0.5 h-[calc(100%+16px)] bg-border" />
              )}

              <div className="flex gap-3">
                {/* Status icon */}
                <div className="relative z-10 mt-0.5">
                  {statusIcons[step.status]}
                </div>

                {/* Step content */}
                <div className="flex-1 pb-4">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{stepTypeIcons[step.type as keyof typeof stepTypeIcons]}</span>
                      <h4 className="font-semibold text-sm">{step.step_id}</h4>
                      <Badge variant="outline" className="text-xs">
                        {step.type}
                      </Badge>
                    </div>
                    <Badge
                      variant="outline"
                      className={cn(
                        "text-xs",
                        step.status === "completed" && "bg-green-50 text-green-700 border-green-200",
                        step.status === "running" && "bg-yellow-50 text-yellow-700 border-yellow-200",
                        step.status === "failed" && "bg-red-50 text-red-700 border-red-200",
                        step.status === "pending" && "bg-gray-50 text-gray-700 border-gray-200"
                      )}
                    >
                      {step.status}
                    </Badge>
                  </div>

                  {/* Timestamps */}
                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>Started: {new Date(step.started_at).toLocaleString()}</div>
                    {step.ended_at && (
                      <div>Ended: {new Date(step.ended_at).toLocaleString()}</div>
                    )}
                    <div className="font-medium">
                      Duration: {formatDuration(step.started_at, step.ended_at)}
                    </div>
                  </div>

                  {/* Output or Error */}
                  {step.output && (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-xs text-primary font-medium flex items-center gap-1">
                        <ChevronRight className="h-3 w-3" />
                        View Output
                      </summary>
                      <pre className="mt-2 text-xs bg-muted p-3 rounded-md overflow-x-auto">
                        {JSON.stringify(step.output, null, 2)}
                      </pre>
                    </details>
                  )}

                  {step.error && (
                    <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-md">
                      <p className="text-xs text-red-800 dark:text-red-200 font-mono">
                        {step.error}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
