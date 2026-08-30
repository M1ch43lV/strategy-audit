# -*- coding: utf-8 -*-
"""Freeze and run file-derived Wave B recovery startup values sequentially."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys

import eligibility_warmup


ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_WARMUP_RECOVERY.csv")

# Values not represented by the original literal timeperiod/window audit.
# Each basis names the finite dependency visible in the canonical source.
OVERRIDES = {
    "AlwaysBuy": (1, "row-local; no history dependency"),
    "HourBasedStrategy_5m": (1, "row-local timestamp minute only"),
    "AwesomeMacd": (34, "TA-Lib default MACD 12/26/9 complete nominal lookback"),
    "Diamond": (11, "maximum shift 10 plus crossover predecessor"),
    "ASDTSRockwellTrading": (34, "TA-Lib default MACD 12/26/9 complete nominal lookback"),
    "Macd": (816, "34 daily MACD candles converted to 24 hourly base candles each"),
    "MACDStrategyADA": (34, "TA-Lib default MACD 12/26/9 dominates default CCI 14"),
    "MACDStrategyAVAX": (34, "TA-Lib default MACD 12/26/9 dominates default CCI 14"),
    "MACDStrategyBTC": (34, "TA-Lib default MACD 12/26/9 dominates default CCI 14"),
    "MACDStrategyENJ": (34, "TA-Lib default MACD 12/26/9 dominates default CCI 14"),
    "MACDStrategyETC": (34, "TA-Lib default MACD 12/26/9 dominates default CCI 14"),
    "MACDStrategySOL": (34, "TA-Lib default MACD 12/26/9 dominates default CCI 14"),
    "MACDStrategyXRP": (34, "TA-Lib default MACD 12/26/9 dominates default CCI 14"),
    "BinHV45_kanaxe": (40, "literal rolling Bollinger window_size 40"),
    "BinHV45_stash": (40, "literal rolling Bollinger window_size 40"),
    "BinHV45_werkkrew": (40, "literal rolling Bollinger window_size 40"),
    "CombinedBinHAndClucHyperV0": (91, "loaded sell Bollinger 91 dominates loaded EMA 50 and rolling 30"),
    "CombinedBinHAndClucHyperV3": (91, "loaded sell Bollinger 91 dominates loaded EMA 50, rolling 30, ATR 14"),
    "SlowPotato": (1440, "literal rolling mean window 1440"),
    "Trend_Strength_Directional": (74, "loaded DI 74 dominates ADX 41 and RSI 14"),
    "e6v34": (100, "literal volume EMA 100 dominates HMA 35 and WILLR 12"),
    "MabStra": (28, "loaded slow SMA 28 dominates fast 14 and mojo 7"),
    "TouchEmaStrategy": (60, "loaded EMA period 60 plus one-row decision shift"),
    "TouchEmaDelayStrategy": (50, "loaded EMA period 50 plus one-row decision shift"),
    "GKD_Baseline": (20, "active EMA baseline 20 dominates ATR 14"),
    "GKD_BaselineAllMAs": (20, "active EMA baseline 20 dominates ATR 14"),
    "GKD_HurstExponent": (69, "Hurst 64 over shifted returns plus EMA smoothing 5"),
    "GKD_PFE": (24, "PFE 10 plus smoothing 5; baseline EMA 20 and ATR 14"),
    "HilbertSineWave": (5, "documented Hilbert smoothing period 5"),
    "OmaGann": (10, "loaded OMA length 10"),
    "bbandrsi": (20, "literal Bollinger 20 dominates RSI 14"),
}

# These calculations depend on the complete prefix and have no finite startup
# boundary to recover. Their startup=1 FOUND result is terminal for E1.
UNBOUNDED = {
    "FVGChannel": "iterative filtered_close and level state depend on the complete prefix",
    "ForexRobootSuperScalper": "OBV/direction are cumulative over the complete prefix",
    "HSI": "Heikin-Ashi open is recursive over the complete prefix",
}


def _sha(path):
    return "sha256_" + hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def _audited_period(strategy):
    path = os.path.join(ROOT, "corpus", strategy + ".md")
    if not os.path.exists(path):
        return None
    text = io.open(path, encoding="utf-8", errors="replace").read()
    match = re.search(r"(\d+)\s+[^,\r\n]+,\s*startup_candle_count", text)
    return int(match.group(1)) if match else None


def rows():
    result = []
    for profile in eligibility_warmup.candidates():
        strategy = profile["strategy_id"]
        canonical = os.path.join(ROOT, profile["canonical_file"].replace("/", os.sep))
        if strategy in UNBOUNDED:
            startup = ""
            state = "terminal_unbounded_prefix_dependency"
            basis = UNBOUNDED[strategy]
        elif strategy in OVERRIDES:
            startup, basis = OVERRIDES[strategy]
            state = "recovery_frozen" if startup > 1 else "startup_1_sufficient"
        else:
            startup = _audited_period(strategy)
            if startup is None:
                raise ValueError("missing file-derived recovery value: %s" % strategy)
            state = "recovery_frozen"
            basis = "canonical corpus static audit longest literal indicator period %d" % startup
        result.append({
            "strategy_id": strategy,
            "implementation_id": profile["implementation_id"],
            "canonical_sha256": _sha(canonical),
            "recovery_startup_candle_count": startup,
            "recovery_state": state,
            "derivation_basis": basis,
        })
    return result


def write_manifest(path=OUTPUT):
    data = rows()
    fields = list(data[0])
    with io.open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)
    print("warmup recovery manifest: %d rows" % len(data))


def run(timeout):
    profiles = {row["strategy_id"]: row for row in eligibility_warmup.candidates()}
    data = eligibility_warmup._load(eligibility_warmup.OUTPUT)
    queued = [row for row in rows() if row["recovery_state"] == "recovery_frozen"]
    for number, item in enumerate(queued, 1):
        strategy = item["strategy_id"]
        startup = int(item["recovery_startup_candle_count"])
        attempts = (data["results"].get(strategy) or {}).get("attempts", {})
        key = str(startup)
        if key in attempts:
            continue
        print("[%d/%d] %s recursive recovery startup=%d" %
              (number, len(queued), strategy, startup), flush=True)
        result = eligibility_warmup.run_one(profiles[strategy], timeout, startup)
        attempts[key] = result
        data["results"][strategy] = {
            "attempts": attempts,
            "latest_startup_candle_count": startup,
        }
        eligibility_warmup._write_json(eligibility_warmup.OUTPUT, data)
        print("  %s: %s" % (result["status"], result["why"]), flush=True)
    print("warmup recovery queue complete")


def selftest():
    inventory = rows()
    assert len(inventory) == 82
    assert len({row["strategy_id"] for row in inventory}) == 82
    assert next(row for row in inventory if row["strategy_id"] == "SlowPotato")[
        "recovery_startup_candle_count"] == 1440
    assert next(row for row in inventory if row["strategy_id"] == "HSI")[
        "recovery_state"] == "terminal_unbounded_prefix_dependency"
    print("eligibility_warmup_recovery selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.write_manifest:
        write_manifest()
    if args.run:
        run(args.timeout)
    if not args.write_manifest and not args.run:
        parser.error("choose --write-manifest and/or --run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
