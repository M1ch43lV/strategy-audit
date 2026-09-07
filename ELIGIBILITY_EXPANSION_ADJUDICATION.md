# Eligibility expansion adjudication

This legacy report records prospective evidence without rewriting the
historical 67-row E0 artifact in `REGIME_ELIGIBILITY.csv`. E0 was later
invalidated as a cohort and contributes zero admissions. Only active
`admitted_E1` rows in the current adjudication CSV define usability; never add
67 to the count in this report.

Two admission routes exist, and a row's route decides what evidence it
owes. `zero_warmup_adapter` covers a strategy that declares no warm-up:
the recursive analyzer refuses such a row outright, so a verdict exists
only through the frozen adapter of plan 5.1. Because a value was supplied
that the author never wrote, those rows additionally owe exact trade
equivalence and a file-specific static proof. `native_gate` covers a row
that was simply never measured and, once measured, passed the original
gates unaided. Nothing was supplied to it, so an equivalence proof for an
override that was never applied does not apply and is reported as
`not_applicable` rather than as a missing proof.

| Strategy | Status | Route | Lookahead | Recursive | Exact full trades |
|---|---|---|---|---|---|
| `AlwaysBuy` | `admitted_E1` | `zero_warmup_adapter` | `PASS` | `PASS` | `true` |
| `BinHV45` | `admitted_E1` | `zero_warmup_adapter` | `PASS` | `PASS` | `true` |
| `BinHV45_kanaxe` | `admitted_E1` | `zero_warmup_adapter` | `PASS` | `PASS` | `true` |
| `BinHV45_stash` | `admitted_E1` | `zero_warmup_adapter` | `PASS` | `PASS` | `true` |
| `BinHV45_werkkrew` | `admitted_E1` | `zero_warmup_adapter` | `PASS` | `PASS` | `true` |
| `BollingerBandStrategy` | `admitted_E1` | `zero_warmup_adapter` | `PASS` | `PASS` | `true` |
| `CCI_BB` | `admitted_E1` | `zero_warmup_adapter` | `PASS` | `PASS` | `true` |
| `HourBasedStrategy_5m` | `admitted_E1` | `zero_warmup_adapter` | `PASS` | `PASS` | `true` |
| `NowoIchimoku5mV2` | `admitted_E1` | `native_gate` | `PASS` | `PASS` | `not_applicable` |
| `ObeliskIM_v1_1` | `admitted_E1` | `native_gate` | `PASS` | `PASS` | `not_applicable` |
| `simple_patterns` | `admitted_E1` | `native_gate` | `PASS` | `PASS` | `not_applicable` |

Rows admitted by this legacy adjudicator output: **11**. The current E1 total
must be computed from active `admitted_E1` rows in
`ELIGIBILITY_EXPANSION_ADJUDICATION.csv` or `cohort=E1_expanded` in
`STRATEGY_STATUS.csv`; it is not 67 plus this number.

Admission here does not start Stage 9 or inspect regime rankings. Newly
admitted profiles still require identity-bound pooled Stage 7 attribution
before they can contribute to the expanded regime analysis.
