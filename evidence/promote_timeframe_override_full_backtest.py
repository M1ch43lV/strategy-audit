"""Promote one owner-approved timeframe override into the pooled manifest.

The original full-backtest result remains under ``original_full_backtest``.
This is a deliberately narrow, hash-bound exception writer; it never changes
strategy source, the normal runner, or any other strategy's result.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from pathlib import Path

from evidence import profile_smoke


ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC = ROOT / "evidence" / "FULL_BACKTEST_RESOURCE_DIAGNOSTIC.json"
MANIFEST = ROOT / "results" / "regime" / "full_backtest_manifest.json"
CONFIG = ROOT / "runtime" / "profile_futures_config.json"
SCOPE = "owner_approved_timeframe_override_pooled_pair_universe"


def _sha256(path: Path) -> str:
    return "sha256_" + hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, data: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _profile(strategy: str) -> dict:
    for row in profile_smoke.read_manifest(profile_smoke.MANIFEST):
        if row["strategy_id"] == strategy:
            return row
    raise ValueError("strategy is absent from execution profiles: " + strategy)


def _diagnostic(strategy: str, timeframe: str) -> dict:
    records = json.loads(DIAGNOSTIC.read_text(encoding="utf-8")).get("results", {}).get(strategy, [])
    matches = [record for record in records if record.get("status") == "measured"
               and record.get("requested_timeframe") == timeframe
               and record.get("pair_count") == 8]
    if not matches:
        raise ValueError("no measured eight-pair diagnostic at timeframe " + timeframe)
    return matches[-1]


def build(strategy: str, timeframe: str) -> tuple[dict, dict]:
    profile = _profile(strategy)
    diagnostic = _diagnostic(strategy, timeframe)
    identity = profile_smoke._identity(profile)
    if diagnostic.get("canonical_identity") != identity:
        raise ValueError("diagnostic identity does not match current source/config")
    source_timeframe = diagnostic.get("source_timeframe")
    if not source_timeframe or source_timeframe == timeframe:
        raise ValueError("override must differ from the declared source timeframe")
    directory = ROOT / Path(diagnostic["subset_config"]).parent
    archives = [Path(path) for path in glob.glob(str(directory / "backtest-result-*.zip"))]
    if not archives:
        raise ValueError("diagnostic archive is missing")
    archive = max(archives, key=lambda item: item.stat().st_mtime)
    longs, shorts, trades_sha256 = profile_smoke._trades(str(archive), strategy)
    with archive.open("rb") as handle:
        archive_sha256 = "sha256_" + hashlib.sha256(handle.read()).hexdigest()
    meta_path = archive.with_suffix(".meta.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get(strategy, {}).get("timeframe") != timeframe:
        raise ValueError("archive does not confirm requested timeframe " + timeframe)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    original = manifest.get("results", {}).get(strategy) or {}
    if original.get("status") != "resource_inconclusive":
        raise ValueError("promotion requires the preserved 1m resource_inconclusive result")
    expected_pairs = json.loads(CONFIG.read_text(encoding="utf-8"))["exchange"]["pair_whitelist"]
    if diagnostic.get("pairs") != expected_pairs:
        raise ValueError("diagnostic pair universe differs from the canonical futures universe")
    record = {
        **identity,
        "status": "measured",
        "measurement_scope": SCOPE,
        "mode": "futures",
        "run_profile": profile["run_profile"],
        "timerange": "20200301-20260821",
        "pairs": expected_pairs,
        "source_timeframe": source_timeframe,
        "execution_timeframe": timeframe,
        "timeframe_override_basis": "owner_decision_2026-09-20",
        "timeframe_override_note": (
            "Owner approved a 5m pooled Full-Backtest after the same 1m "
            "implementation ended resource_inconclusive; the 1m OOM record is retained."),
        "archive": str(archive.relative_to(ROOT)).replace("\\", "/"),
        "archive_sha256": archive_sha256,
        "long_trades": longs,
        "short_trades": shorts,
        "trades": longs + shorts,
        "trades_sha256": trades_sha256,
        "elapsed_s": diagnostic["elapsed_s"],
        "peak_memory_mib": diagnostic.get("peak_memory_mib"),
        "runtime_id": diagnostic.get("runtime_image", ""),
        "runtime_config_sha256": diagnostic["runtime_config_sha256"],
        "invocation": " ".join(diagnostic["command"]),
        "attempted_at": diagnostic["attempted_at"],
        "original_full_backtest": original,
    }
    return manifest, record


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    manifest, record = build(args.strategy, args.timeframe)
    print(json.dumps({key: record[key] for key in (
        "status", "measurement_scope", "source_timeframe", "execution_timeframe",
        "trades", "peak_memory_mib", "timeframe_override_basis")}, indent=2))
    if not args.apply:
        return 0
    manifest.setdefault("results", {})[args.strategy] = record
    _write(MANIFEST, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
