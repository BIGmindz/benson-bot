#!/usr/bin/env python3
"""
Benson Bot Pattern Manager
Interactive system for managing, toggling, and training specific trading patterns
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from benson_config_manager import BensonConfigManager

@dataclass
class TradingPattern:
    """Represents a learned trading pattern"""
    pattern_id: str
    name: str
    description: str
    success_rate: float
    avg_return: float
    total_trades: int
    last_used: str
    confidence_threshold: float
    signal_requirements: Dict
    market_conditions: Dict
    enabled: bool = True
    priority: int = 1

class BensonPatternManager:
    """
    Manages trading patterns with granular control over which patterns are active
    """
    
    def __init__(self, db_path: str = "benson_patterns.db"):
        self.db_path = db_path
        self.config_manager = BensonConfigManager()
        self.patterns = {}
        self.init_pattern_database()
        self.load_patterns()
    
    def init_pattern_database(self):
        """Initialize or connect to pattern database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create pattern_library table for pattern management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_library (
                pattern_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                success_rate REAL DEFAULT 0.0,
                avg_return REAL DEFAULT 0.0,
                total_trades INTEGER DEFAULT 0,
                last_used TEXT,
                confidence_threshold REAL DEFAULT 70.0,
                signal_requirements TEXT,
                market_conditions TEXT,
                enabled INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 1,
                created_date TEXT,
                last_modified TEXT
            )
        ''')
        
        # Create pattern_performance table for tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT,
                trade_date TEXT,
                symbol TEXT,
                action TEXT,
                confidence REAL,
                return_pct REAL,
                success INTEGER,
                session_id TEXT,
                FOREIGN KEY (pattern_id) REFERENCES pattern_library (pattern_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def create_default_patterns(self):
        """Create default trading patterns based on successful strategies"""
        default_patterns = [
            TradingPattern(
                pattern_id="ultra_selective_rsi_oversold",
                name="Ultra-Selective RSI Oversold",
                description="High-confidence trades on severely oversold conditions (RSI < 20) with strong signal alignment",
                success_rate=0.78,
                avg_return=0.045,
                total_trades=0,
                last_used="never",
                confidence_threshold=85.0,
                signal_requirements={
                    "rsi_max": 20,
                    "sentiment_min": 0.3,
                    "supply_chain_min": 1.0,
                    "signal_alignment": 0.7
                },
                market_conditions={
                    "volatility": "high",
                    "trend": "any",
                    "volume": "above_average"
                },
                priority=1
            ),
            TradingPattern(
                pattern_id="maximum_conviction_breakout",
                name="Maximum Conviction Breakout",
                description="Perfect signal alignment for breakout trades with 95%+ confidence",
                success_rate=0.85,
                avg_return=0.065,
                total_trades=0,
                last_used="never", 
                confidence_threshold=95.0,
                signal_requirements={
                    "rsi_range": [25, 75],
                    "sentiment_min": 0.6,
                    "supply_chain_factor": 1.1,
                    "brazil_factor": 1.0,
                    "africa_factor": 1.0,
                    "signal_alignment": 0.8
                },
                market_conditions={
                    "volatility": "moderate",
                    "trend": "bullish",
                    "momentum": "strong"
                },
                priority=1
            ),
            TradingPattern(
                pattern_id="supply_chain_disruption",
                name="Supply Chain Disruption Play",
                description="Capitalize on supply chain signal spikes with regional factor confirmation",
                success_rate=0.72,
                avg_return=0.038,
                total_trades=0,
                last_used="never",
                confidence_threshold=75.0,
                signal_requirements={
                    "supply_chain_min": 1.15,
                    "regional_confirmation": True,
                    "sentiment_neutral": True
                },
                market_conditions={
                    "volatility": "any",
                    "trend": "any"
                },
                priority=2
            ),
            TradingPattern(
                pattern_id="contrarian_sentiment_reversal",
                name="Contrarian Sentiment Reversal",
                description="Fade extreme sentiment with technical confirmation",
                success_rate=0.68,
                avg_return=0.032,
                total_trades=0,
                last_used="never",
                confidence_threshold=70.0,
                signal_requirements={
                    "sentiment_extreme": True,
                    "rsi_divergence": True,
                    "volume_confirmation": True
                },
                market_conditions={
                    "volatility": "high",
                    "trend": "reversing"
                },
                priority=3,
                enabled=False  # Disabled by default - more advanced
            )
        ]
        
        # Save default patterns
        for pattern in default_patterns:
            self.save_pattern(pattern)
        
        print(f"✨ Created {len(default_patterns)} default trading patterns")
    
    def save_pattern(self, pattern: TradingPattern):
        """Save pattern to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO pattern_library (
                pattern_id, name, description, success_rate, avg_return,
                total_trades, last_used, confidence_threshold,
                signal_requirements, market_conditions, enabled, priority,
                created_date, last_modified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.pattern_id, pattern.name, pattern.description,
            pattern.success_rate, pattern.avg_return, pattern.total_trades,
            pattern.last_used, pattern.confidence_threshold,
            json.dumps(pattern.signal_requirements),
            json.dumps(pattern.market_conditions),
            1 if pattern.enabled else 0, pattern.priority,
            now, now
        ))
        
        conn.commit()
        conn.close()
        
        self.patterns[pattern.pattern_id] = pattern
    
    def load_patterns(self):
        """Load all patterns from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM pattern_library')
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📚 No patterns found - creating default patterns...")
            self.create_default_patterns()
            conn.close()
            return
        
        cursor.execute('SELECT * FROM pattern_library ORDER BY priority, name')
        rows = cursor.fetchall()
        
        self.patterns = {}
        for row in rows:
            pattern = TradingPattern(
                pattern_id=row[0],
                name=row[1],
                description=row[2],
                success_rate=row[3],
                avg_return=row[4],
                total_trades=row[5],
                last_used=row[6],
                confidence_threshold=row[7],
                signal_requirements=json.loads(row[8]) if row[8] else {},
                market_conditions=json.loads(row[9]) if row[9] else {},
                enabled=bool(row[10]),
                priority=row[11]
            )
            self.patterns[pattern.pattern_id] = pattern
        
        conn.close()
        print(f"📚 Loaded {len(self.patterns)} trading patterns")
    
    def toggle_pattern(self, pattern_id: str) -> bool:
        """Toggle a pattern on/off"""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.enabled = not pattern.enabled
            self.save_pattern(pattern)
            
            status = "🟢 ENABLED" if pattern.enabled else "🔴 DISABLED"
            print(f"{status}: {pattern.name}")
            return pattern.enabled
        else:
            print(f"❌ Pattern '{pattern_id}' not found")
            return False
    
    def get_active_patterns(self) -> List[TradingPattern]:
        """Get list of currently enabled patterns"""
        return [p for p in self.patterns.values() if p.enabled]
    
    def get_pattern_stats(self) -> Dict:
        """Get pattern statistics"""
        total_patterns = len(self.patterns)
        active_patterns = len(self.get_active_patterns())
        avg_success_rate = sum(p.success_rate for p in self.patterns.values()) / total_patterns if total_patterns > 0 else 0
        
        return {
            'total_patterns': total_patterns,
            'active_patterns': active_patterns,
            'inactive_patterns': total_patterns - active_patterns,
            'avg_success_rate': avg_success_rate,
            'top_performer': max(self.patterns.values(), key=lambda p: p.success_rate) if self.patterns else None
        }
    
    def train_pattern(self, pattern_id: str, trades_data: List[Dict]):
        """Train/update a pattern with new trade data"""
        if pattern_id not in self.patterns:
            print(f"❌ Pattern '{pattern_id}' not found")
            return
        
        pattern = self.patterns[pattern_id]
        
        # Analyze trades that match this pattern
        matching_trades = []
        for trade in trades_data:
            if self.trade_matches_pattern(trade, pattern):
                matching_trades.append(trade)
        
        if not matching_trades:
            print(f"⚠️  No trades match pattern '{pattern.name}'")
            return
        
        # Update pattern statistics
        successful_trades = [t for t in matching_trades if t.get('success', False)]
        old_total = pattern.total_trades
        old_success_rate = pattern.success_rate
        
        pattern.total_trades += len(matching_trades)
        pattern.success_rate = len(successful_trades) / len(matching_trades)
        pattern.avg_return = sum(t.get('return_pct', 0) for t in successful_trades) / len(successful_trades) if successful_trades else 0
        pattern.last_used = datetime.now().isoformat()
        
        # Save updated pattern
        self.save_pattern(pattern)
        
        # Record performance
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for trade in matching_trades:
            cursor.execute('''
                INSERT INTO pattern_performance (
                    pattern_id, trade_date, symbol, action, confidence,
                    return_pct, success, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_id, trade.get('timestamp', ''), trade.get('symbol', ''),
                trade.get('action', ''), trade.get('confidence', 0),
                trade.get('return_pct', 0), 1 if trade.get('success') else 0,
                trade.get('session_id', '')
            ))
        conn.commit()
        conn.close()
        
        print(f"🎯 Pattern '{pattern.name}' trained:")
        print(f"   • New trades: {len(matching_trades)} (was {old_total}, now {pattern.total_trades})")
        print(f"   • Success rate: {pattern.success_rate:.1%} (was {old_success_rate:.1%})")
        print(f"   • Avg return: {pattern.avg_return:.2%}")
    
    def trade_matches_pattern(self, trade: Dict, pattern: TradingPattern) -> bool:
        """Check if a trade matches a pattern's requirements"""
        # Check confidence threshold
        if trade.get('confidence', 0) < pattern.confidence_threshold:
            return False
        
        # Check signal requirements
        reqs = pattern.signal_requirements
        
        if 'rsi_max' in reqs and trade.get('rsi', 100) > reqs['rsi_max']:
            return False
            
        if 'rsi_min' in reqs and trade.get('rsi', 0) < reqs['rsi_min']:
            return False
            
        if 'sentiment_min' in reqs and trade.get('sentiment', 0) < reqs['sentiment_min']:
            return False
            
        if 'supply_chain_min' in reqs and trade.get('supply_chain_factor', 0) < reqs['supply_chain_min']:
            return False
        
        return True
    
    def interactive_pattern_menu(self):
        """Interactive menu for pattern management"""
        while True:
            print("\n" + "="*60)
            print("🧩 BENSON BOT - PATTERN MANAGER")
            print("="*60)
            
            # Display current patterns
            stats = self.get_pattern_stats()
            print(f"\n📊 PATTERN OVERVIEW:")
            print(f"   • Total Patterns: {stats['total_patterns']}")
            print(f"   • Active Patterns: {stats['active_patterns']}")
            print(f"   • Average Success Rate: {stats['avg_success_rate']:.1%}")
            
            print(f"\n🧩 AVAILABLE PATTERNS:")
            for i, (pattern_id, pattern) in enumerate(self.patterns.items(), 1):
                status = "🟢" if pattern.enabled else "🔴"
                priority = "⭐" * pattern.priority
                print(f"   {i}. {status} {pattern.name} {priority}")
                print(f"      └─ Success: {pattern.success_rate:.1%} | Return: {pattern.avg_return:.2%} | Trades: {pattern.total_trades}")
            
            print("\n" + "="*60)
            print("PATTERN OPTIONS:")
            print("🔄 (1-9) Toggle Pattern    📈 (t) Train Pattern")  
            print("📊 (s) Detailed Stats      ➕ (n) New Pattern")
            print("🗑️  (d) Delete Pattern     💾 (e) Export Patterns")
            print("❌ (q) Quit")
            
            choice = input("\n🎯 Select option: ").lower().strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(self.patterns):
                pattern_id = list(self.patterns.keys())[int(choice) - 1]
                self.toggle_pattern(pattern_id)
            elif choice == 't':
                self.train_pattern_interactive()
            elif choice == 's':
                self.show_detailed_stats()
            elif choice == 'n':
                self.create_new_pattern()
            elif choice == 'd':
                self.delete_pattern_interactive()
            elif choice == 'e':
                self.export_patterns()
            elif choice == 'q':
                print("👋 Pattern management complete!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def show_detailed_stats(self):
        """Show detailed statistics for all patterns"""
        print("\n" + "="*80)
        print("📊 DETAILED PATTERN STATISTICS")
        print("="*80)
        
        for pattern in self.patterns.values():
            status = "🟢 ACTIVE" if pattern.enabled else "🔴 INACTIVE"
            print(f"\n🧩 {pattern.name} ({status})")
            print(f"   Description: {pattern.description}")
            print(f"   Performance: {pattern.success_rate:.1%} success rate, {pattern.avg_return:.2%} avg return")
            print(f"   Usage: {pattern.total_trades} trades, last used {pattern.last_used}")
            print(f"   Requirements: Confidence ≥{pattern.confidence_threshold}%")
            
            # Show signal requirements
            if pattern.signal_requirements:
                print("   Signal Requirements:")
                for key, value in pattern.signal_requirements.items():
                    print(f"     • {key}: {value}")
    
    def train_pattern_interactive(self):
        """Interactive pattern training"""
        print("\n🎯 PATTERN TRAINING")
        print("Available patterns:")
        for i, (pattern_id, pattern) in enumerate(self.patterns.items(), 1):
            print(f"   {i}. {pattern.name}")
        
        try:
            choice = int(input("Select pattern to train (number): "))
            if 1 <= choice <= len(self.patterns):
                pattern_id = list(self.patterns.keys())[choice - 1]
                print(f"🎯 Training pattern: {self.patterns[pattern_id].name}")
                print("📚 (Training requires trade data - integrate with trading session)")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def create_new_pattern(self):
        """Create a new custom pattern"""
        print("\n➕ CREATE NEW PATTERN")
        print("(Feature coming soon - advanced pattern creation)")
    
    def delete_pattern_interactive(self):
        """Interactive pattern deletion"""
        print("\n🗑️  DELETE PATTERN")
        print("Available patterns:")
        for i, (pattern_id, pattern) in enumerate(self.patterns.items(), 1):
            print(f"   {i}. {pattern.name}")
        
        try:
            choice = int(input("Select pattern to delete (number): "))
            if 1 <= choice <= len(self.patterns):
                pattern_id = list(self.patterns.keys())[choice - 1]
                confirm = input(f"❓ Delete '{self.patterns[pattern_id].name}'? (y/N): ")
                if confirm.lower() == 'y':
                    self.delete_pattern(pattern_id)
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def delete_pattern(self, pattern_id: str):
        """Delete a pattern"""
        if pattern_id in self.patterns:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM pattern_library WHERE pattern_id = ?', (pattern_id,))
            cursor.execute('DELETE FROM pattern_performance WHERE pattern_id = ?', (pattern_id,))
            conn.commit()
            conn.close()
            
            pattern_name = self.patterns[pattern_id].name
            del self.patterns[pattern_id]
            print(f"🗑️  Deleted pattern: {pattern_name}")
        else:
            print(f"❌ Pattern '{pattern_id}' not found")
    
    def export_patterns(self):
        """Export patterns to JSON file"""
        timestamp = int(datetime.now().timestamp())
        filename = f"benson_patterns_export_{timestamp}.json"
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_patterns': len(self.patterns),
            'patterns': {}
        }
        
        for pattern_id, pattern in self.patterns.items():
            export_data['patterns'][pattern_id] = {
                'name': pattern.name,
                'description': pattern.description,
                'success_rate': pattern.success_rate,
                'avg_return': pattern.avg_return,
                'total_trades': pattern.total_trades,
                'enabled': pattern.enabled,
                'confidence_threshold': pattern.confidence_threshold,
                'signal_requirements': pattern.signal_requirements,
                'market_conditions': pattern.market_conditions
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📤 Patterns exported to: {filename}")

def main():
    """Interactive pattern management interface"""
    print("🧩 Welcome to Benson Bot Pattern Manager!")
    
    pattern_manager = BensonPatternManager()
    pattern_manager.interactive_pattern_menu()

if __name__ == "__main__":
    main()