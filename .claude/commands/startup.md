# /startup - Post-Reset Orientation Command (GitHub-Integrated)

Execute this command immediately after clearing or compacting the Claude Code context window.

## Automated Script Available
Run `.claude/scripts/startup.sh` for automated execution of all steps below.

## What This Command Does

1. **GitHub Sync** - Fetches latest changes and tags from remote
2. **Restores Context** - Loads session state from `.ai/session.json` and GitHub issues
3. **Git Orientation** - Shows current branch, commits since last session, and status
4. **GitHub State** - Displays open issues, PRs, and AI-tagged work items
5. **Environment Check** - Verifies dev server, database, dependencies
6. **Project State** - Generates fresh briefing in `.ai/BRIEFING.md`
7. **Next Actions** - Suggests immediate next steps based on GitHub issues

## Execution Steps

### Step 1: Sync with GitHub
```bash
git fetch --all --tags
```

### Step 2: Load Machine State
Check for session state from previous run:
```bash
# Load from JSON if exists
cat .ai/session.json

# Parse key values
jq -r '.new_tag // .last_tag' .ai/session.json
jq -r '.branch' .ai/session.json
jq -r '.active_pr // "none"' .ai/session.json
```

If no JSON exists, check handoff document:
```bash
cat .claude/context-handoff.md
```

### Step 3: Git Orientation
```bash
# Current state
git branch --show-current
git status --porcelain

# Changes since last session
git rev-list --count ${LAST_TAG}..HEAD
git log ${LAST_TAG}..HEAD --oneline -5

# Recent commits
git log --oneline -5

# Check for PRs on current branch
gh pr list --head $(git branch --show-current) --json number,title,state,url
```

### Step 4: GitHub Issues Check
```bash
# Check Next Session Plan issue
gh issue view 40 --json title,state,body

# Get open issues
gh issue list --state open --limit 5 --json number,title,labels

# Find AI-tagged issues
gh issue list --state open --label "ai:startup"
```

### Step 5: Environment Status
```bash
# Check Node/npm
node -v
npm -v

# Check processes
lsof -i :3000  # Dev server
lsof -i :5555  # Prisma Studio
lsof -i :5432  # Postgres

# Database status
npx prisma migrate status
```

### Step 6: Generate Briefing
Create `.ai/BRIEFING.md`:
```markdown
# AI Session Briefing - [Current Date]

## Current State
- **Branch**: main
- **Uncommitted**: 3 files
- **Last Session**: session-20250927-1309
- **Last PR**: https://github.com/org/repo/pull/123

## Changes Since Last Session
- feat: implemented new feature
- fix: resolved bug in workflow
- chore: updated documentation

## GitHub Issues (Top Priority)
- #28: Fix TypeScript errors [bug]
- #41: Fix dark mode theming [enhancement]
- #40: Next Session Plan [ai:startup]

## Environment Status
- Dev Server: ✓ Running
- Prisma Studio: ⚠️ Stopped
- Database: Configured

## Next Actions (from Issue #40)
1. Continue from branch: main
2. Check issue #28 if TypeScript errors persist
3. Review issue #41 for dark mode theming

## Quick Commands
\`\`\`bash
npm run dev &
gh issue list --state open
gh pr status
\`\`\`
```

### Step 7: Load Project Context
```bash
# Get project info
node -pe "require('./package.json').name"

# Check for key files
test -f CLAUDE.md && echo "CLAUDE.md pointer exists"
head -20 TODO.md
tail -20 CHANGELOG.md
```

### Step 8: Generate Status Summary

Display formatted summary:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Session initialized with GitHub integration!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📌 Next Session Plan: Issue #40
  📄 Full briefing: .ai/BRIEFING.md
  🔧 Session state: .ai/session.json

Ready to continue work. What would you like to focus on?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Quick Start Variations

### After Planned Reset (with Housekeeping)
- Loads from `.ai/session.json`
- Reads Issue #40 for latest plan
- Shows changes since last session tag
- Continues from documented next steps

### After Unexpected Reset
- Falls back to `.claude/context-handoff.md`
- Full git history review
- Rebuilds context from GitHub issues
- Checks all modified files

### Starting New Work
- Creates feature branch if needed
- Loads relevant GitHub issues
- Checks for blocking issues
- Sets up clean workspace

## Integration with GitHub

The startup command now:
1. **Reads from GitHub** - Issues are source of truth
2. **Uses Session Tags** - Track history between sessions
3. **Machine-Readable State** - `.ai/session.json` for precise handoff
4. **Issue #40** - Persistent "Next Session Plan" survives all resets

## Benefits

1. **Mobile Continuity** - Check/update Issue #40 from phone
2. **AI Memory** - Session tags and issues persist forever
3. **Collaboration** - GitHub Copilot sees same issues
4. **Learning** - Build real Git/GitHub skills

## Usage Examples

```bash
# Standard startup after reset
/startup

# Manual run of script
.claude/scripts/startup.sh

# Check state without full startup
cat .ai/session.json
gh issue view 40
```

## Files Created/Used

- `.ai/session.json` - Machine state from last session
- `.ai/BRIEFING.md` - Fresh briefing for this session
- `.claude/context-handoff.md` - Fallback handoff document
- `CLAUDE.md` - Minimal pointer to GitHub and state files
- Issue #40 - Persistent plan on GitHub

## See Also
- `/housekeeping` - Run before context reset to prepare handoff and update GitHub