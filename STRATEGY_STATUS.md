# Strategy status - current evidence for all 1356 rows

**Generated 2026-09-22 10:43:50 by `evidence/strategy_status.py`.** Regenerate it rather than editing it.

**This table decides nothing.** Admission happens only in
`evidence/eligibility_expansion_adjudicate.py`; this is a reading of what has
already been decided, collected from the smoke, bias, full-window,
adjudication and convergence stores.

**Completed full-backtest closure.** 686 rows carry an exact, successful
canonical pooled Stage-7 full-backtest identity (source hash, run profile and
mode timerange). Their `technical_chain_complete=true` closes the technical
work queue, even if a later diagnostic-window amendment made earlier evidence
historical. This does not grant admission or overwrite an exclusion finding.

**Terminal exclusions.** Every row in the `excluded` cohort is closed and
therefore has no `open_work`. `exclusion_unconfirmed` is a distinct, unfinished
cohort: it remains queued because the audit has not earned an exclusion verdict.

**`evidence/REGIME_ELIGIBILITY.csv`'s old E0 baseline is obsolete,
not protected.** As of 2026-09-03 this table stopped treating its
`regime_eligible=true` rows as automatically usable - the recursion
check that produced them used freqtrade's own hardcoded candle
counts, never converted to a strategy's timeframe, not the
calendar-day ladder every other row is held to. Re-measuring it
under this audit's own ladder found rows that did not hold up
(`MacdStrategy` among them, and more since). The file was for a
time described as "frozen and never regenerated", an immutable
historical anchor - that description no longer holds either: it
has in fact been regenerated since (2026-09-14, to surface later
harvest waves to `profile_bias.py`'s own candidate selection), so
there is no remaining reason to treat it as protected or as a
reliable historical snapshot. Each of its rows is decided by the
same C1/C2/C3 criteria as every other row regardless. Original
membership is kept as provenance in `gate_notes`, never as a
reason to skip a check.

**On the run times.** The runners do not stamp a time into their
records, so `last_tested_at` is recovered from what they leave behind:
a result archive's filename, which carries the run's own clock, or
failing that a log file's modification time, which is close but is the
file's time and is labelled `log_mtime` for that reason. 101 of 1356 rows
have neither and are left empty rather than given an invented time.

## Measurement

| | Strategies |
|---|---:|
| in the manifest | 1356 |
| measured at all | 1253 |
| produced trades | 1017 |
| carrying a run time | 1255 |

## Cohort

| Cohort | Strategies |
|---|---:|
| `E1_expanded` | 701 |
| `excluded` | 546 |
| `pending` | 43 |
| `too_few_trades` | 34 |
| `not_a_strategy` | 23 |
| `exclusion_unconfirmed` | 8 |
| `convergence_candidate` | 1 |

## Timeframe and signal family

Both read from the strategy's own source by `strategy_classification.py`,
not measured - see that module's docstring for the marker table and its
limits. `timeframe` is blank on 46 rows the source does not state it for. `strategy_type` can be more than one label - most rows carry two or three - and is blank on 0 rows where no marker matched at all, so its counts below add up to more than 1356.

### Timeframe

| Timeframe | Strategies |
|---|---:|
| `5m` | 779 |
| `1h` | 193 |
| `15m` | 110 |
| `1m` | 100 |
| `4h` | 58 |
| `1d` | 34 |
| `3m` | 18 |
| `30m` | 9 |
| `6h` | 3 |
| `12h` | 2 |
| `2h` | 2 |
| `5h` | 1 |
| `1w` | 1 |

### Signal family

| Type | Strategies |
|---|---:|
| `scalping` | 657 |
| `mean_reversion` | 575 |
| `momentum` | 566 |
| `trend_following` | 314 |
| `volatility_breakout` | 251 |
| `ml_ai` | 203 |
| `grid_dca` | 141 |
| `volume_based` | 139 |
| `unclassified` | 35 |
| `not_applicable` | 23 |
| `always_in_market` | 18 |
| `stat_arb` | 12 |
| `portfolio_rotation` | 4 |
| `ensemble` | 4 |
| `cycle_based` | 4 |
| `multi_indicator` | 3 |
| `pattern_based` | 3 |
| `time_based` | 2 |
| `external_signal` | 1 |
| `no_entry_signal` | 1 |
| `arbitrage` | 1 |

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
| `bear_trend` | `coin_adx >= 25 and coin_minus_di > coin_plus_di` | 78 |
| `bull_trend` | `coin_adx >= 25 and coin_plus_di > coin_minus_di` | 678 |
| `high_vol_shock` | `coin_realized_vol_30d >= 1.291, whatever the DMI state` | 97 |
| `range_choppy` | `coin_adx < 20 and coin_realized_vol_30d >= 0.623` | 424 |
| `range_quiet` | `coin_adx < 20 and coin_realized_vol_30d < 0.623` | 375 |
| `transition` | `20 <= coin_adx < 25` | 78 |

A row may carry more than one phase, and 330 carry none: 209 are model-driven, where the indicators are features of a model and say nothing about which phase it favours, and 121 name no phase-bearing marker at all. Both are left blank rather than given an invented prior - a blank is itself testable, as the prediction that the row is phase-neutral.

`bear_trend` is rare by construction: 1201 of 1356 rows are long-only and a long-only strategy cannot earn in a sustained downtrend, so the direction gate removes it whatever the indicators suggest.

## Test duration

Wall-clock seconds each runner timed its own call at, summed per row
across whichever of the trial-run backtest, the bias-store
look-ahead/recursion pair, a later native look-ahead
re-measurement, the warm-up ladder, a wave B recursion attempt, and
the eight-pair full-window backtest actually ran for it - see
`test_duration` in evidence/strategy_status.py for why this is a sum rather
than a pick-one-source figure. 85 of 1356 rows carry no stamp at all,
either because nothing has run yet or because no runner on that
path records its own time.

Summed across the 1271 rows that do: **125.3 hours** of this audit's own compute so far.

### Slowest 15

| Strategy | Total | Breakdown |
|---|---:|---|
| `MostOfAll` | 10954.7s | backtest=45.1s; full_window=6406.0s; lookahead_remeasured=4470.1s; recursive_ladder=33.5s |
| `ARIMASTR` | 8061.6s | backtest=317.7s; lookahead=1200.0s; lookahead_remeasured=6185.3s; recursive=113.4s; recursive_ladder=245.2s |
| `Hacklemore3` | 7839.3s | backtest=857.1s; lookahead_remeasured=6934.8s; recursive_ladder=47.4s |
| `NNTC_fbb_AdditiveAttention` | 7782.6s | backtest=144.8s; full_window=7637.0s; lookahead=0.8s |
| `Hacklemore` | 7729.0s | backtest=464.1s; lookahead=1200.0s; lookahead_remeasured=6014.3s; recursive=24.0s; recursive_ladder=26.6s |
| `epretrace` | 6188.7s | backtest=65.5s; lookahead=879.9s; lookahead_remeasured=5130.3s; recursive=22.3s; recursive_ladder=61.2s; recursive_wave_b=29.5s |
| `ONS_Portfolio` | 5912.3s | backtest=1800.0s; lookahead_remeasured=4048.1s; recursive_ladder=64.2s |
| `Hacklemore2` | 5638.8s | backtest=3424.2s; lookahead_remeasured=2167.7s; recursive_ladder=46.9s |
| `TrailingBuyStratClucBBRPBMODE` | 5302.7s | backtest=76.3s; full_window=4938.0s; lookahead=269.5s; recursive_ladder=18.9s |
| `ExponentialGradientPortfolio` | 5235.7s | backtest=165.6s; lookahead=1200.0s; lookahead_remeasured=3837.0s; recursive_ladder=33.1s |
| `TrailingBuyStratCluc` | 4881.8s | backtest=57.0s; full_window=4521.8s; lookahead=279.5s; recursive_ladder=23.5s |
| `NostalgiaForInfinityX4` | 4213.0s | backtest=74.7s; lookahead=427.5s; lookahead_remeasured=3667.1s; recursive_ladder=43.7s |
| `NostalgiaForInfinityX3` | 4170.7s | backtest=29.5s; lookahead=412.9s; lookahead_remeasured=3682.6s; recursive_ladder=45.7s |
| `UltraSmartStrategy` | 3600.3s | backtest=3600.3s |
| `Strategy001_custom_exit` | 3446.9s | backtest=3280.9s; lookahead_remeasured=87.9s; recursive_ladder=52.2s; recursive_wave_b=25.9s |

## The order the checks run in

The order is not arbitrary; each step needs what the one before it
produces.

**1. Trial run.** One month over eight pairs, widened to three months
and then one year while fewer than ten trades are observed: does the
strategy start, and does it trade. A strategy that fails here is `open`, never
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
from the recorded adjudication; this step decides whether an admitted
strategy is testable for the pooled market-phase benchmark.

## What excludes a strategy

The complete machine-readable list is generated in
`evidence/exclusion_criteria_list.md`. Each criterion rests on evidence
from this audit's recorded runtime.

| | Criterion | Machine test |
|---|---|---|
| C1 | Look-ahead found | `lookahead == "FOUND"` and `lookahead_evidence == "native"` |
| C2 | Recursion found | `recursive_evidence == "convergence:not_settled"` |
| C3 | Never trades | `no_trades_in_full_measurement` with `trade_evidence == "full_window"` |
| C10 | Canonical pooled full backtest not testable |
`full_backtest_status in {failed, resource_inconclusive, timeout}` |

**A strategy satisfying none of the applicable criteria is not excluded.** It is
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

The criteria in full are in `evidence/exclusion_criteria_list.md`, and every
repair route taken - with the message freqtrade gave beforehand - in
`evidence/repair_measures_list.md`. Both are written by this same command,
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
| Trial run (`profile_smoke`) | 1 month -> 3 months -> 1 year; stop at 10 trades | all 8 |
| Bias check, spot | `20200301-20200601`, three months | `BTC/USDT` only |
| Bias check, futures | `20200301-20200601`, three months | `BTC/USDT:USDT` only |
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
trade. It begins with one month and, below ten trades, follows the
fixed three-month and one-year rungs. What it earns is measured later,
over the full window.

The warm-up ladder steps in days - 1, 2, 7, 14, 30, 90, 365 - converted
to each strategy's own timeframe, and accepts a rung once every
indicator stays inside 1.0 percent.

## How freqtrade was called

A result is not reproducible from its verdict alone, so each row
carries the command it was produced by. **`recorded`** is the argv that
actually ran. **`reconstructed`** is derived from the run profile and
the window, because nothing stored the call before 2026-09-01; it is
labelled because a reconstruction is a different claim from a
recording. 2530 of 3981 commands are recorded so far, and every new run
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

## Passing - 701 strategies

Every original gate returned `PASS`: measured in its native mode,
produced trades, clean look-ahead and recursion, complete candle
coverage, no published trap.

| Strategy | Profile | Cohort | Trades | Recursive evidence | Tested | Results |
|---|---|---|---:|---|---|---|
| `ADXDM` | `spot_long` | `E1_expanded` | 23 | `convergence:288:warmup_supplied` | 2026-09-06 18:28:13 | [archive](user_data/profile_smoke/ADXDM-eef844db-2026-09-06_18-28-13.zip) [log](user_data/convergence_logs/ADXDM-eef844db-ladder.log) |
| `ADXMomentum` | `spot_long` | `E1_expanded` | 2 | `convergence:336:warmup_supplied` | 2026-09-06 14:47:45 | [archive](user_data/profile_smoke/ADXMomentum-d748d610-2026-09-06_14-47-45.zip) [log](user_data/convergence_logs/ADXMomentum-ladder.log) |
| `ADX_15M_USDT` | `spot_long` | `E1_expanded` | 165 | `convergence:672:warmup_supplied` | 2026-09-01 19:31:10 | [archive](user_data/profile_smoke/ADX_15M_USDT-2026-09-01_19-31-10.zip) [log](user_data/convergence_logs/ADX_15M_USDT-ladder.log) |
| `ADX_15M_USDT2` | `spot_long` | `E1_expanded` | 178 | `convergence:672:warmup_supplied` | 2026-09-01 19:31:48 | [archive](user_data/profile_smoke/ADX_15M_USDT2-2026-09-01_19-31-48.zip) [log](user_data/convergence_logs/ADX_15M_USDT2-ladder.log) |
| `ASDTSRockwellTrading` | `spot_long` | `E1_expanded` | 13402 | `convergence:288:warmup_supplied` | 2026-09-05 11:59:26 | [archive](user_data/profile_smoke/ASDTSRockwellTrading-a0a64ac9-2026-09-05_11-59-26.zip) [log](user_data/convergence_logs/ASDTSRockwellTrading-ladder.log) |
| `ActionZone` | `spot_long` | `E1_expanded` | 511 | `convergence:90:warmup_supplied` | 2026-09-05 13:51:31 | [archive](user_data/profile_smoke/ActionZone-e0687d36-2026-09-05_13-51-31.zip) [log](user_data/convergence_logs/ActionZone-ladder.log) |
| `AdaptiveMAStrategy` | `spot_long` | `E1_expanded` | 12604 | `convergence:288:warmup_supplied` | 2026-09-09 21:21:26 | [archive](user_data/profile_smoke/AdaptiveMAStrategy-dcd0265a-2026-09-09_21-21-26.zip) [log](user_data/convergence_logs/AdaptiveMAStrategy-ladder.log) |
| `AdaptiveRegime` | `futures_long_short` | `E1_expanded` | 16 | `convergence:220` | 2026-09-08 18:40:02 | [archive](user_data/profile_smoke/AdaptiveRegime-90b67ba4-2026-09-08_18-40-02.zip) [log](user_data/convergence_logs/AdaptiveRegime-90b67ba4-ladder.log) |
| `AdaptiveRegimeLong` | `spot_long` | `E1_expanded` | 163 | `convergence:365:warmup_supplied` | 2026-09-14 23:41:27 | [archive](user_data/profile_smoke/AdaptiveRegimeLong-aea59d43-smoke_20200301_20210301-fca63e6f-2026-09-14_23-41-27.zip) [log](user_data/convergence_logs/AdaptiveRegimeLong-aea59d43-ladder.log) |
| `AdxSmas` | `spot_long` | `E1_expanded` | 5822 | `convergence:336:warmup_supplied` | 2026-09-05 13:53:08 | [archive](user_data/profile_smoke/AdxSmas-fe8ff69f-2026-09-05_13-53-08.zip) [log](user_data/convergence_logs/AdxSmas-ladder.log) |
| `AdxSmasS` | `futures_short` | `E1_expanded` | 74 | `convergence:336:warmup_supplied` | 2026-09-01 13:34:00 | [log](user_data/convergence_logs/AdxSmasS-ladder.log) |
| `AdxStrengthStrategy` | `spot_long` | `E1_expanded` | 11385 | `convergence:288:warmup_supplied` | 2026-09-09 21:23:43 | [archive](user_data/profile_smoke/AdxStrengthStrategy-43ff628d-2026-09-09_21-23-43.zip) [log](user_data/convergence_logs/AdxStrengthStrategy-ladder.log) |
| `AlligatorStrat` | `spot_long` | `E1_expanded` | 48 | `convergence:540:warmup_supplied` | 2026-09-01 19:32:25 | [archive](user_data/profile_smoke/AlligatorStrat-2026-09-01_19-32-25.zip) [log](user_data/convergence_logs/AlligatorStrat-ladder.log) |
| `AlligatorStrategy` | `spot_long` | `E1_expanded` | 1654 | `convergence:720:warmup_supplied` | 2026-09-05 13:55:04 | [archive](user_data/profile_smoke/AlligatorStrategy-d98e241f-2026-09-05_13-55-04.zip) [log](user_data/convergence_logs/AlligatorStrategy-ladder.log) |
| `AlmgrenChrissStrategy` | `futures_long_short` | `E1_expanded` | 818 | `convergence:192:warmup_supplied` | 2026-09-01 13:01:08 | [log](user_data/convergence_logs/AlmgrenChrissStrategy-ladder.log) |
| `AlwaysBuy` | `spot_long` | `E1_expanded` | 23145 | `convergence:288:warmup_supplied` | 2026-09-06 04:17:40 | [archive](user_data/profile_smoke/AlwaysBuy-3d49f615-2026-09-06_04-17-40.zip) [log](user_data/convergence_logs/AlwaysBuy-ladder.log) |
| `AntigravityGridStrategy` | `spot_long` | `E1_expanded` | 172 | `convergence:672:warmup_supplied` | 2026-09-08 17:17:10 | [archive](user_data/profile_smoke/AntigravityGridStrategy-c15a2d4c-2026-09-08_17-17-10.zip) [log](user_data/convergence_logs/AntigravityGridStrategy-c15a2d4c-ladder.log) |
| `Apollo11` | `spot_long` | `E1_expanded` | 4996 | `convergence:1344:warmup_supplied` | 2026-09-05 14:02:59 | [archive](user_data/profile_smoke/Apollo11-ec6cf35d-2026-09-05_14-02-59.zip) [log](user_data/convergence_logs/Apollo11-ladder.log) |
| `Argrelextrema` | `futures_long_short` | `E1_expanded` | 5473 | `convergence:30` | 2026-09-08 12:38:07 | [archive](user_data/profile_smoke/Argrelextrema-0ba99988-2026-09-08_12-38-07.zip) [log](user_data/convergence_logs/Argrelextrema-0ba99988-ladder.log) |
| `AroonTrendStrategy` | `spot_long` | `E1_expanded` | 14536 | `convergence:288:warmup_supplied` | 2026-09-09 21:26:49 | [archive](user_data/profile_smoke/AroonTrendStrategy-c552fb5d-2026-09-09_21-26-49.zip) [log](user_data/convergence_logs/AroonTrendStrategy-ladder.log) |
| `AtrTrailingStopStrategy` | `spot_long` | `E1_expanded` | 12504 | `convergence:288:warmup_supplied` | 2026-09-09 21:29:16 | [archive](user_data/profile_smoke/AtrTrailingStopStrategy-dde18ecb-2026-09-09_21-29-16.zip) [log](user_data/convergence_logs/AtrTrailingStopStrategy-ladder.log) |
| `AverageStrategy` | `spot_long` | `E1_expanded` | 2472 | `convergence:84:warmup_supplied` | 2026-09-05 13:58:36 | [archive](user_data/profile_smoke/AverageStrategy-458e95dd-2026-09-05_13-58-36.zip) [log](user_data/convergence_logs/AverageStrategy-ladder.log) |
| `AwesomeMacd` | `spot_long` | `E1_expanded` | 4234 | `convergence:336:warmup_supplied` | 2026-09-05 12:54:07 | [archive](user_data/profile_smoke/AwesomeMacd-a1b857b0-2026-09-05_12-54-07.zip) [log](user_data/convergence_logs/AwesomeMacd-ladder.log) |
| `BB10fall` | `spot_long` | `E1_expanded` | 50 | `convergence:168:warmup_supplied` | 2026-09-05 15:09:31 | [archive](user_data/profile_smoke/BB10fall-cef5331b-2026-09-05_15-09-31.zip) [log](user_data/convergence_logs/BB10fall-cef5331b-ladder.log) |
| `BBKCBounce` | `spot_long` | `E1_expanded` | 52 | `convergence:288:warmup_supplied` | 2026-09-09 07:47:51 | [archive](user_data/profile_smoke/BBKCBounce-4161a6f7-2026-09-09_07-47-51.zip) [log](user_data/convergence_logs/BBKCBounce-4161a6f7-ladder.log) |
| `BBMod` | `spot_long` | `E1_expanded` | 300 | `convergence:2016:warmup_supplied` | 2026-09-06 15:09:06 | [archive](user_data/profile_smoke/BBMod-c3880bce-2026-09-06_15-09-06.zip) [log](user_data/convergence_logs/BBMod-ladder.log) |
| `BBRSI` | `spot_long` | `E1_expanded` | 11 | `convergence:168:warmup_supplied` | 2026-09-04 10:32:03 | [archive](user_data/profile_smoke/BBRSI-0d31007a-2026-09-04_10-32-03.zip) [log](user_data/convergence_logs/BBRSI-0d31007a-ladder.log) |
| `BBRSI2` | `spot_long` | `E1_expanded` | 1178 | `convergence:1440:warmup_supplied` | 2026-09-09 16:30:03 | [archive](user_data/profile_smoke/BBRSI2-86823e82-2026-09-09_16-30-03.zip) [log](user_data/convergence_logs/BBRSI2-ladder.log) |
| `BBRSI21` | `spot_long` | `E1_expanded` | 4804 | `convergence:288:warmup_supplied` | 2026-09-06 04:21:04 | [archive](user_data/profile_smoke/BBRSI21-8d3cd1cd-2026-09-06_04-21-04.zip) [log](user_data/convergence_logs/BBRSI21-ladder.log) |
| `BBRSI3366` | `spot_long` | `E1_expanded` | 19791 | `convergence:288:warmup_supplied` | 2026-09-06 04:25:48 | [archive](user_data/profile_smoke/BBRSI3366-5eaa7494-2026-09-06_04-25-48.zip) [log](user_data/convergence_logs/BBRSI3366-ladder.log) |
| `BBRSI4cust` | `spot_long` | `E1_expanded` | 14971 | `convergence:192:warmup_supplied` | 2026-09-06 04:34:08 | [archive](user_data/profile_smoke/BBRSI4cust-15ae73f3-2026-09-06_04-34-08.zip) [log](user_data/convergence_logs/BBRSI4cust-ladder.log) |
| `BBRSINaiveStrategy` | `spot_long` | `E1_expanded` | 17103 | `convergence:192:warmup_supplied` | 2026-09-06 04:28:43 | [archive](user_data/profile_smoke/BBRSINaiveStrategy-06e452ee-2026-09-06_04-28-43.zip) [log](user_data/convergence_logs/BBRSINaiveStrategy-ladder.log) |
| `BBRSIOptim2020Strategy` | `spot_long` | `E1_expanded` | 25910 | `convergence:288:warmup_supplied` | 2026-09-06 04:31:58 | [archive](user_data/profile_smoke/BBRSIOptim2020Strategy-953f76a1-2026-09-06_04-31-58.zip) [log](user_data/convergence_logs/BBRSIOptim2020Strategy-ladder.log) |
| `BBRSIOptimStrategy` | `spot_long` | `E1_expanded` | 8813 | `convergence:288:warmup_supplied` | 2026-09-06 04:39:54 | [archive](user_data/profile_smoke/BBRSIOptimStrategy-17edd828-2026-09-06_04-39-54.zip) [log](user_data/convergence_logs/BBRSIOptimStrategy-ladder.log) |
| `BBRSIOptimizedStrategy` | `spot_long` | `E1_expanded` | 27772 | `convergence:288:warmup_supplied` | 2026-09-05 14:03:48 | [archive](user_data/profile_smoke/BBRSIOptimizedStrategy-79f2af5e-2026-09-05_14-03-48.zip) [log](user_data/convergence_logs/BBRSIOptimizedStrategy-ladder.log) |
| `BBRSIStrategy` | `spot_long` | `E1_expanded` | 10162 | `convergence:192:warmup_supplied` | 2026-09-06 04:38:08 | [archive](user_data/profile_smoke/BBRSIStrategy-6bd56231-2026-09-06_04-38-08.zip) [log](user_data/convergence_logs/BBRSIStrategy-ladder.log) |
| `BBRSITV` | `spot_long` | `E1_expanded` | 11 | `convergence:2016:warmup_supplied` | 2026-09-17 12:12:52 | [archive](user_data/profile_smoke/BBRSITV-1794e5d4-smoke_20200301_20200401-b4807b77-2026-09-17_12-12-52.zip) [log](user_data/convergence_logs/BBRSITV-ladder.log) |
| `BBRSITV4` | `spot_long` | `E1_expanded` | 335 | `convergence:2016:warmup_supplied` | 2026-09-14 23:41:53 | [archive](user_data/profile_smoke/BBRSITV4-43cc369e-smoke_20200301_20200601-9c543975-2026-09-14_23-41-53.zip) [log](user_data/convergence_logs/BBRSITV4-43cc369e-ladder.log) |
| `BBRSITV5` | `spot_long` | `E1_expanded` | 493 | `convergence:2016:warmup_supplied` | 2026-09-14 23:42:00 | [archive](user_data/profile_smoke/BBRSITV5-49193951-smoke_20200301_20200401-b4807b77-2026-09-14_23-42-00.zip) [log](user_data/convergence_logs/BBRSITV5-49193951-ladder.log) |
| `BBRSIoriginal` | `spot_long` | `E1_expanded` | 47 | `convergence:168:warmup_supplied` | 2026-09-01 19:33:39 | [archive](user_data/profile_smoke/BBRSIoriginal-2026-09-01_19-33-39.zip) [log](user_data/convergence_logs/BBRSIoriginal-ladder.log) |
| `BBRSIv2` | `spot_long` | `E1_expanded` | 550 | `convergence:192:warmup_supplied` | 2026-09-06 04:45:47 | [archive](user_data/profile_smoke/BBRSIv2-ef4f5b04-2026-09-06_04-45-47.zip) [log](user_data/convergence_logs/BBRSIv2-ladder.log) |
| `BB_RPB_TSL_RNG` | `spot_long` | `E1_expanded` | 639 | `convergence:2016:warmup_supplied` | 2026-09-05 14:07:19 | [archive](user_data/profile_smoke/BB_RPB_TSL_RNG-3a0f18b7-2026-09-05_14-07-19.zip) [log](user_data/convergence_logs/BB_RPB_TSL_RNG-ladder.log) |
| `BB_RPB_TSL_RNG_2` | `spot_long` | `E1_expanded` | 635 | `convergence:2016:warmup_supplied` | 2026-09-06 04:43:24 | [archive](user_data/profile_smoke/BB_RPB_TSL_RNG_2-e03b9f25-2026-09-06_04-43-24.zip) [log](user_data/convergence_logs/BB_RPB_TSL_RNG_2-ladder.log) |
| `BB_RPB_TSL_RNG_TBS` | `spot_long` | `E1_expanded` | 639 | `convergence:2016:warmup_supplied` | 2026-09-05 14:08:46 | [archive](user_data/profile_smoke/BB_RPB_TSL_RNG_TBS-055d0268-2026-09-05_14-08-46.zip) [log](user_data/convergence_logs/BB_RPB_TSL_RNG_TBS-ladder.log) |
| `BB_RPB_TSL_RNG_TBS_GOLD` | `spot_long` | `E1_expanded` | 796 | `convergence:2016:warmup_supplied` | 2026-09-05 14:10:33 | [archive](user_data/profile_smoke/BB_RPB_TSL_RNG_TBS_GOLD-c7cbefbb-2026-09-05_14-10-33.zip) [log](user_data/convergence_logs/BB_RPB_TSL_RNG_TBS_GOLD-ladder.log) |
| `BB_RPB_TSL_RNG_VWAP` | `spot_long` | `E1_expanded` | 1010 | `convergence:2016:warmup_supplied` | 2026-09-06 04:46:37 | [archive](user_data/profile_smoke/BB_RPB_TSL_RNG_VWAP-ca3d4565-2026-09-06_04-46-37.zip) [log](user_data/convergence_logs/BB_RPB_TSL_RNG_VWAP-ladder.log) |
| `BB_RPB_TSL_c7c477d_20211030` | `spot_long` | `E1_expanded` | 354 | `convergence:2016:warmup_supplied` | 2026-09-07 03:35:11 | [archive](user_data/profile_smoke/BB_RPB_TSL_c7c477d_20211030-2ca1ddc5-2026-09-07_03-35-11.zip) [log](user_data/convergence_logs/BB_RPB_TSL_c7c477d_20211030-2ca1ddc5-ladder.log) |
| `BB_RSI` | `spot_long` | `E1_expanded` | 421 | `convergence:168:warmup_supplied` | 2026-09-01 19:34:17 | [archive](user_data/profile_smoke/BB_RSI-2026-09-01_19-34-17.zip) [log](user_data/convergence_logs/BB_RSI-ladder.log) |
| `BB_RTR` | `spot_long` | `E1_expanded` | 760 | `convergence:2016:warmup_supplied` | 2026-09-05 23:27:42 | [archive](user_data/profile_smoke/BB_RTR-847a19ce-2026-09-05_23-27-42.zip) [log](user_data/convergence_logs/BB_RTR-ladder.log) |
| `BB_Strategy04` | `spot_long` | `E1_expanded` | 56 | `convergence:168:warmup_supplied` | 2026-09-01 19:34:54 | [archive](user_data/profile_smoke/BB_Strategy04-2026-09-01_19-34-54.zip) [log](user_data/convergence_logs/BB_Strategy04-ladder.log) |
| `BBands` | `spot_long` | `E1_expanded` | 13538 | `convergence:1440:warmup_supplied` | 2026-09-09 16:15:53 | [archive](user_data/profile_smoke/BBands-62f4821e-2026-09-09_16-15-53.zip) [log](user_data/convergence_logs/BBands-ladder.log) |
| `BBandsRSI` | `spot_long` | `E1_expanded` | 16374 | `convergence:288:warmup_supplied` | 2026-09-05 14:13:49 | [archive](user_data/profile_smoke/BBandsRSI-e3e39ce3-2026-09-05_14-13-49.zip) [log](user_data/convergence_logs/BBandsRSI-ladder.log) |
| `BBlower` | `spot_long` | `E1_expanded` | 1471 | `convergence:576:warmup_supplied` | 2026-09-06 04:49:19 | [archive](user_data/profile_smoke/BBlower-f669ea81-2026-09-06_04-49-19.zip) [log](user_data/convergence_logs/BBlower-ladder.log) |
| `Babico_SMA5xBBmid` | `spot_long` | `E1_expanded` | 69 | `convergence:30:warmup_supplied` | 2026-09-06 04:47:32 | [archive](user_data/profile_smoke/Babico_SMA5xBBmid-bb288854-2026-09-06_04-47-32.zip) [log](user_data/convergence_logs/Babico_SMA5xBBmid-ladder.log) |
| `Bandtastic` | `spot_long` | `E1_expanded` | 25093 | `convergence:1344:warmup_supplied` | 2026-09-06 01:41:58 | [archive](user_data/profile_smoke/Bandtastic-0393a67b-2026-09-06_01-41-58.zip) [log](user_data/convergence_logs/Bandtastic-ladder.log) |
| `BbRoi` | `spot_long` | `E1_expanded` | 393 | `convergence:1344:warmup_supplied` | 2026-09-01 19:35:31 | [archive](user_data/profile_smoke/BbRoi-2026-09-01_19-35-31.zip) [log](user_data/convergence_logs/BbRoi-ladder.log) |
| `BbWidthExpansionStrategy` | `spot_long` | `E1_expanded` | 12674 | `convergence:288:warmup_supplied` | 2026-09-09 21:31:30 | [archive](user_data/profile_smoke/BbWidthExpansionStrategy-b4818e74-2026-09-09_21-31-30.zip) [log](user_data/convergence_logs/BbWidthExpansionStrategy-ladder.log) |
| `BbandRsi` | `spot_long` | `E1_expanded` | 1262 | `convergence:1440:warmup_supplied` | 2026-09-09 16:16:37 | [archive](user_data/profile_smoke/BbandRsi-6dcf5b91-2026-09-09_16-16-37.zip) [log](user_data/convergence_logs/BbandRsi-6dcf5b91-ladder.log) |
| `BbandRsiRolling` | `spot_long` | `E1_expanded` | 15002 | `convergence:288:warmup_supplied` | 2026-09-05 14:24:52 | [archive](user_data/profile_smoke/BbandRsiRolling-f1489cee-2026-09-05_14-24-52.zip) [log](user_data/convergence_logs/BbandRsiRolling-ladder.log) |
| `Best5m` | `futures_long_short` | `E1_expanded` | 33 | `convergence:288:warmup_supplied` | 2026-09-14 19:21:44 | [archive](user_data/profile_smoke/Best5m-b4504e64-smoke_20200301_20200401-b4807b77-2026-09-14_19-21-44.zip) [log](user_data/convergence_logs/Best5m-b4504e64-ladder.log) |
| `BigDrop` | `spot_long` | `E1_expanded` | 207 | `convergence:576:warmup_supplied` | 2026-09-06 18:25:54 | [archive](user_data/profile_smoke/BigDrop-05954866-2026-09-06_18-25-54.zip) [log](user_data/convergence_logs/BigDrop-05954866-ladder.log) |
| `BigPete` | `spot_long` | `E1_expanded` | 566 | `convergence:288:warmup_supplied` | 2026-09-06 15:08:15 | [archive](user_data/profile_smoke/BigPete-b194f963-2026-09-06_15-08-15.zip) [log](user_data/convergence_logs/BigPete-ladder.log) |
| `BigTrader` | `spot_long` | `E1_expanded` | 133 | `convergence:60` | 2026-09-06 02:54:32 | [archive](user_data/profile_smoke/BigTrader-fc53f0ba-2026-09-06_02-54-32.zip) [log](user_data/convergence_logs/BigTrader-ladder.log) |
| `BigWill` | `spot_long` | `E1_expanded` | 33 | `convergence:2160:warmup_supplied` | 2026-09-06 18:17:28 | [archive](user_data/profile_smoke/BigWill-387f07ca-2026-09-06_18-17-28.zip) [log](user_data/convergence_logs/BigWill-387f07ca-ladder.log) |
| `BigZ03` | `spot_long` | `E1_expanded` | 718 | `convergence:2016:warmup_supplied` | 2026-09-06 05:00:57 | [archive](user_data/profile_smoke/BigZ03-73f3ab21-2026-09-06_05-00-57.zip) [log](user_data/convergence_logs/BigZ03-ladder.log) |
| `BigZ03HO` | `spot_long` | `E1_expanded` | 10851 | `convergence:2016:warmup_supplied` | 2026-09-07 13:42:10 | [archive](user_data/profile_smoke/BigZ03HO-223e9e10-2026-09-07_13-42-10.zip) [log](user_data/convergence_logs/BigZ03HO-ladder.log) |
| `BigZ04_TSL3` | `spot_long` | `E1_expanded` | 1152 | `convergence:2016:warmup_supplied` | 2026-09-05 14:23:34 | [archive](user_data/profile_smoke/BigZ04_TSL3-da25b418-2026-09-05_14-23-34.zip) [log](user_data/convergence_logs/BigZ04_TSL3-ladder.log) |
| `BigZ04_TSL4` | `spot_long` | `E1_expanded` | 1237 | `convergence:288` | 2026-09-05 12:02:28 | [archive](user_data/profile_smoke/BigZ04_TSL4-e8864ca5-2026-09-05_12-02-28.zip) [log](user_data/convergence_logs/BigZ04_TSL4-ladder.log) |
| `BigZ07Next` | `spot_long` | `E1_expanded` | 1337 | `convergence:2016:warmup_supplied` | 2026-09-07 13:35:13 | [archive](user_data/profile_smoke/BigZ07Next-49314d41-2026-09-07_13-35-13.zip) [log](user_data/convergence_logs/BigZ07Next-ladder.log) |
| `BigZ07Next2` | `spot_long` | `E1_expanded` | 1313 | `convergence:2016:warmup_supplied` | 2026-09-07 13:32:12 | [archive](user_data/profile_smoke/BigZ07Next2-746d2c59-2026-09-07_13-32-12.zip) [log](user_data/convergence_logs/BigZ07Next2-ladder.log) |
| `BinClucMad` | `spot_long` | `E1_expanded` | 1962 | `convergence:2016:warmup_supplied` | 2026-09-06 05:11:06 | [archive](user_data/profile_smoke/BinClucMad-22180ec8-2026-09-06_05-11-06.zip) [log](user_data/convergence_logs/BinClucMad-ladder.log) |
| `BinClucMadDevelop` | `spot_long` | `E1_expanded` | 77 | `convergence:2016:warmup_supplied` | 2026-09-09 09:28:11 | [archive](user_data/profile_smoke/BinClucMadDevelop-43196dbd-2026-09-09_09-28-11.zip) [log](user_data/convergence_logs/BinClucMadDevelop-ladder.log) |
| `BinClucMadSMADevelop` | `spot_long` | `E1_expanded` | 50 | `convergence:2016:warmup_supplied` | 2026-09-09 09:27:51 | [archive](user_data/profile_smoke/BinClucMadSMADevelop-485890ae-2026-09-09_09-27-51.zip) [log](user_data/convergence_logs/BinClucMadSMADevelop-ladder.log) |
| `BinClucMadV1` | `spot_long` | `E1_expanded` | 933 | `convergence:2016:warmup_supplied` | 2026-09-07 03:46:21 | [archive](user_data/profile_smoke/BinClucMadV1-708fb3e3-2026-09-07_03-46-21.zip) [log](user_data/convergence_logs/BinClucMadV1-ladder.log) |
| `BinHV27` | `spot_long` | `E1_expanded` | 9671 | `convergence:576:warmup_supplied` | 2026-09-05 14:26:48 | [archive](user_data/profile_smoke/BinHV27-d117151b-2026-09-05_14-26-48.zip) [log](user_data/convergence_logs/BinHV27-ladder.log) |
| `BinHV27F` | `futures_long` | `E1_expanded` | 154 | `convergence:576:warmup_supplied` | 2026-09-02 06:53:08 | [log](user_data/convergence_logs/BinHV27F-ladder.log) |
| `BinHV27_combined` | `futures_long_short` | `E1_expanded` | 57 | `convergence:576:warmup_supplied` | 2026-09-14 19:21:50 | [archive](user_data/profile_smoke/BinHV27_combined-9aaca5ac-smoke_20200301_20200401-b4807b77-2026-09-14_19-21-50.zip) [log](user_data/convergence_logs/BinHV27_combined-9aaca5ac-ladder.log) |
| `BinHV27_short` | `futures_long_short` | `E1_expanded` | 5 | `convergence:576:warmup_supplied` | 2026-09-03 19:04:53 | [log](user_data/convergence_logs/BinHV27_short-ladder.log) |
| `BinHV27_werkkrew` | `spot_long` | `E1_expanded` | 127 | `convergence:576:warmup_supplied` | 2026-09-16 16:07:57 | [archive](user_data/profile_smoke/BinHV27_werkkrew-3a997e27-smoke_20200301_20200401-b4807b77-2026-09-16_16-07-57.zip) [log](user_data/convergence_logs/BinHV27_werkkrew-ladder.log) |
| `BinHV45` | `spot_long` | `E1_expanded` | 92 | `convergence:1440:warmup_supplied` | 2026-09-09 16:14:58 | [archive](user_data/profile_smoke/BinHV45-db2dd482-2026-09-09_16-14-58.zip) [log](user_data/convergence_logs/BinHV45-ladder.log) |
| `BinHV45HO` | `spot_long` | `E1_expanded` | 59 | `convergence:1440:warmup_supplied` | 2026-09-09 16:27:13 | [archive](user_data/profile_smoke/BinHV45HO-2a444e3c-2026-09-09_16-27-13.zip) [log](user_data/convergence_logs/BinHV45HO-ladder.log) |
| `BinHV45_kanaxe` | `spot_long` | `E1_expanded` | 184 | `convergence:1440:warmup_supplied` | 2026-09-09 16:27:50 | [archive](user_data/profile_smoke/BinHV45_kanaxe-5d56a0a8-2026-09-09_16-27-50.zip) [log](user_data/convergence_logs/BinHV45_kanaxe-ladder.log) |
| `BinHV45_stash` | `spot_long` | `E1_expanded` | 179 | `convergence:1440:warmup_supplied` | 2026-09-09 16:28:31 | [archive](user_data/profile_smoke/BinHV45_stash-2477766f-2026-09-09_16-28-31.zip) [log](user_data/convergence_logs/BinHV45_stash-ladder.log) |
| `BinHV45_werkkrew` | `spot_long` | `E1_expanded` | 74 | `convergence:1440:warmup_supplied` | 2026-09-09 16:29:10 | [archive](user_data/profile_smoke/BinHV45_werkkrew-1637ab87-2026-09-09_16-29-10.zip) [log](user_data/convergence_logs/BinHV45_werkkrew-ladder.log) |
| `BinMfiBTCv5003` | `spot_long` | `E1_expanded` | 167 | `convergence:288:warmup_supplied` | 2026-09-05 23:30:28 | [archive](user_data/profile_smoke/BinMfiBTCv5003-e666be24-2026-09-05_23-30-28.zip) [log](user_data/convergence_logs/BinMfiBTCv5003-ladder.log) |
| `BollingerBandStrategy` | `spot_long` | `E1_expanded` | 12758 | `convergence:480:warmup_supplied` | 2026-09-07 16:01:24 | [archive](user_data/profile_smoke/BollingerBandStrategy-e77a29cb-2026-09-07_16-01-24.zip) [log](user_data/convergence_logs/BollingerBandStrategy-ladder.log) |
| `BollingerBounce` | `spot_long` | `E1_expanded` | 60 | `convergence:576:warmup_supplied` | 2026-09-06 18:29:09 | [archive](user_data/profile_smoke/BollingerBounce-4f0dc231-2026-09-06_18-29-09.zip) [log](user_data/convergence_logs/BollingerBounce-4f0dc231-ladder.log) |
| `BollingerBounceStrategy` | `spot_long` | `E1_expanded` | 9836 | `convergence:576:warmup_supplied` | 2026-09-09 21:33:39 | [archive](user_data/profile_smoke/BollingerBounceStrategy-19dcef82-2026-09-09_21-33-39.zip) [log](user_data/convergence_logs/BollingerBounceStrategy-ladder.log) |
| `BollingerBounce_Shorts` | `futures_short` | `E1_expanded` | 76 | `convergence:576:warmup_supplied` | 2026-09-14 19:21:55 | [archive](user_data/profile_smoke/BollingerBounce_Shorts-2011edaf-smoke_20200301_20200401-b4807b77-2026-09-14_19-21-55.zip) [log](user_data/convergence_logs/BollingerBounce_Shorts-2011edaf-ladder.log) |
| `BopTrendStrategy` | `spot_long` | `E1_expanded` | 12383 | `convergence:288:warmup_supplied` | 2026-09-09 21:36:13 | [archive](user_data/profile_smoke/BopTrendStrategy-bb2d63fb-2026-09-09_21-36-13.zip) [log](user_data/convergence_logs/BopTrendStrategy-ladder.log) |
| `BullishEngulfingStrategy` | `spot_long` | `E1_expanded` | 14928 | `convergence:576:warmup_supplied` | 2026-09-09 21:38:35 | [archive](user_data/profile_smoke/BullishEngulfingStrategy-018dc2d8-2026-09-09_21-38-35.zip) [log](user_data/convergence_logs/BullishEngulfingStrategy-ladder.log) |
| `BuyDips` | `spot_long` | `E1_expanded` | 2 | `convergence:576:warmup_supplied` | 2026-09-06 18:26:03 | [archive](user_data/profile_smoke/BuyDips-2afdb8fb-2026-09-06_18-26-03.zip) [log](user_data/convergence_logs/BuyDips-2afdb8fb-ladder.log) |
| `BuyOnly` | `spot_long` | `E1_expanded` | 2279 | `convergence:672:warmup_supplied` | 2026-09-06 05:13:00 | [archive](user_data/profile_smoke/BuyOnly-e2e0e0ff-2026-09-06_05-13-00.zip) [log](user_data/convergence_logs/BuyOnly-ladder.log) |
| `BuyOrDie` | `spot_long` | `E1_expanded` | 2334 | `convergence:288:warmup_supplied` | 2026-09-07 16:42:05 | [archive](user_data/profile_smoke/BuyOrDie-7974d456-2026-09-07_16-42-05.zip) [log](user_data/convergence_logs/BuyOrDie-ladder.log) |
| `CBPete9` | `spot_long` | `E1_expanded` | 132 | `convergence:2016:warmup_supplied` | 2026-09-06 15:08:25 | [archive](user_data/profile_smoke/CBPete9-6ffadd4c-2026-09-06_15-08-25.zip) [log](user_data/convergence_logs/CBPete9-ladder.log) |
| `CCI_BB` | `spot_long` | `E1_expanded` | 1050 | `convergence:288:warmup_supplied` | 2026-09-07 16:45:02 | [archive](user_data/profile_smoke/CCI_BB-05af1dd1-2026-09-07_16-45-02.zip) [log](user_data/convergence_logs/CCI_BB-ladder.log) |
| `CMCWinner` | `spot_long` | `E1_expanded` | 5196 | `convergence:672:warmup_supplied` | 2026-09-05 14:26:45 | [archive](user_data/profile_smoke/CMCWinner-a8094718-2026-09-05_14-26-45.zip) [log](user_data/convergence_logs/CMCWinner-ladder.log) |
| `CTIBS` | `spot_long` | `E1_expanded` | 4654 | `convergence:672:warmup_supplied` | 2026-09-07 16:06:38 | [archive](user_data/profile_smoke/CTIBS-dc6c3262-2026-09-07_16-06-38.zip) [log](user_data/convergence_logs/CTIBS-ladder.log) |
| `Candle2` | `spot_long` | `E1_expanded` | 5931 | `convergence:168:warmup_supplied` | 2026-09-06 11:07:44 | [archive](user_data/profile_smoke/Candle2-21a0249c-2026-09-06_11-07-44.zip) [log](user_data/convergence_logs/Candle2-ladder.log) |
| `CciMeanReversionStrategy` | `spot_long` | `E1_expanded` | 16370 | `convergence:576:warmup_supplied` | 2026-09-09 21:38:57 | [archive](user_data/profile_smoke/CciMeanReversionStrategy-66df7760-2026-09-09_21-38-57.zip) [log](user_data/convergence_logs/CciMeanReversionStrategy-ladder.log) |
| `Cenderawasih_30m` | `spot_long` | `E1_expanded` | 1 | `convergence:672:warmup_supplied` | 2026-09-01 20:43:33 | [archive](user_data/profile_smoke/Cenderawasih_30m-2026-09-01_20-43-33.zip) [log](user_data/convergence_logs/Cenderawasih_30m-ladder.log) |
| `Cenderawasih_3_kucoin` | `spot_long` | `E1_expanded` | 59 | `convergence:288:warmup_supplied` | 2026-09-01 20:42:41 | [archive](user_data/profile_smoke/Cenderawasih_3_kucoin-2026-09-01_20-42-41.zip) [log](user_data/convergence_logs/Cenderawasih_3_kucoin-ladder.log) |
| `ChaikinMoneyFlowStrategy` | `spot_long` | `E1_expanded` | 14737 | `convergence:288:warmup_supplied` | 2026-09-09 21:40:54 | [archive](user_data/profile_smoke/ChaikinMoneyFlowStrategy-553da512-2026-09-09_21-40-54.zip) [log](user_data/convergence_logs/ChaikinMoneyFlowStrategy-ladder.log) |
| `Chandem` | `spot_long` | `E1_expanded` | 12779 | `convergence:2016:warmup_supplied` | 2026-09-07 03:54:02 | [archive](user_data/profile_smoke/Chandem-fb182bdf-2026-09-07_03-54-02.zip) [log](user_data/convergence_logs/Chandem-ladder.log) |
| `Chandemtwo` | `spot_long` | `E1_expanded` | 14649 | `convergence:2016:warmup_supplied` | 2026-09-06 05:26:02 | [archive](user_data/profile_smoke/Chandemtwo-40181d85-2026-09-06_05-26-02.zip) [log](user_data/convergence_logs/Chandemtwo-ladder.log) |
| `Chispei` | `spot_long` | `E1_expanded` | 50 | `convergence:42:warmup_supplied` | 2026-09-01 19:36:09 | [archive](user_data/profile_smoke/Chispei-2026-09-01_19-36-09.zip) [log](user_data/convergence_logs/Chispei-62b19ed2-ladder.log) |
| `Cluc4` | `spot_long` | `E1_expanded` | 171 | `convergence:1440:warmup_supplied` | 2026-09-09 16:30:42 | [archive](user_data/profile_smoke/Cluc4-72b005ae-2026-09-09_16-30-42.zip) [log](user_data/convergence_logs/Cluc4-ladder.log) |
| `Cluc4werk` | `spot_long` | `E1_expanded` | 162 | `convergence:1440:warmup_supplied` | 2026-09-09 16:17:16 | [archive](user_data/profile_smoke/Cluc4werk-442f52c0-2026-09-09_16-17-16.zip) [log](user_data/convergence_logs/Cluc4werk-ladder.log) |
| `Cluc5werk` | `spot_long` | `E1_expanded` | 31 | `convergence:1440:warmup_supplied` | 2026-09-09 16:17:59 | [archive](user_data/profile_smoke/Cluc5werk-12db1a87-2026-09-09_16-17-59.zip) [log](user_data/convergence_logs/Cluc5werk-ladder.log) |
| `Cluc7werk` | `spot_long` | `E1_expanded` | 223 | `convergence:1440:warmup_supplied` | 2026-09-09 16:18:39 | [archive](user_data/profile_smoke/Cluc7werk-4eb74e34-2026-09-09_16-18-39.zip) [log](user_data/convergence_logs/Cluc7werk-ladder.log) |
| `ClucFiatROI` | `spot_long` | `E1_expanded` | 4919 | `convergence:288:warmup_supplied` | 2026-09-05 14:39:56 | [archive](user_data/profile_smoke/ClucFiatROI-37eacf60-2026-09-05_14-39-56.zip) [log](user_data/convergence_logs/ClucFiatROI-ladder.log) |
| `ClucFiatSlow` | `spot_long` | `E1_expanded` | 4919 | `convergence:288:warmup_supplied` | 2026-09-05 14:43:09 | [archive](user_data/profile_smoke/ClucFiatSlow-ece26050-2026-09-05_14-43-09.zip) [log](user_data/convergence_logs/ClucFiatSlow-ladder.log) |
| `ClucHAnix` | `spot_long` | `E1_expanded` | 140 | `convergence:1440:warmup_supplied` | 2026-09-09 16:19:54 | [archive](user_data/profile_smoke/ClucHAnix-895ff1e0-2026-09-09_16-19-54.zip) [log](user_data/convergence_logs/ClucHAnix-ladder.log) |
| `ClucHAnix_5M_E0V1E` | `spot_long` | `E1_expanded` | 4421 | `convergence:288:warmup_supplied` | 2026-09-14 18:14:13 | [archive](user_data/profile_smoke/ClucHAnix_5M_E0V1E-eef9a366-2026-09-14_18-14-13.zip) [log](user_data/convergence_logs/ClucHAnix_5M_E0V1E-ladder.log) |
| `ClucHAnix_5M_E0V1E_DYNAMIC_TB` | `spot_long` | `E1_expanded` | 4421 | `convergence:288:warmup_supplied` | 2026-09-15 06:50:57 | [archive](user_data/profile_smoke/ClucHAnix_5M_E0V1E_DYNAMIC_TB-a98e4371-smoke_20200301_20200401-b4807b77-2026-09-15_06-50-57.zip) [log](user_data/convergence_logs/ClucHAnix_5M_E0V1E_DYNAMIC_TB-a98e4371-ladder.log) |
| `ClucHAnix_5m` | `spot_long` | `E1_expanded` | 73 | `convergence:288:warmup_supplied` | 2026-09-17 12:14:19 | [archive](user_data/profile_smoke/ClucHAnix_5m-0d4d79f1-smoke_20200301_20200401-b4807b77-2026-09-17_12-14-19.zip) [log](user_data/convergence_logs/ClucHAnix_5m-ladder.log) |
| `ClucHAnix_5m1` | `spot_long` | `E1_expanded` | 2488 | `convergence:288:warmup_supplied` | 2026-09-05 15:17:18 | [archive](user_data/profile_smoke/ClucHAnix_5m1-f99f71de-2026-09-05_15-17-18.zip) [log](user_data/convergence_logs/ClucHAnix_5m1-ladder.log) |
| `ClucHAnix_5mTB1` | `spot_long` | `E1_expanded` | 2488 | `convergence:288:warmup_supplied` | 2026-09-14 23:42:42 | [archive](user_data/profile_smoke/ClucHAnix_5mTB1-64f93719-smoke_20200301_20200401-b4807b77-2026-09-14_23-42-42.zip) [log](user_data/convergence_logs/ClucHAnix_5mTB1-64f93719-ladder.log) |
| `ClucHAnix_5m_old` | `spot_long` | `E1_expanded` | 2288 | `convergence:288:warmup_supplied` | 2026-09-07 02:06:58 | [archive](user_data/profile_smoke/ClucHAnix_5m_old-54788119-2026-09-07_02-06-58.zip) [log](user_data/convergence_logs/ClucHAnix_5m_old-ladder.log) |
| `ClucHAnix_BB_RPB` | `spot_long` | `E1_expanded` | 242 | `convergence:2880:warmup_supplied` | 2026-09-06 14:49:03 | [archive](user_data/profile_smoke/ClucHAnix_BB_RPB-d5edb88c-2026-09-06_14-49-03.zip) [log](user_data/convergence_logs/ClucHAnix_BB_RPB-ladder.log) |
| `ClucHAnix_BB_RPB_HO2` | `spot_long` | `E1_expanded` | 201 | `convergence:2880:warmup_supplied` | 2026-09-06 14:50:18 | [archive](user_data/profile_smoke/ClucHAnix_BB_RPB_HO2-50399031-2026-09-06_14-50-18.zip) [log](user_data/convergence_logs/ClucHAnix_BB_RPB_HO2-ladder.log) |
| `ClucHAnix_BB_RPB_MOD` | `spot_long` | `E1_expanded` | 217 | `convergence:2880:warmup_supplied` | 2026-09-06 14:51:41 | [archive](user_data/profile_smoke/ClucHAnix_BB_RPB_MOD-4949016b-2026-09-06_14-51-41.zip) [log](user_data/convergence_logs/ClucHAnix_BB_RPB_MOD-ladder.log) |
| `ClucHAnix_hhll` | `spot_long` | `E1_expanded` | 1817 | `convergence:2016:warmup_supplied` | 2026-09-06 20:10:33 | [archive](user_data/profile_smoke/ClucHAnix_hhll-9fa2f74f-2026-09-06_20-10-33.zip) [log](user_data/convergence_logs/ClucHAnix_hhll-ladder.log) |
| `ClucHAnix_hhll_TB` | `spot_long` | `E1_expanded` | 1817 | `convergence:2016:warmup_supplied` | 2026-09-14 23:43:21 | [archive](user_data/profile_smoke/ClucHAnix_hhll_TB-069e254e-smoke_20200301_20200401-b4807b77-2026-09-14_23-43-21.zip) [log](user_data/convergence_logs/ClucHAnix_hhll_TB-069e254e-ladder.log) |
| `ClucHAwerk` | `spot_long` | `E1_expanded` | 782 | `convergence:1440:warmup_supplied` | 2026-09-09 16:21:12 | [archive](user_data/profile_smoke/ClucHAwerk-06465a96-2026-09-09_16-21-12.zip) [log](user_data/convergence_logs/ClucHAwerk-ladder.log) |
| `ClucMay72018` | `spot_long` | `E1_expanded` | 1885 | `convergence:288:warmup_supplied` | 2026-09-05 16:25:13 | [archive](user_data/profile_smoke/ClucMay72018-b2c7acb8-2026-09-05_16-25-13.zip) [log](user_data/convergence_logs/ClucMay72018-ladder.log) |
| `CofiBitStrategy` | `spot_long` | `E1_expanded` | 20280 | `convergence:288:warmup_supplied` | 2026-09-05 16:27:32 | [archive](user_data/profile_smoke/CofiBitStrategy-e2d65576-2026-09-05_16-27-32.zip) [log](user_data/convergence_logs/CofiBitStrategy-ladder.log) |
| `CombinedBinHAndCluc` | `spot_long` | `E1_expanded` | 2691 | `convergence:288:warmup_supplied` | 2026-09-05 16:27:55 | [archive](user_data/profile_smoke/CombinedBinHAndCluc-5a3aec50-2026-09-05_16-27-55.zip) [log](user_data/convergence_logs/CombinedBinHAndCluc-ladder.log) |
| `CombinedBinHAndCluc2021` | `spot_long` | `E1_expanded` | 2477 | `convergence:288:warmup_supplied` | 2026-09-05 16:30:24 | [archive](user_data/profile_smoke/CombinedBinHAndCluc2021-8fdd7337-2026-09-05_16-30-24.zip) [log](user_data/convergence_logs/CombinedBinHAndCluc2021-ladder.log) |
| `CombinedBinHAndCluc2021Bull` | `spot_long` | `E1_expanded` | 2940 | `convergence:288:warmup_supplied` | 2026-09-05 16:30:31 | [archive](user_data/profile_smoke/CombinedBinHAndCluc2021Bull-28c97ea0-2026-09-05_16-30-31.zip) [log](user_data/convergence_logs/CombinedBinHAndCluc2021Bull-ladder.log) |
| `CombinedBinHAndClucHyper` | `spot_long` | `E1_expanded` | 90 | `convergence:1440:warmup_supplied` | 2026-09-06 14:59:31 | [archive](user_data/profile_smoke/CombinedBinHAndClucHyper-48a908dc-2026-09-06_14-59-31.zip) [log](user_data/convergence_logs/CombinedBinHAndClucHyper-ladder.log) |
| `CombinedBinHAndClucHyperV0` | `spot_long` | `E1_expanded` | 282 | `convergence:1440:warmup_supplied` | 2026-09-09 16:31:26 | [archive](user_data/profile_smoke/CombinedBinHAndClucHyperV0-e03b8c29-2026-09-09_16-31-26.zip) [log](user_data/convergence_logs/CombinedBinHAndClucHyperV0-ladder.log) |
| `CombinedBinHAndClucHyperV3` | `spot_long` | `E1_expanded` | 180 | `convergence:1440:warmup_supplied` | 2026-09-09 16:32:07 | [archive](user_data/profile_smoke/CombinedBinHAndClucHyperV3-84115c08-2026-09-09_16-32-07.zip) [log](user_data/convergence_logs/CombinedBinHAndClucHyperV3-ladder.log) |
| `CombinedBinHAndClucV2` | `spot_long` | `E1_expanded` | 549 | `convergence:576:warmup_supplied` | 2026-09-05 16:32:52 | [archive](user_data/profile_smoke/CombinedBinHAndClucV2-9a6ae965-2026-09-05_16-32-52.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV2-ladder.log) |
| `CombinedBinHAndClucV3` | `spot_long` | `E1_expanded` | 1967 | `convergence:2016:warmup_supplied` | 2026-09-06 05:35:59 | [archive](user_data/profile_smoke/CombinedBinHAndClucV3-f17b9b5c-2026-09-06_05-35-59.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV3-ladder.log) |
| `CombinedBinHAndClucV4` | `spot_long` | `E1_expanded` | 2241 | `convergence:288:warmup_supplied` | 2026-09-05 16:33:14 | [archive](user_data/profile_smoke/CombinedBinHAndClucV4-555d5c39-2026-09-05_16-33-14.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV4-ladder.log) |
| `CombinedBinHAndClucV5` | `spot_long` | `E1_expanded` | 2256 | `convergence:288:warmup_supplied` | 2026-09-05 16:36:04 | [archive](user_data/profile_smoke/CombinedBinHAndClucV5-bfb95c2b-2026-09-05_16-36-04.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV5-ladder.log) |
| `CombinedBinHAndClucV5Hyperoptable` | `spot_long` | `E1_expanded` | 2063 | `convergence:288:warmup_supplied` | 2026-09-06 05:36:59 | [archive](user_data/profile_smoke/CombinedBinHAndClucV5Hyperoptable-a2c34034-2026-09-06_05-36-59.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV5Hyperoptable-ladder.log) |
| `CombinedBinHAndClucV6` | `spot_long` | `E1_expanded` | 1387 | `convergence:2016:warmup_supplied` | 2026-09-05 16:37:01 | [archive](user_data/profile_smoke/CombinedBinHAndClucV6-5ca5df9c-2026-09-05_16-37-01.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV6-ladder.log) |
| `CombinedBinHAndClucV6H` | `spot_long` | `E1_expanded` | 26 | `convergence:2016:warmup_supplied` | 2026-09-09 09:28:22 | [archive](user_data/profile_smoke/CombinedBinHAndClucV6H-88f6bcec-2026-09-09_09-28-22.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV6H-ladder.log) |
| `CombinedBinHAndClucV7` | `spot_long` | `E1_expanded` | 702 | `convergence:2016:warmup_supplied` | 2026-09-05 16:39:01 | [archive](user_data/profile_smoke/CombinedBinHAndClucV7-144044aa-2026-09-05_16-39-01.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV7-ladder.log) |
| `CombinedBinHAndClucV8` | `spot_long` | `E1_expanded` | 700 | `convergence:2016:warmup_supplied` | 2026-09-05 16:40:06 | [archive](user_data/profile_smoke/CombinedBinHAndClucV8-32f7e1b0-2026-09-05_16-40-06.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV8-ladder.log) |
| `CombinedBinHAndClucV8Hyper` | `spot_long` | `E1_expanded` | 1003 | `convergence:2016:warmup_supplied` | 2026-09-05 16:41:57 | [archive](user_data/profile_smoke/CombinedBinHAndClucV8Hyper-e98d8fc3-2026-09-05_16-41-57.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV8Hyper-ladder.log) |
| `CombinedBinHAndClucV8XH` | `spot_long` | `E1_expanded` | 503 | `convergence:2016:warmup_supplied` | 2026-09-05 16:43:05 | [archive](user_data/profile_smoke/CombinedBinHAndClucV8XH-f05ebf6e-2026-09-05_16-43-05.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV8XH-ladder.log) |
| `CombinedBinHAndClucV8XHO` | `spot_long` | `E1_expanded` | 679 | `convergence:2016:warmup_supplied` | 2026-09-06 05:39:10 | [archive](user_data/profile_smoke/CombinedBinHAndClucV8XHO-dc5be8a3-2026-09-06_05-39-10.zip) [log](user_data/convergence_logs/CombinedBinHAndClucV8XHO-ladder.log) |
| `CombinedBinHClucAndMADV3` | `spot_long` | `E1_expanded` | 1298 | `convergence:2016:warmup_supplied` | 2026-09-05 16:44:28 | [archive](user_data/profile_smoke/CombinedBinHClucAndMADV3-bd6b6b26-2026-09-05_16-44-28.zip) [log](user_data/convergence_logs/CombinedBinHClucAndMADV3-ladder.log) |
| `CombinedBinHClucAndMADV5` | `spot_long` | `E1_expanded` | 1331 | `convergence:2016:warmup_supplied` | 2026-09-07 13:44:55 | [archive](user_data/profile_smoke/CombinedBinHClucAndMADV5-f746355d-2026-09-07_13-44-55.zip) [log](user_data/convergence_logs/CombinedBinHClucAndMADV5-ladder.log) |
| `CombinedBinHClucAndMADV6` | `spot_long` | `E1_expanded` | 1309 | `convergence:2016:warmup_supplied` | 2026-09-05 16:45:42 | [archive](user_data/profile_smoke/CombinedBinHClucAndMADV6-13156fb3-2026-09-05_16-45-42.zip) [log](user_data/convergence_logs/CombinedBinHClucAndMADV6-ladder.log) |
| `CombinedBinHClucAndMADV9` | `spot_long` | `E1_expanded` | 2131 | `convergence:2016:warmup_supplied` | 2026-09-05 16:48:09 | [archive](user_data/profile_smoke/CombinedBinHClucAndMADV9-35d68152-2026-09-05_16-48-09.zip) [log](user_data/convergence_logs/CombinedBinHClucAndMADV9-ladder.log) |
| `Combined_Indicators` | `spot_long` | `E1_expanded` | 235 | `convergence:1440:warmup_supplied` | 2026-09-09 16:32:48 | [archive](user_data/profile_smoke/Combined_Indicators-8c5e3bcf-2026-09-09_16-32-48.zip) [log](user_data/convergence_logs/Combined_Indicators-ladder.log) |
| `Combined_NFIv6_SMA` | `spot_long` | `E1_expanded` | 740 | `convergence:2016:warmup_supplied` | 2026-09-05 16:49:33 | [archive](user_data/profile_smoke/Combined_NFIv6_SMA-cd9c21e5-2026-09-05_16-49-33.zip) [log](user_data/convergence_logs/Combined_NFIv6_SMA-ladder.log) |
| `Combined_NFIv7_SMA` | `spot_long` | `E1_expanded` | 722 | `convergence:2016:warmup_supplied` | 2026-09-07 19:05:25 | [archive](user_data/profile_smoke/Combined_NFIv7_SMA-a3e77574-2026-09-07_19-05-25.zip) [log](user_data/convergence_logs/Combined_NFIv7_SMA-ladder.log) |
| `CompleteIndicatorStrategy2` | `futures_long_short` | `E1_expanded` | 1042 | `convergence:336:warmup_supplied` | 2026-09-14 19:21:38 | [archive](user_data/profile_smoke/CompleteIndicatorStrategy2-cc7c80ef-smoke_20200301_20200401-b4807b77-2026-09-14_19-21-38.zip) [log](user_data/convergence_logs/CompleteIndicatorStrategy2-cc7c80ef-ladder.log) |
| `CompositeScoreStrategy` | `spot_long` | `E1_expanded` | 14682 | `convergence:288:warmup_supplied` | 2026-09-09 21:42:06 | [archive](user_data/profile_smoke/CompositeScoreStrategy-b827382b-2026-09-09_21-42-06.zip) [log](user_data/convergence_logs/CompositeScoreStrategy-ladder.log) |
| `ConsensusShort` | `futures_long_short` | `E1_expanded` | 414 | `convergence:288:warmup_supplied` | 2026-09-02 06:55:30 | [log](user_data/convergence_logs/ConsensusShort-ladder.log) |
| `CoppockCurveStrategy` | `spot_long` | `E1_expanded` | 13364 | `convergence:288:warmup_supplied` | 2026-09-09 21:43:12 | [archive](user_data/profile_smoke/CoppockCurveStrategy-cb29834f-2026-09-09_21-43-12.zip) [log](user_data/convergence_logs/CoppockCurveStrategy-ladder.log) |
| `CoreStrategy` | `spot_long` | `E1_expanded` | 40 | `convergence:2016:warmup_supplied` | 2026-09-09 09:28:16 | [archive](user_data/profile_smoke/CoreStrategy-acac6ca9-2026-09-09_09-28-16.zip) [log](user_data/convergence_logs/CoreStrategy-ladder.log) |
| `CrossEMAStrategy` | `spot_long` | `E1_expanded` | 3502 | `convergence:168:warmup_supplied` | 2026-09-05 16:49:47 | [archive](user_data/profile_smoke/CrossEMAStrategy-75a10fc2-2026-09-05_16-49-47.zip) [log](user_data/convergence_logs/CrossEMAStrategy-ladder.log) |
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
| `CustomStoplossWithPSAR` | `spot_long` | `E1_expanded` | 58 | `convergence:24:warmup_supplied` | 2026-09-05 22:37:25 | [archive](user_data/profile_smoke/CustomStoplossWithPSAR-3c86d8a0-2026-09-05_22-37-25.zip) [log](user_data/convergence_logs/CustomStoplossWithPSAR-ladder.log) |
| `DD` | `spot_long` | `E1_expanded` | 23391 | `convergence:288:warmup_supplied` | 2026-09-06 05:51:50 | [archive](user_data/profile_smoke/DD-92f089f2-2026-09-06_05-51-50.zip) [log](user_data/convergence_logs/DD-ladder.log) |
| `DMIPRICEDCAStrategyFuture` | `futures_long_short` | `E1_expanded` | 19 | `convergence:1440:warmup_supplied` | 2026-09-06 16:33:08 | [archive](user_data/profile_smoke/DMIPRICEDCAStrategyFuture-5ed3e947-2026-09-06_16-33-08.zip) [log](user_data/convergence_logs/DMIPRICEDCAStrategyFuture-5ed3e947-ladder.log) |
| `DWT_LongShort` | `futures_long_short` | `E1_expanded` | 859 | `convergence:288:warmup_supplied` | 2026-09-02 06:56:43 | [log](user_data/convergence_logs/DWT_LongShort-ladder.log) |
| `DWT_short` | `futures_long_short` | `E1_expanded` | 362 | `convergence:288:warmup_supplied` | 2026-09-02 06:57:53 | [log](user_data/convergence_logs/DWT_short-ladder.log) |
| `DemaCrossStrategy` | `spot_long` | `E1_expanded` | 13743 | `convergence:288:warmup_supplied` | 2026-09-09 21:44:32 | [archive](user_data/profile_smoke/DemaCrossStrategy-f77e5dfc-2026-09-09_21-44-32.zip) [log](user_data/convergence_logs/DemaCrossStrategy-ladder.log) |
| `DevDsl2Approx` | `futures_long_short` | `E1_expanded` | 19 | `convergence:2016:warmup_supplied` | 2026-09-14 19:22:13 | [archive](user_data/profile_smoke/DevDsl2Approx-f1627c83-smoke_20200301_20200401-b4807b77-2026-09-14_19-22-13.zip) [log](user_data/convergence_logs/DevDsl2Approx-f1627c83-ladder.log) |
| `Diamond` | `spot_long` | `E1_expanded` | 4691 | `convergence:288:warmup_supplied` | 2026-09-06 01:44:11 | [archive](user_data/profile_smoke/Diamond-b639c243-2026-09-06_01-44-11.zip) [log](user_data/convergence_logs/Diamond-ladder.log) |
| `Divergences` | `spot_long` | `E1_expanded` | 7814 | `convergence:2160:warmup_supplied` | 2026-09-05 17:22:18 | [archive](user_data/profile_smoke/Divergences-adb58dfb-2026-09-05_17-22-18.zip) [log](user_data/convergence_logs/Divergences-ladder.log) |
| `DonchianBounce` | `spot_long` | `E1_expanded` | 32 | `convergence:576:warmup_supplied` | 2026-09-15 21:00:17 | [archive](user_data/profile_smoke/DonchianBounce-9e62325a-smoke_20200301_20200601-9c543975-2026-09-15_21-00-17.zip) [log](user_data/convergence_logs/DonchianBounce-9e62325a-ladder.log) |
| `DonchianBreakoutStrategy` | `spot_long` | `E1_expanded` | 10828 | `convergence:288:warmup_supplied` | 2026-09-09 21:45:28 | [archive](user_data/profile_smoke/DonchianBreakoutStrategy-184224cc-2026-09-09_21-45-28.zip) [log](user_data/convergence_logs/DonchianBreakoutStrategy-ladder.log) |
| `DoubleEMACrossoverWithTrend` | `spot_long` | `E1_expanded` | 4019 | `convergence:2160:warmup_supplied` | 2026-09-06 01:34:23 | [archive](user_data/profile_smoke/DoubleEMACrossoverWithTrend-2df7ee08-2026-09-06_01-34-23.zip) [log](user_data/convergence_logs/DoubleEMACrossoverWithTrend-2df7ee08-ladder.log) |
| `Dyna_opti` | `spot_long` | `E1_expanded` | 26 | `convergence:576:warmup_supplied` | 2026-09-04 06:12:17 | [archive](user_data/profile_smoke/Dyna_opti-8aa17cbf-2026-09-04_06-12-17.zip) [log](user_data/convergence_logs/Dyna_opti-ladder.log) |
| `E0V1E` | `spot_long` | `E1_expanded` | 280 | `convergence:2016:warmup_supplied` | 2026-09-06 00:37:37 | [archive](user_data/profile_smoke/E0V1E-35b73da0-2026-09-06_00-37-37.zip) [log](user_data/convergence_logs/E0V1E-ladder.log) |
| `E0V1E2` | `spot_long` | `E1_expanded` | 280 | `convergence:2016:warmup_supplied` | 2026-09-06 00:43:58 | [archive](user_data/profile_smoke/E0V1E2-b64d1b35-2026-09-06_00-43-58.zip) [log](user_data/convergence_logs/E0V1E2-ladder.log) |
| `E0V1EN` | `spot_long` | `E1_expanded` | 25 | `convergence:288:warmup_supplied` | 2026-09-06 15:09:16 | [archive](user_data/profile_smoke/E0V1EN-dc02ef88-2026-09-06_15-09-16.zip) [log](user_data/convergence_logs/E0V1EN-ladder.log) |
| `E0V1E_3` | `spot_long` | `E1_expanded` | 10 | `convergence:288:warmup_supplied` | 2026-09-14 19:31:23 | [archive](user_data/profile_smoke/E0V1E_3-5c053f76-smoke_20200301_20200401-b4807b77-2026-09-14_19-31-23.zip) [log](user_data/convergence_logs/E0V1E_3-5c053f76-ladder.log) |
| `E0V1E_DCA3` | `spot_long` | `E1_expanded` | 1878 | `convergence:2016:warmup_supplied` | 2026-09-07 02:26:20 | [archive](user_data/profile_smoke/E0V1E_DCA3-ab4c346a-2026-09-07_02-26-20.zip) [log](user_data/convergence_logs/E0V1E_DCA3-ladder.log) |
| `E0V1E_Shorts` | `futures_short` | `E1_expanded` | 11 | `convergence:2016:warmup_supplied` | 2026-09-14 19:31:28 | [archive](user_data/profile_smoke/E0V1E_Shorts-75162add-smoke_20200301_20200401-b4807b77-2026-09-14_19-31-28.zip) [log](user_data/convergence_logs/E0V1E_Shorts-75162add-ladder.log) |
| `E0V1E_ewo` | `spot_long` | `E1_expanded` | 268 | `convergence:2016:warmup_supplied` | 2026-09-06 00:47:49 | [archive](user_data/profile_smoke/E0V1E_ewo-689358af-2026-09-06_00-47-49.zip) [log](user_data/convergence_logs/E0V1E_ewo-ladder.log) |
| `E0V1E_protections` | `spot_long` | `E1_expanded` | 280 | `convergence:2016:warmup_supplied` | 2026-09-06 00:49:30 | [archive](user_data/profile_smoke/E0V1E_protections-add87501-2026-09-06_00-49-30.zip) [log](user_data/convergence_logs/E0V1E_protections-ladder.log) |
| `E0V1E_strs` | `spot_long` | `E1_expanded` | 111 | `convergence:288:warmup_supplied` | 2026-09-06 00:51:07 | [archive](user_data/profile_smoke/E0V1E_strs-d8807a22-2026-09-06_00-51-07.zip) [log](user_data/convergence_logs/E0V1E_strs-ladder.log) |
| `EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March` | `futures_long_short` | `E1_expanded` | 354 | `convergence:336:warmup_supplied` | 2026-09-14 19:30:10 | [archive](user_data/profile_smoke/EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March-a6438d1f-smoke_20200301_20200401-b4807b77-2026-09-14_19-30-10.zip) [log](user_data/convergence_logs/EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March-a6438d1f-ladder.log) |
| `EI3v2_tag_cofi_green` | `spot_long` | `E1_expanded` | 116 | `convergence:2016:warmup_supplied` | 2026-09-06 14:47:16 | [archive](user_data/profile_smoke/EI3v2_tag_cofi_green-c37315b6-2026-09-06_14-47-16.zip) [log](user_data/convergence_logs/EI3v2_tag_cofi_green-ladder.log) |
| `EMA50` | `spot_long` | `E1_expanded` | 10435 | `convergence:288:warmup_supplied` | 2026-09-07 13:55:57 | [archive](user_data/profile_smoke/EMA50-07c89e5c-2026-09-07_13-55-57.zip) [log](user_data/convergence_logs/EMA50-ladder.log) |
| `EMA520015_V17` | `spot_long` | `E1_expanded` | 7218 | `convergence:540:warmup_supplied` | 2026-09-06 05:53:43 | [archive](user_data/profile_smoke/EMA520015_V17-94b0e424-2026-09-06_05-53-43.zip) [log](user_data/convergence_logs/EMA520015_V17-ladder.log) |
| `EMABBRSI` | `spot_long` | `E1_expanded` | 104 | `convergence:2160:warmup_supplied` | 2026-09-01 19:36:47 | [archive](user_data/profile_smoke/EMABBRSI-2026-09-01_19-36-47.zip) [log](user_data/convergence_logs/EMABBRSI-ladder.log) |
| `EMABounce` | `spot_long` | `E1_expanded` | 16 | `convergence:288:warmup_supplied` | 2026-09-06 18:36:24 | [archive](user_data/profile_smoke/EMABounce-ab0d2db4-2026-09-06_18-36-24.zip) [log](user_data/convergence_logs/EMABounce-ab0d2db4-ladder.log) |
| `EMABreakout` | `spot_long` | `E1_expanded` | 9296 | `convergence:288:warmup_supplied` | 2026-09-06 06:08:38 | [archive](user_data/profile_smoke/EMABreakout-50cd0f93-2026-09-06_06-08-38.zip) [log](user_data/convergence_logs/EMABreakout-ladder.log) |
| `EMACross` | `spot_long` | `E1_expanded` | 1175 | `convergence:30` | 2026-09-06 18:26:31 | [archive](user_data/profile_smoke/EMACross-b5f64897-2026-09-06_18-26-31.zip) [log](user_data/convergence_logs/EMACross-b5f64897-ladder.log) |
| `EMAPriceCrossoverWithThreshold` | `spot_long` | `E1_expanded` | 1816 | `convergence:2160:warmup_supplied` | 2026-09-06 01:35:42 | [archive](user_data/profile_smoke/EMAPriceCrossoverWithThreshold-b7ab2a0f-2026-09-06_01-35-42.zip) [log](user_data/convergence_logs/EMAPriceCrossoverWithThreshold-b7ab2a0f-ladder.log) |
| `EMASkipPump` | `spot_long` | `E1_expanded` | 25221 | `convergence:288:warmup_supplied` | 2026-09-05 17:27:51 | [archive](user_data/profile_smoke/EMASkipPump-b4f9f8f8-2026-09-05_17-27-51.zip) [log](user_data/convergence_logs/EMASkipPump-ladder.log) |
| `EMAVolume` | `spot_long` | `E1_expanded` | 183 | `convergence:1344:warmup_supplied` | 2026-09-01 19:37:25 | [archive](user_data/profile_smoke/EMAVolume-2026-09-01_19-37-25.zip) [log](user_data/convergence_logs/EMAVolume-ladder.log) |
| `EMA_CROSSOVER_STRATEGY` | `spot_long` | `E1_expanded` | 13697 | `convergence:4032:warmup_supplied` | 2026-09-06 06:01:55 | [archive](user_data/profile_smoke/EMA_CROSSOVER_STRATEGY-19dd135f-2026-09-06_06-01-55.zip) [log](user_data/convergence_logs/EMA_CROSSOVER_STRATEGY-ladder.log) |
| `EMA_Trailing_Stoploss` | `spot_long` | `E1_expanded` | 463 | `convergence:24:warmup_supplied` | 2026-09-05 15:04:54 | [archive](user_data/profile_smoke/EMA_Trailing_Stoploss-c357e7e7-2026-09-05_15-04-54.zip) [log](user_data/convergence_logs/EMA_Trailing_Stoploss-c357e7e7-ladder.log) |
| `EMA_Trailing_Stoploss_LessMagic` | `spot_long` | `E1_expanded` | 463 | `convergence:288:warmup_supplied` | 2026-09-05 15:06:00 | [archive](user_data/profile_smoke/EMA_Trailing_Stoploss_LessMagic-aa2b302f-2026-09-05_15-06-00.zip) [log](user_data/convergence_logs/EMA_Trailing_Stoploss_LessMagic-aa2b302f-ladder.log) |
| `ETCG_Shorts` | `futures_short` | `E1_expanded` | 67 | `convergence:2016:warmup_supplied` | 2026-09-14 19:22:18 | [archive](user_data/profile_smoke/ETCG_Shorts-7a38345a-smoke_20200301_20200401-b4807b77-2026-09-14_19-22-18.zip) [log](user_data/convergence_logs/ETCG_Shorts-7a38345a-ladder.log) |
| `EXPERIMENTAL_STRATEGY` | `spot_long` | `E1_expanded` | 582 | `convergence:288:warmup_supplied` | 2026-09-01 19:38:04 | [archive](user_data/profile_smoke/EXPERIMENTAL_STRATEGY-2026-09-01_19-38-04.zip) [log](user_data/convergence_logs/EXPERIMENTAL_STRATEGY-ladder.log) |
| `EasyInEasyOut` | `spot_long` | `E1_expanded` | 46 | `convergence:1440:warmup_supplied` | 2026-09-09 16:44:31 | [archive](user_data/profile_smoke/EasyInEasyOut-fc725427-2026-09-09_16-44-31.zip) [log](user_data/convergence_logs/EasyInEasyOut-ladder.log) |
| `ElliotV2` | `spot_long` | `E1_expanded` | 334 | `convergence:2016:warmup_supplied` | 2026-09-06 06:06:07 | [archive](user_data/profile_smoke/ElliotV2-a93cb425-2026-09-06_06-06-07.zip) [log](user_data/convergence_logs/ElliotV2-ladder.log) |
| `ElliotV4` | `spot_long` | `E1_expanded` | 747 | `convergence:2016:warmup_supplied` | 2026-09-06 06:10:38 | [archive](user_data/profile_smoke/ElliotV4-77e1bd66-2026-09-06_06-10-38.zip) [log](user_data/convergence_logs/ElliotV4-ladder.log) |
| `ElliotV531` | `spot_long` | `E1_expanded` | 719 | `convergence:2016:warmup_supplied` | 2026-09-06 06:12:24 | [archive](user_data/profile_smoke/ElliotV531-8e61212e-2026-09-06_06-12-24.zip) [log](user_data/convergence_logs/ElliotV531-ladder.log) |
| `ElliotV5HO` | `spot_long` | `E1_expanded` | 668 | `convergence:2016:warmup_supplied` | 2026-09-06 06:16:30 | [archive](user_data/profile_smoke/ElliotV5HO-3f1e7bde-2026-09-06_06-16-30.zip) [log](user_data/convergence_logs/ElliotV5HO-ladder.log) |
| `ElliotV5HOMod2` | `spot_long` | `E1_expanded` | 405 | `convergence:2016:warmup_supplied` | 2026-09-06 06:14:10 | [archive](user_data/profile_smoke/ElliotV5HOMod2-09ea5d90-2026-09-06_06-14-10.zip) [log](user_data/convergence_logs/ElliotV5HOMod2-ladder.log) |
| `ElliotV5HOMod3` | `spot_long` | `E1_expanded` | 449 | `convergence:2016:warmup_supplied` | 2026-09-06 06:14:57 | [archive](user_data/profile_smoke/ElliotV5HOMod3-75950728-2026-09-06_06-14-57.zip) [log](user_data/convergence_logs/ElliotV5HOMod3-ladder.log) |
| `ElliotV5_SMA` | `spot_long` | `E1_expanded` | 616 | `convergence:288` | 2026-09-05 23:52:33 | [archive](user_data/profile_smoke/ElliotV5_SMA-e9be798d-2026-09-05_23-52-33.zip) [log](user_data/convergence_logs/ElliotV5_SMA-ladder.log) |
| `ElliotV7` | `spot_long` | `E1_expanded` | 449 | `convergence:2016:warmup_supplied` | 2026-09-05 12:09:52 | [archive](user_data/profile_smoke/ElliotV7-012579cf-2026-09-05_12-09-52.zip) [log](user_data/convergence_logs/ElliotV7-ladder.log) |
| `ElliotV8HO` | `spot_long` | `E1_expanded` | 337 | `convergence:2016:warmup_supplied` | 2026-09-06 06:18:38 | [archive](user_data/profile_smoke/ElliotV8HO-afc8d86f-2026-09-06_06-18-38.zip) [log](user_data/convergence_logs/ElliotV8HO-ladder.log) |
| `ElliotV8_original` | `spot_long` | `E1_expanded` | 25 | `convergence:2016:warmup_supplied` | 2026-09-06 15:08:33 | [archive](user_data/profile_smoke/ElliotV8_original-ce2403f2-2026-09-06_15-08-33.zip) [log](user_data/convergence_logs/ElliotV8_original-ladder.log) |
| `ElliotV8_original_ichiv2` | `spot_long` | `E1_expanded` | 54 | `convergence:2016:warmup_supplied` | 2026-09-06 14:59:37 | [archive](user_data/profile_smoke/ElliotV8_original_ichiv2-3c67badc-2026-09-06_14-59-37.zip) [log](user_data/convergence_logs/ElliotV8_original_ichiv2-ladder.log) |
| `ElliotV8_original_ichiv2OH` | `spot_long` | `E1_expanded` | 56 | `convergence:2016:warmup_supplied` | 2026-09-06 14:59:43 | [archive](user_data/profile_smoke/ElliotV8_original_ichiv2OH-a45e937f-2026-09-06_14-59-43.zip) [log](user_data/convergence_logs/ElliotV8_original_ichiv2OH-ladder.log) |
| `ElliotV8_original_ichiv3` | `spot_long` | `E1_expanded` | 71 | `convergence:2016:warmup_supplied` | 2026-09-06 14:46:50 | [archive](user_data/profile_smoke/ElliotV8_original_ichiv3-433ffe91-2026-09-06_14-46-50.zip) [log](user_data/convergence_logs/ElliotV8_original_ichiv3-ladder.log) |
| `Elliotv8` | `spot_long` | `E1_expanded` | 25 | `convergence:2016:warmup_supplied` | 2026-09-06 14:46:44 | [archive](user_data/profile_smoke/Elliotv8-bdc3ea5b-2026-09-06_14-46-44.zip) [log](user_data/convergence_logs/Elliotv8-ladder.log) |
| `EmaCrossStrategy` | `spot_long` | `E1_expanded` | 28 | `convergence:180:warmup_supplied` | 2026-09-09 07:43:30 | [archive](user_data/profile_smoke/EmaCrossStrategy-a8314e54-2026-09-09_07-43-30.zip) [log](user_data/convergence_logs/EmaCrossStrategy-a8314e54-ladder.log) |
| `EmaRibbonStrategy` | `spot_long` | `E1_expanded` | 13863 | `convergence:288:warmup_supplied` | 2026-09-09 21:47:44 | [archive](user_data/profile_smoke/EmaRibbonStrategy-4e3345d7-2026-09-09_21-47-44.zip) [log](user_data/convergence_logs/EmaRibbonStrategy-ladder.log) |
| `FAdxSmaStrategy` | `futures_long_short` | `E1_expanded` | 15 | `convergence:336:warmup_supplied` | 2026-09-03 13:54:18 | [log](user_data/convergence_logs/FAdxSmaStrategy-ladder.log) |
| `FBB_DWT` | `spot_long` | `E1_expanded` | 91 | `convergence:288:warmup_supplied` | 2026-09-08 16:03:43 | [archive](user_data/profile_smoke/FBB_DWT-a8f9de02-2026-09-08_16-03-43.zip) [log](user_data/convergence_logs/FBB_DWT-a8f9de02-ladder.log) |
| `FBB_KalmanSIMD` | `spot_long` | `E1_expanded` | 69 | `convergence:288:warmup_supplied` | 2026-09-09 09:38:04 | [archive](user_data/profile_smoke/FBB_KalmanSIMD-a241c667-2026-09-09_09-38-04.zip) [log](user_data/convergence_logs/FBB_KalmanSIMD-a241c667-ladder.log) |
| `FFT` | `spot_long` | `E1_expanded` | 111 | `convergence:288:warmup_supplied` | 2026-09-08 16:04:00 | [archive](user_data/profile_smoke/FFT-94fa3fe9-2026-09-08_16-04-00.zip) [log](user_data/convergence_logs/FFT-94fa3fe9-ladder.log) |
| `FLAGS` | `futures_long_short` | `E1_expanded` | 1 | `convergence:24` | 2026-09-06 18:13:49 | [archive](user_data/profile_smoke/FLAGS-72416802-2026-09-06_18-13-49.zip) [log](user_data/convergence_logs/FLAGS-72416802-ladder.log) |
| `FOttStrategy` | `futures_long_short` | `E1_expanded` | 6447 | `convergence:672:warmup_supplied` | 2026-09-01 13:28:30 | [log](user_data/convergence_logs/FOttStrategy-ladder.log) |
| `FRAYSTRAT` | `spot_long` | `E1_expanded` | 7426 | `convergence:672:warmup_supplied` | 2026-09-05 17:29:53 | [archive](user_data/profile_smoke/FRAYSTRAT-591d1d88-2026-09-05_17-29-53.zip) [log](user_data/convergence_logs/FRAYSTRAT-ladder.log) |
| `FReinforcedStrategy` | `futures_long_short` | `E1_expanded` | 80 | `convergence:2016:warmup_supplied` | 2026-09-02 06:59:03 | [log](user_data/convergence_logs/FReinforcedStrategy-ladder.log) |
| `FSampleStrategy` | `futures_long_short` | `E1_expanded` | 40 | `convergence:336:warmup_supplied` | 2026-09-01 13:29:43 | [log](user_data/convergence_logs/FSampleStrategy-ladder.log) |
| `FSupertrendStrategy` | `futures_long` | `E1_expanded` | 83 | `convergence:168:warmup_supplied` | 2026-09-03 13:54:46 | [log](user_data/convergence_logs/FSupertrendStrategy-ladder.log) |
| `FSupertrendStrategyBTC` | `spot_long` | `E1_expanded` | 89 | `convergence:24` | 2026-09-15 21:44:20 | [archive](user_data/profile_smoke/FSupertrendStrategyBTC-a0068dde-smoke_20200301_20200401-b4807b77-2026-09-15_21-44-20.zip) [log](user_data/convergence_logs/FSupertrendStrategyBTC-a0068dde-ladder.log) |
| `FTT_DWT_FBB_FUTURES` | `futures_long_short` | `E1_expanded` | 941 | `convergence:576:warmup_supplied` | 2026-09-02 07:00:21 | [log](user_data/convergence_logs/FTT_DWT_FBB_FUTURES-ladder.log) |
| `FUTURES` | `futures_long_short` | `E1_expanded` | 1141 | `convergence:1440:warmup_supplied` | 2026-09-06 18:32:53 | [archive](user_data/profile_smoke/FUTURES-676b167a-2026-09-06_18-32-53.zip) [log](user_data/convergence_logs/FUTURES-676b167a-ladder.log) |
| `FVGChannel` | `spot_long` | `E1_expanded` | 12646 | `convergence:2160:warmup_supplied` | 2026-09-06 11:21:21 | [archive](user_data/profile_smoke/FVGChannel-f442e141-2026-09-06_11-21-21.zip) [log](user_data/convergence_logs/FVGChannel-ladder.log) |
| `Fakebuy` | `spot_long` | `E1_expanded` | 329 | `convergence:288:warmup_supplied` | 2026-09-06 06:24:42 | [archive](user_data/profile_smoke/Fakebuy-d1b272c1-2026-09-06_06-24-42.zip) [log](user_data/convergence_logs/Fakebuy-d1b272c1-ladder.log) |
| `FastSupertrendOpt` | `spot_long` | `E1_expanded` | 68 | `convergence:24` | 2026-09-10 08:16:51 | [archive](user_data/profile_smoke/FastSupertrendOpt-fc13211c-smoke_20200301_20200401-b4807b77-2026-09-10_08-16-51.zip) [log](user_data/convergence_logs/FastSupertrendOpt-fc13211c-ladder.log) |
| `FastSupertrend_optim3` | `futures_long_short` | `E1_expanded` | 403 | `convergence:168:warmup_supplied` | 2026-09-02 19:09:03 | [log](user_data/convergence_logs/FastSupertrend_optim3-ladder.log) |
| `FastSupertrend_optim3_rsi_70` | `futures_long_short` | `E1_expanded` | 297 | `convergence:168:warmup_supplied` | 2026-09-02 19:09:29 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_70-ladder.log) |
| `FastSupertrend_optim3_rsi_75` | `futures_long_short` | `E1_expanded` | 320 | `convergence:168:warmup_supplied` | 2026-09-02 19:09:55 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_75-ladder.log) |
| `FastSupertrend_optim3_rsi_752` | `futures_long_short` | `E1_expanded` | 383 | `convergence:168:warmup_supplied` | 2026-09-02 19:10:21 | [log](user_data/convergence_logs/FastSupertrend_optim3_rsi_752-ladder.log) |
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
| `FenixTopProfit` | `futures_long_short` | `E1_expanded` | 28 | `convergence:336:warmup_supplied` | 2026-09-14 19:23:05 | [archive](user_data/profile_smoke/FenixTopProfit-82637b6e-smoke_20200301_20200401-b4807b77-2026-09-14_19-23-05.zip) [log](user_data/convergence_logs/FenixTopProfit-82637b6e-ladder.log) |
| `Fibbo` | `futures_long` | `E1_expanded` | 11 | `convergence:1344:warmup_supplied` | 2026-09-14 19:04:31 | [archive](user_data/profile_smoke/Fibbo-558454bf-smoke_20200301_20210301-fca63e6f-2026-09-14_19-04-31.zip) [log](user_data/convergence_logs/Fibbo-558454bf-ladder.log) |
| `FibonacciEMATrendStrategy` | `futures_long_short` | `E1_expanded` | 91 | `convergence:168:warmup_supplied` | 2026-09-14 19:23:15 | [archive](user_data/profile_smoke/FibonacciEMATrendStrategy-83084414-smoke_20200301_20200401-b4807b77-2026-09-14_19-23-15.zip) [log](user_data/convergence_logs/FibonacciEMATrendStrategy-83084414-ladder.log) |
| `FisherHull` | `spot_long` | `E1_expanded` | 27 | `convergence:1440:warmup_supplied` | 2026-09-09 16:45:19 | [archive](user_data/profile_smoke/FisherHull-40a72168-2026-09-09_16-45-19.zip) [log](user_data/convergence_logs/FisherHull-ladder.log) |
| `FisherTransformStrategy` | `spot_long` | `E1_expanded` | 13590 | `convergence:288:warmup_supplied` | 2026-09-09 21:48:01 | [archive](user_data/profile_smoke/FisherTransformStrategy-496e0ef8-2026-09-09_21-48-01.zip) [log](user_data/convergence_logs/FisherTransformStrategy-ladder.log) |
| `FiveMinCrossAbove` | `spot_long` | `E1_expanded` | 2074 | `convergence:288:warmup_supplied` | 2026-09-07 07:46:28 | [archive](user_data/profile_smoke/FiveMinCrossAbove-798a1782-2026-09-07_07-46-28.zip) [log](user_data/convergence_logs/FiveMinCrossAbove-ladder.log) |
| `FlawlessVictory` | `spot_long` | `E1_expanded` | 10096 | `convergence:96` | 2026-09-14 18:15:10 | [archive](user_data/profile_smoke/FlawlessVictory-16bcd567-2026-09-14_18-15-10.zip) [log](user_data/convergence_logs/FlawlessVictory-ladder.log) |
| `ForexSignal` | `spot_long` | `E1_expanded` | 12678 | `convergence:288:warmup_supplied` | 2026-09-06 06:24:04 | [archive](user_data/profile_smoke/ForexSignal-00154db2-2026-09-06_06-24-04.zip) [log](user_data/convergence_logs/ForexSignal-ladder.log) |
| `FrayStratBTC` | `spot_long` | `E1_expanded` | 8046 | `convergence:672:warmup_supplied` | 2026-09-05 17:31:14 | [archive](user_data/profile_smoke/FrayStratBTC-44376f16-2026-09-05_17-31-14.zip) [log](user_data/convergence_logs/FrayStratBTC-ladder.log) |
| `Freqtrade_backtest_validation_freqtrade1` | `spot_long` | `E1_expanded` | 8627 | `convergence:48:warmup_supplied` | 2026-09-05 23:56:57 | [archive](user_data/profile_smoke/Freqtrade_backtest_validation_freqtrade1-7894fd71-2026-09-05_23-56-57.zip) [log](user_data/convergence_logs/Freqtrade_backtest_validation_freqtrade1-ladder.log) |
| `FrostAuraM115mStrategy` | `spot_long` | `E1_expanded` | 27022 | `convergence:192:warmup_supplied` | 2026-09-05 17:35:44 | [archive](user_data/profile_smoke/FrostAuraM115mStrategy-9a44acc1-2026-09-05_17-35-44.zip) [log](user_data/convergence_logs/FrostAuraM115mStrategy-ladder.log) |
| `FrostAuraM11hStrategy` | `spot_long` | `E1_expanded` | 2159 | `convergence:168:warmup_supplied` | 2026-09-05 17:36:27 | [archive](user_data/profile_smoke/FrostAuraM11hStrategy-9b2c0282-2026-09-05_17-36-27.zip) [log](user_data/convergence_logs/FrostAuraM11hStrategy-ladder.log) |
| `FrostAuraM21hStrategy` | `spot_long` | `E1_expanded` | 11412 | `convergence:192:warmup_supplied` | 2026-09-05 17:37:40 | [archive](user_data/profile_smoke/FrostAuraM21hStrategy-15995b94-2026-09-05_17-37-40.zip) [log](user_data/convergence_logs/FrostAuraM21hStrategy-ladder.log) |
| `FrostAuraM315mStrategy` | `spot_long` | `E1_expanded` | 7728 | `convergence:192:warmup_supplied` | 2026-09-05 17:38:33 | [archive](user_data/profile_smoke/FrostAuraM315mStrategy-4bfcca28-2026-09-05_17-38-33.zip) [log](user_data/convergence_logs/FrostAuraM315mStrategy-ladder.log) |
| `FrostAuraM31hStrategy` | `spot_long` | `E1_expanded` | 2069 | `convergence:168:warmup_supplied` | 2026-09-05 17:39:05 | [archive](user_data/profile_smoke/FrostAuraM31hStrategy-15a97e50-2026-09-05_17-39-05.zip) [log](user_data/convergence_logs/FrostAuraM31hStrategy-ladder.log) |
| `GKD_Baseline` | `spot_long` | `E1_expanded` | 10877 | `convergence:168:warmup_supplied` | 2026-09-06 11:18:54 | [archive](user_data/profile_smoke/GKD_Baseline-3a0dd663-2026-09-06_11-18-54.zip) [log](user_data/convergence_logs/GKD_Baseline-ladder.log) |
| `GKD_BaselineAllMAs` | `spot_long` | `E1_expanded` | 10877 | `convergence:168:warmup_supplied` | 2026-09-06 11:20:16 | [archive](user_data/profile_smoke/GKD_BaselineAllMAs-d132f795-2026-09-06_11-20-16.zip) [log](user_data/convergence_logs/GKD_BaselineAllMAs-ladder.log) |
| `GKD_FisherTransformMTF` | `spot_long` | `E1_expanded` | 3972 | `convergence:168:warmup_supplied` | 2026-09-06 11:22:37 | [archive](user_data/profile_smoke/GKD_FisherTransformMTF-dba7d6d9-2026-09-06_11-22-37.zip) [log](user_data/convergence_logs/GKD_FisherTransformMTF-ladder.log) |
| `GKD_HurstExponent` | `spot_long` | `E1_expanded` | 5142 | `convergence:168:warmup_supplied` | 2026-09-06 11:25:06 | [archive](user_data/profile_smoke/GKD_HurstExponent-48f852cd-2026-09-06_11-25-06.zip) [log](user_data/convergence_logs/GKD_HurstExponent-ladder.log) |
| `GKD_PFE` | `spot_long` | `E1_expanded` | 11053 | `convergence:168:warmup_supplied` | 2026-09-06 11:25:04 | [archive](user_data/profile_smoke/GKD_PFE-3611d4c1-2026-09-06_11-25-04.zip) [log](user_data/convergence_logs/GKD_PFE-ladder.log) |
| `GPTREV` | `spot_long` | `E1_expanded` | 20 | `convergence:1440:warmup_supplied` | 2026-09-09 16:43:40 | [archive](user_data/profile_smoke/GPTREV-7fba7b92-2026-09-09_16-43-40.zip) [log](user_data/convergence_logs/GPTREV-ladder.log) |
| `GRIDDMIPRICEStrategyFutureV5Long` | `futures_long_short` | `E1_expanded` | 12 | `convergence:1440:warmup_supplied` | 2026-09-06 16:37:51 | [archive](user_data/profile_smoke/GRIDDMIPRICEStrategyFutureV5Long-93a155ed-2026-09-06_16-37-51.zip) [log](user_data/convergence_logs/GRIDDMIPRICEStrategyFutureV5Long-93a155ed-ladder.log) |
| `GRIDDMIPRICEStrategyFutureV5Short` | `futures_long_short` | `E1_expanded` | 9 | `convergence:84:warmup_supplied` | 2026-09-06 16:38:14 | [archive](user_data/profile_smoke/GRIDDMIPRICEStrategyFutureV5Short-0a37b705-2026-09-06_16-38-14.zip) [log](user_data/convergence_logs/GRIDDMIPRICEStrategyFutureV5Short-0a37b705-ladder.log) |
| `GRIDDMIPRICEStrategySpot` | `futures_long` | `E1_expanded` | 19 | `convergence:1440:warmup_supplied` | 2026-09-06 17:58:32 | [archive](user_data/profile_smoke/GRIDDMIPRICEStrategySpot-bfcd5e8a-2026-09-06_17-58-32.zip) [log](user_data/convergence_logs/GRIDDMIPRICEStrategySpot-bfcd5e8a-ladder.log) |
| `GnF_V2` | `futures_long_short` | `E1_expanded` | 240 | `convergence:336:warmup_supplied` | 2026-09-14 19:31:56 | [archive](user_data/profile_smoke/GnF_V2-0f3ac6fa-smoke_20200301_20200401-b4807b77-2026-09-14_19-31-56.zip) [log](user_data/convergence_logs/GnF_V2-0f3ac6fa-ladder.log) |
| `GodCard` | `spot_long` | `E1_expanded` | 290 | `convergence:288:warmup_supplied` | 2026-09-06 06:26:51 | [archive](user_data/profile_smoke/GodCard-e992df91-2026-09-06_06-26-51.zip) [log](user_data/convergence_logs/GodCard-ladder.log) |
| `GoldenCrossStrategy` | `spot_long` | `E1_expanded` | 5091 | `convergence:2016:warmup_supplied` | 2026-09-09 21:50:00 | [archive](user_data/profile_smoke/GoldenCrossStrategy-6a5ef5e3-2026-09-09_21-50-00.zip) [log](user_data/convergence_logs/GoldenCrossStrategy-ladder.log) |
| `Gumbo1` | `spot_long` | `E1_expanded` | 15510 | `convergence:288:warmup_supplied` | 2026-09-07 11:53:51 | [archive](user_data/profile_smoke/Gumbo1-d72ec524-2026-09-07_11-53-51.zip) [log](user_data/convergence_logs/Gumbo1-ladder.log) |
| `HEAD_SHOULDER` | `futures_long_short` | `E1_expanded` | 3 | `convergence:96` | 2026-09-06 18:13:56 | [archive](user_data/profile_smoke/HEAD_SHOULDER-3272caf5-2026-09-06_18-13-56.zip) [log](user_data/convergence_logs/HEAD_SHOULDER-3272caf5-ladder.log) |
| `Hacklemore` | `spot_long` | `E1_expanded` | 135 | `convergence:288:warmup_supplied` | 2026-08-31 16:39:41 | [archive](user_data/profile_smoke/Hacklemore-2026-08-31_16-39-41.zip) [log](user_data/convergence_logs/Hacklemore-ladder.log) |
| `Hacklemore2` | `spot_long` | `E1_expanded` | 886 | `convergence:192:warmup_supplied` | 2026-09-06 07:21:38 | [archive](user_data/profile_smoke/Hacklemore2-25466732-2026-09-06_07-21-38.zip) [log](user_data/convergence_logs/Hacklemore2-ladder.log) |
| `Hacklemore3` | `spot_long` | `E1_expanded` | 11 | `convergence:288:warmup_supplied` | 2026-09-10 05:42:59 | [archive](user_data/profile_smoke/Hacklemore3-ec775e72-smoke_20200301_20200401-b4807b77-2026-09-10_05-42-59.zip) [log](user_data/convergence_logs/Hacklemore3-ladder.log) |
| `Hacklemost` | `spot_long` | `E1_expanded` | 176 | `convergence:288:warmup_supplied` | 2026-09-07 18:01:08 | [archive](user_data/profile_smoke/Hacklemost-f578e820-2026-09-07_18-01-08.zip) [log](user_data/convergence_logs/Hacklemost-ladder.log) |
| `Hammer` | `spot_long` | `E1_expanded` | 36 | `convergence:288:warmup_supplied` | 2026-09-09 07:32:38 | [archive](user_data/profile_smoke/Hammer-c157cbf6-2026-09-09_07-32-38.zip) [log](user_data/convergence_logs/Hammer-c157cbf6-ladder.log) |
| `HansenSmaOffsetV1` | `spot_long` | `E1_expanded` | 92 | `convergence:96:warmup_supplied` | 2026-09-05 17:40:54 | [archive](user_data/profile_smoke/HansenSmaOffsetV1-d633da96-2026-09-05_17-40-54.zip) [log](user_data/convergence_logs/HansenSmaOffsetV1-ladder.log) |
| `HedgeAdaptiveRegimeStrategy` | `futures_long_short` | `E1_expanded` | 5020 | `convergence:1440:warmup_supplied` | 2026-09-20 18:28:38 | [archive](user_data/profile_smoke/HedgeAdaptiveRegimeStrategy-abda3016-smoke_20200301_20200401-b4807b77-2026-09-20_18-28-38.zip) [log](user_data/convergence_logs/HedgeAdaptiveRegimeStrategy-abda3016-ladder.log) |
| `HeikinAshiStrategy` | `spot_long` | `E1_expanded` | 13147 | `convergence:288:warmup_supplied` | 2026-09-09 21:50:22 | [archive](user_data/profile_smoke/HeikinAshiStrategy-97b9bc04-2026-09-09_21-50-22.zip) [log](user_data/convergence_logs/HeikinAshiStrategy-ladder.log) |
| `HighFreqDemo` | `futures_long_short` | `E1_expanded` | 5914 | `convergence:1440:warmup_supplied` | 2026-09-08 17:14:22 | [archive](user_data/profile_smoke/HighFreqDemo-006fcf90-2026-09-08_17-14-22.zip) [log](user_data/convergence_logs/HighFreqDemo-006fcf90-ladder.log) |
| `HigherHighStrategy` | `spot_long` | `E1_expanded` | 13466 | `convergence:288:warmup_supplied` | 2026-09-09 21:52:14 | [archive](user_data/profile_smoke/HigherHighStrategy-f85df8fe-2026-09-09_21-52-14.zip) [log](user_data/convergence_logs/HigherHighStrategy-ladder.log) |
| `HilbertSineWave` | `spot_long` | `E1_expanded` | 3755 | `convergence:336:warmup_supplied` | 2026-09-06 11:45:35 | [archive](user_data/profile_smoke/HilbertSineWave-b856be2d-2026-09-06_11-45-35.zip) [log](user_data/convergence_logs/HilbertSineWave-ladder.log) |
| `HourBasedStrategy` | `spot_long` | `E1_expanded` | 8823 | `convergence:24:warmup_supplied` | 2026-09-05 17:40:44 | [archive](user_data/profile_smoke/HourBasedStrategy-f0bf90ca-2026-09-05_17-40-44.zip) [log](user_data/convergence_logs/HourBasedStrategy-ladder.log) |
| `HourBasedStrategy_5m` | `spot_long` | `E1_expanded` | 286 | `convergence:288:warmup_supplied` | 2026-09-17 12:16:58 | [archive](user_data/profile_smoke/HourBasedStrategy_5m-1aaa006f-smoke_20200301_20200401-b4807b77-2026-09-17_12-16-58.zip) [log](user_data/convergence_logs/HourBasedStrategy_5m-ladder.log) |
| `INSIDEUP` | `spot_long` | `E1_expanded` | 489 | `convergence:90:warmup_supplied` | 2026-09-06 06:46:13 | [archive](user_data/profile_smoke/INSIDEUP-dc5f3886-2026-09-06_06-46-13.zip) [log](user_data/convergence_logs/INSIDEUP-ladder.log) |
| `Ichess` | `spot_long` | `E1_expanded` | 313 | `convergence:90:warmup_supplied` | 2026-09-05 17:41:46 | [archive](user_data/profile_smoke/Ichess-d1ad6a71-2026-09-05_17-41-46.zip) [log](user_data/convergence_logs/Ichess-ladder.log) |
| `Ichi` | `spot_long` | `E1_expanded` | 274 | `convergence:96:warmup_supplied` | 2026-09-09 21:01:45 | [archive](user_data/profile_smoke/Ichi-252e3d9b-2026-09-09_21-01-45.zip) [log](user_data/convergence_logs/Ichi-252e3d9b-ladder.log) |
| `Ichimoku` | `spot_long` | `E1_expanded` | 7250 | `convergence:288:warmup_supplied` | 2026-09-05 17:46:50 | [archive](user_data/profile_smoke/Ichimoku-91a3635e-2026-09-05_17-46-50.zip) [log](user_data/convergence_logs/Ichimoku-ladder.log) |
| `IchimokuCloudBreakoutStrategy` | `futures_long_short` | `E1_expanded` | 190 | `convergence:84` | 2026-09-14 19:31:43 | [archive](user_data/profile_smoke/IchimokuCloudBreakoutStrategy-8a53a90c-smoke_20200301_20200401-b4807b77-2026-09-14_19-31-43.zip) [log](user_data/convergence_logs/IchimokuCloudBreakoutStrategy-8a53a90c-ladder.log) |
| `IchimokuCloudStrategy` | `spot_long` | `E1_expanded` | 709 | `convergence:6` | 2026-09-09 21:51:21 | [archive](user_data/profile_smoke/IchimokuCloudStrategy-eede6bf0-2026-09-09_21-51-21.zip) [log](user_data/convergence_logs/IchimokuCloudStrategy-eede6bf0-ladder.log) |
| `IchimokuSimpleStrategy` | `spot_long` | `E1_expanded` | 13304 | `convergence:288:warmup_supplied` | 2026-09-09 21:53:39 | [archive](user_data/profile_smoke/IchimokuSimpleStrategy-c36eb299-2026-09-09_21-53-39.zip) [log](user_data/convergence_logs/IchimokuSimpleStrategy-ladder.log) |
| `IchimokuStrategy` | `spot_long` | `E1_expanded` | 90 | `convergence:480:warmup_supplied` | 2026-09-03 21:08:41 | [archive](user_data/profile_smoke/IchimokuStrategy-67b217c6-2026-09-03_21-08-41.zip) [log](user_data/convergence_logs/IchimokuStrategy-67b217c6-ladder.log) |
| `Ichimoku_SenkouSpanCross` | `spot_long` | `E1_expanded` | 1 | `convergence:180:warmup_supplied` | 2026-09-03 21:09:11 | [archive](user_data/profile_smoke/Ichimoku_SenkouSpanCross-d71627c7-2026-09-03_21-09-11.zip) [log](user_data/convergence_logs/Ichimoku_SenkouSpanCross-d71627c7-ladder.log) |
| `Ichimoku_v12` | `spot_long` | `E1_expanded` | 7 | `convergence:180:warmup_supplied` | 2026-09-01 19:41:45 | [archive](user_data/profile_smoke/Ichimoku_v12-2026-09-01_19-41-45.zip) [log](user_data/convergence_logs/Ichimoku_v12-ladder.log) |
| `Ichimoku_v30` | `spot_long` | `E1_expanded` | 3 | `convergence:180:warmup_supplied` | 2026-09-01 19:42:22 | [archive](user_data/profile_smoke/Ichimoku_v30-2026-09-01_19-42-22.zip) [log](user_data/convergence_logs/Ichimoku_v30-ladder.log) |
| `Ichimoku_v31` | `spot_long` | `E1_expanded` | 1443 | `convergence:150` | 2026-09-05 17:47:01 | [archive](user_data/profile_smoke/Ichimoku_v31-7208d46d-2026-09-05_17-47-01.zip) [log](user_data/convergence_logs/Ichimoku_v31-ladder.log) |
| `Ichimoku_v32` | `spot_long` | `E1_expanded` | 3 | `convergence:180:warmup_supplied` | 2026-09-01 19:43:00 | [archive](user_data/profile_smoke/Ichimoku_v32-2026-09-01_19-43-00.zip) [log](user_data/convergence_logs/Ichimoku_v32-ladder.log) |
| `Ichimoku_v33` | `spot_long` | `E1_expanded` | 3 | `convergence:180:warmup_supplied` | 2026-09-01 19:43:37 | [archive](user_data/profile_smoke/Ichimoku_v33-2026-09-01_19-43-37.zip) [log](user_data/convergence_logs/Ichimoku_v33-ladder.log) |
| `Ichimoku_v37` | `spot_long` | `E1_expanded` | 512 | `convergence:150` | 2026-09-05 17:49:34 | [archive](user_data/profile_smoke/Ichimoku_v37-18e3ba92-2026-09-05_17-49-34.zip) [log](user_data/convergence_logs/Ichimoku_v37-ladder.log) |
| `ImpulseV1` | `spot_long` | `E1_expanded` | 10200 | `convergence:288:warmup_supplied` | 2026-09-07 16:10:19 | [archive](user_data/profile_smoke/ImpulseV1-506c42b6-2026-09-07_16-10-19.zip) [log](user_data/convergence_logs/ImpulseV1-ladder.log) |
| `InformativeSample` | `spot_long` | `E1_expanded` | 11247 | `convergence:576:warmup_supplied` | 2026-09-06 21:15:43 | [archive](user_data/profile_smoke/InformativeSample-56ecc655-2026-09-06_21-15-43.zip) [log](user_data/convergence_logs/InformativeSample-ladder.log) |
| `Inverse` | `spot_long` | `E1_expanded` | 2278 | `convergence:720:warmup_supplied` | 2026-09-05 12:12:07 | [archive](user_data/profile_smoke/Inverse-bfe272f9-2026-09-05_12-12-07.zip) [log](user_data/convergence_logs/Inverse-ladder.log) |
| `InverseV2` | `spot_long` | `E1_expanded` | 889 | `convergence:720:warmup_supplied` | 2026-09-05 12:13:27 | [archive](user_data/profile_smoke/InverseV2-cc2ff292-2026-09-05_12-13-27.zip) [log](user_data/convergence_logs/InverseV2-ladder.log) |
| `JuicyTrend` | `spot_long` | `E1_expanded` | 13919 | `convergence:1344:warmup_supplied` | 2026-09-06 02:30:30 | [archive](user_data/profile_smoke/JuicyTrend-d2cb2ca2-2026-09-06_02-30-30.zip) [log](user_data/convergence_logs/JuicyTrend-ladder.log) |
| `JustROCR` | `spot_long` | `E1_expanded` | 21 | `convergence:24:warmup_supplied` | 2026-09-01 19:44:53 | [archive](user_data/profile_smoke/JustROCR-2026-09-01_19-44-53.zip) [log](user_data/convergence_logs/JustROCR-ladder.log) |
| `JustROCR2` | `spot_long` | `E1_expanded` | 35 | `convergence:288:warmup_supplied` | 2026-09-01 19:45:29 | [archive](user_data/profile_smoke/JustROCR2-2026-09-01_19-45-29.zip) [log](user_data/convergence_logs/JustROCR2-ladder.log) |
| `JustROCR3` | `spot_long` | `E1_expanded` | 94 | `convergence:288:warmup_supplied` | 2026-09-01 19:46:10 | [archive](user_data/profile_smoke/JustROCR3-2026-09-01_19-46-10.zip) [log](user_data/convergence_logs/JustROCR3-ladder.log) |
| `JustROCR4` | `spot_long` | `E1_expanded` | 9 | `convergence:288:warmup_supplied` | 2026-09-01 19:46:51 | [archive](user_data/profile_smoke/JustROCR4-2026-09-01_19-46-51.zip) [log](user_data/convergence_logs/JustROCR4-ladder.log) |
| `JustROCR5` | `spot_long` | `E1_expanded` | 43 | `convergence:1440:warmup_supplied` | 2026-09-01 19:47:36 | [archive](user_data/profile_smoke/JustROCR5-2026-09-01_19-47-36.zip) [log](user_data/convergence_logs/JustROCR5-ladder.log) |
| `JustROCR6` | `spot_long` | `E1_expanded` | 107 | `convergence:1440:warmup_supplied` | 2026-09-01 19:48:20 | [archive](user_data/profile_smoke/JustROCR6-2026-09-01_19-48-20.zip) [log](user_data/convergence_logs/JustROCR6-ladder.log) |
| `KAMACCIRSI` | `spot_long` | `E1_expanded` | 8484 | `convergence:576:warmup_supplied` | 2026-09-07 08:18:39 | [archive](user_data/profile_smoke/KAMACCIRSI-38dc74b2-2026-09-07_08-18-39.zip) [log](user_data/convergence_logs/KAMACCIRSI-ladder.log) |
| `KAMACCIRSI_new` | `spot_long` | `E1_expanded` | 127 | `convergence:288:warmup_supplied` | 2026-09-07 18:03:42 | [archive](user_data/profile_smoke/KAMACCIRSI_new-0443f98b-2026-09-07_18-03-42.zip) [log](user_data/convergence_logs/KAMACCIRSI_new-ladder.log) |
| `KC_BB` | `spot_long` | `E1_expanded` | 536 | `convergence:288:warmup_supplied` | 2026-09-06 07:01:11 | [archive](user_data/profile_smoke/KC_BB-2f26e143-2026-09-06_07-01-11.zip) [log](user_data/convergence_logs/KC_BB-ladder.log) |
| `KamaFama_2_20250115` | `futures_long` | `E1_expanded` | 50 | `convergence:2016:warmup_supplied` | 2026-09-14 19:23:37 | [archive](user_data/profile_smoke/KamaFama_2_20250115-5ad5321a-smoke_20200301_20200401-b4807b77-2026-09-14_19-23-37.zip) [log](user_data/convergence_logs/KamaFama_2_20250115-5ad5321a-ladder.log) |
| `KeltnerBounce` | `spot_long` | `E1_expanded` | 1 | `convergence:576:warmup_supplied` | 2026-09-09 07:32:46 | [archive](user_data/profile_smoke/KeltnerBounce-63c48d3d-2026-09-09_07-32-46.zip) [log](user_data/convergence_logs/KeltnerBounce-63c48d3d-ladder.log) |
| `KeltnerBounce_Shorts` | `futures_short` | `E1_expanded` | 102 | `convergence:576:warmup_supplied` | 2026-09-14 19:22:00 | [archive](user_data/profile_smoke/KeltnerBounce_Shorts-008d9c62-smoke_20200301_20200401-b4807b77-2026-09-14_19-22-00.zip) [log](user_data/convergence_logs/KeltnerBounce_Shorts-008d9c62-ladder.log) |
| `KeltnerChannelStrategy` | `spot_long` | `E1_expanded` | 10510 | `convergence:288:warmup_supplied` | 2026-09-09 21:54:34 | [archive](user_data/profile_smoke/KeltnerChannelStrategy-aef954af-2026-09-09_21-54-34.zip) [log](user_data/convergence_logs/KeltnerChannelStrategy-ladder.log) |
| `KeltnerChannels` | `spot_long` | `E1_expanded` | 3 | `convergence:576:warmup_supplied` | 2026-09-06 18:26:48 | [archive](user_data/profile_smoke/KeltnerChannels-1628032a-2026-09-06_18-26-48.zip) [log](user_data/convergence_logs/KeltnerChannels-1628032a-ladder.log) |
| `Lateralus` | `spot_long` | `E1_expanded` | 44 | `convergence:288:warmup_supplied` | 2026-09-17 12:20:54 | [archive](user_data/profile_smoke/Lateralus-31a5ed07-smoke_20200301_20200401-b4807b77-2026-09-17_12-20-54.zip) [log](user_data/convergence_logs/Lateralus-ladder.log) |
| `LeoStrategy` | `spot_long` | `E1_expanded` | 15 | `convergence:540:warmup_supplied` | 2026-09-06 18:31:18 | [archive](user_data/profile_smoke/LeoStrategy-a4770535-2026-09-06_18-31-18.zip) [log](user_data/convergence_logs/LeoStrategy-a4770535-ladder.log) |
| `LinearRegressionStrategy` | `spot_long` | `E1_expanded` | 13193 | `convergence:288:warmup_supplied` | 2026-09-09 21:55:53 | [archive](user_data/profile_smoke/LinearRegressionStrategy-1c3f226f-2026-09-09_21-55-53.zip) [log](user_data/convergence_logs/LinearRegressionStrategy-ladder.log) |
| `Low_BB` | `spot_long` | `E1_expanded` | 43 | `convergence:1440:warmup_supplied` | 2026-09-09 16:21:52 | [archive](user_data/profile_smoke/Low_BB-36ee484b-2026-09-09_16-21-52.zip) [log](user_data/convergence_logs/Low_BB-ladder.log) |
| `LuxOSC` | `spot_long` | `E1_expanded` | 12082 | `convergence:576:warmup_supplied` | 2026-09-06 21:38:43 | [archive](user_data/profile_smoke/LuxOSC-1a3b1a68-2026-09-06_21-38-43.zip) [log](user_data/convergence_logs/LuxOSC-ladder.log) |
| `MAC` | `spot_long` | `E1_expanded` | 46 | `convergence:90:warmup_supplied` | 2026-09-05 18:02:35 | [archive](user_data/profile_smoke/MAC-1f6368e6-2026-09-05_18-02-35.zip) [log](user_data/convergence_logs/MAC-ladder.log) |
| `MACD003` | `spot_long` | `E1_expanded` | 46 | `convergence:576:warmup_supplied` | 2026-09-06 18:29:22 | [archive](user_data/profile_smoke/MACD003-5def5884-2026-09-06_18-29-22.zip) [log](user_data/convergence_logs/MACD003-5def5884-ladder.log) |
| `MACD9fall` | `spot_long` | `E1_expanded` | 9 | `convergence:720:warmup_supplied` | 2026-09-05 15:10:15 | [archive](user_data/profile_smoke/MACD9fall-3ef1c8d0-2026-09-05_15-10-15.zip) [log](user_data/convergence_logs/MACD9fall-3ef1c8d0-ladder.log) |
| `MACDCCI` | `spot_long` | `E1_expanded` | 16 | `convergence:336:warmup_supplied` | 2026-09-01 19:49:03 | [archive](user_data/profile_smoke/MACDCCI-2026-09-01_19-49-03.zip) [log](user_data/convergence_logs/MACDCCI-ladder.log) |
| `MACDCross` | `spot_long` | `E1_expanded` | 144 | `convergence:288:warmup_supplied` | 2026-09-06 18:29:32 | [archive](user_data/profile_smoke/MACDCross-c19524f6-2026-09-06_18-29-32.zip) [log](user_data/convergence_logs/MACDCross-c19524f6-ladder.log) |
| `MACDCrossoverWithTrend` | `spot_long` | `E1_expanded` | 1420 | `convergence:720:warmup_supplied` | 2026-09-06 01:36:40 | [archive](user_data/profile_smoke/MACDCrossoverWithTrend-b6e682ec-2026-09-06_01-36-40.zip) [log](user_data/convergence_logs/MACDCrossoverWithTrend-b6e682ec-ladder.log) |
| `MACDRL` | `futures_long` | `E1_expanded` | 200 | `convergence:2016:warmup_supplied` | 2026-09-02 07:27:57 | [log](user_data/convergence_logs/MACDRL-ladder.log) |
| `MACDRS` | `futures_long_short` | `E1_expanded` | 613 | `convergence:2016:warmup_supplied` | 2026-09-02 07:30:14 | [log](user_data/convergence_logs/MACDRS-ladder.log) |
| `MACDRSI200` | `spot_long` | `E1_expanded` | 170 | `convergence:2016:warmup_supplied` | 2026-09-01 19:49:47 | [archive](user_data/profile_smoke/MACDRSI200-2026-09-01_19-49-47.zip) [log](user_data/convergence_logs/MACDRSI200-ladder.log) |
| `MACDStrategy` | `spot_long` | `E1_expanded` | 16894 | `convergence:288:warmup_supplied` | 2026-09-05 18:11:58 | [archive](user_data/profile_smoke/MACDStrategy-79bd402e-2026-09-05_18-11-58.zip) [log](user_data/convergence_logs/MACDStrategy-79bd402e-ladder.log) |
| `MACDStrategyADA` | `spot_long` | `E1_expanded` | 4031 | `convergence:288:warmup_supplied` | 2026-09-05 13:25:10 | [archive](user_data/profile_smoke/MACDStrategyADA-0cde35d1-2026-09-05_13-25-10.zip) [log](user_data/convergence_logs/MACDStrategyADA-ladder.log) |
| `MACDStrategyAVAX` | `spot_long` | `E1_expanded` | 2379 | `convergence:288:warmup_supplied` | 2026-09-05 13:25:59 | [archive](user_data/profile_smoke/MACDStrategyAVAX-33d55a2a-2026-09-05_13-25-59.zip) [log](user_data/convergence_logs/MACDStrategyAVAX-ladder.log) |
| `MACDStrategyBTC` | `spot_long` | `E1_expanded` | 6162 | `convergence:288:warmup_supplied` | 2026-09-06 13:59:51 | [archive](user_data/profile_smoke/MACDStrategyBTC-b69154e4-2026-09-06_13-59-51.zip) [log](user_data/convergence_logs/MACDStrategyBTC-ladder.log) |
| `MACDStrategyENJ` | `spot_long` | `E1_expanded` | 1895 | `convergence:288:warmup_supplied` | 2026-09-05 13:29:38 | [archive](user_data/profile_smoke/MACDStrategyENJ-65cf3e26-2026-09-05_13-29-38.zip) [log](user_data/convergence_logs/MACDStrategyENJ-ladder.log) |
| `MACDStrategyETC` | `spot_long` | `E1_expanded` | 8682 | `convergence:288:warmup_supplied` | 2026-09-05 13:37:45 | [archive](user_data/profile_smoke/MACDStrategyETC-d1d0ba70-2026-09-05_13-37-45.zip) [log](user_data/convergence_logs/MACDStrategyETC-ladder.log) |
| `MACDStrategySOL` | `spot_long` | `E1_expanded` | 1744 | `convergence:288:warmup_supplied` | 2026-09-05 13:33:19 | [archive](user_data/profile_smoke/MACDStrategySOL-4e10aebc-2026-09-05_13-33-19.zip) [log](user_data/convergence_logs/MACDStrategySOL-ladder.log) |
| `MACDStrategyXRP` | `spot_long` | `E1_expanded` | 4147 | `convergence:288:warmup_supplied` | 2026-09-05 13:37:09 | [archive](user_data/profile_smoke/MACDStrategyXRP-8c63d974-2026-09-05_13-37-09.zip) [log](user_data/convergence_logs/MACDStrategyXRP-ladder.log) |
| `MACDStrategy_crossed` | `spot_long` | `E1_expanded` | 4384 | `convergence:288:warmup_supplied` | 2026-09-05 18:13:24 | [archive](user_data/profile_smoke/MACDStrategy_crossed-4427a4d5-2026-09-05_18-13-24.zip) [log](user_data/convergence_logs/MACDStrategy_crossed-ladder.log) |
| `MACDTurn` | `spot_long` | `E1_expanded` | 6 | `convergence:288:warmup_supplied` | 2026-09-06 18:29:40 | [archive](user_data/profile_smoke/MACDTurn-e059bfc3-2026-09-06_18-29-40.zip) [log](user_data/convergence_logs/MACDTurn-e059bfc3-ladder.log) |
| `MACDZeroCrossStrategy` | `spot_long` | `E1_expanded` | 296 | `convergence:90:warmup_supplied` | 2026-09-06 11:06:17 | [archive](user_data/profile_smoke/MACDZeroCrossStrategy-18eb90f7-2026-09-06_11-06-17.zip) [log](user_data/convergence_logs/MACDZeroCrossStrategy-ladder.log) |
| `MACD_EMA` | `spot_long` | `E1_expanded` | 15348 | `convergence:2016:warmup_supplied` | 2026-09-05 18:16:16 | [archive](user_data/profile_smoke/MACD_EMA-ebd8acf7-2026-09-05_18-16-16.zip) [log](user_data/convergence_logs/MACD_EMA-ladder.log) |
| `MACD_TRIPLE_MA` | `spot_long` | `E1_expanded` | 11429 | `convergence:288:warmup_supplied` | 2026-09-05 18:17:02 | [archive](user_data/profile_smoke/MACD_TRIPLE_MA-56a72b4d-2026-09-05_18-17-02.zip) [log](user_data/convergence_logs/MACD_TRIPLE_MA-ladder.log) |
| `MACD_TRI_EMA` | `spot_long` | `E1_expanded` | 13543 | `convergence:288:warmup_supplied` | 2026-09-05 18:20:20 | [archive](user_data/profile_smoke/MACD_TRI_EMA-8f2fd8e3-2026-09-05_18-20-20.zip) [log](user_data/convergence_logs/MACD_TRI_EMA-ladder.log) |
| `MADisplaceV3` | `spot_long` | `E1_expanded` | 561 | `convergence:288:warmup_supplied` | 2026-09-05 18:20:00 | [archive](user_data/profile_smoke/MADisplaceV3-1326c489-2026-09-05_18-20-00.zip) [log](user_data/convergence_logs/MADisplaceV3-ladder.log) |
| `MFI` | `spot_long` | `E1_expanded` | 15897 | `convergence:288:warmup_supplied` | 2026-09-05 18:24:13 | [archive](user_data/profile_smoke/MFI-5705ffee-2026-09-05_18-24-13.zip) [log](user_data/convergence_logs/MFI-ladder.log) |
| `MFI2` | `spot_long` | `E1_expanded` | 75 | `convergence:576:warmup_supplied` | 2026-09-06 18:27:02 | [archive](user_data/profile_smoke/MFI2-9083ee50-2026-09-06_18-27-02.zip) [log](user_data/convergence_logs/MFI2-9083ee50-ladder.log) |
| `MFIRSICross` | `spot_long` | `E1_expanded` | 330 | `convergence:288:warmup_supplied` | 2026-09-06 18:28:49 | [archive](user_data/profile_smoke/MFIRSICross-00cbcde3-2026-09-06_18-28-49.zip) [log](user_data/convergence_logs/MFIRSICross-00cbcde3-ladder.log) |
| `MabStra` | `spot_long` | `E1_expanded` | 3592 | `convergence:42:warmup_supplied` | 2026-09-06 09:14:27 | [archive](user_data/profile_smoke/MabStra-43fd2626-2026-09-06_09-14-27.zip) [log](user_data/convergence_logs/MabStra-43fd2626-ladder.log) |
| `MacdAdxStrategy` | `spot_long` | `E1_expanded` | 14209 | `convergence:288:warmup_supplied` | 2026-09-09 21:58:08 | [archive](user_data/profile_smoke/MacdAdxStrategy-c52df265-2026-09-09_21-58-08.zip) [log](user_data/convergence_logs/MacdAdxStrategy-ladder.log) |
| `MacdZeroCrossStrategy` | `spot_long` | `E1_expanded` | 15596 | `convergence:288:warmup_supplied` | 2026-09-09 21:58:18 | [archive](user_data/profile_smoke/MacdZeroCrossStrategy-4830233c-2026-09-09_21-58-18.zip) [log](user_data/convergence_logs/MacdZeroCrossStrategy-4830233c-ladder.log) |
| `MacheteV8b` | `spot_long` | `E1_expanded` | 77 | `convergence:500` | 2026-09-03 20:52:20 | [archive](user_data/profile_smoke/MacheteV8b-b42642cf-2026-09-03_20-52-20.zip) [log](user_data/convergence_logs/MacheteV8b-ladder.log) |
| `MacheteV8bRallimod` | `spot_long` | `E1_expanded` | 63 | `convergence:1344:warmup_supplied` | 2026-09-03 20:55:26 | [archive](user_data/profile_smoke/MacheteV8bRallimod-019087a6-2026-09-03_20-55-26.zip) [log](user_data/convergence_logs/MacheteV8bRallimod-ladder.log) |
| `MacheteV8bRallimod2` | `spot_long` | `E1_expanded` | 11 | `convergence:2016:warmup_supplied` | 2026-09-03 20:56:01 | [archive](user_data/profile_smoke/MacheteV8bRallimod2-2a221533-2026-09-03_20-56-01.zip) [log](user_data/convergence_logs/MacheteV8bRallimod2-ladder.log) |
| `Magic_Trailing_Stoploss` | `spot_long` | `E1_expanded` | 5473 | `convergence:24:warmup_supplied` | 2026-09-05 15:06:57 | [archive](user_data/profile_smoke/Magic_Trailing_Stoploss-1cf71129-2026-09-05_15-06-57.zip) [log](user_data/convergence_logs/Magic_Trailing_Stoploss-1cf71129-ladder.log) |
| `MarketChyperHyperStrategy` | `spot_long` | `E1_expanded` | 3127 | `convergence:336` | 2026-09-05 18:25:53 | [archive](user_data/profile_smoke/MarketChyperHyperStrategy-d7bac38e-2026-09-05_18-25-53.zip) [log](user_data/convergence_logs/MarketChyperHyperStrategy-ladder.log) |
| `Maro4hMacdSd` | `spot_long` | `E1_expanded` | 17803 | `convergence:288:warmup_supplied` | 2026-09-06 07:04:01 | [archive](user_data/profile_smoke/Maro4hMacdSd-579080b7-2026-09-06_07-04-01.zip) [log](user_data/convergence_logs/Maro4hMacdSd-ladder.log) |
| `Martin` | `spot_long` | `E1_expanded` | 10999 | `convergence:288:warmup_supplied` | 2026-09-05 18:31:23 | [archive](user_data/profile_smoke/Martin-39d3a2e9-2026-09-05_18-31-23.zip) [log](user_data/convergence_logs/Martin-ladder.log) |
| `MeanReversionTrend` | `spot_long` | `E1_expanded` | 56 | `convergence:336:warmup_supplied` | 2026-09-15 21:00:36 | [archive](user_data/profile_smoke/MeanReversionTrend-9c6041b5-smoke_20200301_20200601-9c543975-2026-09-15_21-00-36.zip) [log](user_data/convergence_logs/MeanReversionTrend-9c6041b5-ladder.log) |
| `MiniLambo` | `spot_long` | `E1_expanded` | 163 | `convergence:2880:warmup_supplied` | 2026-09-09 16:22:34 | [archive](user_data/profile_smoke/MiniLambo-32df6766-2026-09-09_16-22-34.zip) [log](user_data/convergence_logs/MiniLambo-ladder.log) |
| `MiniLambo_TBS` | `spot_long` | `E1_expanded` | 1181 | `convergence:1440:warmup_supplied` | 2026-09-14 23:43:35 | [archive](user_data/profile_smoke/MiniLambo_TBS-773406bb-smoke_20200301_20200401-b4807b77-2026-09-14_23-43-35.zip) [log](user_data/convergence_logs/MiniLambo_TBS-773406bb-ladder.log) |
| `Minmax` | `spot_long` | `E1_expanded` | 3184 | `convergence:24:warmup_supplied` | 2026-09-05 18:54:33 | [archive](user_data/profile_smoke/Minmax-476cf2d9-2026-09-05_18-54-33.zip) [log](user_data/convergence_logs/Minmax-ladder.log) |
| `MomStrategy` | `spot_long` | `E1_expanded` | 13167 | `convergence:336:warmup_supplied` | 2026-09-06 07:05:04 | [archive](user_data/profile_smoke/MomStrategy-63021af4-2026-09-06_07-05-04.zip) [log](user_data/convergence_logs/MomStrategy-ladder.log) |
| `MomentumCCITrendStrategy` | `futures_long_short` | `E1_expanded` | 10 | `convergence:7:warmup_supplied` | 2026-09-14 19:29:31 | [archive](user_data/profile_smoke/MomentumCCITrendStrategy-f0099a2a-smoke_20200301_20200601-9c543975-2026-09-14_19-29-31.zip) [log](user_data/convergence_logs/MomentumCCITrendStrategy-f0099a2a-ladder.log) |
| `MomentumScoreStrategy` | `spot_long` | `E1_expanded` | 13524 | `convergence:288:warmup_supplied` | 2026-09-09 22:01:33 | [archive](user_data/profile_smoke/MomentumScoreStrategy-81e52e71-2026-09-09_22-01-33.zip) [log](user_data/convergence_logs/MomentumScoreStrategy-ladder.log) |
| `Momentumv2` | `spot_long` | `E1_expanded` | 2072 | `convergence:540:warmup_supplied` | 2026-09-06 07:05:58 | [archive](user_data/profile_smoke/Momentumv2-a2ecd9e8-2026-09-06_07-05-58.zip) [log](user_data/convergence_logs/Momentumv2-ladder.log) |
| `MoneyFlowStrategy` | `spot_long` | `E1_expanded` | 16311 | `convergence:576:warmup_supplied` | 2026-09-09 22:01:13 | [archive](user_data/profile_smoke/MoneyFlowStrategy-11170f24-2026-09-09_22-01-13.zip) [log](user_data/convergence_logs/MoneyFlowStrategy-ladder.log) |
| `MontrealStrategy` | `spot_long` | `E1_expanded` | 23143 | `convergence:192:warmup_supplied` | 2026-09-05 18:48:37 | [archive](user_data/profile_smoke/MontrealStrategy-1e851d26-2026-09-05_18-48-37.zip) [log](user_data/convergence_logs/MontrealStrategy-ladder.log) |
| `MultiActionZone` | `spot_long` | `E1_expanded` | 290 | `convergence:540:warmup_supplied` | 2026-09-15 21:00:04 | [archive](user_data/profile_smoke/MultiActionZone-179b96b7-smoke_20200301_20200601-9c543975-2026-09-15_21-00-04.zip) [log](user_data/convergence_logs/MultiActionZone-179b96b7-ladder.log) |
| `MultiFactorConfluenceStrategy` | `spot_long` | `E1_expanded` | 4445 | `convergence:540:warmup_supplied` | 2026-09-09 22:02:20 | [archive](user_data/profile_smoke/MultiFactorConfluenceStrategy-195fb188-2026-09-09_22-02-20.zip) [log](user_data/convergence_logs/MultiFactorConfluenceStrategy-ladder.log) |
| `MultiMA_TSL` | `spot_long` | `E1_expanded` | 6 | `convergence:2016:warmup_supplied` | 2026-09-04 04:48:31 | [archive](user_data/profile_smoke/MultiMA_TSL-432f3842-2026-09-04_04-48-31.zip) [log](user_data/convergence_logs/MultiMA_TSL-ladder.log) |
| `MultiMA_TSL3b` | `spot_long` | `E1_expanded` | 25 | `convergence:2016:warmup_supplied` | 2026-09-10 08:20:24 | [archive](user_data/profile_smoke/MultiMA_TSL3b-394a8370-smoke_20200301_20200401-b4807b77-2026-09-10_08-20-24.zip) [log](user_data/convergence_logs/MultiMA_TSL3b-394a8370-ladder.log) |
| `MultiOffsetLamboV0` | `spot_long` | `E1_expanded` | 174 | `convergence:2016:warmup_supplied` | 2026-09-05 12:16:40 | [archive](user_data/profile_smoke/MultiOffsetLamboV0-0dfa7f19-2026-09-05_12-16-40.zip) [log](user_data/convergence_logs/MultiOffsetLamboV0-ladder.log) |
| `NASOSRv6_private_Reinuvader_20211121` | `spot_long` | `E1_expanded` | 452 | `convergence:2016:warmup_supplied` | 2026-08-31 15:35:19 | [archive](user_data/profile_smoke/NASOSRv6_private_Reinuvader_20211121-2026-08-31_15-35-19.zip) [log](user_data/convergence_logs/NASOSRv6_private_Reinuvader_20211121-ladder.log) |
| `NASOSv4` | `spot_long` | `E1_expanded` | 79 | `convergence:2016:warmup_supplied` | 2026-09-06 14:46:56 | [archive](user_data/profile_smoke/NASOSv4-d420d31d-2026-09-06_14-46-56.zip) [log](user_data/convergence_logs/NASOSv4-ladder.log) |
| `NASOSv5` | `spot_long` | `E1_expanded` | 664 | `convergence:2016:warmup_supplied` | 2026-09-05 18:59:32 | [archive](user_data/profile_smoke/NASOSv5-fdf79059-2026-09-05_18-59-32.zip) [log](user_data/convergence_logs/NASOSv5-ladder.log) |
| `NASOSv5HO` | `spot_long` | `E1_expanded` | 440 | `convergence:2016:warmup_supplied` | 2026-09-14 23:43:56 | [archive](user_data/profile_smoke/NASOSv5HO-4fa36018-smoke_20200301_20200401-b4807b77-2026-09-14_23-43-56.zip) [log](user_data/convergence_logs/NASOSv5HO-4fa36018-ladder.log) |
| `NASOSv5PD` | `spot_long` | `E1_expanded` | 289 | `convergence:2016:warmup_supplied` | 2026-09-14 23:44:04 | [archive](user_data/profile_smoke/NASOSv5PD-ad088fe3-smoke_20200301_20200401-b4807b77-2026-09-14_23-44-04.zip) [log](user_data/convergence_logs/NASOSv5PD-ad088fe3-ladder.log) |
| `NASOSv5SL` | `spot_long` | `E1_expanded` | 513 | `convergence:2016:warmup_supplied` | 2026-09-17 12:22:15 | [archive](user_data/profile_smoke/NASOSv5SL-15c5cded-smoke_20200301_20200401-b4807b77-2026-09-17_12-22-15.zip) [log](user_data/convergence_logs/NASOSv5SL-15c5cded-ladder.log) |
| `NASOSv5_antipump` | `spot_long` | `E1_expanded` | 625 | `convergence:2016:warmup_supplied` | 2026-09-14 23:43:50 | [archive](user_data/profile_smoke/NASOSv5_antipump-90e3cc66-smoke_20200301_20200401-b4807b77-2026-09-14_23-43-50.zip) [log](user_data/convergence_logs/NASOSv5_antipump-90e3cc66-ladder.log) |
| `NASOSv5_mod1` | `spot_long` | `E1_expanded` | 71 | `convergence:2016:warmup_supplied` | 2026-09-06 14:52:16 | [archive](user_data/profile_smoke/NASOSv5_mod1-dc29bda0-2026-09-06_14-52-16.zip) [log](user_data/convergence_logs/NASOSv5_mod1-ladder.log) |
| `NASOSv5_mod1_DanMod` | `spot_long` | `E1_expanded` | 65 | `convergence:2016:warmup_supplied` | 2026-09-06 15:08:41 | [archive](user_data/profile_smoke/NASOSv5_mod1_DanMod-8ccd7243-2026-09-06_15-08-41.zip) [log](user_data/convergence_logs/NASOSv5_mod1_DanMod-ladder.log) |
| `NASOSv5_mod2` | `spot_long` | `E1_expanded` | 62 | `convergence:2016:warmup_supplied` | 2026-09-06 14:52:23 | [archive](user_data/profile_smoke/NASOSv5_mod2-215c0845-2026-09-06_14-52-23.zip) [log](user_data/convergence_logs/NASOSv5_mod2-ladder.log) |
| `NASOSv5_mod3` | `spot_long` | `E1_expanded` | 74 | `convergence:2016:warmup_supplied` | 2026-09-06 14:52:30 | [archive](user_data/profile_smoke/NASOSv5_mod3-2ce3e304-2026-09-06_14-52-30.zip) [log](user_data/convergence_logs/NASOSv5_mod3-ladder.log) |
| `NDrop` | `spot_long` | `E1_expanded` | 238 | `convergence:576:warmup_supplied` | 2026-09-06 18:27:19 | [archive](user_data/profile_smoke/NDrop-035a8156-2026-09-06_18-27-19.zip) [log](user_data/convergence_logs/NDrop-035a8156-ladder.log) |
| `NEWTEST15m` | `spot_long` | `E1_expanded` | 2172 | `convergence:672:warmup_supplied` | 2026-09-05 17:35:03 | [archive](user_data/profile_smoke/NEWTEST15m-27c783bc-2026-09-05_17-35-03.zip) [log](user_data/convergence_logs/NEWTEST15m-ladder.log) |
| `NFI46` | `spot_long` | `E1_expanded` | 57 | `convergence:2016:warmup_supplied` | 2026-09-06 22:01:15 | [archive](user_data/profile_smoke/NFI46-38afdd57-2026-09-06_22-01-15.zip) [log](user_data/convergence_logs/NFI46-ladder.log) |
| `NFI46Frog` | `spot_long` | `E1_expanded` | 180 | `convergence:2016:warmup_supplied` | 2026-09-03 20:56:46 | [archive](user_data/profile_smoke/NFI46Frog-c5debb17-2026-09-03_20-56-46.zip) [log](user_data/convergence_logs/NFI46Frog-ladder.log) |
| `NFI46FrogZ` | `spot_long` | `E1_expanded` | 13871 | `convergence:2016:warmup_supplied` | 2026-09-08 00:07:36 | [archive](user_data/profile_smoke/NFI46FrogZ-00590e50-2026-09-08_00-07-36.zip) [log](user_data/convergence_logs/NFI46FrogZ-ladder.log) |
| `NFI46Offset` | `spot_long` | `E1_expanded` | 754 | `convergence:2016:warmup_supplied` | 2026-09-05 19:18:56 | [archive](user_data/profile_smoke/NFI46Offset-5834ae71-2026-09-05_19-18-56.zip) [log](user_data/convergence_logs/NFI46Offset-ladder.log) |
| `NFI46OffsetHOA1` | `spot_long` | `E1_expanded` | 832 | `convergence:2016:warmup_supplied` | 2026-09-05 19:20:35 | [archive](user_data/profile_smoke/NFI46OffsetHOA1-91c94296-2026-09-05_19-20-35.zip) [log](user_data/convergence_logs/NFI46OffsetHOA1-ladder.log) |
| `NFI46Z` | `spot_long` | `E1_expanded` | 460 | `convergence:2016:warmup_supplied` | 2026-09-05 19:23:16 | [archive](user_data/profile_smoke/NFI46Z-8a414576-2026-09-05_19-23-16.zip) [log](user_data/convergence_logs/NFI46Z-ladder.log) |
| `NFI47V2` | `spot_long` | `E1_expanded` | 396 | `convergence:2016:warmup_supplied` | 2026-09-06 07:27:56 | [archive](user_data/profile_smoke/NFI47V2-415abd68-2026-09-06_07-27-56.zip) [log](user_data/convergence_logs/NFI47V2-ladder.log) |
| `NFI4Frog` | `spot_long` | `E1_expanded` | 188 | `convergence:2016:warmup_supplied` | 2026-09-03 20:57:25 | [archive](user_data/profile_smoke/NFI4Frog-a1f40e4d-2026-09-03_20-57-25.zip) [log](user_data/convergence_logs/NFI4Frog-ladder.log) |
| `NFI5MOHO` | `spot_long` | `E1_expanded` | 315 | `convergence:2016:warmup_supplied` | 2026-09-05 19:27:10 | [archive](user_data/profile_smoke/NFI5MOHO-b6de4e08-2026-09-05_19-27-10.zip) [log](user_data/convergence_logs/NFI5MOHO-ladder.log) |
| `NFI5MOHO2` | `spot_long` | `E1_expanded` | 1194 | `convergence:2016:warmup_supplied` | 2026-09-06 07:29:46 | [archive](user_data/profile_smoke/NFI5MOHO2-de424a53-2026-09-06_07-29-46.zip) [log](user_data/convergence_logs/NFI5MOHO2-ladder.log) |
| `NFI5MOHO_WIP` | `spot_long` | `E1_expanded` | 749 | `convergence:2016:warmup_supplied` | 2026-09-05 19:29:41 | [archive](user_data/profile_smoke/NFI5MOHO_WIP-25adadea-2026-09-05_19-29-41.zip) [log](user_data/convergence_logs/NFI5MOHO_WIP-ladder.log) |
| `NFI5MOHO_WIP_1` | `spot_long` | `E1_expanded` | 769 | `convergence:2016:warmup_supplied` | 2026-09-06 07:31:12 | [archive](user_data/profile_smoke/NFI5MOHO_WIP_1-ecdff35f-2026-09-06_07-31-12.zip) [log](user_data/convergence_logs/NFI5MOHO_WIP_1-ladder.log) |
| `NFI5MOHO_WIP_2` | `spot_long` | `E1_expanded` | 778 | `convergence:2016:warmup_supplied` | 2026-09-06 07:32:32 | [archive](user_data/profile_smoke/NFI5MOHO_WIP_2-9551ae6f-2026-09-06_07-32-32.zip) [log](user_data/convergence_logs/NFI5MOHO_WIP_2-ladder.log) |
| `NFI7MOHO` | `spot_long` | `E1_expanded` | 1633 | `convergence:2016:warmup_supplied` | 2026-09-07 13:58:53 | [archive](user_data/profile_smoke/NFI7MOHO-4963f506-2026-09-07_13-58-53.zip) [log](user_data/convergence_logs/NFI7MOHO-ladder.log) |
| `NFINextMOHO` | `spot_long` | `E1_expanded` | 1213 | `convergence:2016:warmup_supplied` | 2026-09-07 14:05:23 | [archive](user_data/profile_smoke/NFINextMOHO-92310738-2026-09-07_14-05-23.zip) [log](user_data/convergence_logs/NFINextMOHO-ladder.log) |
| `NFINextMOHO2` | `spot_long` | `E1_expanded` | 1489 | `convergence:2016:warmup_supplied` | 2026-09-07 14:01:51 | [archive](user_data/profile_smoke/NFINextMOHO2-6491efe9-2026-09-07_14-01-51.zip) [log](user_data/convergence_logs/NFINextMOHO2-ladder.log) |
| `NFINextMultiOffsetAndHO` | `spot_long` | `E1_expanded` | 882 | `convergence:2016:warmup_supplied` | 2026-09-07 14:11:14 | [archive](user_data/profile_smoke/NFINextMultiOffsetAndHO-8d25b109-2026-09-07_14-11-14.zip) [log](user_data/convergence_logs/NFINextMultiOffsetAndHO-ladder.log) |
| `NFINextMultiOffsetAndHO2` | `spot_long` | `E1_expanded` | 34 | `convergence:2016:warmup_supplied` | 2026-09-09 16:39:10 | [archive](user_data/profile_smoke/NFINextMultiOffsetAndHO2-9c883070-2026-09-09_16-39-10.zip) [log](user_data/convergence_logs/NFINextMultiOffsetAndHO2-ladder.log) |
| `NSeq` | `spot_long` | `E1_expanded` | 103 | `convergence:576:warmup_supplied` | 2026-09-06 18:27:29 | [archive](user_data/profile_smoke/NSeq-b0a87061-2026-09-06_18-27-29.zip) [log](user_data/convergence_logs/NSeq-b0a87061-ladder.log) |
| `NWEv6_new` | `spot_long` | `E1_expanded` | 6611 | `convergence:480:warmup_supplied` | 2026-09-07 12:55:59 | [archive](user_data/profile_smoke/NWEv6_new-3a4963e7-2026-09-07_12-55-59.zip) [log](user_data/convergence_logs/NWEv6_new-ladder.log) |
| `NormalizerStrategy` | `spot_long` | `E1_expanded` | 2893 | `convergence:610` | 2026-09-06 07:43:37 | [archive](user_data/profile_smoke/NormalizerStrategy-8ddea525-2026-09-06_07-43-37.zip) [log](user_data/convergence_logs/NormalizerStrategy-ladder.log) |
| `NormalizerStrategyHO2` | `spot_long` | `E1_expanded` | 2421 | `convergence:610` | 2026-09-05 19:36:41 | [archive](user_data/profile_smoke/NormalizerStrategyHO2-db1d20f9-2026-09-05_19-36-41.zip) [log](user_data/convergence_logs/NormalizerStrategyHO2-ladder.log) |
| `Nostalgia` | `spot_long` | `E1_expanded` | 641 | `convergence:2016:warmup_supplied` | 2026-09-07 05:02:58 | [archive](user_data/profile_smoke/Nostalgia-ad35efae-2026-09-07_05-02-58.zip) [log](user_data/convergence_logs/Nostalgia-ladder.log) |
| `NostalgiaForInfinity772martinsk3` | `spot_long` | `E1_expanded` | 21 | `convergence:2016:warmup_supplied` | 2026-08-31 15:54:00 | [archive](user_data/profile_smoke/NostalgiaForInfinity772martinsk3-2026-08-31_15-54-00.zip) [log](user_data/convergence_logs/NostalgiaForInfinity772martinsk3-ladder.log) |
| `NostalgiaForInfinityNext772` | `spot_long` | `E1_expanded` | 38 | `convergence:2016:warmup_supplied` | 2026-08-31 15:35:53 | [archive](user_data/profile_smoke/NostalgiaForInfinityNext772-2026-08-31_15-35-53.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNext772-8d6ca7f0-ladder.log) |
| `NostalgiaForInfinityNextGen` | `spot_long` | `E1_expanded` | 141 | `convergence:2880:warmup_supplied` | 2026-09-05 19:38:33 | [archive](user_data/profile_smoke/NostalgiaForInfinityNextGen-3c2dae5e-2026-09-05_19-38-33.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNextGen-ladder.log) |
| `NostalgiaForInfinityNextGen_TSL` | `spot_long` | `E1_expanded` | 121 | `convergence:2880:warmup_supplied` | 2026-09-06 07:45:31 | [archive](user_data/profile_smoke/NostalgiaForInfinityNextGen_TSL-b5f4b310-2026-09-06_07-45-31.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNextGen_TSL-ladder.log) |
| `NostalgiaForInfinityNextV7155` | `spot_long` | `E1_expanded` | 9 | `convergence:2016:warmup_supplied` | 2026-08-31 15:32:47 | [archive](user_data/profile_smoke/NostalgiaForInfinityNextV7155-2026-08-31_15-32-47.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNextV7155-fd1e8353-ladder.log) |
| `NostalgiaForInfinityNext_ChangeToTower_V6_Short` | `futures_long_short` | `E1_expanded` | 27 | `convergence:2016:warmup_supplied` | 2026-09-14 19:29:48 | [archive](user_data/profile_smoke/NostalgiaForInfinityNext_ChangeToTower_V6_Short-f39c2e96-smoke_20200301_20200401-b4807b77-2026-09-14_19-29-48.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNext_ChangeToTower_V6_Short-f39c2e96-ladder.log) |
| `NostalgiaForInfinityNext_maximizer` | `spot_long` | `E1_expanded` | 25 | `convergence:2016:warmup_supplied` | 2026-08-31 16:05:16 | [archive](user_data/profile_smoke/NostalgiaForInfinityNext_maximizer-2026-08-31_16-05-16.zip) [log](user_data/convergence_logs/NostalgiaForInfinityNext_maximizer-78e1c6b3-ladder.log) |
| `NostalgiaForInfinityV1` | `spot_long` | `E1_expanded` | 2880 | `convergence:2016:warmup_supplied` | 2026-09-05 19:41:35 | [archive](user_data/profile_smoke/NostalgiaForInfinityV1-ed100932-2026-09-05_19-41-35.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV1-ladder.log) |
| `NostalgiaForInfinityV2` | `spot_long` | `E1_expanded` | 656 | `convergence:2016:warmup_supplied` | 2026-09-05 19:43:11 | [archive](user_data/profile_smoke/NostalgiaForInfinityV2-f3282564-2026-09-05_19-43-11.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV2-ladder.log) |
| `NostalgiaForInfinityV3` | `spot_long` | `E1_expanded` | 847 | `convergence:2016:warmup_supplied` | 2026-09-05 19:45:19 | [archive](user_data/profile_smoke/NostalgiaForInfinityV3-1319d6e9-2026-09-05_19-45-19.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV3-ladder.log) |
| `NostalgiaForInfinityV4` | `spot_long` | `E1_expanded` | 308 | `convergence:2016:warmup_supplied` | 2026-09-05 19:46:17 | [archive](user_data/profile_smoke/NostalgiaForInfinityV4-522cd25a-2026-09-05_19-46-17.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV4-ladder.log) |
| `NostalgiaForInfinityV4HO` | `spot_long` | `E1_expanded` | 313 | `convergence:2016:warmup_supplied` | 2026-09-05 19:49:11 | [archive](user_data/profile_smoke/NostalgiaForInfinityV4HO-bfa1fa35-2026-09-05_19-49-11.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV4HO-ladder.log) |
| `NostalgiaForInfinityV5` | `spot_long` | `E1_expanded` | 480 | `convergence:2016:warmup_supplied` | 2026-09-06 22:18:55 | [archive](user_data/profile_smoke/NostalgiaForInfinityV5-1f038111-2026-09-06_22-18-55.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV5-ladder.log) |
| `NostalgiaForInfinityV5MultiOffsetAndHO` | `spot_long` | `E1_expanded` | 1481 | `convergence:2016:warmup_supplied` | 2026-09-06 15:58:08 | [archive](user_data/profile_smoke/NostalgiaForInfinityV5MultiOffsetAndHO-ef0e67dc-2026-09-06_15-58-08.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV5MultiOffsetAndHO-ladder.log) |
| `NostalgiaForInfinityV5MultiOffsetAndHO2` | `spot_long` | `E1_expanded` | 1148 | `convergence:2016:warmup_supplied` | 2026-09-06 22:23:24 | [archive](user_data/profile_smoke/NostalgiaForInfinityV5MultiOffsetAndHO2-aedfafde-2026-09-06_22-23-24.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV5MultiOffsetAndHO2-ladder.log) |
| `NostalgiaForInfinityV6` | `spot_long` | `E1_expanded` | 564 | `convergence:2016:warmup_supplied` | 2026-09-07 08:58:02 | [archive](user_data/profile_smoke/NostalgiaForInfinityV6-84e37cca-2026-09-07_08-58-02.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV6-ladder.log) |
| `NostalgiaForInfinityV6HO` | `spot_long` | `E1_expanded` | 564 | `convergence:2016:warmup_supplied` | 2026-09-07 14:34:28 | [archive](user_data/profile_smoke/NostalgiaForInfinityV6HO-92ce7768-2026-09-07_14-34-28.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV6HO-ladder.log) |
| `NostalgiaForInfinityV7` | `spot_long` | `E1_expanded` | 542 | `convergence:2016:warmup_supplied` | 2026-09-08 01:11:59 | [archive](user_data/profile_smoke/NostalgiaForInfinityV7-5a32c38a-2026-09-08_01-11-59.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV7-ladder.log) |
| `NostalgiaForInfinityV7_7_2` | `spot_long` | `E1_expanded` | 40 | `convergence:2016:warmup_supplied` | 2026-08-31 16:05:55 | [archive](user_data/profile_smoke/NostalgiaForInfinityV7_7_2-2026-08-31_16-05-55.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV7_7_2-19436abd-ladder.log) |
| `NostalgiaForInfinityV7_SMA` | `spot_long` | `E1_expanded` | 722 | `convergence:2016:warmup_supplied` | 2026-09-07 09:04:14 | [archive](user_data/profile_smoke/NostalgiaForInfinityV7_SMA-65c4e695-2026-09-07_09-04-14.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV7_SMA-ladder.log) |
| `NostalgiaForInfinityV7_SMAv2_1` | `spot_long` | `E1_expanded` | 425 | `convergence:2016:warmup_supplied` | 2026-09-06 22:32:24 | [archive](user_data/profile_smoke/NostalgiaForInfinityV7_SMAv2_1-3b4479f9-2026-09-06_22-32-24.zip) [log](user_data/convergence_logs/NostalgiaForInfinityV7_SMAv2_1-ladder.log) |
| `NostalgiaForInfinityX` | `spot_long` | `E1_expanded` | 28 | `convergence:2016:warmup_supplied` | 2026-08-31 14:50:00 | [archive](user_data/profile_smoke/NostalgiaForInfinityX-2026-08-31_14-50-00.zip) [log](user_data/convergence_logs/NostalgiaForInfinityX-ladder.log) |
| `NotAnotherSMAOffsetStrategy` | `spot_long` | `E1_expanded` | 700 | `convergence:2016:warmup_supplied` | 2026-09-05 12:40:37 | [archive](user_data/profile_smoke/NotAnotherSMAOffsetStrategy-7155ba0b-2026-09-05_12-40-37.zip) [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategy-ladder.log) |
| `NotAnotherSMAOffsetStrategyHO` | `spot_long` | `E1_expanded` | 73 | `convergence:2016:warmup_supplied` | 2026-09-17 12:11:33 | [archive](user_data/profile_smoke/NotAnotherSMAOffsetStrategyHO-46b0975f-smoke_20200301_20200401-b4807b77-2026-09-17_12-11-33.zip) [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyHO-ladder.log) |
| `NotAnotherSMAOffsetStrategyHOv3` | `spot_long` | `E1_expanded` | 650 | `convergence:2016:warmup_supplied` | 2026-09-05 12:28:47 | [archive](user_data/profile_smoke/NotAnotherSMAOffsetStrategyHOv3-a8426b53-2026-09-05_12-28-47.zip) [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyHOv3-ladder.log) |
| `NotAnotherSMAOffsetStrategyLite` | `spot_long` | `E1_expanded` | 1122 | `convergence:2016:warmup_supplied` | 2026-09-05 12:31:29 | [archive](user_data/profile_smoke/NotAnotherSMAOffsetStrategyLite-8bc980ab-2026-09-05_12-31-29.zip) [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyLite-ladder.log) |
| `NotAnotherSMAOffsetStrategyModHO` | `spot_long` | `E1_expanded` | 951 | `convergence:2016:warmup_supplied` | 2026-09-05 12:32:31 | [archive](user_data/profile_smoke/NotAnotherSMAOffsetStrategyModHO-9595a546-2026-09-05_12-32-31.zip) [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyModHO-ladder.log) |
| `NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901` | `spot_long` | `E1_expanded` | 949 | `convergence:2016:warmup_supplied` | 2026-09-06 07:50:33 | [archive](user_data/profile_smoke/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901-7f3e81e1-2026-09-06_07-50-33.zip) [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901-ladder.log) |
| `NotAnotherSMAOffsetStrategyX1` | `spot_long` | `E1_expanded` | 483 | `convergence:2016:warmup_supplied` | 2026-09-05 20:02:53 | [archive](user_data/profile_smoke/NotAnotherSMAOffsetStrategyX1-d4abd7ee-2026-09-05_20-02-53.zip) [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyX1-ladder.log) |
| `NotAnotherSMAOffsetStrategy_uzi` | `spot_long` | `E1_expanded` | 529 | `convergence:2016:warmup_supplied` | 2026-09-05 12:34:18 | [archive](user_data/profile_smoke/NotAnotherSMAOffsetStrategy_uzi-e05784ab-2026-09-05_12-34-18.zip) [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategy_uzi-ladder.log) |
| `NowoIchimoku1hV2` | `spot_long` | `E1_expanded` | 3195 | `convergence:168:warmup_supplied` | 2026-09-05 20:09:45 | [archive](user_data/profile_smoke/NowoIchimoku1hV2-03eb2650-2026-09-05_20-09-45.zip) [log](user_data/convergence_logs/NowoIchimoku1hV2-ladder.log) |
| `NowoIchimoku5mV2` | `spot_long` | `E1_expanded` | 49 | `native` | 2026-08-31 15:19:45 | [archive](user_data/profile_smoke/NowoIchimoku5mV2-2026-08-31_15-19-45.zip) |
| `ONUR` | `spot_long` | `E1_expanded` | 632 | `convergence:192:warmup_supplied` | 2026-09-06 07:52:14 | [archive](user_data/profile_smoke/ONUR-1758f273-2026-09-06_07-52-14.zip) [log](user_data/convergence_logs/ONUR-ladder.log) |
| `ORBAlgo` | `futures_long_short` | `E1_expanded` | 228 | `convergence:200` | 2026-09-14 19:29:58 | [archive](user_data/profile_smoke/ORBAlgo-091aa388-smoke_20200301_20200401-b4807b77-2026-09-14_19-29-58.zip) [log](user_data/convergence_logs/ORBAlgo-091aa388-ladder.log) |
| `Obelisk_Ichimoku_Slow_v1` | `spot_long` | `E1_expanded` | 30 | `convergence:180` | 2026-09-05 15:15:09 | [archive](user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1-933691c1-2026-09-05_15-15-09.zip) [log](user_data/convergence_logs/Obelisk_Ichimoku_Slow_v1-933691c1-ladder.log) |
| `Obelisk_Ichimoku_Slow_v1_1` | `spot_long` | `E1_expanded` | 30 | `convergence:180` | 2026-09-05 15:16:19 | [archive](user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1_1-877a1601-2026-09-05_15-16-19.zip) [log](user_data/convergence_logs/Obelisk_Ichimoku_Slow_v1_1-877a1601-ladder.log) |
| `Obelisk_Ichimoku_Slow_v1_2` | `spot_long` | `E1_expanded` | 29 | `convergence:180` | 2026-09-05 15:17:11 | [archive](user_data/profile_smoke/Obelisk_Ichimoku_Slow_v1_2-fe861e17-2026-09-05_15-17-11.zip) [log](user_data/convergence_logs/Obelisk_Ichimoku_Slow_v1_2-fe861e17-ladder.log) |
| `Obelisk_TradePro_Ichi_v1_1` | `spot_long` | `E1_expanded` | 4477 | `convergence:24` | 2026-09-06 22:43:27 | [archive](user_data/profile_smoke/Obelisk_TradePro_Ichi_v1_1-d9ad6391-2026-09-06_22-43-27.zip) [log](user_data/convergence_logs/Obelisk_TradePro_Ichi_v1_1-d9ad6391-ladder.log) |
| `Obelisk_TradePro_Ichi_v2` | `spot_long` | `E1_expanded` | 35 | `convergence:180` | 2026-09-05 15:18:10 | [archive](user_data/profile_smoke/Obelisk_TradePro_Ichi_v2-c9b4a814-2026-09-05_15-18-10.zip) [log](user_data/convergence_logs/Obelisk_TradePro_Ichi_v2-c9b4a814-ladder.log) |
| `Obelisk_TradePro_Ichi_v2_1` | `spot_long` | `E1_expanded` | 5525 | `convergence:180` | 2026-09-06 22:45:04 | [archive](user_data/profile_smoke/Obelisk_TradePro_Ichi_v2_1-b409b943-2026-09-06_22-45-04.zip) [log](user_data/convergence_logs/Obelisk_TradePro_Ichi_v2_1-b409b943-ladder.log) |
| `Obelisk_TradePro_Ichi_v2_2` | `spot_long` | `E1_expanded` | 103 | `convergence:180` | 2026-09-05 15:04:05 | [archive](user_data/profile_smoke/Obelisk_TradePro_Ichi_v2_2-596055ad-2026-09-05_15-04-05.zip) [log](user_data/convergence_logs/Obelisk_TradePro_Ichi_v2_2-596055ad-ladder.log) |
| `OmaGann` | `spot_long` | `E1_expanded` | 9521 | `convergence:168:warmup_supplied` | 2026-09-06 11:47:48 | [archive](user_data/profile_smoke/OmaGann-9401627a-2026-09-06_11-47-48.zip) [log](user_data/convergence_logs/OmaGann-ladder.log) |
| `OversoldReversion` | `spot_long` | `E1_expanded` | 25 | `convergence:1250` | 2026-09-05 15:08:45 | [archive](user_data/profile_smoke/OversoldReversion-dcb09e33-2026-09-05_15-08-45.zip) [log](user_data/convergence_logs/OversoldReversion-dcb09e33-ladder.log) |
| `PRICEFOLLOWING` | `spot_long` | `E1_expanded` | 210 | `convergence:288:warmup_supplied` | 2026-09-06 23:06:45 | [archive](user_data/profile_smoke/PRICEFOLLOWING-1b9eb440-2026-09-06_23-06-45.zip) [log](user_data/convergence_logs/PRICEFOLLOWING-ladder.log) |
| `PRICEFOLLOWINGX` | `spot_long` | `E1_expanded` | 964 | `convergence:672:warmup_supplied` | 2026-09-05 20:45:36 | [archive](user_data/profile_smoke/PRICEFOLLOWINGX-cc825e55-2026-09-05_20-45-36.zip) [log](user_data/convergence_logs/PRICEFOLLOWINGX-ladder.log) |
| `ParabolicSarStrategy` | `spot_long` | `E1_expanded` | 11392 | `convergence:288:warmup_supplied` | 2026-09-09 22:03:47 | [archive](user_data/profile_smoke/ParabolicSarStrategy-b60d3532-2026-09-09_22-03-47.zip) [log](user_data/convergence_logs/ParabolicSarStrategy-ladder.log) |
| `PatternRecognition` | `spot_long` | `E1_expanded` | 9 | `convergence:1:warmup_supplied` | 2026-09-09 21:20:02 | [archive](user_data/profile_smoke/PatternRecognition-1dee08f2-2026-09-09_21-20-02.zip) [log](user_data/convergence_logs/PatternRecognition-ladder.log) |
| `Patterns2` | `spot_long` | `E1_expanded` | 117 | `convergence:288:warmup_supplied` | 2026-09-06 18:27:39 | [archive](user_data/profile_smoke/Patterns2-39f34344-2026-09-06_18-27-39.zip) [log](user_data/convergence_logs/Patterns2-39f34344-ladder.log) |
| `Persia` | `spot_long` | `E1_expanded` | 176 | `convergence:2016:warmup_supplied` | 2026-09-04 10:30:24 | [archive](user_data/profile_smoke/Persia-f2f6ac3e-2026-09-04_10-30-24.zip) [log](user_data/convergence_logs/Persia-f2f6ac3e-ladder.log) |
| `PolymarketMeanReversionStrategy` | `spot_long` | `E1_expanded` | 2 | `convergence:180:warmup_supplied` | 2026-09-09 07:43:34 | [archive](user_data/profile_smoke/PolymarketMeanReversionStrategy-9c33dc8c-2026-09-09_07-43-34.zip) [log](user_data/convergence_logs/PolymarketMeanReversionStrategy-9c33dc8c-ladder.log) |
| `PolymarketMomentumStrategy` | `spot_long` | `E1_expanded` | 10 | `convergence:180:warmup_supplied` | 2026-09-09 07:43:38 | [archive](user_data/profile_smoke/PolymarketMomentumStrategy-aee6b82b-2026-09-09_07-43-38.zip) [log](user_data/convergence_logs/PolymarketMomentumStrategy-aee6b82b-ladder.log) |
| `PowerTower` | `spot_long` | `E1_expanded` | 3696 | `convergence:288` | 2026-09-06 01:46:16 | [archive](user_data/profile_smoke/PowerTower-89714471-2026-09-06_01-46-16.zip) [log](user_data/convergence_logs/PowerTower-ladder.log) |
| `PpoMomentumStrategy` | `spot_long` | `E1_expanded` | 13478 | `convergence:288:warmup_supplied` | 2026-09-09 22:06:00 | [archive](user_data/profile_smoke/PpoMomentumStrategy-b9a916e0-2026-09-09_22-06-00.zip) [log](user_data/convergence_logs/PpoMomentumStrategy-ladder.log) |
| `PriceActionCandleStrategy` | `spot_long` | `E1_expanded` | 13470 | `convergence:288:warmup_supplied` | 2026-09-09 22:06:11 | [archive](user_data/profile_smoke/PriceActionCandleStrategy-bafd96a9-2026-09-09_22-06-11.zip) [log](user_data/convergence_logs/PriceActionCandleStrategy-ladder.log) |
| `PriceChannelStrategy` | `spot_long` | `E1_expanded` | 9700 | `convergence:288:warmup_supplied` | 2026-09-09 22:08:06 | [archive](user_data/profile_smoke/PriceChannelStrategy-a656b945-2026-09-09_22-08-06.zip) [log](user_data/convergence_logs/PriceChannelStrategy-ladder.log) |
| `PumpDetector` | `spot_long` | `E1_expanded` | 20538 | `convergence:2016:warmup_supplied` | 2026-09-06 07:58:14 | [archive](user_data/profile_smoke/PumpDetector-382b1730-2026-09-06_07-58-14.zip) [log](user_data/convergence_logs/PumpDetector-ladder.log) |
| `QuickBuyStrategy` | `spot_long` | `E1_expanded` | 838 | `convergence:168:warmup_supplied` | 2026-09-10 10:12:35 | [archive](user_data/profile_smoke/QuickBuyStrategy-e4bfe3e8-smoke_20200301_20200401-b4807b77-2026-09-10_10-12-35.zip) [log](user_data/convergence_logs/QuickBuyStrategy-e4bfe3e8-ladder.log) |
| `Quickie` | `spot_long` | `E1_expanded` | 6331 | `convergence:288:warmup_supplied` | 2026-09-05 20:57:52 | [archive](user_data/profile_smoke/Quickie-dab280e0-2026-09-05_20-57-52.zip) [log](user_data/convergence_logs/Quickie-ladder.log) |
| `RSI` | `spot_long` | `E1_expanded` | 466 | `convergence:192:warmup_supplied` | 2026-09-06 07:56:28 | [archive](user_data/profile_smoke/RSI-6a079fd1-2026-09-06_07-56-28.zip) [log](user_data/convergence_logs/RSI-ladder.log) |
| `RSIBB02` | `spot_long` | `E1_expanded` | 10 | `convergence:168:warmup_supplied` | 2026-09-01 19:50:27 | [archive](user_data/profile_smoke/RSIBB02-2026-09-01_19-50-27.zip) [log](user_data/convergence_logs/RSIBB02-ladder.log) |
| `RSIDirectionalWithTrend` | `spot_long` | `E1_expanded` | 752 | `convergence:720:warmup_supplied` | 2026-09-06 01:37:35 | [archive](user_data/profile_smoke/RSIDirectionalWithTrend-0268a91f-2026-09-06_01-37-35.zip) [log](user_data/convergence_logs/RSIDirectionalWithTrend-0268a91f-ladder.log) |
| `RSIDirectionalWithTrendSlow` | `spot_long` | `E1_expanded` | 546 | `convergence:2160:warmup_supplied` | 2026-09-06 01:38:30 | [archive](user_data/profile_smoke/RSIDirectionalWithTrendSlow-247b9c8f-2026-09-06_01-38-30.zip) [log](user_data/convergence_logs/RSIDirectionalWithTrendSlow-247b9c8f-ladder.log) |
| `RSI_BB` | `spot_long` | `E1_expanded` | 12152 | `convergence:192:warmup_supplied` | 2026-09-07 16:47:57 | [archive](user_data/profile_smoke/RSI_BB-ebe5244c-2026-09-07_16-47-57.zip) [log](user_data/convergence_logs/RSI_BB-ladder.log) |
| `RSI_BB_MACD_Nov_2023_1h_2_Dec` | `futures_long_short` | `E1_expanded` | 630 | `convergence:336:warmup_supplied` | 2026-09-14 19:30:50 | [archive](user_data/profile_smoke/RSI_BB_MACD_Nov_2023_1h_2_Dec-87700a43-smoke_20200301_20200401-b4807b77-2026-09-14_19-30-50.zip) [log](user_data/convergence_logs/RSI_BB_MACD_Nov_2023_1h_2_Dec-87700a43-ladder.log) |
| `RSI_EMA_strategy` | `spot_long` | `E1_expanded` | 4228 | `convergence:288:warmup_supplied` | 2026-09-09 22:08:18 | [archive](user_data/profile_smoke/RSI_EMA_strategy-9053385e-2026-09-09_22-08-18.zip) [log](user_data/convergence_logs/RSI_EMA_strategy-ladder.log) |
| `RSIv2` | `spot_long` | `E1_expanded` | 4957 | `convergence:192:warmup_supplied` | 2026-09-06 07:59:04 | [archive](user_data/profile_smoke/RSIv2-f567e470-2026-09-06_07-59-04.zip) [log](user_data/convergence_logs/RSIv2-ladder.log) |
| `RalliV1` | `spot_long` | `E1_expanded` | 519 | `convergence:2016:warmup_supplied` | 2026-09-05 12:35:25 | [archive](user_data/profile_smoke/RalliV1-ea9894c9-2026-09-05_12-35-25.zip) [log](user_data/convergence_logs/RalliV1-ladder.log) |
| `RalliV1_disable56` | `spot_long` | `E1_expanded` | 513 | `convergence:2016:warmup_supplied` | 2026-09-05 20:53:46 | [archive](user_data/profile_smoke/RalliV1_disable56-0bc70ac8-2026-09-05_20-53-46.zip) [log](user_data/convergence_logs/RalliV1_disable56-ladder.log) |
| `RegimeFilterStrategy` | `futures_long_short` | `E1_expanded` | 65 | `convergence:336:warmup_supplied` | 2026-09-03 14:02:02 | [log](user_data/convergence_logs/RegimeFilterStrategy-ladder.log) |
| `ReinforcedAverageStrategy` | `spot_long` | `E1_expanded` | 1096 | `convergence:84:warmup_supplied` | 2026-09-05 20:54:55 | [archive](user_data/profile_smoke/ReinforcedAverageStrategy-8767d79d-2026-09-05_20-54-55.zip) [log](user_data/convergence_logs/ReinforcedAverageStrategy-ladder.log) |
| `ReinforcedSmoothScalp` | `spot_long` | `E1_expanded` | 586 | `convergence:2880:warmup_supplied` | 2026-09-05 13:39:22 | [archive](user_data/profile_smoke/ReinforcedSmoothScalp-a3abdfaa-2026-09-05_13-39-22.zip) [log](user_data/convergence_logs/ReinforcedSmoothScalp-ladder.log) |
| `RobotradingBody` | `spot_long` | `E1_expanded` | 2422 | `convergence:100` | 2026-09-06 07:59:36 | [archive](user_data/profile_smoke/RobotradingBody-ec6fd706-2026-09-06_07-59-36.zip) [log](user_data/convergence_logs/RobotradingBody-ladder.log) |
| `RocMomentumStrategy` | `spot_long` | `E1_expanded` | 13885 | `convergence:576:warmup_supplied` | 2026-09-09 22:10:07 | [archive](user_data/profile_smoke/RocMomentumStrategy-ecfd7c95-2026-09-09_22-10-07.zip) [log](user_data/convergence_logs/RocMomentumStrategy-ladder.log) |
| `Roth01` | `spot_long` | `E1_expanded` | 10231 | `convergence:288:warmup_supplied` | 2026-09-06 08:05:28 | [archive](user_data/profile_smoke/Roth01-6f953383-2026-09-06_08-05-28.zip) [log](user_data/convergence_logs/Roth01-ladder.log) |
| `Roth03` | `spot_long` | `E1_expanded` | 2874 | `convergence:288:warmup_supplied` | 2026-09-06 08:03:05 | [archive](user_data/profile_smoke/Roth03-039e9893-2026-09-06_08-03-05.zip) [log](user_data/convergence_logs/Roth03-ladder.log) |
| `RsiBollingerStrategy` | `spot_long` | `E1_expanded` | 2375 | `convergence:168:warmup_supplied` | 2026-09-09 22:09:13 | [archive](user_data/profile_smoke/RsiBollingerStrategy-86871f9f-2026-09-09_22-09-13.zip) [log](user_data/convergence_logs/RsiBollingerStrategy-ladder.log) |
| `RsiDivergenceStrategy` | `spot_long` | `E1_expanded` | 404 | `convergence:288:warmup_supplied` | 2026-09-09 22:10:52 | [archive](user_data/profile_smoke/RsiDivergenceStrategy-75586daa-2026-09-09_22-10-52.zip) [log](user_data/convergence_logs/RsiDivergenceStrategy-ladder.log) |
| `SAR` | `spot_long` | `E1_expanded` | 13561 | `convergence:288:warmup_supplied` | 2026-09-05 20:59:02 | [archive](user_data/profile_smoke/SAR-c00b2014-2026-09-05_20-59-02.zip) [log](user_data/convergence_logs/SAR-c00b2014-ladder.log) |
| `SARCross` | `spot_long` | `E1_expanded` | 32 | `convergence:288:warmup_supplied` | 2026-09-06 18:27:47 | [archive](user_data/profile_smoke/SARCross-0c09ed9a-2026-09-06_18-27-47.zip) [log](user_data/convergence_logs/SARCross-0c09ed9a-ladder.log) |
| `SMAIP3` | `spot_long` | `E1_expanded` | 292 | `convergence:2016:warmup_supplied` | 2026-09-06 08:05:25 | [archive](user_data/profile_smoke/SMAIP3-9f3f2209-2026-09-06_08-05-25.zip) [log](user_data/convergence_logs/SMAIP3-ladder.log) |
| `SMAIP3v2` | `spot_long` | `E1_expanded` | 16 | `convergence:2016:warmup_supplied` | 2026-09-06 14:53:00 | [archive](user_data/profile_smoke/SMAIP3v2-e79dedd0-2026-09-06_14-53-00.zip) [log](user_data/convergence_logs/SMAIP3v2-ladder.log) |
| `SMAOG` | `spot_long` | `E1_expanded` | 440 | `convergence:2016:warmup_supplied` | 2026-09-05 12:36:40 | [archive](user_data/profile_smoke/SMAOG-486e4c4f-2026-09-05_12-36-40.zip) [log](user_data/convergence_logs/SMAOG-ladder.log) |
| `SMAOPv1_TTF` | `spot_long` | `E1_expanded` | 87 | `convergence:2016:warmup_supplied` | 2026-09-10 07:30:42 | [archive](user_data/profile_smoke/SMAOPv1_TTF-fd792764-smoke_20200301_20210301-fca63e6f-2026-09-10_07-30-42.zip) [log](user_data/convergence_logs/SMAOPv1_TTF-fd792764-ladder.log) |
| `SMAOffset` | `spot_long` | `E1_expanded` | 1663 | `convergence:288:warmup_supplied` | 2026-09-05 21:02:04 | [archive](user_data/profile_smoke/SMAOffset-2a5b3c73-2026-09-05_21-02-04.zip) [log](user_data/convergence_logs/SMAOffset-ladder.log) |
| `SMAOffsetProtectOpt` | `spot_long` | `E1_expanded` | 162 | `convergence:2016:warmup_supplied` | 2026-09-06 08:09:57 | [archive](user_data/profile_smoke/SMAOffsetProtectOpt-2152c953-2026-09-06_08-09-57.zip) [log](user_data/convergence_logs/SMAOffsetProtectOpt-ladder.log) |
| `SMAOffsetProtectOptV0` | `spot_long` | `E1_expanded` | 223 | `convergence:2016:warmup_supplied` | 2026-09-05 21:02:59 | [archive](user_data/profile_smoke/SMAOffsetProtectOptV0-6414abca-2026-09-05_21-02-59.zip) [log](user_data/convergence_logs/SMAOffsetProtectOptV0-ladder.log) |
| `SMAOffsetProtectOptV1` | `spot_long` | `E1_expanded` | 182 | `convergence:2016:warmup_supplied` | 2026-09-05 12:37:36 | [archive](user_data/profile_smoke/SMAOffsetProtectOptV1-e1bbd837-2026-09-05_12-37-36.zip) [log](user_data/convergence_logs/SMAOffsetProtectOptV1-ladder.log) |
| `SMAOffsetProtectOptV1HO1` | `spot_long` | `E1_expanded` | 1039 | `convergence:2016:warmup_supplied` | 2026-09-05 21:04:21 | [archive](user_data/profile_smoke/SMAOffsetProtectOptV1HO1-16235a5a-2026-09-05_21-04-21.zip) [log](user_data/convergence_logs/SMAOffsetProtectOptV1HO1-ladder.log) |
| `SMAOffsetProtectOptV1Mod` | `spot_long` | `E1_expanded` | 178 | `convergence:2016:warmup_supplied` | 2026-09-06 08:07:34 | [archive](user_data/profile_smoke/SMAOffsetProtectOptV1Mod-1ea5626b-2026-09-06_08-07-34.zip) [log](user_data/convergence_logs/SMAOffsetProtectOptV1Mod-ladder.log) |
| `SMAOffsetProtectOptV1Mod2` | `spot_long` | `E1_expanded` | 180 | `convergence:2016:warmup_supplied` | 2026-09-05 21:05:12 | [archive](user_data/profile_smoke/SMAOffsetProtectOptV1Mod2-aeb50ca9-2026-09-05_21-05-12.zip) [log](user_data/convergence_logs/SMAOffsetProtectOptV1Mod2-ladder.log) |
| `SMAOffsetProtectOptV1Mod2_antipump` | `spot_long` | `E1_expanded` | 180 | `convergence:288` | 2026-09-14 23:44:42 | [archive](user_data/profile_smoke/SMAOffsetProtectOptV1Mod2_antipump-a59e39c8-smoke_20200301_20210301-fca63e6f-2026-09-14_23-44-42.zip) [log](user_data/convergence_logs/SMAOffsetProtectOptV1Mod2_antipump-a59e39c8-ladder.log) |
| `SMAOffsetProtectOptV1_kkeue_20210619` | `spot_long` | `E1_expanded` | 180 | `convergence:2016:warmup_supplied` | 2026-09-06 08:07:47 | [archive](user_data/profile_smoke/SMAOffsetProtectOptV1_kkeue_20210619-1de98e43-2026-09-06_08-07-47.zip) [log](user_data/convergence_logs/SMAOffsetProtectOptV1_kkeue_20210619-ladder.log) |
| `SMAOffsetV2` | `spot_long` | `E1_expanded` | 635 | `convergence:200` | 2026-09-05 21:06:49 | [archive](user_data/profile_smoke/SMAOffsetV2-34f5bfe3-2026-09-05_21-06-49.zip) [log](user_data/convergence_logs/SMAOffsetV2-ladder.log) |
| `SMAOffset_Hippocritical_dca` | `spot_long` | `E1_expanded` | 190 | `convergence:2016:warmup_supplied` | 2026-09-06 02:56:48 | [archive](user_data/profile_smoke/SMAOffset_Hippocritical_dca-396122f8-2026-09-06_02-56-48.zip) [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca-ladder.log) |
| `SMAOffset_Hippocritical_dca_leverage` | `futures_long` | `E1_expanded` | 18 | `convergence:2016:warmup_supplied` | 2026-09-02 07:41:14 | [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca_leverage-ladder.log) |
| `SMAOffset_Hippocritical_dca_old` | `spot_long` | `E1_expanded` | 190 | `convergence:2016:warmup_supplied` | 2026-09-06 02:57:50 | [archive](user_data/profile_smoke/SMAOffset_Hippocritical_dca_old-fec4f46c-2026-09-06_02-57-50.zip) [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca_old-ladder.log) |
| `SMAOffset_Hippocritical_dca_protections` | `spot_long` | `E1_expanded` | 190 | `convergence:2016:warmup_supplied` | 2026-09-06 02:59:09 | [archive](user_data/profile_smoke/SMAOffset_Hippocritical_dca_protections-035af48f-2026-09-06_02-59-09.zip) [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca_protections-ladder.log) |
| `SMA_BBRSI` | `spot_long` | `E1_expanded` | 29 | `convergence:2016:warmup_supplied` | 2026-09-17 12:15:37 | [archive](user_data/profile_smoke/SMA_BBRSI-f844971d-smoke_20200301_20200401-b4807b77-2026-09-17_12-15-37.zip) [log](user_data/convergence_logs/SMA_BBRSI-ladder.log) |
| `SRsi` | `spot_long` | `E1_expanded` | 6709 | `convergence:1440:warmup_supplied` | 2026-09-09 16:39:56 | [archive](user_data/profile_smoke/SRsi-6757d437-2026-09-09_16-39-56.zip) [log](user_data/convergence_logs/SRsi-ladder.log) |
| `STRATEGY_RSI_BB_BOUNDS_CROSS` | `spot_long` | `E1_expanded` | 5897 | `convergence:288:warmup_supplied` | 2026-09-06 08:13:43 | [archive](user_data/profile_smoke/STRATEGY_RSI_BB_BOUNDS_CROSS-00a44a09-2026-09-06_08-13-43.zip) [log](user_data/convergence_logs/STRATEGY_RSI_BB_BOUNDS_CROSS-ladder.log) |
| `STRATEGY_RSI_BB_CROSS` | `spot_long` | `E1_expanded` | 13545 | `convergence:288:warmup_supplied` | 2026-09-07 14:51:29 | [archive](user_data/profile_smoke/STRATEGY_RSI_BB_CROSS-033b8735-2026-09-07_14-51-29.zip) [log](user_data/convergence_logs/STRATEGY_RSI_BB_CROSS-ladder.log) |
| `SUPPORT_RESISTANCE` | `spot_long` | `E1_expanded` | 5 | `convergence:730:warmup_supplied` | 2026-09-06 18:14:10 | [archive](user_data/profile_smoke/SUPPORT_RESISTANCE-e57b787f-2026-09-06_18-14-10.zip) [log](user_data/convergence_logs/SUPPORT_RESISTANCE-e57b787f-ladder.log) |
| `SampleStrategy` | `spot_long` | `E1_expanded` | 10999 | `convergence:288:warmup_supplied` | 2026-09-07 04:58:37 | [archive](user_data/profile_smoke/SampleStrategy-2b02bb67-2026-09-07_04-58-37.zip) [log](user_data/convergence_logs/SampleStrategy-ladder.log) |
| `SampleStrategyV2` | `spot_long` | `E1_expanded` | 4906 | `convergence:576` | 2026-09-05 18:45:44 | [archive](user_data/profile_smoke/SampleStrategyV2-bf71b29d-2026-09-05_18-45-44.zip) [log](user_data/convergence_logs/SampleStrategyV2-ladder.log) |
| `Sar` | `spot_long` | `E1_expanded` | 10999 | `convergence:288:warmup_supplied` | 2026-09-05 21:10:23 | [archive](user_data/profile_smoke/Sar-ee566748-2026-09-05_21-10-23.zip) [log](user_data/convergence_logs/Sar-ladder.log) |
| `Saturn5` | `spot_long` | `E1_expanded` | 2720 | `convergence:1344:warmup_supplied` | 2026-09-05 21:09:26 | [archive](user_data/profile_smoke/Saturn5-5682c41e-2026-09-05_21-09-26.zip) [log](user_data/convergence_logs/Saturn5-ladder.log) |
| `Scalp` | `spot_long` | `E1_expanded` | 2767 | `convergence:1440:warmup_supplied` | 2026-09-09 16:23:18 | [archive](user_data/profile_smoke/Scalp-025555a4-2026-09-09_16-23-18.zip) [log](user_data/convergence_logs/Scalp-ladder.log) |
| `Schism` | `spot_long` | `E1_expanded` | 388 | `convergence:288:warmup_supplied` | 2026-09-03 21:00:02 | [archive](user_data/profile_smoke/Schism-4f0b8f62-2026-09-03_21-00-02.zip) [log](user_data/convergence_logs/Schism-ladder.log) |
| `Schism2` | `spot_long` | `E1_expanded` | 149 | `convergence:288:warmup_supplied` | 2026-09-03 21:05:52 | [archive](user_data/profile_smoke/Schism2-488547c4-2026-09-03_21-05-52.zip) [log](user_data/convergence_logs/Schism2-ladder.log) |
| `Schism2_BTC` | `spot_long` | `E1_expanded` | 225 | `convergence:288:warmup_supplied` | 2026-09-16 16:13:25 | [archive](user_data/profile_smoke/Schism2_BTC-2a7bcf41-smoke_20200301_20200401-b4807b77-2026-09-16_16-13-25.zip) [log](user_data/convergence_logs/Schism2_BTC-2a7bcf41-ladder.log) |
| `Schism2_ETH` | `spot_long` | `E1_expanded` | 334 | `convergence:288:warmup_supplied` | 2026-09-16 16:15:09 | [archive](user_data/profile_smoke/Schism2_ETH-af7072d3-smoke_20200301_20200401-b4807b77-2026-09-16_16-15-09.zip) [log](user_data/convergence_logs/Schism2_ETH-af7072d3-ladder.log) |
| `Schism3` | `spot_long` | `E1_expanded` | 6429 | `convergence:288:warmup_supplied` | 2026-09-07 10:37:44 | [archive](user_data/profile_smoke/Schism3-ee2a15e4-2026-09-07_10-37-44.zip) [log](user_data/convergence_logs/Schism3-ladder.log) |
| `Schism4` | `spot_long` | `E1_expanded` | 7932 | `convergence:288:warmup_supplied` | 2026-09-07 10:52:44 | [archive](user_data/profile_smoke/Schism4-cabe5254-2026-09-07_10-52-44.zip) [log](user_data/convergence_logs/Schism4-ladder.log) |
| `Seb` | `spot_long` | `E1_expanded` | 11597 | `convergence:576:warmup_supplied` | 2026-09-07 11:04:30 | [archive](user_data/profile_smoke/Seb-884e1568-2026-09-07_11-04-30.zip) [log](user_data/convergence_logs/Seb-ladder.log) |
| `Simple` | `spot_long` | `E1_expanded` | 13287 | `convergence:288:warmup_supplied` | 2026-09-07 11:07:53 | [archive](user_data/profile_smoke/Simple-3fee95da-2026-09-07_11-07-53.zip) [log](user_data/convergence_logs/Simple-ladder.log) |
| `SimpleBollinger` | `spot_long` | `E1_expanded` | 1 | `convergence:576:warmup_supplied` | 2026-09-06 18:27:56 | [archive](user_data/profile_smoke/SimpleBollinger-3b182c17-2026-09-06_18-27-56.zip) [log](user_data/convergence_logs/SimpleBollinger-3b182c17-ladder.log) |
| `SimpleHopt` | `spot_long` | `E1_expanded` | 9539 | `convergence:288:warmup_supplied` | 2026-09-05 13:47:16 | [archive](user_data/profile_smoke/SimpleHopt-ade85462-2026-09-05_13-47-16.zip) [log](user_data/convergence_logs/SimpleHopt-ladder.log) |
| `SimpleHopt1Along` | `spot_long` | `E1_expanded` | 10 | `convergence:540:warmup_supplied` | 2026-09-06 14:47:40 | [archive](user_data/profile_smoke/SimpleHopt1Along-df7ee9ca-2026-09-06_14-47-40.zip) [log](user_data/convergence_logs/SimpleHopt1Along-ladder.log) |
| `SimpleRSI_Shorts` | `futures_short` | `E1_expanded` | 2 | `convergence:50` | 2026-09-14 19:31:02 | [archive](user_data/profile_smoke/SimpleRSI_Shorts-f0dec165-smoke_20200301_20210301-fca63e6f-2026-09-14_19-31-02.zip) [log](user_data/convergence_logs/SimpleRSI_Shorts-f0dec165-ladder.log) |
| `SlowPotato` | `spot_long` | `E1_expanded` | 1990 | `convergence:288:warmup_supplied` | 2026-09-07 14:57:45 | [archive](user_data/profile_smoke/SlowPotato-6a44af82-2026-09-07_14-57-45.zip) [log](user_data/convergence_logs/SlowPotato-ladder.log) |
| `Slowbro` | `spot_long` | `E1_expanded` | 76 | `convergence:30` | 2026-09-05 21:40:31 | [archive](user_data/profile_smoke/Slowbro-ad1dbbe4-2026-09-05_21-40-31.zip) [log](user_data/convergence_logs/Slowbro-ladder.log) |
| `SmaRsiStrategy` | `spot_long` | `E1_expanded` | 531 | `convergence:90:warmup_supplied` | 2026-09-05 11:47:20 | [archive](user_data/profile_smoke/SmaRsiStrategy-62d3e5a3-2026-09-05_11-47-20.zip) [log](user_data/convergence_logs/SmaRsiStrategy-ladder.log) |
| `SmartMoneyStrategy` | `spot_long` | `E1_expanded` | 348 | `convergence:1440:warmup_supplied` | 2026-09-07 16:50:03 | [archive](user_data/profile_smoke/SmartMoneyStrategy-83dc6dbe-2026-09-07_16-50-03.zip) [log](user_data/convergence_logs/SmartMoneyStrategy-ladder.log) |
| `SmartMoneyStrategyHyperopt` | `spot_long` | `E1_expanded` | 8 | `convergence:2160:warmup_supplied` | 2026-09-06 15:11:13 | [archive](user_data/profile_smoke/SmartMoneyStrategyHyperopt-fff5e4c0-2026-09-06_15-11-13.zip) [log](user_data/convergence_logs/SmartMoneyStrategyHyperopt-ladder.log) |
| `SmoothOperator` | `spot_long` | `E1_expanded` | 14394 | `convergence:288:warmup_supplied` | 2026-09-05 21:47:15 | [archive](user_data/profile_smoke/SmoothOperator-27d8facc-2026-09-05_21-47-15.zip) [log](user_data/convergence_logs/SmoothOperator-ladder.log) |
| `SmoothScalp` | `spot_long` | `E1_expanded` | 571 | `convergence:1440:warmup_supplied` | 2026-09-09 16:23:59 | [archive](user_data/profile_smoke/SmoothScalp-aa3c9357-2026-09-09_16-23-59.zip) [log](user_data/convergence_logs/SmoothScalp-ladder.log) |
| `Squeeze001` | `spot_long` | `E1_expanded` | 26 | `convergence:576:warmup_supplied` | 2026-09-06 18:28:04 | [archive](user_data/profile_smoke/Squeeze001-f1de728b-2026-09-06_18-28-04.zip) [log](user_data/convergence_logs/Squeeze001-f1de728b-ladder.log) |
| `Squeeze002` | `spot_long` | `E1_expanded` | 175 | `convergence:576:warmup_supplied` | 2026-09-06 18:29:58 | [archive](user_data/profile_smoke/Squeeze002-11618dd8-2026-09-06_18-29-58.zip) [log](user_data/convergence_logs/Squeeze002-11618dd8-ladder.log) |
| `SqueezeMomentum` | `spot_long` | `E1_expanded` | 277 | `convergence:2016:warmup_supplied` | 2026-09-06 14:58:41 | [archive](user_data/profile_smoke/SqueezeMomentum-55dbc2ef-2026-09-06_14-58-41.zip) [log](user_data/convergence_logs/SqueezeMomentum-ladder.log) |
| `SqueezeMomentumStrategy` | `spot_long` | `E1_expanded` | 11451 | `convergence:288:warmup_supplied` | 2026-09-09 22:12:03 | [archive](user_data/profile_smoke/SqueezeMomentumStrategy-7744423e-2026-09-09_22-12-03.zip) [log](user_data/convergence_logs/SqueezeMomentumStrategy-ladder.log) |
| `SqueezeOff` | `spot_long` | `E1_expanded` | 245 | `convergence:576:warmup_supplied` | 2026-09-06 18:29:00 | [archive](user_data/profile_smoke/SqueezeOff-00971d90-2026-09-06_18-29-00.zip) [log](user_data/convergence_logs/SqueezeOff-00971d90-ladder.log) |
| `StarRise` | `spot_long` | `E1_expanded` | 158 | `convergence:2016:warmup_supplied` | 2026-09-06 03:04:41 | [archive](user_data/profile_smoke/StarRise-2ce8ff8a-2026-09-06_03-04-41.zip) [log](user_data/convergence_logs/StarRise-ladder.log) |
| `StarRise_V2` | `spot_long` | `E1_expanded` | 186 | `convergence:2016:warmup_supplied` | 2026-09-14 23:59:57 | [archive](user_data/profile_smoke/StarRise_V2-b4e4e112-smoke_20200301_20200601-9c543975-2026-09-14_23-59-57.zip) [log](user_data/convergence_logs/StarRise_V2-b4e4e112-ladder.log) |
| `StarRise_strat` | `spot_long` | `E1_expanded` | 186 | `convergence:2016:warmup_supplied` | 2026-09-06 03:03:49 | [archive](user_data/profile_smoke/StarRise_strat-7f42ebda-2026-09-06_03-03-49.zip) [log](user_data/convergence_logs/StarRise_strat-ladder.log) |
| `Stavix2` | `spot_long` | `E1_expanded` | 81 | `convergence:1440:warmup_supplied` | 2026-09-01 19:51:30 | [archive](user_data/profile_smoke/Stavix2-2026-09-01_19-51-30.zip) [log](user_data/convergence_logs/Stavix2-4c91e408-ladder.log) |
| `StochRSITEMA` | `spot_long` | `E1_expanded` | 3866 | `convergence:576:warmup_supplied` | 2026-09-07 11:15:54 | [archive](user_data/profile_smoke/StochRSITEMA-ad00b250-2026-09-07_11-15-54.zip) [log](user_data/convergence_logs/StochRSITEMA-ladder.log) |
| `StochasticCciStrategy` | `spot_long` | `E1_expanded` | 1186 | `convergence:336:warmup_supplied` | 2026-09-09 22:11:44 | [archive](user_data/profile_smoke/StochasticCciStrategy-11eeffb3-2026-09-09_22-11-44.zip) [log](user_data/convergence_logs/StochasticCciStrategy-ladder.log) |
| `StochasticOversoldStrategy` | `spot_long` | `E1_expanded` | 14950 | `convergence:288:warmup_supplied` | 2026-09-09 22:13:49 | [archive](user_data/profile_smoke/StochasticOversoldStrategy-ab64b5f2-2026-09-09_22-13-49.zip) [log](user_data/convergence_logs/StochasticOversoldStrategy-ladder.log) |
| `StochasticRsiStrategy` | `spot_long` | `E1_expanded` | 15006 | `convergence:288:warmup_supplied` | 2026-09-09 22:14:02 | [archive](user_data/profile_smoke/StochasticRsiStrategy-e7dd1810-2026-09-09_22-14-02.zip) [log](user_data/convergence_logs/StochasticRsiStrategy-ladder.log) |
| `Strategy001` | `spot_long` | `E1_expanded` | 11597 | `convergence:576:warmup_supplied` | 2026-09-06 02:10:08 | [archive](user_data/profile_smoke/Strategy001-57661416-2026-09-06_02-10-08.zip) [log](user_data/convergence_logs/Strategy001-ladder.log) |
| `Strategy001_custom_exit` | `spot_long` | `E1_expanded` | 14592 | `convergence:576:warmup_supplied` | 2026-09-06 02:40:48 | [archive](user_data/profile_smoke/Strategy001_custom_exit-8f220684-2026-09-06_02-40-48.zip) [log](user_data/convergence_logs/Strategy001_custom_exit-ladder.log) |
| `Strategy001_custom_sell` | `spot_long` | `E1_expanded` | 14592 | `convergence:576:warmup_supplied` | 2026-09-07 15:21:26 | [archive](user_data/profile_smoke/Strategy001_custom_sell-21468069-2026-09-07_15-21-26.zip) [log](user_data/convergence_logs/Strategy001_custom_sell-ladder.log) |
| `Strategy002` | `spot_long` | `E1_expanded` | 1125 | `convergence:288:warmup_supplied` | 2026-09-06 02:13:01 | [archive](user_data/profile_smoke/Strategy002-feae8690-2026-09-06_02-13-01.zip) [log](user_data/convergence_logs/Strategy002-ladder.log) |
| `Strategy003` | `spot_long` | `E1_expanded` | 2974 | `convergence:576:warmup_supplied` | 2026-09-06 02:16:12 | [archive](user_data/profile_smoke/Strategy003-63d0ad16-2026-09-06_02-16-12.zip) [log](user_data/convergence_logs/Strategy003-ladder.log) |
| `Strategy004` | `spot_long` | `E1_expanded` | 4997 | `convergence:576:warmup_supplied` | 2026-09-06 02:19:15 | [archive](user_data/profile_smoke/Strategy004-39eb4f05-2026-09-06_02-19-15.zip) [log](user_data/convergence_logs/Strategy004-ladder.log) |
| `Strategy005` | `spot_long` | `E1_expanded` | 4759 | `convergence:288:warmup_supplied` | 2026-09-06 02:23:44 | [archive](user_data/profile_smoke/Strategy005-880bd83d-2026-09-06_02-23-44.zip) [log](user_data/convergence_logs/Strategy005-ladder.log) |
| `StrategyScalpingFast` | `spot_long` | `E1_expanded` | 267 | `convergence:1440:warmup_supplied` | 2026-09-09 16:41:26 | [archive](user_data/profile_smoke/StrategyScalpingFast-7e07a768-2026-09-09_16-41-26.zip) [log](user_data/convergence_logs/StrategyScalpingFast-ladder.log) |
| `StrategyScalpingFast2` | `spot_long` | `E1_expanded` | 355 | `convergence:1440:warmup_supplied` | 2026-09-09 16:40:43 | [archive](user_data/profile_smoke/StrategyScalpingFast2-aba7fb17-2026-09-09_16-40-43.zip) [log](user_data/convergence_logs/StrategyScalpingFast2-ladder.log) |
| `SuperHV27_BTC` | `spot_long` | `E1_expanded` | 137 | `convergence:576:warmup_supplied` | 2026-09-16 16:15:54 | [archive](user_data/profile_smoke/SuperHV27_BTC-5bfe795f-smoke_20200301_20200401-b4807b77-2026-09-16_16-15-54.zip) [log](user_data/convergence_logs/SuperHV27_BTC-5bfe795f-ladder.log) |
| `SuperTrend` | `spot_long` | `E1_expanded` | 124 | `convergence:1440:warmup_supplied` | 2026-09-09 16:24:55 | [archive](user_data/profile_smoke/SuperTrend-e9770a14-2026-09-09_16-24-55.zip) [log](user_data/convergence_logs/SuperTrend-e9770a14-ladder.log) |
| `SupertrendStrategy` | `spot_long` | `E1_expanded` | 3373 | `convergence:336:warmup_supplied` | 2026-09-05 21:58:20 | [archive](user_data/profile_smoke/SupertrendStrategy-ced5f239-2026-09-05_21-58-20.zip) [log](user_data/convergence_logs/SupertrendStrategy-ladder.log) |
| `SwingHigh` | `spot_long` | `E1_expanded` | 20 | `convergence:336:warmup_supplied` | 2026-09-01 19:52:15 | [archive](user_data/profile_smoke/SwingHigh-2026-09-01_19-52-15.zip) [log](user_data/convergence_logs/SwingHigh-ladder.log) |
| `SwingHighToSky` | `spot_long` | `E1_expanded` | 5040 | `convergence:672:warmup_supplied` | 2026-09-05 22:01:35 | [archive](user_data/profile_smoke/SwingHighToSky-64dfd59e-2026-09-05_22-01-35.zip) [log](user_data/convergence_logs/SwingHighToSky-ladder.log) |
| `TD` | `spot_long` | `E1_expanded` | 14827 | `convergence:12:warmup_supplied` | 2026-09-07 16:08:10 | [archive](user_data/profile_smoke/TD-b6a51c2a-2026-09-07_16-08-10.zip) [log](user_data/convergence_logs/TD-ladder.log) |
| `TDSequentialStrategy` | `spot_long` | `E1_expanded` | 3763 | `convergence:24` | 2026-09-07 00:03:33 | [archive](user_data/profile_smoke/TDSequentialStrategy-833fdb92-2026-09-07_00-03-33.zip) [log](user_data/convergence_logs/TDSequentialStrategy-ladder.log) |
| `TEMA` | `spot_long` | `E1_expanded` | 9966 | `convergence:1440:warmup_supplied` | 2026-09-09 16:25:50 | [archive](user_data/profile_smoke/TEMA-2a9399f6-2026-09-09_16-25-50.zip) [log](user_data/convergence_logs/TEMA-ladder.log) |
| `TEMABounce` | `spot_long` | `E1_expanded` | 10 | `convergence:576:warmup_supplied` | 2026-09-15 21:00:27 | [archive](user_data/profile_smoke/TEMABounce-9f6a881a-smoke_20200301_20200601-9c543975-2026-09-15_21-00-27.zip) [log](user_data/convergence_logs/TEMABounce-9f6a881a-ladder.log) |
| `TRIWAVE` | `spot_long` | `E1_expanded` | 3110 | `convergence:672:warmup_supplied` | 2026-09-06 03:22:30 | [archive](user_data/profile_smoke/TRIWAVE-cd5c62a5-2026-09-06_03-22-30.zip) [log](user_data/convergence_logs/TRIWAVE-ladder.log) |
| `TRIX_spot` | `spot_long` | `E1_expanded` | 71 | `convergence:2160:warmup_supplied` | 2026-09-06 18:23:24 | [archive](user_data/profile_smoke/TRIX_spot-b4f2394c-2026-09-06_18-23-24.zip) [log](user_data/convergence_logs/TRIX_spot-b4f2394c-ladder.log) |
| `TWAPStrategy` | `futures_long_short` | `E1_expanded` | 671 | `convergence:192:warmup_supplied` | 2026-09-01 15:11:56 | [log](user_data/convergence_logs/TWAPStrategy-ladder.log) |
| `TechnicalExampleStrategy` | `spot_long` | `E1_expanded` | 16453 | `convergence:288:warmup_supplied` | 2026-09-07 00:14:54 | [archive](user_data/profile_smoke/TechnicalExampleStrategy-16a5767b-2026-09-07_00-14-54.zip) [log](user_data/convergence_logs/TechnicalExampleStrategy-ladder.log) |
| `TemaMaster` | `spot_long` | `E1_expanded` | 5386 | `convergence:288:warmup_supplied` | 2026-09-07 15:14:05 | [archive](user_data/profile_smoke/TemaMaster-bbf2c003-2026-09-07_15-14-05.zip) [log](user_data/convergence_logs/TemaMaster-ladder.log) |
| `TemaMaster3` | `spot_long` | `E1_expanded` | 118 | `convergence:2880:warmup_supplied` | 2026-09-09 16:42:13 | [archive](user_data/profile_smoke/TemaMaster3-59c6d053-2026-09-09_16-42-13.zip) [log](user_data/convergence_logs/TemaMaster3-ladder.log) |
| `TemaPure` | `spot_long` | `E1_expanded` | 8182 | `convergence:2016:warmup_supplied` | 2026-09-06 08:55:09 | [archive](user_data/profile_smoke/TemaPure-1716b882-2026-09-06_08-55-09.zip) [log](user_data/convergence_logs/TemaPure-ladder.log) |
| `TemaPureNeat` | `spot_long` | `E1_expanded` | 10187 | `convergence:288:warmup_supplied` | 2026-09-06 08:49:38 | [archive](user_data/profile_smoke/TemaPureNeat-92313791-2026-09-06_08-49-38.zip) [log](user_data/convergence_logs/TemaPureNeat-ladder.log) |
| `TemaPureTwo` | `spot_long` | `E1_expanded` | 10411 | `convergence:2016:warmup_supplied` | 2026-09-06 08:50:46 | [archive](user_data/profile_smoke/TemaPureTwo-3dcbc751-2026-09-06_08-50-46.zip) [log](user_data/convergence_logs/TemaPureTwo-ladder.log) |
| `TemaStrategy` | `spot_long` | `E1_expanded` | 13137 | `convergence:288:warmup_supplied` | 2026-09-09 22:15:53 | [archive](user_data/profile_smoke/TemaStrategy-73852f36-2026-09-09_22-15-53.zip) [log](user_data/convergence_logs/TemaStrategy-ladder.log) |
| `TenderEnter` | `spot_long` | `E1_expanded` | 3312 | `convergence:96` | 2026-09-06 08:52:37 | [archive](user_data/profile_smoke/TenderEnter-6b1745fc-2026-09-06_08-52-37.zip) [log](user_data/convergence_logs/TenderEnter-ladder.log) |
| `Test_MAMA4` | `spot_long` | `E1_expanded` | 94 | `convergence:288` | 2026-09-04 06:22:04 | [archive](user_data/profile_smoke/Test_MAMA4-aa83c1d0-2026-09-04_06-22-04.zip) [log](user_data/convergence_logs/Test_MAMA4-ladder.log) |
| `TheForce` | `spot_long` | `E1_expanded` | 12381 | `convergence:672:warmup_supplied` | 2026-09-07 00:16:19 | [archive](user_data/profile_smoke/TheForce-9789c829-2026-09-07_00-16-19.zip) [log](user_data/convergence_logs/TheForce-ladder.log) |
| `TheRealPullbackV2` | `spot_long` | `E1_expanded` | 705 | `convergence:288:warmup_supplied` | 2026-09-07 00:17:26 | [archive](user_data/profile_smoke/TheRealPullbackV2-6b84aa55-2026-09-07_00-17-26.zip) [log](user_data/convergence_logs/TheRealPullbackV2-ladder.log) |
| `ToTheMoon` | `futures_long_short` | `E1_expanded` | 16 | `convergence:24:warmup_supplied` | 2026-09-01 15:13:58 | [log](user_data/convergence_logs/ToTheMoon-ladder.log) |
| `TouchEmaDelayStrategy` | `spot_long` | `E1_expanded` | 1976 | `convergence:480:warmup_supplied` | 2026-09-06 10:42:15 | [archive](user_data/profile_smoke/TouchEmaDelayStrategy-f474cc0c-2026-09-06_10-42-15.zip) [log](user_data/convergence_logs/TouchEmaDelayStrategy-ladder.log) |
| `TouchEmaStrategy` | `spot_long` | `E1_expanded` | 1176 | `convergence:288:warmup_supplied` | 2026-09-06 10:36:44 | [archive](user_data/profile_smoke/TouchEmaStrategy-d87f2077-2026-09-06_10-36-44.zip) [log](user_data/convergence_logs/TouchEmaStrategy-ladder.log) |
| `TrailingBuyStrat2` | `spot_long` | `E1_expanded` | 639 | `convergence:2016:warmup_supplied` | 2026-09-14 23:42:15 | [archive](user_data/profile_smoke/TrailingBuyStrat2-74684ab5-smoke_20200301_20200401-b4807b77-2026-09-14_23-42-15.zip) [log](user_data/convergence_logs/TrailingBuyStrat2-74684ab5-ladder.log) |
| `TrailingBuyStratCluc` | `spot_long` | `E1_expanded` | 2519 | `convergence:1440:warmup_supplied` | 2026-09-14 23:47:43 | [archive](user_data/profile_smoke/TrailingBuyStratCluc-e73b2a7a-smoke_20200301_20200401-b4807b77-2026-09-14_23-47-43.zip) [log](user_data/convergence_logs/TrailingBuyStratCluc-e73b2a7a-ladder.log) |
| `TrailingBuyStratCluc5m` | `spot_long` | `E1_expanded` | 4738 | `convergence:288:warmup_supplied` | 2026-09-14 23:49:23 | [archive](user_data/profile_smoke/TrailingBuyStratCluc5m-2fa6e08a-smoke_20200301_20200401-b4807b77-2026-09-14_23-49-23.zip) [log](user_data/convergence_logs/TrailingBuyStratCluc5m-2fa6e08a-ladder.log) |
| `TrendAtrStrategy` | `spot_long` | `E1_expanded` | 2678 | `convergence:540:warmup_supplied` | 2026-09-09 22:14:51 | [archive](user_data/profile_smoke/TrendAtrStrategy-b0b678b4-2026-09-09_22-14-51.zip) [log](user_data/convergence_logs/TrendAtrStrategy-ladder.log) |
| `TrendBreakout` | `spot_long` | `E1_expanded` | 320 | `convergence:365:warmup_supplied` | 2026-09-15 20:59:25 | [archive](user_data/profile_smoke/TrendBreakout-9b18ab53-smoke_20200301_20200601-9c543975-2026-09-15_20-59-25.zip) [log](user_data/convergence_logs/TrendBreakout-9b18ab53-ladder.log) |
| `TrendFutures` | `futures_long_short` | `E1_expanded` | 41 | `convergence:220` | 2026-09-08 18:40:48 | [archive](user_data/profile_smoke/TrendFutures-4ee78b0b-2026-09-08_18-40-48.zip) [log](user_data/convergence_logs/TrendFutures-4ee78b0b-ladder.log) |
| `Trend_Strength_Directional` | `spot_long` | `E1_expanded` | 6585 | `convergence:192:warmup_supplied` | 2026-09-06 08:56:22 | [archive](user_data/profile_smoke/Trend_Strength_Directional-23329309-2026-09-06_08-56-22.zip) [log](user_data/convergence_logs/Trend_Strength_Directional-ladder.log) |
| `TripleEmaStrategy` | `spot_long` | `E1_expanded` | 12593 | `convergence:288:warmup_supplied` | 2026-09-09 22:16:43 | [archive](user_data/profile_smoke/TripleEmaStrategy-c38906e6-2026-09-09_22-16-43.zip) [log](user_data/convergence_logs/TripleEmaStrategy-ladder.log) |
| `TripleSuperTrendADXRSI` | `futures_long_short` | `E1_expanded` | 192 | `convergence:336:warmup_supplied` | 2026-09-14 19:45:29 | [archive](user_data/profile_smoke/TripleSuperTrendADXRSI-6eecbc1c-smoke_20200301_20200401-b4807b77-2026-09-14_19-45-29.zip) [log](user_data/convergence_logs/TripleSuperTrendADXRSI-6eecbc1c-ladder.log) |
| `TrixSignalStrategy` | `spot_long` | `E1_expanded` | 12747 | `convergence:288:warmup_supplied` | 2026-09-09 22:17:59 | [archive](user_data/profile_smoke/TrixSignalStrategy-af4e0101-2026-09-09_22-17-59.zip) [log](user_data/convergence_logs/TrixSignalStrategy-ladder.log) |
| `TrixStrategy` | `spot_long` | `E1_expanded` | 11611 | `convergence:168:warmup_supplied` | 2026-09-07 00:18:06 | [archive](user_data/profile_smoke/TrixStrategy-b72204f0-2026-09-07_00-18-06.zip) [log](user_data/convergence_logs/TrixStrategy-ladder.log) |
| `TrixV15Strategy` | `spot_long` | `E1_expanded` | 1234 | `convergence:168:warmup_supplied` | 2026-09-07 00:18:53 | [archive](user_data/profile_smoke/TrixV15Strategy-d9dff207-2026-09-07_00-18-53.zip) [log](user_data/convergence_logs/TrixV15Strategy-ladder.log) |
| `TrixV21Strategy` | `spot_long` | `E1_expanded` | 1016 | `convergence:2160:warmup_supplied` | 2026-09-07 00:19:40 | [archive](user_data/profile_smoke/TrixV21Strategy-08b1252e-2026-09-07_00-19-40.zip) [log](user_data/convergence_logs/TrixV21Strategy-ladder.log) |
| `TrixV23Strategy` | `spot_long` | `E1_expanded` | 1126 | `convergence:2160:warmup_supplied` | 2026-09-07 00:20:16 | [archive](user_data/profile_smoke/TrixV23Strategy-ea11f02f-2026-09-07_00-20-16.zip) [log](user_data/convergence_logs/TrixV23Strategy-ladder.log) |
| `Trump_LIM` | `spot_long` | `E1_expanded` | 18 | `convergence:1440` | 2026-09-06 18:17:16 | [archive](user_data/profile_smoke/Trump_LIM-4f331b98-2026-09-06_18-17-16.zip) [log](user_data/convergence_logs/Trump_LIM-4f331b98-ladder.log) |
| `TwoCandle` | `spot_long` | `E1_expanded` | 11075 | `convergence:168:warmup_supplied` | 2026-09-06 11:52:12 | [archive](user_data/profile_smoke/TwoCandle-01e43a04-2026-09-06_11-52-12.zip) [log](user_data/convergence_logs/TwoCandle-ladder.log) |
| `TwoCandleTheory` | `spot_long` | `E1_expanded` | 37 | `convergence:288:warmup_supplied` | 2026-09-04 10:24:31 | [archive](user_data/profile_smoke/TwoCandleTheory-aede3331-2026-09-04_10-24-31.zip) [log](user_data/convergence_logs/TwoCandleTheory-aede3331-ladder.log) |
| `UltimateMomentumIndicator` | `spot_long` | `E1_expanded` | 6961 | `convergence:576:warmup_supplied` | 2026-09-07 00:27:22 | [archive](user_data/profile_smoke/UltimateMomentumIndicator-492c612a-2026-09-07_00-27-22.zip) [log](user_data/convergence_logs/UltimateMomentumIndicator-ladder.log) |
| `UniversalMACD` | `spot_long` | `E1_expanded` | 1629 | `convergence:288:warmup_supplied` | 2026-09-06 02:26:46 | [archive](user_data/profile_smoke/UniversalMACD-c5ae9ce5-2026-09-06_02-26-46.zip) [log](user_data/convergence_logs/UniversalMACD-ladder.log) |
| `Uptrend` | `spot_long` | `E1_expanded` | 375 | `convergence:2016:warmup_supplied` | 2026-09-05 22:17:29 | [archive](user_data/profile_smoke/Uptrend-2cebb2ab-2026-09-05_22-17-29.zip) [log](user_data/convergence_logs/Uptrend-ladder.log) |
| `UziChanTB2` | `spot_long` | `E1_expanded` | 12582 | `convergence:1344:warmup_supplied` | 2026-09-14 23:41:36 | [archive](user_data/profile_smoke/UziChanTB2-19d09656-smoke_20200301_20200401-b4807b77-2026-09-14_23-41-36.zip) [log](user_data/convergence_logs/UziChanTB2-19d09656-ladder.log) |
| `VWAP` | `spot_long` | `E1_expanded` | 751 | `convergence:2016:warmup_supplied` | 2026-09-05 22:20:38 | [archive](user_data/profile_smoke/VWAP-1c5c938a-2026-09-05_22-20-38.zip) [log](user_data/convergence_logs/VWAP-ladder.log) |
| `VolatilitySystem` | `futures_long` | `E1_expanded` | 9 | `convergence:336:warmup_supplied` | 2026-09-01 15:18:07 | [log](user_data/convergence_logs/VolatilitySystem-ladder.log) |
| `VolatilitySystemV2` | `futures_long_short` | `E1_expanded` | 24 | `convergence:336:warmup_supplied` | 2026-09-01 15:18:57 | [log](user_data/convergence_logs/VolatilitySystemV2-ladder.log) |
| `VolumeBreakoutStrategy` | `spot_long` | `E1_expanded` | 9299 | `convergence:288:warmup_supplied` | 2026-09-09 22:18:46 | [archive](user_data/profile_smoke/VolumeBreakoutStrategy-dafc22e5-2026-09-09_22-18-46.zip) [log](user_data/convergence_logs/VolumeBreakoutStrategy-ladder.log) |
| `VortexStrategy` | `spot_long` | `E1_expanded` | 14800 | `convergence:288:warmup_supplied` | 2026-09-09 22:19:59 | [archive](user_data/profile_smoke/VortexStrategy-e792ca6c-2026-09-09_22-19-59.zip) [log](user_data/convergence_logs/VortexStrategy-ladder.log) |
| `VwapReversionStrategy` | `spot_long` | `E1_expanded` | 15621 | `convergence:576:warmup_supplied` | 2026-09-09 22:21:39 | [archive](user_data/profile_smoke/VwapReversionStrategy-56e2a9f0-2026-09-09_22-21-39.zip) [log](user_data/convergence_logs/VwapReversionStrategy-ladder.log) |
| `WTDMIPRICEDCAStrategyFuture` | `futures_long_short` | `E1_expanded` | 29 | `convergence:288:warmup_supplied` | 2026-09-06 17:59:43 | [archive](user_data/profile_smoke/WTDMIPRICEDCAStrategyFuture-6bd08369-2026-09-06_17-59-43.zip) [log](user_data/convergence_logs/WTDMIPRICEDCAStrategyFuture-6bd08369-ladder.log) |
| `WTDMIPRICESDCAtrategy` | `spot_long` | `E1_expanded` | 47 | `convergence:1440:warmup_supplied` | 2026-09-06 17:58:50 | [archive](user_data/profile_smoke/WTDMIPRICESDCAtrategy-f668b499-2026-09-06_17-58-50.zip) [log](user_data/convergence_logs/WTDMIPRICESDCAtrategy-f668b499-ladder.log) |
| `WTHO` | `spot_long` | `E1_expanded` | 141 | `convergence:360:warmup_supplied` | 2026-09-10 08:18:04 | [archive](user_data/profile_smoke/WTHO-4257b426-smoke_20200301_20200401-b4807b77-2026-09-10_08-18-04.zip) [log](user_data/convergence_logs/WTHO-4257b426-ladder.log) |
| `WTX3` | `futures_long_short` | `E1_expanded` | 740 | `convergence:2016:warmup_supplied` | 2026-09-02 20:34:20 | [log](user_data/convergence_logs/WTX3-ladder.log) |
| `WaveTrendStra` | `spot_long` | `E1_expanded` | 7943 | `convergence:180:warmup_supplied` | 2026-09-05 22:20:46 | [archive](user_data/profile_smoke/WaveTrendStra-e3b07ede-2026-09-05_22-20-46.zip) [log](user_data/convergence_logs/WaveTrendStra-ladder.log) |
| `WilliamsRStrategy` | `spot_long` | `E1_expanded` | 15741 | `convergence:2016:warmup_supplied` | 2026-09-09 22:22:09 | [archive](user_data/profile_smoke/WilliamsRStrategy-c16036d4-2026-09-09_22-22-09.zip) [log](user_data/convergence_logs/WilliamsRStrategy-ladder.log) |
| `XebTradeStrat` | `spot_long` | `E1_expanded` | 7950 | `convergence:1440:warmup_supplied` | 2026-09-06 14:59:12 | [archive](user_data/profile_smoke/XebTradeStrat-5d160cab-2026-09-06_14-59-12.zip) [log](user_data/convergence_logs/XebTradeStrat-ladder.log) |
| `XtraThicc` | `spot_long` | `E1_expanded` | 7717 | `convergence:288` | 2026-09-07 00:56:57 | [archive](user_data/profile_smoke/XtraThicc-06cfa9e4-2026-09-07_00-56-57.zip) [log](user_data/convergence_logs/XtraThicc-ladder.log) |
| `YOLO` | `spot_long` | `E1_expanded` | 3 | `convergence:1440:warmup_supplied` | 2026-09-09 16:26:33 | [archive](user_data/profile_smoke/YOLO-99f26510-2026-09-09_16-26-33.zip) [log](user_data/convergence_logs/YOLO-ladder.log) |
| `ZScoreMeanReversionStrategy` | `spot_long` | `E1_expanded` | 34 | `convergence:540:warmup_supplied` | 2026-09-09 22:22:32 | [archive](user_data/profile_smoke/ZScoreMeanReversionStrategy-33c3c74c-2026-09-09_22-22-32.zip) [log](user_data/convergence_logs/ZScoreMeanReversionStrategy-ladder.log) |
| `ZaratustraDCA2_06` | `futures_long_short` | `E1_expanded` | 241 | `convergence:288:warmup_supplied` | 2026-09-02 07:48:03 | [log](user_data/convergence_logs/ZaratustraDCA2_06-ladder.log) |
| `ZaratustraDCA2_07` | `futures_long_short` | `E1_expanded` | 219 | `convergence:288:warmup_supplied` | 2026-09-02 07:49:13 | [log](user_data/convergence_logs/ZaratustraDCA2_07-ladder.log) |
| `ZaratustraDCA5` | `futures_long_short` | `E1_expanded` | 233 | `convergence:288:warmup_supplied` | 2026-09-02 07:51:31 | [log](user_data/convergence_logs/ZaratustraDCA5-ladder.log) |
| `ZaratustraV31` | `futures_long_short` | `E1_expanded` | 4921 | `convergence:168:warmup_supplied` | 2026-09-14 19:32:07 | [archive](user_data/profile_smoke/ZaratustraV31-17f3529d-smoke_20200301_20200401-b4807b77-2026-09-14_19-32-07.zip) [log](user_data/convergence_logs/ZaratustraV31-17f3529d-ladder.log) |
| `abbas` | `spot_long` | `E1_expanded` | 262 | `convergence:2016:warmup_supplied` | 2026-09-06 18:34:59 | [archive](user_data/profile_smoke/abbas-66cc6f6a-2026-09-06_18-34-59.zip) [log](user_data/convergence_logs/abbas-66cc6f6a-ladder.log) |
| `adaptive` | `spot_long` | `E1_expanded` | 559 | `convergence:2016:warmup_supplied` | 2026-09-06 08:57:59 | [archive](user_data/profile_smoke/adaptive-4bc3f073-2026-09-06_08-57-59.zip) [log](user_data/convergence_logs/adaptive-ladder.log) |
| `adaptive_trend` | `spot_long` | `E1_expanded` | 70 | `convergence:180` | 2026-09-09 22:22:58 | [archive](user_data/profile_smoke/adaptive_trend-4c45a656-2026-09-09_22-22-58.zip) [log](user_data/convergence_logs/adaptive_trend-ladder.log) |
| `adx_opt_strat` | `spot_long` | `E1_expanded` | 234 | `convergence:1440:warmup_supplied` | 2026-09-01 19:53:04 | [archive](user_data/profile_smoke/adx_opt_strat-2026-09-01_19-53-04.zip) [log](user_data/convergence_logs/adx_opt_strat-ladder.log) |
| `adxbbrsi2` | `spot_long` | `E1_expanded` | 563 | `convergence:336:warmup_supplied` | 2026-09-06 08:58:12 | [archive](user_data/profile_smoke/adxbbrsi2-ab42fd07-2026-09-06_08-58-12.zip) [log](user_data/convergence_logs/adxbbrsi2-ladder.log) |
| `bb_rsi_opt_new` | `spot_long` | `E1_expanded` | 8 | `convergence:168:warmup_supplied` | 2026-09-01 19:53:42 | [archive](user_data/profile_smoke/bb_rsi_opt_new-2026-09-01_19-53-42.zip) [log](user_data/convergence_logs/bb_rsi_opt_new-ladder.log) |
| `bbandrsi` | `spot_long` | `E1_expanded` | 5577 | `convergence:192:warmup_supplied` | 2026-09-07 17:48:54 | [archive](user_data/profile_smoke/bbandrsi-b2360e0a-2026-09-07_17-48-54.zip) [log](user_data/convergence_logs/bbandrsi-ladder.log) |
| `bbrsi` | `spot_long` | `E1_expanded` | 4565 | `convergence:180:warmup_supplied` | 2026-09-06 04:39:10 | [archive](user_data/profile_smoke/bbrsi-10d8c6d1-2026-09-06_04-39-10.zip) [log](user_data/convergence_logs/bbrsi-10d8c6d1-ladder.log) |
| `bbrsi1_strategy` | `spot_long` | `E1_expanded` | 432 | `convergence:288:warmup_supplied` | 2026-09-01 20:44:53 | [archive](user_data/profile_smoke/bbrsi1_strategy-2026-09-01_20-44-53.zip) [log](user_data/convergence_logs/bbrsi1_strategy-ladder.log) |
| `bbrsi4Freq` | `spot_long` | `E1_expanded` | 3949 | `convergence:168:warmup_supplied` | 2026-09-06 08:59:54 | [archive](user_data/profile_smoke/bbrsi4Freq-71c90bc9-2026-09-06_08-59-54.zip) [log](user_data/convergence_logs/bbrsi4Freq-ladder.log) |
| `bestV2` | `spot_long` | `E1_expanded` | 295 | `convergence:2016:warmup_supplied` | 2026-09-06 09:02:00 | [archive](user_data/profile_smoke/bestV2-4c1faad7-2026-09-06_09-02-00.zip) [log](user_data/convergence_logs/bestV2-ladder.log) |
| `bigshort` | `futures_long_short` | `E1_expanded` | 331 | `convergence:1440:warmup_supplied` | 2026-09-06 18:24:57 | [archive](user_data/profile_smoke/bigshort-ef8d2c90-2026-09-06_18-24-57.zip) [log](user_data/convergence_logs/bigshort-ef8d2c90-ladder.log) |
| `binance` | `spot_long` | `E1_expanded` | 36 | `convergence:2016:warmup_supplied` | 2026-09-14 19:31:33 | [archive](user_data/profile_smoke/binance-59bba357-smoke_20200301_20200401-b4807b77-2026-09-14_19-31-33.zip) [log](user_data/convergence_logs/binance-59bba357-ladder.log) |
| `binance_shorts` | `futures_short` | `E1_expanded` | 11 | `convergence:2016:warmup_supplied` | 2026-09-14 19:31:38 | [archive](user_data/profile_smoke/binance_shorts-2d7eb835-smoke_20200301_20200401-b4807b77-2026-09-14_19-31-38.zip) [log](user_data/convergence_logs/binance_shorts-2d7eb835-ladder.log) |
| `botbaby` | `spot_long` | `E1_expanded` | 10589 | `convergence:1440:warmup_supplied` | 2026-09-06 09:03:24 | [archive](user_data/profile_smoke/botbaby-dc176f79-2026-09-06_09-03-24.zip) [log](user_data/convergence_logs/botbaby-ladder.log) |
| `chatgpt` | `spot_long` | `E1_expanded` | 72 | `convergence:336:warmup_supplied` | 2026-09-06 18:23:33 | [archive](user_data/profile_smoke/chatgpt-60965168-2026-09-06_18-23-33.zip) [log](user_data/convergence_logs/chatgpt-60965168-ladder.log) |
| `conny` | `spot_long` | `E1_expanded` | 4663 | `convergence:96:warmup_supplied` | 2026-09-06 09:05:02 | [archive](user_data/profile_smoke/conny-82fa40ec-2026-09-06_09-05-02.zip) [log](user_data/convergence_logs/conny-ladder.log) |
| `cryptohassle` | `spot_long` | `E1_expanded` | 82 | `convergence:336:warmup_supplied` | 2026-09-01 19:55:42 | [archive](user_data/profile_smoke/cryptohassle-2026-09-01_19-55-42.zip) [log](user_data/convergence_logs/cryptohassle-ladder.log) |
| `cryptotank` | `spot_long` | `E1_expanded` | 1801 | `convergence:336:warmup_supplied` | 2026-09-07 16:18:47 | [archive](user_data/profile_smoke/cryptotank-c9c1afb9-2026-09-07_16-18-47.zip) [log](user_data/convergence_logs/cryptotank-ladder.log) |
| `cryptotankV2` | `spot_long` | `E1_expanded` | 5602 | `convergence:576:warmup_supplied` | 2026-09-07 16:27:29 | [archive](user_data/profile_smoke/cryptotankV2-210f4053-2026-09-07_16-27-29.zip) [log](user_data/convergence_logs/cryptotankV2-ladder.log) |
| `cryptotankV5` | `spot_long` | `E1_expanded` | 4051 | `convergence:672:warmup_supplied` | 2026-09-07 16:17:34 | [archive](user_data/profile_smoke/cryptotankV5-a75d705b-2026-09-07_16-17-34.zip) [log](user_data/convergence_logs/cryptotankV5-ladder.log) |
| `custom_sell` | `spot_long` | `E1_expanded` | 327 | `convergence:288` | 2026-08-31 16:13:12 | [archive](user_data/profile_smoke/custom_sell-2026-08-31_16-13-12.zip) [log](user_data/convergence_logs/custom_sell-ladder.log) |
| `dualwave` | `spot_long` | `E1_expanded` | 2594 | `convergence:672:warmup_supplied` | 2026-09-06 03:30:32 | [archive](user_data/profile_smoke/dualwave-d51fbd84-2026-09-06_03-30-32.zip) [log](user_data/convergence_logs/dualwave-ladder.log) |
| `e6v34` | `spot_long` | `E1_expanded` | 12023 | `convergence:672:warmup_supplied` | 2026-09-06 09:06:34 | [archive](user_data/profile_smoke/e6v34-c1676810-2026-09-06_09-06-34.zip) [log](user_data/convergence_logs/e6v34-ladder.log) |
| `eltoro` | `spot_long` | `E1_expanded` | 3178 | `convergence:1344:warmup_supplied` | 2026-09-07 16:37:48 | [archive](user_data/profile_smoke/eltoro-4b7ac68a-2026-09-07_16-37-48.zip) [log](user_data/convergence_logs/eltoro-ladder.log) |
| `eltoro1_4` | `spot_long` | `E1_expanded` | 1944 | `convergence:2160:warmup_supplied` | 2026-09-06 12:03:32 | [archive](user_data/profile_smoke/eltoro1_4-9577fac2-2026-09-06_12-03-32.zip) [log](user_data/convergence_logs/eltoro1_4-ladder.log) |
| `eltoro1_4_simple` | `spot_long` | `E1_expanded` | 1990 | `convergence:672:warmup_supplied` | 2026-09-07 16:40:05 | [archive](user_data/profile_smoke/eltoro1_4_simple-8a1dc3d9-2026-09-07_16-40-05.zip) [log](user_data/convergence_logs/eltoro1_4_simple-ladder.log) |
| `ema` | `spot_long` | `E1_expanded` | 14453 | `convergence:2016:warmup_supplied` | 2026-09-06 09:09:49 | [archive](user_data/profile_smoke/ema-8c15a763-2026-09-06_09-09-49.zip) [log](user_data/convergence_logs/ema-ladder.log) |
| `fahmibah` | `spot_long` | `E1_expanded` | 17157 | `convergence:288:warmup_supplied` | 2026-09-07 15:44:18 | [archive](user_data/profile_smoke/fahmibah-9c2d9fa5-2026-09-07_15-44-18.zip) [log](user_data/convergence_logs/fahmibah-ladder.log) |
| `gettinMoist` | `spot_long` | `E1_expanded` | 16015 | `convergence:288:warmup_supplied` | 2026-09-07 18:41:13 | [archive](user_data/profile_smoke/gettinMoist-03ddd395-2026-09-07_18-41-13.zip) [log](user_data/convergence_logs/gettinMoist-ladder.log) |
| `gpt_reversal` | `spot_long` | `E1_expanded` | 20 | `convergence:1440:warmup_supplied` | 2026-09-06 18:25:14 | [archive](user_data/profile_smoke/gpt_reversal-15eecf49-2026-09-06_18-25-14.zip) [log](user_data/convergence_logs/gpt_reversal-15eecf49-ladder.log) |
| `hansencandlepatternV1` | `spot_long` | `E1_expanded` | 13621 | `convergence:24:warmup_supplied` | 2026-09-05 22:41:50 | [archive](user_data/profile_smoke/hansencandlepatternV1-3b3b1191-2026-09-05_22-41-50.zip) [log](user_data/convergence_logs/hansencandlepatternV1-ladder.log) |
| `heikin` | `spot_long` | `E1_expanded` | 13722 | `convergence:24:warmup_supplied` | 2026-09-05 22:43:28 | [archive](user_data/profile_smoke/heikin-50477714-2026-09-05_22-43-28.zip) [log](user_data/convergence_logs/heikin-ladder.log) |
| `hlhb` | `spot_long` | `E1_expanded` | 718 | `convergence:540:warmup_supplied` | 2026-09-06 02:27:41 | [archive](user_data/profile_smoke/hlhb-4d4b7c4a-2026-09-06_02-27-41.zip) [log](user_data/convergence_logs/hlhb-4d4b7c4a-ladder.log) |
| `ichi` | `spot_long` | `E1_expanded` | 61 | `convergence:168:warmup_supplied` | 2026-09-06 15:16:31 | [archive](user_data/profile_smoke/ichi-a7e6edf3-2026-09-06_15-16-31.zip) [log](user_data/convergence_logs/ichi-a7e6edf3-ladder.log) |
| `keltnerchannel` | `spot_long` | `E1_expanded` | 1613 | `convergence:360:warmup_supplied` | 2026-09-06 09:13:28 | [archive](user_data/profile_smoke/keltnerchannel-8f9afe32-2026-09-06_09-13-28.zip) [log](user_data/convergence_logs/keltnerchannel-ladder.log) |
| `mabStra` | `spot_long` | `E1_expanded` | 3592 | `convergence:42:warmup_supplied` | 2026-09-05 18:21:41 | [archive](user_data/profile_smoke/mabStra-c5e70fad-2026-09-05_18-21-41.zip) [log](user_data/convergence_logs/mabStra-ladder.log) |
| `macd_recovery` | `spot_long` | `E1_expanded` | 202 | `convergence:2016:warmup_supplied` | 2026-09-01 19:56:22 | [archive](user_data/profile_smoke/macd_recovery-2026-09-01_19-56-22.zip) [log](user_data/convergence_logs/macd_recovery-ladder.log) |
| `mark_strat` | `spot_long` | `E1_expanded` | 942 | `convergence:1440:warmup_supplied` | 2026-09-01 19:57:13 | [archive](user_data/profile_smoke/mark_strat-2026-09-01_19-57-13.zip) [log](user_data/convergence_logs/mark_strat-ladder.log) |
| `mark_strat_opt` | `spot_long` | `E1_expanded` | 11 | `convergence:1440:warmup_supplied` | 2026-09-01 20:50:12 | [archive](user_data/profile_smoke/mark_strat_opt-2026-09-01_20-50-12.zip) [log](user_data/convergence_logs/mark_strat_opt-ladder.log) |
| `momentum` | `futures_long_short` | `E1_expanded` | 682 | `convergence:288` | 2026-09-03 14:12:19 | [log](user_data/convergence_logs/momentum-ladder.log) |
| `momentum_long` | `spot_long` | `E1_expanded` | 12822 | `convergence:288` | 2026-09-06 02:42:17 | [archive](user_data/profile_smoke/momentum_long-4065a69d-2026-09-06_02-42-17.zip) [log](user_data/convergence_logs/momentum_long-ladder.log) |
| `momentum_rsi` | `futures_long_short` | `E1_expanded` | 551 | `convergence:200` | 2026-09-03 14:13:38 | [log](user_data/convergence_logs/momentum_rsi-ladder.log) |
| `momentum_wick` | `futures_long_short` | `E1_expanded` | 361 | `convergence:288` | 2026-09-03 14:14:32 | [log](user_data/convergence_logs/momentum_wick-ladder.log) |
| `moonhouse` | `spot_long` | `E1_expanded` | 90 | `convergence:90:warmup_supplied` | 2026-09-06 12:07:56 | [archive](user_data/profile_smoke/moonhouse-a6f2773a-2026-09-06_12-07-56.zip) [log](user_data/convergence_logs/moonhouse-ladder.log) |
| `multi_tf` | `spot_long` | `E1_expanded` | 62 | `convergence:288:warmup_supplied` | 2026-09-10 10:13:10 | [archive](user_data/profile_smoke/multi_tf-1362b53b-smoke_20200301_20200401-b4807b77-2026-09-10_10-13-10.zip) [log](user_data/convergence_logs/multi_tf-1362b53b-ladder.log) |
| `quantumfirst` | `spot_long` | `E1_expanded` | 227 | `convergence:288:warmup_supplied` | 2026-09-01 19:57:53 | [archive](user_data/profile_smoke/quantumfirst-2026-09-01_19-57-53.zip) [log](user_data/convergence_logs/quantumfirst-ladder.log) |
| `redditMA` | `spot_long` | `E1_expanded` | 193 | `convergence:192:warmup_supplied` | 2026-09-01 19:58:32 | [archive](user_data/profile_smoke/redditMA-2026-09-01_19-58-32.zip) [log](user_data/convergence_logs/redditMA-ladder.log) |
| `simple_patterns` | `spot_long` | `E1_expanded` | 1845 | `native` | 2026-08-31 15:55:52 | [archive](user_data/profile_smoke/simple_patterns-2026-08-31_15-55-52.zip) |
| `simple_vwap_v1` | `spot_long` | `E1_expanded` | 1 | `convergence:2190:warmup_supplied` | 2026-09-05 15:12:31 | [archive](user_data/profile_smoke/simple_vwap_v1-28330b62-2026-09-05_15-12-31.zip) [log](user_data/convergence_logs/simple_vwap_v1-28330b62-ladder.log) |
| `slope_is_dopeCT` | `spot_long` | `E1_expanded` | 5862 | `convergence:672:warmup_supplied` | 2026-09-07 16:24:02 | [archive](user_data/profile_smoke/slope_is_dopeCT-fdf33865-2026-09-07_16-24-02.zip) [log](user_data/convergence_logs/slope_is_dopeCT-ladder.log) |
| `stoploss` | `spot_long` | `E1_expanded` | 10999 | `convergence:288:warmup_supplied` | 2026-09-06 09:23:20 | [archive](user_data/profile_smoke/stoploss-f9006559-2026-09-06_09-23-20.zip) [log](user_data/convergence_logs/stoploss-ladder.log) |
| `strato` | `spot_long` | `E1_expanded` | 7254 | `convergence:1440:warmup_supplied` | 2026-09-09 16:43:00 | [archive](user_data/profile_smoke/strato-79fbe4ba-2026-09-09_16-43-00.zip) [log](user_data/convergence_logs/strato-ladder.log) |
| `tbtest` | `spot_long` | `E1_expanded` | 3821 | `convergence:288:warmup_supplied` | 2026-09-05 22:59:52 | [archive](user_data/profile_smoke/tbtest-651f742e-2026-09-05_22-59-52.zip) [log](user_data/convergence_logs/tbtest-ladder.log) |
| `thetank3` | `spot_long` | `E1_expanded` | 6492 | `convergence:672:warmup_supplied` | 2026-09-07 16:27:35 | [archive](user_data/profile_smoke/thetank3-b9cc49ee-2026-09-07_16-27-35.zip) [log](user_data/convergence_logs/thetank3-ladder.log) |
| `thetank4TV` | `spot_long` | `E1_expanded` | 2676 | `convergence:672:warmup_supplied` | 2026-09-07 16:31:49 | [archive](user_data/profile_smoke/thetank4TV-d429206d-2026-09-07_16-31-49.zip) [log](user_data/convergence_logs/thetank4TV-ladder.log) |
| `true_lambo` | `spot_long` | `E1_expanded` | 931 | `convergence:2016:warmup_supplied` | 2026-09-07 01:19:23 | [archive](user_data/profile_smoke/true_lambo-7c28329d-2026-09-07_01-19-23.zip) [log](user_data/convergence_logs/true_lambo-ladder.log) |
| `twinturboV8` | `spot_long` | `E1_expanded` | 110 | `convergence:2016:warmup_supplied` | 2026-09-06 03:06:26 | [archive](user_data/profile_smoke/twinturboV8-e01abfe2-2026-09-06_03-06-26.zip) [log](user_data/convergence_logs/twinturboV8-ladder.log) |
| `twinturboV8_2` | `spot_long` | `E1_expanded` | 83 | `convergence:2016:warmup_supplied` | 2026-09-06 03:07:09 | [archive](user_data/profile_smoke/twinturboV8_2-bd25893d-2026-09-06_03-07-09.zip) [log](user_data/convergence_logs/twinturboV8_2-ladder.log) |
| `ultratank` | `spot_long` | `E1_expanded` | 2537 | `convergence:336:warmup_supplied` | 2026-09-07 16:30:06 | [archive](user_data/profile_smoke/ultratank-1dfe916a-2026-09-07_16-30-06.zip) [log](user_data/convergence_logs/ultratank-ladder.log) |
| `wavetrend` | `spot_long` | `E1_expanded` | 3985 | `convergence:336:warmup_supplied` | 2026-09-07 16:11:51 | [archive](user_data/profile_smoke/wavetrend-5900a358-2026-09-07_16-11-51.zip) [log](user_data/convergence_logs/wavetrend-ladder.log) |
| `wavetrend_rsi` | `spot_long` | `E1_expanded` | 1589 | `convergence:336:warmup_supplied` | 2026-09-07 16:32:22 | [archive](user_data/profile_smoke/wavetrend_rsi-32bf6591-2026-09-07_16-32-22.zip) [log](user_data/convergence_logs/wavetrend_rsi-ladder.log) |

The calls behind each, one per gate:

- `ADXDM`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ADXDM --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/_ADXDM" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ADXDM-eef844db --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ADXDM --strategy-path user_data/profile_bias_strategies/ADXDM-eef844db --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ADXDM --strategy-path user_data/profile_bias_strategies/ADXDM-eef844db --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ASDTSRockwellTrading --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ASDTSRockwellTrading-a0a64ac9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ASDTSRockwellTrading --strategy-path user_data/profile_bias_strategies/ASDTSRockwellTrading --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ASDTSRockwellTrading --strategy-path user_data/profile_bias_strategies/ASDTSRockwellTrading --timerange 20190101-20190401 --no-color
  ```
- `ActionZone`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ActionZone --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ActionZone-e0687d36 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ActionZone --strategy-path user_data/profile_bias_strategies/ActionZone --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ActionZone --strategy-path user_data/profile_bias_strategies/ActionZone --timerange 20190101-20190401 --no-color
  ```
- `AdaptiveMAStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy AdaptiveMAStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AdaptiveMAStrategy-dcd0265a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AdaptiveMAStrategy --strategy-path user_data/profile_bias_strategies/AdaptiveMAStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AdaptiveMAStrategy --strategy-path user_data/profile_bias_strategies/AdaptiveMAStrategy --timerange 20190101-20190401 --no-color
  ```
- `AdaptiveRegime`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy AdaptiveRegime --strategy-path repos/Kureshi25_cryptobot/user_data/strategies --timerange 20200101-20210101 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AdaptiveRegime-90b67ba4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy AdaptiveRegime --strategy-path user_data/profile_bias_strategies/AdaptiveRegime-90b67ba4 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy AdaptiveRegime --strategy-path user_data/profile_bias_strategies/AdaptiveRegime-90b67ba4 --timerange 20200301-20200401 --no-color --startup-candle 1 2 7 14
  ```
- `AdaptiveRegimeLong`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy AdaptiveRegimeLong --strategy-path repos/Kureshi25_cryptobot/user_data/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AdaptiveRegimeLong --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AdaptiveRegimeLong --strategy-path user_data/profile_bias_strategies/AdaptiveRegimeLong-aea59d43 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AdaptiveRegimeLong --strategy-path user_data/profile_bias_strategies/AdaptiveRegimeLong-aea59d43 --timerange 20200301-20200601 --no-color --startup-candle 2 7 14 30 90 365
  ```
- `AdxSmas`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy AdxSmas --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AdxSmas-fe8ff69f --cache none
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy AdxStrengthStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AdxStrengthStrategy-43ff628d --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy AlligatorStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AlligatorStrategy-d98e241f --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy AlwaysBuy --strategy-path repos/davidzr_freqtrade-strategies/strategies/AlwaysBuy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AlwaysBuy-3d49f615 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AlwaysBuy --strategy-path user_data/profile_bias_strategies/AlwaysBuy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/AlwaysBuy_startup_288.json --strategy AlwaysBuy --strategy-path user_data/profile_bias_strategies/AlwaysBuy --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `AntigravityGridStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy AntigravityGridStrategy --strategy-path repos/Vijay190899_Trade-Bot/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AntigravityGridStrategy-c15a2d4c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AntigravityGridStrategy --strategy-path user_data/profile_bias_strategies/AntigravityGridStrategy-c15a2d4c --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AntigravityGridStrategy --strategy-path user_data/profile_bias_strategies/AntigravityGridStrategy-c15a2d4c --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `Apollo11`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Apollo11 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Apollo11-ec6cf35d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Apollo11_gate.json --strategy Apollo11 --strategy-path user_data/profile_bias_strategies/Apollo11 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Apollo11 --strategy-path user_data/profile_bias_strategies/Apollo11 --timerange 20190101-20190401 --no-color
  ```
- `Argrelextrema`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/Argrelextrema-0ba99988-override-2c7527d808c6.json --strategy Argrelextrema --strategy-path repos/hamidreza07_freqai-strategy/classic --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Argrelextrema-0ba99988 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Argrelextrema-0ba99988_gate.json --strategy Argrelextrema --strategy-path user_data/profile_bias_strategies/Argrelextrema-0ba99988 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy Argrelextrema --strategy-path user_data/profile_bias_strategies/Argrelextrema-0ba99988 --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016 --timeframe 5m
  ```
- `AroonTrendStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy AroonTrendStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AroonTrendStrategy-c552fb5d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AroonTrendStrategy --strategy-path user_data/profile_bias_strategies/AroonTrendStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AroonTrendStrategy --strategy-path user_data/profile_bias_strategies/AroonTrendStrategy --timerange 20190101-20190401 --no-color
  ```
- `AtrTrailingStopStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy AtrTrailingStopStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AtrTrailingStopStrategy-dde18ecb --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AtrTrailingStopStrategy --strategy-path user_data/profile_bias_strategies/AtrTrailingStopStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AtrTrailingStopStrategy --strategy-path user_data/profile_bias_strategies/AtrTrailingStopStrategy --timerange 20190101-20190401 --no-color
  ```
- `AverageStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy AverageStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AverageStrategy-458e95dd --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AverageStrategy --strategy-path user_data/profile_bias_strategies/AverageStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AverageStrategy --strategy-path user_data/profile_bias_strategies/AverageStrategy --timerange 20190101-20190401 --no-color
  ```
- `AwesomeMacd`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy AwesomeMacd --strategy-path repos/MelvynClark_Freqtrade-Strategy/AwesomeMACD --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/AwesomeMacd-a1b857b0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AwesomeMacd --strategy-path user_data/profile_bias_strategies/AwesomeMacd --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/AwesomeMacd_startup_48.json --strategy AwesomeMacd --strategy-path user_data/profile_bias_strategies/AwesomeMacd --timerange 20190101-20190401 --no-color --startup-candle 48 168 336 720 2160
  ```
- `BB10fall`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB10fall --strategy-path repos/shadowp2810_technical_indicators_cryptos/Freqtrade/ft_userdata/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB10fall-cef5331b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BB10fall-cef5331b_gate.json --strategy BB10fall --strategy-path user_data/profile_bias_strategies/BB10fall-cef5331b --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB10fall --strategy-path user_data/profile_bias_strategies/BB10fall-cef5331b --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `BBKCBounce`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BBKCBounce --strategy-path repos/webclinic017_strategies-freqtrade-/archived --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBKCBounce-4161a6f7 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBKCBounce --strategy-path user_data/profile_bias_strategies/BBKCBounce-4161a6f7 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBKCBounce --strategy-path user_data/profile_bias_strategies/BBKCBounce-4161a6f7 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BBRSI2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSI2 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSI2-86823e82 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI2 --strategy-path user_data/profile_bias_strategies/BBRSI2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI2 --strategy-path user_data/profile_bias_strategies/BBRSI2 --timerange 20190101-20190401 --no-color
  ```
- `BBRSI21`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSI21 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSI21 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSI21-8d3cd1cd --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI21 --strategy-path user_data/profile_bias_strategies/BBRSI21 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI21 --strategy-path user_data/profile_bias_strategies/BBRSI21 --timerange 20190101-20190401 --no-color
  ```
- `BBRSI3366`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSI3366 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSI3366 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSI3366-5eaa7494 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI3366 --strategy-path user_data/profile_bias_strategies/BBRSI3366 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI3366 --strategy-path user_data/profile_bias_strategies/BBRSI3366 --timerange 20190101-20190401 --no-color
  ```
- `BBRSI4cust`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSI4cust --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSI4cust --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSI4cust-15ae73f3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI4cust --strategy-path user_data/profile_bias_strategies/BBRSI4cust --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSI4cust --strategy-path user_data/profile_bias_strategies/BBRSI4cust --timerange 20190101-20190401 --no-color
  ```
- `BBRSINaiveStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSINaiveStrategy --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSINaiveStrategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSINaiveStrategy-06e452ee --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSINaiveStrategy --strategy-path user_data/profile_bias_strategies/BBRSINaiveStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSINaiveStrategy --strategy-path user_data/profile_bias_strategies/BBRSINaiveStrategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSIOptim2020Strategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSIOptim2020Strategy --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSIOptim2020Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSIOptim2020Strategy-953f76a1 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptim2020Strategy --strategy-path user_data/profile_bias_strategies/BBRSIOptim2020Strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptim2020Strategy --strategy-path user_data/profile_bias_strategies/BBRSIOptim2020Strategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSIOptimStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSIOptimStrategy --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSIOptimStrategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSIOptimStrategy-17edd828 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptimStrategy --strategy-path user_data/profile_bias_strategies/BBRSIOptimStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptimStrategy --strategy-path user_data/profile_bias_strategies/BBRSIOptimStrategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSIOptimizedStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSIOptimizedStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSIOptimizedStrategy-79f2af5e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptimizedStrategy --strategy-path user_data/profile_bias_strategies/BBRSIOptimizedStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIOptimizedStrategy --strategy-path user_data/profile_bias_strategies/BBRSIOptimizedStrategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSIStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSIStrategy --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSIStrategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSIStrategy-6bd56231 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIStrategy --strategy-path user_data/profile_bias_strategies/BBRSIStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIStrategy --strategy-path user_data/profile_bias_strategies/BBRSIStrategy --timerange 20190101-20190401 --no-color
  ```
- `BBRSITV`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BBRSITV --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSITV-1794e5d4-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSITV --strategy-path user_data/profile_bias_strategies/BBRSITV --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSITV --strategy-path user_data/profile_bias_strategies/BBRSITV --timerange 20190101-20190401 --no-color
  ```
- `BBRSITV4`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy BBRSITV4 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSITV4 --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSITV4 --strategy-path user_data/profile_bias_strategies/BBRSITV4-43cc369e --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSITV4 --strategy-path user_data/profile_bias_strategies/BBRSITV4-43cc369e --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `BBRSITV5`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy BBRSITV5 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSITV5 --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSITV5 --strategy-path user_data/profile_bias_strategies/BBRSITV5-49193951 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSITV5 --strategy-path user_data/profile_bias_strategies/BBRSITV5-49193951 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `BBRSIoriginal`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/BBRSIoriginal-override-f400cf1f3448.json --strategy BBRSIoriginal --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSIoriginal --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSIoriginal --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BBRSIoriginal_gate.json --strategy BBRSIoriginal --strategy-path user_data/profile_bias_strategies/BBRSIoriginal --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BBRSIoriginal_startup_24.json --strategy BBRSIoriginal --strategy-path user_data/profile_bias_strategies/BBRSIoriginal --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `BBRSIv2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBRSIv2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSIv2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBRSIv2-ef4f5b04 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIv2 --strategy-path user_data/profile_bias_strategies/BBRSIv2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIv2 --strategy-path user_data/profile_bias_strategies/BBRSIv2 --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `BB_RPB_TSL_RNG`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB_RPB_TSL_RNG --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_RPB_TSL_RNG-3a0f18b7 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_RNG_2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB_RPB_TSL_RNG_2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BB_RPB_TSL_RNG_2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_RPB_TSL_RNG_2-e03b9f25 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_2 --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_2 --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_2 --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_RNG_TBS`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB_RPB_TSL_RNG_TBS --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_RPB_TSL_RNG_TBS-055d0268 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_TBS --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_TBS --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_TBS --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_TBS --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_RNG_TBS_GOLD`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB_RPB_TSL_RNG_TBS_GOLD --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_RPB_TSL_RNG_TBS_GOLD-c7cbefbb --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_TBS_GOLD --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_TBS_GOLD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_TBS_GOLD --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_TBS_GOLD --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_RNG_VWAP`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB_RPB_TSL_RNG_VWAP --strategy-path repos/davidzr_freqtrade-strategies/strategies/BB_RPB_TSL_RNG_VWAP --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_RPB_TSL_RNG_VWAP-ca3d4565 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_VWAP --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_VWAP --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RPB_TSL_RNG_VWAP --strategy-path user_data/profile_bias_strategies/BB_RPB_TSL_RNG_VWAP --timerange 20190101-20190401 --no-color
  ```
- `BB_RPB_TSL_c7c477d_20211030`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB_RPB_TSL_c7c477d_20211030 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BB_RPB_TSL_c7c477d_20211030 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_RPB_TSL_c7c477d_20211030-2ca1ddc5 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BB_RTR --strategy-path repos/ShahAnuj2610_my-freqtrade/user_data/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BB_RTR-847a19ce --cache none
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BBands --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBands-62f4821e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBands --strategy-path user_data/profile_bias_strategies/BBands --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBands --strategy-path user_data/profile_bias_strategies/BBands --timerange 20190101-20190401 --no-color
  ```
- `BBandsRSI`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBandsRSI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBandsRSI-e3e39ce3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBandsRSI --strategy-path user_data/profile_bias_strategies/BBandsRSI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBandsRSI --strategy-path user_data/profile_bias_strategies/BBandsRSI --timerange 20190101-20190401 --no-color
  ```
- `BBlower`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BBlower --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBlower --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BBlower-f669ea81 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBlower --strategy-path user_data/profile_bias_strategies/BBlower --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBlower --strategy-path user_data/profile_bias_strategies/BBlower --timerange 20190101-20190401 --no-color
  ```
- `Babico_SMA5xBBmid`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Babico_SMA5xBBmid --strategy-path repos/davidzr_freqtrade-strategies/strategies/Babico_SMA5xBBmid --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Babico_SMA5xBBmid-bb288854 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Babico_SMA5xBBmid --strategy-path user_data/profile_bias_strategies/Babico_SMA5xBBmid --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Babico_SMA5xBBmid --strategy-path user_data/profile_bias_strategies/Babico_SMA5xBBmid --timerange 20190101-20190401 --no-color
  ```
- `Bandtastic`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Bandtastic --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Bandtastic-0393a67b --cache none
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BbWidthExpansionStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BbWidthExpansionStrategy-b4818e74 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbWidthExpansionStrategy --strategy-path user_data/profile_bias_strategies/BbWidthExpansionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BbWidthExpansionStrategy --strategy-path user_data/profile_bias_strategies/BbWidthExpansionStrategy --timerange 20190101-20190401 --no-color
  ```
- `BbandRsi`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BbandRsi --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BbandRsi-6dcf5b91 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsi --strategy-path user_data/profile_bias_strategies/BbandRsi --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BbandRsi_startup_1440.json --strategy BbandRsi --strategy-path user_data/profile_bias_strategies/BbandRsi-6dcf5b91 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BbandRsiRolling`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BbandRsiRolling --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BbandRsiRolling-f1489cee --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsiRolling --strategy-path user_data/profile_bias_strategies/BbandRsiRolling --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsiRolling --strategy-path user_data/profile_bias_strategies/BbandRsiRolling --timerange 20190101-20190401 --no-color
  ```
- `Best5m`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy Best5m --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Best5m --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Best5m-b4504e64-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy Best5m --strategy-path user_data/profile_bias_strategies/Best5m-b4504e64 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Best5m_startup_288.json --strategy Best5m --strategy-path user_data/profile_bias_strategies/Best5m-b4504e64 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `BigDrop`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigDrop --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/BigDrop" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigDrop-05954866 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigDrop --strategy-path user_data/profile_bias_strategies/BigDrop-05954866 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigDrop --strategy-path user_data/profile_bias_strategies/BigDrop-05954866 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigPete`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigPete --strategy-path repos/davidzr_freqtrade-strategies/strategies/BigPete --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigPete-b194f963 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigPete --strategy-path user_data/profile_bias_strategies/BigPete --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigPete --strategy-path user_data/profile_bias_strategies/BigPete --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigTrader`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigTrader --strategy-path repos/TheoBrigitte_freqtrade/strategies/profiters --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigTrader-fc53f0ba --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigTrader --strategy-path user_data/profile_bias_strategies/BigTrader --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigTrader --strategy-path user_data/profile_bias_strategies/BigTrader --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigWill`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigWill --strategy-path repos/djienne_YOUTUBE_STRATEGIES_FREQTRADE/Strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigWill-387f07ca --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigWill --strategy-path user_data/profile_bias_strategies/BigWill-387f07ca --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigWill --strategy-path user_data/profile_bias_strategies/BigWill-387f07ca --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `BigZ03`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigZ03 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BigZ03 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigZ03-73f3ab21 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03 --strategy-path user_data/profile_bias_strategies/BigZ03 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03 --strategy-path user_data/profile_bias_strategies/BigZ03 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ03HO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigZ03HO --strategy-path repos/davidzr_freqtrade-strategies/strategies/BigZ03HO --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigZ03HO-223e9e10 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03HO --strategy-path user_data/profile_bias_strategies/BigZ03HO --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03HO --strategy-path user_data/profile_bias_strategies/BigZ03HO --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ04_TSL3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigZ04_TSL3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigZ04_TSL3-da25b418 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL3 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL3 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ04_TSL4`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigZ04_TSL4 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigZ04_TSL4-e8864ca5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL4 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL4 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL4 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL4 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BigZ07Next`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigZ07Next --strategy-path repos/davidzr_freqtrade-strategies/strategies/BigZ07Next --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigZ07Next-49314d41 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ07Next --strategy-path user_data/profile_bias_strategies/BigZ07Next --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ07Next --strategy-path user_data/profile_bias_strategies/BigZ07Next --timerange 20190101-20190401 --no-color
  ```
- `BigZ07Next2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BigZ07Next2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BigZ07Next2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BigZ07Next2-746d2c59 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ07Next2 --strategy-path user_data/profile_bias_strategies/BigZ07Next2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ07Next2 --strategy-path user_data/profile_bias_strategies/BigZ07Next2 --timerange 20190101-20190401 --no-color
  ```
- `BinClucMad`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BinClucMad --strategy-path repos/davidzr_freqtrade-strategies/strategies/BinClucMad --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinClucMad-22180ec8 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMad --strategy-path user_data/profile_bias_strategies/BinClucMad --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMad --strategy-path user_data/profile_bias_strategies/BinClucMad --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BinClucMadDevelop`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BinClucMadDevelop --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinClucMadDevelop-43196dbd --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMadDevelop --strategy-path user_data/profile_bias_strategies/BinClucMadDevelop-43196dbd --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMadDevelop --strategy-path user_data/profile_bias_strategies/BinClucMadDevelop --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BinClucMadSMADevelop`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BinClucMadSMADevelop --strategy-path repair/patched/repos/MMR-19_freqtrade-strategies/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinClucMadSMADevelop-485890ae --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMadSMADevelop --strategy-path user_data/profile_bias_strategies/BinClucMadSMADevelop-485890ae --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMadSMADevelop --strategy-path user_data/profile_bias_strategies/BinClucMadSMADevelop --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BinClucMadV1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BinClucMadV1 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BinClucMadV1 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinClucMadV1-708fb3e3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMadV1 --strategy-path user_data/profile_bias_strategies/BinClucMadV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMadV1 --strategy-path user_data/profile_bias_strategies/BinClucMadV1 --timerange 20190101-20190401 --no-color
  ```
- `BinHV27`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BinHV27 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV27-d117151b --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV27 --strategy-path user_data/profile_bias_strategies/BinHV27 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV27 --strategy-path user_data/profile_bias_strategies/BinHV27 --timerange 20190101-20190401 --no-color
  ```
- `BinHV27F`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long.json --strategy BinHV27F --strategy-path repos/eovie_freqtrade_strs/binance/Archive --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV27F --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy BinHV27F --strategy-path user_data/profile_bias_strategies/BinHV27F --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy BinHV27F --strategy-path user_data/profile_bias_strategies/BinHV27F --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `BinHV27_combined`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy BinHV27_combined --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/BinClucMadV1 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV27_combined-9aaca5ac-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy BinHV27_combined --strategy-path user_data/profile_bias_strategies/BinHV27_combined-9aaca5ac --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy BinHV27_combined --strategy-path user_data/profile_bias_strategies/BinHV27_combined-9aaca5ac --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `BinHV27_short`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy BinHV27_short --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV27_short --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BinHV27_short-15a8226e_gate.json --strategy BinHV27_short --strategy-path user_data/profile_bias_strategies/BinHV27_short-15a8226e --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy BinHV27_short --strategy-path user_data/profile_bias_strategies/BinHV27_short --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `BinHV27_werkkrew`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BinHV27_werkkrew --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV27_werkkrew-3a997e27-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/BinHV27_werkkrew-3a997e27_gate.json --strategy BinHV27_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV27_werkkrew-3a997e27 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV27_werkkrew_startup_288.json --strategy BinHV27_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV27_werkkrew --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BinHV45`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BinHV45 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV45-db2dd482 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45 --strategy-path user_data/profile_bias_strategies/BinHV45 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV45_startup_1440.json --strategy BinHV45 --strategy-path user_data/profile_bias_strategies/BinHV45 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BinHV45HO`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BinHV45HO --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV45HO-2a444e3c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45HO --strategy-path user_data/profile_bias_strategies/BinHV45HO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45HO --strategy-path user_data/profile_bias_strategies/BinHV45HO --timerange 20190101-20190401 --no-color
  ```
- `BinHV45_kanaxe`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BinHV45_kanaxe --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV45_kanaxe-5d56a0a8 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_kanaxe --strategy-path user_data/profile_bias_strategies/BinHV45_kanaxe --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV45_kanaxe_startup_1440.json --strategy BinHV45_kanaxe --strategy-path user_data/profile_bias_strategies/BinHV45_kanaxe --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BinHV45_stash`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BinHV45_stash --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV45_stash-2477766f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_stash --strategy-path user_data/profile_bias_strategies/BinHV45_stash --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV45_stash_startup_1440.json --strategy BinHV45_stash --strategy-path user_data/profile_bias_strategies/BinHV45_stash --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BinHV45_werkkrew`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BinHV45_werkkrew --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinHV45_werkkrew-1637ab87 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV45_werkkrew --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BinHV45_werkkrew_startup_1440.json --strategy BinHV45_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV45_werkkrew --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `BinMfiBTCv5003`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BinMfiBTCv5003 --strategy-path repos/TheoBrigitte_freqtrade/sources/sponsors --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BinMfiBTCv5003-e666be24 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinMfiBTCv5003 --strategy-path user_data/profile_bias_strategies/BinMfiBTCv5003 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinMfiBTCv5003 --strategy-path user_data/profile_bias_strategies/BinMfiBTCv5003 --timerange 20190101-20190401 --no-color
  ```
- `BollingerBandStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BollingerBandStrategy --strategy-path repos/flaviosiotto_freqtrade-strategy/user_data/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BollingerBandStrategy-e77a29cb --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBandStrategy --strategy-path user_data/profile_bias_strategies/BollingerBandStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/BollingerBandStrategy_startup_480.json --strategy BollingerBandStrategy --strategy-path user_data/profile_bias_strategies/BollingerBandStrategy --timerange 20190101-20190401 --no-color --startup-candle 480 960 3360
  ```
- `BollingerBounce`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BollingerBounce --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/__BollingerBounce" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BollingerBounce-4f0dc231 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBounce --strategy-path user_data/profile_bias_strategies/BollingerBounce-4f0dc231 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBounce --strategy-path user_data/profile_bias_strategies/BollingerBounce-4f0dc231 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BollingerBounceStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BollingerBounceStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BollingerBounceStrategy-19dcef82 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBounceStrategy --strategy-path user_data/profile_bias_strategies/BollingerBounceStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBounceStrategy --strategy-path user_data/profile_bias_strategies/BollingerBounceStrategy --timerange 20190101-20190401 --no-color
  ```
- `BollingerBounce_Shorts`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy BollingerBounce_Shorts --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Bounce --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BollingerBounce_Shorts-2011edaf-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy BollingerBounce_Shorts --strategy-path user_data/profile_bias_strategies/BollingerBounce_Shorts-2011edaf --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy BollingerBounce_Shorts --strategy-path user_data/profile_bias_strategies/BollingerBounce_Shorts-2011edaf --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `BopTrendStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BopTrendStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BopTrendStrategy-bb2d63fb --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BopTrendStrategy --strategy-path user_data/profile_bias_strategies/BopTrendStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BopTrendStrategy --strategy-path user_data/profile_bias_strategies/BopTrendStrategy --timerange 20190101-20190401 --no-color
  ```
- `BullishEngulfingStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy BullishEngulfingStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BullishEngulfingStrategy-018dc2d8 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BullishEngulfingStrategy --strategy-path user_data/profile_bias_strategies/BullishEngulfingStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BullishEngulfingStrategy --strategy-path user_data/profile_bias_strategies/BullishEngulfingStrategy --timerange 20190101-20190401 --no-color
  ```
- `BuyDips`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BuyDips --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/BuyDips" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BuyDips-2afdb8fb --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyDips --strategy-path user_data/profile_bias_strategies/BuyDips-2afdb8fb --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyDips --strategy-path user_data/profile_bias_strategies/BuyDips-2afdb8fb --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `BuyOnly`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BuyOnly --strategy-path repos/davidzr_freqtrade-strategies/strategies/BuyOnly --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BuyOnly-e2e0e0ff --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyOnly --strategy-path user_data/profile_bias_strategies/BuyOnly --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyOnly --strategy-path user_data/profile_bias_strategies/BuyOnly --timerange 20190101-20190401 --no-color
  ```
- `BuyOrDie`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy BuyOrDie --strategy-path repos/mikedigriz_freqtrade-strategy-mikedigriz/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/BuyOrDie-7974d456 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyOrDie --strategy-path user_data/profile_bias_strategies/BuyOrDie --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyOrDie --strategy-path user_data/profile_bias_strategies/BuyOrDie --timerange 20190101-20190401 --no-color
  ```
- `CBPete9`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CBPete9 --strategy-path repos/davidzr_freqtrade-strategies/strategies/CBPete9 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CBPete9-6ffadd4c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CBPete9 --strategy-path user_data/profile_bias_strategies/CBPete9 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CBPete9 --strategy-path user_data/profile_bias_strategies/CBPete9 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CCI_BB`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CCI_BB --strategy-path repos/mikedigriz_freqtrade-strategy-mikedigriz/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CCI_BB-05af1dd1 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CCI_BB --strategy-path user_data/profile_bias_strategies/CCI_BB --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/CCI_BB_startup_288.json --strategy CCI_BB --strategy-path user_data/profile_bias_strategies/CCI_BB --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CMCWinner`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CMCWinner --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CMCWinner-a8094718 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CMCWinner --strategy-path user_data/profile_bias_strategies/CMCWinner --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CMCWinner --strategy-path user_data/profile_bias_strategies/CMCWinner --timerange 20190101-20190401 --no-color
  ```
- `CTIBS`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CTIBS --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/CTIBS" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CTIBS-dc6c3262 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CTIBS --strategy-path user_data/profile_bias_strategies/CTIBS --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CTIBS --strategy-path user_data/profile_bias_strategies/CTIBS --timerange 20190101-20190401 --no-color
  ```
- `Candle2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Candle2 --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Candle2-21a0249c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Candle2 --strategy-path user_data/profile_bias_strategies/Candle2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Candle2 --strategy-path user_data/profile_bias_strategies/Candle2 --timerange 20190101-20190401 --no-color
  ```
- `CciMeanReversionStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy CciMeanReversionStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CciMeanReversionStrategy-66df7760 --cache none
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy ChaikinMoneyFlowStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ChaikinMoneyFlowStrategy-553da512 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ChaikinMoneyFlowStrategy --strategy-path user_data/profile_bias_strategies/ChaikinMoneyFlowStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ChaikinMoneyFlowStrategy --strategy-path user_data/profile_bias_strategies/ChaikinMoneyFlowStrategy --timerange 20190101-20190401 --no-color
  ```
- `Chandem`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Chandem --strategy-path repos/davidzr_freqtrade-strategies/strategies/Chandem --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Chandem-fb182bdf --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Chandem --strategy-path user_data/profile_bias_strategies/Chandem --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Chandem --strategy-path user_data/profile_bias_strategies/Chandem --timerange 20190101-20190401 --no-color
  ```
- `Chandemtwo`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Chandemtwo --strategy-path repos/davidzr_freqtrade-strategies/strategies/Chandemtwo --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Chandemtwo-40181d85 --cache none
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Cluc4 --strategy-path repos/davidzr_freqtrade-strategies/strategies/Cluc4 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Cluc4-72b005ae --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc4 --strategy-path user_data/profile_bias_strategies/Cluc4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc4 --strategy-path user_data/profile_bias_strategies/Cluc4 --timerange 20190101-20190401 --no-color
  ```
- `Cluc4werk`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Cluc4werk --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Cluc4werk-442f52c0 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc4werk --strategy-path user_data/profile_bias_strategies/Cluc4werk --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc4werk --strategy-path user_data/profile_bias_strategies/Cluc4werk --timerange 20190101-20190401 --no-color
  ```
- `Cluc5werk`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Cluc5werk --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Cluc5werk-12db1a87 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc5werk --strategy-path user_data/profile_bias_strategies/Cluc5werk --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc5werk --strategy-path user_data/profile_bias_strategies/Cluc5werk --timerange 20190101-20190401 --no-color
  ```
- `Cluc7werk`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Cluc7werk --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Cluc7werk-4eb74e34 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc7werk --strategy-path user_data/profile_bias_strategies/Cluc7werk --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc7werk --strategy-path user_data/profile_bias_strategies/Cluc7werk --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `ClucFiatROI`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucFiatROI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucFiatROI-37eacf60 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucFiatROI --strategy-path user_data/profile_bias_strategies/ClucFiatROI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucFiatROI --strategy-path user_data/profile_bias_strategies/ClucFiatROI --timerange 20190101-20190401 --no-color
  ```
- `ClucFiatSlow`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucFiatSlow --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucFiatSlow-ece26050 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucFiatSlow --strategy-path user_data/profile_bias_strategies/ClucFiatSlow --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucFiatSlow --strategy-path user_data/profile_bias_strategies/ClucFiatSlow --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy ClucHAnix --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix-895ff1e0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/ClucHAnix_gate.json --strategy ClucHAnix --strategy-path user_data/profile_bias_strategies/ClucHAnix --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix --strategy-path user_data/profile_bias_strategies/ClucHAnix --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5M_E0V1E`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy ClucHAnix_5M_E0V1E --strategy-path repos/phuchust_freqtrade_strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_5M_E0V1E-eef9a366 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_5M_E0V1E_DYNAMIC_TB`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy ClucHAnix_5M_E0V1E_DYNAMIC_TB --strategy-path repos/phuchust_freqtrade_strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_5M_E0V1E_DYNAMIC_TB --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E_DYNAMIC_TB --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E_DYNAMIC_TB-a98e4371 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E_DYNAMIC_TB --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E_DYNAMIC_TB-a98e4371 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_5m`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy ClucHAnix_5m --strategy-path repos/davidzr_freqtrade-strategies/strategies/ClucHAnix_5m --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_5m-0d4d79f1-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_5m1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucHAnix_5m1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_5m1-f99f71de --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m1 --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m1 --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_5mTB1`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy ClucHAnix_5mTB1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_5mTB1 --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5mTB1 --strategy-path user_data/profile_bias_strategies/ClucHAnix_5mTB1-64f93719 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5mTB1 --strategy-path user_data/profile_bias_strategies/ClucHAnix_5mTB1-64f93719 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAnix_5m_old`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucHAnix_5m_old --strategy-path repos/TheoBrigitte_freqtrade/strategies/cluc --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_5m_old-54788119 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucHAnix_hhll --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_hhll-9fa2f74f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_hhll --strategy-path user_data/profile_bias_strategies/ClucHAnix_hhll --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_hhll --strategy-path user_data/profile_bias_strategies/ClucHAnix_hhll --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_hhll_TB`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy ClucHAnix_hhll_TB --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAnix_hhll_TB --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_hhll_TB --strategy-path user_data/profile_bias_strategies/ClucHAnix_hhll_TB-069e254e --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_hhll_TB --strategy-path user_data/profile_bias_strategies/ClucHAnix_hhll_TB-069e254e --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `ClucHAwerk`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy ClucHAwerk --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucHAwerk-06465a96 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAwerk --strategy-path user_data/profile_bias_strategies/ClucHAwerk --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAwerk --strategy-path user_data/profile_bias_strategies/ClucHAwerk --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `ClucMay72018`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ClucMay72018 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ClucMay72018-b2c7acb8 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucMay72018 --strategy-path user_data/profile_bias_strategies/ClucMay72018 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucMay72018 --strategy-path user_data/profile_bias_strategies/ClucMay72018 --timerange 20190101-20190401 --no-color
  ```
- `CofiBitStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CofiBitStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CofiBitStrategy-e2d65576 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CofiBitStrategy --strategy-path user_data/profile_bias_strategies/CofiBitStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CofiBitStrategy --strategy-path user_data/profile_bias_strategies/CofiBitStrategy --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndCluc`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndCluc --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndCluc-5a3aec50 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndCluc2021`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndCluc2021 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndCluc2021-8fdd7337 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc2021 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc2021 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndCluc2021 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndCluc2021 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndCluc2021Bull`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndCluc2021Bull --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndCluc2021Bull-28c97ea0 --cache none
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy CombinedBinHAndClucHyperV0 --strategy-path repos/davidzr_freqtrade-strategies/strategies/CombinedBinHAndClucHyperV0 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucHyperV0-e03b8c29 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyperV0 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyperV0 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyperV0 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyperV0 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucHyperV3`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy CombinedBinHAndClucHyperV3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/CombinedBinHAndClucHyperV3 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucHyperV3-84115c08 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyperV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyperV3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucHyperV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucHyperV3 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV2-9a6ae965 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV2 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV2 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV2 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/CombinedBinHAndClucV3 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV3-f17b9b5c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHAndClucV4`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV4 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV4-555d5c39 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV4 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV4 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV4 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV5`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV5 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV5-bfb95c2b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV5 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV5Hyperoptable`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV5Hyperoptable --strategy-path repos/davidzr_freqtrade-strategies/strategies/CombinedBinHAndClucV5Hyperoptable --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV5Hyperoptable-a2c34034 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV5Hyperoptable --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV5Hyperoptable --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV5Hyperoptable --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV5Hyperoptable --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV6`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV6 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV6-5ca5df9c --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV6 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV6 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHAndClucV6H`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy CombinedBinHAndClucV6H --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV6H-88f6bcec --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6H --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV6H-88f6bcec --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6H --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV6H --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHAndClucV7`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV7 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV7-144044aa --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV7 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV7 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV7 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV7 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHAndClucV8`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV8 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV8-32f7e1b0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV8Hyper`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV8Hyper --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV8Hyper-e98d8fc3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8Hyper --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8Hyper --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8Hyper --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8Hyper --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV8XH`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV8XH --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV8XH-f05ebf6e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8XH --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8XH --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8XH --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8XH --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV8XHO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHAndClucV8XHO --strategy-path repos/davidzr_freqtrade-strategies/strategies/CombinedBinHAndClucV8XHO --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHAndClucV8XHO-dc5be8a3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8XHO --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8XHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV8XHO --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV8XHO --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHClucAndMADV3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHClucAndMADV3-bd6b6b26 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHClucAndMADV5`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHClucAndMADV5 --strategy-path repos/davidzr_freqtrade-strategies/strategies/CombinedBinHClucAndMADV5 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHClucAndMADV5-f746355d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV5 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV5 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHClucAndMADV6`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHClucAndMADV6 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHClucAndMADV6-13156fb3 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV6 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV6 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CombinedBinHClucAndMADV9`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CombinedBinHClucAndMADV9 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CombinedBinHClucAndMADV9-35d68152 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV9 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV9 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV9 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV9 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Combined_Indicators`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Combined_Indicators --strategy-path repos/davidzr_freqtrade-strategies/strategies/Combined_Indicators --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Combined_Indicators-8c5e3bcf --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_Indicators --strategy-path user_data/profile_bias_strategies/Combined_Indicators --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_Indicators --strategy-path user_data/profile_bias_strategies/Combined_Indicators --timerange 20190101-20190401 --no-color
  ```
- `Combined_NFIv6_SMA`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Combined_NFIv6_SMA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Combined_NFIv6_SMA-cd9c21e5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv6_SMA --strategy-path user_data/profile_bias_strategies/Combined_NFIv6_SMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv6_SMA --strategy-path user_data/profile_bias_strategies/Combined_NFIv6_SMA --timerange 20190101-20190401 --no-color
  ```
- `Combined_NFIv7_SMA`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Combined_NFIv7_SMA --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Combined_NFIv7_SMA-a3e77574 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv7_SMA --strategy-path user_data/profile_bias_strategies/Combined_NFIv7_SMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Combined_NFIv7_SMA --strategy-path user_data/profile_bias_strategies/Combined_NFIv7_SMA --timerange 20190101-20190401 --no-color
  ```
- `CompleteIndicatorStrategy2`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy CompleteIndicatorStrategy2 --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Best5m --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CompleteIndicatorStrategy2-cc7c80ef-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy CompleteIndicatorStrategy2 --strategy-path user_data/profile_bias_strategies/CompleteIndicatorStrategy2-cc7c80ef --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy CompleteIndicatorStrategy2 --strategy-path user_data/profile_bias_strategies/CompleteIndicatorStrategy2-cc7c80ef --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336
  ```
- `CompositeScoreStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy CompositeScoreStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CompositeScoreStrategy-b827382b --cache none
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy CoppockCurveStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CoppockCurveStrategy-cb29834f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CoppockCurveStrategy --strategy-path user_data/profile_bias_strategies/CoppockCurveStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CoppockCurveStrategy --strategy-path user_data/profile_bias_strategies/CoppockCurveStrategy --timerange 20190101-20190401 --no-color
  ```
- `CoreStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy CoreStrategy --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CoreStrategy-acac6ca9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CoreStrategy --strategy-path user_data/profile_bias_strategies/CoreStrategy-acac6ca9 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CoreStrategy --strategy-path user_data/profile_bias_strategies/CoreStrategy --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `CrossEMAStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CrossEMAStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CrossEMAStrategy-75a10fc2 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy CustomStoplossWithPSAR --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/CustomStoplossWithPSAR-3c86d8a0 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CustomStoplossWithPSAR --strategy-path user_data/profile_bias_strategies/CustomStoplossWithPSAR --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CustomStoplossWithPSAR --strategy-path user_data/profile_bias_strategies/CustomStoplossWithPSAR --timerange 20190101-20190401 --no-color
  ```
- `DD`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy DD --strategy-path repos/davidzr_freqtrade-strategies/strategies/DD --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DD-92f089f2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy DD --strategy-path user_data/profile_bias_strategies/DD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy DD --strategy-path user_data/profile_bias_strategies/DD --timerange 20190101-20190401 --no-color
  ```
- `DMIPRICEDCAStrategyFuture`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy DMIPRICEDCAStrategyFuture --strategy-path repos/LazyPigPig_freqtrade-grid/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DMIPRICEDCAStrategyFuture-5ed3e947 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy DMIPRICEDCAStrategyFuture --strategy-path user_data/profile_bias_strategies/DMIPRICEDCAStrategyFuture-5ed3e947 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/DMIPRICEDCAStrategyFuture_startup_1440.json --strategy DMIPRICEDCAStrategyFuture --strategy-path user_data/profile_bias_strategies/DMIPRICEDCAStrategyFuture-5ed3e947 --timerange 20200301-20200401 --no-color --startup-candle 1440
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy DemaCrossStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DemaCrossStrategy-f77e5dfc --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy DemaCrossStrategy --strategy-path user_data/profile_bias_strategies/DemaCrossStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy DemaCrossStrategy --strategy-path user_data/profile_bias_strategies/DemaCrossStrategy --timerange 20190101-20190401 --no-color
  ```
- `DevDsl2Approx`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy DevDsl2Approx --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/DevDsl2Approx --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DevDsl2Approx-f1627c83-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy DevDsl2Approx --strategy-path user_data/profile_bias_strategies/DevDsl2Approx-f1627c83 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy DevDsl2Approx --strategy-path user_data/profile_bias_strategies/DevDsl2Approx-f1627c83 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `Diamond`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Diamond --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Diamond-b639c243 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Diamond --strategy-path user_data/profile_bias_strategies/Diamond --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Diamond --strategy-path user_data/profile_bias_strategies/Diamond --timerange 20190101-20190401 --no-color
  ```
- `Divergences`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Divergences --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Divergences-adb58dfb --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Divergences --strategy-path user_data/profile_bias_strategies/Divergences --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Divergences --strategy-path user_data/profile_bias_strategies/Divergences --timerange 20190101-20190401 --no-color
  ```
- `DonchianBounce`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy DonchianBounce --strategy-path repos/webclinic017_strategies-freqtrade-/archived --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DonchianBounce --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy DonchianBounce --strategy-path user_data/profile_bias_strategies/DonchianBounce-9e62325a --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy DonchianBounce --strategy-path user_data/profile_bias_strategies/DonchianBounce-9e62325a --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `DonchianBreakoutStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy DonchianBreakoutStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/DonchianBreakoutStrategy-184224cc --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy E0V1E --strategy-path repos/TheoBrigitte_freqtrade/strategies/e0v1e --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1E-35b73da0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E --strategy-path user_data/profile_bias_strategies/E0V1E --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E --strategy-path user_data/profile_bias_strategies/E0V1E --timerange 20190101-20190401 --no-color
  ```
- `E0V1E2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy E0V1E2 --strategy-path repos/TheoBrigitte_freqtrade/strategies/e0v1e --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1E2-b64d1b35 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E2 --strategy-path user_data/profile_bias_strategies/E0V1E2 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E2 --strategy-path user_data/profile_bias_strategies/E0V1E2 --timerange 20190101-20190401 --no-color
  ```
- `E0V1EN`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy E0V1EN --strategy-path repos/eovie_freqtrade_strs/binance/dry_run --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1EN-dc02ef88 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1EN --strategy-path user_data/profile_bias_strategies/E0V1EN --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1EN --strategy-path user_data/profile_bias_strategies/E0V1EN --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `E0V1E_3`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy E0V1E_3 --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/e0v1e --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1E_3-5c053f76-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_3 --strategy-path user_data/profile_bias_strategies/E0V1E_3-5c053f76 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_3 --strategy-path user_data/profile_bias_strategies/E0V1E_3-5c053f76 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `E0V1E_DCA3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy E0V1E_DCA3 --strategy-path repos/TheoBrigitte_freqtrade/strategies/e0v1e --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1E_DCA3-ab4c346a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_DCA3 --strategy-path user_data/profile_bias_strategies/E0V1E_DCA3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_DCA3 --strategy-path user_data/profile_bias_strategies/E0V1E_DCA3 --timerange 20190101-20190401 --no-color
  ```
- `E0V1E_Shorts`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy E0V1E_Shorts --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/e0v1e --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1E_Shorts-75162add-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy E0V1E_Shorts --strategy-path user_data/profile_bias_strategies/E0V1E_Shorts-75162add --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy E0V1E_Shorts --strategy-path user_data/profile_bias_strategies/E0V1E_Shorts-75162add --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `E0V1E_ewo`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy E0V1E_ewo --strategy-path repos/TheoBrigitte_freqtrade/strategies/e0v1e --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1E_ewo-689358af --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_ewo --strategy-path user_data/profile_bias_strategies/E0V1E_ewo --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_ewo --strategy-path user_data/profile_bias_strategies/E0V1E_ewo --timerange 20190101-20190401 --no-color
  ```
- `E0V1E_protections`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy E0V1E_protections --strategy-path repos/TheoBrigitte_freqtrade/strategies/e0v1e --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1E_protections-add87501 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_protections --strategy-path user_data/profile_bias_strategies/E0V1E_protections --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_protections --strategy-path user_data/profile_bias_strategies/E0V1E_protections --timerange 20190101-20190401 --no-color
  ```
- `E0V1E_strs`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy E0V1E_strs --strategy-path repos/TheoBrigitte_freqtrade/strategies/e0v1e --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/E0V1E_strs-d8807a22 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_strs --strategy-path user_data/profile_bias_strategies/E0V1E_strs --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy E0V1E_strs --strategy-path user_data/profile_bias_strategies/E0V1E_strs --timerange 20190101-20190401 --no-color
  ```
- `EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Picasso --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March-a6438d1f-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March --strategy-path user_data/profile_bias_strategies/EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March-a6438d1f --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March --strategy-path user_data/profile_bias_strategies/EDTMA_Long_Short_prot_CE_1h_3Lev_3mt_March-a6438d1f --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336
  ```
- `EI3v2_tag_cofi_green`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EI3v2_tag_cofi_green --strategy-path repos/MMR-19_freqtrade-strategies/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EI3v2_tag_cofi_green-c37315b6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EI3v2_tag_cofi_green --strategy-path user_data/profile_bias_strategies/EI3v2_tag_cofi_green --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EI3v2_tag_cofi_green --strategy-path user_data/profile_bias_strategies/EI3v2_tag_cofi_green --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `EMA50`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMA50 --strategy-path repos/davidzr_freqtrade-strategies/strategies/EMA50 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMA50-07c89e5c --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA50 --strategy-path user_data/profile_bias_strategies/EMA50 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA50 --strategy-path user_data/profile_bias_strategies/EMA50 --timerange 20190101-20190401 --no-color
  ```
- `EMA520015_V17`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMA520015_V17 --strategy-path repos/davidzr_freqtrade-strategies/strategies/EMA520015_V17 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMA520015_V17-94b0e424 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA520015_V17 --strategy-path user_data/profile_bias_strategies/EMA520015_V17 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA520015_V17 --strategy-path user_data/profile_bias_strategies/EMA520015_V17 --timerange 20190101-20190401 --no-color
  ```
- `EMABBRSI`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/EMABBRSI-override-f400cf1f3448.json --strategy EMABBRSI --strategy-path repos/davidzr_freqtrade-strategies/strategies/EMABBRSI --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMABBRSI --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/EMABBRSI_gate.json --strategy EMABBRSI --strategy-path user_data/profile_bias_strategies/EMABBRSI --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EMABBRSI_startup_24.json --strategy EMABBRSI --strategy-path user_data/profile_bias_strategies/EMABBRSI --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160 --timeframe 1h
  ```
- `EMABounce`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMABounce --strategy-path repos/webclinic017_strategies-freqtrade-/archived --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMABounce-ab0d2db4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMABounce --strategy-path user_data/profile_bias_strategies/EMABounce-ab0d2db4 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMABounce --strategy-path user_data/profile_bias_strategies/EMABounce-ab0d2db4 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `EMABreakout`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMABreakout --strategy-path repos/davidzr_freqtrade-strategies/strategies/EMABreakout --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMABreakout-50cd0f93 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMABreakout --strategy-path user_data/profile_bias_strategies/EMABreakout --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMABreakout --strategy-path user_data/profile_bias_strategies/EMABreakout --timerange 20190101-20190401 --no-color
  ```
- `EMACross`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMACross --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/EMACross" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMACross-b5f64897 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMACross --strategy-path user_data/profile_bias_strategies/EMACross-b5f64897 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMACross --strategy-path user_data/profile_bias_strategies/EMACross-b5f64897 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `EMAPriceCrossoverWithThreshold`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy EMAPriceCrossoverWithThreshold --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies-that-work --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMAPriceCrossoverWithThreshold --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMAPriceCrossoverWithThreshold --strategy-path user_data/profile_bias_strategies/EMAPriceCrossoverWithThreshold --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EMAPriceCrossoverWithThreshold_startup_24.json --strategy EMAPriceCrossoverWithThreshold --strategy-path user_data/profile_bias_strategies/EMAPriceCrossoverWithThreshold-b7ab2a0f --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `EMASkipPump`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMASkipPump --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMASkipPump-b4f9f8f8 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy EMA_CROSSOVER_STRATEGY --strategy-path repos/davidzr_freqtrade-strategies/strategies/EMA_CROSSOVER_STRATEGY --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EMA_CROSSOVER_STRATEGY-19dd135f --cache none
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
- `ETCG_Shorts`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy ETCG_Shorts --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/ETCG --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ETCG_Shorts-7a38345a-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy ETCG_Shorts --strategy-path user_data/profile_bias_strategies/ETCG_Shorts-7a38345a --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy ETCG_Shorts --strategy-path user_data/profile_bias_strategies/ETCG_Shorts-7a38345a --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `EXPERIMENTAL_STRATEGY`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/EXPERIMENTAL_STRATEGY-override-2c7527d808c6.json --strategy EXPERIMENTAL_STRATEGY --strategy-path repos/davidzr_freqtrade-strategies/strategies/EXPERIMENTAL_STRATEGY --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EXPERIMENTAL_STRATEGY --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/EXPERIMENTAL_STRATEGY_gate.json --strategy EXPERIMENTAL_STRATEGY --strategy-path user_data/profile_bias_strategies/EXPERIMENTAL_STRATEGY --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/EXPERIMENTAL_STRATEGY_startup_288.json --strategy EXPERIMENTAL_STRATEGY --strategy-path user_data/profile_bias_strategies/EXPERIMENTAL_STRATEGY --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `EasyInEasyOut`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy EasyInEasyOut --strategy-path repos/mikedigriz_freqtrade-strategy-mikedigriz/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EasyInEasyOut-fc725427 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EasyInEasyOut --strategy-path user_data/profile_bias_strategies/EasyInEasyOut --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EasyInEasyOut --strategy-path user_data/profile_bias_strategies/EasyInEasyOut --timerange 20190101-20190401 --no-color
  ```
- `ElliotV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV2-a93cb425 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV2 --strategy-path user_data/profile_bias_strategies/ElliotV2 --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV2 --strategy-path user_data/profile_bias_strategies/ElliotV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ElliotV4`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV4 --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV4 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV4-77e1bd66 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV4 --strategy-path user_data/profile_bias_strategies/ElliotV4 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV4 --strategy-path user_data/profile_bias_strategies/ElliotV4 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV531`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV531 --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV531 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV531-8e61212e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV531 --strategy-path user_data/profile_bias_strategies/ElliotV531 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV531 --strategy-path user_data/profile_bias_strategies/ElliotV531 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5HO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV5HO --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV5HO --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV5HO-3f1e7bde --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HO --strategy-path user_data/profile_bias_strategies/ElliotV5HO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HO --strategy-path user_data/profile_bias_strategies/ElliotV5HO --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5HOMod2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV5HOMod2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV5HOMod2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV5HOMod2-09ea5d90 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HOMod2 --strategy-path user_data/profile_bias_strategies/ElliotV5HOMod2 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HOMod2 --strategy-path user_data/profile_bias_strategies/ElliotV5HOMod2 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5HOMod3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV5HOMod3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV5HOMod3 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV5HOMod3-75950728 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HOMod3 --strategy-path user_data/profile_bias_strategies/ElliotV5HOMod3 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5HOMod3 --strategy-path user_data/profile_bias_strategies/ElliotV5HOMod3 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5_SMA`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV5_SMA --strategy-path repos/TheoBrigitte_freqtrade/strategies/ElliotV5_SMA --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV5_SMA-e9be798d --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5_SMA --strategy-path user_data/profile_bias_strategies/ElliotV5_SMA --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5_SMA --strategy-path user_data/profile_bias_strategies/ElliotV5_SMA --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `ElliotV7`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV7 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV7-012579cf --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV7 --strategy-path user_data/profile_bias_strategies/ElliotV7 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV7 --strategy-path user_data/profile_bias_strategies/ElliotV7 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV8HO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ElliotV8HO --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV8HO --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ElliotV8HO-afc8d86f --cache none
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
- `EmaCrossStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/EmaCrossStrategy-a8314e54-override-aa2053461232.json --strategy EmaCrossStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EmaCrossStrategy-a8314e54 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/EmaCrossStrategy-a8314e54_gate.json --strategy EmaCrossStrategy --strategy-path user_data/profile_bias_strategies/EmaCrossStrategy-a8314e54 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EmaCrossStrategy --strategy-path user_data/profile_bias_strategies/EmaCrossStrategy-a8314e54 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190 --timeframe 4h
  ```
- `EmaRibbonStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy EmaRibbonStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/EmaRibbonStrategy-4e3345d7 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EmaRibbonStrategy --strategy-path user_data/profile_bias_strategies/EmaRibbonStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EmaRibbonStrategy --strategy-path user_data/profile_bias_strategies/EmaRibbonStrategy --timerange 20190101-20190401 --no-color
  ```
- `FAdxSmaStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FAdxSmaStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path user_data/profile_bias_strategies/FAdxSmaStrategy --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FAdxSmaStrategy --strategy-path user_data/profile_bias_strategies/FAdxSmaStrategy --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FBB_DWT`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FBB_DWT --strategy-path repos/kemplail_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FBB_DWT-a8f9de02 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FBB_DWT --strategy-path user_data/profile_bias_strategies/FBB_DWT-a8f9de02 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FBB_DWT --strategy-path user_data/profile_bias_strategies/FBB_DWT-a8f9de02 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `FBB_KalmanSIMD`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy FBB_KalmanSIMD --strategy-path repos/webclinic017_strategies-freqtrade-/binanceus --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FBB_KalmanSIMD-a241c667 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FBB_KalmanSIMD --strategy-path user_data/profile_bias_strategies/FBB_KalmanSIMD-a241c667 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FBB_KalmanSIMD --strategy-path user_data/profile_bias_strategies/FBB_KalmanSIMD-a241c667 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `FFT`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FFT --strategy-path repos/kemplail_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FFT-94fa3fe9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FFT --strategy-path user_data/profile_bias_strategies/FFT-94fa3fe9 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FFT --strategy-path user_data/profile_bias_strategies/FFT-94fa3fe9 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `FLAGS`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy FLAGS --strategy-path repos/djienne_YOUTUBE_STRATEGIES_FREQTRADE/Experiences/FLAGS/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FLAGS-72416802 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy FLAGS --strategy-path user_data/profile_bias_strategies/FLAGS-72416802 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FLAGS --strategy-path user_data/profile_bias_strategies/FLAGS-72416802 --timerange 20200301-20200401 --no-color --startup-candle 24 48 168 336
  ```
- `FOttStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FOttStrategy --strategy-path user_data/profile_repairs --timerange 20200301-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FOttStrategy --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FOttStrategy --strategy-path user_data/profile_bias_strategies/FOttStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FOttStrategy --strategy-path user_data/profile_bias_strategies/FOttStrategy --timerange 20200301-20200401 --no-color
  ```
- `FRAYSTRAT`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FRAYSTRAT --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FRAYSTRAT-591d1d88 --cache none
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
- `FSupertrendStrategyBTC`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy FSupertrendStrategyBTC --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FSupertrendStrategyBTC-a0068dde-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FSupertrendStrategyBTC --strategy-path user_data/profile_bias_strategies/FSupertrendStrategyBTC-a0068dde --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FSupertrendStrategyBTC --strategy-path user_data/profile_bias_strategies/FSupertrendStrategyBTC-a0068dde --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `FTT_DWT_FBB_FUTURES`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FTT_DWT_FBB_FUTURES --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FTT_DWT_FBB_FUTURES --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FTT_DWT_FBB_FUTURES --strategy-path user_data/profile_bias_strategies/FTT_DWT_FBB_FUTURES --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FTT_DWT_FBB_FUTURES --strategy-path user_data/profile_bias_strategies/FTT_DWT_FBB_FUTURES --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `FUTURES`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy FUTURES --strategy-path repos/kemplail_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FUTURES-676b167a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy FUTURES --strategy-path user_data/profile_bias_strategies/FUTURES-676b167a --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy FUTURES --strategy-path user_data/profile_bias_strategies/FUTURES-676b167a --timerange 20200301-20200401 --no-color --startup-candle 1440
  ```
- `FVGChannel`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FVGChannel --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FVGChannel-f442e141 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FVGChannel --strategy-path user_data/profile_bias_strategies/FVGChannel --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FVGChannel --strategy-path user_data/profile_bias_strategies/FVGChannel --timerange 20190101-20190401 --no-color
  ```
- `Fakebuy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Fakebuy --strategy-path repos/davidzr_freqtrade-strategies/strategies/Fakebuy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Fakebuy-d1b272c1 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Fakebuy --strategy-path user_data/profile_bias_strategies/Fakebuy --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Fakebuy --strategy-path user_data/profile_bias_strategies/Fakebuy-d1b272c1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `FastSupertrendOpt`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy FastSupertrendOpt --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrendOpt-fc13211c-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FastSupertrendOpt --strategy-path user_data/profile_bias_strategies/FastSupertrendOpt-fc13211c --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FastSupertrendOpt --strategy-path user_data/profile_bias_strategies/FastSupertrendOpt-fc13211c --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336 720 2160
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
- `FenixTopProfit`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy FenixTopProfit --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Fenix --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FenixTopProfit-82637b6e-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy FenixTopProfit --strategy-path user_data/profile_bias_strategies/FenixTopProfit-82637b6e --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy FenixTopProfit --strategy-path user_data/profile_bias_strategies/FenixTopProfit-82637b6e --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336
  ```
- `Fibbo`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy Fibbo --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Ai --timerange 20200301-20210301 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Fibbo-558454bf-smoke_20200301_20210301-fca63e6f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy Fibbo --strategy-path user_data/profile_bias_strategies/Fibbo-558454bf --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy Fibbo --strategy-path user_data/profile_bias_strategies/Fibbo-558454bf --timerange 20200301-20200601 --no-color --startup-candle 96 192 672 1344
  ```
- `FibonacciEMATrendStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy FibonacciEMATrendStrategy --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Fibbo --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FibonacciEMATrendStrategy-83084414-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy FibonacciEMATrendStrategy --strategy-path user_data/profile_bias_strategies/FibonacciEMATrendStrategy-83084414 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy FibonacciEMATrendStrategy --strategy-path user_data/profile_bias_strategies/FibonacciEMATrendStrategy-83084414 --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336
  ```
- `FisherHull`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy FisherHull --strategy-path repos/mikedigriz_freqtrade-strategy-mikedigriz/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FisherHull-40a72168 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FisherHull --strategy-path user_data/profile_bias_strategies/FisherHull --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FisherHull --strategy-path user_data/profile_bias_strategies/FisherHull --timerange 20190101-20190401 --no-color
  ```
- `FisherTransformStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy FisherTransformStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FisherTransformStrategy-496e0ef8 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FisherTransformStrategy --strategy-path user_data/profile_bias_strategies/FisherTransformStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FisherTransformStrategy --strategy-path user_data/profile_bias_strategies/FisherTransformStrategy --timerange 20190101-20190401 --no-color
  ```
- `FiveMinCrossAbove`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FiveMinCrossAbove --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FiveMinCrossAbove-798a1782 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FiveMinCrossAbove --strategy-path user_data/profile_bias_strategies/FiveMinCrossAbove --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FiveMinCrossAbove --strategy-path user_data/profile_bias_strategies/FiveMinCrossAbove --timerange 20190101-20190401 --no-color
  ```
- `FlawlessVictory`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy FlawlessVictory --strategy-path repos/seannowotny_FlawlessVictoryPort/user_data/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FlawlessVictory-16bcd567 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FlawlessVictory --strategy-path user_data/profile_bias_strategies/FlawlessVictory --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FlawlessVictory --strategy-path user_data/profile_bias_strategies/FlawlessVictory --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `ForexSignal`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ForexSignal --strategy-path repos/davidzr_freqtrade-strategies/strategies/ForexSignal --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ForexSignal-00154db2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ForexSignal --strategy-path user_data/profile_bias_strategies/ForexSignal --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ForexSignal --strategy-path user_data/profile_bias_strategies/ForexSignal --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `FrayStratBTC`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FrayStratBTC --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FrayStratBTC-44376f16 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrayStratBTC --strategy-path user_data/profile_bias_strategies/FrayStratBTC --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrayStratBTC --strategy-path user_data/profile_bias_strategies/FrayStratBTC --timerange 20190101-20190401 --no-color
  ```
- `Freqtrade_backtest_validation_freqtrade1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Freqtrade_backtest_validation_freqtrade1 --strategy-path repos/TheoBrigitte_freqtrade/strategies/berlinguyinca/1h --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Freqtrade_backtest_validation_freqtrade1-7894fd71 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Freqtrade_backtest_validation_freqtrade1 --strategy-path user_data/profile_bias_strategies/Freqtrade_backtest_validation_freqtrade1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Freqtrade_backtest_validation_freqtrade1 --strategy-path user_data/profile_bias_strategies/Freqtrade_backtest_validation_freqtrade1 --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM115mStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FrostAuraM115mStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FrostAuraM115mStrategy-9a44acc1 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM115mStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM115mStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM115mStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM115mStrategy --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM11hStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FrostAuraM11hStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FrostAuraM11hStrategy-9b2c0282 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM11hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM11hStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM11hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM11hStrategy --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM21hStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FrostAuraM21hStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FrostAuraM21hStrategy-15995b94 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM21hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM21hStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM21hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM21hStrategy --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM315mStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FrostAuraM315mStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FrostAuraM315mStrategy-4bfcca28 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM315mStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM315mStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM315mStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM315mStrategy --timerange 20190101-20190401 --no-color
  ```
- `FrostAuraM31hStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy FrostAuraM31hStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FrostAuraM31hStrategy-15a97e50 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM31hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM31hStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FrostAuraM31hStrategy --strategy-path user_data/profile_bias_strategies/FrostAuraM31hStrategy --timerange 20190101-20190401 --no-color
  ```
- `GKD_Baseline`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy GKD_Baseline --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GKD_Baseline-3a0dd663 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_Baseline --strategy-path user_data/profile_bias_strategies/GKD_Baseline --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_Baseline --strategy-path user_data/profile_bias_strategies/GKD_Baseline --timerange 20190101-20190401 --no-color
  ```
- `GKD_BaselineAllMAs`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy GKD_BaselineAllMAs --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GKD_BaselineAllMAs-d132f795 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_BaselineAllMAs --strategy-path user_data/profile_bias_strategies/GKD_BaselineAllMAs --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_BaselineAllMAs --strategy-path user_data/profile_bias_strategies/GKD_BaselineAllMAs --timerange 20190101-20190401 --no-color
  ```
- `GKD_FisherTransformMTF`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy GKD_FisherTransformMTF --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GKD_FisherTransformMTF-dba7d6d9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/GKD_FisherTransformMTF_gate.json --strategy GKD_FisherTransformMTF --strategy-path user_data/profile_bias_strategies/GKD_FisherTransformMTF --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_FisherTransformMTF --strategy-path user_data/profile_bias_strategies/GKD_FisherTransformMTF --timerange 20190101-20190401 --no-color
  ```
- `GKD_HurstExponent`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy GKD_HurstExponent --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GKD_HurstExponent-48f852cd --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_HurstExponent --strategy-path user_data/profile_bias_strategies/GKD_HurstExponent --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_HurstExponent --strategy-path user_data/profile_bias_strategies/GKD_HurstExponent --timerange 20190101-20190401 --no-color
  ```
- `GKD_PFE`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy GKD_PFE --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GKD_PFE-3611d4c1 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_PFE --strategy-path user_data/profile_bias_strategies/GKD_PFE --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GKD_PFE --strategy-path user_data/profile_bias_strategies/GKD_PFE --timerange 20190101-20190401 --no-color
  ```
- `GPTREV`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy GPTREV --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GPTREV-7fba7b92 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GPTREV --strategy-path user_data/profile_bias_strategies/GPTREV --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GPTREV --strategy-path user_data/profile_bias_strategies/GPTREV --timerange 20190101-20190401 --no-color
  ```
- `GRIDDMIPRICEStrategyFutureV5Long`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy GRIDDMIPRICEStrategyFutureV5Long --strategy-path repos/LazyPigPig_freqtrade-grid/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GRIDDMIPRICEStrategyFutureV5Long-93a155ed --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy GRIDDMIPRICEStrategyFutureV5Long --strategy-path user_data/profile_bias_strategies/GRIDDMIPRICEStrategyFutureV5Long-93a155ed --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/GRIDDMIPRICEStrategyFutureV5Long_startup_1440.json --strategy GRIDDMIPRICEStrategyFutureV5Long --strategy-path user_data/profile_bias_strategies/GRIDDMIPRICEStrategyFutureV5Long-93a155ed --timerange 20200301-20200401 --no-color --startup-candle 1440
  ```
- `GRIDDMIPRICEStrategyFutureV5Short`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy GRIDDMIPRICEStrategyFutureV5Short --strategy-path repos/LazyPigPig_freqtrade-grid/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GRIDDMIPRICEStrategyFutureV5Short-0a37b705 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy GRIDDMIPRICEStrategyFutureV5Short --strategy-path user_data/profile_bias_strategies/GRIDDMIPRICEStrategyFutureV5Short-0a37b705 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/GRIDDMIPRICEStrategyFutureV5Short_startup_6.json --strategy GRIDDMIPRICEStrategyFutureV5Short --strategy-path user_data/profile_bias_strategies/GRIDDMIPRICEStrategyFutureV5Short-0a37b705 --timerange 20200301-20200401 --no-color --startup-candle 6 12 42 84
  ```
- `GRIDDMIPRICEStrategySpot`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy GRIDDMIPRICEStrategySpot --strategy-path repos/LazyPigPig_freqtrade-grid/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GRIDDMIPRICEStrategySpot-bfcd5e8a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy GRIDDMIPRICEStrategySpot --strategy-path user_data/profile_bias_strategies/GRIDDMIPRICEStrategySpot-bfcd5e8a --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/GRIDDMIPRICEStrategySpot_startup_1440.json --strategy GRIDDMIPRICEStrategySpot --strategy-path user_data/profile_bias_strategies/GRIDDMIPRICEStrategySpot-bfcd5e8a --timerange 20200301-20200401 --no-color --startup-candle 1440
  ```
- `GnF_V2`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy GnF_V2 --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/remiotore --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GnF_V2-0f3ac6fa-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy GnF_V2 --strategy-path user_data/profile_bias_strategies/GnF_V2-0f3ac6fa --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/GnF_V2_startup_24.json --strategy GnF_V2 --strategy-path user_data/profile_bias_strategies/GnF_V2-0f3ac6fa --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336
  ```
- `GodCard`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy GodCard --strategy-path repos/davidzr_freqtrade-strategies/strategies/GodCard --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GodCard-e992df91 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GodCard --strategy-path user_data/profile_bias_strategies/GodCard --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GodCard --strategy-path user_data/profile_bias_strategies/GodCard --timerange 20190101-20190401 --no-color
  ```
- `GoldenCrossStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy GoldenCrossStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/GoldenCrossStrategy-6a5ef5e3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy GoldenCrossStrategy --strategy-path user_data/profile_bias_strategies/GoldenCrossStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy GoldenCrossStrategy --strategy-path user_data/profile_bias_strategies/GoldenCrossStrategy --timerange 20190101-20190401 --no-color
  ```
- `Gumbo1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Gumbo1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Gumbo1-d72ec524 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Gumbo1 --strategy-path user_data/profile_bias_strategies/Gumbo1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Gumbo1 --strategy-path user_data/profile_bias_strategies/Gumbo1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `HEAD_SHOULDER`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy HEAD_SHOULDER --strategy-path repos/djienne_YOUTUBE_STRATEGIES_FREQTRADE/Experiences/HEAD_SHOULDER/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HEAD_SHOULDER-3272caf5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy HEAD_SHOULDER --strategy-path user_data/profile_bias_strategies/HEAD_SHOULDER-3272caf5 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy HEAD_SHOULDER --strategy-path user_data/profile_bias_strategies/HEAD_SHOULDER-3272caf5 --timerange 20200301-20200401 --no-color --startup-candle 96 192 672 1344
  ```
- `Hacklemore`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy Hacklemore --strategy-path repos/werkkrew_freqtrade-strategies/strategies/archived --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Hacklemore --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Hacklemore_gate.json --strategy Hacklemore --strategy-path user_data/profile_bias_strategies/Hacklemore --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemore --strategy-path user_data/profile_bias_strategies/Hacklemore --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Hacklemore2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Hacklemore2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/Hacklemore2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Hacklemore2-25466732 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Hacklemore2_gate.json --strategy Hacklemore2 --strategy-path user_data/profile_bias_strategies/Hacklemore2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemore2 --strategy-path user_data/profile_bias_strategies/Hacklemore2 --timerange 20190101-20190401 --no-color
  ```
- `Hacklemore3`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Hacklemore3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/Hacklemore3 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Hacklemore3-ec775e72-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Hacklemore3_gate.json --strategy Hacklemore3 --strategy-path user_data/profile_bias_strategies/Hacklemore3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemore3 --strategy-path user_data/profile_bias_strategies/Hacklemore3 --timerange 20190101-20190401 --no-color
  ```
- `Hacklemost`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Hacklemost --strategy-path repos/werkkrew_freqtrade-strategies/strategies/archived --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Hacklemost-f578e820 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemost --strategy-path user_data/profile_bias_strategies/Hacklemost --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hacklemost --strategy-path user_data/profile_bias_strategies/Hacklemost --timerange 20190101-20190401 --no-color
  ```
- `Hammer`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Hammer --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/Hammer" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Hammer-c157cbf6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Hammer --strategy-path user_data/profile_bias_strategies/Hammer-c157cbf6 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Hammer --strategy-path user_data/profile_bias_strategies/Hammer-c157cbf6 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `HansenSmaOffsetV1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy HansenSmaOffsetV1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HansenSmaOffsetV1-d633da96 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HansenSmaOffsetV1 --strategy-path user_data/profile_bias_strategies/HansenSmaOffsetV1 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HansenSmaOffsetV1 --strategy-path user_data/profile_bias_strategies/HansenSmaOffsetV1 --timerange 20190101-20190401 --no-color
  ```
- `HedgeAdaptiveRegimeStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy HedgeAdaptiveRegimeStrategy --strategy-path repair/patched/repos/XXA222_HPRL/config_examples/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HedgeAdaptiveRegimeStrategy-abda3016-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy HedgeAdaptiveRegimeStrategy --strategy-path user_data/profile_bias_strategies/HedgeAdaptiveRegimeStrategy-abda3016 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy HedgeAdaptiveRegimeStrategy --strategy-path user_data/profile_bias_strategies/HedgeAdaptiveRegimeStrategy-abda3016 --timerange 20200301-20200601 --no-color --startup-candle 1440
  ```
- `HeikinAshiStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy HeikinAshiStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HeikinAshiStrategy-97b9bc04 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HeikinAshiStrategy --strategy-path user_data/profile_bias_strategies/HeikinAshiStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HeikinAshiStrategy --strategy-path user_data/profile_bias_strategies/HeikinAshiStrategy --timerange 20190101-20190401 --no-color
  ```
- `HighFreqDemo`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy HighFreqDemo --strategy-path repos/Kureshi25_cryptobot/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HighFreqDemo-006fcf90 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy HighFreqDemo --strategy-path user_data/profile_bias_strategies/HighFreqDemo-006fcf90 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy HighFreqDemo --strategy-path user_data/profile_bias_strategies/HighFreqDemo-006fcf90 --timerange 20200301-20200401 --no-color --startup-candle 1440
  ```
- `HigherHighStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy HigherHighStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HigherHighStrategy-f85df8fe --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HigherHighStrategy --strategy-path user_data/profile_bias_strategies/HigherHighStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HigherHighStrategy --strategy-path user_data/profile_bias_strategies/HigherHighStrategy --timerange 20190101-20190401 --no-color
  ```
- `HilbertSineWave`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy HilbertSineWave --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HilbertSineWave-b856be2d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HilbertSineWave --strategy-path user_data/profile_bias_strategies/HilbertSineWave --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HilbertSineWave --strategy-path user_data/profile_bias_strategies/HilbertSineWave --timerange 20190101-20190401 --no-color
  ```
- `HourBasedStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy HourBasedStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HourBasedStrategy-f0bf90ca --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HourBasedStrategy --strategy-path user_data/profile_bias_strategies/HourBasedStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HourBasedStrategy --strategy-path user_data/profile_bias_strategies/HourBasedStrategy --timerange 20190101-20190401 --no-color
  ```
- `HourBasedStrategy_5m`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy HourBasedStrategy_5m --strategy-path repos/eovie_freqtrade_strs/binance/Archive --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/HourBasedStrategy_5m-1aaa006f-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HourBasedStrategy_5m --strategy-path user_data/profile_bias_strategies/HourBasedStrategy_5m --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/HourBasedStrategy_5m_startup_288.json --strategy HourBasedStrategy_5m --strategy-path user_data/profile_bias_strategies/HourBasedStrategy_5m --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `INSIDEUP`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy INSIDEUP --strategy-path repos/davidzr_freqtrade-strategies/strategies/INSIDEUP --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/INSIDEUP-dc5f3886 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/INSIDEUP_gate.json --strategy INSIDEUP --strategy-path user_data/profile_bias_strategies/INSIDEUP --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy INSIDEUP --strategy-path user_data/profile_bias_strategies/INSIDEUP --timerange 20190101-20190401 --no-color
  ```
- `Ichess`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Ichess --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichess-d1ad6a71 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichess --strategy-path user_data/profile_bias_strategies/Ichess --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichess --strategy-path user_data/profile_bias_strategies/Ichess --timerange 20190101-20190401 --no-color
  ```
- `Ichi`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Ichi --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichi-252e3d9b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichi --strategy-path user_data/profile_bias_strategies/Ichi --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Ichi_startup_96.json --strategy Ichi --strategy-path user_data/profile_bias_strategies/Ichi-252e3d9b --timerange 20200301-20200601 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `Ichimoku`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Ichimoku --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichimoku-91a3635e --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku --strategy-path user_data/profile_bias_strategies/Ichimoku --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku --strategy-path user_data/profile_bias_strategies/Ichimoku --timerange 20190101-20190401 --no-color
  ```
- `IchimokuCloudBreakoutStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy IchimokuCloudBreakoutStrategy --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/ichiv1_plus --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/IchimokuCloudBreakoutStrategy-8a53a90c-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy IchimokuCloudBreakoutStrategy --strategy-path user_data/profile_bias_strategies/IchimokuCloudBreakoutStrategy-8a53a90c --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy IchimokuCloudBreakoutStrategy --strategy-path user_data/profile_bias_strategies/IchimokuCloudBreakoutStrategy-8a53a90c --timerange 20200301-20200601 --no-color --startup-candle 6 12 42 84
  ```
- `IchimokuCloudStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy IchimokuCloudStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/IchimokuCloudStrategy-eede6bf0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy IchimokuCloudStrategy --strategy-path user_data/profile_bias_strategies/IchimokuCloudStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy IchimokuCloudStrategy --strategy-path user_data/profile_bias_strategies/IchimokuCloudStrategy-eede6bf0 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `IchimokuSimpleStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy IchimokuSimpleStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/IchimokuSimpleStrategy-c36eb299 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Ichimoku_v31 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichimoku_v31-7208d46d --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Ichimoku_v37 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Ichimoku_v37-18e3ba92 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v37 --strategy-path user_data/profile_bias_strategies/Ichimoku_v37 --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v37 --strategy-path user_data/profile_bias_strategies/Ichimoku_v37 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540
  ```
- `ImpulseV1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ImpulseV1 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/ImpulseV1" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ImpulseV1-506c42b6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ImpulseV1 --strategy-path user_data/profile_bias_strategies/ImpulseV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ImpulseV1 --strategy-path user_data/profile_bias_strategies/ImpulseV1 --timerange 20190101-20190401 --no-color
  ```
- `InformativeSample`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy InformativeSample --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/InformativeSample-56ecc655 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy InformativeSample --strategy-path user_data/profile_bias_strategies/InformativeSample --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy InformativeSample --strategy-path user_data/profile_bias_strategies/InformativeSample --timerange 20190101-20190401 --no-color
  ```
- `Inverse`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Inverse --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Inverse-bfe272f9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Inverse --strategy-path user_data/profile_bias_strategies/Inverse --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Inverse --strategy-path user_data/profile_bias_strategies/Inverse --timerange 20190101-20190401 --no-color
  ```
- `InverseV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy InverseV2 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/InverseV2-cc2ff292 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy InverseV2 --strategy-path user_data/profile_bias_strategies/InverseV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy InverseV2 --strategy-path user_data/profile_bias_strategies/InverseV2 --timerange 20190101-20190401 --no-color
  ```
- `JuicyTrend`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy JuicyTrend --strategy-path repos/TheoBrigitte_freqtrade/strategies/juicy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/JuicyTrend-d2cb2ca2 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy KAMACCIRSI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/KAMACCIRSI-38dc74b2 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI --strategy-path user_data/profile_bias_strategies/KAMACCIRSI --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI --strategy-path user_data/profile_bias_strategies/KAMACCIRSI --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `KAMACCIRSI_new`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy KAMACCIRSI_new --strategy-path repos/werkkrew_freqtrade-strategies/strategies/archived --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/KAMACCIRSI_new-0443f98b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI_new --strategy-path user_data/profile_bias_strategies/KAMACCIRSI_new --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI_new --strategy-path user_data/profile_bias_strategies/KAMACCIRSI_new --timerange 20190101-20190401 --no-color
  ```
- `KC_BB`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy KC_BB --strategy-path repos/davidzr_freqtrade-strategies/strategies/KC_BB --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/KC_BB-2f26e143 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KC_BB --strategy-path user_data/profile_bias_strategies/KC_BB --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KC_BB --strategy-path user_data/profile_bias_strategies/KC_BB --timerange 20190101-20190401 --no-color
  ```
- `KamaFama_2_20250115`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy KamaFama_2_20250115 --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/KamaFama --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/KamaFama_2_20250115-5ad5321a-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy KamaFama_2_20250115 --strategy-path user_data/profile_bias_strategies/KamaFama_2_20250115-5ad5321a --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy KamaFama_2_20250115 --strategy-path user_data/profile_bias_strategies/KamaFama_2_20250115-5ad5321a --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `KeltnerBounce`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy KeltnerBounce --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/__KeltnerBounce" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/KeltnerBounce-63c48d3d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KeltnerBounce --strategy-path user_data/profile_bias_strategies/KeltnerBounce-63c48d3d --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KeltnerBounce --strategy-path user_data/profile_bias_strategies/KeltnerBounce-63c48d3d --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032 --timeframe 5m
  ```
- `KeltnerBounce_Shorts`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy KeltnerBounce_Shorts --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Bounce --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/KeltnerBounce_Shorts-008d9c62-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy KeltnerBounce_Shorts --strategy-path user_data/profile_bias_strategies/KeltnerBounce_Shorts-008d9c62 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy KeltnerBounce_Shorts --strategy-path user_data/profile_bias_strategies/KeltnerBounce_Shorts-008d9c62 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `KeltnerChannelStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy KeltnerChannelStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/KeltnerChannelStrategy-aef954af --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KeltnerChannelStrategy --strategy-path user_data/profile_bias_strategies/KeltnerChannelStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KeltnerChannelStrategy --strategy-path user_data/profile_bias_strategies/KeltnerChannelStrategy --timerange 20190101-20190401 --no-color
  ```
- `KeltnerChannels`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy KeltnerChannels --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/KeltnerChannels" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/KeltnerChannels-1628032a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KeltnerChannels --strategy-path user_data/profile_bias_strategies/KeltnerChannels-1628032a --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KeltnerChannels --strategy-path user_data/profile_bias_strategies/KeltnerChannels-1628032a --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Lateralus`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Lateralus --strategy-path repos/werkkrew_freqtrade-strategies/strategies/archived --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Lateralus-31a5ed07-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Lateralus_gate.json --strategy Lateralus --strategy-path user_data/profile_bias_strategies/Lateralus --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Lateralus --strategy-path user_data/profile_bias_strategies/Lateralus --timerange 20190101-20190401 --no-color
  ```
- `LeoStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy LeoStrategy --strategy-path repos/kemplail_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/LeoStrategy-a4770535 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy LeoStrategy --strategy-path user_data/profile_bias_strategies/LeoStrategy-a4770535 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy LeoStrategy --strategy-path user_data/profile_bias_strategies/LeoStrategy-a4770535 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `LinearRegressionStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy LinearRegressionStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/LinearRegressionStrategy-1c3f226f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy LinearRegressionStrategy --strategy-path user_data/profile_bias_strategies/LinearRegressionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy LinearRegressionStrategy --strategy-path user_data/profile_bias_strategies/LinearRegressionStrategy --timerange 20190101-20190401 --no-color
  ```
- `Low_BB`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Low_BB --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Low_BB-36ee484b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Low_BB_gate.json --strategy Low_BB --strategy-path user_data/profile_bias_strategies/Low_BB --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Low_BB --strategy-path user_data/profile_bias_strategies/Low_BB --timerange 20190101-20190401 --no-color
  ```
- `LuxOSC`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy LuxOSC --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/LuxOSC-1a3b1a68 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy LuxOSC --strategy-path user_data/profile_bias_strategies/LuxOSC --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy LuxOSC --strategy-path user_data/profile_bias_strategies/LuxOSC --timerange 20190101-20190401 --no-color
  ```
- `MAC`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MAC --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MAC-1f6368e6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MAC --strategy-path user_data/profile_bias_strategies/MAC --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MAC --strategy-path user_data/profile_bias_strategies/MAC --timerange 20190101-20190401 --no-color
  ```
- `MACD003`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACD003 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/__MACD003" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACD003-5def5884 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD003 --strategy-path user_data/profile_bias_strategies/MACD003-5def5884 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MACD003_startup_288.json --strategy MACD003 --strategy-path user_data/profile_bias_strategies/MACD003-5def5884 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
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
- `MACDCross`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDCross --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/__MACDCross" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDCross-c19524f6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDCross --strategy-path user_data/profile_bias_strategies/MACDCross-c19524f6 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDCross --strategy-path user_data/profile_bias_strategies/MACDCross-c19524f6 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategy-79bd402e --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategy --strategy-path user_data/profile_bias_strategies/MACDStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MACDStrategy_startup_288.json --strategy MACDStrategy --strategy-path user_data/profile_bias_strategies/MACDStrategy-79bd402e --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MACDStrategyADA`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategyADA --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategyADA-0cde35d1 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyADA --strategy-path user_data/profile_bias_strategies/MACDStrategyADA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyADA --strategy-path user_data/profile_bias_strategies/MACDStrategyADA --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyAVAX`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategyAVAX --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategyAVAX-33d55a2a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyAVAX --strategy-path user_data/profile_bias_strategies/MACDStrategyAVAX --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyAVAX --strategy-path user_data/profile_bias_strategies/MACDStrategyAVAX --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyBTC`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategyBTC --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategyBTC-b69154e4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyBTC --strategy-path user_data/profile_bias_strategies/MACDStrategyBTC --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyBTC --strategy-path user_data/profile_bias_strategies/MACDStrategyBTC --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyENJ`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategyENJ --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategyENJ-65cf3e26 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyENJ --strategy-path user_data/profile_bias_strategies/MACDStrategyENJ --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyENJ --strategy-path user_data/profile_bias_strategies/MACDStrategyENJ --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyETC`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategyETC --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategyETC-d1d0ba70 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyETC --strategy-path user_data/profile_bias_strategies/MACDStrategyETC --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyETC --strategy-path user_data/profile_bias_strategies/MACDStrategyETC --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategySOL`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategySOL --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategySOL-4e10aebc --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategySOL --strategy-path user_data/profile_bias_strategies/MACDStrategySOL --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategySOL --strategy-path user_data/profile_bias_strategies/MACDStrategySOL --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategyXRP`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategyXRP --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategyXRP-8c63d974 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyXRP --strategy-path user_data/profile_bias_strategies/MACDStrategyXRP --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategyXRP --strategy-path user_data/profile_bias_strategies/MACDStrategyXRP --timerange 20190101-20190401 --no-color
  ```
- `MACDStrategy_crossed`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDStrategy_crossed --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDStrategy_crossed-4427a4d5 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategy_crossed --strategy-path user_data/profile_bias_strategies/MACDStrategy_crossed --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategy_crossed --strategy-path user_data/profile_bias_strategies/MACDStrategy_crossed --timerange 20190101-20190401 --no-color
  ```
- `MACDTurn`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDTurn --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/__MACDTurn" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDTurn-e059bfc3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDTurn --strategy-path user_data/profile_bias_strategies/MACDTurn-e059bfc3 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDTurn --strategy-path user_data/profile_bias_strategies/MACDTurn-e059bfc3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MACDZeroCrossStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACDZeroCrossStrategy --strategy-path repos/ingpawat_freqtrade-strategy-with-backtest/strategy/MACDZeroCrossStrategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACDZeroCrossStrategy-18eb90f7 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDZeroCrossStrategy --strategy-path user_data/profile_bias_strategies/MACDZeroCrossStrategy --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDZeroCrossStrategy --strategy-path user_data/profile_bias_strategies/MACDZeroCrossStrategy --timerange 20190101-20190401 --no-color
  ```
- `MACD_EMA`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACD_EMA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACD_EMA-ebd8acf7 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_EMA --strategy-path user_data/profile_bias_strategies/MACD_EMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_EMA --strategy-path user_data/profile_bias_strategies/MACD_EMA --timerange 20190101-20190401 --no-color
  ```
- `MACD_TRIPLE_MA`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACD_TRIPLE_MA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACD_TRIPLE_MA-56a72b4d --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRIPLE_MA --strategy-path user_data/profile_bias_strategies/MACD_TRIPLE_MA --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRIPLE_MA --strategy-path user_data/profile_bias_strategies/MACD_TRIPLE_MA --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MACD_TRI_EMA`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MACD_TRI_EMA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MACD_TRI_EMA-8f2fd8e3 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRI_EMA --strategy-path user_data/profile_bias_strategies/MACD_TRI_EMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRI_EMA --strategy-path user_data/profile_bias_strategies/MACD_TRI_EMA --timerange 20190101-20190401 --no-color
  ```
- `MADisplaceV3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MADisplaceV3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MADisplaceV3-1326c489 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MADisplaceV3 --strategy-path user_data/profile_bias_strategies/MADisplaceV3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MADisplaceV3 --strategy-path user_data/profile_bias_strategies/MADisplaceV3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MFI`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MFI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MFI-5705ffee --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MFI --strategy-path user_data/profile_bias_strategies/MFI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MFI --strategy-path user_data/profile_bias_strategies/MFI --timerange 20190101-20190401 --no-color
  ```
- `MFI2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MFI2 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/MFI2" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MFI2-9083ee50 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MFI2 --strategy-path user_data/profile_bias_strategies/MFI2-9083ee50 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MFI2 --strategy-path user_data/profile_bias_strategies/MFI2-9083ee50 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MFIRSICross`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MFIRSICross --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/_MFIRSICross" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MFIRSICross-00cbcde3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MFIRSICross --strategy-path user_data/profile_bias_strategies/MFIRSICross-00cbcde3 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MFIRSICross --strategy-path user_data/profile_bias_strategies/MFIRSICross-00cbcde3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MabStra`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MabStra --strategy-path repos/davidzr_freqtrade-strategies/strategies/mabStra --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MabStra-43fd2626 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MabStra --strategy-path user_data/profile_bias_strategies/MabStra --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MabStra_startup_6.json --strategy MabStra --strategy-path user_data/profile_bias_strategies/MabStra-43fd2626 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `MacdAdxStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy MacdAdxStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MacdAdxStrategy-c52df265 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdAdxStrategy --strategy-path user_data/profile_bias_strategies/MacdAdxStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdAdxStrategy --strategy-path user_data/profile_bias_strategies/MacdAdxStrategy --timerange 20190101-20190401 --no-color
  ```
- `MacdZeroCrossStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy MacdZeroCrossStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MacdZeroCrossStrategy-4830233c --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MarketChyperHyperStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MarketChyperHyperStrategy-d7bac38e --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MarketChyperHyperStrategy --strategy-path user_data/profile_bias_strategies/MarketChyperHyperStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MarketChyperHyperStrategy --strategy-path user_data/profile_bias_strategies/MarketChyperHyperStrategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Maro4hMacdSd`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Maro4hMacdSd --strategy-path repos/davidzr_freqtrade-strategies/strategies/Maro4hMacdSd --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Maro4hMacdSd-579080b7 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Maro4hMacdSd --strategy-path user_data/profile_bias_strategies/Maro4hMacdSd --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Maro4hMacdSd --strategy-path user_data/profile_bias_strategies/Maro4hMacdSd --timerange 20190101-20190401 --no-color
  ```
- `Martin`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Martin --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Martin-39d3a2e9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Martin --strategy-path user_data/profile_bias_strategies/Martin --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Martin --strategy-path user_data/profile_bias_strategies/Martin --timerange 20190101-20190401 --no-color
  ```
- `MeanReversionTrend`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy MeanReversionTrend --strategy-path repos/yeboster_liquidity-sweep-freqtrade/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MeanReversionTrend --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MeanReversionTrend --strategy-path user_data/profile_bias_strategies/MeanReversionTrend-9c6041b5 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MeanReversionTrend_startup_24.json --strategy MeanReversionTrend --strategy-path user_data/profile_bias_strategies/MeanReversionTrend-9c6041b5 --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `MiniLambo`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy MiniLambo --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MiniLambo-32df6766 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MiniLambo --strategy-path user_data/profile_bias_strategies/MiniLambo --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MiniLambo --strategy-path user_data/profile_bias_strategies/MiniLambo --timerange 20190101-20190401 --no-color
  ```
- `MiniLambo_TBS`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy MiniLambo_TBS --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MiniLambo_TBS --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MiniLambo_TBS --strategy-path user_data/profile_bias_strategies/MiniLambo_TBS-773406bb --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MiniLambo_TBS --strategy-path user_data/profile_bias_strategies/MiniLambo_TBS-773406bb --timerange 20200301-20200601 --no-color --startup-candle 1440 2880
  ```
- `Minmax`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Minmax --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Minmax-476cf2d9 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Minmax --strategy-path user_data/profile_bias_strategies/Minmax --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Minmax --strategy-path user_data/profile_bias_strategies/Minmax --timerange 20190101-20190401 --no-color
  ```
- `MomStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MomStrategy --strategy-path repos/davidzr_freqtrade-strategies/strategies/MomStrategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MomStrategy-63021af4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MomStrategy --strategy-path user_data/profile_bias_strategies/MomStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MomStrategy --strategy-path user_data/profile_bias_strategies/MomStrategy --timerange 20190101-20190401 --no-color
  ```
- `MomentumCCITrendStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy MomentumCCITrendStrategy --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/MomentumCCITrendStrategy --timerange 20200301-20200601 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MomentumCCITrendStrategy-f0099a2a-smoke_20200301_20200601-9c543975 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy MomentumCCITrendStrategy --strategy-path user_data/profile_bias_strategies/MomentumCCITrendStrategy-f0099a2a --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/MomentumCCITrendStrategy_startup_1.json --strategy MomentumCCITrendStrategy --strategy-path user_data/profile_bias_strategies/MomentumCCITrendStrategy-f0099a2a --timerange 20200301-20200601 --no-color --startup-candle 1 2 7 14
  ```
- `MomentumScoreStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy MomentumScoreStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MomentumScoreStrategy-81e52e71 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MomentumScoreStrategy --strategy-path user_data/profile_bias_strategies/MomentumScoreStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MomentumScoreStrategy --strategy-path user_data/profile_bias_strategies/MomentumScoreStrategy --timerange 20190101-20190401 --no-color
  ```
- `Momentumv2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Momentumv2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/Momentumv2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Momentumv2-a2ecd9e8 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Momentumv2 --strategy-path user_data/profile_bias_strategies/Momentumv2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Momentumv2 --strategy-path user_data/profile_bias_strategies/Momentumv2 --timerange 20190101-20190401 --no-color
  ```
- `MoneyFlowStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy MoneyFlowStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MoneyFlowStrategy-11170f24 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MoneyFlowStrategy --strategy-path user_data/profile_bias_strategies/MoneyFlowStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MoneyFlowStrategy --strategy-path user_data/profile_bias_strategies/MoneyFlowStrategy --timerange 20190101-20190401 --no-color
  ```
- `MontrealStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MontrealStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MontrealStrategy-1e851d26 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MontrealStrategy --strategy-path user_data/profile_bias_strategies/MontrealStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MontrealStrategy --strategy-path user_data/profile_bias_strategies/MontrealStrategy --timerange 20190101-20190401 --no-color
  ```
- `MultiActionZone`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy MultiActionZone --strategy-path repos/miwtoo_ft-action-zone/user_data/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiActionZone --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MultiActionZone-179b96b7_gate.json --strategy MultiActionZone --strategy-path user_data/profile_bias_strategies/MultiActionZone-179b96b7 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiActionZone --strategy-path user_data/profile_bias_strategies/MultiActionZone-179b96b7 --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190
  ```
- `MultiFactorConfluenceStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy MultiFactorConfluenceStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiFactorConfluenceStrategy-195fb188 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiFactorConfluenceStrategy --strategy-path user_data/profile_bias_strategies/MultiFactorConfluenceStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiFactorConfluenceStrategy --strategy-path user_data/profile_bias_strategies/MultiFactorConfluenceStrategy --timerange 20190101-20190401 --no-color
  ```
- `MultiMA_TSL`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MultiMA_TSL --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiMA_TSL-432f3842 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/MultiMA_TSL-432f3842_gate.json --strategy MultiMA_TSL --strategy-path user_data/profile_bias_strategies/MultiMA_TSL-432f3842 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL --strategy-path user_data/profile_bias_strategies/MultiMA_TSL --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MultiMA_TSL3b`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy MultiMA_TSL3b --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiMA_TSL3b-394a8370-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL3b --strategy-path user_data/profile_bias_strategies/MultiMA_TSL3b-394a8370 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL3b --strategy-path user_data/profile_bias_strategies/MultiMA_TSL3b-394a8370 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `MultiOffsetLamboV0`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy MultiOffsetLamboV0 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiOffsetLamboV0-0dfa7f19 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiOffsetLamboV0 --strategy-path user_data/profile_bias_strategies/MultiOffsetLamboV0 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiOffsetLamboV0 --strategy-path user_data/profile_bias_strategies/MultiOffsetLamboV0 --timerange 20190101-20190401 --no-color
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NASOSv5 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5-fdf79059 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NASOSv5_gate.json --strategy NASOSv5 --strategy-path user_data/profile_bias_strategies/NASOSv5 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5 --strategy-path user_data/profile_bias_strategies/NASOSv5 --timerange 20190101-20190401 --no-color
  ```
- `NASOSv5HO`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NASOSv5HO --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5HO --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5HO --strategy-path user_data/profile_bias_strategies/NASOSv5HO-4fa36018 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5HO --strategy-path user_data/profile_bias_strategies/NASOSv5HO-4fa36018 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `NASOSv5PD`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NASOSv5PD --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5PD --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5PD --strategy-path user_data/profile_bias_strategies/NASOSv5PD-ad088fe3 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5PD --strategy-path user_data/profile_bias_strategies/NASOSv5PD-ad088fe3 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `NASOSv5SL`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NASOSv5SL --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5SL --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5SL --strategy-path user_data/profile_bias_strategies/NASOSv5SL-15c5cded --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5SL --strategy-path user_data/profile_bias_strategies/NASOSv5SL-15c5cded --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `NASOSv5_antipump`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NASOSv5_antipump --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NASOSv5_antipump --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5_antipump --strategy-path user_data/profile_bias_strategies/NASOSv5_antipump-90e3cc66 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NASOSv5_antipump --strategy-path user_data/profile_bias_strategies/NASOSv5_antipump-90e3cc66 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
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
- `NDrop`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NDrop --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/NDrop" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NDrop-035a8156 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NDrop --strategy-path user_data/profile_bias_strategies/NDrop-035a8156 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NDrop --strategy-path user_data/profile_bias_strategies/NDrop-035a8156 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NEWTEST15m`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NEWTEST15m --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NEWTEST15m-27c783bc --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NEWTEST15m --strategy-path user_data/profile_bias_strategies/NEWTEST15m --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NEWTEST15m --strategy-path user_data/profile_bias_strategies/NEWTEST15m --timerange 20190101-20190401 --no-color
  ```
- `NFI46`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI46 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI46-38afdd57 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI46FrogZ --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI46FrogZ-00590e50 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46FrogZ --strategy-path user_data/profile_bias_strategies/NFI46FrogZ --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46FrogZ --strategy-path user_data/profile_bias_strategies/NFI46FrogZ --timerange 20190101-20190401 --no-color
  ```
- `NFI46Offset`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI46Offset --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI46Offset-5834ae71 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Offset --strategy-path user_data/profile_bias_strategies/NFI46Offset --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Offset --strategy-path user_data/profile_bias_strategies/NFI46Offset --timerange 20190101-20190401 --no-color
  ```
- `NFI46OffsetHOA1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI46OffsetHOA1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI46OffsetHOA1-91c94296 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46OffsetHOA1 --strategy-path user_data/profile_bias_strategies/NFI46OffsetHOA1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46OffsetHOA1 --strategy-path user_data/profile_bias_strategies/NFI46OffsetHOA1 --timerange 20190101-20190401 --no-color
  ```
- `NFI46Z`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI46Z --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI46Z-8a414576 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Z --strategy-path user_data/profile_bias_strategies/NFI46Z --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI46Z --strategy-path user_data/profile_bias_strategies/NFI46Z --timerange 20190101-20190401 --no-color
  ```
- `NFI47V2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI47V2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFI47V2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI47V2-415abd68 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI5MOHO --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI5MOHO-b6de4e08 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO --strategy-path user_data/profile_bias_strategies/NFI5MOHO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO --strategy-path user_data/profile_bias_strategies/NFI5MOHO --timerange 20190101-20190401 --no-color
  ```
- `NFI5MOHO2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI5MOHO2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFI5MOHO2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI5MOHO2-de424a53 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO2 --strategy-path user_data/profile_bias_strategies/NFI5MOHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO2 --strategy-path user_data/profile_bias_strategies/NFI5MOHO2 --timerange 20190101-20190401 --no-color
  ```
- `NFI5MOHO_WIP`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI5MOHO_WIP --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI5MOHO_WIP-25adadea --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP --timerange 20190101-20190401 --no-color
  ```
- `NFI5MOHO_WIP_1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI5MOHO_WIP_1 --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFI5MOHO_WIP_1 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI5MOHO_WIP_1-ecdff35f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP_1 --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP_1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP_1 --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP_1 --timerange 20190101-20190401 --no-color
  ```
- `NFI5MOHO_WIP_2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI5MOHO_WIP_2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFI5MOHO_WIP_2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI5MOHO_WIP_2-9551ae6f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP_2 --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP_2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI5MOHO_WIP_2 --strategy-path user_data/profile_bias_strategies/NFI5MOHO_WIP_2 --timerange 20190101-20190401 --no-color
  ```
- `NFI7MOHO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFI7MOHO --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFI7MOHO --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFI7MOHO-4963f506 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI7MOHO --strategy-path user_data/profile_bias_strategies/NFI7MOHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFI7MOHO --strategy-path user_data/profile_bias_strategies/NFI7MOHO --timerange 20190101-20190401 --no-color
  ```
- `NFINextMOHO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFINextMOHO --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFINextMOHO --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFINextMOHO-92310738 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMOHO --strategy-path user_data/profile_bias_strategies/NFINextMOHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMOHO --strategy-path user_data/profile_bias_strategies/NFINextMOHO --timerange 20190101-20190401 --no-color
  ```
- `NFINextMOHO2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFINextMOHO2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFINextMOHO2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFINextMOHO2-6491efe9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMOHO2 --strategy-path user_data/profile_bias_strategies/NFINextMOHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMOHO2 --strategy-path user_data/profile_bias_strategies/NFINextMOHO2 --timerange 20190101-20190401 --no-color
  ```
- `NFINextMultiOffsetAndHO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NFINextMultiOffsetAndHO --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFINextMultiOffsetAndHO --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFINextMultiOffsetAndHO-8d25b109 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMultiOffsetAndHO --strategy-path user_data/profile_bias_strategies/NFINextMultiOffsetAndHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMultiOffsetAndHO --strategy-path user_data/profile_bias_strategies/NFINextMultiOffsetAndHO --timerange 20190101-20190401 --no-color
  ```
- `NFINextMultiOffsetAndHO2`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy NFINextMultiOffsetAndHO2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/NFINextMultiOffsetAndHO2 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NFINextMultiOffsetAndHO2-9c883070 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMultiOffsetAndHO2 --strategy-path user_data/profile_bias_strategies/NFINextMultiOffsetAndHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NFINextMultiOffsetAndHO2 --strategy-path user_data/profile_bias_strategies/NFINextMultiOffsetAndHO2 --timerange 20190101-20190401 --no-color
  ```
- `NSeq`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NSeq --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/NSeq" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NSeq-b0a87061 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NSeq --strategy-path user_data/profile_bias_strategies/NSeq-b0a87061 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NSeq --strategy-path user_data/profile_bias_strategies/NSeq-b0a87061 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NWEv6_new`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NWEv6_new --strategy-path repos/anakein_beastbotXB/working --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NWEv6_new-3a4963e7 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NWEv6_new --strategy-path user_data/profile_bias_strategies/NWEv6_new --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NWEv6_new --strategy-path user_data/profile_bias_strategies/NWEv6_new --timerange 20190101-20190401 --no-color --startup-candle 480 960 3360
  ```
- `NormalizerStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NormalizerStrategy --strategy-path repos/davidzr_freqtrade-strategies/strategies/NormalizerStrategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NormalizerStrategy-8ddea525 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NormalizerStrategy --strategy-path user_data/profile_bias_strategies/NormalizerStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NormalizerStrategy --strategy-path user_data/profile_bias_strategies/NormalizerStrategy --timerange 20190101-20190401 --no-color
  ```
- `NormalizerStrategyHO2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NormalizerStrategyHO2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NormalizerStrategyHO2-db1d20f9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NormalizerStrategyHO2 --strategy-path user_data/profile_bias_strategies/NormalizerStrategyHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NormalizerStrategyHO2 --strategy-path user_data/profile_bias_strategies/NormalizerStrategyHO2 --timerange 20190101-20190401 --no-color
  ```
- `Nostalgia`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Nostalgia --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Nostalgia-ad35efae --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Nostalgia --strategy-path user_data/profile_bias_strategies/Nostalgia --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Nostalgia --strategy-path user_data/profile_bias_strategies/Nostalgia --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinity772martinsk3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinity772martinsk3 --strategy-path repair/patched/repos/TheoBrigitte_freqtrade/strategies/nfix --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinity772martinsk3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NostalgiaForInfinity772martinsk3_gate.json --strategy NostalgiaForInfinity772martinsk3 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinity772martinsk3 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinity772martinsk3 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinity772martinsk3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityNext772`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityNext772 --strategy-path repair/patched/repos/TheoBrigitte_freqtrade/sources/nfix --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNext772 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext772 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext772 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext772 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext772-8d6ca7f0 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityNextGen`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityNextGen --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNextGen-3c2dae5e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextGen --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextGen --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextGen --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextGen --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityNextGen_TSL`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityNextGen_TSL --strategy-path repos/davidzr_freqtrade-strategies/strategies/NostalgiaForInfinityNextGen_TSL --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNextGen_TSL-b5f4b310 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextGen_TSL --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextGen_TSL --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextGen_TSL --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextGen_TSL --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityNextV7155`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityNextV7155 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNextV7155 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextV7155 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextV7155 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNextV7155 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNextV7155-fd1e8353 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityNext_ChangeToTower_V6_Short`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy NostalgiaForInfinityNext_ChangeToTower_V6_Short --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/NostalgiaForInfinityNext_ChangeToTower --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNext_ChangeToTower_V6_Short-f39c2e96-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy NostalgiaForInfinityNext_ChangeToTower_V6_Short --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext_ChangeToTower_V6_Short-f39c2e96 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy NostalgiaForInfinityNext_ChangeToTower_V6_Short --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext_ChangeToTower_V6_Short-f39c2e96 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `NostalgiaForInfinityNext_maximizer`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NostalgiaForInfinityNext_maximizer --strategy-path repair/patched/repos/davidzr_freqtrade-strategies/strategies/NostalgiaForInfinityNext_maximizer --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityNext_maximizer --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext_maximizer --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext_maximizer --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityNext_maximizer --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityNext_maximizer-78e1c6b3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityV1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV1-ed100932 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV1 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV1 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV1 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV1 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV2-f3282564 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `NostalgiaForInfinityV3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV3-1319d6e9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV3 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV3 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV3 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV4`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV4 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV4-522cd25a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV4 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV4 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV4 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV4HO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV4HO --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV4HO-bfa1fa35 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV4HO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV4HO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV4HO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV4HO --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV5`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV5 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV5-1f038111 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV5MultiOffsetAndHO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV5MultiOffsetAndHO-ef0e67dc --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5MultiOffsetAndHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5MultiOffsetAndHO --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV5MultiOffsetAndHO2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV5MultiOffsetAndHO2-aedfafde --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5MultiOffsetAndHO2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV5MultiOffsetAndHO2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV5MultiOffsetAndHO2 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV6`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV6 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV6-84e37cca --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV6 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV6 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV6 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV6 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV6HO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV6HO --strategy-path repos/davidzr_freqtrade-strategies/strategies/NostalgiaForInfinityV6HO --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV6HO-92ce7768 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV6HO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV6HO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV6HO --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV6HO --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV7`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV7 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV7-5a32c38a --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV7_SMA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV7_SMA-65c4e695 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_SMA --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_SMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV7_SMA --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV7_SMA --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV7_SMAv2_1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NostalgiaForInfinityV7_SMAv2_1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NostalgiaForInfinityV7_SMAv2_1-3b4479f9 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NotAnotherSMAOffsetStrategy --strategy-path repos/Juusseli_Trade --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NotAnotherSMAOffsetStrategy-7155ba0b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NotAnotherSMAOffsetStrategy_gate.json --strategy NotAnotherSMAOffsetStrategy --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategy --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategy --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyHO`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy NotAnotherSMAOffsetStrategyHO --strategy-path repos/MMR-19_freqtrade-strategies/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NotAnotherSMAOffsetStrategyHO-46b0975f-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NotAnotherSMAOffsetStrategyHO_gate.json --strategy NotAnotherSMAOffsetStrategyHO --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyHO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyHO --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyHO --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyHOv3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NotAnotherSMAOffsetStrategyHOv3 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NotAnotherSMAOffsetStrategyHOv3-a8426b53 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NotAnotherSMAOffsetStrategyHOv3_gate.json --strategy NotAnotherSMAOffsetStrategyHOv3 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyHOv3 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyHOv3 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyHOv3 --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyLite`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NotAnotherSMAOffsetStrategyLite --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NotAnotherSMAOffsetStrategyLite-8bc980ab --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyLite --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyLite --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyLite --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyLite --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyModHO`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NotAnotherSMAOffsetStrategyModHO --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NotAnotherSMAOffsetStrategyModHO-9595a546 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyModHO --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyModHO --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyModHO --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyModHO --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --strategy-path repos/davidzr_freqtrade-strategies/strategies/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901-7f3e81e1 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901 --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategyX1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NotAnotherSMAOffsetStrategyX1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NotAnotherSMAOffsetStrategyX1-d4abd7ee --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/NotAnotherSMAOffsetStrategyX1_gate.json --strategy NotAnotherSMAOffsetStrategyX1 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyX1 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategyX1 --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategyX1 --timerange 20190101-20190401 --no-color
  ```
- `NotAnotherSMAOffsetStrategy_uzi`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NotAnotherSMAOffsetStrategy_uzi --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NotAnotherSMAOffsetStrategy_uzi-e05784ab --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategy_uzi --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategy_uzi --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NotAnotherSMAOffsetStrategy_uzi --strategy-path user_data/profile_bias_strategies/NotAnotherSMAOffsetStrategy_uzi --timerange 20190101-20190401 --no-color
  ```
- `NowoIchimoku1hV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy NowoIchimoku1hV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NowoIchimoku1hV2-03eb2650 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ONUR --strategy-path repos/davidzr_freqtrade-strategies/strategies/ONUR --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ONUR-1758f273 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ONUR --strategy-path user_data/profile_bias_strategies/ONUR --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ONUR --strategy-path user_data/profile_bias_strategies/ONUR --timerange 20190101-20190401 --no-color
  ```
- `ORBAlgo`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy ORBAlgo --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/ORB --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ORBAlgo-091aa388-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy ORBAlgo --strategy-path user_data/profile_bias_strategies/ORBAlgo-091aa388 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy ORBAlgo --strategy-path user_data/profile_bias_strategies/ORBAlgo-091aa388 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
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
- `Obelisk_TradePro_Ichi_v1_1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Obelisk_TradePro_Ichi_v1_1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_TradePro_Ichi_v1_1-d9ad6391 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Obelisk_TradePro_Ichi_v2_1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Obelisk_TradePro_Ichi_v2_1-b409b943 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy OmaGann --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/OmaGann-9401627a --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy PRICEFOLLOWING --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PRICEFOLLOWING-1b9eb440 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PRICEFOLLOWING --strategy-path user_data/profile_bias_strategies/PRICEFOLLOWING --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PRICEFOLLOWING --strategy-path user_data/profile_bias_strategies/PRICEFOLLOWING --timerange 20190101-20190401 --no-color
  ```
- `PRICEFOLLOWINGX`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy PRICEFOLLOWINGX --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PRICEFOLLOWINGX-cc825e55 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PRICEFOLLOWINGX --strategy-path user_data/profile_bias_strategies/PRICEFOLLOWINGX --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PRICEFOLLOWINGX --strategy-path user_data/profile_bias_strategies/PRICEFOLLOWINGX --timerange 20190101-20190401 --no-color
  ```
- `ParabolicSarStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy ParabolicSarStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ParabolicSarStrategy-b60d3532 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ParabolicSarStrategy --strategy-path user_data/profile_bias_strategies/ParabolicSarStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ParabolicSarStrategy --strategy-path user_data/profile_bias_strategies/ParabolicSarStrategy --timerange 20190101-20190401 --no-color
  ```
- `PatternRecognition`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy PatternRecognition --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PatternRecognition-1dee08f2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PatternRecognition --strategy-path user_data/profile_bias_strategies/PatternRecognition-1dee08f2 --timerange 20200301-20200601 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PatternRecognition --strategy-path user_data/profile_bias_strategies/PatternRecognition --timerange 20190101-20190401 --no-color
  ```
- `Patterns2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Patterns2 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/Patterns2" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Patterns2-39f34344 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Patterns2 --strategy-path user_data/profile_bias_strategies/Patterns2-39f34344 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Patterns2 --strategy-path user_data/profile_bias_strategies/Patterns2-39f34344 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Persia`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Persia --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Persia-f2f6ac3e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Persia-f2f6ac3e_gate.json --strategy Persia --strategy-path user_data/profile_bias_strategies/Persia-f2f6ac3e --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/Persia_startup_288.json --strategy Persia --strategy-path user_data/profile_bias_strategies/Persia-f2f6ac3e --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `PolymarketMeanReversionStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/PolymarketMeanReversionStrategy-9c33dc8c-override-aa2053461232.json --strategy PolymarketMeanReversionStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PolymarketMeanReversionStrategy-9c33dc8c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/PolymarketMeanReversionStrategy-9c33dc8c_gate.json --strategy PolymarketMeanReversionStrategy --strategy-path user_data/profile_bias_strategies/PolymarketMeanReversionStrategy-9c33dc8c --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PolymarketMeanReversionStrategy --strategy-path user_data/profile_bias_strategies/PolymarketMeanReversionStrategy-9c33dc8c --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190 --timeframe 4h
  ```
- `PolymarketMomentumStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config user_data/profile_configs/PolymarketMomentumStrategy-aee6b82b-override-aa2053461232.json --strategy PolymarketMomentumStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PolymarketMomentumStrategy-aee6b82b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/PolymarketMomentumStrategy-aee6b82b_gate.json --strategy PolymarketMomentumStrategy --strategy-path user_data/profile_bias_strategies/PolymarketMomentumStrategy-aee6b82b --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PolymarketMomentumStrategy --strategy-path user_data/profile_bias_strategies/PolymarketMomentumStrategy-aee6b82b --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540 2190 --timeframe 4h
  ```
- `PowerTower`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy PowerTower --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PowerTower-89714471 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PowerTower --strategy-path user_data/profile_bias_strategies/PowerTower --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PowerTower --strategy-path user_data/profile_bias_strategies/PowerTower --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `PpoMomentumStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy PpoMomentumStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PpoMomentumStrategy-b9a916e0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PpoMomentumStrategy --strategy-path user_data/profile_bias_strategies/PpoMomentumStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PpoMomentumStrategy --strategy-path user_data/profile_bias_strategies/PpoMomentumStrategy --timerange 20190101-20190401 --no-color
  ```
- `PriceActionCandleStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy PriceActionCandleStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PriceActionCandleStrategy-bafd96a9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PriceActionCandleStrategy --strategy-path user_data/profile_bias_strategies/PriceActionCandleStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PriceActionCandleStrategy --strategy-path user_data/profile_bias_strategies/PriceActionCandleStrategy --timerange 20190101-20190401 --no-color
  ```
- `PriceChannelStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy PriceChannelStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PriceChannelStrategy-a656b945 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PriceChannelStrategy --strategy-path user_data/profile_bias_strategies/PriceChannelStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PriceChannelStrategy --strategy-path user_data/profile_bias_strategies/PriceChannelStrategy --timerange 20190101-20190401 --no-color
  ```
- `PumpDetector`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy PumpDetector --strategy-path repos/davidzr_freqtrade-strategies/strategies/PumpDetector --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/PumpDetector-382b1730 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PumpDetector --strategy-path user_data/profile_bias_strategies/PumpDetector --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PumpDetector --strategy-path user_data/profile_bias_strategies/PumpDetector --timerange 20190101-20190401 --no-color
  ```
- `QuickBuyStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy QuickBuyStrategy --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/QuickBuyStrategy-e4bfe3e8-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy QuickBuyStrategy --strategy-path user_data/profile_bias_strategies/QuickBuyStrategy-e4bfe3e8 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy QuickBuyStrategy --strategy-path user_data/profile_bias_strategies/QuickBuyStrategy-e4bfe3e8 --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `Quickie`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Quickie --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Quickie-dab280e0 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Quickie --strategy-path user_data/profile_bias_strategies/Quickie --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Quickie --strategy-path user_data/profile_bias_strategies/Quickie --timerange 20190101-20190401 --no-color
  ```
- `RSI`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy RSI --strategy-path repos/davidzr_freqtrade-strategies/strategies/RSI --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RSI-6a079fd1 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy RSI_BB --strategy-path repos/mikedigriz_freqtrade-strategy-mikedigriz/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RSI_BB-ebe5244c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI_BB --strategy-path user_data/profile_bias_strategies/RSI_BB --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI_BB --strategy-path user_data/profile_bias_strategies/RSI_BB --timerange 20190101-20190401 --no-color
  ```
- `RSI_BB_MACD_Nov_2023_1h_2_Dec`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy RSI_BB_MACD_Nov_2023_1h_2_Dec --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/Picasso --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RSI_BB_MACD_Nov_2023_1h_2_Dec-87700a43-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy RSI_BB_MACD_Nov_2023_1h_2_Dec --strategy-path user_data/profile_bias_strategies/RSI_BB_MACD_Nov_2023_1h_2_Dec-87700a43 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy RSI_BB_MACD_Nov_2023_1h_2_Dec --strategy-path user_data/profile_bias_strategies/RSI_BB_MACD_Nov_2023_1h_2_Dec-87700a43 --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336
  ```
- `RSI_EMA_strategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy RSI_EMA_strategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RSI_EMA_strategy-9053385e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI_EMA_strategy --strategy-path user_data/profile_bias_strategies/RSI_EMA_strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RSI_EMA_strategy --strategy-path user_data/profile_bias_strategies/RSI_EMA_strategy --timerange 20190101-20190401 --no-color
  ```
- `RSIv2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy RSIv2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/RSIv2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RSIv2-f567e470 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RSIv2 --strategy-path user_data/profile_bias_strategies/RSIv2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RSIv2 --strategy-path user_data/profile_bias_strategies/RSIv2 --timerange 20190101-20190401 --no-color
  ```
- `RalliV1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy RalliV1 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RalliV1-ea9894c9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RalliV1 --strategy-path user_data/profile_bias_strategies/RalliV1 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RalliV1 --strategy-path user_data/profile_bias_strategies/RalliV1 --timerange 20190101-20190401 --no-color
  ```
- `RalliV1_disable56`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy RalliV1_disable56 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RalliV1_disable56-0bc70ac8 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ReinforcedAverageStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ReinforcedAverageStrategy-8767d79d --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ReinforcedAverageStrategy --strategy-path user_data/profile_bias_strategies/ReinforcedAverageStrategy --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ReinforcedAverageStrategy --strategy-path user_data/profile_bias_strategies/ReinforcedAverageStrategy --timerange 20190101-20190401 --no-color
  ```
- `ReinforcedSmoothScalp`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ReinforcedSmoothScalp --strategy-path repos/MelvynClark_Freqtrade-Strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ReinforcedSmoothScalp-a3abdfaa --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ReinforcedSmoothScalp --strategy-path user_data/profile_bias_strategies/ReinforcedSmoothScalp --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ReinforcedSmoothScalp --strategy-path user_data/profile_bias_strategies/ReinforcedSmoothScalp --timerange 20190101-20190401 --no-color
  ```
- `RobotradingBody`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy RobotradingBody --strategy-path repos/davidzr_freqtrade-strategies/strategies/RobotradingBody --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RobotradingBody-ec6fd706 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RobotradingBody --strategy-path user_data/profile_bias_strategies/RobotradingBody --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RobotradingBody --strategy-path user_data/profile_bias_strategies/RobotradingBody --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540
  ```
- `RocMomentumStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy RocMomentumStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RocMomentumStrategy-ecfd7c95 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RocMomentumStrategy --strategy-path user_data/profile_bias_strategies/RocMomentumStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RocMomentumStrategy --strategy-path user_data/profile_bias_strategies/RocMomentumStrategy --timerange 20190101-20190401 --no-color
  ```
- `Roth01`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Roth01 --strategy-path repos/davidzr_freqtrade-strategies/strategies/Roth01 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Roth01-6f953383 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Roth01 --strategy-path user_data/profile_bias_strategies/Roth01 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Roth01 --strategy-path user_data/profile_bias_strategies/Roth01 --timerange 20190101-20190401 --no-color
  ```
- `Roth03`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Roth03 --strategy-path repos/davidzr_freqtrade-strategies/strategies/Roth03 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Roth03-039e9893 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Roth03 --strategy-path user_data/profile_bias_strategies/Roth03 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Roth03 --strategy-path user_data/profile_bias_strategies/Roth03 --timerange 20190101-20190401 --no-color
  ```
- `RsiBollingerStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy RsiBollingerStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RsiBollingerStrategy-86871f9f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RsiBollingerStrategy --strategy-path user_data/profile_bias_strategies/RsiBollingerStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RsiBollingerStrategy --strategy-path user_data/profile_bias_strategies/RsiBollingerStrategy --timerange 20190101-20190401 --no-color
  ```
- `RsiDivergenceStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy RsiDivergenceStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RsiDivergenceStrategy-75586daa --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RsiDivergenceStrategy --strategy-path user_data/profile_bias_strategies/RsiDivergenceStrategy --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RsiDivergenceStrategy --strategy-path user_data/profile_bias_strategies/RsiDivergenceStrategy --timerange 20190101-20190401 --no-color
  ```
- `SAR`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SAR --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SAR-c00b2014 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SAR --strategy-path user_data/profile_bias_strategies/SAR --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SAR --strategy-path user_data/profile_bias_strategies/SAR-c00b2014 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SARCross`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SARCross --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/SARCross" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SARCross-0c09ed9a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SARCross --strategy-path user_data/profile_bias_strategies/SARCross-0c09ed9a --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SARCross --strategy-path user_data/profile_bias_strategies/SARCross-0c09ed9a --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAIP3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAIP3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/SMAIP3 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAIP3-9f3f2209 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOG --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOG-486e4c4f --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOG --strategy-path user_data/profile_bias_strategies/SMAOG --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOG --strategy-path user_data/profile_bias_strategies/SMAOG --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAOPv1_TTF`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy SMAOPv1_TTF --strategy-path user_data/profile_repairs --timerange 20200301-20210301 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOPv1_TTF-fd792764-smoke_20200301_20210301-fca63e6f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOPv1_TTF --strategy-path user_data/profile_bias_strategies/SMAOPv1_TTF-fd792764 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOPv1_TTF --strategy-path user_data/profile_bias_strategies/SMAOPv1_TTF-fd792764 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAOffset`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffset --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffset-2a5b3c73 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset --strategy-path user_data/profile_bias_strategies/SMAOffset --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset --strategy-path user_data/profile_bias_strategies/SMAOffset --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOpt`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffsetProtectOpt --strategy-path repos/davidzr_freqtrade-strategies/strategies/SMAOffsetProtectOpt --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetProtectOpt-2152c953 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOpt --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOpt --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOpt --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOpt --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV0`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffsetProtectOptV0 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetProtectOptV0-6414abca --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV0 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV0 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV0 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV0 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffsetProtectOptV1 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetProtectOptV1-e1bbd837 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1HO1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffsetProtectOptV1HO1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetProtectOptV1HO1-16235a5a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1HO1 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1HO1 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1HO1 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1HO1 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1Mod`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffsetProtectOptV1Mod --strategy-path repos/davidzr_freqtrade-strategies/strategies/SMAOffsetProtectOptV1Mod --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetProtectOptV1Mod-1ea5626b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1Mod2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffsetProtectOptV1Mod2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetProtectOptV1Mod2-aeb50ca9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod2 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod2 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod2 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod2 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetProtectOptV1Mod2_antipump`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy SMAOffsetProtectOptV1Mod2_antipump --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetProtectOptV1Mod2_antipump --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod2_antipump --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod2_antipump-a59e39c8 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1Mod2_antipump --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1Mod2_antipump-a59e39c8 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAOffsetProtectOptV1_kkeue_20210619`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffsetProtectOptV1_kkeue_20210619 --strategy-path repos/davidzr_freqtrade-strategies/strategies/SMAOffsetProtectOptV1_kkeue_20210619 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetProtectOptV1_kkeue_20210619-1de98e43 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1_kkeue_20210619 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1_kkeue_20210619 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetProtectOptV1_kkeue_20210619 --strategy-path user_data/profile_bias_strategies/SMAOffsetProtectOptV1_kkeue_20210619 --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffsetV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffsetV2-34f5bfe3 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetV2 --strategy-path user_data/profile_bias_strategies/SMAOffsetV2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetV2 --strategy-path user_data/profile_bias_strategies/SMAOffsetV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SMAOffset_Hippocritical_dca`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffset_Hippocritical_dca --strategy-path repos/TheoBrigitte_freqtrade/strategies/smas --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffset_Hippocritical_dca-396122f8 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffset_Hippocritical_dca_old --strategy-path repos/TheoBrigitte_freqtrade/strategies/smas --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffset_Hippocritical_dca_old-fec4f46c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca_old --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_old --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca_old --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_old --timerange 20190101-20190401 --no-color
  ```
- `SMAOffset_Hippocritical_dca_protections`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SMAOffset_Hippocritical_dca_protections --strategy-path repos/TheoBrigitte_freqtrade/strategies/smas --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMAOffset_Hippocritical_dca_protections-035af48f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca_protections --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_protections --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca_protections --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca_protections --timerange 20190101-20190401 --no-color
  ```
- `SMA_BBRSI`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy SMA_BBRSI --strategy-path repos/davidzr_freqtrade-strategies/strategies/SMA_BBRSI --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SMA_BBRSI-f844971d-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMA_BBRSI --strategy-path user_data/profile_bias_strategies/SMA_BBRSI --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMA_BBRSI --strategy-path user_data/profile_bias_strategies/SMA_BBRSI --timerange 20190101-20190401 --no-color
  ```
- `SRsi`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy SRsi --strategy-path repos/davidzr_freqtrade-strategies/strategies/SRsi --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SRsi-6757d437 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SRsi --strategy-path user_data/profile_bias_strategies/SRsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SRsi --strategy-path user_data/profile_bias_strategies/SRsi --timerange 20190101-20190401 --no-color
  ```
- `STRATEGY_RSI_BB_BOUNDS_CROSS`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy STRATEGY_RSI_BB_BOUNDS_CROSS --strategy-path repos/davidzr_freqtrade-strategies/strategies/STRATEGY_RSI_BB_BOUNDS_CROSS --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/STRATEGY_RSI_BB_BOUNDS_CROSS-00a44a09 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy STRATEGY_RSI_BB_BOUNDS_CROSS --strategy-path user_data/profile_bias_strategies/STRATEGY_RSI_BB_BOUNDS_CROSS --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy STRATEGY_RSI_BB_BOUNDS_CROSS --strategy-path user_data/profile_bias_strategies/STRATEGY_RSI_BB_BOUNDS_CROSS --timerange 20190101-20190401 --no-color
  ```
- `STRATEGY_RSI_BB_CROSS`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy STRATEGY_RSI_BB_CROSS --strategy-path repos/davidzr_freqtrade-strategies/strategies/STRATEGY_RSI_BB_CROSS --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/STRATEGY_RSI_BB_CROSS-033b8735 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy STRATEGY_RSI_BB_CROSS --strategy-path user_data/profile_bias_strategies/STRATEGY_RSI_BB_CROSS --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy STRATEGY_RSI_BB_CROSS --strategy-path user_data/profile_bias_strategies/STRATEGY_RSI_BB_CROSS --timerange 20190101-20190401 --no-color
  ```
- `SUPPORT_RESISTANCE`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SUPPORT_RESISTANCE --strategy-path repos/djienne_YOUTUBE_STRATEGIES_FREQTRADE/Experiences/SUPPORT_RESISTANCE/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SUPPORT_RESISTANCE-e57b787f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SUPPORT_RESISTANCE --strategy-path user_data/profile_bias_strategies/SUPPORT_RESISTANCE-e57b787f --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SUPPORT_RESISTANCE --strategy-path user_data/profile_bias_strategies/SUPPORT_RESISTANCE-e57b787f --timerange 20190101-20190401 --no-color --startup-candle 2 4 14 28 60 180 730
  ```
- `SampleStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SampleStrategy --strategy-path repos/AlexCryptoKing_freqailstm/user_data/config/templates --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SampleStrategy-2b02bb67 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategy --strategy-path user_data/profile_bias_strategies/SampleStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategy --strategy-path user_data/profile_bias_strategies/SampleStrategy --timerange 20190101-20190401 --no-color
  ```
- `SampleStrategyV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SampleStrategyV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SampleStrategyV2-bf71b29d --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategyV2 --strategy-path user_data/profile_bias_strategies/SampleStrategyV2 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategyV2 --strategy-path user_data/profile_bias_strategies/SampleStrategyV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Sar`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Sar --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Sar-ee566748 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Sar --strategy-path user_data/profile_bias_strategies/Sar --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Sar --strategy-path user_data/profile_bias_strategies/Sar --timerange 20190101-20190401 --no-color
  ```
- `Saturn5`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Saturn5 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Saturn5-5682c41e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/Saturn5_gate.json --strategy Saturn5 --strategy-path user_data/profile_bias_strategies/Saturn5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Saturn5 --strategy-path user_data/profile_bias_strategies/Saturn5 --timerange 20190101-20190401 --no-color
  ```
- `Scalp`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Scalp --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Scalp-025555a4 --cache none
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
- `Schism2_BTC`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Schism2_BTC --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Schism2_BTC-2a7bcf41-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism2_BTC --strategy-path user_data/profile_bias_strategies/Schism2_BTC-2a7bcf41 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism2_BTC --strategy-path user_data/profile_bias_strategies/Schism2_BTC-2a7bcf41 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `Schism2_ETH`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy Schism2_ETH --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Schism2_ETH-af7072d3-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism2_ETH --strategy-path user_data/profile_bias_strategies/Schism2_ETH-af7072d3 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism2_ETH --strategy-path user_data/profile_bias_strategies/Schism2_ETH-af7072d3 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `Schism3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Schism3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Schism3-ee2a15e4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism3 --strategy-path user_data/profile_bias_strategies/Schism3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism3 --strategy-path user_data/profile_bias_strategies/Schism3 --timerange 20190101-20190401 --no-color
  ```
- `Schism4`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Schism4 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Schism4-cabe5254 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism4 --strategy-path user_data/profile_bias_strategies/Schism4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Schism4 --strategy-path user_data/profile_bias_strategies/Schism4 --timerange 20190101-20190401 --no-color
  ```
- `Seb`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Seb --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Seb-884e1568 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Seb --strategy-path user_data/profile_bias_strategies/Seb --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Seb --strategy-path user_data/profile_bias_strategies/Seb --timerange 20190101-20190401 --no-color
  ```
- `Simple`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Simple --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Simple-3fee95da --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Simple --strategy-path user_data/profile_bias_strategies/Simple --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Simple --strategy-path user_data/profile_bias_strategies/Simple --timerange 20190101-20190401 --no-color
  ```
- `SimpleBollinger`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SimpleBollinger --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/SimpleBollinger" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SimpleBollinger-3b182c17 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SimpleBollinger --strategy-path user_data/profile_bias_strategies/SimpleBollinger-3b182c17 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SimpleBollinger --strategy-path user_data/profile_bias_strategies/SimpleBollinger-3b182c17 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SimpleHopt`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SimpleHopt --strategy-path "repos/MelvynClark_Freqtrade-Strategy/Simple Strategy" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SimpleHopt-ade85462 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SimpleHopt --strategy-path user_data/profile_bias_strategies/SimpleHopt --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SimpleHopt --strategy-path user_data/profile_bias_strategies/SimpleHopt --timerange 20190101-20190401 --no-color
  ```
- `SimpleHopt1Along`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SimpleHopt1Along --strategy-path "repos/MelvynClark_Freqtrade-Strategy/Simple Strategy" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SimpleHopt1Along-df7ee9ca --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SimpleHopt1Along --strategy-path user_data/profile_bias_strategies/SimpleHopt1Along --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/SimpleHopt1Along_startup_6.json --strategy SimpleHopt1Along --strategy-path user_data/profile_bias_strategies/SimpleHopt1Along --timerange 20190101-20190401 --no-color --startup-candle 6 12 42 84 180 540
  ```
- `SimpleRSI_Shorts`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy SimpleRSI_Shorts --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/SimpleRSI --timerange 20200301-20210301 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SimpleRSI_Shorts-f0dec165-smoke_20200301_20210301-fca63e6f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy SimpleRSI_Shorts --strategy-path user_data/profile_bias_strategies/SimpleRSI_Shorts-f0dec165 --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy SimpleRSI_Shorts --strategy-path user_data/profile_bias_strategies/SimpleRSI_Shorts-f0dec165 --timerange 20200301-20200601 --no-color --startup-candle 1 2 7 14
  ```
- `SlowPotato`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SlowPotato --strategy-path repos/davidzr_freqtrade-strategies/strategies/SlowPotato --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SlowPotato-6a44af82 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SlowPotato --strategy-path user_data/profile_bias_strategies/SlowPotato --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SlowPotato --strategy-path user_data/profile_bias_strategies/SlowPotato --timerange 20190101-20190401 --no-color
  ```
- `Slowbro`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Slowbro --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Slowbro-ad1dbbe4 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Slowbro --strategy-path user_data/profile_bias_strategies/Slowbro --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Slowbro --strategy-path user_data/profile_bias_strategies/Slowbro --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `SmaRsiStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SmaRsiStrategy --strategy-path repos/DutchCryptoDad_FreqtradeBotStrategyDevelopmentForBeginners --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SmaRsiStrategy-62d3e5a3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SmaRsiStrategy --strategy-path user_data/profile_bias_strategies/SmaRsiStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SmaRsiStrategy --strategy-path user_data/profile_bias_strategies/SmaRsiStrategy --timerange 20190101-20190401 --no-color
  ```
- `SmartMoneyStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SmartMoneyStrategy --strategy-path repos/mikedigriz_freqtrade-strategy-mikedigriz/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SmartMoneyStrategy-83dc6dbe --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SmoothOperator --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SmoothOperator-27d8facc --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SmoothOperator --strategy-path user_data/profile_bias_strategies/SmoothOperator --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SmoothOperator --strategy-path user_data/profile_bias_strategies/SmoothOperator --timerange 20190101-20190401 --no-color
  ```
- `SmoothScalp`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy SmoothScalp --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SmoothScalp-aa3c9357 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SmoothScalp --strategy-path user_data/profile_bias_strategies/SmoothScalp --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SmoothScalp --strategy-path user_data/profile_bias_strategies/SmoothScalp --timerange 20190101-20190401 --no-color
  ```
- `Squeeze001`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Squeeze001 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/Squeeze001" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Squeeze001-f1de728b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Squeeze001 --strategy-path user_data/profile_bias_strategies/Squeeze001-f1de728b --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Squeeze001 --strategy-path user_data/profile_bias_strategies/Squeeze001-f1de728b --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `Squeeze002`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Squeeze002 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/__Squeeze002" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Squeeze002-11618dd8 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Squeeze002 --strategy-path user_data/profile_bias_strategies/Squeeze002-11618dd8 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Squeeze002 --strategy-path user_data/profile_bias_strategies/Squeeze002-11618dd8 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SqueezeMomentum`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SqueezeMomentum --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SqueezeMomentum-55dbc2ef --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeMomentum --strategy-path user_data/profile_bias_strategies/SqueezeMomentum --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeMomentum --strategy-path user_data/profile_bias_strategies/SqueezeMomentum --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `SqueezeMomentumStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy SqueezeMomentumStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SqueezeMomentumStrategy-7744423e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeMomentumStrategy --strategy-path user_data/profile_bias_strategies/SqueezeMomentumStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeMomentumStrategy --strategy-path user_data/profile_bias_strategies/SqueezeMomentumStrategy --timerange 20190101-20190401 --no-color
  ```
- `SqueezeOff`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SqueezeOff --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/5/_SqueezeOff" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SqueezeOff-00971d90 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeOff --strategy-path user_data/profile_bias_strategies/SqueezeOff-00971d90 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SqueezeOff --strategy-path user_data/profile_bias_strategies/SqueezeOff-00971d90 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `StarRise`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy StarRise --strategy-path repos/TheoBrigitte_freqtrade/strategies/starrise --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StarRise-2ce8ff8a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StarRise --strategy-path user_data/profile_bias_strategies/StarRise --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StarRise --strategy-path user_data/profile_bias_strategies/StarRise --timerange 20190101-20190401 --no-color
  ```
- `StarRise_V2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy StarRise_V2 --strategy-path repos/TheoBrigitte_freqtrade/strategies/starrise --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StarRise_V2 --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StarRise_V2 --strategy-path user_data/profile_bias_strategies/StarRise_V2-b4e4e112 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StarRise_V2 --strategy-path user_data/profile_bias_strategies/StarRise_V2-b4e4e112 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `StarRise_strat`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy StarRise_strat --strategy-path repos/TheoBrigitte_freqtrade/strategies/starrise --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StarRise_strat-7f42ebda --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy StochRSITEMA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StochRSITEMA-ad00b250 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochRSITEMA --strategy-path user_data/profile_bias_strategies/StochRSITEMA --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochRSITEMA --strategy-path user_data/profile_bias_strategies/StochRSITEMA --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `StochasticCciStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy StochasticCciStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StochasticCciStrategy-11eeffb3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticCciStrategy --strategy-path user_data/profile_bias_strategies/StochasticCciStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticCciStrategy --strategy-path user_data/profile_bias_strategies/StochasticCciStrategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `StochasticOversoldStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy StochasticOversoldStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StochasticOversoldStrategy-ab64b5f2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticOversoldStrategy --strategy-path user_data/profile_bias_strategies/StochasticOversoldStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticOversoldStrategy --strategy-path user_data/profile_bias_strategies/StochasticOversoldStrategy --timerange 20190101-20190401 --no-color
  ```
- `StochasticRsiStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy StochasticRsiStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StochasticRsiStrategy-e7dd1810 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticRsiStrategy --strategy-path user_data/profile_bias_strategies/StochasticRsiStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticRsiStrategy --strategy-path user_data/profile_bias_strategies/StochasticRsiStrategy --timerange 20190101-20190401 --no-color
  ```
- `Strategy001`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Strategy001 --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Strategy001-57661416 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001 --strategy-path user_data/profile_bias_strategies/Strategy001 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001 --strategy-path user_data/profile_bias_strategies/Strategy001 --timerange 20190101-20190401 --no-color
  ```
- `Strategy001_custom_exit`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Strategy001_custom_exit --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Strategy001_custom_exit-8f220684 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001_custom_exit --strategy-path user_data/profile_bias_strategies/Strategy001_custom_exit --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001_custom_exit --strategy-path user_data/profile_bias_strategies/Strategy001_custom_exit --timerange 20190101-20190401 --no-color
  ```
- `Strategy001_custom_sell`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Strategy001_custom_sell --strategy-path repos/davidzr_freqtrade-strategies/strategies/Strategy001_custom_sell --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Strategy001_custom_sell-21468069 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001_custom_sell --strategy-path user_data/profile_bias_strategies/Strategy001_custom_sell --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy001_custom_sell --strategy-path user_data/profile_bias_strategies/Strategy001_custom_sell --timerange 20190101-20190401 --no-color
  ```
- `Strategy002`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Strategy002 --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Strategy002-feae8690 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy002 --strategy-path user_data/profile_bias_strategies/Strategy002 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy002 --strategy-path user_data/profile_bias_strategies/Strategy002 --timerange 20190101-20190401 --no-color
  ```
- `Strategy003`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Strategy003 --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Strategy003-63d0ad16 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy003 --strategy-path user_data/profile_bias_strategies/Strategy003 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy003 --strategy-path user_data/profile_bias_strategies/Strategy003 --timerange 20190101-20190401 --no-color
  ```
- `Strategy004`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Strategy004 --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Strategy004-39eb4f05 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy004 --strategy-path user_data/profile_bias_strategies/Strategy004 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy004 --strategy-path user_data/profile_bias_strategies/Strategy004 --timerange 20190101-20190401 --no-color
  ```
- `Strategy005`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Strategy005 --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Strategy005-880bd83d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy005 --strategy-path user_data/profile_bias_strategies/Strategy005 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Strategy005 --strategy-path user_data/profile_bias_strategies/Strategy005 --timerange 20190101-20190401 --no-color
  ```
- `StrategyScalpingFast`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy StrategyScalpingFast --strategy-path repos/davidzr_freqtrade-strategies/strategies/StrategyScalpingFast --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StrategyScalpingFast-7e07a768 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StrategyScalpingFast --strategy-path user_data/profile_bias_strategies/StrategyScalpingFast --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StrategyScalpingFast --strategy-path user_data/profile_bias_strategies/StrategyScalpingFast --timerange 20190101-20190401 --no-color
  ```
- `StrategyScalpingFast2`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy StrategyScalpingFast2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/StrategyScalpingFast2 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/StrategyScalpingFast2-aba7fb17 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StrategyScalpingFast2 --strategy-path user_data/profile_bias_strategies/StrategyScalpingFast2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StrategyScalpingFast2 --strategy-path user_data/profile_bias_strategies/StrategyScalpingFast2 --timerange 20190101-20190401 --no-color
  ```
- `SuperHV27_BTC`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy SuperHV27_BTC --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SuperHV27_BTC-5bfe795f-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SuperHV27_BTC --strategy-path user_data/profile_bias_strategies/SuperHV27_BTC-5bfe795f --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/SuperHV27_BTC_startup_288.json --strategy SuperHV27_BTC --strategy-path user_data/profile_bias_strategies/SuperHV27_BTC-5bfe795f --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `SuperTrend`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy SuperTrend --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SuperTrend-e9770a14 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SuperTrend --strategy-path user_data/profile_bias_strategies/SuperTrend --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SuperTrend --strategy-path user_data/profile_bias_strategies/SuperTrend-e9770a14 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `SupertrendStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SupertrendStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SupertrendStrategy-ced5f239 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy SwingHighToSky --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/SwingHighToSky-64dfd59e --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SwingHighToSky --strategy-path user_data/profile_bias_strategies/SwingHighToSky --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/SwingHighToSky_startup_96.json --strategy SwingHighToSky --strategy-path user_data/profile_bias_strategies/SwingHighToSky --timerange 20190101-20190401 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `TD`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TD --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/TD" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TD-b6a51c2a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TD --strategy-path user_data/profile_bias_strategies/TD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TD --strategy-path user_data/profile_bias_strategies/TD --timerange 20190101-20190401 --no-color
  ```
- `TDSequentialStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TDSequentialStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TDSequentialStrategy-833fdb92 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TDSequentialStrategy --strategy-path user_data/profile_bias_strategies/TDSequentialStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TDSequentialStrategy --strategy-path user_data/profile_bias_strategies/TDSequentialStrategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `TEMA`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy TEMA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TEMA-2a9399f6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TEMA --strategy-path user_data/profile_bias_strategies/TEMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TEMA --strategy-path user_data/profile_bias_strategies/TEMA --timerange 20190101-20190401 --no-color
  ```
- `TEMABounce`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy TEMABounce --strategy-path repos/webclinic017_strategies-freqtrade-/archived --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TEMABounce --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TEMABounce --strategy-path user_data/profile_bias_strategies/TEMABounce-9f6a881a --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TEMABounce --strategy-path user_data/profile_bias_strategies/TEMABounce-9f6a881a --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `TRIWAVE`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TRIWAVE --strategy-path repos/TheoBrigitte_freqtrade/strategies/wave --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TRIWAVE-cd5c62a5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TRIWAVE --strategy-path user_data/profile_bias_strategies/TRIWAVE --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TRIWAVE --strategy-path user_data/profile_bias_strategies/TRIWAVE --timerange 20190101-20190401 --no-color
  ```
- `TRIX_spot`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TRIX_spot --strategy-path repos/djienne_YOUTUBE_STRATEGIES_FREQTRADE/Strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TRIX_spot-b4f2394c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TRIX_spot --strategy-path user_data/profile_bias_strategies/TRIX_spot-b4f2394c --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TRIX_spot --strategy-path user_data/profile_bias_strategies/TRIX_spot-b4f2394c --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `TWAPStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy TWAPStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TWAPStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy TWAPStrategy --strategy-path user_data/profile_bias_strategies/TWAPStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy TWAPStrategy --strategy-path user_data/profile_bias_strategies/TWAPStrategy --timerange 20200301-20200401 --no-color
  ```
- `TechnicalExampleStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TechnicalExampleStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TechnicalExampleStrategy-16a5767b --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TechnicalExampleStrategy --strategy-path user_data/profile_bias_strategies/TechnicalExampleStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TechnicalExampleStrategy --strategy-path user_data/profile_bias_strategies/TechnicalExampleStrategy --timerange 20190101-20190401 --no-color
  ```
- `TemaMaster`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TemaMaster --strategy-path repos/davidzr_freqtrade-strategies/strategies/TemaMaster --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TemaMaster-bbf2c003 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaMaster --strategy-path user_data/profile_bias_strategies/TemaMaster --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaMaster --strategy-path user_data/profile_bias_strategies/TemaMaster --timerange 20190101-20190401 --no-color
  ```
- `TemaMaster3`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy TemaMaster3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/TemaMaster3 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TemaMaster3-59c6d053 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaMaster3 --strategy-path user_data/profile_bias_strategies/TemaMaster3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaMaster3 --strategy-path user_data/profile_bias_strategies/TemaMaster3 --timerange 20190101-20190401 --no-color
  ```
- `TemaPure`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TemaPure --strategy-path repos/davidzr_freqtrade-strategies/strategies/TemaPure --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TemaPure-1716b882 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPure --strategy-path user_data/profile_bias_strategies/TemaPure --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPure --strategy-path user_data/profile_bias_strategies/TemaPure --timerange 20190101-20190401 --no-color
  ```
- `TemaPureNeat`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TemaPureNeat --strategy-path repos/davidzr_freqtrade-strategies/strategies/TemaPureNeat --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TemaPureNeat-92313791 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPureNeat --strategy-path user_data/profile_bias_strategies/TemaPureNeat --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPureNeat --strategy-path user_data/profile_bias_strategies/TemaPureNeat --timerange 20190101-20190401 --no-color
  ```
- `TemaPureTwo`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TemaPureTwo --strategy-path repos/davidzr_freqtrade-strategies/strategies/TemaPureTwo --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TemaPureTwo-3dcbc751 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPureTwo --strategy-path user_data/profile_bias_strategies/TemaPureTwo --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaPureTwo --strategy-path user_data/profile_bias_strategies/TemaPureTwo --timerange 20190101-20190401 --no-color
  ```
- `TemaStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy TemaStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TemaStrategy-73852f36 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaStrategy --strategy-path user_data/profile_bias_strategies/TemaStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TemaStrategy --strategy-path user_data/profile_bias_strategies/TemaStrategy --timerange 20190101-20190401 --no-color
  ```
- `TenderEnter`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TenderEnter --strategy-path repos/davidzr_freqtrade-strategies/strategies/TenderEnter --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TenderEnter-6b1745fc --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TheForce --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TheForce-9789c829 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TheForce --strategy-path user_data/profile_bias_strategies/TheForce --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TheForce --strategy-path user_data/profile_bias_strategies/TheForce --timerange 20190101-20190401 --no-color
  ```
- `TheRealPullbackV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TheRealPullbackV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TheRealPullbackV2-6b84aa55 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TouchEmaDelayStrategy --strategy-path repos/flaviosiotto_freqtrade-strategy/user_data/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TouchEmaDelayStrategy-f474cc0c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TouchEmaDelayStrategy --strategy-path user_data/profile_bias_strategies/TouchEmaDelayStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TouchEmaDelayStrategy --strategy-path user_data/profile_bias_strategies/TouchEmaDelayStrategy --timerange 20190101-20190401 --no-color
  ```
- `TouchEmaStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TouchEmaStrategy --strategy-path repos/flaviosiotto_freqtrade-strategy/user_data/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TouchEmaStrategy-d87f2077 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TouchEmaStrategy --strategy-path user_data/profile_bias_strategies/TouchEmaStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TouchEmaStrategy --strategy-path user_data/profile_bias_strategies/TouchEmaStrategy --timerange 20190101-20190401 --no-color
  ```
- `TrailingBuyStrat2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy TrailingBuyStrat2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrailingBuyStrat2 --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrailingBuyStrat2 --strategy-path user_data/profile_bias_strategies/TrailingBuyStrat2-74684ab5 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/TrailingBuyStrat2_startup_288.json --strategy TrailingBuyStrat2 --strategy-path user_data/profile_bias_strategies/TrailingBuyStrat2-74684ab5 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `TrailingBuyStratCluc`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy TrailingBuyStratCluc --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrailingBuyStratCluc --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrailingBuyStratCluc --strategy-path user_data/profile_bias_strategies/TrailingBuyStratCluc-e73b2a7a --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrailingBuyStratCluc --strategy-path user_data/profile_bias_strategies/TrailingBuyStratCluc-e73b2a7a --timerange 20200301-20200601 --no-color --startup-candle 1440 2880
  ```
- `TrailingBuyStratCluc5m`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy TrailingBuyStratCluc5m --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrailingBuyStratCluc5m --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrailingBuyStratCluc5m --strategy-path user_data/profile_bias_strategies/TrailingBuyStratCluc5m-2fa6e08a --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrailingBuyStratCluc5m --strategy-path user_data/profile_bias_strategies/TrailingBuyStratCluc5m-2fa6e08a --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `TrendAtrStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy TrendAtrStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrendAtrStrategy-b0b678b4 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrendAtrStrategy --strategy-path user_data/profile_bias_strategies/TrendAtrStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrendAtrStrategy --strategy-path user_data/profile_bias_strategies/TrendAtrStrategy --timerange 20190101-20190401 --no-color
  ```
- `TrendBreakout`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy TrendBreakout --strategy-path repos/Kureshi25_cryptobot/user_data/strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrendBreakout --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrendBreakout --strategy-path user_data/profile_bias_strategies/TrendBreakout-9b18ab53 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrendBreakout --strategy-path user_data/profile_bias_strategies/TrendBreakout-9b18ab53 --timerange 20190101-20190401 --no-color --startup-candle 1 2 7 14 30 90 365
  ```
- `TrendFutures`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy TrendFutures --strategy-path repos/Kureshi25_cryptobot/user_data/strategies --timerange 20200101-20210101 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrendFutures-4ee78b0b --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy TrendFutures --strategy-path user_data/profile_bias_strategies/TrendFutures-4ee78b0b --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy TrendFutures --strategy-path user_data/profile_bias_strategies/TrendFutures-4ee78b0b --timerange 20200301-20200401 --no-color --startup-candle 1 2 7 14
  ```
- `Trend_Strength_Directional`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Trend_Strength_Directional --strategy-path repos/davidzr_freqtrade-strategies/strategies/Trend_Strength_Directional --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Trend_Strength_Directional-23329309 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Trend_Strength_Directional --strategy-path user_data/profile_bias_strategies/Trend_Strength_Directional --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Trend_Strength_Directional --strategy-path user_data/profile_bias_strategies/Trend_Strength_Directional --timerange 20190101-20190401 --no-color
  ```
- `TripleEmaStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy TripleEmaStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TripleEmaStrategy-c38906e6 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TripleEmaStrategy --strategy-path user_data/profile_bias_strategies/TripleEmaStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TripleEmaStrategy --strategy-path user_data/profile_bias_strategies/TripleEmaStrategy --timerange 20190101-20190401 --no-color
  ```
- `TripleSuperTrendADXRSI`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy TripleSuperTrendADXRSI --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/TripleSuperTrendADXRSI --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TripleSuperTrendADXRSI-6eecbc1c-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy TripleSuperTrendADXRSI --strategy-path user_data/profile_bias_strategies/TripleSuperTrendADXRSI-6eecbc1c --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy TripleSuperTrendADXRSI --strategy-path user_data/profile_bias_strategies/TripleSuperTrendADXRSI-6eecbc1c --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336
  ```
- `TrixSignalStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy TrixSignalStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrixSignalStrategy-af4e0101 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixSignalStrategy --strategy-path user_data/profile_bias_strategies/TrixSignalStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixSignalStrategy --strategy-path user_data/profile_bias_strategies/TrixSignalStrategy --timerange 20190101-20190401 --no-color
  ```
- `TrixStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TrixStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrixStrategy-b72204f0 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixStrategy --strategy-path user_data/profile_bias_strategies/TrixStrategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixStrategy --strategy-path user_data/profile_bias_strategies/TrixStrategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `TrixV15Strategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TrixV15Strategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrixV15Strategy-d9dff207 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV15Strategy --strategy-path user_data/profile_bias_strategies/TrixV15Strategy --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV15Strategy --strategy-path user_data/profile_bias_strategies/TrixV15Strategy --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `TrixV21Strategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TrixV21Strategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrixV21Strategy-08b1252e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV21Strategy --strategy-path user_data/profile_bias_strategies/TrixV21Strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV21Strategy --strategy-path user_data/profile_bias_strategies/TrixV21Strategy --timerange 20190101-20190401 --no-color
  ```
- `TrixV23Strategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TrixV23Strategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TrixV23Strategy-ea11f02f --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV23Strategy --strategy-path user_data/profile_bias_strategies/TrixV23Strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV23Strategy --strategy-path user_data/profile_bias_strategies/TrixV23Strategy --timerange 20190101-20190401 --no-color
  ```
- `Trump_LIM`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Trump_LIM --strategy-path repos/djienne_YOUTUBE_STRATEGIES_FREQTRADE/Experiences/Trump_LIM/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Trump_LIM-4f331b98 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Trump_LIM --strategy-path user_data/profile_bias_strategies/Trump_LIM-4f331b98 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Trump_LIM --strategy-path user_data/profile_bias_strategies/Trump_LIM-4f331b98 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `TwoCandle`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TwoCandle --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TwoCandle-01e43a04 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TwoCandle --strategy-path user_data/profile_bias_strategies/TwoCandle --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TwoCandle --strategy-path user_data/profile_bias_strategies/TwoCandle --timerange 20190101-20190401 --no-color
  ```
- `TwoCandleTheory`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy TwoCandleTheory --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/TwoCandleTheory-aede3331 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TwoCandleTheory --strategy-path user_data/profile_bias_strategies/TwoCandleTheory-aede3331 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TwoCandleTheory --strategy-path user_data/profile_bias_strategies/TwoCandleTheory-aede3331 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `UltimateMomentumIndicator`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy UltimateMomentumIndicator --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/UltimateMomentumIndicator-492c612a --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy UltimateMomentumIndicator --strategy-path user_data/profile_bias_strategies/UltimateMomentumIndicator --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy UltimateMomentumIndicator --strategy-path user_data/profile_bias_strategies/UltimateMomentumIndicator --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `UniversalMACD`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy UniversalMACD --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/UniversalMACD-c5ae9ce5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy UniversalMACD --strategy-path user_data/profile_bias_strategies/UniversalMACD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy UniversalMACD --strategy-path user_data/profile_bias_strategies/UniversalMACD --timerange 20190101-20190401 --no-color
  ```
- `Uptrend`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy Uptrend --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/Uptrend-2cebb2ab --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Uptrend --strategy-path user_data/profile_bias_strategies/Uptrend --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Uptrend --strategy-path user_data/profile_bias_strategies/Uptrend --timerange 20190101-20190401 --no-color
  ```
- `UziChanTB2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy UziChanTB2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/UziChanTB2 --cache none --pairs {pair}   # 8 pairs, one call each
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy UziChanTB2 --strategy-path user_data/profile_bias_strategies/UziChanTB2-19d09656 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy UziChanTB2 --strategy-path user_data/profile_bias_strategies/UziChanTB2-19d09656 --timerange 20200301-20200601 --no-color --startup-candle 96 192 672 1344 2880
  ```
- `VWAP`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy VWAP --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/VWAP-1c5c938a --cache none
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
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy VolumeBreakoutStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/VolumeBreakoutStrategy-dafc22e5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy VolumeBreakoutStrategy --strategy-path user_data/profile_bias_strategies/VolumeBreakoutStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy VolumeBreakoutStrategy --strategy-path user_data/profile_bias_strategies/VolumeBreakoutStrategy --timerange 20190101-20190401 --no-color
  ```
- `VortexStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy VortexStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/VortexStrategy-e792ca6c --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy VortexStrategy --strategy-path user_data/profile_bias_strategies/VortexStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy VortexStrategy --strategy-path user_data/profile_bias_strategies/VortexStrategy --timerange 20190101-20190401 --no-color
  ```
- `VwapReversionStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy VwapReversionStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/VwapReversionStrategy-56e2a9f0 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy VwapReversionStrategy --strategy-path user_data/profile_bias_strategies/VwapReversionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy VwapReversionStrategy --strategy-path user_data/profile_bias_strategies/VwapReversionStrategy --timerange 20190101-20190401 --no-color
  ```
- `WTDMIPRICEDCAStrategyFuture`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy WTDMIPRICEDCAStrategyFuture --strategy-path repos/LazyPigPig_freqtrade-grid/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/WTDMIPRICEDCAStrategyFuture-6bd08369 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy WTDMIPRICEDCAStrategyFuture --strategy-path user_data/profile_bias_strategies/WTDMIPRICEDCAStrategyFuture-6bd08369 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/WTDMIPRICEDCAStrategyFuture_startup_288.json --strategy WTDMIPRICEDCAStrategyFuture --strategy-path user_data/profile_bias_strategies/WTDMIPRICEDCAStrategyFuture-6bd08369 --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `WTDMIPRICESDCAtrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy WTDMIPRICESDCAtrategy --strategy-path repos/LazyPigPig_freqtrade-grid/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/WTDMIPRICESDCAtrategy-f668b499 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy WTDMIPRICESDCAtrategy --strategy-path user_data/profile_bias_strategies/WTDMIPRICESDCAtrategy-f668b499 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/WTDMIPRICESDCAtrategy_startup_1440.json --strategy WTDMIPRICESDCAtrategy --strategy-path user_data/profile_bias_strategies/WTDMIPRICESDCAtrategy-f668b499 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `WTHO`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy WTHO --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/WTHO-4257b426-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy WTHO --strategy-path user_data/profile_bias_strategies/WTHO-4257b426 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/WTHO_startup_12.json --strategy WTHO --strategy-path user_data/profile_bias_strategies/WTHO-4257b426 --timerange 20200301-20200601 --no-color --startup-candle 12 24 84 168 360 1080 4380
  ```
- `WTX3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy WTX3 --strategy-path repos/TheoBrigitte_freqtrade/strategies/wtx3 --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/WTX3 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/WTX3_gate.json --strategy WTX3 --strategy-path user_data/profile_bias_strategies/WTX3 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/WTX3_startup_288.json --strategy WTX3 --strategy-path user_data/profile_bias_strategies/WTX3 --timerange 20200301-20200401 --no-color --startup-candle 288 576 2016
  ```
- `WaveTrendStra`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy WaveTrendStra --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/WaveTrendStra-e3b07ede --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy WaveTrendStra --strategy-path user_data/profile_bias_strategies/WaveTrendStra --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy WaveTrendStra --strategy-path user_data/profile_bias_strategies/WaveTrendStra --timerange 20190101-20190401 --no-color
  ```
- `WilliamsRStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy WilliamsRStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/WilliamsRStrategy-c16036d4 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy XtraThicc --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/XtraThicc-06cfa9e4 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy XtraThicc --strategy-path user_data/profile_bias_strategies/XtraThicc --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy XtraThicc --strategy-path user_data/profile_bias_strategies/XtraThicc --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `YOLO`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy YOLO --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/YOLO-99f26510 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy YOLO --strategy-path user_data/profile_bias_strategies/YOLO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy YOLO --strategy-path user_data/profile_bias_strategies/YOLO --timerange 20190101-20190401 --no-color
  ```
- `ZScoreMeanReversionStrategy`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy ZScoreMeanReversionStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ZScoreMeanReversionStrategy-33c3c74c --cache none
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
- `ZaratustraV31`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy ZaratustraV31 --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/remiotore --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ZaratustraV31-17f3529d-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy ZaratustraV31 --strategy-path user_data/profile_bias_strategies/ZaratustraV31-17f3529d --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/ZaratustraV31_startup_24.json --strategy ZaratustraV31 --strategy-path user_data/profile_bias_strategies/ZaratustraV31-17f3529d --timerange 20200301-20200601 --no-color --startup-candle 24 48 168 336
  ```
- `abbas`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy abbas --strategy-path repos/thinkong_freqtradestrategies/user_data/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/abbas-66cc6f6a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy abbas --strategy-path user_data/profile_bias_strategies/abbas-66cc6f6a --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy abbas --strategy-path user_data/profile_bias_strategies/abbas-66cc6f6a --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `adaptive`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy adaptive --strategy-path repos/davidzr_freqtrade-strategies/strategies/adaptive --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/adaptive-4bc3f073 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive --strategy-path user_data/profile_bias_strategies/adaptive --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive --strategy-path user_data/profile_bias_strategies/adaptive --timerange 20190101-20190401 --no-color
  ```
- `adaptive_trend`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy adaptive_trend --strategy-path repos/mlsys-io_PortfolioBench/strategy/adaptive_trend --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/adaptive_trend-4c45a656 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy adxbbrsi2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/adxbbrsi2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/adxbbrsi2-ab42fd07 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy bbandrsi --strategy-path repos/phuchust_freqtrade_strategy --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/bbandrsi-b2360e0a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbandrsi --strategy-path user_data/profile_bias_strategies/bbandrsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbandrsi --strategy-path user_data/profile_bias_strategies/bbandrsi --timerange 20190101-20190401 --no-color
  ```
- `bbrsi`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy bbrsi --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSI --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/bbrsi-10d8c6d1 --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy bbrsi4Freq --strategy-path repos/davidzr_freqtrade-strategies/strategies/bbrsi4Freq --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/bbrsi4Freq-71c90bc9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi4Freq --strategy-path user_data/profile_bias_strategies/bbrsi4Freq --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi4Freq --strategy-path user_data/profile_bias_strategies/bbrsi4Freq --timerange 20190101-20190401 --no-color
  ```
- `bestV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy bestV2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/bestV2 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/bestV2-4c1faad7 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bestV2 --strategy-path user_data/profile_bias_strategies/bestV2 --timerange 20200301-20260820 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bestV2 --strategy-path user_data/profile_bias_strategies/bestV2 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `bigshort`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_futures_config.json --strategy bigshort --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/2/bigshort" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/bigshort-ef8d2c90 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config profile_futures_config.json --strategy bigshort --strategy-path user_data/profile_bias_strategies/bigshort-ef8d2c90 --timerange 20200301-20200401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config profile_futures_config.json --strategy bigshort --strategy-path user_data/profile_bias_strategies/bigshort-ef8d2c90 --timerange 20200301-20200401 --no-color --startup-candle 1440
  ```
- `binance`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy binance --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/e0v1e --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/binance-59bba357-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy binance --strategy-path user_data/profile_bias_strategies/binance-59bba357 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy binance --strategy-path user_data/profile_bias_strategies/binance-59bba357 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
  ```
- `binance_shorts`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_futures_config.json --strategy binance_shorts --strategy-path repos/vaskosmihaylov_nfi-custom-strategies/user_data/strategies/e0v1e --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/binance_shorts-2d7eb835-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config runtime/profile_futures_config.json --strategy binance_shorts --strategy-path user_data/profile_bias_strategies/binance_shorts-2d7eb835 --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config runtime/profile_futures_config.json --strategy binance_shorts --strategy-path user_data/profile_bias_strategies/binance_shorts-2d7eb835 --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016
  ```
- `botbaby`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy botbaby --strategy-path repos/davidzr_freqtrade-strategies/strategies/botbaby --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/botbaby-dc176f79 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy botbaby --strategy-path user_data/profile_bias_strategies/botbaby --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy botbaby --strategy-path user_data/profile_bias_strategies/botbaby --timerange 20190101-20190401 --no-color --startup-candle 48 96 336 672 1440 4320
  ```
- `chatgpt`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy chatgpt --strategy-path repos/djienne_YOUTUBE_STRATEGIES_FREQTRADE/Strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/chatgpt-60965168 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy chatgpt --strategy-path user_data/profile_bias_strategies/chatgpt-60965168 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/chatgpt_startup_48.json --strategy chatgpt --strategy-path user_data/profile_bias_strategies/chatgpt-60965168 --timerange 20190101-20190401 --no-color --startup-candle 48 168 336 720 2160
  ```
- `conny`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy conny --strategy-path repos/davidzr_freqtrade-strategies/strategies/conny --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/conny-82fa40ec --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy cryptotank --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/cryptotank" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/cryptotank-c9c1afb9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotank --strategy-path user_data/profile_bias_strategies/cryptotank --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotank --strategy-path user_data/profile_bias_strategies/cryptotank --timerange 20190101-20190401 --no-color --startup-candle 24 48 168 336 720 2160
  ```
- `cryptotankV2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy cryptotankV2 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/cryptotankV2" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/cryptotankV2-210f4053 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV2 --strategy-path user_data/profile_bias_strategies/cryptotankV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV2 --strategy-path user_data/profile_bias_strategies/cryptotankV2 --timerange 20190101-20190401 --no-color
  ```
- `cryptotankV5`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy cryptotankV5 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/cryptotankV5" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/cryptotankV5-a75d705b --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy dualwave --strategy-path repos/TheoBrigitte_freqtrade/strategies/wave --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/dualwave-d51fbd84 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy dualwave --strategy-path user_data/profile_bias_strategies/dualwave --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy dualwave --strategy-path user_data/profile_bias_strategies/dualwave --timerange 20190101-20190401 --no-color
  ```
- `e6v34`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy e6v34 --strategy-path repos/davidzr_freqtrade-strategies/strategies/e6v34 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/e6v34-c1676810 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy e6v34 --strategy-path user_data/profile_bias_strategies/e6v34 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy e6v34 --strategy-path user_data/profile_bias_strategies/e6v34 --timerange 20190101-20190401 --no-color
  ```
- `eltoro`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy eltoro --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/eltoro-4b7ac68a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro --strategy-path user_data/profile_bias_strategies/eltoro --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro --strategy-path user_data/profile_bias_strategies/eltoro --timerange 20190101-20190401 --no-color
  ```
- `eltoro1_4`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy eltoro1_4 --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/eltoro1_4-9577fac2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro1_4 --strategy-path user_data/profile_bias_strategies/eltoro1_4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro1_4 --strategy-path user_data/profile_bias_strategies/eltoro1_4 --timerange 20190101-20190401 --no-color
  ```
- `eltoro1_4_simple`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy eltoro1_4_simple --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/eltoro1_4_simple-8a1dc3d9 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro1_4_simple --strategy-path user_data/profile_bias_strategies/eltoro1_4_simple --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy eltoro1_4_simple --strategy-path user_data/profile_bias_strategies/eltoro1_4_simple --timerange 20190101-20190401 --no-color
  ```
- `ema`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ema --strategy-path repos/davidzr_freqtrade-strategies/strategies/ema --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ema-8c15a763 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ema --strategy-path user_data/profile_bias_strategies/ema --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ema --strategy-path user_data/profile_bias_strategies/ema --timerange 20190101-20190401 --no-color
  ```
- `fahmibah`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy fahmibah --strategy-path repos/davidzr_freqtrade-strategies/strategies/fahmibah --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/fahmibah-9c2d9fa5 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy fahmibah --strategy-path user_data/profile_bias_strategies/fahmibah --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy fahmibah --strategy-path user_data/profile_bias_strategies/fahmibah --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `gettinMoist`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy gettinMoist --strategy-path repos/werkkrew_freqtrade-strategies/strategies/archived --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/gettinMoist-03ddd395 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy gettinMoist --strategy-path user_data/profile_bias_strategies/gettinMoist --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy gettinMoist --strategy-path user_data/profile_bias_strategies/gettinMoist --timerange 20190101-20190401 --no-color
  ```
- `gpt_reversal`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy gpt_reversal --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/2/gpt_reversal" --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/gpt_reversal-15eecf49 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy gpt_reversal --strategy-path user_data/profile_bias_strategies/gpt_reversal-15eecf49 --timerange 20190101-20190401 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy gpt_reversal --strategy-path user_data/profile_bias_strategies/gpt_reversal-15eecf49 --timerange 20190101-20190401 --no-color --startup-candle 1440 2880
  ```
- `hansencandlepatternV1`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy hansencandlepatternV1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/hansencandlepatternV1-3b3b1191 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy hansencandlepatternV1 --strategy-path user_data/profile_bias_strategies/hansencandlepatternV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy hansencandlepatternV1 --strategy-path user_data/profile_bias_strategies/hansencandlepatternV1 --timerange 20190101-20190401 --no-color
  ```
- `heikin`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy heikin --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/heikin-50477714 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy heikin --strategy-path user_data/profile_bias_strategies/heikin --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy heikin --strategy-path user_data/profile_bias_strategies/heikin --timerange 20190101-20190401 --no-color
  ```
- `hlhb`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy hlhb --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/hlhb-4d4b7c4a --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy keltnerchannel --strategy-path repos/davidzr_freqtrade-strategies/strategies/keltnerchannel --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/keltnerchannel-8f9afe32 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy keltnerchannel --strategy-path user_data/profile_bias_strategies/keltnerchannel --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy keltnerchannel --strategy-path user_data/profile_bias_strategies/keltnerchannel --timerange 20190101-20190401 --no-color
  ```
- `mabStra`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy mabStra --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/mabStra-c5e70fad --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy momentum_long --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum_long-4065a69d --cache none
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy moonhouse --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/moonhouse-a6f2773a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy moonhouse --strategy-path user_data/profile_bias_strategies/moonhouse --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy moonhouse --strategy-path user_data/profile_bias_strategies/moonhouse --timerange 20190101-20190401 --no-color
  ```
- `multi_tf`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy multi_tf --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/multi_tf-1362b53b-smoke_20200301_20200401-b4807b77 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy multi_tf --strategy-path user_data/profile_bias_strategies/multi_tf-1362b53b --timerange 20200301-20200601 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy multi_tf --strategy-path user_data/profile_bias_strategies/multi_tf-1362b53b --timerange 20200301-20200601 --no-color --startup-candle 288 576 2016 4032
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
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy slope_is_dopeCT --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/slope_is_dopeCT" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/slope_is_dopeCT-fdf33865 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy slope_is_dopeCT --strategy-path user_data/profile_bias_strategies/slope_is_dopeCT --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy slope_is_dopeCT --strategy-path user_data/profile_bias_strategies/slope_is_dopeCT --timerange 20190101-20190401 --no-color
  ```
- `stoploss`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy stoploss --strategy-path repos/davidzr_freqtrade-strategies/strategies/stoploss --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/stoploss-f9006559 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy stoploss --strategy-path user_data/profile_bias_strategies/stoploss --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy stoploss --strategy-path user_data/profile_bias_strategies/stoploss --timerange 20190101-20190401 --no-color
  ```
- `strato`
  ```
  backtest   [recorded] freqtrade backtesting --config runtime/profile_spot_config.json --strategy strato --strategy-path repos/davidzr_freqtrade-strategies/strategies/strato --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/strato-79fbe4ba --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy strato --strategy-path user_data/profile_bias_strategies/strato --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy strato --strategy-path user_data/profile_bias_strategies/strato --timerange 20190101-20190401 --no-color
  ```
- `tbtest`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy tbtest --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/tbtest-651f742e --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/tbtest_gate.json --strategy tbtest --strategy-path user_data/profile_bias_strategies/tbtest --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy tbtest --strategy-path user_data/profile_bias_strategies/tbtest --timerange 20190101-20190401 --no-color
  ```
- `thetank3`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy thetank3 --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/thetank3" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/thetank3-b9cc49ee --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy thetank3 --strategy-path user_data/profile_bias_strategies/thetank3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy thetank3 --strategy-path user_data/profile_bias_strategies/thetank3 --timerange 20190101-20190401 --no-color
  ```
- `thetank4TV`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy thetank4TV --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/thetank4TV" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/thetank4TV-d429206d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy thetank4TV --strategy-path user_data/profile_bias_strategies/thetank4TV --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy thetank4TV --strategy-path user_data/profile_bias_strategies/thetank4TV --timerange 20190101-20190401 --no-color
  ```
- `true_lambo`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy true_lambo --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/true_lambo-7c28329d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy true_lambo --strategy-path user_data/profile_bias_strategies/true_lambo --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy true_lambo --strategy-path user_data/profile_bias_strategies/true_lambo --timerange 20190101-20190401 --no-color
  ```
- `twinturboV8`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy twinturboV8 --strategy-path repos/TheoBrigitte_freqtrade/strategies/twinturbov8 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/twinturboV8-e01abfe2 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy twinturboV8 --strategy-path user_data/profile_bias_strategies/twinturboV8 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy twinturboV8 --strategy-path user_data/profile_bias_strategies/twinturboV8 --timerange 20190101-20190401 --no-color
  ```
- `twinturboV8_2`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy twinturboV8_2 --strategy-path repos/TheoBrigitte_freqtrade/strategies/twinturbov8 --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/twinturboV8_2-bd25893d --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy twinturboV8_2 --strategy-path user_data/profile_bias_strategies/twinturboV8_2 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy twinturboV8_2 --strategy-path user_data/profile_bias_strategies/twinturboV8_2 --timerange 20190101-20190401 --no-color
  ```
- `ultratank`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy ultratank --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/ultratank" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ultratank-1dfe916a --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ultratank --strategy-path user_data/profile_bias_strategies/ultratank --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ultratank --strategy-path user_data/profile_bias_strategies/ultratank --timerange 20190101-20190401 --no-color
  ```
- `wavetrend`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy wavetrend --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/_wavetrend" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/wavetrend-5900a358 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy wavetrend --strategy-path user_data/profile_bias_strategies/wavetrend --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy wavetrend --strategy-path user_data/profile_bias_strategies/wavetrend --timerange 20190101-20190401 --no-color
  ```
- `wavetrend_rsi`
  ```
  backtest   [recorded] freqtrade backtesting --config profile_spot_config.json --strategy wavetrend_rsi --strategy-path "repos/hamidreza07_freqai-strategy/startegy test/4/wavetrend_rsi" --timerange 20200401-20260821 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/wavetrend_rsi-32bf6591 --cache none
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy wavetrend_rsi --strategy-path user_data/profile_bias_strategies/wavetrend_rsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy wavetrend_rsi --strategy-path user_data/profile_bias_strategies/wavetrend_rsi --timerange 20190101-20190401 --no-color
  ```

## Convergence candidates - 1 strategies

A warm-up exists at which every indicator stays inside the band.
That is not admission: the paired full-window run must still show
an identical trade list.

| Strategy | Profile | Chosen warm-up | Worst drift | Tested | Results |
|---|---|---|---|---|---|
| `Schism2MM` | `spot_long` | 288 candles | 0.0% on `rmi-slow` | 2026-09-15 22:06:35 | `user_data/convergence_logs/Schism2MM-ladder.log` |

## Pending - 43 strategies

No hard failure and no verdict. Evidence is missing, which is
neither a pass nor a fail.

`AlexBandSniperV10AI`, `AlexBandSniperV58COptuna`, `AlexNexusForgeV8AIV4_SPOT`, `BaseStrategy`
`Danke`, `DevilStra`, `ExponentialGradientPortfolio`, `FisherBBDynamic`
`FreqAIHybridStrategy`, `GRIDDMIPRICEStrategyFutureV3`, `GRIDDMIPRICEStrategyFutureV4`, `GRIDDMIPRICEStrategyFutureV5`
`Guacamole`, `HarmonicDivergence`, `HarmonicDivergence_fix`, `HurstCycleV5`
`Kamaflage`, `LongShortRangeTradingMachetesV1`, `MartyEMA`, `Matrix`
`MultiMA_TSL5`, `NNTC_fbb_AdditiveAttention`, `NewsHeliusBitqueryML`, `ONS_Portfolio`
`Obelisk_3EMA_StochRSI_ATR`, `Proton`, `QuatreMousquetaires`, `RebalanceStrategySpot`
`Solipsis`, `Solipsis_USD`, `Solipsis_v4`, `TPActivatingTSLwithInitialTSLStrategy`
`TPActivatingTSLwithSLStrategy`, `TrailingStopLossStrategy`, `UltraSmartStrategy`, `ViNBuyPct`
`ViNBuyPctLc2`, `ViNBuyVws`, `degen`, `el_extrema_RL`
`epretrace`, `haGradient`, `tbedit`

## Exclusion unconfirmed - 8 strategies

`excluded` is a verdict, and this audit does not issue one on
somebody else's measurement or on the absence of one. These rows
would have been excluded on exactly that, so they are held here
until a measurement of ours settles them either way. Nothing about
them is hidden by the change of name: the decisive reason and the
basis stay on the row, and the work that would settle it is in
`open_work`.

| Held on | Basis | Strategies |
|---|---|---:|
| `no_verdict_on_lookahead` | `no_finding` | 7 |
| `recursive_bias_unverified` | `no_finding` | 1 |

This is not a softening. A row here may well end up excluded - the
38 held on an inherited look-ahead finding probably will, because a
limited environment does not invent bias. It ends up there on our
own evidence or not at all.

## Not passing - 546 strategies, by decisive reason

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
| `own_measurement` | a disqualifying result measured here, from this implementation | 504 |

Only `own_measurement` is a closed case. The other three carry the
work that would settle them in `open_work`, and the selftest fails if
one of them carries none.

| Reason | Meaning | Strategies |
|---|---|---:|
| `lookahead_found` | reads data it could not have had at the time | 156 |
| `recursive_bias_found` | indicator value still drifts at every warm-up the ladder can reach | 86 |
| `no_trades_in_full_measurement` | never trades over the full window | 7 |
| `full_backtest_not_testable` | the canonical pooled full backtest did not complete under the fixed runtime budget | 34 |
| `repair_refused_would_invent_strategy` | declares no timeframe, no stoploss, no exit logic, or names a model that no longer exists and cannot be restored; supplying one would measure our invention rather than the author's strategy | 51 |
| `local_module_repair_exhausted` | imports a helper the author shipped beside it; every candidate copy in the corpus either fails to import, would shadow an installed package, or imports cleanly but does not define what the strategy calls | 15 |
| `measured_only_in_freqai_arm` | runs only under its author's own FreqAI configuration, measured separately in that arm; not comparable with the ordinary spot audit | 6 |
| `third_party_package_declined` | needs a Python package this runtime does not install; declined because installing one changes the runtime every other strategy runs under, owner's call 2026-09-04 | 30 |
| `shared_runtime_change_declined` | the fix is understood - pandas' or numpy's own type-coercion rules have tightened - but applying it would touch every strategy's column writes, not just this row's; declined, owner's call 2026-09-04 | 11 |
| `duplicate_implementation` | duplicates the executable code of a retained representative - either confirmed further by an identical canonical full-backtest trade set, or, since 2026-09-16, by code identity alone once no config overlay and no measured disagreement stand against it (see evidence_rule in SEMANTIC_DUPLICATE_ADJUDICATION.json for which applied to a given row) | 91 |
| `recursive_check_incomplete_at_longest_rungs` | - | 13 |
| `repeated_timeout_after_exhausted_repair` | - | 4 |
| `user_policy_excluded_after_triage` | - | 42 |


### Reason by wave

| Reason | `-` | `A_pending_diagnostics` | `B_warmup_refusal` | `C_measurement_recovery` | `D_recursive_drift` | `E0_strict67` | `not_scheduled` |
|---|---|---|---|---|---|---|---|
| `lookahead_found` | 79 | 1 | 0 | 15 | 0 | 0 | 61 |
| `recursive_bias_found` | 24 | 0 | 3 | 18 | 14 | 1 | 26 |
| `no_trades_in_full_measurement` | 1 | 0 | 0 | 6 | 0 | 0 | 0 |
| `full_backtest_not_testable` | 14 | 0 | 0 | 17 | 0 | 1 | 2 |
| `repair_refused_would_invent_strategy` | 9 | 1 | 0 | 37 | 0 | 0 | 4 |
| `local_module_repair_exhausted` | 7 | 0 | 0 | 8 | 0 | 0 | 0 |
| `measured_only_in_freqai_arm` | 0 | 0 | 0 | 5 | 0 | 0 | 1 |
| `third_party_package_declined` | 18 | 0 | 0 | 12 | 0 | 0 | 0 |
| `shared_runtime_change_declined` | 4 | 0 | 0 | 6 | 0 | 0 | 1 |
| `duplicate_implementation` | 86 | 1 | 0 | 2 | 0 | 0 | 2 |
| `recursive_check_incomplete_at_longest_rungs` | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| `repeated_timeout_after_exhausted_repair` | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `user_policy_excluded_after_triage` | 41 | 0 | 0 | 1 | 0 | 0 | 0 |

### `lookahead_found` - 156

Reads data it could not have had at the time.

Wave `-` - 79:

`AdvancedFuturesSwingStrategy`, `AlexBattleTankKillerV4`, `AlexNexusForgeV8AIV2`, `Anomaly`
`Auto_EI_t4c0s_Shorts`, `AwesomeEWOLambo`, `AwesomeEWOLambo_Shorts`, `CsMom`
`DonchianChannel`, `EI4_t4c0s_V2_2_Shorts`, `GKD_FisherTransformV4_ML`, `LiquiditySweep`
`NNPredict_AdditiveAttention`, `NNPredict_CNN`, `NNPredict_GRU`, `NNPredict_LSTM2`
`NNPredict_LSTM3`, `NNPredict_MLP`, `NNPredict_Multihead`, `NNPredict_TCN`
`NNPredict_Wavenet`, `NNPredict_Wavenet2`, `NNTC_adx2_LSTM`, `NNTC_adx3_LSTM`
`NNTC_all_LSTM`, `NNTC_aroon_LSTM`, `NNTC_bbw_LSTM`, `NNTC_dwt2_LSTM`
`NNTC_dwt_LSTM`, `NNTC_fbb_Attention`, `NNTC_fbb_Ensemble`, `NNTC_fbb_GRU`
`NNTC_fbb_LSTM`, `NNTC_fbb_Multihead`, `NNTC_fbb_Wavenet`, `NNTC_fwr_LSTM`
`NNTC_highlow_Ensemble`, `NNTC_highlow_LSTM`, `NNTC_jump_Ensemble`, `NNTC_jump_LSTM`
`NNTC_macd2_Attention`, `NNTC_macd3_LSTM`, `NNTC_macd_Attention`, `NNTC_macd_Ensemble`
`NNTC_macd_GRU`, `NNTC_macd_LSTM`, `NNTC_macd_Multihead`, `NNTC_mfi_LSTM`
`NNTC_minmax_LSTM`, `NNTC_nseq_Attention`, `NNTC_nseq_Ensemble`, `NNTC_nseq_GRU`
`NNTC_nseq_LSTM`, `NNTC_nseq_Wavenet`, `NNTC_over_LSTM`, `NNTC_profit_AdditiveAttention`
`NNTC_profit_Attention`, `NNTC_profit_CNN`, `NNTC_profit_Ensemble`, `NNTC_profit_GRU`
`NNTC_profit_LSTM`, `NNTC_profit_LSTM2`, `NNTC_profit_LSTM3`, `NNTC_profit_MLP`
`NNTC_profit_Wavenet`, `NNTC_pv_Ensemble`, `NNTC_pv_LSTM`, `NNTC_pv_MLP`
`NNTC_pv_Wavenet`, `NNTC_slope_LSTM`, `NNTC_smooth_LSTM`, `NNTC_stochastic_LSTM`
`NNTC_swing_LSTM`, `OsirisXRSI`, `PCA`, `SMAoffset_antipump_div`
`StarRise_V3`, `UziChanTB`, `ichiV1_plus`

Wave `A_pending_diagnostics` - 1:

`kalthetank`

Wave `C_measurement_recovery` - 15:

`ARIMASTR`, `ARIMA_15`, `BestSingleAssetPortfolio`, `FastSupertrend`
`FreqaiExampleStrategy`, `MKR`, `NostalgiaForInfinityNext_ChangeToTower_V5_2`, `NostalgiaForInfinityNext_ChangeToTower_V5_3`
`NostalgiaForInfinityNext_ChangeToTower_V6`, `NostalgiaForInfinityXw`, `Stinkfist`, `SuperTrendPure`
`bbema`, `beta_factors_model`, `ichiV1_Marius`

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

### `recursive_bias_found` - 86

Indicator value still drifts at every warm-up the ladder can reach.

Wave `-` - 24:

`AlexStrategyFinalV8Hyper`, `AlexStrategyFinalV9Hyper`, `ClucHAnix_BB_RPB_MOD2_ROI_DYNAMIC_TB`, `ClucHAnix_BB_RPB_MOD_CTT_STB`
`ClucHAnix_BB_RPB_MOD_E0V1E_ROI_DYNAMIC_TB`, `DWT_Predict`, `DWT_Predict2`, `GRIDDMIPRICEStrategyFutureV2`
`GRIDDMIPRICEStrategyFutureV2Both`, `GRIDDMIPRICEStrategyFutureV2Long`, `GRIDDMIPRICEStrategyFutureV2Short`, `GRIDDMIPRICEStrategyFutureV6`
`HPStrategy_12_27`, `Kalman`, `Lmao`, `MtfScalper`
`NFIX7Risk`, `NostalgiaForInfinityX8`, `SuperReversal_mtf`, `TryEverything`
`UltimateAlphaV16`, `mind`, `momentum_tf_divergence`, `newstrategy4`

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

Wave `-` - 1:

`SimpleStrategy`

Wave `C_measurement_recovery` - 6:

`BreakEven`, `DoesNothingStrategy`, `Miku_PP_v3`, `MyStrategyTemplate`
`ViN`, `ep3mas2`

### `full_backtest_not_testable` - 34

The canonical pooled full backtest did not complete under the fixed runtime budget.

Wave `-` - 14:

`BTCBigDrop`, `BTCJump`, `BTCNDrop`, `BTCNSeq`
`ClucHAnixV2`, `ComboHold`, `DCADMIPRICEStrategySpot`, `DCAGRID`
`GRIDDMIPRICEStrategyFuture`, `GRIDDMIPRICEStrategyFutureV7`, `SARIMAX`, `Schism_BTC`
`Schism_ETH`, `TrailingBuyStratClucBBRPBMODE`

Wave `C_measurement_recovery` - 17:

`BBRSIS`, `MultiMA_TSL3`, `MultiMA_TSL3_Mod`, `MultiRSI`
`NFI731_BUSD`, `NFIX_BB_RPB`, `NFIX_BB_RPB_c7c477d_20211030`, `NfiNextModded`
`NostalgiaForInfinityNext`, `ObeliskIM_v1_1`, `ObeliskRSI_v6_1`, `Obelisk_Ichimoku_Slow_v1_3`
`Obelisk_Ichimoku_ZEMA_v1`, `Pmax`, `Supertrend`, `pmaxTest`
`slownsteady`

Wave `E0_strict67` - 1:

`BuyRegions`

Wave `not_scheduled` - 2:

`A9AV`, `Schism5`

### `repair_refused_would_invent_strategy` - 51

Declares no timeframe, no stoploss, no exit logic, or names a model that no longer exists and cannot be restored; supplying one would measure our invention rather than the author's strategy.

Wave `-` - 9:

`DELTA_NEUTRAL`, `E0V1EAI`, `EMA003`, `FBB_2`
`FBB_ROI`, `FreqaiBinaryClassStrategy`, `FreqaiStrategy_v2`, `TaSearchLevelG15m`
`TrendMomoClassifier`

Wave `A_pending_diagnostics` - 1:

`TGMA`

Wave `C_measurement_recovery` - 37:

`AdaptiveRenkoStrategy`, `Astro`, `AutoArimaTripleV1`, `BinanceStream`
`BlueEyes_MPP_v1`, `Chained`, `ClucCrypROI`, `ClucCrypSlow`
`ClucHAnix_BB_RPB_TraNz`, `CryptoFrogNFI2`, `CryptoPredictionTraining`, `EnsembleStrategy`
`EnsembleStrategyV1`, `EnsembleStrategyV2`, `FileLoadingStrategy`, `FreqaiExampleHybridStrategy`
`GodStra`, `GymStrategy`, `HLHB`, `LitmusGoodMinMaxClassificationStrategy`
`LitmusMetaStrategy`, `MasterMoniGoManiHyperStrategy`, `MultiMa`, `MultiTargetClassifierTestStrategy`
`MultiTargetRegressorTestStrategy`, `NoLost`, `PolymarketLogicalArbStrategy`, `Prediction_Strategy`
`QuickAdapterV3`, `RLAgentStrategy`, `RenkoYolo`, `ScalpingCCI`
`SimpleRiskFilterStrategy`, `TrainCatBoostStrategy`, `TuplaBollinger`, `UpSliceStrategy`
`thetank2`

Wave `not_scheduled` - 4:

`MyStrategyNew10`, `NowoIchimoku1hV1`, `Schism6`, `tacos1`

### `local_module_repair_exhausted` - 15

Imports a helper the author shipped beside it; every candidate copy in the corpus either fails to import, would shadow an installed package, or imports cleanly but does not define what the strategy calls.

Wave `-` - 7:

`NNPredict_Attention`, `NNPredict_NBeats`, `NNPredict_NHiTS`, `NNPredict_NLinear`
`NNPredict_Ray`, `NNPredict_TFT`, `NNPredict_dTransformer`

Wave `C_measurement_recovery` - 8:

`AdvancedRiskFilterStrategy`, `BB_RPB_3c`, `DWT`, `DualModelPolymarketPortfolio`
`MlpSpeculativeStrategy`, `Solipsis4`, `Solipsis6`, `SolipsisMM`

### `measured_only_in_freqai_arm` - 6

Runs only under its author's own freqai configuration, measured separately in that arm; not comparable with the ordinary spot audit.

Wave `C_measurement_recovery` - 5:

`RLStrategy`, `TankAi`, `TankAiRevival`, `WTAI`
`WTRSIAI`

Wave `not_scheduled` - 1:

`AstroQAV4`

### `third_party_package_declined` - 30

Needs a python package this runtime does not install; declined because installing one changes the runtime every other strategy runs under, owner's call 2026-09-04.

Wave `-` - 18:

`Cenderawasih_freqai`, `HMMv3`, `Solipsis3_BTC`, `Solipsis3_ETH`
`Solipsis4_BTC`, `Solipsis4_ETH`, `Solipsis5_BTC`, `Solipsis5_ETH`
`Solipsis6_BTC`, `Solipsis6_ETH`, `SolipsisCon_BTC`, `SolipsisMM_BTC`
`SolipsisMM_ETH`, `Solipsis_BTC`, `Solipsis_ETH`, `TM3MultiClass`
`kac_index_v1`, `kac_index_v2`

Wave `C_measurement_recovery` - 12:

`CopyLitmusMinMaxBroadClassificationStrategy`, `Enchilada`, `KMM`, `LitmusEntryRollClassificationStrategy`
`LitmusMLDPStrategy`, `LitmusMinMaxBroadClassificationStrategy`, `LitmusMinMaxClassificationStrategy`, `LitmusMinMaxRegretClassificationStrategy`
`LitmusMinMaxSegmentClassificationStrategy`, `LitmusMinMaxStrategy`, `LitmusMinMaxTrendStrategy`, `LitmusSimpleStrategy`

### `shared_runtime_change_declined` - 11

The fix is understood - pandas' or numpy's own type-coercion rules have tightened - but applying it would touch every strategy's column writes, not just this row's; declined, owner's call 2026-09-04.

Wave `-` - 4:

`BBMod1DCA`, `BB_RPB_TSL_Tranz_TrailingBuy`, `CME`, `MultiMA_TSL3a`

Wave `C_measurement_recovery` - 6:

`GPR`, `MomentumRegimeBasket15m`, `MostOfAll`, `PnF`
`new_turtle`, `new_turtle_roi`

Wave `not_scheduled` - 1:

`DIV_v1`

### `duplicate_implementation` - 91

Duplicates the executable code of a retained representative - either confirmed further by an identical canonical full-backtest trade set, or, since 2026-09-16, by code identity alone once no config overlay and no measured disagreement stand against it (see evidence_rule in semantic_duplicate_adjudication.json for which applied to a given row).

Wave `-` - 86:

`Anomaly_adx`, `Anomaly_all`, `Anomaly_aroon`, `Anomaly_bbw`
`Anomaly_dwt`, `Anomaly_fbb`, `Anomaly_fwr`, `Anomaly_highlow`
`Anomaly_jump`, `Anomaly_macd`, `Anomaly_mfi`, `Anomaly_minmax`
`Anomaly_nseq`, `Anomaly_over`, `Anomaly_profit`, `Anomaly_pv`
`Anomaly_slope`, `Anomaly_smooth`, `Anomaly_stochastic`, `Anomaly_swing`
`BBRSITV1`, `BBRSITV2`, `BBRSITV3`, `BB_RTR_dca`
`BinClucMadSMAv1`, `BinClucMadSMAv2`, `BinClucMadv1`, `BinClucMadv2`
`BlendBasket`, `Cluc4werk_ETH`, `Cluc5mDCA`, `Cluc5werk_BTC`
`Cluc5werk_ETH`, `Cluc5werk_USD`, `ClucCrypROI_BTC`, `ClucCrypROI_ETH`
`ClucCrypSlow_BTC`, `ClucCrypSlow_ETH`, `ClucDCA`, `ClucDCAV2`
`ClucHAwerk_BTC`, `ClucHAwerk_ETH`, `ClucHAwerk_USD`, `ConstantMixBasket`
`CppiBasket`, `EI3v2_tag_cofi_dca_green`, `Enchilada_Slow`, `Hacklemore_Slow`
`InverseVolBasket`, `Lateralus_Slow`, `LmaoStoplossClusterOpt`, `MinVarianceBasket`
`MomentumBasket`, `MomentumRegimeBasket15mFast`, `PCA_dwt`, `PCA_fbb`
`PCA_fwr`, `PCA_highlow`, `PCA_jump`, `PCA_macd`
`PCA_mfi`, `PCA_minmax`, `PCA_nseq`, `PCA_over`
`PCA_profit`, `PCA_pv`, `PCA_stochastic`, `PCA_swing`
`SMAOffsetProtectOptV1_1`, `Schism3_BTC`, `Schism3_ETH`, `Schism4_BTC`
`Schism4_ETH`, `Schism5_BTC`, `Schism5_ETH`, `Schism6_BTC`
`Schism6_ETH`, `Stinkfist_BTC`, `Stinkfist_ETH`, `SuperHV27_ETH`
`SuperReversal_mtf_5min`, `ViNSellCorr`, `ViNSellEps`, `ViNSellRiseCorrFall`
`ViNSellRiseFall`, `VolTargetBasket`

Wave `A_pending_diagnostics` - 1:

`HyperStra_GSN_SMAOnly`

Wave `C_measurement_recovery` - 2:

`FSupertrendStrategyETH`, `SuperHV27`

Wave `not_scheduled` - 2:

`FastSupertrend_optim3_rsi_75fix`, `NostalgiaForInfinityV7_SMAv2`

### `recursive_check_incomplete_at_longest_rungs` - 13

Wave `-` - 13:

`AlexStrategyFinalV8`, `AlexStrategyFinalV9`, `AntigravityStrategy`, `AntigravityStrategyV3`
`Bins`, `DWTHO`, `DWT_LongShortHO`, `ExampleLSTMStrategy`
`NNTC`, `TRIX_LS`, `avellaneda`, `delist_shorter_strategy`
`kijun_cross_strong_s`

### `repeated_timeout_after_exhausted_repair` - 4

Wave `-` - 4:

`MASlopeStrategy`, `MAStopLossStrategy`, `MATrailingStopLossStrategy`, `StopLossStrategy`

### `user_policy_excluded_after_triage` - 42

Wave `-` - 41:

`ARIMA_5`, `BBBHold`, `BB_RPB_TSL_Trailing`, `BaseNNStrategy`
`ClucHAnix_BB_RPB_MOD_CTT_DTB`, `CombinedBinHAndClucV4WS`, `LitmusBBStrategy`, `LitmusBBTrendStrategy`
`LitmusClucStrategy`, `LitmusSARStrategy`, `LitmusScalpStrategy`, `LitmusTrendScalpStrategy`
`LitmusVulcanStrategy`, `MoniGoManiHyperStrategy`, `NNPredict`, `NNPredict_LSTM`
`NNPredict_LSTM0`, `NNPredict_Transformer`, `NNPredict_kTFT`, `NNTC_adx_LSTM`
`NNTC_bbw_Transformer`, `NNTC_fbb_Transformer`, `NNTC_jump_Transformer`, `NNTC_macd_TCN`
`NNTC_macd_Transformer`, `NNTC_nseq_Transformer`, `NNTC_profit_Multihead`, `NNTC_profit_TCN`
`NNTC_profit_Transformer`, `NNTC_profit_Wavenet2`, `NNTC_profit_Wavenet3`, `NNTC_pv_Multihead`
`OBOnlyWSv2bband`, `SuperBuy`, `TS_Coeff`, `TS_Gain`
`TS_Wavelet`, `TrailingBuySellStrat`, `TrailingBuyStrat`, `TrailingBuyStrat2a`
`_Strat`

Wave `C_measurement_recovery` - 1:

`zorkv7_0_0`

## Expansion wave

| Wave | Strategies |
|---|---:|
| `(none)` | 460 |
| `not_scheduled` | 390 |
| `C_measurement_recovery` | 229 |
| `D_recursive_drift` | 121 |
| `B_warmup_refusal` | 82 |
| `E0_strict67` | 67 |
| `A_pending_diagnostics` | 7 |

## Open work

| Item | Strategies |
|---|---:|
| `lookahead_remeasure_pending` | 32 |
| `recursive_ladder_pending` | 28 |
| `needs_a_look` | 12 |
| `repair_attempted` | 3 |
| `to_be_fixed` | 3 |
| `convergence_inconclusive` | 1 |
| `repaired` | 1 |

Per-row detail, including every evidence path, is in
`STRATEGY_STATUS.csv`.
