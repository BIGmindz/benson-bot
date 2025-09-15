from dataclasses import dataclass
from typing import Tuple, Dict
import random
import datetime

@dataclass
class SupplyChainSignalsConfig:
    enabled: bool = False
    api_key: str = None          # placeholder if you later connect to real API
    region: str = "global"       # e.g. "US", "EU", "Asia"
    sensitivity: float = 1.0     # scale the impact

class SupplyChainSignals:
    """
    Supply chain signals module
    - Currently stubbed with placeholder logic
    - Later you can connect APIs: MarineTraffic, Port Authority, Freight Index, etc.
    """

    def __init__(self, config: SupplyChainSignalsConfig):
        self.config = config

    def composite(self) -> Tuple[float, Dict]:
        """
        Returns a composite supply chain stress score (0-1)
        and debug logs. Right now uses dummy/random data.
        """
        # Placeholder: random “congestion” between 0.3–0.7
        congestion = random.uniform(0.3, 0.7)

        # Composite is just congestion scaled by sensitivity
        composite = min(1.0, max(0.0, congestion * self.config.sensitivity))

        logs = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "congestion_index": congestion,
            "region": self.config.region,
            "note": "Stubbed random signal, replace with API data"
        }

        return composite, logs

    def get_position_factor(self, composite: float) -> float:
        """
        Map composite score → trading factor.
        - >0.6 = supply chain stress = bearish (reduce pos)
        - <0.4 = strong supply chain = bullish (increase pos)
        - else neutral
        """
        if composite > 0.6:
            return 0.9   # Decrease pos 10%
        elif composite < 0.4:
            return 1.1   # Increase pos 10%
        else:
            return 1.0   # Neutral
if self.supply_chain_signals:
    try:
        sc_composite, sc_logs = self.supply_chain_signals.composite()
        sc_factor = self.supply_chain_signals.get_position_factor(sc_composite)
        signals["supply_chain"] = sc_factor
        signals["supply_chain_composite"] = sc_composite
        signals["supply_chain_logs"] = sc_logs
    except Exception as e:
        print(f"SupplyChain error: {e}")
if 'supply_chain_composite' in analysis:
    print("\n🚢 SUPPLY CHAIN SIGNALS")
    print(f"   Composite Score: {analysis['supply_chain_composite']:.2f}")
    print(f"   Supply Chain Factor: {analysis.get('supply_chain', 1.0):.2f}")
supply_chain_signals:
  enabled: true
  region: "US"
  sensitivity: 1.0
