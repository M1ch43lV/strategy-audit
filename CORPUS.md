# The corpus: 1,050 unique strategies from 77 repositories

This is, as far as I can establish, **the largest deduplicated index of public
freqtrade strategies that exists** — and the claim is written so that you can
refute it. The search queries are published below. Run them, find a repository I
missed, and the number changes.

What is indexed here is **measurements**, not code. Each strategy gets a card
with its numbers, or with the named reason it could not be measured. The
strategies themselves stay in their authors' repositories under their authors'
licences.

## Scale

```
repositories indexed                        77
class occurrences (with duplicates)      2,868
UNIQUE STRATEGY CLASSES                  1,050
share that are copies                      63%

largest single repository   jaredrsommer/freqtradestrategies   558 classes
this corpus is larger by                                       1.9x
```

## Where the originals actually come from

Sorted by **first appearances**, not file count. The distinction is the whole
point: a repository can hold five hundred strategies and contribute none.

```
repository                                    classes   first seen   copies
PeetCrypto/freqtrade-stuff                        346          311     10%
davidzr/freqtrade-strategies                      461          166     64%
TheoBrigitte/freqtrade                            220          117     47%
mlsys-io/PortfolioBench                            67           66      1%
jaredrsommer/freqtradestrategies                  558           61     89%
hamidreza07/freqai-strategy                        94           55     41%
LazyPigPig/freqtrade-grid                          34           31      9%
Foxel05/freqtrade-stuff                            31           31      0%
MelvynClark/Freqtrade-Strategy                     22           22      0%
webclinic017/strategies-freqtrade-                 55           20     64%
...
keithorange/HUGE_FreqTrade_Strategy_Collection    477            0    100%
p-zombie/freqtrade                                 35            0    100%
```

**Nineteen of the 77 repositories contributed no original strategy at all.**
The most striking is a repository whose name announces a *huge collection*: 477
classes, every one of them already present elsewhere.

The small personal repositories are the original ones. `Foxel05` contributed 31
of 31, `MelvynClark` 21 of 21, `mikedigriz` 7 of 7. The large collections are
mostly re-postings of each other.

> **"First seen" means alphabetical scan order, not authorship.** Who copied
> from whom is not visible in the code, and this index does not claim to know.

## Every repository, by what it actually contains

The table above answers "how much." This section answers "of what" — read
from the actual strategy files, not inferred from file counts. Covers the 68
repositories from before the 2026-09-08 gap-driven harvest (see the next
section for those nine).

**The five largest are hoarded mirrors, not research collections.** Together
they hold more than half the corpus's raw file count, and the pattern in all
five is the same: flat or loosely-organized dumps of other people's famous
public strategies (NostalgiaForInfinity, ClucHAnix, BB_RPB_TSL, SMAOffset
variants), often with the original author's credit comment still in the file,
sometimes saved multiple times as `(1)`/`(2)` re-downloads. Each still holds a
handful of genuinely distinctive files:

- **`jaredrsommer/freqtradestrategies`** — 558 files (478 of them inside a
  subfolder literally named `HUGE_FreqTrade_Strategy_Collection`, i.e.
  `keithorange`'s repo copied wholesale into this one). Distinctive originals:
  `HurstCycle3` (FFT dominant-cycle detection with Future-Line-of-Demarcation
  convergence bands on Heikin-Ashi data), `FVGChannel` (a port of LuxAlgo's
  Fair Value Gap indicator with a Fibonacci-spaced channel),
  `LorentzianClassification` (k-NN over Lorentzian-distance RSI/WT/CCI/ADX
  features plus Nadaraya-Watson kernel regression), `WTAI` (FreqAI CatBoost
  hybrid), `AlexBattleTankKillerV3` (rolling Murrey Math levels).
- **`keithorange/HUGE_FreqTrade_Strategy_Collection`** — 477 files, flat, no
  subfolders, zero first-seen classes. A pure mirror: ~25 NostalgiaForInfinity
  variants, ~15 BB_RPB_TSL, ~13 BBRSI, ~9 ClucHAnix, plus generic MACD/ADX/VWAP
  templates. Nothing here originates in this repo.
- **`davidzr/freqtrade-strategies`** — 461 files, nearly all crediting a
  different outside author in their own docstring. Distinctive: `GodStraNew`
  (brute-force hyperopt gene-search over ~180 TA-Lib indicators),
  `PumpDetector` (a TradingView pump/whale-detection port), `LookaheadStrategy`
  (a shifted-EMA crossover, apparently a deliberate bias-illustration example),
  `RaposaDivergenceV1` (RSI divergence via `scipy` extrema, self-flagged in its
  own docstring as possibly look-ahead biased).
- **`PeetCrypto/freqtrade-stuff`** — 412 files, the single largest *original*
  contributor in the whole corpus (311 first-seen) despite the mirror
  character of most of it. Distinctive: `Persia`/`DevilStra` (brute-force
  "genetic" formula generators over random TA-Lib indicator pairs), `Ichess`
  (composite Ichimoku signal scoring), `Dracula` (hand-rolled support/
  resistance tracker), `Stinkfist` (RMI/momentum-pinball with adaptive exits).
- **`TheoBrigitte/freqtrade`** — folders named after upstream repos/authors,
  code still carrying others' attribution comments, dated `dry-run/` snapshot
  folders showing the owner live-testing downloaded strategies. Distinctive:
  `QuickAdapterV3` (a FreqAI sponsor-released ML feature-engineering strategy
  from robcaulk), `AdaptiveRenkoStrategy` (ATR-optimized Renko-brick trend
  detection), `FVGAdvancedStrategy_V2` (Fair-Value-Gap detector with an
  informative-timeframe filter).

**Repos with genuine original research or unusual machinery:**

- **`mlsys-io/PortfolioBench`** — 66 of 67 first-seen. `MlpSpeculativeStrategy`
  trains an MLP ensemble on TA features; `beta_factors_model` loads a
  joblib-serialized regression predicting weekly returns from Fama-French-style
  crypto factors; `adaptive_trend` runs H4 momentum with a rolling-Sharpe
  filter and market-cap top/bottom-K long/short allocation;
  `PolymarketLogicalArbStrategy` arbitrages Polymarket BTC-threshold contracts
  via subset/superset price-gap z-scores. (`PpoMomentumStrategy`'s "PPO" is the
  Percentage Price Oscillator, not reinforcement learning, despite the name.)
- **`webclinic017/strategies-freqtrade-`** — split by subfolder: `archived/`
  and `binanceus/` are conventional, but `Anomaly/`, `NNPredict/`, `NNTC/`,
  `TSPredict/` build a shared ML framework unusual in this corpus. `Anomaly`
  trains a pluggable classifier zoo (autoencoder, PCA, IsolationForest, LOF,
  KMeans, OneClassSVM, GMM, DBSCAN) to flag trade points as statistical
  outliers; `FBB_KalmanSIMD` fits an EM-tuned Kalman filter (`simdkalman`) to
  smooth/predict price; `NNPredict` trains a per-pair LSTM (GRU/CNN/
  Transformer/TCN/N-BEATS/Wavenet variants); `TS_Wavelet` forecasts individual
  wavelet coefficients via XGBoost/SVR before reconstructing the signal — "very
  compute intensive" per its own docstring.
- **`kemplail/freqtrade-stuff`** — a signal-processing cluster: `DWT` (Haar
  wavelet denoising via `pywt`), `FFT` (Fourier low-pass via `scipy.fft`),
  `SARIMAX` (statsmodels AR(2) forecast), `Kalman` (`pykalman` smoothing) —
  each trades crossovers of "predicted vs. actual close."
- **`markdregan/FreqAI-Marcos-Lopez-De-Prado`** — genuinely implements its
  namesake's methods: `LitmusMLDPStrategy` builds zigzag peak/valley labels,
  applies triple-barrier labeling, and trains a meta-model gated on the
  primary model's own historical performance (real meta-labeling); fractional-
  differentiation code exists (`FracdiffStat`) but is disabled by default.
- **`p-zombie/freqtrade`** — otherwise a pure copy archive (0 first-seen), but
  `GymStrategy` loads a `stable_baselines3` PPO reinforcement-learning model
  for signals, and `TrainCatBoostStrategy` trains a CatBoost classifier on
  seven other named strategies' buy signals as meta-ensemble features.
- **`LazyPigPig/freqtrade-grid`** — grid/DCA trading, not signal-based: the
  `GRIDDMIPRICEStrategy*` family sets `enter_long` unconditionally true and
  manages a 4-line small/big price grid entirely inside
  `adjust_trade_position`; `DCADMIPRICEStrategyFuture`/`RebalanceStrategySpot`
  do position-scaling/rebalancing the same way.
- **`AlexCryptoKing/freqailstm`** — FreqAI + LSTM: `ExampleLSTMStrategy` and
  the `AlexStrategyFinalV6`/`V8`/`V9` (+ `Hyper` variants) family run neural-net
  regressors for entry signals; the repo also vendors an entire local copy of
  the freqtrade/FreqAI framework under `user_data/config/`.
- **`djienne/YOUTUBE_STRATEGIES_FREQTRADE`** — companion code to the author's
  YouTube channel, spanning a wide range of experimental approaches rather
  than one family: `DELTA_NEUTRAL` (delta-neutral hedging), `HMMv3` (hidden
  Markov regime detection, blocked in this corpus by `hmmlearn`'s missing
  build toolchain), `HEAD_SHOULDER`/`SUPPORT_RESISTANCE` (chart-pattern
  detection), `CME` (TradingView-fed strategy, blocked by a declined
  `tvDatafeed` install), `BigWill` (a `pandas_ta` EMA strategy found this
  session to crash when its window is shorter than the indicator period),
  `MartyEMA`, `TRIX_LS`, `SARIMAX`.
- **`jerome-benoit/freqai-strategies`** — `RLAgentStrategy` (ReforceXY) drives
  entries/exits from a reinforcement-learning agent's action output;
  `QuickAdapterV3` is a FreqAI regressor with extensive feature/label
  engineering.
- **`Mohamed-sm/Freqtrade-RLStrategy-IA`** — despite the "RL" name, a standard
  FreqAI classification pipeline (RSI/MACD/SMA/EMA/volume/time features).
- **`mmartel86/freqtrade-setup`** — FreqAI classifier over an extensive
  engineered feature set (RSI/SMA/ATR/BB%/MACD-hist/ADX/OBV/EMA ratios/candle
  body-wick %), 30x leverage, custom profit-reversal exit logic.
- **`Netanelshoshan/freqAI-LSTM`** — FreqAI LSTM regressor combining
  CCI/RSI/momentum/SMA/MACD/ROC/Bollinger features via a hyperoptimizable
  weighted sum, letting the model set exits instead of fixed ROI/stoploss.
- **`Lijunnan0113/Lijunnan0113-Lijunnan_Freqtrade_Strategy`** — futures
  long/short combining discrete wavelet transform and FFT price smoothing with
  Fisher-transformed Williams %R, Bollinger "gain," RMI/SSL trend filters, and
  decay-based dynamic ROI/stoploss.
- **`HeyMrRobot/Freqtrade-Adaptive-Renko-Strategy`** — Renko bricks with an
  ATR-optimized adaptive brick size (`scipy.fminbound`), trading brick-
  direction reversals.

**Personal collections built mostly from other people's published strategies**
(each still checked file-by-file; naming the few genuinely distinctive pieces
where they exist): `hamidreza07/freqai-strategy` (despite the name, mostly
conventional TA across `classic/` and five numbered "startegy test" folders;
real FreqAI use only in `WTAI` and `FreqaiBinaryClassStrategy`) ·
`freqtrade/freqtrade-strategies` (the official project's own tutorial repo:
`Strategy001`-`005`, berlinguyinca's classic scalpers, Mablue's `GodStra`/
`Zeus` auto-indicator generators, a dedicated `lookahead_bias/` teaching
folder) · `werkkrew/freqtrade-strategies` (`Solipsis5` and `Schism` are the
maintained flagships, RMI/informative-pair strategies with dynamic ROI; the
rest is an archived Cluc*/Hacklemore*/BinHV* mirror) ·
`Foxel05/freqtrade-stuff` (fully original but mostly generic offset/momentum
ports; `RaposaDivergenceV1` again, self-flagged for possible look-ahead bias)
· `thinkong/freqtradestrategies` (`HarmonicDivergence`, `TrixV21Strategy`,
`abbas` are its three originals among mostly ClucHAnix/BB_RPB_TSL copies) ·
`phuchust/freqtrade_strategy`, `MelvynClark/Freqtrade-Strategy` (22/22
first-seen by name, but much of the code is a renamed copy of
NostalgiaForInfinityX or freqtrade's own sample template underneath) ·
`titouannwtt/freqtrade-ultimate` (`kac_index_v1`/`v2` pull a live TOTAL3
altcoin-cap index via `tvDatafeed` for regime filtering; `simple_vwap_v1` is
deliberately low-selectivity, aiming for ~90% market exposure) ·
`brookmiles/freqtrade-stuff` (the `Obelisk_*` family: Ichimoku-Cloud trend
following, one variant deliberately skips ROI/trailing-stop exits) ·
`eovie/freqtrade_strs` (borrowed trading logic; the real contribution is
custom `IHyperOptLoss` classes tuning by expectancy/win-rate instead of raw
profit) · `nateemma/strategies` (unusually well-documented: OversoldReversion
mean reversion, a portfolio-rebalancing `BasketStrategy` family, funding-rate
carry, plus reference copies of NFI/MacheteV8b/CryptoFrog for comparison) ·
`iterativv/NostalgiaForInfinity` (the ORIGINAL NFI repo — one of the most
copied public freqtrade strategies in existence, a large multi-condition
system with dozens of independently-tunable entry conditions across
`normal`/`pump`/`quick`/`rebuy`/`rapid`/`grind`/`scalp` modes) ·
`nancyjimenezbnoewowo/NostalgiaForInfinity` (a direct, unmodified fork of the
above, 0 first-seen) · `flaviosiotto/freqtrade-strategy` (`TouchEmaStrategy`,
`BBBreakoutStrategy`, `FakeoutStrategy` via `scipy.argrelextrema`) ·
`i1ya/freqtrade-strategies` (entirely derivative `CombinedBinHClucAndMAD*`/
`BigZ*` variants, explicitly credited to their inspiration, 0 first-seen) ·
`mikedigriz/freqtrade-strategy-mikedigriz` (small honest toolbox: Hull-MA
scalps, Fisher-Hull, a Chaikin-Money-Flow "SmartMoneyStrategy") ·
`MMR-19/freqtrade-strategies` (`Tesla4`/`Tesla7`, EWO/SMA-offset variants
credited to `@Rallipanos`) · `ShahAnuj2610/my-freqtrade` (fused EWO/offset-SMA
community strategies, plus `CryptoPrediction` — a Keras LSTM on OHLCV+SAR) ·
`ShahAnuj2610/my-freqtrade-nfi-nextgen` (NFI forks plus custom trailing-buy
and RSI-gated DCA wrappers) · `cyberjunky/freqtrade_strategy` (NFI, E0V1E, an
EMA-offset scalper) · `devbootstrap/optimize-trading-strategy-using-freqtrade`
(a teaching repo: plain BB+RSI mean reversion, generic as advertised) ·
`hansen1015/freqtrade_strategy` (TA-Lib candlestick patterns, a bare Heikin-
Ashi SMA cross explicitly marked "not for live," 0 first-seen).

**Small and single-strategy repos** (1-4 classes each; every one read, kept
brief since there is little to characterize beyond what it does):
`bustillo/freqtrade-strategies` (ZaratustraDCA: ADX/DMI entries with
BTC-correlation filters, Murrey Math levels, progressive DCA) ·
`Juusseli/Trade` (SMAOffset/EWO template with an HMA50-vs-EMA100 exit guard) ·
`jilv220/BB_RPB_TSL` (Bollinger/Keltner squeeze-off breakout plus RMI/CCI/
StochRSI dip conditions, ensembled) · `DonaldSimpson/remora-freqtrade`
(wrappers calling an external risk-scoring API, fail-open if it's down) ·
`anakein/beastbotXB` (Nadaraya-Watson kernel-regression envelope with SSL
channels) · `ingpawat/freqtrade-strategy-with-backtest` (MACD zero-cross; a
variant adds PAXG-correlation-based dynamic leverage) ·
`shadowp2810/technical_indicators_cryptos` (hand-rolled "fall2/rise2"
candle-pattern detectors) · `botenesp/freqtrade_strategies` (buys low-volume
dips near the lower Bollinger band, avoiding pump-and-dump) ·
`miwtoo/ft-action-zone` (classic EMA12/26 "Action Zone" indicator) ·
`devbootstrap/freqtrade-hyperopt-running-in-cloud-example` (unmodified
`sample_strategy` + `Strategy004`, a cloud-hyperopt demo, no original logic) ·
`imsatoshi/GeneTrader` (EWO/Williams-%R/VWAP/Bollinger/CMF combo, plus files
literally evolved by the repo's own genetic-algorithm optimizer) ·
`keryc/crypto-bot` (unmodified NFI + sample template, no custom logic) ·
`mohammadmoth/Freqtrade-Strategy` (freqtrade's own default sample logic,
essentially unmodified; a 3-Supertrend-agreement variant) ·
`obseries/freqtrade-strategy-ichiv1` (the well-known public "Ichi V1"
Ichimoku strategy; `proton` is an unrelated FreqAI direction-classifier) ·
`Bananajoexxc/RegimeFilterStrategy-Freqtrade` (EMA50-vs-EMA100 bull/bear
regime gate with a 20-period breakout entry) ·
`TomtomEh/freqtrade-websocket` (a live Binance-websocket order-book cache
gating BB/EMA/RSI entries by bid/ask wall ratio) ·
`hippocritical/delist_scraper` (10x-leveraged shorts triggered directly by a
pre-scraped exchange-delisting-announcement feed) ·
`keithorange/FreqTradeCustomOrders` (not a strategy — a CLI-configured
stoploss/exit-management toolkit) ·
`seannowotny/FlawlessVictoryPort` (port of a TradingView "Flawless Victory"
Bollinger/RSI script) ·
`Rikj000/MoniGoMani` (the well-known public MoniGoMani: eight
independently-hyperopt-weighted signals combined into one composite score) ·
`froggleston/cryptofrog-strategies` ("kitchen sink" strategy combining
Heikin-Ashi smoothing, StochRSI, MFI, Bollinger expansion, squeeze-momentum,
with a linear-decay trailing stoploss) ·
`DutchCryptoDad/FreqtradeBotStrategyDevelopmentForBeginners` (a beginner
tutorial repo: RSI+SMA cross, MACD cross, the stock sample template).

**Contributed no strategy content at all** (4 repos, distinct from the
"copies everything" repos above — these have no `IStrategy` class in them to
begin with): `freqtrade/berlinguyinca-trading-strategies` (the repo's own
description: "outdated - please use the official repo... from now on") ·
`raphant/lazyft` (a real, substantial backtest/hyperopt CLI wrapper library
around freqtrade — tooling, not a strategy) · `yalcin/freqtrade-mcp` (an MCP
server exposing freqtrade's codebase for LLM introspection — developer
tooling, not a strategy). A fourth entry, `logs`, in `corpus_sources.json` is
not a repository at all: it is a stray local directory (a leftover log file
and a README) that `census_repos.py`'s directory scan picked up alongside the
77 real repos — noted here so a future reader doesn't go looking for a GitHub
repo named "logs".

## The search, so you can extend or refute it

Repositories were found with the GitHub search API using these queries, then
filtered to those containing classes that inherit `IStrategy`:

```
freqtrade+strategies          freqtrade+strategy+in:name
freqtrade+strategy            freqtrade+in:readme+IStrategy
topic:freqtrade               populate_entry_trend
freqtrade-strategies          populate_buy_trend
freqtrade+hyperopt+strategies NostalgiaForInfinity
freqtrade+bot+strategies
```

**This is not proof of exhaustiveness.** GitHub search does not return
everything, private and archived repositories are invisible, and strategies
posted in gists, forums or Discord are not covered. The claim is "the largest I
could find with these queries", and the queries are here precisely so the claim
can be beaten.

## A size filter that was wrong, and how it was found

Four repositories were initially excluded for exceeding 60 MB. Checking them
showed the filter used the wrong signal entirely — they are large because of
stored backtest results, not strategies:

```
Rikj000/MoniGoMani     271 MB    21 .py files, 2 with strategies
imsatoshi/GeneTrader   226 MB    49 .py files
obseries/...-ichiv1    111 MB     2 .py files
```

Repository size says nothing about strategy count. The filter was replaced: the
tree is listed through the API and only `.py` files containing `IStrategy` are
fetched. Size stops mattering, and so does the caveat that used to accompany it.

One repository (`ShahAnuj2610/my-freqtrade`) could not be cloned at all — it
contains filenames with colons, which Windows rejects. Fetching files
individually recovered it. That is now the default method rather than a
workaround.

## 2026-09-08: closing corpus gaps by trading approach

A keyword census of the corpus (restricted to files that actually declare a
strategy class, not vendored framework copies some repos bundle) showed a
handful of approaches near-empty: transformer-based models, Avellaneda-Stoikov
market-making, regime-switching, and SMC/ICT liquidity-sweep style entries all
had one digit of representation out of ~1,046 strategies at the time. Nine
repositories were harvested to close those gaps specifically, six of them
adding genuinely new strategies:

- **`djienne/AVELLANEDA_MARKET_MAKING_FREQTRADE`** — `avellaneda`. Avellaneda-
  Stoikov market-making on Hyperliquid; a companion script
  (`run_avellaneda_param_calculation.py`, missed by `harvest.py`'s
  `IStrategy`-only filter and fetched separately) recalculates optimal bid/ask
  parameters via a local `subprocess.run([sys.executable, script_path, ...])`
  call every 10 bot loops — verified to be a hardcoded local invocation, not
  attacker-influenced input.
- **`yeboster/liquidity-sweep-freqtrade`** — `LiquiditySweep`,
  `MeanReversionTrend`. SMC/ICT-style liquidity-sweep reversal detection with
  OTE (optimal-trade-entry) zones.
- **`Vijay190899/Trade-Bot`** — `AntigravityStrategy`,
  `AntigravityGridStrategy`, `AntigravityStrategyV3`. A signal-validation gate
  around a reinforcement-learning (PPO-style) core; an optional `TradeMemory`
  self-improvement hook points at the author's own local machine
  (`V:/Antigravity/...`) and degrades gracefully (`try`/`except`) when absent.
- **`OfficialGIGA/freqtrade-ml-strategy`** — `UltimateAlphaV16`. LightGBM-based
  strategy with regime-aware position sizing; needed a sibling `features.py`
  that `harvest.py`'s filter missed (no literal `IStrategy` in that file),
  fetched separately and security-scanned clean.
- **`songhuaxueyue-tech/trend-regime-transformer`** — `CsMom` (two variants:
  `cs_mom_ai.py` with an optional transformer-based regime predictor behind a
  hardcoded Docker path and a `try`/`except` fallback, `cs_mom_stable.py`
  without it).
- **`Kureshi25/cryptobot`** — `AdaptiveRegime`, `AdaptiveRegimeLong`,
  `TrendBreakout`, `TrendFutures`, `HighFreqDemo`. Regime detection via the
  Kaufman Efficiency Ratio, switching between a Donchian-breakout trend arm and
  a Bollinger/RSI mean-reversion arm. `AdaptiveRegimeLong` is a long-only
  variant that subclasses the sibling `AdaptiveRegime` file rather than
  `IStrategy` directly, so `harvest.py`'s filter missed it too; fetched by
  hand. A sixth file in the same repo, `AdaptiveRegimeDemo`, was left out
  deliberately — the author's own docstring calls it "a DELIBERATELY LOOSENED
  copy... built to make the machinery visible, not to make money."

Three repositories were checked and added no new content: `darkvolg/trendrider-strategy`
(`TrendRiderStrategy`, a class name already present elsewhere in the corpus)
and `titouannwtt/freqtrade-france-strategies-kac-index` /
`-strategies_simple_vwap` (`kac_index_v1`/`v2`, `simple_vwap_v1`, all three
already vendored inside `titouannwtt/freqtrade-ultimate`, already in the
corpus).

## Repositories checked and rejected

Not every repository the searches above surfaced was harvested. Recording the
rejections too, not just the additions — a repo that looked relevant and
wasn't is exactly the kind of thing a later search will trip over again
without a note explaining why it was already ruled out.

**Fails the out-of-sample backtest methodology itself, not a code-quality
problem.** These all have a plausible-sounding edge that this project's
methodology structurally cannot measure — the signal is either paid-API-gated
and inert in backtest, needs to replay state that cannot be replayed, or the
author says outright it isn't meant to be evaluated as a strategy:

- **`aicoincom/coinos-skills`** — `FundingRateStrategy`,
  `LiquidationHunterStrategy`, `WhaleFollowStrategy`. Each strategy's
  distinguishing signal (funding rate, liquidation clusters, whale order flow)
  only activates when `self.dp.runmode.value in ('live', 'dry_run')`, gated
  behind a paid AiCoin API tier ($29-$699/month per feature). In backtest the
  signal columns stay at their inert default and the strategy measures as a
  bare RSI+EMA crossover — the thing this repo exists to test never gets
  tested.
- **`Coinversaa/coinversaa-freqtrade-example`** —
  `CoinversaaSmartMoneyStrategy`. The module docstring calls it a "**reference
  implementation** — it demonstrates how to call the API inside a strategy,
  not a production trading system."
- **`djienne/COPY_WALLET_HYPERLIQUID`** — `COPY_HL`. Copies a tracked wallet's
  *current* Hyperliquid position every bot loop via a live API call; there is
  no historical position-history source to replay, so a backtest over a past
  window would apply today's live account state to yesterday's candles.
- **`Nicbyte/solnexus-freqtrade-adapter`** — `SolnexusBridgeStrategy`. Its own
  docstring: "This is a **SCAFFOLD** showing the bridge, not a profitable
  strategy." No `populate_indicators` at all; entries come only from an
  external JSON file a separate, non-public pipeline has to produce.
- **`mihalismacura7-blip/leadedge-examples`** — matched a `freqtrade` search
  only incidentally; `leadedge_signal_strategy.py` is a Hummingbot (not
  freqtrade) script, and its own comments say the edge lives in a 60-400ms
  window, tradeable only with a paid real-time signal feed and low-latency
  execution — unrelated to this project's framework or its backtest horizon.
- **`rajdeep7878/freqtrade-blockchain`** — vendors an entire copy of the
  freqtrade framework itself plus a blockchain audit-log add-on; no actual
  trading strategy in it to harvest.

**No real strategy content to harvest at all** — the repository exists (some
with real activity or star counts) but has no `IStrategy` class, or none
outside of test/framework scaffolding:

- **`djienne/Cartea-Jaimungal_MARKET_MAKING_FREQTRADE`** — a genuine
  parameter-estimation research toolkit (dynamic-spread calibration scripts)
  by the same author as the Avellaneda repo above, but has no
  `user_data/strategies` directory at all — nothing runnable despite the
  freqtrade branding.
- **`hugocen/freqtrade-gym`** — 231 GitHub stars, but it is a *gym
  environment* for training reinforcement-learning models
  (`freqtradegym.py`, `rllib_example.py`, ...), not a deployable strategy.
- **`kiploks/kiploks-freqtrade`** — a backtest-robustness-analytics wrapper
  (`run.py`, Docker scripts) around freqtrade's own output; no strategy files.
- **`MGTONY23/AegisSystems`** — description promised "market regime
  detection"; the repository tree is empty.
- **`cryptodeveloperq/FreqTrade`**, **`MuhammadUmer3/Crypto-Bot`**,
  **`Fahedbentaleb/Crypto-Source`** — empty repositories (the first two
  read as low-effort/marketing placeholders — "Join my journey to passive
  income 🚀💻" — rather than working code).

**Harvested but contributed nothing new** (already covered above): `darkvolg/trendrider-strategy`
and the two `titouannwtt/freqtrade-france-strategies-*` repos duplicate
classes already in the corpus.

## Reproduce

```bash
python harvest.py <owner/repo> [<owner/repo> ...]   # fetch strategy files only
python census_repos.py                              # this table
python corpus.py --shard k/5                        # measure
python ledger.py --pop=corpus            # the ladder, one population at a time
python anatman.py                                   # every lived defect, as a test
```
