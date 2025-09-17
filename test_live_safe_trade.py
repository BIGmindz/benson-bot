#!/usr/bin/env python3
"""
Test actual trade execution with safe order placement
"""

import os
import sys
sys.path.append('/Users/johnbozza/Library/Mobile Documents/com~apple~CloudDocs/Benson Bot')

from dotenv import load_dotenv
load_dotenv()

from trade_executor import create_trade_executor, TradeRequest, OrderSide, OrderType

def test_real_safe_trade():
    print("💸 TESTING REAL SAFE TRADE EXECUTION")
    print("=" * 50)
    
    try:
        # Create trade executor
        executor = create_trade_executor()
        
        # Check balance before
        balance_before = executor.get_account_balance()
        print(f"💰 Balance before: ${balance_before:.2f}")
        
        # Create a small test trade
        trade_request = TradeRequest(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=0.0,  # Will be calculated by safe system
            confidence=0.70,  # Medium confidence - should not get boost
            signal_strength=0.60
        )
        
        print(f"\n🎯 EXECUTING SAFE TRADE:")
        print(f"   Symbol: {trade_request.symbol}")
        print(f"   Side: {trade_request.side.value}")
        print(f"   Expected budget: ~$2.50 (20% of ${balance_before:.2f})")
        
        # Execute the trade
        result = executor.execute_trade(trade_request)
        
        # Display result
        print(f"\n📊 TRADE RESULT:")
        if result.success:
            print(f"   ✅ Status: SUCCESS")
            print(f"   📄 Order ID: {result.order_id}")
            print(f"   💰 Amount: {result.amount:.8f} BTC")
            print(f"   💵 Price: ${result.price:.2f}")
            print(f"   💸 Total Cost: ~${result.amount * result.price:.2f}")
            print(f"   ⏰ Timestamp: {result.timestamp}")
            
            # Check balance after
            balance_after = executor.get_account_balance()
            spent = balance_before - balance_after
            print(f"   💰 Balance after: ${balance_after:.2f}")
            print(f"   📉 Amount spent: ${spent:.2f}")
            
        else:
            print(f"   ❌ Status: FAILED")
            print(f"   💬 Error: {result.error_message}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("⚠️  This will execute a REAL trade with your live Kraken account!")
    print("   - Trade will be ~$2.50 (20% of balance)")  
    print("   - Minimum cash buffer of $5 will be preserved")
    print("   - This tests the 'insufficient funds' fix")
    
    confirm = input("\n🤔 Proceed with live trade test? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        success = test_real_safe_trade()
        print(f"\n{'🎉 SAFE SYSTEM WORKING!' if success else '⚠️  NEEDS ATTENTION'}")
    else:
        print("❌ Test cancelled by user")