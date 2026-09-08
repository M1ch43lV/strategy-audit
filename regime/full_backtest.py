"""Resumable canonical pooled full-window backtests for Phase A."""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import datetime
import json
import os
import sys
import threading
from pathlib import Path

import profile_smoke
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import profile_full_window


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "regime" / "full_backtest_manifest.json"
STATUS = ROOT / "STRATEGY_STATUS.csv"
PERFORMANCE_LIMITS = ROOT / "POOLED_BACKTEST_PERFORMANCE_LIMIT.json"
OOM_LIMITS = ROOT / "POOLED_BACKTEST_OOM_LIMIT.json"
STAKE_OVERFLOWS = ROOT / "POOLED_BACKTEST_STAKE_OVERFLOW.json"
# The window lives in exactly one place - `profile_full_window.TIMERANGE` -
# so this stays a per-mode lookup through that module rather than its own
# copy of the same two dates. A second constant is how this file spent
# 2026-09-03 to 2026-09-05 measuring the pre-amendment window after the
# root runner had already moved to the amended one: nothing failed loudly,
# every row here just quietly disagreed with every row there.
TIMERANGE = profile_full_window.TIMERANGE
timerange = profile_full_window.timerange
LOCK = threading.Lock()


def _write(data: dict, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _load(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "timerange": TIMERANGE, "results": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def eligible() -> list[dict]:
    """The current benchmark population, not the frozen E0 anchor.

    `REGIME_ELIGIBILITY.csv`'s `regime_eligible=true` is the 67-row set E0
    was frozen on 2026-08-30; E0 was retired as a cohort on 2026-09-03 and
    every one of its rows is now decided the same way as the other 833 -
    `STRATEGY_STATUS.csv`'s `cohort == "E1_expanded"`, 579 rows regenerated
    from current evidence rather than a snapshot that predates four
    expansion waves.
    """
    with STATUS.open(newline="", encoding="utf-8-sig") as handle:
        allowed = {row["strategy_id"] for row in csv.DictReader(handle)
                   if row["cohort"] == "E1_expanded"}
    return [row for row in profile_smoke.read_manifest(profile_smoke.MANIFEST)
            if row["strategy_id"] in allowed]


def performance_limits() -> dict:
    """Strategies confirmed to reproducibly exceed the fixed 3600s budget.

    The 3600s timeout is a hard limit, not tuned per strategy (PIPELINE.md
    Stufe 7), so a strategy that keeps landing exactly on it would otherwise
    retry forever - burning another full hour every container pass with no
    prospect of ever reaching `measured`. `POOLED_BACKTEST_PERFORMANCE_LIMIT.json`
    is the hand-curated confirmation (at least two independent timeouts, no
    other failure mode) that a strategy belongs here rather than just being
    unlucky once.
    """
    if not PERFORMANCE_LIMITS.exists():
        return {}
    return json.loads(PERFORMANCE_LIMITS.read_text(encoding="utf-8"))["results"]


def oom_limits() -> dict:
    """Strategies confirmed to hit the OOM killer under the most generous
    resource conditions this audit offers - not just under load.

    A `resource_inconclusive` result (SIGKILL, no exception) is ordinarily
    retried, because it may just mean this row lost a memory race against a
    concurrent worker. `POOLED_BACKTEST_OOM_LIMIT.json` holds strategies that
    stayed `resource_inconclusive` after the 2026-09-07 move to a 16GB VM
    with `--workers 1` - one process, the entire budget to itself, nothing
    left to blame but the strategy's own memory footprint. Retrying those
    further only spends another ~200s per pass confirming what is already
    confirmed.
    """
    if not OOM_LIMITS.exists():
        return {}
    return json.loads(OOM_LIMITS.read_text(encoding="utf-8"))["results"]


def stake_overflows() -> dict:
    """Strategies confirmed to fail from unbounded stake growth, not a limit.

    `profile_futures_config.json` sets `stake_amount: unlimited`, so a
    leveraged strategy that stays profitable long enough compounds its
    wallet exponentially until a single position's computed stake exceeds
    real market liquidity and freqtrade raises. Unlike `resource_inconclusive`
    or `timeout`, this has nothing to do with memory, workers, or wall-clock
    time - a retry reproduces the identical failure at the identical point
    every time. `POOLED_BACKTEST_STAKE_OVERFLOW.json` holds the confirmation.
    """
    if not STAKE_OVERFLOWS.exists():
        return {}
    return json.loads(STAKE_OVERFLOWS.read_text(encoding="utf-8"))["results"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", action="append", default=[])
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--import-manifest", action="append", type=Path, default=[],
                        help="import identity-matching measured results from another runtime")
    parser.add_argument("--import-only", action="store_true")
    args = parser.parse_args(argv)
    rows = eligible()
    row_by_strategy = {row["strategy_id"]: row for row in rows}
    if args.strategy:
        wanted = set(args.strategy)
        rows = [row for row in rows if row["strategy_id"] in wanted]
        missing = wanted - {row["strategy_id"] for row in rows}
        if missing:
            raise SystemExit("not currently eligible: " + ", ".join(sorted(missing)))
    data = _load(args.output)
    data.pop("runtime_id", None)
    # Loaded once, so a run cannot half-apply it. Without this, every row
    # `eligibility_timeframe_repair.py` already recovered a timeframe for
    # (and the module/signature/freqAI repairs) fails again here for the
    # same reason it failed before repair - this runner reads the manifest
    # `profile_full_window.py` already reads, it just never asked before.
    overrides = profile_full_window.repair_overrides()
    # (status this strategy is retired under, its confirmation source) - checked
    # in this order so a strategy present in both is reported as its first match.
    retired = [("performance_limited", performance_limits()),
               ("oom_confirmed", oom_limits()),
               ("stake_overflow_confirmed", stake_overflows())]
    data.update({"schema_version": 1, "timerange": TIMERANGE,
                 "measurement_scope": "canonical_pooled_native_pair_universe"})

    imported = 0
    for path in args.import_manifest:
        foreign = _load(path)
        if foreign.get("timerange") != TIMERANGE:
            raise SystemExit(f"import timerange mismatch: {path}")
        for strategy, result in foreign.get("results", {}).items():
            row = row_by_strategy.get(strategy)
            if not row or result.get("status") != "measured":
                continue
            identity = profile_smoke._identity(row)
            if (result.get("measurement_scope") !=
                    "canonical_pooled_native_pair_universe" or
                    not all(result.get(key) == value for key, value in identity.items())):
                raise SystemExit(f"import identity mismatch: {strategy} from {path}")
            data["results"][strategy] = result
            imported += 1

    def refresh_runtime_ids() -> None:
        data["runtime_ids"] = sorted({
            result.get("runtime_id", "native_unversioned")
            for result in data["results"].values()
            if result.get("status") == "measured"
        })

    if args.import_manifest:
        refresh_runtime_ids()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        _write(data, args.output)
        print(f"imported measured full backtests: {imported}", flush=True)
    if args.import_only:
        return 0

    def run(row):
        strategy = row["strategy_id"]
        identity = profile_smoke._identity(row)
        previous = data["results"].get(strategy) or {}
        if (not args.force and previous.get("status") == "measured" and
                all(previous.get(key) == value for key, value in identity.items())):
            return strategy, previous, True
        if not args.force and previous.get("status") in {status for status, _ in retired}:
            return strategy, previous, True
        for status, confirmations in retired:
            if strategy not in confirmations:
                continue
            # Confirmed unable to reach `measured` under the best conditions
            # this runner offers (see POOLED_BACKTEST_PERFORMANCE_LIMIT.json /
            # POOLED_BACKTEST_OOM_LIMIT.json) - applying this the first time a
            # strategy qualifies retires it without spending another attempt
            # to reconfirm what earlier ones already did.
            result = dict(identity)
            result.update({
                "status": status,
                "why": confirmations[strategy]["why"],
                "measurement_scope": "canonical_pooled_native_pair_universe",
                "attempted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            })
            if previous.get("status"):
                result["attempts"] = previous.get("attempts", []) + [{
                    "status": previous.get("status"), "why": previous.get("why"),
                    "elapsed_s": previous.get("elapsed_s"),
                    "attempted_at": previous.get("attempted_at"),
                }]
            return strategy, result, False
        mode = "futures" if row["run_profile"].startswith("futures_") else "spot"
        settings = overrides.get(strategy) or None
        result = profile_smoke.run_one(row, timerange(mode), args.timeout,
                                        config_overrides=settings)
        config = (profile_smoke.FUTURES_CONFIG if mode == "futures"
                  else profile_smoke.SPOT_CONFIG)
        result.update(identity)
        result["pairs"] = profile_smoke._read_jsonc(config)["exchange"]["pair_whitelist"]
        result["measurement_scope"] = "canonical_pooled_native_pair_universe"
        result["attempted_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        # Every earlier try this runner overwrote used to vanish outright, so a
        # strategy that needed several retries before it measured - or that
        # never does - looked identical to one that succeeded on the first
        # attempt. Carry the previous outcome forward instead of discarding it.
        if previous.get("status"):
            result["attempts"] = previous.get("attempts", []) + [{
                "status": previous.get("status"),
                "why": previous.get("why"),
                "elapsed_s": previous.get("elapsed_s"),
                "attempted_at": previous.get("attempted_at"),
            }]
        return strategy, result, False

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(run, row) for row in rows]
        for future in concurrent.futures.as_completed(futures):
            strategy, result, cached = future.result()
            with LOCK:
                data["results"][strategy] = result
                refresh_runtime_ids()
                _write(data, args.output)
            print(f"{strategy}: {'cached' if cached else result['status']} trades={result.get('trades', '')}",
                  flush=True)
    measured = sum(data["results"].get(strategy, {}).get("status") == "measured"
                   for strategy in row_by_strategy)
    print(f"canonical pooled full backtests measured: {measured}/{len(row_by_strategy)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
