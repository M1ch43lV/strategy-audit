# -*- coding: utf-8 -*-
"""Choice of the option per phase for RegimeRotationBotV2, from the discovery window only.

    ./ftenv/Scripts/python.exe -m bot.phase_choice

The rule is `PIPELINE_EXTENSIONS.md`, Part 4.2, point 1 (written before this was run). For each of the phases BTC bear,
coin sideways and coin transition there are three options: the phase's component (the trades of the base variant
that opened in the phase), Buy-and-Hold of the coin for the length of the phase, and cash. An option other than cash
is taken only if the one-sided 95 % lower confidence bound of its mean net return per phase episode is above 0 in the
discovery window; among those the highest mean wins; if none passes the phase is cash.

Only the discovery window is read here (`WINDOW`); nothing of the validation window enters the choice.

Phase episodes are runs of consecutive days of one coin in one bot phase, the phase being decided as the bot decides
it: BTC bull is hold, BTC bear is bear, else the coin's own SIDEWAYS or TRANSITION. The component's return of an
episode is the sum of the net returns of the trades that opened in it (an episode without a trade earns 0). The
Buy-and-Hold return of an episode is the coin's spot daily open on the day after the episode over the open on its
first day, minus the round-trip cost of a hold trade (fee and slippage, 0.1 % each per side).

Writes `results/regime/rotation_bot/phase_choice.json`.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from bot import rotation_eval as ev  # noqa: E402
from regime import daily_return, specialist_evaluation as se  # noqa: E402

BASE_VARIANT = "RegimeRotationBot"
WINDOW = "discovery"
PHASES = {"bear": "ei3v2", "side": "ichimoku", "trans": "buyordie"}
FEE = 0.001
ROUND_TRIP = 2 * FEE + 2 * ev.SLIP
OUT = os.path.join(ev.RESULTS, "phase_choice.json")


def bot_phase(frame):
    btc, coin = frame["btc_regime"], frame["coin_regime"]
    return np.select([btc.eq("BULL"), btc.eq("BEAR"), coin.eq("SIDEWAYS"), coin.eq("TRANSITION")],
                     ["hold", "bear", "side", "trans"], default="flat")


def episodes(window):
    daily = pd.read_csv(daily_return.DAILY, usecols=["date", "pair", "btc_regime", "coin_regime"])
    daily["date"] = pd.to_datetime(daily["date"], utc=True)
    daily = daily[(daily["date"] >= ev.START) & (daily["date"] < ev.END)].sort_values(["pair", "date"])
    daily["coin"] = daily["pair"].str.split("/").str[0]
    daily["phase"] = bot_phase(daily)
    lo, hi = (ev.START, se.VALIDATION_START) if window == "discovery" else (se.VALIDATION_START, ev.END)
    rows = []
    for coin, part in daily.groupby("coin"):
        part = part.reset_index(drop=True)
        run = (part["phase"] != part["phase"].shift()) | (part["date"].diff() != pd.Timedelta(days=1))
        part["episode"] = run.cumsum()
        for _, e in part.groupby("episode"):
            start, end = e["date"].iloc[0], e["date"].iloc[-1]
            if start < lo or start >= hi:
                continue
            rows.append({"coin": coin, "phase": e["phase"].iloc[0], "start": start, "end": end, "days": len(e)})
    return pd.DataFrame(rows)


def hold_return(coin, start, end, opens):
    s = opens[coin]
    after = end + pd.Timedelta(days=1)
    if start not in s.index or after not in s.index:
        return np.nan
    return float(s.loc[after] / s.loc[start] - 1.0 - ROUND_TRIP)


def lcb(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2:
        return float("nan")
    return float(x.mean() - stats.t.ppf(0.95, n - 1) * x.std(ddof=1) / np.sqrt(n))


def main():
    trades, missing = ev.load_trades(BASE_VARIANT)
    assert not missing, missing
    frame = ev.build_frame(trades, BASE_VARIANT)
    frame["net"] = frame["profit_ratio"] - 2.0 * ev.SLIP * frame["leverage"]
    frame["coin"] = frame["pair"].str.split("/").str[0]
    frame["day"] = frame["open_date"].dt.floor("D")
    opens = {}
    for coin in ev.PAIRS:
        d = pd.read_feather(os.path.join(ROOT, "user_data", "data", "binance", "%s_USDT-1d.feather" % coin), columns=["date", "open"])
        d["date"] = pd.to_datetime(d["date"], utc=True)
        opens[coin] = d.set_index("date")["open"]

    eps = episodes(WINDOW)
    result = {"window": WINDOW, "rule": "PIPELINE_EXTENSIONS.md Part 4.2 point 1", "phases": {}}
    for phase, tag in PHASES.items():
        e = eps[eps["phase"] == phase].reset_index(drop=True)
        comp = []
        for _, row in e.iterrows():
            sel = frame[(frame["coin"] == row["coin"]) & (frame["enter_tag"] == tag)
                        & (frame["day"] >= row["start"]) & (frame["day"] <= row["end"])]
            comp.append(float(sel["net"].sum()))
        hold = [hold_return(r["coin"], r["start"], r["end"], opens) for _, r in e.iterrows()]
        hold = np.array(hold)
        keep = ~np.isnan(hold)
        options = {"cash": {"mean": 0.0, "lcb": 0.0, "n": int(len(e))},
                   "component": {"mean": float(np.mean(comp)), "lcb": lcb(comp), "n": int(len(comp)), "tag": tag},
                   "hold": {"mean": float(hold[keep].mean()), "lcb": lcb(hold[keep]), "n": int(keep.sum())}}
        passing = {k: v for k, v in options.items() if k != "cash" and v["lcb"] > 0}
        choice = max(passing, key=lambda k: passing[k]["mean"]) if passing else "cash"
        for v in options.values():
            v["mean_pct"] = round(100 * v["mean"], 4)
            v["lcb_pct"] = round(100 * v["lcb"], 4) if not np.isnan(v["lcb"]) else None
        result["phases"][phase] = {"episodes": int(len(e)), "phase_days": int(e["days"].sum()), "options": options, "choice": choice}
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=1, sort_keys=True)
        handle.write("\n")
    for phase, r in result["phases"].items():
        print("%-6s episodes %4d days %5d -> %s" % (phase, r["episodes"], r["phase_days"], r["choice"]))
        for name, v in r["options"].items():
            print("        %-10s mean %8.3f %%  LCB %8.3f %%  n %d" % (name, v["mean_pct"], v["lcb_pct"] if v["lcb_pct"] is not None else float("nan"), v["n"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
