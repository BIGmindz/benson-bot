
#!/usr/bin/env python3
"""
Advanced Pattern Recognition Engine for Benson Bot
Multi-dimensional pattern detection with statistical validation
"""

import numpy as np
import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import hashlib

# Optional advanced dependencies
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️ scipy not available - using basic statistics")

try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not available - using basic clustering")

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

@dataclass
class AdvancedPattern:
    """Enhanced pattern with multi-dimensional features"""
    pattern_id: str
    pattern_hash: str  # Unique fingerprint
    
    # Market conditions
    price_trend: str  # "bullish", "bearish", "sideways"
    volatility_regime: str  # "low", "medium", "high"
    volume_profile: str  # "low", "normal", "high"
    
    # Technical indicators
    rsi_range: Tuple[float, float]  # (min, max) RSI during pattern
    rsi_trend: str  # "rising", "falling", "stable"
    supply_chain_avg: float
    supply_chain_volatility: float
    
    # Pattern sequence (last 5 data points)
    price_sequence: List[float]
    rsi_sequence: List[float]
    volume_sequence: List[float]
    
    # Outcome metrics
    success_probability: float  # 0.0 to 1.0
    avg_return: float
    max_drawdown: float
    time_to_profit: int  # minutes
    
    # Statistical validation
    statistical_significance: float  # p-value
    sample_size: int
    confidence_interval: Tuple[float, float]
    
    # Meta information
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int
    market_conditions: Dict
    
    def __post_init__(self):
        """Calculate pattern hash for uniqueness"""
        if not self.pattern_hash:
            pattern_data = f"{self.price_trend}_{self.volatility_regime}_{self.volume_profile}_{self.rsi_range}_{self.rsi_trend}"
            self.pattern_hash = hashlib.md5(pattern_data.encode()).hexdigest()[:12]

@dataclass
class MarketContext:
    """Enhanced market context with more dimensions"""
    timestamp: datetime
    symbol: str
    price: float
    price_change_1h: float
    price_change_24h: float
    volume_24h: float
    volatility: float
    rsi: float
    rsi_trend: str
    supply_chain: float
    market_cap_rank: int
    correlation_btc: float

class AdvancedPatternEngine:
    """Sophisticated pattern recognition engine"""
    
    def __init__(self, db_path: str = "benson_patterns.db"):
        self.db_path = db_path
        self.min_pattern_occurrences = 3  # Minimum sample size
        self.significance_threshold = 0.05  # 95% confidence
        self.pattern_decay_days = 30  # Patterns lose relevance over time
        self.init_database()
    
    def init_database(self):
        """Initialize enhanced pattern database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS advanced_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_hash TEXT UNIQUE,
                pattern_data TEXT,
                statistical_data TEXT,
                created_at TEXT,
                updated_at TEXT,
                occurrence_count INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                context_data TEXT,
                outcome_data TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_outcomes (
                pattern_hash TEXT,
                outcome_return REAL,
                outcome_drawdown REAL,
                time_to_result INTEGER,
                market_conditions TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def extract_market_features(self, market_data: Dict) -> Dict:
        """Extract sophisticated features from market data"""
        features = {}
        
        # Price trend analysis
        price_changes = market_data.get('price_history', [])
        if len(price_changes) >= 5:
            recent_trend = np.polyfit(range(len(price_changes[-5:])), price_changes[-5:], 1)[0]
            features['price_trend'] = 'bullish' if recent_trend > 0.01 else 'bearish' if recent_trend < -0.01 else 'sideways'
            features['trend_strength'] = abs(recent_trend)
        else:
            features['price_trend'] = 'unknown'
            features['trend_strength'] = 0.0
        
        # Volatility regime
        volatility = market_data.get('volatility', 0.0)
        if volatility < 0.3:
            features['volatility_regime'] = 'low'
        elif volatility < 0.7:
            features['volatility_regime'] = 'medium'
        else:
            features['volatility_regime'] = 'high'
        
        # Volume analysis
        volume = market_data.get('volume_24h', 0)
        volume_avg = market_data.get('volume_avg', volume)
        volume_ratio = volume / max(volume_avg, 1)
        
        if volume_ratio < 0.7:
            features['volume_profile'] = 'low'
        elif volume_ratio < 1.3:
            features['volume_profile'] = 'normal'
        else:
            features['volume_profile'] = 'high'
        
        # RSI pattern analysis
        rsi_history = market_data.get('rsi_history', [])
        if len(rsi_history) >= 3:
            rsi_trend = np.polyfit(range(len(rsi_history[-3:])), rsi_history[-3:], 1)[0]
            features['rsi_trend'] = 'rising' if rsi_trend > 1.0 else 'falling' if rsi_trend < -1.0 else 'stable'
            features['rsi_range'] = (min(rsi_history), max(rsi_history))
        else:
            features['rsi_trend'] = 'unknown'
            features['rsi_range'] = (50.0, 50.0)
        
        # Supply chain analysis
        sc_history = market_data.get('supply_chain_history', [])
        if sc_history:
            features['supply_chain_avg'] = np.mean(sc_history)
            features['supply_chain_volatility'] = np.std(sc_history)
        else:
            features['supply_chain_avg'] = 0.5
            features['supply_chain_volatility'] = 0.0
        
        return features
    
    def create_pattern_signature(self, market_context: MarketContext, sequence_data: Dict) -> str:
        """Create unique pattern signature"""
        signature_components = [
            f"trend_{market_context.price_change_24h > 0}",
            f"vol_{market_context.volatility:.1f}",
            f"rsi_{int(market_context.rsi/10)*10}",  # RSI bucket (0-10, 10-20, etc.)
            f"sc_{market_context.supply_chain:.1f}",
            f"seq_{len(sequence_data.get('price_sequence', []))}"
        ]
        
        signature = "_".join(signature_components)
        return hashlib.md5(signature.encode()).hexdigest()[:16]
    
    def detect_patterns(self, market_contexts: List[MarketContext], outcomes: List[Dict]) -> List[AdvancedPattern]:
        """Detect statistically significant patterns"""
        patterns = []
        
        # Group contexts by similar characteristics
        feature_vectors = []
        for context in market_contexts:
            vector = [
                context.price_change_1h,
                context.price_change_24h,
                context.volatility,
                context.rsi,
                context.supply_chain,
                context.correlation_btc
            ]
            feature_vectors.append(vector)
        
        if len(feature_vectors) < self.min_pattern_occurrences:
            return patterns
        
        # Pattern detection with or without sklearn
        if SKLEARN_AVAILABLE:
            # Use advanced clustering with sklearn
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(feature_vectors)
            
            clustering = DBSCAN(eps=0.5, min_samples=self.min_pattern_occurrences)
            cluster_labels = clustering.fit_predict(normalized_features)
            
            unique_labels = set(cluster_labels)
        else:
            # Simple clustering based on similar features
            print("📊 Using basic pattern grouping (sklearn not available)")
            cluster_labels = []
            unique_labels = set()
            
            # Group by similar RSI ranges
            for i, context in enumerate(market_contexts):
                if context.rsi < 30:
                    cluster_labels.append(0)  # Oversold cluster
                elif context.rsi > 70:
                    cluster_labels.append(1)  # Overbought cluster  
                else:
                    cluster_labels.append(2)  # Neutral cluster
            
            unique_labels = set(cluster_labels)
        
        # Analyze each cluster
        for label in unique_labels:
            if label == -1:  # Noise cluster
                continue
                
            cluster_indices = [i for i, l in enumerate(cluster_labels) if l == label]
            cluster_contexts = [market_contexts[i] for i in cluster_indices]
            cluster_outcomes = [outcomes[i] for i in cluster_indices if i < len(outcomes)]
            
            if len(cluster_outcomes) >= self.min_pattern_occurrences:
                pattern = self._create_pattern_from_cluster(cluster_contexts, cluster_outcomes, label)
                if pattern and pattern.statistical_significance < self.significance_threshold:
                    patterns.append(pattern)
        
        return patterns
    
    def _create_pattern_from_cluster(self, contexts: List[MarketContext], outcomes: List[Dict], cluster_id: int) -> Optional[AdvancedPattern]:
        """Create pattern from clustered market contexts and outcomes"""
        if not contexts or not outcomes:
            return None
        
        # Calculate pattern characteristics
        rsi_values = [c.rsi for c in contexts]
        volatilities = [c.volatility for c in contexts]
        supply_chains = [c.supply_chain for c in contexts]
        returns = [o.get('return', 0.0) for o in outcomes]
        
        # Statistical validation
        if len(returns) < 3:
            return None
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Statistical significance testing (with fallback)
        if SCIPY_AVAILABLE:
            t_stat, p_value = stats.ttest_1samp(returns, 0.0)
            # Confidence interval
            confidence_interval = stats.t.interval(
                0.95, len(returns)-1, 
                loc=mean_return, 
                scale=stats.sem(returns)
            )
        else:
            # Basic approximation without scipy
            p_value = 0.05 if abs(mean_return) > std_return else 0.5
            margin = 1.96 * std_return / np.sqrt(len(returns))  # 95% CI approximation
            confidence_interval = (mean_return - margin, mean_return + margin)
        
        # Determine success probability
        positive_returns = sum(1 for r in returns if r > 0)
        success_probability = positive_returns / len(returns)
        
        # Pattern metadata
        price_trends = [c.price_change_24h for c in contexts]
        avg_trend = np.mean(price_trends)
        
        price_trend = 'bullish' if avg_trend > 2.0 else 'bearish' if avg_trend < -2.0 else 'sideways'
        
        avg_volatility = np.mean(volatilities)
        volatility_regime = 'high' if avg_volatility > 0.7 else 'medium' if avg_volatility > 0.3 else 'low'
        
        # Create pattern
        pattern = AdvancedPattern(
            pattern_id=f"cluster_{cluster_id}_{datetime.now().strftime('%Y%m%d')}",
            pattern_hash="",  # Will be set by __post_init__
            price_trend=price_trend,
            volatility_regime=volatility_regime,
            volume_profile='normal',  # Simplified for now
            rsi_range=(min(rsi_values), max(rsi_values)),
            rsi_trend='stable',  # Simplified for now
            supply_chain_avg=np.mean(supply_chains),
            supply_chain_volatility=np.std(supply_chains),
            price_sequence=[c.price for c in contexts[-5:]],
            rsi_sequence=rsi_values[-5:],
            volume_sequence=[c.volume_24h for c in contexts[-5:]],
            success_probability=success_probability,
            avg_return=mean_return,
            max_drawdown=min(returns) if returns else 0.0,
            time_to_profit=120,  # Default 2 hours
            statistical_significance=p_value,
            sample_size=len(returns),
            confidence_interval=confidence_interval,
            first_seen=min(c.timestamp for c in contexts),
            last_seen=max(c.timestamp for c in contexts),
            occurrence_count=len(contexts),
            market_conditions={"cluster_id": cluster_id}
        )
        
        return pattern
    
    def match_current_conditions(self, current_context: MarketContext) -> List[Tuple[AdvancedPattern, float]]:
        """Find patterns matching current market conditions with similarity scores"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT pattern_data FROM advanced_patterns')
        rows = cursor.fetchall()
        conn.close()
        
        matches = []
        
        for row in rows:
            pattern_data = json.loads(row[0])
            # Convert datetime strings back to datetime objects
            pattern_data['first_seen'] = datetime.fromisoformat(pattern_data['first_seen'])
            pattern_data['last_seen'] = datetime.fromisoformat(pattern_data['last_seen'])
            pattern = AdvancedPattern(**pattern_data)
            
            # Calculate similarity score
            similarity = self._calculate_pattern_similarity(pattern, current_context)
            
            if similarity > 0.7:  # 70% similarity threshold
                matches.append((pattern, similarity))
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def _calculate_pattern_similarity(self, pattern: AdvancedPattern, context: MarketContext) -> float:
        """Calculate similarity between pattern and current context"""
        similarity_score = 0.0
        
        # RSI similarity (30% weight)
        rsi_min, rsi_max = pattern.rsi_range
        if rsi_min <= context.rsi <= rsi_max:
            similarity_score += 0.3
        else:
            # Penalize based on distance
            distance = min(abs(context.rsi - rsi_min), abs(context.rsi - rsi_max))
            similarity_score += max(0, 0.3 * (1 - distance / 50))
        
        # Volatility similarity (25% weight)
        vol_map = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        pattern_vol = vol_map.get(pattern.volatility_regime, 0.5)
        vol_similarity = 1 - abs(pattern_vol - context.volatility)
        similarity_score += 0.25 * max(0, vol_similarity)
        
        # Supply chain similarity (20% weight)
        sc_similarity = 1 - abs(pattern.supply_chain_avg - context.supply_chain) / 2.0
        similarity_score += 0.20 * max(0, sc_similarity)
        
        # Price trend similarity (15% weight)
        current_trend = 'bullish' if context.price_change_24h > 2 else 'bearish' if context.price_change_24h < -2 else 'sideways'
        if current_trend == pattern.price_trend:
            similarity_score += 0.15
        
        # Time decay factor (10% weight)
        days_old = (datetime.now() - pattern.last_seen).days
        decay_factor = max(0, 1 - days_old / self.pattern_decay_days)
        similarity_score += 0.10 * decay_factor
        
        return min(1.0, similarity_score)
    
    def save_pattern(self, pattern: AdvancedPattern):
        """Save pattern to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert pattern to dict and handle datetime serialization
        pattern_dict = asdict(pattern)
        pattern_dict['first_seen'] = pattern.first_seen.isoformat()
        pattern_dict['last_seen'] = pattern.last_seen.isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO advanced_patterns
            (pattern_id, pattern_hash, pattern_data, statistical_data, created_at, updated_at, occurrence_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.pattern_id,
            pattern.pattern_hash,
            json.dumps(pattern_dict, cls=NumpyEncoder),
            json.dumps({
                'significance': float(pattern.statistical_significance),
                'confidence_interval': [float(x) for x in pattern.confidence_interval],
                'sample_size': int(pattern.sample_size)
            }),
            pattern.first_seen.isoformat(),
            datetime.now().isoformat(),
            pattern.occurrence_count
        ))
        
        conn.commit()
        conn.close()
    
    def get_pattern_insights(self) -> Dict:
        """Get insights about learned patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT pattern_data FROM advanced_patterns')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"total_patterns": 0}
        
        patterns = []
        for row in rows:
            pattern_data = json.loads(row[0])
            # Convert datetime strings back to datetime objects
            pattern_data['first_seen'] = datetime.fromisoformat(pattern_data['first_seen'])
            pattern_data['last_seen'] = datetime.fromisoformat(pattern_data['last_seen'])
            patterns.append(AdvancedPattern(**pattern_data))
        
        # Calculate insights
        total_patterns = len(patterns)
        avg_success_rate = np.mean([p.success_probability for p in patterns])
        significant_patterns = sum(1 for p in patterns if p.statistical_significance < 0.05)
        
        best_pattern = max(patterns, key=lambda p: p.avg_return)
        worst_pattern = min(patterns, key=lambda p: p.avg_return)
        
        return {
            "total_patterns": total_patterns,
            "significant_patterns": significant_patterns,
            "avg_success_rate": avg_success_rate,
            "best_pattern_return": best_pattern.avg_return,
            "worst_pattern_return": worst_pattern.avg_return,
            "pattern_diversity": len(set(p.pattern_hash for p in patterns))
        }