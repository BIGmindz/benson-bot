#!/usr/bin/env python3
"""
Benson Bot Trade Monitor
Real-time monitoring of trading sessions and performance
"""

import sqlite3
import json
import time
import os
from datetime import datetime

def monitor_trades():
    print("🎯 BENSON BOT TRADE MONITOR")
    print("="*40)
    print("Press Ctrl+C to stop monitoring")
    print("="*40)
    
    while True:
        try:
            # Clear screen (optional)
            # os.system('clear')
            
            # Check database for latest session
            conn = sqlite3.connect("benson_memory.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM trading_sessions ORDER BY timestamp DESC LIMIT 1")
            session = cursor.fetchone()
            
            if session:
                perf_data = json.loads(session["performance_data"])
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"\r[{timestamp}] 💰 Balance: ${perf_data.get('ending_balance', 0):.2f} | "
                      f"📈 Return: {perf_data.get('total_return', 0):.2f}% | "
                      f"🎯 Trades: {perf_data.get('total_trades', 0)} | "
                      f"✅ Win Rate: {perf_data.get('win_rate', 0)*100:.1f}%", end="", flush=True)
            else:
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] ⏳ Waiting for trading data...", end="", flush=True)
            
            conn.close()
            time.sleep(5)  # Update every 5 seconds
            
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(5)

def show_latest_trades():
    """Show detailed view of latest trading session"""
    try:
        conn = sqlite3.connect("benson_memory.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trading_sessions ORDER BY timestamp DESC LIMIT 3")
        sessions = cursor.fetchall()
        
        print("📊 LATEST TRADING SESSIONS")
        print("="*60)
        
        for i, session in enumerate(sessions, 1):
            perf_data = json.loads(session["performance_data"])
            market_data = json.loads(session["market_conditions"])
            
            print(f"\n{i}️⃣ Session: {session['session_id']}")
            print(f"   ⏰ Time: {session['timestamp']}")
            print(f"   💰 Balance: ${perf_data.get('starting_balance', 0):.2f} → ${perf_data.get('ending_balance', 0):.2f}")
            print(f"   📈 Return: {perf_data.get('total_return', 0):.2f}%")
            print(f"   🎯 Trades: {perf_data.get('total_trades', 0)}")
            print(f"   ✅ Win Rate: {perf_data.get('win_rate', 0)*100:.1f}%")
            print(f"   📊 Market: {market_data.get('trend', 'unknown')} trend, {market_data.get('volatility', 'unknown')} volatility")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading trading sessions: {e}")

def check_training_status():
    """Check if training is currently running"""
    print("🔍 TRAINING STATUS CHECK")
    print("="*30)
    
    # Check if process is running
    if os.system('pgrep -f rapid_fire_trainer.py > /dev/null') == 0:
        print("✅ Training session: RUNNING")
        
        # Check log file
        log_file = "rapid_fire_session_20250916_063333.log"
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            mtime = os.path.getmtime(log_file)
            mod_time = datetime.fromtimestamp(mtime)
            print(f"📄 Log file: {size:,} bytes (modified: {mod_time})")
        
        # Check for result files
        result_files = [f for f in os.listdir('.') if f.startswith('rapid_training_results_')]
        if result_files:
            latest_result = max(result_files, key=lambda f: os.path.getmtime(f))
            print(f"📁 Latest results: {latest_result}")
    else:
        print("❌ Training session: NOT RUNNING")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "monitor":
            monitor_trades()
        elif sys.argv[1] == "status":
            check_training_status()
        elif sys.argv[1] == "trades":
            show_latest_trades()
        else:
            print("Usage: python trade_monitor.py [monitor|status|trades]")
    else:
        # Default behavior - show options
        print("🎯 BENSON BOT TRADE MONITOR")
        print("="*40)
        print("Available commands:")
        print("  python trade_monitor.py monitor    # Real-time monitoring")
        print("  python trade_monitor.py status     # Check training status") 
        print("  python trade_monitor.py trades     # Show latest trades")
        print("\nQuick start: python trade_monitor.py trades")