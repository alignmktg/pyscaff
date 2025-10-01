# ADR-007: Frontend Architecture

**Status**: Accepted
**Date**: 2025-10-01
**Authors**: Claude Code + Matt Fischer
**Supersedes**: None
**Related**: ADR-001 (Backend Stack)

## Context

PyScaff is a **full-stack AI workflow orchestrator** for non-technical users. While we have a well-defined Python/FastAPI backend, we had no frontend specification. This created a critical gap: users cannot interact with workflows without a UI.

### The Problem
- Backend-only architecture assumed API consumers
- No specification for workflow creation, monitoring, or interaction
- Missing design system and component strategy
- Unclear how non-technical users would use the system

### User Requirements
From `feature-breakdown-product-friendly.md`:
- Create workflows (YAML editor with validation)
- Start and monitor workflow runs
- Fill forms when workflows pause (wait-states)
- Approve/reject at approval steps
- Debug failures (view execution history, context)
- Non-technical users need visual interface (not just API/CLI)

## Decision

We will build a **Next.js 15 frontend** with **shadcn/ui** and a **minimalist design system**.

### Tech Stack

#### Framework & Core
- **Next.js 15** (App Router) - Server Components, streaming, built-in optimizations
- **TypeScript** - Type safety across entire frontend
- **React 19** - Latest stable with concurrent features

#### UI & Styling
- **shadcn/ui** - Copy-paste components built on Radix primitives
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible, headless component primitives
- **next-themes** - Dark mode support

#### Forms & Validation
- **React Hook Form** - Performant form state management
- **Zod** - Runtime schema validation
- **Dynamic form generation** from step config

#### State Management
- **TanStack Query (React Query)** - Server state (workflows, runs)
  - Auto caching and invalidation
  - Polling for run status updates
  - Optimistic updates
- **Zustand** - Client state (minimal, UI-only)
  - Theme toggle
  - Sidebar state
  - YAML editor unsaved changes

#### API Integration
- **openapi-typescript-codegen** - Auto-generated TypeScript client from OpenAPI spec
- **Native fetch** - No axios/ky needed (built-in in Next.js)
- **Shared API key** - Environment variable for MVID (no login flow)

#### Specialized Components
- **Monaco Editor** - YAML editor with IntelliSense
  - VS Code's editor engine
  - Syntax highlighting
  - Schema-based autocomplete
  - Validation feedback
- **ReactFlow** - Workflow visualization (DAG graphs)
  - Auto-layout algorithms
  - Highlight current step
  - Future: Visual builder support

#### Development & Testing
- **Vitest** - Unit tests (faster than Jest)
- **Playwright** - Integration and E2E tests
- **MSW (Mock Service Worker)** - API mocking for tests
- **ESLint + Prettier** - Code quality

#### Deployment
- **Vercel** - Automatic deployments from Git
- **Monorepo support** - `/frontend` directory

## Design System

### Aesthetic: Minimalist Modern Technical
**Inspiration**: Linear, Vercel Dashboard, Stripe Dashboard

**Principles**:
- Clean layouts with generous whitespace
- Subtle borders and shadows
- Clear visual hierarchy
- Status badges with semantic colors
- Dark mode default (developer-friendly)
- Accessible (WCAG AA minimum)

### Typography
**Sans-serif** (UI text):
- **Font**: Geist Sans (Vercel) or Inter
- **h1**: 2.5rem - Page titles
- **h2**: 2rem - Section headers
- **h3**: 1.5rem - Subsections
- **body**: 1rem - Default text
- **small**: 0.875rem - Metadata, captions

**Monospace** (code, YAML, JSON):
- **Font**: Geist Mono or JetBrains Mono
- **Usage**: YAML editor, JSON viewer, step IDs, run IDs

### Color Palette (Tailwind Config)

**Neutral Grays** (primary palette):
- slate-50 to slate-950
- Dark mode uses slate-800 to slate-950

**Accent Color**:
- indigo-500 - Links, primary actions, focus states

**Semantic Status Colors**:
```typescript
const statusColors = {
  queued: 'slate-400',     // Gray - waiting to start
  running: 'blue-500',     // Blue - actively executing
  waiting: 'amber-500',    // Yellow - paused for input
  completed: 'emerald-500', // Green - success
  failed: 'red-500',       // Red - error
  canceled: 'slate-500'    // Gray - user canceled
}
```

### Component Patterns

**Cards**:
- Background: slate-900 (dark) / white (light)
- Border: 1px solid slate-700 (dark) / slate-200 (light)
- Border radius: 0.5rem (rounded-lg)
- Padding: 1.5rem (p-6)

**Buttons**:
- **Primary**: Solid indigo-600 background
- **Secondary**: Outline border
- **Ghost**: Transparent, subtle hover

**Badges** (status indicators):
- Small rounded pill
- Dot indicator (colored circle) + text
- Example: `🟢 Completed` `🔵 Running` `🟡 Waiting`

**Loading States**:
- **Skeleton screens** (not spinners) for page loads
- **Inline spinners** only for button actions
- **Progress bars** for long operations (AI generation)

**Empty States**:
- Illustration or icon
- Heading: "No [resource] yet"
- Body: Brief explanation
- CTA button: "Create your first [resource]"

## Architecture

### Directory Structure
```
/frontend
  /app                      # Next.js App Router
    /layout.tsx             # Root layout (sidebar, theme)
    /page.tsx               # Dashboard
    /workflows
      /page.tsx             # Workflow list
      /new/page.tsx         # Create workflow
      /[id]/page.tsx        # Workflow detail
      /[id]/edit/page.tsx   # Edit workflow
    /runs
      /page.tsx             # Run list
      /[id]/page.tsx        # Run detail
      /[id]/form/page.tsx   # Form step renderer
    /approvals
      /[token]/page.tsx     # Approval interface
  /components               # Reusable components
    /ui                     # shadcn/ui components
    /workflow-editor        # YAML editor
    /workflow-graph         # ReactFlow graph
    /dynamic-form           # Form renderer
    /run-timeline           # Execution history
  /lib
    /api                    # Auto-generated API client
    /utils                  # Helper functions
    /hooks                  # Custom React hooks
  /styles
    /globals.css            # Tailwind base styles
```

### Routing (App Router)

**Public Routes** (MVID - no auth):
- `/` - Dashboard (workflow list)
- `/workflows` - Workflow list (same as dashboard)
- `/workflows/new` - Create workflow (YAML editor)
- `/workflows/:id` - Workflow detail + runs
- `/workflows/:id/edit` - Edit workflow
- `/runs` - Run list (filterable table)
- `/runs/:id` - Run detail (status, history, context)
- `/runs/:id/form` - Form step (if waiting)
- `/approvals/:token` - Approval interface

### Navigation Flow

```
Dashboard
  ├─> Click "Create Workflow"
  │     └─> /workflows/new (YAML editor)
  │           └─> Save → /workflows/:id (detail)
  │
  ├─> Click workflow card
  │     └─> /workflows/:id
  │           ├─> Click "Start Run" (modal)
  │           │     └─> Submit → /runs/:runId
  │           └─> Click run in list → /runs/:runId
  │
  └─> Click "View All Runs"
        └─> /runs (filterable list)
              └─> Click run → /runs/:runId
                    ├─> If waiting → Show resume form
                    ├─> View history (timeline)
                    └─> View context (JSON tree)

Email (Approval)
  └─> Click approval link → /approvals/:token
        └─> Approve/Reject → Workflow continues
```

## Key Technical Decisions

### 1. Monaco Editor (YAML Editing)

**Why Monaco over CodeMirror?**
- Feature-rich: IntelliSense, multi-cursor, find/replace
- Familiar to developers (VS Code engine)
- Schema-based autocomplete (from workflow JSON Schema)
- Better YAML support out-of-box

**Trade-offs**:
- Larger bundle (~800KB) - acceptable for internal tool
- Can lazy-load on editor page only

### 2. ReactFlow (Workflow Visualization)

**Why ReactFlow over D3/custom SVG?**
- Built for React (declarative)
- Auto-layout algorithms (handles complex workflows)
- Future-proof (supports drag-drop for visual builder)
- Community-maintained, good TypeScript support

**Trade-offs**:
- More features than needed for MVID
- Can use simple vertical flow layout initially

### 3. TanStack Query (Server State)

**Why TanStack Query over useState + fetch?**
- Built-in caching and invalidation
- Polling support (run status updates)
- Optimistic updates (better UX)
- Loading/error states handled

**Pattern**:
```typescript
// Poll run status every 2s if running
const { data: run } = useQuery({
  queryKey: ['run', runId],
  queryFn: () => ExecutionsService.getRun(runId),
  refetchInterval: run?.status === 'running' ? 2000 : false
})
```

### 4. Dynamic Form Rendering

**Challenge**: Render form from step config dynamically.

**Solution**: Config → Zod schema → React Hook Form

```typescript
// Step config
const formConfig = {
  fields: [
    { key: 'topic', type: 'text', required: true },
    { key: 'audience', type: 'select', options: ['dev', 'marketing'] }
  ]
}

// Generate Zod schema
const schema = z.object({
  topic: z.string().min(1),
  audience: z.enum(['dev', 'marketing'])
})

// Render with React Hook Form + shadcn/ui components
```

### 5. Authentication (MVID)

**Shared API Key** (environment variable):
```typescript
// .env.local
NEXT_PUBLIC_API_KEY=sk_internal_dogfood_xxx

// API client config
const client = new ApiClient({
  HEADERS: { 'X-API-Key': process.env.NEXT_PUBLIC_API_KEY }
})
```

**Post-MVID**: JWT tokens with login flow.

## Consequences

### Positive
✅ **User-friendly**: Non-technical users can create/monitor workflows
✅ **Type-safe**: OpenAPI → TypeScript client, no manual typing
✅ **Consistent UX**: shadcn/ui design system
✅ **Fast development**: Pre-built components, auto-generated API client
✅ **Production-ready**: Real-time updates, error handling, dark mode
✅ **Future-proof**: ReactFlow enables visual builder later
✅ **Testable**: MSW for mocking, Playwright for E2E

### Negative
❌ **Bundle size**: Monaco Editor adds ~800KB (mitigated by code splitting)
❌ **Complexity**: More dependencies than plain React
❌ **Learning curve**: Team needs to learn shadcn/ui patterns

### Neutral
⚖️ **Monorepo**: Frontend in separate `/frontend` directory
⚖️ **No SSR initially**: Client-side rendering is fine for MVID (auth later)
⚖️ **Polling not WebSockets**: Simpler for MVID, can upgrade later

## Risks & Mitigation

### Risk 1: Backend API changes break frontend
**Mitigation**: Auto-generate client from OpenAPI spec, update on every backend change

### Risk 2: Monaco Editor bundle size impacts load time
**Mitigation**: Lazy-load editor only on workflow edit pages, code split

### Risk 3: Dynamic form rendering doesn't support all field types
**Mitigation**: Start with basic types (text, select, textarea), add more incrementally

### Risk 4: ReactFlow overkill for simple workflows
**Mitigation**: Use vertical flow layout initially, full graph features later

## Alternatives Considered

### Alternative 1: Vue/Nuxt instead of React/Next
**Rejected**: Team standard is React, Next.js is user's global default

### Alternative 2: No UI (API/CLI only)
**Rejected**: Non-technical users cannot use API/CLI, violates core requirement

### Alternative 3: CodeMirror instead of Monaco
**Rejected**: Monaco has better YAML support and autocomplete from schema

### Alternative 4: WebSockets for real-time updates
**Deferred**: Polling is simpler for MVID, WebSockets can be added post-launch

### Alternative 5: SvelteKit or Remix
**Rejected**: Next.js is user's global default, team familiarity

## Open Questions

1. **Backend deployment?** Where will FastAPI backend be deployed? (affects CORS, API URL)
2. **Monitoring?** Should we add frontend monitoring (Sentry, LogRocket)?
3. **Analytics?** Track user behavior for product insights?

## Success Metrics

**MVID Success**:
- ✅ Non-technical users can create workflows without asking devs
- ✅ Form rendering works for all basic field types
- ✅ Run status updates within 2s (polling)
- ✅ Zero workflow creation errors from bad YAML (validation catches)
- ✅ Approval flow works end-to-end (email → click → resume)

**Technical Metrics**:
- Bundle size < 1.5MB (initial load)
- Time to Interactive < 3s on 3G
- Lighthouse score > 90 (performance, accessibility)

## Related Work

- **PRD**: `pyscaff-prd.md` - Project requirements
- **Feature Breakdown**: `feature-breakdown-product-friendly.md` - MVID scope
- **Backend Docs**: `CLAUDE.md` - Backend API specification
- **GitHub Issue**: #15 (WP-009: Frontend Architecture Specification)

## References

- [Next.js 15 Docs](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [TanStack Query](https://tanstack.com/query)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [ReactFlow](https://reactflow.dev)
- [Tailwind CSS](https://tailwindcss.com)

---

**Last Updated**: 2025-10-01
**Reviewed By**: Matt Fischer
**Next Review**: After MVID launch
