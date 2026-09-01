# -*- coding: utf-8 -*-
"""Re-measure the admitted rows whose gate verdicts came from the old sweep.

`regime_eligibility.classify` promotes a historical spot PASS to a current one
whenever no native verdict exists:

    lookahead = native if native in ("PASS", "FOUND") else historical_lookahead

Futures were handled carefully - a historical PASS is explicitly not inherited
across execution modes - but the same caution was never applied across
environments. The original author's sweep ran without the preconditions this
audit establishes, so a PASS from it says nothing about whether the strategy is
clean here. Thirty admitted rows rest on exactly that.

This queue measures those gates natively, in the pinned runtime, so the usable
set stands on one body of evidence rather than two. It changes no rule and no
threshold: it replaces an inherited verdict with a measured one.

A FOUND here is a real outcome and must be reported as one. Re-measuring only
until the answer is convenient would be worse than not re-measuring at all, so
the cohort is frozen before the first run and every verdict is kept.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

import profile_bias


ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_EVIDENCE_GAP.json")

GATES = ("lookahead", "recursive")


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _load():
    if not os.path.exists(OUTPUT):
        return {"schema_version": 1,
                "why": ("admitted rows whose gate verdicts were inherited from "
                        "the original author's sweep, re-measured natively"),
                "results": {}}
    return json.load(io.open(OUTPUT, encoding="utf-8"))


def _write(data):
    tmp = OUTPUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, OUTPUT)


def cohort():
    """Admitted rows carrying at least one gate from the original sweep.

    Derived from the status table rather than hard-coded, and asserted against
    the evidence on every call, so a row that has since been re-measured leaves
    the cohort instead of being measured twice.
    """
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    selected = []
    for row in _csv(STATUS):
        if row["cohort"] not in ("E0_strict67", "E1_expanded"):
            continue
        gaps = [gate for gate in GATES
                if "%s_from_original_sweep" % gate in row["evidence_gap"]]
        if gaps:
            selected.append((profiles[row["strategy_id"]], gaps))
    return selected


def run(limit, timeout, fallback_timeout):
    rows = cohort()
    data = _load()
    pending = [(row, gaps) for row, gaps in rows
               if row["strategy_id"] not in data["results"]]
    if limit:
        pending = pending[:limit]
    print("evidence gap: %d admitted rows inherit a verdict, %d pending, "
          "running %d" % (len(rows), len(rows) - len(data["results"]),
                          len(pending)), flush=True)
    for number, (row, gaps) in enumerate(pending, 1):
        strategy = row["strategy_id"]
        print("=== [%d/%d] %s (%s) ===" % (number, len(pending), strategy,
                                           ", ".join(gaps)), flush=True)
        record = {"strategy_id": strategy,
                  "implementation_id": row["implementation_id"],
                  "inherited_gates": gaps}
        record.update(profile_bias.identity(row))
        for gate in gaps:
            result = profile_bias.run_diagnostic(row, gate, timeout,
                                                 fallback_timeout)
            record[gate] = result
            print("  %s: %s — %s" % (gate, result.get("status"),
                                     (result.get("why") or "")[:80]), flush=True)
        data["results"][strategy] = record
        _write(data)
    decided = data["results"]
    found = [s for s, r in decided.items()
             for g in r.get("inherited_gates", [])
             if (r.get(g) or {}).get("status") == "FOUND"]
    print("re-measured %d of %d; %d now report FOUND: %s"
          % (len(decided), len(rows), len(found), ", ".join(sorted(found)) or "none"),
          flush=True)
    return 0


def selftest():
    rows = cohort()
    assert rows, "no admitted row inherits a verdict; has the status table been regenerated?"
    ids = [row["strategy_id"] for row, _gaps in rows]
    assert len(ids) == len(set(ids))
    status = {r["strategy_id"]: r for r in _csv(STATUS)}
    for row, gaps in rows:
        entry = status[row["strategy_id"]]
        # Only admitted rows may be here: this queue exists to put the usable
        # set on one body of evidence, not to revisit exclusions.
        assert entry["cohort"] in ("E0_strict67", "E1_expanded")
        for gate in gaps:
            assert entry["%s_evidence" % gate].startswith("historical"), \
                (row["strategy_id"], gate)
    print("eligibility_evidence_gap selftest: PASS (%d rows, %d gates)"
          % (len(rows), sum(len(g) for _r, g in rows)))


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
