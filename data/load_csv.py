"""
CSV data loader for historical OHLCV candles.

NO API CALLS - CSV files only.
Fully reproducible offline.
"""

import csv
import os
import sys


def load_candles(path):
    """Load candles from CSV file with validation.
    
    Args:
        path: Path to CSV file
        
    Returns:
        List of candle dicts with float values
    """
    # Check file exists
    if not os.path.exists(path):
        print(f"\n❌ ERROR: File not found")
        print(f"   Path: {path}")
        print(f"\n   Please create a CSV file with format:")
        print(f"   timestamp,open,high,low,close,volume")
        sys.exit(1)
    
    # Check file not empty
    if os.path.getsize(path) == 0:
        print(f"\n❌ ERROR: File is empty")
        print(f"   Path: {path}")
        sys.exit(1)
    
    candles = []
    errors = []
    
    try:
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            
            # Validate headers exist
            if reader.fieldnames is None:
                print(f"\n❌ ERROR: No headers found in CSV")
                print(f"   Path: {path}")
                print(f"\n   Expected headers:")
                print(f"   timestamp,open,high,low,close,volume")
                sys.exit(1)
            
            # Validate required columns
            required = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
            actual = set(reader.fieldnames)
            missing = required - actual
            
            if missing:
                print(f"\n❌ ERROR: Missing required columns")
                print(f"   Missing: {missing}")
                print(f"   Found:   {actual}")
                print(f"\n   Required columns:")
                print(f"   timestamp,open,high,low,close,volume")
                sys.exit(1)
            
            # Read and validate each row
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    candle = validate_candle_row(row, row_num)
                    if candle:
                        candles.append(candle)
                except ValueError as e:
                    errors.append(f"Row {row_num}: {e}")
                    if len(errors) >= 10:
                        errors.append("... (additional errors suppressed)")
                        break
    
    except PermissionError:
        print(f"\n❌ ERROR: Permission denied")
        print(f"   Cannot read file: {path}")
        sys.exit(1)
    except csv.Error as e:
        print(f"\n❌ ERROR: Invalid CSV format")
        print(f"   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: Failed to read file")
        print(f"   {e}")
        sys.exit(1)
    
    # Report validation errors
    if errors:
        print(f"\n⚠️  WARNING: {len(errors)} rows had errors:")
        for err in errors[:5]:
            print(f"   {err}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")
    
    # Check we have data
    if not candles:
        print(f"\n❌ ERROR: No valid candles found")
        print(f"   Path: {path}")
        print(f"\n   Check that your CSV has valid numeric data.")
        sys.exit(1)
    
    # Validate minimum candle count
    min_candles = 100
    if len(candles) < min_candles:
        print(f"\n⚠️  WARNING: Only {len(candles)} candles loaded")
        print(f"   Recommend at least {min_candles} candles for reliable backtesting")
    
    print(f"✅ Loaded {len(candles)} candles from {path}")
    return candles


def validate_candle_row(row, row_num):
    """Validate a single candle row.
    
    Args:
        row: Dict from CSV reader
        row_num: Row number for error reporting
        
    Returns:
        Valid candle dict or None
        
    Raises:
        ValueError if validation fails
    """
    # Parse timestamp
    try:
        timestamp = float(row["timestamp"])
        if timestamp <= 0:
            raise ValueError("timestamp must be positive")
    except (ValueError, TypeError):
        raise ValueError(f"invalid timestamp: {row.get('timestamp', 'missing')}")
    
    # Parse OHLCV with validation
    try:
        open_price = float(row["open"])
        high_price = float(row["high"])
        low_price = float(row["low"])
        close_price = float(row["close"])
        volume = float(row["volume"])
    except (ValueError, TypeError) as e:
        raise ValueError(f"invalid numeric value: {e}")
    
    # Validate prices are positive
    if open_price <= 0:
        raise ValueError(f"open price must be positive: {open_price}")
    if high_price <= 0:
        raise ValueError(f"high price must be positive: {high_price}")
    if low_price <= 0:
        raise ValueError(f"low price must be positive: {low_price}")
    if close_price <= 0:
        raise ValueError(f"close price must be positive: {close_price}")
    if volume < 0:
        raise ValueError(f"volume cannot be negative: {volume}")
    
    # Validate OHLC relationships
    if high_price < low_price:
        raise ValueError(f"high ({high_price}) < low ({low_price})")
    if high_price < open_price or high_price < close_price:
        raise ValueError(f"high ({high_price}) is not the highest price")
    if low_price > open_price or low_price > close_price:
        raise ValueError(f"low ({low_price}) is not the lowest price")
    
    return {
        "timestamp": timestamp,
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "close": close_price,
        "volume": volume
    }


def validate_candles(candles):
    """Validate candle list integrity.
    
    Args:
        candles: List of candle dicts
        
    Returns:
        True if valid, exits on error
    """
    if not candles:
        print("\n❌ ERROR: Empty candle list")
        sys.exit(1)
    
    if not isinstance(candles, list):
        print("\n❌ ERROR: Candles must be a list")
        sys.exit(1)
    
    # Check for required keys
    required_keys = {"timestamp", "open", "high", "low", "close", "volume"}
    
    for i, candle in enumerate(candles[:5]):  # Check first 5
        if not isinstance(candle, dict):
            print(f"\n❌ ERROR: Candle {i} is not a dict")
            sys.exit(1)
        
        missing = required_keys - set(candle.keys())
        if missing:
            print(f"\n❌ ERROR: Candle {i} missing keys: {missing}")
            sys.exit(1)
    
    return True