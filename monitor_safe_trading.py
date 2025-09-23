#!/usr/bin/env python3
"""
Real-time Benson Bot Safe Trading Monitor
"""

import os
import time
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def check_bot_status():
    """Check if Benson Bot is running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'benson_rsi_bot.py'], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except:
        return False

def get_balance():
    """Get current balance"""
    try:
        import sys
        sys.path.append('/Users/johnbozza/Library/Mobile Documents/com~apple~CloudDocs/Benson Bot')
        from trade_executor import create_trade_executor
        executor = create_trade_executor()
        return executor.get_account_balance()
    except Exception as e:
        return f"Error: {e}"

def get_latest_signals():
    """Get latest trading signals"""
    try:
        with open('benson_signals.csv', 'r') as f:
            lines = f.readlines()
        if len(lines) > 1:
            # Get last 5 signals
            recent = []
            for line in lines[-5:]:
                parts = line.strip().split(',')
                if len(parts) >= 6:
                    recent.append({
                        'time': parts[0][:19],
                        'symbol': parts[2],
                        'price': f"${float(parts[3]):,.2f}",
                        'rsi': f"{float(parts[4]):.1f}",
                        'signal': parts[5]
                    })
            return recent
    except:
        pass
    return []

def show_safe_system_status():
    """Show safe order system status"""
    base_trade = float(os.getenv('BASE_TRADE_USD', '10'))
    max_pct = float(os.getenv('MAX_POSITION_PCT', '0.20'))
    buffer = float(os.getenv('MIN_CASH_BUFFER_USD', '5'))
    
    balance = get_balance()
    if isinstance(balance, (int, float)):
        spendable = max(0, balance - buffer)
        max_by_pct = balance * max_pct
        trade_size = min(base_trade, spendable, max_by_pct)
        
        return {
            'balance': balance,
            'spendable': spendable,
            'trade_size': trade_size,
            'buffer': buffer,
            'max_pct': max_pct * 100
        }
    return None

def main():
    print("🤖 BENSON BOT LIVE MONITORING DASHBOARD")
    print("=" * 60)
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🤖 BENSON BOT LIVE MONITORING DASHBOARD")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Bot status
        bot_running = check_bot_status()
        print(f"🚀 Bot Status: {'✅ RUNNING' if bot_running else '❌ STOPPED'}")
        
        # Balance and safe system
        safe_status = show_safe_system_status()
        if safe_status:
            print(f"\n💰 SAFE TRADING SYSTEM:")
            print(f"   Balance: ${safe_status['balance']:.2f}")
            print(f"   After buffer: ${safe_status['spendable']:.2f}")
            print(f"   Trade size: ${safe_status['trade_size']:.2f}")
            print(f"   Buffer: ${safe_status['buffer']:.2f}")
            print(f"   Max %: {safe_status['max_pct']:.0f}%")
        
        # Recent signals
        signals = get_latest_signals()
        if signals:
            print(f"\n📊 RECENT SIGNALS:")
            for signal in signals:
                print(f"   {signal['time']} | {signal['symbol']} | {signal['price']} | RSI {signal['rsi']} | {signal['signal']}")
        
        print(f"\n⏰ Next update in 30 seconds... (Ctrl+C to exit)")
        
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            print(f"\n👋 Monitoring stopped")
            break

if __name__ == "__main__":
    main()