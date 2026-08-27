# -*- coding: utf-8 -*-
"""scan_market_orders - how many strategies the spot config's price_side excludes.

freqtrade 2026.7 refuses to start when a strategy asks for market ENTRY orders
while `entry_pricing.price_side` is `"same"`:

    Market entry orders require entry_pricing.price_side = "other".

The audit's config sets `"same"` for entry and exit. A strategy hitting this
never processes a candle, and its card reads "could not be measured" - true, but
it reads as a property of the strategy when it is a property of the config.

METHOD. This script does not guess from source text. Two earlier attempts did,
and both produced counts that the ledger contradicted: matching any `"market"`
order type gave 224 strategies of which the audit had measured 150, and
narrowing to entry/exit still left 51 measured. A count the ledger contradicts
is a broken count, not a finding.

So the population is taken from the cards that ACTUALLY failed with this
message, and the source scan is used only to describe them - never to define
them.
"""
import collections
import csv
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT
CARDS = os.path.join(ROOT, "repair", "results_class1")

RX_MSG = re.compile(r"Market (entry|exit) orders require", re.I)
RX_ENTRY_MARKET = re.compile(r"""["'](?:entry|buy)["']\s*:\s*["']market["']""")
RX_EXIT_MARKET = re.compile(r"""["'](?:exit|sell)["']\s*:\s*["']market["']""")


def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AUD, "LEDGER.csv")
    led = {r["strategy"]: r for r in csv.DictReader(io.open(ledger, encoding="utf-8"))}

    blocked = []
    for f in glob.glob(os.path.join(CARDS, "*.json")):
        try:
            c = json.load(io.open(f, encoding="utf-8"))
        except Exception:
            continue
        why = str(c["runs"]["in_sample"].get("why", ""))
        if RX_MSG.search(why):
            blocked.append(c["strategy"])

    print("cards measured so far that fail on price_side: %d" % len(blocked))
    if not blocked:
        return

    kinds = collections.Counter()
    for name in blocked:
        r = led.get(name)
        if not r:
            continue
        p = os.path.join(AUD, r["file"])
        if not os.path.exists(p):
            continue
        src = io.open(p, encoding="utf-8", errors="replace").read()
        kinds["entry market order" if RX_ENTRY_MARKET.search(src) else
              "exit market order" if RX_EXIT_MARKET.search(src) else
              "neither pattern found in source"] += 1
    print("what those blocked strategies declare:")
    for k, v in kinds.most_common():
        print("  %4d  %s" % (v, k))

    print()
    print("blocked so far:", ", ".join(sorted(blocked)[:20]))
    print()
    print("This is a lower bound: the Class 1 run is still in progress, and it")
    print("covers only the strategies the audit never measured. The count for the")
    print("full corpus is not known until every card exists.")


if __name__ == "__main__":
    main()
