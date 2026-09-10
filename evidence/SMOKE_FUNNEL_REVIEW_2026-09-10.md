# Smoke-funnel review — 2026-09-10

This review explains the first funnel column in `strategy_status.html`. Counts
are reconstructed from `STRATEGY_STATUS.csv`, `evidence/PROFILE_SMOKE.json`,
and the measured entries of `results/regime/full_backtest_manifest.json` using
the same predicates as `tools/STRATEGY_STATUS.template.html`.

## Reconciliation

The 1,031 rows whose artifact role is suitable for a smoke run split into 905
passed, 74 terminal smoke-stage exclusions, and 52 other states. The 52 were 32
open, 19 excluded for a later/different reason, and one admitted row.

The admitted exception was `Hacklemore3`. Its stored smoke attempt had timed
out after 300 seconds, while a separate identity-bound Class-1 result card
recorded 34 trades and the strategy had passed look-ahead, recursive and
coverage gates. A targeted Docker rerun on 2026-09-10 completed after 857.1
seconds with 11 long trades in `20200301-20200401`. The fixed cascade therefore
stopped at its first rung. After regenerating status, `Hacklemore3` has
`trade_evidence=smoke`; the admitted exception is now zero.

## The 74 smoke-stage exclusions

- 35 `repair_refused_would_invent_strategy`: missing timeframe, stoploss,
  exit/indicator implementation, author data/model/config, or an invalid
  authored configuration. These are terminal under the frozen E1 repair
  boundary; filling them would choose strategy behavior.
- 18 `third_party_package_declined`: every missing dependency was identified.
  The existing review found no safe deterministic installation in the shared
  audit runtime. They stay excluded unless a strategy-specific isolated image
  is specified and validated prospectively.
- 6 `local_module_repair_exhausted`: the corpus-wide module search or applied
  candidate was exhausted/withdrawn, or exposed a second failure. They are
  terminal without obtaining the author's missing implementation.
- 15 `shared_runtime_change_declined`: pandas/NumPy compatibility failures.
  Six still require individual or runtime-wide behavior. Nine, however, match
  the existing file-local `patch_string_nan` transformation exactly:
  `Danke`, `FSupertrendStrategyBTC`, `FSupertrendStrategyETH`, `FastSupertrend`,
  `FastSupertrendOpt`, `MultiMA_TSL3b`, `MultiMA_TSL5`, `SuperTrendPure`, and
  `Supertrend`.

The nine exact matches should be reopened as bounded repair candidates, not
declared repaired or admitted. The old C8 rationale rejected a global
NumPy-promotion shim affecting every strategy; the current Class-2 machinery
can instead alter only the copied legacy expression, retain the original, and
bind the overlay by hash. Each still needs overlay generation, a smoke rerun,
equivalence proof, and both bias gates. The other 65 exclusions remain
terminal on current evidence.

## The 32 open smoke-stage rows

Four have an already-defined, narrow repair route and should remain open:

- `BaseStrategy`: repository-local module path is already registered.
- `NNPredict`: fetched sibling dependency and isolated TensorFlow runtime are
  registered; the next compatibility failure must be tested, not guessed.
- `SMAOPv1_TTF`: the existing neutral parameter-space overlay matches three
  declarations.
- `WTHO`: the same overlay matches seven declarations.

Six are resource cases requiring one final attempt under the frozen resource
protocol before closure: `GRIDDMIPRICEStrategyFutureV4`, `Guacamole`,
`Kamaflage`, `ONS_Portfolio`, `RebalanceStrategySpot`, and `Schism5`. A timeout
is not a strategy defect. If the permitted recovery attempt is already
exhausted and identity unchanged, they should move to a terminal resource
classification, not remain generically open.

Eight need one bounded data/dependency/harness investigation:
`AutoArimaTripleV1`, `BestSingleAssetPortfolio`, `DELTA_NEUTRAL`,
`MasterMoniGoManiHyperStrategy`, `RLAgentStrategy`, `Solipsis_v4`,
`TuplaBollinger`, and `multi_tf`. Their messages point respectively to history,
portfolio input, missing dataframe, missing archive, isolated dependency,
pandas compatibility, absent data, or an informative pair. None justifies a
strategy-code edit before that check.

The remaining fourteen expose absent author parameters or failures inside the
strategy's calculations: `Astro`, `BlueEyes_MPP_v1`, `CryptoFrogNFI2`,
`GodStra`, `HLHB`, `MultiMa`, `MyStrategyNew10`, `NowoIchimoku1hV1`, `Proton`,
`QuickBuyStrategy`, `RenkoYolo`, `Schism6`, `UpSliceStrategy`, and `tacos1`.
They should receive only a static provenance check for an exact author-supplied
value or implementation elsewhere in the same repository. If none exists,
they become terminal `repair_refused_would_invent_strategy`; guessing a key,
parameter, callable, dataframe shape, or trading calculation is outside E1.

## Decision

Do not collapse all 32 open rows into exclusions. The correct next bounded
queue is 4 known repairs + 6 resource adjudications + 8 data/harness checks +
14 exact-provenance checks. Stop each row as soon as it requires invented
strategy behavior. Separately reopen the 9 narrowly patchable C8 rows. This
preserves the owner's objective of maximizing usable strategies without
weakening the causal or equivalence gates.

## Follow-up execution on 2026-09-10

The five bounded work packages above were executed without inspecting profit
or regime rankings.  Generated CSV files were never edited by hand.

The nine C8 candidates received the existing file-local NumPy string/NaN
overlay. `FastSupertrend`, `FastSupertrendOpt`, and `MultiMA_TSL3b` exceeded
the ten-trade floor in the first month; `MultiMA_TSL5` reached 15 trades only
at the one-year rung. `FSupertrendStrategyBTC`,
`FSupertrendStrategyETH`, `SuperTrendPure`, and `Supertrend` remained at zero
through one year. `Danke` timed out on the one-year rung after two completed
sub-floor rungs. A successful compatibility load therefore did not get
confused with admission or sufficient trade evidence.

Of the four pre-existing repair routes, the neutral parameter-space overlay
made `SMAOPv1_TTF` measurable with 87 trades at the one-year rung and `WTHO`
with 141 trades in the first month. `BaseStrategy` and `NNPredict` still fail
before measurement; their registered first repair exposed no result that can
be promoted.

The resource recovery used the same hard 1,800-second budget. `Schism5`
completed with 1,644 trades. `GRIDDMIPRICEStrategyFutureV4` measured eight
trades in one month, then timed out over three months. `ONS_Portfolio` measured
eight trades in both one and three months, then timed out over one year.
Neither reaches the frozen floor, and both remain terminal resource-
inconclusive rows rather than strategy failures. `RebalanceStrategySpot`,
`Guacamole`, and `Kamaflage` exhausted the same final budget. No additional
resource run is owed.

The data/harness review recovered the exact informative series requested by
`multi_tf`: `ETH/BTC` 1h, 74,203 candles from 2018-03-01 through 2026-08-20.
No synthetic 5h candles were created for `TuplaBollinger`, because Binance
does not publish its authored interval and resampling would define new candle
boundaries. `BestSingleAssetPortfolio` and `Solipsis_v4` received narrow
pandas-compatibility overlays which preserve valid-row calculations and
explicitly initialize an authored empty exit signal. Their execution results
are recorded in the final generated artifacts below.

The exact-provenance review permitted only two additional mechanical repairs:
`QuickBuyStrategy`'s unambiguous one-hour literal `1hr` became current `1h`, and
`BlueEyes_MPP_v1` received the standard `DataFrame` import already referenced
by its annotations. The exact `pivots_points` helper was then found in the
same repository and restored through a path-bound import, but this exposed a
third absent symbol, `merge_informative_pair`. The bounded repair was therefore
stopped and `BlueEyes_MPP_v1` classified as exhausted. Missing strategy
thresholds, parameter dictionaries, configuration blocks, signal calculations,
or backtest behavior in the other cases were not borrowed from sibling
versions and were not guessed. Their row-level terminal families and
explanations are generated by
`tools/blocked_triage.py` into `evidence/BLOCKED_TRIAGE.json` and
`REPAIR_LIST.md`.

After the last retest and regeneration, the authoritative 1,050-row status is:
675 `E1_expanded`, 263 `excluded`, 53 `exclusion_unconfirmed`, 30
`too_few_trades`, 10 terminal-resource or still-actionable `pending`, and 19
`not_a_strategy`. Seventeen previously open rows are now confirmed exclusions
because their only repair would invent strategy behavior. Successful smoke
recovery does not itself admit a strategy: the 53 unconfirmed rows still owe
the applicable look-ahead, recursive, equivalence, and admission gates.

The successful at-least-ten-trade recoveries in these five packages are
`FastSupertrend`, `FastSupertrendOpt`, `MultiMA_TSL3b`, `MultiMA_TSL5`,
`SMAOPv1_TTF`, `WTHO`, `Schism5`, `QuickBuyStrategy`, `multi_tf`, and
`Solipsis_v4`. `BestSingleAssetPortfolio` is executable after compatibility
repair but remains below the floor with eight trades through one year.

The ten remaining pending rows are not an undifferentiated repair queue. Six
have exhausted resource attempts (`Danke`, `GRIDDMIPRICEStrategyFutureV4`,
`Guacamole`, `Kamaflage`, `ONS_Portfolio`, `RebalanceStrategySpot`); the
protocol deliberately retains such inconclusive resource outcomes as pending,
not as strategy defects. `BaseStrategy` and `NNPredict` still have unresolved
local-module/load paths, `Proton` remains in its separate FreqAI repair arm,
and `haGradient` owes its already-recorded look-ahead remeasurement and
recursive ladder. None of these ten should be retried by another generic smoke
run.
