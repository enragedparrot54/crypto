import requests
import csv
import os
import time
from datetime import datetime, timedelta


def download_candles(symbol="BTC-USD", granularity=300, days=90):
    """Download historical candles from Coinbase public API.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC-USD')
        granularity: Candle size in seconds (300 = 5 minutes)
        days: Number of days of data to fetch
        
    Returns:
        List of candle data
    """
    base_url = f"https://api.exchange.coinbase.com/products/{symbol}/candles"
    
    # Coinbase returns max 300 candles per request
    max_candles_per_request = 300
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    print(f"Downloading {days} days of 5-minute candles for {symbol}...")
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    all_candles = []
    current_end = end_time
    
    while current_end > start_time:
        # Calculate start for this batch
        batch_seconds = max_candles_per_request * granularity
        current_start = current_end - timedelta(seconds=batch_seconds)
        
        # Don't go before our target start time
        if current_start < start_time:
            current_start = start_time
        
        params = {
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
            "granularity": granularity
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            candles = response.json()
            
            if not candles:
                break
            
            # Coinbase returns newest first, so reverse for chronological order
            candles.reverse()
            all_candles.extend(candles)
            
            print(f"Downloaded {len(all_candles)} candles so far...")
            
            # Move window back
            current_end = current_start - timedelta(seconds=granularity)
            
            # Rate limiting - Coinbase allows 10 requests per second
            time.sleep(0.15)
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("Rate limit hit, waiting 5 seconds...")
                time.sleep(5)
            else:
                print(f"HTTP error: {e}")
                break
        except Exception as e:
            print(f"Error fetching candles: {e}")
            break
    
    # Sort by timestamp (oldest first)
    all_candles.sort(key=lambda x: x[0])
    
    # Remove duplicates based on timestamp
    seen = set()
    unique_candles = []
    for candle in all_candles:
        if candle[0] not in seen:
            seen.add(candle[0])
            unique_candles.append(candle)
    
    print(f"Downloaded {len(unique_candles)} unique candles total")
    return unique_candles


def save_to_csv(candles, filepath):
    """Save candle data to CSV file.
    
    Coinbase candle format: [timestamp, low, high, open, close, volume]
    
    Args:
        candles: List of candle arrays from Coinbase
        filepath: Output CSV file path
    """
    # Ensure directory exists
    if os.path.dirname(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        for candle in candles:
            # Coinbase format: [timestamp, low, high, open, close, volume]
            timestamp = int(candle[0]) * 1000  # Convert to milliseconds
            low = candle[1]
            high = candle[2]
            open_price = candle[3]
            close_price = candle[4]
            volume = candle[5]
            
            writer.writerow([
                timestamp,
                open_price,
                high,
                low,
                close_price,
                volume
            ])
    
    print(f"Saved to {filepath}")


def main():
    symbol = "BTC-USD"
    granularity = 300  # 5 minutes in seconds
    days = 90
    output_path = "data/BTC_5m.csv"
    
    print("Coinbase Candle Downloader")
    print("==========================")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: 5m")
    print(f"Days: {days}")
    print()
    
    try:
        candles = download_candles(symbol, granularity, days)
        
        if candles:
            save_to_csv(candles, output_path)
            
            # Print summary
            start_ts = candles[0][0]
            end_ts = candles[-1][0]
            print(f"\nSuccess!")
            print(f"Total candles: {len(candles)}")
            print(f"Start: {datetime.utcfromtimestamp(start_ts).strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"End: {datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"Saved to: {output_path}")
        else:
            print("No candles downloaded")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()