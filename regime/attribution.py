"""Attribute canonical Freqtrade trades to causal BTC and coin regimes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

import profile_smoke


ROOT = Path(__file__).resolve().parents[1]
DAILY = ROOT / "results" / "regime" / "regime_daily.csv"
OUT = ROOT / "results" / "regime"
FULL_MANIFEST = OUT / "full_backtest_manifest.json"
START = pd.Timestamp("2020-03-01T00:00:00Z")
END = pd.Timestamp("2026-08-21T00:00:00Z")
MEASUREMENT_SCOPE = "canonical_pooled_native_pair_universe"


def _sha(data: bytes) -> str:
    return "sha256_" + hashlib.sha256(data).hexdigest()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256_" + digest.hexdigest()


def eligible_profiles() -> dict[str, dict]:
    with (ROOT / "REGIME_ELIGIBILITY.csv").open(newline="", encoding="utf-8-sig") as handle:
        eligibility = {row["strategy_id"]: row for row in csv.DictReader(handle)
                       if row["regime_eligible"].lower() == "true"}
    with (ROOT / "EXECUTION_PROFILES.csv").open(newline="", encoding="utf-8-sig") as handle:
        profiles = {row["strategy_id"]: row for row in csv.DictReader(handle)
                    if row["strategy_id"] in eligibility}
    return profiles


def _result_member(names: list[str]) -> str | None:
    candidates = [name for name in names if name.endswith(".json")
                  and not name.endswith("_config.json") and "meta" not in name.lower()]
    return sorted(candidates, key=len)[0] if candidates else None


def read_archive(path: Path, profiles: dict[str, dict]) -> list[dict]:
    records = []
    try:
        with zipfile.ZipFile(path) as archive:
            member = _result_member(archive.namelist())
            if not member:
                return records
            result = json.loads(archive.read(member))
            config_names = [name for name in archive.namelist()
                            if name.endswith("_config.json")]
            config_bytes = archive.read(config_names[0]) if config_names else b""
            for strategy, summary in (result.get("strategy") or {}).items():
                profile = profiles.get(strategy)
                if not profile:
                    continue
                source_names = [name for name in archive.namelist()
                                if name.endswith(f"_{strategy}.py")]
                source_sha = _sha(archive.read(source_names[0])) if source_names else ""
                expected = profile["source_sha256"]
                records.append({
                    "strategy_id": strategy, "archive": path, "summary": summary,
                    "source_sha256": source_sha, "source_match": source_sha == expected,
                    "config_sha256": _sha(config_bytes) if config_bytes else "",
                    "start": pd.to_datetime(summary.get("backtest_start"), utc=True),
                    "end": pd.to_datetime(summary.get("backtest_end"), utc=True),
                    "trades": summary.get("trades") or [],
                    "mode": summary.get("trading_mode", "spot"),
                })
    except (OSError, ValueError, zipfile.BadZipFile, KeyError):
        return []
    return records


def archive_inventory(search_root: Path, profiles: dict[str, dict],
                      archive_paths: list[Path] | None = None) -> tuple[list[dict], list[dict]]:
    accepted, rejected = [], []
    seen = set()
    paths = sorted(archive_paths) if archive_paths is not None else sorted(search_root.rglob("*.zip"))
    for path in paths:
        for record in read_archive(path, profiles):
            profile = profiles[record["strategy_id"]]
            expected_mode = "futures" if profile["run_profile"].startswith("futures_") else "spot"
            config_path = (profile_smoke.FUTURES_CONFIG if expected_mode == "futures"
                           else profile_smoke.SPOT_CONFIG)
            expected_pairs = set(profile_smoke._read_jsonc(config_path)["exchange"]["pair_whitelist"])
            actual_pairs = set(record["summary"].get("pairlist") or [])
            reason = ""
            if not record["source_match"]:
                reason = "canonical_source_hash_mismatch"
            elif record["mode"] != expected_mode:
                reason = "native_mode_mismatch"
            elif (profile["execution_timeframe"] and
                  record["summary"].get("timeframe") != profile["execution_timeframe"]):
                reason = "execution_timeframe_mismatch"
            elif actual_pairs != expected_pairs:
                reason = "not_canonical_pooled_pair_universe"
            elif pd.isna(record["start"]) or pd.isna(record["end"]):
                reason = "missing_backtest_window"
            if reason:
                rejected.append({"strategy_id": record["strategy_id"],
                                 "archive": str(record["archive"].relative_to(ROOT)),
                                 "reason": reason})
                continue
            # De-duplicate exports of the same semantic trade set.
            digest = hashlib.sha256(json.dumps(record["trades"], sort_keys=True).encode()).hexdigest()
            key = (record["strategy_id"], digest)
            if key not in seen:
                accepted.append(record)
                seen.add(key)
    return accepted, rejected


def attribute(archives: list[dict], daily_path: Path = DAILY) -> pd.DataFrame:
    states = pd.read_csv(daily_path, parse_dates=["date"])
    btc_fields = ["btc_regime", "btc_adx", "btc_ser_30", "btc_return_90d",
                  "btc_realized_vol_30d", "btc_episode_id"]
    coin_fields = ["coin_regime", "coin_adx", "coin_ser_30", "coin_return_90d",
                   "coin_realized_vol_30d", "rs_30d", "rs_90d", "coin_episode_id"]
    keep = ["date", "pair"] + btc_fields + coin_fields
    states = states[keep].set_index(["pair", "date"])
    rows = []
    seen_trades = set()
    for archive in archives:
        for ordinal, trade in enumerate(archive["trades"]):
            opened = pd.to_datetime(trade["open_date"], utc=True)
            if not (START <= opened < END):
                continue
            semantic_key = (
                archive["strategy_id"], trade.get("pair"), trade.get("open_timestamp"),
                trade.get("close_timestamp"), bool(trade.get("is_short", False)),
                trade.get("open_rate"), trade.get("close_rate"), trade.get("profit_abs"),
            )
            if semantic_key in seen_trades:
                continue
            seen_trades.add(semantic_key)
            pair = trade["pair"].split(":", 1)[0]
            day = opened.normalize()
            pair_key = (pair, day)
            pair_state = states.loc[pair_key] if pair_key in states.index else None
            btc_key = ("BTC/USDT", day)
            btc_state = pair_state
            if btc_state is None and btc_key in states.index:
                btc_state = states.loc[btc_key]
            row = {
                "strategy_id": archive["strategy_id"], "pair": trade["pair"],
                "trade_ordinal": ordinal, "open_date": opened,
                "close_date": pd.to_datetime(trade.get("close_date"), utc=True),
                "is_short": bool(trade.get("is_short", False)),
                "profit_ratio": float(trade.get("profit_ratio", np.nan)),
                "profit_abs": float(trade.get("profit_abs", np.nan)),
                "trade_duration": trade.get("trade_duration"),
                "enter_tag": trade.get("enter_tag") or "",
                "exit_reason": trade.get("exit_reason") or "",
                "btc_regime_match": btc_state is not None,
                "coin_regime_match": pair_state is not None,
                "regime_match": btc_state is not None and pair_state is not None,
            }
            if btc_state is not None:
                row.update({field: btc_state[field] for field in btc_fields})
            if pair_state is not None:
                row.update({field: pair_state[field] for field in coin_fields})
            rows.append(row)
    return pd.DataFrame(rows)


def _summarize(trades: pd.DataFrame, keys: list[str], match_column: str) -> pd.DataFrame:
    matched = trades[trades[match_column]].copy()
    if matched.empty:
        return pd.DataFrame(columns=keys + ["trades"])
    matched["win_profit"] = matched["profit_abs"].clip(lower=0)
    matched["loss_profit"] = -matched["profit_abs"].clip(upper=0)
    grouped = matched.groupby(keys, dropna=False)
    result = grouped.agg(
        trades=("profit_abs", "size"), long_trades=("is_short", lambda x: int((~x).sum())),
        short_trades=("is_short", "sum"), profit_abs=("profit_abs", "sum"),
        mean_profit_ratio=("profit_ratio", "mean"), wins=("profit_abs", lambda x: int((x > 0).sum())),
        gross_profit=("win_profit", "sum"), gross_loss=("loss_profit", "sum"),
        mean_duration_minutes=("trade_duration", "mean"),
        active_dates=("open_date", lambda x: x.dt.normalize().nunique()),
    ).reset_index()
    result["profit_factor"] = result["gross_profit"] / result["gross_loss"].replace(0.0, np.nan)
    result["win_rate"] = result["wins"] / result["trades"]
    return result


def summarize(trades: pd.DataFrame) -> pd.DataFrame:
    return _summarize(trades, ["strategy_id", "btc_regime", "coin_regime"],
                      "regime_match")


def summarize_btc(trades: pd.DataFrame) -> pd.DataFrame:
    return _summarize(trades, ["strategy_id", "btc_regime"], "btc_regime_match")


def summarize_episodes(trades: pd.DataFrame) -> pd.DataFrame:
    matched = trades[trades["btc_regime_match"]].copy()
    if matched.empty:
        return pd.DataFrame(columns=["strategy_id", "btc_regime", "episodes"])
    by_episode = (matched.groupby(["strategy_id", "btc_regime", "btc_episode_id"])
                  ["profit_abs"].sum().rename("episode_profit").reset_index())
    return (by_episode.groupby(["strategy_id", "btc_regime"])
            .agg(episodes=("btc_episode_id", "nunique"),
                 positive_episodes=("episode_profit", lambda x: int((x > 0).sum())),
                 negative_episodes=("episode_profit", lambda x: int((x < 0).sum())),
                 median_episode_profit=("episode_profit", "median"),
                 worst_episode_profit=("episode_profit", "min"),
                 best_episode_profit=("episode_profit", "max"))
            .reset_index().assign(
                episode_win_rate=lambda x: x["positive_episodes"] / x["episodes"]))


def _write(frame: pd.DataFrame, path: Path) -> None:
    copy = frame.copy()
    for col in copy.select_dtypes(include=["datetime", "datetimetz"]).columns:
        copy[col] = copy[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    copy.to_csv(path, index=False, lineterminator="\n", float_format="%.12g")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-root", type=Path, default=ROOT / "user_data")
    parser.add_argument("--outdir", type=Path, default=OUT)
    parser.add_argument("--full-manifest", type=Path, default=FULL_MANIFEST)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    profiles = eligible_profiles()
    archive_paths = None
    manifest_rejections = []
    evidence_source = "bootstrap_archive_scan"
    if args.full_manifest.exists():
        full = json.loads(args.full_manifest.read_text(encoding="utf-8"))
        archive_paths = []
        for strategy, row in full["results"].items():
            if strategy not in profiles or row.get("status") != "measured":
                continue
            path = ROOT / row.get("archive", "")
            identity = profile_smoke._identity(profiles[strategy])
            reason = ""
            if not row.get("archive") or not path.is_file():
                reason = "manifest_archive_missing"
            elif row.get("measurement_scope") != MEASUREMENT_SCOPE:
                reason = "manifest_measurement_scope_mismatch"
            elif any(row.get(key) != value for key, value in identity.items()):
                reason = "manifest_identity_mismatch"
            elif _file_sha(path) != row.get("archive_sha256"):
                reason = "manifest_archive_hash_mismatch"
            if reason:
                manifest_rejections.append({"strategy_id": strategy,
                                            "archive": row.get("archive", ""),
                                            "reason": reason})
            else:
                archive_paths.append(path)
        evidence_source = str(args.full_manifest.relative_to(ROOT))
    accepted, rejected = archive_inventory(args.search_root, profiles, archive_paths)
    rejected = manifest_rejections + rejected
    trades = attribute(accepted)
    args.outdir.mkdir(parents=True, exist_ok=True)
    _write(trades, args.outdir / "trade_regime_attribution.csv")
    _write(summarize_btc(trades), args.outdir / "strategy_btc_regime_summary.csv")
    _write(summarize(trades), args.outdir / "strategy_regime_summary.csv")
    _write(summarize_episodes(trades), args.outdir / "strategy_episode_summary.csv")
    covered = sorted(set(trades["strategy_id"])) if not trades.empty else []
    btc_matched = int(trades["btc_regime_match"].sum()) if not trades.empty else 0
    coin_matched = int(trades["coin_regime_match"].sum()) if not trades.empty else 0
    unmatched_coin_pairs = ({str(pair): int(count) for pair, count in
                             trades.loc[~trades["coin_regime_match"], "pair"]
                             .value_counts().items()} if not trades.empty else {})
    evidence = {
        "schema_version": 1, "eligible_profiles": len(profiles),
        "attributed_profiles": len(covered), "attributed_strategies": covered,
        "missing_strategies": sorted(set(profiles) - set(covered)),
        "accepted_archives": len(accepted),
        "accepted_archive_evidence": [{
            "strategy_id": row["strategy_id"],
            "archive": str(row["archive"].relative_to(ROOT)),
            "source_sha256": row["source_sha256"],
            "config_sha256": row["config_sha256"],
            "timeframe": row["summary"].get("timeframe"),
            "pairlist": row["summary"].get("pairlist") or [],
            "mode": row["mode"], "start": row["start"].isoformat(),
            "end": row["end"].isoformat(),
        } for row in accepted],
        "evidence_scope": ("Phase A descriptive attribution; source, native mode, and "
                           "timeframe plus manifest source/config identity and archive "
                           "digest are verified. Stage 9+ runs require a separately "
                           "locked runtime/config/data manifest."),
        "archive_selection_source": evidence_source,
        "rejected_archives": rejected,
        "trades": len(trades),
        "btc_regime_matched_trades": btc_matched,
        "coin_regime_matched_trades": coin_matched,
        "coin_regime_unmatched_trades": len(trades) - coin_matched,
        "coin_regime_unmatched_by_pair": unmatched_coin_pairs,
    }
    (args.outdir / "attribution_manifest.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"attributed {len(trades)} trades for {len(covered)}/{len(profiles)} eligible profiles")
    return 0


def selftest() -> None:
    with __import__("tempfile").TemporaryDirectory() as directory:
        path = Path(directory) / "daily.csv"
        pd.DataFrame({
            "date": ["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"],
            "pair": ["BTC/USDT", "BTC/USDT"],
            "btc_regime": ["BULL", "BEAR"], "coin_regime": ["BULL", "BEAR"],
            "btc_adx": [30, 31], "coin_adx": [30, 31],
            "btc_ser_30": [.5, -.5], "coin_ser_30": [.5, -.5],
            "btc_return_90d": [.2, -.2], "coin_return_90d": [.2, -.2],
            "btc_realized_vol_30d": [.5, .6], "coin_realized_vol_30d": [.5, .6],
            "rs_30d": [0, 0], "rs_90d": [0, 0],
            "btc_episode_id": ["BTC-1", "BTC-2"],
            "coin_episode_id": ["BTC-1", "BTC-2"],
        }).to_csv(path, index=False)
        trade = {"pair": "BTC/USDT:USDT", "open_date": "2024-01-01T12:00:00Z",
                 "close_date": "2024-01-02T12:00:00Z", "open_timestamp": 1,
                 "close_timestamp": 2, "is_short": False, "open_rate": 1,
                 "close_rate": 2, "profit_ratio": 1, "profit_abs": 1,
                 "trade_duration": 1440}
        xmr_trade = dict(trade, pair="XMR/USDT:USDT", open_timestamp=3,
                         close_timestamp=4)
        archive = {"strategy_id": "S", "archive": ROOT / "dummy.zip",
                   "trades": [trade, xmr_trade]}
        rows = attribute([archive, archive], path)
        assert len(rows) == 2
        assert rows.iloc[0]["btc_regime"] == "BULL"
        assert rows["btc_regime_match"].all()
        assert rows["coin_regime_match"].tolist() == [True, False]
        assert int(summarize_btc(rows)["trades"].sum()) == 2
        assert int(summarize(rows)["trades"].sum()) == 1
        assert _file_sha(path) == _sha(path.read_bytes())
    print("regime attribution selftest: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
