# Plan: extend the validation window to 2026-09-19

Status: plan only, nothing below has been run. Written 2026-09-20.

## 1. Decisions already taken by the owner

- The validation window is **extended**, from 2026-08-21 to today. The new days become part
  of the validation window. There is **no third window** (no "forward" or "tail" window).
- The discovery window (trades opened before 2024-01-01) is **not recomputed**. No complete
  evaluation run of both windows is wanted; only the validation results are updated.
- The extension is done by backtesting the new days, not by rerunning every strategy from 2020.

Proposed end date: **2026-09-20 00:00 UTC exclusive**, so that 2026-09-19 is a complete day.
Candles exist up to today. (The old end, `2026-08-21`, is exclusive in the same way.)

Consequence to write down: the untouched-data test of the confirmation rule proposed in
Amendment 2026-09-20 ("forward hold-out from 2026-08-21") **falls away**, because those days are
now validation days. The rule stays a post-hoc reporting rule, and its predictive value is no
longer testable on data that has not been seen.

## 2. What was found in the code (facts, not proposals)

| Item | Where | Effect |
|---|---|---|
| Window end for the regime data | `regime/regime_engine.py` `END` | must move; regenerates `regime_daily.csv`, `regime_episodes.csv`, `regime_btc_episodes.csv`, `regime_transitions.csv`, `regime_state_summary.csv`, `regime_feature_distributions.csv`, `regime_manifest.json` |
| Window end for trade attribution | `regime/attribution.py` `END` | trades with `open_date >= END` are dropped; must move |
| Canonical baseline window | `evidence/profile_full_window.py` `TIMERANGE` (`20200301`/`20200401` to `20260821`) | **must not be changed** (see 4.3) |
| Validation start | `regime/specialist_evaluation.py` `VALIDATION_START` = 2024-01-01 | unchanged; there is no validation end constant, so the window grows with the trades |
| Benchmark candles | `specialist_evaluation._candle_path`: spot `<PAIR>-1m.feather` | 1m candles must be extended too |
| Pins on the regime data | `gated_backtest.py`, `gated_attribution.py`, `model_compare.py` carry `regime_daily_sha256` | a new `regime_daily.csv` makes every Model 1/2/3 manifest stale by hash (see 4.2) |
| Archive per strategy | pooled manifest `results/regime/full_backtest_manifest.json`, read by `attribution.main` and `execution_robustness.build` | both must learn to read an extension |
| Data | `user_data/data/binance/` is git-ignored; spot: 8 pairs x 12 timeframes, all ending 2026-08-20 (XMR 2024-02-20, delisted); futures: 8 pairs x 1m/3m/5m/15m/1h/4h/1d, plus 1h mark and 1h funding rate, ends not uniform (some 08-20, 08-26, 09-10, 09-18) | see 4.1 |

Tested on one strategy (`simple_vwap_v1`, 4h, spot, scratch directory, nothing in the repo touched):

- `freqtrade download-data` appends missing candles; 8 pairs x 2 timeframes took 5 s.
- A backtest that starts **60 days before** the old end reproduces the continuous run's trades
  in the new period exactly (17 of 17, same pair, opening, closing, rate). The profit ratio
  differs by up to 2e-5, from stake rounding under `stake_amount: unlimited`. With 0, 7, 14 and 30
  days of run-in, trades differed (5, 3, 3 and 2 of 17), because the strategy holds positions up
  to 28 days.
- Old trades without the `force_exit` trades of the window end, plus the run-in trades that
  close on or after the old end, equal the continuous run's trade set. The old window's 3
  end-of-window `force_exit` trades are replaced by their continued versions.
- Runtime: 4 to 5 s per run-in run, 21 s for the continuous run.

Not tested: futures strategies, 1m strategies, DCA strategies, strategies that hold for months,
Docker-runtime baselines (168 of 632 were measured in Docker, 473 native, 91 without a runtime id).

## 3. Design

**Extension archives, stitched at read time.** For every strategy with a measured baseline a
second, small backtest is run over `[old end - run-in, new end)`. Its archive is registered in a new
store, `results/regime/full_backtest_extension_manifest.json`. The canonical baseline archive and
manifest are not modified. Whoever needs the trades of the extended window calls one function,
`stitch(old_trades, extension_trades)`:

- keep old trades whose `exit_reason` is not `force_exit`;
- add extension trades with `close_date >= old end`;
- nothing else, so no trade is counted twice and the old `force_exit` trades at the window end
  are replaced.

**Run-in length per strategy:** at least 120 days, and at least twice the longest holding time in the
strategy's own old trades, capped at the window length.

**Convergence check per strategy (no full rerun needed):** the extension run overlaps the old window.
Its trades opened in the second half of the overlap must equal the old archive's trades of the same
range (key: pair, open and close timestamp, open rate). If they do, the run-in state has converged and
the stitched set equals a continuous run. If not, the run-in is doubled once; if it still does not
match, the strategy falls back to a full rerun of the extended window (expected to be few), or is
reported as `not_extended` and listed. A mixed validation end across strategies is not acceptable.

## 4. Work packages, in this order

### 4.0 Before anything is run
1. Amendment in `REGIME_PREREGISTRATION.md`: new analysis window end and validation end
   (2026-09-20 exclusive); "Scope and causal clock" updated; Amendment 2026-09-20's forward hold-out
   clause withdrawn by owner decision; the confirmation rule stays as defined and stays post-hoc.
2. Commit the current state as the rollback point (all work so far is committed; `RUNTIME_ENVIRONMENTS.md`
   is Codex's and stays untouched).

### 4.1 Data
- Extend spot: 8 pairs (XMR only if candles exist; none since 2024-02-20) x all 12 timeframes,
  plus `ETH/BTC` 1h; futures: the same pairs, the seven futures timeframes, mark and funding rate.
- Use `freqtrade download-data` in the real data directory (it appends).
- Acceptance: every file ends on the same day (2026-09-19 23:xx or the timeframe's last candle),
  no gaps between the old end and the new end, the old part of every file is byte-identical in
  content (compare the first rows and a hash of the old range before and after).
- The futures files currently end on different dates. The old runs used them up to 2026-08-20; extra
  candles after that date change nothing for the old window.

### 4.2 Regime classification (pipeline stage 9)
- Move `END` in `regime/regime_engine.py` and `regime/attribution.py` to the same value; keep one
  definition if it can be shared without changing behaviour.
- Rerun `regime_engine`. Acceptance: all rows before the old end equal the old `regime_daily.csv`
  (features are causal with a one-day availability lag); episode ids before the last open episode of
  each pair are unchanged; the last open episode per pair may grow; the six-phase thresholds are frozen
  numbers and stay.
- Keep the old `regime_daily.csv` (git history has it; also copy it under an archive name).
  The gated runs (Model 1/2/3) pin its SHA-256. They are **not** extended (they would need gated backtests
  again): they remain snapshots of the old window and stay verifiable when the archived file is passed
  with `--daily`. Their page blocks and the top-10 selection are labelled as snapshots (they already
  are). `model_compare` of Model 0 against Model 1/2/3 is not rerun.

### 4.3 Extension backtests (new module `regime/window_extension.py`)
- Runner modelled on `regime/full_backtest.py`: same eligibility (`E1_expanded` with a measured baseline),
  same repair overrides and data-file staging, same config, same runtime as the baseline where that matters.
- Do **not** change `profile_full_window.TIMERANGE`. Its identity check covers only the source hash and the
  config hash, not the window; changing it would make the runner treat all 632 old results as current for
  a window they were not measured on.
- Workers: 4 native in parallel (memory: peak per run has been below 4.7 GB); timeout 3600 s stays the
  hard ceiling. Strategies whose baseline ran in Docker are first run natively; if the convergence check
  fails for them, repeat in Docker (the wrapper needs a module argument).
- Outputs per strategy: archive path and hash, run-in used, convergence result, number of stitched trades,
  number of replaced `force_exit` trades, runtime id.
- Acceptance: for every strategy `converged` or an explicit fallback; count of trades before the old end
  equals the old count minus the replaced `force_exit` trades; the extension run's own trades never
  include a trade the old archive has with a different close.

### 4.4 Readers of the trades
- `regime/attribution.py`: after `archive_inventory`, replace each record's trades by the stitched list;
  add a flag to disable it. Trades are then attributed with the extended `regime_daily.csv`.
- `evidence/execution_robustness.py`: the cost screen (whole run and per ADX state) reads stitched trades.
  The 5m-detail classification compares the baseline with the 5m detail run over the **old** window and
  stays as it is; it is documented as measured on 2020 to 2026-08-20. No 5m reruns for the extension.
- `regime/model_compare._load_model0` (native report block, used for the page's Freqtrade-native table):
  stays on the old window; the table is labelled "until 2026-08-20". Native report numbers cannot be
  stitched.
- `regime/specialist_evaluation.py`: no change. `regime/discovery_comparison.py`: no change.
- `tools/regime_specialists_page.py`, `tools/regime_specialists_data/`: dates in the templates become
  tokens (two mentions of `2026-08` in the specialists template, four of `2026082x` in the status
  template).

### 4.5 Re-evaluation and acceptance tests
Order: attribution, specialist evaluation, discovery comparison, robustness stores, status table,
both pages.
- **Discovery invariance:** the discovery columns of `discovery_vs_validation.csv` must be identical
  before and after (same trades, same episodes before 2024-01-01). Any difference is a bug, not a result.
- **Validation growth:** trade counts per strategy in validation grow by the number of new trades; no
  strategy loses validation trades except the replaced `force_exit` ones.
- The selftests of `regime.attribution`, `regime.specialist_evaluation` and `evidence.execution_robustness`
  pass; the extension manifest passes a consistency check (one entry per baseline, no unexplained status).
- Rankings, tiers, the robustness list, the confirmation list and the universal candidates are recomputed and
  may change; report how many rows changed tier or rank.

### 4.6 Documents and pages
- `PIPELINE.md`: window definitions in stages 8, 9, 10, 13; a short note that the canonical baseline window
  is unchanged and the extension is a separate store.
- `HANDOFF.md`, `EXECUTION_ROBUSTNESS_PLAN.md` (window of the 5m detail runs), the window table in the status
  page and in `strategy_status.py`.
- Both pages rebuilt and republished with a fresh timestamp (standing rule). The specialists page: the
  discovery/validation text says validation runs to 2026-09-19; the Model 1/2/3 sections say "snapshot until
  2026-08-20".

### 4.7 Git and storage
- `results/regime/trade_regime_attribution.csv` grows by about 1 to 2 percent; committing it uploads a new
  LFS object of about 1.4 GB again. Decide whether to commit the trade file with every regeneration.
- The extension archives live under `user_data/profile_smoke/` (git-ignored, like the baseline archives).

## 5. Time estimate

| Step | Estimate |
|---|---|
| Amendment | 20 minutes |
| Data download | minutes (5 s for 16 files in the test) |
| Regime engine rerun and prefix check | not measured, expected minutes |
| `window_extension.py` and the reader changes | 2 to 3 hours of work |
| Extension backtests, 632 strategies | 4 to 5 s each in the test, so 1 to 3 hours serial and under one hour with 4 workers; more for slow or long-holding strategies and the fallbacks |
| Attribution, evaluation, comparison, robustness, pages | about 15 minutes |

Realistic: one afternoon, most of it my development time; compute is about an hour.

## 6. Risks and open points

1. Convergence is proven on one simple strategy. The per-strategy check is the safeguard, and the fallback
   (full rerun of the extended window) must exist before the batch starts.
2. Under `stake_amount: unlimited` the stake differs between the run-in and the continuous run. Ratios differ
   by about 1e-5; `profit_abs` and the dollar figures of the page depend on the fixed 1000 USD convention and
   are unaffected, but any figure that sums `profit_abs` of the stitched trades mixes two stake histories.
   Check where `profit_abs` is used (attribution summaries do).
3. XMR has no candles after 2024-02-20, so the tail runs have seven pairs; `max_open_trades` is then reduced
   by freqtrade (8 to 7). It made no difference in the test; slot-limited strategies could differ, and the
   convergence check would show it.
4. The confirmation label, the floor tiers and every ranking may shift with 29 more days. That is the
   purpose, but it means previously published numbers change; keep the old figures in git history.
5. Runtime mix: 168 Docker baselines. If the native run-in does not converge for many of them, the Docker
   path becomes part of the batch.
6. Extending `regime_daily.csv` invalidates the pinned hash of all Model 1/2/3 manifests (see 4.2). Decision
   needed: leave them as snapshots (proposed) or rerun them (large).

## 7. Rollback

All changes are additive: a new manifest and archives, one flag in attribution, the two `END` constants,
regenerated outputs. To go back: restore the two constants, delete the extension manifest, regenerate from the
committed state. The old `regime_daily.csv` and every old archive are kept.
