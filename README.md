# Crypto Trading Backtester

A simple backtesting framework for cryptocurrency trading strategies.

## Installation

Install required dependencies:

```bash
pip install ccxt
```

## Project Structure

```
bot/
├── main.py                 # Entry point - runs the backtest
├── data/
│   ├── load_csv.py         # CSV candle data loader
│   └── download_candles.py # Download candles from Binance
├── backtest/
│   └── engine.py           # Backtesting engine
├── broker/
│   └── paper_broker.py     # Paper trading broker for simulated trades
└── strategies/
    ├── base_strategy.py    # Base strategy class
    └── sma_cross.py        # SMA crossover strategy implementation
```

## Features

- **Paper Trading Broker**: Simulates trades with position tracking and weighted average entry prices
- **Backtesting Engine**: Runs strategies against historical candle data
- **SMA Crossover Strategy**: Built-in strategy using fast/slow SMA crossovers
- **Performance Evaluation**: Calculates ending balance, trade count, and PnL
- **Data Downloader**: Fetch historical candles from Binance

## Usage

### 1. Download Historical Data

```bash
python data/download_candles.py
```

This will download 1000 BTC/USDT 5-minute candles from Binance and save them to `data/BTC_5m.csv`.

### 2. Run the Backtester

```bash
python main.py
```

## CSV Data Format

The CSV file must have these columns:
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`

## Creating Custom Strategies

Extend `BaseStrategy` and implement the `on_candle()` method:

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def on_candle(self, history, broker, symbol):
        # Your logic here
        # Return "BUY", "SELL", or "HOLD"
        return "HOLD"
```

## Configuration

Edit `main.py` to adjust:
- `DATA_PATH`: Path to your CSV data file
- `SYMBOL`: Trading pair symbol
- Strategy parameters (e.g., `fast`, `slow`, `trade_fraction`)

## Example Output

```
Crypto Trading Backtester
==========================
Loaded 1000 candles from data/BTC_5m.csv

Running backtest for BTC/USDT...

--- Performance Summary ---
Ending Balance: $10523.45
Number of Trades: 12
PnL: $523.45

--- Last 5 Trades ---
1702656000.0 | BUY  | 0.234500 @ $42650.00 | Balance: $10000.00
1702742400.0 | SELL | 0.234500 @ $43120.00 | Balance: $10523.45
```