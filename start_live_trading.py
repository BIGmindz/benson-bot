#!/usr/bin/env python3
"""
🚀 BENSON BOT LIVE TRADING STARTUP SCRIPT
Enterprise-grade live trading initialization with safety checks
"""

import os
import sys
import yaml
import json
from dotenv import load_dotenv

def check_environment():
    """Comprehensive environment validation"""
    print("🔍 Performing pre-flight checks...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ ERROR: .env file not found")
        print("Run: python3 configure_api_keys.py")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check API credentials
    kraken_api_key = os.getenv("KRAKEN_API_KEY")
    kraken_secret = os.getenv("KRAKEN_SECRET")
    live_trading_enabled = os.getenv("LIVE_TRADING_ENABLED")
    
    if not kraken_api_key or not kraken_secret:
        print("❌ ERROR: Missing Kraken API credentials")
        print("Run: python3 configure_api_keys.py")
        return False
    
    if live_trading_enabled != "true":
        print("❌ ERROR: Live trading not enabled in .env")
        print("Set LIVE_TRADING_ENABLED=true in .env file")
        return False
    
    print("✅ API credentials verified")
    
    # Check config file
    config_path = os.getenv("BENSON_CONFIG", "config/config.yaml")
    if not os.path.exists(config_path):
        print(f"❌ ERROR: Config file not found: {config_path}")
        return False
    
    # Validate config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check live trading settings
    live_config = config.get('live_trading', {})
    if not live_config.get('enabled', False):
        print("❌ ERROR: Live trading disabled in config")
        print("Set live_trading.enabled: true in config/config.yaml")
        return False
    
    if config.get('paper_mode', True):
        print("❌ ERROR: Paper mode still enabled")
        print("Set paper_mode: false in config/config.yaml")
        return False
    
    # Check budget settings
    max_position = live_config.get('max_position_size', 0)
    if max_position < 10:
        print(f"⚠️ WARNING: Very low max position size: ${max_position}")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return False
    
    print(f"✅ Live trading config validated (Max position: ${max_position})")
    
    return True

def display_trading_status():
    """Display current trading configuration"""
    load_dotenv()
    config_path = os.getenv("BENSON_CONFIG", "config/config.yaml")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print("\n" + "="*60)
    print("🚀 BENSON BOT - LIVE TRADING MODE")
    print("="*60)
    
    live_config = config.get('live_trading', {})
    print(f"📊 Exchange: {config.get('exchange', 'kraken').upper()}")
    print(f"💰 Max Position: ${live_config.get('max_position_size', 50)}")
    print(f"🎯 Position Size: {live_config.get('position_size_pct', 100)}%")
    print(f"⛔ Stop Loss: {config.get('stop_loss_pct', 1)}%")
    print(f"🎪 High Confidence Boost: {live_config.get('high_confidence_boost', 1.0)}x")
    print(f"📈 Symbols: {', '.join(config.get('symbols', []))}")
    print(f"🕐 Timeframe: {config.get('timeframe', '5m')}")
    
    rsi_config = config.get('rsi', {})
    print(f"📊 RSI: Buy<{rsi_config.get('buy_threshold', 30)} | Sell>{rsi_config.get('sell_threshold', 70)}")
    
    print("="*60)
    
    return config

def final_confirmation():
    """Final safety confirmation"""
    print("\n⚠️  FINAL SAFETY CHECK")
    print("This will start LIVE TRADING with REAL MONEY")
    print("Make sure you understand the risks involved")
    
    response = input("\nType 'START LIVE TRADING' to continue: ")
    
    if response != "START LIVE TRADING":
        print("❌ Live trading cancelled")
        return False
    
    return True

def main():
    """Main startup sequence"""
    print("🚀 BENSON BOT LIVE TRADING STARTUP")
    print("Enterprise Trading System v2.0")
    print("-" * 40)
    
    # Environment checks
    if not check_environment():
        print("\n❌ Pre-flight checks failed. Aborting.")
        sys.exit(1)
    
    # Display configuration
    config = display_trading_status()
    
    # Final confirmation
    if not final_confirmation():
        sys.exit(0)
    
    # Start live trading
    print("\n🚀 Starting Benson Bot in LIVE TRADING mode...")
    print("Monitor your Kraken Pro account for trades")
    print("Press Ctrl+C to stop trading\n")
    
    # Import and run the main bot
    try:
        from benson_rsi_bot import main as run_bot
        run_bot()
    except KeyboardInterrupt:
        print("\n🛑 Trading stopped by user")
    except Exception as e:
        print(f"\n💥 Trading error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()