#!/usr/bin/env python3
"""
Debug the exact trade request and currency issues
"""

from trade_executor import create_trade_executor, TradeRequest, OrderSide

def debug_trade_execution():
    print("🔍 DEBUGGING TRADE EXECUTION")
    print("=" * 50)
    
    try:
        # Create trade executor with the main config
        trade_executor = create_trade_executor("config/config.yaml")
        
        # Check balance
        balance = trade_executor.get_account_balance() 
        print(f"💰 USD Balance: ${balance:.2f}")
        
        # Create the exact same trade request as the bot
        test_request = TradeRequest(
            symbol="PENGU/USDT",  # Same symbol that failed
            side=OrderSide.BUY,
            amount=0.0,  # Auto-calculate
            confidence=0.75,  # Typical confidence
            signal_strength=0.65,  # Typical signal strength
            metadata={
                "rsi": 9.44,
                "reason": "Debug test"
            }
        )
        
        print(f"\n🎯 TEST TRADE REQUEST:")
        print(f"   Symbol: {test_request.symbol}")
        print(f"   Side: {test_request.side}")
        print(f"   Amount: {test_request.amount} (auto-calculate)")
        print(f"   Confidence: {test_request.confidence}")
        
        # Calculate position size manually
        position_value = trade_executor.calculate_position_size(test_request, balance)
        print(f"\n💵 POSITION CALCULATION:")
        print(f"   Balance: ${balance:.2f}")
        print(f"   Calculated Position: ${position_value:.2f}")
        print(f"   Percentage: {(position_value/balance)*100:.1f}%")
        
        # Get current price for the symbol
        try:
            current_price = trade_executor._get_current_price("PENGU/USDT")
            calculated_amount = position_value / current_price
            print(f"   PENGU Price: ${current_price:.6f}")
            print(f"   PENGU Amount: {calculated_amount:.0f} tokens")
            
            # Check minimum order requirements
            markets = trade_executor.exchange.load_markets()
            market_info = markets.get("PENGU/USDT", {})
            min_amount = market_info.get('limits', {}).get('amount', {}).get('min', 0)
            min_cost = market_info.get('limits', {}).get('cost', {}).get('min', 0)
            
            print(f"\n🔒 KRAKEN LIMITS:")
            print(f"   Min Amount: {min_amount} PENGU")
            print(f"   Min Cost: ${min_cost:.2f}")
            print(f"   Our Amount: {calculated_amount:.0f} PENGU")
            print(f"   Our Cost: ${position_value:.2f}")
            
            if calculated_amount < min_amount:
                print(f"   ❌ PROBLEM: Amount too small!")
            if position_value < min_cost:
                print(f"   ❌ PROBLEM: Cost too small!")
                
        except Exception as e:
            print(f"   ❌ Price check failed: {e}")
        
        # Test the actual security validation
        print(f"\n🔒 SECURITY VALIDATION:")
        is_valid, message = trade_executor.security_manager.validate_trade_request(test_request, balance)
        print(f"   Valid: {is_valid}")
        print(f"   Message: {message}")
        
        return position_value
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        print(traceback.format_exc())
        return 0

def main():
    print("🔧 TRADE EXECUTION DEBUG")
    print("📋 Investigating insufficient funds error")
    print("")
    
    debug_trade_execution()

if __name__ == "__main__":
    main()