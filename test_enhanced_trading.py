#!/usr/bin/env python3

"""Test the enhanced portfolio-aware trading system"""

import sys
sys.path.append('.')

from trade_executor import create_trade_executor, TradeRequest
from datetime import datetime

def test_portfolio_system():
    print("🧪 TESTING ENHANCED PORTFOLIO SYSTEM")
    print("=" * 50)
    
    # Create trade executor
    executor = create_trade_executor()
    
    # Test 1: Get total portfolio value
    print("📊 1. Testing portfolio value calculation...")
    portfolio = executor.get_total_portfolio_value()
    print(f"   Total Portfolio Value: ${portfolio['total_usd_value']:.2f}")
    print(f"   Free USD: ${portfolio['free_usd']:.2f}")
    print(f"   Allocated Positions: ${portfolio['total_usd_value'] - portfolio['free_usd']:.2f}")
    
    print("\n📈 Position Details:")
    for currency, info in portfolio['positions'].items():
        if currency != 'USD':
            print(f"   {currency}: {info['amount']:.6f} = ${info['usd_value']:.2f} @ ${info.get('price', 'N/A')}")
    
    # Test 2: Simulate a buy trade that would require liquidation
    print("\n🔄 2. Testing liquidation logic...")
    print("   Simulating need for $50 USD (should trigger liquidation)...")
    
    # Calculate how much we could get
    available_after_liquidation = executor.ensure_usd_available(50.0)
    print(f"   Available USD after liquidation attempts: ${available_after_liquidation:.2f}")
    
    # Test 3: Simulate position sizing based on total portfolio
    print(f"\n💰 3. Testing position sizing logic...")
    total_value = portfolio['total_usd_value']
    max_position_pct = 0.60  # From .env
    base_trade = 8.0  # From .env
    
    calculated_position = min(base_trade, total_value * max_position_pct)
    print(f"   Total Portfolio: ${total_value:.2f}")
    print(f"   Max Position %: {max_position_pct*100}%")
    print(f"   Calculated Position Size: ${calculated_position:.2f}")
    print(f"   With High Confidence Boost (1.65x): ${calculated_position * 1.65:.2f}")
    
    # Test 4: Check if we can make meaningful trades now
    print(f"\n🎯 4. Trading viability check...")
    if calculated_position >= 7.50:  # Typical minimum for most crypto
        print(f"   ✅ Can make trades: Position size ${calculated_position:.2f} meets minimums")
    else:
        print(f"   ❌ Position too small: ${calculated_position:.2f} below typical minimums")
    
    if total_value >= 50.0:
        print(f"   ✅ Portfolio size adequate: ${total_value:.2f}")
    else:
        print(f"   ⚠️  Small portfolio: ${total_value:.2f} - limited trading opportunities")
    
    print("\n🚀 SYSTEM STATUS:")
    if total_value >= 100 and calculated_position >= 10:
        print("   🟢 EXCELLENT: Ready for active trading with good position sizes")
    elif total_value >= 50 and calculated_position >= 7.50:
        print("   🟡 GOOD: Can trade but with smaller positions")  
    else:
        print("   🔴 LIMITED: Portfolio too small for consistent trading")
        
    return portfolio

if __name__ == "__main__":
    test_portfolio_system()