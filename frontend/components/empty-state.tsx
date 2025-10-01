import { Button } from "@/components/ui/button"
import { FileText } from "lucide-react"
import Link from "next/link"

interface EmptyStateProps {
  title: string
  description: string
  actionLabel: string
  actionHref: string
}

export function EmptyState({
  title,
  description,
  actionLabel,
  actionHref,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-12 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-muted">
        <FileText className="h-10 w-10 text-muted-foreground" />
      </div>
      <h3 className="mt-6 text-xl font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground max-w-md">
        {description}
      </p>
      <Link href={actionHref} className="mt-6">
        <Button>{actionLabel}</Button>
      </Link>
    </div>
  )
}
