# -*- coding: utf-8 -*-
"""Measure look-ahead natively for every convergence candidate that lacks it.

The expansion was aimed at recursion, because recursion was these rows' sole
exclusion reason, and the second gate was never run for most of them. Of the
361 candidates only 53 carry a look-ahead verdict measured from their own
implementation: 177 inherit one from the original author's sweep and 130 have
none at all.

An inherited PASS is the weak case. A FOUND from a different environment is
still disqualifying evidence - a limited environment does not invent bias - but
a PASS is an absence claim, and the old sweep reported "output not parsed" 344
times for this very gate. An absence produced by a run that could not complete
is not evidence of cleanliness.

Thirty inherited verdicts were re-measured on 2026-09-01 and all thirty held.
That is encouraging and not sufficient: zero failures in thirty draws bounds
the error rate at about 9.5 percent, and those thirty were the already-admitted
rows, which had cleared every other gate and are therefore a favourable sample.
At roughly 44 seconds a run the whole backfill costs a few hours, which is less
than the uncertainty is worth.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

import profile_bias
import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_LOOKAHEAD_BACKFILL.json")

# Stores holding a repair run, so a repaired row is gated the way it was
# measured. Without this the gate re-runs the row in its unrepaired state and
# records the original failure as a look-ahead verdict - which it is not.
REPAIR_STORES = (
    os.path.join(ROOT, "ELIGIBILITY_TIMEFRAME_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_MODULE_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_SIGNATURE_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_FREQAI_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_FREQAI_WTAI.json"),
)


def repair_overrides():
    """Config keys a repaired row must be gated with, keyed by strategy."""
    out = {}
    for path in REPAIR_STORES:
        if not os.path.exists(path):
            continue
        results = json.load(io.open(path, encoding="utf-8")).get("results", {})
        for strategy, record in results.items():
            overrides = record.get("config_overrides") or {}
            if overrides:
                out.setdefault(strategy, dict(overrides))
    return out


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _load():
    if not os.path.exists(OUTPUT):
        return {"schema_version": 1,
                "why": ("look-ahead measured natively for convergence "
                        "candidates that had no verdict of their own"),
                "results": {}}
    return json.load(io.open(OUTPUT, encoding="utf-8"))


def _write(data):
    tmp = OUTPUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, OUTPUT)


def cohort():
    """Convergence candidates whose look-ahead verdict is inherited or absent.

    Derived from the status table and re-derived on every call, so a row that
    has since been measured drops out rather than being measured twice. A row
    that already carries a native verdict is never revisited: this backfills a
    gap, it does not re-decide anything.
    """
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    selected = []
    for row in _csv(STATUS):
        # Any row the ladder settled, whatever cohort it landed in. Tying this
        # to `convergence_candidate` missed 21 rows that had settled and then
        # left the cohort precisely because their look-ahead verdict was
        # borrowed - the rows this route exists for.
        # Two sources, one rule: a row that runs and has no look-ahead verdict
        # of its own. Either the ladder settled it - the original arm - or the
        # status table has queued it as `lookahead_remeasure_pending`, which is
        # the same condition stated from the other end.
        settled = row["recursive_evidence"].startswith("convergence:")
        queued = "lookahead_remeasure_pending" in (row["open_work"] or "")
        if not settled and not queued:
            continue
        if row["lookahead_evidence"] == "native":
            continue
        if row["measured"] != "true" or row["runtime_failure"]:
            # A row that will not start cannot be gated; repairing it comes
            # first and is tracked separately.
            continue
        if row["strategy_id"] not in profiles:
            continue
        selected.append(profiles[row["strategy_id"]])
    return selected


def run(limit, timeout, fallback_timeout):
    rows = cohort()
    data = _load()
    overrides = repair_overrides()
    pending = [row for row in rows if row["strategy_id"] not in data["results"]]
    if limit:
        pending = pending[:limit]
    print("look-ahead backfill: %d candidates lack a native verdict, %d pending, "
          "running %d" % (len(rows), len(rows) - len(data["results"]), len(pending)),
          flush=True)
    for number, row in enumerate(pending, 1):
        strategy = row["strategy_id"]
        print("=== [%d/%d] %s ===" % (number, len(pending), strategy), flush=True)
        record = {"strategy_id": strategy,
                  "implementation_id": row["implementation_id"]}
        record.update(profile_bias.identity(row))
        record["lookahead"] = profile_bias.run_diagnostic(
            row, "lookahead", timeout, fallback_timeout,
            config_overrides=overrides.get(strategy))
        if overrides.get(strategy):
            record["config_overrides"] = overrides[strategy]
        data["results"][strategy] = record
        _write(data)
        print("  %s — %s" % (record["lookahead"].get("status"),
                             (record["lookahead"].get("why") or "")[:80]), flush=True)
    decided = data["results"]
    found = sorted(s for s, r in decided.items()
                   if (r.get("lookahead") or {}).get("status") == "FOUND")
    print("measured %d of %d; %d report FOUND: %s"
          % (len(decided), len(rows), len(found), ", ".join(found) or "none"),
          flush=True)
    return 0


def selftest():
    rows = cohort()
    ids = [row["strategy_id"] for row in rows]
    assert len(ids) == len(set(ids))
    status = {r["strategy_id"]: r for r in _csv(STATUS)}
    for row in rows:
        entry = status[row["strategy_id"]]
        assert (entry["recursive_evidence"].startswith("convergence:")
                or "lookahead_remeasure_pending" in (entry["open_work"] or "")),             row["strategy_id"]
        # A native verdict is never re-decided; only a gap is filled.
        assert entry["lookahead_evidence"] != "native", row["strategy_id"]
    native = sum(1 for r in status.values()
                 if r["recursive_evidence"].startswith("convergence:")
                 and r["lookahead_evidence"] == "native")
    print("eligibility_lookahead_backfill selftest: PASS "
          "(%d to measure, %d already native)" % (len(rows), native))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--fallback-timeout", type=int, default=600)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    return run(args.limit, args.timeout, args.fallback_timeout)


if __name__ == "__main__":
    sys.exit(main())
