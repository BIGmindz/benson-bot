#!/usr/bin/env python3
"""
Test the main bot with enhanced portfolio system integration
"""

import subprocess
import time
import signal

def test_enhanced_main_bot():
    print("🧪 TESTING MAIN BOT WITH ENHANCED PORTFOLIO SYSTEM")
    print("=" * 60)
    
    try:
        # Start the main bot process for a brief test
        process = subprocess.Popen(
            ['python', 'benson_rsi_bot.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("✅ Starting main bot for 30-second test...")
        start_time = time.time()
        
        # Capture startup output for 30 seconds
        output_lines = []
        while time.time() - start_time < 30:
            if process.poll() is not None:
                print("⚠️ Bot process ended")
                break
            
            try:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.rstrip())
                    print(line.rstrip())
                    
                    # Look for key indicators that enhanced system is working
                    if "Total Portfolio Value:" in line:
                        print("✅ ENHANCED SYSTEM DETECTED: Using total portfolio value!")
                    elif "Portfolio liquidation system: ACTIVE" in line:
                        print("✅ LIQUIDATION SYSTEM DETECTED: Ready to manage positions!")
                    elif "insufficient cash" in line.lower():
                        print("❌ OLD SYSTEM STILL ACTIVE: Still getting insufficient cash errors")
            except:
                pass
            
            time.sleep(0.1)
        
        # Gracefully stop
        print("\n🛑 Stopping test bot...")
        process.send_signal(signal.SIGINT)
        process.wait(timeout=10)
        
        # Analyze results
        print("\n📊 TEST RESULTS:")
        enhanced_features = 0
        old_errors = 0
        
        for line in output_lines:
            if any(keyword in line for keyword in ["Total Portfolio Value:", "Allocated Positions:", "liquidation system"]):
                enhanced_features += 1
            elif "insufficient cash" in line.lower():
                old_errors += 1
        
        print(f"   Enhanced features detected: {enhanced_features}")
        print(f"   Old insufficient cash errors: {old_errors}")
        
        if enhanced_features >= 2:
            print("   🟢 SUCCESS: Main bot is using enhanced portfolio system!")
        elif old_errors > 0:
            print("   🔴 ISSUE: Still seeing old insufficient cash errors")
        else:
            print("   🟡 PARTIAL: Some features detected, needs more testing")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        if 'process' in locals() and process.poll() is None:
            process.send_signal(signal.SIGINT)
            process.wait()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_enhanced_main_bot()