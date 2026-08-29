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


def _recursive(output, returncode):
    if "invalid startup candle count of 0" in output:
        return "FOUND", "startup_candle_count=0 refused by recursive-analysis"
    if returncode != 0:
        return "NA", _error(output, returncode)
    rows = re.findall(r"│\s*([a-zA-Z_0-9]+)\s*│\s*(-?[\d.]+)%", output)
    bad = [(key, value) for key, value in rows if abs(float(value)) > 0.01]
    if bad:
        return "FOUND", "recursive drift: " + ", ".join(
            "%s %s%%" % item for item in bad[:5])
    return "PASS", "no recursive deviations found"


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
            parser = _lookahead if diagnostic == "lookahead" else _recursive
            status, why = parser(output, process.returncode)
            attempted.append(timerange)
            if status == "NA" and why.startswith("too few trades") and \
                    timerange != timeranges[-1]:
                continue
            result = {
                "status": status, "why": why, "timerange": timerange,
                "attempted_timeranges": attempted,
                "elapsed_s": round(time.time() - started, 1),
                "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned"),
                "output_sha256": "sha256_" + hashlib.sha256(
                    output.encode("utf-8")).hexdigest(),
            }
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
            attempted.append(timerange)
            return {"status": "NA", "why": "TIMEOUT", "timerange": timerange,
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
    assert _lookahead("too few trades caught (2/20)", 0) == (
        "NA", "too few trades (2/20)")
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
    if args.force and args.only:
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
