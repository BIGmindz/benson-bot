#!/usr/bin/env python3
import ccxt

def get_next_10_kraken_pairs():
    exchange = ccxt.kraken({'enableRateLimit': True})
    markets = exchange.load_markets()
    tickers = exchange.fetch_tickers()
    
    # Current top 10 in your bot
    current_top_10 = [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XMR/USDT', 'DOGE/USDT', 
        'XRP/USDT', 'AVAX/USDT', 'LTC/USDT', 'PENGU/USDT', 'ADA/USDT'
    ]
    
    # Get all USDT pairs
    usdt_pairs = []
    for symbol, ticker in tickers.items():
        if '/USDT' in symbol and ticker.get('quoteVolume'):
            # Skip stablecoins
            if any(stable in symbol.upper() for stable in ['USDC', 'RLUSD']):
                continue
            usdt_pairs.append({
                'symbol': symbol,
                'volume_24h': ticker['quoteVolume'],
                'price': ticker['last']
            })
    
    # Sort by volume
    usdt_pairs.sort(key=lambda x: x['volume_24h'], reverse=True)
    
    # Find next 10 (excluding current top 10)
    next_10 = []
    for pair in usdt_pairs:
        if pair['symbol'] not in current_top_10 and len(next_10) < 10:
            next_10.append(pair)
    
    print("🎯 NEXT TOP 10 COINS TO ADD:")
    print("="*50)
    for i, pair in enumerate(next_10, 11):
        print(f"{i:2d}. {pair['symbol']:>12} | Vol: ${pair['volume_24h']:>10,.0f}")
    
    # Generate the full list of 20
    all_symbols = [pair['symbol'] for pair in usdt_pairs[:20] if pair['symbol'] not in ['USDC/USDT', 'RLUSD/USDT']]
    print(f"\n🤖 UPDATED CONFIG FOR TOP 20 COINS:")
    print("symbols: [")
    for symbol in all_symbols[:20]:
        print(f'  "{symbol}",')
    print("]")
    
    return next_10

if __name__ == "__main__":
    get_next_10_kraken_pairs()