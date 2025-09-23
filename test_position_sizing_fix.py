#!/usr/bin/env python3
"""
🧪 TEST NEW POSITION SIZING
Verify that positions are now 20% of balance, not 100%
"""

import yaml
from trade_executor import create_trade_executor, TradeRequest, OrderSide

def test_new_position_sizing():
    """Test the corrected position sizing"""
    
    print("🧪 TESTING NEW POSITION SIZING")
    print("=" * 50)
    
    try:
        # Load config to show the changes
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            
        live_config = config.get('live_trading', {})
        print("📋 NEW CONFIGURATION:")
        print(f"   Max Position Size: ${live_config.get('max_position_size', 0):.2f}")
        print(f"   Position Size %: {live_config.get('position_size_pct', 0):.1f}%")
        print(f"   Max Positions: {live_config.get('max_positions', 0)}")
        print(f"   Symbols: {len(config.get('symbols', []))}")
        
        # Test trade executor with the MAIN config file
        trade_executor = create_trade_executor("config/config.yaml")  # Use main config!
        current_balance = trade_executor.get_account_balance()
        
        print(f"\n💰 Current Balance: ${current_balance:.2f}")
        
        # Create test trade request
        test_request = TradeRequest(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=0.0,  # Auto-calculate
            confidence=0.65,
            signal_strength=0.55,
            metadata={"test": "position_sizing"}
        )
        
        # Calculate what the position size would be
        position_value = trade_executor.calculate_position_size(test_request, current_balance)
        
        print(f"\n🎯 POSITION SIZE TEST:")
        print(f"   Test Confidence: {test_request.confidence}")
        print(f"   Test Signal Strength: {test_request.signal_strength}")
        print(f"   Calculated Position: ${position_value:.2f}")
        print(f"   Percentage of Balance: {(position_value/current_balance)*100:.1f}%")
        
        # Check if it's reasonable (should be around 20% or less)
        expected_max = current_balance * 0.25  # 25% max
        
        if position_value <= expected_max:
            print(f"   ✅ GOOD: Position size is reasonable")
            return True
        else:
            print(f"   ❌ BAD: Position size too large (>${expected_max:.2f} max expected)")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Run position sizing test"""
    
    print("🔧 POSITION SIZING VERIFICATION")
    print("📅 After reducing to 10 coins and 20% position sizing")
    print("")
    
    success = test_new_position_sizing()
    
    if success:
        print(f"\n🎉 POSITION SIZING FIX VERIFIED!")
        print(f"✅ Ready to restart bot with proper position sizing")
        print(f"💡 Bot will now use ~20% per trade instead of 100%")
    else:
        print(f"\n❌ Position sizing still needs adjustment")

if __name__ == "__main__":
    main()