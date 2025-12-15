"""
Base strategy interface.
All strategies must inherit from this class.
"""

from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    @abstractmethod
    def on_candle(self, history, broker, symbol):
        """Process a new candle and return a trading signal.
        
        Args:
            history: List of candle dicts up to current candle (no look-ahead)
                     Each candle has: timestamp, open, high, low, close, volume
            broker: PaperBroker instance for position checks
            symbol: Trading symbol (e.g., "BTC/USDT")
            
        Returns:
            "BUY", "SELL", or "HOLD"
        """
        pass

    def position_size(self, history):
        """Calculate position size for a trade."""
        return 0.0