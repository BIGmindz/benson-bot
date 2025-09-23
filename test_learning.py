#!/usr/bin/env python3
"""
Test the Benson Learning Engine
"""

from learning_engine import BensonLearningEngine
import yaml

def test_learning_engine():
    # Initialize learning engine
    print("🧠 Testing Benson Learning Engine...")
    
    learning_engine = BensonLearningEngine()
    
    # Get current learning stats
    stats = learning_engine.get_learning_stats()
    print(f"📊 Current Stats:")
    print(f"   Sessions: {stats['total_sessions']}")
    print(f"   Patterns: {stats['learned_patterns']}")
    print(f"   Best Return: {stats['best_session_return']:.2f}%")
    print(f"   Learning Active: {stats['learning_active']}")
    
    # Load current config and get optimized version
    with open('config/config.yaml', 'r') as f:
        base_config = yaml.safe_load(f)
    
    print(f"\n⚖️ Current RSI Thresholds:")
    print(f"   Buy: {base_config['rsi']['buy_threshold']}")
    print(f"   Sell: {base_config['rsi']['sell_threshold']}")
    
    # Get optimized config (will return same if no patterns learned yet)
    optimized_config = learning_engine.get_optimized_config(base_config)
    
    if 'optimized_weights' in optimized_config:
        print(f"\n🎯 Optimized Weights Found:")
        for weight_name, value in optimized_config['optimized_weights'].items():
            print(f"   {weight_name}: {value:.3f}")
    else:
        print(f"\n🎯 No optimizations available yet - need successful trading sessions")
    
    print(f"\n✅ Learning engine is ready!")

if __name__ == "__main__":
    test_learning_engine()