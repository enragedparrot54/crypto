"""
Breakout MA Strategy - LONG ONLY.
Returns: "BUY", "SELL", or "HOLD".
"""

from strategies.base_strategy import BaseStrategy


class BreakoutMAStrategy(BaseStrategy):
    """Breakout strategy with MA filter - LONG ONLY.
    
    Signals:
    - "BUY"  = Price breaks above recent high & above MA (open long)
    - "SELL" = Price falls below MA (close long)
    - "HOLD" = No signal
    """

    def __init__(self, lookback=20, ma_period=50):
        self.lookback = lookback
        self.ma_period = ma_period

    def on_candle(self, history, broker, symbol):
        """Return "BUY", "SELL", or "HOLD". LONG ONLY."""
        min_len = max(self.lookback, self.ma_period) + 5
        if len(history) < min_len:
            return "HOLD"

        closes = [c["close"] for c in history]
        price = closes[-1]

        # Calculate MA
        ma = sum(closes[-self.ma_period:]) / self.ma_period

        # Get highest high (excluding current candle)
        highest = max(c["high"] for c in history[-self.lookback - 1:-1])

        has_pos = broker.has_position(symbol)

        # SELL = Close existing LONG
        if has_pos and price < ma:
            return "SELL"

        # BUY = Open new LONG (only if no position)
        if not has_pos and price > highest and price > ma:
            return "BUY"

        return "HOLD"

    def reset(self):
        """Reset strategy state."""
        pass