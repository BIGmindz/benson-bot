#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE INTEGRATION TEST
Test the fixed execute_trade method with the exact same scenario as the bot.
This verifies that amount=0.0 auto-calculation works in full integration.
"""

import yaml
import os
import sys
from datetime import datetime
from trade_executor import TradeExecutor, TradeRequest, OrderSide, OrderType, create_trade_executor

def test_integration_fix():
    """Test the complete integration with amount=0.0 auto-calculation"""
    
    print("🧪 INTEGRATION TEST: Execute Trade with amount=0.0 Auto-Calculation")
    print("=" * 70)
    
    # Load configuration
    try:
        config_path = "kraken_config_section.yaml"
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            return False
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        print(f"✅ Config loaded from {config_path}")
        
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    # Create trade executor
    try:
        trade_executor = create_trade_executor(config_path)
        print("✅ Trade executor created successfully")
        
        # Check balance
        balance = trade_executor.get_account_balance()
        print(f"💰 Current balance: ${balance:.2f}")
        
        if balance < 0.10:  # Lower threshold for test
            print("❌ Insufficient balance for test")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create trade executor: {e}")
        return False
    
    # Create trade request with amount=0.0 (exactly like the bot does)
    try:
        trade_request = TradeRequest(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=0.0,  # 🎯 CRITICAL: This is what the bot sends
            confidence=0.15,  # Low confidence for small position
            signal_strength=0.25,  # Low signal strength  
            metadata={
                "rsi": 35.2,
                "supply_chain_factor": 1.05,
                "africa_factor": 1.0,
                "reason": "Integration test with auto-calculation"
            }
        )
        
        print("\n🎯 TRADE REQUEST CREATED:")
        print(f"   Symbol: {trade_request.symbol}")
        print(f"   Side: {trade_request.side}")
        print(f"   Amount: {trade_request.amount} (ZERO - should auto-calculate)")
        print(f"   Confidence: {trade_request.confidence}")
        print(f"   Signal Strength: {trade_request.signal_strength}")
        
    except Exception as e:
        print(f"❌ Failed to create trade request: {e}")
        return False
    
    # Execute the trade (this should now work!)
    try:
        print(f"\n🚀 EXECUTING TRADE... (this should auto-calculate amount)")
        result = trade_executor.execute_trade(trade_request)
        
        print(f"\n📊 TRADE RESULT:")
        print(f"   Success: {result.success}")
        
        if result.success:
            print(f"   ✅ TRADE SUCCESSFUL!")
            print(f"   Symbol: {result.symbol}")
            print(f"   Side: {result.side}")
            print(f"   Amount: {result.amount:.8f}")
            print(f"   Price: ${result.price:.2f}")
            print(f"   Total Value: ${result.amount * result.price:.2f}")
            print(f"   Order ID: {result.order_id}")
            print(f"   Timestamp: {result.timestamp}")
            return True
        else:
            print(f"   ❌ TRADE FAILED!")
            print(f"   Error: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Trade execution failed with exception: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Run the integration test"""
    
    print(f"\n🎯 BENSON INTEGRATION TEST")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Testing execute_trade fix with amount=0.0 auto-calculation\n")
    
    # Run the test
    success = test_integration_fix()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 INTEGRATION TEST PASSED!")
        print("✅ The fix is working - amount=0.0 auto-calculation successful")
        print("🚀 Ready for live bot deployment!")
    else:
        print("❌ INTEGRATION TEST FAILED!")
        print("🔍 Fix needs more work before deployment")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)