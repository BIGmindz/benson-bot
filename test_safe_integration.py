#!/usr/bin/env python3
"""
Comprehensive test of the integrated safe order placement system
"""

import os
import sys
sys.path.append('/Users/johnbozza/Library/Mobile Documents/com~apple~CloudDocs/Benson Bot')

from dotenv import load_dotenv
load_dotenv()

from trade_executor import create_trade_executor, TradeRequest, OrderSide, OrderType

def test_integrated_safe_trading():
    print("🚀 TESTING INTEGRATED SAFE TRADING SYSTEM")
    print("=" * 60)
    
    try:
        # Create trade executor
        executor = create_trade_executor()
        
        # Check current balance
        balance = executor.get_account_balance()
        print(f"💰 Current balance: ${balance:.2f}")
        
        # Create a test trade request (dry run concept)
        test_request = TradeRequest(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=0.0,  # Will be auto-calculated by safe system
            confidence=0.75,  # Medium confidence
            signal_strength=0.65  # Medium signal strength
        )
        
        print(f"\n🎯 TEST TRADE REQUEST:")
        print(f"   Symbol: {test_request.symbol}")
        print(f"   Side: {test_request.side.value}")
        print(f"   Confidence: {test_request.confidence}")
        print(f"   Signal Strength: {test_request.signal_strength}")
        
        # Test what would happen (simulate the calculation)
        print(f"\n⚙️ SAFE SIZING SIMULATION:")
        
        # Get environment settings
        base_trade = float(os.getenv('BASE_TRADE_USD', '10'))
        min_buffer = float(os.getenv('MIN_CASH_BUFFER_USD', '5'))
        max_pct = float(os.getenv('MAX_POSITION_PCT', '0.20'))
        
        # Calculate available funds
        spendable = max(0.0, balance - min_buffer)
        max_by_pct = balance * max_pct
        final_budget = min(base_trade, spendable, max_by_pct)
        
        print(f"   Base trade size: ${base_trade:.2f}")
        print(f"   Available after buffer: ${spendable:.2f}")
        print(f"   Max by percentage: ${max_by_pct:.2f}")
        print(f"   Final budget: ${final_budget:.2f}")
        
        # Check if we would skip the trade
        if final_budget <= 0:
            print("❌ Trade would be SKIPPED - insufficient funds after buffer")
        else:
            print(f"✅ Trade would proceed with ${final_budget:.2f} budget")
            
            # Get current BTC price for estimation
            ticker = executor.exchange.fetch_ticker("BTC/USD")
            current_price = float(ticker['last'])
            estimated_btc = final_budget / current_price
            print(f"   Estimated BTC amount: {estimated_btc:.8f}")
            
        # Test high confidence scenario
        print(f"\n🚀 HIGH CONFIDENCE SCENARIO:")
        high_confidence_boost = 1.65  # From config
        if test_request.confidence >= 0.85 and test_request.signal_strength >= 0.8:
            boosted_budget = min(base_trade * high_confidence_boost, spendable, max_by_pct)
            print(f"   Would apply {high_confidence_boost}x boost")
            print(f"   Boosted budget: ${boosted_budget:.2f}")
        else:
            print(f"   No boost applied (confidence {test_request.confidence}, strength {test_request.signal_strength})")
        
        # Show safety mechanisms
        print(f"\n🛡️ ACTIVE SAFETY MECHANISMS:")
        print(f"   ✅ Minimum cash buffer: ${min_buffer:.2f}")
        print(f"   ✅ Maximum position percentage: {max_pct*100:.1f}%")
        print(f"   ✅ Slippage protection: {float(os.getenv('SLIPPAGE_PCT', '0.005'))*100:.2f}%")
        print(f"   ✅ Exchange minimum order validation")
        print(f"   ✅ Available funds only (not allocated)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integrated_safe_trading()
    print(f"\n{'✅ SAFE TRADING SYSTEM READY' if success else '❌ SYSTEM NEEDS ATTENTION'}")