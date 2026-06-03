import pandas as pd
import numpy as np


def _rsi(prices: pd.Series, period: int) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, adjust=True, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=True, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def generate_signals_rsi(
    df: pd.DataFrame,
    period: int = 14,
    oversold: int = 30,
    overbought: int = 70,
) -> pd.Series:
    """1 = buy zone (RSI < oversold), -1 = sell zone (RSI > overbought), 0 = neutral."""
    rsi = _rsi(df["close"], period)
    signal = pd.Series(0, index=df.index, dtype=int)
    signal[rsi < oversold] = 1
    signal[rsi > overbought] = -1
    return signal


def generate_signals_ma_crossover(
    df: pd.DataFrame,
    fast: int = 10,
    slow: int = 30,
) -> pd.Series:
    """1 = fast above slow (bullish), -1 = fast below slow (bearish)."""
    fast_ma = df["close"].rolling(window=fast).mean()
    slow_ma = df["close"].rolling(window=slow).mean()
    signal = pd.Series(0, index=df.index, dtype=int)
    signal[fast_ma > slow_ma] = 1
    signal[fast_ma < slow_ma] = -1
    return signal
