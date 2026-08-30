# -*- coding: utf-8 -*-
"""Run resumable paired full-window equivalence for recovered Wave B rows."""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

import eligibility_warmup_equivalence as equivalence
import profile_full_window
import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
RECOVERY = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_WARMUP_RECOVERY.csv")
WARMUP = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_WARMUP.json")
LOOKAHEAD = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_LOOKAHEAD.json")


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def candidates():
    warmup = json.load(io.open(WARMUP, encoding="utf-8"))["results"]
    lookahead = json.load(io.open(LOOKAHEAD, encoding="utf-8"))["results"]
    selected = []
    for row in _csv(RECOVERY):
        strategy = row["strategy_id"]
        if row["recovery_state"] == "terminal_unbounded_prefix_dependency":
            continue
        startup = (row["recovery_startup_candle_count"]
                   if row["recovery_state"] == "recovery_frozen" else "1")
        recursive = ((warmup.get(strategy) or {}).get("attempts", {}).get(startup) or {})
        current_lookahead = (lookahead.get(strategy) or {}).get("lookahead", {})
        if recursive.get("status") == "PASS" and current_lookahead.get("status") == "PASS":
            selected.append((strategy, int(startup)))
    return selected


def run(limit, timeout):
    data = equivalence._load(equivalence.OUTPUT)
    pending = [(strategy, startup) for strategy, startup in candidates()
               if "%s|startup=%d" % (strategy, startup) not in data["results"]]
    if limit:
        pending = pending[:limit]
    for number, (strategy, startup) in enumerate(pending, 1):
        row, diagnostic = equivalence.select(strategy, startup)
        print("[%d/%d] %s canonical pooled full window" %
              (number, len(pending), strategy), flush=True)
        original = profile_smoke.run_one(row, profile_full_window.TIMERANGE, timeout)
        print("  original %s trades=%s" %
              (original["status"], original.get("trades", "")), flush=True)
        print("  %s startup=%d pooled full window" % (strategy, startup), flush=True)
        override = profile_smoke.run_one(
            row, profile_full_window.TIMERANGE, timeout,
            config_overrides={"startup_candle_count": startup})
        print("  override %s trades=%s" %
              (override["status"], override.get("trades", "")), flush=True)
        same = equivalence.equivalent(original, override)
        key = "%s|startup=%d" % (strategy, startup)
        data["runtime_id"] = os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned")
        data["results"][key] = {
            "strategy_id": strategy,
            "implementation_id": row["implementation_id"],
            "startup_candle_count": startup,
            "diagnostic_output_sha256": diagnostic.get("output_sha256", ""),
            "original": original,
            "override": override,
            "exact_semantic_trade_equivalence": same,
            "admission_effect": "none_equivalence_only",
        }
        equivalence._write(equivalence.OUTPUT, data)
        print("  exact semantic trade equivalence: %s" % str(same).lower(), flush=True)
    print("equivalence records: %d" % len(data["results"]))


def selftest():
    selected = candidates()
    assert len(selected) == 26
    assert len({strategy for strategy, _startup in selected}) == 26
    assert ("SlowPotato", 1440) in selected
    print("eligibility_warmup_equivalence_queue selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    run(args.limit, args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
