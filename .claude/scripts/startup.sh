#!/bin/bash

# Post-reset orientation script with GitHub integration
# Restores context from GitHub issues and machine state

set -e

echo "🚀 Claude Code Session Initialization (GitHub-Integrated)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Fetch latest from GitHub
echo ""
echo "🔄 Syncing with GitHub..."
git fetch --all --tags 2>/dev/null && echo "  ✓ Fetched latest changes" || echo "  ⚠️  Could not fetch (offline?)"

# Step 2: Load machine state if exists
SESSION_FILE=".ai/session.json"
HANDOFF_FILE=".claude/context-handoff.md"

if [ -f "$SESSION_FILE" ]; then
    echo ""
    echo "📋 Found session state from previous run"

    # Parse key values from JSON
    LAST_TAG=$(jq -r '.new_tag // .last_tag' "$SESSION_FILE" 2>/dev/null || echo "")
    LAST_BRANCH=$(jq -r '.branch' "$SESSION_FILE" 2>/dev/null || echo "")
    LAST_PR=$(jq -r '.active_pr // "none"' "$SESSION_FILE" 2>/dev/null || echo "none")

    echo "  Last session: ${LAST_TAG:-unknown}"
    echo "  Last branch: ${LAST_BRANCH:-unknown}"
    [ "$LAST_PR" != "none" ] && [ "$LAST_PR" != "null" ] && echo "  Last PR: $LAST_PR"
elif [ -f "$HANDOFF_FILE" ]; then
    echo ""
    echo "📋 Found handoff document"
    echo "  Reading from: $HANDOFF_FILE"
    LAST_TAG=$(grep "Session Tag:" "$HANDOFF_FILE" | cut -d: -f2 | xargs)
fi

# Step 3: Git orientation
echo ""
echo "🌿 Git Status:"
BRANCH=$(git branch --show-current)
echo "  Current branch: $BRANCH"

# Show changes since last session
if [ -n "$LAST_TAG" ]; then
    COMMITS_SINCE=$(git rev-list --count ${LAST_TAG}..HEAD 2>/dev/null || echo "0")
    if [ "$COMMITS_SINCE" -gt 0 ]; then
        echo "  Changes since $LAST_TAG: $COMMITS_SINCE commits"
        git log ${LAST_TAG}..HEAD --oneline -5 --pretty=format:"    %h %s" 2>/dev/null
        echo ""
    fi
fi

UNCOMMITTED=$(git status --porcelain | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
    echo "  ⚠️  Uncommitted changes: $UNCOMMITTED file(s)"
    git status --short | head -5
    [ "$UNCOMMITTED" -gt 5 ] && echo "  ... and $((UNCOMMITTED - 5)) more"
else
    echo "  ✓ Working directory clean"
fi

# Recent commits
echo ""
echo "📜 Recent commits:"
git log --oneline -5 --pretty=format:"  %h %s"
echo ""

# Check for PRs on current branch
if command -v gh &> /dev/null; then
    PR_INFO=$(gh pr list --head "$BRANCH" --json number,title,state,url 2>/dev/null || echo "[]")
    if [ "$PR_INFO" != "[]" ] && [ "$(echo "$PR_INFO" | jq length)" -gt 0 ]; then
        echo ""
        echo "🔗 Active PR on this branch:"
        echo "$PR_INFO" | jq -r '.[] | "  #\(.number) - \(.title) [\(.state)]"'
        echo "$PR_INFO" | jq -r '.[] | "  URL: \(.url)"'
    fi
fi

# Step 4: GitHub Issues check
echo ""
echo "📌 GitHub State:"
if command -v gh &> /dev/null; then
    # Check for Next Session Plan issue
    SESSION_ISSUE=$(gh issue view 40 --json title,state,body 2>/dev/null || echo "{}")
    if [ "$SESSION_ISSUE" != "{}" ]; then
        echo "  ✓ Next Session Plan: #40 ($(echo "$SESSION_ISSUE" | jq -r '.state'))"
    fi

    # Get open issues
    OPEN_ISSUES=$(gh issue list --state open --limit 5 --json number,title,labels)
    ISSUE_COUNT=$(echo "$OPEN_ISSUES" | jq length)
    echo "  Open issues: $ISSUE_COUNT"

    if [ "$ISSUE_COUNT" -gt 0 ]; then
        echo ""
        echo "  Priority issues:"
        echo "$OPEN_ISSUES" | jq -r '.[] | "    #\(.number): \(.title)"' | head -3

        # Check for AI-labeled issues
        AI_ISSUES=$(echo "$OPEN_ISSUES" | jq '[.[] | select(.labels[].name | startswith("ai:"))]' | jq length)
        [ "$AI_ISSUES" -gt 0 ] && echo "  AI-tagged issues: $AI_ISSUES"
    fi
else
    echo "  ⚠️  GitHub CLI not available - install 'gh' for full integration"
fi

# Step 5: Environment check
echo ""
echo "🔧 Environment:"
echo "  Node: $(node -v 2>/dev/null || echo "not found")"
echo "  npm: $(npm -v 2>/dev/null || echo "not found")"

# Check key processes (portable approach)
if lsof -i :3000 &>/dev/null; then
    echo "  ✓ dev-server running on :3000"
else
    echo "  - dev-server not running"
fi

if lsof -i :5555 &>/dev/null; then
    echo "  ✓ prisma-studio running on :5555"
else
    echo "  - prisma-studio not running"
fi

if lsof -i :5432 &>/dev/null; then
    echo "  ✓ postgres running on :5432"
else
    echo "  - postgres not running"
fi

# Database status
if [ -f "prisma/schema.prisma" ]; then
    MIGRATION_STATUS=$(npx prisma migrate status 2>&1 | grep -E "(up to date|behind)" | head -1 || echo "unknown")
    echo "  Database: $MIGRATION_STATUS"
fi

# Step 6: Generate briefing if needed
BRIEFING_FILE=".ai/BRIEFING.md"
echo ""
echo "📄 Generating briefing..."

cat > "$BRIEFING_FILE" << EOF
# AI Session Briefing - $(date '+%Y-%m-%d %H:%M')

## Current State
- **Branch**: $BRANCH
- **Uncommitted**: $UNCOMMITTED files
- **Last Session**: ${LAST_TAG:-none}
${LAST_PR:+- **Last PR**: $LAST_PR}

## Changes Since Last Session
$(if [ -n "$LAST_TAG" ] && [ "$COMMITS_SINCE" -gt 0 ]; then
    git log ${LAST_TAG}..HEAD --oneline --pretty=format:"- %s" | head -5
else
    echo "- No changes tracked (first session or no tags)"
fi)

## GitHub Issues (Top Priority)
$(if command -v gh &> /dev/null; then
    gh issue list --state open --limit 3 --json number,title,labels | \
    jq -r '.[] | "- #\(.number): \(.title) \(if (.labels | length) > 0 then "[\(.labels[].name)]" else "" end)"'
else
    echo "- GitHub CLI not available"
fi)

## Environment Status
- Dev Server: $(lsof -i :3000 &>/dev/null && echo "✓ Running" || echo "⚠️  Stopped")
- Prisma Studio: $(lsof -i :5555 &>/dev/null && echo "✓ Running" || echo "⚠️  Stopped")
- Database: $([ -f "prisma/schema.prisma" ] && echo "Configured" || echo "Not configured")

## Next Actions (from Issue #40)
1. Continue from branch: $BRANCH
2. Check issue #28 if TypeScript errors persist
3. Review issue #41 for dark mode theming

## Quick Commands
\`\`\`bash
# Start dev server
npm run dev &

# View issues
gh issue list --state open

# Check PR status
gh pr status
\`\`\`
EOF

echo "  ✓ Created $BRIEFING_FILE"

# Step 7: Load project context
echo ""
echo "📁 Project Context:"
if [ -f "package.json" ]; then
    PROJECT_NAME=$(node -pe "require('./package.json').name" 2>/dev/null || echo "unknown")
    echo "  Name: $PROJECT_NAME"

    # Check for key dependencies
    grep -q "next" package.json && echo "  Framework: Next.js"
    grep -q "@prisma/client" package.json && echo "  Database: Prisma"
    grep -q "typescript" package.json && echo "  Language: TypeScript"
fi

# Check CLAUDE.md pointer
if [ -f "CLAUDE.md" ]; then
    echo "  ✓ CLAUDE.md pointer exists"
fi

# Step 8: Recommendations
echo ""
echo "💡 Recommended Actions:"

if [ "$UNCOMMITTED" -gt 0 ]; then
    echo "  1. Review and commit uncommitted changes"
elif [ "$BRANCH" != "main" ]; then
    echo "  1. Continue feature work on $BRANCH"
else
    echo "  1. Create feature branch for new work"
fi

if ! lsof -i :3000 &>/dev/null && [ -f "package.json" ]; then
    echo "  2. Start dev server: npm run dev"
fi

if command -v gh &> /dev/null && [ "$ISSUE_COUNT" -gt 0 ]; then
    echo "  3. Check GitHub issues for priority work"
fi

# Step 9: Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Session initialized with GitHub integration!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📌 Next Session Plan: Issue #40"
echo "  📄 Full briefing: $BRIEFING_FILE"
echo "  🔧 Session state: $SESSION_FILE"
echo ""
echo "Ready to continue work. What would you like to focus on?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"