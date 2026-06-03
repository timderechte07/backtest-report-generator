import os
import sys
import queue
import threading
from datetime import datetime

import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.backtester import Backtester
from backend.metrics import calculate_metrics
from backend.report_generator import generate_report

# ── Apple Dark Design System ──────────────────────────────────────────────────
_BG     = "#1C1C1E"   # systemBackground
_CARD   = "#2C2C2E"   # secondarySystemBackground
_CARD2  = "#3A3A3C"   # tertiarySystemBackground
_SEP    = "#38383A"   # separator
_BLUE   = "#0A84FF"   # systemBlue (dark)
_GREEN  = "#30D158"   # systemGreen (dark)
_RED    = "#FF453A"   # systemRed (dark)
_LBL1   = "#FFFFFF"   # primary label
_LBL2   = "#EBEBF5"   # secondary label (96% white)
_LBL3   = "#8E8E93"   # tertiary label
_LBL4   = "#636366"   # quaternary label

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BacktestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color=_BG)
        self.title("Backtest")
        self.geometry("840x800")
        self.minsize(780, 700)

        self.df  = None
        self.q   = queue.Queue()

        self._build()
        self._poll()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._section_header()
        self._data_card()
        self._config_card()
        self._log_card()
        self._bottom_bar()

    # ── Sections ──────────────────────────────────────────────────────────────

    def _section_header(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=0, column=0, padx=32, pady=(26, 4), sticky="ew")

        ctk.CTkLabel(
            f, text="Backtest",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=_LBL1, anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            f, text="Strategy Analysis & Report Generator",
            font=ctk.CTkFont(size=12),
            text_color=_LBL3, anchor="w",
        ).pack(side="left", padx=(14, 0), pady=(6, 0))

    def _data_card(self):
        card = self._card(row=1, pady=(10, 4))

        _label_caps(card, "DATA SOURCE")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", pady=(6, 2))
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text="CSV File", text_color=_LBL1,
                      font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 16))

        self.file_label = ctk.CTkLabel(
            row, text="No file selected  ·  columns: date, open, high, low, close, volume",
            text_color=_LBL4, font=ctk.CTkFont(size=12), anchor="w",
        )
        self.file_label.grid(row=0, column=1, sticky="w")

        ctk.CTkButton(
            row, text="Choose…", command=self._load_csv,
            width=100, height=30, corner_radius=7,
            fg_color=_CARD2, hover_color="#4A4A4E",
            text_color=_LBL2, font=ctk.CTkFont(size=12),
        ).grid(row=0, column=2, padx=(12, 0))

    def _config_card(self):
        card = self._card(row=2, pady=(4, 4))

        # ── Strategy ──
        _label_caps(card, "STRATEGY")

        strat_row = ctk.CTkFrame(card, fg_color="transparent")
        strat_row.pack(fill="x", pady=(6, 12))

        self.strategy_var = ctk.StringVar(value="RSI")
        self.seg = ctk.CTkSegmentedButton(
            strat_row,
            values=["RSI", "MA Crossover"],
            variable=self.strategy_var,
            command=self._on_strat,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=_CARD2,
            selected_color=_BLUE,
            selected_hover_color="#0070E0",
            unselected_color=_CARD2,
            unselected_hover_color="#4A4A4E",
            text_color=_LBL1,
            height=36, corner_radius=9,
        )
        self.seg.pack(side="left")

        # Dynamic param container
        self.param_box = ctk.CTkFrame(card, fg_color="transparent")
        self.param_box.pack(fill="x", pady=(0, 4))

        self._build_rsi_params()
        self._build_ma_params()
        self._show_strat("RSI")

        # ── Divider ──
        ctk.CTkFrame(card, fg_color=_SEP, height=1).pack(
            fill="x", pady=(10, 12)
        )

        # ── Risk Management ──
        _label_caps(card, "RISK MANAGEMENT")

        risk_row = ctk.CTkFrame(card, fg_color="transparent")
        risk_row.pack(fill="x", pady=(6, 2))

        risk_fields = [
            ("Stop Loss %",       "sl_entry",  "2.0",   90),
            ("Take Profit %",     "tp_entry",  "4.0",   90),
            ("Initial Capital $", "cap_entry", "10000", 120),
        ]
        for label, attr, default, w in risk_fields:
            grp = ctk.CTkFrame(risk_row, fg_color="transparent")
            grp.pack(side="left", padx=(0, 28))
            ctk.CTkLabel(grp, text=label, text_color=_LBL3,
                          font=ctk.CTkFont(size=11)).pack(anchor="w")
            e = self._entry(grp, default, width=w)
            e.pack(anchor="w", pady=(4, 0))
            setattr(self, attr, e)

    def _build_rsi_params(self):
        self.rsi_frame = ctk.CTkFrame(self.param_box, fg_color="transparent")
        fields = [
            ("RSI Period", "rsi_period",    "14"),
            ("Oversold",   "rsi_oversold",  "30"),
            ("Overbought", "rsi_overbought","70"),
        ]
        for label, attr, default in fields:
            grp = ctk.CTkFrame(self.rsi_frame, fg_color="transparent")
            grp.pack(side="left", padx=(0, 24))
            ctk.CTkLabel(grp, text=label, text_color=_LBL3,
                          font=ctk.CTkFont(size=11)).pack(anchor="w")
            e = self._entry(grp, default)
            e.pack(anchor="w", pady=(4, 0))
            setattr(self, attr, e)

    def _build_ma_params(self):
        self.ma_frame = ctk.CTkFrame(self.param_box, fg_color="transparent")
        for label, attr, default in [("Fast MA", "ma_fast", "10"),
                                      ("Slow MA", "ma_slow", "30")]:
            grp = ctk.CTkFrame(self.ma_frame, fg_color="transparent")
            grp.pack(side="left", padx=(0, 24))
            ctk.CTkLabel(grp, text=label, text_color=_LBL3,
                          font=ctk.CTkFont(size=11)).pack(anchor="w")
            e = self._entry(grp, default)
            e.pack(anchor="w", pady=(4, 0))
            setattr(self, attr, e)

    def _show_strat(self, strat):
        for w in self.param_box.winfo_children():
            w.pack_forget()
        (self.rsi_frame if strat == "RSI" else self.ma_frame).pack(fill="x")

    def _log_card(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.grid(row=3, column=0, padx=32, pady=(4, 4), sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        _label_caps(hdr, "OUTPUT LOG", pack_side="left")

        terminal = ctk.CTkFrame(
            outer, fg_color="#111111",
            corner_radius=12, border_width=1, border_color=_SEP,
        )
        terminal.grid(row=1, column=0, sticky="nsew")
        terminal.grid_rowconfigure(0, weight=1)
        terminal.grid_columnconfigure(0, weight=1)

        self.log_box = ctk.CTkTextbox(
            terminal,
            font=ctk.CTkFont(family="Courier New", size=11),
            fg_color="transparent",
            text_color="#3DCC70",     # terminal green
            state="disabled",
            wrap="word",
            scrollbar_button_color=_SEP,
            scrollbar_button_hover_color=_CARD2,
        )
        self.log_box.grid(row=0, column=0, padx=16, pady=12, sticky="nsew")

    def _bottom_bar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=4, column=0, padx=32, pady=(6, 24), sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        # Progress bar (thin, Apple-like)
        self.progress = ctk.CTkProgressBar(
            bar, height=3, corner_radius=2,
            fg_color=_SEP, progress_color=_BLUE,
        )
        self.progress.grid(row=0, column=0, columnspan=3,
                           sticky="ew", pady=(0, 12))
        self.progress.set(0)

        self.run_btn = ctk.CTkButton(
            bar, text="Run Backtest",
            command=self._on_run,
            width=176, height=48, corner_radius=24,
            fg_color=_BLUE, hover_color="#0070E0",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.run_btn.grid(row=1, column=0)

        self.status = ctk.CTkLabel(
            bar, text="Ready",
            text_color=_LBL4, font=ctk.CTkFont(size=12), anchor="w",
        )
        self.status.grid(row=1, column=1, padx=18, sticky="w")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _card(self, row, pady=(6, 6)):
        outer = ctk.CTkFrame(
            self, fg_color=_CARD, corner_radius=12,
            border_width=1, border_color=_SEP,
        )
        outer.grid(row=row, column=0, padx=32, pady=pady, sticky="ew")
        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="x", padx=22, pady=16)
        return inner

    def _entry(self, parent, default, width=90):
        e = ctk.CTkEntry(
            parent, width=width, height=36, corner_radius=8,
            fg_color=_CARD2, border_color=_SEP, border_width=1,
            text_color=_LBL1, font=ctk.CTkFont(size=13),
        )
        e.insert(0, default)
        return e

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}]  {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _on_strat(self, choice):
        self._show_strat(choice)

    # ── CSV loading ───────────────────────────────────────────────────────────

    def _load_csv(self):
        path = filedialog.askopenfilename(
            title="Select OHLCV CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            df = pd.read_csv(path)
            df.columns = df.columns.str.lower().str.strip()

            required = {"open", "high", "low", "close", "volume"}
            missing  = required - set(df.columns)
            if missing:
                messagebox.showerror(
                    "Invalid CSV",
                    f"Missing columns: {', '.join(sorted(missing))}\n"
                    f"Found: {', '.join(df.columns)}",
                )
                return

            date_col = next(
                (c for c in df.columns
                 if c in ("date", "datetime", "time", "timestamp")), None
            )
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col])
                df = df.set_index(date_col).sort_index()
            else:
                df = df.reset_index(drop=True)

            self.df = df
            name = os.path.basename(path)
            self.file_label.configure(
                text=f"{name}  ·  {len(df):,} rows",
                text_color=_LBL2,
            )
            self._log(f"Loaded  {name}  ({len(df):,} rows)")
            if hasattr(df.index, "date"):
                self._log(
                    f"Date range  {df.index[0].date()}  to  {df.index[-1].date()}"
                )
        except Exception as exc:
            messagebox.showerror("Load Error", str(exc))

    # ── Run backtest ──────────────────────────────────────────────────────────

    def _on_run(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please select a CSV file first.")
            return
        try:
            sl      = float(self.sl_entry.get())
            tp      = float(self.tp_entry.get())
            capital = float(self.cap_entry.get())
            strat   = self.strategy_var.get()
            if strat == "RSI":
                params = {
                    "period":     int(self.rsi_period.get()),
                    "oversold":   int(self.rsi_oversold.get()),
                    "overbought": int(self.rsi_overbought.get()),
                }
            else:
                params = {
                    "fast": int(self.ma_fast.get()),
                    "slow": int(self.ma_slow.get()),
                }
        except ValueError:
            messagebox.showerror("Invalid Input",
                                  "All parameter fields must contain valid numbers.")
            return

        self.run_btn.configure(state="disabled", text="Running…")
        self.status.configure(text="Calculating…", text_color=_BLUE)
        self.progress.set(0)

        threading.Thread(
            target=self._worker,
            args=(strat, sl, tp, capital, params),
            daemon=True,
        ).start()

    def _worker(self, strat, sl, tp, capital, params):
        log  = lambda m: self.q.put(("log", m))
        prog = lambda p: self.q.put(("progress", p / 100))

        try:
            log(f"Strategy  {strat}  ·  SL {sl}%  ·  TP {tp}%  ·  Capital ${capital:,.0f}")
            log(f"Parameters  {params}")

            bt = Backtester(self.df, strat, sl, tp, capital, params)
            trades, equity = bt.run(progress_callback=prog)
            log(f"Backtest complete  ·  {len(trades)} trades executed")

            m = calculate_metrics(trades, equity, capital)
            log(
                f"Return {m['total_return']:+.2f}%   "
                f"Winrate {m['winrate']:.1f}%   "
                f"Sharpe {m['sharpe_ratio']:.3f}   "
                f"MaxDD {m['max_drawdown']:.2f}%"
            )

            os.makedirs("reports", exist_ok=True)
            ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
            out = os.path.join(
                "reports", f"backtest_{strat.replace(' ', '_')}_{ts}.pdf"
            )

            log("Generating PDF report…")
            generate_report(trades, equity, m, strat, out)
            log(f"Saved  {out}")

            self.q.put(("done", out))

        except Exception as exc:
            import traceback
            self.q.put(("error", f"{exc}\n\n{traceback.format_exc()}"))

    # ── Queue polling ─────────────────────────────────────────────────────────

    def _poll(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "progress":
                    self.progress.set(data)
                elif kind == "log":
                    self._log(data)
                elif kind == "done":
                    self.run_btn.configure(state="normal", text="Run Backtest")
                    self.status.configure(text="Report saved  ✓", text_color=_GREEN)
                    self.progress.set(1.0)
                    try:
                        os.startfile(data)
                    except Exception:
                        pass
                elif kind == "error":
                    self.run_btn.configure(state="normal", text="Run Backtest")
                    self.status.configure(text="Error occurred", text_color=_RED)
                    self._log(f"ERROR  {data}")
                    messagebox.showerror("Error", data[:500])
        except queue.Empty:
            pass
        self.after(100, self._poll)


# ── Shared widget helper ──────────────────────────────────────────────────────

def _label_caps(parent, text, pack_side=None):
    """Small-caps section label in Apple style."""
    lbl = ctk.CTkLabel(
        parent, text=text,
        text_color=_LBL4,
        font=ctk.CTkFont(size=10, weight="bold"),
    )
    if pack_side:
        lbl.pack(side=pack_side)
    else:
        lbl.pack(anchor="w", pady=(0, 2))
    return lbl
