"""
Strategies - LONG ONLY.
All strategies return: "BUY", "SELL", or "HOLD".
"""

from strategies.base_strategy import BaseStrategy
from strategies.breakout_ma import BreakoutMAStrategy
from strategies.sol_daytrader import SOLDayTraderStrategy
from strategies.sma_cross import SMACrossStrategy

__all__ = [
    "BaseStrategy",
    "BreakoutMAStrategy",
    "SOLDayTraderStrategy",
    "SMACrossStrategy"
]