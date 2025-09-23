#!/usr/bin/env python3
"""
Rapid Trading Session Runner
Optimized for 30-60 minute profitable sessions
"""

import os
import sys
import time
import json
import signal
from datetime import datetime, timedelta
from rapid_profit_engine import RapidProfitEngine, RapidConfig

class RapidTradingSession:
    def __init__(self, duration_minutes=30):
        self.duration_minutes = duration_minutes
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        # Enhanced config for profitability
        config = RapidConfig(
            min_profit_target=0.025,    # 2.5% minimum
            max_profit_target=0.05,     # 5% maximum  
            stop_loss_pct=0.015,        # 1.5% stop loss
            max_hold_minutes=45,        # 45 min max hold
            min_position_size=8.0,      # $8 minimum
            max_position_size=50.0      # $50 maximum
        )
        
        self.engine = RapidProfitEngine(config)
        self.running = True
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print("\n🛑 Graceful shutdown requested...")
        self.running = False
    
    def run(self):
        print(f"🚀 Starting {self.duration_minutes}-minute rapid trading session")
        print(f"⏰ Session will end at {self.end_time.strftime('%H:%M:%S')}")
        print("=" * 60)
        
        session_stats = {
            'start_time': self.start_time.isoformat(),
            'target_duration': self.duration_minutes,
            'trades_executed': 0,
            'total_profit': 0,
            'win_rate': 0
        }
        
        try:
            # Run the trading session
            results = self.engine.run_rapid_session(self.duration_minutes)
            
            # Update stats
            session_stats.update(results)
            session_stats['end_time'] = datetime.now().isoformat()
            session_stats['actual_duration'] = (datetime.now() - self.start_time).total_seconds() / 60
            
            # Print final results
            print("\n" + "=" * 60)
            print("📊 RAPID SESSION RESULTS:")
            print(f"⏱️  Duration: {session_stats['actual_duration']:.1f} minutes")
            print(f"📈 Trades: {results['total_trades']}")
            print(f"🎯 Win Rate: {results['win_rate']:.1f}%")
            print(f"💰 Total Profit: ${results['total_profit_usd']:.2f}")
            
            if results['total_profit_usd'] > 0:
                print("🎉 PROFITABLE SESSION! 🎉")
            else:
                print("📉 Session ended with loss")
            
            # Save results
            timestamp = int(datetime.now().timestamp())
            filename = f"rapid_session_results_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(session_stats, f, indent=2)
            
            print(f"💾 Results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Session error: {e}")
            return False
        
        return results['total_profit_usd'] > 0

def main():
    """Run a rapid trading session"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run rapid trading session')
    parser.add_argument('--duration', type=int, default=30, help='Session duration in minutes')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Running in TEST mode (no real trades)")
        return
    
    # Create and run session
    session = RapidTradingSession(args.duration)
    success = session.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
