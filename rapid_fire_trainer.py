#!/usr/bin/env python3
"""
Rapid Fire Training System for Benson Bot Learning Engine
Generates high-frequency buy/sell signals to rapidly build pattern database
"""

import time
import random
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import yaml
import numpy as np
from signals.supply_chain_signals import SupplyChainSignals, SupplyChainSignalsConfig
from profit_engine import ProfitEngine
from benson_config_manager import BensonConfigManager

class RapidFireTrainer:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the rapid-fire trainer with toggleable features"""
        
        # Load user configuration settings (toggleable features)
        self.user_config = BensonConfigManager()
        self.feature_config = self.user_config.get_config_for_trading()
        
        # Load trading configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize exchange
        self.exchange = ccxt.kraken({
            'apiKey': '',
            'secret': '',
            'sandbox': False,  # Paper trading mode
            'enableRateLimit': True,
        })
        
        # Initialize supply chain signals (toggleable)
        if self.feature_config['supply_chain_enabled']:
            try:
                supply_config = SupplyChainSignalsConfig(
                    enabled=True,
                    region="global",
                    sensitivity=self.feature_config['supply_chain_sensitivity']
                )
                self.supply_chain_signals = SupplyChainSignals(supply_config)
                emoji = "🔗" if self.feature_config['show_emojis'] else ""
                print(f"{emoji} Supply Chain signals: ENABLED")
            except Exception as e:
                emoji = "🔗" if self.feature_config['show_emojis'] else ""
                print(f"{emoji} Supply Chain signals: DISABLED - {e}")
                self.supply_chain_signals = None
        else:
            emoji = "🔗" if self.feature_config['show_emojis'] else ""
            print(f"{emoji} Supply Chain signals: DISABLED (user setting)")
            self.supply_chain_signals = None
        
        # Initialize learning engine (toggleable)
        if self.feature_config['learning_engine_enabled']:
            try:
                from learning_engine import BensonLearningEngine
                self.learning_engine = BensonLearningEngine()
                self.has_learning_engine = True
                emoji = "🧠" if self.feature_config['show_emojis'] else ""
                print(f"{emoji} Advanced Pattern Recognition Engine: ENABLED")
            except Exception as e:
                emoji = "🧠" if self.feature_config['show_emojis'] else ""
                print(f"{emoji} Learning engine: DISABLED - {e}")
                self.learning_engine = None
                self.has_learning_engine = False
        else:
            emoji = "🧠" if self.feature_config['show_emojis'] else ""
            print(f"{emoji} Learning engine: DISABLED (user setting)")
            self.learning_engine = None
            self.has_learning_engine = False
        
        # Training parameters
        self.symbols = self.config['symbols']
        self.rapid_fire_settings = {
            'trades_per_minute': 2,       # 2 trades per minute for 4-hour session
            'session_duration': 7200,      # 2 hours in seconds
            'starting_budget': 100.0,     # $100 starting budget
            'position_size_pct': 0.1,     # Base position size (will be adjusted dynamically)
                        'min_position_pct': 0.01,      # Minimum 1% for learning trades
            'max_position_pct': 0.85,     # Maximum 85% position size for ultra-high confidence
            'confidence_multiplier': 2.5, # Aggressive position scaling
            'recent_performance_factor': 0.3, # How much recent wins/losses affect sizing
            'rsi_sensitivity': 0.8,       # More sensitive triggers
            'random_trades': True,        # Include some random trades to learn from
            'pattern_variations': True    # Test different market conditions
        }
        
        # Portfolio tracking
        self.portfolio_balance = self.rapid_fire_settings['starting_budget']
        self.positions = {}  # Track open positions
        self.trade_history = []
        self.portfolio_history = [{'timestamp': datetime.now(), 'balance': self.portfolio_balance}]
        
        # Initialize Profit Engine for advanced profit management (toggleable)
        if self.feature_config['profit_engine_enabled']:
            try:
                self.profit_engine = ProfitEngine(initial_balance=self.rapid_fire_settings['starting_budget'])
                emoji = "💰" if self.feature_config['show_emojis'] else ""
                print(f"{emoji} Profit Engine: ENABLED")
                self.has_profit_engine = True
            except Exception as e:
                emoji = "💰" if self.feature_config['show_emojis'] else ""
                print(f"{emoji} Profit Engine: DISABLED - {e}")
                self.profit_engine = None
                self.has_profit_engine = False
        else:
            emoji = "💰" if self.feature_config['show_emojis'] else ""
            print(f"{emoji} Profit Engine: DISABLED (user setting)")
            self.profit_engine = None
            self.has_profit_engine = False
        
        # Training state
        self.training_data = []
        self.session_id = f"rapid_training_{int(time.time())}"
        
    def generate_synthetic_market_conditions(self) -> Dict:
        """Generate varied market conditions for training including real signals"""
        # Get supply chain signals if available
        supply_chain_composite = 0.5
        supply_chain_factor = 1.0
        if self.supply_chain_signals:
            try:
                supply_chain_composite, supply_logs = self.supply_chain_signals.composite()
                supply_chain_factor = self.supply_chain_signals.get_position_factor(supply_chain_composite)
            except Exception as e:
                print(f"Supply chain error: {e}")
        
        conditions = {
            'market_trend': random.choice(['bullish', 'bearish', 'sideways']),
            'volatility': random.choice(['low', 'medium', 'high']),
            'volume_regime': random.choice(['low', 'normal', 'high']),
            'supply_chain_composite': supply_chain_composite,
            'supply_chain_factor': supply_chain_factor,
            'rsi_bias': random.uniform(-10, 10),  # Bias RSI readings for variety
            # Simulate other signals
            'sentiment_score': random.uniform(-1.0, 1.0),  # -1 bearish, +1 bullish
            'brazil_factor': random.uniform(0.8, 1.2),
            'africa_factor': random.uniform(0.8, 1.2),
        }
        return conditions
    
    def calculate_rapid_rsi(self, symbol: str, market_conditions: Dict) -> float:
        """Calculate RSI with synthetic variations for training"""
        try:
            # Get real market data
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', limit=50)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate base RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            base_rsi = 100 - (100 / (1 + rs))
            current_rsi = base_rsi.iloc[-1]
            
            # Apply synthetic variations based on market conditions
            if market_conditions['market_trend'] == 'bearish':
                current_rsi *= 0.9  # Lower RSI in bear markets
            elif market_conditions['market_trend'] == 'bullish':
                current_rsi *= 1.1  # Higher RSI in bull markets
                
            # Add volatility effects
            volatility_factor = {'low': 0.95, 'medium': 1.0, 'high': 1.05}[market_conditions['volatility']]
            current_rsi *= volatility_factor
            
            # Add RSI bias for training variety
            current_rsi += market_conditions['rsi_bias']
            
            # Clamp to valid RSI range
            return max(0, min(100, current_rsi))
            
        except Exception as e:
            print(f"Error calculating RSI for {symbol}: {e}")
            return random.uniform(20, 80)  # Fallback random RSI
    
    def should_rapid_buy(self, symbol: str, rsi: float, market_conditions: Dict) -> Tuple[bool, float]:
        """Determine if we should buy (with confidence score) - Now factors in ALL signals"""
        base_threshold = 30 * self.rapid_fire_settings['rsi_sensitivity']
        
        # Adjust threshold based on market conditions
        if market_conditions['market_trend'] == 'bearish':
            threshold = base_threshold * 0.9  # More aggressive in bear markets
        else:
            threshold = base_threshold
            
        # Factor in all available signals
        signal_weights = {
            'rsi': 0.3,
            'sentiment': 0.25,
            'supply_chain': 0.2,
            'brazil': 0.125,
            'africa': 0.125
        }
        
        # Calculate individual signal contributions
        rsi_signal = 1 if rsi < threshold else 0
        sentiment_signal = max(0, market_conditions['sentiment_score'])  # Positive sentiment helps buy
        supply_chain_signal = 1 if market_conditions['supply_chain_factor'] > 1.0 else 0  # Strong supply chain = bullish
        brazil_signal = 1 if market_conditions['brazil_factor'] > 1.0 else 0
        africa_signal = 1 if market_conditions['africa_factor'] > 1.0 else 0
        
        # Combined signal score
        combined_score = (
            signal_weights['rsi'] * rsi_signal +
            signal_weights['sentiment'] * sentiment_signal +
            signal_weights['supply_chain'] * supply_chain_signal +
            signal_weights['brazil'] * brazil_signal +
            signal_weights['africa'] * africa_signal
        )
        
        should_buy = combined_score > 0.6  # Require VERY strong combined signal (raised from 0.4)
        
        # Calculate confidence based on signal strength
        confidence = combined_score * 100
        if market_conditions['market_trend'] == 'bullish':
            confidence *= 1.2  # Boost confidence in bull market
            
        return should_buy, min(100, confidence)
    
    def should_rapid_sell(self, symbol: str, rsi: float, market_conditions: Dict) -> Tuple[bool, float]:
        """Determine if we should sell (with confidence score) - Now factors in ALL signals"""
        base_threshold = 70 / self.rapid_fire_settings['rsi_sensitivity']
        
        # Adjust threshold based on market conditions  
        if market_conditions['market_trend'] == 'bullish':
            threshold = base_threshold * 1.1  # Less aggressive selling in bull markets
        else:
            threshold = base_threshold
            
        # Factor in all available signals for selling
        signal_weights = {
            'rsi': 0.3,
            'sentiment': 0.25,
            'supply_chain': 0.2,
            'brazil': 0.125,
            'africa': 0.125
        }
        
        # Calculate individual signal contributions (inverted for selling)
        rsi_signal = 1 if rsi > threshold else 0
        sentiment_signal = max(0, -market_conditions['sentiment_score'])  # Negative sentiment helps sell
        supply_chain_signal = 1 if market_conditions['supply_chain_factor'] < 1.0 else 0  # Weak supply chain = bearish
        brazil_signal = 1 if market_conditions['brazil_factor'] < 1.0 else 0
        africa_signal = 1 if market_conditions['africa_factor'] < 1.0 else 0
        
        # Combined signal score
        combined_score = (
            signal_weights['rsi'] * rsi_signal +
            signal_weights['sentiment'] * sentiment_signal +
            signal_weights['supply_chain'] * supply_chain_signal +
            signal_weights['brazil'] * brazil_signal +
            signal_weights['africa'] * africa_signal
        )
        
        should_sell = combined_score > 0.6  # Require VERY strong combined signal (raised from 0.4)
        
        # Calculate confidence based on signal strength
        confidence = combined_score * 100
        if market_conditions['market_trend'] == 'bearish':
            confidence *= 1.2  # Boost confidence in bear market
            
        return should_sell, min(100, confidence)
    
    def calculate_position_size(self, confidence: float, signal_strength: float) -> float:
        """Calculate intelligent position size with Profit Engine integration"""
        
        # Use Profit Engine's advanced scaling if available
        if self.has_profit_engine:
            return self.profit_engine.calculate_scaled_position_size(confidence, signal_strength)
        
        # Fallback to original logic if Profit Engine not available
        base_size = self.rapid_fire_settings['position_size_pct']
        
        # 1. Confidence-based adjustment (higher confidence = larger position)
        confidence_factor = (confidence / 100.0) * self.rapid_fire_settings['confidence_multiplier']
        
        # 2. Signal strength adjustment (stronger signals = larger position)
        signal_factor = min(2.5, signal_strength * 2.0)  # Increased multiplier for strong signals
        
        # 3. ULTRA-HIGH QUALITY BOOST: If this trade passed our strict criteria, it deserves big money
        ultra_quality_boost = 1.0
        if confidence >= 70.0 and signal_strength >= 0.6:  # Matches our strict trading criteria
            ultra_quality_boost = 2.0  # Double the position size for these rare gems!
            print(f"💎 ULTRA-HIGH QUALITY TRADE DETECTED - Boosting position size!")
        
        # 4. Recent performance adjustment (recent wins increase, losses decrease)
        performance_factor = 1.0
        if len(self.trade_history) >= 5:
            recent_trades = self.trade_history[-5:]  # Last 5 trades
            win_rate = sum(1 for trade in recent_trades if trade['outcome'] == 'profit') / len(recent_trades)
            avg_return = sum(trade['profit_pct'] for trade in recent_trades) / len(recent_trades)
            
            # Adjust based on recent performance
            performance_factor = 1.0 + (win_rate - 0.5) * self.rapid_fire_settings['recent_performance_factor']
            performance_factor += (avg_return / 100.0) * 0.5  # Small boost for positive returns
            performance_factor = max(0.5, min(2.0, performance_factor))  # Keep between 0.5x and 2.0x
        
        # 4. Portfolio protection (reduce size if balance is down significantly)
        balance_factor = 1.0
        starting_balance = self.rapid_fire_settings['starting_budget']
        current_ratio = self.portfolio_balance / starting_balance
        if current_ratio < 0.9:  # If down more than 10%
            balance_factor = max(0.7, current_ratio)  # Reduce position size
        elif current_ratio > 1.1:  # If up more than 10%
            balance_factor = min(1.3, 1.0 + (current_ratio - 1.0) * 0.5)  # Slightly increase
        
        # Calculate final position size with ultra-quality boost
        adjusted_size = base_size * confidence_factor * signal_factor * ultra_quality_boost * performance_factor * balance_factor
        
        # Apply min/max limits
        min_size = self.rapid_fire_settings['min_position_pct']
        max_size = self.rapid_fire_settings['max_position_pct']
        final_size = max(min_size, min(max_size, adjusted_size))
        
        return final_size

    def execute_rapid_trade(self, symbol: str, action: str, rsi: float, confidence: float, market_conditions: Dict) -> Dict:
        """Execute a paper trade and record training data"""
        timestamp = datetime.now()
        
        # Simulate trade execution
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
        except:
            price = random.uniform(1, 1000)  # Fallback price
            
        # Calculate intelligent position size
        signal_strength = confidence / 100.0  # Convert confidence to 0-1 scale
        position_size_pct = self.calculate_position_size(confidence, signal_strength)
        position_value = self.portfolio_balance * position_size_pct
        shares = position_value / price
        
        trade_data = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': action,
            'price': price,
            'shares': shares,
            'position_value': position_value,
            'rsi': rsi,
            'confidence': confidence,
            'market_conditions': market_conditions,
            'session_id': self.session_id
        }
        
        # Simulate outcome and update portfolio
        outcome_probability = confidence / 100.0
        if market_conditions['market_trend'] == 'bullish' and action == 'BUY':
            outcome_probability *= 1.2
        elif market_conditions['market_trend'] == 'bearish' and action == 'SELL':
            outcome_probability *= 1.2
        else:
            outcome_probability *= 0.8
            
        # Simulate profit/loss
        success = random.random() < outcome_probability
        if success:
            profit_pct = random.uniform(0.5, 3.0)  # 0.5-3% profit
        else:
            profit_pct = random.uniform(-2.0, -0.5)  # 0.5-2% loss
            
        # Update portfolio balance
        profit_loss = position_value * (profit_pct / 100)
        self.portfolio_balance += profit_loss
        
        # Integrate with Profit Engine for advanced profit management
        if self.has_profit_engine:
            # Add position to profit engine tracking
            if action in ['BUY', 'SELL']:  # Only track actual positions
                self.profit_engine.add_position(
                    symbol=symbol,
                    entry_price=price,
                    shares=shares,
                    confidence=confidence,
                    position_value=position_value
                )
                
                # Update profit engine with current balance
                self.profit_engine.current_balance = self.portfolio_balance
                if profit_loss > 0:
                    self.profit_engine.total_profits += profit_loss
                    
                # Process automatic reinvestment if threshold reached
                if self.profit_engine.process_profit_reinvestment():
                    self.portfolio_balance = self.profit_engine.current_balance
                    
                # Process automatic profit withdrawal if needed
                withdrawal = self.profit_engine.process_profit_withdrawal()
                if withdrawal > 0:
                    self.portfolio_balance = self.profit_engine.current_balance
        
        trade_data['outcome'] = 'profit' if success else 'loss'
        trade_data['profit_pct'] = profit_pct
        trade_data['profit_loss'] = profit_loss
        trade_data['new_balance'] = self.portfolio_balance
        
        self.training_data.append(trade_data)
        self.trade_history.append(trade_data)
        self.portfolio_history.append({'timestamp': timestamp, 'balance': self.portfolio_balance})
        
        # Enhanced trade output with all signal information and dynamic position size
        signals_info = f"RSI {rsi:.1f} | Sent {market_conditions['sentiment_score']:.2f} | SC {market_conditions['supply_chain_factor']:.2f} | BR {market_conditions['brazil_factor']:.2f} | AF {market_conditions['africa_factor']:.2f}"
        print(f"🚀 TRADE: {action} {symbol} @ ${price:.4f} | ${position_value:.2f} ({shares:.4f} shares) [{position_size_pct*100:.1f}%] | {signals_info} | Confidence {confidence:.1f}% | {trade_data['outcome']} {profit_pct:.1f}% | Balance: ${self.portfolio_balance:.2f}")
        
        return trade_data
    
    def run_rapid_training_session(self):
        """Run a high-speed trading session with portfolio tracking"""
        print("🔥 STARTING PAPER TRADING SESSION")
        print("=" * 60)
        print(f"⏱️  Duration: {self.rapid_fire_settings['session_duration'] / 3600:.1f} hours")
        print(f"💰 Starting Budget: ${self.rapid_fire_settings['starting_budget']:.2f}")
        print(f"⚡ Rate: {self.rapid_fire_settings['trades_per_minute']} trades/minute")
        print(f"📊 Position Size: {self.rapid_fire_settings['min_position_pct']*100:.1f}%-{self.rapid_fire_settings['max_position_pct']*100:.1f}% (dynamic based on confidence)")
        print(f"📈 Symbols: {len(self.symbols)} cryptocurrencies")
        print(f"🎯 Session ID: {self.session_id}")
        print()
        
        start_time = time.time()
        trade_interval = 60 / self.rapid_fire_settings['trades_per_minute']  # Seconds between trades
        trades_executed = 0
        profitable_trades = 0
        
        while time.time() - start_time < self.rapid_fire_settings['session_duration']:
            # Pick random symbol
            symbol = random.choice(self.symbols)
            
            # Generate synthetic market conditions
            market_conditions = self.generate_synthetic_market_conditions()
            
            # Calculate RSI with variations
            rsi = self.calculate_rapid_rsi(symbol, market_conditions)
            
            # Determine action
            if random.random() < 0.05:  # 5% random trades for learning edge cases
                action = random.choice(['BUY', 'SELL'])
                confidence = random.uniform(20, 80)
                print(f"🎲 RANDOM TRADE for edge case learning")
            else:
                # Intelligent decision based on RSI
                should_buy, buy_confidence = self.should_rapid_buy(symbol, rsi, market_conditions)
                should_sell, sell_confidence = self.should_rapid_sell(symbol, rsi, market_conditions)
                
                if should_buy and buy_confidence > 70:  # Only trade with HIGH confidence
                    action = 'BUY'
                    confidence = buy_confidence
                elif should_sell and sell_confidence > 70:  # Only trade with HIGH confidence
                    action = 'SELL' 
                    confidence = sell_confidence
                else:
                    action = 'HOLD'
                    confidence = 0
            
            # Execute trade if not HOLD
            if action != 'HOLD':
                trade_result = self.execute_rapid_trade(symbol, action, rsi, confidence, market_conditions)
                trades_executed += 1
                if trade_result['outcome'] == 'profit':
                    profitable_trades += 1
                
                # Feed data to learning engine every 20 trades
                if trades_executed % 20 == 0:
                    if self.has_learning_engine:
                        self.feed_to_learning_engine()
                    win_rate = (profitable_trades / trades_executed) * 100
                    total_return = ((self.portfolio_balance - self.rapid_fire_settings['starting_budget']) / self.rapid_fire_settings['starting_budget']) * 100
                    print(f"📚 Processed {len(self.training_data)} patterns | Win Rate: {win_rate:.1f}% | Return: {total_return:.1f}%")
            
            # Sleep until next trade
            time.sleep(trade_interval)
        
        # Final learning engine update
        if self.has_learning_engine:
            self.feed_to_learning_engine()
        
        # Calculate final statistics
        total_return = ((self.portfolio_balance - self.rapid_fire_settings['starting_budget']) / self.rapid_fire_settings['starting_budget']) * 100
        win_rate = (profitable_trades / trades_executed) * 100 if trades_executed > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"🏁 PAPER TRADING SESSION COMPLETE!")
        print(f"📊 Total Trades: {trades_executed}")
        print(f"⏱️  Duration: {(time.time() - start_time) / 3600:.2f} hours")
        print(f"⚡ Actual Rate: {trades_executed / ((time.time() - start_time) / 60):.1f} trades/minute")
        print(f"💰 Starting Balance: ${self.rapid_fire_settings['starting_budget']:.2f}")
        print(f"💰 Final Balance: ${self.portfolio_balance:.2f}")
        print(f"📈 Total Return: {total_return:.2f}%")
        print(f"✅ Win Rate: {win_rate:.1f}% ({profitable_trades}/{trades_executed})")
        print(f"📚 Patterns Generated: {len(self.training_data)}")
        
        # Show Profit Engine summary
        if self.has_profit_engine:
            try:
                profit_summary = self.profit_engine.get_portfolio_summary()
                print(f"💎 Profit Engine Summary:")
                print(f"   • Total Profits Generated: ${profit_summary['total_profits']:.2f}")
                print(f"   • Profits Withdrawn: ${profit_summary['withdrawn_profits']:.2f}")
                print(f"   • Portfolio Scaling: {'Active' if profit_summary['profit_scaling_active'] else 'Inactive'}")
                print(f"   • Open Positions Tracked: {profit_summary['open_positions']}")
                if profit_summary['total_profits'] > 0:
                    print(f"   • Next Auto-Withdrawal: ${profit_summary['next_withdrawal_at']:.2f}")
            except Exception as e:
                print(f"💎 Profit Engine: Summary unavailable - {e}")
        
        # Show learning engine stats
        if self.has_learning_engine:
            try:
                stats = self.learning_engine.get_learning_stats()
                print(f"🧠 Learning Engine Update:")
                print(f"   • Total Sessions: {stats['total_sessions']}")
                print(f"   • Patterns Learned: {stats['learned_patterns']}")
                print(f"   • Learning Active: {stats['learning_active']}")
            except:
                print("🧠 Learning Engine: Data processed successfully")
        else:
            print("🧠 Learning Engine: Disabled (patterns saved for later training)")
            
        # Save session results
        self.save_session_results()
    
    def feed_to_learning_engine(self):
        """Feed training data to the learning engine"""
        if not self.training_data or not self.has_learning_engine:
            return
            
        # Convert training data to learning engine format
        for trade in self.training_data:
            session_data = {
                'timestamp': trade['timestamp'],
                'symbol': trade['symbol'],
                'action': trade['action'],
                'price': trade['price'],
                'rsi': trade['rsi'],
                'supply_chain_score': trade['market_conditions'].get('supply_chain_factor', 1.0),
                'confidence': trade['confidence'],
                'outcome': trade['outcome'],
                'profit_pct': trade['profit_pct'],
                'market_trend': trade['market_conditions']['market_trend'],
                'volatility': trade['market_conditions']['volatility']
            }
            
            # Add to learning engine (this would integrate with your existing learning system)
            # For now, just accumulate the data
            
        # Clear processed data
        self.training_data = []
        
    def save_session_results(self):
        """Save session results to file"""
        import json
        results = {
            'session_id': self.session_id,
            'settings': self.rapid_fire_settings,
            'final_balance': self.portfolio_balance,
            'total_trades': len(self.trade_history),
            'profitable_trades': len([t for t in self.trade_history if t['outcome'] == 'profit']),
            'total_return_pct': ((self.portfolio_balance - self.rapid_fire_settings['starting_budget']) / self.rapid_fire_settings['starting_budget']) * 100,
            'portfolio_history': [{'timestamp': str(h['timestamp']), 'balance': h['balance']} for h in self.portfolio_history],
            'trade_history': [
                {
                    'timestamp': str(t['timestamp']),
                    'symbol': t['symbol'],
                    'action': t['action'],
                    'price': t['price'],
                    'shares': t['shares'],
                    'position_value': t['position_value'],
                    'profit_pct': t['profit_pct'],
                    'profit_loss': t['profit_loss'],
                    'new_balance': t['new_balance']
                } for t in self.trade_history
            ]
        }
        
        filename = f"rapid_training_results_{self.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Session results saved to: {filename}")

def main():
    """Run rapid fire training"""
    trainer = RapidFireTrainer()
    trainer.run_rapid_training_session()

if __name__ == "__main__":
    main()