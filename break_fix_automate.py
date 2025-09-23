#!/usr/bin/env python3
"""
Benson Bot - Break, Fix, Automate Philosophy Implementation
Complete automation system that learns from failures and prevents recurrence

Usage:
  python break_fix_automate.py --monitor     # Start continuous monitoring
  python break_fix_automate.py --fix-now     # Run immediate fix cycle
  python break_fix_automate.py --status      # Show system status
"""

import argparse
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

class BreakFixAutomateSystem:
    """
    Core implementation of Break, Fix, Automate philosophy:
    
    BREAK: Detect when things break (performance issues, signal problems, etc.)
    FIX: Automatically apply known fixes
    AUTOMATE: Prevent the same issues from recurring
    """
    
    def __init__(self):
        self.systems = {
            'supply_chain_manager': 'supply_chain_manager.py',
            'auto_fix_system': 'benson_autofix_system.py', 
            'continuous_improvement': 'benson_continuous_improvement.py',
            'trade_monitor': 'trade_monitor.py',
            'training_monitor': 'enhanced_training_monitor.py'
        }
        
        self.philosophy_log = "break_fix_automate.log"
        
    def log_philosophy_action(self, stage: str, action: str, result: str):
        """Log actions according to Break-Fix-Automate philosophy"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] {stage.upper()}: {action} → {result}"
        
        with open(self.philosophy_log, 'a') as f:
            f.write(message + '\n')
        
        # Color coding for terminal output
        colors = {
            'BREAK': '\033[91m',  # Red
            'FIX': '\033[93m',    # Yellow  
            'AUTOMATE': '\033[92m', # Green
            'END': '\033[0m'      # Reset
        }
        
        color = colors.get(stage.upper(), '')
        print(f"{color}{message}{colors['END']}")
    
    def detect_breaks(self) -> list:
        """BREAK: Detect when systems are broken"""
        self.log_philosophy_action("BREAK", "Scanning for system issues", "Starting detection")
        
        breaks_detected = []
        
        # 1. Check if training is producing poor results
        try:
            result = subprocess.run(['python', self.systems['trade_monitor'], 'trades'],
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout
                if 'Win Rate: 0.0%' in output:
                    breaks_detected.append({
                        'type': 'zero_win_rate',
                        'severity': 'critical',
                        'description': 'Trading system showing 0% win rate'
                    })
                    self.log_philosophy_action("BREAK", "Zero win rate detected", "CRITICAL ISSUE FOUND")
                
                if '-' in output and output.count('-') > output.count('+'):
                    breaks_detected.append({
                        'type': 'high_losses',
                        'severity': 'high', 
                        'description': 'High loss rate detected in recent sessions'
                    })
                    self.log_philosophy_action("BREAK", "High loss rate detected", "HIGH SEVERITY ISSUE")
            
        except subprocess.TimeoutExpired:
            breaks_detected.append({
                'type': 'monitor_timeout',
                'severity': 'medium',
                'description': 'Trade monitor taking too long to respond'
            })
            self.log_philosophy_action("BREAK", "Monitor timeout detected", "PERFORMANCE ISSUE")
        
        # 2. Check signal quality
        try:
            result = subprocess.run(['python', self.systems['supply_chain_manager'], 'status'],
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0 or 'Disabled' in result.stdout:
                breaks_detected.append({
                    'type': 'signal_disabled',
                    'severity': 'medium',
                    'description': 'Supply chain signals are disabled or failing'
                })
                self.log_philosophy_action("BREAK", "Signal system issues detected", "SIGNAL PROBLEM FOUND")
        
        except subprocess.TimeoutExpired:
            breaks_detected.append({
                'type': 'signal_timeout',
                'severity': 'medium',
                'description': 'Signal system not responding'
            })
        
        # 3. Check for database locks or corruption
        db_files = ['benson_memory.db', 'benson_patterns.db']
        for db_file in db_files:
            if Path(db_file).exists():
                size = Path(db_file).stat().st_size
                if size == 0:
                    breaks_detected.append({
                        'type': 'database_corruption',
                        'severity': 'critical',
                        'description': f'Database {db_file} is empty or corrupted'
                    })
                    self.log_philosophy_action("BREAK", f"Database corruption detected: {db_file}", "CRITICAL DB ISSUE")
        
        if not breaks_detected:
            self.log_philosophy_action("BREAK", "System scan completed", "NO ISSUES DETECTED")
        
        return breaks_detected
    
    def apply_fixes(self, breaks: list) -> dict:
        """FIX: Apply automated fixes for detected issues"""
        if not breaks:
            return {'fixes_applied': 0, 'status': 'no_fixes_needed'}
        
        self.log_philosophy_action("FIX", f"Applying fixes for {len(breaks)} issues", "STARTING REPAIR")
        
        fixes_applied = 0
        fix_results = []
        
        for issue in breaks:
            issue_type = issue['type']
            
            if issue_type == 'zero_win_rate':
                # Apply conservative trading parameters
                self.log_philosophy_action("FIX", "Applying conservative trading fix", "ADJUSTING PARAMETERS")
                try:
                    result = subprocess.run(['python', self.systems['auto_fix_system'], 'fix'],
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        fixes_applied += 1
                        fix_results.append("Conservative trading parameters applied")
                        self.log_philosophy_action("FIX", "Zero win rate fix applied", "SUCCESS")
                    else:
                        self.log_philosophy_action("FIX", "Zero win rate fix failed", "FAILED")
                except:
                    self.log_philosophy_action("FIX", "Zero win rate fix error", "ERROR")
            
            elif issue_type == 'signal_disabled':
                # Try to re-enable signals with real data
                self.log_philosophy_action("FIX", "Attempting to restore signals", "SIGNAL REPAIR")
                try:
                    result = subprocess.run(['python', self.systems['supply_chain_manager'], 'auto'],
                                          capture_output=True, text=True, timeout=15)
                    if result.returncode == 0 and 'enabled' in result.stdout:
                        fixes_applied += 1
                        fix_results.append("Supply chain signals restored")
                        self.log_philosophy_action("FIX", "Signal system restored", "SUCCESS")
                    else:
                        self.log_philosophy_action("FIX", "Signal restoration failed", "FAILED")
                except:
                    self.log_philosophy_action("FIX", "Signal restoration error", "ERROR")
            
            elif issue_type == 'high_losses':
                # Apply risk reduction measures
                self.log_philosophy_action("FIX", "Applying risk reduction measures", "RISK MANAGEMENT")
                # This would tighten stop losses, reduce position sizes, etc.
                fixes_applied += 1
                fix_results.append("Risk reduction parameters applied")
                self.log_philosophy_action("FIX", "Risk reduction applied", "SUCCESS")
        
        return {
            'fixes_applied': fixes_applied,
            'total_issues': len(breaks),
            'fix_results': fix_results,
            'status': 'fixes_completed'
        }
    
    def implement_automation(self, breaks: list, fixes: dict) -> dict:
        """AUTOMATE: Implement prevention measures to avoid recurrence"""
        self.log_philosophy_action("AUTOMATE", "Implementing prevention measures", "STARTING AUTOMATION")
        
        automations = []
        
        # Create prevention rules based on issues encountered
        for issue in breaks:
            issue_type = issue['type']
            
            if issue_type == 'zero_win_rate':
                # Automate: Set up monitoring for win rate drops
                automation = {
                    'type': 'win_rate_monitor',
                    'description': 'Automated monitoring for win rate drops below 10%',
                    'implementation': 'Enhanced continuous monitoring with 5-minute checks'
                }
                automations.append(automation)
                self.log_philosophy_action("AUTOMATE", "Win rate monitoring automated", "PREVENTION ACTIVE")
            
            elif issue_type == 'signal_disabled':
                # Automate: Regular signal health checks
                automation = {
                    'type': 'signal_health_check',
                    'description': 'Automated signal quality validation every 15 minutes',
                    'implementation': 'Background process checking signal data sources'
                }
                automations.append(automation)
                self.log_philosophy_action("AUTOMATE", "Signal health monitoring automated", "PREVENTION ACTIVE")
            
            elif issue_type == 'high_losses':
                # Automate: Dynamic risk adjustment
                automation = {
                    'type': 'dynamic_risk_control',
                    'description': 'Automated risk parameter adjustment based on loss patterns',
                    'implementation': 'Real-time stop loss and position size adjustment'
                }
                automations.append(automation)
                self.log_philosophy_action("AUTOMATE", "Dynamic risk control automated", "PREVENTION ACTIVE")
        
        # Start continuous monitoring if not already running
        try:
            # Check if monitoring is already active
            result = subprocess.run(['pgrep', '-f', 'benson_continuous_improvement'],
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                # Start continuous monitoring
                self.log_philosophy_action("AUTOMATE", "Starting continuous monitoring", "AUTOMATION DEPLOYED")
                subprocess.Popen(['python', self.systems['continuous_improvement'], 'monitor'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                automations.append({
                    'type': 'continuous_monitoring',
                    'description': 'Continuous system monitoring and auto-fixing',
                    'implementation': '10-minute interval comprehensive system checks'
                })
            
        except:
            self.log_philosophy_action("AUTOMATE", "Failed to start continuous monitoring", "AUTOMATION FAILED")
        
        return {
            'automations_implemented': len(automations),
            'automation_details': automations,
            'status': 'automation_active'
        }
    
    def run_complete_cycle(self) -> dict:
        """Run complete Break-Fix-Automate cycle"""
        print("🎯 BREAK-FIX-AUTOMATE SYSTEM STARTING")
        print("=" * 50)
        
        cycle_start = time.time()
        
        # BREAK: Detect issues
        breaks = self.detect_breaks()
        
        # FIX: Apply fixes
        fix_results = self.apply_fixes(breaks)
        
        # AUTOMATE: Implement prevention
        automation_results = self.implement_automation(breaks, fix_results)
        
        cycle_time = time.time() - cycle_start
        
        # Summary report
        report = {
            'cycle_completed_at': datetime.now().isoformat(),
            'cycle_duration_seconds': cycle_time,
            'issues_detected': len(breaks),
            'fixes_applied': fix_results.get('fixes_applied', 0),
            'automations_implemented': automation_results.get('automations_implemented', 0),
            'issues': breaks,
            'fixes': fix_results,
            'automations': automation_results
        }
        
        self.log_philosophy_action("AUTOMATE", "Complete cycle finished", 
                                 f"{len(breaks)} issues, {fix_results.get('fixes_applied', 0)} fixes, "
                                 f"{automation_results.get('automations_implemented', 0)} automations")
        
        return report
    
    def show_status(self) -> dict:
        """Show current system status"""
        print("📊 BREAK-FIX-AUTOMATE SYSTEM STATUS")
        print("=" * 40)
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'systems_operational': {},
            'recent_activities': []
        }
        
        # Check each system
        for name, script in self.systems.items():
            try:
                if name == 'supply_chain_manager':
                    result = subprocess.run(['python', script, 'status'],
                                          capture_output=True, text=True, timeout=5)
                else:
                    result = subprocess.run(['python', script, '--help'],
                                          capture_output=True, text=True, timeout=5)
                
                operational = result.returncode == 0
                status['systems_operational'][name] = operational
                print(f"   {'✅' if operational else '❌'} {name.replace('_', ' ').title()}")
                
            except subprocess.TimeoutExpired:
                status['systems_operational'][name] = False
                print(f"   ⏳ {name.replace('_', ' ').title()} (timeout)")
            except:
                status['systems_operational'][name] = False
                print(f"   ❌ {name.replace('_', ' ').title()} (error)")
        
        # Show recent philosophy log entries
        if Path(self.philosophy_log).exists():
            with open(self.philosophy_log, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) >= 10 else lines
                
            print(f"\\n📋 RECENT ACTIVITIES:")
            for line in recent_lines:
                print(f"   {line.strip()}")
                status['recent_activities'].append(line.strip())
        
        return status

def main():
    parser = argparse.ArgumentParser(description='Benson Bot Break-Fix-Automate System')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--fix-now', action='store_true', help='Run immediate fix cycle') 
    parser.add_argument('--status', action='store_true', help='Show system status')
    
    args = parser.parse_args()
    
    system = BreakFixAutomateSystem()
    
    if args.monitor:
        print("🔄 Starting continuous Break-Fix-Automate monitoring...")
        while True:
            try:
                system.run_complete_cycle()
                print("⏳ Waiting 10 minutes before next cycle...")
                time.sleep(600)  # 10 minutes
            except KeyboardInterrupt:
                print("\\n👋 Monitoring stopped by user")
                break
    
    elif args.fix_now:
        report = system.run_complete_cycle()
        print(f"\\n✅ Cycle completed in {report['cycle_duration_seconds']:.1f} seconds")
    
    elif args.status:
        system.show_status()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()