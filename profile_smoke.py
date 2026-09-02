# -*- coding: utf-8 -*-
"""Mode-correct smoke backtests for the canonical execution-profile manifest.

The result answers only two runtime questions: did the strategy produce a valid
Freqtrade result in this mode/window, and how many resulting trades were long
or short?  A zero count never removes a statically detected capability.
"""
from __future__ import print_function

import argparse
import csv
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import zipfile


import runlog


ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
OUTPUT = os.path.join(ROOT, "PROFILE_SMOKE.json")
FUTURES_CONFIG = os.path.join(ROOT, "profile_futures_config.json")
SPOT_CONFIG = os.path.join(ROOT, "profile_spot_config.json")
# Use the interpreter running this pipeline. PROFILE_PYTHON remains available
# for an explicit isolated runtime, while Docker/WSL can use their own Python.
PYTHON = os.environ.get("PROFILE_PYTHON", sys.executable)

# A store claim older than this belongs to a runner that no longer exists.
# Two hours is longer than any single run has ever taken.
STALE_CLAIM_S = 2 * 60 * 60
FT_WRAPPER = os.path.join(ROOT, "profile_freqtrade.py")
CLASS1 = os.path.join(ROOT, "PROFILE_CLASS1.json")
EXPORT_DIR = os.path.join(ROOT, "user_data", "profile_smoke")
CONFIG_DIR = os.path.join(ROOT, "user_data", "profile_configs")
LOG_DIR = os.path.join(ROOT, "user_data", "profile_smoke_logs")


def read_manifest(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_results(path):
    if not os.path.exists(path):
        return {"schema_version": 1, "results": {}}
    with io.open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data.setdefault("schema_version", 1)
    data.setdefault("results", {})
    return data


def write_results(data, path):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def _jsonc(text):
    """Remove // and /* */ comments without touching quoted strings."""
    out = []
    index = 0
    quoted = False
    escaped = False
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if quoted:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            index += 1
        elif char == '"':
            quoted = True
            out.append(char)
            index += 1
        elif char == "/" and nxt == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
        elif char == "/" and nxt == "*":
            index += 2
            while index + 1 < len(text) and text[index:index + 2] != "*/":
                index += 1
            index += 2
        else:
            out.append(char)
            index += 1
    uncommented = "".join(out)
    out = []
    quoted = False
    escaped = False
    for index, char in enumerate(uncommented):
        if quoted:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
            out.append(char)
        elif char == ",":
            lookahead = index + 1
            while lookahead < len(uncommented) and uncommented[lookahead].isspace():
                lookahead += 1
            if lookahead >= len(uncommented) or uncommented[lookahead] not in "}]":
                out.append(char)
        else:
            out.append(char)
    return "".join(out)


def _read_jsonc(path):
    with io.open(path, encoding="utf-8-sig") as handle:
        return json.loads(_jsonc(handle.read()))


def _class1(strategy):
    if not os.path.exists(CLASS1):
        return {}
    return _read_jsonc(CLASS1).get("strategies", {}).get(strategy, {})


def _runtime(strategy, mode="futures"):
    repair = _class1(strategy)
    base_config = FUTURES_CONFIG if mode == "futures" else SPOT_CONFIG
    config_path = base_config
    source = repair.get("config_source")
    if source:
        config = _read_jsonc(base_config)
        author = _read_jsonc(os.path.join(ROOT, source.replace("/", os.sep)))
        for key in repair.get("config_keys", []):
            if key not in author:
                raise ValueError("author config key missing: %s" % key)
            config[key] = author[key]
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config_path = os.path.join(CONFIG_DIR, _safe(strategy) + ".json")
        with io.open(config_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")

    env = os.environ.copy()
    python_paths = [os.path.join(ROOT, value.replace("/", os.sep))
                    for value in repair.get("python_paths", [])]
    if python_paths:
        previous = env.get("PYTHONPATH")
        env["PYTHONPATH"] = os.pathsep.join(python_paths + ([previous] if previous else []))
    # A rule that names a signature adapter is passed to the wrapper, which
    # installs it inside the freqtrade process before the strategy is loaded.
    adapters = list(repair.get("rules", []))
    if adapters:
        env["PROFILE_COMPAT_SIGNATURES"] = ",".join(adapters)
    extension_paths = [os.path.join(ROOT, value.replace("/", os.sep))
                       for value in repair.get("freqtrade_paths", [])]
    if extension_paths:
        env["PROFILE_FREQTRADE_PATH"] = os.pathsep.join(extension_paths)
    extra_args = []
    if repair.get("freqaimodel"):
        extra_args.extend(["--freqaimodel", repair["freqaimodel"]])
    if repair.get("freqaimodel_path"):
        model_path = os.path.join(ROOT, repair["freqaimodel_path"].replace("/", os.sep))
        extra_args.extend(["--freqaimodel-path", model_path])
    return config_path, env, repair, extra_args


def _override_config(strategy, config_path, overrides):
    """Write a deterministic top-level config overlay for controlled diagnostics."""
    config = _read_jsonc(config_path)
    config.update(overrides)
    semantic = json.dumps(overrides, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(semantic.encode("utf-8")).hexdigest()[:12]
    os.makedirs(CONFIG_DIR, exist_ok=True)
    path = os.path.join(CONFIG_DIR, "%s-override-%s.json" %
                        (_safe(strategy), digest))
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)
    return path


def _identity(row):
    """Bind every result to the exact canonical code and effective config."""
    canonical = os.path.abspath(os.path.join(
        ROOT, row["canonical_file"].replace("/", os.sep)))
    mode = "futures" if row["run_profile"].startswith("futures_") else "spot"
    config_path, _env, _repair, _args = _runtime(row["strategy_id"], mode)
    identities = {}
    for field, path in (("canonical_sha256", canonical),
                        ("runtime_config_sha256", config_path)):
        with io.open(path, "rb") as handle:
            identities[field] = "sha256_" + hashlib.sha256(handle.read()).hexdigest()
    return identities


def _safe(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def _sha256_file(path):
    with io.open(path, "rb") as handle:
        return "sha256_" + hashlib.sha256(handle.read()).hexdigest()


def _error(output, returncode):
    errors = re.findall(r"(?:ERROR - |(?:Error|Exception): )(.+)", output)
    if errors:
        return errors[-1].strip()[:300]
    return "process exit %d without a readable backtest archive" % returncode


def _archive(prefix, started):
    candidates = [
        path for path in glob.glob(prefix + "-*.zip")
        if os.path.getmtime(path) >= started - 2
    ]
    return max(candidates, key=os.path.getmtime) if candidates else None


def _trades(archive, strategy):
    with zipfile.ZipFile(archive) as bundle:
        members = [name for name in bundle.namelist()
                   if name.endswith(".json") and not name.endswith("_config.json")]
        data = None
        for member in members:
            candidate = json.loads(bundle.read(member).decode("utf-8"))
            if strategy in (candidate.get("strategy") or {}):
                data = candidate
                break
    if data is None:
        raise ValueError("strategy missing from result JSON members")
    strategies = data["strategy"]
    trades = strategies[strategy].get("trades") or []
    shorts = sum(bool(trade.get("is_short")) for trade in trades)
    semantic = json.dumps(trades, sort_keys=True, separators=(",", ":"))
    return (len(trades) - shorts, shorts,
            "sha256_" + hashlib.sha256(semantic.encode("utf-8")).hexdigest())


def _invocation(command):
    """The freqtrade call, as a string a reader can paste, paths relative."""
    root = os.path.normcase(os.path.abspath(ROOT))
    parts = []
    for item in command[1:]:          # the interpreter is an implementation detail
        text = str(item)
        # Paths are made relative so the line is the same on any machine, and
        # comparing normcase means it works whichever separator built them.
        if os.path.isabs(text) and os.path.normcase(text).startswith(root):
            text = os.path.relpath(text, ROOT).replace(os.sep, "/")
        parts.append('"%s"' % text if " " in text else text)
    if parts and parts[0].endswith("profile_freqtrade.py"):
        parts[0] = "freqtrade"
    return " ".join(parts)


def run_one(row, timerange, timeout, pair=None, extra_env=None,
            config_overrides=None):
    strategy = row["strategy_id"]
    canonical = os.path.abspath(os.path.join(ROOT, row["canonical_file"].replace("/", os.sep)))
    profile = row["run_profile"]
    mode = "futures" if profile.startswith("futures_") else "spot"
    if not os.path.exists(canonical):
        raise ValueError("canonical source not found: %s" % row["canonical_file"])

    os.makedirs(EXPORT_DIR, exist_ok=True)
    suffix = "-" + _safe(pair) if pair else ""
    prefix = os.path.join(EXPORT_DIR, _safe(strategy) + suffix)
    try:
        config_path, env, class1, extra_args = _runtime(strategy, mode)
        if config_overrides:
            config_path = _override_config(strategy, config_path, config_overrides)
        if extra_env:
            env.update(extra_env)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return {"status": "failed", "mode": mode, "run_profile": profile,
                "timerange": timerange, "elapsed_s": 0,
                "why": "Class 1 runtime setup failed: %s" % exc}
    cmd = [
        PYTHON, FT_WRAPPER, "backtesting", "--config", config_path,
        "--strategy", strategy, "--strategy-path", os.path.dirname(canonical),
        "--timerange", timerange, "--fee", "0.001", "--export", "trades",
        "--backtest-directory", prefix, "--cache", "none",
    ] + (["--pairs", pair] if pair else []) + extra_args
    # The invocation is part of the result. Without it a record says what came
    # out but not what was asked, and a reader cannot reproduce the run without
    # re-deriving the arguments from four other files.
    invocation = _invocation(cmd)
    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout)
        output = proc.stdout.decode("utf-8", "replace")
        runlog.append("backtesting", strategy, invocation, output,
                      {"run_profile": profile, "timerange": timerange,
                       "returncode": proc.returncode,
                       "elapsed_s": round(time.time() - started, 1)})
    except subprocess.TimeoutExpired:
        runlog.append("backtesting", strategy, invocation, "",
                      {"run_profile": profile, "timerange": timerange,
                       "outcome": "timeout after %d seconds" % timeout})
        return {"status": "timeout", "mode": mode, "run_profile": profile,
                "timerange": timerange, "elapsed_s": round(time.time() - started, 1),
                "class1_rules": class1.get("rules", []),
                "why": "timeout after %d seconds" % timeout,
                "invocation": invocation}

    archive = _archive(prefix, started)
    if not archive:
        os.makedirs(LOG_DIR, exist_ok=True)
        log_path = os.path.join(LOG_DIR, _safe(strategy) + suffix + ".log")
        with io.open(log_path, "w", encoding="utf-8") as handle:
            handle.write(output)
        return {"status": "failed", "mode": mode, "run_profile": profile,
                "timerange": timerange, "elapsed_s": round(time.time() - started, 1),
                "class1_rules": class1.get("rules", []),
                "why": _error(output, proc.returncode),
                "invocation": invocation,
                "debug_log": os.path.relpath(log_path, ROOT).replace(os.sep, "/")}
    try:
        longs, shorts, trades_sha256 = _trades(archive, strategy)
    except (ValueError, KeyError, zipfile.BadZipFile) as exc:
        return {"status": "failed", "mode": mode, "run_profile": profile,
                "timerange": timerange, "elapsed_s": round(time.time() - started, 1),
                "class1_rules": class1.get("rules", []),
                "why": "%s: %s" % (type(exc).__name__, exc)}
    with io.open(archive, "rb") as archive_handle:
        archive_sha256 = "sha256_" + hashlib.sha256(archive_handle.read()).hexdigest()
    runtime_config_sha256 = _sha256_file(config_path)
    return {"status": "measured", "mode": mode, "run_profile": profile,
            "timerange": timerange, "elapsed_s": round(time.time() - started, 1),
            "class1_rules": class1.get("rules", []), "invocation": invocation,
            "long_trades": longs, "short_trades": shorts,
            "trades": longs + shorts, "trades_sha256": trades_sha256,
            "archive": os.path.relpath(archive, ROOT).replace(os.sep, "/"),
            "archive_sha256": archive_sha256,
            "runtime_config_sha256": runtime_config_sha256,
            "config_overrides": config_overrides or {},
            "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned")}


def select(rows, strategies, profiles, limit):
    chosen = []
    wanted = set(strategies or [])
    for row in rows:
        if wanted and row["strategy_id"] not in wanted:
            continue
        if row["run_profile"] not in profiles:
            continue
        chosen.append(row)
    if wanted:
        missing = wanted - {row["strategy_id"] for row in chosen}
        if missing:
            raise SystemExit("not selected from manifest: %s" % ", ".join(sorted(missing)))
    return chosen[:limit] if limit else chosen


def selftest():
    assert _safe("A/B C") == "A_B_C"
    rows = [{"strategy_id": "A", "run_profile": "futures_long"},
            {"strategy_id": "B", "run_profile": "spot_long"}]
    assert [r["strategy_id"] for r in select(rows, [], {"futures_long"}, 0)] == ["A"]
    sample = '{"url":"https://example.invalid/a//b",// c\n"x":1,/*d*/}'
    assert json.loads(_jsonc(sample))["x"] == 1
    print("profile_smoke selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=MANIFEST)
    parser.add_argument("--output", default=OUTPUT)
    parser.add_argument("--strategy", action="append", default=[])
    parser.add_argument("--profiles", nargs="+", default=[
        "futures_long", "futures_short", "futures_long_short"])
    parser.add_argument("--timerange", default="20200301-20200401")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0

    rows = select(read_manifest(args.manifest), args.strategy, set(args.profiles), args.limit)
    # A second runner on the same store loses whatever the first wrote after it
    # started: each holds the whole file in memory and rewrites it. That
    # happened on 2026-09-01 and cost three measurements. The claim is taken
    # for the life of the run, not per write, because the harm is two runs
    # overlapping at all rather than two writes colliding.
    claim = args.output + ".running"
    try:
        os.mkdir(claim)
    except OSError:
        # A killed container leaves the claim behind, and a claim nobody holds
        # must not wedge the store for good. One that has not been touched for
        # STALE_CLAIM_S is taken over, with a line saying so.
        age = time.time() - os.path.getmtime(claim) if os.path.exists(claim) else 0
        if age < STALE_CLAIM_S:
            raise SystemExit(
                "another runner already holds %s (%s exists, %d s old). Give "
                "this run its own --output, or wait for that one to finish."
                % (os.path.basename(args.output), os.path.basename(claim), age))
        print("taking over a claim last touched %d s ago; the runner that made "
              "it is gone" % age, flush=True)
        os.utime(claim, None)
    try:
        return _run(args, rows, claim)
    finally:
        try:
            os.rmdir(claim)
        except OSError:
            pass


def _run(args, rows, claim):
    data = read_results(args.output)
    data["timerange"] = args.timerange
    data["config"] = os.path.basename(FUTURES_CONFIG)
    print("profile smoke candidates: %d" % len(rows), flush=True)
    for index, row in enumerate(rows, 1):
        name = row["strategy_id"]
        previous = data["results"].get(name)
        try:
            identity = _identity(row)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            identity = {"identity_error": "%s: %s" % (type(exc).__name__, exc)}
        if previous and not args.force:
            previous.update(identity)
            write_results(data, args.output)
            print("[%d/%d] %-38s skip" % (index, len(rows), name), flush=True)
            continue
        result = run_one(row, args.timerange, args.timeout)
        result.update(identity)
        result["runtime_id"] = os.environ.get(
            "PROFILE_RUNTIME_ID", "native_unversioned")
        data["results"][name] = result
        write_results(data, args.output)
        detail = ("L=%s S=%s" % (result.get("long_trades"), result.get("short_trades"))
                  if result["status"] == "measured" else result.get("why", ""))
        print("[%d/%d] %-38s %-8s %s" %
              (index, len(rows), name, result["status"], detail), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
