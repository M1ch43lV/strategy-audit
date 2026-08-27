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
| Boundary | The original sweep restricted lookup to the strategy's own repository. The later profile audit separately records copied strategies whose missing helper is restored from another corpus repository only when the dependency relationship is explicit; those exceptions appear in `PROFILE_CLASS1.json`. |
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
direction, axis/limit arguments, assignment, and `inplace` behavior. The rule
does not infer replacements for other removed APIs.

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

`PROFILE_CLASS1.json` records the additional environment/configuration
restorations discovered by the native futures-profile smoke runs.
`PROFILE_REPAIRS.json`, generated by `profile_repairs.py`, records 25 additional
Class 2 overlays: 22 `strict_equivalent` and three `output_equivalent`.
Originals remain untouched. The rules cover NumPy string/NaN coercion, explicit
writable buffers for current pandas/PyWavelets, current futures settlement-pair
syntax, signal-column dtype initialization, and one neutral parameter-space
declaration.

All 101 native futures candidates were attempted with `profile_smoke.py`: 84
measured and 17 failed with explicit reasons. The remaining failures are not
silently “repaired”: incomplete author configurations, unavailable historical
model/dependency stacks, and the credential-bearing `KMM` source remain blocked
or partial. `HurstCycleV4` succeeded in a longer control window and therefore
was correctly classified as a smoke-window limitation rather than repaired.
