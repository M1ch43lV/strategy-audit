# -*- coding: utf-8 -*-
"""verify_futures - check the futures store before anything is measured on it.

The first futures download was killed mid-flight by an IP ban, so some files on
disk are partial. A partial candle series does not announce itself: it produces
a shorter backtest that still looks like a result. Anything inherited from that
run has to be checked rather than assumed complete.

Reports per file: row count, first and last timestamp, and whether the spacing
matches the timeframe. Funding is expected at 8-hour intervals even though
freqtrade files it under a 1h name.
"""
import glob
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "user_data", "data", "binance", "futures")

TFMIN = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
         "1h": 60, "2h": 120, "4h": 240, "6h": 360, "12h": 720, "1d": 1440}
RX = re.compile(r"^(?P<pair>.+?)-(?P<tf>\w+)-(?P<kind>futures|mark|funding_rate)\.feather$")


def main():
    files = sorted(glob.glob(os.path.join(OUT, "*.feather")))
    if not files:
        print("no futures files yet")
        return
    print("%-18s %-5s %-13s %9s  %-10s %-10s %s"
          % ("pair", "tf", "kind", "rows", "from", "to", "spacing"))
    suspect = []
    for f in files:
        m = RX.match(os.path.basename(f))
        if not m:
            continue
        try:
            d = pd.read_feather(f)
        except Exception as e:
            print("  UNREADABLE %s (%s)" % (os.path.basename(f), type(e).__name__))
            suspect.append(f)
            continue
        if d.empty:
            print("  EMPTY %s" % os.path.basename(f))
            suspect.append(f)
            continue
        gaps = d["date"].diff().dt.total_seconds().div(60)
        expect = 480 if m.group("kind") == "funding_rate" else TFMIN.get(m.group("tf"))
        clean = (gaps.iloc[1:] == expect).mean() * 100 if expect else float("nan")
        flag = "" if clean >= 95 else "  <- CHECK"
        print("%-18s %-5s %-13s %9d  %-10s %-10s %6.1f%%%s"
              % (m.group("pair"), m.group("tf"), m.group("kind"), len(d),
                 str(d["date"].iloc[0])[:10], str(d["date"].iloc[-1])[:10], clean, flag))
        if clean < 95:
            suspect.append(f)
    print()
    print("files needing a second look: %d" % len(suspect))
    for f in suspect:
        print("  %s" % os.path.basename(f))
    if suspect:
        print()
        print("Delete these and let fetch_futures_archive.py rebuild them; it skips")
        print("what is already complete, so nothing else is refetched.")


if __name__ == "__main__":
    main()
