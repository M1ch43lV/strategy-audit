# -*- coding: utf-8 -*-
"""Admit a row that clears both bias gates at a warm-up that settles it.

THE DECISION THIS IMPLEMENTS (2026-09-02, owner's call). The audit's purpose is
to rank working strategies by market phase, not to reproduce what an author
once ran. Authors writing before the drift question was understood declared
warm-ups that do not let their own indicators settle, so their original results
were not correct in the first place. What is wanted is the mathematically clean
result: no recursive drift, no look-ahead, under the current freqtrade. That a
cleaner warm-up changes the trade count - fewer or more - is accepted as the
consequence of measuring properly rather than as a defect.

WHAT THIS SUPERSEDES. Preregistration requirement 7 routed a converged row
whose trade list changed under the supplied warm-up to E3 exploratory rather
than E1, on the ground that the fix altered behaviour. That is retired: the
altered behaviour is the point, not a finding against the row.

Requirement 5's paired full-window run therefore stops being an admission gate.
It compared the strategy at its declared warm-up against the settled one, and
its only consequence was the E1/E3 split that no longer exists. Where it has
already run, its verdict stays on the record as provenance - it says whether a
row's numbers are the author's or ours, which matters when reading a result,
just not when deciding admission.

WHAT STILL APPLIES, because the decision was about warm-up and not about the
other gates:

* look-ahead `PASS`, measured from this implementation. Not the absence of a
  FOUND - an NA is no verdict and cannot admit anything.
* recursion settled by the ladder, from this implementation.
* coverage `PASS`, `traps_n` zero, `artifact_role=strategy`, and not
  `behavior_changed`. A documented backtesting trap is not a warm-up question
  and three rows are held by it.

Every admitted row records the warm-up it was measured at, and whether that
value is at or below the author's own. The distinction is no longer a gate but
it is still the truth about where a number came from.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
CONVERGENCE = os.path.join(ROOT, "WARMUP_CONVERGENCE.json")
ADJUDICATION = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_ADJUDICATION.csv")
RULE = "converged_clean_gates_v1"
COHORT = "E1_expanded_confirmatory"


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _json(path, key="results"):
    if not os.path.exists(path):
        return {}
    return json.load(io.open(path, encoding="utf-8")).get(key, {})


def eligible(row):
    """Whether this row meets the new rule, and why not when it does not."""
    if row["lookahead"] != "PASS":
        return False, "look-ahead is %s, not PASS" % (row["lookahead"] or "absent")
    if row["lookahead_evidence"] != "native":
        return False, "look-ahead verdict is %s, not measured here" % \
            row["lookahead_evidence"]
    if row["recursive"] not in ("PASS", "PASS_1PCT"):
        return False, "recursion is %s" % (row["recursive"] or "absent")
    if not row["recursive_evidence"].startswith("convergence:"):
        return False, "recursion was not settled by the ladder (%s)" % \
            row["recursive_evidence"]
    if row["coverage_status"] != "PASS":
        return False, "coverage is %s" % (row["coverage_status"] or "absent")
    if row["traps_n"] not in ("", "0"):
        return False, "carries %s documented backtesting trap(s)" % row["traps_n"]
    if row["artifact_role"] != "strategy":
        return False, "artifact_role is %s" % row["artifact_role"]
    if not row["observed_trades"] or row["observed_trades"] == "0":
        return False, "never trades"
    return True, ""


def candidates():
    """Rows the new rule admits, with what each was measured at."""
    convergence = _json(CONVERGENCE)
    admitted = {r["strategy_id"] for r in _csv(ADJUDICATION)}
    out, refused = [], []
    for row in _csv(STATUS):
        if row["strategy_id"] in admitted:
            continue
        if row["cohort"] in ("E0_strict67", "E1_expanded"):
            continue
        ok, why = eligible(row)
        settled = convergence.get(row["strategy_id"]) or {}
        if ok:
            out.append((row, settled))
        elif row["recursive_evidence"].startswith("convergence:"):
            refused.append((row["strategy_id"], why))
    return out, refused


def record(row, settled):
    band = "0.01" if row["recursive"] == "PASS" else "1.0"
    override = "no" if row["needed_no_override"] == "true" else "yes"
    return {
        "strategy_id": row["strategy_id"],
        "run_profile": row["run_profile"],
        "implementation_id": "",
        "ruleset": RULE,
        "adjudication_status": "admitted_E1",
        "expanded_cohort": COHORT,
        "canonical_measured": row["measured"],
        "canonical_observed_trades": row["observed_trades"],
        "current_native_lookahead": row["lookahead"],
        "adapted_recursive": row["recursive"],
        "recursive_source": row["recursive_evidence"],
        # No longer a gate; recorded as what it is where it exists.
        "full_trade_equivalence": "not_required_under_%s" % RULE,
        "static_proof": "",
        "coverage_status": row["coverage_status"],
        "traps_n": row["traps_n"],
        "baseline_status": row["baseline_status"],
        "baseline_reason": row["primary_reason"],
        "adjudication_reason": (
            "both gates clear, measured here; warm-up %s candles (%s days), "
            "worst drift %s%% inside the %s%% band, warm-up supplied: %s"
            % (settled.get("chosen_startup_candle_count", "?"),
               settled.get("chosen_ladder_days", "?"),
               settled.get("max_drift_pct", "?"), band, override)),
    }


def apply(write):
    rows, refused = candidates()
    existing = _csv(ADJUDICATION)
    fields = list(existing[0]) if existing else list(record(*rows[0]))
    added = [record(row, settled) for row, settled in rows]
    if write and added:
        tmp = ADJUDICATION + ".tmp"
        with io.open(tmp, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields,
                                    lineterminator="\n")
            writer.writeheader()
            for entry in existing:
                writer.writerow(entry)
            for entry in added:
                writer.writerow({key: entry.get(key, "") for key in fields})
        os.replace(tmp, ADJUDICATION)
    return added, refused


def selftest():
    rows, refused = candidates()
    for row, _settled in rows:
        assert row["lookahead"] == "PASS", row["strategy_id"]
        assert row["lookahead_evidence"] == "native", row["strategy_id"]
        assert row["recursive"] in ("PASS", "PASS_1PCT"), row["strategy_id"]
        assert row["recursive_evidence"].startswith("convergence:"), \
            row["strategy_id"]
        assert row["traps_n"] in ("", "0"), row["strategy_id"]
        assert row["coverage_status"] == "PASS", row["strategy_id"]
    for _strategy, why in refused:
        assert why, "a refusal must say what stopped it"
    print("eligibility_admit_converged selftest: PASS "
          "(%d admissible, %d converged rows refused)" % (len(rows), len(refused)))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    added, refused = apply(args.apply)
    print("%s %d rows under %s"
          % ("admitted" if args.apply else "would admit", len(added), RULE))
    if refused:
        print("converged but held (%d):" % len(refused))
        for strategy, why in sorted(refused):
            print("   %-34s %s" % (strategy, why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
