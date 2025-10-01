import { Badge } from "@/components/ui/badge"
import { RunStatus } from "@/lib/types"
import { cn } from "@/lib/utils"

interface StatusBadgeProps {
  status: RunStatus
  className?: string
}

const statusConfig = {
  queued: {
    label: "Queued",
    className: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 border-blue-200",
  },
  running: {
    label: "Running",
    className: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 border-yellow-200",
  },
  waiting: {
    label: "Waiting",
    className: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 border-orange-200",
  },
  completed: {
    label: "Completed",
    className: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-200",
  },
  failed: {
    label: "Failed",
    className: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border-red-200",
  },
  canceled: {
    label: "Canceled",
    className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200 border-gray-200",
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <Badge variant="outline" className={cn(config.className, className)}>
      {config.label}
    </Badge>
  )
}
