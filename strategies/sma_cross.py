"""
SMA Cross Strategy - LONG ONLY.
Returns: "BUY", "SELL", or "HOLD".
"""

from strategies.base_strategy import BaseStrategy


class SMACrossStrategy(BaseStrategy):
    """Simple Moving Average crossover - LONG ONLY.
    
    Signals:
    - "BUY"  = Fast SMA crosses above slow SMA (open long)
    - "SELL" = Fast SMA crosses below slow SMA (close long)
    - "HOLD" = No crossover
    """

    def __init__(self, fast_period=10, slow_period=30):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.prev_fast = None
        self.prev_slow = None

    def _sma(self, closes, period):
        if len(closes) < period:
            return None
        return sum(closes[-period:]) / period

    def on_candle(self, history, broker, symbol):
        """Return "BUY", "SELL", or "HOLD". LONG ONLY."""
        if len(history) < self.slow_period + 5:
            return "HOLD"

        closes = [c["close"] for c in history]

        fast = self._sma(closes, self.fast_period)
        slow = self._sma(closes, self.slow_period)

        if fast is None or slow is None:
            return "HOLD"

        # Detect crossover
        cross = None
        if self.prev_fast is not None and self.prev_slow is not None:
            if self.prev_fast <= self.prev_slow and fast > slow:
                cross = "BULLISH"
            elif self.prev_fast >= self.prev_slow and fast < slow:
                cross = "BEARISH"

        self.prev_fast = fast
        self.prev_slow = slow

        has_pos = broker.has_position(symbol)

        # SELL = Close existing LONG
        if has_pos and cross == "BEARISH":
            return "SELL"

        # BUY = Open new LONG (only if no position)
        if not has_pos and cross == "BULLISH":
            return "BUY"

        return "HOLD"

    def reset(self):
        """Reset strategy state."""
        self.prev_fast = None
        self.prev_slow = None