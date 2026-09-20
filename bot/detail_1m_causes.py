# -*- coding: utf-8 -*-
"""Where does the 1m-detail change come from? Trade by trade, control 5m against 1m detail.

    ./ftenv/Scripts/python.exe -m bot.detail_1m_causes

For each strategy of the batch the two runs' trades are matched by pair and opening candle. Then the
change of the mean profit per trade is split into
- trades that both runs opened (same entry): how their exit and profit differ, and by which exit reason;
- trades only one run has (the entry set changed, because an earlier trade closed differently and
  freed or blocked the pair).
"""
from __future__ import annotations

import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from bot import detail_1m_batch as batch, detail_1m_report as report  # noqa: E402


def load(strategy, archive):
    frame = batch.trades_from(os.path.relpath(archive, ROOT).replace(os.sep, "/"), strategy)
    frame = frame.copy()
    frame["key"] = frame["pair"] + "|" + frame["open_date"].dt.floor("5min").astype(str)
    return frame.drop_duplicates("key", keep="first").set_index("key")


def main():
    total = {"matched_n": 0, "matched_delta_sum": 0.0, "only_ctrl_n": 0, "only_ctrl_sum": 0.0, "only_1m_n": 0, "only_1m_sum": 0.0}
    for entry in batch.select():
        sid = entry["strategy_id"]
        c, d = report.newest(sid, batch.CONTROL_KEY), report.newest(sid, batch.KEY)
        if not (c and d):
            continue
        a, b = load(sid, c), load(sid, d)
        common = a.index.intersection(b.index)
        ma, mb = a.loc[common], b.loc[common]
        delta = mb["profit_ratio"] - ma["profit_ratio"]
        same_exit = (ma["exit_reason"] == mb["exit_reason"])
        moved = delta.abs() > 1e-4
        only_a, only_b = a.drop(common), b.drop(common)
        print("== %s   [trailing=%s custom_stoploss=%s dynamic_roi=%s]" % (
            sid, entry["trailing"], entry["custom_stoploss"], entry["dynamic_roi"]))
        print("   trades control %d, 1m %d, same entry %d (%.0f %%); profit differs on %d of the common trades (%.0f %%)" % (
            len(a), len(b), len(common), 100.0 * len(common) / max(1, len(a)), int(moved.sum()), 100.0 * moved.mean() if len(common) else 0))
        print("   on the common trades: mean %+.3f %% per trade (control %.3f %%, 1m %.3f %%)" % (
            100 * delta.mean(), 100 * ma["profit_ratio"].mean(), 100 * mb["profit_ratio"].mean()))
        if int(moved.sum()):
            changes = pd.crosstab(ma.loc[moved, "exit_reason"], mb.loc[moved, "exit_reason"])
            worst = (mb.loc[moved, "profit_ratio"] - ma.loc[moved, "profit_ratio"]).groupby(
                [ma.loc[moved, "exit_reason"], mb.loc[moved, "exit_reason"]]).agg(["count", "sum"])
            worst = worst.sort_values("sum")
            top = worst.head(3)
            print("   exit changes with the largest total effect (control -> 1m): " + "; ".join(
                "%s->%s n=%d sum %+.2f" % (k[0], k[1], int(v["count"]), v["sum"]) for k, v in top.iterrows()))
            best = worst.tail(2)
            print("   and in the other direction: " + "; ".join(
                "%s->%s n=%d sum %+.2f" % (k[0], k[1], int(v["count"]), v["sum"]) for k, v in best.iterrows()))
        print("   only in control: %d trades, mean %.3f %% | only in 1m: %d trades, mean %.3f %%" % (
            len(only_a), 100 * only_a["profit_ratio"].mean() if len(only_a) else float("nan"),
            len(only_b), 100 * only_b["profit_ratio"].mean() if len(only_b) else float("nan")))
        # how much of the difference in the sum of ratios each part explains
        explained_common = float(delta.sum())
        explained_only = float(only_b["profit_ratio"].sum() - only_a["profit_ratio"].sum())
        print("   change of the ratio sum: %+.2f from common trades, %+.2f from trades only one run has" % (explained_common, explained_only))
        total["matched_n"] += len(common)
        total["matched_delta_sum"] += explained_common
        total["only_ctrl_n"] += len(only_a)
        total["only_ctrl_sum"] += float(only_a["profit_ratio"].sum())
        total["only_1m_n"] += len(only_b)
        total["only_1m_sum"] += float(only_b["profit_ratio"].sum())
    print("== all strategies:", {k: round(v, 2) for k, v in total.items()})


if __name__ == "__main__":
    main()
