# -*- coding: utf-8 -*-
u"""coverage — how much of the window each pair actually covers.

WHY. I wrote "8 pairs to USDT," and that reads as "eight pairs for the whole window."
The measurement says otherwise: DASH was listed 2019-03-28 (46% of the author's window), XMR
was delisted from Binance 2024-02-20 (61% of the window outside the sample). Fully covering the author's window
are THREE pairs out of eight.

This doesn't break the numbers: you can't trade a nonexistent pair, and the engine honestly
doesn't trade it. But the basket composition CHANGES over the window, and the reader doesn't
know that. `missing_pairs` in the card doesn't see this — it checks for a missing
FILE, and the file exists, it's just short.

The boundary is named directly: coverage is calculated at the EDGES of the series within the window, not
searching for holes inside. A leaky series with correct edges will show 100%.
"""
from __future__ import print_function

import glob
import os
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import pandas as pd

WINDOWS = ((u"author's window", "2018-03-01", "2020-03-01"),
           (u"outside the sample", "2020-03-01", "2026-08-20"))


def cov(dt, lo, hi):
    lo, hi = pd.Timestamp(lo, tz="UTC"), pd.Timestamp(hi, tz="UTC")
    s = dt[(dt >= lo) & (dt <= hi)]
    if len(s) == 0:
        return 0.0
    return 100.0 * (s.iloc[-1] - s.iloc[0]).total_seconds() / (hi - lo).total_seconds()


def main():
    tf = sys.argv[1] if len(sys.argv) > 1 else "1h"
    files = sorted(glob.glob(os.path.join(_ROOT, "user_data", "data", "binance",
                                          "*-%s.feather" % tf)))
    if not files:
        print(u"no data for %s" % tf)
        return
    print(u"WINDOW COVERAGE, timeframe %s" % tf)
    print(u"%-12s %-12s %-12s %12s %12s" % (u"pair", u"first", u"last",
                                            WINDOWS[0][0], WINDOWS[1][0]))
    full = 0
    for f in files:
        d = pd.read_feather(f)
        dt = d["date"]
        c = [cov(dt, w[1], w[2]) for w in WINDOWS]
        if c[0] > 99.0:
            full += 1
        print(u"%-12s %-12s %-12s %11.1f%% %11.1f%%"
              % (os.path.basename(f).split("-")[0], str(dt.iloc[0])[:10],
                 str(dt.iloc[-1])[:10], c[0], c[1]))
    print()
    print(u"The author's window is fully covered by %d pairs out of %d." % (full, len(files)))
    print(u"\"8 pairs\" is the query list, not what was traded for the whole window.")


if __name__ == "__main__":
    main()
