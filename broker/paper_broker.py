"""
Paper Broker for backtesting.
Simulates order execution without real money.
No leverage. No margin. Simple and deterministic.
"""


class PaperBroker:
    """Simple paper trading broker for backtesting.
    
    Features:
    - One open position per symbol
    - Buy uses available cash
    - Sell closes position fully
    - No leverage or margin
    - Deterministic execution at specified price
    """

    def __init__(self, initial_cash=10000.0):
        """Initialize paper broker with starting cash.
        
        Args:
            initial_cash: Starting balance in USD
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}  # {symbol: {"amount": float, "entry_price": float}}

    def has_position(self, symbol):
        """Check if there is an open position for symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTC/USDT")
            
        Returns:
            True if position exists with amount > 0
        """
        if symbol not in self.positions:
            return False
        return self.positions[symbol]["amount"] > 0

    def position_amount(self, symbol):
        """Get position size for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position amount, or 0.0 if no position
        """
        if symbol not in self.positions:
            return 0.0
        return self.positions[symbol]["amount"]

    def position_entry(self, symbol):
        """Get entry price for symbol's position.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Entry price, or 0.0 if no position
        """
        if symbol not in self.positions:
            return 0.0
        return self.positions[symbol]["entry_price"]

    def get_equity(self, prices):
        """Calculate total equity (cash + position value).
        
        Args:
            prices: Dict of {symbol: current_price}
            
        Returns:
            Total equity value in USD
        """
        equity = self.cash
        
        for symbol, position in self.positions.items():
            if position["amount"] > 0 and symbol in prices:
                equity += position["amount"] * prices[symbol]
        
        return equity

    def _buy(self, symbol, amount, price):
        """Execute a buy order.
        
        Only one position per symbol allowed.
        Uses available cash to buy.
        
        Args:
            symbol: Trading symbol
            amount: Amount to buy
            price: Execution price
            
        Returns:
            True if order executed, False otherwise
        """
        # Validate inputs
        if amount <= 0 or price <= 0:
            return False
        
        # Block if already in position (one position per symbol)
        if self.has_position(symbol):
            return False
        
        # Calculate cost
        cost = amount * price
        
        # Check sufficient cash
        if cost > self.cash:
            return False
        
        # Execute buy
        self.cash -= cost
        self.positions[symbol] = {
            "amount": amount,
            "entry_price": price
        }
        
        return True

    def _sell(self, symbol, amount, price):
        """Execute a sell order.
        
        Closes position fully (ignores amount if it exceeds position).
        
        Args:
            symbol: Trading symbol
            amount: Amount to sell (will sell full position)
            price: Execution price
            
        Returns:
            True if order executed, False otherwise
        """
        # Validate inputs
        if amount <= 0 or price <= 0:
            return False
        
        # Check if position exists
        if not self.has_position(symbol):
            return False
        
        # Get actual position amount
        position_amount = self.positions[symbol]["amount"]
        
        # Sell the full position (or requested amount if smaller)
        sell_amount = min(amount, position_amount)
        
        # Calculate proceeds
        proceeds = sell_amount * price
        
        # Execute sell
        self.cash += proceeds
        
        # Close position fully
        self.positions[symbol] = {
            "amount": 0.0,
            "entry_price": 0.0
        }
        
        return True

    def reset(self):
        """Reset broker to initial state."""
        self.cash = self.initial_cash
        self.positions = {}

    def get_balance(self):
        """Get current cash balance.
        
        Returns:
            Available cash in USD
        """
        return self.cash

    def get_position_value(self, symbol, current_price):
        """Get current value of position.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            
        Returns:
            Position value in USD, or 0.0 if no position
        """
        if not self.has_position(symbol):
            return 0.0
        return self.positions[symbol]["amount"] * current_price

    def get_unrealized_pnl(self, symbol, current_price):
        """Get unrealized profit/loss for position.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            
        Returns:
            Unrealized PnL in USD, or 0.0 if no position
        """
        if not self.has_position(symbol):
            return 0.0
        
        position = self.positions[symbol]
        entry_value = position["amount"] * position["entry_price"]
        current_value = position["amount"] * current_price
        
        return current_value - entry_value

    def __repr__(self):
        """String representation of broker state."""
        return f"PaperBroker(cash=${self.cash:.2f}, positions={len(self.positions)})"