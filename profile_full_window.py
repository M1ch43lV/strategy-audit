# -*- coding: utf-8 -*-
"""Resumable native-mode pair-sharded full-window trade measurements.

One positive pair is sufficient to resolve a zero-trade smoke as positive.
A final zero is accepted only after every configured pair completes. Sharding
does not replace pooled performance backtests; it answers only the Stage 6
binary trade-presence gate.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import io
import json
import os
import sys
import threading

import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(ROOT, "PROFILE_FULL_WINDOW.json")
TIMERANGE = "20200301-20260821"
LOCK = threading.Lock()

CONVERGENCE = os.path.join(ROOT, "WARMUP_CONVERGENCE.json")
# Stores holding a repair run. A repaired row has to be measured the way it
# was repaired, or the run reports on a configuration nobody intends to use.
REPAIR_STORES = (
    os.path.join(ROOT, "ELIGIBILITY_TIMEFRAME_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_MODULE_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_SIGNATURE_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_FREQAI_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_FREQAI_WTAI.json"),
)


def settled_warmups():
    """The warm-up each row settled at, as a config override.

    `REGIME_PREREGISTRATION.md`, amendment of 2026-09-02: the settled warm-up
    is the measurement. A full-window run at the author's declared value
    measures exactly the drift the ladder exists to remove, so the number the
    ranking is built on would carry it.
    """
    if not os.path.exists(CONVERGENCE):
        return {}
    results = json.load(io.open(CONVERGENCE, encoding="utf-8")).get("results", {})
    out = {}
    for strategy, record in results.items():
        if record.get("state") != "converged":
            continue
        startup = record.get("chosen_startup_candle_count")
        if startup:
            out[strategy] = {"startup_candle_count": int(startup)}
    return out


def repair_overrides():
    """Config keys a repaired row must be run with, keyed by strategy."""
    out = {}
    for path in REPAIR_STORES:
        if not os.path.exists(path):
            continue
        results = json.load(io.open(path, encoding="utf-8")).get("results", {})
        for strategy, record in results.items():
            overrides = record.get("config_overrides") or {}
            if overrides:
                out.setdefault(strategy, dict(overrides))
    return out


def run_settings():
    """Everything a row must be run with: its repair, then its warm-up.

    The repair takes precedence on a shared key, because it is what makes the
    strategy start at all. Same merge order as the look-ahead queue, so the
    full window and the checks agree on what the row is.
    """
    merged = {}
    warmups = settled_warmups()
    repairs = repair_overrides()
    for strategy in set(warmups) | set(repairs):
        settings = dict(warmups.get(strategy) or {})
        settings.update(repairs.get(strategy) or {})
        merged[strategy] = settings
    return merged


def _write(data, path):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def _load(path):
    if not os.path.exists(path):
        return {"schema_version": 2, "timerange": TIMERANGE, "results": {}}
    data = json.load(io.open(path, encoding="utf-8"))
    data["schema_version"] = 2
    data.setdefault("results", {})
    return data


def _pairs(mode):
    config_path = (profile_smoke.FUTURES_CONFIG if mode == "futures"
                   else profile_smoke.SPOT_CONFIG)
    config = profile_smoke._read_jsonc(config_path)
    return list(config["exchange"]["pair_whitelist"])


def _aggregate(record, pairs):
    parts = record.get("pair_results", {})
    measured = [parts[p] for p in pairs
                if parts.get(p, {}).get("status") == "measured"]
    positive = [part for part in measured if int(part.get("trades", 0)) > 0]
    if positive:
        record.update({
            "status": "measured",
            "trades": sum(int(part.get("trades", 0)) for part in measured),
            "long_trades": sum(int(part.get("long_trades", 0)) for part in measured),
            "short_trades": sum(int(part.get("short_trades", 0)) for part in measured),
            "measurement_scope": "full_window_trade_presence",
            "why": "at least one pair produced trades over the full window",
        })
    elif len(measured) == len(pairs):
        record.update({
            "status": "measured", "trades": 0, "long_trades": 0,
            "short_trades": 0, "measurement_scope": "all_pairs_full_window",
            "why": "all configured pairs completed with zero trades",
        })
    else:
        record.update({
            "status": "incomplete", "measurement_scope": "pair_shards",
            "why": "%d/%d pairs completed; no positive pair yet" %
                   (len(measured), len(pairs)),
        })


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", action="append", required=True)
    parser.add_argument("--output", default=OUTPUT)
    parser.add_argument("--timerange", default=TIMERANGE)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--pair", action="append", default=[])
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--settled-only", action="store_true",
        help="run only rows whose warm-up the ladder settled, so every "
             "number in the set rests on the same basis")
    args = parser.parse_args(argv)
    if args.timerange != TIMERANGE:
        raise SystemExit("full-window timerange must be %s" % TIMERANGE)

    rows = {row["strategy_id"]: row
            for row in profile_smoke.read_manifest(profile_smoke.MANIFEST)}
    data = _load(args.output)
    data.update({"timerange": TIMERANGE,
                 "pair_universes": {"spot": _pairs("spot"),
                                    "futures": _pairs("futures")},
                 "runtime_id": os.environ.get(
                     "PROFILE_RUNTIME_ID", "native_unversioned")})

    # Every row is run with what it was repaired and settled at. Loaded once,
    # so a run cannot half-apply them.
    overrides = run_settings()
    settled = [name for name in args.strategy
               if "startup_candle_count" in (overrides.get(name) or {})]
    unsettled = [name for name in args.strategy if name not in set(settled)]
    if unsettled and args.settled_only:
        print("skipping %d row(s) with no settled warm-up: %s"
              % (len(unsettled), ", ".join(sorted(unsettled)[:8])), flush=True)
        args.strategy = [name for name in args.strategy
                         if name in set(settled)]
        unsettled = []
    # A row without a settled warm-up runs at whatever its author declared.
    # That is a different basis from its neighbour's, and the difference has
    # to be visible before the numbers are compared, not discovered after.
    print("full window: %d row(s) at a settled warm-up, %d at the author's "
          "declared value" % (len(settled), len(unsettled)), flush=True)

    for strategy in args.strategy:
        row = rows[strategy]
        mode = "futures" if row["run_profile"].startswith("futures_") else "spot"
        configured_pairs = _pairs(mode)
        pairs = [pair for pair in configured_pairs
                 if not args.pair or pair in set(args.pair)]
        if args.pair and len(pairs) != len(set(args.pair)):
            raise SystemExit("requested pair is not in the frozen %s basket" % mode)
        identity = profile_smoke._identity(row)
        record = data["results"].get(strategy) or {}
        if any(record.get(key) != value for key, value in identity.items()):
            record = {}
        record.update(identity)
        record.update({"mode": mode, "run_profile": row["run_profile"],
                       "timerange": TIMERANGE,
                       "runtime_id": data["runtime_id"]})
        record.setdefault("pair_results", {})
        todo = [pair for pair in pairs if args.force or
                record["pair_results"].get(pair, {}).get("status") != "measured"]
        print("%s: %d pair shard(s)" % (strategy, len(todo)), flush=True)

        settings = overrides.get(strategy) or None
        if settings:
            record["config_overrides"] = settings

        def run(pair):
            return pair, profile_smoke.run_one(
                row, TIMERANGE, args.timeout, pair,
                config_overrides=settings)

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=max(1, args.workers)) as pool:
            futures = [pool.submit(run, pair) for pair in todo]
            for future in concurrent.futures.as_completed(futures):
                pair, result = future.result()
                result["runtime_id"] = data["runtime_id"]
                with LOCK:
                    record["pair_results"][pair] = result
                    _aggregate(record, configured_pairs)
                    data["results"][strategy] = record
                    _write(data, args.output)
                print("  %-18s %-10s trades=%s" %
                      (pair, result["status"], result.get("trades", "")), flush=True)
        _aggregate(record, configured_pairs)
        _write(data, args.output)
        print("  result: %s (%s)" % (record["status"], record["why"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
