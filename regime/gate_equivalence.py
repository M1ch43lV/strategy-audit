"""Integration-test that an ungated adapter preserves Freqtrade trades exactly."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import profile_smoke


ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ("MacdStrategy", "RegimeFilterStrategy", "FAdxSmaStrategy",
            "FSupertrendStrategy", "momentum")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", action="append", default=[])
    parser.add_argument("--timerange", default="20200301-20200401")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results" / "regime" / "gate_equivalence.json")
    args = parser.parse_args(argv)
    selected = args.strategy or list(DEFAULTS)
    profiles = {row["strategy_id"]: row
                for row in profile_smoke.read_manifest(profile_smoke.MANIFEST)}
    results = []
    with tempfile.TemporaryDirectory() as directory:
        config_path = Path(directory) / "ungated.json"
        config_path.write_text(json.dumps({"mode": "ungated"}), encoding="utf-8")
        for strategy in selected:
            row = profiles[strategy]
            base = profile_smoke.run_one(row, args.timerange, args.timeout)
            gated = profile_smoke.run_one(
                row, args.timerange, args.timeout,
                extra_env={"REGIME_GATE_CONFIG": str(config_path)})
            match = (base.get("status") == gated.get("status") == "measured" and
                     base.get("trades_sha256") == gated.get("trades_sha256"))
            results.append({"strategy_id": strategy, "run_profile": row["run_profile"],
                            "timerange": args.timerange, "baseline": base,
                            "ungated_adapter": gated, "exact_trade_match": match})
            print(f"{strategy}: {'PASS' if match else 'FAIL'}")
    payload = {"schema_version": 1, "results": results,
               "all_exact": all(row["exact_trade_match"] for row in results)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["all_exact"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
