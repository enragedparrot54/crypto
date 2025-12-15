from broker.paper_broker import PaperBroker


class BacktestEngine:
    """Engine for running backtests on trading strategies."""

    def __init__(self):
        self.results = []
        self.broker = None
        self.initial_balance = 10000.0

    def run_backtest(self, strategy, candles, symbol):
        """Run a backtest with the given strategy and candles.

        Args:
            strategy: Strategy instance with on_candle() or execute_strategy() method
            candles: List of candle dicts with OHLCV data
            symbol: Trading symbol

        Returns:
            List of trade result dicts
        """
        self.broker = PaperBroker(initial_cash=self.initial_balance)
        self.results = []
        history = []

        for candle in candles:
            history.append(candle)
            price = candle["open"]

            # Support both on_candle() and execute_strategy() methods
            if hasattr(strategy, "execute_strategy"):
                order = strategy.execute_strategy(history)
                if order:
                    success = self.broker.execute_order(order, price, symbol)
                    if success:
                        self.results.append(
                            {
                                "timestamp": candle["timestamp"],
                                "type": order.get("type", order.get("side", "UNKNOWN")),
                                "symbol": symbol,
                                "price": price,
                                "amount": order.get("amount", 0),
                                "balance_after": self.broker.get_equity({symbol: price}),
                            }
                        )
            else:
                # Fallback to on_candle()
                signal = strategy.on_candle(history, self.broker, symbol)

                if signal == "BUY":
                    amount = self.broker.cash / price
                    if amount > 0 and self.broker._buy(symbol, amount, price):
                        self.results.append(
                            {
                                "timestamp": candle["timestamp"],
                                "type": "BUY",
                                "symbol": symbol,
                                "price": price,
                                "amount": amount,
                                "balance_after": self.broker.get_equity({symbol: price}),
                            }
                        )

                elif signal == "SELL":
                    amount = self.broker.position_amount(symbol)
                    if amount > 0 and self.broker._sell(symbol, amount, price):
                        self.results.append(
                            {
                                "timestamp": candle["timestamp"],
                                "type": "SELL",
                                "symbol": symbol,
                                "price": price,
                                "amount": amount,
                                "balance_after": self.broker.get_equity({symbol: price}),
                            }
                        )

        return self.results

    def evaluate_performance(self):
        """Evaluate backtest performance.

        Returns:
            Dict with performance metrics
        """
        if self.broker is None:
            return {
                "ending_balance": 0.0,
                "num_trades": 0,
                "pnl": 0.0,
            }

        # Get ending balance (cash + any remaining positions at last known price)
        if self.results:
            ending_balance = self.results[-1]["balance_after"]
        else:
            ending_balance = self.broker.cash

        return {
            "ending_balance": ending_balance,
            "num_trades": len(self.results),
            "pnl": ending_balance - self.initial_balance,
        }