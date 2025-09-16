#!/usr/bin/env python3
"""
Benson Bot - Profit Taking & Reinvestment Engine
Advanced profit management with dynamic scaling and reinvestment
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

class ProfitEngine:
    """
    Intelligent profit-taking and reinvestment system that:
    1. Takes profits based on confidence levels and position performance
    2. Implements trailing stops and partial profit taking
    3. Automatically reinvests profits with scaling position sizes
    4. Manages portfolio growth and compound returns
    """
    
    def __init__(self, initial_balance: float = 100.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.total_profits = 0.0
        self.withdrawn_profits = 0.0
        self.positions = {}  # Track open positions
        self.profit_history = []
        self.settings = self.load_profit_settings()
        self.logger = self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for profit engine"""
        logger = logging.getLogger('ProfitEngine')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('profit_engine.log')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def load_profit_settings(self) -> Dict:
        """Load profit taking and reinvestment configuration"""
        return {
            # Profit Taking Rules
            'profit_targets': {
                'low_confidence': 0.02,     # 2% profit for <75% confidence trades  
                'medium_confidence': 0.035, # 3.5% profit for 75-85% confidence
                'high_confidence': 0.05,    # 5% profit for 85-95% confidence
                'ultra_confidence': 0.08    # 8% profit for >95% confidence trades
            },
            'trailing_stop': {
                'enabled': True,
                'initial_stop': 0.015,      # 1.5% initial trailing stop
                'step_size': 0.005,         # Move stop up by 0.5% as profits grow
                'max_trailing': 0.04        # Maximum 4% trailing stop
            },
            'partial_profit_taking': {
                'enabled': True,
                'first_target': 0.025,      # Take 33% profit at 2.5% gain
                'second_target': 0.045,     # Take 50% profit at 4.5% gain
                'final_target': 0.08        # Take remaining at 8% gain
            },
            
            # Reinvestment Engine
            'reinvestment': {
                'compound_threshold': 0.10,  # Reinvest when profits reach 10% of balance
                'scaling_factor': 1.2,       # Increase position sizes by 20% when profits grow
                'max_position_scale': 2.0,   # Maximum 2x scaling from profits
                'profit_retention': 0.8      # Keep 80% of profits for reinvestment
            },
            
            # Portfolio Scaling
            'portfolio_scaling': {
                'enabled': True,
                'base_position_range': (0.01, 0.85),  # 1%-85% base range
                'profit_multiplier': 1.5,             # Scale positions by 1.5x with profits
                'max_scaled_position': 0.85,          # Never exceed 85% position
                'rebalance_frequency': 100             # Rebalance every 100 trades
            },
            
            # Profit Withdrawal
            'withdrawal': {
                'auto_withdraw': True,
                'withdraw_threshold': 0.25,   # Withdraw when profits > 25% of original balance
                'withdraw_percentage': 0.20,  # Withdraw 20% of excess profits
                'min_balance_ratio': 1.5      # Keep minimum 150% of original balance
            }
        }
    
    def calculate_profit_target(self, confidence: float, position_size: float) -> float:
        """Calculate dynamic profit target based on confidence and position size"""
        settings = self.settings['profit_targets']
        
        if confidence >= 95:
            base_target = settings['ultra_confidence']
        elif confidence >= 85:
            base_target = settings['high_confidence']  
        elif confidence >= 75:
            base_target = settings['medium_confidence']
        else:
            base_target = settings['low_confidence']
            
        # Scale target based on position size (larger positions = higher targets)
        position_multiplier = 1 + (position_size - 0.1) * 0.5  # Scale from position size
        
        return base_target * position_multiplier
    
    def should_take_profit(self, position: Dict, current_price: float) -> Tuple[bool, float, str]:
        """
        Determine if we should take profit on a position
        Returns: (should_exit, exit_percentage, reason)
        """
        entry_price = position['entry_price']
        position_size = position['size']
        confidence = position['confidence']
        current_return = (current_price - entry_price) / entry_price
        
        # Calculate profit target
        profit_target = self.calculate_profit_target(confidence, position_size)
        
        # Full profit taking logic
        if current_return >= profit_target:
            return True, 1.0, f"PROFIT TARGET HIT: {current_return:.2%} >= {profit_target:.2%}"
        
        # Partial profit taking
        partial_settings = self.settings['partial_profit_taking']
        if partial_settings['enabled']:
            if current_return >= partial_settings['final_target'] and not position.get('final_taken'):
                return True, 0.5, f"FINAL PARTIAL: {current_return:.2%} profit"
            elif current_return >= partial_settings['second_target'] and not position.get('second_taken'):
                position['second_taken'] = True
                return True, 0.5, f"SECOND PARTIAL: {current_return:.2%} profit"  
            elif current_return >= partial_settings['first_target'] and not position.get('first_taken'):
                position['first_taken'] = True
                return True, 0.33, f"FIRST PARTIAL: {current_return:.2%} profit"
        
        # Trailing stop logic
        trailing_settings = self.settings['trailing_stop']
        if trailing_settings['enabled']:
            if 'highest_price' not in position:
                position['highest_price'] = current_price
                position['trailing_stop'] = entry_price * (1 + trailing_settings['initial_stop'])
            
            # Update trailing stop
            if current_price > position['highest_price']:
                position['highest_price'] = current_price
                new_stop = current_price * (1 - min(
                    trailing_settings['max_trailing'],
                    trailing_settings['initial_stop'] + (current_return * 0.5)
                ))
                position['trailing_stop'] = max(position['trailing_stop'], new_stop)
            
            # Check if trailing stop hit
            if current_price <= position['trailing_stop']:
                return True, 1.0, f"TRAILING STOP: Price {current_price} <= Stop {position['trailing_stop']:.4f}"
        
        return False, 0.0, "HOLD"
    
    def calculate_scaled_position_size(self, base_confidence: float, base_signal_strength: float) -> float:
        """Calculate position size with profit-based scaling"""
        # Get base position size (from existing rapid_fire_trainer logic)
        base_position = self.calculate_base_position_size(base_confidence, base_signal_strength)
        
        scaling_settings = self.settings['portfolio_scaling']
        if not scaling_settings['enabled']:
            return base_position
        
        # Calculate scaling factor based on accumulated profits
        profit_ratio = self.total_profits / self.initial_balance
        scaling_multiplier = 1 + (profit_ratio * scaling_settings['profit_multiplier'])
        scaling_multiplier = min(scaling_multiplier, self.settings['reinvestment']['max_position_scale'])
        
        # Apply scaling
        scaled_position = base_position * scaling_multiplier
        
        # Ensure we don't exceed maximum scaled position
        max_scaled = scaling_settings['max_scaled_position']
        final_position = min(scaled_position, max_scaled)
        
        self.logger.info(f"Position Scaling: Base {base_position:.1%} -> Scaled {final_position:.1%} "
                        f"(Profit Ratio: {profit_ratio:.1%}, Multiplier: {scaling_multiplier:.2f})")
        
        return final_position
    
    def calculate_base_position_size(self, confidence: float, signal_strength: float) -> float:
        """Calculate base position size (integrates with rapid_fire_trainer logic)"""
        if confidence < 70 or signal_strength < 0.6:
            return 0.01  # 1% minimum for learning trades
        
        # Ultra-aggressive scaling for high-quality trades
        confidence_factor = (confidence - 70) / 30  # 0 to 1 scale for 70-100% confidence
        signal_factor = (signal_strength - 0.6) / 0.4  # 0 to 1 scale for 0.6-1.0 signal
        
        # Combined quality score
        quality_score = (confidence_factor + signal_factor) / 2
        
        # Ultra-quality boost for perfect setups
        if confidence >= 95 and signal_strength >= 0.8:
            quality_score *= 1.5  # 50% boost for perfect setups
            
        # Scale to 1%-85% range
        min_position, max_position = 0.01, 0.85
        position_size = min_position + (quality_score * (max_position - min_position))
        
        return min(position_size, max_position)
    
    def process_profit_reinvestment(self) -> bool:
        """Process automatic profit reinvestment"""
        reinvest_settings = self.settings['reinvestment']
        profit_threshold = self.initial_balance * reinvest_settings['compound_threshold']
        
        if self.total_profits < profit_threshold:
            return False
        
        # Calculate reinvestment amount
        available_profits = self.total_profits * reinvest_settings['profit_retention']
        
        # Add to current balance for larger positions
        old_balance = self.current_balance
        self.current_balance += available_profits
        
        # Mark profits as reinvested
        reinvested_amount = available_profits
        self.total_profits -= reinvested_amount
        
        self.logger.info(f"💰 PROFIT REINVESTMENT: ${reinvested_amount:.2f} reinvested. "
                        f"Balance: ${old_balance:.2f} -> ${self.current_balance:.2f}")
        
        # Log reinvestment event
        self.profit_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'reinvestment',
            'amount': reinvested_amount,
            'new_balance': self.current_balance,
            'total_profits': self.total_profits
        })
        
        return True
    
    def process_profit_withdrawal(self) -> float:
        """Process automatic profit withdrawal"""
        withdrawal_settings = self.settings['withdrawal']
        if not withdrawal_settings['auto_withdraw']:
            return 0.0
        
        # Check if we should withdraw
        min_balance = self.initial_balance * withdrawal_settings['min_balance_ratio']
        excess_balance = self.current_balance - min_balance
        
        if excess_balance <= 0:
            return 0.0
        
        # Calculate withdrawal amount
        withdrawal_amount = excess_balance * withdrawal_settings['withdraw_percentage']
        
        # Process withdrawal
        self.current_balance -= withdrawal_amount
        self.withdrawn_profits += withdrawal_amount
        
        self.logger.info(f"💸 PROFIT WITHDRAWAL: ${withdrawal_amount:.2f} withdrawn. "
                        f"Total Withdrawn: ${self.withdrawn_profits:.2f}")
        
        # Log withdrawal event
        self.profit_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'withdrawal',
            'amount': withdrawal_amount,
            'new_balance': self.current_balance,
            'total_withdrawn': self.withdrawn_profits
        })
        
        return withdrawal_amount
    
    def update_position_profit(self, symbol: str, current_price: float, 
                              original_position_value: float) -> Dict:
        """Update position profit tracking"""
        if symbol not in self.positions:
            return {'action': 'hold', 'message': 'Position not tracked'}
        
        position = self.positions[symbol]
        should_exit, exit_percentage, reason = self.should_take_profit(position, current_price)
        
        if should_exit:
            # Calculate profit
            entry_price = position['entry_price']
            profit_per_share = current_price - entry_price
            shares_to_exit = position['shares'] * exit_percentage
            profit_amount = profit_per_share * shares_to_exit
            
            # Update tracking
            self.total_profits += profit_amount
            if exit_percentage == 1.0:  # Full exit
                del self.positions[symbol]
            else:  # Partial exit
                position['shares'] -= shares_to_exit
            
            self.logger.info(f"💎 PROFIT TAKEN: {symbol} - ${profit_amount:.2f} profit "
                           f"({exit_percentage:.0%} exit) - {reason}")
            
            return {
                'action': 'exit',
                'exit_percentage': exit_percentage,
                'profit_amount': profit_amount,
                'reason': reason,
                'new_total_profits': self.total_profits
            }
        
        return {'action': 'hold', 'message': reason}
    
    def add_position(self, symbol: str, entry_price: float, shares: float, 
                    confidence: float, position_value: float):
        """Add a new position to tracking"""
        self.positions[symbol] = {
            'symbol': symbol,
            'entry_price': entry_price,
            'shares': shares,
            'confidence': confidence,
            'position_value': position_value,
            'entry_time': datetime.now().isoformat(),
            'first_taken': False,
            'second_taken': False,
            'final_taken': False
        }
        
        self.logger.info(f"📈 NEW POSITION: {symbol} @ ${entry_price:.4f} "
                        f"({shares:.4f} shares, {confidence:.1f}% confidence)")
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        total_position_value = sum(
            pos['shares'] * pos['entry_price'] for pos in self.positions.values()
        )
        
        total_return = (self.current_balance + total_position_value - self.initial_balance) / self.initial_balance
        
        return {
            'current_balance': self.current_balance,
            'total_profits': self.total_profits,
            'withdrawn_profits': self.withdrawn_profits,
            'open_positions': len(self.positions),
            'total_position_value': total_position_value,
            'total_portfolio_value': self.current_balance + total_position_value,
            'total_return_percentage': total_return * 100,
            'profit_scaling_active': self.total_profits > self.initial_balance * 0.1,
            'next_withdrawal_at': self.initial_balance * 1.25  # 25% profit threshold
        }
    
    def export_profit_report(self, filename: str = None) -> str:
        """Export detailed profit report"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"profit_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_summary': self.get_portfolio_summary(),
            'settings': self.settings,
            'profit_history': self.profit_history,
            'open_positions': self.positions
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📊 Profit report exported to: {filename}")
        return filename

def main():
    """Test the Profit Engine"""
    print("💰 BENSON BOT - PROFIT TAKING & REINVESTMENT ENGINE")
    print("=" * 60)
    
    # Initialize engine
    profit_engine = ProfitEngine(initial_balance=100.0)
    
    print("🔧 Configuration loaded:")
    summary = profit_engine.get_portfolio_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"   {key}: ${value:.2f}" if 'balance' in key or 'value' in key or 'profit' in key 
                  else f"   {key}: {value:.2f}%")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n📊 Base Position Sizing Examples:")
    test_scenarios = [
        (75, 0.65, "Ultra-high quality (meets criteria)"),
        (90, 0.8, "Near-perfect trade"),
        (99, 0.9, "Perfect maximum conviction trade")
    ]
    
    for confidence, signal, desc in test_scenarios:
        base_size = profit_engine.calculate_base_position_size(confidence, signal)
        scaled_size = profit_engine.calculate_scaled_position_size(confidence, signal)
        print(f"   {desc}: {base_size:.1%} -> {scaled_size:.1%} (with profit scaling)")
    
    print(f"\n💎 Profit Engine Ready for Integration!")
    
    # Export initial configuration
    report_file = profit_engine.export_profit_report("profit_engine_config.json")
    print(f"📄 Configuration saved to: {report_file}")

if __name__ == "__main__":
    main()