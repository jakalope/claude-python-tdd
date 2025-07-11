#!/bin/bash
# TDD Wrapper Installation Script

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_DIR="${HOME}/.config/tdd"

echo "🚀 Installing Claude TDD Wrapper..."
echo "================================="

# Detect virtual environment
VENV_ACTIVE=false
if [ -n "$VIRTUAL_ENV" ]; then
    VENV_ACTIVE=true
    INSTALL_DIR="$VIRTUAL_ENV/bin"
    PYTHON_EXECUTABLE="$VIRTUAL_ENV/bin/python"
    echo "🐍 Virtual environment detected: $VIRTUAL_ENV"
else
    INSTALL_DIR="${HOME}/.local/bin"
    PYTHON_EXECUTABLE="python3"
    echo "⚠️  No virtual environment active. Installing globally to $INSTALL_DIR"
    echo ""
    read -p "Continue with global installation? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled. Please activate a virtual environment and try again."
        exit 1
    fi
fi

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "${HOME}/.tdd-state"

# Copy main scripts
echo "📦 Installing TDD wrapper..."
cp "${SCRIPT_DIR}/tdd-python" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/tdd-python"

# Install Python modules
echo "📦 Installing Python modules..."
PYTHON_VERSION=$($PYTHON_EXECUTABLE -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

if [ "$VENV_ACTIVE" = true ]; then
    # Install in virtualenv site-packages
    SITE_PACKAGES="$VIRTUAL_ENV/lib/python${PYTHON_VERSION}/site-packages"
else
    # Install in user site-packages
    SITE_PACKAGES="${HOME}/.local/lib/python${PYTHON_VERSION}/site-packages"
fi

mkdir -p "$SITE_PACKAGES"

cp "${SCRIPT_DIR}/tdd_tracker.py" "$SITE_PACKAGES/"
cp "${SCRIPT_DIR}/tdd_config.py" "$SITE_PACKAGES/"
cp "${SCRIPT_DIR}/tdd_import_hook.py" "$SITE_PACKAGES/"

# Create global config if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo "📝 Creating default configuration..."
    cat > "$CONFIG_DIR/config.json" << 'EOF'
{
  "enabled": true,
  "strict_mode": false,
  "test_timeout_minutes": 5,
  "require_test_before_run": true,
  "require_test_before_commit": true,
  "allow_repl": true,
  "test_commands": [
    "pytest",
    "python -m pytest",
    "python -m unittest"
  ],
  "coverage": {
    "enabled": true,
    "minimum": 80,
    "fail_under": 70
  },
  "import_hook": {
    "enabled": false,
    "warn_only": true,
    "auto_install": false
  }
}
EOF
fi

# Setup git hooks
echo "🔗 Setting up git hooks..."
if [ -d .git ]; then
    mkdir -p .git/hooks
    if [ ! -f .git/hooks/pre-commit ]; then
        ln -sf "${SCRIPT_DIR}/git-hooks/pre-commit" .git/hooks/
        echo "  ✓ Pre-commit hook installed"
    else
        echo "  ⚠️  Pre-commit hook already exists, skipping"
    fi
    
    if [ ! -f .git/hooks/post-commit ]; then
        ln -sf "${SCRIPT_DIR}/git-hooks/post-commit" .git/hooks/
        echo "  ✓ Post-commit hook installed"
    else
        echo "  ⚠️  Post-commit hook already exists, skipping"
    fi
else
    echo "  ℹ️  Not in a git repository, skipping git hooks"
fi

# Setup Claude Code hooks
echo "🪝 Setting up Claude Code hooks..."

# Determine Claude config directory based on venv
if [ "$VENV_ACTIVE" = true ]; then
    CLAUDE_CONFIG_DIR="$VIRTUAL_ENV/.claude-code"
else
    CLAUDE_CONFIG_DIR="${HOME}/.claude-code"
fi

CLAUDE_HOOKS_DIR="${CLAUDE_CONFIG_DIR}/hooks"

# Check if claude-code-hooks directory exists
if [ -d "${SCRIPT_DIR}/claude-code-hooks" ]; then
    echo "  Installing Claude Code hooks for CLAUDE.md awareness..."
    
    # Create directories
    mkdir -p "$CLAUDE_CONFIG_DIR"
    mkdir -p "$CLAUDE_HOOKS_DIR"
    
    # Copy hook scripts
    cp "${SCRIPT_DIR}/claude-code-hooks/claude-md-tracker.sh" "$CLAUDE_HOOKS_DIR/"
    cp "${SCRIPT_DIR}/claude-code-hooks/post-compaction-reminder.sh" "$CLAUDE_HOOKS_DIR/"
    
    # Make hooks executable
    chmod +x "$CLAUDE_HOOKS_DIR/claude-md-tracker.sh"
    chmod +x "$CLAUDE_HOOKS_DIR/post-compaction-reminder.sh"
    
    # Create or update Claude Code settings
    CLAUDE_SETTINGS_FILE="${CLAUDE_CONFIG_DIR}/settings.json"
    
    if [ -f "$CLAUDE_SETTINGS_FILE" ]; then
        echo "  ⚠️  Claude Code settings already exist at: $CLAUDE_SETTINGS_FILE"
        echo "  Please manually add these hooks to your configuration:"
        echo "    \"Stop\": \"$CLAUDE_HOOKS_DIR/claude-md-tracker.sh\","
        echo "    \"PostToolUse\": \"$CLAUDE_HOOKS_DIR/claude-md-tracker.sh\""
    else
        cat > "$CLAUDE_SETTINGS_FILE" << EOF
{
  "hooks": {
    "Stop": "$CLAUDE_HOOKS_DIR/claude-md-tracker.sh",
    "PostToolUse": "$CLAUDE_HOOKS_DIR/claude-md-tracker.sh"
  }
}
EOF
        echo "  ✓ Claude Code hooks configured in: $CLAUDE_SETTINGS_FILE"
    fi
    
    echo "  ✓ Claude Code hooks installed - will remind to re-read CLAUDE.md after compaction"
else
    echo "  ℹ️  Claude Code hooks directory not found, skipping"
fi

# Setup aliases
echo "🔧 Setting up aliases..."

# Function to add alias to a file
add_alias_to_file() {
    local file="$1"
    local alias_line="alias tdd-python='${INSTALL_DIR}/tdd-python'"
    local comment_line="# alias python='${INSTALL_DIR}/tdd-python'  # Uncomment to make TDD wrapper the default"
    
    # Check if alias already exists
    if grep -q "alias tdd-python=" "$file" 2>/dev/null; then
        echo "  ℹ️  TDD alias already exists in $file"
        return 0
    fi
    
    # Add the alias
    echo "" >> "$file"
    echo "# TDD Python Wrapper" >> "$file"
    echo "$alias_line" >> "$file"
    echo "$comment_line" >> "$file"
    echo "  ✓ Added TDD alias to $file"
}

# Check for virtual environment
VENV_ACTIVATE=""
FOUND_VENV=false

# Check common virtualenv locations
if [ -n "$VIRTUAL_ENV" ]; then
    VENV_ACTIVATE="$VIRTUAL_ENV/bin/activate"
    FOUND_VENV=true
elif [ -f "venv/bin/activate" ]; then
    VENV_ACTIVATE="venv/bin/activate"
    FOUND_VENV=true
elif [ -f ".venv/bin/activate" ]; then
    VENV_ACTIVATE=".venv/bin/activate"
    FOUND_VENV=true
elif [ -f "env/bin/activate" ]; then
    VENV_ACTIVATE="env/bin/activate"
    FOUND_VENV=true
fi

if [ "$FOUND_VENV" = true ]; then
    echo "🐍 Virtual environment detected: $VENV_ACTIVATE"
    add_alias_to_file "$VENV_ACTIVATE"
    echo ""
    echo "  ℹ️  Alias added to virtualenv. Reactivate your environment to use it:"
    echo "     deactivate && source $VENV_ACTIVATE"
else
    echo "⚠️  No virtual environment detected."
    echo ""
    
    # Determine shell config file
    SHELL_RC=""
    if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
        SHELL_RC="${HOME}/.zshrc"
    elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
        SHELL_RC="${HOME}/.bashrc"
    fi
    
    if [ -n "$SHELL_RC" ] && [ -f "$SHELL_RC" ]; then
        echo "  Would you like to add the TDD alias to $SHELL_RC?"
        echo "  This will make 'tdd-python' available globally."
        echo ""
        read -p "  Add alias to $SHELL_RC? [y/N] " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            add_alias_to_file "$SHELL_RC"
            echo "  ℹ️  Restart your shell or run: source $SHELL_RC"
        else
            echo "  ℹ️  Skipping global alias installation."
            echo ""
            echo "  To use TDD wrapper, either:"
            echo "    1. Create a virtualenv and re-run this installer"
            echo "    2. Use the full path: ${INSTALL_DIR}/tdd-python"
            echo "    3. Manually add to your shell config:"
            echo "       alias tdd-python='${INSTALL_DIR}/tdd-python'"
        fi
    else
        echo "  ℹ️  Could not determine shell configuration file."
        echo "  Add this alias manually to your shell config:"
        echo "     alias tdd-python='${INSTALL_DIR}/tdd-python'"
    fi
fi

# Check PATH (only for global installations)
if [ "$VENV_ACTIVE" = false ] && [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  Warning: $INSTALL_DIR is not in your PATH"
    echo "Add the following to your shell configuration:"
    echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
fi

# Check for optional dependencies
echo ""
echo "🔍 Checking optional dependencies..."

# Check for pytest
if ! $PYTHON_EXECUTABLE -c "import pytest" &>/dev/null; then
    echo "  ⚠️  pytest not found - install with: pip install pytest"
fi

# Check for PyYAML
if ! $PYTHON_EXECUTABLE -c "import yaml" &>/dev/null; then
    echo "  ⚠️  PyYAML not found - YAML config support disabled"
    echo "     To enable YAML config files, install with: pip install pyyaml"
fi

echo ""
echo "✅ Installation complete!"
echo ""

if [ "$VENV_ACTIVE" = true ]; then
    echo "📍 Installed in virtual environment: $VIRTUAL_ENV"
    echo ""
    echo "📚 Quick Start:"
    echo "  1. Your virtualenv now has 'tdd-python' available"
    echo "  2. Install pytest if not already: pip install pytest"
    echo "  3. Initialize TDD in your project: tdd-python --init"
    echo "  4. Check TDD status: tdd-python --status"
    echo "  5. View configuration: tdd-python --config"
    echo ""
    echo "🔧 To make TDD the default Python in this venv:"
    echo "  Uncomment the alias line in: $VIRTUAL_ENV/bin/activate"
    echo ""
    echo "🪝 Claude Code hooks:"
    echo "  - Installed to: $CLAUDE_CONFIG_DIR"
    echo "  - Will remind Claude to re-read CLAUDE.md after context compaction"
    echo ""
    echo "⚠️  Note: This installation is specific to this virtual environment"
else
    echo "📍 Installed globally in: $INSTALL_DIR"
    echo ""
    echo "📚 Quick Start:"
    echo "  1. Use 'tdd-python' instead of 'python' to enforce TDD"
    echo "  2. Install pytest if not already: pip install --user pytest"
    echo "  3. Initialize TDD in your project: tdd-python --init"
    echo "  4. Check TDD status: tdd-python --status"
    echo "  5. View configuration: tdd-python --config"
    echo ""
    echo "🔧 To make TDD the default Python:"
    echo "  Uncomment the alias line in your shell configuration"
    echo "  or add: alias python='tdd-python'"
    echo ""
    echo "🪝 Claude Code hooks:"
    echo "  - Installed to: $CLAUDE_CONFIG_DIR"
    echo "  - Will remind Claude to re-read CLAUDE.md after context compaction"
fi

echo ""
echo "📖 For more information, see README.md"