# Regime audit preregistration

**Status:** frozen for feature generation and attribution; the eligibility
expansion amendment below was accepted on 2026-08-30 before ranking; choices
marked `OPEN` must be resolved before Stage 9 produces any ranked strategy table.
The 2026-09-07 gate-factor amendment was accepted before any productive gated
run or candidate specification existed.

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

The analysis window is 2020-03-01 00:00 UTC through 2026-08-21 00:00 UTC
(exclusive end). A daily candle is usable only on the following UTC day. No
feature, label, gate, or attribution may use the still-open daily candle.

## Frozen eligibility expansion amendment, with E0 clauses superseded

The user authorized maximizing technically trustworthy strategy coverage on
2026-08-30, before any strategy-by-regime ranking was inspected. The complete
prospective protocol is frozen in `ELIGIBILITY_EXPANSION_PLAN.md`.

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

## Amendment 2026-09-09: three-month Futures recursion window

**Owner's decision**, before the affected Futures recursion exclusions were
retested. The native Futures recursive-bias diagnostic and the warm-up
convergence ladder now use `20200301-20200601`, three calendar months, instead
of `20200301-20200401`. Spot remains `20190101-20190401`, also three months.

The earlier asymmetry was inherited mechanically: the Spot window came from
the predecessor bias harness, while Futures reused its one-month smoke-test
window. No methodological justification for applying a shorter recursion
observation interval to Futures was recorded. Local BTC perpetual candles begin
on 2020-01-01, leaving two months of prefix history before the new interval.

Stored one-month Futures recursion and convergence records remain provenance,
but cannot satisfy the amended gate. A rerun moves each superseded record under
`superseded` before writing the three-month result. The affected set is selected
only by the pre-existing technical exclusion `recursive_bias_found`, never by
profit or regime performance.

## Amendment 2026-09-10: fixed smoke trade-count cascade

**Owner's decision**, recorded before rechecking the low-trade smoke records.
The canonical trial run starts with `20200301-20200401`. If that run completes
but produces fewer than ten trades, the same unchanged strategy and runtime
are tested over `20200301-20200601`, then `20200301-20210301`. The cascade
stops at the first rung with at least ten trades. A runtime failure does not
become a trade-count verdict and is not repaired by merely widening the date
range. Every attempted rung, archive identity, and trade count is retained.

This is a prospective, result-blind diagnostic rule: the rungs and threshold
were fixed before the rerun and do not depend on profitability or market-regime
performance. It prevents a quiet calendar month from being mistaken for a
strategy that does not trade. It does not relax the eligibility gates and it
does not supersede stronger evidence already obtained over the complete frozen
window. In particular, a look-ahead analysis that remains below ten trades
after its 6.5-year fallback, or a full-window backtest with zero trades, is not
rerun on these shorter smoke rungs.

## Amendment 2026-09-10: identical Spot and Futures bias windows

**Owner's decision**, before any Spot diagnostic was rerun under this change.
The native look-ahead, recursive-bias, and warm-up-convergence diagnostics now
use the identical calendar interval `20200301-20200601` for Spot and Futures.
This supersedes only the sentence in the 2026-09-09 amendment that retained
Spot at `20190101-20190401`; its three-month duration remains unchanged.

Using the same calendar dates removes the sampled market period as a difference
between the two execution modes. Both diagnostics use BTC only, so the later
listing dates of the other seven pooled pairs do not constrain this interval.
January and February 2020 remain available as prefix history for both modes.

Stored Spot records over `20190101-20190401` remain immutable provenance but
cannot satisfy a new decision under this amendment. They must be superseded and
rerun under `20200301-20200601`; selection for rerun is based on the obsolete
timerange, not on profitability or regime performance.

## Amendment 2026-09-10: completed full backtest closes technical work

**Owner's decision.** A successful canonical pooled Stage-7 full backtest is
evidence that the exact strategy implementation completed the technical chain
which precedes that run. A subsequent change to a Spot or Futures diagnostic
calendar window must therefore not return that implementation to the
measurement queue.

The closure is identity-bound: the recorded Stage-7 result must be `measured`,
have the canonical pooled scope, and match the current source hash and run
profile. Its recorded full-backtest timerange remains visible as provenance;
the later Spot diagnostic-window shift does not invalidate this closure. It is exposed as
`technical_chain_complete=true` in `STRATEGY_STATUS.csv`. It closes only
`open_work`; it does not retrospectively admit a strategy, reverse an existing
exclusion finding, or treat an OOM, timeout, failed, or identity-mismatched run
as completed.

## Amendment 2026-09-10: exclusions close the work queue

**Owner's decision.** A strategy recorded in the final `excluded` cohort is a
completed audit case. Its exclusion reason and evidence remain visible, but it
must never retain an `open_work` item merely because a supporting diagnostic is
historical or an ancillary recursion ladder did not finish. This does not apply
to `exclusion_unconfirmed`: that separate cohort has not earned an exclusion
verdict and remains open until its evidence gap is resolved.

## Amendment 2026-09-11: warm-up convergence precedes final recursive-bias

**Owner's decision**, applied prospectively to every strategy that still has
technical gate work. The diagnostic sequence is now: native look-ahead first;
only after a `PASS`, the frozen warm-up convergence ladder; only after a
current `converged` ladder result, final native recursive-bias using that
ladder's selected startup-candle count. A native look-ahead `FOUND` is a final
information-leak exclusion, so neither later measurement is useful or
permitted for that implementation. `NA` is not a pass and likewise blocks
follow-up work until its technical cause is resolved.

This changes workload order, not an admission threshold, timerange, strategy
implementation, or any existing measurement. It prevents an author's declared
or Freqtrade default warm-up from deciding the final recursion verdict when the
fixed ladder demonstrates that it is too short. The runner defers recursive
work until the prerequisite exists and passes the settled value explicitly;
`PIPELINE.md` documents the same order for future work. Older recursive records
remain provenance and are not silently reclassified by this prospective change.

## Amendment 2026-09-10: non-testable canonical full backtests are excluded

**Owner's decision.** A strategy that reached Stage 7 but has a canonical
pooled full-backtest status of `failed`, `resource_inconclusive`, or `timeout`
is not testable for this benchmark and is final `excluded` under C10
`full_backtest_not_testable`. The recorded outcome is retained as provenance;
it is not requeued or retried. This rule applies to the 34 previously E1
admitted rows with those statuses, and does not infer anything about their
profitability.

## Frozen warm-up convergence amendment

Authorized by the owner on 2026-09-01, before any strategy-by-regime ranking
was generated or inspected. It governs a new admission route. Its contemporary
promise that E0 would remain a valid untouched cohort was superseded on
2026-09-03 after E0's missing checks were discovered.

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

**Historical clause, superseded 2026-09-03.** At adoption, E0 was to remain the
frozen 67 and be reported beside every result. It is retained only as an
immutable record of that mistaken Stage 6 classification and must not enter any
current result. Former E0 members require independent E1 admission.

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

Implemented by `evidence/eligibility_admit_converged.py` under ruleset
`converged_clean_gates_v1`; every row it admits carries that ruleset, so any
result can still be reported with and without this amendment.

## Amendment 2026-09-03: the spot analysis window starts a month later

**Owner's decision**, on a finding from the warm-up ladder's own coverage.

The convergence ladder tests warm-ups up to 365 days, but its ceiling is
capped by whichever of the eight basket pairs has the least history before
the analysis window starts - a warm-up the ladder accepts is later reused as
`startup_candle_count` in the full-window run across all eight pairs, and a
value that exceeds one pair's available history would silently shorten that
pair's measured span rather than fail loudly.

`DASH/USDT` was listed on Binance 2019-03-28, the latest of the eight. At the
original window start of 2020-03-01 that left 337 days of prefix history -
short of the 365-day rung by four weeks. Not one of the 62 strategies the
ladder could not settle, across both the original and the `shim5`-widened
runs, was ever offered that rung. Two converged the moment `shim5` let them
reach 90 days at all; the rest sat at whatever their timeframe's nearest
reachable rung was, some worse off there than at 14 days, because drift
against the full-history reference is not monotone in the warm-up.

**The spot window now starts 2020-04-01**, not 2020-03-01. `DASH/USDT` then
carries 370 days of prefix, clearing the 365-day rung with a few days to
spare; `XMR/USDT`, the second-latest listing, clears it with more. The cost
is 31 days off a 6.5-year window, under 0.5 percent, and current for only 18
strategies' full-window measurements at the time of the change - the
market-phase benchmark itself had not yet started.

**The futures window is untouched, and stays at 2020-03-01.** Futures pairs
were listed later still - the last, `DASH/USDT:USDT`, on 2020-02-04 - so
matching fix would need a start of 2021-02-04, cutting eleven months from the
whole futures window to help fourteen strategies. Declined: those fourteen
are capped by history that will never arrive on this exchange, which is a
fact about the pair's own listing date, not a choice this audit is making.
Their reason names that rather than folding it into a bias verdict.

Implemented in `profile_full_window.TIMERANGE` (now `{"spot":
"20200401-20260821", "futures": "20200301-20260821"}`) and
`warmup_convergence.WINDOW_START` (now `{"spot": "2020-04-01", "futures":
"2020-03-01"}`), which the ladder's ceiling and the full-window run must
agree on - the same reasoning as the `shim5` amendment: a warm-up accepted
under one window and applied under another can silently shorten a pair's
span. The `recursive-analysis` and `lookahead-analysis` diagnostic windows
(`profile_bias.WINDOWS`) are a separate, shorter measurement and are not
affected - those checks are forced onto `BTC/USDT` alone by freqtrade itself,
for which `DASH/USDT`'s listing date is irrelevant.

## Amendment 2026-09-03: E0 is retired as a separate cohort

**Owner's decision**, on a finding from re-measuring the frozen 67 for the
first time in this audit's own runtime.

E0 was frozen on 2026-08-30 as a reproducibility anchor: "E0 is untouched. It
remains the frozen 67 and is reported beside every result." The intent was
sound - keep one unmoving reference point while the eligibility expansion
ran. The consequence, only visible once E0 was finally measured here, was
not: E0's own recursion-bias standing had never rested on this audit's
methodology at all.

The Stage 6 sweep that produced the 67 ran `recursive-analysis` without
`--startup-candle` (`harness.py`, commit `be77d12`, 20.08; the same command
is item 1 of `CHECKLIST.md`, commit `4d5a937`, the same day). Freqtrade then
falls back to its own hardcoded default - five fixed candle counts (199,
399, 499, 999, 1999), the same five regardless of a strategy's timeframe,
plus whatever the strategy's own `startup_candle_count` declares. A one-day
strategy tests up to 1999 days of history that way; a five-minute strategy
tests under seven. Whether the resulting table showed "near-zero variation"
was never asked in calendar time, and never checked against a longer warm-up
in case a false plateau was sitting in front of a real one - the exact
failure this audit's own convergence ladder exists to catch (`BigZ04`'s
`bb_lowerband_1h` sits at a flat 3.63% from 200 through 8640 candles, then
jumps to -12.88% at 90 days).

Measured under this audit's own ladder for the first time this week: 64 of
67 hold up cleanly under both checks. One, `MacdStrategy`, does not - 1.07%
residual drift at the largest warm-up the data supports (365 days, after the
2026-09-03 window amendment), just outside the 1% band. Two, `BuyRegions`
and `StochRSITEMA`, had been misread by a defect in our own table parser
(see below) rather than measured at all.

**E0_strict67 is retired and invalid as a cohort.** The 67 are no longer
admitted by having been in the original Stage 6 corpus; each must complete the
same current audit chain as every other strategy, including current-runtime
measurement, the C1-C4 exclusions, convergence, coverage, trade evidence,
artifact role, and repair provenance. No E0 flag may skip a check or serve as a
fallback verdict.
Membership in the original frozen set is kept as provenance on the row
(`gate_notes`), never as a reason to skip a check or override a finding.

`MacdStrategy` moves to `excluded` under C2. The other 66 were subsequently
admitted independently under `converged_clean_gates_v1`; their usability comes
from those 66 row-level E1 decisions, never from former E0 membership.

## Amendment 2026-09-03: a second reader defect, corpus-wide

While re-measuring E0's recursion drift, `StochRSITEMA` came back
"inconclusive: no drift table" despite its stored log showing a complete,
readable 76-row table. The cause: `recursive_table()`'s row-name filter
required a bare Python identifier (`[a-zA-Z_0-9]+`) and silently dropped any
row whose name did not match - `rsi(14)`, `stoch-slowk`, `BBB_20_2.0`,
`1h-rsi`, `50 SMA`. 68 stored logs across the corpus carry at least one such
row; some were misread as having no table at all, others as `converged` on
an incomplete table that never showed the very indicator whose name could
not be parsed.

Fixed in `profile_bias.recursive_table()`; re-derived from stored logs via
`tools/warmup_reparse.py --store punctuated`, applied only where the reading grew
richer (58 records) and never where it would have shrunk, which is the
signature of a different defect entirely (below).

**A related, independent defect surfaced during the same re-read.** Ten
pairs of strategy IDs in the corpus differ only in case - `SuperTrend` and
`Supertrend`, `BBRSI` and `bbrsi`, `mabStra` and `MabStra`, among others -
genuinely different strategies from different source files. The path
construction used for per-strategy logs and isolated source directories
(`profile_smoke._safe`) preserved case but did not otherwise disambiguate,
and this filesystem folds case, so both members of every such pair wrote to
the identical path. Whichever ran later silently overwrote the earlier one's
log. `_safe` now appends a short hash of the exact-cased name, so no two
different strategy IDs can ever collide again; already-written `debug_log`
paths are untouched, since nothing regenerates them to look a file up.
Records whose log the punctuation fix would have shrunk (`SuperTrend`,
`bbrsi`, `hlhb`, `MACDStrategy`, `MacdZeroCrossStrategy`) are queued for a
fresh, collision-safe run rather than reparsed from a log that no longer
describes them.

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

## OPEN before Stage 9 ranking

The following choices are intentionally not inferred from strategy outcomes:

1. Exact discovery/validation split (calendar proposal: discovery through
   2023-12-31, validation from 2024-01-01).
2. Minimum trade and independent-episode evidence for specialist status.
3. Exact exposure-matched benchmark construction.
4. Whether SER stays continuous or receives preregistered categories.
5. Whether the 90-day return robustness classifier freezes at +/-20 percent.
6. ~~Whether volatility stays descriptive in version 1.~~ **DECIDED
   2026-09-05**: it becomes a reporting label at the two frozen thresholds,
   splitting `SIDEWAYS` and adding `high_vol_shock`. The primary DMI/ADX model
   is unchanged. See the amendment above.
7. Whether breadth remains the eight-pair, availability-aware audit universe.
8. Whether forced exit is included only as a later sensitivity test.
9. Portfolio allocation when multiple strategy/pair candidates qualify.

No ranked discovery output may be generated while these entries remain `OPEN`.
