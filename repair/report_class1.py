# -*- coding: utf-8 -*-
"""report_class1 - summarise the Class 1 re-measurement.

Answers the question the whole exercise exists for: of the strategies the audit
could not measure, how many produce a result once the environment is repaired -
and do those results look different from the ones the audit did measure?

Deliberately reports three separate things and never merges them:

  * how far each strategy got (both windows, one window, none)
  * why the ones that failed, failed - grouped by cause and by WHOSE cause it is
  * for the ones that produced numbers, the same figures the audit's ledger
    carries, so the two populations can be compared directly

"NOT-APPLICABLE" is never counted as a pass. That is the audit author's own rule
and the reason his funnel is trustworthy where it is; adopting it here keeps the
two runs comparable.
"""
import collections
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS = os.path.join(ROOT, "repair", "results_class1")


def whose_fault(why):
    """Attribute a failure to the test rig or to the strategy.

    The split matters: a strategy that cannot run because the harness is spot-only
    says nothing about the strategy, while a KeyError in its own indicator code
    says everything.
    """
    w = str(why)
    if "Short strategies cannot run in spot" in w:
        return "rig: spot-only config"
    if "freqAI is not enabled" in w:
        return "rig: FreqAI not enabled"
    if "No data found" in w:
        return "rig: missing candles"
    if "TIMED OUT" in w:
        return "rig: time limit"
    if "API key" in w or "api key" in w:
        return "strategy: needs external service"
    if "parameter space" in w:
        return "strategy: hyperopt parameter without space"
    if "no summary" in w:
        return "strategy: ran, produced no trades"
    if "DTypePromotion" in w or "dtype" in w:
        return "strategy: pandas/numpy 2 break"
    if any(k in w for k in ("Error", "Exception")):
        return "strategy: runtime error in its own code"
    return "other"


def main():
    files = sorted(glob.glob(os.path.join(CARDS, "*.json")))
    cards = []
    for f in files:
        try:
            cards.append(json.load(io.open(f, encoding="utf-8")))
        except Exception:
            pass
    if not cards:
        print("no cards yet")
        return

    both, is_only, none_ = [], [], []
    for c in cards:
        i = c["runs"]["in_sample"]["level"]
        o = (c["runs"].get("out_sample") or {}).get("level")
        if i == "PASSED" and o == "PASSED":
            both.append(c)
        elif i == "PASSED":
            is_only.append(c)
        else:
            none_.append(c)

    print("cards so far: %d" % len(cards))
    print("  both windows measured : %d" % len(both))
    print("  in-sample only        : %d" % len(is_only))
    print("  produced nothing      : %d" % len(none_))

    print("\nwhy the %d produced nothing, by whose cause it is:" % len(none_))
    c = collections.Counter(whose_fault(x["runs"]["in_sample"].get("why")) for x in none_)
    rig = sum(v for k, v in c.items() if k.startswith("rig"))
    strat = sum(v for k, v in c.items() if k.startswith("strategy"))
    for k, v in c.most_common():
        print("  %4d  %s" % (v, k))
    print("  ----")
    print("  %4d  test rig" % rig)
    print("  %4d  strategy itself" % strat)

    if both:
        print("\nstrategies that produced numbers in both windows:")
        print("  %-30s %5s %8s %10s %10s %10s" %
              ("strategy", "tf", "trades", "OOS %", "market %", "beats BH"))
        beats = 0
        for x in sorted(both, key=lambda z: -( (z["runs"]["out_sample"]["summary"] or {}).get("total_pct") or -1e9)):
            s = x["runs"]["out_sample"]["summary"] or {}
            tot, mkt = s.get("total_pct"), s.get("market_change_pct")
            bh = (tot is not None and mkt is not None and tot > mkt)
            beats += bool(bh)
            print("  %-30s %5s %8s %10s %10s %10s" % (
                x["strategy"][:30], x.get("declared_timeframe"), s.get("trades"),
                tot, mkt, "YES" if bh else "no"))
        print("\n  beat buy-and-hold out of sample: %d of %d" % (beats, len(both)))
        print("  (raw comparison only - the audit's ladder applies further gates,")
        print("   and the strategy return compounds while Market change does not)")


if __name__ == "__main__":
    main()
