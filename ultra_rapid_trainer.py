#!/usr/bin/env python3
"""
30-Minute Ultra-Rapid Fire Training - 4 Trades Per Minute
High-intensity training session to stress-test our 50-symbol portfolio
15-second intervals for maximum pattern generation
"""

import time
import random
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import yaml
import numpy as np
import os
from dotenv import load_dotenv
from signals.supply_chain_signals import SupplyChainSignals, SupplyChainSignalsConfig

# Load environment variables from .env file
load_dotenv()
from profit_engine import ProfitEngine
from benson_config_manager import BensonConfigManager

class UltraRapidTrainer:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize ultra-rapid trainer for 30-minute 4-trades/min session"""
        
        # Load user configuration settings
        self.user_config = BensonConfigManager()
        self.feature_config = self.user_config.get_config_for_trading()
        
        # Load trading configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Check if live trading is enabled
        self.live_trading_mode = not self.config.get('paper_mode', True)
        
        if self.live_trading_mode:
            # Load live trading credentials from environment
            api_key = os.getenv('KRAKEN_API_KEY')
            api_secret = os.getenv('KRAKEN_SECRET')
            live_enabled = os.getenv('LIVE_TRADING_ENABLED', 'false').lower() == 'true'
            
            if not api_key or not api_secret:
                raise ValueError("🚨 LIVE TRADING REQUIRES KRAKEN_API_KEY and KRAKEN_SECRET environment variables")
            
            if not live_enabled:
                raise ValueError("🚨 Set LIVE_TRADING_ENABLED=true in environment to enable live trading")
            
            print("🚨 LIVE TRADING MODE ENABLED - USING REAL MONEY")
            print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")
            
            # Initialize exchange with live credentials
            self.exchange = ccxt.kraken({
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': False,  # LIVE TRADING
                'enableRateLimit': True,
            })
            
            # Import live trading portfolio
            from live_portfolio import LiveTradingPortfolio
            self.portfolio_class = LiveTradingPortfolio
            
        else:
            print("📋 PAPER TRADING MODE - Using simulated trades")
            # Initialize exchange for paper trading (no credentials needed)
            self.exchange = ccxt.kraken({
                'apiKey': '',
                'secret': '',
                'sandbox': False,  # Paper trading mode
                'enableRateLimit': True,
            })
            
            # Use standard paper trading portfolio
            from paper_portfolio import PaperTradingPortfolio
            self.portfolio_class = PaperTradingPortfolio
        
        # Initialize components
        self._initialize_components()
        
        # Premium quality training parameters - 30 minutes, 1 trade per minute
        self.ultra_settings = {
            'trades_per_minute': 1.0,        # TARGET: 1 premium trade per minute
            'trade_interval_seconds': 60,    # 60 seconds between trades for careful selection
            'session_duration': 1800,        # 30 minutes in seconds (1800)
            'starting_budget': 100.0,        # $100 starting budget
            'position_size_pct': 0.25,       # Base position size for premium trades
            'min_position_pct': 0.08,        # Minimum 8% positions for solid trades
            'max_position_pct': 0.95,        # Maximum 95% for ultra-high conviction trades
            'confidence_multiplier': 3.0,    # High scaling for premium quality
            'confidence_threshold': 75,      # HIGH threshold - only excellent trades
            'random_trade_pct': 0.05,        # Only 5% random trades - focus on quality
            'rsi_sensitivity': 0.82,         # Balanced sensitivity for quality detection
            'premium_quality_mode': True     # Enable premium 1-trade-per-minute mode
        }
        
        # Portfolio tracking
        self.portfolio_balance = self.ultra_settings['starting_budget']
        self.positions = {}
        self.trade_history = []
        self.portfolio_history = [{'timestamp': datetime.now(), 'balance': self.portfolio_balance}]
        
        # Session tracking
        self.session_id = f"ultra_rapid_{int(time.time())}"
        self.training_data = []
        
        # Performance metrics
        self.trade_interval = self.ultra_settings['trade_interval_seconds']  # 15 seconds between trades
        
        print("⚡ ULTRA-RAPID FIRE TRAINER INITIALIZED")
        print(f"🎯 Session: 30 minutes, 1 trade every 15 seconds = ~120 total trades")
        print(f"📊 Portfolio: {len(self.config['symbols'])} symbols")
        
    def _initialize_components(self):
        """Initialize all trading components"""
        # Supply chain signals
        if self.feature_config.get('supply_chain_enabled', True):
            try:
                supply_config = SupplyChainSignalsConfig(
                    enabled=True,
                    region="global",
                    sensitivity=self.feature_config.get('supply_chain_sensitivity', 1.0)
                )
                self.supply_chain_signals = SupplyChainSignals(supply_config)
                print("🔗 Supply Chain signals: ENABLED")
            except Exception as e:
                print(f"🔗 Supply Chain signals: DISABLED - {e}")
                self.supply_chain_signals = None
        else:
            self.supply_chain_signals = None
            
        # Learning engine
        if self.feature_config.get('learning_engine_enabled', True):
            try:
                from learning_engine import BensonLearningEngine
                self.learning_engine = BensonLearningEngine()
                self.has_learning_engine = True
                print("🧠 Learning Engine: ENABLED")
            except Exception as e:
                print(f"🧠 Learning Engine: DISABLED - {e}")
                self.learning_engine = None
                self.has_learning_engine = False
        else:
            self.learning_engine = None
            self.has_learning_engine = False
            
        # Profit engine
        if self.feature_config.get('profit_engine_enabled', True):
            try:
                self.profit_engine = ProfitEngine(initial_balance=self.ultra_settings['starting_budget'])
                print("💰 Profit Engine: ENABLED")
                self.has_profit_engine = True
            except Exception as e:
                print(f"💰 Profit Engine: DISABLED - {e}")
                self.profit_engine = None
                self.has_profit_engine = False
        else:
            self.profit_engine = None
            self.has_profit_engine = False
    
    def generate_market_conditions(self) -> Dict:
        """Generate realistic market conditions with supply chain data"""
        # Get real supply chain signals if available
        supply_chain_composite = 0.5
        supply_chain_factor = 1.0
        if self.supply_chain_signals:
            try:
                supply_chain_composite, _ = self.supply_chain_signals.composite()
                supply_chain_factor = self.supply_chain_signals.get_position_factor(supply_chain_composite)
            except:
                pass
        
        return {
            'market_trend': random.choice(['bullish', 'bearish', 'sideways']),
            'volatility': random.choice(['low', 'medium', 'high']),
            'supply_chain_composite': supply_chain_composite,
            'supply_chain_factor': supply_chain_factor,
            'sentiment_score': random.uniform(-1.0, 1.0),
            'brazil_factor': random.uniform(0.85, 1.15),
            'africa_factor': random.uniform(0.85, 1.15),
            'rsi_bias': random.uniform(-8, 8),
        }
    
    def calculate_rsi(self, symbol: str, conditions: Dict) -> float:
        """Generate synthetic RSI with bias for training"""
        base_rsi = random.uniform(20, 80)
        
        # Apply market trend bias
        if conditions['market_trend'] == 'bullish':
            base_rsi += random.uniform(0, 15)
        elif conditions['market_trend'] == 'bearish':
            base_rsi -= random.uniform(0, 15)
            
        # Apply volatility bias
        if conditions['volatility'] == 'high':
            base_rsi += random.uniform(-10, 10)
            
        # Apply conditions bias
        base_rsi += conditions['rsi_bias']
        
        return max(1, min(99, base_rsi))
    
    def should_buy(self, symbol: str, rsi: float, conditions: Dict) -> Tuple[bool, float]:
        """Determine if should buy with confidence score"""
        # RSI oversold signal (more aggressive for ultra-rapid)
        rsi_signal = 1.0 if rsi < 40 else (40 - rsi) / 20 if rsi < 60 else 0
        
        # Sentiment signal
        sentiment_signal = max(0, conditions['sentiment_score'])
        
        # Supply chain signal
        supply_signal = max(0, (conditions['supply_chain_factor'] - 1.0) * 5)
        
        # Regional signals
        brazil_signal = 1 if conditions['brazil_factor'] > 1.05 else 0
        africa_signal = 1 if conditions['africa_factor'] > 1.05 else 0
        
        # Signal weights (optimized for rapid fire)
        weights = {
            'rsi': 0.35,
            'sentiment': 0.25,
            'supply_chain': 0.20,
            'brazil': 0.10,
            'africa': 0.10
        }
        
        combined_score = (
            weights['rsi'] * rsi_signal +
            weights['sentiment'] * sentiment_signal +
            weights['supply_chain'] * supply_signal +
            weights['brazil'] * brazil_signal +
            weights['africa'] * africa_signal
        )
        
        should_buy_flag = combined_score > 0.4  # Lower threshold for more trades
        confidence = min(100, combined_score * 120)
        
        return should_buy_flag, confidence
    
    def should_sell(self, symbol: str, rsi: float, conditions: Dict) -> Tuple[bool, float]:
        """Determine if should sell with confidence score"""
        # RSI overbought signal
        rsi_signal = 1.0 if rsi > 60 else (rsi - 60) / 20 if rsi > 40 else 0
        
        # Bearish sentiment
        sentiment_signal = max(0, -conditions['sentiment_score'])
        
        # Supply chain stress
        supply_signal = max(0, (1.0 - conditions['supply_chain_factor']) * 5)
        
        # Regional stress signals
        brazil_signal = 1 if conditions['brazil_factor'] < 0.95 else 0
        africa_signal = 1 if conditions['africa_factor'] < 0.95 else 0
        
        # Signal weights
        weights = {
            'rsi': 0.35,
            'sentiment': 0.25,
            'supply_chain': 0.20,
            'brazil': 0.10,
            'africa': 0.10
        }
        
        combined_score = (
            weights['rsi'] * rsi_signal +
            weights['sentiment'] * sentiment_signal +
            weights['supply_chain'] * supply_signal +
            weights['brazil'] * brazil_signal +
            weights['africa'] * africa_signal
        )
        
        should_sell_flag = combined_score > 0.4
        confidence = min(100, combined_score * 120)
        
        return should_sell_flag, confidence
    
    def calculate_position_size(self, confidence: float, symbol: str) -> float:
        """Calculate position size for ultra-rapid trading"""
        if self.has_profit_engine:
            return self.profit_engine.calculate_scaled_position_size(confidence, confidence/100.0)
        
        # Ultra-rapid position sizing
        base_size = self.ultra_settings['position_size_pct']
        
        # Confidence scaling (less aggressive for volume)
        confidence_factor = (confidence / 100.0) * self.ultra_settings['confidence_multiplier']
        
        # Recent performance factor
        performance_factor = 1.0
        if len(self.trade_history) >= 10:
            recent_trades = self.trade_history[-10:]
            win_rate = sum(1 for t in recent_trades if t['outcome'] == 'profit') / len(recent_trades)
            performance_factor = 0.8 + (win_rate * 0.4)  # 0.8x to 1.2x based on win rate
        
        # Balance protection
        balance_factor = min(1.2, self.portfolio_balance / self.ultra_settings['starting_budget'])
        
        final_size = base_size * confidence_factor * performance_factor * balance_factor
        
        return max(self.ultra_settings['min_position_pct'], 
                  min(self.ultra_settings['max_position_pct'], final_size))
    
    def execute_trade(self, symbol: str, action: str, rsi: float, confidence: float, conditions: Dict) -> Dict:
        """Execute ultra-rapid paper trade"""
        timestamp = datetime.now()
        
        # Get price (with fallback for unavailable symbols)
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
        except:
            # Use synthetic price for paper trading
            price = random.uniform(0.01, 1000)
        
        # Calculate position
        position_size_pct = self.calculate_position_size(confidence, symbol)
        position_value = self.portfolio_balance * position_size_pct
        shares = position_value / price
        
        # Simulate outcome (more realistic for ultra-rapid)
        outcome_prob = (confidence / 100.0) * 0.7  # Base 70% success at 100% confidence
        
        # Market condition adjustments
        if conditions['market_trend'] == 'bullish' and action == 'BUY':
            outcome_prob *= 1.15
        elif conditions['market_trend'] == 'bearish' and action == 'SELL':
            outcome_prob *= 1.15
        else:
            outcome_prob *= 0.9
        
        # Execute outcome
        success = random.random() < outcome_prob
        if success:
            profit_pct = random.uniform(0.3, 2.0)  # Smaller profits for rapid fire
        else:
            profit_pct = random.uniform(-1.5, -0.3)  # Smaller losses
        
        # Update portfolio
        profit_loss = position_value * (profit_pct / 100)
        self.portfolio_balance += profit_loss
        
        # Record trade
        trade_data = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': action,
            'price': price,
            'shares': shares,
            'position_value': position_value,
            'position_pct': position_size_pct * 100,
            'rsi': rsi,
            'confidence': confidence,
            'outcome': 'profit' if success else 'loss',
            'profit_pct': profit_pct,
            'profit_loss': profit_loss,
            'new_balance': self.portfolio_balance,
            'session_id': self.session_id,
            'market_conditions': conditions
        }
        
        self.trade_history.append(trade_data)
        self.training_data.append(trade_data)
        self.portfolio_history.append({'timestamp': timestamp, 'balance': self.portfolio_balance})
        
        return trade_data
    
    def run_ultra_rapid_session(self):
        """Execute 30-minute ultra-rapid trading session"""
        print("\n" + "⚡" * 60)
        print("🚀 ULTRA-PREMIUM QUALITY TRAINING SESSION")
        print("⚡" * 60)
        print(f"⏱️  Duration: 30 minutes")
        print(f"💰 Starting Budget: ${self.ultra_settings['starting_budget']:.2f}")
        print(f"👑 Target Rate: 1 PREMIUM trade/minute (~30 total trades)")
        print(f"📊 Symbols: {len(self.config['symbols'])} cryptocurrencies")
        print(f"🎯 Session ID: {self.session_id}")
        print(f"� Position Range: {self.ultra_settings['min_position_pct']*100:.0f}% - {self.ultra_settings['max_position_pct']*100:.0f}% (HIGH CONVICTION)")
        print(f"🏆 Confidence Threshold: {self.ultra_settings['confidence_threshold']}% (HIGH QUALITY)")
        print()
        
        start_time = time.time()
        trade_interval = self.ultra_settings['trade_interval_seconds']  # 60 seconds between premium trades
        trades_executed = 0
        profitable_trades = 0
        next_trade_time = start_time
        
        print(f"⏰ Trade interval: {trade_interval:.1f} seconds")
        print("🔥 STARTING ULTRA-RAPID EXECUTION...")
        print()
        
        while time.time() < start_time + self.ultra_settings['session_duration']:
            current_time = time.time()
            
            # Only trade if it's time for the next trade
            if current_time >= next_trade_time:
                # Select symbol
                symbol = random.choice(self.config['symbols'])
                
                # Generate conditions
                conditions = self.generate_market_conditions()
                
                # Calculate RSI
                rsi = self.calculate_rsi(symbol, conditions)
                
                # Determine action
                if random.random() < self.ultra_settings['random_trade_pct']:
                    # Random trade for edge case learning
                    action = random.choice(['BUY', 'SELL'])
                    confidence = random.uniform(40, 80)
                    trade_type = "🎲 RANDOM"
                else:
                    # Intelligent decision
                    should_buy, buy_conf = self.should_buy(symbol, rsi, conditions)
                    should_sell, sell_conf = self.should_sell(symbol, rsi, conditions)
                    
                    if should_buy and buy_conf > self.ultra_settings['confidence_threshold']:
                        action = 'BUY'
                        confidence = buy_conf
                        trade_type = "🟢 BUY"
                    elif should_sell and sell_conf > self.ultra_settings['confidence_threshold']:
                        action = 'SELL'
                        confidence = sell_conf
                        trade_type = "🔴 SELL"
                    else:
                        action = 'HOLD'
                        confidence = 0
                        trade_type = "⚪ HOLD"
                
                # Execute trade
                if action != 'HOLD':
                    trade_result = self.execute_trade(symbol, action, rsi, confidence, conditions)
                    trades_executed += 1
                    if trade_result['outcome'] == 'profit':
                        profitable_trades += 1
                    
                    # Compact output for rapid fire
                    profit_emoji = "✅" if trade_result['outcome'] == 'profit' else "❌"
                    elapsed_min = (current_time - start_time) / 60
                    print(f"{profit_emoji} #{trades_executed:3d} | {elapsed_min:4.1f}m | {trade_type} {symbol:12} | ${trade_result['price']:8.4f} | {trade_result['position_pct']:4.1f}% | C:{confidence:3.0f}% | P:{trade_result['profit_pct']:+5.1f}% | Bal:${self.portfolio_balance:7.2f}")
                
                # Set next trade time
                next_trade_time = current_time + trade_interval
                
                # Periodic summary every 30 trades
                if trades_executed > 0 and trades_executed % 30 == 0:
                    elapsed_time = current_time - start_time
                    actual_rate = trades_executed / (elapsed_time / 60)
                    win_rate = (profitable_trades / trades_executed) * 100
                    total_return = ((self.portfolio_balance - self.ultra_settings['starting_budget']) / self.ultra_settings['starting_budget']) * 100
                    print(f"\n📊 CHECKPOINT: {trades_executed} trades | {actual_rate:.1f} t/min | WR: {win_rate:.1f}% | Return: {total_return:+.1f}%\\n")
                    
                    # Feed to learning engine
                    if self.has_learning_engine and len(self.training_data) >= 20:
                        self.feed_to_learning_engine()
            
            # Small sleep to prevent CPU overload
            time.sleep(0.1)
        
        # Final statistics
        total_time = time.time() - start_time
        actual_rate = trades_executed / (total_time / 60) if total_time > 0 else 0
        win_rate = (profitable_trades / trades_executed) * 100 if trades_executed > 0 else 0
        total_return = ((self.portfolio_balance - self.ultra_settings['starting_budget']) / self.ultra_settings['starting_budget']) * 100
        
        print("\\n" + "🏁" * 60)
        print("🏁 ULTRA-RAPID SESSION COMPLETE!")
        print("🏁" * 60)
        print(f"⏱️  Total Time: {total_time/60:.2f} minutes")
        print(f"📊 Total Trades: {trades_executed}")
        print(f"⚡ Actual Rate: {actual_rate:.1f} trades/minute")
        print(f"🎯 Target Rate: {self.ultra_settings['trades_per_minute']} trades/minute")
        print(f"💰 Starting Balance: ${self.ultra_settings['starting_budget']:.2f}")
        print(f"💰 Final Balance: ${self.portfolio_balance:.2f}")
        print(f"📈 Total Return: {total_return:+.2f}%")
        print(f"✅ Win Rate: {win_rate:.1f}% ({profitable_trades}/{trades_executed})")
        print(f"📚 Training Patterns: {len(self.training_data)}")
        
        # Save results
        self.save_session_results()
        
        # Final learning engine update
        if self.has_learning_engine:
            self.feed_to_learning_engine()
            print("🧠 Final patterns fed to Learning Engine")
        
        return {
            'trades_executed': trades_executed,
            'win_rate': win_rate,
            'total_return': total_return,
            'actual_rate': actual_rate
        }
    
    def feed_to_learning_engine(self):
        """Feed training data to learning engine"""
        if self.has_learning_engine and self.training_data:
            try:
                # Convert to learning engine format
                session_data = {
                    'session_id': self.session_id,
                    'trades': self.training_data,
                    'final_balance': self.portfolio_balance,
                    'session_type': 'ultra_rapid_training'
                }
                
                # Feed to learning engine
                self.learning_engine.learn_from_session(session_data)
                
                # Clear processed data
                self.training_data = []
                
            except Exception as e:
                print(f"⚠️ Learning engine error: {e}")
    
    def save_session_results(self):
        """Save ultra-rapid session results"""
        import json
        
        results = {
            'session_id': self.session_id,
            'session_type': 'ultra_rapid_30min',
            'settings': self.ultra_settings,
            'final_balance': self.portfolio_balance,
            'total_trades': len(self.trade_history),
            'profitable_trades': len([t for t in self.trade_history if t['outcome'] == 'profit']),
            'win_rate': len([t for t in self.trade_history if t['outcome'] == 'profit']) / len(self.trade_history) * 100 if self.trade_history else 0,
            'total_return_pct': ((self.portfolio_balance - self.ultra_settings['starting_budget']) / self.ultra_settings['starting_budget']) * 100,
            'trade_history': [
                {
                    'timestamp': str(t['timestamp']),
                    'symbol': t['symbol'],
                    'action': t['action'],
                    'price': t['price'],
                    'position_pct': t['position_pct'],
                    'confidence': t['confidence'],
                    'profit_pct': t['profit_pct'],
                    'outcome': t['outcome']
                } for t in self.trade_history
            ]
        }
        
        filename = f"ultra_rapid_session_{self.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")

def main():
    """Run ultra-rapid 30-minute training session"""
    print("⚡ Initializing Ultra-Rapid Fire Trainer...")
    trainer = UltraRapidTrainer()
    results = trainer.run_ultra_rapid_session()
    
    print(f"\\n🎯 MISSION ACCOMPLISHED!")
    print(f"Target: 4 trades/min → Achieved: {results['actual_rate']:.1f} trades/min")
    
    if results['actual_rate'] >= 4.0:
        print("🏆 SUCCESS: Target rate achieved!")
    elif results['actual_rate'] >= 3.5:
        print("⭐ GOOD: Close to target rate!")
    else:
        print("🔄 RETRY: Below target, consider optimization!")

if __name__ == "__main__":
    main()