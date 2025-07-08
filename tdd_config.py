#!/usr/bin/env python3
"""
TDD Configuration Management
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

class TDDConfig:
    """Manage TDD configuration with inheritance and overrides"""
    
    DEFAULT_CONFIG = {
        'enabled': True,
        'strict_mode': True,
        'test_timeout_minutes': 5,
        'require_test_before_run': True,
        'require_test_before_commit': True,
        'allow_repl': True,
        'allow_notebooks': False,
        
        'test_patterns': [
            'test_*.py',
            '*_test.py',
            'tests.py',
            'tests/test_*.py',
            'tests/*_test.py'
        ],
        
        'test_commands': [
            'pytest',
            'python -m pytest',
            'python -m unittest',
            'nose2',
            'python -m nose2'
        ],
        
        'excluded_files': [
            'setup.py',
            'conftest.py',
            '__init__.py',
            'test_*.py',
            '*_test.py'
        ],
        
        'excluded_dirs': [
            '__pycache__',
            '.git',
            '.tox',
            '.pytest_cache',
            'venv',
            'env',
            '.venv',
            'node_modules'
        ],
        
        'coverage': {
            'enabled': True,
            'minimum': 80,
            'fail_under': 70,
            'omit': [
                '*/tests/*',
                '*/test_*',
                '*_test.py',
                '*/venv/*',
                '*/env/*'
            ]
        },
        
        'complexity': {
            'enabled': True,
            'max_complexity': 10,
            'ignore_dirs': ['tests', 'migrations']
        },
        
        'hooks': {
            'pre_test': [],
            'post_test': [],
            'pre_run': [],
            'test_failed': ['echo "Tests failed! Fix them before proceeding."'],
            'violation': []
        },
        
        'notifications': {
            'enabled': False,
            'channels': ['console'],
            'on_success': True,
            'on_failure': True
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.cwd() / '.tdd-config.json'
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration with inheritance"""
        config = self.DEFAULT_CONFIG.copy()
        
        # Load global config
        global_config = self._load_global_config()
        if global_config:
            config = self._merge_configs(config, global_config)
        
        # Load project config
        if self.config_path.exists():
            project_config = self._load_file(self.config_path)
            config = self._merge_configs(config, project_config)
        
        # Load environment overrides
        env_config = self._load_env_config()
        if env_config:
            config = self._merge_configs(config, env_config)
        
        return config
    
    def save_config(self, config: Optional[Dict] = None):
        """Save configuration to file"""
        config = config or self.config
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default=None):
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value):
        """Set configuration value with dot notation support"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def validate(self) -> List[str]:
        """Validate configuration"""
        errors = []
        
        # Check test commands
        test_commands = self.get('test_commands', [])
        if not test_commands:
            errors.append("No test commands configured")
        
        # Check coverage settings
        if self.get('coverage.enabled'):
            min_coverage = self.get('coverage.minimum', 0)
            fail_under = self.get('coverage.fail_under', 0)
            
            if min_coverage < fail_under:
                errors.append("coverage.minimum should be >= coverage.fail_under")
        
        # Check hook commands
        for hook_name, commands in self.get('hooks', {}).items():
            if not isinstance(commands, list):
                errors.append(f"Hook '{hook_name}' must be a list of commands")
        
        return errors
    
    def _load_file(self, path: Path) -> Dict:
        """Load configuration from file"""
        if not path.exists():
            return {}
        
        if path.suffix == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        elif path.suffix in ['.yml', '.yaml']:
            if HAS_YAML:
                with open(path, 'r') as f:
                    return yaml.safe_load(f) or {}
            else:
                print(f"Warning: PyYAML not installed, skipping {path}")
                return {}
        
        return {}
    
    def _load_global_config(self) -> Optional[Dict]:
        """Load global configuration from user home"""
        global_paths = [
            Path.home() / '.tdd-config.json',
            Path.home() / '.config' / 'tdd' / 'config.json',
            Path('/etc/tdd/config.json')
        ]
        
        for path in global_paths:
            if path.exists():
                return self._load_file(path)
        
        return None
    
    def _load_env_config(self) -> Dict:
        """Load configuration from environment variables"""
        config = {}
        prefix = 'TDD_'
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert TDD_COVERAGE_ENABLED to coverage.enabled
                config_key = key[len(prefix):].lower().replace('_', '.')
                
                # Try to parse JSON values
                try:
                    config_value = json.loads(value)
                except json.JSONDecodeError:
                    # Handle boolean strings
                    if value.lower() in ['true', 'false']:
                        config_value = value.lower() == 'true'
                    else:
                        config_value = value
                
                # Build nested dictionary
                keys = config_key.split('.')
                current = config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = config_value
        
        return config
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result

class TDDRules:
    """Define and enforce TDD rules"""
    
    def __init__(self, config: TDDConfig):
        self.config = config
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Dict]:
        """Load TDD rules from configuration"""
        default_rules = [
            {
                'name': 'test_first',
                'description': 'Tests must be written before implementation',
                'enabled': True,
                'severity': 'error'
            },
            {
                'name': 'test_coverage',
                'description': 'Code coverage must meet minimum threshold',
                'enabled': self.config.get('coverage.enabled', True),
                'severity': 'warning',
                'params': {
                    'minimum': self.config.get('coverage.minimum', 80)
                }
            },
            {
                'name': 'test_naming',
                'description': 'Test files must follow naming conventions',
                'enabled': True,
                'severity': 'warning'
            },
            {
                'name': 'complexity_limit',
                'description': 'Code complexity must not exceed threshold',
                'enabled': self.config.get('complexity.enabled', True),
                'severity': 'warning',
                'params': {
                    'max_complexity': self.config.get('complexity.max_complexity', 10)
                }
            },
            {
                'name': 'test_isolation',
                'description': 'Tests must be isolated and not depend on external state',
                'enabled': True,
                'severity': 'error'
            }
        ]
        
        # Load custom rules from config
        custom_rules = self.config.get('custom_rules', [])
        return default_rules + custom_rules
    
    def check_rule(self, rule_name: str, context: Dict) -> Optional[str]:
        """Check if a specific rule is violated"""
        rule = next((r for r in self.rules if r['name'] == rule_name), None)
        
        if not rule or not rule.get('enabled', True):
            return None
        
        # Rule-specific checks
        if rule_name == 'test_first':
            return self._check_test_first(context)
        elif rule_name == 'test_coverage':
            return self._check_coverage(context, rule.get('params', {}))
        elif rule_name == 'test_naming':
            return self._check_naming(context)
        elif rule_name == 'complexity_limit':
            return self._check_complexity(context, rule.get('params', {}))
        
        return None
    
    def _check_test_first(self, context: Dict) -> Optional[str]:
        """Check if test was written before implementation"""
        impl_file = context.get('implementation_file')
        test_file = context.get('test_file')
        
        if not impl_file or not test_file:
            return None
        
        impl_stat = Path(impl_file).stat()
        test_stat = Path(test_file).stat()
        
        if impl_stat.st_mtime < test_stat.st_mtime:
            return "Implementation was modified before test"
        
        return None
    
    def _check_coverage(self, context: Dict, params: Dict) -> Optional[str]:
        """Check if coverage meets threshold"""
        coverage = context.get('coverage_percent')
        minimum = params.get('minimum', 80)
        
        if coverage is not None and coverage < minimum:
            return f"Coverage {coverage}% is below minimum {minimum}%"
        
        return None
    
    def _check_naming(self, context: Dict) -> Optional[str]:
        """Check if test files follow naming conventions"""
        test_file = context.get('test_file')
        if not test_file:
            return None
        
        path = Path(test_file)
        patterns = self.config.get('test_patterns', [])
        
        for pattern in patterns:
            if path.match(pattern):
                return None
        
        return f"Test file '{test_file}' doesn't match naming patterns"
    
    def _check_complexity(self, context: Dict, params: Dict) -> Optional[str]:
        """Check code complexity"""
        complexity = context.get('complexity_score')
        max_complexity = params.get('max_complexity', 10)
        
        if complexity is not None and complexity > max_complexity:
            return f"Complexity {complexity} exceeds maximum {max_complexity}"
        
        return None