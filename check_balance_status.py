#!/usr/bin/env python3
"""
Check current balance status
"""

from trade_executor import create_trade_executor

def check_balance_status():
    executor = create_trade_executor('kraken_config_section.yaml')
    balance_info = executor.exchange.fetch_balance()

    print('💰 CURRENT ACCOUNT STATUS:')
    print('=' * 40)

    # Check USD
    usd = balance_info.get('USD', {})
    print(f'USD: ${usd.get("free", 0):.2f} (free), ${usd.get("used", 0):.2f} (used), ${usd.get("total", 0):.2f} (total)')

    # Check for any positions that might be tying up funds
    print('\n📊 ALL POSITIONS WITH BALANCE:')
    for currency, data in balance_info.items():
        if isinstance(data, dict) and data.get('total', 0) > 0:
            total = data.get('total', 0)
            free = data.get('free', 0) 
            used = data.get('used', 0)
            print(f'{currency}: {free} (free), {used} (used), {total} (total)')

    # Check XRP balance specifically
    xrp = balance_info.get('XRP', {})
    xrp_balance = xrp.get('free', 0)
    print(f'\n🪙 XRP Available: {xrp_balance:.5f} XRP')

    if xrp_balance > 10:
        xrp_price = 3.04  # Approximate
        xrp_value = xrp_balance * xrp_price
        print(f'XRP Value: ~${xrp_value:.2f}')
        print('💡 SOLUTION: Can sell more XRP for trading funds')

if __name__ == "__main__":
    check_balance_status()