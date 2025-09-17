#!/usr/bin/env python3
"""
Benson Bot Configuration Manager
Interactive toggle system for all bot features with persistent settings
"""

import json
import os
from typing import Dict, Any
from datetime import datetime

class BensonConfigManager:
    """
    Interactive configuration manager with toggleable features
    Saves settings persistently and provides UI-friendly interface
    """
    
    def __init__(self, config_file: str = "benson_user_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"📁 Loaded configuration from {self.config_file}")
                return config
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
                
        # Create default configuration
        default_config = {
            "signals": {
                "supply_chain": {
                    "enabled": True,
                    "sensitivity": 1.0,
                    "region": "global",
                    "description": "🔗 Supply Chain Signals - Market disruption & logistics analysis"
                },
                "sentiment": {
                    "enabled": True,
                    "weight": 0.25,
                    "sources": ["social", "news", "market"],
                    "description": "😊 Sentiment Analysis - Social media & news sentiment"
                },
                "rsi": {
                    "enabled": True,
                    "period": 14,
                    "oversold": 30,
                    "overbought": 70,
                    "description": "📊 RSI Signals - Relative Strength Index technical analysis"
                },
                "brazil_factor": {
                    "enabled": True,
                    "weight": 0.125,
                    "description": "🇧🇷 Brazil Economic Factor - Regional market conditions"
                },
                "africa_factor": {
                    "enabled": True,
                    "weight": 0.125,
                    "description": "🌍 Africa Economic Factor - Regional market conditions"
                }
            },
            "engines": {
                "learning_engine": {
                    "enabled": True,
                    "auto_train": True,
                    "pattern_threshold": 100,
                    "description": "🧠 Learning Engine - AI pattern recognition & training"
                },
                "profit_engine": {
                    "enabled": True,
                    "auto_reinvest": True,
                    "auto_withdraw": True,
                    "scaling_active": True,
                    "description": "💰 Profit Engine - Intelligent profit management & scaling"
                },
                "pattern_recognition": {
                    "enabled": True,
                    "advanced_mode": True,
                    "description": "🔍 Advanced Pattern Recognition - Market pattern analysis"
                }
            },
            "trading": {
                "ultra_selective": {
                    "enabled": True,
                    "confidence_threshold": 70.0,
                    "signal_threshold": 0.6,
                    "description": "💎 Ultra-Selective Trading - Only highest quality trades"
                },
                "maximum_conviction": {
                    "enabled": True,
                    "max_position": 0.85,
                    "scaling_factor": 2.0,
                    "description": "🚀 Maximum Conviction - Up to 85% positions on perfect trades"
                },
                "random_learning": {
                    "enabled": True,
                    "frequency": 0.1,
                    "description": "🎲 Random Learning Trades - Edge case exploration"
                }
            },
            "ui": {
                "show_emojis": True,
                "verbose_logging": True,
                "real_time_updates": True,
                "color_coding": True,
                "description": "🎨 User Interface - Display preferences"
            },
            "meta": {
                "created": datetime.now().isoformat(),
                "version": "2.0",
                "last_modified": datetime.now().isoformat()
            }
        }
        
        self.save_config(default_config)
        print(f"✨ Created default configuration in {self.config_file}")
        return default_config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save current configuration to file"""
        if config is None:
            config = self.config
            
        config["meta"]["last_modified"] = datetime.now().isoformat()
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"💾 Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def toggle_feature(self, category: str, feature: str) -> bool:
        """Toggle a feature on/off and return new state"""
        if category in self.config and feature in self.config[category]:
            current_state = self.config[category][feature].get("enabled", False)
            new_state = not current_state
            self.config[category][feature]["enabled"] = new_state
            self.save_config()
            
            desc = self.config[category][feature].get("description", f"{feature}")
            status = "🟢 ENABLED" if new_state else "🔴 DISABLED"
            print(f"{status}: {desc}")
            return new_state
        else:
            print(f"❌ Feature {category}.{feature} not found")
            return False
    
    def get_feature_status(self, category: str, feature: str) -> bool:
        """Get current status of a feature"""
        if category in self.config and feature in self.config[category]:
            return self.config[category][feature].get("enabled", False)
        return False
    
    def interactive_config_menu(self):
        """Interactive menu for toggling features"""
        while True:
            print("\n" + "="*60)
            print("🎛️  BENSON BOT - INTERACTIVE CONFIGURATION")
            print("="*60)
            
            # Display current status
            print("\n📊 CURRENT STATUS:")
            
            print("\n🔗 SIGNALS:")
            for signal, config in self.config["signals"].items():
                status = "🟢" if config["enabled"] else "🔴"
                print(f"   {status} {signal.replace('_', ' ').title()}")
            
            print("\n🎯 ENGINES:")
            for engine, config in self.config["engines"].items():
                status = "🟢" if config["enabled"] else "🔴"
                print(f"   {status} {engine.replace('_', ' ').title()}")
                
            print("\n💎 TRADING FEATURES:")
            for feature, config in self.config["trading"].items():
                status = "🟢" if config["enabled"] else "🔴"
                print(f"   {status} {feature.replace('_', ' ').title()}")
            
            print("\n🎨 USER INTERFACE:")
            for ui_feature, config in self.config["ui"].items():
                if ui_feature != "description":
                    status = "🟢" if config else "🔴"
                    print(f"   {status} {ui_feature.replace('_', ' ').title()}")
            
            print("\n" + "="*60)
            print("TOGGLE OPTIONS:")
            print("1️⃣  Supply Chain Signals    2️⃣  Sentiment Analysis")
            print("3️⃣  Learning Engine         4️⃣  Profit Engine") 
            print("5️⃣  Ultra-Selective Mode    6️⃣  Maximum Conviction")
            print("7️⃣  Pattern Recognition     8️⃣  Random Learning")
            print("9️⃣  Show Emojis            0️⃣  Verbose Logging")
            print("📋 (s)tatus  💾 (e)xport  🔄 (r)eset  🧩 (p)atterns  ❌ (q)uit")
            
            choice = input("\n🎯 Select option: ").lower().strip()
            
            if choice == '1':
                self.toggle_feature("signals", "supply_chain")
            elif choice == '2':
                self.toggle_feature("signals", "sentiment")
            elif choice == '3':
                self.toggle_feature("engines", "learning_engine")
            elif choice == '4':
                self.toggle_feature("engines", "profit_engine")
            elif choice == '5':
                self.toggle_feature("trading", "ultra_selective")
            elif choice == '6':
                self.toggle_feature("trading", "maximum_conviction")
            elif choice == '7':
                self.toggle_feature("engines", "pattern_recognition")
            elif choice == '8':
                self.toggle_feature("trading", "random_learning")
            elif choice == '9':
                self.config["ui"]["show_emojis"] = not self.config["ui"]["show_emojis"]
                status = "🟢 ENABLED" if self.config["ui"]["show_emojis"] else "🔴 DISABLED"
                print(f"{status}: 🎨 Emoji Display")
                self.save_config()
            elif choice == '0':
                self.config["ui"]["verbose_logging"] = not self.config["ui"]["verbose_logging"]
                status = "🟢 ENABLED" if self.config["ui"]["verbose_logging"] else "🔴 DISABLED"
                print(f"{status}: 📝 Verbose Logging")
                self.save_config()
            elif choice == 's':
                self.print_detailed_status()
            elif choice == 'e':
                self.export_config()
            elif choice == 'r':
                self.reset_to_defaults()
            elif choice == 'p':
                self.launch_pattern_manager()
            elif choice == 'q':
                print("👋 Configuration saved! Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def print_detailed_status(self):
        """Print detailed status of all features"""
        print("\n" + "="*60)
        print("📊 DETAILED CONFIGURATION STATUS")
        print("="*60)
        
        for category, features in self.config.items():
            if category == "meta":
                continue
                
            print(f"\n🔧 {category.upper().replace('_', ' ')}:")
            
            for feature, config in features.items():
                if isinstance(config, dict):
                    status = "🟢 ON " if config.get("enabled", False) else "🔴 OFF"
                    desc = config.get("description", feature.replace('_', ' ').title())
                    print(f"   {status} | {desc}")
                    
                    # Show additional settings
                    for key, value in config.items():
                        if key not in ["enabled", "description"]:
                            print(f"         └─ {key}: {value}")
    
    def export_config(self):
        """Export current configuration"""
        timestamp = int(datetime.now().timestamp())
        export_file = f"benson_config_export_{timestamp}.json"
        
        try:
            with open(export_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"📤 Configuration exported to: {export_file}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        confirm = input("⚠️  Reset all settings to defaults? (y/N): ").lower()
        if confirm == 'y':
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            self.config = self.load_config()
            print("🔄 Configuration reset to defaults!")
    
    def launch_pattern_manager(self):
        """Launch the pattern management interface"""
        try:
            from pattern_manager import BensonPatternManager
            print("\n🧩 Launching Pattern Manager...")
            pattern_manager = BensonPatternManager()
            pattern_manager.interactive_pattern_menu()
        except ImportError:
            print("❌ Pattern Manager not available - please ensure pattern_manager.py exists")
        except Exception as e:
            print(f"❌ Error launching Pattern Manager: {e}")
    
    def get_config_for_trading(self) -> Dict[str, Any]:
        """Get configuration formatted for trading systems"""
        return {
            "supply_chain_enabled": self.get_feature_status("signals", "supply_chain"),
            "sentiment_enabled": self.get_feature_status("signals", "sentiment"),
            "learning_engine_enabled": self.get_feature_status("advanced", "learning_engine"),
            "profit_engine_enabled": self.get_feature_status("engines", "profit_engine"),
            "advanced_patterns_enabled": self.config["advanced"]["learning_engine"].get("advanced_patterns", False),
            "ultra_selective_enabled": self.get_feature_status("trading", "ultra_selective"),
            "maximum_conviction_enabled": self.get_feature_status("trading", "maximum_conviction"),
            "show_emojis": self.config["ui"]["show_emojis"],
            "verbose_logging": self.config["ui"]["verbose_logging"],
            
            # Feature-specific settings
            "confidence_threshold": self.config["trading"]["ultra_selective"].get("confidence_threshold", 70.0),
            "signal_threshold": self.config["trading"]["ultra_selective"].get("signal_threshold", 0.6),
            "max_position": self.config["trading"]["maximum_conviction"].get("max_position", 0.85),
            "supply_chain_sensitivity": self.config["signals"]["supply_chain"].get("sensitivity", 1.0),
        }


def main():
    """Interactive configuration interface"""
    print("🎛️  Welcome to Benson Bot Configuration Manager!")
    
    config_manager = BensonConfigManager()
    config_manager.interactive_config_menu()


if __name__ == "__main__":
    main()