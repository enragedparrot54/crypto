"""
Simple Breakout + Moving Average Strategy.

This is a simplified intraday strategy for 5-minute candles.
NOT real ICT - just a basic breakout with trend filter.

Logic:
- BUY when price breaks above recent high AND above MA
- SELL when price breaks below MA
- Uses close prices only
"""

from strategies.base_strategy import BaseStrategy


class BreakoutMAStrategy(BaseStrategy):
    """Breakout strategy with moving average trend filter.
    
    Entry (BUY):
        - Price closes above highest high of lookback period
        - Price is above moving average (trend filter)
        
    Exit (SELL):
        - Price closes below moving average
        
    Uses close prices only to avoid look-ahead bias.
    """

    def __init__(self, lookback=20, ma_period=50):
        """Initialize strategy parameters.
        
        Args:
            lookback: Number of candles for recent high/low range (default: 20)
            ma_period: Moving average period for trend filter (default: 50)
        """
        self.lookback = lookback
        self.ma_period = ma_period

    def _calculate_ma(self, closes):
        """Calculate simple moving average.
        
        Args:
            closes: List of close prices
            
        Returns:
            Moving average value, or None if not enough data
        """
        if len(closes) < self.ma_period:
            return None
        
        # Use last ma_period closes
        recent_closes = closes[-self.ma_period:]
        return sum(recent_closes) / self.ma_period

    def _get_recent_high(self, candles):
        """Get highest high from recent candles.
        
        Args:
            candles: List of candle dicts
            
        Returns:
            Highest high value, or None if not enough data
        """
        if len(candles) < self.lookback + 1:
            return None
        
        # Look at candles BEFORE the current one (exclude current)
        lookback_candles = candles[-(self.lookback + 1):-1]
        return max(c["high"] for c in lookback_candles)

    def _get_recent_low(self, candles):
        """Get lowest low from recent candles.
        
        Args:
            candles: List of candle dicts
            
        Returns:
            Lowest low value, or None if not enough data
        """
        if len(candles) < self.lookback + 1:
            return None
        
        # Look at candles BEFORE the current one (exclude current)
        lookback_candles = candles[-(self.lookback + 1):-1]
        return min(c["low"] for c in lookback_candles)

    def on_candle(self, history, broker, symbol):
        """Process candle and generate trading signal.
        
        Args:
            history: List of candles up to current (no look-ahead)
            broker: PaperBroker instance
            symbol: Trading symbol
            
        Returns:
            "BUY", "SELL", or "HOLD"
        """
        # Need enough history for indicators
        min_history = max(self.lookback, self.ma_period) + 1
        if len(history) < min_history:
            return "HOLD"
        
        # Get current candle close price
        current_close = history[-1]["close"]
        
        # Extract close prices for MA calculation
        closes = [c["close"] for c in history]
        
        # Calculate moving average
        ma = self._calculate_ma(closes)
        if ma is None:
            return "HOLD"
        
        # Get recent high (excluding current candle)
        recent_high = self._get_recent_high(history)
        if recent_high is None:
            return "HOLD"
        
        # Check if we have a position
        has_position = broker.has_position(symbol)
        
        # === EXIT LOGIC ===
        # Sell if price closes below MA
        if has_position:
            if current_close < ma:
                return "SELL"
            return "HOLD"
        
        # === ENTRY LOGIC ===
        # Buy if:
        # 1. Price closes above recent high (breakout)
        # 2. Price is above MA (trend filter)
        if not has_position:
            breakout = current_close > recent_high
            above_ma = current_close > ma
            
            if breakout and above_ma:
                return "BUY"
        
        return "HOLD"