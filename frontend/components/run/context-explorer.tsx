"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useState } from "react"
import { ChevronDown, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

interface ContextExplorerProps {
  context: {
    static?: Record<string, unknown>
    profile?: Record<string, unknown>
    runtime?: Record<string, unknown>
  }
}

interface JsonNodeProps {
  data: unknown
  name?: string
  depth?: number
}

function JsonNode({ data, name, depth = 0 }: JsonNodeProps) {
  const [isExpanded, setIsExpanded] = useState(depth < 2)

  if (data === null) {
    return (
      <div className="flex items-center gap-2">
        {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
        <span className="text-gray-500">null</span>
      </div>
    )
  }

  if (data === undefined) {
    return (
      <div className="flex items-center gap-2">
        {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
        <span className="text-gray-500">undefined</span>
      </div>
    )
  }

  if (typeof data === "boolean") {
    return (
      <div className="flex items-center gap-2">
        {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
        <span className="text-orange-600 dark:text-orange-400">{data.toString()}</span>
      </div>
    )
  }

  if (typeof data === "number") {
    return (
      <div className="flex items-center gap-2">
        {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
        <span className="text-green-600 dark:text-green-400">{data}</span>
      </div>
    )
  }

  if (typeof data === "string") {
    return (
      <div className="flex items-center gap-2">
        {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
        <span className="text-red-600 dark:text-red-400">&quot;{data}&quot;</span>
      </div>
    )
  }

  if (Array.isArray(data)) {
    if (data.length === 0) {
      return (
        <div className="flex items-center gap-2">
          {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
          <span className="text-gray-500">[]</span>
        </div>
      )
    }

    return (
      <div>
        <div
          className="flex items-center gap-1 cursor-pointer hover:bg-accent/50 rounded px-1 -mx-1"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <ChevronDown className="h-3 w-3 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-3 w-3 text-muted-foreground" />
          )}
          {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
          <span className="text-gray-500 text-xs">Array[{data.length}]</span>
        </div>
        {isExpanded && (
          <div className="ml-4 border-l border-border pl-3 mt-1 space-y-1">
            {data.map((item, index) => (
              <JsonNode key={index} data={item} name={`[${index}]`} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    )
  }

  if (typeof data === "object") {
    const entries = Object.entries(data)

    if (entries.length === 0) {
      return (
        <div className="flex items-center gap-2">
          {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
          <span className="text-gray-500">{"{}"}</span>
        </div>
      )
    }

    return (
      <div>
        <div
          className={cn(
            "flex items-center gap-1 rounded px-1 -mx-1",
            depth > 0 && "cursor-pointer hover:bg-accent/50"
          )}
          onClick={() => depth > 0 && setIsExpanded(!isExpanded)}
        >
          {depth > 0 && (
            isExpanded ? (
              <ChevronDown className="h-3 w-3 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-3 w-3 text-muted-foreground" />
            )
          )}
          {name && <span className="text-blue-600 dark:text-blue-400 font-medium">{name}</span>}
          {!isExpanded && depth > 0 && (
            <span className="text-gray-500 text-xs">{"{...}"}</span>
          )}
        </div>
        {isExpanded && (
          <div className={cn("ml-4 space-y-1", depth > 0 && "border-l border-border pl-3 mt-1")}>
            {entries.map(([key, value]) => (
              <JsonNode key={key} data={value} name={key} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      {name && <span className="text-blue-600 dark:text-blue-400">{name}:</span>}
      <span className="text-gray-500">{String(data)}</span>
    </div>
  )
}

export function ContextExplorer({ context }: ContextExplorerProps) {
  const sections = [
    { key: "static", label: "Static", data: context.static },
    { key: "profile", label: "Profile", data: context.profile },
    { key: "runtime", label: "Runtime", data: context.runtime },
  ]

  const hasData = sections.some(
    (section) => section.data && Object.keys(section.data).length > 0
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Context Data</CardTitle>
      </CardHeader>
      <CardContent>
        {!hasData ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            No context data available
          </p>
        ) : (
          <div className="space-y-6">
            {sections.map((section) => {
              const hasContent = section.data && Object.keys(section.data).length > 0

              if (!hasContent) return null

              return (
                <div key={section.key} className="space-y-2">
                  <div className="flex items-center gap-2 pb-2 border-b">
                    <h4 className="text-sm font-semibold">{section.label}</h4>
                    <Badge variant="outline" className="text-xs">
                      {Object.keys(section.data!).length} keys
                    </Badge>
                  </div>
                  <div className="font-mono text-xs">
                    <JsonNode data={section.data} depth={0} />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
