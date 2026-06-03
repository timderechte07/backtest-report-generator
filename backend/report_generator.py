import matplotlib
matplotlib.use("Agg")  # thread-safe, no GUI window

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from datetime import datetime

# ── Apple Design System ───────────────────────────────────────────────────────
C = {
    "bg":      "#FFFFFF",
    "header":  "#1C1C1E",   # systemBackground dark
    "card":    "#F2F2F7",   # secondarySystemBackground
    "card2":   "#E5E5EA",   # tertiarySystemBackground
    "blue":    "#007AFF",
    "green":   "#34C759",
    "red":     "#FF3B30",
    "orange":  "#FF9F0A",
    "purple":  "#AF52DE",
    "gray1":   "#8E8E93",   # secondaryLabel
    "gray2":   "#C7C7CC",   # separator
    "gray3":   "#E5E5EA",   # light separator
    "label1":  "#1C1C1E",
    "label2":  "#3C3C43",
}

plt.rcParams.update({
    "font.family":         ["Segoe UI", "Arial", "Calibri", "DejaVu Sans"],
    "axes.spines.top":     False,
    "axes.spines.right":   False,
    "axes.spines.left":    False,
    "axes.spines.bottom":  False,
    "xtick.bottom":        False,
    "ytick.left":          False,
})


# ── Public API ────────────────────────────────────────────────────────────────

def generate_report(
    trades: list,
    equity_series: pd.Series,
    metrics: dict,
    strategy_name: str,
    output_path: str,
) -> None:
    with PdfPages(output_path) as pdf:
        _page_dashboard(pdf, equity_series, metrics, strategy_name)
        if trades:
            _page_trades(pdf, trades, strategy_name, metrics)

        d = pdf.infodict()
        d["Title"]        = f"Backtest Report — {strategy_name}"
        d["Author"]       = "Backtest Report Generator"
        d["CreationDate"] = datetime.now()


# ── Page 1: Dashboard ─────────────────────────────────────────────────────────

def _page_dashboard(pdf, equity_series, metrics, strategy_name):
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.patch.set_facecolor(C["bg"])

    _header(fig, strategy_name, equity_series, metrics)
    _metric_row(fig, metrics)
    _equity_chart(fig, equity_series)
    _drawdown_chart(fig, equity_series)

    pdf.savefig(fig, bbox_inches="tight", dpi=180)
    plt.close(fig)


# ── Header band ───────────────────────────────────────────────────────────────

def _header(fig, strategy_name, equity_series, metrics):
    H_BOTTOM = 0.838
    H_HEIGHT = 0.162

    # Dark background
    _fig_rect(fig, 0, H_BOTTOM, 1, H_HEIGHT, C["header"], zorder=1)

    # Subtle accent line at bottom of header
    _fig_rect(fig, 0, H_BOTTOM, 1, 0.003, C["blue"], zorder=2)

    # Left: labels
    fig.text(0.040, 0.967, "BACKTEST REPORT",
             transform=fig.transFigure, fontsize=8,
             color=C["gray1"], fontweight="700", va="center",
             zorder=10, style="normal")

    fig.text(0.040, 0.930, strategy_name,
             transform=fig.transFigure, fontsize=22,
             color="#FFFFFF", fontweight="bold", va="center", zorder=10)

    if hasattr(equity_series.index[0], "strftime"):
        date_str = (f"{equity_series.index[0].strftime('%d %b %Y')}"
                    f"  –  {equity_series.index[-1].strftime('%d %b %Y')}")
    else:
        date_str = f"{len(equity_series):,} bars"

    fig.text(0.040, 0.867, date_str,
             transform=fig.transFigure, fontsize=9,
             color="#636366", va="center", zorder=10)

    # Right: total return (big hero number)
    ret = metrics["total_return"]
    ret_color = C["green"] if ret >= 0 else C["red"]

    fig.text(0.960, 0.940, f"{ret:+.2f}%",
             transform=fig.transFigure, fontsize=30,
             color=ret_color, fontweight="bold",
             va="center", ha="right", zorder=10)

    fig.text(0.960, 0.867, f"Final  ${metrics['final_equity']:>10,.2f}",
             transform=fig.transFigure, fontsize=9,
             color="#636366", va="center", ha="right", zorder=10)


# ── Metric cards ──────────────────────────────────────────────────────────────

def _metric_row(fig, m):
    pf = m["profit_factor"]
    pf_str = f"{pf:.2f}" if pf < 999 else "∞"

    wr_color  = C["green"] if m["winrate"] >= 50   else C["red"]
    sh_color  = C["blue"]  if m["sharpe_ratio"] > 0 else C["red"]

    CARDS = [
        # label,          value,                          accent color
        ("SHARPE RATIO",  f"{m['sharpe_ratio']:.3f}",     sh_color),
        ("MAX DRAWDOWN",  f"{m['max_drawdown']:.2f}%",    C["red"]),
        ("WIN RATE",      f"{m['winrate']:.1f}%",         wr_color),
        ("TOTAL TRADES",  str(m["total_trades"]),          C["orange"]),
        ("AVG WIN",       f"{m['avg_win']:+.2f}%",        C["green"]),
        ("PROFIT FACTOR", pf_str,                         C["purple"]),
    ]

    xs = [0.040, 0.360, 0.680]   # card x-positions (3 per row)
    W  = 0.285                   # card width

    # Row 1
    Y1, H1 = 0.670, 0.148
    for i in range(3):
        label, value, color = CARDS[i]
        _draw_card(fig, xs[i], Y1, W, H1, label, value, color)

    # Row 2
    Y2, H2 = 0.510, 0.142
    for i in range(3):
        label, value, color = CARDS[i + 3]
        _draw_card(fig, xs[i], Y2, W, H2, label, value, color)

    # Section label above cards
    fig.text(0.040, 0.833, "PERFORMANCE METRICS",
             transform=fig.transFigure, fontsize=7,
             color=C["gray1"], fontweight="700", va="center", zorder=10)


def _draw_card(fig, x, y, w, h, label, value, accent_color):
    # Card background (rounded)
    _fig_fancy_rect(fig, x, y, w, h, C["card"], radius=0.012, zorder=3)

    # Left accent bar
    _fig_fancy_rect(fig, x, y + h * 0.15, 0.0045, h * 0.70, accent_color,
                    radius=0.003, zorder=4)

    # Label
    fig.text(x + 0.018, y + h * 0.68, label,
             transform=fig.transFigure, fontsize=7,
             color=C["gray1"], fontweight="700", va="center", zorder=5)

    # Value (large, bold)
    fig.text(x + 0.018, y + h * 0.30, value,
             transform=fig.transFigure, fontsize=19,
             color=C["label1"], fontweight="bold", va="center", zorder=5)


# ── Equity chart ──────────────────────────────────────────────────────────────

def _equity_chart(fig, equity_series):
    ax = fig.add_axes([0.055, 0.277, 0.900, 0.218])
    ax.set_facecolor(C["bg"])
    _clean_ax(ax)

    initial   = equity_series.iloc[0]
    final     = equity_series.iloc[-1]
    line_c    = C["blue"] if final >= initial else C["red"]

    xs = equity_series.index
    ys = equity_series.values

    # Fill: blue above start, red below start
    ax.fill_between(xs, ys, initial,
                    where=(ys >= initial),
                    color=C["blue"], alpha=0.10, linewidth=0, zorder=2)
    ax.fill_between(xs, ys, initial,
                    where=(ys < initial),
                    color=C["red"], alpha=0.10, linewidth=0, zorder=2)

    # Base line (initial capital)
    ax.axhline(initial, color=C["gray2"], linewidth=0.6,
               linestyle=(0, (6, 4)), zorder=1, alpha=0.8)

    # Main equity line
    ax.plot(xs, ys, color=line_c, linewidth=2.2,
            solid_capstyle="round", zorder=4)

    # End-point dot + label
    ax.scatter([xs[-1]], [final], color=line_c, s=45, zorder=6)
    ax.annotate(f"  ${final:,.0f}",
                xy=(xs[-1], final), xytext=(4, 0),
                textcoords="offset points", fontsize=8.5,
                color=line_c, fontweight="bold", va="center")

    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.tick_params(axis="y", labelsize=7.5, labelcolor=C["gray1"], pad=4)
    ax.tick_params(axis="x", labelsize=7.5, labelcolor=C["gray1"], pad=4)
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)

    # Subtle horizontal grid
    ax.yaxis.grid(True, color=C["gray3"], linewidth=0.4, linestyle="-", zorder=0)
    ax.set_axisbelow(True)

    fig.text(0.055, 0.503, "EQUITY CURVE",
             transform=fig.transFigure, fontsize=7,
             color=C["gray1"], fontweight="700", va="center")


# ── Drawdown chart ────────────────────────────────────────────────────────────

def _drawdown_chart(fig, equity_series):
    ax = fig.add_axes([0.055, 0.042, 0.900, 0.200])
    ax.set_facecolor(C["bg"])
    _clean_ax(ax)

    peak = equity_series.cummax()
    dd   = (equity_series - peak) / peak * 100

    ax.fill_between(dd.index, dd.values, 0,
                    color=C["red"], alpha=0.20, linewidth=0, zorder=2)
    ax.plot(dd.index, dd.values,
            color=C["red"], linewidth=1.6, solid_capstyle="round", zorder=3)
    ax.axhline(0, color=C["gray2"], linewidth=0.5, zorder=1)

    # Max drawdown marker
    min_idx = dd.idxmin()
    min_val = dd.min()
    ax.scatter([min_idx], [min_val], color=C["red"], s=30, zorder=5)
    ax.annotate(f"  {min_val:.1f}%",
                xy=(min_idx, min_val), xytext=(4, -2),
                textcoords="offset points", fontsize=8,
                color=C["red"], fontweight="bold", va="top")

    ax.tick_params(axis="y", labelsize=7.5, labelcolor=C["gray1"], pad=4)
    ax.tick_params(axis="x", labelsize=7.5, labelcolor=C["gray1"], pad=4)
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)
    ax.yaxis.grid(True, color=C["gray3"], linewidth=0.4, linestyle="-", zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylabel("")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))

    fig.text(0.055, 0.250, "DRAWDOWN",
             transform=fig.transFigure, fontsize=7,
             color=C["gray1"], fontweight="700", va="center")


# ── Trade list pages ──────────────────────────────────────────────────────────

def _page_trades(pdf, trades, strategy_name, metrics):
    df = pd.DataFrame(trades)
    for col in ("entry_date", "exit_date"):
        try:
            df[col] = pd.to_datetime(df[col]).dt.strftime("%d %b %Y")
        except Exception:
            df[col] = df[col].astype(str)

    cols    = ["entry_date", "exit_date", "entry_price", "exit_price",
               "pnl", "pnl_pct", "exit_reason"]
    headers = ["Entry Date", "Exit Date", "Entry $", "Exit $",
               "P&L $", "P&L %", "Reason"]

    ROWS_PP  = 28
    total_pg = max(1, (len(df) - 1) // ROWS_PP + 1)

    for start in range(0, len(df), ROWS_PP):
        chunk = df.iloc[start: start + ROWS_PP]
        page  = start // ROWS_PP + 1

        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor(C["bg"])

        # Header
        _fig_rect(fig, 0, 0.870, 1, 0.130, C["header"], zorder=1)
        _fig_rect(fig, 0, 0.870, 1, 0.003, C["blue"],   zorder=2)

        fig.text(0.040, 0.960, "TRADE HISTORY",
                 transform=fig.transFigure, fontsize=8,
                 color=C["gray1"], fontweight="700", zorder=10)
        fig.text(0.040, 0.921, strategy_name,
                 transform=fig.transFigure, fontsize=20,
                 color="#FFFFFF", fontweight="bold", zorder=10)

        wins_pct = metrics["winrate"]
        fig.text(0.960, 0.935,
                 f"{len(df)} trades   ·   {wins_pct:.1f}% win rate",
                 transform=fig.transFigure, fontsize=9,
                 color=C["gray1"], ha="right", zorder=10)
        fig.text(0.960, 0.900,
                 f"Page {page} of {total_pg}",
                 transform=fig.transFigure, fontsize=8,
                 color="#636366", ha="right", zorder=10)

        # Table
        ax = fig.add_axes([0.025, 0.025, 0.950, 0.825])
        ax.set_facecolor(C["bg"])
        ax.axis("off")

        cell_data = []
        for _, row in chunk.iterrows():
            cell_data.append([
                row["entry_date"],
                row["exit_date"],
                f"{row['entry_price']:.4f}",
                f"{row['exit_price']:.4f}",
                f"{row['pnl']:+,.2f}",
                f"{row['pnl_pct']:+.3f}%",
                row["exit_reason"],
            ])

        table = ax.table(
            cellText=cell_data,
            colLabels=headers,
            loc="upper center",
            cellLoc="center",
            bbox=[0, 0, 1, 1],
        )
        _style_table(table, chunk)

        pdf.savefig(fig, bbox_inches="tight", dpi=180)
        plt.close(fig)


def _style_table(table, chunk):
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 1.55)

    n_cols = 7
    col_widths = [0.16, 0.16, 0.12, 0.12, 0.12, 0.12, 0.12]

    for (r, c), cell in table.get_celld().items():
        cell.set_linewidth(0)
        cell.PAD = 0.06

        if r == 0:
            cell.set_facecolor(C["label1"])
            cell.set_text_props(color="#FFFFFF", fontweight="700", fontsize=8)
            if c == 0:
                cell.set_facecolor(C["label1"])
        else:
            row_obj  = chunk.iloc[r - 1]
            is_win   = row_obj["pnl"] > 0
            row_base = "#FAFAFA" if r % 2 == 0 else "#FFFFFF"

            if c in (4, 5):
                cell.set_facecolor("#EAF6EC" if is_win else "#FEECEB")
                cell.set_text_props(
                    color=C["green"] if is_win else C["red"],
                    fontweight="600", fontsize=8.5,
                )
            elif c == 6:
                reason = row_obj["exit_reason"]
                bg = {"Stop Loss": "#FEECEB",
                      "Take Profit": "#EAF6EC"}.get(reason, row_base)
                tc = {"Stop Loss": C["red"],
                      "Take Profit": C["green"]}.get(reason, C["label2"])
                cell.set_facecolor(bg)
                cell.set_text_props(color=tc, fontsize=8.5)
            else:
                cell.set_facecolor(row_base)
                cell.set_text_props(color=C["label1"], fontsize=8.5)


# ── Drawing helpers ───────────────────────────────────────────────────────────

def _fig_rect(fig, x, y, w, h, color, zorder=1):
    """Simple rectangle at figure coordinates."""
    p = mpatches.Rectangle(
        (x, y), w, h,
        facecolor=color, edgecolor="none", linewidth=0,
        transform=fig.transFigure, zorder=zorder, clip_on=False,
    )
    fig.patches.append(p)


def _fig_fancy_rect(fig, x, y, w, h, color, radius=0.01, zorder=1):
    """Rounded rectangle at figure coordinates."""
    p = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, edgecolor="none", linewidth=0,
        transform=fig.transFigure, zorder=zorder, clip_on=False,
    )
    fig.patches.append(p)


def _clean_ax(ax):
    for spine in ax.spines.values():
        spine.set_visible(False)
