#!/usr/bin/env python3
"""
Paper Trading Portfolio Manager for Benson Bot
Manages virtual portfolio with budget constraints and position tracking
Automatically contributes trading data to the Data Contribution Network
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import json
from datetime import datetime, timezone

# Import Data Contribution Network components
try:
    from data_contribution_engine import DataContributionEngine
    from privacy_consent_manager import PrivacyManager
    from data_quality_validator import DataQualityValidator
    CONTRIBUTION_ENABLED = True
except ImportError:
    print("⚠️  Data Contribution Network not available - running in standalone mode")
    CONTRIBUTION_ENABLED = False

@dataclass
class Position:
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    entry_price: float
    entry_time: float
    current_price: float
    unrealized_pnl: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass 
class Trade:
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: float
    pnl: float = 0.0
    reason: str = ""

class PaperTradingPortfolio:
    def __init__(self, config: dict):
        paper_config = config.get('paper_trading', {})
        self.starting_balance = paper_config.get('starting_balance', 10000.0)
        self.balance = self.starting_balance
        self.max_position_size = paper_config.get('max_position_size', 500.0)
        self.position_size_pct = paper_config.get('position_size_pct', 5.0) / 100.0
        self.max_positions = paper_config.get('max_positions', 10)
        self.stop_loss_pct = paper_config.get('stop_loss_pct', 5.0) / 100.0
        self.take_profit_pct = paper_config.get('take_profit_pct', 10.0) / 100.0
        
        # Portfolio tracking
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Trade] = []
        self.total_pnl = 0.0
        
        # Data Contribution Network integration
        self.paper_user_id = "paper_trader_bot"
        self.contribution_enabled = CONTRIBUTION_ENABLED
        self.contribution_batch = []  # Batch trades for contribution
        self.contribution_interval = paper_config.get('contribution_interval', 10)  # Contribute every N trades
        
        if self.contribution_enabled:
            try:
                # Initialize contribution system components
                self.contribution_engine = DataContributionEngine()
                self.privacy_manager = PrivacyManager() 
                self.quality_validator = DataQualityValidator()
                
                # Auto-setup paper trader consent (privacy-compliant for bot data)
                self._setup_paper_trader_consent()
                
                print("✅ Paper Trading → Data Contribution Network: ENABLED")
            except Exception as e:
                print(f"⚠️  Data Contribution setup failed: {e}")
                self.contribution_enabled = False
        
        print(f"💰 Paper Trading Portfolio Initialized:")
        print(f"   Starting Balance: ${self.starting_balance:,.2f}")
        print(f"   Max Position Size: ${self.max_position_size:,.2f} ({self.position_size_pct*100:.1f}% of balance)")
        print(f"   Max Positions: {self.max_positions}")
        print(f"   Stop Loss: {self.stop_loss_pct*100:.1f}% | Take Profit: {self.take_profit_pct*100:.1f}%")
    
    def _setup_paper_trader_consent(self):
        """Setup automated consent for paper trader bot contributions"""
        try:
            # Create consent for paper trader (enhanced anonymization for training data)
            consent_data = {
                'consent_level': 'enhanced',  # Enhanced for better training data
                'data_types': ['trading_data', 'performance_metrics', 'pattern_recognition'],
                'privacy_level': 'anonymized',  # Anonymized paper trading data
                'purpose': 'training_and_validation'
            }
            
            consent_result = self.privacy_manager.collect_user_consent(
                user_id=self.paper_user_id,
                consent_data=consent_data
            )
            
            if consent_result:
                print(f"🔒 Auto-consent configured for {self.paper_user_id}")
                print(f"   Level: Enhanced | Privacy: Anonymized | Types: Trading + Performance + Patterns")
            else:
                print(f"⚠️  Failed to setup auto-consent for {self.paper_user_id}")
                
        except Exception as e:
            print(f"❌ Consent setup error: {e}")
            self.contribution_enabled = False
    
    def _contribute_trade_data(self, trade: Trade, position_data: dict = None):
        """Contribute individual trade data to the network"""
        if not self.contribution_enabled:
            return
            
        try:
            # Format trade data for contribution
            trade_data = {
                'trade_id': f"paper_{int(trade.timestamp)}_{trade.symbol}",
                'symbol': trade.symbol,
                'side': trade.side,
                'quantity': trade.quantity,
                'price': trade.price,
                'timestamp': trade.timestamp,
                'pnl': trade.pnl,
                'reason': trade.reason,
                'source': 'paper_trading',
                'performance_metrics': {
                    'portfolio_value': self.get_portfolio_value(),
                    'total_pnl': self.total_pnl,
                    'active_positions': len(self.positions),
                    'trade_sequence': len(self.trade_history)
                }
            }
            
            # Add position context if provided
            if position_data:
                trade_data['position_context'] = position_data
                
            # Add to batch for contribution
            self.contribution_batch.append(trade_data)
            
            # Contribute batch when interval is reached
            if len(self.contribution_batch) >= self.contribution_interval:
                self._submit_contribution_batch()
                
        except Exception as e:
            print(f"⚠️  Trade contribution error: {e}")
    
    def _submit_contribution_batch(self):
        """Submit batched trade data to contribution network"""
        if not self.contribution_enabled or not self.contribution_batch:
            return
            
        try:
            # Format batch for contribution
            batch_data = {
                'user_id': self.paper_user_id,
                'data_type': 'paper_trading_batch',
                'timestamp': datetime.now().isoformat(),
                'trades': self.contribution_batch,
                'batch_summary': {
                    'total_trades': len(self.contribution_batch),
                    'symbols': list(set(trade['symbol'] for trade in self.contribution_batch)),
                    'net_pnl': sum(trade.get('pnl', 0) for trade in self.contribution_batch),
                    'performance_trend': self._calculate_performance_trend()
                }
            }
            
            # Submit to contribution engine
            contribution_id = self.contribution_engine.submit_data_contribution(
                user_id=self.paper_user_id,
                trading_data=batch_data
            )
            
            if contribution_id:
                # Validate contributed data quality
                validation_result = self.quality_validator.validate_data_contribution(
                    trading_data=batch_data,
                    user_id=self.paper_user_id,
                    contribution_id=contribution_id
                )
                
                print(f"📊 CONTRIBUTED BATCH: {len(self.contribution_batch)} trades")
                print(f"   Quality Score: {validation_result.quality_score:.1f}/100")
                print(f"   Contribution ID: {contribution_id[:8]}...")
                
                # Clear batch
                self.contribution_batch = []
                
        except Exception as e:
            print(f"❌ Batch contribution error: {e}")
    
    def _calculate_performance_trend(self) -> str:
        """Calculate performance trend for contribution metadata"""
        if len(self.trade_history) < 2:
            return "insufficient_data"
            
        # Get last 5 trades PnL
        recent_trades = self.trade_history[-5:]
        recent_pnl = [trade.pnl for trade in recent_trades if trade.pnl != 0]
        
        if len(recent_pnl) < 2:
            return "neutral"
            
        positive_trades = sum(1 for pnl in recent_pnl if pnl > 0)
        
        if positive_trades >= len(recent_pnl) * 0.7:
            return "improving"
        elif positive_trades <= len(recent_pnl) * 0.3:
            return "declining"
        else:
            return "stable"
    
    def calculate_position_size(self, price: float, supply_chain_factor: float = 1.0) -> float:
        """Calculate position size based on budget constraints"""
        # Base position size as percentage of current balance
        base_size = self.balance * self.position_size_pct
        
        # Apply supply chain factor (adjust position sizing)
        adjusted_size = base_size * supply_chain_factor
        
        # Cap at max position size
        position_value = min(adjusted_size, self.max_position_size)
        
        # Calculate quantity based on current price
        quantity = position_value / price
        
        return quantity
    
    def can_open_position(self, symbol: str, price: float) -> bool:
        """Check if we can open a new position"""
        if symbol in self.positions:
            return False  # Already have position
        
        if len(self.positions) >= self.max_positions:
            return False  # Too many positions
        
        min_position_value = price * self.calculate_position_size(price)
        if self.balance < min_position_value:
            return False  # Not enough balance
        
        return True
    
    def open_position(self, symbol: str, side: str, price: float, supply_chain_factor: float = 1.0, reason: str = "") -> Optional[Position]:
        """Open a new paper trading position"""
        if not self.can_open_position(symbol, price):
            return None
        
        quantity = self.calculate_position_size(price, supply_chain_factor)
        position_value = quantity * price
        
        # Update balance
        self.balance -= position_value
        
        # Calculate stop loss and take profit levels
        if side == "BUY":
            stop_loss = price * (1 - self.stop_loss_pct)
            take_profit = price * (1 + self.take_profit_pct)
        else:
            stop_loss = price * (1 + self.stop_loss_pct)  
            take_profit = price * (1 - self.take_profit_pct)
        
        # Create position
        position = Position(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=price,
            entry_time=time.time(),
            current_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        self.positions[symbol] = position
        
        # Record trade
        trade = Trade(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            timestamp=time.time(),
            reason=reason
        )
        self.trade_history.append(trade)
        
        # Contribute trade data to network
        position_context = {
            'entry_price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_value': position_value,
            'supply_chain_factor': supply_chain_factor
        }
        self._contribute_trade_data(trade, position_context)
        
        print(f"📈 PAPER TRADE: {side} {quantity:.4f} {symbol} @ ${price:.4f} (${position_value:.2f}) | Reason: {reason}")
        print(f"   Balance: ${self.balance:.2f} | Positions: {len(self.positions)}")
        
        return position
    
    def close_position(self, symbol: str, price: float, reason: str = "") -> Optional[float]:
        """Close a paper trading position"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        # Calculate PnL
        if position.side == "BUY":
            pnl = (price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - price) * position.quantity
        
        # Update balance
        position_value = position.quantity * price
        self.balance += position_value
        self.total_pnl += pnl
        
        # Record trade
        trade = Trade(
            symbol=symbol,
            side="SELL" if position.side == "BUY" else "BUY",
            quantity=position.quantity,
            price=price,
            timestamp=time.time(),
            pnl=pnl,
            reason=reason
        )
        self.trade_history.append(trade)
        
        # Contribute closing trade data with position outcome
        position_outcome = {
            'entry_price': position.entry_price,
            'exit_price': price,
            'holding_period': time.time() - position.entry_time,
            'pnl': pnl,
            'pnl_percentage': (pnl / (position.entry_price * position.quantity)) * 100,
            'exit_reason': reason,
            'position_side': position.side
        }
        self._contribute_trade_data(trade, position_outcome)
        
        print(f"📉 PAPER CLOSE: {trade.side} {position.quantity:.4f} {symbol} @ ${price:.4f}")
        print(f"   PnL: ${pnl:+.2f} | Total PnL: ${self.total_pnl:+.2f} | Balance: ${self.balance:.2f}")
        
        # Remove position
        del self.positions[symbol]
        
        return pnl
    
    def update_positions(self, prices: Dict[str, float]):
        """Update all positions with current prices and check stop loss/take profit"""
        positions_to_close = []
        
        for symbol, position in self.positions.items():
            if symbol not in prices:
                continue
                
            current_price = prices[symbol]
            position.current_price = current_price
            
            # Calculate unrealized PnL
            if position.side == "BUY":
                position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
            else:
                position.unrealized_pnl = (position.entry_price - current_price) * position.quantity
            
            # Check stop loss and take profit
            if position.side == "BUY":
                if current_price <= position.stop_loss:
                    positions_to_close.append((symbol, current_price, "Stop Loss"))
                elif current_price >= position.take_profit:
                    positions_to_close.append((symbol, current_price, "Take Profit"))
            else:
                if current_price >= position.stop_loss:
                    positions_to_close.append((symbol, current_price, "Stop Loss"))
                elif current_price <= position.take_profit:
                    positions_to_close.append((symbol, current_price, "Take Profit"))
        
        # Close positions that hit stop loss or take profit
        for symbol, price, reason in positions_to_close:
            self.close_position(symbol, price, reason)
    
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value including unrealized PnL"""
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        return self.balance + unrealized_pnl
    
    def get_portfolio_summary(self) -> dict:
        """Get portfolio summary for display"""
        portfolio_value = self.get_portfolio_value()
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        
        return {
            'balance': self.balance,
            'portfolio_value': portfolio_value,
            'total_pnl': self.total_pnl,
            'unrealized_pnl': unrealized_pnl,
            'active_positions': len(self.positions),
            'total_trades': len(self.trade_history),
            'return_pct': ((portfolio_value - self.starting_balance) / self.starting_balance) * 100
        }
    
    def print_portfolio_status(self):
        """Print current portfolio status"""
        summary = self.get_portfolio_summary()
        
        print(f"\n💼 PORTFOLIO STATUS:")
        print(f"   Balance: ${summary['balance']:,.2f}")
        print(f"   Portfolio Value: ${summary['portfolio_value']:,.2f}")
        print(f"   Total Return: {summary['return_pct']:+.2f}% (${summary['total_pnl'] + summary['unrealized_pnl']:+,.2f})")
        print(f"   Realized PnL: ${summary['total_pnl']:+,.2f}")
        print(f"   Unrealized PnL: ${summary['unrealized_pnl']:+,.2f}")
        print(f"   Active Positions: {summary['active_positions']}/{self.max_positions}")
        print(f"   Total Trades: {summary['total_trades']}")
        
        if self.positions:
            print(f"\n📊 ACTIVE POSITIONS:")
            for symbol, pos in self.positions.items():
                pnl_pct = (pos.unrealized_pnl / (pos.entry_price * pos.quantity)) * 100
                print(f"   {symbol}: {pos.side} {pos.quantity:.4f} @ ${pos.entry_price:.4f} | "
                      f"Current: ${pos.current_price:.4f} | PnL: ${pos.unrealized_pnl:+.2f} ({pnl_pct:+.1f}%)")
    
    def finalize_session(self):
        """Finalize paper trading session and submit any remaining contributions"""
        if self.contribution_enabled and self.contribution_batch:
            print(f"\n🔄 Finalizing session - submitting final batch ({len(self.contribution_batch)} trades)")
            self._submit_contribution_batch()
            
        # Submit session summary
        if self.contribution_enabled:
            self._submit_session_summary()
    
    def _submit_session_summary(self):
        """Submit comprehensive session summary to contribution network"""
        try:
            summary = self.get_portfolio_summary()
            
            session_data = {
                'user_id': self.paper_user_id,
                'data_type': 'paper_trading_session_summary',
                'timestamp': datetime.now().isoformat(),
                'session_metrics': {
                    'starting_balance': self.starting_balance,
                    'ending_balance': summary['balance'],
                    'portfolio_value': summary['portfolio_value'],
                    'total_return_pct': summary['return_pct'],
                    'total_pnl': summary['total_pnl'],
                    'total_trades': summary['total_trades'],
                    'active_positions': summary['active_positions'],
                    'win_rate': self._calculate_win_rate(),
                    'avg_trade_pnl': self._calculate_avg_trade_pnl(),
                    'performance_trend': self._calculate_performance_trend()
                },
                'risk_metrics': {
                    'max_positions': self.max_positions,
                    'position_size_pct': self.position_size_pct,
                    'stop_loss_pct': self.stop_loss_pct,
                    'take_profit_pct': self.take_profit_pct
                }
            }
            
            contribution_id = self.contribution_engine.contribute_data(
                user_id=self.paper_user_id,
                data=session_data
            )
            
            if contribution_id:
                print(f"📊 SESSION SUMMARY CONTRIBUTED:")
                print(f"   Return: {summary['return_pct']:+.2f}% | Trades: {summary['total_trades']}")
                print(f"   Contribution ID: {contribution_id[:8]}...")
                
        except Exception as e:
            print(f"⚠️  Session summary contribution error: {e}")
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate from closed positions"""
        profitable_trades = [trade for trade in self.trade_history if trade.pnl > 0]
        closed_trades = [trade for trade in self.trade_history if trade.pnl != 0]
        
        if not closed_trades:
            return 0.0
            
        return (len(profitable_trades) / len(closed_trades)) * 100
    
    def _calculate_avg_trade_pnl(self) -> float:
        """Calculate average PnL per closed trade"""
        closed_trades = [trade for trade in self.trade_history if trade.pnl != 0]
        
        if not closed_trades:
            return 0.0
            
        return sum(trade.pnl for trade in closed_trades) / len(closed_trades)