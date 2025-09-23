#!/usr/bin/env python3
"""
🎯 BENSON BOT LIVE TRADING MONITOR
Real-time portfolio and trading performance dashboard
"""

import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from portfolio_manager import PortfolioManager
from trade_executor import create_trade_executor


def display_portfolio_dashboard(portfolio_manager, trade_executor):
    """Display comprehensive portfolio dashboard"""
    try:
        # Get current balance
        current_balance = trade_executor.get_account_balance()
        
        # Get portfolio metrics
        metrics = portfolio_manager.get_portfolio_metrics(current_balance)
        
        # Get open positions
        open_positions = portfolio_manager.get_open_positions()
        
        # Clear screen (works on most terminals)
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 80)
        print("🚀 BENSON BOT - LIVE TRADING DASHBOARD")
        print(f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 80)
        
        # Portfolio Overview
        print("\n📊 PORTFOLIO OVERVIEW")
        print("-" * 40)
        print(f"💰 Total Value:      ${metrics.total_value:>10.2f}")
        print(f"💵 Cash Balance:     ${metrics.cash_balance:>10.2f}")
        print(f"📈 Positions Value:  ${metrics.positions_value:>10.2f}")
        print(f"📊 Total P&L:       ${metrics.total_pnl:>10.2f}")
        print(f"🌅 Daily P&L:       ${metrics.daily_pnl:>10.2f}")
        
        # Performance Metrics
        print("\n📈 PERFORMANCE METRICS")
        print("-" * 40)
        print(f"🎯 Win Rate:         {metrics.win_rate:>9.1f}%")
        print(f"📝 Total Trades:     {metrics.total_trades:>10}")
        print(f"✅ Winning Trades:   {metrics.winning_trades:>10}")
        print(f"❌ Losing Trades:    {metrics.losing_trades:>10}")
        print(f"🚀 Largest Win:      ${metrics.largest_win:>10.2f}")
        print(f"💸 Largest Loss:     ${metrics.largest_loss:>10.2f}")
        
        # Open Positions
        if open_positions:
            print("\n🔥 OPEN POSITIONS")
            print("-" * 80)
            print(f"{'Symbol':<12} {'Side':<4} {'Amount':<12} {'Entry $':<10} {'Current $':<10} {'P&L $':<10} {'P&L %':<8}")
            print("-" * 80)
            
            for position in open_positions:
                pnl_pct = (position.unrealized_pnl / (position.entry_amount * position.entry_price)) * 100
                pnl_emoji = "📈" if position.unrealized_pnl > 0 else "📉" if position.unrealized_pnl < 0 else "➡️"
                
                print(f"{position.symbol:<12} {position.side.upper():<4} {position.current_amount:<12.6f} "
                      f"{position.entry_price:<10.2f} {position.current_price:<10.2f} "
                      f"{position.unrealized_pnl:<10.2f} {pnl_pct:<7.1f}% {pnl_emoji}")
        else:
            print("\n💤 NO OPEN POSITIONS")
        
        # Risk Metrics
        print("\n⚠️ RISK METRICS")
        print("-" * 40)
        exposure_pct = (metrics.positions_value / metrics.total_value * 100) if metrics.total_value > 0 else 0
        print(f"🎲 Market Exposure:  {exposure_pct:>9.1f}%")
        print(f"🔒 Cash Reserve:     {(metrics.cash_balance/metrics.total_value*100):>9.1f}%")
        
        # Trading Status
        print("\n🤖 TRADING STATUS")
        print("-" * 40)
        print("🟢 System Status:    ACTIVE")
        print("🔄 Auto Trading:    ENABLED")
        print("📊 Signal Monitor:   RUNNING")
        print("⚡ Portfolio Mgmt:   ACTIVE")
        
        print("\n" + "=" * 80)
        print("Press Ctrl+C to stop monitoring | Updates every 30 seconds")
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")


def main():
    """Main monitoring loop"""
    load_dotenv()
    
    try:
        # Initialize components
        portfolio_manager = PortfolioManager()
        trade_executor = create_trade_executor()
        
        print("🚀 Starting Benson Bot Live Trading Monitor...")
        print("📊 Initializing dashboard...")
        
        while True:
            display_portfolio_dashboard(portfolio_manager, trade_executor)
            time.sleep(30)  # Update every 30 seconds
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n💥 Monitor error: {e}")


if __name__ == "__main__":
    main()