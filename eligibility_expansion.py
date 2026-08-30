# -*- coding: utf-8 -*-
"""Freeze the outcome-blind eligibility expansion candidate universe.

This inventory consumes technical Stage 6 artifacts only.  It must not read
strategy-by-regime performance or ranking outputs.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
ELIGIBILITY = os.path.join(ROOT, "REGIME_ELIGIBILITY.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
CLUSTERS = os.path.join(ROOT, "cluster", "CLUSTERS.csv")
PLAN = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_PLAN.md")
PREREGISTRATION = os.path.join(ROOT, "REGIME_PREREGISTRATION.md")
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_CANDIDATES.csv")
MISSINGNESS = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_MISSINGNESS.csv")
MANIFEST = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_MANIFEST.json")
REPORT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION.md")

FROZEN_AT = "2026-08-30"
SCHEMA_VERSION = 1

CANDIDATE_FIELDS = [
    "strategy_id", "run_profile", "implementation_id", "expansion_wave",
    "scheduled", "baseline_eligibility_status", "baseline_exclusion_reasons",
    "baseline_pending_reasons", "baseline_recursive_kind",
    "baseline_canonical_measured", "baseline_canonical_observed_trades",
    "terminal_status", "source_repo", "canonical_file", "execution_timeframe",
    "artifact_role", "canonical_population", "repair_class", "repair_rules",
    "equivalence_status", "runtime_smoke_status", "classification_status",
    "classification_reason", "taxonomy_logic", "taxonomy_speed",
    "taxonomy_complexity", "taxonomy_regime_hypothesis", "family_id",
    "family_evidence",
]

MISSINGNESS_FIELDS = ["dimension", "value", "count", "share_of_wave_c"]


def _read_csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _sha256(path):
    digest = hashlib.sha256()
    with io.open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256_" + digest.hexdigest()


def _reasons(value):
    return set(filter(None, (value or "").split(";")))


def expansion_wave(row):
    """Return the frozen wave label using technical evidence only."""
    hard = _reasons(row.get("exclusion_reasons"))
    pending = _reasons(row.get("pending_reasons"))
    status = row.get("eligibility_status")
    if status == "eligible":
        return "E0_strict67"
    if status == "pending_diagnostics":
        return "A_pending_diagnostics"
    if hard == {"recursive_bias_found"} and not pending and \
            row.get("recursive_kind") == "refused_no_warmup":
        return "B_warmup_refusal"
    if hard == {"canonical_implementation_not_measured"}:
        return "C_measurement_recovery"
    if hard == {"recursive_bias_found"} and not pending and \
            row.get("recursive_kind") == "drift_measured":
        return "D_recursive_drift"
    return "not_scheduled"


def _terminal_status(wave):
    if wave == "E0_strict67":
        return "admitted_E0"
    if wave == "not_scheduled":
        return "baseline_excluded"
    return "queued"


def build_rows(eligibility_rows, profile_rows, cluster_rows):
    profiles = {row["strategy_id"]: row for row in profile_rows}
    clusters = {row["strategy"]: row for row in cluster_rows}
    output = []
    for eligible in eligibility_rows:
        strategy = eligible["strategy_id"]
        profile = profiles.get(strategy, {})
        cluster = clusters.get(strategy, {})
        wave = expansion_wave(eligible)
        output.append({
            "strategy_id": strategy,
            "run_profile": eligible.get("run_profile", ""),
            "implementation_id": eligible.get("implementation_id", ""),
            "expansion_wave": wave,
            "scheduled": str(wave != "not_scheduled").lower(),
            "baseline_eligibility_status": eligible.get("eligibility_status", ""),
            "baseline_exclusion_reasons": eligible.get("exclusion_reasons", ""),
            "baseline_pending_reasons": eligible.get("pending_reasons", ""),
            "baseline_recursive_kind": eligible.get("recursive_kind", ""),
            "baseline_canonical_measured": eligible.get("canonical_measured", ""),
            "baseline_canonical_observed_trades": eligible.get(
                "canonical_observed_trades", ""),
            "terminal_status": _terminal_status(wave),
            "source_repo": profile.get("repo", ""),
            "canonical_file": profile.get("canonical_file", ""),
            "execution_timeframe": profile.get("execution_timeframe", ""),
            "artifact_role": profile.get("artifact_role", ""),
            "canonical_population": profile.get("canonical_population", ""),
            "repair_class": profile.get("repair_class", ""),
            "repair_rules": profile.get("repair_rules", ""),
            "equivalence_status": profile.get("equivalence_status", ""),
            "runtime_smoke_status": profile.get("runtime_smoke_status", ""),
            "classification_status": profile.get("classification_status", ""),
            "classification_reason": profile.get("classification_reason", ""),
            "taxonomy_logic": cluster.get("logic", ""),
            "taxonomy_speed": cluster.get("speed", ""),
            "taxonomy_complexity": cluster.get("complexity", ""),
            "taxonomy_regime_hypothesis": cluster.get("regime_hypothesis", ""),
            # Exact copy-family dependence requires a dedicated artifact. Repo or
            # taxonomy labels must not be silently promoted to family identity.
            "family_id": "",
            "family_evidence": "pending_dedicated_family_manifest",
        })
    return output


MISSINGNESS_DIMENSIONS = [
    "run_profile", "source_repo", "execution_timeframe", "artifact_role",
    "canonical_population", "repair_class", "equivalence_status",
    "runtime_smoke_status", "classification_status", "taxonomy_logic",
    "taxonomy_complexity",
]


def build_missingness(rows):
    wave_c = [row for row in rows if row["expansion_wave"] == "C_measurement_recovery"]
    total = len(wave_c)
    output = []
    for dimension in MISSINGNESS_DIMENSIONS:
        counts = collections.Counter((row.get(dimension) or "<missing>") for row in wave_c)
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            output.append({
                "dimension": dimension,
                "value": value,
                "count": count,
                "share_of_wave_c": "%.6f" % (float(count) / total if total else 0.0),
            })
    return output


def _csv_bytes(rows, fields):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def _member_hash(rows, waves):
    members = sorted(
        "%s|%s|%s" % (row["strategy_id"], row["run_profile"], row["implementation_id"])
        for row in rows if row["expansion_wave"] in waves)
    return "sha256_" + hashlib.sha256("\n".join(members).encode("utf-8")).hexdigest()


def build_manifest(rows, input_paths):
    waves = collections.Counter(row["expansion_wave"] for row in rows)
    candidate_waves = {
        "A_pending_diagnostics", "B_warmup_refusal",
        "C_measurement_recovery", "D_recursive_drift",
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "frozen_before_stage9_ranking",
        "frozen_at": FROZEN_AT,
        "outcome_blind": True,
        "unit": "strategy_id_x_native_run_profile",
        "inputs": {
            os.path.relpath(path, ROOT).replace(os.sep, "/"): {
                "sha256": _sha256(path),
                "bytes": os.path.getsize(path),
            }
            for path in input_paths
        },
        "baseline": {
            "total": len(rows),
            "E0_strict67": waves["E0_strict67"],
            "scheduled_expansion_candidates": sum(waves[name] for name in candidate_waves),
            "not_scheduled": waves["not_scheduled"],
        },
        "waves": dict(sorted(waves.items())),
        "E0_member_sha256": _member_hash(rows, {"E0_strict67"}),
        "expansion_candidate_member_sha256": _member_hash(rows, candidate_waves),
        "candidate_members": {
            wave: sorted(
                "%s|%s|%s" % (row["strategy_id"], row["run_profile"],
                               row["implementation_id"])
                for row in rows if row["expansion_wave"] == wave)
            for wave in sorted(candidate_waves)
        },
        "stop_states": [
            "admitted_E1", "retained_E2", "assigned_E3",
            "hard_ineligible", "pending_attempts_exhausted",
        ],
        "ranking_outputs_read": False,
    }


def _report(rows, missingness, manifest):
    wave_counts = collections.Counter(row["expansion_wave"] for row in rows)
    lines = [
        "# Eligibility expansion inventory", "",
        "**Frozen:** 2026-08-30, before Stage 9 ranking",
        "**Protocol:** `ELIGIBILITY_EXPANSION_PLAN.md`", "",
        "This inventory uses technical Stage 6 evidence only. No strategy-by-regime",
        "performance or ranking output was read to select candidates.", "",
        "## Frozen waves", "", "| Wave | Rows |", "|---|---:|",
    ]
    for wave, count in sorted(wave_counts.items()):
        lines.append("| `%s` | %d |" % (wave, count))
    lines.extend([
        "", "The four expansion waves contain **%d** candidates. E0 contains "
        "**%d** already eligible profiles; **%d** rows are not scheduled by this "
        "equivalent-repair expansion." % (
            manifest["baseline"]["scheduled_expansion_candidates"],
            manifest["baseline"]["E0_strict67"],
            manifest["baseline"]["not_scheduled"]),
        "", "Candidate member hash: `%s`." %
        manifest["expansion_candidate_member_sha256"],
        "", "## Wave C missingness", "",
        "The 230 measurement-recovery rows are summarized without treating source",
        "taxonomy as an eligibility rule. `<missing>` remains explicit.", "",
    ])
    for dimension in MISSINGNESS_DIMENSIONS:
        subset = [row for row in missingness if row["dimension"] == dimension]
        lines.extend(["### `%s`" % dimension, "", "| Value | Rows | Share |",
                      "|---|---:|---:|"])
        for row in subset:
            lines.append("| `%s` | %s | %.1f%% |" % (
                row["value"], row["count"], 100.0 * float(row["share_of_wave_c"])))
        lines.append("")
    lines.extend([
        "## Dependence-family status", "",
        "No exact copy-family identifier is currently available in the technical",
        "inputs. Repository and source taxonomy are retained for missingness cuts,",
        "but are not silently treated as dependence families. A dedicated frozen",
        "family manifest is required before Stage 9 inference.", "",
    ])
    return "\n".join(lines).encode("utf-8")


def render(eligibility_path=ELIGIBILITY, profiles_path=PROFILES,
           clusters_path=CLUSTERS):
    rows = build_rows(_read_csv(eligibility_path), _read_csv(profiles_path),
                      _read_csv(clusters_path))
    missingness = build_missingness(rows)
    inputs = [eligibility_path, profiles_path, clusters_path, PLAN, PREREGISTRATION]
    manifest = build_manifest(rows, inputs)
    return {
        OUTPUT: _csv_bytes(rows, CANDIDATE_FIELDS),
        MISSINGNESS: _csv_bytes(missingness, MISSINGNESS_FIELDS),
        MANIFEST: (json.dumps(manifest, ensure_ascii=False, indent=2,
                              sort_keys=True) + "\n").encode("utf-8"),
        REPORT: _report(rows, missingness, manifest),
    }, rows


def _write_atomic(path, content):
    tmp = path + ".tmp"
    with io.open(tmp, "wb") as handle:
        handle.write(content)
    os.replace(tmp, path)


def selftest():
    base = {"eligibility_status": "ineligible", "exclusion_reasons": "",
            "pending_reasons": "", "recursive_kind": ""}
    assert expansion_wave(dict(base, eligibility_status="eligible")) == "E0_strict67"
    assert expansion_wave(dict(base, eligibility_status="pending_diagnostics")) == \
        "A_pending_diagnostics"
    assert expansion_wave(dict(base, exclusion_reasons="recursive_bias_found",
                               recursive_kind="refused_no_warmup")) == \
        "B_warmup_refusal"
    assert expansion_wave(dict(base, exclusion_reasons=
                               "canonical_implementation_not_measured")) == \
        "C_measurement_recovery"
    assert expansion_wave(dict(base, exclusion_reasons="recursive_bias_found",
                               recursive_kind="drift_measured")) == \
        "D_recursive_drift"
    assert expansion_wave(dict(base, exclusion_reasons="lookahead_found")) == \
        "not_scheduled"
    print("eligibility_expansion selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    rendered, rows = render()
    if args.check:
        changed = [path for path, content in rendered.items()
                   if not os.path.exists(path) or io.open(path, "rb").read() != content]
        if changed:
            for path in changed:
                print("stale: %s" % os.path.relpath(path, ROOT))
            return 1
        print("eligibility expansion artifacts: current")
        return 0
    for path, content in rendered.items():
        _write_atomic(path, content)
    counts = collections.Counter(row["expansion_wave"] for row in rows)
    print("eligibility expansion rows: %d" % len(rows))
    for wave, count in sorted(counts.items()):
        print("  %-28s %d" % (wave, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
