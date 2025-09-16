#!/usr/bin/env python3
import ccxt
import json
from datetime import datetime

def get_kraken_top_pairs():
    # Connect to Kraken
    exchange = ccxt.kraken({'enableRateLimit': True})
    
    print('🔄 Loading Kraken markets...')
    markets = exchange.load_markets()
    
    print('📊 Getting 24h ticker data...')
    tickers = exchange.fetch_tickers()
    
    # Filter for USDT pairs and sort by volume
    usdt_pairs = []
    for symbol, ticker in tickers.items():
        if '/USDT' in symbol and ticker.get('quoteVolume'):
            usdt_pairs.append({
                'symbol': symbol,
                'volume_24h': ticker['quoteVolume'],
                'price': ticker['last'],
                'change_24h': ticker.get('percentage', 0) or 0
            })
    
    # Sort by 24h volume
    usdt_pairs.sort(key=lambda x: x['volume_24h'], reverse=True)
    
    print('\n🚀 TOP 15 USDT PAIRS ON KRAKEN (by 24h volume):')
    print('=' * 80)
    for i, pair in enumerate(usdt_pairs[:15], 1):
        symbol = pair['symbol']
        volume = pair['volume_24h']
        price = pair['price']
        change = pair['change_24h']
        print(f'{i:2d}. {symbol:>12} | Vol: ${volume:>12,.0f} | Price: ${price:>10.4f} | Change: {change:>6.1f}%')
    
    print(f'\n📝 Total USDT pairs available: {len(usdt_pairs)}')
    print(f'🕒 Data as of: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Return top 10 symbols for bot configuration
    top_10_symbols = [pair['symbol'] for pair in usdt_pairs[:10]]
    print(f'\n🤖 Recommended symbols for Benson Bot:')
    print(f'symbols: {json.dumps(top_10_symbols, indent=2)}')
    
    return top_10_symbols

if __name__ == "__main__":
    get_kraken_top_pairs()