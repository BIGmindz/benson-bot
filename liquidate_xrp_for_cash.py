#!/usr/bin/env python3
"""
💰 LIQUIDATE XRP POSITION FOR TRADING CASH
Sell $50 worth of XRP to get USD for active trading
Much safer than trying to deal with BTC.F futures
"""

import yaml
from trade_executor import create_trade_executor, TradeRequest, OrderSide, OrderType
from datetime import datetime

def liquidate_xrp_for_cash():
    """Sell $50 worth of XRP to get trading cash"""
    
    print("💰 LIQUIDATING XRP POSITION FOR TRADING CASH")
    print("=" * 60)
    
    try:
        # Create trade executor
        trade_executor = create_trade_executor("kraken_config_section.yaml")
        
        # Get current balance
        balance_info = trade_executor.exchange.fetch_balance()
        
        # Check XRP balance
        xrp_balance = balance_info.get('XRP', {}).get('free', 0.0)
        print(f"🪙 XRP Balance: {xrp_balance:.5f} XRP")
        
        if xrp_balance <= 0:
            print("❌ No XRP position found to liquidate")
            return False
        
        # Get current XRP price
        current_price = trade_executor._get_current_price("XRP/USD")
        total_value = xrp_balance * current_price
        
        print(f"💵 Total XRP Value: ${total_value:.2f}")
        print(f"📈 Current XRP Price: ${current_price:.4f}")
        
        # Calculate how much XRP to sell for $50
        target_usd = 50.0
        xrp_to_sell = target_usd / current_price
        
        if xrp_to_sell > xrp_balance:
            print(f"⚠️  Want to sell ${target_usd:.2f} but only have ${total_value:.2f} worth")
            print(f"🔧 Adjusting to sell all XRP: {xrp_balance:.5f} XRP")
            xrp_to_sell = xrp_balance
            target_usd = xrp_balance * current_price
        
        print(f"\n🔥 SELLING {xrp_to_sell:.5f} XRP for ~${target_usd:.2f}")
        
        # Create sell order
        order_result = trade_executor.exchange.create_order(
            symbol="XRP/USD",
            type='market',
            side='sell',
            amount=xrp_to_sell
        )
        
        print(f"✅ XRP LIQUIDATION SUCCESSFUL!")
        print(f"📋 Order ID: {order_result.get('id', 'N/A')}")
        print(f"💰 Sold: {xrp_to_sell:.5f} XRP")
        print(f"🎯 Expected Proceeds: ~${target_usd:.2f}")
        print(f"📊 Remaining XRP: {xrp_balance - xrp_to_sell:.5f} XRP (~${(xrp_balance - xrp_to_sell) * current_price:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during XRP liquidation: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def check_final_balance():
    """Check balance after XRP liquidation"""
    try:
        trade_executor = create_trade_executor("kraken_config_section.yaml")
        
        balance_info = trade_executor.exchange.fetch_balance()
        usd_balance = balance_info.get('USD', {}).get('free', 0.0)
        xrp_balance = balance_info.get('XRP', {}).get('free', 0.0)
        
        print(f"\n💰 POST-LIQUIDATION BALANCE:")
        print(f"   USD: ${usd_balance:.2f}")
        print(f"   XRP: {xrp_balance:.5f} XRP")
        
        if usd_balance > 45:  # Should be ~$50-$51 after selling
            print(f"✅ SUCCESS! Ready for active trading with ${usd_balance:.2f}")
            return True
        else:
            print(f"⚠️  Expected more USD - got ${usd_balance:.2f}")
            return False
        
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return False

def main():
    """Main liquidation process"""
    
    print(f"\n🎯 XRP LIQUIDATION SCRIPT")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Goal: Sell $50 worth of XRP to get USD for Benson Bot trading\n")
    
    # Show current situation
    print("🔍 CURRENT SITUATION:")
    print("   • BTC.F position is futures - complex to liquidate")
    print("   • XRP position is $478+ in liquid spot assets")
    print("   • XRP/USD pair is active and tradeable")
    print("   • Selling ~16.5 XRP leaves 140+ XRP remaining")
    
    # Confirm action
    print(f"\n⚠️  ABOUT TO SELL ~$50 WORTH OF XRP")
    print(f"   This will convert XRP to USD for active trading")
    
    # Perform liquidation
    success = liquidate_xrp_for_cash()
    
    if success:
        # Wait a moment for order to settle
        import time
        print(f"\n⏳ Waiting 3 seconds for order to settle...")
        time.sleep(3)
        
        # Check new balance
        balance_success = check_final_balance()
        
        if balance_success:
            print(f"\n🎉 LIQUIDATION COMPLETE!")
            print(f"🚀 Benson Bot ready for active trading!")
            print(f"💡 You can now restart the bot with sufficient funds")
        else:
            print(f"\n⚠️  Liquidation may need more time to settle")
    else:
        print("❌ Liquidation failed - check error messages above")

if __name__ == "__main__":
    main()