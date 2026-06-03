import pandas as pd
from .strategies import generate_signals_rsi, generate_signals_ma_crossover


class Backtester:
    def __init__(
        self,
        df: pd.DataFrame,
        strategy: str,
        stop_loss_pct: float,
        take_profit_pct: float,
        initial_capital: float = 10_000,
        strategy_params: dict = None,
    ):
        self.df = df.copy()
        self.strategy = strategy
        self.sl = stop_loss_pct / 100.0
        self.tp = take_profit_pct / 100.0
        self.initial_capital = initial_capital
        self.params = strategy_params or {}

    def _signals(self) -> pd.Series:
        if self.strategy == "RSI":
            return generate_signals_rsi(self.df, **self.params)
        if self.strategy == "MA Crossover":
            return generate_signals_ma_crossover(self.df, **self.params)
        raise ValueError(f"Unknown strategy: {self.strategy}")

    def run(self, progress_callback=None):
        df = self.df
        signals = self._signals()
        n = len(df)

        capital = self.initial_capital
        equity = []
        position = None
        trades = []

        for i in range(n):
            if progress_callback and i % max(1, n // 200) == 0:
                progress_callback(i / n * 100)

            row = df.iloc[i]
            sig = signals.iloc[i]
            date = df.index[i]

            # Check open position for SL / TP / signal exit
            if position is not None:
                exit_price = None
                exit_reason = None

                if row["low"] <= position["stop_loss"]:
                    exit_price = position["stop_loss"]
                    exit_reason = "Stop Loss"
                elif row["high"] >= position["take_profit"]:
                    exit_price = position["take_profit"]
                    exit_reason = "Take Profit"
                elif sig == -1:
                    exit_price = row["close"]
                    exit_reason = "Signal"

                if exit_price is not None:
                    ret = (exit_price - position["entry_price"]) / position["entry_price"]
                    pnl = capital * ret
                    capital += pnl
                    trades.append(
                        {
                            "entry_date": position["entry_date"],
                            "exit_date": date,
                            "entry_price": position["entry_price"],
                            "exit_price": exit_price,
                            "pnl": round(pnl, 2),
                            "pnl_pct": round(ret * 100, 4),
                            "exit_reason": exit_reason,
                            "win": pnl > 0,
                        }
                    )
                    position = None

            # Open a new long position
            if position is None and sig == 1:
                ep = row["close"]
                position = {
                    "entry_date": date,
                    "entry_price": ep,
                    "stop_loss": ep * (1 - self.sl),
                    "take_profit": ep * (1 + self.tp),
                }

            equity.append(capital)

        if progress_callback:
            progress_callback(100)

        equity_series = pd.Series(equity, index=df.index)
        return trades, equity_series
