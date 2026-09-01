# Wave C - both bias gates over the 53 rows that produced trades

Measurement was never eligibility. `ELIGIBILITY_EXPANSION_PLAN.md` requires
that "full measurement and both bias gates still follow", and none of the 53
Wave C rows that produced trades had a bias verdict. All 53 now do.

## Outcome

| | rows |
|---|---:|
| passed both gates | **3** |
| bias demonstrated on at least one gate | 37 |
| recursive analyzer refused the row | 7 |
| no verdict on at least one gate | 6 |
| **total** | **53** |

Cross-tabulated, because a single count hides which gate decided:

| look-ahead | recursive | rows | reading |
|---|---|---:|---|
| `PASS` | `PASS` | 3 | candidate |
| `FOUND` | `FOUND` | 12 | excluded twice over |
| `PASS` | `FOUND` | 12 | excluded on recursion |
| `NA` | `FOUND` | 10 | excluded on recursion |
| `FOUND` | `PASS` | 3 | excluded on look-ahead |
| `PASS` | refused | 6 | **undecided, not excluded** |
| `NA` | refused | 1 | undecided |
| `NA` | `PASS` | 3 | undecided |
| `NA` | `NA` | 3 | undecided |

## The three that passed

`NowoIchimoku5mV2`, `ObeliskIM_v1_1`, `simple_patterns`. All three are
`spot_long`, all three carry `coverage_status=PASS`, `traps_n=0`, and
`artifact_role=strategy`. Their only baseline exclusion reason was
`canonical_implementation_not_measured`, which Wave C resolved.

They are **not yet admitted to E1**. See the open work below.

Two of the three are Ichimoku implementations, and that is worth stating
because two other Ichimoku rows in the same run were excluded:
`NostalgiaForInfinityNext` and `Obelisk_Ichimoku_ZEMA_v1` both fail on
`chikou_span`, the close shifted forward for display. The indicator family
does not decide the verdict; the individual implementation does. A screen by
indicator name would have been wrong in both directions.

## Seven rows the analyzer refused, and why they are not exclusions

Seven rows record `recursive = FOUND` with the reason
`startup_candle_count=0 refused by recursive-analysis`. That is not a bias
finding. The strategy declares no warm-up, the analyzer declines to run, and
no statement about the strategy is produced. `profile_bias._recursive` maps
this refusal onto the same status as a demonstrated drift, which is a
reporting defect, not a measurement one: the `why` string is accurate and the
underlying evidence is intact.

Six of the seven have a clean look-ahead `PASS`:
`BB_RPB_TSL`, `BB_RPB_TSL_2`, `BB_RPB_TSL_BI`, `BB_RPB_TSL_BIV1`, `MultiRSI`,
`pmaxTest`. The seventh, `epretrace`, has `lookahead = NA`.

This is exactly the condition that defines Wave B, whose 82 rows share the
same refusal. The frozen zero-warm-up adapter of plan section 5.1 already
exists for it, and it is not lenient: of 13 rows whose trade lists matched
exactly, five were still refused admission on file-specific static grounds.
These seven landed in Wave C only because at freeze time their sole known
defect was that nobody had measured them.

Four of the six are variants of one strategy and must not be counted as four
independent observations.

## Open work

1. **Done: the three are admitted.** E1 stands at 78.

   The adjudicator could not express their case as it stood. It is driven by
   `ELIGIBILITY_EXPANSION_PROOFS.json` and checks `trade_equivalence` and
   `static_proof`, and both exist only because a Wave B row declares no warm-up,
   the analyzer refuses it, and a verdict is obtainable solely by supplying a
   value the author never wrote. A Wave C row was supplied nothing: it was
   never measured, and once measured it passed the original gates unaided.
   Demanding an equivalence proof for an override that was never applied would
   not have been strict but incoherent. It therefore gained a second ruleset,
   `native_gate_pass_v1`, asserting the original Stage 6 rule and nothing
   weaker: identity, native measurement with trades, both gates `PASS`,
   coverage `PASS`, trap-free, artifact role strategy, not `behavior_changed`.
   Rewriting the frozen `REGIME_ELIGIBILITY.csv` was never an alternative.

2. **Done: the seven refusals were routed to the warm-up procedure.** Five
   showed real drift at a one-candle warm-up and two passed outright. All seven
   then joined the warm-up convergence cohort, where the drift is measured
   across a fixed ladder rather than at a single value. `epretrace` is terminal
   pending: its look-ahead run exceeded an hour twice, which exhausts the two
   attempts the resource protocol allows.
3. **Six rows still hold an `NA`.** Three are `NA/PASS` and could still become
   candidates if a look-ahead verdict can be obtained. `ARIMASTR` and
   `beta_factors_model` fail inside their own code; `HarmonicDivergence_fix`
   raises `list index out of range` on both gates.
