# -*- coding: utf-8 -*-
"""Short test: how much does the return per trade fall when a 5m strategy is rerun with 1m detail candles?

    ./ftenv/Scripts/python.exe -m bot.detail_1m_batch --workers 3

Selection (computed, not hand-picked): strategies whose own timeframe is 5m, ranked by their
validation-window dollar gain (`strategy_total_dollar_gain.csv`), of which the source declares a
mechanism that a coarse candle can misjudge: `trailing_stop = True`, a custom stoploss, or a dynamic
ROI (a table of two or more steps, or `custom_roi`). Strategies with the same trades and gain (variants
of one implementation) count once. The first ten are run.

Each is rerun through the pipeline's own runner (`profile_smoke.run_one`, so the same runtime rules,
config and repairs as its canonical run) over the validation window with `--timeframe-detail 1m`.
It is compared with its canonical 5m archive over the same window, trade by trade in aggregate, the way
`bot/compare_detail.py` does it: mean profit ratio per trade, and the sum of the ratios.

Writes `results/regime/rotation_bot/detail_1m_batch.json`.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import io
import json
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evidence import execution_robustness as er, profile_smoke  # noqa: E402

WINDOW_START = pd.Timestamp("2024-01-01", tz="UTC")
TIMERANGE = "20240101-20260821"
OUT = os.path.join(ROOT, "results", "regime", "rotation_bot", "detail_1m_batch.json")
KEY = "val_1m"
CONTROL_KEY = "val_5m"


def declares_mechanism(text):
    trailing = bool(re.search(r"^\s*trailing_stop\s*=\s*True", text, re.M))
    custom_stop = bool(re.search(r"use_custom_stoploss\s*=\s*True", text)) or bool(re.search(r"def custom_stoploss", text))
    table = re.search(r"minimal_roi\s*=\s*\{(.*?)\}", text, re.S)
    steps = len(re.findall(r"[\"']?\d+[\"']?\s*:", table.group(1))) if table else 0
    dynamic_roi = steps >= 2 or bool(re.search(r"def custom_roi", text))
    return {"trailing": trailing, "custom_stoploss": custom_stop, "dynamic_roi": dynamic_roi, "roi_steps": steps}


def select(count=10):
    gain = pd.read_csv(os.path.join(ROOT, "results", "regime", "specialist_evaluation", "strategy_total_dollar_gain.csv"))
    with io.open(os.path.join(ROOT, "STRATEGY_STATUS.csv"), encoding="utf-8-sig", newline="") as handle:
        status = {r["strategy_id"]: r for r in csv.DictReader(handle)}
    robustness = json.load(open(er.ROBUSTNESS_OUTPUT, encoding="utf-8"))["results"]
    seen, chosen = set(), []
    for row in gain.itertuples():
        sid = row.strategy_id
        if (robustness.get(sid) or {}).get("main_timeframe") != "5m":
            continue
        source = os.path.join(ROOT, status.get(sid, {}).get("source_file") or "")
        if not os.path.isfile(source):
            continue
        mech = declares_mechanism(io.open(source, encoding="utf-8", errors="replace").read())
        if not (mech["trailing"] or mech["custom_stoploss"] or mech["dynamic_roi"]):
            continue
        signature = (int(row.trades), round(float(row.dollar_gain_usd), 2))
        if signature in seen:
            continue
        seen.add(signature)
        chosen.append(dict(strategy_id=sid, validation_gain_usd=round(float(row.dollar_gain_usd)), **mech))
        if len(chosen) == count:
            break
    return chosen


def trades_from(archive, strategy):
    block = er.read_block(archive, strategy)
    frame = pd.DataFrame(block["trades"])
    frame["open_date"] = pd.to_datetime(frame["open_date"], utc=True)
    return frame[frame["open_date"] >= WINDOW_START]


def stats(frame):
    ratio = frame["profit_ratio"]
    return {"trades": int(len(frame)), "mean_ratio_pct": 100 * float(ratio.mean()), "sum_ratio": float(ratio.sum()),
            "win_rate_pct": 100 * float((ratio > 0).mean())}


def run(entry, rows, manifest, timeout):
    sid = entry["strategy_id"]
    result = profile_smoke.run_one(rows[sid], TIMERANGE, timeout, artifact_key=KEY,
                                   extra_cli_args=["--timeframe-detail", "1m"])
    out = dict(entry, run_status=result.get("status"), elapsed_s=result.get("elapsed_s"),
               mode=result.get("mode"), why=result.get("why"))
    base = manifest[sid]
    out["canonical_runtime"] = (base.get("runtime_id") or "")[:12]
    if result.get("status") != "measured":
        return out
    canonical = stats(trades_from(base["archive"], sid))
    detail = stats(trades_from(result["archive"], sid))
    out.update(canonical=canonical, detail_1m=detail,
               mean_change_pct=100 * (detail["mean_ratio_pct"] - canonical["mean_ratio_pct"]) / abs(canonical["mean_ratio_pct"]) if canonical["mean_ratio_pct"] else None,
               sum_change_pct=100 * (detail["sum_ratio"] - canonical["sum_ratio"]) / abs(canonical["sum_ratio"]) if canonical["sum_ratio"] else None)
    return out


def control(chosen, args):
    """The same window and runner without detail candles: what the 5m run gives when it starts at 2024-01-01."""
    rows = {r["strategy_id"]: r for r in profile_smoke.read_manifest(profile_smoke.MANIFEST)}
    out = {}

    def one(entry):
        sid = entry["strategy_id"]
        result = profile_smoke.run_one(rows[sid], TIMERANGE, args.timeout, artifact_key=CONTROL_KEY)
        if result.get("status") != "measured":
            return sid, {"run_status": result.get("status"), "why": result.get("why")}
        return sid, dict(stats(trades_from(result["archive"], sid)), run_status="measured", archive=result["archive"])

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for sid, record in pool.map(one, chosen):
            out[sid] = record
            print(sid, record.get("run_status"), record.get("trades"), None if "mean_ratio_pct" not in record else round(record["mean_ratio_pct"], 3), flush=True)
    path = os.path.join(ROOT, "results", "regime", "rotation_bot", "detail_5m_control_batch.json")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1)
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--control", action="store_true",
                        help="run the same window at 5m without detail candles (native runtime), to separate the "
                             "effect of the detail candles from the effect of starting the window at 2024-01-01")
    parser.add_argument("--only", default="", help="comma-separated strategy ids")
    args = parser.parse_args()
    chosen = select()
    if args.only:
        chosen = [c for c in chosen if c["strategy_id"] in set(args.only.split(","))]
    if args.control:
        return control(chosen, args)
    for entry in chosen:
        print("selected", entry, flush=True)
    rows = {r["strategy_id"]: r for r in profile_smoke.read_manifest(profile_smoke.MANIFEST)}
    manifest = json.load(open(os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json"), encoding="utf-8"))["results"]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run, e, rows, manifest, args.timeout): e for e in chosen}
        for future in concurrent.futures.as_completed(futures):
            r = future.result()
            results.append(r)
            print("%-38s %-9s %6.0f s  canonical n=%s mean %s%%  1m n=%s mean %s%%  mean change %s%%" % (
                r["strategy_id"], r["run_status"], r.get("elapsed_s") or 0,
                r.get("canonical", {}).get("trades"), None if "canonical" not in r else round(r["canonical"]["mean_ratio_pct"], 3),
                r.get("detail_1m", {}).get("trades"), None if "detail_1m" not in r else round(r["detail_1m"]["mean_ratio_pct"], 3),
                None if r.get("mean_change_pct") is None else round(r["mean_change_pct"], 1)), flush=True)
    results.sort(key=lambda r: -r["validation_gain_usd"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(results, open(OUT, "w", encoding="utf-8"), indent=1)
    good = [r for r in results if "canonical" in r]
    if good:
        mean_of_changes = sum(r["mean_change_pct"] for r in good) / len(good)
        pooled_canon = sum(r["canonical"]["sum_ratio"] for r in good)
        pooled_detail = sum(r["detail_1m"]["sum_ratio"] for r in good)
        print("strategies measured: %d of %d" % (len(good), len(results)))
        print("average change of the mean profit per trade: %+.1f %% (median %+.1f %%)" % (
            mean_of_changes, sorted(r["mean_change_pct"] for r in good)[len(good) // 2]))
        print("sum of ratios over all: %.2f -> %.2f (%+.1f %%)" % (pooled_canon, pooled_detail, 100 * (pooled_detail - pooled_canon) / abs(pooled_canon)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
