# -*- coding: utf-8 -*-
"""Where do the Stage 8b reruns (5m detail candles) deviate from the author-timeframe run, and why?

    ./ftenv/Scripts/python.exe -m bot.detail_5m_deviation

For every strategy with a measured 5m detail run (`evidence/EXECUTION_ROBUSTNESS.json`), the detail
archive is compared with the canonical baseline archive, over the validation window (trades that opened
from 2024-01-01) and over the whole window. The trades of both runs are matched by pair and opening
candle; the change of the sum of the profit ratios is split into

- trades both runs opened (the exit price or reason moved),
- trades only one run has (the entry set changed).

The strategy's source is scanned for the mechanisms that a coarse candle can misjudge (trailing stop,
custom stoploss, dynamic ROI, exit signals that depend on the profit, position adjustment), and the
deviation is grouped by them. A baseline made in another runtime than its detail run is flagged: there the
deviation cannot be told from a runtime difference without a control run.

Writes `results/regime/rotation_bot/detail_5m_deviation.json`.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evidence import execution_robustness as er  # noqa: E402

VALIDATION = pd.Timestamp("2024-01-01", tz="UTC")
OUT = os.path.join(ROOT, "results", "regime", "rotation_bot", "detail_5m_deviation.json")


def mechanisms(text):
    trailing = bool(re.search(r"^\s*trailing_stop\s*=\s*True", text, re.M))
    custom_stop = bool(re.search(r"use_custom_stoploss\s*=\s*True", text)) or bool(re.search(r"def custom_stoploss", text))
    table = re.search(r"minimal_roi\s*=\s*\{(.*?)\}", text, re.S)
    steps = len(re.findall(r"[\"']?\d+[\"']?\s*:", table.group(1))) if table else 0
    return {
        "trailing": trailing, "custom_stoploss": custom_stop,
        "dynamic_roi": steps >= 2 or bool(re.search(r"def custom_roi", text)),
        "profit_exit": bool(re.search(r"(sell|exit)_profit_only\s*=\s*True", text)) or bool(re.search(r"def custom_(sell|exit)", text)),
        "dca": bool(re.search(r"position_adjustment_enable\s*=\s*True", text)),
    }


def load(archive, strategy):
    block = er.read_block(archive, strategy)
    if not block or not block.get("trades"):
        return None
    frame = pd.DataFrame(block["trades"])
    frame["open_date"] = pd.to_datetime(frame["open_date"], utc=True)
    minutes = er.TF_MINUTES.get(block.get("timeframe") or "", 5)
    frame["key"] = frame["pair"] + "|" + frame["open_date"].dt.floor("%dmin" % minutes).astype(str)
    return frame.drop_duplicates("key", keep="first").set_index("key")


def compare(base, det, since):
    if since is not None:
        base = base[base["open_date"] >= since]
        det = det[det["open_date"] >= since]
    if base.empty or det.empty:
        return None
    common = base.index.intersection(det.index)
    only_b, only_d = base.drop(common), det.drop(common)
    bm, dm = base.loc[common], det.loc[common]
    delta = dm["profit_ratio"] - bm["profit_ratio"]
    moved = delta.abs() > 1e-4
    transitions = Counter()
    effect = defaultdict(float)
    for a, b, d in zip(bm.loc[moved, "exit_reason"], dm.loc[moved, "exit_reason"], delta[moved]):
        transitions[(a, b)] += 1
        effect[(a, b)] += float(d)
    top = sorted(effect.items(), key=lambda kv: -abs(kv[1]))[:3]
    return {
        "trades_base": int(len(base)), "trades_detail": int(len(det)), "common": int(len(common)),
        "mean_base_pct": 100 * float(base["profit_ratio"].mean()), "mean_detail_pct": 100 * float(det["profit_ratio"].mean()),
        "sum_base": float(base["profit_ratio"].sum()), "sum_detail": float(det["profit_ratio"].sum()),
        "common_delta_sum": float(delta.sum()), "entries_delta_sum": float(only_d["profit_ratio"].sum() - only_b["profit_ratio"].sum()),
        "share_moved": float(moved.mean()) if len(common) else 0.0,
        "top_exit_changes": [{"from": k[0], "to": k[1], "n": transitions[k], "sum": round(v, 3)} for k, v in top],
    }


def main():
    rob = json.load(open(er.ROBUSTNESS_OUTPUT, encoding="utf-8"))["results"]
    base_store = json.load(open(er.BASELINE_STORE, encoding="utf-8"))["results"]
    with io.open(os.path.join(ROOT, "STRATEGY_STATUS.csv"), encoding="utf-8-sig", newline="") as handle:
        status = {r["strategy_id"]: r for r in csv.DictReader(handle)}
    rows = []
    for sid, rec in sorted(rob.items()):
        detail_archive = (rec.get("detail") or {}).get("archive")
        if not detail_archive or rec.get("status") not in ("PASS", "SENSITIVE"):
            continue
        base = load(base_store[sid]["archive"], sid)
        det = load(detail_archive, sid)
        if base is None or det is None:
            continue
        source = os.path.join(ROOT, status.get(sid, {}).get("source_file") or "")
        mech = mechanisms(io.open(source, encoding="utf-8", errors="replace").read()) if os.path.isfile(source) else {}
        rows.append({
            "strategy_id": sid, "status": rec["status"], "reasons": rec.get("reasons"), "timeframe": rec.get("main_timeframe"),
            "same_runtime": (rec.get("comparison") or {}).get("same_runtime"), "mechanisms": mech,
            "validation": compare(base, det, VALIDATION), "whole": compare(base, det, None)})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rows, open(OUT, "w", encoding="utf-8"), indent=1)
    return rows


def pct(new, old):
    return 100.0 * (new - old) / abs(old) if old else float("nan")


def median(values):
    values = sorted(values)
    return values[len(values) // 2] if values else float("nan")


def dominant_cause(r):
    """One label for what moved most on the common trades of a strategy."""
    v = r["validation"]
    if abs(v["entries_delta_sum"]) > abs(v["common_delta_sum"]):
        return "entry set changed"
    if not v["top_exit_changes"]:
        return "no change"
    top = v["top_exit_changes"][0]
    a, b = top["from"], top["to"]
    if a == b:
        return {"trailing_stop_loss": "trailing stop, same reason (fill price)", "roi": "ROI, same reason (timing/price)",
                "stop_loss": "fixed stoploss (fill price)"}.get(a, "same exit reason (%s)" % a)
    return "exit reason changed (%s -> %s)" % (a, b)


def report(rows):
    usable = [r for r in rows if r["validation"]]
    print("strategies with both runs: %d (SENSITIVE %d)" % (len(usable), sum(1 for r in usable if r["status"] == "SENSITIVE")))
    same = Counter((r["status"], r["same_runtime"]) for r in usable)
    print("baseline and detail run in the same runtime (status, same runtime):", dict(same))

    def d_pp(r):
        return r["validation"]["mean_detail_pct"] - r["validation"]["mean_base_pct"]

    def rel(r):
        base = r["validation"]["mean_base_pct"]
        return 100.0 * (r["validation"]["mean_detail_pct"] - base) / abs(base) if abs(base) >= 0.3 else None

    def summary(label, group):
        if not group:
            return
        pp = [d_pp(r) for r in group]
        relative = [x for x in (rel(r) for r in group) if x is not None]
        sb = sum(r["validation"]["sum_base"] for r in group)
        sd = sum(r["validation"]["sum_detail"] for r in group)
        common = sum(r["validation"]["common_delta_sum"] for r in group)
        entries = sum(r["validation"]["entries_delta_sum"] for r in group)
        print("%-40s n=%3d | change of the mean per trade: median %+.3f pp, avg %+.3f pp | strategies with |mean| >= 0.3 %%: n=%3d, median |change| %5.1f %%, share above 20 %% %3.0f %% | "
              "pooled mean %+.2f %% (common %+.1f, entries %+.1f)" % (
                  label, len(group), median(pp), sum(pp) / len(pp), len(relative), median([abs(x) for x in relative]),
                  100.0 * sum(1 for x in relative if abs(x) > 20) / max(1, len(relative)),
                  pct(sd, sb), common, entries))

    print("\n-- validation window, by status")
    summary("all", usable)
    summary("PASS", [r for r in usable if r["status"] == "PASS"])
    summary("SENSITIVE", [r for r in usable if r["status"] == "SENSITIVE"])
    print("\n-- does the runtime alone move the result? (PASS strategies only)")
    summary("PASS, same runtime", [r for r in usable if r["status"] == "PASS" and r["same_runtime"]])
    summary("PASS, different runtime", [r for r in usable if r["status"] == "PASS" and not r["same_runtime"]])
    print("\n-- validation window, by author timeframe")
    for tf in ("15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"):
        summary(tf, [r for r in usable if r["timeframe"] == tf])
    print("\n-- validation window, by declared mechanism (a strategy counts in every group it belongs to)")
    for name in ("trailing", "custom_stoploss", "dynamic_roi", "profit_exit", "dca"):
        summary(name + " declared", [r for r in usable if r["mechanisms"].get(name)])
        summary("no " + name, [r for r in usable if not r["mechanisms"].get(name)])
    summary("none of trailing/custom stop/profit exit", [r for r in usable if not (r["mechanisms"].get("trailing") or r["mechanisms"].get("custom_stoploss") or r["mechanisms"].get("profit_exit"))])
    print("\n-- SENSITIVE strategies")
    sens = [r for r in usable if r["status"] == "SENSITIVE"]
    print("reasons:", dict(Counter(x for r in sens for x in (r["reasons"] or []))))
    print("same runtime: %d, different runtime: %d (there a runtime difference cannot be excluded without a control run)" % (
        sum(1 for r in sens if r["same_runtime"]), sum(1 for r in sens if not r["same_runtime"])))
    print("dominant cause on the common trades:")
    for cause, n in Counter(dominant_cause(r) for r in sens).most_common():
        print("   %2d  %s" % (n, cause))
    print("declared mechanism among the SENSITIVE: " + ", ".join("%s %d" % (name, sum(1 for r in sens if r["mechanisms"].get(name))) for name in ("trailing", "custom_stoploss", "dynamic_roi", "profit_exit", "dca")) +
          "; none of them: %d" % sum(1 for r in sens if not any(r["mechanisms"].get(k) for k in ("trailing", "custom_stoploss", "dynamic_roi", "profit_exit", "dca"))))
    print("\n-- the SENSITIVE strategies whose baseline and detail run share the runtime")
    for r in sens:
        if r["same_runtime"]:
            v = r["validation"]
            print("%-34s tf=%-4s n %4d->%4d mean %7.3f -> %7.3f  %s" % (r["strategy_id"][:34], r["timeframe"], v["trades_base"], v["trades_detail"], v["mean_base_pct"], v["mean_detail_pct"], dominant_cause(r)))


if __name__ == "__main__":
    report(main())
