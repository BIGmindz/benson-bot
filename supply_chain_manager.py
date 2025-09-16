#!/usr/bin/env python3
"""
Supply Chain Signal Management System
Handles disabling/enabling supply chain signals based on data quality
"""

import json
import yaml
import requests
import time
from datetime import datetime
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SupplyChainDataSource:
    name: str
    url: str
    api_key_required: bool
    test_endpoint: str
    description: str

class SupplyChainManager:
    """Manages supply chain signal availability and data quality"""
    
    def __init__(self):
        self.config_yaml_path = "config/config.yaml"
        self.config_json_path = "benson_user_config.json"
        
        # Potential real data sources to integrate
        self.data_sources = [
            SupplyChainDataSource(
                name="MarineTraffic API",
                url="https://services.marinetraffic.com/api",
                api_key_required=True,
                test_endpoint="/exportvessels/v:3",
                description="Real-time vessel tracking and port congestion"
            ),
            SupplyChainDataSource(
                name="Freightos Baltic Index",
                url="https://fbx.freightos.com",
                api_key_required=False,
                test_endpoint="/api/freight-index",
                description="Global freight rate index"
            ),
            SupplyChainDataSource(
                name="Port Authority APIs",
                url="https://api.portoflosangeles.org",
                api_key_required=True,
                test_endpoint="/v1/congestion",
                description="Port congestion and throughput data"
            ),
            SupplyChainDataSource(
                name="Baltic Exchange",
                url="https://www.balticexchange.com",
                api_key_required=True,
                test_endpoint="/api/indices",
                description="Dry cargo shipping rates"
            )
        ]
    
    def check_supply_chain_status(self) -> Dict:
        """Check current supply chain signal configuration"""
        try:
            # Check YAML config
            with open(self.config_yaml_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
            yaml_enabled = yaml_config.get('supply_chain_signals', {}).get('enabled', False)
            
            # Check JSON config
            with open(self.config_json_path, 'r') as f:
                json_config = json.load(f)
            json_enabled = json_config.get('signals', {}).get('supply_chain', {}).get('enabled', False)
            
            return {
                'yaml_enabled': yaml_enabled,
                'json_enabled': json_enabled,
                'both_enabled': yaml_enabled and json_enabled,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def disable_supply_chain_signals(self, reason: str = "Data quality issues") -> bool:
        """Disable supply chain signals in both config files"""
        try:
            print(f"🚫 DISABLING Supply Chain Signals: {reason}")
            
            # Update YAML config
            with open(self.config_yaml_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            if 'supply_chain_signals' in yaml_config:
                yaml_config['supply_chain_signals']['enabled'] = False
                
            with open(self.config_yaml_path, 'w') as f:
                yaml.dump(yaml_config, f, default_flow_style=False, indent=2)
            
            # Update JSON config
            with open(self.config_json_path, 'r') as f:
                json_config = json.load(f)
            
            if 'signals' in json_config and 'supply_chain' in json_config['signals']:
                json_config['signals']['supply_chain']['enabled'] = False
                json_config['signals']['supply_chain']['description'] = f"🔗 Supply Chain Signals - DISABLED ({reason})"
            
            with open(self.config_json_path, 'w') as f:
                json.dump(json_config, f, indent=2)
            
            print("✅ Supply chain signals disabled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error disabling supply chain signals: {e}")
            return False
    
    def test_data_source_availability(self, source: SupplyChainDataSource) -> Tuple[bool, str]:
        """Test if a data source is available and returning real data"""
        try:
            # Simple connectivity test
            response = requests.get(source.url, timeout=10)
            if response.status_code == 200:
                return True, f"✅ {source.name}: Available"
            else:
                return False, f"❌ {source.name}: HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"❌ {source.name}: Connection failed - {e}"
    
    def scan_for_real_data_sources(self) -> Dict:
        """Scan all potential data sources for availability"""
        print("🔍 SCANNING for real supply chain data sources...")
        results = {
            'timestamp': datetime.now().isoformat(),
            'sources_tested': len(self.data_sources),
            'available_sources': [],
            'unavailable_sources': [],
            'real_data_available': False
        }
        
        for source in self.data_sources:
            available, message = self.test_data_source_availability(source)
            print(f"   {message}")
            
            if available:
                results['available_sources'].append({
                    'name': source.name,
                    'description': source.description,
                    'requires_api_key': source.api_key_required
                })
                results['real_data_available'] = True
            else:
                results['unavailable_sources'].append({
                    'name': source.name,
                    'error': message
                })
        
        return results
    
    def enable_supply_chain_signals(self, reason: str = "Real data sources detected") -> bool:
        """Enable supply chain signals in both config files"""
        try:
            print(f"✅ ENABLING Supply Chain Signals: {reason}")
            
            # Update YAML config
            with open(self.config_yaml_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            if 'supply_chain_signals' in yaml_config:
                yaml_config['supply_chain_signals']['enabled'] = True
                
            with open(self.config_yaml_path, 'w') as f:
                yaml.dump(yaml_config, f, default_flow_style=False, indent=2)
            
            # Update JSON config
            with open(self.config_json_path, 'r') as f:
                json_config = json.load(f)
            
            if 'signals' in json_config and 'supply_chain' in json_config['signals']:
                json_config['signals']['supply_chain']['enabled'] = True
                json_config['signals']['supply_chain']['description'] = f"🔗 Supply Chain Signals - ENABLED ({reason})"
            
            with open(self.config_json_path, 'w') as f:
                json.dump(json_config, f, indent=2)
            
            print("✅ Supply chain signals enabled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error enabling supply chain signals: {e}")
            return False
    
    def auto_check_and_enable(self) -> Dict:
        """Automatically check for real data and enable if available"""
        print("🤖 AUTO-CHECK: Scanning for real supply chain data...")
        
        # Check current status
        status = self.check_supply_chain_status()
        scan_results = self.scan_for_real_data_sources()
        
        result = {
            'current_status': status,
            'scan_results': scan_results,
            'action_taken': 'none',
            'timestamp': datetime.now().isoformat()
        }
        
        if scan_results['real_data_available'] and not status.get('both_enabled', False):
            # Real data found and signals are disabled - enable them
            if self.enable_supply_chain_signals("Real data sources detected"):
                result['action_taken'] = 'enabled'
                print("🎉 Supply chain signals have been ENABLED due to real data availability!")
        elif not scan_results['real_data_available'] and status.get('both_enabled', False):
            # No real data found but signals are enabled - disable them
            if self.disable_supply_chain_signals("No real data sources available"):
                result['action_taken'] = 'disabled'
                print("⚠️ Supply chain signals have been DISABLED due to lack of real data!")
        else:
            print(f"ℹ️ No action needed. Signals enabled: {status.get('both_enabled', False)}, Real data: {scan_results['real_data_available']}")
        
        return result

def main():
    """Command line interface for supply chain management"""
    import sys
    
    manager = SupplyChainManager()
    
    if len(sys.argv) < 2:
        print("🔗 SUPPLY CHAIN SIGNAL MANAGER")
        print("=" * 40)
        print("Commands:")
        print("  status    - Check current signal status")
        print("  disable   - Disable supply chain signals")
        print("  enable    - Enable supply chain signals")
        print("  scan      - Scan for real data sources")
        print("  auto      - Auto-check and enable/disable based on data availability")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        status = manager.check_supply_chain_status()
        print("📊 SUPPLY CHAIN STATUS:")
        print(f"   YAML Config: {'✅ Enabled' if status.get('yaml_enabled') else '❌ Disabled'}")
        print(f"   JSON Config: {'✅ Enabled' if status.get('json_enabled') else '❌ Disabled'}")
        print(f"   Both Active: {'✅ Yes' if status.get('both_enabled') else '❌ No'}")
        
    elif command == "disable":
        manager.disable_supply_chain_signals("Manual disable requested")
        
    elif command == "enable":
        manager.enable_supply_chain_signals("Manual enable requested")
        
    elif command == "scan":
        results = manager.scan_for_real_data_sources()
        print(f"📡 Found {len(results['available_sources'])} available data sources")
        
    elif command == "auto":
        results = manager.auto_check_and_enable()
        print(f"🤖 Auto-check complete: {results['action_taken']}")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()