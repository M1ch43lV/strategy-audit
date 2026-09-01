# Strategy status - current evidence for all 900 rows

**Generated 2026-09-01 12:28:47 by `strategy_status.py`.** Regenerate it rather than editing it.

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
file's time and is labelled `log_mtime` for that reason. 557 of 900 rows
have neither and are left empty rather than given an invented time.

## Measurement

| | Strategies |
|---|---:|
| in the manifest | 900 |
| measured at all | 688 |
| produced trades | 661 |
| carrying a run time | 343 |

## Cohort

| Cohort | Strategies |
|---|---:|
| `excluded` | 714 |
| `E0_strict67` | 67 |
| `not_yet_tested` | 60 |
| `convergence_candidate` | 41 |
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

## Convergence candidates - 41 strategies

A warm-up exists at which every indicator stays inside the band.
That is not admission: the paired full-window run must still show
an identical trade list.

| Strategy | Profile | Chosen warm-up | Worst drift | Tested | Results |
|---|---|---|---|---|---|
| `AdaptiveMAStrategy` | `spot_long` | 288 candles | 0.0% on `kama_fast` | 2026-09-01 12:07:18 | `user_data/convergence_logs/AdaptiveMAStrategy-ladder.log` |
| `AdxStrengthStrategy` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 12:07:43 | `user_data/convergence_logs/AdxStrengthStrategy-ladder.log` |
| `AroonTrendStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:08:07 | `user_data/convergence_logs/AroonTrendStrategy-ladder.log` |
| `AtrTrailingStopStrategy` | `spot_long` | 288 candles | 0.0% on `atr` | 2026-09-01 12:08:31 | `user_data/convergence_logs/AtrTrailingStopStrategy-ladder.log` |
| `BBRSI4cust` | `spot_long` | 192 candles | 0.0% on `plus_di` | 2026-09-01 12:08:55 | `user_data/convergence_logs/BBRSI4cust-ladder.log` |
| `BBRSINaiveStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 12:09:19 | `user_data/convergence_logs/BBRSINaiveStrategy-ladder.log` |
| `BBRSIOptim2020Strategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:09:44 | `user_data/convergence_logs/BBRSIOptim2020Strategy-ladder.log` |
| `BBRSIOptimStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:10:08 | `user_data/convergence_logs/BBRSIOptimStrategy-ladder.log` |
| `BBRSIStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 12:10:32 | `user_data/convergence_logs/BBRSIStrategy-ladder.log` |
| `BB_RPB_TSL_RNG_VWAP` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 12:10:58 | `user_data/convergence_logs/BB_RPB_TSL_RNG_VWAP-ladder.log` |
| `BB_RTR` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 12:11:28 | `user_data/convergence_logs/BB_RTR-ladder.log` |
| `BbWidthExpansionStrategy` | `spot_long` | 288 candles | 0.0% on `bb_upper` | 2026-09-01 12:11:52 | `user_data/convergence_logs/BbWidthExpansionStrategy-ladder.log` |
| `BigZ07Next` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_5m` | 2026-09-01 12:15:15 | `user_data/convergence_logs/BigZ07Next-ladder.log` |
| `BigZ07Next2` | `spot_long` | 2016 candles | 0.0% on `btc_rsi_5m` | 2026-09-01 12:15:43 | `user_data/convergence_logs/BigZ07Next2-ladder.log` |
| `BinClucMadV1` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:16:09 | `user_data/convergence_logs/BinClucMadV1-ladder.log` |
| `BollingerBounceStrategy` | `spot_long` | 576 candles | 0.0% on `bb_upper` | 2026-09-01 12:16:36 | `user_data/convergence_logs/BollingerBounceStrategy-ladder.log` |
| `BopTrendStrategy` | `spot_long` | 288 candles | 0.0% on `bop_ma` | 2026-09-01 12:17:01 | `user_data/convergence_logs/BopTrendStrategy-ladder.log` |
| `BullishEngulfingStrategy` | `spot_long` | 576 candles | 0.0% on `ema50` | 2026-09-01 12:17:26 | `user_data/convergence_logs/BullishEngulfingStrategy-ladder.log` |
| `BuyOnly` | `spot_long` | 672 candles | 0.0% on `rsi` | 2026-09-01 12:17:52 | `user_data/convergence_logs/BuyOnly-ladder.log` |
| `CTIBS` | `spot_long` | 672 candles | 0.0% on `ema_135` | 2026-09-01 12:18:16 | `user_data/convergence_logs/CTIBS-ladder.log` |
| `CciMeanReversionStrategy` | `spot_long` | 576 candles | 0.0% on `cci` | 2026-09-01 12:18:42 | `user_data/convergence_logs/CciMeanReversionStrategy-ladder.log` |
| `ChaikinMoneyFlowStrategy` | `spot_long` | 288 candles | 0.0% on `cmf` | 2026-09-01 12:19:08 | `user_data/convergence_logs/ChaikinMoneyFlowStrategy-ladder.log` |
| `CombinedBinHAndClucV5Hyperoptable` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 12:21:09 | `user_data/convergence_logs/CombinedBinHAndClucV5Hyperoptable-ladder.log` |
| `CombinedBinHAndClucV8XHO` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:21:34 | `user_data/convergence_logs/CombinedBinHAndClucV8XHO-ladder.log` |
| `Combined_NFIv7_SMA` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:00 | `user_data/convergence_logs/Combined_NFIv7_SMA-ladder.log` |
| `Combined_NFIv7_SMA_Rallipanos_20210707` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:25 | `user_data/convergence_logs/Combined_NFIv7_SMA_Rallipanos_20210707-ladder.log` |
| `Combined_NFIv7_SMA_bAdBoY_20211204` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:51 | `user_data/convergence_logs/Combined_NFIv7_SMA_bAdBoY_20211204-ladder.log` |
| `CompositeScoreStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:23:15 | `user_data/convergence_logs/CompositeScoreStrategy-ladder.log` |
| `CoppockCurveStrategy` | `spot_long` | 288 candles | 0.0% on `coppock` | 2026-09-01 12:23:39 | `user_data/convergence_logs/CoppockCurveStrategy-ladder.log` |
| `DemaCrossStrategy` | `spot_long` | 288 candles | 0.0% on `dema20` | 2026-09-01 12:24:04 | `user_data/convergence_logs/DemaCrossStrategy-ladder.log` |
| `DonchianBreakoutStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:24:28 | `user_data/convergence_logs/DonchianBreakoutStrategy-ladder.log` |
| `E0V1E_DCA3` | `spot_long` | 2016 candles | 0.0% on `sma_15` | 2026-09-01 12:24:54 | `user_data/convergence_logs/E0V1E_DCA3-ladder.log` |
| `EmaRibbonStrategy` | `spot_long` | 288 candles | 0.0% on `ema8` | 2026-09-01 12:25:20 | `user_data/convergence_logs/EmaRibbonStrategy-ladder.log` |
| `FisherTransformStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:25:45 | `user_data/convergence_logs/FisherTransformStrategy-ladder.log` |
| `GoldenCrossStrategy` | `spot_long` | 2016 candles | 0.0% on `ema50` | 2026-09-01 12:26:10 | `user_data/convergence_logs/GoldenCrossStrategy-ladder.log` |
| `HeikinAshiStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:26:36 | `user_data/convergence_logs/HeikinAshiStrategy-ladder.log` |
| `HigherHighStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:27:00 | `user_data/convergence_logs/HigherHighStrategy-ladder.log` |
| `IchimokuSimpleStrategy` | `spot_long` | 288 candles | 0.0% on `senkou_b` | 2026-09-01 12:27:25 | `user_data/convergence_logs/IchimokuSimpleStrategy-ladder.log` |
| `ImpulseV1` | `spot_long` | 288 candles | 0.0% on `200_SMA` | 2026-09-01 12:27:51 | `user_data/convergence_logs/ImpulseV1-ladder.log` |
| `Inverse` | `spot_long` | 720 candles | 0.007% on `ema_200_4h` | 2026-09-01 12:28:16 | `user_data/convergence_logs/Inverse-ladder.log` |
| `InverseV2` | `spot_long` | 720 candles | 0.007% on `ema_200_4h` | 2026-09-01 12:28:42 | `user_data/convergence_logs/InverseV2-ladder.log` |

## Pending - 7 strategies

No hard failure and no verdict. Evidence is missing, which is
neither a pass nor a fail.

`Fakebuy`, `HyperStra_GSN_SMAOnly`, `InverseVolatilityPortfolio`, `RiskParityPortfolio`
`TGMA`, `haGradient`, `kalthetank`

## Not yet tested - 60 strategies

No run of any kind is recorded for these. They are not failures
and not candidates; nobody has looked. They are listed so the
corpus is not quietly reduced to the part that happened to be
convenient to measure.

| Wave | Strategies |
|---|---:|
| `not_scheduled` | 48 |
| `C_measurement_recovery` | 12 |

`A9AV`, `AstroQAV4`, `AwesomeMacdS`, `BBMod`
`BB_RPB_TSL_Tranz`, `BB_RPB_TSLmeneguzzo`, `BcmbigzDevelop`, `BinClucMadDevelop`
`BinClucMadSMADevelop`, `BinHV27_werkkrew`, `ClucHAnix5m`, `ClucHAnix_BB_RPB`
`ClucHAnix_BB_RPB_HO2`, `ClucHAnix_BB_RPB_MOD`, `Cluckie`, `CoreStrategy`
`CryptoFrogNFI`, `CryptoFrogNFIHO1A`, `CryptoFrogOffset`, `DIV_v1`
`Guacamole`, `InformativeDecoratorTest`, `Kamaflage`, `MacheteV8b`
`MacheteV8bRallimod`, `MacheteV8bRallimod2`, `MultiMA_TSL`, `MyStrategyNew10`
`NFI46Frog`, `NFI4Frog`, `NowoIchimoku1hV1`, `ONS_Portfolio`
`RSIDivTirail`, `RaposaDivergenceV1`, `ReinforcedSmoothScalpS`, `Schism`
`Schism2`, `Schism5`, `Schism6`, `SmartMoneyStrategyHyperopt`
`Solipsis3`, `Solipsis5`, `SolipsisCon`, `SqueezeMomentum`
`Strategy`, `StrategyAnalysis`, `Tank5ModulusDCA`, `Tank5ModulusDCAV3`
`TestStrategyLegacyV1`, `TestStrategyNoImplements`, `ThreeCommasStrategy`, `YourStrat`
`freqai_rl_test_strat`, `freqai_test_classifier`, `freqai_test_multimodel_classifier_strat`, `freqai_test_multimodel_strat`
`freqai_test_strat`, `qrsi`, `tacos1`, `turbov8`

## Not passing - 714 strategies, by decisive reason

A row usually fails several gates. It is grouped by the most final
one: a strategy that reads future candles is out however clean its
warm-up is.

| Reason | Meaning | Strategies |
|---|---|---:|
| `lookahead_found` | reads data it could not have had at the time | 69 |
| `technical_trap_found` | carries a published backtesting trap | 40 |
| `recursive_bias_found` | indicator value depends on how much history was loaded | 428 |
| `no_trades_in_full_measurement` | never trades over the full window | 6 |
| `canonical_implementation_not_measured` | never ran | 152 |
| `unclassified` | - | 19 |

### `lookahead_found` - 69

Reads data it could not have had at the time.

`ARIMA_15`, `AlexBTK_CT`, `AlexBattleTankKiller`, `AlexBattleTankKillerV3`
`AlexBattleTankKillerV40H`, `Auto_EI_t4c0s`, `BBBreakoutStrategy`, `BB_RPB_TSL_c7c477d_20211030`
`BreakoutStrategy`, `BuyAllSellAllStrategy`, `CCIStrategy`, `Cci`
`EI1_t4c0s_V4`, `EI4_t4c0s_V2`, `EI4_t4c0s_V2_2`, `ElliotWave`
`FVGAdvancedStrategy_V2`, `FakeoutStrategy`, `FrayLIVEBTC15m`, `FrostAuraRandomStrategy`
`Heracles`, `HyperStra_SMAOnly`, `Ichi`, `IchiVwapAdx`
`IchimokuCloudStrategy`, `Leveraged`, `LookaheadStrategy`, `LorentzianClassification`
`MSO`, `MaxSharpePortfolio`, `MinimumVariancePortfolio`, `MomentumRegimeBasket`
`NOTankAi_17`, `NOTankAi_19`, `NWEv6`, `NeuroV1`
`NfiNextModded`, `NostalgiaForInfinityNext`, `NostalgiaForInfinityNext772`, `NostalgiaForInfinityNextV7155`
`NostalgiaForInfinityNext_ChangeToTower_V5_2`, `NostalgiaForInfinityNext_ChangeToTower_V5_3`, `NostalgiaForInfinityNext_ChangeToTower_V6`, `NostalgiaForInfinityNext_maximizer`
`NostalgiaForInfinityV7_7_2`, `NostalgiaForInfinityXw`, `Obelisk_Ichimoku_Slow_v1_3`, `Obelisk_Ichimoku_ZEMA_v1`
`Obelisk_TradePro_Ichi_v1_1`, `Obelisk_TradePro_Ichi_v2_1`, `Precognition`, `ReinforcedQuickie`
`Renko`, `Rsiqui`, `RsiquiV2`, `RsiquiV5`
`RsiquiV5_long_only`, `StarRise_strat3`, `Stinkfist`, `TSPredict`
`Tank1Modulus`, `UziChan`, `UziChan2`, `Zeus`
`grad`, `ichiV1`, `ichiV1_Marius`, `tsp0chicken`
`wtc`

### `technical_trap_found` - 40

Carries a published backtesting trap.

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

### `recursive_bias_found` - 428

Indicator value depends on how much history was loaded.

`ASDTSRockwellTrading`, `ActionZone`, `AdxSmas`, `AdxSmasS`
`AlligatorStrategy`, `AlmgrenChrissStrategy`, `Apollo11`, `AverageStrategy`
`AwesomeMacd`, `BBMod1`, `BBRSI2`, `BBRSI21`
`BBRSI3366`, `BBRSIOptimizedStrategy`, `BBRSITV`, `BB_RPB_TSL`
`BB_RPB_TSL_2`, `BB_RPB_TSL_BI`, `BB_RPB_TSL_BIV1`, `BB_RPB_TSL_RNG`
`BB_RPB_TSL_RNG_2`, `BB_RPB_TSL_RNG_TBS`, `BB_RPB_TSL_RNG_TBS_GOLD`, `BB_RPB_TSL_SMA_Tranz`
`BB_RPB_TSL_SMA_Tranz_TB_1_1_1`, `BB_RPB_TSL_SMA_Tranz_TB_MOD`, `BBands`, `BBandsRSI`
`BBlower`, `Babico_SMA5xBBmid`, `Bandtastic`, `BbandRsi`
`BbandRsiRolling`, `BcmbigzV1`, `BeastBotXBLR6`, `BeastBotXBLR7`
`BigZ0307HO`, `BigZ04`, `BigZ0407`, `BigZ0407HO`
`BigZ04HO`, `BigZ04HO2`, `BigZ06`, `BigZ07`
`BinHV27`, `BinHV27F`, `BinHV27_short`, `BinHV45HO`
`BinMfiBTCv5003`, `BuyOrDie`, `CMCWinner`, `COPY_HL`
`Candle2`, `Chandem`, `Chandemtwo`, `Cluc4`
`Cluc4werk`, `Cluc5werk`, `ClucFiatROI`, `ClucFiatSlow`
`ClucHAnix`, `ClucHAnix_BB_RPB_MOD2_ROI`, `ClucHAnix_BB_RPB_MOD_CTT`, `ClucHAnix_BB_RPB_MOD_E0V1E_ROI`
`ClucHAnix_hhll`, `ClucMay72018`, `CofiBitStrategy`, `CombinedBinHAndCluc`
`CombinedBinHAndCluc2021`, `CombinedBinHAndCluc2021Bull`, `CombinedBinHAndClucHyperV0`, `CombinedBinHAndClucHyperV3`
`CombinedBinHAndClucV2`, `CombinedBinHAndClucV4`, `CombinedBinHAndClucV5`, `CombinedBinHAndClucV8`
`CombinedBinHAndClucV8Hyper`, `CombinedBinHAndClucV8XH`, `Combined_Indicators`, `Combined_NFIv6_SMA`
`ConsensusShort`, `CrossEMAStrategy`, `CustomStoplossWithPSAR`, `DCBBBounce`
`DD`, `DWT_LongShort`, `DWT_short`, `DevilStra`
`Diamond`, `Dimond`, `Divergences`, `Dracula`
`E0V1E`, `E0V1E2`, `E0V1E_ewo`, `E0V1E_protections`
`E0V1E_strs`, `EMA50`, `EMA520015_V17`, `EMABreakout`
`EMASkipPump`, `EasyInEasyOut`, `ElliotV4`, `ElliotV531`
`ElliotV5HO`, `ElliotV5HOMod2`, `ElliotV5HOMod3`, `ElliotV7`
`ElliotV8HO`, `FOttStrategy`, `FRAYSTRAT`, `FReinforcedStrategy`
`FSampleStrategy`, `FTT_DWT_FBB_FUTURES`, `FVGChannel`, `FisherHull`
`FiveMinCrossAbove`, `ForexRobootSuperScalper`, `FrayStratBTC`, `Freqtrade_backtest_validation_freqtrade1`
`FrostAuraM115mStrategy`, `FrostAuraM11hStrategy`, `FrostAuraM21hStrategy`, `FrostAuraM315mStrategy`
`FrostAuraM31hStrategy`, `GKD_Baseline`, `GKD_BaselineAllMAs`, `GKD_C`
`GKD_CT`, `GKD_FisherTransform`, `GKD_FisherTransformMTF`, `GKD_HurstExponent`
`GKD_PFE`, `GPTREV`, `GeneStrategy`, `GeneStrategy_v2`
`GeneTrader_gen10_1734895087_6007`, `GeneTrader_gen5_1735014093_4541`, `GodCard`, `GodStraNew`
`GodStraNew40`, `GodStraNew_SMAonly`, `GoldHedgeZeroMACD`, `HEW`
`HSI`, `Hacklemore2`, `Hacklemore3`, `Hacklemost`
`HansenSmaOffsetV1`, `HilbertSineWave`, `HourBasedStrategy`, `HurstCycle3`
`HurstCycle7`, `HurstCycleV4`, `HurstCycleV5`, `HurstCycleV5RSI`
`HurstCycleV6`, `INSIDEUP`, `Ichess`, `Ichimoku`
`InformativeSample`, `JuicyTrend`, `KAMACCIRSI_new`, `KC_BB`
`KeltnerChannelStrategy`, `KitchenSink`, `Lateralus`, `LinearRegressionStrategy`
`Low_BB`, `LuxOSC`, `MAC`, `MACDRL`
`MACDRS`, `MACDStrategy`, `MACDStrategyADA`, `MACDStrategyAVAX`
`MACDStrategyBTC`, `MACDStrategyENJ`, `MACDStrategyETC`, `MACDStrategySOL`
`MACDStrategyXRP`, `MACDStrategy_crossed`, `MACDZeroCrossStrategy`, `MACD_EMA`
`MACD_TRI_EMA`, `MFI`, `MabStra`, `Macd`
`MacdAdxStrategy`, `MacdZeroCrossStrategy`, `Maro4hMacdSd`, `Martin`
`MiniLambo`, `Minmax`, `MomStrategy`, `MomentumScoreStrategy`
`Momentumv2`, `MoneyFlowStrategy`, `MontrealStrategy`, `MultiFactorConfluenceStrategy`
`MultiMA_TSL3`, `MultiMA_TSL3_Mod`, `MultiOffsetLamboV0`, `MultiRSI`
`MyStratV1`, `NASOSRv6_private_Reinuvader_20211121`, `NASOSv5`, `NEWTEST15m`
`NFI46`, `NFI46FrogZ`, `NFI46Offset`, `NFI46OffsetHOA1`
`NFI46Z`, `NFI47V2`, `NFI5MOHO`, `NFI5MOHO2`
`NFI5MOHO_WIP`, `NFI5MOHO_WIP_1`, `NFI5MOHO_WIP_2`, `NFI731_BUSD`
`NFI7MOHO`, `NFINextMOHO`, `NFINextMOHO2`, `NFINextMultiOffsetAndHO`
`NFINextMultiOffsetAndHO2`, `NFIX_BB_RPB`, `NFIX_BB_RPB_c7c477d_20211030`, `NOTankAi_15`
`NOTankAi_15_Cleaned`, `NOTankAi_15_Cleaned_v2`, `NormalizerStrategy`, `NormalizerStrategyHO2`
`Nostalgia`, `NostalgiaForInfinity772martinsk3`, `NostalgiaForInfinityNextGen`, `NostalgiaForInfinityNextGen_TSL`
`NostalgiaForInfinityV3`, `NostalgiaForInfinityV4`, `NostalgiaForInfinityV4HO`, `NostalgiaForInfinityV5`
`NostalgiaForInfinityV5MultiOffsetAndHO`, `NostalgiaForInfinityV5MultiOffsetAndHO2`, `NostalgiaForInfinityV6`, `NostalgiaForInfinityV6HO`
`NostalgiaForInfinityV7`, `NostalgiaForInfinityV7_SMA`, `NostalgiaForInfinityV7_SMAv2`, `NostalgiaForInfinityV7_SMAv2_1`
`NostalgiaForInfinityX`, `NostalgiaForInfinityX2`, `NostalgiaForInfinityX3`, `NostalgiaForInfinityX4`
`NostalgiaForInfinityX5`, `NostalgiaForInfinityX6`, `NostalgiaForInfinityX7`, `NotAnotherSMAOffSetStrategy_V2`
`NotAnotherSMAOffsetStrategy`, `NotAnotherSMAOffsetStrategyHO`, `NotAnotherSMAOffsetStrategyHOv3`, `NotAnotherSMAOffsetStrategyLite`
`NotAnotherSMAOffsetStrategyModHO`, `NotAnotherSMAOffsetStrategyModHO_LamineDz_20210901`, `NotAnotherSMAOffsetStrategyX1`, `NotAnotherSMAOffsetStrategy_uzi`
`NotAnotherSMAOffsetStrategy_uzi3`, `NowoIchimoku1hV2`, `ONUR`, `ObeliskRSI_v6_1`
`ObvTrendStrategy`, `OmaGann`, `PRICEFOLLOWING`, `PRICEFOLLOWING2`
`PRICEFOLLOWINGX`, `ParabolicSarStrategy`, `PatternRecognition`, `PolymarketPortfolio`
`PpoMomentumStrategy`, `PriceActionCandleStrategy`, `PriceChannelStrategy`, `PumpDetector`
`Quickie`, `RSI`, `RSI_BB`, `RSI_EMA_strategy`
`RSIv2`, `RalliV1`, `RalliV1_disable56`, `ReinforcedAverageStrategy`
`ReinforcedSmoothScalp`, `RocMomentumStrategy`, `Roth01`, `Roth03`
`RsiBollingerStrategy`, `RsiDivergenceStrategy`, `SAR`, `SMAOffset`
`SMAOffsetProtectOpt`, `SMAOffsetProtectOptV0`, `SMAOffsetProtectOptV1`, `SMAOffsetProtectOptV1HO1`
`SMAOffsetProtectOptV1Mod`, `SMAOffsetProtectOptV1Mod2`, `SMAOffsetProtectOptV1_kkeue_20210619`, `SMAOffset_Hippocritical_dca`
`SMAOffset_Hippocritical_dca_leverage`, `SMAOffset_Hippocritical_dca_old`, `SMAOffset_Hippocritical_dca_protections`, `SMA_BBRSI`
`SRsi`, `STRATEGY_RSI_BB_BOUNDS_CROSS`, `STRATEGY_RSI_BB_CROSS`, `SampleStrategy`
`Sar`, `Saturn5`, `Scalp`, `Schism2MM`
`Schism3`, `Schism4`, `Seb`, `Simple`
`SimpleHopt`, `SlowPotato`, `SmaRsiStrategy`, `SmartMoneyStrategy`
`SmoothOperator`, `SmoothScalp`, `SqueezeMomentumStrategy`, `StarRise`
`StarRise_strat`, `StochasticOversoldStrategy`, `StochasticRsiStrategy`, `Strategy001`
`Strategy001_custom_exit`, `Strategy001_custom_sell`, `Strategy002`, `Strategy003`
`Strategy004`, `Strategy005`, `StrategyScalpingFast`, `StrategyScalpingFast2`
`StrategyTestV2`, `StrategyTestV3`, `SuperTrend`, `SupertrendStrategy`
`SwingHighToSky`, `TD`, `TEMA`, `TRIWAVE`
`TWAPStrategy`, `TechnicalExampleStrategy`, `TemaMaster`, `TemaMaster3`
`TemaPure`, `TemaPureNeat`, `TemaPureTwo`, `TemaStrategy`
`TheForce`, `ToTheMoon`, `TouchEmaDelayStrategy`, `TouchEmaStrategy`
`TrendAtrStrategy`, `TrendFollowingStrategy`, `TrendRiderStrategy`, `Trend_Strength_Directional`
`TripleEmaStrategy`, `TrixSignalStrategy`, `TrixV21Strategy`, `TrixV23Strategy`
`TwoCandle`, `UniversalMACD`, `Uptrend`, `VWAP`
`VolatilitySystem`, `VolatilitySystemV2`, `VolumeBreakoutStrategy`, `VortexStrategy`
`VwapReversionStrategy`, `WaveTrendStra`, `WilliamsRStrategy`, `YOLO`
`ZScoreMeanReversionStrategy`, `ZaratustraDCA2_06`, `ZaratustraDCA2_07`, `ZaratustraDCA5`
`adaptive`, `adxbbrsi2`, `bbandrsi`, `bbrsi`
`bbrsi4Freq`, `conny`, `cryptotankV2`, `custom`
`dualwave`, `e6v34`, `eltoro`, `eltoro1_4`
`eltoro1_4_simple`, `ema`, `epretrace`, `falconTrader`
`flawless_lambo`, `gettinMoist`, `hansencandlepatternV1`, `heikin`
`hlhb`, `keltnerchannel`, `lambotest`, `mabStra`
`moonhouse`, `newstrategy53`, `newstrategy53_22`, `pcb20`
`pmaxTest`, `slope_is_dopeCT`, `slownsteady`, `stoploss`
`stratfib`, `strato`, `tacos`, `tbtest`
`thetank3`, `thetank4TV`, `true_lambo`, `twinturboV8`
`twinturboV8_2`, `ultratank`, `wavetrend`, `wavetrend_rsi`

### `no_trades_in_full_measurement` - 6

Never trades over the full window.

`DoubleEMACrossoverWithTrend`, `EMAPriceCrossoverWithThreshold`, `Insomnia_short`, `MACDCrossoverWithTrend`
`RSIDirectionalWithTrend`, `RSIDirectionalWithTrendSlow`

### `canonical_implementation_not_measured` - 152

Never ran.

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

### `unclassified` - 19

`ARIMASTR`, `BasketStrategy`, `BreakEven`, `DoesNothingStrategy`
`ExponentialGradientPortfolio`, `FundingCarry`, `Hacklemore`, `HarmonicDivergence`
`HarmonicDivergence_fix`, `Matrix`, `Miku_PP_v3`, `MostOfAll`
`MyStrategyTemplate`, `Obelisk_3EMA_StochRSI_ATR`, `ViN`, `beta_factors_model`
`custom_sell`, `ep3mas2`, `zorkv7_0_0`

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
| `first_measurement` | 60 |
| `paired_full_window_equivalence` | 41 |
| `convergence_not_converged_within_ladder` | 10 |

Per-row detail, including every evidence path, is in
`STRATEGY_STATUS.csv`.
