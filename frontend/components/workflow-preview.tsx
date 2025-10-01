"use client"

import { useCallback, useEffect } from "react"
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Position,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import yaml from "js-yaml"
import { Badge } from "@/components/ui/badge"

interface WorkflowPreviewProps {
  yamlContent: string
}

interface WorkflowStep {
  id: string
  type: string
  name: string
  next?: string | null
}

interface WorkflowDefinition {
  name?: string
  start_step?: string
  steps?: WorkflowStep[]
}

export function WorkflowPreview({ yamlContent }: WorkflowPreviewProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const parseWorkflow = useCallback((yamlStr: string) => {
    try {
      const workflow = yaml.load(yamlStr) as WorkflowDefinition

      if (!workflow || !workflow.steps || !Array.isArray(workflow.steps)) {
        return { nodes: [], edges: [] }
      }

      // Create nodes in vertical layout
      const newNodes: Node[] = workflow.steps.map((step, index) => ({
        id: step.id,
        type: "default",
        position: { x: 250, y: index * 150 },
        data: {
          label: (
            <div className="flex flex-col gap-1 p-2">
              <div className="font-semibold">{step.name}</div>
              <Badge variant="secondary" className="w-fit text-xs">
                {step.type}
              </Badge>
            </div>
          ),
        },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
      }))

      // Create edges based on next field
      const newEdges: Edge[] = workflow.steps
        .filter((step) => step.next)
        .map((step) => ({
          id: `${step.id}-${step.next}`,
          source: step.id,
          target: step.next!,
          type: "smoothstep",
          animated: true,
        }))

      return { nodes: newNodes, edges: newEdges }
    } catch {
      return { nodes: [], edges: [] }
    }
  }, [])

  useEffect(() => {
    const { nodes: newNodes, edges: newEdges } = parseWorkflow(yamlContent)
    setNodes(newNodes)
    setEdges(newEdges)
  }, [yamlContent, parseWorkflow, setNodes, setEdges])

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        className="bg-background"
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}
