#!/usr/bin/env python3
"""
Benson Bot Auto-Fix System
"Break, Fix, Automate" Philosophy Implementation

This system automatically detects issues, fixes them, and prevents recurrence
"""

import json
import yaml
import sqlite3
import time
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Issue:
    id: str
    title: str
    description: str
    severity: str  # critical, high, medium, low
    detected_at: datetime
    fixed_at: Optional[datetime] = None
    auto_fix_available: bool = False
    fix_function: Optional[str] = None

class BensonAutoFixSystem:
    """Automated issue detection and resolution system"""
    
    def __init__(self):
        self.issues_db = "benson_autofix.db"
        self.config_yaml = "config/config.yaml"
        self.config_json = "benson_user_config.json"
        self.memory_db = "benson_memory.db"
        
        self.init_autofix_database()
        
        # Known fix patterns
        self.fix_registry = {
            'random_supply_chain_data': self.fix_supply_chain_signals,
            'zero_win_rate_crisis': self.fix_zero_win_rate,
            'high_loss_rate': self.fix_high_losses,
            'signal_weight_imbalance': self.fix_zero_win_rate,  # Use same fix for now
            'learning_engine_inactive': self.fix_zero_win_rate,  # Use same fix for now
            'api_connection_failure': self.fix_supply_chain_signals,  # Use same fix
            'database_lock': self.fix_database_locks,
            'memory_leak': self.fix_database_locks,  # Use same fix for now
            'config_corruption': self.fix_zero_win_rate  # Use conservative fix
        }
    
    def init_autofix_database(self):
        """Initialize the auto-fix tracking database"""
        conn = sqlite3.connect(self.issues_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detected_issues (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                severity TEXT,
                detected_at TEXT,
                fixed_at TEXT,
                fix_method TEXT,
                auto_fixed BOOLEAN,
                recurrence_count INTEGER DEFAULT 1,
                last_occurrence TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fix_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_id TEXT,
                timestamp TEXT,
                fix_attempted TEXT,
                success BOOLEAN,
                details TEXT,
                FOREIGN KEY (issue_id) REFERENCES detected_issues (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prevention_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_pattern TEXT,
                prevention_method TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def detect_issues(self) -> List[Issue]:
        """Comprehensive issue detection across all systems"""
        issues = []
        
        # 1. Trading Performance Issues
        performance_issues = self._detect_performance_issues()
        issues.extend(performance_issues)
        
        # 2. Signal Quality Issues  
        signal_issues = self._detect_signal_issues()
        issues.extend(signal_issues)
        
        # 3. Configuration Issues
        config_issues = self._detect_config_issues()
        issues.extend(config_issues)
        
        # 4. Database Issues
        db_issues = self._detect_database_issues()
        issues.extend(db_issues)
        
        # 5. System Resource Issues
        system_issues = self._detect_system_issues()
        issues.extend(system_issues)
        
        return issues
    
    def _detect_performance_issues(self) -> List[Issue]:
        """Detect trading performance problems"""
        issues = []
        
        try:
            conn = sqlite3.connect(self.memory_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check recent sessions
            cursor.execute('''
                SELECT * FROM trading_sessions 
                ORDER BY timestamp DESC 
                LIMIT 5
            ''')
            sessions = cursor.fetchall()
            
            if sessions:
                # Analyze performance patterns
                zero_win_sessions = 0
                high_loss_sessions = 0
                total_sessions = len(sessions)
                
                for session in sessions:
                    perf_data = json.loads(session['performance_data'])
                    win_rate = perf_data.get('win_rate', 0)
                    total_return = perf_data.get('total_return', 0)
                    
                    if win_rate == 0:
                        zero_win_sessions += 1
                    
                    if total_return < -20:
                        high_loss_sessions += 1
                
                # Issue: Consistent zero win rates
                if zero_win_sessions >= 3:
                    issues.append(Issue(
                        id="zero_win_rate_crisis",
                        title="Critical: Zero Win Rate Crisis",
                        description=f"{zero_win_sessions}/{total_sessions} recent sessions have 0% win rate",
                        severity="critical",
                        detected_at=datetime.now(),
                        auto_fix_available=True,
                        fix_function="fix_zero_win_rate"
                    ))
                
                # Issue: High loss rate
                if high_loss_sessions >= 2:
                    issues.append(Issue(
                        id="high_loss_rate",
                        title="High Loss Rate Detected",
                        description=f"{high_loss_sessions}/{total_sessions} sessions with >20% losses",
                        severity="high", 
                        detected_at=datetime.now(),
                        auto_fix_available=True,
                        fix_function="fix_high_losses"
                    ))
            
            conn.close()
            
        except Exception as e:
            issues.append(Issue(
                id="database_access_error",
                title="Database Access Error",
                description=f"Cannot read performance data: {e}",
                severity="high",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_function="fix_database_locks"
            ))
        
        return issues
    
    def _detect_signal_issues(self) -> List[Issue]:
        """Detect signal quality and configuration issues"""
        issues = []
        
        try:
            # Check supply chain signals
            from signals.supply_chain_signals import SupplyChainSignals, SupplyChainSignalsConfig
            
            config = SupplyChainSignalsConfig(enabled=True, region="global", sensitivity=1.0)
            signals = SupplyChainSignals(config)
            
            composite, logs = signals.composite()
            
            # Check for random/placeholder data
            if logs.get('note', '').find('random') != -1 or logs.get('source') == 'intelligent_estimation':
                issues.append(Issue(
                    id="random_supply_chain_data",
                    title="Supply Chain Using Fallback Data",
                    description="Supply chain signals not using real market data",
                    severity="medium",
                    detected_at=datetime.now(),
                    auto_fix_available=True,
                    fix_function="fix_supply_chain_signals"
                ))
        
        except Exception as e:
            issues.append(Issue(
                id="signal_system_error",
                title="Signal System Error",
                description=f"Cannot test signal systems: {e}",
                severity="high",
                detected_at=datetime.now(),
                auto_fix_available=False
            ))
        
        return issues
    
    def _detect_config_issues(self) -> List[Issue]:
        """Detect configuration file problems"""
        issues = []
        
        # Check YAML config
        try:
            with open(self.config_yaml, 'r') as f:
                yaml_config = yaml.safe_load(f)
        except Exception as e:
            issues.append(Issue(
                id="yaml_config_corruption",
                title="YAML Config File Corrupted",
                description=f"Cannot parse config.yaml: {e}",
                severity="critical",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_function="fix_config_files"
            ))
        
        # Check JSON config
        try:
            with open(self.config_json, 'r') as f:
                json_config = json.load(f)
        except Exception as e:
            issues.append(Issue(
                id="json_config_corruption", 
                title="JSON Config File Corrupted",
                description=f"Cannot parse benson_user_config.json: {e}",
                severity="critical",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_function="fix_config_files"
            ))
        
        return issues
    
    def _detect_database_issues(self) -> List[Issue]:
        """Detect database problems"""
        issues = []
        
        # Check for database locks
        db_files = ['benson_memory.db', 'benson_patterns.db', 'benson_analytics.db']
        
        for db_file in db_files:
            if os.path.exists(db_file):
                try:
                    conn = sqlite3.connect(db_file, timeout=1.0)
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    conn.close()
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e):
                        issues.append(Issue(
                            id=f"database_lock_{db_file}",
                            title=f"Database Locked: {db_file}",
                            description=f"Database {db_file} is locked and cannot be accessed",
                            severity="high",
                            detected_at=datetime.now(),
                            auto_fix_available=True,
                            fix_function="fix_database_locks"
                        ))
        
        return issues
    
    def _detect_system_issues(self) -> List[Issue]:
        """Detect system resource and process issues"""
        issues = []
        
        # Check if training processes are hanging
        try:
            result = subprocess.run(['pgrep', '-f', 'rapid_fire_trainer'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                # Process is running, check if it's been running too long
                pid = result.stdout.strip()
                if pid:
                    # Get process start time
                    ps_result = subprocess.run(['ps', '-o', 'etime=', '-p', pid],
                                            capture_output=True, text=True)
                    if ps_result.returncode == 0:
                        runtime = ps_result.stdout.strip()
                        # If running more than 3 hours, might be hanging
                        if ':' in runtime:
                            parts = runtime.split(':')
                            if len(parts) >= 3 or (len(parts) == 2 and int(parts[0]) > 180):
                                issues.append(Issue(
                                    id="training_process_hanging",
                                    title="Training Process May Be Hanging",
                                    description=f"Training process running for {runtime}",
                                    severity="medium",
                                    detected_at=datetime.now(),
                                    auto_fix_available=False
                                ))
        except:
            pass
        
        return issues
    
    def fix_supply_chain_signals(self, issue: Issue) -> bool:
        """Fix supply chain signal data issues"""
        try:
            print(f"🔧 FIXING: {issue.title}")
            
            # Run our existing supply chain manager
            result = subprocess.run(['python', 'supply_chain_manager.py', 'auto'],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Supply chain signals auto-fixed")
                return True
            else:
                print(f"❌ Auto-fix failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            return False
    
    def fix_zero_win_rate(self, issue: Issue) -> bool:
        """Fix zero win rate crisis"""
        try:
            print(f"🔧 FIXING: {issue.title}")
            
            # Implement emergency trading parameter adjustments
            fixes_applied = []
            
            # 1. Loosen RSI thresholds
            with open(self.config_yaml, 'r') as f:
                config = yaml.safe_load(f)
            
            original_buy = config.get('rsi', {}).get('buy_threshold', 35)
            original_sell = config.get('rsi', {}).get('sell_threshold', 65)
            
            # Make more conservative (less trades, higher quality)
            config['rsi']['buy_threshold'] = max(25, original_buy - 5)
            config['rsi']['sell_threshold'] = min(75, original_sell + 5)
            
            with open(self.config_yaml, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            fixes_applied.append(f"RSI thresholds: {original_buy}→{config['rsi']['buy_threshold']}, {original_sell}→{config['rsi']['sell_threshold']}")
            
            # 2. Reduce position sizes (more conservative)
            if 'paper_trading' in config:
                original_pos_size = config['paper_trading'].get('position_size_pct', 18.0)
                config['paper_trading']['position_size_pct'] = max(5.0, original_pos_size * 0.7)
                
                with open(self.config_yaml, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, indent=2)
                
                fixes_applied.append(f"Position size: {original_pos_size}%→{config['paper_trading']['position_size_pct']}%")
            
            print(f"✅ Applied fixes: {', '.join(fixes_applied)}")
            return True
            
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            return False
    
    def fix_high_losses(self, issue: Issue) -> bool:
        """Fix high loss rate issues"""
        try:
            print(f"🔧 FIXING: {issue.title}")
            
            # Tighten stop losses and take profits
            with open(self.config_yaml, 'r') as f:
                config = yaml.safe_load(f)
            
            if 'paper_trading' in config:
                # Tighten stop loss
                original_stop = config['paper_trading'].get('stop_loss_pct', 4.0)
                config['paper_trading']['stop_loss_pct'] = max(2.0, original_stop * 0.8)
                
                # Lower take profit (take profits sooner)
                original_profit = config['paper_trading'].get('take_profit_pct', 8.0)
                config['paper_trading']['take_profit_pct'] = max(4.0, original_profit * 0.8)
                
                with open(self.config_yaml, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, indent=2)
                
                print(f"✅ Tightened stops: {original_stop}%→{config['paper_trading']['stop_loss_pct']}%")
                print(f"✅ Lowered profit target: {original_profit}%→{config['paper_trading']['take_profit_pct']}%")
                return True
            
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            return False
    
    def fix_database_locks(self, issue: Issue) -> bool:
        """Fix database lock issues"""
        try:
            print(f"🔧 FIXING: {issue.title}")
            
            # Kill any processes that might be locking databases
            subprocess.run(['pkill', '-f', 'sqlite'], capture_output=True)
            
            # Wait a moment
            time.sleep(2)
            
            # Test database access
            db_files = ['benson_memory.db', 'benson_patterns.db']
            for db_file in db_files:
                if os.path.exists(db_file):
                    try:
                        conn = sqlite3.connect(db_file, timeout=1.0)
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        conn.close()
                        print(f"✅ {db_file} access restored")
                    except:
                        print(f"⚠️ {db_file} still locked")
                        return False
            
            return True
            
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            return False
    
    def log_issue(self, issue: Issue):
        """Log detected issue to database"""
        conn = sqlite3.connect(self.issues_db)
        cursor = conn.cursor()
        
        # Check if this issue already exists
        cursor.execute('''
            SELECT recurrence_count FROM detected_issues WHERE id = ?
        ''', (issue.id,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update recurrence count
            cursor.execute('''
                UPDATE detected_issues 
                SET recurrence_count = recurrence_count + 1,
                    last_occurrence = ?
                WHERE id = ?
            ''', (issue.detected_at.isoformat(), issue.id))
        else:
            # Insert new issue
            cursor.execute('''
                INSERT INTO detected_issues 
                (id, title, description, severity, detected_at, last_occurrence)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (issue.id, issue.title, issue.description, issue.severity,
                 issue.detected_at.isoformat(), issue.detected_at.isoformat()))
        
        conn.commit()
        conn.close()
    
    def auto_fix_issues(self, issues: List[Issue]) -> Dict:
        """Automatically fix all fixable issues"""
        results = {
            'total_issues': len(issues),
            'fixed': 0,
            'failed': 0,
            'not_fixable': 0,
            'details': []
        }
        
        for issue in issues:
            self.log_issue(issue)
            
            if issue.auto_fix_available and issue.fix_function:
                fix_func = self.fix_registry.get(issue.id)
                if fix_func:
                    try:
                        success = fix_func(issue)
                        if success:
                            results['fixed'] += 1
                            results['details'].append(f"✅ Fixed: {issue.title}")
                        else:
                            results['failed'] += 1
                            results['details'].append(f"❌ Failed to fix: {issue.title}")
                    except Exception as e:
                        results['failed'] += 1
                        results['details'].append(f"❌ Error fixing {issue.title}: {e}")
                else:
                    results['not_fixable'] += 1
                    results['details'].append(f"⚠️ No fix method for: {issue.title}")
            else:
                results['not_fixable'] += 1
                results['details'].append(f"ℹ️ Manual intervention needed: {issue.title}")
        
        return results
    
    def run_auto_fix_cycle(self) -> Dict:
        """Complete auto-fix cycle: detect, fix, report"""
        print("🤖 BENSON AUTO-FIX SYSTEM STARTING")
        print("=" * 50)
        
        # Detect issues
        print("🔍 Detecting issues...")
        issues = self.detect_issues()
        
        print(f"📊 Found {len(issues)} issues:")
        for issue in issues:
            severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "🔶", "low": "ℹ️"}
            print(f"   {severity_emoji.get(issue.severity, '🔶')} {issue.title}")
        
        # Auto-fix issues
        if issues:
            print(f"\n🔧 Attempting to fix {len(issues)} issues...")
            results = self.auto_fix_issues(issues)
            
            print(f"\n📈 RESULTS:")
            print(f"   ✅ Fixed: {results['fixed']}")
            print(f"   ❌ Failed: {results['failed']}")
            print(f"   ⚠️ Need manual intervention: {results['not_fixable']}")
            
            print(f"\n📋 DETAILS:")
            for detail in results['details']:
                print(f"   {detail}")
            
            return results
        else:
            print("✅ No issues detected - system healthy!")
            return {'total_issues': 0, 'system_healthy': True}

def main():
    """Command line interface for auto-fix system"""
    import sys
    
    auto_fix = BensonAutoFixSystem()
    
    if len(sys.argv) < 2:
        print("🤖 BENSON AUTO-FIX SYSTEM")
        print("=" * 30)
        print("Commands:")
        print("  detect    - Detect issues only")
        print("  fix       - Detect and fix issues") 
        print("  status    - Show issue history")
        print("  monitor   - Continuous monitoring mode")
        return
    
    command = sys.argv[1].lower()
    
    if command == "detect":
        issues = auto_fix.detect_issues()
        print(f"🔍 Detected {len(issues)} issues")
        for issue in issues:
            print(f"   • {issue.title} ({issue.severity})")
    
    elif command == "fix":
        auto_fix.run_auto_fix_cycle()
    
    elif command == "monitor":
        print("🔄 Starting continuous monitoring...")
        while True:
            auto_fix.run_auto_fix_cycle()
            print(f"\n⏳ Waiting 5 minutes before next check...")
            time.sleep(300)  # 5 minutes
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()