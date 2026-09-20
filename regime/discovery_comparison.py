# -*- coding: utf-8 -*-
"""Does what held in the discovery window hold in the validation window?

`regime/specialist_evaluation.py` labels every trade `discovery` (opened before
2024-01-01) or `validation` and then evaluates only the validation trades, so the
discovery window has so far been dropped: nothing was selected in it and nothing was
compared with it. This module runs the *same* evaluation, unchanged, on the discovery
trades and sets the two results side by side, row by row (strategy x market phase, for
the BTC and for the coin regime).

It is descriptive. It changes no ranking, no floor and no selection; the evaluation
functions are called as they are, on a copy of the trades whose discovery rows are
relabelled so that the evaluation's window filter accepts them. The floor (5 episodes
and 10 trades) therefore applies to the discovery window exactly as it does to the
validation window.

    ./ftenv/Scripts/python.exe -m regime.discovery_comparison

Writes `results/regime/specialist_evaluation/discovery_vs_validation.csv` (one row per
strategy, kind and phase) and `discovery_vs_validation_summary.json`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from regime import specialist_evaluation as se

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "regime" / "specialist_evaluation"
STATES = ["BULL", "BEAR", "SIDEWAYS", "TRANSITION"]
KINDS = (("btc", "btc_regime", se.btc_specialist_table),
         ("coin", "coin_regime", se.coin_specialist_table))
KEEP = ["trades", "episodes", "excess_return", "tier", "episode_excess_lcb", "lcb_grade",
        "dollar_gain_usd"]


def discovery_trades(trades: pd.DataFrame) -> pd.DataFrame:
    """The discovery trades, labelled so the evaluation's own filter takes them."""
    frame = trades[trades["analysis_window"] == "discovery"].copy()
    frame["analysis_window"] = "validation"
    return frame


def paired_rows(trades: pd.DataFrame) -> pd.DataFrame:
    """One row per strategy, kind and phase, with the result of both windows."""
    disc = discovery_trades(trades)
    rows = []
    for kind, column, table_fn in KINDS:
        d = table_fn(disc)
        v = table_fn(trades)            # the evaluation's own validation result
        merged = d[["strategy_id", column] + KEEP].merge(
            v[["strategy_id", column] + KEEP], on=["strategy_id", column], how="outer",
            suffixes=("_disc", "_val"))
        merged = merged.rename(columns={column: "regime"})
        merged.insert(1, "kind", kind)
        rows.append(merged)
    frame = pd.concat(rows, ignore_index=True)
    frame["floor_disc"] = frame["tier_disc"] == "VALIDATION"
    frame["floor_val"] = frame["tier_val"] == "VALIDATION"
    return frame


def _spearman(x, y):
    from scipy import stats
    if len(x) < 8:
        return None, None
    rho, p = stats.spearmanr(x, y)
    return float(rho), float(p)


def summarize(frame: pd.DataFrame) -> dict:
    """Per kind and phase, on the rows that clear the floor in both windows."""
    out = {}
    for kind in ("btc", "coin"):
        part = frame[frame["kind"] == kind]
        for state in STATES + ["ALL"]:
            sub = part if state == "ALL" else part[part["regime"] == state]
            both = sub[sub["floor_disc"] & sub["floor_val"]]
            n_disc = int(sub["floor_disc"].sum())
            n_val = int(sub["floor_val"].sum())
            record = {"rows_floor_disc": n_disc, "rows_floor_val": n_val, "rows_both": int(len(both))}
            if len(both) >= 8:
                rho, p = _spearman(both["excess_return_disc"], both["excess_return_val"])
                pos = both[both["excess_return_disc"] > 0]
                non = both[both["excess_return_disc"] <= 0]
                top = both.nlargest(max(1, len(both) // 10), "excess_return_disc")
                lcb = both[both["episode_excess_lcb_disc"] > 0]
                record.update({
                    "spearman": rho, "spearman_p": p,
                    "disc_positive": int(len(pos)),
                    "val_positive_given_disc_positive": float((pos["excess_return_val"] > 0).mean()) if len(pos) else None,
                    "val_positive_given_disc_not_positive": float((non["excess_return_val"] > 0).mean()) if len(non) else None,
                    "val_positive_all_both": float((both["excess_return_val"] > 0).mean()),
                    "top_decile_n": int(len(top)),
                    "top_decile_val_median": float(top["excess_return_val"].median()),
                    "all_val_median": float(both["excess_return_val"].median()),
                    "disc_lcb_positive": int(len(lcb)),
                    "val_positive_given_disc_lcb_positive": float((lcb["excess_return_val"] > 0).mean()) if len(lcb) else None,
                })
            out["%s/%s" % (kind, state)] = record
    return out


def universal_pairs(frame: pd.DataFrame) -> pd.DataFrame:
    """Per strategy that clears the floor in all four coin phases in both windows: the
    median excess return over the four phases, discovery against validation."""
    coin = frame[(frame["kind"] == "coin") & frame["floor_disc"] & frame["floor_val"]]
    counts = coin.groupby("strategy_id")["regime"].nunique()
    ids = counts[counts == 4].index
    sub = coin[coin["strategy_id"].isin(ids)]
    grouped = sub.groupby("strategy_id").agg(
        median_disc=("excess_return_disc", "median"), median_val=("excess_return_val", "median"))
    return grouped.reset_index()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trades", type=Path, default=se.DEFAULT_TRADES)
    parser.add_argument("--outdir", type=Path, default=OUT)
    args = parser.parse_args(argv)
    trades = se.load_trades(args.trades, None)
    duplicates = se.duplicate_excluded_ids() & set(trades["strategy_id"])
    if duplicates:
        trades = trades[~trades["strategy_id"].isin(duplicates)]
    trades = se.attach_benchmark(trades)
    trades = se.split_discovery_validation(trades)

    frame = paired_rows(trades)
    summary = summarize(frame)
    uni = universal_pairs(frame)
    rho, p = _spearman(uni["median_disc"], uni["median_val"]) if len(uni) else (None, None)
    summary["universal"] = {"strategies": int(len(uni)), "spearman": rho, "spearman_p": p}
    summary["discovery_trades"] = int((trades["analysis_window"] == "discovery").sum())
    summary["validation_trades"] = int((trades["analysis_window"] == "validation").sum())
    summary["validation_start"] = se.VALIDATION_START.isoformat()

    args.outdir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.outdir / "discovery_vs_validation.csv", index=False, float_format="%.6g")
    (args.outdir / "discovery_vs_validation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    both = int((frame["floor_disc"] & frame["floor_val"]).sum())
    print("rows: %d, floor in discovery: %d, floor in validation: %d, both: %d" % (
        len(frame), int(frame["floor_disc"].sum()), int(frame["floor_val"].sum()), both))
    for key in ("btc/ALL", "coin/ALL"):
        print(key, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in summary[key].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
