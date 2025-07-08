#!/usr/bin/env python3
"""
Custom Python import hook for TDD enforcement
"""

import sys
import importlib.abc
import importlib.machinery
import importlib.util
from pathlib import Path
from typing import Optional
import warnings

from tdd_tracker import TDDDatabase
from tdd_config import TDDConfig

class TDDImportHook(importlib.abc.MetaPathFinder):
    """Import hook that enforces TDD practices"""
    
    def __init__(self):
        self.db = TDDDatabase()
        self.config = TDDConfig()
        self.enabled = self.config.get('import_hook.enabled', False)
        self.warn_only = self.config.get('import_hook.warn_only', True)
        self.checked_modules = set()
    
    def find_spec(self, fullname, path, target=None):
        """Called when Python tries to import a module"""
        if not self.enabled:
            return None
        
        # Skip if already checked
        if fullname in self.checked_modules:
            return None
        
        # Skip standard library and third-party modules
        if self._is_stdlib_or_thirdparty(fullname):
            return None
        
        # Find the actual module file
        spec = self._find_module_spec(fullname, path)
        if not spec or not spec.origin:
            return None
        
        module_file = Path(spec.origin)
        
        # Skip if not a Python file or doesn't exist
        if not module_file.suffix == '.py' or not module_file.exists():
            return None
        
        # Check if it's a test file
        if self._is_test_file(module_file):
            return None
        
        # Check TDD compliance
        needs_test, reason = self.db.needs_test(str(module_file))
        
        if needs_test:
            self._handle_violation(fullname, module_file, reason)
        
        self.checked_modules.add(fullname)
        return None  # Let normal import continue
    
    def _find_module_spec(self, fullname, path):
        """Find the module spec using standard finders"""
        for finder in sys.meta_path:
            if finder is self:
                continue
            if hasattr(finder, 'find_spec'):
                spec = finder.find_spec(fullname, path)
                if spec:
                    return spec
        return None
    
    def _is_stdlib_or_thirdparty(self, fullname):
        """Check if module is from standard library or third-party"""
        # Simple heuristic: check if it starts with known prefixes
        stdlib_prefixes = [
            'os', 'sys', 'json', 'pathlib', 'datetime', 'collections',
            'itertools', 'functools', 'typing', 're', 'math', 'random',
            'subprocess', 'threading', 'multiprocessing', 'asyncio'
        ]
        
        thirdparty_prefixes = [
            'numpy', 'pandas', 'matplotlib', 'requests', 'flask', 'django',
            'pytest', 'setuptools', 'pip', 'wheel'
        ]
        
        root = fullname.split('.')[0]
        return root in stdlib_prefixes or root in thirdparty_prefixes
    
    def _is_test_file(self, filepath: Path):
        """Check if file is a test file"""
        patterns = self.config.get('test_patterns', [])
        for pattern in patterns:
            if filepath.match(pattern):
                return True
        return False
    
    def _handle_violation(self, module_name, module_file, reason):
        """Handle TDD violation during import"""
        message = (
            f"TDD Warning: Importing '{module_name}' from {module_file}\n"
            f"Reason: {reason}\n"
            f"Run tests before importing this module!"
        )
        
        if self.warn_only:
            warnings.warn(message, TDDWarning, stacklevel=3)
            self.db.record_violation(
                str(module_file),
                'import_without_test',
                'warning',
                f"Module imported without passing tests: {reason}"
            )
        else:
            self.db.record_violation(
                str(module_file),
                'import_without_test',
                'error',
                f"Import blocked - tests required: {reason}"
            )
            raise TDDImportError(message)

class TDDWarning(UserWarning):
    """Warning for TDD violations"""
    pass

class TDDImportError(ImportError):
    """Error raised when import is blocked due to TDD violation"""
    pass

def install_import_hook():
    """Install the TDD import hook"""
    hook = TDDImportHook()
    if hook.enabled and hook not in sys.meta_path:
        # Insert after built-in importers but before others
        sys.meta_path.insert(2, hook)
        print("🔗 TDD import hook installed")
    return hook

def uninstall_import_hook():
    """Remove the TDD import hook"""
    sys.meta_path = [
        finder for finder in sys.meta_path 
        if not isinstance(finder, TDDImportHook)
    ]
    print("🔗 TDD import hook removed")

class TDDContext:
    """Context manager for temporary TDD enforcement"""
    
    def __init__(self, enabled=True, warn_only=True):
        self.enabled = enabled
        self.warn_only = warn_only
        self.hook = None
        self.original_enabled = None
        self.original_warn_only = None
    
    def __enter__(self):
        self.hook = TDDImportHook()
        self.original_enabled = self.hook.enabled
        self.original_warn_only = self.hook.warn_only
        
        self.hook.enabled = self.enabled
        self.hook.warn_only = self.warn_only
        
        if self.hook not in sys.meta_path:
            sys.meta_path.insert(2, self.hook)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.hook:
            self.hook.enabled = self.original_enabled
            self.hook.warn_only = self.original_warn_only
            
            if not self.original_enabled:
                sys.meta_path = [
                    f for f in sys.meta_path 
                    if f is not self.hook
                ]

# Automatic installation if configured
if __name__ != '__main__':
    config = TDDConfig()
    if config.get('import_hook.auto_install', False):
        install_import_hook()