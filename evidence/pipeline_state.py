# -*- coding: utf-8 -*-
"""One canonical read path over the strategy-audit evidence stores.

The individual JSON files remain append-only provenance owned by their
respective runners.  Consumers must not infer pipeline state from any one of
them.  :class:`EvidenceStore` applies the precedence historically embedded in
``evidence.strategy_status`` and exposes the resolved measurement, Look-Ahead,
Recursive-Bias, convergence, and canonical Full-Backtest state for one
strategy.

``STRATEGY_STATUS.csv`` and ``evidence/PIPELINE_STATE.json`` are the published
read models.  The latter also contains a stage-by-stage queue summary so an
agent never needs to count raw runner stores.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime
import hashlib
import io
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "evidence", "PIPELINE_STATE.json")
STATUS_CSV = os.path.join(ROOT, "STRATEGY_STATUS.csv")

NATIVE_LOOKAHEAD_EVIDENCE = ("native", "reviewed_indicator_only")


def _json(path, key="results"):
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8") as handle:
        return (json.load(handle).get(key) or {})


def _csv(path):
    if not os.path.exists(path):
        return []
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def completed_full_backtest(profile, record):
    """Whether this exact implementation completed an accepted pooled run."""
    return bool(record) and all((
        record.get("status") == "measured",
        record.get("measurement_scope") in (
            "canonical_pooled_native_pair_universe",
            "owner_approved_timeframe_override_pooled_pair_universe",
            "owner_approved_timeframe_5m_recovery_pooled_pair_universe"),
        record.get("run_profile") == profile.get("run_profile"),
        record.get("canonical_sha256") == profile.get("source_sha256"),
    ))


class EvidenceStore:
    """Resolved view of all stores that contribute technical gate evidence."""

    def __init__(self, root=ROOT):
        self.root = root
        evidence = os.path.join(root, "evidence")
        self.paths = {
            "baseline": os.path.join(evidence, "REGIME_ELIGIBILITY.csv"),
            "profiles": os.path.join(evidence, "EXECUTION_PROFILES.csv"),
            "smoke": os.path.join(evidence, "PROFILE_SMOKE.json"),
            "bias": os.path.join(evidence, "PROFILE_BIAS.json"),
            "full_window": os.path.join(evidence, "PROFILE_FULL_WINDOW.json"),
            "convergence": os.path.join(evidence, "WARMUP_CONVERGENCE.json"),
            "wave_b": os.path.join(evidence, "ELIGIBILITY_EXPANSION_WARMUP.json"),
            "review": os.path.join(evidence, "LOOKAHEAD_INDICATOR_REVIEW.json"),
            "class1": os.path.join(evidence, "PROFILE_CLASS1.json"),
            "full_backtest": os.path.join(
                    root, "results", "regime", "full_backtest_manifest.json"),
            "execution_robustness": os.path.join(
                    evidence, "EXECUTION_ROBUSTNESS.json"),
            "cost_screen": os.path.join(evidence, "COST_SCREEN.json"),
        }
        self.repair_paths = (
            os.path.join(evidence, "ELIGIBILITY_TIMEFRAME_REPAIR.json"),
            os.path.join(evidence, "ELIGIBILITY_MODULE_REPAIR.json"),
            os.path.join(evidence, "ELIGIBILITY_SIGNATURE_REPAIR.json"),
            os.path.join(evidence, "ELIGIBILITY_FREQAI_REPAIR.json"),
            os.path.join(evidence, "ELIGIBILITY_FREQAI_WTAI.json"),
        )
        self.lookahead_paths = (
            os.path.join(evidence, "ELIGIBILITY_LOOKAHEAD_BACKFILL.json"),
            os.path.join(evidence, "ELIGIBILITY_EVIDENCE_GAP.json"),
        )

        self.baseline = {row["strategy_id"]: row
                         for row in _csv(self.paths["baseline"])}
        self.profiles = {row["strategy_id"]: row
                         for row in _csv(self.paths["profiles"])}
        self.smoke = dict(_json(self.paths["smoke"]))
        self.bias = _json(self.paths["bias"])
        self.full_window = _json(self.paths["full_window"])
        self.convergence = _json(self.paths["convergence"])
        self.wave_b = _json(self.paths["wave_b"])
        self.class1 = _json(self.paths["class1"], "strategies") or {}
        self.review = _json(self.paths["review"], "reviewed")
        full_backtest = _json(self.paths["full_backtest"])
        self.full_backtests = full_backtest
        self.execution_robustness = _json(self.paths["execution_robustness"])
        self.cost_screen = _json(self.paths["cost_screen"])

        self.repaired = {}
        self.repair_store = {}
        for path in self.repair_paths:
            for name, record in _json(path).items():
                if name not in self.repaired:
                    self.repaired[name] = record
                    self.repair_store[name] = self._relative(path)

        self.remeasured = {}
        self.remeasured_sha = {}
        self.remeasured_store = {}
        self.attempted_gate = {}
        self.attempted_store = {}
        for path in self.lookahead_paths:
            for name, record in _json(path).items():
                gate = record.get("lookahead") or {}
                if gate.get("status") in ("PASS", "FOUND"):
                    # Later stores retain the historical strategy-status
                    # precedence: a later native remeasurement replaces an
                    # earlier native remeasurement for the same row.
                    self.remeasured[name] = gate
                    self.remeasured_sha[name] = record.get("canonical_sha256")
                    self.remeasured_store[name] = self._relative(path)
                elif gate.get("status") and name not in self.attempted_gate:
                    self.attempted_gate[name] = gate
                    self.attempted_store[name] = self._relative(path)

    def _relative(self, path):
        return os.path.relpath(path, self.root).replace(os.sep, "/")

    def resolve(self, strategy_id, profile=None, baseline=None):
        """Resolve one strategy without losing raw-store provenance.

        The returned dictionary intentionally carries both public resolved
        fields and the selected raw records used by ``strategy_status``.
        ``*_attempted`` distinguishes a completed ``NA`` from a gate that was
        never run, while ``*_has_verdict`` is true only for an actual verdict.
        """
        profile = profile or self.profiles.get(strategy_id) or {}
        baseline = baseline or self.baseline.get(strategy_id) or {}
        current_rules = (self.class1.get(strategy_id, {}).get("rules") or [])

        measurement = self.smoke.get(strategy_id) or {}
        measurement_store = (self._relative(self.paths["smoke"])
                             if measurement else "")
        repair_run = self.repaired.get(strategy_id) or {}
        smoke_is_current = (
            measurement.get("status") == "measured"
            and measurement.get("class1_rules", current_rules) == current_rules)
        if repair_run.get("status") in ("measured", "failed") \
                and not smoke_is_current \
                and repair_run.get("class1_rules", current_rules) == current_rules \
                and (not measurement.get("canonical_sha256")
                     or repair_run.get("canonical_sha256")
                     == measurement.get("canonical_sha256")):
            measurement = repair_run
            measurement_store = self.repair_store.get(strategy_id, "")

        window = self.full_window.get(strategy_id) or {}
        diagnostics = self.bias.get(strategy_id) or {}
        diagnostics_store = (self._relative(self.paths["bias"])
                             if diagnostics else "")
        settled = self.convergence.get(strategy_id) or {}
        warmup = self.wave_b.get(strategy_id) or {}
        attempt = (warmup.get("attempts") or {}).get(
            str(warmup.get("latest_startup_candle_count"))) or {}

        trades, trade_evidence, trade_store = "", "", ""
        if window.get("status") == "measured":
            trades = window.get("trades", "")
            trade_evidence = "full_window"
            trade_store = self._relative(self.paths["full_window"])
        elif measurement.get("status") == "measured":
            trades = measurement.get("trades", "")
            trade_evidence = "smoke"
            trade_store = measurement_store
        elif baseline.get("canonical_measured") == "true":
            trades = baseline.get("canonical_observed_trades", "")
            trade_evidence = "baseline"
            trade_store = self._relative(self.paths["baseline"])

        gate_stores = {}
        for gate in ("lookahead", "recursive"):
            if (repair_run.get(gate) or {}).get("status") in ("PASS", "FOUND"):
                diagnostics = dict(diagnostics)
                diagnostics[gate] = repair_run[gate]
                gate_stores[gate] = self.repair_store.get(strategy_id, "")

        fresh = self.remeasured.get(strategy_id)
        tried = self.attempted_gate.get(strategy_id)
        lookahead = ((fresh or diagnostics.get("lookahead") or {}).get("status")
                     or baseline.get("lookahead") or "")
        lookahead_attempted = bool(fresh or diagnostics.get("lookahead") or tried)
        lookahead_evidence = (
            "native" if lookahead_attempted
            else (baseline.get("lookahead_evidence_source") or "missing"))
        if not lookahead and tried:
            lookahead = tried.get("status") or ""
        if fresh:
            lookahead_store = self.remeasured_store.get(strategy_id, "")
        elif diagnostics.get("lookahead"):
            lookahead_store = (gate_stores.get("lookahead") or diagnostics_store)
        elif tried:
            lookahead_store = self.attempted_store.get(strategy_id, "")
        elif baseline.get("lookahead"):
            lookahead_store = self._relative(self.paths["baseline"])
        else:
            lookahead_store = ""

        review = self.review.get(strategy_id)
        review_note = ""
        review_store = ""
        if lookahead == "FOUND" and review:
            active_sha = (self.remeasured_sha.get(strategy_id)
                          if fresh is not None
                          else diagnostics.get("canonical_sha256"))
            if active_sha and active_sha == review.get("canonical_sha256"):
                lookahead = "PASS"
                lookahead_evidence = "reviewed_indicator_only"
                review_store = self._relative(self.paths["review"])
                review_note = (
                    "lookahead reviewed: flagged column not decisive (%s, "
                    "see evidence/LOOKAHEAD_INDICATOR_REVIEW.json)"
                    % review.get("pattern", ""))

        recursive = ((diagnostics.get("recursive") or {}).get("status")
                     or baseline.get("recursive") or "")
        recursive_attempted = bool(diagnostics.get("recursive") or settled or attempt)
        if diagnostics.get("recursive"):
            recursive_evidence = "native"
            recursive_store = (gate_stores.get("recursive") or diagnostics_store)
        elif baseline.get("canonical_measured") == "true":
            recursive_evidence = "baseline"
            recursive_store = self._relative(self.paths["baseline"])
        else:
            recursive_evidence = (baseline.get("recursive_evidence_source")
                                  or "missing")
            recursive_store = (self._relative(self.paths["baseline"])
                               if baseline.get("recursive") else "")

        if recursive == "FOUND" and not diagnostics.get("recursive") \
                and not settled \
                and baseline.get("recursive_kind") == "refused_no_warmup":
            recursive = "WARMUP_NEEDED"
            recursive_evidence += ":refused_no_warmup"
        if settled.get("state") == "converged":
            drift = settled.get("max_drift_pct")
            recursive = "PASS" if (drift or 0) < 0.01 else "PASS_1PCT"
            recursive_evidence = "convergence:%s%s" % (
                settled.get("chosen_startup_candle_count"),
                "" if settled.get("needed_no_override") else ":warmup_supplied")
            recursive_store = self._relative(self.paths["convergence"])
        elif settled.get("state") == "not_converged_within_ladder":
            recursive = "FOUND"
            recursive_evidence = "convergence:not_settled"
            recursive_store = self._relative(self.paths["convergence"])
        elif settled.get("state") == "crashes_even_at_longest_rungs":
            recursive = "NA"
            recursive_evidence = "convergence:crash_exhausted"
            recursive_store = self._relative(self.paths["convergence"])
        elif attempt:
            recursive_evidence = "wave_b:%s:superseded" % (
                attempt.get("startup_candle_count"))
            recursive_store = self._relative(self.paths["wave_b"])

        full_backtest = self.full_backtests.get(strategy_id) or {}
        full_complete = completed_full_backtest(profile, full_backtest)
        robustness = self.execution_robustness.get(strategy_id) or {}
        robustness_status = robustness.get("status", "PENDING") if full_complete else "NA"
        # The cost screen needs no detail run, so it exists for every complete
        # Full-Backtest. Owner decision 2026-09-19: a cost PASS is a condition of
        # `robustness_qualified`, the condition for the verified specialist
        # designation, and (same day, later) it is judged per ADX regime state,
        # on the trades of that state only, so a specialist that is strong in one
        # state is not marked down by the weak states around it. The whole-run
        # `cost_screen_status` stays published as a description and no longer
        # gates. `NA` is not a PASS.
        cost = self.cost_screen.get(strategy_id) or {}
        cost_status = cost.get("status", "PENDING") if full_complete else "NA"
        regimes_pass = list(cost.get("cost_pass_regimes") or []) if full_complete else []
        gate_record = (fresh or tried or diagnostics.get("lookahead") or {})

        return {
            "strategy_id": strategy_id,
            "measured": (measurement.get("status") == "measured"
                         or baseline.get("canonical_measured") == "true"),
            "measurement_attempted": bool(measurement or window),
            "measurement_store": measurement_store,
            "observed_trades": trades,
            "trade_evidence": trade_evidence,
            "trade_store": trade_store,
            "lookahead": lookahead,
            "lookahead_attempted": lookahead_attempted,
            "lookahead_has_verdict": lookahead in ("PASS", "FOUND"),
            "lookahead_evidence": lookahead_evidence,
            "lookahead_store": lookahead_store,
            "lookahead_review_store": review_store,
            "recursive": recursive,
            "recursive_attempted": recursive_attempted,
            "recursive_has_verdict": recursive in ("PASS", "PASS_1PCT", "FOUND"),
            "recursive_evidence": recursive_evidence,
            "recursive_store": recursive_store,
            "full_backtest_status": full_backtest.get("status", ""),
            "technical_chain_complete": full_complete,
            "execution_robustness_status": robustness_status,
            # Necessary, not sufficient: true when the execution stage passes and at
            # least one ADX state passes the cost screen. The designation for a
            # claimed state must consult that state in `cost_screen_regimes_pass`.
            "robustness_qualified": robustness_status == "PASS" and bool(regimes_pass),
            # A PASS is either a measured 5m detail run or, at or below 5m,
            # the owner rule that counts the baseline as equal to one.
            "execution_robustness_basis": robustness.get("basis", "") if full_complete else "",
            "cost_screen_status": cost_status,
            "cost_screen_regimes_pass": ";".join(regimes_pass),
            "cost_break_even_bps": cost.get("break_even_slippage_bps_per_side", ""),
            "full_backtest_store": (self._relative(self.paths["full_backtest"])
                                    if full_backtest else ""),
            # Selected records used by the status generator. Keeping these in
            # this return value prevents it from rebuilding precedence itself.
            "measurement_record": measurement,
            "repair_record": repair_run,
            "full_window_record": window,
            "diagnostics_record": diagnostics,
            "convergence_record": settled,
            "warmup_attempt_record": attempt,
            "fresh_lookahead_record": fresh,
            "attempted_lookahead_record": tried,
            "lookahead_gate_record": gate_record,
            "lookahead_review_note": review_note,
            "full_backtest_record": full_backtest,
            "execution_robustness_record": robustness,
        }


_STAGE_ORDER = (
    ("stage_1_measurement_or_repair", frozenset((
        "first_measurement_in_current_runtime", "runtime_repair_pending",
        "to_be_fixed", "needs_a_look", "repair_attempted",
        "repair_withdrawn"))),
    ("stage_2_lookahead", frozenset((
        "lookahead_verdict", "lookahead_remeasure_pending"))),
    ("stage_3_4_convergence_or_recursive", frozenset((
        "convergence_inconclusive", "recursive_ladder_pending"))),
    ("stage_5_full_window", frozenset(("full_window_measurement_pending",))),
)


def summarize_status(rows):
    """Return mutually exclusive next-action counts plus Full-Backtest state."""
    rows = list(rows)
    next_action = collections.Counter()
    open_rows = []
    for row in rows:
        work = set(filter(None, (row.get("open_work") or "").split(";")))
        if not work:
            continue
        open_rows.append(row)
        stage = "unclassified_open_work"
        for label, markers in _STAGE_ORDER:
            if work & markers:
                stage = label
                break
        next_action[stage] += 1

    admitted = [row for row in rows if row.get("cohort") == "E1_expanded"]
    full = collections.Counter(
        row.get("full_backtest_status") or "missing" for row in admitted)
    complete = sum(row.get("technical_chain_complete") == "true"
                   for row in admitted)
    measured_stale = sum(
        row.get("full_backtest_status") == "measured"
        and row.get("technical_chain_complete") != "true"
        for row in admitted)
    closed_without_archive = sum(
        row.get("full_backtest_status") in (
            "oom_confirmed", "performance_limited", "stake_overflow_confirmed",
            "failed", "resource_inconclusive", "timeout")
        for row in admitted)
    return {
        "total_strategies": len(rows),
        "cohorts": dict(sorted(collections.Counter(
            row.get("cohort") or "missing" for row in rows).items())),
        "technical_chain": {
            "open_strategies": len(open_rows),
            "next_action": dict(next_action),
        },
        "full_backtest_for_admitted": {
            "admitted_strategies": len(admitted),
            "identity_current_complete": complete,
            "measured_but_identity_stale": measured_stale,
            "closed_without_complete_archive": closed_without_archive,
            "status": dict(sorted(full.items())),
        },
    }


def _public_resolution(resolved):
    return {
        "measurement": {
            "attempted": resolved["measurement_attempted"],
            "measured": resolved["measured"],
            "observed_trades": resolved["observed_trades"],
            "trade_evidence": resolved["trade_evidence"],
            "producer_store": resolved["trade_store"],
            "selected_measurement_store": resolved["measurement_store"],
        },
        "lookahead": {
            "attempted": resolved["lookahead_attempted"],
            "has_verdict": resolved["lookahead_has_verdict"],
            "status": resolved["lookahead"],
            "evidence": resolved["lookahead_evidence"],
            "producer_store": resolved["lookahead_store"],
            "review_store": resolved["lookahead_review_store"],
        },
        "recursive": {
            "attempted": resolved["recursive_attempted"],
            "has_verdict": resolved["recursive_has_verdict"],
            "status": resolved["recursive"],
            "evidence": resolved["recursive_evidence"],
            "producer_store": resolved["recursive_store"],
        },
        "full_backtest": {
            "status": resolved["full_backtest_status"],
            "identity_current_complete": resolved["technical_chain_complete"],
            "producer_store": resolved["full_backtest_store"],
        },
        "execution_robustness": {
            "status": resolved["execution_robustness_status"],
            "basis": resolved["execution_robustness_basis"],
            "producer_store": "evidence/EXECUTION_ROBUSTNESS.json",
        },
        # Both components are published above and below; this is their conjunction.
        "robustness_qualification": {
            "qualified": resolved["robustness_qualified"],
            "requires": ["execution_robustness:PASS",
                         "cost_screen:PASS in the claimed ADX regime state"],
            "note": "at the strategy level: PASS in at least one state",
        },
        "cost_screen": {
            "status": resolved["cost_screen_status"],
            "scope_of_status": "whole run, descriptive; does not gate",
            "regimes_pass": [x for x in resolved["cost_screen_regimes_pass"].split(";") if x],
            "regimes_pass_window": "validation window from 2024-01-01, the specialist "
                                   "evaluation's VALIDATION_START",
            "break_even_slippage_bps_per_side": resolved["cost_break_even_bps"],
            "producer_store": "evidence/COST_SCREEN.json",
        },
    }


def document(rows, generated_at=None, evidence_store=None):
    """Build the canonical machine-readable read model from resolved rows."""
    rows = list(rows)
    store = evidence_store or EvidenceStore(ROOT)
    strategies = {}
    for row in rows:
        strategy_id = row["strategy_id"]
        enriched = dict(row)
        enriched["evidence_resolution"] = _public_resolution(store.resolve(
            strategy_id, store.profiles.get(strategy_id),
            store.baseline.get(strategy_id)))
        strategies[strategy_id] = enriched
    return {
        "schema_version": 1,
        "generated_at": generated_at or datetime.datetime.now().replace(
            microsecond=0).isoformat(),
        "authority": "generated_read_model_not_a_verdict_store",
        "raw_store_policy": (
            "Raw evidence stores retain provenance and writer ownership; "
            "read pipeline-wide state only from this file or STRATEGY_STATUS.csv."),
        "summary": summarize_status(rows),
        "strategies": strategies,
    }


def write_document(rows, path=OUTPUT, generated_at=None):
    payload = document(rows, generated_at=generated_at)
    temporary = path + ".tmp"
    with io.open(temporary, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)
    return payload


def selftest(root=ROOT):
    """Assert the accessor reproduces every published resolved evidence field."""
    store = EvidenceStore(root)
    status_path = os.path.join(root, "STRATEGY_STATUS.csv")
    published = {row["strategy_id"]: row for row in _csv(status_path)}
    assert set(store.profiles) == set(published), (
        len(store.profiles), len(published))
    checked = 0
    for strategy_id, profile in store.profiles.items():
        resolved = store.resolve(strategy_id, profile,
                                 store.baseline.get(strategy_id) or {})
        row = published[strategy_id]
        expected = {
            "measured": "true" if resolved["measured"] else "false",
            "observed_trades": str(resolved["observed_trades"]),
            "trade_evidence": resolved["trade_evidence"],
            "lookahead": resolved["lookahead"],
            "lookahead_evidence": resolved["lookahead_evidence"],
            "recursive": resolved["recursive"],
            "recursive_evidence": resolved["recursive_evidence"],
            "full_backtest_status": resolved["full_backtest_status"],
            "technical_chain_complete": (
                "true" if resolved["technical_chain_complete"] else "false"),
        }
        actual = {key: row.get(key, "") for key in expected}
        assert actual == expected, (strategy_id, actual, expected)
        checked += 1
    print("pipeline state selftest: PASS (%d strategies)" % checked)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    rows = _csv(STATUS_CSV)
    summary = summarize_status(rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
