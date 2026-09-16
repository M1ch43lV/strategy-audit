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
import shutil
import subprocess
import sys
import threading
import time
import zipfile


from runtime import runlog
from repair.overrides import repair_overrides


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "evidence/EXECUTION_PROFILES.csv")
OUTPUT = os.path.join(ROOT, "evidence/PROFILE_SMOKE.json")
SMOKE_TIMERANGES = (
    "20200301-20200401",
    "20200301-20200601",
)
SMOKE_TRADE_FLOOR = 10
# The one-year third rung is gone (2026-09-15): the NNPredict_* cluster
# showed it buys an hour of retraining per strategy for a verdict the
# three-month rung already gives just as reliably - zero trades at three
# months turned out to mean zero trades at one year too, every time it was
# checked, once the actual bug (a pandas chained-assignment no-op, not a
# short window) was found and fixed. A trade-poor row now stops at the
# three-month rung; whether that is "the strategy genuinely does not trade"
# or "something upstream of this window is broken" is the next stage's
# question, not a longer smoke window's. The version bump means a low
# result recorded under the old three-rung policy is deliberately stale -
# see _result_is_current() below - and gets exactly this shorter cascade
# the next time it is asked for, not silently reused.
SMOKE_POLICY_ID = "fixed_1m_3m_until_10_trades_v2"
FUTURES_CONFIG = os.path.join(ROOT, "runtime", "profile_futures_config.json")
SPOT_CONFIG = os.path.join(ROOT, "runtime", "profile_spot_config.json")
# Use the interpreter running this pipeline. PROFILE_PYTHON remains available
# for an explicit isolated runtime, while Docker/WSL can use their own Python.
PYTHON = os.environ.get("PROFILE_PYTHON", sys.executable)

# A store claim older than this belongs to a runner that no longer exists.
# Two hours is longer than any single run has ever taken.
STALE_CLAIM_S = 2 * 60 * 60
FT_WRAPPER = os.path.join(ROOT, "evidence/profile_freqtrade.py")
CLASS1 = os.path.join(ROOT, "evidence/PROFILE_CLASS1.json")
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
        # Same deterministic-path hazard as `_override_config`, one step
        # worse: this wrote straight to the final name with no tmp file at
        # all, so a second pair shard's writer could read the first's
        # half-written JSON rather than merely losing a race on the rename.
        # No admitted row uses `config_source` yet, but the benchmark run
        # this is for adds workers and strategies, not fewer of either.
        tmp = "%s.%d.%d.tmp" % (config_path, os.getpid(), threading.get_ident())
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp, config_path)

    env = os.environ.copy()
    # Windows' console default (cp1252) cannot encode plain author output
    # (an ASCII-art banner in AlexBandSniperV10AI's own __init__, found
    # 2026-09-14) - UnicodeEncodeError before backtesting even starts, not a
    # strategy problem. setdefault so an already-set encoding is respected.
    env.setdefault("PYTHONIOENCODING", "utf-8")
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
    # TF_USE_LEGACY_KERAS is read by TensorFlow itself at its own first
    # import, before any of this project's own compat shims get a chance to
    # run inside the process - so it has to reach the subprocess as a real
    # OS environment variable, not a patch applied from within. Redirects
    # every `tf.keras.*` access to the standalone `tf_keras` package (Keras
    # 2) for this one subprocess; a bare `import keras` elsewhere in the
    # same strategy is untouched, since only `tf.keras` is redirected - see
    # repair/compat_signature.py's tf_keras_bare_*_redirect shims for the
    # narrow, opt-in fix for a strategy whose own code mixes both spellings.
    if repair.get("tf_use_legacy_keras"):
        env["TF_USE_LEGACY_KERAS"] = "1"
    _stage_working_dir_data(repair)
    extra_args = []
    if repair.get("freqaimodel"):
        extra_args.extend(["--freqaimodel", repair["freqaimodel"]])
    if repair.get("freqaimodel_path"):
        model_path = os.path.join(ROOT, repair["freqaimodel_path"].replace("/", os.sep))
        extra_args.extend(["--freqaimodel-path", model_path])
    return config_path, env, repair, extra_args


def _stage_working_dir_data(repair):
    """Place a `data_files` entry that names a `dest` into the run's cwd.

    Two shapes of author-shipped input need two different destinations, and
    the difference is the strategy's own code, not a preference. A strategy
    that resolves its input from `__file__` wants the file beside itself,
    which it already is under `repos/` - only the bias runner's isolated copy
    needs it staged, and `profile_bias._stage_data_files` does that. A
    strategy that resolves from a relative path instead wants it under the
    working directory every runner uses (ROOT): `QuatreMousquetaires` reads
    `./user_data/tv_data/NASDAQ_daily_data.csv` and its three siblings, so an
    entry with an explicit `dest` is copied there for every run.

    The copy's mtime is today's, which for this strategy means its own
    24-hour freshness cache treats the series as current and never calls
    TradingView. That is the author's caching logic reading the author's own
    shipped file; the content is theirs, only the timestamp is ours, and the
    series covers the measurement window. Recopied on every run rather than
    once, because the file lands under `user_data/` - regenerable by design,
    and cleared often.
    """
    for entry in repair.get("data_files", []):
        if not isinstance(entry, dict) or not entry.get("dest"):
            continue
        source = os.path.join(ROOT, entry["source"].replace("/", os.sep))
        target = os.path.join(ROOT, entry["dest"].replace("/", os.sep))
        if not os.path.exists(source):
            print("  data_files: source missing, not staged: %s" % entry["source"],
                  flush=True)
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        temporary = "%s.%d.tmp" % (target, os.getpid())
        shutil.copyfile(source, temporary)
        os.replace(temporary, target)


def _override_config(strategy, config_path, overrides):
    """Write a deterministic top-level config overlay for controlled diagnostics.

    The target path is deterministic in the overrides, so two pair shards of
    the same strategy - run concurrently by `profile_full_window`'s thread
    pool - compute the same path and race to write it. Each writer gets its
    own tmp name (pid + thread id) so the two never touch the same file; the
    final `os.replace` is then a no-op race over identical content rather
    than a "the other thread already deleted my tmp file" ENOENT.
    """
    config = _read_jsonc(config_path)
    config.update(overrides)
    semantic = json.dumps(overrides, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(semantic.encode("utf-8")).hexdigest()[:12]
    os.makedirs(CONFIG_DIR, exist_ok=True)
    path = os.path.join(CONFIG_DIR, "%s-override-%s.json" %
                        (_safe(strategy), digest))
    tmp = "%s.%d.%d.tmp" % (path, os.getpid(), threading.get_ident())
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
    """A filesystem-safe name that never collides across strategies.

    The corpus carries ten pairs of strategy IDs that differ only in case -
    `SuperTrend` and `Supertrend`, `BBRSI` and `bbrsi`, `mabStra` and
    `MabStra`, among others - genuinely different strategies from different
    source files. Windows' default filesystem is case-INsensitive, so the old
    version of this function, which only stripped illegal characters and left
    case alone, sent both members of every such pair to the identical path.
    Whichever one ran later silently overwrote the earlier one's log, and
    for the isolated strategy directory (`profile_bias._isolated_strategy`)
    put two different strategies' source files side by side in one directory
    - already a documented hazard here (`AutoArimaTripleV1.py` opens a log at
    import time and kills any gate pointed at its directory).

    A short hash of the ORIGINAL, case-preserved name is appended, so two
    names that fold to the same lowercase form still diverge. This changes
    the path only for RUNS FROM NOW ON; every already-written `debug_log`
    field in the stores still points at the file it was written to, and nothing
    reads a path back through this function to find it again.
    """
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
    return "%s-%s" % (stem, hashlib.sha256(name.encode("utf-8")).hexdigest()[:8])


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
    if parts and parts[0].endswith("evidence/profile_freqtrade.py"):
        parts[0] = "freqtrade"
    return " ".join(parts)


def run_one(row, timerange, timeout, pair=None, extra_env=None,
            config_overrides=None, artifact_key=None, run_context=None):
    strategy = row["strategy_id"]
    canonical = os.path.abspath(os.path.join(ROOT, row["canonical_file"].replace("/", os.sep)))
    profile = row["run_profile"]
    mode = "futures" if profile.startswith("futures_") else "spot"
    if not os.path.exists(canonical):
        raise ValueError("canonical source not found: %s" % row["canonical_file"])

    os.makedirs(EXPORT_DIR, exist_ok=True)
    suffix_source = artifact_key if artifact_key is not None else pair
    suffix = "-" + _safe(suffix_source) if suffix_source else ""
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
    run_metadata = {"run_profile": profile, "timerange": timerange}
    if run_context:
        run_metadata.update(run_context)
    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout)
        output = proc.stdout.decode("utf-8", "replace")
        runlog.append("backtesting", strategy, invocation, output,
                      dict(run_metadata, returncode=proc.returncode,
                           elapsed_s=round(time.time() - started, 1)))
    except subprocess.TimeoutExpired:
        runlog.append("backtesting", strategy, invocation, "",
                      dict(run_metadata, outcome="timeout after %d seconds" % timeout))
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
        # SIGKILL with nothing in the output is the Linux OOM killer, not the
        # strategy: freqtrade never got a chance to log why it died. A pooled
        # run shares one memory ceiling (.wslconfig) across several concurrent
        # processes, so this says which process lost, not that the strategy is
        # broken - a genuine crash (segfault, exception) still reaches `_error`
        # below and stays "failed".
        if proc.returncode == -9:
            return {"status": "resource_inconclusive", "mode": mode,
                    "run_profile": profile, "timerange": timerange,
                    "elapsed_s": round(time.time() - started, 1),
                    "class1_rules": class1.get("rules", []),
                    "why": ("killed by SIGKILL (-9) with no exception logged: "
                            "the OOM killer, not the strategy - retry with "
                            "less concurrent load before treating this as a "
                            "strategy defect"),
                    "invocation": invocation,
                    "debug_log": os.path.relpath(log_path, ROOT).replace(os.sep, "/")}
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
            "artifact_key": artifact_key or "",
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


def _policy_id(timeranges, trade_floor):
    if (tuple(timeranges) == SMOKE_TIMERANGES
            and trade_floor == SMOKE_TRADE_FLOOR):
        return SMOKE_POLICY_ID
    semantic = json.dumps({"timeranges": list(timeranges),
                           "trade_floor": trade_floor}, sort_keys=True)
    return "custom_" + hashlib.sha256(semantic.encode("utf-8")).hexdigest()[:12]


def run_cascade(row, timeranges, trade_floor, timeout, config_overrides=None,
                policy_id=None):
    """Widen a successful but trade-poor smoke run by a frozen rule.

    Runtime failures are not evidence that a longer market interval helps, so
    only a measured result below the floor advances to the next rung.  Every
    attempt is retained; the last attempted rung remains the top-level result
    consumed by the existing status and adjudication readers.
    """
    policy_id = policy_id or _policy_id(timeranges, trade_floor)
    attempts = []
    final = None
    for timerange in timeranges:
        result = run_one(
            row, timerange, timeout, config_overrides=config_overrides,
            artifact_key="smoke_%s" % timerange.replace("-", "_"),
            run_context={"smoke_policy_id": policy_id,
                         "trade_floor": trade_floor,
                         "rung": len(attempts) + 1},
        )
        attempts.append(result)
        final = result
        if result.get("status") != "measured":
            break
        if int(result.get("trades", 0)) >= trade_floor:
            break
    final = dict(final or {})
    final["smoke_policy_id"] = policy_id
    final["trade_floor"] = trade_floor
    final["attempted_timeranges"] = [item.get("timerange") for item in attempts]
    final["attempts"] = attempts
    return final


def _result_is_current(previous, identity, timeranges, trade_floor):
    if not previous or not all(previous.get(key) == value
                               for key, value in identity.items()):
        return False
    # A prior failure is unrelated to interval length, and a prior result that
    # already reached the floor needs no wider diagnostic window.
    if previous.get("status") != "measured":
        return True
    if int(previous.get("trades", 0)) >= trade_floor:
        return True
    # A low-trade result is current once every rung the CURRENT policy would
    # try was already attempted - not only when the two rung lists match
    # exactly. Prefix, not equality: when a policy amendment only ever
    # shortens the cascade (2026-09-15 dropped the one-year third rung), a
    # row that already tried the dropped rung, and stayed under the floor
    # anyway, has already answered every question the shorter policy would
    # ask - it just also tried one rung further and got the same answer.
    # Re-running it would repeat rungs, not learn anything the stored
    # attempt does not already show. Confirmed against the 17 rows the
    # 2026-09-15 amendment affects: every one of them had already reached
    # the three-month rung (most the one-year rung too), none had tried only
    # one month - re-running any of them under the shorter policy would have
    # been pure waste, not new evidence.
    attempted = previous.get("attempted_timeranges") or []
    return attempted[:len(timeranges)] == list(timeranges)


def selftest():
    assert _safe("A/B C").startswith("A_B_C-")
    # The whole point: two names differing only in case must never collide,
    # because Windows' default filesystem folds case and ten such pairs are
    # real, different strategies in this corpus.
    assert _safe("SuperTrend") != _safe("Supertrend")
    assert _safe("SuperTrend").lower() != _safe("Supertrend").lower()
    assert _safe("SuperTrend") == _safe("SuperTrend")
    rows = [{"strategy_id": "A", "run_profile": "futures_long"},
            {"strategy_id": "B", "run_profile": "spot_long"}]
    assert [r["strategy_id"] for r in select(rows, [], {"futures_long"}, 0)] == ["A"]
    sample = '{"url":"https://example.invalid/a//b",// c\n"x":1,/*d*/}'
    assert json.loads(_jsonc(sample))["x"] == 1

    # A stored record is only skipped when its OWN identity still matches
    # the file on disk today - not merely because a record exists at all.
    # Three real rows (NostalgiaForInfinityX7, RLAgentStrategy,
    # MomentumRegimeBasket15m) had their canonical_sha256 silently stamped
    # onto a pre-upstream-update result before this was fixed.
    import argparse as _argparse
    import tempfile
    global _identity, run_one, _class1
    saved_identity, saved_run_one, saved_class1 = _identity, run_one, _class1
    calls = []
    _identity = lambda row: {"canonical_sha256": row["_sha"]}
    counts = {"a": 1, "b": 7, "c": 12}
    run_one = lambda row, timerange, timeout, **kwargs: (
        calls.append((row["strategy_id"], timerange)) or
        {"status": "measured", "timerange": timerange,
         "trades": counts[timerange]})
    try:
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "smoke.json")
            args = _argparse.Namespace(output=output,
                                       timeranges=["a", "b", "c"],
                                       trade_floor=10, force=False, timeout=1)
            row = {"strategy_id": "S", "_sha": "sha_v1"}
            _run(args, [row], None)
            assert calls == [("S", "a"), ("S", "b"), ("S", "c")]
            stored = read_results(output)["results"]["S"]
            assert stored["trades"] == 12
            assert stored["attempted_timeranges"] == ["a", "b", "c"]
            _run(args, [row], None)
            assert len(calls) == 3, "completed cascade must skip"
            row = {"strategy_id": "S", "_sha": "sha_v2"}
            _run(args, [row], None)
            assert len(calls) == 6, \
                "changed identity must re-measure, not stamp and skip"
            legacy = dict(stored, canonical_sha256="sha_v3", trades=1)
            legacy.pop("smoke_policy_id")
            legacy.pop("attempted_timeranges")
            data = read_results(output)
            data["results"]["S"] = legacy
            write_results(data, output)
            row = {"strategy_id": "S", "_sha": "sha_v3"}
            _run(args, [row], None)
            assert len(calls) == 9, "legacy low-trade smoke must cascade"

            # A row that already tried MORE rungs than a since-shortened
            # policy now asks for, and stayed under the floor at all of
            # them, is current - not stale merely because the stored rung
            # list is longer than the new one. This is the 2026-09-15 fix:
            # dropping a third rung must not force every row that already
            # tried it, and still measured low, to be re-run for nothing.
            counts["c"] = 3  # even the long-since-dropped rung stayed low
            three_rung_record = dict(stored, canonical_sha256="sha_v4",
                                     trades=3,
                                     attempted_timeranges=["a", "b", "c"])
            data = read_results(output)
            data["results"]["S"] = three_rung_record
            write_results(data, output)
            short_args = _argparse.Namespace(output=output,
                                             timeranges=["a", "b"],
                                             trade_floor=10, force=False,
                                             timeout=1)
            row = {"strategy_id": "S", "_sha": "sha_v4"}
            _run(short_args, [row], None)
            assert len(calls) == 9, \
                "a row already covering the shorter policy's rungs must skip"

            # The genuinely uncovered case still cascades: only rung "a" was
            # ever tried, so the shorter two-rung policy still owes rung "b".
            one_rung_record = dict(stored, canonical_sha256="sha_v5",
                                   trades=1, attempted_timeranges=["a"])
            data = read_results(output)
            data["results"]["S"] = one_rung_record
            write_results(data, output)
            row = {"strategy_id": "S", "_sha": "sha_v5"}
            _run(short_args, [row], None)
            assert len(calls) == 11, \
                "a row covering only a prefix of the policy must still cascade"

            # A runtime shim (repair/compat_signature.py, wired in via
            # PROFILE_CLASS1.json's rules/python_paths/etc.) changes strategy
            # BEHAVIOUR without touching canonical_sha256 or runtime_config_
            # sha256 at all, and a `failed` status short-circuits to "current"
            # in _result_is_current regardless of identity content. Without
            # folding the repair config into identity, a row recorded
            # `failed` before its fix rule existed would read as current
            # forever after the rule was added - found 2026-09-16 auditing
            # this exact mechanism (the min_roi_reached_entry cleanup).
            _class1 = lambda name: {}
            run_one = lambda row, timerange, timeout, **kwargs: (
                calls.append((row["strategy_id"], timerange)) or
                {"status": "failed", "timerange": timerange, "why": "boom"})
            row = {"strategy_id": "T", "_sha": "sha_fixed"}
            _run(args, [row], None)
            before = len(calls)
            _run(args, [row], None)
            assert len(calls) == before, "an unrepaired failure must stay skipped"
            _class1 = lambda name: {"rules": ["some_new_fix"]}
            _run(args, [row], None)
            assert len(calls) == before + 1, \
                "a repair rule added after a failed record must force a rerun"
            _run(args, [row], None)
            assert len(calls) == before + 1, \
                "the same repair rule must not force a rerun a second time"
            _class1 = lambda name: {"rules": ["some_new_fix"],
                                    "python_paths": ["repos/x/utils"]}
            _run(args, [row], None)
            assert len(calls) == before + 2, \
                ("a python_paths change with the SAME rules list must also "
                 "force a rerun - rules alone is not the whole repair config")
    finally:
        _identity, run_one, _class1 = saved_identity, saved_run_one, saved_class1
    print("profile_smoke selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=MANIFEST)
    parser.add_argument("--output", default=OUTPUT)
    parser.add_argument("--strategy", action="append", default=[])
    parser.add_argument("--profiles", nargs="+", default=[
        "futures_long", "futures_short", "futures_long_short"])
    parser.add_argument("--timerange", default="",
                        help="single-window compatibility override; disables cascade")
    parser.add_argument("--timeranges", nargs="+", default=list(SMOKE_TIMERANGES),
                        help="fixed smoke cascade, shortest to longest")
    parser.add_argument("--trade-floor", type=int, default=SMOKE_TRADE_FLOOR)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0

    if args.timerange:
        args.timeranges = [args.timerange]
    if not args.timeranges or args.trade_floor < 1:
        raise SystemExit("at least one timerange and a positive trade floor are required")
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
    policy_id = _policy_id(args.timeranges, args.trade_floor)
    data["timerange"] = args.timeranges[0]
    data["timeranges"] = list(args.timeranges)
    data["trade_floor"] = args.trade_floor
    data["smoke_policy_id"] = policy_id
    data["config"] = os.path.basename(FUTURES_CONFIG)
    # A repair-store override (a recovered timeframe, most often) has to
    # reach this run the same way it already reaches regime/full_backtest.py
    # and eligibility_timeframe_repair.py's own specialised runner - without
    # it, this plain CLI re-fails a row a repair store already answered.
    # `BBRSIS` measured 110 trades under `eligibility_timeframe_repair.py`
    # (its own `ticker_interval = '5m'`, recovered as a config override) and
    # then failed here, on the identical row, for want of the same value
    # this call never asked for.
    overrides = repair_overrides()
    print("profile smoke candidates: %d" % len(rows), flush=True)
    for index, row in enumerate(rows, 1):
        name = row["strategy_id"]
        previous = data["results"].get(name)
        settings = overrides.get(name) or None
        try:
            identity = _identity(row)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            identity = {"identity_error": "%s: %s" % (type(exc).__name__, exc)}
        # Folded in only when an override actually exists for this row: a
        # row with none keeps exactly today's comparison, so this cannot
        # read the rest of the corpus as changed just because the field now
        # exists. A row that DOES have one and never carried it before -
        # every row measured before this fix - is, correctly, read as
        # changed exactly once.
        if settings:
            identity = dict(identity)
            identity["config_overrides"] = settings
        # Same reasoning, for a different way a row's evidence can go stale:
        # a runtime shim (repair/compat_signature.py) changes what happens
        # when the CANONICAL FILE runs, without touching the file's own
        # bytes or the shared base config - `canonical_sha256`/`runtime_
        # config_sha256` cannot see it. Found 2026-09-16 auditing this exact
        # mechanism: a strategy recorded `failed` before a fix rule was
        # added to its PROFILE_CLASS1.json entry stayed `failed` forever
        # after, because `_result_is_current` returns True for any non-
        # `measured` status once identity matches, and identity never
        # changed. `python_paths`/`tf_use_legacy_keras`/`freqaimodel` are
        # included alongside `rules` for the same reason `config_overrides`
        # is handled separately from the file hashes above - repointing an
        # import path (the NNTC_* wrong-sibling-copy fix, Phase 14) changes
        # nothing `rules` alone would catch. Folded in only when non-empty,
        # so the overwhelming majority of rows with no repair config at all
        # see no change in behaviour here.
        repair_signature = {key: value for key, value in _class1(name).items()
                            if key in ("rules", "python_paths", "tf_use_legacy_keras",
                                       "freqaimodel", "freqaimodel_path",
                                       "config_source", "config_keys",
                                       "freqtrade_paths", "data_files") and value}
        if repair_signature:
            identity = dict(identity)
            identity["class1_repair_signature"] = repair_signature
        # A stored record is only current if it was measured under this
        # exact file and config - not merely "some record exists". Checking
        # only presence let three rows updated by an upstream `git pull`
        # (NostalgiaForInfinityX7, RLAgentStrategy, MomentumRegimeBasket15m)
        # get their `canonical_sha256` silently stamped onto the OLD result
        # here, which reads as "measured, identity current" while nothing
        # of the new file was ever run - `regime/full_backtest.py` already
        # gets this right the same way, one identity comparison before
        # deciding to skip.
        if (not args.force and _result_is_current(
                previous, identity, args.timeranges, args.trade_floor)):
            write_results(data, args.output)
            print("[%d/%d] %-38s skip" % (index, len(rows), name), flush=True)
            continue
        result = run_cascade(row, args.timeranges, args.trade_floor,
                             args.timeout, config_overrides=settings,
                             policy_id=policy_id)
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
