# Regime audit preregistration

**Status:** frozen for feature generation and attribution; ranking choices marked
`OPEN` below must be resolved before Stage 9 produces any ranked strategy table.

## Scope and causal clock

The canonical, deduplicated strategy corpus and its native run profiles are
defined by `EXECUTION_PROFILES.csv`. Technical admission is defined only by
`REGIME_ELIGIBILITY.csv`; whole-window profit is not an admission rule.

The analysis window is 2020-03-01 00:00 UTC through 2026-08-21 00:00 UTC
(exclusive end). A daily candle is usable only on the following UTC day. No
feature, label, gate, or attribution may use the still-open daily candle.

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
