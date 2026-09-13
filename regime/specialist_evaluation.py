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

`max_drawdown` (section 19's `worst_regime_drawdown`) is a per-(strategy,
regime) equity-curve reconstruction - see `_regime_drawdown()` - built on
the same fixed-$1000-stake convention as the dollar-gain figures below, for
the same reason: a compounding curve over a strategy's own regime-matched
trades produces the identical exponential-math distortion `_fixed_stake_gain()`
already documents dropping.

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
from scipy import stats as scipy_stats

from regime import attribution


ROOT = Path(__file__).resolve().parents[1]
CANDLE_DIR = ROOT / "user_data" / "data" / "binance"
DEFAULT_TRADES = ROOT / "results" / "regime" / "trade_regime_attribution.csv"
REGIME_DAILY = ROOT / "results" / "regime" / "regime_daily.csv"
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
    "profit_ratio", "profit_abs", "trade_duration", "exit_reason",
    "btc_regime_match", "coin_regime_match", "btc_regime", "btc_episode_id",
    "coin_regime", "coin_episode_id",
]

# 2026-09-14, FreqForge-inspired scoring (github.com/baxr6/FreqForge).
# Split 2026-09-14 (DeepSeek-v4-pro review, conversation
# "regime-code-audit-2026-09-14") after the first version scored FreqForge's
# "Liquidation-Safety" category off `FORCED_EXIT_REASONS`, which also
# contains `force_exit` - a harmless, common exit (e.g. the backtest window
# simply ending) with nothing to do with a margin call. `LIQUIDATION_EXIT_REASONS`
# is the strict, score-relevant rate; `FORCED_EXIT_REASONS` remains for the
# separate, purely descriptive `forced_exit_rate` column (never scored).
# Checked against the corpus: 900 of 3,459,380 trades (~0.026%) are
# `force_exit`/`liquidation` combined, so even the descriptive rate rarely
# differs from 0 in practice.
LIQUIDATION_EXIT_REASONS = {"liquidation"}
FORCED_EXIT_REASONS = {"force_exit", "liquidation"}


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
    dtypes = {id_column: "string", "pair": "string", "exit_reason": "string",
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


def _episode_price_bounds(daily: pd.DataFrame, episode_column: str,
                          group_cols: list[str]) -> pd.DataFrame:
    """One row per distinct episode (grouped by `group_cols + [episode_column]`
    - `[]` for the market-wide BTC episode id, `["coin_pair"]` for the
    pair-specific coin episode id): the timestamp of its first classified day
    (`episode_start`) and one day past its last classified day (`episode_end_ts`,
    not the last day's own midnight - that would sample the price at the
    *start* of the phase's last day and silently drop that whole day's move)."""
    bounds = (daily.groupby(group_cols + [episode_column])["date"]
              .agg(episode_start="min", episode_end="max").reset_index())
    bounds["episode_end_ts"] = bounds["episode_end"] + pd.Timedelta(days=1)
    return bounds


def attach_benchmark(trades: pd.DataFrame, daily: pd.DataFrame | None = None,
                     daily_path: Path = REGIME_DAILY) -> pd.DataFrame:
    """Four exposure-matched benchmark columns, all the coin's own spot
    buy-and-hold - never BTC's price, even for the BTC-regime column, and
    never leveraged: an opportunity-cost reference for the asset itself.

    - `benchmark_return`: over exactly the trade's own open-to-close interval
      (`REGIME_PREREGISTRATION.md` amendment, entry 3). Used only by
      `total_dollar_gain_table`'s regime-agnostic total, which has no single
      market phase to measure against.
    - `btc_episode_benchmark_return` / `coin_episode_benchmark_return`: over
      the *entire* BTC-regime / coin-regime episode the trade fell in - from
      the episode's first classified day to its last (`regime_daily.csv`'s
      `btc_episode_id`/`coin_episode_id`), regardless of when within it the
      trade itself opened or closed. Added 2026-09-12 per explicit user
      request: the trade-duration benchmark can only ever be beaten by an
      unleveraged long trade through fee drag or price-timing noise (a long,
      1x trade's own return is mechanically ~ the same interval's spot
      return), so it cannot answer "does this strategy time a market phase
      better than simply holding through it" - only a benchmark spanning the
      whole phase can. Used by `btc_specialist_table`/`coin_specialist_table`
      and everything downstream of them (rankings, universal candidates).
    - `joint_episode_benchmark_return`: over the *overlap* of the trade's BTC
      episode and its coin episode - the true condition Model 3's AND-gate
      actually requires (both states matched at once), which neither
      marginal episode alone represents. Added 2026-09-12 per explicit user
      request to present Model 3's gated result as one combined table rather
      than two separate BTC-/coin-regime breakdowns that necessarily agree on
      every trade's regime label but disagree on episode length and hence on
      excess-return. Used only by `joint_specialist_table`.

    All four are NaN wherever the coin has no candle coverage for the
    relevant interval - the documented XMR/USDT post-delisting gap is the
    only known case in the current corpus, and is left as a gap rather than
    imputed, the same choice `regime.attribution` already makes for regime
    state itself.

    Also attaches `btc_episode_days`/`coin_episode_days`/`joint_episode_days`
    (2026-09-14, FreqForge-inspired scoring): the calendar-day span of the
    episode each trade fell in, broadcast from the same episode bounds the
    benchmark returns above already use - needs no candle lookup, just
    `episode_end_ts - episode_start`. Used to annualize Sortino/CAGR against
    the days a strategy was actually *in* this regime (summed across its own
    scattered episodes), not the calendar span between its first and last
    matched trade, which would count years of out-of-regime gaps as if they
    were in-regime time."""
    trades = trades.copy()
    trades["coin_pair"] = trades["pair"].str.split(":", n=1).str[0]
    trades["benchmark_return"] = np.nan
    trades["btc_episode_benchmark_return"] = np.nan
    trades["coin_episode_benchmark_return"] = np.nan
    trades["joint_episode_benchmark_return"] = np.nan
    trades["joint_episode_days"] = np.nan
    # Composite key identifying the actual overlap window between a trade's
    # BTC episode and its coin episode - Model 3's real gate condition (both
    # states matched at once), which the two marginal episodes alone cannot
    # represent. Well-defined string even where episode ids are missing;
    # only rows with a resolvable benchmark below ever get looked up by it.
    trades["joint_episode_id"] = (trades["btc_episode_id"].astype(str) + "|" +
                                  trades["coin_episode_id"].astype(str))
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

    if daily is None:
        daily = pd.read_csv(daily_path, usecols=["date", "pair", "btc_episode_id",
                                                 "coin_episode_id"],
                           dtype={"btc_episode_id": "string", "coin_episode_id": "string"})
        daily["date"] = pd.to_datetime(daily["date"], utc=True)
    btc_bounds = _episode_price_bounds(daily, "btc_episode_id", [])
    coin_bounds = _episode_price_bounds(daily.rename(columns={"pair": "coin_pair"}),
                                        "coin_episode_id", ["coin_pair"])
    btc_bounds_j = btc_bounds.rename(columns={"episode_start": "btc_start",
                                              "episode_end_ts": "btc_end_ts"})
    coin_bounds_j = coin_bounds.rename(columns={"episode_start": "coin_start",
                                                "episode_end_ts": "coin_end_ts"})

    # Episode day-spans need no price data, so broadcast them globally (no
    # per-pair loop) rather than duplicating this inside it.
    btc_bounds["btc_episode_days"] = (
        btc_bounds["episode_end_ts"] - btc_bounds["episode_start"]).dt.days
    coin_bounds["coin_episode_days"] = (
        coin_bounds["episode_end_ts"] - coin_bounds["episode_start"]).dt.days
    trades["btc_episode_days"] = trades["btc_episode_id"].map(
        btc_bounds.set_index("btc_episode_id")["btc_episode_days"])
    coin_days_lookup = coin_bounds.set_index(["coin_pair", "coin_episode_id"])["coin_episode_days"]
    trades["coin_episode_days"] = pd.MultiIndex.from_frame(
        trades[["coin_pair", "coin_episode_id"]]).map(coin_days_lookup)

    def _episode_return(sub_bounds: pd.DataFrame, unit_candles: pd.DataFrame) -> pd.Series:
        start_price = _asof_price(pd.Series(sub_bounds["episode_start"].to_numpy(),
                                            index=sub_bounds.index), unit_candles)
        end_price = _asof_price(pd.Series(sub_bounds["episode_end_ts"].to_numpy(),
                                          index=sub_bounds.index), unit_candles)
        with np.errstate(invalid="ignore", divide="ignore"):
            return (end_price.reindex(sub_bounds.index) /
                    start_price.reindex(sub_bounds.index) - 1.0)

    for pair, group in trades.groupby("coin_pair", sort=False):
        candles = _candle_series(pair, cache)
        if candles is None or candles.empty:
            continue
        unit_candles = candles.assign(date=candles["date"].astype(unit))

        open_price = _asof_price(group["open_date"], unit_candles).to_numpy()
        close_price = _asof_price(group["close_date"], unit_candles).to_numpy()
        with np.errstate(invalid="ignore", divide="ignore"):
            trades.loc[group.index, "benchmark_return"] = close_price / open_price - 1.0

        btc_ids = group["btc_episode_id"].dropna().unique()
        if len(btc_ids):
            sub = btc_bounds[btc_bounds["btc_episode_id"].isin(btc_ids)].copy()
            sub["_ret"] = _episode_return(sub, unit_candles).to_numpy()
            lookup = sub.set_index("btc_episode_id")["_ret"]
            trades.loc[group.index, "btc_episode_benchmark_return"] = \
                group["btc_episode_id"].map(lookup).to_numpy()

        coin_ids = group["coin_episode_id"].dropna().unique()
        if len(coin_ids):
            sub = coin_bounds[(coin_bounds["coin_pair"] == pair) &
                             (coin_bounds["coin_episode_id"].isin(coin_ids))].copy()
            sub["_ret"] = _episode_return(sub, unit_candles).to_numpy()
            lookup = sub.set_index("coin_episode_id")["_ret"]
            trades.loc[group.index, "coin_episode_benchmark_return"] = \
                group["coin_episode_id"].map(lookup).to_numpy()

        # Model 3's actual joint condition: the overlap of this trade's BTC
        # episode and its coin episode, not either alone - non-empty by
        # construction for any trade at all (the day it opened lies in both).
        joint_keys = group[["btc_episode_id", "coin_episode_id"]].dropna().drop_duplicates()
        if len(joint_keys):
            sub = joint_keys.merge(btc_bounds_j[["btc_episode_id", "btc_start", "btc_end_ts"]],
                                   on="btc_episode_id", how="left")
            sub = sub.merge(
                coin_bounds_j.loc[coin_bounds_j["coin_pair"] == pair,
                                  ["coin_episode_id", "coin_start", "coin_end_ts"]],
                on="coin_episode_id", how="left")
            sub["episode_start"] = sub[["btc_start", "coin_start"]].max(axis=1)
            sub["episode_end_ts"] = sub[["btc_end_ts", "coin_end_ts"]].min(axis=1)
            sub["_ret"] = _episode_return(sub, unit_candles).to_numpy()
            sub["_days"] = (sub["episode_end_ts"] - sub["episode_start"]).dt.days
            sub["_key"] = sub["btc_episode_id"].astype(str) + "|" + sub["coin_episode_id"].astype(str)
            lookup = sub.set_index("_key")["_ret"]
            trades.loc[group.index, "joint_episode_benchmark_return"] = \
                group["joint_episode_id"].map(lookup).to_numpy()
            days_lookup = sub.set_index("_key")["_days"]
            trades.loc[group.index, "joint_episode_days"] = \
                group["joint_episode_id"].map(days_lookup).to_numpy()

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


def _regime_drawdown(df: pd.DataFrame, group_cols: list[str]) -> pd.Series:
    """Section 19's `worst_regime_drawdown`: the worst peak-to-trough drop of
    a hypothetical equity curve built only from this group's own matched
    trades, ordered by `close_date`, normalized against the capital actually
    committed by that point - not against the curve's own running peak.

    Same fixed-$1000-per-trade convention as `_fixed_stake_gain()`: each
    trade contributes its own fresh $1000 stake's profit, summed rather than
    compounded, for the same reason that function's docstring gives
    (compounding reproduces an exponential-math distortion, not strategy
    quality). Normalizing by the running *peak* instead of by capital
    committed was tried first and was wrong (2026-09-13, caught by a user
    reading the published artifact): with N independent $1000 stakes and no
    shared depleting balance, a long run of many small, ordinary losses can
    dwarf a peak that only rose a little - e.g. `CryptoFrogHO2`'s worst
    single trade ever lost 13% (no leverage, `is_short` false throughout),
    yet peak-normalized drawdown in one regime came out to 685%, purely from
    summing ~4,500 trades' losses against a peak of a few hundred dollars.
    That number answered "how many peak-dollars deep was the trough", which
    for many independent stakes is not a percentage at all.

    Normalizing by capital committed instead - `(i+1) * START_CAPITAL` after
    i+1 trades, since each trade brought its own $1000 regardless of
    profit/loss - makes the result a bounded, meaningful fraction: at most
    k trades since the peak can each have lost at most 100% of their own
    stake (unleveraged, `profit_ratio >= -1`), so their combined loss is at
    most k * $1000, and capital committed by then is at least k * $1000 -
    the ratio cannot exceed 1.0 unless at least one trade's own
    `profit_ratio` fell below -1, which only happens with leverage or a
    short whose loss exceeded the stake. A row still above 100% after this
    fix is exactly that signal, not an aggregation artifact.

    Returns 0.0 for a group whose curve never dips below its starting
    capital (including a single-trade group)."""
    if df.empty:
        return pd.Series(dtype="float64")
    def _worst(profit_ratios: pd.Series) -> float:
        n = len(profit_ratios)
        equity = START_CAPITAL + (profit_ratios.to_numpy() * START_CAPITAL).cumsum()
        equity = np.concatenate([[START_CAPITAL], equity])
        peak = np.maximum.accumulate(equity)
        committed = START_CAPITAL * np.maximum(np.arange(n + 1), 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            drawdown = np.where(committed > 0, (peak - equity) / committed, 0.0)
        return float(drawdown.max())
    ordered = df.sort_values("close_date")
    return ordered.groupby(group_cols, dropna=False)["profit_ratio"].apply(_worst)


# ---------------------------------------------------------------------------
# FreqForge-inspired scoring (github.com/baxr6/FreqForge), added 2026-09-14
# on explicit user request after a DeepSeek-v4-pro critique of the first
# draft caught two real defects, both fixed below - not merely caveated:
#
# 1. CAGR must compound the group's *total* return, not its mean per-trade
#    return - `(1+mean_profit_ratio)^(365/days)` is blind to trade count
#    (10 trades at +2% and 50 trades at +2% over the same days produced the
#    same figure despite a 5x difference in actual profit). Fixed by
#    compounding `dollar_gain_usd / START_CAPITAL` (the group's total
#    fixed-stake return) instead of the per-trade mean.
# 2. The FreqForge "drawdown control" score must not depend on *when* in a
#    group's history a loss happened. `_regime_drawdown()`'s existing
#    capital-committed-since-group-start normalization is positionally
#    biased for that purpose: the same -40% trade scores 40% drawdown as
#    the group's 1st trade but ~0.4% as its 100th, purely because 99
#    unrelated prior trades inflated the denominator. `_regime_drawdown()`
#    itself is untouched (it answers a different, already-shipped question
#    - a leverage-detection bound over the whole regime history - and nothing
#    about it was wrong for that purpose). This section instead adds
#    `_regime_drawdown_since_peak()`, which resets the committed-capital
#    denominator every time the curve makes a new high, so the same
#    loss scores the same regardless of its position in the sequence.
#
# Second round, 2026-09-14, after a full-module DeepSeek-v4-pro code review
# (conversation "regime-code-audit-2026-09-14", both the review and the
# fix proposals below checked with it before implementing) found four more
# defects in this section, all fixed:
#
# 3. Sortino mixed time scales: the numerator (`sum_profit / total_days`)
#    was a per-day rate, the denominator (`np.std` of raw trade-level
#    negative `profit_ratio`) was not - dividing them and multiplying by
#    `sqrt(365)` produced a number that looked annualized but wasn't
#    dimensionally a Sortino ratio at all. Fixed by moving both sides to
#    the same (trade) level - mean and downside-std of `profit_ratio`
#    directly - and annualizing with `sqrt(trades_per_year)` instead of
#    `sqrt(365)`, the standard way to annualize a ratio built from
#    irregularly-spaced observations (trades here, instead of days).
#    Downside-std now uses `ddof=1` (sample, not population, standard
#    deviation - matching `_episode_excess_lcb()`), defined only from two
#    or more losing trades; fewer routes to the same -100/best-case
#    sentinel branch as zero losing trades already did, so this changes no
#    existing behavior for that edge, only the >=2-losses case.
# 4. CAGR was even more wrong: `dollar_gain_usd / START_CAPITAL` is the
#    *sum* of many independent $1000 stakes' returns, not the growth of one
#    compounding position, yet the formula raised `(1 + that sum)` to a
#    power as if it were - 50 trades at +2% over 100 days produced a
#    "CAGR" over 1000%. Fixed by dropping the compounding claim entirely:
#    `annualized_return = mean_profit_ratio * trades_per_year`, a linear
#    (non-compounding) annualized rate, consistent with the fixed-stake,
#    never-compounded accounting this whole module already uses everywhere
#    else (`_fixed_stake_gain()`'s docstring explains why compounding was
#    rejected). Renamed throughout (`cagr` -> `annualized_return`,
#    `_cagr_points()` -> `_annualized_return_points()`) so the column can
#    never be mistaken for a true compound annual growth rate; point-scale
#    anchors re-picked for this metric's much smaller typical range (frozen
#    before inspecting any strategy's value, same discipline as every other
#    threshold here).
# 5. `_freqforge_metrics()`'s `profit_factor` (+inf on zero losing trades,
#    scored 100 by `_profit_factor_points()`) disagreed with
#    `attribution.py`'s `_summarize()`, which turned the identical case into
#    NaN via a `.replace(0.0, np.nan)`. Unified on +inf (see
#    `regime/attribution.py`'s `_summarize()`).
# 6. `liquidation_rate` (FreqForge's "Liquidation-Safety" category) was
#    computed from `FORCED_EXIT_REASONS = {"force_exit", "liquidation"}` -
#    but `force_exit` also fires for reasons that have nothing to do with a
#    margin call (most commonly the backtest window simply ending), so the
#    category measured something broader than its name claimed. Split: the
#    score now uses `LIQUIDATION_EXIT_REASONS = {"liquidation"}` only;
#    `forced_exit_rate` (the old, broader definition) is kept as a separate,
#    purely descriptive column, never scored.
#
# FreqForge itself never resolves the frozen "do not rely on a single
# composite score" question `REGIME_AUDIT_PLAN.md` section 17 already
# settled for this audit's own ranking rule - `freqforge_score` here is
# reported as one more descriptive column, alongside its six inputs, never
# a replacement for the tier/excess-return ranking used everywhere else in
# this module.
# ---------------------------------------------------------------------------

def _regime_drawdown_since_peak(df: pd.DataFrame, group_cols: list[str]) -> pd.Series:
    """Same fixed-$1000-stake equity curve as `_regime_drawdown()`, but the
    capital-committed denominator resets at every new high instead of
    accumulating from the group's first trade - see the module-level note
    above for why `_regime_drawdown()` itself is wrong for this specific
    use (FreqForge's drawdown-control category), even though it is correct
    for the leverage-bound it was built for."""
    if df.empty:
        return pd.Series(dtype="float64")
    def _worst(profit_ratios: pd.Series) -> float:
        n = len(profit_ratios)
        equity = START_CAPITAL + (profit_ratios.to_numpy() * START_CAPITAL).cumsum()
        equity = np.concatenate([[START_CAPITAL], equity])
        peak = np.maximum.accumulate(equity)
        at_peak = equity >= peak - 1e-9
        # Index of the most recent new-high point at or before each step.
        last_peak_idx = np.where(at_peak, np.arange(n + 1), -1)
        last_peak_idx = np.maximum.accumulate(last_peak_idx)
        committed_since_peak = np.maximum(np.arange(n + 1) - last_peak_idx, 1) * START_CAPITAL
        with np.errstate(invalid="ignore", divide="ignore"):
            drawdown = np.where(committed_since_peak > 0,
                               (peak - equity) / committed_since_peak, 0.0)
        return float(drawdown.max())
    ordered = df.sort_values("close_date")
    return ordered.groupby(group_cols, dropna=False)["profit_ratio"].apply(_worst)


def _regime_days(episode_level: pd.DataFrame, group_cols: list[str],
                 episode_days_column: str) -> pd.Series:
    """Total calendar days a group actually spent in this regime: the sum of
    its own distinct episodes' day-spans (`episode_level` is already
    deduplicated to one row per (strategy, regime, coin_pair, episode) by
    the caller), not the span between its first and last matched trade -
    which would count years of out-of-regime gaps between scattered
    episodes as if they were in-regime time."""
    if episode_level.empty:
        return pd.Series(dtype="float64")
    return episode_level.groupby(group_cols, dropna=False)[episode_days_column].sum()


def _scale_points(value: float, anchors: list[tuple[float, float]]) -> float:
    """Piecewise-linear interpolation through `anchors` ((x, points) pairs,
    x ascending), clamped to the first/last point outside that range. Shared
    interpolator for every FreqForge point-scale below - only the anchor
    table differs per category."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    xs = [a[0] for a in anchors]
    ys = [a[1] for a in anchors]
    if value <= xs[0]:
        return ys[0]
    if value >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= value <= xs[i + 1]:
            frac = (value - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + frac * (ys[i + 1] - ys[i])
    return ys[-1]


def _sortino_points(sortino: float) -> float:
    # FreqForge treats freqtrade's own "-100.0" broken-Sortino sentinel (no
    # losing trades at all - the denominator freqtrade's own
    # calculate_sortino() would divide by is zero/NaN) as best-in-class, not
    # worst, since it means nothing to be downside-punished for.
    if sortino is not None and not np.isnan(sortino) and sortino <= -99.99:
        return 100.0
    return _scale_points(sortino, [(0.0, 0.0), (1.5, 50.0), (3.0, 100.0)])


def _drawdown_points(drawdown: float) -> float:
    return _scale_points(drawdown, [(0.0, 100.0), (0.10, 90.0), (0.20, 50.0), (0.40, 0.0)])


def _annualized_return_points(value: float) -> float:
    # Piecewise-linear, not FreqForge's log-scaled CAGR curve: `value` here
    # is `annualized_return` (see the module note above), a linear/
    # non-compounding rate, so it lives on a much smaller typical scale than
    # a true compounding CAGR ever would. Anchors chosen directly from what
    # a linear annualized rate ought to mean (0% -> 0pts, +20%/yr -> 50pts
    # decent, +100%/yr -> 90pts very good, +300%/yr and beyond -> 100pts
    # excellent) - frozen before inspecting any strategy's value, not fitted
    # to this corpus's distribution.
    return _scale_points(value, [(0.0, 0.0), (0.20, 50.0), (1.0, 90.0), (3.0, 100.0)])


def _liquidation_points(rate: float) -> float:
    return _scale_points(rate, [(0.0, 100.0), (0.10, 0.0)])


def _profit_factor_points(pf: float) -> float:
    # FreqForge's own strategy was never below 1.0 (profitable overall), so
    # it never defined that region; extending the (1.0, 20) anchor linearly
    # down to (0, 0) is this module's own choice, not FreqForge's.
    #
    # +inf (no losing trades at all - gross_loss is zero) is FreqForge's own
    # documented special case: "usually means a perfect win rate broke the
    # ratio's division, not that the run was bad" - scored 100, not 0.
    if pf is not None and np.isposinf(pf):
        return 100.0
    if pf is None or np.isnan(pf):
        return 0.0
    return _scale_points(pf, [(0.0, 0.0), (1.0, 20.0), (2.0, 70.0), (10.0, 100.0)])


def _worst_trade_points(worst_trade: float) -> float:
    if worst_trade is None or np.isnan(worst_trade):
        return np.nan
    # FreqForge's own formula (100 + worst_trade_pct) is unbounded below for
    # a loss beyond -100% (leverage/short past full stake) - clamped at 0
    # here rather than left to swing the composite arbitrarily negative.
    return float(np.clip(100.0 + worst_trade * 100.0, 0.0, 100.0))


FREQFORGE_WEIGHTS = {
    "sortino": 0.25, "drawdown": 0.25, "annualized_return": 0.15,
    "liquidation": 0.15, "profit_factor": 0.10, "worst_trade": 0.10,
}


def _freqforge_metrics(validation: pd.DataFrame, episode_level: pd.DataFrame,
                       group_cols: list[str], episode_days_column: str) -> pd.DataFrame:
    """The six FreqForge categories (profit_factor, worst_trade,
    liquidation_rate, sortino, annualized_return, drawdown_since_peak) plus
    their point-scores and the weighted `freqforge_score`, per (strategy,
    regime) group. Descriptive only - see the module note above this
    section."""
    gross_profit = validation.groupby(group_cols, dropna=False)["profit_ratio"].apply(
        lambda s: s[s > 0].sum() * START_CAPITAL)
    gross_loss = validation.groupby(group_cols, dropna=False)["profit_ratio"].apply(
        # abs(), not a bare negation: negating a genuinely empty sum (0.0)
        # produces -0.0, and positive/-0.0 is -inf, not the +inf
        # _profit_factor_points()'s "no losing trades" case checks for.
        lambda s: abs(s[s < 0].sum()) * START_CAPITAL)
    with np.errstate(invalid="ignore", divide="ignore"):
        # gross_profit/gross_loss are both >= 0 by construction, so this is
        # +inf (no losing trades - see _profit_factor_points' FreqForge
        # special case) or NaN (no trades either way), never -inf.
        profit_factor = gross_profit / gross_loss
    worst_trade = validation.groupby(group_cols, dropna=False)["profit_ratio"].min()
    liquidation_rate = validation.groupby(group_cols, dropna=False)["exit_reason"].apply(
        lambda s: float(s.isin(LIQUIDATION_EXIT_REASONS).mean()))
    forced_exit_rate = validation.groupby(group_cols, dropna=False)["exit_reason"].apply(
        lambda s: float(s.isin(FORCED_EXIT_REASONS).mean()))

    total_days = _regime_days(episode_level, group_cols, episode_days_column)
    trade_count = validation.groupby(group_cols, dropna=False)["profit_ratio"].size()
    mean_trade_return = validation.groupby(group_cols, dropna=False)["profit_ratio"].mean()
    # ddof=1 (sample std), and only from >=2 losing trades - matches
    # _episode_excess_lcb()'s convention. Exactly 0 or 1 losing trades both
    # fall through to the -100/best-case sentinel below (a single loss has
    # no defined sample spread either), same behavior this had before for
    # the zero-losses case.
    downside_std = validation.groupby(group_cols, dropna=False)["profit_ratio"].apply(
        lambda s: float(np.std(s[s < 0], ddof=1)) if (s < 0).sum() >= 2 else np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        trades_per_year = trade_count / (total_days / 365.0)
        # Sortino: both sides of the ratio are now trade-level (mean and
        # downside-std of profit_ratio directly), annualized by
        # sqrt(trades per year) - the standard way to annualize a ratio
        # built from irregularly-spaced observations - instead of mixing a
        # per-day rate against a per-trade spread (see module note above).
        aligned_downside = downside_std.reindex(mean_trade_return.index)
        sortino = np.where(
            aligned_downside.notna() & (aligned_downside != 0),
            mean_trade_return / aligned_downside.replace(0, np.nan) *
            np.sqrt(trades_per_year.reindex(mean_trade_return.index)),
            -100.0)
        sortino = pd.Series(sortino, index=mean_trade_return.index)
        # annualized_return: a linear (non-compounding) annualized rate -
        # mean per-trade return times how many such trades happen per year
        # - not a compound growth rate (see module note above for why a
        # true CAGR is incompatible with this module's fixed-stake,
        # never-compounded accounting).
        annualized_return = mean_trade_return * trades_per_year

    drawdown_since_peak = _regime_drawdown_since_peak(validation, group_cols)

    table = pd.DataFrame({
        "profit_factor": profit_factor,
        "worst_trade": worst_trade,
        "liquidation_rate": liquidation_rate,
        "forced_exit_rate": forced_exit_rate,
        "total_regime_days": total_days,
        "sortino": sortino,
        "annualized_return": annualized_return,
        "drawdown_since_peak": drawdown_since_peak,
    })
    table["sortino_pts"] = table["sortino"].apply(_sortino_points)
    table["drawdown_pts"] = table["drawdown_since_peak"].apply(_drawdown_points)
    table["annualized_return_pts"] = table["annualized_return"].apply(_annualized_return_points)
    table["liquidation_pts"] = table["liquidation_rate"].apply(_liquidation_points)
    table["profit_factor_pts"] = table["profit_factor"].apply(_profit_factor_points)
    table["worst_trade_pts"] = table["worst_trade"].apply(_worst_trade_points)
    table["freqforge_score"] = (
        table["sortino_pts"] * FREQFORGE_WEIGHTS["sortino"] +
        table["drawdown_pts"] * FREQFORGE_WEIGHTS["drawdown"] +
        table["annualized_return_pts"] * FREQFORGE_WEIGHTS["annualized_return"] +
        table["liquidation_pts"] * FREQFORGE_WEIGHTS["liquidation"] +
        table["profit_factor_pts"] * FREQFORGE_WEIGHTS["profit_factor"] +
        table["worst_trade_pts"] * FREQFORGE_WEIGHTS["worst_trade"])
    return table.reset_index()


# ---------------------------------------------------------------------------
# Episode-weighted excess return and its confidence bound, added 2026-09-14
# on explicit user request after a DeepSeek-v4-pro discussion
# (conversation "regime-audit-reliability-score") about combining effect
# size (how much better than buy-and-hold) with sample reliability
# (episodes, not trades) into one number, Gainium-style A-F grade included.
#
# That discussion surfaced a real, separate defect while designing the new
# metric: `excess_return` itself averaged `profit_ratio` per *trade*, while
# `mean_benchmark_return` already averaged per *episode* - the same
# uneven-weighting bug this module already fixed once for the dollar
# figures (2026-09-13), just smaller in magnitude here since it distorts a
# mean, not a sum. A strategy with 50 trades in one episode and 2 in
# another had the 50-trade episode count 25x as much toward
# `mean_profit_ratio` as the 2-trade one, even though both are exactly one
# independent data point. Fixed by summing each episode's own trades'
# profit_ratio first (matching the fixed-$1000-per-trade convention used
# everywhere else - this is the same quantity `dollar_gain_usd` sums, just
# not yet multiplied by START_CAPITAL), then averaging *that* across
# episodes - both `mean_profit_ratio` and `mean_benchmark_return` are now
# one-vote-per-episode, and every downstream user of `excess_return` (tier
# is unaffected - it never used excess_return - but ranking, Top-N
# selection, and every specific percentage quoted in the artifact's prose
# changed and needed re-deriving).
# ---------------------------------------------------------------------------

def _episode_pairs(validation: pd.DataFrame, regime_column: str,
                   benchmark_column: str, episode_column: str) -> pd.DataFrame:
    """One row per (strategy, regime, coin_pair, episode) that has a
    resolvable benchmark: that episode's own strategy return (its trades'
    `profit_ratio` summed, not averaged - the same fixed-stake convention
    `dollar_gain_usd` already uses) paired with its benchmark_column value
    (identical for every trade in the episode, so any one of them is the
    episode's value). This is the single source both the corrected
    `excess_return` and the new episode-excess LCB are built from."""
    key = ["strategy_id", regime_column, "coin_pair", episode_column]
    episode_strategy = (validation.groupby(key, dropna=False)["profit_ratio"]
                        .sum().rename("episode_profit_ratio").reset_index())
    episode_benchmark = (validation.dropna(subset=[benchmark_column])
                         .drop_duplicates(subset=key)[key + [benchmark_column]])
    pairs = episode_benchmark.merge(episode_strategy, on=key, how="left")
    pairs["episode_excess"] = pairs["episode_profit_ratio"] - pairs[benchmark_column]
    return pairs


def _episode_excess_lcb(pairs: pd.DataFrame, group_cols: list[str]) -> pd.Series:
    """One-sided 95% lower confidence bound on the mean episode excess
    return: mean(x) - t(0.95, n-1) * s/sqrt(n), x = each episode's own
    excess return, n = independent episodes (never trades - trades inside
    one episode are correlated, not independent draws). NaN below n=2:
    a sample standard deviation needs at least two points, and this
    project's own VALIDATION floor already requires 5 anyway - an
    EXPLORATORY row with 0-1 episodes has nothing to bound.

    Deliberately conservative: few episodes -> wide interval -> low bound,
    with no separate minimum-episode rule bolted on - the bound already
    encodes reliability. Assumes approximately normal episode returns
    (Student-t); genuinely skewed/fat-tailed episode distributions would
    need a bootstrap LCB instead, not implemented here."""
    if pairs.empty:
        return pd.Series(dtype="float64")
    def _lcb(x: pd.Series) -> float:
        x = x.dropna()
        n = len(x)
        if n < 2:
            return np.nan
        mean = x.mean()
        se = x.std(ddof=1) / np.sqrt(n)
        if se == 0:
            return mean
        t_crit = scipy_stats.t.ppf(0.95, n - 1)
        return float(mean - t_crit * se)
    return pairs.groupby(group_cols, dropna=False)["episode_excess"].apply(_lcb)


def _lcb_grade(lcb: float) -> str:
    """Gainium-style A-F letter grade from the episode-excess LCB alone -
    thresholds are round numbers chosen for legibility, not derived from
    the data (frozen before any strategy's grade was inspected, same
    discipline as every other threshold in this project)."""
    if lcb is None or (isinstance(lcb, float) and np.isnan(lcb)):
        return ""
    if lcb > 0.02:
        return "A"
    if lcb > 0.0:
        return "B"
    if lcb > -0.02:
        return "C"
    if lcb > -0.05:
        return "D"
    return "F"


def _specialist_table(trades: pd.DataFrame, regime_column: str, match_column: str,
                      benchmark_column: str, episode_column: str,
                      episode_summary: pd.DataFrame,
                      episode_days_column: str) -> pd.DataFrame:
    validation = trades[(trades["analysis_window"] == "validation") &
                        trades[match_column]]
    if validation.empty:
        return pd.DataFrame(columns=["strategy_id", regime_column, "trades",
                                     "episodes", "mean_profit_ratio",
                                     "mean_benchmark_return", "excess_return", "tier",
                                     "dollar_gain_usd", "benchmark_dollar_gain_usd",
                                     "excess_dollar_gain_usd", "max_drawdown",
                                     "profit_factor", "worst_trade", "liquidation_rate",
                                     "forced_exit_rate", "total_regime_days", "sortino",
                                     "annualized_return", "drawdown_since_peak",
                                     "sortino_pts", "drawdown_pts", "annualized_return_pts",
                                     "liquidation_pts", "profit_factor_pts",
                                     "worst_trade_pts", "freqforge_score",
                                     "episode_excess_lcb", "lcb_grade"])
    group_cols = ["strategy_id", regime_column]
    grouped = validation.groupby(group_cols, dropna=False)
    table = grouped.agg(
        trades=("profit_ratio", "size"),
    ).reset_index()
    table = table.merge(episode_summary[["strategy_id", regime_column, "episodes"]],
                        on=["strategy_id", regime_column], how="left")
    table["episodes"] = table["episodes"].fillna(0).astype(int)

    # The benchmark is one $1000 stake per distinct (coin, episode) a
    # strategy actually traded in - never one per trade. Every trade inside
    # the same episode carries the identical episode-level benchmark_return
    # (attach_benchmark() broadcasts it), so summing/averaging over trades
    # directly would count that one phase's buy-and-hold once per trade
    # inside it - a strategy with 1,230 trades across 40 episodes would have
    # its benchmark dollar figure inflated roughly 30x (confirmed in the
    # published artifact: `Obelisk_TradePro_Ichi_v2_2` showed a +$94,882
    # ADX-Sideways "B&H-Gewinn" this way). Deduplicating first fixes both
    # the dollar sum and the mean (and hence excess_return) at once - both
    # now weight each episode once, matching "$1000 at the start of the
    # phase", not "$1000 per trade taken during the phase". `coin_pair` is
    # part of the key because a BTC-regime episode is one global calendar
    # window shared by all 8 pairs, but each pair's own price move over it
    # differs - two different coins traded within the same BTC episode are
    # two genuinely different buy-and-hold stakes, not duplicates.
    episode_level = (validation.dropna(subset=[benchmark_column])
                     .drop_duplicates(subset=["strategy_id", regime_column,
                                              "coin_pair", episode_column]))

    # episode_pairs carries the SAME episodes as episode_level (one
    # resolvable-benchmark row each) but with the strategy's own summed
    # per-episode return alongside it - see the module note above for why
    # mean_profit_ratio moved from a per-trade to a per-episode average.
    episode_pairs = _episode_pairs(validation, regime_column, benchmark_column, episode_column)
    bench_stats = episode_pairs.groupby(group_cols, dropna=False).agg(
        mean_profit_ratio=("episode_profit_ratio", "mean"),
        mean_benchmark_return=(benchmark_column, "mean"),
        benchmark_matched_episodes=(benchmark_column, "count"))
    table = table.merge(bench_stats.reset_index(), on=group_cols, how="left")
    table["excess_return"] = table["mean_profit_ratio"] - table["mean_benchmark_return"]
    table["tier"] = np.where(
        (table["episodes"] >= MIN_EPISODES) & (table["trades"] >= MIN_TRADES),
        "VALIDATION", "EXPLORATORY")

    episode_excess_lcb = _episode_excess_lcb(episode_pairs, group_cols)

    dollar_gain = _fixed_stake_gain(validation, "profit_ratio", group_cols)
    benchmark_dollar_gain = _fixed_stake_gain(episode_level, benchmark_column, group_cols)
    regime_drawdown = _regime_drawdown(validation, group_cols)
    table = table.set_index(group_cols)
    table["dollar_gain_usd"] = dollar_gain
    table["benchmark_dollar_gain_usd"] = benchmark_dollar_gain
    table["max_drawdown"] = regime_drawdown
    table["episode_excess_lcb"] = episode_excess_lcb
    table = table.reset_index()
    table["excess_dollar_gain_usd"] = table["dollar_gain_usd"] - table["benchmark_dollar_gain_usd"]
    table["lcb_grade"] = table["episode_excess_lcb"].apply(_lcb_grade)

    freqforge = _freqforge_metrics(validation, episode_level, group_cols, episode_days_column)
    table = table.merge(freqforge, on=group_cols, how="left")

    return table.sort_values(["strategy_id", regime_column]).reset_index(drop=True)


# Both table builders below only count episodes from the VALIDATION window
# before handing them to _specialist_table() - a real bug a DeepSeek-v4-pro
# code review found 2026-09-14 (conversation "regime-code-audit-2026-09-14"):
# they used to pass the full, unfiltered `trades` (2020-03-01 onward) to
# attribution.summarize_episodes()/summarize_coin_episodes(), so the
# "episodes" count feeding the VALIDATION/EXPLORATORY tier split included
# discovery-window episodes too, while "trades" (aggregated inside
# _specialist_table() from its own already-validation-filtered `validation`)
# never did. REGIME_PREREGISTRATION.md's amendment is explicit - "5
# independent regime episodes within the validation window" - so a
# strategy with, say, 6 episodes before 2024 but only 2 after could be
# wrongly promoted to VALIDATION on pre-2024 evidence its trade count
# didn't share. Fixed by filtering to analysis_window == "validation" here,
# matching what _specialist_table() already does internally for trades.
def btc_specialist_table(trades: pd.DataFrame) -> pd.DataFrame:
    validation = trades[trades["analysis_window"] == "validation"]
    return _specialist_table(trades, "btc_regime", "btc_regime_match",
                             "btc_episode_benchmark_return", "btc_episode_id",
                             attribution.summarize_episodes(validation), "btc_episode_days")


def coin_specialist_table(trades: pd.DataFrame) -> pd.DataFrame:
    validation = trades[trades["analysis_window"] == "validation"]
    return _specialist_table(trades, "coin_regime", "coin_regime_match",
                             "coin_episode_benchmark_return", "coin_episode_id",
                             attribution.summarize_coin_episodes(validation), "coin_episode_days")


def joint_specialist_table(trades: pd.DataFrame) -> pd.DataFrame:
    """Model 3's real gated dimension: the entry gate requires BTC state AND
    coin state to both be allowed *at the signal candle*, so almost every
    admitted trade's recorded `btc_regime` and `coin_regime` (looked up at
    `open_date`, one candle later) agree too - but not quite all: either
    side can flip state on the fill candle independently of the other,
    so a small number of trades (7 of ~22,000 in Model 3's pilot
    attribution, none reaching VALIDATION tier) legitimately disagree. This
    is a one-candle signal-vs-fill lag, not a bug, so it is not asserted
    away - `coin_regime` (the specific asset the benchmark is actually
    priced against) is used as the single display label rather than
    requiring agreement. One combined table, instead of
    `btc_specialist_table`/`coin_specialist_table` shown side by side, which
    almost always agree on the label anyway but disagree on episode length
    and excess-return (different episode definitions). Added 2026-09-12 per
    explicit user request; benchmarked against
    `joint_episode_benchmark_return` (the true overlap of the BTC episode
    and the coin episode a trade fell in, not either marginal one).
    Meaningless for Model 0/1/2 trades, where nothing requires the two
    dimensions to be related at all - only call this on an AND-gated
    (Model 3) attribution."""
    trades = trades.copy()
    trades["joint_regime_match"] = trades["btc_regime_match"] & trades["coin_regime_match"]
    # analysis_window == "validation" here too (same fix and reason as
    # btc_specialist_table()/coin_specialist_table() above) - otherwise
    # this table's own episode count would include discovery-window
    # episodes the tier split must not.
    matched = trades[trades["joint_regime_match"] &
                     (trades["analysis_window"] == "validation")]
    episode_summary = (matched.groupby(["strategy_id", "coin_regime"])["joint_episode_id"]
                       .nunique().rename("episodes").reset_index())
    return _specialist_table(trades, "coin_regime", "joint_regime_match",
                             "joint_episode_benchmark_return", "joint_episode_id",
                             episode_summary, "joint_episode_days")


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
                    "trade_duration": 360, "exit_reason": "exit_signal",
                    "btc_regime_match": True, "coin_regime_match": True,
                    "btc_regime": regime, "btc_episode_id": episode,
                    "coin_regime": regime, "coin_episode_id": episode,
                }
            def daily_row(day, episode):
                return {"date": pd.Timestamp(day).tz_localize("UTC").normalize()
                        if pd.Timestamp(day).tzinfo is None else pd.Timestamp(day).normalize(),
                        "pair": "BTC/USDT", "btc_episode_id": episode, "coin_episode_id": episode}

            rows = []
            daily_rows = []
            # 6 independent BULL episodes, 2 trades each, all in validation
            # window - clears both the episode and trade floor.
            for i in range(6):
                day = pd.Timestamp("2024-02-01", tz="UTC") + pd.Timedelta(days=i * 7)
                rows.append(make("S1", "BULL", i, day, 0.05, f"BULL-{i}"))
                rows.append(make("S1", "BULL", i, day + pd.Timedelta(hours=1), 0.03, f"BULL-{i}"))
                daily_rows.append(daily_row(day, f"BULL-{i}"))
            # Only 2 BEAR episodes for S1 - below the 5-episode floor.
            for i in range(2):
                day = pd.Timestamp("2024-05-01", tz="UTC") + pd.Timedelta(days=i * 7)
                rows.append(make("S1", "BEAR", i, day, -0.02, f"BEAR-{i}"))
                daily_rows.append(daily_row(day, f"BEAR-{i}"))
            daily_rows.append(daily_row(pd.Timestamp("2023-06-01", tz="UTC"), "EARLY-0"))
            synthetic_daily = pd.DataFrame(daily_rows)

            trades = pd.DataFrame(rows)
            trades = attach_benchmark(trades, daily=synthetic_daily)
            trades = split_discovery_validation(trades)
            assert (trades["analysis_window"] == "validation").all()
            assert trades["benchmark_return"].notna().all()
            assert trades["btc_episode_benchmark_return"].notna().all()
            assert trades["coin_episode_benchmark_return"].notna().all()

            # Dedicated check that the episode benchmark spans the whole
            # regime episode, not just the trade's own interval, using the
            # real 2020-01-01..05 candle range (100/110/121/108.9/130) instead
            # of the flat 2024 tail every other fixture trade lands on.
            ep_trades = pd.DataFrame([{
                "strategy_id": "EP1", "pair": "BTC/USDT:USDT",
                "open_date": pd.Timestamp("2020-01-01T12:00:00Z"),
                "close_date": pd.Timestamp("2020-01-02T12:00:00Z"),
                "is_short": False, "profit_ratio": 0.01, "profit_abs": 1.0,
                "trade_duration": 1440,
                "btc_regime_match": True, "coin_regime_match": True,
                "btc_regime": "BULL", "btc_episode_id": "EP-BULL-0",
                "coin_regime": "BULL", "coin_episode_id": "EP-BULL-0",
            }])
            ep_daily = pd.DataFrame([
                {"date": pd.Timestamp("2020-01-01", tz="UTC"), "pair": "BTC/USDT",
                 "btc_episode_id": "EP-BULL-0", "coin_episode_id": "EP-BULL-0"},
                {"date": pd.Timestamp("2020-01-04", tz="UTC"), "pair": "BTC/USDT",
                 "btc_episode_id": "EP-BULL-0", "coin_episode_id": "EP-BULL-0"},
            ])
            ep_row = attach_benchmark(ep_trades, daily=ep_daily).iloc[0]
            # Trade's own interval (Jan 1 12:00 -> Jan 2 12:00): backward-asof
            # lands on the Jan 1 and Jan 2 candles, 110/100 - 1 = 10%.
            assert abs(ep_row["benchmark_return"] - 0.10) < 1e-9
            # Full episode (first classified day Jan 1 through last classified
            # day Jan 4, i.e. through the close of Jan 4/start of Jan 5):
            # 130/100 - 1 = 30% - the day-3 and day-4 moves the trade-duration
            # benchmark above cannot see at all.
            assert abs(ep_row["btc_episode_benchmark_return"] - 0.30) < 1e-9
            assert abs(ep_row["coin_episode_benchmark_return"] - 0.30) < 1e-9

            # Regression: benchmark_dollar_gain_usd/mean_benchmark_return must
            # count each distinct (coin, episode) once, not once per trade
            # inside it - the bug a user caught in the published artifact (a
            # 1,230-trade/40-episode strategy showed a +$94,882 "B&H-Gewinn",
            # roughly 30x too high, because the same episode's 30% benchmark
            # return was summed once per trade instead of once per episode).
            ep2_trades = pd.DataFrame([
                {"strategy_id": "EP2", "pair": "BTC/USDT:USDT",
                 "open_date": pd.Timestamp("2020-01-01T06:00:00Z"),
                 "close_date": pd.Timestamp("2020-01-01T18:00:00Z"),
                 "is_short": False, "profit_ratio": 0.02, "profit_abs": 2.0,
                 "trade_duration": 720, "exit_reason": "exit_signal",
                 "btc_regime_match": True, "coin_regime_match": True,
                 "btc_regime": "BULL", "btc_episode_id": "EP-BULL-0",
                 "coin_regime": "BULL", "coin_episode_id": "EP-BULL-0"},
                {"strategy_id": "EP2", "pair": "BTC/USDT:USDT",
                 "open_date": pd.Timestamp("2020-01-02T06:00:00Z"),
                 "close_date": pd.Timestamp("2020-01-02T18:00:00Z"),
                 "is_short": False, "profit_ratio": 0.03, "profit_abs": 3.0,
                 "trade_duration": 720, "exit_reason": "exit_signal",
                 "btc_regime_match": True, "coin_regime_match": True,
                 "btc_regime": "BULL", "btc_episode_id": "EP-BULL-0",
                 "coin_regime": "BULL", "coin_episode_id": "EP-BULL-0"},
            ])
            ep2_trades = attach_benchmark(ep2_trades, daily=ep_daily)
            ep2_trades["analysis_window"] = "validation"  # bypass the date
            # split - VALIDATION_START postdates this fixture's 2020 dates,
            # and only the aggregation under test matters here.
            ep2_table = btc_specialist_table(ep2_trades)
            ep2_row = ep2_table[(ep2_table["strategy_id"] == "EP2") &
                                (ep2_table["btc_regime"] == "BULL")].iloc[0]
            assert ep2_row["trades"] == 2
            assert abs(ep2_row["benchmark_dollar_gain_usd"] - 300.0) < 1e-6
            assert abs(ep2_row["mean_benchmark_return"] - 0.30) < 1e-9
            # The strategy's own dollar gain is unaffected - each trade is
            # still its own fresh $1000 stake, summed rather than deduped.
            assert abs(ep2_row["dollar_gain_usd"] - 1000.0 * (0.02 + 0.03)) < 1e-6

            # max_drawdown: a fixed-$1000-stake curve over four trades in
            # close_date order, +10%/-5%/-10%/+20% -> equity 1000, 1100,
            # 1050, 950, 1150; peak so far at each step 1000, 1100, 1100,
            # 1100, 1150; capital committed so far (i * $1000) 1000(floor),
            # 1000, 2000, 3000, 4000. Normalized by capital committed, not by
            # the peak (that was the 2026-09-13 bug - see _regime_drawdown()'s
            # docstring): worst ratio is at trade 3 (1100-950)/3000, not
            # trade 2's (1100-1050)/2000.
            dd_days = [pd.Timestamp("2024-03-01", tz="UTC") + pd.Timedelta(days=i)
                      for i in range(4)]
            dd_rows = [make("DD1", "BULL", i, dd_days[i], ratio, "DD-0")
                      for i, ratio in enumerate([0.10, -0.05, -0.10, 0.20])]
            dd_daily = pd.DataFrame([daily_row(day, "DD-0") for day in dd_days])
            dd_trades = attach_benchmark(pd.DataFrame(dd_rows), daily=dd_daily)
            dd_trades["analysis_window"] = "validation"
            dd_table = btc_specialist_table(dd_trades)
            dd_row = dd_table[(dd_table["strategy_id"] == "DD1") &
                              (dd_table["btc_regime"] == "BULL")].iloc[0]
            assert abs(dd_row["max_drawdown"] - (150.0 / 3000.0)) < 1e-9

            # Regression for the 2026-09-13 bug: 50 trades at -5% each, no
            # winners, so the peak never rises above the $1000 starting
            # capital. The old peak-normalized version divided a growing
            # cumulative loss by that flat, tiny peak - here (1000-(1000-
            # 50*50))/1000 = 250%, fifty small -5% trades reported as a
            # worse-than-total-wipeout. Normalized by capital committed
            # instead, losing a steady 5% of every stake is exactly a 5%
            # drawdown, matching what actually happened - not an amount that
            # grows with trade count for a constant per-trade loss.
            many_days = [pd.Timestamp("2024-04-01", tz="UTC") + pd.Timedelta(days=i)
                        for i in range(50)]
            many_rows = [make("DD2", "BULL", i, many_days[i], -0.05, "DD2-0")
                        for i in range(50)]
            many_daily = pd.DataFrame([daily_row(day, "DD2-0") for day in many_days])
            many_trades = attach_benchmark(pd.DataFrame(many_rows), daily=many_daily)
            many_trades["analysis_window"] = "validation"
            many_table = btc_specialist_table(many_trades)
            many_row = many_table[(many_table["strategy_id"] == "DD2") &
                                  (many_table["btc_regime"] == "BULL")].iloc[0]
            assert many_row["max_drawdown"] <= 1.0
            assert abs(many_row["max_drawdown"] - 0.05) < 1e-9

            # joint_specialist_table(): the BTC episode (Jan 1-3, price
            # 100->108.9, +8.9%) and coin episode (Jan 2-4, price 110->130,
            # +18.18%) only partially overlap - the true joint window is
            # Jan 2-4's *start* through Jan 3's *end* (Jan 2 through Jan 4
            # exclusive-of-Jan-5, i.e. 110 -> 108.9, -1%). All three figures
            # must differ, and joint_specialist_table() must use the third,
            # not either marginal one.
            ej_daily = pd.DataFrame([
                {"date": pd.Timestamp("2020-01-01", tz="UTC"), "pair": "BTC/USDT",
                 "btc_episode_id": "EP-BTC-J", "coin_episode_id": "OTHER-COIN"},
                {"date": pd.Timestamp("2020-01-02", tz="UTC"), "pair": "BTC/USDT",
                 "btc_episode_id": "EP-BTC-J", "coin_episode_id": "EP-COIN-J"},
                {"date": pd.Timestamp("2020-01-03", tz="UTC"), "pair": "BTC/USDT",
                 "btc_episode_id": "EP-BTC-J", "coin_episode_id": "EP-COIN-J"},
                {"date": pd.Timestamp("2020-01-04", tz="UTC"), "pair": "BTC/USDT",
                 "btc_episode_id": "OTHER-BTC", "coin_episode_id": "EP-COIN-J"},
            ])
            ej_trades = pd.DataFrame([{
                "strategy_id": "EJ1", "pair": "BTC/USDT:USDT",
                "open_date": pd.Timestamp("2020-01-02T12:00:00Z"),
                "close_date": pd.Timestamp("2020-01-02T18:00:00Z"),
                "is_short": False, "profit_ratio": 0.01, "profit_abs": 1.0,
                "trade_duration": 360, "exit_reason": "exit_signal",
                "btc_regime_match": True, "coin_regime_match": True,
                "btc_regime": "BULL", "btc_episode_id": "EP-BTC-J",
                "coin_regime": "BULL", "coin_episode_id": "EP-COIN-J",
            }])
            ej_trades = attach_benchmark(ej_trades, daily=ej_daily)
            ej_row = ej_trades.iloc[0]
            assert abs(ej_row["btc_episode_benchmark_return"] - 0.089) < 1e-9
            assert abs(ej_row["coin_episode_benchmark_return"] - 0.181818181818) < 1e-9
            assert abs(ej_row["joint_episode_benchmark_return"] - (-0.01)) < 1e-9

            ej_trades["analysis_window"] = "validation"
            joint_table = joint_specialist_table(ej_trades)
            joint_row = joint_table[(joint_table["strategy_id"] == "EJ1") &
                                    (joint_table["coin_regime"] == "BULL")].iloc[0]
            assert abs(joint_row["excess_return"] - (0.01 - (-0.01))) < 1e-9
            assert abs(joint_row["benchmark_dollar_gain_usd"] - (-10.0)) < 1e-6

            # Real Model 3 data has a handful of trades (signal-vs-fill
            # one-candle lag) where btc_regime_match and coin_regime_match
            # are both True but btc_regime != coin_regime - must not raise,
            # and must group under coin_regime rather than assert agreement.
            mismatched = pd.DataFrame([{
                "strategy_id": "EJ1", "pair": "BTC/USDT:USDT",
                "open_date": pd.Timestamp("2020-01-02T12:00:00Z"),
                "close_date": pd.Timestamp("2020-01-02T18:00:00Z"),
                "is_short": False, "profit_ratio": 0.01, "profit_abs": 1.0,
                "trade_duration": 360, "exit_reason": "exit_signal",
                "btc_regime_match": True, "coin_regime_match": True,
                "btc_regime": "BEAR", "btc_episode_id": "EP-BTC-J",
                "coin_regime": "BULL", "coin_episode_id": "EP-COIN-J",
            }])
            mismatched = attach_benchmark(mismatched, daily=ej_daily)
            mismatched["analysis_window"] = "validation"
            mismatched_table = joint_specialist_table(mismatched)
            assert set(mismatched_table["coin_regime"]) == {"BULL"}
            assert mismatched_table.iloc[0]["trades"] == 1

            btc_table = btc_specialist_table(trades)
            bull_row = btc_table[(btc_table["strategy_id"] == "S1") &
                                 (btc_table["btc_regime"] == "BULL")].iloc[0]
            assert bull_row["episodes"] == 6
            assert bull_row["trades"] == 12
            assert bull_row["tier"] == "VALIDATION"
            # All 12 trades are gains (+5%/+3% alternating) - the curve never
            # dips below its own starting capital, so the worst drawdown is
            # zero, not undefined or negative.
            assert bull_row["max_drawdown"] == 0.0
            # Episode-weighted mean_profit_ratio regression (2026-09-14):
            # each of the 6 BULL episodes sums to +5%+3%=+8%; averaged over
            # 6 EQUAL episodes that is 8%, not the 4% a per-TRADE mean over
            # all 12 trades would give ((0.05+0.03)/2, since every episode
            # repeats the same two trades). The two only coincide when
            # every episode has the same trade count, which is exactly why
            # this fixture alone couldn't have caught the original bug -
            # see the EPW fixture below for a fixture that can.
            assert abs(bull_row["mean_profit_ratio"] - 0.08) < 1e-9
            # Candle coverage for these 2024 dates falls outside the 2020
            # fixture's 5-day price series, so backward-asof pins both ends
            # of every episode to the same last known price - benchmark is
            # a flat 0% here, making excess_return equal mean_profit_ratio.
            assert abs(bull_row["excess_return"] - 0.08) < 1e-9
            # All 6 episodes have IDENTICAL excess (zero variance across
            # episodes), so the LCB collapses to the mean itself (se=0
            # short-circuits the t-widened bound) - confident because
            # consistent, not because n is large.
            assert abs(bull_row["episode_excess_lcb"] - 0.08) < 1e-9
            assert bull_row["lcb_grade"] == "A"
            bear_row = btc_table[(btc_table["strategy_id"] == "S1") &
                                 (btc_table["btc_regime"] == "BEAR")].iloc[0]
            assert bear_row["episodes"] == 2
            assert bear_row["tier"] == "EXPLORATORY"

            # Episode-weighting regression this fixture couldn't have
            # caught: two BULL episodes, 3 trades of +30% each vs. 1 trade
            # of -10%. A per-trade mean over all 4 trades gives
            # (0.30*3-0.10)/4 = 20% - the bug. Weighting by episode instead
            # (each episode sums its own trades first) gives
            # (0.90 + (-0.10))/2 = 40%, the correct value.
            epw_days_a = [pd.Timestamp("2024-08-01", tz="UTC") + pd.Timedelta(days=i)
                         for i in range(3)]
            epw_rows = ([make("EPW", "BULL", i, epw_days_a[i], 0.30, "EPW-A") for i in range(3)] +
                       [make("EPW", "BULL", 3, pd.Timestamp("2024-08-10", tz="UTC"), -0.10, "EPW-B")])
            epw_daily = pd.DataFrame(
                [daily_row(day, "EPW-A") for day in epw_days_a] +
                [daily_row(pd.Timestamp("2024-08-10", tz="UTC"), "EPW-B")])
            epw_trades = attach_benchmark(pd.DataFrame(epw_rows), daily=epw_daily)
            epw_trades["analysis_window"] = "validation"
            epw_table = btc_specialist_table(epw_trades)
            epw_row = epw_table[(epw_table["strategy_id"] == "EPW") &
                                (epw_table["btc_regime"] == "BULL")].iloc[0]
            assert epw_row["episodes"] == 2
            assert epw_row["trades"] == 4
            assert abs(epw_row["mean_profit_ratio"] - 0.40) < 1e-9
            assert abs(epw_row["excess_return"] - 0.40) < 1e-9
            # LCB from n=2 wildly divergent episodes (+90%, -10%): mean=40%,
            # s=std([0.90,-0.10], ddof=1)=1/sqrt(2), se=s/sqrt(2)=0.5,
            # t(0.95, 1 df) is large (~6.31) - the bound swings deeply
            # negative despite the good-looking point estimate, exactly the
            # "don't trust two episodes" signal this metric exists for.
            expected_epw_t = scipy_stats.t.ppf(0.95, 1)
            expected_epw_lcb = 0.40 - expected_epw_t * 0.5
            assert expected_epw_lcb < -1.0
            assert abs(epw_row["episode_excess_lcb"] - expected_epw_lcb) < 1e-6
            assert epw_row["lcb_grade"] == "F"

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
            early_trades = split_discovery_validation(
                attach_benchmark(pd.DataFrame([early]), daily=synthetic_daily))
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

            # Tier-episode-window regression (2026-09-14, DeepSeek-v4-pro
            # review, conversation "regime-code-audit-2026-09-14"):
            # btc_specialist_table()/coin_specialist_table() used to pass the
            # FULL, unfiltered trades history to
            # attribution.summarize_episodes()/summarize_coin_episodes(), so
            # the "episodes" count feeding the VALIDATION/EXPLORATORY tier
            # split included discovery-window episodes the frozen rule
            # explicitly excludes ("5 independent regime episodes within the
            # validation window", REGIME_PREREGISTRATION.md's 2026-09-11
            # amendment). TIERBUG has 6 discovery-window BULL episodes (1
            # trade each, well before 2024) plus only 2 validation-window
            # BULL episodes (5 trades each, 10 trades total - clears
            # MIN_TRADES on its own). The old code would have seen 8 total
            # episodes (>= MIN_EPISODES) and wrongly promoted this to
            # VALIDATION; the fix must see only the 2 real ones and keep it
            # EXPLORATORY.
            tier_discovery_days = [pd.Timestamp("2020-06-01", tz="UTC") + pd.Timedelta(days=60 * i)
                                   for i in range(6)]
            tier_discovery_rows = [
                make("TIERBUG", "BULL", i, tier_discovery_days[i], 0.01, f"TBDISC-{i}")
                for i in range(6)
            ]
            # Discovery episodes need a resolvable daily row too - not for
            # the episode-count fix under test, but because attach_benchmark()
            # always computes the joint BTC/coin episode overlap for every
            # trade regardless of which table will use it, and a joint key
            # with no daily match on either side left-joins to NaN bounds,
            # which then crashes merge_asof rather than merely leaving the
            # benchmark column NaN.
            tier_daily_rows = [daily_row(day, f"TBDISC-{i}")
                              for i, day in enumerate(tier_discovery_days)]
            tier_validation_rows = []
            for ep in range(2):
                for offset in range(5):
                    day = (pd.Timestamp("2024-02-01", tz="UTC") +
                          pd.Timedelta(days=30 * ep + offset))
                    tier_validation_rows.append(make("TIERBUG", "BULL", offset, day, 0.01, f"TBVAL-{ep}"))
                    tier_daily_rows.append(daily_row(day, f"TBVAL-{ep}"))
            tier_trades = attach_benchmark(
                pd.DataFrame(tier_discovery_rows + tier_validation_rows),
                daily=pd.DataFrame(tier_daily_rows))
            tier_trades = split_discovery_validation(tier_trades)
            assert (tier_trades["analysis_window"] == "discovery").sum() == 6
            assert (tier_trades["analysis_window"] == "validation").sum() == 10
            tier_table = btc_specialist_table(tier_trades)
            tier_row = tier_table[(tier_table["strategy_id"] == "TIERBUG") &
                                  (tier_table["btc_regime"] == "BULL")].iloc[0]
            assert tier_row["trades"] == 10
            assert tier_row["episodes"] == 2
            assert tier_row["tier"] == "EXPLORATORY"

            # FreqForge-inspired scoring (2026-09-14): profit_factor,
            # worst_trade, liquidation_rate on the DD1 fixture from the
            # max_drawdown test above (+10%/-5%/-10%/+20%, all exit_signal).
            assert abs(dd_row["profit_factor"] - 2.0) < 1e-9  # 300 gross / 150 gross
            assert abs(dd_row["worst_trade"] - (-0.10)) < 1e-9
            assert dd_row["liquidation_rate"] == 0.0
            assert dd_row["forced_exit_rate"] == 0.0

            # Liquidation/forced-exit split (2026-09-14, DeepSeek-v4-pro
            # review): the old single `liquidation_rate` counted both real
            # liquidations and plain `force_exit` (which also fires for
            # harmless reasons, e.g. the backtest window simply ending) -
            # LIQ1 has one real "liquidation" exit and one "force_exit",
            # so liquidation_rate must count only the former (0.5) while
            # forced_exit_rate counts both (1.0).
            liq_day = pd.Timestamp("2024-08-01", tz="UTC")
            liq_rows = [
                dict(make("LIQ1", "BULL", 0, liq_day, -0.10, "LIQ-0"), exit_reason="liquidation"),
                dict(make("LIQ1", "BULL", 1, liq_day + pd.Timedelta(hours=12), 0.05, "LIQ-0"),
                     exit_reason="force_exit"),
            ]
            liq_daily = pd.DataFrame([daily_row(liq_day, "LIQ-0")])
            liq_trades = attach_benchmark(pd.DataFrame(liq_rows), daily=liq_daily)
            liq_trades["analysis_window"] = "validation"
            liq_table = btc_specialist_table(liq_trades)
            liq_row = liq_table[(liq_table["strategy_id"] == "LIQ1") &
                                (liq_table["btc_regime"] == "BULL")].iloc[0]
            assert abs(liq_row["liquidation_rate"] - 0.5) < 1e-9
            assert abs(liq_row["forced_exit_rate"] - 1.0) < 1e-9

            # Sortino sentinel: DD2's 50 trades are all -5%, so the losing
            # subset has zero variance (std=0 regardless of ddof, all values
            # identical) - freqtrade's own calculate_sortino() treats a
            # zero/NaN denominator as the broken "-100.0" sentinel, and
            # FreqForge scores that sentinel 100 (best-in-class), not worst,
            # since there is nothing to be downside-punished for.
            assert many_row["sortino"] <= -99.99
            assert _sortino_points(many_row["sortino"]) == 100.0

            # Sortino corrected (2026-09-14, DeepSeek-v4-pro review): the
            # first draft mixed a per-day mean (sum(profit_ratio)/days)
            # against a per-trade downside-std, then annualized with
            # sqrt(365) as if both were daily. Fixed to keep both sides of
            # the ratio on the trade level and annualize by
            # sqrt(trades_per_year) instead - the standard way to annualize
            # a ratio built from irregularly-spaced observations. 4 trades
            # in one 4-day episode, +10/-5/-15/+5%, ordered by close_date.
            sortino_days = [pd.Timestamp("2024-05-01", tz="UTC") + pd.Timedelta(days=i)
                           for i in range(4)]
            sortino_rows = [make("DD3", "BULL", i, sortino_days[i], ratio, "DD3-0")
                           for i, ratio in enumerate([0.10, -0.05, -0.15, 0.05])]
            sortino_daily = pd.DataFrame([daily_row(day, "DD3-0") for day in sortino_days])
            sortino_trades = attach_benchmark(pd.DataFrame(sortino_rows), daily=sortino_daily)
            sortino_trades["analysis_window"] = "validation"
            sortino_table = btc_specialist_table(sortino_trades)
            sortino_row = sortino_table[(sortino_table["strategy_id"] == "DD3") &
                                        (sortino_table["btc_regime"] == "BULL")].iloc[0]
            assert sortino_row["total_regime_days"] == 4
            expected_mean_trade = np.mean([0.10, -0.05, -0.15, 0.05])
            expected_downside_std = np.std([-0.05, -0.15], ddof=1)
            expected_trades_per_year = 4 / (4 / 365.0)
            expected_sortino = (expected_mean_trade / expected_downside_std *
                                np.sqrt(expected_trades_per_year))
            assert abs(sortino_row["sortino"] - expected_sortino) < 1e-6

            # annualized_return regression (2026-09-14, DeepSeek-v4-pro
            # review): the original CAGR bug was blind to trade count (10
            # trades and 50 trades at the same +2% each, over the same days,
            # produced identical CAGR despite 5x the real profit); the first
            # fix ("compound the group's total fixed-stake return") went too
            # far the other way - compounding many independent $1000 stakes
            # as if they were one reinvested position exploded to absurd
            # values at high trade counts (this exact fixture used to assert
            # >1000% CAGR). Replaced with a linear (non-compounding)
            # `annualized_return = mean_profit_ratio * trades_per_year`,
            # consistent with the fixed-stake, never-compounded accounting
            # this module uses everywhere else. Both fixtures span the same
            # single 10-day episode at the same +2%/trade; only trade count
            # (5x) differs, so annualized_return must now scale by EXACTLY
            # 5x - neither blind to trade count (the original bug) nor
            # exploding from it (the compounding "fix"'s own bug).
            cagr_days = [pd.Timestamp("2024-06-01", tz="UTC") + pd.Timedelta(days=i)
                        for i in range(10)]
            cagr_a_rows = [make("CAGRA", "BULL", i, cagr_days[i], 0.02, "CAGRA-0")
                          for i in range(10)]
            cagr_b_rows = [make("CAGRB", "BULL", i * 10 + j, cagr_days[i], 0.02, "CAGRB-0")
                          for i in range(10) for j in range(5)]
            cagr_daily = pd.DataFrame([daily_row(day, "CAGRA-0") for day in cagr_days] +
                                      [daily_row(day, "CAGRB-0") for day in cagr_days])
            cagr_trades = attach_benchmark(
                pd.concat([pd.DataFrame(cagr_a_rows), pd.DataFrame(cagr_b_rows)],
                         ignore_index=True),
                daily=cagr_daily)
            cagr_trades["analysis_window"] = "validation"
            cagr_table = btc_specialist_table(cagr_trades)
            cagr_a_row = cagr_table[(cagr_table["strategy_id"] == "CAGRA") &
                                    (cagr_table["btc_regime"] == "BULL")].iloc[0]
            cagr_b_row = cagr_table[(cagr_table["strategy_id"] == "CAGRB") &
                                    (cagr_table["btc_regime"] == "BULL")].iloc[0]
            assert cagr_a_row["total_regime_days"] == 10
            assert cagr_b_row["total_regime_days"] == 10
            expected_return_a = 0.02 * (10 / (10 / 365.0))
            expected_return_b = 0.02 * (50 / (10 / 365.0))
            assert abs(cagr_a_row["annualized_return"] - expected_return_a) / expected_return_a < 1e-9
            assert abs(cagr_b_row["annualized_return"] - expected_return_b) / expected_return_b < 1e-9
            assert abs(cagr_b_row["annualized_return"] -
                      cagr_a_row["annualized_return"] * 5.0) < 1e-9

            # Drawdown-since-peak position-independence: the exact
            # counterexample DeepSeek-v4-pro gave against the first draft,
            # which reused _regime_drawdown()'s capital-committed-since-
            # GROUP-START normalization (positionally biased - the same
            # loss scored 40% as the group's 1st trade but ~0.4% as its
            # 100th). A -40% trade must score the same drawdown-since-peak
            # whether it is the group's only trade or its 100th, as long as
            # every prior trade only tied (never exceeded) the peak.
            peak_early_days = [pd.Timestamp("2024-07-01", tz="UTC")]
            peak_early_rows = [make("PEAKEARLY", "BULL", 0, peak_early_days[0], -0.40, "PE-0")]
            peak_early_daily = pd.DataFrame([daily_row(peak_early_days[0], "PE-0")])
            peak_early_trades = attach_benchmark(pd.DataFrame(peak_early_rows), daily=peak_early_daily)
            peak_early_trades["analysis_window"] = "validation"
            peak_early_table = btc_specialist_table(peak_early_trades)
            peak_early_row = peak_early_table[
                (peak_early_table["strategy_id"] == "PEAKEARLY") &
                (peak_early_table["btc_regime"] == "BULL")].iloc[0]

            peak_late_days = [pd.Timestamp("2024-07-01", tz="UTC") + pd.Timedelta(days=i)
                              for i in range(100)]
            peak_late_rows = ([make("PEAKLATE", "BULL", i, peak_late_days[i], 0.0, "PL-0")
                              for i in range(99)] +
                             [make("PEAKLATE", "BULL", 99, peak_late_days[99], -0.40, "PL-0")])
            peak_late_daily = pd.DataFrame([daily_row(day, "PL-0") for day in peak_late_days])
            peak_late_trades = attach_benchmark(pd.DataFrame(peak_late_rows), daily=peak_late_daily)
            peak_late_trades["analysis_window"] = "validation"
            peak_late_table = btc_specialist_table(peak_late_trades)
            peak_late_row = peak_late_table[
                (peak_late_table["strategy_id"] == "PEAKLATE") &
                (peak_late_table["btc_regime"] == "BULL")].iloc[0]

            assert abs(peak_early_row["drawdown_since_peak"] - 0.40) < 1e-9
            assert abs(peak_late_row["drawdown_since_peak"] - 0.40) < 1e-9
            # _regime_drawdown() (the OTHER, already-shipped metric) is
            # exactly the positionally-biased one - confirms the two
            # metrics are genuinely different, not accidentally identical.
            assert peak_late_row["max_drawdown"] < 0.01

            # Point-scale boundary checks - anchors and clamping, not full
            # pipeline runs.
            assert _sortino_points(0.0) == 0.0
            assert _sortino_points(1.5) == 50.0
            assert _sortino_points(3.0) == 100.0
            assert _sortino_points(10.0) == 100.0
            assert _sortino_points(-5.0) == 0.0
            assert _drawdown_points(0.0) == 100.0
            assert _drawdown_points(0.40) == 0.0
            assert _drawdown_points(0.60) == 0.0
            assert _annualized_return_points(0.0) == 0.0
            assert _annualized_return_points(0.20) == 50.0
            assert _annualized_return_points(1.0) == 90.0
            assert _annualized_return_points(3.0) == 100.0
            assert _annualized_return_points(10.0) == 100.0
            assert _annualized_return_points(-0.5) == 0.0
            assert _liquidation_points(0.0) == 100.0
            assert _liquidation_points(0.10) == 0.0
            assert _liquidation_points(0.50) == 0.0
            assert _profit_factor_points(1.0) == 20.0
            assert _profit_factor_points(2.0) == 70.0
            assert _profit_factor_points(10.0) == 100.0
            assert _profit_factor_points(0.0) == 0.0
            assert _profit_factor_points(float("inf")) == 100.0
            # bull_row (S1, BULL) is all 12 trades positive - no losing
            # trades at all, so profit_factor is +inf (division by a zero
            # gross_loss), which FreqForge scores 100 (best-in-class), not
            # the 0 a naive NaN/inf fallback would give.
            assert np.isposinf(bull_row["profit_factor"])
            assert _profit_factor_points(bull_row["profit_factor"]) == 100.0
            # Worst-trade severity clamps at 0 for a loss beyond -100%
            # (leverage/short past full stake) rather than swinging
            # arbitrarily negative.
            assert _worst_trade_points(-0.13) == 87.0
            assert _worst_trade_points(-1.0) == 0.0
            assert _worst_trade_points(-2.0) == 0.0

            # LCB letter-grade boundaries.
            assert _lcb_grade(0.021) == "A"
            assert _lcb_grade(0.02) == "B"  # boundary itself is exclusive on the A side
            assert _lcb_grade(0.01) == "B"
            assert _lcb_grade(0.0) == "C"
            assert _lcb_grade(-0.019) == "C"
            assert _lcb_grade(-0.02) == "D"
            assert _lcb_grade(-0.049) == "D"
            assert _lcb_grade(-0.05) == "F"
            assert _lcb_grade(-1.0) == "F"
            assert _lcb_grade(float("nan")) == ""
            assert _lcb_grade(None) == ""
        finally:
            CANDLE_DIR = saved_dir
    print("specialist evaluation selftest: PASS")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trades", type=Path, default=DEFAULT_TRADES)
    parser.add_argument("--strategies", type=str, default="",
                        help="comma-separated strategy_id filter")
    parser.add_argument("--outdir", type=Path, default=OUT)
    parser.add_argument("--joint", action="store_true",
                        help="also compute joint_specialist_table() - only "
                             "valid for an AND-gated trades file (Model 3) "
                             "where btc_regime always equals coin_regime "
                             "whenever both matched; raises otherwise")
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

    joint_table = None
    if args.joint:
        joint_table = joint_specialist_table(trades)
        joint_ranking = rank_specialists(joint_table, "coin_regime")
        _write(joint_table, args.outdir / "joint_specialist_table.csv")
        _write(joint_ranking, args.outdir / "joint_specialist_ranking.csv")

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
        "validation_tier_joint_rows": (
            int((joint_table["tier"] == "VALIDATION").sum()) if joint_table is not None else None),
        "evidence_scope": (
            "Specialist/universal evaluation, strategy_filter above defines "
            "its population (null = every strategy in source_trades). Ranks "
            "only VALIDATION-tier rows (>= %d validation-window episodes "
            "and >= %d trades together); everything else is reported but "
            "never ranked. Excess return is always against the "
            "exposure-matched benchmark - the coin's own spot buy-and-hold, "
            "but over the *entire* BTC-/coin-regime episode a trade fell "
            "in, not just that trade's own open-to-close interval (changed "
            "2026-09-12; see attach_benchmark()'s docstring for why), "
            "never raw profit, and (2026-09-14) averaged one-vote-per-"
            "episode - each episode's own trades summed first, then that "
            "sum averaged across episodes - not a raw per-trade mean, "
            "which let episodes with more trades outweigh others despite "
            "being equally one independent observation; see "
            "_episode_pairs()'s docstring. episode_excess_lcb is a "
            "one-sided 95%% lower confidence bound on that same "
            "per-episode excess return (t-distribution, n=episodes); "
            "lcb_grade is a Gainium-style A-F letter from fixed thresholds "
            "on that bound - see _episode_excess_lcb()/_lcb_grade()'s "
            "docstrings. Both descriptive, not the ranking rule. "
            "max_drawdown is the worst peak-to-trough "
            "drop of a fixed-$%g-stake curve built only from each row's own "
            "matched trades, ordered by close_date - see "
            "_regime_drawdown()'s docstring." % (MIN_EPISODES, MIN_TRADES, START_CAPITAL)
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
          f"coin={manifest['validation_tier_coin_rows']}"
          + (f" joint={manifest['validation_tier_joint_rows']}" if joint_table is not None else "")
          + f"; universal candidates: {manifest['universal_candidates']}; "
          f"strategies with a total-dollar-gain row: "
          f"{manifest['strategies_with_total_dollar_gain']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
