# -*- coding: utf-8 -*-
"""Evaluate a rotation-bot backtest: does it earn the target, beat Buy-and-Hold, survive costs, and
hold up from the discovery window to the validation window?

    ./ftenv/Scripts/python.exe -m bot.rotation_eval RegimeRotationBot [RegimeRotationBot2x ...]

Input: the eight per-pair archives of `bot/run_rotation.py`. Everything is computed from each trade's
profit ratio with the evaluation's own conventions (fixed stake per trade, a trade belongs to the
window it opened in, the regime of the day it opened, the coin's own buy-and-hold over the whole
episode as benchmark), never from a run's account balance, which is meaningless for a run of one
pair. The account is modelled as eight slots, one per pair, each slot holding one position at a time.

Reported per window (discovery before 2024-01-01, validation from then on):

- trades and mean profit per trade, gross and after 0.1 % extra slippage per side (leverage counted);
- daily return on the provided capital (profit ratio sum / slot-days) and on the employed capital;
- the compounded daily growth of the equal-weight eight-slot account (each slot compounds its own
  trades; slots are averaged), against equal-weight Buy-and-Hold of the same pairs and days;
- the same per component (`enter_tag`), and for every component the phase row of the evaluation:
  excess return against the episode's Buy-and-Hold, the lower confidence bound, floor, and
  whether the row is *confirmed* (floor and LCB above 0 in both windows).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evidence import execution_robustness as er  # noqa: E402
from regime import attribution, discovery_comparison as dc, specialist_evaluation as se  # noqa: E402
from regime import daily_return  # noqa: E402

OUT = os.path.join(ROOT, "user_data", "rotation")
RESULTS = os.path.join(ROOT, "results", "regime", "rotation_bot")
PAIRS = ["BTC", "ETH", "LTC", "XRP", "ADA", "XLM", "XMR", "DASH"]
START = pd.Timestamp("2020-04-01", tz="UTC")
END = attribution.END
SLIP = er.COST["reference_slippage_per_side"]
TARGET = 0.0008
# component -> (kind, regime) of the evaluation row that answers for it
COMPONENT_ROW = {"hold": ("btc", "BULL"), "ei3v2": ("btc", "BEAR"), "ichimoku": ("coin", "SIDEWAYS"),
                 "buyordie": ("coin", "TRANSITION"), "hold_short": ("btc", "BEAR")}


def load_trades(variant):
    trades, missing = [], []
    for coin in PAIRS:
        found = sorted(glob.glob(os.path.join(OUT, "%s_%s-*.zip" % (variant, coin))))
        block = er.read_block(os.path.relpath(found[-1], ROOT).replace(os.sep, "/"), variant) if found else None
        if block is None:
            missing.append(coin)
            continue
        trades.extend(block.get("trades") or [])
    return trades, missing


def build_frame(trades, variant):
    frame = attribution.attribute([{"strategy_id": variant, "trades": trades, "model": "model0"}])
    leverage = np.array([t.get("leverage") or 1.0 for t in trades], dtype=float)
    frame["leverage"] = leverage[frame["trade_ordinal"].to_numpy()]
    return frame


def slot_days():
    daily = pd.read_csv(daily_return.DAILY, usecols=["date", "pair", "btc_regime"])
    daily["date"] = pd.to_datetime(daily["date"], utc=True)
    daily = daily[(daily["date"] >= START) & (daily["date"] < END)]
    daily["window"] = np.where(daily["date"] >= se.VALIDATION_START, "validation", "discovery")
    return daily[daily["btc_regime"].notna()].groupby("window").size().to_dict(), \
        {w: int(g["date"].nunique()) for w, g in daily.groupby("window")}


def window_of(frame):
    return np.where(frame["open_date"] >= se.VALIDATION_START, "validation", "discovery")


def growth_per_day(net, pair, days_in_window):
    """Compounded daily growth of the equal-weight account of eight slots."""
    factors = []
    for coin in PAIRS:
        sel = net[pair == coin]
        factors.append(float(np.prod(1.0 + sel)) if len(sel) else 1.0)
    total = float(np.mean(factors))
    return total ** (1.0 / days_in_window) - 1.0 if total > 0 else -1.0, total


def pooled_account(part, days, slots=len(PAIRS)):
    """One capital for all pairs, computed from the trade list.

    The stake of a new trade is the free capital divided by the number of free slots, which is what Freqtrade's
    `stake_amount: unlimited` does with `max_open_trades` = the number of pairs. Profits are booked when a trade closes,
    the fee and the extra slippage are in the net ratio. Returns the growth factor, the compounded daily growth and the
    worst peak-to-trough fall of the booked capital. The primary figures of the evaluation stay those of the slot
    model; this is a second reading."""
    rows = part.sort_values("open_date")
    events = []
    for i, (opened, minutes, net) in enumerate(zip(rows["open_date"], rows["trade_duration"].astype(float), rows["net"])):
        events.append((opened, 1, i, net))
        events.append((opened + pd.Timedelta(minutes=max(1.0, 0.0 if pd.isna(minutes) else minutes)), 0, i, net))
    events.sort(key=lambda e: (e[0], e[1]))       # a close before an open at the same instant
    free, stakes, curve = 1.0, {}, []
    for _, kind, i, net in events:
        if kind == 1:
            stake = free / max(1, slots - len(stakes))
            stakes[i] = stake
            free -= stake
        else:
            free += stakes.pop(i) * (1.0 + net)
            curve.append(free + sum(stakes.values()))
    total = free + sum(stakes.values())
    peak, worst = 1.0, 0.0
    for value in curve:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    growth = total ** (1.0 / days) - 1.0 if total > 0 else -1.0
    return total, growth, worst


def buy_hold(window_days):
    """Equal-weight buy-and-hold of the same pairs on the spot daily candles, per window."""
    closes = {}
    for coin in PAIRS:
        d = pd.read_feather(os.path.join(ROOT, "user_data", "data", "binance", "%s_USDT-1d.feather" % coin), columns=["date", "close"])
        d["date"] = pd.to_datetime(d["date"], utc=True)
        closes[coin] = d.set_index("date")["close"]
    out = {}
    for window, (a, b) in {"discovery": (START, se.VALIDATION_START), "validation": (se.VALIDATION_START, END)}.items():
        factors = []
        for coin, s in closes.items():
            part = s[(s.index >= a) & (s.index < b)]
            if len(part) > 1:
                factors.append(part.iloc[-1] / part.iloc[0])
        total = float(np.mean(factors))
        out[window] = {"factor": total, "daily": total ** (1.0 / window_days[window]) - 1.0}
    return out


def phase_row(frame, kind, regime):
    """The evaluation's row of one component: both windows, LCB, floor, confirmed."""
    priced = se.split_discovery_validation(se.attach_benchmark(frame.copy()))
    paired = dc.paired_rows(priced)
    row = paired[(paired["kind"] == kind) & (paired["regime"] == regime)]
    if row.empty:
        return None
    r = row.iloc[0]
    def num(v):
        return None if pd.isna(v) else round(float(v), 5)
    return {"kind": kind, "regime": regime,
            "trades_disc": num(r["trades_disc"]), "episodes_disc": num(r["episodes_disc"]), "excess_disc": num(r["excess_return_disc"]), "lcb_disc": num(r["episode_excess_lcb_disc"]),
            "trades_val": num(r["trades_val"]), "episodes_val": num(r["episodes_val"]), "excess_val": num(r["excess_return_val"]), "lcb_val": num(r["episode_excess_lcb_val"]),
            "floor_disc": bool(r["floor_disc"]), "floor_val": bool(r["floor_val"]), "confirmed": bool(r["confirmed"])}


def summary(frame, slots, days, windows):
    frame = frame.copy()
    frame["window"] = window_of(frame)
    frame["net"] = frame["profit_ratio"] - 2.0 * SLIP * frame["leverage"]
    frame["cap_days"] = np.maximum(frame["trade_duration"].astype(float), daily_return.MIN_HOLD_MINUTES) / 1440.0
    frame["coin"] = frame["pair"].str.split("/").str[0]
    out = {}
    for window in ("discovery", "validation"):
        part = frame[frame["window"] == window]
        record = {"trades": int(len(part)), "days": days[window], "slot_days": int(slots[window])}
        if len(part):
            g, factor = growth_per_day(part.sort_values("open_date")["net"].to_numpy(), part.sort_values("open_date")["coin"].to_numpy(), days[window])
            pooled = pooled_account(part, days[window])
            record.update({
                "mean_ratio_gross_pct": round(100 * float(part["profit_ratio"].mean()), 4),
                "mean_ratio_net_pct": round(100 * float(part["net"].mean()), 4),
                "daily_gross_on_provided_pct": round(100 * float(part["profit_ratio"].sum()) / slots[window], 5),
                "daily_net_on_provided_pct": round(100 * float(part["net"].sum()) / slots[window], 5),
                "daily_net_on_employed_pct": round(100 * float(part["net"].sum() / part["cap_days"].sum()), 4),
                "compounded_daily_net_pct": round(100 * g, 5), "compounded_total_factor": round(factor, 4),
                "pooled_total_factor": round(pooled[0], 4), "pooled_daily_net_pct": round(100 * pooled[1], 5),
                "pooled_worst_fall_pct": round(100 * pooled[2], 2),
                "share_liquidated": round(float((part["exit_reason"] == "liquidation").mean()), 4),
                "exit_reasons": part["exit_reason"].value_counts().to_dict()})
        out[window] = record
    return out


def evaluate(variant):
    trades, missing = load_trades(variant)
    if missing:
        raise SystemExit("%s: no archive for %s" % (variant, ", ".join(missing)))
    frame = build_frame(trades, variant)
    slots, days = slot_days()
    hold = buy_hold(days)
    result = {"variant": variant, "trades_total": int(len(frame)), "target_daily_pct": 100 * TARGET,
              "whole": summary(frame, slots, days, None), "buy_hold_equal_weight": hold, "components": {}}
    for tag, part in frame.groupby("enter_tag"):
        entry = summary(part, slots, days, None)
        cell = COMPONENT_ROW.get(tag)
        entry["evaluation_row"] = phase_row(part, *cell) if cell else None
        result["components"][tag] = entry
    result["whole"]["evaluation_rows"] = {"%s/%s" % (k, r): phase_row(frame, k, r) for k in ("btc", "coin")
                                          for r in ("BULL", "BEAR", "SIDEWAYS", "TRANSITION")}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("variants", nargs="+")
    args = parser.parse_args(argv)
    os.makedirs(RESULTS, exist_ok=True)
    for variant in args.variants:
        result = evaluate(variant)
        path = os.path.join(RESULTS, variant + ".json")
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=1, sort_keys=True)
            handle.write("\n")
        print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
