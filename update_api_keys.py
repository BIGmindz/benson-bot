#!/usr/bin/env python3
"""
🔐 BENSON BOT API CREDENTIALS UPDATER
Update your Kraken API credentials for live trading
"""

import os
from getpass import getpass

def update_api_credentials():
    """Update Kraken API credentials in .env file"""
    
    print("🔐 BENSON BOT LIVE TRADING SETUP")
    print("=" * 40)
    print("Enter your REAL Kraken Pro API credentials")
    print("⚠️  These will be used for LIVE TRADING with real money!")
    print()
    
    # Get API credentials securely
    api_key = input("Enter your Kraken Pro API Key: ").strip()
    if not api_key:
        print("❌ API Key cannot be empty!")
        return
    
    api_secret = getpass("Enter your Kraken Pro Secret Key (hidden): ").strip()
    if not api_secret:
        print("❌ Secret Key cannot be empty!")
        return
    
    # Confirm live trading
    print("\n⚠️  CONFIRMATION:")
    print(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}")
    print("Secret Key: [HIDDEN]")
    print("\n🚨 This will enable LIVE TRADING with REAL MONEY!")
    
    confirm = input("\nType 'LIVE' to confirm: ").strip()
    if confirm != 'LIVE':
        print("❌ Setup cancelled. Type 'LIVE' to confirm live trading.")
        return
    
    # Update .env file
    env_content = f"""# 🔐 BENSON BOT LIVE TRADING CREDENTIALS
# REAL Kraken Pro API credentials for live trading

# Kraken API Credentials (LIVE TRADING)
KRAKEN_API_KEY={api_key}
KRAKEN_SECRET={api_secret}

# Trading Safety Settings
LIVE_TRADING_ENABLED=true
MAX_DAILY_LOSS=50.0         # Maximum daily loss in USD
EMERGENCY_STOP=false        # Set to 'true' to immediately stop all trading

# Optional: Webhook/Notification Settings
DISCORD_WEBHOOK=           # Discord webhook for trade notifications
SLACK_WEBHOOK=             # Slack webhook for alerts
EMAIL_NOTIFICATIONS=       # Email for critical alerts

# Development/Testing
DEBUG_MODE=false           # Enable debug logging
SIMULATION_MODE=false      # Use simulated prices for testing

# Note: Never commit this .env file with real credentials!
# This file is automatically ignored by git (.gitignore)
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ SUCCESS!")
    print("🔑 API credentials updated in .env file")
    print("🚀 Benson Bot is now configured for LIVE TRADING!")
    print("\n📋 Next steps:")
    print("1. Restart Benson Bot: python3 benson_rsi_bot.py")
    print("2. Monitor your Kraken Pro account for live trades")
    print("3. Check terminal output for trading activity")

if __name__ == "__main__":
    update_api_credentials()