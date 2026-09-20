# -*- coding: utf-8 -*-
"""Validation-window totals and phase tables of the 5m detail runs, beside those of the author timeframe.

`regime/specialist_evaluation.py` prices every strategy's validation trades once, from the
author-timeframe baseline (`strategy_total_dollar_gain.csv`). Stage 8b reruns a strategy above 5m
with 5m candles for everything that happens inside a candle, and that rerun makes different
trades. This module prices the rerun's validation trades the same way, so the two can be
shown next to each other: trades, fixed-$1000 dollar gain, the coin's own buy-and-hold over the
same trades, the excess, and the mean profit per trade before and after 0.1 % slippage per side.

Nothing is decided here and no ranking changes. The functions are the evaluation's and the
cost screen's own (`attribution.attribute`, `attach_benchmark`, `total_dollar_gain_table`,
`regime_cost_screen`, `validation_total`), applied to the detail archive instead of the baseline.

    ./ftenv/Scripts/python.exe -m regime.detail_totals            # every measured detail run
    ./ftenv/Scripts/python.exe -m regime.detail_totals --check    # reproduce the baseline figures

Writes `results/regime/specialist_evaluation/detail_5m_total_dollar_gain.csv`, one row per
strategy that has a measured detail run, and the same runs' phase tables
(`detail_5m_btc_specialist_table.csv`, `detail_5m_coin_specialist_table.csv`, with the daily
returns of `regime/daily_return.py` in `detail_5m_phase_daily.csv`), computed by the evaluation's own
`btc_specialist_table` / `coin_specialist_table`. Strategies at or below 5m have no rerun (owner rule) and
no row. `--check` runs the same code on the baseline archives of a few strategies and compares
the result with `strategy_total_dollar_gain.csv`; it must agree, or this module prices trades
differently from the evaluation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evidence import execution_robustness as er  # noqa: E402
from regime import attribution, specialist_evaluation as se  # noqa: E402

OUTDIR = ROOT / "results" / "regime" / "specialist_evaluation"
OUT = OUTDIR / "detail_5m_total_dollar_gain.csv"
BASELINE_TABLE = ROOT / "results" / "regime" / "specialist_evaluation" / "strategy_total_dollar_gain.csv"
CHUNK = 25


def price(blocks: dict, with_phases: bool = False):
    """One row per strategy: the validation window of these native blocks, priced as the
    evaluation prices the baseline. With `with_phases`, returns (table, btc phases, coin phases,
    daily returns per phase) instead of the table alone."""
    archives = [{"strategy_id": s, "trades": b.get("trades") or [], "model": "model0"}
                for s, b in blocks.items() if b.get("trades")]
    if not archives:
        return (pd.DataFrame(),) * 4 if with_phases else pd.DataFrame()
    frame = attribution.attribute(archives)
    leverage = {a["strategy_id"]: np.array([t.get("leverage") or 1.0 for t in a["trades"]],
                                           dtype=float) for a in archives}
    frame["leverage"] = [leverage[s][o] for s, o in zip(frame["strategy_id"], frame["trade_ordinal"])]
    cost = {s: er.validation_total(er.regime_cost_screen(part), "btc")
            for s, part in frame.groupby("strategy_id", sort=False)}
    daily = daily_returns(frame)
    priced = se.split_discovery_validation(se.attach_benchmark(frame))
    table = se.total_dollar_gain_table(priced)
    table["cost_mean_pct"] = table["strategy_id"].map(lambda s: cost[s]["mean_profit_pct"])
    table["cost_stressed_pct"] = table["strategy_id"].map(lambda s: cost[s]["stressed_pct"])
    table["daily_on_capital"] = table["strategy_id"].map(lambda s: daily.get(s, (None, None))[0])
    table["daily_on_slots"] = table["strategy_id"].map(lambda s: daily.get(s, (None, None))[1])
    if not with_phases:
        return table
    return (table, se.btc_specialist_table(priced), se.coin_specialist_table(priced), phase_daily(frame))


def phase_daily(frame: pd.DataFrame) -> pd.DataFrame:
    """Daily return per strategy, kind and phase, as regime/daily_return.py defines it: after 0.1 %
    slippage per side and on both capitals for the validation window, before slippage on the
    provided capital for the discovery window."""
    from regime import daily_return
    daily = pd.read_csv(daily_return.DAILY, usecols=["date", "pair", "btc_regime", "coin_regime"])
    daily["date"] = pd.to_datetime(daily["date"], utc=True)
    daily = daily[daily["date"] < attribution.END]
    slots = daily_return.slot_days(daily).set_index(["kind", "regime", "window"])["slot_days"]
    slip = er.COST["reference_slippage_per_side"]
    window = np.where(frame["open_date"] >= se.VALIDATION_START, "validation", "discovery")
    base = frame.assign(window=window,
                        net=frame["profit_ratio"] - 2.0 * slip * frame["leverage"],
                        days=np.maximum(frame["trade_duration"].astype(float), daily_return.MIN_HOLD_MINUTES) / 1440.0)
    rows = []
    for kind, column, _ in daily_return.KINDS:
        part = base[base[column].notna()]
        grouped = part.groupby(["strategy_id", "window", column]).agg(
            raw=("profit_ratio", "sum"), net=("net", "sum"), days=("days", "sum")).reset_index()
        grouped = grouped.rename(columns={column: "regime"})
        grouped["kind"] = kind
        rows.append(grouped)
    out = pd.concat(rows, ignore_index=True)
    out["slot_days"] = [slots.get((k, r, w), np.nan) for k, r, w in zip(out["kind"], out["regime"], out["window"])]
    val = out[out["window"] == "validation"]
    disc = out[out["window"] == "discovery"].set_index(["strategy_id", "kind", "regime"])
    result = pd.DataFrame({"strategy_id": val["strategy_id"], "kind": val["kind"], "regime": val["regime"],
                           "daily_on_capital": val["net"] / val["days"], "daily_on_slots": val["net"] / val["slot_days"]})
    keys = list(zip(val["strategy_id"], val["kind"], val["regime"]))
    result["daily_discovery"] = [(disc.at[k, "raw"] / disc.at[k, "slot_days"]) if k in disc.index else np.nan for k in keys]
    return result.reset_index(drop=True)


def daily_returns(frame: pd.DataFrame) -> dict:
    """Whole validation window, after 0.1 % slippage per side: the daily return on employed
    capital and on provided capital (regime/daily_return.py defines both), per strategy."""
    from regime import daily_return
    daily = pd.read_csv(daily_return.DAILY, usecols=["date", "pair", "btc_regime"])
    daily["date"] = pd.to_datetime(daily["date"], utc=True)
    daily = daily[(daily["date"] >= se.VALIDATION_START) & (daily["date"] < attribution.END)]
    slots = float(daily["btc_regime"].notna().sum())
    val = frame[(frame["open_date"] >= se.VALIDATION_START) & frame["btc_regime"].notna()].copy()
    slip = er.COST["reference_slippage_per_side"]
    val["net"] = val["profit_ratio"] - 2.0 * slip * val["leverage"]
    val["days"] = np.maximum(val["trade_duration"].astype(float), daily_return.MIN_HOLD_MINUTES) / 1440.0
    grouped = val.groupby("strategy_id").agg(net=("net", "sum"), days=("days", "sum"))
    return {s: (r["net"] / r["days"], r["net"] / slots) for s, r in grouped.iterrows()}


def measured_blocks(strategies=None):
    """Native blocks of the measured detail runs, keyed by strategy."""
    record = json.loads((ROOT / "evidence" / "EXECUTION_ROBUSTNESS.json").read_text(encoding="utf-8"))["results"]
    for strategy, rec in sorted(record.items()):
        archive = (rec.get("detail") or {}).get("archive")
        if not archive or (strategies and strategy not in strategies):
            continue
        block = er.read_block(archive, strategy)
        if block is not None:
            yield strategy, archive, block


def run(strategies=None):
    parts, archives = [], {}
    batch = {}
    phases = {"btc": [], "coin": [], "daily": []}

    def flush():
        if batch:
            table, btc, coin, daily = price(dict(batch), with_phases=True)
            parts.append(table)
            phases["btc"].append(btc)
            phases["coin"].append(coin)
            phases["daily"].append(daily)
            batch.clear()

    for strategy, archive, block in measured_blocks(strategies):
        batch[strategy] = block
        archives[strategy] = archive
        if len(batch) >= CHUNK:
            flush()
            print("priced %d strategies" % sum(len(p) for p in parts), flush=True)
    flush()
    table = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    table["detail_archive"] = table["strategy_id"].map(archives)
    table = table.sort_values("dollar_gain_usd", ascending=False).reset_index(drop=True)
    return table, {k: pd.concat([p for p in v if len(p)], ignore_index=True) for k, v in phases.items()}


def check(sample: int = 4) -> bool:
    """The same code on baseline archives must give the evaluation's own figures."""
    base = pd.read_csv(BASELINE_TABLE).set_index("strategy_id")
    manifest = json.loads((ROOT / "results" / "regime" / "full_backtest_manifest.json").read_text(encoding="utf-8"))["results"]
    names = [s for s in base.index if manifest.get(s, {}).get("status") == "measured"][:: max(1, len(base) // sample)][:sample]
    blocks = {s: er.read_block(manifest[s]["archive"], s) for s in names}
    got = price({s: b for s, b in blocks.items() if b}).set_index("strategy_id")
    ok = True
    for s in got.index:
        for column in ("trades", "dollar_gain_usd", "benchmark_dollar_gain_usd"):
            a, b = float(got.at[s, column]), float(base.at[s, column])
            same = abs(a - b) <= 1e-6 * max(1.0, abs(b))
            ok &= same
            print("%-34s %-26s %14.4f %14.4f %s" % (s, column, a, b, "ok" if same else "DIFFERS"))
    return bool(ok)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="reproduce the baseline figures on a sample")
    parser.add_argument("--strategies", default="", help="comma-separated filter")
    args = parser.parse_args(argv)
    if args.check:
        return 0 if check() else 1
    chosen = {s.strip() for s in args.strategies.split(",") if s.strip()} or None
    table, phases = run(chosen)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False, lineterminator="\n", float_format="%.12g")
    for name, file in (("btc", "detail_5m_btc_specialist_table.csv"), ("coin", "detail_5m_coin_specialist_table.csv"),
                       ("daily", "detail_5m_phase_daily.csv")):
        phases[name].to_csv(OUTDIR / file, index=False, lineterminator="\n", float_format="%.12g")
    print("wrote %s: %d strategies; phase rows btc %d, coin %d" % (OUT, len(table), len(phases["btc"]), len(phases["coin"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
