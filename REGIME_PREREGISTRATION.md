# Regime audit preregistration

**Status:** frozen for feature generation and attribution; the eligibility
expansion amendment below was accepted on 2026-08-30 before ranking; choices
marked `OPEN` must be resolved before Stage 9 produces any ranked strategy table.

## Scope and causal clock

The canonical, deduplicated strategy corpus and its native run profiles are
defined by `EXECUTION_PROFILES.csv`. Technical admission is defined only by
`REGIME_ELIGIBILITY.csv`; whole-window profit is not an admission rule.

The analysis window is 2020-03-01 00:00 UTC through 2026-08-21 00:00 UTC
(exclusive end). A daily candle is usable only on the following UTC day. No
feature, label, gate, or attribution may use the still-open daily candle.

## Frozen eligibility expansion amendment

The user authorized maximizing technically trustworthy strategy coverage on
2026-08-30, before any strategy-by-regime ranking was inspected. The complete
prospective protocol is frozen in `ELIGIBILITY_EXPANSION_PLAN.md`.

The completed 67-profile Stage 6 corpus is retained as `E0_strict67` and must
be reported as a nested confirmatory sensitivity. A new
`E1_expanded_confirmatory` corpus may add deduplicated profiles only after a
predeclared equivalent repair or missing diagnostic is completed and every
original technical gate returns `PASS`. The eligibility thresholds themselves
are not relaxed.

Recursive `FOUND` rows with exact decision-invariance evidence but no fresh
recursive `PASS` are `E2_drift_sensitivity`, never E1. Behavior-changing,
lookahead-rewritten, trap-corrected, or otherwise derived variants are
`E3_derived_exploratory` and cannot support confirmatory claims about the
published originals.

The candidate universe, repair boundary, identity/equivalence requirements,
resource attempts, and stop rule are fixed before expansion measurements. No
profit or regime outcome may select a repair, candidate, diagnostic window, or
stopping point. E1 and its hashes must be frozen before Stage 9 ranking.

E0 and E1 are reported side by side. Strategy copy families are dependence
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
3. Compare original, BTC-entry-gated, and BTC-plus-coin-entry-gated runs.
4. Lock candidate identities, rules, hashes, data fingerprints, and versions.
5. Evaluate the locked set once on validation; failed candidates are not replaced.
6. Run robustness, sensitivity, and behavioral clustering only after primary
   results and selection are locked.

Original exits remain authoritative. Forced exit at a regime change is not a
primary treatment.

## Frozen reporting safeguards

- Report trade count, episode count, exposure, profit factor, expectancy,
  drawdown, return, and benchmark excess; do not equate cash exposure with alpha.
- Preserve run profile and repair provenance. Pool the canonical corpus but do
  not pool unstandardized spot/futures mechanics or duplicate code families as
  independent replications.
- Label every result `PRIMARY`, `VALIDATION`, `ROBUSTNESS`, `SENSITIVITY`, or
  `EXPLORATORY`.
- Phase-A attribution is descriptive and is never called gated performance.

## Frozen warm-up convergence amendment

Authorized by the owner on 2026-09-01, before any strategy-by-regime ranking
was generated or inspected. It governs a new admission route and changes
nothing about E0.

**The problem it solves.** The recursive gate asks whether an indicator's value
depends on how much history was loaded. Answering it requires a warm-up, and
the warm-up value used so far was the longest literal indicator period found in
the source. That heuristic is demonstrably wrong in three ways already
recorded: it read a minimum instead of a maximum (`Strategy004`), it carried a
period across timeframes without conversion (`Cluc4`, `BB_RPB_TSL`), and it
ignores that a recursively smoothed indicator never forgets its seed. Setting
the warm-up equal to the period leaves roughly `e^-2` of the seed for a
standard EMA and `e^-1` for Wilder smoothing - 13.5 and 36.8 percent. Measured
confirmation: `pmaxTest` with warm-up 112 still drifts 4.5 percent on `rsi_112`.

**The rule, fixed here before it is run.**

1. Ladder, in calendar days: 1, 2, 7, 14, 30, 90, 365, converted to candles
   through the strategy's own timeframe and capped at the candles actually
   available before the frozen window start for that pair basket. Days rather
   than multiples of the file-derived period, because that period is the thing
   that keeps being wrong; a ladder anchored to it inherits its errors, while a
   day is the same span of market history for every strategy. The ladder
   reaches a year because 30 days is 30 candles at a daily timeframe and cannot
   settle an EMA200. Rungs that collapse onto the same candle count are not run
   twice.
2. Acceptance: freqtrade `recursive-analysis` reports no indicator whose
   absolute drift reaches **1.0 percent**.
3. The chosen value is the smallest rung at which that rung AND every larger
   rung in the table stay inside the band. Not the first crossing: a drift
   curve does not fall monotonically. `SmaRsiStrategy` reports 0.588 percent
   for `rsi` at 14 candles, then 4.262 at 25 and 1.718 at 30 before settling
   near zero at 90. Taking the first value under the band would pick 14, where
   the indicator is plainly not settled; convergence means it stays settled.
   Among the rungs that qualify, the one with the smallest worst-case drift is
   taken, and an exact tie keeps the smaller warm-up. Every candidate has
   already cleared the band at its own value and at every larger one, so this
   choice cannot pass or fail a row; it only selects the warm-up at which the
   indicators are most settled. Choosing the smallest drift across ALL rungs,
   qualifying or not, is inadmissible: it would pick the value that flatters
   the test statistic, and on a non-monotone curve it lands on a crossing.
   There is no per-row search beyond the ladder.
3a. The whole ladder is measured in ONE analyzer run. `recursive-analysis`
   accepts the startup values to test and prints one column per value, plus a
   column for the strategy's own declared warm-up. The declared value is
   therefore never overridden: it is read as its own column, which is what
   makes requirement 6 below decidable.
4. A row where no ladder value satisfies acceptance is terminal for this route.
5. Acceptance is not admission. A chosen value must additionally survive the
   paired full-window run: identical trade list, identical `trades_sha256`,
   against the strategy as declared. Coverage `PASS`, trap-free,
   `artifact_role=strategy` and not `behavior_changed` continue to apply.
6. A row whose settled value is at or below the author's own declared warm-up
   needs no override at all. It was excluded by a defect in this audit's
   parser, which read the wrong table column, and admitting it requires neither
   a changed warm-up nor the wider band. Such a row is recorded as
   `needed_no_override` and is reported separately, because it is a correction
   rather than a relaxation.
7. A row that converges but whose trade list changes is **E3 exploratory**, not
   E1. The fix altered behaviour, which is a finding, not an admission.
8. Rows admitted through this route carry the label `convergence_warmup_v1` so
   every result can be reported with and without them.
9. Every admitted row records its chosen warm-up, the ladder step it came from,
   the complete drift table it was decided on, the drift at the author's own
   declared warm-up, the largest remaining drift and the indicator carrying it,
   and the trade count the equality was established over. The trade count is required because
   equality over eight trades and equality over 1,845 are not comparable
   evidence, and a reader must be able to see which one a row rests on.

**What this relaxes, stated plainly.** The frozen Stage 6 gate treats any drift
above 0.01 percent as recursive bias. This route accepts up to 1.0 percent, a
hundredfold wider band, and 545 of the 900 rows were excluded by that gate. The
preregistration's own sentence that eligibility thresholds are not relaxed no
longer holds without qualification, and this paragraph is that qualification.
The justification is that 0.01 percent is unreachable in principle for any
recursively smoothed indicator, so the old gate did not separate careful
strategies from careless ones; it separated strategies that use an EMA from
strategies that do not. Requirement 5 partly offsets the wider band, and its strength must not be
overstated. An identical trade list constrains decisions rather than
intermediate values, and decisions are what this study measures. It is not,
however, a stricter criterion than a drift bound, and the two are not ordered.
A five percent drift can leave every trade unchanged when no signal sits near a
decision threshold, and a hundredth of a percent can flip one when a signal
does. It is evidence about this timerange and this pair basket, not a property
of the computation. It is weakest exactly where evidence is already thinnest: a
row with eight trades has almost no opportunity to differ, while one with 1,845
has many.

This audit already contains the decisive counterexample. In Wave B,
`Combined_Indicators` and `CombinedBinHAndClucHyperV0` matched the original
trade list exactly and were still refused, because their decisions rest on
`ta.EMA`, which never fully forgets its seed. Exact trade equality admitted
precisely what the recursion reasoning caught. Each requirement therefore
covers a failure the other misses, which is why both are required and neither
is described as the guarantee.

**Scope.** Every row whose sole hard exclusion reason is `recursive_bias_found`
- 440 rows once the profiles already admitted to E1 are removed, of which 124
are Wave D, 242 were never scheduled and 74 are the Wave B remainder. Rows
carrying a second hard reason are deliberately excluded: 35 also record
`lookahead_found`, 17 a technical trap and 43 no canonical measurement, and no
warm-up changes any of those. Processing order is fixed here, not chosen from
results: Wave D, then the unscheduled rows, then the Wave B remainder.

**E0 is untouched.** It remains the frozen 67 and is reported beside every
result derived under this amendment.

## Amendment 2026-09-02: the settled warm-up is the measurement

**Owner's decision, recorded before the rows it affects were admitted.**

Requirement 7 above routed a converged row whose trade list changed under the
supplied warm-up to E3 exploratory rather than E1, on the ground that the fix
altered behaviour. **Requirement 7 is retired.** So is requirement 5's paired
full-window run as an admission gate.

The reasoning, in the owner's terms. This audit ranks working strategies by
market phase; it is not an attempt to reproduce what an author once ran. Many
of these strategies were written before indicator drift was widely understood,
and their declared warm-ups do not let their own indicators settle - 226 of the
354 candidates declare a value below the one at which their drift disappears,
some by a factor of seventy. A result computed at such a warm-up was not
correct when the author computed it either. What is wanted is the
mathematically clean result: no recursive drift, no look-ahead, under the
current freqtrade. That a clean warm-up yields fewer trades, or more, is the
consequence of measuring properly and not a defect in the row.

**What this costs, stated plainly.** The paired run was the only test that
separated "repaired" from "reconfigured". Of the 26 rows it has already
decided, 13 produced an identical trade list and 13 did not - `SlowPotato`
1,835 against 1,899, `JuicyTrend` 13,698 against 13,607, and two rows with the
same count and a different checksum. Under this amendment all 26 would be
admitted alike. A reader of a market-phase result therefore cannot assume the
number is what the author's own configuration would have produced, and for
roughly half of them it is not.

**What is kept so that cost stays visible.** Every admitted row records the
warm-up it was measured at, the ladder step, the drift, and whether that value
is at or below the author's own declaration (`needed_no_override`). Two of the
354 need no supplied warm-up at all; 126 declare none, so freqtrade's recursion
analyzer refuses them outright and a value had to be supplied before the gate
could run at all; 226 declare a value that runs and was overridden by ours.
Where the paired run has already produced a verdict it stays on the record as
provenance. None of this decides admission any more; all of it decides how a
number should be read.

**What is unchanged.** The amendment is about warm-up and nothing else. A row
still needs a look-ahead `PASS` measured from its own implementation - an `NA`
is no verdict and admits nothing - recursion settled by the ladder, coverage
`PASS`, `traps_n` zero, `artifact_role=strategy`, and not `behavior_changed`.
Three rows that clear both bias gates are held by a documented backtesting
trap, which is not a warm-up question.

Implemented by `eligibility_admit_converged.py` under ruleset
`converged_clean_gates_v1`; every row it admits carries that ruleset, so any
result can still be reported with and without this amendment.

## OPEN before Stage 9 ranking

The following choices are intentionally not inferred from strategy outcomes:

1. Exact discovery/validation split (calendar proposal: discovery through
   2023-12-31, validation from 2024-01-01).
2. Minimum trade and independent-episode evidence for specialist status.
3. Exact exposure-matched benchmark construction.
4. Whether SER stays continuous or receives preregistered categories.
5. Whether the 90-day return robustness classifier freezes at +/-20 percent.
6. Whether volatility stays descriptive in version 1.
7. Whether breadth remains the eight-pair, availability-aware audit universe.
8. Whether forced exit is included only as a later sensitivity test.
9. Portfolio allocation when multiple strategy/pair candidates qualify.

No ranked discovery output may be generated while these entries remain `OPEN`.
