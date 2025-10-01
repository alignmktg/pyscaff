"use client"

import { useState } from "react"
import Editor from "@monaco-editor/react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import yaml from "js-yaml"

interface YamlEditorProps {
  value: string
  onChange: (value: string) => void
  onValidate?: (isValid: boolean, error?: string) => void
}

export function YamlEditor({ value, onChange, onValidate }: YamlEditorProps) {
  const [validationError, setValidationError] = useState<string | null>(null)
  const [isValid, setIsValid] = useState<boolean | null>(null)

  const handleValidate = () => {
    try {
      yaml.load(value)
      setValidationError(null)
      setIsValid(true)
      onValidate?.(true)
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Invalid YAML syntax"
      setValidationError(errorMessage)
      setIsValid(false)
      onValidate?.(false, errorMessage)
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b p-3">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold">Workflow Definition</h3>
          {isValid === true && (
            <Badge variant="outline" className="gap-1">
              <CheckCircle2 className="h-3 w-3 text-emerald-500" />
              Valid YAML
            </Badge>
          )}
          {isValid === false && (
            <Badge variant="outline" className="gap-1">
              <AlertCircle className="h-3 w-3 text-destructive" />
              Invalid YAML
            </Badge>
          )}
        </div>
        <Button onClick={handleValidate} size="sm" variant="secondary">
          Validate
        </Button>
      </div>

      {validationError && (
        <div className="border-b bg-destructive/10 px-4 py-2">
          <p className="text-sm text-destructive">{validationError}</p>
        </div>
      )}

      <div className="flex-1">
        <Editor
          height="100%"
          language="yaml"
          theme="vs-dark"
          value={value}
          onChange={(val) => onChange(val || "")}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: "var(--font-geist-mono), monospace",
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            wordWrap: "on",
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  )
}
