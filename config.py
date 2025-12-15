"""
Configuration file for backtest parameters.
All tunable parameters are defined here.

This is a CSV-only backtester.
No live trading. No exchange APIs.
"""

# Account settings
INITIAL_BALANCE = 10000.0  # Starting balance in USD

# Risk management
STOP_LOSS_PCT = -1.0  # Stop loss percentage (e.g., -1.0 = -1%)
TAKE_PROFIT_PCT = 2.0  # Take profit percentage (e.g., 2.0 = +2%)
RISK_PER_TRADE_PCT = 1.0  # Risk percentage of account per trade

# Trade cooldown
COOLDOWN_CANDLES = 6  # Minimum candles between trades after a sell

# Trend filter
TREND_EMA_PERIOD = 200  # EMA period for higher-timeframe trend filter

# Logging
TRADES_LOG_FILE = "trades.csv"  # CSV file for trade logging
EQUITY_LOG_FILE = "equity.csv"  # CSV file for equity curve

# Data files (CSV only - no API calls)
DATA_FILES = {
    "BTC": "data/BTC_5m.csv",
    "ETH": "data/ETH_5m.csv",
    "SOL": "data/SOL_5m.csv",
}