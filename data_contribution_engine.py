"""
🌐 DATA CONTRIBUTION ENGINE
=============================
Transform users into data partners with privacy-first contribution system.
Leverages user trading data to improve patterns while rewarding contributors.

Key Features:
- Privacy-first data anonymization
- Quality-based contribution scoring  
- Tiered rewards and discounts
- Automated pattern enhancement
- Community data network effects

Revenue Model:
- Better patterns from more data = higher subscription value
- Data contributors get discounts but drive platform improvement
- Network effects: more users = better patterns = more valuable platform
"""

import sqlite3
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class DataContribution:
    """Represents a user's data contribution"""
    user_id: str
    contribution_id: str
    data_type: str  # 'trades', 'market_data', 'patterns', 'signals'
    data_quality_score: float  # 0-100
    volume_score: float  # Based on amount of data
    uniqueness_score: float  # How unique/valuable this data is
    contribution_date: datetime
    anonymized_data: Dict
    privacy_level: str  # 'public', 'anonymized', 'encrypted'

@dataclass
class ContributorRewards:
    """Rewards earned by data contributors"""
    user_id: str
    total_contribution_score: float
    tier: str  # 'bronze', 'silver', 'gold', 'platinum'
    discount_percentage: float  # 0-75% off subscriptions
    premium_access: List[str]  # Premium patterns/features unlocked
    revenue_share_percentage: float  # 0-5% of platform revenue
    monthly_credits: int  # API/service credits earned

class DataContributionEngine:
    def __init__(self, db_path: str = 'benson_data_contributions.db'):
        self.db_path = db_path
        self.init_database()
        
        # Contribution scoring weights
        self.quality_weight = 0.4
        self.volume_weight = 0.3  
        self.uniqueness_weight = 0.3
        
        # Tier thresholds (total contribution score)
        self.tier_thresholds = {
            'bronze': 100,
            'silver': 500,
            'gold': 2000,
            'platinum': 5000
        }
        
        # Reward structures by tier
        self.tier_rewards = {
            'bronze': {'discount': 10, 'revenue_share': 0.1, 'credits': 100},
            'silver': {'discount': 25, 'revenue_share': 0.5, 'credits': 300},
            'gold': {'discount': 50, 'revenue_share': 1.5, 'credits': 750},
            'platinum': {'discount': 75, 'revenue_share': 3.0, 'credits': 2000}
        }

    def init_database(self):
        """Initialize data contribution database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Data contributions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_contributions (
                contribution_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                data_type TEXT NOT NULL,
                data_quality_score REAL NOT NULL,
                volume_score REAL NOT NULL,
                uniqueness_score REAL NOT NULL,
                total_score REAL NOT NULL,
                contribution_date TIMESTAMP NOT NULL,
                anonymized_data TEXT NOT NULL,
                privacy_level TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User contribution profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contributor_profiles (
                user_id TEXT PRIMARY KEY,
                total_contribution_score REAL DEFAULT 0,
                tier TEXT DEFAULT 'bronze',
                discount_percentage REAL DEFAULT 0,
                revenue_share_percentage REAL DEFAULT 0,
                monthly_credits INTEGER DEFAULT 0,
                premium_access TEXT DEFAULT '[]',
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contribution TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Data quality metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_quality_metrics (
                metric_id TEXT PRIMARY KEY,
                contribution_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                benchmark_score REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contribution_id) REFERENCES data_contributions (contribution_id)
            )
        """)
        
        # Pattern improvement tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_improvements (
                improvement_id TEXT PRIMARY KEY,
                pattern_id TEXT NOT NULL,
                contributing_users TEXT NOT NULL,  -- JSON list of user_ids
                before_performance REAL NOT NULL,
                after_performance REAL NOT NULL,
                improvement_percentage REAL NOT NULL,
                data_contributions_used INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Community data network stats
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_stats (
                stat_date DATE PRIMARY KEY,
                total_contributors INTEGER NOT NULL,
                total_contributions INTEGER NOT NULL,
                data_volume_gb REAL NOT NULL,
                pattern_improvements INTEGER NOT NULL,
                platform_performance_boost REAL NOT NULL,
                community_value_generated REAL NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()

    def anonymize_trading_data(self, trading_data: Dict, user_id: str) -> Dict:
        """Anonymize user trading data while preserving patterns"""
        # Create deterministic but anonymous user hash
        user_hash = hashlib.sha256(f"{user_id}_salt_2025".encode()).hexdigest()[:16]
        
        anonymized = {
            'contributor_id': user_hash,
            'trades': [],
            'market_conditions': trading_data.get('market_conditions', {}),
            'time_patterns': trading_data.get('time_patterns', {}),
            'metadata': {
                'contribution_date': datetime.now().isoformat(),
                'data_version': '1.0',
                'privacy_level': 'anonymized'
            }
        }
        
        # Anonymize individual trades
        for trade in trading_data.get('trades', []):
            anonymized_trade = {
                'timestamp': trade.get('timestamp'),
                'pair': trade.get('pair'),
                'side': trade.get('side'),
                'entry_price_normalized': self._normalize_price(trade.get('entry_price', 0)),
                'exit_price_normalized': self._normalize_price(trade.get('exit_price', 0)),
                'return_percentage': trade.get('return_percentage', 0),
                'position_size_percentage': trade.get('position_size_percentage', 0),
                'market_conditions': trade.get('market_conditions', {}),
                'signals_used': trade.get('signals_used', []),
                'confidence_score': trade.get('confidence_score', 0)
            }
            anonymized['trades'].append(anonymized_trade)
        
        return anonymized

    def _normalize_price(self, price: float) -> float:
        """Normalize prices to protect actual values while preserving patterns"""
        if price <= 0:
            return 0
        # Convert to percentage change from a baseline
        return round((price / 1000) % 100, 4)

    def calculate_data_quality_score(self, trading_data: Dict) -> float:
        """Calculate quality score for contributed data"""
        quality_metrics = []
        
        # Trade count factor (more trades = better data)
        trade_count = len(trading_data.get('trades', []))
        count_score = min(trade_count / 100 * 30, 30)  # Max 30 points for 100+ trades
        quality_metrics.append(count_score)
        
        # Time span factor (longer history = better)
        if trading_data.get('trades'):
            dates = [trade.get('timestamp') for trade in trading_data['trades'] if trade.get('timestamp')]
            if dates:
                time_span_days = (max(dates) - min(dates)).days if len(dates) > 1 else 1
                time_score = min(time_span_days / 365 * 25, 25)  # Max 25 points for 1+ year
                quality_metrics.append(time_score)
        
        # Data completeness (all required fields present)
        completeness_scores = []
        for trade in trading_data.get('trades', []):
            required_fields = ['timestamp', 'pair', 'side', 'entry_price', 'return_percentage']
            present_fields = sum(1 for field in required_fields if trade.get(field) is not None)
            completeness_scores.append(present_fields / len(required_fields))
        
        if completeness_scores:
            completeness_score = np.mean(completeness_scores) * 20  # Max 20 points
            quality_metrics.append(completeness_score)
        
        # Performance variety (different market conditions)
        market_conditions = set()
        for trade in trading_data.get('trades', []):
            if trade.get('market_conditions'):
                market_conditions.add(str(trade['market_conditions']))
        
        variety_score = min(len(market_conditions) / 10 * 15, 15)  # Max 15 points for 10+ conditions
        quality_metrics.append(variety_score)
        
        # Signal usage (contributes to pattern understanding)
        signals_used = set()
        for trade in trading_data.get('trades', []):
            for signal in trade.get('signals_used', []):
                signals_used.add(signal)
        
        signal_score = min(len(signals_used) / 5 * 10, 10)  # Max 10 points for 5+ signals
        quality_metrics.append(signal_score)
        
        return min(sum(quality_metrics), 100.0)

    def calculate_volume_score(self, trading_data: Dict) -> float:
        """Calculate volume score based on amount of data"""
        trade_count = len(trading_data.get('trades', []))
        
        # Progressive scoring for trade volume
        if trade_count >= 1000:
            return 100.0
        elif trade_count >= 500:
            return 80.0 + (trade_count - 500) / 500 * 20
        elif trade_count >= 100:
            return 60.0 + (trade_count - 100) / 400 * 20
        elif trade_count >= 50:
            return 40.0 + (trade_count - 50) / 50 * 20
        elif trade_count >= 10:
            return 20.0 + (trade_count - 10) / 40 * 20
        else:
            return trade_count / 10 * 20

    def calculate_uniqueness_score(self, trading_data: Dict, user_id: str) -> float:
        """Calculate how unique this data contribution is"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing similar contributions
        cursor.execute("""
            SELECT anonymized_data FROM data_contributions 
            WHERE user_id != ? AND data_type = 'trades'
        """, (user_id,))
        existing_data = cursor.fetchall()
        conn.close()
        
        if not existing_data:
            return 100.0  # First contribution is highly unique
        
        # Calculate similarity with existing data
        uniqueness_factors = []
        
        # Trading pairs uniqueness
        user_pairs = set()
        for trade in trading_data.get('trades', []):
            if trade.get('pair'):
                user_pairs.add(trade['pair'])
        
        existing_pairs = set()
        for data_row in existing_data[:10]:  # Sample first 10 for performance
            try:
                existing_trades = json.loads(data_row[0])
                for trade in existing_trades.get('trades', []):
                    if trade.get('pair'):
                        existing_pairs.add(trade['pair'])
            except:
                continue
        
        if existing_pairs:
            unique_pairs = user_pairs - existing_pairs
            pair_uniqueness = len(unique_pairs) / len(user_pairs) * 100 if user_pairs else 0
            uniqueness_factors.append(pair_uniqueness)
        
        # Strategy uniqueness (based on signals and patterns)
        user_signals = set()
        for trade in trading_data.get('trades', []):
            for signal in trade.get('signals_used', []):
                user_signals.add(signal)
        
        signal_uniqueness = 70 if user_signals else 30  # Placeholder - would need deeper analysis
        uniqueness_factors.append(signal_uniqueness)
        
        # Time period uniqueness
        time_uniqueness = 60  # Placeholder - would analyze trading time patterns
        uniqueness_factors.append(time_uniqueness)
        
        return np.mean(uniqueness_factors) if uniqueness_factors else 50.0

    def submit_data_contribution(self, user_id: str, trading_data: Dict, 
                                privacy_level: str = 'anonymized') -> DataContribution:
        """Submit and process a data contribution"""
        
        # Generate contribution ID
        contribution_id = str(uuid.uuid4())
        
        # Anonymize the data
        anonymized_data = self.anonymize_trading_data(trading_data, user_id)
        
        # Calculate scores
        quality_score = self.calculate_data_quality_score(trading_data)
        volume_score = self.calculate_volume_score(trading_data)
        uniqueness_score = self.calculate_uniqueness_score(trading_data, user_id)
        
        # Calculate total contribution score
        total_score = (quality_score * self.quality_weight + 
                      volume_score * self.volume_weight + 
                      uniqueness_score * self.uniqueness_weight)
        
        # Create contribution record
        contribution = DataContribution(
            user_id=user_id,
            contribution_id=contribution_id,
            data_type='trades',
            data_quality_score=quality_score,
            volume_score=volume_score,
            uniqueness_score=uniqueness_score,
            contribution_date=datetime.now(),
            anonymized_data=anonymized_data,
            privacy_level=privacy_level
        )
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO data_contributions 
            (contribution_id, user_id, data_type, data_quality_score, volume_score, 
             uniqueness_score, total_score, contribution_date, anonymized_data, privacy_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (contribution_id, user_id, 'trades', quality_score, volume_score,
              uniqueness_score, total_score, datetime.now(), 
              json.dumps(anonymized_data), privacy_level))
        
        # Update contributor profile
        self.update_contributor_profile(user_id, total_score)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Data contribution accepted!")
        print(f"📊 Quality: {quality_score:.1f}/100 | Volume: {volume_score:.1f}/100 | Uniqueness: {uniqueness_score:.1f}/100")
        print(f"🏆 Total Score: {total_score:.1f}")
        
        return contribution

    def update_contributor_profile(self, user_id: str, new_contribution_score: float):
        """Update contributor profile with new contribution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get or create contributor profile
        cursor.execute("SELECT * FROM contributor_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        if profile:
            # Update existing profile
            new_total_score = profile[1] + new_contribution_score
            cursor.execute("""
                UPDATE contributor_profiles 
                SET total_contribution_score = ?, last_contribution = ?
                WHERE user_id = ?
            """, (new_total_score, datetime.now(), user_id))
        else:
            # Create new profile
            new_total_score = new_contribution_score
            cursor.execute("""
                INSERT INTO contributor_profiles 
                (user_id, total_contribution_score, last_contribution)
                VALUES (?, ?, ?)
            """, (user_id, new_total_score, datetime.now()))
        
        # Calculate new tier and rewards
        new_tier = self.calculate_tier(new_total_score)
        rewards = self.calculate_rewards(new_tier, new_total_score)
        
        # Update tier and rewards
        cursor.execute("""
            UPDATE contributor_profiles 
            SET tier = ?, discount_percentage = ?, revenue_share_percentage = ?, 
                monthly_credits = ?, premium_access = ?
            WHERE user_id = ?
        """, (new_tier, rewards.discount_percentage, rewards.revenue_share_percentage,
              rewards.monthly_credits, json.dumps(rewards.premium_access), user_id))
        
        conn.commit()
        conn.close()
        
        print(f"🎖️ Contributor tier: {new_tier.upper()}")
        print(f"💰 Subscription discount: {rewards.discount_percentage}%")
        print(f"📈 Revenue share: {rewards.revenue_share_percentage}%")
        print(f"🎁 Monthly credits: {rewards.monthly_credits}")

    def calculate_tier(self, total_contribution_score: float) -> str:
        """Calculate contributor tier based on total score"""
        for tier in ['platinum', 'gold', 'silver', 'bronze']:
            if total_contribution_score >= self.tier_thresholds[tier]:
                return tier
        return 'bronze'

    def calculate_rewards(self, tier: str, total_score: float) -> ContributorRewards:
        """Calculate rewards for contributor tier"""
        base_rewards = self.tier_rewards[tier]
        
        # Premium access based on tier
        premium_access = []
        if tier in ['silver', 'gold', 'platinum']:
            premium_access.append('early_pattern_access')
        if tier in ['gold', 'platinum']:
            premium_access.extend(['advanced_analytics', 'custom_pattern_builder'])
        if tier == 'platinum':
            premium_access.extend(['enterprise_api_access', 'pattern_creator_tools'])
        
        return ContributorRewards(
            user_id='',  # Will be set by caller
            total_contribution_score=total_score,
            tier=tier,
            discount_percentage=base_rewards['discount'],
            premium_access=premium_access,
            revenue_share_percentage=base_rewards['revenue_share'],
            monthly_credits=base_rewards['credits']
        )

    def get_contributor_benefits(self, user_id: str) -> Dict:
        """Get current benefits for a contributor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM contributor_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        if not profile:
            return {
                'tier': 'none',
                'discount_percentage': 0,
                'revenue_share_percentage': 0,
                'monthly_credits': 0,
                'premium_access': [],
                'total_contribution_score': 0
            }
        
        return {
            'tier': profile[2],
            'discount_percentage': profile[3],
            'revenue_share_percentage': profile[4],
            'monthly_credits': profile[5],
            'premium_access': json.loads(profile[6]),
            'total_contribution_score': profile[1]
        }

    def generate_community_stats(self) -> Dict:
        """Generate community data network statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total contributors
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM contributor_profiles WHERE status = 'active'")
        total_contributors = cursor.fetchone()[0]
        
        # Total contributions
        cursor.execute("SELECT COUNT(*) FROM data_contributions WHERE status = 'active'")
        total_contributions = cursor.fetchone()[0]
        
        # Total contribution score (proxy for data volume)
        cursor.execute("SELECT SUM(total_score) FROM data_contributions WHERE status = 'active'")
        total_score = cursor.fetchone()[0] or 0
        data_volume_gb = total_score / 1000  # Rough approximation
        
        # Pattern improvements
        cursor.execute("SELECT COUNT(*) FROM pattern_improvements")
        pattern_improvements = cursor.fetchone()[0]
        
        # Top contributors by tier
        cursor.execute("""
            SELECT tier, COUNT(*) FROM contributor_profiles 
            WHERE status = 'active' GROUP BY tier
        """)
        tier_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        # Calculate platform performance boost
        performance_boost = min(total_contributors / 1000 * 15, 25)  # Max 25% boost
        
        # Estimate community value generated
        community_value = total_contributors * 50 + total_contributions * 25  # $50/contributor + $25/contribution
        
        return {
            'total_contributors': total_contributors,
            'total_contributions': total_contributions,
            'data_volume_gb': round(data_volume_gb, 2),
            'pattern_improvements': pattern_improvements,
            'platform_performance_boost': round(performance_boost, 2),
            'community_value_generated': community_value,
            'tier_distribution': tier_distribution,
            'average_contribution_score': round(total_score / max(total_contributions, 1), 2)
        }

    def simulate_data_contribution_demo(self):
        """Simulate the data contribution system with demo users"""
        print("🌐 BENSON DATA CONTRIBUTION ENGINE DEMO")
        print("=" * 55)
        
        # Demo users with different contribution profiles
        demo_users = [
            {
                'user_id': 'demo_trader_001',
                'name': 'Active Day Trader',
                'trades_count': 150,
                'trade_quality': 'high'
            },
            {
                'user_id': 'demo_trader_002', 
                'name': 'Swing Trader',
                'trades_count': 80,
                'trade_quality': 'medium'
            },
            {
                'user_id': 'demo_trader_003',
                'name': 'Algorithmic Trader',
                'trades_count': 300,
                'trade_quality': 'excellent'
            }
        ]
        
        for demo_user in demo_users:
            print(f"\n👤 Processing contribution from {demo_user['name']}")
            print("-" * 50)
            
            # Generate demo trading data
            trading_data = self.generate_demo_trading_data(
                demo_user['trades_count'], 
                demo_user['trade_quality']
            )
            
            # Submit contribution
            contribution = self.submit_data_contribution(
                demo_user['user_id'], 
                trading_data, 
                'anonymized'
            )
            
            # Show benefits
            benefits = self.get_contributor_benefits(demo_user['user_id'])
            print(f"💎 Benefits Unlocked:")
            print(f"   • {benefits['discount_percentage']}% subscription discount")
            print(f"   • {benefits['revenue_share_percentage']}% platform revenue share")
            print(f"   • {benefits['monthly_credits']} monthly API credits")
            print(f"   • Premium features: {', '.join(benefits['premium_access'])}")
        
        # Generate community stats
        print(f"\n🌍 COMMUNITY DATA NETWORK STATS")
        print("-" * 50)
        stats = self.generate_community_stats()
        
        print(f"👥 Total Contributors: {stats['total_contributors']}")
        print(f"📊 Data Contributions: {stats['total_contributions']}")
        print(f"💾 Data Volume: {stats['data_volume_gb']} GB")
        print(f"🚀 Platform Performance Boost: +{stats['platform_performance_boost']}%")
        print(f"💰 Community Value Generated: ${stats['community_value_generated']:,}")
        
        print(f"\n🏆 Contributor Tiers:")
        for tier, count in stats['tier_distribution'].items():
            print(f"   • {tier.title()}: {count} contributors")
        
        print(f"\n🎯 DATA NETWORK EFFECTS:")
        print(f"   • More contributors = better pattern accuracy")
        print(f"   • Better patterns = higher subscription value")
        print(f"   • Contributors get discounts but drive platform growth")
        print(f"   • Network effects create competitive moat")

    def generate_demo_trading_data(self, trade_count: int, quality: str) -> Dict:
        """Generate demo trading data for testing"""
        np.random.seed(42)  # Consistent demo data
        
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT']
        signals = ['rsi_divergence', 'volume_spike', 'support_bounce', 'breakout', 'momentum']
        
        trades = []
        for i in range(trade_count):
            # Quality affects return distribution
            if quality == 'excellent':
                return_pct = np.random.normal(2.5, 5.0)  # Higher average returns
            elif quality == 'high':
                return_pct = np.random.normal(1.5, 4.0)
            else:
                return_pct = np.random.normal(0.8, 6.0)
            
            trade = {
                'timestamp': datetime.now() - timedelta(days=np.random.randint(1, 365)),
                'pair': np.random.choice(pairs),
                'side': np.random.choice(['buy', 'sell']),
                'entry_price': np.random.uniform(100, 50000),
                'exit_price': 0,  # Will be calculated
                'return_percentage': return_pct,
                'position_size_percentage': np.random.uniform(1, 10),
                'market_conditions': {
                    'volatility': np.random.uniform(0.1, 0.8),
                    'trend': np.random.choice(['bullish', 'bearish', 'sideways'])
                },
                'signals_used': list(np.random.choice(signals, size=np.random.randint(1, 4), replace=False)),
                'confidence_score': np.random.uniform(60, 95) if quality in ['high', 'excellent'] else np.random.uniform(40, 80)
            }
            
            # Calculate exit price
            trade['exit_price'] = trade['entry_price'] * (1 + trade['return_percentage'] / 100)
            
            trades.append(trade)
        
        return {
            'trades': trades,
            'market_conditions': {
                'overall_trend': 'bullish',
                'volatility_regime': 'medium'
            },
            'time_patterns': {
                'preferred_trading_hours': [9, 10, 11, 14, 15],
                'active_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            }
        }


# Demo execution
if __name__ == "__main__":
    engine = DataContributionEngine()
    engine.simulate_data_contribution_demo()