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
