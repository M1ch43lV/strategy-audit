# -*- coding: utf-8 -*-
"""Backtest the rotation bot over the whole window, one pair per run, in parallel.

    ./ftenv/Scripts/python.exe -m bot.run_rotation RegimeRotationBot --workers 4

Why per pair: the bot makes no decision that depends on another pair (the BTC phase is read from
BTC's own candles, whatever pair is traded), so a run per pair gives the same trades as one run over
all eight, and each run stays well inside the project's 3600 s ceiling. The account of a single-pair
run is meaningless (the whole wallet goes into that pair), which is why the evaluation
(`bot/rotation_eval.py`) works from each trade's profit ratio, never from the run's balance.

Base timeframe 5m with `--timeframe-detail 1m`, futures, isolated margin, 0.1 % fee per side, the
window `profile_full_window.TIMERANGE` uses for futures strategies.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evidence import profile_full_window  # noqa: E402

PAIRS = ["BTC", "ETH", "LTC", "XRP", "ADA", "XLM", "XMR", "DASH"]
OUT = os.path.join(ROOT, "user_data", "rotation")
TIMEOUT = 3600


def archive_of(variant, coin):
    found = sorted(glob.glob(os.path.join(OUT, "%s_%s-*.zip" % (variant, coin))))
    return found[-1] if found else None


def run_one(variant, coin, timerange):
    if archive_of(variant, coin):
        return coin, "exists", 0.0
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    cmd = [sys.executable, os.path.join(ROOT, "evidence", "profile_freqtrade.py"), "backtesting",
           "--config", os.path.join(ROOT, "runtime", "profile_futures_config.json"),
           "--strategy", variant, "--strategy-path", os.path.join(ROOT, "bot"),
           "--timerange", timerange, "--fee", "0.001", "--export", "trades",
           "--backtest-directory", os.path.join(OUT, "%s_%s" % (variant, coin)), "--cache", "none",
           "--datadir", os.path.join(ROOT, "user_data", "data", "binance"),
           "--timeframe-detail", "1m", "--pairs", "%s/USDT:USDT" % coin]
    started = time.time()
    log = os.path.join(OUT, "%s_%s.log" % (variant, coin))
    with open(log, "w", encoding="utf-8") as handle:
        try:
            proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=handle, stderr=subprocess.STDOUT, timeout=TIMEOUT)
            status = "ok" if proc.returncode == 0 else "rc%d" % proc.returncode
        except subprocess.TimeoutExpired:
            status = "timeout"
    if status == "ok" and not archive_of(variant, coin):
        status = "no_archive"
    return coin, status, time.time() - started


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("variant")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timerange", default=profile_full_window.TIMERANGE["spot"])
    args = parser.parse_args()
    os.makedirs(OUT, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, args.variant, coin, args.timerange) for coin in PAIRS]
        for future in concurrent.futures.as_completed(futures):
            coin, status, seconds = future.result()
            print("%s %-5s %-10s %6.0f s" % (args.variant, coin, status, seconds), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
