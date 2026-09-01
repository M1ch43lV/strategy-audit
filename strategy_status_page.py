# -*- coding: utf-8 -*-
"""Build the published page from STRATEGY_STATUS.csv.

The page and the table have to say the same thing, and for a while they did
not: the page was assembled by hand from whatever the table happened to hold
that afternoon, so a correction to the table did not reach it. This puts one
command between them.

Field names are shortened on the way in. The page carries 900 rows and every
byte of key text is paid for 900 times; the mapping is right here, so nothing
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


ROOT = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(ROOT, "STRATEGY_STATUS.csv")
TEMPLATE = os.path.join(ROOT, "STRATEGY_STATUS.template.html")

# short key -> column in STRATEGY_STATUS.csv
FIELDS = {
    "s": "strategy_id",
    "c": "cohort",
    "w": "expansion_wave",
    "t": "observed_trades",
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
}


def rows():
    with io.open(TABLE, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            # An empty value is dropped rather than shipped as "": the page
            # tests for presence everywhere, and 900 rows of empty strings is
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
    with io.open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(page)
    return len(data["rows"]), os.path.getsize(destination)


def selftest():
    template = io.open(TEMPLATE, encoding="utf-8").read()
    assert "__DATA__" in template and "__GEN__" in template
    with io.open(TABLE, newline="", encoding="utf-8-sig") as handle:
        columns = set(next(csv.reader(handle)))
    missing = sorted(set(FIELDS.values()) - columns)
    assert not missing, "template asks for columns the table does not have: %s" \
        % ", ".join(missing)
    # Whatever the page renders as a verdict has to exist in the table, or the
    # page will quietly show a blank cell for a value nobody notices is gone.
    for key in ("l", "r", "n", "c"):
        assert FIELDS[key] in columns
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
