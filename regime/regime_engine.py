"""Generate the frozen causal daily regime dataset from local audit candles."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import talib

from .episodes import build_episodes, build_transitions, episode_ids
from .features import asset_features, classify_dmi, signed_efficiency_ratio, wilder_dmi


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "user_data" / "data" / "binance"
OUT = ROOT / "results" / "regime"
PAIRS = ("BTC", "ETH", "LTC", "XRP", "ADA", "XLM", "XMR", "DASH")
START = pd.Timestamp("2020-03-01T00:00:00Z")
END = pd.Timestamp("2026-08-21T00:00:00Z")


def _input(pair: str, datadir: Path) -> Path:
    return datadir / f"{pair}_USDT-1d.feather"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256_" + digest.hexdigest()


def build(datadir: Path = DATA) -> tuple[pd.DataFrame, dict]:
    assets = {}
    fingerprints = {}
    for symbol in PAIRS:
        path = _input(symbol, datadir)
        candles = pd.read_feather(path, columns=["date", "open", "high", "low", "close", "volume"])
        candles["date"] = pd.to_datetime(candles["date"], utc=True)
        assets[symbol] = asset_features(candles)
        fingerprints[path.name] = _sha(path)

    btc = assets["BTC"].rename(columns={
        col: "btc_" + col for col in assets["BTC"].columns if col not in ("date", "close")
    }).drop(columns="close")
    rows = []
    for symbol in PAIRS:
        coin = assets[symbol].rename(columns={
            col: "coin_" + col for col in assets[symbol].columns if col not in ("date", "close")
        }).drop(columns="close")
        merged = coin.merge(btc, on="date", how="left", validate="many_to_one")
        merged.insert(1, "pair", f"{symbol}/USDT")
        merged["rs_30d"] = merged["coin_return_30d"] - merged["btc_return_30d"]
        merged["rs_90d"] = merged["coin_return_90d"] - merged["btc_return_90d"]
        rows.append(merged[(merged["date"] >= START) & (merged["date"] < END)])
    daily = pd.concat(rows, ignore_index=True).sort_values(["date", "pair"]).reset_index(drop=True)

    active = daily[daily["coin_regime"] != "WARMUP"]
    breadth = (active.assign(
        plus=lambda x: x["coin_plus_di"].gt(x["coin_minus_di"]),
        trending=lambda x: x["coin_adx"].ge(25.0),
        bull=lambda x: x["coin_regime"].eq("BULL"),
        bear=lambda x: x["coin_regime"].eq("BEAR"),
    ).groupby("date").agg(
        breadth_available_coins=("pair", "size"),
        pct_coins_plus_di_gt_minus_di=("plus", "mean"),
        pct_coins_adx_ge_25=("trending", "mean"),
        pct_coins_bull_state=("bull", "mean"),
        pct_coins_bear_state=("bear", "mean"),
    ).reset_index())
    daily = daily.merge(breadth, on="date", how="left", validate="many_to_one")
    btc_dates = (daily[["date", "btc_regime"]].drop_duplicates("date")
                 .sort_values("date").reset_index(drop=True))
    btc_dates["btc_episode_id"] = episode_ids(
        btc_dates["date"], btc_dates["btc_regime"], "BTC")
    daily = daily.merge(btc_dates[["date", "btc_episode_id"]], on="date",
                        how="left", validate="many_to_one")
    daily["coin_episode_id"] = ""
    for pair, index in daily.groupby("pair", sort=True).groups.items():
        group = daily.loc[index].sort_values("date")
        symbol = pair.split("/", 1)[0]
        daily.loc[group.index, "coin_episode_id"] = episode_ids(
            group["date"], group["coin_regime"], symbol).to_numpy()
    manifest = {
        "schema_version": 1,
        "parameters": {"dmi_period": 14, "adx_bull_bear": 25.0,
                       "adx_sideways": 20.0, "ser_period": 30,
                       "return_periods": [30, 90], "realized_vol_period": 30,
                       "annualization_days": 365, "availability_lag_days": 1},
        "window_start": START.isoformat(), "window_end_exclusive": END.isoformat(),
        "pairs": [f"{p}/USDT" for p in PAIRS], "input_sha256": fingerprints,
        "runtime_versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                             "pandas": pd.__version__, "ta_lib": talib.__version__},
    }
    return daily, manifest


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    copy = frame.copy()
    for col in copy.select_dtypes(include=["datetime", "datetimetz"]).columns:
        copy[col] = copy[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    copy.to_csv(path, index=False, lineterminator="\n", float_format="%.12g")


def write_outputs(daily: pd.DataFrame, manifest: dict, outdir: Path = OUT) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    _write_csv(daily, outdir / "regime_daily.csv")
    _write_csv(build_episodes(daily), outdir / "regime_episodes.csv")
    btc_daily = (daily[["date", "btc_regime"]].drop_duplicates("date")
                 .rename(columns={"btc_regime": "coin_regime"}))
    _write_csv(build_episodes(btc_daily.assign(pair="BTC_GLOBAL")),
               outdir / "regime_btc_episodes.csv")
    _write_csv(build_transitions(daily), outdir / "regime_transitions.csv")
    states = (daily.groupby(["pair", "btc_regime", "coin_regime"], dropna=False)
              .size().rename("days").reset_index())
    _write_csv(states, outdir / "regime_state_summary.csv")
    numeric = [c for c in daily.columns if c.startswith(("btc_", "coin_", "rs_", "pct_"))
               and pd.api.types.is_numeric_dtype(daily[c])]
    distributions = (daily.groupby("pair")[numeric]
                     .agg(["count", "mean", "std", "min", "median", "max"]))
    distributions.columns = [f"{a}__{b}" for a, b in distributions.columns]
    _write_csv(distributions.reset_index(), outdir / "regime_feature_distributions.csv")
    manifest["output_sha256"] = {
        path.name: _sha(path) for path in sorted(outdir.glob("regime_*.csv"))
    }
    (outdir / "regime_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def selftest() -> None:
    n = 240
    dates = pd.date_range("2020-01-01", periods=n, tz="UTC")
    def frame(close):
        close = np.asarray(close, dtype=float)
        return pd.DataFrame({"date": dates, "open": close, "high": close + 1,
                             "low": close - 1, "close": close, "volume": 1.0})
    up = asset_features(frame(np.arange(n) + 100.0))
    down = asset_features(frame(500.0 - np.arange(n)))
    wave = asset_features(frame(100.0 + np.sin(np.arange(n) * np.pi / 2)))
    assert (up["regime"].iloc[80:] == "BULL").mean() > 0.9
    assert (down["regime"].iloc[80:] == "BEAR").mean() > 0.9
    assert (wave["regime"].iloc[100:] == "SIDEWAYS").mean() > 0.7
    # Lag: changing candle D cannot change the feature attached to date D.
    altered = frame(np.arange(n) + 100.0)
    altered.loc[120:, ["open", "high", "low", "close"]] *= 10
    other = asset_features(altered)
    causal_columns = [column for column in up if column not in ("date", "close")]
    pd.testing.assert_frame_equal(up.loc[:120, causal_columns],
                                  other.loc[:120, causal_columns])
    pd.testing.assert_series_equal(up["date"], other["date"])
    # ``close`` is deliberately retained only inside asset_features for return
    # calculation and must differ at the mutation boundary. build() drops it
    # from the published dataset, so no unlagged OHLCV value can leak onward.
    assert up.loc[120, "close"] != other.loc[120, "close"]
    print("regime engine selftest: PASS")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datadir", type=Path, default=DATA)
    parser.add_argument("--outdir", type=Path, default=OUT)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    daily, manifest = build(args.datadir)
    write_outputs(daily, manifest, args.outdir)
    print(f"regime daily rows: {len(daily)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
