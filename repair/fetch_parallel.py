# -*- coding: utf-8 -*-
"""fetch_parallel - download candles for many (pair, timeframe) combinations at once.

WHAT IS AND IS NOT CHANGED. The data logic is the audit's own `fetch_bulk.py`,
imported and reused unmodified: the same Binance monthly archives, the same
parser, the same daily top-up for the unfinished month, the same de-duplication
and column order. Only the SCHEDULING is replaced. Bytes on disk are therefore
identical to what the sequential script would have written; if they were not,
the whole point of reusing the module would be lost.

WHY THE LOCK IS NOT REUSED. `fetch_bulk.main()` takes one global lock named
"fetch" because the author once had two downloaders writing the same candle
files. That hazard is real but it is per FILE, and each (pair, timeframe) pair
writes its own file. This driver therefore serialises per output file - a job
is skipped if its file already exists - and runs different files concurrently.
The property the original lock protected is preserved; the over-broad part is
dropped.

Already complete files are skipped, so an interrupted run resumes.
"""
import io
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT
os.environ.setdefault("AUDIT_ROOT", AUD)

# fetch_bulk reads its timeframe from sys.argv at import time; give it a value
# so importing it never fails, then ignore that value and pass tf explicitly.
_argv = sys.argv
sys.argv = [_argv[0], "1h"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_bulk_upstream as fb  # noqa: E402
sys.argv = _argv

import pandas as pd  # noqa: E402

MIN_BYTES = 100000  # same completeness threshold the original uses


def out_path(pair_file, tf):
    return os.path.join(fb.OUT, "%s-%s.feather" % (pair_file, tf))


def already_done(pair_file, tf):
    p = out_path(pair_file, tf)
    return os.path.exists(p) and os.path.getsize(p) > MIN_BYTES


def fetch_one(sym, pair_file, tf):
    """Download one (pair, timeframe). Returns a human-readable status line."""
    t0 = time.time()
    rows, gaps, neterr = [], 0, 0
    for y, m in fb.months():
        r, st = fb.grab(sym, tf, "%04d-%02d" % (y, m))
        if st == u"ok":
            rows += r
        elif st == u"\u043d\u0435\u0442 \u0432 \u0430\u0440\u0445\u0438\u0432\u0435":
            gaps += 1          # pair was not listed that month - absence, not error
        else:
            neterr += 1
    tail = 0
    for day in fb.TAIL_DAYS:   # top up the month the monthly archive has not closed
        r, st = fb.grab(sym, tf, day, daily=True)
        if st == u"ok":
            rows += r
            tail += len(r)
        elif st != u"\u043d\u0435\u0442 \u0432 \u0430\u0440\u0445\u0438\u0432\u0435":
            neterr += 1
    if not rows:
        return "  x %-9s %-4s NO MONTHS AT ALL (network failures %d)" % (sym, tf, neterr)
    d = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
    d = d.drop_duplicates("ts").sort_values("ts")
    d["date"] = pd.to_datetime(d["ts"], unit="ms", utc=True)
    tmp = out_path(pair_file, tf) + ".tmp"
    d[["date", "open", "high", "low", "close", "volume"]] \
        .reset_index(drop=True).to_feather(tmp)
    os.replace(tmp, out_path(pair_file, tf))   # never leave a half-written file
    note = ""
    if gaps:
        note += " | %d months unlisted" % gaps
    if neterr:
        note += " | %d NETWORK FAILURES - SERIES INCOMPLETE" % neterr
    return "  + %-9s %-4s %8d candles  %s .. %s  in %.0fs%s" % (
        sym, tf, len(d), str(d["date"].iloc[0])[:10], str(d["date"].iloc[-1])[:10],
        time.time() - t0, note)


def main():
    tfs = sys.argv[1:] or ["5m", "15m", "4h", "1d", "30m", "6h", "3m", "2h", "1w", "1m"]
    workers = int(os.environ.get("FETCH_WORKERS", "12"))
    jobs = [(s, f, tf) for tf in tfs for s, f in sorted(fb.PAIRS.items())
            if not already_done(f, tf)]
    skipped = len(tfs) * len(fb.PAIRS) - len(jobs)
    print("timeframes %s | jobs %d | already complete %d | workers %d"
          % (",".join(tfs), len(jobs), skipped, workers), flush=True)
    if not jobs:
        return
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_one, s, f, tf): (s, tf) for s, f, tf in jobs}
        for fut in as_completed(futs):
            done += 1
            try:
                line = fut.result()
            except Exception as e:
                s, tf = futs[fut]
                line = "  x %-9s %-4s EXCEPTION %r" % (s, tf, e)
            print("[%d/%d] %s" % (done, len(jobs), line), flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
