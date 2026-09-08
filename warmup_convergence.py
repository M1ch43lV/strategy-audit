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
# Amendment 2026-09-03 (REGIME_PREREGISTRATION.md): the ceiling this caps the
# ladder at exists to protect the full-window run these values are later
# reused in - see profile_full_window.py's own note on the same amendment.
# Spot and futures pairs were listed on Binance at different times, so their
# windows now differ too; each mode's start must match the window
# profile_full_window.timerange(mode) actually uses, or a warm-up this ladder
# accepts could still silently truncate the pair it is later run against.
WINDOW_START = {"spot": "2020-04-01", "futures": "2020-03-01"}

# Freqtrade refuses any startup_candle_count above five times what the exchange
# serves per request - "more than 5x (4999 candles)" for Binance - and exits
# with code 0 while refusing, so the refusal reads as a silent clean run unless
# it is caught. It is caught in profile_bias._recursive now, and the ladder is
# capped here so the rung is never requested in the first place. The cap binds
# hardest exactly where the warm-up matters most: at a five-minute timeframe it
# allows about 17 days, so the 30, 90 and 365 day rungs do not exist there.
# Freqtrade refuses a warm-up that would need more than five OHLCV calls per
# pair - 4999 candles on Binance. Its own comment says the reason: a budget for
# calls to the exchange, so a live bot does not hammer the API. A backtest
# makes none of those calls; the candles are feather files on disk.
#
# Enforced, that budget capped the ladder at the fourth rung for every
# five-minute strategy: 4999 candles is fourteen days, and the ladder is meant
# to climb to 365. Sixty-two rows were recorded as never settling without ever
# being offered the last three rungs. `startup_candles_not_limited_by_call_
# budget` lifts it, and then the only ceiling left is the one that is real -
# the history actually on disk, which `available_prefix_candles` already
# applies.
MAX_STARTUP_CANDLES = 4999
STARTUP_SHIM = "startup_candles_not_limited_by_call_budget"


def startup_ceiling(strategy=None):
    """The largest warm-up worth asking for, given what is installed."""
    if strategy and STARTUP_SHIM in class1_rules().get(strategy, ()):
        return None
    return MAX_STARTUP_CANDLES


def class1_rules():
    """Compatibility rules registered per strategy."""
    path = os.path.join(ROOT, "PROFILE_CLASS1.json")
    if not os.path.exists(path):
        return {}
    entries = json.load(io.open(path, encoding="utf-8")).get("strategies", {})
    return {name: set(entry.get("rules") or [])
            for name, entry in entries.items()
            if entry.get("status") in ("applied", "partial")}

# Freqtrade refuses a strategy declaring no warm-up before it evaluates
# anything, and the refusal takes the whole ladder run with it.
_REFUSED = re.compile(
    r"This strategy requires (\d+) candles to start, "
    r"which is more than 5x \((\d+) candles\)")

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
        count = int((frame["date"] < WINDOW_START[mode]).sum())
        smallest = count if smallest is None else min(smallest, count)
    return smallest


def ladder(timeframe, cap=None, budget=MAX_STARTUP_CANDLES):
    """The frozen day ladder in candles for one timeframe, capped at history.

    Returns (days, candles) pairs so a record can state the rung in the unit
    the rule is written in. A rung that repeats the previous candle count is
    dropped; at a one-week timeframe several day rungs collapse onto one.
    """
    minutes = timeframe_minutes(timeframe)
    if not minutes:
        return []
    # `budget=None` means the call-budget guard is lifted for this row, so the
    # only ceiling left is the history actually on disk. It is not the same as
    # "no argument given", which keeps the guard.
    if budget is None:
        ceiling = cap
    else:
        ceiling = budget if cap is None else min(cap, budget)
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


def window_thawed_rows():
    """Spot rows the 2026-09-03 window amendment newly lets reach 365 days.

    Distinct from `budget_capped_rows`: that cohort is everything the call
    budget shim applies to, spot and futures alike, whether or not the window
    change helps it. This one is only the rows for which it actually does -
    computed the same way the amendment's own targets were, so a row that
    still falls short after the window moved is left where it is rather than
    re-run to reproduce the same answer.
    """
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    results = _load(OUTPUT).get("results", {})
    superseded = _load(OUTPUT).get("superseded", {})
    known = set(results) | set(superseded)
    wanted = []
    for strategy in sorted(known):
        row = profiles.get(strategy)
        if not row or row["run_profile"].startswith("futures_"):
            continue
        # The current result always wins over history: a row moved aside
        # and then re-measured (ARIMASTR, BBRSIS, under `shim5`) must be read
        # from its converged verdict, not from the stale record that sent it
        # to `superseded` in the first place.
        prior = results.get(strategy)
        if prior is None:
            history = superseded.get(strategy) or []
            history = history if isinstance(history, list) else [history]
            prior = next((r for r in reversed(history)
                         if r.get("state") == "not_converged_within_ladder"),
                        None)
        if not prior or prior.get("state") != "not_converged_within_ladder":
            continue
        timeframe = prior.get("timeframe")
        minutes = timeframe_minutes(timeframe)
        cap = available_prefix_candles(row["run_profile"], timeframe)
        if not minutes or cap is None:
            continue
        needed = -(-365 * 1440 // minutes)
        if cap >= needed and max(prior.get("ladder_days") or [0]) < 365:
            wanted.append(strategy)
    return [profiles[strategy] for strategy in wanted]


def budget_capped_rows():
    """Rows whose ladder freqtrade's call budget cut short.

    A record that says "no startup settles the indicators" is only worth that
    much if the ladder was allowed to climb. For every five-minute strategy it
    was not: 4999 candles is fourteen days, and the last three rungs were
    never offered. These rows carry the shim that lifts the budget, so their
    old record describes a ladder that no longer applies.
    """
    # Read from the registry, not from the results store: the old records
    # are moved under `superseded` before this runs, so a cohort derived from
    # `results` would come back empty exactly when it is needed.
    rules = class1_rules()
    known = {row["strategy_id"] for row in _csv(PROFILES)}
    return [strategy for strategy in sorted(rules)
            if STARTUP_SHIM in rules[strategy] and strategy in known]


def frozen_baseline_rows():
    """Legacy CLI selector retained after E0's retirement.

    The 67 were re-measured through the ladder, E0 was invalidated as a cohort,
    and `strategy_status.py` deliberately never assigns `E0_strict67` again.
    This therefore returns no rows. Do not reconstruct the set from provenance:
    the completed row-level evidence is already represented by E1 decisions or
    exclusion, and rerunning it would duplicate finished work.
    """
    return [row["strategy_id"] for row in _csv(STATUS)
            if row["cohort"] == "E0_strict67"]


def ladder_pending_rows():
    """Every unfinished row the status table has queued for the ladder.

    The older cohorts each name a specific historical shape. This one asks the
    table itself what is still open, which is what makes it right for the 40
    rows the trap heuristic used to exclude: they run and trade, they never
    had a ladder run of ours, and nothing about their shape is historical -
    they were simply never reached.
    """
    rows = []
    for row in _csv(STATUS):
        if row["cohort"] not in ("exclusion_unconfirmed", "pending"):
            continue
        work = row["open_work"] or ""
        # Two shapes, one need. `recursive_ladder_pending` is a row the ladder
        # has never seen. `convergence_inconclusive` is one it saw and could
        # not judge - 39 of those because the ladder ran them without the
        # repair that makes them start at all, so the record describes a
        # configuration nobody intends to use.
        if "recursive_ladder_pending" not in work                 and "convergence_inconclusive" not in work:
            continue
        rows.append(row["strategy_id"])
    return rows


def unsettled_rows():
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
    # Recursion has to be the thing that decides the row. A strategy that reads
    # future candles, carries a published trap, or will not start at all stays
    # out whatever its warm-up does, so measuring it spends half a minute to
    # change nothing. That is the same restraint `recursion_only_rows` applies,
    # expressed against the current table rather than the frozen reasons.
    blocking = ("lookahead_found", "behavior_changed_primary_exclusion",
                "technical_trap_found", "strategy_does_not_run",
                "no_trades_in_full_measurement")
    wanted = []
    for row in _csv(STATUS):
        work = row["open_work"] or ""
        if "recursive_ladder_pending" not in work                 and "convergence_inconclusive" not in work:
            continue
        if row["primary_reason"] in blocking or row["lookahead"] == "FOUND":
            continue
        if row["cohort"] == "not_tested_in_current_runtime":
            continue
        wanted.append(row["strategy_id"])
    return wanted


def cohort(name):
    """Rows this route may consider. Selection never reads an outcome."""
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    if name == "recursion_only":
        wanted = [row["strategy_id"] for row in recursion_only_rows()]
    elif name == "wave_c_refusals":
        wanted = [row["strategy_id"]
                  for row in eligibility_warmup.refusal_candidates()]
    elif name == "recursive_unsettled":
        wanted = unsettled_rows()
    elif name == "ladder_pending":
        wanted = ladder_pending_rows()
    elif name == "frozen_baseline":
        wanted = frozen_baseline_rows()
    elif name == "budget_capped":
        wanted = budget_capped_rows()
    elif name == "window_thawed":
        wanted = [row["strategy_id"] for row in window_thawed_rows()]
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


# Stores holding a repair run. A repaired row has to be measured the way it
# was repaired, or the ladder reports on a configuration nobody intends to
# use. The look-ahead queue learned this in September; the ladder had not.
REPAIR_STORES = (
    os.path.join(ROOT, "ELIGIBILITY_TIMEFRAME_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_MODULE_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_SIGNATURE_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_FREQAI_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_FREQAI_WTAI.json"),
)


def repair_overrides():
    """Config keys a repaired row must be run with, keyed by strategy."""
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


def run_ladder(row, timeout, startups, overrides=None):
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
    # A recovered timeframe is passed the way the repair runner passes it,
    # on the command line, so the isolated source stays untouched.
    for key, value in sorted((overrides or {}).items()):
        flag = "--" + key.replace("_", "-")
        if flag not in extra:
            extra = list(extra) + [flag, str(value)]
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


_CONFIG_TIMEFRAME = re.compile(r"^timeframe\s*=\s*['\"]([0-9]+[mhdwM])['\"]", re.M)


def sibling_config_timeframe(canonical_file):
    """The timeframe from a same-directory `Config*.py`, if the strategy
    reads it from a sibling config module instead of declaring its own.

    2026-09-08, wave-2 futures/short harvest: 18 rows in
    `hamidreza07_freqai-strategy` read the value this way rather than
    stating it, which is why `execution_profiles.py`'s static source scan -
    looking for a literal `timeframe = ...` in the strategy file itself -
    finds nothing and `EXECUTION_PROFILES.csv` records `timeframe_source:
    unresolved`. All 18 still ran a real Probelauf, so the value was never
    actually missing, only indirected through the author's own sibling
    file. This reads the same file the strategy imports at runtime; it is
    not a different or invented value.

    Glob rather than a fixed `Config.py`: `SqueezeOff` imports
    `Config_SqueezeOff`, not `Config` - the same repository names its
    per-strategy config module after the strategy in some folders and
    plainly `Config` in others. Scoped to this one directory only, so the
    risk of picking up an unrelated file is the same as it would be for a
    literal `Config.py` check.
    """
    directory = os.path.dirname(os.path.join(ROOT, canonical_file.replace("/", os.sep)))
    if not os.path.isdir(directory):
        return None
    candidates = sorted(name for name in os.listdir(directory)
                        if name.startswith("Config") and name.endswith(".py"))
    for name in candidates:
        text = io.open(os.path.join(directory, name),
                       encoding="utf-8", errors="replace").read()
        match = _CONFIG_TIMEFRAME.search(text)
        if match:
            return match.group(1)
    return None


def resolve(row, timeout, overrides=None):
    """Find the smallest warm-up from which this row stays inside the band."""
    strategy = row["strategy_id"]
    # A repair-store override (Argrelextrema: config_overrides={"timeframe":
    # "5m"} from eligibility_timeframe_repair.py) already reaches run_ladder
    # below for the subprocess config - it also has to reach the candle math
    # here, or a strategy whose timeframe is only known through the override
    # still reports no_usable_ladder despite having a real, evidenced value.
    timeframe = ((overrides or {}).get("timeframe")
                 or row.get("execution_timeframe") or row.get("declared_timeframe")
                 or sibling_config_timeframe(row["canonical_file"]))
    cap = available_prefix_candles(row["run_profile"], timeframe)
    rungs = ladder(timeframe, cap, startup_ceiling(strategy))
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

    candles = [candles for _days, candles in rungs]
    output, meta = run_ladder(row, timeout, candles, overrides)
    record.update(meta)
    if output is None:
        record["state"] = "inconclusive"
        record["why"] = meta.get("why", "TIMEOUT")
        return record

    # A single rung the strategy cannot compute aborts the whole run, and the
    # analyzer's exception then reaches the record as "no drift table", which
    # names neither the cause nor the cure. The cure is usually to start
    # higher: most of these failures are an indicator refusing a series
    # shorter than it needs (TRIX_LS: `rsi_.rolling(length)` on `None`;
    # kijun_cross_strong_s: a `NoneType` subscript) - both already pass a real
    # Probelauf on full history, so the crash is the ladder's own extreme short
    # rungs, not a defect the strategy shows under real use. So the bottom
    # rung is dropped and the ladder tried again, stopping once only the 3
    # longest rungs are left - not promoted to a pass or a fail either way,
    # just given every rung short of the ones the ladder rule itself judges
    # least informative a chance to be the reason, before deciding it is not.
    dropped = []
    while meta.get("returncode") and len(candles) > 3:
        dropped.append(candles[0])
        candles = candles[1:]
        rungs = rungs[1:]
        output, meta = run_ladder(row, timeout, candles, overrides)
        record.update(meta)
        if output is None:
            record["state"] = "inconclusive"
            record["why"] = meta.get("why", "TIMEOUT")
            return record
    if dropped:
        record["ladder_rungs_dropped_as_uncomputable"] = dropped
        record["ladder_candles"] = candles
        record["ladder_days"] = [days for days, _value in rungs]
    if meta.get("returncode"):
        if len(candles) <= 3:
            # Every rung short of the 3 longest is gone and it still crashes.
            # The recursive-bias check is not optional for any row, so a
            # strategy that cannot complete it even given the most generous
            # remaining warm-up is decided, not left open - unlike plain
            # `inconclusive`, which stays a question because a shorter,
            # untried rung might still have worked.
            record["state"] = "crashes_even_at_longest_rungs"
            record["why"] = profile_bias._error(output, meta["returncode"])
            return record
        record["state"] = "inconclusive"
        record["why"] = profile_bias._error(output, meta["returncode"])
        return record

    # One rung above what the exchange serves refuses the WHOLE run, and the
    # rungs below it - which are the ones likely to settle the row - are lost
    # with it. The refusal states the limit, so the ladder is trimmed to it and
    # re-run once. Twenty-one rows were recorded as inconclusive for no better
    # reason than asking for a top rung nobody could have answered.
    refused = _REFUSED.search(output)
    if refused:
        limit = int(refused.group(2))
        trimmed = [value for value in candles if value <= limit]
        record["exchange_startup_limit"] = limit
        if not trimmed:
            record["state"] = "inconclusive"
            record["why"] = ("even the smallest rung of %d candles is above the "
                             "exchange limit of %d" % (candles[0], limit))
            return record
        record["ladder_trimmed_to_exchange_limit"] = trimmed
        record["ladder_candles"] = trimmed
        record["ladder_days"] = [days for days, value in rungs if value <= limit]
        output, meta = run_ladder(row, timeout, trimmed, overrides)
        record.update(meta)
        if output is None or _REFUSED.search(output):
            record["state"] = "inconclusive"
            record["why"] = (meta.get("why") or "refused again after trimming "
                             "the ladder to the exchange limit")
            return record
        rungs = [(days, value) for days, value in rungs if value <= limit]

    columns, rows = profile_bias.recursive_table(output)
    if not columns or not rows:
        # No table and the analyzer saying it found no variance are not the
        # same outcome. The second is freqtrade reporting that the smallest
        # rung already matches the full-history run exactly, which is why it
        # printed nothing: it stopped there. That is a pass at the first rung.
        if profile_bias.NO_VARIANCE in output:
            record["state"] = "converged"
            record["chosen_startup_candle_count"] = rungs[0][1]
            record["chosen_ladder_days"] = rungs[0][0]
            record["max_drift_pct"] = 0.0
            record["max_drift_indicator"] = None
            record["needed_no_override"] = (
                record.get("declared_warmup_override") is None)
            record["why"] = ("analyzer reports no variance at the smallest "
                             "rung; it compared and stopped there")
            return record
        record["state"] = "inconclusive"
        record["why"] = "analyzer produced no drift table"
        return record

    record["columns"] = [{"startup_candle_count": startup,
                          "from_strategy": from_strategy}
                         for startup, from_strategy in columns]
    record["drifts"] = {name: values for name, values in sorted(rows.items())}
    # Columns the analyzer could not put a number on at any rung are set aside
    # from the decision, and named here so the record says so rather than
    # quietly dropping them. See profile_bias.settled_startup.
    blind = profile_bias.undefined_throughout(output)
    if blind:
        record["undefined_throughout"] = blind
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
        if blind:
            record["why"] += (" (%s set aside: unreadable at every rung)"
                              % ", ".join(blind))
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


# Two record shapes that a defect of ours produced, not the analyzer. Both are
# handled now - an over-large top rung is trimmed to the exchange limit, and a
# bottom rung the strategy cannot compute is dropped - so a record carrying
# either was made by code that could not have got the answer.
DEFECTIVE = ("freqtrade refused startup",
             "analyzer produced no drift table",
             # Not a defect of ours but of the moment: a run that could not
             # reach the exchange never evaluated the strategy, so its message
             # describes the machine. Nine rows carry it.
             "Could not load markets",
             # The ladder ran the row in its unrepaired state. Thirty-nine
             # records carry freqtrade's refusal, and thirty-eight of them
             # have the timeframe recovered from the author's own
             # `ticker_interval` sitting in the repair store all along. The
             # run measured a configuration nobody intends to use.
             "Timeframe needs to be set")


def redo_defective(cohort_name):
    """Drop records a known defect produced, so the row is measured again.

    The record is not deleted: it moves under `superseded` with the reason, in
    the same file. A measurement that was wrong is still evidence about what we
    did, and three corrections this week were only findable because the old
    reading was still there to compare against.
    """
    data = _load(OUTPUT)
    wanted = {row["strategy_id"] for row in cohort(cohort_name)}
    superseded = data.setdefault("superseded", {})
    moved = []
    for strategy in sorted(wanted):
        record = data["results"].get(strategy)
        if not record or record.get("state") != "inconclusive":
            continue
        why = record.get("why") or ""
        if not any(marker in why for marker in DEFECTIVE):
            continue
        record["superseded_because"] = (
            "recorded before the ladder trimmed an over-large top rung and "
            "dropped an uncomputable bottom rung; re-run under the fix")
        superseded.setdefault(strategy, []).append(record)
        del data["results"][strategy]
        moved.append((strategy, why[:60]))
    _write(OUTPUT, data)
    return moved


def run(cohort_name, limit, timeout, wanted=None):
    rows = cohort(cohort_name)
    if wanted:
        # Mirrors profile_bias.py's --only: an explicit strategy list selects
        # from within the cohort, so a specific wave can be run without the
        # rest of what "ladder_pending" happens to also contain interleaved
        # alphabetically with it.
        rows = [row for row in rows if row["strategy_id"] in wanted]
    data = _load(OUTPUT)
    pending = [row for row in rows if row["strategy_id"] not in data["results"]]
    if limit:
        pending = pending[:limit]
    overrides = repair_overrides()

    print("convergence cohort %s: %d rows, %d pending, running %d" %
          (cohort_name, len(rows), len([r for r in rows
                                        if r["strategy_id"] not in data["results"]]),
           len(pending)), flush=True)
    for number, row in enumerate(pending, 1):
        print("=== [%d/%d] %s ===" % (number, len(pending), row["strategy_id"]),
              flush=True)
        record = resolve(row, timeout, overrides.get(row["strategy_id"]))
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
                                 "ladder_pending", "frozen_baseline",
                                 "budget_capped", "window_thawed",
                                 "wave_b_static_rejected",
                                 "recursive_unsettled"))
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--strategy", action="append", default=[],
                        help="restrict the cohort to these strategy_ids")
    parser.add_argument("--redo-defective", action="store_true",
                        dest="redo",
                        help="move records a known defect produced aside")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.redo:
        moved = redo_defective(args.cohort)
        print("moved %d defective records aside" % len(moved))
        for strategy, why in moved:
            print("   %-30s %s" % (strategy, why))
        return 0
    return run(args.cohort, args.limit, args.timeout, set(args.strategy) or None)


if __name__ == "__main__":
    sys.exit(main())
