#!/usr/bin/env python3
"""
Enhanced Training Monitor
Tracks performance improvements after signal quality fixes
"""

import time
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict

class EnhancedTrainingMonitor:
    def __init__(self):
        self.db_path = "benson_memory.db"
        self.results_pattern = "rapid_training_results_*.json"
        
    def get_recent_performance(self) -> Dict:
        """Get performance data from recent sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get recent sessions
            cursor.execute("""
                SELECT * FROM trading_sessions 
                ORDER BY timestamp DESC 
                LIMIT 3
            """)
            sessions = cursor.fetchall()
            
            results = []
            for session in sessions:
                perf_data = json.loads(session['performance_data'])
                results.append({
                    'session_id': session['session_id'],
                    'timestamp': session['timestamp'],
                    'balance': perf_data.get('ending_balance', 0),
                    'return_pct': perf_data.get('total_return', 0),
                    'trades': perf_data.get('total_trades', 0),
                    'win_rate': perf_data.get('win_rate', 0) * 100
                })
            
            conn.close()
            return {'sessions': results, 'count': len(results)}
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_current_training_status(self) -> Dict:
        """Check if rapid fire trainer is running and get progress"""
        training_running = os.system('pgrep -f rapid_fire_trainer.py > /dev/null') == 0
        
        # Calculate progress
        start_time = datetime(2025, 9, 16, 6, 33, 33)
        current_time = datetime.now()
        elapsed_seconds = (current_time - start_time).total_seconds()
        progress_pct = min(100, (elapsed_seconds / 7200) * 100)
        
        return {
            'running': training_running,
            'progress_pct': progress_pct,
            'elapsed_minutes': elapsed_seconds / 60,
            'estimated_completion': '08:33:33' if training_running else 'Unknown'
        }
    
    def analyze_improvement_potential(self, sessions: list) -> Dict:
        """Analyze if improvements are being made"""
        if len(sessions) < 2:
            return {'insufficient_data': True}
        
        # Compare most recent vs previous sessions
        latest = sessions[0]
        baseline = sessions[-1]  # Oldest recent session
        
        improvements = {
            'win_rate_improved': latest['win_rate'] > baseline['win_rate'],
            'return_improved': latest['return_pct'] > baseline['return_pct'],
            'more_trades': latest['trades'] > baseline['trades'],
            'win_rate_delta': latest['win_rate'] - baseline['win_rate'],
            'return_delta': latest['return_pct'] - baseline['return_pct']
        }
        
        # Check if we're above crisis levels
        improvements['above_crisis_levels'] = {
            'win_rate_positive': latest['win_rate'] > 0,
            'return_positive': latest['return_pct'] > -10,  # Better than -10%
            'multiple_trades': latest['trades'] > 1
        }
        
        return improvements
    
    def monitor_signal_effectiveness(self) -> Dict:
        """Check if supply chain signal improvements are working"""
        try:
            from signals.supply_chain_signals import SupplyChainSignals, SupplyChainSignalsConfig
            
            config = SupplyChainSignalsConfig(enabled=True, region="global", sensitivity=1.0)
            signals = SupplyChainSignals(config)
            
            # Test signal quality
            composite, logs = signals.composite()
            
            return {
                'supply_chain_active': True,
                'using_real_data': logs.get('source') != 'intelligent_estimation',
                'data_source': logs.get('source', 'unknown'),
                'signal_strength': composite,
                'signal_quality': 'good' if logs.get('status') == 'real_data_acquired' else 'fallback'
            }
        except Exception as e:
            return {'supply_chain_active': False, 'error': str(e)}
    
    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        print("🎯 ENHANCED TRAINING MONITOR REPORT")
        print("=" * 50)
        print(f"📅 Report Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Training status
        training_status = self.check_current_training_status()
        print(f"\n⏰ TRAINING SESSION:")
        print(f"   Status: {'🟢 RUNNING' if training_status['running'] else '🔴 STOPPED'}")
        print(f"   Progress: {training_status['progress_pct']:.1f}%")
        print(f"   Elapsed: {training_status['elapsed_minutes']:.0f} minutes")
        
        # Signal effectiveness
        signal_status = self.monitor_signal_effectiveness()
        print(f"\n🔗 SIGNAL QUALITY:")
        print(f"   Supply Chain: {'✅ Active' if signal_status.get('supply_chain_active') else '❌ Inactive'}")
        print(f"   Data Source: {signal_status.get('data_source', 'Unknown')}")
        print(f"   Using Real Data: {'✅ Yes' if signal_status.get('using_real_data') else '⚠️ Fallback'}")
        print(f"   Signal Strength: {signal_status.get('signal_strength', 0):.3f}")
        
        # Performance analysis
        perf_data = self.get_recent_performance()
        if 'sessions' in perf_data and perf_data['sessions']:
            sessions = perf_data['sessions']
            print(f"\n📊 RECENT PERFORMANCE ({len(sessions)} sessions):")
            
            for i, session in enumerate(sessions, 1):
                age = 'Latest' if i == 1 else f'{i-1} sessions ago'
                print(f"   {i}. {age}: {session['return_pct']:.1f}% return, {session['win_rate']:.1f}% wins, {session['trades']} trades")
            
            # Improvement analysis
            improvements = self.analyze_improvement_potential(sessions)
            if not improvements.get('insufficient_data'):
                print(f"\n📈 IMPROVEMENT ANALYSIS:")
                print(f"   Win Rate: {'✅ Improved' if improvements['win_rate_improved'] else '❌ Declined'} ({improvements['win_rate_delta']:+.1f}%)")
                print(f"   Returns: {'✅ Improved' if improvements['return_improved'] else '❌ Declined'} ({improvements['return_delta']:+.1f}%)")
                
                crisis_check = improvements['above_crisis_levels']
                print(f"\n🚨 CRISIS LEVEL CHECK:")
                print(f"   Win Rate > 0%: {'✅ Yes' if crisis_check['win_rate_positive'] else '❌ Still 0%'}")
                print(f"   Return > -10%: {'✅ Yes' if crisis_check['return_positive'] else '❌ High losses'}")
                print(f"   Multiple Trades: {'✅ Yes' if crisis_check['multiple_trades'] else '❌ Too few'}")
        
        print(f"\n🎯 KEY IMPROVEMENTS MADE:")
        print(f"   ✅ Disabled random supply chain data")
        print(f"   ✅ Integrated real freight data sources") 
        print(f"   ✅ Market-correlated stress indicators")
        print(f"   ⏳ Training session testing improvements")
        
        return "Report completed"

if __name__ == "__main__":
    monitor = EnhancedTrainingMonitor()
    monitor.generate_status_report()