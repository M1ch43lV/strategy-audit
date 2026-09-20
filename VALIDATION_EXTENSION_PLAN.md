# Plan: extend the validation window to 2026-09-19

**On hold (owner decision 2026-09-20): the extension will be carried out at a later date. Nothing is to be started until
the owner asks for it.** The plan stays valid as written; before starting, re-check the window end and the data.

Status: plan only (version 3, 2026-09-20), nothing below has been run except the one-strategy
probe in section 2. Version 2 added the owner's decisions of 2026-09-20 (5m robustness and the
Freqtrade-native figures are extended too) and the two-tier design that follows from them. Version 3
incorporates the review by DeepSeek (deepseek-v4-pro), see section 10.

## 1. Decisions taken by the owner

- The validation window is **extended**; the new days become part of it. There is **no third window**.
- The end is **2026-09-19, the whole day included**: `2026-09-20 00:00 UTC` exclusive, the same convention as
  the old end `2026-08-21` (exclusive).
- The discovery window (trades opened before 2024-01-01) is **not recomputed**. Discovery numbers must stay
  identical (acceptance test 5.1).
- **Model 1/2/3 stay as snapshots** of the old window (they pin the SHA-256 of the old `regime_daily.csv`).
- The **5m robustness run is extended** over the new window (stage 8b), and so are the **Freqtrade-native
  figures** of the page.

Consequence to write down: the untouched-data test of the confirmation rule proposed in Amendment 2026-09-20
("forward hold-out from 2026-08-21") **falls away**, because those days are now validation days. The rule stays a
post-hoc reporting rule.

## 2. Facts from the code and from the probe

| Item | Where | Effect |
|---|---|---|
| Window end, regime data | `regime/regime_engine.py` `END` | must move; regenerates `regime_daily.csv`, episodes, transitions, state summary, distributions, manifest |
| Window end, attribution | `regime/attribution.py` `END` | trades with `open_date >= END` are dropped; must move |
| Canonical baseline window | `evidence/profile_full_window.py` `TIMERANGE` (`20200301`/`20200401` to `20260821`) | **not changed** (see 4.3) |
| Validation start | `specialist_evaluation.VALIDATION_START` = 2024-01-01 | unchanged; no validation end constant exists |
| Benchmark candles | `specialist_evaluation._candle_path`: spot `<PAIR>-1m.feather` | 1m candles must be extended |
| Pins on the regime data | `gated_backtest.py`, `gated_attribution.py`, `model_compare.py`: `regime_daily_sha256` | Model 1/2/3 become stale by hash; kept as snapshots, verifiable with the archived old file via `--daily` |
| Trade readers | `attribution.main` (archive from the pooled manifest), `execution_robustness.build` | both need to read the extension |
| 5m classifier | `execution_robustness.metrics/compare/classify` | thresholds act on the **native compounded** figures of two full-window runs (profit sign, profit change, trade count) |
| Native report table | page: `regime_specialists_page.native_stats` via `model_compare._load_model0(manifest, ids, timerange)` | native report block of a run over the whole window |
| Data | `user_data/data/binance/` (git-ignored). Spot: 8 pairs x 12 timeframes, all ending 2026-08-20 (XMR 2024-02-20, delisted). Futures: 8 pairs x 1m/3m/5m/15m/1h/4h/1d, 1h mark, 1h funding rate, ends not uniform (08-20, 08-26, 09-10, 09-18) | must be extended and normalised |

Probe on one strategy (`simple_vwap_v1`, 4h, spot, scratch directory, repo untouched):

- `freqtrade download-data` appends missing candles: 16 files in 5 s.
- A backtest that starts **60 days before** the old end reproduces the continuous run's trades in the new period
  exactly (17 of 17: pair, opening, closing, rate). Profit ratio differs by up to 2e-5 (stake rounding under
  `stake_amount: unlimited`). With 0, 7, 14, 30 days of run-in, 5, 3, 3, 2 of 17 trades differed; the strategy holds up
  to 28 days.
- Old trades without the window-end `force_exit` trades, plus run-in trades closing on or after the old end, equal the
  continuous run's trade set (3 `force_exit` trades replaced by their continuation).
- 4 to 5 s per run-in run, 21 s for the continuous run.

**What a run-in cannot give:** the native report block and the compounded figures. Profit total, CAGR, Sharpe,
Sortino, Calmar, drawdown and market change come from the equity curve of one continuous run with compounding stake;
they cannot be stitched from two runs. The 5m classifier acts on the same compounded figures. Both therefore need
**continuous full-window runs** over the extended window.

Not tested: futures, 1m, DCA strategies, strategies holding for months, Docker-runtime baselines (168 of 632 were
measured in Docker, 473 native, 91 without a runtime id).

## 3. Design: two tiers

**Tier A, all 632 strategies with a measured baseline: run-in extension.** A second, short backtest over
`[old end - run-in, new end)`. Its archive is registered in a new store
`results/regime/full_backtest_extension_manifest.json`. The trades for the extended window are
`stitch(old, extension)`: old trades that are not `force_exit`, plus extension trades with `close_date >= old end`.
Run-in: the largest of 120 days, twice the longest holding time in the strategy's own old trades, and the strategy's
**settled warm-up plus 30 days** (`settled_days` from the warm-up ladder, up to 365 days). The last term matters: freqtrade
loads only the *declared* `startup_candle_count` before the start of a timerange, and a number of strategies declare none (125 when last counted), so their
indicators start cold at the run-in start. The settled warm-up is the project's own measure of how long an indicator needs.

**Per-strategy convergence check against the old archive**, all of it mandatory:
1. the trades of the run-in run opened in the second half of the overlap equal the old archive's trades of the same range,
   comparing pair, open and close timestamp, open rate, close rate, exit reason and profit ratio (tolerance 1e-4, the stake
   rounding seen in the probe was 2e-5);
2. **the positions open at the old end match**: every old `force_exit` trade must reappear in the run-in run with the same pair,
   open timestamp and open rate and a close on or after the old end. This is the check that matters most, because those are the
   only trades whose fate the state at the old end decides;
3. the number of trades opened per pair in the second half is equal.
On failure the run-in doubles once, then the strategy falls back to Tier B. The first half of the overlap is not compared and
does not need to be: the stitch takes every old trade from the old archive, which is the continuous run by determinism, and
uses the run-in run only for trades that close on or after the old end.
Purpose: validation trades, attribution, cost screen. About one hour, more if run-ins double.

**Tier B, the strategies that need compounded or native figures: continuous full-window reruns over the extended
window.** Set: the 404 universal candidates (native table) united with the 224 strategies with a 5m detail run
(classifier): **466 strategies**. Per strategy: a baseline run over `20200301|0401-20260920`, and for the 224 also the
5m detail run over the same window. Output to new, non-canonical manifests (runner option `--window-end`, allowed only
with a non-canonical `--output`, like `--timeframe-detail`). Recorded elapsed times of the old runs: baseline 45.1 h,
detail 26.4 h, **71.5 h serial**; at the 3.4x speed-up seen with four containers about **21 h wall** as an upper bound
(the probe ran 3x faster than the recorded 62 s, so the real time may be well below). Two baselines and one detail run
already took more than 3000 s; the 3600 s ceiling stays hard, so a few new `ERROR`/timeout results are expected and
are reported, not hidden.

Where both tiers exist for a strategy, the Tier B trades are used, and Tier A serves as an independent acceptance test
of the stitch (5.2).

**Not chosen: a fixed-stake redefinition of the classifier** (mean profit ratio of stitched trades instead of the
compounded profit). It would avoid the detail full reruns but changes a frozen classification; the owner asked for the
existing check to be carried forward.

## 4. Work packages, in this order

### 4.0 Before anything is run
1. Amendment in `REGIME_PREREGISTRATION.md`: new analysis and validation end (2026-09-20 exclusive), "Scope and causal
   clock" updated, the forward hold-out clause of Amendment 2026-09-20 withdrawn by owner decision, the confirmation rule
   unchanged and post-hoc, Model 1/2/3 declared snapshots of the old window, and the sources of the extended figures
   (Tier A, Tier B) named.
2. State is committed (rollback point). `RUNTIME_ENVIRONMENTS.md` is Codex's and stays untouched.
3. **Pilot before the batch.** At least one strategy from each class the probe did not cover: futures, 1m, DCA, one that holds
   for months (1d), one with no declared `startup_candle_count`, one whose baseline ran in Docker. For each, run Tier A and one
   continuous full-window run over the extended window (in scratch), and compare the trade sets. The batch starts only if the
   pilot converges, or the rule (run-in length, fallback) is changed until it does.

### 4.1 Data
- Extend spot (8 pairs, XMR only if candles exist; all 12 timeframes; `ETH/BTC` 1h) and futures (the same pairs, the seven
  timeframes, mark, funding rate) with `freqtrade download-data` in the real data directory.
- Acceptance: all files end consistently, no gaps between old end and new end, the old range of every file unchanged
  (hash of the old range before and after), 1m and 5m included.

### 4.2 Regime classification (pipeline stage 9)
- Move `END` in `regime_engine.py` and `attribution.py`; keep one definition if that changes no behaviour. Rerun the engine.
- Acceptance: **every** row of `regime_daily.csv` before the old end (states, ADX, features, episode ids) equals the old file.
  What may change: the episode table rows of episodes that were still open at the old end (their end date and length grow), and
  with it the buy-and-hold benchmark of those episodes, hence the excess return of the trades inside them. That is the effect of
  the extension, not an error; list those episodes and the trades and rows they touch. The six-phase thresholds are frozen
  numbers.
- Copy the old `regime_daily.csv` under an archive name for the Model 1/2/3 snapshot (`--daily`).

### 4.3 Extension runners
- New module `regime/window_extension.py` (Tier A) and a `--window-end` option in `regime/full_backtest.py` (Tier B),
  both modelled on the existing runner: same eligibility (`E1_expanded` with a measured baseline), repair overrides,
  data-file staging, config and, where it matters, runtime.
- Do **not** change `profile_full_window.TIMERANGE`: its identity check covers source and config hash only, not the
  window, so a change would make the runner treat all old results as current for a window they were not measured on.
- The extended results live in separate manifests. `choose_detail_records` currently picks any
  `execution_robustness_detail_*.json` record per strategy by status and time; it must select by window, or extended and
  old records would be mixed.
- Runtime: every run uses the runtime id of the strategy's old baseline (168 Docker, 473 native, 91 without an id, treated as
  native), for Tier A as for Tier B. If the convergence check fails for a Docker baseline that was run natively, repeat that run in
  Docker before doubling the run-in. The check therefore doubles as a detector of runtime differences.
- Workers: Tier A 4 in parallel. Tier B detail runs in Docker with `runtime/detail_batch_parallel.py` (4 containers, 3.5 GB each,
  solo repeat for OOM and timeouts) extended by the window option; Tier B baselines native or Docker as above. Never run two
  big batches at once.
- The 3600 s ceiling is not raised for anyone. Runs whose recorded time was above 3000 s (two baselines, one detail run) go first
  and alone, so that their outcome is known early; a timeout keeps the old-window figure, labelled.

### 4.4 Readers
- `regime/attribution.py`: trades per strategy come from the Tier B extended archive where it exists, else from the
  stitch of Tier A. The provenance goes into a new column `trade_source` (`canonical`, `stitched`, `extended_full`).
  Stitched trades come from two stake histories, so **no consumer may sum `profit_abs` across stitched trades and call it a
  result**: the evaluation uses `profit_ratio` with the fixed 1000 USD convention and is not affected; the descriptive
  attribution summaries (`strategy_*_summary.csv`) sum `profit_abs`, so they carry the source and are labelled. A flag switches
  the extension off.
- `evidence/execution_robustness.py`: classification on the extended baseline against the extended detail run (same
  thresholds, no change to the rule); cost screen (whole and per ADX state) on the extended trades. Strategies without an
  extended pair stay `PENDING` for the extended window and are listed; the status table names the window of every value.
- Native table on the page: `model_compare._load_model0` already takes a manifest path and a timerange; point it at the
  extended manifest.
- The 166 strategies outside Tier B are neither in the native table (it lists the universal candidates) nor classified by 8b
  (no 5m detail run; strategies at or below 5m pass by rule). Their native figures are used nowhere; they need Tier A only. The
  status table's trade counts (`pft`) stay those of the canonical window and are labelled so.
- `specialist_evaluation.py`, `discovery_comparison.py`: unchanged.
- Page tools and templates: hard-coded dates become tokens (two `2026-08` mentions in the specialists template, four
  `2026082x` in the status template); Model 1/2/3 blocks labelled as snapshots until 2026-08-20.

### 4.5 Order of execution, and what is shown when
1. Data, regime data, Tier A (about two hours in total). Then attribution, evaluation, comparison and pages show the
   extended validation window; the native table and the 5m column still show the old window, **labelled as such**.
2. Tier B in the background (about a day of wall time at worst). When its batches finish, the native table, the 5m
   classification and the cost screen switch to the extended window; both pages are rebuilt.
The owner accepts the interim state only if it is labelled; otherwise nothing is published until Tier B is complete.

## 5. Acceptance tests
1. **Discovery invariance:** discovery columns of `discovery_vs_validation.csv` identical before and after.
2. **Stitch check:** for every strategy in both tiers, Tier A stitched trades equal the Tier B trades (pair, open, close,
   rate); ratios within 1e-4.
3. Trade counts before the old end equal the old counts minus the replaced `force_exit` trades.
3b. The evaluation's benchmark for validation trades opened in the new period is present for every matched trade (1m candles
    reach the new end).
4. Regime data: prefix identical (4.2). Data: 4.1.
5. Selftests of `regime.attribution`, `regime.specialist_evaluation`, `evidence.execution_robustness` pass.
6. Extension manifest: one entry per baseline strategy, each with status, run-in, convergence result, tier and runtime;
   no unexplained status.
7. Report how many strategies changed tier, rank, robustness status or confirmation label.

## 6. Documents, pages, git
- `PIPELINE.md` (stages 8, 8b, 9, 10, 13), `HANDOFF.md`, `EXECUTION_ROBUSTNESS_PLAN.md`, the window table in the status
  page and in `strategy_status.py`; both pages rebuilt and republished with a fresh timestamp.
- `results/regime/trade_regime_attribution.csv` grows by about 1 to 2 percent; each commit of it uploads a new LFS object of
  about 1.4 GB. Decide when to commit it. Extension archives live under `user_data/profile_smoke/` (git-ignored).
- New result stores (extended baseline, extended detail, extension manifest) are inputs and are committed like the old ones.

## 7. Risks and open points
1. Convergence of Tier A is proven on one simple strategy; the pilot (4.0) and the per-strategy check with the Tier B fallback are
   the safeguards.
1b. The extension adds about 30 days to a validation window of about 2.7 years. Few new episodes per phase are expected (about 3
    coin episodes for bull and bear across all coins in that time), so most rows will move little; the purpose is completeness,
    not power.
2. Under `stake_amount: unlimited` stakes differ between run-in and continuous run; ratios differ by about 1e-5. Any figure
   that sums `profit_abs` of stitched trades mixes two stake histories; check where `profit_abs` is used (attribution
   summaries do). Tier B trades are continuous and free of this.
3. XMR has no candles after 2024-02-20; run-in runs have seven pairs and freqtrade reduces `max_open_trades` from 8 to 7.
   No effect in the probe; the checks would show it.
4. Tier B may push a few long strategies over the 3600 s ceiling; they are reported as `ERROR`/timeout for the extended
   window and keep their old-window figures, labelled.
5. Docker runtime: 168 baselines were measured there. Cross-runtime comparisons stay flagged as before.
6. All published numbers of the ranking, tiers, robustness, confirmation and universal lists may change; old figures stay in
   git history.

## 8. Time estimate
| Step | Estimate |
|---|---|
| Amendment | 20 minutes |
| Data | minutes |
| Regime rerun and prefix check | not measured, expected minutes |
| `window_extension.py`, `--window-end`, reader changes, detail-store selection by window | 3 to 4 hours of work |
| Tier A, 632 strategies | 1 to 3 hours serial, under one hour with 4 workers |
| Attribution, evaluation, comparison, pages (interim publication) | about 15 minutes |
| Tier B, 466 baselines and 224 detail runs | 71.5 h serial by recorded times, at worst about 21 h wall |
| Final rebuild after Tier B | about 15 minutes |

## 9. Rollback
All changes are additive: new manifests and archives, two `END` constants, one flag each in attribution and the runner,
regenerated outputs. To go back: restore the two constants, delete the extended manifests, regenerate from the committed state.
The old `regime_daily.csv` and every old archive are kept.

## 10. Review by DeepSeek (deepseek-v4-pro), and what was done with it

The plan (version 2) was submitted with the request to find what is overlooked. Ten objections came back. Assessment:

| Objection | Verdict | Action |
|---|---|---|
| Validation is no longer independent; the confirmation rule is post-hoc; suggests keeping a hold-out or calling the new days a sensitivity analysis | Correct as a statement, and already recorded in section 1. The owner decided against a third window. | Kept. The amendment and both pages say that the validation window was extended after its results were known and that the rule is post-hoc. The suggestion of a hold-out contradicts the owner's decision and is not followed. |
| Convergence check covers only the second half of the overlap | Partly wrong: the first half is not used by the stitch (old trades come from the old archive, which is the continuous run). The risk is the state at the old end. | Check extended to the positions open at the old end (point 2 in section 3). |
| Only open rate compared, not close rate, exit reason, profit | Correct | Added to the check. |
| Run-in ignores indicator lookback | Correct in substance and sharper than stated: many strategies declare no `startup_candle_count`, so their indicators start cold. | Run-in includes the settled warm-up plus 30 days (section 3). |
| Episode assignment of the last open episode may change | Correct that the benchmark of open episodes changes; wrong that ids or states change (the classification is causal). | Acceptance test made exact (4.2); the changed episodes are listed. |
| 166 strategies outside Tier B keep old native figures | Not a gap: those figures are used nowhere. | Stated explicitly (4.4). |
| Docker and native mix | Correct | Runtime per strategy fixed to the old baseline's; the check detects differences (4.3). |
| Tier B timeouts; suggests a longer timeout | The risk is correct. A longer timeout is excluded by the standing rule that 3600 s is a hard ceiling. | Slow runs go first and alone, outcome labelled (4.3). |
| Benchmark from 1m candles not updated explicitly | Covered by 4.1, made an explicit acceptance test | Test 3b added. |
| Only one strategy tested | Correct | Pilot over the missing classes before the batch (4.0). |
