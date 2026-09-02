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
BIAS = os.path.join(ROOT, "PROFILE_BIAS.json")
RULE = "no_variance_is_a_pass_v1"
BIAS_RULE = "current_reader_v1"
BLIND_RULE = "undefined_column_is_not_a_finding_v1"


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


def blind_candidates(store, threshold):
    """Ladder records the current reader now settles, and why they did not.

    The fourth reader correction. An indicator the analyzer could not put a
    number on at ANY rung is not a strategy that fails to settle - more warm-up
    was never going to give that column a value. Until now such a column made
    convergence unreachable for its whole strategy, whatever every other
    indicator did, and the record came out as a recursion finding.

    Only records that flip are returned, and only where the log survives to be
    read again. A record whose other indicators genuinely stay out of band
    keeps its finding: setting the blind column aside changes nothing for it.
    """
    found = []
    for strategy, record in sorted(store.items()):
        if record.get("state") != "not_converged_within_ladder":
            continue
        output = _output(record)
        if output is None:
            continue
        blind = profile_bias.undefined_throughout(output)
        if not blind:
            continue
        settled = profile_bias.settled_startup(output, threshold)
        if settled is None:
            continue
        found.append((strategy, record, blind, settled))
    return found


def apply_blind(store, threshold, dry_run):
    changed = []
    for strategy, record, blind, settled in blind_candidates(store, threshold):
        startup, indicator, value = settled
        before = record.get("state")
        if not dry_run:
            rung_days = record.get("ladder_days") or []
            rung_candles = record.get("ladder_candles") or []
            record["state"] = "converged"
            record["chosen_startup_candle_count"] = startup
            record["chosen_ladder_days"] = next(
                (day for day, candles in zip(rung_days, rung_candles)
                 if candles == startup), None)
            record["max_drift_pct"] = abs(value)
            record["max_drift_indicator"] = indicator
            record["undefined_throughout"] = blind
            record["why"] = (
                "settles at %d candles once %s is set aside; the analyzer "
                "reported nan%% for it at every rung, so no warm-up could ever "
                "have given it a value" % (startup, ", ".join(blind)))
            record["reparsed_from_log"] = BLIND_RULE
        changed.append((strategy, before, startup, blind))
    return changed


def bias_candidates(store):
    """Recursion records whose log the current reader disagrees with.

    The convergence store was re-read when the column bug was found; this one
    never was, so the table still shows verdicts produced by the reader that
    took the first numeric column instead of the strategy's own. Where the log
    survives it can simply be read again. Where it does not, the old verdict
    stands and is marked, because an unverifiable record is not the same thing
    as a checked one.
    """
    found = []
    for strategy, record in sorted(store.items()):
        gate = record.get("recursive") or {}
        if not gate.get("status"):
            continue
        path = gate.get("debug_log")
        full = (path if path and os.path.isabs(path)
                else os.path.join(ROOT, path) if path else None)
        if not full or not os.path.exists(full):
            continue
        output = io.open(full, encoding="utf-8", errors="replace").read()
        status, why = profile_bias._recursive(output, gate.get("returncode", 0) or 0)
        if status != gate["status"] or why != gate.get("why"):
            found.append((strategy, gate, status, why))
    return found


def apply_bias(store, dry_run):
    changed = []
    for strategy, gate, status, why in bias_candidates(store):
        changed.append((strategy, gate["status"], status, why))
        if dry_run:
            continue
        gate["superseded_status"] = gate["status"]
        gate["superseded_why"] = gate.get("why")
        gate["status"] = status
        gate["why"] = why
        gate["reparsed_from_log"] = BIAS_RULE
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
    # A record re-parsed under the blind rule must name the column it set
    # aside, and that column must really be unreadable at every rung in its
    # own log. Otherwise the rule would be a way of ignoring inconvenient
    # numbers rather than a way of ignoring absent ones.
    threshold = _load(CONVERGENCE).get("drift_threshold_pct", 1.0)
    for strategy, record in store.items():
        if record.get("reparsed_from_log") != BLIND_RULE:
            continue
        output = _output(record)
        assert output is not None, strategy
        blind = profile_bias.undefined_throughout(output)
        assert blind, strategy
        assert record.get("undefined_throughout") == blind, strategy
        assert record["state"] == "converged", strategy
        settled = profile_bias.settled_startup(output, threshold)
        assert settled is not None, strategy
        assert record["chosen_startup_candle_count"] == settled[0], strategy
    blind_done = sum(1 for r in store.values()
                     if r.get("reparsed_from_log") == BLIND_RULE)
    blind_left = len(blind_candidates(store, threshold))
    # Every re-parsed bias verdict must be exactly what the log now says, and
    # what it replaced must still be on the record.
    bias = _load(BIAS)["results"]
    for strategy, gate, status, _why in bias_candidates(bias):
        assert gate.get("reparsed_from_log") != BIAS_RULE,             "%s: re-parsed record still disagrees with its log (%s)" % (
                strategy, status)
    for strategy, record in bias.items():
        gate = record.get("recursive") or {}
        if gate.get("reparsed_from_log") == BIAS_RULE:
            assert "superseded_status" in gate, strategy
    bias_done = sum(1 for r in bias.values()
                    if (r.get("recursive") or {}).get("reparsed_from_log")
                    == BIAS_RULE)
    print("warmup_reparse selftest: PASS (%d ladder re-parsed, %d still to "
          "read; %d bias re-parsed, %d still to read; %d blind re-parsed, "
          "%d still to read)"
          % (reparsed, remaining, bias_done, len(bias_candidates(bias)),
             blind_done, blind_left))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="write the corrected verdicts back")
    parser.add_argument("--store", default="ladder",
                        choices=("ladder", "bias", "blind"))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.store == "bias":
        data = _load(BIAS)
        changed = apply_bias(data["results"], not args.apply)
        counts = collections.Counter((before, after)
                                     for _s, before, after, _w in changed)
        print("%s %d recursion verdicts read again: %s"
              % ("rewrote" if args.apply else "would rewrite", len(changed),
                 ", ".join("%s->%s=%d" % (b, a, n)
                           for (b, a), n in counts.most_common()) or "-"))
        for strategy, before, after, why in changed:
            print("   %-34s %-6s -> %-6s %s" % (strategy, before, after, why[:60]))
        if args.apply and changed:
            _write(BIAS, data)
        return 0
    if args.store == "blind":
        data = _load(CONVERGENCE)
        threshold = data.get("drift_threshold_pct", 1.0)
        changed = apply_blind(data["results"], threshold, not args.apply)
        print("%s %d records that only an unreadable column held back"
              % ("rewrote" if args.apply else "would rewrite", len(changed)))
        for strategy, before, startup, blind in changed:
            print("   %-34s %-26s -> converged at %d candles, set aside %s"
                  % (strategy, before, startup, ", ".join(blind)))
        if args.apply and changed:
            _write(CONVERGENCE, data)
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
