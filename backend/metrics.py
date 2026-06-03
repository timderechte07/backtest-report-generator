import numpy as np
import pandas as pd


def calculate_metrics(
    trades: list,
    equity_series: pd.Series,
    initial_capital: float,
) -> dict:
    final_equity = equity_series.iloc[-1]
    total_return = (final_equity - initial_capital) / initial_capital * 100

    peak = equity_series.cummax()
    drawdown = (equity_series - peak) / peak * 100
    max_drawdown = drawdown.min()

    daily_returns = equity_series.pct_change().dropna()
    sharpe = (
        (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        if daily_returns.std() > 0
        else 0.0
    )

    base = {
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe,
        "final_equity": final_equity,
        "total_trades": 0,
        "winrate": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "profit_factor": 0.0,
    }

    if not trades:
        return base

    df_t = pd.DataFrame(trades)
    wins = df_t[df_t["pnl"] > 0]
    losses = df_t[df_t["pnl"] <= 0]

    gross_profit = wins["pnl"].sum() if len(wins) > 0 else 0.0
    gross_loss = abs(losses["pnl"].sum()) if len(losses) > 0 else 1e-9

    base.update(
        {
            "total_trades": len(df_t),
            "winrate": len(wins) / len(df_t) * 100,
            "avg_win": wins["pnl_pct"].mean() if len(wins) > 0 else 0.0,
            "avg_loss": losses["pnl_pct"].mean() if len(losses) > 0 else 0.0,
            "profit_factor": gross_profit / gross_loss,
        }
    )
    return base
