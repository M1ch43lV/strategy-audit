# -*- coding: utf-8 -*-
"""Exploratory E3 arm: re-measure trailing-stop strategies with trailing off.

Freqtrade cannot see the price path inside a candle, so a trailing stop is the
one exit mechanism a backtest can only approximate. This arm answers a single
question: how far do conclusions move when that mechanism is removed?

Nothing here is confirmatory. The canonical arm is never re-run and never
rewritten; the strategy sources are never edited. Trailing is disabled through
the configuration, which `StrategyResolver` applies over the strategy attribute,
so each canonical source keeps its hash and only the effective config differs.
"""
from __future__ import annotations

import argparse
import ast
import csv
import io
import json
import os
import sys
import zipfile

import profile_full_window
import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
CANONICAL = os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json")
OUTPUT = os.path.join(ROOT, "results", "regime", "trailing_sensitivity.json")
TIMERANGE = profile_full_window.TIMERANGE
METRICS = ("total_trades", "profit_total", "profit_total_abs",
           "max_drawdown_account", "cagr", "sharpe", "sortino", "winrate")
TRAILING_FIELDS = ("trailing_stop", "trailing_stop_positive",
                   "trailing_stop_positive_offset",
                   "trailing_only_offset_is_reached")


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _load(path):
    if not os.path.exists(path):
        return {"schema_version": 1, "timerange": TIMERANGE,
                "arm": "E3_exploratory_trailing_disabled", "results": {}}
    return json.load(io.open(path, encoding="utf-8"))


def _write(path, data):
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def declared_trailing(path):
    """Read the effective class-body trailing settings of a strategy file.

    The last assignment wins, mirroring Python's own semantics: several authors
    paste a hyperopt block below their original values, so an early
    ``trailing_stop = False`` can be overridden further down the class body.
    """
    tree = ast.parse(io.open(path, encoding="utf-8", errors="replace").read())
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for statement in node.body:
            if not isinstance(statement, ast.Assign):
                continue
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in TRAILING_FIELDS:
                    try:
                        found[target.id] = ast.literal_eval(statement.value)
                    except ValueError:
                        found[target.id] = "<dynamic>"
    return found


def _metrics(archive, strategy):
    """Pull the headline figures of one stored backtest archive."""
    if not archive or not os.path.exists(os.path.join(ROOT, archive)):
        return {}
    with zipfile.ZipFile(os.path.join(ROOT, archive)) as bundle:
        for name in bundle.namelist():
            if not name.endswith(".json") or name.endswith("_config.json"):
                continue
            data = json.loads(bundle.read(name).decode("utf-8"))
            block = (data.get("strategy") or {}).get(strategy)
            if block:
                return {key: block[key] for key in METRICS if key in block}
    return {}


def affected():
    """Measured canonical rows whose effective trailing stop is enabled."""
    canonical = json.load(io.open(CANONICAL, encoding="utf-8"))["results"]
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    rows = []
    for strategy, result in sorted(canonical.items()):
        row = profiles.get(strategy)
        if result.get("status") != "measured" or not row:
            continue
        settings = declared_trailing(
            os.path.join(ROOT, row["canonical_file"].replace("/", os.sep)))
        if settings.get("trailing_stop") is True:
            rows.append((row, result, settings))
    return rows


def run(limit, timeout):
    data = _load(OUTPUT)
    pending = [item for item in affected()
               if item[0]["strategy_id"] not in data["results"]]
    if limit:
        pending = pending[:limit]
    for number, (row, canonical, settings) in enumerate(pending, 1):
        strategy = row["strategy_id"]
        print("[%d/%d] %s trailing disabled" % (number, len(pending), strategy),
              flush=True)
        override = profile_smoke.run_one(
            row, TIMERANGE, timeout, config_overrides={"trailing_stop": False})
        identity = profile_smoke._identity(row)
        # A comparison is only meaningful against the very same canonical code
        # and pooled scope that produced the confirmatory result.
        comparable = (canonical.get("canonical_sha256") == identity["canonical_sha256"]
                      and canonical.get("measurement_scope") ==
                      "canonical_pooled_native_pair_universe")
        data["results"][strategy] = {
            "strategy_id": strategy,
            "implementation_id": row["implementation_id"],
            "run_profile": row["run_profile"],
            "declared_trailing": settings,
            "canonical": {"trades": canonical.get("trades"),
                          "trades_sha256": canonical.get("trades_sha256"),
                          "metrics": _metrics(canonical.get("archive"), strategy)},
            "trailing_disabled": dict(
                override, metrics=_metrics(override.get("archive"), strategy)),
            "canonical_comparable": comparable,
            "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned"),
            "admission_effect": "none_exploratory_E3",
        }
        _write(OUTPUT, data)
        print("  %s trades=%s (canonical %s)" %
              (override.get("status"), override.get("trades", ""),
               canonical.get("trades")), flush=True)
    print("trailing sensitivity records: %d" % len(data["results"]))


def selftest():
    rows = affected()
    assert rows, "no trailing-stop strategies selected"
    names = {row["strategy_id"] for row, _canonical, _settings in rows}
    # TGMA is not measured canonically, so it cannot enter this paired arm.
    assert "TGMA" not in names
    for _row, canonical, settings in rows:
        assert settings.get("trailing_stop") is True
        assert canonical.get("status") == "measured"
    print("trailing_sensitivity selftest: PASS (%d strategies affected)" % len(rows))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=5400)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    run(args.limit, args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
