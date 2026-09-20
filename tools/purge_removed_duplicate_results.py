# -*- coding: utf-8 -*-
"""Take the measurement records of removed duplicates out of the result stores.

`tools/harvest.py` deletes a freshly downloaded duplicate and logs it in
`evidence/REMOVED_DUPLICATE_SOURCES.json`, but the results the duplicate had already
produced stayed behind in the stores the runners write (the pooled manifest, the
full-window shards, the warm-up ladder, the trial run, the look-ahead backfill, the OOM
confirmations). Everything derived from them then counted it as a strategy of its
own: a duplicate of NostalgiaForInfinityV7 took a row in the specialist rankings.

The records are written to `evidence/REMOVED_DUPLICATE_RESULTS.json` first, verbatim,
and only then removed, so what was measured stays on record. The run archives under
`user_data/` are not touched.

Derived files (`regime.attribution`, the specialist evaluation, the robustness stores,
the status table) are not edited here; regenerate them afterwards.

    ./ftenv/Scripts/python.exe -m tools.purge_removed_duplicate_results --dry-run
    ./ftenv/Scripts/python.exe -m tools.purge_removed_duplicate_results
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOVED = os.path.join(ROOT, "evidence", "REMOVED_DUPLICATE_SOURCES.json")
LOG = os.path.join(ROOT, "evidence", "REMOVED_DUPLICATE_RESULTS.json")
TABLE = os.path.join(ROOT, "STRATEGY_STATUS.csv")

# Mappings inside a store that are keyed by strategy id: the record itself and, for the
# warm-up ladder, the attempts it replaced.
SECTIONS = ("results", "superseded")

# Stores whose `results` mapping is keyed by strategy id and written by a runner.
# The decision documents (ELIGIBILITY_EXPANSION_*, REGIME_ELIGIBILITY.csv) are a record
# of what was decided at the time and stay as they are.
STORES = [
    "results/regime/full_backtest_manifest.json",
    "evidence/PROFILE_FULL_WINDOW_shardA.json",
    "evidence/PROFILE_FULL_WINDOW_shardB.json",
    "evidence/WARMUP_CONVERGENCE.json",
    "evidence/PROFILE_SMOKE.json",
    "evidence/ELIGIBILITY_LOOKAHEAD_BACKFILL.json",
    "evidence/POOLED_BACKTEST_OOM_LIMIT.json",
]


def _load(path):
    with io.open(path, encoding="utf-8", newline="") as handle:
        return handle.read()


def _dump(data, style):
    text = json.dumps(data, indent=2, sort_keys=style["sort_keys"],
                      ensure_ascii=style["ensure_ascii"])
    return text + ("\n" if style["newline"] else "")


def _style(text):
    """The way a store is written, found by writing it back and comparing."""
    data = json.loads(text)
    for sort_keys in (True, False):
        for ensure_ascii in (True, False):
            for newline in (True, False):
                style = {"sort_keys": sort_keys, "ensure_ascii": ensure_ascii,
                         "newline": newline}
                if _dump(data, style) == text.replace("\r\n", "\n"):
                    return style
    return None


def purge_ids():
    """Removed at intake, not recovered since, and not in the status table."""
    with io.open(REMOVED, encoding="utf-8") as handle:
        removed = json.load(handle)["removed"]
    with io.open(TABLE, newline="", encoding="utf-8-sig") as handle:
        table = {row["strategy_id"] for row in csv.DictReader(handle)}
    return {row["strategy_id"]: row for row in removed
            if not row.get("recovered_at") and row["strategy_id"] not in table}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    ids = purge_ids()
    plan, kept = {}, {}
    for store in STORES:
        path = os.path.join(ROOT, store)
        text = _load(path)
        data = json.loads(text)
        style = _style(text)
        hits = sorted({s for section in SECTIONS for s in ids
                       if s in (data.get(section) or {})})
        plan[store] = (data, style, hits, "\r\n" in text)
        for strategy in hits:
            for section in SECTIONS:
                if strategy in (data.get(section) or {}):
                    kept.setdefault(strategy, {})[store + "#" + section] = data[section][strategy]
        if hits and style is None:
            raise SystemExit("cannot reproduce the layout of %s; not touching it" % store)
    for store, (_, _, hits, _) in plan.items():
        print("%-52s %s" % (store, ", ".join(hits) or "-"))
    if args.dry_run or not kept:
        return 0

    # Log first. An entry that is already there is not overwritten.
    log = {"schema_version": 1, "entries": {}}
    if os.path.exists(LOG):
        log = json.loads(_load(LOG))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    for strategy, records in sorted(kept.items()):
        entry = log["entries"].setdefault(strategy, {
            "canonical_representative": ids[strategy].get("canonical_representative"),
            "evidence_rule": ids[strategy].get("evidence_rule"),
            "removed_at": ids[strategy].get("removed_at"),
            "purged_at": now, "records": {}})
        for store, record in records.items():
            entry["records"].setdefault(store, record)
    with io.open(LOG, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(log, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print("logged %d strategies in %s" % (len(kept), os.path.relpath(LOG, ROOT)))

    for store, (data, style, hits, crlf) in plan.items():
        if not hits:
            continue
        for strategy in hits:
            for section in SECTIONS:
                (data.get(section) or {}).pop(strategy, None)
        if "runtime_ids" in data:
            data["runtime_ids"] = sorted({
                result.get("runtime_id", "native_unversioned")
                for result in data["results"].values() if result.get("status") == "measured"})
        text = _dump(data, style)
        if crlf:
            text = text.replace("\n", "\r\n")
        with io.open(os.path.join(ROOT, store), "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        print("removed %d from %s" % (len(hits), store))
    return 0


if __name__ == "__main__":
    sys.exit(main())
