#!/bin/bash
# Quick test script for iterative development

set -e

echo "🧪 TDD Installation Test Script"
echo "=============================="
echo ""

# Save current directory
ORIG_DIR=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create test directory
TEST_DIR="/tmp/tdd-test-$$"
echo "📁 Creating test directory: $TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Create a simple Python project
echo "📝 Creating test Python project..."
cat > calculator.py << 'EOF'
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

if __name__ == "__main__":
    print(f"2 + 3 = {add(2, 3)}")
    print(f"4 * 5 = {multiply(4, 5)}")
EOF

cat > test_calculator.py << 'EOF'
import pytest
from calculator import add, multiply

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_multiply():
    assert multiply(4, 5) == 20
    assert multiply(0, 100) == 0
EOF

# Initialize git repo
echo "🔧 Initializing git repository..."
git init -q
git add .
git commit -q -m "Initial test project"

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install pytest
echo "📦 Installing pytest..."
pip install -q pytest

# Run installer
echo ""
echo "🚀 Running TDD installer..."
echo "y" | "$SCRIPT_DIR/install.sh"

# Test the installation
echo ""
echo "🔍 Testing installation..."

# Check if tdd-python exists
if command -v tdd-python &> /dev/null; then
    echo "✅ tdd-python command found"
else
    echo "❌ tdd-python command not found in PATH"
fi

# Check virtualenv activation script
if grep -q "tdd-python" venv/bin/activate; then
    echo "✅ Alias added to virtualenv"
else
    echo "❌ Alias not found in virtualenv"
fi

# Test TDD functionality
echo ""
echo "📋 Testing TDD enforcement..."

# This should pass (tests exist and pass)
echo "  Testing with passing tests..."
if tdd-python calculator.py &> /dev/null; then
    echo "  ✅ Execution allowed with passing tests"
else
    echo "  ❌ Execution blocked despite passing tests"
fi

# Create a file without tests
cat > no_tests.py << 'EOF'
def untested_function():
    return "This has no tests!"

if __name__ == "__main__":
    print(untested_function())
EOF

# This should fail (no tests)
echo "  Testing without test file..."
if tdd-python no_tests.py &> /dev/null; then
    echo "  ❌ Execution allowed without tests"
else
    echo "  ✅ Execution blocked without tests"
fi

# Test git hooks
echo ""
echo "🔗 Testing git hooks..."
if [ -L .git/hooks/pre-commit ]; then
    echo "✅ Pre-commit hook installed"
else
    echo "❌ Pre-commit hook not installed"
fi

# Test uninstall
echo ""
read -p "Test uninstallation? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Testing uninstallation..."
    echo -e "y\ny\ny" | tdd-python --uninstall
    
    # Verify removal
    if command -v tdd-python &> /dev/null; then
        echo "❌ tdd-python still in PATH after uninstall"
    else
        echo "✅ tdd-python removed from PATH"
    fi
    
    if grep -q "tdd-python" venv/bin/activate; then
        echo "❌ Alias still in virtualenv after uninstall"
    else
        echo "✅ Alias removed from virtualenv"
    fi
fi

# Cleanup
cd "$ORIG_DIR"
echo ""
echo "🧹 Cleaning up test directory..."
rm -rf "$TEST_DIR"

echo ""
echo "✅ Test complete!"