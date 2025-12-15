"""
Trading strategies module.
"""

from strategies.base_strategy import BaseStrategy
from strategies.sma_cross import SMACrossStrategy
from strategies.breakout_ma import BreakoutMAStrategy

__all__ = ["BaseStrategy", "SMACrossStrategy", "BreakoutMAStrategy"]