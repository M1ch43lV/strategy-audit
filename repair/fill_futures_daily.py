# -*- coding: utf-8 -*-
"""Fill local futures candle/mark gaps from Binance Vision daily archives.

Monthly archives lag the active month.  This resumable helper reads each
existing Freqtrade feather file, requests only missing calendar days and the
unclosed monthly tail, merges by timestamp, and writes atomically.  Raw market
data remains ignored; `regime_coverage.py` publishes the integrity evidence.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATADIR = os.path.join(ROOT, "user_data", "data", "binance", "futures")
BASE = "https://data.binance.vision/data/futures/um/daily"
TF_MINUTES = {"1m": 1, "3m": 3, "5m": 5, "15m": 15,
              "1h": 60, "4h": 240, "1d": 1440}


def _spec(path):
    name = os.path.basename(path)
    match = re.match(r"([A-Z]+)_USDT_USDT-([^-]+)-(futures|mark)\.feather$", name)
    if not match:
        return None
    asset, timeframe, suffix = match.groups()
    return asset + "USDT", timeframe, ("klines" if suffix == "futures" else "markPriceKlines")


def _days_to_fetch(dates, delta, through):
    days = set()
    if len(dates):
        last_day = dates.iloc[-1].date()
        day = last_day + pd.Timedelta(days=1)
        while day <= through.date():
            days.add(day)
            day += pd.Timedelta(days=1)
        gaps = dates.diff()
        for index in gaps[gaps > delta].index:
            before = dates.iloc[index - 1].normalize()
            after = dates.iloc[index].normalize()
            day = before
            while day <= after:
                days.add(day.date())
                day += pd.Timedelta(days=1)
    return sorted(days)


def _url(symbol, timeframe, kind, day):
    date = day.strftime("%Y-%m-%d")
    return "%s/%s/%s/%s/%s-%s-%s.zip" % (
        BASE, kind, symbol, timeframe, symbol, timeframe, date)


def _grab(job):
    path, symbol, timeframe, kind, day = job
    url = _url(symbol, timeframe, kind, day)
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(url, timeout=60).read()
            with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
                text = bundle.read(bundle.namelist()[0]).decode("utf-8")
            rows = []
            for line in text.splitlines():
                fields = line.split(",")
                if not fields or not fields[0][:1].isdigit():
                    continue
                timestamp = int(float(fields[0]))
                if timestamp > 1e14:
                    timestamp //= 1000
                rows.append((timestamp, float(fields[1]), float(fields[2]),
                             float(fields[3]), float(fields[4]),
                             float(fields[5]) if kind == "klines" else 0.0))
            return path, rows, "ok"
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return path, [], "absent"
        except Exception:
            pass
        time.sleep(1 + attempt)
    return path, [], "network"


def _merge(path, rows):
    if not rows:
        return 0
    existing = pd.read_feather(path)
    added = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
    added["date"] = pd.to_datetime(added.pop("ts"), unit="ms", utc=True).astype(
        "datetime64[ms, UTC]")
    combined = pd.concat([existing, added], ignore_index=True)
    before = len(combined)
    combined = combined.drop_duplicates("date").sort_values("date")
    new_rows = len(combined) - len(existing)
    if new_rows <= 0:
        return 0
    tmp = path + ".tmp"
    combined[["date", "open", "high", "low", "close", "volume"]] \
        .reset_index(drop=True).to_feather(tmp)
    os.replace(tmp, path)
    assert len(combined) <= before
    return new_rows


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--datadir", default=DATADIR)
    parser.add_argument("--through", default="2026-08-20")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    through = pd.Timestamp(args.through, tz="UTC")
    jobs = []
    for path in sorted(os.path.join(args.datadir, name)
                       for name in os.listdir(args.datadir)):
        spec = _spec(path)
        if not spec:
            continue
        symbol, timeframe, kind = spec
        if timeframe not in TF_MINUTES:
            continue
        dates = pd.read_feather(path, columns=["date"])["date"]
        delta = pd.Timedelta(minutes=TF_MINUTES[timeframe])
        for day in _days_to_fetch(dates, delta, through):
            jobs.append((path, symbol, timeframe, kind, day))
    print("daily archive jobs: %d across %d files" %
          (len(jobs), len({job[0] for job in jobs})), flush=True)
    if args.dry_run or not jobs:
        return 0
    rows_by_path = defaultdict(list)
    statuses = defaultdict(int)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(_grab, job) for job in jobs]
        for number, future in enumerate(as_completed(futures), 1):
            path, rows, status = future.result()
            statuses[status] += 1
            rows_by_path[path].extend(rows)
            if number % 100 == 0 or number == len(futures):
                print("[%d/%d] ok=%d absent=%d network=%d" % (
                    number, len(futures), statuses["ok"], statuses["absent"],
                    statuses["network"]), flush=True)
    added = 0
    for path, rows in rows_by_path.items():
        added += _merge(path, rows)
    print("files updated: %d | candle rows added: %d" %
          (sum(bool(rows) for rows in rows_by_path.values()), added))
    if statuses["network"]:
        print("NETWORK FAILURES: rerun the same command; writes are resumable")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
