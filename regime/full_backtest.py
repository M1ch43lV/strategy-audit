"""Resumable canonical pooled full-window backtests for Phase A."""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import os
import threading
from pathlib import Path

import profile_smoke


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "regime" / "full_backtest_manifest.json"
TIMERANGE = "20200301-20260821"
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
    with (ROOT / "REGIME_ELIGIBILITY.csv").open(newline="", encoding="utf-8-sig") as handle:
        allowed = {row["strategy_id"] for row in csv.DictReader(handle)
                   if row["regime_eligible"].lower() == "true"}
    return [row for row in profile_smoke.read_manifest(profile_smoke.MANIFEST)
            if row["strategy_id"] in allowed]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", action="append", default=[])
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    rows = eligible()
    if args.strategy:
        wanted = set(args.strategy)
        rows = [row for row in rows if row["strategy_id"] in wanted]
        missing = wanted - {row["strategy_id"] for row in rows}
        if missing:
            raise SystemExit("not currently eligible: " + ", ".join(sorted(missing)))
    data = _load(args.output)
    data.update({"schema_version": 1, "timerange": TIMERANGE,
                 "measurement_scope": "canonical_pooled_native_pair_universe",
                 "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned")})

    def run(row):
        strategy = row["strategy_id"]
        identity = profile_smoke._identity(row)
        previous = data["results"].get(strategy) or {}
        if (not args.force and previous.get("status") == "measured" and
                all(previous.get(key) == value for key, value in identity.items())):
            return strategy, previous, True
        result = profile_smoke.run_one(row, TIMERANGE, args.timeout)
        mode = "futures" if row["run_profile"].startswith("futures_") else "spot"
        config = (profile_smoke.FUTURES_CONFIG if mode == "futures"
                  else profile_smoke.SPOT_CONFIG)
        result.update(identity)
        result["pairs"] = profile_smoke._read_jsonc(config)["exchange"]["pair_whitelist"]
        result["measurement_scope"] = "canonical_pooled_native_pair_universe"
        return strategy, result, False

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(run, row) for row in rows]
        for future in concurrent.futures.as_completed(futures):
            strategy, result, cached = future.result()
            with LOCK:
                data["results"][strategy] = result
                _write(data, args.output)
            print(f"{strategy}: {'cached' if cached else result['status']} trades={result.get('trades', '')}",
                  flush=True)
    measured = sum(row.get("status") == "measured" for row in data["results"].values())
    print(f"canonical pooled full backtests measured: {measured}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
