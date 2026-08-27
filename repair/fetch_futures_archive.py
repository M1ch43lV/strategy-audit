# -*- coding: utf-8 -*-
"""fetch_futures_archive - USDT-M futures data from Binance's static archives.

REPLACES AN APPROACH THAT FAILED. The first attempt parallelised freqtrade's
`download-data`, which talks to the REST API. Eight concurrent processes earned
an IP ban:

    binance 418 {"code":-1003,"msg":"Way too many requests; IP(...) banned until ..."}

The ceiling there was Binance's rate limit, not the line. `data.binance.vision`
is a static file host with no such limit - the same source the audit's own
`fetch_bulk.py` uses for spot - so parallelism is actually usable here.

THREE FEEDS, NOT ONE. Futures pricing needs more than candles, and getting this
wrong would corrupt every result quietly rather than loudly:

    klines           the OHLCV the strategy trades on
    markPriceKlines  what liquidation and unrealised PnL are measured against
    fundingRate      the periodic payment between long and short

freqtrade stores all three in the same OHLCV-shaped frame. For funding the rate
sits in `open` and the remaining columns are zero - that layout was read off the
file freqtrade itself produced, not guessed.

RESULTS FROM THIS DATA ARE A SEPARATE STRATUM. Leverage and funding make futures
figures incomparable with the spot run.
"""
import io
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT
OUT = os.path.join(AUD, "user_data", "data", "binance", "futures")

BASE = "https://data.binance.vision/data/futures/um/monthly"
PAIRS = {"BTCUSDT": "BTC_USDT_USDT", "ETHUSDT": "ETH_USDT_USDT",
         "LTCUSDT": "LTC_USDT_USDT", "XRPUSDT": "XRP_USDT_USDT",
         "ADAUSDT": "ADA_USDT_USDT", "XLMUSDT": "XLM_USDT_USDT",
         "DASHUSDT": "DASH_USDT_USDT", "XMRUSDT": "XMR_USDT_USDT"}
TIMEFRAMES = ["1m", "3m", "5m", "15m", "1h", "4h", "1d"]
Y0, M0, Y1, M1 = 2019, 9, 2026, 7      # USDT-M perpetuals start late 2019
RETRY = 4
MIN_BYTES = 20000


def months():
    y, m = Y0, M0
    while (y, m) <= (Y1, M1):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def grab(url):
    """(rows, status). status: ok | absent | network"""
    for attempt in range(RETRY):
        try:
            raw = urllib.request.urlopen(url, timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return [], "absent"      # pair not listed that month - a fact
            time.sleep(1 + attempt)
            continue
        except Exception:
            time.sleep(1 + attempt)
            continue
        z = zipfile.ZipFile(io.BytesIO(raw))
        rows = []
        for line in z.read(z.namelist()[0]).decode().splitlines():
            p = line.split(",")
            if not p or not p[0][:1].isdigit():
                continue                 # header row in newer archives
            rows.append(p)
        return rows, "ok"
    return [], "network"


def _ts(v):
    t = int(float(v))
    return t // 1000 if t > 1e14 else t   # microseconds since 2025


def fetch_klines(sym, tf, kind):
    """kind: 'klines' or 'markPriceKlines'"""
    out, gaps, neterr = [], 0, 0
    for y, m in months():
        url = "%s/%s/%s/%s/%s-%s-%04d-%02d.zip" % (BASE, kind, sym, tf, sym, tf, y, m)
        rows, st = grab(url)
        if st == "ok":
            for p in rows:
                out.append((_ts(p[0]), float(p[1]), float(p[2]),
                            float(p[3]), float(p[4]),
                            float(p[5]) if kind == "klines" else 0.0))
        elif st == "absent":
            gaps += 1
        else:
            neterr += 1
    return out, gaps, neterr


def fetch_funding(sym):
    out, gaps, neterr = [], 0, 0
    for y, m in months():
        url = "%s/fundingRate/%s/%s-fundingRate-%04d-%02d.zip" % (BASE, sym, sym, y, m)
        rows, st = grab(url)
        if st == "ok":
            for p in rows:
                # calc_time, funding_interval_hours, last_funding_rate
                out.append((_ts(p[0]), float(p[-1]), 0.0, 0.0, 0.0, 0.0))
        elif st == "absent":
            gaps += 1
        else:
            neterr += 1
    return out, gaps, neterr


def write(rows, path):
    if not rows:
        return 0
    d = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
    d = d.drop_duplicates("ts").sort_values("ts")
    d["date"] = pd.to_datetime(d["ts"], unit="ms", utc=True).astype("datetime64[ms, UTC]")
    tmp = path + ".tmp"
    d[["date", "open", "high", "low", "close", "volume"]] \
        .reset_index(drop=True).to_feather(tmp)
    os.replace(tmp, path)                 # no half-written file on interruption
    return len(d)


def job_done(path):
    return os.path.exists(path) and os.path.getsize(path) > MIN_BYTES


def run_job(spec):
    sym, name, kind, tf = spec
    if kind == "funding":
        path = os.path.join(OUT, "%s-1h-funding_rate.feather" % name)
    elif kind == "markPriceKlines":
        path = os.path.join(OUT, "%s-%s-mark.feather" % (name, tf))
    else:
        path = os.path.join(OUT, "%s-%s-futures.feather" % (name, tf))
    if job_done(path):
        return "%-14s %-16s %-4s skip (present)" % (sym, kind, tf)
    t0 = time.time()
    if kind == "funding":
        rows, gaps, neterr = fetch_funding(sym)
    else:
        rows, gaps, neterr = fetch_klines(sym, tf, kind)
    n = write(rows, path)
    note = ""
    if gaps:
        note += " | %d months unlisted" % gaps
    if neterr:
        note += " | %d NETWORK FAILURES - SERIES INCOMPLETE" % neterr
    if n == 0:
        return "%-14s %-16s %-4s NOTHING (not listed?)%s" % (sym, kind, tf, note)
    return "%-14s %-16s %-4s %8d rows in %.0fs%s" % (sym, kind, tf, n, time.time() - t0, note)


def main():
    os.makedirs(OUT, exist_ok=True)
    syms = sys.argv[1:] or list(PAIRS)
    jobs = []
    for sym in syms:
        name = PAIRS[sym]
        jobs.append((sym, name, "funding", "1h"))
        jobs.append((sym, name, "markPriceKlines", "1h"))
        for tf in TIMEFRAMES:
            jobs.append((sym, name, "klines", tf))
    workers = int(os.environ.get("FUTURES_WORKERS", "12"))
    print("jobs %d | workers %d | static archives, no API rate limit"
          % (len(jobs), workers), flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run_job, j) for j in jobs]
        for f in as_completed(futs):
            done += 1
            print("[%d/%d] %s" % (done, len(jobs), f.result()), flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
