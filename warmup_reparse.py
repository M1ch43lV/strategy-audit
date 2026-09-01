# -*- coding: utf-8 -*-
"""Re-read stored ladder logs with the current parser.

Every correction to the drift-table reader so far has been a correction to the
reader, not to the runs: the analyzer's output was right and complete, and we
took the wrong thing from it. Where the log survives, the honest and cheap
repair is to read it again rather than spend an hour of freqtrade time
reproducing output we already have on disk.

The rule this tool exists for is the third such correction. `analyze_indicators`
walks the rungs in ascending order and stops at the first one whose last row
matches the full-history run exactly, logging

    No variance on indicator(s) found due to recursive formula.

and printing no table at all. Reading "no table" as "nothing was compared" was
right for the undefined-cell case and wrong for this one; it turned the
strongest available pass into a non-verdict for 17 rows, three of which were
sitting in the excluded list under a reason that says, in as many words, that
the record was made under a parser defect.

A re-parse only ever replaces a verdict with what the same output actually
says. It records `reparsed_from_log` so nothing here can later be mistaken for
a fresh run: the timestamp still belongs to the original run, not to today.

One thing this rule takes on trust, and it should be said plainly. The break
means only the smallest rung was ever compared, so the larger rungs carry no
measurement - the usual settling rule, which asks that a rung and every larger
rung stay in band, cannot be checked here. The reference both are compared
against is the full-history run, and a rung that already reproduces it exactly
cannot be improved on by more warm-up. That is freqtrade's own reasoning for
stopping, and it is why the row is recorded at zero drift rather than at "not
measured above this rung".
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import sys

import profile_bias


ROOT = os.path.dirname(os.path.abspath(__file__))
CONVERGENCE = os.path.join(ROOT, "WARMUP_CONVERGENCE.json")
RULE = "no_variance_is_a_pass_v1"


def _load(path):
    return json.load(io.open(path, encoding="utf-8"))


def _write(path, data):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def _output(record):
    path = record.get("debug_log")
    if not path:
        return None
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    return io.open(full, encoding="utf-8", errors="replace").read()


def candidates(store):
    """Records whose verdict the current parser would not have produced.

    Restricted to the one shape this correction is about. A record that already
    carries a table was read from the table and is not revisited here; a record
    with no log cannot be re-read at all and stays as it is.
    """
    found = []
    for strategy, record in sorted(store.items()):
        if record.get("why") != "analyzer produced no drift table":
            continue
        output = _output(record)
        if output is None:
            continue
        if profile_bias.NO_VARIANCE in output:
            found.append((strategy, record, output))
    return found


def apply(store, dry_run):
    changed = []
    for strategy, record, _output in candidates(store):
        rung_candles = record.get("ladder_candles") or []
        rung_days = record.get("ladder_days") or []
        if not rung_candles:
            continue
        before = record.get("state")
        if not dry_run:
            record["state"] = "converged"
            record["chosen_startup_candle_count"] = rung_candles[0]
            record["chosen_ladder_days"] = rung_days[0] if rung_days else None
            record["max_drift_pct"] = 0.0
            record["max_drift_indicator"] = None
            record["needed_no_override"] = (
                record.get("declared_warmup_override") is None)
            record["why"] = ("analyzer reports no variance at the smallest "
                             "rung; it compared and stopped there")
            # The run is the original one. Only the reading is new.
            record["reparsed_from_log"] = RULE
        changed.append((strategy, before, rung_candles[0]))
    return changed


def selftest():
    store = _load(CONVERGENCE)["results"]
    # Nothing may be re-parsed into a pass without the analyzer's own sentence
    # in the log. That sentence is the entire evidence for this rule.
    for strategy, record in store.items():
        if record.get("reparsed_from_log") != RULE:
            continue
        output = _output(record)
        assert output is not None, strategy
        assert profile_bias.NO_VARIANCE in output, strategy
        assert record["state"] == "converged", strategy
        assert record["max_drift_pct"] == 0.0, strategy
    reparsed = sum(1 for r in store.values()
                   if r.get("reparsed_from_log") == RULE)
    remaining = len(candidates(store))
    print("warmup_reparse selftest: PASS (%d re-parsed, %d still to read)"
          % (reparsed, remaining))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="write the corrected verdicts back")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    data = _load(CONVERGENCE)
    changed = apply(data["results"], not args.apply)
    states = collections.Counter(before for _s, before, _c in changed)
    print("%s %d records read again: %s"
          % ("rewrote" if args.apply else "would rewrite", len(changed),
             ", ".join("%s=%d" % kv for kv in states.most_common()) or "-"))
    for strategy, before, startup in changed:
        print("   %-30s %-14s -> converged at %d candles"
              % (strategy, before, startup))
    if args.apply and changed:
        _write(CONVERGENCE, data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
