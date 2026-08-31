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


# A run killed by the kernel, stopped by the timeout, or unable to reach the
# exchange never evaluated the strategy, so its message describes the machine
# rather than the tested code.
RESOURCE_MARKERS = (
    "process exit -9",
    "timeout after",
    "Could not load markets",
)

# The protocol allows one standard attempt plus one documented single-worker
# recovery attempt; a second inconclusive result is terminal.
MAX_ATTEMPTS = 2


def resource_inconclusive(result):
    """True when a run produced no verdict about the strategy itself."""
    if result.get("status") == "measured":
        return False
    if result.get("status") == "timeout":
        return True
    why = result.get("why") or ""
    return any(marker in why for marker in RESOURCE_MARKERS)


def outcome(original, override):
    """Classify one paired attempt without collapsing distinct causes.

    `equivalent` and `not_equivalent` are statements about the strategy and are
    only reachable when both sides actually produced trades. A resource kill is
    never reported as a failed equivalence.
    """
    if resource_inconclusive(original) or resource_inconclusive(override):
        return "resource_inconclusive"
    if original.get("status") != "measured" or override.get("status") != "measured":
        return "technical_failure"
    return "equivalent" if equivalent(original, override) else "not_equivalent"


def attempts_of(record):
    """Normalize a stored record into its retained attempt list.

    Records written before attempts were retained hold a single attempt inline;
    reading them through this function keeps that evidence as attempt one.
    """
    if not record:
        return []
    stored = record.get("attempts")
    if stored:
        return [dict(attempt) for attempt in stored]
    original = record.get("original") or {}
    override = record.get("override") or {}
    return [{"original": original, "override": override,
             "outcome": record.get("outcome") or outcome(original, override),
             "runtime_id": record.get("runtime_id", "")}]


def terminal_state(attempts):
    """Resolve the protocol state implied by the attempts recorded so far."""
    if not attempts:
        return "not_attempted"
    last = attempts[-1]["outcome"]
    if last != "resource_inconclusive":
        return last
    if len(attempts) >= MAX_ATTEMPTS:
        return "pending_diagnostics"
    return "recovery_available"


def recoverable(record):
    """True while the single permitted recovery attempt is still unused."""
    return terminal_state(attempts_of(record)) == "recovery_available"


def build_record(previous, row, startup, diagnostic, original, override,
                 runtime_id):
    """Append one attempt to a row, never discarding the attempts it follows."""
    attempts = attempts_of(previous)
    attempts.append({"original": original, "override": override,
                     "outcome": outcome(original, override),
                     "runtime_id": runtime_id})
    latest = attempts[-1]
    return {
        "strategy_id": row["strategy_id"],
        "implementation_id": row["implementation_id"],
        "startup_candle_count": startup,
        "diagnostic_output_sha256": diagnostic.get("output_sha256", ""),
        "original": latest["original"],
        "override": latest["override"],
        "exact_semantic_trade_equivalence": latest["outcome"] == "equivalent",
        "outcome": latest["outcome"],
        "attempts": attempts,
        "terminal_state": terminal_state(attempts),
        "admission_effect": "none_equivalence_only",
    }


def selftest():
    one = {"status": "measured", "trades": 1, "long_trades": 1,
           "short_trades": 0, "trades_sha256": "sha256_x"}
    assert equivalent(one, dict(one))
    assert not equivalent(one, dict(one, trades_sha256="sha256_y"))

    killed = {"status": "failed",
              "why": "process exit -9 without a readable backtest archive"}
    markets = {"status": "failed",
               "why": "Could not load markets, therefore cannot start."}
    broken = {"status": "failed",
              "why": "Impossible to load Strategy 'X'. This class does not exist."}
    assert resource_inconclusive(killed)
    assert resource_inconclusive(markets)
    assert resource_inconclusive({"status": "timeout"})
    assert not resource_inconclusive(broken)
    assert not resource_inconclusive(one)

    # A resource kill must never be reported as a strategy-level verdict.
    assert outcome(one, dict(one)) == "equivalent"
    assert outcome(one, dict(one, trades_sha256="sha256_y")) == "not_equivalent"
    assert outcome(killed, killed) == "resource_inconclusive"
    assert outcome(one, markets) == "resource_inconclusive"
    assert outcome(one, broken) == "technical_failure"

    # A legacy inline record is read as attempt one and keeps its recovery.
    legacy = {"original": killed, "override": killed,
              "exact_semantic_trade_equivalence": False}
    assert len(attempts_of(legacy)) == 1
    assert terminal_state(attempts_of(legacy)) == "recovery_available"
    assert recoverable(legacy)

    row = {"strategy_id": "X", "implementation_id": "impl"}
    recovered = build_record(legacy, row, 40, {}, one, dict(one), "docker:test")
    assert len(recovered["attempts"]) == 2, "the replaced attempt must survive"
    assert recovered["attempts"][0]["outcome"] == "resource_inconclusive"
    assert recovered["outcome"] == "equivalent"
    assert recovered["exact_semantic_trade_equivalence"] is True
    assert recovered["terminal_state"] == "equivalent"
    assert not recoverable(recovered)

    # A second inconclusive result exhausts the budget and is terminal.
    exhausted = build_record(legacy, row, 40, {}, killed, killed, "docker:test")
    assert len(exhausted["attempts"]) == MAX_ATTEMPTS
    assert exhausted["terminal_state"] == "pending_diagnostics"
    assert not recoverable(exhausted)
    print("eligibility_warmup_equivalence selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy")
    parser.add_argument("--startup-candle-count", type=int)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--recover", action="store_true",
                        help="spend the single permitted recovery attempt on a "
                             "stored resource-inconclusive row")
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
    previous = data["results"].get(key)
    if previous and not (args.force or (args.recover and recoverable(previous))):
        print("equivalence result already stored: %s (%s)" %
              (key, terminal_state(attempts_of(previous))))
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
    runtime_id = os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned")
    data["runtime_id"] = runtime_id
    record = build_record(previous, row, args.startup_candle_count, diagnostic,
                          original, override, runtime_id)
    data["results"][key] = record
    _write(OUTPUT, data)
    print("outcome: %s (attempt %d, %s)" %
          (record["outcome"], len(record["attempts"]), record["terminal_state"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
