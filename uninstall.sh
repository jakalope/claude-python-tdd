#!/bin/bash
# TDD Wrapper Uninstallation Script

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/tdd"
STATE_DIR="${HOME}/.tdd-state"

echo "🗑️  Uninstalling Claude TDD Wrapper..."
echo "===================================="

# Remove main executable
if [ -f "$INSTALL_DIR/tdd-python" ]; then
    echo "📦 Removing TDD wrapper executable..."
    rm -f "$INSTALL_DIR/tdd-python"
    echo "  ✓ Removed tdd-python"
fi

# Remove Python modules
echo "📦 Removing Python modules..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
SITE_PACKAGES="${HOME}/.local/lib/python${PYTHON_VERSION}/site-packages"

for module in tdd_tracker.py tdd_config.py tdd_import_hook.py; do
    if [ -f "$SITE_PACKAGES/$module" ]; then
        rm -f "$SITE_PACKAGES/$module"
        echo "  ✓ Removed $module"
    fi
done

# Remove __pycache__ directories
find "$SITE_PACKAGES" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove git hooks
echo "🔗 Removing git hooks..."
if [ -d .git/hooks ]; then
    for hook in pre-commit post-commit; do
        if [ -L ".git/hooks/$hook" ]; then
            # Check if it's a symlink to our hook
            link_target=$(readlink ".git/hooks/$hook")
            if [[ "$link_target" == *"claude-tdd"* ]]; then
                rm -f ".git/hooks/$hook"
                echo "  ✓ Removed $hook hook"
            else
                echo "  ⚠️  $hook hook exists but doesn't point to TDD wrapper, skipping"
            fi
        fi
    done
else
    echo "  ℹ️  Not in a git repository, skipping git hooks"
fi

# Handle configuration and state
echo ""
read -p "Remove configuration files and TDD state? This will delete all TDD history. [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Remove configuration
    if [ -f "$CONFIG_DIR/config.json" ]; then
        rm -f "$CONFIG_DIR/config.json"
        echo "  ✓ Removed global configuration"
    fi
    
    # Remove state database
    if [ -d "$STATE_DIR" ]; then
        rm -rf "$STATE_DIR"
        echo "  ✓ Removed TDD state database"
    fi
    
    # Remove local project config
    if [ -f ".tdd-config.json" ]; then
        read -p "Remove local .tdd-config.json? [y/N] " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f ".tdd-config.json"
            echo "  ✓ Removed local configuration"
        fi
    fi
else
    echo "  ℹ️  Keeping configuration and state files"
fi

# Remove aliases
echo ""
echo "🔧 Removing aliases..."

remove_alias_from_file() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        return
    fi
    
    # Check if file contains TDD aliases
    if grep -q "# TDD Python Wrapper" "$file" 2>/dev/null; then
        echo "  Found TDD aliases in $file"
        
        # Create backup
        cp "$file" "${file}.tdd-backup"
        
        # Remove TDD section (from comment to next blank line or EOF)
        awk '
            /# TDD Python Wrapper/ { in_tdd_section = 1; next }
            in_tdd_section && /^$/ { in_tdd_section = 0; next }
            in_tdd_section { next }
            { print }
        ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
        
        echo "  ✓ Removed TDD aliases from $file"
        echo "  ℹ️  Backup saved as ${file}.tdd-backup"
    fi
}

# Check virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    remove_alias_from_file "$VIRTUAL_ENV/bin/activate"
elif [ -f "venv/bin/activate" ]; then
    remove_alias_from_file "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
    remove_alias_from_file ".venv/bin/activate" 
elif [ -f "env/bin/activate" ]; then
    remove_alias_from_file "env/bin/activate"
fi

# Check shell configs
for rc_file in "${HOME}/.bashrc" "${HOME}/.zshrc"; do
    if [ -f "$rc_file" ]; then
        if grep -q "# TDD Python Wrapper" "$rc_file" 2>/dev/null; then
            echo ""
            read -p "Remove TDD aliases from $rc_file? [y/N] " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                remove_alias_from_file "$rc_file"
            fi
        fi
    fi
done

echo ""
echo "✅ Uninstallation complete!"
echo ""
echo "ℹ️  Note:"
echo "  - If you had sourced any modified files, restart your shell"
echo "  - If using a virtualenv, reactivate it"
echo "  - Any backup files created end with .tdd-backup"