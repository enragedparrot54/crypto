# Crypto Backtester (CSV Only)

A simple cryptocurrency backtesting system using historical OHLCV data from CSV files.

**⚠️ No live trading. No exchange APIs. Backtest only.**

## Quick Start

```bash
cd bot
python3 main.py
```

## Required CSV Format

Place your historical data in `data/BTC_5m.csv` with this format:

```csv
timestamp,open,high,low,close,volume
1609459200000,29000.00,29100.00,28900.00,29050.00,123.45
1609459500000,29050.00,29150.00,29000.00,29100.00,98.76
```

- **timestamp**: Unix timestamp in milliseconds
- **open/high/low/close**: Price values
- **volume**: Trading volume

## Supported Symbols

- `data/BTC_5m.csv` - Bitcoin
- `data/ETH_5m.csv` - Ethereum  
- `data/SOL_5m.csv` - Solana

## Configuration

Edit `config.py` to adjust:

- `INITIAL_BALANCE` - Starting paper balance
- `STOP_LOSS_PCT` - Stop loss percentage
- `TAKE_PROFIT_PCT` - Take profit percentage
- `RISK_PER_TRADE_PCT` - Risk per trade
- `COOLDOWN_CANDLES` - Candles between trades
- `TREND_EMA_PERIOD` - EMA trend filter period

## Output Files

After running a backtest:

- `trades.csv` - All executed trades
- `equity.csv` - Equity curve over time

## Project Structure

```
bot/
├── main.py              # Entry point
├── config.py            # Configuration
├── data/
│   ├── load_csv.py      # CSV loader
│   └── BTC_5m.csv       # Historical data
├── backtest/
│   └── engine.py        # Backtest engine
├── broker/
│   └── paper_broker.py  # Paper trading broker
└── strategies/
    ├── base_strategy.py # Strategy interface
    └── sma_cross.py     # SMA crossover strategy
```

## Notes

- This backtester uses **CSV files only**
- No Binance, Coinbase, or other exchange APIs
- No internet connection required
- Paper trading simulation only