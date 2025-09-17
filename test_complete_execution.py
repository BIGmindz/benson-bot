#!/usr/bin/env python3
"""
Test the complete execute_trade method to see where it fails
"""

from trade_executor import create_trade_executor, TradeRequest, OrderSide

def test_complete_trade_execution():
    print("🔍 TESTING COMPLETE TRADE EXECUTION")
    print("=" * 50)
    
    try:
        # Create trade executor
        trade_executor = create_trade_executor("config/config.yaml")
        
        # Create trade request (same as bot does)
        test_request = TradeRequest(
            symbol="PENGU/USDT",
            side=OrderSide.BUY,
            amount=0.0,  # This is what the bot sends
            confidence=0.75,
            signal_strength=0.65,
            metadata={
                "rsi": 9.44,
                "reason": "Complete execution test"
            }
        )
        
        print(f"🎯 EXECUTING COMPLETE TRADE:")
        print(f"   Symbol: {test_request.symbol}")
        print(f"   Initial Amount: {test_request.amount}")
        
        # Execute the complete trade (this should work now)
        result = trade_executor.execute_trade(test_request)
        
        print(f"\n📊 TRADE RESULT:")
        print(f"   Success: {result.success}")
        
        if result.success:
            print(f"   ✅ TRADE SUCCESSFUL!")
            print(f"   Symbol: {result.symbol}")
            print(f"   Amount: {result.amount}")
            print(f"   Order ID: {result.order_id}")
            print(f"   💰 This proves the fix works!")
        else:
            print(f"   ❌ TRADE FAILED!")
            print(f"   Error: {result.error_message}")
            print(f"   🔍 This tells us exactly what's wrong")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    print("🧪 COMPLETE TRADE EXECUTION TEST")
    print("📋 Testing the full execute_trade method")
    print("")
    
    success = test_complete_trade_execution()
    
    if success:
        print(f"\n🎉 TRADE EXECUTION WORKS!")
        print(f"✅ The fix is correct - bot should work")
    else:
        print(f"\n❌ TRADE EXECUTION STILL FAILING")
        print(f"🔧 Need to debug further")

if __name__ == "__main__":
    main()