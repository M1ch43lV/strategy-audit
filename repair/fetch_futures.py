# -*- coding: utf-8 -*-
"""fetch_futures - download USDT-M futures candles for the short-capable stratum.

50 strategies in the corpus declare `can_short` and cannot run in the audit's
spot configuration. Measuring them needs futures data, and futures data is not
just candles: freqtrade also needs mark-price series and funding rates to price
a position correctly.

WHY NOT fetch_parallel.py. That driver reuses the audit's `fetch_bulk`, which
reads Binance's *spot* monthly archives. The futures equivalents live under
different paths and the mark/funding pieces are separate feeds again. Rebuilding
that by hand would mean reimplementing what freqtrade's own downloader already
does correctly, and getting funding wrong would corrupt every result silently.

So this parallelises freqtrade's downloader across pairs rather than replacing
it. One process per pair; the ceiling is Binance's rate limiting, not bandwidth,
which is why the worker count is deliberately modest.

RESULTS FROM THIS DATA ARE A SEPARATE STRATUM. Leverage and funding make futures
figures incomparable with the spot run - they do not belong in the same table.
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT
FT = os.path.join(AUD, "ftenv", "Scripts", "freqtrade.exe")

# Timeframes the short-capable strategies declare, plus 4h/1d for informative use.
TIMEFRAMES = ["1m", "3m", "5m", "15m", "1h", "4h", "1d"]

# Binance USDT-M perpetuals. XMR is included only so its absence is recorded
# rather than assumed: Binance delisted XMR in February 2024, so the download is
# expected to come back short or empty, and that is a fact about the market.
PAIRS = ["BTC/USDT:USDT", "ETH/USDT:USDT", "LTC/USDT:USDT", "XRP/USDT:USDT",
         "ADA/USDT:USDT", "XLM/USDT:USDT", "DASH/USDT:USDT", "XMR/USDT:USDT"]

TIMERANGE = os.environ.get("FUTURES_TIMERANGE", "20190901-20260820")


def fetch(pair):
    t0 = time.time()
    cmd = [FT, "download-data",
           "--config", os.path.join(AUD, "user_data", "config.json"),
           "--trading-mode", "futures",
           "--pairs", pair,
           "--timeframes"] + TIMEFRAMES + [
           "--timerange", TIMERANGE,
           "--data-format-ohlcv", "feather"]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONWARNINGS="ignore")
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=7200, env=env, cwd=AUD)
        out = (r.stdout + r.stderr).decode("utf-8", "replace")
        bad = [l for l in out.splitlines()
               if " ERROR " in l or "Failed" in l or "not available" in l]
        status = "ok" if r.returncode == 0 and not bad else "issues"
        note = ("" if not bad else " | " + bad[-1].strip()[:90])
        return "%-16s %-8s %5.0fs%s" % (pair, status, time.time() - t0, note)
    except subprocess.TimeoutExpired:
        return "%-16s TIMEOUT after 7200s" % pair


def main():
    pairs = sys.argv[1:] or PAIRS
    workers = int(os.environ.get("FUTURES_WORKERS", "4"))
    print("pairs %d | timeframes %s | timerange %s | workers %d"
          % (len(pairs), ",".join(TIMEFRAMES), TIMERANGE, workers), flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch, p): p for p in pairs}
        for f in as_completed(futs):
            done += 1
            print("[%d/%d] %s" % (done, len(pairs), f.result()), flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
