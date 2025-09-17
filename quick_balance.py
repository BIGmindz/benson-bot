#!/usr/bin/env python3
"""
Quick balance check
"""

from trade_executor import create_trade_executor

executor = create_trade_executor("config/config.yaml")
balance_info = executor.exchange.fetch_balance()

print("💰 CURRENT USD BALANCE:")
usd = balance_info.get('USD', {})
print(f"   Free: ${usd.get('free', 0):.2f}")
print(f"   Used: ${usd.get('used', 0):.2f}") 
print(f"   Total: ${usd.get('total', 0):.2f}")

print(f"\n📊 RECENT POSITION CHANGES:")
# Check for any new positions since earlier
for currency, data in balance_info.items():
    if isinstance(data, dict) and data.get('total', 0) > 0:
        total = data.get('total', 0)
        if currency not in ['BABY', 'BADGER', 'CCD', 'ETH.B', 'ETH.F', 'PEPE', 'RENDER', 'SEI.B', 'SOL.F', 'SOL03.S', 'USDG.F', 'BTC.F', 'XRP', 'USD']:
            print(f"   NEW: {currency}: {total}")