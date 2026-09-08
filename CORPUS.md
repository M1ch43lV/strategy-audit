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
