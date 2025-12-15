import ccxt
import csv
import os
import time


def download_candles(symbol="BTC/USDT", timeframe="5m", days=90):
    """Download historical candles from Binance.
    
    Args:
        symbol: Trading pair symbol
        timeframe: Candle timeframe (e.g., '5m', '1h')
        days: Number of days of data to fetch
        
    Returns:
        List of candle data
    """
    print(f"Connecting to Binance...")
    exchange = ccxt.binance()
    
    # Calculate how many candles we need
    # 5-minute candles: 12 per hour * 24 hours * days
    candles_per_day = 12 * 24  # 288 candles per day for 5m timeframe
    total_candles = candles_per_day * days
    
    # Binance limits to 1000 candles per request
    limit_per_request = 1000
    
    # Calculate start time (days ago from now)
    now = exchange.milliseconds()
    since = now - (days * 24 * 60 * 60 * 1000)
    
    print(f"Downloading {days} days of {timeframe} candles for {symbol}...")
    print(f"Expected candles: ~{total_candles}")
    
    all_ohlcv = []
    
    while since < now:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit_per_request)
            
            if not ohlcv:
                break
                
            all_ohlcv.extend(ohlcv)
            
            # Move since to after the last candle
            since = ohlcv[-1][0] + 1
            
            print(f"Downloaded {len(all_ohlcv)} candles so far...")
            
            # Rate limiting - be nice to the API
            time.sleep(0.1)
            
        except ccxt.RateLimitExceeded:
            print("Rate limit hit, waiting 10 seconds...")
            time.sleep(10)
        except Exception as e:
            print(f"Error fetching candles: {e}")
            break
    
    print(f"Downloaded {len(all_ohlcv)} candles total")
    return all_ohlcv


def save_to_csv(ohlcv, filepath):
    """Save OHLCV data to CSV file.
    
    Args:
        ohlcv: List of [timestamp, open, high, low, close, volume]
        filepath: Output CSV file path
    """
    # Ensure directory exists
    if os.path.dirname(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        for candle in ohlcv:
            writer.writerow([
                int(candle[0]),    # timestamp in milliseconds
                candle[1],         # open
                candle[2],         # high
                candle[3],         # low
                candle[4],         # close
                candle[5]          # volume
            ])
    
    print(f"Saved to {filepath}")


def main():
    symbol = "BTC/USDT"
    timeframe = "5m"
    days = 90
    output_path = "data/BTC_5m.csv"
    
    print("Binance Candle Downloader")
    print("=========================")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Days: {days}")
    print()
    
    try:
        ohlcv = download_candles(symbol, timeframe, days)
        
        if ohlcv:
            save_to_csv(ohlcv, output_path)
            
            # Print summary
            start_time = ohlcv[0][0]
            end_time = ohlcv[-1][0]
            print(f"\nSuccess!")
            print(f"Total candles: {len(ohlcv)}")
            print(f"Start: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start_time / 1000))}")
            print(f"End: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end_time / 1000))}")
            print(f"Saved to: {output_path}")
        else:
            print("No candles downloaded")
            
    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()