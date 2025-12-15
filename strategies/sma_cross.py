from strategies.base_strategy import BaseStrategy


class SMACrossStrategy(BaseStrategy):
    def __init__(self, fast=10, slow=20, trade_fraction=1.0):
        self.fast = fast
        self.slow = slow
        self.trade_fraction = trade_fraction

    def _sma(self, prices, period):
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    def on_candle(self, history, broker, symbol):
        """Generate trading signal based on SMA crossover.
        
        Args:
            history: List of candle dicts with 'close' prices
            broker: Broker instance to check positions
            symbol: Trading symbol
            
        Returns:
            "BUY", "SELL", or "HOLD"
        """
        if len(history) < self.slow + 1:
            return "HOLD"

        closes = [c['close'] for c in history]

        # Current SMAs
        fast_sma = self._sma(closes, self.fast)
        slow_sma = self._sma(closes, self.slow)

        # Previous SMAs (excluding last candle)
        prev_closes = closes[:-1]
        prev_fast_sma = self._sma(prev_closes, self.fast)
        prev_slow_sma = self._sma(prev_closes, self.slow)

        if None in (fast_sma, slow_sma, prev_fast_sma, prev_slow_sma):
            return "HOLD"

        has_position = broker.get_position(symbol) > 0

        # BUY: fast crosses above slow and no position
        if prev_fast_sma <= prev_slow_sma and fast_sma > slow_sma and not has_position:
            return "BUY"

        # SELL: fast crosses below slow and has position
        if prev_fast_sma >= prev_slow_sma and fast_sma < slow_sma and has_position:
            return "SELL"

        return