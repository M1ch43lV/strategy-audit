# Eligibility expansion protocol

**Status:** accepted and frozen on 2026-08-30, before Stage 9 ranking
**Purpose:** maximize the number of strategies that can be evaluated across
market regimes without admitting future leakage, unresolved evidence, duplicate
implementations, or behavior-changing repairs into confirmatory claims.

This protocol is an amendment to the completed Stage 6 measurement campaign.
It does not erase or relabel the frozen 67-profile result. It creates a
prospective expansion campaign whose repair rules, candidate universe, and stop
conditions are fixed before any strategy-by-regime ranking is inspected.

## 1. Estimands and populations

The confirmatory target population is:

> The deduplicated public Freqtrade `strategy_id x native run_profile`
> implementations that can be measured honestly after the repair rules frozen
> here and that then satisfy every original technical eligibility gate.

This is not an estimate for all 900 source profiles. It is conditional on
successful measurement and validation under this protocol.

Four evidence populations are retained:

| Code | Population | Use |
|---|---|---|
| `E0_strict67` | The 67 profiles frozen at the completed Stage 6 checkpoint | Mandatory nested confirmatory sensitivity and provenance baseline |
| `E1_expanded_confirmatory` | E0 plus newly validated profiles that pass every original gate after a permitted equivalent repair or completed missing diagnostic | Expanded confirmatory analysis |
| `E2_drift_sensitivity` | Profiles with recursive drift whose decisions are exactly invariant under the frozen tests but whose recursive diagnostic remains `FOUND` | Sensitivity only |
| `E3_derived_exploratory` | `behavior_changed`, lookahead-rewritten, trap-corrected, or otherwise behavior-changing variants | Separate exploratory analysis only |

One `strategy_id x run_profile` contributes at most one canonical
implementation to E0 or E1. Original and repaired variants are never counted as
independent strategies.

## 2. Rules that do not change

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

## 3. Frozen candidate waves

The machine-readable candidate manifest is derived only from the current
technical artifacts. Candidate membership must be hashed before the first new
measurement.

### Wave A - seven pending diagnostics

Process all seven current `pending_diagnostics` rows. Diagnostic limitations may
be repaired only at the harness, dependency, resource, or provably equivalent
metadata layer. No entry or exit rule may change.

### Wave B - warm-up refusals

Process all 82 rows that meet all of the following at the frozen checkpoint:

- sole hard reason `recursive_bias_found`;
- `recursive_kind=refused_no_warmup`;
- no pending reason.

Determine the required startup history from the strategy's complete indicator
and informative-timeframe dependency graph. A startup metadata change may enter
E1 only after the equivalence and full rerun requirements below are met.

### Wave C - canonical measurement recovery

Inventory all 230 rows whose sole hard reason is
`canonical_implementation_not_measured`. Before execution, report missingness by
repository, native run profile, timeframe, artifact role, repair provenance,
runtime status, strategy family, and dependency/runtime class.

The queue is exhaustive rather than opportunistic: every row receives a
terminal classification under the same rule set. Artifact-role review and an
unknown execution profile must be resolved before measurement. Successful load
or smoke execution is not eligibility; full measurement and both bias gates
still follow.

### Wave D - measured recursive drift

Process the 124 rows whose sole hard reason is recursive bias, whose subtype is
`drift_measured`, and which have no pending evidence. These rows cannot enter E1
while recursive status remains `FOUND`.

A permitted equivalent repair followed by a fresh recursive `PASS` may admit a
row to E1. If status remains `FOUND` but all frozen decision-invariance checks
pass, the row may enter E2 only. Failed invariance remains excluded.

### Later behavior-changing work

Lookahead rewrites, persistent recursive corrections, trailing/ROI trap
corrections, and entry-rule changes needed to create trades belong to E3. They
are attempted only after E1 is frozen and cannot enlarge confirmatory evidence.

## 4. Permitted repair boundary

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

## 5. Equivalence and decision-invariance evidence

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

### 5.1 Zero-warm-up analyzer adapter

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

## 6. Measurement and resource protocol

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

## 7. Stop rule

The expansion ends when every row in Waves A-D has one terminal state:

- admitted to E1 after every original gate passes;
- retained in E2 after frozen decision-invariance evidence;
- assigned to E3 because the required repair changes behavior;
- hard ineligible with a demonstrated technical failure; or
- pending after the fixed diagnostic/resource attempts are exhausted.

There is no target survivor count. In particular, 156 is only the arithmetic
ceiling from E0 plus Waves A and B, not a success criterion or forecast. The
protocol does not stop early after reaching a desirable count and does not add
new repair classes after inspecting rankings.

E1 membership and all input/code/result hashes are frozen before Stage 9 is
rerun. E0 is never overwritten.

## 8. Statistical safeguards after expansion

- Report E0 and E1 results side by side for every confirmatory conclusion.
- Preserve original/repaired provenance and report their strata.
- Treat copy families as dependence clusters; report family-clustered bootstrap
  or hierarchical uncertainty and an equal-family-weight sensitivity.
- Reuse the audit's Benjamini-Hochberg and Benjamini-Yekutieli procedures where
  inferential multiplicity correction is applicable.
- Keep discovery and validation separated; failed validation candidates are not
  replaced.
- Never describe 286,616 trades, or any larger expanded trade count, as the
  number of independent strategy observations.

## 9. Required artifacts

The expansion produces:

- `ELIGIBILITY_EXPANSION_MANIFEST.json` - frozen inputs, candidate IDs, hashes,
  waves, rules, and stop conditions;
- `ELIGIBILITY_EXPANSION_CANDIDATES.csv` - row-level wave and terminal status;
- `ELIGIBILITY_EXPANSION_MISSINGNESS.csv` - Wave C missingness inventory;
- `ELIGIBILITY_EXPANSION.md` - counts, repairs, failures, pending rows, E0/E1/E2/E3;
- append-only technical result artifacts keyed by canonical identity;
- regenerated eligibility and pooled Stage 7 artifacts only after E1 is frozen.

No strategy-by-regime ranking is read or generated while this protocol is being
implemented.
