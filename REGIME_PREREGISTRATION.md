# Regime audit preregistration

**Status:** binding for the regime study: scope and causal clock, the frozen DMI/ADX model, the four model
levels, the analysis order, the reporting safeguards, the six reporting phases, the nine former OPEN choices (all
decided, see the end of the file) and the confirmation rule of 2026-09-20. Frozen for feature generation and
attribution. The eligibility expansion amendment was accepted on 2026-08-30 before ranking; the 2026-09-07
gate-factor amendment was accepted before any productive gated run or candidate specification existed.

**What is not here any more.** The amendments that fixed the rules of the check chain (bias windows, smoke cascade,
warm-up convergence, closure and exclusion rules, E0's retirement) moved to `PIPELINE.md`, "Decision record", on
2026-09-20, unchanged. The table `Amendments that moved` below lists them by their old title.

**Current eligibility authority:** the 2026-09-03 retirement of E0 overrides
every earlier sentence in this file that called the 67-profile Stage 6 snapshot
eligible, confirmatory, untouched, or reportable beside E1. `E0_strict67` is an
archival provenance tag only. It is not a cohort, sensitivity population,
admission source, fallback, denominator, or benchmark result.

## Scope and causal clock

The canonical, deduplicated strategy corpus and its native run profiles are
defined by `evidence/EXECUTION_PROFILES.csv`. Technical admission is defined only by an
active `admitted_E1` decision in `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` under
the current audit rules, exposed as `cohort=E1_expanded` in
`STRATEGY_STATUS.csv`. `evidence/REGIME_ELIGIBILITY.csv` is the invalidated historical
Stage 6 snapshot and supplies provenance only. Whole-window profit is not an
admission rule.

The analysis window is 2020-04-01 00:00 UTC through 2026-08-21 00:00 UTC
(exclusive end), for spot and futures alike (owner, 2026-09-21; until then futures started on 2020-03-01,
see `PIPELINE.md`, Decision record). The regime indicators read the earlier candles as warm-up. A daily candle is usable only on the following UTC day. No
feature, label, gate, or attribution may use the still-open daily candle.

## Frozen eligibility expansion amendment, with E0 clauses superseded

The user authorized maximizing technically trustworthy strategy coverage on
2026-08-30, before any strategy-by-regime ranking was inspected. The complete
prospective protocol is frozen in `PIPELINE_EXTENSIONS.md`, Part 1.

The original amendment retained the completed 67-profile Stage 6 corpus as
`E0_strict67`. That clause is superseded by the 2026-09-03 finding below: the
67 had not all completed this audit's own check chain. E0 membership now grants
nothing. `E1_expanded_confirmatory` contains only deduplicated profiles with an
active row-level `admitted_E1` decision after the applicable current-runtime
measurement, look-ahead, convergence, coverage, trade, role, and repair checks.
This applies equally to former E0 members and every other strategy.

Recursive `FOUND` rows with exact decision-invariance evidence but no fresh
recursive `PASS` are `E2_drift_sensitivity`, never E1. Behavior-changing,
lookahead-rewritten, trap-corrected, or otherwise derived variants are
`E3_derived_exploratory` and cannot support confirmatory claims about the
published originals.

The candidate universe, repair boundary, identity/equivalence requirements,
resource attempts, and stop rule are fixed before expansion measurements. No
profit or regime outcome may select a repair, candidate, diagnostic window, or
stopping point. E1 and its hashes must be frozen before Stage 9 ranking.

E0 must not be reported as a confirmatory or sensitivity cohort. Its original
membership may appear only as provenance. Strategy copy families are dependence
clusters, with family-clustered or hierarchical uncertainty and an
equal-family-weight sensitivity. Where inferential multiplicity correction is
applicable, report both Benjamini-Hochberg and Benjamini-Yekutieli results.

## Frozen primary model

- Wilder-compatible DMI(14) and ADX(14), calculated independently for BTC and
  each audit coin.
- `BULL`: ADX >= 25 and +DI > -DI.
- `BEAR`: ADX >= 25 and -DI > +DI.
- `SIDEWAYS`: ADX < 20.
- `TRANSITION`: 20 <= ADX < 25.
- BTC is the global state; the traded coin is the local state. All 16 state
  combinations remain observable and none is removed post hoc.

## Frozen stored robustness variables

Store Signed Kaufman Efficiency Ratio over 30 completed daily bars, 30/90-day
returns, annualized 30-day realized log-return volatility, relative strength
against BTC, raw and normalized DMI spread, and breadth over the eight audit
pairs available on that day. These variables are descriptive until a rule below
is explicitly frozen; they do not alter the primary DMI/ADX labels.

## Analysis order

1. Attribute ungated trades to the state available at entry (Phase A).
2. Verify an ungated adapter reproduces the canonical baseline.
3. Compare original, BTC-entry-gated, coin-entry-gated, and
   BTC-plus-coin-entry-gated runs.
4. Lock candidate identities, rules, hashes, data fingerprints, and versions.
5. Evaluate the locked set once on validation; failed candidates are not replaced.
6. Run robustness, sensitivity, and behavioral clustering only after primary
   results and selection are locked.

Original exits remain authoritative. Forced exit at a regime change is not a
primary treatment.

## Amendment 2026-09-07: separate global and local gate effects

**Owner's decision**, recorded before any productive Model 1, Model 2, or
Model 3 run, before a candidate gate specification was frozen, and before any
gated performance was inspected.

The previously implemented Model 2 combined the global BTC state and the local
coin state with logical AND. That combination is retained, but reassigned to
Model 3. Model 2 is now pair-local and must not read, require, validate, or gate
on the BTC state:

- **Model 0:** original entries and exits, no regime gate.
- **Model 1:** original entry AND selected global BTC state.
- **Model 2:** original entry AND selected local coin state.
- **Model 3:** original entry AND selected global BTC state AND selected local
  coin state.

This is a factorial separation of the two observable gate dimensions. Model 1
measures the global gate alone, Model 2 the local gate alone, and Model 3 their
intersection. Model 3 must reuse exactly Model 1's BTC state lists and exactly
Model 2's coin state lists for the same candidate identity; otherwise the
incremental comparisons are not admitted.

BTC and coin states remain attached to every attributable trade in every
model. Recording a BTC state for a Model 2 trade is descriptive attribution,
not a BTC entry condition. Missing local evidence fails closed for Models 2
and 3; it does not close the global-only Model 1 gate. All gates remain
entry-only and original exits remain authoritative.

## Frozen reporting safeguards

- Report trade count, episode count, exposure, profit factor, expectancy,
  drawdown, return, and benchmark excess; do not equate cash exposure with alpha.
- Preserve run profile and repair provenance. Pool the canonical corpus but do
  not pool unstandardized spot/futures mechanics or duplicate code families as
  independent replications.
- Label every result `PRIMARY`, `VALIDATION`, `ROBUSTNESS`, `SENSITIVITY`, or
  `EXPLORATORY`.
- Phase-A attribution is descriptive and is never called gated performance.

## Amendments that moved

Moved verbatim to `PIPELINE.md`, "Decision record for Stages 0-8", where they are listed by date. A code comment or an
old transcript that cites one of these titles as being in this file means the entry of that title there.

| Title as it stood here | Date | Subject |
|---|---|---|
| Frozen warm-up convergence amendment | 2026-09-01 | Warm-up convergence ladder, acceptance rule and scope |
| Amendment 2026-09-02: the settled warm-up is the measurement | 2026-09-02 | The settled warm-up is the measurement; paired run no longer an admission gate |
| Amendment 2026-09-03: the spot analysis window starts a month later | 2026-09-03 | Spot analysis window starts 2020-04-01 |
| Amendment 2026-09-03: E0 is retired as a separate cohort | 2026-09-03 | E0 retired as a cohort |
| Amendment 2026-09-03: a second reader defect, corpus-wide | 2026-09-03 | Table parser and case-colliding log paths |
| Amendment 2026-09-09: three-month Futures recursion window | 2026-09-09 | Futures recursion window becomes three months |
| Amendment 2026-09-10: fixed smoke trade-count cascade | 2026-09-10 | Fixed smoke trade-count cascade |
| Amendment 2026-09-10: identical Spot and Futures bias windows | 2026-09-10 | Identical Spot and Futures bias windows |
| Amendment 2026-09-10: completed full backtest closes technical work | 2026-09-10 | Completed full backtest closes technical work |
| Amendment 2026-09-10: exclusions close the work queue | 2026-09-10 | Exclusions close the work queue |
| Amendment 2026-09-10: non-testable canonical full backtests are excluded | 2026-09-10 | Non-testable canonical full backtests are excluded (C10) |
| Amendment 2026-09-11: warm-up convergence precedes final recursive-bias | 2026-09-11 | Look-ahead, then warm-up ladder, then final recursive-bias |
| Amendment 2026-09-15: smoke cascade drops the one-year third rung | 2026-09-15 | Smoke cascade drops the one-year rung |
| Amendment 2026-09-16: the 'frozen file' description is dropped | 2026-09-16 | "Frozen file" description of REGIME_ELIGIBILITY.csv dropped |

## Amendment 2026-09-05: volatility becomes a reporting label, and the six phases

**Owner's decision**, resolving OPEN item 6 before any per-phase strategy
result was inspected. That order is the whole value of the decision: a
volatility cut chosen after seeing which strategies it flatters is not a
preregistered cut.

**The primary DMI/ADX model is untouched.** `BULL`, `BEAR`, `SIDEWAYS` and
`TRANSITION` keep their definitions, keep deciding attribution, and the
sixteen BTC-by-coin combinations remain observable. Nothing below changes a
single daily label the frozen model emits.

What changes is that annualized 30-day realized log-return volatility, until
now stored as descriptive only, becomes a **reporting** label alongside those
states. `SIDEWAYS` is the reason. It covers both a dead low-volatility drift
and a violent range that traverses its own width every other day, and those
two reward opposite machinery: a grid earns per traversal and earns almost
nothing in the first, while a cointegration pair holds in the first and breaks
in the second. Reporting both as one state averages a strategy's best phase
against its worst and calls the result no specialisation.

**The six reporting phases**, over `coin_realized_vol_30d`:

| Phase | Rule |
| --- | --- |
| `bull_trend` | ADX >= 25 and +DI > -DI |
| `bear_trend` | ADX >= 25 and -DI > +DI |
| `range_quiet` | ADX < 20 and vol < 0.623 |
| `range_choppy` | ADX < 20 and vol >= 0.623 |
| `transition` | 20 <= ADX < 25 |
| `high_vol_shock` | vol >= 1.291, whatever the DMI state |

`high_vol_shock` outranks the DMI label: a day in the top volatility decile is
that day's market, and reading it as an ordinary `BULL` puts a blow-off and a
steady rally in one bucket.

**Both thresholds are frozen as the numbers above, not as quantile rules.**
They were measured once over the frozen window in
`results/regime/regime_daily.csv` - 18000 pair-days - as the 90th percentile
of realized volatility over all pair-days and its median over `SIDEWAYS` days
alone. Stated as numbers because a quantile re-derived from a different slice
is a different cut wearing the same name. Over the frozen window they divide
the days 23.6 / 19.3 / 17.9 / 15.2 / 14.0 / 10.0 percent, so no phase is
starved of evidence.

Implemented in `market_phase_hypothesis.PHASES`, which also carries the
per-strategy prediction this split exists to make testable
(`evidence/MARKET_PHASE_HYPOTHESIS.json`, surfaced as `assumed_market_regime` in
`STRATEGY_STATUS.csv`). That prediction is not part of the frozen model and
decides nothing; it is written down now so the benchmark can refute it.

## Amendment 2026-09-11: the eight OPEN pre-Stage-9 choices are resolved

**Owner's decision**, recorded before any Model 1, Model 2, or Model 3 run,
before a candidate gate specification was written, and before any
strategy-by-regime performance was inspected - the same provenance guarantee
every other amendment in this document relies on. Reached by walking through
each entry of the `OPEN before Stage 9 ranking` list below in order, with a
recommendation checked against the corpus's own data (episode counts, return
distributions) where one was available, never against strategy performance.

1. **Discovery/validation split.** Frozen at the proposed calendar boundary:
   discovery `2020-04-01`-`2023-12-31` (`2020-03-01` until 2026-09-21), validation `2024-01-01` through the
   analysis window's end (`2026-08-21`). Reason: `REGIME_AUDIT_PLAN.md` §20's
   own concern - hundreds of strategies times many regimes is a large
   data-snooping surface - and no sharper boundary was proposed or checked
   against any outcome.

2. **Minimum trade/independent-episode evidence for specialist status.**
   Frozen at **5 independent regime episodes within the validation window**
   plus **10 trades total** across them, required together for a
   `VALIDATION`-tier specialist claim; short of either, the row is reported
   only as `EXPLORATORY`, never as a validated specialist. Reason: the
   corpus's own BTC episode counts in the validation window
   (`results/regime/regime_btc_episodes.csv`, `start >= 2024-01-01`) are
   BULL=15, BEAR=16, SIDEWAYS=20, TRANSITION=36 - a floor above roughly a
   third of the smallest of these would make a validated bull or bear
   specialist claim nearly unreachable for any strategy. The 10-trade figure
   is not new: it reuses the floor `STRATEGY_STATUS.csv`'s `too_few_trades`
   cohort already applies, freqtrade's own minimum for a look-ahead verdict.

3. **Exposure-matched benchmark construction.** Frozen as the third option
   `REGIME_AUDIT_PLAN.md` §16.4 lists: invested only during the strategy's
   own exposure intervals - for each trade, the coin's own buy-and-hold
   return over that same open-to-close interval, summed. Reason: deterministic
   and reproducible (no sampling seed, unlike "randomly sampled exposure"),
   and it answers the README's original concern precisely - what a passive
   holder would have earned during exactly the windows the strategy itself
   was in the market, not an arbitrary exposure-percentage abstraction.

4. **SER: continuous or categorical.** Frozen as continuous only - no
   preregistered SER categories in version 1. Reason: SER's role
   (`REGIME_AUDIT_PLAN.md` §6) is to check whether DMI/ADX findings survive
   under an independent trend concept, which a continuous comparison already
   answers (distribution-by-regime, monotonicity of specialist rankings).
   Manufacturing a second categorical regime from SER would only reopen the
   threshold-choice risk the plan itself warns against ("do not choose
   whichever method gives the nicest strategy rankings after the fact")
   without serving a need the continuous form does not already meet.

5. **90-day return classifier threshold.** Frozen at the proposed
   +/-20 percent. Reason: checked against the corpus's own BTC 90-day return
   distribution (`results/regime/regime_daily.csv`, 2,364 days) - 36 percent
   of days exceed +20 percent, 18 percent fall below -20 percent, 46 percent
   sit between, none of the three buckets empty or dominant, and the median
   (+6 percent) and interquartile range (-14 percent to +34 percent) place
   +/-20 percent well inside the natural spread rather than at a degenerate
   edge. This check used only price data, never a strategy's trades or
   returns.

6. Volatility as a reporting label - already decided 2026-09-05; unchanged
   here. See that amendment above.

7. **Breadth denominator.** Frozen as the eight-pair audit universe with an
   availability-aware denominator - the count of pairs with a valid daily
   candle that day, not a fixed 8. Reason: `XMR/USDT` has had no spot candles
   since its documented 2024-02-20 Binance delisting
   (`evidence/REGIME_COVERAGE.md`); a fixed denominator of 8 would silently
   depress every breadth reading after that date for a data-availability
   reason having nothing to do with actual market breadth. This mirrors the
   availability-aware handling `regime/attribution.py` already applies to
   the same gap rather than introducing a new rule for it.

8. **Forced exit on regime change.** Confirmed excluded from the primary
   entry-only gate model in version 1; may be examined later only as an
   explicitly labelled sensitivity test, never folded into Model 1/2/3
   themselves. Reason: this was already the plan's own draft position
   (`REGIME_AUDIT_PLAN.md` §14, "Forced regime exits may be examined later as
   a separate sensitivity test"), and keeping Model 1/2/3 to a single changed
   degree of freedom - which entries are permitted - is what makes their
   deltas against Model 0 and against each other attributable to the entry
   gate alone.

9. **Portfolio-level allocation across qualifying candidates.** Explicitly
   deferred, not decided, for version 1. Reason: the plan itself leaves this
   open with the same warning as every other entry here (do not resolve by
   which answer performs best), the existing runners
   (`regime/gated_backtest.py`, `regime/model_compare.py`) operate on one
   candidate at a time, not a capital-constrained portfolio, and per-strategy
   specialist/universal ranking already answers the question this round of
   work is for. Portfolio-level selection is a materially different problem
   - capital constraints, cross-strategy correlation, `max_open_trades`
   interaction - better scoped once it is visible how often multiple
   candidates qualify at once, which nothing in the corpus can show yet.

## Amendment 2026-09-20: confirmation across the discovery and validation windows, and a forward hold-out

**Owner's decision.** Timing: made *after* discovery and validation, with both windows'
results known, so it is a post-hoc reporting rule and is labelled as such. Classification:
reporting-only. It adds columns and changes no ranking, no floor, no tier and no
eligibility.

The evaluation labelled each trade `discovery` (opened before 2024-01-01) or `validation`
and then used only the validation trades. `regime/discovery_comparison.py` now runs the
same evaluation, floor and benchmark on the discovery trades and pairs the two results per
strategy, regime kind (BTC or coin) and phase. Two results are added on top of that pairing.

1. **Confirmed.** A strategy in a phase is *confirmed* when it clears the specialist floor
   (5 episodes and 10 trades) in **both** windows and the one-sided 95 % lower confidence
   bound of its episode excess return (`episode_excess_lcb`) is above 0 in **both**.
2. **Confirmation score.** The smaller of the two lower confidence bounds, the weakest link.
   It rewards being good in both windows. It does not reward similarity as such, so equally
   poor results give a negative score and no label.
3. **Universal candidates** (VALIDATION tier in all four coin phases). *Strict*: confirmed
   in all four phases. Where that does not hold, the *mild* rule applies: better than
   Buy-and-Hold in both windows (excess return above 0, floor in both) in at least three of
   the four phases. The label is the strongest rule that holds (`strict`, `mild`, `none`);
   the score of a universal candidate is the score of its weakest phase. The mild rule was
   added because the strict one left no universal candidate (0 of 404), which is a
   data-informed choice and is recorded as one.

The constants are `CONFIRM_LCB_MIN = 0` and `UNIVERSAL_MILD_PHASES = 3` in
`regime/discovery_comparison.py`. Both windows were known when they were chosen, so the
counts they produce say nothing about how well the rule predicts.

**Forward hold-out from 2026-08-21.** The analysis window ends at 2026-08-21 00:00 UTC. No
result in this audit uses data after that date. The rule above is frozen as of this
amendment; a later change to the thresholds or to the definition is a new amendment and
cannot be tested on the same forward window. To test it, extend the candle data and the
pooled backtests to a new end date, run the same evaluation on the window that starts at
2026-08-21, and compare, per phase, the share of confirmed strategies that beat
Buy-and-Hold in that window with the share of the strategies that were not confirmed. The
result is reported whichever way it falls. The window needs enough episodes to clear the
floor per phase, which is a matter of months, not weeks. Extending the analysis window is
a separate decision of the owner and is not made here.

## OPEN before Stage 9 ranking

The following choices are intentionally not inferred from strategy outcomes.
All nine are now resolved; see the amendment directly above for the decision
and reasoning behind each.

1. ~~Exact discovery/validation split (calendar proposal: discovery through
   2023-12-31, validation from 2024-01-01).~~ **DECIDED 2026-09-11**: frozen
   as proposed.
2. ~~Minimum trade and independent-episode evidence for specialist
   status.~~ **DECIDED 2026-09-11**: 5 validation-window episodes and 10
   trades, together, for `VALIDATION`-tier specialist status.
3. ~~Exact exposure-matched benchmark construction.~~ **DECIDED
   2026-09-11**: invested only during the strategy's own exposure intervals.
4. ~~Whether SER stays continuous or receives preregistered categories.~~
   **DECIDED 2026-09-11**: continuous only.
5. ~~Whether the 90-day return robustness classifier freezes at +/-20
   percent.~~ **DECIDED 2026-09-11**: yes, +/-20 percent.
6. ~~Whether volatility stays descriptive in version 1.~~ **DECIDED
   2026-09-05**: it becomes a reporting label at the two frozen thresholds,
   splitting `SIDEWAYS` and adding `high_vol_shock`. The primary DMI/ADX model
   is unchanged. See the amendment above.
7. ~~Whether breadth remains the eight-pair, availability-aware audit
   universe.~~ **DECIDED 2026-09-11**: yes, denominator is pairs with valid
   data that day, not a fixed 8.
8. ~~Whether forced exit is included only as a later sensitivity test.~~
   **DECIDED 2026-09-11**: yes, excluded from Model 1/2/3, sensitivity test
   only.
9. ~~Portfolio allocation when multiple strategy/pair candidates qualify.~~
   **DECIDED 2026-09-11**: explicitly deferred, out of scope for version 1.

No ranked discovery output may be generated while these entries remain `OPEN`.
All are now decided; a candidate spec and a productive Model 1/2/3 run may
proceed under the choices recorded above.
