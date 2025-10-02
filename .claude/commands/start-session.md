# /start-session

Auto-loads PRD context at session start.

## Instructions

1. Read `/Users/MacFish/Code/pyscaff/pyscaff-prd.md` (canonical spec)
2. Read `/Users/MacFish/Code/pyscaff/SESSION-HANDOFF.md` (session state)
3. List open GitHub issues in milestone "MVID v1.0" (run: `gh issue list --milestone "MVID v1.0" --state open`)
4. Present Work Session Charter:

---

**MVID v1.0 Work Session**

**PRD Version:** {version from prd-prd.md}
**Open Issues:** {count} ({list first 3 by number and title})
**Last Session Summary:** {from SESSION-HANDOFF.md}

**MVID Scope (PRD Section 1):**
- 5 executors: form, ai_generate, conditional, api_call, approval
- 11 API endpoints
- Frontend: Dashboard, Workflow CRUD, Run monitoring, Forms, Approvals
- Exit criteria: Start run → form → AI → approval → complete

**Governance Rules:**
- All work must cite PRD sections
- Work packages are vertical slices (backend + frontend + tests)
- No layer-scoped work (frontend-only, backend-only)
- GitHub issues = source of truth

**Ready to work. What should I tackle first?**

---
