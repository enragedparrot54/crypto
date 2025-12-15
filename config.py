"""
Configuration - CSV-only backtester.
SOL-USD | LONG ONLY | $1,000 starting balance.
"""

# === SYMBOL ===
SYMBOL = "SOL-USD"
TIMEFRAME = "5m"
DATA_FILE = "data/SOL_5m.csv"

# === ACCOUNT ===
INITIAL_BALANCE = 1000.0

# === RISK ===
RISK_PER_TRADE_PCT = 1.0
STOP_LOSS_PCT = -2.0
TAKE_PROFIT_PCT = 4.0

# === COOLDOWN ===
COOLDOWN_CANDLES = 6

# === TREND FILTER ===
TREND_EMA_PERIOD = 200

# === OUTPUT ===
TRADES_LOG_FILE = "trades.csv"
EQUITY_LOG_FILE = "equity.csv"