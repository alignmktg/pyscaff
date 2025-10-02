# /verify-prd

Validates proposed work against PRD spec.

## Instructions

1. Ask user: "What work are you proposing?"
2. Read `/Users/MacFish/Code/pyscaff/pyscaff-prd.md`
3. Analyze proposal:
   - **In scope?** Check Sections 1 (Scope), 21 (Exit Criteria)
   - **API surface?** Check Section 5 (API endpoints)
   - **Executors?** Check Section 1 (5 types only)
   - **Vertical slice?** Must span backend + frontend + tests
4. Report:

---

**PRD Verification Report**

**Proposal:** {summarize user request}

**Scope Check:**
- ✅/❌ In PRD Section {X}: {quote relevant text}
- ✅/❌ Required for exit criteria (Section 21)
- ✅/❌ Vertical slice (backend + frontend + tests)

**Recommendation:**
- **APPROVED**: Proceed with work package
- **MODIFY**: {suggest changes to align with PRD}
- **REJECT**: Out of MVID scope, defer to v2

**PRD Sections to cite in work package:** {list}

---
