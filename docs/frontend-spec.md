# PyScaff Frontend Specification (MVID)

**Version**: 0.1.0
**Last Updated**: 2025-10-01
**Status**: Draft → Approved
**Related ADR**: ADR-007 (Frontend Architecture)

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Pages & Routes](#pages--routes)
5. [Core Components](#core-components)
6. [Design System](#design-system)
7. [API Integration](#api-integration)
8. [State Management](#state-management)
9. [Form Rendering](#form-rendering)
10. [Real-Time Updates](#real-time-updates)
11. [Error Handling](#error-handling)
12. [Testing Strategy](#testing-strategy)
13. [Deployment](#deployment)
14. [Work Packages](#work-packages)

---

## Overview

PyScaff frontend is a **Next.js 15 web application** that enables non-technical users to create, manage, and monitor AI-powered workflows. It provides:

- **Workflow Editor**: YAML-based workflow creation with live validation
- **Run Monitoring**: Real-time status updates and execution history
- **Interactive Forms**: Dynamic form rendering from step configurations
- **Approval Interface**: Email-triggered approval/rejection flow
- **Debugging Tools**: Context explorer, step history timeline

**Target Users**:
- Internal team (MVID): Product managers, operations, marketing
- Post-MVID: Business users who need AI automation without coding

---

## Tech Stack

See **ADR-007** for detailed rationale. Summary:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Next.js 15 (App Router) | Server Components, streaming, optimizations |
| **Language** | TypeScript | Type safety |
| **UI Components** | shadcn/ui + Radix | Accessible, customizable primitives |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Forms** | React Hook Form + Zod | Performant forms with validation |
| **State** | TanStack Query + Zustand | Server state + client state |
| **API Client** | openapi-typescript-codegen | Auto-generated from OpenAPI |
| **YAML Editor** | Monaco Editor | VS Code engine |
| **Visualization** | ReactFlow | Workflow DAG graphs |
| **Testing** | Vitest + Playwright + MSW | Unit + E2E + API mocking |
| **Deployment** | Vercel | Auto-deploy from Git |

---

## Project Structure

```
/frontend
  /app                          # Next.js App Router pages
    layout.tsx                  # Root layout (sidebar nav, theme)
    page.tsx                    # Dashboard
    /workflows
      page.tsx                  # Workflow list
      /new
        page.tsx                # Create workflow (YAML editor)
      /[id]
        page.tsx                # Workflow detail
        /edit
          page.tsx              # Edit workflow
    /runs
      page.tsx                  # Run list (filterable)
      /[id]
        page.tsx                # Run detail (status, history, context)
        /form
          page.tsx              # Form step renderer (dynamic)
    /approvals
      /[token]
        page.tsx                # Approval interface
  /components                   # Reusable components
    /ui                         # shadcn/ui components
      button.tsx
      card.tsx
      badge.tsx
      skeleton.tsx
      ...
    /workflow
      workflow-editor.tsx       # Monaco-based YAML editor
      workflow-graph.tsx        # ReactFlow visualization
      workflow-card.tsx         # Workflow list card
    /run
      run-timeline.tsx          # Execution history timeline
      run-status-badge.tsx      # Status indicator
      context-explorer.tsx      # JSON tree viewer
    /form
      dynamic-form.tsx          # Form renderer from config
      field-renderer.tsx        # Individual field components
    /common
      page-header.tsx
      empty-state.tsx
      error-boundary.tsx
  /lib
    /api                        # Auto-generated API client
      services/                 # WorkflowsService, ExecutionsService, etc.
      models/                   # TypeScript types from OpenAPI
    /utils
      cn.ts                     # Tailwind class merger
      format.ts                 # Date/time formatting
      yaml-validator.ts         # YAML validation helpers
    /hooks
      use-workflow.ts           # Workflow data hook
      use-run.ts                # Run data hook (with polling)
      use-run-history.ts        # Run history hook
    /schemas
      form-schema-generator.ts  # Step config → Zod schema
  /styles
    globals.css                 # Tailwind base + custom styles
  package.json
  tsconfig.json
  tailwind.config.ts
  next.config.js
  .env.local                    # Environment variables
```

---

## Pages & Routes

### 1. Dashboard (`/`)

**Purpose**: Landing page showing workflow overview

**Layout**:
```
┌─────────────────────────────────────────┐
│ [Logo] PyScaff         [Theme] [Profile]│
├──────┬──────────────────────────────────┤
│      │  Dashboard                       │
│ Nav  │  ┌─────────────┬─────────────┐   │
│      │  │ Create      │ View All    │   │
│ • Wo │  │ Workflow    │ Runs        │   │
│ • Ru │  └─────────────┴─────────────┘   │
│      │                                   │
│      │  Recent Workflows                │
│      │  ┌──────────────────────────┐    │
│      │  │ 📄 Blog Post Generator   │    │
│      │  │ 3 runs • Updated 2h ago  │    │
│      │  └──────────────────────────┘    │
│      │  ┌──────────────────────────┐    │
│      │  │ 📄 Customer Onboarding   │    │
│      │  │ 12 runs • Updated 1d ago │    │
│      │  └──────────────────────────┘    │
└──────┴──────────────────────────────────┘
```

**Components**:
- `WorkflowCard` - Shows workflow name, run count, last updated
- `CTACard` - "Create Workflow" and "View All Runs" buttons
- `EmptyState` - If no workflows exist

**API Calls**:
- `GET /v1/workflows` - Fetch workflow list
- Polling: None

**Actions**:
- Click "Create Workflow" → `/workflows/new`
- Click workflow card → `/workflows/:id`
- Click "View All Runs" → `/runs`

---

### 2. Workflow List (`/workflows`)

**Purpose**: Browse all workflows (filterable, searchable)

**Layout**:
```
┌───────────────────────────────────────────┐
│ Workflows                                 │
│ ┌─────────────┐ ┌──────────────────────┐ │
│ │ + New       │ │ [Search workflows]  │ │
│ └─────────────┘ └──────────────────────┘ │
│                                           │
│ ┌─────────────────────────────────────┐  │
│ │ Name             │ Runs │ Updated   │  │
│ ├──────────────────┼──────┼───────────┤  │
│ │ Blog Generator   │   3  │ 2h ago    │  │
│ │ Onboarding Flow  │  12  │ 1d ago    │  │
│ │ Lead Scoring     │   0  │ 3d ago    │  │
│ └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

**Components**:
- `WorkflowTable` - Data table with sorting
- `SearchBar` - Filter workflows by name
- `NewWorkflowButton` - CTA button

**API Calls**:
- `GET /v1/workflows` with search/filter params

---

### 3. Workflow Editor (`/workflows/new`, `/workflows/:id/edit`)

**Purpose**: Create/edit workflows via YAML editor

**Layout**:
```
┌─────────────────────────────────────────────┐
│ Create Workflow             [Save] [Cancel] │
├──────────────────┬──────────────────────────┤
│ YAML Editor      │ Preview                  │
│                  │                           │
│ 1 name: "Blog"   │  ┌──────┐                │
│ 2 start: form    │  │ Form │                │
│ 3 steps:         │  └──┬───┘                │
│ 4   - id: form   │     │                    │
│ 5     type: form │  ┌──▼────────┐           │
│ 6     fields:    │  │ AI Generate│          │
│ 7       - key:   │  └──┬────────┘           │
│                  │     │                    │
│ [✓ Valid]        │  ┌──▼────┐               │
│                  │  │Approval│               │
│                  │  └────────┘               │
└──────────────────┴──────────────────────────┘
```

**Components**:
- `WorkflowEditor` - Monaco editor with YAML syntax
- `WorkflowGraph` - ReactFlow preview (live updates)
- `ValidationPanel` - Show errors/warnings
- `SaveButton` - Validate + save to API

**Features**:
- **Live validation**: Validate on keystroke (debounced)
- **Autocomplete**: Suggest step types, fields
- **Schema enforcement**: Validate against JSON Schema
- **Unsaved changes warning**: Prompt before leaving page

**API Calls**:
- `POST /v1/workflows/validate` - Validate YAML (debounced)
- `POST /v1/workflows` - Save workflow (on submit)
- `PUT /v1/workflows/:id` - Update workflow (edit mode)

---

### 4. Workflow Detail (`/workflows/:id`)

**Purpose**: View workflow definition and associated runs

**Layout**:
```
┌─────────────────────────────────────────────┐
│ Blog Post Generator    [Edit] [Start Run]  │
├─────────────────────────────────────────────┤
│ Workflow Definition (YAML)                  │
│ ┌─────────────────────────────────────────┐ │
│ │ name: Blog Post Generator               │ │
│ │ start_step: collect_topic               │ │
│ │ steps:                                  │ │
│ │   - id: collect_topic                   │ │
│ │     type: form                          │ │
│ │     ...                                 │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Recent Runs                                 │
│ ┌─────────────────────────────────────────┐ │
│ │ run_789 • 🟢 Completed • 2h ago         │ │
│ │ run_788 • 🔴 Failed • 5h ago            │ │
│ │ run_787 • 🟡 Waiting • 1d ago           │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**Components**:
- `WorkflowDefinitionViewer` - Read-only YAML display (Monaco)
- `RunList` - Table of recent runs
- `StartRunModal` - Modal to input initial values

**API Calls**:
- `GET /v1/workflows/:id` - Fetch workflow
- `GET /v1/executions?workflow_id=:id` - Fetch runs

**Actions**:
- Click "Edit" → `/workflows/:id/edit`
- Click "Start Run" → Modal → `POST /v1/executions`
- Click run in list → `/runs/:runId`

---

### 5. Run List (`/runs`)

**Purpose**: Browse all workflow runs (filterable by status)

**Layout**:
```
┌───────────────────────────────────────────────┐
│ All Runs                                      │
│ ┌────────┬────────┬─────────┬────────┐       │
│ │ All    │Running │ Waiting │Complete│       │
│ └────────┴────────┴─────────┴────────┘       │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │ Run ID  │ Workflow      │ Status │ Time  │ │
│ ├─────────┼───────────────┼────────┼───────┤ │
│ │ run_789 │ Blog Gen      │🟢 Done │ 2h ago│ │
│ │ run_788 │ Onboarding    │🟡 Wait │ 5h ago│ │
│ │ run_787 │ Lead Score    │🔴 Fail │ 1d ago│ │
│ └───────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

**Components**:
- `RunTable` - Filterable data table
- `StatusFilterTabs` - Filter by status
- `RunStatusBadge` - Colored badge with icon

**API Calls**:
- `GET /v1/executions?status=:status` - Filtered runs

---

### 6. Run Detail (`/runs/:id`)

**Purpose**: Monitor run status, view history, debug failures

**Layout**:
```
┌─────────────────────────────────────────────┐
│ Run: run_789              🟡 Waiting         │
│ Workflow: Blog Post Generator               │
│ Started: 2h ago • Current: collect_topic    │
├─────────────────────────────────────────────┤
│ ┌─ Timeline ───────────────────────────────┐│
│ │ ✓ form (5s) → ✓ ai_generate (12s)       ││
│ │ → ⏸️ approval (waiting...)                ││
│ └─────────────────────────────────────────┘│
│                                             │
│ ┌─ Context ────────────────────────────────┐│
│ │ {                                        ││
│ │   "topic": "AI Workflows",               ││
│ │   "audience": "developers",              ││
│ │   "draft": "AI workflows are..."         ││
│ │ }                                        ││
│ └─────────────────────────────────────────┘│
│                                             │
│ [Resume with Input]                         │
└─────────────────────────────────────────────┘
```

**Components**:
- `RunStatusHeader` - Status badge, workflow name, timestamps
- `RunTimeline` - Vertical timeline of step execution
- `ContextExplorer` - JSON tree viewer (collapsible)
- `ResumeButton` - Shows if status = "waiting"

**API Calls**:
- `GET /v1/executions/:id` - Fetch run status (polling every 2s if running)
- `GET /v1/executions/:id/history` - Fetch step history
- `GET /v1/executions/:id/context` - Fetch context

**Polling Logic**:
```typescript
const { data: run } = useQuery({
  queryKey: ['run', runId],
  queryFn: () => ExecutionsService.getRun(runId),
  refetchInterval: run?.status === 'running' ? 2000 : false
})
```

---

### 7. Form Renderer (`/runs/:id/form` or inline)

**Purpose**: Render dynamic form from step config, submit to resume

**Layout**:
```
┌─────────────────────────────────────────┐
│ Blog Post Topic                         │
├─────────────────────────────────────────┤
│ Topic *                                 │
│ [________________________]              │
│                                         │
│ Audience *                              │
│ [developers ▼]                          │
│                                         │
│ [Cancel]              [Submit]          │
└─────────────────────────────────────────┘
```

**Components**:
- `DynamicForm` - Generates form from step config
- `FieldRenderer` - Maps field type → shadcn/ui component
- `SubmitButton` - Calls resume API

**Form Generation Logic**:
```typescript
// Step config
{
  type: "form",
  config: {
    fields: [
      { key: "topic", type: "text", required: true },
      { key: "audience", type: "select", options: ["dev", "marketing"] }
    ]
  }
}

// Generate Zod schema
const schema = z.object({
  topic: z.string().min(1, "Topic is required"),
  audience: z.enum(["dev", "marketing"])
})

// Render with React Hook Form
<Form {...form}>
  <Input name="topic" />
  <Select name="audience" />
  <Button type="submit">Submit</Button>
</Form>
```

**Field Type Mapping**:
| Step Config Type | shadcn Component | HTML Input Type |
|-----------------|------------------|-----------------|
| `text` | `<Input />` | `text` |
| `email` | `<Input />` | `email` |
| `number` | `<Input />` | `number` |
| `textarea` | `<Textarea />` | - |
| `select` | `<Select />` | - |
| `checkbox` | `<Checkbox />` | `checkbox` |
| `date` | `<DatePicker />` | `date` |

**API Calls**:
- `POST /v1/executions/:id/resume` - Submit form data

---

### 8. Approval Interface (`/approvals/:token`)

**Purpose**: Email-triggered approval/rejection

**Layout**:
```
┌─────────────────────────────────────────┐
│ Approval Required                       │
├─────────────────────────────────────────┤
│ Workflow: Blog Post Generator           │
│ Run: run_789                            │
│                                         │
│ Blog Draft Preview:                     │
│ ┌─────────────────────────────────────┐ │
│ │ Title: AI Workflows 101             │ │
│ │ Body: AI workflows are powerful...  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Comment (optional)                      │
│ [________________________]              │
│                                         │
│ [Reject]              [Approve]         │
└─────────────────────────────────────────┘
```

**Components**:
- `ApprovalHeader` - Workflow/run info
- `ApprovalPreview` - Show data awaiting approval
- `CommentField` - Optional comment textarea
- `ApprovalButtons` - Approve/Reject

**API Calls**:
- `GET /v1/executions/:id` - Fetch run data (from token)
- `POST /v1/executions/:id/resume` - Submit approval decision

**Email Template**:
```
Subject: Approval Required - Blog Post Generator

A workflow is waiting for your approval:

Workflow: Blog Post Generator
Run ID: run_789

[View Details & Approve]
[Reject]

---
Powered by PyScaff
```

---

## Core Components

### Workflow Components

#### `WorkflowEditor`
```typescript
interface WorkflowEditorProps {
  initialYaml?: string
  onSave: (yaml: string) => Promise<void>
  onValidate: (yaml: string) => Promise<ValidationResult>
}
```

**Features**:
- Monaco editor with YAML language support
- Live validation (debounced 500ms)
- Error highlighting (red squiggles)
- Autocomplete from JSON Schema
- Ctrl+S to save

#### `WorkflowGraph`
```typescript
interface WorkflowGraphProps {
  workflow: Workflow
  currentStepId?: string // Highlight during run
}
```

**Features**:
- ReactFlow visualization
- Vertical layout (top-to-bottom)
- Node types: form, ai_generate, conditional, api_call, approval
- Edge labels: "next" or "if_true/if_false"
- Highlight current step (blue border)

---

### Run Components

#### `RunTimeline`
```typescript
interface RunTimelineProps {
  history: RunStep[]
}
```

**Layout**:
```
✓ collect_topic (5s)
   └─> Completed at 10:00:00
✓ ai_generate (12s)
   └─> Completed at 10:00:05
⏸️ manager_approval (waiting...)
   └─> Started at 10:00:17
```

**Features**:
- Vertical timeline
- Icons: ✓ (completed), ⏸️ (waiting), ✗ (failed)
- Duration display
- Expandable details (output/error)

#### `ContextExplorer`
```typescript
interface ContextExplorerProps {
  context: Record<string, any>
}
```

**Features**:
- JSON tree viewer (react-json-view or custom)
- Collapsible sections
- Syntax highlighting
- Copy to clipboard

---

### Form Components

#### `DynamicForm`
```typescript
interface DynamicFormProps {
  fields: FormField[]
  onSubmit: (values: Record<string, any>) => Promise<void>
}

interface FormField {
  key: string
  type: 'text' | 'email' | 'number' | 'textarea' | 'select' | 'checkbox'
  required?: boolean
  pattern?: string
  options?: string[] // For select
}
```

**Implementation**:
```typescript
// Generate Zod schema from fields
const generateSchema = (fields: FormField[]) => {
  const shape: Record<string, z.ZodTypeAny> = {}

  fields.forEach(field => {
    if (field.type === 'text') {
      let schema = z.string()
      if (field.required) schema = schema.min(1)
      if (field.pattern) schema = schema.regex(new RegExp(field.pattern))
      shape[field.key] = schema
    }
    // ... other types
  })

  return z.object(shape)
}

// Use with React Hook Form
const form = useForm({
  resolver: zodResolver(generateSchema(fields))
})
```

---

## Design System

See **ADR-007** for full spec. Summary:

### Colors

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))"
        },
        // Status colors
        status: {
          queued: "hsl(var(--slate-400))",
          running: "hsl(var(--blue-500))",
          waiting: "hsl(var(--amber-500))",
          completed: "hsl(var(--emerald-500))",
          failed: "hsl(var(--red-500))",
          canceled: "hsl(var(--slate-500))"
        }
      }
    }
  }
}
```

### Typography

```css
/* globals.css */
@layer base {
  :root {
    --font-sans: 'Geist Sans', 'Inter', sans-serif;
    --font-mono: 'Geist Mono', 'JetBrains Mono', monospace;
  }

  body {
    @apply font-sans;
  }

  code, pre, .yaml, .json {
    @apply font-mono;
  }
}
```

### Component Variants

```typescript
// Example: Button variants
<Button variant="default">Primary Action</Button>
<Button variant="outline">Secondary</Button>
<Button variant="ghost">Subtle</Button>
<Button variant="destructive">Delete</Button>
```

---

## API Integration

### Auto-Generated Client

```bash
# Generate client from backend OpenAPI spec
npx openapi-typescript-codegen \
  --input http://localhost:8000/openapi.json \
  --output ./lib/api \
  --client fetch
```

**Generated Structure**:
```
/lib/api
  /services
    WorkflowsService.ts       # Workflow CRUD
    ExecutionsService.ts      # Run CRUD + resume
    StateService.ts           # History + context
  /models
    Workflow.ts
    Run.ts
    Step.ts
  index.ts
```

### Usage with React Query

```typescript
// hooks/use-workflow.ts
export function useWorkflow(id: string) {
  return useQuery({
    queryKey: ['workflow', id],
    queryFn: () => WorkflowsService.getWorkflow({ id })
  })
}

// hooks/use-run.ts (with polling)
export function useRun(id: string) {
  return useQuery({
    queryKey: ['run', id],
    queryFn: () => ExecutionsService.getRun({ id }),
    refetchInterval: (data) =>
      data?.status === 'running' ? 2000 : false
  })
}
```

### Environment Config

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=sk_internal_dogfood_xxx
```

---

## State Management

### Server State (TanStack Query)

**Query Keys Structure**:
```typescript
const queryKeys = {
  workflows: {
    all: ['workflows'] as const,
    detail: (id: string) => ['workflow', id] as const
  },
  runs: {
    all: ['runs'] as const,
    detail: (id: string) => ['run', id] as const,
    history: (id: string) => ['run', id, 'history'] as const,
    context: (id: string) => ['run', id, 'context'] as const
  }
}
```

**Mutations**:
```typescript
const createWorkflow = useMutation({
  mutationFn: WorkflowsService.createWorkflow,
  onSuccess: () => {
    queryClient.invalidateQueries(queryKeys.workflows.all)
  }
})

const startRun = useMutation({
  mutationFn: ExecutionsService.startExecution,
  onSuccess: (data) => {
    queryClient.invalidateQueries(queryKeys.runs.all)
    router.push(`/runs/${data.id}`)
  }
})
```

### Client State (Zustand)

```typescript
// lib/stores/ui-store.ts
interface UIStore {
  theme: 'light' | 'dark'
  sidebarCollapsed: boolean
  toggleTheme: () => void
  toggleSidebar: () => void
}

export const useUIStore = create<UIStore>((set) => ({
  theme: 'dark',
  sidebarCollapsed: false,
  toggleTheme: () => set((state) => ({
    theme: state.theme === 'dark' ? 'light' : 'dark'
  })),
  toggleSidebar: () => set((state) => ({
    sidebarCollapsed: !state.sidebarCollapsed
  }))
}))
```

---

## Form Rendering

### Dynamic Schema Generation

```typescript
// lib/schemas/form-schema-generator.ts
import { z } from 'zod'

export function generateFormSchema(fields: FormField[]) {
  const shape: Record<string, z.ZodTypeAny> = {}

  fields.forEach(field => {
    switch (field.type) {
      case 'text':
      case 'email':
      case 'textarea':
        let stringSchema = z.string()
        if (field.required) {
          stringSchema = stringSchema.min(1, `${field.key} is required`)
        }
        if (field.pattern) {
          stringSchema = stringSchema.regex(
            new RegExp(field.pattern),
            `Invalid ${field.key} format`
          )
        }
        if (field.type === 'email') {
          stringSchema = stringSchema.email('Invalid email')
        }
        shape[field.key] = stringSchema
        break

      case 'number':
        let numberSchema = z.number()
        if (field.required) {
          numberSchema = numberSchema.min(0)
        }
        shape[field.key] = numberSchema
        break

      case 'select':
        if (!field.options || field.options.length === 0) {
          throw new Error(`Select field ${field.key} must have options`)
        }
        shape[field.key] = z.enum(field.options as [string, ...string[]])
        break

      case 'checkbox':
        shape[field.key] = z.boolean()
        break
    }
  })

  return z.object(shape)
}
```

### Field Component Mapping

```typescript
// components/form/field-renderer.tsx
export function FieldRenderer({ field }: { field: FormField }) {
  switch (field.type) {
    case 'text':
    case 'email':
    case 'number':
      return (
        <FormField
          name={field.key}
          render={({ field: formField }) => (
            <FormItem>
              <FormLabel>{field.label || field.key}</FormLabel>
              <FormControl>
                <Input
                  type={field.type}
                  placeholder={field.placeholder}
                  {...formField}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      )

    case 'textarea':
      return (
        <FormField
          name={field.key}
          render={({ field: formField }) => (
            <FormItem>
              <FormLabel>{field.label || field.key}</FormLabel>
              <FormControl>
                <Textarea {...formField} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      )

    case 'select':
      return (
        <FormField
          name={field.key}
          render={({ field: formField }) => (
            <FormItem>
              <FormLabel>{field.label || field.key}</FormLabel>
              <Select onValueChange={formField.onChange} defaultValue={formField.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select an option" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {field.options?.map(option => (
                    <SelectItem key={option} value={option}>
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
      )

    case 'checkbox':
      return (
        <FormField
          name={field.key}
          render={({ field: formField }) => (
            <FormItem className="flex items-center space-x-2">
              <FormControl>
                <Checkbox
                  checked={formField.value}
                  onCheckedChange={formField.onChange}
                />
              </FormControl>
              <FormLabel>{field.label || field.key}</FormLabel>
              <FormMessage />
            </FormItem>
          )}
        />
      )
  }
}
```

---

## Real-Time Updates

### Polling Strategy

```typescript
// hooks/use-run.ts
export function useRun(id: string) {
  const { data: run, ...query } = useQuery({
    queryKey: ['run', id],
    queryFn: () => ExecutionsService.getRun({ id }),
    refetchInterval: (data) => {
      // Poll every 2s if running
      if (data?.status === 'running') return 2000
      // Stop polling for terminal states
      if (['completed', 'failed', 'canceled'].includes(data?.status || '')) {
        return false
      }
      // Poll every 5s for waiting state (less urgent)
      if (data?.status === 'waiting') return 5000
      return false
    },
    refetchIntervalInBackground: false // Stop when tab inactive
  })

  return { run, ...query }
}
```

### Optimistic Updates

```typescript
// Optimistic update for resume
const resumeRun = useMutation({
  mutationFn: (data: ResumeRequest) =>
    ExecutionsService.resumeRun({ id: runId, data }),
  onMutate: async (variables) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries(['run', runId])

    // Snapshot previous value
    const previousRun = queryClient.getQueryData(['run', runId])

    // Optimistically update
    queryClient.setQueryData(['run', runId], (old: Run) => ({
      ...old,
      status: 'running'
    }))

    return { previousRun }
  },
  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(['run', runId], context?.previousRun)
  },
  onSettled: () => {
    // Refetch after mutation
    queryClient.invalidateQueries(['run', runId])
  }
})
```

---

## Error Handling

### Error Boundary

```typescript
// components/common/error-boundary.tsx
export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <NextErrorBoundary
      fallback={({ error, reset }) => (
        <div className="flex flex-col items-center justify-center min-h-screen">
          <AlertCircle className="w-12 h-12 text-destructive mb-4" />
          <h2 className="text-2xl font-bold mb-2">Something went wrong</h2>
          <p className="text-muted-foreground mb-4">
            {error.message || 'An unexpected error occurred'}
          </p>
          <Button onClick={reset}>Try again</Button>
        </div>
      )}
    >
      {children}
    </NextErrorBoundary>
  )
}
```

### API Error Handling

```typescript
// lib/api/error-handler.ts
export function handleApiError(error: unknown) {
  if (error instanceof ApiError) {
    // API returned error response
    toast.error(error.body?.message || 'An error occurred')
  } else if (error instanceof Error) {
    // Network or other error
    toast.error(error.message)
  } else {
    toast.error('An unexpected error occurred')
  }
}

// Usage in mutations
const createWorkflow = useMutation({
  mutationFn: WorkflowsService.createWorkflow,
  onError: handleApiError
})
```

### Loading States

```typescript
// Use skeleton instead of spinners
function WorkflowList() {
  const { data: workflows, isLoading } = useWorkflows()

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-1/3" />
              <Skeleton className="h-4 w-1/2" />
            </CardHeader>
          </Card>
        ))}
      </div>
    )
  }

  // ... render workflows
}
```

### Empty States

```typescript
function EmptyWorkflows() {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <FileText className="w-16 h-16 text-muted-foreground mb-4" />
      <h3 className="text-xl font-semibold mb-2">No workflows yet</h3>
      <p className="text-muted-foreground mb-6">
        Create your first workflow to get started
      </p>
      <Button asChild>
        <Link href="/workflows/new">
          <Plus className="w-4 h-4 mr-2" />
          Create Workflow
        </Link>
      </Button>
    </div>
  )
}
```

---

## Testing Strategy

### Unit Tests (Vitest)

```typescript
// __tests__/schemas/form-schema-generator.test.ts
import { describe, it, expect } from 'vitest'
import { generateFormSchema } from '@/lib/schemas/form-schema-generator'

describe('generateFormSchema', () => {
  it('generates schema for required text field', () => {
    const schema = generateFormSchema([
      { key: 'name', type: 'text', required: true }
    ])

    expect(schema.parse({ name: 'Test' })).toEqual({ name: 'Test' })
    expect(() => schema.parse({ name: '' })).toThrow()
  })

  it('generates schema for select with options', () => {
    const schema = generateFormSchema([
      { key: 'role', type: 'select', options: ['admin', 'user'] }
    ])

    expect(schema.parse({ role: 'admin' })).toEqual({ role: 'admin' })
    expect(() => schema.parse({ role: 'invalid' })).toThrow()
  })
})
```

### Integration Tests (Playwright)

```typescript
// e2e/workflow-creation.spec.ts
import { test, expect } from '@playwright/test'

test('create workflow end-to-end', async ({ page }) => {
  await page.goto('http://localhost:3000')

  // Click create workflow
  await page.click('text=Create Workflow')

  // Fill YAML editor
  await page.fill('.monaco-editor', `
    name: Test Workflow
    start_step: step1
    steps:
      - id: step1
        type: form
        fields:
          - key: test
            type: text
  `)

  // Wait for validation
  await expect(page.locator('text=✓ Valid')).toBeVisible()

  // Save
  await page.click('text=Save')

  // Should redirect to workflow detail
  await expect(page).toHaveURL(/\/workflows\/wf_/)
})
```

### API Mocking (MSW)

```typescript
// mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/v1/workflows', () => {
    return HttpResponse.json({
      workflows: [
        { id: 'wf_1', name: 'Test Workflow', version: 1 }
      ]
    })
  }),

  http.post('/v1/executions', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      id: 'run_123',
      status: 'running',
      workflow_id: body.workflow_id
    }, { status: 202 })
  })
]
```

---

## Deployment

### Vercel Configuration

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url",
    "NEXT_PUBLIC_API_KEY": "@api-key"
  }
}
```

### Environment Variables

**Development** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=sk_dev_xxx
```

**Production** (Vercel):
```bash
NEXT_PUBLIC_API_URL=https://api.pyscaff.com
NEXT_PUBLIC_API_KEY=sk_prod_xxx
```

### Build Commands

```bash
# Install dependencies
npm install

# Generate API client from backend
npm run generate-api

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

---

## Work Packages

Frontend implementation broken into work packages:

| WP ID | Title | Priority | Effort | Dependencies |
|-------|-------|----------|--------|--------------|
| WP-010 | Project setup + design system | P0 | 1-2 days | WP-009 |
| WP-011 | Workflow dashboard + list | P0 | 2-3 days | WP-010, WP-006 |
| WP-012 | YAML workflow editor | P0 | 3-5 days | WP-010, WP-006 |
| WP-013 | Run list + detail pages | P0 | 2-3 days | WP-010, WP-007 |
| WP-014 | Dynamic form renderer | P0 | 3-4 days | WP-010, WP-007 |
| WP-015 | Approval interface | P1 | 1-2 days | WP-010, WP-007 |
| WP-016 | Run timeline + context viewer | P1 | 2-3 days | WP-010, WP-008 |
| WP-017 | Workflow graph visualization | P1 | 2-3 days | WP-010 |
| WP-018 | Testing setup + E2E tests | P1 | 2-3 days | WP-011-017 |

**Total Estimated Effort**: 18-28 days (3.5-5.5 weeks)

---

## Appendix

### shadcn/ui Components Used

```bash
# Install shadcn/ui
npx shadcn-ui@latest init

# Add components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add form
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add select
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add table
npx shadcn-ui@latest add tabs
```

### Package Dependencies

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@radix-ui/react-*": "latest",
    "tailwindcss": "^3.4.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.5.0",
    "react-hook-form": "^7.50.0",
    "zod": "^3.22.0",
    "@monaco-editor/react": "^4.6.0",
    "reactflow": "^11.10.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vitest": "^1.2.0",
    "@playwright/test": "^1.40.0",
    "msw": "^2.0.0",
    "eslint": "^8.56.0",
    "prettier": "^3.2.0"
  }
}
```

---

**Document Version**: 0.1.0
**Last Updated**: 2025-10-01
**Approved By**: Matt Fischer
**Next Review**: After WP-010 completion
