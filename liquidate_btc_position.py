#!/usr/bin/env python3
"""
🎯 LIQUIDATE BTC.F POSITION TO CASH
Convert the $50 BTC.F position to USD for active trading
"""

import yaml
from trade_executor import create_trade_executor, TradeRequest, OrderSide, OrderType
from datetime import datetime

def liquidate_btc_position():
    """Liquidate BTC.F position to get cash for trading"""
    
    print("💰 LIQUIDATING BTC.F POSITION")
    print("=" * 50)
    
    try:
        # Create trade executor
        trade_executor = create_trade_executor("kraken_config_section.yaml")
        
        # Get current balance
        balance_info = trade_executor.exchange.fetch_balance()
        
        # Check BTC.F balance
        btc_f_balance = balance_info.get('BTC.F', {}).get('free', 0.0)
        print(f"🪙 BTC.F Balance: {btc_f_balance:.8f} BTC")
        
        if btc_f_balance <= 0:
            print("❌ No BTC.F position found to liquidate")
            return False
        
        # Get current BTC price
        current_price = trade_executor._get_current_price("BTC/USD")
        estimated_value = btc_f_balance * current_price
        
        print(f"💵 Estimated Value: ${estimated_value:.2f}")
        print(f"📈 Current BTC Price: ${current_price:.2f}")
        
        # Create sell order for BTC.F
        print(f"\n🔥 SELLING {btc_f_balance:.8f} BTC.F at market price...")
        
        # Check if we can sell BTC.F directly or need to convert
        # First try to get market info for BTC.F
        try:
            markets = trade_executor.exchange.load_markets()
            
            # Look for BTC.F/USD or similar pairs
            btc_f_pairs = [symbol for symbol in markets.keys() if 'BTC.F' in symbol and 'USD' in symbol]
            
            if btc_f_pairs:
                sell_pair = btc_f_pairs[0]
                print(f"📊 Found trading pair: {sell_pair}")
                
                # Create sell order
                order_result = trade_executor.exchange.create_order(
                    symbol=sell_pair,
                    type='market',
                    side='sell',
                    amount=btc_f_balance
                )
                
                print(f"✅ LIQUIDATION SUCCESSFUL!")
                print(f"📋 Order ID: {order_result.get('id', 'N/A')}")
                print(f"💰 Sold: {btc_f_balance:.8f} BTC.F")
                print(f"🎯 Estimated Proceeds: ${estimated_value:.2f}")
                
                return True
                
            else:
                print("⚠️  No direct BTC.F/USD pair found")
                print("🔄 May need to convert BTC.F to BTC first, then BTC to USD")
                
                # Try BTC.F to BTC conversion
                btc_pairs = [symbol for symbol in markets.keys() if 'BTC.F' in symbol and 'BTC' in symbol and 'BTC.F' != symbol.split('/')[1]]
                
                if btc_pairs:
                    convert_pair = btc_pairs[0]
                    print(f"🔄 Converting via: {convert_pair}")
                    
                    # This might be more complex - let's see what pairs are available
                    print("Available BTC.F pairs:")
                    for symbol in markets.keys():
                        if 'BTC.F' in symbol:
                            print(f"   {symbol}")
                    
                else:
                    print("❌ No conversion path found for BTC.F")
                    return False
        
        except Exception as e:
            print(f"❌ Error during liquidation: {e}")
            import traceback
            print(traceback.format_exc())
            return False
            
    except Exception as e:
        print(f"❌ Failed to create trade executor: {e}")
        return False

def check_new_balance():
    """Check balance after liquidation"""
    try:
        trade_executor = create_trade_executor("kraken_config_section.yaml")
        
        balance_info = trade_executor.exchange.fetch_balance()
        usd_balance = balance_info.get('USD', {}).get('free', 0.0)
        btc_f_balance = balance_info.get('BTC.F', {}).get('free', 0.0)
        
        print(f"\n💰 POST-LIQUIDATION BALANCE:")
        print(f"   USD: ${usd_balance:.2f}")
        print(f"   BTC.F: {btc_f_balance:.8f} BTC")
        
        return usd_balance
        
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return 0.0

def main():
    """Main liquidation process"""
    
    print(f"\n🎯 BTC.F LIQUIDATION SCRIPT")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Goal: Convert BTC.F position to USD for active trading\n")
    
    # Check current balance first
    print("🔍 CHECKING CURRENT BALANCE:")
    current_balance = check_new_balance()
    
    if current_balance > 10:
        print(f"✅ Already have ${current_balance:.2f} USD - liquidation may not be needed")
        return
    
    # Perform liquidation
    success = liquidate_btc_position()
    
    if success:
        # Check new balance
        new_balance = check_new_balance()
        print(f"\n🎉 LIQUIDATION COMPLETE!")
        print(f"💰 New USD Balance: ${new_balance:.2f}")
        
        if new_balance > 10:
            print("✅ Ready for active trading!")
        else:
            print("⚠️  Balance still low - check if liquidation completed")
    else:
        print("❌ Liquidation failed - manual intervention may be needed")

if __name__ == "__main__":
    main()