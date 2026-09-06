"""Non-ranked, identity-checked Model 0/1/2 comparison table.

This module deliberately does not select candidates, rank strategies, or
construct the still-open exposure-matched benchmark.  It only places locked
measurements with identical windows side by side and reports transparent
mechanical deltas.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

import profile_smoke
from regime import attribution, gated_attribution, gated_backtest


ROOT = Path(__file__).resolve().parents[1]
MODEL0 = ROOT / "results" / "regime" / "full_backtest_manifest.json"
OUT = ROOT / "results" / "regime"
MODEL0_SCOPE = "canonical_pooled_native_pair_universe"
SUMMARY_FIELDS = (
    "total_trades", "trade_count_long", "trade_count_short", "profit_total",
    "profit_total_abs", "profit_factor", "expectancy", "max_drawdown_account",
    "max_drawdown_abs", "cagr", "sharpe", "sortino", "market_change",
)


def _write_json(value: dict, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _candidate_projection(manifest: dict) -> list[dict]:
    return [{key: row.get(key) for key in (
        "candidate_id", "strategy_id", "long_btc_states", "short_btc_states"
    )} for row in manifest.get("candidates", [])]


def _validate_pair(model1: dict, model2: dict) -> None:
    gated_attribution._validate_header(model1, "model1")
    gated_attribution._validate_header(model2, "model2")
    for key in ("candidate_set_id", "candidate_ids", "analysis_role", "timerange",
                "regime_daily_sha256", "eligibility_snapshot_sha256"):
        if model1.get(key) != model2.get(key):
            raise ValueError(f"Model 1 and Model 2 differ in {key}")
    if _candidate_projection(model1) != _candidate_projection(model2):
        raise ValueError("Model 1 and Model 2 differ in candidate identity or BTC gate")


def _load_model0(path: Path, source_strategies: set[str], expected_timerange: dict):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("measurement_scope") != MODEL0_SCOPE:
        raise ValueError("Model 0 measurement_scope mismatch")
    profiles = attribution.eligible_profiles()
    accepted = {}
    rejected = []
    for strategy in sorted(source_strategies):
        profile = profiles.get(strategy)
        result = (manifest.get("results") or {}).get(strategy)
        reason = ""
        mode = ("futures" if profile and profile["run_profile"].startswith("futures_")
                else "spot")
        archive_path = ROOT / result.get("archive", "") if result else ROOT
        if not profile:
            reason = "source_strategy_not_currently_eligible"
        elif not result:
            reason = "model0_not_run"
        elif result.get("status") != "measured":
            reason = f"model0_{result.get('status', 'unknown')}"
        elif result.get("measurement_scope") != MODEL0_SCOPE:
            reason = "model0_measurement_scope_mismatch"
        elif result.get("timerange") != expected_timerange[mode]:
            reason = "model0_timerange_mismatch"
        elif any(result.get(key) != value
                 for key, value in profile_smoke._identity(profile).items()):
            reason = "model0_identity_mismatch"
        elif not result.get("archive") or not archive_path.is_file():
            reason = "model0_archive_missing"
        elif attribution._file_sha(archive_path) != result.get("archive_sha256"):
            reason = "model0_archive_hash_mismatch"
        if reason:
            rejected.append({"strategy_id": strategy, "reason": reason})
            continue
        rows, archive_rejections = attribution.archive_inventory(
            ROOT, {strategy: profile}, [archive_path])
        if archive_rejections or len(rows) != 1:
            rejected.append({
                "strategy_id": strategy,
                "reason": (archive_rejections[0]["reason"] if archive_rejections
                           else "model0_archive_did_not_resolve_to_one_strategy"),
            })
            continue
        accepted[strategy] = rows[0]
    return manifest, accepted, rejected


def _metrics(record: dict) -> dict:
    summary = record["summary"]
    result = {field: summary.get(field) for field in SUMMARY_FIELDS}
    start = pd.to_datetime(summary.get("backtest_start"), utc=True)
    end = pd.to_datetime(summary.get("backtest_end"), utc=True)
    window_seconds = max((end - start).total_seconds(), 0.0)
    position_seconds = 0.0
    weighted_capital_seconds = 0.0
    for trade in summary.get("trades") or []:
        opened = pd.to_datetime(trade.get("open_date"), utc=True)
        closed = pd.to_datetime(trade.get("close_date"), utc=True)
        duration = max((closed - opened).total_seconds(), 0.0)
        position_seconds += duration
        stake = abs(float(trade.get("stake_amount") or 0.0))
        leverage = abs(float(trade.get("leverage") or 1.0))
        weighted_capital_seconds += stake * leverage * duration
    starting_balance = float(summary.get("starting_balance") or 0.0)
    mean_open_positions = position_seconds / window_seconds if window_seconds else np.nan
    capital_exposure = (weighted_capital_seconds / (starting_balance * window_seconds)
                        if starting_balance and window_seconds else np.nan)
    try:
        max_open = float(summary.get("max_open_trades_setting"))
    except (TypeError, ValueError):
        max_open = np.nan
    result.update({
        "backtest_start": start.isoformat() if not pd.isna(start) else "",
        "backtest_end": end.isoformat() if not pd.isna(end) else "",
        "position_time_days": position_seconds / 86400.0,
        "mean_open_positions": mean_open_positions,
        "slot_utilization": (mean_open_positions / max_open
                             if np.isfinite(max_open) and max_open > 0 else np.nan),
        "time_weighted_gross_capital_exposure": capital_exposure,
    })
    return result


def _comparison_rows(candidates: list[dict], model0: dict, model1: dict, model2: dict):
    long_rows = []
    wide_rows = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        strategy = candidate["strategy_id"]
        records = {
            "model0": model0.get(strategy),
            "model1": model1.get(candidate_id),
            "model2": model2.get(candidate_id),
        }
        if any(record is None for record in records.values()):
            continue
        metrics = {model: _metrics(record) for model, record in records.items()}
        for model, values in metrics.items():
            long_rows.append({"candidate_id": candidate_id,
                              "strategy_id": strategy, "model": model, **values})
        wide = {"candidate_id": candidate_id, "strategy_id": strategy}
        for model, values in metrics.items():
            for key, value in values.items():
                wide[f"{model}_{key}"] = value
        for key in SUMMARY_FIELDS + ("position_time_days", "mean_open_positions",
                                     "slot_utilization",
                                     "time_weighted_gross_capital_exposure"):
            for left, right in (("model1", "model0"), ("model2", "model1")):
                left_value, right_value = metrics[left].get(key), metrics[right].get(key)
                try:
                    wide[f"delta_{left}_minus_{right}_{key}"] = float(left_value) - float(right_value)
                except (TypeError, ValueError):
                    wide[f"delta_{left}_minus_{right}_{key}"] = np.nan
        wide_rows.append(wide)
    return pd.DataFrame(long_rows), pd.DataFrame(wide_rows)


def selftest() -> None:
    summary = {
        "backtest_start": "2024-01-01T00:00:00Z",
        "backtest_end": "2024-01-03T00:00:00Z",
        "starting_balance": 1000,
        "max_open_trades_setting": 2,
        "total_trades": 1,
        "profit_total": 0.1,
        "trades": [{"open_date": "2024-01-01T00:00:00Z",
                    "close_date": "2024-01-02T00:00:00Z",
                    "stake_amount": 100, "leverage": 1}],
    }
    values = _metrics({"summary": summary})
    assert values["position_time_days"] == 1.0
    assert values["mean_open_positions"] == 0.5
    assert values["slot_utilization"] == 0.25
    assert values["time_weighted_gross_capital_exposure"] == 0.05
    one = {"schema_version": 1, "model": "model1",
           "measurement_scope": gated_backtest.MODELS["model1"]["scope"],
           "candidate_set_id": "x", "candidate_ids": ["c"],
           "candidates": [{"candidate_id": "c", "strategy_id": "S",
                           "long_btc_states": ["BULL"], "short_btc_states": []}],
           "analysis_role": "PILOT", "timerange": {"spot": "a", "futures": "b"},
           "regime_daily_sha256": "d", "eligibility_snapshot_sha256": "e"}
    two = dict(one, model="model2",
               measurement_scope=gated_backtest.MODELS["model2"]["scope"])
    two["candidates"] = [dict(one["candidates"][0], long_coin_states=["BULL"],
                              short_coin_states=[])]
    _validate_pair(one, two)
    print("model comparison selftest: PASS")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model0", type=Path, default=MODEL0)
    parser.add_argument("--model1", type=Path, default=gated_backtest.MODELS["model1"]["output"])
    parser.add_argument("--model2", type=Path, default=gated_backtest.MODELS["model2"]["output"])
    parser.add_argument("--daily", type=Path, default=attribution.DAILY)
    parser.add_argument("--outdir", type=Path, default=OUT)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    for path in (args.model0, args.model1, args.model2, args.daily):
        if not path.is_file():
            parser.error(f"required input not found: {path}")
    model1_manifest = json.loads(args.model1.read_text(encoding="utf-8"))
    model2_manifest = json.loads(args.model2.read_text(encoding="utf-8"))
    _validate_pair(model1_manifest, model2_manifest)
    candidates = model1_manifest["candidates"]
    sources = {row["strategy_id"] for row in candidates}
    model0_manifest, model0, rejected0 = _load_model0(
        args.model0, sources, model1_manifest["timerange"])
    accepted1, rejected1, _evidence1 = gated_attribution._load_archives(
        model1_manifest, "model1", args.daily)
    accepted2, rejected2, _evidence2 = gated_attribution._load_archives(
        model2_manifest, "model2", args.daily)
    model1 = {row["analysis_id"]: row for row in accepted1}
    model2 = {row["analysis_id"]: row for row in accepted2}
    rejections = {"model0": rejected0, "model1": rejected1, "model2": rejected2}
    if any(rejections.values()) and not args.allow_partial:
        counts = {model: len(rows) for model, rows in rejections.items() if rows}
        raise SystemExit(
            "model set is incomplete; no comparison written: " +
            ", ".join(f"{key}={value}" for key, value in counts.items())
        )
    long_frame, wide_frame = _comparison_rows(candidates, model0, model1, model2)
    args.outdir.mkdir(parents=True, exist_ok=True)
    attribution._write(long_frame, args.outdir / "model_metrics_long.csv")
    attribution._write(wide_frame, args.outdir / "model_comparison.csv")
    compared = wide_frame["candidate_id"].tolist() if not wide_frame.empty else []
    payload = {
        "schema_version": 1,
        "candidate_set_id": model1_manifest.get("candidate_set_id"),
        "analysis_role": model1_manifest.get("analysis_role"),
        "candidate_ids": model1_manifest.get("candidate_ids"),
        "compared_candidate_ids": compared,
        "missing_candidate_ids": sorted(set(model1_manifest["candidate_ids"]) - set(compared)),
        "partial": any(rejections.values()),
        "rejections": rejections,
        "input_sha256": {
            "model0": attribution._file_sha(args.model0),
            "model1": attribution._file_sha(args.model1),
            "model2": attribution._file_sha(args.model2),
            "regime_daily": attribution._file_sha(args.daily),
        },
        "model0_timerange": model0_manifest.get("timerange"),
        "comparison_scope": (
            "Non-ranked mechanical Model 0/1/2 metrics and deltas. "
            "No exposure-matched benchmark, specialist threshold, or alpha claim is included."
        ),
    }
    _write_json(payload, args.outdir / "model_comparison_manifest.json")
    print(f"compared Model 0/1/2 for {len(compared)}/{len(candidates)} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
