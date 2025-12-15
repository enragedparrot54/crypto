from broker.paper_broker import PaperBroker
from datetime import datetime
import csv
import os

import config


class BacktestEngine:
    """Engine for running backtests on trading strategies."""

    def __init__(self, verbose=True):
        self.results = []
        self.broker = None
        self.initial_balance = config.INITIAL_BALANCE
        self.verbose = verbose
        self.equity_curve = []
        self.candles_since_last_sell = None  # None means no cooldown active
        self.ema_value = None  # Cached EMA value
        self.last_buy_price = None  # Track entry price for PnL calculation

    def _log(self, message):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def _format_timestamp(self, ts):
        """Convert timestamp to readable format."""
        try:
            return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
        except:
            return str(ts)

    def _init_trade_log(self):
        """Initialize the trades CSV file with headers."""
        with open(config.TRADES_LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'side', 'price', 'size', 'pnl', 'balance_after'])

    def _init_equity_log(self):
        """Initialize the equity CSV file with headers."""
        with open(config.EQUITY_LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'equity'])

    def _log_equity_to_csv(self, timestamp, equity):
        """Append equity value to the CSV log file."""
        with open(config.EQUITY_LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self._format_timestamp(timestamp),
                f"{equity:.2f}"
            ])

    def _log_trade_to_csv(self, timestamp, side, price, size, pnl, balance_after):
        """Append a trade to the CSV log file."""
        with open(config.TRADES_LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self._format_timestamp(timestamp),
                side,
                f"{price:.2f}",
                f"{size:.6f}",
                f"{pnl:.2f}",
                f"{balance_after:.2f}"
            ])

    def _update_ema(self, close_price):
        """Update EMA with new close price (incremental calculation)."""
        k = 2 / (config.TREND_EMA_PERIOD + 1)
        
        if self.ema_value is None:
            self.ema_value = close_price
        else:
            self.ema_value = (close_price * k) + (self.ema_value * (1 - k))
        
        return self.ema_value

    def _is_above_trend(self, price):
        """Check if price is above EMA trend filter."""
        if self.ema_value is None:
            return False
        return price > self.ema_value

    def _calculate_position_size(self, price):
        """Calculate position size based on risk management."""
        if price <= 0 or self.broker.cash <= 0:
            return 0.0
        
        risk_amount = self.broker.cash * (config.RISK_PER_TRADE_PCT / 100)
        stop_distance = price * (abs(config.STOP_LOSS_PCT) / 100)
        
        if stop_distance <= 0:
            return 0.0
        
        position_size = risk_amount / stop_distance
        max_affordable = self.broker.cash / price
        position_size = min(position_size, max_affordable)
        
        return position_size

    def _check_stop_loss_take_profit(self, symbol, current_price):
        """Check if stop loss or take profit has been hit."""
        if not self.broker.has_position(symbol):
            return None
        
        entry_price = self.broker.position_entry(symbol)
        if entry_price <= 0:
            return None
        
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        if pnl_pct <= config.STOP_LOSS_PCT:
            return "STOP_LOSS"
        elif pnl_pct >= config.TAKE_PROFIT_PCT:
            return "TAKE_PROFIT"
        
        return None

    def run_backtest(self, strategy, candles, symbol):
        """Run a backtest with the given strategy and candles.
        
        Processes candles one at a time in chronological order.
        Strategy only sees historical data up to current index (no look-ahead bias).
        
        Args:
            strategy: Trading strategy with on_candle(history, broker, symbol) method
            candles: List of candle dicts with timestamp, open, high, low, close, volume
            symbol: Trading symbol (e.g., "BTC/USDT")
            
        Returns:
            List of trade result dicts
        """
        # Initialize state
        self.broker = PaperBroker(initial_cash=self.initial_balance)
        self.results = []
        self.equity_curve = []
        self.candles_since_last_sell = None
        self.ema_value = None
        self.last_buy_price = None
        
        # Historical candles visible to strategy (prevents look-ahead bias)
        history = []

        # Initialize CSV logs
        self._init_trade_log()
        self._init_equity_log()

        self._log(f"\n{'='*50}")
        self._log("BACKTEST STARTED")
        self._log(f"{'='*50}")
        self._log(f"Symbol: {symbol}")
        self._log(f"Candles: {len(candles)}")
        self._log(f"Initial Balance: ${self.initial_balance:.2f}")
        self._log(f"Risk Per Trade: {config.RISK_PER_TRADE_PCT}%")
        self._log(f"Cooldown Period: {config.COOLDOWN_CANDLES} candles")
        self._log(f"Stop Loss: {config.STOP_LOSS_PCT}%")
        self._log(f"Take Profit: +{config.TAKE_PROFIT_PCT}%")
        self._log(f"Trend Filter: EMA({config.TREND_EMA_PERIOD})")
        self._log(f"{'='*50}\n")

        # Process candles one at a time (no look-ahead)
        for i, candle in enumerate(candles):
            # Add current candle to history (strategy can only see up to current index)
            history.append(candle)
            
            # Use open price for order execution (realistic fill)
            price = candle["open"]
            
            # Update EMA with previous close (avoid look-ahead on current candle)
            if i > 0:
                self._update_ema(candles[i - 1]["close"])
            
            # Record equity at each candle
            current_equity = self.broker.get_equity({symbol: price})
            self.equity_curve.append(current_equity)
            self._log_equity_to_csv(candle["timestamp"], current_equity)

            # Update cooldown counter
            if self.candles_since_last_sell is not None:
                self.candles_since_last_sell += 1

            # Check stop loss / take profit FIRST (before strategy signal)
            sl_tp_trigger = self._check_stop_loss_take_profit(symbol, price)
            
            if sl_tp_trigger:
                amount = self.broker.position_amount(symbol)
                if amount > 0 and self.broker._sell(symbol, amount, price):
                    balance_after = self.broker.get_equity({symbol: price})
                    pnl = (price - self.last_buy_price) * amount if self.last_buy_price else 0
                    
                    self.results.append({
                        "timestamp": candle["timestamp"],
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "amount": amount,
                        "balance_after": balance_after,
                        "trigger": sl_tp_trigger,
                        "pnl": pnl
                    })
                    
                    self._log_trade_to_csv(candle["timestamp"], "SELL", price, amount, pnl, balance_after)
                    
                    emoji = "🛑" if sl_tp_trigger == "STOP_LOSS" else "🎯"
                    self._log(f"{emoji} {sl_tp_trigger} | {self._format_timestamp(candle['timestamp'])} | "
                              f"{amount:.6f} {symbol} @ ${price:.2f} | "
                              f"PnL: ${pnl:.2f} | Balance: ${balance_after:.2f}")
                    
                    self.last_buy_price = None
                    self.candles_since_last_sell = 0
                continue  # Skip strategy signal this candle

            # Get signal from strategy (strategy only sees history up to current candle)
            signal = strategy.on_candle(history, self.broker, symbol)
            
            # Normalize signal to uppercase
            if signal:
                signal = signal.upper()

            if signal == "BUY":
                # Block if already in position (only one position at a time)
                if self.broker.has_position(symbol):
                    continue
                
                # Check cooldown
                if self.candles_since_last_sell is not None and self.candles_since_last_sell < config.COOLDOWN_CANDLES:
                    self._log(f"⏸️  BUY BLOCKED | Cooldown: {config.COOLDOWN_CANDLES - self.candles_since_last_sell} candles remaining")
                    continue

                # Check trend filter
                if not self._is_above_trend(price):
                    if self.ema_value is not None:
                        self._log(f"📉 BUY BLOCKED | Price ${price:.2f} below EMA({config.TREND_EMA_PERIOD}) ${self.ema_value:.2f}")
                    continue

                if self.broker.cash <= 0:
                    continue
                
                # Calculate position size
                amount = self._calculate_position_size(price)
                
                if amount <= 0:
                    continue
                    
                # Execute buy through paper broker
                if self.broker._buy(symbol, amount, price):
                    balance_after = self.broker.get_equity({symbol: price})
                    self.last_buy_price = price
                    
                    self.results.append({
                        "timestamp": candle["timestamp"],
                        "type": "BUY",
                        "symbol": symbol,
                        "price": price,
                        "amount": amount,
                        "balance_after": balance_after,
                        "trigger": "STRATEGY",
                        "pnl": 0
                    })
                    
                    self._log_trade_to_csv(candle["timestamp"], "BUY", price, amount, 0, balance_after)
                    
                    self._log(f"🟢 BUY  | {self._format_timestamp(candle['timestamp'])} | "
                              f"{amount:.6f} {symbol} @ ${price:.2f} | "
                              f"Balance: ${balance_after:.2f}")

            elif signal == "SELL":
                # Only sell if we have a position (enforces BUY → SELL order)
                if not self.broker.has_position(symbol):
                    continue
                    
                amount = self.broker.position_amount(symbol)
                if amount <= 0:
                    continue
                    
                # Execute sell through paper broker
                if self.broker._sell(symbol, amount, price):
                    balance_after = self.broker.get_equity({symbol: price})
                    pnl = (price - self.last_buy_price) * amount if self.last_buy_price else 0
                    
                    self.results.append({
                        "timestamp": candle["timestamp"],
                        "type": "SELL",
                        "symbol": symbol,
                        "price": price,
                        "amount": amount,
                        "balance_after": balance_after,
                        "trigger": "STRATEGY",
                        "pnl": pnl
                    })
                    
                    self._log_trade_to_csv(candle["timestamp"], "SELL", price, amount, pnl, balance_after)
                    
                    self._log(f"🔴 SELL | {self._format_timestamp(candle['timestamp'])} | "
                              f"{amount:.6f} {symbol} @ ${price:.2f} | "
                              f"PnL: ${pnl:.2f} | Balance: ${balance_after:.2f}")
                    
                    self.last_buy_price = None
                    self.candles_since_last_sell = 0
            
            # signal == "HOLD" or None: do nothing

        # Print final summary
        self._print_summary(symbol)
        return self.results

    def _calculate_max_drawdown(self):
        """Calculate maximum drawdown from equity curve."""
        if len(self.equity_curve) < 2:
            return 0.0
        
        peak = self.equity_curve[0]
        max_drawdown = 0.0
        
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown

    def _calculate_win_rate(self):
        """Calculate win rate from completed trades."""
        trades = []
        buy_price = None
        
        for result in self.results:
            if result["type"] == "BUY":
                buy_price = result["price"]
            elif result["type"] == "SELL" and buy_price is not None:
                profit = result["price"] - buy_price
                trades.append(profit)
                buy_price = None
        
        if not trades:
            return 0.0, 0, 0
        
        winning_trades = sum(1 for t in trades if t > 0)
        return (winning_trades / len(trades)) * 100, winning_trades, len(trades)

    def _calculate_avg_profit_per_trade(self):
        """Calculate average profit per completed trade."""
        trades = []
        buy_price = None
        buy_amount = None
        
        for result in self.results:
            if result["type"] == "BUY":
                buy_price = result["price"]
                buy_amount = result["amount"]
            elif result["type"] == "SELL" and buy_price is not None:
                profit = (result["price"] - buy_price) * buy_amount
                trades.append(profit)
                buy_price = None
                buy_amount = None
        
        if not trades:
            return 0.0
        
        return sum(trades) / len(trades)

    def _count_triggers(self):
        """Count sells by trigger type."""
        triggers = {"STOP_LOSS": 0, "TAKE_PROFIT": 0, "STRATEGY": 0}
        for result in self.results:
            if result["type"] == "SELL":
                trigger = result.get("trigger", "STRATEGY")
                triggers[trigger] = triggers.get(trigger, 0) + 1
        return triggers

    def _print_summary(self, symbol):
        """Print backtest summary."""
        self._log(f"\n{'='*50}")
        self._log("BACKTEST COMPLETE")
        self._log(f"{'='*50}")
        
        performance = self.evaluate_performance()
        win_rate, winning, total_round_trips = self._calculate_win_rate()
        max_drawdown = self._calculate_max_drawdown()
        avg_profit = self._calculate_avg_profit_per_trade()
        triggers = self._count_triggers()
        
        pnl_percent = (performance['pnl'] / self.initial_balance) * 100
        
        self._log(f"\n📊 PERFORMANCE SUMMARY")
        self._log(f"-" * 50)
        self._log(f"Starting Balance:     ${self.initial_balance:.2f}")
        self._log(f"Final Balance:        ${performance['ending_balance']:.2f}")
        self._log(f"Net Profit:           ${performance['pnl']:.2f} ({pnl_percent:.2f}%)")
        self._log(f"-" * 50)
        self._log(f"Total Trades:         {performance['num_trades']}")
        self._log(f"Round-trip Trades:    {total_round_trips}")
        self._log(f"Winning Trades:       {winning}")
        self._log(f"Win Rate:             {win_rate:.2f}%")
        self._log(f"-" * 50)
        self._log(f"Max Drawdown:         {max_drawdown:.2f}%")
        self._log(f"Avg Profit/Trade:     ${avg_profit:.2f}")
        self._log(f"-" * 50)
        self._log(f"Stop Losses Hit:      {triggers['STOP_LOSS']}")
        self._log(f"Take Profits Hit:     {triggers['TAKE_PROFIT']}")
        self._log(f"Strategy Sells:       {triggers['STRATEGY']}")
        
        if self.broker.positions:
            self._log(f"\n📦 Open Positions:")
            for sym, pos in self.broker.positions.items():
                self._log(f"  {sym}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f}")
        
        self._log(f"\n📁 Trade log: {config.TRADES_LOG_FILE}")
        self._log(f"📈 Equity curve: {config.EQUITY_LOG_FILE}")
        self._log(f"{'='*50}\n")

    def evaluate_performance(self):
        """Evaluate backtest performance."""
        if self.broker is None:
            return {
                "ending_balance": 0.0,
                "num_trades": 0,
                "pnl": 0.0,
            }

        if self.equity_curve:
            ending_balance = self.equity_curve[-1]
        else:
            ending_balance = self.broker.cash

        return {
            "ending_balance": ending_balance,
            "num_trades": len(self.results),
            "pnl": ending_balance - self.initial_balance,
        }