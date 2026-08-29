# Regime candle coverage — Stage 6 evidence

This report inventories the unversioned Freqtrade candle files used by the
native execution profiles. The machine-readable result is
`REGIME_COVERAGE.csv`; its policy is frozen in
`REGIME_COVERAGE_POLICY.json`.

The checked window is `2020-03-01T00:00:00Z` through `2026-08-21T00:00:00Z` (exclusive end). A documented
listing/delisting boundary is valid available history. Exchange-wide gaps
shared by every pair active at that timestamp are recorded and accepted;
pair-specific holes, duplicates, non-monotonic data, missing files, and bad
temporal edges remain `PENDING`.

Raw candle files are deliberately not committed. `source_fingerprint` binds
each result to file size, temporal edges, row count, and duplicate count.

## Status

| Status | Strategy profiles |
|---|---:|
| `PASS` | 864 |
| `PENDING` | 36 |

## Run profiles

| Run profile / status | Strategies |
|---|---:|
| `futures_long / PASS` | 37 |
| `futures_long_short / PASS` | 58 |
| `futures_long_short / PENDING` | 3 |
| `futures_short / PASS` | 3 |
| `spot_long / PASS` | 766 |
| `spot_long / PENDING` | 32 |
| `unknown / PENDING` | 1 |

## Pending data conditions

Counts are row counts and may overlap.

| Condition | Rows |
|---|---:|
| Unsupported, missing, or unknown timeframe/profile | 35 |
| One or more required pair files missing | 0 |
| One or more temporal edges incomplete | 1 |
| Futures mark/funding feed incomplete | 0 |
| Pair-specific interior gaps | 0 |
| Duplicate candles | 0 |

The policy explicitly limits spot `XMR/USDT` at its documented 2024-02-20
Binance delisting boundary. This preserves the audit's pair-available-history
design while exposing the changing basket composition rather than pretending
that all eight pairs existed for the whole window.
