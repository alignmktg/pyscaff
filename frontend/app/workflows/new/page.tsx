"use client"

import { useState } from "react"
import { YamlEditor } from "@/components/yaml-editor"
import { WorkflowPreview } from "@/components/workflow-preview"
import { Button } from "@/components/ui/button"
import { Save, ArrowLeft } from "lucide-react"
import Link from "next/link"
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable"

const defaultYaml = `name: Blog Post Generator
start_step: collect_topic
steps:
  - id: collect_topic
    type: form
    name: Collect Topic
    next: generate_outline
    config:
      fields:
        - key: topic
          type: text
          required: true
        - key: audience
          type: select
          options:
            - developers
            - marketers

  - id: generate_outline
    type: ai_generate
    name: Generate Outline
    next: approval
    config:
      template_id: blog_outline
      variables:
        - topic
        - audience
      json_schema:
        type: object
        properties:
          sections:
            type: array
            items:
              type: string

  - id: approval
    type: approval
    name: Approve Outline
    next: null
    config:
      approvers:
        - editor@example.com
`

export default function NewWorkflowPage() {
  const [yamlContent, setYamlContent] = useState(defaultYaml)
  const [isValid, setIsValid] = useState<boolean>(true)

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b p-4">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Create Workflow</h1>
            <p className="text-sm text-muted-foreground">
              Define your AI workflow using YAML
            </p>
          </div>
        </div>
        <Button disabled className="gap-2">
          <Save className="h-4 w-4" />
          Save (Backend API pending)
        </Button>
      </div>

      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="horizontal">
          <ResizablePanel defaultSize={50} minSize={30}>
            <YamlEditor
              value={yamlContent}
              onChange={setYamlContent}
              onValidate={(valid) => setIsValid(valid)}
            />
          </ResizablePanel>

          <ResizableHandle withHandle />

          <ResizablePanel defaultSize={50} minSize={30}>
            <div className="flex h-full flex-col">
              <div className="border-b p-3">
                <h3 className="font-semibold">Workflow Preview</h3>
                {!isValid && (
                  <p className="text-xs text-muted-foreground">
                    Fix YAML errors to see preview
                  </p>
                )}
              </div>
              <div className="flex-1">
                <WorkflowPreview yamlContent={yamlContent} />
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  )
}
