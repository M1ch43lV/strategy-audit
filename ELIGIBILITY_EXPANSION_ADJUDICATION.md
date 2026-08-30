# Eligibility expansion adjudication

This report overlays new prospective evidence without rewriting the frozen
67-row E0 result in `REGIME_ELIGIBILITY.csv`.

| Strategy | Status | Lookahead | Recursive adapter | Exact full trades |
|---|---|---|---|---|
| `AlwaysBuy` | `admitted_E1` | `PASS` | `PASS` | `true` |
| `HourBasedStrategy_5m` | `admitted_E1` | `PASS` | `PASS` | `true` |

Current E1 count: **69** = 67 frozen E0 profiles + 2 newly adjudicated profile(s).

Admission here does not start Stage 9 or inspect regime rankings. Newly
admitted profiles still require identity-bound pooled Stage 7 attribution
before they can contribute to the expanded regime analysis.
