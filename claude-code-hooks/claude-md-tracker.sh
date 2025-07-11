#!/bin/bash
# Claude Code Hook - Smart CLAUDE.md Tracker
# Detects context changes and reminds Claude to re-read CLAUDE.md

# State file to track conversation state
STATE_FILE="${HOME}/.claude-code-state/claude-md-tracker"
mkdir -p "$(dirname "$STATE_FILE")"

# Get current session info
CURRENT_SESSION="${CLAUDE_SESSION_ID:-unknown}"
CURRENT_TIME=$(date +%s)

# Read previous state
PREV_SESSION=""
PREV_TIME=""
if [ -f "$STATE_FILE" ]; then
    PREV_SESSION=$(head -n 1 "$STATE_FILE" 2>/dev/null || echo "")
    PREV_TIME=$(tail -n 1 "$STATE_FILE" 2>/dev/null || echo "0")
fi

# Check if this is a new session or significant time gap
NEW_SESSION=false
if [ "$CURRENT_SESSION" != "$PREV_SESSION" ] || [ $((CURRENT_TIME - PREV_TIME)) -gt 1800 ]; then
    NEW_SESSION=true
fi

# Update state
echo "$CURRENT_SESSION" > "$STATE_FILE"
echo "$CURRENT_TIME" >> "$STATE_FILE"

# Function to find CLAUDE.md
find_claude_md() {
    local paths=("CLAUDE.md" "../CLAUDE.md" "../../CLAUDE.md" "../../../CLAUDE.md")
    for path in "${paths[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    return 1
}

# Function to show reminder
show_reminder() {
    local claude_md_path="$1"
    local trigger="$2"
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    echo "║ 📋 CLAUDE.md REMINDER ($trigger)"
    echo "║                                                                                ║"
    echo "║ Project context file found: $claude_md_path"
    echo "║                                                                                ║"
    echo "║ This file contains project-specific instructions that should be considered     ║"
    echo "║ when working on this codebase. Key sections typically include:                ║"
    echo "║ • Project overview and architecture                                            ║"
    echo "║ • Coding standards and conventions                                             ║"
    echo "║ • Testing requirements and patterns                                            ║"
    echo "║ • Development workflow and tools                                               ║"
    echo "╚════════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Show a condensed preview
    if [ -f "$claude_md_path" ]; then
        echo "Key sections from $claude_md_path:"
        echo "────────────────────────────────────────────────────────────────────────────────"
        
        # Extract headers and first line of each section
        awk '
        /^#/ { 
            print "│ " $0 
            getline
            if (NF > 0) print "│   " $0
        }
        ' "$claude_md_path" | head -n 20
        
        echo "────────────────────────────────────────────────────────────────────────────────"
        echo ""
    fi
}

# Main logic
CLAUDE_MD_PATH=$(find_claude_md)
if [ -n "$CLAUDE_MD_PATH" ]; then
    # Check different trigger conditions
    
    # 1. New session detected
    if [ "$NEW_SESSION" = true ]; then
        show_reminder "$CLAUDE_MD_PATH" "New Session"
    
    # 2. Hook triggered by compaction (PostToolUse)
    elif [ "$CLAUDE_HOOK_TYPE" = "PostToolUse" ] && [[ "$CLAUDE_TOOL_NAME" == *"compact"* ]]; then
        show_reminder "$CLAUDE_MD_PATH" "After Compaction"
    
    # 3. Hook triggered by clear command
    elif [ "$CLAUDE_HOOK_TYPE" = "PostToolUse" ] && [[ "$CLAUDE_TOOL_RESULT" == *"clear"* ]]; then
        show_reminder "$CLAUDE_MD_PATH" "After Clear"
    
    # 4. Stop hook after long conversation (every 10 responses)
    elif [ "$CLAUDE_HOOK_TYPE" = "Stop" ]; then
        RESPONSE_COUNT=$(ls ~/.claude-code-state/response-* 2>/dev/null | wc -l)
        if [ $((RESPONSE_COUNT % 10)) -eq 0 ]; then
            show_reminder "$CLAUDE_MD_PATH" "Periodic Check"
        fi
    fi
fi

# Always exit 0 to allow Claude to continue
exit 0