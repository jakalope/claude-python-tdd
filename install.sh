#!/bin/bash
# TDD Wrapper Installation Script

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/tdd"

echo "🚀 Installing Claude TDD Wrapper..."
echo "================================="

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
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
SITE_PACKAGES="${HOME}/.local/lib/python${PYTHON_VERSION}/site-packages"
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

# Create alias for easy use
echo "🔧 Setting up aliases..."
SHELL_RC=""

if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="${HOME}/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="${HOME}/.bashrc"
fi

if [ -n "$SHELL_RC" ] && [ -f "$SHELL_RC" ]; then
    if ! grep -q "alias python=tdd-python" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# TDD Python Wrapper" >> "$SHELL_RC"
        echo "alias tdd-python='${INSTALL_DIR}/tdd-python'" >> "$SHELL_RC"
        echo "# Uncomment to make TDD wrapper the default Python" >> "$SHELL_RC"
        echo "# alias python='${INSTALL_DIR}/tdd-python'" >> "$SHELL_RC"
        echo "  ✓ Added aliases to $SHELL_RC"
    else
        echo "  ℹ️  Aliases already exist in $SHELL_RC"
    fi
fi

# Check PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  Warning: $INSTALL_DIR is not in your PATH"
    echo "Add the following to your shell configuration:"
    echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📚 Quick Start:"
echo "  1. Use 'tdd-python' instead of 'python' to enforce TDD"
echo "  2. Initialize TDD in your project: tdd-python --init"
echo "  3. Check TDD status: tdd-python --status"
echo "  4. View configuration: tdd-python --config"
echo ""
echo "🔧 To make TDD the default Python:"
echo "  Uncomment the alias line in your shell configuration"
echo "  or add: alias python='tdd-python'"
echo ""
echo "📖 For more information, see README.md"