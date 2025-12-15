"""
Crypto Backtester - CSV Only
No live trading. No exchange APIs.
"""

import os
import sys
from datetime import datetime

from data.load_csv import load_candles
from backtest.engine import BacktestEngine
from strategies.sma_cross import SMACrossStrategy
import config


# Data file path
DATA_PATH = "data/BTC_5m.csv"
SYMBOL = "BTC/USDT"


def main():
    """
    Backtest-only paper trading system.
    No live trading, APIs, WebSockets, or real orders.
    """
    print("\n" + "=" * 50)
    print("CRYPTO BACKTESTER (CSV Only)")
    print("No live trading. No exchange APIs.")
    print("=" * 50)
    
    # Check if data file exists
    if not os.path.exists(DATA_PATH):
        print(f"\nERROR: Data file not found: {DATA_PATH}")
        print(f"\nPlease create a CSV file with format:")
        print(f"  timestamp,open,high,low,close,volume")
        print(f"\nPlace your historical data at: {DATA_PATH}")
        sys.exit(1)
    
    # Load candles from CSV (historical data only)
    print(f"\nLoading data from: {DATA_PATH}")
    candles = load_candles(DATA_PATH)
    
    if not candles:
        print("ERROR: No candles loaded from CSV file")
        sys.exit(1)
    
    print(f"✅ Loaded {len(candles)} candles")
    
    # Show data range
    first_ts = candles[0]['timestamp']
    last_ts = candles[-1]['timestamp']
    try:
        first_date = datetime.fromtimestamp(first_ts / 1000).strftime('%Y-%m-%d %H:%M')
        last_date = datetime.fromtimestamp(last_ts / 1000).strftime('%Y-%m-%d %H:%M')
        print(f"📅 Date range: {first_date} to {last_date}")
    except:
        print(f"📅 Timestamp range: {first_ts} to {last_ts}")
    
    # Initialize backtest engine and strategy
    engine = BacktestEngine(verbose=True)
    strategy = SMACrossStrategy(fast=10, slow=30, risk_percent=1.0)
    
    # Run backtest (paper trading only - no real orders)
    print(f"\nRunning backtest for {SYMBOL}...")
    results = engine.run_backtest(strategy, candles, SYMBOL)
    
    # Print final summary
    print("\n" + "=" * 50)
    print("BACKTEST COMPLETE")
    print("=" * 50)
    print(f"📊 Candles processed: {len(candles)}")
    print(f"📈 Trades executed:   {len(results)}")
    
    performance = engine.evaluate_performance()
    print(f"💰 Starting balance:  ${config.INITIAL_BALANCE:.2f}")
    print(f"💰 Final balance:     ${performance['ending_balance']:.2f}")
    print(f"📁 Trade log:         {config.TRADES_LOG_FILE}")
    print(f"📁 Equity curve:      {config.EQUITY_LOG_FILE}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()