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
strategy, kind and phase), `discovery_vs_validation_summary.json` and
`universal_confirmation.csv`.

Confirmation (frozen 2026-09-20, REGIME_PREREGISTRATION.md, "Amendment 2026-09-20"): a
strategy in a phase is *confirmed* when it clears the floor in both windows and the
one-sided 95 % lower confidence bound of its episode excess return (`episode_excess_lcb`)
is above 0 in both. Its *confirmation score* is the smaller of the two bounds, the weakest
link; the score says nothing about similarity, so equally poor results earn nothing. For a
universal candidate (all four coin phases at VALIDATION tier) the strict rule is: confirmed
in all four phases. Where that does not hold, the milder rule applies: better than
Buy-and-Hold in both windows (excess above 0, floor in both) in at least three of the four
phases. The label reports the strongest rule that holds, `strict`, `mild` or `none`; the
universal score is the score of its weakest phase.
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
# The confirmation rule. Frozen in the amendment named in the docstring; change it there first.
CONFIRM_LCB_MIN = 0.0            # both lower confidence bounds must exceed this
UNIVERSAL_MILD_PHASES = 3        # milder rule: better than Buy-and-Hold in both windows in this many of 4


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
    both = frame["floor_disc"] & frame["floor_val"]
    frame["confirmation_score"] = np.where(
        both, np.fmin(frame["episode_excess_lcb_disc"], frame["episode_excess_lcb_val"]), np.nan)
    frame["confirmed"] = both & (frame["confirmation_score"] > CONFIRM_LCB_MIN)
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


def universal_confirmation(frame: pd.DataFrame, universal_ids) -> pd.DataFrame:
    """Per universal candidate: the strongest confirmation rule that holds, and its score."""
    coin = frame[(frame["kind"] == "coin") & frame["strategy_id"].isin(set(universal_ids))]
    rows = []
    for strategy, part in coin.groupby("strategy_id"):
        both = part["floor_disc"] & part["floor_val"]
        positive = both & (part["excess_return_disc"] > 0) & (part["excess_return_val"] > 0)
        confirmed = int(part["confirmed"].sum())
        scores = part["confirmation_score"]
        if confirmed == 4:
            rule = "strict"
        elif int(positive.sum()) >= UNIVERSAL_MILD_PHASES:
            rule = "mild"
        else:
            rule = "none"
        rows.append({"strategy_id": strategy, "phases_floor_both": int(both.sum()),
                     "phases_confirmed": confirmed, "phases_better_in_both": int(positive.sum()),
                     "rule": rule,
                     "score": float(scores.min()) if len(scores) == 4 and scores.notna().all() else np.nan})
    return pd.DataFrame(rows, columns=["strategy_id", "phases_floor_both", "phases_confirmed",
                                       "phases_better_in_both", "rule", "score"])


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

    universal_path = args.outdir / "universal_strategies.csv"
    universal_ids = pd.read_csv(universal_path)["strategy_id"] if universal_path.is_file() else []
    confirmation = universal_confirmation(frame, universal_ids)
    summary["confirmation"] = {
        "confirmed_rows": {kind: int(frame[(frame["kind"] == kind) & frame["confirmed"]].shape[0])
                           for kind in ("btc", "coin")},
        "universal": {rule: int((confirmation["rule"] == rule).sum())
                      for rule in ("strict", "mild", "none")},
        "rule": {"lcb_min": CONFIRM_LCB_MIN, "universal_mild_phases": UNIVERSAL_MILD_PHASES},
    }
    args.outdir.mkdir(parents=True, exist_ok=True)
    confirmation.to_csv(args.outdir / "universal_confirmation.csv", index=False, float_format="%.6g")
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
