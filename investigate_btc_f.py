#!/usr/bin/env python3
"""
🔍 INVESTIGATE BTC.F POSITION
Check what BTC.F actually is and how to convert it to USD
"""

from trade_executor import create_trade_executor

def investigate_btc_f():
    """Investigate the BTC.F position and available options"""
    
    print("🔍 INVESTIGATING BTC.F POSITION")
    print("=" * 50)
    
    try:
        trade_executor = create_trade_executor("kraken_config_section.yaml")
        
        # Get full balance details
        balance_info = trade_executor.exchange.fetch_balance()
        
        print("💰 FULL BALANCE BREAKDOWN:")
        for currency, data in balance_info.items():
            if isinstance(data, dict) and data.get('free', 0) > 0:
                free_amount = data['free']
                print(f"   {currency}: {free_amount} (free)")
        
        print(f"\n🔍 BTC.F DETAILS:")
        btc_f_info = balance_info.get('BTC.F', {})
        print(f"   Free: {btc_f_info.get('free', 0)}")
        print(f"   Used: {btc_f_info.get('used', 0)}")
        print(f"   Total: {btc_f_info.get('total', 0)}")
        
        # Load markets and check what's available
        markets = trade_executor.exchange.load_markets()
        
        print(f"\n📊 SEARCHING FOR BTC.F TRADING PAIRS:")
        btc_f_pairs = []
        for symbol in markets.keys():
            if 'BTC.F' in symbol:
                btc_f_pairs.append(symbol)
                market_info = markets[symbol]
                print(f"   {symbol}: {market_info.get('base', 'N/A')} / {market_info.get('quote', 'N/A')}")
                print(f"      Active: {market_info.get('active', False)}")
                print(f"      Type: {market_info.get('type', 'N/A')}")
        
        if not btc_f_pairs:
            print("   ❌ No BTC.F trading pairs found")
        
        # Check for similar BTC pairs
        print(f"\n🔍 RELATED BTC PAIRS:")
        btc_pairs = []
        for symbol in markets.keys():
            if symbol.startswith('BTC') and 'USD' in symbol:
                btc_pairs.append(symbol)
                market_info = markets[symbol]
                print(f"   {symbol}: Active={market_info.get('active', False)}")
        
        # Check the raw account info from Kraken
        print(f"\n🔍 RAW KRAKEN BALANCE INFO:")
        raw_info = balance_info.get('info', {})
        if 'result' in raw_info:
            result = raw_info['result']
            for currency, data in result.items():
                if 'BTC' in currency and float(data.get('balance', 0)) > 0:
                    print(f"   {currency}: balance={data.get('balance', 0)}, hold={data.get('hold_trade', 0)}")
        
        # Check if this is a futures position
        print(f"\n💡 BTC.F ANALYSIS:")
        print(f"   BTC.F likely stands for 'BTC Futures'")
        print(f"   This might be a futures contract position")
        print(f"   May require different liquidation method")
        
        # Try to find futures-related endpoints
        try:
            # Check if exchange supports futures
            if hasattr(trade_executor.exchange, 'fetch_positions'):
                positions = trade_executor.exchange.fetch_positions()
                print(f"   📊 Futures positions: {len(positions)}")
                for pos in positions:
                    if pos.get('symbol') and 'BTC' in pos.get('symbol', ''):
                        print(f"      {pos.get('symbol')}: {pos.get('size', 0)} contracts")
        except Exception as e:
            print(f"   ⚠️  Futures check failed: {e}")
        
        return btc_f_pairs
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def main():
    """Main investigation"""
    print("🕵️ BTC.F INVESTIGATION REPORT")
    print("=" * 60)
    
    btc_f_pairs = investigate_btc_f()
    
    print(f"\n🎯 RECOMMENDATIONS:")
    if btc_f_pairs:
        print(f"✅ Found {len(btc_f_pairs)} BTC.F trading pairs - can liquidate")
    else:
        print("❌ No direct trading pairs found")
        print("💡 Possible solutions:")
        print("   1. Check Kraken web interface for manual conversion")
        print("   2. BTC.F might be a futures position requiring special handling")
        print("   3. May need to close futures position rather than sell spot")
        print("   4. Contact Kraken support for conversion guidance")

if __name__ == "__main__":
    main()