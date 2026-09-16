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
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evidence import exclusion_criteria


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "STRATEGY_STATUS.csv")
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "STRATEGY_STATUS.template.html")
# regime/full_backtest.py's pooled, all-eight-pairs-together run - PIPELINE.md
# Stage 7. Deliberately not read by evidence/strategy_status.py: its own
# docstring says a pooled result must never feed admission back (the pooled
# run answers a different question, for Stage 9, from the paired per-pair
# `evidence/PROFILE_FULL_WINDOW.json` Stage-6 gate that does feed it). That
# boundary is about STRATEGY_STATUS.csv and the cohort it decides - reading
# the pooled manifest here, for the page's own Trades column only, doesn't
# cross it: nothing here changes a cohort, only what the reader is shown for
# a row already admitted on other evidence.
POOLED_BACKTEST = os.path.join(ROOT, "results/regime/full_backtest_manifest.json")

_NUMBER_WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
                 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
                 11: "Eleven", 12: "Twelve"}


def _spelled(n):
    return _NUMBER_WORDS.get(n, str(n))


def _inline(text):
    """`evidence/exclusion_criteria.py`'s prose, as the HTML it was always
    meant to become. Escaped first so a literal `&`/`<`/`>` in a criterion's
    text can never be read as markup, then only backtick code spans are
    converted - the one inline construct every `CRITERIA["what"]` entry
    actually uses (checked: none currently carries `**bold**` either, but a
    future one might, so bold is deliberately left unconverted rather than
    silently wrong)."""
    escaped = (text.replace("&", "&amp;").replace("<", "&lt;")
                   .replace(">", "&gt;"))
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def _criteria_cards():
    """The exclusion-criteria legend, from the one place the criteria are
    defined. Built by hand in the template until 2026-09-09, when it still
    read C1-C3 four criteria after C4 was added - the count and the cards
    were never the same list."""
    cards = []
    for criterion in exclusion_criteria.CRITERIA:
        cards.append(
            "      <div>\n        <h3>%s &middot; %s</h3>\n"
            "        <p class=\"lead\">%s</p>\n      </div>"
            % (criterion["id"], _inline(criterion["name"]),
               _inline(criterion["what"])))
    return "\n".join(cards)

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


POOLED_RETIRED = ("failed", "resource_inconclusive", "timeout",
                  "performance_limited", "oom_confirmed", "stake_overflow_confirmed")


def pooled_results():
    if not os.path.exists(POOLED_BACKTEST):
        return {}
    return json.load(io.open(POOLED_BACKTEST, encoding="utf-8")).get("results", {})


def pooled_trades(results):
    """strategy_id -> pooled trade count, for rows the pooled run measured.

    Only `status == "measured"` counts. Every other listed terminal status is
    a non-testable result, not a trade count.
    """
    return {strategy: record["trades"] for strategy, record in results.items()
            if record.get("status") == "measured"}


def pooled_retired(results):
    """strategy_id -> True for rows confirmed not testable under this
    benchmark's fixed conditions by regime/full_backtest.py (see
    evidence/POOLED_BACKTEST_PERFORMANCE_LIMIT.json /
    evidence/POOLED_BACKTEST_OOM_LIMIT.json / _STAKE_OVERFLOW.json).

    The owner added `failed`, `resource_inconclusive`, and `timeout` on
    2026-09-10: they are final non-testable outcomes for this benchmark.
    """
    return {strategy for strategy, record in results.items()
            if record.get("status") in POOLED_RETIRED}


def rows():
    pooled = pooled_results()
    trades = pooled_trades(pooled)
    retired = pooled_retired(pooled)
    with io.open(TABLE, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            # An empty value is dropped rather than shipped as "": the page
            # tests for presence everywhere, and a corpus of empty strings is
            # a quarter of the payload.
            out = {key: row[column] for key, column in FIELDS.items()
                   if row.get(column)}
            strategy = row["strategy_id"]
            if strategy in trades:
                out["pft"] = trades[strategy]
            if strategy in retired:
                out["pfr"] = True
            yield out


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
    page = page.replace("__CRITERIA__", _criteria_cards())
    page = page.replace("__CRITERIA_COUNT__",
                        _spelled(len(exclusion_criteria.CRITERIA)))
    page = page.replace("__NOT_CRITERIA_COUNT__",
                        _spelled(len(exclusion_criteria.NOT_CRITERIA)))
    # Same hand-typed-number bug as __TOTAL__, one footer line lower: the
    # footer still claimed 588 native look-ahead rows and a 2026-09-02
    # snapshot long after both moved.
    page = page.replace("__LOOKAHEAD_NATIVE__",
                        str(sum(1 for row in data["rows"] if row.get("ls") == "native")))
    page = page.replace("__WARMUP_SETTLED__",
                        str(sum(1 for row in data["rows"] if row.get("cs"))))
    with io.open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(page)
    return len(data["rows"]), os.path.getsize(destination)


def selftest():
    template = io.open(TEMPLATE, encoding="utf-8").read()
    assert "__DATA__" in template and "__GEN__" in template and "__TOTAL__" in template
    assert "__CRITERIA__" in template and "__CRITERIA_COUNT__" in template \
        and "__NOT_CRITERIA_COUNT__" in template
    assert "__LOOKAHEAD_NATIVE__" in template and "__WARMUP_SETTLED__" in template
    # The legend has to show every criterion that can actually exclude a row,
    # or the page understates what "excluded" means - which is exactly the
    # bug this replaced (three cards typed by hand, six criteria added since
    # and never added to the page).
    cards = _criteria_cards()
    for criterion in exclusion_criteria.CRITERIA:
        assert criterion["id"] in cards, \
            "legend is missing %s" % criterion["id"]
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
    pooled_all = pooled_results()
    pooled = pooled_trades(pooled_all)
    assert pooled, "no measured rows in %s - has the pooled run moved?" \
        % os.path.basename(POOLED_BACKTEST)
    for trades in pooled.values():
        assert isinstance(trades, int) and trades >= 0, trades
    retired = pooled_retired(pooled_all)
    assert not (retired & set(pooled)), \
        "rows both measured and retired in the pooled run: %s" \
        % ", ".join(sorted(retired & set(pooled)))
    print("strategy_status_page selftest: PASS (%d fields, %d pooled trade "
          "counts, %d pooled-retired)" % (len(FIELDS), len(pooled), len(retired)))


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
