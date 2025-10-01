"use client"

import { useParams, useRouter } from "next/navigation"
import { useRun, useRunHistory, useRunContext, useCancelRun } from "@/lib/hooks/useRuns"
import { RunDetail } from "@/components/run/run-detail"
import { RunTimeline } from "@/components/run/run-timeline"
import { ContextExplorer } from "@/components/run/context-explorer"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { AlertCircle, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"

export default function RunDetailPage() {
  const params = useParams()
  const router = useRouter()
  const runId = params.id as string

  const { data: run, isLoading: isLoadingRun, error: runError } = useRun(runId)
  const { data: history, isLoading: isLoadingHistory } = useRunHistory(runId)
  const { data: context, isLoading: isLoadingContext } = useRunContext(runId)
  const cancelRun = useCancelRun()

  const handleCancel = async () => {
    try {
      await cancelRun.mutateAsync(runId)
    } catch (error) {
      console.error("Failed to cancel run:", error)
    }
  }

  const handleResume = () => {
    // Navigate to a resume form (not implemented in this WP)
    console.log("Resume functionality would be implemented here")
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <div>
        <Link href="/runs">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Runs
          </Button>
        </Link>
      </div>

      {/* Loading state */}
      {isLoadingRun && (
        <div className="space-y-6">
          <Skeleton className="h-64 w-full" />
          <div className="grid gap-6 lg:grid-cols-2">
            <Skeleton className="h-96 w-full" />
            <Skeleton className="h-96 w-full" />
          </div>
        </div>
      )}

      {/* Error state */}
      {runError && (
        <Card className="border-destructive">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
              <div>
                <p className="font-semibold text-destructive">Error loading run</p>
                <p className="text-sm text-destructive/80 mt-1">
                  {(runError as Error).message}
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-3"
                  onClick={() => router.push("/runs")}
                >
                  Back to Runs
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Run details */}
      {run && (
        <>
          <RunDetail
            run={run}
            onResume={handleResume}
            onCancel={handleCancel}
            isCanceling={cancelRun.isPending}
          />

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Timeline */}
            <div>
              {isLoadingHistory ? (
                <Skeleton className="h-96 w-full" />
              ) : (
                <RunTimeline steps={history?.steps || []} />
              )}
            </div>

            {/* Context */}
            <div>
              {isLoadingContext ? (
                <Skeleton className="h-96 w-full" />
              ) : (
                <ContextExplorer context={context || { static: {}, profile: {}, runtime: {} }} />
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
