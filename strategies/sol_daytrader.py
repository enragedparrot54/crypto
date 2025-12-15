"""
SOL Day Trader - LONG ONLY.
Returns: "BUY", "SELL", or "HOLD".
"""

from strategies.base_strategy import BaseStrategy


class SOLDayTraderStrategy(BaseStrategy):
    """EMA crossover strategy - LONG ONLY.
    
    Signals:
    - "BUY"  = EMA20 crosses above EMA50 (open long)
    - "SELL" = EMA20 crosses below EMA50 (close long)
    - "HOLD" = No crossover
    """

    def __init__(self, ema_fast=20, ema_slow=50, atr_period=14, atr_threshold=0.3):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.atr_period = atr_period
        self.atr_threshold = atr_threshold
        self.prev_ema_fast = None
        self.prev_ema_slow = None

    def _ema(self, closes, period):
        if len(closes) < period:
            return None
        k = 2 / (period + 1)
        ema = sum(closes[:period]) / period
        for p in closes[period:]:
            ema = (p * k) + (ema * (1 - k))
        return ema

    def _atr(self, candles, period):
        if len(candles) < period + 1:
            return None
        trs = []
        for i in range(1, len(candles)):
            h = candles[i]["high"]
            l = candles[i]["low"]
            pc = candles[i - 1]["close"]
            trs.append(max(h - l, abs(h - pc), abs(l - pc)))
        if len(trs) < period:
            return None
        return sum(trs[-period:]) / period

    def on_candle(self, history, broker, symbol):
        """Return "BUY", "SELL", or "HOLD". LONG ONLY."""
        min_len = max(self.ema_slow, self.atr_period) + 10
        if len(history) < min_len:
            return "HOLD"

        closes = [c["close"] for c in history]
        price = closes[-1]

        ef = self._ema(closes, self.ema_fast)
        es = self._ema(closes, self.ema_slow)
        if ef is None or es is None:
            return "HOLD"

        atr = self._atr(history, self.atr_period)

        # Detect crossover
        cross = None
        if self.prev_ema_fast is not None and self.prev_ema_slow is not None:
            if self.prev_ema_fast <= self.prev_ema_slow and ef > es:
                cross = "BULLISH"
            elif self.prev_ema_fast >= self.prev_ema_slow and ef < es:
                cross = "BEARISH"

        self.prev_ema_fast = ef
        self.prev_ema_slow = es

        has_pos = broker.has_position(symbol)

        # SELL = Close existing LONG
        if has_pos and cross == "BEARISH":
            return "SELL"

        # BUY = Open new LONG (only if no position)
        if not has_pos and cross == "BULLISH":
            if atr and price > 0 and (atr / price) * 100 >= self.atr_threshold:
                return "BUY"

        return "HOLD"

    def reset(self):
        """Reset strategy state."""
        self.prev_ema_fast = None
        self.prev_ema_slow = None