# Strategy status - current evidence for all 900 rows

**Generated 2026-09-01 15:00:36 by `strategy_status.py`.** Regenerate it rather than editing it.

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
file's time and is labelled `log_mtime` for that reason. 343 of 900 rows
have neither and are left empty rather than given an invented time.

## Measurement

| | Strategies |
|---|---:|
| in the manifest | 900 |
| measured at all | 688 |
| produced trades | 661 |
| carrying a run time | 557 |

## Cohort

| Cohort | Strategies |
|---|---:|
| `excluded` | 498 |
| `convergence_candidate` | 257 |
| `E0_strict67` | 67 |
| `not_tested_in_current_runtime` | 60 |
| `E1_expanded` | 11 |
| `pending` | 7 |

## Passing - 78 strategies

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
| `AlwaysBuy` | `spot_long` | `E1_expanded` | 32359 | `baseline` | - | - |
| `BinHV45` | `spot_long` | `E1_expanded` | 749 | `baseline` | - | - |
| `BinHV45_kanaxe` | `spot_long` | `E1_expanded` | 1798 | `baseline` | - | - |
| `BinHV45_stash` | `spot_long` | `E1_expanded` | 1700 | `baseline` | - | - |
| `BinHV45_werkkrew` | `spot_long` | `E1_expanded` | 760 | `baseline` | - | - |
| `BollingerBandStrategy` | `spot_long` | `E1_expanded` | 16302 | `baseline` | - | - |
| `CCI_BB` | `spot_long` | `E1_expanded` | 926 | `baseline` | - | - |
| `HourBasedStrategy_5m` | `spot_long` | `E1_expanded` | 11784 | `baseline` | - | - |
| `NowoIchimoku5mV2` | `spot_long` | `E1_expanded` | 49 | `native` | 2026-08-31 15:19:45 | `user_data/profile_smoke/NowoIchimoku5mV2-2026-08-31_15-19-45.zip` |
| `ObeliskIM_v1_1` | `spot_long` | `E1_expanded` | 64 | `native` | 2026-08-31 15:20:09 | `user_data/profile_smoke/ObeliskIM_v1_1-2026-08-31_15-20-09.zip` |
| `simple_patterns` | `spot_long` | `E1_expanded` | 1845 | `native` | 2026-08-31 15:55:52 | `user_data/profile_smoke/simple_patterns-2026-08-31_15-55-52.zip` |

## Convergence candidates - 257 strategies

A warm-up exists at which every indicator stays inside the band.
That is not admission: the paired full-window run must still show
an identical trade list.

| Strategy | Profile | Chosen warm-up | Worst drift | Tested | Results |
|---|---|---|---|---|---|
| `ActionZone` | `spot_long` | 90 candles | 0.008% on `slowMA` | 2026-09-01 12:59:33 | `user_data/convergence_logs/ActionZone-ladder.log` |
| `AdaptiveMAStrategy` | `spot_long` | 288 candles | 0.0% on `kama_fast` | 2026-09-01 12:07:18 | `user_data/convergence_logs/AdaptiveMAStrategy-ladder.log` |
| `AdxSmas` | `spot_long` | 336 candles | 0.0% on `adx` | 2026-09-01 13:33:11 | `user_data/convergence_logs/AdxSmas-ladder.log` |
| `AdxSmasS` | `futures_short` | 336 candles | 0.0% on `adx` | 2026-09-01 13:34:00 | `user_data/convergence_logs/AdxSmasS-ladder.log` |
| `AdxStrengthStrategy` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 12:07:43 | `user_data/convergence_logs/AdxStrengthStrategy-ladder.log` |
| `AlligatorStrategy` | `spot_long` | 720 candles | 0.0% on `stoch_rsi` | 2026-09-01 13:00:43 | `user_data/convergence_logs/AlligatorStrategy-ladder.log` |
| `AlmgrenChrissStrategy` | `futures_long_short` | 192 candles | 0.0% on `rsi` | 2026-09-01 13:01:08 | `user_data/convergence_logs/AlmgrenChrissStrategy-ladder.log` |
| `Apollo11` | `spot_long` | 1344 candles | 0.0% on `s1_ema_md` | 2026-09-01 13:01:32 | `user_data/convergence_logs/Apollo11-ladder.log` |
| `AroonTrendStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:08:07 | `user_data/convergence_logs/AroonTrendStrategy-ladder.log` |
| `AtrTrailingStopStrategy` | `spot_long` | 288 candles | 0.0% on `atr` | 2026-09-01 12:08:31 | `user_data/convergence_logs/AtrTrailingStopStrategy-ladder.log` |
| `AverageStrategy` | `spot_long` | 84 candles | 0.0% on `maShort` | 2026-09-01 13:34:48 | `user_data/convergence_logs/AverageStrategy-ladder.log` |
| `BBRSI4cust` | `spot_long` | 192 candles | 0.0% on `plus_di` | 2026-09-01 12:08:55 | `user_data/convergence_logs/BBRSI4cust-ladder.log` |
| `BBRSINaiveStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 12:09:19 | `user_data/convergence_logs/BBRSINaiveStrategy-ladder.log` |
| `BBRSIOptim2020Strategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:09:44 | `user_data/convergence_logs/BBRSIOptim2020Strategy-ladder.log` |
| `BBRSIOptimStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:10:08 | `user_data/convergence_logs/BBRSIOptimStrategy-ladder.log` |
| `BBRSIOptimizedStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 13:02:19 | `user_data/convergence_logs/BBRSIOptimizedStrategy-ladder.log` |
| `BBRSIStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 12:10:32 | `user_data/convergence_logs/BBRSIStrategy-ladder.log` |
| `BBRSITV` | `spot_long` | 2016 candles | 0.0% on `rsi` | 2026-09-01 13:02:44 | `user_data/convergence_logs/BBRSITV-ladder.log` |
| `BB_RPB_TSL_RNG` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 13:35:37 | `user_data/convergence_logs/BB_RPB_TSL_RNG-ladder.log` |
| `BB_RPB_TSL_RNG_TBS` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 13:36:25 | `user_data/convergence_logs/BB_RPB_TSL_RNG_TBS-ladder.log` |
| `BB_RPB_TSL_RNG_TBS_GOLD` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 13:37:28 | `user_data/convergence_logs/BB_RPB_TSL_RNG_TBS_GOLD-ladder.log` |
| `BB_RPB_TSL_RNG_VWAP` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 12:10:58 | `user_data/convergence_logs/BB_RPB_TSL_RNG_VWAP-ladder.log` |
| `BB_RTR` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 12:11:28 | `user_data/convergence_logs/BB_RTR-ladder.log` |
| `BBands` | `spot_long` | 1440 candles | 0.0% on `adx` | 2026-09-01 13:04:20 | `user_data/convergence_logs/BBands-ladder.log` |
| `BBandsRSI` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 13:04:45 | `user_data/convergence_logs/BBandsRSI-ladder.log` |
| `Babico_SMA5xBBmid` | `spot_long` | 30 candles | 0.0% on `bb_low` | 2026-09-01 13:38:15 | `user_data/convergence_logs/Babico_SMA5xBBmid-ladder.log` |
| `BbWidthExpansionStrategy` | `spot_long` | 288 candles | 0.0% on `bb_upper` | 2026-09-01 12:11:52 | `user_data/convergence_logs/BbWidthExpansionStrategy-ladder.log` |
| `BbandRsi` | `spot_long` | 1440 candles | 0.0% on `bb_lowerband` | 2026-09-01 13:39:05 | `user_data/convergence_logs/BbandRsi-ladder.log` |
| `BbandRsiRolling` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 13:39:54 | `user_data/convergence_logs/BbandRsiRolling-ladder.log` |
| `BigZ07Next` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_5m` | 2026-09-01 12:15:15 | `user_data/convergence_logs/BigZ07Next-ladder.log` |
| `BigZ07Next2` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_5m` | 2026-09-01 12:15:43 | `user_data/convergence_logs/BigZ07Next2-ladder.log` |
| `BinClucMadV1` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:16:09 | `user_data/convergence_logs/BinClucMadV1-ladder.log` |
| `BinHV27` | `spot_long` | 576 candles | 0.0% on `adx` | 2026-09-01 13:40:42 | `user_data/convergence_logs/BinHV27-ladder.log` |
| `BinHV45HO` | `spot_long` | 1440 candles | 0.0% on `mid` | 2026-09-01 13:41:32 | `user_data/convergence_logs/BinHV45HO-ladder.log` |
| `BinMfiBTCv5003` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 13:09:38 | `user_data/convergence_logs/BinMfiBTCv5003-ladder.log` |
| `BollingerBounceStrategy` | `spot_long` | 576 candles | 0.0% on `bb_upper` | 2026-09-01 12:16:36 | `user_data/convergence_logs/BollingerBounceStrategy-ladder.log` |
| `BopTrendStrategy` | `spot_long` | 288 candles | 0.0% on `bop_ma` | 2026-09-01 12:17:01 | `user_data/convergence_logs/BopTrendStrategy-ladder.log` |
| `BullishEngulfingStrategy` | `spot_long` | 576 candles | 0.0% on `ema50` | 2026-09-01 12:17:26 | `user_data/convergence_logs/BullishEngulfingStrategy-ladder.log` |
| `BuyOnly` | `spot_long` | 672 candles | 0.0% on `rsi` | 2026-09-01 12:17:52 | `user_data/convergence_logs/BuyOnly-ladder.log` |
| `CMCWinner` | `spot_long` | 672 candles | 0.0% on `mfi` | 2026-09-01 13:42:18 | `user_data/convergence_logs/CMCWinner-ladder.log` |
| `CTIBS` | `spot_long` | 672 candles | 0.0% on `ema_135` | 2026-09-01 12:18:16 | `user_data/convergence_logs/CTIBS-ladder.log` |
| `CciMeanReversionStrategy` | `spot_long` | 576 candles | 0.0% on `cci` | 2026-09-01 12:18:42 | `user_data/convergence_logs/CciMeanReversionStrategy-ladder.log` |
| `ChaikinMoneyFlowStrategy` | `spot_long` | 288 candles | 0.0% on `cmf` | 2026-09-01 12:19:08 | `user_data/convergence_logs/ChaikinMoneyFlowStrategy-ladder.log` |
| `Cluc4werk` | `spot_long` | 1440 candles | 0.0% on `lower` | 2026-09-01 13:43:54 | `user_data/convergence_logs/Cluc4werk-ladder.log` |
| `Cluc5werk` | `spot_long` | 1440 candles | 0.0% on `lower` | 2026-09-01 13:44:44 | `user_data/convergence_logs/Cluc5werk-ladder.log` |
| `ClucFiatROI` | `spot_long` | 288 candles | 0.0% on `ema_fast` | 2026-09-01 13:11:38 | `user_data/convergence_logs/ClucFiatROI-ladder.log` |
| `ClucFiatSlow` | `spot_long` | 288 candles | 0.0% on `ema_fast` | 2026-09-01 13:12:03 | `user_data/convergence_logs/ClucFiatSlow-ladder.log` |
| `ClucHAnix` | `spot_long` | 1440 candles | 0.0% on `lower` | 2026-09-01 13:45:46 | `user_data/convergence_logs/ClucHAnix-ladder.log` |
| `ClucHAnix_hhll` | `spot_long` | 2016 candles | 0.0% on `lower` | 2026-09-01 13:12:56 | `user_data/convergence_logs/ClucHAnix_hhll-ladder.log` |
| `ClucMay72018` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 13:46:34 | `user_data/convergence_logs/ClucMay72018-ladder.log` |
| `CofiBitStrategy` | `spot_long` | 288 candles | 0.0% on `fastd` | 2026-09-01 13:47:22 | `user_data/convergence_logs/CofiBitStrategy-ladder.log` |
| `CombinedBinHAndCluc` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 13:48:09 | `user_data/convergence_logs/CombinedBinHAndCluc-ladder.log` |
| `CombinedBinHAndCluc2021` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 13:48:57 | `user_data/convergence_logs/CombinedBinHAndCluc2021-ladder.log` |
| `CombinedBinHAndCluc2021Bull` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 13:49:45 | `user_data/convergence_logs/CombinedBinHAndCluc2021Bull-ladder.log` |
| `CombinedBinHAndClucV2` | `spot_long` | 576 candles | 0.0% on `ssl_down` | 2026-09-01 13:15:19 | `user_data/convergence_logs/CombinedBinHAndClucV2-ladder.log` |
| `CombinedBinHAndClucV4` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 13:15:44 | `user_data/convergence_logs/CombinedBinHAndClucV4-ladder.log` |
| `CombinedBinHAndClucV5` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 13:16:09 | `user_data/convergence_logs/CombinedBinHAndClucV5-ladder.log` |
| `CombinedBinHAndClucV5Hyperoptable` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 12:21:09 | `user_data/convergence_logs/CombinedBinHAndClucV5Hyperoptable-ladder.log` |
| `CombinedBinHAndClucV8` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 13:16:34 | `user_data/convergence_logs/CombinedBinHAndClucV8-ladder.log` |
| `CombinedBinHAndClucV8Hyper` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 13:16:59 | `user_data/convergence_logs/CombinedBinHAndClucV8Hyper-ladder.log` |
| `CombinedBinHAndClucV8XH` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 13:17:23 | `user_data/convergence_logs/CombinedBinHAndClucV8XH-ladder.log` |
| `CombinedBinHAndClucV8XHO` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:21:34 | `user_data/convergence_logs/CombinedBinHAndClucV8XHO-ladder.log` |
| `Combined_NFIv6_SMA` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 13:17:48 | `user_data/convergence_logs/Combined_NFIv6_SMA-ladder.log` |
| `Combined_NFIv7_SMA` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:00 | `user_data/convergence_logs/Combined_NFIv7_SMA-ladder.log` |
| `Combined_NFIv7_SMA_Rallipanos_20210707` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:25 | `user_data/convergence_logs/Combined_NFIv7_SMA_Rallipanos_20210707-ladder.log` |
| `Combined_NFIv7_SMA_bAdBoY_20211204` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:51 | `user_data/convergence_logs/Combined_NFIv7_SMA_bAdBoY_20211204-ladder.log` |
| `CompositeScoreStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:23:15 | `user_data/convergence_logs/CompositeScoreStrategy-ladder.log` |
| `CoppockCurveStrategy` | `spot_long` | 288 candles | 0.0% on `coppock` | 2026-09-01 12:23:39 | `user_data/convergence_logs/CoppockCurveStrategy-ladder.log` |
| `CrossEMAStrategy` | `spot_long` | 168 candles | 0.0% on `stoch_rsi` | 2026-09-01 13:18:36 | `user_data/convergence_logs/CrossEMAStrategy-ladder.log` |
| `DCBBBounce` | `spot_long` | 576 candles | 0.0% on `bb_upperband` | 2026-09-01 13:19:24 | `user_data/convergence_logs/DCBBBounce-ladder.log` |
| `DemaCrossStrategy` | `spot_long` | 288 candles | 0.0% on `dema20` | 2026-09-01 12:24:04 | `user_data/convergence_logs/DemaCrossStrategy-ladder.log` |
| `Divergences` | `spot_long` | 2160 candles | 0.0% on `mean68close` | 2026-09-01 13:21:26 | `user_data/convergence_logs/Divergences-ladder.log` |
| `DonchianBreakoutStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:24:28 | `user_data/convergence_logs/DonchianBreakoutStrategy-ladder.log` |
| `Dracula` | `spot_long` | 1440 candles | 0.0% on `bb_bbh` | 2026-09-01 13:53:01 | `user_data/convergence_logs/Dracula-ladder.log` |
| `E0V1E` | `spot_long` | 2016 candles | 0.0% on `sma_15` | 2026-09-01 13:22:16 | `user_data/convergence_logs/E0V1E-ladder.log` |
| `E0V1E2` | `spot_long` | 2016 candles | 0.0% on `sma_15` | 2026-09-01 13:22:41 | `user_data/convergence_logs/E0V1E2-ladder.log` |
| `E0V1E_DCA3` | `spot_long` | 2016 candles | 0.0% on `sma_15` | 2026-09-01 12:24:54 | `user_data/convergence_logs/E0V1E_DCA3-ladder.log` |
| `E0V1E_ewo` | `spot_long` | 2016 candles | 0.0% on `sma_15` | 2026-09-01 13:23:07 | `user_data/convergence_logs/E0V1E_ewo-ladder.log` |
| `E0V1E_protections` | `spot_long` | 2016 candles | 0.0% on `sma_15` | 2026-09-01 13:23:31 | `user_data/convergence_logs/E0V1E_protections-ladder.log` |
| `E0V1E_strs` | `spot_long` | 288 candles | 0.0% on `sma_15` | 2026-09-01 13:23:57 | `user_data/convergence_logs/E0V1E_strs-ladder.log` |
| `EMA50` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 13:24:21 | `user_data/convergence_logs/EMA50-ladder.log` |
| `EMABreakout` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 13:24:46 | `user_data/convergence_logs/EMABreakout-ladder.log` |
| `EMASkipPump` | `spot_long` | 288 candles | 0.0% on `ema_21` | 2026-09-01 13:53:49 | `user_data/convergence_logs/EMASkipPump-ladder.log` |
| `ElliotV4` | `spot_long` | 2016 candles | 0.0% on `ma_buy_14` | 2026-09-01 13:25:34 | `user_data/convergence_logs/ElliotV4-ladder.log` |
| `ElliotV531` | `spot_long` | 2016 candles | 0.0% on `ma_sell_17` | 2026-09-01 13:25:59 | `user_data/convergence_logs/ElliotV531-ladder.log` |
| `ElliotV5HO` | `spot_long` | 2016 candles | 0.0% on `ma_buy_11` | 2026-09-01 13:26:23 | `user_data/convergence_logs/ElliotV5HO-ladder.log` |
| `ElliotV5HOMod2` | `spot_long` | 2016 candles | 0.0% on `ma_buy_17` | 2026-09-01 13:26:48 | `user_data/convergence_logs/ElliotV5HOMod2-ladder.log` |
| `ElliotV5HOMod3` | `spot_long` | 2016 candles | 0.0% on `ma_buy_17` | 2026-09-01 13:27:12 | `user_data/convergence_logs/ElliotV5HOMod3-ladder.log` |
| `ElliotV7` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 13:27:41 | `user_data/convergence_logs/ElliotV7-ladder.log` |
| `ElliotV8HO` | `spot_long` | 2016 candles | 0.0% on `ma_sell_24` | 2026-09-01 13:28:05 | `user_data/convergence_logs/ElliotV8HO-ladder.log` |
| `EmaRibbonStrategy` | `spot_long` | 288 candles | 0.0% on `ema8` | 2026-09-01 12:25:20 | `user_data/convergence_logs/EmaRibbonStrategy-ladder.log` |
| `FOttStrategy` | `futures_long_short` | 672 candles | 0.0% on `ott` | 2026-09-01 13:28:30 | `user_data/convergence_logs/FOttStrategy-ladder.log` |
| `FRAYSTRAT` | `spot_long` | 672 candles | 0.0% on `adx` | 2026-09-01 13:28:54 | `user_data/convergence_logs/FRAYSTRAT-ladder.log` |
| `FSampleStrategy` | `futures_long_short` | 336 candles | 0.0% on `adx` | 2026-09-01 13:29:43 | `user_data/convergence_logs/FSampleStrategy-ladder.log` |
| `FisherHull` | `spot_long` | 1440 candles | 0.0% on `cci` | 2026-09-01 13:54:39 | `user_data/convergence_logs/FisherHull-ladder.log` |
| `FisherTransformStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:25:45 | `user_data/convergence_logs/FisherTransformStrategy-ladder.log` |
| `FrayStratBTC` | `spot_long` | 672 candles | 0.0% on `adx` | 2026-09-01 13:55:52 | `user_data/convergence_logs/FrayStratBTC-ladder.log` |
| `FrostAuraM115mStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 13:56:17 | `user_data/convergence_logs/FrostAuraM115mStrategy-ladder.log` |
| `FrostAuraM11hStrategy` | `spot_long` | 168 candles | 0.0% on `rsi` | 2026-09-01 13:56:41 | `user_data/convergence_logs/FrostAuraM11hStrategy-ladder.log` |
| `FrostAuraM21hStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 13:57:05 | `user_data/convergence_logs/FrostAuraM21hStrategy-ladder.log` |
| `FrostAuraM315mStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 13:57:30 | `user_data/convergence_logs/FrostAuraM315mStrategy-ladder.log` |
| `FrostAuraM31hStrategy` | `spot_long` | 168 candles | 0.0% on `rsi` | 2026-09-01 13:57:55 | `user_data/convergence_logs/FrostAuraM31hStrategy-ladder.log` |
| `GKD_C` | `spot_long` | 2160 candles | 0.633% on `baseline` | 2026-09-01 13:58:45 | `user_data/convergence_logs/GKD_C-ladder.log` |
| `GKD_FisherTransform` | `spot_long` | 168 candles | 0.0% on `fisher_smooth_6h` | 2026-09-01 14:00:27 | `user_data/convergence_logs/GKD_FisherTransform-ladder.log` |
| `GKD_FisherTransformMTF` | `spot_long` | 168 candles | 0.0% on `fisher_smooth_4h` | 2026-09-01 14:01:15 | `user_data/convergence_logs/GKD_FisherTransformMTF-ladder.log` |
| `GPTREV` | `spot_long` | 1440 candles | 0.0% on `rsi_15m` | 2026-09-01 14:01:43 | `user_data/convergence_logs/GPTREV-ladder.log` |
| `GoldenCrossStrategy` | `spot_long` | 2016 candles | 0.0% on `ema50` | 2026-09-01 12:26:10 | `user_data/convergence_logs/GoldenCrossStrategy-ladder.log` |
| `Hacklemore2` | `spot_long` | 192 candles | 0.0% on `volume_mean_slow` | 2026-09-01 14:06:05 | `user_data/convergence_logs/Hacklemore2-ladder.log` |
| `Hacklemore3` | `spot_long` | 288 candles | 0.0% on `volume_mean_slow` | 2026-09-01 14:06:53 | `user_data/convergence_logs/Hacklemore3-ladder.log` |
| `Hacklemost` | `spot_long` | 288 candles | 0.0% on `ema_slow` | 2026-09-01 14:07:44 | `user_data/convergence_logs/Hacklemost-ladder.log` |
| `HansenSmaOffsetV1` | `spot_long` | 96 candles | 0.0% on `emac` | 2026-09-01 14:08:31 | `user_data/convergence_logs/HansenSmaOffsetV1-ladder.log` |
| `HeikinAshiStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:26:36 | `user_data/convergence_logs/HeikinAshiStrategy-ladder.log` |
| `HigherHighStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:27:00 | `user_data/convergence_logs/HigherHighStrategy-ladder.log` |
| `INSIDEUP` | `spot_long` | 90 candles | 0.0% on `rsi_14` | 2026-09-01 14:14:51 | `user_data/convergence_logs/INSIDEUP-ladder.log` |
| `Ichess` | `spot_long` | 90 candles | 0.0% on `Ichimoku_Score` | 2026-09-01 14:15:39 | `user_data/convergence_logs/Ichess-ladder.log` |
| `IchimokuSimpleStrategy` | `spot_long` | 288 candles | 0.0% on `senkou_b` | 2026-09-01 12:27:25 | `user_data/convergence_logs/IchimokuSimpleStrategy-ladder.log` |
| `ImpulseV1` | `spot_long` | 288 candles | 0.0% on `200_SMA` | 2026-09-01 12:27:51 | `user_data/convergence_logs/ImpulseV1-ladder.log` |
| `InformativeSample` | `spot_long` | 576 candles | 0.0% on `ema20` | 2026-09-01 14:17:18 | `user_data/convergence_logs/InformativeSample-ladder.log` |
| `Inverse` | `spot_long` | 720 candles | 0.007% on `ema_200_4h` | 2026-09-01 12:28:16 | `user_data/convergence_logs/Inverse-ladder.log` |
| `InverseV2` | `spot_long` | 720 candles | 0.007% on `ema_200_4h` | 2026-09-01 12:28:42 | `user_data/convergence_logs/InverseV2-ladder.log` |
| `KAMACCIRSI_new` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:29:09 | `user_data/convergence_logs/KAMACCIRSI_new-ladder.log` |
| `KeltnerChannelStrategy` | `spot_long` | 288 candles | 0.0% on `ema20` | 2026-09-01 12:29:34 | `user_data/convergence_logs/KeltnerChannelStrategy-ladder.log` |
| `Lateralus` | `spot_long` | 288 candles | 0.0% on `macd_1h` | 2026-09-01 14:18:09 | `user_data/convergence_logs/Lateralus-ladder.log` |
| `LinearRegressionStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:29:59 | `user_data/convergence_logs/LinearRegressionStrategy-ladder.log` |
| `Low_BB` | `spot_long` | 1440 candles | 0.0% on `bb_lowerband` | 2026-09-01 14:19:00 | `user_data/convergence_logs/Low_BB-ladder.log` |
| `LuxOSC` | `spot_long` | 576 candles | 0.0% on `osc` | 2026-09-01 14:19:26 | `user_data/convergence_logs/LuxOSC-ladder.log` |
| `MAC` | `spot_long` | 90 candles | 0.858% on `macdhist` | 2026-09-01 14:19:51 | `user_data/convergence_logs/MAC-ladder.log` |
| `MACDStrategy` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:22:14 | `user_data/convergence_logs/MACDStrategy-ladder.log` |
| `MACDStrategy_crossed` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:23:01 | `user_data/convergence_logs/MACDStrategy_crossed-ladder.log` |
| `MACDZeroCrossStrategy` | `spot_long` | 90 candles | 0.0% on `macd` | 2026-09-01 14:23:48 | `user_data/convergence_logs/MACDZeroCrossStrategy-ladder.log` |
| `MACD_EMA` | `spot_long` | 2016 candles | 0.0% on `macd` | 2026-09-01 14:24:36 | `user_data/convergence_logs/MACD_EMA-ladder.log` |
| `MACD_TRI_EMA` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:25:25 | `user_data/convergence_logs/MACD_TRI_EMA-ladder.log` |
| `MFI` | `spot_long` | 288 candles | 0.0% on `MFI` | 2026-09-01 14:26:13 | `user_data/convergence_logs/MFI-ladder.log` |
| `MacdAdxStrategy` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 12:30:24 | `user_data/convergence_logs/MacdAdxStrategy-ladder.log` |
| `MacdZeroCrossStrategy` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:23:48 | `user_data/convergence_logs/MacdZeroCrossStrategy-ladder.log` |
| `Martin` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 14:26:38 | `user_data/convergence_logs/Martin-ladder.log` |
| `MiniLambo` | `spot_long` | 2880 candles | 0.0% on `ema_14` | 2026-09-01 14:27:06 | `user_data/convergence_logs/MiniLambo-ladder.log` |
| `MomentumScoreStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:31:13 | `user_data/convergence_logs/MomentumScoreStrategy-ladder.log` |
| `Momentumv2` | `spot_long` | 540 candles | 0.0% on `macd` | 2026-09-01 12:31:37 | `user_data/convergence_logs/Momentumv2-ladder.log` |
| `MoneyFlowStrategy` | `spot_long` | 576 candles | 0.0% on `mfi` | 2026-09-01 12:32:02 | `user_data/convergence_logs/MoneyFlowStrategy-ladder.log` |
| `MontrealStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 14:28:21 | `user_data/convergence_logs/MontrealStrategy-ladder.log` |
| `MultiFactorConfluenceStrategy` | `spot_long` | 540 candles | 0.0% on `macd` | 2026-09-01 12:32:26 | `user_data/convergence_logs/MultiFactorConfluenceStrategy-ladder.log` |
| `MultiOffsetLamboV0` | `spot_long` | 2016 candles | 0.0% on `sma_offset_buy` | 2026-09-01 14:28:46 | `user_data/convergence_logs/MultiOffsetLamboV0-ladder.log` |
| `MyStratV1` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 12:32:52 | `user_data/convergence_logs/MyStratV1-ladder.log` |
| `NASOSv5` | `spot_long` | 2016 candles | 0.0% on `ma_sell_16` | 2026-09-01 14:29:12 | `user_data/convergence_logs/NASOSv5-ladder.log` |
| `NEWTEST15m` | `spot_long` | 672 candles | 0.0% on `adx` | 2026-09-01 14:29:37 | `user_data/convergence_logs/NEWTEST15m-ladder.log` |
| `NFI46` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 14:30:04 | `user_data/convergence_logs/NFI46-ladder.log` |
| `NFI46FrogZ` | `spot_long` | 2016 candles | 0.0% on `fastd` | 2026-09-01 14:30:31 | `user_data/convergence_logs/NFI46FrogZ-ladder.log` |
| `NFI46Offset` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 14:30:57 | `user_data/convergence_logs/NFI46Offset-ladder.log` |
| `NFI46OffsetHOA1` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 14:31:24 | `user_data/convergence_logs/NFI46OffsetHOA1-ladder.log` |
| `NFI46Z` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 14:31:53 | `user_data/convergence_logs/NFI46Z-ladder.log` |
| `NFI47V2` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 12:33:20 | `user_data/convergence_logs/NFI47V2-ladder.log` |
| `NFI5MOHO` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 14:32:21 | `user_data/convergence_logs/NFI5MOHO-ladder.log` |
| `NFI5MOHO2` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:33:48 | `user_data/convergence_logs/NFI5MOHO2-ladder.log` |
| `NFI5MOHO_WIP` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 14:32:49 | `user_data/convergence_logs/NFI5MOHO_WIP-ladder.log` |
| `NFI5MOHO_WIP_1` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:34:16 | `user_data/convergence_logs/NFI5MOHO_WIP_1-ladder.log` |
| `NFI5MOHO_WIP_2` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:34:44 | `user_data/convergence_logs/NFI5MOHO_WIP_2-ladder.log` |
| `NFI7MOHO` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 12:35:13 | `user_data/convergence_logs/NFI7MOHO-ladder.log` |
| `NFINextMOHO` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_5m` | 2026-09-01 12:35:41 | `user_data/convergence_logs/NFINextMOHO-ladder.log` |
| `NFINextMOHO2` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_5m` | 2026-09-01 12:36:07 | `user_data/convergence_logs/NFINextMOHO2-ladder.log` |
| `NFINextMultiOffsetAndHO` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_1h` | 2026-09-01 12:36:33 | `user_data/convergence_logs/NFINextMultiOffsetAndHO-ladder.log` |
| `NFINextMultiOffsetAndHO2` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_1h` | 2026-09-01 12:37:00 | `user_data/convergence_logs/NFINextMultiOffsetAndHO2-ladder.log` |
| `NormalizerStrategy` | `spot_long` | 610 candles | 0.0% on `norm_34` | 2026-09-01 12:37:23 | `user_data/convergence_logs/NormalizerStrategy-ladder.log` |
| `NormalizerStrategyHO2` | `spot_long` | 610 candles | 0.0% on `norm_34` | 2026-09-01 14:34:54 | `user_data/convergence_logs/NormalizerStrategyHO2-ladder.log` |
| `Nostalgia` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_1h` | 2026-09-01 12:37:49 | `user_data/convergence_logs/Nostalgia-ladder.log` |
| `NostalgiaForInfinityNextGen` | `spot_long` | 2880 candles | 0.0% on `btc_rsi_14_1h` | 2026-09-01 14:35:20 | `user_data/convergence_logs/NostalgiaForInfinityNextGen-ladder.log` |
| `NostalgiaForInfinityNextGen_TSL` | `spot_long` | 2880 candles | 0.0% on `btc_rsi_14_1h` | 2026-09-01 14:35:46 | `user_data/convergence_logs/NostalgiaForInfinityNextGen_TSL-ladder.log` |
| `NostalgiaForInfinityV3` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 14:36:11 | `user_data/convergence_logs/NostalgiaForInfinityV3-ladder.log` |
| `NostalgiaForInfinityV4` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 14:36:37 | `user_data/convergence_logs/NostalgiaForInfinityV4-ladder.log` |
| `NostalgiaForInfinityV4HO` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 14:37:03 | `user_data/convergence_logs/NostalgiaForInfinityV4HO-ladder.log` |
| `NostalgiaForInfinityV5` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 14:37:31 | `user_data/convergence_logs/NostalgiaForInfinityV5-ladder.log` |
| `NostalgiaForInfinityV5MultiOffsetAndHO` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:38:14 | `user_data/convergence_logs/NostalgiaForInfinityV5MultiOffsetAndHO-ladder.log` |
| `NostalgiaForInfinityV5MultiOffsetAndHO2` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 14:37:59 | `user_data/convergence_logs/NostalgiaForInfinityV5MultiOffsetAndHO2-ladder.log` |
| `NostalgiaForInfinityV6` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 14:38:27 | `user_data/convergence_logs/NostalgiaForInfinityV6-ladder.log` |
| `NostalgiaForInfinityV6HO` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 12:38:41 | `user_data/convergence_logs/NostalgiaForInfinityV6HO-ladder.log` |
| `NostalgiaForInfinityV7` | `spot_long` | 2016 candles | 0.0% on `ema_20_1h` | 2026-09-01 14:38:55 | `user_data/convergence_logs/NostalgiaForInfinityV7-ladder.log` |
| `NostalgiaForInfinityV7_SMA` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 14:39:23 | `user_data/convergence_logs/NostalgiaForInfinityV7_SMA-ladder.log` |
| `NostalgiaForInfinityV7_SMAv2` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 14:39:50 | `user_data/convergence_logs/NostalgiaForInfinityV7_SMAv2-ladder.log` |
| `NostalgiaForInfinityV7_SMAv2_1` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 14:40:17 | `user_data/convergence_logs/NostalgiaForInfinityV7_SMAv2_1-ladder.log` |
| `NotAnotherSMAOffsetStrategy` | `spot_long` | 2016 candles | 0.0% on `ma_buy_14` | 2026-09-01 14:44:33 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategy-ladder.log` |
| `NotAnotherSMAOffsetStrategyHO` | `spot_long` | 2016 candles | 0.0% on `ma_buy_16` | 2026-09-01 14:44:59 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategyHO-ladder.log` |
| `NotAnotherSMAOffsetStrategyHOv3` | `spot_long` | 2016 candles | 0.0% on `ma_sell_16` | 2026-09-01 14:45:25 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategyHOv3-ladder.log` |
| `NotAnotherSMAOffsetStrategyLite` | `spot_long` | 2016 candles | 0.0% on `ema_24` | 2026-09-01 12:39:05 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategyLite-ladder.log` |
| `NotAnotherSMAOffsetStrategyModHO` | `spot_long` | 2016 candles | 0.0% on `hma_50` | 2026-09-01 14:45:51 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategyModHO-ladder.log` |
| `NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901` | `spot_long` | 2016 candles | 0.0% on `hma_50` | 2026-09-01 14:46:17 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901-ladder.log` |
| `NotAnotherSMAOffsetStrategyX1` | `spot_long` | 2016 candles | 0.0% on `ma_sell_24` | 2026-09-01 14:46:44 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategyX1-ladder.log` |
| `NotAnotherSMAOffsetStrategy_uzi` | `spot_long` | 2016 candles | 0.0% on `ma_buy_14` | 2026-09-01 14:47:10 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategy_uzi-ladder.log` |
| `NotAnotherSMAOffsetStrategy_uzi3` | `spot_long` | 2016 candles | 0.0% on `hma_50` | 2026-09-01 14:47:36 | `user_data/convergence_logs/NotAnotherSMAOffsetStrategy_uzi3-ladder.log` |
| `NowoIchimoku1hV2` | `spot_long` | 168 candles | 0.0% on `upper` | 2026-09-01 14:48:01 | `user_data/convergence_logs/NowoIchimoku1hV2-ladder.log` |
| `PRICEFOLLOWING` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 14:48:31 | `user_data/convergence_logs/PRICEFOLLOWING-ladder.log` |
| `PRICEFOLLOWING2` | `spot_long` | 672 candles | 0.0% on `adx` | 2026-09-01 14:48:59 | `user_data/convergence_logs/PRICEFOLLOWING2-ladder.log` |
| `PRICEFOLLOWINGX` | `spot_long` | 672 candles | 0.0% on `adx` | 2026-09-01 14:49:28 | `user_data/convergence_logs/PRICEFOLLOWINGX-ladder.log` |
| `ParabolicSarStrategy` | `spot_long` | 288 candles | 0.0% on `ema50` | 2026-09-01 12:39:54 | `user_data/convergence_logs/ParabolicSarStrategy-ladder.log` |
| `PolymarketPortfolio` | `spot_long` | 180 candles | 0.0% on `prob_ema_fast` | 2026-09-01 14:51:07 | `user_data/convergence_logs/PolymarketPortfolio-ladder.log` |
| `PpoMomentumStrategy` | `spot_long` | 288 candles | 0.0% on `ppo` | 2026-09-01 12:40:19 | `user_data/convergence_logs/PpoMomentumStrategy-ladder.log` |
| `PriceActionCandleStrategy` | `spot_long` | 288 candles | 0.0% on `ema50` | 2026-09-01 12:40:43 | `user_data/convergence_logs/PriceActionCandleStrategy-ladder.log` |
| `PriceChannelStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:41:07 | `user_data/convergence_logs/PriceChannelStrategy-ladder.log` |
| `PumpDetector` | `spot_long` | 2016 candles | 0.0% on `var2_test` | 2026-09-01 12:41:32 | `user_data/convergence_logs/PumpDetector-ladder.log` |
| `Quickie` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:51:56 | `user_data/convergence_logs/Quickie-ladder.log` |
| `RSIv2` | `spot_long` | 192 candles | 0.0% on `rsi_30m` | 2026-09-01 12:41:55 | `user_data/convergence_logs/RSIv2-ladder.log` |
| `RalliV1` | `spot_long` | 2016 candles | 0.0% on `ma_buy_14` | 2026-09-01 14:52:21 | `user_data/convergence_logs/RalliV1-ladder.log` |
| `RalliV1_disable56` | `spot_long` | 2016 candles | 0.0% on `ma_buy_14` | 2026-09-01 14:52:46 | `user_data/convergence_logs/RalliV1_disable56-ladder.log` |
| `ReinforcedAverageStrategy` | `spot_long` | 84 candles | 0.0% on `maShort` | 2026-09-01 14:53:35 | `user_data/convergence_logs/ReinforcedAverageStrategy-ladder.log` |
| `RocMomentumStrategy` | `spot_long` | 576 candles | 0.0% on `rsi` | 2026-09-01 12:42:20 | `user_data/convergence_logs/RocMomentumStrategy-ladder.log` |
| `RsiBollingerStrategy` | `spot_long` | 168 candles | 0.0% on `rsi` | 2026-09-01 12:42:44 | `user_data/convergence_logs/RsiBollingerStrategy-ladder.log` |
| `RsiDivergenceStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 14:54:00 | `user_data/convergence_logs/RsiDivergenceStrategy-ladder.log` |
| `SAR` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 15:00:35 | `user_data/convergence_logs/SAR-ladder.log` |
| `SMAOffset` | `spot_long` | 288 candles | 0.0% on `ma_offset_buy` | 2026-09-01 14:54:50 | `user_data/convergence_logs/SMAOffset-ladder.log` |
| `SMAOffsetProtectOpt` | `spot_long` | 2016 candles | 0.0% on `ma_buy_20` | 2026-09-01 14:55:15 | `user_data/convergence_logs/SMAOffsetProtectOpt-ladder.log` |
| `SMAOffsetProtectOptV0` | `spot_long` | 2016 candles | 0.0% on `ma_buy_20` | 2026-09-01 14:55:41 | `user_data/convergence_logs/SMAOffsetProtectOptV0-ladder.log` |
| `SMAOffsetProtectOptV1` | `spot_long` | 2016 candles | 0.0% on `ma_13` | 2026-09-01 14:56:06 | `user_data/convergence_logs/SMAOffsetProtectOptV1-ladder.log` |
| `SMAOffsetProtectOptV1HO1` | `spot_long` | 2016 candles | 0.0% on `ma_buy_17` | 2026-09-01 14:56:32 | `user_data/convergence_logs/SMAOffsetProtectOptV1HO1-ladder.log` |
| `SMAOffsetProtectOptV1Mod` | `spot_long` | 2016 candles | 0.0% on `ma_buy_16` | 2026-09-01 14:56:58 | `user_data/convergence_logs/SMAOffsetProtectOptV1Mod-ladder.log` |
| `SMAOffsetProtectOptV1Mod2` | `spot_long` | 2016 candles | 0.0% on `ma_buy_16` | 2026-09-01 14:57:24 | `user_data/convergence_logs/SMAOffsetProtectOptV1Mod2-ladder.log` |
| `SMAOffsetProtectOptV1_kkeue_20210619` | `spot_long` | 2016 candles | 0.0% on `ma_buy_16` | 2026-09-01 14:57:51 | `user_data/convergence_logs/SMAOffsetProtectOptV1_kkeue_20210619-ladder.log` |
| `SMAOffset_Hippocritical_dca` | `spot_long` | 2016 candles | 0.0% on `EWO` | 2026-09-01 14:58:16 | `user_data/convergence_logs/SMAOffset_Hippocritical_dca-ladder.log` |
| `SMAOffset_Hippocritical_dca_old` | `spot_long` | 2016 candles | 0.0% on `EWO` | 2026-09-01 14:59:11 | `user_data/convergence_logs/SMAOffset_Hippocritical_dca_old-ladder.log` |
| `SMAOffset_Hippocritical_dca_protections` | `spot_long` | 2016 candles | 0.0% on `EWO` | 2026-09-01 14:59:41 | `user_data/convergence_logs/SMAOffset_Hippocritical_dca_protections-ladder.log` |
| `SMA_BBRSI` | `spot_long` | 2016 candles | 0.0% on `rsi` | 2026-09-01 15:00:08 | `user_data/convergence_logs/SMA_BBRSI-ladder.log` |
| `SRsi` | `spot_long` | 1440 candles | 0.0% on `rsi` | 2026-09-01 12:43:10 | `user_data/convergence_logs/SRsi-ladder.log` |
| `STRATEGY_RSI_BB_BOUNDS_CROSS` | `spot_long` | 288 candles | 0.0% on `bb_lb` | 2026-09-01 12:43:35 | `user_data/convergence_logs/STRATEGY_RSI_BB_BOUNDS_CROSS-ladder.log` |
| `STRATEGY_RSI_BB_CROSS` | `spot_long` | 288 candles | 0.0% on `bb_lowerband` | 2026-09-01 12:44:00 | `user_data/convergence_logs/STRATEGY_RSI_BB_CROSS-ladder.log` |
| `SampleStrategy` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 12:44:24 | `user_data/convergence_logs/SampleStrategy-ladder.log` |
| `Sar` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 15:00:35 | `user_data/convergence_logs/Sar-ladder.log` |
| `SmaRsiStrategy` | `spot_long` | 90 candles | 0.041% on `rsi` | 2026-09-01 12:44:48 | `user_data/convergence_logs/SmaRsiStrategy-ladder.log` |
| `SqueezeMomentumStrategy` | `spot_long` | 288 candles | 0.0% on `bb_upper` | 2026-09-01 12:45:12 | `user_data/convergence_logs/SqueezeMomentumStrategy-ladder.log` |
| `StochasticOversoldStrategy` | `spot_long` | 288 candles | 0.0% on `stoch_k` | 2026-09-01 12:45:36 | `user_data/convergence_logs/StochasticOversoldStrategy-ladder.log` |
| `StochasticRsiStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:46:00 | `user_data/convergence_logs/StochasticRsiStrategy-ladder.log` |
| `StrategyScalpingFast` | `spot_long` | 1440 candles | 0.0% on `ema_high` | 2026-09-01 12:46:27 | `user_data/convergence_logs/StrategyScalpingFast-ladder.log` |
| `TRIWAVE` | `spot_long` | 672 candles | 0.0% on `rsi_med_2h` | 2026-09-01 12:46:51 | `user_data/convergence_logs/TRIWAVE-ladder.log` |
| `TemaStrategy` | `spot_long` | 288 candles | 0.0% on `tema20` | 2026-09-01 12:47:16 | `user_data/convergence_logs/TemaStrategy-ladder.log` |
| `TrendAtrStrategy` | `spot_long` | 540 candles | 0.0% on `ema_fast` | 2026-09-01 12:47:40 | `user_data/convergence_logs/TrendAtrStrategy-ladder.log` |
| `TripleEmaStrategy` | `spot_long` | 288 candles | 0.0% on `ema8` | 2026-09-01 12:48:03 | `user_data/convergence_logs/TripleEmaStrategy-ladder.log` |
| `TrixSignalStrategy` | `spot_long` | 288 candles | 0.0% on `trix` | 2026-09-01 12:48:28 | `user_data/convergence_logs/TrixSignalStrategy-ladder.log` |
| `UniversalMACD` | `spot_long` | 288 candles | 0.0% on `ma12` | 2026-09-01 12:48:53 | `user_data/convergence_logs/UniversalMACD-ladder.log` |
| `VolumeBreakoutStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:49:17 | `user_data/convergence_logs/VolumeBreakoutStrategy-ladder.log` |
| `VortexStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:49:42 | `user_data/convergence_logs/VortexStrategy-ladder.log` |
| `VwapReversionStrategy` | `spot_long` | 576 candles | 0.0% on `vwap` | 2026-09-01 12:50:07 | `user_data/convergence_logs/VwapReversionStrategy-ladder.log` |
| `WilliamsRStrategy` | `spot_long` | 2016 candles | 0.0% on `ema50` | 2026-09-01 12:50:33 | `user_data/convergence_logs/WilliamsRStrategy-ladder.log` |
| `adxbbrsi2` | `spot_long` | 336 candles | 0.0% on `adx` | 2026-09-01 12:50:58 | `user_data/convergence_logs/adxbbrsi2-ladder.log` |
| `bbrsi` | `spot_long` | 180 candles | 0.0% on `rsi` | 2026-09-01 12:51:22 | `user_data/convergence_logs/bbrsi-ladder.log` |
| `bbrsi4Freq` | `spot_long` | 168 candles | 0.0% on `rsi` | 2026-09-01 12:51:45 | `user_data/convergence_logs/bbrsi4Freq-ladder.log` |
| `conny` | `spot_long` | 96 candles | 0.0% on `consensus_sell` | 2026-09-01 12:52:10 | `user_data/convergence_logs/conny-ladder.log` |
| `cryptotankV2` | `spot_long` | 576 candles | 0.0% on `pivot` | 2026-09-01 12:52:35 | `user_data/convergence_logs/cryptotankV2-ladder.log` |
| `eltoro` | `spot_long` | 1344 candles | 0.0% on `BTC_EWO_Fast_1h` | 2026-09-01 12:53:00 | `user_data/convergence_logs/eltoro-ladder.log` |
| `eltoro1_4` | `spot_long` | 2160 candles | 0.0% on `INFEWO_4h` | 2026-09-01 12:53:24 | `user_data/convergence_logs/eltoro1_4-ladder.log` |
| `eltoro1_4_simple` | `spot_long` | 672 candles | 0.0% on `INFEWO_4h` | 2026-09-01 12:53:49 | `user_data/convergence_logs/eltoro1_4_simple-ladder.log` |
| `gettinMoist` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 12:54:38 | `user_data/convergence_logs/gettinMoist-ladder.log` |
| `hlhb` | `spot_long` | 540 candles | 0.0% on `rsi` | 2026-09-01 12:55:01 | `user_data/convergence_logs/hlhb-ladder.log` |
| `slope_is_dopeCT` | `spot_long` | 672 candles | 0.0% on `rsi` | 2026-09-01 12:55:49 | `user_data/convergence_logs/slope_is_dopeCT-ladder.log` |
| `stoploss` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 12:56:13 | `user_data/convergence_logs/stoploss-ladder.log` |
| `strato` | `spot_long` | 1440 candles | 0.0% on `rsi` | 2026-09-01 12:56:41 | `user_data/convergence_logs/strato-ladder.log` |
| `thetank3` | `spot_long` | 672 candles | 0.0% on `ema_125` | 2026-09-01 12:57:28 | `user_data/convergence_logs/thetank3-ladder.log` |
| `thetank4TV` | `spot_long` | 672 candles | 0.0% on `ema_125` | 2026-09-01 12:57:53 | `user_data/convergence_logs/thetank4TV-ladder.log` |
| `ultratank` | `spot_long` | 336 candles | 0.0% on `pivot` | 2026-09-01 12:58:17 | `user_data/convergence_logs/ultratank-ladder.log` |
| `wavetrend` | `spot_long` | 336 candles | 0.0% on `rsi` | 2026-09-01 12:58:45 | `user_data/convergence_logs/wavetrend-ladder.log` |
| `wavetrend_rsi` | `spot_long` | 336 candles | 0.0% on `rsi` | 2026-09-01 12:59:09 | `user_data/convergence_logs/wavetrend_rsi-ladder.log` |

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

## Not passing - 498 strategies, by decisive reason

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

| Reason | Meaning | Strategies |
|---|---|---:|
| `lookahead_found` | reads data it could not have had at the time | 69 |
| `technical_trap_found` | carries a published backtesting trap | 40 |
| `recursive_bias_found` | indicator value still drifts at every warm-up the ladder can reach | 23 |
| `recursive_bias_unverified` | recorded under a parser defect and not re-measured; not a finding | 189 |
| `no_trades_in_full_measurement` | never trades over the full window | 16 |
| `canonical_implementation_not_measured` | never ran | 152 |
| `no_verdict_on_lookahead_and_recursive` | measured; neither gate returned a verdict | 5 |
| `no_verdict_on_lookahead` | measured and recursion clean; look-ahead has no verdict | 4 |


### Reason by wave

| Reason | `B_warmup_refusal` | `C_measurement_recovery` | `D_recursive_drift` | `not_scheduled` |
|---|---|---|---|---|
| `lookahead_found` | 0 | 15 | 0 | 54 |
| `technical_trap_found` | 0 | 0 | 0 | 40 |
| `recursive_bias_found` | 0 | 0 | 14 | 9 |
| `recursive_bias_unverified` | 74 | 29 | 0 | 86 |
| `no_trades_in_full_measurement` | 0 | 10 | 0 | 6 |
| `canonical_implementation_not_measured` | 0 | 152 | 0 | 0 |
| `no_verdict_on_lookahead_and_recursive` | 0 | 5 | 0 | 0 |
| `no_verdict_on_lookahead` | 0 | 4 | 0 | 0 |

### `lookahead_found` - 69

Reads data it could not have had at the time.

Wave `C_measurement_recovery` - 15:

`ARIMA_15`, `NfiNextModded`, `NostalgiaForInfinityNext`, `NostalgiaForInfinityNext772`
`NostalgiaForInfinityNextV7155`, `NostalgiaForInfinityNext_ChangeToTower_V5_2`, `NostalgiaForInfinityNext_ChangeToTower_V5_3`, `NostalgiaForInfinityNext_ChangeToTower_V6`
`NostalgiaForInfinityNext_maximizer`, `NostalgiaForInfinityV7_7_2`, `NostalgiaForInfinityXw`, `Obelisk_Ichimoku_Slow_v1_3`
`Obelisk_Ichimoku_ZEMA_v1`, `Stinkfist`, `ichiV1_Marius`

Wave `not_scheduled` - 54:

`AlexBTK_CT`, `AlexBattleTankKiller`, `AlexBattleTankKillerV3`, `AlexBattleTankKillerV40H`
`Auto_EI_t4c0s`, `BBBreakoutStrategy`, `BB_RPB_TSL_c7c477d_20211030`, `BreakoutStrategy`
`BuyAllSellAllStrategy`, `CCIStrategy`, `Cci`, `EI1_t4c0s_V4`
`EI4_t4c0s_V2`, `EI4_t4c0s_V2_2`, `ElliotWave`, `FVGAdvancedStrategy_V2`
`FakeoutStrategy`, `FrayLIVEBTC15m`, `FrostAuraRandomStrategy`, `Heracles`
`HyperStra_SMAOnly`, `Ichi`, `IchiVwapAdx`, `IchimokuCloudStrategy`
`Leveraged`, `LookaheadStrategy`, `LorentzianClassification`, `MSO`
`MaxSharpePortfolio`, `MinimumVariancePortfolio`, `MomentumRegimeBasket`, `NOTankAi_17`
`NOTankAi_19`, `NWEv6`, `NeuroV1`, `Obelisk_TradePro_Ichi_v1_1`
`Obelisk_TradePro_Ichi_v2_1`, `Precognition`, `ReinforcedQuickie`, `Renko`
`Rsiqui`, `RsiquiV2`, `RsiquiV5`, `RsiquiV5_long_only`
`StarRise_strat3`, `TSPredict`, `Tank1Modulus`, `UziChan`
`UziChan2`, `Zeus`, `grad`, `ichiV1`
`tsp0chicken`, `wtc`

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

### `recursive_bias_found` - 23

Indicator value still drifts at every warm-up the ladder can reach.

Wave `D_recursive_drift` - 14:

`BigZ0307HO`, `BigZ0407`, `BigZ0407HO`, `BigZ04HO`
`BigZ04HO2`, `BigZ06`, `BigZ07`, `ClucHAnix_BB_RPB_MOD2_ROI`
`ClucHAnix_BB_RPB_MOD_CTT`, `ClucHAnix_BB_RPB_MOD_E0V1E_ROI`, `ObvTrendStrategy`, `flawless_lambo`
`lambotest`, `tacos`

Wave `not_scheduled` - 9:

`BcmbigzV1`, `BeastBotXBLR6`, `BeastBotXBLR7`, `BigZ04`
`GoldHedgeZeroMACD`, `NOTankAi_15`, `NOTankAi_15_Cleaned`, `NOTankAi_15_Cleaned_v2`
`NotAnotherSMAOffSetStrategy_V2`

### `recursive_bias_unverified` - 189

Recorded under a parser defect and not re-measured; not a finding.

Wave `B_warmup_refusal` - 74:

`ASDTSRockwellTrading`, `AwesomeMacd`, `BBRSI2`, `BBRSI21`
`BBRSI3366`, `BB_RPB_TSL_RNG_2`, `BBlower`, `Bandtastic`
`BuyOrDie`, `Candle2`, `Chandem`, `Chandemtwo`
`Cluc4`, `CombinedBinHAndClucHyperV0`, `CombinedBinHAndClucHyperV3`, `Combined_Indicators`
`DD`, `Diamond`, `EMA520015_V17`, `EasyInEasyOut`
`FVGChannel`, `ForexRobootSuperScalper`, `Freqtrade_backtest_validation_freqtrade1`, `GKD_Baseline`
`GKD_BaselineAllMAs`, `GKD_HurstExponent`, `GKD_PFE`, `GodCard`
`HSI`, `HilbertSineWave`, `JuicyTrend`, `KC_BB`
`MACDStrategyADA`, `MACDStrategyAVAX`, `MACDStrategyBTC`, `MACDStrategyENJ`
`MACDStrategyETC`, `MACDStrategySOL`, `MACDStrategyXRP`, `MabStra`
`Macd`, `Maro4hMacdSd`, `MomStrategy`, `ONUR`
`OmaGann`, `RSI`, `RSI_BB`, `RSI_EMA_strategy`
`ReinforcedSmoothScalp`, `Roth01`, `Roth03`, `SimpleHopt`
`SlowPotato`, `SmartMoneyStrategy`, `Strategy001`, `Strategy001_custom_exit`
`Strategy001_custom_sell`, `Strategy002`, `Strategy003`, `Strategy004`
`Strategy005`, `StrategyScalpingFast2`, `TemaMaster`, `TemaMaster3`
`TemaPure`, `TemaPureNeat`, `TemaPureTwo`, `TouchEmaDelayStrategy`
`TouchEmaStrategy`, `Trend_Strength_Directional`, `TwoCandle`, `bbandrsi`
`e6v34`, `ema`

Wave `C_measurement_recovery` - 29:

`BBMod1`, `BB_RPB_TSL`, `BB_RPB_TSL_2`, `BB_RPB_TSL_BI`
`BB_RPB_TSL_BIV1`, `BB_RPB_TSL_SMA_Tranz`, `BB_RPB_TSL_SMA_Tranz_TB_1_1_1`, `BB_RPB_TSL_SMA_Tranz_TB_MOD`
`GeneStrategy`, `GeneStrategy_v2`, `GeneTrader_gen10_1734895087_6007`, `GeneTrader_gen5_1735014093_4541`
`KitchenSink`, `MultiMA_TSL3`, `MultiMA_TSL3_Mod`, `MultiRSI`
`NASOSRv6_private_Reinuvader_20211121`, `NFI731_BUSD`, `NFIX_BB_RPB`, `NFIX_BB_RPB_c7c477d_20211030`
`NostalgiaForInfinity772martinsk3`, `NostalgiaForInfinityX`, `ObeliskRSI_v6_1`, `epretrace`
`falconTrader`, `newstrategy53`, `newstrategy53_22`, `pmaxTest`
`slownsteady`

Wave `not_scheduled` - 86:

`BinHV27F`, `BinHV27_short`, `COPY_HL`, `ConsensusShort`
`CustomStoplossWithPSAR`, `DWT_LongShort`, `DWT_short`, `DevilStra`
`Dimond`, `FReinforcedStrategy`, `FTT_DWT_FBB_FUTURES`, `FiveMinCrossAbove`
`GKD_CT`, `GodStraNew`, `GodStraNew40`, `GodStraNew_SMAonly`
`HEW`, `HourBasedStrategy`, `HurstCycle3`, `HurstCycle7`
`HurstCycleV4`, `HurstCycleV5`, `HurstCycleV5RSI`, `HurstCycleV6`
`Ichimoku`, `MACDRL`, `MACDRS`, `Minmax`
`NostalgiaForInfinityX2`, `NostalgiaForInfinityX3`, `NostalgiaForInfinityX4`, `NostalgiaForInfinityX5`
`NostalgiaForInfinityX6`, `NostalgiaForInfinityX7`, `PatternRecognition`, `SMAOffset_Hippocritical_dca_leverage`
`Saturn5`, `Scalp`, `Schism2MM`, `Schism3`
`Schism4`, `Seb`, `Simple`, `SmoothOperator`
`SmoothScalp`, `StarRise`, `StarRise_strat`, `StrategyTestV2`
`StrategyTestV3`, `SuperTrend`, `SupertrendStrategy`, `SwingHighToSky`
`TD`, `TEMA`, `TWAPStrategy`, `TechnicalExampleStrategy`
`TheForce`, `ToTheMoon`, `TrendFollowingStrategy`, `TrendRiderStrategy`
`TrixV21Strategy`, `TrixV23Strategy`, `Uptrend`, `VWAP`
`VolatilitySystem`, `VolatilitySystemV2`, `WaveTrendStra`, `YOLO`
`ZScoreMeanReversionStrategy`, `ZaratustraDCA2_06`, `ZaratustraDCA2_07`, `ZaratustraDCA5`
`adaptive`, `custom`, `dualwave`, `hansencandlepatternV1`
`heikin`, `keltnerchannel`, `mabStra`, `moonhouse`
`pcb20`, `stratfib`, `tbtest`, `true_lambo`
`twinturboV8`, `twinturboV8_2`

### `no_trades_in_full_measurement` - 16

Never trades over the full window.

Wave `C_measurement_recovery` - 10:

`BasketStrategy`, `BreakEven`, `DoesNothingStrategy`, `FundingCarry`
`Miku_PP_v3`, `MostOfAll`, `MyStrategyTemplate`, `Obelisk_3EMA_StochRSI_ATR`
`ViN`, `ep3mas2`

Wave `not_scheduled` - 6:

`DoubleEMACrossoverWithTrend`, `EMAPriceCrossoverWithThreshold`, `Insomnia_short`, `MACDCrossoverWithTrend`
`RSIDirectionalWithTrend`, `RSIDirectionalWithTrendSlow`

### `canonical_implementation_not_measured` - 152

Never ran.

Wave `C_measurement_recovery` - 152:

`ADX_15M_USDT`, `ADX_15M_USDT2`, `AdaptiveRenkoStrategy`, `AdvancedRiskFilterStrategy`
`AlligatorStrat`, `Astro`, `AutoArimaTripleV1`, `BBRSI`
`BBRSIS`, `BBRSIoriginal`, `BB_RPB_3c`, `BB_RSI`
`BB_Strategy04`, `BaseStrategy`, `BbRoi`, `BestSingleAssetPortfolio`
`BinanceStream`, `BlueEyes_MPP_v1`, `Cenderawasih_30m`, `Cenderawasih_3_kucoin`
`Chained`, `Chispei`, `ClucCrypROI`, `ClucCrypSlow`
`ClucHAnix_BB_RPB_MOD_trailing_buy`, `ClucHAnix_BB_RPB_TraNz`, `CombinedBinHAndClucV6H`, `CopyLitmusMinMaxBroadClassificationStrategy`
`CryptoFrog`, `CryptoFrogHO`, `CryptoFrogHO2`, `CryptoFrogHO2A`
`CryptoFrogHO3A1`, `CryptoFrogHO3A2`, `CryptoFrogHO3A3`, `CryptoFrogHO3A4`
`CryptoFrogNFI2`, `CryptoFrog_nateema`, `CryptoPredictionTraining`, `DWT`
`DWT_Leveraged`, `Danke`, `DualModelPolymarketPortfolio`, `Dyna_opti`
`EMABBRSI`, `EMAVolume`, `EXPERIMENTAL_STRATEGY`, `EmaCrossStrategy`
`Enchilada`, `EnsembleStrategy`, `EnsembleStrategyV1`, `EnsembleStrategyV2`
`FSupertrendStrategyBTC`, `FSupertrendStrategyETH`, `FastSupertrend`, `FastSupertrendOpt`
`FileLoadingStrategy`, `FixedRiskRewardLoss`, `FreqaiExampleHybridStrategy`, `FreqaiExampleStrategy`
`GPR`, `GodStra`, `GymStrategy`, `HLHB`
`IchimokuStrategy`, `Ichimoku_SenkouSpanCross`, `Ichimoku_v12`, `Ichimoku_v30`
`Ichimoku_v32`, `Ichimoku_v33`, `Ichimoku_v35`, `JustROCR`
`JustROCR2`, `JustROCR3`, `JustROCR4`, `JustROCR5`
`JustROCR6`, `KMM`, `LitmusEntryRollClassificationStrategy`, `LitmusGoodMinMaxClassificationStrategy`
`LitmusMLDPStrategy`, `LitmusMetaStrategy`, `LitmusMinMaxBroadClassificationStrategy`, `LitmusMinMaxClassificationStrategy`
`LitmusMinMaxRegretClassificationStrategy`, `LitmusMinMaxSegmentClassificationStrategy`, `LitmusMinMaxStrategy`, `LitmusMinMaxTrendStrategy`
`LitmusSimpleStrategy`, `LongShortRangeTradingMachetesV1`, `MACDCCI`, `MACDRSI200`
`MKR`, `MasterMoniGoManiHyperStrategy`, `MlpSpeculativeStrategy`, `MomentumRegimeBasket15m`
`MultiMA_TSL5`, `MultiMa`, `MultiTargetClassifierTestStrategy`, `MultiTargetRegressorTestStrategy`
`NoLost`, `Persia`, `Pmax`, `PnF`
`PolymarketLogicalArbStrategy`, `PolymarketMeanReversionStrategy`, `PolymarketMomentumStrategy`, `Prediction_Strategy`
`Proton`, `QuickAdapterV3`, `QuickBuyStrategy`, `RLAgentStrategy`
`RLStrategy`, `RSIBB02`, `RenkoYolo`, `SMAOPv1_TTF`
`ScalpingCCI`, `SimpleRiskFilterStrategy`, `Solipsis`, `Solipsis4`
`Solipsis6`, `SolipsisMM`, `Stavix2`, `SuperHV27`
`SuperTrendPure`, `Supertrend`, `SwingHigh`, `TankAi`
`TankAiRevival`, `Test_MAMA4`, `TrainCatBoostStrategy`, `TuplaBollinger`
`TwoCandleTheory`, `UpSliceStrategy`, `WTAI`, `WTHO`
`WTRSIAI`, `adx_opt_strat`, `bb_rsi_opt_new`, `bbema`
`bbrsi1_strategy`, `chispei`, `cryptohassle`, `macd_recovery`
`mark_strat`, `mark_strat_opt`, `multi_tf`, `new_turtle`
`new_turtle_roi`, `quantumfirst`, `redditMA`, `thetank2`

### `no_verdict_on_lookahead_and_recursive` - 5

Measured; neither gate returned a verdict.

Wave `C_measurement_recovery` - 5:

`ARIMASTR`, `HarmonicDivergence`, `HarmonicDivergence_fix`, `beta_factors_model`
`zorkv7_0_0`

### `no_verdict_on_lookahead` - 4

Measured and recursion clean; look-ahead has no verdict.

Wave `C_measurement_recovery` - 4:

`ExponentialGradientPortfolio`, `Hacklemore`, `Matrix`, `custom_sell`

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
| `paired_full_window_equivalence` | 257 |
| `lookahead_verdict` | 113 |
| `first_measurement_in_current_runtime` | 60 |
| `convergence_inconclusive` | 36 |
| `re-measure_gates_in_current_runtime` | 30 |
| `convergence_not_converged_within_ladder` | 23 |

Per-row detail, including every evidence path, is in
`STRATEGY_STATUS.csv`.
