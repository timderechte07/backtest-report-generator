"""Run this script once to generate a sample OHLCV CSV for testing."""
import os
import numpy as np
import pandas as pd

np.random.seed(42)

N = 1500
dates = pd.date_range(start="2020-01-01", periods=N, freq="B")  # business days

# Simulate a realistic price series via geometric Brownian motion
returns = np.random.normal(0.0003, 0.012, N)
close = 100.0 * np.exp(np.cumsum(returns))
spread = np.abs(np.random.normal(0, 0.004, N))
high = close * (1 + spread)
low  = close * (1 - spread)
open_ = np.roll(close, 1)
open_[0] = close[0]
volume = np.random.randint(500_000, 8_000_000, N)

df = pd.DataFrame(
    {
        "date":   dates,
        "open":   open_.round(4),
        "high":   high.round(4),
        "low":    low.round(4),
        "close":  close.round(4),
        "volume": volume,
    }
)

os.makedirs("sample_data", exist_ok=True)
out = os.path.join("sample_data", "sample_ohlcv.csv")
df.to_csv(out, index=False)
print(f"Generated {out}  ({N} rows, {dates[0].date()} to {dates[-1].date()})")
