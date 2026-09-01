# -*- coding: utf-8 -*-
"""Current status of every strategy, as an overlay on the frozen baseline.

`REGIME_ELIGIBILITY.csv` is E0 and is deliberately never regenerated: it is the
baseline every published figure is bound to. That means it cannot answer "what
do we know about this strategy today", and after four expansion waves the
answer lives scattered across the smoke, bias, adjudication and convergence
stores. This file collects them into one table without touching E0.

Nothing here decides anything. Admission happens in
`eligibility_expansion_adjudicate.py` and nowhere else; this is a reading of
what has already been decided, regenerated from the evidence files so it cannot
quietly go stale.
"""
from __future__ import annotations

import argparse
import collections
import csv
import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
ELIGIBILITY = os.path.join(ROOT, "REGIME_ELIGIBILITY.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
CANDIDATES = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_CANDIDATES.csv")
ADJUDICATION = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_ADJUDICATION.csv")
SMOKE = os.path.join(ROOT, "PROFILE_SMOKE.json")
BIAS = os.path.join(ROOT, "PROFILE_BIAS.json")
FULL_WINDOW = os.path.join(ROOT, "PROFILE_FULL_WINDOW.json")
CONVERGENCE = os.path.join(ROOT, "WARMUP_CONVERGENCE.json")
OUTPUT = os.path.join(ROOT, "STRATEGY_STATUS.csv")
REPORT = os.path.join(ROOT, "STRATEGY_STATUS.md")

FIELDS = [
    "strategy_id", "run_profile", "expansion_wave", "cohort", "measured",
    "observed_trades", "trade_evidence", "lookahead", "recursive",
    "recursive_evidence", "coverage_status", "traps_n", "artifact_role",
    "baseline_status", "baseline_exclusion_reasons", "open_work",
]


def _csv(path):
    if not os.path.exists(path):
        return []
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _json(path, key="results"):
    if not os.path.exists(path):
        return {}
    return json.load(io.open(path, encoding="utf-8")).get(key, {})


def _integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def rows():
    baseline = {r["strategy_id"]: r for r in _csv(ELIGIBILITY)}
    profiles = {r["strategy_id"]: r for r in _csv(PROFILES)}
    waves = {r["strategy_id"]: r for r in _csv(CANDIDATES)}
    admitted = {r["strategy_id"]: r for r in _csv(ADJUDICATION)
                if r["adjudication_status"] == "admitted_E1"}
    smoke = _json(SMOKE)
    bias = _json(BIAS)
    full = _json(FULL_WINDOW)
    convergence = _json(CONVERGENCE)

    out = []
    for strategy in sorted(profiles):
        profile = profiles[strategy]
        base = baseline.get(strategy, {})
        wave = waves.get(strategy, {}).get("expansion_wave", "")
        measurement = smoke.get(strategy) or {}
        window = full.get(strategy) or {}
        diagnostics = bias.get(strategy) or {}
        settled = convergence.get(strategy) or {}

        # Trade evidence, newest first: the pooled window outranks the smoke.
        trades, source = "", ""
        if window.get("status") == "measured":
            trades, source = window.get("trades", ""), "full_window"
        elif measurement.get("status") == "measured":
            trades, source = measurement.get("trades", ""), "smoke"
        elif base.get("canonical_measured") == "true":
            trades, source = base.get("canonical_observed_trades", ""), "baseline"

        lookahead = ((diagnostics.get("lookahead") or {}).get("status")
                     or base.get("lookahead") or "")
        recursive = ((diagnostics.get("recursive") or {}).get("status")
                     or base.get("recursive") or "")
        recursive_evidence = "native" if diagnostics.get("recursive") else "baseline"
        if settled.get("state") == "converged":
            recursive_evidence = "convergence:%s" % settled.get(
                "chosen_startup_candle_count")

        if strategy in admitted:
            cohort = ("E0_strict67" if base.get("regime_eligible") == "true"
                      else "E1_expanded")
        elif base.get("regime_eligible") == "true":
            cohort = "E0_strict67"
        elif settled.get("state") == "converged":
            cohort = "convergence_candidate"
        elif base.get("eligibility_status") == "pending_diagnostics":
            cohort = "pending"
        else:
            cohort = "excluded"

        open_work = []
        if cohort == "convergence_candidate":
            open_work.append("paired_full_window_equivalence")
            if lookahead not in ("PASS", "FOUND"):
                open_work.append("lookahead_verdict")
        elif cohort == "excluded" and settled.get("state") in (
                "not_converged_within_ladder", "inconclusive"):
            open_work.append("convergence_" + settled["state"])
        elif cohort == "excluded" and wave and not settled and not diagnostics:
            open_work.append("not_yet_revisited")

        out.append({
            "strategy_id": strategy,
            "run_profile": profile.get("run_profile", ""),
            "expansion_wave": wave,
            "cohort": cohort,
            "measured": "true" if (measurement.get("status") == "measured"
                                   or base.get("canonical_measured") == "true")
                        else "false",
            "observed_trades": trades,
            "trade_evidence": source,
            "lookahead": lookahead,
            "recursive": recursive,
            "recursive_evidence": recursive_evidence,
            "coverage_status": base.get("coverage_status", ""),
            "traps_n": base.get("traps_n", ""),
            "artifact_role": profile.get("artifact_role", ""),
            "baseline_status": base.get("eligibility_status", ""),
            "baseline_exclusion_reasons": base.get("exclusion_reasons", ""),
            "open_work": ";".join(open_work),
        })
    return out


def _csv_bytes(data):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return handle.getvalue().encode("utf-8")


def _table(counter, title, key_name):
    lines = ["| %s | Strategies |" % key_name, "|---|---:|"]
    for key, count in counter.most_common():
        lines.append("| `%s` | %d |" % (key or "(none)", count))
    return [title, ""] + lines + [""]


def _report(data):
    cohorts = collections.Counter(row["cohort"] for row in data)
    waves = collections.Counter(row["expansion_wave"] for row in data)
    work = collections.Counter(w for row in data
                               for w in row["open_work"].split(";") if w)
    measured = sum(1 for row in data if row["measured"] == "true")
    traded = sum(1 for row in data if _integer(row["observed_trades"]) > 0)
    lines = [
        "# Strategy status - current evidence for all %d rows" % len(data), "",
        "Generated by `strategy_status.py`. **This table decides nothing.**",
        "Admission happens only in `eligibility_expansion_adjudicate.py`; this",
        "is a reading of what has already been decided, collected from the",
        "smoke, bias, full-window, adjudication and convergence stores so that",
        "it cannot quietly go stale.", "",
        "`REGIME_ELIGIBILITY.csv` remains the frozen E0 baseline and is never",
        "regenerated. Where this table and E0 disagree, E0 is not wrong: it is",
        "the state at the freeze, and the difference is the expansion.", "",
        "## Measurement", "",
        "| | Strategies |", "|---|---:|",
        "| in the manifest | %d |" % len(data),
        "| measured at all | %d |" % measured,
        "| produced trades | %d |" % traded,
        "",
    ]
    lines += _table(cohorts, "## Cohort", "Cohort")
    lines += _table(waves, "## Expansion wave", "Wave")
    if work:
        lines += _table(work, "## Open work", "Item")
    lines += [
        "The row-level record is `STRATEGY_STATUS.csv`.", "",
    ]
    return "\n".join(lines).encode("utf-8")


def _write(path, content):
    tmp = path + ".tmp"
    with io.open(tmp, "wb") as handle:
        handle.write(content)
    os.replace(tmp, path)


def selftest():
    data = rows()
    assert len(data) == 900, len(data)
    assert len({row["strategy_id"] for row in data}) == 900
    baseline = {r["strategy_id"]: r for r in _csv(ELIGIBILITY)}
    # Every row the frozen baseline calls eligible must still read as E0 here.
    frozen = {s for s, r in baseline.items() if r["regime_eligible"] == "true"}
    assert len(frozen) == 67, len(frozen)
    listed = {row["strategy_id"] for row in data if row["cohort"] == "E0_strict67"}
    assert frozen == listed, sorted(frozen ^ listed)
    # Admitted rows are never silently folded into the baseline count.
    admitted = {r["strategy_id"] for r in _csv(ADJUDICATION)
                if r["adjudication_status"] == "admitted_E1"}
    assert admitted and not admitted & frozen
    assert {row["strategy_id"] for row in data
            if row["cohort"] == "E1_expanded"} == admitted
    print("strategy_status selftest: PASS (%d rows, %d E0, %d E1)"
          % (len(data), len(frozen), len(admitted)))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    data = rows()
    rendered = {OUTPUT: _csv_bytes(data), REPORT: _report(data)}
    if args.check:
        stale = [path for path, content in rendered.items()
                 if not os.path.exists(path)
                 or io.open(path, "rb").read() != content]
        for path in stale:
            print("stale: %s" % os.path.relpath(path, ROOT))
        if stale:
            return 1
        print("strategy status: current")
        return 0
    for path, content in rendered.items():
        _write(path, content)
    counts = collections.Counter(row["cohort"] for row in data)
    for cohort, count in counts.most_common():
        print("%s: %d" % (cohort, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
