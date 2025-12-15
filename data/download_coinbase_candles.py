"""
Download historical candles from Coinbase public API.
SOL-USD | 5m candles | 90 days.

Note: This is for data preparation only.
The backtester itself uses CSV files, not live API calls.
"""

import requests
import csv
import time
from datetime import datetime, timedelta

# === CONFIGURATION ===
SYMBOL = "SOL-USD"
TIMEFRAME = "5m"
DAYS = 90
OUTPUT_FILE = "data/SOL_5m.csv"

# Coinbase granularity mapping
GRANULARITY = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "6h": 21600,
    "1d": 86400
}


def download_candles():
    """Download SOL-USD candles from Coinbase."""
    print(f"\n{'='*50}")
    print(f"Downloading {SYMBOL} candles")
    print(f"{'='*50}")
    print(f"Timeframe: {TIMEFRAME}")
    print(f"Days:      {DAYS}")
    print(f"Output:    {OUTPUT_FILE}")
    print(f"{'='*50}\n")

    granularity = GRANULARITY.get(TIMEFRAME, 300)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=DAYS)

    all_candles = []
    current_start = start_time

    # Coinbase allows max 300 candles per request
    max_candles_per_request = 300
    interval_seconds = granularity * max_candles_per_request

    while current_start < end_time:
        current_end = min(current_start + timedelta(seconds=interval_seconds), end_time)

        url = f"https://api.exchange.coinbase.com/products/{SYMBOL}/candles"
        params = {
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
            "granularity": granularity
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            candles = response.json()

            if candles:
                all_candles.extend(candles)
                print(f"  Fetched {len(candles)} candles from {current_start.strftime('%Y-%m-%d')}")

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error: {e}")

        current_start = current_end
        time.sleep(0.5)  # Rate limiting

    if not all_candles:
        print("\n❌ No candles downloaded")
        return

    # Sort by timestamp (oldest first)
    all_candles.sort(key=lambda x: x[0])

    # Remove duplicates
    seen = set()
    unique_candles = []
    for c in all_candles:
        if c[0] not in seen:
            seen.add(c[0])
            unique_candles.append(c)

    # Write to CSV
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        for candle in unique_candles:
            # Coinbase format: [timestamp, low, high, open, close, volume]
            ts, low, high, open_p, close_p, volume = candle
            writer.writerow([
                int(ts * 1000),  # Convert to milliseconds
                open_p,
                high,
                low,
                close_p,
                volume
            ])

    print(f"\n✅ Saved {len(unique_candles)} candles to {OUTPUT_FILE}")
    print(f"   Date range: {datetime.fromtimestamp(unique_candles[0][0]).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(unique_candles[-1][0]).strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    download_candles()