# -*- coding: utf-8 -*-
"""Adjudicate expansion proofs without mutating the frozen Stage 6 table."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
PROOFS = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_PROOFS.json")
ELIGIBILITY = os.path.join(ROOT, "REGIME_ELIGIBILITY.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
WARMUP = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_WARMUP.json")
LOOKAHEAD = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_LOOKAHEAD.json")
EQUIVALENCE = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_EQUIVALENCE.json")
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_ADJUDICATION.csv")
REPORT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_ADJUDICATION.md")

FIELDS = [
    "strategy_id", "run_profile", "implementation_id", "ruleset",
    "adjudication_status", "expanded_cohort", "canonical_measured",
    "canonical_observed_trades", "current_native_lookahead",
    "adapted_recursive", "full_trade_equivalence", "static_proof",
    "coverage_status", "traps_n", "baseline_status", "baseline_reason",
    "adjudication_reason",
]


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _json(path):
    return json.load(io.open(path, encoding="utf-8"))


def _sha(path):
    return "sha256_" + hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def _integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _static_proof_ok(static, startup):
    """Accept a proof only when no decision reaches below the adapter boundary.

    Plan 5.1 condition 6 requires independence from history *below* the adapter
    boundary, which is not the same as having no history at all. A strategy
    whose longest finite lookback fits inside its startup value satisfies the
    condition; an unbounded, stateful or recursively smoothed dependency never
    does, because no finite warm-up makes it exact.
    """
    fields = ("entry_history_dependency", "exit_history_dependency",
              "indicator_history_dependency")
    values = [str(static.get(key, "")) for key in fields]
    if all(value.startswith("none;") for value in values):
        return True
    if not all(value.startswith(("none;", "bounded;")) for value in values):
        return False
    bound = static.get("max_history_lookback_candles")
    return (isinstance(bound, int) and bound > 0 and
            _integer(startup) > 0 and bound <= _integer(startup))


def adjudicate():
    registry = _json(PROOFS)
    eligibility = {row["strategy_id"]: row for row in _csv(ELIGIBILITY)}
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    warmup = _json(WARMUP).get("results", {})
    lookahead = _json(LOOKAHEAD).get("results", {})
    equivalence = _json(EQUIVALENCE).get("results", {})
    rows = []
    for strategy, proof in sorted(registry.get("strategies", {}).items()):
        baseline = eligibility.get(strategy, {})
        profile = profiles.get(strategy, {})
        startup = str((((proof.get("recursive_evidence") or "").split("/attempts/"))
                       + [""])[1])
        recursive = ((warmup.get(strategy) or {}).get("attempts", {}).get(startup) or {})
        current_lookahead = (lookahead.get(strategy) or {})
        lookahead_result = current_lookahead.get("lookahead") or {}
        equivalence_key = "%s|startup=%s" % (strategy, startup)
        paired = equivalence.get(equivalence_key) or {}
        static = proof.get("static_proof") or {}
        canonical_path = os.path.join(
            ROOT, (profile.get("canonical_file") or "").replace("/", os.sep))
        checks = {
            "profile_identity": profile.get("implementation_id") == proof.get(
                "implementation_id"),
            "source_identity": bool(canonical_path and os.path.exists(canonical_path)) and
                _sha(canonical_path) == proof.get("canonical_sha256"),
            "native_measurement": baseline.get("canonical_measured") == "true" and
                _integer(baseline.get("canonical_observed_trades")) > 0,
            "lookahead_pass": lookahead_result.get("status") == "PASS" and
                current_lookahead.get("canonical_sha256") == proof.get("canonical_sha256") and
                current_lookahead.get("run_profile") == proof.get("run_profile"),
            "recursive_pass": recursive.get("status") == "PASS" and
                recursive.get("canonical_sha256") == proof.get("canonical_sha256") and
                recursive.get("implementation_id") == proof.get("implementation_id"),
            "trade_equivalence": paired.get("exact_semantic_trade_equivalence") is True and
                paired.get("implementation_id") == proof.get("implementation_id") and
                (paired.get("original") or {}).get("trades_sha256") ==
                (paired.get("override") or {}).get("trades_sha256"),
            "static_proof": _static_proof_ok(static, startup),
            "coverage_pass": baseline.get("coverage_status") == "PASS",
            "trap_free": _integer(baseline.get("traps_n")) == 0,
            "not_behavior_changed": profile.get("equivalence_status") != "behavior_changed",
        }
        failed = [name for name, passed in checks.items() if not passed]
        admitted = not failed
        rows.append({
            "strategy_id": strategy,
            "run_profile": proof.get("run_profile", ""),
            "implementation_id": proof.get("implementation_id", ""),
            "ruleset": registry.get("ruleset", ""),
            "adjudication_status": "admitted_E1" if admitted else "proof_incomplete",
            "expanded_cohort": "E1_expanded_confirmatory" if admitted else "",
            "canonical_measured": baseline.get("canonical_measured", ""),
            "canonical_observed_trades": baseline.get("canonical_observed_trades", ""),
            "current_native_lookahead": lookahead_result.get("status", "NA"),
            "adapted_recursive": recursive.get("status", "NA"),
            "full_trade_equivalence": str(paired.get(
                "exact_semantic_trade_equivalence") is True).lower(),
            "static_proof": str(checks["static_proof"]).lower(),
            "coverage_status": baseline.get("coverage_status", ""),
            "traps_n": baseline.get("traps_n", ""),
            "baseline_status": baseline.get("eligibility_status", ""),
            "baseline_reason": baseline.get("exclusion_reasons", ""),
            "adjudication_reason": "all frozen adapter checks passed" if admitted else
                "failed checks: " + ";".join(failed),
        })
    return rows


def _csv_bytes(rows):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def _report(rows):
    admitted = [row for row in rows if row["adjudication_status"] == "admitted_E1"]
    lines = [
        "# Eligibility expansion adjudication", "",
        "This report overlays new prospective evidence without rewriting the frozen",
        "67-row E0 result in `REGIME_ELIGIBILITY.csv`.", "",
        "| Strategy | Status | Lookahead | Recursive adapter | Exact full trades |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| `%s` | `%s` | `%s` | `%s` | `%s` |" % (
            row["strategy_id"], row["adjudication_status"],
            row["current_native_lookahead"], row["adapted_recursive"],
            row["full_trade_equivalence"]))
    lines.extend([
        "", "Current E1 count: **%d** = 67 frozen E0 profiles + %d newly "
        "adjudicated profile(s)." % (67 + len(admitted), len(admitted)), "",
        "Admission here does not start Stage 9 or inspect regime rankings. Newly",
        "admitted profiles still require identity-bound pooled Stage 7 attribution",
        "before they can contribute to the expanded regime analysis.", "",
    ])
    return "\n".join(lines).encode("utf-8")


def _write(path, content):
    tmp = path + ".tmp"
    with io.open(tmp, "wb") as handle:
        handle.write(content)
    os.replace(tmp, path)


def selftest():
    assert _integer("3") == 3
    assert _integer("") == 0
    none_proof = {"entry_history_dependency": "none; constant",
                  "exit_history_dependency": "none; constant",
                  "indicator_history_dependency": "none; constant"}
    assert _static_proof_ok(none_proof, "1")
    bounded = {"entry_history_dependency": "bounded; one-row shift",
               "exit_history_dependency": "none; no exit signal",
               "indicator_history_dependency": "bounded; rolling window 40",
               "max_history_lookback_candles": 40}
    assert _static_proof_ok(bounded, "40")
    # A bound wider than the warm-up reaches below the boundary.
    assert not _static_proof_ok(dict(bounded, max_history_lookback_candles=41), "40")
    # An unbounded or recursive dependency is never provable this way.
    assert not _static_proof_ok(
        dict(bounded, indicator_history_dependency="unbounded; EMA is recursive"), "40")
    # A bounded claim without a stated numeric bound is not a proof.
    assert not _static_proof_ok(
        {k: v for k, v in bounded.items() if k != "max_history_lookback_candles"}, "40")
    print("eligibility_expansion_adjudicate selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    rows = adjudicate()
    rendered = {OUTPUT: _csv_bytes(rows), REPORT: _report(rows)}
    if args.check:
        stale = [path for path, content in rendered.items()
                 if not os.path.exists(path) or io.open(path, "rb").read() != content]
        if stale:
            for path in stale:
                print("stale: %s" % os.path.relpath(path, ROOT))
            return 1
        print("eligibility expansion adjudication: current")
        return 0
    for path, content in rendered.items():
        _write(path, content)
    for row in rows:
        print("%s: %s" % (row["strategy_id"], row["adjudication_status"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
