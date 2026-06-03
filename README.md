# Backtest Report Generator

> **Professional algorithmic trading backtester with automated PDF report generation — built in pure Python.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=flat-square&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-11557C?style=flat-square)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2%2B-1C1C1E?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-34C759?style=flat-square)

---

## What This Project Does

This desktop application lets traders and analysts **backtest trading strategies on their own OHLCV data** and instantly receive a polished, print-ready PDF report — no coding required on their end.

Load a CSV → configure parameters → click **Run Backtest** → a professional PDF opens automatically.

---

## Screenshots

### Application — Apple-style Dark UI

```
┌─────────────────────────────────────────────────────────┐
│  Backtest           Strategy Analysis & Report Generator │
├─────────────────────────────────────────────────────────┤
│  DATA SOURCE                                             │
│  CSV File   btc_daily.csv · 1,500 rows      [Choose…]  │
├─────────────────────────────────────────────────────────┤
│  STRATEGY                                                │
│  [ RSI ]  [ MA Crossover ]                               │
│  RSI Period: 14   Oversold: 30   Overbought: 70          │
│                                                          │
│  RISK MANAGEMENT                                         │
│  Stop Loss %: 2.0   Take Profit %: 4.0   Capital: 10000  │
├─────────────────────────────────────────────────────────┤
│  OUTPUT LOG                                              │
│  ▌ [14:02:31]  Loaded btc_daily.csv (1,500 rows)        │
│  ▌ [14:02:31]  Date range 2020-01-01 to 2025-09-30      │
│  ▌ [14:02:32]  Backtest complete · 136 trades executed   │
│  ▌ [14:02:32]  Return +167.88%  Winrate 50.0%           │
│  ▌ [14:02:33]  Report saved → reports/backtest_...pdf   │
├─────────────────────────────────────────────────────────┤
│  ████████████████████████████████  100%                  │
│  ( Run Backtest )   Report saved ✓                       │
└─────────────────────────────────────────────────────────┘
```

### PDF Report — Page 1: Dashboard

```
╔══════════════════════════════════════════════════════════╗
║  BACKTEST REPORT                                         ║
║  MA Crossover               01 Jan 2020 – 30 Sep 2025   ║
║                                             +167.88%     ║
║                                     Final  $26,788.00   ║
╠══════════════════════════════════════════════════════════╣
║  PERFORMANCE METRICS                                     ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     ║
║  │ SHARPE RATIO │ │ MAX DRAWDOWN │ │   WIN RATE   │     ║
║  │    1.269     │ │   -11.07%    │ │    50.0%     │     ║
║  └──────────────┘ └──────────────┘ └──────────────┘     ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     ║
║  │ TOTAL TRADES │ │   AVG WIN    │ │PROFIT FACTOR │     ║
║  │     136      │ │   +2.45%     │ │    1.87      │     ║
║  └──────────────┘ └──────────────┘ └──────────────┘     ║
║                                                          ║
║  EQUITY CURVE                                            ║
║  $27k ┤                    ╭──────╮                      ║
║  $18k ┤          ╭────────╯      ╰──── $26,788          ║
║  $10k ┤ ─ ─ ─ ─ ╯  (start)                              ║
║       └──────────────────────────────────────────        ║
║  DRAWDOWN                                                ║
║      ┤▓▓▓▓▓▓▓▓▓▓▓  max: -11.07%                         ║
╚══════════════════════════════════════════════════════════╝
```

---

## Features

### Core Engine
- **Bar-by-bar backtesting** using pandas — no external backtesting libraries
- **Stop Loss** and **Take Profit** hit-testing against intrabar high/low (realistic fills)
- **Two strategies out of the box:**
  - RSI — configurable period, oversold & overbought levels
  - Moving Average Crossover — configurable fast & slow windows
- Clean architecture — adding a new strategy takes ~10 lines of code

### Performance Metrics
| Metric | Description |
|---|---|
| Total Return | `(final − initial) / initial × 100` |
| Sharpe Ratio | Annualised `(mean_ret / std_ret) × √252` |
| Max Drawdown | Peak-to-trough equity decline |
| Win Rate | % of profitable trades |
| Avg Win / Avg Loss | Mean P&L % per winning / losing trade |
| Profit Factor | Gross profit ÷ gross loss |

### Desktop GUI (CustomTkinter)
- **Apple-style dark mode** — `#1C1C1E` background, card layout, pill buttons
- Segmented button for strategy switching with dynamic parameter rows
- Non-blocking UI — backtest runs in a **background thread**
- Real-time log with timestamped messages
- `queue.Queue` for safe thread → GUI communication
- Smooth 3 px progress bar

### PDF Report (Matplotlib)
- **A4 landscape** — print-ready at 180 dpi
- Page 1: dark header band, 6 metric cards, equity curve, drawdown chart
- Page 2+: trade-by-trade list with green/red P&L highlights
- Equity curve styled after Apple Stocks — blue fill above start, red below
- Auto-opens after generation

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| GUI | CustomTkinter | Modern-looking Tk widgets, zero install friction |
| Data | Pandas + NumPy | Industry-standard, fast vectorised operations |
| Charting | Matplotlib (Agg backend) | Thread-safe PDF rendering, full layout control |
| PDF | `matplotlib.backends.backend_pdf.PdfPages` | No additional dependency (reportlab-free) |
| Threading | `threading` + `queue.Queue` | Keeps UI responsive during long backtests |

---

## Project Structure

```
backtest-report-generator/
│
├── main.py                     ← entry point
├── requirements.txt
├── generate_sample_data.py     ← generate test OHLCV CSV
│
├── backend/
│   ├── strategies.py           ← signal generators (RSI, MA Crossover)
│   ├── backtester.py           ← bar-by-bar engine with SL/TP logic
│   ├── metrics.py              ← performance metric calculations
│   └── report_generator.py    ← multi-page PDF builder
│
├── ui/
│   └── app.py                  ← CustomTkinter dark-mode application
│
└── reports/                    ← generated PDFs land here
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate sample data (optional)
python generate_sample_data.py

# 3. Launch the app
python main.py
```

**requirements.txt**
```
customtkinter>=5.2.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
```

---

## CSV Format

The app accepts any CSV with these columns (case-insensitive):

| Column | Type | Description |
|---|---|---|
| `date` | string / datetime | Row timestamp |
| `open` | float | Opening price |
| `high` | float | Intrabar high |
| `low` | float | Intrabar low |
| `close` | float | Closing price |
| `volume` | int | Volume |

Works with data from Yahoo Finance, Binance, MetaTrader, TradingView exports, and any other standard OHLCV source.

---

## Extending the Project

The codebase is intentionally modular. Common extension requests:

| Extension | Where to touch |
|---|---|
| New strategy (MACD, Bollinger, etc.) | Add one function in `backend/strategies.py` |
| Additional metrics (Calmar, Sortino) | Add to `backend/metrics.py` |
| New PDF pages (monthly heatmap, etc.) | Add `_page_*` function in `backend/report_generator.py` |
| Portfolio / multi-asset mode | Extend `backend/backtester.py` |
| Dark-mode PDF | Swap `C["bg"]` from `#FFFFFF` to `#1C1C1E` |

---

## What I Can Build For You

This project demonstrates my ability to deliver **complete, production-quality Python applications** — from data processing logic to professional UI and automated document output.

If you need any of the following, let's talk:

- **Custom trading tools** — backtester, screener, live signal dashboard
- **Data analysis desktop apps** — load CSVs, run calculations, export PDF/Excel
- **Automated report generation** — scheduled or on-demand PDF/Word output
- **Python GUI applications** — CustomTkinter, PyQt, or web-based (Streamlit/Dash)
- **Financial data pipelines** — pandas, yfinance, ccxt, Alpaca, Interactive Brokers API

I write **clean, well-structured code** that you can read, maintain, and extend — not spaghetti that only works on my machine.

---

## About This Code

- Zero third-party backtesting frameworks — the engine is written from scratch so every assumption is visible and modifiable
- Type hints throughout for IDE support and code clarity
- Background threading with queue-based messaging — no frozen UI, no race conditions
- Each module has a single responsibility — strategies, backtester, metrics, and report generator are fully decoupled

---

## License

MIT — free to use, modify, and distribute.

---

*Built with Python · Pandas · Matplotlib · CustomTkinter*
