#!/usr/bin/env python3
"""
🔧 POSITION SIZING DEBUG SCRIPT
Methodical debugging of the exact failure scenario
"""

import traceback
from trade_executor import TradeRequest, OrderSide, create_trade_executor
from dataclasses import replace

def debug_position_sizing():
    print("🔧 POSITION SIZING DEEP DEBUG")
    print("=" * 60)
    
    try:
        # Step 1: Initialize trade executor
        print("📊 Step 1: Initializing trade executor...")
        executor = create_trade_executor()
        balance = executor.get_account_balance()
        print(f"✅ Balance: ${balance:.2f}")
        
        # Step 2: Create the exact same request as the bot
        print(f"\n📊 Step 2: Creating TradeRequest with amount=0.0...")
        trade_request = TradeRequest(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=0.0,  # This is what's failing
            confidence=0.75,
            signal_strength=0.85,
            metadata={"test": "debug"}
        )
        print(f"✅ TradeRequest created: {trade_request.symbol}, amount={trade_request.amount}")
        
        # Step 3: Test position calculation manually
        print(f"\n📊 Step 3: Manual position calculation...")
        position_value = executor.calculate_position_size(trade_request, balance)
        print(f"✅ Position value: ${position_value:.2f}")
        
        # Step 4: Test price fetching
        print(f"\n📊 Step 4: Testing price fetching...")
        current_price = executor._get_current_price("BTC/USD")
        print(f"✅ Current BTC price: ${current_price:.2f}")
        
        # Step 5: Calculate amount manually
        print(f"\n📊 Step 5: Manual amount calculation...")
        calculated_amount = position_value / current_price
        print(f"✅ Calculated amount: {calculated_amount:.8f} BTC")
        
        # Step 6: Test security validation with zero amount (should fail)
        print(f"\n📊 Step 6: Testing security validation with amount=0.0...")
        is_valid_zero, msg_zero = executor.security_manager.validate_trade_request(trade_request, balance)
        print(f"❌ Zero amount validation: {is_valid_zero} - {msg_zero}")
        
        # Step 7: Test security validation with calculated amount (should pass)
        print(f"\n📊 Step 7: Testing security validation with calculated amount...")
        fixed_request = replace(trade_request, amount=calculated_amount)
        is_valid_calc, msg_calc = executor.security_manager.validate_trade_request(fixed_request, balance)
        print(f"✅ Calculated amount validation: {is_valid_calc} - {msg_calc}")
        
        # Step 8: Test the full execute_trade path
        print(f"\n📊 Step 8: Testing FULL execute_trade() method...")
        print("⚠️  This is a DRY RUN - will test all validation but NOT place actual order")
        
        # Let me trace through the execute_trade method step by step
        print(f"   8a. Initial validation...")
        is_valid, validation_message = executor.security_manager.validate_trade_request(trade_request, balance)
        print(f"       Initial validation: {is_valid} - {validation_message}")
        
        if not is_valid:
            print(f"   8b. Amount is 0.0, should trigger auto-calculation...")
            if trade_request.amount <= 0:
                print(f"       Triggering position size calculation...")
                position_value = executor.calculate_position_size(trade_request, balance)
                current_price = executor._get_current_price(trade_request.symbol)
                calculated_amount = position_value / current_price
                
                print(f"       Position value: ${position_value:.2f}")
                print(f"       Current price: ${current_price:.2f}")
                print(f"       Calculated amount: {calculated_amount:.8f}")
                
                # Create new request with calculated amount
                updated_request = replace(trade_request, amount=calculated_amount)
                print(f"       Updated request amount: {updated_request.amount:.8f}")
                
                # Test final validation
                final_valid, final_msg = executor.security_manager.validate_trade_request(updated_request, balance)
                print(f"       Final validation: {final_valid} - {final_msg}")
                
                if final_valid:
                    print(f"✅ POSITION SIZING FIX WORKING!")
                    print(f"✅ Ready for live trade: ${position_value:.2f} BTC order")
                else:
                    print(f"❌ Final validation still failing: {final_msg}")
        
        print(f"\n🎯 DEBUG SUMMARY:")
        print(f"   Balance: ${balance:.2f}")
        print(f"   Position: ${position_value:.2f}")
        print(f"   BTC Price: ${current_price:.2f}")
        print(f"   Amount: {calculated_amount:.8f} BTC")
        print(f"   Valid: {final_valid if 'final_valid' in locals() else 'Not tested'}")
        
    except Exception as e:
        print(f"\n❌ DEBUG FAILED: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_position_sizing()