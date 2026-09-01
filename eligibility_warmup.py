# -*- coding: utf-8 -*-
"""Run the frozen diagnostic-only startup=1 pilot for Wave B.

The canonical strategy source is not modified and PROFILE_BIAS.json is not
overwritten.  A PASS here is only feasibility evidence.  E1 admission still
requires the full equivalence and canonical rerun protocol.
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

import profile_bias
import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_CANDIDATES.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
MANIFEST = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_MANIFEST.json")
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_WARMUP.json")
CONFIG_DIR = os.path.join(ROOT, "user_data", "expansion_configs")
LOG_DIR = os.path.join(ROOT, "user_data", "expansion_logs")
BIAS = os.path.join(ROOT, "PROFILE_BIAS.json")
DEFAULT_OVERRIDE = 1
RULE = "diagnostic_startup_override_v1"

# Wave C rows the recursive analyzer refused rather than judged. They record
# `recursive = FOUND` with this marker, which is not a bias finding: the
# analyzer declined to run and made no statement about the strategy. That is
# precisely the condition Wave B exists for, and these rows landed in Wave C
# only because at freeze time their sole known defect was that nobody had
# measured them. Applying the frozen adapter to newly matching rows is what
# plan section 6 requires; inventing a softer second route is not.
#
# The set is frozen here, and refusal_candidates() re-derives it from the
# stored evidence and refuses to run if the two have drifted apart. Four of the
# seven are variants of one strategy and are not independent observations.
REFUSAL_MARKER = "refused by recursive-analysis"
WAVE_C_REFUSALS = (
    "BB_RPB_TSL",
    "BB_RPB_TSL_2",
    "BB_RPB_TSL_BI",
    "BB_RPB_TSL_BIV1",
    "MultiRSI",
    "epretrace",
    "pmaxTest",
)


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _sha(path):
    digest = hashlib.sha256(io.open(path, "rb").read()).hexdigest()
    return "sha256_" + digest


def _safe(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def _load(path):
    if not os.path.exists(path):
        return {"schema_version": 1, "rule": RULE, "results": {}}
    data = json.load(io.open(path, encoding="utf-8"))
    if data.get("rule") == "diagnostic_only_startup_candle_count_1":
        data["rule"] = RULE
        data["results"] = {
            strategy: {
                "attempts": {"1": result},
                "latest_startup_candle_count": 1,
            }
            for strategy, result in data.get("results", {}).items()
        }
    if data.get("rule") != RULE:
        raise ValueError("warmup output rule mismatch")
    return data


def _write_json(path, data):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def candidates(candidate_path=CANDIDATES, profile_path=PROFILES,
               manifest_path=MANIFEST):
    manifest = json.load(io.open(manifest_path, encoding="utf-8"))
    frozen = set(manifest["candidate_members"]["B_warmup_refusal"])
    profiles = {row["strategy_id"]: row for row in _csv(profile_path)}
    selected = []
    for row in _csv(candidate_path):
        if row["expansion_wave"] != "B_warmup_refusal":
            continue
        member = "%s|%s|%s" % (
            row["strategy_id"], row["run_profile"], row["implementation_id"])
        if member not in frozen:
            raise ValueError("candidate is not in frozen Wave B: %s" % member)
        profile = profiles[row["strategy_id"]]
        if profile["implementation_id"] != row["implementation_id"]:
            raise ValueError("profile identity changed: %s" % row["strategy_id"])
        selected.append(profile)
    if len(selected) != len(frozen):
        raise ValueError("Wave B candidate/profile cardinality mismatch")
    return selected


def refusal_candidates(candidate_path=CANDIDATES, profile_path=PROFILES,
                       bias_path=BIAS):
    """Wave C rows whose recursive verdict is a refusal, not a finding.

    The frozen list is authoritative, but it is checked against the evidence on
    every call. A row that has since obtained a real verdict, or a new row that
    has since started refusing, changes the cohort, and a cohort that changed
    silently would make the resulting admissions unauditable.
    """
    bias = json.load(io.open(bias_path, encoding="utf-8")).get("results", {})
    wave_c = {row["strategy_id"] for row in _csv(candidate_path)
              if row["expansion_wave"] == "C_measurement_recovery"}
    derived = {strategy for strategy in wave_c
               if REFUSAL_MARKER in
               (((bias.get(strategy) or {}).get("recursive") or {}).get("why") or "")}
    frozen = set(WAVE_C_REFUSALS)
    if derived != frozen:
        raise ValueError(
            "Wave C refusal cohort drifted; frozen %s, evidence %s"
            % (sorted(frozen), sorted(derived)))
    profiles = {row["strategy_id"]: row for row in _csv(profile_path)}
    return [profiles[strategy] for strategy in WAVE_C_REFUSALS]


COHORTS = {"wave_b": candidates, "wave_c_refusals": refusal_candidates}


def _runtime(row, startup_candle_count):
    mode, base_config, env, repair, extra = profile_bias._runtime(row)
    config = json.load(io.open(base_config, encoding="utf-8"))
    config["startup_candle_count"] = startup_candle_count
    os.makedirs(CONFIG_DIR, exist_ok=True)
    path = os.path.join(CONFIG_DIR, "%s_startup_%d.json" % (
        _safe(row["strategy_id"]), startup_candle_count))
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)
    return mode, path, env, repair, extra


def identity(row, config, mode, repair, startup_candle_count):
    canonical = os.path.join(ROOT, row["canonical_file"].replace("/", os.sep))
    return {
        "implementation_id": row["implementation_id"],
        "canonical_sha256": _sha(canonical),
        "runtime_config_sha256": _sha(config),
        "run_profile": row["run_profile"],
        "mode": mode,
        "class1_rules": repair.get("rules", []),
        "diagnostic_rule": RULE,
        "startup_candle_count": startup_candle_count,
    }


def run_one(row, timeout, startup_candle_count):
    strategy = row["strategy_id"]
    canonical = os.path.join(ROOT, row["canonical_file"].replace("/", os.sep))
    mode, config, env, repair, extra = _runtime(row, startup_candle_count)
    strategy_path = profile_bias._isolated_strategy(row, canonical)
    original_directory = os.path.dirname(canonical)
    existing_imports = env.get("PROFILE_STRATEGY_IMPORT_PATH", "")
    env["PROFILE_STRATEGY_IMPORT_PATH"] = os.pathsep.join(
        [original_directory] + ([existing_imports] if existing_imports else []))
    timerange = profile_bias.WINDOWS[mode]
    command = [profile_bias.PYTHON, profile_bias.FT_WRAPPER,
               "recursive-analysis", "--config", config,
               "--strategy", strategy, "--strategy-path", strategy_path,
               "--timerange", timerange, "--no-color"] + extra
    started = time.time()
    try:
        process = subprocess.run(command, capture_output=True, timeout=timeout,
                                 env=env, cwd=ROOT)
        output = (process.stdout + process.stderr).decode("utf-8", "replace")
        status, why = profile_bias._recursive(output, process.returncode)
        result = identity(row, config, mode, repair, startup_candle_count)
        result.update({
            "status": status,
            "why": why,
            # The verdict is a threshold decision and discards the numbers
            # behind it. The convergence route needs them to see how far a row
            # still is from its band, so they are retained alongside, without
            # changing what the frozen gate itself decides.
            "drifts": profile_bias.recursive_drifts(output),
            "timerange": timerange,
            "elapsed_s": round(time.time() - started, 1),
            "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned"),
            "output_sha256": "sha256_" + hashlib.sha256(
                output.encode("utf-8")).hexdigest(),
            "admission_effect": "none_pilot_only",
        })
        # The analyzer output is retained for every outcome, not only for a
        # failure. On 2026-09-01 nine rows were recorded as converged because
        # freqtrade had refused the run and exited 0; those passes carried no
        # log, so the mistake could only be found by reproducing a run by hand.
        # A pass is exactly the outcome whose evidence you later want to check.
        os.makedirs(LOG_DIR, exist_ok=True)
        log_path = os.path.join(LOG_DIR, "%s-recursive-startup-%d.log" % (
            _safe(strategy), startup_candle_count))
        with io.open(log_path, "w", encoding="utf-8") as handle:
            handle.write(output)
        result["debug_log"] = os.path.relpath(log_path, ROOT).replace(os.sep, "/")
        return result
    except subprocess.TimeoutExpired:
        result = identity(row, config, mode, repair, startup_candle_count)
        result.update({
            "status": "NA", "why": "TIMEOUT", "timerange": timerange,
            "elapsed_s": round(time.time() - started, 1),
            "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned"),
            "admission_effect": "none_pilot_only",
        })
        return result


def selftest():
    manifest = {"candidate_members": {"B_warmup_refusal": ["A|spot_long|A:1"]}}
    row = {"strategy_id": "A", "run_profile": "spot_long", "implementation_id": "A:1"}
    assert "%s|%s|%s" % (row["strategy_id"], row["run_profile"],
                           row["implementation_id"]) in \
        set(manifest["candidate_members"]["B_warmup_refusal"])
    assert _safe("A B/C") == "A_B_C"

    # The Wave C refusal cohort must still match the stored evidence exactly.
    refusals = refusal_candidates()
    assert [row["strategy_id"] for row in refusals] == list(WAVE_C_REFUSALS)
    assert len(WAVE_C_REFUSALS) == 7
    # A refusal is not a bias finding, so none of these rows may already carry
    # a real recursive verdict.
    bias = json.load(io.open(BIAS, encoding="utf-8"))["results"]
    for strategy in WAVE_C_REFUSALS:
        assert REFUSAL_MARKER in bias[strategy]["recursive"]["why"]
    # Wave B is untouched by the second cohort.
    assert len(candidates()) == 82
    assert not set(WAVE_C_REFUSALS) & {row["strategy_id"] for row in candidates()}
    print("eligibility_warmup selftest: PASS (%d Wave B, %d Wave C refusals)"
          % (len(candidates()), len(refusals)))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--skip", action="append", default=[])
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--startup-candle-count", type=int,
                        default=DEFAULT_OVERRIDE)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cohort", default="wave_b", choices=sorted(COHORTS),
                        help="wave_b is the frozen 82-row refusal wave; "
                             "wave_c_refusals is the 7 Wave C rows the "
                             "analyzer refused rather than judged")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.startup_candle_count < 1:
        raise SystemExit("startup-candle-count must be positive")
    rows = COHORTS[args.cohort]()
    if args.only:
        wanted = set(args.only)
        rows = [row for row in rows if row["strategy_id"] in wanted]
    if args.skip:
        skipped = set(args.skip)
        rows = [row for row in rows if row["strategy_id"] not in skipped]
    rows = rows[:args.limit]
    data = _load(OUTPUT)
    for number, row in enumerate(rows, 1):
        strategy = row["strategy_id"]
        stored = data["results"].get(strategy, {})
        attempts = stored.get("attempts", {})
        attempt_key = str(args.startup_candle_count)
        if not args.force and attempt_key in attempts:
            continue
        print("[%d/%d] %s recursive startup=%d" %
              (number, len(rows), strategy, args.startup_candle_count), flush=True)
        result = run_one(row, args.timeout, args.startup_candle_count)
        attempts[attempt_key] = result
        data["results"][strategy] = {
            "attempts": attempts,
            "latest_startup_candle_count": args.startup_candle_count,
        }
        _write_json(OUTPUT, data)
        print("  %s: %s" % (result["status"], result["why"]), flush=True)
    print("warmup pilot records: %d" % len(data["results"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
