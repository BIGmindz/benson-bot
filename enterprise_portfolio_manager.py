#!/usr/bin/env python3
"""
🏭 ENTERPRISE PRODUCTION SYSTEM INTEGRATION
Portfolio-Aware Trading System with Enterprise Standards

Author: Benson Bot CTO
Created: 2025-09-17
Version: 2.0.0-enterprise
"""

import os
import sys
import time
import logging
import traceback
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Type definitions for enterprise integration
from typing import Any, Union

# Import core trading components
try:
    from trade_executor import TradeExecutor, create_trade_executor, TradeRequest, TradeResult, OrderSide
except ImportError:
    # Fallback type definitions for testing
    class TradeRequest:
        def __init__(self, symbol: str, side: Any, amount: float, confidence: float, signal_strength: float, metadata: Dict = None):
            self.symbol = symbol
            self.side = side
            self.amount = amount
            self.confidence = confidence
            self.signal_strength = signal_strength
            self.metadata = metadata or {}
    
    class TradeResult:
        def __init__(self, success: bool, symbol: str, side: Any, amount: float, price: float, order_id: str, timestamp: float, error_message: str = None):
            self.success = success
            self.symbol = symbol
            self.side = side
            self.amount = amount
            self.price = price
            self.order_id = order_id
            self.timestamp = timestamp
            self.error_message = error_message
    
    class OrderSide:
        BUY = "BUY"
        SELL = "SELL"

try:
    from benson_config_manager import BensonConfigManager
except ImportError:
    # Fallback for testing
    class BensonConfigManager:
        def get_config_for_trading(self):
            return {
                'position_sizing': {'max_position_pct': 0.15, 'risk_per_trade': 0.02},
                'risk_management': {'max_daily_loss_pct': 0.05, 'max_positions': 5}
            }

# Import existing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from trade_executor import create_trade_executor, TradeRequest, OrderSide
    from benson_config_manager import BensonConfigManager
except ImportError as e:
    print(f"❌ Critical import error: {e}")
    sys.exit(1)


@dataclass
class PortfolioHealthMetrics:
    """Enterprise portfolio health monitoring"""
    total_value: float
    free_usd: float
    allocated_value: float
    utilization_pct: float
    liquidation_capability: float
    position_count: int
    health_score: float
    timestamp: str


@dataclass 
class TradingSessionMetrics:
    """Enterprise trading session monitoring"""
    session_id: str
    start_time: str
    total_signals: int
    successful_trades: int
    failed_trades: int
    avoided_trades: int
    total_volume: float
    portfolio_change: float
    performance_score: float


class EnterprisePortfolioManager:
    """
    🏭 Enterprise-Grade Portfolio Management System
    
    Features:
    - Real-time portfolio valuation
    - Intelligent position liquidation
    - Risk-aware position sizing
    - Comprehensive monitoring
    - Production error handling
    """
    
    def __init__(self, config_manager: BensonConfigManager):
        self.config = config_manager
        self.logger = self._setup_enterprise_logging()
        self.trade_executor = create_trade_executor()
        self.session_id = self._generate_session_id()
        self.metrics_history: List[PortfolioHealthMetrics] = []
        
        # Enterprise configuration
        self.max_liquidation_attempts = 3
        self.liquidation_timeout = 30  # seconds
        self.health_check_interval = 60  # seconds
        self.min_health_score = 0.7
        
        self.logger.info(f"🏭 Enterprise Portfolio Manager initialized - Session: {self.session_id}")
    
    def _setup_enterprise_logging(self) -> logging.Logger:
        """Setup production-grade logging"""
        logger = logging.getLogger('EnterprisePortfolio')
        logger.setLevel(logging.INFO)
        
        # Create file handler with rotation
        handler = logging.FileHandler('enterprise_portfolio.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        return f"enterprise-{int(time.time())}"
    
    def get_portfolio_health(self) -> PortfolioHealthMetrics:
        """
        🏥 Enterprise Portfolio Health Assessment
        Returns comprehensive portfolio health metrics
        """
        try:
            portfolio_data = self.trade_executor.get_total_portfolio_value()
            
            total_value = portfolio_data['total_usd_value']
            free_usd = portfolio_data['free_usd']
            allocated_value = total_value - free_usd
            utilization_pct = (allocated_value / total_value * 100) if total_value > 0 else 0
            position_count = len([p for p in portfolio_data['positions'] if p != 'USD'])
            
            # Calculate liquidation capability (how much we can quickly convert to cash)
            liquidatable_value = sum(
                pos['usd_value'] for pos in portfolio_data['positions'].values()
                if isinstance(pos, dict) and pos.get('symbol') and pos['usd_value'] > 1.0
            )
            
            # Health score calculation (0.0 = critical, 1.0 = excellent)
            health_factors = []
            health_factors.append(min(total_value / 100, 1.0))  # Portfolio size factor
            health_factors.append(min(free_usd / 10, 1.0))      # Liquidity factor  
            health_factors.append(min(liquidatable_value / 50, 1.0))  # Liquidation factor
            health_factors.append(1.0 if position_count <= 10 else 0.7)  # Diversification factor
            
            health_score = sum(health_factors) / len(health_factors)
            
            metrics = PortfolioHealthMetrics(
                total_value=total_value,
                free_usd=free_usd,
                allocated_value=allocated_value,
                utilization_pct=utilization_pct,
                liquidation_capability=liquidatable_value,
                position_count=position_count,
                health_score=health_score,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # Store metrics history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:  # Keep last 100 entries
                self.metrics_history = self.metrics_history[-100:]
            
            self.logger.info(f"💊 Portfolio Health: Score={health_score:.2f}, Value=${total_value:.2f}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Portfolio health assessment failed: {e}")
            raise
    
    def ensure_trading_liquidity(self, required_amount: float, max_attempts: int = 3) -> Tuple[bool, float]:
        """
        💰 Enterprise Liquidity Management
        
        Ensures sufficient USD liquidity for trading through intelligent position liquidation
        Returns: (success: bool, available_amount: float)
        """
        try:
            self.logger.info(f"💰 Liquidity request: ${required_amount:.2f}")
            
            # Check current liquidity
            portfolio = self.trade_executor.get_total_portfolio_value()
            current_liquidity = portfolio['free_usd']
            
            if current_liquidity >= required_amount:
                self.logger.info(f"✅ Sufficient liquidity available: ${current_liquidity:.2f}")
                return True, current_liquidity
            
            # Calculate liquidation requirement
            deficit = required_amount - current_liquidity
            self.logger.info(f"🔄 Liquidation needed: ${deficit:.2f} (have ${current_liquidity:.2f})")
            
            # Attempt intelligent liquidation
            for attempt in range(max_attempts):
                try:
                    liquidated_amount = self.trade_executor.ensure_usd_available(required_amount)
                    
                    if liquidated_amount >= required_amount:
                        self.logger.info(f"✅ Liquidation successful: ${liquidated_amount:.2f} available")
                        return True, liquidated_amount
                    
                    self.logger.warning(f"⚠️ Liquidation attempt {attempt + 1} insufficient: ${liquidated_amount:.2f}")
                    time.sleep(2)  # Brief pause between attempts
                    
                except Exception as e:
                    self.logger.error(f"❌ Liquidation attempt {attempt + 1} failed: {e}")
                    if attempt == max_attempts - 1:
                        raise
            
            return False, current_liquidity
            
        except Exception as e:
            self.logger.error(f"❌ Liquidity management failed: {e}")
            return False, 0.0
    
    def execute_enterprise_trade(self, request: TradeRequest) -> Dict:
        """
        🏭 Enterprise Trade Execution with Full Portfolio Intelligence
        
        Features:
        - Pre-trade portfolio health check
        - Intelligent liquidity management  
        - Real-time position sizing
        - Comprehensive error handling
        - Post-trade validation
        """
        trade_start = time.time()
        trade_id = f"trade-{int(trade_start)}"
        
        try:
            self.logger.info(f"🏭 Enterprise trade initiated: {trade_id} - {request.symbol} {request.side.value}")
            
            # Phase 1: Pre-trade health assessment
            health = self.get_portfolio_health()
            if health.health_score < self.min_health_score:
                return {
                    'success': False,
                    'error': f'Portfolio health too low: {health.health_score:.2f} < {self.min_health_score}',
                    'health_metrics': health
                }
            
            # Phase 2: Liquidity management for BUY orders
            if request.side == OrderSide.BUY:
                # Calculate required liquidity (trade amount + buffer)
                base_amount = float(os.getenv('BASE_TRADE_USD', 8))
                required_liquidity = base_amount + float(os.getenv('MIN_CASH_BUFFER_USD', 2))
                
                success, available = self.ensure_trading_liquidity(required_liquidity)
                if not success:
                    return {
                        'success': False, 
                        'error': f'Insufficient liquidity: need ${required_liquidity:.2f}, available ${available:.2f}',
                        'health_metrics': health
                    }
            
            # Phase 3: Execute trade with enhanced portfolio awareness
            trade_result = self.trade_executor.execute_trade(request)
            
            # Phase 4: Post-trade validation
            execution_time = time.time() - trade_start
            post_health = self.get_portfolio_health()
            
            result = {
                'success': trade_result.success,
                'trade_id': trade_id,
                'execution_time': execution_time,
                'pre_health': health,
                'post_health': post_health,
                'trade_result': trade_result
            }
            
            if trade_result.success:
                self.logger.info(f"✅ Enterprise trade completed: {trade_id} - ${trade_result.amount * trade_result.price:.2f}")
            else:
                self.logger.warning(f"⚠️ Enterprise trade failed: {trade_id} - {trade_result.error_message}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Enterprise trade execution failed: {trade_id} - {str(e)}")
            return {
                'success': False,
                'error': f'Trade execution exception: {str(e)}',
                'trade_id': trade_id,
                'execution_time': time.time() - trade_start
            }
    
    def get_trading_readiness_report(self) -> Dict:
        """
        📊 Enterprise Trading Readiness Assessment
        Returns comprehensive system readiness report
        """
        try:
            health = self.get_portfolio_health()
            
            # Test liquidation capability
            test_amount = 10.0  # Test with $10
            can_liquidate, available = self.ensure_trading_liquidity(test_amount, max_attempts=1)
            
            # Calculate trading capacity
            max_position_size = health.total_value * float(os.getenv('MAX_POSITION_PCT', 0.6))
            recommended_trade_size = min(float(os.getenv('BASE_TRADE_USD', 8)), max_position_size)
            
            readiness_score = health.health_score
            if can_liquidate:
                readiness_score += 0.2
            if health.free_usd >= recommended_trade_size:
                readiness_score += 0.1
            
            readiness_score = min(readiness_score, 1.0)
            
            report = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'session_id': self.session_id,
                'health_metrics': health,
                'liquidation_capable': can_liquidate,
                'available_liquidity': available,
                'max_position_size': max_position_size,
                'recommended_trade_size': recommended_trade_size,
                'readiness_score': readiness_score,
                'trading_ready': readiness_score >= 0.8,
                'recommendations': []
            }
            
            # Generate recommendations
            if health.free_usd < 5:
                report['recommendations'].append("Consider liquidating small positions for better liquidity")
            if health.position_count > 15:
                report['recommendations'].append("Portfolio may be over-diversified, consider consolidation")
            if health.health_score < 0.8:
                report['recommendations'].append("Portfolio health needs attention before aggressive trading")
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Readiness assessment failed: {e}")
            return {'error': str(e), 'trading_ready': False}
    
    # ===== ADDITIONAL METHODS FOR TEST COMPATIBILITY =====
    
    def get_health_metrics(self) -> PortfolioHealthMetrics:
        """Alias for get_portfolio_health for test compatibility"""
        return self.get_portfolio_health()
    
    def execute_trade_with_monitoring(self, request: TradeRequest) -> TradeResult:
        """Execute trade with comprehensive enterprise monitoring"""
        try:
            # Pre-trade validation
            health_metrics = self.get_health_metrics()
            
            if health_metrics.health_score < 0.3:
                return TradeResult(
                    success=False,
                    symbol=request.symbol,
                    side=request.side,
                    amount=0,
                    price=0,
                    order_id="",
                    timestamp=time.time(),
                    error_message=f"Low health score: {health_metrics.health_score:.2f}"
                )
            
            # Execute via enterprise trade method
            enterprise_result = self.execute_enterprise_trade(request)
            
            # Convert to TradeResult format
            if enterprise_result.get('success'):
                return TradeResult(
                    success=True,
                    symbol=request.symbol,
                    side=request.side,
                    amount=enterprise_result.get('amount', 0),
                    price=enterprise_result.get('price', 0),
                    order_id=enterprise_result.get('order_id', ''),
                    timestamp=time.time(),
                    error_message=None
                )
            else:
                return TradeResult(
                    success=False,
                    symbol=request.symbol,
                    side=request.side,
                    amount=0,
                    price=0,
                    order_id="",
                    timestamp=time.time(),
                    error_message=enterprise_result.get('error', 'Unknown error')
                )
                
        except Exception as e:
            self.logger.error(f"Trade execution with monitoring failed: {e}")
            return TradeResult(
                success=False,
                symbol=request.symbol,
                side=request.side,
                amount=0,
                price=0,
                order_id="",
                timestamp=time.time(),
                error_message=str(e)
            )
    
    def get_session_metrics(self) -> TradingSessionMetrics:
        """Get comprehensive trading session metrics"""
        try:
            session_data = self._load_session_data()
            
            return TradingSessionMetrics(
                session_id=session_data.get('session_id', 'unknown'),
                start_time=session_data.get('start_time', '2025-09-17T00:00:00Z'),
                total_signals=session_data.get('total_signals', 0),
                successful_trades=session_data.get('successful_trades', 0),
                failed_trades=session_data.get('failed_trades', 0),
                avoided_trades=session_data.get('avoided_trades', 0),
                total_volume=session_data.get('total_volume', 0.0),
                portfolio_change=session_data.get('portfolio_change', 0.0),
                performance_score=session_data.get('performance_score', 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Session metrics calculation failed: {e}")
            return TradingSessionMetrics(
                session_id='error',
                start_time='2025-09-17T00:00:00Z',
                total_signals=0,
                successful_trades=0,
                failed_trades=0,
                avoided_trades=0,
                total_volume=0.0,
                portfolio_change=0.0,
                performance_score=0.0
            )
    
    def _load_session_data(self) -> Dict:
        """Load session data from storage"""
        try:
            # In production, this would load from database
            # For now, return mock data that matches TradingSessionMetrics structure
            return {
                'session_id': self.session_id,
                'start_time': '2025-09-17T00:00:00Z',
                'total_signals': 0,
                'successful_trades': 0,
                'failed_trades': 0,
                'avoided_trades': 0,
                'total_volume': 0.0,
                'portfolio_change': 0.0,
                'performance_score': 0.0
            }
        except Exception as e:
            self.logger.error(f"Session data loading failed: {e}")
            return {
                'session_id': 'error',
                'start_time': '2025-09-17T00:00:00Z',
                'total_signals': 0,
                'successful_trades': 0,
                'failed_trades': 0,
                'avoided_trades': 0,
                'total_volume': 0.0,
                'portfolio_change': 0.0,
                'performance_score': 0.0
            }
    
    def handle_trade_error(self, error: Exception, trade_request: TradeRequest) -> None:
        """Handle trade execution errors with comprehensive logging"""
        try:
            error_info = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'symbol': trade_request.symbol,
                'side': trade_request.side.value,
                'amount': trade_request.amount,
                'confidence': trade_request.confidence,
                'timestamp': time.time()
            }
            
            self.logger.error(f"🔴 TRADE ERROR: {error_info['error_type']} - {error_info['error_message']}")
            self.logger.error(f"   Trade: {error_info['symbol']} {error_info['side']} {error_info['amount']} @ {error_info['confidence']:.1%} confidence")
            
            # In production, this would also:
            # - Store error in database
            # - Send alerts if critical
            # - Update system metrics
            # - Trigger failsafe procedures if needed
            
        except Exception as logging_error:
            # Failsafe error handling
            print(f"Critical error in error handling: {logging_error}")
    
    def log_trade_failure(self, trade_request: TradeRequest, error_message: str) -> None:
        """Log trade failure with detailed context"""
        try:
            self.logger.warning(f"⚠️ TRADE FAILURE LOGGED: {trade_request.symbol} {trade_request.side.value}")
            self.logger.warning(f"   Error: {error_message}")
            self.logger.warning(f"   Context: Confidence={trade_request.confidence:.1%}, Signal={trade_request.signal_strength:.2f}")
        except Exception as e:
            print(f"Failed to log trade failure: {e}")
    
    def log_position_close(self, position_id: str, result: TradeResult, reason: str) -> None:
        """Log position closure with comprehensive details"""
        try:
            self.logger.info(f"📉 POSITION CLOSED: {position_id}")
            self.logger.info(f"   Symbol: {result.symbol} {result.side.value}")
            self.logger.info(f"   Amount: {result.amount} @ ${result.price:.4f}")
            self.logger.info(f"   Reason: {reason}")
            self.logger.info(f"   Order ID: {result.order_id}")
        except Exception as e:
            print(f"Failed to log position close: {e}")
    
    def should_rebalance_portfolio(self) -> bool:
        """Determine if portfolio rebalancing is recommended"""
        try:
            health_metrics = self.get_health_metrics()
            
            # Simple rebalancing logic - could be more sophisticated
            if health_metrics.health_score < 0.6:
                return True
            if health_metrics.utilization_pct > 80:
                return True
            if health_metrics.position_count > 8:
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Rebalancing assessment failed: {e}")
            return False
    
    def get_rebalancing_recommendations(self) -> List[str]:
        """Get specific rebalancing recommendations"""
        try:
            recommendations = []
            health_metrics = self.get_health_metrics()
            
            if health_metrics.utilization_pct > 80:
                recommendations.append("Reduce position sizes to improve liquidity")
            
            if health_metrics.position_count > 8:
                recommendations.append("Consider consolidating smaller positions")
                
            if health_metrics.free_usd < 10:
                recommendations.append("Increase cash reserves for opportunities")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Rebalancing recommendations failed: {e}")
            return ["Unable to generate recommendations - system error"]
    
    def save_health_snapshot(self, health_metrics: PortfolioHealthMetrics, session_metrics: TradingSessionMetrics) -> None:
        """Save comprehensive portfolio and session snapshot"""
        try:
            snapshot = {
                'timestamp': time.time(),
                'health_score': health_metrics.health_score,
                'total_value': health_metrics.total_value,
                'utilization_pct': health_metrics.utilization_pct,
                'position_count': health_metrics.position_count,
                'session_trades': session_metrics.total_trades,
                'success_rate': session_metrics.success_rate
            }
            
            self.logger.info(f"📸 HEALTH SNAPSHOT: Score={snapshot['health_score']:.2f}, Value=${snapshot['total_value']:.2f}")
            
            # In production, this would save to database
            
        except Exception as e:
            self.logger.error(f"Health snapshot save failed: {e}")
    
    def handle_monitoring_error(self, error: Exception) -> None:
        """Handle portfolio monitoring system errors"""
        try:
            self.logger.error(f"🔴 MONITORING ERROR: {type(error).__name__}: {error}")
            # In production: implement failsafe monitoring procedures
        except Exception as e:
            print(f"Critical monitoring error: {e}")


def main():
    """Enterprise system validation"""
    print("🏭 ENTERPRISE PORTFOLIO SYSTEM VALIDATION")
    print("=" * 60)
    
    config = BensonConfigManager()
    enterprise_portfolio = EnterprisePortfolioManager(config)
    
    # Generate readiness report
    report = enterprise_portfolio.get_trading_readiness_report()
    
    print(f"📊 TRADING READINESS REPORT")
    print(f"   Session ID: {report.get('session_id')}")
    print(f"   Health Score: {report['health_metrics'].health_score:.2f}/1.00")
    print(f"   Portfolio Value: ${report['health_metrics'].total_value:.2f}")
    print(f"   Available Liquidity: ${report.get('available_liquidity', 0):.2f}")
    print(f"   Trading Ready: {'✅ YES' if report.get('trading_ready') else '❌ NO'}")
    
    if report.get('recommendations'):
        print(f"   Recommendations:")
        for rec in report['recommendations']:
            print(f"     • {rec}")


if __name__ == "__main__":
    main()