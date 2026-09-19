"""Reconcile missing smoke cards without repeating stronger measurements.

An identity-current canonical pooled Full-Backtest is stronger execution
evidence than the short smoke cascade.  This writer copies that existing card
into the smoke store with explicit reconstruction provenance.  Confirmed
duplicate implementations and test fixtures are documented as formal
exemptions, never fabricated as executed runs.  Every remaining row is emitted
as a real Smoke queue candidate.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import json
import os

from evidence import profile_smoke
from evidence.finalize_evidence import publication_lock, refresh_published_state
from evidence.pipeline_state import EvidenceStore, completed_full_backtest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL_BACKTEST = os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json")
AUDIT_OUTPUT = os.path.join(ROOT, "evidence", "PROFILE_SMOKE_BACKFILL.json")
PIPELINE_STATE = os.path.join(ROOT, "evidence", "PIPELINE_STATE.json")


def _json(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _profiles():
    with io.open(profile_smoke.MANIFEST, newline="", encoding="utf-8-sig") as handle:
        return {row["strategy_id"]: row for row in csv.DictReader(handle)}


def classify():
    profiles = _profiles()
    smoke = profile_smoke.read_results(profile_smoke.OUTPUT)
    full_document = _json(FULL_BACKTEST)
    full = full_document.get("results") or {}
    published = (_json(PIPELINE_STATE).get("strategies") or {})
    store = EvidenceStore(ROOT)
    records = {}
    imports = {}
    for strategy_id in sorted(set(profiles) - set(smoke["results"])):
        profile = profiles[strategy_id]
        baseline = store.baseline.get(strategy_id) or {}
        current = published.get(strategy_id) or {}
        resolved = store.resolve(strategy_id, profile, baseline)
        full_record = full.get(strategy_id) or {}
        if completed_full_backtest(profile, full_record):
            if full_record.get("status") != "measured":
                raise AssertionError((strategy_id, full_record.get("status")))
            imported = dict(full_record)
            imported.update({
                "record_origin": "reconstructed_from_identity_current_full_backtest",
                "reconstructed_from": "results/regime/full_backtest_manifest.json",
                "smoke_equivalent": False,
                "documentation_note": (
                    "No short Smoke card was retained. This identity-current "
                    "canonical pooled Full-Backtest card is stronger execution evidence."),
            })
            imports[strategy_id] = imported
            disposition = "reconstruct_from_identity_current_full_backtest"
        elif current.get("artifact_role") != "strategy":
            disposition = "not_applicable_non_strategy_artifact"
        elif current.get("primary_reason") == "duplicate_implementation":
            disposition = "not_applicable_confirmed_duplicate"
        elif current.get("cohort") == "excluded":
            disposition = "not_applicable_terminal_exclusion"
        else:
            disposition = "requires_smoke_run"
        records[strategy_id] = {
            "strategy_id": strategy_id,
            "disposition": disposition,
            "artifact_role": current.get("artifact_role", ""),
            "cohort": current.get("cohort", ""),
            "primary_reason": current.get("primary_reason", ""),
            "canonical_file": profile.get("canonical_file", ""),
            "run_profile": profile.get("run_profile", ""),
            "full_backtest_status": full_record.get("status", ""),
            "full_backtest_identity_current": completed_full_backtest(profile, full_record),
            "measurement_producer_store": resolved["measurement_store"],
        }
    return smoke, records, imports


def document(records, generated_at=None):
    counts = {}
    for record in records.values():
        key = record["disposition"]
        counts[key] = counts.get(key, 0) + 1
    return {
        "schema_version": 1,
        "generated_at": generated_at or datetime.datetime.now().replace(
            microsecond=0).isoformat(),
        "policy": (
            "Reuse only identity-current stronger execution evidence; document "
            "formal exemptions; run every remaining strategy through Smoke."),
        "counts": dict(sorted(counts.items())),
        "records": records,
    }


def finalize_run():
    """Replace queued dispositions with the canonical Smoke result.

    The original 496-row reconciliation is retained verbatim apart from the
    rows that were deliberately queued.  Re-running ``classify`` here would
    lose that audit population because those rows now exist in the Smoke
    store.
    """
    audit = _json(AUDIT_OUTPUT)
    smoke = profile_smoke.read_results(profile_smoke.OUTPUT).get("results") or {}
    pending = []
    for strategy_id, record in audit["records"].items():
        if record.get("disposition") != "requires_smoke_run":
            continue
        result = smoke.get(strategy_id)
        if not result:
            pending.append(strategy_id)
            continue
        status = result.get("status") or "unknown"
        record["disposition"] = "smoke_completed_%s" % status
        record["smoke_status"] = status
        record["smoke_runtime_id"] = result.get("runtime_id", "")
        record["smoke_debug_log"] = result.get("debug_log", "")
        record["smoke_archive"] = result.get("archive", "")
        record["smoke_long_trades"] = result.get("long_trades")
        record["smoke_short_trades"] = result.get("short_trades")
    if pending:
        raise RuntimeError("Smoke results still missing: %s" % ", ".join(pending))
    audit["generated_at"] = datetime.datetime.now().replace(microsecond=0).isoformat()
    audit["counts"] = document(audit["records"])["counts"]
    return audit


def _write_json(path, payload):
    temporary = path + ".tmp"
    with io.open(temporary, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--finalize-run", action="store_true")
    args = parser.parse_args(argv)
    if args.finalize_run:
        audit = finalize_run()
        with publication_lock():
            _write_json(AUDIT_OUTPUT, audit)
            refresh_published_state()
        print(json.dumps(audit["counts"], indent=2, sort_keys=True))
        return 0
    smoke, records, imports = classify()
    audit = document(records)
    print(json.dumps(audit["counts"], indent=2, sort_keys=True))
    queue = [name for name, record in records.items()
             if record["disposition"] == "requires_smoke_run"]
    print("real smoke queue: %d" % len(queue))
    if not args.apply:
        return 0
    with publication_lock():
        for strategy_id, record in imports.items():
            smoke["results"][strategy_id] = record
        _write_json(profile_smoke.OUTPUT, smoke)
        _write_json(AUDIT_OUTPUT, audit)
        refresh_published_state()
    print("reconstructed %d stronger measurements; documented %d rows" %
          (len(imports), len(records)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
