# src/futures/paper_gateway.py
from typing import Dict, Optional
import time
import uuid

class PaperGateway:
    """
    Minimal futures paper-trading adaptor:
      - place_order: records a fill instantly at current price (no slippage here)
      - attach_stop_takeprofit: stores SL/TP for bookkeeping
    Stores positions in-memory; good enough for smoke tests & integration.
    """
    def __init__(self, logger=None):
        self.logger = logger or print
        self.orders: Dict[str, Dict] = {}
        self.positions: Dict[str, Dict] = {}  # by symbol (single net position per symbol)

    def place_order(self, *, symbol: str, side: str, type: str, size: float, leverage: float) -> str:
        oid = str(uuid.uuid4())[:8]
        now = time.time()
        # Create/adjust net position
        pos = self.positions.get(symbol, {"symbol": symbol, "size": 0.0, "entry": None, "leverage": leverage})
        signed = size if side == "long" else -size

        if pos["size"] == 0:
            pos["entry"] = self._last_price_hint(symbol)  # caller should set before
            pos["size"] = signed
        else:
            # simple netting: weighted avg entry when adding to same direction
            if (pos["size"] > 0 and signed > 0) or (pos["size"] < 0 and signed < 0):
                new_size = pos["size"] + signed
                if new_size != 0:
                    pos["entry"] = pos["entry"]  # keep entry for simplicity; refine if you want WAP
                pos["size"] = new_size
            else:
                pos["size"] += signed
                if pos["size"] == 0:
                    pos["entry"] = None

        pos["leverage"] = leverage
        self.positions[symbol] = pos

        self.orders[oid] = {"id": oid, "symbol": symbol, "side": side, "type": type, "size": size,
                            "leverage": leverage, "ts": now}
        self.logger(f"[PAPER] order {oid} {side} {symbol} size={size:.4f} lev={leverage}")
        return oid

    def attach_stop_takeprofit(self, symbol: str, order_id: str, stop_price: float, tp_price: float) -> None:
        od = self.orders.get(order_id)
        if od:
            od["stop_price"] = float(stop_price)
            od["tp_price"] = float(tp_price)
            self.logger(f"[PAPER] SL/TP set for {order_id}: SL={stop_price:.2f} TP={tp_price:.2f}")

    # hint is set externally before calling place_order
    def set_last_price_hint(self, symbol: str, price: float):
        od = {"_pxhint": price}
        self.orders["_pxhint_"+symbol] = od

    def _last_price_hint(self, symbol: str) -> Optional[float]:
        od = self.orders.get("_pxhint_"+symbol)
        return od.get("_pxhint") if od else None
