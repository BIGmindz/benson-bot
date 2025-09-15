# src/futures/portfolio_metrics_stubs.py
class PortfolioStub:
    def __init__(self, starting_equity_usd: float = 10000.0):
        self._equity = float(starting_equity_usd)

    def equity_usd(self) -> float:
        return self._equity

    def breaches_caps(self, symbol: str, caps) -> bool:
        # No real exposure tracking in stub; always OK
        return False

class MetricsStub:
    def __init__(self):
        self.daily_drawdown_pct = 0.0
        self.consecutive_losses = 0
