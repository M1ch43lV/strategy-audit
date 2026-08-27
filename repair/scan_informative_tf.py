# -*- coding: utf-8 -*-
"""scan_informative_tf - which timeframes do strategies request beyond their own?

The candle download covered the timeframe each strategy DECLARES. Strategies
also pull higher timeframes through `@informative('1d')` or by building
`informative_pairs()` by hand, and freqtrade needs those candles too. Where they
are missing the run dies with

    Informative dataframe for (BTC/USDT, 12h, spot) is empty.

which reads as a strategy problem and is a missing-data problem.

Scans the corpus for informative timeframe strings and reports which of them the
local candle store cannot serve. Regex, not AST: these appear as decorator
arguments and as string literals inside `informative_pairs()` list building, and
a decorator scan alone would miss the hand-built ones.
"""
import collections
import csv
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT

TF_TOKEN = r"(?:[1-9]\d*(?:m|h|d|w|M))"
RX_INFORMATIVE_DEC = re.compile(r"@informative\(\s*['\"](%s)['\"]" % TF_TOKEN)
RX_INF_PAIRS = re.compile(
    r"informative_pairs|inf_timeframe|informative_timeframe", re.I)
RX_TF_LITERAL = re.compile(r"['\"](%s)['\"]" % TF_TOKEN)


def have():
    out = set()
    for f in glob.glob(os.path.join(AUD, "user_data", "data", "binance", "*.feather")):
        out.add(os.path.basename(f).replace(".feather", "").rsplit("-", 1)[1])
    return out


def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AUD, "LEDGER.csv")
    present = have()
    wanted = collections.Counter()
    who = collections.defaultdict(set)
    for r in csv.DictReader(io.open(ledger, encoding="utf-8")):
        p = os.path.join(AUD, r["file"])
        if not os.path.exists(p):
            continue
        src = io.open(p, encoding="utf-8", errors="replace").read()
        tfs = set(RX_INFORMATIVE_DEC.findall(src))
        # hand-built informative_pairs: take timeframe literals from those lines
        if RX_INF_PAIRS.search(src):
            for line in src.splitlines():
                if RX_INF_PAIRS.search(line) or "inf_tf" in line:
                    tfs.update(RX_TF_LITERAL.findall(line))
        for tf in tfs:
            wanted[tf] += 1
            who[tf].add(r["strategy"])

    print("informative timeframes requested across the corpus:")
    print("  %-6s %6s  %s" % ("tf", "count", "candles present?"))
    missing = []
    for tf, n in sorted(wanted.items(), key=lambda kv: -kv[1]):
        ok = tf in present
        if not ok:
            missing.append((tf, n))
        print("  %-6s %6d  %s" % (tf, n, "yes" if ok else "NO"))
    print()
    if missing:
        print("missing, and how many strategies want them:")
        for tf, n in missing:
            print("  %-6s %4d strategies" % (tf, n))
        print()
        print("download list:", " ".join(tf for tf, _ in missing))
    else:
        print("every requested informative timeframe is available locally")


if __name__ == "__main__":
    main()
