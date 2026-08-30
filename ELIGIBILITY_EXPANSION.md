# Eligibility expansion inventory

**Frozen:** 2026-08-30, before Stage 9 ranking
**Protocol:** `ELIGIBILITY_EXPANSION_PLAN.md`

This inventory uses technical Stage 6 evidence only. No strategy-by-regime
performance or ranking output was read to select candidates.

## Frozen waves

| Wave | Rows |
|---|---:|
| `A_pending_diagnostics` | 7 |
| `B_warmup_refusal` | 82 |
| `C_measurement_recovery` | 230 |
| `D_recursive_drift` | 124 |
| `E0_strict67` | 67 |
| `not_scheduled` | 390 |

The four expansion waves contain **443** candidates. E0 contains **67** already eligible profiles; **390** rows are not scheduled by this equivalent-repair expansion.

Candidate member hash: `sha256_2374db291d23252c7d6208709e0702ccb37bd6659f66e29a85cccfaab110be04`.

## Wave C missingness

The 230 measurement-recovery rows are summarized without treating source
taxonomy as an eligibility rule. `<missing>` remains explicit.

### `run_profile`

| Value | Rows | Share |
|---|---:|---:|
| `spot_long` | 212 | 92.2% |
| `futures_long_short` | 14 | 6.1% |
| `futures_long` | 3 | 1.3% |
| `unknown` | 1 | 0.4% |

### `source_repo`

| Value | Rows | Share |
|---|---:|---:|
| `PeetCrypto/freqtrade-stuff` | 100 | 43.5% |
| `davidzr/freqtrade-strategies` | 30 | 13.0% |
| `TheoBrigitte/freqtrade` | 26 | 11.3% |
| `markdregan/FreqAI-Marcos-Lopez-De-Prado` | 23 | 10.0% |
| `jaredrsommer/freqtradestrategies` | 13 | 5.7% |
| `mlsys-io/PortfolioBench` | 9 | 3.9% |
| `ShahAnuj2610/my-freqtrade` | 4 | 1.7% |
| `nateemma/strategies` | 4 | 1.7% |
| `Foxel05/freqtrade-stuff` | 3 | 1.3% |
| `MelvynClark/Freqtrade-Strategy` | 3 | 1.3% |
| `DonaldSimpson/remora-freqtrade` | 2 | 0.9% |
| `werkkrew/freqtrade-strategies` | 2 | 0.9% |
| `DutchCryptoDad/FreqtradeBotStrategyDevelopmentForBeginners` | 1 | 0.4% |
| `HeyMrRobot/Freqtrade-Adaptive-Renko-Strategy` | 1 | 0.4% |
| `MMR-19/freqtrade-strategies` | 1 | 0.4% |
| `Mohamed-sm/Freqtrade-RLStrategy-IA` | 1 | 0.4% |
| `TomtomEh/freqtrade-websocket` | 1 | 0.4% |
| `botenesp/freqtrade_strategies` | 1 | 0.4% |
| `flaviosiotto/freqtrade-strategy` | 1 | 0.4% |
| `iterativv/NostalgiaForInfinity` | 1 | 0.4% |
| `jerome-benoit/freqai-strategies` | 1 | 0.4% |
| `keithorange/FreqTradeCustomOrders` | 1 | 0.4% |
| `obseries/freqtrade-strategy-ichiv1` | 1 | 0.4% |

### `execution_timeframe`

| Value | Rows | Share |
|---|---:|---:|
| `5m` | 108 | 47.0% |
| `<missing>` | 33 | 14.3% |
| `1h` | 26 | 11.3% |
| `15m` | 16 | 7.0% |
| `3m` | 13 | 5.7% |
| `4h` | 13 | 5.7% |
| `1m` | 8 | 3.5% |
| `30m` | 5 | 2.2% |
| `1d` | 4 | 1.7% |
| `12h` | 1 | 0.4% |
| `1w` | 1 | 0.4% |
| `2h` | 1 | 0.4% |
| `5h` | 1 | 0.4% |

### `artifact_role`

| Value | Rows | Share |
|---|---:|---:|
| `strategy` | 218 | 94.8% |
| `test_candidate` | 9 | 3.9% |
| `template_candidate` | 3 | 1.3% |

### `canonical_population`

| Value | Rows | Share |
|---|---:|---:|
| `original` | 181 | 78.7% |
| `repaired` | 49 | 21.3% |

### `repair_class`

| Value | Rows | Share |
|---|---:|---:|
| `<missing>` | 181 | 78.7% |
| `class2` | 49 | 21.3% |

### `equivalence_status`

| Value | Rows | Share |
|---|---:|---:|
| `not_applicable` | 181 | 78.7% |
| `strict_equivalent` | 49 | 21.3% |

### `runtime_smoke_status`

| Value | Rows | Share |
|---|---:|---:|
| `not_run` | 213 | 92.6% |
| `failed` | 17 | 7.4% |

### `classification_status`

| Value | Rows | Share |
|---|---:|---:|
| `provisional` | 207 | 90.0% |
| `review` | 23 | 10.0% |

### `taxonomy_logic`

| Value | Rows | Share |
|---|---:|---:|
| `trend_following` | 106 | 46.1% |
| `unclear` | 41 | 17.8% |
| `ml_freqai` | 30 | 13.0% |
| `momentum` | 17 | 7.4% |
| `volatility` | 16 | 7.0% |
| `mean_reversion` | 14 | 6.1% |
| `hybrid` | 5 | 2.2% |
| `breakout` | 1 | 0.4% |

### `taxonomy_complexity`

| Value | Rows | Share |
|---|---:|---:|
| `simple` | 118 | 51.3% |
| `complex` | 60 | 26.1% |
| `moderate` | 52 | 22.6% |

## Dependence-family status

No exact copy-family identifier is currently available in the technical
inputs. Repository and source taxonomy are retained for missingness cuts,
but are not silently treated as dependence families. A dedicated frozen
family manifest is required before Stage 9 inference.
