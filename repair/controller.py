"""Coordinate the bounded Class 1 and Class 2 repair handlers.

The controller is deliberately a control plane, not a new repair mechanism.
Class 1 continues to restore runtime prerequisites without changing strategy
source.  Class 2 continues to create separately hashed, proven overlays.  The
handlers keep their own evidence stores; this program records only orchestration
provenance in ``evidence/REPAIR_CONTROLLER.jsonl``.

By default it prints a plan.  ``--apply`` is explicit, serial, and refuses to
run while Docker has an active benchmark container.  It never edits files
under ``repos/`` and it does not make repair triage an automatic pipeline gate.

Examples (from the repository root)::

    .\\ftenv\\Scripts\\python.exe -m repair.controller
    .\\ftenv\\Scripts\\python.exe -m repair.controller --class class2 --apply
    .\\ftenv\\Scripts\\python.exe -m repair.controller --selftest
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
LOG = EVIDENCE / "REPAIR_CONTROLLER.jsonl"
LOCK = ROOT / "user_data" / ".repair_controller.running"


class RepairControllerError(RuntimeError):
    """A safe refusal by the controller, never a strategy verdict."""


@dataclass(frozen=True)
class Handler:
    """One existing repair writer with its independent evidence ownership."""

    name: str
    repair_class: str
    description: str
    command: tuple[str, ...]
    evidence: tuple[str, ...]


def _child_python() -> str:
    """Prefer the pinned audit runtime without requiring it for plan mode."""
    configured = os.environ.get("PROFILE_PYTHON")
    if configured:
        return configured
    pinned = ROOT / "ftenv" / "Scripts" / "python.exe"
    return str(pinned) if pinned.exists() else sys.executable


def handlers(python: str | None = None) -> tuple[Handler, ...]:
    """Return the fixed, intentionally small set of automatic repair writers."""
    python = python or _child_python()
    return (
        Handler(
            name="class1_timeframe_retry",
            repair_class="class1",
            description="Retry only recorded, author-evidenced timeframe recoveries that previously timed out.",
            command=(python, "-m", "evidence.eligibility_timeframe_repair",
                     "--stage", "smoke", "--retry-timeouts"),
            evidence=("evidence/ELIGIBILITY_TIMEFRAME_REPAIR.json", "evidence/PROFILE_SMOKE.json"),
        ),
        Handler(
            name="class1_local_modules",
            repair_class="class1",
            description="Restore only author-supplied local modules proven by import verification.",
            command=(python, "-m", "repair.local_modules", "--apply"),
            evidence=("evidence/REPAIR_LOCAL_MODULES.json", "evidence/PROFILE_CLASS1.json"),
        ),
        Handler(
            name="class2_profile_overlays",
            repair_class="class2",
            description="Generate narrowly proven execution-profile overlays and their manifest.",
            command=(python, "-m", "evidence.profile_repairs"),
            evidence=("evidence/PROFILE_REPAIRS.json", "user_data/profile_repairs/"),
        ),
        Handler(
            name="class2_legacy_overlays",
            repair_class="class2",
            description="Generate legacy-ledger mechanical overlays, diffs, and a patch report.",
            command=(python, "repair/patch_class2.py"),
            evidence=("repair/patch_class2_report.json", "repair/patched/", "repair/patched/diffs/"),
        ),
        Handler(
            name="class2_vin_spearman_overlay",
            repair_class="class2",
            description="Create the separately classified ViNBuyVws explicit-Spearman overlay.",
            command=(python, "repair/patch_class2.py", "--strategy", "ViNBuyVws"),
            evidence=("repair/patch_class2_report.json", "repair/patched/", "repair/patched/diffs/"),
        ),
        Handler(
            name="repair_adjudication",
            repair_class="adjudication",
            description="Record hash-bound source refusals or explicit owner-scope closures; preserve the distinction in evidence.",
            command=(python, "-m", "repair.adjudicate", "--apply"),
            evidence=("evidence/REPAIR_ADJUDICATION.json",),
        ),
    )


def _active_docker() -> list[str]:
    """Repair writers must not change profiles while a benchmark is reading them."""
    completed = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}|{{.Image}}"], cwd=ROOT,
        text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RepairControllerError("could not inspect Docker: " + completed.stderr.strip())
    return [line for line in completed.stdout.splitlines() if line.strip()]


@contextlib.contextmanager
def _lock():
    """Keep explicit repair applications serialized and leave stale locks visible."""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = LOCK.open("x", encoding="utf-8", newline="\n")
    except FileExistsError as error:
        raise RepairControllerError("repair controller lock exists: " + str(LOCK)) from error
    try:
        handle.write(json.dumps({"pid": os.getpid(), "started_at": dt.datetime.now(dt.timezone.utc).isoformat()}) + "\n")
        handle.flush()
        yield
    finally:
        handle.close()
        LOCK.unlink(missing_ok=True)


def _record(handler: Handler, run_id: str, status: str, command: list[str],
            returncode: int | None = None, output: str = "", reason: str = "") -> dict:
    """Create one append-only orchestration record without replacing raw evidence."""
    return {
        "schema_version": 1,
        "run_id": run_id,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "controller": "repair.controller",
        "handler": handler.name,
        "repair_class": handler.repair_class,
        "status": status,
        "command": command,
        "evidence": list(handler.evidence),
        "returncode": returncode,
        "reason": reason,
        # Keep logs reproducible but bounded; full handler evidence remains authoritative.
        "output_tail": output[-4000:],
    }


def _append(record: dict) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _selected(classes: set[str], python: str | None = None) -> tuple[Handler, ...]:
    return tuple(handler for handler in handlers(python) if handler.repair_class in classes)


def plan(selected: tuple[Handler, ...]) -> str:
    """Render a side-effect-free plan suitable for review and automation logs."""
    lines = ["Repair controller plan (no writes):"]
    for handler in selected:
        lines.append("- %s [%s]: %s" % (handler.name, handler.repair_class, handler.description))
        lines.append("  command: " + subprocess.list2cmdline(list(handler.command)))
        lines.append("  evidence: " + ", ".join(handler.evidence))
    lines.append("Raw evidence stores remain handler-owned; controller log: evidence/REPAIR_CONTROLLER.jsonl")
    return "\n".join(lines)


def apply(selected: tuple[Handler, ...]) -> int:
    """Run selected handlers serially, preserving the first handler failure."""
    active = _active_docker()
    if active:
        raise RepairControllerError("active Docker runner blocks repair application: " + "; ".join(active))
    with _lock():
        for handler in selected:
            run_id = str(uuid.uuid4())
            try:
                completed = subprocess.run(handler.command, cwd=ROOT, text=True,
                                           capture_output=True, check=False)
            except OSError as error:
                _append(_record(handler, run_id, "ERROR", list(handler.command),
                                None, "", "could not start handler: " + str(error)))
                print("[ERROR] %s (run %s)" % (handler.name, run_id), file=sys.stderr)
                print("could not start handler: " + str(error), file=sys.stderr)
                return 1
            output = (completed.stdout or "") + (completed.stderr or "")
            status = "PASS" if completed.returncode == 0 else "ERROR"
            _append(_record(handler, run_id, status, list(handler.command),
                            completed.returncode, output,
                            "" if status == "PASS" else "handler exited non-zero"))
            print("[%s] %s (run %s)" % (status, handler.name, run_id))
            if output:
                print(output.rstrip())
            if status != "PASS":
                return completed.returncode or 1
    return 0


def selftest() -> None:
    """Check controller wiring only; individual handler selftests stay separate."""
    fixed_python = "audit-python"
    all_handlers = handlers(fixed_python)
    assert [handler.repair_class for handler in all_handlers] == ["class1", "class1", "class2", "class2", "class2", "adjudication"]
    assert len({handler.name for handler in all_handlers}) == len(all_handlers)
    assert all(handler.command[0] == fixed_python for handler in all_handlers)
    assert all(handler.evidence for handler in all_handlers)
    assert _selected({"class1"}, fixed_python) == all_handlers[:2]
    assert _selected({"class2"}, fixed_python) == all_handlers[2:5]
    assert _selected({"adjudication"}, fixed_python) == (all_handlers[5],)
    rendered = plan(all_handlers)
    assert "no writes" in rendered and "handler-owned" in rendered
    print("repair controller selftest: PASS")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--class", dest="classes", choices=("class1", "class2", "adjudication"),
                        action="append", help="repair class to include (default: both)")
    parser.add_argument("--apply", action="store_true",
                        help="execute selected handlers serially after Docker/lock checks")
    parser.add_argument("--selftest", action="store_true", help="validate controller wiring without writes")
    args = parser.parse_args(argv)

    if args.selftest:
        selftest()
        return 0
    classes = set(args.classes or ("class1", "class2", "adjudication"))
    selected = _selected(classes)
    print(plan(selected))
    if not args.apply:
        return 0
    return apply(selected)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RepairControllerError as error:
        print("REFUSED: " + str(error), file=sys.stderr)
        raise SystemExit(2)
