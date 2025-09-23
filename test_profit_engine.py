
import unittest
import time
from datetime import datetime, timedelta
from profit_engine import ProfitEngine

class TestProfitEngine(unittest.TestCase):

    def setUp(self):
        """Set up a fresh ProfitEngine for each test."""
        # Use a dummy config for predictable test results
        self.config = {
            "dynamic_profit_target": {"enabled": True, "base_percentage": 1.2},
            "trailing_stop_loss": {"enabled": True, "percentage": 1.8},
            "time_based_exit": {"enabled": True, "max_hold_minutes": 25}
        }
        self.engine = ProfitEngine()
        self.engine.config = self.config # Override with test config

    def test_profit_target_hit(self):
        """Test that a SELL decision is made when the profit target is reached."""
        print("\n--- Testing Scenario 1: Profit Target ---")
        position = {
            'symbol': 'BTC/USD',
            'avg_price': 50000,
            'quantity': 0.1,
            'timestamp': time.time()
        }
        # Price increases by 1.5% ( > 1.2% target)
        current_price = 50000 * 1.015
        decision, reason = self.engine.get_decision(position, current_price)
        print(f"Decision: {decision}, Reason: {reason}")
        self.assertEqual(decision, 'sell')
        self.assertEqual(reason, 'profit_target_hit')

    def test_stop_loss_triggered(self):
        """Test that a SELL decision is made when the stop-loss is triggered."""
        print("\n--- Testing Scenario 2: Stop-Loss ---")
        position = {
            'symbol': 'ETH/USD',
            'avg_price': 4000,
            'quantity': 1,
            'timestamp': time.time()
        }
        # Price drops by 2% ( > 1.8% stop-loss)
        current_price = 4000 * (1 - 0.02)
        decision, reason = self.engine.get_decision(position, current_price)
        print(f"Decision: {decision}, Reason: {reason}")
        self.assertEqual(decision, 'sell')
        self.assertEqual(reason, 'stop_loss_triggered')

    def test_time_based_exit(self):
        """Test that a SELL decision is made when the max hold time is exceeded."""
        print("\n--- Testing Scenario 3: Time-Based Exit ---")
        # Position opened 30 minutes ago ( > 25 min limit)
        old_timestamp = (datetime.now() - timedelta(minutes=30)).timestamp()
        position = {
            'symbol': 'SOL/USD',
            'avg_price': 150,
            'quantity': 10,
            'timestamp': old_timestamp
        }
        # Price is neutral
        current_price = 150
        decision, reason = self.engine.get_decision(position, current_price)
        print(f"Decision: {decision}, Reason: {reason}")
        self.assertEqual(decision, 'sell')
        self.assertEqual(reason, 'time_based_exit')

    def test_hold_decision(self):
        """Test that a HOLD decision is made when no exit criteria are met."""
        print("\n--- Testing Scenario 4: Hold ---")
        position = {
            'symbol': 'ADA/USD',
            'avg_price': 2.00,
            'quantity': 1000,
            'timestamp': time.time()
        }
        # Price increases by 0.5% (less than profit target and not a loss)
        current_price = 2.00 * 1.005
        decision, reason = self.engine.get_decision(position, current_price)
        print(f"Decision: {decision}, Reason: {reason}")
        self.assertEqual(decision, 'hold')
        self.assertIsNone(reason)

if __name__ == '__main__':
    print("🚀 **Testing the New Profit Engine** 🚀")
    unittest.main()
