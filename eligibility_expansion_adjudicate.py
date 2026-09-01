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
SMOKE = os.path.join(ROOT, "PROFILE_SMOKE.json")
BIAS = os.path.join(ROOT, "PROFILE_BIAS.json")

# Two admission routes, and the difference is what evidence a row needs.
#
# ZERO_WARMUP covers Wave B: the recursive analyzer refuses a strategy that
# declares no warm-up, so the row obtains a verdict only through the frozen
# adapter of plan 5.1. Because a value was supplied that the author never
# wrote, such a row additionally owes exact trade equivalence and a
# file-specific static proof.
#
# NATIVE_GATE covers Wave C: nothing was supplied and nothing was adapted. The
# row was simply never measured, and once measured it passed the original
# look-ahead and recursive gates unaided. Demanding an equivalence proof for an
# override that was never applied would not be strict, it would be incoherent.
# The checks below are the original Stage 6 rule, unrelaxed.
ZERO_WARMUP = "zero_warmup_analyzer_adapter_v1"
NATIVE_GATE = "native_gate_pass_v1"
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_ADJUDICATION.csv")
REPORT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_ADJUDICATION.md")

FIELDS = [
    "strategy_id", "run_profile", "implementation_id", "ruleset",
    "adjudication_status", "expanded_cohort", "canonical_measured",
    "canonical_observed_trades", "current_native_lookahead",
    "adapted_recursive", "recursive_source", "full_trade_equivalence",
    "static_proof",
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


def _source_identity(path, proof):
    """True when the canonical file on disk still hashes to the proof.

    `os.path.exists` is not enough. An empty `canonical_file` joins to the
    repository root, which exists as a directory, and hashing it raises rather
    than returning a mismatch. A missing path is a failed check, never a crash.
    """
    if not path or not os.path.isfile(path):
        return False
    return _sha(path) == proof.get("canonical_sha256")


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


def _row(strategy, proof, profile, baseline, ruleset, checks, observed,
         lookahead_status, recursive_status, recursive_source,
         equivalence_flag, static_flag):
    """Render one adjudicated row. Admission requires every check to hold."""
    failed = [name for name, passed in checks.items() if not passed]
    admitted = not failed
    return {
        "strategy_id": strategy,
        "run_profile": proof.get("run_profile", ""),
        "implementation_id": proof.get("implementation_id", ""),
        "ruleset": ruleset,
        "adjudication_status": "admitted_E1" if admitted else "proof_incomplete",
        "expanded_cohort": "E1_expanded_confirmatory" if admitted else "",
        "canonical_measured": "true" if checks.get("native_measurement") else "false",
        "canonical_observed_trades": observed,
        "current_native_lookahead": lookahead_status,
        "adapted_recursive": recursive_status,
        "recursive_source": recursive_source,
        "full_trade_equivalence": equivalence_flag,
        "static_proof": static_flag,
        "coverage_status": baseline.get("coverage_status", ""),
        "traps_n": baseline.get("traps_n", ""),
        "baseline_status": baseline.get("eligibility_status", ""),
        "baseline_reason": baseline.get("exclusion_reasons", ""),
        "adjudication_reason": "all frozen adapter checks passed" if admitted else
            "failed checks: " + ";".join(failed),
    }


def _bound(record, proof, profile, expected_mode):
    """True when stored evidence was produced by exactly this implementation.

    Evidence is keyed by strategy name, and a name is not an identity. A record
    counts only when the file it came from, the run profile, and the trading
    mode still match the profile being adjudicated.
    """
    return bool(record) and all([
        record.get("canonical_sha256") == proof.get("canonical_sha256"),
        record.get("canonical_sha256") == profile.get("source_sha256"),
        record.get("run_profile") == proof.get("run_profile"),
        record.get("run_profile") == profile.get("run_profile"),
        record.get("mode", expected_mode) == expected_mode,
    ])


def _adjudicate_native_gate(strategy, proof, profile, baseline, smoke, bias):
    """Wave C: the original gates, passed with no adapter involved.

    Measurement evidence deliberately comes from PROFILE_SMOKE.json rather than
    EXECUTION_PROFILES.csv. That manifest was generated before Wave C ran and
    still records these rows as unmeasured; treating its stale "false" as
    authoritative would refuse a row for the very gap the wave closed.
    """
    expected_mode = "futures" if proof.get("run_profile", "").startswith(
        "futures_") else "spot"
    measurement = smoke.get(strategy) or {}
    diagnostics = bias.get(strategy) or {}
    lookahead = diagnostics.get("lookahead") or {}
    recursive = diagnostics.get("recursive") or {}
    canonical_path = os.path.join(
        ROOT, (profile.get("canonical_file") or "").replace("/", os.sep))
    measurement_bound = _bound(measurement, proof, profile, expected_mode)
    diagnostics_bound = _bound(diagnostics, proof, profile, expected_mode)
    checks = {
        "profile_identity": profile.get("implementation_id") == proof.get(
            "implementation_id"),
        "source_identity": _source_identity(canonical_path, proof),
        "native_measurement": measurement_bound and
            measurement.get("status") == "measured" and
            _integer(measurement.get("trades")) > 0,
        "lookahead_pass": diagnostics_bound and lookahead.get("status") == "PASS",
        "recursive_pass": diagnostics_bound and recursive.get("status") == "PASS",
        "coverage_pass": baseline.get("coverage_status") == "PASS",
        "trap_free": _integer(baseline.get("traps_n")) == 0,
        "artifact_role_strategy": profile.get("artifact_role") == "strategy",
        "not_behavior_changed": profile.get("equivalence_status") != "behavior_changed",
    }
    return _row(strategy, proof, profile, baseline, NATIVE_GATE, checks,
                measurement.get("trades", "") if measurement_bound else "",
                lookahead.get("status", "NA"), recursive.get("status", "NA"),
                "native_gate", "not_applicable", "not_applicable")


def _adjudicate_zero_warmup(strategy, proof, profile, baseline, warmup,
                            lookahead, equivalence):
    """Wave B: a verdict obtainable only through the frozen zero-warm-up adapter."""
    startup = str((((proof.get("recursive_evidence") or "").split("/attempts/"))
                   + [""])[1])
    recursive = ((warmup.get(strategy) or {}).get("attempts", {}).get(startup) or {})
    current_lookahead = lookahead.get(strategy) or {}
    lookahead_result = current_lookahead.get("lookahead") or {}
    paired = equivalence.get("%s|startup=%s" % (strategy, startup)) or {}
    static = proof.get("static_proof") or {}
    canonical_path = os.path.join(
        ROOT, (profile.get("canonical_file") or "").replace("/", os.sep))
    checks = {
        "profile_identity": profile.get("implementation_id") == proof.get(
            "implementation_id"),
        "source_identity": _source_identity(canonical_path, proof),
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
    row = _row(strategy, proof, profile, baseline, ZERO_WARMUP, checks,
               baseline.get("canonical_observed_trades", ""),
               lookahead_result.get("status", "NA"),
               recursive.get("status", "NA"), "zero_warmup_adapter",
               str(paired.get("exact_semantic_trade_equivalence") is True).lower(),
               str(checks["static_proof"]).lower())
    row["canonical_measured"] = baseline.get("canonical_measured", "")
    return row


def adjudicate():
    registry = _json(PROOFS)
    eligibility = {row["strategy_id"]: row for row in _csv(ELIGIBILITY)}
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    warmup = _json(WARMUP).get("results", {})
    lookahead = _json(LOOKAHEAD).get("results", {})
    equivalence = _json(EQUIVALENCE).get("results", {})
    smoke = _json(SMOKE).get("results", {})
    bias = _json(BIAS).get("results", {})
    default_ruleset = registry.get("ruleset", ZERO_WARMUP)
    rows = []
    for strategy, proof in sorted(registry.get("strategies", {}).items()):
        baseline = eligibility.get(strategy, {})
        profile = profiles.get(strategy, {})
        ruleset = proof.get("ruleset", default_ruleset)
        if ruleset == NATIVE_GATE:
            rows.append(_adjudicate_native_gate(
                strategy, proof, profile, baseline, smoke, bias))
        elif ruleset == ZERO_WARMUP:
            rows.append(_adjudicate_zero_warmup(
                strategy, proof, profile, baseline, warmup, lookahead,
                equivalence))
        else:
            raise SystemExit("unknown ruleset for %s: %s" % (strategy, ruleset))
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
        "Two admission routes exist, and a row's route decides what evidence it",
        "owes. `zero_warmup_adapter` covers a strategy that declares no warm-up:",
        "the recursive analyzer refuses such a row outright, so a verdict exists",
        "only through the frozen adapter of plan 5.1. Because a value was supplied",
        "that the author never wrote, those rows additionally owe exact trade",
        "equivalence and a file-specific static proof. `native_gate` covers a row",
        "that was simply never measured and, once measured, passed the original",
        "gates unaided. Nothing was supplied to it, so an equivalence proof for an",
        "override that was never applied does not apply and is reported as",
        "`not_applicable` rather than as a missing proof.", "",
        "| Strategy | Status | Route | Lookahead | Recursive | Exact full trades |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| `%s` | `%s` | `%s` | `%s` | `%s` | `%s` |" % (
            row["strategy_id"], row["adjudication_status"],
            row["recursive_source"], row["current_native_lookahead"],
            row["adapted_recursive"], row["full_trade_equivalence"]))
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
    # --- native gate (Wave C) -------------------------------------------
    sha = "sha256_" + "a" * 64
    proof = {"canonical_sha256": sha, "implementation_id": "X:aaaaaaaaaaaa",
             "run_profile": "spot_long", "ruleset": NATIVE_GATE}
    profile = {"implementation_id": "X:aaaaaaaaaaaa", "source_sha256": sha,
               "run_profile": "spot_long", "artifact_role": "strategy",
               "equivalence_status": "not_applicable", "canonical_file": ""}
    baseline = {"coverage_status": "PASS", "traps_n": "0"}
    evidence = {"canonical_sha256": sha, "run_profile": "spot_long",
                "mode": "spot"}
    smoke = {"X": dict(evidence, status="measured", trades=49)}
    bias = {"X": dict(evidence, lookahead={"status": "PASS"},
                      recursive={"status": "PASS"})}

    def verdict(smoke_store=None, bias_store=None, prof=None, base=None):
        return _adjudicate_native_gate(
            "X", proof, prof or profile, base or baseline,
            smoke_store if smoke_store is not None else smoke,
            bias_store if bias_store is not None else bias)

    # source_identity cannot pass with an empty canonical_file, so a fully
    # clean row still fails on exactly that one check and nothing else.
    assert verdict()["adjudication_reason"] == "failed checks: source_identity"
    assert verdict()["recursive_source"] == "native_gate"
    # The Wave B evidence types are absent by construction, not missing.
    assert verdict()["full_trade_equivalence"] == "not_applicable"
    assert verdict()["static_proof"] == "not_applicable"

    def failed(row):
        return set(row["adjudication_reason"].split(": ")[1].split(";"))

    # A demonstrated bias on either gate is refused.
    found = {"X": dict(evidence, lookahead={"status": "FOUND"},
                       recursive={"status": "PASS"})}
    assert "lookahead_pass" in failed(verdict(bias_store=found))
    drift = {"X": dict(evidence, lookahead={"status": "PASS"},
                       recursive={"status": "FOUND"})}
    assert "recursive_pass" in failed(verdict(bias_store=drift))
    # A refusal is a FOUND too, and must never be read as a pass.
    refused = {"X": dict(evidence, lookahead={"status": "PASS"},
                         recursive={"status": "FOUND",
                                    "why": "startup_candle_count=0 refused"})}
    assert "recursive_pass" in failed(verdict(bias_store=refused))
    # Zero trades is not a measurement.
    assert "native_measurement" in failed(
        verdict(smoke_store={"X": dict(evidence, status="measured", trades=0)}))
    # Evidence from another file, profile or mode does not count as this row's.
    for wrong in ({"canonical_sha256": "sha256_" + "b" * 64},
                  {"run_profile": "futures_long"}, {"mode": "futures"}):
        stale = {"X": dict(evidence, status="measured", trades=49, **wrong)}
        assert "native_measurement" in failed(verdict(smoke_store=stale))
        assert not _bound(stale["X"], proof, profile, "spot")
    assert _bound(dict(evidence, status="measured"), proof, profile, "spot")
    # The remaining original gates still apply.
    assert "coverage_pass" in failed(
        verdict(base=dict(baseline, coverage_status="PENDING")))
    assert "trap_free" in failed(verdict(base=dict(baseline, traps_n="1")))
    assert "not_behavior_changed" in failed(
        verdict(prof=dict(profile, equivalence_status="behavior_changed")))
    assert "artifact_role_strategy" in failed(
        verdict(prof=dict(profile, artifact_role="test")))
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
