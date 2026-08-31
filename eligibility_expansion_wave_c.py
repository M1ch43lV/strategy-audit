# -*- coding: utf-8 -*-
"""Exhaustive canonical smoke queue for Wave C.

Wave C rows carry the single hard reason `canonical_implementation_not_measured`.
Their gap is simply that no runtime measurement was ever attempted: the frozen
inventory records `runtime_smoke_status = not_run` for 213 of 230 rows.

The queue is exhaustive rather than opportunistic. It measures every Wave C row
whose artifact role is a trading strategy, in manifest order, and stores each
result the moment it exists. Rows resolved by the pre-flight review as test
fixtures or templates are never measured.

A measurement is not eligibility. A row that runs here still has to clear both
bias gates afterwards, exactly as Wave A did.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import sys

import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_CANDIDATES.csv")
WAVE = "C_measurement_recovery"
# The frozen smoke window; see PROFILE_SMOKE.json, which records it per file.
TIMERANGE = "20200301-20200401"


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def candidates():
    """Wave C rows that are actually trading strategies, in manifest order."""
    wanted = {row["strategy_id"] for row in _csv(CANDIDATES)
              if row["expansion_wave"] == WAVE}
    rows = []
    for row in profile_smoke.read_manifest(profile_smoke.MANIFEST):
        if row["strategy_id"] not in wanted:
            continue
        if row.get("artifact_role") != "strategy":
            continue
        rows.append(row)
    return rows


def pending(data, rows):
    return [row for row in rows if row["strategy_id"] not in data["results"]]


def run(limit, timeout, timerange):
    rows = candidates()
    data = profile_smoke.read_results(profile_smoke.OUTPUT)
    data["timerange"] = timerange
    queue = pending(data, rows)
    if limit:
        queue = queue[:limit]
    print("wave C strategies: %d, pending: %d, running: %d" %
          (len(rows), len(pending(data, rows)), len(queue)), flush=True)
    for number, row in enumerate(queue, 1):
        strategy = row["strategy_id"]
        result = profile_smoke.run_one(row, timerange, timeout)
        try:
            result.update(profile_smoke._identity(row))
        except (OSError, ValueError, KeyError) as exc:
            result["identity_error"] = "%s: %s" % (type(exc).__name__, exc)
        result["runtime_id"] = os.environ.get(
            "PROFILE_RUNTIME_ID", "native_unversioned")
        data["results"][strategy] = result
        profile_smoke.write_results(data, profile_smoke.OUTPUT)
        detail = ("L=%s S=%s" % (result.get("long_trades"), result.get("short_trades"))
                  if result["status"] == "measured" else str(result.get("why", ""))[:70])
        print("[%d/%d] %-38s %-9s %s" %
              (number, len(queue), strategy, result["status"], detail), flush=True)
    print("wave C measured rows stored: %d" % len(data["results"]))


def selftest():
    rows = candidates()
    names = {row["strategy_id"] for row in rows}
    assert len(rows) == len(names) == 218, len(rows)
    # The pre-flight review resolved these as non-strategy artifacts.
    for excluded in ("TestStrategyNoImplements", "ThreeCommasStrategy", "YourStrat"):
        assert excluded not in names, excluded
    for row in rows:
        assert row["run_profile"] != "unknown", row["strategy_id"]
    print("eligibility_expansion_wave_c selftest: PASS (%d strategies)" % len(rows))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--timerange", default=TIMERANGE)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    run(args.limit, args.timeout, args.timerange)
    return 0


if __name__ == "__main__":
    sys.exit(main())
