#!/usr/bin/env python3
"""
Test with BTC/USD instead of USDT pairs to see if it's a currency issue
"""

from trade_executor import create_trade_executor, TradeRequest, OrderSide

def test_btc_usd_trade():
    print("🔍 TESTING BTC/USD TRADE (NOT USDT)")
    print("=" * 50)
    
    try:
        trade_executor = create_trade_executor("config/config.yaml")
        
        # Check what markets are actually available
        markets = trade_executor.exchange.load_markets()
        
        print("📊 CHECKING AVAILABLE MARKETS:")
        btc_markets = [symbol for symbol in markets.keys() if 'BTC' in symbol and 'USD' in symbol]
        pengu_markets = [symbol for symbol in markets.keys() if 'PENGU' in symbol]
        
        print(f"   BTC pairs: {btc_markets[:5]}...")  # First 5
        print(f"   PENGU pairs: {pengu_markets}")
        
        # Test with BTC/USD specifically
        test_symbol = "BTC/USD"
        if test_symbol in markets:
            print(f"\n✅ {test_symbol} is available")
            
            # Get market info
            market_info = markets[test_symbol]
            min_amount = market_info.get('limits', {}).get('amount', {}).get('min', 0)
            min_cost = market_info.get('limits', {}).get('cost', {}).get('min', 0)
            
            print(f"   Min Amount: {min_amount} BTC")
            print(f"   Min Cost: ${min_cost:.2f}")
            
            # Test trade request
            test_request = TradeRequest(
                symbol=test_symbol,
                side=OrderSide.BUY,
                amount=0.0,  # Auto-calculate
                confidence=0.5,  # Low confidence = smaller position
                signal_strength=0.4,
                metadata={"test": "btc_usd_test"}
            )
            
            print(f"\n🎯 TESTING {test_symbol} TRADE:")
            result = trade_executor.execute_trade(test_request)
            
            if result.success:
                print(f"   ✅ SUCCESS! {test_symbol} trade worked")
                return True
            else:
                print(f"   ❌ FAILED: {result.error_message}")
        else:
            print(f"\n❌ {test_symbol} not available")
            
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    print("🔧 CURRENCY MISMATCH TEST")
    print("💡 Testing BTC/USD instead of USDT pairs")
    print("")
    
    success = test_btc_usd_trade()
    
    if success:
        print(f"\n🎉 BTC/USD WORKS!")
        print(f"💡 Problem is USDT vs USD currency mismatch")
        print(f"🔧 Need to use USD pairs instead of USDT")
    else:
        print(f"\n❌ Still failing - deeper issue")

if __name__ == "__main__":
    main()