#!/usr/bin/env python3
"""
🚀 BENSON BOT LIVE TRADING SETUP WIZARD
Interactive setup for transitioning from paper to live trading
"""

import os
import yaml
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    template_path = ".env.template"
    env_path = ".env"
    
    if os.path.exists(env_path):
        print("✅ .env file already exists")
        return True
    
    if not os.path.exists(template_path):
        print("❌ .env.template not found")
        return False
    
    shutil.copy(template_path, env_path)
    print("✅ Created .env file from template")
    return True

def check_kraken_credentials():
    """Check if Kraken credentials are configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('KRAKEN_API_KEY')
    secret = os.getenv('KRAKEN_SECRET')
    
    if not api_key or api_key == 'your_kraken_api_key_here':
        return False, "KRAKEN_API_KEY not configured"
    
    if not secret or secret == 'your_kraken_secret_here':
        return False, "KRAKEN_SECRET not configured"
    
    return True, "Credentials configured"

def test_kraken_connection():
    """Test connection to Kraken API"""
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        import ccxt
        
        api_key = os.getenv('KRAKEN_API_KEY')
        secret = os.getenv('KRAKEN_SECRET')
        
        exchange = ccxt.kraken({
            'apiKey': api_key,
            'secret': secret,
            'sandbox': False,
            'enableRateLimit': True,
        })
        
        # Test API connection
        balance = exchange.fetch_balance()
        usd_balance = balance.get('USD', {}).get('free', 0.0)
        
        return True, f"Connected successfully. USD Balance: ${usd_balance:.2f}"
        
    except Exception as e:
        return False, f"Connection failed: {str(e)[:100]}"

def check_config_file():
    """Check if config.yaml is properly configured for live trading"""
    config_path = "config/config.yaml"
    
    if not os.path.exists(config_path):
        return False, "config.yaml not found"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    paper_mode = config.get('paper_mode', True)
    live_config = config.get('live_trading', {})
    
    if paper_mode:
        return False, "paper_mode is still enabled"
    
    if not live_config:
        return False, "live_trading configuration missing"
    
    return True, "Configuration ready for live trading"

def setup_gitignore():
    """Ensure .env is in .gitignore"""
    gitignore_path = ".gitignore"
    
    # Read existing .gitignore
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        if '.env' in content:
            print("✅ .env already in .gitignore")
            return True
    
    # Add .env to .gitignore
    with open(gitignore_path, 'a') as f:
        f.write("\n# Environment variables (contains secrets)\n.env\n")
    
    print("✅ Added .env to .gitignore")
    return True

def display_kraken_api_instructions():
    """Display instructions for getting Kraken API keys"""
    print("\n🔑 KRAKEN API SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to https://www.kraken.com/u/security/api")
    print("2. Click 'Create New Key'")
    print("3. Set permissions:")
    print("   ✅ Query Funds")
    print("   ✅ Query Open Orders & Trades")
    print("   ✅ Query Closed Orders & Trades") 
    print("   ✅ Query Ledger Entries")
    print("   ✅ Create & Modify Orders")
    print("   ❌ Withdraw Funds (leave unchecked for security)")
    print("4. Copy the API Key and Private Key")
    print("5. Add them to your .env file:")
    print("   KRAKEN_API_KEY=your_actual_api_key")
    print("   KRAKEN_SECRET=your_actual_secret")
    print("6. Set LIVE_TRADING_ENABLED=true when ready")
    print("\n⚠️  SECURITY NOTES:")
    print("• Never share your API keys")
    print("• API keys have withdrawal disabled by default")
    print("• You can revoke keys anytime from Kraken website")

def display_safety_checklist():
    """Display safety checklist for live trading"""
    print("\n🛡️  LIVE TRADING SAFETY CHECKLIST:")
    print("=" * 50)
    print("✅ Start with small amounts ($50-200)")
    print("✅ Set daily loss limits ($20-50)")
    print("✅ Monitor trades closely initially")
    print("✅ Have emergency stop procedures ready")
    print("✅ Test with paper trading first")
    print("✅ Understand position sizing")
    print("✅ Know how to manually close positions")
    print("✅ Have Kraken mobile app for monitoring")
    print("\n⚠️  RISK WARNINGS:")
    print("• Cryptocurrency trading involves significant risk")
    print("• Past performance does not guarantee future results")
    print("• Only trade with money you can afford to lose")
    print("• Markets can be highly volatile")
    print("• Automated trading can amplify losses")

def main():
    """Main setup wizard"""
    print("🚀 BENSON BOT - LIVE TRADING SETUP WIZARD")
    print("=" * 60)
    print("This wizard will help you transition from paper to live trading")
    print("⚠️  WARNING: Live trading involves real money and risk")
    print("")
    
    # Safety confirmation
    response = input("Do you understand the risks and want to proceed? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Setup cancelled")
        return
    
    print("\n📋 SETUP CHECKLIST:")
    print("-" * 30)
    
    # 1. Create .env file
    print("1. Creating environment file...")
    if not create_env_file():
        print("❌ Failed to create .env file")
        return
    
    # 2. Setup .gitignore
    print("2. Configuring git security...")
    setup_gitignore()
    
    # 3. Check configuration
    print("3. Checking configuration...")
    config_ok, config_msg = check_config_file()
    print(f"   Config: {config_msg}")
    
    # 4. Check credentials
    print("4. Checking API credentials...")
    try:
        cred_ok, cred_msg = check_kraken_credentials()
        print(f"   Credentials: {cred_msg}")
        
        if cred_ok:
            # 5. Test connection
            print("5. Testing API connection...")
            conn_ok, conn_msg = test_kraken_connection()
            print(f"   Connection: {conn_msg}")
            
            if conn_ok and config_ok:
                print("\n🎉 SETUP COMPLETE!")
                print("✅ All checks passed - ready for live trading")
                print("")
                print("🚀 NEXT STEPS:")
                print("1. Set LIVE_TRADING_ENABLED=true in .env")
                print("2. Run: python ultra_rapid_trainer.py")
                print("3. Monitor trades closely")
                return True
            else:
                print(f"\n⚠️  Setup incomplete:")
                if not conn_ok:
                    print(f"   API: {conn_msg}")
                if not config_ok:
                    print(f"   Config: {config_msg}")
        else:
            print(f"   ❌ {cred_msg}")
            
    except ImportError:
        print("   ❌ Missing python-dotenv package")
        print("   Run: pip install python-dotenv")
        return False
    
    # Show instructions if setup incomplete
    if not cred_ok:
        display_kraken_api_instructions()
    
    display_safety_checklist()
    
    print("\n📝 MANUAL STEPS REQUIRED:")
    print("1. Edit .env file with your Kraken credentials")
    print("2. Set LIVE_TRADING_ENABLED=true when ready")
    print("3. Ensure config.yaml has paper_mode: false")
    print("4. Review live_trading settings in config.yaml")
    print("5. Run setup again to verify")
    
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Run this setup again after completing the manual steps")
        print("🔍 Use 'python setup_live_trading.py' to re-run checks")