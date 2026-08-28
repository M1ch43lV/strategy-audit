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


ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
OUTPUT = os.path.join(ROOT, "PROFILE_SMOKE.json")
FUTURES_CONFIG = os.path.join(ROOT, "profile_futures_config.json")
# Use the interpreter running this pipeline. PROFILE_PYTHON remains available
# for an explicit isolated runtime, while Docker/WSL can use their own Python.
PYTHON = os.environ.get("PROFILE_PYTHON", sys.executable)
FT_WRAPPER = os.path.join(ROOT, "profile_freqtrade.py")
CLASS1 = os.path.join(ROOT, "PROFILE_CLASS1.json")
EXPORT_DIR = os.path.join(ROOT, "user_data", "profile_smoke")
CONFIG_DIR = os.path.join(ROOT, "user_data", "profile_configs")


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


def _runtime(strategy):
    repair = _class1(strategy)
    config_path = FUTURES_CONFIG
    source = repair.get("config_source")
    if source:
        config = _read_jsonc(FUTURES_CONFIG)
        author = _read_jsonc(os.path.join(ROOT, source.replace("/", os.sep)))
        for key in repair.get("config_keys", []):
            if key not in author:
                raise ValueError("author config key missing: %s" % key)
            config[key] = author[key]
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config_path = os.path.join(CONFIG_DIR, _safe(strategy) + ".json")
        with io.open(config_path, "w", encoding="utf-8") as handle:
            json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")

    env = os.environ.copy()
    python_paths = [os.path.join(ROOT, value.replace("/", os.sep))
                    for value in repair.get("python_paths", [])]
    if python_paths:
        previous = env.get("PYTHONPATH")
        env["PYTHONPATH"] = os.pathsep.join(python_paths + ([previous] if previous else []))
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


def _identity(row):
    """Bind every result to the exact canonical code and effective config."""
    canonical = os.path.abspath(os.path.join(
        ROOT, row["canonical_file"].replace("/", os.sep)))
    config_path, _env, _repair, _args = _runtime(row["strategy_id"])
    identities = {}
    for field, path in (("canonical_sha256", canonical),
                        ("runtime_config_sha256", config_path)):
        with io.open(path, "rb") as handle:
            identities[field] = "sha256_" + hashlib.sha256(handle.read()).hexdigest()
    return identities


def _safe(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


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
    return len(trades) - shorts, shorts


def run_one(row, timerange, timeout):
    strategy = row["strategy_id"]
    canonical = os.path.abspath(os.path.join(ROOT, row["canonical_file"].replace("/", os.sep)))
    profile = row["run_profile"]
    if not profile.startswith("futures_"):
        raise ValueError("only futures profiles are currently supported by this runner")
    if not os.path.exists(canonical):
        raise ValueError("canonical source not found: %s" % row["canonical_file"])

    os.makedirs(EXPORT_DIR, exist_ok=True)
    prefix = os.path.join(EXPORT_DIR, _safe(strategy))
    try:
        config_path, env, class1, extra_args = _runtime(strategy)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return {"status": "failed", "mode": "futures", "run_profile": profile,
                "timerange": timerange, "elapsed_s": 0,
                "why": "Class 1 runtime setup failed: %s" % exc}
    cmd = [
        PYTHON, FT_WRAPPER, "backtesting", "--config", config_path,
        "--strategy", strategy, "--strategy-path", os.path.dirname(canonical),
        "--timerange", timerange, "--fee", "0.001", "--export", "trades",
        "--backtest-directory", prefix, "--cache", "none",
    ] + extra_args
    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout)
        output = proc.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "mode": "futures", "run_profile": profile,
                "timerange": timerange, "elapsed_s": round(time.time() - started, 1),
                "class1_rules": class1.get("rules", []),
                "why": "timeout after %d seconds" % timeout}

    archive = _archive(prefix, started)
    if not archive:
        return {"status": "failed", "mode": "futures", "run_profile": profile,
                "timerange": timerange, "elapsed_s": round(time.time() - started, 1),
                "class1_rules": class1.get("rules", []),
                "why": _error(output, proc.returncode)}
    try:
        longs, shorts = _trades(archive, strategy)
    except (ValueError, KeyError, zipfile.BadZipFile) as exc:
        return {"status": "failed", "mode": "futures", "run_profile": profile,
                "timerange": timerange, "elapsed_s": round(time.time() - started, 1),
                "class1_rules": class1.get("rules", []),
                "why": "%s: %s" % (type(exc).__name__, exc)}
    return {"status": "measured", "mode": "futures", "run_profile": profile,
            "timerange": timerange, "elapsed_s": round(time.time() - started, 1),
            "class1_rules": class1.get("rules", []),
            "long_trades": longs, "short_trades": shorts,
            "trades": longs + shorts}


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
