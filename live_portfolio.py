#!/usr/bin/env python3
"""
🚀 LIVE TRADING PORTFOLIO MANAGER
Real money trading with comprehensive safety mechanisms
Extends paper trading system with live execution capabilities
"""

import os
import time
import ccxt
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from paper_portfolio import PaperTradingPortfolio, Position, Trade

@dataclass
class LiveTradingLimits:
    """Safety limits for live trading"""
    max_daily_loss: float = 100.0
    max_position_size: float = 50.0
    max_positions: int = 3
    min_balance: float = 200.0
    daily_trade_limit: int = 20
    cooldown_after_loss: int = 300  # 5 minutes
    emergency_stop: bool = False

class LiveTradingPortfolio(PaperTradingPortfolio):
    """
    🔴 LIVE TRADING PORTFOLIO MANAGER
    
    Executes real trades on Kraken with comprehensive safety mechanisms:
    - Multiple safety checks before each trade
    - Daily loss limits and emergency stops
    - Balance verification and position limits
    - Real-time risk monitoring
    """
    
    def __init__(self, config: dict):
        """Initialize live trading portfolio with safety mechanisms"""
        super().__init__(config)
        
        # Load environment variables for API credentials
        self.api_key = os.getenv('KRAKEN_API_KEY')
        self.api_secret = os.getenv('KRAKEN_SECRET')
        self.live_trading_enabled = os.getenv('LIVE_TRADING_ENABLED', 'false').lower() == 'true'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("🚨 MISSING KRAKEN CREDENTIALS - Set KRAKEN_API_KEY and KRAKEN_SECRET environment variables")
        
        if not self.live_trading_enabled:
            raise ValueError("🚨 LIVE TRADING DISABLED - Set LIVE_TRADING_ENABLED=true in environment variables")
        
        # Initialize live trading exchange
        self.exchange = ccxt.kraken({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'sandbox': False,  # 🚨 LIVE TRADING
            'enableRateLimit': True,
        })
        
        # Load live trading configuration
        live_config = config.get('live_trading', {})
        self.limits = LiveTradingLimits(
            max_daily_loss=live_config.get('daily_loss_limit', 100.0),
            max_position_size=live_config.get('max_position_size', 50.0),
            max_positions=live_config.get('max_positions', 3),
            min_balance=live_config.get('min_balance', 200.0),
            emergency_stop=os.getenv('EMERGENCY_STOP', 'false').lower() == 'true'
        )
        
        # Daily tracking
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.last_trade_time = 0
        self.last_reset_date = datetime.now().date()
        
        # Safety state
        self.safety_violations = []
        self.last_violation_time = 0
        
        # Real balance tracking
        self.real_balance = 0.0
        self.last_balance_check = 0
        
        print("🚨 LIVE TRADING PORTFOLIO INITIALIZED")
        print("⚠️  WARNING: This will execute REAL TRADES with REAL MONEY")
        print(f"   API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
        print(f"   Daily Loss Limit: ${self.limits.max_daily_loss}")
        print(f"   Max Position Size: ${self.limits.max_position_size}")
        print(f"   Max Positions: {self.limits.max_positions}")
        print(f"   Min Balance: ${self.limits.min_balance}")
        
        # Initial safety check
        self._perform_startup_safety_check()
    
    def _perform_startup_safety_check(self):
        """Comprehensive startup safety verification"""
        print("🔍 Performing startup safety checks...")
        
        try:
            # Check exchange connection
            self.exchange.load_markets()
            print("✅ Exchange connection verified")
            
            # Check account balance
            self._update_real_balance()
            if self.real_balance < self.limits.min_balance:
                raise ValueError(f"🚨 INSUFFICIENT BALANCE: ${self.real_balance:.2f} < ${self.limits.min_balance:.2f}")
            print(f"✅ Balance verified: ${self.real_balance:.2f}")
            
            # Check for emergency stop
            if self.limits.emergency_stop:
                raise ValueError("🚨 EMERGENCY STOP ACTIVE - Trading disabled")
            print("✅ Emergency stop: Inactive")
            
            # Reset daily counters if new day
            self._reset_daily_counters_if_needed()
            
            print("🟢 ALL SAFETY CHECKS PASSED - Live trading authorized")
            
        except Exception as e:
            print(f"🚨 STARTUP SAFETY CHECK FAILED: {e}")
            raise
    
    def _update_real_balance(self) -> float:
        """Get real account balance from Kraken"""
        current_time = time.time()
        
        # Cache balance for 30 seconds to avoid API spam
        if current_time - self.last_balance_check < 30:
            return self.real_balance
        
        try:
            balance = self.exchange.fetch_balance()
            self.real_balance = balance['USD']['free'] if 'USD' in balance else 0.0
            self.last_balance_check = current_time
            return self.real_balance
        except Exception as e:
            print(f"⚠️ Balance check failed: {e}")
            return self.real_balance  # Return cached value
    
    def _reset_daily_counters_if_needed(self):
        """Reset daily tracking if it's a new day"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            print(f"📅 New trading day - resetting counters")
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset_date = today
            self.safety_violations = []
    
    def _comprehensive_safety_check(self, symbol: str, side: str, price: float, quantity: float) -> bool:
        """Comprehensive safety verification before executing trade"""
        print(f"🔒 Safety check: {side} {quantity:.6f} {symbol} @ ${price:.4f}")
        
        # Reset daily counters if needed
        self._reset_daily_counters_if_needed()
        
        # 1. Emergency stop check
        if self.limits.emergency_stop or os.getenv('EMERGENCY_STOP', 'false').lower() == 'true':
            print("🚨 TRADE BLOCKED: Emergency stop active")
            return False
        
        # 2. Daily loss limit check
        if self.daily_pnl <= -self.limits.max_daily_loss:
            print(f"🚨 TRADE BLOCKED: Daily loss limit reached (${self.daily_pnl:.2f})")
            self.safety_violations.append(f"Daily loss limit: ${self.daily_pnl:.2f}")
            return False
        
        # 3. Daily trade limit check
        if self.daily_trades >= self.limits.daily_trade_limit:
            print(f"🚨 TRADE BLOCKED: Daily trade limit reached ({self.daily_trades})")
            return False
        
        # 4. Position size check
        position_value = quantity * price
        if position_value > self.limits.max_position_size:
            print(f"🚨 TRADE BLOCKED: Position too large (${position_value:.2f} > ${self.limits.max_position_size})")
            return False
        
        # 5. Maximum positions check
        if len(self.positions) >= self.limits.max_positions and symbol not in self.positions:
            print(f"🚨 TRADE BLOCKED: Max positions reached ({len(self.positions)})")
            return False
        
        # 6. Balance check
        current_balance = self._update_real_balance()
        if current_balance < self.limits.min_balance:
            print(f"🚨 TRADE BLOCKED: Insufficient balance (${current_balance:.2f} < ${self.limits.min_balance})")
            return False
        
        # 7. Cooldown after losses
        if self.safety_violations and (time.time() - self.last_violation_time) < self.limits.cooldown_after_loss:
            remaining = self.limits.cooldown_after_loss - (time.time() - self.last_violation_time)
            print(f"🚨 TRADE BLOCKED: Cooldown active ({remaining:.0f}s remaining)")
            return False
        
        # 8. Market hours check (optional - Kraken is 24/7)
        # Could add specific trading hours if desired
        
        print("✅ All safety checks passed")
        return True
    
    def execute_live_trade(self, symbol: str, side: str, price: float, supply_chain_factor: float = 1.0, reason: str = "") -> Optional[Position]:
        """
        🚨 EXECUTE LIVE TRADE - REAL MONEY TRANSACTION
        
        This function executes actual trades on Kraken with real money.
        Multiple safety checks are performed before execution.
        """
        
        # Calculate position size (conservative for live trading)
        quantity = self.calculate_position_size(price, supply_chain_factor) * 0.5  # 50% of paper size for safety
        
        # Comprehensive safety verification
        if not self._comprehensive_safety_check(symbol, side, price, quantity):
            return None
        
        try:
            print(f"🚨 EXECUTING LIVE TRADE: {side} {quantity:.6f} {symbol} @ ${price:.4f}")
            print(f"   Position Value: ${quantity * price:.2f}")
            print(f"   Reason: {reason}")
            print("   ⚠️  REAL MONEY TRANSACTION IN PROGRESS...")
            
            # Execute the actual trade on Kraken
            if side == "BUY":
                order = self.exchange.create_market_buy_order(symbol, quantity)
            else:
                order = self.exchange.create_market_sell_order(symbol, quantity)
            
            print(f"✅ LIVE TRADE EXECUTED: Order ID {order['id']}")
            
            # Update tracking
            self.daily_trades += 1
            self.last_trade_time = time.time()
            
            # Create position record (similar to paper trading)
            position = Position(
                symbol=symbol,
                side=side,
                quantity=float(order['filled']),  # Use actual filled quantity
                entry_price=float(order['average']),  # Use actual average price
                entry_time=time.time(),
                current_price=float(order['average']),
                stop_loss=float(order['average']) * (0.97 if side == "BUY" else 1.03),
                take_profit=float(order['average']) * (1.06 if side == "BUY" else 0.94),
                reason=f"LIVE: {reason}"
            )
            
            # Add to positions
            self.positions[symbol] = position
            
            # Create trade record
            trade = Trade(
                symbol=symbol,
                side=side,
                quantity=position.quantity,
                price=position.entry_price,
                timestamp=position.entry_time,
                pnl=0.0,  # Will be calculated when closed
                reason=f"LIVE OPEN: {reason}"
            )
            
            self.trade_history.append(trade)
            
            # Update real balance
            self._update_real_balance()
            
            print(f"🎯 LIVE POSITION OPENED: {symbol}")
            print(f"   Quantity: {position.quantity:.6f}")
            print(f"   Entry Price: ${position.entry_price:.4f}")
            print(f"   Stop Loss: ${position.stop_loss:.4f}")
            print(f"   Take Profit: ${position.take_profit:.4f}")
            print(f"   Balance: ${self.real_balance:.2f}")
            
            return position
            
        except Exception as e:
            print(f"🚨 LIVE TRADE EXECUTION FAILED: {e}")
            self.safety_violations.append(f"Trade execution error: {str(e)[:50]}")
            self.last_violation_time = time.time()
            return None
    
    def close_live_position(self, symbol: str, reason: str = "Manual close") -> bool:
        """Close a live trading position"""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        try:
            # Get current market price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            print(f"🚨 CLOSING LIVE POSITION: {symbol}")
            print(f"   Entry: ${position.entry_price:.4f} → Current: ${current_price:.4f}")
            
            # Execute close order (opposite side)
            close_side = "SELL" if position.side == "BUY" else "BUY"
            
            if close_side == "SELL":
                order = self.exchange.create_market_sell_order(symbol, position.quantity)
            else:
                order = self.exchange.create_market_buy_order(symbol, position.quantity)
            
            # Calculate P&L
            if position.side == "BUY":
                pnl = (current_price - position.entry_price) * position.quantity
            else:
                pnl = (position.entry_price - current_price) * position.quantity
            
            # Update daily P&L
            self.daily_pnl += pnl
            self.total_pnl += pnl
            
            print(f"✅ LIVE POSITION CLOSED: {symbol}")
            print(f"   P&L: ${pnl:+.2f}")
            print(f"   Daily P&L: ${self.daily_pnl:+.2f}")
            print(f"   Total P&L: ${self.total_pnl:+.2f}")
            
            # Create close trade record
            close_trade = Trade(
                symbol=symbol,
                side=close_side,
                quantity=position.quantity,
                price=current_price,
                timestamp=time.time(),
                pnl=pnl,
                reason=f"LIVE CLOSE: {reason}"
            )
            
            self.trade_history.append(close_trade)
            
            # Remove position
            del self.positions[symbol]
            
            # Update balance
            self._update_real_balance()
            
            return True
            
        except Exception as e:
            print(f"🚨 FAILED TO CLOSE LIVE POSITION {symbol}: {e}")
            return False
    
    def get_live_portfolio_summary(self) -> dict:
        """Get comprehensive live trading portfolio summary"""
        summary = super().get_portfolio_summary()
        
        # Add live trading specific metrics
        summary.update({
            'real_balance': self.real_balance,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'daily_loss_limit': self.limits.max_daily_loss,
            'safety_violations': len(self.safety_violations),
            'emergency_stop': self.limits.emergency_stop,
            'live_trading_enabled': self.live_trading_enabled
        })
        
        return summary
    
    def print_live_status(self):
        """Print comprehensive live trading status"""
        print(f"\n🚨 LIVE TRADING PORTFOLIO STATUS:")
        print(f"   Real Balance: ${self.real_balance:.2f}")
        print(f"   Daily P&L: ${self.daily_pnl:+.2f} (Limit: -${self.limits.max_daily_loss})")
        print(f"   Daily Trades: {self.daily_trades} (Limit: {self.limits.daily_trade_limit})")
        print(f"   Active Positions: {len(self.positions)}/{self.limits.max_positions}")
        print(f"   Total P&L: ${self.total_pnl:+.2f}")
        print(f"   Safety Violations: {len(self.safety_violations)}")
        
        if self.safety_violations:
            print(f"   Recent Violations:")
            for violation in self.safety_violations[-3:]:
                print(f"     • {violation}")
        
        if self.positions:
            print(f"\n📊 LIVE POSITIONS:")
            for symbol, pos in self.positions.items():
                # Get current price for P&L calculation
                try:
                    ticker = self.exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    if pos.side == "BUY":
                        unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
                    else:
                        unrealized_pnl = (pos.entry_price - current_price) * pos.quantity
                    
                    print(f"   {symbol}: {pos.side} {pos.quantity:.6f} @ ${pos.entry_price:.4f}")
                    print(f"     Current: ${current_price:.4f} | P&L: ${unrealized_pnl:+.2f}")
                    print(f"     Stop: ${pos.stop_loss:.4f} | Target: ${pos.take_profit:.4f}")
                except:
                    print(f"   {symbol}: {pos.side} {pos.quantity:.6f} @ ${pos.entry_price:.4f} (Price update failed)")


def create_live_trading_setup():
    """Interactive setup for live trading transition"""
    print("🚨 BENSON BOT - LIVE TRADING SETUP")
    print("=" * 60)
    print("⚠️  WARNING: This will configure REAL MONEY trading")
    print("🔐 You will need Kraken API credentials with trading permissions")
    print("")
    
    # Check if .env file exists
    env_file = "/Users/johnbozza/Library/Mobile Documents/com~apple~CloudDocs/Benson Bot/.env"
    
    if not os.path.exists(env_file):
        print("📝 Creating .env file from template...")
        import shutil
        shutil.copy(".env.template", ".env")
        print("✅ .env file created")
        print("")
        print("🔧 NEXT STEPS:")
        print("1. Edit the .env file and add your Kraken API credentials")
        print("2. Set LIVE_TRADING_ENABLED=true when ready")
        print("3. Run the bot with live trading enabled")
        print("")
        print("⚠️  IMPORTANT: Never commit .env file to version control!")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('KRAKEN_API_KEY')
    secret = os.getenv('KRAKEN_SECRET') 
    enabled = os.getenv('LIVE_TRADING_ENABLED', 'false').lower() == 'true'
    
    print("🔍 Checking configuration...")
    
    if not api_key or api_key == 'your_kraken_api_key_here':
        print("❌ KRAKEN_API_KEY not configured")
        return False
    
    if not secret or secret == 'your_kraken_secret_here':
        print("❌ KRAKEN_SECRET not configured")
        return False
    
    if not enabled:
        print("❌ LIVE_TRADING_ENABLED is false")
        return False
    
    print("✅ Credentials configured")
    print("✅ Live trading enabled")
    print("")
    print("🎯 Ready for live trading!")
    return True

if __name__ == "__main__":
    print("🚨 LIVE TRADING PORTFOLIO MANAGER")
    print("⚠️  WARNING: This manages REAL MONEY trades")
    print("=" * 60)
    
    if not create_live_trading_setup():
        print("❌ Live trading setup incomplete")
        exit(1)
    
    # Load configuration
    import yaml
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize live trading portfolio
    try:
        portfolio = LiveTradingPortfolio(config)
        portfolio.print_live_status()
        
        print("\n🟢 Live trading portfolio ready!")
        print("💡 Use portfolio.execute_live_trade() to place trades")
        
    except Exception as e:
        print(f"❌ Failed to initialize live trading: {e}")
        exit(1)