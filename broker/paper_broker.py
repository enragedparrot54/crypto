"""
Paper Broker - LONG ONLY.
One position max. No shorts. No leverage.
Starting balance: $1,000.
"""

import config


class PaperBroker:
    """LONG ONLY paper broker.
    
    Rules:
    - Starting balance: $1,000
    - One position at a time
    - BUY opens a LONG position
    - SELL closes the LONG position
    - No short selling
    - Position sizing uses available balance only
    - BUY ignored if position exists
    - SELL ignored if no position exists
    """

    DEFAULT_BALANCE = 1000.0

    def __init__(self, initial_cash=None):
        # Set starting balance to exactly $1,000
        if initial_cash is None:
            initial_cash = self.DEFAULT_BALANCE
        
        if not isinstance(initial_cash, (int, float)) or initial_cash <= 0:
            initial_cash = self.DEFAULT_BALANCE
        
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        
        # LONG position state
        self.position_symbol = None
        self.position_size = 0.0
        self.entry_price = 0.0

    def has_position(self, symbol=None):
        """Check if a LONG position exists."""
        if self.position_size <= 0:
            return False
        if symbol is not None and self.position_symbol != symbol:
            return False
        return True

    def position_amount(self, symbol=None):
        """Get LONG position size."""
        if not self.has_position(symbol):
            return 0.0
        return self.position_size

    def position_entry(self, symbol=None):
        """Get LONG entry price."""
        if not self.has_position(symbol):
            return 0.0
        return self.entry_price

    def get_balance(self):
        """Get available cash balance."""
        return self.cash

    def get_equity(self, price=None):
        """Get total equity (cash + position value)."""
        equity = self.cash
        if self.has_position():
            if isinstance(price, (int, float)) and price > 0:
                equity += self.position_size * price
        return equity

    def max_buy_amount(self, price):
        """Calculate max amount that can be bought with available balance."""
        if not isinstance(price, (int, float)) or price <= 0:
            return 0.0
        return self.cash / price

    def buy(self, symbol, amount, price):
        """Open LONG position using available balance only.
        
        Ignored if:
        - Position already exists
        - Invalid inputs
        - Insufficient cash (no leverage)
        """
        # Validate inputs
        if not symbol or not isinstance(symbol, str):
            return False
        if not isinstance(amount, (int, float)) or amount <= 0:
            return False
        if not isinstance(price, (int, float)) or price <= 0:
            return False
        
        # IGNORE: Position already exists
        if self.has_position():
            return False
        
        # Calculate cost
        cost = amount * price
        
        # BLOCK: Cannot exceed available balance (no leverage)
        if cost > self.cash:
            return False
        
        # Open LONG using available balance
        self.cash -= cost
        self.position_symbol = symbol
        self.position_size = float(amount)
        self.entry_price = float(price)
        
        return True

    def sell(self, symbol, amount, price):
        """Close LONG position.
        
        Ignored if:
        - No position exists
        - Invalid inputs
        
        Note: 'amount' parameter ignored, always sells full position.
        """
        # Validate inputs
        if not isinstance(price, (int, float)) or price <= 0:
            return False
        
        # IGNORE: No position to close
        if not self.has_position(symbol):
            return False
        
        # Close LONG (sell entire position)
        proceeds = self.position_size * price
        self.cash += proceeds
        
        # Clear position
        self.position_symbol = None
        self.position_size = 0.0
        self.entry_price = 0.0
        
        return True

    def reset(self):
        """Reset to initial state ($1,000)."""
        self.cash = self.initial_cash
        self.position_symbol = None
        self.position_size = 0.0
        self.entry_price = 0.0