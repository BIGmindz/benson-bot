#!/usr/bin/env python3
"""
30-Minute Live Trading Session Manager
"""

import subprocess
import time
import signal
import sys
from datetime import datetime, timedelta

def run_30_min_session():
    print("🚀 BENSON BOT - 30 MINUTE LIVE TRADING SESSION")
    print("=" * 60)
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=30)
    
    print(f"⏰ Session Start: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Session End:   {end_time.strftime('%H:%M:%S')}")
    print(f"🎯 Duration: 30 minutes")
    print("=" * 60)
    
    # Start the bot process
    try:
        process = subprocess.Popen(
            ['python', 'benson_rsi_bot.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"✅ Bot started (PID: {process.pid})")
        print("📊 Real-time trading output:")
        print("-" * 60)
        
        # Monitor output for 30 minutes
        while datetime.now() < end_time:
            if process.poll() is not None:
                print(f"⚠️ Bot process ended unexpectedly")
                break
                
            # Check for output
            try:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
            except:
                pass
            
            # Small sleep to prevent overwhelming
            time.sleep(0.1)
        
        # Time's up - gracefully stop the bot
        print("-" * 60)
        print(f"⏰ 30 minutes completed at {datetime.now().strftime('%H:%M:%S')}")
        
        if process.poll() is None:
            print("🛑 Gracefully stopping bot...")
            process.send_signal(signal.SIGINT)
            
            # Wait up to 10 seconds for graceful shutdown
            try:
                process.wait(timeout=10)
                print("✅ Bot stopped gracefully")
            except subprocess.TimeoutExpired:
                print("⚠️ Force stopping bot...")
                process.kill()
                process.wait()
        
        print("🏁 30-minute live trading session completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Session interrupted by user")
        if 'process' in locals() and process.poll() is None:
            process.send_signal(signal.SIGINT)
            process.wait()
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'process' in locals() and process.poll() is None:
            process.kill()

if __name__ == "__main__":
    run_30_min_session()