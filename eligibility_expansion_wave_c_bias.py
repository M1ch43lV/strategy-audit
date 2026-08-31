# -*- coding: utf-8 -*-
"""Run both bias gates over the Wave C rows that produced trades.

Wave C established only that a row runs. `ELIGIBILITY_EXPANSION_PLAN.md`
is explicit that this is not eligibility: "Successful load or smoke execution
is not eligibility; full measurement and both bias gates still follow." This
queue is that follow-up, and it is the step that turns a measurement into a
usable strategy.

Selection is mechanical and never looks at profit. A row qualifies when it is
a Wave C trading strategy whose canonical implementation produced at least one
trade, in the smoke window or over the full pooled window. Rows with zero
trades everywhere are excluded because the analyzer has nothing to inspect;
they are already excluded by the eligibility rule for the same reason.

The queue is resumable and refuses to re-decide a stored verdict. Order is
manifest order so two sessions process the same rows in the same sequence.
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
CANDIDATES = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_CANDIDATES.csv")
FULL_WINDOW = os.path.join(ROOT, "PROFILE_FULL_WINDOW.json")
WAVE = "C_measurement_recovery"
DIAGNOSTICS = ("lookahead", "recursive")


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _results(path):
    if not os.path.exists(path):
        return {}
    return json.load(io.open(path, encoding="utf-8")).get("results", {})


def _traded(record):
    return (record.get("status") == "measured" and
            int(record.get("trades") or 0) > 0)


def candidates():
    """Wave C trading strategies with at least one observed trade."""
    wanted = {row["strategy_id"] for row in _csv(CANDIDATES)
              if row["expansion_wave"] == WAVE}
    smoke = _results(profile_smoke.OUTPUT)
    full = _results(FULL_WINDOW)
    rows = []
    for row in profile_smoke.read_manifest(profile_smoke.MANIFEST):
        strategy = row["strategy_id"]
        if strategy not in wanted or row.get("artifact_role") != "strategy":
            continue
        if _traded(smoke.get(strategy) or {}) or _traded(full.get(strategy) or {}):
            rows.append(row)
    return rows


def pending(rows, stored):
    """Rows still missing a verdict for at least one gate."""
    remaining = []
    for row in rows:
        record = stored.get(row["strategy_id"]) or {}
        if any(record.get(gate, {}).get("status") not in ("PASS", "FOUND")
               for gate in DIAGNOSTICS):
            remaining.append(row)
    return remaining


def run(limit, timeout, fallback_timeout):
    rows = candidates()
    todo = pending(rows, _results(profile_bias.OUTPUT))
    if limit:
        todo = todo[:limit]
    print("wave C bias queue: %d candidate(s), %d pending, running %d" %
          (len(rows), len(pending(rows, _results(profile_bias.OUTPUT))), len(todo)),
          flush=True)
    for number, row in enumerate(todo, 1):
        strategy = row["strategy_id"]
        print("=== [%d/%d] %s ===" % (number, len(todo), strategy), flush=True)
        # No --force: a stored PASS/FOUND is never re-decided by this queue.
        profile_bias.main(["--only", strategy, "--limit", "1",
                           "--timeout", str(timeout),
                           "--fallback-timeout", str(fallback_timeout)])
    stored = _results(profile_bias.OUTPUT)
    print("wave C bias: %d of %d candidates decided" %
          (len(rows) - len(pending(rows, stored)), len(rows)), flush=True)
    return 0


def selftest():
    rows = candidates()
    ids = [row["strategy_id"] for row in rows]
    assert len(ids) == len(set(ids)), "manifest order must not repeat a row"

    wave = {row["strategy_id"] for row in _csv(CANDIDATES)
            if row["expansion_wave"] == WAVE}
    assert set(ids) <= wave, "only frozen Wave C rows may enter this queue"

    smoke = _results(profile_smoke.OUTPUT)
    full = _results(FULL_WINDOW)
    for strategy in ids:
        assert _traded(smoke.get(strategy) or {}) or _traded(full.get(strategy) or {})

    stored = _results(profile_bias.OUTPUT)
    todo = pending(rows, stored)
    # A row already carrying both verdicts is never offered again.
    for row in rows:
        record = stored.get(row["strategy_id"]) or {}
        decided = all(record.get(gate, {}).get("status") in ("PASS", "FOUND")
                      for gate in DIAGNOSTICS)
        assert decided != (row in todo)
    print("eligibility_expansion_wave_c_bias selftest: PASS "
          "(%d candidates, %d pending)" % (len(rows), len(todo)))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--fallback-timeout", type=int, default=300)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    return run(args.limit, args.timeout, args.fallback_timeout)


if __name__ == "__main__":
    sys.exit(main())
