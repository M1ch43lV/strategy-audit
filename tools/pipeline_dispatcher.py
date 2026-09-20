"""Serially dispatch the next eligible canonical strategy-audit gate.

This is orchestration only.  It reads the published pipeline state, invokes
existing runners without changing their arguments or evidence semantics, and
lets each runner remain the owner of its own evidence store.  By default it
plans only; ``--apply`` is required to start one run and ``--watch --apply``
repeats that safe one-run cycle.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tomllib
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Direct script execution places only ``tools/`` on sys.path.  Keep the
    # repository root importable so post-run metadata finalization can load
    # the sibling ``tools.run_metadata`` module after a successful benchmark.
    sys.path.insert(0, str(ROOT))
STATE = ROOT / "evidence" / "PIPELINE_STATE.json"
WARMUP = ROOT / "evidence" / "WARMUP_CONVERGENCE.json"
BIAS = ROOT / "evidence" / "PROFILE_BIAS.json"
LOCK = ROOT / "user_data" / ".pipeline_dispatcher.running"
METADATA = ROOT / "evidence" / "RUN_METADATA.jsonl"
CONFIG = ROOT / ".codex" / "config.toml"
AUDIT_IMAGE_PREFIX = "strategy-audit-runtime:"
STALE_LOCK_SECONDS = 300
PS = "powershell.exe" if os.name == "nt" else "powershell"

RUNNERS = {
    "smoke": "runtime/profile_smoke_docker.ps1",
    "lookahead": "runtime/profile_bias_docker.ps1",
    "warmup": "runtime/warmup_convergence_docker.ps1",
    "recursive": "runtime/profile_bias_docker.ps1",
    "full_backtest": "runtime/regime_full_backtest_docker.ps1",
    "execution_detail": "runtime/regime_full_backtest_docker.ps1",
}
KNOWN_SMOKE_PROFILES = {
    "spot_long", "spot_short", "spot_long_short",
    "futures_long", "futures_short", "futures_long_short",
}
REPAIR_BLOCKERS = {
    "runtime_repair_pending", "to_be_fixed", "needs_a_look",
    "repair_attempted", "repair_withdrawn",
}


class DispatchError(RuntimeError):
    """A safe controller refusal, not a strategy verdict."""


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _route(gate: str) -> tuple[str, str]:
    """Read the configured route rather than duplicating routing policy."""
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    route = (config.get("routing") or {}).get(gate) or {}
    model, reasoning = route.get("model"), route.get("reasoning")
    if not model or not reasoning:
        raise DispatchError("missing configured route for " + gate)
    return model, reasoning


def _work(row: dict) -> set[str]:
    return set(filter(None, (row.get("open_work") or "").split(";")))


def _docker_running() -> list[str]:
    """Return active audit containers that would contend for benchmark state.

    The host also runs unrelated Gainium services (Mongo, Redis and RabbitMQ).
    They do not write this repository's evidence and must not block dispatch.
    Only the pinned strategy-audit runtime image participates in this lock.
    """
    completed = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}|{{.Image}}"], cwd=ROOT,
        text=True, capture_output=True, check=False)
    if completed.returncode:
        raise DispatchError("could not inspect Docker before dispatch: "
                            + completed.stderr.strip())
    return [line for line in completed.stdout.splitlines()
            if line.strip() and line.split("|", 1)[1].startswith(AUDIT_IMAGE_PREFIX)]


def recover_stale_lock() -> bool:
    """Remove only an old, empty legacy lock after the Docker contention check.

    This deliberately is not automatic.  A caller must opt in after confirming
    that no host-side runner is active; a current dispatcher always owns a
    non-stale lock for less than this short recovery interval.
    """
    if not LOCK.exists():
        return False
    if _docker_running():
        raise DispatchError("cannot recover dispatcher lock while an audit Docker container runs")
    if any(LOCK.iterdir()):
        raise DispatchError("refusing to recover a non-empty dispatcher lock")
    age = time.time() - LOCK.stat().st_mtime
    if age < STALE_LOCK_SECONDS:
        raise DispatchError("refusing to recover a recent dispatcher lock")
    LOCK.rmdir()
    return True


def _load_state() -> dict:
    if not STATE.exists():
        raise DispatchError("published pipeline state is missing")
    return _json(STATE)


def _state_is_current() -> tuple[bool, str]:
    """Do not dispatch from a publication snapshot that trails its writers."""
    completed = subprocess.run(
        [sys.executable, "-m", "evidence.strategy_status", "--check"], cwd=ROOT,
        text=True, capture_output=True, check=False)
    return completed.returncode == 0, (completed.stdout + completed.stderr).strip()


def _converged() -> set[str]:
    if not WARMUP.exists():
        return set()
    return {name for name, record in _json(WARMUP).get("results", {}).items()
            if record.get("state") == "converged"}


def _has_lookahead_attempt(strategy: str) -> bool:
    """Tell a true retry from a newly-intaken row's placeholder label."""
    if not BIAS.exists():
        return False
    record = _json(BIAS).get("results", {}).get(strategy, {})
    return bool(record.get("lookahead"))


def _first(rows: Iterable[dict], predicate) -> dict | None:
    return next((row for row in sorted(rows, key=lambda item: item["strategy_id"])
                 if predicate(row)), None)


def choose(state: dict, strategy: str = "") -> dict:
    """Choose exactly one safe next action from the canonical read model.

    Repair triage and the zero-trade full-window probe are intentionally not
    guessed here.  They require their dedicated, preregistered routes and are
    represented as an escalation instead of a fabricated normal gate.
    """
    rows = list(state["strategies"].values())
    if strategy:
        rows = [row for row in rows if row["strategy_id"] == strategy]
        if not rows:
            raise DispatchError("requested strategy is absent from published state: " + strategy)
    converged = _converged()
    warm_records = _json(WARMUP).get("results", {}) if WARMUP.exists() else {}

    row = _first(rows, lambda item: (
        "first_measurement_in_current_runtime" in _work(item)
        and not (_work(item) & REPAIR_BLOCKERS)
        and item.get("run_profile") in KNOWN_SMOKE_PROFILES))
    if row:
        return {"kind": "run", "gate": "smoke", "strategy": row["strategy_id"],
                "args": ["--strategy", row["strategy_id"], "--profiles",
                         row["run_profile"], "--limit", "1", "--timeout", "300"]}

    row = _first(rows, lambda item: (
        item.get("measured") == "true"
        # `lookahead_remeasure_pending` normally means an attempt already
        # exists but produced NA/timeout/error evidence.  Fresh intake rows
        # can receive that generic publication label before any bias card
        # exists; those are genuine first diagnostics and must enter Stage 2.
        # Existing attempts remain an escalation boundary.
        and not (_work(item) & REPAIR_BLOCKERS)
        and ("lookahead_verdict" in _work(item)
             or ("lookahead_remeasure_pending" in _work(item)
                 and not _has_lookahead_attempt(item["strategy_id"])))))
    if row:
        return {"kind": "run", "gate": "lookahead", "strategy": row["strategy_id"],
                "args": ["--only", row["strategy_id"], "--diagnostics", "lookahead",
                         "--limit", "1", "--timeout", "1200", "--fallback-timeout", "300"]}

    row = _first(rows, lambda item: (
        "recursive_ladder_pending" in _work(item)
        and item.get("lookahead") == "PASS"
        and not (_work(item) & REPAIR_BLOCKERS)
        # A convergence record (including inconclusive/no-usable-ladder) is
        # already a completed attempt. It needs a repair or explicit rerun
        # decision, not an automatic duplicate ladder.
        and item["strategy_id"] not in warm_records))
    if row:
        return {"kind": "run", "gate": "warmup", "metadata_gate": "warmup_recursive",
                "strategy": row["strategy_id"],
                "args": ["--cohort", "lookahead_pass", "--strategy", row["strategy_id"],
                         "--limit", "1", "--timeout", "1800"]}

    row = _first(rows, lambda item: (
        item["strategy_id"] in converged and item.get("lookahead") == "PASS"
        and item.get("recursive") not in ("PASS", "PASS_1PCT")
        and not (_work(item) & REPAIR_BLOCKERS)
        and "recursive_ladder_pending" in _work(item)))
    if row:
        return {"kind": "run", "gate": "recursive", "metadata_gate": "warmup_recursive",
                "strategy": row["strategy_id"],
                "args": ["--only", row["strategy_id"], "--diagnostics", "recursive",
                         "--limit", "1", "--timeout", "1200", "--fallback-timeout", "300"]}

    row = _first(rows, lambda item: (
        item.get("lookahead") == "PASS"
        and item.get("recursive") in ("PASS", "PASS_1PCT")
        and item.get("coverage_status") == "PENDING"
        and not (_work(item) & REPAIR_BLOCKERS)))
    if row:
        return {"kind": "run", "gate": "coverage", "metadata_gate": "warmup_recursive",
                "strategy": row["strategy_id"], "args": []}

    row = _first(rows, lambda item: (
        item.get("cohort") == "E1_expanded"
        and item.get("full_backtest_status") in (None, "")))
    if row:
        return {"kind": "run", "gate": "full_backtest", "strategy": row["strategy_id"],
                "args": ["--strategy", row["strategy_id"], "--workers", "1", "--timeout", "3600"]}

    row = _first(rows, lambda item: (
        item.get("technical_chain_complete") is True
        and item.get("execution_robustness_status") == "PENDING"))
    if row:
        detail_timeframe = _detail_timeframe(row.get("timeframe") or "")
        if detail_timeframe == "5m":
            return {"kind": "run", "gate": "execution_detail",
                    "metadata_gate": "execution_robustness", "strategy": row["strategy_id"],
                    "args": ["--strategy", row["strategy_id"], "--workers", "1", "--timeout", "3600",
                             "--timeframe-detail", "5m", "--output",
                             "results/regime/execution_robustness_detail_5m_docker.json"]}
        if detail_timeframe is None:
            return {"kind": "run", "gate": "execution_robustness",
                    "strategy": row["strategy_id"], "args": []}
        return {"kind": "escalate", "strategy": row["strategy_id"],
                "reason": "execution robustness requires a resolvable authored timeframe"}

    manual = _first(rows, lambda item: bool(_work(item)))
    if manual:
        return {"kind": "escalate", "strategy": manual["strategy_id"],
                "reason": "no automatically safe route for open_work="
                          + ";".join(sorted(_work(manual)))}
    return {"kind": "idle", "reason": "no eligible pending work"}


def _detail_timeframe(timeframe: str) -> str | None:
    """Return the frozen Stage-8b route without changing the authored TF."""
    minutes = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
               "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480,
               "12h": 720, "1d": 1440, "1w": 10080}.get(timeframe)
    if minutes is None:
        return "unknown"
    return "5m" if minutes > 5 else None


def _command(action: dict) -> list[str]:
    if action["gate"] == "coverage":
        return [sys.executable, "-m", "evidence.regime_coverage"]
    if action["gate"] == "execution_robustness":
        return [sys.executable, "-m", "evidence.execution_robustness"]
    return [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
            str(ROOT / RUNNERS[action["gate"]]), *action["args"]]


def _refresh_state() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "evidence.strategy_status"], cwd=ROOT,
        text=True, capture_output=True, check=False)
    if completed.returncode:
        raise DispatchError("canonical publication refresh failed: "
                            + completed.stderr.strip())


def _admit_then_refresh() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "evidence.eligibility_admit_converged", "--apply"],
        cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise DispatchError("eligibility admission failed: " + completed.stderr.strip())
    _refresh_state()


def _finalize_success(action: dict) -> None:
    """Publish exactly the derived evidence the completed route requires."""
    if action["gate"] == "execution_detail":
        completed = subprocess.run(
            [sys.executable, "-m", "evidence.execution_robustness"], cwd=ROOT,
            text=True, capture_output=True, check=False)
        if completed.returncode:
            raise DispatchError("execution-robustness publication failed: "
                                + completed.stderr.strip())
        _refresh_state()
        return
    if action["gate"] == "execution_robustness":
        _refresh_state()
        return
    # The raw runner owns its evidence store. Rebuild the published reader
    # before admission so a just-written coverage or convergence record is
    # visible to the admission rule in this same dispatcher cycle.
    _refresh_state()
    _admit_then_refresh()


def _result_status(action: dict, returncode: int) -> str:
    """Map process completion to operational metadata, never a strategy verdict."""
    if returncode:
        return "ERROR"
    state = _load_state().get("strategies", {}).get(action["strategy"], {})
    if action["gate"] == "full_backtest":
        return "PASS" if state.get("full_backtest_status") == "measured" else "FAIL"
    if action["gate"] == "lookahead":
        return "PASS" if state.get("lookahead") == "PASS" else "FAIL"
    if action["gate"] == "recursive":
        return "PASS" if state.get("recursive") in ("PASS", "PASS_1PCT") else "FAIL"
    if action["gate"] == "warmup":
        return "PASS" if action["strategy"] in _converged() else "FAIL"
    if action["gate"] == "coverage":
        return "PASS" if state.get("coverage_status") == "PASS" else "FAIL"
    if action["gate"] in ("execution_detail", "execution_robustness"):
        return "PASS" if state.get("execution_robustness_status") == "PASS" else "FAIL"
    return "PASS" if state.get("measured") in (True, "true") else "FAIL"


def _append_metadata(action: dict, command: list[str], status: str, output: str) -> None:
    gate = action.get("metadata_gate", action["gate"])
    model, reasoning = _route(gate)
    previous_run_id = ""
    if METADATA.exists():
        for line in reversed(METADATA.read_text(encoding="utf-8").splitlines()):
            prior = json.loads(line)
            if (prior.get("gate") == gate and
                    prior.get("strategy_ref") == action["strategy"]):
                previous_run_id = prior.get("run_id", "")
                break
    record = {
        "run_id": "dispatcher-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "gate": gate, "model": model, "reasoning": reasoning, "status": status,
        "strategy_ref": action["strategy"], "task": "pipeline dispatcher",
        "command": command, "evidence": ["evidence/PIPELINE_STATE.json"],
        "tool_versions": {"dispatcher": "1", "python": sys.version.split()[0]},
        "escalation_reason": "", "previous_run_id": previous_run_id,
    }
    from tools.run_metadata import append_record
    append_record(METADATA, record)
    if output:
        print(output, end="" if output.endswith("\n") else "\n")


@contextlib.contextmanager
def dispatcher_lock():
    try:
        LOCK.mkdir()
    except FileExistsError as exc:
        raise DispatchError("another dispatcher holds " + str(LOCK)) from exc
    try:
        yield
    finally:
        try:
            LOCK.rmdir()
        except OSError:
            pass


def run_once(apply: bool, strategy: str = "") -> int:
    active = _docker_running()
    if active:
        print(json.dumps({"kind": "blocked", "reason": "active Docker container", "containers": active}, indent=2))
        return 0
    current, detail = _state_is_current()
    if not current:
        print(json.dumps({"kind": "blocked", "reason": "published pipeline state is stale",
                          "detail": detail}, ensure_ascii=False, indent=2))
        return 0
    action = choose(_load_state(), strategy)
    if not apply or action["kind"] != "run":
        print(json.dumps(action, ensure_ascii=False, indent=2))
        return 0
    command = _command(action)
    print(json.dumps({"dispatch": action, "command": command}, ensure_ascii=False, indent=2), flush=True)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode == 0:
        _finalize_success(action)
    status = _result_status(action, completed.returncode)
    _append_metadata(action, command, status, completed.stdout + completed.stderr)
    if completed.returncode:
        raise DispatchError("runner failed with exit %d" % completed.returncode)
    return 0


def selftest() -> None:
    base = {"strategies": {
        "A": {"strategy_id": "A", "open_work": "first_measurement_in_current_runtime", "run_profile": "spot_long"},
        "B": {"strategy_id": "B", "open_work": "lookahead_verdict", "run_profile": "spot_long", "measured": "true"},
    }}
    assert choose(base)["gate"] == "smoke"
    base["strategies"]["A"]["open_work"] = "first_measurement_in_current_runtime;recursive_ladder_pending"
    assert choose(base)["gate"] == "smoke"
    base["strategies"]["A"]["open_work"] = "runtime_repair_pending"
    assert choose(base)["gate"] == "lookahead"
    base["strategies"]["B"]["open_work"] = "recursive_ladder_pending;to_be_fixed"
    base["strategies"]["B"]["lookahead"] = "PASS"
    assert choose(base)["kind"] == "escalate"
    post = {"strategies": {"C": {
        "strategy_id": "C", "technical_chain_complete": True,
        "execution_robustness_status": "PENDING", "timeframe": "1m",
    }}}
    assert choose(post)["gate"] == "execution_robustness"
    post["strategies"]["C"]["timeframe"] = "1h"
    assert choose(post)["gate"] == "execution_detail"
    print("pipeline_dispatcher selftest: PASS")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="start exactly one eligible runner")
    parser.add_argument("--watch", action="store_true", help="repeat after every completed run")
    parser.add_argument("--strategy", help="restrict planning and dispatch to one strategy ID")
    parser.add_argument("--intake", action="store_true",
                        help="refresh source-derived intake evidence before the named strategy")
    parser.add_argument("--recover-stale-lock", action="store_true",
                        help="remove only an old empty lock after checking audit Docker is idle")
    parser.add_argument("--interval", type=int, default=60, help="idle polling interval in seconds")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.interval < 1:
        raise SystemExit("--interval must be positive")
    if args.intake:
        if not args.strategy:
            raise SystemExit("--intake requires --strategy")
        if not args.apply:
            raise SystemExit("--intake writes source-derived evidence; pass --apply")
    if args.recover_stale_lock:
        recovered = recover_stale_lock()
        print(json.dumps({"stale_lock_recovered": recovered}, indent=2))
    with dispatcher_lock():
        if args.intake:
            command = [sys.executable, "-c",
                       "from tools.harvest import refresh_intake_evidence; raise SystemExit(refresh_intake_evidence())"]
            completed = subprocess.run(command, cwd=ROOT, text=True,
                                       capture_output=True, check=False)
            intake_action = {"gate": "classification", "strategy": args.strategy}
            _append_metadata(intake_action, command,
                             "PASS" if completed.returncode == 0 else "ERROR",
                             completed.stdout + completed.stderr)
            if completed.returncode:
                raise DispatchError("source intake refresh failed with exit %d" % completed.returncode)
        while True:
            run_once(args.apply, args.strategy or "")
            if not args.watch:
                return 0
            time.sleep(args.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DispatchError as exc:
        print("pipeline dispatcher: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
