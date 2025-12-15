import os

from data.load_csv import load_candles
from backtest.engine import BacktestEngine
from broker.paper_broker import PaperBroker
from strategies.base_strategy import BaseStrategy


DATA_PATH = "data/BTC_5m.csv"
SYMBOL = "BTC/USDT"


class DummyStrategy(BaseStrategy):
    """A dummy strategy that always holds."""
    
    def on_candle(self, history, broker, symbol):
        return "HOLD"


def main():
    print("Crypto Trading Backtester")
    print("==========================")
    
    # Check if data file exists
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at '{DATA_PATH}'")
        return
    
    # Load candles
    candles = load_candles(DATA_PATH)
    
    if not candles:
        print("Error: No candles loaded from CSV file")
        return
    
    print(f"Loaded {len(candles)} candles from {DATA_PATH}")
    
    # Initialize components
    engine = BacktestEngine()
    broker = PaperBroker(initial_cash=10000.0)
    strategy = DummyStrategy()
    
    # Run backtest
    print(f"\nRunning backtest for {SYMBOL}...")
    trades = engine.run_backtest(strategy, candles, SYMBOL)
    
    # Print performance summary
    performance = engine.evaluate_performance()
    print("\n--- Performance Summary ---")
    print(f"Ending Balance: ${performance['ending_balance']:.2f}")
    print(f"Number of Trades: {performance['num_trades']}")
    print(f"PnL: ${performance['pnl']:.2f}")
    
    # Print last 5 trades
    if trades:
        print("\n--- Last 5 Trades ---")
        for trade in trades[-5:]:
            print(
                f"{trade['timestamp']} | {trade['type']:4} | "
                f"{trade['amount']:.6f} @ ${trade['price']:.2f} | "
                f"Balance: ${trade['balance_after']:.2f}"
            )
    else:
        print("\nNo trades executed during backtest.")


if __name__ == "__main__":
    main()