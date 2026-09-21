# -*- coding: utf-8 -*-
"""Portfolio of the component search: the uptrend hold plus the chosen candidate of each idle phase.

    ./ftenv/Scripts/python.exe -m bot.component_portfolio [hold variant for 2x, default RegimeRotationBotV2N1x2]

Reads `results/regime/rotation_bot/component_search.json` (`bot/component_search.py`, rule `PIPELINE_EXTENSIONS.md`
Part 4.4). The chosen candidate's trades are taken from its own canonical archive and kept when the trade opened in the
phase it was chosen for; the hold trades come from the bot's archives (1x: the base variant, 2x: the variant given). The
slot model (one slot per coin and day, fixed stake) is used; the trades of different candidates may overlap on one pair,
so the pooled account is not computed. The validation window is read for information only.

Writes `results/regime/rotation_bot/component_portfolio.json`.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from bot import component_search as cs, rotation_eval as ev  # noqa: E402

OUT = os.path.join(ev.RESULTS, "component_portfolio.json")


def frame_of(trades, label):
    if not trades:
        return pd.DataFrame()
    frame = pd.DataFrame({"pair": [t["pair"] for t in trades], "open_date": pd.to_datetime([t["open_date"] for t in trades], utc=True),
                          "profit_ratio": [t["profit_ratio"] for t in trades], "leverage": [t.get("leverage") or 1.0 for t in trades],
                          "trade_duration": [t.get("trade_duration") or 0 for t in trades], "exit_reason": [t.get("exit_reason") or "" for t in trades],
                          "close_date": pd.to_datetime([t.get("close_date") or t["open_date"] for t in trades], utc=True)})
    frame["enter_tag"] = label
    return frame[frame["open_date"] >= ev.START]


def hold_frame(variant):
    trades, missing = ev.load_trades(variant)
    assert not missing, missing
    return frame_of([t for t in trades if t.get("enter_tag") == "hold"], "hold")


def in_phase(frame, phase, lookup):
    frame = frame.copy()
    frame["day"] = frame["open_date"].dt.floor("D")
    frame["coin"] = frame["pair"].str.split("/").str[0]
    m = frame.merge(lookup[["coin", "date", "phase"]], left_on=["coin", "day"], right_on=["coin", "date"], how="left")
    return m[m["phase"] == phase].drop(columns=["day", "coin", "date", "phase"])


def main(argv=None):
    hold_2x = (argv or sys.argv[1:] or ["RegimeRotationBotV2N1x2"])[0]
    search = json.load(open(cs.OUT, encoding="utf-8"))
    chosen = search["final"]["chosen"]
    lookup, _ = cs.daily_frame()
    manifest = json.load(open(os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json"), encoding="utf-8"))["results"]
    slots, days = ev.slot_days()

    parts = {}
    for phase, cand in chosen.items():
        if cand is None:
            continue
        assert not cand.startswith("bot:"), "a bot component was chosen: %s" % cand
        trades = cs.archive_trades(cand, manifest)
        parts[phase] = in_phase(frame_of(trades, "%s:%s" % (phase, cand)), phase, lookup)

    def evaluate(hold, label):
        frames = [hold] + [p for p in parts.values() if len(p)]
        frame = pd.concat(frames, ignore_index=True)
        result = {"label": label, "whole": ev.summary(frame, slots, days, None), "components": {}}
        for tag, part in frame.groupby("enter_tag"):
            result["components"][tag] = ev.summary(part, slots, days, None)
        for record in [result["whole"]] + list(result["components"].values()):
            for window in ("discovery", "validation"):
                for k in ("pooled_total_factor", "pooled_daily_net_pct", "pooled_worst_fall_pct"):
                    record.get(window, {}).pop(k, None)
        return result

    out = {"rule": "PIPELINE_EXTENSIONS.md Part 4.4", "chosen": chosen, "hold_1x_variant": "RegimeRotationBot", "hold_2x_variant": hold_2x,
           "portfolio_1x": evaluate(hold_frame("RegimeRotationBot"), "hold 1x plus chosen candidates")}
    try:
        out["portfolio_2x"] = evaluate(hold_frame(hold_2x), "hold 2x plus chosen candidates")
    except AssertionError:
        out["portfolio_2x"] = None
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(out, handle, indent=1, sort_keys=True, default=lambda o: float(o) if hasattr(o, "__float__") else str(o))
        handle.write("\n")
    keys = ("trades", "daily_net_on_provided_pct", "daily_net_on_employed_pct", "mean_ratio_net_pct", "compounded_total_factor", "share_liquidated")
    for name in ("portfolio_1x", "portfolio_2x"):
        r = out[name]
        if not r:
            print(name, "missing")
            continue
        for window in ("discovery", "validation"):
            print("%s %-10s" % (name, window), {k: r["whole"][window].get(k) for k in keys})
            for tag, c in sorted(r["components"].items()):
                print("      %-46s" % tag, {k: c[window].get(k) for k in keys if c.get(window)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
