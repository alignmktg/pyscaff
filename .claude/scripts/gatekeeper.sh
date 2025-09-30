#!/bin/bash

# Gatekeeper Script - Technical discipline enforcer
# Evaluates ideas against best practices and guards against scope creep

set -euo pipefail

echo "==================================================="
echo "🛡️  GATEKEEPER - Technical Discipline Enforcer"
echo "==================================================="
echo ""

# Function to display usage
usage() {
    cat << EOF
Usage: $0 "<idea or request>"

The Gatekeeper evaluates your idea against:
- Industry best practices
- Current MVP scope
- Work package discipline (2-6 hour batches)
- BDD/TDD requirements
- Project constitution principles

Examples:
  $0 "Should we add OAuth login?"
  $0 "Can we refactor the entire auth system?"
  $0 "Let's add real-time collaboration"

EOF
    exit 1
}

# Check for arguments
if [ $# -eq 0 ]; then
    usage
fi

IDEA="$*"

echo "📝 Evaluating: \"$IDEA\""
echo ""
echo "Checking against project principles..."
echo ""

# Core evaluation criteria
cat << 'EVALUATION'
🎯 EVALUATION CRITERIA:

1. ⏱️  WORK PACKAGE SIZE
   ✓ Can this be completed in 2-6 hours?
   ✓ Single atomic commit possible?
   ✓ Clear definition of done?

2. 🎪 MVP FOCUS
   ✓ Is this essential for MVP?
   ✓ Does it serve current users?
   ✓ Can we ship without it?

3. 🧪 TEST DISCIPLINE
   ✓ Can we write tests first?
   ✓ Is 80% coverage achievable?
   ✓ Clear acceptance criteria?

4. 🏗️  TECHNICAL DEBT
   ✓ Does this add unnecessary complexity?
   ✓ Are we solving real vs imagined problems?
   ✓ Is there a simpler solution?

5. 📋 PROJECT CONSTITUTION
   ✓ Safe-by-default approach?
   ✓ Transparent and observable?
   ✓ Incremental delivery possible?

EVALUATION

echo ""
echo "---------------------------------------------------"
echo "📊 DECISION FRAMEWORK:"
echo ""

# Decision matrix
cat << 'MATRIX'
PROCEED IF:
✅ Fits in single work package (2-6 hours)
✅ Has clear business value for MVP
✅ Can be tested with BDD/TDD
✅ Doesn't violate constitution
✅ Has GitHub issue created

REJECT IF:
❌ "Nice to have" not "need to have"
❌ Requires multiple work packages
❌ Adds complexity without proven need
❌ Violates single-commit principle
❌ No clear acceptance criteria

DEFER IF:
⏸️  Good idea but not MVP critical
⏸️  Requires significant architecture changes
⏸️  Dependencies not ready
⏸️  Better solution might emerge

MATRIX

echo ""
echo "---------------------------------------------------"
echo "💡 RECOMMENDED APPROACH:"
echo ""

# Context-aware recommendations
if [[ "$IDEA" == *"OAuth"* ]] || [[ "$IDEA" == *"oauth"* ]] || [[ "$IDEA" == *"social login"* ]]; then
    echo "❌ OAuth/Social Login: Explicitly out of MVP scope"
    echo "   Keep using email/password only as specified"

elif [[ "$IDEA" == *"refactor"* ]] || [[ "$IDEA" == *"rewrite"* ]]; then
    echo "⚠️  Refactoring: Only if fixing actual problems"
    echo "   Create specific GitHub issue with:"
    echo "   - Current problem (with evidence)"
    echo "   - Proposed solution"
    echo "   - Success metrics"

elif [[ "$IDEA" == *"real-time"* ]] || [[ "$IDEA" == *"websocket"* ]]; then
    echo "❌ Real-time features: Not in MVP scope"
    echo "   MVP is synchronous-only as specified"

elif [[ "$IDEA" == *"microservice"* ]] || [[ "$IDEA" == *"micro-service"* ]]; then
    echo "❌ Microservices: Explicitly forbidden in MVP"
    echo "   Keep monolithic Next.js architecture"

else
    echo "📋 To proceed with this idea:"
    echo "   1. Create GitHub issue with clear scope"
    echo "   2. Define acceptance criteria"
    echo "   3. Write BDD tests first"
    echo "   4. Implement in 2-6 hour work package"
    echo "   5. Single commit with semantic message"
fi

echo ""
echo "---------------------------------------------------"
echo "📚 RELEVANT DOCUMENTS:"
echo ""
echo "   • Project Constitution: .specify/memory/constitution.md"
echo "   • Work Package Template: .claude/templates/work-package-template.md"
echo "   • Current MVP Scope: CLAUDE.md"
echo ""
echo "Remember: We're building an MVP, not the perfect system!"
echo "==================================================="