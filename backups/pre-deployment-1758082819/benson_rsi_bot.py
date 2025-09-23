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

# 🚀 ENTERPRISE TRADING MODULES
from trade_executor import TradeExecutor, TradeRequest, OrderSide, OrderType, create_trade_executor
from portfolio_manager import PortfolioManager
from enterprise_portfolio_manager import EnterprisePortfolioManager
from benson_config_manager import BensonConfigManager


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
    from dotenv import load_dotenv
    load_dotenv()
    kraken_api_key = os.getenv("KRAKEN_API_KEY")
    kraken_secret = os.getenv("KRAKEN_SECRET")
    exchange_kwargs = {"enableRateLimit": True}
    if exchange_id == "kraken" and kraken_api_key and kraken_secret:
        exchange_kwargs["apiKey"] = kraken_api_key
        exchange_kwargs["secret"] = kraken_secret
    exchange_cls = getattr(ccxt, exchange_id)
    exchange = exchange_cls(exchange_kwargs)

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
    
    # Initialize enterprise-grade portfolio management system
    portfolio = None
    trade_executor = None
    portfolio_manager = None
    enterprise_portfolio = None
    
    # Check if live trading is enabled
    is_live_trading = cfg.get("live_trading", {}).get("enabled", False) and not cfg.get("paper_mode", False)
    
    if is_live_trading:
        print("🏭 ENTERPRISE LIVE TRADING MODE ACTIVATED")
        try:
            # Initialize enterprise components with production standards
            config_manager = BensonConfigManager()
            enterprise_portfolio = EnterprisePortfolioManager(config_manager)
            trade_executor = create_trade_executor()
            portfolio_manager = PortfolioManager()
            
            # Generate enterprise readiness report
            readiness_report = enterprise_portfolio.get_trading_readiness_report()
            
            # Enhanced startup diagnostics
            portfolio = trade_executor.get_total_portfolio_value()
            total_value = portfolio['total_usd_value']
            free_usd = portfolio['free_usd']
            allocated_value = total_value - free_usd
            
            print(f"� ENTERPRISE PORTFOLIO STATUS:")
            print(f"   Total Value: ${total_value:.2f}")
            print(f"   Free USD: ${free_usd:.2f}")
            print(f"   Allocated: ${allocated_value:.2f}")
            print(f"   Health Score: {readiness_report['health_metrics'].health_score:.2f}/1.00")
            print(f"   Trading Ready: {'✅ YES' if readiness_report.get('trading_ready') else '❌ NO'}")
            
            if not readiness_report.get('trading_ready'):
                print("⚠️ WARNING: System not optimally ready for trading")
                for rec in readiness_report.get('recommendations', []):
                    print(f"   • {rec}")
                    
            if allocated_value > 0:
                print(f"   Allocated Positions: ${allocated_value:.2f}")
                print(f"   🔄 Portfolio liquidation system: ACTIVE")
            
            if total_value < 20.0:
                print("⚠️ WARNING: Low portfolio value for active trading")
            elif total_value >= 100.0:
                print(f"✅ Portfolio size excellent for active trading")
            else:
                print(f"✅ Portfolio size adequate for trading")
            
            print("✅ Live trading components initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize live trading: {e}")
            print("🔄 Falling back to paper trading mode")
            is_live_trading = False
            portfolio = PaperTradingPortfolio(cfg)
    
    else:
        print("📄 Paper trading mode")
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
                        
                        # Calculate confidence and signal strength
                        volatility_estimate = abs(rsi_val - 50) / 50  # Simple volatility proxy
                        signal_weights = {"rsi": weights.rsi_weight, "supply_chain": weights.supply_chain_weight}
                        
                        confidence = 0.5  # Default confidence
                        signal_strength = abs(combined_score)  # Signal strength from combined score
                        
                        if learning_engine:
                            confidence = learning_engine.calculate_trade_confidence(
                                symbol, rsi_val, supply_chain_factor, volatility_estimate, signal_weights
                            )
                        
                        # 🚀 ENTERPRISE LIVE TRADING EXECUTION
                        if is_live_trading and trade_executor and portfolio_manager and enterprise_portfolio:
                            try:
                                # Pre-trade health check
                                health_metrics = enterprise_portfolio.get_health_metrics()
                                
                                if health_metrics.health_score < 0.5:
                                    print(f"⚠️ TRADE DEFERRED: Low health score {health_metrics.health_score:.2f}")
                                    continue
                                
                                # Create trade request with enterprise validation
                                trade_request = TradeRequest(
                                    symbol=symbol,
                                    side=OrderSide.BUY if combined_signal == "BUY" else OrderSide.SELL,
                                    amount=0.0,  # Auto-calculate based on confidence
                                    confidence=confidence,
                                    signal_strength=signal_strength,
                                    metadata={
                                        "rsi": rsi_val,
                                        "supply_chain_factor": supply_chain_factor,
                                        "africa_factor": africa_factor,
                                        "health_score": health_metrics.health_score,
                                        "reason": f"RSI {rsi_val:.1f}, SC {supply_chain_factor:.2f}"
                                    }
                                )
                                
                                # Enterprise trade execution with comprehensive monitoring
                                result = enterprise_portfolio.execute_trade_with_monitoring(trade_request)
                                
                                if result.success:
                                    print(f"✅ ENTERPRISE TRADE EXECUTED: {result.symbol} {result.side.upper()} ${result.amount * result.price:.2f}")
                                    print(f"   Health Score: {health_metrics.health_score:.2f} | Liquidity: ${health_metrics.available_liquidity:.2f}")
                                    
                                    # Add position to portfolio manager with enterprise monitoring
                                    portfolio_manager.add_position(
                                        result, confidence, signal_strength,
                                        stop_loss=price * 0.98,  # 2% stop loss
                                        take_profit=price * 1.05  # 5% take profit
                                    )
                                else:
                                    print(f"❌ ENTERPRISE TRADE FAILED: {result.error_message}")
                                    enterprise_portfolio.log_trade_failure(trade_request, result.error_message)
                            
                            except Exception as e:
                                print(f"💥 ENTERPRISE TRADE ERROR: {e}")
                                enterprise_portfolio.handle_trade_error(e, trade_request)
                        
                        # Execute paper trade for comparison/backup
                        elif portfolio:
                            reason = f"RSI {rsi_val:.1f}"
                            if combined_signal == "BUY" and portfolio.can_open_position(symbol, price):
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
            
            # 🎯 ENTERPRISE PORTFOLIO MANAGEMENT & MONITORING
            if is_live_trading and portfolio_manager and enterprise_portfolio and current_prices:
                try:
                    # Update live positions with current prices
                    for position in portfolio_manager.get_open_positions():
                        if position.symbol in current_prices:
                            portfolio_manager.update_position(position.id, current_prices[position.symbol])
                    
                    # Enterprise health monitoring and automated management
                    health_metrics = enterprise_portfolio.get_health_metrics()
                    session_metrics = enterprise_portfolio.get_session_metrics()
                    
                    # Check for stop loss/take profit triggers with enterprise monitoring
                    positions_to_close = portfolio_manager.check_stop_loss_take_profit(current_prices)
                    
                    for position_id in positions_to_close:
                        # Close the position with enterprise logging
                        close_result = trade_executor.close_position(position_id)
                        if close_result.success:
                            portfolio_manager.close_position(position_id, close_result)
                            enterprise_portfolio.log_position_close(position_id, close_result, "stop_loss_take_profit")
                    
                    # Get and log comprehensive portfolio metrics
                    portfolio = trade_executor.get_total_portfolio_value()
                    current_balance = portfolio['total_usd_value']  # Use total portfolio value
                    portfolio_metrics = portfolio_manager.get_portfolio_metrics(current_balance)
                    
                    # Enterprise-grade status reporting
                    if len(portfolio_manager.get_open_positions()) > 0:
                        print(f"📊 ENTERPRISE PORTFOLIO STATUS:")
                        print(f"   Total Value: ${portfolio_metrics.total_value:.2f} | P&L: ${portfolio_metrics.total_pnl:.2f}")
                        print(f"   Win Rate: {portfolio_metrics.win_rate:.1f}% | Health: {health_metrics.health_score:.2f}")
                        print(f"   Session Trades: {session_metrics.total_trades} | Success Rate: {session_metrics.success_rate:.1f}%")
                        
                        # Risk monitoring alerts
                        if health_metrics.health_score < 0.6:
                            print(f"   ⚠️ HEALTH ALERT: Score {health_metrics.health_score:.2f} - Enhanced monitoring active")
                        if session_metrics.failure_rate > 0.3:
                            print(f"   🔴 FAILURE ALERT: {session_metrics.failure_rate:.1%} failure rate - Consider reducing exposure")
                    
                    # Automated portfolio rebalancing check
                    if enterprise_portfolio.should_rebalance_portfolio():
                        rebalance_actions = enterprise_portfolio.get_rebalancing_recommendations()
                        print(f"🔄 REBALANCING RECOMMENDED: {len(rebalance_actions)} actions suggested")
                        # Note: Actual rebalancing would be implemented based on risk tolerance
                    
                    # Save comprehensive portfolio snapshot every hour
                    if int(time.time()) % 3600 < 30:  # Within first 30 seconds of each hour
                        portfolio_manager.save_portfolio_snapshot(portfolio_metrics)
                        enterprise_portfolio.save_health_snapshot(health_metrics, session_metrics)
                
                except Exception as e:
                    print(f"⚠️ Enterprise portfolio management error: {e}")
                    enterprise_portfolio.handle_monitoring_error(e)

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


