#!/usr/bin/env python3
"""
Test the new safe order placement system
"""

import os
import sys
sys.path.append('/Users/johnbozza/Library/Mobile Documents/com~apple~CloudDocs/Benson Bot')

from dotenv import load_dotenv
load_dotenv()

from trade_executor import place_market_order_safe, create_trade_executor
from pprint import pprint

def test_safe_order_placement():
    print("🧪 TESTING SAFE ORDER PLACEMENT SYSTEM")
    print("=" * 50)
    
    try:
        # Create trade executor to get exchange instance
        executor = create_trade_executor()
        exchange = executor.exchange
        
        # Test dry run for BTC/USD
        print("\n🔍 DRY RUN TEST - BTC/USD BUY")
        result = place_market_order_safe(
            exchange=exchange,
            symbol="BTC/USD", 
            side="buy",
            desired_usd=10.0,  # Try to buy $10 worth
            dry_run=True,
            logger=print
        )
        
        print("Dry run result:")
        pprint(result)
        
        # Check available balance
        balance = exchange.fetch_balance()
        usd_free = balance.get('free', {}).get('USD', 0.0)
        print(f"\n💰 Current free USD: ${usd_free:.2f}")
        
        # Test environment variables
        print(f"\n⚙️ ENVIRONMENT SETTINGS:")
        print(f"BASE_TRADE_USD: ${os.getenv('BASE_TRADE_USD', '10')}")
        print(f"MAX_POSITION_PCT: {float(os.getenv('MAX_POSITION_PCT', '0.20'))*100}%")
        print(f"MIN_CASH_BUFFER_USD: ${os.getenv('MIN_CASH_BUFFER_USD', '5')}")
        print(f"SLIPPAGE_PCT: {float(os.getenv('SLIPPAGE_PCT', '0.005'))*100}%")
        
        # Calculate what the system would do
        buffer = float(os.getenv('MIN_CASH_BUFFER_USD', '5'))
        max_pct = float(os.getenv('MAX_POSITION_PCT', '0.20'))
        spendable = max(0.0, usd_free - buffer)
        max_by_pct = usd_free * max_pct
        
        print(f"\n📊 SAFE SIZING CALCULATION:")
        print(f"Free USD: ${usd_free:.2f}")
        print(f"After buffer (${buffer}): ${spendable:.2f}")
        print(f"Max by percentage ({max_pct*100}%): ${max_by_pct:.2f}")
        print(f"Final budget: ${min(10.0, spendable, max_by_pct):.2f}")
        
        if result['status'] == 'dry_run':
            print(f"\n✅ Safe order would trade: {result['amount']:.8f} BTC")
            print(f"✅ Estimated cost: ${result['notional']:.2f}")
            print(f"✅ Price with slippage: ${result['price']:.2f}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_safe_order_placement()