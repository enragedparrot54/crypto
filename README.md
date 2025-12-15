# Crypto Backtester (CSV Only)

A simple cryptocurrency backtesting system using historical OHLCV data.

## ⚠️ Important

- **NO LIVE TRADING** - Paper trading simulation only
- **NO API CALLS** - All data from local CSV files
- **NO EXCHANGE CONNECTIONS** - Fully offline
- **NO Binance, ccxt, or live data sources**

## Quick Start

```bash
cd bot
python3 main.py
```

## Data Requirements

Place your CSV data in `data/SOL_5m.csv`:

```csv
timestamp,open,high,low,close,volume
1609459200000,150.00,152.50,149.00,151.25,12345.67
1609459500000,151.25,153.00,150.50,152.00,9876.54
```

### Column Format

| Column | Type | Description |
|--------|------|-------------|
| timestamp | int | Unix timestamp (milliseconds) |
| open | float | Open price |
| high | float | High price |
| low | float | Low price |
| close | float | Close price |
| volume | float | Trading volume |

## Configuration

Edit `config.py`:

```python
SYMBOL = "SOL-USD"
TIMEFRAME = "5m"
DATA_FILE = "data/SOL_5m.csv"
INITIAL_BALANCE = 1000.0
```

## Output

- `trades.csv` - All executed trades
- `equity.csv` - Equity curve over time

## Project Structure

```
bot/
├── main.py              # Entry point
├── config.py            # Settings
├── data/
│   ├── load_csv.py      # CSV loader (no APIs)
│   └── SOL_5m.csv       # Your data file
├── backtest/
│   └── engine.py        # Backtest engine
├── broker/
│   └── paper_broker.py  # Paper trading
└── strategies/
    └── sol_daytrader.py # Trading strategy
```

## Offline Verification

This project makes **ZERO network requests**:

- ❌ No `requests` library
- ❌ No `ccxt` library
- ❌ No `websocket` connections
- ❌ No Binance/Coinbase/exchange APIs
- ✅ CSV file reading only
- ✅ Local file writing only

## License

For educational purposes only. Not financial advice.