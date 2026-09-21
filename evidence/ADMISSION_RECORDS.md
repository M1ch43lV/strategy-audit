# Admission records - what the eligibility expansion waves and the smoke funnel review found

Result records of finished work, **not rules**. The protocol they were run under is `PIPELINE_EXTENSIONS.md`, Part 1;
the current state of every strategy is `STRATEGY_STATUS.csv`. All expansion waves are terminal, and nothing here is a
queue. Six evidence files were merged into this one on 2026-09-20 without changes to the text; each part names its
former file.

| Part | Subject |
|---|---|
| 1 | Wave A: seven pending diagnostics |
| 2 | Wave B: static proofs |
| 3 | Wave C: pre-measurement resolution |
| 4 | Wave C: canonical measurement results |
| 5 | Wave C: both bias gates over the 53 rows that produced trades |
| 6 | Smoke-funnel review 2026-09-10 (read before reclassifying or rerunning any of its rows) |
| 7 | 5m recovery of the 1m out-of-memory strategies: check of the records and what it brought (2026-09-21) |

A file name inside the text of a merged part (for example `ELIGIBILITY_EXPANSION_PLAN.md`) names the file as it was then; the table "Where a former document went" in `README.md` resolves it.

## 1. Wave A results

*Formerly `evidence/EXPANSION_WAVE_A_RESULTS.md`, merged here on 2026-09-20 without changes to the text below.*

All seven rows were already measured, had coverage `PASS`, zero traps and no
hard exclusion reason. Each was pending only because a bias diagnostic had not
completed. Repairs stayed at the resource and harness layer; no entry or exit
rule was touched.

### Terminal states

| Strategy | Outcome | Basis |
|---|---|---|
| `Fakebuy` | **passes both gates** | needed time only; see below |
| `HyperStra_GSN_SMAOnly` | lookahead `FOUND` | bias in 10 of 13 signals |
| `kalthetank` | lookahead `FOUND` | bias in 13 of 20 signals |
| `haGradient` | terminal pending | incompatible with the analyzer by construction |
| `InverseVolatilityPortfolio` | terminal pending | analyzer catches 0 of 10 required trades |
| `RiskParityPortfolio` | terminal pending | analyzer catches 0 of 10 required trades |
| `TGMA` | terminal pending | contradictory trailing stop; repair changes exits |

Net effect: one row becomes admissible, two are excluded on evidence rather
than left undecided, and four remain pending for reasons that cannot be removed
without changing what is being tested.

### What the resource layer actually fixed

`Fakebuy` spent 635 s on the first window and then hit the 300 s fallback limit
that the cascade gives its later, larger windows. With a matching timeout it
completes in the intermediate window and reports no bias.
`HyperStra_GSN_SMAOnly` was killed by the old 5.8 GiB memory ceiling; under the
raised limit it completes and reports bias. Neither outcome was available
before, and one of them is negative - the resource fix bought verdicts, not
admissions.

### Why three rows cannot be repaired here

- **`haGradient`** raises `ValueError` when `len(dataframe)` is below its FFT
  window. Freqtrade's lookahead analysis works by replaying the strategy on
  deliberately truncated slices, so the analyzer must hand it short frames. The
  cascade was extended and ran all three windows; the failure still reports 101
  rows, because the limit is the analyzer's truncation, not the window. Making
  this pass means editing the strategy to tolerate short frames, which changes
  behaviour and belongs to E3.
- **`InverseVolatilityPortfolio` / `RiskParityPortfolio`** are daily-timeframe
  portfolio strategies that enter only on rebalance dates, so they never reach
  the analyzer's minimum of 10 caught trades. Note that bias diagnostics run at
  `max_open_trades = 3` while canonical measurement uses `8`; aligning them
  would invalidate every bias result already recorded, so it was not done.
- **`TGMA`** sets `trailing_stop = True` (overriding an earlier `False`) with
  activation at 1.3 % profit and a 3.5 % trail, so the stop activates below
  entry. Freqtrade rejects the pair as incoherent. `use_custom_stoploss = True`
  is set but no `custom_stoploss` method exists; in `IStrategy` the custom and
  trailing branches are independent, so the trailing logic is live rather than
  vestigial. Any repair alters exits.

### Historical E0 handling, superseded 2026-09-03

At the time, regenerating `REGIME_ELIGIBILITY.csv` from the new bias results
would have moved
`Fakebuy` to `eligible` and the two `FOUND` rows to `ineligible`, taking the
table from 67 to 68. That file is the frozen E0 baseline and was deliberately
not rewritten. The later uniform-chain audit invalidated E0 as a cohort.
`Fakebuy` and every former E0 member are usable only through independent active
E1 adjudications; E0 remains provenance only.

## 2. Wave B static proofs

*Formerly `evidence/EXPANSION_STATIC_PROOF_FINDINGS.md`, merged here on 2026-09-20 without changes to the text below.*

Plan 5.1 condition 6 requires a file-specific proof that decisions do not
depend on history *below* the adapter boundary. Reviewing the 13 exactly
equivalent rows split them cleanly in two.

### Admitted (6 new, plus the 2 already held)

Every lookback is a finite window that fits inside the frozen warm-up.

| Strategy | Warm-up | Longest lookback | Basis |
|---|---|---|---|
| `BinHV45` | 40 | 40 | 40-candle rolling band + one-row shift |
| `BinHV45_kanaxe` | 40 | 40 | same family, no other indicator |
| `BinHV45_stash` | 40 | 40 | same family, no other indicator |
| `BinHV45_werkkrew` | 40 | 40 | same family; `nan_to_num` + `.gt(0)` also blocks warm-up entries |
| `BollingerBandStrategy` | 21 | 21 | `BBANDS(20)` and 21-candle rolling sums, no shift |
| `CCI_BB` | 20 | 20 | `CCI(14)` and a 20-candle band, no shift |

### Not admitted (5)

No proof was written for these. The frozen warm-up does not cover the
dependency, so writing one would assert something untrue.

- **`Strategy004`** (warm-up 5, timeframe 5m). Contains `STOCHF(dataframe, 50)`,
  `ADX(dataframe, 35)`, `CCI` (14) and `rolling(12)`. The longest literal period
  is 50, ten times the frozen warm-up. The recorded derivation basis, "longest
  literal indicator period 5", took a minimum rather than a maximum.
- **`Cluc4`** (warm-up 168, timeframe 1m). Its informative frame is hourly and
  carries `ROCR(timeperiod=168)`. 168 hourly candles are 10,080 one-minute
  candles, so the value was carried across timeframes without conversion.
- **`TouchEmaStrategy`** (warm-up 60, timeframe 5m). `populate_indicators`
  iterates the whole `IntParameter(40, 100)` range, so EMAs up to period 100 are
  computed. Worse, `bars_delay_*` is a counter mutated through `self` inside a
  row-wise `apply`, which accumulates from the first row of the frame. That
  dependency is stateful and unbounded, not merely long.
- **`Combined_Indicators`** (warm-up 50) and **`CombinedBinHAndClucHyperV0`**
  (warm-up 91). Their finite windows fit, but both decide on `ta.EMA`, which is
  recursively smoothed and never fully forgets its seed. No finite warm-up makes
  such a series exact, so the condition cannot be proved, only approximated.

### Why the exact trade match was not sufficient on its own

All 13 rows matched the original pooled trade list exactly. That match shows the
warm-up metadata does not change behaviour, which is the right question for
admission. It does not show the warm-up is long enough: with the authored
`startup_candle_count=0` the early rows carry NaN indicators and simply produce
no entries, so both configurations agree about a region in which neither trades.
Condition 6 exists precisely to catch that, and here it caught five rows.

### Adjudicator change

The checker previously accepted a proof only when all three dependency fields
began with the literal `none;`, which admits only strategies with no history at
all. That is narrower than the written condition. It now also accepts a bounded
dependency that states `max_history_lookback_candles` and fits inside the
warm-up, and still rejects anything unbounded, stateful or recursive.

## 3. Wave C pre-measurement resolution

*Formerly `evidence/EXPANSION_WAVE_C_PREFLIGHT.md`, merged here on 2026-09-20 without changes to the text below.*

The plan requires artifact-role review and resolution of any unknown execution
profile before Wave C measurement starts. Both are now done. The missingness
inventory in `ELIGIBILITY_EXPANSION_MISSINGNESS.csv` covers all 230 rows.

### The headline number

`runtime_smoke_status` is `not_run` for **213 of 230** rows and `failed` for
only 17. Wave C is overwhelmingly a queue of strategies nobody ever attempted,
not a pile of broken ones. That is the reason to expect a materially better
yield here than Wave B's 13 of 82.

### Twelve rows are not trading strategies

Each was checked against its file, not just its recorded label.

**Nine test fixtures** belonging to freqtrade's own test suite:

| Strategy | File |
|---|---|
| `TestStrategyNoImplements` | `tests/strategy/strats/broken_strats/broken_futures_strategies.py` |
| `TestStrategyLegacyV1` | `tests/strategy/strats/` |
| `InformativeDecoratorTest` | `tests/strategy/strats/informative_decorator_strategy.py` |
| `freqai_test_strat` | `tests/strategy/strats/` |
| `freqai_test_classifier` | `tests/strategy/strats/` |
| `freqai_test_multimodel_strat` | `tests/strategy/strats/` |
| `freqai_test_multimodel_classifier_strategy` | `tests/strategy/strats/` |
| `freqai_rl_test_strat` | `tests/strategy/strats/` |
| `Strategy` | `NostalgiaForInfinity/tests/unit/test_data/` |

`TestStrategyNoImplements` sits under `broken_strats/` and is deliberately
incomplete: it exists so freqtrade can assert that loading it fails. Measuring
it would produce a number about a test fixture, not about a trading method.

**Three templates** with no signal logic of their own:

- `ThreeCommasStrategy` defines only `confirm_trade_entry`, a callback hook. It
  has no `populate_entry_trend` or `populate_buy_trend` at all.
- `YourStrat` (in `TrailingBuyStrat.py`) is the placeholder a user is meant to
  replace: the file states the companion class "is designed to heritate from
  yours". The entry logic lives in the subclass, not here.
- `StrategyAnalysis` is an analysis scaffold, not a traded method.

These twelve receive a terminal state of *not a trading strategy*. They are not
measured, and they are not counted as failures.

### The unknown execution profile

Exactly one row carried `run_profile = unknown`: `TestStrategyNoImplements`.
It has no profile because it implements no interface. Resolved by the same
finding; no separate decision is needed.

### Resulting scope

Wave C's measurable pool is **218** rows, not 230. Of those, 30 are FreqAI
machine-learning strategies whose dependency and runtime class will need
attention before they can be measured, and 33 have no recorded execution
timeframe.

Successful loading or a passing smoke run is not eligibility. Every measured
row still has to clear both bias gates afterwards, exactly as Wave A showed:
there, completing the diagnostics excluded two strategies on evidence and
admitted one.

## 4. Wave C measurement results

*Formerly `evidence/EXPANSION_WAVE_C_RESULTS.md`, merged here on 2026-09-20 without changes to the text below.*

**Historical context:** references below to comparability with the frozen 67
describe the rule at the time. E0 was invalidated as a cohort on 2026-09-03;
those 67 labels now provide provenance only and no admission authority.

All 218 measurable Wave C rows were run through the frozen smoke window
`20200301-20200401`. The queue was exhaustive: every row has a result.

### Outcome

| | rows |
|---|---|
| measured, produced trades | 53 |
| measured, zero trades in the smoke window | 13 |
| failed | 152 |
| **total** | **218** |

66 of 218 rows ran at all - a 30 % start rate. Measurement is not eligibility:
both bias gates still follow, and Wave A showed those gates excluding two of the
three rows they decided.

### Why 152 rows failed

| cause | rows | can it be repaired here? |
|---|---|---|
| class not loadable | 51 | no - genuine defects |
| no `timeframe` declared | 48 | **decision required** |
| numpy / pandas dtype conflict | 12 | no - would need an older stack |
| outdated freqtrade interface | 10 | no - would need source edits |
| freqAI not enabled in config | 5 | possibly, at the config layer |
| required field missing (`stoploss`) | 3 | no |
| required method missing | 2 | no |
| assorted single defects | 21 | no |

#### The 48 rows without a declared timeframe

These strategies never state which candle size they trade. Their authors must
have supplied it from a config we do not have. Setting one would not be a
neutral repair: the timeframe decides the entire behaviour of a strategy, so
picking a value invents a parameter the author never chose and classifies a
strategy that never existed. This is the same class of problem as the trailing
stop, but sharper, and it is left open pending an explicit decision.

#### The 12 dtype and 10 interface failures

These are old strategies meeting freqtrade 2026.7. Repairing them means either
editing the sources, which changes behaviour, or pinning an older runtime. At
the time, the latter was rejected as breaking comparability with the frozen 67;
that cohort was later invalidated, but the common-runtime requirement remains.
Neither option was available at the harness layer, so both remained terminal
in this wave.

### The 13 zero-trade rows, settled

All 13 have their pooled full-window run. None adds a usable strategy, and the
run was still worth doing: it separated three different things a zero had been
hiding.

| Outcome | Rows |
|---|---:|
| genuinely never trades over the full window | 6 |
| defective in a way the one-month window concealed | 2 |
| already measured before this pass | 4 |
| resource-terminal | 1 |

The two defects are the reason a zero cannot be taken at face value.
`Matrix` reads a `coef` column its own indicator step never creates, and
`zorkv7_0_0` asks a quantile transform for 100,000 quantiles from 10,000
samples. Both ran clean in the smoke window because neither reached the failing
code there. A passed short test is not evidence that a strategy works.

`HarmonicDivergence` spent 1800 seconds on one of eight pairs without
finishing, after reaching 18.5 GiB under the old memory ceiling. Its single
recovery attempt is deliberately unused.

### Both bias gates

See `EXPANSION_WAVE_C_BIAS_RESULTS.md`. Of the 53 rows that produced trades,
three passed both gates and are admitted to E1; 37 are excluded on demonstrated
bias; seven were refused rather than judged by the recursive analyzer and were
routed to the warm-up procedure; six still hold an `NA`.

## 5. Wave C bias results

*Formerly `evidence/EXPANSION_WAVE_C_BIAS_RESULTS.md`, merged here on 2026-09-20 without changes to the text below.*

Measurement was never eligibility. `ELIGIBILITY_EXPANSION_PLAN.md` requires
that "full measurement and both bias gates still follow", and none of the 53
Wave C rows that produced trades had a bias verdict. All 53 now do.

### Outcome

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

### The three that passed

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

### Seven rows the analyzer refused, and why they are not exclusions

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

### Open work

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

## 6. Smoke-funnel review 2026-09-10

*Formerly `evidence/SMOKE_FUNNEL_REVIEW_2026-09-10.md`, merged here on 2026-09-20 without changes to the text below.*

This review explains the first funnel column in `strategy_status.html`. Counts
are reconstructed from `STRATEGY_STATUS.csv`, `evidence/PROFILE_SMOKE.json`,
and the measured entries of `results/regime/full_backtest_manifest.json` using
the same predicates as `tools/STRATEGY_STATUS.template.html`.

### Reconciliation

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

### The 74 smoke-stage exclusions

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

### The 32 open smoke-stage rows

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

### Decision

Do not collapse all 32 open rows into exclusions. The correct next bounded
queue is 4 known repairs + 6 resource adjudications + 8 data/harness checks +
14 exact-provenance checks. Stop each row as soon as it requires invented
strategy behavior. Separately reopen the 9 narrowly patchable C8 rows. This
preserves the owner's objective of maximizing usable strategies without
weakening the causal or equivalence gates.

### Follow-up execution on 2026-09-10

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

## 7. 5m recovery of the 1m out-of-memory strategies: check and yield (2026-09-21)

Rule and route: `PIPELINE.md`, Decision record, Amendments of 2026-09-20 and 2026-09-21 (owner). Of 60 strategies whose
canonical 1m pooled Full-Backtest was `oom_confirmed` or `resource_inconclusive`, 47 passed smoke, look-ahead, warm-up,
recursion and a measured eight-pair 5m Full-Backtest and were promoted into E1; 13 stopped earlier (5 at warm-up, 3 at
smoke, 2 at look-ahead, 1 at recursion, 2 without a measured 5m Full-Backtest). The numbers below come from
`python -m tools.recovery_5m_review` (`results/regime/recovery_5m_review.json`) and are those of the published
*Regime-Spezialisten* page.

**Check of the records.** For all 47: cohort `E1_expanded`, `technical_chain_complete`, full-backtest status `measured`
with scope `owner_approved_timeframe_5m_recovery_pooled_pair_universe`, archive present and its digest and trade count equal
to the manifest, archive timeframe 5m, look-ahead and recursion `PASS`, Stage 8b `PASS` by the at-or-below-5m rule, the
canonical 1m result kept under `original_full_backtest`. Two defects were found and fixed:

- `regime.attribution` rejected all 47 (scope not canonical, archive timeframe 5m against the profile's 1m), so no ranking
  contained them. It accepts the owner-approved scopes now.
- 41 spot recoveries ran over `20200301-20260821` instead of the frozen spot window from 2020-04-01 (24,878 trades opened
  in March 2020). The diagnostic runner now takes the window per mode; the attribution drops those trades.

Not changed, but visible: the status table and the Test Bench show the look-ahead and warm-up evidence of the original 1m
identity (start-up of 1440 candles at 1m); the gates at 5m (288 candles) are in `evidence/TIMEFRAME_5M_RECOVERY.json`.

**Where they stand** (567 strategies with a whole-window row, 675 evaluated). 35 of the 47 have a whole-window row.

| | 47 recovered | others |
|---|---|---|
| Median rank by validation dollar gain | 295 | 284 (population median) |
| In the top 10 / 25 / 50 / 100 | 2 / 4 / 7 / 9 | |
| Whole-window gain above 0 | 46 % | 47 % |
| Above Buy-and-Hold | 40 % | 37 % |
| Stage 8b `PASS` | 100 % | 92 % |
| At least one verified specialist row | 21 of 35 | 298 of 515 |
| At least one confirmed row | 23 of 35 | 168 of 515 |

In the phase tables they hold 15 of the 80 places of the eight Top-10 lists: BTC sideways 4, BTC transition 3, coin
sideways 2, coin transition 4, coin bear 2, none in the BTC and coin uptrend. `FisherHull` is first in three of the phase
lists. Of the 9 verified universal specialists, 3 are recoveries (`DMIPRICEDCAStrategyFuture`, `WTDMIPRICESDCAtrategy`,
`Trump_LIM`).

**Reading.**

- The whole-window ranking is unremarkable: the median rank is that of the population. Two of the top ten (`DMIPRICEDCAStrategyFuture`,
  `GRIDDMIPRICEStrategySpot`) are DCA strategies whose own account did not earn what the fixed-stake dollar figure shows: the
  first ends at 96 % of its start capital with 5x leverage and a 55 % drawdown, the second at 2 % (its account collapsed).
  The same convention effect as for `ZaratustraDCA5`.
- The yield is in the phases. Mean-reversion scalpers (BinHV45, Cluc, Low_BB, FisherHull, Trump_LIM) are over-represented in
  the sideways, transition and bear lists, and confirmed rows are twice as frequent as elsewhere. Solid own accounts:
  `Trump_LIM` (+129 %, drawdown 14 %), `BinHV45_werkkrew` (+132 %, 16 %), `Low_BB` (+55 %, 22 %), `ClucHAnix` (+163 %, 45 %).
  `FisherHull` is first in three phases and below Buy-and-Hold over the whole window (excess -$3,199).
- Independent evidence is smaller than 47: 44 distinct trade sets, in a handful of families (BinHV45, Cluc, DMIPRICE, MiniLambo);
  none equals the trade set of a strategy outside the group.
- Cost: 5.1 hours of full-backtest compute, peak memory 6.1 GB, 47 of 60 successes. What is measured is a 5m rerun of
  1m strategies, that is the same rules at a coarser resolution and not the behaviour the author had; that is why the pages
  mark them with a dagger.
