import pandas as pd
import time
import math
import os
import signal
from datetime import datetime, timezone
import yaml
from typing import Dict, Any
from dataclasses import dataclass
#from signals.africa_signals 
#import AfricaSignals, AfricaSignalsConfig
from signals.supply_chain_signals import SupplyChainSignals, SupplyChainSignalsConfig
from paper_portfolio import PaperTradingPortfolio
from learning_engine import BensonLearningEngine, apply_learned_optimizations


# ---------- Utilities ----------
def load_config(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found at {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)

def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

def wilder_rsi(close: pd.Series, period: int = 14) -> float:
    """Wilder's RSI using EMA for gains/losses (handles div-by-zero)."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's smoothing (EMA with alpha=1/period)
    avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()

    last_gain = avg_gain.iloc[-1]
    last_loss = avg_loss.iloc[-1]

    if last_loss == 0 and last_gain == 0:
        return 50.0
    if last_loss == 0:
        return 100.0

    rs = last_gain / last_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)

def calculate_rsi_from_ohlcv(ohlcv, period: int) -> float:
    closes = [c[4] for c in ohlcv]
    series = pd.Series(closes)
    if len(series) < period + 5:
        return float("nan")
    return wilder_rsi(series, period=period)

def backoff_sleep(attempt: int, base: float = 2.0, max_wait: float = 60.0):
    wait = min(max_wait, base ** attempt)
    time.sleep(wait)

def safe_fetch_ohlcv(exchange, symbol, timeframe, limit=200):
    return exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

def safe_fetch_ticker(exchange, symbol):
    t = exchange.fetch_ticker(symbol)
    price = t.get("last") or t.get("close")
    if price is None:
        raise RuntimeError(f"No price in ticker for {symbol}")
    return price

@dataclass
class SignalWeight:
    """Configuration for signal combination"""
    rsi_weight: float = 0.25
    sentiment_weight: float = 0.20
    brazil_weight: float = 0.20
    africa_weight: float = 0.175
    supply_chain_weight: float = 0.175

# ---------- Main ----------
def main():
    # Load config
    config_path = os.getenv("BENSON_CONFIG", "config/config.yaml")
    cfg = load_config(config_path)
    
    # Initialize learning engine and apply optimizations
    learning_engine = BensonLearningEngine()
    cfg = apply_learned_optimizations(cfg, learning_engine)
    
    # Display learning stats
    stats = learning_engine.get_learning_stats()
    print(f"🧠 LEARNING ENGINE: {stats['total_sessions']} sessions, {stats['learned_patterns']} patterns learned")
    if stats['best_session_return'] > 0:
        print(f"   Best session return: {stats['best_session_return']:.2f}%")
    
    fut_cfg = (cfg.get("futures") or {})
    futures_enabled = bool(fut_cfg.get("enabled", False))
    
    session_start_time = time.time()

    exchange_id = cfg.get("exchange", "binance")
    import ccxt
    exchange_cls = getattr(ccxt, exchange_id)
    exchange = exchange_cls({"enableRateLimit": True})

    exchange.load_markets()
    symbols = cfg["symbols"]
    invalid = [s for s in symbols if s not in exchange.markets]
    if invalid:
        raise ValueError(f"Invalid symbols for {exchange_id}: {invalid}")

    timeframe = cfg.get("timeframe", "5m")
    rsi_period = cfg["rsi"]["period"]
    buy_th = cfg["rsi"]["buy_threshold"]
    sell_th = cfg["rsi"]["sell_threshold"]
    cooldown_min = cfg.get("cooldown_minutes", 10)
    log_path = cfg.get("csv_log", "benson_signals.csv")

    # --- Africa Signals Initialization ---
    africa_signals = None
    africa_enabled = cfg.get('africa_signals', {}).get('enabled', False)
    if africa_enabled:
        # africa_config_dict = cfg['africa_signals']
        # africa_config = AfricaSignalsConfig(**africa_config_dict)
        # africa_signals = AfricaSignals(africa_config)
        print("🌍 Africa signals: ENABLED (but not implemented)")
    else:
        print("🌍 Africa signals: DISABLED")

    # --- Supply Chain Signals Initialization ---
    supply_chain_signals = None
    supply_chain_enabled = cfg.get('supply_chain_signals', {}).get('enabled', False)
    if supply_chain_enabled:
        supply_chain_config_dict = cfg['supply_chain_signals']
        supply_chain_config = SupplyChainSignalsConfig(**supply_chain_config_dict)
        supply_chain_signals = SupplyChainSignals(supply_chain_config)
        print("🚢 Supply Chain signals: ENABLED")
    else:
        print("🚢 Supply Chain signals: DISABLED")

    # --- Other signals: stubs (replace with real logic where needed) ---
    brazil_signals = None  # TODO: add Brazil signals logic
    sentiment_signals = None  # TODO: add Sentiment signals logic

    # Apply learned signal weights if available
    weights = SignalWeight()
    if 'optimized_weights' in cfg:
        opt_weights = cfg['optimized_weights']
        weights.rsi_weight = opt_weights.get('rsi', weights.rsi_weight)
        weights.supply_chain_weight = opt_weights.get('supply_chain', weights.supply_chain_weight)
        weights.africa_weight = opt_weights.get('africa', weights.africa_weight)
        weights.brazil_weight = opt_weights.get('brazil', weights.brazil_weight)
        weights.sentiment_weight = opt_weights.get('sentiment', weights.sentiment_weight)
        print(f"⚖️ Using optimized weights: RSI={weights.rsi_weight:.3f}, SC={weights.supply_chain_weight:.3f}")
    
    # Initialize paper trading portfolio if enabled
    portfolio = None
    if cfg.get("paper_mode", False):
        portfolio = PaperTradingPortfolio(cfg)

    # Debounce state per symbol
    last_signal: Dict[str, str] = {s: "HOLD" for s in symbols}
    last_alert_ts: Dict[str, float] = {s: 0.0 for s in symbols}
    cooldown_sec = cooldown_min * 60

    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write("ts_utc,exchange,symbol,price,rsi,signal,africa_composite,africa_factor,timeframe\n")

    print("🤖 Benson Bot Starting...")
    print(f"🌐 Exchange: {exchange_id}")
    print(f"📊 Monitoring: {symbols}")
    print(f"🕒 Timeframe: {timeframe}")
    print(f"📈 RSI: period={rsi_period} | Buy<{buy_th} | Sell>{sell_th}")
    print(f"🧯 Cooldown: {cooldown_min} min between repeated alerts per symbol")
    active = ["RSI"]
    if brazil_signals:
        active.append("Brazil")
    if sentiment_signals:
        active.append("Sentiment")
    if africa_signals:
        active.append("Africa")
    if supply_chain_signals:
        active.append("Supply Chain")
    print("Active signals: " + ", ".join(active))
    print("-" * 60)

    # Clean shutdown handling
    stop = {"flag": False}
    def handle_sigint(sig, frame):
        stop["flag"] = True
        print("\n🛑 Stopping gracefully...")
    signal.signal(signal.SIGINT, handle_sigint)

    attempt = 0
    poll_seconds = cfg.get("poll_seconds", 60)

    while not stop["flag"]:
        try:
            # Collect all prices for portfolio updates
            current_prices = {}
            
            for symbol in symbols:
                ohlcv = safe_fetch_ohlcv(exchange, symbol, timeframe, limit=200)
                rsi_val = calculate_rsi_from_ohlcv(ohlcv, rsi_period)

                if rsi_val is None or (isinstance(rsi_val, float) and math.isnan(rsi_val)):
                    print(f"[{utc_now_str()}] {symbol}: insufficient data for RSI yet.")
                    continue

                price = safe_fetch_ticker(exchange, symbol)
                current_prices[symbol] = price  # Store for portfolio updates

                # --- Africa signals ---
                africa_composite = None
                africa_factor = 1.0
                africa_logs = None
                if africa_signals:
                    try:
                        africa_composite, africa_logs = africa_signals.composite()
                        africa_factor = africa_signals.regional_factor(africa_composite)
                    except Exception as e:
                        print(f"Africa error: {e}")

                # --- Supply Chain signals ---
                supply_chain_composite = None
                supply_chain_factor = 1.0
                supply_chain_logs = None
                if supply_chain_signals:
                    try:
                        supply_chain_composite, supply_chain_logs = supply_chain_signals.composite()
                        supply_chain_factor = supply_chain_signals.get_position_factor(supply_chain_composite)
                    except Exception as e:
                        print(f"Supply Chain error: {e}")

                # --- Combine with other signals (add your real logic as needed) ---
                # Placeholder for sentiment/brazil signals
                sentiment_signal = 0
                brazil_signal = 0

                rsi_signal = 1 if rsi_val < buy_th else -1 if rsi_val > sell_th else 0

                combined_score = (
                    weights.rsi_weight * rsi_signal
                    + weights.sentiment_weight * sentiment_signal
                    + weights.brazil_weight * brazil_signal
                    + weights.africa_weight * (africa_factor if africa_signals else 0)
                    + weights.supply_chain_weight * (supply_chain_factor if supply_chain_signals else 0)
                )

                combined_signal = (
                    "BUY" if combined_score > 0.3 else
                    "SELL" if combined_score < -0.3 else
                    "HOLD"
                )

                # Print signals
                print(f"[{utc_now_str()}] {symbol:>12}: ${price:,.4f} | RSI {rsi_val:5.2f} | SC {supply_chain_factor:.2f} | Africa {africa_factor:.2f} | Combo {combined_signal}")
                
                # Optionally, print supply chain logs
                if supply_chain_logs:
                    print(f"    🚢 Supply Chain: {supply_chain_composite:.2f} congestion")
                    
                # Optionally, print Africa logs
                if africa_logs and 'signals' in africa_logs:
                    print(f"    Africa logs (top 3):")
                    for signal_name, score in list(africa_logs['signals'].items())[:3]:
                        print(f"      • {signal_name}: {score:.2f}")

                # Only alert on new actionable signals AND respect cooldown
                now = time.time()
                cooldown_ok = (now - last_alert_ts[symbol]) >= cooldown_sec
                changed = combined_signal != last_signal[symbol]

                if combined_signal in ("BUY", "SELL") and changed and cooldown_ok:
                    
                    # Check if we should avoid this trade based on learned failure patterns
                    should_avoid = False
                    avoid_reason = ""
                    
                    if combined_signal == "BUY" and learning_engine:
                        # Calculate current volatility estimate (using price changes)
                        volatility_estimate = abs(rsi_val - 50) / 50  # Simple volatility proxy
                        signal_weights = {"rsi": weights.rsi_weight, "supply_chain": weights.supply_chain_weight}
                        
                        should_avoid, avoid_reason = learning_engine.should_avoid_trade(
                            symbol, rsi_val, supply_chain_factor, volatility_estimate, signal_weights
                        )
                    
                    if should_avoid:
                        print(f"⚠️ TRADE AVOIDED: {symbol} {avoid_reason}")
                    else:
                        print(f"🚨 SIGNAL: {combined_signal} {symbol} @ ${price:,.4f} (RSI {rsi_val:0.2f}, Africa {africa_factor:.2f})")
                        last_alert_ts[symbol] = now
                        
                        # Execute paper trade if portfolio is enabled
                        if portfolio:
                            reason = f"RSI {rsi_val:.1f}"
                            if combined_signal == "BUY" and portfolio.can_open_position(symbol, price):
                                # Calculate confidence score for this trade
                                if learning_engine:
                                    confidence = learning_engine.calculate_trade_confidence(
                                        symbol, rsi_val, supply_chain_factor, volatility_estimate, signal_weights
                                    )
                                    reason += f" (Confidence: {confidence:.1%})"
                                
                                portfolio.open_position(symbol, "BUY", price, supply_chain_factor, reason)
                            elif combined_signal == "SELL" and symbol in portfolio.positions:
                                portfolio.close_position(symbol, price, reason)

                # Log to CSV (add Africa signals/combined signal if desired)
                with open(log_path, "a") as f:
                    f.write(f"{utc_now_str()},{exchange_id},{symbol},{price},{rsi_val:.4f},{combined_signal},{africa_composite},{africa_factor},{timeframe}\n")

                last_signal[symbol] = combined_signal

            # Update portfolio positions with current prices and check stop loss/take profit
            if portfolio and current_prices:
                portfolio.update_positions(current_prices)

            attempt = 0
            print("-" * 60)
            
            # Print portfolio status every 5 minutes (5 cycles)
            if portfolio and (time.time() % 300) < poll_seconds:
                portfolio.print_portfolio_status()
            
            time.sleep(poll_seconds)

        except Exception as e:
            attempt += 1
            print(f"❌ Error (attempt {attempt}): {type(e).__name__}: {e}")
            backoff_sleep(attempt)

    print("✅ Exit complete. Logs saved to:", log_path)
    
    # Learn from this session if portfolio was used
    if portfolio and learning_engine:
        session_duration = int(time.time() - session_start_time)
        print(f"\n🧠 ANALYZING SESSION ({session_duration}s)...")
        
        try:
            # Analyze the completed session
            session = learning_engine.analyze_session(portfolio, log_path, session_duration)
            print(f"📊 Session Performance: {session.total_return:.2f}% return, {session.win_rate*100:.1f}% win rate")
            
            # Learn from successful sessions
            updated_config = learning_engine.learn_from_session(session, cfg)
            
            # Save updated config if changed
            if updated_config != cfg:
                with open(config_path.replace('.yaml', '_optimized.yaml'), 'w') as f:
                    import yaml
                    yaml.dump(updated_config, f)
                print("💾 Saved optimized config to config_optimized.yaml")
                
        except Exception as e:
            print(f"⚠️ Learning analysis failed: {e}")

if __name__ == "__main__":
    main()


