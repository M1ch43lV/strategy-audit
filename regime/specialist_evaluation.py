"""Specialist and universal strategy evaluation.

Applies the choices `REGIME_PREREGISTRATION.md`'s 2026-09-11 amendment froze
- discovery/validation split, the 5-episode/10-trade specialist floor, the
exposure-matched benchmark - to a trade attribution already produced by
`regime.attribution` or `regime.gated_attribution`. See
`REGIME_AUDIT_PLAN.md` sections 17-19 for the metric and ranking design this
follows.

This module never ranks by raw return alone (excess return is always against
the exposure-matched benchmark, never absolute profit) and never collapses a
strategy's regime profile into one composite score - both explicitly ruled
out in sections 17 and 19 and the amendment itself.

Known limitation: `worst_regime_drawdown` from section 19's regime
fingerprint is not produced here. It needs an equity-curve reconstruction
per strategy per regime slice, a materially bigger feature than the rest of
this module; every other field in that fingerprint is.

Also reports a `$1000`-fixed-stake dollar total per (strategy, regime) and
per strategy overall (`total_dollar_gain_table`) - descriptive only,
alongside the benchmark-relative excess return, never a ranking input. Each
trade is priced as its own fresh $1000 stake, summed rather than
compounded: sequential reinvestment was tried and dropped (2026-09-11) once
it produced results dominated by exponential math rather than strategy
quality at a few hundred trades (e.g. one pilot strategy's $1000 became
$0.006 over ~3,000 trades) - see `_fixed_stake_gain()`.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from regime import attribution


ROOT = Path(__file__).resolve().parents[1]
CANDLE_DIR = ROOT / "user_data" / "data" / "binance"
DEFAULT_TRADES = ROOT / "results" / "regime" / "trade_regime_attribution.csv"
OUT = ROOT / "results" / "regime" / "specialist_evaluation"

# Frozen 2026-09-11: REGIME_PREREGISTRATION.md, "Amendment 2026-09-11: the
# eight OPEN pre-Stage-9 choices are resolved", entries 1 and 2.
VALIDATION_START = pd.Timestamp("2024-01-01T00:00:00Z")
MIN_EPISODES = 5
MIN_TRADES = 10

# Added 2026-09-11 per explicit user request: a purely descriptive dollar
# view alongside the benchmark-relative excess return. Never used for
# ranking or the specialist floor. Fixed stake, not compounded - see
# _fixed_stake_gain()'s docstring for why compounding was tried and dropped.
START_CAPITAL = 1000.0

TRADE_COLUMNS = [
    "strategy_id", "pair", "open_date", "close_date", "is_short",
    "profit_ratio", "profit_abs", "trade_duration",
    "btc_regime_match", "coin_regime_match", "btc_regime", "btc_episode_id",
    "coin_regime", "coin_episode_id",
]


def _candle_path(pair: str) -> Path:
    # Always the coin's own spot series, regardless of whether the strategy
    # traded it as spot or futures: the exposure-matched benchmark is an
    # opportunity-cost reference for the asset itself, not a claim about
    # futures funding mechanics.
    return CANDLE_DIR / (pair.replace("/", "_") + "-1m.feather")


def _candle_series(pair: str, cache: dict) -> pd.DataFrame | None:
    if pair in cache:
        return cache[pair]
    path = _candle_path(pair)
    if not path.is_file():
        cache[pair] = None
        return None
    frame = pd.read_feather(path, columns=["date", "close"])
    frame["date"] = pd.to_datetime(frame["date"], utc=True)
    frame = frame.sort_values("date").reset_index(drop=True)
    cache[pair] = frame
    return frame


def _detect_id_column(path: Path) -> str:
    """`regime.attribution`'s Model 0 output names the analysis unit
    `strategy_id`; `regime.gated_attribution`'s Model 1/2/3 output renames
    the same slot to `candidate_id` (one row per gated candidate, not per
    strategy - a strategy can have more than one candidate). Both are valid
    inputs here; detect which one this file has instead of requiring a
    flag."""
    header = pd.read_csv(path, nrows=0).columns
    if "strategy_id" in header:
        return "strategy_id"
    if "candidate_id" in header:
        return "candidate_id"
    raise ValueError(f"{path} has neither a strategy_id nor candidate_id column")


def load_trades(path: Path, strategies: set[str] | None = None,
                chunksize: int = 500_000) -> pd.DataFrame:
    """Streamed, optionally strategy-filtered read of a (potentially very
    large - the canonical Model 0 file is ~1.3 GB) trade attribution CSV.
    Accepts Model 0 (`strategy_id`) or Model 1/2/3 (`candidate_id`) input -
    see `_detect_id_column()` - and always returns it as `strategy_id`, the
    name every function past this point expects."""
    id_column = _detect_id_column(path)
    columns = [id_column if c == "strategy_id" else c for c in TRADE_COLUMNS]
    dtypes = {id_column: "string", "pair": "string",
              "btc_regime": "string", "coin_regime": "string",
              "btc_episode_id": "string", "coin_episode_id": "string"}
    parts = []
    for chunk in pd.read_csv(path, usecols=columns, chunksize=chunksize, dtype=dtypes):
        if id_column != "strategy_id":
            chunk = chunk.rename(columns={id_column: "strategy_id"})
        if strategies is not None:
            chunk = chunk[chunk["strategy_id"].isin(strategies)]
        if not chunk.empty:
            parts.append(chunk)
    if not parts:
        return pd.DataFrame(columns=TRADE_COLUMNS)
    trades = pd.concat(parts, ignore_index=True)
    trades["open_date"] = pd.to_datetime(trades["open_date"], utc=True)
    trades["close_date"] = pd.to_datetime(trades["close_date"], utc=True)
    return trades


def attach_benchmark(trades: pd.DataFrame) -> pd.DataFrame:
    """Exposure-matched benchmark return per trade: the coin's own spot
    buy-and-hold return over exactly the trade's own open-to-close interval
    (`REGIME_PREREGISTRATION.md` amendment, entry 3). NaN wherever the coin
    has no candle coverage for that interval - the documented XMR/USDT
    post-delisting gap is the only known case in the current corpus, and is
    left as a gap rather than imputed, the same choice `regime.attribution`
    already makes for regime state itself."""
    trades = trades.copy()
    trades["coin_pair"] = trades["pair"].str.split(":", n=1).str[0]
    trades["benchmark_return"] = np.nan
    unit = "datetime64[us, UTC]"
    cache: dict = {}

    def _asof_price(dates: pd.Series, candles: pd.DataFrame) -> pd.Series:
        # merge_asof requires identical datetime precision on both sides,
        # which candle feathers and however the caller built its trade frame
        # do not reliably agree on (ms vs us vs ns) - cast here, at the only
        # place that actually merges. Matched back to the caller's own row
        # labels (`__row__`), not by date value: two trades can legitimately
        # share an open timestamp, and a value-keyed reindex would silently
        # duplicate or drop rows where a plain integer-index match cannot.
        left = pd.DataFrame({"__row__": dates.index, "__d__": dates.astype(unit).to_numpy()})
        left = left.sort_values("__d__")
        merged = pd.merge_asof(left, candles, left_on="__d__", right_on="date",
                               direction="backward")
        return merged.set_index("__row__")["close"].reindex(dates.index)

    for pair, group in trades.groupby("coin_pair", sort=False):
        candles = _candle_series(pair, cache)
        if candles is None or candles.empty:
            continue
        unit_candles = candles.assign(date=candles["date"].astype(unit))
        open_price = _asof_price(group["open_date"], unit_candles).to_numpy()
        close_price = _asof_price(group["close_date"], unit_candles).to_numpy()
        with np.errstate(invalid="ignore", divide="ignore"):
            benchmark = close_price / open_price - 1.0
        trades.loc[group.index, "benchmark_return"] = benchmark
    return trades


def split_discovery_validation(trades: pd.DataFrame) -> pd.DataFrame:
    trades = trades.copy()
    trades["analysis_window"] = np.where(
        trades["open_date"] >= VALIDATION_START, "validation", "discovery")
    return trades


def _fixed_stake_gain(df: pd.DataFrame, value_column: str,
                      group_cols: list[str]) -> pd.Series:
    """Fixed-$1000-stake dollar P&L per group: each trade priced as its own
    fresh $1000 (`value_column * START_CAPITAL`), summed rather than
    compounded.

    Sequential reinvestment (each trade multiplying a running balance) was
    tried first and dropped: at a few hundred trades it produces results
    dominated by exponential math rather than strategy quality (one pilot
    strategy's $1000 became $0.006 over ~3,000 trades), and it implies a
    single-position-at-a-time account these strategies never ran - they
    trade up to 8 pairs concurrently. A fixed stake per trade avoids both:
    it is the total dollar P&L if you'd committed a fresh $1000 to every
    one of this group's trades, not a claim about compounded capital
    growth or the strategy's real position sizing.
    """
    if df.empty:
        return pd.Series(dtype="float64")
    return df.groupby(group_cols, dropna=False)[value_column].sum() * START_CAPITAL


def _specialist_table(trades: pd.DataFrame, regime_column: str, match_column: str,
                      episode_summary: pd.DataFrame) -> pd.DataFrame:
    validation = trades[(trades["analysis_window"] == "validation") &
                        trades[match_column]]
    if validation.empty:
        return pd.DataFrame(columns=["strategy_id", regime_column, "trades",
                                     "episodes", "mean_profit_ratio",
                                     "mean_benchmark_return", "excess_return", "tier",
                                     "dollar_gain_usd", "benchmark_dollar_gain_usd",
                                     "excess_dollar_gain_usd"])
    grouped = validation.groupby(["strategy_id", regime_column], dropna=False)
    table = grouped.agg(
        trades=("profit_ratio", "size"),
        mean_profit_ratio=("profit_ratio", "mean"),
        mean_benchmark_return=("benchmark_return", "mean"),
        benchmark_matched_trades=("benchmark_return", "count"),
    ).reset_index()
    table = table.merge(episode_summary[["strategy_id", regime_column, "episodes"]],
                        on=["strategy_id", regime_column], how="left")
    table["episodes"] = table["episodes"].fillna(0).astype(int)
    table["excess_return"] = table["mean_profit_ratio"] - table["mean_benchmark_return"]
    table["tier"] = np.where(
        (table["episodes"] >= MIN_EPISODES) & (table["trades"] >= MIN_TRADES),
        "VALIDATION", "EXPLORATORY")

    group_cols = ["strategy_id", regime_column]
    dollar_gain = _fixed_stake_gain(validation, "profit_ratio", group_cols)
    benchmark_dollar_gain = _fixed_stake_gain(
        validation.dropna(subset=["benchmark_return"]), "benchmark_return", group_cols)
    table = table.set_index(group_cols)
    table["dollar_gain_usd"] = dollar_gain
    table["benchmark_dollar_gain_usd"] = benchmark_dollar_gain
    table = table.reset_index()
    table["excess_dollar_gain_usd"] = table["dollar_gain_usd"] - table["benchmark_dollar_gain_usd"]

    return table.sort_values(["strategy_id", regime_column]).reset_index(drop=True)


def btc_specialist_table(trades: pd.DataFrame) -> pd.DataFrame:
    return _specialist_table(trades, "btc_regime", "btc_regime_match",
                             attribution.summarize_episodes(trades))


def coin_specialist_table(trades: pd.DataFrame) -> pd.DataFrame:
    return _specialist_table(trades, "coin_regime", "coin_regime_match",
                             attribution.summarize_coin_episodes(trades))


def rank_specialists(table: pd.DataFrame, regime_column: str) -> pd.DataFrame:
    """Best-per-regime ranking, `VALIDATION`-tier rows only - an
    `EXPLORATORY` row never wins a specialist ranking regardless of its
    excess return, per the specialist floor (amendment entry 2)."""
    qualified = table[table["tier"] == "VALIDATION"]
    if qualified.empty:
        return pd.DataFrame(columns=[regime_column, "rank", "strategy_id",
                                     "excess_return", "trades", "episodes"])
    rows = []
    for regime, group in qualified.groupby(regime_column):
        ranked = group.sort_values("excess_return", ascending=False).reset_index(drop=True)
        for rank, row in ranked.iterrows():
            rows.append({regime_column: regime, "rank": rank + 1,
                        "strategy_id": row["strategy_id"],
                        "excess_return": row["excess_return"],
                        "trades": row["trades"], "episodes": row["episodes"]})
    return pd.DataFrame(rows)


def universal_table(coin_table: pd.DataFrame) -> pd.DataFrame:
    """Section 19: a universal strategy is not the top-return strategy, it
    is the one with no catastrophic regime. Only assessed for a strategy that
    clears the specialist floor in every one of the four coin-regime states
    - otherwise there is not enough validation-window evidence in one of
    them to make a maximin claim at all, and the row is left out rather than
    scored on partial coverage."""
    columns = ["strategy_id", "regimes_covered", "worst_regime", "worst_regime_return",
               "median_regime_excess_return", "regime_consistency"]
    if coin_table.empty:
        return pd.DataFrame(columns=columns)
    rows = []
    for strategy, group in coin_table.groupby("strategy_id"):
        covered = set(group.loc[group["tier"] == "VALIDATION", "coin_regime"])
        if covered != {"BULL", "BEAR", "SIDEWAYS", "TRANSITION"}:
            continue
        qualified = group[group["tier"] == "VALIDATION"]
        worst = qualified.loc[qualified["excess_return"].idxmin()]
        rows.append({
            "strategy_id": strategy,
            "regimes_covered": len(covered),
            "worst_regime": worst["coin_regime"],
            "worst_regime_return": worst["excess_return"],
            "median_regime_excess_return": qualified["excess_return"].median(),
            "regime_consistency": float((qualified["excess_return"] > 0).mean()),
        })
    if not rows:
        # None of this population's strategies clear the floor in all four
        # coin regimes at once (e.g. a small, tightly-gated candidate set) -
        # a real, reportable outcome, not the same case as coin_table.empty.
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows).sort_values("worst_regime_return", ascending=False).reset_index(drop=True)


def total_dollar_gain_table(trades: pd.DataFrame) -> pd.DataFrame:
    """Per-strategy fixed-$1000-stake dollar P&L across every
    validation-window trade, regardless of regime or regime match - the
    single headline dollar figure the per-regime tables break down. Not
    gated by the specialist floor: this is a descriptive total, not a
    ranking input, so every strategy with at least one validation trade
    gets a row."""
    validation = trades[trades["analysis_window"] == "validation"]
    if validation.empty:
        return pd.DataFrame(columns=["strategy_id", "trades", "dollar_gain_usd",
                                     "benchmark_matched_trades",
                                     "benchmark_dollar_gain_usd", "excess_dollar_gain_usd"])
    counts = validation.groupby("strategy_id").size().rename("trades")
    dollar_gain = _fixed_stake_gain(validation, "profit_ratio", ["strategy_id"])
    dollar_gain.name = "dollar_gain_usd"
    benchmark_rows = validation.dropna(subset=["benchmark_return"])
    bench_counts = benchmark_rows.groupby("strategy_id").size().rename("benchmark_matched_trades")
    benchmark_dollar_gain = _fixed_stake_gain(benchmark_rows, "benchmark_return", ["strategy_id"])
    benchmark_dollar_gain.name = "benchmark_dollar_gain_usd"

    table = pd.concat([counts, dollar_gain, bench_counts, benchmark_dollar_gain], axis=1).reset_index()
    table["benchmark_matched_trades"] = table["benchmark_matched_trades"].fillna(0).astype(int)
    table["excess_dollar_gain_usd"] = table["dollar_gain_usd"] - table["benchmark_dollar_gain_usd"]
    return table.sort_values("dollar_gain_usd", ascending=False).reset_index(drop=True)


def _write(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, lineterminator="\n", float_format="%.12g")
    os.replace(temporary, path)


def selftest() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        directory_path = Path(directory)
        candles = pd.DataFrame({
            "date": pd.date_range("2020-01-01", periods=5, freq="D", tz="UTC"),
            "close": [100.0, 110.0, 121.0, 108.9, 130.0],
        })
        candles.to_feather(directory_path / "BTC_USDT-1m.feather")
        global CANDLE_DIR
        saved_dir = CANDLE_DIR
        CANDLE_DIR = directory_path
        try:
            def make(strategy, regime, ordinal, open_day, ratio, episode):
                return {
                    "strategy_id": strategy, "pair": "BTC/USDT:USDT",
                    "open_date": pd.Timestamp(open_day),
                    "close_date": pd.Timestamp(open_day) + pd.Timedelta(hours=6),
                    "is_short": False, "profit_ratio": ratio, "profit_abs": ratio * 100,
                    "trade_duration": 360,
                    "btc_regime_match": True, "coin_regime_match": True,
                    "btc_regime": regime, "btc_episode_id": episode,
                    "coin_regime": regime, "coin_episode_id": episode,
                }
            rows = []
            # 6 independent BULL episodes, 2 trades each, all in validation
            # window - clears both the episode and trade floor.
            for i in range(6):
                day = pd.Timestamp("2024-02-01", tz="UTC") + pd.Timedelta(days=i * 7)
                rows.append(make("S1", "BULL", i, day, 0.05, f"BULL-{i}"))
                rows.append(make("S1", "BULL", i, day + pd.Timedelta(hours=1), 0.03, f"BULL-{i}"))
            # Only 2 BEAR episodes for S1 - below the 5-episode floor.
            for i in range(2):
                day = pd.Timestamp("2024-05-01", tz="UTC") + pd.Timedelta(days=i * 7)
                rows.append(make("S1", "BEAR", i, day, -0.02, f"BEAR-{i}"))
            trades = pd.DataFrame(rows)
            trades = attach_benchmark(trades)
            trades = split_discovery_validation(trades)
            assert (trades["analysis_window"] == "validation").all()
            assert trades["benchmark_return"].notna().all()

            btc_table = btc_specialist_table(trades)
            bull_row = btc_table[(btc_table["strategy_id"] == "S1") &
                                 (btc_table["btc_regime"] == "BULL")].iloc[0]
            assert bull_row["episodes"] == 6
            assert bull_row["trades"] == 12
            assert bull_row["tier"] == "VALIDATION"
            bear_row = btc_table[(btc_table["strategy_id"] == "S1") &
                                 (btc_table["btc_regime"] == "BEAR")].iloc[0]
            assert bear_row["episodes"] == 2
            assert bear_row["tier"] == "EXPLORATORY"

            ranking = rank_specialists(btc_table, "btc_regime")
            assert set(ranking["btc_regime"]) == {"BULL"}
            assert ranking.iloc[0]["strategy_id"] == "S1"

            # Fixed-$1000-stake dollar gain: sum of each trade's own $1000
            # stake through the 12 BULL trades (+5%/+3% alternating, 6
            # times) - not compounded, so order doesn't matter.
            expected_bull_gain = 1000.0 * 6 * (0.05 + 0.03)
            assert abs(bull_row["dollar_gain_usd"] - expected_bull_gain) < 1e-6
            # The strategy-level total sums BULL's 12 trades and BEAR's 2
            # (-2% each) together - a plain sum, so it must equal BULL's own
            # gain plus the two BEAR trades' fixed-stake loss.
            total_gain = total_dollar_gain_table(trades)
            s1_total = total_gain[total_gain["strategy_id"] == "S1"].iloc[0]
            expected_total_gain = expected_bull_gain + 1000.0 * 2 * (-0.02)
            assert abs(s1_total["dollar_gain_usd"] - expected_total_gain) < 1e-6
            assert s1_total["trades"] == 14

            # A pre-2024 trade must land in discovery, not validation, and
            # not count toward the specialist floor.
            early = make("S2", "BULL", 0, pd.Timestamp("2023-06-01", tz="UTC"), 0.9, "EARLY-0")
            early_trades = split_discovery_validation(attach_benchmark(pd.DataFrame([early])))
            assert early_trades.iloc[0]["analysis_window"] == "discovery"

            # universal_table() must not raise when no strategy covers all
            # four coin regimes (S1 here only has BULL+BEAR) - a real,
            # reportable "zero universal candidates" outcome, not an error.
            # This is the bug a Model 2/3 gated-candidate run hit: an empty
            # `rows` list produced a column-less DataFrame that KeyError'd
            # on the sort_values() call below it.
            coin_table = coin_specialist_table(trades)
            empty_universal = universal_table(coin_table)
            assert empty_universal.empty
            assert list(empty_universal.columns) == [
                "strategy_id", "regimes_covered", "worst_regime",
                "worst_regime_return", "median_regime_excess_return", "regime_consistency"]

            # regime.gated_attribution's Model 1/2/3 output names the same
            # slot `candidate_id`, not `strategy_id` - load_trades() must
            # detect and normalize it rather than raising a missing-column
            # error (the bug this session found and fixed).
            candidate_csv = directory_path / "gated_trades.csv"
            gated = pd.DataFrame([make("C1", "BULL", 0, pd.Timestamp("2024-06-01", tz="UTC"), 0.02, "G-0")])
            gated = gated.rename(columns={"strategy_id": "candidate_id"})
            gated[["candidate_id"] + TRADE_COLUMNS[1:]].to_csv(candidate_csv, index=False)
            assert _detect_id_column(candidate_csv) == "candidate_id"
            loaded = load_trades(candidate_csv)
            assert "strategy_id" in loaded.columns
            assert list(loaded["strategy_id"]) == ["C1"]
        finally:
            CANDLE_DIR = saved_dir
    print("specialist evaluation selftest: PASS")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trades", type=Path, default=DEFAULT_TRADES)
    parser.add_argument("--strategies", type=str, default="",
                        help="comma-separated strategy_id filter")
    parser.add_argument("--outdir", type=Path, default=OUT)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    strategies = {s.strip() for s in args.strategies.split(",") if s.strip()} or None
    id_column = _detect_id_column(args.trades)
    trades = load_trades(args.trades, strategies)
    trades = attach_benchmark(trades)
    trades = split_discovery_validation(trades)

    btc_table = btc_specialist_table(trades)
    coin_table = coin_specialist_table(trades)
    btc_ranking = rank_specialists(btc_table, "btc_regime")
    coin_ranking = rank_specialists(coin_table, "coin_regime")
    universal = universal_table(coin_table)
    total_gain = total_dollar_gain_table(trades)

    args.outdir.mkdir(parents=True, exist_ok=True)
    _write(btc_table, args.outdir / "btc_specialist_table.csv")
    _write(coin_table, args.outdir / "coin_specialist_table.csv")
    _write(btc_ranking, args.outdir / "btc_specialist_ranking.csv")
    _write(coin_ranking, args.outdir / "coin_specialist_ranking.csv")
    _write(universal, args.outdir / "universal_strategies.csv")
    _write(total_gain, args.outdir / "strategy_total_dollar_gain.csv")

    manifest = {
        "schema_version": 1,
        "source_trades": str(args.trades),
        "strategy_filter": sorted(strategies) if strategies else None,
        "validation_start": VALIDATION_START.isoformat(),
        "min_episodes": MIN_EPISODES,
        "min_trades": MIN_TRADES,
        "start_capital_usd": START_CAPITAL,
        "source_id_column": id_column,
        "strategies_evaluated": sorted(set(trades["strategy_id"])),
        "validation_tier_btc_rows": int((btc_table["tier"] == "VALIDATION").sum()),
        "validation_tier_coin_rows": int((coin_table["tier"] == "VALIDATION").sum()),
        "universal_candidates": int(len(universal)),
        "strategies_with_total_dollar_gain": int(len(total_gain)),
        "evidence_scope": (
            "Specialist/universal evaluation, strategy_filter above defines "
            "its population (null = every strategy in source_trades). Ranks "
            "only VALIDATION-tier rows (>= %d validation-window episodes "
            "and >= %d trades together); everything else is reported but "
            "never ranked. Excess return is always against the "
            "exposure-matched benchmark (coin's own spot buy-and-hold over "
            "the same trade intervals), never raw profit. "
            "worst_regime_drawdown is not produced - see this module's "
            "docstring." % (MIN_EPISODES, MIN_TRADES)
        ),
        "dollar_gain_scope": (
            "dollar_gain_usd/benchmark_dollar_gain_usd (per-regime tables) "
            "and strategy_total_dollar_gain.csv (regime-agnostic) price "
            "each validation-window trade as its own fresh $%g stake and "
            "sum the result - not compounded/reinvested. A descriptive "
            "dollar view, never used for ranking or the specialist floor; "
            "see _fixed_stake_gain()'s docstring for why compounding was "
            "tried and dropped." % START_CAPITAL
        ),
    }
    (args.outdir / "evaluation_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"evaluated {len(set(trades['strategy_id']))} strategies, "
          f"{len(trades)} trades; VALIDATION-tier rows: "
          f"btc={manifest['validation_tier_btc_rows']} "
          f"coin={manifest['validation_tier_coin_rows']}; "
          f"universal candidates: {manifest['universal_candidates']}; "
          f"strategies with a total-dollar-gain row: "
          f"{manifest['strategies_with_total_dollar_gain']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
