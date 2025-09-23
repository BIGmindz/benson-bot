#!/usr/bin/env python3
"""
🔐 BENSON BOT API KEY CONFIGURATION
Interactive setup to securely configure Kraken API credentials
"""
import os
import getpass
import re

def configure_api_keys():
    print("🔐 BENSON BOT - KRAKEN API KEY SETUP")
    print("=" * 50)
    print("This script will help you configure your Kraken API credentials securely.")
    print("Your keys will be saved to the .env file and never displayed in plain text.")
    print("")
    
    # Get current values
    env_path = '.env'
    if not os.path.exists(env_path):
        print("❌ .env file not found! Please run setup_live_trading.py first.")
        return
    
    print("📋 INSTRUCTIONS:")
    print("1. Go to https://www.kraken.com/u/security/api")
    print("2. Create a new API key with these permissions:")
    print("   ✅ Query Funds")
    print("   ✅ Query Open Orders & Trades") 
    print("   ✅ Query Closed Orders & Trades")
    print("   ✅ Query Ledger Entries")
    print("   ✅ Create & Modify Orders")
    print("   ❌ Withdraw Funds (leave unchecked)")
    print("")
    
    # Get API Key
    api_key = getpass.getpass("🔑 Enter your Kraken API Key (hidden input): ")
    if not api_key or len(api_key) < 10:
        print("❌ Invalid API key. Must be at least 10 characters.")
        return
    
    # Get Secret
    secret = getpass.getpass("🔐 Enter your Kraken Secret (hidden input): ")
    if not secret or len(secret) < 10:
        print("❌ Invalid secret. Must be at least 10 characters.")
        return
    
    # Confirm live trading
    print("")
    live_trading = input("🚨 Enable live trading with real money? (yes/NO): ").lower().strip()
    live_enabled = live_trading == 'yes'
    
    # Read current .env file
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Replace the values
    content = re.sub(r'KRAKEN_API_KEY=.*', f'KRAKEN_API_KEY={api_key}', content)
    content = re.sub(r'KRAKEN_SECRET=.*', f'KRAKEN_SECRET={secret}', content)
    content = re.sub(r'LIVE_TRADING_ENABLED=.*', f'LIVE_TRADING_ENABLED={str(live_enabled).lower()}', content)
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("")
    print("✅ API credentials configured successfully!")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]} (masked)")
    print(f"🔐 Secret: {secret[:4]}...{secret[-4:]} (masked)")
    print(f"⚡ Live Trading: {'ENABLED' if live_enabled else 'DISABLED'}")
    print("")
    
    if live_enabled:
        print("🚨 LIVE TRADING ENABLED!")
        print("⚠️  You can now trade with real money.")
        print("💡 Run 'python setup_live_trading.py' to verify your setup.")
        print("🚀 Run 'python ultra_rapid_trainer.py' to start live trading.")
    else:
        print("📊 Paper trading mode active.")
        print("💡 Set LIVE_TRADING_ENABLED=true in .env when ready for live trading.")
    
    print("")
    print("🔒 Security Notes:")
    print("• Your API keys are now saved in .env (git-ignored)")
    print("• Never share your .env file or API keys")
    print("• You can revoke keys anytime from Kraken website")

if __name__ == "__main__":
    try:
        configure_api_keys()
    except KeyboardInterrupt:
        print("\n❌ Configuration cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")