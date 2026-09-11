"""Causal trade attribution for identity-bound Model 1/2/3 archives."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from regime import attribution
from regime import gated_backtest
from evidence import profile_smoke


ROOT = Path(__file__).resolve().parents[1]


def _write_json(value: dict, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _candidate_output(frame):
    return frame.rename(columns={"strategy_id": "candidate_id"})


def _validate_header(manifest: dict, model: str) -> None:
    if manifest.get("schema_version") != 1:
        raise ValueError("gated manifest schema_version must be 1")
    if manifest.get("model") != model:
        raise ValueError(f"manifest model is {manifest.get('model')!r}, expected {model!r}")
    expected_scope = gated_backtest.MODELS[model]["scope"]
    if manifest.get("measurement_scope") != expected_scope:
        raise ValueError("gated manifest measurement_scope mismatch")
    candidate_ids = manifest.get("candidate_ids")
    if not isinstance(candidate_ids, list) or not candidate_ids:
        raise ValueError("gated manifest has no candidate_ids")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("gated manifest has duplicate candidate_ids")
    definitions = manifest.get("candidates")
    if (not isinstance(definitions, list) or
            {row.get("candidate_id") for row in definitions if isinstance(row, dict)} !=
            set(candidate_ids)):
        raise ValueError("gated manifest candidate definitions do not match candidate_ids")


def _load_archives(manifest: dict, model: str, daily_path: Path):
    profiles = attribution.eligible_profiles()
    daily_sha = attribution._file_sha(daily_path)
    accepted = []
    rejected = []
    candidate_evidence = []
    # Shared with regime.attribution and model_compare: keyed on (archive
    # path, strategy) plus that archive's own size/mtime, so re-running this
    # after adding candidates does not re-hash every already-verified
    # archive - only a new or genuinely changed one pays for a fresh read.
    cache = attribution._load_cache()
    definitions = {row.get("candidate_id"): row for row in manifest.get("candidates", [])}
    for candidate_id in manifest["candidate_ids"]:
        result = (manifest.get("results") or {}).get(candidate_id)
        reason = ""
        source_strategy = (result.get("strategy_id", "") if result else
                           definitions.get(candidate_id, {}).get("strategy_id", ""))
        profile = profiles.get(source_strategy)
        archive_path = ROOT / result.get("archive", "") if result else ROOT
        if not result:
            reason = "candidate_not_run"
        elif result.get("status") != "measured":
            reason = f"candidate_{result.get('status', 'unknown')}"
        elif result.get("candidate_id") != candidate_id:
            reason = "candidate_id_mismatch"
        elif result.get("model") != model:
            reason = "candidate_model_mismatch"
        elif result.get("measurement_scope") != gated_backtest.MODELS[model]["scope"]:
            reason = "candidate_measurement_scope_mismatch"
        elif not profile:
            reason = "source_strategy_not_currently_eligible"
        elif result.get("regime_daily_sha256") != daily_sha:
            reason = "regime_daily_hash_mismatch"
        elif gated_backtest._json_sha(result.get("gate_config")) != result.get("gate_rule_sha256"):
            reason = "gate_rule_hash_mismatch"
        elif any(result.get(key) != value
                 for key, value in profile_smoke._identity(profile).items()):
            reason = "canonical_identity_mismatch"
        elif not result.get("archive") or not archive_path.is_file():
            reason = "archive_missing"
        elif attribution._cached_file_sha(archive_path, cache) != result.get("archive_sha256"):
            reason = "archive_hash_mismatch"
        if reason:
            rejected.append({"candidate_id": candidate_id,
                             "strategy_id": source_strategy, "reason": reason})
            continue
        rows, archive_rejections = attribution.archive_inventory(
            ROOT, {source_strategy: profile}, [archive_path], cache)
        if archive_rejections or len(rows) != 1:
            rejected.append({
                "candidate_id": candidate_id,
                "strategy_id": source_strategy,
                "reason": (archive_rejections[0]["reason"] if archive_rejections
                           else "archive_did_not_resolve_to_one_strategy"),
            })
            continue
        record = rows[0]
        record.update({"analysis_id": candidate_id, "model": model})
        accepted.append(record)
        candidate_evidence.append({
            "candidate_id": candidate_id,
            "strategy_id": source_strategy,
            "archive": result["archive"],
            "archive_sha256": result["archive_sha256"],
            "gate_rule_sha256": result["gate_rule_sha256"],
            "timerange": result["timerange"],
            "runtime_id": result.get("runtime_id", "native_unversioned"),
        })
    attribution._save_cache(cache)
    return accepted, rejected, candidate_evidence


def selftest() -> None:
    sample = {
        "schema_version": 1,
        "model": "model1",
        "measurement_scope": gated_backtest.MODELS["model1"]["scope"],
        "candidate_ids": ["one"],
        "candidates": [{"candidate_id": "one", "strategy_id": "Example"}],
    }
    _validate_header(sample, "model1")
    try:
        _validate_header(sample, "model2")
    except ValueError as exc:
        assert "expected 'model2'" in str(exc)
    else:
        raise AssertionError("a Model 1 manifest must not be read as Model 2")
    model3 = dict(sample, model="model3",
                  measurement_scope=gated_backtest.MODELS["model3"]["scope"])
    _validate_header(model3, "model3")
    sample["candidate_ids"] = ["one", "one"]
    try:
        _validate_header(sample, "model1")
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate candidate ids must be rejected")
    print("gated attribution selftest: PASS")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=sorted(gated_backtest.MODELS))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--daily", type=Path, default=attribution.DAILY)
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if not args.model:
        parser.error("--model is required")
    manifest_path = args.manifest or gated_backtest.MODELS[args.model]["output"]
    if not manifest_path.is_file():
        parser.error(f"gated manifest not found: {manifest_path}")
    if not args.daily.is_file():
        parser.error(f"regime daily file not found: {args.daily}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _validate_header(manifest, args.model)
    accepted, rejected, evidence = _load_archives(manifest, args.model, args.daily)
    if rejected and not args.allow_partial:
        counts = {}
        for row in rejected:
            counts[row["reason"]] = counts.get(row["reason"], 0) + 1
        raise SystemExit(
            "gated candidate set is incomplete; no attribution written: " +
            ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
        )
    trades = attribution.attribute(accepted, args.daily)
    outdir = args.outdir or ROOT / "results" / "regime" / f"{args.model}_attribution"
    outdir.mkdir(parents=True, exist_ok=True)
    attribution._write(_candidate_output(trades), outdir / "trade_regime_attribution.csv")
    outputs = {
        "candidate_btc_regime_summary.csv": attribution.summarize_btc(trades),
        "candidate_regime_summary.csv": attribution.summarize(trades),
        "candidate_episode_summary.csv": attribution.summarize_episodes(trades),
        "candidate_phase_summary.csv": attribution.summarize_phase(trades),
        "candidate_phase_episode_summary.csv": attribution.summarize_phase_episodes(trades),
    }
    for name, frame in outputs.items():
        attribution._write(_candidate_output(frame), outdir / name)
    covered = sorted(set(trades["strategy_id"])) if not trades.empty else []
    payload = {
        "schema_version": 1,
        "model": args.model,
        "analysis_role": manifest.get("analysis_role"),
        "candidate_set_id": manifest.get("candidate_set_id"),
        "candidate_spec_sha256": manifest.get("candidate_spec_sha256"),
        "source_manifest": str(manifest_path),
        "source_manifest_sha256": attribution._file_sha(manifest_path),
        "regime_daily_sha256": attribution._file_sha(args.daily),
        "expected_candidates": len(manifest["candidate_ids"]),
        "attributed_candidates": len(covered),
        "attributed_candidate_ids": covered,
        "missing_candidate_ids": sorted(set(manifest["candidate_ids"]) - set(covered)),
        "accepted_archive_evidence": evidence,
        "rejected_candidates": rejected,
        "partial": bool(rejected),
        "trades": len(trades),
        "evidence_scope": (
            "Causal entry-time attribution of true entry-gated backtests. "
            "This artifact does not rank candidates or resolve preregistration choices."
        ),
    }
    _write_json(payload, outdir / "attribution_manifest.json")
    print(f"attributed {len(trades)} trades for {len(covered)}/{len(manifest['candidate_ids'])} "
          f"{args.model} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
