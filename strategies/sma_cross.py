"""
Simple SMA Crossover Strategy.

Buys when fast SMA crosses above slow SMA.
Sells when fast SMA crosses below slow SMA.
"""

from strategies.base_strategy import BaseStrategy


class SMACrossStrategy(BaseStrategy):
    """SMA Crossover strategy.
    
    Entry (BUY): Fast SMA crosses above Slow SMA
    Exit (SELL): Fast SMA crosses below Slow SMA
    """

    def __init__(self, fast=10, slow=30, risk_percent=1.0):
        """Initialize strategy parameters.
        
        Args:
            fast: Fast SMA period (default: 10)
            slow: Slow SMA period (default: 30)
            risk_percent: Risk per trade (unused, for compatibility)
        """
        self.fast = fast
        self.slow = slow
        self.risk_percent = risk_percent
        self.prev_fast_ma = None
        self.prev_slow_ma = None

    def _calculate_sma(self, closes, period):
        """Calculate simple moving average.
        
        Args:
            closes: List of close prices
            period: SMA period
            
        Returns:
            SMA value, or None if not enough data
        """
        if len(closes) < period:
            return None
        return sum(closes[-period:]) / period

    def on_candle(self, history, broker, symbol):
        """Process candle and generate trading signal.
        
        Args:
            history: List of candles up to current
            broker: PaperBroker instance
            symbol: Trading symbol
            
        Returns:
            "BUY", "SELL", or "HOLD"
        """
        # Need enough history
        if len(history) < self.slow + 1:
            return "HOLD"
        
        # Extract close prices
        closes = [c["close"] for c in history]
        
        # Calculate current SMAs
        fast_ma = self._calculate_sma(closes, self.fast)
        slow_ma = self._calculate_sma(closes, self.slow)
        
        if fast_ma is None or slow_ma is None:
            return "HOLD"
        
        signal = "HOLD"
        
        # Check for crossover (need previous values)
        if self.prev_fast_ma is not None and self.prev_slow_ma is not None:
            has_position = broker.has_position(symbol)
            
            # Bullish crossover: fast crosses above slow
            if self.prev_fast_ma <= self.prev_slow_ma and fast_ma > slow_ma:
                if not has_position:
                    signal = "BUY"
            
            # Bearish crossover: fast crosses below slow
            elif self.prev_fast_ma >= self.prev_slow_ma and fast_ma < slow_ma:
                if has_position:
                    signal = "SELL"
        
        # Store for next iteration
        self.prev_fast_ma = fast_ma
        self.prev_slow_ma = slow_ma
        
        return signal