class PaperBroker:
    """Paper trading broker for backtesting."""

    def __init__(self, initial_cash=10000.0):
        self.cash = initial_cash
        self.positions = {}  # symbol -> {"amount": float, "entry_price": float}
        self.trade_log = []

    def get_position(self, symbol):
        """Get position amount for a symbol."""
        if symbol in self.positions:
            return self.positions[symbol]["amount"]
        return 0.0

    def has_position(self, symbol):
        """Check if we have a position in a symbol."""
        return symbol in self.positions and self.positions[symbol]["amount"] > 0

    def position_amount(self, symbol):
        """Get the amount held for a symbol."""
        if symbol in self.positions:
            return self.positions[symbol]["amount"]
        return 0.0

    def position_entry(self, symbol):
        """Get the entry price for a symbol."""
        if symbol in self.positions:
            return self.positions[symbol]["entry_price"]
        return 0.0

    def _buy(self, symbol, amount, price):
        """Execute a buy order.

        Args:
            symbol: Trading symbol
            amount: Amount to buy
            price: Price per unit
        """
        cost = amount * price
        if cost > self.cash:
            return False

        self.cash -= cost

        if symbol in self.positions:
            # Weighted average entry price
            current = self.positions[symbol]
            total_amount = current["amount"] + amount
            weighted_entry = (
                (current["amount"] * current["entry_price"]) + (amount * price)
            ) / total_amount
            self.positions[symbol] = {
                "amount": total_amount,
                "entry_price": weighted_entry
            }
        else:
            self.positions[symbol] = {
                "amount": amount,
                "entry_price": price
            }

        self.trade_log.append({
            "type": "BUY",
            "symbol": symbol,
            "amount": amount,
            "price": price
        })
        return True

    def _sell(self, symbol, amount, price):
        """Execute a sell order.

        Args:
            symbol: Trading symbol
            amount: Amount to sell
            price: Price per unit
        """
        if symbol not in self.positions:
            return False

        current_amount = self.positions[symbol]["amount"]
        if amount > current_amount:
            return False

        self.cash += amount * price
        new_amount = current_amount - amount

        if new_amount <= 0:
            del self.positions[symbol]
        else:
            self.positions[symbol]["amount"] = new_amount

        self.trade_log.append({
            "type": "SELL",
            "symbol": symbol,
            "amount": amount,
            "price": price
        })
        return True

    def get_equity(self, prices):
        """Calculate total equity (cash + positions value).

        Args:
            prices: Dict of symbol -> current price
        """
        equity = self.cash
        for symbol, position in self.positions.items():
            if symbol in prices:
                equity += position["amount"] * prices[symbol]
        return equity