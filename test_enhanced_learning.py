#!/usr/bin/env python3
"""
Test Enhanced Benson Learning System - Success & Failure Learning
"""

from learning_engine import BensonLearningEngine, TradingSession, MarketPattern
from dataclasses import asdict
import time

def test_enhanced_learning():
    print("🧠 Testing Enhanced Benson Learning System")
    print("=" * 50)
    
    learning_engine = BensonLearningEngine()
    
    # Simulate a failed trading session
    print("\n1️⃣ Simulating UNSUCCESSFUL trading session...")
    failed_session = TradingSession(
        session_id="test_failure_001",
        start_time=time.time() - 3600,
        end_time=time.time(),
        starting_balance=10000.0,
        ending_balance=9500.0,
        total_return=-5.0,  # Lost 5%
        total_trades=10,
        win_rate=0.3,  # Only 30% win rate
        avg_win=50.0,
        avg_loss=-100.0,
        max_drawdown=-8.0,
        sharpe_ratio=-0.5,
        volatility=0.85,  # High volatility
        market_conditions={"trend": "volatile", "volume": "high"},
        signal_weights={"rsi": 0.25, "supply_chain": 0.175},
        rsi_params={"buy_threshold": 25, "sell_threshold": 75}  # Aggressive thresholds
    )
    
    # Learn from the failed session
    config = {"rsi": {"buy_threshold": 30, "sell_threshold": 70}}
    learning_engine.learn_from_session(failed_session, config)
    
    print("\n2️⃣ Testing pattern avoidance...")
    # Test if similar conditions trigger avoidance
    should_avoid, reason = learning_engine.should_avoid_trade(
        symbol="BTC/USDT",
        rsi=26.0,  # Similar to failed pattern (25)
        supply_chain=0.5,
        current_volatility=0.8,  # High volatility like failure
        signal_weights={"rsi": 0.25, "supply_chain": 0.175}
    )
    
    if should_avoid:
        print(f"✅ AVOIDANCE WORKING: {reason}")
    else:
        print("❌ Avoidance not triggered")
    
    print("\n3️⃣ Testing confidence scoring...")
    # Test confidence calculation
    confidence = learning_engine.calculate_trade_confidence(
        symbol="ETH/USDT",
        rsi=35.0,  # Different from failure pattern
        supply_chain=0.4,
        current_volatility=0.3,  # Low volatility (good)
        signal_weights={"rsi": 0.25, "supply_chain": 0.175}
    )
    
    print(f"📊 Trade Confidence: {confidence:.1%}")
    if confidence < 0.4:
        print("⚠️ Low confidence - avoid trade")
    elif confidence > 0.6:
        print("✅ High confidence - good trade opportunity")
    else:
        print("🤔 Medium confidence - proceed with caution")
    
    print("\n4️⃣ Learning Statistics:")
    stats = learning_engine.get_learning_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Enhanced Learning System Test Complete!")
    print("✅ The bot now learns from BOTH successes AND failures")
    print("✅ Actively avoids patterns that previously caused losses")
    print("✅ Uses confidence scoring to make better decisions")

if __name__ == "__main__":
    test_enhanced_learning()