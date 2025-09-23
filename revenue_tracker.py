#!/usr/bin/env python3
"""
💰 BENSON REVENUE TRACKING SYSTEM
Comprehensive billing, revenue sharing, and financial analytics for Patterns as a Service

Features:
- Usage-based billing and subscription management
- Automated revenue sharing with pattern creators
- Financial analytics and reporting
- Tax compliance and reporting
- Payment processing integration
- Revenue forecasting and optimization

Revenue Streams:
- Pattern subscriptions ($9.99-$199.99/month)
- API calls ($0.01-$0.10 per call)  
- Custom pattern creation ($499-$2999)
- Enterprise data integration ($299-$4999/month)
- Professional services ($5000-$50000)

Author: Benson Trading Systems
"""

import sqlite3
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid
import calendar
from decimal import Decimal, ROUND_HALF_UP

@dataclass
class RevenueStream:
    """Individual revenue stream tracking"""
    stream_id: str
    stream_type: str  # 'subscription', 'api_usage', 'custom_pattern', 'enterprise', 'services'
    customer_id: str
    pattern_id: Optional[str]
    amount: float
    currency: str
    billing_period: str  # 'monthly', 'annual', 'one-time', 'usage-based'
    start_date: datetime
    end_date: Optional[datetime]
    status: str  # 'active', 'cancelled', 'paused', 'completed'
    creator_share_rate: float
    platform_share_rate: float

@dataclass
class PaymentTransaction:
    """Payment transaction record"""
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    transaction_type: str  # 'charge', 'refund', 'payout'
    payment_method: str
    status: str  # 'pending', 'completed', 'failed'
    created_date: datetime
    processed_date: Optional[datetime]
    fees: float
    net_amount: float

class RevenueTracker:
    """💰 Comprehensive revenue tracking and billing system"""
    
    def __init__(self):
        """Initialize revenue tracking system"""
        self.db_path = 'benson_revenue.db'
        self.init_revenue_database()
        
        # Revenue sharing rates by tier
        self.creator_share_rates = {
            'free': 0.0,
            'basic': 0.70,
            'premium': 0.75,
            'enterprise': 0.80,
            'custom': 0.85
        }
        
        print("💰 Revenue Tracking System initialized!")
        print("📊 Multi-stream billing and creator payouts enabled")
    
    def init_revenue_database(self):
        """Initialize revenue tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Revenue streams
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue_streams (
                stream_id TEXT PRIMARY KEY,
                stream_type TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                pattern_id TEXT,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                billing_period TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT DEFAULT 'active',
                creator_share_rate REAL,
                platform_share_rate REAL,
                created_date TEXT,
                updated_date TEXT
            )
        ''')
        
        # Payment transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_transactions (
                transaction_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                stream_id TEXT,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                transaction_type TEXT NOT NULL,
                payment_method TEXT,
                status TEXT DEFAULT 'pending',
                created_date TEXT,
                processed_date TEXT,
                fees REAL DEFAULT 0,
                net_amount REAL,
                metadata TEXT
            )
        ''')
        
        # Creator payouts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS creator_payouts (
                payout_id TEXT PRIMARY KEY,
                creator_id TEXT NOT NULL,
                period_start TEXT,
                period_end TEXT,
                gross_revenue REAL,
                creator_share REAL,
                platform_fees REAL,
                net_payout REAL,
                status TEXT DEFAULT 'pending',
                payout_date TEXT,
                payout_method TEXT,
                transaction_reference TEXT
            )
        ''')
        
        # Monthly revenue summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_revenue (
                summary_id TEXT PRIMARY KEY,
                year INTEGER,
                month INTEGER,
                total_revenue REAL,
                subscription_revenue REAL,
                usage_revenue REAL,
                custom_pattern_revenue REAL,
                enterprise_revenue REAL,
                services_revenue REAL,
                creator_payouts REAL,
                platform_revenue REAL,
                growth_rate REAL,
                customer_count INTEGER,
                churn_rate REAL,
                created_date TEXT
            )
        ''')
        
        # Customer lifetime value
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_ltv (
                ltv_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                total_revenue REAL,
                months_active INTEGER,
                avg_monthly_revenue REAL,
                predicted_ltv REAL,
                churn_probability REAL,
                last_updated TEXT,
                UNIQUE(customer_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("💳 Revenue tracking database initialized")
    
    def create_revenue_stream(self, stream_config: Dict) -> str:
        """💰 Create new revenue stream"""
        stream_id = f"stream_{uuid.uuid4().hex[:12]}"
        
        # Determine revenue sharing rates
        tier = stream_config.get('tier', 'basic')
        creator_share_rate = self.creator_share_rates.get(tier, 0.70)
        platform_share_rate = 1.0 - creator_share_rate
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO revenue_streams
            (stream_id, stream_type, customer_id, pattern_id, amount, currency,
             billing_period, start_date, end_date, status, creator_share_rate,
             platform_share_rate, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stream_id,
            stream_config['stream_type'],
            stream_config['customer_id'],
            stream_config.get('pattern_id'),
            stream_config['amount'],
            stream_config.get('currency', 'USD'),
            stream_config.get('billing_period', 'monthly'),
            stream_config['start_date'],
            stream_config.get('end_date'),
            'active',
            creator_share_rate,
            platform_share_rate,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"💰 Created revenue stream: {stream_config['stream_type']}")
        print(f"💵 Amount: ${stream_config['amount']:.2f}/{stream_config.get('billing_period', 'month')}")
        print(f"🤝 Creator share: {creator_share_rate:.1%} | Platform: {platform_share_rate:.1%}")
        
        return stream_id
    
    def process_payment(self, payment_data: Dict) -> str:
        """💳 Process payment transaction"""
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
        
        # Calculate fees (simplified - 2.9% + $0.30 for demo)
        amount = payment_data['amount']
        fees = (amount * 0.029) + 0.30
        net_amount = amount - fees
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO payment_transactions
            (transaction_id, customer_id, stream_id, amount, currency, transaction_type,
             payment_method, status, created_date, fees, net_amount, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_id,
            payment_data['customer_id'],
            payment_data.get('stream_id'),
            amount,
            payment_data.get('currency', 'USD'),
            payment_data.get('transaction_type', 'charge'),
            payment_data.get('payment_method', 'card'),
            'completed',  # Simplified - assume success
            datetime.now().isoformat(),
            fees,
            net_amount,
            json.dumps(payment_data.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
        
        print(f"💳 Processed payment: ${amount:.2f}")
        print(f"💰 Net amount: ${net_amount:.2f} (fees: ${fees:.2f})")
        
        return transaction_id
    
    def calculate_monthly_revenue(self, year: int, month: int) -> Dict:
        """📊 Calculate comprehensive monthly revenue metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        # Total revenue by stream type
        cursor.execute('''
            SELECT rs.stream_type, SUM(pt.amount) 
            FROM revenue_streams rs
            JOIN payment_transactions pt ON rs.stream_id = pt.stream_id
            WHERE pt.created_date >= ? AND pt.created_date < ? 
            AND pt.status = 'completed' AND pt.transaction_type = 'charge'
            GROUP BY rs.stream_type
        ''', (start_str, end_str))
        
        revenue_by_type = dict(cursor.fetchall())
        
        # Total revenue
        total_revenue = sum(revenue_by_type.values())
        
        # Creator payouts
        cursor.execute('''
            SELECT SUM(net_payout)
            FROM creator_payouts
            WHERE period_start >= ? AND period_end < ?
        ''', (start_str, end_str))
        
        creator_payouts = cursor.fetchone()[0] or 0
        
        # Active customers
        cursor.execute('''
            SELECT COUNT(DISTINCT customer_id)
            FROM payment_transactions
            WHERE created_date >= ? AND created_date < ?
            AND status = 'completed'
        ''', (start_str, end_str))
        
        customer_count = cursor.fetchone()[0] or 0
        
        # Previous month for growth calculation
        prev_start = start_date - timedelta(days=32)
        prev_start = datetime(prev_start.year, prev_start.month, 1)
        prev_end = start_date
        
        cursor.execute('''
            SELECT SUM(pt.amount)
            FROM revenue_streams rs
            JOIN payment_transactions pt ON rs.stream_id = pt.stream_id
            WHERE pt.created_date >= ? AND pt.created_date < ? 
            AND pt.status = 'completed' AND pt.transaction_type = 'charge'
        ''', (prev_start.isoformat(), prev_end.isoformat()))
        
        prev_revenue = cursor.fetchone()[0] or 0
        growth_rate = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        conn.close()
        
        # Build comprehensive revenue metrics
        metrics = {
            'year': year,
            'month': month,
            'total_revenue': total_revenue,
            'subscription_revenue': revenue_by_type.get('subscription', 0),
            'usage_revenue': revenue_by_type.get('api_usage', 0),
            'custom_pattern_revenue': revenue_by_type.get('custom_pattern', 0),
            'enterprise_revenue': revenue_by_type.get('enterprise', 0),
            'services_revenue': revenue_by_type.get('services', 0),
            'creator_payouts': creator_payouts,
            'platform_revenue': total_revenue - creator_payouts,
            'growth_rate': growth_rate,
            'customer_count': customer_count,
            'churn_rate': self.calculate_churn_rate(year, month),
            'avg_revenue_per_customer': total_revenue / customer_count if customer_count > 0 else 0
        }
        
        # Save monthly summary
        self.save_monthly_summary(metrics)
        
        return metrics
    
    def calculate_churn_rate(self, year: int, month: int) -> float:
        """📉 Calculate monthly churn rate"""
        # Simplified churn calculation - customers who cancelled subscriptions
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        
        # Customers at start of month
        cursor.execute('''
            SELECT COUNT(DISTINCT customer_id)
            FROM revenue_streams
            WHERE start_date < ? AND (end_date IS NULL OR end_date > ?)
            AND status = 'active'
        ''', (start_date.isoformat(), start_date.isoformat()))
        
        customers_start = cursor.fetchone()[0] or 0
        
        # Customers who cancelled during month
        cursor.execute('''
            SELECT COUNT(DISTINCT customer_id)
            FROM revenue_streams
            WHERE status = 'cancelled' AND updated_date >= ? AND updated_date < ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        churned_customers = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return (churned_customers / customers_start * 100) if customers_start > 0 else 0
    
    def save_monthly_summary(self, metrics: Dict):
        """💾 Save monthly revenue summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        summary_id = f"summary_{metrics['year']}_{metrics['month']:02d}"
        
        cursor.execute('''
            INSERT OR REPLACE INTO monthly_revenue
            (summary_id, year, month, total_revenue, subscription_revenue,
             usage_revenue, custom_pattern_revenue, enterprise_revenue,
             services_revenue, creator_payouts, platform_revenue, growth_rate,
             customer_count, churn_rate, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            summary_id, metrics['year'], metrics['month'], metrics['total_revenue'],
            metrics['subscription_revenue'], metrics['usage_revenue'],
            metrics['custom_pattern_revenue'], metrics['enterprise_revenue'],
            metrics['services_revenue'], metrics['creator_payouts'],
            metrics['platform_revenue'], metrics['growth_rate'],
            metrics['customer_count'], metrics['churn_rate'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def process_creator_payouts(self, period_start: datetime, period_end: datetime):
        """🤝 Process creator revenue sharing payouts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate creator earnings by creator
        cursor.execute('''
            SELECT rs.pattern_id, SUM(pt.net_amount * rs.creator_share_rate) as creator_earnings
            FROM revenue_streams rs
            JOIN payment_transactions pt ON rs.stream_id = pt.stream_id
            WHERE pt.created_date >= ? AND pt.created_date < ?
            AND pt.status = 'completed' AND pt.transaction_type = 'charge'
            AND rs.creator_share_rate > 0
            GROUP BY rs.pattern_id
        ''', (period_start.isoformat(), period_end.isoformat()))
        
        creator_earnings = cursor.fetchall()
        
        for pattern_id, earnings in creator_earnings:
            if earnings > 10.00:  # Minimum payout threshold
                # Get creator info (simplified - using pattern_id as creator_id)
                creator_id = f"creator_{pattern_id}"
                
                # Calculate payout after platform fees (2% processing fee)
                platform_fees = earnings * 0.02
                net_payout = earnings - platform_fees
                
                payout_id = f"payout_{uuid.uuid4().hex[:12]}"
                
                cursor.execute('''
                    INSERT INTO creator_payouts
                    (payout_id, creator_id, period_start, period_end, 
                     gross_revenue, creator_share, platform_fees, net_payout,
                     status, payout_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    payout_id, creator_id, period_start.isoformat(),
                    period_end.isoformat(), earnings, earnings, platform_fees,
                    net_payout, 'pending', datetime.now().isoformat()
                ))
                
                print(f"💸 Creator payout: {creator_id} - ${net_payout:.2f}")
        
        conn.commit()
        conn.close()
        print(f"✅ Processed {len(creator_earnings)} creator payouts")
    
    def generate_revenue_report(self, months: int = 12) -> Dict:
        """📊 Generate comprehensive revenue report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get monthly data for trend analysis
        cursor.execute('''
            SELECT year, month, total_revenue, growth_rate, customer_count, churn_rate
            FROM monthly_revenue
            ORDER BY year DESC, month DESC
            LIMIT ?
        ''', (months,))
        
        monthly_data = cursor.fetchall()
        
        if not monthly_data:
            return {"error": "No revenue data available"}
        
        # Calculate key metrics
        total_revenue_12m = sum(row[2] for row in monthly_data)
        avg_monthly_revenue = total_revenue_12m / len(monthly_data)
        
        growth_rates = [row[3] for row in monthly_data if row[3] is not None]
        avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        
        avg_customers = sum(row[4] for row in monthly_data) / len(monthly_data)
        
        churn_rates = [row[5] for row in monthly_data if row[5] is not None]
        avg_churn_rate = sum(churn_rates) / len(churn_rates) if churn_rates else 0
        
        # Current month metrics
        current_month = monthly_data[0] if monthly_data else None
        
        # Revenue by stream type (all time)
        cursor.execute('''
            SELECT rs.stream_type, SUM(pt.amount)
            FROM revenue_streams rs
            JOIN payment_transactions pt ON rs.stream_id = pt.stream_id
            WHERE pt.status = 'completed'
            GROUP BY rs.stream_type
        ''')
        
        revenue_by_stream = dict(cursor.fetchall())
        
        # Top performing patterns/customers
        cursor.execute('''
            SELECT rs.pattern_id, SUM(pt.net_amount) as revenue
            FROM revenue_streams rs
            JOIN payment_transactions pt ON rs.stream_id = pt.stream_id
            WHERE pt.status = 'completed' AND rs.pattern_id IS NOT NULL
            GROUP BY rs.pattern_id
            ORDER BY revenue DESC
            LIMIT 10
        ''')
        
        top_patterns = cursor.fetchall()
        
        conn.close()
        
        report = {
            "reporting_period": f"Last {months} months",
            "summary": {
                "total_revenue_12m": total_revenue_12m,
                "avg_monthly_revenue": avg_monthly_revenue,
                "avg_growth_rate": avg_growth_rate,
                "avg_customers": avg_customers,
                "avg_churn_rate": avg_churn_rate,
                "annualized_revenue": avg_monthly_revenue * 12
            },
            "current_month": {
                "revenue": current_month[2] if current_month else 0,
                "growth_rate": current_month[3] if current_month else 0,
                "customers": current_month[4] if current_month else 0,
                "churn_rate": current_month[5] if current_month else 0
            },
            "revenue_streams": revenue_by_stream,
            "top_patterns": [{"pattern_id": p[0], "revenue": p[1]} for p in top_patterns],
            "monthly_trend": [
                {
                    "year": row[0],
                    "month": row[1],
                    "revenue": row[2],
                    "growth": row[3],
                    "customers": row[4]
                } for row in monthly_data
            ]
        }
        
        return report
    
    def export_financial_data(self, start_date: datetime, end_date: datetime, format: str = "csv") -> str:
        """📁 Export financial data for accounting/tax purposes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pt.transaction_id, pt.customer_id, pt.amount, pt.currency,
                   pt.transaction_type, pt.created_date, pt.fees, pt.net_amount,
                   rs.stream_type, rs.pattern_id
            FROM payment_transactions pt
            LEFT JOIN revenue_streams rs ON pt.stream_id = rs.stream_id
            WHERE pt.created_date >= ? AND pt.created_date <= ?
            AND pt.status = 'completed'
            ORDER BY pt.created_date
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        transactions = cursor.fetchall()
        conn.close()
        
        filename = f"benson_financial_export_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Headers
            writer.writerow([
                'Transaction ID', 'Customer ID', 'Amount', 'Currency',
                'Transaction Type', 'Date', 'Fees', 'Net Amount',
                'Stream Type', 'Pattern ID'
            ])
            
            # Data rows
            for transaction in transactions:
                writer.writerow(transaction)
        
        print(f"📁 Exported {len(transactions)} transactions to {filename}")
        return filename

def demo_revenue_tracking():
    """💰 Demonstrate comprehensive revenue tracking system"""
    tracker = RevenueTracker()
    
    print("\n💰 REVENUE TRACKING DEMO")
    print("="*40)
    
    # Create demo revenue streams
    demo_streams = [
        {
            'stream_type': 'subscription',
            'customer_id': 'customer_001',
            'pattern_id': 'pattern_rsi_oversold',
            'amount': 49.99,
            'billing_period': 'monthly',
            'start_date': datetime.now().isoformat(),
            'tier': 'premium'
        },
        {
            'stream_type': 'enterprise',
            'customer_id': 'customer_hedge_fund',
            'amount': 1999.99,
            'billing_period': 'monthly',
            'start_date': datetime.now().isoformat(),
            'tier': 'enterprise'
        },
        {
            'stream_type': 'custom_pattern',
            'customer_id': 'customer_002',
            'pattern_id': 'custom_pattern_001',
            'amount': 999.99,
            'billing_period': 'one-time',
            'start_date': datetime.now().isoformat(),
            'tier': 'custom'
        },
        {
            'stream_type': 'api_usage',
            'customer_id': 'customer_api_user',
            'amount': 149.50,
            'billing_period': 'usage-based',
            'start_date': datetime.now().isoformat(),
            'tier': 'basic'
        }
    ]
    
    stream_ids = []
    for stream_config in demo_streams:
        stream_id = tracker.create_revenue_stream(stream_config)
        stream_ids.append(stream_id)
        
        # Process payment for this stream
        payment_data = {
            'customer_id': stream_config['customer_id'],
            'stream_id': stream_id,
            'amount': stream_config['amount'],
            'payment_method': 'card'
        }
        tracker.process_payment(payment_data)
        print()
    
    print("💳 MONTHLY REVENUE CALCULATION")
    print("="*35)
    
    # Calculate current month revenue
    now = datetime.now()
    monthly_metrics = tracker.calculate_monthly_revenue(now.year, now.month)
    
    print(f"📊 Monthly Revenue Report - {calendar.month_name[now.month]} {now.year}")
    print(f"💰 Total Revenue: ${monthly_metrics['total_revenue']:,.2f}")
    print(f"📈 Growth Rate: {monthly_metrics['growth_rate']:+.1f}%")
    print(f"👥 Customers: {monthly_metrics['customer_count']:,}")
    print(f"💸 Creator Payouts: ${monthly_metrics['creator_payouts']:,.2f}")
    print(f"🏢 Platform Revenue: ${monthly_metrics['platform_revenue']:,.2f}")
    print(f"💵 ARPC: ${monthly_metrics['avg_revenue_per_customer']:,.2f}")
    
    print(f"\n📊 Revenue by Stream Type:")
    print(f"   • Subscriptions: ${monthly_metrics['subscription_revenue']:,.2f}")
    print(f"   • Enterprise: ${monthly_metrics['enterprise_revenue']:,.2f}")  
    print(f"   • Custom Patterns: ${monthly_metrics['custom_pattern_revenue']:,.2f}")
    print(f"   • API Usage: ${monthly_metrics['usage_revenue']:,.2f}")
    
    print("\n💸 CREATOR PAYOUTS")
    print("="*20)
    
    # Process creator payouts for this month
    month_start = datetime(now.year, now.month, 1)
    month_end = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
    tracker.process_creator_payouts(month_start, month_end)
    
    print("\n📊 COMPREHENSIVE REVENUE REPORT")
    print("="*40)
    
    # Generate full revenue report
    revenue_report = tracker.generate_revenue_report(12)
    
    print(f"💰 Annual Revenue: ${revenue_report['summary']['annualized_revenue']:,.2f}")
    print(f"📈 Avg Growth Rate: {revenue_report['summary']['avg_growth_rate']:+.1f}%")
    print(f"👥 Avg Customers: {revenue_report['summary']['avg_customers']:,.0f}")
    print(f"📉 Avg Churn Rate: {revenue_report['summary']['avg_churn_rate']:.1f}%")
    
    print(f"\n🏆 Top Revenue Streams:")
    for stream_type, revenue in revenue_report['revenue_streams'].items():
        print(f"   • {stream_type.title()}: ${revenue:,.2f}")
    
    # Export financial data
    print("\n📁 FINANCIAL DATA EXPORT")
    print("="*30)
    
    start_export = datetime.now() - timedelta(days=30)
    end_export = datetime.now()
    filename = tracker.export_financial_data(start_export, end_export)
    
    return tracker

if __name__ == "__main__":
    print("💰 BENSON REVENUE TRACKING SYSTEM")
    print("Comprehensive billing and creator revenue sharing")
    print("="*60)
    
    # Run demo
    tracker = demo_revenue_tracking()
    
    print("\n🎯 REVENUE SYSTEM READY!")
    print("Features:")
    print("• Multi-stream revenue tracking")
    print("• Automated creator payouts (70-85% revenue sharing)")
    print("• Usage-based billing and subscriptions")
    print("• Financial reporting and tax compliance")
    print("• Revenue forecasting and analytics")
    
    print("\n💎 Complete PaaS Revenue Streams:")
    print("• Pattern Subscriptions: $9.99-$199.99/month")
    print("• API Decision Engine: $0.01-$0.10 per call")
    print("• Custom Pattern Creation: $499-$2,999")
    print("• Enterprise Data Integration: $299-$4,999/month")
    print("• Professional Services: $5,000-$50,000")
    print("• Pattern Marketplace Commission: 15-30%")