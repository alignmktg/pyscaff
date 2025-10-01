import Link from "next/link"
import { Workflow } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Calendar, Layers } from "lucide-react"

interface WorkflowCardProps {
  workflow: Workflow
}

export function WorkflowCard({ workflow }: WorkflowCardProps) {
  const stepCount = workflow.steps.length
  const updatedDate = workflow.updated_at
    ? new Date(workflow.updated_at).toLocaleDateString()
    : "Unknown"

  return (
    <Link href={`/workflows/${workflow.id}`}>
      <Card className="transition-all hover:border-primary hover:shadow-md">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="text-xl">{workflow.name}</CardTitle>
              <CardDescription>
                Version {workflow.version}
              </CardDescription>
            </div>
            <Badge variant="outline" className="ml-2">
              v{workflow.version}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Layers className="h-4 w-4" />
              <span>{stepCount} steps</span>
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              <span>Updated {updatedDate}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
