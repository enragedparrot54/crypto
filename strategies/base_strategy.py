class BaseStrategy:
    """Base class for trading strategies."""

    def on_candle(self, history, broker, symbol):
        """Process a new candle and return a trading signal.
        
        Args:
            history: List of candle dicts with OHLCV data
            broker: Broker instance to check positions and execute trades
            symbol: Trading symbol
            
        Returns:
            "BUY", "SELL", or "HOLD"
        """
        raise NotImplementedError("Subclasses must implement this method")