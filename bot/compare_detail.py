# -*- coding: utf-8 -*-
"""One strategy, three runs over the same window: the pipeline's canonical 5m run, a native 5m control
run (same runtime as the detail run), and the same run with 1m detail candles.

    ./ftenv/Scripts/python.exe -m bot.compare_detail EI3v2_tag_cofi_green user_data/rotation/ei3v2_ctrl user_data/rotation/ei3v2_1m 2024-01-01

The canonical archive was made in Docker, the other two natively; the control run separates a
runtime difference from the effect of the detail candles. Trades are compared as the evaluation sees
them: by profit ratio, fixed stake, a trade belonging to the window it opened in.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evidence import execution_robustness as er  # noqa: E402


def trades_of(archive, strategy):
    block = er.read_block(os.path.relpath(archive, ROOT).replace(os.sep, "/"), strategy)
    frame = pd.DataFrame(block["trades"])
    frame["open_date"] = pd.to_datetime(frame["open_date"], utc=True)
    frame["close_date"] = pd.to_datetime(frame["close_date"], utc=True)
    return frame, block


def newest(prefix):
    found = sorted(glob.glob(os.path.join(ROOT, prefix + "-*.zip")))
    if not found:
        raise SystemExit("no archive for " + prefix)
    return found[-1]


def describe(name, frame, start):
    part = frame[frame["open_date"] >= start]
    ratio = part["profit_ratio"]
    reasons = part["exit_reason"].value_counts().to_dict()
    return {
        "run": name, "trades": len(part), "mean_ratio_pct": round(100 * ratio.mean(), 4),
        "sum_ratio": round(float(ratio.sum()), 3), "win_rate_pct": round(100 * float((ratio > 0).mean()), 1),
        "median_ratio_pct": round(100 * ratio.median(), 4),
        "mean_duration_h": round(part["trade_duration"].mean() / 60.0, 2),
        "worst_ratio_pct": round(100 * ratio.min(), 2), "best_ratio_pct": round(100 * ratio.max(), 2),
        "exit_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
    }


def main():
    strategy, control, detail, since = sys.argv[1:5]
    start = pd.Timestamp(since, tz="UTC")
    manifest = json.load(open(os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json"), encoding="utf-8"))["results"]
    canonical = manifest[strategy]["archive"]
    runs = [("canonical 5m (Docker)", os.path.join(ROOT, canonical.replace("/", os.sep))),
            ("control 5m (native)", newest(control)), ("1m detail (native)", newest(detail))]
    rows = []
    for name, archive in runs:
        frame, _ = trades_of(archive, strategy)
        rows.append(describe(name, frame, start))
    for r in rows:
        print("%-24s n=%-5d mean %8.4f%%  sum %8.3f  win %5.1f%%  median %8.4f%%  duration %6.2f h  worst %7.2f%%  best %7.2f%%"
              % (r["run"], r["trades"], r["mean_ratio_pct"], r["sum_ratio"], r["win_rate_pct"], r["median_ratio_pct"],
                 r["mean_duration_h"], r["worst_ratio_pct"], r["best_ratio_pct"]))
        print("    exits:", r["exit_reasons"])
    a, b, c = rows
    for x, y, label in ((a, b, "canonical -> control (runtime)"), (b, c, "control -> 1m detail (candles)"), (a, c, "canonical -> 1m detail (both)")):
        rel = (y["sum_ratio"] - x["sum_ratio"]) / abs(x["sum_ratio"]) if x["sum_ratio"] else float("nan")
        print("%-34s sum ratio %8.3f -> %8.3f (%+.0f %%), trades %d -> %d, mean %.4f%% -> %.4f%%"
              % (label, x["sum_ratio"], y["sum_ratio"], 100 * rel, x["trades"], y["trades"], x["mean_ratio_pct"], y["mean_ratio_pct"]))
    json.dump(rows, open(os.path.join(ROOT, "results", "regime", "rotation_bot", "detail_compare_%s.json" % strategy), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
