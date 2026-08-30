# -*- coding: utf-8 -*-
"""Compare canonical and startup-overridden full pooled trade lists for Wave B."""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

import profile_full_window
import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_CANDIDATES.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
WARMUP = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_WARMUP.json")
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_EQUIVALENCE.json")


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _load(path):
    if not os.path.exists(path):
        return {"schema_version": 1, "timerange": profile_full_window.TIMERANGE,
                "results": {}}
    return json.load(io.open(path, encoding="utf-8"))


def _write(path, data):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def select(strategy, startup_candle_count):
    candidates = {row["strategy_id"]: row for row in _csv(CANDIDATES)
                  if row["expansion_wave"] == "B_warmup_refusal"}
    if strategy not in candidates:
        raise SystemExit("strategy is not in frozen Wave B: %s" % strategy)
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    row = profiles[strategy]
    if row["implementation_id"] != candidates[strategy]["implementation_id"]:
        raise SystemExit("canonical identity changed: %s" % strategy)
    warmup = json.load(io.open(WARMUP, encoding="utf-8"))
    attempt = (((warmup.get("results") or {}).get(strategy) or {})
               .get("attempts", {}).get(str(startup_candle_count)))
    if not attempt or attempt.get("status") != "PASS":
        raise SystemExit("matching warmup diagnostic PASS required before equivalence")
    return row, attempt


def equivalent(original, override):
    keys = ["status", "trades", "long_trades", "short_trades", "trades_sha256"]
    return (original.get("status") == "measured" and
            override.get("status") == "measured" and
            all(original.get(key) == override.get(key) for key in keys))


def selftest():
    one = {"status": "measured", "trades": 1, "long_trades": 1,
           "short_trades": 0, "trades_sha256": "sha256_x"}
    assert equivalent(one, dict(one))
    assert not equivalent(one, dict(one, trades_sha256="sha256_y"))
    print("eligibility_warmup_equivalence selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy")
    parser.add_argument("--startup-candle-count", type=int)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if not args.strategy or args.startup_candle_count is None:
        raise SystemExit("strategy and startup-candle-count are required")
    row, diagnostic = select(args.strategy, args.startup_candle_count)
    data = _load(OUTPUT)
    key = "%s|startup=%d" % (args.strategy, args.startup_candle_count)
    if key in data["results"] and not args.force:
        print("equivalence result already stored: %s" % key)
        return 0
    print("%s: canonical pooled full window" % args.strategy, flush=True)
    original = profile_smoke.run_one(
        row, profile_full_window.TIMERANGE, args.timeout)
    print("  %s trades=%s" % (original["status"], original.get("trades", "")),
          flush=True)
    print("%s: startup=%d pooled full window" %
          (args.strategy, args.startup_candle_count), flush=True)
    override = profile_smoke.run_one(
        row, profile_full_window.TIMERANGE, args.timeout,
        config_overrides={"startup_candle_count": args.startup_candle_count})
    print("  %s trades=%s" % (override["status"], override.get("trades", "")),
          flush=True)
    is_equivalent = equivalent(original, override)
    data["runtime_id"] = os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned")
    data["results"][key] = {
        "strategy_id": args.strategy,
        "implementation_id": row["implementation_id"],
        "startup_candle_count": args.startup_candle_count,
        "diagnostic_output_sha256": diagnostic.get("output_sha256", ""),
        "original": original,
        "override": override,
        "exact_semantic_trade_equivalence": is_equivalent,
        "admission_effect": "none_equivalence_only",
    }
    _write(OUTPUT, data)
    print("exact semantic trade equivalence: %s" % str(is_equivalent).lower())
    return 0


if __name__ == "__main__":
    sys.exit(main())
