"""
CSV data loader for historical OHLCV candles.
No API calls - CSV files only.

Expected format:
    timestamp,open,high,low,close,volume

Returns data as-is (no reordering or modification).
"""

import csv
import os
import sys


def load_candles(path):
    """Load candles from CSV file.
    
    Reads CSV with columns: timestamp, open, high, low, close, volume
    Converts all numeric fields to float.
    Returns data in original order (no reordering).
    
    Args:
        path: Path to CSV file
        
    Returns:
        List of candle dicts:
        [
            {
                "timestamp": float,
                "open": float,
                "high": float,
                "low": float,
                "close": float,
                "volume": float
            },
            ...
        ]
    """
    # Check file exists
    if not os.path.exists(path):
        print(f"ERROR: Data file not found: {path}")
        print(f"\nTo use this backtester, create a CSV file with format:")
        print(f"  timestamp,open,high,low,close,volume")
        print(f"\nExample row:")
        print(f"  1609459200000,29000.00,29100.00,28900.00,29050.00,123.45")
        sys.exit(1)
    
    # Check file not empty
    if os.path.getsize(path) == 0:
        print(f"ERROR: Data file is empty: {path}")
        sys.exit(1)
    
    candles = []
    
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        
        # Validate headers exist
        if reader.fieldnames is None:
            print(f"ERROR: CSV file has no headers: {path}")
            sys.exit(1)
        
        # Validate required columns
        required_columns = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
        actual_columns = set(reader.fieldnames)
        missing = required_columns - actual_columns
        
        if missing:
            print(f"ERROR: CSV missing required columns: {missing}")
            print(f"Required: {required_columns}")
            print(f"Found: {actual_columns}")
            sys.exit(1)
        
        # Read rows
        row_num = 1  # Header is row 0
        for row in reader:
            row_num += 1
            try:
                candle = {
                    "timestamp": float(row["timestamp"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"])
                }
                candles.append(candle)
            except (ValueError, KeyError) as e:
                print(f"WARNING: Skipping invalid row {row_num}: {e}")
                continue
    
    # Check we got data
    if not candles:
        print(f"ERROR: No valid candles found in: {path}")
        sys.exit(1)
    
    print(f"✅ Loaded {len(candles)} candles from {path}")
    
    return candles


def validate_candles(candles):
    """Validate candle data integrity.
    
    Checks:
    - All required fields present
    - All values are positive numbers
    - High >= Low
    - High >= Open, Close
    - Low <= Open, Close
    
    Args:
        candles: List of candle dicts
        
    Returns:
        True if valid, False otherwise
    """
    if not candles:
        print("ERROR: Empty candle list")
        return False
    
    required_keys = {"timestamp", "open", "high", "low", "close", "volume"}
    
    for i, candle in enumerate(candles):
        # Check all keys present
        if not required_keys.issubset(candle.keys()):
            print(f"ERROR: Candle {i} missing keys: {required_keys - candle.keys()}")
            return False
        
        # Check positive values
        for key in ["open", "high", "low", "close"]:
            if candle[key] <= 0:
                print(f"ERROR: Candle {i} has non-positive {key}: {candle[key]}")
                return False
        
        # Check OHLC relationships
        if candle["high"] < candle["low"]:
            print(f"ERROR: Candle {i} has high < low")
            return False
        
        if candle["high"] < candle["open"] or candle["high"] < candle["close"]:
            print(f"WARNING: Candle {i} has high below open or close")
        
        if candle["low"] > candle["open"] or candle["low"] > candle["close"]:
            print(f"WARNING: Candle {i} has low above open or close")
    
    return True