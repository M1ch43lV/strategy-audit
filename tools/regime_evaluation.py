# -*- coding: utf-8 -*-
"""Stages 9-13 for Model 0: regime labels check, attribution, specialist evaluation, published pages.

    ./ftenv/Scripts/python.exe -m tools.regime_evaluation            # run the sequence
    ./ftenv/Scripts/python.exe -m tools.regime_evaluation --check    # is a rerun due?  exit 0 = current, 1 = stale

The serial pipeline dispatcher starts this once the per-strategy queue is empty and the input fingerprint changed
(`tools/pipeline_dispatcher.py`). It is orchestration only: every step is an existing program that owns its own
outputs, and nothing here changes a rule.

Model 1, Model 2 and Model 3 are outside it. Their gated backtests, attribution and comparison were paused by the
owner on 2026-09-21; the pages keep the immutable snapshots under `tools/regime_specialists_data/`. `STEPS` must not
name a gated program, and `run()` refuses if one ever does.

The window that matters for the spot runs is checked, not assumed: an owner-approved rerun over `20200301-...` of a spot
strategy is trimmed to the frozen spot window (`profile_full_window.TIMERANGE`) by `regime.attribution`.

A run writes `results/regime/regime_evaluation_state.json` with the fingerprint of its inputs. The fingerprint covers the
E1 cohort with the accepted archive of each member (digest and measurement scope), the regime labels, the execution
robustness and cost screen stores, and the source of the programs below, so a change to any of them makes the next
rerun due and a change to none of them does not.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "results" / "regime" / "regime_evaluation_state.json"
STATUS = ROOT / "STRATEGY_STATUS.csv"
MANIFEST = ROOT / "results" / "regime" / "full_backtest_manifest.json"
INPUT_FILES = (
    ROOT / "results" / "regime" / "regime_daily.csv",
    ROOT / "evidence" / "EXECUTION_ROBUSTNESS.json",
    ROOT / "evidence" / "COST_SCREEN.json",
)

# (module, what it is). Model 0 only.
STEPS = (
    ("regime.regime_engine", "Stage 9: regime labels from the analysis window start (2020-04-01)"),
    ("regime.validate_regime", "Stage 9: regime labels validate"),
    ("regime.report", "Stage 9: REGIME_DATA_REPORT.md"),
    ("regime.attribution", "Stage 10: Model 0 attribution of every accepted archive"),
    ("regime.specialist_evaluation", "Stage 13: specialist and universal evaluation"),
    ("regime.discovery_comparison", "Stage 13: discovery against validation, confirmation"),
    ("regime.daily_return", "Stage 13: daily return per phase"),
    ("regime.detail_totals", "Stage 13: 5m totals beside the author timeframe"),
    ("tools.regime_specialists_page", "Stage 13: the two published pages (Regime-Spezialisten, Gating-Hypothese)"),
)
GATED = ("gated_backtest", "gated_attribution", "model_compare")
CODE = tuple(ROOT / (module.replace(".", "/") + ".py") for module, _ in STEPS) + (
    Path(__file__),
    ROOT / "evidence" / "execution_robustness.py", ROOT / "evidence" / "profile_full_window.py",
    ROOT / "tools" / "REGIME_SPECIALISTS.template.html", ROOT / "tools" / "REGIME_GATING.template.html",
    ROOT / "tools" / "regime_pages_common.js", ROOT / "tools" / "regime_pages_common.css",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"


def fingerprint() -> str:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["results"]
    with io.open(STATUS, encoding="utf-8-sig", newline="") as handle:
        e1 = sorted(row["strategy_id"] for row in csv.DictReader(handle) if row["cohort"] == "E1_expanded")
    members = []
    for sid in e1:
        row = manifest.get(sid) or {}
        members.append([sid, row.get("status"), row.get("measurement_scope"), row.get("archive_sha256")])
    parts = {"e1": members, "inputs": [_sha(p) for p in INPUT_FILES], "code": [_sha(p) for p in CODE]}
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode("utf-8")).hexdigest()


def is_stale() -> tuple[bool, str]:
    if not STATE.is_file():
        return True, "no regime evaluation state"
    recorded = json.loads(STATE.read_text(encoding="utf-8")).get("fingerprint")
    changed = recorded != fingerprint()
    return changed, "input fingerprint changed" if changed else "current"


def run() -> int:
    for module, _ in STEPS:
        if any(name in module for name in GATED):
            raise SystemExit("refusing a gated Model 1/2/3 program: " + module)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    done = []
    for module, label in STEPS:
        print("== %s: %s" % (module, label), flush=True)
        completed = subprocess.run([sys.executable, "-m", module], cwd=ROOT, text=True, capture_output=True, check=False)
        tail = (completed.stdout + completed.stderr).strip().splitlines()[-4:]
        print("\n".join(tail), flush=True)
        if completed.returncode:
            print("regime evaluation stopped at %s (exit %d); no state written" % (module, completed.returncode), file=sys.stderr)
            return completed.returncode
        done.append(module)
    STATE.write_text(json.dumps({
        "started_at": started, "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "fingerprint": fingerprint(), "steps": done,
        "scope": "Model 0 only; Model 1/2/3 are owner-paused since 2026-09-21",
    }, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


def selftest() -> None:
    assert not any(any(name in module for name in GATED) for module, _ in STEPS)
    assert len({m for m, _ in STEPS}) == len(STEPS)
    for path in CODE:
        assert path.is_file(), path
    assert len(fingerprint()) == 64
    print("regime_evaluation selftest: PASS")


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in args:
        selftest()
        return 0
    if "--check" in args:
        stale, why = is_stale()
        print(("stale: " if stale else "") + why)
        return 1 if stale else 0
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
