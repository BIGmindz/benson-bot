#!/usr/bin/env python3
"""
🚀 BENSON BOT TRADE EXECUTION ENGINE
Enterprise-grade modular trading system with security and scalability
"""

import os
import time
import logging
import math
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import ccxt
from dotenv import load_dotenv
import json
from datetime import datetime, timezone


# Load environment variables
load_dotenv()

def env_float(name, default):
    """Safe envir        try:
            # Get total portfolio value instead of just free USD
            portfolio = self.get_total_portfolio_value()
            total_value = portfolio['total_usd_value']
            free_usd = portfolio['free_usd']
            
            self.logger.info(f"💰 Portfolio value: ${total_value:.2f} (Free USD: ${free_usd:.2f})")
            
            # Calculate desired trade size based on total portfolio, not just free cash
            desired_usd = None
            if hasattr(request, 'confidence') and hasattr(request, 'signal_strength'):
                # Use total portfolio value for position sizing
                base_amount = min(BASE_TRADE_USD, total_value * MAX_POSITION_PCT)
                if request.confidence >= 0.85 and request.signal_strength >= 0.8:
                    high_confidence_boost = self.config.get('live_trading', {}).get('high_confidence_boost', 1.65)
                    desired_usd = base_amount * high_confidence_boost
                    self.logger.info(f"🚀 High confidence trade: {high_confidence_boost}x boost applied")
                else:
                    desired_usd = base_amount
            else:
                desired_usd = min(BASE_TRADE_USD, total_value * MAX_POSITION_PCT)
            
            # For buy orders, ensure we have enough USD (liquidate positions if needed)
            if request.side.value == 'buy':
                available_usd = self.ensure_usd_available(desired_usd + MIN_CASH_BUFFER_USD)
                if available_usd < desired_usd:
                    self.logger.warning(f"🚫 Insufficient portfolio value for trade: need ${desired_usd:.2f}, have ${available_usd:.2f}")
                    return TradeResult(
                        success=False,
                        symbol=request.symbol,
                        error_message=f"Insufficient portfolio value after liquidation attempts"
                    )
            
            # For sell orders, check if we're selling the position we already own
            elif request.side.value == 'sell':
                base_currency = request.symbol.split('/')[0]
                if base_currency in portfolio['positions']:
                    position_info = portfolio['positions'][base_currency]
                    self.logger.info(f"📊 Existing {base_currency} position: {position_info['amount']:.6f} (${position_info['usd_value']:.2f})")to float conversion"""
    try:
        return float(os.getenv(name, default))
    except Exception:
        return float(default)

# Safe order placement configuration from environment
BASE_TRADE_USD = env_float("BASE_TRADE_USD", 10)
MAX_POSITION_PCT = env_float("MAX_POSITION_PCT", 0.20)
MIN_CASH_BUFFER_USD = env_float("MIN_CASH_BUFFER_USD", 5)
SLIPPAGE_PCT = env_float("SLIPPAGE_PCT", 0.005)


def _kraken_quote_symbol(symbol: str) -> str:
    """Extract quote currency from symbol"""
    if "/" in symbol:
        return symbol.split("/")[1]
    if ":" in symbol:
        return symbol.split(":")[1]
    return "USD"


def _market_min_cost(exchange, symbol):
    """Get minimum cost requirement for symbol"""
    try:
        m = exchange.market(symbol)
        limits = m.get("limits") or {}
        cost = (limits.get("cost") or {}).get("min")
        if cost:
            return float(cost)
        return 0.0
    except Exception:
        return 0.0


def _amount_precision(exchange, symbol, amount):
    """Apply exchange precision rules to amount"""
    try:
        return float(exchange.amount_to_precision(symbol, amount))
    except Exception:
        return float(f"{amount:.8f}")


def _price_with_slippage(price, side):
    """Apply slippage buffer to price"""
    if side.lower() == "buy":
        return price * (1 + SLIPPAGE_PCT)
    else:
        return price * (1 - SLIPPAGE_PCT)


def place_market_order_safe(exchange, symbol, side, desired_usd=None, dry_run=False, logger=print):
    """
    Places a market order sized strictly by AVAILABLE balance.
    - Leaves MIN_CASH_BUFFER_USD untouched.
    - Caps per-trade spend by MAX_POSITION_PCT of available cash.
    - Honors Kraken min cost and symbol precision.
    - Returns dict with 'status' and details.
    """
    side = side.lower()
    if side not in ("buy", "sell"):
        return {"status": "error", "msg": f"invalid side {side}"}

    # 1) Pull balances and price
    bal = exchange.fetch_balance()
    quote = _kraken_quote_symbol(symbol)
    free = (bal.get("free") or {}).get(quote, 0.0) or 0.0

    # For sells, the "available" asset is base
    base = symbol.split("/")[0] if "/" in symbol else symbol.split(":")[0]
    free_base = (bal.get("free") or {}).get(base, 0.0) or 0.0

    ticker = exchange.fetch_ticker(symbol)
    last = float(ticker["last"] or ticker["close"] or ticker["bid"] or ticker["ask"])
    px = _price_with_slippage(last, side)

    # 2) Compute spendable/cap
    if side == "buy":
        spendable = max(0.0, free - MIN_CASH_BUFFER_USD)
        cap_by_pct = free * MAX_POSITION_PCT
        budget = min(desired_usd or BASE_TRADE_USD, spendable, cap_by_pct)
        if budget <= 0.0:
            return {"status": "skip", "msg": "insufficient available USD after buffer"}
        raw_amount = budget / px
    else:
        # sell path — limit by available base units
        if free_base <= 0.0:
            return {"status": "skip", "msg": f"no available {base} to sell"}
        target_units = (desired_usd or BASE_TRADE_USD) / px
        raw_amount = min(free_base, target_units)

    # 3) Respect precision & min cost
    amount = _amount_precision(exchange, symbol, raw_amount)
    if amount <= 0.0:
        return {"status": "skip", "msg": "amount collapsed to 0 after precision"}

    notional = amount * px
    min_cost = _market_min_cost(exchange, symbol)
    if min_cost and notional < min_cost:
        # try to raise to min cost but still within spendable/available
        needed_units = min_cost / px
        adj_amount = _amount_precision(exchange, symbol, needed_units)
        if side == "buy":
            # check if we actually have cash to do this
            if adj_amount * px > max(0.0, free - MIN_CASH_BUFFER_USD):
                return {"status": "skip", "msg": f"below Kraken min notional ({min_cost}), insufficient cash to meet it"}
        else:
            # selling: check if we have the base units
            if adj_amount > free_base:
                return {"status": "skip", "msg": f"below Kraken min notional ({min_cost}), insufficient base to meet it"}
        amount = adj_amount
        notional = amount * px

    # 4) Place order (or dry run)
    if dry_run:
        return {
            "status": "dry_run",
            "symbol": symbol,
            "side": side,
            "price": px,
            "amount": amount,
            "notional": notional,
            "free_usd": free,
            "free_base": free_base
        }

    try:
        order = exchange.create_order(symbol, "market", side, amount)
        return {"status": "ok", "order": order, "amount": amount, "price": px, "notional": notional}
    except Exception as e:
        logger(f"[order-error] {symbol} {side} -> {e}")
        return {"status": "error", "msg": str(e)}


class OrderType(Enum):
    """Supported order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop-loss"
    TAKE_PROFIT = "take-profit"


class OrderSide(Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class TradeRequest:
    """Immutable trade request structure"""
    symbol: str
    side: OrderSide
    amount: float
    order_type: OrderType = OrderType.MARKET
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 0.0
    signal_strength: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class TradeResult:
    """Trade execution result"""
    success: bool
    order_id: Optional[str] = None
    symbol: str = ""
    side: str = ""
    amount: float = 0.0
    price: float = 0.0
    fee: float = 0.0
    timestamp: str = ""
    error_message: Optional[str] = None
    raw_response: Dict = None


class SecurityManager:
    """🔐 Security and validation layer"""
    
    def __init__(self, max_position_size: float, max_daily_loss: float):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.daily_losses = 0.0
        self.daily_reset_time = datetime.now(timezone.utc).date()
        
    def validate_trade_request(self, request: TradeRequest, current_balance: float) -> Tuple[bool, str]:
        """Validate trade request against security rules"""
        
        # Reset daily losses if new day
        current_date = datetime.now(timezone.utc).date()
        if current_date > self.daily_reset_time:
            self.daily_losses = 0.0
            self.daily_reset_time = current_date
        
        # Check daily loss limit
        if self.daily_losses >= self.max_daily_loss:
            return False, f"Daily loss limit exceeded: ${self.daily_losses:.2f} >= ${self.max_daily_loss:.2f}"
        
        # Check position size
        position_value = request.amount * (request.price or 0)
        if position_value > self.max_position_size:
            return False, f"Position size too large: ${position_value:.2f} > ${self.max_position_size:.2f}"
        
        # Check sufficient balance
        if position_value > current_balance:
            return False, f"Insufficient balance: ${position_value:.2f} > ${current_balance:.2f}"
        
        # Validate symbol format
        if not request.symbol or '/' not in request.symbol:
            return False, f"Invalid symbol format: {request.symbol}"
        
        # Validate amount
        if request.amount <= 0:
            return False, f"Invalid amount: {request.amount}"
        
        return True, "Trade request validated"
    
    def record_loss(self, loss_amount: float):
        """Record a trading loss"""
        if loss_amount > 0:
            self.daily_losses += loss_amount


class TradeExecutor:
    """🎯 Core trade execution engine with enterprise features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        self.exchange = self._initialize_exchange()
        self.security_manager = SecurityManager(
            max_position_size=config.get('live_trading', {}).get('max_position_size', 50.0),
            max_daily_loss=config.get('live_trading', {}).get('daily_loss_limit', 50.0)
        )
        self.positions = {}  # Track open positions
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('TradeExecutor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler
            handler = logging.FileHandler('trade_executor.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Console handler for critical events
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize exchange connection with credentials"""
        load_dotenv()
        
        exchange_id = self.config.get("exchange", "kraken")
        
        # Get API credentials
        api_key = os.getenv("KRAKEN_API_KEY")
        api_secret = os.getenv("KRAKEN_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError("Missing Kraken API credentials in .env file")
        
        # Initialize exchange
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'sandbox': False,  # Ensure live trading
        })
        
        # Test connection
        try:
            exchange.load_markets()
            balance = exchange.fetch_balance()
            self.logger.info(f"✅ Exchange connection established: {exchange_id}")
            self.logger.info(f"💰 Account balance loaded successfully")
        except Exception as e:
            self.logger.error(f"❌ Exchange connection failed: {e}")
            raise
        
        return exchange
    
    def get_account_balance(self) -> float:
        """Get current USD balance"""
        try:
            balance = self.exchange.fetch_balance()
            usd_balance = balance.get('USD', {}).get('free', 0.0)
            return float(usd_balance)
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return 0.0
    
    def get_total_portfolio_value(self) -> Dict[str, float]:
        """Get total portfolio value including all allocated positions"""
        try:
            balance = self.exchange.fetch_balance()
            total_usd_value = 0.0
            position_details = {}
            
            for currency, amounts in balance.items():
                if isinstance(amounts, dict) and amounts.get('total', 0) > 0.00001:
                    total_amount = amounts.get('total', 0)
                    
                    if currency == 'USD':
                        # Direct USD value
                        usd_value = total_amount
                        total_usd_value += usd_value
                        position_details[currency] = {
                            'amount': total_amount,
                            'usd_value': usd_value,
                            'price': 1.0
                        }
                    else:
                        # Get current market price for non-USD assets
                        try:
                            symbol = f'{currency}/USD'
                            # Handle Kraken's special futures/staking symbols
                            if '.F' in currency or '.S' in currency or '.B' in currency:
                                # Skip these special derivatives for now
                                continue
                                
                            ticker = self.exchange.fetch_ticker(symbol)
                            current_price = ticker['last']
                            usd_value = total_amount * current_price
                            total_usd_value += usd_value
                            
                            position_details[currency] = {
                                'amount': total_amount,
                                'usd_value': usd_value,
                                'price': current_price,
                                'symbol': symbol
                            }
                            
                        except Exception as e:
                            self.logger.warning(f"Could not get USD value for {currency}: {e}")
                            continue
            
            return {
                'total_usd_value': total_usd_value,
                'free_usd': balance.get('USD', {}).get('free', 0.0),
                'positions': position_details
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching portfolio value: {e}")
            return {'total_usd_value': 0.0, 'free_usd': 0.0, 'positions': {}}
    
    def liquidate_position(self, currency: str, amount: float = None) -> bool:
        """Liquidate a specific position to free up USD"""
        try:
            # Get current balance for this currency
            balance = self.exchange.fetch_balance()
            available_amount = balance.get(currency, {}).get('free', 0.0)
            
            if available_amount <= 0.00001:
                self.logger.warning(f"No {currency} available to liquidate")
                return False
            
            # Use provided amount or liquidate all
            sell_amount = amount if amount and amount <= available_amount else available_amount
            
            symbol = f'{currency}/USD'
            
            # Use our safe order placement for selling
            safe_result = place_market_order_safe(
                exchange=self.exchange,
                symbol=symbol,
                side='sell',
                desired_usd=None,  # Sell specific amount, not USD value
                dry_run=False,
                logger=self.logger.info
            )
            
            if safe_result["status"] == "ok":
                self.logger.info(f"✅ Liquidated {sell_amount:.6f} {currency} → ${safe_result['notional']:.2f}")
                return True
            else:
                self.logger.error(f"❌ Failed to liquidate {currency}: {safe_result['msg']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error liquidating {currency}: {e}")
            return False
    
    def ensure_usd_available(self, needed_usd: float) -> float:
        """Ensure enough USD is available by liquidating positions if needed"""
        portfolio = self.get_total_portfolio_value()
        free_usd = portfolio['free_usd']
        
        if free_usd >= needed_usd:
            return free_usd  # Already have enough
        
        # Need to liquidate some positions
        deficit = needed_usd - free_usd
        self.logger.info(f"💰 Need ${needed_usd:.2f}, have ${free_usd:.2f}, liquidating ${deficit:.2f}")
        
        # Sort positions by USD value (largest first)
        positions = portfolio['positions']
        tradeable_positions = [(k, v) for k, v in positions.items() 
                              if k != 'USD' and 'symbol' in v]
        tradeable_positions.sort(key=lambda x: x[1]['usd_value'], reverse=True)
        
        liquidated_value = 0.0
        for currency, pos_info in tradeable_positions:
            if liquidated_value >= deficit:
                break  # We have enough now
                
            # Try to liquidate this position
            if self.liquidate_position(currency):
                liquidated_value += pos_info['usd_value']
                self.logger.info(f"✅ Liquidated {currency} (${pos_info['usd_value']:.2f})")
        
        # Return updated free USD
        updated_portfolio = self.get_total_portfolio_value()
        return updated_portfolio['free_usd']
    
    def calculate_position_size(self, request: TradeRequest, current_balance: float) -> float:
        """Calculate optimal position size with confidence scaling"""
        base_size_pct = self.config.get('live_trading', {}).get('position_size_pct', 100.0) / 100.0
        
        # Apply confidence boost
        confidence_boost = 1.0
        high_confidence_boost = self.config.get('live_trading', {}).get('high_confidence_boost', 1.0)
        
        if request.confidence >= 0.85 and request.signal_strength >= 0.8:
            confidence_boost = high_confidence_boost
            self.logger.info(f"🚀 High confidence trade: {confidence_boost}x boost applied")
        
        # Calculate position size
        base_position = current_balance * base_size_pct
        scaled_position = base_position * confidence_boost
        
        # Apply security limits
        max_position = self.config.get('live_trading', {}).get('max_position_size', 50.0)
        final_position = min(scaled_position, max_position)
        
        self.logger.info(f"💰 Position sizing: Base=${base_position:.2f}, Scaled=${scaled_position:.2f}, Final=${final_position:.2f}")
        
        return final_position
    
    def execute_trade(self, request: TradeRequest) -> TradeResult:
        """Execute trade with safe position sizing based on available funds"""
        
        try:
            # Get current balance for logging
            current_balance = self.get_account_balance()
            self.logger.info(f"💰 Current balance: ${current_balance:.2f}")
            
            # Use safe order placement instead of old position sizing logic
            desired_usd = None
            if hasattr(request, 'confidence') and hasattr(request, 'signal_strength'):
                # Calculate desired USD amount based on confidence
                base_amount = BASE_TRADE_USD
                if request.confidence >= 0.85 and request.signal_strength >= 0.8:
                    high_confidence_boost = self.config.get('live_trading', {}).get('high_confidence_boost', 1.65)
                    desired_usd = base_amount * high_confidence_boost
                    self.logger.info(f"� High confidence trade: {high_confidence_boost}x boost applied")
                else:
                    desired_usd = base_amount
            
            # Place safe market order
            safe_result = place_market_order_safe(
                exchange=self.exchange,
                symbol=request.symbol,
                side=request.side.value,
                desired_usd=desired_usd,
                dry_run=False,
                logger=self.logger.info
            )
            
            # Handle safe order result
            if safe_result["status"] == "skip":
                self.logger.warning(f"🚫 Trade skipped: {safe_result['msg']}")
                return TradeResult(
                    success=False,
                    symbol=request.symbol,
                    error_message=f"Safe order placement skipped: {safe_result['msg']}"
                )
            
            elif safe_result["status"] == "error":
                self.logger.error(f"❌ Safe order placement failed: {safe_result['msg']}")
                return TradeResult(
                    success=False,
                    symbol=request.symbol,
                    error_message=f"Safe order placement error: {safe_result['msg']}"
                )
            
            elif safe_result["status"] == "ok":
                order = safe_result["order"]
                amount = safe_result["amount"]
                price = safe_result["price"]
                notional = safe_result["notional"]
                
                # Log successful trade with safe sizing details
                self.logger.info(f"✅ Safe trade executed: {request.symbol} | Amount: {amount:.6f} | Price: ${price:.4f} | Notional: ${notional:.2f}")
                
                # Store position info
                self.positions[order['id']] = {
                    'symbol': request.symbol,
                    'side': request.side.value,
                    'amount': amount,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'confidence': getattr(request, 'confidence', 0.0),
                    'signal_strength': getattr(request, 'signal_strength', 0.0)
                }
                
                # Create successful result
                result = TradeResult(
                    success=True,
                    order_id=order['id'],
                    symbol=request.symbol,
                    side=request.side.value,
                    amount=amount,
                    price=price,
                    fee=order.get('fee', {}).get('cost', 0.0) if order.get('fee') else 0.0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    raw_response=order
                )
                
                return result
            
            else:
                error_msg = f"Unknown safe order status: {safe_result['status']}"
                self.logger.error(f"⚠️ {error_msg}")
                return TradeResult(success=False, symbol=request.symbol, error_message=error_msg)
            
        except ccxt.InsufficientFunds as e:
            error_msg = f"Insufficient funds for {request.symbol}: {str(e)}"
            self.logger.error(f"💸 {error_msg}")
            return TradeResult(success=False, symbol=request.symbol, error_message=error_msg)
            
        except ccxt.InvalidOrder as e:
            error_msg = f"Invalid order for {request.symbol}: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return TradeResult(success=False, symbol=request.symbol, error_message=error_msg)
            
        except ccxt.NetworkError as e:
            error_msg = f"Network error during trade execution: {str(e)}"
            self.logger.error(f"🌐 {error_msg}")
            return TradeResult(success=False, symbol=request.symbol, error_message=error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error during trade execution: {str(e)}"
            self.logger.error(f"⚠️ {error_msg}")
            return TradeResult(success=False, symbol=request.symbol, error_message=error_msg)
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current market price for symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = float(ticker['last'])
            self.logger.debug(f"📈 Current price for {symbol}: ${price:.6f}")
            return price
        except Exception as e:
            self.logger.error(f"Error fetching price for {symbol}: {e}")
            raise ValueError(f"Could not get current price for {symbol}: {e}")
    
    def _validate_minimum_amount(self, symbol: str, amount: float) -> Tuple[bool, str]:
        """Validate minimum trading amount for symbol"""
        try:
            market = self.exchange.markets.get(symbol)
            if not market:
                return False, f"Market not found for {symbol}"
            
            min_amount = market.get('limits', {}).get('amount', {}).get('min', 0.0001)
            if amount < min_amount:
                return False, f"Amount {amount:.6f} below minimum {min_amount:.6f} for {symbol}"
            
            return True, "Amount validation passed"
            
        except Exception as e:
            self.logger.warning(f"Could not validate minimum amount for {symbol}: {e}")
            # If we can't validate, assume it's okay but log the issue
            return True, f"Amount validation skipped: {e}"
    
    def get_open_positions(self) -> Dict[str, Dict]:
        """Get all open positions"""
        return self.positions.copy()
    
    def close_position(self, order_id: str) -> TradeResult:
        """Close a specific position"""
        if order_id not in self.positions:
            return TradeResult(success=False, error_message=f"Position {order_id} not found")
        
        position = self.positions[order_id]
        
        # Create opposite order to close position
        close_request = TradeRequest(
            symbol=position['symbol'],
            side=OrderSide.SELL if position['side'] == 'buy' else OrderSide.BUY,
            amount=position['amount'],
            order_type=OrderType.MARKET
        )
        
        result = self.execute_trade(close_request)
        
        if result.success:
            # Remove from positions
            del self.positions[order_id]
            self.logger.info(f"🔒 Position closed: {order_id}")
        
        return result
    
    def emergency_stop(self) -> bool:
        """Emergency stop - close all positions"""
        self.logger.critical("🚨 EMERGENCY STOP ACTIVATED - CLOSING ALL POSITIONS")
        
        success_count = 0
        for order_id in list(self.positions.keys()):
            result = self.close_position(order_id)
            if result.success:
                success_count += 1
        
        self.logger.critical(f"🛑 Emergency stop completed: {success_count}/{len(self.positions)} positions closed")
        return success_count == len(self.positions)


def create_trade_executor(config_path: str = "config/config.yaml") -> TradeExecutor:
    """Factory function to create trade executor"""
    import yaml
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return TradeExecutor(config)


if __name__ == "__main__":
    # Example usage
    executor = create_trade_executor()
    
    # Test trade request
    test_request = TradeRequest(
        symbol="BTC/USD",
        side=OrderSide.BUY,
        amount=0.001,
        confidence=0.95,
        signal_strength=0.85
    )
    
    result = executor.execute_trade(test_request)
    print(f"Trade result: {result}")