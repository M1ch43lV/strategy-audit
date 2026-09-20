"""Run a non-canonical, pair-subset resource diagnostic for a full backtest.

This tool never writes the canonical pooled manifest or a generated status
view.  Its output can explain an OOM result, but cannot replace it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

from evidence import profile_smoke
from tools.run_metadata import append_record


ROOT = Path(__file__).resolve().parents[1]
FUTURES_CONFIG = ROOT / "runtime" / "profile_futures_config.json"
SPOT_CONFIG = ROOT / "runtime" / "profile_spot_config.json"
OUTPUT = ROOT / "evidence" / "FULL_BACKTEST_RESOURCE_DIAGNOSTIC.json"
METADATA = ROOT / "evidence" / "RUN_METADATA.jsonl"
IMAGE = "strategy-audit-runtime:2026.7"
TIMERANGE = "20200301-20260821"
POLL_SECONDS = 2.0


def _sha256(path: Path) -> str:
    return "sha256_" + hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _memory_mib(text: str) -> float | None:
    """Parse Docker's current-memory field without treating a limit as usage."""
    match = re.match(r"\s*([0-9.]+)\s*([KMG]iB|B)\s*/", text)
    if not match:
        return None
    value, unit = float(match.group(1)), match.group(2)
    return value * {"B": 1 / 1024 / 1024, "KiB": 1 / 1024, "MiB": 1, "GiB": 1024}[unit]


def _row(strategy: str) -> dict:
    rows = {row["strategy_id"]: row for row in profile_smoke.read_manifest(profile_smoke.MANIFEST)}
    if strategy not in rows:
        raise SystemExit("unknown strategy: " + strategy)
    row = rows[strategy]
    return row


def _config_for(row: dict) -> Path:
    """Select the frozen profile config without changing the strategy source."""
    return FUTURES_CONFIG if row["run_profile"].startswith("futures_") else SPOT_CONFIG


def _active_audit_container() -> bool:
    completed = subprocess.run(["docker", "ps", "--format", "{{.Image}}"], text=True,
                               capture_output=True, check=False)
    return any(line.startswith(IMAGE) for line in completed.stdout.splitlines())


def _container_stats(name: str, stop: threading.Event, samples: list[float]) -> None:
    while not stop.wait(POLL_SECONDS):
        completed = subprocess.run(
            ["docker", "stats", name, "--no-stream", "--format", "{{.MemUsage}}"],
            text=True, capture_output=True, check=False)
        amount = _memory_mib(completed.stdout)
        if amount is not None:
            samples.append(amount)


def run(strategy: str, pair_count: int, timeout: int, output: Path,
        timeframe: str = "") -> dict:
    if _active_audit_container():
        raise SystemExit("refusing resource diagnostic while an audit container is active")
    row = _row(strategy)
    base_config = _config_for(row)
    base = json.loads(base_config.read_text(encoding="utf-8"))
    pairs = base["exchange"]["pair_whitelist"][:pair_count]
    if len(pairs) != pair_count:
        raise SystemExit("pair count exceeds the canonical futures universe")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = f"-tf{timeframe}" if timeframe else ""
    identifier = f"{strategy}-{stamp}-pairs{pair_count}{suffix}"
    directory = ROOT / "user_data" / "resource_diagnostics" / identifier
    directory.mkdir(parents=True, exist_ok=False)
    config = dict(base)
    config["exchange"] = dict(base["exchange"], pair_whitelist=pairs)
    config_path = directory / "futures_subset_config.json"
    _write(config_path, config)
    canonical = Path(row["canonical_file"])
    container_name = "resource-diag-" + hashlib.sha256(identifier.encode()).hexdigest()[:12]
    config_in_container = "/audit/" + config_path.relative_to(ROOT).as_posix()
    output_in_container = "/audit/" + directory.relative_to(ROOT).as_posix()
    command = [
        "docker", "run", "--rm", "--name", container_name,
        "-v", f"{ROOT}:/audit", "-w", "/audit", "--entrypoint", "python", IMAGE,
        "evidence/profile_freqtrade.py", "backtesting", "--config", config_in_container,
        "--strategy", strategy, "--strategy-path", "/audit/" + str(canonical.parent).replace("\\", "/"),
        "--timerange", TIMERANGE, "--fee", "0.001", "--export", "trades",
        "--backtest-directory", output_in_container, "--cache", "none",
    ]
    if timeframe:
        command += ["--timeframe", timeframe]
    samples: list[float] = []
    stop = threading.Event()
    watcher = threading.Thread(target=_container_stats, args=(container_name, stop, samples), daemon=True)
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    watcher.start()
    try:
        stdout, _ = process.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run(["docker", "kill", container_name], text=True, capture_output=True, check=False)
        stdout, _ = process.communicate()
    finally:
        stop.set()
        watcher.join(timeout=POLL_SECONDS + 1)
    elapsed = round(time.monotonic() - started, 1)
    if timed_out:
        status, why = "timeout", f"diagnostic timeout after {timeout}s"
    elif process.returncode in (137, -9):
        status, why = "resource_inconclusive", "container ended with SIGKILL/OOM signature"
    elif process.returncode:
        status, why = "error", f"diagnostic process exit {process.returncode}"
    else:
        status, why = "measured", "completed non-canonical pair-subset diagnostic"
    result = {
        "attempted_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "strategy": strategy,
        "canonical_identity": profile_smoke._identity(row),
        "diagnostic_scope": ("noncanonical_timeframe_override_resource_probe"
                             if timeframe else "noncanonical_pair_subset_resource_probe"),
        "canonical_baseline_reference": "results/regime/full_backtest_manifest.json",
        "pairs": pairs,
        "pair_count": pair_count,
        "source_timeframe": row.get("execution_timeframe", ""),
        "requested_timeframe": timeframe or row.get("execution_timeframe", ""),
        "timerange": TIMERANGE,
        "runtime_image": IMAGE,
        "runtime_config": str(base_config.relative_to(ROOT)).replace("\\", "/"),
        "runtime_config_sha256": _sha256(base_config),
        "subset_config": str(config_path.relative_to(ROOT)).replace("\\", "/"),
        "subset_config_sha256": _sha256(config_path),
        "command": command,
        "elapsed_s": elapsed,
        "peak_memory_mib": round(max(samples), 1) if samples else None,
        "memory_samples": len(samples),
        "status": status,
        "why": why,
        "stdout_tail": stdout[-4000:],
    }
    data = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {"schema_version": 1, "results": {}}
    data.setdefault("results", {}).setdefault(strategy, []).append(result)
    _write(output, data)
    append_record(METADATA, {
        "run_id": "resource-diagnostic-" + stamp,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "gate": "resource_diagnostic", "model": "gpt-5.6-terra", "reasoning": "low",
        "status": "PASS" if status == "measured" else "ERROR", "strategy_ref": strategy,
        "task": "non-canonical full-backtest resource diagnostic", "command": command,
        "evidence": [str(output.relative_to(ROOT)).replace("\\", "/")],
        "tool_versions": {"diagnostic": "1", "python": sys.version.split()[0]},
        "escalation_reason": "noncanonical resource diagnosis; no pipeline status is changed",
        "previous_run_id": "dispatcher-20260920T192001Z",
    })
    print(json.dumps(result, indent=2))
    return result


def selftest() -> None:
    assert _memory_mib("1.5GiB / 15GiB") == 1536.0
    assert _memory_mib("512MiB / 15GiB") == 512.0
    assert _memory_mib("bad") is None
    print("full_backtest_resource_diagnostic selftest: PASS")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy")
    parser.add_argument("--pair-count", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--timeframe", default="",
                        help="non-canonical Freqtrade timeframe override, for example 5m")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if not args.strategy:
        raise SystemExit("--strategy is required unless --selftest is used")
    if args.pair_count < 1 or args.timeout < 1:
        raise SystemExit("pair count and timeout must be positive")
    run(args.strategy, args.pair_count, args.timeout, args.output, args.timeframe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
