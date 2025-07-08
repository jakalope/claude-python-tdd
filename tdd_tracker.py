#!/usr/bin/env python3
"""
Advanced TDD State Tracker with visualization and reporting
"""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import subprocess

class TDDDatabase:
    """SQLite-based TDD state tracking"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (Path.home() / '.tdd-state' / 'tdd.db')
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_state (
                    filepath TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    last_modified TIMESTAMP,
                    last_tested TIMESTAMP,
                    test_passed BOOLEAN,
                    test_coverage REAL,
                    complexity_score INTEGER
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_file TEXT NOT NULL,
                    target_file TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    passed BOOLEAN,
                    duration_ms INTEGER,
                    error_message TEXT,
                    coverage_percent REAL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tdd_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT NOT NULL,
                    cycle_type TEXT CHECK(cycle_type IN ('red', 'green', 'refactor')),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT NOT NULL,
                    violation_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    severity TEXT CHECK(severity IN ('warning', 'error', 'critical')),
                    message TEXT
                )
            ''')
    
    def record_file_state(self, filepath: str, test_passed: bool, 
                         coverage: Optional[float] = None):
        """Record the current state of a file"""
        file_hash = self._calculate_file_hash(filepath)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO file_state 
                (filepath, file_hash, last_modified, last_tested, test_passed, test_coverage)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filepath, file_hash, datetime.now(), datetime.now(), 
                  test_passed, coverage))
    
    def record_test_run(self, test_file: str, target_file: Optional[str],
                       passed: bool, duration_ms: int, 
                       error_message: Optional[str] = None,
                       coverage: Optional[float] = None):
        """Record a test run"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO test_runs 
                (test_file, target_file, passed, duration_ms, error_message, coverage_percent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (test_file, target_file, passed, duration_ms, error_message, coverage))
    
    def record_tdd_cycle(self, filepath: str, cycle_type: str, details: str = ""):
        """Record TDD cycle progression"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO tdd_cycles (filepath, cycle_type, details)
                VALUES (?, ?, ?)
            ''', (filepath, cycle_type, details))
    
    def record_violation(self, filepath: str, violation_type: str, 
                        severity: str, message: str):
        """Record a TDD violation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO violations (filepath, violation_type, severity, message)
                VALUES (?, ?, ?, ?)
            ''', (filepath, violation_type, severity, message))
    
    def get_file_state(self, filepath: str) -> Optional[Dict]:
        """Get current state of a file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT file_hash, last_modified, last_tested, test_passed, 
                       test_coverage, complexity_score
                FROM file_state WHERE filepath = ?
            ''', (filepath,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'file_hash': row[0],
                    'last_modified': row[1],
                    'last_tested': row[2],
                    'test_passed': row[3],
                    'test_coverage': row[4],
                    'complexity_score': row[5]
                }
        return None
    
    def get_recent_cycles(self, filepath: str, limit: int = 10) -> List[Dict]:
        """Get recent TDD cycles for a file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT cycle_type, timestamp, details
                FROM tdd_cycles 
                WHERE filepath = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (filepath, limit))
            
            return [
                {'cycle_type': row[0], 'timestamp': row[1], 'details': row[2]}
                for row in cursor.fetchall()
            ]
    
    def get_test_history(self, days: int = 7) -> List[Dict]:
        """Get test run history"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT test_file, target_file, timestamp, passed, 
                       duration_ms, coverage_percent
                FROM test_runs
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff,))
            
            return [
                {
                    'test_file': row[0],
                    'target_file': row[1],
                    'timestamp': row[2],
                    'passed': row[3],
                    'duration_ms': row[4],
                    'coverage_percent': row[5]
                }
                for row in cursor.fetchall()
            ]
    
    def get_violation_summary(self) -> Dict[str, int]:
        """Get summary of violations by type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT violation_type, COUNT(*) as count
                FROM violations
                GROUP BY violation_type
                ORDER BY count DESC
            ''')
            
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def needs_test(self, filepath: str) -> Tuple[bool, str]:
        """Check if a file needs testing with reason"""
        if not Path(filepath).exists():
            return True, "File does not exist"
        
        current_hash = self._calculate_file_hash(filepath)
        state = self.get_file_state(filepath)
        
        if not state:
            return True, "No test history found"
        
        if state['file_hash'] != current_hash:
            return True, "File has been modified since last test"
        
        if not state['test_passed']:
            return True, "Previous test failed"
        
        # Check if test is stale
        if state['last_tested']:
            last_tested = datetime.fromisoformat(state['last_tested'])
            if datetime.now() - last_tested > timedelta(hours=1):
                return True, "Test results are stale (>1 hour old)"
        
        return False, "Tests are up to date"
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA256 hash of file content"""
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

class TDDReporter:
    """Generate TDD compliance reports"""
    
    def __init__(self, db: TDDDatabase):
        self.db = db
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate comprehensive TDD report"""
        if output_format == 'json':
            return self._json_report()
        elif output_format == 'html':
            return self._html_report()
        else:
            return self._text_report()
    
    def _text_report(self) -> str:
        """Generate text format report"""
        report = []
        report.append("=" * 60)
        report.append("TDD Compliance Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Test history summary
        history = self.db.get_test_history(days=7)
        if history:
            total_runs = len(history)
            passed_runs = sum(1 for h in history if h['passed'])
            pass_rate = (passed_runs / total_runs) * 100 if total_runs > 0 else 0
            
            report.append(f"Test Runs (Last 7 days): {total_runs}")
            report.append(f"Pass Rate: {pass_rate:.1f}%")
            report.append("")
        
        # Violations summary
        violations = self.db.get_violation_summary()
        if violations:
            report.append("Violations:")
            for vtype, count in violations.items():
                report.append(f"  - {vtype}: {count}")
            report.append("")
        
        # Recent test runs
        report.append("Recent Test Runs:")
        report.append("-" * 40)
        for run in history[:10]:
            status = "PASS" if run['passed'] else "FAIL"
            report.append(f"{run['timestamp']} | {status} | {run['test_file']}")
        
        return "\n".join(report)
    
    def _json_report(self) -> str:
        """Generate JSON format report"""
        history = self.db.get_test_history(days=7)
        violations = self.db.get_violation_summary()
        
        report_data = {
            'generated': datetime.now().isoformat(),
            'summary': {
                'total_runs': len(history),
                'passed_runs': sum(1 for h in history if h['passed']),
                'pass_rate': self._calculate_pass_rate(history)
            },
            'violations': violations,
            'recent_runs': history[:20]
        }
        
        return json.dumps(report_data, indent=2)
    
    def _html_report(self) -> str:
        """Generate HTML format report"""
        history = self.db.get_test_history(days=7)
        pass_rate = self._calculate_pass_rate(history)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TDD Compliance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 20px; 
                          background: #f0f0f0; border-radius: 5px; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>TDD Compliance Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="metrics">
                <div class="metric">
                    <h3>Test Runs (7 days)</h3>
                    <p>{len(history)}</p>
                </div>
                <div class="metric">
                    <h3>Pass Rate</h3>
                    <p class="{'pass' if pass_rate > 80 else 'fail'}">{pass_rate:.1f}%</p>
                </div>
            </div>
            
            <h2>Recent Test Runs</h2>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Status</th>
                    <th>Test File</th>
                    <th>Duration (ms)</th>
                </tr>
        """
        
        for run in history[:20]:
            status_class = 'pass' if run['passed'] else 'fail'
            status_text = 'PASS' if run['passed'] else 'FAIL'
            html += f"""
                <tr>
                    <td>{run['timestamp']}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{run['test_file']}</td>
                    <td>{run.get('duration_ms', 'N/A')}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html
    
    def _calculate_pass_rate(self, history: List[Dict]) -> float:
        """Calculate test pass rate"""
        if not history:
            return 0.0
        passed = sum(1 for h in history if h['passed'])
        return (passed / len(history)) * 100

class TDDEnforcer:
    """Enhanced TDD enforcement with cycle tracking"""
    
    def __init__(self, db: TDDDatabase):
        self.db = db
        self.current_cycle = None
    
    def start_red_phase(self, filepath: str):
        """Start the RED phase - write failing test"""
        self.current_cycle = 'red'
        self.db.record_tdd_cycle(filepath, 'red', 'Writing failing test')
        print("🔴 RED Phase: Write a failing test")
    
    def start_green_phase(self, filepath: str):
        """Start the GREEN phase - make test pass"""
        self.current_cycle = 'green'
        self.db.record_tdd_cycle(filepath, 'green', 'Making test pass')
        print("🟢 GREEN Phase: Make the test pass")
    
    def start_refactor_phase(self, filepath: str):
        """Start the REFACTOR phase - improve code"""
        self.current_cycle = 'refactor'
        self.db.record_tdd_cycle(filepath, 'refactor', 'Refactoring code')
        print("🔵 REFACTOR Phase: Improve the code")
    
    def validate_cycle_transition(self, filepath: str, 
                                 from_phase: str, to_phase: str) -> bool:
        """Validate TDD cycle transitions"""
        valid_transitions = {
            'red': ['green'],
            'green': ['refactor', 'red'],
            'refactor': ['red']
        }
        
        if to_phase in valid_transitions.get(from_phase, []):
            return True
        
        self.db.record_violation(
            filepath, 
            'invalid_cycle_transition',
            'error',
            f"Invalid transition from {from_phase} to {to_phase}"
        )
        return False
    
    def check_test_first(self, filepath: str) -> bool:
        """Ensure test exists before implementation"""
        test_files = self._find_test_files(filepath)
        
        if not test_files:
            self.db.record_violation(
                filepath,
                'no_test_found',
                'critical',
                'No test file found for implementation'
            )
            return False
        
        # Check if test was modified recently
        impl_stat = Path(filepath).stat()
        for test_file in test_files:
            test_stat = Path(test_file).stat()
            if test_stat.st_mtime > impl_stat.st_mtime:
                return True
        
        self.db.record_violation(
            filepath,
            'test_not_recent',
            'warning',
            'Test file not modified before implementation'
        )
        return False
    
    def _find_test_files(self, filepath: str) -> List[str]:
        """Find test files for given implementation file"""
        path = Path(filepath)
        stem = path.stem
        parent = path.parent
        
        patterns = [
            f"test_{stem}.py",
            f"{stem}_test.py",
            f"tests/test_{stem}.py",
            f"tests/{stem}_test.py"
        ]
        
        test_files = []
        for pattern in patterns:
            matches = list(parent.glob(pattern))
            if parent.name != 'tests':
                tests_dir = parent / 'tests'
                if tests_dir.exists():
                    matches.extend(tests_dir.glob(pattern.split('/')[-1]))
            test_files.extend(str(f) for f in matches if f.exists())
        
        return test_files