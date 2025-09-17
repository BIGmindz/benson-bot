#!/usr/bin/env python3
"""
🔄 SELL SMALL AMOUNT OF XRP FOR TESTING
Get $25 more for testing the corrected position sizing
"""

from trade_executor import create_trade_executor

def get_testing_funds():
    """Sell $25 worth of XRP for testing"""
    
    print("💰 GETTING TESTING FUNDS")
    print("=" * 40)
    
    try:
        trade_executor = create_trade_executor("kraken_config_section.yaml")
        
        # Check XRP balance
        balance_info = trade_executor.exchange.fetch_balance()
        xrp_balance = balance_info.get('XRP', {}).get('free', 0.0)
        current_price = trade_executor._get_current_price("XRP/USD")
        
        print(f"🪙 XRP Balance: {xrp_balance:.5f} XRP")
        print(f"📈 XRP Price: ${current_price:.4f}")
        
        # Calculate XRP to sell for $25
        target_usd = 25.0
        xrp_to_sell = target_usd / current_price
        
        print(f"🔄 Selling {xrp_to_sell:.5f} XRP for ${target_usd:.2f}")
        
        # Execute sale
        order_result = trade_executor.exchange.create_order(
            symbol="XRP/USD",
            type='market', 
            side='sell',
            amount=xrp_to_sell
        )
        
        print(f"✅ SALE SUCCESSFUL!")
        print(f"📋 Order ID: {order_result.get('id', 'N/A')}")
        print(f"💰 Sold: {xrp_to_sell:.5f} XRP")
        print(f"🎯 Expected: ~${target_usd:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔧 GETTING FUNDS FOR POSITION SIZE TESTING")
    print("💡 Selling $25 worth of XRP to test corrected bot")
    print("")
    
    success = get_testing_funds()
    
    if success:
        print(f"\n🎉 SUCCESS! Ready to test corrected position sizing")
        print(f"💡 Should now have ~$25 USD for testing")
        print(f"🧪 Bot will use 20% position sizing instead of 100%")

if __name__ == "__main__":
    main()