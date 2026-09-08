# Strategy status - current evidence for all 1038 rows

**Generated 2026-09-08 16:12:07 by `strategy_status.py`.** Regenerate it rather than editing it.

**This table decides nothing.** Admission happens only in
`eligibility_expansion_adjudicate.py`; this is a reading of what has
already been decided, collected from the smoke, bias, full-window,
adjudication and convergence stores.

`REGIME_ELIGIBILITY.csv` remains a frozen file and is never
regenerated - but as of 2026-09-03 this table no longer treats its
`regime_eligible=true` rows as automatically usable. The recursion
check that produced them used freqtrade's own hardcoded candle
counts, never converted to a strategy's timeframe, not the
calendar-day ladder every other row is held to; measured under this
audit's own ladder for the first time this week, 64 of the 67 held
up and 1 (`MacdStrategy`) did not. Each of the 67 is now decided by
the same C1/C2/C3 criteria as every other row. Original membership
is kept as provenance in `gate_notes`, never as a reason to skip a
check.

**On the run times.** The runners do not stamp a time into their
records, so `last_tested_at` is recovered from what they leave behind:
a result archive's filename, which carries the run's own clock, or
failing that a log file's modification time, which is close but is the
file's time and is labelled `log_mtime` for that reason. 14 of 1038 rows
have neither and are left empty rather than given an invented time.

## Measurement

| | Strategies |
|---|---:|
| in the manifest | 1038 |
| measured at all | 856 |
| produced trades | 814 |
| carrying a run time | 1024 |

## Cohort

| Cohort | Strategies |
|---|---:|
| `E1_expanded` | 608 |
| `excluded` | 248 |
| `pending` | 59 |
| `exclusion_unconfirmed` | 42 |
| `convergence_candidate` | 37 |
| `too_few_trades` | 25 |
| `not_a_strategy` | 19 |

## Timeframe and signal family

Both read from the strategy's own source by `strategy_classification.py`,
not measured - see that module's docstring for the marker table and its
limits. `timeframe` is blank on 162 rows the source does not state it for. `strategy_type` can be more than one label - most rows carry two or three - and is blank on 154 rows where no marker matched at all, so its counts below add up to more than 1038.

### Timeframe

| Timeframe | Strategies |
|---|---:|
| `5m` | 508 |
| `1h` | 141 |
| `15m` | 85 |
| `1m` | 52 |
| `4h` | 40 |
| `1d` | 23 |
| `30m` | 9 |
| `3m` | 8 |
| `6h` | 3 |
| `2h` | 2 |
| `12h` | 1 |
| `1hr` | 1 |
| `15` | 1 |
| `5h` | 1 |
| `1w` | 1 |

### Signal family

| Type | Strategies |
|---|---:|
| `scalping` | 568 |
| `mean_reversion` | 462 |
| `momentum` | 451 |
| `trend_following` | 245 |
| `volatility_breakout` | 196 |
| `volume_based` | 127 |
| `grid_dca` | 97 |
| `ml_ai` | 46 |
| `stat_arb` | 9 |

## Assumed market phase

**A prediction, written down before the benchmark that will test it.**
It decides nothing here and clears no row. It is recorded now because
a hypothesis formed after the per-phase numbers are on screen is not a
hypothesis - the mirror image of the rule against tuning the regime
labels to make strategies look specialised.

The frozen primary model emits four states. These six split `SIDEWAYS`
on volatility and add a shock phase that outranks the DMI label,
because a dead low-volatility drift and a violent range reward
opposite machinery, and a top-decile volatility day is the market
whichever way ADX points. Owner's decision of 2026-09-05 on
preregistration OPEN item 6; the amendment records it.

| Phase | Market-side rule | Strategies predicted |
|---|---|---:|
| `bear_trend` | `coin_adx >= 25 and coin_minus_di > coin_plus_di` | 34 |
| `bull_trend` | `coin_adx >= 25 and coin_plus_di > coin_minus_di` | 549 |
| `high_vol_shock` | `coin_realized_vol_30d >= 1.291, whatever the DMI state` | 42 |
| `range_choppy` | `coin_adx < 20 and coin_realized_vol_30d >= 0.623` | 271 |
| `range_quiet` | `coin_adx < 20 and coin_realized_vol_30d < 0.623` | 255 |
| `transition` | `20 <= coin_adx < 25` | 23 |

A row may carry more than one phase, and 222 carry none: 47 are model-driven, where the indicators are features of a model and say nothing about which phase it favours, and 175 name no phase-bearing marker at all. Both are left blank rather than given an invented prior - a blank is itself testable, as the prediction that the row is phase-neutral.

`bear_trend` is rare by construction: 934 of 1038 rows are long-only and a long-only strategy cannot earn in a sustained downtrend, so the direction gate removes it whatever the indicators suggest.

## Test duration

Wall-clock seconds each runner timed its own call at, summed per row
across whichever of the trial-run backtest, the bias-store
look-ahead/recursion pair, a later native look-ahead
re-measurement, the warm-up ladder, a wave B recursion attempt, and
the eight-pair full-window backtest actually ran for it - see
`test_duration` in strategy_status.py for why this is a sum rather
than a pick-one-source figure. 4 of 1038 rows carry no stamp at all,
either because nothing has run yet or because no runner on that
path records its own time.

Summed across the 1034 rows that do: **62.6 hours** of this audit's own compute so far.

### Slowest 15

| Strategy | Total | Breakdown |
|---|---:|---|
| `MostOfAll` | 10954.7s | backtest=45.1s; full_window=6406.0s; lookahead_remeasured=4470.1s; recursive_ladder=33.5s |
| `ARIMASTR` | 8061.6s | backtest=317.7s; lookahead=1200.0s; lookahead_remeasured=6185.3s; recursive=113.4s; recursive_ladder=245.2s |
| `Hacklemore` | 7729.0s | backtest=464.1s; lookahead=1200.0s; lookahead_remeasured=6014.3s; recursive=24.0s; recursive_ladder=26.6s |
| `Hacklemore3` | 6982.2s | lookahead_remeasured=6934.8s; recursive_ladder=47.4s |
| `epretrace` | 6656.8s | backtest=65.5s; lookahead=1348.0s; lookahead_remeasured=5130.3s; recursive=22.3s; recursive_ladder=61.2s; recursive_wave_b=29.5s |
| `ExponentialGradientPortfolio` | 4604.3s | backtest=165.6s; lookahead=543.3s; lookahead_remeasured=3837.0s; recursive=25.3s; recursive_ladder=33.1s |
| `ONS_Portfolio` | 4412.3s | backtest=300.0s; lookahead_remeasured=4048.1s; recursive_ladder=64.2s |
| `NostalgiaForInfinityX3` | 3757.8s | backtest=29.5s; lookahead_remeasured=3682.6s; recursive_ladder=45.7s |
| `NostalgiaForInfinityX4` | 3750.4s | backtest=39.6s; lookahead_remeasured=3667.1s; recursive_ladder=43.7s |
| `BreakoutStrategy` | 3176.5s | backtest=65.0s; full_window=3033.6s; lookahead=56.1s; recursive=21.8s |
| `TSPredict` | 2987.1s | backtest=13.2s; full_window=2919.0s; lookahead=44.6s; recursive=10.3s |
| `haGradient` | 2862.0s | backtest=38.4s; lookahead=2772.5s; recursive=24.0s; recursive_ladder=27.1s |
| `HarmonicDivergence` | 2601.6s | backtest=51.3s; full_window=1802.9s; lookahead_remeasured=710.9s; recursive_ladder=36.5s |
| `HurstCycleV6` | 2246.7s | backtest=15.9s; lookahead_remeasured=2176.7s; recursive_ladder=54.1s |
| `Hacklemore2` | 2214.6s | lookahead_remeasured=2167.7s; recursive_ladder=46.9s |

## The order the checks run in

The order is not arbitrary; each step needs what the one before it
produces.

**1. Trial run.** One month over eight pairs: does the strategy start,
and does it trade. A strategy that fails here is `open`, never
`excluded` - no check has seen it, so nothing about it has been
judged. It is labelled `to_be_fixed` until the obstacle is either
removed or shown to be the strategy's own; `repair_verdict` then says
which it is, and that is a separate question from whether the strategy
is still in play.

**2. Recursion, on the warm-up ladder.** Second because it needs no
trades - it compares indicator values, not signals - so it can judge a
strategy the look-ahead check cannot yet touch. It produces the warm-up
at which the indicators settle, which the next step needs.

**3. Look-ahead, at that warm-up.** Freqtrade's `lookahead-analysis`
builds a Backtesting object, and `Backtesting.__init__` takes
`required_startup` from the strategy's declared `startup_candle_count`.
So the check runs at whatever warm-up is in force - and 125 strategies
declare none, which would have their signals compared on indicators
still undefined at the start of the window. Running it after the ladder
means running it at a value shown to settle them. This check needs ten
trades and widens its window rather than failing when there are fewer.

**4. Backtest over the full window.** Only for a strategy that has
cleared both bias checks: `20200301-20260821`, six and a half years
over all eight pairs, at the warm-up the ladder settled on. It is the
most expensive step by a wide margin, which is why it comes last and
only for strategies whose numbers can be trusted. Admission follows
from it, and the market-phase work is built on it.

## What excludes a strategy

Three things, and nothing else. Each is a result this audit produced
itself, on this data, in this runtime.

| | Criterion | Machine test |
|---|---|---|
| C1 | Look-ahead found | `lookahead == "FOUND"` and `lookahead_evidence == "native"` |
| C2 | Recursion found | `recursive_evidence == "convergence:not_settled"` |
| C3 | Never trades | `no_trades_in_full_measurement` with `trade_evidence == "full_window"` |

**A strategy satisfying none of these is not excluded.** It is
unfinished, and `open_work` names what is missing. Five things have
at one time or another excluded strategies here and have been
withdrawn: the source-code trap heuristic, a verdict inherited from
the original sweep, an `NA`, the analyzer refusing for want of a
warm-up, and a failed trial run. Three of them had removed
strategies from the work before anyone looked at them.

C3 has one further condition, and four of the eleven rows failed it:
zero trades is the strategy's own property only when nothing on our
side stopped it trading. `BasketStrategy` marks 8831 entries and
sizes every one to zero, because a portfolio basket measured one
pair at a time has no portfolio to weight against. `MostOfAll` loses
its supertrend to pandas copy-on-write. `FundingCarry` needs funding
rates it cannot have on spot, and `Insomnia_short` raises only short
signals with `can_short` unset. Those four read `open`, not
`excluded`.

The criteria in full are in `exclusion_criteria_list.md`, and every
repair route taken - with the message freqtrade gave beforehand - in
`repair_measures_list.md`. Both are written by this same command,
from these same rows, and the generator refuses a row excluded for a
reason nobody has written down, or a repair route taken and not
recorded. So a new ground or a new repair reaches those lists by
being used, not by being remembered.

## Windows and pairs each check uses

A number cannot be read without knowing what it was measured over.
The checks do not share a window, and two of them do not share the
pair set either.

| Check | Window | Pairs |
|---|---|---|
| Trial run (`profile_smoke`) | `20200301-20200401`, one month | all 8 |
| Bias check, spot | `20190101-20190401`, three months | `BTC/USDT` only |
| Bias check, futures | `20200301-20200401`, one month | `BTC/USDT:USDT` only |
| Look-ahead, first fallback | `20200101-20220101` | BTC only |
| Look-ahead, second fallback | `20200301-20260820` | BTC only |
| Full run (`profile_full_window`) | `20200301-20260821`, 6.5 years | all 8 |

The eight pairs against USDT are BTC, ETH, LTC, XRP, ADA, XLM, XMR and
DASH, at a 0.1 percent fee with `max_open_trades=8`.

**One pair for the bias checks is freqtrade's own doing**, not a choice
of this audit: `recursive-analysis` logs "Using pair BTC/USDT only for
recursive analysis. Replacing whitelist." and replaces whatever the
config holds.

**The look-ahead check widens its window rather than failing.** It needs
ten trades; when the frozen window yields fewer it retries on the first
fallback and then the second, and the record keeps every window it
tried in `attempted_timeranges`. A verdict from a wider window is still
that strategy's verdict, but it was not reached over the same span as
its neighbour's.

**The trial run answers one question:** does the strategy start and
trade. One month over eight pairs is enough for that and cheap. What it
earns is measured later, over the full window.

The warm-up ladder steps in days - 1, 2, 7, 14, 30, 90, 365 - converted
to each strategy's own timeframe, and accepts a rung once every
indicator stays inside 1.0 percent.

## How freqtrade was called

A result is not reproducible from its verdict alone, so each row
carries the command it was produced by. **`recorded`** is the argv that
actually ran. **`reconstructed`** is derived from the run profile and
the window, because nothing stored the call before 2026-09-01; it is
labelled because a reconstruction is a different claim from a
recording. 1401 of 2600 commands are recorded so far, and every new run
adds one.

There is one column per gate, not one per row. A row can carry three
calls and they differ in more than their subcommand, so a single
column could only ever show one of them and drop the rest silently.
The full-window backtest is eight calls, one per pair; the table
leaves the pair as a placeholder and states the count, while every
individual call with its own console output is in
`user_data/freqtrade_runs.log`.

The gates differ in more than their subcommand, which is the reason
this is worth publishing at all. A backtest runs with
`--fee 0.001 --export trades --cache none`. The bias gates add
`--no-color` and use a config that forces `price_side=other`, because
look-ahead analysis forces market orders and freqtrade will not
evaluate a single signal without it. The warm-up ladder passes
`--startup-candle` with every rung at once, which is why one run
reports the whole ladder.

## Passing - 608 strategies

Every original gate returned `PASS`: measured in its native mode,
produced trades, clean look-ahead and recursion, complete candle
coverage, no published trap.

| Strategy | Profile | Cohort | Trades | Recursive evidence | Tested | Results |
|---|---|---|---:|---|---|---|
| `A9AV` | `spot_long` | `E1_expanded` | 4941 | `convergence:288:warmup_supplied` | 2026-09-06 15:09:39 | [archive](user_data/profile_smoke/A9AV-fb0d7493-2026-09-06_15-09-39.zip) [log](user_data/convergence_logs/A9AV-ladder.log) |
| `ADXMomentum` | `spot_long` | `E1_expanded` | 2 | `convergence:336:warmup_supplied` | 2026-09-06 14:47:45 | [archive](user_data/profile_smoke/ADXMomentum-d748d610-2026-09-06_14-47-45.zip) [log](user_data/convergence_logs/ADXMomentum-ladder.log) |
| `ADX_15M_USDT` | `spot_long` | `E1_expanded` | 165 | `convergence:672:warmup_supplied` | 2026-09-01 19:31:10 | [archive](user_data/profile_smoke/ADX_15M_USDT-2026-09-01_19-31-10.zip) [log](user_data/convergence_logs/ADX_15M_USDT-ladder.log) |
| `ADX_15M_USDT2` | `spot_long` | `E1_expanded` | 178 | `convergence:672:warmup_supplied` | 2026-09-01 19:31:48 | [archive](user_data/profile_smoke/ADX_15M_USDT2-2026-09-01_19-31-48.zip) [log](user_data/convergence_logs/ADX_15M_USDT2-ladder.log) |
| `ASDTSRockwellTrading` | `spot_long` | `E1_expanded` | 29952 | `convergence:288:warmup_supplied` | 2026-09-01 15:32:20 | [log](user_data/convergence_logs/ASDTSRockwellTrading-ladder.log) |
| `ActionZone` | `spot_long` | `E1_expanded` | 561 | `convergence:90:warmup_supplied` | 2026-09-01 12:59:33 | [log](user_data/convergence_logs/ActionZone-ladder.log) |
| `AdaptiveMAStrategy` | `spot_long` | `E1_expanded` | 3195 | `convergence:288:warmup_supplied` | 2026-09-01 12:07:18 | [log](user_data/convergence_logs/AdaptiveMAStrategy-ladder.log) |
| `AdxSmas` | `spot_long` | `E1_expanded` | 7004 | `convergence:336:warmup_supplied` | 2026-09-01 13:33:11 | [log](user_data/convergence_logs/AdxSmas-ladder.log) |
| `AdxSmasS` | `futures_short` | `E1_expanded` | 74 | `convergence:336:warmup_supplied` | 2026-09-01 13:34:00 | [log](user_data/convergence_logs/AdxSmasS-ladder.log) |
| `AdxStrengthStrategy` | `spot_long` | `E1_expanded` | 16952 | `convergence:288:warmup_supplied` | 2026-09-01 12:07:43 | [log](user_data/convergence_logs/AdxStrengthStrategy-ladder.log) |
| `AlligatorStrat` | `spot_long` | `E1_expanded` | 48 | `convergence:540:warmup_supplied` | 2026-09-01 19:32:25 | [archive](user_data/profile_smoke/AlligatorStrat-2026-09-01_19-32-25.zip) [log](user_data/convergence_logs/AlligatorStrat-ladder.log) |
| `AlligatorStrategy` | `spot_long` | `E1_expanded` | 1839 | `convergence:720:warmup_supplied` | 2026-09-01 13:00:43 | [log](user_data/convergence_logs/AlligatorStrategy-ladder.log) |
| `AlmgrenChrissStrategy` | `futures_long_short` | `E1_expanded` | 818 | `convergence:192:warmup_supplied` | 2026-09-01 13:01:08 | [log](user_data/convergence_logs/AlmgrenChrissStrategy-ladder.log) |
| `AlwaysBuy` | `spot_long` | `E1_expanded` | 32359 | `convergence:288:warmup_supplied` | 2026-09-01 23:39:39 | [log](user_data/convergence_logs/AlwaysBuy-ladder.log) |
| `Apollo11` | `spot_long` | `E1_expanded` | 6378 | `convergence:1344:warmup_supplied` | 2026-09-01 13:01:32 | [log](user_data/convergence_logs/Apollo11-ladder.log) |
| `AroonTrendStrategy` | `spot_long` | `E1_expanded` | 24271 | `convergence:288:warmup_supplied` | 2026-09-01 12:08:07 | [log](user_data/convergence_logs/AroonTrendStrategy-ladder.log) |
| `AtrTrailingStopStrategy` | `spot_long` | `E1_expanded` | 24938 | `convergence:288:warmup_supplied` | 2026-09-01 12:08:31 | [log](user_data/convergence_logs/AtrTrailingStopStrategy-ladder.log) |
| `AverageStrategy` | `spot_long` | `E1_expanded` | 2875 | `convergence:84:warmup_supplied` | 2026-09-01 13:34:48 | [log](user_data/convergence_logs/AverageStrategy-ladder.log) |
| `AwesomeMacd` | `spot_long` | `E1_expanded` | 3989 | `convergence:336:warmup_supplied` | 2026-09-02 06:51:58 | [log](user_data/convergence_logs/AwesomeMacd-ladder.log) |
| `BB10fall` | `spot_long` | `E1_expanded` | 50 | `convergence:168:warmup_supplied` | 2026-09-05 15:09:31 | [archive](user_data/profile_smoke/BB10fall-cef5331b-2026-09-05_15-09-31.zip) [log](user_data/convergence_logs/BB10fall-cef5331b-ladder.log) |
| `BBMod` | `spot_long` | `E1_expanded` | 300 | `convergence:2016:warmup_supplied` | 2026-09-06 15:09:06 | [archive](user_data/profile_smoke/BBMod-c3880bce-2026-09-06_15-09-06.zip) [log](user_data/convergence_logs/BBMod-ladder.log) |
| `BBRSI` | `spot_long` | `E1_expanded` | 11 | `convergence:168:warmup_supplied` | 2026-09-04 10:32:03 | [archive](user_data/profile_smoke/BBRSI-0d31007a-2026-09-04_10-32-03.zip) [log](user_data/convergence_logs/BBRSI-0d31007a-ladder.log) |
| `BBRSI2` | `spot_long` | `E1_expanded` | 24422 | `convergence:1440:warmup_supplied` | 2026-09-01 15:33:59 | [log](user_data/convergence_logs/BBRSI2-ladder.log) |
| `BBRSI21` | `spot_long` | `E1_expanded` | 5845 | `convergence:288:warmup_supplied` | 2026-09-01 15:34:51 | [log](user_data/convergence_logs/BBRSI21-ladder.log) |
| `BBRSI3366` | `spot_long` | `E1_expanded` | 26873 | `convergence:288:warmup_supplied` | 2026-09-01 15:35:41 | [log](user_data/convergence_logs/BBRSI3366-ladder.log) |
| `BBRSI4cust` | `spot_long` | `E1_expanded` | 22886 | `convergence:192:warmup_supplied` | 2026-09-01 12:08:55 | [log](user_data/convergence_logs/BBRSI4cust-ladder.log) |
| `BBRSINaiveStrategy` | `spot_long` | `E1_expanded` | 20022 | `convergence:192:warmup_supplied` | 2026-09-01 12:09:19 | [log](user_data/convergence_logs/BBRSINaiveStrategy-ladder.log) |
| `BBRSIOptim2020Strategy` | `spot_long` | `E1_expanded` | 34955 | `convergence:288:warmup_supplied` | 2026-09-01 12:09:44 | [log](user_data/convergence_logs/BBRSIOptim2020Strategy-ladder.log) |
| `BBRSIOptimStrategy` | `spot_long` | `E1_expanded` | 10697 | `convergence:288:warmup_supplied` | 2026-09-01 12:10:08 | [log](user_data/convergence_logs/BBRSIOptimStrategy-ladder.log) |
| `BBRSIOptimizedStrategy` | `spot_long` | `E1_expanded` | 33132 | `convergence:288:warmup_supplied` | 2026-09-01 13:02:19 | [log](user_data/convergence_logs/BBRSIOptimizedStrategy-ladder.log) |
| `BBRSIS` | `spot_long` | `E1_expanded` |  | `convergence:8640:warmup_supplied` | 2026-09-03 14:40:12 | [log](user_data/profile_smoke_logs/BBRSIS.log) |
| `BBRSIStrategy` | `spot_long` | `E1_expanded` | 12330 | `convergence:192:warmup_supplied` | 2026-09-01 12:10:32 | [log](user_data/convergence_logs/BBRSIStrategy-ladder.log) |
| `BBRSITV` | `spot_long` | `E1_expanded` | 420 | `convergence:2016:warmup_supplied` | 2026-09-01 13:02:44 | [log](user_data/convergence_logs/BBRSITV-ladder.log) |
| `BBRSIoriginal` | `spot_long` | `E1_expanded` | 47 | `convergence:168:warmup_supplied` | 2026-09-01 19:33:39 | [archive](user_data/profile_smoke/BBRSIoriginal-2026-09-01_19-33-39.zip) [log](user_data/convergence_logs/BBRSIoriginal-ladder.log) |
| `BBRSIv2` | `spot_long` | `E1_expanded` | 584 | `convergence:192:warmup_supplied` | 2026-09-03 13:43:03 | [log](user_data/convergence_logs/BBRSIv2-ladder.log) |
| `BB_RPB_TSL_RNG` | `spot_long` | `E1_expanded` | 778 | `convergence:2016:warmup_supplied` | 2026-09-01 13:35:37 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG-ladder.log) |
| `BB_RPB_TSL_RNG_2` | `spot_long` | `E1_expanded` | 776 | `convergence:2016:warmup_supplied` | 2026-09-01 15:36:32 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG_2-ladder.log) |
| `BB_RPB_TSL_RNG_TBS` | `spot_long` | `E1_expanded` | 778 | `convergence:2016:warmup_supplied` | 2026-09-01 13:36:25 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG_TBS-ladder.log) |
| `BB_RPB_TSL_RNG_TBS_GOLD` | `spot_long` | `E1_expanded` | 969 | `convergence:2016:warmup_supplied` | 2026-09-01 13:37:28 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG_TBS_GOLD-ladder.log) |
| `BB_RPB_TSL_RNG_VWAP` | `spot_long` | `E1_expanded` | 1289 | `convergence:2016:warmup_supplied` | 2026-09-01 12:10:58 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG_VWAP-ladder.log) |
| `BB_RPB_TSL_c7c477d_20211030` | `spot_long` | `E1_expanded` | 494 | `convergence:2016:warmup_supplied` | 2026-09-06 08:08:54 | [log](user_data/convergence_logs/BB_RPB_TSL_c7c477d_20211030-2ca1ddc5-ladder.log) |
| `BB_RSI` | `spot_long` | `E1_expanded` | 421 | `convergence:168:warmup_supplied` | 2026-09-01 19:34:17 | [archive](user_data/profile_smoke/BB_RSI-2026-09-01_19-34-17.zip) [log](user_data/convergence_logs/BB_RSI-ladder.log) |
| `BB_RTR` | `spot_long` | `E1_expanded` | 987 | `convergence:2016:warmup_supplied` | 2026-09-01 12:11:28 | [log](user_data/convergence_logs/BB_RTR-ladder.log) |
| `BB_Strategy04` | `spot_long` | `E1_expanded` | 56 | `convergence:168:warmup_supplied` | 2026-09-01 19:34:54 | [archive](user_data/profile_smoke/BB_Strategy04-2026-09-01_19-34-54.zip) [log](user_data/convergence_logs/BB_Strategy04-ladder.log) |
| `BBands` | `spot_long` | `E1_expanded` | 7063 | `convergence:1440:warmup_supplied` | 2026-09-01 13:04:20 | [log](user_data/convergence_logs/BBands-ladder.log) |
| `BBandsRSI` | `spot_long` | `E1_expanded` | 24684 | `convergence:288:warmup_supplied` | 2026-09-01 13:04:45 | [log](user_data/convergence_logs/BBandsRSI-ladder.log) |
| `BBlower` | `spot_long` | `E1_expanded` | 1790 | `convergence:576:warmup_supplied` | 2026-09-01 15:37:20 | [log](user_data/convergence_logs/BBlower-ladder.log) |
| `Babico_SMA5xBBmid` | `spot_long` | `E1_expanded` | 79 | `convergence:30:warmup_supplied` | 2026-09-01 13:38:15 | [log](user_data/convergence_logs/Babico_SMA5xBBmid-ladder.log) |
| `Bandtastic` | `spot_long` | `E1_expanded` | 28745 | `convergence:1344:warmup_supplied` | 2026-09-01 15:38:10 | [log](user_data/convergence_logs/Bandtastic-ladder.log) |
| `BbRoi` | `spot_long` | `E1_expanded` | 393 | `convergence:1344:warmup_supplied` | 2026-09-01 19:35:31 | [archive](user_data/profile_smoke/BbRoi-2026-09-01_19-35-31.zip) [log](user_data/convergence_logs/BbRoi-ladder.log) |
| `BbWidthExpansionStrategy` | `spot_long` | `E1_expanded` | 21692 | `convergence:288:warmup_supplied` | 2026-09-01 12:11:52 | [log](user_data/convergence_logs/BbWidthExpansionStrategy-ladder.log) |
| `BbandRsi` | `spot_long` | `E1_expanded` | 16106 | `convergence:1440:warmup_supplied` | 2026-09-03 19:39:25 | [log](user_data/convergence_logs/BbandRsi-6dcf5b91-ladder.log) |
| `BbandRsiRolling` | `spot_long` | `E1_expanded` | 17916 | `convergence:288:warmup_supplied` | 2026-09-01 13:39:54 | [log](user_data/convergence_logs/BbandRsiRolling-ladder.log) |
| `BigPete` | `spot_long` | `E1_expanded` | 566 | `convergence:288:warmup_supplied` | 2026-09-06 15:08:15 | [archive](user_data/profile_smoke/BigPete-b194f963-2026-09-06_15-08-15.zip) [log](user_data/convergence_logs/BigPete-ladder.log) |
| `BigTrader` | `spot_long` | `E1_expanded` | 166 | `convergence:60` | 2026-09-03 13:43:30 | [log](user_data/convergence_logs/BigTrader-ladder.log) |
| `BigZ03` | `spot_long` | `E1_expanded` | 925 | `convergence:2016:warmup_supplied` | 2026-09-03 13:43:56 | [log](user_data/convergence_logs/BigZ03-ladder.log) |
| `BigZ03HO` | `spot_long` | `E1_expanded` | 7275 | `convergence:2016:warmup_supplied` | 2026-09-03 13:44:23 | [log](user_data/convergence_logs/BigZ03HO-ladder.log) |
| `BigZ04_TSL3` | `spot_long` | `E1_expanded` | 1643 | `convergence:2016:warmup_supplied` | 2026-09-03 13:44:49 | [log](user_data/convergence_logs/BigZ04_TSL3-ladder.log) |
| `BigZ04_TSL4` | `spot_long` | `E1_expanded` | 1756 | `convergence:288` | 2026-09-03 13:45:16 | [log](user_data/convergence_logs/BigZ04_TSL4-ladder.log) |
| `BigZ07Next` | `spot_long` | `E1_expanded` | 1754 | `convergence:2016:warmup_supplied` | 2026-09-01 12:15:15 | [log](user_data/convergence_logs/BigZ07Next-ladder.log) |
| `BigZ07Next2` | `spot_long` | `E1_expanded` | 1716 | `convergence:2016:warmup_supplied` | 2026-09-01 12:15:43 | [log](user_data/convergence_logs/BigZ07Next2-ladder.log) |
| `BinClucMad` | `spot_long` | `E1_expanded` | 2517 | `convergence:2016:warmup_supplied` | 2026-09-03 13:45:43 | [log](user_data/convergence_logs/BinClucMad-ladder.log) |
| `BinClucMadV1` | `spot_long` | `E1_expanded` | 1164 | `convergence:2016:warmup_supplied` | 2026-09-01 12:16:09 | [log](user_data/convergence_logs/BinClucMadV1-ladder.log) |
| `BinHV27` | `spot_long` | `E1_expanded` | 11503 | `convergence:576:warmup_supplied` | 2026-09-01 13:40:42 | [log](user_data/convergence_logs/BinHV27-ladder.log) |
| `BinHV27F` | `futures_long` | `E1_expanded` | 154 | `convergence:576:warmup_supplied` | 2026-09-02 06:53:08 | [log](user_data/convergence_logs/BinHV27F-ladder.log) |
| `BinHV27_short` | `futures_long_short` | `E1_expanded` | 5 | `convergence:576:warmup_supplied` | 2026-09-03 19:04:53 | [log](user_data/convergence_logs/BinHV27_short-ladder.log) |
| `BinHV27_werkkrew` | `spot_long` | `E1_expanded` | 127 | `convergence:576:warmup_supplied` | 2026-09-03 21:02:46 | [archive](user_data/profile_smoke/BinHV27_werkkrew-3a997e27-2026-09-03_21-02-46.zip) [log](user_data/convergence_logs/BinHV27_werkkrew-ladder.log) |
| `BinHV45` | `spot_long` | `E1_expanded` | 749 | `convergence:1440:warmup_supplied` | 2026-09-01 23:46:36 | [log](user_data/convergence_logs/BinHV45-ladder.log) |
| `BinHV45HO` | `spot_long` | `E1_expanded` | 389 | `convergence:1440:warmup_supplied` | 2026-09-01 13:41:32 | [log](user_data/convergence_logs/BinHV45HO-ladder.log) |
| `BinHV45_kanaxe` | `spot_long` | `E1_expanded` | 1798 | `convergence:1440:warmup_supplied` | 2026-09-01 23:47:31 | [log](user_data/convergence_logs/BinHV45_kanaxe-ladder.log) |
| `BinHV45_stash` | `spot_long` | `E1_expanded` | 1700 | `convergence:1440:warmup_supplied` | 2026-09-01 23:48:23 | [log](user_data/convergence_logs/BinHV45_stash-ladder.log) |
| `BinHV45_werkkrew` | `spot_long` | `E1_expanded` | 760 | `convergence:1440:warmup_supplied` | 2026-09-01 23:49:18 | [log](user_data/convergence_logs/BinHV45_werkkrew-ladder.log) |
| `BinMfiBTCv5003` | `spot_long` | `E1_expanded` | 171 | `convergence:288:warmup_supplied` | 2026-09-01 13:09:38 | [log](user_data/convergence_logs/BinMfiBTCv5003-ladder.log) |
| `BollingerBandStrategy` | `spot_long` | `E1_expanded` | 16302 | `convergence:480:warmup_supplied` | 2026-09-01 23:50:09 | [log](user_data/convergence_logs/BollingerBandStrategy-ladder.log) |
| `BollingerBounceStrategy` | `spot_long` | `E1_expanded` | 11490 | `convergence:576:warmup_supplied` | 2026-09-01 12:16:36 | [log](user_data/convergence_logs/BollingerBounceStrategy-ladder.log) |
| `BopTrendStrategy` | `spot_long` | `E1_expanded` | 24576 | `convergence:288:warmup_supplied` | 2026-09-01 12:17:01 | [log](user_data/convergence_logs/BopTrendStrategy-ladder.log) |
| `BullishEngulfingStrategy` | `spot_long` | `E1_expanded` | 24227 | `convergence:576:warmup_supplied` | 2026-09-01 12:17:26 | [log](user_data/convergence_logs/BullishEngulfingStrategy-ladder.log) |
| `BuyOnly` | `spot_long` | `E1_expanded` | 2779 | `convergence:672:warmup_supplied` | 2026-09-01 12:17:52 | [log](user_data/convergence_logs/BuyOnly-ladder.log) |
| `BuyOrDie` | `spot_long` | `E1_expanded` | 3247 | `convergence:288:warmup_supplied` | 2026-09-01 15:38:59 | [log](user_data/convergence_logs/BuyOrDie-ladder.log) |
| `BuyRegions` | `spot_long` | `E1_expanded` | 4672 | `convergence:288:warmup_supplied` | 2026-09-04 06:15:11 | [log](user_data/convergence_logs/BuyRegions-dff7fcd2-ladder.log) |
| `CBPete9` | `spot_long` | `E1_expanded` | 132 | `convergence:2016:warmup_supplied` | 2026-09-06 15:08:25 | [archive](user_data/profile_smoke/CBPete9-6ffadd4c-2026-09-06_15-08-25.zip) [log](user_data/convergence_logs/CBPete9-ladder.log) |
| `CCI_BB` | `spot_long` | `E1_expanded` | 926 | `convergence:288:warmup_supplied` | 2026-09-01 23:51:00 | [log](user_data/convergence_logs/CCI_BB-ladder.log) |
| `CMCWinner` | `spot_long` | `E1_expanded` | 6632 | `convergence:672:warmup_supplied` | 2026-09-01 13:42:18 | [log](user_data/convergence_logs/CMCWinner-ladder.log) |
| `CTIBS` | `spot_long` | `E1_expanded` | 5553 | `convergence:672:warmup_supplied` | 2026-09-01 12:18:16 | [log](user_data/convergence_logs/CTIBS-ladder.log) |
| `Candle2` | `spot_long` | `E1_expanded` | 7626 | `convergence:168:warmup_supplied` | 2026-09-01 15:39:47 | [log](user_data/convergence_logs/Candle2-ladder.log) |
| `CciMeanReversionStrategy` | `spot_long` | `E1_expanded` | 26207 | `convergence:576:warmup_supplied` | 2026-09-01 12:18:42 | [log](user_data/convergence_logs/CciMeanReversionStrategy-ladder.log) |
| `Cenderawasih_30m` | `spot_long` | `E1_expanded` | 1 | `convergence:672:warmup_supplied` | 2026-09-01 20:43:33 | [archive](user_data/profile_smoke/Cenderawasih_30m-2026-09-01_20-43-33.zip) [log](user_data/convergence_logs/Cenderawasih_30m-ladder.log) |
| `Cenderawasih_3_kucoin` | `spot_long` | `E1_expanded` | 59 | `convergence:288:warmup_supplied` | 2026-09-01 20:42:41 | [archive](user_data/profile_smoke/Cenderawasih_3_kucoin-2026-09-01_20-42-41.zip) [log](user_data/convergence_logs/Cenderawasih_3_kucoin-ladder.log) |
| `ChaikinMoneyFlowStrategy` | `spot_long` | `E1_expanded` | 29264 | `convergence:288:warmup_supplied` | 2026-09-01 12:19:08 | [log](user_data/convergence_logs/ChaikinMoneyFlowStrategy-ladder.log) |
| `Chandem` | `spot_long` | `E1_expanded` | 16308 | `convergence:2016:warmup_supplied` | 2026-09-01 15:40:37 | [log](user_data/convergence_logs/Chandem-ladder.log) |
| `Chandemtwo` | `spot_long` | `E1_expanded` | 18812 | `convergence:2016:warmup_supplied` | 2026-09-01 15:41:25 | [log](user_data/convergence_logs/Chandemtwo-ladder.log) |
| `Chispei` | `spot_long` | `E1_expanded` | 50 | `convergence:42:warmup_supplied` | 2026-09-01 19:36:09 | [archive](user_data/profile_smoke/Chispei-2026-09-01_19-36-09.zip) [log](user_data/convergence_logs/Chispei-62b19ed2-ladder.log) |
| `Cluc4` | `spot_long` | `E1_expanded` | 4881 | `convergence:1440:warmup_supplied` | 2026-09-01 15:42:17 | [log](user_data/convergence_logs/Cluc4-ladder.log) |
| `Cluc4werk` | `spot_long` | `E1_expanded` | 3269 | `convergence:1440:warmup_supplied` | 2026-09-01 13:43:54 | [log](user_data/convergence_logs/Cluc4werk-ladder.log) |
| `Cluc5werk` | `spot_long` | `E1_expanded` | 2210 | `convergence:1440:warmup_supplied` | 2026-09-01 13:44:44 | [log](user_data/convergence_logs/Cluc5werk-ladder.log) |
| `Cluc7werk` | `spot_long` | `E1_expanded` | 1719 | `convergence:1440:warmup_supplied` | 2026-09-03 13:46:37 | [log](user_data/convergence_logs/Cluc7werk-ladder.log) |
| `ClucFiatROI` | `spot_long` | `E1_expanded` | 6026 | `convergence:288:warmup_supplied` | 2026-09-01 13:11:38 | [log](user_data/convergence_logs/ClucFiatROI-ladder.log) |
| `ClucFiatSlow` | `spot_long` | `E1_expanded` | 6026 | `convergence:288:warmup_supplied` | 2026-09-01 13:12:03 | [log](user_data/convergence_logs/ClucFiatSlow-ladder.log) |
| `ClucHAnix` | `spot_long` | `E1_expanded` | 480 | `convergence:1440:warmup_supplied` | 2026-09-01 13:45:46 | [log](user_data/convergence_logs/ClucHAnix-ladder.log) |
| `ClucHAnix_5M_E0V1E` | `spot_long` | `E1_expanded` | 5459 | `convergence:288:warmup_supplied` | 2026-09-03 13:47:08 | [log](user_data/convergence_logs/ClucHAnix_5M_E0V1E-ladder.log) |
| `ClucHAnix_5m` | `spot_long` | `E1_expanded` | 2834 | `convergence:288:warmup_supplied` | 2026-09-03 13:47:38 | [log](user_data/convergence_logs/ClucHAnix_5m-ladder.log) |
| `ClucHAnix_5m1` | `spot_long` | `E1_expanded` | 3049 | `convergence:288:warmup_supplied` | 2026-09-03 13:48:10 | [log](user_data/convergence_logs/ClucHAnix_5m1-ladder.log) |
| `ClucHAnix_5m_old` | `spot_long` | `E1_expanded` | 2834 | `convergence:288:warmup_supplied` | 2026-09-03 13:48:41 | [log](user_data/convergence_logs/ClucHAnix_5m_old-ladder.log) |
| `ClucHAnix_BB_RPB` | `spot_long` | `E1_expanded` | 242 | `convergence:2880:warmup_supplied` | 2026-09-06 14:49:03 | [archive](user_data/profile_smoke/ClucHAnix_BB_RPB-d5edb88c-2026-09-06_14-49-03.zip) [log](user_data/convergence_logs/ClucHAnix_BB_RPB-ladder.log) |
| `ClucHAnix_BB_RPB_HO2` | `spot_long` | `E1_expanded` | 201 | `convergence:2880:warmup_supplied` | 2026-09-06 14:50:18 | [archive](user_data/profile_smoke/ClucHAnix_BB_RPB_HO2-50399031-2026-09-06_14-50-18.zip) [log](user_data/convergence_logs/ClucHAnix_BB_RPB_HO2-ladder.log) |
| `ClucHAnix_BB_RPB_MOD` | `spot_long` | `E1_expanded` | 217 | `convergence:2880:warmup_supplied` | 2026-09-06 14:51:41 | [archive](user_data/profile_smoke/ClucHAnix_BB_RPB_MOD-4949016b-2026-09-06_14-51-41.zip) [log](user_data/convergence_logs/ClucHAnix_BB_RPB_MOD-ladder.log) |
| `ClucHAnix_hhll` | `spot_long` | `E1_expanded` | 2278 | `convergence:2016:warmup_supplied` | 2026-09-01 13:12:56 | [log](user_data/convergence_logs/ClucHAnix_hhll-ladder.log) |
| `ClucHAwerk` | `spot_long` | `E1_expanded` | 2183 | `convergence:1440:warmup_supplied` | 2026-09-03 13:49:23 | [log](user_data/convergence_logs/ClucHAwerk-ladder.log) |
| `ClucMay72018` | `spot_long` | `E1_expanded` | 2507 | `convergence:288:warmup_supplied` | 2026-09-01 13:46:34 | [log](user_data/convergence_logs/ClucMay72018-ladder.log) |
| `CofiBitStrategy` | `spot_long` | `E1_expanded` | 27444 | `convergence:288:warmup_supplied` | 2026-09-01 13:47:22 | [log](user_data/convergence_logs/CofiBitStrategy-ladder.log) |
| `CombinedBinHAndCluc` | `spot_long` | `E1_expanded` | 3540 | `convergence:288:warmup_supplied` | 2026-09-01 13:48:09 | [log](user_data/convergence_logs/CombinedBinHAndCluc-ladder.log) |
| `CombinedBinHAndCluc2021` | `spot_long` | `E1_expanded` | 3297 | `convergence:288:warmup_supplied` | 2026-09-01 13:48:57 | [log](user_data/convergence_logs/CombinedBinHAndCluc2021-ladder.log) |
| `CombinedBinHAndCluc2021Bull` | `spot_long` | `E1_expanded` | 3876 | `convergence:288:warmup_supplied` | 2026-09-01 13:49:45 | [log](user_data/convergence_logs/CombinedBinHAndCluc2021Bull-ladder.log) |
| `CombinedBinHAndClucHyper` | `spot_long` | `E1_expanded` | 90 | `convergence:1440:warmup_supplied` | 2026-09-06 14:59:31 | [archive](user_data/profile_smoke/CombinedBinHAndClucHyper-48a908dc-2026-09-06_14-59-31.zip) [log](user_data/convergence_logs/CombinedBinHAndClucHyper-ladder.log) |
| `CombinedBinHAndClucHyperV0` | `spot_long` | `E1_expanded` | 4252 | `convergence:1440:warmup_supplied` | 2026-09-01 15:43:08 | [log](user_data/convergence_logs/CombinedBinHAndClucHyperV0-ladder.log) |
| `CombinedBinHAndClucHyperV3` | `spot_long` | `E1_expanded` | 1810 | `convergence:1440:warmup_supplied` | 2026-09-01 15:43:59 | [log](user_data/convergence_logs/CombinedBinHAndClucHyperV3-ladder.log) |
| `CombinedBinHAndClucV2` | `spot_long` | `E1_expanded` | 728 | `convergence:576:warmup_supplied` | 2026-09-01 13:15:19 | [log](user_data/convergence_logs/CombinedBinHAndClucV2-ladder.log) |
| `CombinedBinHAndClucV3` | `spot_long` | `E1_expanded` | 2589 | `convergence:2016:warmup_supplied` | 2026-09-03 13:49:49 | [log](user_data/convergence_logs/CombinedBinHAndClucV3-ladder.log) |
| `CombinedBinHAndClucV4` | `spot_long` | `E1_expanded` | 2965 | `convergence:288:warmup_supplied` | 2026-09-01 13:15:44 | [log](user_data/convergence_logs/CombinedBinHAndClucV4-ladder.log) |
| `CombinedBinHAndClucV5` | `spot_long` | `E1_expanded` | 2985 | `convergence:288:warmup_supplied` | 2026-09-01 13:16:09 | [log](user_data/convergence_logs/CombinedBinHAndClucV5-ladder.log) |
| `CombinedBinHAndClucV5Hyperoptable` | `spot_long` | `E1_expanded` | 2705 | `convergence:288:warmup_supplied` | 2026-09-01 12:21:09 | [log](user_data/convergence_logs/CombinedBinHAndClucV5Hyperoptable-ladder.log) |
| `CombinedBinHAndClucV6` | `spot_long` | `E1_expanded` | 1724 | `convergence:2016:warmup_supplied` | 2026-09-03 13:50:16 | [log](user_data/convergence_logs/CombinedBinHAndClucV6-ladder.log) |
| `CombinedBinHAndClucV7` | `spot_long` | `E1_expanded` | 889 | `convergence:2016:warmup_supplied` | 2026-09-03 13:50:43 | [log](user_data/convergence_logs/CombinedBinHAndClucV7-ladder.log) |
| `CombinedBinHAndClucV8` | `spot_long` | `E1_expanded` | 884 | `convergence:2016:warmup_supplied` | 2026-09-01 13:16:34 | [log](user_data/convergence_logs/CombinedBinHAndClucV8-ladder.log) |
| `CombinedBinHAndClucV8Hyper` | `spot_long` | `E1_expanded` | 1243 | `convergence:2016:warmup_supplied` | 2026-09-01 13:16:59 | [log](user_data/convergence_logs/CombinedBinHAndClucV8Hyper-ladder.log) |
| `CombinedBinHAndClucV8XH` | `spot_long` | `E1_expanded` | 642 | `convergence:2016:warmup_supplied` | 2026-09-01 13:17:23 | [log](user_data/convergence_logs/CombinedBinHAndClucV8XH-ladder.log) |
| `CombinedBinHAndClucV8XHO` | `spot_long` | `E1_expanded` | 851 | `convergence:2016:warmup_supplied` | 2026-09-01 12:21:34 | [log](user_data/convergence_logs/CombinedBinHAndClucV8XHO-ladder.log) |
| `CombinedBinHClucAndMADV3` | `spot_long` | `E1_expanded` | 1717 | `convergence:2016:warmup_supplied` | 2026-09-03 13:51:10 | [log](user_data/convergence_logs/CombinedBinHClucAndMADV3-ladder.log) |
| `CombinedBinHClucAndMADV5` | `spot_long` | `E1_expanded` | 1644 | `convergence:2016:warmup_supplied` | 2026-09-03 13:51:37 | [log](user_data/convergence_logs/CombinedBinHClucAndMADV5-ladder.log) |
| `CombinedBinHClucAndMADV6` | `spot_long` | `E1_expanded` | 1616 | `convergence:2016:warmup_supplied` | 2026-09-03 13:52:03 | [log](user_data/convergence_logs/CombinedBinHClucAndMADV6-ladder.log) |
| `CombinedBinHClucAndMADV9` | `spot_long` | `E1_expanded` | 2842 | `convergence:2016:warmup_supplied` | 2026-09-03 13:52:30 | [log](user_data/convergence_logs/CombinedBinHClucAndMADV9-ladder.log) |
| `Combined_Indicators` | `spot_long` | `E1_expanded` | 2969 | `convergence:1440:warmup_supplied` | 2026-09-01 15:44:51 | [log](user_data/convergence_logs/Combined_Indicators-ladder.log) |
| `Combined_NFIv6_SMA` | `spot_long` | `E1_expanded` | 951 | `convergence:2016:warmup_supplied` | 2026-09-01 13:17:48 | [log](user_data/convergence_logs/Combined_NFIv6_SMA-ladder.log) |
| `Combined_NFIv7_SMA` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 12:22:00 | [log](user_data/convergence_logs/Combined_NFIv7_SMA-ladder.log) |
| `Combined_NFIv7_SMA_Rallipanos_20210707` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 12:22:25 | [log](user_data/convergence_logs/Combined_NFIv7_SMA_Rallipanos_20210707-ladder.log) |
| `Combined_NFIv7_SMA_bAdBoY_20211204` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 12:22:51 | [log](user_data/convergence_logs/Combined_NFIv7_SMA_bAdBoY_20211204-ladder.log) |
| `CompositeScoreStrategy` | `spot_long` | `E1_expanded` | 28771 | `convergence:288:warmup_supplied` | 2026-09-01 12:23:15 | [log](user_data/convergence_logs/CompositeScoreStrategy-ladder.log) |
| `ConsensusShort` | `futures_long_short` | `E1_expanded` | 414 | `convergence:288:warmup_supplied` | 2026-09-02 06:55:30 | [log](user_data/convergence_logs/ConsensusShort-ladder.log) |
| `CoppockCurveStrategy` | `spot_long` | `E1_expanded` | 22332 | `convergence:288:warmup_supplied` | 2026-09-01 12:23:39 | [log](user_data/convergence_logs/CoppockCurveStrategy-ladder.log) |
| `CrossEMAStrategy` | `spot_long` | `E1_expanded` | 4063 | `convergence:168:warmup_supplied` | 2026-09-01 13:18:36 | [log](user_data/convergence_logs/CrossEMAStrategy-ladder.log) |
| `CryptoFrog` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:43:11 | [log](user_data/profile_smoke_logs/CryptoFrog.log) |
| `CryptoFrogHO` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:44:17 | [log](user_data/profile_smoke_logs/CryptoFrogHO.log) |
| `CryptoFrogHO2` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:45:18 | [log](user_data/profile_smoke_logs/CryptoFrogHO2.log) |
| `CryptoFrogHO2A` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:46:12 | [log](user_data/profile_smoke_logs/CryptoFrogHO2A.log) |
| `CryptoFrogHO3A1` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:47:07 | [log](user_data/profile_smoke_logs/CryptoFrogHO3A1.log) |
| `CryptoFrogHO3A2` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:48:01 | [log](user_data/profile_smoke_logs/CryptoFrogHO3A2.log) |
| `CryptoFrogHO3A3` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:48:55 | [log](user_data/profile_smoke_logs/CryptoFrogHO3A3.log) |
| `CryptoFrogHO3A4` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:49:56 | [log](user_data/profile_smoke_logs/CryptoFrogHO3A4.log) |
| `CryptoFrogNFI` | `spot_long` | `E1_expanded` | 370 | `convergence:2016:warmup_supplied` | 2026-09-03 20:53:08 | [archive](user_data/profile_smoke/CryptoFrogNFI-08ea05db-2026-09-03_20-53-08.zip) [log](user_data/convergence_logs/CryptoFrogNFI-ladder.log) |
| `CryptoFrogNFIHO1A` | `spot_long` | `E1_expanded` | 358 | `convergence:2016:warmup_supplied` | 2026-09-03 20:53:56 | [archive](user_data/profile_smoke/CryptoFrogNFIHO1A-366468cd-2026-09-03_20-53-56.zip) [log](user_data/convergence_logs/CryptoFrogNFIHO1A-ladder.log) |
| `CryptoFrogOffset` | `spot_long` | `E1_expanded` | 295 | `convergence:2016:warmup_supplied` | 2026-09-03 20:54:39 | [archive](user_data/profile_smoke/CryptoFrogOffset-058d44a6-2026-09-03_20-54-39.zip) [log](user_data/convergence_logs/CryptoFrogOffset-ladder.log) |
| `CryptoFrog_nateema` | `spot_long` | `E1_expanded` |  | `convergence:288:warmup_supplied` | 2026-09-02 18:52:49 | [log](user_data/profile_smoke_logs/CryptoFrog_nateema.log) |
| `CustomStoplossWithPSAR` | `spot_long` | `E1_expanded` | 140 | `convergence:24:warmup_supplied` | 2026-09-01 13:50:31 | [log](user_data/convergence_logs/CustomStoplossWithPSAR-ladder.log) |
| `DD` | `spot_long` | `E1_expanded` | 32051 | `convergence:288:warmup_supplied` | 2026-09-01 15:45:44 | [log](user_data/convergence_logs/DD-ladder.log) |
| `DWT_LongShort` | `futures_long_short` | `E1_expanded` | 859 | `convergence:288:warmup_supplied` | 2026-09-02 06:56:43 | [log](user_data/convergence_logs/DWT_LongShort-ladder.log) |
| `DWT_short` | `futures_long_short` | `E1_expanded` | 362 | `convergence:288:warmup_supplied` | 2026-09-02 06:57:53 | [log](user_data/convergence_logs/DWT_short-ladder.log) |
| `DemaCrossStrategy` | `spot_long` | `E1_expanded` | 21528 | `convergence:288:warmup_supplied` | 2026-09-01 12:24:04 | [log](user_data/convergence_logs/DemaCrossStrategy-ladder.log) |
| `Diamond` | `spot_long` | `E1_expanded` | 4603 | `convergence:288:warmup_supplied` | 2026-09-01 15:46:33 | [log](user_data/convergence_logs/Diamond-ladder.log) |
| `Divergences` | `spot_long` | `E1_expanded` | 9981 | `convergence:2160:warmup_supplied` | 2026-09-01 13:21:26 | [log](user_data/convergence_logs/Divergences-ladder.log) |
| `DonchianBreakoutStrategy` | `spot_long` | `E1_expanded` | 21512 | `convergence:288:warmup_supplied` | 2026-09-01 12:24:28 | [log](user_data/convergence_logs/DonchianBreakoutStrategy-ladder.log) |
| `DoubleEMACrossoverWithTrend` | `spot_long` | `E1_expanded` | 4019 | `convergence:2160:warmup_supplied` | 2026-09-03 19:41:49 | [log](user_data/convergence_logs/DoubleEMACrossoverWithTrend-2df7ee08-ladder.log) |
| `Dyna_opti` | `spot_long` | `E1_expanded` | 26 | `convergence:576:warmup_supplied` | 2026-09-04 06:12:17 | [archive](user_data/profile_smoke/Dyna_opti-8aa17cbf-2026-09-04_06-12-17.zip) [log](user_data/convergence_logs/Dyna_opti-ladder.log) |
| `E0V1E` | `spot_long` | `E1_expanded` | 329 | `convergence:2016:warmup_supplied` | 2026-09-01 13:22:16 | [log](user_data/convergence_logs/E0V1E-ladder.log) |
| `E0V1E2` | `spot_long` | `E1_expanded` | 330 | `convergence:2016:warmup_supplied` | 2026-09-01 13:22:41 | [log](user_data/convergence_logs/E0V1E2-ladder.log) |
| `E0V1EN` | `spot_long` | `E1_expanded` | 25 | `convergence:288:warmup_supplied` | 2026-09-06 15:09:16 | [archive](user_data/profile_smoke/E0V1EN-dc02ef88-2026-09-06_15-09-16.zip) [log](user_data/convergence_logs/E0V1EN-ladder.log) |
| `E0V1E_DCA3` | `spot_long` | `E1_expanded` | 2152 | `convergence:2016:warmup_supplied` | 2026-09-01 12:24:54 | [log](user_data/convergence_logs/E0V1E_DCA3-ladder.log) |
| `E0V1E_ewo` | `spot_long` | `E1_expanded` | 309 | `convergence:2016:warmup_supplied` | 2026-09-01 13:23:07 | [log](user_data/convergence_logs/E0V1E_ewo-ladder.log) |
| `E0V1E_protections` | `spot_long` | `E1_expanded` | 329 | `convergence:2016:warmup_supplied` | 2026-09-01 13:23:31 | [log](user_data/convergence_logs/E0V1E_protections-ladder.log) |
| `E0V1E_strs` | `spot_long` | `E1_expanded` | 134 | `convergence:288:warmup_supplied` | 2026-09-01 13:23:57 | [log](user_data/convergence_logs/E0V1E_strs-ladder.log) |
| `EI3v2_tag_cofi_green` | `spot_long` | `E1_expanded` | 116 | `convergence:2016:warmup_supplied` | 2026-09-06 14:47:16 | [archive](user_data/profile_smoke/EI3v2_tag_cofi_green-c37315b6-2026-09-06_14-47-16.zip) [log](user_data/convergence_logs/EI3v2_tag_cofi_green-ladder.log) |
| `EMA50` | `spot_long` | `E1_expanded` | 5751 | `convergence:288:warmup_supplied` | 2026-09-01 13:24:21 | [log](user_data/convergence_logs/EMA50-ladder.log) |
| `EMA520015_V17` | `spot_long` | `E1_expanded` | 8265 | `convergence:540:warmup_supplied` | 2026-09-01 15:47:21 | [log](user_data/convergence_logs/EMA520015_V17-ladder.log) |
| `EMABBRSI` | `spot_long` | `E1_expanded` | 104 | `convergence:2160:warmup_supplied` | 2026-09-01 19:36:47 | [archive](user_data/profile_smoke/EMABBRSI-2026-09-01_19-36-47.zip) [log](user_data/convergence_logs/EMABBRSI-ladder.log) |
| `EMABreakout` | `spot_long` | `E1_expanded` | 5734 | `convergence:288:warmup_supplied` | 2026-09-01 13:24:46 | [log](user_data/convergence_logs/EMABreakout-ladder.log) |
| `EMAPriceCrossoverWithThreshold` | `spot_long` | `E1_expanded` | 1816 | `convergence:2160:warmup_supplied` | 2026-09-03 19:42:59 | [log](user_data/convergence_logs/EMAPriceCrossoverWithThreshold-b7ab2a0f-ladder.log) |
| `EMASkipPump` | `spot_long` | `E1_expanded` | 34322 | `convergence:288:warmup_supplied` | 2026-09-01 13:53:49 | [log](user_data/convergence_logs/EMASkipPump-ladder.log) |
| `EMAVolume` | `spot_long` | `E1_expanded` | 183 | `convergence:1344:warmup_supplied` | 2026-09-01 19:37:25 | [archive](user_data/profile_smoke/EMAVolume-2026-09-01_19-37-25.zip) [log](user_data/convergence_logs/EMAVolume-ladder.log) |
| `EMA_CROSSOVER_STRATEGY` | `spot_long` | `E1_expanded` | 26980 | `convergence:4032:warmup_supplied` | 2026-09-03 13:52:59 | [log](user_data/convergence_logs/EMA_CROSSOVER_STRATEGY-ladder.log) |
| `EMA_Trailing_Stoploss` | `spot_long` | `E1_expanded` | 463 | `convergence:24:warmup_supplied` | 2026-09-05 15:04:54 | [archive](user_data/profile_smoke/EMA_Trailing_Stoploss-c357e7e7-2026-09-05_15-04-54.zip) [log](user_data/convergence_logs/EMA_Trailing_Stoploss-c357e7e7-ladder.log) |
| `EMA_Trailing_Stoploss_LessMagic` | `spot_long` | `E1_expanded` | 463 | `convergence:288:warmup_supplied` | 2026-09-05 15:06:00 | [archive](user_data/profile_smoke/EMA_Trailing_Stoploss_LessMagic-aa2b302f-2026-09-05_15-06-00.zip) [log](user_data/convergence_logs/EMA_Trailing_Stoploss_LessMagic-aa2b302f-ladder.log) |
| `EXPERIMENTAL_STRATEGY` | `spot_long` | `E1_expanded` | 582 | `convergence:288:warmup_supplied` | 2026-09-01 19:38:04 | [archive](user_data/profile_smoke/EXPERIMENTAL_STRATEGY-2026-09-01_19-38-04.zip) [log](user_data/convergence_logs/EXPERIMENTAL_STRATEGY-ladder.log) |
| `EasyInEasyOut` | `spot_long` | `E1_expanded` | 17 | `convergence:1440:warmup_supplied` | 2026-09-01 15:48:12 | [log](user_data/convergence_logs/EasyInEasyOut-ladder.log) |
| `ElliotV2` | `spot_long` | `E1_expanded` | 402 | `convergence:2016:warmup_supplied` | 2026-09-03 13:53:25 | [log](user_data/convergence_logs/ElliotV2-ladder.log) |
| `ElliotV4` | `spot_long` | `E1_expanded` | 915 | `convergence:2016:warmup_supplied` | 2026-09-01 13:25:34 | [log](user_data/convergence_logs/ElliotV4-ladder.log) |
| `ElliotV531` | `spot_long` | `E1_expanded` | 887 | `convergence:2016:warmup_supplied` | 2026-09-01 13:25:59 | [log](user_data/convergence_logs/ElliotV531-ladder.log) |
| `ElliotV5HO` | `spot_long` | `E1_expanded` | 810 | `convergence:2016:warmup_supplied` | 2026-09-01 13:26:23 | [log](user_data/convergence_logs/ElliotV5HO-ladder.log) |
| `ElliotV5HOMod2` | `spot_long` | `E1_expanded` | 494 | `convergence:2016:warmup_supplied` | 2026-09-01 13:26:48 | [log](user_data/convergence_logs/ElliotV5HOMod2-ladder.log) |
| `ElliotV5HOMod3` | `spot_long` | `E1_expanded` | 547 | `convergence:2016:warmup_supplied` | 2026-09-01 13:27:12 | [log](user_data/convergence_logs/ElliotV5HOMod3-ladder.log) |
| `ElliotV5_SMA` | `spot_long` | `E1_expanded` | 723 | `convergence:288` | 2026-09-03 13:53:52 | [log](user_data/convergence_logs/ElliotV5_SMA-ladder.log) |
| `ElliotV7` | `spot_long` | `E1_expanded` | 554 | `convergence:2016:warmup_supplied` | 2026-09-01 13:27:41 | [log](user_data/convergence_logs/ElliotV7-ladder.log) |
| `ElliotV8HO` | `spot_long` | `E1_expanded` | 386 | `convergence:2016:warmup_supplied` | 2026-09-01 13:28:05 | [log](user_data/convergence_logs/ElliotV8HO-ladder.log) |
| `ElliotV8_original` | `spot_long` | `E1_expanded` | 25 | `convergence:2016:warmup_supplied` | 2026-09-06 15:08:33 | [archive](user_data/profile_smoke/ElliotV8_original-ce2403f2-2026-09-06_15-08-33.zip) [log](user_data/convergence_logs/ElliotV8_original-ladder.log) |
| `ElliotV8_original_ichiv2` | `spot_long` | `E1_expanded` | 54 | `convergence:2016:warmup_supplied` | 2026-09-06 14:59:37 | [archive](user_data/profile_smoke/ElliotV8_original_ichiv2-3c67badc-2026-09-06_14-59-37.zip) [log](user_data/convergence_logs/ElliotV8_original_ichiv2-ladder.log) |
| `ElliotV8_original_ichiv2OH` | `spot_long` | `E1_expanded` | 56 | `convergence:2016:warmup_supplied` | 2026-09-06 14:59:43 | [archive](user_data/profile_smoke/ElliotV8_original_ichiv2OH-a45e937f-2026-09-06_14-59-43.zip) [log](user_data/convergence_logs/ElliotV8_original_ichiv2OH-ladder.log) |
| `ElliotV8_original_ichiv3` | `spot_long` | `E1_expanded` | 71 | `convergence:2016:warmup_supplied` | 2026-09-06 14:46:50 | [archive](user_data/profile_smoke/ElliotV8_original_ichiv3-433ffe91-2026-09-06_14-46-50.zip) [log](user_data/convergence_logs/ElliotV8_original_ichiv3-ladder.log) |
| `Elliotv8` | `spot_long` | `E1_expanded` | 25 | `convergence:2016:warmup_supplied` | 2026-09-06 14:46:44 | [archive](user_data/profile_smoke/Elliotv8-bdc3ea5b-2026-09-06_14-46-44.zip) [log](user_data/convergence_logs/Elliotv8-ladder.log) |
| `EmaRibbonStrategy` | `spot_long` | `E1_expanded` | 22752 | `convergence:288:warmup_supplied` | 2026-09-01 12:25:20 | [log](user_data/convergence_logs/EmaRibbonStrategy-ladder.log) |
| `FAdxSmaStrategy` | `futures_long_short` | `E1_expanded` | 15 | `convergence:336:warmup_supplied` | 2026-09-03 13:54:18 | [log](user_data/convergence_logs/FAdxSmaStrategy-ladder.log) |
| `FOttStrategy` | `futures_long_short` | `E1_expanded` | 6447 | `convergence:672:warmup_supplied` | 2026-09-01 13:28:30 | [log](user_data/convergence_logs/FOttStrategy-ladder.log) |
| `FRAYSTRAT` | `spot_long` | `E1_expanded` | 12446 | `convergence:672:warmup_supplied` | 2026-09-01 13:28:54 | [log](user_data/convergence_logs/FRAYSTRAT-ladder.log) |
| `FReinforcedStrategy` | `futures_long_short` | `E1_expanded` | 80 | `convergence:2016:warmup_supplied` | 2026-09-02 06:59:03 | [log](user_data/convergence_logs/FReinforcedStrategy-ladder.log) |
| `FSampleStrategy` | `futures_long_short` | `E1_expanded` | 40 | `convergence:336:warmup_supplied` | 2026-09-01 13:29:43 | [log](user_data/convergence_logs/FSampleStrategy-ladder.log) |
| `FSupertrendStrategy` | `futures_long` | `E1_expanded` | 83 | `convergence:168:warmup_supplied` | 2026-09-03 13:54:46 | [log](user_data/convergence_logs/FSupertrendStrategy-ladder.log) |
| `FTT_DWT_FBB_FUTURES` | `futures_long_short` | `E1_expanded` | 941 | `convergence:576:warmup_supplied` | 2026-09-02 07:00:21 | [log](user_data/convergence_logs/FTT_DWT_FBB_FUTURES-ladder.log) |
| `FVGChannel` | `spot_long` | `E1_expanded` | 16599 | `convergence:2160:warmup_supplied` | 2026-09-01 15:49:04 | [log](user_data/convergence_logs/FVGChannel-ladder.log) |
| `Fakebuy` | `spot_long` | `E1_expanded` | 339 | `convergence:288:warmup_supplied` | 2026-09-03 19:43:37 | [log](user_data/convergence_logs/Fakebuy-d1b272c1-ladder.log) |
| `FastSupertrend_optim3` | `futures_long_short` | `E1_expanded` | 403 | `convergence:168:warmup_supplied` | 2026-09-02 19:09:03 | [log](user_data/convergence_logs/FastSupertrend_optim3-ladder.log) |
| `FastSupertrend_optim3_rsi_70` | `futures_long_short` | `E1_expanded` | 297 | `convergence:168:warmup_supplied` | 2026-09-02 19:09:29 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_70-ladder.log) |
| `FastSupertrend_optim3_rsi_75` | `futures_long_short` | `E1_expanded` | 320 | `convergence:168:warmup_supplied` | 2026-09-02 19:09:55 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_75-ladder.log) |
| `FastSupertrend_optim3_rsi_752` | `futures_long_short` | `E1_expanded` | 383 | `convergence:168:warmup_supplied` | 2026-09-02 19:10:21 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_752-ladder.log) |
| `FastSupertrend_optim3_rsi_75fix` | `futures_long_short` | `E1_expanded` | 320 | `convergence:168:warmup_supplied` | 2026-09-02 19:10:46 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_75fix-ladder.log) |
| `FastSupertrend_optim3_rsi_75fix_signal` | `futures_long_short` | `E1_expanded` | 215 | `convergence:168:warmup_supplied` | 2026-09-02 19:11:12 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_75fix_signal-ladder.log) |
| `FastSupertrend_optim3_rsi_75lev` | `futures_long_short` | `E1_expanded` | 763 | `convergence:168:warmup_supplied` | 2026-09-02 19:11:38 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_75lev-ladder.log) |
| `FastSupertrend_optim3_rsi_75sell` | `futures_long_short` | `E1_expanded` | 319 | `convergence:168:warmup_supplied` | 2026-09-02 19:12:05 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_75sell-ladder.log) |
| `FastSupertrend_optim3_rsi_80` | `futures_long_short` | `E1_expanded` | 396 | `convergence:168:warmup_supplied` | 2026-09-02 19:12:31 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_80-ladder.log) |
| `FastSupertrend_optim_quick` | `futures_long_short` | `E1_expanded` | 557 | `convergence:168:warmup_supplied` | 2026-09-02 19:12:57 | [log](user_data/convergence_logs/FastSupertrend_optim_quick-ladder.log) |
| `FastSupertrend_optim_quick2` | `futures_long_short` | `E1_expanded` | 1587 | `convergence:168:warmup_supplied` | 2026-09-02 19:13:23 | [log](user_data/convergence_logs/FastSupertrend_optim_quick2-ladder.log) |
| `FastSupertrend_optim_quick3` | `futures_long_short` | `E1_expanded` | 1283 | `convergence:168:warmup_supplied` | 2026-09-02 19:13:49 | [log](user_data/convergence_logs/FastSupertrend_optim_quick3-ladder.log) |
| `FastSupertrend_optim_quick4` | `futures_long_short` | `E1_expanded` | 1245 | `convergence:168:warmup_supplied` | 2026-09-02 19:14:15 | [log](user_data/convergence_logs/FastSupertrend_optim_quick4-ladder.log) |
| `FastSupertrend_optim_quick5` | `futures_long_short` | `E1_expanded` | 1166 | `convergence:168:warmup_supplied` | 2026-09-02 19:14:43 | [log](user_data/convergence_logs/FastSupertrend_optim_quick5-ladder.log) |
| `FastSupertrend_ts_origstop_fix` | `futures_long_short` | `E1_expanded` | 53 | `convergence:168:warmup_supplied` | 2026-09-03 13:55:11 | [log](user_data/convergence_logs/FastSupertrend_ts_origstop_fix-ladder.log) |
| `FisherHull` | `spot_long` | `E1_expanded` | 34 | `convergence:1440:warmup_supplied` | 2026-09-01 13:54:39 | [log](user_data/convergence_logs/FisherHull-ladder.log) |
| `FisherTransformStrategy` | `spot_long` | `E1_expanded` | 22576 | `convergence:288:warmup_supplied` | 2026-09-01 12:25:45 | [log](user_data/convergence_logs/FisherTransformStrategy-ladder.log) |
| `FiveMinCrossAbove` | `spot_long` | `E1_expanded` | 1851 | `convergence:288:warmup_supplied` | 2026-09-01 13:55:28 | [log](user_data/convergence_logs/FiveMinCrossAbove-ladder.log) |
| `FlawlessVictory` | `spot_long` | `E1_expanded` | 12240 | `convergence:96` | 2026-09-03 13:55:37 | [log](user_data/convergence_logs/FlawlessVictory-ladder.log) |
| `ForexSignal` | `spot_long` | `E1_expanded` | 26316 | `convergence:288:warmup_supplied` | 2026-09-03 13:56:04 | [log](user_data/convergence_logs/ForexSignal-ladder.log) |
| `FrayStratBTC` | `spot_long` | `E1_expanded` | 9089 | `convergence:672:warmup_supplied` | 2026-09-01 13:55:52 | [log](user_data/convergence_logs/FrayStratBTC-ladder.log) |
| `Freqtrade_backtest_validation_freqtrade1` | `spot_long` | `E1_expanded` | 10164 | `convergence:48:warmup_supplied` | 2026-09-01 15:50:45 | [log](user_data/convergence_logs/Freqtrade_backtest_validation_freqtrade1-ladder.log) |
| `FrostAuraM115mStrategy` | `spot_long` | `E1_expanded` | 30851 | `convergence:192:warmup_supplied` | 2026-09-01 13:56:17 | [log](user_data/convergence_logs/FrostAuraM115mStrategy-ladder.log) |
| `FrostAuraM11hStrategy` | `spot_long` | `E1_expanded` | 2636 | `convergence:168:warmup_supplied` | 2026-09-01 13:56:41 | [log](user_data/convergence_logs/FrostAuraM11hStrategy-ladder.log) |
| `FrostAuraM21hStrategy` | `spot_long` | `E1_expanded` | 19880 | `convergence:192:warmup_supplied` | 2026-09-01 13:57:05 | [log](user_data/convergence_logs/FrostAuraM21hStrategy-ladder.log) |
| `FrostAuraM315mStrategy` | `spot_long` | `E1_expanded` | 9121 | `convergence:192:warmup_supplied` | 2026-09-01 13:57:30 | [log](user_data/convergence_logs/FrostAuraM315mStrategy-ladder.log) |
| `FrostAuraM31hStrategy` | `spot_long` | `E1_expanded` | 2469 | `convergence:168:warmup_supplied` | 2026-09-01 13:57:55 | [log](user_data/convergence_logs/FrostAuraM31hStrategy-ladder.log) |
| `GKD_Baseline` | `spot_long` | `E1_expanded` | 18338 | `convergence:168:warmup_supplied` | 2026-09-01 15:51:35 | [log](user_data/convergence_logs/GKD_Baseline-ladder.log) |
| `GKD_BaselineAllMAs` | `spot_long` | `E1_expanded` | 18338 | `convergence:168:warmup_supplied` | 2026-09-01 15:52:23 | [log](user_data/convergence_logs/GKD_BaselineAllMAs-ladder.log) |
| `GKD_FisherTransformMTF` | `spot_long` | `E1_expanded` | 4750 | `convergence:168:warmup_supplied` | 2026-09-01 14:01:15 | [log](user_data/convergence_logs/GKD_FisherTransformMTF-ladder.log) |
| `GKD_HurstExponent` | `spot_long` | `E1_expanded` | 5896 | `convergence:168:warmup_supplied` | 2026-09-01 15:53:13 | [log](user_data/convergence_logs/GKD_HurstExponent-ladder.log) |
| `GKD_PFE` | `spot_long` | `E1_expanded` | 17113 | `convergence:168:warmup_supplied` | 2026-09-01 15:54:03 | [log](user_data/convergence_logs/GKD_PFE-ladder.log) |
| `GPTREV` | `spot_long` | `E1_expanded` | 600 | `convergence:1440:warmup_supplied` | 2026-09-01 14:01:43 | [log](user_data/convergence_logs/GPTREV-ladder.log) |
| `GodCard` | `spot_long` | `E1_expanded` | 476 | `convergence:288:warmup_supplied` | 2026-09-01 15:54:53 | [log](user_data/convergence_logs/GodCard-ladder.log) |
| `GoldenCrossStrategy` | `spot_long` | `E1_expanded` | 5920 | `convergence:2016:warmup_supplied` | 2026-09-01 12:26:10 | [log](user_data/convergence_logs/GoldenCrossStrategy-ladder.log) |
| `Gumbo1` | `spot_long` | `E1_expanded` | 23582 | `convergence:288:warmup_supplied` | 2026-09-03 13:56:32 | [log](user_data/convergence_logs/Gumbo1-ladder.log) |
| `Hacklemore` | `spot_long` | `E1_expanded` | 135 | `convergence:288:warmup_supplied` | 2026-08-31 16:39:41 | [archive](user_data/profile_smoke/Hacklemore-2026-08-31_16-39-41.zip) [log](user_data/convergence_logs/Hacklemore-ladder.log) |
| `Hacklemore2` | `spot_long` | `E1_expanded` | 643 | `convergence:192:warmup_supplied` | 2026-09-01 14:06:05 | [log](user_data/convergence_logs/Hacklemore2-ladder.log) |
| `Hacklemore3` | `spot_long` | `E1_expanded` | 34 | `convergence:288:warmup_supplied` | 2026-09-01 14:06:53 | [log](user_data/convergence_logs/Hacklemore3-ladder.log) |
| `Hacklemost` | `spot_long` | `E1_expanded` | 168 | `convergence:288:warmup_supplied` | 2026-09-01 14:07:44 | [log](user_data/convergence_logs/Hacklemost-ladder.log) |
| `HansenSmaOffsetV1` | `spot_long` | `E1_expanded` | 119 | `convergence:96:warmup_supplied` | 2026-09-01 14:08:31 | [log](user_data/convergence_logs/HansenSmaOffsetV1-ladder.log) |
| `HeikinAshiStrategy` | `spot_long` | `E1_expanded` | 26155 | `convergence:288:warmup_supplied` | 2026-09-01 12:26:36 | [log](user_data/convergence_logs/HeikinAshiStrategy-ladder.log) |
| `HigherHighStrategy` | `spot_long` | `E1_expanded` | 26360 | `convergence:288:warmup_supplied` | 2026-09-01 12:27:00 | [log](user_data/convergence_logs/HigherHighStrategy-ladder.log) |
| `HilbertSineWave` | `spot_long` | `E1_expanded` | 4447 | `convergence:336:warmup_supplied` | 2026-09-01 15:56:37 | [log](user_data/convergence_logs/HilbertSineWave-ladder.log) |
| `HourBasedStrategy` | `spot_long` | `E1_expanded` | 10884 | `convergence:24:warmup_supplied` | 2026-09-01 14:09:19 | [log](user_data/convergence_logs/HourBasedStrategy-ladder.log) |
| `HourBasedStrategy_5m` | `spot_long` | `E1_expanded` | 11784 | `convergence:288:warmup_supplied` | 2026-09-01 23:55:49 | [log](user_data/convergence_logs/HourBasedStrategy_5m-ladder.log) |
| `INSIDEUP` | `spot_long` | `E1_expanded` | 554 | `convergence:90:warmup_supplied` | 2026-09-01 14:14:51 | [log](user_data/convergence_logs/INSIDEUP-ladder.log) |
| `Ichess` | `spot_long` | `E1_expanded` | 355 | `convergence:90:warmup_supplied` | 2026-09-01 14:15:39 | [log](user_data/convergence_logs/Ichess-ladder.log) |
| `Ichimoku` | `spot_long` | `E1_expanded` | 8609 | `convergence:288:warmup_supplied` | 2026-09-01 14:16:28 | [log](user_data/convergence_logs/Ichimoku-ladder.log) |
| `IchimokuCloudStrategy` | `spot_long` | `E1_expanded` | 796 | `convergence:6` | 2026-09-06 07:58:46 | [log](user_data/convergence_logs/IchimokuCloudStrategy-eede6bf0-ladder.log) |
| `IchimokuSimpleStrategy` | `spot_long` | `E1_expanded` | 19831 | `convergence:288:warmup_supplied` | 2026-09-01 12:27:25 | [log](user_data/convergence_logs/IchimokuSimpleStrategy-ladder.log) |
| `IchimokuStrategy` | `spot_long` | `E1_expanded` | 90 | `convergence:480:warmup_supplied` | 2026-09-03 21:08:41 | [archive](user_data/profile_smoke/IchimokuStrategy-67b217c6-2026-09-03_21-08-41.zip) [log](user_data/convergence_logs/IchimokuStrategy-67b217c6-ladder.log) |
| `Ichimoku_SenkouSpanCross` | `spot_long` | `E1_expanded` | 1 | `convergence:180:warmup_supplied` | 2026-09-03 21:09:11 | [archive](user_data/profile_smoke/Ichimoku_SenkouSpanCross-d71627c7-2026-09-03_21-09-11.zip) [log](user_data/convergence_logs/Ichimoku_SenkouSpanCross-d71627c7-ladder.log) |
| `Ichimoku_v12` | `spot_long` | `E1_expanded` | 7 | `convergence:180:warmup_supplied` | 2026-09-01 19:41:45 | [archive](user_data/profile_smoke/Ichimoku_v12-2026-09-01_19-41-45.zip) [log](user_data/convergence_logs/Ichimoku_v12-ladder.log) |
| `Ichimoku_v30` | `spot_long` | `E1_expanded` | 3 | `convergence:180:warmup_supplied` | 2026-09-01 19:42:22 | [archive](user_data/profile_smoke/Ichimoku_v30-2026-09-01_19-42-22.zip) [log](user_data/convergence_logs/Ichimoku_v30-ladder.log) |
| `Ichimoku_v31` | `spot_long` | `E1_expanded` | 1564 | `convergence:150` | 2026-09-03 13:57:01 | [log](user_data/convergence_logs/Ichimoku_v31-ladder.log) |
| `Ichimoku_v32` | `spot_long` | `E1_expanded` | 3 | `convergence:180:warmup_supplied` | 2026-09-01 19:43:00 | [archive](user_data/profile_smoke/Ichimoku_v32-2026-09-01_19-43-00.zip) [log](user_data/convergence_logs/Ichimoku_v32-ladder.log) |
| `Ichimoku_v33` | `spot_long` | `E1_expanded` | 3 | `convergence:180:warmup_supplied` | 2026-09-01 19:43:37 | [archive](user_data/profile_smoke/Ichimoku_v33-2026-09-01_19-43-37.zip) [log](user_data/convergence_logs/Ichimoku_v33-ladder.log) |
| `Ichimoku_v37` | `spot_long` | `E1_expanded` | 507 | `convergence:150` | 2026-09-03 13:57:27 | [log](user_data/convergence_logs/Ichimoku_v37-ladder.log) |
| `ImpulseV1` | `spot_long` | `E1_expanded` | 1097 | `convergence:288:warmup_supplied` | 2026-09-01 12:27:51 | [log](user_data/convergence_logs/ImpulseV1-ladder.log) |
| `InformativeSample` | `spot_long` | `E1_expanded` | 15553 | `convergence:576:warmup_supplied` | 2026-09-01 14:17:18 | [log](user_data/convergence_logs/InformativeSample-ladder.log) |
| `Inverse` | `spot_long` | `E1_expanded` | 2470 | `convergence:720:warmup_supplied` | 2026-09-01 12:28:16 | [log](user_data/convergence_logs/Inverse-ladder.log) |
| `InverseV2` | `spot_long` | `E1_expanded` | 989 | `convergence:720:warmup_supplied` | 2026-09-01 12:28:42 | [log](user_data/convergence_logs/InverseV2-ladder.log) |
| `JuicyTrend` | `spot_long` | `E1_expanded` | 24136 | `convergence:1344:warmup_supplied` | 2026-09-01 15:57:25 | [log](user_data/convergence_logs/JuicyTrend-ladder.log) |
| `JustROCR` | `spot_long` | `E1_expanded` | 21 | `convergence:24:warmup_supplied` | 2026-09-01 19:44:53 | [archive](user_data/profile_smoke/JustROCR-2026-09-01_19-44-53.zip) [log](user_data/convergence_logs/JustROCR-ladder.log) |
| `JustROCR2` | `spot_long` | `E1_expanded` | 35 | `convergence:288:warmup_supplied` | 2026-09-01 19:45:29 | [archive](user_data/profile_smoke/JustROCR2-2026-09-01_19-45-29.zip) [log](user_data/convergence_logs/JustROCR2-ladder.log) |
| `JustROCR3` | `spot_long` | `E1_expanded` | 94 | `convergence:288:warmup_supplied` | 2026-09-01 19:46:10 | [archive](user_data/profile_smoke/JustROCR3-2026-09-01_19-46-10.zip) [log](user_data/convergence_logs/JustROCR3-ladder.log) |
| `JustROCR4` | `spot_long` | `E1_expanded` | 9 | `convergence:288:warmup_supplied` | 2026-09-01 19:46:51 | [archive](user_data/profile_smoke/JustROCR4-2026-09-01_19-46-51.zip) [log](user_data/convergence_logs/JustROCR4-ladder.log) |
| `JustROCR5` | `spot_long` | `E1_expanded` | 43 | `convergence:1440:warmup_supplied` | 2026-09-01 19:47:36 | [archive](user_data/profile_smoke/JustROCR5-2026-09-01_19-47-36.zip) [log](user_data/convergence_logs/JustROCR5-ladder.log) |
| `JustROCR6` | `spot_long` | `E1_expanded` | 107 | `convergence:1440:warmup_supplied` | 2026-09-01 19:48:20 | [archive](user_data/profile_smoke/JustROCR6-2026-09-01_19-48-20.zip) [log](user_data/convergence_logs/JustROCR6-ladder.log) |
| `KAMACCIRSI` | `spot_long` | `E1_expanded` | 10269 | `convergence:576:warmup_supplied` | 2026-09-03 13:57:54 | [log](user_data/convergence_logs/KAMACCIRSI-ladder.log) |
| `KAMACCIRSI_new` | `spot_long` | `E1_expanded` | 189 | `convergence:288:warmup_supplied` | 2026-09-01 12:29:09 | [log](user_data/convergence_logs/KAMACCIRSI_new-ladder.log) |
| `KC_BB` | `spot_long` | `E1_expanded` | 695 | `convergence:288:warmup_supplied` | 2026-09-01 15:58:17 | [log](user_data/convergence_logs/KC_BB-ladder.log) |
| `KeltnerChannelStrategy` | `spot_long` | `E1_expanded` | 16720 | `convergence:288:warmup_supplied` | 2026-09-01 12:29:34 | [log](user_data/convergence_logs/KeltnerChannelStrategy-ladder.log) |
| `Lateralus` | `spot_long` | `E1_expanded` | 3077 | `convergence:288:warmup_supplied` | 2026-09-01 14:18:09 | [log](user_data/convergence_logs/Lateralus-ladder.log) |
| `LinearRegressionStrategy` | `spot_long` | `E1_expanded` | 24570 | `convergence:288:warmup_supplied` | 2026-09-01 12:29:59 | [log](user_data/convergence_logs/LinearRegressionStrategy-ladder.log) |
| `Low_BB` | `spot_long` | `E1_expanded` | 649 | `convergence:1440:warmup_supplied` | 2026-09-01 14:19:00 | [log](user_data/convergence_logs/Low_BB-ladder.log) |
| `LuxOSC` | `spot_long` | `E1_expanded` | 14577 | `convergence:576:warmup_supplied` | 2026-09-01 14:19:26 | [log](user_data/convergence_logs/LuxOSC-ladder.log) |
| `MAC` | `spot_long` | `E1_expanded` | 52 | `convergence:90:warmup_supplied` | 2026-09-01 14:19:51 | [log](user_data/convergence_logs/MAC-ladder.log) |
| `MACD9fall` | `spot_long` | `E1_expanded` | 9 | `convergence:720:warmup_supplied` | 2026-09-05 15:10:15 | [archive](user_data/profile_smoke/MACD9fall-3ef1c8d0-2026-09-05_15-10-15.zip) [log](user_data/convergence_logs/MACD9fall-3ef1c8d0-ladder.log) |
| `MACDCCI` | `spot_long` | `E1_expanded` | 16 | `convergence:336:warmup_supplied` | 2026-09-01 19:49:03 | [archive](user_data/profile_smoke/MACDCCI-2026-09-01_19-49-03.zip) [log](user_data/convergence_logs/MACDCCI-ladder.log) |
| `MACDCrossoverWithTrend` | `spot_long` | `E1_expanded` | 1420 | `convergence:720:warmup_supplied` | 2026-09-03 19:44:44 | [log](user_data/convergence_logs/MACDCrossoverWithTrend-b6e682ec-ladder.log) |
| `MACDRL` | `futures_long` | `E1_expanded` | 200 | `convergence:2016:warmup_supplied` | 2026-09-02 07:27:57 | [log](user_data/convergence_logs/MACDRL-ladder.log) |
| `MACDRS` | `futures_long_short` | `E1_expanded` | 613 | `convergence:2016:warmup_supplied` | 2026-09-02 07:30:14 | [log](user_data/convergence_logs/MACDRS-ladder.log) |
| `MACDRSI200` | `spot_long` | `E1_expanded` | 170 | `convergence:2016:warmup_supplied` | 2026-09-01 19:49:47 | [archive](user_data/profile_smoke/MACDRSI200-2026-09-01_19-49-47.zip) [log](user_data/convergence_logs/MACDRSI200-ladder.log) |
| `MACDStrategy` | `spot_long` | `E1_expanded` | 20565 | `convergence:288:warmup_supplied` | 2026-09-03 19:45:50 | [log](user_data/convergence_logs/MACDStrategy-79bd402e-ladder.log) |
| `MACDStrategyADA` | `spot_long` | `E1_expanded` | 7456 | `convergence:288:warmup_supplied` | 2026-09-01 15:59:06 | [log](user_data/convergence_logs/MACDStrategyADA-ladder.log) |
| `MACDStrategyAVAX` | `spot_long` | `E1_expanded` | 7456 | `convergence:288:warmup_supplied` | 2026-09-01 15:59:57 | [log](user_data/convergence_logs/MACDStrategyAVAX-ladder.log) |
| `MACDStrategyBTC` | `spot_long` | `E1_expanded` | 7456 | `convergence:288:warmup_supplied` | 2026-09-01 16:00:47 | [log](user_data/convergence_logs/MACDStrategyBTC-ladder.log) |
| `MACDStrategyENJ` | `spot_long` | `E1_expanded` | 7456 | `convergence:288:warmup_supplied` | 2026-09-01 16:01:36 | [log](user_data/convergence_logs/MACDStrategyENJ-ladder.log) |
| `MACDStrategyETC` | `spot_long` | `E1_expanded` | 7456 | `convergence:288:warmup_supplied` | 2026-09-01 16:02:24 | [log](user_data/convergence_logs/MACDStrategyETC-ladder.log) |
| `MACDStrategySOL` | `spot_long` | `E1_expanded` | 7456 | `convergence:288:warmup_supplied` | 2026-09-01 16:03:11 | [log](user_data/convergence_logs/MACDStrategySOL-ladder.log) |
| `MACDStrategyXRP` | `spot_long` | `E1_expanded` | 7456 | `convergence:288:warmup_supplied` | 2026-09-01 16:04:01 | [log](user_data/convergence_logs/MACDStrategyXRP-ladder.log) |
| `MACDStrategy_crossed` | `spot_long` | `E1_expanded` | 5065 | `convergence:288:warmup_supplied` | 2026-09-01 14:23:01 | [log](user_data/convergence_logs/MACDStrategy_crossed-ladder.log) |
| `MACDZeroCrossStrategy` | `spot_long` | `E1_expanded` | 339 | `convergence:90:warmup_supplied` | 2026-09-01 14:23:48 | [log](user_data/convergence_logs/MACDZeroCrossStrategy-ladder.log) |
| `MACD_EMA` | `spot_long` | `E1_expanded` | 25655 | `convergence:2016:warmup_supplied` | 2026-09-01 14:24:36 | [log](user_data/convergence_logs/MACD_EMA-ladder.log) |
| `MACD_TRIPLE_MA` | `spot_long` | `E1_expanded` | 14845 | `convergence:288:warmup_supplied` | 2026-09-03 13:58:21 | [log](user_data/convergence_logs/MACD_TRIPLE_MA-ladder.log) |
| `MACD_TRI_EMA` | `spot_long` | `E1_expanded` | 31828 | `convergence:288:warmup_supplied` | 2026-09-01 14:25:25 | [log](user_data/convergence_logs/MACD_TRI_EMA-ladder.log) |
| `MADisplaceV3` | `spot_long` | `E1_expanded` | 718 | `convergence:288:warmup_supplied` | 2026-09-03 13:58:47 | [log](user_data/convergence_logs/MADisplaceV3-ladder.log) |
| `MFI` | `spot_long` | `E1_expanded` | 20266 | `convergence:288:warmup_supplied` | 2026-09-01 14:26:13 | [log](user_data/convergence_logs/MFI-ladder.log) |
| `MabStra` | `spot_long` | `E1_expanded` | 4303 | `convergence:42:warmup_supplied` | 2026-09-03 19:46:55 | [log](user_data/convergence_logs/MabStra-43fd2626-ladder.log) |
| `MacdAdxStrategy` | `spot_long` | `E1_expanded` | 27220 | `convergence:288:warmup_supplied` | 2026-09-01 12:30:24 | [log](user_data/convergence_logs/MacdAdxStrategy-ladder.log) |
| `MacdZeroCrossStrategy` | `spot_long` | `E1_expanded` | 29909 | `convergence:288:warmup_supplied` | 2026-09-03 19:47:29 | [log](user_data/convergence_logs/MacdZeroCrossStrategy-4830233c-ladder.log) |
| `MacheteV8b` | `spot_long` | `E1_expanded` | 77 | `convergence:500` | 2026-09-03 20:52:20 | [archive](user_data/profile_smoke/MacheteV8b-b42642cf-2026-09-03_20-52-20.zip) [log](user_data/convergence_logs/MacheteV8b-ladder.log) |
| `MacheteV8bRallimod` | `spot_long` | `E1_expanded` | 63 | `convergence:1344:warmup_supplied` | 2026-09-03 20:55:26 | [archive](user_data/profile_smoke/MacheteV8bRallimod-019087a6-2026-09-03_20-55-26.zip) [log](user_data/convergence_logs/MacheteV8bRallimod-ladder.log) |
| `MacheteV8bRallimod2` | `spot_long` | `E1_expanded` | 11 | `convergence:2016:warmup_supplied` | 2026-09-03 20:56:01 | [archive](user_data/profile_smoke/MacheteV8bRallimod2-2a221533-2026-09-03_20-56-01.zip) [log](user_data/convergence_logs/MacheteV8bRallimod2-ladder.log) |
| `Magic_Trailing_Stoploss` | `spot_long` | `E1_expanded` | 5473 | `convergence:24:warmup_supplied` | 2026-09-05 15:06:57 | [archive](user_data/profile_smoke/Magic_Trailing_Stoploss-1cf71129-2026-09-05_15-06-57.zip) [log](user_data/convergence_logs/Magic_Trailing_Stoploss-1cf71129-ladder.log) |
| `MarketChyperHyperStrategy` | `spot_long` | `E1_expanded` | 2406 | `convergence:336` | 2026-09-03 13:59:41 | [log](user_data/convergence_logs/MarketChyperHyperStrategy-ladder.log) |
| `Maro4hMacdSd` | `spot_long` | `E1_expanded` | 30492 | `convergence:288:warmup_supplied` | 2026-09-01 16:06:29 | [log](user_data/convergence_logs/Maro4hMacdSd-ladder.log) |
| `Martin` | `spot_long` | `E1_expanded` | 12724 | `convergence:288:warmup_supplied` | 2026-09-01 14:26:38 | [log](user_data/convergence_logs/Martin-ladder.log) |
| `MiniLambo` | `spot_long` | `E1_expanded` | 1469 | `convergence:2880:warmup_supplied` | 2026-09-01 14:27:06 | [log](user_data/convergence_logs/MiniLambo-ladder.log) |
| `Minmax` | `spot_long` | `E1_expanded` | 3882 | `convergence:24:warmup_supplied` | 2026-09-01 14:27:56 | [log](user_data/convergence_logs/Minmax-ladder.log) |
| `MomStrategy` | `spot_long` | `E1_expanded` | 21607 | `convergence:336:warmup_supplied` | 2026-09-01 16:07:18 | [log](user_data/convergence_logs/MomStrategy-ladder.log) |
| `MomentumScoreStrategy` | `spot_long` | `E1_expanded` | 27460 | `convergence:288:warmup_supplied` | 2026-09-01 12:31:13 | [log](user_data/convergence_logs/MomentumScoreStrategy-ladder.log) |
| `Momentumv2` | `spot_long` | `E1_expanded` | 2263 | `convergence:540:warmup_supplied` | 2026-09-01 12:31:37 | [log](user_data/convergence_logs/Momentumv2-ladder.log) |
| `MoneyFlowStrategy` | `spot_long` | `E1_expanded` | 19490 | `convergence:576:warmup_supplied` | 2026-09-01 12:32:02 | [log](user_data/convergence_logs/MoneyFlowStrategy-ladder.log) |
| `MontrealStrategy` | `spot_long` | `E1_expanded` | 26411 | `convergence:192:warmup_supplied` | 2026-09-01 14:28:21 | [log](user_data/convergence_logs/MontrealStrategy-ladder.log) |
| `MultiFactorConfluenceStrategy` | `spot_long` | `E1_expanded` | 5224 | `convergence:540:warmup_supplied` | 2026-09-01 12:32:26 | [log](user_data/convergence_logs/MultiFactorConfluenceStrategy-ladder.log) |
| `MultiMA_TSL` | `spot_long` | `E1_expanded` | 6 | `convergence:2016:warmup_supplied` | 2026-09-04 04:48:31 | [archive](user_data/profile_smoke/MultiMA_TSL-432f3842-2026-09-04_04-48-31.zip) [log](user_data/convergence_logs/MultiMA_TSL-ladder.log) |
| `MultiMA_TSL3` | `spot_long` | `E1_expanded` | 15 | `convergence:2016:warmup_supplied` | 2026-08-31 15:13:04 | [archive](user_data/profile_smoke/MultiMA_TSL3-2026-08-31_15-13-04.zip) [log](user_data/convergence_logs/MultiMA_TSL3-ladder.log) |
| `MultiMA_TSL3_Mod` | `spot_long` | `E1_expanded` | 13 | `convergence:2016:warmup_supplied` | 2026-08-31 16:03:58 | [archive](user_data/profile_smoke/MultiMA_TSL3_Mod-2026-08-31_16-03-58.zip) [log](user_data/convergence_logs/MultiMA_TSL3_Mod-ladder.log) |
| `MultiOffsetLamboV0` | `spot_long` | `E1_expanded` | 200 | `convergence:2016:warmup_supplied` | 2026-09-01 14:28:46 | [log](user_data/convergence_logs/MultiOffsetLamboV0-ladder.log) |
| `MultiRSI` | `spot_long` | `E1_expanded` | 442 | `convergence:2016:warmup_supplied` | 2026-08-31 15:13:48 | [archive](user_data/profile_smoke/MultiRSI-2026-08-31_15-13-48.zip) [log](user_data/convergence_logs/MultiRSI-ladder.log) |
| `MyStratV1` | `spot_long` | `E1_expanded` | 684 | `convergence:2016:warmup_supplied` | 2026-09-01 12:32:52 | [log](user_data/convergence_logs/MyStratV1-ladder.log) |
| `NASOSRv6_private_Reinuvader_20211121` | `spot_long` | `E1_expanded` | 452 | `convergence:2016:warmup_supplied` | 2026-08-31 15:35:19 | [archive](user_data/profile_smoke/NASOSRv6_private_Reinuvader_20211121-2026-08-31_15-35-19.zip) [log](user_data/convergence_logs/NASOSRv6_private_Reinuvader_20211121-ladder.log) |
| `NASOSv4` | `spot_long` | `E1_expanded` | 79 | `convergence:2016:warmup_supplied` | 2026-09-06 14:46:56 | [archive](user_data/profile_smoke/NASOSv4-d420d31d-2026-09-06_14-46-56.zip) [log](user_data/convergence_logs/NASOSv4-ladder.log) |
| `NASOSv5` | `spot_long` | `E1_expanded` | 801 | `convergence:2016:warmup_supplied` | 2026-09-01 14:29:12 | [log](user_data/convergence_logs/NASOSv5-ladder.log) |
| `NASOSv5_mod1` | `spot_long` | `E1_expanded` | 71 | `convergence:2016:warmup_supplied` | 2026-09-06 14:52:16 | [archive](user_data/profile_smoke/NASOSv5_mod1-dc29bda0-2026-09-06_14-52-16.zip) [log](user_data/convergence_logs/NASOSv5_mod1-ladder.log) |
| `NASOSv5_mod1_DanMod` | `spot_long` | `E1_expanded` | 65 | `convergence:2016:warmup_supplied` | 2026-09-06 15:08:41 | [archive](user_data/profile_smoke/NASOSv5_mod1_DanMod-8ccd7243-2026-09-06_15-08-41.zip) [log](user_data/convergence_logs/NASOSv5_mod1_DanMod-ladder.log) |
| `NASOSv5_mod2` | `spot_long` | `E1_expanded` | 62 | `convergence:2016:warmup_supplied` | 2026-09-06 14:52:23 | [archive](user_data/profile_smoke/NASOSv5_mod2-215c0845-2026-09-06_14-52-23.zip) [log](user_data/convergence_logs/NASOSv5_mod2-ladder.log) |
| `NASOSv5_mod3` | `spot_long` | `E1_expanded` | 74 | `convergence:2016:warmup_supplied` | 2026-09-06 14:52:30 | [archive](user_data/profile_smoke/NASOSv5_mod3-2ce3e304-2026-09-06_14-52-30.zip) [log](user_data/convergence_logs/NASOSv5_mod3-ladder.log) |
| `NEWTEST15m` | `spot_long` | `E1_expanded` | 2644 | `convergence:672:warmup_supplied` | 2026-09-01 14:29:37 | [log](user_data/convergence_logs/NEWTEST15m-ladder.log) |
| `NFI46` | `spot_long` | `E1_expanded` | 77 | `convergence:2016:warmup_supplied` | 2026-09-01 14:30:04 | [log](user_data/convergence_logs/NFI46-ladder.log) |
| `NFI46Frog` | `spot_long` | `E1_expanded` | 180 | `convergence:2016:warmup_supplied` | 2026-09-03 20:56:46 | [archive](user_data/profile_smoke/NFI46Frog-c5debb17-2026-09-03_20-56-46.zip) [log](user_data/convergence_logs/NFI46Frog-ladder.log) |
| `NFI46FrogZ` | `spot_long` | `E1_expanded` | 16273 | `convergence:2016:warmup_supplied` | 2026-09-01 14:30:31 | [log](user_data/convergence_logs/NFI46FrogZ-ladder.log) |
| `NFI46Offset` | `spot_long` | `E1_expanded` | 941 | `convergence:2016:warmup_supplied` | 2026-09-01 14:30:57 | [log](user_data/convergence_logs/NFI46Offset-ladder.log) |
| `NFI46OffsetHOA1` | `spot_long` | `E1_expanded` | 1037 | `convergence:2016:warmup_supplied` | 2026-09-01 14:31:24 | [log](user_data/convergence_logs/NFI46OffsetHOA1-ladder.log) |
| `NFI46Z` | `spot_long` | `E1_expanded` | 699 | `convergence:2016:warmup_supplied` | 2026-09-01 14:31:53 | [log](user_data/convergence_logs/NFI46Z-ladder.log) |
| `NFI47V2` | `spot_long` | `E1_expanded` | 524 | `convergence:2016:warmup_supplied` | 2026-09-01 12:33:20 | [log](user_data/convergence_logs/NFI47V2-ladder.log) |
| `NFI4Frog` | `spot_long` | `E1_expanded` | 188 | `convergence:2016:warmup_supplied` | 2026-09-03 20:57:25 | [archive](user_data/profile_smoke/NFI4Frog-a1f40e4d-2026-09-03_20-57-25.zip) [log](user_data/convergence_logs/NFI4Frog-ladder.log) |
| `NFI5MOHO` | `spot_long` | `E1_expanded` | 378 | `convergence:2016:warmup_supplied` | 2026-09-01 14:32:21 | [log](user_data/convergence_logs/NFI5MOHO-ladder.log) |
| `NFI5MOHO2` | `spot_long` | `E1_expanded` | 1436 | `convergence:2016:warmup_supplied` | 2026-09-01 12:33:48 | [log](user_data/convergence_logs/NFI5MOHO2-ladder.log) |
| `NFI5MOHO_WIP` | `spot_long` | `E1_expanded` | 951 | `convergence:2016:warmup_supplied` | 2026-09-01 14:32:49 | [log](user_data/convergence_logs/NFI5MOHO_WIP-ladder.log) |
| `NFI5MOHO_WIP_1` | `spot_long` | `E1_expanded` | 976 | `convergence:2016:warmup_supplied` | 2026-09-01 12:34:16 | [log](user_data/convergence_logs/NFI5MOHO_WIP_1-ladder.log) |
| `NFI5MOHO_WIP_2` | `spot_long` | `E1_expanded` | 988 | `convergence:2016:warmup_supplied` | 2026-09-01 12:34:44 | [log](user_data/convergence_logs/NFI5MOHO_WIP_2-ladder.log) |
| `NFI731_BUSD` | `spot_long` | `E1_expanded` | 19 | `convergence:2016:warmup_supplied` | 2026-08-31 15:14:23 | [archive](user_data/profile_smoke/NFI731_BUSD-2026-08-31_15-14-23.zip) [log](user_data/convergence_logs/NFI731_BUSD-ladder.log) |
| `NFI7MOHO` | `spot_long` | `E1_expanded` | 1966 | `convergence:2016:warmup_supplied` | 2026-09-01 12:35:13 | [log](user_data/convergence_logs/NFI7MOHO-ladder.log) |
| `NFINextMOHO` | `spot_long` | `E1_expanded` | 1442 | `convergence:2016:warmup_supplied` | 2026-09-01 12:35:41 | [log](user_data/convergence_logs/NFINextMOHO-ladder.log) |
| `NFINextMOHO2` | `spot_long` | `E1_expanded` | 1784 | `convergence:2016:warmup_supplied` | 2026-09-01 12:36:07 | [log](user_data/convergence_logs/NFINextMOHO2-ladder.log) |
| `NFINextMultiOffsetAndHO` | `spot_long` | `E1_expanded` | 1094 | `convergence:2016:warmup_supplied` | 2026-09-01 12:36:33 | [log](user_data/convergence_logs/NFINextMultiOffsetAndHO-ladder.log) |
| `NFINextMultiOffsetAndHO2` | `spot_long` | `E1_expanded` | 705 | `convergence:2016:warmup_supplied` | 2026-09-01 12:37:00 | [log](user_data/convergence_logs/NFINextMultiOffsetAndHO2-ladder.log) |
| `NFIX_BB_RPB` | `spot_long` | `E1_expanded` | 34 | `convergence:2016:warmup_supplied` | 2026-08-31 15:14:55 | [archive](user_data/profile_smoke/NFIX_BB_RPB-2026-08-31_15-14-55.zip) [log](user_data/convergence_logs/NFIX_BB_RPB-ladder.log) |
| `NFIX_BB_RPB_c7c477d_20211030` | `spot_long` | `E1_expanded` | 16 | `convergence:2016:warmup_supplied` | 2026-08-31 16:04:36 | [archive](user_data/profile_smoke/NFIX_BB_RPB_c7c477d_20211030-2026-08-31_16-04-36.zip) [log](user_data/convergence_logs/NFIX_BB_RPB_c7c477d_20211030-ladder.log) |
| `NWEv6_new` | `spot_long` | `E1_expanded` | 8108 | `convergence:480:warmup_supplied` | 2026-09-03 14:00:13 | [log](user_data/convergence_logs/NWEv6_new-ladder.log) |
| `NfiNextModded` | `spot_long` | `E1_expanded` | 106 | `convergence:2016:warmup_supplied` | 2026-08-31 15:15:48 | [archive](user_data/profile_smoke/NfiNextModded-2026-08-31_15-15-48.zip) [log](user_data/convergence_logs/NfiNextModded-94125b64-ladder.log) |
| `NormalizerStrategy` | `spot_long` | `E1_expanded` | 3747 | `convergence:610` | 2026-09-01 12:37:23 | [log](user_data/convergence_logs/NormalizerStrategy-ladder.log) |
| `NormalizerStrategyHO2` | `spot_long` | `E1_expanded` | 3149 | `convergence:610` | 2026-09-01 14:34:54 | [log](user_data/convergence_logs/NormalizerStrategyHO2-ladder.log) |
| `Nostalgia` | `spot_long` | `E1_expanded` | 834 | `convergence:2016:warmup_supplied` | 2026-09-01 12:37:49 | [log](user_data/convergence_logs/Nostalgia-ladder.log) |
| `NostalgiaForInfinity772martinsk3` | `spot_long` | `E1_expanded` | 21 | `convergence:2016:warmup_supplied` | 2026-08-31 15:54:00 | [archive](user_data/profile_smoke/NostalgiaForInfinity772martinsk3-2026-08-31_15-54-00.zip) [log](user_data/convergence_logs/NostalgiaForInfinity772martinsk3-ladder.log) |
| `NostalgiaForInfinityNext` | `spot_long` | `E1_expanded` | 24 | `convergence:2016:warmup_supplied` | 2026-08-31 14:47:57 | [archive](user_data/profile_smoke/NostalgiaForInfinityNext-2026-08-31_14-47-57.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNext-b808c258-ladder.log) |
| `NostalgiaForInfinityNext772` | `spot_long` | `E1_expanded` | 38 | `convergence:2016:warmup_supplied` | 2026-08-31 15:35:53 | [archive](user_data/profile_smoke/NostalgiaForInfinityNext772-2026-08-31_15-35-53.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNext772-8d6ca7f0-ladder.log) |
| `NostalgiaForInfinityNextGen` | `spot_long` | `E1_expanded` | 158 | `convergence:2880:warmup_supplied` | 2026-09-01 14:35:20 | [log](user_data/convergence_logs/NostalgiaForInfinityNextGen-ladder.log) |
| `NostalgiaForInfinityNextGen_TSL` | `spot_long` | `E1_expanded` | 138 | `convergence:2880:warmup_supplied` | 2026-09-01 14:35:46 | [log](user_data/convergence_logs/NostalgiaForInfinityNextGen_TSL-ladder.log) |
| `NostalgiaForInfinityNextV7155` | `spot_long` | `E1_expanded` | 9 | `convergence:2016:warmup_supplied` | 2026-08-31 15:32:47 | [archive](user_data/profile_smoke/NostalgiaForInfinityNextV7155-2026-08-31_15-32-47.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNextV7155-fd1e8353-ladder.log) |
| `NostalgiaForInfinityNext_maximizer` | `spot_long` | `E1_expanded` | 25 | `convergence:2016:warmup_supplied` | 2026-08-31 16:05:16 | [archive](user_data/profile_smoke/NostalgiaForInfinityNext_maximizer-2026-08-31_16-05-16.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNext_maximizer-78e1c6b3-ladder.log) |
| `NostalgiaForInfinityV1` | `spot_long` | `E1_expanded` | 3457 | `convergence:2016:warmup_supplied` | 2026-09-03 14:00:40 | [log](user_data/convergence_logs/NostalgiaForInfinityV1-ladder.log) |
| `NostalgiaForInfinityV2` | `spot_long` | `E1_expanded` | 825 | `convergence:2016:warmup_supplied` | 2026-09-03 14:01:08 | [log](user_data/convergence_logs/NostalgiaForInfinityV2-ladder.log) |
| `NostalgiaForInfinityV3` | `spot_long` | `E1_expanded` | 1015 | `convergence:2016:warmup_supplied` | 2026-09-01 14:36:11 | [log](user_data/convergence_logs/NostalgiaForInfinityV3-ladder.log) |
| `NostalgiaForInfinityV4` | `spot_long` | `E1_expanded` | 401 | `convergence:2016:warmup_supplied` | 2026-09-01 14:36:37 | [log](user_data/convergence_logs/NostalgiaForInfinityV4-ladder.log) |
| `NostalgiaForInfinityV4HO` | `spot_long` | `E1_expanded` | 379 | `convergence:2016:warmup_supplied` | 2026-09-01 14:37:03 | [log](user_data/convergence_logs/NostalgiaForInfinityV4HO-ladder.log) |
| `NostalgiaForInfinityV5` | `spot_long` | `E1_expanded` | 618 | `convergence:2016:warmup_supplied` | 2026-09-01 14:37:31 | [log](user_data/convergence_logs/NostalgiaForInfinityV5-ladder.log) |
| `NostalgiaForInfinityV5MultiOffsetAndHO` | `spot_long` | `E1_expanded` | 1766 | `convergence:2016:warmup_supplied` | 2026-09-01 12:38:14 | [log](user_data/convergence_logs/NostalgiaForInfinityV5MultiOffsetAndHO-ladder.log) |
| `NostalgiaForInfinityV5MultiOffsetAndHO2` | `spot_long` | `E1_expanded` | 1381 | `convergence:2016:warmup_supplied` | 2026-09-01 14:37:59 | [log](user_data/convergence_logs/NostalgiaForInfinityV5MultiOffsetAndHO2-ladder.log) |
| `NostalgiaForInfinityV6` | `spot_long` | `E1_expanded` | 712 | `convergence:2016:warmup_supplied` | 2026-09-01 14:38:27 | [log](user_data/convergence_logs/NostalgiaForInfinityV6-ladder.log) |
| `NostalgiaForInfinityV6HO` | `spot_long` | `E1_expanded` | 712 | `convergence:2016:warmup_supplied` | 2026-09-01 12:38:41 | [log](user_data/convergence_logs/NostalgiaForInfinityV6HO-ladder.log) |
| `NostalgiaForInfinityV7` | `spot_long` | `E1_expanded` | 684 | `convergence:2016:warmup_supplied` | 2026-09-01 14:38:55 | [log](user_data/convergence_logs/NostalgiaForInfinityV7-ladder.log) |
| `NostalgiaForInfinityV7_7_2` | `spot_long` | `E1_expanded` | 40 | `convergence:2016:warmup_supplied` | 2026-08-31 16:05:55 | [archive](user_data/profile_smoke/NostalgiaForInfinityV7_7_2-2026-08-31_16-05-55.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV7_7_2-19436abd-ladder.log) |
| `NostalgiaForInfinityV7_SMA` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 14:39:23 | [log](user_data/convergence_logs/NostalgiaForInfinityV7_SMA-ladder.log) |
| `NostalgiaForInfinityV7_SMAv2` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 14:39:50 | [log](user_data/convergence_logs/NostalgiaForInfinityV7_SMAv2-ladder.log) |
| `NostalgiaForInfinityV7_SMAv2_1` | `spot_long` | `E1_expanded` | 545 | `convergence:2016:warmup_supplied` | 2026-09-01 14:40:17 | [log](user_data/convergence_logs/NostalgiaForInfinityV7_SMAv2_1-ladder.log) |
| `NostalgiaForInfinityX` | `spot_long` | `E1_expanded` | 28 | `convergence:2016:warmup_supplied` | 2026-08-31 14:50:00 | [archive](user_data/profile_smoke/NostalgiaForInfinityX-2026-08-31_14-50-00.zip) [log](user_data/convergence_logs/NostalgiaForInfinityX-ladder.log) |
| `NotAnotherSMAOffsetStrategy` | `spot_long` | `E1_expanded` | 898 | `convergence:2016:warmup_supplied` | 2026-09-01 14:44:33 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategy-ladder.log) |
| `NotAnotherSMAOffsetStrategyHO` | `spot_long` | `E1_expanded` | 905 | `convergence:2016:warmup_supplied` | 2026-09-01 14:44:59 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyHO-ladder.log) |
| `NotAnotherSMAOffsetStrategyHOv3` | `spot_long` | `E1_expanded` | 752 | `convergence:2016:warmup_supplied` | 2026-09-01 14:45:25 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyHOv3-ladder.log) |
| `NotAnotherSMAOffsetStrategyLite` | `spot_long` | `E1_expanded` | 1415 | `convergence:2016:warmup_supplied` | 2026-09-01 12:39:05 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyLite-ladder.log) |
| `NotAnotherSMAOffsetStrategyModHO` | `spot_long` | `E1_expanded` | 1144 | `convergence:2016:warmup_supplied` | 2026-09-01 14:45:51 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyModHO-ladder.log) |
| `NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901` | `spot_long` | `E1_expanded` | 1143 | `convergence:2016:warmup_supplied` | 2026-09-01 14:46:17 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901-ladder.log) |
| `NotAnotherSMAOffsetStrategyX1` | `spot_long` | `E1_expanded` | 597 | `convergence:2016:warmup_supplied` | 2026-09-01 14:46:44 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyX1-ladder.log) |
| `NotAnotherSMAOffsetStrategy_uzi` | `spot_long` | `E1_expanded` | 651 | `convergence:2016:warmup_supplied` | 2026-09-01 14:47:10 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategy_uzi-ladder.log) |
| `NowoIchimoku1hV2` | `spot_long` | `E1_expanded` | 3695 | `convergence:168:warmup_supplied` | 2026-09-01 14:48:01 | [log](user_data/convergence_logs/NowoIchimoku1hV2-ladder.log) |
| `NowoIchimoku5mV2` | `spot_long` | `E1_expanded` | 49 | `native` | 2026-08-31 15:19:45 | [archive](user_data/profile_smoke/NowoIchimoku5mV2-2026-08-31_15-19-45.zip) |
| `ONUR` | `spot_long` | `E1_expanded` | 534 | `convergence:192:warmup_supplied` | 2026-09-01 16:08:06 | [log](user_data/convergence_logs/ONUR-ladder.log) |
| `ObeliskIM_v1_1` | `spot_long` | `E1_expanded` | 64 | `native` | 2026-08-31 15:20:09 | [archive](user_data/profile_smoke/ObeliskIM_v1_1-2026-08-31_15-20-09.zip) |
| `ObeliskRSI_v6_1` | `spot_long` | `E1_expanded` | 269 | `convergence:2016:warmup_supplied` | 2026-08-31 15:20:32 | [archive](user_data/profile_smoke/ObeliskRSI_v6_1-2026-08-31_15-20-32.zip) [log](user_data/convergence_logs/ObeliskRSI_v6_1-ladder.log) |
| `Obelisk_Ichimoku_Slow_v1` | `spot_long` | `E1_expanded` | 30 | `convergence:180` | 2026-09-05 15:15:09 | [archive](user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1-933691c1-2026-09-05_15-15-09.zip) [log](user_data/convergence_logs/Obelisk_Ichimoku_Slow_v1-933691c1-ladder.log) |
| `Obelisk_Ichimoku_Slow_v1_1` | `spot_long` | `E1_expanded` | 30 | `convergence:180` | 2026-09-05 15:16:19 | [archive](user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1_1-877a1601-2026-09-05_15-16-19.zip) [log](user_data/convergence_logs/Obelisk_Ichimoku_Slow_v1_1-877a1601-ladder.log) |
| `Obelisk_Ichimoku_Slow_v1_2` | `spot_long` | `E1_expanded` | 29 | `convergence:180` | 2026-09-05 15:17:11 | [archive](user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1_2-fe861e17-2026-09-05_15-17-11.zip) [log](user_data/convergence_logs/Obelisk_Ichimoku_Slow_v1_2-fe861e17-ladder.log) |
| `Obelisk_Ichimoku_Slow_v1_3` | `spot_long` | `E1_expanded` | 57 | `convergence:2160:warmup_supplied` | 2026-08-31 15:21:17 | [archive](user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1_3-2026-08-31_15-21-17.zip) [log](user_data/convergence_logs/Obelisk_Ichimoku_Slow_v1_3-0482a784-ladder.log) |
| `Obelisk_Ichimoku_ZEMA_v1` | `spot_long` | `E1_expanded` | 38 | `convergence:288` | 2026-08-31 14:48:19 | [archive](user_data/profile_smoke/Obelisk_Ichimoku_ZEMA_v1-2026-08-31_14-48-19.zip) [log](user_data/convergence_logs/Obelisk_Ichimoku_ZEMA_v1-7b2ec464-ladder.log) |
| `Obelisk_TradePro_Ichi_v1_1` | `spot_long` | `E1_expanded` | 5059 | `convergence:24` | 2026-09-06 08:01:16 | [log](user_data/convergence_logs/Obelisk_TradePro_Ichi_v1_1-d9ad6391-ladder.log) |
| `Obelisk_TradePro_Ichi_v2` | `spot_long` | `E1_expanded` | 35 | `convergence:180` | 2026-09-05 15:18:10 | [archive](user_data/profile_smoke/Obelisk_TradePro_Ichi_v2-c9b4a814-2026-09-05_15-18-10.zip) [log](user_data/convergence_logs/Obelisk_TradePro_Ichi_v2-c9b4a814-ladder.log) |
| `Obelisk_TradePro_Ichi_v2_1` | `spot_long` | `E1_expanded` | 6419 | `convergence:180` | 2026-09-06 08:11:23 | [log](user_data/convergence_logs/Obelisk_TradePro_Ichi_v2_1-b409b943-ladder.log) |
| `Obelisk_TradePro_Ichi_v2_2` | `spot_long` | `E1_expanded` | 103 | `convergence:180` | 2026-09-05 15:04:05 | [archive](user_data/profile_smoke/Obelisk_TradePro_Ichi_v2_2-596055ad-2026-09-05_15-04-05.zip) [log](user_data/convergence_logs/Obelisk_TradePro_Ichi_v2_2-596055ad-ladder.log) |
| `OmaGann` | `spot_long` | `E1_expanded` | 11035 | `convergence:168:warmup_supplied` | 2026-09-01 16:08:55 | [log](user_data/convergence_logs/OmaGann-ladder.log) |
| `OversoldReversion` | `spot_long` | `E1_expanded` | 25 | `convergence:1250` | 2026-09-05 15:08:45 | [archive](user_data/profile_smoke/OversoldReversion-dcb09e33-2026-09-05_15-08-45.zip) [log](user_data/convergence_logs/OversoldReversion-dcb09e33-ladder.log) |
| `PRICEFOLLOWING` | `spot_long` | `E1_expanded` | 272 | `convergence:288:warmup_supplied` | 2026-09-01 14:48:31 | [log](user_data/convergence_logs/PRICEFOLLOWING-ladder.log) |
| `PRICEFOLLOWINGX` | `spot_long` | `E1_expanded` | 1172 | `convergence:672:warmup_supplied` | 2026-09-01 14:49:28 | [log](user_data/convergence_logs/PRICEFOLLOWINGX-ladder.log) |
| `ParabolicSarStrategy` | `spot_long` | `E1_expanded` | 24042 | `convergence:288:warmup_supplied` | 2026-09-01 12:39:54 | [log](user_data/convergence_logs/ParabolicSarStrategy-ladder.log) |
| `Persia` | `spot_long` | `E1_expanded` | 176 | `convergence:2016:warmup_supplied` | 2026-09-04 10:30:24 | [archive](user_data/profile_smoke/Persia-f2f6ac3e-2026-09-04_10-30-24.zip) [log](user_data/convergence_logs/Persia-f2f6ac3e-ladder.log) |
| `PowerTower` | `spot_long` | `E1_expanded` | 5001 | `convergence:288` | 2026-09-03 14:01:36 | [log](user_data/convergence_logs/PowerTower-ladder.log) |
| `PpoMomentumStrategy` | `spot_long` | `E1_expanded` | 20537 | `convergence:288:warmup_supplied` | 2026-09-01 12:40:19 | [log](user_data/convergence_logs/PpoMomentumStrategy-ladder.log) |
| `PriceActionCandleStrategy` | `spot_long` | `E1_expanded` | 24545 | `convergence:288:warmup_supplied` | 2026-09-01 12:40:43 | [log](user_data/convergence_logs/PriceActionCandleStrategy-ladder.log) |
| `PriceChannelStrategy` | `spot_long` | `E1_expanded` | 17105 | `convergence:288:warmup_supplied` | 2026-09-01 12:41:07 | [log](user_data/convergence_logs/PriceChannelStrategy-ladder.log) |
| `PumpDetector` | `spot_long` | `E1_expanded` | 32258 | `convergence:2016:warmup_supplied` | 2026-09-01 12:41:32 | [log](user_data/convergence_logs/PumpDetector-ladder.log) |
| `Quickie` | `spot_long` | `E1_expanded` | 7676 | `convergence:288:warmup_supplied` | 2026-09-01 14:51:56 | [log](user_data/convergence_logs/Quickie-ladder.log) |
| `RSI` | `spot_long` | `E1_expanded` | 400 | `convergence:192:warmup_supplied` | 2026-09-01 16:09:44 | [log](user_data/convergence_logs/RSI-ladder.log) |
| `RSIBB02` | `spot_long` | `E1_expanded` | 10 | `convergence:168:warmup_supplied` | 2026-09-01 19:50:27 | [archive](user_data/profile_smoke/RSIBB02-2026-09-01_19-50-27.zip) [log](user_data/convergence_logs/RSIBB02-ladder.log) |
| `RSIDirectionalWithTrend` | `spot_long` | `E1_expanded` | 752 | `convergence:720:warmup_supplied` | 2026-09-03 19:48:33 | [log](user_data/convergence_logs/RSIDirectionalWithTrend-0268a91f-ladder.log) |
| `RSIDirectionalWithTrendSlow` | `spot_long` | `E1_expanded` | 546 | `convergence:2160:warmup_supplied` | 2026-09-03 19:49:38 | [log](user_data/convergence_logs/RSIDirectionalWithTrendSlow-247b9c8f-ladder.log) |
| `RSI_BB` | `spot_long` | `E1_expanded` | 14931 | `convergence:192:warmup_supplied` | 2026-09-01 16:10:33 | [log](user_data/convergence_logs/RSI_BB-ladder.log) |
| `RSI_EMA_strategy` | `spot_long` | `E1_expanded` | 5240 | `convergence:288:warmup_supplied` | 2026-09-01 16:11:22 | [log](user_data/convergence_logs/RSI_EMA_strategy-ladder.log) |
| `RSIv2` | `spot_long` | `E1_expanded` | 5908 | `convergence:192:warmup_supplied` | 2026-09-01 12:41:55 | [log](user_data/convergence_logs/RSIv2-ladder.log) |
| `RalliV1` | `spot_long` | `E1_expanded` | 657 | `convergence:2016:warmup_supplied` | 2026-09-01 14:52:21 | [log](user_data/convergence_logs/RalliV1-ladder.log) |
| `RalliV1_disable56` | `spot_long` | `E1_expanded` | 651 | `convergence:2016:warmup_supplied` | 2026-09-01 14:52:46 | [log](user_data/convergence_logs/RalliV1_disable56-ladder.log) |
| `RegimeFilterStrategy` | `futures_long_short` | `E1_expanded` | 65 | `convergence:336:warmup_supplied` | 2026-09-03 14:02:02 | [log](user_data/convergence_logs/RegimeFilterStrategy-ladder.log) |
| `ReinforcedAverageStrategy` | `spot_long` | `E1_expanded` | 1163 | `convergence:84:warmup_supplied` | 2026-09-01 14:53:35 | [log](user_data/convergence_logs/ReinforcedAverageStrategy-ladder.log) |
| `ReinforcedSmoothScalp` | `spot_long` | `E1_expanded` | 663 | `convergence:2880:warmup_supplied` | 2026-09-01 16:12:10 | [log](user_data/convergence_logs/ReinforcedSmoothScalp-ladder.log) |
| `RobotradingBody` | `spot_long` | `E1_expanded` | 2895 | `convergence:100` | 2026-09-03 14:02:27 | [log](user_data/convergence_logs/RobotradingBody-ladder.log) |
| `RocMomentumStrategy` | `spot_long` | `E1_expanded` | 26606 | `convergence:576:warmup_supplied` | 2026-09-01 12:42:20 | [log](user_data/convergence_logs/RocMomentumStrategy-ladder.log) |
| `Roth01` | `spot_long` | `E1_expanded` | 12346 | `convergence:288:warmup_supplied` | 2026-09-01 16:13:01 | [log](user_data/convergence_logs/Roth01-ladder.log) |
| `Roth03` | `spot_long` | `E1_expanded` | 3509 | `convergence:288:warmup_supplied` | 2026-09-01 16:13:52 | [log](user_data/convergence_logs/Roth03-ladder.log) |
| `RsiBollingerStrategy` | `spot_long` | `E1_expanded` | 2885 | `convergence:168:warmup_supplied` | 2026-09-01 12:42:44 | [log](user_data/convergence_logs/RsiBollingerStrategy-ladder.log) |
| `RsiDivergenceStrategy` | `spot_long` | `E1_expanded` | 474 | `convergence:288:warmup_supplied` | 2026-09-01 14:54:00 | [log](user_data/convergence_logs/RsiDivergenceStrategy-ladder.log) |
| `SAR` | `spot_long` | `E1_expanded` | 30880 | `convergence:288:warmup_supplied` | 2026-09-03 19:50:11 | [log](user_data/convergence_logs/SAR-c00b2014-ladder.log) |
| `SMAIP3` | `spot_long` | `E1_expanded` | 364 | `convergence:2016:warmup_supplied` | 2026-09-03 14:02:54 | [log](user_data/convergence_logs/SMAIP3-ladder.log) |
| `SMAIP3v2` | `spot_long` | `E1_expanded` | 16 | `convergence:2016:warmup_supplied` | 2026-09-06 14:53:00 | [archive](user_data/profile_smoke/SMAIP3v2-e79dedd0-2026-09-06_14-53-00.zip) [log](user_data/convergence_logs/SMAIP3v2-ladder.log) |
| `SMAOG` | `spot_long` | `E1_expanded` | 538 | `convergence:2016:warmup_supplied` | 2026-09-03 14:03:21 | [log](user_data/convergence_logs/SMAOG-ladder.log) |
| `SMAOffset` | `spot_long` | `E1_expanded` | 2108 | `convergence:288:warmup_supplied` | 2026-09-01 14:54:50 | [log](user_data/convergence_logs/SMAOffset-ladder.log) |
| `SMAOffsetProtectOpt` | `spot_long` | `E1_expanded` | 181 | `convergence:2016:warmup_supplied` | 2026-09-01 14:55:15 | [log](user_data/convergence_logs/SMAOffsetProtectOpt-ladder.log) |
| `SMAOffsetProtectOptV0` | `spot_long` | `E1_expanded` | 253 | `convergence:2016:warmup_supplied` | 2026-09-01 14:55:41 | [log](user_data/convergence_logs/SMAOffsetProtectOptV0-ladder.log) |
| `SMAOffsetProtectOptV1` | `spot_long` | `E1_expanded` | 203 | `convergence:2016:warmup_supplied` | 2026-09-01 14:56:06 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1-ladder.log) |
| `SMAOffsetProtectOptV1HO1` | `spot_long` | `E1_expanded` | 1233 | `convergence:2016:warmup_supplied` | 2026-09-01 14:56:32 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1HO1-ladder.log) |
| `SMAOffsetProtectOptV1Mod` | `spot_long` | `E1_expanded` | 202 | `convergence:2016:warmup_supplied` | 2026-09-01 14:56:58 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1Mod-ladder.log) |
| `SMAOffsetProtectOptV1Mod2` | `spot_long` | `E1_expanded` | 206 | `convergence:2016:warmup_supplied` | 2026-09-01 14:57:24 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1Mod2-ladder.log) |
| `SMAOffsetProtectOptV1_kkeue_20210619` | `spot_long` | `E1_expanded` | 206 | `convergence:2016:warmup_supplied` | 2026-09-01 14:57:51 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1_kkeue_20210619-ladder.log) |
| `SMAOffsetV2` | `spot_long` | `E1_expanded` | 794 | `convergence:200` | 2026-09-03 14:03:48 | [log](user_data/convergence_logs/SMAOffsetV2-ladder.log) |
| `SMAOffset_Hippocritical_dca` | `spot_long` | `E1_expanded` | 218 | `convergence:2016:warmup_supplied` | 2026-09-01 14:58:16 | [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca-ladder.log) |
| `SMAOffset_Hippocritical_dca_leverage` | `futures_long` | `E1_expanded` | 18 | `convergence:2016:warmup_supplied` | 2026-09-02 07:41:14 | [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca_leverage-ladder.log) |
| `SMAOffset_Hippocritical_dca_old` | `spot_long` | `E1_expanded` | 218 | `convergence:2016:warmup_supplied` | 2026-09-01 14:59:11 | [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca_old-ladder.log) |
| `SMAOffset_Hippocritical_dca_protections` | `spot_long` | `E1_expanded` | 218 | `convergence:2016:warmup_supplied` | 2026-09-01 14:59:41 | [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca_protections-ladder.log) |
| `SMA_BBRSI` | `spot_long` | `E1_expanded` | 706 | `convergence:2016:warmup_supplied` | 2026-09-01 15:00:08 | [log](user_data/convergence_logs/SMA_BBRSI-ladder.log) |
| `SRsi` | `spot_long` | `E1_expanded` | 23768 | `convergence:1440:warmup_supplied` | 2026-09-01 12:43:10 | [log](user_data/convergence_logs/SRsi-ladder.log) |
| `STRATEGY_RSI_BB_BOUNDS_CROSS` | `spot_long` | `E1_expanded` | 7197 | `convergence:288:warmup_supplied` | 2026-09-01 12:43:35 | [log](user_data/convergence_logs/STRATEGY_RSI_BB_BOUNDS_CROSS-ladder.log) |
| `STRATEGY_RSI_BB_CROSS` | `spot_long` | `E1_expanded` | 16827 | `convergence:288:warmup_supplied` | 2026-09-01 12:44:00 | [log](user_data/convergence_logs/STRATEGY_RSI_BB_CROSS-ladder.log) |
| `SampleStrategy` | `spot_long` | `E1_expanded` | 12724 | `convergence:288:warmup_supplied` | 2026-09-01 12:44:24 | [log](user_data/convergence_logs/SampleStrategy-ladder.log) |
| `SampleStrategyV2` | `spot_long` | `E1_expanded` | 5882 | `convergence:576` | 2026-09-03 14:04:18 | [log](user_data/convergence_logs/SampleStrategyV2-ladder.log) |
| `Sar` | `spot_long` | `E1_expanded` | 12724 | `convergence:288:warmup_supplied` | 2026-09-01 15:00:35 | [log](user_data/convergence_logs/Sar-ladder.log) |
| `Saturn5` | `spot_long` | `E1_expanded` | 3356 | `convergence:1344:warmup_supplied` | 2026-09-01 15:01:02 | [log](user_data/convergence_logs/Saturn5-ladder.log) |
| `Scalp` | `spot_long` | `E1_expanded` | 28414 | `convergence:1440:warmup_supplied` | 2026-09-01 15:01:53 | [log](user_data/convergence_logs/Scalp-ladder.log) |
| `Schism` | `spot_long` | `E1_expanded` | 388 | `convergence:288:warmup_supplied` | 2026-09-03 21:00:02 | [archive](user_data/profile_smoke/Schism-4f0b8f62-2026-09-03_21-00-02.zip) [log](user_data/convergence_logs/Schism-ladder.log) |
| `Schism2` | `spot_long` | `E1_expanded` | 149 | `convergence:288:warmup_supplied` | 2026-09-03 21:05:52 | [archive](user_data/profile_smoke/Schism2-488547c4-2026-09-03_21-05-52.zip) [log](user_data/convergence_logs/Schism2-ladder.log) |
| `Schism3` | `spot_long` | `E1_expanded` | 3631 | `convergence:288:warmup_supplied` | 2026-09-01 15:02:45 | [log](user_data/convergence_logs/Schism3-ladder.log) |
| `Schism4` | `spot_long` | `E1_expanded` | 993 | `convergence:288:warmup_supplied` | 2026-09-01 15:03:10 | [log](user_data/convergence_logs/Schism4-ladder.log) |
| `Seb` | `spot_long` | `E1_expanded` | 13947 | `convergence:576:warmup_supplied` | 2026-09-01 15:04:02 | [log](user_data/convergence_logs/Seb-ladder.log) |
| `Simple` | `spot_long` | `E1_expanded` | 16675 | `convergence:288:warmup_supplied` | 2026-09-01 15:04:56 | [log](user_data/convergence_logs/Simple-ladder.log) |
| `SimpleHopt` | `spot_long` | `E1_expanded` | 16675 | `convergence:288:warmup_supplied` | 2026-09-01 16:14:42 | [log](user_data/convergence_logs/SimpleHopt-ladder.log) |
| `SimpleHopt1Along` | `spot_long` | `E1_expanded` | 10 | `convergence:540:warmup_supplied` | 2026-09-06 14:47:40 | [archive](user_data/profile_smoke/SimpleHopt1Along-df7ee9ca-2026-09-06_14-47-40.zip) [log](user_data/convergence_logs/SimpleHopt1Along-ladder.log) |
| `SlowPotato` | `spot_long` | `E1_expanded` | 638 | `convergence:288:warmup_supplied` | 2026-09-01 16:15:31 | [log](user_data/convergence_logs/SlowPotato-ladder.log) |
| `Slowbro` | `spot_long` | `E1_expanded` | 95 | `convergence:30` | 2026-09-03 14:04:45 | [log](user_data/convergence_logs/Slowbro-ladder.log) |
| `SmaRsiStrategy` | `spot_long` | `E1_expanded` | 575 | `convergence:90:warmup_supplied` | 2026-09-01 12:44:48 | [log](user_data/convergence_logs/SmaRsiStrategy-ladder.log) |
| `SmartMoneyStrategy` | `spot_long` | `E1_expanded` | 285 | `convergence:1440:warmup_supplied` | 2026-09-01 16:16:19 | [log](user_data/convergence_logs/SmartMoneyStrategy-ladder.log) |
| `SmartMoneyStrategyHyperopt` | `spot_long` | `E1_expanded` | 8 | `convergence:2160:warmup_supplied` | 2026-09-06 15:11:13 | [archive](user_data/profile_smoke/SmartMoneyStrategyHyperopt-fff5e4c0-2026-09-06_15-11-13.zip) [log](user_data/convergence_logs/SmartMoneyStrategyHyperopt-ladder.log) |
| `SmoothOperator` | `spot_long` | `E1_expanded` | 17127 | `convergence:288:warmup_supplied` | 2026-09-01 15:05:49 | [log](user_data/convergence_logs/SmoothOperator-ladder.log) |
| `SmoothScalp` | `spot_long` | `E1_expanded` | 26236 | `convergence:1440:warmup_supplied` | 2026-09-01 15:06:43 | [log](user_data/convergence_logs/SmoothScalp-ladder.log) |
| `SqueezeMomentum` | `spot_long` | `E1_expanded` | 277 | `convergence:2016:warmup_supplied` | 2026-09-06 14:58:41 | [archive](user_data/profile_smoke/SqueezeMomentum-55dbc2ef-2026-09-06_14-58-41.zip) [log](user_data/convergence_logs/SqueezeMomentum-ladder.log) |
| `SqueezeMomentumStrategy` | `spot_long` | `E1_expanded` | 23183 | `convergence:288:warmup_supplied` | 2026-09-01 12:45:12 | [log](user_data/convergence_logs/SqueezeMomentumStrategy-ladder.log) |
| `StarRise` | `spot_long` | `E1_expanded` | 220 | `convergence:2016:warmup_supplied` | 2026-09-01 15:07:11 | [log](user_data/convergence_logs/StarRise-ladder.log) |
| `StarRise_strat` | `spot_long` | `E1_expanded` | 255 | `convergence:2016:warmup_supplied` | 2026-09-01 15:07:38 | [log](user_data/convergence_logs/StarRise_strat-ladder.log) |
| `Stavix2` | `spot_long` | `E1_expanded` | 81 | `convergence:1440:warmup_supplied` | 2026-09-01 19:51:30 | [archive](user_data/profile_smoke/Stavix2-2026-09-01_19-51-30.zip) [log](user_data/convergence_logs/Stavix2-4c91e408-ladder.log) |
| `StochRSITEMA` | `spot_long` | `E1_expanded` | 4542 | `convergence:576:warmup_supplied` | 2026-09-03 14:05:12 | [log](user_data/convergence_logs/StochRSITEMA-ladder.log) |
| `StochasticCciStrategy` | `spot_long` | `E1_expanded` | 1325 | `convergence:336:warmup_supplied` | 2026-09-03 14:05:38 | [log](user_data/convergence_logs/StochasticCciStrategy-ladder.log) |
| `StochasticOversoldStrategy` | `spot_long` | `E1_expanded` | 23710 | `convergence:288:warmup_supplied` | 2026-09-01 12:45:36 | [log](user_data/convergence_logs/StochasticOversoldStrategy-ladder.log) |
| `StochasticRsiStrategy` | `spot_long` | `E1_expanded` | 24673 | `convergence:288:warmup_supplied` | 2026-09-01 12:46:00 | [log](user_data/convergence_logs/StochasticRsiStrategy-ladder.log) |
| `Strategy001` | `spot_long` | `E1_expanded` | 13947 | `convergence:576:warmup_supplied` | 2026-09-01 16:17:10 | [log](user_data/convergence_logs/Strategy001-ladder.log) |
| `Strategy001_custom_exit` | `spot_long` | `E1_expanded` | 2581 | `convergence:576:warmup_supplied` | 2026-09-01 16:18:03 | [log](user_data/convergence_logs/Strategy001_custom_exit-ladder.log) |
| `Strategy001_custom_sell` | `spot_long` | `E1_expanded` | 17710 | `convergence:576:warmup_supplied` | 2026-09-01 16:18:58 | [log](user_data/convergence_logs/Strategy001_custom_sell-ladder.log) |
| `Strategy002` | `spot_long` | `E1_expanded` | 1293 | `convergence:288:warmup_supplied` | 2026-09-01 16:19:49 | [log](user_data/convergence_logs/Strategy002-ladder.log) |
| `Strategy003` | `spot_long` | `E1_expanded` | 3498 | `convergence:576:warmup_supplied` | 2026-09-01 16:20:40 | [log](user_data/convergence_logs/Strategy003-ladder.log) |
| `Strategy004` | `spot_long` | `E1_expanded` | 6076 | `convergence:576:warmup_supplied` | 2026-09-01 16:21:32 | [log](user_data/convergence_logs/Strategy004-ladder.log) |
| `Strategy005` | `spot_long` | `E1_expanded` | 5597 | `convergence:288:warmup_supplied` | 2026-09-01 16:22:21 | [log](user_data/convergence_logs/Strategy005-ladder.log) |
| `StrategyScalpingFast` | `spot_long` | `E1_expanded` | 4830 | `convergence:1440:warmup_supplied` | 2026-09-01 12:46:27 | [log](user_data/convergence_logs/StrategyScalpingFast-ladder.log) |
| `StrategyScalpingFast2` | `spot_long` | `E1_expanded` | 1468 | `convergence:1440:warmup_supplied` | 2026-09-01 16:23:18 | [log](user_data/convergence_logs/StrategyScalpingFast2-ladder.log) |
| `SuperHV27` | `spot_long` | `E1_expanded` | 226 | `convergence:576:warmup_supplied` | 2026-09-03 21:02:15 | [archive](user_data/profile_smoke/SuperHV27-aefe004a-2026-09-03_21-02-15.zip) [log](user_data/convergence_logs/SuperHV27-ladder.log) |
| `SuperTrend` | `spot_long` | `E1_expanded` | 2219 | `convergence:1440:warmup_supplied` | 2026-09-03 19:50:54 | [log](user_data/convergence_logs/SuperTrend-e9770a14-ladder.log) |
| `SupertrendStrategy` | `spot_long` | `E1_expanded` | 3820 | `convergence:336:warmup_supplied` | 2026-09-02 07:43:31 | [log](user_data/convergence_logs/SupertrendStrategy-ladder.log) |
| `SwingHigh` | `spot_long` | `E1_expanded` | 20 | `convergence:336:warmup_supplied` | 2026-09-01 19:52:15 | [archive](user_data/profile_smoke/SwingHigh-2026-09-01_19-52-15.zip) [log](user_data/convergence_logs/SwingHigh-ladder.log) |
| `SwingHighToSky` | `spot_long` | `E1_expanded` | 6105 | `convergence:672:warmup_supplied` | 2026-09-03 07:45:15 | [log](user_data/convergence_logs/SwingHighToSky-ladder.log) |
| `TD` | `spot_long` | `E1_expanded` | 6164 | `convergence:12:warmup_supplied` | 2026-09-01 15:11:03 | [log](user_data/convergence_logs/TD-ladder.log) |
| `TDSequentialStrategy` | `spot_long` | `E1_expanded` | 4587 | `convergence:24` | 2026-09-03 14:06:05 | [log](user_data/convergence_logs/TDSequentialStrategy-ladder.log) |
| `TEMA` | `spot_long` | `E1_expanded` | 25158 | `convergence:1440:warmup_supplied` | 2026-09-01 15:11:31 | [log](user_data/convergence_logs/TEMA-ladder.log) |
| `TRIWAVE` | `spot_long` | `E1_expanded` | 3624 | `convergence:672:warmup_supplied` | 2026-09-01 12:46:51 | [log](user_data/convergence_logs/TRIWAVE-ladder.log) |
| `TWAPStrategy` | `futures_long_short` | `E1_expanded` | 671 | `convergence:192:warmup_supplied` | 2026-09-01 15:11:56 | [log](user_data/convergence_logs/TWAPStrategy-ladder.log) |
| `TechnicalExampleStrategy` | `spot_long` | `E1_expanded` | 24430 | `convergence:288:warmup_supplied` | 2026-09-01 15:12:44 | [log](user_data/convergence_logs/TechnicalExampleStrategy-ladder.log) |
| `TemaMaster` | `spot_long` | `E1_expanded` | 6494 | `convergence:288:warmup_supplied` | 2026-09-01 16:24:07 | [log](user_data/convergence_logs/TemaMaster-ladder.log) |
| `TemaMaster3` | `spot_long` | `E1_expanded` | 6058 | `convergence:2880:warmup_supplied` | 2026-09-01 16:24:59 | [log](user_data/convergence_logs/TemaMaster3-ladder.log) |
| `TemaPure` | `spot_long` | `E1_expanded` | 9651 | `convergence:2016:warmup_supplied` | 2026-09-01 16:25:50 | [log](user_data/convergence_logs/TemaPure-ladder.log) |
| `TemaPureNeat` | `spot_long` | `E1_expanded` | 12402 | `convergence:288:warmup_supplied` | 2026-09-01 16:26:40 | [log](user_data/convergence_logs/TemaPureNeat-ladder.log) |
| `TemaPureTwo` | `spot_long` | `E1_expanded` | 12383 | `convergence:2016:warmup_supplied` | 2026-09-01 16:27:31 | [log](user_data/convergence_logs/TemaPureTwo-ladder.log) |
| `TemaStrategy` | `spot_long` | `E1_expanded` | 18093 | `convergence:288:warmup_supplied` | 2026-09-01 12:47:16 | [log](user_data/convergence_logs/TemaStrategy-ladder.log) |
| `TenderEnter` | `spot_long` | `E1_expanded` | 4027 | `convergence:96` | 2026-09-03 14:06:31 | [log](user_data/convergence_logs/TenderEnter-ladder.log) |
| `Test_MAMA4` | `spot_long` | `E1_expanded` | 94 | `convergence:288` | 2026-09-04 06:22:04 | [archive](user_data/profile_smoke/Test_MAMA4-aa83c1d0-2026-09-04_06-22-04.zip) [log](user_data/convergence_logs/Test_MAMA4-ladder.log) |
| `TheForce` | `spot_long` | `E1_expanded` | 24088 | `convergence:672:warmup_supplied` | 2026-09-01 15:13:10 | [log](user_data/convergence_logs/TheForce-ladder.log) |
| `TheRealPullbackV2` | `spot_long` | `E1_expanded` | 918 | `convergence:288:warmup_supplied` | 2026-09-03 14:06:58 | [log](user_data/convergence_logs/TheRealPullbackV2-ladder.log) |
| `ToTheMoon` | `futures_long_short` | `E1_expanded` | 16 | `convergence:24:warmup_supplied` | 2026-09-01 15:13:58 | [log](user_data/convergence_logs/ToTheMoon-ladder.log) |
| `TouchEmaDelayStrategy` | `spot_long` | `E1_expanded` | 2331 | `convergence:480:warmup_supplied` | 2026-09-01 16:28:24 | [log](user_data/convergence_logs/TouchEmaDelayStrategy-ladder.log) |
| `TouchEmaStrategy` | `spot_long` | `E1_expanded` | 5193 | `convergence:288:warmup_supplied` | 2026-09-01 16:29:16 | [log](user_data/convergence_logs/TouchEmaStrategy-ladder.log) |
| `TrendAtrStrategy` | `spot_long` | `E1_expanded` | 3067 | `convergence:540:warmup_supplied` | 2026-09-01 12:47:40 | [log](user_data/convergence_logs/TrendAtrStrategy-ladder.log) |
| `Trend_Strength_Directional` | `spot_long` | `E1_expanded` | 7684 | `convergence:192:warmup_supplied` | 2026-09-01 16:30:06 | [log](user_data/convergence_logs/Trend_Strength_Directional-ladder.log) |
| `TripleEmaStrategy` | `spot_long` | `E1_expanded` | 17670 | `convergence:288:warmup_supplied` | 2026-09-01 12:48:03 | [log](user_data/convergence_logs/TripleEmaStrategy-ladder.log) |
| `TrixSignalStrategy` | `spot_long` | `E1_expanded` | 17885 | `convergence:288:warmup_supplied` | 2026-09-01 12:48:28 | [log](user_data/convergence_logs/TrixSignalStrategy-ladder.log) |
| `TrixStrategy` | `spot_long` | `E1_expanded` | 13554 | `convergence:168:warmup_supplied` | 2026-09-03 14:07:24 | [log](user_data/convergence_logs/TrixStrategy-ladder.log) |
| `TrixV15Strategy` | `spot_long` | `E1_expanded` | 1444 | `convergence:168:warmup_supplied` | 2026-09-03 14:07:50 | [log](user_data/convergence_logs/TrixV15Strategy-ladder.log) |
| `TrixV21Strategy` | `spot_long` | `E1_expanded` | 1152 | `convergence:2160:warmup_supplied` | 2026-09-01 15:15:37 | [log](user_data/convergence_logs/TrixV21Strategy-ladder.log) |
| `TrixV23Strategy` | `spot_long` | `E1_expanded` | 1305 | `convergence:2160:warmup_supplied` | 2026-09-01 15:16:03 | [log](user_data/convergence_logs/TrixV23Strategy-ladder.log) |
| `TwoCandle` | `spot_long` | `E1_expanded` | 18935 | `convergence:168:warmup_supplied` | 2026-09-01 16:30:56 | [log](user_data/convergence_logs/TwoCandle-ladder.log) |
| `UltimateMomentumIndicator` | `spot_long` | `E1_expanded` | 8147 | `convergence:576:warmup_supplied` | 2026-09-03 14:08:16 | [log](user_data/convergence_logs/UltimateMomentumIndicator-ladder.log) |
| `UniversalMACD` | `spot_long` | `E1_expanded` | 2090 | `convergence:288:warmup_supplied` | 2026-09-01 12:48:53 | [log](user_data/convergence_logs/UniversalMACD-ladder.log) |
| `Uptrend` | `spot_long` | `E1_expanded` | 471 | `convergence:2016:warmup_supplied` | 2026-09-01 15:16:28 | [log](user_data/convergence_logs/Uptrend-ladder.log) |
| `VWAP` | `spot_long` | `E1_expanded` | 986 | `convergence:2016:warmup_supplied` | 2026-09-01 15:17:16 | [log](user_data/convergence_logs/VWAP-ladder.log) |
| `VolatilitySystem` | `futures_long` | `E1_expanded` | 9 | `convergence:336:warmup_supplied` | 2026-09-01 15:18:07 | [log](user_data/convergence_logs/VolatilitySystem-ladder.log) |
| `VolatilitySystemV2` | `futures_long_short` | `E1_expanded` | 24 | `convergence:336:warmup_supplied` | 2026-09-01 15:18:57 | [log](user_data/convergence_logs/VolatilitySystemV2-ladder.log) |
| `VolumeBreakoutStrategy` | `spot_long` | `E1_expanded` | 16564 | `convergence:288:warmup_supplied` | 2026-09-01 12:49:17 | [log](user_data/convergence_logs/VolumeBreakoutStrategy-ladder.log) |
| `VortexStrategy` | `spot_long` | `E1_expanded` | 29787 | `convergence:288:warmup_supplied` | 2026-09-01 12:49:42 | [log](user_data/convergence_logs/VortexStrategy-ladder.log) |
| `VwapReversionStrategy` | `spot_long` | `E1_expanded` | 22316 | `convergence:576:warmup_supplied` | 2026-09-01 12:50:07 | [log](user_data/convergence_logs/VwapReversionStrategy-ladder.log) |
| `WTX3` | `futures_long_short` | `E1_expanded` | 740 | `convergence:2016:warmup_supplied` | 2026-09-02 20:34:20 | [log](user_data/convergence_logs/WTX3-ladder.log) |
| `WaveTrendStra` | `spot_long` | `E1_expanded` | 9256 | `convergence:180:warmup_supplied` | 2026-09-01 15:19:48 | [log](user_data/convergence_logs/WaveTrendStra-ladder.log) |
| `WilliamsRStrategy` | `spot_long` | `E1_expanded` | 26924 | `convergence:2016:warmup_supplied` | 2026-09-01 12:50:33 | [log](user_data/convergence_logs/WilliamsRStrategy-ladder.log) |
| `XebTradeStrat` | `spot_long` | `E1_expanded` | 7950 | `convergence:1440:warmup_supplied` | 2026-09-06 14:59:12 | [archive](user_data/profile_smoke/XebTradeStrat-5d160cab-2026-09-06_14-59-12.zip) [log](user_data/convergence_logs/XebTradeStrat-ladder.log) |
| `XtraThicc` | `spot_long` | `E1_expanded` | 9167 | `convergence:288` | 2026-09-03 14:08:44 | [log](user_data/convergence_logs/XtraThicc-ladder.log) |
| `YOLO` | `spot_long` | `E1_expanded` | 560 | `convergence:1440:warmup_supplied` | 2026-09-01 15:20:39 | [log](user_data/convergence_logs/YOLO-ladder.log) |
| `ZScoreMeanReversionStrategy` | `spot_long` | `E1_expanded` | 37 | `convergence:540:warmup_supplied` | 2026-09-01 15:21:04 | [log](user_data/convergence_logs/ZScoreMeanReversionStrategy-ladder.log) |
| `ZaratustraDCA2_06` | `futures_long_short` | `E1_expanded` | 241 | `convergence:288:warmup_supplied` | 2026-09-02 07:48:03 | [log](user_data/convergence_logs/ZaratustraDCA2_06-ladder.log) |
| `ZaratustraDCA2_07` | `futures_long_short` | `E1_expanded` | 219 | `convergence:288:warmup_supplied` | 2026-09-02 07:49:13 | [log](user_data/convergence_logs/ZaratustraDCA2_07-ladder.log) |
| `ZaratustraDCA5` | `futures_long_short` | `E1_expanded` | 233 | `convergence:288:warmup_supplied` | 2026-09-02 07:51:31 | [log](user_data/convergence_logs/ZaratustraDCA5-ladder.log) |
| `adaptive` | `spot_long` | `E1_expanded` | 647 | `convergence:2016:warmup_supplied` | 2026-09-01 15:23:35 | [log](user_data/convergence_logs/adaptive-ladder.log) |
| `adaptive_trend` | `spot_long` | `E1_expanded` | 322 | `convergence:180` | 2026-09-03 14:09:10 | [log](user_data/convergence_logs/adaptive_trend-ladder.log) |
| `adx_opt_strat` | `spot_long` | `E1_expanded` | 234 | `convergence:1440:warmup_supplied` | 2026-09-01 19:53:04 | [archive](user_data/profile_smoke/adx_opt_strat-2026-09-01_19-53-04.zip) [log](user_data/convergence_logs/adx_opt_strat-ladder.log) |
| `adxbbrsi2` | `spot_long` | `E1_expanded` | 741 | `convergence:336:warmup_supplied` | 2026-09-01 12:50:58 | [log](user_data/convergence_logs/adxbbrsi2-ladder.log) |
| `bb_rsi_opt_new` | `spot_long` | `E1_expanded` | 8 | `convergence:168:warmup_supplied` | 2026-09-01 19:53:42 | [archive](user_data/profile_smoke/bb_rsi_opt_new-2026-09-01_19-53-42.zip) [log](user_data/convergence_logs/bb_rsi_opt_new-ladder.log) |
| `bbandrsi` | `spot_long` | `E1_expanded` | 6758 | `convergence:192:warmup_supplied` | 2026-09-01 16:31:44 | [log](user_data/convergence_logs/bbandrsi-ladder.log) |
| `bbrsi` | `spot_long` | `E1_expanded` | 5507 | `convergence:180:warmup_supplied` | 2026-09-03 19:51:59 | [log](user_data/convergence_logs/bbrsi-10d8c6d1-ladder.log) |
| `bbrsi1_strategy` | `spot_long` | `E1_expanded` | 432 | `convergence:288:warmup_supplied` | 2026-09-01 20:44:53 | [archive](user_data/profile_smoke/bbrsi1_strategy-2026-09-01_20-44-53.zip) [log](user_data/convergence_logs/bbrsi1_strategy-ladder.log) |
| `bbrsi4Freq` | `spot_long` | `E1_expanded` | 4791 | `convergence:168:warmup_supplied` | 2026-09-01 12:51:45 | [log](user_data/convergence_logs/bbrsi4Freq-ladder.log) |
| `bestV2` | `spot_long` | `E1_expanded` | 345 | `convergence:2016:warmup_supplied` | 2026-09-03 14:09:38 | [log](user_data/convergence_logs/bestV2-ladder.log) |
| `botbaby` | `spot_long` | `E1_expanded` | 12338 | `convergence:1440:warmup_supplied` | 2026-09-03 14:10:04 | [log](user_data/convergence_logs/botbaby-ladder.log) |
| `chispei` | `spot_long` | `E1_expanded` | 50 | `convergence:42:warmup_supplied` | 2026-09-01 19:55:01 | [archive](user_data/profile_smoke/chispei-2026-09-01_19-55-01.zip) [log](user_data/convergence_logs/chispei-ladder.log) |
| `conny` | `spot_long` | `E1_expanded` | 5825 | `convergence:96:warmup_supplied` | 2026-09-01 12:52:10 | [log](user_data/convergence_logs/conny-ladder.log) |
| `cryptohassle` | `spot_long` | `E1_expanded` | 82 | `convergence:336:warmup_supplied` | 2026-09-01 19:55:42 | [archive](user_data/profile_smoke/cryptohassle-2026-09-01_19-55-42.zip) [log](user_data/convergence_logs/cryptohassle-ladder.log) |
| `cryptotank` | `spot_long` | `E1_expanded` | 2312 | `convergence:336:warmup_supplied` | 2026-09-03 14:10:30 | [log](user_data/convergence_logs/cryptotank-ladder.log) |
| `cryptotankV2` | `spot_long` | `E1_expanded` | 770 | `convergence:576:warmup_supplied` | 2026-09-01 12:52:35 | [log](user_data/convergence_logs/cryptotankV2-ladder.log) |
| `cryptotankV5` | `spot_long` | `E1_expanded` | 4782 | `convergence:672:warmup_supplied` | 2026-09-03 14:10:56 | [log](user_data/convergence_logs/cryptotankV5-ladder.log) |
| `custom_sell` | `spot_long` | `E1_expanded` | 327 | `convergence:288` | 2026-08-31 16:13:12 | [archive](user_data/profile_smoke/custom_sell-2026-08-31_16-13-12.zip) [log](user_data/convergence_logs/custom_sell-ladder.log) |
| `dualwave` | `spot_long` | `E1_expanded` | 1767 | `convergence:672:warmup_supplied` | 2026-09-01 15:24:26 | [log](user_data/convergence_logs/dualwave-ladder.log) |
| `e6v34` | `spot_long` | `E1_expanded` | 19447 | `convergence:672:warmup_supplied` | 2026-09-01 16:32:32 | [log](user_data/convergence_logs/e6v34-ladder.log) |
| `eltoro` | `spot_long` | `E1_expanded` | 3704 | `convergence:1344:warmup_supplied` | 2026-09-01 12:53:00 | [log](user_data/convergence_logs/eltoro-ladder.log) |
| `eltoro1_4` | `spot_long` | `E1_expanded` | 2393 | `convergence:2160:warmup_supplied` | 2026-09-01 12:53:24 | [log](user_data/convergence_logs/eltoro1_4-ladder.log) |
| `eltoro1_4_simple` | `spot_long` | `E1_expanded` | 2417 | `convergence:672:warmup_supplied` | 2026-09-01 12:53:49 | [log](user_data/convergence_logs/eltoro1_4_simple-ladder.log) |
| `ema` | `spot_long` | `E1_expanded` | 30806 | `convergence:2016:warmup_supplied` | 2026-09-01 16:33:20 | [log](user_data/convergence_logs/ema-ladder.log) |
| `fahmibah` | `spot_long` | `E1_expanded` | 20943 | `convergence:288:warmup_supplied` | 2026-09-03 14:11:27 | [log](user_data/convergence_logs/fahmibah-ladder.log) |
| `gettinMoist` | `spot_long` | `E1_expanded` | 20036 | `convergence:288:warmup_supplied` | 2026-09-01 12:54:38 | [log](user_data/convergence_logs/gettinMoist-ladder.log) |
| `hansencandlepatternV1` | `spot_long` | `E1_expanded` | 17165 | `convergence:24:warmup_supplied` | 2026-09-01 15:25:15 | [log](user_data/convergence_logs/hansencandlepatternV1-ladder.log) |
| `heikin` | `spot_long` | `E1_expanded` | 21053 | `convergence:24:warmup_supplied` | 2026-09-01 15:26:03 | [log](user_data/convergence_logs/heikin-ladder.log) |
| `hlhb` | `spot_long` | `E1_expanded` | 861 | `convergence:540:warmup_supplied` | 2026-09-03 19:52:33 | [log](user_data/convergence_logs/hlhb-4d4b7c4a-ladder.log) |
| `ichi` | `spot_long` | `E1_expanded` | 61 | `convergence:168:warmup_supplied` | 2026-09-06 15:16:31 | [archive](user_data/profile_smoke/ichi-a7e6edf3-2026-09-06_15-16-31.zip) [log](user_data/convergence_logs/ichi-a7e6edf3-ladder.log) |
| `keltnerchannel` | `spot_long` | `E1_expanded` | 1131 | `convergence:360:warmup_supplied` | 2026-09-01 15:26:51 | [log](user_data/convergence_logs/keltnerchannel-ladder.log) |
| `mabStra` | `spot_long` | `E1_expanded` | 1174 | `convergence:42:warmup_supplied` | 2026-09-03 07:51:13 | [log](user_data/convergence_logs/mabStra-ladder.log) |
| `macd_recovery` | `spot_long` | `E1_expanded` | 202 | `convergence:2016:warmup_supplied` | 2026-09-01 19:56:22 | [archive](user_data/profile_smoke/macd_recovery-2026-09-01_19-56-22.zip) [log](user_data/convergence_logs/macd_recovery-ladder.log) |
| `mark_strat` | `spot_long` | `E1_expanded` | 942 | `convergence:1440:warmup_supplied` | 2026-09-01 19:57:13 | [archive](user_data/profile_smoke/mark_strat-2026-09-01_19-57-13.zip) [log](user_data/convergence_logs/mark_strat-ladder.log) |
| `mark_strat_opt` | `spot_long` | `E1_expanded` | 11 | `convergence:1440:warmup_supplied` | 2026-09-01 20:50:12 | [archive](user_data/profile_smoke/mark_strat_opt-2026-09-01_20-50-12.zip) [log](user_data/convergence_logs/mark_strat_opt-ladder.log) |
| `momentum` | `futures_long_short` | `E1_expanded` | 682 | `convergence:288` | 2026-09-03 14:12:19 | [log](user_data/convergence_logs/momentum-ladder.log) |
| `momentum_long` | `spot_long` | `E1_expanded` | 15967 | `convergence:288` | 2026-09-03 14:12:46 | [log](user_data/convergence_logs/momentum_long-ladder.log) |
| `momentum_rsi` | `futures_long_short` | `E1_expanded` | 551 | `convergence:200` | 2026-09-03 14:13:38 | [log](user_data/convergence_logs/momentum_rsi-ladder.log) |
| `momentum_wick` | `futures_long_short` | `E1_expanded` | 361 | `convergence:288` | 2026-09-03 14:14:32 | [log](user_data/convergence_logs/momentum_wick-ladder.log) |
| `moonhouse` | `spot_long` | `E1_expanded` | 96 | `convergence:90:warmup_supplied` | 2026-09-01 15:28:29 | [log](user_data/convergence_logs/moonhouse-ladder.log) |
| `pmaxTest` | `spot_long` | `E1_expanded` | 23 | `convergence:2016:warmup_supplied` | 2026-08-31 15:33:16 | [archive](user_data/profile_smoke/pmaxTest-2026-08-31_15-33-16.zip) [log](user_data/convergence_logs/pmaxTest-ladder.log) |
| `quantumfirst` | `spot_long` | `E1_expanded` | 227 | `convergence:288:warmup_supplied` | 2026-09-01 19:57:53 | [archive](user_data/profile_smoke/quantumfirst-2026-09-01_19-57-53.zip) [log](user_data/convergence_logs/quantumfirst-ladder.log) |
| `redditMA` | `spot_long` | `E1_expanded` | 193 | `convergence:192:warmup_supplied` | 2026-09-01 19:58:32 | [archive](user_data/profile_smoke/redditMA-2026-09-01_19-58-32.zip) [log](user_data/convergence_logs/redditMA-ladder.log) |
| `simple_patterns` | `spot_long` | `E1_expanded` | 1845 | `native` | 2026-08-31 15:55:52 | [archive](user_data/profile_smoke/simple_patterns-2026-08-31_15-55-52.zip) |
| `simple_vwap_v1` | `spot_long` | `E1_expanded` | 1 | `convergence:2190:warmup_supplied` | 2026-09-05 15:12:31 | [archive](user_data/profile_smoke/simple_vwap_v1-28330b62-2026-09-05_15-12-31.zip) [log](user_data/convergence_logs/simple_vwap_v1-28330b62-ladder.log) |
| `slope_is_dopeCT` | `spot_long` | `E1_expanded` | 821 | `convergence:672:warmup_supplied` | 2026-09-01 12:55:49 | [log](user_data/convergence_logs/slope_is_dopeCT-ladder.log) |
| `slownsteady` | `spot_long` | `E1_expanded` | 35 | `convergence:2016:warmup_supplied` | 2026-08-31 15:54:44 | [archive](user_data/profile_smoke/slownsteady-2026-08-31_15-54-44.zip) [log](user_data/convergence_logs/slownsteady-ladder.log) |
| `stoploss` | `spot_long` | `E1_expanded` | 12724 | `convergence:288:warmup_supplied` | 2026-09-01 12:56:13 | [log](user_data/convergence_logs/stoploss-ladder.log) |
| `strato` | `spot_long` | `E1_expanded` | 24409 | `convergence:1440:warmup_supplied` | 2026-09-01 12:56:41 | [log](user_data/convergence_logs/strato-ladder.log) |
| `tbtest` | `spot_long` | `E1_expanded` | 4884 | `convergence:288:warmup_supplied` | 2026-09-01 15:30:07 | [log](user_data/convergence_logs/tbtest-ladder.log) |
| `thetank3` | `spot_long` | `E1_expanded` | 8620 | `convergence:672:warmup_supplied` | 2026-09-01 12:57:28 | [log](user_data/convergence_logs/thetank3-ladder.log) |
| `thetank4TV` | `spot_long` | `E1_expanded` | 3023 | `convergence:672:warmup_supplied` | 2026-09-01 12:57:53 | [log](user_data/convergence_logs/thetank4TV-ladder.log) |
| `true_lambo` | `spot_long` | `E1_expanded` | 1194 | `convergence:2016:warmup_supplied` | 2026-09-01 15:30:39 | [log](user_data/convergence_logs/true_lambo-ladder.log) |
| `twinturboV8` | `spot_long` | `E1_expanded` | 131 | `convergence:2016:warmup_supplied` | 2026-09-01 15:31:06 | [log](user_data/convergence_logs/twinturboV8-ladder.log) |
| `twinturboV8_2` | `spot_long` | `E1_expanded` | 119 | `convergence:2016:warmup_supplied` | 2026-09-01 15:31:32 | [log](user_data/convergence_logs/twinturboV8_2-ladder.log) |
| `ultratank` | `spot_long` | `E1_expanded` | 3076 | `convergence:336:warmup_supplied` | 2026-09-01 12:58:17 | [log](user_data/convergence_logs/ultratank-ladder.log) |
| `wavetrend` | `spot_long` | `E1_expanded` | 4691 | `convergence:336:warmup_supplied` | 2026-09-01 12:58:45 | [log](user_data/convergence_logs/wavetrend-ladder.log) |
| `wavetrend_rsi` | `spot_long` | `E1_expanded` | 5240 | `convergence:336:warmup_supplied` | 2026-09-01 12:59:09 | [log](user_data/convergence_logs/wavetrend_rsi-ladder.log) |

The calls behind each, one per gate:

- `A9AV`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy A9AV --strategy-path repair/patched/repos/jaredrsommer_freqtradestrategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/A9AV-fb0d7493 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy A9AV --strategy-path user_data/profile_bias_strategies/A9AV --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/A9AV_startup_288.json --strategy A9AV --strategy-path user_data/profile_bias_strategies/A9AV --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ADXMomentum`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ADXMomentum --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ADXMomentum-d748d610 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ADXMomentum --strategy-path user_data/profile_bias_strategies/ADXMomentum --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ADXMomentum --strategy-path user_data/profile_bias_strategies/ADXMomentum --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `ADX_15M_USDT`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/ADX_15M_USDT-override-c517447bf6b2.json --strategy ADX_15M_USDT --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ADX_15M_USDT --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/ADX_15M_USDT_gate.json --strategy ADX_15M_USDT --strategy-path user_data/profile_bias_strategies/ADX_15M_USDT --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/ADX_15M_USDT_startup_96.json --strategy ADX_15M_USDT --strategy-path user_data/profile_bias_strategies/ADX_15M_USDT --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880 --timeframe 15m
  ```
- `ADX_15M_USDT2`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/ADX_15M_USDT2-override-c517447bf6b2.json --strategy ADX_15M_USDT2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/ADX_15M_USDT2 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ADX_15M_USDT2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/ADX_15M_USDT2_gate.json --strategy ADX_15M_USDT2 --strategy-path user_data/profile_bias_strategies/ADX_15M_USDT2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/ADX_15M_USDT2_startup_96.json --strategy ADX_15M_USDT2 --strategy-path user_data/profile_bias_strategies/ADX_15M_USDT2 --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880 --timeframe 15m
  ```
- `ASDTSRockwellTrading`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ASDTSRockwellTrading --strategy-path user_data/profile_bias_strategies/ASDTSRockwellTrading --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ASDTSRockwellTrading --strategy-path user_data/profile_bias_strategies/ASDTSRockwellTrading --timerange 20190101-20190401 --no-color
  ```
- `ActionZone`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ActionZone --strategy-path user_data/profile_bias_strategies/ActionZone --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ActionZone --strategy-path user_data/profile_bias_strategies/ActionZone --timerange 20190101-20190401 --no-color
  ```
- `AdaptiveMAStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AdaptiveMAStrategy --strategy-path user_data/profile_bias_strategies/AdaptiveMAStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AdaptiveMAStrategy --strategy-path user_data/profile_bias_strategies/AdaptiveMAStrategy --timerange 20190101-20190401 --no-color
  ```
- `AdxSmas`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AdxSmas --strategy-path user_data/profile_bias_strategies/AdxSmas --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AdxSmas --strategy-path user_data/profile_bias_strategies/AdxSmas --timerange 20190101-20190401 --no-color
  ```
- `AdxSmasS`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_short.json --strategy AdxSmasS --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AdxSmasS --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_short.json --strategy AdxSmasS --strategy-path user_data/profile_bias_strategies/AdxSmasS --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_short.json --strategy AdxSmasS --strategy-path user_data/profile_bias_strategies/AdxSmasS --timerange 20200301-20200401 --no-color
  ```
- `AdxStrengthStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AdxStrengthStrategy --strategy-path user_data/profile_bias_strategies/AdxStrengthStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AdxStrengthStrategy --strategy-path user_data/profile_bias_strategies/AdxStrengthStrategy --timerange 20190101-20190401 --no-color
  ```
- `AlligatorStrat`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/AlligatorStrat-override-aa2053461232.json --strategy AlligatorStrat --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AlligatorStrat --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/AlligatorStrat_gate.json --strategy AlligatorStrat --strategy-path user_data/profile_bias_strategies/AlligatorStrat --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/AlligatorStrat_startup_6.json --strategy AlligatorStrat --strategy-path user_data/profile_bias_strategies/AlligatorStrat --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 --timeframe 4h
  ```
- `AlligatorStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AlligatorStrategy --strategy-path user_data/profile_bias_strategies/AlligatorStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AlligatorStrategy --strategy-path user_data/profile_bias_strategies/AlligatorStrategy --timerange 20190101-20190401 --no-color
  ```
- `AlmgrenChrissStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy AlmgrenChrissStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AlmgrenChrissStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy AlmgrenChrissStrategy --strategy-path user_data/profile_bias_strategies/AlmgrenChrissStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy AlmgrenChrissStrategy --strategy-path user_data/profile_bias_strategies/AlmgrenChrissStrategy --timerange 20200301-20200401 --no-color
  ```
- `AlwaysBuy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AlwaysBuy --strategy-path user_data/profile_bias_strategies/AlwaysBuy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/AlwaysBuy_startup_288.json --strategy AlwaysBuy --strategy-path user_data/profile_bias_strategies/AlwaysBuy --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Apollo11`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Apollo11_gate.json --strategy Apollo11 --strategy-path user_data/profile_bias_strategies/Apollo11 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Apollo11 --strategy-path user_data/profile_bias_strategies/Apollo11 --timerange 20190101-20190401 --no-color
  ```
- `AroonTrendStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AroonTrendStrategy --strategy-path user_data/profile_bias_strategies/AroonTrendStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AroonTrendStrategy --strategy-path user_data/profile_bias_strategies/AroonTrendStrategy --timerange 20190101-20190401 --no-color
  ```
- `AtrTrailingStopStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AtrTrailingStopStrategy --strategy-path user_data/profile_bias_strategies/AtrTrailingStopStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AtrTrailingStopStrategy --strategy-path user_data/profile_bias_strategies/AtrTrailingStopStrategy --timerange 20190101-20190401 --no-color
  ```
- `AverageStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AverageStrategy --strategy-path user_data/profile_bias_strategies/AverageStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AverageStrategy --strategy-path user_data/profile_bias_strategies/AverageStrategy --timerange 20190101-20190401 --no-color
  ```
- `AwesomeMacd`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AwesomeMacd --strategy-path user_data/profile_bias_strategies/AwesomeMacd --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/AwesomeMacd_startup_48.json --strategy AwesomeMacd --strategy-path user_data/profile_bias_strategies/AwesomeMacd --timerange 20190101-20190401 --no-color --startup-candle 48 168 336 720 2160
  ```
- `BB10fall`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB10fall --strategy-path repos/shadowp2810_technical_indicators_cryptos/Freqtrade/ft_userdata/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB10fall-cef5331b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BB10fall-cef5331b_gate.json --strategy BB10fall --strategy-path user_data/profile_bias_strategies/BB10fall-cef5331b --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB10fall --strategy-path user_data/profile_bias_strategies/BB10fall-cef5331b --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `BBMod`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBMod --strategy-path repos/eovie_freqtrade_strs/binance/Archive --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBMod-c3880bce --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BBMod-c3880bce_gate.json --strategy BBMod --strategy-path user_data/profile_bias_strategies/BBMod-c3880bce --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBMod --strategy-path user_data/profile_bias_strategies/BBMod --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BBRSI`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/BBRSI-0d31007a-override-f400cf1f3448.json --strategy BBRSI --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSI-0d31007a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BBRSI-0d31007a_gate.json --strategy BBRSI --strategy-path user_data/profile_bias_strategies/BBRSI-0d31007a --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BBRSI_startup_24.json --strategy BBRSI --strategy-path user_data/profile_bias_strategies/BBRSI-0d31007a --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `BBRSI2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI2 --strategy-path user_data/profile_bias_strategies/BBRSI2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI2 --strategy-path user_data/profile_bias_strategies/BBRSI2 --timerange 20190101-20190401 --no-color
  ```
- `BBRSI21`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI21 --strategy-path user_data/profile_bias_strategies/BBRSI21 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI21 --strategy-path user_data/profile_bias_strategies/BBRSI21 --timerange 20190101-20190401 --no-color
  ```
- `BBRSI3366`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI3366 --strategy-path user_data/profile_bias_strategies/BBRSI3366 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI3366 --strategy-path user_data/profile_bias_strategies/BBRSI3366 --timerange 20190101-20190401 --no-color
  ```
- `BBRSI4cust`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI4cust --strategy-path user_data/profile_bias_strategies/BBRSI4cust --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI4cust --strategy-path user_data/profile_bias_strategies/BBRSI4cust --timerange 20190101-20190401 --no-color
  ```
- `BBRSINaiveStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSINaiveStrategy --strategy-path user_data/profile_bias_strategies/BBRSINaiveStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSINaiveStrategy --strategy-path user_data/profile_bias_strategies/BBRSINaiveStrategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSIOptim2020Strategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptim2020Strategy --strategy-path user_data/profile_bias_strategies/BBRSIOptim2020Strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptim2020Strategy --strategy-path user_data/profile_bias_strategies/BBRSIOptim2020Strategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSIOptimStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptimStrategy --strategy-path user_data/profile_bias_strategies/BBRSIOptimStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptimStrategy --strategy-path user_data/profile_bias_strategies/BBRSIOptimStrategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSIOptimizedStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptimizedStrategy --strategy-path user_data/profile_bias_strategies/BBRSIOptimizedStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptimizedStrategy --strategy-path user_data/profile_bias_strategies/BBRSIOptimizedStrategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSIS`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy BBRSIS --strategy-path repair/patched/repos/davidzr_freqtrade-strategies/strategies/BBRSIS --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSIS --cache none --timeframe 5m
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BBRSIS_gate.json --strategy BBRSIS --strategy-path user_data/profile_bias_strategies/BBRSIS --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BBRSIS_startup_288.json --strategy BBRSIS --strategy-path user_data/profile_bias_strategies/BBRSIS --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 8640 25920 --timeframe 5m
  ```
- `BBRSIStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIStrategy --strategy-path user_data/profile_bias_strategies/BBRSIStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIStrategy --strategy-path user_data/profile_bias_strategies/BBRSIStrategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSITV`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSITV --strategy-path user_data/profile_bias_strategies/BBRSITV --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSITV --strategy-path user_data/profile_bias_strategies/BBRSITV --timerange 20190101-20190401 --no-color
  ```
- `BBRSIoriginal`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/BBRSIoriginal-override-f400cf1f3448.json --strategy BBRSIoriginal --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSIoriginal --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSIoriginal --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BBRSIoriginal_gate.json --strategy BBRSIoriginal --strategy-path user_data/profile_bias_strategies/BBRSIoriginal --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BBRSIoriginal_startup_24.json --strategy BBRSIoriginal --strategy-path user_data/profile_bias_strategies/BBRSIoriginal --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `BBRSIv2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIv2 --strategy-path user_data/profile_bias_strategies/BBRSIv2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIv2 --strategy-path user_data/profile_bias_strategies/BBRSIv2 --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `BB_RPB_TSL_RNG`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_RNG_2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_2 --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_2 --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_2 --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_RNG_TBS`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_TBS --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_TBS --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_TBS --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_TBS --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_RNG_TBS_GOLD`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_TBS_GOLD --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_TBS_GOLD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_TBS_GOLD --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_TBS_GOLD --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_RNG_VWAP`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_VWAP --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_VWAP --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_VWAP --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_VWAP --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_c7c477d_20211030`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_c7c477d_20211030 --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_c7c477d_20211030 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BB_RPB_TSL_c7c477d_20211030_startup_288.json --strategy BB_RPB_TSL_c7c477d_20211030 --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_c7c477d_20211030-2ca1ddc5 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BB_RSI`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/BB_RSI-override-f400cf1f3448.json --strategy BB_RSI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_RSI --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BB_RSI_gate.json --strategy BB_RSI --strategy-path user_data/profile_bias_strategies/BB_RSI --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BB_RSI_startup_24.json --strategy BB_RSI --strategy-path user_data/profile_bias_strategies/BB_RSI --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `BB_RTR`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RTR --strategy-path user_data/profile_bias_strategies/BB_RTR --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RTR --strategy-path user_data/profile_bias_strategies/BB_RTR --timerange 20190101-20190401 --no-color
  ```
- `BB_Strategy04`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/BB_Strategy04-override-f400cf1f3448.json --strategy BB_Strategy04 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_Strategy04 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BB_Strategy04_gate.json --strategy BB_Strategy04 --strategy-path user_data/profile_bias_strategies/BB_Strategy04 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BB_Strategy04_startup_24.json --strategy BB_Strategy04 --strategy-path user_data/profile_bias_strategies/BB_Strategy04 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `BBands`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBands --strategy-path user_data/profile_bias_strategies/BBands --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBands --strategy-path user_data/profile_bias_strategies/BBands --timerange 20190101-20190401 --no-color
  ```
- `BBandsRSI`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBandsRSI --strategy-path user_data/profile_bias_strategies/BBandsRSI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBandsRSI --strategy-path user_data/profile_bias_strategies/BBandsRSI --timerange 20190101-20190401 --no-color
  ```
- `BBlower`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBlower --strategy-path user_data/profile_bias_strategies/BBlower --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBlower --strategy-path user_data/profile_bias_strategies/BBlower --timerange 20190101-20190401 --no-color
  ```
- `Babico_SMA5xBBmid`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Babico_SMA5xBBmid --strategy-path user_data/profile_bias_strategies/Babico_SMA5xBBmid --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Babico_SMA5xBBmid --strategy-path user_data/profile_bias_strategies/Babico_SMA5xBBmid --timerange 20190101-20190401 --no-color
  ```
- `Bandtastic`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Bandtastic --strategy-path user_data/profile_bias_strategies/Bandtastic --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Bandtastic --strategy-path user_data/profile_bias_strategies/Bandtastic --timerange 20190101-20190401 --no-color
  ```
- `BbRoi`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/BbRoi-override-c517447bf6b2.json --strategy BbRoi --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BbRoi --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BbRoi_gate.json --strategy BbRoi --strategy-path user_data/profile_bias_strategies/BbRoi --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BbRoi_startup_96.json --strategy BbRoi --strategy-path user_data/profile_bias_strategies/BbRoi --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880 --timeframe 15m
  ```
- `BbWidthExpansionStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbWidthExpansionStrategy --strategy-path user_data/profile_bias_strategies/BbWidthExpansionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BbWidthExpansionStrategy --strategy-path user_data/profile_bias_strategies/BbWidthExpansionStrategy --timerange 20190101-20190401 --no-color
  ```
- `BbandRsi`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsi --strategy-path user_data/profile_bias_strategies/BbandRsi --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BbandRsi_startup_1440.json --strategy BbandRsi --strategy-path user_data/profile_bias_strategies/BbandRsi-6dcf5b91 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BbandRsiRolling`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsiRolling --strategy-path user_data/profile_bias_strategies/BbandRsiRolling --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsiRolling --strategy-path user_data/profile_bias_strategies/BbandRsiRolling --timerange 20190101-20190401 --no-color
  ```
- `BigPete`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigPete --strategy-path repos/davidzr_freqtrade-strategies/strategies/BigPete --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigPete-b194f963 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigPete --strategy-path user_data/profile_bias_strategies/BigPete --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigPete --strategy-path user_data/profile_bias_strategies/BigPete --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigTrader`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigTrader --strategy-path user_data/profile_bias_strategies/BigTrader --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigTrader --strategy-path user_data/profile_bias_strategies/BigTrader --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ03`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03 --strategy-path user_data/profile_bias_strategies/BigZ03 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03 --strategy-path user_data/profile_bias_strategies/BigZ03 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ03HO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03HO --strategy-path user_data/profile_bias_strategies/BigZ03HO --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03HO --strategy-path user_data/profile_bias_strategies/BigZ03HO --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ04_TSL3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL3 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL3 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ04_TSL4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL4 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL4 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL4 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL4 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ07Next`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ07Next --strategy-path user_data/profile_bias_strategies/BigZ07Next --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ07Next --strategy-path user_data/profile_bias_strategies/BigZ07Next --timerange 20190101-20190401 --no-color
  ```
- `BigZ07Next2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ07Next2 --strategy-path user_data/profile_bias_strategies/BigZ07Next2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ07Next2 --strategy-path user_data/profile_bias_strategies/BigZ07Next2 --timerange 20190101-20190401 --no-color
  ```
- `BinClucMad`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMad --strategy-path user_data/profile_bias_strategies/BinClucMad --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMad --strategy-path user_data/profile_bias_strategies/BinClucMad --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BinClucMadV1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMadV1 --strategy-path user_data/profile_bias_strategies/BinClucMadV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMadV1 --strategy-path user_data/profile_bias_strategies/BinClucMadV1 --timerange 20190101-20190401 --no-color
  ```
- `BinHV27`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV27 --strategy-path user_data/profile_bias_strategies/BinHV27 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV27 --strategy-path user_data/profile_bias_strategies/BinHV27 --timerange 20190101-20190401 --no-color
  ```
- `BinHV27F`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long.json --strategy BinHV27F --strategy-path repos/eovie_freqtrade_strs/binance/Archive --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV27F --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy BinHV27F --strategy-path user_data/profile_bias_strategies/BinHV27F --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy BinHV27F --strategy-path user_data/profile_bias_strategies/BinHV27F --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `BinHV27_short`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy BinHV27_short --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV27_short --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BinHV27_short-15a8226e_gate.json --strategy BinHV27_short --strategy-path user_data/profile_bias_strategies/BinHV27_short-15a8226e --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy BinHV27_short --strategy-path user_data/profile_bias_strategies/BinHV27_short --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `BinHV27_werkkrew`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BinHV27_werkkrew --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV27_werkkrew-3a997e27 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BinHV27_werkkrew-3a997e27_gate.json --strategy BinHV27_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV27_werkkrew-3a997e27 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV27_werkkrew_startup_288.json --strategy BinHV27_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV27_werkkrew --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BinHV45`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45 --strategy-path user_data/profile_bias_strategies/BinHV45 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV45_startup_1440.json --strategy BinHV45 --strategy-path user_data/profile_bias_strategies/BinHV45 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BinHV45HO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45HO --strategy-path user_data/profile_bias_strategies/BinHV45HO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45HO --strategy-path user_data/profile_bias_strategies/BinHV45HO --timerange 20190101-20190401 --no-color
  ```
- `BinHV45_kanaxe`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_kanaxe --strategy-path user_data/profile_bias_strategies/BinHV45_kanaxe --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV45_kanaxe_startup_1440.json --strategy BinHV45_kanaxe --strategy-path user_data/profile_bias_strategies/BinHV45_kanaxe --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BinHV45_stash`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_stash --strategy-path user_data/profile_bias_strategies/BinHV45_stash --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV45_stash_startup_1440.json --strategy BinHV45_stash --strategy-path user_data/profile_bias_strategies/BinHV45_stash --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BinHV45_werkkrew`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV45_werkkrew --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV45_werkkrew_startup_1440.json --strategy BinHV45_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV45_werkkrew --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BinMfiBTCv5003`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinMfiBTCv5003 --strategy-path user_data/profile_bias_strategies/BinMfiBTCv5003 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinMfiBTCv5003 --strategy-path user_data/profile_bias_strategies/BinMfiBTCv5003 --timerange 20190101-20190401 --no-color
  ```
- `BollingerBandStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBandStrategy --strategy-path user_data/profile_bias_strategies/BollingerBandStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BollingerBandStrategy_startup_480.json --strategy BollingerBandStrategy --strategy-path user_data/profile_bias_strategies/BollingerBandStrategy --timerange 20190101-20190401 --no-color --startup-candle 480 960 3360
  ```
- `BollingerBounceStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBounceStrategy --strategy-path user_data/profile_bias_strategies/BollingerBounceStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBounceStrategy --strategy-path user_data/profile_bias_strategies/BollingerBounceStrategy --timerange 20190101-20190401 --no-color
  ```
- `BopTrendStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BopTrendStrategy --strategy-path user_data/profile_bias_strategies/BopTrendStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BopTrendStrategy --strategy-path user_data/profile_bias_strategies/BopTrendStrategy --timerange 20190101-20190401 --no-color
  ```
- `BullishEngulfingStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BullishEngulfingStrategy --strategy-path user_data/profile_bias_strategies/BullishEngulfingStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BullishEngulfingStrategy --strategy-path user_data/profile_bias_strategies/BullishEngulfingStrategy --timerange 20190101-20190401 --no-color
  ```
- `BuyOnly`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyOnly --strategy-path user_data/profile_bias_strategies/BuyOnly --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyOnly --strategy-path user_data/profile_bias_strategies/BuyOnly --timerange 20190101-20190401 --no-color
  ```
- `BuyOrDie`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyOrDie --strategy-path user_data/profile_bias_strategies/BuyOrDie --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyOrDie --strategy-path user_data/profile_bias_strategies/BuyOrDie --timerange 20190101-20190401 --no-color
  ```
- `BuyRegions`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyRegions --strategy-path user_data/profile_bias_strategies/BuyRegions --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyRegions --strategy-path user_data/profile_bias_strategies/BuyRegions-dff7fcd2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CBPete9`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CBPete9 --strategy-path repos/davidzr_freqtrade-strategies/strategies/CBPete9 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CBPete9-6ffadd4c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CBPete9 --strategy-path user_data/profile_bias_strategies/CBPete9 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CBPete9 --strategy-path user_data/profile_bias_strategies/CBPete9 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CCI_BB`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CCI_BB --strategy-path user_data/profile_bias_strategies/CCI_BB --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CCI_BB_startup_288.json --strategy CCI_BB --strategy-path user_data/profile_bias_strategies/CCI_BB --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CMCWinner`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CMCWinner --strategy-path user_data/profile_bias_strategies/CMCWinner --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CMCWinner --strategy-path user_data/profile_bias_strategies/CMCWinner --timerange 20190101-20190401 --no-color
  ```
- `CTIBS`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CTIBS --strategy-path user_data/profile_bias_strategies/CTIBS --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CTIBS --strategy-path user_data/profile_bias_strategies/CTIBS --timerange 20190101-20190401 --no-color
  ```
- `Candle2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Candle2 --strategy-path user_data/profile_bias_strategies/Candle2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Candle2 --strategy-path user_data/profile_bias_strategies/Candle2 --timerange 20190101-20190401 --no-color
  ```
- `CciMeanReversionStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CciMeanReversionStrategy --strategy-path user_data/profile_bias_strategies/CciMeanReversionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CciMeanReversionStrategy --strategy-path user_data/profile_bias_strategies/CciMeanReversionStrategy --timerange 20190101-20190401 --no-color
  ```
- `Cenderawasih_30m`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Cenderawasih_30m --strategy-path repos/TheoBrigitte_freqtrade/strategies/cenderawasih --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Cenderawasih_30m --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cenderawasih_30m --strategy-path user_data/profile_bias_strategies/Cenderawasih_30m --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cenderawasih_30m --strategy-path user_data/profile_bias_strategies/Cenderawasih_30m --timerange 20190101-20190401 --no-color --startup-candle 48 96 336 672 1440 4320
  ```
- `Cenderawasih_3_kucoin`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Cenderawasih_3_kucoin --strategy-path repos/TheoBrigitte_freqtrade/strategies/cenderawasih3 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Cenderawasih_3_kucoin --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cenderawasih_3_kucoin --strategy-path user_data/profile_bias_strategies/Cenderawasih_3_kucoin --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cenderawasih_3_kucoin --strategy-path user_data/profile_bias_strategies/Cenderawasih_3_kucoin --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ChaikinMoneyFlowStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ChaikinMoneyFlowStrategy --strategy-path user_data/profile_bias_strategies/ChaikinMoneyFlowStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ChaikinMoneyFlowStrategy --strategy-path user_data/profile_bias_strategies/ChaikinMoneyFlowStrategy --timerange 20190101-20190401 --no-color
  ```
- `Chandem`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Chandem --strategy-path user_data/profile_bias_strategies/Chandem --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Chandem --strategy-path user_data/profile_bias_strategies/Chandem --timerange 20190101-20190401 --no-color
  ```
- `Chandemtwo`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Chandemtwo --strategy-path user_data/profile_bias_strategies/Chandemtwo --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Chandemtwo --strategy-path user_data/profile_bias_strategies/Chandemtwo --timerange 20190101-20190401 --no-color
  ```
- `Chispei`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/Chispei-override-aa2053461232.json --strategy Chispei --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Chispei --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Chispei_gate.json --strategy Chispei --strategy-path user_data/profile_bias_strategies/Chispei --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Chispei_startup_6.json --strategy Chispei --strategy-path user_data/profile_bias_strategies/Chispei-62b19ed2 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190 --timeframe 4h
  ```
- `Cluc4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc4 --strategy-path user_data/profile_bias_strategies/Cluc4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc4 --strategy-path user_data/profile_bias_strategies/Cluc4 --timerange 20190101-20190401 --no-color
  ```
- `Cluc4werk`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc4werk --strategy-path user_data/profile_bias_strategies/Cluc4werk --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc4werk --strategy-path user_data/profile_bias_strategies/Cluc4werk --timerange 20190101-20190401 --no-color
  ```
- `Cluc5werk`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc5werk --strategy-path user_data/profile_bias_strategies/Cluc5werk --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc5werk --strategy-path user_data/profile_bias_strategies/Cluc5werk --timerange 20190101-20190401 --no-color
  ```
- `Cluc7werk`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc7werk --strategy-path user_data/profile_bias_strategies/Cluc7werk --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc7werk --strategy-path user_data/profile_bias_strategies/Cluc7werk --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `ClucFiatROI`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucFiatROI --strategy-path user_data/profile_bias_strategies/ClucFiatROI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucFiatROI --strategy-path user_data/profile_bias_strategies/ClucFiatROI --timerange 20190101-20190401 --no-color
  ```
- `ClucFiatSlow`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucFiatSlow --strategy-path user_data/profile_bias_strategies/ClucFiatSlow --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucFiatSlow --strategy-path user_data/profile_bias_strategies/ClucFiatSlow --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/ClucHAnix_gate.json --strategy ClucHAnix --strategy-path user_data/profile_bias_strategies/ClucHAnix --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix --strategy-path user_data/profile_bias_strategies/ClucHAnix --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5M_E0V1E`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_5m`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_5m1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m1 --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m1 --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_5m_old`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m_old --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m_old --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m_old --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m_old --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_BB_RPB`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucHAnix_BB_RPB --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_BB_RPB-d5edb88c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_BB_RPB --strategy-path user_data/profile_bias_strategies/ClucHAnix_BB_RPB --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_BB_RPB --strategy-path user_data/profile_bias_strategies/ClucHAnix_BB_RPB --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `ClucHAnix_BB_RPB_HO2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucHAnix_BB_RPB_HO2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_BB_RPB_HO2-50399031 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_BB_RPB_HO2 --strategy-path user_data/profile_bias_strategies/ClucHAnix_BB_RPB_HO2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_BB_RPB_HO2 --strategy-path user_data/profile_bias_strategies/ClucHAnix_BB_RPB_HO2 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `ClucHAnix_BB_RPB_MOD`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucHAnix_BB_RPB_MOD --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_BB_RPB_MOD-4949016b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_BB_RPB_MOD --strategy-path user_data/profile_bias_strategies/ClucHAnix_BB_RPB_MOD --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_BB_RPB_MOD --strategy-path user_data/profile_bias_strategies/ClucHAnix_BB_RPB_MOD --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `ClucHAnix_hhll`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_hhll --strategy-path user_data/profile_bias_strategies/ClucHAnix_hhll --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_hhll --strategy-path user_data/profile_bias_strategies/ClucHAnix_hhll --timerange 20190101-20190401 --no-color
  ```
- `ClucHAwerk`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAwerk --strategy-path user_data/profile_bias_strategies/ClucHAwerk --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAwerk --strategy-path user_data/profile_bias_strategies/ClucHAwerk --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `ClucMay72018`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucMay72018 --strategy-path user_data/profile_bias_strategies/ClucMay72018 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucMay72018 --strategy-path user_data/profile_bias_strategies/ClucMay72018 --timerange 20190101-20190401 --no-color
  ```
- `CofiBitStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CofiBitStrategy --strategy-path user_data/profile_bias_strategies/CofiBitStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CofiBitStrategy --strategy-path user_data/profile_bias_strategies/CofiBitStrategy --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndCluc`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndCluc2021`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc2021 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc2021 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc2021 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc2021 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndCluc2021Bull`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc2021Bull --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc2021Bull --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc2021Bull --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc2021Bull --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucHyper`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucHyper --strategy-path repos/TheoBrigitte_freqtrade/sources/sponsors --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucHyper-48a908dc --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyper --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyper --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyper --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyper --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `CombinedBinHAndClucHyperV0`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyperV0 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyperV0 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyperV0 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyperV0 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucHyperV3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyperV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyperV3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyperV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyperV3 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV2 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV2 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV2 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHAndClucV4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV4 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV4 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV4 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV5 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV5Hyperoptable`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV5Hyperoptable --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV5Hyperoptable --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV5Hyperoptable --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV5Hyperoptable --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV6`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV6 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV6 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHAndClucV7`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV7 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV7 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV7 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV7 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHAndClucV8`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV8Hyper`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8Hyper --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8Hyper --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8Hyper --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8Hyper --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV8XH`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8XH --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8XH --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8XH --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8XH --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV8XHO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8XHO --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8XHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8XHO --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8XHO --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHClucAndMADV5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV5 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV5 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHClucAndMADV6`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV6 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV6 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHClucAndMADV9`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV9 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV9 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV9 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV9 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Combined_Indicators`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_Indicators --strategy-path user_data/profile_bias_strategies/Combined_Indicators --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_Indicators --strategy-path user_data/profile_bias_strategies/Combined_Indicators --timerange 20190101-20190401 --no-color
  ```
- `Combined_NFIv6_SMA`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv6_SMA --strategy-path user_data/profile_bias_strategies/Combined_NFIv6_SMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv6_SMA --strategy-path user_data/profile_bias_strategies/Combined_NFIv6_SMA --timerange 20190101-20190401 --no-color
  ```
- `Combined_NFIv7_SMA`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv7_SMA --strategy-path user_data/profile_bias_strategies/Combined_NFIv7_SMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv7_SMA --strategy-path user_data/profile_bias_strategies/Combined_NFIv7_SMA --timerange 20190101-20190401 --no-color
  ```
- `Combined_NFIv7_SMA_Rallipanos_20210707`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv7_SMA_Rallipanos_20210707 --strategy-path user_data/profile_bias_strategies/Combined_NFIv7_SMA_Rallipanos_20210707 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv7_SMA_Rallipanos_20210707 --strategy-path user_data/profile_bias_strategies/Combined_NFIv7_SMA_Rallipanos_20210707 --timerange 20190101-20190401 --no-color
  ```
- `Combined_NFIv7_SMA_bAdBoY_20211204`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv7_SMA_bAdBoY_20211204 --strategy-path user_data/profile_bias_strategies/Combined_NFIv7_SMA_bAdBoY_20211204 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv7_SMA_bAdBoY_20211204 --strategy-path user_data/profile_bias_strategies/Combined_NFIv7_SMA_bAdBoY_20211204 --timerange 20190101-20190401 --no-color
  ```
- `CompositeScoreStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CompositeScoreStrategy --strategy-path user_data/profile_bias_strategies/CompositeScoreStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CompositeScoreStrategy --strategy-path user_data/profile_bias_strategies/CompositeScoreStrategy --timerange 20190101-20190401 --no-color
  ```
- `ConsensusShort`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy ConsensusShort --strategy-path repos/eovie_freqtrade_strs/binance/Archive --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ConsensusShort --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy ConsensusShort --strategy-path user_data/profile_bias_strategies/ConsensusShort --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy ConsensusShort --strategy-path user_data/profile_bias_strategies/ConsensusShort --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `CoppockCurveStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CoppockCurveStrategy --strategy-path user_data/profile_bias_strategies/CoppockCurveStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CoppockCurveStrategy --strategy-path user_data/profile_bias_strategies/CoppockCurveStrategy --timerange 20190101-20190401 --no-color
  ```
- `CrossEMAStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CrossEMAStrategy --strategy-path user_data/profile_bias_strategies/CrossEMAStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CrossEMAStrategy --strategy-path user_data/profile_bias_strategies/CrossEMAStrategy --timerange 20190101-20190401 --no-color
  ```
- `CryptoFrog`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrog --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrog --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrog_gate.json --strategy CryptoFrog --strategy-path user_data/profile_bias_strategies/CryptoFrog --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrog_startup_288.json --strategy CryptoFrog --strategy-path user_data/profile_bias_strategies/CryptoFrog --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogHO`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrogHO --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogHO --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogHO_gate.json --strategy CryptoFrogHO --strategy-path user_data/profile_bias_strategies/CryptoFrogHO --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrogHO_startup_288.json --strategy CryptoFrogHO --strategy-path user_data/profile_bias_strategies/CryptoFrogHO --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogHO2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrogHO2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogHO2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogHO2_gate.json --strategy CryptoFrogHO2 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrogHO2_startup_288.json --strategy CryptoFrogHO2 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogHO2A`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrogHO2A --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogHO2A --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogHO2A_gate.json --strategy CryptoFrogHO2A --strategy-path user_data/profile_bias_strategies/CryptoFrogHO2A --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrogHO2A_startup_288.json --strategy CryptoFrogHO2A --strategy-path user_data/profile_bias_strategies/CryptoFrogHO2A --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogHO3A1`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrogHO3A1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogHO3A1 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogHO3A1_gate.json --strategy CryptoFrogHO3A1 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO3A1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrogHO3A1_startup_288.json --strategy CryptoFrogHO3A1 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO3A1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogHO3A2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrogHO3A2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogHO3A2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogHO3A2_gate.json --strategy CryptoFrogHO3A2 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO3A2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrogHO3A2_startup_288.json --strategy CryptoFrogHO3A2 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO3A2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogHO3A3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrogHO3A3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogHO3A3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogHO3A3_gate.json --strategy CryptoFrogHO3A3 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO3A3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrogHO3A3_startup_288.json --strategy CryptoFrogHO3A3 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO3A3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogHO3A4`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrogHO3A4 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogHO3A4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogHO3A4_gate.json --strategy CryptoFrogHO3A4 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO3A4 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrogHO3A4_startup_288.json --strategy CryptoFrogHO3A4 --strategy-path user_data/profile_bias_strategies/CryptoFrogHO3A4 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogNFI`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CryptoFrogNFI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogNFI-08ea05db --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogNFI-08ea05db_gate.json --strategy CryptoFrogNFI --strategy-path user_data/profile_bias_strategies/CryptoFrogNFI-08ea05db --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CryptoFrogNFI --strategy-path user_data/profile_bias_strategies/CryptoFrogNFI --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogNFIHO1A`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CryptoFrogNFIHO1A --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogNFIHO1A-366468cd --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogNFIHO1A-366468cd_gate.json --strategy CryptoFrogNFIHO1A --strategy-path user_data/profile_bias_strategies/CryptoFrogNFIHO1A-366468cd --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CryptoFrogNFIHO1A --strategy-path user_data/profile_bias_strategies/CryptoFrogNFIHO1A --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrogOffset`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CryptoFrogOffset --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrogOffset-058d44a6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrogOffset-058d44a6_gate.json --strategy CryptoFrogOffset --strategy-path user_data/profile_bias_strategies/CryptoFrogOffset-058d44a6 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CryptoFrogOffset --strategy-path user_data/profile_bias_strategies/CryptoFrogOffset --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CryptoFrog_nateema`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy CryptoFrog_nateema --strategy-path repos/TheoBrigitte_freqtrade/strategies/cryptofrog-strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CryptoFrog_nateema --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/CryptoFrog_nateema_gate.json --strategy CryptoFrog_nateema --strategy-path user_data/profile_bias_strategies/CryptoFrog_nateema --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CryptoFrog_nateema_startup_288.json --strategy CryptoFrog_nateema --strategy-path user_data/profile_bias_strategies/CryptoFrog_nateema --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CustomStoplossWithPSAR`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CustomStoplossWithPSAR --strategy-path user_data/profile_bias_strategies/CustomStoplossWithPSAR --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CustomStoplossWithPSAR --strategy-path user_data/profile_bias_strategies/CustomStoplossWithPSAR --timerange 20190101-20190401 --no-color
  ```
- `DD`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy DD --strategy-path user_data/profile_bias_strategies/DD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy DD --strategy-path user_data/profile_bias_strategies/DD --timerange 20190101-20190401 --no-color
  ```
- `DWT_LongShort`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy DWT_LongShort --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DWT_LongShort --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy DWT_LongShort --strategy-path user_data/profile_bias_strategies/DWT_LongShort --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy DWT_LongShort --strategy-path user_data/profile_bias_strategies/DWT_LongShort --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `DWT_short`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy DWT_short --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DWT_short --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy DWT_short --strategy-path user_data/profile_bias_strategies/DWT_short --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy DWT_short --strategy-path user_data/profile_bias_strategies/DWT_short --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `DemaCrossStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy DemaCrossStrategy --strategy-path user_data/profile_bias_strategies/DemaCrossStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy DemaCrossStrategy --strategy-path user_data/profile_bias_strategies/DemaCrossStrategy --timerange 20190101-20190401 --no-color
  ```
- `Diamond`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Diamond --strategy-path user_data/profile_bias_strategies/Diamond --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Diamond --strategy-path user_data/profile_bias_strategies/Diamond --timerange 20190101-20190401 --no-color
  ```
- `Divergences`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Divergences --strategy-path user_data/profile_bias_strategies/Divergences --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Divergences --strategy-path user_data/profile_bias_strategies/Divergences --timerange 20190101-20190401 --no-color
  ```
- `DonchianBreakoutStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy DonchianBreakoutStrategy --strategy-path user_data/profile_bias_strategies/DonchianBreakoutStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy DonchianBreakoutStrategy --strategy-path user_data/profile_bias_strategies/DonchianBreakoutStrategy --timerange 20190101-20190401 --no-color
  ```
- `DoubleEMACrossoverWithTrend`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy DoubleEMACrossoverWithTrend --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies-that-work --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DoubleEMACrossoverWithTrend --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy DoubleEMACrossoverWithTrend --strategy-path user_data/profile_bias_strategies/DoubleEMACrossoverWithTrend --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/DoubleEMACrossoverWithTrend_startup_24.json --strategy DoubleEMACrossoverWithTrend --strategy-path user_data/profile_bias_strategies/DoubleEMACrossoverWithTrend-2df7ee08 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Dyna_opti`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Dyna_opti --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Dyna_opti-8aa17cbf --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Dyna_opti-8aa17cbf_gate.json --strategy Dyna_opti --strategy-path user_data/profile_bias_strategies/Dyna_opti-8aa17cbf --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Dyna_opti --strategy-path user_data/profile_bias_strategies/Dyna_opti --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `E0V1E`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E --strategy-path user_data/profile_bias_strategies/E0V1E --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E --strategy-path user_data/profile_bias_strategies/E0V1E --timerange 20190101-20190401 --no-color
  ```
- `E0V1E2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E2 --strategy-path user_data/profile_bias_strategies/E0V1E2 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E2 --strategy-path user_data/profile_bias_strategies/E0V1E2 --timerange 20190101-20190401 --no-color
  ```
- `E0V1EN`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy E0V1EN --strategy-path repos/eovie_freqtrade_strs/binance/dry_run --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1EN-dc02ef88 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1EN --strategy-path user_data/profile_bias_strategies/E0V1EN --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1EN --strategy-path user_data/profile_bias_strategies/E0V1EN --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `E0V1E_DCA3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_DCA3 --strategy-path user_data/profile_bias_strategies/E0V1E_DCA3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_DCA3 --strategy-path user_data/profile_bias_strategies/E0V1E_DCA3 --timerange 20190101-20190401 --no-color
  ```
- `E0V1E_ewo`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_ewo --strategy-path user_data/profile_bias_strategies/E0V1E_ewo --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_ewo --strategy-path user_data/profile_bias_strategies/E0V1E_ewo --timerange 20190101-20190401 --no-color
  ```
- `E0V1E_protections`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_protections --strategy-path user_data/profile_bias_strategies/E0V1E_protections --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_protections --strategy-path user_data/profile_bias_strategies/E0V1E_protections --timerange 20190101-20190401 --no-color
  ```
- `E0V1E_strs`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_strs --strategy-path user_data/profile_bias_strategies/E0V1E_strs --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_strs --strategy-path user_data/profile_bias_strategies/E0V1E_strs --timerange 20190101-20190401 --no-color
  ```
- `EI3v2_tag_cofi_green`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EI3v2_tag_cofi_green --strategy-path repos/MMR-19_freqtrade-strategies/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EI3v2_tag_cofi_green-c37315b6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EI3v2_tag_cofi_green --strategy-path user_data/profile_bias_strategies/EI3v2_tag_cofi_green --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EI3v2_tag_cofi_green --strategy-path user_data/profile_bias_strategies/EI3v2_tag_cofi_green --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `EMA50`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA50 --strategy-path user_data/profile_bias_strategies/EMA50 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA50 --strategy-path user_data/profile_bias_strategies/EMA50 --timerange 20190101-20190401 --no-color
  ```
- `EMA520015_V17`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA520015_V17 --strategy-path user_data/profile_bias_strategies/EMA520015_V17 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA520015_V17 --strategy-path user_data/profile_bias_strategies/EMA520015_V17 --timerange 20190101-20190401 --no-color
  ```
- `EMABBRSI`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/EMABBRSI-override-f400cf1f3448.json --strategy EMABBRSI --strategy-path repos/davidzr_freqtrade-strategies/strategies/EMABBRSI --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMABBRSI --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/EMABBRSI_gate.json --strategy EMABBRSI --strategy-path user_data/profile_bias_strategies/EMABBRSI --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EMABBRSI_startup_24.json --strategy EMABBRSI --strategy-path user_data/profile_bias_strategies/EMABBRSI --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `EMABreakout`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMABreakout --strategy-path user_data/profile_bias_strategies/EMABreakout --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMABreakout --strategy-path user_data/profile_bias_strategies/EMABreakout --timerange 20190101-20190401 --no-color
  ```
- `EMAPriceCrossoverWithThreshold`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy EMAPriceCrossoverWithThreshold --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies-that-work --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMAPriceCrossoverWithThreshold --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMAPriceCrossoverWithThreshold --strategy-path user_data/profile_bias_strategies/EMAPriceCrossoverWithThreshold --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EMAPriceCrossoverWithThreshold_startup_24.json --strategy EMAPriceCrossoverWithThreshold --strategy-path user_data/profile_bias_strategies/EMAPriceCrossoverWithThreshold-b7ab2a0f --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `EMASkipPump`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMASkipPump --strategy-path user_data/profile_bias_strategies/EMASkipPump --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMASkipPump --strategy-path user_data/profile_bias_strategies/EMASkipPump --timerange 20190101-20190401 --no-color
  ```
- `EMAVolume`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/EMAVolume-override-c517447bf6b2.json --strategy EMAVolume --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMAVolume --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/EMAVolume_gate.json --strategy EMAVolume --strategy-path user_data/profile_bias_strategies/EMAVolume --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EMAVolume_startup_96.json --strategy EMAVolume --strategy-path user_data/profile_bias_strategies/EMAVolume --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880 --timeframe 15m
  ```
- `EMA_CROSSOVER_STRATEGY`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA_CROSSOVER_STRATEGY --strategy-path user_data/profile_bias_strategies/EMA_CROSSOVER_STRATEGY --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA_CROSSOVER_STRATEGY --strategy-path user_data/profile_bias_strategies/EMA_CROSSOVER_STRATEGY --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `EMA_Trailing_Stoploss`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMA_Trailing_Stoploss --strategy-path repos/brookmiles_freqtrade-stuff/strategies/examples --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMA_Trailing_Stoploss-c357e7e7 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/EMA_Trailing_Stoploss-c357e7e7_gate.json --strategy EMA_Trailing_Stoploss --strategy-path user_data/profile_bias_strategies/EMA_Trailing_Stoploss-c357e7e7 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EMA_Trailing_Stoploss_startup_24.json --strategy EMA_Trailing_Stoploss --strategy-path user_data/profile_bias_strategies/EMA_Trailing_Stoploss-c357e7e7 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `EMA_Trailing_Stoploss_LessMagic`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMA_Trailing_Stoploss_LessMagic --strategy-path repos/brookmiles_freqtrade-stuff/strategies/examples --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMA_Trailing_Stoploss_LessMagic-aa2b302f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/EMA_Trailing_Stoploss_LessMagic-aa2b302f_gate.json --strategy EMA_Trailing_Stoploss_LessMagic --strategy-path user_data/profile_bias_strategies/EMA_Trailing_Stoploss_LessMagic-aa2b302f --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EMA_Trailing_Stoploss_LessMagic_startup_288.json --strategy EMA_Trailing_Stoploss_LessMagic --strategy-path user_data/profile_bias_strategies/EMA_Trailing_Stoploss_LessMagic-aa2b302f --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `EXPERIMENTAL_STRATEGY`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/EXPERIMENTAL_STRATEGY-override-2c7527d808c6.json --strategy EXPERIMENTAL_STRATEGY --strategy-path repos/davidzr_freqtrade-strategies/strategies/EXPERIMENTAL_STRATEGY --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EXPERIMENTAL_STRATEGY --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/EXPERIMENTAL_STRATEGY_gate.json --strategy EXPERIMENTAL_STRATEGY --strategy-path user_data/profile_bias_strategies/EXPERIMENTAL_STRATEGY --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EXPERIMENTAL_STRATEGY_startup_288.json --strategy EXPERIMENTAL_STRATEGY --strategy-path user_data/profile_bias_strategies/EXPERIMENTAL_STRATEGY --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `EasyInEasyOut`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EasyInEasyOut --strategy-path user_data/profile_bias_strategies/EasyInEasyOut --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EasyInEasyOut --strategy-path user_data/profile_bias_strategies/EasyInEasyOut --timerange 20190101-20190401 --no-color
  ```
- `ElliotV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV2 --strategy-path user_data/profile_bias_strategies/ElliotV2 --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV2 --strategy-path user_data/profile_bias_strategies/ElliotV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ElliotV4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV4 --strategy-path user_data/profile_bias_strategies/ElliotV4 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV4 --strategy-path user_data/profile_bias_strategies/ElliotV4 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV531`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV531 --strategy-path user_data/profile_bias_strategies/ElliotV531 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV531 --strategy-path user_data/profile_bias_strategies/ElliotV531 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5HO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HO --strategy-path user_data/profile_bias_strategies/ElliotV5HO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HO --strategy-path user_data/profile_bias_strategies/ElliotV5HO --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5HOMod2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HOMod2 --strategy-path user_data/profile_bias_strategies/ElliotV5HOMod2 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HOMod2 --strategy-path user_data/profile_bias_strategies/ElliotV5HOMod2 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5HOMod3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HOMod3 --strategy-path user_data/profile_bias_strategies/ElliotV5HOMod3 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HOMod3 --strategy-path user_data/profile_bias_strategies/ElliotV5HOMod3 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5_SMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5_SMA --strategy-path user_data/profile_bias_strategies/ElliotV5_SMA --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5_SMA --strategy-path user_data/profile_bias_strategies/ElliotV5_SMA --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ElliotV7`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV7 --strategy-path user_data/profile_bias_strategies/ElliotV7 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV7 --strategy-path user_data/profile_bias_strategies/ElliotV7 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV8HO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8HO --strategy-path user_data/profile_bias_strategies/ElliotV8HO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8HO --strategy-path user_data/profile_bias_strategies/ElliotV8HO --timerange 20190101-20190401 --no-color
  ```
- `ElliotV8_original`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV8_original --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV8_original --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV8_original-ce2403f2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8_original --strategy-path user_data/profile_bias_strategies/ElliotV8_original --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8_original --strategy-path user_data/profile_bias_strategies/ElliotV8_original --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ElliotV8_original_ichiv2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV8_original_ichiv2 --strategy-path repos/TheoBrigitte_freqtrade/strategies/eliot --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV8_original_ichiv2-3c67badc --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8_original_ichiv2 --strategy-path user_data/profile_bias_strategies/ElliotV8_original_ichiv2 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8_original_ichiv2 --strategy-path user_data/profile_bias_strategies/ElliotV8_original_ichiv2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ElliotV8_original_ichiv2OH`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV8_original_ichiv2OH --strategy-path repos/TheoBrigitte_freqtrade/strategies/eliot --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV8_original_ichiv2OH-a45e937f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8_original_ichiv2OH --strategy-path user_data/profile_bias_strategies/ElliotV8_original_ichiv2OH --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8_original_ichiv2OH --strategy-path user_data/profile_bias_strategies/ElliotV8_original_ichiv2OH --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ElliotV8_original_ichiv3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV8_original_ichiv3 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV8_original_ichiv3-433ffe91 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8_original_ichiv3 --strategy-path user_data/profile_bias_strategies/ElliotV8_original_ichiv3 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV8_original_ichiv3 --strategy-path user_data/profile_bias_strategies/ElliotV8_original_ichiv3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Elliotv8`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Elliotv8 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Elliotv8-bdc3ea5b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Elliotv8 --strategy-path user_data/profile_bias_strategies/Elliotv8 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Elliotv8 --strategy-path user_data/profile_bias_strategies/Elliotv8 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `EmaRibbonStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EmaRibbonStrategy --strategy-path user_data/profile_bias_strategies/EmaRibbonStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EmaRibbonStrategy --strategy-path user_data/profile_bias_strategies/EmaRibbonStrategy --timerange 20190101-20190401 --no-color
  ```
- `FAdxSmaStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FAdxSmaStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path user_data/profile_bias_strategies/FAdxSmaStrategy --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FAdxSmaStrategy --strategy-path user_data/profile_bias_strategies/FAdxSmaStrategy --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FOttStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FOttStrategy --strategy-path user_data/profile_repairs --timerange 20200301-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FOttStrategy --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FOttStrategy --strategy-path user_data/profile_bias_strategies/FOttStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FOttStrategy --strategy-path user_data/profile_bias_strategies/FOttStrategy --timerange 20200301-20200401 --no-color
  ```
- `FRAYSTRAT`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FRAYSTRAT --strategy-path user_data/profile_bias_strategies/FRAYSTRAT --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FRAYSTRAT --strategy-path user_data/profile_bias_strategies/FRAYSTRAT --timerange 20190101-20190401 --no-color
  ```
- `FReinforcedStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FReinforcedStrategy --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FReinforcedStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FReinforcedStrategy --strategy-path user_data/profile_bias_strategies/FReinforcedStrategy --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FReinforcedStrategy --strategy-path user_data/profile_bias_strategies/FReinforcedStrategy --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `FSampleStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FSampleStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FSampleStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FSampleStrategy --strategy-path user_data/profile_bias_strategies/FSampleStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FSampleStrategy --strategy-path user_data/profile_bias_strategies/FSampleStrategy --timerange 20200301-20200401 --no-color
  ```
- `FSupertrendStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long.json --strategy FSupertrendStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FSupertrendStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long.json --strategy FSupertrendStrategy --strategy-path user_data/profile_bias_strategies/FSupertrendStrategy --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FSupertrendStrategy --strategy-path user_data/profile_bias_strategies/FSupertrendStrategy --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FTT_DWT_FBB_FUTURES`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FTT_DWT_FBB_FUTURES --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FTT_DWT_FBB_FUTURES --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FTT_DWT_FBB_FUTURES --strategy-path user_data/profile_bias_strategies/FTT_DWT_FBB_FUTURES --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FTT_DWT_FBB_FUTURES --strategy-path user_data/profile_bias_strategies/FTT_DWT_FBB_FUTURES --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `FVGChannel`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FVGChannel --strategy-path user_data/profile_bias_strategies/FVGChannel --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FVGChannel --strategy-path user_data/profile_bias_strategies/FVGChannel --timerange 20190101-20190401 --no-color
  ```
- `Fakebuy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Fakebuy --strategy-path user_data/profile_bias_strategies/Fakebuy --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Fakebuy --strategy-path user_data/profile_bias_strategies/Fakebuy-d1b272c1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `FastSupertrend_optim3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_gate.json --strategy FastSupertrend_optim3 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim3_rsi_70`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3_rsi_70 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3_rsi_70 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_rsi_70_gate.json --strategy FastSupertrend_optim3_rsi_70 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_70 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3_rsi_70 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_70 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim3_rsi_75`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3_rsi_75 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3_rsi_75 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_rsi_75_gate.json --strategy FastSupertrend_optim3_rsi_75 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3_rsi_75 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim3_rsi_752`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3_rsi_752 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3_rsi_752 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_rsi_752_gate.json --strategy FastSupertrend_optim3_rsi_752 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_752 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3_rsi_752 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_752 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim3_rsi_75fix`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3_rsi_75fix --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3_rsi_75fix --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_rsi_75fix_gate.json --strategy FastSupertrend_optim3_rsi_75fix --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75fix --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3_rsi_75fix --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75fix --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim3_rsi_75fix_signal`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3_rsi_75fix_signal --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3_rsi_75fix_signal --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_rsi_75fix_signal_gate.json --strategy FastSupertrend_optim3_rsi_75fix_signal --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75fix_signal --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3_rsi_75fix_signal --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75fix_signal --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim3_rsi_75lev`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3_rsi_75lev --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3_rsi_75lev --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_rsi_75lev_gate.json --strategy FastSupertrend_optim3_rsi_75lev --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75lev --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3_rsi_75lev --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75lev --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim3_rsi_75sell`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3_rsi_75sell --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3_rsi_75sell --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_rsi_75sell_gate.json --strategy FastSupertrend_optim3_rsi_75sell --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75sell --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3_rsi_75sell --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_75sell --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim3_rsi_80`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim3_rsi_80 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim3_rsi_80 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim3_rsi_80_gate.json --strategy FastSupertrend_optim3_rsi_80 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_80 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim3_rsi_80 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim3_rsi_80 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim_quick`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim_quick --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim_quick --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim_quick_gate.json --strategy FastSupertrend_optim_quick --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim_quick --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim_quick2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim_quick2 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim_quick2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim_quick2_gate.json --strategy FastSupertrend_optim_quick2 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick2 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim_quick2 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick2 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim_quick3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim_quick3 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim_quick3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim_quick3_gate.json --strategy FastSupertrend_optim_quick3 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick3 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim_quick3 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick3 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim_quick4`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim_quick4 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim_quick4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim_quick4_gate.json --strategy FastSupertrend_optim_quick4 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick4 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim_quick4 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick4 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_optim_quick5`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_optim_quick5 --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_optim_quick5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/FastSupertrend_optim_quick5_gate.json --strategy FastSupertrend_optim_quick5 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick5 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_optim_quick5 --strategy-path user_data/profile_bias_strategies/FastSupertrend_optim_quick5 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FastSupertrend_ts_origstop_fix`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_ts_origstop_fix --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_bias_strategies/FastSupertrend_ts_origstop_fix --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_bias_strategies/FastSupertrend_ts_origstop_fix --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FisherHull`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FisherHull --strategy-path user_data/profile_bias_strategies/FisherHull --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FisherHull --strategy-path user_data/profile_bias_strategies/FisherHull --timerange 20190101-20190401 --no-color
  ```
- `FisherTransformStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FisherTransformStrategy --strategy-path user_data/profile_bias_strategies/FisherTransformStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FisherTransformStrategy --strategy-path user_data/profile_bias_strategies/FisherTransformStrategy --timerange 20190101-20190401 --no-color
  ```
- `FiveMinCrossAbove`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FiveMinCrossAbove --strategy-path user_data/profile_bias_strategies/FiveMinCrossAbove --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FiveMinCrossAbove --strategy-path user_data/profile_bias_strategies/FiveMinCrossAbove --timerange 20190101-20190401 --no-color
  ```
- `FlawlessVictory`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FlawlessVictory --strategy-path user_data/profile_bias_strategies/FlawlessVictory --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FlawlessVictory --strategy-path user_data/profile_bias_strategies/FlawlessVictory --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `ForexSignal`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ForexSignal --strategy-path user_data/profile_bias_strategies/ForexSignal --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ForexSignal --strategy-path user_data/profile_bias_strategies/ForexSignal --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `FrayStratBTC`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrayStratBTC --strategy-path user_data/profile_bias_strategies/FrayStratBTC --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrayStratBTC --strategy-path user_data/profile_bias_strategies/FrayStratBTC --timerange 20190101-20190401 --no-color
  ```
- `Freqtrade_backtest_validation_freqtrade1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Freqtrade_backtest_validation_freqtrade1 --strategy-path user_data/profile_bias_strategies/Freqtrade_backtest_validation_freqtrade1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Freqtrade_backtest_validation_freqtrade1 --strategy-path user_data/profile_bias_strategies/Freqtrade_backtest_validation_freqtrade1 --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM115mStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM115mStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM115mStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM115mStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM115mStrategy --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM11hStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM11hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM11hStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM11hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM11hStrategy --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM21hStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM21hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM21hStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM21hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM21hStrategy --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM315mStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM315mStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM315mStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM315mStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM315mStrategy --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM31hStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM31hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM31hStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM31hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM31hStrategy --timerange 20190101-20190401 --no-color
  ```
- `GKD_Baseline`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_Baseline --strategy-path user_data/profile_bias_strategies/GKD_Baseline --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_Baseline --strategy-path user_data/profile_bias_strategies/GKD_Baseline --timerange 20190101-20190401 --no-color
  ```
- `GKD_BaselineAllMAs`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_BaselineAllMAs --strategy-path user_data/profile_bias_strategies/GKD_BaselineAllMAs --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_BaselineAllMAs --strategy-path user_data/profile_bias_strategies/GKD_BaselineAllMAs --timerange 20190101-20190401 --no-color
  ```
- `GKD_FisherTransformMTF`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/GKD_FisherTransformMTF_gate.json --strategy GKD_FisherTransformMTF --strategy-path user_data/profile_bias_strategies/GKD_FisherTransformMTF --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_FisherTransformMTF --strategy-path user_data/profile_bias_strategies/GKD_FisherTransformMTF --timerange 20190101-20190401 --no-color
  ```
- `GKD_HurstExponent`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_HurstExponent --strategy-path user_data/profile_bias_strategies/GKD_HurstExponent --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_HurstExponent --strategy-path user_data/profile_bias_strategies/GKD_HurstExponent --timerange 20190101-20190401 --no-color
  ```
- `GKD_PFE`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_PFE --strategy-path user_data/profile_bias_strategies/GKD_PFE --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_PFE --strategy-path user_data/profile_bias_strategies/GKD_PFE --timerange 20190101-20190401 --no-color
  ```
- `GPTREV`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GPTREV --strategy-path user_data/profile_bias_strategies/GPTREV --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GPTREV --strategy-path user_data/profile_bias_strategies/GPTREV --timerange 20190101-20190401 --no-color
  ```
- `GodCard`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GodCard --strategy-path user_data/profile_bias_strategies/GodCard --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GodCard --strategy-path user_data/profile_bias_strategies/GodCard --timerange 20190101-20190401 --no-color
  ```
- `GoldenCrossStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GoldenCrossStrategy --strategy-path user_data/profile_bias_strategies/GoldenCrossStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GoldenCrossStrategy --strategy-path user_data/profile_bias_strategies/GoldenCrossStrategy --timerange 20190101-20190401 --no-color
  ```
- `Gumbo1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Gumbo1 --strategy-path user_data/profile_bias_strategies/Gumbo1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Gumbo1 --strategy-path user_data/profile_bias_strategies/Gumbo1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Hacklemore`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy Hacklemore --strategy-path repos/werkkrew_freqtrade-strategies/strategies/archived --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Hacklemore --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Hacklemore_gate.json --strategy Hacklemore --strategy-path user_data/profile_bias_strategies/Hacklemore --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemore --strategy-path user_data/profile_bias_strategies/Hacklemore --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Hacklemore2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Hacklemore2_gate.json --strategy Hacklemore2 --strategy-path user_data/profile_bias_strategies/Hacklemore2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemore2 --strategy-path user_data/profile_bias_strategies/Hacklemore2 --timerange 20190101-20190401 --no-color
  ```
- `Hacklemore3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Hacklemore3_gate.json --strategy Hacklemore3 --strategy-path user_data/profile_bias_strategies/Hacklemore3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemore3 --strategy-path user_data/profile_bias_strategies/Hacklemore3 --timerange 20190101-20190401 --no-color
  ```
- `Hacklemost`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemost --strategy-path user_data/profile_bias_strategies/Hacklemost --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemost --strategy-path user_data/profile_bias_strategies/Hacklemost --timerange 20190101-20190401 --no-color
  ```
- `HansenSmaOffsetV1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HansenSmaOffsetV1 --strategy-path user_data/profile_bias_strategies/HansenSmaOffsetV1 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HansenSmaOffsetV1 --strategy-path user_data/profile_bias_strategies/HansenSmaOffsetV1 --timerange 20190101-20190401 --no-color
  ```
- `HeikinAshiStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HeikinAshiStrategy --strategy-path user_data/profile_bias_strategies/HeikinAshiStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HeikinAshiStrategy --strategy-path user_data/profile_bias_strategies/HeikinAshiStrategy --timerange 20190101-20190401 --no-color
  ```
- `HigherHighStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HigherHighStrategy --strategy-path user_data/profile_bias_strategies/HigherHighStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HigherHighStrategy --strategy-path user_data/profile_bias_strategies/HigherHighStrategy --timerange 20190101-20190401 --no-color
  ```
- `HilbertSineWave`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HilbertSineWave --strategy-path user_data/profile_bias_strategies/HilbertSineWave --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HilbertSineWave --strategy-path user_data/profile_bias_strategies/HilbertSineWave --timerange 20190101-20190401 --no-color
  ```
- `HourBasedStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HourBasedStrategy --strategy-path user_data/profile_bias_strategies/HourBasedStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HourBasedStrategy --strategy-path user_data/profile_bias_strategies/HourBasedStrategy --timerange 20190101-20190401 --no-color
  ```
- `HourBasedStrategy_5m`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HourBasedStrategy_5m --strategy-path user_data/profile_bias_strategies/HourBasedStrategy_5m --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/HourBasedStrategy_5m_startup_288.json --strategy HourBasedStrategy_5m --strategy-path user_data/profile_bias_strategies/HourBasedStrategy_5m --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `INSIDEUP`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/INSIDEUP_gate.json --strategy INSIDEUP --strategy-path user_data/profile_bias_strategies/INSIDEUP --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy INSIDEUP --strategy-path user_data/profile_bias_strategies/INSIDEUP --timerange 20190101-20190401 --no-color
  ```
- `Ichess`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichess --strategy-path user_data/profile_bias_strategies/Ichess --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichess --strategy-path user_data/profile_bias_strategies/Ichess --timerange 20190101-20190401 --no-color
  ```
- `Ichimoku`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku --strategy-path user_data/profile_bias_strategies/Ichimoku --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku --strategy-path user_data/profile_bias_strategies/Ichimoku --timerange 20190101-20190401 --no-color
  ```
- `IchimokuCloudStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy IchimokuCloudStrategy --strategy-path user_data/profile_bias_strategies/IchimokuCloudStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy IchimokuCloudStrategy --strategy-path user_data/profile_bias_strategies/IchimokuCloudStrategy-eede6bf0 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `IchimokuSimpleStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy IchimokuSimpleStrategy --strategy-path user_data/profile_bias_strategies/IchimokuSimpleStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy IchimokuSimpleStrategy --strategy-path user_data/profile_bias_strategies/IchimokuSimpleStrategy --timerange 20190101-20190401 --no-color
  ```
- `IchimokuStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/IchimokuStrategy-67b217c6-override-1e59e7a90fc3.json --strategy IchimokuStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/IchimokuStrategy-67b217c6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/IchimokuStrategy-67b217c6_gate.json --strategy IchimokuStrategy --strategy-path user_data/profile_bias_strategies/IchimokuStrategy-67b217c6 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/IchimokuStrategy_startup_480.json --strategy IchimokuStrategy --strategy-path user_data/profile_bias_strategies/IchimokuStrategy-67b217c6 --timerange 20190101-20190401 --no-color --startup-candle 480 960 3360 --timeframe 3m
  ```
- `Ichimoku_SenkouSpanCross`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/Ichimoku_SenkouSpanCross-d71627c7-override-aa2053461232.json --strategy Ichimoku_SenkouSpanCross --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichimoku_SenkouSpanCross-d71627c7 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Ichimoku_SenkouSpanCross-d71627c7_gate.json --strategy Ichimoku_SenkouSpanCross --strategy-path user_data/profile_bias_strategies/Ichimoku_SenkouSpanCross-d71627c7 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Ichimoku_SenkouSpanCross_startup_6.json --strategy Ichimoku_SenkouSpanCross --strategy-path user_data/profile_bias_strategies/Ichimoku_SenkouSpanCross-d71627c7 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190 --timeframe 4h
  ```
- `Ichimoku_v12`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/Ichimoku_v12-override-aa2053461232.json --strategy Ichimoku_v12 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichimoku_v12 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Ichimoku_v12_gate.json --strategy Ichimoku_v12 --strategy-path user_data/profile_bias_strategies/Ichimoku_v12 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Ichimoku_v12_startup_6.json --strategy Ichimoku_v12 --strategy-path user_data/profile_bias_strategies/Ichimoku_v12 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 --timeframe 4h
  ```
- `Ichimoku_v30`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/Ichimoku_v30-override-aa2053461232.json --strategy Ichimoku_v30 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichimoku_v30 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Ichimoku_v30_gate.json --strategy Ichimoku_v30 --strategy-path user_data/profile_bias_strategies/Ichimoku_v30 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Ichimoku_v30_startup_6.json --strategy Ichimoku_v30 --strategy-path user_data/profile_bias_strategies/Ichimoku_v30 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 --timeframe 4h
  ```
- `Ichimoku_v31`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v31 --strategy-path user_data/profile_bias_strategies/Ichimoku_v31 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v31 --strategy-path user_data/profile_bias_strategies/Ichimoku_v31 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Ichimoku_v32`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/Ichimoku_v32-override-aa2053461232.json --strategy Ichimoku_v32 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichimoku_v32 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Ichimoku_v32_gate.json --strategy Ichimoku_v32 --strategy-path user_data/profile_bias_strategies/Ichimoku_v32 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Ichimoku_v32_startup_6.json --strategy Ichimoku_v32 --strategy-path user_data/profile_bias_strategies/Ichimoku_v32 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 --timeframe 4h
  ```
- `Ichimoku_v33`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/Ichimoku_v33-override-aa2053461232.json --strategy Ichimoku_v33 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichimoku_v33 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Ichimoku_v33_gate.json --strategy Ichimoku_v33 --strategy-path user_data/profile_bias_strategies/Ichimoku_v33 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Ichimoku_v33_startup_6.json --strategy Ichimoku_v33 --strategy-path user_data/profile_bias_strategies/Ichimoku_v33 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 --timeframe 4h
  ```
- `Ichimoku_v37`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v37 --strategy-path user_data/profile_bias_strategies/Ichimoku_v37 --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v37 --strategy-path user_data/profile_bias_strategies/Ichimoku_v37 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540
  ```
- `ImpulseV1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ImpulseV1 --strategy-path user_data/profile_bias_strategies/ImpulseV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ImpulseV1 --strategy-path user_data/profile_bias_strategies/ImpulseV1 --timerange 20190101-20190401 --no-color
  ```
- `InformativeSample`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy InformativeSample --strategy-path user_data/profile_bias_strategies/InformativeSample --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy InformativeSample --strategy-path user_data/profile_bias_strategies/InformativeSample --timerange 20190101-20190401 --no-color
  ```
- `Inverse`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Inverse --strategy-path user_data/profile_bias_strategies/Inverse --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Inverse --strategy-path user_data/profile_bias_strategies/Inverse --timerange 20190101-20190401 --no-color
  ```
- `InverseV2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy InverseV2 --strategy-path user_data/profile_bias_strategies/InverseV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy InverseV2 --strategy-path user_data/profile_bias_strategies/InverseV2 --timerange 20190101-20190401 --no-color
  ```
- `JuicyTrend`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy JuicyTrend --strategy-path user_data/profile_bias_strategies/JuicyTrend --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy JuicyTrend --strategy-path user_data/profile_bias_strategies/JuicyTrend --timerange 20190101-20190401 --no-color
  ```
- `JustROCR`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/JustROCR-override-f400cf1f3448.json --strategy JustROCR --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/JustROCR --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/JustROCR_gate.json --strategy JustROCR --strategy-path user_data/profile_bias_strategies/JustROCR --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/JustROCR_startup_24.json --strategy JustROCR --strategy-path user_data/profile_bias_strategies/JustROCR --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `JustROCR2`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/JustROCR2-override-2c7527d808c6.json --strategy JustROCR2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/JustROCR2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/JustROCR2_gate.json --strategy JustROCR2 --strategy-path user_data/profile_bias_strategies/JustROCR2 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/JustROCR2_startup_288.json --strategy JustROCR2 --strategy-path user_data/profile_bias_strategies/JustROCR2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `JustROCR3`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/JustROCR3-override-2c7527d808c6.json --strategy JustROCR3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/JustROCR3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/JustROCR3_gate.json --strategy JustROCR3 --strategy-path user_data/profile_bias_strategies/JustROCR3 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/JustROCR3_startup_288.json --strategy JustROCR3 --strategy-path user_data/profile_bias_strategies/JustROCR3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `JustROCR4`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/JustROCR4-override-2c7527d808c6.json --strategy JustROCR4 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/JustROCR4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/JustROCR4_gate.json --strategy JustROCR4 --strategy-path user_data/profile_bias_strategies/JustROCR4 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/JustROCR4_startup_288.json --strategy JustROCR4 --strategy-path user_data/profile_bias_strategies/JustROCR4 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `JustROCR5`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/JustROCR5-override-93c76024faa3.json --strategy JustROCR5 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/JustROCR5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/JustROCR5_gate.json --strategy JustROCR5 --strategy-path user_data/profile_bias_strategies/JustROCR5 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/JustROCR5_startup_1440.json --strategy JustROCR5 --strategy-path user_data/profile_bias_strategies/JustROCR5 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880 --timeframe 1m
  ```
- `JustROCR6`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy JustROCR6 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/JustROCR6 --cache none --timeframe 1m --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/JustROCR6_gate.json --strategy JustROCR6 --strategy-path user_data/profile_bias_strategies/JustROCR6 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/JustROCR6_startup_1440.json --strategy JustROCR6 --strategy-path user_data/profile_bias_strategies/JustROCR6 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880 --timeframe 1m
  ```
- `KAMACCIRSI`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI --strategy-path user_data/profile_bias_strategies/KAMACCIRSI --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI --strategy-path user_data/profile_bias_strategies/KAMACCIRSI --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `KAMACCIRSI_new`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI_new --strategy-path user_data/profile_bias_strategies/KAMACCIRSI_new --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI_new --strategy-path user_data/profile_bias_strategies/KAMACCIRSI_new --timerange 20190101-20190401 --no-color
  ```
- `KC_BB`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KC_BB --strategy-path user_data/profile_bias_strategies/KC_BB --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KC_BB --strategy-path user_data/profile_bias_strategies/KC_BB --timerange 20190101-20190401 --no-color
  ```
- `KeltnerChannelStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KeltnerChannelStrategy --strategy-path user_data/profile_bias_strategies/KeltnerChannelStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KeltnerChannelStrategy --strategy-path user_data/profile_bias_strategies/KeltnerChannelStrategy --timerange 20190101-20190401 --no-color
  ```
- `Lateralus`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Lateralus_gate.json --strategy Lateralus --strategy-path user_data/profile_bias_strategies/Lateralus --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Lateralus --strategy-path user_data/profile_bias_strategies/Lateralus --timerange 20190101-20190401 --no-color
  ```
- `LinearRegressionStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy LinearRegressionStrategy --strategy-path user_data/profile_bias_strategies/LinearRegressionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy LinearRegressionStrategy --strategy-path user_data/profile_bias_strategies/LinearRegressionStrategy --timerange 20190101-20190401 --no-color
  ```
- `Low_BB`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Low_BB_gate.json --strategy Low_BB --strategy-path user_data/profile_bias_strategies/Low_BB --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Low_BB --strategy-path user_data/profile_bias_strategies/Low_BB --timerange 20190101-20190401 --no-color
  ```
- `LuxOSC`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy LuxOSC --strategy-path user_data/profile_bias_strategies/LuxOSC --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy LuxOSC --strategy-path user_data/profile_bias_strategies/LuxOSC --timerange 20190101-20190401 --no-color
  ```
- `MAC`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MAC --strategy-path user_data/profile_bias_strategies/MAC --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MAC --strategy-path user_data/profile_bias_strategies/MAC --timerange 20190101-20190401 --no-color
  ```
- `MACD9fall`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACD9fall --strategy-path repos/shadowp2810_technical_indicators_cryptos/Freqtrade/ft_userdata/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACD9fall-3ef1c8d0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MACD9fall-3ef1c8d0_gate.json --strategy MACD9fall --strategy-path user_data/profile_bias_strategies/MACD9fall-3ef1c8d0 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD9fall --strategy-path user_data/profile_bias_strategies/MACD9fall-3ef1c8d0 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `MACDCCI`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/MACDCCI-override-87e303112603.json --strategy MACDCCI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDCCI --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MACDCCI_gate.json --strategy MACDCCI --strategy-path user_data/profile_bias_strategies/MACDCCI --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MACDCCI_startup_48.json --strategy MACDCCI --strategy-path user_data/profile_bias_strategies/MACDCCI --timerange 20190101-20190401 --no-color --startup-candle 48 96 336 672 1440 4320 --timeframe 30m
  ```
- `MACDCrossoverWithTrend`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy MACDCrossoverWithTrend --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies-that-work --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDCrossoverWithTrend --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDCrossoverWithTrend --strategy-path user_data/profile_bias_strategies/MACDCrossoverWithTrend --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MACDCrossoverWithTrend_startup_24.json --strategy MACDCrossoverWithTrend --strategy-path user_data/profile_bias_strategies/MACDCrossoverWithTrend-b6e682ec --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `MACDRL`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long.json --strategy MACDRL --strategy-path repos/MelvynClark_Freqtrade-Strategy/MACDR --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDRL --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long.json --strategy MACDRL --strategy-path user_data/profile_bias_strategies/MACDRL --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MACDRL_startup_288.json --strategy MACDRL --strategy-path user_data/profile_bias_strategies/MACDRL --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `MACDRS`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy MACDRS --strategy-path repos/MelvynClark_Freqtrade-Strategy/MACDR --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDRS --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy MACDRS --strategy-path user_data/profile_bias_strategies/MACDRS --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MACDRS_startup_288.json --strategy MACDRS --strategy-path user_data/profile_bias_strategies/MACDRS --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `MACDRSI200`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/MACDRSI200-override-2c7527d808c6.json --strategy MACDRSI200 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDRSI200 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MACDRSI200_gate.json --strategy MACDRSI200 --strategy-path user_data/profile_bias_strategies/MACDRSI200 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MACDRSI200_startup_288.json --strategy MACDRSI200 --strategy-path user_data/profile_bias_strategies/MACDRSI200 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `MACDStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategy --strategy-path user_data/profile_bias_strategies/MACDStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MACDStrategy_startup_288.json --strategy MACDStrategy --strategy-path user_data/profile_bias_strategies/MACDStrategy-79bd402e --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MACDStrategyADA`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyADA --strategy-path user_data/profile_bias_strategies/MACDStrategyADA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyADA --strategy-path user_data/profile_bias_strategies/MACDStrategyADA --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyAVAX`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyAVAX --strategy-path user_data/profile_bias_strategies/MACDStrategyAVAX --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyAVAX --strategy-path user_data/profile_bias_strategies/MACDStrategyAVAX --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyBTC`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyBTC --strategy-path user_data/profile_bias_strategies/MACDStrategyBTC --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyBTC --strategy-path user_data/profile_bias_strategies/MACDStrategyBTC --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyENJ`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyENJ --strategy-path user_data/profile_bias_strategies/MACDStrategyENJ --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyENJ --strategy-path user_data/profile_bias_strategies/MACDStrategyENJ --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyETC`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyETC --strategy-path user_data/profile_bias_strategies/MACDStrategyETC --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyETC --strategy-path user_data/profile_bias_strategies/MACDStrategyETC --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategySOL`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategySOL --strategy-path user_data/profile_bias_strategies/MACDStrategySOL --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategySOL --strategy-path user_data/profile_bias_strategies/MACDStrategySOL --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyXRP`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyXRP --strategy-path user_data/profile_bias_strategies/MACDStrategyXRP --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyXRP --strategy-path user_data/profile_bias_strategies/MACDStrategyXRP --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategy_crossed`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategy_crossed --strategy-path user_data/profile_bias_strategies/MACDStrategy_crossed --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategy_crossed --strategy-path user_data/profile_bias_strategies/MACDStrategy_crossed --timerange 20190101-20190401 --no-color
  ```
- `MACDZeroCrossStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDZeroCrossStrategy --strategy-path user_data/profile_bias_strategies/MACDZeroCrossStrategy --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDZeroCrossStrategy --strategy-path user_data/profile_bias_strategies/MACDZeroCrossStrategy --timerange 20190101-20190401 --no-color
  ```
- `MACD_EMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_EMA --strategy-path user_data/profile_bias_strategies/MACD_EMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_EMA --strategy-path user_data/profile_bias_strategies/MACD_EMA --timerange 20190101-20190401 --no-color
  ```
- `MACD_TRIPLE_MA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRIPLE_MA --strategy-path user_data/profile_bias_strategies/MACD_TRIPLE_MA --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRIPLE_MA --strategy-path user_data/profile_bias_strategies/MACD_TRIPLE_MA --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MACD_TRI_EMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRI_EMA --strategy-path user_data/profile_bias_strategies/MACD_TRI_EMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRI_EMA --strategy-path user_data/profile_bias_strategies/MACD_TRI_EMA --timerange 20190101-20190401 --no-color
  ```
- `MADisplaceV3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MADisplaceV3 --strategy-path user_data/profile_bias_strategies/MADisplaceV3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MADisplaceV3 --strategy-path user_data/profile_bias_strategies/MADisplaceV3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MFI`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MFI --strategy-path user_data/profile_bias_strategies/MFI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MFI --strategy-path user_data/profile_bias_strategies/MFI --timerange 20190101-20190401 --no-color
  ```
- `MabStra`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MabStra --strategy-path user_data/profile_bias_strategies/MabStra --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MabStra_startup_6.json --strategy MabStra --strategy-path user_data/profile_bias_strategies/MabStra-43fd2626 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `MacdAdxStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdAdxStrategy --strategy-path user_data/profile_bias_strategies/MacdAdxStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdAdxStrategy --strategy-path user_data/profile_bias_strategies/MacdAdxStrategy --timerange 20190101-20190401 --no-color
  ```
- `MacdZeroCrossStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdZeroCrossStrategy --strategy-path user_data/profile_bias_strategies/MacdZeroCrossStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdZeroCrossStrategy --strategy-path user_data/profile_bias_strategies/MacdZeroCrossStrategy-4830233c --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MacheteV8b`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MacheteV8b --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MacheteV8b-b42642cf --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MacheteV8b-b42642cf_gate.json --strategy MacheteV8b --strategy-path user_data/profile_bias_strategies/MacheteV8b-b42642cf --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacheteV8b --strategy-path user_data/profile_bias_strategies/MacheteV8b --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `MacheteV8bRallimod`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MacheteV8bRallimod --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MacheteV8bRallimod-019087a6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MacheteV8bRallimod-019087a6_gate.json --strategy MacheteV8bRallimod --strategy-path user_data/profile_bias_strategies/MacheteV8bRallimod-019087a6 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacheteV8bRallimod --strategy-path user_data/profile_bias_strategies/MacheteV8bRallimod --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `MacheteV8bRallimod2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MacheteV8bRallimod2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MacheteV8bRallimod2-2a221533 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MacheteV8bRallimod2-2a221533_gate.json --strategy MacheteV8bRallimod2 --strategy-path user_data/profile_bias_strategies/MacheteV8bRallimod2-2a221533 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacheteV8bRallimod2 --strategy-path user_data/profile_bias_strategies/MacheteV8bRallimod2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Magic_Trailing_Stoploss`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Magic_Trailing_Stoploss --strategy-path repos/brookmiles_freqtrade-stuff/strategies/examples --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Magic_Trailing_Stoploss-1cf71129 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Magic_Trailing_Stoploss-1cf71129_gate.json --strategy Magic_Trailing_Stoploss --strategy-path user_data/profile_bias_strategies/Magic_Trailing_Stoploss-1cf71129 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Magic_Trailing_Stoploss_startup_24.json --strategy Magic_Trailing_Stoploss --strategy-path user_data/profile_bias_strategies/Magic_Trailing_Stoploss-1cf71129 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `MarketChyperHyperStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MarketChyperHyperStrategy --strategy-path user_data/profile_bias_strategies/MarketChyperHyperStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MarketChyperHyperStrategy --strategy-path user_data/profile_bias_strategies/MarketChyperHyperStrategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Maro4hMacdSd`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Maro4hMacdSd --strategy-path user_data/profile_bias_strategies/Maro4hMacdSd --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Maro4hMacdSd --strategy-path user_data/profile_bias_strategies/Maro4hMacdSd --timerange 20190101-20190401 --no-color
  ```
- `Martin`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Martin --strategy-path user_data/profile_bias_strategies/Martin --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Martin --strategy-path user_data/profile_bias_strategies/Martin --timerange 20190101-20190401 --no-color
  ```
- `MiniLambo`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MiniLambo --strategy-path user_data/profile_bias_strategies/MiniLambo --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MiniLambo --strategy-path user_data/profile_bias_strategies/MiniLambo --timerange 20190101-20190401 --no-color
  ```
- `Minmax`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Minmax --strategy-path user_data/profile_bias_strategies/Minmax --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Minmax --strategy-path user_data/profile_bias_strategies/Minmax --timerange 20190101-20190401 --no-color
  ```
- `MomStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MomStrategy --strategy-path user_data/profile_bias_strategies/MomStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MomStrategy --strategy-path user_data/profile_bias_strategies/MomStrategy --timerange 20190101-20190401 --no-color
  ```
- `MomentumScoreStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MomentumScoreStrategy --strategy-path user_data/profile_bias_strategies/MomentumScoreStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MomentumScoreStrategy --strategy-path user_data/profile_bias_strategies/MomentumScoreStrategy --timerange 20190101-20190401 --no-color
  ```
- `Momentumv2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Momentumv2 --strategy-path user_data/profile_bias_strategies/Momentumv2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Momentumv2 --strategy-path user_data/profile_bias_strategies/Momentumv2 --timerange 20190101-20190401 --no-color
  ```
- `MoneyFlowStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MoneyFlowStrategy --strategy-path user_data/profile_bias_strategies/MoneyFlowStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MoneyFlowStrategy --strategy-path user_data/profile_bias_strategies/MoneyFlowStrategy --timerange 20190101-20190401 --no-color
  ```
- `MontrealStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MontrealStrategy --strategy-path user_data/profile_bias_strategies/MontrealStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MontrealStrategy --strategy-path user_data/profile_bias_strategies/MontrealStrategy --timerange 20190101-20190401 --no-color
  ```
- `MultiFactorConfluenceStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiFactorConfluenceStrategy --strategy-path user_data/profile_bias_strategies/MultiFactorConfluenceStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiFactorConfluenceStrategy --strategy-path user_data/profile_bias_strategies/MultiFactorConfluenceStrategy --timerange 20190101-20190401 --no-color
  ```
- `MultiMA_TSL`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MultiMA_TSL --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiMA_TSL-432f3842 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MultiMA_TSL-432f3842_gate.json --strategy MultiMA_TSL --strategy-path user_data/profile_bias_strategies/MultiMA_TSL-432f3842 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL --strategy-path user_data/profile_bias_strategies/MultiMA_TSL --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MultiMA_TSL3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy MultiMA_TSL3 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiMA_TSL3 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL3 --strategy-path user_data/profile_bias_strategies/MultiMA_TSL3 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL3 --strategy-path user_data/profile_bias_strategies/MultiMA_TSL3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MultiMA_TSL3_Mod`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy MultiMA_TSL3_Mod --strategy-path repair/patched/repos/davidzr_freqtrade-strategies/strategies/MultiMA_TSL3_Mod --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiMA_TSL3_Mod --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL3_Mod --strategy-path user_data/profile_bias_strategies/MultiMA_TSL3_Mod --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL3_Mod --strategy-path user_data/profile_bias_strategies/MultiMA_TSL3_Mod --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MultiOffsetLamboV0`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiOffsetLamboV0 --strategy-path user_data/profile_bias_strategies/MultiOffsetLamboV0 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiOffsetLamboV0 --strategy-path user_data/profile_bias_strategies/MultiOffsetLamboV0 --timerange 20190101-20190401 --no-color
  ```
- `MultiRSI`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy MultiRSI --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiRSI --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiRSI --strategy-path user_data/profile_bias_strategies/MultiRSI --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MultiRSI_startup_288.json --strategy MultiRSI --strategy-path user_data/profile_bias_strategies/MultiRSI --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MyStratV1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MyStratV1 --strategy-path user_data/profile_bias_strategies/MyStratV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MyStratV1 --strategy-path user_data/profile_bias_strategies/MyStratV1 --timerange 20190101-20190401 --no-color
  ```
- `NASOSRv6_private_Reinuvader_20211121`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NASOSRv6_private_Reinuvader_20211121 --strategy-path repair/patched/repos/ShahAnuj2610_my-freqtrade/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSRv6_private_Reinuvader_20211121 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NASOSRv6_private_Reinuvader_20211121_gate.json --strategy NASOSRv6_private_Reinuvader_20211121 --strategy-path user_data/profile_bias_strategies/NASOSRv6_private_Reinuvader_20211121 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSRv6_private_Reinuvader_20211121 --strategy-path user_data/profile_bias_strategies/NASOSRv6_private_Reinuvader_20211121 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NASOSv4`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NASOSv4 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv4-d420d31d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NASOSv4_gate.json --strategy NASOSv4 --strategy-path user_data/profile_bias_strategies/NASOSv4 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv4 --strategy-path user_data/profile_bias_strategies/NASOSv4 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NASOSv5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NASOSv5_gate.json --strategy NASOSv5 --strategy-path user_data/profile_bias_strategies/NASOSv5 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5 --strategy-path user_data/profile_bias_strategies/NASOSv5 --timerange 20190101-20190401 --no-color
  ```
- `NASOSv5_mod1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NASOSv5_mod1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5_mod1-dc29bda0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NASOSv5_mod1_gate.json --strategy NASOSv5_mod1 --strategy-path user_data/profile_bias_strategies/NASOSv5_mod1 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5_mod1 --strategy-path user_data/profile_bias_strategies/NASOSv5_mod1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NASOSv5_mod1_DanMod`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NASOSv5_mod1_DanMod --strategy-path repos/davidzr_freqtrade-strategies/strategies/NASOSv5_mod1_DanMod --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5_mod1_DanMod-8ccd7243 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NASOSv5_mod1_DanMod_gate.json --strategy NASOSv5_mod1_DanMod --strategy-path user_data/profile_bias_strategies/NASOSv5_mod1_DanMod --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5_mod1_DanMod --strategy-path user_data/profile_bias_strategies/NASOSv5_mod1_DanMod --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NASOSv5_mod2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NASOSv5_mod2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5_mod2-215c0845 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NASOSv5_mod2_gate.json --strategy NASOSv5_mod2 --strategy-path user_data/profile_bias_strategies/NASOSv5_mod2 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5_mod2 --strategy-path user_data/profile_bias_strategies/NASOSv5_mod2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NASOSv5_mod3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NASOSv5_mod3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5_mod3-2ce3e304 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NASOSv5_mod3_gate.json --strategy NASOSv5_mod3 --strategy-path user_data/profile_bias_strategies/NASOSv5_mod3 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5_mod3 --strategy-path user_data/profile_bias_strategies/NASOSv5_mod3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NEWTEST15m`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NEWTEST15m --strategy-path user_data/profile_bias_strategies/NEWTEST15m --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NEWTEST15m --strategy-path user_data/profile_bias_strategies/NEWTEST15m --timerange 20190101-20190401 --no-color
  ```
- `NFI46`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46 --strategy-path user_data/profile_bias_strategies/NFI46 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46 --strategy-path user_data/profile_bias_strategies/NFI46 --timerange 20190101-20190401 --no-color
  ```
- `NFI46Frog`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI46Frog --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI46Frog-c5debb17 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NFI46Frog-c5debb17_gate.json --strategy NFI46Frog --strategy-path user_data/profile_bias_strategies/NFI46Frog-c5debb17 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Frog --strategy-path user_data/profile_bias_strategies/NFI46Frog --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NFI46FrogZ`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46FrogZ --strategy-path user_data/profile_bias_strategies/NFI46FrogZ --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46FrogZ --strategy-path user_data/profile_bias_strategies/NFI46FrogZ --timerange 20190101-20190401 --no-color
  ```
- `NFI46Offset`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Offset --strategy-path user_data/profile_bias_strategies/NFI46Offset --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Offset --strategy-path user_data/profile_bias_strategies/NFI46Offset --timerange 20190101-20190401 --no-color
  ```
- `NFI46OffsetHOA1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46OffsetHOA1 --strategy-path user_data/profile_bias_strategies/NFI46OffsetHOA1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46OffsetHOA1 --strategy-path user_data/profile_bias_strategies/NFI46OffsetHOA1 --timerange 20190101-20190401 --no-color
  ```
- `NFI46Z`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Z --strategy-path user_data/profile_bias_strategies/NFI46Z --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Z --strategy-path user_data/profile_bias_strategies/NFI46Z --timerange 20190101-20190401 --no-color
  ```
- `NFI47V2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI47V2 --strategy-path user_data/profile_bias_strategies/NFI47V2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI47V2 --strategy-path user_data/profile_bias_strategies/NFI47V2 --timerange 20190101-20190401 --no-color
  ```
- `NFI4Frog`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI4Frog --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI4Frog-a1f40e4d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NFI4Frog-a1f40e4d_gate.json --strategy NFI4Frog --strategy-path user_data/profile_bias_strategies/NFI4Frog-a1f40e4d --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI4Frog --strategy-path user_data/profile_bias_strategies/NFI4Frog --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NFI5MOHO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO --strategy-path user_data/profile_bias_strategies/NFI5MOHO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO --strategy-path user_data/profile_bias_strategies/NFI5MOHO --timerange 20190101-20190401 --no-color
  ```
- `NFI5MOHO2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO2 --strategy-path user_data/profile_bias_strategies/NFI5MOHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO2 --strategy-path user_data/profile_bias_strategies/NFI5MOHO2 --timerange 20190101-20190401 --no-color
  ```
- `NFI5MOHO_WIP`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP --timerange 20190101-20190401 --no-color
  ```
- `NFI5MOHO_WIP_1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP_1 --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP_1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP_1 --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP_1 --timerange 20190101-20190401 --no-color
  ```
- `NFI5MOHO_WIP_2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP_2 --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP_2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP_2 --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP_2 --timerange 20190101-20190401 --no-color
  ```
- `NFI731_BUSD`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NFI731_BUSD --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI731_BUSD --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI731_BUSD --strategy-path user_data/profile_bias_strategies/NFI731_BUSD --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI731_BUSD --strategy-path user_data/profile_bias_strategies/NFI731_BUSD --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NFI7MOHO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI7MOHO --strategy-path user_data/profile_bias_strategies/NFI7MOHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI7MOHO --strategy-path user_data/profile_bias_strategies/NFI7MOHO --timerange 20190101-20190401 --no-color
  ```
- `NFINextMOHO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMOHO --strategy-path user_data/profile_bias_strategies/NFINextMOHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMOHO --strategy-path user_data/profile_bias_strategies/NFINextMOHO --timerange 20190101-20190401 --no-color
  ```
- `NFINextMOHO2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMOHO2 --strategy-path user_data/profile_bias_strategies/NFINextMOHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMOHO2 --strategy-path user_data/profile_bias_strategies/NFINextMOHO2 --timerange 20190101-20190401 --no-color
  ```
- `NFINextMultiOffsetAndHO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMultiOffsetAndHO --strategy-path user_data/profile_bias_strategies/NFINextMultiOffsetAndHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMultiOffsetAndHO --strategy-path user_data/profile_bias_strategies/NFINextMultiOffsetAndHO --timerange 20190101-20190401 --no-color
  ```
- `NFINextMultiOffsetAndHO2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMultiOffsetAndHO2 --strategy-path user_data/profile_bias_strategies/NFINextMultiOffsetAndHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMultiOffsetAndHO2 --strategy-path user_data/profile_bias_strategies/NFINextMultiOffsetAndHO2 --timerange 20190101-20190401 --no-color
  ```
- `NFIX_BB_RPB`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NFIX_BB_RPB --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFIX_BB_RPB --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NFIX_BB_RPB_gate.json --strategy NFIX_BB_RPB --strategy-path user_data/profile_bias_strategies/NFIX_BB_RPB --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFIX_BB_RPB --strategy-path user_data/profile_bias_strategies/NFIX_BB_RPB --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NFIX_BB_RPB_c7c477d_20211030`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NFIX_BB_RPB_c7c477d_20211030 --strategy-path repair/patched/repos/davidzr_freqtrade-strategies/strategies/NFIX_BB_RPB_c7c477d_20211030 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFIX_BB_RPB_c7c477d_20211030 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NFIX_BB_RPB_c7c477d_20211030_gate.json --strategy NFIX_BB_RPB_c7c477d_20211030 --strategy-path user_data/profile_bias_strategies/NFIX_BB_RPB_c7c477d_20211030 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFIX_BB_RPB_c7c477d_20211030 --strategy-path user_data/profile_bias_strategies/NFIX_BB_RPB_c7c477d_20211030 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NWEv6_new`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NWEv6_new --strategy-path user_data/profile_bias_strategies/NWEv6_new --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NWEv6_new --strategy-path user_data/profile_bias_strategies/NWEv6_new --timerange 20190101-20190401 --no-color --startup-candle 480 960 3360
  ```
- `NfiNextModded`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NfiNextModded --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NfiNextModded --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NfiNextModded --strategy-path user_data/profile_bias_strategies/NfiNextModded --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NfiNextModded --strategy-path user_data/profile_bias_strategies/NfiNextModded-94125b64 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NormalizerStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NormalizerStrategy --strategy-path user_data/profile_bias_strategies/NormalizerStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NormalizerStrategy --strategy-path user_data/profile_bias_strategies/NormalizerStrategy --timerange 20190101-20190401 --no-color
  ```
- `NormalizerStrategyHO2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NormalizerStrategyHO2 --strategy-path user_data/profile_bias_strategies/NormalizerStrategyHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NormalizerStrategyHO2 --strategy-path user_data/profile_bias_strategies/NormalizerStrategyHO2 --timerange 20190101-20190401 --no-color
  ```
- `Nostalgia`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Nostalgia --strategy-path user_data/profile_bias_strategies/Nostalgia --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Nostalgia --strategy-path user_data/profile_bias_strategies/Nostalgia --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinity772martinsk3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinity772martinsk3 --strategy-path repair/patched/repos/TheoBrigitte_freqtrade/strategies/nfix --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinity772martinsk3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NostalgiaForInfinity772martinsk3_gate.json --strategy NostalgiaForInfinity772martinsk3 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinity772martinsk3 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinity772martinsk3 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinity772martinsk3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityNext`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityNext --strategy-path repair/patched/repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNext --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext-b808c258 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityNext772`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityNext772 --strategy-path repair/patched/repos/TheoBrigitte_freqtrade/sources/nfix --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNext772 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext772 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext772 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext772 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext772-8d6ca7f0 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityNextGen`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextGen --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextGen --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextGen --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextGen --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityNextGen_TSL`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextGen_TSL --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextGen_TSL --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextGen_TSL --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextGen_TSL --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityNextV7155`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityNextV7155 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNextV7155 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextV7155 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextV7155 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextV7155 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextV7155-fd1e8353 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityNext_maximizer`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityNext_maximizer --strategy-path repair/patched/repos/davidzr_freqtrade-strategies/strategies/NostalgiaForInfinityNext_maximizer --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNext_maximizer --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext_maximizer --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext_maximizer --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext_maximizer --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext_maximizer-78e1c6b3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityV1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV1 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV1 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityV3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV3 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV3 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV3 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV4 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV4 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV4 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV4HO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV4HO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV4HO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV4HO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV4HO --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV5MultiOffsetAndHO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5MultiOffsetAndHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5MultiOffsetAndHO --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV5MultiOffsetAndHO2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5MultiOffsetAndHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5MultiOffsetAndHO2 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV6`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV6 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV6 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV6 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV6 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV6HO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV6HO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV6HO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV6HO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV6HO --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV7`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV7_7_2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityV7_7_2 --strategy-path repair/patched/repos/davidzr_freqtrade-strategies/strategies/NostalgiaForInfinityV7_7_2 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV7_7_2 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_7_2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_7_2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_7_2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_7_2-19436abd --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityV7_SMA`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_SMA --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_SMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_SMA --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_SMA --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV7_SMAv2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_SMAv2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_SMAv2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_SMAv2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_SMAv2 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV7_SMAv2_1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_SMAv2_1 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_SMAv2_1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_SMAv2_1 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_SMAv2_1 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityX`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityX --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityX --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NostalgiaForInfinityX_gate.json --strategy NostalgiaForInfinityX --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityX --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityX --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityX --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NotAnotherSMAOffsetStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NotAnotherSMAOffsetStrategy_gate.json --strategy NotAnotherSMAOffsetStrategy --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategy --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategy --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyHO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NotAnotherSMAOffsetStrategyHO_gate.json --strategy NotAnotherSMAOffsetStrategyHO --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyHO --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyHO --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyHOv3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NotAnotherSMAOffsetStrategyHOv3_gate.json --strategy NotAnotherSMAOffsetStrategyHOv3 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyHOv3 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyHOv3 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyHOv3 --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyLite`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyLite --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyLite --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyLite --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyLite --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyModHO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyModHO --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyModHO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyModHO --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyModHO --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyX1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NotAnotherSMAOffsetStrategyX1_gate.json --strategy NotAnotherSMAOffsetStrategyX1 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyX1 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyX1 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyX1 --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategy_uzi`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategy_uzi --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategy_uzi --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategy_uzi --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategy_uzi --timerange 20190101-20190401 --no-color
  ```
- `NowoIchimoku1hV2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NowoIchimoku1hV2 --strategy-path user_data/profile_bias_strategies/NowoIchimoku1hV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NowoIchimoku1hV2 --strategy-path user_data/profile_bias_strategies/NowoIchimoku1hV2 --timerange 20190101-20190401 --no-color
  ```
- `NowoIchimoku5mV2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NowoIchimoku5mV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NowoIchimoku5mV2 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NowoIchimoku5mV2 --strategy-path user_data/profile_bias_strategies/NowoIchimoku5mV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NowoIchimoku5mV2 --strategy-path user_data/profile_bias_strategies/NowoIchimoku5mV2 --timerange 20190101-20190401 --no-color
  ```
- `ONUR`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ONUR --strategy-path user_data/profile_bias_strategies/ONUR --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ONUR --strategy-path user_data/profile_bias_strategies/ONUR --timerange 20190101-20190401 --no-color
  ```
- `ObeliskIM_v1_1`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy ObeliskIM_v1_1 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ObeliskIM_v1_1 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ObeliskIM_v1_1 --strategy-path user_data/profile_bias_strategies/ObeliskIM_v1_1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ObeliskIM_v1_1 --strategy-path user_data/profile_bias_strategies/ObeliskIM_v1_1 --timerange 20190101-20190401 --no-color
  ```
- `ObeliskRSI_v6_1`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy ObeliskRSI_v6_1 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ObeliskRSI_v6_1 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ObeliskRSI_v6_1 --strategy-path user_data/profile_bias_strategies/ObeliskRSI_v6_1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ObeliskRSI_v6_1 --strategy-path user_data/profile_bias_strategies/ObeliskRSI_v6_1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Obelisk_Ichimoku_Slow_v1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Obelisk_Ichimoku_Slow_v1 --strategy-path repos/brookmiles_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1-933691c1 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Obelisk_Ichimoku_Slow_v1-933691c1_gate.json --strategy Obelisk_Ichimoku_Slow_v1 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_Slow_v1-933691c1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_Ichimoku_Slow_v1 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_Slow_v1-933691c1 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Obelisk_Ichimoku_Slow_v1_1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Obelisk_Ichimoku_Slow_v1_1 --strategy-path repos/brookmiles_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1_1-877a1601 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Obelisk_Ichimoku_Slow_v1_1-877a1601_gate.json --strategy Obelisk_Ichimoku_Slow_v1_1 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_Slow_v1_1-877a1601 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_Ichimoku_Slow_v1_1 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_Slow_v1_1-877a1601 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Obelisk_Ichimoku_Slow_v1_2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Obelisk_Ichimoku_Slow_v1_2 --strategy-path repos/brookmiles_freqtrade-stuff/strategies/archive --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1_2-fe861e17 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Obelisk_Ichimoku_Slow_v1_2-fe861e17_gate.json --strategy Obelisk_Ichimoku_Slow_v1_2 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_Slow_v1_2-fe861e17 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_Ichimoku_Slow_v1_2 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_Slow_v1_2-fe861e17 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Obelisk_Ichimoku_Slow_v1_3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy Obelisk_Ichimoku_Slow_v1_3 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1_3 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_Ichimoku_Slow_v1_3 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_Slow_v1_3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_Ichimoku_Slow_v1_3 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_Slow_v1_3-0482a784 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Obelisk_Ichimoku_ZEMA_v1`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy Obelisk_Ichimoku_ZEMA_v1 --strategy-path repair/patched/repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_Ichimoku_ZEMA_v1 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_Ichimoku_ZEMA_v1 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_ZEMA_v1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_Ichimoku_ZEMA_v1 --strategy-path user_data/profile_bias_strategies/Obelisk_Ichimoku_ZEMA_v1-7b2ec464 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Obelisk_TradePro_Ichi_v1_1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_TradePro_Ichi_v1_1 --strategy-path user_data/profile_bias_strategies/Obelisk_TradePro_Ichi_v1_1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_TradePro_Ichi_v1_1 --strategy-path user_data/profile_bias_strategies/Obelisk_TradePro_Ichi_v1_1-d9ad6391 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Obelisk_TradePro_Ichi_v2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Obelisk_TradePro_Ichi_v2 --strategy-path repos/brookmiles_freqtrade-stuff/strategies/archive --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_TradePro_Ichi_v2-c9b4a814 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Obelisk_TradePro_Ichi_v2-c9b4a814_gate.json --strategy Obelisk_TradePro_Ichi_v2 --strategy-path user_data/profile_bias_strategies/Obelisk_TradePro_Ichi_v2-c9b4a814 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_TradePro_Ichi_v2 --strategy-path user_data/profile_bias_strategies/Obelisk_TradePro_Ichi_v2-c9b4a814 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Obelisk_TradePro_Ichi_v2_1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_TradePro_Ichi_v2_1 --strategy-path user_data/profile_bias_strategies/Obelisk_TradePro_Ichi_v2_1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_TradePro_Ichi_v2_1 --strategy-path user_data/profile_bias_strategies/Obelisk_TradePro_Ichi_v2_1-b409b943 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Obelisk_TradePro_Ichi_v2_2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Obelisk_TradePro_Ichi_v2_2 --strategy-path repos/brookmiles_freqtrade-stuff/strategies/archive --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_TradePro_Ichi_v2_2-596055ad --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Obelisk_TradePro_Ichi_v2_2-596055ad_gate.json --strategy Obelisk_TradePro_Ichi_v2_2 --strategy-path user_data/profile_bias_strategies/Obelisk_TradePro_Ichi_v2_2-596055ad --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Obelisk_TradePro_Ichi_v2_2 --strategy-path user_data/profile_bias_strategies/Obelisk_TradePro_Ichi_v2_2-596055ad --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `OmaGann`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy OmaGann --strategy-path user_data/profile_bias_strategies/OmaGann --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy OmaGann --strategy-path user_data/profile_bias_strategies/OmaGann --timerange 20190101-20190401 --no-color
  ```
- `OversoldReversion`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy OversoldReversion --strategy-path repos/nateemma_strategies/Reversion --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/OversoldReversion-dcb09e33 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/OversoldReversion-dcb09e33_gate.json --strategy OversoldReversion --strategy-path user_data/profile_bias_strategies/OversoldReversion-dcb09e33 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy OversoldReversion --strategy-path user_data/profile_bias_strategies/OversoldReversion-dcb09e33 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `PRICEFOLLOWING`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PRICEFOLLOWING --strategy-path user_data/profile_bias_strategies/PRICEFOLLOWING --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PRICEFOLLOWING --strategy-path user_data/profile_bias_strategies/PRICEFOLLOWING --timerange 20190101-20190401 --no-color
  ```
- `PRICEFOLLOWINGX`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PRICEFOLLOWINGX --strategy-path user_data/profile_bias_strategies/PRICEFOLLOWINGX --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PRICEFOLLOWINGX --strategy-path user_data/profile_bias_strategies/PRICEFOLLOWINGX --timerange 20190101-20190401 --no-color
  ```
- `ParabolicSarStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ParabolicSarStrategy --strategy-path user_data/profile_bias_strategies/ParabolicSarStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ParabolicSarStrategy --strategy-path user_data/profile_bias_strategies/ParabolicSarStrategy --timerange 20190101-20190401 --no-color
  ```
- `Persia`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Persia --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Persia-f2f6ac3e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Persia-f2f6ac3e_gate.json --strategy Persia --strategy-path user_data/profile_bias_strategies/Persia-f2f6ac3e --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Persia_startup_288.json --strategy Persia --strategy-path user_data/profile_bias_strategies/Persia-f2f6ac3e --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `PowerTower`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PowerTower --strategy-path user_data/profile_bias_strategies/PowerTower --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PowerTower --strategy-path user_data/profile_bias_strategies/PowerTower --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `PpoMomentumStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PpoMomentumStrategy --strategy-path user_data/profile_bias_strategies/PpoMomentumStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PpoMomentumStrategy --strategy-path user_data/profile_bias_strategies/PpoMomentumStrategy --timerange 20190101-20190401 --no-color
  ```
- `PriceActionCandleStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PriceActionCandleStrategy --strategy-path user_data/profile_bias_strategies/PriceActionCandleStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PriceActionCandleStrategy --strategy-path user_data/profile_bias_strategies/PriceActionCandleStrategy --timerange 20190101-20190401 --no-color
  ```
- `PriceChannelStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PriceChannelStrategy --strategy-path user_data/profile_bias_strategies/PriceChannelStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PriceChannelStrategy --strategy-path user_data/profile_bias_strategies/PriceChannelStrategy --timerange 20190101-20190401 --no-color
  ```
- `PumpDetector`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PumpDetector --strategy-path user_data/profile_bias_strategies/PumpDetector --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PumpDetector --strategy-path user_data/profile_bias_strategies/PumpDetector --timerange 20190101-20190401 --no-color
  ```
- `Quickie`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Quickie --strategy-path user_data/profile_bias_strategies/Quickie --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Quickie --strategy-path user_data/profile_bias_strategies/Quickie --timerange 20190101-20190401 --no-color
  ```
- `RSI`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI --strategy-path user_data/profile_bias_strategies/RSI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI --strategy-path user_data/profile_bias_strategies/RSI --timerange 20190101-20190401 --no-color
  ```
- `RSIBB02`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/RSIBB02-override-f400cf1f3448.json --strategy RSIBB02 --strategy-path repos/davidzr_freqtrade-strategies/strategies/RSIBB02 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RSIBB02 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/RSIBB02_gate.json --strategy RSIBB02 --strategy-path user_data/profile_bias_strategies/RSIBB02 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/RSIBB02_startup_24.json --strategy RSIBB02 --strategy-path user_data/profile_bias_strategies/RSIBB02 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `RSIDirectionalWithTrend`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy RSIDirectionalWithTrend --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies-that-work --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RSIDirectionalWithTrend --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSIDirectionalWithTrend --strategy-path user_data/profile_bias_strategies/RSIDirectionalWithTrend --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/RSIDirectionalWithTrend_startup_24.json --strategy RSIDirectionalWithTrend --strategy-path user_data/profile_bias_strategies/RSIDirectionalWithTrend-0268a91f --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `RSIDirectionalWithTrendSlow`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy RSIDirectionalWithTrendSlow --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies-that-work --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RSIDirectionalWithTrendSlow --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSIDirectionalWithTrendSlow --strategy-path user_data/profile_bias_strategies/RSIDirectionalWithTrendSlow --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/RSIDirectionalWithTrendSlow_startup_24.json --strategy RSIDirectionalWithTrendSlow --strategy-path user_data/profile_bias_strategies/RSIDirectionalWithTrendSlow-247b9c8f --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `RSI_BB`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI_BB --strategy-path user_data/profile_bias_strategies/RSI_BB --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI_BB --strategy-path user_data/profile_bias_strategies/RSI_BB --timerange 20190101-20190401 --no-color
  ```
- `RSI_EMA_strategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI_EMA_strategy --strategy-path user_data/profile_bias_strategies/RSI_EMA_strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI_EMA_strategy --strategy-path user_data/profile_bias_strategies/RSI_EMA_strategy --timerange 20190101-20190401 --no-color
  ```
- `RSIv2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSIv2 --strategy-path user_data/profile_bias_strategies/RSIv2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RSIv2 --strategy-path user_data/profile_bias_strategies/RSIv2 --timerange 20190101-20190401 --no-color
  ```
- `RalliV1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RalliV1 --strategy-path user_data/profile_bias_strategies/RalliV1 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RalliV1 --strategy-path user_data/profile_bias_strategies/RalliV1 --timerange 20190101-20190401 --no-color
  ```
- `RalliV1_disable56`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RalliV1_disable56 --strategy-path user_data/profile_bias_strategies/RalliV1_disable56 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RalliV1_disable56 --strategy-path user_data/profile_bias_strategies/RalliV1_disable56 --timerange 20190101-20190401 --no-color
  ```
- `RegimeFilterStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy RegimeFilterStrategy --strategy-path repos/Bananajoexxc_RegimeFilterStrategy-Freqtrade/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RegimeFilterStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy RegimeFilterStrategy --strategy-path user_data/profile_bias_strategies/RegimeFilterStrategy --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy RegimeFilterStrategy --strategy-path user_data/profile_bias_strategies/RegimeFilterStrategy --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `ReinforcedAverageStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ReinforcedAverageStrategy --strategy-path user_data/profile_bias_strategies/ReinforcedAverageStrategy --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ReinforcedAverageStrategy --strategy-path user_data/profile_bias_strategies/ReinforcedAverageStrategy --timerange 20190101-20190401 --no-color
  ```
- `ReinforcedSmoothScalp`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ReinforcedSmoothScalp --strategy-path user_data/profile_bias_strategies/ReinforcedSmoothScalp --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ReinforcedSmoothScalp --strategy-path user_data/profile_bias_strategies/ReinforcedSmoothScalp --timerange 20190101-20190401 --no-color
  ```
- `RobotradingBody`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RobotradingBody --strategy-path user_data/profile_bias_strategies/RobotradingBody --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RobotradingBody --strategy-path user_data/profile_bias_strategies/RobotradingBody --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540
  ```
- `RocMomentumStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RocMomentumStrategy --strategy-path user_data/profile_bias_strategies/RocMomentumStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RocMomentumStrategy --strategy-path user_data/profile_bias_strategies/RocMomentumStrategy --timerange 20190101-20190401 --no-color
  ```
- `Roth01`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Roth01 --strategy-path user_data/profile_bias_strategies/Roth01 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Roth01 --strategy-path user_data/profile_bias_strategies/Roth01 --timerange 20190101-20190401 --no-color
  ```
- `Roth03`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Roth03 --strategy-path user_data/profile_bias_strategies/Roth03 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Roth03 --strategy-path user_data/profile_bias_strategies/Roth03 --timerange 20190101-20190401 --no-color
  ```
- `RsiBollingerStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RsiBollingerStrategy --strategy-path user_data/profile_bias_strategies/RsiBollingerStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RsiBollingerStrategy --strategy-path user_data/profile_bias_strategies/RsiBollingerStrategy --timerange 20190101-20190401 --no-color
  ```
- `RsiDivergenceStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RsiDivergenceStrategy --strategy-path user_data/profile_bias_strategies/RsiDivergenceStrategy --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RsiDivergenceStrategy --strategy-path user_data/profile_bias_strategies/RsiDivergenceStrategy --timerange 20190101-20190401 --no-color
  ```
- `SAR`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SAR --strategy-path user_data/profile_bias_strategies/SAR --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SAR --strategy-path user_data/profile_bias_strategies/SAR-c00b2014 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAIP3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAIP3 --strategy-path user_data/profile_bias_strategies/SMAIP3 --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAIP3 --strategy-path user_data/profile_bias_strategies/SMAIP3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAIP3v2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAIP3v2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAIP3v2-e79dedd0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/SMAIP3v2-e79dedd0_gate.json --strategy SMAIP3v2 --strategy-path user_data/profile_bias_strategies/SMAIP3v2-e79dedd0 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAIP3v2 --strategy-path user_data/profile_bias_strategies/SMAIP3v2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAOG`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOG --strategy-path user_data/profile_bias_strategies/SMAOG --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOG --strategy-path user_data/profile_bias_strategies/SMAOG --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAOffset`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset --strategy-path user_data/profile_bias_strategies/SMAOffset --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset --strategy-path user_data/profile_bias_strategies/SMAOffset --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOpt`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOpt --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOpt --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOpt --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOpt --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV0`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV0 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV0 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV0 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV0 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1HO1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1HO1 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1HO1 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1HO1 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1HO1 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1Mod`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1Mod2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod2 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod2 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod2 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod2 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1_kkeue_20210619`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1_kkeue_20210619 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1_kkeue_20210619 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1_kkeue_20210619 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1_kkeue_20210619 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetV2 --strategy-path user_data/profile_bias_strategies/SMAOffsetV2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetV2 --strategy-path user_data/profile_bias_strategies/SMAOffsetV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAOffset_Hippocritical_dca`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca --timerange 20190101-20190401 --no-color
  ```
- `SMAOffset_Hippocritical_dca_leverage`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long.json --strategy SMAOffset_Hippocritical_dca_leverage --strategy-path repos/TheoBrigitte_freqtrade/strategies/smas/dry-run/2025-01-29 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffset_Hippocritical_dca_leverage --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy SMAOffset_Hippocritical_dca_leverage --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_leverage --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy SMAOffset_Hippocritical_dca_leverage --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_leverage --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `SMAOffset_Hippocritical_dca_old`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca_old --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_old --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca_old --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_old --timerange 20190101-20190401 --no-color
  ```
- `SMAOffset_Hippocritical_dca_protections`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca_protections --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_protections --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca_protections --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_protections --timerange 20190101-20190401 --no-color
  ```
- `SMA_BBRSI`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMA_BBRSI --strategy-path user_data/profile_bias_strategies/SMA_BBRSI --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMA_BBRSI --strategy-path user_data/profile_bias_strategies/SMA_BBRSI --timerange 20190101-20190401 --no-color
  ```
- `SRsi`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SRsi --strategy-path user_data/profile_bias_strategies/SRsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SRsi --strategy-path user_data/profile_bias_strategies/SRsi --timerange 20190101-20190401 --no-color
  ```
- `STRATEGY_RSI_BB_BOUNDS_CROSS`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy STRATEGY_RSI_BB_BOUNDS_CROSS --strategy-path user_data/profile_bias_strategies/STRATEGY_RSI_BB_BOUNDS_CROSS --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy STRATEGY_RSI_BB_BOUNDS_CROSS --strategy-path user_data/profile_bias_strategies/STRATEGY_RSI_BB_BOUNDS_CROSS --timerange 20190101-20190401 --no-color
  ```
- `STRATEGY_RSI_BB_CROSS`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy STRATEGY_RSI_BB_CROSS --strategy-path user_data/profile_bias_strategies/STRATEGY_RSI_BB_CROSS --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy STRATEGY_RSI_BB_CROSS --strategy-path user_data/profile_bias_strategies/STRATEGY_RSI_BB_CROSS --timerange 20190101-20190401 --no-color
  ```
- `SampleStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategy --strategy-path user_data/profile_bias_strategies/SampleStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategy --strategy-path user_data/profile_bias_strategies/SampleStrategy --timerange 20190101-20190401 --no-color
  ```
- `SampleStrategyV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategyV2 --strategy-path user_data/profile_bias_strategies/SampleStrategyV2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategyV2 --strategy-path user_data/profile_bias_strategies/SampleStrategyV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Sar`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Sar --strategy-path user_data/profile_bias_strategies/Sar --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Sar --strategy-path user_data/profile_bias_strategies/Sar --timerange 20190101-20190401 --no-color
  ```
- `Saturn5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Saturn5_gate.json --strategy Saturn5 --strategy-path user_data/profile_bias_strategies/Saturn5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Saturn5 --strategy-path user_data/profile_bias_strategies/Saturn5 --timerange 20190101-20190401 --no-color
  ```
- `Scalp`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Scalp --strategy-path user_data/profile_bias_strategies/Scalp --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Scalp --strategy-path user_data/profile_bias_strategies/Scalp --timerange 20190101-20190401 --no-color
  ```
- `Schism`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Schism --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Schism-4f0b8f62 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Schism-4f0b8f62_gate.json --strategy Schism --strategy-path user_data/profile_bias_strategies/Schism-4f0b8f62 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism --strategy-path user_data/profile_bias_strategies/Schism --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Schism2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Schism2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Schism2-488547c4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Schism2-488547c4_gate.json --strategy Schism2 --strategy-path user_data/profile_bias_strategies/Schism2-488547c4 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism2 --strategy-path user_data/profile_bias_strategies/Schism2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Schism3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism3 --strategy-path user_data/profile_bias_strategies/Schism3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism3 --strategy-path user_data/profile_bias_strategies/Schism3 --timerange 20190101-20190401 --no-color
  ```
- `Schism4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism4 --strategy-path user_data/profile_bias_strategies/Schism4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism4 --strategy-path user_data/profile_bias_strategies/Schism4 --timerange 20190101-20190401 --no-color
  ```
- `Seb`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Seb --strategy-path user_data/profile_bias_strategies/Seb --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Seb --strategy-path user_data/profile_bias_strategies/Seb --timerange 20190101-20190401 --no-color
  ```
- `Simple`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Simple --strategy-path user_data/profile_bias_strategies/Simple --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Simple --strategy-path user_data/profile_bias_strategies/Simple --timerange 20190101-20190401 --no-color
  ```
- `SimpleHopt`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SimpleHopt --strategy-path user_data/profile_bias_strategies/SimpleHopt --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SimpleHopt --strategy-path user_data/profile_bias_strategies/SimpleHopt --timerange 20190101-20190401 --no-color
  ```
- `SimpleHopt1Along`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SimpleHopt1Along --strategy-path "repos/MelvynClark_Freqtrade-Strategy/Simple Strategy" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SimpleHopt1Along-df7ee9ca --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SimpleHopt1Along --strategy-path user_data/profile_bias_strategies/SimpleHopt1Along --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/SimpleHopt1Along_startup_6.json --strategy SimpleHopt1Along --strategy-path user_data/profile_bias_strategies/SimpleHopt1Along --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540
  ```
- `SlowPotato`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SlowPotato --strategy-path user_data/profile_bias_strategies/SlowPotato --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SlowPotato --strategy-path user_data/profile_bias_strategies/SlowPotato --timerange 20190101-20190401 --no-color
  ```
- `Slowbro`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Slowbro --strategy-path user_data/profile_bias_strategies/Slowbro --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Slowbro --strategy-path user_data/profile_bias_strategies/Slowbro --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `SmaRsiStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SmaRsiStrategy --strategy-path user_data/profile_bias_strategies/SmaRsiStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SmaRsiStrategy --strategy-path user_data/profile_bias_strategies/SmaRsiStrategy --timerange 20190101-20190401 --no-color
  ```
- `SmartMoneyStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SmartMoneyStrategy --strategy-path user_data/profile_bias_strategies/SmartMoneyStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SmartMoneyStrategy --strategy-path user_data/profile_bias_strategies/SmartMoneyStrategy --timerange 20190101-20190401 --no-color
  ```
- `SmartMoneyStrategyHyperopt`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SmartMoneyStrategyHyperopt --strategy-path repos/mikedigriz_freqtrade-strategy-mikedigriz/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SmartMoneyStrategyHyperopt-fff5e4c0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SmartMoneyStrategyHyperopt --strategy-path user_data/profile_bias_strategies/SmartMoneyStrategyHyperopt --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/SmartMoneyStrategyHyperopt_startup_24.json --strategy SmartMoneyStrategyHyperopt --strategy-path user_data/profile_bias_strategies/SmartMoneyStrategyHyperopt --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `SmoothOperator`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SmoothOperator --strategy-path user_data/profile_bias_strategies/SmoothOperator --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SmoothOperator --strategy-path user_data/profile_bias_strategies/SmoothOperator --timerange 20190101-20190401 --no-color
  ```
- `SmoothScalp`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SmoothScalp --strategy-path user_data/profile_bias_strategies/SmoothScalp --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SmoothScalp --strategy-path user_data/profile_bias_strategies/SmoothScalp --timerange 20190101-20190401 --no-color
  ```
- `SqueezeMomentum`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SqueezeMomentum --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SqueezeMomentum-55dbc2ef --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeMomentum --strategy-path user_data/profile_bias_strategies/SqueezeMomentum --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeMomentum --strategy-path user_data/profile_bias_strategies/SqueezeMomentum --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SqueezeMomentumStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeMomentumStrategy --strategy-path user_data/profile_bias_strategies/SqueezeMomentumStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeMomentumStrategy --strategy-path user_data/profile_bias_strategies/SqueezeMomentumStrategy --timerange 20190101-20190401 --no-color
  ```
- `StarRise`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StarRise --strategy-path user_data/profile_bias_strategies/StarRise --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StarRise --strategy-path user_data/profile_bias_strategies/StarRise --timerange 20190101-20190401 --no-color
  ```
- `StarRise_strat`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StarRise_strat --strategy-path user_data/profile_bias_strategies/StarRise_strat --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StarRise_strat --strategy-path user_data/profile_bias_strategies/StarRise_strat --timerange 20190101-20190401 --no-color
  ```
- `Stavix2`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/Stavix2-override-93c76024faa3.json --strategy Stavix2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/Stavix2 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Stavix2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Stavix2_gate.json --strategy Stavix2 --strategy-path user_data/profile_bias_strategies/Stavix2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Stavix2_startup_1440.json --strategy Stavix2 --strategy-path user_data/profile_bias_strategies/Stavix2-4c91e408 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880 --timeframe 1m
  ```
- `StochRSITEMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochRSITEMA --strategy-path user_data/profile_bias_strategies/StochRSITEMA --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochRSITEMA --strategy-path user_data/profile_bias_strategies/StochRSITEMA --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `StochasticCciStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticCciStrategy --strategy-path user_data/profile_bias_strategies/StochasticCciStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticCciStrategy --strategy-path user_data/profile_bias_strategies/StochasticCciStrategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `StochasticOversoldStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticOversoldStrategy --strategy-path user_data/profile_bias_strategies/StochasticOversoldStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticOversoldStrategy --strategy-path user_data/profile_bias_strategies/StochasticOversoldStrategy --timerange 20190101-20190401 --no-color
  ```
- `StochasticRsiStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticRsiStrategy --strategy-path user_data/profile_bias_strategies/StochasticRsiStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticRsiStrategy --strategy-path user_data/profile_bias_strategies/StochasticRsiStrategy --timerange 20190101-20190401 --no-color
  ```
- `Strategy001`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001 --strategy-path user_data/profile_bias_strategies/Strategy001 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001 --strategy-path user_data/profile_bias_strategies/Strategy001 --timerange 20190101-20190401 --no-color
  ```
- `Strategy001_custom_exit`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001_custom_exit --strategy-path user_data/profile_bias_strategies/Strategy001_custom_exit --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001_custom_exit --strategy-path user_data/profile_bias_strategies/Strategy001_custom_exit --timerange 20190101-20190401 --no-color
  ```
- `Strategy001_custom_sell`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001_custom_sell --strategy-path user_data/profile_bias_strategies/Strategy001_custom_sell --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001_custom_sell --strategy-path user_data/profile_bias_strategies/Strategy001_custom_sell --timerange 20190101-20190401 --no-color
  ```
- `Strategy002`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy002 --strategy-path user_data/profile_bias_strategies/Strategy002 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy002 --strategy-path user_data/profile_bias_strategies/Strategy002 --timerange 20190101-20190401 --no-color
  ```
- `Strategy003`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy003 --strategy-path user_data/profile_bias_strategies/Strategy003 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy003 --strategy-path user_data/profile_bias_strategies/Strategy003 --timerange 20190101-20190401 --no-color
  ```
- `Strategy004`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy004 --strategy-path user_data/profile_bias_strategies/Strategy004 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy004 --strategy-path user_data/profile_bias_strategies/Strategy004 --timerange 20190101-20190401 --no-color
  ```
- `Strategy005`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy005 --strategy-path user_data/profile_bias_strategies/Strategy005 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy005 --strategy-path user_data/profile_bias_strategies/Strategy005 --timerange 20190101-20190401 --no-color
  ```
- `StrategyScalpingFast`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StrategyScalpingFast --strategy-path user_data/profile_bias_strategies/StrategyScalpingFast --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StrategyScalpingFast --strategy-path user_data/profile_bias_strategies/StrategyScalpingFast --timerange 20190101-20190401 --no-color
  ```
- `StrategyScalpingFast2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StrategyScalpingFast2 --strategy-path user_data/profile_bias_strategies/StrategyScalpingFast2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StrategyScalpingFast2 --strategy-path user_data/profile_bias_strategies/StrategyScalpingFast2 --timerange 20190101-20190401 --no-color
  ```
- `SuperHV27`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SuperHV27 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SuperHV27-aefe004a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/SuperHV27-aefe004a_gate.json --strategy SuperHV27 --strategy-path user_data/profile_bias_strategies/SuperHV27-aefe004a --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/SuperHV27_startup_288.json --strategy SuperHV27 --strategy-path user_data/profile_bias_strategies/SuperHV27 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SuperTrend`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SuperTrend --strategy-path user_data/profile_bias_strategies/SuperTrend --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SuperTrend --strategy-path user_data/profile_bias_strategies/SuperTrend-e9770a14 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `SupertrendStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SupertrendStrategy --strategy-path user_data/profile_bias_strategies/SupertrendStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SupertrendStrategy --strategy-path user_data/profile_bias_strategies/SupertrendStrategy --timerange 20190101-20190401 --no-color --startup-candle 48 168 336 720 2160
  ```
- `SwingHigh`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/SwingHigh-override-87e303112603.json --strategy SwingHigh --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SwingHigh --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/SwingHigh_gate.json --strategy SwingHigh --strategy-path user_data/profile_bias_strategies/SwingHigh --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/SwingHigh_startup_48.json --strategy SwingHigh --strategy-path user_data/profile_bias_strategies/SwingHigh --timerange 20190101-20190401 --no-color --startup-candle 48 96 336 672 1440 4320 --timeframe 30m
  ```
- `SwingHighToSky`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SwingHighToSky --strategy-path user_data/profile_bias_strategies/SwingHighToSky --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/SwingHighToSky_startup_96.json --strategy SwingHighToSky --strategy-path user_data/profile_bias_strategies/SwingHighToSky --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `TD`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TD --strategy-path user_data/profile_bias_strategies/TD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TD --strategy-path user_data/profile_bias_strategies/TD --timerange 20190101-20190401 --no-color
  ```
- `TDSequentialStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TDSequentialStrategy --strategy-path user_data/profile_bias_strategies/TDSequentialStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TDSequentialStrategy --strategy-path user_data/profile_bias_strategies/TDSequentialStrategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `TEMA`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TEMA --strategy-path user_data/profile_bias_strategies/TEMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TEMA --strategy-path user_data/profile_bias_strategies/TEMA --timerange 20190101-20190401 --no-color
  ```
- `TRIWAVE`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TRIWAVE --strategy-path user_data/profile_bias_strategies/TRIWAVE --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TRIWAVE --strategy-path user_data/profile_bias_strategies/TRIWAVE --timerange 20190101-20190401 --no-color
  ```
- `TWAPStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy TWAPStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TWAPStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy TWAPStrategy --strategy-path user_data/profile_bias_strategies/TWAPStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy TWAPStrategy --strategy-path user_data/profile_bias_strategies/TWAPStrategy --timerange 20200301-20200401 --no-color
  ```
- `TechnicalExampleStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TechnicalExampleStrategy --strategy-path user_data/profile_bias_strategies/TechnicalExampleStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TechnicalExampleStrategy --strategy-path user_data/profile_bias_strategies/TechnicalExampleStrategy --timerange 20190101-20190401 --no-color
  ```
- `TemaMaster`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaMaster --strategy-path user_data/profile_bias_strategies/TemaMaster --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaMaster --strategy-path user_data/profile_bias_strategies/TemaMaster --timerange 20190101-20190401 --no-color
  ```
- `TemaMaster3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaMaster3 --strategy-path user_data/profile_bias_strategies/TemaMaster3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaMaster3 --strategy-path user_data/profile_bias_strategies/TemaMaster3 --timerange 20190101-20190401 --no-color
  ```
- `TemaPure`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPure --strategy-path user_data/profile_bias_strategies/TemaPure --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPure --strategy-path user_data/profile_bias_strategies/TemaPure --timerange 20190101-20190401 --no-color
  ```
- `TemaPureNeat`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPureNeat --strategy-path user_data/profile_bias_strategies/TemaPureNeat --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPureNeat --strategy-path user_data/profile_bias_strategies/TemaPureNeat --timerange 20190101-20190401 --no-color
  ```
- `TemaPureTwo`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPureTwo --strategy-path user_data/profile_bias_strategies/TemaPureTwo --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPureTwo --strategy-path user_data/profile_bias_strategies/TemaPureTwo --timerange 20190101-20190401 --no-color
  ```
- `TemaStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaStrategy --strategy-path user_data/profile_bias_strategies/TemaStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaStrategy --strategy-path user_data/profile_bias_strategies/TemaStrategy --timerange 20190101-20190401 --no-color
  ```
- `TenderEnter`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TenderEnter --strategy-path user_data/profile_bias_strategies/TenderEnter --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TenderEnter --strategy-path user_data/profile_bias_strategies/TenderEnter --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `Test_MAMA4`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Test_MAMA4 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Test_MAMA4-aa83c1d0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Test_MAMA4-aa83c1d0_gate.json --strategy Test_MAMA4 --strategy-path user_data/profile_bias_strategies/Test_MAMA4-aa83c1d0 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Test_MAMA4 --strategy-path user_data/profile_bias_strategies/Test_MAMA4 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `TheForce`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TheForce --strategy-path user_data/profile_bias_strategies/TheForce --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TheForce --strategy-path user_data/profile_bias_strategies/TheForce --timerange 20190101-20190401 --no-color
  ```
- `TheRealPullbackV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TheRealPullbackV2 --strategy-path user_data/profile_bias_strategies/TheRealPullbackV2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TheRealPullbackV2 --strategy-path user_data/profile_bias_strategies/TheRealPullbackV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ToTheMoon`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy ToTheMoon --strategy-path repos/TheoBrigitte_freqtrade/strategies/moon --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ToTheMoon --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy ToTheMoon --strategy-path user_data/profile_bias_strategies/ToTheMoon --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy ToTheMoon --strategy-path user_data/profile_bias_strategies/ToTheMoon --timerange 20200301-20200401 --no-color
  ```
- `TouchEmaDelayStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TouchEmaDelayStrategy --strategy-path user_data/profile_bias_strategies/TouchEmaDelayStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TouchEmaDelayStrategy --strategy-path user_data/profile_bias_strategies/TouchEmaDelayStrategy --timerange 20190101-20190401 --no-color
  ```
- `TouchEmaStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TouchEmaStrategy --strategy-path user_data/profile_bias_strategies/TouchEmaStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TouchEmaStrategy --strategy-path user_data/profile_bias_strategies/TouchEmaStrategy --timerange 20190101-20190401 --no-color
  ```
- `TrendAtrStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrendAtrStrategy --strategy-path user_data/profile_bias_strategies/TrendAtrStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrendAtrStrategy --strategy-path user_data/profile_bias_strategies/TrendAtrStrategy --timerange 20190101-20190401 --no-color
  ```
- `Trend_Strength_Directional`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Trend_Strength_Directional --strategy-path user_data/profile_bias_strategies/Trend_Strength_Directional --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Trend_Strength_Directional --strategy-path user_data/profile_bias_strategies/Trend_Strength_Directional --timerange 20190101-20190401 --no-color
  ```
- `TripleEmaStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TripleEmaStrategy --strategy-path user_data/profile_bias_strategies/TripleEmaStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TripleEmaStrategy --strategy-path user_data/profile_bias_strategies/TripleEmaStrategy --timerange 20190101-20190401 --no-color
  ```
- `TrixSignalStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixSignalStrategy --strategy-path user_data/profile_bias_strategies/TrixSignalStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixSignalStrategy --strategy-path user_data/profile_bias_strategies/TrixSignalStrategy --timerange 20190101-20190401 --no-color
  ```
- `TrixStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixStrategy --strategy-path user_data/profile_bias_strategies/TrixStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixStrategy --strategy-path user_data/profile_bias_strategies/TrixStrategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `TrixV15Strategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV15Strategy --strategy-path user_data/profile_bias_strategies/TrixV15Strategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV15Strategy --strategy-path user_data/profile_bias_strategies/TrixV15Strategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `TrixV21Strategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV21Strategy --strategy-path user_data/profile_bias_strategies/TrixV21Strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV21Strategy --strategy-path user_data/profile_bias_strategies/TrixV21Strategy --timerange 20190101-20190401 --no-color
  ```
- `TrixV23Strategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV23Strategy --strategy-path user_data/profile_bias_strategies/TrixV23Strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV23Strategy --strategy-path user_data/profile_bias_strategies/TrixV23Strategy --timerange 20190101-20190401 --no-color
  ```
- `TwoCandle`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TwoCandle --strategy-path user_data/profile_bias_strategies/TwoCandle --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TwoCandle --strategy-path user_data/profile_bias_strategies/TwoCandle --timerange 20190101-20190401 --no-color
  ```
- `UltimateMomentumIndicator`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy UltimateMomentumIndicator --strategy-path user_data/profile_bias_strategies/UltimateMomentumIndicator --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy UltimateMomentumIndicator --strategy-path user_data/profile_bias_strategies/UltimateMomentumIndicator --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `UniversalMACD`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy UniversalMACD --strategy-path user_data/profile_bias_strategies/UniversalMACD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy UniversalMACD --strategy-path user_data/profile_bias_strategies/UniversalMACD --timerange 20190101-20190401 --no-color
  ```
- `Uptrend`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Uptrend --strategy-path user_data/profile_bias_strategies/Uptrend --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Uptrend --strategy-path user_data/profile_bias_strategies/Uptrend --timerange 20190101-20190401 --no-color
  ```
- `VWAP`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy VWAP --strategy-path user_data/profile_bias_strategies/VWAP --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy VWAP --strategy-path user_data/profile_bias_strategies/VWAP --timerange 20190101-20190401 --no-color
  ```
- `VolatilitySystem`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long.json --strategy VolatilitySystem --strategy-path repos/TheoBrigitte_freqtrade/strategies/volatility --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/VolatilitySystem --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy VolatilitySystem --strategy-path user_data/profile_bias_strategies/VolatilitySystem --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long.json --strategy VolatilitySystem --strategy-path user_data/profile_bias_strategies/VolatilitySystem --timerange 20200301-20200401 --no-color
  ```
- `VolatilitySystemV2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy VolatilitySystemV2 --strategy-path repos/TheoBrigitte_freqtrade/strategies/volatility --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/VolatilitySystemV2 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy VolatilitySystemV2 --strategy-path user_data/profile_bias_strategies/VolatilitySystemV2 --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy VolatilitySystemV2 --strategy-path user_data/profile_bias_strategies/VolatilitySystemV2 --timerange 20200301-20200401 --no-color
  ```
- `VolumeBreakoutStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy VolumeBreakoutStrategy --strategy-path user_data/profile_bias_strategies/VolumeBreakoutStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy VolumeBreakoutStrategy --strategy-path user_data/profile_bias_strategies/VolumeBreakoutStrategy --timerange 20190101-20190401 --no-color
  ```
- `VortexStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy VortexStrategy --strategy-path user_data/profile_bias_strategies/VortexStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy VortexStrategy --strategy-path user_data/profile_bias_strategies/VortexStrategy --timerange 20190101-20190401 --no-color
  ```
- `VwapReversionStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy VwapReversionStrategy --strategy-path user_data/profile_bias_strategies/VwapReversionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy VwapReversionStrategy --strategy-path user_data/profile_bias_strategies/VwapReversionStrategy --timerange 20190101-20190401 --no-color
  ```
- `WTX3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy WTX3 --strategy-path repos/TheoBrigitte_freqtrade/strategies/wtx3 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/WTX3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/WTX3_gate.json --strategy WTX3 --strategy-path user_data/profile_bias_strategies/WTX3 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/WTX3_startup_288.json --strategy WTX3 --strategy-path user_data/profile_bias_strategies/WTX3 --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `WaveTrendStra`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy WaveTrendStra --strategy-path user_data/profile_bias_strategies/WaveTrendStra --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy WaveTrendStra --strategy-path user_data/profile_bias_strategies/WaveTrendStra --timerange 20190101-20190401 --no-color
  ```
- `WilliamsRStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy WilliamsRStrategy --strategy-path user_data/profile_bias_strategies/WilliamsRStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy WilliamsRStrategy --strategy-path user_data/profile_bias_strategies/WilliamsRStrategy --timerange 20190101-20190401 --no-color
  ```
- `XebTradeStrat`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy XebTradeStrat --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/XebTradeStrat-5d160cab --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy XebTradeStrat --strategy-path user_data/profile_bias_strategies/XebTradeStrat --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/XebTradeStrat_startup_1440.json --strategy XebTradeStrat --strategy-path user_data/profile_bias_strategies/XebTradeStrat --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `XtraThicc`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy XtraThicc --strategy-path user_data/profile_bias_strategies/XtraThicc --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy XtraThicc --strategy-path user_data/profile_bias_strategies/XtraThicc --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `YOLO`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy YOLO --strategy-path user_data/profile_bias_strategies/YOLO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy YOLO --strategy-path user_data/profile_bias_strategies/YOLO --timerange 20190101-20190401 --no-color
  ```
- `ZScoreMeanReversionStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ZScoreMeanReversionStrategy --strategy-path user_data/profile_bias_strategies/ZScoreMeanReversionStrategy --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ZScoreMeanReversionStrategy --strategy-path user_data/profile_bias_strategies/ZScoreMeanReversionStrategy --timerange 20190101-20190401 --no-color
  ```
- `ZaratustraDCA2_06`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy ZaratustraDCA2_06 --strategy-path repos/TheoBrigitte_freqtrade/strategies/Zaratustra --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ZaratustraDCA2_06 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy ZaratustraDCA2_06 --strategy-path user_data/profile_bias_strategies/ZaratustraDCA2_06 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy ZaratustraDCA2_06 --strategy-path user_data/profile_bias_strategies/ZaratustraDCA2_06 --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `ZaratustraDCA2_07`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy ZaratustraDCA2_07 --strategy-path repos/bustillo_freqtrade-strategies/ZaratustraDCA --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ZaratustraDCA2_07 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy ZaratustraDCA2_07 --strategy-path user_data/profile_bias_strategies/ZaratustraDCA2_07 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy ZaratustraDCA2_07 --strategy-path user_data/profile_bias_strategies/ZaratustraDCA2_07 --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `ZaratustraDCA5`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy ZaratustraDCA5 --strategy-path repos/bustillo_freqtrade-strategies/ZaratustraDCA --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ZaratustraDCA5 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy ZaratustraDCA5 --strategy-path user_data/profile_bias_strategies/ZaratustraDCA5 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/ZaratustraDCA5_startup_288.json --strategy ZaratustraDCA5 --strategy-path user_data/profile_bias_strategies/ZaratustraDCA5 --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `adaptive`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive --strategy-path user_data/profile_bias_strategies/adaptive --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive --strategy-path user_data/profile_bias_strategies/adaptive --timerange 20190101-20190401 --no-color
  ```
- `adaptive_trend`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive_trend --strategy-path user_data/profile_bias_strategies/adaptive_trend --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive_trend --strategy-path user_data/profile_bias_strategies/adaptive_trend --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540
  ```
- `adx_opt_strat`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/adx_opt_strat-override-93c76024faa3.json --strategy adx_opt_strat --strategy-path repos/davidzr_freqtrade-strategies/strategies/adx_opt_strat --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/adx_opt_strat --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/adx_opt_strat_gate.json --strategy adx_opt_strat --strategy-path user_data/profile_bias_strategies/adx_opt_strat --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/adx_opt_strat_startup_1440.json --strategy adx_opt_strat --strategy-path user_data/profile_bias_strategies/adx_opt_strat --timerange 20190101-20190401 --no-color --startup-candle 1440 2880 --timeframe 1m
  ```
- `adxbbrsi2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy adxbbrsi2 --strategy-path user_data/profile_bias_strategies/adxbbrsi2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy adxbbrsi2 --strategy-path user_data/profile_bias_strategies/adxbbrsi2 --timerange 20190101-20190401 --no-color
  ```
- `bb_rsi_opt_new`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/bb_rsi_opt_new-override-f400cf1f3448.json --strategy bb_rsi_opt_new --strategy-path repos/davidzr_freqtrade-strategies/strategies/bb_rsi_opt_new --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/bb_rsi_opt_new --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bb_rsi_opt_new_gate.json --strategy bb_rsi_opt_new --strategy-path user_data/profile_bias_strategies/bb_rsi_opt_new --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bb_rsi_opt_new --strategy-path user_data/profile_bias_strategies/bb_rsi_opt_new --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `bbandrsi`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbandrsi --strategy-path user_data/profile_bias_strategies/bbandrsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbandrsi --strategy-path user_data/profile_bias_strategies/bbandrsi --timerange 20190101-20190401 --no-color
  ```
- `bbrsi`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi --strategy-path user_data/profile_bias_strategies/bbrsi --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi --strategy-path user_data/profile_bias_strategies/bbrsi-10d8c6d1 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `bbrsi1_strategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy bbrsi1_strategy --strategy-path repos/davidzr_freqtrade-strategies/strategies/bbrsi1_strategy --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/bbrsi1_strategy --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi1_strategy --strategy-path user_data/profile_bias_strategies/bbrsi1_strategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi1_strategy --strategy-path user_data/profile_bias_strategies/bbrsi1_strategy --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `bbrsi4Freq`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi4Freq --strategy-path user_data/profile_bias_strategies/bbrsi4Freq --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi4Freq --strategy-path user_data/profile_bias_strategies/bbrsi4Freq --timerange 20190101-20190401 --no-color
  ```
- `bestV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bestV2 --strategy-path user_data/profile_bias_strategies/bestV2 --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bestV2 --strategy-path user_data/profile_bias_strategies/bestV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `botbaby`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy botbaby --strategy-path user_data/profile_bias_strategies/botbaby --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy botbaby --strategy-path user_data/profile_bias_strategies/botbaby --timerange 20190101-20190401 --no-color --startup-candle 48 96 336 672 1440 4320
  ```
- `chispei`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/chispei-override-aa2053461232.json --strategy chispei --strategy-path repos/botenesp_freqtrade_strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/chispei --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/chispei_gate.json --strategy chispei --strategy-path user_data/profile_bias_strategies/chispei --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/chispei_startup_6.json --strategy chispei --strategy-path user_data/profile_bias_strategies/chispei --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 --timeframe 4h
  ```
- `conny`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy conny --strategy-path user_data/profile_bias_strategies/conny --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy conny --strategy-path user_data/profile_bias_strategies/conny --timerange 20190101-20190401 --no-color
  ```
- `cryptohassle`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/cryptohassle-override-f400cf1f3448.json --strategy cryptohassle --strategy-path repos/davidzr_freqtrade-strategies/strategies/cryptohassle --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/cryptohassle --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/cryptohassle_gate.json --strategy cryptohassle --strategy-path user_data/profile_bias_strategies/cryptohassle --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/cryptohassle_startup_24.json --strategy cryptohassle --strategy-path user_data/profile_bias_strategies/cryptohassle --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `cryptotank`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotank --strategy-path user_data/profile_bias_strategies/cryptotank --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotank --strategy-path user_data/profile_bias_strategies/cryptotank --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `cryptotankV2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV2 --strategy-path user_data/profile_bias_strategies/cryptotankV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV2 --strategy-path user_data/profile_bias_strategies/cryptotankV2 --timerange 20190101-20190401 --no-color
  ```
- `cryptotankV5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV5 --strategy-path user_data/profile_bias_strategies/cryptotankV5 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV5 --strategy-path user_data/profile_bias_strategies/cryptotankV5 --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `custom_sell`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy custom_sell --strategy-path repos/davidzr_freqtrade-strategies/strategies/custom_sell --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/custom_sell --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/custom_sell_gate.json --strategy custom_sell --strategy-path user_data/profile_bias_strategies/custom_sell --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy custom_sell --strategy-path user_data/profile_bias_strategies/custom_sell --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `dualwave`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy dualwave --strategy-path user_data/profile_bias_strategies/dualwave --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy dualwave --strategy-path user_data/profile_bias_strategies/dualwave --timerange 20190101-20190401 --no-color
  ```
- `e6v34`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy e6v34 --strategy-path user_data/profile_bias_strategies/e6v34 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy e6v34 --strategy-path user_data/profile_bias_strategies/e6v34 --timerange 20190101-20190401 --no-color
  ```
- `eltoro`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro --strategy-path user_data/profile_bias_strategies/eltoro --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro --strategy-path user_data/profile_bias_strategies/eltoro --timerange 20190101-20190401 --no-color
  ```
- `eltoro1_4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro1_4 --strategy-path user_data/profile_bias_strategies/eltoro1_4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro1_4 --strategy-path user_data/profile_bias_strategies/eltoro1_4 --timerange 20190101-20190401 --no-color
  ```
- `eltoro1_4_simple`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro1_4_simple --strategy-path user_data/profile_bias_strategies/eltoro1_4_simple --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro1_4_simple --strategy-path user_data/profile_bias_strategies/eltoro1_4_simple --timerange 20190101-20190401 --no-color
  ```
- `ema`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ema --strategy-path user_data/profile_bias_strategies/ema --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ema --strategy-path user_data/profile_bias_strategies/ema --timerange 20190101-20190401 --no-color
  ```
- `fahmibah`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy fahmibah --strategy-path user_data/profile_bias_strategies/fahmibah --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy fahmibah --strategy-path user_data/profile_bias_strategies/fahmibah --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `gettinMoist`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy gettinMoist --strategy-path user_data/profile_bias_strategies/gettinMoist --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy gettinMoist --strategy-path user_data/profile_bias_strategies/gettinMoist --timerange 20190101-20190401 --no-color
  ```
- `hansencandlepatternV1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy hansencandlepatternV1 --strategy-path user_data/profile_bias_strategies/hansencandlepatternV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy hansencandlepatternV1 --strategy-path user_data/profile_bias_strategies/hansencandlepatternV1 --timerange 20190101-20190401 --no-color
  ```
- `heikin`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy heikin --strategy-path user_data/profile_bias_strategies/heikin --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy heikin --strategy-path user_data/profile_bias_strategies/heikin --timerange 20190101-20190401 --no-color
  ```
- `hlhb`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy hlhb --strategy-path user_data/profile_bias_strategies/hlhb --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy hlhb --strategy-path user_data/profile_bias_strategies/hlhb-4d4b7c4a --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `ichi`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ichi --strategy-path repos/werkkrew_freqtrade-strategies/strategies/archived --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ichi-a7e6edf3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ichi --strategy-path user_data/profile_bias_strategies/ichi --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/ichi_startup_24.json --strategy ichi --strategy-path user_data/profile_bias_strategies/ichi-a7e6edf3 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `keltnerchannel`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy keltnerchannel --strategy-path user_data/profile_bias_strategies/keltnerchannel --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy keltnerchannel --strategy-path user_data/profile_bias_strategies/keltnerchannel --timerange 20190101-20190401 --no-color
  ```
- `mabStra`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy mabStra --strategy-path user_data/profile_bias_strategies/mabStra --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/mabStra_startup_6.json --strategy mabStra --strategy-path user_data/profile_bias_strategies/mabStra --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540
  ```
- `macd_recovery`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/macd_recovery-override-2c7527d808c6.json --strategy macd_recovery --strategy-path repos/davidzr_freqtrade-strategies/strategies/macd_recovery --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/macd_recovery --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/macd_recovery_gate.json --strategy macd_recovery --strategy-path user_data/profile_bias_strategies/macd_recovery --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/macd_recovery_startup_288.json --strategy macd_recovery --strategy-path user_data/profile_bias_strategies/macd_recovery --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `mark_strat`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/mark_strat-override-93c76024faa3.json --strategy mark_strat --strategy-path repos/davidzr_freqtrade-strategies/strategies/mark_strat --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/mark_strat --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/mark_strat_gate.json --strategy mark_strat --strategy-path user_data/profile_bias_strategies/mark_strat --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy mark_strat --strategy-path user_data/profile_bias_strategies/mark_strat --timerange 20190101-20190401 --no-color --startup-candle 1440 2880 --timeframe 1m
  ```
- `mark_strat_opt`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/mark_strat_opt-override-93c76024faa3.json --strategy mark_strat_opt --strategy-path repos/davidzr_freqtrade-strategies/strategies/mark_strat_opt --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/mark_strat_opt --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/mark_strat_opt_gate.json --strategy mark_strat_opt --strategy-path user_data/profile_bias_strategies/mark_strat_opt --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy mark_strat_opt --strategy-path user_data/profile_bias_strategies/mark_strat_opt --timerange 20190101-20190401 --no-color --startup-candle 1440 2880 --timeframe 1m
  ```
- `momentum`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum --strategy-path user_data/profile_bias_strategies/momentum --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy momentum --strategy-path user_data/profile_bias_strategies/momentum --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `momentum_long`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy momentum_long --strategy-path user_data/profile_bias_strategies/momentum_long --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy momentum_long --strategy-path user_data/profile_bias_strategies/momentum_long --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `momentum_rsi`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_rsi --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum_rsi --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_rsi --strategy-path user_data/profile_bias_strategies/momentum_rsi --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy momentum_rsi --strategy-path user_data/profile_bias_strategies/momentum_rsi --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `momentum_wick`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_wick --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum_wick --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_wick --strategy-path user_data/profile_bias_strategies/momentum_wick --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy momentum_wick --strategy-path user_data/profile_bias_strategies/momentum_wick --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `moonhouse`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy moonhouse --strategy-path user_data/profile_bias_strategies/moonhouse --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy moonhouse --strategy-path user_data/profile_bias_strategies/moonhouse --timerange 20190101-20190401 --no-color
  ```
- `pmaxTest`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy pmaxTest --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/pmaxTest --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy pmaxTest --strategy-path user_data/profile_bias_strategies/pmaxTest --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/pmaxTest_startup_288.json --strategy pmaxTest --strategy-path user_data/profile_bias_strategies/pmaxTest --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `quantumfirst`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/quantumfirst-override-2c7527d808c6.json --strategy quantumfirst --strategy-path repos/davidzr_freqtrade-strategies/strategies/quantumfirst --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/quantumfirst --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/quantumfirst_gate.json --strategy quantumfirst --strategy-path user_data/profile_bias_strategies/quantumfirst --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/quantumfirst_startup_288.json --strategy quantumfirst --strategy-path user_data/profile_bias_strategies/quantumfirst --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `redditMA`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/redditMA-override-c517447bf6b2.json --strategy redditMA --strategy-path repos/davidzr_freqtrade-strategies/strategies/redditMA --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/redditMA --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/redditMA_gate.json --strategy redditMA --strategy-path user_data/profile_bias_strategies/redditMA --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy redditMA --strategy-path user_data/profile_bias_strategies/redditMA --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880 --timeframe 15m
  ```
- `simple_patterns`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy simple_patterns --strategy-path repos/TheoBrigitte_freqtrade/strategies/yodo --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/simple_patterns --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy simple_patterns --strategy-path user_data/profile_bias_strategies/simple_patterns --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy simple_patterns --strategy-path user_data/profile_bias_strategies/simple_patterns --timerange 20190101-20190401 --no-color
  ```
- `simple_vwap_v1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy simple_vwap_v1 --strategy-path repos/titouannwtt_freqtrade-ultimate/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/simple_vwap_v1-28330b62 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/simple_vwap_v1-28330b62_gate.json --strategy simple_vwap_v1 --strategy-path user_data/profile_bias_strategies/simple_vwap_v1-28330b62 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy simple_vwap_v1 --strategy-path user_data/profile_bias_strategies/simple_vwap_v1-28330b62 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `slope_is_dopeCT`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy slope_is_dopeCT --strategy-path user_data/profile_bias_strategies/slope_is_dopeCT --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy slope_is_dopeCT --strategy-path user_data/profile_bias_strategies/slope_is_dopeCT --timerange 20190101-20190401 --no-color
  ```
- `slownsteady`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy slownsteady --strategy-path repair/patched/repos/TheoBrigitte_freqtrade/strategies/slownsteady --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/slownsteady --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy slownsteady --strategy-path user_data/profile_bias_strategies/slownsteady --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy slownsteady --strategy-path user_data/profile_bias_strategies/slownsteady --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `stoploss`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy stoploss --strategy-path user_data/profile_bias_strategies/stoploss --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy stoploss --strategy-path user_data/profile_bias_strategies/stoploss --timerange 20190101-20190401 --no-color
  ```
- `strato`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy strato --strategy-path user_data/profile_bias_strategies/strato --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy strato --strategy-path user_data/profile_bias_strategies/strato --timerange 20190101-20190401 --no-color
  ```
- `tbtest`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/tbtest_gate.json --strategy tbtest --strategy-path user_data/profile_bias_strategies/tbtest --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy tbtest --strategy-path user_data/profile_bias_strategies/tbtest --timerange 20190101-20190401 --no-color
  ```
- `thetank3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy thetank3 --strategy-path user_data/profile_bias_strategies/thetank3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy thetank3 --strategy-path user_data/profile_bias_strategies/thetank3 --timerange 20190101-20190401 --no-color
  ```
- `thetank4TV`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy thetank4TV --strategy-path user_data/profile_bias_strategies/thetank4TV --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy thetank4TV --strategy-path user_data/profile_bias_strategies/thetank4TV --timerange 20190101-20190401 --no-color
  ```
- `true_lambo`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy true_lambo --strategy-path user_data/profile_bias_strategies/true_lambo --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy true_lambo --strategy-path user_data/profile_bias_strategies/true_lambo --timerange 20190101-20190401 --no-color
  ```
- `twinturboV8`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy twinturboV8 --strategy-path user_data/profile_bias_strategies/twinturboV8 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy twinturboV8 --strategy-path user_data/profile_bias_strategies/twinturboV8 --timerange 20190101-20190401 --no-color
  ```
- `twinturboV8_2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy twinturboV8_2 --strategy-path user_data/profile_bias_strategies/twinturboV8_2 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy twinturboV8_2 --strategy-path user_data/profile_bias_strategies/twinturboV8_2 --timerange 20190101-20190401 --no-color
  ```
- `ultratank`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ultratank --strategy-path user_data/profile_bias_strategies/ultratank --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ultratank --strategy-path user_data/profile_bias_strategies/ultratank --timerange 20190101-20190401 --no-color
  ```
- `wavetrend`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy wavetrend --strategy-path user_data/profile_bias_strategies/wavetrend --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy wavetrend --strategy-path user_data/profile_bias_strategies/wavetrend --timerange 20190101-20190401 --no-color
  ```
- `wavetrend_rsi`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy wavetrend_rsi --strategy-path user_data/profile_bias_strategies/wavetrend_rsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy wavetrend_rsi --strategy-path user_data/profile_bias_strategies/wavetrend_rsi --timerange 20190101-20190401 --no-color
  ```

## Convergence candidates - 37 strategies

A warm-up exists at which every indicator stays inside the band.
That is not admission: the paired full-window run must still show
an identical trade list.

| Strategy | Profile | Chosen warm-up | Worst drift | Tested | Results |
|---|---|---|---|---|---|
| `ADXDM` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-06 18:28:13 | `user_data/convergence_logs/ADXDM-eef844db-ladder.log` |
| `BigDrop` | `spot_long` | 576 candles | 0.0% on `mfi` | 2026-09-06 18:25:54 | `user_data/convergence_logs/BigDrop-05954866-ladder.log` |
| `BollingerBounce` | `spot_long` | 576 candles | 0.0% on `mfi` | 2026-09-06 18:29:09 | `user_data/convergence_logs/BollingerBounce-4f0dc231-ladder.log` |
| `BuyDips` | `spot_long` | 576 candles | 0.0% on `mfi` | 2026-09-06 18:26:03 | `user_data/convergence_logs/BuyDips-2afdb8fb-ladder.log` |
| `DCAGRID` | `spot_long` | 1440 candles | 0.0% on `None` | 2026-09-06 18:08:21 | `user_data/convergence_logs/DCAGRID-8f1a8a50-ladder.log` |
| `DMIPRICEDCAStrategyFuture` | `futures_long_short` | 1440 candles | 0.0% on `None` | 2026-09-06 16:33:08 | `user_data/convergence_logs/DMIPRICEDCAStrategyFuture-5ed3e947-ladder.log` |
| `EMABounce` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-06 18:36:24 | `user_data/convergence_logs/EMABounce-ab0d2db4-ladder.log` |
| `EMACross` | `spot_long` | 30 candles | 0.0% on `ema_short_5` | 2026-09-06 18:26:31 | `user_data/convergence_logs/EMACross-b5f64897-ladder.log` |
| `FLAGS` | `futures_long_short` | 24 candles | 0.0% on `None` | 2026-09-06 18:13:49 | `user_data/convergence_logs/FLAGS-72416802-ladder.log` |
| `FUTURES` | `futures_long_short` | 1440 candles | 0.0% on `ema5` | 2026-09-06 18:32:53 | `user_data/convergence_logs/FUTURES-676b167a-ladder.log` |
| `GRIDDMIPRICEStrategyFutureV5Long` | `futures_long_short` | 1440 candles | 0.0% on `None` | 2026-09-06 16:37:51 | `user_data/convergence_logs/GRIDDMIPRICEStrategyFutureV5Long-93a155ed-ladder.log` |
| `GRIDDMIPRICEStrategyFutureV5Short` | `futures_long_short` | 84 candles | 0.828% on `wt2` | 2026-09-06 16:38:14 | `user_data/convergence_logs/GRIDDMIPRICEStrategyFutureV5Short-0a37b705-ladder.log` |
| `GRIDDMIPRICEStrategySpot` | `futures_long` | 1440 candles | 0.0% on `None` | 2026-09-06 17:58:32 | `user_data/convergence_logs/GRIDDMIPRICEStrategySpot-bfcd5e8a-ladder.log` |
| `HEAD_SHOULDER` | `futures_long_short` | 96 candles | 0.0% on `None` | 2026-09-06 18:13:56 | `user_data/convergence_logs/HEAD_SHOULDER-3272caf5-ladder.log` |
| `KeltnerChannels` | `spot_long` | 576 candles | 0.0% on `adx` | 2026-09-06 18:26:48 | `user_data/convergence_logs/KeltnerChannels-1628032a-ladder.log` |
| `LeoStrategy` | `spot_long` | 540 candles | 0.0% on `ema10` | 2026-09-06 18:31:18 | `user_data/convergence_logs/LeoStrategy-a4770535-ladder.log` |
| `MACD003` | `spot_long` | 576 candles | 0.0% on `mfi` | 2026-09-06 18:29:22 | `user_data/convergence_logs/MACD003-5def5884-ladder.log` |
| `MACDCross` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-06 18:29:32 | `user_data/convergence_logs/MACDCross-c19524f6-ladder.log` |
| `MACDTurn` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-06 18:29:40 | `user_data/convergence_logs/MACDTurn-e059bfc3-ladder.log` |
| `MFI2` | `spot_long` | 576 candles | 0.0% on `adx` | 2026-09-06 18:27:02 | `user_data/convergence_logs/MFI2-9083ee50-ladder.log` |
| `MFIRSICross` | `spot_long` | 288 candles | 0.0% on `mfi` | 2026-09-06 18:28:49 | `user_data/convergence_logs/MFIRSICross-00cbcde3-ladder.log` |
| `MultiActionZone` | `spot_long` | 540 candles | 0.002% on `resample_1440_slowMA` | 2026-09-05 15:21:02 | `user_data/convergence_logs/MultiActionZone-179b96b7-ladder.log` |
| `NDrop` | `spot_long` | 576 candles | 0.0% on `mfi` | 2026-09-06 18:27:19 | `user_data/convergence_logs/NDrop-035a8156-ladder.log` |
| `NSeq` | `spot_long` | 576 candles | 0.0% on `mfi` | 2026-09-06 18:27:29 | `user_data/convergence_logs/NSeq-b0a87061-ladder.log` |
| `Patterns2` | `spot_long` | 288 candles | 0.0% on `mfi` | 2026-09-06 18:27:39 | `user_data/convergence_logs/Patterns2-39f34344-ladder.log` |
| `SARCross` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-06 18:27:47 | `user_data/convergence_logs/SARCross-0c09ed9a-ladder.log` |
| `SUPPORT_RESISTANCE` | `spot_long` | 730 candles | 0.0% on `signal` | 2026-09-06 18:14:10 | `user_data/convergence_logs/SUPPORT_RESISTANCE-e57b787f-ladder.log` |
| `SimpleBollinger` | `spot_long` | 576 candles | 0.0% on `adx` | 2026-09-06 18:27:56 | `user_data/convergence_logs/SimpleBollinger-3b182c17-ladder.log` |
| `Squeeze001` | `spot_long` | 576 candles | 0.0% on `sma` | 2026-09-06 18:28:04 | `user_data/convergence_logs/Squeeze001-f1de728b-ladder.log` |
| `Squeeze002` | `spot_long` | 576 candles | 0.0% on `sma` | 2026-09-06 18:29:58 | `user_data/convergence_logs/Squeeze002-11618dd8-ladder.log` |
| `TRIX_spot` | `spot_long` | 2160 candles | 0.0% on `EMA` | 2026-09-06 18:23:24 | `user_data/convergence_logs/TRIX_spot-b4f2394c-ladder.log` |
| `Trump_LIM` | `spot_long` | 1440 candles | 0.0% on `None` | 2026-09-06 18:17:16 | `user_data/convergence_logs/Trump_LIM-4f331b98-ladder.log` |
| `WTDMIPRICEDCAStrategyFuture` | `futures_long_short` | 288 candles | 0.0% on `wt1` | 2026-09-06 17:59:43 | `user_data/convergence_logs/WTDMIPRICEDCAStrategyFuture-6bd08369-ladder.log` |
| `WTDMIPRICESDCAtrategy` | `spot_long` | 1440 candles | 0.0% on `wt2` | 2026-09-06 17:58:50 | `user_data/convergence_logs/WTDMIPRICESDCAtrategy-f668b499-ladder.log` |
| `bigshort` | `futures_long_short` | 1440 candles | 0.0% on `fastd_15m` | 2026-09-06 18:24:57 | `user_data/convergence_logs/bigshort-ef8d2c90-ladder.log` |
| `chatgpt` | `spot_long` | 336 candles | 0.0% on `stc` | 2026-09-06 18:23:33 | `user_data/convergence_logs/chatgpt-60965168-ladder.log` |
| `gpt_reversal` | `spot_long` | 1440 candles | 0.0% on `rsi_15m` | 2026-09-06 18:25:14 | `user_data/convergence_logs/gpt_reversal-15eecf49-ladder.log` |

## Pending - 59 strategies

No hard failure and no verdict. Evidence is missing, which is
neither a pass nor a fail.

`AlexStrategyFinalV8`, `AlexStrategyFinalV9`, `Astro`, `AutoArimaTripleV1`
`BBKCBounce`, `BTCBigDrop`, `BTCJump`, `BTCMACDCross`
`BTCNDrop`, `BTCNSeq`, `BestSingleAssetPortfolio`, `Bins`
`BlueEyes_MPP_v1`, `ComboHold`, `CryptoFrogNFI2`, `DCADMIPRICEStrategySpot`
`DELTA_NEUTRAL`, `DWTHO`, `DWT_LongShortHO`, `DWT_Predict`
`DWT_Predict2`, `DonchianBounce`, `E0V1EAI`, `ExampleLSTMStrategy`
`FBB_2`, `FileLoadingStrategy`, `GRIDDMIPRICEStrategyFutureV4`, `GRIDDMIPRICEStrategyFutureV5`
`GRIDDMIPRICEStrategyFutureV6`, `GRIDDMIPRICEStrategyFutureV7`, `GodStra`, `Guacamole`
`HLHB`, `Kamaflage`, `MartyEMA`, `MasterMoniGoManiHyperStrategy`
`MultiMa`, `MyStrategyNew10`, `NowoIchimoku1hV1`, `ONS_Portfolio`
`Proton`, `QuickBuyStrategy`, `RLAgentStrategy`, `RLStrategy`
`RebalanceStrategySpot`, `RenkoYolo`, `SARIMAX`, `SMAOPv1_TTF`
`Schism5`, `Schism6`, `Solipsis_v4`, `TEMABounce`
`TuplaBollinger`, `UpSliceStrategy`, `WTHO`, `delist_shorter_strategy`
`haGradient`, `multi_tf`, `tacos1`

## Exclusion unconfirmed - 42 strategies

`excluded` is a verdict, and this audit does not issue one on
somebody else's measurement or on the absence of one. These rows
would have been excluded on exactly that, so they are held here
until a measurement of ours settles them either way. Nothing about
them is hidden by the change of name: the decisive reason and the
basis stay on the row, and the work that would settle it is in
`open_work`.

| Held on | Basis | Strategies |
|---|---|---:|
| `no_verdict_on_lookahead` | `no_finding` | 20 |
| `unclassified` | `no_finding` | 14 |
| `no_verdict_on_lookahead_and_recursive` | `no_finding` | 6 |
| `recursive_bias_unverified` | `no_finding` | 1 |
| `recursive_warmup_refused` | `no_finding` | 1 |

This is not a softening. A row here may well end up excluded - the
38 held on an inherited look-ahead finding probably will, because a
limited environment does not invent bias. It ends up there on our
own evidence or not at all.

## Not passing - 248 strategies, by decisive reason

A row usually fails several gates. It is grouped by the most final
one: a strategy that reads future candles is out however clean its
warm-up is.

**`recursive_bias_unverified` is not a finding.** The parser that
produced most recursion verdicts read the drift at 199 candles rather
than at the strategy's own warm-up, because the analyzer sorts its
columns by value and the strategy's column moves. Across 302 retained
logs the correction flipped 47 verdicts, every one of them from
excluded to clean. A recursion label therefore counts as confirmed
only where the convergence ladder has since failed to settle the row;
everywhere else it says what it is - a record made under a known
defect, awaiting re-measurement.

**Those logs have now been read again.** Of the 124 recursion
records that still have their log, 55 said something other than what
the table showed: 40 turn out to have no verdict at all, because at
the warm-up the strategy declares the indicators are still undefined;
one is clean; and 14 keep their verdict but had the wrong numbers
attached, read off a column belonging to a different warm-up. The
remaining 76 records kept no log and cannot be checked at all, so
they keep what they were given and stay queued for the ladder.

**`WARMUP_NEEDED` is not a finding either.** 134 rows in the frozen
baseline carry `recursive_kind=refused_no_warmup`: the analyzer
declined them because the strategy declares no warm-up, so it never
compared anything. That was being shown as recursion `FOUND` for 47
rows. It now reads `WARMUP_NEEDED`, which is what the record says.

**`wave_b:<n>:superseded` is a run of ours we do not yet trust.**
Wave B supplied a warm-up to those refused rows and re-ran the gate,
but under the parser described above. Re-parsing the 106 wave B logs
that survive overturns 58 of them, every one from FOUND to no
verdict; the runs behind the PASS verdicts kept no log and cannot be
re-parsed at all. Eight admitted rows rest on such a verdict. They
stay admitted - E1 is frozen and this table decides nothing -
and they are queued for the ladder as `recursive_ladder_pending`.

### What each exclusion rests on

The decisive reason names the gate that stopped a row. It does not
say whether that gate produced evidence, and the difference decides
whether the row is finished with or waiting on us.

| Basis | Meaning | Strategies |
|---|---|---:|
| `own_measurement` | a disqualifying result measured here, from this implementation | 248 |

Only `own_measurement` is a closed case. The other three carry the
work that would settle them in `open_work`, and the selftest fails if
one of them carries none.

| Reason | Meaning | Strategies |
|---|---|---:|
| `lookahead_found` | reads data it could not have had at the time | 74 |
| `recursive_bias_found` | indicator value still drifts at every warm-up the ladder can reach | 72 |
| `no_trades_in_full_measurement` | never trades over the full window | 7 |
| `repair_refused_would_invent_strategy` | declares no timeframe, no stoploss, no exit logic, or names a model that no longer exists and cannot be restored; supplying one would measure our invention rather than the author's strategy | 30 |
| `local_module_repair_exhausted` | imports a helper the author shipped beside it; every candidate copy in the corpus either fails to import, would shadow an installed package, or imports cleanly but does not define what the strategy calls | 20 |
| `measured_only_in_freqai_arm` | runs only under its author's own FreqAI configuration, measured separately in that arm; not comparable with the ordinary spot audit | 5 |
| `third_party_package_declined` | needs a Python package this runtime does not install; declined because installing one changes the runtime every other strategy runs under, owner's call 2026-09-04 | 20 |
| `shared_runtime_change_declined` | the fix is understood - pandas' or numpy's own type-coercion rules have tightened - but applying it would touch every strategy's column writes, not just this row's; declined, owner's call 2026-09-04 | 20 |


### Reason by wave

| Reason | `-` | `A_pending_diagnostics` | `B_warmup_refusal` | `C_measurement_recovery` | `D_recursive_drift` | `E0_strict67` | `not_scheduled` |
|---|---|---|---|---|---|---|---|
| `lookahead_found` | 1 | 2 | 0 | 10 | 0 | 0 | 61 |
| `recursive_bias_found` | 10 | 0 | 3 | 18 | 14 | 1 | 26 |
| `no_trades_in_full_measurement` | 0 | 0 | 0 | 7 | 0 | 0 | 0 |
| `repair_refused_would_invent_strategy` | 6 | 1 | 0 | 23 | 0 | 0 | 0 |
| `local_module_repair_exhausted` | 8 | 0 | 0 | 12 | 0 | 0 | 0 |
| `measured_only_in_freqai_arm` | 0 | 0 | 0 | 4 | 0 | 0 | 1 |
| `third_party_package_declined` | 7 | 0 | 0 | 13 | 0 | 0 | 0 |
| `shared_runtime_change_declined` | 1 | 0 | 0 | 15 | 0 | 0 | 4 |

### `lookahead_found` - 74

Reads data it could not have had at the time.

Wave `-` - 1:

`DonchianChannel`

Wave `A_pending_diagnostics` - 2:

`HyperStra_GSN_SMAOnly`, `kalthetank`

Wave `C_measurement_recovery` - 10:

`ARIMASTR`, `ARIMA_15`, `MKR`, `NostalgiaForInfinityNext_ChangeToTower_V5_2`
`NostalgiaForInfinityNext_ChangeToTower_V5_3`, `NostalgiaForInfinityNext_ChangeToTower_V6`, `NostalgiaForInfinityXw`, `Stinkfist`
`bbema`, `ichiV1_Marius`

Wave `not_scheduled` - 61:

`AlexBTK_CT`, `AlexBattleTankKiller`, `AlexBattleTankKillerV3`, `AlexBattleTankKillerV40H`
`Auto_EI_t4c0s`, `BBBreakoutStrategy`, `BreakoutStrategy`, `BuyAllSellAllStrategy`
`CCIStrategy`, `Cci`, `DCBBBounce`, `Dracula`
`EI1_t4c0s_V4`, `EI4_t4c0s_V2`, `EI4_t4c0s_V2_2`, `ElliotWave`
`FVGAdvancedStrategy_V2`, `FakeoutStrategy`, `FrayLIVEBTC15m`, `FrostAuraRandomStrategy`
`HEW`, `Heracles`, `HurstCycle3`, `HyperStra_SMAOnly`
`IchiVwapAdx`, `Leveraged`, `LookaheadStrategy`, `LorentzianClassification`
`MSO`, `MaxSharpePortfolio`, `MinimumVariancePortfolio`, `MomentumRegimeBasket`
`NOTankAi_17`, `NOTankAi_19`, `NWEv6`, `NeuroV1`
`NotAnotherSMAOffsetStrategy_uzi3`, `PolymarketPortfolio`, `Precognition`, `RSIDivTirail`
`ReinforcedQuickie`, `Renko`, `Rsiqui`, `RsiquiV2`
`RsiquiV5`, `RsiquiV5_long_only`, `StarRise_strat3`, `TSPredict`
`Tank1Modulus`, `Tank5ModulusDCA`, `Tank5ModulusDCAV3`, `UziChan`
`UziChan2`, `Zeus`, `custom`, `grad`
`ichiV1`, `qrsi`, `tsp0chicken`, `turbov8`
`wtc`

### `recursive_bias_found` - 72

Indicator value still drifts at every warm-up the ladder can reach.

Wave `-` - 10:

`AlexStrategyFinalV8Hyper`, `AlexStrategyFinalV9Hyper`, `GRIDDMIPRICEStrategyFutureV2`, `GRIDDMIPRICEStrategyFutureV2Both`
`GRIDDMIPRICEStrategyFutureV2Long`, `GRIDDMIPRICEStrategyFutureV2Short`, `SuperReversal_mtf`, `TryEverything`
`mind`, `momentum_tf_divergence`

Wave `B_warmup_refusal` - 3:

`ForexRobootSuperScalper`, `HSI`, `Macd`

Wave `C_measurement_recovery` - 18:

`BBMod1`, `BB_RPB_TSL`, `BB_RPB_TSL_2`, `BB_RPB_TSL_BI`
`BB_RPB_TSL_BIV1`, `BB_RPB_TSL_SMA_Tranz`, `BB_RPB_TSL_SMA_Tranz_TB_1_1_1`, `BB_RPB_TSL_SMA_Tranz_TB_MOD`
`ClucHAnix_BB_RPB_MOD_trailing_buy`, `GeneStrategy`, `GeneStrategy_v2`, `GeneTrader_gen10_1734895087_6007`
`GeneTrader_gen5_1735014093_4541`, `Ichimoku_v35`, `KitchenSink`, `falconTrader`
`newstrategy53`, `newstrategy53_22`

Wave `D_recursive_drift` - 14:

`BigZ0307HO`, `BigZ0407`, `BigZ0407HO`, `BigZ04HO`
`BigZ04HO2`, `BigZ06`, `BigZ07`, `ClucHAnix_BB_RPB_MOD2_ROI`
`ClucHAnix_BB_RPB_MOD_CTT`, `ClucHAnix_BB_RPB_MOD_E0V1E_ROI`, `ObvTrendStrategy`, `flawless_lambo`
`lambotest`, `tacos`

Wave `E0_strict67` - 1:

`MacdStrategy`

Wave `not_scheduled` - 26:

`BB_RPB_TSL_Tranz`, `BB_RPB_TSLmeneguzzo`, `BcmbigzDevelop`, `BcmbigzV1`
`BeastBotXBLR6`, `BeastBotXBLR7`, `BigZ04`, `ClucHAnix5m`
`GKD_CT`, `GoldHedgeZeroMACD`, `HurstCycle7`, `HurstCycleV5RSI`
`HurstCycleV6`, `NOTankAi_15`, `NOTankAi_15_Cleaned`, `NOTankAi_15_Cleaned_v2`
`NostalgiaForInfinityX5`, `NostalgiaForInfinityX6`, `NostalgiaForInfinityX7`, `PrawnstarOBV`
`SimpleHopt1Ashort`, `SimpleHoptS`, `Solipsis5`, `TrendFollowingStrategy`
`TrendRiderStrategy`, `pcb20`

### `no_trades_in_full_measurement` - 7

Never trades over the full window.

Wave `C_measurement_recovery` - 7:

`BreakEven`, `DoesNothingStrategy`, `Miku_PP_v3`, `MyStrategyTemplate`
`Obelisk_3EMA_StochRSI_ATR`, `ViN`, `ep3mas2`

### `repair_refused_would_invent_strategy` - 30

Declares no timeframe, no stoploss, no exit logic, or names a model that no longer exists and cannot be restored; supplying one would measure our invention rather than the author's strategy.

Wave `-` - 6:

`EMA003`, `FBB_ROI`, `FreqaiBinaryClassStrategy`, `FreqaiStrategy_v2`
`TaSearchLevelG15m`, `TrendMomoClassifier`

Wave `A_pending_diagnostics` - 1:

`TGMA`

Wave `C_measurement_recovery` - 23:

`AdaptiveRenkoStrategy`, `Chained`, `ClucCrypROI`, `ClucCrypSlow`
`ClucHAnix_BB_RPB_TraNz`, `CryptoPredictionTraining`, `EnsembleStrategy`, `EnsembleStrategyV1`
`EnsembleStrategyV2`, `FreqaiExampleHybridStrategy`, `FreqaiExampleStrategy`, `LitmusGoodMinMaxClassificationStrategy`
`LitmusMetaStrategy`, `MultiTargetClassifierTestStrategy`, `MultiTargetRegressorTestStrategy`, `NoLost`
`PolymarketLogicalArbStrategy`, `Prediction_Strategy`, `QuickAdapterV3`, `ScalpingCCI`
`SimpleRiskFilterStrategy`, `TrainCatBoostStrategy`, `thetank2`

### `local_module_repair_exhausted` - 20

Imports a helper the author shipped beside it; every candidate copy in the corpus either fails to import, would shadow an installed package, or imports cleanly but does not define what the strategy calls.

Wave `-` - 8:

`Anomaly`, `BBBHold`, `FBB_KalmanSIMD`, `Hammer`
`KeltnerBounce`, `NNPredict`, `NNTC`, `PCA`

Wave `C_measurement_recovery` - 12:

`AdvancedRiskFilterStrategy`, `BB_RPB_3c`, `BaseStrategy`, `BinanceStream`
`DWT`, `DualModelPolymarketPortfolio`, `EmaCrossStrategy`, `MlpSpeculativeStrategy`
`PolymarketMeanReversionStrategy`, `PolymarketMomentumStrategy`, `Solipsis6`, `SolipsisMM`

### `measured_only_in_freqai_arm` - 5

Runs only under its author's own freqai configuration, measured separately in that arm; not comparable with the ordinary spot audit.

Wave `C_measurement_recovery` - 4:

`TankAi`, `TankAiRevival`, `WTAI`, `WTRSIAI`

Wave `not_scheduled` - 1:

`AstroQAV4`

### `third_party_package_declined` - 20

Needs a python package this runtime does not install; declined because installing one changes the runtime every other strategy runs under, owner's call 2026-09-04.

Wave `-` - 7:

`CME`, `Cenderawasih_freqai`, `HMMv3`, `Kalman`
`QuatreMousquetaires`, `kac_index_v1`, `kac_index_v2`

Wave `C_measurement_recovery` - 13:

`CopyLitmusMinMaxBroadClassificationStrategy`, `Enchilada`, `GymStrategy`, `KMM`
`LitmusEntryRollClassificationStrategy`, `LitmusMLDPStrategy`, `LitmusMinMaxBroadClassificationStrategy`, `LitmusMinMaxClassificationStrategy`
`LitmusMinMaxRegretClassificationStrategy`, `LitmusMinMaxSegmentClassificationStrategy`, `LitmusMinMaxStrategy`, `LitmusMinMaxTrendStrategy`
`LitmusSimpleStrategy`

### `shared_runtime_change_declined` - 20

The fix is understood - pandas' or numpy's own type-coercion rules have tightened - but applying it would touch every strategy's column writes, not just this row's; declined, owner's call 2026-09-04.

Wave `-` - 1:

`MultiMA_TSL3b`

Wave `C_measurement_recovery` - 15:

`CombinedBinHAndClucV6H`, `Danke`, `FSupertrendStrategyBTC`, `FSupertrendStrategyETH`
`FastSupertrend`, `FastSupertrendOpt`, `GPR`, `MomentumRegimeBasket15m`
`MostOfAll`, `MultiMA_TSL5`, `PnF`, `SuperTrendPure`
`Supertrend`, `new_turtle`, `new_turtle_roi`

Wave `not_scheduled` - 4:

`BinClucMadDevelop`, `BinClucMadSMADevelop`, `CoreStrategy`, `DIV_v1`

## Expansion wave

| Wave | Strategies |
|---|---:|
| `not_scheduled` | 390 |
| `C_measurement_recovery` | 230 |
| `(none)` | 138 |
| `D_recursive_drift` | 124 |
| `B_warmup_refusal` | 82 |
| `E0_strict67` | 67 |
| `A_pending_diagnostics` | 7 |

## Open work

| Item | Strategies |
|---|---:|
| `recursive_ladder_pending` | 213 |
| `convergence_not_converged_within_ladder` | 72 |
| `needs_a_look` | 47 |
| `lookahead_remeasure_pending` | 40 |
| `convergence_inconclusive` | 16 |
| `to_be_fixed` | 7 |
| `repair_attempted` | 3 |
| `refuse_repair` | 1 |

Per-row detail, including every evidence path, is in
`STRATEGY_STATUS.csv`.
