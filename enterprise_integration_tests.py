#!/usr/bin/env python3
"""
Enterprise Integration Test Suite
Comprehensive validation of Benson Bot enterprise-grade trading system
"""

import os
import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enterprise_portfolio_manager import EnterprisePortfolioManager, PortfolioHealthMetrics, TradingSessionMetrics
from benson_config_manager import BensonConfigManager
from trade_executor import TradeExecutor, TradeRequest, TradeResult, OrderSide

class TestEnterpriseIntegration(unittest.TestCase):
    """Enterprise-grade integration test suite"""
    
    def setUp(self):
        """Set up test environment with enterprise components"""
        self.config_manager = Mock(spec=BensonConfigManager)
        self.config_manager.get_config_for_trading.return_value = {
            'position_sizing': {
                'max_position_pct': 0.15,
                'risk_per_trade': 0.02
            },
            'risk_management': {
                'max_daily_loss_pct': 0.05,
                'max_positions': 5
            }
        }
        
        self.enterprise_portfolio = EnterprisePortfolioManager(self.config_manager)
        self.mock_trade_executor = Mock(spec=TradeExecutor)
    
    def test_health_metrics_calculation(self):
        """Test comprehensive health metrics calculation"""
        print("\n🏥 Testing enterprise health metrics...")
        
        # Mock the trade executor method that's called internally
        with patch.object(self.enterprise_portfolio, 'trade_executor') as mock_executor:
            mock_executor.get_total_portfolio_value.return_value = {
                'total_usd_value': 500.0,
                'free_usd': 50.0,
                'positions': {
                    'BTC': {'symbol': 'BTC', 'usd_value': 200.0},
                    'ETH': {'symbol': 'ETH', 'usd_value': 250.0},
                    'USD': 50.0
                }
            }
            
            health_metrics = self.enterprise_portfolio.get_health_metrics()
            
            # Validate health metrics structure
            self.assertIsInstance(health_metrics, PortfolioHealthMetrics)
            self.assertGreaterEqual(health_metrics.health_score, 0.0)
            self.assertLessEqual(health_metrics.health_score, 1.0)
            self.assertEqual(health_metrics.total_value, 500.0)
            
        print(f"✅ Health Score: {health_metrics.health_score:.2f}")
        print(f"✅ Total Balance: ${health_metrics.total_value:.2f}")
        print(f"✅ Free USD: ${health_metrics.free_usd:.2f}")
    
    def test_trading_readiness_assessment(self):
        """Test comprehensive trading readiness evaluation"""
        print("\n🎯 Testing trading readiness assessment...")
        
        # Mock healthy system state
        with patch.object(self.enterprise_portfolio, 'get_health_metrics') as mock_health:
            mock_health.return_value = PortfolioHealthMetrics(
                total_value=500.0,
                free_usd=50.0,
                allocated_value=450.0,
                utilization_pct=90.0,
                liquidation_capability=400.0,
                position_count=2,
                health_score=0.85,
                timestamp="2025-09-17T00:00:00Z"
            )
            
            readiness_report = self.enterprise_portfolio.get_trading_readiness_report()
            
            # Validate readiness report
            self.assertIsInstance(readiness_report, dict)
            self.assertIn('trading_ready', readiness_report)
            self.assertIn('health_metrics', readiness_report)
            self.assertIn('recommendations', readiness_report)
            
            # Should be ready with good health score
            self.assertTrue(readiness_report['trading_ready'])
            
        print(f"✅ Trading Ready: {readiness_report['trading_ready']}")
        print(f"✅ Health Score: {readiness_report['health_metrics'].health_score:.2f}")
        print(f"✅ Recommendations: {len(readiness_report.get('recommendations', []))}")
    
    def test_trade_execution_with_monitoring(self):
        """Test enterprise trade execution with comprehensive monitoring"""
        print("\n🚀 Testing enterprise trade execution...")
        
        # Create mock trade request
        trade_request = TradeRequest(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=0.01,
            confidence=0.75,
            signal_strength=0.65,
            metadata={"rsi": 25.5, "supply_chain_factor": 1.1}
        )
        
        # Mock successful trade result
        mock_result = TradeResult(
            success=True,
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=0.01,
            price=45000.0,
            order_id="test_order_123",
            timestamp=time.time(),
            error_message=None
        )
        
        # Mock enterprise trade execution
        with patch.object(self.enterprise_portfolio, 'execute_enterprise_trade') as mock_enterprise_trade:
            mock_enterprise_trade.return_value = {
                'success': True,
                'amount': 0.01,
                'price': 45000.0,
                'order_id': 'test_order_123'
            }
            
            # Mock health metrics for pre-trade check
            with patch.object(self.enterprise_portfolio, 'get_health_metrics') as mock_health:
                mock_health.return_value = PortfolioHealthMetrics(
                    total_value=500.0,
                    free_usd=50.0,
                    allocated_value=450.0,
                    utilization_pct=90.0,
                    liquidation_capability=400.0,
                    position_count=1,
                    health_score=0.85,
                    timestamp="2025-09-17T00:00:00Z"
                )
                
                result = self.enterprise_portfolio.execute_trade_with_monitoring(trade_request)
                
                # Validate execution result
                self.assertIsInstance(result, TradeResult)
                self.assertTrue(result.success)
                self.assertEqual(result.symbol, "BTC/USD")
                self.assertEqual(result.amount, 0.01)
        
        print(f"✅ Trade executed: {result.symbol} {result.side.value} ${result.amount * result.price:.2f}")
        print(f"✅ Order ID: {result.order_id}")
    
    def test_session_metrics_tracking(self):
        """Test comprehensive session metrics tracking"""
        print("\n📊 Testing session metrics tracking...")
        
        # Simulate multiple trades
        trade_results = [
            (True, "Successful trade 1"),
            (True, "Successful trade 2"),
            (False, "Failed trade 1"),
            (True, "Successful trade 3")
        ]
        
        # Mock session state
        with patch.object(self.enterprise_portfolio, '_load_session_data') as mock_load:
            mock_load.return_value = {
                'session_id': 'test-session',
                'start_time': '2025-09-17T00:00:00Z',
                'total_signals': 10,
                'successful_trades': 3,
                'failed_trades': 1,
                'avoided_trades': 2,
                'total_volume': 1500.0,
                'portfolio_change': 25.0,
                'performance_score': 0.72
            }
            
            session_metrics = self.enterprise_portfolio.get_session_metrics()
            
            # Validate session metrics
            self.assertIsInstance(session_metrics, TradingSessionMetrics)
            self.assertEqual(session_metrics.successful_trades, 3)
            self.assertEqual(session_metrics.failed_trades, 1)
            self.assertEqual(session_metrics.total_volume, 1500.0)
        
        print(f"✅ Successful Trades: {session_metrics.successful_trades}")
        print(f"✅ Failed Trades: {session_metrics.failed_trades}")
        print(f"✅ Total Volume: ${session_metrics.total_volume:.2f}")
    
    def test_error_handling_resilience(self):
        """Test enterprise-grade error handling and resilience"""
        print("\n🛡️ Testing error handling resilience...")
        
        # Test trade execution error handling
        trade_request = TradeRequest(
            symbol="ETH/USD",
            side=OrderSide.BUY,
            amount=0.5,
            confidence=0.60,
            signal_strength=0.55
        )
        
        # Simulate various error conditions
        test_errors = [
            Exception("Network timeout"),
            Exception("Insufficient funds"),
            Exception("Order rejection"),
            Exception("API rate limit exceeded")
        ]
        
        for error in test_errors:
            try:
                self.enterprise_portfolio.handle_trade_error(error, trade_request)
                print(f"✅ Handled error: {type(error).__name__}: {error}")
            except Exception as e:
                self.fail(f"Error handling failed for {type(error).__name__}: {e}")
    
    def test_comprehensive_system_integration(self):
        """Test full system integration with all components"""
        print("\n🔄 Testing comprehensive system integration...")
        
        # Mock all external dependencies
        with patch('trade_executor.create_trade_executor') as mock_create_executor, \
             patch('portfolio_manager.PortfolioManager') as mock_portfolio_manager:
            
            # Setup mocks
            mock_executor = Mock()
            mock_executor.get_total_portfolio_value.return_value = {
                'total_usd_value': 500.0,
                'free_usd': 50.0
            }
            mock_create_executor.return_value = mock_executor
            
            mock_pm = Mock()
            mock_pm.get_open_positions.return_value = []
            mock_portfolio_manager.return_value = mock_pm
            
            # Test initialization workflow
            try:
                # This would be called from main bot
                config_manager = BensonConfigManager()
                enterprise_portfolio = EnterprisePortfolioManager(config_manager)
                
                # Verify initialization
                self.assertIsNotNone(enterprise_portfolio)
                
                # Test readiness check
                readiness = enterprise_portfolio.get_trading_readiness_report()
                self.assertIsInstance(readiness, dict)
                
                print("✅ System initialization successful")
                print("✅ Enterprise portfolio manager active")
                print("✅ Health monitoring operational")
                
            except Exception as e:
                self.fail(f"System integration test failed: {e}")
    
    def test_performance_benchmarks(self):
        """Test system performance under load"""
        print("\n⚡ Testing performance benchmarks...")
        
        # Test health metrics calculation performance
        start_time = time.time()
        
        # Mock the trade executor for performance testing
        with patch.object(self.enterprise_portfolio, 'trade_executor') as mock_executor:
            mock_executor.get_total_portfolio_value.return_value = {
                'total_usd_value': 500.0,
                'free_usd': 50.0,
                'positions': {'USD': 50.0}
            }
            
            for i in range(100):
                health_metrics = self.enterprise_portfolio.get_health_metrics()
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        print(f"✅ Health metrics calculation: {avg_time*1000:.2f}ms average")
        
        # Performance should be under 100ms per calculation (relaxed for testing)
        self.assertLess(avg_time, 0.1)
        
        print("✅ Performance benchmarks passed")

def run_enterprise_tests():
    """Run comprehensive enterprise integration tests"""
    print("🏭 ENTERPRISE INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEnterpriseIntegration)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎯 ENTERPRISE TEST SUMMARY")
    print(f"   Tests Run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ ALL ENTERPRISE TESTS PASSED")
        print("🚀 System ready for production deployment")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Review failures before production deployment")
        return False

if __name__ == "__main__":
    success = run_enterprise_tests()
    sys.exit(0 if success else 1)