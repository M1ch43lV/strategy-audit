# -*- coding: utf-8 -*-
"""Daily return per market phase, for strategies and for Buy-and-Hold.

The question this answers: does capital put into a strategy earn at least X % per day while
its market phase lasts (owner's target: 0.08 % per day)? Two readings, both fixed-stake
(each trade is its own $1 stake, nothing compounded, the evaluation's convention):

- **on employed capital** (`daily_on_capital`): sum of the trades' profit ratios divided by the
  capital-days those trades held (a trade holds one stake for its duration, floored at
  `MIN_HOLD_MINUTES`). Idle capital does not count. A scalper that is in the market for minutes
  reaches large figures here, so this reading alone flatters short-holding strategies.
- **on provided capital** (`daily_on_slots`): the same profit divided by the *slot-days* of the
  phase, one slot per coin (the strategy holds at most one trade per pair) for every day the
  coin is in that state. Capital that sits idle counts. This is what a phase-by-phase account
  actually earns per day per unit of the capital set aside for it.

Buy-and-Hold is fully invested, so its two readings coincide: the sum of the episodes' returns
over the sum of their days.

Cost stress is not applied here: the slippage result per state lives in
`evidence/COST_SCREEN.json` (with leverage from the native blocks) and is joined by the page.

    ./ftenv/Scripts/python.exe -m regime.daily_return

Writes `results/regime/specialist_evaluation/phase_daily_return.csv` (strategy, kind, regime,
window) and `buy_hold_daily_return.csv` (kind, regime, window). Descriptive; changes no ranking.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from regime import specialist_evaluation as se  # noqa: E402

OUT = ROOT / "results" / "regime" / "specialist_evaluation"
TRADES = ROOT / "results" / "regime" / "trade_regime_attribution.csv"
DAILY = ROOT / "results" / "regime" / "regime_daily.csv"
MIN_HOLD_MINUTES = 60
KINDS = (("btc", "btc_regime", "btc_episode_id"), ("coin", "coin_regime", "coin_episode_id"))
VALIDATION_START = se.VALIDATION_START


def _window(dates: pd.Series) -> pd.Series:
    return np.where(dates >= VALIDATION_START, "validation", "discovery")


def strategy_phase_returns() -> pd.DataFrame:
    """Per strategy, kind, regime and window: trades, profit ratio sum, capital-days."""
    columns = ["strategy_id", "open_date", "trade_duration", "profit_ratio", "btc_regime", "coin_regime"]
    parts = []
    for chunk in pd.read_csv(TRADES, usecols=columns, chunksize=500_000,
                             dtype={"strategy_id": "string", "btc_regime": "string", "coin_regime": "string"}):
        chunk["open_date"] = pd.to_datetime(chunk["open_date"], utc=True)
        chunk["window"] = _window(chunk["open_date"])
        chunk["days"] = np.maximum(chunk["trade_duration"].astype(float), MIN_HOLD_MINUTES) / 1440.0
        for kind, column, _ in KINDS:
            part = chunk[chunk[column].notna()]
            grouped = part.groupby(["strategy_id", "window", column], observed=True).agg(
                trades=("profit_ratio", "size"), ratio_sum=("profit_ratio", "sum"),
                capital_days=("days", "sum")).reset_index().rename(columns={column: "regime"})
            grouped["kind"] = kind
            parts.append(grouped)
    frame = pd.concat(parts, ignore_index=True)
    return (frame.groupby(["strategy_id", "kind", "regime", "window"], as_index=False)
            [["trades", "ratio_sum", "capital_days"]].sum())


def slot_days(daily: pd.DataFrame) -> pd.DataFrame:
    """Coin-days in each state, per kind and window: the slots a phase provides."""
    rows = []
    daily = daily.assign(window=_window(daily["date"]))
    for kind, column, _ in KINDS:
        counts = daily[daily[column].notna()].groupby(["window", column]).size().rename("slot_days").reset_index()
        counts = counts.rename(columns={column: "regime"})
        counts["kind"] = kind
        rows.append(counts)
    return pd.concat(rows, ignore_index=True)


def buy_and_hold(daily: pd.DataFrame) -> pd.DataFrame:
    """Buy-and-Hold over every episode, per pair: fully invested, so one reading."""
    bounds = []
    for kind, column, episode in KINDS:
        d = daily[daily[column].notna()]
        group = ["pair", episode] if kind == "coin" else ["pair", episode]
        b = d.groupby(group).agg(start=("date", "min"), end=("date", "max"), regime=(column, "first")).reset_index()
        b["end_ts"] = b["end"] + pd.Timedelta(days=1)
        b["kind"] = kind
        bounds.append(b.drop(columns=[episode]))
    bounds = pd.concat(bounds, ignore_index=True)
    bounds["ret"] = np.nan
    for pair, part in bounds.groupby("pair"):
        candles = se._candle_series(pair, {})
        if candles is None:
            continue
        c = candles.assign(date=candles["date"].astype("datetime64[us, UTC]"))

        def price(ts):
            left = pd.DataFrame({"i": ts.index, "d": ts.astype("datetime64[us, UTC]").to_numpy()}).sort_values("d")
            m = pd.merge_asof(left, c, left_on="d", right_on="date", direction="backward")
            return m.set_index("i")["close"].reindex(ts.index)

        bounds.loc[part.index, "ret"] = (price(part["end_ts"]) / price(part["start"]) - 1.0).to_numpy()
    bounds["days"] = (bounds["end_ts"] - bounds["start"]).dt.days
    bounds["window"] = _window(bounds["start"])
    bounds = bounds.dropna(subset=["ret"])
    out = bounds.groupby(["kind", "regime", "window"]).agg(
        episodes=("ret", "size"), days=("days", "sum"), ratio_sum=("ret", "sum")).reset_index()
    out["daily_return"] = out["ratio_sum"] / out["days"]
    return out


def main() -> int:
    daily = pd.read_csv(DAILY, usecols=["date", "pair", "btc_regime", "coin_regime", "btc_episode_id", "coin_episode_id"],
                        dtype={"btc_episode_id": "string", "coin_episode_id": "string"})
    daily["date"] = pd.to_datetime(daily["date"], utc=True)
    daily = daily[daily["date"] < pd.Timestamp("2026-08-21T00:00:00Z")]

    trades = strategy_phase_returns()
    slots = slot_days(daily)
    trades = trades.merge(slots, on=["kind", "regime", "window"], how="left")
    trades["daily_on_capital"] = trades["ratio_sum"] / trades["capital_days"]
    trades["daily_on_slots"] = trades["ratio_sum"] / trades["slot_days"]
    OUT.mkdir(parents=True, exist_ok=True)
    trades.to_csv(OUT / "phase_daily_return.csv", index=False, lineterminator="\n", float_format="%.10g")
    bh = buy_and_hold(daily)
    bh.to_csv(OUT / "buy_hold_daily_return.csv", index=False, lineterminator="\n", float_format="%.10g")
    print("phase rows %d, strategies %d" % (len(trades), trades["strategy_id"].nunique()))
    print(bh[bh["window"] == "validation"].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
