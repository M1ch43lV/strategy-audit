# -*- coding: utf-8 -*-
"""Whole-window benchmark of the discovery window: dollar gain and Freqtrade's own metrics.

`regime/specialist_evaluation.py` prices only the validation window in `strategy_total_dollar_gain.csv`,
and Freqtrade's own report block of a full backtest covers the whole run (2020-04 to 2026-08), discovery
and validation together. Neither says what a strategy did in the discovery window (trades opened before
2024-01-01) on its own. This module computes both for that window from the same trade lists:

* the fixed-$1000-stake dollar gain, the coin's own buy-and-hold over the same trades and the excess,
  priced by the evaluation's own `total_dollar_gain_table` on the discovery trades;
* Freqtrade's report metrics (win rate, CAGR, Sharpe, Sortino, Calmar, profit factor, expectancy, SQN,
  max drawdown, final capital), computed with `freqtrade.data.metrics` from the trades' `profit_abs`,
  starting capital $1000 and the window 2020-04-01 to 2024-01-01.

Two sources, as on the 5m basis of the pages: `baseline` (the pooled baseline run, whose resolution is 5m
or finer for a strategy at or below 5m) and `detail_5m` (the 5m rerun of stage 8b, for a strategy above
5m). The page picks per strategy. A run's own account compounds across the whole period, so its first
years are exactly a discovery-window run except for trades still open at the end of 2023, which a run
that stopped there would have closed by force; `market_change` (Freqtrade's buy-and-hold of the whole
period) is not recomputed.

    ./ftenv/Scripts/python.exe -m regime.discovery_benchmark

Writes `results/regime/specialist_evaluation/discovery_total_dollar_gain.csv` and
`discovery_native_stats.csv`, each with a `source` column.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from freqtrade.data import metrics as ftm  # noqa: E402
from regime import attribution, detail_totals, discovery_comparison as dc, specialist_evaluation as se  # noqa: E402

OUTDIR = ROOT / "results" / "regime" / "specialist_evaluation"
TOTALS = OUTDIR / "discovery_total_dollar_gain.csv"
NATIVE = OUTDIR / "discovery_native_stats.csv"
BASELINE_GAIN = OUTDIR / "strategy_total_dollar_gain.csv"
START = attribution.START
END = se.VALIDATION_START
CHUNK = 25


def native_stats(trades: pd.DataFrame) -> dict:
    """Freqtrade's report metrics for one strategy's trades of the window, as its own functions define them."""
    balance = se.START_CAPITAL
    trades = trades.sort_values("close_date")
    profit = trades["profit_abs"].astype(float)
    wins, losses = int((profit > 0).sum()), int((profit < 0).sum())
    days = max(1, (END - START).days)
    final = balance + float(profit.sum())
    gross_win, gross_loss = float(profit[profit > 0].sum()), float(-profit[profit < 0].sum())
    try:
        drawdown = ftm.calculate_max_drawdown(trades, starting_balance=balance)
        dd_account, dd_abs = drawdown.relative_account_drawdown, drawdown.drawdown_abs
    except ValueError:
        dd_account = dd_abs = 0.0
    expectancy, expectancy_ratio = ftm.calculate_expectancy(trades)
    return {
        "total_trades": len(trades),
        "trade_count_long": int((~trades["is_short"].astype(bool)).sum()),
        "trade_count_short": int(trades["is_short"].astype(bool).sum()),
        "profit_total": float(profit.sum()) / balance, "profit_total_abs": float(profit.sum()),
        "cagr": ftm.calculate_cagr(days, balance, final),
        "sharpe": ftm.calculate_sharpe(trades, START, END, balance),
        "sortino": ftm.calculate_sortino(trades, START, END, balance),
        "calmar": ftm.calculate_calmar(trades, START, END, balance),
        "sqn": ftm.calculate_sqn(trades, balance),
        "profit_factor": gross_win / gross_loss if gross_loss > 0 else None,
        "expectancy": expectancy, "expectancy_ratio": expectancy_ratio,
        "winrate": wins / len(trades), "wins": wins, "losses": losses,
        "draws": len(trades) - wins - losses,
        "max_drawdown_account": dd_account, "max_drawdown_abs": dd_abs,
        "market_change": None, "starting_balance": balance, "final_balance": final,
        "trades_per_day": len(trades) / days,
    }


def summarize(priced: pd.DataFrame, source: str):
    """(totals, native rows) of one priced trade frame, restricted to its discovery trades."""
    disc = dc.discovery_trades(priced)
    totals = se.total_dollar_gain_table(disc)
    totals["source"] = source
    rows = []
    for strategy, part in priced[priced["analysis_window"] == "discovery"].groupby("strategy_id", sort=False):
        row = native_stats(part)
        row.update(strategy_id=strategy, source=source)
        rows.append(row)
    return totals, rows


def baseline(strategies) -> tuple[pd.DataFrame, list]:
    """The pooled baseline trades of these strategies, priced on their discovery trades."""
    trades = se.load_trades(se.DEFAULT_TRADES, set(strategies))
    trades = trades[(trades["open_date"] >= START) & (trades["open_date"] < END)]
    priced = se.split_discovery_validation(se.attach_benchmark(trades))
    return summarize(priced, "baseline")


def detail(strategies=None) -> tuple[list, list]:
    """The 5m detail runs of stage 8b, chunk by chunk."""
    totals, rows, batch = [], [], {}

    def flush():
        archives = [{"strategy_id": s, "trades": b.get("trades") or [], "model": "model0"}
                    for s, b in batch.items() if b.get("trades")]
        if archives:
            priced = se.split_discovery_validation(se.attach_benchmark(attribution.attribute(archives)))
            t, r = summarize(priced, "detail_5m")
            totals.append(t)
            rows.extend(r)
        batch.clear()

    for strategy, _archive, block in detail_totals.measured_blocks(strategies):
        batch[strategy] = block
        if len(batch) >= CHUNK:
            flush()
            print("  detail runs done: %d" % len(rows), flush=True)
    flush()
    return totals, rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--only", nargs="*", help="strategy ids (default: all)")
    args = parser.parse_args(argv)
    only = set(args.only) if args.only else None
    gain = pd.read_csv(BASELINE_GAIN)["strategy_id"]
    base_totals, base_rows = baseline(set(gain) if only is None else only)
    det_totals, det_rows = detail(only)
    totals = pd.concat([base_totals] + det_totals, ignore_index=True)
    native = pd.DataFrame(base_rows + det_rows)
    if only is None:
        totals.to_csv(TOTALS, index=False, float_format="%.12g")
        native.to_csv(NATIVE, index=False, float_format="%.12g")
    print("discovery totals: %d rows, native stats: %d rows" % (len(totals), len(native)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
