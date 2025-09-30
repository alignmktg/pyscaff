# /housekeeping - Pre-Reset Cleanup Command (GitHub-Integrated)

Execute this command before clearing or compacting the Claude Code context window.

## Automated Script Available
Run `.claude/scripts/housekeeping.sh` for automated execution of all steps below.

## What This Command Does

1. **GitHub Integration**
   - Creates/updates AI coordination labels (`ai:housekeeping`, `ai:startup`, `ai:blocked`)
   - Updates Issue #40 (Next Session Plan) with current state
   - Creates session tags for history tracking

2. **Updates Documentation Files**
   - CLAUDE.md - Becomes a pointer to GitHub issues and state files (max 15 lines)
   - CHANGELOG.md - Groups commits by type (feat/fix/chore) since last session
   - Machine state in `.ai/session.json` for AI handoff

3. **Git State Management**
   - Commits any uncommitted changes with descriptive message
   - Creates session tag (`session-YYYYMMDD-HHMM`)
   - Documents current branch and PR status
   - Captures recent commit history

4. **Process Cleanup**
   - Tracks running processes (dev server, Prisma Studio, Postgres)
   - Kills orphaned development servers
   - Documents processes in session state

5. **Generates Handoff Documents**
   - `.ai/session.json` - Machine-readable state with branch, tag, PRs, issues
   - `.claude/context-handoff.md` - Human-readable handoff for context transfer
   - Updates GitHub Issue #40 with session summary

## Execution Steps

### Step 1: Check Git Status
```bash
git status --porcelain
git branch --show-current
gh pr list --head $(git branch --show-current) --json number,title,state,url
```

### Step 2: Check Last Session Tag
```bash
git tag --list 'session-*' --sort=-creatordate | head -1
```

### Step 3: Quick Quality Check (Non-blocking)
```bash
npm run lint 2>&1 | tail -3
```

### Step 4: Update CHANGELOG.md
Group commits by type since last session:
```bash
git log $LAST_TAG..HEAD --oneline --grep="^feat" --pretty=format:"- %s"
git log $LAST_TAG..HEAD --oneline --grep="^fix" --pretty=format:"- %s"
git log $LAST_TAG..HEAD --oneline --grep="^chore" --pretty=format:"- %s"
```

### Step 5: Process Management
Check and document running processes:
```bash
lsof -i :3000  # Dev server
lsof -i :5555  # Prisma Studio
lsof -i :5432  # Postgres
```

### Step 6: Generate Machine State
Create `.ai/session.json`:
```json
{
  "timestamp": "2025-09-27T18:09:09Z",
  "branch": "main",
  "last_tag": "session-20250927-1200",
  "new_tag": "session-20250927-1309",
  "uncommitted_files": 7,
  "active_pr": "https://github.com/org/repo/pull/123",
  "running_processes": {"dev-server": 3000},
  "last_commits": ["hash - message", ...]
}
```

### Step 7: Update CLAUDE.md Pointer
Keep minimal, GitHub-focused:
```markdown
# CLAUDE.md - AI Assistant Pointer

## Current State
- **Branch**: main
- **Session**: session-20250927-1309
- **Next Session Plan**: https://github.com/alignmktg/scaff1/issues/40

## Quick Links
- [Open Issues](https://github.com/alignmktg/scaff1/issues)
- [Session State](.ai/session.json)
- [Handoff Doc](.claude/context-handoff.md)
```

### Step 8: Update GitHub Issue #40
```bash
gh issue edit 40 --body "updated content with session state"
```

### Step 9: Commit Documentation
```bash
git add -A
git commit -m "chore(ai-housekeeping): update docs and session state

- Session tag: session-20250927-1309
- Updated CLAUDE.md pointer
- Generated .ai/session.json
- Captured process state"
```

### Step 10: Create Session Tag
```bash
git tag -f "session-$(date +"%Y%m%d-%H%M")"
```

### Step 11: Generate Context Handoff
Create `.claude/context-handoff.md` with:
- Git state and session tag
- Recent commits since last tag
- GitHub issue links
- Environment state
- Next recommended steps

### Step 12: Clean Test Artifacts
```bash
rm -f test-*.png test-*.js *.log /tmp/*.log
```

### Step 13: Final Status Report
Display:
- Branch and session tag
- GitHub issue #40 updated
- State files created
- Ready for context reset

## Usage Notes

- Run when conversation feels sluggish
- Always run before manual context clearing
- Run after completing major work packages
- Session tags and GitHub issues persist across resets
- The `.ai/` directory contains machine-readable state
- Issue #40 serves as persistent "Next Session Plan"

## Benefits of GitHub Integration

1. **Mobile Work** - Manage tasks from GitHub mobile app
2. **AI Continuity** - Issues and tags survive context resets
3. **Version Control Learning** - Build real Git skills
4. **Collaboration** - GitHub Copilot + Claude Code work together

## See Also
- `/startup` - Run after context reset to restore state from GitHub