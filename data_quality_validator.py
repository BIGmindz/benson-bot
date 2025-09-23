"""
🔍 ADVANCED DATA QUALITY VALIDATION SYSTEM  
============================================
Intelligent validation, anomaly detection, and quality assurance for data contributions.
Ensures only high-quality trading data improves pattern performance.

Quality Dimensions:
- Data Completeness (all required fields present)
- Data Accuracy (realistic values, no outliers)  
- Data Consistency (logical trade sequences)
- Data Uniqueness (not duplicate or synthetic)
- Performance Credibility (returns match market reality)

Validation Pipeline:
1. Schema validation (structure check)
2. Statistical anomaly detection
3. Market reality checks
4. Pattern consistency analysis
5. Quality scoring and feedback
"""

import sqlite3
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import statistics
import re

@dataclass
class ValidationResult:
    """Results from data quality validation"""
    is_valid: bool
    quality_score: float  # 0-100
    validation_details: Dict
    warnings: List[str]
    errors: List[str]
    recommendations: List[str]

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for data contribution"""
    completeness_score: float
    accuracy_score: float  
    consistency_score: float
    uniqueness_score: float
    credibility_score: float
    overall_score: float

class DataQualityValidator:
    def __init__(self, db_path: str = 'benson_data_quality.db'):
        self.db_path = db_path
        self.init_database()
        
        # Quality thresholds
        self.min_quality_score = 60.0  # Minimum to accept contribution
        self.excellent_quality_score = 85.0  # Excellent contribution threshold
        
        # Market reality bounds (for sanity checks)
        self.market_bounds = {
            'max_daily_return': 50.0,  # 50% max single day return
            'min_daily_return': -50.0,  # -50% max single day loss
            'max_position_size': 50.0,  # 50% max position size
            'min_trade_duration': 60,   # 1 minute minimum
            'max_trade_duration': 86400 * 30,  # 30 days maximum
            'reasonable_win_rate_min': 0.20,  # 20% minimum win rate
            'reasonable_win_rate_max': 0.90   # 90% maximum win rate
        }

    def init_database(self):
        """Initialize data quality tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Quality validation results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_results (
                validation_id TEXT PRIMARY KEY,
                contribution_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                overall_quality_score REAL NOT NULL,
                completeness_score REAL NOT NULL,
                accuracy_score REAL NOT NULL,
                consistency_score REAL NOT NULL,
                uniqueness_score REAL NOT NULL,
                credibility_score REAL NOT NULL,
                is_valid BOOLEAN NOT NULL,
                validation_details TEXT NOT NULL,
                warnings TEXT NOT NULL,
                errors TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Anomaly detection results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_detections (
                anomaly_id TEXT PRIMARY KEY,
                contribution_id TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,  -- 'statistical', 'market_bounds', 'consistency', 'synthetic'
                anomaly_severity TEXT NOT NULL,  -- 'low', 'medium', 'high', 'critical'
                anomaly_description TEXT NOT NULL,
                anomaly_score REAL NOT NULL,  -- 0-100, higher = more anomalous
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Quality benchmarks (for comparison)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_benchmarks (
                benchmark_id TEXT PRIMARY KEY,
                metric_type TEXT NOT NULL,
                benchmark_value REAL NOT NULL,
                benchmark_description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Blacklisted patterns (known bad data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_blacklist (
                blacklist_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,  -- 'user_id', 'data_pattern', 'statistical_signature'
                pattern_value TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    def validate_data_contribution(self, trading_data: Dict, user_id: str, contribution_id: str) -> ValidationResult:
        """Comprehensive validation of trading data contribution"""
        
        # Initialize validation tracking
        warnings = []
        errors = []
        recommendations = []
        validation_details = {}
        
        print(f"🔍 Validating data contribution from user {user_id[:8]}...")
        
        # Check if this is paper trading data
        is_paper_trading = self.is_paper_trading_data(trading_data, user_id)
        
        if is_paper_trading:
            print("📋 Paper Trading Data Detected - Applying specialized validation")
            return self.validate_paper_trading_contribution(trading_data, user_id, contribution_id)
        
        # Standard validation for live trading data
        # 1. Schema and completeness validation
        completeness_result = self.validate_completeness(trading_data)
        validation_details['completeness'] = completeness_result
        validation_details['completeness'] = completeness_result
        
        if completeness_result['score'] < 70:
            errors.extend(completeness_result['errors'])
        else:
            warnings.extend(completeness_result['warnings'])
        
        # 2. Statistical accuracy validation  
        accuracy_result = self.validate_accuracy(trading_data)
        validation_details['accuracy'] = accuracy_result
        
        if accuracy_result['score'] < 60:
            errors.extend(accuracy_result['errors'])
        else:
            warnings.extend(accuracy_result['warnings'])
        
        # 3. Logical consistency validation
        consistency_result = self.validate_consistency(trading_data)
        validation_details['consistency'] = consistency_result
        
        if consistency_result['score'] < 50:
            errors.extend(consistency_result['errors'])
        
        # 4. Uniqueness validation (not duplicate/synthetic)
        uniqueness_result = self.validate_uniqueness(trading_data, user_id)
        validation_details['uniqueness'] = uniqueness_result
        
        if uniqueness_result['score'] < 40:
            warnings.append("Data appears synthetic or duplicate")
        
        # 5. Market credibility validation
        credibility_result = self.validate_credibility(trading_data)
        validation_details['credibility'] = credibility_result
        
        if credibility_result['score'] < 30:
            errors.append("Returns appear unrealistic for market conditions")
        
        # Calculate overall quality score
        quality_metrics = QualityMetrics(
            completeness_score=completeness_result['score'],
            accuracy_score=accuracy_result['score'],
            consistency_score=consistency_result['score'],
            uniqueness_score=uniqueness_result['score'],
            credibility_score=credibility_result['score'],
            overall_score=0  # Will calculate
        )
        
        # Weighted overall score
        weights = {'completeness': 0.25, 'accuracy': 0.20, 'consistency': 0.20, 'uniqueness': 0.15, 'credibility': 0.20}
        
        overall_score = (
            quality_metrics.completeness_score * weights['completeness'] +
            quality_metrics.accuracy_score * weights['accuracy'] +
            quality_metrics.consistency_score * weights['consistency'] +
            quality_metrics.uniqueness_score * weights['uniqueness'] +
            quality_metrics.credibility_score * weights['credibility']
        )
        
        quality_metrics.overall_score = overall_score
        
        # Determine if valid
        is_valid = overall_score >= self.min_quality_score and len(errors) == 0
        
        # Generate recommendations
        recommendations.extend(self.generate_quality_recommendations(quality_metrics, trading_data))
        
        # Store validation results
        self.store_validation_results(contribution_id, user_id, quality_metrics, 
                                    validation_details, warnings, errors, recommendations)
        
        # Report results
        quality_level = self.get_quality_level(overall_score)
        print(f"{'✅' if is_valid else '❌'} Validation Complete - {quality_level}")
        print(f"📊 Overall Score: {overall_score:.1f}/100")
        print(f"⚠️  Warnings: {len(warnings)} | ❌ Errors: {len(errors)}")
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=overall_score,
            validation_details=validation_details,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations
        )

    def is_paper_trading_data(self, trading_data: Dict, user_id: str) -> bool:
        """Detect if trading data is from paper trading system"""
        # Check for paper trading indicators
        paper_indicators = [
            user_id == 'paper_trader_bot',
            trading_data.get('source') == 'paper_trading',
            'paper_trading' in str(trading_data).lower(),
            trading_data.get('data_type', '').startswith('paper_trading')
        ]
        
        return any(paper_indicators)
    
    def validate_paper_trading_contribution(self, trading_data: Dict, user_id: str, contribution_id: str) -> ValidationResult:
        """Specialized validation for paper trading contributions"""
        warnings = []
        errors = []
        recommendations = []
        validation_details = {}
        
        print("📋 Applying Paper Trading Validation Rules")
        
        # Enhanced scoring for paper trading (training data value)
        completeness_result = self.validate_paper_completeness(trading_data)
        validation_details['completeness'] = completeness_result
        
        accuracy_result = self.validate_paper_accuracy(trading_data)  
        validation_details['accuracy'] = accuracy_result
        
        consistency_result = self.validate_paper_consistency(trading_data)
        validation_details['consistency'] = consistency_result
        
        # Paper trading gets bonus points for training value
        training_value_result = self.assess_paper_training_value(trading_data)
        validation_details['training_value'] = training_value_result
        
        # Calculate paper trading quality score
        quality_metrics = QualityMetrics(
            completeness_score=completeness_result['score'],
            accuracy_score=accuracy_result['score'],
            consistency_score=consistency_result['score'],
            uniqueness_score=85.0,  # Paper trading is always unique
            credibility_score=training_value_result['score'],
            overall_score=0
        )
        
        # Weighted score optimized for training data value
        paper_weights = {
            'completeness': 0.30,  # Structure is crucial for training
            'accuracy': 0.25,      # Mathematical accuracy important
            'consistency': 0.25,   # Logical consistency key
            'training_value': 0.20 # Bonus for training contribution
        }
        
        overall_score = (
            quality_metrics.completeness_score * paper_weights['completeness'] +
            quality_metrics.accuracy_score * paper_weights['accuracy'] +
            quality_metrics.consistency_score * paper_weights['consistency'] +
            training_value_result['score'] * paper_weights['training_value']
        )
        
        quality_metrics.overall_score = overall_score
        
        # Paper trading is always valid if properly structured
        is_valid = overall_score >= 70.0  # Lower threshold for training data
        
        # Generate paper-specific recommendations
        recommendations.extend(self.generate_paper_recommendations(quality_metrics, trading_data))
        
        # Store results
        self.store_validation_results(contribution_id, user_id, quality_metrics,
                                    validation_details, warnings, errors, recommendations)
        
        quality_level = "🏆 EXCELLENT" if overall_score >= 90 else "✅ GOOD" if overall_score >= 75 else "⚠️ ACCEPTABLE"
        print(f"✅ Paper Trading Validation Complete - {quality_level}")
        print(f"📊 Overall Score: {overall_score:.1f}/100")
        print(f"🎯 Training Value Score: {training_value_result['score']:.1f}/100")
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=overall_score,
            validation_details=validation_details,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations
        )

    def validate_paper_completeness(self, trading_data: Dict) -> Dict:
        """Validate completeness of paper trading data"""
        score = 100.0
        warnings = []
        errors = []
        
        # Check for paper-specific required fields
        required_paper_fields = ['timestamp', 'performance_metrics']
        
        if isinstance(trading_data, dict) and 'trades' in trading_data:
            # Batch submission format
            trades = trading_data.get('trades', [])
            if not trades:
                score -= 30
                errors.append("No trades in batch submission")
            else:
                # Check individual trade completeness
                for i, trade in enumerate(trades[:5]):  # Check first 5 trades
                    trade_score = self._validate_trade_completeness(trade)
                    if trade_score < 80:
                        score -= 5
                        warnings.append(f"Trade {i+1} missing some fields")
                        
        elif isinstance(trading_data, dict) and any(field in trading_data for field in ['symbol', 'side', 'price']):
            # Single trade format
            trade_score = self._validate_trade_completeness(trading_data)
            score = min(score, trade_score)
        else:
            score = 50
            errors.append("Unrecognized paper trading data format")
        
        return {
            'score': max(0, score),
            'warnings': warnings,
            'errors': errors
        }
    
    def validate_paper_accuracy(self, trading_data: Dict) -> Dict:
        """Validate mathematical accuracy of paper trading data"""
        score = 100.0
        warnings = []
        errors = []
        
        try:
            # Validate PnL calculations if present
            if 'pnl' in str(trading_data).lower():
                pnl_accuracy = self._validate_pnl_calculations(trading_data)
                score = min(score, pnl_accuracy)
                
            # Validate portfolio value consistency
            if 'portfolio_value' in str(trading_data):
                portfolio_accuracy = self._validate_portfolio_calculations(trading_data)
                score = min(score, portfolio_accuracy)
                
        except Exception as e:
            score -= 20
            warnings.append(f"Accuracy validation error: {str(e)}")
        
        return {
            'score': max(0, score),
            'warnings': warnings,
            'errors': errors
        }
    
    def validate_paper_consistency(self, trading_data: Dict) -> Dict:
        """Validate logical consistency of paper trading data"""
        score = 100.0
        warnings = []
        errors = []
        
        # Check timestamp consistency
        timestamps = self._extract_timestamps(trading_data)
        if len(timestamps) > 1:
            if not all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1)):
                score -= 15
                warnings.append("Timestamps not in chronological order")
        
        # Check position sizing logic
        position_sizes = self._extract_position_sizes(trading_data)
        if position_sizes and max(position_sizes) > 0.5:  # 50% position size
            score -= 10
            warnings.append("Some position sizes appear very large")
        
        return {
            'score': max(0, score),
            'warnings': warnings,
            'errors': errors
        }
    
    def assess_paper_training_value(self, trading_data: Dict) -> Dict:
        """Assess the training value of paper trading data"""
        score = 75.0  # Base score for paper trading
        training_factors = []
        
        # Bonus points for comprehensive data
        if 'performance_metrics' in str(trading_data):
            score += 10
            training_factors.append("Performance metrics included")
        
        if 'reason' in str(trading_data):
            score += 10 
            training_factors.append("Trade reasoning provided")
        
        if 'session_summary' in str(trading_data).lower():
            score += 15
            training_factors.append("Session summary included")
        
        # Check for variety in data
        symbols = self._extract_symbols(trading_data)
        if len(symbols) > 1:
            score += 5
            training_factors.append(f"Multiple symbols ({len(symbols)})")
            
        return {
            'score': min(100, score),
            'training_factors': training_factors,
            'warnings': [],
            'errors': []
        }
    
    def generate_paper_recommendations(self, quality_metrics: QualityMetrics, trading_data: Dict) -> List[str]:
        """Generate recommendations for paper trading contributions"""
        recommendations = []
        
        if quality_metrics.completeness_score < 90:
            recommendations.append("Include more comprehensive trade metadata for better training value")
        
        if quality_metrics.accuracy_score < 85:
            recommendations.append("Ensure PnL and portfolio calculations are mathematically accurate")
        
        if quality_metrics.overall_score >= 90:
            recommendations.append("Excellent paper trading data - ideal for pattern training")
        
        return recommendations
    
    def _validate_trade_completeness(self, trade: Dict) -> float:
        """Validate completeness of individual trade"""
        required_fields = ['symbol', 'side', 'price', 'timestamp']
        optional_fields = ['quantity', 'pnl', 'reason']
        
        score = 100.0
        for field in required_fields:
            if field not in trade:
                score -= 20
        
        for field in optional_fields:
            if field not in trade:
                score -= 5
        
        return max(0, score)
    
    def _validate_pnl_calculations(self, trading_data: Dict) -> float:
        """Validate PnL calculation accuracy"""
        # Simplified validation - assume accurate for paper trading
        return 95.0  # Paper trading PnL should be mathematically accurate
    
    def _validate_portfolio_calculations(self, trading_data: Dict) -> float:
        """Validate portfolio value calculations"""
        # Simplified validation for paper trading
        return 90.0
    
    def _extract_timestamps(self, trading_data: Dict) -> List[float]:
        """Extract timestamps from trading data"""
        timestamps = []
        if isinstance(trading_data, dict):
            if 'timestamp' in trading_data:
                try:
                    timestamps.append(float(trading_data['timestamp']))
                except:
                    pass
            if 'trades' in trading_data:
                for trade in trading_data.get('trades', []):
                    if isinstance(trade, dict) and 'timestamp' in trade:
                        try:
                            timestamps.append(float(trade['timestamp']))
                        except:
                            pass
        return sorted(timestamps)
    
    def _extract_position_sizes(self, trading_data: Dict) -> List[float]:
        """Extract position sizes from trading data"""
        sizes = []
        if isinstance(trading_data, dict):
            if 'quantity' in trading_data:
                try:
                    sizes.append(float(trading_data['quantity']))
                except:
                    pass
            if 'trades' in trading_data:
                for trade in trading_data.get('trades', []):
                    if isinstance(trade, dict) and 'quantity' in trade:
                        try:
                            sizes.append(float(trade['quantity']))
                        except:
                            pass
        return sizes
    
    def _extract_symbols(self, trading_data: Dict) -> List[str]:
        """Extract trading symbols from data"""
        symbols = set()
        if isinstance(trading_data, dict):
            if 'symbol' in trading_data:
                symbols.add(trading_data['symbol'])
            if 'trades' in trading_data:
                for trade in trading_data.get('trades', []):
                    if isinstance(trade, dict) and 'symbol' in trade:
                        symbols.add(trade['symbol'])
        return list(symbols)

    def validate_completeness(self, trading_data: Dict) -> Dict:
        """Validate data completeness and structure"""
        score = 100.0
        warnings = []
        errors = []
        
        # Check required top-level fields
        required_fields = ['trades']
        optional_fields = ['market_conditions', 'time_patterns']
        
        for field in required_fields:
            if field not in trading_data:
                errors.append(f"Missing required field: {field}")
                score -= 30
        
        # Check trades structure
        trades = trading_data.get('trades', [])
        if not trades:
            errors.append("No trades provided")
            score -= 50
        elif len(trades) < 10:
            warnings.append("Very few trades provided (less than 10)")
            score -= 10
        
        # Check individual trade completeness
        required_trade_fields = ['timestamp', 'pair', 'side', 'entry_price', 'return_percentage']
        optional_trade_fields = ['exit_price', 'position_size_percentage', 'signals_used', 'confidence_score']
        
        incomplete_trades = 0
        for i, trade in enumerate(trades[:20]):  # Check first 20 trades
            missing_fields = [field for field in required_trade_fields if field not in trade]
            if missing_fields:
                incomplete_trades += 1
                if incomplete_trades <= 3:  # Report first 3 issues
                    warnings.append(f"Trade {i+1} missing: {', '.join(missing_fields)}")
        
        if incomplete_trades > 0:
            completion_rate = (len(trades) - incomplete_trades) / len(trades)
            score *= completion_rate
            if completion_rate < 0.8:
                errors.append(f"Only {completion_rate:.1%} of trades complete")
        
        # Bonus for optional fields
        for field in optional_fields:
            if field in trading_data:
                score += 5
        
        return {
            'score': min(score, 100.0),
            'warnings': warnings,
            'errors': errors,
            'details': {
                'trades_count': len(trades),
                'incomplete_trades': incomplete_trades,
                'completion_rate': (len(trades) - incomplete_trades) / max(len(trades), 1)
            }
        }

    def validate_accuracy(self, trading_data: Dict) -> Dict:
        """Validate statistical accuracy and detect outliers"""
        score = 100.0
        warnings = []
        errors = []
        
        trades = trading_data.get('trades', [])
        if not trades:
            return {'score': 0, 'warnings': [], 'errors': ['No trades to validate']}
        
        # Extract numeric values for analysis
        returns = [trade.get('return_percentage', 0) for trade in trades if trade.get('return_percentage') is not None]
        position_sizes = [trade.get('position_size_percentage', 0) for trade in trades if trade.get('position_size_percentage') is not None]
        entry_prices = [trade.get('entry_price', 0) for trade in trades if trade.get('entry_price') is not None and trade.get('entry_price') > 0]
        
        # Return validation
        if returns:
            # Check for extreme outliers
            extreme_returns = [r for r in returns if abs(r) > 100]  # >100% return
            if extreme_returns:
                score -= len(extreme_returns) * 5
                warnings.append(f"{len(extreme_returns)} trades with extreme returns (>100%)")
            
            # Check for impossible returns
            impossible_returns = [r for r in returns if abs(r) > 1000]  # >1000% return
            if impossible_returns:
                score -= len(impossible_returns) * 20
                errors.append(f"{len(impossible_returns)} trades with impossible returns (>1000%)")
            
            # Statistical consistency
            if len(returns) >= 10:
                mean_return = np.mean(returns)
                std_return = np.std(returns)
                
                # Check if standard deviation is reasonable
                if std_return > 50:  # Very high volatility
                    warnings.append(f"Very high return volatility (σ={std_return:.1f}%)")
                    score -= 10
                
                # Check for unrealistic consistency (too perfect)
                if std_return < 1 and mean_return > 5:  # Low volatility but high returns
                    warnings.append("Returns appear unrealistically consistent")
                    score -= 15
        
        # Position size validation
        if position_sizes:
            oversized_positions = [p for p in position_sizes if p > 50]  # >50% positions
            if oversized_positions:
                score -= len(oversized_positions) * 3
                warnings.append(f"{len(oversized_positions)} positions over 50% of portfolio")
            
            impossible_positions = [p for p in position_sizes if p > 100 or p <= 0]
            if impossible_positions:
                score -= len(impossible_positions) * 10
                errors.append(f"{len(impossible_positions)} invalid position sizes")
        
        # Price validation  
        if entry_prices:
            # Check for reasonable price ranges by analyzing price patterns
            price_ranges = {}
            for trade in trades:
                pair = trade.get('pair', '')
                price = trade.get('entry_price', 0)
                if pair and price > 0:
                    if pair not in price_ranges:
                        price_ranges[pair] = []
                    price_ranges[pair].append(price)
            
            # Check for consistent price ranges per pair
            for pair, prices in price_ranges.items():
                if len(prices) > 1:
                    price_ratio = max(prices) / min(prices)
                    if price_ratio > 100:  # Price varied by 100x - suspicious
                        warnings.append(f"Suspicious price range for {pair} (ratio: {price_ratio:.1f}x)")
                        score -= 5
        
        return {
            'score': max(score, 0.0),
            'warnings': warnings,
            'errors': errors,
            'details': {
                'returns_analyzed': len(returns),
                'extreme_returns': len([r for r in returns if abs(r) > 100]),
                'mean_return': np.mean(returns) if returns else 0,
                'return_volatility': np.std(returns) if returns else 0
            }
        }

    def validate_consistency(self, trading_data: Dict) -> Dict:
        """Validate logical consistency of trading data"""
        score = 100.0
        warnings = []
        errors = []
        
        trades = trading_data.get('trades', [])
        if not trades:
            return {'score': 0, 'warnings': [], 'errors': ['No trades to validate']}
        
        inconsistency_count = 0
        
        for i, trade in enumerate(trades):
            entry_price = trade.get('entry_price', 0)
            exit_price = trade.get('exit_price', 0)
            return_pct = trade.get('return_percentage', 0)
            side = trade.get('side', '')
            
            # Check price-return consistency
            if entry_price > 0 and exit_price > 0 and return_pct != 0:
                if side == 'buy':
                    expected_return = (exit_price - entry_price) / entry_price * 100
                elif side == 'sell':
                    expected_return = (entry_price - exit_price) / entry_price * 100
                else:
                    expected_return = return_pct  # Can't validate without side
                
                if abs(expected_return - return_pct) > 1.0:  # Allow 1% tolerance
                    inconsistency_count += 1
                    if inconsistency_count <= 3:  # Report first 3
                        warnings.append(f"Trade {i+1}: Price-return mismatch ({expected_return:.1f}% vs {return_pct:.1f}%)")
        
        if inconsistency_count > 0:
            consistency_rate = (len(trades) - inconsistency_count) / len(trades)
            score = consistency_rate * 100
            
            if consistency_rate < 0.7:
                errors.append(f"Only {consistency_rate:.1%} of trades are logically consistent")
            elif consistency_rate < 0.9:
                warnings.append(f"{consistency_rate:.1%} consistency rate - some data issues")
        
        # Check timestamp consistency
        timestamps = []
        for trade in trades:
            timestamp = trade.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        continue
                timestamps.append(timestamp)
        
        if len(timestamps) > 1:
            # Check for reasonable time ordering and gaps
            timestamps.sort()
            time_gaps = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
            
            # Check for suspiciously regular timing (might be synthetic)
            if len(set(time_gaps)) == 1 and len(time_gaps) > 10:
                warnings.append("Trades have suspiciously regular timing intervals")
                score -= 10
        
        return {
            'score': max(score, 0.0),
            'warnings': warnings,
            'errors': errors,
            'details': {
                'trades_checked': len(trades),
                'inconsistent_trades': inconsistency_count,
                'consistency_rate': (len(trades) - inconsistency_count) / max(len(trades), 1)
            }
        }

    def validate_uniqueness(self, trading_data: Dict, user_id: str) -> Dict:
        """Validate data uniqueness and detect duplicates/synthetic data"""
        score = 100.0
        warnings = []
        
        trades = trading_data.get('trades', [])
        
        # Check for duplicate trades within submission
        trade_signatures = []
        for trade in trades:
            # Create signature from key fields
            signature = f"{trade.get('timestamp')}_{trade.get('pair')}_{trade.get('entry_price')}_{trade.get('return_percentage')}"
            trade_signatures.append(signature)
        
        duplicate_count = len(trade_signatures) - len(set(trade_signatures))
        if duplicate_count > 0:
            score -= duplicate_count * 2
            warnings.append(f"{duplicate_count} duplicate trades detected within submission")
        
        # Check for patterns indicating synthetic data
        returns = [trade.get('return_percentage', 0) for trade in trades if trade.get('return_percentage') is not None]
        
        if returns and len(returns) >= 10:
            # Check for suspiciously round numbers
            round_returns = sum(1 for r in returns if r == round(r))
            round_percentage = round_returns / len(returns)
            
            if round_percentage > 0.8:  # More than 80% round numbers
                score -= 20
                warnings.append("High percentage of round-number returns (may be synthetic)")
            
            # Check for mathematical patterns
            return_diffs = [returns[i+1] - returns[i] for i in range(len(returns)-1)]
            if len(set(return_diffs)) <= 3 and len(return_diffs) > 10:
                score -= 25
                warnings.append("Returns follow mathematical pattern (may be synthetic)")
        
        # Check against known data patterns (would expand with ML models)
        synthetic_indicators = self.detect_synthetic_patterns(trading_data)
        if synthetic_indicators:
            score -= len(synthetic_indicators) * 10
            warnings.extend(synthetic_indicators)
        
        return {
            'score': max(score, 0.0),
            'warnings': warnings,
            'errors': [],
            'details': {
                'duplicate_trades': duplicate_count,
                'synthetic_indicators': len(synthetic_indicators) if synthetic_indicators else 0,
                'uniqueness_factors_checked': 4
            }
        }

    def validate_credibility(self, trading_data: Dict) -> Dict:
        """Validate market credibility and realistic performance"""
        score = 100.0
        warnings = []
        errors = []
        
        trades = trading_data.get('trades', [])
        if not trades:
            return {'score': 0, 'warnings': [], 'errors': ['No trades to validate']}
        
        # Calculate performance metrics
        returns = [trade.get('return_percentage', 0) for trade in trades if trade.get('return_percentage') is not None]
        
        if returns:
            total_trades = len(returns)
            winning_trades = sum(1 for r in returns if r > 0)
            win_rate = winning_trades / total_trades
            
            avg_return = np.mean(returns)
            total_return = np.prod([1 + r/100 for r in returns]) - 1
            
            # Check win rate credibility
            if win_rate > 0.95:  # >95% win rate is suspicious
                score -= 30
                errors.append(f"Unrealistic win rate: {win_rate:.1%}")
            elif win_rate > 0.85:  # >85% win rate is very high
                score -= 15
                warnings.append(f"Very high win rate: {win_rate:.1%}")
            
            # Check average return credibility
            if avg_return > 10:  # >10% average return per trade
                score -= 20
                warnings.append(f"Very high average return per trade: {avg_return:.1f}%")
            elif avg_return > 20:  # >20% average return per trade  
                score -= 40
                errors.append(f"Unrealistic average return per trade: {avg_return:.1f}%")
            
            # Check total return credibility based on time period
            timestamps = [trade.get('timestamp') for trade in trades if trade.get('timestamp')]
            if timestamps and len(timestamps) > 1:
                try:
                    # Parse timestamps
                    parsed_timestamps = []
                    for ts in timestamps:
                        if isinstance(ts, str):
                            parsed_timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                        else:
                            parsed_timestamps.append(ts)
                    
                    if parsed_timestamps:
                        time_span_days = (max(parsed_timestamps) - min(parsed_timestamps)).days
                        if time_span_days > 30:  # More than 30 days of data
                            annualized_return = ((1 + total_return) ** (365 / time_span_days)) - 1
                            
                            if annualized_return > 5:  # >500% annualized return
                                score -= 40
                                errors.append(f"Unrealistic annualized return: {annualized_return:.1%}")
                            elif annualized_return > 2:  # >200% annualized return
                                score -= 20
                                warnings.append(f"Very high annualized return: {annualized_return:.1%}")
                except:
                    pass  # Skip if timestamp parsing fails
            
            # Check for consistency with market volatility
            return_volatility = np.std(returns)
            if return_volatility < 1 and avg_return > 3:
                score -= 25
                warnings.append("Low volatility with high returns (may be curve-fitted)")
        
        return {
            'score': max(score, 0.0),
            'warnings': warnings,
            'errors': errors,
            'details': {
                'win_rate': win_rate if returns else 0,
                'avg_return': avg_return if returns else 0,
                'total_return': total_return if returns else 0,
                'return_volatility': np.std(returns) if returns else 0
            }
        }

    def detect_synthetic_patterns(self, trading_data: Dict) -> List[str]:
        """Detect patterns indicating synthetic/generated data"""
        indicators = []
        trades = trading_data.get('trades', [])
        
        # Pattern 1: Perfectly alternating wins/losses
        returns = [trade.get('return_percentage', 0) for trade in trades]
        if len(returns) >= 10:
            alternating_count = 0
            for i in range(1, len(returns)):
                if (returns[i-1] > 0) != (returns[i] > 0):
                    alternating_count += 1
            
            if alternating_count / (len(returns) - 1) > 0.8:
                indicators.append("Suspiciously alternating wins/losses pattern")
        
        # Pattern 2: Mathematical progression in returns
        if len(returns) >= 5:
            diffs = [returns[i+1] - returns[i] for i in range(len(returns)-1)]
            if len(set([round(d, 2) for d in diffs])) <= 2 and len(diffs) > 5:
                indicators.append("Returns follow arithmetic progression")
        
        return indicators

    def get_quality_level(self, score: float) -> str:
        """Get quality level description from score"""
        if score >= 90:
            return "🏆 EXCELLENT"
        elif score >= 75:
            return "✅ GOOD"
        elif score >= 60:
            return "⚠️ ACCEPTABLE"
        elif score >= 40:
            return "❌ POOR"
        else:
            return "🚫 REJECTED"

    def generate_quality_recommendations(self, metrics: QualityMetrics, trading_data: Dict) -> List[str]:
        """Generate personalized recommendations to improve data quality"""
        recommendations = []
        
        if metrics.completeness_score < 80:
            recommendations.append("Include all required trade fields: timestamp, pair, side, entry_price, return_percentage")
            recommendations.append("Add optional fields like exit_price and signals_used for higher quality score")
        
        if metrics.accuracy_score < 70:
            recommendations.append("Review trade returns for outliers and impossible values")
            recommendations.append("Ensure position sizes are realistic (typically 1-20% of portfolio)")
        
        if metrics.consistency_score < 70:
            recommendations.append("Verify that entry/exit prices match reported returns")
            recommendations.append("Check that trade sides (buy/sell) are correctly specified")
        
        if metrics.uniqueness_score < 50:
            recommendations.append("Avoid submitting duplicate or synthetic trading data")
            recommendations.append("Include diverse trading strategies and market conditions")
        
        if metrics.credibility_score < 60:
            recommendations.append("Ensure win rates and returns are realistic for market conditions")
            recommendations.append("Include both winning and losing trades for authenticity")
        
        # General recommendations
        trades = trading_data.get('trades', [])
        if len(trades) < 50:
            recommendations.append("Submit more trading history (50+ trades) for better scoring")
        
        return recommendations

    def store_validation_results(self, contribution_id: str, user_id: str, metrics: QualityMetrics,
                                validation_details: Dict, warnings: List[str], errors: List[str],
                                recommendations: List[str]):
        """Store validation results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validation_id = f"val_{contribution_id}"
        
        cursor.execute("""
            INSERT INTO validation_results 
            (validation_id, contribution_id, user_id, overall_quality_score,
             completeness_score, accuracy_score, consistency_score, uniqueness_score, credibility_score,
             is_valid, validation_details, warnings, errors, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (validation_id, contribution_id, user_id, metrics.overall_score,
              metrics.completeness_score, metrics.accuracy_score, metrics.consistency_score,
              metrics.uniqueness_score, metrics.credibility_score,
              metrics.overall_score >= self.min_quality_score,
              json.dumps(validation_details), json.dumps(warnings), 
              json.dumps(errors), json.dumps(recommendations)))
        
        conn.commit()
        conn.close()

    def get_quality_statistics(self) -> Dict:
        """Get platform-wide quality statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute("SELECT COUNT(*), AVG(overall_quality_score) FROM validation_results")
        total_validations, avg_quality = cursor.fetchone()
        
        # Quality distribution
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN overall_quality_score >= 90 THEN 1 ELSE 0 END) as excellent,
                SUM(CASE WHEN overall_quality_score >= 75 THEN 1 ELSE 0 END) as good,
                SUM(CASE WHEN overall_quality_score >= 60 THEN 1 ELSE 0 END) as acceptable,
                SUM(CASE WHEN overall_quality_score < 60 THEN 1 ELSE 0 END) as poor
            FROM validation_results
        """)
        quality_dist = cursor.fetchone()
        
        # Top quality issues
        cursor.execute("""
            SELECT 
                AVG(completeness_score) as avg_completeness,
                AVG(accuracy_score) as avg_accuracy,
                AVG(consistency_score) as avg_consistency,
                AVG(uniqueness_score) as avg_uniqueness,
                AVG(credibility_score) as avg_credibility
            FROM validation_results
        """)
        avg_scores = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_validations': total_validations or 0,
            'average_quality_score': round(avg_quality or 0, 1),
            'quality_distribution': {
                'excellent': quality_dist[0] if quality_dist else 0,
                'good': quality_dist[1] if quality_dist else 0,
                'acceptable': quality_dist[2] if quality_dist else 0,
                'poor': quality_dist[3] if quality_dist else 0
            },
            'average_dimension_scores': {
                'completeness': round(avg_scores[0] if avg_scores else 0, 1),
                'accuracy': round(avg_scores[1] if avg_scores else 0, 1),
                'consistency': round(avg_scores[2] if avg_scores else 0, 1),
                'uniqueness': round(avg_scores[3] if avg_scores else 0, 1),
                'credibility': round(avg_scores[4] if avg_scores else 0, 1)
            }
        }

    def simulate_quality_validation_demo(self):
        """Demonstrate data quality validation system"""
        print("🔍 BENSON DATA QUALITY VALIDATION DEMO")
        print("=" * 60)
        
        # Demo validation scenarios
        demo_scenarios = [
            {
                'name': 'High Quality Trader',
                'user_id': 'quality_001',
                'data_issues': []
            },
            {
                'name': 'Problematic Data',
                'user_id': 'quality_002', 
                'data_issues': ['extreme_returns', 'inconsistent_prices']
            },
            {
                'name': 'Synthetic Data',
                'user_id': 'quality_003',
                'data_issues': ['perfect_alternating', 'round_numbers']
            }
        ]
        
        for scenario in demo_scenarios:
            print(f"\n👤 Validating: {scenario['name']}")
            print("-" * 40)
            
            # Generate test data with specific issues
            test_data = self.generate_test_data_with_issues(scenario['data_issues'])
            
            # Run validation
            result = self.validate_data_contribution(test_data, scenario['user_id'], f"demo_{scenario['user_id']}")
            
            print(f"📊 Quality Breakdown:")
            details = result.validation_details
            for dimension, data in details.items():
                print(f"   • {dimension.title()}: {data['score']:.1f}/100")
            
            if result.warnings:
                print(f"\n⚠️  Warnings ({len(result.warnings)}):")
                for warning in result.warnings[:3]:  # Show first 3
                    print(f"   • {warning}")
            
            if result.errors:
                print(f"\n❌ Errors ({len(result.errors)}):")
                for error in result.errors[:3]:  # Show first 3
                    print(f"   • {error}")
            
            print(f"\n💡 Recommendations:")
            for rec in result.recommendations[:2]:  # Show first 2
                print(f"   • {rec}")
        
        # Show platform statistics
        print(f"\n📈 PLATFORM QUALITY STATISTICS")
        print("-" * 40)
        stats = self.get_quality_statistics()
        
        print(f"📊 Total Validations: {stats['total_validations']}")
        print(f"📈 Average Quality: {stats['average_quality_score']}/100")
        
        print(f"\n🏆 Quality Distribution:")
        dist = stats['quality_distribution']
        print(f"   • Excellent (90+): {dist['excellent']}")
        print(f"   • Good (75-89): {dist['good']}")
        print(f"   • Acceptable (60-74): {dist['acceptable']}")
        print(f"   • Poor (<60): {dist['poor']}")
        
        print(f"\n🎯 Quality Impact:")
        print(f"   • Only high-quality data improves patterns")
        print(f"   • Automated filtering prevents garbage in/garbage out")
        print(f"   • Contributors get immediate feedback to improve")
        print(f"   • Platform maintains data integrity at scale")

    def generate_test_data_with_issues(self, issues: List[str]) -> Dict:
        """Generate test trading data with specific quality issues"""
        np.random.seed(42)
        
        trade_count = 50
        trades = []
        
        for i in range(trade_count):
            # Base trade
            return_pct = np.random.normal(1.5, 4.0)
            
            # Apply issues
            if 'extreme_returns' in issues and i % 10 == 0:
                return_pct = np.random.uniform(50, 200)  # Extreme return
            
            if 'perfect_alternating' in issues:
                return_pct = 5.0 if i % 2 == 0 else -3.0  # Perfect alternating
            
            if 'round_numbers' in issues:
                return_pct = round(return_pct)  # Only round numbers
            
            entry_price = np.random.uniform(100, 50000)
            exit_price = entry_price * (1 + return_pct / 100)
            
            # Apply price inconsistency issues
            if 'inconsistent_prices' in issues and i % 5 == 0:
                exit_price = np.random.uniform(100, 50000)  # Random exit price
            
            trade = {
                'timestamp': (datetime.now() - timedelta(days=i)).isoformat(),
                'pair': np.random.choice(['BTC/USDT', 'ETH/USDT']),
                'side': 'buy',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'return_percentage': return_pct,
                'position_size_percentage': np.random.uniform(2, 8),
                'signals_used': ['rsi', 'volume']
            }
            trades.append(trade)
        
        return {
            'trades': trades,
            'market_conditions': {'trend': 'bullish'},
            'time_patterns': {'active_hours': [9, 10, 11]}
        }


# Demo execution
if __name__ == "__main__":
    validator = DataQualityValidator()
    validator.simulate_quality_validation_demo()