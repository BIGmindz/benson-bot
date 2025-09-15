#!/usr/bin/env python3
import argparse, math, os, sys, time, json, sqlite3, re
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import requests
import yaml
from tenacity import retry, wait_exponential, stop_after_attempt

############################
# Utilities
############################
def annualize_vol(logret_series: pd.Series, periods_per_year: int = 365) -> float:
    s = logret_series.dropna()
    if len(s) < 3:
        return np.nan
    return float(s.std(ddof=1) * math.sqrt(periods_per_year))

def pct(x, y):
    return (x / y - 1.0) if (x is not None and y not in (None, 0)) else np.nan

def is_excluded_symbol(sym: str) -> bool:
    s = sym.lower()
    # crude filters to avoid junk like 3L/3S tokens, leveraged products, pegs
    bad = ["bull", "bear", "3l", "3s", "up", "down", "leveraged", "eth2", "staked", "pegged"]
    return any(b in s for b in bad)

############################
# CoinGecko API
############################
CG_BASE = "https://api.coingecko.com/api/v3"

@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
def cg_get(path: str, params: Dict=None):
    url = f"{CG_BASE}{path}"
    r = requests.get(url, params=params, timeout=float(CONFIG['runtime']['request_timeout_s']))
    r.raise_for_status()
    return r.json()

def get_market_universe(vs: str, limit: int) -> pd.DataFrame:
    # paginate 250 per page
    out = []
    page = 1
    while len(out) < limit:
        per_page = min(250, limit - len(out))
        data = cg_get(
            "/coins/markets",
            params=dict(vs_currency=vs, order="market_cap_desc", per_page=per_page, page=page, price_change_percentage="24h")
        )
        if not data:
            break
        out.extend(data)
        page += 1
        time.sleep(0.8)  # be nice
    df = pd.DataFrame(out)
    return df

def get_price_history(coin_id: str, vs: str, days: int) -> pd.DataFrame:
    data = cg_get(f"/coins/{coin_id}/market_chart", params=dict(vs_currency=vs, days=days, interval="daily"))
    prices = data.get("prices", [])
    if not prices:
        return pd.DataFrame(columns=["date","close"])
    df = pd.DataFrame(prices, columns=["ts","close"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms").dt.date
    df = df.drop(columns=["ts"]).drop_duplicates("date").sort_values("date")
    return df[["date","close"]]

############################
# Core
############################
def compute_vols_for_coin(coin_row: pd.Series, horizons: List[int], vs: str, days: int) -> Dict:
    coin_id = coin_row["id"]
    sym = coin_row["symbol"].upper()
    name = coin_row["name"]
    hist = get_price_history(coin_id, vs, days)
    if hist.empty or hist["close"].isna().all():
        return {}
    hist["close"] = hist["close"].astype(float)
    hist["logret"] = np.log(hist["close"]).diff()

    res = {
        "id": coin_id,
        "symbol": sym,
        "name": name,
        "mcap": float(coin_row.get("market_cap") or np.nan),
        "vol24h_usd": float(coin_row.get("total_volume") or np.nan),
        "price": float(coin_row.get("current_price") or np.nan),
    }
    # per-horizon vols
    for h in horizons:
        # require enough observations
        window = hist.tail(h)
        if len(window) < max(3, int(h * CONFIG["scoring"]["min_obs_ratio"])):
            vol = np.nan
        else:
            vol = annualize_vol(window["logret"])
        res[f"vol_ann_{h}d"] = vol
    return res

def score_row(row: pd.Series, weights: Dict[str, float]) -> float:
    s = 0.0
    denom = 0.0
    for k, w in weights.items():
        v = row.get(f"vol_ann_{k[1:]}") if k.startswith("d") else row.get(f"vol_ann_{k}")
        # handle mapping: d30->vol_ann_30d
        if k.startswith("d"):
            h = int(k[1:])
            v = row.get(f"vol_ann_{h}d")
        if pd.notna(v):
            s += w * v
            denom += w
    return s / denom if denom > 0 else np.nan

def load_config(path="mvc_config.yaml") -> Dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_outputs(df: pd.DataFrame, cfg: Dict):
    # sort and trim
    topk = int(cfg["output"]["top_k"])
    out = df.sort_values("score", ascending=False).head(topk).copy()

    # write CSV
    csv_path = cfg["output"]["csv_path"]
    out.to_csv(csv_path, index=False)

    # write JSON (clean subset for Benson)
    keep = ["symbol","name","price","mcap","vol24h_usd","vol_ann_30d","vol_ann_60d","vol_ann_90d","score"]
    json_path = cfg["output"]["json_path"]
    with open(json_path, "w") as f:
        json.dump(out[keep].to_dict(orient="records"), f, indent=2)

    # optional SQLite
    if cfg["output"].get("write_sqlite"):
        import sqlite3, datetime as dt
        conn = sqlite3.connect(cfg["output"]["sqlite_path"])
        out.assign(run_ts=pd.Timestamp.utcnow().isoformat()).to_sql("volatile_candidates", conn, if_exists="append", index=False)
        conn.close()

    # optional webhook
    if cfg["benson"]["enabled"] and cfg["benson"]["mode"] == "webhook" and cfg["benson"]["webhook_url"]:
        try:
            hdrs = {"Content-Type":"application/json"}
            if cfg["benson"].get("api_key"):
                hdrs["Authorization"] = f"Bearer {cfg['benson']['api_key']}"
            with open(json_path, "r") as f:
                payload = json.load(f)
            requests.post(cfg["benson"]["webhook_url"], headers=hdrs, json={"candidates": payload}, timeout=15)
        except Exception as e:
            print(f"[warn] webhook failed: {e}", file=sys.stderr)

    print(f"Wrote: {csv_path} and {json_path}")

def main():
    parser = argparse.ArgumentParser(description="Most Volatile Crypto tracker")
    parser.add_argument("--config", default="mvc_config.yaml")
    parser.add_argument("--top", type=int, default=None, help="override top_k")
    parser.add_argument("--min-mcap", type=float, default=None)
    parser.add_argument("--min-vol", type=float, default=None)
    args = parser.parse_args()

    global CONFIG
    CONFIG = load_config(args.config)

    # CLI overrides
    if args.top is not None:
        CONFIG["output"]["top_k"] = int(args.top)
    if args.min_mcap is not None:
        CONFIG["universe"]["min_mcap"] = float(args.min_mcap)
    if args.min_vol is not None:
        CONFIG["universe"]["min_vol_24h"] = float(args.min_vol)

    vs = CONFIG["universe"]["vs_currency"]
    limit = int(CONFIG["universe"]["max_assets"])
    days = int(CONFIG["universe"]["days"])
    horizons = list(CONFIG["universe"]["horizons"])
    weights = CONFIG["scoring"]["weights"]

    # 1) Universe pull
    mkts = get_market_universe(vs, limit)

    # 2) Filters
    if CONFIG["universe"]["exclude_stablecoins"]:
        stable_like = ["usd", "usdt", "usdc", "busd", "tusd", "dai", "usde", "susd", "gusd", "usdd"]
        mkts = mkts[~mkts["symbol"].str.lower().isin(stable_like)]
    if CONFIG["universe"]["exclude_wrapped"]:
        mkts = mkts[~mkts["name"].str.contains("Wrapped", case=False, na=False)]
    if CONFIG["universe"]["exclude_leveraged_tokens"]:
        mkts = mkts[~mkts["symbol"].str.contains(r"(3l|3s|bull|bear|up|down)$", case=False, na=False)]
    # hard filter
    mkts = mkts[(mkts["market_cap"] >= CONFIG["universe"]["min_mcap"]) & (mkts["total_volume"] >= CONFIG["universe"]["min_vol_24h"])]
    mkts = mkts.reset_index(drop=True)

    rows = []
    for _, row in mkts.iterrows():
        res = compute_vols_for_coin(row, horizons, vs, days)
        if not res:
            continue
        rows.append(res)
        time.sleep(0.2)

    if not rows:
        print("No rows produced; consider relaxing filters.", file=sys.stderr)
        sys.exit(2)

    df = pd.DataFrame(rows)
    # rename vols for scoring convenience
    df = df.rename(columns={
        "vol_ann_30d":"vol_ann_30d",
        "vol_ann_60d":"vol_ann_60d",
        "vol_ann_90d":"vol_ann_90d",
    })
    # score
    def _score(r):
        s = 0.0; denom = 0.0
        # map keys like d30,d60,d90 to proper cols
        for k,w in weights.items():
            h = int(k[1:]) if k.startswith("d") else int(re.sub(r"[^0-9]","",k))
            v = r.get(f"vol_ann_{h}d", np.nan)
            if pd.notna(v):
                s += w * v; denom += w
        return s/denom if denom>0 else np.nan
    df["score"] = df.apply(_score, axis=1)

    # save
    save_outputs(df, CONFIG)

if __name__ == "__main__":
    main()
