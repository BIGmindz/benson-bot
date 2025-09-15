# Most Volatile Crypto (MVC) — Benson Module

This module finds the **most volatile cryptocurrencies** over 30/60/90 days,
filters by liquidity, and exports candidates Benson can trade.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Dry run: top 25 by 30/60/90d annualized vol, MCAP>=100M, 24h Volume>=10M
python volatility_tracker.py --top 25 --min-mcap 100000000 --min-vol 10000000
```

Outputs:
- `exports/volatile_candidates.json` (for Benson ingestion)
- `exports/volatile_candidates.csv` (for review)
- SQLite DB optional (toggle in config)

## Integration points

- **File drop**: Benson polls `exports/volatile_candidates.json`
- **Webhook**: set `benson.webhook_url` + `benson.api_key` in `mvc_config.yaml`
- **Redis queue** (optional stub included)

## Notes
- Uses CoinGecko public endpoints for market caps, volumes, and price history.
- Volatility = annualized σ of daily log returns over 30/60/90d windows.
- Includes ATR(14) on daily candles (if OHLC endpoint available); falls back to close-to-close vol.
