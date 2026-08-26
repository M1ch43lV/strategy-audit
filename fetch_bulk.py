# -*- coding: utf-8 -*-
u"""Loading candles FROM MONTHLY Binance ARCHIVES, not via paginated API.

WHY REWRITTEN. The paginated variant (`fetch_tf.py`) returns 1000 candles in
1.9 s. For 5m that is 29 minutes PER PAIR, for 1m — 19 hours per pair. It was not
broken, it was unusable in time, and 25 minutes of work yielded zero files.
The monthly archive returns 8928 five-minute candles in 1.55 s — same source, same
data, 11 times faster (for 1m — 60 times).

HONESTY AT BOUNDARIES. A pair not listed this month returns 404. This is NOT
a network error and not a reason to stay silent: the month is skipped, and the number of skips
is printed at the end. Missing data must be visible as missing,
not as a short series.
"""
from __future__ import print_function
import os as _os
_ROOT = _os.environ.get("AUDIT_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
import io, os, sys, time, urllib.error, urllib.request, zipfile

sys.path.insert(0, _ROOT)
import pandas as pd

OUT = _os.path.join(_ROOT, "user_data/data/binance")
PAIRS = {"BTCUSDT": "BTC_USDT", "LTCUSDT": "LTC_USDT", "ETHUSDT": "ETH_USDT",
         "XRPUSDT": "XRP_USDT", "ADAUSDT": "ADA_USDT", "XLMUSDT": "XLM_USDT",
         "XMRUSDT": "XMR_USDT", "DASHUSDT": "DASH_USDT"}
BASE = "https://data.binance.vision/data/spot/monthly/klines/%s/%s/%s-%s-%s.zip"
DAILY = "https://data.binance.vision/data/spot/daily/klines/%s/%s/%s-%s-%s.zip"
# Monthly archives end with the last FULL month. Without daily backfill
# 5m broke off at 2026-07-31, while hourly went to 2026-08-20 — different windows for
# different timeframes, i.e., incomparable runs. A 20-day hole is less than
# a percent, and that is exactly why it is easy to miss.
TAIL_DAYS = ["2026-08-%02d" % d for d in range(1, 21)]
TF = sys.argv[1] if len(sys.argv) > 1 else "5m"
Y0, M0, Y1, M1 = 2018, 3, 2026, 7
RETRY = 4


def months():
    y, m = Y0, M0
    while (y, m) <= (Y1, M1):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def grab(sym, tf, tag, daily=False):
    u"""(rows, status). Status: ok | not in archive | NETWORK."""
    url = (DAILY if daily else BASE) % (sym, tf, sym, tf, tag)
    for attempt in range(RETRY):
        try:
            raw = urllib.request.urlopen(url, timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return [], u"not in archive"
            time.sleep(1 + attempt)
            continue
        except Exception:
            time.sleep(1 + attempt)
            continue
        z = zipfile.ZipFile(io.BytesIO(raw))
        rows = []
        for line in z.read(z.namelist()[0]).decode().splitlines():
            p = line.split(",")
            if len(p) < 6 or not p[0][:1].isdigit():   # header of new archives
                continue
            ts = int(float(p[0]))
            if ts > 1e14:                              # microseconds since 2025
                ts //= 1000
            rows.append((ts, float(p[1]), float(p[2]),
                         float(p[3]), float(p[4]), float(p[5])))
        return rows, u"ok"
    return [], u"NETWORK"


def main():
    # The same lock as in corpus.py: two loaders for one candle folder —
    # the same defect class, and it already happened to me (20.08).
    import runlock
    if not runlock.acquire("fetch"):
        raise SystemExit(2)
    import atexit
    atexit.register(lambda: runlock.release("fetch"))
    os.makedirs(OUT, exist_ok=True)
    force = "--refill" in sys.argv
    todo = [(s, f) for s, f in PAIRS.items()
            if force or not (os.path.exists(os.path.join(OUT, "%s-%s.feather" % (f, TF)))
                             and os.path.getsize(os.path.join(OUT, "%s-%s.feather" % (f, TF))) > 100000)]
    print(u"TIMEFRAME %s · pairs to load %d of %d" % (TF, len(todo), len(PAIRS)), flush=True)
    for sym, ft in todo:
        t0 = time.time()  # TOTAL: duration for printing, not part of the verdict
        rows, gaps, neterr = [], [], 0
        for y, m in months():
            r, st = grab(sym, TF, "%04d-%02d" % (y, m))
            if st == u"ok":
                rows += r
            elif st == u"not in archive":
                gaps.append("%04d-%02d" % (y, m))
            else:
                neterr += 1
        tail = 0
        for day in TAIL_DAYS:                     # backfill of unclosed month
            r, st = grab(sym, TF, day, daily=True)
            if st == u"ok":
                rows += r
                tail += len(r)
            elif st != u"not in archive":
                neterr += 1
        if not rows:
            print(u"  ✗ %-9s NOT A SINGLE MONTH (network failures %d)" % (sym, neterr), flush=True)
            continue
        d = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
        d = d.drop_duplicates("ts").sort_values("ts")
        d["date"] = pd.to_datetime(d["ts"], unit="ms", utc=True)
        d[["date", "open", "high", "low", "close", "volume"]] \
            .reset_index(drop=True).to_feather(os.path.join(OUT, "%s-%s.feather" % (ft, TF)))
        note = u""
        if gaps:
            note += u" ? months without listing %d (since %s)" % (len(gaps), gaps[0])
        note += u" · days backfilled %d" % tail
        if neterr:
            note += u" · NETWORK FAILURES %d — series INCOMPLETE" % neterr
        print(u"  ✓ %-9s %8d candles  %s … %s  in %.0f s%s"
              % (sym, len(d), str(d["date"].iloc[0])[:10], str(d["date"].iloc[-1])[:10],
                 time.time() - t0, note), flush=True)  # TOTAL: print duration
    print(u"DONE %s" % TF, flush=True)


if __name__ == "__main__":
    main()
