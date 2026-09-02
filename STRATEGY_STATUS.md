# Strategy status - current evidence for all 900 rows

**Generated 2026-09-02 07:46:16 by `strategy_status.py`.** Regenerate it rather than editing it.

**This table decides nothing.** Admission happens only in
`eligibility_expansion_adjudicate.py`; this is a reading of what has
already been decided, collected from the smoke, bias, full-window,
adjudication and convergence stores.

`REGIME_ELIGIBILITY.csv` remains the frozen E0 baseline and is never
regenerated. Where this table and E0 disagree, E0 is not wrong: it is
the state at the freeze, and the difference is the expansion.

**On the run times.** The runners do not stamp a time into their
records, so `last_tested_at` is recovered from what they leave behind:
a result archive's filename, which carries the run's own clock, or
failing that a log file's modification time, which is close but is the
file's time and is labelled `log_mtime` for that reason. 229 of 900 rows
have neither and are left empty rather than given an invented time.

## Measurement

| | Strategies |
|---|---:|
| in the manifest | 900 |
| measured at all | 741 |
| produced trades | 711 |
| carrying a run time | 671 |

## Cohort

| Cohort | Strategies |
|---|---:|
| `E1_expanded` | 360 |
| `excluded` | 236 |
| `exclusion_unconfirmed` | 163 |
| `E0_strict67` | 67 |
| `not_tested_in_current_runtime` | 60 |
| `convergence_candidate` | 7 |
| `pending` | 7 |

## How freqtrade was called

A result is not reproducible from its verdict alone, so each row
carries the command it was produced by. **`recorded`** is the argv that
actually ran. **`reconstructed`** is derived from the run profile and
the window, because nothing stored the call before 2026-09-01; it is
labelled because a reconstruction is a different claim from a
recording. 460 of 2102 commands are recorded so far, and every new run
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

## Passing - 427 strategies

Every original gate returned `PASS`: measured in its native mode,
produced trades, clean look-ahead and recursion, complete candle
coverage, no published trap.

| Strategy | Profile | Cohort | Trades | Recursive evidence | Tested | Results |
|---|---|---|---:|---|---|---|
| `BBRSIv2` | `spot_long` | `E0_strict67` | 584 | `baseline` | - | - |
| `BigTrader` | `spot_long` | `E0_strict67` | 166 | `native` | - | - |
| `BigZ03` | `spot_long` | `E0_strict67` | 925 | `baseline` | - | - |
| `BigZ03HO` | `spot_long` | `E0_strict67` | 7275 | `baseline` | - | - |
| `BigZ04_TSL3` | `spot_long` | `E0_strict67` | 1643 | `native` | - | - |
| `BigZ04_TSL4` | `spot_long` | `E0_strict67` | 1756 | `baseline` | - | - |
| `BinClucMad` | `spot_long` | `E0_strict67` | 2517 | `baseline` | - | - |
| `BuyRegions` | `spot_long` | `E0_strict67` | 4672 | `baseline` | - | - |
| `Cluc7werk` | `spot_long` | `E0_strict67` | 1719 | `native` | - | - |
| `ClucHAnix_5M_E0V1E` | `spot_long` | `E0_strict67` | 5459 | `baseline` | - | - |
| `ClucHAnix_5m` | `spot_long` | `E0_strict67` | 2834 | `native` | - | - |
| `ClucHAnix_5m1` | `spot_long` | `E0_strict67` | 3049 | `native` | - | - |
| `ClucHAnix_5m_old` | `spot_long` | `E0_strict67` | 2834 | `baseline` | - | - |
| `ClucHAwerk` | `spot_long` | `E0_strict67` | 2183 | `native` | - | - |
| `CombinedBinHAndClucV3` | `spot_long` | `E0_strict67` | 2589 | `baseline` | - | - |
| `CombinedBinHAndClucV6` | `spot_long` | `E0_strict67` | 1724 | `native` | - | - |
| `CombinedBinHAndClucV7` | `spot_long` | `E0_strict67` | 889 | `native` | - | - |
| `CombinedBinHClucAndMADV3` | `spot_long` | `E0_strict67` | 1717 | `native` | - | - |
| `CombinedBinHClucAndMADV5` | `spot_long` | `E0_strict67` | 1644 | `baseline` | - | - |
| `CombinedBinHClucAndMADV6` | `spot_long` | `E0_strict67` | 1616 | `native` | - | - |
| `CombinedBinHClucAndMADV9` | `spot_long` | `E0_strict67` | 2842 | `native` | - | - |
| `EMA_CROSSOVER_STRATEGY` | `spot_long` | `E0_strict67` | 26980 | `baseline` | - | - |
| `ElliotV2` | `spot_long` | `E0_strict67` | 402 | `native` | - | - |
| `ElliotV5_SMA` | `spot_long` | `E0_strict67` | 723 | `native` | - | - |
| `FAdxSmaStrategy` | `futures_long_short` | `E0_strict67` | 15 | `native` | - | - |
| `FSupertrendStrategy` | `futures_long` | `E0_strict67` | 83 | `native` | - | - |
| `FastSupertrend_ts_origstop_fix` | `futures_long_short` | `E0_strict67` | 53 | `native` | - | - |
| `FlawlessVictory` | `spot_long` | `E0_strict67` | 12240 | `baseline` | - | - |
| `ForexSignal` | `spot_long` | `E0_strict67` | 26316 | `baseline` | - | - |
| `Gumbo1` | `spot_long` | `E0_strict67` | 23582 | `native` | - | - |
| `Ichimoku_v31` | `spot_long` | `E0_strict67` | 1564 | `native` | - | - |
| `Ichimoku_v37` | `spot_long` | `E0_strict67` | 507 | `native` | - | - |
| `KAMACCIRSI` | `spot_long` | `E0_strict67` | 10269 | `native` | - | - |
| `MACD_TRIPLE_MA` | `spot_long` | `E0_strict67` | 14845 | `native` | - | - |
| `MADisplaceV3` | `spot_long` | `E0_strict67` | 718 | `native` | - | - |
| `MacdStrategy` | `spot_long` | `E0_strict67` | 454 | `native` | - | - |
| `MarketChyperHyperStrategy` | `spot_long` | `E0_strict67` | 2406 | `native` | - | - |
| `NWEv6_new` | `spot_long` | `E0_strict67` | 8108 | `baseline` | - | - |
| `NostalgiaForInfinityV1` | `spot_long` | `E0_strict67` | 3457 | `native` | - | - |
| `NostalgiaForInfinityV2` | `spot_long` | `E0_strict67` | 825 | `native` | - | - |
| `PowerTower` | `spot_long` | `E0_strict67` | 5001 | `baseline` | - | - |
| `RegimeFilterStrategy` | `futures_long_short` | `E0_strict67` | 65 | `native` | - | - |
| `RobotradingBody` | `spot_long` | `E0_strict67` | 2895 | `baseline` | - | - |
| `SMAIP3` | `spot_long` | `E0_strict67` | 364 | `native` | - | - |
| `SMAOG` | `spot_long` | `E0_strict67` | 538 | `native` | - | - |
| `SMAOffsetV2` | `spot_long` | `E0_strict67` | 794 | `native` | - | - |
| `SampleStrategyV2` | `spot_long` | `E0_strict67` | 5882 | `native` | - | - |
| `Slowbro` | `spot_long` | `E0_strict67` | 95 | `native` | - | - |
| `StochRSITEMA` | `spot_long` | `E0_strict67` | 4542 | `native` | - | - |
| `StochasticCciStrategy` | `spot_long` | `E0_strict67` | 1325 | `baseline` | - | - |
| `TDSequentialStrategy` | `spot_long` | `E0_strict67` | 4587 | `native` | - | - |
| `TenderEnter` | `spot_long` | `E0_strict67` | 4027 | `baseline` | - | - |
| `TheRealPullbackV2` | `spot_long` | `E0_strict67` | 918 | `native` | - | - |
| `TrixStrategy` | `spot_long` | `E0_strict67` | 13554 | `native` | - | - |
| `TrixV15Strategy` | `spot_long` | `E0_strict67` | 1444 | `native` | - | - |
| `UltimateMomentumIndicator` | `spot_long` | `E0_strict67` | 8147 | `native` | - | - |
| `XtraThicc` | `spot_long` | `E0_strict67` | 9167 | `native` | - | - |
| `adaptive_trend` | `spot_long` | `E0_strict67` | 322 | `native` | - | - |
| `bestV2` | `spot_long` | `E0_strict67` | 345 | `native` | - | - |
| `botbaby` | `spot_long` | `E0_strict67` | 12338 | `baseline` | - | - |
| `cryptotank` | `spot_long` | `E0_strict67` | 2312 | `baseline` | - | - |
| `cryptotankV5` | `spot_long` | `E0_strict67` | 4782 | `baseline` | - | - |
| `fahmibah` | `spot_long` | `E0_strict67` | 20943 | `baseline` | - | - |
| `momentum` | `futures_long_short` | `E0_strict67` | 682 | `native` | - | - |
| `momentum_long` | `spot_long` | `E0_strict67` | 15967 | `baseline` | - | - |
| `momentum_rsi` | `futures_long_short` | `E0_strict67` | 551 | `native` | - | - |
| `momentum_wick` | `futures_long_short` | `E0_strict67` | 361 | `native` | - | - |
| `ASDTSRockwellTrading` | `spot_long` | `E1_expanded` | 29952 | `convergence:288:warmup_supplied` | 2026-09-01 15:32:20 | [log](user_data/convergence_logs/ASDTSRockwellTrading-ladder.log) |
| `ActionZone` | `spot_long` | `E1_expanded` | 561 | `convergence:90:warmup_supplied` | 2026-09-01 12:59:33 | [log](user_data/convergence_logs/ActionZone-ladder.log) |
| `AdaptiveMAStrategy` | `spot_long` | `E1_expanded` | 3195 | `convergence:288:warmup_supplied` | 2026-09-01 12:07:18 | [log](user_data/convergence_logs/AdaptiveMAStrategy-ladder.log) |
| `AdxSmas` | `spot_long` | `E1_expanded` | 7004 | `convergence:336:warmup_supplied` | 2026-09-01 13:33:11 | [log](user_data/convergence_logs/AdxSmas-ladder.log) |
| `AdxSmasS` | `futures_short` | `E1_expanded` | 74 | `convergence:336:warmup_supplied` | 2026-09-01 13:34:00 | [log](user_data/convergence_logs/AdxSmasS-ladder.log) |
| `AdxStrengthStrategy` | `spot_long` | `E1_expanded` | 16952 | `convergence:288:warmup_supplied` | 2026-09-01 12:07:43 | [log](user_data/convergence_logs/AdxStrengthStrategy-ladder.log) |
| `AlligatorStrategy` | `spot_long` | `E1_expanded` | 1839 | `convergence:720:warmup_supplied` | 2026-09-01 13:00:43 | [log](user_data/convergence_logs/AlligatorStrategy-ladder.log) |
| `AlmgrenChrissStrategy` | `futures_long_short` | `E1_expanded` | 818 | `convergence:192:warmup_supplied` | 2026-09-01 13:01:08 | [log](user_data/convergence_logs/AlmgrenChrissStrategy-ladder.log) |
| `AlwaysBuy` | `spot_long` | `E1_expanded` | 32359 | `convergence:288:warmup_supplied` | 2026-09-01 23:39:39 | [log](user_data/convergence_logs/AlwaysBuy-ladder.log) |
| `AroonTrendStrategy` | `spot_long` | `E1_expanded` | 24271 | `convergence:288:warmup_supplied` | 2026-09-01 12:08:07 | [log](user_data/convergence_logs/AroonTrendStrategy-ladder.log) |
| `AtrTrailingStopStrategy` | `spot_long` | `E1_expanded` | 24938 | `convergence:288:warmup_supplied` | 2026-09-01 12:08:31 | [log](user_data/convergence_logs/AtrTrailingStopStrategy-ladder.log) |
| `AverageStrategy` | `spot_long` | `E1_expanded` | 2875 | `convergence:84:warmup_supplied` | 2026-09-01 13:34:48 | [log](user_data/convergence_logs/AverageStrategy-ladder.log) |
| `BBRSI2` | `spot_long` | `E1_expanded` | 24422 | `convergence:1440:warmup_supplied` | 2026-09-01 15:33:59 | [log](user_data/convergence_logs/BBRSI2-ladder.log) |
| `BBRSI21` | `spot_long` | `E1_expanded` | 5845 | `convergence:288:warmup_supplied` | 2026-09-01 15:34:51 | [log](user_data/convergence_logs/BBRSI21-ladder.log) |
| `BBRSI3366` | `spot_long` | `E1_expanded` | 26873 | `convergence:288:warmup_supplied` | 2026-09-01 15:35:41 | [log](user_data/convergence_logs/BBRSI3366-ladder.log) |
| `BBRSI4cust` | `spot_long` | `E1_expanded` | 22886 | `convergence:192:warmup_supplied` | 2026-09-01 12:08:55 | [log](user_data/convergence_logs/BBRSI4cust-ladder.log) |
| `BBRSINaiveStrategy` | `spot_long` | `E1_expanded` | 20022 | `convergence:192:warmup_supplied` | 2026-09-01 12:09:19 | [log](user_data/convergence_logs/BBRSINaiveStrategy-ladder.log) |
| `BBRSIOptim2020Strategy` | `spot_long` | `E1_expanded` | 34955 | `convergence:288:warmup_supplied` | 2026-09-01 12:09:44 | [log](user_data/convergence_logs/BBRSIOptim2020Strategy-ladder.log) |
| `BBRSIOptimStrategy` | `spot_long` | `E1_expanded` | 10697 | `convergence:288:warmup_supplied` | 2026-09-01 12:10:08 | [log](user_data/convergence_logs/BBRSIOptimStrategy-ladder.log) |
| `BBRSIOptimizedStrategy` | `spot_long` | `E1_expanded` | 33132 | `convergence:288:warmup_supplied` | 2026-09-01 13:02:19 | [log](user_data/convergence_logs/BBRSIOptimizedStrategy-ladder.log) |
| `BBRSIStrategy` | `spot_long` | `E1_expanded` | 12330 | `convergence:192:warmup_supplied` | 2026-09-01 12:10:32 | [log](user_data/convergence_logs/BBRSIStrategy-ladder.log) |
| `BBRSITV` | `spot_long` | `E1_expanded` | 420 | `convergence:2016:warmup_supplied` | 2026-09-01 13:02:44 | [log](user_data/convergence_logs/BBRSITV-ladder.log) |
| `BB_RPB_TSL_RNG` | `spot_long` | `E1_expanded` | 778 | `convergence:2016:warmup_supplied` | 2026-09-01 13:35:37 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG-ladder.log) |
| `BB_RPB_TSL_RNG_2` | `spot_long` | `E1_expanded` | 776 | `convergence:2016:warmup_supplied` | 2026-09-01 15:36:32 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG_2-ladder.log) |
| `BB_RPB_TSL_RNG_TBS` | `spot_long` | `E1_expanded` | 778 | `convergence:2016:warmup_supplied` | 2026-09-01 13:36:25 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG_TBS-ladder.log) |
| `BB_RPB_TSL_RNG_TBS_GOLD` | `spot_long` | `E1_expanded` | 969 | `convergence:2016:warmup_supplied` | 2026-09-01 13:37:28 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG_TBS_GOLD-ladder.log) |
| `BB_RPB_TSL_RNG_VWAP` | `spot_long` | `E1_expanded` | 1289 | `convergence:2016:warmup_supplied` | 2026-09-01 12:10:58 | [log](user_data/convergence_logs/BB_RPB_TSL_RNG_VWAP-ladder.log) |
| `BB_RTR` | `spot_long` | `E1_expanded` | 987 | `convergence:2016:warmup_supplied` | 2026-09-01 12:11:28 | [log](user_data/convergence_logs/BB_RTR-ladder.log) |
| `BBands` | `spot_long` | `E1_expanded` | 7063 | `convergence:1440:warmup_supplied` | 2026-09-01 13:04:20 | [log](user_data/convergence_logs/BBands-ladder.log) |
| `BBandsRSI` | `spot_long` | `E1_expanded` | 24684 | `convergence:288:warmup_supplied` | 2026-09-01 13:04:45 | [log](user_data/convergence_logs/BBandsRSI-ladder.log) |
| `BBlower` | `spot_long` | `E1_expanded` | 1790 | `convergence:576:warmup_supplied` | 2026-09-01 15:37:20 | [log](user_data/convergence_logs/BBlower-ladder.log) |
| `Babico_SMA5xBBmid` | `spot_long` | `E1_expanded` | 79 | `convergence:30:warmup_supplied` | 2026-09-01 13:38:15 | [log](user_data/convergence_logs/Babico_SMA5xBBmid-ladder.log) |
| `Bandtastic` | `spot_long` | `E1_expanded` | 28745 | `convergence:1344:warmup_supplied` | 2026-09-01 15:38:10 | [log](user_data/convergence_logs/Bandtastic-ladder.log) |
| `BbWidthExpansionStrategy` | `spot_long` | `E1_expanded` | 21692 | `convergence:288:warmup_supplied` | 2026-09-01 12:11:52 | [log](user_data/convergence_logs/BbWidthExpansionStrategy-ladder.log) |
| `BbandRsi` | `spot_long` | `E1_expanded` | 16106 | `convergence:1440:warmup_supplied` | 2026-09-01 16:31:44 | [log](user_data/convergence_logs/BbandRsi-ladder.log) |
| `BbandRsiRolling` | `spot_long` | `E1_expanded` | 17916 | `convergence:288:warmup_supplied` | 2026-09-01 13:39:54 | [log](user_data/convergence_logs/BbandRsiRolling-ladder.log) |
| `BigZ07Next` | `spot_long` | `E1_expanded` | 1754 | `convergence:2016:warmup_supplied` | 2026-09-01 12:15:15 | [log](user_data/convergence_logs/BigZ07Next-ladder.log) |
| `BigZ07Next2` | `spot_long` | `E1_expanded` | 1716 | `convergence:2016:warmup_supplied` | 2026-09-01 12:15:43 | [log](user_data/convergence_logs/BigZ07Next2-ladder.log) |
| `BinClucMadV1` | `spot_long` | `E1_expanded` | 1164 | `convergence:2016:warmup_supplied` | 2026-09-01 12:16:09 | [log](user_data/convergence_logs/BinClucMadV1-ladder.log) |
| `BinHV27` | `spot_long` | `E1_expanded` | 11503 | `convergence:576:warmup_supplied` | 2026-09-01 13:40:42 | [log](user_data/convergence_logs/BinHV27-ladder.log) |
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
| `CCI_BB` | `spot_long` | `E1_expanded` | 926 | `convergence:288:warmup_supplied` | 2026-09-01 23:51:00 | [log](user_data/convergence_logs/CCI_BB-ladder.log) |
| `CMCWinner` | `spot_long` | `E1_expanded` | 6632 | `convergence:672:warmup_supplied` | 2026-09-01 13:42:18 | [log](user_data/convergence_logs/CMCWinner-ladder.log) |
| `CTIBS` | `spot_long` | `E1_expanded` | 5553 | `convergence:672:warmup_supplied` | 2026-09-01 12:18:16 | [log](user_data/convergence_logs/CTIBS-ladder.log) |
| `Candle2` | `spot_long` | `E1_expanded` | 7626 | `convergence:168:warmup_supplied` | 2026-09-01 15:39:47 | [log](user_data/convergence_logs/Candle2-ladder.log) |
| `CciMeanReversionStrategy` | `spot_long` | `E1_expanded` | 26207 | `convergence:576:warmup_supplied` | 2026-09-01 12:18:42 | [log](user_data/convergence_logs/CciMeanReversionStrategy-ladder.log) |
| `ChaikinMoneyFlowStrategy` | `spot_long` | `E1_expanded` | 29264 | `convergence:288:warmup_supplied` | 2026-09-01 12:19:08 | [log](user_data/convergence_logs/ChaikinMoneyFlowStrategy-ladder.log) |
| `Chandem` | `spot_long` | `E1_expanded` | 16308 | `convergence:2016:warmup_supplied` | 2026-09-01 15:40:37 | [log](user_data/convergence_logs/Chandem-ladder.log) |
| `Chandemtwo` | `spot_long` | `E1_expanded` | 18812 | `convergence:2016:warmup_supplied` | 2026-09-01 15:41:25 | [log](user_data/convergence_logs/Chandemtwo-ladder.log) |
| `Cluc4` | `spot_long` | `E1_expanded` | 4881 | `convergence:1440:warmup_supplied` | 2026-09-01 15:42:17 | [log](user_data/convergence_logs/Cluc4-ladder.log) |
| `Cluc4werk` | `spot_long` | `E1_expanded` | 3269 | `convergence:1440:warmup_supplied` | 2026-09-01 13:43:54 | [log](user_data/convergence_logs/Cluc4werk-ladder.log) |
| `Cluc5werk` | `spot_long` | `E1_expanded` | 2210 | `convergence:1440:warmup_supplied` | 2026-09-01 13:44:44 | [log](user_data/convergence_logs/Cluc5werk-ladder.log) |
| `ClucFiatROI` | `spot_long` | `E1_expanded` | 6026 | `convergence:288:warmup_supplied` | 2026-09-01 13:11:38 | [log](user_data/convergence_logs/ClucFiatROI-ladder.log) |
| `ClucFiatSlow` | `spot_long` | `E1_expanded` | 6026 | `convergence:288:warmup_supplied` | 2026-09-01 13:12:03 | [log](user_data/convergence_logs/ClucFiatSlow-ladder.log) |
| `ClucHAnix_hhll` | `spot_long` | `E1_expanded` | 2278 | `convergence:2016:warmup_supplied` | 2026-09-01 13:12:56 | [log](user_data/convergence_logs/ClucHAnix_hhll-ladder.log) |
| `ClucMay72018` | `spot_long` | `E1_expanded` | 2507 | `convergence:288:warmup_supplied` | 2026-09-01 13:46:34 | [log](user_data/convergence_logs/ClucMay72018-ladder.log) |
| `CofiBitStrategy` | `spot_long` | `E1_expanded` | 27444 | `convergence:288:warmup_supplied` | 2026-09-01 13:47:22 | [log](user_data/convergence_logs/CofiBitStrategy-ladder.log) |
| `CombinedBinHAndCluc` | `spot_long` | `E1_expanded` | 3540 | `convergence:288:warmup_supplied` | 2026-09-01 13:48:09 | [log](user_data/convergence_logs/CombinedBinHAndCluc-ladder.log) |
| `CombinedBinHAndCluc2021` | `spot_long` | `E1_expanded` | 3297 | `convergence:288:warmup_supplied` | 2026-09-01 13:48:57 | [log](user_data/convergence_logs/CombinedBinHAndCluc2021-ladder.log) |
| `CombinedBinHAndCluc2021Bull` | `spot_long` | `E1_expanded` | 3876 | `convergence:288:warmup_supplied` | 2026-09-01 13:49:45 | [log](user_data/convergence_logs/CombinedBinHAndCluc2021Bull-ladder.log) |
| `CombinedBinHAndClucHyperV0` | `spot_long` | `E1_expanded` | 4252 | `convergence:1440:warmup_supplied` | 2026-09-01 15:43:08 | [log](user_data/convergence_logs/CombinedBinHAndClucHyperV0-ladder.log) |
| `CombinedBinHAndClucHyperV3` | `spot_long` | `E1_expanded` | 1810 | `convergence:1440:warmup_supplied` | 2026-09-01 15:43:59 | [log](user_data/convergence_logs/CombinedBinHAndClucHyperV3-ladder.log) |
| `CombinedBinHAndClucV2` | `spot_long` | `E1_expanded` | 728 | `convergence:576:warmup_supplied` | 2026-09-01 13:15:19 | [log](user_data/convergence_logs/CombinedBinHAndClucV2-ladder.log) |
| `CombinedBinHAndClucV4` | `spot_long` | `E1_expanded` | 2965 | `convergence:288:warmup_supplied` | 2026-09-01 13:15:44 | [log](user_data/convergence_logs/CombinedBinHAndClucV4-ladder.log) |
| `CombinedBinHAndClucV5` | `spot_long` | `E1_expanded` | 2985 | `convergence:288:warmup_supplied` | 2026-09-01 13:16:09 | [log](user_data/convergence_logs/CombinedBinHAndClucV5-ladder.log) |
| `CombinedBinHAndClucV5Hyperoptable` | `spot_long` | `E1_expanded` | 2705 | `convergence:288:warmup_supplied` | 2026-09-01 12:21:09 | [log](user_data/convergence_logs/CombinedBinHAndClucV5Hyperoptable-ladder.log) |
| `CombinedBinHAndClucV8` | `spot_long` | `E1_expanded` | 884 | `convergence:2016:warmup_supplied` | 2026-09-01 13:16:34 | [log](user_data/convergence_logs/CombinedBinHAndClucV8-ladder.log) |
| `CombinedBinHAndClucV8Hyper` | `spot_long` | `E1_expanded` | 1243 | `convergence:2016:warmup_supplied` | 2026-09-01 13:16:59 | [log](user_data/convergence_logs/CombinedBinHAndClucV8Hyper-ladder.log) |
| `CombinedBinHAndClucV8XH` | `spot_long` | `E1_expanded` | 642 | `convergence:2016:warmup_supplied` | 2026-09-01 13:17:23 | [log](user_data/convergence_logs/CombinedBinHAndClucV8XH-ladder.log) |
| `CombinedBinHAndClucV8XHO` | `spot_long` | `E1_expanded` | 851 | `convergence:2016:warmup_supplied` | 2026-09-01 12:21:34 | [log](user_data/convergence_logs/CombinedBinHAndClucV8XHO-ladder.log) |
| `Combined_Indicators` | `spot_long` | `E1_expanded` | 2969 | `convergence:1440:warmup_supplied` | 2026-09-01 15:44:51 | [log](user_data/convergence_logs/Combined_Indicators-ladder.log) |
| `Combined_NFIv6_SMA` | `spot_long` | `E1_expanded` | 951 | `convergence:2016:warmup_supplied` | 2026-09-01 13:17:48 | [log](user_data/convergence_logs/Combined_NFIv6_SMA-ladder.log) |
| `Combined_NFIv7_SMA` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 12:22:00 | [log](user_data/convergence_logs/Combined_NFIv7_SMA-ladder.log) |
| `Combined_NFIv7_SMA_Rallipanos_20210707` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 12:22:25 | [log](user_data/convergence_logs/Combined_NFIv7_SMA_Rallipanos_20210707-ladder.log) |
| `Combined_NFIv7_SMA_bAdBoY_20211204` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 12:22:51 | [log](user_data/convergence_logs/Combined_NFIv7_SMA_bAdBoY_20211204-ladder.log) |
| `CompositeScoreStrategy` | `spot_long` | `E1_expanded` | 28771 | `convergence:288:warmup_supplied` | 2026-09-01 12:23:15 | [log](user_data/convergence_logs/CompositeScoreStrategy-ladder.log) |
| `ConsensusShort` | `futures_long_short` | `E1_expanded` | 414 | `convergence:288:warmup_supplied` | 2026-09-02 06:55:30 | [log](user_data/convergence_logs/ConsensusShort-ladder.log) |
| `CoppockCurveStrategy` | `spot_long` | `E1_expanded` | 22332 | `convergence:288:warmup_supplied` | 2026-09-01 12:23:39 | [log](user_data/convergence_logs/CoppockCurveStrategy-ladder.log) |
| `CrossEMAStrategy` | `spot_long` | `E1_expanded` | 4063 | `convergence:168:warmup_supplied` | 2026-09-01 13:18:36 | [log](user_data/convergence_logs/CrossEMAStrategy-ladder.log) |
| `CustomStoplossWithPSAR` | `spot_long` | `E1_expanded` | 140 | `convergence:24:warmup_supplied` | 2026-09-01 13:50:31 | [log](user_data/convergence_logs/CustomStoplossWithPSAR-ladder.log) |
| `DD` | `spot_long` | `E1_expanded` | 32051 | `convergence:288:warmup_supplied` | 2026-09-01 15:45:44 | [log](user_data/convergence_logs/DD-ladder.log) |
| `DWT_LongShort` | `futures_long_short` | `E1_expanded` | 859 | `convergence:288:warmup_supplied` | 2026-09-02 06:56:43 | [log](user_data/convergence_logs/DWT_LongShort-ladder.log) |
| `DWT_short` | `futures_long_short` | `E1_expanded` | 362 | `convergence:288:warmup_supplied` | 2026-09-02 06:57:53 | [log](user_data/convergence_logs/DWT_short-ladder.log) |
| `DemaCrossStrategy` | `spot_long` | `E1_expanded` | 21528 | `convergence:288:warmup_supplied` | 2026-09-01 12:24:04 | [log](user_data/convergence_logs/DemaCrossStrategy-ladder.log) |
| `Divergences` | `spot_long` | `E1_expanded` | 9981 | `convergence:2160:warmup_supplied` | 2026-09-01 13:21:26 | [log](user_data/convergence_logs/Divergences-ladder.log) |
| `DonchianBreakoutStrategy` | `spot_long` | `E1_expanded` | 21512 | `convergence:288:warmup_supplied` | 2026-09-01 12:24:28 | [log](user_data/convergence_logs/DonchianBreakoutStrategy-ladder.log) |
| `E0V1E` | `spot_long` | `E1_expanded` | 329 | `convergence:2016:warmup_supplied` | 2026-09-01 13:22:16 | [log](user_data/convergence_logs/E0V1E-ladder.log) |
| `E0V1E2` | `spot_long` | `E1_expanded` | 330 | `convergence:2016:warmup_supplied` | 2026-09-01 13:22:41 | [log](user_data/convergence_logs/E0V1E2-ladder.log) |
| `E0V1E_DCA3` | `spot_long` | `E1_expanded` | 2152 | `convergence:2016:warmup_supplied` | 2026-09-01 12:24:54 | [log](user_data/convergence_logs/E0V1E_DCA3-ladder.log) |
| `E0V1E_ewo` | `spot_long` | `E1_expanded` | 309 | `convergence:2016:warmup_supplied` | 2026-09-01 13:23:07 | [log](user_data/convergence_logs/E0V1E_ewo-ladder.log) |
| `E0V1E_protections` | `spot_long` | `E1_expanded` | 329 | `convergence:2016:warmup_supplied` | 2026-09-01 13:23:31 | [log](user_data/convergence_logs/E0V1E_protections-ladder.log) |
| `E0V1E_strs` | `spot_long` | `E1_expanded` | 134 | `convergence:288:warmup_supplied` | 2026-09-01 13:23:57 | [log](user_data/convergence_logs/E0V1E_strs-ladder.log) |
| `EMA50` | `spot_long` | `E1_expanded` | 5751 | `convergence:288:warmup_supplied` | 2026-09-01 13:24:21 | [log](user_data/convergence_logs/EMA50-ladder.log) |
| `EMA520015_V17` | `spot_long` | `E1_expanded` | 8265 | `convergence:540:warmup_supplied` | 2026-09-01 15:47:21 | [log](user_data/convergence_logs/EMA520015_V17-ladder.log) |
| `EMABreakout` | `spot_long` | `E1_expanded` | 5734 | `convergence:288:warmup_supplied` | 2026-09-01 13:24:46 | [log](user_data/convergence_logs/EMABreakout-ladder.log) |
| `EMASkipPump` | `spot_long` | `E1_expanded` | 34322 | `convergence:288:warmup_supplied` | 2026-09-01 13:53:49 | [log](user_data/convergence_logs/EMASkipPump-ladder.log) |
| `ElliotV4` | `spot_long` | `E1_expanded` | 915 | `convergence:2016:warmup_supplied` | 2026-09-01 13:25:34 | [log](user_data/convergence_logs/ElliotV4-ladder.log) |
| `ElliotV531` | `spot_long` | `E1_expanded` | 887 | `convergence:2016:warmup_supplied` | 2026-09-01 13:25:59 | [log](user_data/convergence_logs/ElliotV531-ladder.log) |
| `ElliotV5HO` | `spot_long` | `E1_expanded` | 810 | `convergence:2016:warmup_supplied` | 2026-09-01 13:26:23 | [log](user_data/convergence_logs/ElliotV5HO-ladder.log) |
| `ElliotV5HOMod2` | `spot_long` | `E1_expanded` | 494 | `convergence:2016:warmup_supplied` | 2026-09-01 13:26:48 | [log](user_data/convergence_logs/ElliotV5HOMod2-ladder.log) |
| `ElliotV5HOMod3` | `spot_long` | `E1_expanded` | 547 | `convergence:2016:warmup_supplied` | 2026-09-01 13:27:12 | [log](user_data/convergence_logs/ElliotV5HOMod3-ladder.log) |
| `ElliotV7` | `spot_long` | `E1_expanded` | 554 | `convergence:2016:warmup_supplied` | 2026-09-01 13:27:41 | [log](user_data/convergence_logs/ElliotV7-ladder.log) |
| `ElliotV8HO` | `spot_long` | `E1_expanded` | 386 | `convergence:2016:warmup_supplied` | 2026-09-01 13:28:05 | [log](user_data/convergence_logs/ElliotV8HO-ladder.log) |
| `EmaRibbonStrategy` | `spot_long` | `E1_expanded` | 22752 | `convergence:288:warmup_supplied` | 2026-09-01 12:25:20 | [log](user_data/convergence_logs/EmaRibbonStrategy-ladder.log) |
| `FOttStrategy` | `futures_long_short` | `E1_expanded` | 6447 | `convergence:672:warmup_supplied` | 2026-09-01 13:28:30 | [log](user_data/convergence_logs/FOttStrategy-ladder.log) |
| `FRAYSTRAT` | `spot_long` | `E1_expanded` | 12446 | `convergence:672:warmup_supplied` | 2026-09-01 13:28:54 | [log](user_data/convergence_logs/FRAYSTRAT-ladder.log) |
| `FReinforcedStrategy` | `futures_long_short` | `E1_expanded` | 80 | `convergence:2016:warmup_supplied` | 2026-09-02 06:59:03 | [log](user_data/convergence_logs/FReinforcedStrategy-ladder.log) |
| `FSampleStrategy` | `futures_long_short` | `E1_expanded` | 40 | `convergence:336:warmup_supplied` | 2026-09-01 13:29:43 | [log](user_data/convergence_logs/FSampleStrategy-ladder.log) |
| `FTT_DWT_FBB_FUTURES` | `futures_long_short` | `E1_expanded` | 941 | `convergence:576:warmup_supplied` | 2026-09-02 07:00:21 | [log](user_data/convergence_logs/FTT_DWT_FBB_FUTURES-ladder.log) |
| `FVGChannel` | `spot_long` | `E1_expanded` | 16599 | `convergence:2160:warmup_supplied` | 2026-09-01 15:49:04 | [log](user_data/convergence_logs/FVGChannel-ladder.log) |
| `FisherHull` | `spot_long` | `E1_expanded` | 34 | `convergence:1440:warmup_supplied` | 2026-09-01 13:54:39 | [log](user_data/convergence_logs/FisherHull-ladder.log) |
| `FisherTransformStrategy` | `spot_long` | `E1_expanded` | 22576 | `convergence:288:warmup_supplied` | 2026-09-01 12:25:45 | [log](user_data/convergence_logs/FisherTransformStrategy-ladder.log) |
| `FiveMinCrossAbove` | `spot_long` | `E1_expanded` | 1851 | `convergence:288:warmup_supplied` | 2026-09-01 13:55:28 | [log](user_data/convergence_logs/FiveMinCrossAbove-ladder.log) |
| `FrayStratBTC` | `spot_long` | `E1_expanded` | 9089 | `convergence:672:warmup_supplied` | 2026-09-01 13:55:52 | [log](user_data/convergence_logs/FrayStratBTC-ladder.log) |
| `Freqtrade_backtest_validation_freqtrade1` | `spot_long` | `E1_expanded` | 10164 | `convergence:48:warmup_supplied` | 2026-09-01 15:50:45 | [log](user_data/convergence_logs/Freqtrade_backtest_validation_freqtrade1-ladder.log) |
| `FrostAuraM115mStrategy` | `spot_long` | `E1_expanded` | 30851 | `convergence:192:warmup_supplied` | 2026-09-01 13:56:17 | [log](user_data/convergence_logs/FrostAuraM115mStrategy-ladder.log) |
| `FrostAuraM11hStrategy` | `spot_long` | `E1_expanded` | 2636 | `convergence:168:warmup_supplied` | 2026-09-01 13:56:41 | [log](user_data/convergence_logs/FrostAuraM11hStrategy-ladder.log) |
| `FrostAuraM21hStrategy` | `spot_long` | `E1_expanded` | 19880 | `convergence:192:warmup_supplied` | 2026-09-01 13:57:05 | [log](user_data/convergence_logs/FrostAuraM21hStrategy-ladder.log) |
| `FrostAuraM315mStrategy` | `spot_long` | `E1_expanded` | 9121 | `convergence:192:warmup_supplied` | 2026-09-01 13:57:30 | [log](user_data/convergence_logs/FrostAuraM315mStrategy-ladder.log) |
| `FrostAuraM31hStrategy` | `spot_long` | `E1_expanded` | 2469 | `convergence:168:warmup_supplied` | 2026-09-01 13:57:55 | [log](user_data/convergence_logs/FrostAuraM31hStrategy-ladder.log) |
| `GKD_Baseline` | `spot_long` | `E1_expanded` | 18338 | `convergence:168:warmup_supplied` | 2026-09-01 15:51:35 | [log](user_data/convergence_logs/GKD_Baseline-ladder.log) |
| `GKD_BaselineAllMAs` | `spot_long` | `E1_expanded` | 18338 | `convergence:168:warmup_supplied` | 2026-09-01 15:52:23 | [log](user_data/convergence_logs/GKD_BaselineAllMAs-ladder.log) |
| `GKD_HurstExponent` | `spot_long` | `E1_expanded` | 5896 | `convergence:168:warmup_supplied` | 2026-09-01 15:53:13 | [log](user_data/convergence_logs/GKD_HurstExponent-ladder.log) |
| `GKD_PFE` | `spot_long` | `E1_expanded` | 17113 | `convergence:168:warmup_supplied` | 2026-09-01 15:54:03 | [log](user_data/convergence_logs/GKD_PFE-ladder.log) |
| `GPTREV` | `spot_long` | `E1_expanded` | 600 | `convergence:1440:warmup_supplied` | 2026-09-01 14:01:43 | [log](user_data/convergence_logs/GPTREV-ladder.log) |
| `GodCard` | `spot_long` | `E1_expanded` | 476 | `convergence:288:warmup_supplied` | 2026-09-01 15:54:53 | [log](user_data/convergence_logs/GodCard-ladder.log) |
| `GoldenCrossStrategy` | `spot_long` | `E1_expanded` | 5920 | `convergence:2016:warmup_supplied` | 2026-09-01 12:26:10 | [log](user_data/convergence_logs/GoldenCrossStrategy-ladder.log) |
| `Hacklemost` | `spot_long` | `E1_expanded` | 168 | `convergence:288:warmup_supplied` | 2026-09-01 14:07:44 | [log](user_data/convergence_logs/Hacklemost-ladder.log) |
| `HansenSmaOffsetV1` | `spot_long` | `E1_expanded` | 119 | `convergence:96:warmup_supplied` | 2026-09-01 14:08:31 | [log](user_data/convergence_logs/HansenSmaOffsetV1-ladder.log) |
| `HeikinAshiStrategy` | `spot_long` | `E1_expanded` | 26155 | `convergence:288:warmup_supplied` | 2026-09-01 12:26:36 | [log](user_data/convergence_logs/HeikinAshiStrategy-ladder.log) |
| `HigherHighStrategy` | `spot_long` | `E1_expanded` | 26360 | `convergence:288:warmup_supplied` | 2026-09-01 12:27:00 | [log](user_data/convergence_logs/HigherHighStrategy-ladder.log) |
| `HilbertSineWave` | `spot_long` | `E1_expanded` | 4447 | `convergence:336:warmup_supplied` | 2026-09-01 15:56:37 | [log](user_data/convergence_logs/HilbertSineWave-ladder.log) |
| `HourBasedStrategy` | `spot_long` | `E1_expanded` | 10884 | `convergence:24:warmup_supplied` | 2026-09-01 14:09:19 | [log](user_data/convergence_logs/HourBasedStrategy-ladder.log) |
| `HourBasedStrategy_5m` | `spot_long` | `E1_expanded` | 11784 | `convergence:288:warmup_supplied` | 2026-09-01 23:55:49 | [log](user_data/convergence_logs/HourBasedStrategy_5m-ladder.log) |
| `Ichess` | `spot_long` | `E1_expanded` | 355 | `convergence:90:warmup_supplied` | 2026-09-01 14:15:39 | [log](user_data/convergence_logs/Ichess-ladder.log) |
| `Ichimoku` | `spot_long` | `E1_expanded` | 8609 | `convergence:288:warmup_supplied` | 2026-09-01 14:16:28 | [log](user_data/convergence_logs/Ichimoku-ladder.log) |
| `IchimokuSimpleStrategy` | `spot_long` | `E1_expanded` | 19831 | `convergence:288:warmup_supplied` | 2026-09-01 12:27:25 | [log](user_data/convergence_logs/IchimokuSimpleStrategy-ladder.log) |
| `ImpulseV1` | `spot_long` | `E1_expanded` | 1097 | `convergence:288:warmup_supplied` | 2026-09-01 12:27:51 | [log](user_data/convergence_logs/ImpulseV1-ladder.log) |
| `InformativeSample` | `spot_long` | `E1_expanded` | 15553 | `convergence:576:warmup_supplied` | 2026-09-01 14:17:18 | [log](user_data/convergence_logs/InformativeSample-ladder.log) |
| `Inverse` | `spot_long` | `E1_expanded` | 2470 | `convergence:720:warmup_supplied` | 2026-09-01 12:28:16 | [log](user_data/convergence_logs/Inverse-ladder.log) |
| `InverseV2` | `spot_long` | `E1_expanded` | 989 | `convergence:720:warmup_supplied` | 2026-09-01 12:28:42 | [log](user_data/convergence_logs/InverseV2-ladder.log) |
| `JuicyTrend` | `spot_long` | `E1_expanded` | 24136 | `convergence:1344:warmup_supplied` | 2026-09-01 15:57:25 | [log](user_data/convergence_logs/JuicyTrend-ladder.log) |
| `KAMACCIRSI_new` | `spot_long` | `E1_expanded` | 189 | `convergence:288:warmup_supplied` | 2026-09-01 12:29:09 | [log](user_data/convergence_logs/KAMACCIRSI_new-ladder.log) |
| `KC_BB` | `spot_long` | `E1_expanded` | 695 | `convergence:288:warmup_supplied` | 2026-09-01 15:58:17 | [log](user_data/convergence_logs/KC_BB-ladder.log) |
| `KeltnerChannelStrategy` | `spot_long` | `E1_expanded` | 16720 | `convergence:288:warmup_supplied` | 2026-09-01 12:29:34 | [log](user_data/convergence_logs/KeltnerChannelStrategy-ladder.log) |
| `LinearRegressionStrategy` | `spot_long` | `E1_expanded` | 24570 | `convergence:288:warmup_supplied` | 2026-09-01 12:29:59 | [log](user_data/convergence_logs/LinearRegressionStrategy-ladder.log) |
| `LuxOSC` | `spot_long` | `E1_expanded` | 14577 | `convergence:576:warmup_supplied` | 2026-09-01 14:19:26 | [log](user_data/convergence_logs/LuxOSC-ladder.log) |
| `MAC` | `spot_long` | `E1_expanded` | 52 | `convergence:90:warmup_supplied` | 2026-09-01 14:19:51 | [log](user_data/convergence_logs/MAC-ladder.log) |
| `MACDStrategy` | `spot_long` | `E1_expanded` | 20565 | `convergence:288:warmup_supplied` | 2026-09-01 14:22:14 | [log](user_data/convergence_logs/MACDStrategy-ladder.log) |
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
| `MACD_TRI_EMA` | `spot_long` | `E1_expanded` | 31828 | `convergence:288:warmup_supplied` | 2026-09-01 14:25:25 | [log](user_data/convergence_logs/MACD_TRI_EMA-ladder.log) |
| `MFI` | `spot_long` | `E1_expanded` | 20266 | `convergence:288:warmup_supplied` | 2026-09-01 14:26:13 | [log](user_data/convergence_logs/MFI-ladder.log) |
| `MacdAdxStrategy` | `spot_long` | `E1_expanded` | 27220 | `convergence:288:warmup_supplied` | 2026-09-01 12:30:24 | [log](user_data/convergence_logs/MacdAdxStrategy-ladder.log) |
| `MacdZeroCrossStrategy` | `spot_long` | `E1_expanded` | 29909 | `convergence:288:warmup_supplied` | 2026-09-01 14:23:48 | [log](user_data/convergence_logs/MacdZeroCrossStrategy-ladder.log) |
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
| `MultiMA_TSL3` | `spot_long` | `E1_expanded` | 15 | `convergence:2016:warmup_supplied` | 2026-08-31 15:13:04 | [archive](user_data/profile_smoke/MultiMA_TSL3-2026-08-31_15-13-04.zip) [log](user_data/convergence_logs/MultiMA_TSL3-ladder.log) |
| `MultiOffsetLamboV0` | `spot_long` | `E1_expanded` | 200 | `convergence:2016:warmup_supplied` | 2026-09-01 14:28:46 | [log](user_data/convergence_logs/MultiOffsetLamboV0-ladder.log) |
| `MyStratV1` | `spot_long` | `E1_expanded` | 684 | `convergence:2016:warmup_supplied` | 2026-09-01 12:32:52 | [log](user_data/convergence_logs/MyStratV1-ladder.log) |
| `NEWTEST15m` | `spot_long` | `E1_expanded` | 2644 | `convergence:672:warmup_supplied` | 2026-09-01 14:29:37 | [log](user_data/convergence_logs/NEWTEST15m-ladder.log) |
| `NFI46` | `spot_long` | `E1_expanded` | 77 | `convergence:2016:warmup_supplied` | 2026-09-01 14:30:04 | [log](user_data/convergence_logs/NFI46-ladder.log) |
| `NFI46FrogZ` | `spot_long` | `E1_expanded` | 16273 | `convergence:2016:warmup_supplied` | 2026-09-01 14:30:31 | [log](user_data/convergence_logs/NFI46FrogZ-ladder.log) |
| `NFI46Offset` | `spot_long` | `E1_expanded` | 941 | `convergence:2016:warmup_supplied` | 2026-09-01 14:30:57 | [log](user_data/convergence_logs/NFI46Offset-ladder.log) |
| `NFI46OffsetHOA1` | `spot_long` | `E1_expanded` | 1037 | `convergence:2016:warmup_supplied` | 2026-09-01 14:31:24 | [log](user_data/convergence_logs/NFI46OffsetHOA1-ladder.log) |
| `NFI46Z` | `spot_long` | `E1_expanded` | 699 | `convergence:2016:warmup_supplied` | 2026-09-01 14:31:53 | [log](user_data/convergence_logs/NFI46Z-ladder.log) |
| `NFI47V2` | `spot_long` | `E1_expanded` | 524 | `convergence:2016:warmup_supplied` | 2026-09-01 12:33:20 | [log](user_data/convergence_logs/NFI47V2-ladder.log) |
| `NFI5MOHO` | `spot_long` | `E1_expanded` | 378 | `convergence:2016:warmup_supplied` | 2026-09-01 14:32:21 | [log](user_data/convergence_logs/NFI5MOHO-ladder.log) |
| `NFI5MOHO2` | `spot_long` | `E1_expanded` | 1436 | `convergence:2016:warmup_supplied` | 2026-09-01 12:33:48 | [log](user_data/convergence_logs/NFI5MOHO2-ladder.log) |
| `NFI5MOHO_WIP` | `spot_long` | `E1_expanded` | 951 | `convergence:2016:warmup_supplied` | 2026-09-01 14:32:49 | [log](user_data/convergence_logs/NFI5MOHO_WIP-ladder.log) |
| `NFI5MOHO_WIP_1` | `spot_long` | `E1_expanded` | 976 | `convergence:2016:warmup_supplied` | 2026-09-01 12:34:16 | [log](user_data/convergence_logs/NFI5MOHO_WIP_1-ladder.log) |
| `NFI5MOHO_WIP_2` | `spot_long` | `E1_expanded` | 988 | `convergence:2016:warmup_supplied` | 2026-09-01 12:34:44 | [log](user_data/convergence_logs/NFI5MOHO_WIP_2-ladder.log) |
| `NFI7MOHO` | `spot_long` | `E1_expanded` | 1966 | `convergence:2016:warmup_supplied` | 2026-09-01 12:35:13 | [log](user_data/convergence_logs/NFI7MOHO-ladder.log) |
| `NFINextMOHO` | `spot_long` | `E1_expanded` | 1442 | `convergence:2016:warmup_supplied` | 2026-09-01 12:35:41 | [log](user_data/convergence_logs/NFINextMOHO-ladder.log) |
| `NFINextMOHO2` | `spot_long` | `E1_expanded` | 1784 | `convergence:2016:warmup_supplied` | 2026-09-01 12:36:07 | [log](user_data/convergence_logs/NFINextMOHO2-ladder.log) |
| `NFINextMultiOffsetAndHO` | `spot_long` | `E1_expanded` | 1094 | `convergence:2016:warmup_supplied` | 2026-09-01 12:36:33 | [log](user_data/convergence_logs/NFINextMultiOffsetAndHO-ladder.log) |
| `NFINextMultiOffsetAndHO2` | `spot_long` | `E1_expanded` | 705 | `convergence:2016:warmup_supplied` | 2026-09-01 12:37:00 | [log](user_data/convergence_logs/NFINextMultiOffsetAndHO2-ladder.log) |
| `NormalizerStrategy` | `spot_long` | `E1_expanded` | 3747 | `convergence:610` | 2026-09-01 12:37:23 | [log](user_data/convergence_logs/NormalizerStrategy-ladder.log) |
| `NormalizerStrategyHO2` | `spot_long` | `E1_expanded` | 3149 | `convergence:610` | 2026-09-01 14:34:54 | [log](user_data/convergence_logs/NormalizerStrategyHO2-ladder.log) |
| `Nostalgia` | `spot_long` | `E1_expanded` | 834 | `convergence:2016:warmup_supplied` | 2026-09-01 12:37:49 | [log](user_data/convergence_logs/Nostalgia-ladder.log) |
| `NostalgiaForInfinityNextGen` | `spot_long` | `E1_expanded` | 158 | `convergence:2880:warmup_supplied` | 2026-09-01 14:35:20 | [log](user_data/convergence_logs/NostalgiaForInfinityNextGen-ladder.log) |
| `NostalgiaForInfinityNextGen_TSL` | `spot_long` | `E1_expanded` | 138 | `convergence:2880:warmup_supplied` | 2026-09-01 14:35:46 | [log](user_data/convergence_logs/NostalgiaForInfinityNextGen_TSL-ladder.log) |
| `NostalgiaForInfinityV3` | `spot_long` | `E1_expanded` | 1015 | `convergence:2016:warmup_supplied` | 2026-09-01 14:36:11 | [log](user_data/convergence_logs/NostalgiaForInfinityV3-ladder.log) |
| `NostalgiaForInfinityV4` | `spot_long` | `E1_expanded` | 401 | `convergence:2016:warmup_supplied` | 2026-09-01 14:36:37 | [log](user_data/convergence_logs/NostalgiaForInfinityV4-ladder.log) |
| `NostalgiaForInfinityV4HO` | `spot_long` | `E1_expanded` | 379 | `convergence:2016:warmup_supplied` | 2026-09-01 14:37:03 | [log](user_data/convergence_logs/NostalgiaForInfinityV4HO-ladder.log) |
| `NostalgiaForInfinityV5` | `spot_long` | `E1_expanded` | 618 | `convergence:2016:warmup_supplied` | 2026-09-01 14:37:31 | [log](user_data/convergence_logs/NostalgiaForInfinityV5-ladder.log) |
| `NostalgiaForInfinityV5MultiOffsetAndHO` | `spot_long` | `E1_expanded` | 1766 | `convergence:2016:warmup_supplied` | 2026-09-01 12:38:14 | [log](user_data/convergence_logs/NostalgiaForInfinityV5MultiOffsetAndHO-ladder.log) |
| `NostalgiaForInfinityV5MultiOffsetAndHO2` | `spot_long` | `E1_expanded` | 1381 | `convergence:2016:warmup_supplied` | 2026-09-01 14:37:59 | [log](user_data/convergence_logs/NostalgiaForInfinityV5MultiOffsetAndHO2-ladder.log) |
| `NostalgiaForInfinityV6` | `spot_long` | `E1_expanded` | 712 | `convergence:2016:warmup_supplied` | 2026-09-01 14:38:27 | [log](user_data/convergence_logs/NostalgiaForInfinityV6-ladder.log) |
| `NostalgiaForInfinityV6HO` | `spot_long` | `E1_expanded` | 712 | `convergence:2016:warmup_supplied` | 2026-09-01 12:38:41 | [log](user_data/convergence_logs/NostalgiaForInfinityV6HO-ladder.log) |
| `NostalgiaForInfinityV7` | `spot_long` | `E1_expanded` | 684 | `convergence:2016:warmup_supplied` | 2026-09-01 14:38:55 | [log](user_data/convergence_logs/NostalgiaForInfinityV7-ladder.log) |
| `NostalgiaForInfinityV7_SMA` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 14:39:23 | [log](user_data/convergence_logs/NostalgiaForInfinityV7_SMA-ladder.log) |
| `NostalgiaForInfinityV7_SMAv2` | `spot_long` | `E1_expanded` | 927 | `convergence:2016:warmup_supplied` | 2026-09-01 14:39:50 | [log](user_data/convergence_logs/NostalgiaForInfinityV7_SMAv2-ladder.log) |
| `NostalgiaForInfinityV7_SMAv2_1` | `spot_long` | `E1_expanded` | 545 | `convergence:2016:warmup_supplied` | 2026-09-01 14:40:17 | [log](user_data/convergence_logs/NostalgiaForInfinityV7_SMAv2_1-ladder.log) |
| `NotAnotherSMAOffsetStrategyLite` | `spot_long` | `E1_expanded` | 1415 | `convergence:2016:warmup_supplied` | 2026-09-01 12:39:05 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyLite-ladder.log) |
| `NotAnotherSMAOffsetStrategyModHO` | `spot_long` | `E1_expanded` | 1144 | `convergence:2016:warmup_supplied` | 2026-09-01 14:45:51 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyModHO-ladder.log) |
| `NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901` | `spot_long` | `E1_expanded` | 1143 | `convergence:2016:warmup_supplied` | 2026-09-01 14:46:17 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901-ladder.log) |
| `NotAnotherSMAOffsetStrategy_uzi` | `spot_long` | `E1_expanded` | 651 | `convergence:2016:warmup_supplied` | 2026-09-01 14:47:10 | [log](user_data/convergence_logs/NotAnotherSMAOffsetStrategy_uzi-ladder.log) |
| `NowoIchimoku1hV2` | `spot_long` | `E1_expanded` | 3695 | `convergence:168:warmup_supplied` | 2026-09-01 14:48:01 | [log](user_data/convergence_logs/NowoIchimoku1hV2-ladder.log) |
| `NowoIchimoku5mV2` | `spot_long` | `E1_expanded` | 49 | `native` | 2026-08-31 15:19:45 | [archive](user_data/profile_smoke/NowoIchimoku5mV2-2026-08-31_15-19-45.zip) |
| `ONUR` | `spot_long` | `E1_expanded` | 534 | `convergence:192:warmup_supplied` | 2026-09-01 16:08:06 | [log](user_data/convergence_logs/ONUR-ladder.log) |
| `ObeliskIM_v1_1` | `spot_long` | `E1_expanded` | 64 | `native` | 2026-08-31 15:20:09 | [archive](user_data/profile_smoke/ObeliskIM_v1_1-2026-08-31_15-20-09.zip) |
| `OmaGann` | `spot_long` | `E1_expanded` | 11035 | `convergence:168:warmup_supplied` | 2026-09-01 16:08:55 | [log](user_data/convergence_logs/OmaGann-ladder.log) |
| `PRICEFOLLOWING` | `spot_long` | `E1_expanded` | 272 | `convergence:288:warmup_supplied` | 2026-09-01 14:48:31 | [log](user_data/convergence_logs/PRICEFOLLOWING-ladder.log) |
| `PRICEFOLLOWINGX` | `spot_long` | `E1_expanded` | 1172 | `convergence:672:warmup_supplied` | 2026-09-01 14:49:28 | [log](user_data/convergence_logs/PRICEFOLLOWINGX-ladder.log) |
| `ParabolicSarStrategy` | `spot_long` | `E1_expanded` | 24042 | `convergence:288:warmup_supplied` | 2026-09-01 12:39:54 | [log](user_data/convergence_logs/ParabolicSarStrategy-ladder.log) |
| `PpoMomentumStrategy` | `spot_long` | `E1_expanded` | 20537 | `convergence:288:warmup_supplied` | 2026-09-01 12:40:19 | [log](user_data/convergence_logs/PpoMomentumStrategy-ladder.log) |
| `PriceActionCandleStrategy` | `spot_long` | `E1_expanded` | 24545 | `convergence:288:warmup_supplied` | 2026-09-01 12:40:43 | [log](user_data/convergence_logs/PriceActionCandleStrategy-ladder.log) |
| `PriceChannelStrategy` | `spot_long` | `E1_expanded` | 17105 | `convergence:288:warmup_supplied` | 2026-09-01 12:41:07 | [log](user_data/convergence_logs/PriceChannelStrategy-ladder.log) |
| `PumpDetector` | `spot_long` | `E1_expanded` | 32258 | `convergence:2016:warmup_supplied` | 2026-09-01 12:41:32 | [log](user_data/convergence_logs/PumpDetector-ladder.log) |
| `Quickie` | `spot_long` | `E1_expanded` | 7676 | `convergence:288:warmup_supplied` | 2026-09-01 14:51:56 | [log](user_data/convergence_logs/Quickie-ladder.log) |
| `RSI` | `spot_long` | `E1_expanded` | 400 | `convergence:192:warmup_supplied` | 2026-09-01 16:09:44 | [log](user_data/convergence_logs/RSI-ladder.log) |
| `RSI_BB` | `spot_long` | `E1_expanded` | 14931 | `convergence:192:warmup_supplied` | 2026-09-01 16:10:33 | [log](user_data/convergence_logs/RSI_BB-ladder.log) |
| `RSI_EMA_strategy` | `spot_long` | `E1_expanded` | 5240 | `convergence:288:warmup_supplied` | 2026-09-01 16:11:22 | [log](user_data/convergence_logs/RSI_EMA_strategy-ladder.log) |
| `RSIv2` | `spot_long` | `E1_expanded` | 5908 | `convergence:192:warmup_supplied` | 2026-09-01 12:41:55 | [log](user_data/convergence_logs/RSIv2-ladder.log) |
| `RalliV1` | `spot_long` | `E1_expanded` | 657 | `convergence:2016:warmup_supplied` | 2026-09-01 14:52:21 | [log](user_data/convergence_logs/RalliV1-ladder.log) |
| `RalliV1_disable56` | `spot_long` | `E1_expanded` | 651 | `convergence:2016:warmup_supplied` | 2026-09-01 14:52:46 | [log](user_data/convergence_logs/RalliV1_disable56-ladder.log) |
| `ReinforcedAverageStrategy` | `spot_long` | `E1_expanded` | 1163 | `convergence:84:warmup_supplied` | 2026-09-01 14:53:35 | [log](user_data/convergence_logs/ReinforcedAverageStrategy-ladder.log) |
| `ReinforcedSmoothScalp` | `spot_long` | `E1_expanded` | 663 | `convergence:2880:warmup_supplied` | 2026-09-01 16:12:10 | [log](user_data/convergence_logs/ReinforcedSmoothScalp-ladder.log) |
| `RocMomentumStrategy` | `spot_long` | `E1_expanded` | 26606 | `convergence:576:warmup_supplied` | 2026-09-01 12:42:20 | [log](user_data/convergence_logs/RocMomentumStrategy-ladder.log) |
| `Roth01` | `spot_long` | `E1_expanded` | 12346 | `convergence:288:warmup_supplied` | 2026-09-01 16:13:01 | [log](user_data/convergence_logs/Roth01-ladder.log) |
| `Roth03` | `spot_long` | `E1_expanded` | 3509 | `convergence:288:warmup_supplied` | 2026-09-01 16:13:52 | [log](user_data/convergence_logs/Roth03-ladder.log) |
| `RsiBollingerStrategy` | `spot_long` | `E1_expanded` | 2885 | `convergence:168:warmup_supplied` | 2026-09-01 12:42:44 | [log](user_data/convergence_logs/RsiBollingerStrategy-ladder.log) |
| `RsiDivergenceStrategy` | `spot_long` | `E1_expanded` | 474 | `convergence:288:warmup_supplied` | 2026-09-01 14:54:00 | [log](user_data/convergence_logs/RsiDivergenceStrategy-ladder.log) |
| `SAR` | `spot_long` | `E1_expanded` | 30880 | `convergence:288:warmup_supplied` | 2026-09-01 15:00:35 | [log](user_data/convergence_logs/SAR-ladder.log) |
| `SMAOffset` | `spot_long` | `E1_expanded` | 2108 | `convergence:288:warmup_supplied` | 2026-09-01 14:54:50 | [log](user_data/convergence_logs/SMAOffset-ladder.log) |
| `SMAOffsetProtectOpt` | `spot_long` | `E1_expanded` | 181 | `convergence:2016:warmup_supplied` | 2026-09-01 14:55:15 | [log](user_data/convergence_logs/SMAOffsetProtectOpt-ladder.log) |
| `SMAOffsetProtectOptV0` | `spot_long` | `E1_expanded` | 253 | `convergence:2016:warmup_supplied` | 2026-09-01 14:55:41 | [log](user_data/convergence_logs/SMAOffsetProtectOptV0-ladder.log) |
| `SMAOffsetProtectOptV1` | `spot_long` | `E1_expanded` | 203 | `convergence:2016:warmup_supplied` | 2026-09-01 14:56:06 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1-ladder.log) |
| `SMAOffsetProtectOptV1HO1` | `spot_long` | `E1_expanded` | 1233 | `convergence:2016:warmup_supplied` | 2026-09-01 14:56:32 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1HO1-ladder.log) |
| `SMAOffsetProtectOptV1Mod` | `spot_long` | `E1_expanded` | 202 | `convergence:2016:warmup_supplied` | 2026-09-01 14:56:58 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1Mod-ladder.log) |
| `SMAOffsetProtectOptV1Mod2` | `spot_long` | `E1_expanded` | 206 | `convergence:2016:warmup_supplied` | 2026-09-01 14:57:24 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1Mod2-ladder.log) |
| `SMAOffsetProtectOptV1_kkeue_20210619` | `spot_long` | `E1_expanded` | 206 | `convergence:2016:warmup_supplied` | 2026-09-01 14:57:51 | [log](user_data/convergence_logs/SMAOffsetProtectOptV1_kkeue_20210619-ladder.log) |
| `SMAOffset_Hippocritical_dca` | `spot_long` | `E1_expanded` | 218 | `convergence:2016:warmup_supplied` | 2026-09-01 14:58:16 | [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca-ladder.log) |
| `SMAOffset_Hippocritical_dca_old` | `spot_long` | `E1_expanded` | 218 | `convergence:2016:warmup_supplied` | 2026-09-01 14:59:11 | [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca_old-ladder.log) |
| `SMAOffset_Hippocritical_dca_protections` | `spot_long` | `E1_expanded` | 218 | `convergence:2016:warmup_supplied` | 2026-09-01 14:59:41 | [log](user_data/convergence_logs/SMAOffset_Hippocritical_dca_protections-ladder.log) |
| `SMA_BBRSI` | `spot_long` | `E1_expanded` | 706 | `convergence:2016:warmup_supplied` | 2026-09-01 15:00:08 | [log](user_data/convergence_logs/SMA_BBRSI-ladder.log) |
| `SRsi` | `spot_long` | `E1_expanded` | 23768 | `convergence:1440:warmup_supplied` | 2026-09-01 12:43:10 | [log](user_data/convergence_logs/SRsi-ladder.log) |
| `STRATEGY_RSI_BB_BOUNDS_CROSS` | `spot_long` | `E1_expanded` | 7197 | `convergence:288:warmup_supplied` | 2026-09-01 12:43:35 | [log](user_data/convergence_logs/STRATEGY_RSI_BB_BOUNDS_CROSS-ladder.log) |
| `STRATEGY_RSI_BB_CROSS` | `spot_long` | `E1_expanded` | 16827 | `convergence:288:warmup_supplied` | 2026-09-01 12:44:00 | [log](user_data/convergence_logs/STRATEGY_RSI_BB_CROSS-ladder.log) |
| `SampleStrategy` | `spot_long` | `E1_expanded` | 12724 | `convergence:288:warmup_supplied` | 2026-09-01 12:44:24 | [log](user_data/convergence_logs/SampleStrategy-ladder.log) |
| `Sar` | `spot_long` | `E1_expanded` | 12724 | `convergence:288:warmup_supplied` | 2026-09-01 15:00:35 | [log](user_data/convergence_logs/Sar-ladder.log) |
| `Scalp` | `spot_long` | `E1_expanded` | 28414 | `convergence:1440:warmup_supplied` | 2026-09-01 15:01:53 | [log](user_data/convergence_logs/Scalp-ladder.log) |
| `Schism3` | `spot_long` | `E1_expanded` | 3631 | `convergence:288:warmup_supplied` | 2026-09-01 15:02:45 | [log](user_data/convergence_logs/Schism3-ladder.log) |
| `Schism4` | `spot_long` | `E1_expanded` | 993 | `convergence:288:warmup_supplied` | 2026-09-01 15:03:10 | [log](user_data/convergence_logs/Schism4-ladder.log) |
| `Seb` | `spot_long` | `E1_expanded` | 13947 | `convergence:576:warmup_supplied` | 2026-09-01 15:04:02 | [log](user_data/convergence_logs/Seb-ladder.log) |
| `Simple` | `spot_long` | `E1_expanded` | 16675 | `convergence:288:warmup_supplied` | 2026-09-01 15:04:56 | [log](user_data/convergence_logs/Simple-ladder.log) |
| `SimpleHopt` | `spot_long` | `E1_expanded` | 16675 | `convergence:288:warmup_supplied` | 2026-09-01 16:14:42 | [log](user_data/convergence_logs/SimpleHopt-ladder.log) |
| `SmaRsiStrategy` | `spot_long` | `E1_expanded` | 575 | `convergence:90:warmup_supplied` | 2026-09-01 12:44:48 | [log](user_data/convergence_logs/SmaRsiStrategy-ladder.log) |
| `SmartMoneyStrategy` | `spot_long` | `E1_expanded` | 285 | `convergence:1440:warmup_supplied` | 2026-09-01 16:16:19 | [log](user_data/convergence_logs/SmartMoneyStrategy-ladder.log) |
| `SmoothOperator` | `spot_long` | `E1_expanded` | 17127 | `convergence:288:warmup_supplied` | 2026-09-01 15:05:49 | [log](user_data/convergence_logs/SmoothOperator-ladder.log) |
| `SmoothScalp` | `spot_long` | `E1_expanded` | 26236 | `convergence:1440:warmup_supplied` | 2026-09-01 15:06:43 | [log](user_data/convergence_logs/SmoothScalp-ladder.log) |
| `SqueezeMomentumStrategy` | `spot_long` | `E1_expanded` | 23183 | `convergence:288:warmup_supplied` | 2026-09-01 12:45:12 | [log](user_data/convergence_logs/SqueezeMomentumStrategy-ladder.log) |
| `StarRise` | `spot_long` | `E1_expanded` | 220 | `convergence:2016:warmup_supplied` | 2026-09-01 15:07:11 | [log](user_data/convergence_logs/StarRise-ladder.log) |
| `StarRise_strat` | `spot_long` | `E1_expanded` | 255 | `convergence:2016:warmup_supplied` | 2026-09-01 15:07:38 | [log](user_data/convergence_logs/StarRise_strat-ladder.log) |
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
| `SuperTrend` | `spot_long` | `E1_expanded` | 2219 | `convergence:1440:warmup_supplied` | 2026-09-01 15:09:01 | [log](user_data/convergence_logs/SuperTrend-ladder.log) |
| `TD` | `spot_long` | `E1_expanded` | 6164 | `convergence:12:warmup_supplied` | 2026-09-01 15:11:03 | [log](user_data/convergence_logs/TD-ladder.log) |
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
| `TheForce` | `spot_long` | `E1_expanded` | 24088 | `convergence:672:warmup_supplied` | 2026-09-01 15:13:10 | [log](user_data/convergence_logs/TheForce-ladder.log) |
| `ToTheMoon` | `futures_long_short` | `E1_expanded` | 16 | `convergence:24:warmup_supplied` | 2026-09-01 15:13:58 | [log](user_data/convergence_logs/ToTheMoon-ladder.log) |
| `TouchEmaDelayStrategy` | `spot_long` | `E1_expanded` | 2331 | `convergence:480:warmup_supplied` | 2026-09-01 16:28:24 | [log](user_data/convergence_logs/TouchEmaDelayStrategy-ladder.log) |
| `TouchEmaStrategy` | `spot_long` | `E1_expanded` | 5193 | `convergence:288:warmup_supplied` | 2026-09-01 16:29:16 | [log](user_data/convergence_logs/TouchEmaStrategy-ladder.log) |
| `TrendAtrStrategy` | `spot_long` | `E1_expanded` | 3067 | `convergence:540:warmup_supplied` | 2026-09-01 12:47:40 | [log](user_data/convergence_logs/TrendAtrStrategy-ladder.log) |
| `Trend_Strength_Directional` | `spot_long` | `E1_expanded` | 7684 | `convergence:192:warmup_supplied` | 2026-09-01 16:30:06 | [log](user_data/convergence_logs/Trend_Strength_Directional-ladder.log) |
| `TripleEmaStrategy` | `spot_long` | `E1_expanded` | 17670 | `convergence:288:warmup_supplied` | 2026-09-01 12:48:03 | [log](user_data/convergence_logs/TripleEmaStrategy-ladder.log) |
| `TrixSignalStrategy` | `spot_long` | `E1_expanded` | 17885 | `convergence:288:warmup_supplied` | 2026-09-01 12:48:28 | [log](user_data/convergence_logs/TrixSignalStrategy-ladder.log) |
| `TrixV21Strategy` | `spot_long` | `E1_expanded` | 1152 | `convergence:2160:warmup_supplied` | 2026-09-01 15:15:37 | [log](user_data/convergence_logs/TrixV21Strategy-ladder.log) |
| `TrixV23Strategy` | `spot_long` | `E1_expanded` | 1305 | `convergence:2160:warmup_supplied` | 2026-09-01 15:16:03 | [log](user_data/convergence_logs/TrixV23Strategy-ladder.log) |
| `TwoCandle` | `spot_long` | `E1_expanded` | 18935 | `convergence:168:warmup_supplied` | 2026-09-01 16:30:56 | [log](user_data/convergence_logs/TwoCandle-ladder.log) |
| `UniversalMACD` | `spot_long` | `E1_expanded` | 2090 | `convergence:288:warmup_supplied` | 2026-09-01 12:48:53 | [log](user_data/convergence_logs/UniversalMACD-ladder.log) |
| `Uptrend` | `spot_long` | `E1_expanded` | 471 | `convergence:2016:warmup_supplied` | 2026-09-01 15:16:28 | [log](user_data/convergence_logs/Uptrend-ladder.log) |
| `VWAP` | `spot_long` | `E1_expanded` | 986 | `convergence:2016:warmup_supplied` | 2026-09-01 15:17:16 | [log](user_data/convergence_logs/VWAP-ladder.log) |
| `VolatilitySystem` | `futures_long` | `E1_expanded` | 9 | `convergence:336:warmup_supplied` | 2026-09-01 15:18:07 | [log](user_data/convergence_logs/VolatilitySystem-ladder.log) |
| `VolatilitySystemV2` | `futures_long_short` | `E1_expanded` | 24 | `convergence:336:warmup_supplied` | 2026-09-01 15:18:57 | [log](user_data/convergence_logs/VolatilitySystemV2-ladder.log) |
| `VolumeBreakoutStrategy` | `spot_long` | `E1_expanded` | 16564 | `convergence:288:warmup_supplied` | 2026-09-01 12:49:17 | [log](user_data/convergence_logs/VolumeBreakoutStrategy-ladder.log) |
| `VortexStrategy` | `spot_long` | `E1_expanded` | 29787 | `convergence:288:warmup_supplied` | 2026-09-01 12:49:42 | [log](user_data/convergence_logs/VortexStrategy-ladder.log) |
| `VwapReversionStrategy` | `spot_long` | `E1_expanded` | 22316 | `convergence:576:warmup_supplied` | 2026-09-01 12:50:07 | [log](user_data/convergence_logs/VwapReversionStrategy-ladder.log) |
| `WaveTrendStra` | `spot_long` | `E1_expanded` | 9256 | `convergence:180:warmup_supplied` | 2026-09-01 15:19:48 | [log](user_data/convergence_logs/WaveTrendStra-ladder.log) |
| `WilliamsRStrategy` | `spot_long` | `E1_expanded` | 26924 | `convergence:2016:warmup_supplied` | 2026-09-01 12:50:33 | [log](user_data/convergence_logs/WilliamsRStrategy-ladder.log) |
| `YOLO` | `spot_long` | `E1_expanded` | 560 | `convergence:1440:warmup_supplied` | 2026-09-01 15:20:39 | [log](user_data/convergence_logs/YOLO-ladder.log) |
| `ZScoreMeanReversionStrategy` | `spot_long` | `E1_expanded` | 37 | `convergence:540:warmup_supplied` | 2026-09-01 15:21:04 | [log](user_data/convergence_logs/ZScoreMeanReversionStrategy-ladder.log) |
| `adaptive` | `spot_long` | `E1_expanded` | 647 | `convergence:2016:warmup_supplied` | 2026-09-01 15:23:35 | [log](user_data/convergence_logs/adaptive-ladder.log) |
| `adxbbrsi2` | `spot_long` | `E1_expanded` | 741 | `convergence:336:warmup_supplied` | 2026-09-01 12:50:58 | [log](user_data/convergence_logs/adxbbrsi2-ladder.log) |
| `bbandrsi` | `spot_long` | `E1_expanded` | 6758 | `convergence:192:warmup_supplied` | 2026-09-01 16:31:44 | [log](user_data/convergence_logs/bbandrsi-ladder.log) |
| `bbrsi` | `spot_long` | `E1_expanded` | 5507 | `convergence:180:warmup_supplied` | 2026-09-01 12:51:22 | [log](user_data/convergence_logs/bbrsi-ladder.log) |
| `bbrsi4Freq` | `spot_long` | `E1_expanded` | 4791 | `convergence:168:warmup_supplied` | 2026-09-01 12:51:45 | [log](user_data/convergence_logs/bbrsi4Freq-ladder.log) |
| `conny` | `spot_long` | `E1_expanded` | 5825 | `convergence:96:warmup_supplied` | 2026-09-01 12:52:10 | [log](user_data/convergence_logs/conny-ladder.log) |
| `cryptotankV2` | `spot_long` | `E1_expanded` | 770 | `convergence:576:warmup_supplied` | 2026-09-01 12:52:35 | [log](user_data/convergence_logs/cryptotankV2-ladder.log) |
| `dualwave` | `spot_long` | `E1_expanded` | 1767 | `convergence:672:warmup_supplied` | 2026-09-01 15:24:26 | [log](user_data/convergence_logs/dualwave-ladder.log) |
| `e6v34` | `spot_long` | `E1_expanded` | 19447 | `convergence:672:warmup_supplied` | 2026-09-01 16:32:32 | [log](user_data/convergence_logs/e6v34-ladder.log) |
| `eltoro` | `spot_long` | `E1_expanded` | 3704 | `convergence:1344:warmup_supplied` | 2026-09-01 12:53:00 | [log](user_data/convergence_logs/eltoro-ladder.log) |
| `eltoro1_4` | `spot_long` | `E1_expanded` | 2393 | `convergence:2160:warmup_supplied` | 2026-09-01 12:53:24 | [log](user_data/convergence_logs/eltoro1_4-ladder.log) |
| `eltoro1_4_simple` | `spot_long` | `E1_expanded` | 2417 | `convergence:672:warmup_supplied` | 2026-09-01 12:53:49 | [log](user_data/convergence_logs/eltoro1_4_simple-ladder.log) |
| `ema` | `spot_long` | `E1_expanded` | 30806 | `convergence:2016:warmup_supplied` | 2026-09-01 16:33:20 | [log](user_data/convergence_logs/ema-ladder.log) |
| `gettinMoist` | `spot_long` | `E1_expanded` | 20036 | `convergence:288:warmup_supplied` | 2026-09-01 12:54:38 | [log](user_data/convergence_logs/gettinMoist-ladder.log) |
| `hansencandlepatternV1` | `spot_long` | `E1_expanded` | 17165 | `convergence:24:warmup_supplied` | 2026-09-01 15:25:15 | [log](user_data/convergence_logs/hansencandlepatternV1-ladder.log) |
| `heikin` | `spot_long` | `E1_expanded` | 21053 | `convergence:24:warmup_supplied` | 2026-09-01 15:26:03 | [log](user_data/convergence_logs/heikin-ladder.log) |
| `hlhb` | `spot_long` | `E1_expanded` | 861 | `convergence:540:warmup_supplied` | 2026-09-01 12:55:01 | [log](user_data/convergence_logs/hlhb-ladder.log) |
| `keltnerchannel` | `spot_long` | `E1_expanded` | 1131 | `convergence:360:warmup_supplied` | 2026-09-01 15:26:51 | [log](user_data/convergence_logs/keltnerchannel-ladder.log) |
| `pmaxTest` | `spot_long` | `E1_expanded` | 23 | `convergence:2016:warmup_supplied` | 2026-08-31 15:33:16 | [archive](user_data/profile_smoke/pmaxTest-2026-08-31_15-33-16.zip) [log](user_data/convergence_logs/pmaxTest-ladder.log) |
| `simple_patterns` | `spot_long` | `E1_expanded` | 1845 | `native` | 2026-08-31 15:55:52 | [archive](user_data/profile_smoke/simple_patterns-2026-08-31_15-55-52.zip) |
| `slope_is_dopeCT` | `spot_long` | `E1_expanded` | 821 | `convergence:672:warmup_supplied` | 2026-09-01 12:55:49 | [log](user_data/convergence_logs/slope_is_dopeCT-ladder.log) |
| `slownsteady` | `spot_long` | `E1_expanded` | 35 | `convergence:2016:warmup_supplied` | 2026-08-31 15:54:44 | [archive](user_data/profile_smoke/slownsteady-2026-08-31_15-54-44.zip) [log](user_data/convergence_logs/slownsteady-ladder.log) |
| `stoploss` | `spot_long` | `E1_expanded` | 12724 | `convergence:288:warmup_supplied` | 2026-09-01 12:56:13 | [log](user_data/convergence_logs/stoploss-ladder.log) |
| `strato` | `spot_long` | `E1_expanded` | 24409 | `convergence:1440:warmup_supplied` | 2026-09-01 12:56:41 | [log](user_data/convergence_logs/strato-ladder.log) |
| `thetank3` | `spot_long` | `E1_expanded` | 8620 | `convergence:672:warmup_supplied` | 2026-09-01 12:57:28 | [log](user_data/convergence_logs/thetank3-ladder.log) |
| `thetank4TV` | `spot_long` | `E1_expanded` | 3023 | `convergence:672:warmup_supplied` | 2026-09-01 12:57:53 | [log](user_data/convergence_logs/thetank4TV-ladder.log) |
| `true_lambo` | `spot_long` | `E1_expanded` | 1194 | `convergence:2016:warmup_supplied` | 2026-09-01 15:30:39 | [log](user_data/convergence_logs/true_lambo-ladder.log) |
| `twinturboV8` | `spot_long` | `E1_expanded` | 131 | `convergence:2016:warmup_supplied` | 2026-09-01 15:31:06 | [log](user_data/convergence_logs/twinturboV8-ladder.log) |
| `twinturboV8_2` | `spot_long` | `E1_expanded` | 119 | `convergence:2016:warmup_supplied` | 2026-09-01 15:31:32 | [log](user_data/convergence_logs/twinturboV8_2-ladder.log) |
| `ultratank` | `spot_long` | `E1_expanded` | 3076 | `convergence:336:warmup_supplied` | 2026-09-01 12:58:17 | [log](user_data/convergence_logs/ultratank-ladder.log) |
| `wavetrend` | `spot_long` | `E1_expanded` | 4691 | `convergence:336:warmup_supplied` | 2026-09-01 12:58:45 | [log](user_data/convergence_logs/wavetrend-ladder.log) |
| `wavetrend_rsi` | `spot_long` | `E1_expanded` | 5240 | `convergence:336:warmup_supplied` | 2026-09-01 12:59:09 | [log](user_data/convergence_logs/wavetrend_rsi-ladder.log) |

The calls behind each, one per gate:

- `BBRSIv2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIv2 --strategy-path user_data/profile_bias_strategies/BBRSIv2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIv2 --strategy-path user_data/profile_bias_strategies/BBRSIv2 --timerange 20190101-20190401 --no-color
  ```
- `BigTrader`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigTrader --strategy-path user_data/profile_bias_strategies/BigTrader --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigTrader --strategy-path user_data/profile_bias_strategies/BigTrader --timerange 20190101-20190401 --no-color
  ```
- `BigZ03`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03 --strategy-path user_data/profile_bias_strategies/BigZ03 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03 --strategy-path user_data/profile_bias_strategies/BigZ03 --timerange 20190101-20190401 --no-color
  ```
- `BigZ03HO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03HO --strategy-path user_data/profile_bias_strategies/BigZ03HO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03HO --strategy-path user_data/profile_bias_strategies/BigZ03HO --timerange 20190101-20190401 --no-color
  ```
- `BigZ04_TSL3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL3 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL3 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL3 --timerange 20190101-20190401 --no-color
  ```
- `BigZ04_TSL4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL4 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL4 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL4 --timerange 20190101-20190401 --no-color
  ```
- `BinClucMad`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMad --strategy-path user_data/profile_bias_strategies/BinClucMad --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMad --strategy-path user_data/profile_bias_strategies/BinClucMad --timerange 20190101-20190401 --no-color
  ```
- `BuyRegions`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyRegions --strategy-path user_data/profile_bias_strategies/BuyRegions --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyRegions --strategy-path user_data/profile_bias_strategies/BuyRegions --timerange 20190101-20190401 --no-color
  ```
- `Cluc7werk`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc7werk --strategy-path user_data/profile_bias_strategies/Cluc7werk --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc7werk --strategy-path user_data/profile_bias_strategies/Cluc7werk --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5M_E0V1E`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5m`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5m1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m1 --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m1 --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m1 --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5m_old`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m_old --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m_old --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m_old --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m_old --timerange 20190101-20190401 --no-color
  ```
- `ClucHAwerk`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAwerk --strategy-path user_data/profile_bias_strategies/ClucHAwerk --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAwerk --strategy-path user_data/profile_bias_strategies/ClucHAwerk --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV3 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV6`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV6 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV6 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV7`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV7 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV7 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV7 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV7 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV3 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV5 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV6`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV6 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV6 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV6 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV9`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV9 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV9 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV9 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV9 --timerange 20190101-20190401 --no-color
  ```
- `EMA_CROSSOVER_STRATEGY`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA_CROSSOVER_STRATEGY --strategy-path user_data/profile_bias_strategies/EMA_CROSSOVER_STRATEGY --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA_CROSSOVER_STRATEGY --strategy-path user_data/profile_bias_strategies/EMA_CROSSOVER_STRATEGY --timerange 20190101-20190401 --no-color
  ```
- `ElliotV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV2 --strategy-path user_data/profile_bias_strategies/ElliotV2 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV2 --strategy-path user_data/profile_bias_strategies/ElliotV2 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5_SMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5_SMA --strategy-path user_data/profile_bias_strategies/ElliotV5_SMA --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5_SMA --strategy-path user_data/profile_bias_strategies/ElliotV5_SMA --timerange 20190101-20190401 --no-color
  ```
- `FAdxSmaStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FAdxSmaStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path user_data/profile_bias_strategies/FAdxSmaStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path user_data/profile_bias_strategies/FAdxSmaStrategy --timerange 20200301-20200401 --no-color
  ```
- `FSupertrendStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long.json --strategy FSupertrendStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FSupertrendStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long.json --strategy FSupertrendStrategy --strategy-path user_data/profile_bias_strategies/FSupertrendStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long.json --strategy FSupertrendStrategy --strategy-path user_data/profile_bias_strategies/FSupertrendStrategy --timerange 20200301-20200401 --no-color
  ```
- `FastSupertrend_ts_origstop_fix`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_ts_origstop_fix --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_bias_strategies/FastSupertrend_ts_origstop_fix --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_bias_strategies/FastSupertrend_ts_origstop_fix --timerange 20200301-20200401 --no-color
  ```
- `FlawlessVictory`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FlawlessVictory --strategy-path user_data/profile_bias_strategies/FlawlessVictory --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FlawlessVictory --strategy-path user_data/profile_bias_strategies/FlawlessVictory --timerange 20190101-20190401 --no-color
  ```
- `ForexSignal`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ForexSignal --strategy-path user_data/profile_bias_strategies/ForexSignal --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ForexSignal --strategy-path user_data/profile_bias_strategies/ForexSignal --timerange 20190101-20190401 --no-color
  ```
- `Gumbo1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Gumbo1 --strategy-path user_data/profile_bias_strategies/Gumbo1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Gumbo1 --strategy-path user_data/profile_bias_strategies/Gumbo1 --timerange 20190101-20190401 --no-color
  ```
- `Ichimoku_v31`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v31 --strategy-path user_data/profile_bias_strategies/Ichimoku_v31 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v31 --strategy-path user_data/profile_bias_strategies/Ichimoku_v31 --timerange 20190101-20190401 --no-color
  ```
- `Ichimoku_v37`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v37 --strategy-path user_data/profile_bias_strategies/Ichimoku_v37 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v37 --strategy-path user_data/profile_bias_strategies/Ichimoku_v37 --timerange 20190101-20190401 --no-color
  ```
- `KAMACCIRSI`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI --strategy-path user_data/profile_bias_strategies/KAMACCIRSI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI --strategy-path user_data/profile_bias_strategies/KAMACCIRSI --timerange 20190101-20190401 --no-color
  ```
- `MACD_TRIPLE_MA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRIPLE_MA --strategy-path user_data/profile_bias_strategies/MACD_TRIPLE_MA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRIPLE_MA --strategy-path user_data/profile_bias_strategies/MACD_TRIPLE_MA --timerange 20190101-20190401 --no-color
  ```
- `MADisplaceV3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MADisplaceV3 --strategy-path user_data/profile_bias_strategies/MADisplaceV3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MADisplaceV3 --strategy-path user_data/profile_bias_strategies/MADisplaceV3 --timerange 20190101-20190401 --no-color
  ```
- `MacdStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdStrategy --strategy-path user_data/profile_bias_strategies/MacdStrategy --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdStrategy --strategy-path user_data/profile_bias_strategies/MacdStrategy --timerange 20190101-20190401 --no-color
  ```
- `MarketChyperHyperStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MarketChyperHyperStrategy --strategy-path user_data/profile_bias_strategies/MarketChyperHyperStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MarketChyperHyperStrategy --strategy-path user_data/profile_bias_strategies/MarketChyperHyperStrategy --timerange 20190101-20190401 --no-color
  ```
- `NWEv6_new`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NWEv6_new --strategy-path user_data/profile_bias_strategies/NWEv6_new --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NWEv6_new --strategy-path user_data/profile_bias_strategies/NWEv6_new --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV1 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV1 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV1 --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV2 --strategy-path user_data/profile_bias_strategies/NostalgiaForInfinityV2 --timerange 20190101-20190401 --no-color
  ```
- `PowerTower`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PowerTower --strategy-path user_data/profile_bias_strategies/PowerTower --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PowerTower --strategy-path user_data/profile_bias_strategies/PowerTower --timerange 20190101-20190401 --no-color
  ```
- `RegimeFilterStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy RegimeFilterStrategy --strategy-path repos/Bananajoexxc_RegimeFilterStrategy-Freqtrade/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RegimeFilterStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy RegimeFilterStrategy --strategy-path user_data/profile_bias_strategies/RegimeFilterStrategy --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy RegimeFilterStrategy --strategy-path user_data/profile_bias_strategies/RegimeFilterStrategy --timerange 20200301-20200401 --no-color
  ```
- `RobotradingBody`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RobotradingBody --strategy-path user_data/profile_bias_strategies/RobotradingBody --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RobotradingBody --strategy-path user_data/profile_bias_strategies/RobotradingBody --timerange 20190101-20190401 --no-color
  ```
- `SMAIP3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAIP3 --strategy-path user_data/profile_bias_strategies/SMAIP3 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAIP3 --strategy-path user_data/profile_bias_strategies/SMAIP3 --timerange 20190101-20190401 --no-color
  ```
- `SMAOG`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOG --strategy-path user_data/profile_bias_strategies/SMAOG --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOG --strategy-path user_data/profile_bias_strategies/SMAOG --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetV2 --strategy-path user_data/profile_bias_strategies/SMAOffsetV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetV2 --strategy-path user_data/profile_bias_strategies/SMAOffsetV2 --timerange 20190101-20190401 --no-color
  ```
- `SampleStrategyV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategyV2 --strategy-path user_data/profile_bias_strategies/SampleStrategyV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategyV2 --strategy-path user_data/profile_bias_strategies/SampleStrategyV2 --timerange 20190101-20190401 --no-color
  ```
- `Slowbro`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Slowbro --strategy-path user_data/profile_bias_strategies/Slowbro --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Slowbro --strategy-path user_data/profile_bias_strategies/Slowbro --timerange 20190101-20190401 --no-color
  ```
- `StochRSITEMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochRSITEMA --strategy-path user_data/profile_bias_strategies/StochRSITEMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochRSITEMA --strategy-path user_data/profile_bias_strategies/StochRSITEMA --timerange 20190101-20190401 --no-color
  ```
- `StochasticCciStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticCciStrategy --strategy-path user_data/profile_bias_strategies/StochasticCciStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticCciStrategy --strategy-path user_data/profile_bias_strategies/StochasticCciStrategy --timerange 20190101-20190401 --no-color
  ```
- `TDSequentialStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TDSequentialStrategy --strategy-path user_data/profile_bias_strategies/TDSequentialStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TDSequentialStrategy --strategy-path user_data/profile_bias_strategies/TDSequentialStrategy --timerange 20190101-20190401 --no-color
  ```
- `TenderEnter`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TenderEnter --strategy-path user_data/profile_bias_strategies/TenderEnter --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TenderEnter --strategy-path user_data/profile_bias_strategies/TenderEnter --timerange 20190101-20190401 --no-color
  ```
- `TheRealPullbackV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TheRealPullbackV2 --strategy-path user_data/profile_bias_strategies/TheRealPullbackV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TheRealPullbackV2 --strategy-path user_data/profile_bias_strategies/TheRealPullbackV2 --timerange 20190101-20190401 --no-color
  ```
- `TrixStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixStrategy --strategy-path user_data/profile_bias_strategies/TrixStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixStrategy --strategy-path user_data/profile_bias_strategies/TrixStrategy --timerange 20190101-20190401 --no-color
  ```
- `TrixV15Strategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV15Strategy --strategy-path user_data/profile_bias_strategies/TrixV15Strategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV15Strategy --strategy-path user_data/profile_bias_strategies/TrixV15Strategy --timerange 20190101-20190401 --no-color
  ```
- `UltimateMomentumIndicator`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy UltimateMomentumIndicator --strategy-path user_data/profile_bias_strategies/UltimateMomentumIndicator --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy UltimateMomentumIndicator --strategy-path user_data/profile_bias_strategies/UltimateMomentumIndicator --timerange 20190101-20190401 --no-color
  ```
- `XtraThicc`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy XtraThicc --strategy-path user_data/profile_bias_strategies/XtraThicc --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy XtraThicc --strategy-path user_data/profile_bias_strategies/XtraThicc --timerange 20190101-20190401 --no-color
  ```
- `adaptive_trend`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive_trend --strategy-path user_data/profile_bias_strategies/adaptive_trend --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive_trend --strategy-path user_data/profile_bias_strategies/adaptive_trend --timerange 20190101-20190401 --no-color
  ```
- `bestV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bestV2 --strategy-path user_data/profile_bias_strategies/bestV2 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bestV2 --strategy-path user_data/profile_bias_strategies/bestV2 --timerange 20190101-20190401 --no-color
  ```
- `botbaby`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy botbaby --strategy-path user_data/profile_bias_strategies/botbaby --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy botbaby --strategy-path user_data/profile_bias_strategies/botbaby --timerange 20190101-20190401 --no-color
  ```
- `cryptotank`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotank --strategy-path user_data/profile_bias_strategies/cryptotank --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotank --strategy-path user_data/profile_bias_strategies/cryptotank --timerange 20190101-20190401 --no-color
  ```
- `cryptotankV5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV5 --strategy-path user_data/profile_bias_strategies/cryptotankV5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV5 --strategy-path user_data/profile_bias_strategies/cryptotankV5 --timerange 20190101-20190401 --no-color
  ```
- `fahmibah`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy fahmibah --strategy-path user_data/profile_bias_strategies/fahmibah --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy fahmibah --strategy-path user_data/profile_bias_strategies/fahmibah --timerange 20190101-20190401 --no-color
  ```
- `momentum`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum --strategy-path user_data/profile_bias_strategies/momentum --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum --strategy-path user_data/profile_bias_strategies/momentum --timerange 20200301-20200401 --no-color
  ```
- `momentum_long`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy momentum_long --strategy-path user_data/profile_bias_strategies/momentum_long --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy momentum_long --strategy-path user_data/profile_bias_strategies/momentum_long --timerange 20190101-20190401 --no-color
  ```
- `momentum_rsi`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_rsi --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum_rsi --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_rsi --strategy-path user_data/profile_bias_strategies/momentum_rsi --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_rsi --strategy-path user_data/profile_bias_strategies/momentum_rsi --timerange 20200301-20200401 --no-color
  ```
- `momentum_wick`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_wick --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum_wick --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_wick --strategy-path user_data/profile_bias_strategies/momentum_wick --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_wick --strategy-path user_data/profile_bias_strategies/momentum_wick --timerange 20200301-20200401 --no-color
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
- `BB_RTR`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RTR --strategy-path user_data/profile_bias_strategies/BB_RTR --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BB_RTR --strategy-path user_data/profile_bias_strategies/BB_RTR --timerange 20190101-20190401 --no-color
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
- `BbWidthExpansionStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbWidthExpansionStrategy --strategy-path user_data/profile_bias_strategies/BbWidthExpansionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BbWidthExpansionStrategy --strategy-path user_data/profile_bias_strategies/BbWidthExpansionStrategy --timerange 20190101-20190401 --no-color
  ```
- `BbandRsi`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsi --strategy-path user_data/profile_bias_strategies/BbandRsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsi --strategy-path user_data/profile_bias_strategies/BbandRsi --timerange 20190101-20190401 --no-color
  ```
- `BbandRsiRolling`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsiRolling --strategy-path user_data/profile_bias_strategies/BbandRsiRolling --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BbandRsiRolling --strategy-path user_data/profile_bias_strategies/BbandRsiRolling --timerange 20190101-20190401 --no-color
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
- `ClucHAnix_hhll`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_hhll --strategy-path user_data/profile_bias_strategies/ClucHAnix_hhll --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_hhll --strategy-path user_data/profile_bias_strategies/ClucHAnix_hhll --timerange 20190101-20190401 --no-color
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
- `EMABreakout`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMABreakout --strategy-path user_data/profile_bias_strategies/EMABreakout --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMABreakout --strategy-path user_data/profile_bias_strategies/EMABreakout --timerange 20190101-20190401 --no-color
  ```
- `EMASkipPump`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMASkipPump --strategy-path user_data/profile_bias_strategies/EMASkipPump --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMASkipPump --strategy-path user_data/profile_bias_strategies/EMASkipPump --timerange 20190101-20190401 --no-color
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
- `EmaRibbonStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EmaRibbonStrategy --strategy-path user_data/profile_bias_strategies/EmaRibbonStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EmaRibbonStrategy --strategy-path user_data/profile_bias_strategies/EmaRibbonStrategy --timerange 20190101-20190401 --no-color
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
- `IchimokuSimpleStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy IchimokuSimpleStrategy --strategy-path user_data/profile_bias_strategies/IchimokuSimpleStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy IchimokuSimpleStrategy --strategy-path user_data/profile_bias_strategies/IchimokuSimpleStrategy --timerange 20190101-20190401 --no-color
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
- `LinearRegressionStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy LinearRegressionStrategy --strategy-path user_data/profile_bias_strategies/LinearRegressionStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy LinearRegressionStrategy --strategy-path user_data/profile_bias_strategies/LinearRegressionStrategy --timerange 20190101-20190401 --no-color
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
- `MACDStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategy --strategy-path user_data/profile_bias_strategies/MACDStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACDStrategy --strategy-path user_data/profile_bias_strategies/MACDStrategy --timerange 20190101-20190401 --no-color
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
- `MACD_TRI_EMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRI_EMA --strategy-path user_data/profile_bias_strategies/MACD_TRI_EMA --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRI_EMA --strategy-path user_data/profile_bias_strategies/MACD_TRI_EMA --timerange 20190101-20190401 --no-color
  ```
- `MFI`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MFI --strategy-path user_data/profile_bias_strategies/MFI --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MFI --strategy-path user_data/profile_bias_strategies/MFI --timerange 20190101-20190401 --no-color
  ```
- `MacdAdxStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdAdxStrategy --strategy-path user_data/profile_bias_strategies/MacdAdxStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdAdxStrategy --strategy-path user_data/profile_bias_strategies/MacdAdxStrategy --timerange 20190101-20190401 --no-color
  ```
- `MacdZeroCrossStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdZeroCrossStrategy --strategy-path user_data/profile_bias_strategies/MacdZeroCrossStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdZeroCrossStrategy --strategy-path user_data/profile_bias_strategies/MacdZeroCrossStrategy --timerange 20190101-20190401 --no-color
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
- `MultiMA_TSL3`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy MultiMA_TSL3 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/MultiMA_TSL3 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL3 --strategy-path user_data/profile_bias_strategies/MultiMA_TSL3 --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiMA_TSL3 --strategy-path user_data/profile_bias_strategies/MultiMA_TSL3 --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `MultiOffsetLamboV0`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiOffsetLamboV0 --strategy-path user_data/profile_bias_strategies/MultiOffsetLamboV0 --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MultiOffsetLamboV0 --strategy-path user_data/profile_bias_strategies/MultiOffsetLamboV0 --timerange 20190101-20190401 --no-color
  ```
- `MyStratV1`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MyStratV1 --strategy-path user_data/profile_bias_strategies/MyStratV1 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MyStratV1 --strategy-path user_data/profile_bias_strategies/MyStratV1 --timerange 20190101-20190401 --no-color
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
- `OmaGann`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy OmaGann --strategy-path user_data/profile_bias_strategies/OmaGann --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy OmaGann --strategy-path user_data/profile_bias_strategies/OmaGann --timerange 20190101-20190401 --no-color
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
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SAR --strategy-path user_data/profile_bias_strategies/SAR --timerange 20190101-20190401 --no-color
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
- `SMAOffset_Hippocritical_dca`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffset_Hippocritical_dca --strategy-path user_data/profile_bias_strategies/SMAOffset_Hippocritical_dca --timerange 20190101-20190401 --no-color
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
- `Sar`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Sar --strategy-path user_data/profile_bias_strategies/Sar --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Sar --strategy-path user_data/profile_bias_strategies/Sar --timerange 20190101-20190401 --no-color
  ```
- `Scalp`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Scalp --strategy-path user_data/profile_bias_strategies/Scalp --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Scalp --strategy-path user_data/profile_bias_strategies/Scalp --timerange 20190101-20190401 --no-color
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
- `SuperTrend`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SuperTrend --strategy-path user_data/profile_bias_strategies/SuperTrend --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SuperTrend --strategy-path user_data/profile_bias_strategies/SuperTrend --timerange 20190101-20190401 --no-color
  ```
- `TD`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TD --strategy-path user_data/profile_bias_strategies/TD --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TD --strategy-path user_data/profile_bias_strategies/TD --timerange 20190101-20190401 --no-color
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
- `TheForce`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TheForce --strategy-path user_data/profile_bias_strategies/TheForce --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TheForce --strategy-path user_data/profile_bias_strategies/TheForce --timerange 20190101-20190401 --no-color
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
- `adaptive`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive --strategy-path user_data/profile_bias_strategies/adaptive --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive --strategy-path user_data/profile_bias_strategies/adaptive --timerange 20190101-20190401 --no-color
  ```
- `adxbbrsi2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy adxbbrsi2 --strategy-path user_data/profile_bias_strategies/adxbbrsi2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy adxbbrsi2 --strategy-path user_data/profile_bias_strategies/adxbbrsi2 --timerange 20190101-20190401 --no-color
  ```
- `bbandrsi`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbandrsi --strategy-path user_data/profile_bias_strategies/bbandrsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbandrsi --strategy-path user_data/profile_bias_strategies/bbandrsi --timerange 20190101-20190401 --no-color
  ```
- `bbrsi`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi --strategy-path user_data/profile_bias_strategies/bbrsi --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi --strategy-path user_data/profile_bias_strategies/bbrsi --timerange 20190101-20190401 --no-color
  ```
- `bbrsi4Freq`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi4Freq --strategy-path user_data/profile_bias_strategies/bbrsi4Freq --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bbrsi4Freq --strategy-path user_data/profile_bias_strategies/bbrsi4Freq --timerange 20190101-20190401 --no-color
  ```
- `conny`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy conny --strategy-path user_data/profile_bias_strategies/conny --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy conny --strategy-path user_data/profile_bias_strategies/conny --timerange 20190101-20190401 --no-color
  ```
- `cryptotankV2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV2 --strategy-path user_data/profile_bias_strategies/cryptotankV2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV2 --strategy-path user_data/profile_bias_strategies/cryptotankV2 --timerange 20190101-20190401 --no-color
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
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy hlhb --strategy-path user_data/profile_bias_strategies/hlhb --timerange 20190101-20190401 --no-color
  ```
- `keltnerchannel`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy keltnerchannel --strategy-path user_data/profile_bias_strategies/keltnerchannel --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy keltnerchannel --strategy-path user_data/profile_bias_strategies/keltnerchannel --timerange 20190101-20190401 --no-color
  ```
- `pmaxTest`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy pmaxTest --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/pmaxTest --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy pmaxTest --strategy-path user_data/profile_bias_strategies/pmaxTest --timerange 20200101-20220101 --no-color
  recursive  [recorded] freqtrade recursive-analysis --config user_data/expansion_configs/pmaxTest_startup_288.json --strategy pmaxTest --strategy-path user_data/profile_bias_strategies/pmaxTest --timerange 20190101-20190401 --no-color --startup-candle 288 576 2016 4032
  ```
- `simple_patterns`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy simple_patterns --strategy-path repos/TheoBrigitte_freqtrade/strategies/yodo --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/simple_patterns --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy simple_patterns --strategy-path user_data/profile_bias_strategies/simple_patterns --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy simple_patterns --strategy-path user_data/profile_bias_strategies/simple_patterns --timerange 20190101-20190401 --no-color
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

## Convergence candidates - 7 strategies

A warm-up exists at which every indicator stays inside the band.
That is not admission: the paired full-window run must still show
an identical trade list.

| Strategy | Profile | Chosen warm-up | Worst drift | Tested | Results |
|---|---|---|---|---|---|
| `AwesomeMacd` | `spot_long` | 336 candles | 0.0% on `adx` | 2026-09-02 06:51:58 | `user_data/convergence_logs/AwesomeMacd-ladder.log` |
| `Diamond` | `spot_long` | 288 candles | 0.0% on `None` | 2026-09-01 15:46:33 | `user_data/convergence_logs/Diamond-ladder.log` |
| `EasyInEasyOut` | `spot_long` | 1440 candles | 0.0% on `None` | 2026-09-01 15:48:12 | `user_data/convergence_logs/EasyInEasyOut-ladder.log` |
| `MACDRL` | `futures_long` | 2016 candles | 0.0% on `ema200_200` | 2026-09-02 07:27:57 | `user_data/convergence_logs/MACDRL-ladder.log` |
| `MACDRS` | `futures_long_short` | 2016 candles | 0.0% on `ema200_long_200` | 2026-09-02 07:30:14 | `user_data/convergence_logs/MACDRS-ladder.log` |
| `SlowPotato` | `spot_long` | 288 candles | 0.0% on `None` | 2026-09-01 16:15:31 | `user_data/convergence_logs/SlowPotato-ladder.log` |
| `StrategyTestV2` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 15:08:04 | `user_data/convergence_logs/StrategyTestV2-ladder.log` |

## Pending - 7 strategies

No hard failure and no verdict. Evidence is missing, which is
neither a pass nor a fail.

`Fakebuy`, `HyperStra_GSN_SMAOnly`, `InverseVolatilityPortfolio`, `RiskParityPortfolio`
`TGMA`, `haGradient`, `kalthetank`

## Attempted, no measurement - 60 strategies

No run under the current pipeline is recorded for these. The
original corpus sweep did attempt every row, but it ran in an
environment that did not establish the preconditions this audit
requires - which is the whole reason the pre-checks are being
redone - so its outcome is a hint about what to expect and never a
verdict. Where such a hint exists it is shown in brackets.

| Strategy | Wave | Status |
|---|---|---|
| `InformativeDecoratorTest` | `C_measurement_recovery` | `no run under the current runtime (historical hint: ValueError: Informative dataframe for (NEO/USDT, 30m, spot) is empty. Can't populate informative indicators.)` |
| `Strategy` | `C_measurement_recovery` | `no run under the current runtime (historical hint: 'stoploss' is a required property)` |
| `StrategyAnalysis` | `C_measurement_recovery` | `no run under the current runtime (historical hint: TypeError: Can't instantiate abstract class StrategyAnalysis without an implementation for abstract method 'populate_indicators')` |
| `TestStrategyLegacyV1` | `C_measurement_recovery` | `no run under the current runtime (historical hint: Strategy Interface v1 is no longer supported. Please update your strategy to implement `populate_indicators`, `populate_entry_trend` and)` |
| `TestStrategyNoImplements` | `C_measurement_recovery` | `no run under the current runtime (historical hint: `populate_entry_trend` or `populate_buy_trend` must be implemented.)` |
| `ThreeCommasStrategy` | `C_measurement_recovery` | `no run under the current runtime (historical hint: Impossible to load Strategy 'ThreeCommasStrategy'. This class does not exist or contains Python code errors.)` |
| `YourStrat` | `C_measurement_recovery` | `no run under the current runtime (historical hint: TypeError: Can't instantiate abstract class YourStrat without an implementation for abstract method 'populate_indicators')` |
| `freqai_rl_test_strat` | `C_measurement_recovery` | `no run under the current runtime (historical hint: Timeframe needs to be set in either configuration or as cli argument `--timeframe 5m`)` |
| `freqai_test_classifier` | `C_measurement_recovery` | `no run under the current runtime (historical hint: Timeframe needs to be set in either configuration or as cli argument `--timeframe 5m`)` |
| `freqai_test_multimodel_classifier_strat` | `C_measurement_recovery` | `no run under the current runtime (historical hint: Timeframe needs to be set in either configuration or as cli argument `--timeframe 5m`)` |
| `freqai_test_multimodel_strat` | `C_measurement_recovery` | `no run under the current runtime (historical hint: Timeframe needs to be set in either configuration or as cli argument `--timeframe 5m`)` |
| `freqai_test_strat` | `C_measurement_recovery` | `no run under the current runtime (historical hint: Timeframe needs to be set in either configuration or as cli argument `--timeframe 5m`)` |
| `A9AV` | `not_scheduled` | `no run under the current runtime (historical hint: AttributeError: 'Rolling' object has no attribute 'any')` |
| `AstroQAV4` | `not_scheduled` | `no run under the current runtime (historical hint: freqAI is not enabled. Please enable it in your config to use this strategy.)` |
| `AwesomeMacdS` | `not_scheduled` | `no run under the current runtime (historical hint: engine exited with code 0 but produced no summary (no trades at all, or output not parsed))` |
| `BBMod` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: Invalid value '0' for dtype 'datetime64[ms, UTC]')` |
| `BB_RPB_TSL_Tranz` | `not_scheduled` | `no run under the current runtime (historical hint: numpy.exceptions.DTypePromotionError: The DType <class 'numpy.dtypes.StrDType'> could not be promoted by <class 'numpy.dtypes._PyFloatDType'>. This means that n)` |
| `BB_RPB_TSLmeneguzzo` | `not_scheduled` | `no run under the current runtime (historical hint: numpy.exceptions.DTypePromotionError: The DType <class 'numpy.dtypes.StrDType'> could not be promoted by <class 'numpy.dtypes._PyFloatDType'>. This means that n)` |
| `BcmbigzDevelop` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: Invalid value '1' for dtype 'bool')` |
| `BinClucMadDevelop` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: Invalid value '1' for dtype 'bool')` |
| `BinClucMadSMADevelop` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: Invalid value '1' for dtype 'bool')` |
| `BinHV27_werkkrew` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: BinHV27_werkkrew.min_roi_reached_entry() takes 2 positional arguments but 4 were given)` |
| `ClucHAnix5m` | `not_scheduled` | `no run under the current runtime (historical hint: engine exited with code 0 but produced no summary (no trades at all, or output not parsed))` |
| `ClucHAnix_BB_RPB` | `not_scheduled` | `no run under the current runtime` |
| `ClucHAnix_BB_RPB_HO2` | `not_scheduled` | `no run under the current runtime (historical hint: numpy._core._exceptions._ArrayMemoryError: Unable to allocate 337. MiB for an array with shape (48, 920831) and data type float64)` |
| `ClucHAnix_BB_RPB_MOD` | `not_scheduled` | `no run under the current runtime` |
| `Cluckie` | `not_scheduled` | `no run under the current runtime (historical hint: engine exited with code 0 but produced no summary (no trades at all, or output not parsed))` |
| `CoreStrategy` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: Invalid value '1' for dtype 'bool')` |
| `CryptoFrogNFI` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time')` |
| `CryptoFrogNFIHO1A` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time')` |
| `CryptoFrogOffset` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time')` |
| `DIV_v1` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: NDFrame.fillna() got an unexpected keyword argument 'method')` |
| `Guacamole` | `not_scheduled` | `no run under the current runtime (historical hint: TIMED OUT)` |
| `Kamaflage` | `not_scheduled` | `no run under the current runtime (historical hint: TIMED OUT)` |
| `MacheteV8b` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time')` |
| `MacheteV8bRallimod` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time')` |
| `MacheteV8bRallimod2` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time')` |
| `MultiMA_TSL` | `not_scheduled` | `no run under the current runtime (historical hint: ValueError: cannot reindex on an axis with duplicate labels)` |
| `MyStrategyNew10` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: attribute name must be string, not 'NoneType')` |
| `NFI46Frog` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time')` |
| `NFI4Frog` | `not_scheduled` | `no run under the current runtime (historical hint: TypeError: IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time')` |
| `NowoIchimoku1hV1` | `not_scheduled` | `no run under the current runtime (historical hint: KeyError: 'buy')` |
| `ONS_Portfolio` | `not_scheduled` | `no run under the current runtime (historical hint: TIMED OUT)` |
| `RSIDivTirail` | `not_scheduled` | `no run under the current runtime (historical hint: OSError: Cannot save file into a non-existent directory: 'user_data\csvs')` |
| `RaposaDivergenceV1` | `not_scheduled` | `no run under the current runtime (historical hint: engine exited with code 0 but produced no summary (no trades at all, or output not parsed))` |
| `ReinforcedSmoothScalpS` | `not_scheduled` | `no run under the current runtime (historical hint: engine exited with code 0 but produced no summary (no trades at all, or output not parsed))` |
| `Schism` | `not_scheduled` | `no run under the current runtime (historical hint: Unexpected error KeyError('price_side') calling <bound method Schism.confirm_trade_entry of <Schism-0318.Schism object at)` |
| `Schism2` | `not_scheduled` | `no run under the current runtime (historical hint: Unexpected error KeyError('price_side') calling <bound method Schism2.confirm_trade_entry of <Schism-v2.Schism2 object at)` |
| `Schism5` | `not_scheduled` | `no run under the current runtime (historical hint: TIMED OUT)` |
| `Schism6` | `not_scheduled` | `no run under the current runtime (historical hint: KeyError: 'inf-rsi')` |
| `SmartMoneyStrategyHyperopt` | `not_scheduled` | `no run under the current runtime (historical hint: WRONG SUBJECT: strategy declared 30m, engine computed on 1h)` |
| `Solipsis3` | `not_scheduled` | `no run under the current runtime (historical hint: Unexpected error KeyError('price_side') calling <bound method Solipsis3.confirm_trade_entry of <Solipsis-v3-fuck (1).Solipsis3)` |
| `Solipsis5` | `not_scheduled` | `no run under the current runtime (historical hint: Unexpected error KeyError('price_side') calling <bound method Solipsis5.confirm_trade_entry of <Solipsis-v2.5.Solipsis5 object)` |
| `SolipsisCon` | `not_scheduled` | `no run under the current runtime` |
| `SqueezeMomentum` | `not_scheduled` | `no run under the current runtime (historical hint: OSError: Cannot save file into a non-existent directory: 'user_data\csvs')` |
| `Tank5ModulusDCA` | `not_scheduled` | `no run under the current runtime (historical hint: TIMED OUT)` |
| `Tank5ModulusDCAV3` | `not_scheduled` | `no run under the current runtime (historical hint: numpy._core._exceptions._ArrayMemoryError: Unable to allocate 1.61 MiB for an array with shape (210529,) and data type float64)` |
| `qrsi` | `not_scheduled` | `no run under the current runtime (historical hint: ValueError: Invalid frequency: 15m. Failed to parse with error message: ValueError("'m' is no longer supported for offsets. Please use 'ME' instead."))` |
| `tacos1` | `not_scheduled` | `no run under the current runtime (historical hint: No data found. Terminating.)` |
| `turbov8` | `not_scheduled` | `no run under the current runtime (historical hint: engine exited with code 0 but produced no summary (no trades at all, or output not parsed))` |

## Exclusion unconfirmed - 163 strategies

`excluded` is a verdict, and this audit does not issue one on
somebody else's measurement or on the absence of one. These rows
would have been excluded on exactly that, so they are held here
until a measurement of ours settles them either way. Nothing about
them is hidden by the change of name: the decisive reason and the
basis stay on the row, and the work that would settle it is in
`open_work`.

| Held on | Basis | Strategies |
|---|---|---:|
| `no_verdict_on_lookahead` | `no_finding` | 56 |
| `no_verdict_on_lookahead_and_recursive` | `no_finding` | 51 |
| `lookahead_found` | `inherited` | 38 |
| `recursive_bias_unverified` | `no_finding` | 12 |
| `no_trades_in_full_measurement` | `inherited` | 5 |
| `no_verdict_on_recursive` | `no_finding` | 1 |

This is not a softening. A row here may well end up excluded - the
38 held on an inherited look-ahead finding probably will, because a
limited environment does not invent bias. It ends up there on our
own evidence or not at all.

## Not passing - 236 strategies, by decisive reason

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
stay admitted - E0 and E1 are frozen and this table decides nothing -
and they are queued for the ladder as `recursive_ladder_pending`.

### What each exclusion rests on

The decisive reason names the gate that stopped a row. It does not
say whether that gate produced evidence, and the difference decides
whether the row is finished with or waiting on us.

| Basis | Meaning | Strategies |
|---|---|---:|
| `own_measurement` | a disqualifying result measured here, from this implementation | 137 |
| `blocked` | the strategy did not run, so nothing about it was judged | 99 |

Only `own_measurement` is a closed case. The other three carry the
work that would settle them in `open_work`, and the selftest fails if
one of them carries none.

| Reason | Meaning | Strategies |
|---|---|---:|
| `lookahead_found` | reads data it could not have had at the time | 33 |
| `technical_trap_found` | carries a published backtesting trap | 40 |
| `strategy_does_not_run` | fails before it can be measured; the message is in runtime_failure | 99 |
| `recursive_bias_found` | indicator value still drifts at every warm-up the ladder can reach | 53 |
| `no_trades_in_full_measurement` | never trades over the full window | 11 |


### Reason by wave

| Reason | `B_warmup_refusal` | `C_measurement_recovery` | `D_recursive_drift` | `not_scheduled` |
|---|---|---|---|---|
| `lookahead_found` | 0 | 15 | 0 | 18 |
| `technical_trap_found` | 0 | 0 | 0 | 40 |
| `strategy_does_not_run` | 0 | 99 | 0 | 0 |
| `recursive_bias_found` | 3 | 18 | 14 | 18 |
| `no_trades_in_full_measurement` | 0 | 10 | 0 | 1 |

### `lookahead_found` - 33

Reads data it could not have had at the time.

Wave `C_measurement_recovery` - 15:

`ARIMA_15`, `NfiNextModded`, `NostalgiaForInfinityNext`, `NostalgiaForInfinityNext772`
`NostalgiaForInfinityNextV7155`, `NostalgiaForInfinityNext_ChangeToTower_V5_2`, `NostalgiaForInfinityNext_ChangeToTower_V5_3`, `NostalgiaForInfinityNext_ChangeToTower_V6`
`NostalgiaForInfinityNext_maximizer`, `NostalgiaForInfinityV7_7_2`, `NostalgiaForInfinityXw`, `Obelisk_Ichimoku_Slow_v1_3`
`Obelisk_Ichimoku_ZEMA_v1`, `Stinkfist`, `ichiV1_Marius`

Wave `not_scheduled` - 18:

`BreakoutStrategy`, `FakeoutStrategy`, `Heracles`, `HyperStra_SMAOnly`
`IchiVwapAdx`, `MaxSharpePortfolio`, `MinimumVariancePortfolio`, `MomentumRegimeBasket`
`NOTankAi_17`, `NOTankAi_19`, `PolymarketPortfolio`, `Precognition`
`RsiquiV2`, `RsiquiV5`, `TSPredict`, `Zeus`
`custom`, `tsp0chicken`

### `technical_trap_found` - 40

Carries a published backtesting trap.

Wave `not_scheduled` - 40:

`ADXMomentum`, `BigPete`, `CBPete9`, `CombinedBinHAndClucHyper`
`E0V1EN`, `EI3v2_tag_cofi_green`, `ElliotV8_original`, `ElliotV8_original_ichiv2`
`ElliotV8_original_ichiv2OH`, `ElliotV8_original_ichiv3`, `Elliotv8`, `FastSupertrend_optim3`
`FastSupertrend_optim3_rsi_70`, `FastSupertrend_optim3_rsi_75`, `FastSupertrend_optim3_rsi_752`, `FastSupertrend_optim3_rsi_75fix`
`FastSupertrend_optim3_rsi_75fix_signal`, `FastSupertrend_optim3_rsi_75lev`, `FastSupertrend_optim3_rsi_75sell`, `FastSupertrend_optim3_rsi_80`
`FastSupertrend_optim_quick`, `FastSupertrend_optim_quick2`, `FastSupertrend_optim_quick3`, `FastSupertrend_optim_quick4`
`FastSupertrend_optim_quick5`, `NASOSv4`, `NASOSv5_mod1`, `NASOSv5_mod1_DanMod`
`NASOSv5_mod2`, `NASOSv5_mod3`, `PrawnstarOBV`, `SMAIP3v2`
`SimpleHopt1Along`, `SimpleHopt1Ashort`, `SimpleHoptS`, `WTX3`
`XebTradeStrat`, `ichi`, `tesla4`, `tesla7`

### `strategy_does_not_run` - 99

Fails before it can be measured; the message is in runtime_failure.

| Failure | Strategies | Which |
|---|---:|---|
| Timeframe needs to be set in either configuration or as cli argument `--timeframe 5m` | 10 | `Chained`, `EnsembleStrategy`, `EnsembleStrategyV1`, `EnsembleStrategyV2`, `FreqaiExampleStrategy`, `LitmusGoodMinMaxClassificationStrategy`, `MultiTargetClassifierTestStrategy`, `MultiTargetRegressorTestStrategy`, `QuickAdapterV3`, `ScalpingCCI` |
| The DType <class 'numpy.dtypes.StrDType'> could not be promoted by <class 'numpy.dtypes._PyFloatDType'>. This means that no common DType exists for the given | 8 | `Danke`, `FSupertrendStrategyBTC`, `FSupertrendStrategyETH`, `FastSupertrend`, `FastSupertrendOpt`, `MultiMA_TSL5`, `SuperTrendPure`, `Supertrend` |
| cannot import name '__version__' from 'freqtrade' (unknown location) | 4 | `DualModelPolymarketPortfolio`, `EmaCrossStrategy`, `PolymarketMeanReversionStrategy`, `PolymarketMomentumStrategy` |
| Configuration error: 'stoploss' is a required property | 3 | `AdaptiveRenkoStrategy`, `ClucCrypROI`, `ClucCrypSlow` |
| freqAI is not enabled. Please enable it in your config to use this strategy. | 3 | `RLStrategy`, `TankAi`, `TankAiRevival` |
| `populate_exit_trend` or `populate_sell_trend` must be implemented. | 2 | `ClucHAnix_BB_RPB_TraNz`, `SimpleRiskFilterStrategy` |
| IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time' | 2 | `Dyna_opti`, `Solipsis4` |
| You are using the `populate_any_indicators()` function which was deprecated on March 1, 2023. Please refer to the strategy migration guide to use the new | 2 | `WTAI`, `WTRSIAI` |
| Invalid value 'False' for dtype 'float64' | 2 | `new_turtle`, `new_turtle_roi` |
| Remora API key missing. Set REMORA_API_KEY env var. | 1 | `AdvancedRiskFilterStrategy` |
| Length of values (180) does not match length of index (82) | 1 | `Astro` |
| Impossible to load Strategy 'AutoArimaTripleV1'. This class does not exist or contains Python code errors. | 1 | `AutoArimaTripleV1` |
| Impossible to load Strategy 'BBRSI'. This class does not exist or contains Python code errors. | 1 | `BBRSI` |
| Impossible to load Strategy 'BB_RPB_3c'. This class does not exist or contains Python code errors. | 1 | `BB_RPB_3c` |
| Impossible to load Strategy 'BaseStrategy'. This class does not exist or contains Python code errors. | 1 | `BaseStrategy` |
| Encountered all NA values | 1 | `BestSingleAssetPortfolio` |
| Impossible to load Strategy 'BinanceStream'. This class does not exist or contains Python code errors. | 1 | `BinanceStream` |
| Impossible to load Strategy 'BlueEyes_MPP_v1'. This class does not exist or contains Python code errors. | 1 | `BlueEyes_MPP_v1` |
| Impossible to load Strategy 'ClucHAnix_BB_RPB_MOD_trailing_buy'. This class does not exist or contains Python code errors. | 1 | `ClucHAnix_BB_RPB_MOD_trailing_buy` |
| Invalid value '1' for dtype 'bool' | 1 | `CombinedBinHAndClucV6H` |
| Impossible to load Strategy 'CopyLitmusMinMaxBroadClassificationStrategy'. This class does not exist or contains Python code errors. | 1 | `CopyLitmusMinMaxBroadClassificationStrategy` |
| 'CryptoFrogNFI2' object has no attribute 'buy_pump_threshold_7'. Did you mean: 'buy_pump_threshold_1'? | 1 | `CryptoFrogNFI2` |
| Impossible to load Strategy 'CryptoPredictionTraining'. This class does not exist or contains Python code errors. | 1 | `CryptoPredictionTraining` |
| buffer source array is read-only | 1 | `DWT` |
| Impossible to load Strategy 'Enchilada'. This class does not exist or contains Python code errors. | 1 | `Enchilada` |
| Impossible to load Strategy 'FileLoadingStrategy'. This class does not exist or contains Python code errors. | 1 | `FileLoadingStrategy` |
| Impossible to load FreqaiModel 'CatboostClassifier'. This class does not exist or contains Python code errors. | 1 | `FreqaiExampleHybridStrategy` |
| Invalid value '114.31926513711869' for dtype 'int64' | 1 | `GPR` |
| index 14 is out of bounds for axis 0 with size 2 | 1 | `GodStra` |
| Impossible to load Strategy 'GymStrategy'. This class does not exist or contains Python code errors. | 1 | `GymStrategy` |
| 'tuple' object has no attribute 'items' | 1 | `HLHB` |
| Impossible to load Strategy 'IchimokuStrategy'. This class does not exist or contains Python code errors. | 1 | `IchimokuStrategy` |
| Impossible to load Strategy 'Ichimoku_SenkouSpanCross'. This class does not exist or contains Python code errors. | 1 | `Ichimoku_SenkouSpanCross` |
| Impossible to load Strategy 'KMM'. This class does not exist or contains Python code errors. | 1 | `KMM` |
| Impossible to load Strategy 'LitmusEntryRollClassificationStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusEntryRollClassificationStrategy` |
| Impossible to load Strategy 'LitmusMLDPStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusMLDPStrategy` |
| Impossible to load FreqaiModel 'LitmusMultiTargetClassifier'. This class does not exist or contains Python code errors. | 1 | `LitmusMetaStrategy` |
| Impossible to load Strategy 'LitmusMinMaxBroadClassificationStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusMinMaxBroadClassificationStrategy` |
| Impossible to load Strategy 'LitmusMinMaxClassificationStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusMinMaxClassificationStrategy` |
| Impossible to load Strategy 'LitmusMinMaxRegretClassificationStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusMinMaxRegretClassificationStrategy` |
| Impossible to load Strategy 'LitmusMinMaxSegmentClassificationStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusMinMaxSegmentClassificationStrategy` |
| Impossible to load Strategy 'LitmusMinMaxStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusMinMaxStrategy` |
| Impossible to load Strategy 'LitmusMinMaxTrendStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusMinMaxTrendStrategy` |
| Impossible to load Strategy 'LitmusSimpleStrategy'. This class does not exist or contains Python code errors. | 1 | `LitmusSimpleStrategy` |
| NDFrame.replace() got an unexpected keyword argument 'method' | 1 | `LongShortRangeTradingMachetesV1` |
| Impossible to load Strategy 'MKR'. This class does not exist or contains Python code errors. | 1 | `MKR` |
| process exit 0 without a readable backtest archive | 1 | `MasterMoniGoManiHyperStrategy` |
| Impossible to load Strategy 'MlpSpeculativeStrategy'. This class does not exist or contains Python code errors. | 1 | `MlpSpeculativeStrategy` |
| Cannot compare dtypes int64 and datetime64[ms, UTC] | 1 | `MomentumRegimeBasket15m` |
| 'buy-ma-10' | 1 | `MultiMa` |
| Configuration error: The config stoploss needs to be different from 0 to avoid problems with sell orders. | 1 | `NoLost` |
| Impossible to load Strategy 'Persia'. This class does not exist or contains Python code errors. | 1 | `Persia` |
| PMAX() got an unexpected keyword argument 'atrperiod'. Did you mean 'period'? | 1 | `Pmax` |
| Invalid value '1' for dtype 'str'. Value should be a string or missing value, got 'int' instead. | 1 | `PnF` |
| Could not find pair source at './strategy/PolymarketLogicalArb/freqtrade_pair_mapping.csv'. Update PAIR_SOURCE_PATH in the strategy. | 1 | `PolymarketLogicalArbStrategy` |
| Impossible to load Strategy 'Prediction_Strategy'. This class does not exist or contains Python code errors. | 1 | `Prediction_Strategy` |
| 'proton_parameters' | 1 | `Proton` |
| invalid literal for int() with base 10: '1h' | 1 | `QuickBuyStrategy` |
| Impossible to load FreqaiModel 'ReforceXY'. This class does not exist or contains Python code errors. | 1 | `RLAgentStrategy` |
| 'adx' | 1 | `RenkoYolo` |
| Cannot determine parameter space for ttf_length. | 1 | `SMAOPv1_TTF` |
| module 'custom_indicators' has no attribute 'bollinger_bands' | 1 | `Solipsis6` |
| module 'custom_indicators' has no attribute 'fib_ret' | 1 | `SolipsisMM` |
| SuperHV27.min_roi_reached_entry() takes 2 positional arguments but 4 were given | 1 | `SuperHV27` |
| cannot reindex on an axis with duplicate labels | 1 | `Test_MAMA4` |
| Impossible to load Strategy 'TrainCatBoostStrategy'. This class does not exist or contains Python code errors. | 1 | `TrainCatBoostStrategy` |
| No data found. Terminating. | 1 | `TuplaBollinger` |
| Impossible to load Strategy 'TwoCandleTheory'. This class does not exist or contains Python code errors. | 1 | `TwoCandleTheory` |
| '<' not supported between instances of 'float' and 'method' | 1 | `UpSliceStrategy` |
| Cannot determine parameter space for mfi_length. | 1 | `WTHO` |
| Informative dataframe for (ETH/BTC, 1h, spot) is empty. Can't populate informative indicators. | 1 | `multi_tf` |
| Can't instantiate abstract class thetank2 without an implementation for abstract method 'populate_indicators' | 1 | `thetank2` |

### `recursive_bias_found` - 53

Indicator value still drifts at every warm-up the ladder can reach.

Wave `B_warmup_refusal` - 3:

`ForexRobootSuperScalper`, `HSI`, `Macd`

Wave `C_measurement_recovery` - 18:

`ARIMASTR`, `BBMod1`, `BB_RPB_TSL`, `BB_RPB_TSL_2`
`BB_RPB_TSL_BI`, `BB_RPB_TSL_BIV1`, `BB_RPB_TSL_SMA_Tranz`, `BB_RPB_TSL_SMA_Tranz_TB_1_1_1`
`BB_RPB_TSL_SMA_Tranz_TB_MOD`, `GeneStrategy`, `GeneStrategy_v2`, `GeneTrader_gen10_1734895087_6007`
`GeneTrader_gen5_1735014093_4541`, `KitchenSink`, `MultiMA_TSL3_Mod`, `falconTrader`
`newstrategy53`, `newstrategy53_22`

Wave `D_recursive_drift` - 14:

`BigZ0307HO`, `BigZ0407`, `BigZ0407HO`, `BigZ04HO`
`BigZ04HO2`, `BigZ06`, `BigZ07`, `ClucHAnix_BB_RPB_MOD2_ROI`
`ClucHAnix_BB_RPB_MOD_CTT`, `ClucHAnix_BB_RPB_MOD_E0V1E_ROI`, `ObvTrendStrategy`, `flawless_lambo`
`lambotest`, `tacos`

Wave `not_scheduled` - 18:

`BcmbigzV1`, `BeastBotXBLR6`, `BeastBotXBLR7`, `BigZ04`
`GKD_CT`, `GoldHedgeZeroMACD`, `HurstCycle7`, `HurstCycleV5RSI`
`HurstCycleV6`, `NOTankAi_15`, `NOTankAi_15_Cleaned`, `NOTankAi_15_Cleaned_v2`
`NostalgiaForInfinityX5`, `NostalgiaForInfinityX6`, `NostalgiaForInfinityX7`, `NotAnotherSMAOffSetStrategy_V2`
`TrendRiderStrategy`, `pcb20`

### `no_trades_in_full_measurement` - 11

Never trades over the full window.

Wave `C_measurement_recovery` - 10:

`BasketStrategy`, `BreakEven`, `DoesNothingStrategy`, `FundingCarry`
`Miku_PP_v3`, `MostOfAll`, `MyStrategyTemplate`, `Obelisk_3EMA_StochRSI_ATR`
`ViN`, `ep3mas2`

Wave `not_scheduled` - 1:

`Insomnia_short`

## Expansion wave

| Wave | Strategies |
|---|---:|
| `not_scheduled` | 390 |
| `C_measurement_recovery` | 230 |
| `D_recursive_drift` | 124 |
| `B_warmup_refusal` | 82 |
| `E0_strict67` | 67 |
| `A_pending_diagnostics` | 7 |

## Open work

| Item | Strategies |
|---|---:|
| `lookahead_remeasure_pending` | 158 |
| `recursive_ladder_pending` | 109 |
| `first_measurement_in_current_runtime` | 60 |
| `needs_a_look` | 56 |
| `convergence_not_converged_within_ladder` | 53 |
| `refuse_repair` | 21 |
| `repair_attempted` | 16 |
| `convergence_inconclusive` | 15 |
| `paired_full_window_equivalence` | 7 |
| `full_window_measurement_pending` | 5 |
| `repair_withdrawn` | 4 |
| `to_be_fixed` | 2 |

Per-row detail, including every evidence path, is in
`STRATEGY_STATUS.csv`.
