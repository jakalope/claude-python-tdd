# Claude TDD Wrapper

A comprehensive Test-Driven Development (TDD) enforcement wrapper for Python that ensures Claude Code (and other tools) follow proper TDD practices.

## Features

### 🔴 Core TDD Enforcement
- **Test-First Development**: Blocks code execution if tests don't exist or haven't been run
- **Red-Green-Refactor Cycle**: Tracks and enforces proper TDD cycle progression
- **Automatic Test Discovery**: Finds related test files using intelligent patterns
- **Test Status Tracking**: Maintains state of test runs and file modifications

### 📊 Advanced Tracking
- **SQLite Database**: Persistent tracking of TDD compliance
- **Coverage Integration**: Monitors and enforces code coverage thresholds
- **Complexity Analysis**: Tracks code complexity metrics
- **Violation Reporting**: Records and reports TDD violations

### 🔧 Configuration
- **Flexible Configuration**: JSON/YAML config with environment variable overrides
- **Project & Global Settings**: Cascading configuration system
- **Custom Rules**: Define your own TDD rules and enforcement patterns
- **Hook System**: Pre/post test hooks for custom workflows

### 🔗 Integration
- **Git Hooks**: Pre-commit and post-commit hooks for TDD enforcement
- **Import Hook**: Optional Python import hook to check test status
- **Claude Code Compatible**: Designed specifically for AI-assisted development
- **CI/CD Ready**: Integrates with continuous integration pipelines

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-tdd.git
cd claude-tdd

# Run the installation script
./install.sh
```

### Manual Install

1. Copy `tdd-python` to your PATH:
   ```bash
   cp tdd-python ~/.local/bin/
   chmod +x ~/.local/bin/tdd-python
   ```

2. Install Python modules:
   ```bash
   pip install --user .
   ```

3. Initialize in your project:
   ```bash
   tdd-python --init
   ```

## Usage

### Basic Usage

Replace `python` with `tdd-python`:

```bash
# Instead of:
python my_script.py

# Use:
tdd-python my_script.py
```

### Command Line Options

```bash
# Initialize TDD configuration in current directory
tdd-python --init

# Check TDD status
tdd-python --status

# View current configuration
tdd-python --config

# Reset TDD state
tdd-python --reset
```

### Configuration

Create `.tdd-config.json` in your project root:

```json
{
  "strict_mode": true,
  "require_test_before_run": true,
  "test_timeout_minutes": 5,
  "test_patterns": [
    "test_*.py",
    "*_test.py",
    "tests/test_*.py"
  ],
  "test_commands": [
    "pytest",
    "python -m pytest"
  ],
  "coverage": {
    "enabled": true,
    "minimum": 80
  }
}
```

### Environment Variables

Override configuration with environment variables:

```bash
export TDD_STRICT_MODE=true
export TDD_COVERAGE_MINIMUM=90
export TDD_TEST_TIMEOUT_MINUTES=10
```

## TDD Workflow

### 1. Write a Failing Test (RED)

```python
# test_calculator.py
def test_add():
    from calculator import add
    assert add(2, 3) == 5  # This will fail initially
```

### 2. Run with TDD Wrapper

```bash
tdd-python calculator.py
# ❌ TDD Error: No test files found for calculator.py
```

### 3. Make Test Pass (GREEN)

```python
# calculator.py
def add(a, b):
    return a + b
```

### 4. Run Again

```bash
tdd-python calculator.py
# 🧪 Running tests: pytest test_calculator.py
# ✅ Tests passed!
# [Your script runs]
```

### 5. Refactor (BLUE)

Improve your code while keeping tests green.

## Git Integration

### Automatic Setup

The installer sets up git hooks automatically. These hooks:

1. **Pre-commit**: Ensures all staged files have passing tests
2. **Post-commit**: Records successful commits in TDD database

### Manual Git Hook Setup

```bash
# Link the hooks
ln -s /path/to/tdd/git-hooks/pre-commit .git/hooks/
ln -s /path/to/tdd/git-hooks/post-commit .git/hooks/
```

## Advanced Features

### Import Hook

Enable the import hook to check test status when modules are imported:

```json
{
  "import_hook": {
    "enabled": true,
    "warn_only": true,
    "auto_install": true
  }
}
```

### Custom Test Commands

Configure project-specific test runners:

```json
{
  "test_commands": [
    "pytest --cov=myproject",
    "python -m pytest -v",
    "make test"
  ]
}
```

### Exclude Patterns

Skip TDD checks for specific files:

```json
{
  "excluded_files": [
    "setup.py",
    "conftest.py",
    "migrations/*.py"
  ]
}
```

## Reporting

### Generate TDD Report

```python
from tdd_tracker import TDDDatabase, TDDReporter

db = TDDDatabase()
reporter = TDDReporter(db)

# Text report
print(reporter.generate_report('text'))

# JSON report
report_data = reporter.generate_report('json')

# HTML report
with open('tdd-report.html', 'w') as f:
    f.write(reporter.generate_report('html'))
```

## Troubleshooting

### Tests Not Found

Ensure your test files follow naming conventions:
- `test_<module>.py`
- `<module>_test.py`
- `tests/test_<module>.py`

### Permission Denied

Make sure the wrapper is executable:
```bash
chmod +x ~/.local/bin/tdd-python
```

### Import Errors

Add the TDD modules to your Python path:
```bash
export PYTHONPATH="$PYTHONPATH:/path/to/claude-tdd"
```

## Best Practices

1. **Always Write Tests First**: The wrapper enforces this, embrace it!
2. **Keep Tests Fast**: Slow tests discourage TDD
3. **One Assertion Per Test**: Makes failures clear
4. **Test Behavior, Not Implementation**: Focus on what, not how
5. **Refactor Regularly**: Use the green state to improve code

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes (of course!)
4. Make your changes
5. Run tests with `tdd-python`
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Designed specifically for Claude Code integration
- Inspired by test-driven development best practices
- Built with love for clean, tested code