import ccxt
import os
import yaml

def get_top_movers():
    """Fetches top 10 gainers and losers from Kraken."""
    try:
        exchange = ccxt.kraken()
        exchange.load_markets()
        tickers = exchange.fetch_tickers()
    except Exception as e:
        print(f"Error fetching data from Kraken: {e}")
        return [], []

    movers = []
    for symbol, ticker in tickers.items():
        if symbol.endswith('/USD') and ticker.get('change') is not None:
            # Use 'change' which is the 24h percentage change
            change_pct = ticker.get('percentage')
            if change_pct is not None:
                movers.append({'symbol': symbol, 'change': change_pct})

    # Sort by percentage change
    movers.sort(key=lambda x: x['change'], reverse=True)

    gainers = movers[:10]
    losers = movers[-10:]
    
    return [g['symbol'] for g in gainers], [l['symbol'] for l in losers]

def update_config_symbols(new_symbols):
    """Adds new symbols to the config file, avoiding duplicates."""
    config_path = 'config/config.yaml'
    if not os.path.exists(config_path):
        print(f"Config file not found at {config_path}")
        return

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    existing_symbols = set(config.get('symbols', []))
    
    # Add new symbols
    for symbol in new_symbols:
        existing_symbols.add(symbol)
        
    config['symbols'] = sorted(list(existing_symbols))

    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Successfully updated config with {len(new_symbols)} new symbols.")
    print(f"Total symbols being monitored: {len(config['symbols'])}")


if __name__ == "__main__":
    print("📈 Fetching top market movers from Kraken...")
    top_gainers, top_losers = get_top_movers()

    if not top_gainers and not top_losers:
        print("Could not retrieve market movers. Exiting.")
    else:
        print("\n--- Top 10 Gainers ---")
        for g in top_gainers:
            print(f"- {g}")
            
        print("\n--- Top 10 Losers ---")
        for l in top_losers:
            print(f"- {l}")

        update_config_symbols(top_gainers + top_losers)
