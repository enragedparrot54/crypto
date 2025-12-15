"""
Base Strategy - LONG ONLY.
Returns: "BUY", "SELL", or "HOLD".
"""

from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """Base class for LONG ONLY strategies.
    
    Signal definitions:
    - "BUY"  = Open a LONG position
    - "SELL" = Close an existing LONG position
    - "HOLD" = Do nothing
    
    No short selling.
    """

    @abstractmethod
    def on_candle(self, history, broker, symbol):
        """Process candle and return signal.
        
        Args:
            history: List of candles up to current
            broker: PaperBroker instance
            symbol: Trading symbol
            
        Returns:
            "BUY", "SELL", or "HOLD"
        """
        pass

    def reset(self):
        """Reset strategy state."""
        pass