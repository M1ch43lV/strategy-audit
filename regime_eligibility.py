# -*- coding: utf-8 -*-
"""Build the preregistered technical eligibility table for regime analysis.

This stage never uses profit, significance, market return, or source taxonomy.
It distinguishes a demonstrated technical failure from a diagnostic that has
not yet been run in the canonical execution profile.
"""
from __future__ import annotations

import argparse
import collections
import csv
import io
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
LEDGER = os.path.join(ROOT, "LEDGER.csv")
COVERAGE = os.path.join(ROOT, "REGIME_COVERAGE.csv")
OUTPUT = os.path.join(ROOT, "REGIME_ELIGIBILITY.csv")
REPORT = os.path.join(ROOT, "REGIME_ELIGIBILITY.md")

FIELDS = [
    "strategy_id", "run_profile", "implementation_id", "canonical_file",
    "canonical_population", "repair_class", "equivalence_status",
    "artifact_role", "canonical_measured", "canonical_observed_trades",
    "trade_evidence_source", "validated_modes", "lookahead", "recursive",
    "recursive_kind", "traps_n", "coverage_status", "coverage_evidence",
    "regime_eligible", "eligibility_status",
    "exclusion_reasons", "pending_reasons", "coverage_policy",
]


def _read_csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def classify(profile, ledger, coverage=None):
    hard = []
    pending = []
    coverage = coverage or {}
    run_profile = profile["run_profile"]
    expected_mode = "futures" if run_profile.startswith("futures_") else "spot"
    measured = profile["canonical_measured"] == "true"
    trades = _integer(profile.get("canonical_observed_trades"))
    trade_source = profile.get("trade_evidence_source", "")

    if run_profile == "unknown":
        pending.append("execution_profile_unresolved")
    if profile.get("artifact_role") != "strategy":
        pending.append("artifact_role_requires_review")
    if not measured:
        hard.append("canonical_implementation_not_measured")
    elif trades == 0:
        if trade_source == "runtime_smoke":
            pending.append("zero_trades_in_smoke_requires_full_window")
        else:
            hard.append("no_trades_in_full_measurement")

    if expected_mode not in set(filter(None, profile.get("validated_modes", "").split(";"))):
        pending.append("native_mode_not_runtime_validated")

    equivalence = profile.get("equivalence_status")
    if equivalence == "behavior_changed":
        hard.append("behavior_changed_primary_exclusion")
    elif equivalence == "output_equivalent":
        pending.append("output_equivalent_requires_canonical_bias_rerun")

    lookahead = ledger.get("lookahead", "NA") or "NA"
    recursive = ledger.get("recursive", "NA") or "NA"
    traps_n = _integer(ledger.get("traps_n"))
    if lookahead == "FOUND":
        hard.append("lookahead_found")
    elif lookahead != "PASS":
        pending.append("lookahead_not_completed")
    if recursive == "FOUND":
        hard.append("recursive_bias_found")
    elif recursive != "PASS":
        pending.append("recursive_bias_not_completed")
    if traps_n:
        hard.append("technical_trap_found")

    coverage_status = (coverage.get("coverage_status") or "PENDING").upper()
    if coverage_status == "FAIL":
        hard.append("exact_regime_window_coverage_failed")
    elif coverage_status != "PASS":
        pending.append("exact_regime_window_coverage_not_verified")

    # The historical bias diagnostics were spot runs. Futures candidates must
    # be checked in their native mode even if a historical spot field says PASS.
    if expected_mode == "futures" and measured:
        pending.append("futures_mode_bias_diagnostics_not_completed")

    hard = list(dict.fromkeys(hard))
    pending = list(dict.fromkeys(pending))
    if hard:
        status = "sensitivity_only" if hard == ["behavior_changed_primary_exclusion"] else "ineligible"
    elif pending:
        status = "pending_diagnostics"
    else:
        status = "eligible"

    return {
        "strategy_id": profile["strategy_id"],
        "run_profile": run_profile,
        "implementation_id": profile["implementation_id"],
        "canonical_file": profile["canonical_file"],
        "canonical_population": profile["canonical_population"],
        "repair_class": profile["repair_class"],
        "equivalence_status": equivalence,
        "artifact_role": profile["artifact_role"],
        "canonical_measured": profile["canonical_measured"],
        "canonical_observed_trades": profile.get("canonical_observed_trades", ""),
        "trade_evidence_source": trade_source,
        "validated_modes": profile.get("validated_modes", ""),
        "lookahead": lookahead,
        "recursive": recursive,
        "recursive_kind": ledger.get("recursive_kind", ""),
        "traps_n": traps_n,
        "coverage_status": coverage_status,
        "coverage_evidence": coverage.get("coverage_evidence", ""),
        "regime_eligible": str(status == "eligible").lower(),
        "eligibility_status": status,
        "exclusion_reasons": ";".join(hard),
        "pending_reasons": ";".join(pending),
        "coverage_policy": "pair_available_history;verify_exact_regime_window_before_run",
    }


def build(profile_path=PROFILES, ledger_path=LEDGER, coverage_path=COVERAGE):
    profiles = _read_csv(profile_path)
    ledger = {row["strategy"]: row for row in _read_csv(ledger_path)}
    coverage_rows = _read_csv(coverage_path) if os.path.exists(coverage_path) else []
    coverage = {(row["strategy_id"], row["run_profile"]): row for row in coverage_rows}
    return [classify(row, ledger.get(row["strategy_id"], {}),
                     coverage.get((row["strategy_id"], row["run_profile"]), {}))
            for row in profiles]


def _write_csv(rows, path):
    tmp = path + ".tmp"
    with io.open(tmp, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def _table(counter):
    return "\n".join("| `%s` | %d |" % item for item in sorted(counter.items()))


def _write_report(rows, path):
    statuses = collections.Counter(row["eligibility_status"] for row in rows)
    for name in ("eligible", "pending_diagnostics", "ineligible"):
        statuses.setdefault(name, 0)
    profiles = collections.Counter(row["run_profile"] for row in rows)
    exclusions = collections.Counter(
        reason for row in rows for reason in row["exclusion_reasons"].split(";") if reason)
    pending = collections.Counter(
        reason for row in rows for reason in row["pending_reasons"].split(";") if reason)
    text = """# Regime eligibility — technical Stage 6

This table is keyed by `strategy_id × run_profile` and uses the single
canonical implementation selected in `EXECUTION_PROFILES.csv`. It is frozen
before any regime-performance ranking. Here, eligibility means admission to
the Stage 7 regime backtests; it is not approval for live trading.

## Rule

`regime_eligible=true` requires all of the following:

1. the canonical implementation was measured in its native mode;
2. a full measurement produced trades (a zero-trade smoke is pending, not a
   final no-trade exclusion);
3. look-ahead and recursive-bias diagnostics passed;
4. exact pair/candle coverage of the frozen regime window passed;
5. no published technical trap was found;
6. the canonical implementation is not `behavior_changed`;
7. `output_equivalent` overlays have canonical bias reruns before admission.

Profit, significance, buy-and-hold performance, source archetype, and cluster
membership are deliberately absent. `pending_diagnostics` means evidence is
missing; it does not mean pass or fail. Futures PASS values are not inherited
from historical spot diagnostics.

Coverage uses available pair history, matching the existing audit. Exact pair
and candle coverage for the frozen regime window is a hard Stage 7 precondition.
Until `REGIME_COVERAGE.csv` supplies a `PASS` for a strategy/run-profile row,
that row remains `pending_diagnostics` rather than being called eligible.
At the current checkpoint, 22 rows pass every gate other than this coverage
check; that is a workload count, not an eligibility result.

The coverage input schema is `strategy_id,run_profile,coverage_status,coverage_evidence`.
`coverage_status` is `PASS`, `FAIL`, or `PENDING`; evidence should identify the
pair/timerange completeness check that produced the status.

## Current status

| Status | Strategies |
|---|---:|
%s

## Native run profiles

| Run profile | Strategies |
|---|---:|
%s

## Exclusion reasons

Reasons are non-exclusive.

| Reason | Strategies |
|---|---:|
%s

## Pending reasons

Reasons are non-exclusive and are counted across all rows. A row already
excluded by one hard failure may still record a missing, orthogonal diagnostic;
hard exclusion takes precedence over pending status. The same diagnostic
cannot be both failed and pending on one row.

| Reason | Strategies |
|---|---:|
%s

The machine-readable row-level record is `REGIME_ELIGIBILITY.csv`.
""" % (_table(statuses), _table(profiles), _table(exclusions), _table(pending))
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(tmp, path)


def selftest():
    base = {
        "strategy_id": "A", "run_profile": "spot_long", "implementation_id": "A:1",
        "canonical_file": "A.py", "canonical_population": "original", "repair_class": "",
        "equivalence_status": "not_applicable", "artifact_role": "strategy",
        "canonical_measured": "true", "canonical_observed_trades": "10",
        "trade_evidence_source": "historical_ledger", "validated_modes": "spot",
    }
    coverage = {"coverage_status": "PASS", "coverage_evidence": "selftest"}
    passed = classify(base, {"lookahead": "PASS", "recursive": "PASS", "traps_n": "0"}, coverage)
    assert passed["eligibility_status"] == "eligible"
    failed = classify(base, {"lookahead": "FOUND", "recursive": "PASS", "traps_n": "0"}, coverage)
    assert failed["eligibility_status"] == "ineligible"
    smoke = dict(base, canonical_observed_trades="0", trade_evidence_source="runtime_smoke")
    assert classify(smoke, {"lookahead": "NA", "recursive": "NA"})["eligibility_status"] == "pending_diagnostics"
    assert classify(base, {"lookahead": "PASS", "recursive": "PASS"})["eligibility_status"] == "pending_diagnostics"
    print("regime_eligibility selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default=PROFILES)
    parser.add_argument("--ledger", default=LEDGER)
    parser.add_argument("--coverage", default=COVERAGE)
    parser.add_argument("--output", default=OUTPUT)
    parser.add_argument("--report", default=REPORT)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    rows = build(args.profiles, args.ledger, args.coverage)
    _write_csv(rows, args.output)
    _write_report(rows, args.report)
    counts = collections.Counter(row["eligibility_status"] for row in rows)
    print("regime eligibility rows: %d" % len(rows))
    for name, count in sorted(counts.items()):
        print("  %-22s %d" % (name, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
