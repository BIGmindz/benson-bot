#!/usr/bin/env python3

import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

exchange = ccxt.kraken({
    'apiKey': os.getenv('KRAKEN_API_KEY'),
    'secret': os.getenv('KRAKEN_SECRET'),
    'sandbox': False,
    'enableRateLimit': True,
})

try:
    balance = exchange.fetch_balance()
    print('🏦 ALLOCATED POSITIONS (Non-zero balances):')
    total_usd_value = 0
    
    for currency, amounts in balance.items():
        if isinstance(amounts, dict) and amounts.get('total', 0) > 0.00001:
            free = amounts.get('free', 0)
            used = amounts.get('used', 0)
            total = amounts.get('total', 0)
            print(f'{currency}: Free={free:.8f}, Used={used:.8f}, Total={total:.8f}')
            
            # Get current price if it's not USD
            if currency == 'USD':
                total_usd_value += total
                print(f'  └─ USD value: ${total:.2f}')
            elif total > 0.00001:
                try:
                    symbol = f'{currency}/USD'
                    ticker = exchange.fetch_ticker(symbol)
                    usd_value = total * ticker['last']
                    total_usd_value += usd_value
                    print(f'  └─ {currency} value: ${usd_value:.2f} @ ${ticker["last"]:.4f}')
                except Exception as e:
                    print(f'  └─ Could not get USD value for {currency}: {e}')
    
    print(f'\n💰 TOTAL PORTFOLIO VALUE: ${total_usd_value:.2f}')
    print(f'🆓 Free USD for new trades: ${balance["USD"]["free"]:.2f}')
    print(f'📈 Allocated positions value: ${total_usd_value - balance["USD"]["free"]:.2f}')
                    
except Exception as e:
    print(f'❌ Error: {e}')