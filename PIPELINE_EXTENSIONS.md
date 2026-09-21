# Pipeline extensions - admission expansion, execution robustness, validation extension

`PIPELINE.md` is the check chain: the stages, the programs, the current rule of each stage and the record of the
decisions behind them. This file holds what was **added to** that chain by a protocol of its own. Each part was a
separate plan file until 2026-09-20; the text is unchanged, only the headings moved one level down.

| Part | Extends stage | Status | Formerly |
|---|---|---|---|
| 1. Eligibility expansion protocol | 6, 7 (who is admitted) | Frozen 2026-08-30, E0 clauses superseded 2026-09-03; all expansion waves terminal. Results of the waves: `evidence/ADMISSION_RECORDS.md` | `ELIGIBILITY_EXPANSION_PLAN.md` |
| 2. Execution robustness and cost screen | 8b (after the pooled Full-Backtest) | Built and running; Amendments 2026-09-19 and 2026-09-20 are current | `EXECUTION_ROBUSTNESS_PLAN.md` |
| 3. Validation window extension | 9 to 13 (regime, attribution, evaluation) | **On hold** (owner, 2026-09-20). Do not start, do not change `END` or `TIMERANGE` | `VALIDATION_EXTENSION_PLAN.md` |
| 4. Regime rotation bot | none (a consumer of the results, not part of the chain) | Variants and the rule of each, written before it is run | new 2026-09-20 |

Section numbers quoted inside a part (for example `section 5.1`) refer to that part. A file name inside the text of a merged part (for example `EXECUTION_ROBUSTNESS_PLAN.md`) names the file as it was then; the table "Where a former document went" in `README.md` resolves it.

## 1. Eligibility expansion protocol

*Formerly `ELIGIBILITY_EXPANSION_PLAN.md`, merged here on 2026-09-20 without changes to the text below.*

**Status:** accepted and frozen on 2026-08-30, before Stage 9 ranking; all E0
admission/reporting clauses superseded on 2026-09-03; FreqAI runtime
restoration added as a permitted repair class on 2026-09-14 (see §4.1)
**Purpose:** maximize the number of strategies that can be evaluated across
market regimes without admitting future leakage, unresolved evidence, duplicate
implementations, or behavior-changing repairs into confirmatory claims.

This protocol began as an amendment to the Stage 6 campaign. The later audit
showed that its 67-profile result had not passed one uniform, complete check
chain. The immutable files remain as historical evidence, but the 67 labels
have no admission or inferential force. Every usable strategy, including a
former E0 member, requires its own active E1 adjudication under the current
rules. The prospective repair rules, candidate universe, and stop conditions
remain fixed before any strategy-by-regime ranking is inspected.

### 1. Estimands and populations

The confirmatory target population is:

> The deduplicated public Freqtrade `strategy_id x native run_profile`
> implementations that can be measured honestly after the repair rules frozen
> here and that then satisfy every original technical eligibility gate.

This is not an estimate for all 900 source profiles. It is conditional on
successful measurement and validation under this protocol.

Four evidence populations are retained:

| Code | Population | Use |
|---|---|---|
| `E0_strict67` | Historical tag for the 67 profiles recorded at Stage 6 before the uniform check chain existed | Provenance only; invalid as cohort, sensitivity, baseline, fallback, or admission |
| `E1_expanded_confirmatory` | Every profile with an active row-level `admitted_E1` decision after the applicable current audit chain, including independently re-admitted former E0 members | Confirmatory analysis population |
| `E2_drift_sensitivity` | Profiles with recursive drift whose decisions are exactly invariant under the frozen tests but whose recursive diagnostic remains `FOUND` | Sensitivity only |
| `E3_derived_exploratory` | `behavior_changed`, lookahead-rewritten, trap-corrected, or otherwise behavior-changing variants | Separate exploratory analysis only |

One `strategy_id x run_profile` contributes at most one canonical
implementation to E1. Original and repaired variants are never counted as
independent strategies. E0 membership is retained only as a historical tag.

### 2. Rules that do not change

Admission to E1 still requires:

1. identity-bound canonical measurement in the native execution mode;
2. at least one trade in the full frozen measurement window;
3. canonical lookahead `PASS`;
4. canonical recursive-bias `PASS`;
5. exact frozen-window pair/candle coverage `PASS`;
6. no published technical trap;
7. equivalence status other than `behavior_changed`;
8. a canonical bias rerun for every `output_equivalent` overlay.

`NA`, timeout, process termination, an unparsed result, insufficient analyzer
trades, or missing evidence is never converted to `PASS`. Profit, significance,
market comparison, regime performance, taxonomy, and cluster membership remain
absent from technical admission.

Actual lookahead and unresolved recursive drift are not waived to increase the
count. A behavior-changing correction creates an E3 variant, not an E1 pass.

### 3. Frozen candidate waves

The machine-readable candidate manifest is derived only from the current
technical artifacts. Candidate membership must be hashed before the first new
measurement.

#### Wave A - seven pending diagnostics

Process all seven current `pending_diagnostics` rows. Diagnostic limitations may
be repaired only at the harness, dependency, resource, or provably equivalent
metadata layer. No entry or exit rule may change.

#### Wave B - warm-up refusals

Process all 82 rows that meet all of the following at the frozen checkpoint:

- sole hard reason `recursive_bias_found`;
- `recursive_kind=refused_no_warmup`;
- no pending reason.

Determine the required startup history from the strategy's complete indicator
and informative-timeframe dependency graph. A startup metadata change may enter
E1 only after the equivalence and full rerun requirements below are met.

#### Wave C - canonical measurement recovery

Inventory all 230 rows whose sole hard reason is
`canonical_implementation_not_measured`. Before execution, report missingness by
repository, native run profile, timeframe, artifact role, repair provenance,
runtime status, strategy family, and dependency/runtime class.

The queue is exhaustive rather than opportunistic: every row receives a
terminal classification under the same rule set. Artifact-role review and an
unknown execution profile must be resolved before measurement. Successful load
or smoke execution is not eligibility; full measurement and both bias gates
still follow.

#### Wave D - measured recursive drift

Process the 124 rows whose sole hard reason is recursive bias, whose subtype is
`drift_measured`, and which have no pending evidence. These rows cannot enter E1
while recursive status remains `FOUND`.

A permitted equivalent repair followed by a fresh recursive `PASS` may admit a
row to E1. If status remains `FOUND` but all frozen decision-invariance checks
pass, the row may enter E2 only. Failed invariance remains excluded.

#### Later behavior-changing work

Lookahead rewrites, persistent recursive corrections, trailing/ROI trap
corrections, and entry-rule changes needed to create trades belong to E3. They
are attempted only after E1 is frozen and cannot enlarge confirmatory evidence.

### 4. Permitted repair boundary

Permitted E1 repairs are limited to:

- environment and dependency restoration;
- documented current-API aliases with identical reachable semantics;
- path, import, data-format, and unambiguous legacy metadata compatibility;
- startup metadata that is proven not to alter reachable trading decisions;
- a source overlay with a file-specific strict or output-equivalence proof.

The original source-of-record remains unchanged. Every overlay records its
source hash, repaired hash, repair class, rules, provenance, and proof artifact.

The following are behavior-changing and therefore E3 only:

- modifying an entry or exit predicate;
- changing a reachable parameter, ROI table, stoploss, trailing relationship,
  leverage, direction capability, protection, or position-sizing rule;
- replacing missing indicator values in a way that can reach a decision;
- truncating or substituting FFT/model inputs;
- disabling shorts or informative data used by the authored strategy;
- accepting a different execution mode merely because it runs.

If a new compatibility failure class is discovered, work stops for that class.
A written amendment must define one deterministic rule for every matching row
before any of those rows resume. No repair rule may depend on profit or regime
performance.

#### 4.1 FreqAI runtime restoration (2026-09-14 amendment)

A newly discovered compatibility failure class: a strategy whose own source
requires `freqai.enabled=true` to load at all fails immediately with
`freqAI is not enabled. Please enable it in your config to use this strategy.`
- an `ImportError` before a single indicator runs, not a trading-decision
question. `repair/run_freqai.py` had measured these strategies since before
this amendment, but on a separate, explicitly non-comparable track
(`run_class="freqai"`, "NOT A CLASS 1 REPAIR", never entering E1) - on the
reasoning that the `freqai` config block (training window, model, feature
engineering) is not something the strategy file supplies. On owner review
(2026-09-14) that reasoning does not survive contact with how every other
Freqtrade strategy in this corpus is already run: `stake_amount`,
`pair_whitelist`, `fee`, `dry_run_wallet` and the rest of the base runtime
config are never supplied by the strategy file either, for any of the 1,369
canonical strategies - they are audit infrastructure every strategy already
receives to run at all. A `freqai` block is the same kind of missing
infrastructure for the narrower class of strategies whose own code declares
it needs one, not evidence about what the strategy does. Restoring it is
`environment and dependency restoration` under §4, on these conditions:

- **The configuration is fixed and uniform, never per-strategy-tuned.**
  Exactly the block `repair/run_freqai.py` already defines and states
  plainly in its own docstring - `train_period_days=30`,
  `backtest_period_days=7`, `purge_old_models=2`,
  `fit_live_predictions_candles=300`, `DI_threshold=0.9`,
  `weight_factor=0.9`, `principal_component_analysis=False`,
  `use_SVM_to_remove_outliers=False`, `indicator_periods_candles=[10, 20]`,
  `data_split_parameters={test_size: 0.33, random_state: 1}`,
  `model_training_parameters={n_estimators: 100, verbosity: -1}`,
  model `LightGBMRegressor` - applied identically to every strategy in this
  class. `include_timeframes` and `include_corr_pairlist` are the only
  per-strategy-derived values, both by a fixed algorithmic rule (the
  strategy's own declared timeframe plus the next locally-available ones;
  correlated pairs deliberately left empty - see the module docstring), not
  chosen per strategy to change what it produces. No repair row in this
  class may set a value the docstring does not already name for every row.
- **Execution mode is not part of this repair.** Spot vs. futures for a
  FreqAI-repaired strategy is decided exactly the way it already is for
  every one of the other 1,369 canonical strategies: by the strategy's own
  `can_short` declaration, read by the same AST check
  (`evidence/execution_profiles.py`'s `declared_can_short()`) that sets
  `run_profile` for the whole corpus. This is not `accepting a different
  execution mode merely because it runs` (§4's prohibition on that remains
  in force) - nothing about the mode is chosen because it happens to let
  the strategy execute; it is the same author-declared classification every
  other row already receives before this amendment existed. A strategy that
  declares `can_short=True` was always going to run in futures mode in this
  audit; a FreqAI strategy is no exception and gets no separate choice.
- **The original source-of-record is untouched.** The `freqai` block is
  injected as a `config_source`/`config_keys` overlay in
  `evidence/PROFILE_CLASS1.json` - the same overlay mechanism §4 already
  permits for other config-sourced repairs - naming
  `user_data/freqai_configs/<strategy>.json` (the exact file
  `repair/run_freqai.py` already writes) and `config_keys: ["freqai"]`.
  `--freqaimodel LightGBMRegressor` is passed as a CLI flag the same way,
  via the existing `freqaimodel` field `evidence/profile_smoke.py`'s
  `_runtime()` already reads.
- **A FreqAI-repaired row is not exempt from anything else in this
  document.** It still needs canonical lookahead `PASS`, canonical
  recursive-bias `PASS`, coverage `PASS`, at least one trade in the frozen
  window, and every other §2 requirement before E1. `run_class="freqai"` on
  a result card now means "this row's config includes a restored `freqai`
  block", not "excluded from confirmatory analysis" - the two-population
  design `repair/run_freqai.py`'s original docstring described is retired
  by this amendment, not narrowed.

This amendment resolves exactly one compatibility failure class
(`freqAI is not enabled`) for exactly the rows whose own source requires it.
It does not reopen or relax any other clause in §4.

### 5. Equivalence and decision-invariance evidence

An E1 repair must satisfy the existing `strict_equivalent` or
`output_equivalent` definition and then pass all canonical diagnostics.

Where both original and overlay can execute, compare across the complete frozen
window and all eight available-history pairs:

- entry and exit decision columns;
- signal direction and tags;
- timestamps and pair identities;
- order side, size/stake, leverage, and price inputs where strategy-controlled;
- complete pooled trade sequence and semantic trade-list hash.

All compared reachable decisions must be identical. Numeric closeness alone is
insufficient.

For `output_equivalent`, also retain a file-specific reachability or margin
proof covering the parameter range; one historical trade-list match alone does
not prove future equivalence.

E2 decision invariance is evaluated across the analyzer's frozen startup
lengths and the canonical execution. Exact decisions and strategy-controlled
order fields must match. E2 never receives `regime_eligible=true` while the
recursive gate remains `FOUND`.

#### 5.1 Zero-warm-up analyzer adapter

Freqtrade's recursive analyzer refuses an authored
`startup_candle_count=0` before evaluating indicators. For Wave B only, this is
handled by one general diagnostic adapter rather than by editing the original:

1. run recursive analysis with the smallest positive startup value;
2. if an indicator has a documented larger minimum lookback, use that complete
   dependency lookback as the single recovery attempt;
3. retain every attempt and never interpret an analyzer exception as PASS;
4. require a current native lookahead PASS;
5. compare original and adapted pooled eight-pair trades over the full frozen
   window by exact semantic hash;
6. retain a file-specific static proof that the authored calculations and
   decisions are independent of history below the adapter boundary.

An adapted recursive `PASS` can satisfy the E1 recursive gate only when all six
conditions hold. A recursive `FOUND` remains a hard E1 failure even if a trade
comparison happens to match. A full-window match without the static proof is
E2 evidence, not E1 admission. The adapter and effective config hash are stored
as diagnostic provenance; the original source remains canonical.

### 6. Measurement and resource protocol

- Never run two benchmark or analyzer writers concurrently.
- Use the existing identity-bound Docker runtime unless a documented pinned
  runtime is required by the strategy.
- Memory-heavy profiles run with one worker.
- Preserve the existing fixed diagnostic timerange cascade; do not choose a
  window from trade or regime outcomes.
- One standard attempt and one documented single-worker recovery attempt are
  allowed for timeout or process termination. A second inconclusive result is
  terminal `pending_diagnostics` for this expansion.
- Analyzer limitations may be addressed only by a general harness change that
  preserves the tested strategy and is applied to every matching candidate.
- Every result is resumable, identity-bound, and written atomically.

### 7. Stop rule

The expansion ends when every row in Waves A-D has one terminal state:

- admitted to E1 after every original gate passes;
- retained in E2 after frozen decision-invariance evidence;
- assigned to E3 because the required repair changes behavior;
- hard ineligible with a demonstrated technical failure; or
- pending after the fixed diagnostic/resource attempts are exhausted.

There is no target survivor count. The former figure 156 was only historical
planning arithmetic that added the invalid E0 count to Waves A and B; it is not
a success criterion, forecast, or valid population ceiling. The
protocol does not stop early after reaching a desirable count and does not add
new repair classes after inspecting rankings.

E1 membership and all input/code/result hashes are frozen before Stage 9 is
rerun. E0 artifacts are not overwritten because they document the error, but
their rows are never admitted or analyzed on that basis.

### 8. Statistical safeguards after expansion

- Never report E0 as a confirmatory or sensitivity result. Former membership
  may be shown only as provenance beside the member's independently valid E1
  result.
- Preserve original/repaired provenance and report their strata.
- Treat copy families as dependence clusters; report family-clustered bootstrap
  or hierarchical uncertainty and an equal-family-weight sensitivity.
- Reuse the audit's Benjamini-Hochberg and Benjamini-Yekutieli procedures where
  inferential multiplicity correction is applicable.
- Keep discovery and validation separated; failed validation candidates are not
  replaced.
- Never describe 286,616 trades, or any larger expanded trade count, as the
  number of independent strategy observations.

### 9. Required artifacts

The expansion produces:

- `evidence/ELIGIBILITY_EXPANSION_MANIFEST.json` - frozen inputs, candidate IDs, hashes,
  waves, rules, and stop conditions;
- `evidence/ELIGIBILITY_EXPANSION_CANDIDATES.csv` - row-level wave and terminal status;
- `evidence/ELIGIBILITY_EXPANSION_MISSINGNESS.csv` - Wave C missingness inventory;
- `evidence/ELIGIBILITY_EXPANSION.md` - historical frozen wave inventory; its E0 labels
  are provenance, while current E1/E2/E3 status comes from current adjudication;
- append-only technical result artifacts keyed by canonical identity;
- regenerated eligibility and pooled Stage 7 artifacts only after E1 is frozen.

No strategy-by-regime ranking is read or generated while this protocol is being
implemented.

## 2. Execution robustness and cost screen (Stage 8b)

*Formerly `EXECUTION_ROBUSTNESS_PLAN.md`, merged here on 2026-09-20 without changes to the text below.*

### Scope and status

This is a prospective, additive post-Full-Backtest verification stage. It does
not replace any Smoke, Look-Ahead, Warm-up/Recursive, admission, or canonical
pooled Full-Backtest result. Existing historical results remain provenance and
are never reclassified by this addendum.

The stage is applied to every identity-current strategy with a measured
canonical pooled Full-Backtest and a declared main timeframe greater than 5m.
Selection is independent of performance, rank, or profitability.

*Revised on 2026-09-19: strategies at or below 5m are not rerun, and count as equal
to a strategy that received the 5m run. See "Amendment 2026-09-19" at the end of
this file.*

### Intracandle-detail check

For each eligible strategy, rerun the canonical pooled Full-Backtest with the
same strategy source, execution profile, configuration, eight-pair universe,
timerange, fee, and shared-capital parameters. Add only:

```text
--timeframe-detail 5m
```

The strategy keeps its declared main timeframe. The check must not override it
to 5m or refactor its signal logic. Freqtrade therefore evaluates signals on
the authored timeframe and uses 5m candles only to model intrabar trade
progression, callbacks, exit timing, and released trade slots.

Strategies at 5m or 1m are not eligible for this 5m-detail check. A future
1m-detail extension for 5m strategies requires a separate preregistered
amendment and verified 1m data coverage.

### Results and interpretation

Every run records the baseline manifest reference and identity hashes, exact
command, main/detail timeframe, data coverage, runtime/tool versions, and the
native result summary in `evidence/EXECUTION_ROBUSTNESS.json`.

The status is one of:

- `PASS`: reproducible detail run with no material sensitivity signal.
- `SENSITIVE`: reproducible run meeting one or more predeclared warnings.
- `NA`: not applicable or required detail data unavailable.
- `ERROR`: execution or publication failure; never a strategy verdict.

`SENSITIVE` is a review classification, not an automatic exclusion. It is
triggered when the detail run becomes unprofitable, loses more than 50 percent
of the baseline net profit, or has an exit/duration profile indicating
intra-candle sensitivity. The full native metrics and baseline comparison must
remain visible; no aggregate ranking may conceal the classification.

`STRATEGY_STATUS.csv` and `evidence/PIPELINE_STATE.json` publish
`execution_robustness_status` and `robustness_qualified`. Only `PASS` sets the
latter to true. This does not alter E1 admission. It is an additional final
eligibility condition for calling a result an ADX regime specialist or
universal specialist; `SENSITIVE`, `NA`, `ERROR`, and `PENDING` remain
visible but cannot receive that verified designation.

*Revised on 2026-09-19: `robustness_qualified` additionally requires a cost-screen
`PASS` in the claimed ADX regime state. See "Cost screen per ADX regime state"
and "Qualification for the verified specialist designation" in the amendment
at the end of this file.*

### Follow-up stages

Cost/slippage stress, limit-order fill-risk review, and temporal walk-forward
validation are separate prospective stages. They are not inferred from this
check and must receive their own immutable parameters before execution.

### Resource and execution rules

Runs are serial and use the same memory safeguards as canonical Full-Backtests.
The detail data must be present before a run is admitted. A missing data set is
recorded as `NA`, not repaired by changing the strategy or timerange. Evidence
publication, pipeline-state refresh, metadata recording, commit, and push
occur after every completed batch.

### Amendment 2026-09-19: classifier, strategies at or below 5m, cost screen

Owner decisions of this date, and the definitions the first implementation
(`evidence/execution_robustness.py`) applies. Nothing above is withdrawn; where
this amendment is more specific it governs.

#### Scope: strategies at or below 5m are not rerun

Owner decision, on resource grounds, made after a first draft of this amendment
had proposed a 1m-detail batch for them. That batch is not run and not planned.

The stage covers every identity-current strategy with a measured canonical
pooled Full-Backtest. Above 5m the 5m detail run applies. A strategy at or below
5m (404 of the measured baselines: 400 at 5m, 4 at 3m) already simulates at the
granularity the others are rerun at, so it is **counted equal to a strategy that
received the 5m run**: `PASS`, reason `baseline_at_detail_granularity`, and
it satisfies the execution half of `robustness_qualified` exactly as a measured
`PASS` does (the cost half is separate, see below).

This is a rule and not a measurement, and the record says so: `basis` is
`owner_rule_at_or_below_5m` where it is `measured_detail_run` for a rerun, and the
status table publishes it as `execution_robustness_basis`. What the rule does not
show is ordering inside one 5m candle, which only a 1m run would. The 1m data
exists (about 4.4 million candles per pair, complete apart from the exchange's
own gaps) should the decision be reopened.

#### What `SENSITIVE` means

The plan's third trigger ("an exit/duration profile indicating intra-candle
sensitivity") had no measurable form. It is replaced. A run is `SENSITIVE` when
any of these holds, comparing the detail run with its baseline:

1. **`profit_sign_flip`** - net profit changes sign. Covers the plan's "becomes
   unprofitable" and its mirror image.
2. **`profit_change_over_50pct`** - net profit changes by more than 50 percent of
   the baseline's magnitude, in either direction. The plan's clause only looked
   at losses; on the first 42 runs `TrendBreakout` went from -52.8 % to +75.6 %
   and `AdaptiveRegime` from -11.7 % to +27.6 %, which is large execution
   sensitivity that a losses-only rule reads as `PASS`. The freqtrade baseline is
   pessimistic where a stoploss and a take-profit both fit inside one candle.
3. **`trade_count_change_over_10pct`** - the trade set changes by more than 10
   percent. The regime attribution is built on the baseline trades; a materially
   different trade set means it no longer describes the more realistic run.

The distance between the two exit-reason mixes is reported but is not a trigger:
on the first 42 runs its median was 0.002 and its maximum 0.063, including runs
that flipped sign, so a threshold on it could never fire.

These thresholds are hashed into every record (`thresholds_sha256`). They were
fixed while 42 of the 230 five-minute-detail runs existed and before the rest
did; that is disclosed here rather than presented as predeclared in the strict
sense. `SENSITIVE` remains a review classification, not an exclusion.

#### Validity of a comparison

A record is only produced when all of the following hold, otherwise it is `NA`
or `ERROR` with the reason named:

- the native result echoes `timeframe_detail` equal to the one requested
  (`ERROR: detail_flag_not_applied_in_native_result`) and the baseline does not
  (`ERROR: baseline_is_itself_a_detail_run`);
- `canonical_sha256`, `runtime_config_sha256`, `run_profile`, `timerange` and the
  pair list are identical between baseline and detail run (`NA:
  identity_mismatch:...`);
- detail candles cover at least 99 percent of what the main timeframe's own data
  for the same pair and window implies. freqtrade silently falls back to the
  coarse candle where detail data is missing, so a run over partial data would
  still "measure" (`NA: detail_data_incomplete`).

#### Runtime attribution and anomalies

The record states whether baseline and detail ran in the same runtime. A
`SENSITIVE` result across runtimes carries `control_run_needed`: the baseline of
24 of the first 30 strategies came from `native_unversioned`, the detail runs
from Docker, so the difference is not yet attributable to the detail candles.
Strategies without intra-candle logic reproduce exactly across the two runtimes
(`AlligatorStrategy` 590.5 % in both), which bounds the effect without removing
it. No control run is scheduled by this amendment.

The classifier also reports, without changing any status, findings about the
runs themselves. The first is trades that close before they open: 0 in the
baselines, 15 trades across 7 strategies in the detail runs, so an artifact of
`--timeframe-detail` rather than of any strategy.

#### Cost screen

Separate from the detail check and needing no new backtest. The canonical
baseline trades are re-priced with additional slippage per side, on the notional
(`stake_amount` times leverage), on top of the 0.1 % fee the run already charges.
The reference stress doubles the modelled friction: 0.1 % extra per side, 0.2 %
per round trip. The grid is 0.05 %, 0.1 % and 0.2 % per side.

- `PASS` - net profit stays positive at the reference stress.
- `SENSITIVE` - baseline profitable, not profitable at the reference stress.
- `NA` - baseline not profitable, or no trades. A cost can only worsen it.

Each record carries the break-even slippage per side in basis points and the
article's caution flag (mean profit per trade below 0.5 %), which is reported
but not decisive: 43 of 102 strategies below that mean still pass the doubling
stress. The calculation is first order. With `stake_amount: unlimited` a lower
balance would shrink later stakes, which it leaves out.

#### Cost screen per ADX regime state

Owner decision 2026-09-19, later the same day: a regime specialist that performs
very well in some market phases must not be marked down by the cost picture of the
phases where the strategy does not run well. The whole-run screen above is
therefore descriptive only, and the cost condition is judged per ADX regime state.

- **States.** The primary DMI/ADX model's four states, `BULL`, `BEAR`, `SIDEWAYS`
  and `TRANSITION`, once for BTC (`btc`) and once for the traded coin (`coin`). A
  trade belongs to the state on the day it opened, assigned by
  `regime.attribution.attribute()` itself and not re-derived. Where the project's
  own regime summary was current, 2343 of 2343 cell trade counts match it.
- **Basis.** A fixed stake per trade, the specialist evaluation's own convention,
  so a state late in the window is not inflated by a compounded balance. A trade's
  cost is twice the slippage times its leverage, as a ratio of its margin. This
  differs from the whole-run screen, which prices actual stakes.
- **Trade floor.** 10 trades per state, the specialist evaluation's own floor;
  `selftest()` asserts the two constants stay equal. Below it the state is `NA`.
- **Window.** A specialist claim rests on the validation window from 2024-01-01
  (`regime.specialist_evaluation.VALIDATION_START`, frozen 2026-09-11), so that
  window decides. The whole window is published beside it as context
  (`cost_pass_regimes_all_windows`). The two differ mostly for universal
  specialists: 7 pass in all four coin states on the validation window, 128 on
  the whole window, because many states have fewer than 10 validation trades.
- **Status per state.** `PASS` when the state's mean per-trade profit stays
  positive at the reference stress; `SENSITIVE` when it is positive but does not;
  `NA` when the state is not profitable, has no trades, or is below the floor.

#### Qualification for the verified specialist designation

`robustness_qualified` is the condition for the verified specialist designation,
and it has two parts:

- `execution_robustness_status` is `PASS` (measured, or by the rule for strategies
  at or below 5m), **and**
- the cost screen passes **in the state where the specialist claim is made**.

`robustness_qualified` in the status table is the strategy-level form: execution
`PASS` and cost `PASS` in at least one state on the validation window, with those
states listed in `cost_screen_regimes_pass`. It is necessary and not sufficient.
The designation for one claimed state must consult that state
(`qualifies_in(record, kind, state)`), and a universal specialist must pass in all
four (`qualifies_universal(record, kind)`). Because a strategy with any positive
state can reach the strategy-level flag, that flag discriminates weakly by itself;
the per-state list is the information.

Each component stays published (`execution_robustness_status`,
`cost_screen_regimes_pass`), and the whole-run `cost_screen_status` stays as a
description that no longer gates. `evidence/PIPELINE_STATE.json` carries the
conjunction as `robustness_qualification`.

`regime/specialist_evaluation.py` does not consult any of this yet, although
rankings already exist: the Model 0 evaluation of 584 strategies and the Model
1/2/3 evaluations of the candidate sets, published as the *Regime-Spezialisten*
artifact on 2026-09-15. They predate this stage and carried no annotation. Since
2026-09-20 the published page joins the annotation as a *Robustheit* column
(`tools/regime_specialists_page.py`); the ranking CSVs still carry none. The
designation is "clears the specialist floor" AND the per-state qualification, a
column that changes no ranking. (An earlier version of this section
said that no ranked output existed; that was wrong.)

#### Generated stores

`evidence/EXECUTION_ROBUSTNESS.json` and `evidence/COST_SCREEN.json` are written
only by `python -m evidence.execution_robustness` and never edited by hand. Each
record carries the numbers it was decided on, so the files stay readable without
`user_data/`; a rebuild without an archive keeps that strategy's existing record.
Rebuild after every detail batch, then regenerate the status table.

### Amendment 2026-09-20: how large the detail effect is, what causes it, and what to run

Two questions, both answered from runs that exist: how much do the results of a strategy at 5m change when
it is rerun with 1m detail candles (section 1), and why do the Stage 8b reruns of strategies above 5m deviate
from their author-timeframe runs (section 3). The recommendation for future work is in section 2. Nothing
here changes `THRESHOLDS`, the classifier or a status; it is evidence for a decision that stays with the
owner.

#### 1. Test: strategies at 5m, rerun with 1m detail

The rule of 2026-09-19 counts a strategy at or below 5m as having passed the detail check, because its own
candle is already as fine as the detail candle. That is a rule and not a measurement. To see what it leaves
out, ten strategies were rerun with `--timeframe-detail 1m`.

**Selection**, computed by `bot/detail_1m_batch.py`, not picked by hand: own timeframe 5m; ranked by the
validation-window dollar gain of `strategy_total_dollar_gain.csv`; the source declares a trailing stop, a
custom stoploss or a dynamic ROI (a table of two or more steps, or `custom_roi`); strategies with the same
trades and gain count once; the first ten. `ClucFiatSlow` is thereby not tested separately from
`ClucFiatROI`.

**Method.** Each strategy ran through the pipeline's own runner (`profile_smoke.run_one`, so the same config,
runtime rules and repairs as its canonical run) over the validation window, 2024-01-01 to 2026-08-20, with
1m detail. Each was compared with (a) its canonical archive and (b) a control: the same runner and window at
5m without detail candles. The control matters because a window that starts in 2024 does not start in the
state of a run that began in 2020. Trades are compared by the mean profit ratio per trade, the sum of the
ratios, and matched by pair and opening candle.

| strategy | canonical n / mean % | control n / mean % | 1m detail n / mean % | 1m vs control |
|---|---|---|---|---|
| EI3v2_tag_cofi_green | 757 / 0.889 | 757 / 0.889 | 763 / 0.755 | -15.1 % |
| BuyOrDie | 843 / 0.734 | 884 / 0.688 | 884 / 0.688 | 0.0 % |
| E0V1E_DCA3 | 407 / 1.131 | 407 / 1.130 | 427 / 0.792 | -30.0 % |
| ClucFiatROI | 1377 / 0.262 | 1392 / 0.258 | 1400 / 0.289 | +12.1 % |
| SMAOffset_Hippocritical_dca_leverage | 138 / 2.556 | 138 / 2.556 | 213 / 2.481 | -2.9 % |
| UniversalMACD | 466 / 0.675 | 466 / 0.675 | 466 / 0.713 | +5.6 % |
| CombinedBinHAndClucV3 | 473 / 0.658 | 473 / 0.658 | 483 / 0.780 | +18.5 % |
| SMAOffset | 443 / 0.660 | 443 / 0.660 | 443 / 0.660 | 0.0 % |
| NFI5MOHO_WIP | 230 / 1.204 | 230 / 1.204 | 241 / 0.951 | -21.0 % |
| ZaratustraDCA5 | not comparable, see below | 7322 / 0.123 | timeout at 3600 s | - |

**Result over the nine that finished.** The detail candles alone change the mean profit per trade by -3.6 %
on average (median 0 %; worse in four, better in five). Pooled over all trades the mean falls from 0.703 % to
0.693 % (-1.4 %), and the sum of the ratios changes by +1.0 %. Against the canonical runs it is -4.6 % on
average and -2.9 % pooled. The spread is large: -30 % to +19 %. The largest loss, -30 % (E0V1E_DCA3), is below
the 50 % that makes a strategy `SENSITIVE` in the classifier. No strategy's mean profit per trade changed its sign.

A runtime difference does not appear in these ten: for seven the control has the same trade count and the same mean as
the canonical run (the canonical archives are Docker or native runs, the control is native). Two controls differ from the
canonical run because of the window start, not the runtime: BuyOrDie, which holds positions for months
(843 canonical against 884 in every 2024 run), and ClucFiatROI (1377 against 1392). Without the control the
1m effect of BuyOrDie would have read -6.2 % instead of 0 %.

**ZaratustraDCA5 (not comparable, and not measurable at 1m within the ceiling).** The 1m run reached the
ceiling of 3600 s and is recorded as a timeout; the ceiling is not raised. Its 5m control also does not
match the canonical run in trade count (7322 against 4161), and the reason is the account, not the candles:
the canonical run with `stake_amount: "unlimited"` lost 96.7 % of its account over the whole window and
ended at $33.7, so its later stakes were small (mean $9 in the validation window), which probably limited the
number of entries (the minimum stake was not checked); the control started with a fresh $1000 (mean stake $67) and placed 76 % more. The profit ratio per
trade is independent of the stake (0.166 % against 0.123 %), the set of trades is not. The strategy is a DCA
strategy on futures with long and short trades. The fixed-$1000-per-trade convention of the evaluation shows
+$6,898 for it in the validation window while the account of its own run collapsed; that is a property of the
convention and of DCA, worth a caveat wherever its dollar figure is quoted. A strategy of this kind cannot be
compared across windows that start in different account states and cannot be run at 1m inside the ceiling.

#### 2. Causes and recommendation

**Where the change comes from** (`bot/detail_1m_causes.py`, the nine strategies, control against 1m,
5155 trades that both runs opened):

- Almost all of it is on trades both runs opened, at the exit. Only 35 trades exist only in the control and 56
  only at 1m; their sums are +0.74 and +0.92 against -1.97 from the common trades.
- Trailing stops are the main cause. For EI3v2 361 trades keep the exit reason `trailing_stop_loss` and lose
  0.93 of a total change of -1.07 in the ratio sum; for E0V1E_DCA3 242 trades explain -1.06 of -1.08. The sign
  is not fixed: for CombinedBinHAndClucV3 28 trailing trades gain +0.61. The coarse candle does not know the
  order of the high and the low inside it, which is the likely reason; what was measured is the effect, not the
  mechanism inside freqtrade.
- Exits that depend on the profit do the same: NFI5MOHO_WIP (`signal_profit_*`) changes on 31 % of its trades,
  -0.29 % per trade.
- A dynamic ROI moves little: UniversalMACD +0.18 over 119 ROI trades.
- A fixed stoploss and a fixed target change nothing: BuyOrDie and SMAOffset show 0 % on every trade. BuyOrDie
  has a trailing stop, but it only starts at +36 % and never triggers in practice.
- A change of the entry set is small, larger for the two DCA strategies (E0V1E_DCA3, SMAOffset_Hippocritical_
  dca_leverage), where a different exit moves the next fill.

**Recommendation for strategies that are tested in the future.**

1. Screen at the granularity that is already run: the 5m detail rerun for strategies above 5m, the own
   timeframe for strategies at or below 5m. Do not apply a flat discount: the single strategies moved between
   -30 % and +19 %, so a discount would correct a third of them in the wrong direction. If a number is needed
   for planning, the pooled effect of 1m over 5m is about -1 % to -3 % of the mean profit per trade.
2. Run 1m detail for a strategy that reaches a shortlist or a specialist designation and whose source declares
   a trailing stop, an exit that depends on the profit (`exit_profit_only`, `custom_exit`/`custom_sell`), or
   position adjustment. A strategy with only a fixed stoploss and a fixed or table ROI does not need it. The
   1m runs took 1 to 2 minutes for most strategies (ClucFiatROI 7, BuyOrDie 19), so a shortlist of a few dozen is
   a matter of hours.
3. Compare a 1m run with a 5m control in the same window and runtime, never with a run that started at another
   date, for strategies that hold positions for months or compound their account.
4. Do not rank strategies with a trailing stop or a profit-dependent exit by differences smaller than about
   30 % of their mean profit per trade; the 5m figure does not resolve them.
5. A strategy that does not finish at 1m within the ceiling is recorded as `1m not measurable`, its 5m figure
   stays with that flag, and the ceiling is not raised.
6. Consider extending the rule of 2026-09-19 to require a 1m rerun for a strategy at or below 5m when its
   source declares one of the mechanisms of point 2. This is a proposal; the current rule stands until decided.

#### 3. Test: the existing 5m detail reruns of strategies above 5m

`bot/detail_5m_deviation.py` compares, for every strategy with a measured 5m detail run, the detail archive
with the canonical archive over the validation window and matches trades by pair and opening candle. 195
strategies have both runs and trades in the validation window: 157 `PASS` and 38 `SENSITIVE`. The report is
`results/regime/rotation_bot/detail_5m_deviation.json`.

- **The bulk does not move.** Median change of the mean profit per trade: 0.000 pp over all 195 and over the 157
  `PASS`. For the 157
  `PASS`, the strategies with a mean of at least 0.3 % per trade (83 of them) have a median absolute change of
  1.5 % and 11 % of them change by more than 20 %. For the 38 `SENSITIVE` (16 with such a mean) the median is
  70 % and 88 % exceed 20 %.
- **What separates them is the declared mechanism.** Strategies whose source declares none of trailing stop,
  custom stoploss and profit-dependent exit (99): median absolute change 0.2 %, 6 % above 20 %. Strategies with a
  trailing stop (61, of these 26 with a mean of 0.3 % or more): median 18.3 %, 46 % above 20 %. Among the 38
  `SENSITIVE`, 23 declare a trailing stop, 24 a dynamic ROI, 10 a profit-dependent exit, 8 a custom stoploss, 3
  position adjustment; one declares none of these.
- **The dominant cause on the common trades of the `SENSITIVE`:** 18 of 38 trailing stop with an unchanged exit
  reason (a different fill price), 7 a changed entry set, 5 ROI with an unchanged reason (timing and price), 2
  stoploss to ROI, and single cases. The same pattern as at 1m: the trailing fill decides, the ROI table and
  the entry set follow.
- **The author timeframe matters.** Median absolute change of the mean per trade, strategies with a mean of at
  least 0.3 %: 15m 4.7 %, 1h 8.3 %, 4h 0.0 % (5 % above 20 %), 1d 16.3 % (47 % above 20 %). The coarse daily
  candle leaves the most room; the 4h group has a median of 0 % but 5 % of it above 20 %. The likely reason is the candle size, which was not tested separately.
- **Percentages of a small base mislead.** The largest relative changes (Chispei, mabStra, Inverse) are on means
  near zero. The comparison above therefore uses percentage points and only counts strategies with a mean of at
  least 0.3 % per trade when it quotes a relative change.

**The runtime confound.** Of the 195, 157 baselines were made in another runtime than their detail run
(`same_runtime` false), among them 33 of the 38 `SENSITIVE`. The `PASS` strategies show that the runtime alone
moves little: same runtime (31) and different runtime (126) both have a median change of 0.000 pp, and the share
above 20 % is 13 % against 10 %. That does not prove it for the 33 `SENSITIVE`. The five `SENSITIVE` with the
same runtime (AdaptiveRegime, MomentumCCITrendStrategy, PatternRecognition, PolymarketMomentumStrategy,
TrendBreakout, all on 4h or 1d) show the same causes: three trailing fill, one a changed entry set, one a
stoploss that became a trailing exit. The other 33 are "sensitive, cause likely the detail candles, runtime not
excluded". A control run of each in the runtime of its detail run without detail candles would settle it; that
is open. Until then a `SENSITIVE` of the 33 stays as classified and carries `control_run_needed` in its record.

#### 4. Reproduction

`python -m bot.detail_1m_batch` (the ten runs), `python -m bot.detail_1m_batch --control` (the 5m controls),
`python -m bot.detail_1m_report` (the table), `python -m bot.detail_1m_causes` (section 2),
`python -m bot.detail_5m_deviation` (section 3). Results under `results/regime/rotation_bot/`. The runs used
`profile_smoke.run_one` with `artifact_key` `val_1m` and `val_5m`, so their archives sit beside the canonical
ones in `user_data/profile_smoke/` and replace none of them.

## 3. Validation window extension (on hold)

*Formerly `VALIDATION_EXTENSION_PLAN.md`, merged here on 2026-09-20 without changes to the text below.*

**On hold (owner decision 2026-09-20): the extension will be carried out at a later date. Nothing is to be started until
the owner asks for it.** The plan stays valid as written; before starting, re-check the window end and the data.

Status: plan only (version 3, 2026-09-20), nothing below has been run except the one-strategy
probe in section 2. Version 2 added the owner's decisions of 2026-09-20 (5m robustness and the
Freqtrade-native figures are extended too) and the two-tier design that follows from them. Version 3
incorporates the review by DeepSeek (deepseek-v4-pro), see section 10.

### 1. Decisions taken by the owner

- The validation window is **extended**; the new days become part of it. There is **no third window**.
- The end is **2026-09-19, the whole day included**: `2026-09-20 00:00 UTC` exclusive, the same convention as
  the old end `2026-08-21` (exclusive).
- The discovery window (trades opened before 2024-01-01) is **not recomputed**. Discovery numbers must stay
  identical (acceptance test 5.1).
- **Model 1/2/3 stay as snapshots** of the old window (they pin the SHA-256 of the old `regime_daily.csv`).
- The **5m robustness run is extended** over the new window (stage 8b), and so are the **Freqtrade-native
  figures** of the page.

Consequence to write down: the untouched-data test of the confirmation rule proposed in Amendment 2026-09-20
("forward hold-out from 2026-08-21") **falls away**, because those days are now validation days. The rule stays a
post-hoc reporting rule.

### 2. Facts from the code and from the probe

| Item | Where | Effect |
|---|---|---|
| Window end, regime data | `regime/regime_engine.py` `END` | must move; regenerates `regime_daily.csv`, episodes, transitions, state summary, distributions, manifest |
| Window end, attribution | `regime/attribution.py` `END` | trades with `open_date >= END` are dropped; must move |
| Canonical baseline window | `evidence/profile_full_window.py` `TIMERANGE` (`20200301`/`20200401` to `20260821`) | **not changed** (see 4.3) |
| Validation start | `specialist_evaluation.VALIDATION_START` = 2024-01-01 | unchanged; no validation end constant exists |
| Benchmark candles | `specialist_evaluation._candle_path`: spot `<PAIR>-1m.feather` | 1m candles must be extended |
| Pins on the regime data | `gated_backtest.py`, `gated_attribution.py`, `model_compare.py`: `regime_daily_sha256` | Model 1/2/3 become stale by hash; kept as snapshots, verifiable with the archived old file via `--daily` |
| Trade readers | `attribution.main` (archive from the pooled manifest), `execution_robustness.build` | both need to read the extension |
| 5m classifier | `execution_robustness.metrics/compare/classify` | thresholds act on the **native compounded** figures of two full-window runs (profit sign, profit change, trade count) |
| Native report table | page: `regime_specialists_page.native_stats` via `model_compare._load_model0(manifest, ids, timerange)` | native report block of a run over the whole window |
| Data | `user_data/data/binance/` (git-ignored). Spot: 8 pairs x 12 timeframes, all ending 2026-08-20 (XMR 2024-02-20, delisted). Futures: 8 pairs x 1m/3m/5m/15m/1h/4h/1d, 1h mark, 1h funding rate, ends not uniform (08-20, 08-26, 09-10, 09-18) | must be extended and normalised |

Probe on one strategy (`simple_vwap_v1`, 4h, spot, scratch directory, repo untouched):

- `freqtrade download-data` appends missing candles: 16 files in 5 s.
- A backtest that starts **60 days before** the old end reproduces the continuous run's trades in the new period
  exactly (17 of 17: pair, opening, closing, rate). Profit ratio differs by up to 2e-5 (stake rounding under
  `stake_amount: unlimited`). With 0, 7, 14, 30 days of run-in, 5, 3, 3, 2 of 17 trades differed; the strategy holds up
  to 28 days.
- Old trades without the window-end `force_exit` trades, plus run-in trades closing on or after the old end, equal the
  continuous run's trade set (3 `force_exit` trades replaced by their continuation).
- 4 to 5 s per run-in run, 21 s for the continuous run.

**What a run-in cannot give:** the native report block and the compounded figures. Profit total, CAGR, Sharpe,
Sortino, Calmar, drawdown and market change come from the equity curve of one continuous run with compounding stake;
they cannot be stitched from two runs. The 5m classifier acts on the same compounded figures. Both therefore need
**continuous full-window runs** over the extended window.

Not tested: futures, 1m, DCA strategies, strategies holding for months, Docker-runtime baselines (168 of 632 were
measured in Docker, 473 native, 91 without a runtime id).

### 3. Design: two tiers

**Tier A, all 632 strategies with a measured baseline: run-in extension.** A second, short backtest over
`[old end - run-in, new end)`. Its archive is registered in a new store
`results/regime/full_backtest_extension_manifest.json`. The trades for the extended window are
`stitch(old, extension)`: old trades that are not `force_exit`, plus extension trades with `close_date >= old end`.
Run-in: the largest of 120 days, twice the longest holding time in the strategy's own old trades, and the strategy's
**settled warm-up plus 30 days** (`settled_days` from the warm-up ladder, up to 365 days). The last term matters: freqtrade
loads only the *declared* `startup_candle_count` before the start of a timerange, and a number of strategies declare none (125 when last counted), so their
indicators start cold at the run-in start. The settled warm-up is the project's own measure of how long an indicator needs.

**Per-strategy convergence check against the old archive**, all of it mandatory:
1. the trades of the run-in run opened in the second half of the overlap equal the old archive's trades of the same range,
   comparing pair, open and close timestamp, open rate, close rate, exit reason and profit ratio (tolerance 1e-4, the stake
   rounding seen in the probe was 2e-5);
2. **the positions open at the old end match**: every old `force_exit` trade must reappear in the run-in run with the same pair,
   open timestamp and open rate and a close on or after the old end. This is the check that matters most, because those are the
   only trades whose fate the state at the old end decides;
3. the number of trades opened per pair in the second half is equal.
On failure the run-in doubles once, then the strategy falls back to Tier B. The first half of the overlap is not compared and
does not need to be: the stitch takes every old trade from the old archive, which is the continuous run by determinism, and
uses the run-in run only for trades that close on or after the old end.
Purpose: validation trades, attribution, cost screen. About one hour, more if run-ins double.

**Tier B, the strategies that need compounded or native figures: continuous full-window reruns over the extended
window.** Set: the 404 universal candidates (native table) united with the 224 strategies with a 5m detail run
(classifier): **466 strategies**. Per strategy: a baseline run over `20200301|0401-20260920`, and for the 224 also the
5m detail run over the same window. Output to new, non-canonical manifests (runner option `--window-end`, allowed only
with a non-canonical `--output`, like `--timeframe-detail`). Recorded elapsed times of the old runs: baseline 45.1 h,
detail 26.4 h, **71.5 h serial**; at the 3.4x speed-up seen with four containers about **21 h wall** as an upper bound
(the probe ran 3x faster than the recorded 62 s, so the real time may be well below). Two baselines and one detail run
already took more than 3000 s; the 3600 s ceiling stays hard, so a few new `ERROR`/timeout results are expected and
are reported, not hidden.

Where both tiers exist for a strategy, the Tier B trades are used, and Tier A serves as an independent acceptance test
of the stitch (5.2).

**Not chosen: a fixed-stake redefinition of the classifier** (mean profit ratio of stitched trades instead of the
compounded profit). It would avoid the detail full reruns but changes a frozen classification; the owner asked for the
existing check to be carried forward.

### 4. Work packages, in this order

#### 4.0 Before anything is run
1. Amendment in `REGIME_PREREGISTRATION.md`: new analysis and validation end (2026-09-20 exclusive), "Scope and causal
   clock" updated, the forward hold-out clause of Amendment 2026-09-20 withdrawn by owner decision, the confirmation rule
   unchanged and post-hoc, Model 1/2/3 declared snapshots of the old window, and the sources of the extended figures
   (Tier A, Tier B) named.
2. State is committed (rollback point). `RUNTIME_ENVIRONMENTS.md` is Codex's and stays untouched.
3. **Pilot before the batch.** At least one strategy from each class the probe did not cover: futures, 1m, DCA, one that holds
   for months (1d), one with no declared `startup_candle_count`, one whose baseline ran in Docker. For each, run Tier A and one
   continuous full-window run over the extended window (in scratch), and compare the trade sets. The batch starts only if the
   pilot converges, or the rule (run-in length, fallback) is changed until it does.

#### 4.1 Data
- Extend spot (8 pairs, XMR only if candles exist; all 12 timeframes; `ETH/BTC` 1h) and futures (the same pairs, the seven
  timeframes, mark, funding rate) with `freqtrade download-data` in the real data directory.
- Acceptance: all files end consistently, no gaps between old end and new end, the old range of every file unchanged
  (hash of the old range before and after), 1m and 5m included.

#### 4.2 Regime classification (pipeline stage 9)
- Move `END` in `regime_engine.py` and `attribution.py`; keep one definition if that changes no behaviour. Rerun the engine.
- Acceptance: **every** row of `regime_daily.csv` before the old end (states, ADX, features, episode ids) equals the old file.
  What may change: the episode table rows of episodes that were still open at the old end (their end date and length grow), and
  with it the buy-and-hold benchmark of those episodes, hence the excess return of the trades inside them. That is the effect of
  the extension, not an error; list those episodes and the trades and rows they touch. The six-phase thresholds are frozen
  numbers.
- Copy the old `regime_daily.csv` under an archive name for the Model 1/2/3 snapshot (`--daily`).

#### 4.3 Extension runners
- New module `regime/window_extension.py` (Tier A) and a `--window-end` option in `regime/full_backtest.py` (Tier B),
  both modelled on the existing runner: same eligibility (`E1_expanded` with a measured baseline), repair overrides,
  data-file staging, config and, where it matters, runtime.
- Do **not** change `profile_full_window.TIMERANGE`: its identity check covers source and config hash only, not the
  window, so a change would make the runner treat all old results as current for a window they were not measured on.
- The extended results live in separate manifests. `choose_detail_records` currently picks any
  `execution_robustness_detail_*.json` record per strategy by status and time; it must select by window, or extended and
  old records would be mixed.
- Runtime: every run uses the runtime id of the strategy's old baseline (168 Docker, 473 native, 91 without an id, treated as
  native), for Tier A as for Tier B. If the convergence check fails for a Docker baseline that was run natively, repeat that run in
  Docker before doubling the run-in. The check therefore doubles as a detector of runtime differences.
- Workers: Tier A 4 in parallel. Tier B detail runs in Docker with `runtime/detail_batch_parallel.py` (4 containers, 3.5 GB each,
  solo repeat for OOM and timeouts) extended by the window option; Tier B baselines native or Docker as above. Never run two
  big batches at once.
- The 3600 s ceiling is not raised for anyone. Runs whose recorded time was above 3000 s (two baselines, one detail run) go first
  and alone, so that their outcome is known early; a timeout keeps the old-window figure, labelled.

#### 4.4 Readers
- `regime/attribution.py`: trades per strategy come from the Tier B extended archive where it exists, else from the
  stitch of Tier A. The provenance goes into a new column `trade_source` (`canonical`, `stitched`, `extended_full`).
  Stitched trades come from two stake histories, so **no consumer may sum `profit_abs` across stitched trades and call it a
  result**: the evaluation uses `profit_ratio` with the fixed 1000 USD convention and is not affected; the descriptive
  attribution summaries (`strategy_*_summary.csv`) sum `profit_abs`, so they carry the source and are labelled. A flag switches
  the extension off.
- `evidence/execution_robustness.py`: classification on the extended baseline against the extended detail run (same
  thresholds, no change to the rule); cost screen (whole and per ADX state) on the extended trades. Strategies without an
  extended pair stay `PENDING` for the extended window and are listed; the status table names the window of every value.
- Native table on the page: `model_compare._load_model0` already takes a manifest path and a timerange; point it at the
  extended manifest.
- The 166 strategies outside Tier B are neither in the native table (it lists the universal candidates) nor classified by 8b
  (no 5m detail run; strategies at or below 5m pass by rule). Their native figures are used nowhere; they need Tier A only. The
  status table's trade counts (`pft`) stay those of the canonical window and are labelled so.
- `specialist_evaluation.py`, `discovery_comparison.py`: unchanged.
- Page tools and templates: hard-coded dates become tokens (two `2026-08` mentions in the specialists template, four
  `2026082x` in the status template); Model 1/2/3 blocks labelled as snapshots until 2026-08-20.

#### 4.5 Order of execution, and what is shown when
1. Data, regime data, Tier A (about two hours in total). Then attribution, evaluation, comparison and pages show the
   extended validation window; the native table and the 5m column still show the old window, **labelled as such**.
2. Tier B in the background (about a day of wall time at worst). When its batches finish, the native table, the 5m
   classification and the cost screen switch to the extended window; both pages are rebuilt.
The owner accepts the interim state only if it is labelled; otherwise nothing is published until Tier B is complete.

### 5. Acceptance tests
1. **Discovery invariance:** discovery columns of `discovery_vs_validation.csv` identical before and after.
2. **Stitch check:** for every strategy in both tiers, Tier A stitched trades equal the Tier B trades (pair, open, close,
   rate); ratios within 1e-4.
3. Trade counts before the old end equal the old counts minus the replaced `force_exit` trades.
3b. The evaluation's benchmark for validation trades opened in the new period is present for every matched trade (1m candles
    reach the new end).
4. Regime data: prefix identical (4.2). Data: 4.1.
5. Selftests of `regime.attribution`, `regime.specialist_evaluation`, `evidence.execution_robustness` pass.
6. Extension manifest: one entry per baseline strategy, each with status, run-in, convergence result, tier and runtime;
   no unexplained status.
7. Report how many strategies changed tier, rank, robustness status or confirmation label.

### 6. Documents, pages, git
- `PIPELINE.md` (stages 8, 8b, 9, 10, 13), `HANDOFF.md`, `EXECUTION_ROBUSTNESS_PLAN.md`, the window table in the status
  page and in `strategy_status.py`; both pages rebuilt and republished with a fresh timestamp.
- `results/regime/trade_regime_attribution.csv` grows by about 1 to 2 percent; each commit of it uploads a new LFS object of
  about 1.4 GB. Decide when to commit it. Extension archives live under `user_data/profile_smoke/` (git-ignored).
- New result stores (extended baseline, extended detail, extension manifest) are inputs and are committed like the old ones.

### 7. Risks and open points
1. Convergence of Tier A is proven on one simple strategy; the pilot (4.0) and the per-strategy check with the Tier B fallback are
   the safeguards.
1b. The extension adds about 30 days to a validation window of about 2.7 years. Few new episodes per phase are expected (about 3
    coin episodes for bull and bear across all coins in that time), so most rows will move little; the purpose is completeness,
    not power.
2. Under `stake_amount: unlimited` stakes differ between run-in and continuous run; ratios differ by about 1e-5. Any figure
   that sums `profit_abs` of stitched trades mixes two stake histories; check where `profit_abs` is used (attribution
   summaries do). Tier B trades are continuous and free of this.
3. XMR has no candles after 2024-02-20; run-in runs have seven pairs and freqtrade reduces `max_open_trades` from 8 to 7.
   No effect in the probe; the checks would show it.
4. Tier B may push a few long strategies over the 3600 s ceiling; they are reported as `ERROR`/timeout for the extended
   window and keep their old-window figures, labelled.
5. Docker runtime: 168 baselines were measured there. Cross-runtime comparisons stay flagged as before.
6. All published numbers of the ranking, tiers, robustness, confirmation and universal lists may change; old figures stay in
   git history.

### 8. Time estimate
| Step | Estimate |
|---|---|
| Amendment | 20 minutes |
| Data | minutes |
| Regime rerun and prefix check | not measured, expected minutes |
| `window_extension.py`, `--window-end`, reader changes, detail-store selection by window | 3 to 4 hours of work |
| Tier A, 632 strategies | 1 to 3 hours serial, under one hour with 4 workers |
| Attribution, evaluation, comparison, pages (interim publication) | about 15 minutes |
| Tier B, 466 baselines and 224 detail runs | 71.5 h serial by recorded times, at worst about 21 h wall |
| Final rebuild after Tier B | about 15 minutes |

### 9. Rollback
All changes are additive: new manifests and archives, two `END` constants, one flag each in attribution and the runner,
regenerated outputs. To go back: restore the two constants, delete the extended manifests, regenerate from the committed state.
The old `regime_daily.csv` and every old archive are kept.

### 10. Review by DeepSeek (deepseek-v4-pro), and what was done with it

The plan (version 2) was submitted with the request to find what is overlooked. Ten objections came back. Assessment:

| Objection | Verdict | Action |
|---|---|---|
| Validation is no longer independent; the confirmation rule is post-hoc; suggests keeping a hold-out or calling the new days a sensitivity analysis | Correct as a statement, and already recorded in section 1. The owner decided against a third window. | Kept. The amendment and both pages say that the validation window was extended after its results were known and that the rule is post-hoc. The suggestion of a hold-out contradicts the owner's decision and is not followed. |
| Convergence check covers only the second half of the overlap | Partly wrong: the first half is not used by the stitch (old trades come from the old archive, which is the continuous run). The risk is the state at the old end. | Check extended to the positions open at the old end (point 2 in section 3). |
| Only open rate compared, not close rate, exit reason, profit | Correct | Added to the check. |
| Run-in ignores indicator lookback | Correct in substance and sharper than stated: many strategies declare no `startup_candle_count`, so their indicators start cold. | Run-in includes the settled warm-up plus 30 days (section 3). |
| Episode assignment of the last open episode may change | Correct that the benchmark of open episodes changes; wrong that ids or states change (the classification is causal). | Acceptance test made exact (4.2); the changed episodes are listed. |
| 166 strategies outside Tier B keep old native figures | Not a gap: those figures are used nowhere. | Stated explicitly (4.4). |
| Docker and native mix | Correct | Runtime per strategy fixed to the old baseline's; the check detects differences (4.3). |
| Tier B timeouts; suggests a longer timeout | The risk is correct. A longer timeout is excluded by the standing rule that 3600 s is a hard ceiling. | Slow runs go first and alone, outcome labelled (4.3). |
| Benchmark from 1m candles not updated explicitly | Covered by 4.1, made an explicit acceptance test | Test 3b added. |
| Only one strategy tested | Correct | Pilot over the missing classes before the batch (4.0). |

## 4. Regime rotation bot: variants and their preregistered rules

The bot (`bot/RegimeRotationBot.py`) runs one component per ADX phase: Buy-and-Hold in the BTC uptrend, EI3v2 in the
BTC downtrend, Ichimoku in coin SIDEWAYS, BuyOrDie in coin TRANSITION. It is evaluated by `bot/rotation_eval.py` from
per-pair backtests (`bot/run_rotation.py`, 5m with 1m detail, futures, 0.1 % fee and 0.1 % slippage per side). This part
holds the rule of each variant *before* the variant is run. It changes no regime label, no threshold of the study and no
stage of the chain.

### 4.1 Result of the base variant (`RegimeRotationBot`), read before the rule below was written

Validation window, daily return on provided capital (fixed stake, eight slots): whole bot 0.083 %, hold alone 0.100 %.
Compounded growth factor over the window: whole bot 1.14, hold alone 1.58, equal-weight Buy-and-Hold 1.08. In the
discovery window the whole bot was ahead of hold alone (0.145 % against 0.134 % per day; factor 4.65 against 3.97). Per
component in the validation window: hold +0.100 %, EI3v2 +0.004 % (the only confirmed one), Ichimoku +0.003 %, BuyOrDie
-0.025 % (negative in both windows). So the components other than hold subtract in the validation window. The
validation numbers of this variant were known when the rule below was written; that is disclosed here and it limits
what a later read of the validation window can prove.

### 4.2 Rule for `RegimeRotationBotV2` (written 2026-09-20, before V2 was run)

1. **Choice of component per phase, from the discovery window only** (2020-04-01 to 2023-12-31). For each of the phases
   BTC bear, coin sideways and coin transition there are three options: the component, Buy-and-Hold of the coin for the
   length of the phase (1x, entry when the phase starts, exit when it ends, same costs), and cash. An option other than
   cash is taken only if the one-sided 95 % lower confidence bound of its mean net return per phase episode is above
   0 in the discovery window (t bound over episodes, as `episode_excess_lcb`, but against cash, not against Buy-and-Hold).
   Among the options that pass, the one with the highest mean net return per episode is taken; if none passes, the
   phase is cash. Nothing from the validation window enters this choice. The bound instead of the plain maximum guards
   against picking the best of several noisy numbers.
2. **Phase confirmation.** A change of the BTC or of the coin state is accepted only after the new raw state has held for
   `N = 2` consecutive days. `N` is fixed, not searched. The regime labels themselves are not changed; the
   confirmation is bot logic. The hold in the BTC uptrend is subject to the same confirmation.
3. **Reading.** V2 is read once on the validation window and reported whichever way it falls, next to the base variant,
   hold alone and equal-weight Buy-and-Hold. To separate the two changes, the same component choice with `N = 1` is
   run and reported (`RegimeRotationBotV2N1`); it is a decomposition and does not choose `N`.
4. **Account model.** The primary figures stay those of the slot model (eight slots, fixed stake), so V2 is comparable
   with the base variant. Added for both variants, as a second reading: a pooled account (one capital; the stake of a
   new trade is the free capital divided by the number of free slots, as Freqtrade's `stake_amount: unlimited` does),
   computed from the trade list. It is reported beside the slot model and never replaces it.
5. **Not tested here:** 2x hold, shorts and the coin-downtrend variant stay stopped (owner, 2026-09-20).

A second read of the validation window after a further change would no longer be out of sample. The forward hold-out
of the confirmation rule (Part 3 and `REGIME_PREREGISTRATION.md`, Amendment 2026-09-20) is the test that does not
depend on it, and it is on hold.

### 4.3 Result of V2, read once on the validation window (2026-09-20)

Choice per phase (`python -m bot.phase_choice`, discovery only; `results/regime/rotation_bot/phase_choice.json`): BTC bear
goes to cash (EI3v2: mean +0.34 % per episode, lower bound -0.44 %), coin sideways keeps Ichimoku (+1.31 %, lower bound
+0.40 %), coin transition goes to cash (BuyOrDie -0.79 %). Note that the bound is against cash. EI3v2 is confirmed
against Buy-and-Hold in the specialist evaluation and still fails here, because most bear episodes contain no trade of
it; the two rules ask different questions.

Reproduce: `python -m bot.run_rotation <variant>` for each variant, then `python -m bot.rotation_eval <variants>`;
figures are in `results/regime/rotation_bot/<variant>.json`.

| Validation window | Base | V2N1 (choice only) | V2 (choice and N=2) | Hold alone (base) |
|---|---|---|---|---|
| Daily return on provided capital | 0.083 % | 0.102 % | 0.074 % | 0.100 % |
| Growth factor, slot model | 1.14 | 1.55 | 1.32 | 1.58 |
| Growth factor, pooled account | 1.36 | 1.72 | 1.45 | 1.71 |
| Worst fall of the pooled account | -37.5 % | -24.0 % | -33.6 % | -20.8 % |
| Trades | 979 | 307 | 288 | 120 |

Equal-weight Buy-and-Hold of the same pairs: factor 1.08. In the discovery window the same three variants reach 0.145 %,
0.178 % and 0.146 % per day and pooled factors 4.05, 7.49 and 4.52.

Reading, without re-tuning:

- **The component choice worked as intended (V2N1).** It stops the subtraction: the bot now earns as much as hold
  alone (0.102 % against 0.100 %, pooled factor 1.72 against 1.71) and clears the 0.08 % target. Ichimoku in sideways adds
  about 0.002 % per day to hold, which cannot be told from zero. What was gained is that nothing is lost, not that
  something is added.
- **The preregistered V2 with `N = 2` is worse than the choice alone.** The confirmation delays the entry into the BTC
  uptrend by a day and its exit by a day; the hold component falls from 0.100 % to 0.057 % per day and from 120 to 104
  trades. The phase takeovers fall from 74 to 20 already without the confirmation, so the churn it was meant to remove
  came from the removed components, not from state flicker.
- **Consequence.** `N = 2` is rejected on the validation window and is not adopted. Taking V2N1 as the new base is a
  choice made after reading the validation window; a further variant read on the same window is no longer out of sample,
  so any such step waits for a window that has not been read (the forward hold-out of Part 3, on hold).
- **Limits.** The pooled account concentrates: with few open positions one trade gets all free capital, hence the falls
  above. Validation numbers of the base variant were known when the rule was written (4.1). A single window and one
  path of eight correlated coins; no confidence interval was computed for the differences above.

### 4.4 Rule for the component search and for the 2x hold (written 2026-09-21, before either was run)

Question: can any strategy of the corpus earn more than cash in the phases where the bot sits idle (BTC bear, coin
sideways, coin transition), and what does a 2x hold do to the daily return? The owner ordered both on 2026-09-21 and
ordered that the four weeks up to 2026-09-19 are **not** added to any window.

**Component search** (`bot/component_search.py`).

1. *Phases and episodes* are those of the bot (4.2): BTC bull is hold, BTC bear is bear, otherwise the coin's own
   sideways or transition. An episode is a run of consecutive days of one coin in one phase. A strategy's return in an
   episode is the sum of the net returns of its trades that opened in it, 0 if it has none. Net is the profit ratio
   less 0.1 % slippage per side, times leverage.
2. *Candidates:* every strategy with a canonical Model 0 trade list, `cohort == E1_expanded` and
   `execution_robustness_status == PASS`, plus the four components of the bot (EI3v2, Ichimoku, BuyOrDie, and Buy-and-Hold
   of the coin for the phase). At least 30 trades opened in the phase in the training window. The execution status is
   read from a whole-run comparison and uses no phase result; the cost screen of the specialist page is not used,
   because it is judged on the validation window.
3. *Test:* per (candidate, phase), a one-sided t-test that the mean episode return is above 0 against cash, over all
   episodes of the phase in the training window. The Benjamini-Hochberg procedure at q = 0.10 is applied over all
   (candidate, phase) tests together. Only passers are eligible. The first pass assumes leverage 1 (the attribution
   table carries none); for the passers the archive's own leverage is read and the test repeated with the true costs;
   a passer that fails it drops out.
4. *Choice:* per phase the eligible candidate with the highest mean episode return in the training window; if none, cash.
5. *Check of the procedure (walk-forward inside discovery):* training window 2020-04-01 to 2022-12-31, test window 2023.
   Reported for each phase: the number of passers, the mean 2023 episode return of the chosen candidate, of all
   passers, and of all candidates with the floor (the "no selection" reference), and the share of passers with a
   positive 2023 mean. If the chosen candidates do not do better than the reference in 2023, the selection has no
   demonstrated value and is reported as such.
6. *Final choice:* training window is the whole discovery window (2020-04-01 to 2023-12-31). The portfolio is hold in the
   BTC uptrend plus the chosen candidate of each phase, evaluated in the slot model (one slot per coin and day, fixed
   stake; the pooled account is not computed for the portfolio because trades of different candidates may overlap on
   one pair). The validation window is read for information and is labelled as no longer out of sample: its numbers
   for the bot were known, and the specialist page has shown the validation results of every strategy.

**2x hold.** `RegimeRotationBotV2N1x2` is `RegimeRotationBotV2N1` with `hold_leverage = 2.0`, backtested per pair like
every variant (5m, 1m detail, futures, isolated). Reported next to V2N1: daily return, factors, worst fall of the pooled
account, liquidations. The portfolio of the component search is reported once with the 1x and once with the 2x hold
trades. Nothing is chosen from this; it is a measurement of what the leverage does.
