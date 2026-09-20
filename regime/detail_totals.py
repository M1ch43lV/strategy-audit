# -*- coding: utf-8 -*-
"""Validation-window totals of the 5m detail runs, beside those of the author timeframe.

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
strategy that has a measured detail run. Strategies at or below 5m have no rerun (owner rule) and
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

OUT = ROOT / "results" / "regime" / "specialist_evaluation" / "detail_5m_total_dollar_gain.csv"
BASELINE_TABLE = ROOT / "results" / "regime" / "specialist_evaluation" / "strategy_total_dollar_gain.csv"
CHUNK = 25


def price(blocks: dict) -> pd.DataFrame:
    """One row per strategy: the validation window of these native blocks, priced as the
    evaluation prices the baseline."""
    archives = [{"strategy_id": s, "trades": b.get("trades") or [], "model": "model0"}
                for s, b in blocks.items() if b.get("trades")]
    if not archives:
        return pd.DataFrame()
    frame = attribution.attribute(archives)
    leverage = {a["strategy_id"]: np.array([t.get("leverage") or 1.0 for t in a["trades"]],
                                           dtype=float) for a in archives}
    frame["leverage"] = [leverage[s][o] for s, o in zip(frame["strategy_id"], frame["trade_ordinal"])]
    cost = {s: er.validation_total(er.regime_cost_screen(part), "btc")
            for s, part in frame.groupby("strategy_id", sort=False)}
    priced = se.split_discovery_validation(se.attach_benchmark(frame))
    table = se.total_dollar_gain_table(priced)
    table["cost_mean_pct"] = table["strategy_id"].map(lambda s: cost[s]["mean_profit_pct"])
    table["cost_stressed_pct"] = table["strategy_id"].map(lambda s: cost[s]["stressed_pct"])
    return table


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


def run(strategies=None) -> pd.DataFrame:
    parts, archives = [], {}
    batch = {}

    def flush():
        if batch:
            parts.append(price(dict(batch)))
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
    return table.sort_values("dollar_gain_usd", ascending=False).reset_index(drop=True)


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
    table = run(chosen)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False, lineterminator="\n", float_format="%.12g")
    print("wrote %s: %d strategies" % (OUT, len(table)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
