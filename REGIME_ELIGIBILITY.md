# Regime eligibility — technical Stage 6

This table is keyed by `strategy_id × run_profile` and uses the single
canonical implementation selected in `EXECUTION_PROFILES.csv`. It is frozen
before any regime-performance ranking. Here, eligibility means admission to
the Stage 7 regime backtests; it is not approval for live trading.

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
Until `REGIME_COVERAGE.csv` supplies a `PASS` for a strategy/run-profile row,
that row remains `pending_diagnostics` rather than being called eligible.
At the current checkpoint, 31 rows pass all gates including coverage; 0 pass
every other gate and wait only for coverage.

The coverage input schema is `strategy_id,run_profile,coverage_status,coverage_evidence`.
`coverage_status` is `PASS`, `FAIL`, or `PENDING`; evidence should identify the
pair/timerange completeness check that produced the status.

## Current status

| Status | Strategies |
|---|---:|
| `eligible` | 31 |
| `ineligible` | 751 |
| `pending_diagnostics` | 118 |

## Native run profiles

| Run profile | Strategies |
|---|---:|
| `futures_long` | 37 |
| `futures_long_short` | 61 |
| `futures_short` | 3 |
| `spot_long` | 798 |
| `unknown` | 1 |

## Exclusion reasons

Reasons are non-exclusive.

| Reason | Strategies |
|---|---:|
| `behavior_changed_primary_exclusion` | 1 |
| `canonical_implementation_not_measured` | 278 |
| `lookahead_found` | 43 |
| `no_trades_in_full_measurement` | 5 |
| `recursive_bias_found` | 477 |
| `technical_trap_found` | 42 |

## Pending reasons

Reasons are non-exclusive and are counted across all rows. A row already
excluded by one hard failure may still record a missing, orthogonal diagnostic;
hard exclusion takes precedence over pending status. The same diagnostic
cannot be both failed and pending on one row.

| Reason | Strategies |
|---|---:|
| `artifact_role_requires_review` | 14 |
| `exact_regime_window_coverage_not_verified` | 80 |
| `execution_profile_unresolved` | 1 |
| `futures_mode_bias_diagnostics_not_completed` | 57 |
| `lookahead_not_completed` | 595 |
| `native_mode_not_runtime_validated` | 278 |
| `output_equivalent_requires_canonical_bias_rerun` | 4 |
| `recursive_bias_not_completed` | 191 |
| `zero_trades_in_smoke_requires_full_window` | 13 |

The machine-readable row-level record is `REGIME_ELIGIBILITY.csv`.
