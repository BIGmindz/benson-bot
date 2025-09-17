#!/usr/bin/env python3
"""
🚀 BENSON BOT PORTFOLIO MANAGER
Enterprise-grade portfolio management with risk controls and performance tracking
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import pandas as pd
from trade_executor import TradeResult, OrderSide


class PositionStatus(Enum):
    """Position status types"""
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass
class Position:
    """Portfolio position tracking"""
    id: str
    symbol: str
    side: str
    entry_amount: float
    entry_price: float
    current_amount: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    entry_timestamp: str
    last_update: str
    status: PositionStatus
    confidence: float
    signal_strength: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    fees_paid: float = 0.0


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float
    cash_balance: float
    positions_value: float
    total_pnl: float
    daily_pnl: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    largest_win: float
    largest_loss: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: float = 0.0


class PortfolioManager:
    """🎯 Enterprise portfolio management system"""
    
    def __init__(self, db_path: str = "benson_portfolio.db"):
        self.db_path = db_path
        self.logger = self._setup_logging()
        self._init_database()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup portfolio logging"""
        logger = logging.getLogger('PortfolioManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('portfolio_manager.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Initialize portfolio database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Positions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            entry_amount REAL NOT NULL,
            entry_price REAL NOT NULL,
            current_amount REAL NOT NULL,
            current_price REAL NOT NULL,
            unrealized_pnl REAL DEFAULT 0.0,
            realized_pnl REAL DEFAULT 0.0,
            entry_timestamp TEXT NOT NULL,
            last_update TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            signal_strength REAL DEFAULT 0.0,
            stop_loss REAL,
            take_profit REAL,
            fees_paid REAL DEFAULT 0.0,
            metadata TEXT
        )
        ''')
        
        # Trade history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_id TEXT NOT NULL,
            trade_type TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            amount REAL NOT NULL,
            price REAL NOT NULL,
            fee REAL DEFAULT 0.0,
            pnl REAL DEFAULT 0.0,
            timestamp TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            signal_strength REAL DEFAULT 0.0,
            metadata TEXT
        )
        ''')
        
        # Portfolio snapshots table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total_value REAL NOT NULL,
            cash_balance REAL NOT NULL,
            positions_value REAL NOT NULL,
            total_pnl REAL NOT NULL,
            daily_pnl REAL NOT NULL,
            open_positions INTEGER DEFAULT 0,
            metrics TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("📊 Portfolio database initialized")
    
    def add_position(self, trade_result: TradeResult, confidence: float = 0.0, 
                    signal_strength: float = 0.0, stop_loss: float = None, 
                    take_profit: float = None) -> bool:
        """Add new position to portfolio"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            position = Position(
                id=trade_result.order_id,
                symbol=trade_result.symbol,
                side=trade_result.side,
                entry_amount=trade_result.amount,
                entry_price=trade_result.price,
                current_amount=trade_result.amount,
                current_price=trade_result.price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                entry_timestamp=trade_result.timestamp,
                last_update=trade_result.timestamp,
                status=PositionStatus.OPEN,
                confidence=confidence,
                signal_strength=signal_strength,
                stop_loss=stop_loss,
                take_profit=take_profit,
                fees_paid=trade_result.fee
            )
            
            cursor.execute('''
            INSERT INTO positions (
                id, symbol, side, entry_amount, entry_price, current_amount,
                current_price, unrealized_pnl, realized_pnl, entry_timestamp,
                last_update, status, confidence, signal_strength, stop_loss,
                take_profit, fees_paid, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position.id, position.symbol, position.side, position.entry_amount,
                position.entry_price, position.current_amount, position.current_price,
                position.unrealized_pnl, position.realized_pnl, position.entry_timestamp,
                position.last_update, position.status.value, position.confidence,
                position.signal_strength, position.stop_loss, position.take_profit,
                position.fees_paid, json.dumps(trade_result.raw_response)
            ))
            
            # Record trade in history
            self._record_trade_history(cursor, position.id, "OPEN", trade_result, 
                                     confidence, signal_strength)
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"📈 Position added: {position.symbol} | {position.side.upper()} | ${position.entry_amount * position.entry_price:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding position: {e}")
            return False
    
    def update_position(self, position_id: str, current_price: float) -> bool:
        """Update position with current market price"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get current position
            cursor.execute('SELECT * FROM positions WHERE id = ? AND status = "open"', (position_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            # Calculate unrealized PnL
            entry_price = row['entry_price']
            amount = row['current_amount']
            side = row['side']
            
            if side == 'buy':
                unrealized_pnl = (current_price - entry_price) * amount
            else:  # sell
                unrealized_pnl = (entry_price - current_price) * amount
            
            # Update position
            cursor.execute('''
            UPDATE positions 
            SET current_price = ?, unrealized_pnl = ?, last_update = ?
            WHERE id = ?
            ''', (current_price, unrealized_pnl, datetime.now(timezone.utc).isoformat(), position_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating position {position_id}: {e}")
            return False
    
    def close_position(self, position_id: str, exit_trade: TradeResult) -> bool:
        """Close position and calculate realized PnL"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get position
            cursor.execute('SELECT * FROM positions WHERE id = ?', (position_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            # Calculate realized PnL
            entry_price = row['entry_price']
            exit_price = exit_trade.price
            amount = row['entry_amount']
            side = row['side']
            
            if side == 'buy':
                realized_pnl = (exit_price - entry_price) * amount
            else:  # sell
                realized_pnl = (entry_price - exit_price) * amount
            
            # Account for fees
            total_fees = row['fees_paid'] + exit_trade.fee
            realized_pnl -= total_fees
            
            # Update position
            cursor.execute('''
            UPDATE positions 
            SET status = ?, realized_pnl = ?, current_price = ?, 
                unrealized_pnl = 0.0, fees_paid = ?, last_update = ?
            WHERE id = ?
            ''', (PositionStatus.CLOSED.value, realized_pnl, exit_price, 
                  total_fees, exit_trade.timestamp, position_id))
            
            # Record closing trade
            self._record_trade_history(cursor, position_id, "CLOSE", exit_trade)
            
            conn.commit()
            conn.close()
            
            pnl_emoji = "📈" if realized_pnl > 0 else "📉"
            self.logger.info(f"{pnl_emoji} Position closed: {row['symbol']} | PnL: ${realized_pnl:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
            return False
    
    def _record_trade_history(self, cursor, position_id: str, trade_type: str, 
                            trade_result: TradeResult, confidence: float = 0.0, 
                            signal_strength: float = 0.0):
        """Record trade in history table"""
        cursor.execute('''
        INSERT INTO trade_history (
            position_id, trade_type, symbol, side, amount, price, fee,
            timestamp, confidence, signal_strength, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            position_id, trade_type, trade_result.symbol, trade_result.side,
            trade_result.amount, trade_result.price, trade_result.fee,
            trade_result.timestamp, confidence, signal_strength,
            json.dumps(trade_result.raw_response)
        ))
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM positions WHERE status = "open"')
            rows = cursor.fetchall()
            
            positions = []
            for row in rows:
                position = Position(
                    id=row['id'],
                    symbol=row['symbol'],
                    side=row['side'],
                    entry_amount=row['entry_amount'],
                    entry_price=row['entry_price'],
                    current_amount=row['current_amount'],
                    current_price=row['current_price'],
                    unrealized_pnl=row['unrealized_pnl'],
                    realized_pnl=row['realized_pnl'],
                    entry_timestamp=row['entry_timestamp'],
                    last_update=row['last_update'],
                    status=PositionStatus(row['status']),
                    confidence=row['confidence'],
                    signal_strength=row['signal_strength'],
                    stop_loss=row['stop_loss'],
                    take_profit=row['take_profit'],
                    fees_paid=row['fees_paid']
                )
                positions.append(position)
            
            conn.close()
            return positions
            
        except Exception as e:
            self.logger.error(f"Error getting open positions: {e}")
            return []
    
    def get_portfolio_metrics(self, cash_balance: float) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all positions
            cursor.execute('SELECT * FROM positions')
            positions = cursor.fetchall()
            
            # Calculate metrics
            total_pnl = sum(row['realized_pnl'] + row['unrealized_pnl'] for row in positions)
            positions_value = sum(row['current_amount'] * row['current_price'] 
                                for row in positions if row['status'] == 'open')
            
            # Get closed positions for win rate
            cursor.execute('SELECT realized_pnl FROM positions WHERE status = "closed"')
            closed_positions = cursor.fetchall()
            
            winning_trades = sum(1 for pos in closed_positions if pos['realized_pnl'] > 0)
            losing_trades = len(closed_positions) - winning_trades
            win_rate = (winning_trades / len(closed_positions) * 100) if closed_positions else 0.0
            
            largest_win = max((pos['realized_pnl'] for pos in closed_positions), default=0.0)
            largest_loss = min((pos['realized_pnl'] for pos in closed_positions), default=0.0)
            
            # Get today's PnL
            today = datetime.now(timezone.utc).date().isoformat()
            cursor.execute('''
            SELECT SUM(realized_pnl) as daily_pnl 
            FROM positions 
            WHERE DATE(entry_timestamp) = ?
            ''', (today,))
            daily_pnl_row = cursor.fetchone()
            daily_pnl = daily_pnl_row['daily_pnl'] if daily_pnl_row['daily_pnl'] else 0.0
            
            conn.close()
            
            metrics = PortfolioMetrics(
                total_value=cash_balance + positions_value,
                cash_balance=cash_balance,
                positions_value=positions_value,
                total_pnl=total_pnl,
                daily_pnl=daily_pnl,
                win_rate=win_rate,
                total_trades=len(positions),
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                largest_win=largest_win,
                largest_loss=largest_loss
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio metrics: {e}")
            return PortfolioMetrics(
                total_value=cash_balance, cash_balance=cash_balance, positions_value=0.0,
                total_pnl=0.0, daily_pnl=0.0, win_rate=0.0, total_trades=0,
                winning_trades=0, losing_trades=0, largest_win=0.0, largest_loss=0.0
            )
    
    def save_portfolio_snapshot(self, metrics: PortfolioMetrics):
        """Save portfolio snapshot for historical tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO portfolio_snapshots (
                timestamp, total_value, cash_balance, positions_value,
                total_pnl, daily_pnl, open_positions, metrics
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(timezone.utc).isoformat(),
                metrics.total_value, metrics.cash_balance, metrics.positions_value,
                metrics.total_pnl, metrics.daily_pnl, 
                len(self.get_open_positions()),
                json.dumps(asdict(metrics))
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving portfolio snapshot: {e}")
    
    def check_stop_loss_take_profit(self, current_prices: Dict[str, float]) -> List[str]:
        """Check for stop loss or take profit triggers"""
        positions_to_close = []
        
        try:
            open_positions = self.get_open_positions()
            
            for position in open_positions:
                symbol = position.symbol
                current_price = current_prices.get(symbol)
                
                if not current_price:
                    continue
                
                should_close = False
                reason = ""
                
                # Check stop loss
                if position.stop_loss:
                    if (position.side == 'buy' and current_price <= position.stop_loss) or \
                       (position.side == 'sell' and current_price >= position.stop_loss):
                        should_close = True
                        reason = f"Stop loss triggered at ${current_price:.2f}"
                
                # Check take profit
                if position.take_profit and not should_close:
                    if (position.side == 'buy' and current_price >= position.take_profit) or \
                       (position.side == 'sell' and current_price <= position.take_profit):
                        should_close = True
                        reason = f"Take profit triggered at ${current_price:.2f}"
                
                if should_close:
                    self.logger.info(f"🎯 {reason} for {symbol} position {position.id}")
                    positions_to_close.append(position.id)
            
        except Exception as e:
            self.logger.error(f"Error checking stop loss/take profit: {e}")
        
        return positions_to_close


if __name__ == "__main__":
    # Example usage
    portfolio = PortfolioManager()
    
    # Get portfolio status
    metrics = portfolio.get_portfolio_metrics(1000.0)
    print(f"Portfolio Status: ${metrics.total_value:.2f}")
    print(f"Win Rate: {metrics.win_rate:.1f}%")