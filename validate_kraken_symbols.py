#!/usr/bin/env python3
"""
Kraken Symbol Validator for Benson Bot
Validates 40 cryptos from config.yaml against Kraken's available trading pairs
Converts USDT symbols to USD format and identifies unavailable symbols
"""

import ccxt
import yaml
import json
from datetime import datetime
from typing import List, Dict, Tuple

class KrakenSymbolValidator:
    def __init__(self):
        """Initialize Kraken exchange connection"""
        self.exchange = ccxt.kraken({'enableRateLimit': True})
        self.markets = None
        self.tickers = None
        
    def load_kraken_data(self):
        """Load Kraken markets and ticker data"""
        print('🔄 Loading Kraken markets and ticker data...')
        self.markets = self.exchange.load_markets()
        self.tickers = self.exchange.fetch_tickers()
        print(f'✅ Loaded {len(self.markets)} markets and {len(self.tickers)} tickers')
        
    def load_config_symbols(self, config_path: str = "config/config.yaml") -> List[str]:
        """Load symbols from config.yaml"""
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config.get('symbols', [])
        
    def validate_symbols(self, symbols: List[str]) -> Dict:
        """Validate each symbol against Kraken's available pairs"""
        results = {
            'available': [],
            'converted': [],
            'unavailable': [],
            'validation_details': []
        }
        
        print(f'\n🔍 Validating {len(symbols)} symbols against Kraken...')
        print('=' * 80)
        
        for i, symbol in enumerate(symbols, 1):
            print(f'{i:2d}. Checking {symbol:15}', end=' ')
            
            validation_result = self._validate_single_symbol(symbol)
            results['validation_details'].append(validation_result)
            
            if validation_result['status'] == 'available':
                results['available'].append(validation_result)
                print(f"✅ Available")
            elif validation_result['status'] == 'converted':
                results['converted'].append(validation_result)
                print(f"🔄 Converted to {validation_result['kraken_symbol']}")
            else:
                results['unavailable'].append(validation_result)
                print(f"❌ Not available")
                
        return results
        
    def _validate_single_symbol(self, symbol: str) -> Dict:
        """Validate a single symbol and attempt conversion"""
        base_symbol = symbol.split('/')[0]
        
        # Direct check
        if symbol in self.markets:
            ticker_data = self.tickers.get(symbol, {})
            return {
                'original_symbol': symbol,
                'kraken_symbol': symbol,
                'status': 'available',
                'volume_24h': ticker_data.get('quoteVolume', 0),
                'price': ticker_data.get('last', 0),
                'change_24h': ticker_data.get('percentage', 0) or 0
            }
            
        # Try USD conversion (most common for Kraken)
        usd_symbol = f"{base_symbol}/USD"
        if usd_symbol in self.markets:
            ticker_data = self.tickers.get(usd_symbol, {})
            return {
                'original_symbol': symbol,
                'kraken_symbol': usd_symbol,
                'status': 'converted',
                'conversion_note': 'USDT -> USD',
                'volume_24h': ticker_data.get('quoteVolume', 0),
                'price': ticker_data.get('last', 0),
                'change_24h': ticker_data.get('percentage', 0) or 0
            }
            
        # Try other common Kraken quote currencies
        for quote in ['EUR', 'GBP', 'CAD', 'JPY']:
            alt_symbol = f"{base_symbol}/{quote}"
            if alt_symbol in self.markets:
                ticker_data = self.tickers.get(alt_symbol, {})
                return {
                    'original_symbol': symbol,
                    'kraken_symbol': alt_symbol,
                    'status': 'converted',
                    'conversion_note': f'USDT -> {quote}',
                    'volume_24h': ticker_data.get('quoteVolume', 0),
                    'price': ticker_data.get('last', 0),
                    'change_24h': ticker_data.get('percentage', 0) or 0
                }
        
        return {
            'original_symbol': symbol,
            'kraken_symbol': None,
            'status': 'unavailable',
            'reason': 'No matching pair found on Kraken'
        }
        
    def generate_kraken_config(self, validation_results: Dict) -> List[str]:
        """Generate validated Kraken symbol list for config"""
        kraken_symbols = []
        
        # Add available symbols
        for item in validation_results['available']:
            kraken_symbols.append(item['kraken_symbol'])
            
        # Add converted symbols  
        for item in validation_results['converted']:
            kraken_symbols.append(item['kraken_symbol'])
            
        return kraken_symbols
        
    def print_validation_report(self, validation_results: Dict):
        """Print comprehensive validation report"""
        print(f'\n📊 KRAKEN SYMBOL VALIDATION REPORT')
        print('=' * 80)
        print(f'🕒 Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        total = len(validation_results['validation_details'])
        available = len(validation_results['available'])
        converted = len(validation_results['converted'])
        unavailable = len(validation_results['unavailable'])
        
        print(f'\n📈 SUMMARY:')
        print(f'   Total symbols checked: {total}')
        print(f'   ✅ Available as-is: {available}')
        print(f'   🔄 Converted: {converted}')
        print(f'   ❌ Unavailable: {unavailable}')
        print(f'   Success rate: {((available + converted) / total * 100):.1f}%')
        
        if validation_results['converted']:
            print(f'\n🔄 CONVERTED SYMBOLS:')
            for item in validation_results['converted']:
                print(f'   {item["original_symbol"]:15} -> {item["kraken_symbol"]:15} ({item["conversion_note"]})')
                
        if validation_results['unavailable']:
            print(f'\n❌ UNAVAILABLE SYMBOLS:')
            for item in validation_results['unavailable']:
                print(f'   {item["original_symbol"]:15} - {item["reason"]}')
                
        # Top performers by volume
        available_with_volume = [
            item for item in validation_results['validation_details'] 
            if item['status'] in ['available', 'converted'] and item.get('volume_24h', 0) > 0
        ]
        available_with_volume.sort(key=lambda x: x.get('volume_24h', 0), reverse=True)
        
        print(f'\n🚀 TOP 10 BY 24H VOLUME:')
        for i, item in enumerate(available_with_volume[:10], 1):
            symbol = item['kraken_symbol']
            volume = item.get('volume_24h', 0)
            price = item.get('price', 0)
            change = item.get('change_24h', 0)
            print(f'   {i:2d}. {symbol:>12} | Vol: ${volume:>12,.0f} | Price: ${price:>10.4f} | Change: {change:>6.1f}%')
            
    def save_results(self, validation_results: Dict, kraken_symbols: List[str]):
        """Save validation results to files"""
        # Save detailed validation results
        with open('kraken_validation_results.json', 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)
            
        # Save Kraken-compatible symbol list
        with open('kraken_symbols.json', 'w') as f:
            json.dump(kraken_symbols, f, indent=2)
            
        # Save YAML-ready format
        config_section = {
            'symbols': kraken_symbols,
            'validation_timestamp': datetime.now().isoformat(),
            'validation_summary': {
                'total_checked': len(validation_results['validation_details']),
                'available': len(validation_results['available']),
                'converted': len(validation_results['converted']),
                'unavailable': len(validation_results['unavailable'])
            }
        }
        
        with open('kraken_config_section.yaml', 'w') as f:
            yaml.dump(config_section, f, default_flow_style=False)
            
        print(f'\n💾 SAVED FILES:')
        print(f'   📄 kraken_validation_results.json - Detailed validation results')
        print(f'   📄 kraken_symbols.json - Kraken-compatible symbol list')
        print(f'   📄 kraken_config_section.yaml - YAML config section')

def main():
    """Main execution function"""
    print('🤖 BENSON BOT - KRAKEN SYMBOL VALIDATOR')
    print('=' * 80)
    
    validator = KrakenSymbolValidator()
    
    try:
        # Load Kraken data
        validator.load_kraken_data()
        
        # Load symbols from config
        symbols = validator.load_config_symbols()
        print(f'\n📋 Loaded {len(symbols)} symbols from config.yaml')
        
        # Validate symbols
        validation_results = validator.validate_symbols(symbols)
        
        # Generate Kraken-compatible list
        kraken_symbols = validator.generate_kraken_config(validation_results)
        
        # Print report
        validator.print_validation_report(validation_results)
        
        # Save results
        validator.save_results(validation_results, kraken_symbols)
        
        print(f'\n✅ Validation complete! Ready to update config.yaml with {len(kraken_symbols)} validated symbols.')
        
    except Exception as e:
        print(f'\n❌ ERROR: {str(e)}')
        raise

if __name__ == "__main__":
    main()