# Strategy status - current evidence for all 900 rows

**Generated 2026-09-01 22:50:49 by `strategy_status.py`.** Regenerate it rather than editing it.

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
file's time and is labelled `log_mtime` for that reason. 237 of 900 rows
have neither and are left empty rather than given an invented time.

## Measurement

| | Strategies |
|---|---:|
| in the manifest | 900 |
| measured at all | 741 |
| produced trades | 711 |
| carrying a run time | 663 |

## Cohort

| Cohort | Strategies |
|---|---:|
| `convergence_candidate` | 378 |
| `excluded` | 209 |
| `exclusion_unconfirmed` | 168 |
| `E0_strict67` | 67 |
| `not_tested_in_current_runtime` | 60 |
| `E1_expanded` | 11 |
| `pending` | 7 |

## How freqtrade was called

A result is not reproducible from its verdict alone, so each row
carries the command it was produced by. **`recorded`** is the argv that
actually ran. **`reconstructed`** is derived from the run profile and
the window, because nothing stored the call before 2026-09-01; it is
labelled because a reconstruction is a different claim from a
recording. 345 of 2102 commands are recorded so far, and every new run
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
| `AlwaysBuy` | `spot_long` | `E1_expanded` | 32359 | `wave_b:1:superseded` | - | - |
| `BinHV45` | `spot_long` | `E1_expanded` | 749 | `wave_b:40:superseded` | - | - |
| `BinHV45_kanaxe` | `spot_long` | `E1_expanded` | 1798 | `wave_b:40:superseded` | - | - |
| `BinHV45_stash` | `spot_long` | `E1_expanded` | 1700 | `wave_b:40:superseded` | - | - |
| `BinHV45_werkkrew` | `spot_long` | `E1_expanded` | 760 | `wave_b:40:superseded` | - | - |
| `BollingerBandStrategy` | `spot_long` | `E1_expanded` | 16302 | `wave_b:21:superseded` | - | - |
| `CCI_BB` | `spot_long` | `E1_expanded` | 926 | `wave_b:20:superseded` | - | - |
| `HourBasedStrategy_5m` | `spot_long` | `E1_expanded` | 11784 | `wave_b:1:superseded` | - | - |
| `NowoIchimoku5mV2` | `spot_long` | `E1_expanded` | 49 | `native` | 2026-08-31 15:19:45 | [archive](user_data/profile_smoke/NowoIchimoku5mV2-2026-08-31_15-19-45.zip) |
| `ObeliskIM_v1_1` | `spot_long` | `E1_expanded` | 64 | `native` | 2026-08-31 15:20:09 | [archive](user_data/profile_smoke/ObeliskIM_v1_1-2026-08-31_15-20-09.zip) |
| `simple_patterns` | `spot_long` | `E1_expanded` | 1845 | `native` | 2026-08-31 15:55:52 | [archive](user_data/profile_smoke/simple_patterns-2026-08-31_15-55-52.zip) |

The calls behind each, one per gate:

- `BBRSIv2`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIv2 --strategy-path user_data/profile_bias_strategies/BBRSIv2 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BBRSIv2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BBRSIv2 --timerange 20190101-20190401 --no-color
  ```
- `BigTrader`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigTrader --strategy-path repos/TheoBrigitte_freqtrade/strategies/profiters --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigTrader --strategy-path repos/TheoBrigitte_freqtrade/strategies/profiters --timerange 20190101-20190401 --no-color
  ```
- `BigZ03`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03 --strategy-path user_data/profile_bias_strategies/BigZ03 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03 --strategy-path repos/davidzr_freqtrade-strategies/strategies/BigZ03 --timerange 20190101-20190401 --no-color
  ```
- `BigZ03HO`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03HO --strategy-path user_data/profile_bias_strategies/BigZ03HO --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ03HO --strategy-path repos/davidzr_freqtrade-strategies/strategies/BigZ03HO --timerange 20190101-20190401 --no-color
  ```
- `BigZ04_TSL3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `BigZ04_TSL4`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL4 --strategy-path user_data/profile_bias_strategies/BigZ04_TSL4 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BigZ04_TSL4 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20190101-20190401 --no-color
  ```
- `BinClucMad`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMad --strategy-path user_data/profile_bias_strategies/BinClucMad --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinClucMad --strategy-path repos/davidzr_freqtrade-strategies/strategies/BinClucMad --timerange 20190101-20190401 --no-color
  ```
- `BuyRegions`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyRegions --strategy-path repos/nateemma_strategies/TSPredict --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BuyRegions --strategy-path repos/nateemma_strategies/TSPredict --timerange 20190101-20190401 --no-color
  ```
- `Cluc7werk`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc7werk --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Cluc7werk --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5M_E0V1E`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E --strategy-path user_data/profile_bias_strategies/ClucHAnix_5M_E0V1E --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5M_E0V1E --strategy-path repos/phuchust_freqtrade_strategy --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5m`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5m1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `ClucHAnix_5m_old`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m_old --strategy-path user_data/profile_bias_strategies/ClucHAnix_5m_old --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAnix_5m_old --strategy-path repos/TheoBrigitte_freqtrade/strategies/cluc --timerange 20190101-20190401 --no-color
  ```
- `ClucHAwerk`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAwerk --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ClucHAwerk --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV3`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV3 --strategy-path user_data/profile_bias_strategies/CombinedBinHAndClucV3 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/CombinedBinHAndClucV3 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV6`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV6 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHAndClucV7`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV7 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHAndClucV7 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV5 --strategy-path user_data/profile_bias_strategies/CombinedBinHClucAndMADV5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV5 --strategy-path repos/davidzr_freqtrade-strategies/strategies/CombinedBinHClucAndMADV5 --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV6`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV6 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV6 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `CombinedBinHClucAndMADV9`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV9 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CombinedBinHClucAndMADV9 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `EMA_CROSSOVER_STRATEGY`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA_CROSSOVER_STRATEGY --strategy-path user_data/profile_bias_strategies/EMA_CROSSOVER_STRATEGY --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy EMA_CROSSOVER_STRATEGY --strategy-path repos/davidzr_freqtrade-strategies/strategies/EMA_CROSSOVER_STRATEGY --timerange 20190101-20190401 --no-color
  ```
- `ElliotV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV2 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/ElliotV2 --timerange 20190101-20190401 --no-color
  ```
- `ElliotV5_SMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5_SMA --strategy-path repos/TheoBrigitte_freqtrade/strategies/ElliotV5_SMA --timerange 20200101-20220101 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ElliotV5_SMA --strategy-path repos/TheoBrigitte_freqtrade/strategies/ElliotV5_SMA --timerange 20190101-20190401 --no-color
  ```
- `FAdxSmaStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FAdxSmaStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FAdxSmaStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --no-color
  ```
- `FSupertrendStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long.json --strategy FSupertrendStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FSupertrendStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long.json --strategy FSupertrendStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long.json --strategy FSupertrendStrategy --strategy-path repos/freqtrade_freqtrade-strategies/user_data/strategies/futures --timerange 20200301-20200401 --no-color
  ```
- `FastSupertrend_ts_origstop_fix`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/FastSupertrend_ts_origstop_fix --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy FastSupertrend_ts_origstop_fix --strategy-path user_data/profile_repairs --timerange 20200301-20200401 --no-color
  ```
- `FlawlessVictory`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy FlawlessVictory --strategy-path user_data/profile_bias_strategies/FlawlessVictory --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy FlawlessVictory --strategy-path repos/seannowotny_FlawlessVictoryPort/user_data/strategies --timerange 20190101-20190401 --no-color
  ```
- `ForexSignal`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ForexSignal --strategy-path user_data/profile_bias_strategies/ForexSignal --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ForexSignal --strategy-path repos/davidzr_freqtrade-strategies/strategies/ForexSignal --timerange 20190101-20190401 --no-color
  ```
- `Gumbo1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Gumbo1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Gumbo1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `Ichimoku_v31`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v31 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v31 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `Ichimoku_v37`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v37 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Ichimoku_v37 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `KAMACCIRSI`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy KAMACCIRSI --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `MACD_TRIPLE_MA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRIPLE_MA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MACD_TRIPLE_MA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `MADisplaceV3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MADisplaceV3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MADisplaceV3 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `MacdStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdStrategy --strategy-path repos/DutchCryptoDad_FreqtradeBotStrategyDevelopmentForBeginners --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MacdStrategy --strategy-path repos/DutchCryptoDad_FreqtradeBotStrategyDevelopmentForBeginners --timerange 20190101-20190401 --no-color
  ```
- `MarketChyperHyperStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy MarketChyperHyperStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy MarketChyperHyperStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `NWEv6_new`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NWEv6_new --strategy-path user_data/profile_bias_strategies/NWEv6_new --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NWEv6_new --strategy-path repos/anakein_beastbotXB/working --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV1`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV1 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `NostalgiaForInfinityV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NostalgiaForInfinityV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `PowerTower`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy PowerTower --strategy-path user_data/profile_bias_strategies/PowerTower --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy PowerTower --strategy-path repos/TheoBrigitte_freqtrade/strategies/freqtrade-strategies --timerange 20190101-20190401 --no-color
  ```
- `RegimeFilterStrategy`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy RegimeFilterStrategy --strategy-path repos/Bananajoexxc_RegimeFilterStrategy-Freqtrade/strategies --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/RegimeFilterStrategy --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy RegimeFilterStrategy --strategy-path repos/Bananajoexxc_RegimeFilterStrategy-Freqtrade/strategies --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy RegimeFilterStrategy --strategy-path repos/Bananajoexxc_RegimeFilterStrategy-Freqtrade/strategies --timerange 20200301-20200401 --no-color
  ```
- `RobotradingBody`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy RobotradingBody --strategy-path user_data/profile_bias_strategies/RobotradingBody --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy RobotradingBody --strategy-path repos/davidzr_freqtrade-strategies/strategies/RobotradingBody --timerange 20190101-20190401 --no-color
  ```
- `SMAIP3`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAIP3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/SMAIP3 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAIP3 --strategy-path repos/davidzr_freqtrade-strategies/strategies/SMAIP3 --timerange 20190101-20190401 --no-color
  ```
- `SMAOG`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOG --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOG --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20190101-20190401 --no-color
  ```
- `SMAOffsetV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SMAOffsetV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `SampleStrategyV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategyV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy SampleStrategyV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `Slowbro`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy Slowbro --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy Slowbro --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `StochRSITEMA`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochRSITEMA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochRSITEMA --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `StochasticCciStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticCciStrategy --strategy-path user_data/profile_bias_strategies/StochasticCciStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy StochasticCciStrategy --strategy-path repos/mlsys-io_PortfolioBench/strategy --timerange 20190101-20190401 --no-color
  ```
- `TDSequentialStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TDSequentialStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TDSequentialStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `TenderEnter`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TenderEnter --strategy-path user_data/profile_bias_strategies/TenderEnter --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TenderEnter --strategy-path repos/davidzr_freqtrade-strategies/strategies/TenderEnter --timerange 20190101-20190401 --no-color
  ```
- `TheRealPullbackV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TheRealPullbackV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TheRealPullbackV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `TrixStrategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixStrategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `TrixV15Strategy`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV15Strategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy TrixV15Strategy --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `UltimateMomentumIndicator`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy UltimateMomentumIndicator --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy UltimateMomentumIndicator --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `XtraThicc`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy XtraThicc --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy XtraThicc --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `adaptive_trend`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive_trend --strategy-path repos/mlsys-io_PortfolioBench/strategy/adaptive_trend --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy adaptive_trend --strategy-path repos/mlsys-io_PortfolioBench/strategy/adaptive_trend --timerange 20190101-20190401 --no-color
  ```
- `bestV2`
  ```
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy bestV2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/bestV2 --timerange 20200301-20260820 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy bestV2 --strategy-path repos/davidzr_freqtrade-strategies/strategies/bestV2 --timerange 20190101-20190401 --no-color
  ```
- `botbaby`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy botbaby --strategy-path user_data/profile_bias_strategies/botbaby --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy botbaby --strategy-path repos/davidzr_freqtrade-strategies/strategies/botbaby --timerange 20190101-20190401 --no-color
  ```
- `cryptotank`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotank --strategy-path user_data/profile_bias_strategies/cryptotank --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotank --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20190101-20190401 --no-color
  ```
- `cryptotankV5`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV5 --strategy-path user_data/profile_bias_strategies/cryptotankV5 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy cryptotankV5 --strategy-path repos/jaredrsommer_freqtradestrategies --timerange 20190101-20190401 --no-color
  ```
- `fahmibah`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy fahmibah --strategy-path user_data/profile_bias_strategies/fahmibah --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy fahmibah --strategy-path repos/davidzr_freqtrade-strategies/strategies/fahmibah --timerange 20190101-20190401 --no-color
  ```
- `momentum`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --no-color
  ```
- `momentum_long`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy momentum_long --strategy-path user_data/profile_bias_strategies/momentum_long --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy momentum_long --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20190101-20190401 --no-color
  ```
- `momentum_rsi`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_rsi --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum_rsi --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_rsi --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_rsi --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --no-color
  ```
- `momentum_wick`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_wick --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/momentum_wick --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_wick --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/futures_futures_long_short.json --strategy momentum_wick --strategy-path repos/TheoBrigitte_freqtrade/strategies/momentum --timerange 20200301-20200401 --no-color
  ```
- `AlwaysBuy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy AlwaysBuy --strategy-path user_data/profile_bias_strategies/AlwaysBuy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy AlwaysBuy --strategy-path repos/davidzr_freqtrade-strategies/strategies/AlwaysBuy --timerange 20190101-20190401 --no-color
  ```
- `BinHV45`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45 --strategy-path user_data/profile_bias_strategies/BinHV45 --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45 --strategy-path repos/Foxel05_freqtrade-stuff/strategies --timerange 20190101-20190401 --no-color
  ```
- `BinHV45_kanaxe`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_kanaxe --strategy-path user_data/profile_bias_strategies/BinHV45_kanaxe --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_kanaxe --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20190101-20190401 --no-color
  ```
- `BinHV45_stash`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_stash --strategy-path user_data/profile_bias_strategies/BinHV45_stash --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_stash --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20190101-20190401 --no-color
  ```
- `BinHV45_werkkrew`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_werkkrew --strategy-path user_data/profile_bias_strategies/BinHV45_werkkrew --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BinHV45_werkkrew --strategy-path repos/TheoBrigitte_freqtrade/strategies/BinHV45 --timerange 20190101-20190401 --no-color
  ```
- `BollingerBandStrategy`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBandStrategy --strategy-path user_data/profile_bias_strategies/BollingerBandStrategy --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy BollingerBandStrategy --strategy-path repos/flaviosiotto_freqtrade-strategy/user_data/strategies --timerange 20190101-20190401 --no-color
  ```
- `CCI_BB`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy CCI_BB --strategy-path user_data/profile_bias_strategies/CCI_BB --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy CCI_BB --strategy-path repos/mikedigriz_freqtrade-strategy-mikedigriz/strategies --timerange 20190101-20190401 --no-color
  ```
- `HourBasedStrategy_5m`
  ```
  lookahead  [recorded] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy HourBasedStrategy_5m --strategy-path user_data/profile_bias_strategies/HourBasedStrategy_5m --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy HourBasedStrategy_5m --strategy-path repos/eovie_freqtrade_strs/binance/Archive --timerange 20190101-20190401 --no-color
  ```
- `NowoIchimoku5mV2`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy NowoIchimoku5mV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/NowoIchimoku5mV2 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy NowoIchimoku5mV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy NowoIchimoku5mV2 --strategy-path repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `ObeliskIM_v1_1`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy ObeliskIM_v1_1 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/ObeliskIM_v1_1 --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy ObeliskIM_v1_1 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy ObeliskIM_v1_1 --strategy-path repair/patched/repos/PeetCrypto_freqtrade-stuff --timerange 20190101-20190401 --no-color
  ```
- `simple_patterns`
  ```
  backtest   [reconstructed] freqtrade backtesting --config user_data/config.json --strategy simple_patterns --strategy-path repos/TheoBrigitte_freqtrade/strategies/yodo --timerange 20200301-20200401 --fee 0.001 --export trades --backtest-directory user_data/profile_smoke/simple_patterns --cache none
  lookahead  [reconstructed] freqtrade lookahead-analysis --config user_data/profile_configs/bias_spot.json --strategy simple_patterns --strategy-path repos/TheoBrigitte_freqtrade/strategies/yodo --timerange 20190101-20190401 --no-color
  recursive  [reconstructed] freqtrade recursive-analysis --config user_data/profile_configs/bias_spot.json --strategy simple_patterns --strategy-path repos/TheoBrigitte_freqtrade/strategies/yodo --timerange 20190101-20190401 --no-color
  ```

## Convergence candidates - 378 strategies

A warm-up exists at which every indicator stays inside the band.
That is not admission: the paired full-window run must still show
an identical trade list.

| Strategy | Profile | Chosen warm-up | Worst drift | Tested | Results |
|---|---|---|---|---|---|
| `ASDTSRockwellTrading` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 15:32:20 | `user_data/convergence_logs/ASDTSRockwellTrading-ladder.log` |
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
| `BBRSI2` | `spot_long` | 1440 candles | 0.0% on `bb_lowerband` | 2026-09-01 15:33:59 | `user_data/convergence_logs/BBRSI2-ladder.log` |
| `BBRSI21` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 15:34:51 | `user_data/convergence_logs/BBRSI21-ladder.log` |
| `BBRSI3366` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 15:35:41 | `user_data/convergence_logs/BBRSI3366-ladder.log` |
| `BBRSI4cust` | `spot_long` | 192 candles | 0.0% on `plus_di` | 2026-09-01 12:08:55 | `user_data/convergence_logs/BBRSI4cust-ladder.log` |
| `BBRSINaiveStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 12:09:19 | `user_data/convergence_logs/BBRSINaiveStrategy-ladder.log` |
| `BBRSIOptim2020Strategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:09:44 | `user_data/convergence_logs/BBRSIOptim2020Strategy-ladder.log` |
| `BBRSIOptimStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:10:08 | `user_data/convergence_logs/BBRSIOptimStrategy-ladder.log` |
| `BBRSIOptimizedStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 13:02:19 | `user_data/convergence_logs/BBRSIOptimizedStrategy-ladder.log` |
| `BBRSIStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 12:10:32 | `user_data/convergence_logs/BBRSIStrategy-ladder.log` |
| `BBRSITV` | `spot_long` | 2016 candles | 0.0% on `rsi` | 2026-09-01 13:02:44 | `user_data/convergence_logs/BBRSITV-ladder.log` |
| `BB_RPB_TSL_RNG` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 13:35:37 | `user_data/convergence_logs/BB_RPB_TSL_RNG-ladder.log` |
| `BB_RPB_TSL_RNG_2` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 15:36:32 | `user_data/convergence_logs/BB_RPB_TSL_RNG_2-ladder.log` |
| `BB_RPB_TSL_RNG_TBS` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 13:36:25 | `user_data/convergence_logs/BB_RPB_TSL_RNG_TBS-ladder.log` |
| `BB_RPB_TSL_RNG_TBS_GOLD` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 13:37:28 | `user_data/convergence_logs/BB_RPB_TSL_RNG_TBS_GOLD-ladder.log` |
| `BB_RPB_TSL_RNG_VWAP` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 12:10:58 | `user_data/convergence_logs/BB_RPB_TSL_RNG_VWAP-ladder.log` |
| `BB_RTR` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 12:11:28 | `user_data/convergence_logs/BB_RTR-ladder.log` |
| `BBands` | `spot_long` | 1440 candles | 0.0% on `adx` | 2026-09-01 13:04:20 | `user_data/convergence_logs/BBands-ladder.log` |
| `BBandsRSI` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 13:04:45 | `user_data/convergence_logs/BBandsRSI-ladder.log` |
| `BBlower` | `spot_long` | 576 candles | 0.0% on `CMO` | 2026-09-01 15:37:20 | `user_data/convergence_logs/BBlower-ladder.log` |
| `Babico_SMA5xBBmid` | `spot_long` | 30 candles | 0.0% on `bb_low` | 2026-09-01 13:38:15 | `user_data/convergence_logs/Babico_SMA5xBBmid-ladder.log` |
| `Bandtastic` | `spot_long` | 1344 candles | 0.0% on `rsi` | 2026-09-01 15:38:10 | `user_data/convergence_logs/Bandtastic-ladder.log` |
| `BbWidthExpansionStrategy` | `spot_long` | 288 candles | 0.0% on `bb_upper` | 2026-09-01 12:11:52 | `user_data/convergence_logs/BbWidthExpansionStrategy-ladder.log` |
| `BbandRsi` | `spot_long` | 1440 candles | 0.0% on `bb_lowerband` | 2026-09-01 16:31:44 | `user_data/convergence_logs/BbandRsi-ladder.log` |
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
| `BuyOrDie` | `spot_long` | 288 candles | 0.0% on `hma_20` | 2026-09-01 15:38:59 | `user_data/convergence_logs/BuyOrDie-ladder.log` |
| `CMCWinner` | `spot_long` | 672 candles | 0.0% on `mfi` | 2026-09-01 13:42:18 | `user_data/convergence_logs/CMCWinner-ladder.log` |
| `COPY_HL` | `futures_long` | 24 candles | 0.0% on `None` | 2026-09-01 13:43:04 | `user_data/convergence_logs/COPY_HL-ladder.log` |
| `CTIBS` | `spot_long` | 672 candles | 0.0% on `ema_135` | 2026-09-01 12:18:16 | `user_data/convergence_logs/CTIBS-ladder.log` |
| `Candle2` | `spot_long` | 168 candles | 0.0% on `range_4h` | 2026-09-01 15:39:47 | `user_data/convergence_logs/Candle2-ladder.log` |
| `CciMeanReversionStrategy` | `spot_long` | 576 candles | 0.0% on `cci` | 2026-09-01 12:18:42 | `user_data/convergence_logs/CciMeanReversionStrategy-ladder.log` |
| `ChaikinMoneyFlowStrategy` | `spot_long` | 288 candles | 0.0% on `cmf` | 2026-09-01 12:19:08 | `user_data/convergence_logs/ChaikinMoneyFlowStrategy-ladder.log` |
| `Chandem` | `spot_long` | 2016 candles | 0.0% on `CMO` | 2026-09-01 15:40:37 | `user_data/convergence_logs/Chandem-ladder.log` |
| `Chandemtwo` | `spot_long` | 2016 candles | 0.0% on `CMO` | 2026-09-01 15:41:25 | `user_data/convergence_logs/Chandemtwo-ladder.log` |
| `Cluc4` | `spot_long` | 1440 candles | 0.0% on `lower` | 2026-09-01 15:42:17 | `user_data/convergence_logs/Cluc4-ladder.log` |
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
| `CombinedBinHAndClucHyperV0` | `spot_long` | 1440 candles | 0.0% on `lower_21` | 2026-09-01 15:43:08 | `user_data/convergence_logs/CombinedBinHAndClucHyperV0-ladder.log` |
| `CombinedBinHAndClucHyperV3` | `spot_long` | 1440 candles | 0.0% on `lower_21` | 2026-09-01 15:43:59 | `user_data/convergence_logs/CombinedBinHAndClucHyperV3-ladder.log` |
| `CombinedBinHAndClucV2` | `spot_long` | 576 candles | 0.0% on `ssl_down` | 2026-09-01 13:15:19 | `user_data/convergence_logs/CombinedBinHAndClucV2-ladder.log` |
| `CombinedBinHAndClucV4` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 13:15:44 | `user_data/convergence_logs/CombinedBinHAndClucV4-ladder.log` |
| `CombinedBinHAndClucV5` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 13:16:09 | `user_data/convergence_logs/CombinedBinHAndClucV5-ladder.log` |
| `CombinedBinHAndClucV5Hyperoptable` | `spot_long` | 288 candles | 0.0% on `lower` | 2026-09-01 12:21:09 | `user_data/convergence_logs/CombinedBinHAndClucV5Hyperoptable-ladder.log` |
| `CombinedBinHAndClucV8` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 13:16:34 | `user_data/convergence_logs/CombinedBinHAndClucV8-ladder.log` |
| `CombinedBinHAndClucV8Hyper` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 13:16:59 | `user_data/convergence_logs/CombinedBinHAndClucV8Hyper-ladder.log` |
| `CombinedBinHAndClucV8XH` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 13:17:23 | `user_data/convergence_logs/CombinedBinHAndClucV8XH-ladder.log` |
| `CombinedBinHAndClucV8XHO` | `spot_long` | 2016 candles | 0.0% on `ema_50_1h` | 2026-09-01 12:21:34 | `user_data/convergence_logs/CombinedBinHAndClucV8XHO-ladder.log` |
| `Combined_Indicators` | `spot_long` | 1440 candles | 0.0% on `lower` | 2026-09-01 15:44:51 | `user_data/convergence_logs/Combined_Indicators-ladder.log` |
| `Combined_NFIv6_SMA` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 13:17:48 | `user_data/convergence_logs/Combined_NFIv6_SMA-ladder.log` |
| `Combined_NFIv7_SMA` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:00 | `user_data/convergence_logs/Combined_NFIv7_SMA-ladder.log` |
| `Combined_NFIv7_SMA_Rallipanos_20210707` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:25 | `user_data/convergence_logs/Combined_NFIv7_SMA_Rallipanos_20210707-ladder.log` |
| `Combined_NFIv7_SMA_bAdBoY_20211204` | `spot_long` | 2016 candles | 0.0% on `ema_fast_1h` | 2026-09-01 12:22:51 | `user_data/convergence_logs/Combined_NFIv7_SMA_bAdBoY_20211204-ladder.log` |
| `CompositeScoreStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:23:15 | `user_data/convergence_logs/CompositeScoreStrategy-ladder.log` |
| `CoppockCurveStrategy` | `spot_long` | 288 candles | 0.0% on `coppock` | 2026-09-01 12:23:39 | `user_data/convergence_logs/CoppockCurveStrategy-ladder.log` |
| `CrossEMAStrategy` | `spot_long` | 168 candles | 0.0% on `stoch_rsi` | 2026-09-01 13:18:36 | `user_data/convergence_logs/CrossEMAStrategy-ladder.log` |
| `CustomStoplossWithPSAR` | `spot_long` | 24 candles | 0.0% on `None` | 2026-09-01 13:50:31 | `user_data/convergence_logs/CustomStoplossWithPSAR-ladder.log` |
| `DCBBBounce` | `spot_long` | 576 candles | 0.0% on `bb_upperband` | 2026-09-01 13:19:24 | `user_data/convergence_logs/DCBBBounce-ladder.log` |
| `DD` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 15:45:44 | `user_data/convergence_logs/DD-ladder.log` |
| `DemaCrossStrategy` | `spot_long` | 288 candles | 0.0% on `dema20` | 2026-09-01 12:24:04 | `user_data/convergence_logs/DemaCrossStrategy-ladder.log` |
| `DevilStra` | `spot_long` | 6 candles | 0.0% on `None` | 2026-09-01 13:51:19 | `user_data/convergence_logs/DevilStra-ladder.log` |
| `Diamond` | `spot_long` | 288 candles | 0.0% on `None` | 2026-09-01 15:46:33 | `user_data/convergence_logs/Diamond-ladder.log` |
| `Dimond` | `spot_long` | 288 candles | 0.0% on `None` | 2026-09-01 13:52:07 | `user_data/convergence_logs/Dimond-ladder.log` |
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
| `EMA520015_V17` | `spot_long` | 540 candles | 0.028% on `ema350` | 2026-09-01 15:47:21 | `user_data/convergence_logs/EMA520015_V17-ladder.log` |
| `EMABreakout` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 13:24:46 | `user_data/convergence_logs/EMABreakout-ladder.log` |
| `EMASkipPump` | `spot_long` | 288 candles | 0.0% on `ema_21` | 2026-09-01 13:53:49 | `user_data/convergence_logs/EMASkipPump-ladder.log` |
| `EasyInEasyOut` | `spot_long` | 1440 candles | 0.0% on `None` | 2026-09-01 15:48:12 | `user_data/convergence_logs/EasyInEasyOut-ladder.log` |
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
| `FVGChannel` | `spot_long` | 2160 candles | 0.0% on `ha_open` | 2026-09-01 15:49:04 | `user_data/convergence_logs/FVGChannel-ladder.log` |
| `FisherHull` | `spot_long` | 1440 candles | 0.0% on `cci` | 2026-09-01 13:54:39 | `user_data/convergence_logs/FisherHull-ladder.log` |
| `FisherTransformStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:25:45 | `user_data/convergence_logs/FisherTransformStrategy-ladder.log` |
| `FiveMinCrossAbove` | `spot_long` | 288 candles | 0.0% on `None` | 2026-09-01 13:55:28 | `user_data/convergence_logs/FiveMinCrossAbove-ladder.log` |
| `FrayStratBTC` | `spot_long` | 672 candles | 0.0% on `adx` | 2026-09-01 13:55:52 | `user_data/convergence_logs/FrayStratBTC-ladder.log` |
| `Freqtrade_backtest_validation_freqtrade1` | `spot_long` | 48 candles | 0.0% on `fastMA` | 2026-09-01 15:50:45 | `user_data/convergence_logs/Freqtrade_backtest_validation_freqtrade1-ladder.log` |
| `FrostAuraM115mStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 13:56:17 | `user_data/convergence_logs/FrostAuraM115mStrategy-ladder.log` |
| `FrostAuraM11hStrategy` | `spot_long` | 168 candles | 0.0% on `rsi` | 2026-09-01 13:56:41 | `user_data/convergence_logs/FrostAuraM11hStrategy-ladder.log` |
| `FrostAuraM21hStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 13:57:05 | `user_data/convergence_logs/FrostAuraM21hStrategy-ladder.log` |
| `FrostAuraM315mStrategy` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 13:57:30 | `user_data/convergence_logs/FrostAuraM315mStrategy-ladder.log` |
| `FrostAuraM31hStrategy` | `spot_long` | 168 candles | 0.0% on `rsi` | 2026-09-01 13:57:55 | `user_data/convergence_logs/FrostAuraM31hStrategy-ladder.log` |
| `GKD_Baseline` | `spot_long` | 168 candles | 0.0% on `baseline` | 2026-09-01 15:51:35 | `user_data/convergence_logs/GKD_Baseline-ladder.log` |
| `GKD_BaselineAllMAs` | `spot_long` | 168 candles | 0.0% on `baseline` | 2026-09-01 15:52:23 | `user_data/convergence_logs/GKD_BaselineAllMAs-ladder.log` |
| `GKD_C` | `spot_long` | 2160 candles | 0.633% on `baseline` | 2026-09-01 13:58:45 | `user_data/convergence_logs/GKD_C-ladder.log` |
| `GKD_FisherTransform` | `spot_long` | 168 candles | 0.0% on `fisher_smooth_6h` | 2026-09-01 14:00:27 | `user_data/convergence_logs/GKD_FisherTransform-ladder.log` |
| `GKD_FisherTransformMTF` | `spot_long` | 168 candles | 0.0% on `fisher_smooth_4h` | 2026-09-01 14:01:15 | `user_data/convergence_logs/GKD_FisherTransformMTF-ladder.log` |
| `GKD_HurstExponent` | `spot_long` | 168 candles | 0.0% on `hurst` | 2026-09-01 15:53:13 | `user_data/convergence_logs/GKD_HurstExponent-ladder.log` |
| `GKD_PFE` | `spot_long` | 168 candles | 0.0% on `pfe_smooth` | 2026-09-01 15:54:03 | `user_data/convergence_logs/GKD_PFE-ladder.log` |
| `GPTREV` | `spot_long` | 1440 candles | 0.0% on `rsi_15m` | 2026-09-01 14:01:43 | `user_data/convergence_logs/GPTREV-ladder.log` |
| `GodCard` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 15:54:53 | `user_data/convergence_logs/GodCard-ladder.log` |
| `GodStraNew` | `spot_long` | 6 candles | 0.0% on `None` | 2026-09-01 14:02:30 | `user_data/convergence_logs/GodStraNew-ladder.log` |
| `GodStraNew40` | `spot_long` | 6 candles | 0.0% on `None` | 2026-09-01 14:03:17 | `user_data/convergence_logs/GodStraNew40-ladder.log` |
| `GodStraNew_SMAonly` | `spot_long` | 288 candles | 0.0% on `None` | 2026-09-01 14:04:05 | `user_data/convergence_logs/GodStraNew_SMAonly-ladder.log` |
| `GoldenCrossStrategy` | `spot_long` | 2016 candles | 0.0% on `ema50` | 2026-09-01 12:26:10 | `user_data/convergence_logs/GoldenCrossStrategy-ladder.log` |
| `Hacklemore2` | `spot_long` | 192 candles | 0.0% on `volume_mean_slow` | 2026-09-01 14:06:05 | `user_data/convergence_logs/Hacklemore2-ladder.log` |
| `Hacklemore3` | `spot_long` | 288 candles | 0.0% on `volume_mean_slow` | 2026-09-01 14:06:53 | `user_data/convergence_logs/Hacklemore3-ladder.log` |
| `Hacklemost` | `spot_long` | 288 candles | 0.0% on `ema_slow` | 2026-09-01 14:07:44 | `user_data/convergence_logs/Hacklemost-ladder.log` |
| `HansenSmaOffsetV1` | `spot_long` | 96 candles | 0.0% on `emac` | 2026-09-01 14:08:31 | `user_data/convergence_logs/HansenSmaOffsetV1-ladder.log` |
| `HeikinAshiStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:26:36 | `user_data/convergence_logs/HeikinAshiStrategy-ladder.log` |
| `HigherHighStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:27:00 | `user_data/convergence_logs/HigherHighStrategy-ladder.log` |
| `HilbertSineWave` | `spot_long` | 336 candles | 0.0% on `cycle` | 2026-09-01 15:56:37 | `user_data/convergence_logs/HilbertSineWave-ladder.log` |
| `HourBasedStrategy` | `spot_long` | 24 candles | 0.0% on `None` | 2026-09-01 14:09:19 | `user_data/convergence_logs/HourBasedStrategy-ladder.log` |
| `INSIDEUP` | `spot_long` | 90 candles | 0.0% on `rsi_14` | 2026-09-01 14:14:51 | `user_data/convergence_logs/INSIDEUP-ladder.log` |
| `Ichess` | `spot_long` | 90 candles | 0.0% on `Ichimoku_Score` | 2026-09-01 14:15:39 | `user_data/convergence_logs/Ichess-ladder.log` |
| `Ichimoku` | `spot_long` | 288 candles | 0.0% on `None` | 2026-09-01 14:16:28 | `user_data/convergence_logs/Ichimoku-ladder.log` |
| `IchimokuSimpleStrategy` | `spot_long` | 288 candles | 0.0% on `senkou_b` | 2026-09-01 12:27:25 | `user_data/convergence_logs/IchimokuSimpleStrategy-ladder.log` |
| `ImpulseV1` | `spot_long` | 288 candles | 0.0% on `200_SMA` | 2026-09-01 12:27:51 | `user_data/convergence_logs/ImpulseV1-ladder.log` |
| `InformativeSample` | `spot_long` | 576 candles | 0.0% on `ema20` | 2026-09-01 14:17:18 | `user_data/convergence_logs/InformativeSample-ladder.log` |
| `Inverse` | `spot_long` | 720 candles | 0.007% on `ema_200_4h` | 2026-09-01 12:28:16 | `user_data/convergence_logs/Inverse-ladder.log` |
| `InverseV2` | `spot_long` | 720 candles | 0.007% on `ema_200_4h` | 2026-09-01 12:28:42 | `user_data/convergence_logs/InverseV2-ladder.log` |
| `JuicyTrend` | `spot_long` | 1344 candles | 0.0% on `ma1` | 2026-09-01 15:57:25 | `user_data/convergence_logs/JuicyTrend-ladder.log` |
| `KAMACCIRSI_new` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:29:09 | `user_data/convergence_logs/KAMACCIRSI_new-ladder.log` |
| `KC_BB` | `spot_long` | 288 candles | 0.0% on `sma_20` | 2026-09-01 15:58:17 | `user_data/convergence_logs/KC_BB-ladder.log` |
| `KeltnerChannelStrategy` | `spot_long` | 288 candles | 0.0% on `ema20` | 2026-09-01 12:29:34 | `user_data/convergence_logs/KeltnerChannelStrategy-ladder.log` |
| `Lateralus` | `spot_long` | 288 candles | 0.0% on `macd_1h` | 2026-09-01 14:18:09 | `user_data/convergence_logs/Lateralus-ladder.log` |
| `LinearRegressionStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:29:59 | `user_data/convergence_logs/LinearRegressionStrategy-ladder.log` |
| `Low_BB` | `spot_long` | 1440 candles | 0.0% on `bb_lowerband` | 2026-09-01 14:19:00 | `user_data/convergence_logs/Low_BB-ladder.log` |
| `LuxOSC` | `spot_long` | 576 candles | 0.0% on `osc` | 2026-09-01 14:19:26 | `user_data/convergence_logs/LuxOSC-ladder.log` |
| `MAC` | `spot_long` | 90 candles | 0.858% on `macdhist` | 2026-09-01 14:19:51 | `user_data/convergence_logs/MAC-ladder.log` |
| `MACDStrategy` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:22:14 | `user_data/convergence_logs/MACDStrategy-ladder.log` |
| `MACDStrategyADA` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 15:59:06 | `user_data/convergence_logs/MACDStrategyADA-ladder.log` |
| `MACDStrategyAVAX` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 15:59:57 | `user_data/convergence_logs/MACDStrategyAVAX-ladder.log` |
| `MACDStrategyBTC` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:00:47 | `user_data/convergence_logs/MACDStrategyBTC-ladder.log` |
| `MACDStrategyENJ` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:01:36 | `user_data/convergence_logs/MACDStrategyENJ-ladder.log` |
| `MACDStrategyETC` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:02:24 | `user_data/convergence_logs/MACDStrategyETC-ladder.log` |
| `MACDStrategySOL` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:03:11 | `user_data/convergence_logs/MACDStrategySOL-ladder.log` |
| `MACDStrategyXRP` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:04:01 | `user_data/convergence_logs/MACDStrategyXRP-ladder.log` |
| `MACDStrategy_crossed` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:23:01 | `user_data/convergence_logs/MACDStrategy_crossed-ladder.log` |
| `MACDZeroCrossStrategy` | `spot_long` | 90 candles | 0.0% on `macd` | 2026-09-01 14:23:48 | `user_data/convergence_logs/MACDZeroCrossStrategy-ladder.log` |
| `MACD_EMA` | `spot_long` | 2016 candles | 0.0% on `macd` | 2026-09-01 14:24:36 | `user_data/convergence_logs/MACD_EMA-ladder.log` |
| `MACD_TRI_EMA` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:25:25 | `user_data/convergence_logs/MACD_TRI_EMA-ladder.log` |
| `MFI` | `spot_long` | 288 candles | 0.0% on `MFI` | 2026-09-01 14:26:13 | `user_data/convergence_logs/MFI-ladder.log` |
| `MacdAdxStrategy` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 12:30:24 | `user_data/convergence_logs/MacdAdxStrategy-ladder.log` |
| `MacdZeroCrossStrategy` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:23:48 | `user_data/convergence_logs/MacdZeroCrossStrategy-ladder.log` |
| `Maro4hMacdSd` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:06:29 | `user_data/convergence_logs/Maro4hMacdSd-ladder.log` |
| `Martin` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 14:26:38 | `user_data/convergence_logs/Martin-ladder.log` |
| `MiniLambo` | `spot_long` | 2880 candles | 0.0% on `ema_14` | 2026-09-01 14:27:06 | `user_data/convergence_logs/MiniLambo-ladder.log` |
| `Minmax` | `spot_long` | 24 candles | 0.0% on `None` | 2026-09-01 14:27:56 | `user_data/convergence_logs/Minmax-ladder.log` |
| `MomStrategy` | `spot_long` | 336 candles | 0.0% on `adx` | 2026-09-01 16:07:18 | `user_data/convergence_logs/MomStrategy-ladder.log` |
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
| `ONUR` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 16:08:06 | `user_data/convergence_logs/ONUR-ladder.log` |
| `OmaGann` | `spot_long` | 168 candles | 0.0% on `high_ma` | 2026-09-01 16:08:55 | `user_data/convergence_logs/OmaGann-ladder.log` |
| `PRICEFOLLOWING` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 14:48:31 | `user_data/convergence_logs/PRICEFOLLOWING-ladder.log` |
| `PRICEFOLLOWING2` | `spot_long` | 672 candles | 0.0% on `adx` | 2026-09-01 14:48:59 | `user_data/convergence_logs/PRICEFOLLOWING2-ladder.log` |
| `PRICEFOLLOWINGX` | `spot_long` | 672 candles | 0.0% on `adx` | 2026-09-01 14:49:28 | `user_data/convergence_logs/PRICEFOLLOWINGX-ladder.log` |
| `ParabolicSarStrategy` | `spot_long` | 288 candles | 0.0% on `ema50` | 2026-09-01 12:39:54 | `user_data/convergence_logs/ParabolicSarStrategy-ladder.log` |
| `PatternRecognition` | `spot_long` | 1 candles | 0.0% on `None` | 2026-09-01 14:50:17 | `user_data/convergence_logs/PatternRecognition-ladder.log` |
| `PolymarketPortfolio` | `spot_long` | 180 candles | 0.0% on `prob_ema_fast` | 2026-09-01 21:30:47 | `user_data/convergence_logs/PolymarketPortfolio-ladder.log` |
| `PpoMomentumStrategy` | `spot_long` | 288 candles | 0.0% on `ppo` | 2026-09-01 12:40:19 | `user_data/convergence_logs/PpoMomentumStrategy-ladder.log` |
| `PriceActionCandleStrategy` | `spot_long` | 288 candles | 0.0% on `ema50` | 2026-09-01 12:40:43 | `user_data/convergence_logs/PriceActionCandleStrategy-ladder.log` |
| `PriceChannelStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:41:07 | `user_data/convergence_logs/PriceChannelStrategy-ladder.log` |
| `PumpDetector` | `spot_long` | 2016 candles | 0.0% on `var2_test` | 2026-09-01 12:41:32 | `user_data/convergence_logs/PumpDetector-ladder.log` |
| `Quickie` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 14:51:56 | `user_data/convergence_logs/Quickie-ladder.log` |
| `RSI` | `spot_long` | 192 candles | 0.0% on `rsi_30m` | 2026-09-01 16:09:44 | `user_data/convergence_logs/RSI-ladder.log` |
| `RSI_BB` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 16:10:33 | `user_data/convergence_logs/RSI_BB-ladder.log` |
| `RSI_EMA_strategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 16:11:22 | `user_data/convergence_logs/RSI_EMA_strategy-ladder.log` |
| `RSIv2` | `spot_long` | 192 candles | 0.0% on `rsi_30m` | 2026-09-01 12:41:55 | `user_data/convergence_logs/RSIv2-ladder.log` |
| `RalliV1` | `spot_long` | 2016 candles | 0.0% on `ma_buy_14` | 2026-09-01 14:52:21 | `user_data/convergence_logs/RalliV1-ladder.log` |
| `RalliV1_disable56` | `spot_long` | 2016 candles | 0.0% on `ma_buy_14` | 2026-09-01 14:52:46 | `user_data/convergence_logs/RalliV1_disable56-ladder.log` |
| `ReinforcedAverageStrategy` | `spot_long` | 84 candles | 0.0% on `maShort` | 2026-09-01 14:53:35 | `user_data/convergence_logs/ReinforcedAverageStrategy-ladder.log` |
| `ReinforcedSmoothScalp` | `spot_long` | 2880 candles | 0.0% on `resample_75_date` | 2026-09-01 16:12:10 | `user_data/convergence_logs/ReinforcedSmoothScalp-ladder.log` |
| `RocMomentumStrategy` | `spot_long` | 576 candles | 0.0% on `rsi` | 2026-09-01 12:42:20 | `user_data/convergence_logs/RocMomentumStrategy-ladder.log` |
| `Roth01` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:13:01 | `user_data/convergence_logs/Roth01-ladder.log` |
| `Roth03` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:13:52 | `user_data/convergence_logs/Roth03-ladder.log` |
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
| `Saturn5` | `spot_long` | 1344 candles | 0.0% on `s1_ema_md` | 2026-09-01 15:01:02 | `user_data/convergence_logs/Saturn5-ladder.log` |
| `Scalp` | `spot_long` | 1440 candles | 0.0% on `fastd` | 2026-09-01 15:01:53 | `user_data/convergence_logs/Scalp-ladder.log` |
| `Schism2MM` | `spot_long` | 288 candles | 0.0% on `mp` | 2026-09-01 15:02:19 | `user_data/convergence_logs/Schism2MM-ladder.log` |
| `Schism3` | `spot_long` | 288 candles | 0.0% on `mp` | 2026-09-01 15:02:45 | `user_data/convergence_logs/Schism3-ladder.log` |
| `Schism4` | `spot_long` | 288 candles | 0.0% on `mp` | 2026-09-01 15:03:10 | `user_data/convergence_logs/Schism4-ladder.log` |
| `Seb` | `spot_long` | 576 candles | 0.0% on `ema20` | 2026-09-01 15:04:02 | `user_data/convergence_logs/Seb-ladder.log` |
| `Simple` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 15:04:56 | `user_data/convergence_logs/Simple-ladder.log` |
| `SimpleHopt` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:14:42 | `user_data/convergence_logs/SimpleHopt-ladder.log` |
| `SlowPotato` | `spot_long` | 288 candles | 0.0% on `None` | 2026-09-01 16:15:31 | `user_data/convergence_logs/SlowPotato-ladder.log` |
| `SmaRsiStrategy` | `spot_long` | 90 candles | 0.041% on `rsi` | 2026-09-01 12:44:48 | `user_data/convergence_logs/SmaRsiStrategy-ladder.log` |
| `SmartMoneyStrategy` | `spot_long` | 1440 candles | 0.0% on `cmf` | 2026-09-01 16:16:19 | `user_data/convergence_logs/SmartMoneyStrategy-ladder.log` |
| `SmoothOperator` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 15:05:49 | `user_data/convergence_logs/SmoothOperator-ladder.log` |
| `SmoothScalp` | `spot_long` | 1440 candles | 0.0% on `fastd` | 2026-09-01 15:06:43 | `user_data/convergence_logs/SmoothScalp-ladder.log` |
| `SqueezeMomentumStrategy` | `spot_long` | 288 candles | 0.0% on `bb_upper` | 2026-09-01 12:45:12 | `user_data/convergence_logs/SqueezeMomentumStrategy-ladder.log` |
| `StarRise` | `spot_long` | 2016 candles | 0.0% on `r_480_1h` | 2026-09-01 15:07:11 | `user_data/convergence_logs/StarRise-ladder.log` |
| `StarRise_strat` | `spot_long` | 2016 candles | 0.0% on `r_480_1h` | 2026-09-01 15:07:38 | `user_data/convergence_logs/StarRise_strat-ladder.log` |
| `StochasticOversoldStrategy` | `spot_long` | 288 candles | 0.0% on `stoch_k` | 2026-09-01 12:45:36 | `user_data/convergence_logs/StochasticOversoldStrategy-ladder.log` |
| `StochasticRsiStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:46:00 | `user_data/convergence_logs/StochasticRsiStrategy-ladder.log` |
| `Strategy001` | `spot_long` | 576 candles | 0.0% on `ema20` | 2026-09-01 16:17:10 | `user_data/convergence_logs/Strategy001-ladder.log` |
| `Strategy001_custom_exit` | `spot_long` | 576 candles | 0.0% on `ema20` | 2026-09-01 16:18:03 | `user_data/convergence_logs/Strategy001_custom_exit-ladder.log` |
| `Strategy001_custom_sell` | `spot_long` | 576 candles | 0.0% on `ema20` | 2026-09-01 16:18:58 | `user_data/convergence_logs/Strategy001_custom_sell-ladder.log` |
| `Strategy002` | `spot_long` | 288 candles | 0.0% on `slowk` | 2026-09-01 16:19:49 | `user_data/convergence_logs/Strategy002-ladder.log` |
| `Strategy003` | `spot_long` | 576 candles | 0.0% on `mfi` | 2026-09-01 16:20:40 | `user_data/convergence_logs/Strategy003-ladder.log` |
| `Strategy004` | `spot_long` | 576 candles | 0.0% on `adx` | 2026-09-01 16:21:32 | `user_data/convergence_logs/Strategy004-ladder.log` |
| `Strategy005` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 16:22:21 | `user_data/convergence_logs/Strategy005-ladder.log` |
| `StrategyScalpingFast` | `spot_long` | 1440 candles | 0.0% on `ema_high` | 2026-09-01 12:46:27 | `user_data/convergence_logs/StrategyScalpingFast-ladder.log` |
| `StrategyScalpingFast2` | `spot_long` | 1440 candles | 0.0% on `resample_5_sma` | 2026-09-01 16:23:18 | `user_data/convergence_logs/StrategyScalpingFast2-ladder.log` |
| `StrategyTestV2` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 15:08:04 | `user_data/convergence_logs/StrategyTestV2-ladder.log` |
| `SuperTrend` | `spot_long` | 1440 candles | 0.0% on `tema` | 2026-09-01 15:09:01 | `user_data/convergence_logs/SuperTrend-ladder.log` |
| `TD` | `spot_long` | 12 candles | 0.0% on `ha_open` | 2026-09-01 15:11:03 | `user_data/convergence_logs/TD-ladder.log` |
| `TEMA` | `spot_long` | 1440 candles | 0.0% on `adx` | 2026-09-01 15:11:31 | `user_data/convergence_logs/TEMA-ladder.log` |
| `TRIWAVE` | `spot_long` | 672 candles | 0.0% on `rsi_med_2h` | 2026-09-01 12:46:51 | `user_data/convergence_logs/TRIWAVE-ladder.log` |
| `TWAPStrategy` | `futures_long_short` | 192 candles | 0.0% on `rsi` | 2026-09-01 15:11:56 | `user_data/convergence_logs/TWAPStrategy-ladder.log` |
| `TechnicalExampleStrategy` | `spot_long` | 288 candles | 0.0% on `cmf` | 2026-09-01 15:12:44 | `user_data/convergence_logs/TechnicalExampleStrategy-ladder.log` |
| `TemaMaster` | `spot_long` | 288 candles | 0.0% on `CMO` | 2026-09-01 16:24:07 | `user_data/convergence_logs/TemaMaster-ladder.log` |
| `TemaMaster3` | `spot_long` | 2880 candles | 0.0% on `CMO` | 2026-09-01 16:24:59 | `user_data/convergence_logs/TemaMaster3-ladder.log` |
| `TemaPure` | `spot_long` | 2016 candles | 0.0% on `CMO` | 2026-09-01 16:25:50 | `user_data/convergence_logs/TemaPure-ladder.log` |
| `TemaPureNeat` | `spot_long` | 288 candles | 0.0% on `CMO` | 2026-09-01 16:26:40 | `user_data/convergence_logs/TemaPureNeat-ladder.log` |
| `TemaPureTwo` | `spot_long` | 2016 candles | 0.0% on `CMO` | 2026-09-01 16:27:31 | `user_data/convergence_logs/TemaPureTwo-ladder.log` |
| `TemaStrategy` | `spot_long` | 288 candles | 0.0% on `tema20` | 2026-09-01 12:47:16 | `user_data/convergence_logs/TemaStrategy-ladder.log` |
| `TheForce` | `spot_long` | 672 candles | 0.0% on `fastd` | 2026-09-01 15:13:10 | `user_data/convergence_logs/TheForce-ladder.log` |
| `ToTheMoon` | `futures_long_short` | 24 candles | 0.0% on `None` | 2026-09-01 15:13:58 | `user_data/convergence_logs/ToTheMoon-ladder.log` |
| `TouchEmaDelayStrategy` | `spot_long` | 480 candles | 0.0% on `ema_long_50` | 2026-09-01 16:28:24 | `user_data/convergence_logs/TouchEmaDelayStrategy-ladder.log` |
| `TouchEmaStrategy` | `spot_long` | 288 candles | 0.0% on `ema_long_60` | 2026-09-01 16:29:16 | `user_data/convergence_logs/TouchEmaStrategy-ladder.log` |
| `TrendAtrStrategy` | `spot_long` | 540 candles | 0.0% on `ema_fast` | 2026-09-01 12:47:40 | `user_data/convergence_logs/TrendAtrStrategy-ladder.log` |
| `Trend_Strength_Directional` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 16:30:06 | `user_data/convergence_logs/Trend_Strength_Directional-ladder.log` |
| `TripleEmaStrategy` | `spot_long` | 288 candles | 0.0% on `ema8` | 2026-09-01 12:48:03 | `user_data/convergence_logs/TripleEmaStrategy-ladder.log` |
| `TrixSignalStrategy` | `spot_long` | 288 candles | 0.0% on `trix` | 2026-09-01 12:48:28 | `user_data/convergence_logs/TrixSignalStrategy-ladder.log` |
| `TrixV21Strategy` | `spot_long` | 2160 candles | 0.0% on `stoch_rsi` | 2026-09-01 15:15:37 | `user_data/convergence_logs/TrixV21Strategy-ladder.log` |
| `TrixV23Strategy` | `spot_long` | 2160 candles | 0.0% on `btc_usdt_ema_184_1h` | 2026-09-01 15:16:03 | `user_data/convergence_logs/TrixV23Strategy-ladder.log` |
| `TwoCandle` | `spot_long` | 168 candles | 0.0% on `ha_open` | 2026-09-01 16:30:56 | `user_data/convergence_logs/TwoCandle-ladder.log` |
| `UniversalMACD` | `spot_long` | 288 candles | 0.0% on `ma12` | 2026-09-01 12:48:53 | `user_data/convergence_logs/UniversalMACD-ladder.log` |
| `Uptrend` | `spot_long` | 2016 candles | 0.0% on `mama` | 2026-09-01 15:16:28 | `user_data/convergence_logs/Uptrend-ladder.log` |
| `VWAP` | `spot_long` | 2016 candles | 0.0% on `vwap_low` | 2026-09-01 15:17:16 | `user_data/convergence_logs/VWAP-ladder.log` |
| `VolatilitySystem` | `futures_long` | 336 candles | 0.016% on `resample_180_atr` | 2026-09-01 15:18:07 | `user_data/convergence_logs/VolatilitySystem-ladder.log` |
| `VolatilitySystemV2` | `futures_long_short` | 336 candles | 0.016% on `resample_180_atr` | 2026-09-01 15:18:57 | `user_data/convergence_logs/VolatilitySystemV2-ladder.log` |
| `VolumeBreakoutStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:49:17 | `user_data/convergence_logs/VolumeBreakoutStrategy-ladder.log` |
| `VortexStrategy` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 12:49:42 | `user_data/convergence_logs/VortexStrategy-ladder.log` |
| `VwapReversionStrategy` | `spot_long` | 576 candles | 0.0% on `vwap` | 2026-09-01 12:50:07 | `user_data/convergence_logs/VwapReversionStrategy-ladder.log` |
| `WaveTrendStra` | `spot_long` | 180 candles | 0.0% on `wt1` | 2026-09-01 15:19:48 | `user_data/convergence_logs/WaveTrendStra-ladder.log` |
| `WilliamsRStrategy` | `spot_long` | 2016 candles | 0.0% on `ema50` | 2026-09-01 12:50:33 | `user_data/convergence_logs/WilliamsRStrategy-ladder.log` |
| `YOLO` | `spot_long` | 1440 candles | 0.0% on `adx` | 2026-09-01 15:20:39 | `user_data/convergence_logs/YOLO-ladder.log` |
| `ZScoreMeanReversionStrategy` | `spot_long` | 540 candles | 0.038% on `ema_trend` | 2026-09-01 15:21:04 | `user_data/convergence_logs/ZScoreMeanReversionStrategy-ladder.log` |
| `adaptive` | `spot_long` | 2016 candles | 0.0% on `mama` | 2026-09-01 15:23:35 | `user_data/convergence_logs/adaptive-ladder.log` |
| `adxbbrsi2` | `spot_long` | 336 candles | 0.0% on `adx` | 2026-09-01 12:50:58 | `user_data/convergence_logs/adxbbrsi2-ladder.log` |
| `bbandrsi` | `spot_long` | 192 candles | 0.0% on `rsi` | 2026-09-01 16:31:44 | `user_data/convergence_logs/bbandrsi-ladder.log` |
| `bbrsi` | `spot_long` | 180 candles | 0.0% on `rsi` | 2026-09-01 12:51:22 | `user_data/convergence_logs/bbrsi-ladder.log` |
| `bbrsi4Freq` | `spot_long` | 168 candles | 0.0% on `rsi` | 2026-09-01 12:51:45 | `user_data/convergence_logs/bbrsi4Freq-ladder.log` |
| `conny` | `spot_long` | 96 candles | 0.0% on `consensus_sell` | 2026-09-01 12:52:10 | `user_data/convergence_logs/conny-ladder.log` |
| `cryptotankV2` | `spot_long` | 576 candles | 0.0% on `pivot` | 2026-09-01 12:52:35 | `user_data/convergence_logs/cryptotankV2-ladder.log` |
| `custom` | `spot_long` | 2016 candles | 0.0% on `osc` | 2026-09-01 15:24:00 | `user_data/convergence_logs/custom-ladder.log` |
| `dualwave` | `spot_long` | 672 candles | 0.0% on `rsi_2h` | 2026-09-01 15:24:26 | `user_data/convergence_logs/dualwave-ladder.log` |
| `e6v34` | `spot_long` | 672 candles | 0.0% on `hma15` | 2026-09-01 16:32:32 | `user_data/convergence_logs/e6v34-ladder.log` |
| `eltoro` | `spot_long` | 1344 candles | 0.0% on `BTC_EWO_Fast_1h` | 2026-09-01 12:53:00 | `user_data/convergence_logs/eltoro-ladder.log` |
| `eltoro1_4` | `spot_long` | 2160 candles | 0.0% on `INFEWO_4h` | 2026-09-01 12:53:24 | `user_data/convergence_logs/eltoro1_4-ladder.log` |
| `eltoro1_4_simple` | `spot_long` | 672 candles | 0.0% on `INFEWO_4h` | 2026-09-01 12:53:49 | `user_data/convergence_logs/eltoro1_4_simple-ladder.log` |
| `ema` | `spot_long` | 2016 candles | 0.0% on `ema11` | 2026-09-01 16:33:20 | `user_data/convergence_logs/ema-ladder.log` |
| `gettinMoist` | `spot_long` | 288 candles | 0.0% on `macd` | 2026-09-01 12:54:38 | `user_data/convergence_logs/gettinMoist-ladder.log` |
| `hansencandlepatternV1` | `spot_long` | 24 candles | 0.0% on `emac` | 2026-09-01 15:25:15 | `user_data/convergence_logs/hansencandlepatternV1-ladder.log` |
| `heikin` | `spot_long` | 24 candles | 0.0% on `emac` | 2026-09-01 15:26:03 | `user_data/convergence_logs/heikin-ladder.log` |
| `hlhb` | `spot_long` | 540 candles | 0.0% on `rsi` | 2026-09-01 12:55:01 | `user_data/convergence_logs/hlhb-ladder.log` |
| `keltnerchannel` | `spot_long` | 360 candles | 0.0% on `kc_upperband` | 2026-09-01 15:26:51 | `user_data/convergence_logs/keltnerchannel-ladder.log` |
| `moonhouse` | `spot_long` | 1 candles | 0.0% on `None` | 2026-09-01 15:28:29 | `user_data/convergence_logs/moonhouse-ladder.log` |
| `slope_is_dopeCT` | `spot_long` | 672 candles | 0.0% on `rsi` | 2026-09-01 12:55:49 | `user_data/convergence_logs/slope_is_dopeCT-ladder.log` |
| `stoploss` | `spot_long` | 288 candles | 0.0% on `adx` | 2026-09-01 12:56:13 | `user_data/convergence_logs/stoploss-ladder.log` |
| `stratfib` | `spot_long` | 720 candles | 0.0% on `dema3` | 2026-09-01 15:29:19 | `user_data/convergence_logs/stratfib-ladder.log` |
| `strato` | `spot_long` | 1440 candles | 0.0% on `rsi` | 2026-09-01 12:56:41 | `user_data/convergence_logs/strato-ladder.log` |
| `tbtest` | `spot_long` | 288 candles | 0.0% on `rsi` | 2026-09-01 15:30:07 | `user_data/convergence_logs/tbtest-ladder.log` |
| `thetank3` | `spot_long` | 672 candles | 0.0% on `ema_125` | 2026-09-01 12:57:28 | `user_data/convergence_logs/thetank3-ladder.log` |
| `thetank4TV` | `spot_long` | 672 candles | 0.0% on `ema_125` | 2026-09-01 12:57:53 | `user_data/convergence_logs/thetank4TV-ladder.log` |
| `true_lambo` | `spot_long` | 2016 candles | 0.0% on `bb_lowerband2` | 2026-09-01 15:30:39 | `user_data/convergence_logs/true_lambo-ladder.log` |
| `twinturboV8` | `spot_long` | 2016 candles | 0.0% on `BTC_EWO_Fast_1h` | 2026-09-01 15:31:06 | `user_data/convergence_logs/twinturboV8-ladder.log` |
| `twinturboV8_2` | `spot_long` | 2016 candles | 0.0% on `BTC_EWO_Fast_1h` | 2026-09-01 15:31:32 | `user_data/convergence_logs/twinturboV8_2-ladder.log` |
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

## Exclusion unconfirmed - 168 strategies

`excluded` is a verdict, and this audit does not issue one on
somebody else's measurement or on the absence of one. These rows
would have been excluded on exactly that, so they are held here
until a measurement of ours settles them either way. Nothing about
them is hidden by the change of name: the decisive reason and the
basis stay on the row, and the work that would settle it is in
`open_work`.

| Held on | Basis | Strategies |
|---|---|---:|
| `no_verdict_on_lookahead_and_recursive` | `no_finding` | 57 |
| `recursive_bias_unverified` | `no_finding` | 43 |
| `lookahead_found` | `inherited` | 38 |
| `no_verdict_on_lookahead` | `no_finding` | 15 |
| `no_verdict_on_recursive` | `no_finding` | 10 |
| `no_trades_in_full_measurement` | `inherited` | 5 |

This is not a softening. A row here may well end up excluded - the
38 held on an inherited look-ahead finding probably will, because a
limited environment does not invent bias. It ends up there on our
own evidence or not at all.

## Not passing - 209 strategies, by decisive reason

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
| `own_measurement` | a disqualifying result measured here, from this implementation | 110 |
| `blocked` | the strategy did not run, so nothing about it was judged | 99 |

Only `own_measurement` is a closed case. The other three carry the
work that would settle them in `open_work`, and the selftest fails if
one of them carries none.

| Reason | Meaning | Strategies |
|---|---|---:|
| `lookahead_found` | reads data it could not have had at the time | 31 |
| `technical_trap_found` | carries a published backtesting trap | 40 |
| `strategy_does_not_run` | fails before it can be measured; the message is in runtime_failure | 99 |
| `recursive_bias_found` | indicator value still drifts at every warm-up the ladder can reach | 28 |
| `no_trades_in_full_measurement` | never trades over the full window | 11 |


### Reason by wave

| Reason | `B_warmup_refusal` | `C_measurement_recovery` | `D_recursive_drift` | `not_scheduled` |
|---|---|---|---|---|
| `lookahead_found` | 0 | 15 | 0 | 16 |
| `technical_trap_found` | 0 | 0 | 0 | 40 |
| `strategy_does_not_run` | 0 | 99 | 0 | 0 |
| `recursive_bias_found` | 3 | 0 | 14 | 11 |
| `no_trades_in_full_measurement` | 0 | 10 | 0 | 1 |

### `lookahead_found` - 31

Reads data it could not have had at the time.

Wave `C_measurement_recovery` - 15:

`ARIMA_15`, `NfiNextModded`, `NostalgiaForInfinityNext`, `NostalgiaForInfinityNext772`
`NostalgiaForInfinityNextV7155`, `NostalgiaForInfinityNext_ChangeToTower_V5_2`, `NostalgiaForInfinityNext_ChangeToTower_V5_3`, `NostalgiaForInfinityNext_ChangeToTower_V6`
`NostalgiaForInfinityNext_maximizer`, `NostalgiaForInfinityV7_7_2`, `NostalgiaForInfinityXw`, `Obelisk_Ichimoku_Slow_v1_3`
`Obelisk_Ichimoku_ZEMA_v1`, `Stinkfist`, `ichiV1_Marius`

Wave `not_scheduled` - 16:

`BreakoutStrategy`, `FakeoutStrategy`, `Heracles`, `HyperStra_SMAOnly`
`IchiVwapAdx`, `MaxSharpePortfolio`, `MinimumVariancePortfolio`, `MomentumRegimeBasket`
`NOTankAi_17`, `NOTankAi_19`, `Precognition`, `RsiquiV2`
`RsiquiV5`, `TSPredict`, `Zeus`, `tsp0chicken`

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
| freqAI is not enabled. Please enable it in your config to use this strategy. | 5 | `RLStrategy`, `TankAi`, `TankAiRevival`, `WTAI`, `WTRSIAI` |
| cannot import name '__version__' from 'freqtrade' (unknown location) | 4 | `DualModelPolymarketPortfolio`, `EmaCrossStrategy`, `PolymarketMeanReversionStrategy`, `PolymarketMomentumStrategy` |
| Configuration error: 'stoploss' is a required property | 3 | `AdaptiveRenkoStrategy`, `ClucCrypROI`, `ClucCrypSlow` |
| `populate_exit_trend` or `populate_sell_trend` must be implemented. | 2 | `ClucHAnix_BB_RPB_TraNz`, `SimpleRiskFilterStrategy` |
| IStrategy.min_roi_reached_entry() missing 2 required positional arguments: 'trade_dur' and 'current_time' | 2 | `Dyna_opti`, `Solipsis4` |
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

### `recursive_bias_found` - 28

Indicator value still drifts at every warm-up the ladder can reach.

Wave `B_warmup_refusal` - 3:

`ForexRobootSuperScalper`, `HSI`, `Macd`

Wave `D_recursive_drift` - 14:

`BigZ0307HO`, `BigZ0407`, `BigZ0407HO`, `BigZ04HO`
`BigZ04HO2`, `BigZ06`, `BigZ07`, `ClucHAnix_BB_RPB_MOD2_ROI`
`ClucHAnix_BB_RPB_MOD_CTT`, `ClucHAnix_BB_RPB_MOD_E0V1E_ROI`, `ObvTrendStrategy`, `flawless_lambo`
`lambotest`, `tacos`

Wave `not_scheduled` - 11:

`BcmbigzV1`, `BeastBotXBLR6`, `BeastBotXBLR7`, `BigZ04`
`GoldHedgeZeroMACD`, `NOTankAi_15`, `NOTankAi_15_Cleaned`, `NOTankAi_15_Cleaned_v2`
`NotAnotherSMAOffSetStrategy_V2`, `TrendRiderStrategy`, `pcb20`

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
| `paired_full_window_equivalence` | 378 |
| `recursive_ladder_pending` | 145 |
| `lookahead_remeasure_pending` | 141 |
| `first_measurement_in_current_runtime` | 60 |
| `needs_a_look` | 59 |
| `lookahead_verdict` | 42 |
| `convergence_inconclusive` | 34 |
| `convergence_not_converged_within_ladder` | 28 |
| `refuse_repair` | 15 |
| `repair_attempted` | 13 |
| `to_be_fixed` | 8 |
| `full_window_measurement_pending` | 5 |
| `repair_withdrawn` | 4 |

Per-row detail, including every evidence path, is in
`STRATEGY_STATUS.csv`.
