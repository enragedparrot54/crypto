"""
Backtest Engine - LONG ONLY.
CSV-only. No live trading. No short selling.
"""

from broker.paper_broker import PaperBroker
from datetime import datetime
import csv
import sys

import config


class BacktestEngine:
    """Backtest engine - LONG ONLY.
    
    Rules:
    - BUY only executes if no position exists
    - SELL only executes if a position exists
    - All trades logged with timestamp, price, action
    """

    MIN_CANDLES_BEFORE_TRADING = 60

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.broker = None
        self.results = []
        self.equity_curve = []
        self.candles_since_last_sell = None
        self.ema_value = None
        self.last_buy_price = None

    def _log(self, message):
        if self.verbose:
            print(message)

    def _format_timestamp(self, ts):
        try:
            if not isinstance(ts, (int, float)) or ts <= 0:
                return str(ts)
            return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
        except (ValueError, OSError, OverflowError):
            return str(ts)

    def _safe_divide(self, num, denom, default=0.0):
        if denom == 0 or denom is None:
            return default
        return num / denom

    def _init_trade_log(self):
        try:
            with open(config.TRADES_LOG_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'action', 'symbol', 'price', 'size', 'pnl', 'balance'])
        except (IOError, PermissionError):
            pass

    def _init_equity_log(self):
        try:
            with open(config.EQUITY_LOG_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'equity'])
        except (IOError, PermissionError):
            pass

    def _log_trade(self, timestamp, action, symbol, price, size, pnl, balance):
        """Log trade to CSV and console."""
        ts_str = self._format_timestamp(timestamp)
        
        # Log to CSV
        try:
            with open(config.TRADES_LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([ts_str, action, symbol, f"{price:.2f}", f"{size:.6f}", f"{pnl:.2f}", f"{balance:.2f}"])
        except (IOError, PermissionError):
            pass
        
        # Log to console
        if action == "BUY":
            self._log(f"🟢 BUY  | {ts_str} | {symbol} | ${price:.2f} | Size: {size:.6f}")
        elif action == "SELL":
            pnl_emoji = "✅" if pnl >= 0 else "❌"
            self._log(f"🔴 SELL | {ts_str} | {symbol} | ${price:.2f} | PnL: ${pnl:+.2f} {pnl_emoji} | Balance: ${balance:.2f}")

    def _log_equity(self, timestamp, equity):
        try:
            with open(config.EQUITY_LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([self._format_timestamp(timestamp), f"{equity:.2f}"])
        except (IOError, PermissionError):
            pass

    def _update_ema(self, close_price):
        if not isinstance(close_price, (int, float)) or close_price <= 0:
            return self.ema_value
        period = config.TREND_EMA_PERIOD if config.TREND_EMA_PERIOD > 0 else 200
        k = 2 / (period + 1)
        if self.ema_value is None:
            self.ema_value = close_price
        else:
            self.ema_value = (close_price * k) + (self.ema_value * (1 - k))
        return self.ema_value

    def _is_above_trend(self, price):
        if self.ema_value is None:
            return False
        return price > self.ema_value

    def _calculate_position_size(self, price):
        if price <= 0 or self.broker.cash <= 0:
            return 0.0
        risk_pct = getattr(config, 'RISK_PER_TRADE_PCT', 1.0)
        stop_loss_pct = abs(getattr(config, 'STOP_LOSS_PCT', -2.0))
        if stop_loss_pct <= 0:
            stop_loss_pct = 2.0
        risk_amount = self.broker.cash * (risk_pct / 100)
        stop_distance = price * (stop_loss_pct / 100)
        if stop_distance <= 0:
            return 0.0
        position_size = risk_amount / stop_distance
        max_affordable = self.broker.cash / price
        return min(position_size, max_affordable)

    def _check_stop_loss_take_profit(self, symbol, price):
        if not self.broker.has_position(symbol):
            return None
        entry = self.broker.position_entry(symbol)
        if entry <= 0:
            return None
        pnl_pct = ((price - entry) / entry) * 100
        if pnl_pct <= config.STOP_LOSS_PCT:
            return "STOP_LOSS"
        if pnl_pct >= config.TAKE_PROFIT_PCT:
            return "TAKE_PROFIT"
        return None

    def _validate_candles(self, candles):
        if not candles or not isinstance(candles, list) or len(candles) == 0:
            print("\n❌ ERROR: Invalid candles")
            sys.exit(1)
        required = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
        if not isinstance(candles[0], dict) or not required.issubset(candles[0].keys()):
            print("\n❌ ERROR: Invalid candle format")
            sys.exit(1)
        return True

    def run_backtest(self, strategy, candles, symbol):
        """Run LONG ONLY backtest."""
        self._validate_candles(candles)

        if strategy is None or not hasattr(strategy, 'on_candle'):
            print("\n❌ ERROR: Invalid strategy")
            sys.exit(1)

        # Initialize
        self.broker = PaperBroker(initial_cash=config.INITIAL_BALANCE)
        self.results = []
        self.equity_curve = []
        self.candles_since_last_sell = None
        self.ema_value = None
        self.last_buy_price = None

        history = []
        self._init_trade_log()
        self._init_equity_log()

        self._log(f"\n{'='*50}")
        self._log(f"BACKTEST - {symbol} - LONG ONLY")
        self._log(f"{'='*50}")
        self._log(f"Candles: {len(candles)}")
        self._log(f"Balance: ${config.INITIAL_BALANCE:.2f}")
        self._log(f"{'='*50}\n")

        for i, candle in enumerate(candles):
            history.append(candle)
            price = candle.get("close", 0)
            if not isinstance(price, (int, float)) or price <= 0:
                continue

            timestamp = candle.get("timestamp", 0)

            # Update EMA
            if i > 0:
                self._update_ema(candles[i - 1].get("close", 0))

            # Record equity
            equity = self.broker.get_equity(price)
            self.equity_curve.append({"timestamp": timestamp, "equity": equity})
            self._log_equity(timestamp, equity)

            # Cooldown
            if self.candles_since_last_sell is not None:
                self.candles_since_last_sell += 1

            # Wait for minimum candles
            if i < self.MIN_CANDLES_BEFORE_TRADING:
                continue

            # Check SL/TP
            sl_tp = self._check_stop_loss_take_profit(symbol, price)
            if sl_tp:
                self._execute_sell(symbol, price, timestamp, sl_tp)
                continue

            # Get strategy signal
            try:
                signal = strategy.on_candle(history, self.broker, symbol)
            except Exception:
                signal = "HOLD"

            signal = str(signal).upper() if signal else "HOLD"

            # Execute signal with broker state checks
            if signal == "BUY":
                self._execute_buy(symbol, price, timestamp)
            elif signal == "SELL":
                self._execute_sell(symbol, price, timestamp, "STRATEGY")

        self._print_summary(symbol, candles)
        return self.results

    def _execute_buy(self, symbol, price, timestamp):
        """Execute BUY only if no position exists."""
        # CHECK: No position must exist
        if self.broker.has_position(symbol):
            return False

        if price <= 0:
            return False

        # Cooldown check
        cooldown = getattr(config, 'COOLDOWN_CANDLES', 6)
        if self.candles_since_last_sell is not None and self.candles_since_last_sell < cooldown:
            return False

        # Trend filter
        if not self._is_above_trend(price):
            return False

        if self.broker.cash <= 0:
            return False

        amount = self._calculate_position_size(price)
        if amount <= 0:
            return False

        # Execute BUY
        if self.broker.buy(symbol, amount, price):
            self.last_buy_price = price
            balance = self.broker.get_equity(price)

            self.results.append({
                "timestamp": timestamp,
                "action": "BUY",
                "symbol": symbol,
                "price": price,
                "size": amount,
                "pnl": 0,
                "balance": balance
            })

            self._log_trade(timestamp, "BUY", symbol, price, amount, 0, balance)
            return True

        return False

    def _execute_sell(self, symbol, price, timestamp, trigger):
        """Execute SELL only if position exists."""
        # CHECK: Position must exist
        if not self.broker.has_position(symbol):
            return False

        if price <= 0:
            return False

        amount = self.broker.position_amount(symbol)
        if amount <= 0:
            return False

        # Calculate PnL
        pnl = 0
        if self.last_buy_price and self.last_buy_price > 0:
            pnl = (price - self.last_buy_price) * amount

        # Execute SELL
        if self.broker.sell(symbol, amount, price):
            balance = self.broker.get_equity(price)

            self.results.append({
                "timestamp": timestamp,
                "action": "SELL",
                "trigger": trigger,
                "symbol": symbol,
                "price": price,
                "size": amount,
                "pnl": pnl,
                "balance": balance
            })

            self._log_trade(timestamp, "SELL", symbol, price, amount, pnl, balance)
            self.last_buy_price = None
            self.candles_since_last_sell = 0
            return True

        return False

    def _print_summary(self, symbol, candles):
        perf = self.evaluate_performance()
        sells = [r for r in self.results if r.get("action") == "SELL"]
        winners = sum(1 for s in sells if s.get("pnl", 0) > 0)
        win_rate = self._safe_divide(winners * 100, len(sells), 0)

        self._log(f"\n{'='*50}")
        self._log(f"SUMMARY - {symbol} - LONG ONLY")
        self._log(f"{'='*50}")
        self._log(f"Starting:  ${config.INITIAL_BALANCE:.2f}")
        self._log(f"Ending:    ${perf['ending_balance']:.2f}")
        self._log(f"PnL:       ${perf['pnl']:+.2f}")
        self._log(f"Return:    {self._safe_divide(perf['pnl'] * 100, config.INITIAL_BALANCE):+.2f}%")
        self._log(f"Trades:    {perf['num_trades']}")
        self._log(f"Win Rate:  {win_rate:.1f}%")
        self._log(f"{'='*50}\n")

    def evaluate_performance(self):
        if self.broker is None:
            return {"ending_balance": 0, "num_trades": 0, "pnl": 0}
        ending = self.equity_curve[-1]["equity"] if self.equity_curve else self.broker.cash
        return {
            "ending_balance": ending,
            "num_trades": len(self.results),
            "pnl": ending - config.INITIAL_BALANCE
        }