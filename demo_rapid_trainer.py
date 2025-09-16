#!/usr/bin/env python3
"""
5-Minute Demo Ultra-Rapid Trainer - 3 trades/minute
Shorter demo to show full session completion
"""

import time
import random
import ccxt
import yaml
import numpy as np
from datetime import datetime
from benson_config_manager import BensonConfigManager

class QuickDemo:
    def __init__(self):
        with open("config/config.yaml", 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.user_config = BensonConfigManager()
        self.feature_config = self.user_config.get_config_for_trading()
        
        self.settings = {
            'duration_minutes': 5,
            'trades_per_minute': 3,
            'starting_budget': 100.0
        }
        
        self.portfolio_balance = self.settings['starting_budget']
        self.trade_history = []
        self.session_id = f"demo_{int(time.time())}"
        
    def generate_conditions(self):
        return {
            'market_trend': random.choice(['bullish', 'bearish', 'sideways']),
            'rsi': random.uniform(20, 80),
            'confidence': random.uniform(60, 95)
        }
        
    def execute_demo_trade(self, symbol, action, conditions):
        timestamp = datetime.now()
        price = random.uniform(0.01, 1000)
        position_pct = random.uniform(5, 15)
        position_value = self.portfolio_balance * (position_pct / 100)
        
        # Simulate outcome
        success = random.random() < 0.65
        profit_pct = random.uniform(0.3, 2.0) if success else random.uniform(-1.5, -0.3)
        profit_loss = position_value * (profit_pct / 100)
        
        self.portfolio_balance += profit_loss
        
        trade_data = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': action,
            'price': price,
            'position_pct': position_pct,
            'confidence': conditions['confidence'],
            'outcome': 'profit' if success else 'loss',
            'profit_pct': profit_pct,
            'new_balance': self.portfolio_balance
        }
        
        self.trade_history.append(trade_data)
        return trade_data
        
    def run_demo(self):
        print("⚡ 5-MINUTE ULTRA-RAPID DEMO")
        print(f"🎯 Target: {self.settings['trades_per_minute']} trades/minute for {self.settings['duration_minutes']} minutes")
        print(f"💰 Starting: ${self.settings['starting_budget']:.2f}")
        print()
        
        start_time = time.time()
        duration_seconds = self.settings['duration_minutes'] * 60
        trade_interval = 60 / self.settings['trades_per_minute']
        trades_executed = 0
        profitable_trades = 0
        
        while time.time() - start_time < duration_seconds:
            symbol = random.choice(self.config['symbols'])
            conditions = self.generate_conditions()
            action = random.choice(['BUY', 'SELL'])
            
            trade = self.execute_demo_trade(symbol, action, conditions)
            trades_executed += 1
            
            if trade['outcome'] == 'profit':
                profitable_trades += 1
            
            elapsed_min = (time.time() - start_time) / 60
            profit_emoji = "✅" if trade['outcome'] == 'profit' else "❌"
            
            print(f"{profit_emoji} #{trades_executed:2d} | {elapsed_min:4.1f}m | {action} {symbol:12} | ${trade['price']:8.4f} | {trade['position_pct']:4.1f}% | C:{trade['confidence']:3.0f}% | P:{trade['profit_pct']:+5.1f}% | Bal:${self.portfolio_balance:7.2f}")
            
            time.sleep(trade_interval)
        
        # Final stats
        total_time = time.time() - start_time
        actual_rate = trades_executed / (total_time / 60)
        win_rate = (profitable_trades / trades_executed) * 100
        total_return = ((self.portfolio_balance - self.settings['starting_budget']) / self.settings['starting_budget']) * 100
        
        print("\\n🏁 DEMO COMPLETE!")
        print(f"⏱️ Time: {total_time/60:.2f} minutes")
        print(f"📊 Trades: {trades_executed}")
        print(f"⚡ Rate: {actual_rate:.1f} trades/minute (target: {self.settings['trades_per_minute']})")
        print(f"✅ Win Rate: {win_rate:.1f}%")
        print(f"📈 Return: {total_return:+.2f}%")
        print(f"💰 Final: ${self.portfolio_balance:.2f}")
        
        if actual_rate >= self.settings['trades_per_minute']:
            print("🎯 TARGET ACHIEVED!")
        
        return actual_rate >= self.settings['trades_per_minute']

if __name__ == "__main__":
    demo = QuickDemo()
    demo.run_demo()