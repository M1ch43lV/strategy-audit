# Repair register

What was changed, in which class, and how to undo it. **Class 1** touches no
strategy file. **Class 2** uses an overlay copy of a strategy file; the original
under `strategy-audit/repos/` remains untouched.

Class 1 and Class 2 describe **repair provenance, not separate study
populations**. The regime study uses one deduplicated canonical corpus with two
provenance values:

- `original`: the strategy as published, under the original audit setup;
- `repaired`: the strategy under the documented repair stack, including both
  Class 1 environment repairs and any Class 2 overlay.

Every repaired result must additionally record `repair_class`, `repair_rules`,
and `equivalence_status`. Allowed equivalence values are:

- `strict_equivalent`: documented API/alias replacement with the same value;
- `output_equivalent`: intermediate values may differ, but a file-specific
  proof establishes identical reachable trading decisions;
- `behavior_changed`: the repair restores intended functionality but changes
  executable behavior; no equivalence is claimed.

Primary corpus and regime tables pool canonical implementations while retaining
`population=repaired` as row metadata. Sensitivity analysis must exclude `behavior_changed`;
those cases are reported descriptively. FreqAI remains a separate `run_class`
because its training setup is investigator-defined, but it is not a third
population.

**Phases 0–1 below are Class 1. No original strategy file is modified.**

## Phase 0 — isolated environment

| | |
|---|---|
| What | Created `strategy-audit/ftenv`, installed freqtrade 2026.7 |
| Class | 1 |
| Why isolated | `pmdarima` and `scikit-optimize` can pull numpy backwards. The user's working `.venv` stays untouched. `harness.py` already expects `ftenv/Scripts/freqtrade.exe` at exactly this path and was not finding it. |
| Stack | freqtrade 2026.7 · pandas 3.0.5 · numpy 2.5.2 · TA-Lib 0.7.1 — identical to the audit's, so results stay comparable |
| Undo | `rm -rf strategy-audit/ftenv` |

## Phase 1a — missing dependencies installed

| | |
|---|---|
| What | `finta arrow ta ephem pywavelets py3cw scikit-optimize feature_engine statsmodels optuna tensorflow lightgbm pmdarima talipp` |
| Class | 1 |
| Rationale | The strategy authors assumed these packages without declaring them. Their absence is a property of the packaging, not of the trading logic. |
| Verification | numpy 2.5.2 and pandas 3.0.5 unchanged after every install step, TA-Lib still loads |
| Not installed | `zigzag` — pins `Cython<0.30`, and that Cython's DLL is blocked by a Windows application control policy on this machine. Working around it would mean changing the machine's security policy. 5 strategies stay unmeasurable. Its `pyproject.toml` is also malformed (`Cython>=^0.29`, a mix of PEP 508 and Poetry caret syntax). |
| Additional profile attempt | `pyrenko==0.1` imports when installed without its obsolete numpy 1.18.5 dependency pin. `AdaptiveRenkoStrategy` remains partial because the author supplied no required stoploss configuration. |
| Not attempted | `remora`, `hyperliquid`, `stable_baselines3`, `openai`, `tslearn`, `pykalman` — outside the effort budget or blocked by security/configuration evidence |
| Undo | with `ftenv` |

## Phase 1b — module search path instead of code changes

| | |
|---|---|
| What | `repair/modpath.py` locates helper modules that ARE in the corpus but that the harness cannot see |
| Class | 1 |
| Rationale | `harness.py` passes `--strategy-path <dirname(file)>` so repositories do not bleed into each other. Helper modules live in a sibling or parent directory and become invisible. A path problem, not a defect. |
| Boundary | The original sweep restricted lookup to the strategy's own repository. The later profile audit separately records copied strategies whose missing helper is restored from another corpus repository only when the dependency relationship is explicit; those exceptions appear in `evidence/PROFILE_CLASS1.json`. |
| Effect | 8 strategies fully resolved. The 22 estimated beforehand were too optimistic. |

### A finding from 1b that argues against our own thesis

38 strategies import a local helper module that **does not exist in their own
repository**. `CryptoFrog` sits in `PeetCrypto_freqtrade-stuff` while its
`custom_indicators.py` exists only in `froggleston_cryptofrog-strategies`;
`DWT` sits in `TheoBrigitte_freqtrade` while the module is only in `nateemma`.
These strategies were **copied between repositories without their helper
module** — they were never runnable where they are published. The profile audit
can test a documented dependency-restoration environment, but the publication
defect remains visible rather than being rewritten as an original success. That is a real
defect in the publication and supports the audit author's copy thesis rather
than undermining it.

## Phase 1c — compatibility shim for API drift

| | |
|---|---|
| What | `repair/compat_shim.py`, activated through `ftenv/Lib/site-packages/sitecustomize.py` |
| Class | 1 |
| Scope | `np.NAN/NaN/INF/float_/int_` → their numpy 2 equivalents · `numpy.lib.math` → the standard library `math` module it always was · `CategoricalParameter`, `IntParameter`, `DecimalParameter` and friends re-exported from `freqtrade.strategy.hyper`, which they left for `freqtrade.strategy.parameters` |
| Rationale | These are **aliases to identical objects**, not reimplementations. `np.NAN` *is* `np.nan`. |
| Boundary | `technical.indicators.accumulation_distribution` was removed with no replacement. Writing our own A/D indicator under the original name would be an invention wearing the original's label. The 2 affected strategies stay failing. |
| Undo | delete `sitecustomize.py` |

## Phase 1d — eight corpus files recovered

| | |
|---|---|
| What | 8 strategy files listed in `LEDGER.csv` were absent from the local corpus |
| Class | 1 (restores the corpus; nothing is edited) |

Both causes are Windows filename problems, not missing code.

**5 from `ShahAnuj2610/my-freqtrade`.** The directory holds only `.git/` — 28
files, all in the object store, **no working tree**. The clone succeeded and the
checkout did not. This is the repository `CORPUS.md` already flags: *"could not
be cloned at all — it contains filenames with colons, which Windows rejects."*
The author worked around it with per-file fetches and these five slipped
through. The objects were intact, so `git cat-file blob HEAD:<path>` recovered
them without touching the network.

**3 from `PeetCrypto/freqtrade-stuff`.** Not a clone but a per-file harvest; 410
files present, these three absent. Two carry spaces and parentheses in their
names (`NFIXMod1.3_TraNz (3).py`, `NostalgiaForInfinityXw (1).py`), which most
likely broke the fetch. Re-fetched from the public repository with URL-encoded
paths.

All eight were verified to parse and to contain exactly the `IStrategy` class
the ledger names — no HTML error pages, no name mismatches. Classification now
covers **895 of 895** instead of 887, and 7 of the 8 are `G0` cases that enter
the load probe.

## Phase 1e — parallel candle download

| | |
|---|---|
| What | `repair/fetch_parallel.py` |
| Class | 1 |

The audit's `fetch_bulk.py` data logic is imported and reused unmodified — same
Binance monthly archives, same parser, same daily top-up for the unclosed month,
same de-duplication and column order. Only the scheduling changes: 16 concurrent
(pair, timeframe) jobs instead of one sequential pass.

`fetch_bulk.main()` takes a single global lock named `fetch`, because the author
once had two downloaders writing the same candle files. That hazard is real but
it is per output FILE, and each (pair, timeframe) writes its own. This driver
serialises per file — a job is skipped when its file is already complete — and
runs different files concurrently, so the property the original lock protected
is preserved. Writes go through a `.tmp` plus `os.replace`, which the original
does not do, so an interrupted run cannot leave a half-written file that the
size check would later mistake for complete.

## A second mistake of ours, found and fixed

The load probe took "the last line of output" as the verdict. TensorFlow and
absl write to stderr *after* the probe has printed, so two results were reported
as `I0000 00:00:...` log lines. Fixed by having the child mark its verdict with
an explicit sentinel.

The fix itself then broke the probe to **0 of 399**: of two intended
replacements only the parser-side one applied, and the assertion guarding it
merely checked that the marker appeared *somewhere in the file* — which the
parser-side change alone satisfied. A check that cannot see its own failure is
not a check. The assertion now looks specifically inside the `CHILD` block, and
the fix was verified by running real probes rather than by reading the file.

## Effect, measured

| Stage | Strategies importing (of 399) |
|---|---:|
| Audit author's baseline (`loadcheck_run.json`, comparable subset) | 268 of 362 |
| ftenv + packages + corrected path order | 304 |
| plus shim (`np.NAN`, freqtrade parameters) | 312 |
| plus `numpy.lib.math` alias | 337 |
| plus xgboost/portalocker, sentinel fix, 8 files recovered | 352 |
| plus catboost/matplotlib | **353** |

Importing is necessary but not sufficient: a strategy that imports can still die
inside `populate_indicators` on a pandas API change, and it needs candle data
for its declared timeframe. With the candle set now complete, the second
condition resolves as follows.

| | Count |
|---|---:|
| Newly importing | 353 |
| of those, candle data present for the declared timeframe | **283** |
| no timeframe declared anywhere (unmeasurable by construction) | 67 |
| exotic timeframe with no data (`12h`, `5h`, `1hr`) | 3 |

| Corpus reach | Strategies | Share |
|---|---:|---:|
| Measured by the audit as published | 496 | 55.4% |
| Could now enter the ladder | **779** | **87.0%** |

The remaining unknown is runtime: how many of the 283 survive an actual backtest
rather than merely importing. That is not yet measured and must not be assumed.

## A mistake of ours, found and fixed

The first version of `loadprobe.py` **prepended** the strategy directory to
`sys.path`. Local files such as `technical.py` then shadowed real packages and
**12 strategies that had loaded fine before started failing** — the repair did
damage. It surfaced only because the result (287) was worse than the audit
author's own baseline (268 of 362) and the number was not taken at face value.
Fixed: `sys.path.extend(...)` instead of `sys.path[:0]`. Installed packages win,
local helpers stay reachable.

## Data note: weekly candles have systematic gaps

The 1w series are missing 8 weeks each, identically across all eight pairs, and
every missing week **starts in the last days of a month** (2022-05-30,
2022-06-27, 2022-08-29, 2022-09-26, 2022-10-31, 2022-11-28, 2025-01-27,
2025-02-24). Binance's monthly archive for weekly klines omits weeks that
straddle a month boundary. This is a property of the source and of
`fetch_bulk.py`'s month-by-month strategy, not of this parallel driver — the
original would produce the same series.

Impact here is negligible: exactly 1 strategy in the corpus declares `1w`. It is
recorded because an undocumented hole in a series is the kind of thing that
later gets mistaken for a result. All other timeframes are gap-free to 100%,
except 2h at 99.9%.

## Candle inventory

88 files, 8 pairs x 11 timeframes, 54.8M candles, 1.4 GB. Zero corrupt files;
the downloader reported no network failures on any of the 75 jobs.

| TF | candles | gap-free |
|---|---:|---:|
| 1m | 32,894,210 | 100.0% |
| 3m | 10,964,766 | 100.0% |
| 5m | 6,578,876 | 100.0% |
| 15m | 2,192,980 | 100.0% |
| 30m | 1,096,529 | 100.0% |
| 1h | 548,322 | 100.0% |
| 2h | 274,234 | 99.9% |
| 4h | 137,176 | 100.0% |
| 6h | 91,481 | 100.0% |
| 1d | 22,875 | 100.0% |
| 1w | 3,161 | 97.6% |

Series edges match the known listing history: XMR ends 2024-02-20 (delisted),
DASH starts 2019-03-28, XLM 2018-05-31, XRP 2018-05-04, ADA 2018-04-17. BTC, ETH
and LTC span the full window from 2018-03-01.

---

# Phase 3 — Class 2: overlays of strategy code

**This is the only phase that edits copies of strategy files.** Originals in
`repos/` stay untouched; patched copies live in
`repair/patched/<same relative path>` with a unified diff per file in
`repair/patched/diffs/`. Measurement points `--strategy-path` at the overlay.
These results belong to `population=repaired`; Class 2 remains visible through
the provenance and equivalence fields above rather than becoming a third
population.

Tool: `repair/patch_class2.py`. Result: **59 strategies patched, 0 refused.**

## The standard every rule must meet

A patch is allowed only when it can be *proven* not to change trading behaviour.
Each rule carries a `precondition` evaluated against the specific file; a rule
that cannot establish its precondition skips the file and records why. Guessing
what the author meant is not repair.

| Rule | What it must prove | Files |
|---|---|---:|
| `dead_np_where_dtype` | `dataframe['pmx']` has stores and **zero loads** - write-only, so the value cannot reach any decision | 37 |
| `param_missing_space` | the parameter's name is a key in **exactly one** of `buy_params` / `sell_params` - the file states its own answer | 5 |
| `pandas_removed_keywords` | pandas' documented `fillna(method=...)` replacement is used without changing arguments or direction | 19 |
| `rolling_any_masked` | the disputed rows cannot reach the result (see below) | 1 |
| `restore_commented_feature_source` | restores the sole producer of 15 columns that are immediately consumed; behavior changes and is flagged | 1 |
| `rolling_any_detect_only` | - never patches, reports only | 0 |

Counts are rule applications; four strategies receive both
`dead_np_where_dtype` and `param_missing_space`, so 63 applications affect 59
strategy overlays.

Equivalence classification by rule:

| Rule | `equivalence_status` |
|---|---|
| `dead_np_where_dtype` | `strict_equivalent` for trading output (the value is dead) |
| `param_missing_space` | `strict_equivalent` |
| `pandas_removed_keywords` | `strict_equivalent` |
| `rolling_any_masked` | `output_equivalent` |
| `restore_commented_feature_source` | `behavior_changed` |

## Why dead_np_where_dtype is safe

```python
pmx = np.where((pm_arr > 0.00), np.where((mavalue < pm_arr), 'down', 'up'), np.NaN)
```

numpy 1 merged the string branches and the float NaN into a string array; numpy 2
refuses. `'nan'` is what numpy 1 actually produced, but that fidelity argument is
secondary: the precondition establishes on the AST that the resulting column is
written and never read, so no replacement can change a trade.

The first version of this precondition used a regex and the condition
`if not m or A and B`, whose operator precedence made it far laxer than intended
- it could have passed a file where the column **is** read. Replaced by an AST
walk counting `Store` and `Load` contexts, which answers the question exactly.

## Why param_missing_space does not rename

freqtrade 2026.7 raises `Cannot determine parameter space for X` when a
parameter has neither an explicit `space=` nor a `buy_`/`sell_` name prefix.
Adding `space='buy'` is provable because the file itself states the answer: the
tuned value sits in `buy_params`.

Renaming the attribute to `buy_max_slip` is the obvious alternative and is
**wrong** - the params-dict key would no longer match, the tuned value (0.668)
would be silently dropped and `default=0.33` would take over. A behaviour change
wearing the mask of a rename.

## Why pandas_removed_keywords is compatible

pandas removed the `method=` keyword from `fillna`. The overlay replaces only
the documented forms `fillna(method='ffill', ...)` and
`fillna(method='bfill', ...)` with `ffill(...)` and `bfill(...)`, preserving the
direction and axis/limit arguments. Where the legacy call is a chained
`dataframe[column].fillna(..., inplace=True)`, pandas 3 Copy-on-Write no longer
updates the parent DataFrame. The overlay uses the directly equivalent parent
assignment `dataframe[column] = dataframe[column].ffill()` (or `bfill()`). This
restores the pre-Copy-on-Write parent update without inventing a value or signal.
The rule does not infer replacements for other removed APIs.

## Why restore_commented_feature_source is behavior-changing

`AstroQAV4` consumes 15 Murrey-math columns whose only producer is a function
call and loop commented out immediately above the consumers. Restoring those
three lines makes the strategy executable and is strong evidence of the
author's intent, but it plainly changes executed code. It is therefore marked
`behavior_changed`, remains in the repaired population with that flag, and is
excluded from compatibility-equivalence sensitivity results.

## Why rolling_any is refused in general but patched once

pandas removed `Rolling.any`. Candidate replacements were measured against each
other and they **disagree in the first n-1 rows**: `.max().astype(bool)` yields
True where `.sum() > 0` yields False, because `NaN.astype(bool)` is True. Which
of them matched the removed method can no longer be observed - the method is
gone. Unproven equivalence, so the generic rule reports and never writes.

`A9AV` is patched because there the disagreement provably cannot reach the
result, and the precondition checks each step rather than trusting the argument:

1. the term is ANDed with `volume > SMA_9`, and `SMA_9 = rolling(length).mean()`
   is NaN for its first `length-1` rows, where `NaN > x` is False - those rows
   cannot produce a signal at all;
2. the disputed rows are `0 .. n-2` with `n = opposing_signal_filter`;
3. from the declared ranges n in [1,5] and length in [5,15], max(n) <= min(length),
   so the disputed rows fall inside the masked region across the **whole**
   declared parameter space, not merely at the defaults.

Verified afterwards by running the patched file: it loads, resolves
`length = 9` and `opposing_signal_filter = 2`, and backtests. The original
`AttributeError: 'Rolling' object has no attribute 'any'` is gone.

Noted in passing, not fixed: on the buy side the filter is dead logic.
`dataframe['sell_signal'] = 0` is set in `populate_indicators` and only becomes
non-zero in `populate_sell_trend`, which freqtrade calls *after*
`populate_buy_trend` - so at that point the column is all zeros and the filter
always passes. That is a defect in the strategy, and repairing it would be
authorship, not repair.

## A finding about the audit's config, not about the strategies

16 of the strategies measured so far fail with:

```
Market entry orders require entry_pricing.price_side = "other".
```

The audit's config sets `"same"` for both entry and exit pricing. Every strategy
declaring market entry orders therefore aborts before a single candle is
processed, and its card reads "could not be measured" - true, but it reads as a
property of the strategy when it is a property of the config. 15 of the 16
declare a market entry order, 1 a market exit.

Two earlier attempts to size this from source text produced counts the ledger
contradicted (224 strategies of which the audit had measured 150; then 87 of
which 51). A count the ledger contradicts is a broken count, not a finding.
`repair/scan_market_orders.py` now derives the population from the cards that
actually failed and uses source scanning only to describe them.

---

# Phase 4 — execution-profile compatibility audit

`evidence/PROFILE_CLASS1.json` records the additional environment/configuration
restorations discovered by the native futures-profile smoke runs.
`evidence/PROFILE_REPAIRS.json`, generated by `evidence/profile_repairs.py`, records 26 additional
Class 2 overlays: 23 `strict_equivalent` and three `output_equivalent`.
Originals remain untouched. The rules cover NumPy string/NaN coercion, explicit
writable buffers for current pandas/PyWavelets, current futures settlement-pair
syntax, signal-column dtype initialization, and one neutral parameter-space
declaration.

`FOttStrategy` additionally contains two unused-variable loops that repeatedly
apply whole-DataFrame shift recurrences once per candle, plus a chained
`Series.iat` write that pandas 3 Copy-on-Write no longer propagates. Rule
`linearize_quadratic_fixpoint_recurrence` evaluates the identical recurrence
left-to-right in NumPy. `repair/verify_fott_linear.py` proves exact OTT/VAR
equality against emulated writable legacy-pandas semantics on twelve rising,
falling, and deterministic-random cases. The original file remains untouched.

All 101 native futures candidates were attempted with `evidence/profile_smoke.py`: 84
measured and 17 failed with explicit reasons. The remaining failures are not
silently “repaired”: incomplete author configurations, unavailable historical
model/dependency stacks, and the credential-bearing `KMM` source remain blocked
or partial. `HurstCycleV4` succeeded in a longer control window and therefore
was correctly classified as a smoke-window limitation rather than repaired.

## Class 1: datetime-safe copied RMI helper

`DWT_LongShort`, `DWT_short`, and `FTT_DWT_FBB_FUTURES` import the author's
copied Solipsis `custom_indicators.py`. Its `RMI` implementation calls
`fillna(0)` on the whole Freqtrade dataframe. Current pandas rejects integer
zero for the timezone-aware `date` column before the indicator can run.

`repair/compat_helpers/custom_indicators.py` re-exports the copied module and
overrides only `RMI`: it fills the two numeric intermediates `maxup` and
`maxdown` that the formula actually consumes. The formula and its returned
series are otherwise unchanged. This is recorded as Class 1 rule
`datetime_safe_rmi_fillna`; it restores compatibility without changing the
strategy's intended behavior.

The same global Class 1 aliases used by the original Windows audit environment
are activated in the Linux diagnostic runtime through the versioned
`repair/sitecustomize.py`. This is environment parity, not an additional
strategy repair.

## Class 1: FreqAI runtime parity boundary

The pinned Linux audit image now includes `xgboost==3.4.1`, matching the native
Windows audit environment and restoring XGBoost-backed strategy imports without
touching strategy source. The official Freqtrade 2026.7 image uses Python 3.14,
for which TensorFlow publishes no compatible wheel. `TSPredict` and
`tsp0chicken` therefore run in the isolated Windows Python 3.13 environment
with Freqtrade 2026.7, TensorFlow 2.21.0, XGBoost 3.4.1, NumPy 2.5.2, pandas
3.0.5, SciPy 1.18.1, and TA-Lib 0.7.1. Every result records this runtime ID;
the boundary is environment compatibility, not a Class 2 strategy edit.

When Windows Application Control later blocked that environment, the canonical
pooled `BuyRegions` run moved to `runtime/Dockerfile.audit-tensorflow`: a separate
digest-pinned Python 3.12 Linux base with the same Freqtrade, TensorFlow, Keras,
NumPy, pandas, SciPy, and TA-Lib versions. The standard Python 3.14 audit image
is unchanged. The manifest records the special image digest, and neither the
canonical strategy bytes nor signal calculations are modified.

## Class 1: historical delisted-pair execution

The frozen spot basket intentionally retains XMR/USDT through its documented
2024-02-20 Binance delisting boundary. Current Freqtrade's `StaticPairList`
otherwise removes an inactive market before backtesting and reports `No pair in
whitelist`, even though complete historical candles are locally available.
`runtime/profile_spot_config.json` and the generated canonical spot-bias config therefore
enable StaticPairList's documented `allow_inactive` option. This changes no strategy signal or historical price;
it permits the preregistered available-history run that the coverage policy
already requires.

## Class 1: isolated analyzer discovery path

Freqtrade's look-ahead and recursive commands enumerate and import every Python
file under `--strategy-path`, not only the requested class. A targeted
`BbandRsi` diagnostic therefore failed while importing unrelated sibling
`AutoArimaTripleV1`, whose module-level logger assumes an absent repository
`logs/` directory. Bias diagnostics now copy the exact canonical target bytes
to an ignored one-file resolver directory and append the original source
directory only as a low-precedence helper-import path. Installed packages keep
precedence, local author helpers remain available, the archived strategy hash
stays identical, and an unrelated sibling can no longer decide the target's
diagnostic status. This is resolver isolation, not a strategy source repair.

`BuyRegions` also imports the author's adjacent `utils` package. Its Class 1
runtime entry now retains `repos/nateemma_strategies` while the canonical file
is isolated, exactly as the already registered `TSPredict` family does. No
strategy bytes or signal calculations are changed.

Generated diagnostic configs are written with explicit LF newlines on both
Windows and Linux. This removes host line-ending differences from the config
identity hash; it does not alter parsed configuration values or execution.

---

# Phase 5 — the 32 `to_be_fixed` rows (Stufe 1), 2026-09-09

`REPAIR_LIST.md`'s `to_be_fixed` family (32 strategies that never ran) was
worked row by row: could each be repaired mechanically, and is the evidence
already on record. Four sub-families, each with its own established route.

## `local_module_off_path` (15) — `repair/local_modules.py` re-run

The row's own automated resolver was re-run cold against the current corpus.
**1 resolved, 14 confirmed unresolved.**

`FileLoadingStrategy` resolved: 1 copy of `custom_order_form_handler` in the
corpus satisfies the import, applied to `evidence/PROFILE_CLASS1.json`. Class 1,
no strategy bytes touched. Re-probed with `evidence/profile_smoke.py` afterwards:
the import now succeeds, and the row moved to a *different*, already-known
unfixable defect — no `timeframe` declaration of any kind, the same class as
`EMA003` below. Net effect: one defect traded for another, correctly
diagnosed rather than silently left on the old error.

The other 14 (`BBBHold`, `BBKCBounce`, `BB_RPB_3c`, `BTCMACDCross`,
`BinanceStream`, `DonchianBounce`, `DualModelPolymarketPortfolio`,
`EmaCrossStrategy`, `Hammer`, `KeltnerBounce`, `MlpSpeculativeStrategy`,
`PolymarketMeanReversionStrategy`, `PolymarketMomentumStrategy`,
`TEMABounce`) stay `unresolved`: no copy of the missing module anywhere in
the corpus makes the import succeed. Spot-checked `BBBHold` by hand rather
than trusting the resolver blind: its own directory *does* carry a
`Config.py` (`.../startegy test/5/_BBBHold/Config.py`), and the resolver did
try it — it fails for the same reason as every sibling copy, because that
`Config.py` genuinely does not define `use_exit_signal`, the attribute
`BBBHold.py` reads from it. Not a corpus-search gap; the author's own bundled
config is incomplete in every copy this repo shipped. Inventing the missing
attribute would be authorship, not repair.

## `timeframe_missing` (13) — all already refused, none overridden

`evidence/eligibility_timeframe_repair.py` had already resolved this entire
family before this pass; nothing here was re-guessed. 7 are FreqAI strategies
whose timeframe comes from the freqai config block, not the strategy source
(`FreqaiBinaryClassStrategy`, `FreqaiExampleStrategy`,
`LitmusGoodMinMaxClassificationStrategy`, `MultiTargetClassifierTestStrategy`,
`MultiTargetRegressorTestStrategy`, `QuickAdapterV3`, `TrendMomoClassifier`).
4 declare only `informative_timeframe`, a different value from the unstated
base (`Chained`, `EnsembleStrategy`, `EnsembleStrategyV1`,
`EnsembleStrategyV2`). `EMA003` declares no timeframe at all. `ScalpingCCI`
declares `ticker_interval = '15'` with no unit — and its own code branches on
whether the string contains `"m"`, so guessing the unit would pick a
different code path than the author's value produces. All six refusals are
evidence-based, not merely unattempted; none is overridden here.

## `freqai_not_enabled` (2)

`E0V1EAI` declares its own `timeframe = '5m'` in source — the *timeframe*
half of this family's usual problem does not apply to it — but nothing in
`repos/hamidreza07_freqai-strategy` (no JSON, no comment, no docstring) names
a `freqaimodel`. Enabling freqai without an author-stated model would be
choosing one ourselves; not attempted, same standard as the timeframe
refusals above. `RLStrategy` was already run under the freqai investigator
arm (`repair/FREQAI_RESULTS.md`): even with freqai enabled it produces no
usable summary because its training data is removed entirely by NaN
filtering, an author-side data problem, not a config gap. Not re-attempted.

## `freqai_model_missing` (2) — the "Impossible to load FreqaiModel" message was masking two different real causes

Both rows already had a config restored from the author's own settings
(`evidence/ELIGIBILITY_FREQAI_REPAIR.json`, `restore_author_config`) and both
still failed. Freqtrade's load error names none of the three things it could
be, so each was traced by hand rather than accepted at face value:

**`FreqaiExampleHybridStrategy`.** The model class
`CatboostClassifier` genuinely exists in the corpus
(`repos/markdregan_FreqAI-Marcos-Lopez-De-Prado/freqtrade/freqai/prediction_models/CatboostClassifier.py`,
imports only the installed `catboost` package and standard
`freqtrade.freqai.*` — no custom sibling dependency). The prior run's
invocation never passed `--freqaimodel-path`, so freqtrade only searched
`user_data/freqaimodels` and its own installed package, neither of which has
it. Re-run with `--freqaimodel-path` pointed at that directory, under
`strategy-audit-runtime-rl:2026.7` (already carries `catboost`, built for the
freqai-rl arm and reused here since the lean image does not). That got past
the load error and into real training — and then failed differently:
`KeyError: '&s-up_or_down'` in the strategy's own `populate_entry_trend`
(`FreqaiExampleHybridStrategy.py:274`), reading a prediction column the
corpus's `CatboostClassifier` does not return under that name. Two
independent problems shared one generic message; the first is fixed, the
second is a genuine mismatch between this forked model implementation and
this strategy's expectations, not something to paper over by renaming a
column. Left unresolved, status not changed to `applied` in
`evidence/PROFILE_CLASS1.json` for this row.

**`LitmusMetaStrategy`.** The model class `LitmusMultiTargetClassifier` also
exists (`.../user_data/freqaimodels/deprecated/LitmusMultiTargetClassifier.py`)
and the prior invocation's `--freqaimodel-path` already pointed at it
correctly — that was not the problem. The file itself imports
`freqtrade.litmus.model_helpers`, a custom subpackage this repository bundles
inside its own forked copy of freqtrade (`repos/markdregan_.../freqtrade/litmus/`),
not inside the installed freqtrade package. Reaching it would mean putting
that repo's root on the import path — and `repair/local_modules.py`'s own
`SHADOWS` guard exists for exactly this case: that directory contains a
`freqtrade/` package of its own and would replace the installed one for
every strategy in the same process, not just this row. Not attempted; this
needs a narrower mechanism (e.g. exposing just the one submodule under
`sys.modules['freqtrade.litmus']`) that has not been built or proven safe,
so it is left diagnosed rather than half-fixed under time pressure.

## A repair outside the 32, found while fixing `FreqaiExampleHybridStrategy`

`FreqaiExampleStrategy` sits in the `timeframe_missing` family above (its
timeframe comes from the freqai config, refused there) but turned out to be
freqtrade's own official template, byte-identical to the one shipped inside
the installed `freqtrade` package apart from a pre-2026 typing/doc-link
diff — confirmed by diffing the corpus copy against
`ftenv/Lib/site-packages/freqtrade/templates/FreqaiExampleStrategy.py`
directly rather than assumed from the name. Its companion
`config_examples/config_freqai.example.json` in the same source repository
states `timeframe: "3m"`, `trading_mode: "futures"`, and a complete
`feature_parameters` block. Built into `user_data/freqai_configs/FreqaiExampleStrategy.json`
on top of `runtime/profile_futures_config.json` (the strategy sets
`can_short`, which freqtrade refuses under a spot config), run with
`--freqaimodel LightGBMRegressor` — a freqtrade-bundled model, no extra
package.

## Not attempted, deferred for a dedicated pass

`QuickAdapterV3`'s model, `QuickAdapterRegressorV3`, and its config template
both exist in the corpus (`repos/jerome-benoit_freqai-strategies/quickadapter/`),
unlike the rows above where a config had to be built from evidence. But the
model file imports `optuna`, `optunahub`, `scikit-image`, and a local sibling
module `LabelTransformer` — three new packages plus another local-module
resolution, a bigger lift than a single package pin. Not attempted this pass.

`LitmusGoodMinMaxClassificationStrategy`, `MultiTargetClassifierTestStrategy`,
`MultiTargetRegressorTestStrategy`, `FreqaiBinaryClassStrategy`,
`TrendMomoClassifier`: no author-provided config or named model anywhere in
their repositories (checked directly, not assumed from the family). Same
standard as the timeframe refusals above — not fixed without inventing a
choice the author never stated.

---

# Phase 6 — fetching what harvest never pulled, and two tools that fetch it wrong

Continuation of Phase 5, on explicit instruction: for the local-module and
timeframe rows still open, check the strategy's own origin GitHub repository
rather than stopping at "not in our corpus." Three repositories, eight
strategies fixed this way, plus two real bugs in the repair tooling itself,
found only because the fetched evidence let a genuine positive be told apart
from a tool problem.

## Fetched from origin: `webclinic017/strategies-freqtrade-`

`BBKCBounce`, `BTCMACDCross`, `DonchianBounce`, `TEMABounce` all do
`from user_data.strategies import Config`. GitHub's tree for this repo has
`archived/Config.py` — never harvested (no `IStrategy` literal) — sitting in
the same directory as all four. Every attribute the four strategies read
from it (`minimal_roi`, `trailing_stop*`, `stoploss`, `timeframe`,
`process_only_new_candles`, `use_sell_signal`, `sell_profit_only`,
`ignore_roi_if_buy_signal`, `order_types`) is confirmed present in the
fetched file before use. The import is dotted (`user_data.strategies`, not a
bare `Config`), so a plain `sys.path` entry cannot satisfy it — the fetched
file was placed at
`repair/compat_helpers/webclinic017_config/user_data/strategies/Config.py`,
an import-namespace package (no `__init__.py` in either `user_data/` or
`strategies/`) that merges via PEP 420 with the audit's own `user_data/
strategies/`, which is real but empty, rather than shadowing it. All four
measure now (52/0/0/0 trades in the smoke window — a real result, not
another failure: three of them are genuinely quiet in one month, the same
question `evidence/profile_full_window.py` already exists to settle).

## Fetched from origin: `mlsys-io/PortfolioBench`

`EmaCrossStrategy`, `PolymarketMeanReversionStrategy`,
`PolymarketMomentumStrategy` import from `alpha.*`; `DualModelPolymarketPortfolio`
additionally from `polymarket.contracts`. Both packages exist in the repo's
tree, both are pure pandas/numpy/talib (checked before fetching, to keep the
fetch itself bounded) with no heavy dependency, and neither was ever
harvested for the same IStrategy-only reason. Fetched into `repair/
compat_helpers/mlsys_io_portfoliobench/{alpha,polymarket}/` and registered
against all four rows. `DualModelPolymarketPortfolio` measures (0 trades).
The other three additionally lacked a timeframe (`ScalpingCCI`'s family, not
this one) — the repository's own `pipelines/simple_ema_cross.json` names
`EmaCrossStrategy` by its pipeline type and states outright, in prose,
"4-hour timeframe"; `user_data/config_polymarket.json`, a config the repo
keeps separate from its generic 5m default specifically for the Polymarket
strategies, states the same 4h. Added to `evidence/eligibility_timeframe_repair.py`'s
`MANUAL` table as `corpus_twin` evidence, the same category `FixedRiskRewardLoss`
already used there. All three now measure with real trades: 28, 2, 10.

`MlpSpeculativeStrategy` (same repo) is not attempted: its dependency chain
reaches `.h5`/`.keras` model files, meaning TensorFlow/Keras — a different
runtime image, not a fetch.

## Fetched from origin, but the row stays refused: `BinanceStream`

`from binance import Client` looked like another missing corpus module;
it is the `python-binance` PyPI package, a name collision `repair/
local_modules.py`'s own docstring already warns about. Installed
(`python-binance==1.0.37`, verified in isolation against the numpy/scipy/
pandas pins, added to `runtime/requirements-audit-runtime.txt`, image
rebuilt). Past that, `from freqtrade.strategy.interface import
SellCheckTuple, SellType` — freqtrade's sell-to-exit rename moved
`ExitCheckTuple`/`ExitType` to `freqtrade.enums`; `SellCheckTuple` also
renamed its one constructor keyword (`sell_type` → `exit_type`), and the
enum's own member names renamed too (`SELL_SIGNAL` → `EXIT_SIGNAL`, ...).
Fixed with a new Class 1 signature shim,
`repair/compat_signature.py:install_legacy_sell_check_tuple` — a
keyword-translating wrapper around `ExitCheckTuple` plus a small
`__getattr__` proxy that translates the well-documented SELL→EXIT enum
renames and passes anything else through unchanged. Past both blockers, the
row hits `'stoploss' is a required property` — the strategy declares none,
anywhere. That is `no_stoploss`, the same author-side gap already refused
for ten other rows; correctly refused here too, not invented.

## Not found anywhere, including the live origin: `BB_RPB_3c`

`user_data.freqtrade3cw`, imported by `PeetCrypto/freqtrade-stuff`'s copy,
does not exist in that repository's current `HEAD` either — checked by tree
listing, not assumed. Genuinely gone, not merely unharvested. Stays
unresolved.

## A bug in `repair/local_modules.py`, found by a result that didn't add up

`BBBHold`/`Hammer`/`KeltnerBounce` (the `hamidreza07/freqai-strategy` `Config`
family from Phase 5) were re-checked here rather than left as "no copy
works," because the earlier verdict rested on comparing many candidates'
error text and every one read the same generic
`AttributeError: module 'Config' has no attribute 'X'`. Tried alone, in a
fresh process, `NSeq/Config.py` satisfies `BBBHold`'s import cleanly. Tried
through `resolve()`'s own candidate loop, it failed with the same
`AttributeError` as everything before it.

Cause: `try_import()` execs the strategy file, which does `import Config` -
resolved through the REAL import system, which caches the result in
`sys.modules['Config']`. The function only ever cleaned up its own synthetic
probe name, never that. Many of these rows share the literal name `Config`,
so the FIRST candidate tried for ANY of them poisoned the cache for every
later candidate and every later row in the same process — a later,
genuinely-satisfying candidate imported the earlier candidate's stale
module instead of its own file, kept failing, and was recorded `unresolved`
on a false negative.

First fix attempt evicted every `sys.modules` key the exec added, which
went too far the other way: `technical`/`talib`/freqtrade's own vendored
`qtpylib` carry process-global C-extension/registration state that does not
tolerate being re-executed under a new module object, and rows started
failing with `ImportError: cannot load module more than once per process`
instead. Correct fix evicts only the specific module under test (and its
submodules) before and after each attempt — `try_import()` now takes the
target module name for exactly this. Re-run: `BBBHold` resolves to `NSeq`
(same file as before, the caching bug just never let it be tried clean);
`Hammer` and `KeltnerBounce` resolve to `BuyDips`. All three measure now
(36, 1 trades; `BBBHold` still fails, on a *different* missing attribute,
`ignore_roi_if_buy_signal`, that no candidate anywhere — corpus or fetched —
happens to define together with `use_exit_signal`; a real, if narrower, gap
in the author's own publishing, not this tool's bug).

## Two selftest/precedence conflicts from applying fixes by hand

Registering a GitHub-fetched fix under the resolver's own rule name,
`restore_copied_local_module`, broke `repair/local_modules.py --selftest`'s
own invariant — "nothing carries this rule without `resolve()` having found
it" — for exactly the rows this phase fixed by a route `resolve()` cannot
take (it only ever searches this corpus's own `repos/**`, never `repair/
compat_helpers/`). Given a genuinely different provenance, given it a
genuinely different name: `restore_fetched_local_module`, mapped to the
same `local_module_off_path` family in `evidence/strategy_status.py`'s
`SHIM_FAMILY`. The invariant is true again because the two things it was
conflating are no longer registered under the same name.

That rename then broke something else: `evidence/strategy_status.py` decides
whether a repair-store measurement supersedes a stale `PROFILE_SMOKE.json`
failure by comparing the repair store's *snapshotted* `class1_rules` against
the *current* `PROFILE_CLASS1.json` rules for that row — and the retag
changed the current side out from under three already-measured rows
(`EmaCrossStrategy`, `PolymarketMeanReversionStrategy`,
`PolymarketMomentumStrategy`), so their real, `measured`, 28/2/10-trade
results stopped counting as current and the rows fell back to their old
`PROFILE_SMOKE.json` failure. Fixed by re-running `eligibility_timeframe_repair.py`'s
smoke stage for the three so their stored snapshot matches the live rule
name again.

A second, independent staleness surfaced the same way and from the same
root cause — three rows (again `EmaCrossStrategy` and the two Polymarket
strategies) excluded as `local_module_repair_exhausted` although they were
genuinely trading. `attempted` (rows `repair/local_modules.py`'s OWN search
still calls `unresolved`, since it never looks in `repair/compat_helpers/`)
was unconditionally overwriting a `repaired` verdict that had already been
set, two lines earlier in the same function, from a real `measured` result.
Fixed by not overwriting a verdict that already reads `repaired`.

Between these two, a third and unrelated cause of the same symptom: this
phase's own live test of the harvest.py change below re-fetched
`mlsys-io/PortfolioBench` and, in doing so, legitimately overwrote
`EmaCrossStrategy.py` on disk with fresh bytes from GitHub - moving its
`canonical_sha256` out from under the already-measured record a third time.
Not a bug; `evidence/execution_profiles.py` and `evidence/profile_smoke.py`
were simply re-run to bring the corpus-derived stores back in sync with
what is now actually on disk, the same recovery a genuine upstream edit
would need.

## Two more `ModuleNotFoundError`s from the September reorg, found the same way this session's Antigravity/AntigravityV3 admission bug was

`evidence/eligibility_admit_converged.py` (`import strategy_status`) and
`evidence/execution_profiles.py` (`from profile_smoke import _read_jsonc`,
reached only through the JSONC fallback branch, which is why it survived
`--selftest`) both still used the pre-reorg bare-module form. Both now read
`from evidence import <module>`, matching every sibling script the reorg
already updated correctly. A repo-wide grep for the same bare-import shape
across `evidence/`, `tools/`, `repair/`, `regime/`, `cluster/` found three
more candidates (`tools/probe_shim_neutral.py`, `cluster/classify.py`,
`repair/measure_one.py`) — each has its own explicit `sys.path.insert(...)`
immediately before the bare import and is correct as written; the two fixed
here had no such guard, which is what made them the actual bug.

## `tools/harvest.py`: fetch what a strategy needs, not only what contains "IStrategy"

Standing instruction after this phase: harvest should not require finding
the same missing sibling by hand, repo by repo, again. Three additions,
each capped to keep the module's whole reason for existing (avoid a
271 MB `git clone` for a handful of strategies) intact:

1. `Config.py` (any case) is now kept unconditionally — it never contains
   the `IStrategy` literal itself, only values a sibling strategy reads.
2. `dependency_closure()` parses every kept file's own top-level
   `import`/`from ... import` lines and, for every name that resolves to a
   real path in *this repository's own tree* (never guessed — either it is
   there or it is not fetched), fetches it and parses its imports too,
   transitively, capped at `MAX_CLOSURE = 40` files so one repository's own
   wide `utils` fan-in cannot turn a single strategy into a second clone of
   the module count problem this file exists to avoid. Live-tested against
   `mlsys-io/PortfolioBench`: pulled `alpha/` and `polymarket/` in full,
   unprompted, exactly the two packages Phase 6 above fetched by hand.
   First version of this indexed every blob under a matched top-level name,
   not only `.py` ones, and pulled two PyTorch `.pth` checkpoint files
   (megabytes each) along with the source; restricted to `.py`.
3. `README*` at the repository root is fetched unconditionally, never
   executed — occasionally the only place a timeframe or config is written
   down in prose, as it was for `EmaCrossStrategy` above; this fold's own
   evidence would already be on disk if this fold had existed before it.

**Security boundary, added in the same fold.** Harvest fetches `.py` source
from ~900 unaudited public repositories that this audit later imports and
executes (freqtrade's resolver calls `exec_module` directly — no sandbox at
the Python level); nothing before this checked the content for anything
worse than a secret leaving in the other direction (`tools/secret_gate.py`).
New `tools/malware_gate.py`, same shape and the same stated boundary as
`secret_gate.py` — a pattern scan against known-dangerous shapes (decoded
`eval`/`exec`, `__import__`-obfuscated calls, a shell command built from a
downloaded string, `curl | sh`, a reverse-shell socket/dup2 pair, a write
into another program's autostart location, credential-looking env vars
POSTed out, `pickle.loads` of network content), not a sandbox and not proof
of absence, run on every fetched byte (strategy, `Config.py`, closure file,
README) before it is written to disk; a match is reported and the file is
withheld rather than written. Answers the direct question asked: no, this
was not previously ensured — the `IStrategy`/`config.py` filter alone says
nothing about a helper module three directories over, and nothing anywhere
in the pipeline scanned incoming content before this fold.

## Retroactive scan: everything harvested before the gate existed

`tools/malware_gate.py --scan-corpus` (new mode, same module) walks every
`.py` and `README*` file already under `repos/` — the identical predicate
`tools/harvest.py` now applies at fetch time — since the gate above only
protects what is harvested from this point on, and the ~900-repository
corpus already on disk predates it entirely. 4,779 files scanned (30 over
the 600 KB cap skipped, matching `harvest.py`'s own `MAX_FILE`; 0 unreadable),
report at `evidence/MALWARE_SCAN.json`.

**2 hits, both checked by hand and cleared — 0 confirmed.**

- `repos/eovie_freqtrade_strs/binance/aws_run_bot/README.md` — matched the
  `curl | sh` pattern on `curl -fsSL https://get.docker.com | bash`, Docker's
  own documented install one-liner, in a README's own AWS setup
  instructions. A real shape, an ordinary use of it.
- `repos/nateemma_strategies/scripts/noisycoconut_sweep.py` — matched the
  `__import__` obfuscation pattern on `{**__import__("os").environ}`, a
  compact way to copy `os.environ` into a dict without a top-level `import os`
  in a local hyperopt-sweep helper script. Calls `.environ`, not `.system()`
  or anything that reaches a shell; not obfuscating a dangerous call, just an
  inline import.

Consistent with the gate's own stated boundary (a pattern scan, not a
sandbox or proof of absence): every hit still needs a human read before it
means anything, same as `secret_gate.py`'s own false positives always have.
Re-run whenever the corpus grows, same as `secret_gate.py` runs before every
commit that adds files.

---

# Phase 7 — the excluded rows, checked again for a repairable local module

On explicit instruction: go back through everything already `excluded` and
look for rows a module fetch from their own origin repo could still move.
Scoped to `repair_family == local_module_off_path` — 11 rows before this
phase, `BinanceStream` counted among them only because of the bug fixed
first below.

## A third instance of the same precedence bug

Before the search could even start, `BinanceStream` (Phase 6's own row)
showed up misclassified: `evidence/BLOCKED_TRIAGE.json`'s fresh probe already
had it correctly as `no_stoploss`/`refuse_repair` - the genuine, final
verdict from last phase - but `STRATEGY_STATUS.csv` still read
`local_module_repair_exhausted`. The `attempted` block in
`evidence/strategy_status.py` (the one already guarded against overwriting a
`repaired` verdict, added earlier this same phase) had no matching guard
against overwriting a `refuse_repair` one - and a comment eleven lines above
it, describing exactly this scenario for a different row (`FBB_2`), had
already explained why that guard belongs there. Extended the condition to
`repair.get("verdict") not in ("repaired", "refuse_repair")`. Cohort counts
do not move (`BinanceStream` was already `excluded`); only its recorded
reason is now the true one.

## Two more genuine fetches, and a real gap in the fetch tool itself

`NNPredict` (`hamidreza07/freqai-strategy`) and `NNTC`
(`webclinic017/strategies-freqtrade-`) were both `local_module_off_path`,
both TensorFlow-based neural-net strategies, each blocked on several sibling
`.py` files never harvested. Both origin repos give every strategy its own
directory, `NNPredict`'s own `utils/` sitting IN that directory rather than
at the repo root the way `mlsys-io/PortfolioBench`'s `alpha`/`polymarket`
did in Phase 6.

That exposed a real gap in Phase 6's own `dependency_closure()`: it only
ever indexed and resolved names against the REPO ROOT. `import
NNPredictor_LSTM0` inside `NNPredict.py` cannot resolve there - the file
freqtrade actually needs sits beside `NNPredict.py`, in a directory
`--strategy-path` already puts on `sys.path`, never at the repo's own root.
Fixed by rebuilding `_tree_index()` to key on `(directory, name)` pairs
instead of bare names, and resolving each import against the importing
file's own directory FIRST, falling back to the repo root only if nothing
sibling matches - which is exactly why `NNTC`'s `utils/ClassifierKerasTrinary`
(root-level in that repo, unlike `NNPredict`'s) still resolves correctly
under the same function.

Fixing that surfaced a second bug: re-running the harvest against
`hamidreza07/freqai-strategy` (94 strategy classes) fetched a full 17-file
`utils/` tree for `NNPredict`'s neighbour `Anomaly` but never fetched
`NNPredictor_LSTM0.py` itself - the one file that started this whole chain.
`MAX_CLOSURE` was a budget shared across the ENTIRE repository's closure in
one pass, and Python's `set.pop()` has no defined order, so which of ~94
strategies' dependencies got fetched before the shared budget ran out was
effectively random. Restructured so each seed strategy gets its own
independent `MAX_CLOSURE` budget (`_closure_one()`), sharing only the
already-fetched set so nothing is downloaded twice - a strategy elsewhere in
a large repository can no longer starve a different one's three-file need.
Re-run: `NNPredictor_LSTM0.py` and its own `utils/ClassifierKerasLinear`
chain both present now.

`tqdm` (needed by `NNPredict`, present transitively in the native `ftenv`
but absent from both Docker images, which resolve from
`requirements-audit-runtime.txt` alone) added there, verified in isolation
against the pins. A second small package gap surfaced the same way:
`setuptools` 82.0.0 dropped `pkg_resources` from the default install (only
`setuptools[legacy]` still carries it), and both `NNPredict` and `NNTC`
import it directly through their shared `utils/Environment.py`. Pinned
`setuptools==80.10.2`, the last release before the drop, verified in
isolation. Both images rebuilt twice (once per package added).

**Module resolution for both rows is now complete and confirmed** - each
imports cleanly, with every sibling file the fetch was ever about. What
each hits past that point is a separate, deeper problem, neither one a
missing module:

- **`NNPredict`** reaches real training and fails inside
  `utils/ClassifierKeras.py`: `tf.compat.v1.keras.backend.set_session(sess)`
  - TF1's session-binding API, meaningless under TF2's eager execution,
    which Keras 3's `tf.compat.v1` shim does not fully restore. Silently
    no-opping it is not the kind of change this repair standard allows
    without a specific argument for why the training that follows is still
    the same training; not attempted under time pressure.
- **`NNTC`** reaches real training on `BTC/USDT` and fails on
  `blabels[np.where(slabels > 0)] = 0.0`: `ValueError: assignment
  destination is read-only` - the same pandas-3 copy-on-write class already
  on record for `DWT` in this same phase (and for the RMI helper patched in
  Phase 4), not a new kind of problem, just not this one's.

One genuine, reusable fix came out of getting this far: `NNTClassifier.py`
decorates a class with `@tf.keras.saving.register_keras_serializable(...)`
at import time. `tf.keras` is Keras 3's backward-compatibility namespace
(`keras._tf_keras.keras`) and re-exports most of `keras`, but not `saving` -
`keras.saving.register_keras_serializable` exists and works, `tf.keras.
saving` is simply missing from the compat module. New Class 1 shim,
`repair/compat_signature.py:install_tf_keras_saving` (rule
`tf_keras_saving_reexport`): assigns the real `keras.saving` across, the
same object reached through the name that already works, not a
reimplementation. `evidence/PROFILE_CLASS1.json` for both rows records
what module fetch achieved and what remains; neither is a false `applied`
claim about the strategy running end to end.

## Checked and confirmed unfixable this way — not fetched

- **`BB_RPB_3c`** (`PeetCrypto/freqtrade-stuff`): `user_data.freqtrade3cw`
  does not exist in that repository's current `HEAD` either (tree listing
  checked directly). Genuinely gone, not merely unharvested - already the
  Phase 6 finding, re-confirmed rather than assumed still true.
- **`Solipsis6`/`SolipsisMM`** (`PeetCrypto/freqtrade-stuff`, originally
  werkkrew's Solipsis family): need `custom_indicators.bollinger_bands` and
  `.fib_ret` respectively. Checked three places, not one: `PeetCrypto`'s
  copy, `werkkrew/freqtrade-strategies`' own original `custom_indicators.py`
  (the true source, `strategies/solipsis/custom_indicators.py`), and every
  `custom_indicators.py` anywhere in the whole corpus by function-definition
  grep. Neither function is defined anywhere. A confirmed gap in what the
  author himself ever published, not a harvest gap - inventing either
  function would be authorship measured as if it were his.
- **`DWT`**: already past its module blocker (applied in an earlier phase);
  the current failure, `buffer source array is read-only`, is a numpy
  copy-on-write issue unrelated to module availability. Not this question.
- **`AdvancedRiskFilterStrategy`** (`DonaldSimpson/remora-freqtrade`): the
  `remora` package genuinely lives in the same repository next to the
  example strategy and could be fetched - but `remora.client.RemoraClient`
  raises immediately without a real `REMORA_API_KEY` and, given one, calls a
  live hosted risk-scoring API (`https://remora-ai.com/api/v1/risk`) for
  every decision. Fetching the module would not unblock the row: the actual
  dependency is a paid third-party service this audit has no account for,
  the same class of blocker already declined for `KMM` (`openai`, Phase
  1a/4) - not attempted.
- **`Cenderawasih_freqai`** (`freqtrade.freqai.strategy_bridge`) and
  **`Enchilada`** (`technical.tradingview`): neither name resolves to
  anything in the strategy's own origin repository - checked directly, not
  assumed. Both are dotted paths under an already-installed package
  (`freqtrade`, `technical`) rather than the strategy's own repo, so "their
  own repo module" does not apply to either; genuinely absent third-party
  submodules, not local files.
- **`MlpSpeculativeStrategy`** (`mlsys-io/PortfolioBench`): its own module IS
  fetchable and now would be found automatically by the fixed closure - the
  blocker was never the fetch. It needs PyTorch AND TensorFlow/Keras
  together in the same runtime (`NNModel.py` imports `torch`, `ensemble.py`
  imports `tensorflow.keras`), and neither existing image
  (`strategy-audit-runtime-rl`: PyTorch only; `strategy-audit-tensorflow-runtime`:
  TensorFlow only) carries both. A third, combined image is a bigger,
  separate decision - not attempted this phase.

---

# Phase 8 — three requests at once: settle `to_be_fixed`, install for
`third_party_package`, patch `dtype_drift`

## 1. `to_be_fixed` settled through the mechanisms that decide it, not by hand

`REPAIR_LIST.md`/`blocked_triage.py`'s `to_be_fixed` label is a static,
message-pattern classification, unrelated to whatever a later, row-specific
investigation concluded - moving a row out of it means fixing what
`evidence/strategy_status.py` itself decides, not editing the generated
file. Four rows this phase actually is investigation had already settled,
each blocked by a genuine precedence bug: a fresher, more specific finding
was being overwritten by an older, vaguer one.

- **`FileLoadingStrategy`**: repaired past its local-module blocker in
  Phase 6, then found to have no timeframe declaration at all underneath -
  correctly refused by `eligibility_timeframe_repair.py`'s own `derive()`,
  but `strategy_status.py`'s `repair_source` block was overwriting that
  refusal back to the row's now-stale `local_module_off_path` label whenever
  ANY repair-store history existed for the row. Guard changed from
  `strategy not in repair_source` to `repair.get("verdict") != "repaired"` -
  `refused_timeframe` re-derives itself fresh from the row's *current*
  `runtime_failure` on every call, so it is never stale the way
  `repair_source` can be.
- **`RLStrategy`**: the FreqAI investigator arm already ran it and got a
  named, structural `freqtrade.exceptions.OperationalException` ("all
  training data dropped due to NaNs") - a different claim from "ran and
  produced nothing", but the verdict logic only recognised one specific
  exception text (`DI_cutoff`, `FreqaiExampleHybridStrategy`'s reason) as
  conclusive. Widened to recognise any named `OperationalException`, not
  just that one string.
- **`E0V1EAI`**: declares its own timeframe (5m), so `freqai_not_enabled`
  never described what actually blocks it - no `freqaimodel` name anywhere
  in `hamidreza07/freqai-strategy` (no config, no comment, no docstring).
  New family `freqai_no_model_named`, added to `NO_REPAIR_POSSIBLE`;
  `freqai_not_enabled` itself removed from `exclusion_criteria.py`'s
  `REPAIRS` list once E0V1EAI - the only row that ever carried it - moved
  off it, since the file's own selftest refuses a documented family with no
  matching row.
- **`BBBHold`**: local-module search resolved and applied (`NSeq/Config.py`
  satisfies the import), but the strategy also reads
  `ignore_roi_if_buy_signal`, which no `Config.py` anywhere - corpus or the
  true origin repository - defines. New family `local_module_incomplete`,
  also added to `NO_REPAIR_POSSIBLE`.

Both new families needed their own `REPAIRS` entry in
`evidence/exclusion_criteria.py` - the same selftest that catches an
undocumented family also catches a documented one with nothing to point at.

`NNPredict`/`NNTC`/`BB_RPB_3c`/`MlpSpeculativeStrategy` were deliberately
NOT moved: each is genuinely still open (a compat shim not yet attempted, a
combined runtime not yet built) or already excluded via a different,
already-accurate mechanism (`local_module_repair_exhausted`) - moving them
to `refuse_repair` would overstate how settled they are.

## 2. `third_party_package`: installed what installs, diagnosed what doesn't

Went through all 25 rows by distinct package name, not by row - several
share one package. Nine rows fixed, five packages added
(`prettytable`, `simdkalman`, plus `yfinance`/`pykalman`/`smartmoneyconcepts`,
which were already IN `requirements-audit-runtime.txt` from earlier phases
but had drifted out of sync with the native `ftenv` venv - that file only
ever governed the Docker images; `pip install -r
runtime/requirements-audit-runtime.txt` against `ftenv` directly brought it
back in line, which is what actually unblocked `Kalman`, `CME`'s first
layer, and `NNTC`/`BaseStrategy`'s `pkg_resources`, not new work). Now
measuring: **`Anomaly`** (513 trades), **`PCA`** (126), **`Kalman`** (111),
**`FBB_KalmanSIMD`** (69) via `prettytable`/`simdkalman`, both verified in
isolation against the pins and added to `requirements-audit-runtime.txt`,
image rebuilt.

**`BaseStrategy`**: past `pkg_resources` (setuptools fix carries over),
resolved `utils.DataframePopulator/DataframeUtils/Environment` as a
repo-root package (`repos/nateemma_strategies/utils`, sibling of
`Framework/` where the strategy lives - the sibling-then-root resolution
Phase 7 built). Runs into a new, different problem past that: the process
stops silently after "adding indicators" on all 8 pairs, no exception, no
archive - the same shape already on record for `avellaneda`. Not chased
further; a `Framework`-named class is also plausibly meant to be
subclassed, not run standalone.

**`GymStrategy`**: `from stable_baselines3 import PPO` needed no new build
at all - `strategy-audit-runtime-rl:2026.7` already carries it (freqtrade's
own RL extras). Its `ticker_interval = '5m'` is recoverable by the standard
route too. Neither is the real blocker:
`self.model = PPO.load('/freqtrade/user_data/model.gym')` needs a
pre-trained checkpoint that does not exist anywhere in
`PeetCrypto/freqtrade-stuff` (checked the tree directly) or the rest of the
corpus. Training one ourselves would decide the strategy's actual trading
behaviour, not restore it - registered `refuse_repair` /
`missing_author_data_file`, the same standard as any other missing data
file.

**Confirmed not installable, each for a different reason - not one
"declined" bucket:**

| Package | Rows | Why |
|---|---:|---|
| `zigzag` | 5 (`LitmusMinMax*`) | its `pyproject.toml` itself is malformed - `Cython>=^0.29` mixes PEP 508 and Poetry caret syntax, so pip's build backend refuses it outright. Confirmed on Linux inside `strategy-audit-runtime:2026.7`, not only the Windows machine the original block was recorded on - not an OS policy, a broken package. |
| `tvDatafeed` | 3 (`QuatreMousquetaires`, `kac_index_v1/v2`) | never published to PyPI at all (`pip index versions` finds nothing); its own docs install it via `git+https://github.com/...`, which this audit's pinned, reproducible-install standard does not do for a one-off. Also a live TradingView-login data source by design, the same class of blocker as `avellaneda`. |
| `cointanalysis` | 1 (`LitmusSimpleStrategy`) | listed as having existed on PyPI (libraries.io) but not currently resolvable by pip under any version - removed or yanked since. |
| `openai` | 1 (`KMM`) | installs cleanly; the row needs a paid, credentialed API account regardless, already declined for that reason. |
| `freqtrade.litmus` | 4 (`CopyLitmusMinMaxBroadClassificationStrategy` and 3 siblings) | not a PyPI package - the same custom subpackage inside `markdregan/...`'s forked freqtrade already diagnosed for `LitmusMetaStrategy` in Phase 6; reaching it would shadow the installed freqtrade. |
| `technical.tradingview` | 1 (`Enchilada`) | not a package, a submodule absent from the installed `technical` version and from `werkkrew/freqtrade-strategies` alike. |
| `freqtrade.freqai.strategy_bridge` | 1 (`Cenderawasih_freqai`) | not a package, absent from `hamidreza07/freqai-strategy` and everywhere else checked. |

`CME`/`HMMv3` still fail past their first `yfinance` layer on a second,
already-documented one (`tvDatafeed`, `hmmlearn` - the latter needs a C
compiler this image does not carry).

## 3. `dtype_drift`: one general, safety-proven rule, applied where it holds

New `repair/patch_class2.py` rule, `legacy_signal_int_literal`: a strategy
written before pandas enforced a column's declared dtype assigns the bare
`1`/`0` it always meant as a flag - `dataframe.loc[conditions, 'buy'] = 1`,
freqtrade's own pre-2021 idiom, or the same shape against a custom column
the file itself elsewhere sets to `True`/`False` (proving, on the AST, that
the author already meant it as a flag, not merely a name that looks like
one). `True`/`False` are the exact same value as `1`/`0` under Python's own
`bool <: int`, so which literal spells "flagged" cannot change a trading
decision either way. Handles both the single-column shape and
`.loc[cond, ['col', 'tag']] = (1, 'text')`, replacing only the tuple
position paired with a proven-bool column.

Applied against a purpose-built ledger of the 19 `dtype_drift` rows (not
the retired `old/predecessor_audit/LEDGER.csv` `patch_class2.py` defaults
to - a custom ledger is just the same three columns, `strategy,repo,file`,
pointed at `evidence/EXECUTION_PROFILES.csv`'s current canonical paths).
**18 of 19 patched, 9 confirmed measuring** after `execution_profiles.py`
picked up the new overlays: `BinClucMadDevelop` (77 trades),
`BinClucMadSMADevelop` (50), `CoreStrategy` (40), `CombinedBinHAndClucV6H`
(26), and five more already progressing past their dtype error into the
ordinary check chain. `DIV_v1` re-patched from its true original (not the
already-overlaid path, which would have nested `repair/patched/repair/
patched/...` had it been used directly as the ledger's `file` column - caught
and corrected before writing).

**Not one bug family despite the shared message - confirmed by what
remains.** Nine of the patched rows still fail, each on a genuinely
different dtype problem the same rule correctly does not touch: a
`np.where` mixing string and float branches (`MultiMA_TSL5` and others,
inside a `pmax()` function whose output IS read downstream, so the
existing `dead_np_where_dtype` rule's write-only precondition correctly
refuses it too - this needs its own proof, not attempted), a float value
into a declared-int column (`GPR`), a bool into a declared-float column
(`DIV_v1`, `new_turtle`, `new_turtle_roi` - the reverse direction from this
rule's own fix), an int into a declared-string tag column (`PnF`, a second,
different assignment from the one this rule already corrected in the same
file), and an outright dtype comparison rather than an assignment
(`MomentumRegimeBasket15m`, `int64` vs `datetime64`). Each would need its
own read and its own proof; none is guessed at here.

# Phase 9 — Stufe 2/3 batch, and a timeframe traced through a repaired import

Ran the warm-up ladder (`evidence.warmup_convergence --cohort ladder_pending`)
and the look-ahead gate (`evidence.profile_bias --diagnostics lookahead
--only ...`) over every row still carrying `recursive_ladder_pending` (64)
or `lookahead_remeasure_pending` (54). `eligibility_lookahead_backfill.py`
was checked first and ruled out for the look-ahead batch - its own docstring
scopes it to a frozen 361-row expansion-wave population, not the current
54-row set; `--diagnostics lookahead --only <name>` on `profile_bias.py`
reads the full `EXECUTION_PROFILES.csv` manifest instead of its narrower
default `candidates()` (itself scoped to the 7-row `REGIME_ELIGIBILITY.csv`,
also not this population), so it was the correct general tool.

Ladder: 30 of 64 rows had never run. 13 converged, 11
`crashes_even_at_longest_rungs` (no drift table at any rung - not a
finding, but an incomplete check counts as a failed one, by
`strategy_status.py`'s own long-standing rule), 3 `inconclusive`, 2
`no_usable_ladder`, 1 `not_converged_within_ladder` (`Kalman`, a
confirmed drift). Look-ahead: 54/54 measured, 13 PASS, 2 FOUND, 39 NA.

**`Hammer` and `KeltnerBounce`'s `no_usable_ladder` turned out to be a
gap in a repair, not a missing fact.** Both read `Config.timeframe`
(hamidreza07/freqai-strategy); neither ships a `Config.py` of its own -
confirmed against the origin GitHub repo directly (`gh api
repos/hamidreza07/freqai-strategy/contents/...`), not just the local
mirror, so this is not a harvest gap. `repair/local_modules.py` had
already resolved their `import Config` to `BuyDips/Config.py`, one of 18
byte-identical copies across the same batch folder (all 21 available
copies in `startegy test/5/` declare `timeframe = '5m'`, no exceptions).
The ladder's own candle-math step, `sibling_config_timeframe()`, only
reads a `Config*.py` in the strategy's *own* directory, so it never saw
this - the value existed, proven, one directory over.

Fixed generally rather than as a two-row patch: `repair/overrides.py`
gained `imported_module_timeframe(python_path, module)`, reading the
timeframe from the exact file `local_modules.py`'s import test already
proved a row loads. `repair/local_modules.py`'s `resolve()` now sets
`config_overrides={"timeframe": ...}` whenever the resolved copy states
one and the row has none of its own (checked against
`EXECUTION_PROFILES.csv` so a real declared value is never shadowed).
`evidence/REPAIR_LOCAL_MODULES.json` was added to `repair/overrides.py`'s
`REPAIR_STORES`, so every downstream runner picks the value up through
the one function that already reads all the others.

Regenerating `REPAIR_LOCAL_MODULES.json` from scratch would have dropped
`Hammer`/`KeltnerBounce` - the current `BLOCKED_TRIAGE.json` no longer
lists them under `local_module_off_path` (they no longer fail the trial
run) - so the fix was applied by re-calling the real `resolve()` on
their two existing records directly and merging the results back, not by
a fresh full `run()` and not by hand.

`evidence/warmup_convergence.py`'s `redo_defective()` extended to also
retire a `no_usable_ladder` / "no declared timeframe" record once a
repair store carries a timeframe for that row - a second, structurally
different defect shape from the `inconclusive`/`DEFECTIVE`-marker one it
already handled. Running it found not just the two rows this was built
for but four more already sitting on a stale `no_usable_ladder` despite
having a `MANUAL` timeframe override in `eligibility_timeframe_repair.py`
since earlier work: `EmaCrossStrategy`, `FixedRiskRewardLoss`,
`PolymarketMeanReversionStrategy`, `PolymarketMomentumStrategy`. All six
re-ran and converged.

Independent confirmation, from a pipeline stage that does not depend on
the new override at all: the look-ahead batch (already running against
the frozen 54-row list before this fix was written) reached `Hammer` and
`KeltnerBounce` afterward and passed both - freqtrade's own
`lookahead-analysis` loads the strategy for real and resolves
`Config.timeframe` live through the already-repaired import path, needing
no static value up front the way the ladder's pre-run candle math does.

After the merge (`evidence.strategy_status`): `Hammer`, `KeltnerBounce`,
and the four other freed rows moved to `convergence_candidate` - both
gates clear, queued for the paired full-window run. The 11
`crashes_even_at_longest_rungs` rows and `Kalman` moved to `excluded`, as
predicted from reading `strategy_status.py` before the merge ran.
`Anomaly`, `NNPredict`, `PCA` (`inconclusive`) and the un-fixed
`no_usable_ladder`/`inconclusive` states stayed open, also as predicted -
neither state forces exclusion on its own. Final: `E1_expanded` 661,
`excluded` 255, `exclusion_unconfirmed` 38, `pending` 33,
`too_few_trades` 30, `not_a_strategy` 19, `convergence_candidate` 14.

**All 14 `convergence_candidate` rows closed out the same day**, checked
against `eligibility_admit_converged.eligible()` directly. 7 (`AdaptiveRegime`,
`BBKCBounce`, `BinClucMadDevelop`, `BinClucMadSMADevelop`,
`CombinedBinHAndClucV6H`, `CoreStrategy`, `TrendFutures`) were already fully
eligible - `--apply` had simply never run since they converged. 5 (`Hammer`,
`KeltnerBounce`, `EmaCrossStrategy`, `PolymarketMeanReversionStrategy`,
`PolymarketMomentumStrategy`) were blocked on `coverage_status=PENDING`:
`evidence/EXECUTION_PROFILES.csv`'s own timeframe column was still empty for
`Hammer`/`KeltnerBounce` because `evidence/execution_profiles.py` (which
already reads `repair_overrides()`, unchanged by this session) had not been
re-run since `REPAIR_LOCAL_MODULES.json` joined `REPAIR_STORES`. Re-running
`execution_profiles` -> `regime_coverage` -> `strategy_status` ->
`eligibility_admit_converged --apply` cleared all 12 in one pass - no new
measurement, only propagation of evidence that already existed.

The remaining 2 (`DonchianBounce`, `TEMABounce`) were genuine `never trades`
holds - the 1-month smoke window found nothing, which is a real gap the
admission rule refuses to guess past. `evidence/profile_full_window.py
--strategy DonchianBounce --strategy TEMABounce` (paarweise sharded, the
same tool that resolved `MeanReversionTrend`/`TrendBreakout` earlier this
session) found trades on 7 of 8 pairs each over the full 6.5-year window -
the 1-month smoke was too short a window for either, not a true zero.
`E1_expanded` after both closes: 675, `convergence_candidate`: 0.

**The published page's "What excludes a strategy" legend had drifted to
three of nine criteria.** `evidence/exclusion_criteria.py`'s `CRITERIA` list
is the actual source of truth (it already gates `strategy_status.py`'s own
selftest), but `tools/STRATEGY_STATUS.template.html` had C1-C3 typed in by
hand and was never touched again after C4-C9 were added later - the
"generated with this page" note two paragraphs below it was true of the row
table, never of this legend. Fixed by making it generated for real:
`tools/strategy_status_page.py` now imports `evidence.exclusion_criteria`
directly and renders one card per `CRITERIA` entry (`id`, `name`, `what`,
backtick spans converted to `<code>`) into a new `__CRITERIA__` template
placeholder, with `__CRITERIA_COUNT__`/`__NOT_CRITERIA_COUNT__` replacing
the two hand-typed counts ("Three things...", "Five things...") the same
way `__TOTAL__` already replaced the row count for the same reason. The
selftest now asserts every `CRITERIA["id"]` appears in the rendered legend,
so a tenth criterion added later fails the build instead of going unnoticed
again.

**The published page's Trades column was reading the wrong full-window
number, and for most admitted rows no number at all.** `evidence/
strategy_status.py`'s `observed_trades`/`trade_evidence` only ever reads
`evidence/PROFILE_FULL_WINDOW.json` (`evidence/profile_full_window.py`, the
paired per-pair Stage-6 gate) - by PIPELINE.md's own explicit design,
`regime/full_backtest.py`'s pooled run (all eight pairs together, one shared
`max_open_trades` budget, `results/regime/full_backtest_manifest.json`) never
feeds it back, because a pooled result must not retroactively decide
admission. That boundary is correct for `STRATEGY_STATUS.csv` and left
untouched. But the page's Trades column was reading only the same starved
`full_window`/`smoke` pair the CSV carries, so 550 of 675 admitted rows
that already have a real, measured, six-and-a-half-year pooled trade count
on record showed a stale one-month trial-run number, or nothing at all -
not a gap in what had been measured, a gap in what the page looked at.

Fixed at the display layer only, not in `strategy_status.py`: `tools/
strategy_status_page.py` now reads `results/regime/full_backtest_manifest.json`
directly (`pooled_trades()`, `status == "measured"` only) and adds a `pft`
field per row where it exists. The template's `tradesCell()` now ranks three
tiers instead of two - pooled (`pft`, plain, the real portfolio number),
sharded (`full_window`, marked †, six-and-a-half years but eight independent
per-pair runs summed rather than one shared-budget run), trial run (`smoke`,
marked *) - so the three are never shown as the same claim. Sorting the
Trades column now uses the same `tradeValue()` the cell renders, so a sort
never disagrees with what is on screen.

**35 admitted rows turned out to have no trial run of their own at all.**
Reading the Trades column with the fix above still left 35 `E1_expanded`
rows blank - `BBRSI2`, `BinHV45` and 33 more, all `hamidreza07`-unrelated
classic spot strategies (BinHV45/Cluc-family, TEMA, SuperTrend...). Each
already carries a native, freshly-measured `lookahead`/`recursive` verdict,
so the strategy plainly loads and trades under this runtime - but none had
an entry in `evidence/PROFILE_SMOKE.json` at all, meaning `evidence/
profile_smoke.py` had simply never been run against them here. Not a display
gap this time: a real missing measurement, closed by actually running it
(`python -m evidence.profile_smoke --profiles spot_long --strategy ...`,
`--profiles` needed explicitly since the tool's own default is futures-only
and every one of these 35 is `spot_long` - the first attempt without it
failed outright with "not selected from manifest"). 34 of 35 measured
clean; `Hacklemore3` timed out at 300s and stays blank, genuinely unmeasured
rather than papered over.

**The 35-row fix was not the whole gap - 99 more rows carried the same
disconnect**, found because the reader added up the Trades stat card's own
"passed" and "excluded" numbers against "suitable for a smoke run" and the
sum came up ~130 short. Checked directly: 82 `excluded` rows (mostly C1/C2/
C9 - a native, working lookahead or recursion verdict, proving the strategy
loads and runs under those freqtrade subcommands) plus 10 `too_few_trades`,
5 `exclusion_unconfirmed`, and 2 `E1_expanded` rows had no
`evidence/PROFILE_SMOKE.json` entry of their own either. The 75 rows
excluded under C4/C5/C7/C8 (no repair possible at all) were deliberately
left out of the backfill target - re-running those would only reproduce
the same refusal.

`python -m evidence.profile_smoke --profiles spot_long futures_long_short
futures_long futures_short --strategy ...` against the 99: 78 measured
clean, 4 new genuine failures (`WTAI`/`WTRSIAI` on freqtrade's retired
`populate_any_indicators()`, `AstroQAV4` needing FreqAI enabled,
`BBRSIS` - see below), 17 skipped because they already carried an
unrelated, unchanged failure (`profile_smoke.py`'s own skip check, no
change needed there). Gap closed from 131 to 51: 32 genuinely `pending`
(`strategy_does_not_run`, correctly still open, not excluded), 19
`excluded` rows whose own trial run fails for a reason unrelated to why
they were excluded, and the 2 admitted stragglers below.

**`BBRSIS` turned out to be a second, unrelated bug, predating this
backfill.** It already had a working, 110-trade measurement - not in
`PROFILE_SMOKE.json` but in `evidence/ELIGIBILITY_TIMEFRAME_REPAIR.json`,
from the `ticker_interval`-recovery route. `strategy_status.py` only
trusts that store's record over a fresher `PROFILE_SMOKE.json` one when
their `class1_rules` match - and `PROFILE_CLASS1.json` later registered
`startup_candles_not_limited_by_call_budget` for this row (a ladder-only
candle-budget shim, irrelevant to whether the plain backtest runs), so the
rule-match check now fails and the old, working measurement is never
read. Not fixed here - genuinely a different bug from the one this
session closed, and narrow (found on one row so far) rather than
systemic. `Hacklemore3` is simpler: its file and config are unchanged
since its last 300-second timeout, so `profile_smoke.py` correctly
declined to reproduce it rather than guessing a longer timeout would help.

**`BBRSIS`, chased down: two real bugs, one of them far larger than the
row it was found on.**

First bug, general and now fixed: `evidence/profile_smoke.py`'s own plain
CLI never called `repair_overrides()` at all - only `regime/full_backtest.py`
and `eligibility_timeframe_repair.py`'s specialised runner did. `BBRSIS`
already had a working, 110-trade measurement filed under
`eligibility_timeframe_repair.py`'s recovered `ticker_interval` override; a
bare `python -m evidence.profile_smoke --strategy BBRSIS` re-failed the
identical row for want of the same value. Fixed by having `_run()` fetch
`repair_overrides()` once and pass it to `run_one()` - folded into the
skip-check's own identity comparison only when a strategy actually has an
override, so a row with none reads exactly as it did before this existed.

Re-running with the override applied surfaced the second, much bigger bug:
`BBRSIS` still failed, now on `NDFrame.fillna() got an unexpected keyword
argument 'method'` - a pandas-3 removed-keyword issue a `repair/patched/`
overlay already fixed (`dataframe.fillna(method='ffill')` -> `.ffill()`),
except `evidence/EXECUTION_PROFILES.csv` was not selecting that overlay as
canonical. Traced to `repair/patch_class2.py`'s report writer:
`patch_class2_report.json` - the only record `execution_profiles.py` reads
to know a patched overlay exists - was overwritten wholesale, not merged,
by whatever ledger the driver last ran against. Phase 8's custom
19-strategy `dtype_drift` ledger run had silently erased every OTHER
strategy's "patched" entry that a previous, full-corpus run had written -
58 strategies, `BBRSIS` among them, its overlay still sitting untouched on
disk with nothing left pointing at it.

Fixed at the source: `main()` now loads the existing report first and
carries forward, unchanged, every strategy the current ledger does not
itself touch - a partial ledger updates its own rows instead of erasing
everyone else's. Recovering the 58 already-lost entries needed one run
against the default ledger (`old/predecessor_audit/LEDGER.csv`) - which
immediately produced a THIRD problem: `legacy_signal_int_literal` (built in
Phase 8 for a 19-row `dtype_drift` population) matches any bare `0`/`1`
written into `buy`/`sell`/`enter_long`/etc., which is ordinary, correct,
extremely common freqtrade code - so the same rule, run against the full
896-row ledger instead of the 19-row custom one, "patched" 807 strategies
that had never been broken. The transform itself stays provably safe
either way (`bool <: int`), and `execution_profiles.py` only ever selects
an overlay when the original does NOT already work, so none of those 807
changed what any row actually runs on - but recording 807 strategies as
"repaired" when nothing about them needed it is exactly the kind of
scope a diff should never carry silently. Reverted precisely, not by
re-running anything a second time: every `patch_class2_report.json` entry
whose rule list was `["legacy_signal_int_literal"]` alone AND whose
strategy was not one of the original 19 had its overlay file and diff
deleted and its report entry dropped; the 76 entries that remain are
exactly the pre-incident 58 plus Phase 8's 18 - confirmed by the file
count matching before any of this began. `evidence/execution_profiles.py`
re-run afterward; `BBRSIS` now measures 110 trades again, matching the
record that had been sitting unreachable in `ELIGIBILITY_TIMEFRAME_REPAIR.json`
the whole time.

**The Trades stat cards, required to reconcile exactly, found two more
bugs on the way to actually doing it.** Asked to prove `passed + excluded +
a new third "other" tile` sums to the PRIOR stage's own `passed` count, at
every one of the four stages - not approximately, exactly. Two mismatches
surfaced immediately:

`MostOfAll` counted in both `smoke run passed` and `excluded - smoke run
failed` at once: it carries `trade_evidence: full_window` (it ran, and
produced a real trade count) AND `primary_reason:
shared_runtime_change_declined` (C8 - its own computed column is silently
lost to pandas copy-on-write, a corpus-wide fix declined as too invasive).
Both are true; only one is about whether the trial run itself produced
evidence. Fixed by making "excluded" explicitly exclude rows that also
satisfy "passed" - a row that ran keeps counting as having run, whatever
it is excluded for.

`NowoIchimoku5mV2`, `ObeliskIM_v1_1` and `simple_patterns` are admitted
(`E1_expanded`) rows that the recursion-bias check could not explain: PASS,
but `recursive_evidence: "native"`, not the `convergence:...` string the
funnel's own check required. Traced to `evidence/strategy_status.py`'s
`NATIVE_LOOKAHEAD_EVIDENCE = ("native", "reviewed_indicator_only")` having
a look-ahead-only counterpart that recursion never got: the ladder's own
`convergence:` evidence is one native measurement, `profile_bias.py`'s
single-shot recursive diagnostic (no ladder needed when the strategy's own
declared warm-up already settles it) is another, equally native one this
funnel's check had never recognised. Widened to accept either, mirroring
the same two-source native-evidence pattern the look-ahead stage already
had - confirmed correct against a fact this could check itself: with the
fix, "look-ahead-bias passed" computes to exactly 675, admission's own
E1_expanded count, matching a criterion this page never touches.

All four stages now sum exactly, checked directly rather than eyeballed:
1050 downloaded -> 1031 suitable -> 905/74/52 (smoke) -> 757/78/70
(recursion) -> 675/26/56 (look-ahead) -> 583/57/35 (full-backtest).

**The Timeframe column's real bug: `evidence/strategy_status.py` was reading
the wrong file.** 31 of 675 admitted rows showed `NA` for Timeframe despite
carrying a native `lookahead`/`recursive` verdict - and a settled ladder
(`convergence:288`, `convergence:576`...) is only possible if a real,
specific timeframe was fed into the candle math, so an admitted row with no
displayed timeframe was never a coherent state. Traced to
`STRATEGY_STATUS.csv`'s `timeframe` column reading exclusively from
`evidence/STRATEGY_CLASSIFICATION.json`'s own `timeframe` field (line 1535),
an older, narrower pass that never learned about
`sibling_config_timeframe()` or `repair_overrides()` - both added to
`evidence/execution_profiles.py`'s own `execution_timeframe` derivation this
session and last. Checked directly: `EXECUTION_PROFILES.csv` already had the
correct value (`source: author_sibling_config`) for every one of these rows;
`STRATEGY_STATUS.csv` was simply never told to look there.

Confirmed the scale before touching anything: 54 rows had a value in
`EXECUTION_PROFILES.csv` and nothing in `STRATEGY_CLASSIFICATION.json`; 3
had a value in both that disagreed. Read the disagreements rather than
guessing a precedence: `QuickBuyStrategy` (`1h` vs `1hr`) and `ScalpingCCI`
(`15m` vs `15`) are the same value, one normalized and one not -
`execution_profiles.py`'s is. `FisherBBDynamic` disagreed for real (`5m` vs
`15m`) - its source file line 122 is `# timeframe = '15m'`, commented out,
directly above the live line 123 `timeframe = '5m'`; the older classification
pass evidently read the comment. `execution_profiles.py`'s value is correct
in all three.

Fixed by preferring `profile.get("execution_timeframe")` over
`classification`'s own field, falling back to classification only for the 2
rows where it alone carries a value (`evidence/strategy_status.py`, the
`timeframe` field of the row dict). Not a `STRATEGY_CLASSIFICATION.json`
regeneration - that file's own pass is simply superseded here, the same way
an inherited baseline is superseded by a native measurement elsewhere in
this table. Cohorts are unaffected (this column is display-only, not read
by any admission or exclusion criterion); rows with a blank Timeframe
dropped from 88 to 34, and all 34 remaining are genuinely undetermined -
mostly C4 (`repair_refused_would_invent_strategy`) rows already excluded
for exactly that reason.
