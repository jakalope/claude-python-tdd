#!/bin/bash
# Claude Code Hook - Post-Compaction CLAUDE.md Reminder
# This hook detects when compaction occurs and reminds Claude to re-read CLAUDE.md

# Check if this is a PostToolUse hook for a compaction operation
# Look for compaction indicators in the environment or previous command
if [ -n "$CLAUDE_TOOL_NAME" ] && [[ "$CLAUDE_TOOL_NAME" == *"compact"* ]]; then
    COMPACTION_DETECTED=true
elif [ -n "$CLAUDE_LAST_COMMAND" ] && [[ "$CLAUDE_LAST_COMMAND" == *"/compact"* ]]; then
    COMPACTION_DETECTED=true
else
    # Check if this is a Stop hook after a compaction-like operation
    # Look for indicators that context was reduced
    COMPACTION_DETECTED=false
fi

# Check if CLAUDE.md exists in current or parent directories
CLAUDE_MD_PATH=""
if [ -f "CLAUDE.md" ]; then
    CLAUDE_MD_PATH="CLAUDE.md"
elif [ -f "../CLAUDE.md" ]; then
    CLAUDE_MD_PATH="../CLAUDE.md"
elif [ -f "../../CLAUDE.md" ]; then
    CLAUDE_MD_PATH="../../CLAUDE.md"
fi

# If CLAUDE.md exists, show the reminder
if [ -n "$CLAUDE_MD_PATH" ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║ 🔄 CONTEXT COMPACTION DETECTED - CLAUDE.md REMINDER                         ║"
    echo "║                                                                              ║"
    echo "║ After compaction, some project context may be lost. Please ensure Claude    ║"
    echo "║ re-reads the project-specific instructions in:                              ║"
    echo "║                                                                              ║"
    echo "║ 📄 $CLAUDE_MD_PATH"
    echo "║                                                                              ║"
    echo "║ This file contains important project context, coding standards, and         ║"
    echo "║ specific instructions that should be preserved across conversations.        ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Optionally show first few lines of CLAUDE.md as a preview
    if [ -f "$CLAUDE_MD_PATH" ]; then
        echo "Preview of $CLAUDE_MD_PATH:"
        echo "──────────────────────────────────────────────────────────────────────────────"
        head -n 10 "$CLAUDE_MD_PATH" | sed 's/^/│ /'
        echo "──────────────────────────────────────────────────────────────────────────────"
        echo ""
    fi
fi

# Always exit 0 to allow Claude to continue
exit 0