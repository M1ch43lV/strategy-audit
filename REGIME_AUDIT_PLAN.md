# Regime-based Freqtrade Strategy Audit

**Working title:** Regime-Aware Audit and Strategy Selection for Public Freqtrade Strategies
**Status:** Stage 7 complete / Stage 9 awaiting preregistration decisions
**Version:** 0.19
**Date:** 2026-08-30
**Primary target:** Codex / other AI coding sessions working on `Apex-prim/strategy-audit`
**Repository:** https://github.com/Apex-prim/strategy-audit

> This document is a living methodological and implementation plan. It is intentionally written so that a new AI session can understand the motivation, prior findings, current proposed design, unresolved decisions, and implementation order without relying on previous chat context.

---

## 0. How another AI session should use this document

Before changing code or methodology:

1. Read this document in full.
2. Inspect the current repository, especially `README.md`, `BASELINE.md`, `CORPUS_PLAN.md`, `PREREGISTRATION.md`, `LEDGER.md`, `LEDGER.csv`, `CORRECTIONS.md`, `DECISION_INVARIANCE.md`, and the existing audit scripts.
3. Verify that the repository has not materially changed since this document was written.
4. Separate **frozen primary design**, **secondary robustness design**, and **open discussion items**.
5. Do not silently modify primary thresholds or eligibility rules after seeing strategy-performance results.
6. If proposing a change, add it to the **Decision / Discussion Log** at the end of this document with:
   - proposal,
   - reason,
   - expected benefit,
   - possible bias introduced,
   - whether it must be decided before the next result run.
7. Prefer additive changes over rewriting or deleting the repository's existing audit logic.
8. Preserve the original strategy files and the existing baseline audit results.

This file should function as both:

- an implementation handoff for Codex,
- a methodological preregistration draft,
- and a discussion document for additional AI reviewers.

---

# 1. Starting point: what the existing repository already established

The public repository `Apex-prim/strategy-audit` audits public Freqtrade strategies using Freqtrade itself rather than reimplementing strategy logic.

At the time this plan was written, the repository headline states:

- **895 unique strategy classes** in the ledger,
- collected from **53 public repositories**,
- **496 measured** at the first gate,
- **456 produced trades**,
- then progressively fewer survive profitability, significance, look-ahead, recursive-bias, trap, multiplicity, effect-size, and economic gates.

The current published ladder in `README.md` is approximately:

```text
G0_measured       895 -> 496
G1_trades         496 -> 456
G2_is_pos         456 -> 158
G3_is_sig         158 -> 83
G4_os_pos          83 -> 81
G5_os_sig          81 -> 72
G6_lookahead       72 -> 17
G7_recursive       17 -> 2
G8_traps            2 -> 2
G9_candle           2 -> 2
G10_fdr             2 -> 2
G11_effect          2 -> 1
G12_economic        1 -> 0
```

Repository source:
https://github.com/Apex-prim/strategy-audit

The exact counts must always be re-read from the current repository before a new run; this document must not become an authoritative duplicate of a changing ledger.

## 1.1 Existing execution model

According to `CORPUS_PLAN.md` / repository documentation, the audit uses:

- Freqtrade itself as the execution engine,
- the strategy's own declared timeframe,
- spot trading,
- the strategy's original code,
- eight requested USDT pairs:
  - BTC,
  - ETH,
  - LTC,
  - XRP,
  - ADA,
  - XLM,
  - XMR,
  - DASH,
- in-sample window around `2018-03-01 ... 2020-03-01`,
- out-of-sample window around `2020-03-01 ... 2026-08-20`,
- 0.1% fee per side headline assumption, with higher-cost sensitivity reported.

Reference:
https://github.com/Apex-prim/strategy-audit/blob/main/CORPUS_PLAN.md

## 1.2 Existing buy-and-hold finding

`BASELINE.md` makes `Market change` the buy-and-hold comparison. Freqtrade's `Market change` represents buy-and-hold over the same pairs and same backtest window.

Reference:
https://github.com/Apex-prim/strategy-audit/blob/main/BASELINE.md

The current repository reports that the remaining economically relevant survivor captured substantially less return than buy-and-hold over the full OOS window. The README gives an example of roughly:

- strategy cumulative return: **+106.9%**,
- buy-and-hold / market change: **+346.3%**,
- shortfall: about **239 percentage points**.

However, the repository itself then demonstrates that this aggregate result is highly **window-direction dependent**.

## 1.3 Existing regime clue: the aggregate verdict depends on market direction

The repository contains an exploratory calendar-year split in which the market sign cleanly separates the previous survivor set's comparison with buy-and-hold:

```text
year    market       survivors beating buy-and-hold
2020   +143.04%      0 of 5
2021   +218.33%      0 of 5
2022    -66.70%      5 of 5
2023    +76.37%      0 of 5
2024    +95.90%      0 of 5
2025    -20.89%      5 of 5
2026    -29.65%      5 of 5
```

The README explicitly warns that this historical regime table belongs to an earlier survivor population and is exploratory / superseded for the current survivors. It nevertheless records an important methodological finding:

> The aggregate verdict was a property of the chosen window and its direction.

Repository source:
https://github.com/Apex-prim/strategy-audit

This is the key motivation for the new investigation.

## 1.4 Why the existing final-survivor funnel must NOT define regime eligibility

The existing ladder asks a different question:

> Which published strategies remain profitable/significant/technically valid/economically superior across the chosen whole windows?

The new question is:

> Which strategies are useful in specific market conditions, and can a regime-aware selector combine specialist strategies better than one universal strategy?

A strategy can therefore be poor over the entire 2020–2026 window but excellent in one specific state, for example:

- BTC bear + coin bear,
- BTC bear + coin bull relative-strength episode,
- sideways/choppy market,
- strong bull trend.

Therefore the regime project must create a **`regime_eligible` eligibility
flag** based primarily on technical integrity, not whole-window profitability.
The flag is keyed by `strategy_id × run_profile` in the pooled canonical
corpus. `original` and `repaired` remain provenance values, not eligibility
containers or separate primary populations.

Do **not** restrict the new analysis to the 72, 17, 2, or 1 strategies that survive later economic gates in the existing ladder.

The starting pool should be derived from the broad measured/trading corpus and then filtered only for technical reasons relevant to reliable regime testing.

---

# 2. New research objective

The primary objective is no longer to find one globally best strategy.

The objective is to test whether a **meta-strategy** can select strategies conditional on the observable market state.

Conceptually:

```text
GLOBAL BTC REGIME
        +
LOCAL COIN STATE
        ↓
SELECT SUITABLE STRATEGY
```

Desired final outputs include:

1. best bull-market specialists,
2. best bear-market specialists,
3. best sideways / non-trending specialists,
4. strategies that exploit coins with relative strength against BTC,
5. robust universal strategies that survive all major regimes without catastrophic degradation,
6. evidence on whether BTC regime alone is sufficient or whether coin-specific state adds meaningful information.

The long-term live-system hypothesis is:

```text
Current BTC regime + current coin state
                ↓
       strategy-selection layer
                ↓
      original Freqtrade strategy
```

The present project is an audit / research project, not yet a production trading system.

---

# 3. Design principles

The first version should maximize:

- simplicity,
- investigator transparency,
- reproducibility,
- causal / live-compatible classification,
- minimal look-ahead risk,
- minimal parameter tuning,
- separation of discovery and validation,
- preservation of the original strategy logic.

Avoid beginning with:

- HMM,
- clustering-based regime discovery,
- machine-learning regime classifiers,
- optimized regime thresholds,
- large feature sets.

Those methods may become useful later, after the first rule-based results exist.

---

# 4. Regime architecture: global BTC regime + local coin state

The preferred conceptual hierarchy is:

```text
BTC / global crypto conditions
            ↓
      GLOBAL REGIME
            ↓
     individual coin
            ↓
       COIN STATE
            ↓
    strategy suitability
```

BTC is treated as the primary systemic crypto-risk signal because most crypto assets historically share substantial common market direction with BTC.

However, BTC must not be the only input to later interpretation: a coin can show strong positive or negative behavior relative to BTC.

Therefore:

- **BTC regime = global context / risk regime**
- **Coin state = local trend / tradability state**
- **Relative strength = contextual descriptor and later possible selection variable**

---

# 5. PRIMARY regime model: DMI / ADX

## 5.1 Why DMI / ADX is primary

DMI/ADX separates two questions cleanly:

- `+DI` vs `-DI`: direction,
- `ADX`: strength of trend.

It is rule-based, widely understood, deterministic, causal, and can be implemented identically for BTC and every individual coin.

Use Wilder-compatible DMI/ADX on **daily OHLCV**.

### Proposed frozen primary parameters

```text
DMI / ADX period = 14
```

### Proposed primary states

```text
ADX >= 25 AND +DI > -DI  -> BULL
ADX >= 25 AND -DI > +DI  -> BEAR
ADX < 20                 -> SIDEWAYS
20 <= ADX < 25           -> TRANSITION
```

Do not optimize these thresholds after observing strategy outcomes.

## 5.2 Daily causal timing rule

For a completed daily candle `D`:

```text
calculate DMI/ADX after D closes
                ↓
regime becomes usable from D+1
```

This one-day availability lag must be explicit in code.

For intraday strategies, all candles during day `D+1` see only regime information based on data through the close of day `D`.

Timezone: UTC.

## 5.3 Run the same state engine twice

For every date and pair calculate:

### BTC state

```text
btc_plus_di
btc_minus_di
btc_adx
btc_regime
```

### Coin state

```text
coin_plus_di
coin_minus_di
coin_adx
coin_state
```

This produces the primary 4 × 4 matrix:

```text
BTC:  BULL / BEAR / SIDEWAYS / TRANSITION
Coin: BULL / BEAR / SIDEWAYS / TRANSITION
```

There are 16 possible combinations.

Do not pre-delete combinations merely because they appear unusual.

For example:

```text
BTC BEAR + COIN BULL
```

may represent exactly the relative-strength behavior that a specialist strategy can exploit.

---

# 6. SECONDARY / ROBUSTNESS model A: Signed Kaufman Efficiency Ratio

Efficiency Ratio **is explicitly part of this plan**, but it is **not the primary regime definition in version 1**.

Purpose:

> Test whether findings attributed to DMI/ADX survive under an independent concept of trend quality.

The signed efficiency ratio can be represented as:

```text
SER(n) = (Close_t - Close_(t-n)) /
         sum(abs(Close_i - Close_(i-1))) over n periods
```

Interpretation:

```text
SER close to +1 -> efficient upward trend
SER around 0    -> choppy / non-directional movement
SER close to -1 -> efficient downward trend
```

## 6.1 Proposed first implementation

Always store, at minimum:

```text
btc_ser_30
coin_ser_30
```

Proposed lookback for the first implementation:

```text
n = 30 daily bars
```

## 6.2 Important open methodological decision

Unlike ADX 20/25, there is no equally universal canonical SER threshold that should be pretended to be investigator-independent.

Therefore version 0.3 makes the following distinction:

### Pre-specified and safe now

- calculate SER(30),
- store it for every day,
- use it as a continuous robustness variable,
- compare its distributions across DMI/ADX regimes,
- evaluate whether specialist rankings are monotonic with signed efficiency.

### Not yet frozen

Whether SER should define its own hard categories such as:

```text
SER > x     -> bull trend
|SER| < y   -> sideways
SER < -x    -> bear trend
```

Any thresholds `x` and `y` must be agreed and preregistered **before** seeing strategy-performance results from the SER classifier.

Other AI reviewers are explicitly invited to propose a principled threshold method.

Potential options to discuss:

1. fixed literature-inspired thresholds,
2. thresholds determined on a historical training-only period,
3. expanding-window percentiles,
4. use SER only as a continuous robustness dimension, without hard regimes.

Do not choose whichever method gives the nicest strategy rankings after the fact.

---

# 7. SECONDARY / ROBUSTNESS model B: Rolling Return + Realized Volatility

Return / volatility **is also explicitly part of this plan**.

Purpose:

> Provide a deliberately simple and intuitive alternative regime definition that does not depend on DMI/ADX mechanics.

Always calculate and store:

```text
btc_return_30d
btc_return_90d
coin_return_30d
coin_return_90d

btc_realized_vol_30d
coin_realized_vol_30d
```

## 7.1 Proposed return-direction classifier

Candidate rule for discussion / preregistration:

```text
90d return > +20%  -> BULL
90d return < -20%  -> BEAR
otherwise          -> SIDEWAYS / NEUTRAL
```

This is intentionally simple but the ±20% threshold is a modeling choice and must be treated as such.

It should be frozen before results if used as a categorical classifier.

## 7.2 Volatility dimension

Realized volatility should initially be stored continuously.

Possible later categorization:

```text
NORMAL VOL
HIGH VOL
EXTREME VOL / CRISIS
```

A causal percentile-based method may be preferable to fixed absolute volatility thresholds because crypto volatility changes structurally over time.

If percentiles are used, they must be based only on prior data, e.g. a trailing historical window, never on the full 2020–2026 sample.

## 7.3 Role of this model

This model is a **robustness benchmark**, not the primary classifier.

A compelling result would be:

> Strategy X behaves as a bull specialist under DMI/ADX and also performs best when 90-day returns are strongly positive.

A fragile result would be:

> Strategy X appears to be a bull specialist only under one narrow DMI/ADX definition and loses the effect under return/volatility classification.

---

# 8. Additional variables to store now without using them as primary regime gates

Store them because recomputing the entire corpus later is expensive.

## 8.1 Relative strength versus BTC

```text
rs_30d = coin_return_30d - btc_return_30d
rs_90d = coin_return_90d - btc_return_90d
```

These help distinguish:

```text
BTC bull + coin bull + coin outperforming BTC
```

from:

```text
BTC bull + coin bull + coin lagging BTC
```

Do not make RS a primary gate in the first run unless it is preregistered before results.

## 8.2 DMI spread

Store:

```text
btc_di_spread  = btc_plus_di - btc_minus_di
coin_di_spread = coin_plus_di - coin_minus_di
```

Optional normalized form:

```text
(+DI - -DI) / (+DI + -DI)
```

This may later distinguish weak directional signals from strong directional dominance.

## 8.3 Market breadth

Possible daily breadth descriptors:

```text
pct_coins_plus_di_gt_minus_di
pct_coins_adx_ge_25
pct_coins_bull_state
pct_coins_bear_state
```

Breadth must initially remain descriptive.

Later it may separate:

```text
broad crypto bull
```

from:

```text
BTC-led / narrow bull
```

---

# 9. Strategy taxonomy BEFORE performance analysis

## 9.1 Yes: classify strategies beforehand

The source-code strategy type should be documented before examining regime-performance results.

However, this should be called a **taxonomy**, not necessarily statistical clustering.

Use multi-label categories such as:

```text
trend_momentum
mean_reversion
breakout
volatility_range
oscillator_reversal
hybrid
unknown
```

Possible fields:

```text
strategy
primary_archetype
secondary_archetypes
confidence
evidence
classifier_version
```

## 9.2 No: do not use the taxonomy to decide which regimes a strategy is allowed to enter

Every technically valid strategy should be tested across every primary regime combination.

Reason:

- indicator names do not guarantee actual behavior,
- many strategies are hybrids,
- a strategy described as mean-reversion may empirically behave as a bear-market defensive specialist,
- pre-filtering by taxonomy would bake the hypothesis into the test.

The taxonomy is for interpretation, not exclusion.

## 9.3 Classification should inspect conditions, not only indicator presence

Example:

```text
RSI < 30
```

suggests reversal / mean reversion.

But:

```text
RSI > 50 AND EMA20 > EMA50
```

may be momentum / trend continuation.

Therefore Codex should analyze entry logic and supporting indicators, not simply map `RSI -> mean_reversion`.

Ambiguous strategies should be labeled `hybrid` or `unknown` rather than forced into a category.

---

# 10. Behavioral clustering AFTER the primary test

True statistical clustering should be performed only after regime behavior is measured.

For each strategy build a regime-performance fingerprint containing, for example:

```text
return / avg trade / PF / drawdown / exposure
for each BTC × coin regime cell
```

Then optionally cluster strategies on those fingerprints.

This answers:

> Which strategies actually behave similarly?

Compare:

```text
source taxonomy
vs
observed behavioral cluster
```

Interesting discrepancies should be reported rather than corrected away.

Behavioral clustering is exploratory unless separately preregistered.

---

# 11. Canonical corpus, execution profiles, and regime eligibility

The primary analysis uses one **canonical corpus** containing as many unique
strategies as can be measured honestly. `original` and `repaired` are retained
as implementation-provenance fields, not as permanently separated analysis
worlds. Each unique `strategy_id` contributes at most one canonical
implementation to a given run profile, so an original and its repaired overlay
can never be counted as two independent strategies.

Canonical selection follows this order:

1. use the original when it runs reliably in the intended execution profile;
2. otherwise use the documented repaired implementation;
3. retain both measurements only for paired repair-sensitivity checks;
4. never duplicate them in rankings, inferential tests, or clustering.

Before eligibility, store execution compatibility separately from provenance:

```text
mode_support          = spot / futures / both / unknown
direction_capability = long_only / short_only / long_short / unknown
run_profile          = spot_long / futures_long / futures_short /
                       futures_long_short / unknown
author_mode_intent   = spot / futures / unspecified
evidence_level       = metadata / config / static_code / runtime_smoke /
                       runtime_full
```

`can_short = True` is evidence that Freqtrade requires futures mode, but it is
not evidence that reachable short entries exist or that a particular test
window produces short trades. Static signal capability and observed long/short
trade counts must therefore remain separate fields.

Primary behavioral clusters are formed within comparable run profiles. A later
cross-profile meta-clustering may use standardized regime fingerprints, but
must not treat spot and futures returns from different data windows as directly
exchangeable observations. Repair provenance is metadata for interpretation
and sensitivity analysis, not a clustering boundary.

Create a new field:

```text
regime_eligible
```

This field defines an analysis subset of the canonical corpus for a specific
run profile. A strategy may be eligible for `futures_long_short` and ineligible
for `spot_long`. Eligibility is therefore keyed by `strategy_id` and
`run_profile`, not by strategy name alone.

Do not inherit the existing economic survivor ladder as eligibility.

Candidate technical eligibility criteria:

- strategy can be loaded and measured,
- strategy produces trades,
- sufficient candle/data coverage,
- no disqualifying look-ahead behavior,
- no disqualifying recursive-bias behavior,
- no technical trap that makes the backtest mechanically invalid,
- original source-of-record remains unmodified; a documented repair overlay may
  be the measured implementation in the repaired population.

Important:

The exact technical eligibility definition must be derived from the repository's existing diagnostics and written down before regime-performance results are ranked.

Do not assume that `456` is the final regime-eligible count. `456` is the current count with trades before later technical screening in the published ladder.

Create a dedicated eligibility report explaining every exclusion.

## 11.1 Two provenance classes; one canonical analysis corpus

Retain exactly two implementation-provenance values:

```text
original
repaired
```

`original` means the strategy as published under the original audit setup.
`repaired` means the strategy under the documented repair stack. The repaired
provenance combines Class 1 environment repairs and Class 2 source overlays;
Class 1/Class 2 are provenance fields, not additional populations. Both values
are pooled in the canonical primary corpus after deduplication by `strategy_id`.

Every repaired result must store:

```text
population = repaired
repair_class
repair_rules
equivalence_status
source_tree
```

`equivalence_status` is one of:

- `strict_equivalent` — documented API/alias replacement or a provably dead
  value with identical reachable trading behavior;
- `output_equivalent` — intermediate warm-up values may differ, but a
  file-specific proof covers the full parameter range and establishes that the
  difference cannot reach a trading decision;
- `behavior_changed` — intended functionality is restored, but executable
  behavior changes and no equivalence is claimed.

Primary tables analyze the pooled canonical corpus and expose provenance on
every row. Mandatory sensitivity tables compare original/repaired strata and
repeat every inferential result after excluding `behavior_changed`.
Behavior-changing cases are also listed individually and reported
descriptively; they must never support a claim that compatibility repairs are
behavior-neutral.

A forced `can_short=False` overlay is recorded as
`variant=forced_long_only`, `equivalence_status=behavior_changed`. It may be
tested to maximize coverage, but it is excluded from the native primary result
and reported as a sensitivity variant rather than as the author's futures
strategy.

The historical repair register contains 59 source overlays. The execution-
profile audit adds 26 generated Class 2 overlays and an explicit Class 1
environment/configuration register. The current canonical manifest therefore
contains 763 original, 53 Class 1, and 84 Class 2 implementations; across the
complete stack it records 132 `strict_equivalent`, four `output_equivalent`,
one `behavior_changed`, and 763 `not_applicable` rows. These are implementation
snapshot counts only. Recompute them from the manifests before preregistration
rather than copying them into analysis code.

All 101 native futures-profile candidates have a mode-correct smoke result:
84 measured and 17 failed. Failures remain in the corpus with explicit Class 1,
Class 2, or blocked status; they are not silently discarded or assigned an
invented configuration. A longer-window control established that
`HurstCycleV4` was a smoke-window limitation rather than a compatibility error.

FreqAI uses an investigator-chosen training configuration. It therefore remains
a separate `run_class`/analysis stratum inside the applicable population, not a
third population, and is never pooled silently with ordinary strategy runs.

---

# 12. Phase A — cheap attribution analysis

First run each eligible implementation in its normal full-window form, retaining
the `original`/`repaired` population and repair-provenance fields above.

For every trade annotate the state observable at entry:

```text
strategy
pair
trade_id
open_time
close_time
profit
btc_regime_at_entry
coin_state_at_entry
btc_adx_at_entry
coin_adx_at_entry
btc_ser_30_at_entry
coin_ser_30_at_entry
btc_return_90d_at_entry
coin_return_90d_at_entry
btc_rv_30d_at_entry
coin_rv_30d_at_entry
rs_30d_at_entry
rs_90d_at_entry
regime_episode_id
```

This phase answers:

> Under which conditions do the eligible strategy implementations' trades
> perform well or badly?

It does **not** answer:

> What would happen if the strategy were actually activated only in that regime?

That distinction must be repeated in the report.

---

# 13. Regime episodes

Do not treat thousands of highly adjacent days as independent evidence.

Create contiguous episodes of the same primary BTC regime.

Store:

```text
episode_id
regime
start
end
duration_days
```

Optionally create combined BTC × coin episodes as well, but keep the BTC episode definition simple first.

For each strategy/regime calculate:

```text
number_of_episodes
positive_episodes
negative_episodes
episode_win_rate
median_episode_performance
worst_episode_performance
best_episode_performance
```

A strategy that works in one historical bull episode only should not be called a robust bull specialist.

---

# 14. Phase B — true regime-gated Freqtrade backtests

Phase B is the economically relevant test of the proposed meta-system.

Do not modify original strategy source files.

Implement a wrapper / gate layer so that new entries require:

```text
original_strategy_entry
AND btc_regime == target_btc_regime
```

for BTC-only tests, or:

```text
original_strategy_entry
AND btc_regime == target_btc_regime
AND coin_state == target_coin_state
```

for BTC + coin tests.

Primary rule:

> The regime gate controls **entries only**.

If a position was opened under a valid regime and the regime later changes, do not force-close it in version 1. Let the original strategy's exit logic operate normally.

Forced regime exits may be examined later as a separate sensitivity test.

---

# 15. Three model levels to compare directly

For every strategy compare:

## Model 0 — Original strategy

```text
original strategy, no regime filter
```

## Model 1 — BTC-regime gated

```text
original strategy
AND selected BTC regime
```

## Model 2 — BTC + coin-state gated

```text
original strategy
AND selected BTC regime
AND selected coin state
```

Central research question:

> Does the local coin state add useful information beyond the global BTC regime?

This should be evaluated out of sample, not assumed.

---

# 16. Benchmarks

The existing repository correctly highlights buy-and-hold, but the new regime project needs several benchmarks.

## 16.1 Full-window buy-and-hold

Same concept as Freqtrade `Market change`.

Purpose:

- opportunity-cost reference,
- continuity with the existing audit.

## 16.2 Regime-gated buy-and-hold

Hold the coin only when the same regime gate is active; otherwise hold cash.

Example:

```text
BTC BULL + COIN BULL -> hold coin
all other states     -> cash
```

This is a more relevant active-regime benchmark.

## 16.3 Cash

Especially important for spot bear-market evaluation.

A strategy that returns approximately 0% during a -60% market may be a strong defensive result even though absolute return is not positive.

## 16.4 Exposure-matched benchmark — important open enhancement

The existing README explicitly notes that low-exposure strategies can look good in falling markets simply because they are mostly out of the market.

An exposure-matched benchmark should therefore be considered a high-priority extension.

Possible forms require discussion before implementation, e.g.:

- randomly sampled market exposure with matching exposure percentage,
- deterministic proportional buy-and-hold exposure,
- benchmark invested only during the strategy's actual exposure intervals.

Do not choose a benchmark after seeing which version makes strategies look strongest.

---

# 17. Metrics

For true regime-gated backtests store at minimum:

```text
total_return
CAGR
max_drawdown
Sharpe
Sortino
Calmar
profit_factor
trade_count
win_rate
average_trade
median_trade
exposure
average_trade_duration
```

Also compute:

```text
excess_return_vs_full_bh
excess_return_vs_regime_bh
maxdd_vs_benchmark
episode_win_rate
number_of_regime_episodes
```

Do not rely on a single composite score.

---

# 18. Define specialist strategies

A specialist should not be selected by maximum return alone.

Report a transparent multi-metric profile including:

- return,
- excess return vs appropriate benchmark,
- max drawdown,
- Sortino / Calmar,
- trade count,
- exposure,
- number of independent regime episodes,
- episode consistency,
- cost sensitivity.

Examples of desired rankings:

```text
Best BTC Bull specialist
Best BTC Bear specialist
Best Sideways specialist
Best BTC Bull + Coin Bull specialist
Best BTC Bear + Coin Bull relative-strength specialist
Best BTC Bear + Coin Bear defensive specialist
```

Minimum trade/episode requirements should be discussed and frozen before final ranking.

---

# 19. Define universal strategies

Universal strategies are not necessarily top-return strategies.

They should have no catastrophic regime.

Create a regime fingerprint and explicitly report:

```text
worst_regime_return
worst_regime_drawdown
worst_regime_sortino
median_regime_excess_return
regime_consistency
```

A maximin-style interpretation is useful:

> Prefer strategies whose weakest regime is still tolerable.

Do not collapse the whole decision into one opaque score unless the weighting is separately preregistered.

---

# 20. Discovery versus locked validation

This is essential because hundreds of strategies × many regimes create major data-snooping risk.

A proposed split is:

```text
Discovery:
2020-03-01 ... 2023-12-31

Locked validation:
2024-01-01 ... 2026-08-20
```

This exact split is a proposal, not yet immutable in version 0.3.

Before running the first regime-performance sweep, create:

```text
REGIME_PREREGISTRATION.md
```

and freeze:

- population definition,
- primary DMI/ADX rules,
- discovery/validation dates,
- ranking requirements,
- benchmark definitions,
- primary endpoint(s).

After discovery, create a hashed selection manifest:

```text
selection_manifest.json
```

The validation stage must not permit silent replacement of failed candidates.

---

# 21. Multiple testing and duplicated strategy families

The repository already notes strong dependency / duplication across public strategies.

Do not treat copied strategies as independent confirmations.

Retain all rows for transparency but identify copy families.

Report multiplicity-aware statistics where inferential tests are used.

The existing audit reports both Benjamini-Hochberg and Benjamini-Yekutieli because dependency among strategies is substantial; reuse existing infrastructure where appropriate rather than inventing a separate multiplicity framework without reason.

---

# 22. Sensitivity analyses — only after primary results are locked

After the primary DMI/ADX analysis is complete, allowed secondary investigations can include:

## 22.1 ADX threshold sensitivity

```text
ADX trend threshold = 20 / 25 / 30
```

Primary remains whatever was preregistered.

## 22.2 Signed Efficiency Ratio robustness

Test whether strategy specialization persists as signed efficiency increases/decreases.

If categorical SER thresholds are preregistered, reproduce the specialist tables under those states.

## 22.3 Return / volatility robustness

Repeat major conclusions under the 90-day-return classifier and volatility strata.

## 22.4 EMA comparison

Optional later comparison with simple EMA trend structure.

## 22.5 HMM / unsupervised regime models

Deferred until after rule-based findings exist.

If eventually used, implement walk-forward / filtering only; do not retrospectively smooth historical states with future data.

---

# 23. Tests that must exist before full compute

## 23.1 Causality test

Modify all future OHLCV after date `T`.

All regime features and labels available on or before `T` must remain unchanged.

## 23.2 One-day lag test

Daily candle `D` cannot influence trades before `D+1`.

## 23.3 Synthetic DMI/ADX tests

- clean uptrend -> predominantly BULL after warmup,
- clean downtrend -> predominantly BEAR,
- oscillating range -> predominantly SIDEWAYS / low ADX.

## 23.4 Strategy integrity test

Hash original strategy files before and after the sweep. They must be identical.

## 23.5 Baseline regression test

Adding regime infrastructure must not change existing ungated Freqtrade results.

## 23.6 Reproducibility test

Same inputs + same code + same Freqtrade version must produce identical regime files and backtest summaries within expected deterministic tolerance.

---

# 24. Proposed repository structure

Prefer additions such as:

```text
regime/
    __init__.py
    regime_engine.py
    features.py
    episodes.py
    gate_adapter.py
    strategy_taxonomy.py
    attribution.py
    benchmarks.py
    ranking.py
    validation.py

results/regime/
    regime_daily.csv
    regime_episodes.csv
    regime_eligibility.csv
    strategy_taxonomy.csv
    trade_regime_attribution.csv
    strategy_btc_regime_summary.csv
    strategy_regime_summary.csv
    regime_gated_backtests.csv
    regime_benchmarks.csv
    specialists.csv
    universal_strategies.csv
    strategy_regime_fingerprints.csv
    selection_manifest.json
    validation_results.csv

REGIME_PREREGISTRATION.md
REGIME_ANALYSIS.md
REGIME_AUDIT_PLAN.md
```

Adapt names to the existing repository conventions rather than forcing this exact tree if it clashes with current design.

---

# 25. Implementation order for Codex

Do not begin with the full corpus backtest.

## Stage 1 — repository understanding

1. Inspect repository architecture.
2. Reproduce the current published audit locally if feasible.
3. Identify reusable loaders, Freqtrade invocation code, result parsers, bias fields, and duplicate-family logic.
4. Document any discrepancy between this plan and the current repository.

## Stage 2 — preregistration draft

5. Create `REGIME_PREREGISTRATION.md` from the frozen sections of this plan.
6. Leave explicitly unresolved decisions marked `OPEN` rather than silently deciding them.
7. Do not execute performance ranking until open primary decisions are resolved.

## Stage 3 — feature engine

8. Implement daily DMI/ADX for BTC and coins.
9. Implement one-day availability lag.
10. Implement SER(30).
11. Implement 30d/90d returns.
12. Implement 30d realized volatility.
13. Implement relative strength vs BTC.
14. Implement DMI spread and optional breadth descriptors.
15. Write causal unit tests.

## Stage 4 — validate regime data

16. Generate regime data for BTC and the eight requested pairs.
17. Produce summary statistics:
    - time in each regime,
    - number and duration of episodes,
    - transition counts,
    - feature distributions.
18. Visually inspect a small number of timelines only as a sanity check, not as a reason to tune thresholds.

## Stage 5 — strategy taxonomy

19. Build the canonical strategy manifest without double-counting repaired overlays.
20. Classify execution profiles (`spot`, `futures`, `long`, `short`, `both`) and store author intent, static capability, observed trades, evidence, and uncertainty separately.
21. Validate ambiguous profiles with mode-correct load and smoke runs.
22. Create deterministic source-code archetype taxonomy.
23. Store evidence and confidence.
24. Never exclude based on either taxonomy.

## Stage 6 — regime eligibility

25. **Implemented:** build `regime_eligible` by `strategy_id × run_profile` from technical audit fields.
26. **Implemented:** produce row-level exclusion and pending reasons in `REGIME_ELIGIBILITY.csv` and the summary in `REGIME_ELIGIBILITY.md`.
27. **Implemented:** do not use whole-window profitability/significance as eligibility gates.
28. **Coverage implemented:** `REGIME_COVERAGE.csv` records exact frozen-window pair/candle checks; before Stage 7, complete the remaining native-profile coverage and canonical bias diagnostics, then regenerate eligibility without changing its rules.

## Stage 7 — Phase A attribution

25. Annotate every trade with the causal regime features available at entry.
26. Produce BTC-only and BTC×coin performance summaries.
27. Produce episode-level consistency statistics.
28. Do not yet claim that regime gating improves portfolio performance.

**Implementation status:** complete. All canonical pooled trades are annotated
with every causal state available at entry; BTC-only, BTC x coin, and episode
summaries are separate, and Phase A remains descriptive.

## Stage 8 — regime-gate adapter

29. Implement entry-only gating outside original strategy files.
30. Confirm ungated wrapper exactly reproduces original results.
31. Test on 5–10 diverse strategies before scaling.

## Stage 9 — discovery sweep

32. Run Model 0 / Model 1 / Model 2 on the discovery period.
33. Compute full, regime-gated, and cash benchmarks.
34. Include exposure metrics.
35. Rank specialists and universal candidates using preregistered criteria.

## Stage 10 — lock selection

36. Write and hash `selection_manifest.json`.
37. Record code version, data fingerprints, Freqtrade version, and parameter definitions.

## Stage 11 — validation

38. Run the locked candidates on validation data.
39. Do not substitute failed candidates.
40. Report effect sizes, drawdowns, consistency, and benchmark excess returns.

## Stage 12 — robustness and exploratory analysis

41. Signed ER analysis.
42. Return / volatility analysis.
43. ADX sensitivity.
44. Behavioral clustering.
45. EMA or HMM only if still justified.

---

# 26. Primary questions the final analysis should answer

The final `REGIME_ANALYSIS.md` should explicitly answer:

1. Does strategy performance materially differ across DMI/ADX-defined BTC regimes?
2. Does individual coin state add predictive / selection value beyond BTC regime?
3. Which strategies are robust bull specialists?
4. Which strategies are robust bear / defensive specialists?
5. Which strategies work in sideways markets?
6. Are there repeatable BTC-bear / coin-bull relative-strength opportunities?
7. Which strategies are robust universal candidates?
8. Do findings survive multiple independent regime concepts, especially signed efficiency and rolling-return classifications?
9. Are apparent bear-market successes simply low exposure / cash behavior?
10. Does regime-aware gating improve risk-adjusted performance over the original strategy and over appropriate benchmarks?
11. Do source-code archetypes match observed behavioral archetypes?
12. Are conclusions stable across independent market episodes rather than driven by one cycle?

---

# 27. Reporting taxonomy

Every finding should be labeled one of:

```text
PRIMARY
VALIDATION
ROBUSTNESS
SENSITIVITY
EXPLORATORY
```

Never present exploratory behavioral clustering or post-hoc threshold tuning as if it were a primary preregistered result.

---

# 28. Key methodological cautions

## 28.1 Do not confuse trade attribution with gated performance

A trade entered during a bull regime performing well does not prove that turning the strategy on only during bull regimes improves the portfolio.

Phase B is required.

## 28.2 Do not confuse avoiding a bear market with alpha

A low-exposure spot strategy can outperform buy-and-hold during a crash by simply holding cash.

Report exposure and appropriate benchmarks.

## 28.3 Do not tune the regime labels to make strategies look specialized

The classifier must be decided before the strategy-performance table is inspected.

## 28.4 Do not count duplicated strategy code as independent replication

Use copy-family metadata.

## 28.5 Do not use future candles in state classification

Every feature must be live-computable at the time it is used.

## 28.6 Do not let taxonomy become a prior exclusion rule

The hypothesis `mean reversion works in sideways markets` is something to test, not something to enforce.

---

# 29. Discussion questions for other AI reviewers

Other AI sessions should review and challenge at least these points before the primary run:

### A. Regime eligibility

What exact combination of existing look-ahead, recursive, trap, and coverage fields should define `regime_eligible` across the broad 456-trading-strategy pool?

### B. Discovery / validation split

Is `2020-03-01 ... 2023-12-31` vs `2024-01-01 ... 2026-08-20` statistically adequate, or would an episode-aware split be better?

### C. Minimum evidence for specialist status

What minimum number of trades and independent episodes should be required?

### D. Exposure-matched benchmark

What benchmark most fairly separates genuine timing/selection alpha from simply holding cash?

### E. Efficiency Ratio

Should SER remain continuous or receive preregistered categories? If categorical, what non-data-mined threshold rule is defensible?

### F. Return classifier

Are ±20% over 90 days acceptable fixed crypto thresholds, or should the return classifier use a different preregistered definition?

### G. Volatility

Should volatility remain descriptive in version 1, or should high-vol/crash become a formal second regime dimension?

### H. Coin universe / breadth

Should breadth use only the eight audit pairs or a broader survivorship-aware crypto universe?

### I. Exit on regime change

Primary proposal is entry-only gating. Should forced exit be included as a later sensitivity test?

### J. Portfolio-level selection

After individual strategy/regime results exist, how should capital be allocated if multiple coins and strategies qualify simultaneously?

No reviewer should resolve these questions by inspecting which answer produces the best historical performance.

---

# 30. Decision / Discussion Log

Use this section for future AI sessions.

## Decision 0.3-01 — Primary classifier

**Status:** proposed to freeze before first regime-performance run
**Decision:** DMI(14)/ADX(14), daily, BTC + individual coin, states BULL/BEAR/SIDEWAYS/TRANSITION.
**Reason:** simple, deterministic, interpretable, direction and trend-strength separated.

## Decision 0.3-02 — Efficiency Ratio

**Status:** included, classification thresholds still open
**Decision:** compute Signed Kaufman Efficiency Ratio with proposed 30-day lookback for all dates and pairs. Use as robustness variable even if no categorical SER regime is chosen.
**Reason:** independent measure of directional efficiency / chop.

## Decision 0.3-03 — Return / volatility model

**Status:** included, categorical thresholds still discussion draft
**Decision:** compute 30d/90d returns and 30d realized volatility for BTC and coins. Candidate directional robustness classifier is ±20% 90d return.
**Reason:** maximally understandable independent benchmark model.

## Decision 0.3-04 — Strategy classification

**Status:** proposed
**Decision:** source-code taxonomy before results; behavioral clustering only after results; taxonomy never restricts eligible regime cells.
**Reason:** avoids circular confirmation of strategy archetype hypotheses.

## Decision 0.3-05 — BTC versus coin

**Status:** proposed
**Decision:** hierarchical model: BTC defines global regime; each coin defines local state; compare BTC-only versus BTC+coin gating empirically.
**Reason:** preserves systemic crypto context while allowing relative/local behavior.

## Decision 0.3-06 — HMM

**Status:** deferred
**Decision:** do not use HMM in version 1.
**Reason:** first analysis should be simple and investigator-auditable. HMM may be revisited after initial results.

## Decision 0.3-07 — Existing whole-window gates

**Status:** proposed
**Decision:** do not use whole-window economic profitability/significance gates to define regime eligibility. Build a technical `regime_eligible` field by canonical strategy and run profile.
**Reason:** specialist strategies may be poor globally but useful conditionally.

## Decision 0.4-01 — Population and repair compromise

**Status:** superseded by Decision 0.5-01
**Historical decision (superseded):** use exactly two populations, `original` and `repaired`.
Class 1/Class 2 remain repair-provenance fields. `regime_eligible` is an
eligibility flag within both populations, and FreqAI is a `run_class`, not an
additional population. Results marked `behavior_changed` remain visible in the
repaired population but are excluded from equivalence sensitivity analyses.
**Reason:** this preserves a simple comparison without concealing how strongly
an implementation was repaired. The provenance distinction remains mandatory,
but the requirement to split it into separate primary populations is retired.

## Decision 0.5-01 — Canonical pooled corpus and execution profiles

**Status:** adopted
**Timing:** before regime-performance ranking
**Class:** methodological
**Decision:** analyze one deduplicated canonical corpus. `original` and
`repaired` remain provenance values and mandatory sensitivity strata, but do
not split the primary analysis. Select at most one canonical implementation per
`strategy_id` and run profile. Classify and test strategies under the native
profiles `spot_long`, `futures_long`, `futures_short`, or
`futures_long_short`; preserve uncertainty and observed direction separately.
Cluster primarily within run profile and never duplicate original/repaired
implementations as independent strategies.
**Reason:** maximize usable coverage without allowing compatibility repair or
duplicate implementations to inflate evidence. Spot and futures mechanics and
available histories differ, so pooling implementations is valid while pooling
unstandardized run profiles is not.

## Decision 0.6-01 — Technical regime eligibility

**Status:** adopted and implemented
**Timing:** before regime-performance ranking
**Class:** methodological
**Decision:** `regime_eligible=true` requires a canonical implementation
measured in its native mode, trades in a full measurement, PASS for look-ahead
and recursive-bias diagnostics, PASS for exact pair/candle coverage of the
frozen regime window, no published technical trap, and no `behavior_changed`
repair. A zero-trade smoke remains pending until a full window is run.
`output_equivalent` repairs require canonical bias reruns.
Historical spot PASS values are not inherited by futures profiles. Missing
evidence is `pending_diagnostics`, never an implicit PASS or FAIL. Profit,
significance, market comparison, taxonomy, and cluster membership are excluded
from the rule.
**Current snapshot:** 31 eligible, 113 pending diagnostics, 756 ineligible
across 900 native `strategy_id × run_profile` rows. The coverage inventory
passes 820 rows and leaves 80 pending. These counts are generated, not frozen
constants.
**Reason:** admit every technically trustworthy strategy without repeating the
old whole-window economic survivor funnel or rewarding strategies whose bias
checks simply never ran.

## Decision 0.7-01 — Native candle-coverage gate

**Status:** adopted and implemented
**Timing:** before regime-performance ranking
**Class:** methodological
**Decision:** freeze the Stage 6 coverage window at 2020-03-01 00:00 UTC through
2026-08-21 00:00 UTC exclusive. Require every native-profile pair/timeframe
file to cover its documented available history, contain monotonic unique
timestamps, and have no pair-specific interior gaps. Exchange-wide gaps shared
by every active pair are recorded but accepted. The documented XMR/USDT
delisting boundary is available-history metadata, not fabricated missing data.
Missing files and unresolved timeframes remain `PENDING`, never `PASS` or a
permanent strategy exclusion.
**Current snapshot:** 820 PASS and 80 PENDING coverage rows. Raw candles remain
ignored; the versioned CSV stores temporal evidence and a source fingerprint.
**Reason:** preserve the original pair-available-history design while making
changing basket composition and local data incompleteness explicit.

## Decision 0.7-02 — Canonical native-mode bias reruns

**Status:** adopted and in progress
**Timing:** before regime-performance ranking
**Class:** methodological
**Decision:** store canonical look-ahead and recursive reruns separately from
the historical ledger in `PROFILE_BIAS.json`, bound to canonical source,
effective config, mode, timerange, and output hashes. Spot may retain a valid
historical diagnostic for an unchanged canonical implementation. Futures may
retain historical FOUND as disqualifying evidence but never inherit a spot
PASS. A short diagnostic window may expand to the frozen full window when the
look-ahead analyzer sees too few trades; the fallback is time-bounded and
resumable. Zero-trade smokes and unresolved coverage are handled before bias
runs rather than monopolizing the queue.
**Current snapshot:** thirty-seven canonical records produced. `MacdStrategy`, `SMAOG`,
and futures `RegimeFilterStrategy` newly satisfy eligibility; `Dimond` and
futures-short `AdxSmasS` are excluded by native recursive findings;
`FTT_DWT_FBB_FUTURES` passes native look-ahead analysis but is excluded by
reproducible recursive drift in `fisher_rsi` and `fisher_wr`. Its copied RMI
helper was repaired as Class 1 after the original recursive run exposed a
current-pandas datetime fill incompatibility; that compatibility repair is
separate from the subsequent bias finding.

## Decision 0.8-01 — Pinned Linux diagnostic runtime

**Status:** adopted and implemented
**Timing:** after Windows infrastructure failure, before further bias results
**Class:** operational reproducibility; no strategy or selection-rule change
**Decision:** run the remaining native bias diagnostics in the versioned
`Dockerfile.audit` runtime when Windows Smart App Control blocks unsigned PyPI
DLLs. The image pins Freqtrade 2026.7 and the same NumPy, pandas, SciPy, TA-Lib,
and non-FreqAI optional strategy dependencies as the original audit
environment. The
repository is mounted read/write so raw ignored candles are reused, while
`profile_bias.py` records the container image ID with each new diagnostic.
The global Class 1 compatibility aliases are activated through the versioned
`repair/sitecustomize.py` in every subprocess. `profile_bias_docker.ps1`
rebuilds and launches this runtime.
**Validation:** FTT first reproduced its old RMI failure boundary, then passed
look-ahead analysis after the already classified Class 1 repairs were present.
The fully fingerprinted recursive rerun found drift of -0.048 percent in
`fisher_rsi` and -0.027 percent in `fisher_wr`, both above the preregistered
0.01-percent tolerance. One- and two-thread OpenBLAS sensitivity reruns
reproduced both values exactly to three decimal places. Stage 6 consequently
moved from 25/144/731 to
25 eligible, 143 pending, and 732 ineligible.
**Reason:** retain Smart App Control and avoid unsupported per-file bypasses
while keeping the numerical audit stack fixed and reproducible.

## Decision 0.9-01 — First controlled futures bias batch

**Status:** completed
**Timing:** after the pinned runtime validation, before further batch expansion
**Class:** measurement checkpoint; no methodology or strategy change
**Decision:** process native futures diagnostics in five-strategy checkpoints
before increasing batch size. The first batch covered `MACDRS`, `MACDRL`,
`ZaratustraDCA2_06`, `DWT_LongShort`, and `DWT_short`. All five passed
look-ahead analysis and produced native recursive findings. The two MACD
strategies declare `startup_candle_count=0`; choosing a replacement would be
strategy authorship, so no repair is made. Zaratustra and both DWT variants
show indicator drift above the preregistered tolerance. The DWT strategies
loaded successfully through their strict-equivalent source overlays and Class
1 helper repairs, separating repair success from bias eligibility.
**Current snapshot:** 25 eligible, 138 pending diagnostics, and 737 ineligible.
**Reason:** confirm that the Docker runtime and compatibility overlays remain
stable on a mixed original/repaired futures batch before wider execution.

## Decision 0.10-01 — Second controlled futures bias batch

**Status:** completed
**Timing:** after the first five-strategy checkpoint
**Class:** measurement and environment-parity checkpoint; no selection-rule
change
**Decision:** add the non-FreqAI optional packages already present in the
original Windows audit environment to `requirements-audit-runtime.txt`, then
rerun the second five-strategy futures batch in one fingerprinted image.
`FastSupertrend_ts_origstop_fix`, `momentum`, `momentum_rsi`, and
`momentum_wick` pass both native bias gates and become eligible. `ToTheMoon`
initially failed resolver discovery because `ephem` was absent from the Linux
runtime; after restoring the same `ephem==4.2.1` dependency used by the Windows
audit, look-ahead passes and recursive analysis refuses the author's
`startup_candle_count=0`. No start value is invented, so `ToTheMoon` is
excluded by the existing recursive rule.
**Current snapshot:** 29 eligible, 133 pending diagnostics, and 738 ineligible.
**Reason:** preserve environment parity while keeping dependency repair
separate from the subsequent strategy-level eligibility result.

## Decision 0.11-01 — Third controlled futures bias batch

**Status:** completed
**Timing:** after the second five-strategy checkpoint
**Class:** measurement and reporting checkpoint; no selection-rule or strategy
change
**Decision:** process `RsiquiV2`, `RsiquiV5`, `TrendFollowingStrategy`,
`VolatilitySystemV2`, and `ZaratustraDCA2_07` in the same fingerprinted native
futures runtime. Both Rsiqui variants produce genuine look-ahead findings:
Freqtrade identifies `rsi_gra`, plus strategy-specific entry or exit columns,
as biased even though its separate biased-entry and biased-exit counters are
zero. The result parser now records those indicator columns and preserves raw
logs for positive findings; this is an evidence-detail change, not a change to
the gate. Both Rsiqui variants, `TrendFollowingStrategy`, and
`VolatilitySystemV2` also declare `startup_candle_count=0`, which recursive
analysis refuses; under Decision 0.6-01, a refused diagnostic is not a PASS and
therefore cannot establish eligibility. It is not relabelled as look-ahead
bias. `ZaratustraDCA2_07` passes look-ahead analysis but produces
recursive drift above tolerance in ATR and DMI-family indicators. No source or
startup value is changed because doing so would alter strategy behavior.
**Current snapshot:** 29 eligible, 128 pending diagnostics, and 743 ineligible.
**Reason:** retain reproducible positive evidence and avoid mistaking zero
summary counters for an unbiased result when Freqtrade reports biased columns.
The five status transitions result from newly completed diagnostics; the
parser detail change does not alter any PASS/FOUND status.

## Decision 0.12-01 — Fourth controlled futures bias batch

**Status:** completed
**Timing:** after the third five-strategy checkpoint
**Class:** measurement checkpoint; no selection-rule or strategy change
**Decision:** process `ZaratustraDCA5`, `BinHV27_short`, `ConsensusShort`,
`FakeoutStrategy`, and `AlmgrenChrissStrategy` in the same fingerprinted native
futures runtime. `ZaratustraDCA5` passes look-ahead analysis but recursive
analysis refuses its authored `startup_candle_count=0`. The output-equivalent
Class 2 `BinHV27_short` overlay produces recursive drift of 63370.607 percent
in `trend`; its look-ahead fallback over the full window is externally killed
with process status -9 and remains `NA`, not a fabricated PASS or finding.
`ConsensusShort` passes look-ahead analysis and produces recursive drift in
`consensus_buy` and `rmi`. The strict-equivalent Class 2 `FakeoutStrategy`
overlay produces look-ahead findings in its peak and entry columns, while its
zero startup count also prevents a recursive PASS. `AlmgrenChrissStrategy`
passes look-ahead analysis and produces recursive drift in `rsi` and `kappa`.
Each strategy has at least one native finding, so the inconclusive
`BinHV27_short` look-ahead result does not leave that strategy pending under
the unchanged eligibility rule. No compatibility or source repair is needed.
**Current snapshot:** 29 eligible, 123 pending diagnostics, and 748 ineligible.
**Reason:** measure repaired and original strategies under identical gates,
while preserving an infrastructure-limited diagnostic as inconclusive.

## Decision 0.13-01 — Fifth controlled futures bias batch

**Status:** completed
**Timing:** after the fourth five-strategy checkpoint
**Class:** measurement checkpoint; no selection-rule or strategy change
**Decision:** process `TWAPStrategy`, `FAdxSmaStrategy`,
`FReinforcedStrategy`, `FSampleStrategy`, and `FSupertrendStrategy` in the same
fingerprinted native futures runtime. `FAdxSmaStrategy` and the futures-long
`FSupertrendStrategy` pass both native bias gates and become eligible.
`TWAPStrategy` passes look-ahead analysis but produces recursive `rsi` drift.
The strict-equivalent Class 2 `FReinforcedStrategy` overlay passes look-ahead
analysis but produces recursive drift in its Bollinger bands.
`FSampleStrategy` passes look-ahead analysis but produces recursive drift in
`adx`, `rsi`, `sar`, and `tema`. The repaired implementation is therefore
measured under the same gate without its provenance either excluding or
favoring it.
**Current snapshot:** 31 eligible, 118 pending diagnostics, and 751 ineligible.
**Reason:** continue profile-balanced measurement and confirm that a
futures-long strategy can enter the shared canonical corpus while remaining a
distinct run profile for later analysis.

## Decision 0.14-01 — Sixth controlled futures bias batch

**Status:** completed
**Timing:** after the fifth five-strategy checkpoint
**Class:** measurement and repair-boundary checkpoint; no selection-rule or
strategy change
**Decision:** process `HurstCycleV5`, `IchiVwapAdx`, `NOTankAi_17`,
`NOTankAi_19`, and `haGradient` in the same fingerprinted native futures
runtime. `IchiVwapAdx` produces both Chikou-related look-ahead findings and
recursive drift. Both NOTank variants produce look-ahead findings in adaptive
RSI and signal columns plus large recursive drift in their oscillator and
threshold means. `HurstCycleV5` cannot complete look-ahead analysis because
`pandas_ta` returns no RSI for an intentionally short analyzer slice and the
source performs arithmetic on that value; its authored zero startup count
independently prevents a recursive PASS, so it is ineligible. `haGradient`
explicitly requires 120 FFT samples while declaring only 20 startup candles;
the look-ahead and recursive analyzers reach 102- and 31-row partial histories
and the source deliberately raises. Substituting NaN/no-signal behavior or
changing either startup value can reach a trading decision, so neither case
meets the file-specific equivalence proof required for Class 2. No repair is
invented. `haGradient` therefore remains pending with both diagnostics `NA`.
**Current snapshot:** 31 eligible, 114 pending diagnostics, and 755 ineligible.
The directly runnable futures bias queue is exhausted. Five other futures
profiles first require their preregistered full-window zero-trade measurement;
`haGradient` retains the documented source/analyzer incompatibility.
**Reason:** maximize measured coverage without weakening the repair standard
or treating an analyzer exception as a PASS or bias finding.

## Decision 0.15-01 — Separate full-window trade evidence

**Status:** implemented and calibration started
**Timing:** after exhausting the directly runnable futures bias queue, before
resolving zero-trade smoke profiles
**Class:** implementation and measurement checkpoint; no eligibility-rule or
strategy change
**Decision:** store full-window backtest evidence in
`PROFILE_FULL_WINDOW.json` rather than overwriting `PROFILE_SMOKE.json`.
`regime_eligibility.py` consumes a full-window result only when its canonical
source and effective runtime-config hashes match the current execution profile.
A measured positive trade count replaces zero-trade smoke evidence; a measured
zero becomes `no_trades_in_full_measurement`; failures and timeouts leave the
strategy pending. `profile_smoke_docker.ps1` binds each result to the pinned
container image. The first calibration runs `FOttStrategy` over
2020-03-01 through 2026-08-21 exclusive and reaches the fixed 1800-second
limit while remaining CPU-active. It is recorded as `timeout`, not as zero
trades or a strategy failure. The current eligibility snapshot therefore
remains 31 eligible, 114 pending diagnostics, and 755 ineligible.
**Reason:** keep short smoke evidence immutable, prevent mixed-window records,
and make expensive full-window measurements resumable without relaxing the
zero-trade gate.

## Decision 0.16-01 — FOtt pandas compatibility and linear recurrence

**Status:** completed
**Timing:** after the first full-window timeout exposed quadratic scaling and
before any regime-performance result
**Class:** implementation and measurement checkpoint; no eligibility-rule
change
**Decision:** add a strict-equivalent Class 2 overlay for `FOttStrategy`.
The source repeats two unused-variable whole-DataFrame loops once per candle,
which reaches the same shift-recursive fixed point at quadratic cost. The
overlay evaluates each recurrence once from left to right. It also replaces a
legacy chained `Series.iat` assignment whose write no longer reaches the
DataFrame under pandas 3 Copy-on-Write with the identical NumPy recurrence.
A dedicated verifier compares the overlay against emulated writable
pre-Copy-on-Write pandas semantics over rising, falling, and deterministic
random inputs at four lengths; all twelve cases match exactly. The 31-day
native smoke changes from the broken zero-trade execution to 82 long and 105
short trades. Eight pair-sharded full-window runs complete in approximately
121 to 131 seconds each and produce 6447 trades in total. Native look-ahead
analysis passes, but recursive analysis finds 12.616-percent drift in `ott`
and 4.950-percent drift in `var`; `FOttStrategy` is therefore ineligible under
the unchanged gate rather than remaining pending.
**Current snapshot:** 31 eligible, 113 pending diagnostics, and 756 ineligible.
**Reason:** restore the author's executable recurrence and make its full-window
measurement tractable without allowing a compatibility repair to bypass the
same bias diagnostics applied to originals.

## Decision 0.17-01 — Legacy timeframe evidence and remaining Stage 6 repairs

**Status:** implemented; remaining FreqAI diagnostics in progress
**Timing:** before regime-performance inspection or ranking
**Class:** implementation and measurement checkpoint; no eligibility-rule change
**Decision:** recognize an authored legacy `ticker_interval` as timeframe
metadata and normalize only unambiguous historical spellings (`Nhr` to `Nh`, a
bare integer to minutes) for candle selection. This does not promote runtime
status or edit an original strategy. Coverage consequently moves from 820 PASS
and 80 PENDING to 864 PASS and 36 PENDING. The remainder consists of genuinely
dynamic/missing configuration, an unavailable 5h series, one unknown test
artifact, and the already documented weekly source gaps.

The current-pandas chained inplace `ffill` failure in the strict-equivalent
Class 2 Breakout/Fakeout family is replaced in overlays by direct DataFrame
assignment. `BreakoutStrategy` then produces trades and native look-ahead and
recursive findings, so it is ineligible rather than pending. The same
mechanical rule changes the canonical hash of `FakeoutStrategy`; its older
positive bias record is deliberately invalidated and must be rerun. XGBoost
3.4.1 is restored to the pinned Linux runtime. TensorFlow has no Python 3.14
wheel for that image, so the two TensorFlow FreqAI full-window runs use the
otherwise version-matched Windows Python 3.13 audit environment and record that
runtime explicitly.

**Current snapshot:** 31 eligible, 112 pending diagnostics, and 757 ineligible.
`TSPredict` has already produced positive full-window trades while its remaining
pair shards continue; `tsp0chicken` follows in the same native runtime.
**Reason:** recover author-specified data intervals and executable compatibility
without confusing metadata, environment parity, or a repaired load with a bias
PASS.

## Decision 0.17-02 — Frozen causal feature engine and regime evidence

**Status:** Stages 2–4 implemented
**Timing:** before inspecting strategy-by-regime performance
**Class:** methodological freeze plus implementation
**Decision:** add `REGIME_PREREGISTRATION.md` and freeze the primary engine at
pinned TA-Lib Wilder DMI(14)/ADX(14), thresholds 20/25, four states, and a
one-completed-UTC-day availability lag. Calculate the same engine for BTC and
each of the eight audit coins. Store continuous SER(30), 30/90-day returns,
30-day annualized realized volatility, relative strength, DMI spreads, and
availability-aware eight-coin breadth without using them as primary gates.
Generated evidence contains 18,000 pair-days plus state summaries, 1,614
episodes, 64 transition edges, feature distributions, and fixed sanity
timelines. Its manifest binds all eight input feather files, all output tables,
and every frozen parameter by hash. Synthetic direction/range, future-mutation,
one-day-lag, key uniqueness, BTC-consistency, episode-partition, and output-hash
tests pass.
**Reason:** establish a transparent causal market-state layer before any
strategy outcome can influence thresholds or categories.

## Decision 0.17-03 — Phase A attribution boundary and entry-only adapter

**Status:** implemented and corpus evidence collection in progress
**Timing:** after feature freeze, before any strategy ranking
**Class:** implementation-only
**Decision:** attribute a trade exactly once using its entry timestamp's causal
`pair × UTC-day` state. Accept Phase A archives only when the embedded strategy
source hash, native spot/futures mode, and execution timeframe match the
canonical profile; retain the embedded config hash and label this evidence
descriptive rather than a locked validation run. Duplicate archive exports are
removed before the entry-date join. Install optional gating around Freqtrade's
`IStrategy.advise_entry`: first obtain the author's entry columns, then suppress
only disallowed `enter_long`/`enter_short` values. Original exits are never
changed, missing regime rows fail closed, and `ungated` returns the original
DataFrame unchanged. Exact trade-list integration checks across diverse native
profiles remain required before scaling gated runs.
**Reason:** separate descriptive attribution from causal gated performance and
implement the planned treatment without editing strategy sources.

## Decision 0.18-01 - Exhausted Stage 6 diagnostics and pooled Phase A runs

**Status:** Stage 6 complete; Stage 7 canonical pooled runs in progress
**Timing:** before inspecting strategy-by-regime performance or ranking
**Class:** implementation and measurement checkpoint; no eligibility-rule change
**Decision:** finish the native bias queue with one-file analyzer isolation,
author-helper paths at low precedence, and LF-stable generated config identity.
When the short look-ahead window contains too few trades, try the fixed
2020-01-01 through 2022-01-01 intermediate window before the frozen full
fallback. This is a diagnostic resource bound, not a result threshold or a
performance split. `BuyRegions` passes after restoring its author's adjacent
`utils` package as Class 1; `ElliotV5_SMA` passes in the intermediate window.
`Fakebuy` times out there after 900 seconds, and the other six unresolved rows
remain `pending_diagnostics`: one full-window process is killed with only 17
canonical trades, one authored trailing-stop relationship cannot be made valid
without changing exit behavior, two FFT strategies cannot process the
analyzer's partial histories without behavioral edits, and two portfolio
strategies remain below the analyzer's immutable minimum-trade requirement.
No `NA` is promoted to PASS or FAIL.

The final Stage 6 snapshot is 67 eligible, seven pending diagnostics, and 826
ineligible. Coverage is 864 PASS and 36 PENDING; every remaining coverage-only
gap belongs to a row already blocked by another gate. Stage 7 uses one pooled
native backtest per eligible strategy over the complete eight-pair universe;
pair-sharded runs are not accepted because they change shared capital and
`max_open_trades` mechanics. The five-profile ungated adapter equivalence suite
is complete with exact semantic trade-list hashes.
**Reason:** close every safely actionable technical gap while preserving
inconclusive evidence and ensure Phase A reflects the actual pooled execution
mechanics rather than a convenient sum of independent pair runs.

---

## Decision 0.19-01 - Complete canonical pooled Phase A attribution

**Status:** Stage 7 complete; Stage 9 blocked only on the frozen open choices
**Timing:** before inspecting strategy-by-regime performance or ranking
**Class:** implementation and measurement checkpoint; no methodology change
**Decision:** accept the complete identity-bound corpus of 67 pooled native
backtests over all eight pairs and the frozen `20200301-20260821` timerange.
The corpus contains 286,616 trades. Every trade has a causal BTC state; 285,613
also have a coin-local state. The remaining 1,003 are exclusively
`XMR/USDT:USDT` trades after the documented spot XMR delisting boundary. They
retain the available BTC state, remain excluded from BTC x coin cells, and are
not assigned an imputed local state.

`BuyRegions`, the final profile, was measured in a separate digest-pinned Linux
Python 3.12 image because the standard Freqtrade 2026.7 Python 3.14 image has no
TensorFlow 2.21 wheel and Windows Application Control blocks the former native
environment. Freqtrade and all frozen numerical package versions match; the
manifest records the image digest, and no strategy bytes or signals changed.
`trade_regime_attribution.csv`, `strategy_btc_regime_summary.csv`,
`strategy_regime_summary.csv`, `strategy_episode_summary.csv`, and
`attribution_manifest.json` are the Phase A evidence. The row-level CSV omits
only the redundant repeated archive path; the manifest retains the complete
verified strategy-to-archive mapping.
**Reason:** close Stage 7 with all preregistered profiles, preserve genuinely
unavailable local state rather than fabricating coverage, and keep BTC-only,
BTC x coin, and episode evidence distinct before any Stage 9 selection.

---

# 31. Change protocol

When this file is updated:

1. increment version number,
2. add a decision-log entry,
3. state whether change occurred:
   - before any relevant results,
   - after discovery but before validation,
   - after validation,
4. classify the change as:
   - methodological,
   - implementation-only,
   - reporting-only,
5. never overwrite history of a decision that was changed after data were observed,
6. preserve old versions in git history.

Suggested commit format:

```text
regime-plan: v0.4 clarify exposure benchmark before results
```

---

# 32. Immediate Codex task

A new Codex session should **not immediately run the full corpus**.

Its first deliverable should be a short repository-specific implementation proposal that answers:

1. Which existing files/functions can be reused?
2. How can daily regime data be injected without changing strategy source files?
3. Which existing ledger fields can define technical `regime_eligible` status for the broad corpus?
4. How will entry-only regime gating be implemented while preserving original exits?
5. How will ungated equivalence be tested?
6. Which open decisions in section 29 must be resolved before any strategy ranking is generated?

Only after this design review should implementation proceed.

---

# 33. One-paragraph handoff summary

The existing `Apex-prim/strategy-audit` tested 895 public Freqtrade strategy classes and found that whole-window economic conclusions are heavily affected by the market window; its own exploratory calendar-year split showed that strategies can appear weak against buy-and-hold in rising years and defensive in falling years, while low exposure complicates interpretation. The new project therefore asks a different question: whether strategy suitability is conditional on observable market regimes. Version 1 should use a transparent, causal DMI(14)/ADX(14) daily classifier applied separately to BTC and each coin, creating a global BTC regime plus local coin state. All technically trustworthy strategies should be evaluated across all states rather than pre-filtered by presumed archetype. Source-code taxonomy (mean reversion, momentum, breakout, hybrid, etc.) should be recorded before outcomes but used only for interpretation; behavioral clustering comes later. Signed Kaufman Efficiency Ratio and 90-day return plus 30-day realized volatility are explicitly included as independent robustness models. First attribute existing trades to regimes, then perform true entry-gated Freqtrade backtests, compare original vs BTC-only vs BTC+coin gating, use buy-and-hold, regime-gated buy-and-hold, cash, and ideally exposure-aware benchmarks, split discovery from locked validation, and report specialists as well as universal strategies without silently tuning regime rules after seeing results.
