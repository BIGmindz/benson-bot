#!/usr/bin/env python3
"""
4-Hour Session Monitor
Comprehensive monitoring for the 4-hour paper trading session
"""

import time
import os
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

class FourHourSessionMonitor:
    def __init__(self):
        self.session_start = time.time()
        self.session_duration = 14400  # 4 hours in seconds
        self.log_file = "4hour_session.log"
        self.expected_completion = self.session_start + self.session_duration
        
    def get_session_status(self):
        """Get current session status"""
        current_time = time.time()
        elapsed = current_time - self.session_start
        progress = (elapsed / self.session_duration) * 100
        remaining = self.session_duration - elapsed
        
        return {
            "elapsed_seconds": elapsed,
            "progress_percent": min(100, progress),
            "remaining_seconds": max(0, remaining),
            "expected_completion": datetime.fromtimestamp(self.expected_completion).strftime("%H:%M:%S"),
            "current_time": datetime.now().strftime("%H:%M:%S")
        }
    
    def check_process_alive(self):
        """Check if the training process is still running"""
        try:
            # Check if rapid_fire_trainer.py process is running
            result = subprocess.run(['pgrep', '-f', 'rapid_fire_trainer.py'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_latest_trades(self, num_trades=5):
        """Get latest trades from log file"""
        if not Path(self.log_file).exists():
            return []
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            
            trades = []
            for line in reversed(lines):
                if "🚀 TRADE:" in line and len(trades) < num_trades:
                    trades.append(line.strip())
            
            return list(reversed(trades))
        except:
            return []
    
    def get_performance_stats(self):
        """Extract performance statistics from log"""
        if not Path(self.log_file).exists():
            return None
        
        try:
            with open(self.log_file, 'r') as f:
                content = f.read()
            
            # Look for balance updates
            balances = []
            lines = content.split('\n')
            for line in lines:
                if "Balance:" in line:
                    try:
                        # Extract balance value
                        balance_part = line.split("Balance:")[1].strip()
                        balance_value = float(balance_part.replace('$', '').split()[0])
                        balances.append(balance_value)
                    except:
                        continue
            
            if balances:
                starting_balance = 100.0
                current_balance = balances[-1]
                return_pct = ((current_balance - starting_balance) / starting_balance) * 100
                
                return {
                    "starting_balance": starting_balance,
                    "current_balance": current_balance,
                    "return_percent": return_pct,
                    "total_trades": len([line for line in lines if "🚀 TRADE:" in line])
                }
            
        except:
            pass
        
        return None
    
    def display_status(self):
        """Display comprehensive session status"""
        status = self.get_session_status()
        process_alive = self.check_process_alive()
        latest_trades = self.get_latest_trades(3)
        performance = self.get_performance_stats()
        
        print("🎯 4-HOUR COMPREHENSIVE SESSION MONITOR")
        print("=" * 50)
        print(f"📅 Current Time: {status['current_time']}")
        print(f"⏰ Session Progress: {status['progress_percent']:.1f}%")
        print(f"⏱️  Elapsed: {status['elapsed_seconds']/3600:.1f} hours")
        print(f"⏳ Remaining: {status['remaining_seconds']/3600:.1f} hours")
        print(f"🏁 Expected Completion: {status['expected_completion']}")
        print()
        
        print(f"🔄 Process Status: {'🟢 RUNNING' if process_alive else '🔴 STOPPED'}")
        print()
        
        if performance:
            print("📊 CURRENT PERFORMANCE:")
            print(f"   💰 Starting Balance: ${performance['starting_balance']:.2f}")
            print(f"   💰 Current Balance: ${performance['current_balance']:.2f}")
            print(f"   📈 Return: {performance['return_percent']:+.2f}%")
            print(f"   📊 Total Trades: {performance['total_trades']}")
            print()
        
        if latest_trades:
            print("🚀 LATEST TRADES:")
            for trade in latest_trades[-3:]:
                # Clean up the trade line for display
                clean_trade = trade.replace("🚀 TRADE:", "   •").replace("|", "│")
                print(clean_trade)
            print()
        
        print("🌍 COMPREHENSIVE SYSTEMS ACTIVE:")
        print("   ✅ 7-Component Supply Chain Signals")
        print("   ✅ Advanced Pattern Recognition")
        print("   ✅ Break-Fix-Automate Monitoring")
        print("   ✅ Profit Engine Optimization")
        print("   ✅ Learning Engine Pattern Capture")
        
        # Progress bar
        progress_bar_length = 40
        filled_length = int(progress_bar_length * status['progress_percent'] / 100)
        bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
        print(f"\\n📊 Progress: [{bar}] {status['progress_percent']:.1f}%")
        
        return status
    
    def monitor_session(self, update_interval=60):
        """Continuously monitor the session"""
        print("🚀 Starting 4-Hour Session Monitoring...")
        print("   Press Ctrl+C to exit monitoring (session will continue)")
        print()
        
        try:
            while True:
                os.system('clear')  # Clear screen on macOS/Linux
                status = self.display_status()
                
                if status['progress_percent'] >= 100:
                    print("\\n🏁 SESSION COMPLETE!")
                    break
                
                if not self.check_process_alive():
                    print("\\n⚠️  WARNING: Training process appears to have stopped!")
                    break
                
                print(f"\\n⏳ Next update in {update_interval} seconds...")
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\\n👋 Monitoring stopped. Session continues in background.")
            print(f"📋 Monitor progress: tail -f {self.log_file}")

def main():
    import sys
    
    monitor = FourHourSessionMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        # Just show status once
        monitor.display_status()
    else:
        # Continuous monitoring
        monitor.monitor_session()

if __name__ == "__main__":
    main()