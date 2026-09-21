"""Run the source-preserving 5m recovery route for canonical 1m full-run OOMs.

This repair handler does not alter strategies, canonical profiles, C10/E1, or
the canonical full manifest. Each qualifying 1m OOM repeats smoke, look-ahead,
warm-up convergence, and recursive-bias at 5m before a separate eight-pair
5m full-run resource measurement is permitted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

from evidence import full_backtest_resource_diagnostic as resource_diagnostic
from evidence import profile_bias, profile_smoke, warmup_convergence
from tools.run_metadata import append_record

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "evidence" / "EXECUTION_PROFILES.csv"
FULL_MANIFEST = ROOT / "results" / "regime" / "full_backtest_manifest.json"
OUTPUT = ROOT / "evidence" / "TIMEFRAME_5M_RECOVERY.json"
FULL_OUTPUT = ROOT / "evidence" / "TIMEFRAME_5M_RECOVERY_FULL.json"
METADATA = ROOT / "evidence" / "RUN_METADATA.jsonl"
TIMEFRAME = "5m"
SMOKE_TIMERANGES = ("20200301-20200401", "20200301-20200601")
SMOKE_TRADE_FLOOR = 10


def _load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _identity(row):
    value = dict(profile_smoke._identity(row))
    value["source_execution_timeframe"] = row.get("execution_timeframe", "")
    value["recovery_execution_timeframe"] = TIMEFRAME
    return value


def candidates():
    """Join the profile-owned timeframe to canonical full-run OOM evidence."""
    profiles = {row["strategy_id"]: row for row in profile_smoke.read_manifest(str(PROFILES))}
    full = _load(FULL_MANIFEST, {}).get("results", {})
    return sorted((row for name, row in profiles.items()
                   if row.get("execution_timeframe") == "1m"
                   and full.get(name, {}).get("status") in
                   {"oom_confirmed", "resource_inconclusive"}),
                  key=lambda row: row["strategy_id"].lower())


def _gate_status(gate, result):
    if gate == "smoke":
        if result.get("status") == "measured":
            return "PASS" if int(result.get("trades", 0)) >= SMOKE_TRADE_FLOOR else "FAIL"
        return "ERROR"
    if gate in {"lookahead", "recursive"}:
        return {"PASS": "PASS", "FOUND": "FAIL"}.get(result.get("status"), "ERROR")
    if gate == "warmup_recursive":
        return "PASS" if result.get("state") == "converged" else "ERROR"
    if gate == "full_backtest":
        return "PASS" if result.get("status") == "measured" else "ERROR"
    raise ValueError("unknown gate: " + gate)


def _pass(gate, result):
    return bool(result) and _gate_status(gate, result) == "PASS"


def _metadata(strategy, gate, result, task, previous=""):
    # Run metadata deliberately models warm-up and the final recursive check
    # as one routing gate. Keep the detailed substep in ``task``/evidence,
    # rather than inventing a second gate name outside its public contract.
    metadata_gate = "warmup_recursive" if gate == "recursive" else gate
    append_record(METADATA, {
        "run_id": "timeframe-5m-%s-%s" % (metadata_gate, hashlib.sha256(
            (strategy + dt.datetime.now(dt.timezone.utc).isoformat()).encode()).hexdigest()[:16]),
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "gate": metadata_gate,
        "model": "gpt-5.6-terra" if metadata_gate == "full_backtest" else "gpt-5.6-luna",
        "reasoning": "medium" if metadata_gate == "full_backtest" else "low",
        "status": _gate_status(gate, result),
        "strategy_ref": strategy + " [5m recovery]",
        "task": task,
        "command": result.get("invocation") or result.get("command") or "recorded API invocation",
        "evidence": ["evidence/TIMEFRAME_5M_RECOVERY.json"],
        "tool_versions": {"controller": "timeframe_5m_recovery_v1", "python": sys.version.split()[0]},
        "escalation_reason": "",
        "previous_run_id": previous,
    })


def _finalize(record):
    if not _pass("smoke", record.get("smoke")):
        record["status"] = "recovery_blocked_smoke"
    elif not _pass("lookahead", record.get("lookahead")):
        record["status"] = "recovery_blocked_lookahead"
    elif not _pass("warmup_recursive", record.get("warmup")):
        record["status"] = "recovery_blocked_warmup"
    elif not _pass("recursive", record.get("recursive")):
        record["status"] = "recovery_blocked_recursive"
    elif record.get("full_backtest"):
        record["status"] = ("measured_5m_pending_owner_promotion"
                            if _pass("full_backtest", record["full_backtest"])
                            else "recovery_full_backtest_not_measured")
    else:
        record["status"] = "eligible_for_5m_full_backtest"


def run_one(row, data, smoke_timeout, gate_timeout, full_timeout, force=False):
    strategy = row["strategy_id"]
    identity = _identity(row)
    old = data.setdefault("results", {}).get(strategy, {})
    record = dict(old) if all(old.get(k) == v for k, v in identity.items()) else {}
    record.update(identity)
    record.update({"strategy_id": strategy,
                   "repair_family": "full_backtest_oom_timeframe_5m_recovery",
                   "canonical_full_backtest_reference": "results/regime/full_backtest_manifest.json",
                   "source_strategy_is_unchanged": True,
                   "updated_at": dt.datetime.now(dt.timezone.utc).isoformat()})

    if force or not record.get("smoke"):
        record["smoke"] = profile_smoke.run_cascade(
            row, SMOKE_TIMERANGES, SMOKE_TRADE_FLOOR, smoke_timeout,
            config_overrides={"timeframe": TIMEFRAME},
            policy_id="timeframe_5m_recovery_smoke_v1",
            extra_cli_args=["--timeframe", TIMEFRAME],
            artifact_namespace="timeframe_5m_recovery_smoke")
        _metadata(strategy, "smoke", record["smoke"], "5m recovery smoke cascade", "canonical-1m-oom")
        data["results"][strategy] = record; _write(OUTPUT, data)
    if not _pass("smoke", record.get("smoke")):
        _finalize(record); return record

    overrides = {"timeframe": TIMEFRAME}
    if force or not record.get("lookahead"):
        record["lookahead"] = profile_bias.run_diagnostic(
            row, "lookahead", gate_timeout, min(gate_timeout, 300), config_overrides=overrides)
        _metadata(strategy, "lookahead", record["lookahead"], "5m recovery look-ahead analysis")
        data["results"][strategy] = record; _write(OUTPUT, data)
    if not _pass("lookahead", record.get("lookahead")):
        _finalize(record); return record

    if force or not record.get("warmup"):
        record["warmup"] = warmup_convergence.resolve(row, gate_timeout, overrides=overrides)
        _metadata(strategy, "warmup_recursive", record["warmup"], "5m recovery warm-up convergence ladder")
        data["results"][strategy] = record; _write(OUTPUT, data)
    if not _pass("warmup_recursive", record.get("warmup")):
        _finalize(record); return record

    if force or not record.get("recursive"):
        record["recursive"] = profile_bias.run_diagnostic(
            row, "recursive", gate_timeout, min(gate_timeout, 300), config_overrides=overrides,
            settled_startup=record["warmup"]["chosen_startup_candle_count"])
        _metadata(strategy, "recursive", record["recursive"], "5m recovery final recursive-bias analysis")
        data["results"][strategy] = record; _write(OUTPUT, data)
    if not _pass("recursive", record.get("recursive")):
        _finalize(record); return record

    if force or not record.get("full_backtest"):
        record["full_backtest"] = resource_diagnostic.run(
            strategy, pair_count=8, timeout=full_timeout, output=FULL_OUTPUT, timeframe=TIMEFRAME)
        _metadata(strategy, "full_backtest", record["full_backtest"],
                  "5m recovery eight-pair full-backtest resource run", "canonical-1m-oom")
        data["results"][strategy] = record; _write(OUTPUT, data)
    _finalize(record)
    return record


def selftest():
    assert len(candidates()) == 60
    assert _gate_status("smoke", {"status": "measured", "trades": 10}) == "PASS"
    assert _gate_status("lookahead", {"status": "FOUND"}) == "FAIL"
    assert _gate_status("warmup_recursive", {"state": "converged"}) == "PASS"
    assert _gate_status("full_backtest", {"status": "resource_inconclusive"}) == "ERROR"
    print("timeframe_5m_recovery selftest: PASS (60 candidates)")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--smoke-timeout", type=int, default=300)
    parser.add_argument("--gate-timeout", type=int, default=1200)
    parser.add_argument("--full-timeout", type=int, default=3600)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--promote-successes", action="store_true",
                        help="after all candidates finish, apply the owner-authorized E1 promotions")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest(); return 0
    rows = candidates()
    if args.strategy:
        wanted = set(args.strategy)
        rows = [row for row in rows if row["strategy_id"] in wanted]
        missing = wanted - {row["strategy_id"] for row in rows}
        if missing:
            raise SystemExit("not a 1m OOM recovery candidate: " + ", ".join(sorted(missing)))
    if args.limit:
        rows = rows[:args.limit]
    print("5m OOM recovery candidates: %d" % len(rows))
    if not args.apply:
        print("plan only; pass --apply to run serially without changing canonical state")
        return 0
    data = _load(OUTPUT, {"schema_version": 1, "policy": "timeframe_5m_recovery_v1", "results": {}})
    for number, row in enumerate(rows, 1):
        record = run_one(row, data, args.smoke_timeout, args.gate_timeout, args.full_timeout, args.force)
        data["results"][row["strategy_id"]] = record; _write(OUTPUT, data)
        print("[%d/%d] %s %s" % (number, len(rows), row["strategy_id"], record["status"]), flush=True)
    if args.promote_successes:
        # This must happen only after the serial run closed its own work. The
        # standalone promoter additionally refuses a live controller lock.
        from repair import promote_timeframe_5m_recovery
        return promote_timeframe_5m_recovery.main(["--apply", "--allow-controller-lock"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
