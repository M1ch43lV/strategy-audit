"""Stage 4 structural validation for generated regime evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "regime"
STATES = {"BULL", "BEAR", "SIDEWAYS", "TRANSITION", "WARMUP"}


def _sha(path: Path) -> str:
    return "sha256_" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate(outdir: Path = OUT) -> list[str]:
    errors = []
    daily_path = outdir / "regime_daily.csv"
    manifest = json.loads((outdir / "regime_manifest.json").read_text(encoding="utf-8"))
    daily = pd.read_csv(daily_path, parse_dates=["date"])
    expected_pairs = set(manifest["pairs"])
    if set(daily["pair"]) != expected_pairs:
        errors.append("pair universe differs from manifest")
    if daily.duplicated(["pair", "date"]).any():
        errors.append("duplicate pair/date rows")
    if not set(daily["btc_regime"].dropna()).issubset(STATES):
        errors.append("unknown BTC state")
    if not set(daily["coin_regime"].dropna()).issubset(STATES):
        errors.append("unknown coin state")
    btc_cols = [c for c in daily if c.startswith("btc_")]
    for _date, group in daily.groupby("date"):
        for col in btc_cols:
            if group[col].nunique(dropna=False) > 1:
                errors.append(f"BTC feature differs across pairs: {col}")
                break
        if errors:
            break
    for name, expected in manifest["output_sha256"].items():
        if _sha(outdir / name) != expected:
            errors.append(f"output fingerprint mismatch: {name}")
    episodes = pd.read_csv(outdir / "regime_episodes.csv")
    if int(episodes["days"].sum()) != len(daily):
        errors.append("episode days do not partition daily rows")
    btc_episodes = pd.read_csv(outdir / "regime_btc_episodes.csv")
    if int(btc_episodes["days"].sum()) != daily["date"].nunique():
        errors.append("BTC episode days do not partition unique dates")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=OUT)
    args = parser.parse_args(argv)
    errors = validate(args.outdir)
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("regime validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
