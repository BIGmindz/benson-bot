#!/usr/bin/env python3
"""
Enhanced Benson Bot Learning Engine with Advanced Pattern Recognition
Analyzes trading performance and adapts strategy based on successful and unsuccessful patterns
"""

import json
import sqlite3
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import os

# Import advanced pattern engine
try:
    from advanced_pattern_engine import AdvancedPatternEngine, MarketContext
    ADVANCED_PATTERNS_AVAILABLE = True
except ImportError:
    ADVANCED_PATTERNS_AVAILABLE = False
    print("⚠️ Advanced pattern engine not available - using basic patterns")

@dataclass
class TradingSession:
    """Represents a complete trading session with performance metrics"""
    session_id: str
    start_time: float
    end_time: float
    starting_balance: float
    ending_balance: float
    total_return: float
    total_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    market_conditions: Dict
    signal_weights: Dict
    rsi_params: Dict

@dataclass
class MarketPattern:
    """Represents a successful market pattern/condition"""
    pattern_id: str
    success_rate: float
    avg_return: float
    market_volatility: float
    rsi_threshold: float
    supply_chain_range: Tuple[float, float]
    best_symbols: List[str]
    optimal_weights: Dict
    confidence_score: float

class BensonLearningEngine:
    """Enhanced learning system with advanced pattern recognition"""
    
    def __init__(self, db_path: str = "benson_memory.db"):
        self.db_path = db_path
        self.init_database()
        self.learning_threshold = 0.05  # 5% minimum return to consider "good"
        self.adaptation_rate = 0.1  # How fast to adapt (10%)
        
        # Initialize advanced pattern engine if available
        if ADVANCED_PATTERNS_AVAILABLE:
            self.advanced_patterns = AdvancedPatternEngine()
            print("🧠 Advanced Pattern Recognition Engine: ENABLED")
        else:
            self.advanced_patterns = None
            print("🧠 Advanced Pattern Recognition Engine: DISABLED (using basic patterns)")
        
    def init_database(self):
        """Initialize SQLite database for persistent memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trading sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_sessions (
                session_id TEXT PRIMARY KEY,
                timestamp TEXT,
                performance_data TEXT,
                market_conditions TEXT,
                config_used TEXT
            )
        ''')
        
        # Learned patterns table  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_data TEXT,
                success_count INTEGER DEFAULT 0,
                last_updated TEXT,
                confidence_score REAL
            )
        ''')
        
        # Adaptive parameters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adaptive_params (
                param_name TEXT PRIMARY KEY,
                current_value REAL,
                historical_values TEXT,
                last_updated TEXT,
                performance_correlation REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def get_advanced_trade_recommendation(self, symbol: str, price: float, rsi: float, 
                                       supply_chain: float, volume_24h: float, 
                                       price_change_24h: float) -> Tuple[str, float, str]:
        """Get trade recommendation using advanced pattern recognition"""
        
        if not ADVANCED_PATTERNS_AVAILABLE or not self.advanced_patterns:
            return "HOLD", 0.5, "Advanced patterns not available"
        
        # Create current market context
        current_context = MarketContext(
            timestamp=datetime.now(),
            symbol=symbol,
            price=price,
            price_change_1h=price_change_24h / 24,  # Rough estimate
            price_change_24h=price_change_24h,
            volume_24h=volume_24h,
            volatility=abs(price_change_24h) / 100,  # Simple volatility proxy
            rsi=rsi,
            rsi_trend='stable',  # Simplified
            supply_chain=supply_chain,
            market_cap_rank=1,  # Placeholder
            correlation_btc=0.8  # Placeholder
        )
        
        # Find matching patterns
        pattern_matches = self.advanced_patterns.match_current_conditions(current_context)
        
        if not pattern_matches:
            return "HOLD", 0.5, "No matching patterns found"
        
        # Analyze top matches
        total_weight = 0.0
        weighted_success = 0.0
        weighted_return = 0.0
        recommendations = []
        
        for pattern, similarity in pattern_matches[:3]:  # Top 3 matches
            weight = similarity * pattern.occurrence_count
            total_weight += weight
            
            weighted_success += pattern.success_probability * weight
            weighted_return += pattern.avg_return * weight
            
            if pattern.success_probability > 0.6 and pattern.avg_return > 2.0:
                recommendations.append("BUY")
            elif pattern.success_probability < 0.4 or pattern.avg_return < -2.0:
                recommendations.append("SELL")
            else:
                recommendations.append("HOLD")
        
        if total_weight > 0:
            final_success_prob = weighted_success / total_weight
            final_return_expectation = weighted_return / total_weight
        else:
            final_success_prob = 0.5
            final_return_expectation = 0.0
        
        # Determine final recommendation
        buy_votes = recommendations.count("BUY")
        sell_votes = recommendations.count("SELL")
        
        if buy_votes > sell_votes and final_success_prob > 0.6:
            recommendation = "BUY"
        elif sell_votes > buy_votes or final_success_prob < 0.3:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
        
        confidence = final_success_prob
        reason = f"Pattern analysis: {len(pattern_matches)} matches, avg return: {final_return_expectation:.1f}%"
        
        return recommendation, confidence, reason
    
    def should_avoid_trade(self, symbol: str, rsi: float, supply_chain: float, 
                          current_volatility: float, signal_weights: dict) -> tuple[bool, str]:
        """Check if current conditions match unsuccessful patterns - avoid trade if so"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT pattern_data, confidence_score FROM learned_patterns')
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            pattern_data = json.loads(row[0])
            confidence = row[1]
            pattern = MarketPattern(**pattern_data)
            
            # Skip successful patterns - we want to check failure patterns
            if pattern.success_rate > 0.5:
                continue
                
            # Check if current conditions match this unsuccessful pattern
            avoid_score = 0.0
            reasons = []
            
            # RSI threshold similarity (higher weight for failures)
            if abs(rsi - pattern.rsi_threshold) < 5:  # Within 5 RSI points
                avoid_score += 0.4 * confidence
                reasons.append(f"RSI {rsi:.1f} similar to failed pattern ({pattern.rsi_threshold})")
            
            # High volatility check
            if current_volatility > 0.7 and pattern.market_volatility > 0.7:
                avoid_score += 0.3 * confidence  
                reasons.append(f"High volatility {current_volatility:.2f} matches failure pattern")
            
            # Signal weights similarity
            if signal_weights:
                weight_diff = sum(abs(signal_weights.get(k, 0.5) - pattern.optimal_weights.get(k, 0.5)) 
                                for k in pattern.optimal_weights.keys())
                if weight_diff < 0.5:  # Similar weight configuration
                    avoid_score += 0.3 * confidence
                    reasons.append("Signal weights match unsuccessful configuration")
            
            # If avoid score is high enough, recommend avoiding
            if avoid_score > 0.3:  # 30% confidence to avoid (more sensitive)
                reason_str = f"🚫 AVOID: {', '.join(reasons[:2])}"
                return True, reason_str
        
        return False, ""
    
    def calculate_trade_confidence(self, symbol: str, rsi: float, supply_chain: float, 
                                 current_volatility: float, signal_weights: dict) -> float:
        """Calculate confidence score considering both successful and unsuccessful patterns"""
        base_confidence = 0.5  # Neutral starting point
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT pattern_data, confidence_score FROM learned_patterns')
        rows = cursor.fetchall()
        conn.close()
        
        positive_boost = 0.0
        negative_penalty = 0.0
        
        for row in rows:
            pattern_data = json.loads(row[0])
            confidence = row[1]
            pattern = MarketPattern(**pattern_data)
            
            # Calculate similarity to this pattern
            similarity_score = 0.0
            
            # RSI similarity
            rsi_similarity = max(0, 1 - abs(rsi - pattern.rsi_threshold) / 20)  # Scale to 0-1
            similarity_score += rsi_similarity * 0.4
            
            # Volatility similarity  
            vol_similarity = max(0, 1 - abs(current_volatility - pattern.market_volatility) / 1.0)
            similarity_score += vol_similarity * 0.3
            
            # Signal weight similarity
            if signal_weights and pattern.optimal_weights:
                weight_similarity = 1 - sum(abs(signal_weights.get(k, 0.5) - pattern.optimal_weights.get(k, 0.5)) 
                                          for k in pattern.optimal_weights.keys()) / len(pattern.optimal_weights)
                similarity_score += max(0, weight_similarity) * 0.3
            
            # Apply positive or negative reinforcement based on pattern success
            if pattern.success_rate > 0.5:  # Successful pattern
                positive_boost += similarity_score * confidence * pattern.success_rate
            else:  # Unsuccessful pattern - apply penalty
                negative_penalty += similarity_score * confidence * (1 - pattern.success_rate)
        
        # Calculate final confidence with reinforcement
        final_confidence = base_confidence + (positive_boost * 0.4) - (negative_penalty * 0.6)
        
        # Keep in valid range
        return max(0.1, min(0.9, final_confidence))
    
    def analyze_session(self, portfolio, trades_log: str, session_duration: int) -> TradingSession:
        """Analyze a completed trading session and extract insights"""
        
        # Calculate session performance metrics
        summary = portfolio.get_portfolio_summary()
        
        # Analyze trades from CSV log
        trade_data = self._load_trades_from_csv(trades_log)
        
        # Calculate advanced metrics
        returns = self._calculate_returns(trade_data)
        win_rate = self._calculate_win_rate(portfolio.trade_history)
        sharpe = self._calculate_sharpe_ratio(returns)
        max_dd = self._calculate_max_drawdown(returns)
        
        # Detect market conditions during session
        market_conditions = self._analyze_market_conditions(trade_data)
        
        session = TradingSession(
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=time.time() - session_duration,
            end_time=time.time(),
            starting_balance=portfolio.starting_balance,
            ending_balance=summary['portfolio_value'],
            total_return=summary['return_pct'],
            total_trades=summary['total_trades'],
            win_rate=win_rate,
            avg_win=self._calculate_avg_win(portfolio.trade_history),
            avg_loss=self._calculate_avg_loss(portfolio.trade_history),
            max_drawdown=max_dd,
            sharpe_ratio=sharpe,
            volatility=np.std(returns) if returns else 0.0,
            market_conditions=market_conditions,
            signal_weights={"rsi": 0.25, "supply_chain": 0.175},  # Current weights
            rsi_params={"buy_threshold": 30, "sell_threshold": 70}
        )
        
        return session
    
    def learn_from_session(self, session: TradingSession, config: Dict) -> Dict:
        """Learn from session using both basic and advanced pattern recognition"""
        
        # Save session to database
        self._save_session(session)
        
        # Basic pattern extraction (existing functionality)
        successful_patterns = []
        unsuccessful_patterns = []
        
        if session.total_return > self.learning_threshold:
            successful_patterns = self._extract_successful_patterns(session)
            print(f"🎯 Extracted {len(successful_patterns)} successful patterns")
        
        if session.total_return < -self.learning_threshold or session.win_rate < 0.4:
            unsuccessful_patterns = self._extract_unsuccessful_patterns(session)
            print(f"🚫 Extracted {len(unsuccessful_patterns)} failure patterns to avoid")
        
        # Save all basic patterns
        for pattern in successful_patterns + unsuccessful_patterns:
            self._save_pattern(pattern)
        
        # Advanced pattern analysis if available
        if ADVANCED_PATTERNS_AVAILABLE and self.advanced_patterns:
            print(f"🔬 Running advanced pattern analysis...")
            
            # TODO: Implement integration with trading session data
            # This would require more detailed market data collection during trading
            insights = self.advanced_patterns.get_pattern_insights()
            print(f"📊 Pattern insights: {insights.get('total_patterns', 0)} advanced patterns learned")
            
        # Update adaptive parameters based on session results
        if successful_patterns:
            updated_config = self._adapt_parameters(session, config)
            
            print(f"🧠 LEARNING: Session return {session.total_return:.2f}% - Extracting patterns...")
            print(f"📊 Found {len(successful_patterns)} successful patterns")
            
            return updated_config
        
        # Even if no successful patterns, still return config (may have learned failure patterns)
        print(f"📝 No successful patterns, but learned {len(unsuccessful_patterns)} patterns to avoid")
        return config
    
    def get_optimized_config(self, base_config: Dict) -> Dict:
        """Get optimized configuration based on learned patterns"""
        
        # Load best performing patterns
        patterns = self._get_best_patterns(limit=5)
        
        if not patterns:
            return base_config
        
        optimized_config = base_config.copy()
        
        # Optimize RSI thresholds based on successful patterns
        avg_rsi_buy = np.mean([p.rsi_threshold for p in patterns])
        avg_rsi_sell = 100 - avg_rsi_buy  # Mirror logic
        
        # Gradually adapt thresholds
        current_buy = base_config.get('rsi', {}).get('buy_threshold', 30)
        current_sell = base_config.get('rsi', {}).get('sell_threshold', 70)
        
        new_buy = current_buy + (avg_rsi_buy - current_buy) * self.adaptation_rate
        new_sell = current_sell + (avg_rsi_sell - current_sell) * self.adaptation_rate
        
        optimized_config['rsi']['buy_threshold'] = round(new_buy, 1)
        optimized_config['rsi']['sell_threshold'] = round(new_sell, 1)
        
        # Optimize signal weights
        if patterns:
            avg_weights = {}
            for pattern in patterns:
                for weight_name, value in pattern.optimal_weights.items():
                    if weight_name not in avg_weights:
                        avg_weights[weight_name] = []
                    avg_weights[weight_name].append(value)
            
            # Store optimized weights for the bot to use
            optimized_weights = {k: np.mean(v) for k, v in avg_weights.items()}
            optimized_config['optimized_weights'] = optimized_weights
        
        print(f"🎯 OPTIMIZATION: Adapted RSI thresholds to {new_buy:.1f}/{new_sell:.1f}")
        print(f"⚖️ WEIGHTS: {optimized_config.get('optimized_weights', 'Using defaults')}")
        
        return optimized_config
    
    def _extract_successful_patterns(self, session: TradingSession) -> List[MarketPattern]:
        """Extract patterns from successful trading sessions"""
        patterns = []
        
        # Pattern 1: RSI threshold performance
        if session.win_rate > 0.6:  # 60%+ win rate
            pattern = MarketPattern(
                pattern_id=f"rsi_success_{session.session_id}",
                success_rate=session.win_rate,
                avg_return=session.total_return,
                market_volatility=session.volatility,
                rsi_threshold=session.rsi_params['buy_threshold'],
                supply_chain_range=(0.3, 0.7),  # Placeholder
                best_symbols=["BTC/USDT", "ETH/USDT"],  # Most traded
                optimal_weights=session.signal_weights,
                confidence_score=min(1.0, session.win_rate * (session.total_return / 10))
            )
            patterns.append(pattern)
        
        return patterns
    
    def _extract_unsuccessful_patterns(self, session: TradingSession) -> List[MarketPattern]:
        """Extract patterns from unsuccessful trading sessions to avoid"""
        patterns = []
        
        # Pattern 1: Poor RSI threshold performance (low win rate)
        if session.win_rate < 0.4:  # Less than 40% win rate
            pattern = MarketPattern(
                pattern_id=f"rsi_failure_{session.session_id}",
                success_rate=session.win_rate,
                avg_return=session.total_return,
                market_volatility=session.volatility,
                rsi_threshold=session.rsi_params['buy_threshold'],
                supply_chain_range=(0.3, 0.7),  # Will refine based on actual data
                best_symbols=[],  # Empty for failure patterns
                optimal_weights=session.signal_weights,
                confidence_score=min(1.0, (1 - session.win_rate) * abs(session.total_return / 10))
            )
            patterns.append(pattern)
        
        # Pattern 2: Negative returns despite decent win rate
        if session.total_return < -2.0 and session.win_rate > 0.4:
            pattern = MarketPattern(
                pattern_id=f"bad_returns_{session.session_id}",
                success_rate=session.win_rate,
                avg_return=session.total_return,
                market_volatility=session.volatility,
                rsi_threshold=session.rsi_params['buy_threshold'],
                supply_chain_range=(0.3, 0.7),
                best_symbols=[],
                optimal_weights=session.signal_weights,
                confidence_score=min(1.0, abs(session.total_return) / 10)
            )
            patterns.append(pattern)
        
        # Pattern 3: High volatility losses
        if session.volatility > 0.8 and session.total_return < -1.0:
            pattern = MarketPattern(
                pattern_id=f"high_vol_loss_{session.session_id}",
                success_rate=session.win_rate,
                avg_return=session.total_return,
                market_volatility=session.volatility,
                rsi_threshold=session.rsi_params['buy_threshold'],
                supply_chain_range=(0.3, 0.7),
                best_symbols=[],
                optimal_weights=session.signal_weights,
                confidence_score=min(1.0, session.volatility * abs(session.total_return) / 10)
            )
            patterns.append(pattern)
        
        return patterns
    
    def _save_session(self, session: TradingSession):
        """Save session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trading_sessions 
            (session_id, timestamp, performance_data, market_conditions, config_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session.session_id,
            datetime.now().isoformat(),
            json.dumps(asdict(session)),
            json.dumps(session.market_conditions),
            json.dumps(session.signal_weights)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_pattern(self, pattern: MarketPattern):
        """Save learned pattern to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO learned_patterns
            (pattern_id, pattern_data, success_count, last_updated, confidence_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            pattern.pattern_id,
            json.dumps(asdict(pattern)),
            1,
            datetime.now().isoformat(),
            pattern.confidence_score
        ))
        
        conn.commit()
        conn.close()
    
    def _get_best_patterns(self, limit: int = 5) -> List[MarketPattern]:
        """Get best performing patterns from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_data FROM learned_patterns 
            ORDER BY confidence_score DESC 
            LIMIT ?
        ''', (limit,))
        
        patterns = []
        for row in cursor.fetchall():
            pattern_data = json.loads(row[0])
            pattern = MarketPattern(**pattern_data)
            patterns.append(pattern)
        
        conn.close()
        return patterns
    
    def _calculate_returns(self, trade_data: List) -> List[float]:
        """Calculate returns from trade data"""
        if not trade_data:
            return []
        
        returns = []
        for trade in trade_data:
            if hasattr(trade, 'pnl') and trade.pnl != 0:
                returns.append(trade.pnl)
        
        return returns
    
    def _calculate_win_rate(self, trades: List) -> float:
        """Calculate win rate from trades"""
        if not trades:
            return 0.0
        
        wins = sum(1 for trade in trades if hasattr(trade, 'pnl') and trade.pnl > 0)
        return wins / len(trades) if trades else 0.0
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return 0.0
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        return avg_return / std_return if std_return > 0 else 0.0
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0
        
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        
        return abs(np.min(drawdown)) if len(drawdown) > 0 else 0.0
    
    def _calculate_avg_win(self, trades: List) -> float:
        """Calculate average winning trade"""
        wins = [trade.pnl for trade in trades if hasattr(trade, 'pnl') and trade.pnl > 0]
        return np.mean(wins) if wins else 0.0
    
    def _calculate_avg_loss(self, trades: List) -> float:
        """Calculate average losing trade"""
        losses = [abs(trade.pnl) for trade in trades if hasattr(trade, 'pnl') and trade.pnl < 0]
        return np.mean(losses) if losses else 0.0
    
    def _analyze_market_conditions(self, trade_data: List) -> Dict:
        """Analyze market conditions during the session"""
        return {
            "volatility": "medium",
            "trend": "sideways",
            "volume": "normal"
        }
    
    def _load_trades_from_csv(self, csv_path: str) -> List:
        """Load trade data from CSV log"""
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                return df.to_dict('records')
        except:
            pass
        return []
    
    def _adapt_parameters(self, session: TradingSession, config: Dict) -> Dict:
        """Adapt strategy parameters based on successful session"""
        
        adapted_config = config.copy()
        
        # If the session was very successful (>10% return), be more aggressive with adaptation
        if session.total_return > 10.0:
            adaptation_factor = 0.2  # 20% adaptation
        elif session.total_return > 5.0:
            adaptation_factor = 0.15  # 15% adaptation  
        else:
            adaptation_factor = self.adaptation_rate  # 10% adaptation
        
        # Save adaptation to database for tracking
        self._save_adaptive_param("rsi_buy_threshold", 
                                  session.rsi_params['buy_threshold'],
                                  session.total_return)
        
        return adapted_config
    
    def _save_adaptive_param(self, param_name: str, value: float, performance: float):
        """Save adaptive parameter change"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO adaptive_params
            (param_name, current_value, last_updated, performance_correlation)
            VALUES (?, ?, ?, ?)
        ''', (param_name, value, datetime.now().isoformat(), performance))
        
        conn.commit()
        conn.close()
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about the learning system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count sessions
        cursor.execute("SELECT COUNT(*) FROM trading_sessions")
        total_sessions = cursor.fetchone()[0]
        
        # Count patterns
        cursor.execute("SELECT COUNT(*) FROM learned_patterns")
        total_patterns = cursor.fetchone()[0]
        
        # Get best session
        cursor.execute("""
            SELECT performance_data FROM trading_sessions 
            ORDER BY json_extract(performance_data, '$.total_return') DESC 
            LIMIT 1
        """)
        
        best_session_data = cursor.fetchone()
        best_return = 0.0
        if best_session_data:
            session_data = json.loads(best_session_data[0])
            best_return = session_data.get('total_return', 0.0)
        
        conn.close()
        
        return {
            "total_sessions": total_sessions,
            "learned_patterns": total_patterns,
            "best_session_return": best_return,
            "learning_active": total_patterns > 0
        }

# Integration functions for the main bot
def create_learning_engine():
    """Create and return learning engine instance"""
    return BensonLearningEngine()

def apply_learned_optimizations(config: Dict, learning_engine: BensonLearningEngine) -> Dict:
    """Apply learned optimizations to bot configuration"""
    return learning_engine.get_optimized_config(config)