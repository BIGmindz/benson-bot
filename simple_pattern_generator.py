#!/usr/bin/env python3
"""
Simple Rapid Pattern Generator for Learning Engine
Generates synthetic trading patterns to boost learning data
"""

import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List
from learning_engine import BensonLearningEngine

class SimplePatternGenerator:
    def __init__(self):
        self.learning_engine = BensonLearningEngine()
        self.session_patterns = []
        
    def generate_pattern(self) -> Dict:
        """Generate a realistic trading pattern"""
        # Market conditions
        market_trend = random.choice(['bullish', 'bearish', 'sideways'])
        volatility = random.choice(['low', 'medium', 'high'])
        
        # Generate RSI based on market conditions
        if market_trend == 'bearish':
            base_rsi = random.uniform(15, 45)  # Lower RSI in bear markets
        elif market_trend == 'bullish':
            base_rsi = random.uniform(45, 85)  # Higher RSI in bull markets  
        else:
            base_rsi = random.uniform(25, 75)  # Mixed in sideways
            
        # Add volatility effects
        if volatility == 'high':
            rsi_noise = random.uniform(-15, 15)
        elif volatility == 'medium':
            rsi_noise = random.uniform(-8, 8)
        else:
            rsi_noise = random.uniform(-3, 3)
            
        final_rsi = max(0, min(100, base_rsi + rsi_noise))
        
        # Generate other signals
        supply_chain_score = random.uniform(0.5, 1.5)
        price_change_24h = random.uniform(-20, 20)
        volume_ratio = random.uniform(0.5, 3.0)
        
        # Determine trade action based on RSI
        if final_rsi < 30:
            action = 'BUY'
            confidence = (30 - final_rsi) / 30 * 80 + random.uniform(10, 20)
        elif final_rsi > 70:
            action = 'SELL'  
            confidence = (final_rsi - 70) / 30 * 80 + random.uniform(10, 20)
        else:
            action = 'HOLD'
            confidence = random.uniform(20, 60)
            
        confidence = min(100, confidence)
        
        # Simulate outcome based on market conditions and confidence
        success_probability = confidence / 100.0
        
        # Market condition adjustments
        if market_trend == 'bullish' and action == 'BUY':
            success_probability *= 1.3
        elif market_trend == 'bearish' and action == 'SELL':
            success_probability *= 1.3
        elif market_trend == 'sideways':
            success_probability *= 0.8
        else:
            success_probability *= 0.7
            
        # Generate profit/loss
        success = random.random() < success_probability
        if success:
            profit_pct = random.uniform(2, 12)  # 2-12% profit
        else:
            profit_pct = random.uniform(-8, -1)  # 1-8% loss
            
        symbol = random.choice([
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT',
            'DOT/USDT', 'AVAX/USDT', 'ALGO/USDT', 'LINK/USDT', 'LTC/USDT'
        ])
        
        pattern = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'rsi': final_rsi,
            'supply_chain_score': supply_chain_score,
            'price_change_24h': price_change_24h,
            'volume_ratio': volume_ratio,
            'confidence': confidence,
            'market_trend': market_trend,
            'volatility': volatility,
            'success': success,
            'profit_pct': profit_pct,
            'pattern_type': 'synthetic_training'
        }
        
        return pattern
    
    def run_pattern_generation(self, duration_seconds=120, patterns_per_minute=15):
        """Generate patterns rapidly"""
        print("🔥 RAPID PATTERN GENERATION STARTED")
        print("=" * 50)
        print(f"⏱️  Duration: {duration_seconds} seconds ({duration_seconds/60:.1f} minutes)")
        print(f"⚡ Rate: {patterns_per_minute} patterns/minute")
        print(f"🎯 Expected Output: ~{int(duration_seconds * patterns_per_minute / 60)} patterns")
        print()
        
        start_time = time.time()
        pattern_interval = 60.0 / patterns_per_minute
        patterns_generated = 0
        
        while time.time() - start_time < duration_seconds:
            pattern = self.generate_pattern()
            self.session_patterns.append(pattern)
            patterns_generated += 1
            
            # Print every 10th pattern
            if patterns_generated % 10 == 0:
                print(f"📊 Generated {patterns_generated} patterns... "
                      f"Latest: {pattern['action']} {pattern['symbol']} "
                      f"RSI {pattern['rsi']:.1f} → {'✅' if pattern['success'] else '❌'} "
                      f"{pattern['profit_pct']:+.1f}%")
            
            time.sleep(pattern_interval)
        
        print("\n" + "=" * 50)
        print("🏁 PATTERN GENERATION COMPLETE!")
        print(f"📊 Total Patterns: {patterns_generated}")
        print(f"⏱️  Actual Duration: {time.time() - start_time:.1f} seconds")
        print(f"⚡ Actual Rate: {patterns_generated / ((time.time() - start_time) / 60):.1f} patterns/minute")
        
        # Analyze generated patterns
        successful_patterns = [p for p in self.session_patterns if p['success']]
        failed_patterns = [p for p in self.session_patterns if not p['success']]
        
        print(f"\n🎯 Pattern Analysis:")
        print(f"   ✅ Successful: {len(successful_patterns)} ({len(successful_patterns)/patterns_generated*100:.1f}%)")
        print(f"   ❌ Failed: {len(failed_patterns)} ({len(failed_patterns)/patterns_generated*100:.1f}%)")
        print(f"   📈 Avg Profit: {sum(p['profit_pct'] for p in successful_patterns)/len(successful_patterns) if successful_patterns else 0:.1f}%")
        print(f"   📉 Avg Loss: {sum(p['profit_pct'] for p in failed_patterns)/len(failed_patterns) if failed_patterns else 0:.1f}%")
        
        # Save patterns to file for learning engine
        self.save_patterns()
        print(f"\n💾 Patterns saved for learning engine integration")
        print("🎯 Your main bot can now learn from these additional patterns!")
        
    def save_patterns(self):
        """Save patterns to file"""
        timestamp = int(time.time())
        filename = f"rapid_training_patterns_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.session_patterns, f, indent=2)
            
        print(f"💾 Saved {len(self.session_patterns)} patterns to {filename}")

def main():
    generator = SimplePatternGenerator()
    
    print("🧠 CURRENT LEARNING ENGINE STATUS:")
    stats = generator.learning_engine.get_learning_stats()
    print(f"   📊 Sessions: {stats['total_sessions']}")
    print(f"   🎯 Patterns: {stats['learned_patterns']}")
    print(f"   💰 Best Return: {stats['best_session_return']:.2f}%")
    print()
    
    # Run 2-minute session generating ~30 patterns
    generator.run_pattern_generation(duration_seconds=120, patterns_per_minute=15)

if __name__ == "__main__":
    main()