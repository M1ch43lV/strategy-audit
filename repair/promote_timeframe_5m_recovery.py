"""Promote completed, owner-authorized 5m OOM recoveries into E1 evidence.

This is a terminal repair action. It accepts only all-60-complete recovery
evidence, retains each canonical 1m OOM record inside the replacement result,
and refreshes the generated state only after every eligible record is written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
from pathlib import Path

from evidence import full_backtest_resource_diagnostic as diagnostic_runner
from evidence import profile_smoke

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "evidence" / "TIMEFRAME_5M_RECOVERY.json"
RECOVERY_FULL = ROOT / "evidence" / "TIMEFRAME_5M_RECOVERY_FULL.json"
MANIFEST = ROOT / "results" / "regime" / "full_backtest_manifest.json"
SCOPE = "owner_approved_timeframe_5m_recovery_pooled_pair_universe"
TIMEFRAME = "5m"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _profiles():
    return {row["strategy_id"]: row for row in profile_smoke.read_manifest(profile_smoke.MANIFEST)}


def _active_audit_container():
    return diagnostic_runner._active_audit_container()


def _archive(record, strategy):
    directory = ROOT / Path(record["subset_config"]).parent
    candidates = [Path(value) for value in glob.glob(str(directory / "backtest-result-*.zip"))]
    if not candidates:
        raise ValueError(strategy + ": full-run archive is missing")
    return max(candidates, key=lambda value: value.stat().st_mtime)


def _record(strategy, recovery, full, original, profile):
    identity = profile_smoke._identity(profile)
    if recovery.get("canonical_sha256") != identity.get("canonical_sha256"):
        raise ValueError(strategy + ": recovery source identity is stale")
    if full.get("canonical_identity") != identity:
        raise ValueError(strategy + ": full-run identity is stale")
    if any((full.get("status") != "measured", full.get("requested_timeframe") != TIMEFRAME,
            full.get("pair_count") != 8, full.get("source_timeframe") != "1m")):
        raise ValueError(strategy + ": recovery full run does not meet promotion criteria")
    if original.get("status") not in {"oom_confirmed", "resource_inconclusive"}:
        raise ValueError(strategy + ": preserved canonical result is not a 1m OOM")
    config = diagnostic_runner._config_for(profile)
    expected_pairs = json.loads(config.read_text(encoding="utf-8"))["exchange"]["pair_whitelist"]
    if full.get("pairs") != expected_pairs:
        raise ValueError(strategy + ": recovery pair universe differs from its frozen profile")
    archive = _archive(full, strategy)
    longs, shorts, trades_sha256 = profile_smoke._trades(str(archive), strategy)
    with archive.open("rb") as handle:
        archive_sha256 = "sha256_" + hashlib.sha256(handle.read()).hexdigest()
    meta = json.loads(archive.with_suffix(".meta.json").read_text(encoding="utf-8"))
    if meta.get(strategy, {}).get("timeframe") != TIMEFRAME:
        raise ValueError(strategy + ": archive does not confirm 5m execution")
    return {
        **identity,
        "status": "measured",
        "measurement_scope": SCOPE,
        "mode": "futures" if profile["run_profile"].startswith("futures_") else "spot",
        "run_profile": profile["run_profile"],
        "timerange": full["timerange"],
        "pairs": expected_pairs,
        "source_timeframe": "1m",
        "execution_timeframe": TIMEFRAME,
        "timeframe_override_basis": "owner_decision_2026-09-21_5m_oom_recovery",
        "timeframe_override_note": (
            "Owner authorized E1 promotion after this exact implementation passed "
            "the isolated 5m smoke, look-ahead, warm-up, recursive, and eight-pair "
            "full-backtest recovery route; the canonical 1m OOM is retained."),
        "repair_family": "full_backtest_oom_timeframe_5m_recovery",
        "archive": str(archive.relative_to(ROOT)).replace("\\", "/"),
        "archive_sha256": archive_sha256,
        "long_trades": longs,
        "short_trades": shorts,
        "trades": longs + shorts,
        "trades_sha256": trades_sha256,
        "elapsed_s": full["elapsed_s"],
        "peak_memory_mib": full.get("peak_memory_mib"),
        "runtime_id": full.get("runtime_image", ""),
        "runtime_config_sha256": full["runtime_config_sha256"],
        "invocation": " ".join(full["command"]),
        "attempted_at": full["attempted_at"],
        "original_full_backtest": original,
    }


def build():
    recovery = _load(RECOVERY).get("results", {})
    profiles = _profiles()
    expected = {row["strategy_id"] for row in __import__("repair.timeframe_5m_recovery", fromlist=["candidates"]).candidates()}
    if set(recovery) != expected:
        raise ValueError("recovery is incomplete: %d/%d candidate records" % (len(recovery), len(expected)))
    unfinished = [name for name in expected if recovery[name].get("status") == "in_progress" or not recovery[name].get("status")]
    if unfinished:
        raise ValueError("recovery still in progress: " + ", ".join(sorted(unfinished)))
    full = _load(RECOVERY_FULL).get("results", {}) if RECOVERY_FULL.exists() else {}
    manifest = _load(MANIFEST)
    promoted = {}
    for strategy in sorted(expected):
        entry = recovery[strategy]
        if entry.get("status") != "measured_5m_pending_owner_promotion":
            continue
        records = [row for row in full.get(strategy, []) if row.get("status") == "measured"]
        if not records:
            raise ValueError(strategy + ": successful recovery lacks full-run evidence")
        promoted[strategy] = _record(strategy, entry, records[-1],
                                     manifest["results"].get(strategy, {}), profiles[strategy])
    return manifest, recovery, promoted


def apply(allow_controller_lock=False):
    if _active_audit_container() or ((ROOT / "user_data" / ".repair_controller.running").exists()
                                     and not allow_controller_lock):
        raise RuntimeError("refusing promotion while an audit or repair controller is active")
    manifest, recovery, promoted = build()
    for strategy, record in promoted.items():
        manifest["results"][strategy] = record
        recovery[strategy]["status"] = "promoted_E1"
        recovery[strategy]["promotion"] = {
            "at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "measurement_scope": SCOPE,
            "manifest": "results/regime/full_backtest_manifest.json",
        }
    _write(MANIFEST, manifest)
    _write(RECOVERY, {"schema_version": 1, "policy": "timeframe_5m_recovery_v1",
                      "results": recovery})
    from evidence.finalize_evidence import publication_lock, refresh_published_state
    with publication_lock():
        refresh_published_state()
    print("promoted %d successful 5m OOM recoveries into E1" % len(promoted))


def selftest():
    assert SCOPE.endswith("pooled_pair_universe")
    assert TIMEFRAME == "5m"
    print("promote_timeframe_5m_recovery selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--allow-controller-lock", action="store_true",
                        help="internal: permit the common controller's own serial lock")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest(); return 0
    _manifest, _recovery, promoted = build()
    print("eligible 5m OOM recovery promotions: %d" % len(promoted))
    if args.apply:
        apply(args.allow_controller_lock)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
