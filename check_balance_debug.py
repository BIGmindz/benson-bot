#!/usr/bin/env python3
"""
Check account balance details
"""

import yaml
from trade_executor import create_trade_executor

def check_balance():
    try:
        trade_executor = create_trade_executor("kraken_config_section.yaml")
        
        # Get full balance info
        balance = trade_executor.exchange.fetch_balance()
        print("Full balance response:")
        print(balance)
        
        # Check different currency codes
        for currency in ['USD', 'ZUSD', 'USDC', 'FREE']:
            if currency in balance:
                print(f"{currency}: {balance[currency]}")
                
        usd_balance = trade_executor.get_account_balance()
        print(f"\nCalculated USD balance: ${usd_balance:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_balance()