#!/usr/bin/env python3
"""
📊 BENSON PATTERN ANALYTICS SERVICE
Advanced performance tracking, backtesting, and analytics dashboard
Real-time pattern performance monitoring for enterprise clients

Features:
- Real-time pattern performance tracking
- Advanced backtesting engine with risk metrics
- Pattern comparison and optimization
- Performance degradation alerts
- Revenue analytics and forecasting
- Interactive dashboards and reports

Author: Benson Trading Systems
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Optional imports for advanced analytics
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

@dataclass
class PatternMetrics:
    """Performance metrics for a trading pattern"""
    pattern_id: str
    name: str
    total_trades: int
    win_rate: float
    avg_return: float
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    profit_factor: float
    avg_trade_duration: float
    volatility: float
    beta: float
    alpha: float
    calmar_ratio: float
    recovery_factor: float

class PatternAnalytics:
    """📊 Advanced pattern performance analytics and tracking"""
    
    def __init__(self):
        """Initialize analytics engine with comprehensive tracking"""
        self.db_path = 'benson_analytics.db'
        self.init_analytics_database()
        self.performance_cache = {}
        
        print("📊 Pattern Analytics Service initialized!")
    
    def init_analytics_database(self):
        """Initialize analytics database with comprehensive schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pattern performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                symbol TEXT,
                action TEXT,
                entry_price REAL,
                exit_price REAL,
                position_size REAL,
                return_pct REAL,
                duration_minutes INTEGER,
                confidence REAL,
                signal_strength REAL,
                market_conditions TEXT,
                volatility REAL,
                volume REAL
            )
        ''')
        
        # Daily pattern metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                date TEXT NOT NULL,
                trades_count INTEGER,
                win_rate REAL,
                avg_return REAL,
                total_return REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                profit_factor REAL,
                revenue_generated REAL,
                UNIQUE(pattern_id, date)
            )
        ''')
        
        # Pattern comparisons
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comparison_id TEXT,
                pattern_ids TEXT,
                comparison_date TEXT,
                metrics_comparison TEXT,
                recommendation TEXT
            )
        ''')
        
        # Performance alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT,
                message TEXT,
                created_date TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        print("📈 Analytics database schema initialized")
    
    def record_trade_result(self, pattern_id: str, trade_data: Dict) -> None:
        """📝 Record a completed trade for pattern analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pattern_performance
            (pattern_id, timestamp, symbol, action, entry_price, exit_price, 
             position_size, return_pct, duration_minutes, confidence, signal_strength,
             market_conditions, volatility, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            datetime.now().isoformat(),
            trade_data.get('symbol', 'UNKNOWN'),
            trade_data.get('action', 'UNKNOWN'),
            trade_data.get('entry_price', 0),
            trade_data.get('exit_price', 0),
            trade_data.get('position_size', 0),
            trade_data.get('return_pct', 0),
            trade_data.get('duration_minutes', 0),
            trade_data.get('confidence', 0.5),
            trade_data.get('signal_strength', 0.5),
            trade_data.get('market_conditions', 'normal'),
            trade_data.get('volatility', 0),
            trade_data.get('volume', 0)
        ))
        
        conn.commit()
        conn.close()
        
        # Update daily metrics
        self.update_daily_metrics(pattern_id)
        
        # Check for performance alerts
        self.check_performance_alerts(pattern_id)
    
    def calculate_pattern_metrics(self, pattern_id: str, days: int = 30) -> PatternMetrics:
        """🧮 Calculate comprehensive performance metrics for a pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get trade data
        query = '''
            SELECT return_pct, duration_minutes FROM pattern_performance 
            WHERE pattern_id = ? AND timestamp > datetime('now', '-{} days')
            ORDER BY timestamp DESC
        '''.format(days)
        
        cursor.execute(query, (pattern_id,))
        trades = cursor.fetchall()
        conn.close()
        
        if not trades:
            return None
        
        # Convert to lists for processing
        returns = [float(trade[0]) for trade in trades]
        durations = [float(trade[1]) for trade in trades]
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = len([r for r in returns if r > 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        avg_return = sum(returns) / len(returns) if returns else 0
        total_return = sum(returns)
        
        # Risk metrics
        returns_array = np.array(returns)
        max_drawdown = self.calculate_max_drawdown(returns_array)
        volatility = np.std(returns_array) * np.sqrt(252) if len(returns_array) > 1 else 0
        
        # Ratios
        sharpe_ratio = self.calculate_sharpe_ratio(returns_array)
        sortino_ratio = self.calculate_sortino_ratio(returns_array)
        profit_factor = self.calculate_profit_factor(returns_array)
        calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Other metrics
        avg_trade_duration = sum(durations) / len(durations) if durations else 0
        
        # Get pattern name
        pattern_name = self.get_pattern_name(pattern_id)
        
        return PatternMetrics(
            pattern_id=pattern_id,
            name=pattern_name,
            total_trades=total_trades,
            win_rate=win_rate,
            avg_return=avg_return,
            total_return=total_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            profit_factor=profit_factor,
            avg_trade_duration=avg_trade_duration,
            volatility=volatility,
            beta=0.0,  # Would calculate vs market benchmark
            alpha=avg_return - 0.02,  # Alpha vs risk-free rate
            calmar_ratio=calmar_ratio,
            recovery_factor=total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        )
    
    def calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """📉 Calculate maximum drawdown from returns series"""
        if len(returns) == 0:
            return 0.0
        
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return float(np.min(drawdown))
    
    def calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """📊 Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - risk_free_rate/252
        return float(np.mean(excess_returns) / np.std(returns) * np.sqrt(252))
    
    def calculate_sortino_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """📈 Calculate Sortino ratio (downside deviation)"""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - risk_free_rate/252
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_deviation = np.std(downside_returns) * np.sqrt(252)
        return float(np.mean(excess_returns) * 252 / downside_deviation)
    
    def calculate_profit_factor(self, returns: np.ndarray) -> float:
        """💰 Calculate profit factor (gross profits / gross losses)"""
        profits = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        
        return float(profits / losses) if losses != 0 else float('inf')
    
    def get_pattern_name(self, pattern_id: str) -> str:
        """Get pattern name from marketplace database"""
        try:
            conn = sqlite3.connect('benson_marketplace.db')
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM pattern_listings WHERE pattern_id = ?', (pattern_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else f"Pattern_{pattern_id[:8]}"
        except:
            return f"Pattern_{pattern_id[:8]}"
    
    def update_daily_metrics(self, pattern_id: str) -> None:
        """📅 Update daily aggregated metrics"""
        today = datetime.now().date().isoformat()
        metrics = self.calculate_pattern_metrics(pattern_id, days=1)
        
        if not metrics:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_metrics
            (pattern_id, date, trades_count, win_rate, avg_return, total_return,
             max_drawdown, sharpe_ratio, profit_factor, revenue_generated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id, today, metrics.total_trades, metrics.win_rate,
            metrics.avg_return, metrics.total_return, metrics.max_drawdown,
            metrics.sharpe_ratio, metrics.profit_factor, 
            metrics.total_return * 1000  # Simulate revenue calculation
        ))
        
        conn.commit()
        conn.close()
    
    def check_performance_alerts(self, pattern_id: str) -> None:
        """🚨 Check for performance degradation alerts"""
        metrics = self.calculate_pattern_metrics(pattern_id, days=7)
        if not metrics:
            return
        
        alerts = []
        
        # Performance degradation alerts
        if metrics.win_rate < 0.4:
            alerts.append({
                'type': 'low_win_rate',
                'severity': 'HIGH',
                'message': f'Win rate dropped to {metrics.win_rate:.1%} (below 40%)'
            })
        
        if metrics.max_drawdown < -0.15:
            alerts.append({
                'type': 'high_drawdown',
                'severity': 'HIGH',
                'message': f'Maximum drawdown reached {metrics.max_drawdown:.1%} (exceeds 15%)'
            })
        
        if metrics.sharpe_ratio < 0.5:
            alerts.append({
                'type': 'low_sharpe',
                'severity': 'MEDIUM',
                'message': f'Sharpe ratio declined to {metrics.sharpe_ratio:.2f} (below 0.5)'
            })
        
        # Record alerts
        if alerts:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for alert in alerts:
                cursor.execute('''
                    INSERT INTO performance_alerts
                    (pattern_id, alert_type, severity, message, created_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (pattern_id, alert['type'], alert['severity'], 
                      alert['message'], datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
    
    def compare_patterns(self, pattern_ids: List[str], days: int = 30) -> Dict:
        """⚖️ Compare multiple patterns performance"""
        comparison_results = {}
        pattern_metrics = []
        
        for pattern_id in pattern_ids:
            metrics = self.calculate_pattern_metrics(pattern_id, days)
            if metrics:
                pattern_metrics.append(metrics)
        
        if len(pattern_metrics) < 2:
            return {"error": "Need at least 2 patterns for comparison"}
        
        # Create comparison matrix
        comparison_data = []
        for metrics in pattern_metrics:
            comparison_data.append({
                'Name': metrics.name,
                'Win Rate': f"{metrics.win_rate:.1%}",
                'Avg Return': f"{metrics.avg_return:.2%}",
                'Total Return': f"{metrics.total_return:.2%}",
                'Max Drawdown': f"{metrics.max_drawdown:.2%}",
                'Sharpe Ratio': f"{metrics.sharpe_ratio:.2f}",
                'Profit Factor': f"{metrics.profit_factor:.2f}",
                'Total Trades': metrics.total_trades
            })
        
        # Determine best pattern for each metric
        best_metrics = {
            'highest_win_rate': max(pattern_metrics, key=lambda x: x.win_rate),
            'highest_return': max(pattern_metrics, key=lambda x: x.total_return),
            'best_sharpe': max(pattern_metrics, key=lambda x: x.sharpe_ratio),
            'lowest_drawdown': max(pattern_metrics, key=lambda x: -x.max_drawdown),
            'best_profit_factor': max(pattern_metrics, key=lambda x: x.profit_factor)
        }
        
        # Overall recommendation
        scores = {}
        for metrics in pattern_metrics:
            score = (
                metrics.win_rate * 0.25 +
                metrics.total_return * 0.25 +
                metrics.sharpe_ratio * 0.2 +
                (-metrics.max_drawdown) * 0.15 +
                min(metrics.profit_factor, 10) * 0.15
            )
            scores[metrics.pattern_id] = score
        
        best_overall = max(scores.items(), key=lambda x: x[1])
        
        comparison_results = {
            'comparison_data': comparison_data,
            'best_metrics': {
                'win_rate': best_metrics['highest_win_rate'].name,
                'return': best_metrics['highest_return'].name,
                'sharpe_ratio': best_metrics['best_sharpe'].name,
                'drawdown': best_metrics['lowest_drawdown'].name,
                'profit_factor': best_metrics['best_profit_factor'].name
            },
            'overall_recommendation': self.get_pattern_name(best_overall[0]),
            'recommendation_score': best_overall[1]
        }
        
        return comparison_results
    
    def generate_performance_report(self, pattern_id: str, days: int = 30) -> Dict:
        """📋 Generate comprehensive performance report"""
        metrics = self.calculate_pattern_metrics(pattern_id, days)
        if not metrics:
            return {"error": "No data available for this pattern"}
        
        # Get recent alerts
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT alert_type, severity, message, created_date
            FROM performance_alerts
            WHERE pattern_id = ? AND created_date > datetime('now', '-7 days')
            ORDER BY created_date DESC
            LIMIT 5
        ''', (pattern_id,))
        recent_alerts = cursor.fetchall()
        conn.close()
        
        # Performance grade
        grade = self.calculate_performance_grade(metrics)
        
        report = {
            'pattern_name': metrics.name,
            'analysis_period': f'{days} days',
            'performance_grade': grade,
            'key_metrics': {
                'total_trades': metrics.total_trades,
                'win_rate': f"{metrics.win_rate:.1%}",
                'avg_return_per_trade': f"{metrics.avg_return:.2%}",
                'total_return': f"{metrics.total_return:.2%}",
                'max_drawdown': f"{metrics.max_drawdown:.2%}",
                'sharpe_ratio': metrics.sharpe_ratio,
                'profit_factor': metrics.profit_factor
            },
            'risk_metrics': {
                'volatility': f"{metrics.volatility:.2%}",
                'sortino_ratio': metrics.sortino_ratio,
                'calmar_ratio': metrics.calmar_ratio,
                'recovery_factor': metrics.recovery_factor
            },
            'recent_alerts': [
                {
                    'type': alert[0],
                    'severity': alert[1],
                    'message': alert[2],
                    'date': alert[3]
                } for alert in recent_alerts
            ],
            'recommendations': self.generate_recommendations(metrics)
        }
        
        return report
    
    def calculate_performance_grade(self, metrics: PatternMetrics) -> str:
        """🎯 Calculate performance grade A-F"""
        score = 0
        
        # Win rate scoring (0-25 points)
        if metrics.win_rate >= 0.7:
            score += 25
        elif metrics.win_rate >= 0.6:
            score += 20
        elif metrics.win_rate >= 0.5:
            score += 15
        else:
            score += max(0, metrics.win_rate * 30)
        
        # Return scoring (0-25 points)
        annual_return = metrics.total_return * (365/30)  # Annualized
        if annual_return >= 0.5:
            score += 25
        elif annual_return >= 0.3:
            score += 20
        elif annual_return >= 0.15:
            score += 15
        else:
            score += max(0, annual_return * 50)
        
        # Sharpe ratio scoring (0-25 points)
        if metrics.sharpe_ratio >= 2.0:
            score += 25
        elif metrics.sharpe_ratio >= 1.5:
            score += 20
        elif metrics.sharpe_ratio >= 1.0:
            score += 15
        else:
            score += max(0, metrics.sharpe_ratio * 12.5)
        
        # Drawdown scoring (0-25 points)
        if metrics.max_drawdown >= -0.05:
            score += 25
        elif metrics.max_drawdown >= -0.1:
            score += 20
        elif metrics.max_drawdown >= -0.15:
            score += 15
        else:
            score += max(0, (0.25 + metrics.max_drawdown) * 100)
        
        # Convert to letter grade
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        elif score >= 45:
            return "D"
        else:
            return "F"
    
    def generate_recommendations(self, metrics: PatternMetrics) -> List[str]:
        """💡 Generate actionable recommendations"""
        recommendations = []
        
        if metrics.win_rate < 0.5:
            recommendations.append("Consider refining entry criteria to improve win rate")
        
        if metrics.max_drawdown < -0.1:
            recommendations.append("Implement stricter position sizing to reduce drawdown risk")
        
        if metrics.sharpe_ratio < 1.0:
            recommendations.append("Evaluate risk-adjusted returns - consider reducing position sizes")
        
        if metrics.avg_trade_duration > 1440:  # More than 24 hours
            recommendations.append("Consider faster exit strategies to reduce holding time")
        
        if metrics.profit_factor < 1.5:
            recommendations.append("Review stop-loss and take-profit levels to improve profit factor")
        
        if not recommendations:
            recommendations.append("Pattern is performing well - continue monitoring")
        
        return recommendations

if __name__ == "__main__":
    # Initialize analytics service
    analytics = PatternAnalytics()
    
    print("📊 PATTERN ANALYTICS SERVICE DEMO")
    print("="*50)
    
    # Simulate some trade data for demo
    demo_pattern_id = "pattern_001"
    
    # Record some demo trades
    demo_trades = [
        {'symbol': 'BTC/USD', 'action': 'BUY', 'entry_price': 45000, 'exit_price': 46500, 'position_size': 0.1, 'return_pct': 0.033, 'duration_minutes': 120, 'confidence': 0.85, 'signal_strength': 0.7},
        {'symbol': 'ETH/USD', 'action': 'BUY', 'entry_price': 3200, 'exit_price': 3150, 'position_size': 0.15, 'return_pct': -0.016, 'duration_minutes': 90, 'confidence': 0.75, 'signal_strength': 0.6},
        {'symbol': 'BTC/USD', 'action': 'SELL', 'entry_price': 44000, 'exit_price': 45200, 'position_size': 0.08, 'return_pct': -0.027, 'duration_minutes': 180, 'confidence': 0.70, 'signal_strength': 0.65},
        {'symbol': 'SOL/USD', 'action': 'BUY', 'entry_price': 180, 'exit_price': 192, 'position_size': 0.12, 'return_pct': 0.067, 'duration_minutes': 240, 'confidence': 0.90, 'signal_strength': 0.8},
        {'symbol': 'BTC/USD', 'action': 'BUY', 'entry_price': 46500, 'exit_price': 48200, 'position_size': 0.2, 'return_pct': 0.037, 'duration_minutes': 300, 'confidence': 0.88, 'signal_strength': 0.75}
    ]
    
    for trade in demo_trades:
        analytics.record_trade_result(demo_pattern_id, trade)
    
    print("✅ Recorded 5 demo trades")
    
    # Calculate metrics
    metrics = analytics.calculate_pattern_metrics(demo_pattern_id)
    if metrics:
        print(f"\n📈 PATTERN METRICS FOR {metrics.name}")
        print(f"  Total Trades: {metrics.total_trades}")
        print(f"  Win Rate: {metrics.win_rate:.1%}")
        print(f"  Average Return: {metrics.avg_return:.2%}")
        print(f"  Total Return: {metrics.total_return:.2%}")
        print(f"  Max Drawdown: {metrics.max_drawdown:.2%}")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"  Profit Factor: {metrics.profit_factor:.2f}")
    
    # Generate performance report
    print(f"\n📋 PERFORMANCE REPORT")
    report = analytics.generate_performance_report(demo_pattern_id)
    print(f"  Performance Grade: {report['performance_grade']}")
    print(f"  Key Recommendations:")
    for rec in report['recommendations']:
        print(f"    • {rec}")
    
    print("\n🎯 Pattern Analytics Service ready for enterprise monitoring!")