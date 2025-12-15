from strategies.base_strategy import BaseStrategy


class BuyAndHoldStrategy(BaseStrategy):
    """A simple buy-and-hold strategy that buys once and never sells."""

    def __init__(self, symbol="BTC/USDT"):
        self.symbol = symbol
        self.has_bought = False

    def execute_strategy(self, history):
        """Execute buy-and-hold strategy.
        
        Args:
            history: List of candle dicts with OHLCV data
            
        Returns:
            Order dict on first candle, None otherwise
        """
        if not history:
            return None

        # Buy only on the first candle
        if not self.has_bought:
            self.has_bought = True
            candle = history[-1]
            return {
                "type": "BUY",
                "symbol": self.symbol,
                "amount": 0,  # 0 means use all available cash
                "price": candle["open"]
            }

        return None

    def on_candle(self, history, broker, symbol):
        """Fallback for on_candle interface."""
        if not self.has_bought:
            self.has_bought = True
            return "BUY"