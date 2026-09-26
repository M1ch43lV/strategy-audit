"""Serially dispatch the next eligible canonical strategy-audit gate.

This is orchestration only.  It reads the published pipeline state, invokes
existing runners without changing their arguments or evidence semantics, and
lets each runner remain the owner of its own evidence store.  By default it
plans only; ``--apply`` is required to start one run and ``--watch --apply``
repeats that safe one-run cycle.

Once no per-strategy work is left it also runs Stages 9-13 for Model 0
(`tools/regime_evaluation.py`: attribution, specialist evaluation, the two published
pages), when the fingerprint of their inputs changed.

Gated Model 1/2/3 backtests, their attribution and their comparison are intentionally
outside this dispatcher and are owner-paused until an explicit later decision
re-enables them.
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

REGIME_GATE = "regime_evaluation"
RUNNERS = {
    "smoke": "runtime/profile_smoke_docker.ps1",
    "lookahead": "runtime/profile_bias_docker.ps1",
    "warmup": "runtime/warmup_convergence_docker.ps1",
    "recursive": "runtime/profile_bias_docker.ps1",
    "full_backtest": "runtime/regime_full_backtest_docker.ps1",
    "execution_detail": "runtime/regime_full_backtest_docker.ps1",
}
DISABLED_GATED_GATES = frozenset(("model1", "model2", "model3"))
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


def _is_true(value: object) -> bool:
    """Accept the JSON boolean and the published CSV-style representation."""
    return value is True or value == "true"


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


def _regime_stale() -> bool:
    from tools import regime_evaluation
    return regime_evaluation.is_stale()[0]


def owed_recovery() -> list[str]:
    from repair import timeframe_5m_recovery
    return timeframe_5m_recovery.owed()


def _window_stale() -> tuple[dict, dict]:
    """Strategies whose accepted canonical run used another window than today's per-mode rule.

    Returns (base runs to repeat, detail runs to repeat). The window of both modes is `20200401-20260821` since
    2026-09-21; a canonical futures run made before that started on 2020-03-01. Only canonical pooled runs are
    repeated here. The owner-approved 5m recoveries have their own route and are trimmed to the window in the
    attribution instead. A detail run is repeated once its base run has the current window, because the classifier
    refuses to compare runs over different windows.
    """
    from evidence import execution_robustness as er, profile_full_window
    manifest = _json(ROOT / "results" / "regime" / "full_backtest_manifest.json")["results"]
    base: dict[str, str] = {}
    for sid, row in manifest.items():
        if row.get("status") == "measured" and row.get("measurement_scope") == "canonical_pooled_native_pair_universe":
            want = profile_full_window.timerange(row.get("mode"))
            if row.get("timerange") != want:
                base[sid] = want
    detail: dict[str, str] = {}
    for sid, record in er.choose_detail_records().items():
        row = manifest.get(sid) or {}
        if (record.get("status") == "measured" and sid not in base and row.get("status") == "measured"
                and row.get("measurement_scope") == "canonical_pooled_native_pair_universe"
                and record.get("timerange") != row.get("timerange")):
            detail[sid] = row.get("timerange", "")
    return base, detail


def choose(state: dict, strategy: str = "", regime_stale=_regime_stale, window_stale=_window_stale,
           recovery_owed=owed_recovery) -> dict:
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

    # Pooled full backtests run as a batch (owner, 2026-09-21): four containers of 3.5 GB side by side, then the
    # strategies that died or timed out again alone with 15.5 GB (`runtime/full_batch_parallel.py`). The batch takes
    # every strategy owed one: a first run, and a canonical run over the old futures window (Decision 2026-09-21).
    stale_base, stale_detail = window_stale()
    owed_full = sorted(item["strategy_id"] for item in rows
                       if item.get("cohort") == "E1_expanded"
                       and (item.get("full_backtest_status") in (None, "") or item["strategy_id"] in stale_base))
    if owed_full:
        return {"kind": "run", "gate": "parallel_full", "metadata_gate": "full_backtest",
                "strategy": "batch-full", "names": owed_full, "args": []}

    # The 5m detail runs, the same way: those still pending and those over the old window.
    pending_detail = sorted(item["strategy_id"] for item in rows
                            if _is_true(item.get("technical_chain_complete"))
                            and item.get("execution_robustness_status") == "PENDING"
                            and _detail_timeframe(item.get("timeframe") or "") == "5m")
    stale_detail_rows = sorted(item["strategy_id"] for item in rows
                               if item["strategy_id"] in stale_detail and item.get("cohort") == "E1_expanded")
    owed_detail = sorted(set(pending_detail) | set(stale_detail_rows))
    if owed_detail:
        return {"kind": "run", "gate": "parallel_detail", "metadata_gate": "execution_robustness",
                "strategy": "batch-detail", "names": owed_detail, "args": []}

    row = _first(rows, lambda item: (
        _is_true(item.get("technical_chain_complete"))
        and item.get("execution_robustness_status") == "PENDING"))
    if row:
        detail_timeframe = _detail_timeframe(row.get("timeframe") or "")
        if detail_timeframe is None:
            return {"kind": "run", "gate": "execution_robustness",
                    "strategy": row["strategy_id"], "args": []}
        return {"kind": "escalate", "strategy": row["strategy_id"],
                "reason": "execution robustness requires a resolvable authored timeframe"}

    # A strategy whose 1m pooled run is a known out-of-memory case goes straight to the 5m recovery route (its four gates
    # and the 5m full backtest, `repair.timeframe_5m_recovery`), one at a time because that run needs 5-6 GB. Promotion into
    # E1 is a separate owner decision and is not made here. Never for a single requested strategy that is not owed it.
    row = next((sid for sid in recovery_owed() if not strategy or sid == strategy), None)
    if row:
        return {"kind": "run", "gate": "recovery_5m", "metadata_gate": "resource_diagnostic",
                "strategy": row, "args": []}

    # Pipeline-level work, after every strategy-level route is exhausted, never for a single requested strategy:
    # Stages 9-13 for Model 0 when an input (an accepted archive, the E1 cohort, the regime labels, the robustness
    # stores or the program source) changed since the last complete run.
    if not strategy and regime_stale():
        return {"kind": "run", "gate": REGIME_GATE, "metadata_gate": "regime_evaluation",
                "strategy": "regime-evaluation-model0", "args": []}

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
    if action["gate"] in DISABLED_GATED_GATES:
        raise DispatchError("Model 1/2/3 gated backtests are owner-paused")
    if action["gate"] == REGIME_GATE:
        return [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                str(ROOT / "runtime" / "regime_evaluation_docker.ps1")]
    if action["gate"] == "parallel_full":
        return [sys.executable, str(ROOT / "runtime" / "full_batch_parallel.py"),
                *[a for name in action["names"] for a in ("--strategy", name)]]
    if action["gate"] == "parallel_detail":
        return [sys.executable, str(ROOT / "runtime" / "detail_batch_parallel.py"),
                *[a for name in action["names"] for a in ("--strategy", name)]]
    if action["gate"] == "recovery_5m":
        return [sys.executable, "-m", "repair.timeframe_5m_recovery", "--apply", "--strategy", action["strategy"]]
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
    if action["gate"] == REGIME_GATE:
        return  # the run wrote its own state and pages; no strategy row changes
    if action["gate"] == "recovery_5m":
        _refresh_state()
        return
    if action["gate"] in ("execution_detail", "parallel_detail"):
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
    if action["gate"] in (REGIME_GATE, "parallel_full", "parallel_detail", "recovery_5m"):
        return "PASS"
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


def run_once(apply: bool, strategy: str = "") -> str:
    """Plan (and, with ``apply``, run) exactly one step. Returns "idle" when ``choose()`` found no
    eligible work at all (used by ``--watch`` to stop instead of polling forever), "blocked" for a
    transient condition expected to clear on its own, and "ran"/"planned" otherwise."""
    active = _docker_running()
    if active:
        print(json.dumps({"kind": "blocked", "reason": "active Docker container", "containers": active}, indent=2))
        return "blocked"
    current, detail = _state_is_current()
    if not current:
        print(json.dumps({"kind": "blocked", "reason": "published pipeline state is stale",
                          "detail": detail}, ensure_ascii=False, indent=2))
        return "blocked"
    action = choose(_load_state(), strategy)
    if not apply or action["kind"] != "run":
        print(json.dumps(action, ensure_ascii=False, indent=2), flush=True)
        return "idle" if action["kind"] == "idle" else "planned"
    command = _command(action)
    print(json.dumps({"dispatch": action, "command": command}, ensure_ascii=False, indent=2), flush=True)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode == 0:
        _finalize_success(action)
    status = _result_status(action, completed.returncode)
    _append_metadata(action, command, status, completed.stdout + completed.stderr)
    if completed.returncode:
        raise DispatchError("runner failed with exit %d" % completed.returncode)
    return "ran"


def selftest() -> None:
    no_window = lambda: ({}, {})

    def pick(state, strategy="", **kw):
        kw.setdefault("window_stale", no_window)
        kw.setdefault("recovery_owed", lambda: [])
        return choose(state, strategy, **kw)

    base = {"strategies": {
        "A": {"strategy_id": "A", "open_work": "first_measurement_in_current_runtime", "run_profile": "spot_long"},
        "B": {"strategy_id": "B", "open_work": "lookahead_verdict", "run_profile": "spot_long", "measured": "true"},
    }}
    assert pick(base)["gate"] == "smoke"
    base["strategies"]["A"]["open_work"] = "first_measurement_in_current_runtime;recursive_ladder_pending"
    assert pick(base)["gate"] == "smoke"
    base["strategies"]["A"]["open_work"] = "runtime_repair_pending"
    assert pick(base)["gate"] == "lookahead"
    base["strategies"]["B"]["open_work"] = "recursive_ladder_pending;to_be_fixed"
    base["strategies"]["B"]["lookahead"] = "PASS"
    assert pick(base, regime_stale=lambda: False)["kind"] == "escalate"
    post = {"strategies": {"C": {
        "strategy_id": "C", "technical_chain_complete": True,
        "execution_robustness_status": "PENDING", "timeframe": "1m",
    }}}
    assert pick(post)["gate"] == "execution_robustness"
    post["strategies"]["C"]["timeframe"] = "1h"
    assert pick(post)["gate"] == "parallel_detail" and pick(post)["names"] == ["C"]
    post["strategies"]["C"]["technical_chain_complete"] = "true"
    assert pick(post)["gate"] == "parallel_detail"
    idle = {"strategies": {"D": {"strategy_id": "D", "open_work": ""}}}
    assert pick(idle, regime_stale=lambda: True)["gate"] == REGIME_GATE
    assert pick(idle, regime_stale=lambda: False)["kind"] == "idle"
    assert pick(idle, "D", regime_stale=lambda: True)["kind"] == "idle"   # never for one requested strategy
    fresh = {"strategies": {"E": {"strategy_id": "E", "open_work": "first_measurement_in_current_runtime",
                                  "run_profile": "spot_long"}}}
    assert pick(fresh, regime_stale=lambda: True)["gate"] == "smoke"    # strategy work comes first
    assert _command({"gate": REGIME_GATE})[-1].endswith("regime_evaluation_docker.ps1")
    late = {"strategies": {"F": {"strategy_id": "F", "open_work": "", "cohort": "E1_expanded", "full_backtest_status": "measured", "technical_chain_complete": True,
                                 "execution_robustness_status": "PASS", "timeframe": "1h"}}}
    hit = pick(late, window_stale=lambda: ({"F": "20200401-20260821"}, {}), regime_stale=lambda: False)
    assert hit["gate"] == "parallel_full" and hit["names"] == ["F"]             # old futures window: repeat the base run in the batch
    hit = pick(late, window_stale=lambda: ({}, {"F": "20200401-20260821"}), regime_stale=lambda: False)
    assert hit["gate"] == "parallel_detail" and hit["names"] == ["F"]           # then its detail run
    both = pick(late, window_stale=lambda: ({"F": "x"}, {"F": "x"}), regime_stale=lambda: False)
    assert both["gate"] == "parallel_full"                                      # base before detail
    first_run = {"strategies": {"G": {"strategy_id": "G", "open_work": "", "cohort": "E1_expanded"}}}
    hit = pick(first_run, regime_stale=lambda: False)
    assert hit["gate"] == "parallel_full" and hit["names"] == ["G"]             # a first run also goes through the batch
    cmd = _command(hit)
    assert cmd[1].endswith("full_batch_parallel.py") and cmd[-2:] == ["--strategy", "G"]
    idle_state = {"strategies": {"H": {"strategy_id": "H", "open_work": ""}}}
    hit = pick(idle_state, recovery_owed=lambda: ["H"], regime_stale=lambda: False)
    assert hit["gate"] == "recovery_5m" and hit["strategy"] == "H"              # a known 1m OOM goes straight to 5m
    assert _command(hit)[-3:] == ["--apply", "--strategy", "H"]
    assert pick(idle_state, "H", recovery_owed=lambda: ["Q"], regime_stale=lambda: False)["kind"] == "idle"   # another strategy's recovery is not ours
    try:
        _command({"gate": "model1"})
    except DispatchError:
        pass
    else:
        raise AssertionError("owner-paused gated route must be refused")
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
            outcome = run_once(args.apply, args.strategy or "")
            if not args.watch:
                return 0
            if outcome == "idle":
                print(json.dumps({"kind": "stopping", "reason": "no eligible pending work"}, indent=2), flush=True)
                return 0
            time.sleep(args.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DispatchError as exc:
        print("pipeline dispatcher: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
