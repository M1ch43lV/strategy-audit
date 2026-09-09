# -*- coding: utf-8 -*-
"""Build the published page from STRATEGY_STATUS.csv.

The page and the table have to say the same thing, and for a while they did
not: the page was assembled by hand from whatever the table happened to hold
that afternoon, so a correction to the table did not reach it. This puts one
command between them.

Field names are shortened on the way in. The page carries the full corpus and
every byte of key text is repeated per row; the mapping is right here, so nothing
is lost by it.
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
TABLE = os.path.join(ROOT, "STRATEGY_STATUS.csv")
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "STRATEGY_STATUS.template.html")

# short key -> column in STRATEGY_STATUS.csv
#
# rp/tf/ty/amr/amre/td/tde/te were dropped from an earlier version of this
# dict (Timeframe/Type/Phase/Duration silently went blank on the published
# page, and the repo origin was never on it at all) - restored 2026-09-08
# against an archived pre-regression copy of the page rather than guessed,
# and the template's render() needs every one of these keys back too.
FIELDS = {
    "s": "strategy_id",
    "c": "cohort",
    "w": "expansion_wave",
    "rp": "repo",
    "tf": "timeframe",
    "ty": "strategy_type",
    "amr": "assumed_market_regime",
    "amre": "assumed_market_regime_evidence",
    "t": "observed_trades",
    "te": "trade_evidence",
    "td": "test_duration_s",
    "tde": "test_duration_evidence",
    "l": "lookahead",
    "ls": "lookahead_evidence",
    "r": "recursive",
    "rs": "recursive_evidence",
    "n": "primary_reason",
    "f": "runtime_failure",
    "g": "evidence_gap",
    "d": "last_tested_at",
    "ds": "last_tested_source",
    "cs": "settled_startup",
    "cd": "settled_days",
    "md": "settled_drift_pct",
    "no": "needed_no_override",
    "kb": "cmd_backtest",
    "kl": "cmd_lookahead",
    "kr": "cmd_recursive",
    "o": "open_work",
    "xb": "exclusion_basis",
    "rv": "repair_verdict",
    "rf": "repair_family",
    "rs2": "repair_settings",
    "gn": "gate_notes",
}


def rows():
    with io.open(TABLE, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            # An empty value is dropped rather than shipped as "": the page
            # tests for presence everywhere, and a corpus of empty strings is
            # a quarter of the payload.
            yield {key: row[column] for key, column in FIELDS.items()
                   if row.get(column)}


def build(destination):
    template = io.open(TEMPLATE, encoding="utf-8").read()
    data = {"rows": list(rows())}
    generated = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")
    page = template.replace("__DATA__", json.dumps(data, ensure_ascii=False,
                                                   separators=(",", ":")))
    page = page.replace("__GEN__", generated[:16])
    # The row count used to be typed into the template by hand ("900") and
    # never got touched again after that - three build()s later the page
    # still said 900 while the table underneath had moved to 1038. Same
    # placeholder mechanism as __DATA__/__GEN__ so it can't happen again.
    page = page.replace("__TOTAL__", str(len(data["rows"])))
    with io.open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(page)
    return len(data["rows"]), os.path.getsize(destination)


def selftest():
    template = io.open(TEMPLATE, encoding="utf-8").read()
    assert "__DATA__" in template and "__GEN__" in template and "__TOTAL__" in template
    with io.open(TABLE, newline="", encoding="utf-8-sig") as handle:
        columns = set(next(csv.reader(handle)))
    missing = sorted(set(FIELDS.values()) - columns)
    assert not missing, "template asks for columns the table does not have: %s" \
        % ", ".join(missing)
    # Whatever the page renders as a verdict has to exist in the table, or the
    # page will quietly show a blank cell for a value nobody notices is gone.
    for key in ("l", "r", "n", "c"):
        assert FIELDS[key] in columns
    with io.open(TABLE, newline="", encoding="utf-8-sig") as handle:
        data = list(csv.DictReader(handle))
    missing_type = [row["strategy_id"] for row in data
                    if not row.get("strategy_type")]
    assert not missing_type, "blank strategy_type rows: %s" % ", ".join(missing_type)
    print("strategy_status_page selftest: PASS (%d fields)" % len(FIELDS))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(ROOT, "strategy_status.html"))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    count, size = build(args.out)
    print("built %s: %d rows, %.1f KB" % (args.out, count, size / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
