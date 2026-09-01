# -*- coding: utf-8 -*-
"""Run canonical look-ahead/recursive diagnostics in the native mode.

Results are written after every diagnostic, bound to canonical source and
effective config hashes, and can be resumed safely.  This is intentionally a
separate evidence layer: it never rewrites the historical published ledger.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time

import profile_smoke
import runlog


ROOT = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
ELIGIBILITY = os.path.join(ROOT, "REGIME_ELIGIBILITY.csv")
OUTPUT = os.path.join(ROOT, "PROFILE_BIAS.json")
SPOT_CONFIG = os.path.join(ROOT, "user_data", "config.json")
CONFIG_DIR = os.path.join(ROOT, "user_data", "profile_configs")
# Use the interpreter running this pipeline. This keeps the Windows venv and
# the Linux/Docker execution path equivalent without host-specific branching.
PYTHON = os.environ.get("PROFILE_PYTHON", sys.executable)
FT_WRAPPER = os.path.join(ROOT, "profile_freqtrade.py")
LOG_DIR = os.path.join(ROOT, "user_data", "profile_bias_logs")
ISOLATED_DIR = os.path.join(ROOT, "user_data", "profile_bias_strategies")
WINDOWS = {"spot": "20190101-20190401", "futures": "20200301-20200401"}
INTERMEDIATE_WINDOW = "20200101-20220101"
FALLBACK_WINDOW = "20200301-20260820"


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _sha(path):
    with io.open(path, "rb") as handle:
        return "sha256_" + hashlib.sha256(handle.read()).hexdigest()


def _load(path):
    if not os.path.exists(path):
        return {"schema_version": 1, "results": {}}
    data = json.load(io.open(path, encoding="utf-8"))
    data.setdefault("schema_version", 1)
    data.setdefault("results", {})
    return data


def _write(data, path):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def _runtime(row):
    mode = "futures" if row["run_profile"].startswith("futures_") else "spot"
    if mode == "futures":
        config, env, repair, extra = profile_smoke._runtime(row["strategy_id"])
    else:
        _base_config, env, repair, extra = profile_smoke._runtime(
            row["strategy_id"], mode="spot")
        data = json.load(io.open(SPOT_CONFIG, encoding="utf-8"))
        # Current lookahead-analysis forces market orders. Freqtrade then
        # requires price_side=other before it evaluates a single signal. This
        # config-only compatibility repair affects fill pricing, not indicator
        # or signal generation, and keeps original strategy sources untouched.
        data.setdefault("entry_pricing", {})["price_side"] = "other"
        data.setdefault("exit_pricing", {})["price_side"] = "other"
        pairlists = data.setdefault("pairlists", [{"method": "StaticPairList"}])
        for pairlist in pairlists:
            if pairlist.get("method") == "StaticPairList":
                pairlist["allow_inactive"] = True
        os.makedirs(CONFIG_DIR, exist_ok=True)
        shard = re.sub(r"[^A-Za-z0-9_.-]+", "_", os.environ.get("PROFILE_BIAS_SHARD", ""))
        config = os.path.join(CONFIG_DIR, "bias_spot%s.json" % ("_" + shard if shard else ""))
        with io.open(config, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        repair = dict(repair)
        repair["rules"] = list(repair.get("rules", [])) + [
            "bias_market_order_price_side_compatibility"]
    return mode, config, env, repair, extra


def identity(row):
    """Return every current input that can invalidate stored bias evidence."""
    mode, config, _env, repair, _extra = _runtime(row)
    return {
        "canonical_sha256": _sha(os.path.join(
            ROOT, row["canonical_file"].replace("/", os.sep))),
        "runtime_config_sha256": _sha(config),
        "mode": mode,
        "run_profile": row["run_profile"],
        "class1_rules": repair.get("rules", []),
    }


def identity_matches(row, result):
    expected = identity(row)
    return all(result.get(key) == value for key, value in expected.items())


def _error(output, returncode):
    errors = re.findall(r"(?:ERROR - |(?:Error|Exception): )(.+)", output)
    if errors:
        return errors[-1].strip()[:300]
    return "process exit %d or unparsed output" % returncode


def _isolated_strategy(row, canonical):
    """Expose only the target file to analyzers that enumerate a whole path."""
    directory = os.path.join(ISOLATED_DIR, profile_smoke._safe(row["strategy_id"]))
    os.makedirs(directory, exist_ok=True)
    target = os.path.join(directory, os.path.basename(canonical))
    temporary = target + ".tmp"
    shutil.copyfile(canonical, temporary)
    os.replace(temporary, target)
    return directory


def _lookahead(output, returncode):
    if returncode != 0:
        return "NA", _error(output, returncode)
    if re.search(r"no bias detected", output, re.I):
        return "PASS", "no bias detected"
    too_few = re.search(r"too few trades caught \((\d+)/(\d+)\)", output, re.I)
    if too_few:
        return "NA", "too few trades (%s/%s)" % too_few.groups()
    match = re.search(
        r"(?:\||\u2502)\s*(Yes|No)\s*(?:\||\u2502)\s*(\d*)\s*"
        r"(?:\||\u2502)\s*(\d*)\s*(?:\||\u2502)\s*(\d*)\s*"
        r"(?:\||\u2502)\s*([^\|\u2502\r\n]*)\s*(?:\||\u2502)",
        output,
    )
    if match and match.group(1) == "No":
        return "PASS", "no bias detected"
    if match and match.group(1) == "Yes":
        why = "bias: entries %s, exits %s of %s signals" % (
            match.group(3), match.group(4), match.group(2))
        indicators = match.group(5).strip()
        if indicators:
            why += "; indicators " + indicators
        return "FOUND", why
    errors = re.findall(r"(?:ERROR - |(?:Error|Exception): )(.+)", output)
    return "NA", errors[-1].strip()[:300] if errors else "lookahead output not parsed"


# The frozen Stage 6 gate. The convergence amendment runs the same analyzer at
# a wider band; the default here is never changed so E0 stays reproducible.
DEFAULT_DRIFT_THRESHOLD = 0.01


# The analyzer prints one column per tested startup value, numerically sorted,
# and labels the strategy's own value "(from strategy)". Its position moves with
# the value, so the column must be located by that label rather than by index.
_HEADER = re.compile(r"┃\s*Indicators\s*┃(.+?)┃\s*$", re.M)
_FROM_STRATEGY = re.compile(r"\(from strategy\)")


def _strategy_column(output):
    """Index of the strategy's own column among the table's value columns."""
    columns, _rows = recursive_table(output)
    for index, (_startup, from_strategy) in enumerate(columns):
        if from_strategy:
            return index
    return None


def _cell(value):
    """One table cell: a number, zero for a dash, or None when undefined.

    A dash is the analyzer having nothing worth printing at that startup, which
    is zero. "nan" is the indicator being undefined there - too little history
    for it to have a value at all - which is the absence of a measurement, not
    a small one, and must never be read as agreement.
    """
    value = value.strip()
    if value == "-":
        return 0.0
    if value.lower().startswith("nan"):
        return None
    match = re.fullmatch(r"(-?[\d.]+)%", value)
    return float(match.group(1)) if match else None


def recursive_table(output):
    """The full drift table: (columns, rows).

    `columns` is a list of `(startup_candles, is_from_strategy)` in the order
    the analyzer printed them, which is ascending by startup value. `rows` maps
    each indicator to a list of values aligned to those columns.

    Reading every column matters because one analyzer run already reports every
    startup that was asked for. A ladder does not need one run per rung, and
    the shape of a row across the columns is what shows whether an indicator
    has actually settled or merely crosses the threshold once.
    """
    header = _HEADER.search(output)
    if not header:
        return [], {}
    columns = []
    for cell in header.group(1).split("┃"):
        cell = cell.strip()
        match = re.match(r"(\d+)", cell)
        if not match:
            continue
        columns.append((int(match.group(1)), bool(_FROM_STRATEGY.search(cell))))
    rows = {}
    for line in output.splitlines():
        if not line.startswith("│"):
            continue
        cells = [part.strip() for part in line.strip("│").split("│")]
        if len(cells) != len(columns) + 1:
            continue
        name = cells[0]
        if not re.fullmatch(r"[a-zA-Z_0-9]+", name):
            continue
        rows[name] = [_cell(part) for part in cells[1:]]
    return columns, rows


def settled_startup(output, threshold):
    """Smallest startup from which every indicator stays inside the band.

    Convergence is not the first crossing. A drift curve need not fall
    monotonically: `SmaRsiStrategy` reports 0.588 percent for `rsi` at 14
    candles, 4.262 at 25 and 1.718 at 30 before settling near zero at 90.
    Taking the first value under the band would pick 14, where the indicator is
    plainly not settled. So a startup qualifies only when it and every larger
    startup in the table are defined and inside the band.

    Among the columns that qualify, the one with the SMALLEST worst-case drift
    is returned. Every candidate has already cleared the band at its own value
    and at every larger one, so choosing between them adds no freedom to pass
    or fail a row; it only picks the warm-up at which the indicators are most
    settled. Selecting the smallest drift across all columns, qualifying or
    not, would be a different and inadmissible thing: it would pick the value
    that flatters the test statistic, and for a non-monotone curve it lands on
    a crossing rather than on settlement.

    Returns `(startup, worst_indicator, worst_value)` or None.
    """
    columns, rows = recursive_table(output)
    if not columns or not rows:
        return None
    qualifying = []
    for index, (startup, _from_strategy) in enumerate(columns):
        worst = None
        ok = True
        for later in range(index, len(columns)):
            for name, values in rows.items():
                value = values[later]
                if value is None or abs(value) >= threshold:
                    ok = False
                    break
                if later == index and (worst is None
                                       or abs(value) > abs(worst[1])):
                    worst = (name, value)
            if not ok:
                break
        if ok:
            qualifying.append((startup, worst[0] if worst else None,
                               worst[1] if worst else 0.0))
    if not qualifying:
        return None
    # Ties keep the smaller warm-up: it consumes less history, and a difference
    # the analyzer reports as identical is not a reason to demand more.
    return min(qualifying, key=lambda item: (abs(item[2]), item[0]))


def recursive_drifts(output):
    """Indicator drifts AT THE STRATEGY'S OWN WARM-UP, as (name, percent) pairs.

    The verdict alone discards the numbers, and the convergence route needs
    them: it has to know how far a row still is from its band, and which
    indicator carries the remainder.

    Cells reading "-" mean the analyzer found no deviation worth printing at
    that startup and are treated as zero, which is what they are.
    """
    columns, rows = recursive_table(output)
    index = None
    for position, (_startup, from_strategy) in enumerate(columns):
        if from_strategy:
            index = position
            break
    if index is None:
        return []
    return [(name, values[index]) for name, values in rows.items()]


UNDEFINED = "indicators undefined at this warm-up"

# freqtrade's own words for "the two runs agree exactly". In
# `RecursiveAnalysis.analyze_indicators` the rungs are walked in ascending
# order and the first one whose last row is identical to the full-history run
# logs this and breaks - so no table is printed at all when the smallest rung
# already agrees. That is the strongest possible pass, and reading it as "no
# measurement" turned 17 clean rows into non-verdicts.
NO_VARIANCE = "No variance on indicator(s) found due to recursive formula."


def _recursive(output, returncode, threshold=DEFAULT_DRIFT_THRESHOLD):
    if "invalid startup candle count of 0" in output:
        return "FOUND", "startup_candle_count=0 refused by recursive-analysis"
    if returncode != 0:
        return "NA", _error(output, returncode)
    # Freqtrade refuses a warm-up larger than five times what the exchange
    # serves per request and exits with code 0 while doing so. Without this
    # check the run looks like a clean pass with nothing to report, which is
    # the most dangerous shape a false negative can take.
    refused = re.search(r"This strategy requires (\d+) candles to start, "
                        r"which is more than 5x \((\d+) candles\)", output)
    if refused:
        return "NA", ("startup_candle_count %s exceeds the exchange limit of %s "
                      "candles; the analyzer never ran" % refused.groups())
    drifts = recursive_drifts(output)
    undefined = [key for key, value in drifts if value is None]
    if undefined:
        return "NA", "%s: %s" % (UNDEFINED, ", ".join(sorted(undefined)[:5]))
    if not drifts:
        # An empty table has two causes and they are opposite. Either nothing
        # was compared - the earlier false passes all had this shape and stay
        # NA - or every indicator matched the full-history run exactly, which
        # the analyzer states in as many words before it stops. Only that
        # sentence distinguishes them, so only that sentence may pass a row.
        if NO_VARIANCE in output:
            return "PASS", ("analyzer reports no variance at the smallest "
                            "warm-up tested")
        return "NA", "analyzer produced no drift table"
    bad = [(key, value) for key, value in drifts if abs(value) >= threshold]
    if bad:
        return "FOUND", "recursive drift: " + ", ".join(
            "%s %s%%" % (key, value) for key, value in bad[:5])
    return "PASS", "no recursive deviations found"


def _window_too_small(status, why):
    """True when a diagnostic failed only because this window is too short.

    Freqtrade reports the shortfall as "too few trades", while an indicator that
    needs a minimum series length reports it as "Insufficient data points".
    Both describe the same situation from different layers, so both continue the
    fixed cascade. The cascade windows are frozen in advance and identical for
    every candidate; nothing here selects a window from trade or regime results.
    """
    if status != "NA":
        return False
    return (why.startswith("too few trades") or
            "Insufficient data points" in why)


def run_diagnostic(row, diagnostic, timeout, fallback_timeout):
    strategy = row["strategy_id"]
    canonical = os.path.join(ROOT, row["canonical_file"].replace("/", os.sep))
    mode, config, env, repair, extra = _runtime(row)
    strategy_path = _isolated_strategy(row, canonical)
    original_directory = os.path.dirname(canonical)
    existing_imports = env.get("PROFILE_STRATEGY_IMPORT_PATH", "")
    env["PROFILE_STRATEGY_IMPORT_PATH"] = os.pathsep.join(
        [original_directory] + ([existing_imports] if existing_imports else []))
    started = time.time()
    timeranges = [WINDOWS[mode]]
    if diagnostic == "lookahead" and timeranges[0] != FALLBACK_WINDOW:
        timeranges.extend([INTERMEDIATE_WINDOW, FALLBACK_WINDOW])
    attempted = []
    for attempt, timerange in enumerate(timeranges):
        command = [PYTHON, FT_WRAPPER, diagnostic + "-analysis", "--config", config,
                   "--strategy", strategy, "--strategy-path", strategy_path,
                   "--timerange", timerange, "--no-color"] + extra
        try:
            process = subprocess.run(command, capture_output=True,
                                     timeout=fallback_timeout if attempt else timeout,
                                     env=env, cwd=ROOT)
            output = (process.stdout + process.stderr).decode("utf-8", "replace")
            runlog.append(diagnostic + "-analysis", strategy,
                          profile_smoke._invocation(command), output,
                          {"timerange": timerange,
                           "returncode": process.returncode,
                           "attempt": len(attempted) + 1})
            parser = _lookahead if diagnostic == "lookahead" else _recursive
            status, why = parser(output, process.returncode)
            attempted.append(timerange)
            if _window_too_small(status, why) and timerange != timeranges[-1]:
                continue
            result = {
                "status": status, "why": why, "timerange": timerange,
                "invocation": profile_smoke._invocation(command),
                "attempted_timeranges": attempted,
                "elapsed_s": round(time.time() - started, 1),
                "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned"),
                "output_sha256": "sha256_" + hashlib.sha256(
                    output.encode("utf-8")).hexdigest(),
            }
            if diagnostic == "recursive":
                # The verdict is a threshold decision and throws the numbers
                # away. Keeping them lets a later reader see how far a row was
                # from the line without rerunning the analyzer.
                result["drifts"] = recursive_drifts(output)
            # Preserve inconclusive and positive findings for auditability.
            # PASS logs are omitted because their output hash is sufficient.
            if status in ("NA", "FOUND"):
                os.makedirs(LOG_DIR, exist_ok=True)
                log_path = os.path.join(LOG_DIR, "%s-%s.log" % (
                    profile_smoke._safe(strategy), diagnostic))
                with io.open(log_path, "w", encoding="utf-8") as handle:
                    handle.write(output)
                result["debug_log"] = os.path.relpath(log_path, ROOT).replace(os.sep, "/")
            return result
        except subprocess.TimeoutExpired:
            runlog.append(diagnostic + "-analysis", strategy,
                          profile_smoke._invocation(command), "",
                          {"timerange": timerange, "outcome": "timeout"})
            attempted.append(timerange)
            return {"status": "NA", "why": "TIMEOUT", "timerange": timerange,
                    "invocation": profile_smoke._invocation(command),
                    "attempted_timeranges": attempted,
                    "elapsed_s": round(time.time() - started, 1)}


def candidates(profile_path, eligibility_path):
    profiles = {row["strategy_id"]: row for row in _csv(profile_path)}
    pending = _csv(eligibility_path)
    return [profiles[row["strategy_id"]] for row in pending
            if row["eligibility_status"] == "pending_diagnostics" and
            not ({"zero_trades_in_smoke_requires_full_window",
                  "exact_regime_window_coverage_not_verified",
                  "execution_profile_unresolved",
                  "artifact_role_requires_review"} &
                 set(filter(None, row["pending_reasons"].split(";")))) and
            ("lookahead_not_completed" in row["pending_reasons"] or
             "recursive_bias_not_completed" in row["pending_reasons"])]


def selftest():
    border = "\u2502"
    found = "%s Yes %s 20 %s 0 %s 0 %s rsi_gra, enter_long %s" % (
        border, border, border, border, border, border)
    assert _lookahead(found, 0) == (
        "FOUND",
        "bias: entries 0, exits 0 of 20 signals; indicators rsi_gra, enter_long",
    )
    passed = "%s No %s 4 %s 0 %s 0 %s  %s" % (
        border, border, border, border, border, border)
    assert _lookahead(passed, 0) == ("PASS", "no bias detected")
    # Both messages mean the same thing: this window is too short for the
    # analyzer. Only these continue the frozen cascade.
    assert _window_too_small("NA", "too few trades (0/10)")
    assert _window_too_small("NA", "Insufficient data points for FFT: 102. Need 120.")
    assert not _window_too_small("NA", "TIMEOUT")
    assert not _window_too_small("NA", "process exit -9 or unparsed output")
    assert not _window_too_small("PASS", "too few trades (0/10)")
    assert _lookahead("too few trades caught (2/20)", 0) == (
        "NA", "too few trades (2/20)")

    ran = "Start checking for recursive bias"
    # The strategy's own column moves with its value, because the analyzer
    # sorts the tested startups numerically. Reading the first numeric column
    # instead measured every warm-up above 199 at 199, which is how a ladder of
    # seven rungs produced the same 12.317% seven times on 2026-09-01.
    middle = "\n".join([
        "┃ Indicators ┃ 199 ┃ 288 (from strategy) ┃ 1999 ┃",
        "│ ema_200 │ -9.900% │ 0.018% │ -0.001% │",
        "│ rsi_112 │ -1.000% │ -4.547% │ 0.000% │",
        ran])
    assert recursive_drifts(middle) == [("ema_200", 0.018), ("rsi_112", -4.547)]
    first = "\n".join([
        "┃ Indicators ┃ 34 (from strategy) ┃ 199 ┃",
        "│ macd │ -189.560% │ -0.003% │",
        ran])
    assert recursive_drifts(first) == [("macd", -189.56)]
    last = "\n".join([
        "┃ Indicators ┃ 199 ┃ 999 ┃ 4032 (from strategy) ┃",
        "│ ewo │ 12.317% │ 3.000% │ -0.004% │",
        ran])
    assert recursive_drifts(last) == [("ewo", -0.004)]
    # A dash means the analyzer saw nothing worth printing at that startup.
    dashed = "\n".join([
        "┃ Indicators ┃ 34 (from strategy) ┃ 199 ┃",
        "│ macdhist │ - │ 0.000% │",
        ran])
    assert recursive_drifts(dashed) == [("macdhist", 0.0)]
    # "nan%" is the indicator being undefined at that warm-up: no comparison
    # happened, so there is no verdict and certainly no pass.
    undefined = "\n".join([
        "┃ Indicators ┃ 1 (from strategy) ┃ 199 ┃",
        "│ rsi │ nan% │ -0.093% │",
        "│ sma21 │ nan% │ 0.000% │",
        ran])
    assert recursive_drifts(undefined) == [("rsi", None), ("sma21", None)]
    status, why = _recursive(undefined, 0)
    assert status == "NA" and UNDEFINED in why, (status, why)
    assert _recursive(undefined, 0, threshold=1.0)[0] == "NA"

    # Settling, not crossing, and then the calmest of the settled columns.
    nl = chr(10)
    curve = nl.join([
        "┃ Indicators ┃     14 ┃ 25 (from strategy) ┃     30 ┃     90 ┃     365 ┃",
        "│ rsi │ 0.588% │ 4.262% │ 1.718% │ 0.041% │ -0.052% │",
        ran])
    # 14 is under 1% but 25 and 30 are not, so 14 is a crossing, not a floor.
    assert settled_startup(curve, 1.0) == (90, "rsi", 0.041)
    # Widen the band so 25 and 30 qualify too: the choice among qualifying
    # columns is the smallest drift, which is still 90.
    assert settled_startup(curve, 5.0) == (90, "rsi", 0.041)
    # An exact tie keeps the smaller warm-up rather than demanding more history.
    flat = nl.join([
        "┃ Indicators ┃ 30 (from strategy) ┃ 90 ┃ 365 ┃",
        "│ ema │ 0.000% │ 0.000% │ -0.000% │",
        ran])
    assert settled_startup(flat, 1.0)[0] == 30
    # An undefined cell disqualifies its own column and every smaller one.
    holed = nl.join([
        "┃ Indicators ┃ 30 (from strategy) ┃ 90 ┃ 365 ┃",
        "│ ema │ 0.000% │ nan% │ 0.000% │",
        ran])
    assert settled_startup(holed, 1.0) == (365, "ema", 0.0)
    # Without the label there is no column to read, so there is no verdict.
    assert recursive_drifts("│ ema_200 │ 0.018% │" + ran) == []

    assert _recursive(middle, 0)[0] == "FOUND"
    assert _recursive(middle, 0, threshold=1.0)[0] == "FOUND"   # rsi_112 remains
    assert _recursive(first, 0)[0] == "FOUND"
    assert _recursive(last, 0, threshold=1.0) == (
        "PASS", "no recursive deviations found")
    # An empty table is ambiguous between "nothing deviated" and "nothing was
    # compared", so it is never a pass.
    assert _recursive(ran, 0) == ("NA", "analyzer produced no drift table")
    assert _recursive("", 0) == ("NA", "analyzer produced no drift table")
    refusal = ("Configuration error: This strategy requires 8640 candles to "
               "start, which is more than 5x (4999 candles) the amount of "
               "candles Binance provides for .")
    status, why = _recursive(refusal, 0)
    assert status == "NA" and "exceeds the exchange limit" in why, why
    # The refusal outranks a completed-looking run, if both markers appear.
    assert _recursive(refusal + ran, 0)[0] == "NA"
    # A refusal outranks any threshold; it is not a measurement at all.
    assert _recursive("invalid startup candle count of 0", 0,
                      threshold=1.0)[0] == "FOUND"
    print("profile_bias selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default=PROFILES)
    parser.add_argument("--eligibility", default=ELIGIBILITY)
    parser.add_argument("--output", default=OUTPUT)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--diagnostics", default="lookahead,recursive")
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--fallback-timeout", type=int, default=300)
    parser.add_argument("--force", action="store_true",
                        help="rerun selected diagnostics even when PASS/FOUND is stored")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    wanted = set(filter(None, args.diagnostics.split(",")))
    if not wanted <= {"lookahead", "recursive"}:
        raise SystemExit("diagnostics must be lookahead and/or recursive")
    if args.only:
        # An explicit row name selects from the whole profile manifest. Reaching
        # a row must not require --force, which additionally overwrites a stored
        # PASS/FOUND verdict; selecting a row and re-deciding one are different
        # acts. Expansion-wave rows are ineligible in the frozen E0 table by
        # construction, so the pending-diagnostics filter can never reach them.
        rows = _csv(args.profiles)
    else:
        rows = candidates(args.profiles, args.eligibility)
    if args.only:
        rows = [row for row in rows if row["strategy_id"] in set(args.only)]
    rows = rows[:args.limit]
    data = _load(args.output)
    for number, row in enumerate(rows, 1):
        strategy = row["strategy_id"]
        current_identity = identity(row)
        mode = current_identity["mode"]
        previous = data["results"].get(strategy) or {}
        if any(previous.get(key) != value for key, value in current_identity.items()
               if key in previous):
            previous = {}
        previous.update(current_identity)
        for diagnostic in ("lookahead", "recursive"):
            if diagnostic not in wanted or (not args.force and
                    previous.get(diagnostic, {}).get("status") in ("PASS", "FOUND")):
                continue
            print("[%d/%d] %s %s %s" %
                  (number, len(rows), strategy, mode, diagnostic), flush=True)
            previous[diagnostic] = run_diagnostic(
                row, diagnostic, args.timeout, args.fallback_timeout)
            data["results"][strategy] = previous
            _write(data, args.output)
            print("  %s: %s" % (previous[diagnostic]["status"],
                                 previous[diagnostic]["why"]), flush=True)
    print("profile bias records: %d" % len(data["results"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
