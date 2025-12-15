import csv


def load_candles(path):
    """Load candles from CSV file.
    
    Args:
        path: Path to CSV file with columns: timestamp, open, high, low, close, volume
        
    Returns:
        List of dicts with float values
    """
    candles = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candle = {
                'timestamp': float(row['timestamp']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            }
            candles.append(candle)
    return candles