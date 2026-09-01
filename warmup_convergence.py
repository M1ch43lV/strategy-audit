# -*- coding: utf-8 -*-
"""Choose a diagnostic warm-up by convergence instead of by literal period.

The frozen rule is in `REGIME_PREREGISTRATION.md` under "Frozen warm-up
convergence amendment". In short: walk a fixed ladder of warm-up values and
take the FIRST one at which freqtrade's `recursive-analysis` reports no
indicator drifting by 1.0 percent or more.

Why this replaces the old value. The previous warm-up was the longest literal
indicator period found in the source, and that heuristic failed three recorded
ways: it read a minimum as a maximum (`Strategy004`), it carried a period
across timeframes without converting it (`Cluc4`, `BB_RPB_TSL`, whose
`ema_100_1h` needs 1200 five-minute candles rather than 100), and it ignores
that a recursively smoothed indicator never forgets its seed. Warm-up equal to
the period leaves about `e**-2` of the seed for a standard EMA and `e**-1`
under Wilder smoothing. Measured here: `pmaxTest` at warm-up 112 still drifts
4.5 percent on `rsi_112`.

What this script does NOT do. Acceptance is not admission. A converged row
still owes a look-ahead PASS and a paired full-window run with an identical
trade list, and a row that converges but trades differently is E3 exploratory,
never E1. Nothing here reads profit, regime, or ranking output, and the ladder
and threshold are fixed before any run rather than searched per row.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

import eligibility_warmup
import profile_bias
import profile_smoke
import runlog


ROOT = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_CANDIDATES.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
OUTPUT = os.path.join(ROOT, "WARMUP_CONVERGENCE.json")
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
LOG_DIR = os.path.join(ROOT, "user_data", "convergence_logs")

# Frozen by the amendment. The ladder is expressed in CALENDAR DAYS and
# converted to candles through the strategy's own timeframe.
#
# Days rather than multiples of the file-derived period, because that derived
# period is the thing that keeps being wrong: it read a minimum as a maximum in
# `Strategy004`, and it carried an hourly period onto a five-minute frame in
# `Cluc4` and `BB_RPB_TSL`. A ladder anchored to it inherits its errors. A day
# is independent of the source audit, is the same span of market history for
# every strategy, and converts exactly: 30 days is 8,640 five-minute candles,
# 720 hourly candles, or 30 daily ones.
#
# The rungs reach 365 days because a slow strategy needs them. At a one-day
# timeframe, 30 days is 30 candles, which cannot settle an EMA200; a year can.
LADDER_DAYS = (1, 2, 7, 14, 30, 90, 365)
DRIFT_THRESHOLD_PCT = 1.0
WINDOW_START = "2020-03-01"

# Freqtrade refuses any startup_candle_count above five times what the exchange
# serves per request - "more than 5x (4999 candles)" for Binance - and exits
# with code 0 while refusing, so the refusal reads as a silent clean run unless
# it is caught. It is caught in profile_bias._recursive now, and the ladder is
# capped here so the rung is never requested in the first place. The cap binds
# hardest exactly where the warm-up matters most: at a five-minute timeframe it
# allows about 17 days, so the 30, 90 and 365 day rungs do not exist there.
MAX_STARTUP_CANDLES = 4999

# Freqtrade refuses a strategy declaring no warm-up before it evaluates
# anything, and the refusal takes the whole ladder run with it.
ZERO_WARMUP_REFUSAL = "invalid startup candle count of 0"

# Wave B rows whose exact trade match was refused a static proof because the
# decision rests on a recursively smoothed series. They are the rows the
# amendment was written for, so they are revisited under it by name.
WAVE_B_STATIC_REJECTED = (
    "Cluc4",
    "Combined_Indicators",
    "CombinedBinHAndClucHyperV0",
    "Strategy004",
    "TouchEmaStrategy",
)

_MINUTES = {"m": 1, "h": 60, "d": 1440, "w": 10080}


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _load(path):
    if not os.path.exists(path):
        return {"schema_version": 1,
                "drift_threshold_pct": DRIFT_THRESHOLD_PCT,
                "ladder_days": list(LADDER_DAYS),
                "results": {}}
    return json.load(io.open(path, encoding="utf-8"))


def _write(path, data):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def timeframe_minutes(timeframe):
    match = re.fullmatch(r"(\d+)([mhdw])", (timeframe or "").strip())
    if not match:
        return None
    return int(match.group(1)) * _MINUTES[match.group(2)]


def available_prefix_candles(run_profile, timeframe):
    """Candles that actually exist before the frozen window starts.

    A warm-up larger than the available history does not fail loudly; freqtrade
    simply starts later, which silently measures a different window than every
    other row. The ladder is capped here so that cannot happen.
    """
    minutes = timeframe_minutes(timeframe)
    if not minutes:
        return None
    mode = "futures" if run_profile.startswith("futures_") else "spot"
    config = profile_smoke._read_jsonc(
        profile_smoke.FUTURES_CONFIG if mode == "futures"
        else profile_smoke.SPOT_CONFIG)
    directory = os.path.join(ROOT, "user_data", "data", "binance")
    if mode == "futures":
        directory = os.path.join(directory, "futures")
    try:
        import pandas
    except ImportError:
        return None
    smallest = None
    for pair in config["exchange"]["pair_whitelist"]:
        stem = pair.replace("/", "_").replace(":", "_")
        suffix = "-futures" if mode == "futures" else ""
        path = os.path.join(directory, "%s-%s%s.feather" % (stem, timeframe, suffix))
        if not os.path.exists(path):
            continue
        frame = pandas.read_feather(path, columns=["date"])
        count = int((frame["date"] < WINDOW_START).sum())
        smallest = count if smallest is None else min(smallest, count)
    return smallest


def ladder(timeframe, cap=None):
    """The frozen day ladder in candles for one timeframe, capped at history.

    Returns (days, candles) pairs so a record can state the rung in the unit
    the rule is written in. A rung that repeats the previous candle count is
    dropped; at a one-week timeframe several day rungs collapse onto one.
    """
    minutes = timeframe_minutes(timeframe)
    if not minutes:
        return []
    ceiling = MAX_STARTUP_CANDLES if cap is None else min(cap, MAX_STARTUP_CANDLES)
    rungs = []
    for days in LADDER_DAYS:
        candles = max(1, -(-days * 1440 // minutes))
        if candles > ceiling:
            break
        if rungs and rungs[-1][1] == candles:
            continue
        rungs.append((days, candles))
    return rungs


# Rows already admitted to E1 are not revisited: their verdict stands and the
# route exists to decide rows that have none.
def _admitted():
    path = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_PROOFS.json")
    if not os.path.exists(path):
        return set()
    return set(json.load(io.open(path, encoding="utf-8")).get("strategies", {}))


# The processing order is fixed here, not chosen from results. Wave D first
# because recursion is its sole barrier and nothing else is outstanding; then
# the unscheduled rows in the same condition; then the Wave B remainder, which
# has already been through the older route.
_WAVE_ORDER = ("D_recursive_drift", "not_scheduled", "B_warmup_refusal")


def recursion_only_rows():
    """Every row whose only hard exclusion reason is recursive drift.

    This is the cohort the amendment exists for. A row carrying a second hard
    reason - a look-ahead finding, a technical trap, no measurement at all -
    stays excluded whatever its warm-up does, so running it would spend hours
    to change nothing.
    """
    rows = [row for row in _csv(CANDIDATES)
            if (row["baseline_exclusion_reasons"] or "") == "recursive_bias_found"]
    admitted = _admitted()
    rows = [row for row in rows if row["strategy_id"] not in admitted]
    order = {wave: index for index, wave in enumerate(_WAVE_ORDER)}
    rows.sort(key=lambda row: (order.get(row["expansion_wave"], len(order)),
                               row["strategy_id"]))
    return rows


def warmup_refused_rows():
    """Rows whose recursion verdict was a refusal, not a measurement.

    Two things land here. A row whose inherited verdict reads FOUND because
    the analyzer declined it for want of a declared warm-up - it never got as
    far as comparing anything. And a Wave B row re-run under the old parser,
    which read the wrong column of the drift table and took an undefined cell
    for a clean one; those verdicts are recorded as superseded rather than
    trusted, and eight of them carry an admission.

    Selection reads `open_work`, which the status table sets from provenance
    alone, so no outcome decides who is measured.
    """
    return [row["strategy_id"] for row in _csv(STATUS)
            if "recursive_ladder_pending" in (row["open_work"] or "")]


def cohort(name):
    """Rows this route may consider. Selection never reads an outcome."""
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    if name == "recursion_only":
        wanted = [row["strategy_id"] for row in recursion_only_rows()]
    elif name == "wave_c_refusals":
        wanted = [row["strategy_id"]
                  for row in eligibility_warmup.refusal_candidates()]
    elif name == "warmup_refused":
        wanted = warmup_refused_rows()
    elif name == "wave_b_static_rejected":
        wanted = list(WAVE_B_STATIC_REJECTED)
    elif name == "wave_d":
        wanted = [row["strategy_id"] for row in _csv(CANDIDATES)
                  if row["expansion_wave"] == "D_recursive_drift"]
    else:
        raise SystemExit("unknown cohort: %s" % name)
    return [profiles[strategy] for strategy in wanted if strategy in profiles]


def derived_value(strategy):
    import eligibility_warmup_recovery as recovery
    if strategy in recovery.OVERRIDES:
        return recovery.OVERRIDES[strategy][0]
    return recovery._audited_period(strategy)


def run_ladder(row, timeout, startups):
    """Ask the analyzer for every ladder rung in a single run.

    `recursive-analysis` accepts the startup values to test and prints one
    column per value, plus the strategy's own. So the whole ladder is one run
    of about half a minute rather than one run per rung, and the strategy's
    declared warm-up is left untouched: it appears as its own column instead of
    being overridden.
    """
    strategy = row["strategy_id"]
    canonical = os.path.join(ROOT, row["canonical_file"].replace("/", os.sep))
    mode, config, env, repair, extra = profile_bias._runtime(row)
    strategy_path = profile_bias._isolated_strategy(row, canonical)
    existing = env.get("PROFILE_STRATEGY_IMPORT_PATH", "")
    env["PROFILE_STRATEGY_IMPORT_PATH"] = os.pathsep.join(
        [os.path.dirname(canonical)] + ([existing] if existing else []))

    invocation = [None]

    def attempt(config_path):
        command = [profile_bias.PYTHON, profile_bias.FT_WRAPPER,
                   "recursive-analysis", "--config", config_path,
                   "--strategy", strategy, "--strategy-path", strategy_path,
                   "--timerange", profile_bias.WINDOWS[mode], "--no-color",
                   "--startup-candle"] + [str(v) for v in startups] + extra
        # The second attempt supplies a warm-up, so the two calls differ. The
        # one kept is the one whose output was read.
        invocation[0] = profile_smoke._invocation(command)
        return subprocess.run(command, capture_output=True, timeout=timeout,
                              env=env, cwd=ROOT)

    started = time.time()
    override = None
    try:
        process = attempt(config)
        output = (process.stdout + process.stderr).decode("utf-8", "replace")
        if ZERO_WARMUP_REFUSAL in output:
            # A strategy that declares no warm-up is refused outright, and the
            # refusal takes the whole run with it - including the ladder columns
            # the analyzer would otherwise have printed. This is the Wave B
            # condition, and the answer is the Wave B one: supply the smallest
            # rung so the analyzer will run at all. The declared column then
            # reports that supplied value rather than the author's, so the row
            # can never be recorded as having needed no override.
            override = min(startups)
            _mode, config, env, _repair, _extra = eligibility_warmup._runtime(
                row, override)
            env["PROFILE_STRATEGY_IMPORT_PATH"] = os.pathsep.join(
                [os.path.dirname(canonical)] + ([existing] if existing else []))
            process = attempt(config)
    except subprocess.TimeoutExpired:
        return None, {"status": "NA", "why": "TIMEOUT",
                      "invocation": invocation[0],
                      "elapsed_s": round(time.time() - started, 1)}
    output = (process.stdout + process.stderr).decode("utf-8", "replace")
    runlog.append("recursive-analysis/ladder", strategy, invocation[0], output,
                  {"startups": ",".join(str(v) for v in startups),
                   "returncode": process.returncode,
                   "warmup_supplied": override,
                   "elapsed_s": round(time.time() - started, 1)})
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "%s-ladder.log"
                            % profile_smoke._safe(strategy))
    with io.open(log_path, "w", encoding="utf-8") as handle:
        handle.write(output)
    meta = {
        "invocation": invocation[0],
        "elapsed_s": round(time.time() - started, 1),
        "returncode": process.returncode,
        "declared_warmup_override": override,
        "timerange": profile_bias.WINDOWS[mode],
        "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned"),
        "debug_log": os.path.relpath(log_path, ROOT).replace(os.sep, "/"),
        "output_sha256": "sha256_" + hashlib.sha256(
            output.encode("utf-8")).hexdigest(),
    }
    return output, meta


def resolve(row, timeout):
    """Find the smallest warm-up from which this row stays inside the band."""
    strategy = row["strategy_id"]
    timeframe = row.get("execution_timeframe") or row.get("declared_timeframe")
    cap = available_prefix_candles(row["run_profile"], timeframe)
    rungs = ladder(timeframe, cap)
    record = {
        "strategy_id": strategy,
        "implementation_id": row["implementation_id"],
        "run_profile": row["run_profile"],
        "timeframe": timeframe,
        "file_derived_period": derived_value(strategy),
        "available_prefix_candles": cap,
        "ladder_days": [days for days, _candles in rungs],
        "ladder_candles": [candles for _days, candles in rungs],
        "drift_threshold_pct": DRIFT_THRESHOLD_PCT,
    }
    if not rungs:
        record["state"] = "no_usable_ladder"
        record["why"] = ("no declared timeframe" if not timeframe_minutes(timeframe)
                         else "available history is shorter than the first rung")
        return record

    output, meta = run_ladder(row, timeout,
                              [candles for _days, candles in rungs])
    record.update(meta)
    if output is None:
        record["state"] = "inconclusive"
        record["why"] = meta.get("why", "TIMEOUT")
        return record

    refused = re.search(r"This strategy requires (\d+) candles to start", output)
    if refused:
        record["state"] = "inconclusive"
        record["why"] = ("freqtrade refused startup %s as above the exchange "
                         "limit" % refused.group(1))
        return record

    columns, rows = profile_bias.recursive_table(output)
    if not columns or not rows:
        record["state"] = "inconclusive"
        record["why"] = "analyzer produced no drift table"
        return record

    record["columns"] = [{"startup_candle_count": startup,
                          "from_strategy": from_strategy}
                         for startup, from_strategy in columns]
    record["drifts"] = {name: values for name, values in sorted(rows.items())}
    declared = next((index for index, (_s, from_strategy)
                     in enumerate(columns) if from_strategy), None)
    if declared is not None:
        worst = [abs(values[declared]) for values in rows.values()
                 if values[declared] is not None]
        record["declared_startup_candle_count"] = columns[declared][0]
        record["declared_max_drift_pct"] = max(worst) if worst else None

    settled = profile_bias.settled_startup(output, DRIFT_THRESHOLD_PCT)
    if settled is None:
        record["state"] = "not_converged_within_ladder"
        largest = columns[-1][0]
        record["why"] = ("no startup up to %d candles keeps every indicator "
                         "inside %s%%" % (largest, DRIFT_THRESHOLD_PCT))
        return record
    startup, indicator, value = settled
    record["state"] = "converged"
    record["chosen_startup_candle_count"] = startup
    record["chosen_ladder_days"] = next(
        (days for days, candles in rungs if candles == startup), None)
    record["max_drift_pct"] = abs(value)
    record["max_drift_indicator"] = indicator
    # A row settled at its own declared warm-up needs no override at all: it
    # was excluded by the parser reading the wrong column, not by its code.
    # A row that had to be given a warm-up before the analyzer would run has
    # by definition not been left alone, whatever column it settled in.
    record["needed_no_override"] = (
        record.get("declared_warmup_override") is None
        and declared is not None and startup <= columns[declared][0])
    return record


def run(cohort_name, limit, timeout):
    rows = cohort(cohort_name)
    data = _load(OUTPUT)
    pending = [row for row in rows if row["strategy_id"] not in data["results"]]
    if limit:
        pending = pending[:limit]
    print("convergence cohort %s: %d rows, %d pending, running %d" %
          (cohort_name, len(rows), len([r for r in rows
                                        if r["strategy_id"] not in data["results"]]),
           len(pending)), flush=True)
    for number, row in enumerate(pending, 1):
        print("=== [%d/%d] %s ===" % (number, len(pending), row["strategy_id"]),
              flush=True)
        record = resolve(row, timeout)
        record["cohort"] = cohort_name
        data["results"][row["strategy_id"]] = record
        _write(OUTPUT, data)
        print("  state: %s" % record["state"], flush=True)
    converged = [key for key, value in data["results"].items()
                 if value.get("state") == "converged"]
    print("converged so far: %d of %d recorded" %
          (len(converged), len(data["results"])), flush=True)
    return 0


def selftest():
    assert timeframe_minutes("5m") == 5
    assert timeframe_minutes("1h") == 60
    assert timeframe_minutes("1d") == 1440
    assert timeframe_minutes("") is None

    # A day is the same span of history whatever the timeframe, which is the
    # whole reason the ladder is written in days.
    assert ladder("1d") == [(1, 1), (2, 2), (7, 7), (14, 14), (30, 30),
                            (90, 90), (365, 365)]
    assert ladder("1h") == [(1, 24), (2, 48), (7, 168), (14, 336), (30, 720),
                            (90, 2160)]
    # Freqtrade's own ceiling truncates the fast timeframes. At five minutes a
    # month of warm-up is 8,640 candles, which it refuses outright.
    assert ladder("5m") == [(1, 288), (2, 576), (7, 2016), (14, 4032)]
    assert all(candles <= MAX_STARTUP_CANDLES for _d, candles in ladder("1m"))
    # 30 daily candles cannot settle an EMA200; 365 can, and 365 is under the
    # ceiling, so the slow timeframes keep the full ladder.
    assert ladder("1d")[-1][1] == 365
    # History that does not exist is never requested either.
    assert ladder("1h", cap=200) == [(1, 24), (2, 48), (7, 168)]
    assert ladder("1d", cap=0) == []
    assert ladder("") == []
    # Rungs that collapse onto the same candle count are not run twice.
    assert [candles for _days, candles in ladder("1w")] == [1, 2, 5, 13, 53]

    rows = cohort("recursion_only")
    assert 400 <= len(rows) <= 448, len(rows)
    # A row with a second hard reason cannot be rescued by any warm-up, so it
    # must not be in the cohort.
    hard = {row["strategy_id"]: row["baseline_exclusion_reasons"]
            for row in _csv(CANDIDATES)}
    for row in rows:
        assert hard[row["strategy_id"]] == "recursive_bias_found"
    # Nothing already admitted to E1 is revisited.
    assert not {row["strategy_id"] for row in rows} & _admitted()
    # Wave D leads the fixed processing order.
    waves = {row["strategy_id"]: row["expansion_wave"] for row in _csv(CANDIDATES)}
    first = [waves[row["strategy_id"]] for row in rows[:124]]
    assert set(first) == {"D_recursive_drift"}, sorted(set(first))

    assert len(cohort("wave_c_refusals")) == len(eligibility_warmup.WAVE_C_REFUSALS)
    assert len(cohort("wave_b_static_rejected")) == len(WAVE_B_STATIC_REJECTED)
    assert len(cohort("wave_d")) == 124
    print("warmup_convergence selftest: PASS "
          "(%d recursion-only rows, %d of them Wave D)"
          % (len(rows), len(cohort("wave_d"))))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", default="recursion_only",
                        choices=("recursion_only", "wave_d", "wave_c_refusals",
                                 "wave_b_static_rejected"))
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    return run(args.cohort, args.limit, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
