from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime
import sqlite3

app = FastAPI()

DB_PATH = "benson.sqlite"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        type TEXT,
        symbol TEXT,
        signal TEXT,
        price REAL,
        reason TEXT,
        extra TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        symbol TEXT,
        label TEXT,
        outcome TEXT,
        extra TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

class SignalRequest(BaseModel):
    symbol: str
    candles: List[float]
    ts: Optional[str] = None

class SignalResponse(BaseModel):
    signal: Literal["BUY", "SELL", "HOLD"]
    size: float = 0.0
    reason: str

class TradeRequest(BaseModel):
    symbol: str
    side: Literal["BUY", "SELL"]
    size: float
    price: Optional[float] = None
    paper: bool = True

class LogRequest(BaseModel):
    type: str
    symbol: str
    signal: str
    price: float
    reason: Optional[str] = None
    extra: Optional[str] = None

class FeedbackRequest(BaseModel):
    symbol: str
    label: str
    outcome: str
    extra: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}

@app.post("/signals", response_model=SignalResponse)
def signals(req: SignalRequest):
    last = req.candles[-1] if req.candles else 0
    if last < 30:
        signal = "BUY"
        reason = "RSI below 30"
    elif last > 70:
        signal = "SELL"
        reason = "RSI above 70"
    else:
        signal = "HOLD"
        reason = "RSI neutral"
    return SignalResponse(signal=signal, size=1.0, reason=reason)

@app.post("/trade")
def trade(req: TradeRequest):
    if req.paper:
        return {"status": "paper", "detail": "No real trade executed"}
    return {"status": "ok", "detail": "Trade executed"}

@app.post("/log")
def log(req: LogRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO logs (ts, type, symbol, signal, price, reason, extra) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), req.type, req.symbol, req.signal, req.price, req.reason, req.extra)
    )
    conn.commit()
    conn.close()
    return {"status": "logged"}

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO feedback (ts, symbol, label, outcome, extra) VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), req.symbol, req.label, req.outcome, req.extra)
    )
    conn.commit()
    conn.close()
    return {"status": "feedback stored"}

@app.get("/metrics")
def metrics():
    return {"uptime": "unknown", "requests": "unknown"}