#!/usr/bin/env python3
"""
Quick test to demonstrate intelligent position sizing
"""

from rapid_fire_trainer import RapidFireTrainer
import time

def test_position_sizing():
    """Test the intelligent position sizing feature"""
    trainer = RapidFireTrainer()
    
    print("🧪 TESTING INTELLIGENT POSITION SIZING")
    print("="*50)
    
    # Test different confidence levels
    test_cases = [
        {"confidence": 30.0, "description": "Low confidence"},
        {"confidence": 50.0, "description": "Medium confidence"},
        {"confidence": 75.0, "description": "High confidence"},
        {"confidence": 95.0, "description": "Very high confidence"},
    ]
    
    for test in test_cases:
        confidence = test["confidence"]
        signal_strength = confidence / 100.0
        position_size = trainer.calculate_position_size(confidence, signal_strength)
        
        print(f"{test['description']} ({confidence}%): {position_size*100:.1f}% position size")
    
    print()
    print("🚀 Running 5 sample trades to show dynamic sizing...")
    print()
    
    # Run a few sample trades
    for i in range(5):
        try:
            symbol = trainer.symbols[i % len(trainer.symbols)]
            market_conditions = trainer.get_market_conditions()
            rsi = 30 + (i * 15)  # Vary RSI from 30 to 90
            
            # Test buy signal
            should_buy, confidence = trainer.should_rapid_buy(symbol, rsi, market_conditions)
            
            if should_buy:
                trade = trainer.execute_rapid_trade(symbol, 'BUY', rsi, confidence, market_conditions)
            else:
                # Test sell signal instead
                should_sell, confidence = trainer.should_rapid_sell(symbol, rsi + 40, market_conditions)
                if should_sell:
                    trade = trainer.execute_rapid_trade(symbol, 'SELL', rsi + 40, confidence, market_conditions)
        
        except Exception as e:
            print(f"⚠️  Error in trade {i+1}: {e}")
        
        time.sleep(1)  # Small delay between trades
    
    print()
    print("✅ Position sizing test completed!")
    print(f"📊 Final balance: ${trainer.portfolio_balance:.2f}")
    print(f"📈 Total trades: {len(trainer.trade_history)}")

if __name__ == "__main__":
    test_position_sizing()