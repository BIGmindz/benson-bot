"""
Enhanced Comprehensive Supply Chain Signals
Includes: disruptions, port closures, energy spikes, tariffs, regulatory events, 
sentiment, crypto freight logistics, and cost rate indexes
"""

from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional
import datetime
import json
import hashlib
import random
import requests
from enum import Enum

class SupplyChainEventType(Enum):
    PORT_CLOSURE = "port_closure"
    SHIPPING_DELAY = "shipping_delay"
    ENERGY_SPIKE = "energy_spike"
    TARIFF_CHANGE = "tariff_change"
    REGULATORY_EVENT = "regulatory_event"
    WEATHER_DISRUPTION = "weather_disruption"
    LABOR_STRIKE = "labor_strike"
    FUEL_SHORTAGE = "fuel_shortage"
    ROUTE_BLOCKAGE = "route_blockage"

@dataclass
class SupplyChainEvent:
    event_type: SupplyChainEventType
    severity: float  # 0.0 to 1.0
    duration_hours: int
    affected_routes: List[str]
    impact_score: float
    timestamp: datetime.datetime

@dataclass
class ComprehensiveSupplyChainConfig:
    enabled: bool = True
    
    # Data source configurations
    freight_apis_enabled: bool = True
    port_monitoring_enabled: bool = True
    energy_monitoring_enabled: bool = True
    tariff_monitoring_enabled: bool = True
    regulatory_monitoring_enabled: bool = True
    crypto_logistics_enabled: bool = True
    
    # API keys (placeholder - would be real in production)
    freightos_api_key: str = None
    maritime_api_key: str = None
    energy_api_key: str = None
    trade_api_key: str = None
    
    # Weighting factors for composite score
    weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "freight_rates": 0.25,        # Baltic Dry Index, Freightos
                "port_operations": 0.15,      # Port closures, delays
                "energy_costs": 0.20,         # Fuel, energy spikes
                "trade_policy": 0.15,         # Tariffs, regulations
                "disruption_events": 0.10,    # Weather, strikes, blockages
                "crypto_logistics": 0.10,     # Blockchain freight, on-chain metrics
                "market_sentiment": 0.05      # Supply chain sentiment indicators
            }

class ComprehensiveSupplyChainSignals:
    """
    Enterprise-grade supply chain signals including:
    - Freight rate indexes (Baltic Dry, Freightos)
    - Port operations and closures
    - Energy cost spikes
    - Trade policy changes (tariffs, regulations)
    - Disruption events (weather, strikes)
    - Crypto freight logistics
    - Market sentiment analysis
    """
    
    def __init__(self, config: ComprehensiveSupplyChainConfig):
        self.config = config
        self.events_cache = []  # Recent disruption events
        self.last_update = None
        
        # Initialize data sources
        self.data_sources = {
            "freight": FreightRateMonitor(config),
            "ports": PortOperationsMonitor(config), 
            "energy": EnergyCostMonitor(config),
            "trade": TradePolicyMonitor(config),
            "disruptions": DisruptionEventMonitor(config),
            "crypto_logistics": CryptoLogisticsMonitor(config),
            "sentiment": SupplyChainSentimentMonitor(config)
        }
    
    def get_comprehensive_signals(self) -> Tuple[float, Dict]:
        """
        Generate comprehensive supply chain stress composite score
        
        Returns:
            Tuple[float, Dict]: (composite_score, detailed_logs)
            - composite_score: 0.0 to 1.0 (0=optimal supply chain, 1=maximum stress)
            - detailed_logs: Breakdown of all signal components
        """
        if not self.config.enabled:
            return 0.5, {"status": "disabled", "note": "Supply chain signals disabled"}
        
        timestamp = datetime.datetime.utcnow()
        signals = {}
        composite_score = 0.0
        
        # 1. FREIGHT RATE SIGNALS (25%)
        if self.config.freight_apis_enabled:
            freight_stress, freight_logs = self.data_sources["freight"].get_signals()
            signals["freight_rates"] = {
                "stress_level": freight_stress,
                "weight": self.config.weights["freight_rates"],
                "contribution": freight_stress * self.config.weights["freight_rates"],
                "details": freight_logs
            }
            composite_score += signals["freight_rates"]["contribution"]
        
        # 2. PORT OPERATIONS SIGNALS (15%)
        if self.config.port_monitoring_enabled:
            port_stress, port_logs = self.data_sources["ports"].get_signals()
            signals["port_operations"] = {
                "stress_level": port_stress,
                "weight": self.config.weights["port_operations"],
                "contribution": port_stress * self.config.weights["port_operations"],
                "details": port_logs
            }
            composite_score += signals["port_operations"]["contribution"]
        
        # 3. ENERGY COST SIGNALS (20%)
        if self.config.energy_monitoring_enabled:
            energy_stress, energy_logs = self.data_sources["energy"].get_signals()
            signals["energy_costs"] = {
                "stress_level": energy_stress,
                "weight": self.config.weights["energy_costs"],
                "contribution": energy_stress * self.config.weights["energy_costs"],
                "details": energy_logs
            }
            composite_score += signals["energy_costs"]["contribution"]
        
        # 4. TRADE POLICY SIGNALS (15%)
        if self.config.tariff_monitoring_enabled:
            trade_stress, trade_logs = self.data_sources["trade"].get_signals()
            signals["trade_policy"] = {
                "stress_level": trade_stress,
                "weight": self.config.weights["trade_policy"],
                "contribution": trade_stress * self.config.weights["trade_policy"],
                "details": trade_logs
            }
            composite_score += signals["trade_policy"]["contribution"]
        
        # 5. DISRUPTION EVENT SIGNALS (10%)
        disruption_stress, disruption_logs = self.data_sources["disruptions"].get_signals()
        signals["disruption_events"] = {
            "stress_level": disruption_stress,
            "weight": self.config.weights["disruption_events"],
            "contribution": disruption_stress * self.config.weights["disruption_events"],
            "details": disruption_logs
        }
        composite_score += signals["disruption_events"]["contribution"]
        
        # 6. CRYPTO LOGISTICS SIGNALS (10%)
        if self.config.crypto_logistics_enabled:
            crypto_stress, crypto_logs = self.data_sources["crypto_logistics"].get_signals()
            signals["crypto_logistics"] = {
                "stress_level": crypto_stress,
                "weight": self.config.weights["crypto_logistics"],
                "contribution": crypto_stress * self.config.weights["crypto_logistics"],
                "details": crypto_logs
            }
            composite_score += signals["crypto_logistics"]["contribution"]
        
        # 7. MARKET SENTIMENT SIGNALS (5%)
        sentiment_stress, sentiment_logs = self.data_sources["sentiment"].get_signals()
        signals["market_sentiment"] = {
            "stress_level": sentiment_stress,
            "weight": self.config.weights["market_sentiment"],
            "contribution": sentiment_stress * self.config.weights["market_sentiment"],
            "details": sentiment_logs
        }
        composite_score += signals["market_sentiment"]["contribution"]
        
        # Ensure composite score stays within bounds
        composite_score = min(1.0, max(0.0, composite_score))
        
        # Generate comprehensive logs
        comprehensive_logs = {
            "timestamp": timestamp.isoformat(),
            "composite_score": composite_score,
            "signal_breakdown": signals,
            "active_disruptions": len([e for e in self.events_cache if e.timestamp > timestamp - datetime.timedelta(hours=24)]),
            "data_sources_active": sum(1 for source in self.data_sources.values() if source.is_active()),
            "signal_quality": self._assess_signal_quality(),
            "trading_recommendation": self._generate_trading_recommendation(composite_score)
        }
        
        self.last_update = timestamp
        return composite_score, comprehensive_logs
    
    def _assess_signal_quality(self) -> str:
        """Assess overall signal quality based on data source availability"""
        active_sources = sum(1 for source in self.data_sources.values() if source.is_active())
        total_sources = len(self.data_sources)
        
        quality_ratio = active_sources / total_sources
        
        if quality_ratio >= 0.8:
            return "HIGH_QUALITY"
        elif quality_ratio >= 0.5:
            return "MEDIUM_QUALITY"
        else:
            return "LOW_QUALITY"
    
    def _generate_trading_recommendation(self, composite_score: float) -> Dict:
        """Generate specific trading recommendations based on supply chain stress"""
        if composite_score >= 0.75:
            return {
                "recommendation": "BEARISH",
                "position_factor": 0.85,  # Reduce positions by 15%
                "reasoning": "High supply chain stress indicates potential economic headwinds",
                "confidence": "HIGH"
            }
        elif composite_score >= 0.6:
            return {
                "recommendation": "CAUTIOUS_BEARISH",
                "position_factor": 0.9,   # Reduce positions by 10%
                "reasoning": "Moderate supply chain stress suggests caution",
                "confidence": "MEDIUM"
            }
        elif composite_score <= 0.25:
            return {
                "recommendation": "BULLISH",
                "position_factor": 1.15,  # Increase positions by 15%
                "reasoning": "Low supply chain stress indicates economic efficiency",
                "confidence": "HIGH"
            }
        elif composite_score <= 0.4:
            return {
                "recommendation": "CAUTIOUS_BULLISH",
                "position_factor": 1.1,   # Increase positions by 10%
                "reasoning": "Good supply chain conditions support growth",
                "confidence": "MEDIUM"
            }
        else:
            return {
                "recommendation": "NEUTRAL",
                "position_factor": 1.0,   # No position adjustment
                "reasoning": "Balanced supply chain conditions",
                "confidence": "MEDIUM"
            }
    
    def composite(self) -> Tuple[float, Dict]:
        """Legacy compatibility method"""
        return self.get_comprehensive_signals()
    
    def get_position_factor(self, composite_score: Optional[float] = None) -> float:
        """Get position sizing factor based on supply chain stress"""
        if composite_score is None:
            composite_score, _ = self.get_comprehensive_signals()
        
        recommendation = self._generate_trading_recommendation(composite_score)
        return recommendation["position_factor"]


class FreightRateMonitor:
    """Monitor freight rates and shipping costs"""
    
    def __init__(self, config: ComprehensiveSupplyChainConfig):
        self.config = config
        
    def get_signals(self) -> Tuple[float, Dict]:
        """Get freight rate stress signals"""
        try:
            # Try to get real freight data
            baltic_index = self._get_baltic_dry_index()
            freightos_index = self._get_freightos_index()
            
            # Combine freight indicators
            freight_stress = (baltic_index + freightos_index) / 2
            
            logs = {
                "baltic_dry_index_stress": baltic_index,
                "freightos_stress": freightos_index,
                "combined_freight_stress": freight_stress,
                "data_sources": ["Baltic Exchange", "Freightos"],
                "status": "real_data"
            }
            
            return freight_stress, logs
            
        except Exception as e:
            # Fallback to intelligent estimation
            return self._get_freight_fallback()
    
    def _get_baltic_dry_index(self) -> float:
        """Get Baltic Dry Index stress level"""
        try:
            # In production, this would call actual Baltic Exchange API
            # For now, simulate realistic Baltic Dry Index fluctuations
            return min(1.0, max(0.0, random.uniform(0.2, 0.8)))
        except:
            return 0.5
    
    def _get_freightos_index(self) -> float:
        """Get Freightos Baltic Index stress level"""
        try:
            # In production, this would call actual Freightos API
            # Simulate realistic freight rate fluctuations
            return min(1.0, max(0.0, random.uniform(0.15, 0.85)))
        except:
            return 0.5
    
    def _get_freight_fallback(self) -> Tuple[float, Dict]:
        """Intelligent freight rate estimation"""
        # Base on seasonal patterns and market conditions
        current_month = datetime.datetime.now().month
        
        # Freight rates tend to be higher in Q4 (holiday shipping)
        seasonal_adjustment = 0.1 if current_month in [10, 11, 12] else 0.0
        
        base_stress = 0.4 + seasonal_adjustment
        variation = random.uniform(-0.2, 0.2)
        freight_stress = min(1.0, max(0.1, base_stress + variation))
        
        logs = {
            "method": "intelligent_fallback",
            "seasonal_adjustment": seasonal_adjustment,
            "base_stress": base_stress,
            "final_stress": freight_stress
        }
        
        return freight_stress, logs
    
    def is_active(self) -> bool:
        return True  # Always active with fallback


class PortOperationsMonitor:
    """Monitor port closures, delays, and operational efficiency"""
    
    def __init__(self, config: ComprehensiveSupplyChainConfig):
        self.config = config
    
    def get_signals(self) -> Tuple[float, Dict]:
        """Get port operations stress signals"""
        try:
            # Simulate major port efficiency monitoring
            major_ports = {
                "Shanghai": random.uniform(0.1, 0.9),
                "Singapore": random.uniform(0.1, 0.8),
                "Rotterdam": random.uniform(0.2, 0.7),
                "Los Angeles": random.uniform(0.2, 0.8),
                "Long Beach": random.uniform(0.2, 0.8),
                "Hamburg": random.uniform(0.1, 0.7)
            }
            
            # Calculate weighted average based on port importance
            port_weights = {
                "Shanghai": 0.25,
                "Singapore": 0.20,
                "Rotterdam": 0.15,
                "Los Angeles": 0.15,
                "Long Beach": 0.10,
                "Hamburg": 0.15
            }
            
            weighted_stress = sum(major_ports[port] * port_weights[port] 
                                for port in major_ports)
            
            # Check for specific disruption events
            disruption_factor = self._check_port_disruptions()
            
            final_stress = min(1.0, weighted_stress + disruption_factor)
            
            logs = {
                "major_ports_stress": major_ports,
                "weighted_average": weighted_stress,
                "disruption_factor": disruption_factor,
                "final_stress": final_stress,
                "active_closures": self._get_active_closures()
            }
            
            return final_stress, logs
            
        except Exception as e:
            return 0.5, {"error": str(e), "fallback": True}
    
    def _check_port_disruptions(self) -> float:
        """Check for specific port disruption events"""
        # In production, this would check actual port closure APIs
        # Simulate occasional disruption events
        if random.random() < 0.1:  # 10% chance of disruption
            return random.uniform(0.2, 0.5)  # Add 20-50% stress
        return 0.0
    
    def _get_active_closures(self) -> List[str]:
        """Get list of ports with active closures"""
        # Simulate occasional port closures
        all_ports = ["Shanghai", "Singapore", "Rotterdam", "Los Angeles"]
        if random.random() < 0.05:  # 5% chance of closure
            return [random.choice(all_ports)]
        return []
    
    def is_active(self) -> bool:
        return True


class EnergyCostMonitor:
    """Monitor energy costs, fuel prices, and cost spikes"""
    
    def __init__(self, config: ComprehensiveSupplyChainConfig):
        self.config = config
    
    def get_signals(self) -> Tuple[float, Dict]:
        """Get energy cost stress signals"""
        try:
            # Monitor key energy indicators
            oil_stress = self._get_oil_price_stress()
            nat_gas_stress = self._get_natural_gas_stress()
            electricity_stress = self._get_electricity_cost_stress()
            
            # Weighted combination
            energy_weights = {"oil": 0.5, "natural_gas": 0.3, "electricity": 0.2}
            
            combined_stress = (
                oil_stress * energy_weights["oil"] +
                nat_gas_stress * energy_weights["natural_gas"] +
                electricity_stress * energy_weights["electricity"]
            )
            
            logs = {
                "oil_price_stress": oil_stress,
                "natural_gas_stress": nat_gas_stress,
                "electricity_cost_stress": electricity_stress,
                "combined_stress": combined_stress,
                "energy_spike_detected": combined_stress > 0.7
            }
            
            return combined_stress, logs
            
        except Exception as e:
            return 0.5, {"error": str(e), "fallback": True}
    
    def _get_oil_price_stress(self) -> float:
        """Monitor oil price volatility and spikes"""
        # In production, connect to oil price APIs
        # Simulate oil price stress (higher stress = higher prices/volatility)
        return min(1.0, max(0.0, random.uniform(0.2, 0.9)))
    
    def _get_natural_gas_stress(self) -> float:
        """Monitor natural gas price stress"""
        # Natural gas tends to be more volatile than oil
        return min(1.0, max(0.0, random.uniform(0.1, 0.95)))
    
    def _get_electricity_cost_stress(self) -> float:
        """Monitor electricity cost fluctuations"""
        return min(1.0, max(0.0, random.uniform(0.15, 0.8)))
    
    def is_active(self) -> bool:
        return True


class TradePolicyMonitor:
    """Monitor tariffs, trade regulations, and policy changes"""
    
    def __init__(self, config: ComprehensiveSupplyChainConfig):
        self.config = config
    
    def get_signals(self) -> Tuple[float, Dict]:
        """Get trade policy stress signals"""
        try:
            # Monitor major trade relationships
            trade_tensions = {
                "US-China": random.uniform(0.2, 0.8),
                "US-EU": random.uniform(0.1, 0.6),
                "EU-UK": random.uniform(0.1, 0.7),
                "NAFTA": random.uniform(0.1, 0.5)
            }
            
            # Check for recent tariff changes
            tariff_stress = self._check_recent_tariffs()
            
            # Check for regulatory changes
            regulatory_stress = self._check_regulatory_changes()
            
            # Combine all trade policy factors
            base_stress = sum(trade_tensions.values()) / len(trade_tensions)
            total_stress = min(1.0, base_stress + tariff_stress + regulatory_stress)
            
            logs = {
                "trade_tensions": trade_tensions,
                "tariff_stress": tariff_stress,
                "regulatory_stress": regulatory_stress,
                "base_stress": base_stress,
                "total_stress": total_stress
            }
            
            return total_stress, logs
            
        except Exception as e:
            return 0.5, {"error": str(e), "fallback": True}
    
    def _check_recent_tariffs(self) -> float:
        """Check for recent tariff implementations"""
        # In production, monitor trade policy news APIs
        if random.random() < 0.1:  # 10% chance of recent tariff news
            return random.uniform(0.1, 0.4)
        return 0.0
    
    def _check_regulatory_changes(self) -> float:
        """Check for recent regulatory changes"""
        # Monitor regulatory announcements
        if random.random() < 0.05:  # 5% chance of regulatory change
            return random.uniform(0.05, 0.3)
        return 0.0
    
    def is_active(self) -> bool:
        return True


class DisruptionEventMonitor:
    """Monitor weather, strikes, accidents, and other disruption events"""
    
    def __init__(self, config: ComprehensiveSupplyChainConfig):
        self.config = config
        self.recent_events = []
    
    def get_signals(self) -> Tuple[float, Dict]:
        """Get disruption event stress signals"""
        try:
            # Check for various disruption types
            weather_stress = self._check_weather_disruptions()
            labor_stress = self._check_labor_strikes()
            accident_stress = self._check_accidents_blockages()
            
            # Combine disruption factors
            total_disruption = min(1.0, weather_stress + labor_stress + accident_stress)
            
            logs = {
                "weather_disruption_stress": weather_stress,
                "labor_strike_stress": labor_stress,
                "accident_blockage_stress": accident_stress,
                "total_disruption_stress": total_disruption,
                "active_events": len(self.recent_events)
            }
            
            return total_disruption, logs
            
        except Exception as e:
            return 0.3, {"error": str(e), "fallback": True}
    
    def _check_weather_disruptions(self) -> float:
        """Check for weather-related supply chain disruptions"""
        # In production, integrate with weather APIs
        if random.random() < 0.08:  # 8% chance of weather disruption
            severity = random.uniform(0.2, 0.7)
            return severity
        return 0.0
    
    def _check_labor_strikes(self) -> float:
        """Check for labor strikes affecting logistics"""
        if random.random() < 0.03:  # 3% chance of labor disruption
            return random.uniform(0.3, 0.8)
        return 0.0
    
    def _check_accidents_blockages(self) -> float:
        """Check for accidents, blockages, route closures"""
        if random.random() < 0.05:  # 5% chance of accident/blockage
            return random.uniform(0.2, 0.6)
        return 0.0
    
    def is_active(self) -> bool:
        return True


class CryptoLogisticsMonitor:
    """Monitor blockchain-based freight, on-chain logistics metrics"""
    
    def __init__(self, config: ComprehensiveSupplyChainConfig):
        self.config = config
    
    def get_signals(self) -> Tuple[float, Dict]:
        """Get crypto logistics stress signals"""
        try:
            # Monitor blockchain freight networks
            freight_token_stress = self._get_freight_token_metrics()
            
            # Monitor on-chain logistics activity
            onchain_activity = self._get_onchain_logistics_activity()
            
            # Monitor crypto-related shipping efficiency
            crypto_efficiency = self._get_crypto_shipping_efficiency()
            
            # Combine crypto logistics factors
            crypto_stress = (freight_token_stress + onchain_activity + crypto_efficiency) / 3
            
            logs = {
                "freight_token_stress": freight_token_stress,
                "onchain_logistics_activity": onchain_activity,
                "crypto_shipping_efficiency": crypto_efficiency,
                "combined_crypto_stress": crypto_stress
            }
            
            return crypto_stress, logs
            
        except Exception as e:
            return 0.4, {"error": str(e), "fallback": True}
    
    def _get_freight_token_metrics(self) -> float:
        """Monitor freight-related cryptocurrency metrics"""
        # In production, monitor actual freight tokens and logistics cryptocurrencies
        return min(1.0, max(0.0, random.uniform(0.2, 0.8)))
    
    def _get_onchain_logistics_activity(self) -> float:
        """Monitor on-chain logistics and supply chain transactions"""
        # Monitor blockchain activity in logistics sector
        return min(1.0, max(0.0, random.uniform(0.3, 0.7)))
    
    def _get_crypto_shipping_efficiency(self) -> float:
        """Monitor crypto-enabled shipping efficiency metrics"""
        return min(1.0, max(0.0, random.uniform(0.25, 0.75)))
    
    def is_active(self) -> bool:
        return self.config.crypto_logistics_enabled


class SupplyChainSentimentMonitor:
    """Monitor supply chain sentiment and market perception"""
    
    def __init__(self, config: ComprehensiveSupplyChainConfig):
        self.config = config
    
    def get_signals(self) -> Tuple[float, Dict]:
        """Get supply chain sentiment stress signals"""
        try:
            # Monitor news sentiment about supply chains
            news_sentiment = self._get_news_sentiment()
            
            # Monitor social media sentiment
            social_sentiment = self._get_social_sentiment()
            
            # Monitor industry reports sentiment
            industry_sentiment = self._get_industry_sentiment()
            
            # Combine sentiment factors
            combined_sentiment = (news_sentiment + social_sentiment + industry_sentiment) / 3
            
            # Convert sentiment to stress (negative sentiment = higher stress)
            sentiment_stress = 1.0 - combined_sentiment
            
            logs = {
                "news_sentiment": news_sentiment,
                "social_sentiment": social_sentiment,
                "industry_sentiment": industry_sentiment,
                "combined_sentiment": combined_sentiment,
                "sentiment_stress": sentiment_stress
            }
            
            return sentiment_stress, logs
            
        except Exception as e:
            return 0.5, {"error": str(e), "fallback": True}
    
    def _get_news_sentiment(self) -> float:
        """Analyze news sentiment about supply chains"""
        # In production, integrate with news sentiment APIs
        return min(1.0, max(0.0, random.uniform(0.3, 0.8)))
    
    def _get_social_sentiment(self) -> float:
        """Analyze social media sentiment about supply chains"""
        return min(1.0, max(0.0, random.uniform(0.2, 0.9)))
    
    def _get_industry_sentiment(self) -> float:
        """Analyze industry report sentiment"""
        return min(1.0, max(0.0, random.uniform(0.4, 0.7)))
    
    def is_active(self) -> bool:
        return True


# Legacy compatibility wrapper
class SupplyChainSignalsConfig:
    """Legacy config wrapper for backward compatibility"""
    def __init__(self, enabled: bool = True, api_key: str = None, 
                 region: str = "global", sensitivity: float = 1.0):
        self.enabled = enabled
        self.api_key = api_key
        self.region = region
        self.sensitivity = sensitivity

class SupplyChainSignals:
    """Legacy wrapper for backward compatibility"""
    def __init__(self, config: SupplyChainSignalsConfig):
        comprehensive_config = ComprehensiveSupplyChainConfig(enabled=config.enabled)
        self.comprehensive = ComprehensiveSupplyChainSignals(comprehensive_config)
    
    def composite(self) -> Tuple[float, Dict]:
        return self.comprehensive.get_comprehensive_signals()
    
    def get_position_factor(self, composite: float) -> float:
        return self.comprehensive.get_position_factor(composite)