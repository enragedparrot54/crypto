"""
CSV-only backtester.
SOL-USD | LONG ONLY | $1,000 starting balance.
"""

import os
import sys

from data.load_csv import load_candles
from backtest.engine import BacktestEngine
from strategies.sol_daytrader import SOLDayTraderStrategy
import config


def main():
    print("\n" + "=" * 50)
    print("BACKTESTER - SOL-USD - LONG ONLY")
    print("=" * 50)

    # Check if CSV file exists
    if not os.path.exists(config.DATA_FILE):
        print(f"\n❌ ERROR: Data file not found")
        print(f"   Expected: {config.DATA_FILE}")
        print(f"\n   Please create a CSV file with columns:")
        print(f"   timestamp,open,high,low,close,volume")
        sys.exit(1)

    # Check if file is empty
    if os.path.getsize(config.DATA_FILE) == 0:
        print(f"\n❌ ERROR: Data file is empty")
        print(f"   File: {config.DATA_FILE}")
        sys.exit(1)

    print(f"\nSymbol:   {config.SYMBOL}")
    print(f"Balance:  ${config.INITIAL_BALANCE:.2f}")
    print(f"Data:     {config.DATA_FILE}")
    print(f"Mode:     LONG ONLY")

    # Load candles
    candles = load_candles(config.DATA_FILE)

    if not candles:
        print(f"\n❌ ERROR: No valid candles in file")
        print(f"   File: {config.DATA_FILE}")
        sys.exit(1)

    print(f"Candles:  {len(candles)}")

    # Run backtest
    engine = BacktestEngine(verbose=True)
    strategy = SOLDayTraderStrategy()

    results = engine.run_backtest(strategy, candles, config.SYMBOL)

    # Results
    perf = engine.evaluate_performance()
    ret = ((perf["ending_balance"] - config.INITIAL_BALANCE) / config.INITIAL_BALANCE) * 100

    print("\n" + "=" * 50)
    print("RESULTS - SOL-USD - LONG ONLY")
    print("=" * 50)
    print(f"Starting:  ${config.INITIAL_BALANCE:.2f}")
    print(f"Ending:    ${perf['ending_balance']:.2f}")
    print(f"Return:    {ret:+.2f}%")
    print(f"Trades:    {perf['num_trades']}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()