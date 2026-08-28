# -*- coding: utf-8 -*-
"""Measure exact candle coverage for each canonical native run profile.

The price files remain unversioned.  This script publishes a small,
reproducible inventory of their temporal edges and integrity instead.  A
documented listing/delisting boundary is allowed; a missing file, bad edge,
duplicate timestamp, non-monotonic series, or pair-specific interior gap is
not silently accepted.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
POLICY = os.path.join(ROOT, "REGIME_COVERAGE_POLICY.json")
OUTPUT = os.path.join(ROOT, "REGIME_COVERAGE.csv")
REPORT = os.path.join(ROOT, "REGIME_COVERAGE.md")
SPOT_DATA = os.path.join(ROOT, "user_data", "data", "binance")
FUTURES_DATA = os.path.join(ROOT, "user_data", "data", "binance", "futures")

FIELDS = [
    "strategy_id", "run_profile", "timeframe", "coverage_status",
    "coverage_evidence", "window_start", "window_end_exclusive",
    "required_pairs", "complete_pairs", "availability_limited_pairs",
    "missing_files", "edge_failures", "auxiliary_failures", "pair_specific_gaps",
    "synchronized_gaps", "duplicate_candles", "source_fingerprint",
]

TF_MINUTES = {
    "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
    "1h": 60, "2h": 120, "4h": 240, "6h": 360, "12h": 720,
    "1d": 1440, "1w": 10080,
}


def _read_csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _pair_stem(pair, futures):
    stem = pair.split(":", 1)[0].replace("/", "_")
    return stem + ("_USDT" if futures else "")


def _path(datadir, pair, timeframe, futures):
    suffix = "-%s-futures.feather" % timeframe if futures else "-%s.feather" % timeframe
    return os.path.join(datadir, _pair_stem(pair, futures) + suffix)


def _availability_end(policy, mode, pair, default):
    value = policy.get("availability_end_exclusive", {}).get("%s:%s" % (mode, pair))
    return value or default


def inspect_group(mode, timeframe, datadir, policy):
    import pandas as pd

    futures = mode == "futures"
    pairs = policy["futures_pairs" if futures else "spot_pairs"]
    start = pd.Timestamp(policy["window_start"])
    end = pd.Timestamp(policy["window_end_exclusive"])
    delta = pd.Timedelta(minutes=TF_MINUTES[timeframe])
    missing = []
    edge_failures = []
    duplicates = 0
    availability_limited = []
    series = {}
    fingerprint_parts = []

    def inspect_auxiliary(pair, kind, cadence):
        stem = _pair_stem(pair, True)
        name = ("%s-1h-mark.feather" % stem if kind == "mark" else
                "%s-1h-funding_rate.feather" % stem)
        path = os.path.join(datadir, name)
        failures = []
        if not os.path.exists(path):
            return ["%s@%s_missing" % (pair, kind)]
        dates = pd.read_feather(path, columns=["date"])["date"]
        if dates.dt.tz is None:
            dates = dates.dt.tz_localize("UTC")
        else:
            dates = dates.dt.tz_convert("UTC")
        if not dates.is_monotonic_increasing:
            failures.append("%s@%s_non_monotonic" % (pair, kind))
        duplicate_n = int(dates.duplicated().sum())
        if duplicate_n:
            failures.append("%s@%s_duplicates=%d" % (pair, kind, duplicate_n))
        expected_end = pd.Timestamp(_availability_end(
            policy, mode, pair, policy["window_end_exclusive"]))
        if len(dates) == 0 or dates.iloc[0] > start:
            failures.append("%s@%s_start" % (pair, kind))
        if len(dates) == 0 or dates.iloc[-1] < expected_end - cadence:
            failures.append("%s@%s_end" % (pair, kind))
        first = dates.iloc[0] if len(dates) else None
        last = dates.iloc[-1] if len(dates) else None
        fingerprint_parts.append("%s|%s|%s|%s|%s|%s" % (
            name, os.path.getsize(path), first, last, len(dates), duplicate_n))
        return failures

    for pair in pairs:
        path = _path(datadir, pair, timeframe, futures)
        if not os.path.exists(path):
            missing.append(pair)
            continue
        dates = pd.read_feather(path, columns=["date"])["date"]
        if dates.dt.tz is None:
            dates = dates.dt.tz_localize("UTC")
        else:
            dates = dates.dt.tz_convert("UTC")
        duplicate_n = int(dates.duplicated().sum())
        duplicates += duplicate_n
        if not dates.is_monotonic_increasing:
            edge_failures.append("%s@non_monotonic" % pair)
        expected_end = pd.Timestamp(_availability_end(
            policy, mode, pair, policy["window_end_exclusive"]))
        if expected_end < end:
            availability_limited.append(pair)
        first = dates.iloc[0] if len(dates) else None
        last = dates.iloc[-1] if len(dates) else None
        if first is None or first > start:
            edge_failures.append("%s@start" % pair)
        if last is None or last < expected_end - delta:
            edge_failures.append("%s@end" % pair)
        active = dates[(dates >= start) & (dates < expected_end)]
        gaps = active.diff()
        # The event key is the first candle after the gap.  Comparing event
        # keys across all pairs distinguishes exchange-wide downtime from a
        # hole in one pair's file.
        series[pair] = set(value.isoformat() for value in active[gaps > delta])
        fingerprint_parts.append("%s|%s|%s|%s|%s|%s" % (
            pair, os.path.getsize(path), first, last, len(dates), duplicate_n))

    pair_specific = set()
    synchronized = set()
    all_events = set().union(*series.values()) if series else set()
    for event in all_events:
        event_ts = pd.Timestamp(event)
        active_pairs = []
        with_gap = []
        for pair in pairs:
            if pair not in series:
                continue
            expected_end = pd.Timestamp(_availability_end(
                policy, mode, pair, policy["window_end_exclusive"]))
            if start <= event_ts < expected_end:
                active_pairs.append(pair)
                if event in series[pair]:
                    with_gap.append(pair)
        if active_pairs and len(with_gap) == len(active_pairs):
            synchronized.add(event)
        else:
            pair_specific.add(event)

    auxiliary_failures = []
    if futures:
        for pair in pairs:
            auxiliary_failures.extend(inspect_auxiliary(
                pair, "mark", pd.Timedelta(hours=1)))
            # Funding intervals are normally eight hours but can vary by
            # contract. Edge/ordering integrity is required; cadence is not
            # guessed from a fixed interval.
            auxiliary_failures.extend(inspect_auxiliary(
                pair, "funding", pd.Timedelta(hours=8)))

    failed_pairs = ({x.split("@", 1)[0] for x in edge_failures} |
                    {x.split("@", 1)[0] for x in auxiliary_failures})
    complete = len(pairs) - len(missing) - len(failed_pairs)
    problems = bool(missing or edge_failures or auxiliary_failures or
                    pair_specific or duplicates)
    status = "PENDING" if problems else "PASS"
    evidence = ("policy=%s;mode=%s;timeframe=%s;complete=%d/%d;"
                "availability_limited=%d;sync_gaps=%d;pair_gaps=%d;aux_failures=%d;duplicates=%d" % (
                    policy["policy_version"], mode, timeframe, complete, len(pairs),
                    len(availability_limited), len(synchronized), len(pair_specific),
                    len(auxiliary_failures), duplicates))
    fingerprint = hashlib.sha256("\n".join(sorted(fingerprint_parts)).encode("utf-8")).hexdigest()
    return {
        "coverage_status": status,
        "coverage_evidence": evidence,
        "window_start": policy["window_start"],
        "window_end_exclusive": policy["window_end_exclusive"],
        "required_pairs": len(pairs),
        "complete_pairs": complete,
        "availability_limited_pairs": ";".join(availability_limited),
        "missing_files": ";".join(missing),
        "edge_failures": ";".join(edge_failures),
        "auxiliary_failures": ";".join(auxiliary_failures),
        "pair_specific_gaps": len(pair_specific),
        "synchronized_gaps": len(synchronized),
        "duplicate_candles": duplicates,
        "source_fingerprint": "sha256_" + fingerprint,
    }


def build(profile_path=PROFILES, policy_path=POLICY, spot_datadir=SPOT_DATA,
          futures_datadir=FUTURES_DATA):
    profiles = _read_csv(profile_path)
    policy = json.load(io.open(policy_path, encoding="utf-8"))
    cache = {}
    rows = []
    for profile in profiles:
        run_profile = profile["run_profile"]
        mode = "futures" if run_profile.startswith("futures_") else "spot"
        timeframe = profile.get("execution_timeframe") or profile.get("declared_timeframe", "")
        key = (mode, timeframe)
        if timeframe not in TF_MINUTES or run_profile == "unknown":
            result = {
                "coverage_status": "PENDING",
                "coverage_evidence": "unsupported_or_unknown_profile",
                "window_start": policy["window_start"],
                "window_end_exclusive": policy["window_end_exclusive"],
                "required_pairs": 0, "complete_pairs": 0,
                "availability_limited_pairs": "", "missing_files": "",
                "edge_failures": "", "auxiliary_failures": "",
                "pair_specific_gaps": "",
                "synchronized_gaps": "", "duplicate_candles": "",
                "source_fingerprint": "",
            }
        else:
            if key not in cache:
                datadir = futures_datadir if mode == "futures" else spot_datadir
                cache[key] = inspect_group(mode, timeframe, datadir, policy)
            result = cache[key]
        row = {"strategy_id": profile["strategy_id"],
               "run_profile": run_profile, "timeframe": timeframe}
        row.update(result)
        rows.append(row)
    return rows


def _write(rows, path):
    tmp = path + ".tmp"
    with io.open(tmp, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def _table(counter):
    return "\n".join("| `%s` | %d |" % item for item in sorted(counter.items()))


def _write_report(rows, policy, path):
    statuses = collections.Counter(row["coverage_status"] for row in rows)
    profiles = collections.Counter("%s / %s" % (row["run_profile"], row["coverage_status"])
                                   for row in rows)
    unsupported = sum(row["coverage_evidence"] == "unsupported_or_unknown_profile"
                      for row in rows)
    missing = sum(bool(row["missing_files"]) for row in rows)
    edges = sum(bool(row["edge_failures"]) for row in rows)
    auxiliary = sum(bool(row["auxiliary_failures"]) for row in rows)
    pair_gaps = sum(bool(row["pair_specific_gaps"] and
                         int(row["pair_specific_gaps"])) for row in rows)
    duplicates = sum(bool(row["duplicate_candles"] and
                           int(row["duplicate_candles"])) for row in rows)
    text = """# Regime candle coverage — Stage 6 evidence

This report inventories the unversioned Freqtrade candle files used by the
native execution profiles. The machine-readable result is
`REGIME_COVERAGE.csv`; its policy is frozen in
`REGIME_COVERAGE_POLICY.json`.

The checked window is `%s` through `%s` (exclusive end). A documented
listing/delisting boundary is valid available history. Exchange-wide gaps
shared by every pair active at that timestamp are recorded and accepted;
pair-specific holes, duplicates, non-monotonic data, missing files, and bad
temporal edges remain `PENDING`.

Raw candle files are deliberately not committed. `source_fingerprint` binds
each result to file size, temporal edges, row count, and duplicate count.

## Status

| Status | Strategy profiles |
|---|---:|
%s

## Run profiles

| Run profile / status | Strategies |
|---|---:|
%s

## Pending data conditions

Counts are row counts and may overlap.

| Condition | Rows |
|---|---:|
| Unsupported, missing, or unknown timeframe/profile | %d |
| One or more required pair files missing | %d |
| One or more temporal edges incomplete | %d |
| Futures mark/funding feed incomplete | %d |
| Pair-specific interior gaps | %d |
| Duplicate candles | %d |

The policy explicitly limits spot `XMR/USDT` at its documented 2024-02-20
Binance delisting boundary. This preserves the audit's pair-available-history
design while exposing the changing basket composition rather than pretending
that all eight pairs existed for the whole window.
""" % (policy["window_start"], policy["window_end_exclusive"],
       _table(statuses), _table(profiles), unsupported, missing, edges, auxiliary,
       pair_gaps, duplicates)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(tmp, path)


def selftest():
    assert _pair_stem("BTC/USDT", False) == "BTC_USDT"
    assert _pair_stem("BTC/USDT:USDT", True) == "BTC_USDT_USDT"
    assert set(TF_MINUTES) == {"1m", "3m", "5m", "15m", "30m", "1h",
                               "2h", "4h", "6h", "12h", "1d", "1w"}
    print("regime_coverage selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default=PROFILES)
    parser.add_argument("--policy", default=POLICY)
    parser.add_argument("--spot-datadir", default=SPOT_DATA)
    parser.add_argument("--futures-datadir", default=FUTURES_DATA)
    parser.add_argument("--output", default=OUTPUT)
    parser.add_argument("--report", default=REPORT)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    rows = build(args.profiles, args.policy, args.spot_datadir, args.futures_datadir)
    _write(rows, args.output)
    policy = json.load(io.open(args.policy, encoding="utf-8"))
    _write_report(rows, policy, args.report)
    counts = collections.Counter(row["coverage_status"] for row in rows)
    print("regime coverage rows: %d" % len(rows))
    for name, count in sorted(counts.items()):
        print("  %-10s %d" % (name, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
