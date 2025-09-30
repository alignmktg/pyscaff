#!/bin/bash

# Pre-reset cleanup script with GitHub integration
# Prepares codebase and GitHub state for context window reset

set -e

echo "🧹 Starting GitHub-integrated housekeeping..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Git status check
echo ""
echo "📊 Git Status:"
BRANCH=$(git branch --show-current)
echo "  Branch: $BRANCH"
UNCOMMITTED=$(git status --porcelain | wc -l)
echo "  Uncommitted files: $UNCOMMITTED"

if [ "$UNCOMMITTED" -gt 0 ]; then
    echo "  Files with changes:"
    git status --short | head -10
fi

# Check for active PRs
if command -v gh &> /dev/null; then
    PR_INFO=$(gh pr list --head "$BRANCH" --json number,title,state,url 2>/dev/null || echo "[]")
    if [ "$PR_INFO" != "[]" ] && [ "$(echo "$PR_INFO" | jq length)" -gt 0 ]; then
        echo "  Active PR: $(echo "$PR_INFO" | jq -r '.[0] | "#\(.number) - \(.title)"')"
        PR_URL=$(echo "$PR_INFO" | jq -r '.[0].url')
    fi
fi

# Step 2: Determine last session tag
LAST_TAG=$(git tag --list 'session-*' --sort=-creatordate | head -1 || echo "")
if [ -n "$LAST_TAG" ]; then
    echo "  Last session: $LAST_TAG"
fi

# Step 3: Quick quality check (non-blocking)
echo ""
echo "🔍 Quick quality check:"
if [ -f "package.json" ] && command -v npm &> /dev/null; then
    echo "  Running linter..."
    npm run lint 2>&1 | tail -3 || echo "  ⚠️  Lint check failed (non-blocking)"
else
    echo "  Skipping (no package.json)"
fi

# Step 4: Update CHANGELOG with grouped commits
echo ""
echo "📝 Updating documentation..."
if [ -f "CHANGELOG.md" ] && [ -n "$LAST_TAG" ]; then
    echo "  Changes since $LAST_TAG:"

    # Group commits by type
    FEATS=$(git log $LAST_TAG..HEAD --oneline --grep="^feat" --pretty=format:"  - %s" 2>/dev/null | head -3)
    FIXES=$(git log $LAST_TAG..HEAD --oneline --grep="^fix" --pretty=format:"  - %s" 2>/dev/null | head -3)
    CHORES=$(git log $LAST_TAG..HEAD --oneline --grep="^chore" --pretty=format:"  - %s" 2>/dev/null | head -3)

    [ -n "$FEATS" ] && echo "Features:" && echo "$FEATS"
    [ -n "$FIXES" ] && echo "Fixes:" && echo "$FIXES"
    [ -n "$CHORES" ] && echo "Chores:" && echo "$CHORES"

    echo "  ℹ️  Update CHANGELOG.md manually if needed"
fi

# Step 5: Process management
echo ""
echo "🔧 Process management:"

# Create AI state directory
mkdir -p .ai

# Track processes (portable approach)
RUNNING_PROCS=""

# Check dev server
if lsof -i :3000 &>/dev/null; then
    PID=$(lsof -ti :3000 | head -1)
    echo "  ✓ dev-server running on :3000 (PID: $PID)"
    RUNNING_PROCS="${RUNNING_PROCS}\"dev-server\":3000,"
fi

# Check Prisma Studio
if lsof -i :5555 &>/dev/null; then
    PID=$(lsof -ti :5555 | head -1)
    echo "  ✓ prisma-studio running on :5555 (PID: $PID)"
    RUNNING_PROCS="${RUNNING_PROCS}\"prisma-studio\":5555,"
fi

# Check Postgres
if lsof -i :5432 &>/dev/null; then
    PID=$(lsof -ti :5432 | head -1)
    echo "  ✓ postgres running on :5432 (PID: $PID)"
    RUNNING_PROCS="${RUNNING_PROCS}\"postgres\":5432,"
fi

# Step 6: Generate machine-readable session state
echo ""
echo "💾 Generating session state..."

DATE_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION_TAG="session-$(date +"%Y%m%d-%H%M")"

# Create session.json
cat > .ai/session.json << EOF
{
  "timestamp": "$DATE_ISO",
  "branch": "$BRANCH",
  "last_tag": "$LAST_TAG",
  "new_tag": "$SESSION_TAG",
  "uncommitted_files": $UNCOMMITTED,
  "active_pr": $([ -n "$PR_URL" ] && echo "\"$PR_URL\"" || echo "null"),
  "running_processes": {${RUNNING_PROCS%,}},
  "last_commits": [
$(git log --oneline -3 --pretty=format:'    "%h - %s"' | paste -sd',' -)
  ]
}
EOF

echo "  ✓ Created .ai/session.json"

# Step 7: Update CLAUDE.md as pointer
cat > CLAUDE.md << EOF
# CLAUDE.md - AI Assistant Pointer

## Current State
- **Branch**: $BRANCH
- **Session**: $SESSION_TAG
- **Next Session Plan**: https://github.com/alignmktg/scaff1/issues/40

## Quick Links
- [Open Issues](https://github.com/alignmktg/scaff1/issues)
- [Active PRs](https://github.com/alignmktg/scaff1/pulls)
- [Session State](.ai/session.json)
- [Handoff Doc](.claude/context-handoff.md)

## See Also
- \`.ai/BRIEFING.md\` for detailed state
- Run \`.claude/scripts/startup.sh\` after reset
EOF

echo "  ✓ Updated CLAUDE.md pointer"

# Step 8: Update Next Session Plan issue
if command -v gh &> /dev/null; then
    echo ""
    echo "🔄 Updating GitHub issue..."

    # Get open issues to include in plan
    OPEN_ISSUES=$(gh issue list --state open --limit 5 --json number,title | jq -r '.[] | "- #\(.number): \(.title)"')

    gh issue edit 40 --body "$(cat <<EOF
## Current Focus
Continuing work on Scaff MVP - AI-augmented workflow platform.

## Session State (Updated: $(date '+%Y-%m-%d %H:%M'))
- **Branch**: $BRANCH
- **Last Session Tag**: $SESSION_TAG
- **Active PR**: ${PR_URL:-None}
- **Dev Server**: $(lsof -i :3000 &>/dev/null && echo "Running on :3000" || echo "Stopped")

## Open Issues
$OPEN_ISSUES

## Next 3 Actions
1. Continue from branch: $BRANCH
2. Check issue #28 (TypeScript errors) if still blocking
3. Review issue #41 (Dark mode theming)

## Quick Start Commands
\`\`\`bash
# On next session start
.claude/scripts/startup.sh

# Or manually
git fetch --all --tags
git checkout $BRANCH
cat .ai/session.json
\`\`\`

## Session Handoff
- Machine state: \`.ai/session.json\`
- Human briefing: \`.ai/BRIEFING.md\`
- Last tag: $SESSION_TAG

---
*Auto-updated by housekeeping script at $(date)*
EOF
)" 2>/dev/null && echo "  ✓ Updated issue #40" || echo "  ⚠️  Could not update issue"
fi

# Step 9: Commit documentation changes
if [ "$UNCOMMITTED" -gt 0 ] || [ -n "$(git status --porcelain CLAUDE.md .ai/ 2>/dev/null)" ]; then
    echo ""
    echo "💾 Committing changes..."
    git add -A
    git commit -m "chore(ai-housekeeping): update docs and session state

- Session tag: $SESSION_TAG
- Updated CLAUDE.md pointer
- Generated .ai/session.json
- Captured process state" || true
fi

# Step 10: Create session tag
echo ""
echo "🏷️  Creating session tag..."
git tag -f "$SESSION_TAG" && echo "  ✓ Tagged as $SESSION_TAG"

# Step 11: Generate detailed handoff
HANDOFF_FILE=".claude/context-handoff.md"
cat > "$HANDOFF_FILE" << EOF
# Context Handoff - $(date '+%Y-%m-%d %H:%M')

## Git State
- Current Branch: $BRANCH
- Session Tag: $SESSION_TAG
- Uncommitted Changes: $([[ $UNCOMMITTED -gt 0 ]] && echo "yes ($UNCOMMITTED files)" || echo "no")
${PR_URL:+- Active PR: $PR_URL}

## Recent Commits (Since ${LAST_TAG:-beginning})
\`\`\`
$(git log ${LAST_TAG:+$LAST_TAG..HEAD} --oneline -10 2>/dev/null || git log --oneline -10)
\`\`\`

## GitHub State
- Next Session Issue: [#40](https://github.com/alignmktg/scaff1/issues/40)
- Open Issues: $(gh issue list --state open --json number | jq length 2>/dev/null || echo "unknown")

## Environment State
- Working Directory: $(pwd)
- Node Version: $(node -v 2>/dev/null || echo "not found")
${RUNNING_PROCS:+- Running Processes: ${RUNNING_PROCS%,}}

## Session Summary
Housekeeping completed with GitHub integration. Session state captured in:
- Machine-readable: \`.ai/session.json\`
- GitHub issue: #40
- Session tag: $SESSION_TAG

## Recommended Next Steps
1. Run \`.claude/scripts/startup.sh\` after context reset
2. Check GitHub issue #40 for latest state
3. Continue work on branch: $BRANCH

## Key Files
- Session State: \`.ai/session.json\`
- GitHub Issue: https://github.com/alignmktg/scaff1/issues/40
- This Handoff: $HANDOFF_FILE
EOF

echo "  ✓ Created $HANDOFF_FILE"

# Step 12: Clean test artifacts
echo ""
echo "🗑️  Cleaning test artifacts..."
CLEANED=0
for pattern in "test-*.png" "test-*.js" "*.log" "/tmp/*.log"; do
    COUNT=$(find . -maxdepth 1 -name "$pattern" 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        rm -f $pattern
        CLEANED=$((CLEANED + COUNT))
    fi
done
echo "  Removed $CLEANED test artifact(s)"

# Final report
echo ""
echo "✅ GitHub-Integrated Housekeeping Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Branch: $BRANCH"
echo "  Session Tag: $SESSION_TAG"
echo "  GitHub Issue: #40 updated"
echo "  State Files: .ai/session.json"
echo "  Handoff: $HANDOFF_FILE"
echo ""
echo "  Ready for context reset!"
echo "  Next: Run .claude/scripts/startup.sh after reset"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"