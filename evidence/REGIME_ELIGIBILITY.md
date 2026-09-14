# Regime eligibility — technical Stage 6

**Historical-invalidity warning:** this generator reproduces the Stage 6 E0
classification. E0 was retired on 2026-09-03 because its 67 rows had not all
completed one uniform audit chain. A `regime_eligible=true` value here grants
no current admission and must never be used as fallback evidence.

This table is keyed by `strategy_id × run_profile` and uses the single
canonical implementation selected in `evidence/EXECUTION_PROFILES.csv`. It is frozen
before any regime-performance ranking. At the time, eligibility purported to
mean admission to Stage 7; that interpretation is no longer valid.

## Rule

`regime_eligible=true` requires all of the following:

1. the canonical implementation was measured in its native mode;
2. a full measurement produced trades (a zero-trade smoke is pending, not a
   final no-trade exclusion);
3. look-ahead and recursive-bias diagnostics passed;
4. exact pair/candle coverage of the frozen regime window passed;
5. no published technical trap was found;
6. the canonical implementation is not `behavior_changed`;
7. `output_equivalent` overlays have canonical bias reruns before admission.

Profit, significance, buy-and-hold performance, source archetype, and cluster
membership are deliberately absent. `pending_diagnostics` means evidence is
missing; it does not mean pass or fail. Futures PASS values are not inherited
from historical spot diagnostics.

Coverage uses available pair history, matching the existing audit. Exact pair
and candle coverage for the frozen regime window is a hard Stage 7 precondition.
Until `evidence/REGIME_COVERAGE.csv` supplies a `PASS` for a strategy/run-profile row,
that row remains `pending_diagnostics` rather than being called eligible.
In this historical classification, 121 rows pass all gates including coverage; 0 pass
every other gate and wait only for coverage.

The committed report and CSV are immutable provenance of the invalid E0
classification and are deliberately not regenerated. Do not combine their 67
rows with an expansion count. Quote usable strategies only from active
`admitted_E1` decisions in `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`, exposed as
`cohort=E1_expanded` in `STRATEGY_STATUS.csv`.

The coverage input schema is `strategy_id,run_profile,coverage_status,coverage_evidence`.
`coverage_status` is `PASS`, `FAIL`, or `PENDING`; evidence should identify the
pair/timerange completeness check that produced the status.

## Current status

| Status | Strategies |
|---|---:|
| `eligible` | 121 |
| `ineligible` | 969 |
| `pending_diagnostics` | 279 |

## Native run profiles

| Run profile | Strategies |
|---|---:|
| `futures_long` | 56 |
| `futures_long_short` | 140 |
| `futures_short` | 14 |
| `spot_long` | 1152 |
| `unknown` | 7 |

## Exclusion reasons

Reasons are non-exclusive.

| Reason | Strategies |
|---|---:|
| `behavior_changed_primary_exclusion` | 1 |
| `canonical_implementation_not_measured` | 150 |
| `lookahead_found` | 68 |
| `no_trades_in_full_measurement` | 321 |
| `recursive_bias_found` | 468 |

## Pending reasons

Reasons are non-exclusive and are counted across all rows. A row already
excluded by one hard failure may still record a missing, orthogonal diagnostic;
hard exclusion takes precedence over pending status. The same diagnostic
cannot be both failed and pending on one row.

| Reason | Strategies |
|---|---:|
| `artifact_role_requires_review` | 28 |
| `exact_regime_window_coverage_not_verified` | 357 |
| `execution_profile_unresolved` | 7 |
| `futures_mode_bias_diagnostics_not_completed` | 177 |
| `lookahead_not_completed` | 848 |
| `native_mode_not_runtime_validated` | 203 |
| `output_equivalent_requires_canonical_bias_rerun` | 5 |
| `recursive_bias_not_completed` | 668 |
| `zero_trades_in_smoke_requires_full_window` | 51 |

The machine-readable row-level record is `evidence/REGIME_ELIGIBILITY.csv`.
