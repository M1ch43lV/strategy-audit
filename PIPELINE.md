# Pipeline — which program runs when, and what it touches

Handwritten, not generated: unlike `STRATEGY_STATUS.csv` or `RUNTIME_ENVIRONMENTS.md`, this sequence does not change with each measurement, but only when the test chain itself changes. Whoever installs a new stage or modifies an existing one updates this file by hand.

This file answers a single question: **in which order do the scripts run, and which file reads/writes which one?** What each stage means content-wise and why it was decided this way and not otherwise is specified in `REGIME_PREREGISTRATION.md` (binding) and `REGIME_AUDIT_PLAN.md` (reference) — see `DOCUMENT_MAP.md` for the reading order to it.

All native runs (not Docker) need the Python interpreter from `ftenv/Scripts/python.exe` (`freqtrade`/`pandas` is installed there, not in the system Python) — usually via the environment variable `PROFILE_PYTHON`.

## Stage 0 — Corpus Collection (once, or when new repositories are added)

`python -m tools.harvest owner/repo` is the complete source-intake command. When it finds at least one new class, it regenerates execution profiles, classification, preregistered phase hypotheses, semantic duplicate evidence, duplicate adjudication, strategy status, and the status page in dependency order. These are source/report transformations only: harvest never starts a smoke run, bias diagnostic, full backtest, or performance-based decision. `--no-refresh` is the explicit batch-download escape hatch.

| Program | Reads | Writes |
|---|---|---|
| `tools/harvest.py` | GitHub API (only `.py` files with `IStrategy`) | Files under `repos/<repo>/` |
| `tools/census_repos.py` | `evidence/corpus_sources.json`, `repos/**` | Statistics on copy families (console/reference for `evidence/exclusion_criteria.py`s C-text) |
| `evidence/new_repo_candidates.py` | GitHub topic search, `evidence/corpus_sources.json` | `evidence/NEW_REPO_CANDIDATES.json`, `evidence/NEW_REPO_CANDIDATES.md` |
| `evidence/repo_freshness.py` | local `git log` per repo, GitHub tip, `evidence/EXECUTION_PROFILES.csv` | `evidence/REPO_FRESHNESS.csv`, `evidence/REPO_FRESHNESS.md` |

Result of this stage: new rows in `evidence/EXECUTION_PROFILES.csv` (one row per strategy implementation, the canonical source for the rest of the chain).

## Stage 1 — Test Run (loads the strategy, checks if trading is happening at all)

| Program | Reads | Writes |
|---|---|---|
| `evidence/profile_smoke.py` | `evidence/EXECUTION_PROFILES.csv`, `evidence/PROFILE_CLASS1.json` (Repair Rules) | `evidence/PROFILE_SMOKE.json` |

Since the prospective amendment of 2026-09-10, the trial run is a fixed cascade: `20200301-20200401` (1 month), with fewer than 10 trades `20200301-20200601` (3 months), thereafter `20200301-20210301` (1 year). It stops at the first result with at least 10 trades and records all attempts. Errors/timeouts are not reinterpreted as passed through a longer window. Existing full-window evidence remains prioritized.

**2026-09-06, completed:** `ELIGIBILITY_NEVER_RUN.json` and `ELIGIBILITY_TRAP_SMOKE.json` were one-time fallback stores from previous waves (no runner in the current repo rewrote them) — 65 of the 83 lines in them had no separate `evidence/PROFILE_SMOKE.json` entry, `evidence/strategy_status.py` fell back to these two files for them. Caught up via targeted `evidence/profile_smoke.py --strategy ... --profiles spot_long futures_long unknown` (empirically checked: previously 65 of 83 lines in `STRATEGY_STATUS.csv` changed if the files were omitted, afterwards not a single one) and removed both files, including the fallback loop in `evidence/strategy_status.py`.

If the test run fails due to a specified, fixable obstacle (missing `timeframe`, missing local module, signature change of freqtrade/pandas/numpy), one of the following repair routes will take effect, after which stage 1 runs again for this line:

| Repair Route | Writes |
|---|---|
| `evidence/eligibility_timeframe_evidence.py` → `evidence/eligibility_timeframe_repair.py` | `evidence/ELIGIBILITY_TIMEFRAME_EVIDENCE.json`, `evidence/ELIGIBILITY_TIMEFRAME_REPAIR.json` |
| `repair/local_modules.py` | `evidence/REPAIR_LOCAL_MODULES.json` |
| `repair/patch_class2.py`-type signature repairs | `evidence/ELIGIBILITY_SIGNATURE_REPAIR.json` |
| `repair/compat_signature.py` (17 shims, loaded automatically via `evidence/profile_freqtrade.py`) | no own store — effective at runtime, logged in `evidence/PROFILE_CLASS1.json` |

## Stage 2 — Bias Exclusion Check: Look-Ahead First

| Program | Reads | Writes |
|---|---|---|
| `evidence/profile_bias.py` (`run_diagnostic`, native or Docker) | `evidence/EXECUTION_PROFILES.csv`, repair stores | `evidence/PROFILE_BIAS.json` |
| `evidence/eligibility_lookahead_backfill.py` | `STRATEGY_STATUS.csv`, `evidence/EXECUTION_PROFILES.csv`, `evidence/WARMUP_CONVERGENCE.json`, `evidence/PROFILE_CLASS1.json` | `evidence/ELIGIBILITY_LOOKAHEAD_BACKFILL.json` |
| `evidence/profile_bias_merge.py` | disjoint shard files (in parallel runs) | the canonical `evidence/PROFILE_BIAS.json` |

A native look-ahead finding of `FOUND` is a final information-leak exclusion. Neither the warm-up ladder nor Recursive-Bias runs afterward because they cannot repair an information leak.

The diagnostic interval has been identical in both modes since the amendment of 2026-09-10: `20200301-20200601`. A stored futures run of only one month or a spot run over `20190101-20190401` is of historical provenance and must be superseded and measured again before a new decision.

An exception applies to the work queue: A successful canonical pooled Stage-8 full backtest closes the preceding technical verification chain for exactly the same implementation. `evidence/strategy_status.py` shows this as `technical_chain_complete=true` and then does not set `open_work` if the source hash and run profile match `results/regime/full_backtest_manifest.json`. This is not a retrospective E1 admission and does not override any documented exclusion; failed, OOM, or timeout Stage-8 attempts do not count as completion.

Regardless, each row with the cohort value `excluded` is a completed work case: it remains visible with its exclusion reason and evidence, but does not receive `open_work`. `exclusion_unconfirmed` is explicitly not synonymous with this; these not-yet-confirmed exclusions remain open until the missing decision evidence is available.

In addition, the owner decided on 2026-09-10 for level 8: A previously approved strategy with `full_backtest_status`, `failed`, `resource_inconclusive`, or `timeout` is not testable for this benchmark and is finally excluded as C10 `full_backtest_not_testable`. These three states will not be rescheduled in the full backtest.

## Stage 3 — Warm-up Convergence Ladder after Passing Look-Ahead

| Program | Reads | Writes |
|---|---|---|
| `evidence/warmup_convergence.py` (`lookahead_pass`) | `evidence/EXECUTION_PROFILES.csv`, identity-linked Look-Ahead-PASS, repair stores | `evidence/WARMUP_CONVERGENCE.json` |

Only a look-ahead line with `PASS` can reach this stage. `NA` is not a pass and will not receive a follow-up measurement until the technical cause is clarified. The frozen convergence ladder is 1, 2, 7, 14, 30, 90, 365 days, converted into candles over its own timeframe. A line is `converged`, `not_converged_within_ladder`, or `inconclusive`.

## Stage 4 — Final Recursive Bias after Converged Warm-up

| Program | Reads | Writes |
|---|---|---|
| `evidence/profile_bias.py` (`recursive`, native or Docker) | `evidence/EXECUTION_PROFILES.csv`, stored Look-Ahead-PASS and converged ladder with chosen initial value | `evidence/PROFILE_BIAS.json` |

The final Recursive-Bias run explicitly receives the ladder's smallest converged `chosen_startup_candle_count` as `--startup-candle`. Without a Look-Ahead `PASS` and a current converged ladder, the runner defers it. Thus neither an author's overly short declared value nor Freqtrade's standard warm-up can determine the final finding.

## Stage 5 — Data Coverage

| Program | Reads | Writes |
|---|---|---|
| `evidence/regime_coverage.py` | `evidence/EXECUTION_PROFILES.csv`, candle files under `user_data/data/binance` | `evidence/REGIME_COVERAGE.csv`, `evidence/REGIME_COVERAGE.md` |

Pure file system check (no Freqtrade execution), cached per `(mode, timeframe)` — inexpensive, safely reproducible at any time. Currently covers all 1,050 lines; the historical count as of 2026-09-06 was 919.

## Stage 6 — Merging

| Program | Reads | Writes |
|---|---|---|
| `evidence/strategy_status.py` | **everything** from level 0–5 plus `evidence/REGIME_ELIGIBILITY.csv` (invalidated historical E0 snapshot, exclusively provenance), `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` (active E1 decisions), `evidence/STRATEGY_CLASSIFICATION.json`, `evidence/MARKET_PHASE_HYPOTHESIS.json`, `evidence/BLOCKED_TRIAGE.json` | `STRATEGY_STATUS.csv`, `STRATEGY_STATUS.md`, **automatically in the same run**: `evidence/exclusion_criteria_list.md`, `evidence/repair_measures_list.md`, `RUNTIME_ENVIRONMENTS.md` |

A single call (`python -m evidence.strategy_status`) writes all five files. `--check` only checks whether they are still up to date (does not write anything); `--selftest` runs the built-in consistency checks.

E0 is not a fallback option: its 67 old `regime_eligible=true` flags may not replace any check and may not allow any line. Only an active `admitted_E1` decision generates `cohort=E1_expanded`; the old E0 membership appears only in `gate_notes`.

## Stage 7 — Admission (Admission)

| Program | Reads | Writes |
|---|---|---|
| `evidence/eligibility_admit_converged.py` (current rule, `converged_clean_gates_v1`) | `STRATEGY_STATUS.csv`, `evidence/WARMUP_CONVERGENCE.json` | appends new `admitted_E1` lines to `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` |
| `evidence/eligibility_expansion_adjudicate.py` (older Wave-B/C rules, `zero_warmup_analyzer_adapter_v1` / `native_gate_pass_v1`) | `evidence/ELIGIBILITY_EXPANSION_PROOFS.json`, `evidence/ELIGIBILITY_EXPANSION_WARMUP.json`, `evidence/ELIGIBILITY_EXPANSION_LOOKAHEAD.json`, `evidence/ELIGIBILITY_EXPANSION_EQUIVALENCE.json` | same `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`, plus `.md` report |

**Afterwards, mandatory back to level 6.** The admission decision is only available in `STRATEGY_STATUS.csv` when `evidence/strategy_status.py` runs again and reads back the extended `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`. A run of level 7 without a subsequent level 6 still shows the old status in `STRATEGY_STATUS.csv`.

## Stage 8 — Backtest over the full window

Two structurally different, both necessary measurements (see `REGIME_AUDIT_PLAN.md` §28.1) — neither replaces the other:

| Program | Purpose | Reads | Writes |
|---|---|---|---|
| `evidence/profile_full_window.py` (sharded in pairs) | Stage-7 Confirmation: does the strategy trade across the entire window, per pair | `evidence/EXECUTION_PROFILES.csv` | `evidence/PROFILE_FULL_WINDOW.json` (or shard files in parallel containers) |
| `evidence/merge_full_window_shards.py` | merges shards | `evidence/PROFILE_FULL_WINDOW_shardA.json`, `_shardB.json`, `_shardTF.json` | the canonical `evidence/PROFILE_FULL_WINDOW.json` |
| `regime/full_backtest.py` (pooled, `canonical_pooled_native_pair_universe`) | Phase A: actual performance backtest over all 8 pairs pooled | `STRATEGY_STATUS.csv` (E1 cohort) | `results/regime/full_backtest_manifest.json`, `full_backtest_native.json` |

`evidence/PROFILE_FULL_WINDOW.json` flows back into Stage 5 (`evidence/strategy_status.py` reads it for `observed_trades`/`trade_evidence`). The pooled backtest results from `regime/full_backtest.py` **do not** flow back into the approval — they are the data basis for Stage 9.

**Misunderstanding that suggests itself: 'Single pair' does not mean 'every pair fully measured.'** `evidence/profile_full_window.py` is a yes/no gate, not a performance measurement: it only answers 'does the strategy act over the entire window at all, for at least one pair?' As soon as ONE pair produces trades, the question is answered, and the rest of the pair list is no longer touched for this strategy (comment in the script header: 'One positive pair is sufficient to resolve a zero-trade smoke as positive... Sharding does not replace pooled performance backtests'). Only if ALL configured pairs produce zero trades does each one actually need to run through to confirm '0 trades' — which is why `evidence/PROFILE_FULL_WINDOW_shardA.json`/`_shardB.json` show fewer completed pair measurements for many strategies. as configured pairs, even though the strategy itself is already considered `measured`.

The actual completeness — every pair over the entire 6.5-year window, without interruption — is provided exclusively by `regime/full_backtest.py` (line above): it calls freqtrade without the `--pairs` filter, thus with the complete pair list together in a single backtest, and never terminates early.

**Performance limit instead of endless retry.** The 3600s timeout is a hard limit, not adjustable per strategy. `SuperHV27` and `Schism` each ran twice independently exactly up to the 3600s limit, without crashing and without OOM signature — the compatibility shims (`repair/compat_signature.py`) fixed the original crash, but the remaining per-trade costs over 8 pairs and 6.5 years are not enough for that. `evidence/POOLED_BACKTEST_PERFORMANCE_LIMIT.json` records this confirmation (rule: at least two independent timeouts, no other type of error in between); `regime/full_backtest.py` reads it and sets the status once to `performance_limited`, instead of consuming a full hour again on each container run. The strategy remains approved (`E1_expanded`) — it permanently only lacks the pooled performance metric for Stage 9.

**The same principle for confirmed memory shortage.** 52 strategies (BBRSI2/BBands/BinHV45-*/Cluc*-family, among others) were `resource_inconclusive` both under the original 13-14GB/`--workers 2` setting and afterwards, after increasing to 16GB VM memory with `--workers 1` on 2026-09-07 — a single process with the full memory budget, no concurrency left that could be blamed. This refutes resource contention as the cause; what remains is the strategy's own memory consumption over 8 pairs and 6.5 years. `evidence/POOLED_BACKTEST_OOM_LIMIT.json` records the confirmation, `regime/full_backtest.py` sets the status once to `oom_confirmed` instead of repeatedly trying endlessly. Here too: still allowed, just without the level-9 metric.

**Third category: unlimited stake growth.** `FastSupertrend_optim3_rsi_75lev` failed at 37% of the pooled run with `Stake amount 12570778.900608359 too high for XMR/USDT:USDT`. Cause: `runtime/profile_futures_config.json` sets `stake_amount: unlimited`; the strategy fixes leverage at 5× and lets profits run (`minimal_roi = {"0": 0.99}`). Over enough profitable years, the wallet grows exponentially until the calculated stake exceeds any real market liquidity. Unlike the first two categories, this is 100% deterministic: it is unrelated to memory, workers, or timing, and a retry reproduces exactly the same error at the same point. No earlier stage detects it: the smoke test uses the same configuration but only a one-month window, far too short for compounding to reach this scale, while Recursive-Bias and Look-Ahead-Bias test information leakage rather than capital scaling. `evidence/POOLED_BACKTEST_STAKE_OVERFLOW.json` records the confirmation; the same mechanism as above sets `stake_overflow_confirmed`. Whether other leveraged strategies carry the same risk was deliberately left open.

**Correction 2026-09-07: `evidence/profile_full_window.py` is not required for the entire E1 cohort, only for zero-trade candidates.** The citation above (`REGIME_AUDIT_PLAN.md` §28.1) does not support this claim — §28.1 addresses trade attribution versus gated performance (Phase A/B), not single-pair versus pooled backtests. The actual reason `evidence/profile_full_window.py` exists is stated in `evidence/strategy_status.py`: admission itself requires only `observed_trades != 0` from the smoke test (`evidence/eligibility_admit_converged.py` specifies no minimum, not even 10; this was checked across the repository despite a contrary recollection). The full 6.5-year window is mandatory only when the smoke test showed zero trades and a strategy might therefore be excluded (`full_window_measurement_pending`, only for `reason == "no_trades_in_full_measurement"`). Otherwise, a randomly quiet smoke-test month could unjustly exclude a strategy that does trade.

Sample on this date: **0 of 608 `E1_expanded` strategies have `observed_trades == 0`.** At that time, no admitted strategy needed this stage: all 571 strategies assigned to the `full-window-a`/`full-window-b` containers already had positive smoke-test evidence and needed no confirmation. `regime/full_backtest.py` (pooled and already running for the same cohort) also provides a more representative trade count for this majority because it shares the `max_open_trades` capital constraint across all pairs instead of isolating each pair. Both containers therefore stopped after all 571 assignments, with zero genuine zero-trade cases. Before any future cohort expansion starts `evidence/profile_full_window.py`, first check `observed_trades == 0` in `STRATEGY_STATUS.csv` and run it only for that subset.

## Stage 9 — Market Regime Classification

| Program | Reads | Writes |
|---|---|---|
| `regime/regime_engine.py` | local candle files | `results/regime/regime_daily.csv`, `regime_episodes.csv`, `regime_transitions.csv`, `regime_btc_episodes.csv`, `regime_state_summary.csv`, `regime_feature_distributions.csv`, `regime_manifest.json` |
| `regime/validate_regime.py` | the same `results/regime/regime_*.csv` | nothing (pure test, console output PASS/FAIL) |
| `regime/report.py` | the same files | `REGIME_DATA_REPORT.md` |

Generates the frozen 4-state model (BULL/BEAR/SIDEWAYS/TRANSITION from DMI(14)/ADX(14)) plus the raw data from which the six-phase extension (`bull_trend`/`bear_trend`/`range_quiet`/`range_choppy`/`transition`/`high_vol_shock`) in Stage 9 is derived.

## Stage 10 — Attribution (per strategy/candidate, per regime/phase)

| Program | Reads | Writes |
|---|---|---|
| `regime/attribution.py` | `results/regime/regime_daily.csv`, `full_backtest_manifest.json`, `STRATEGY_STATUS.csv` (E1 cohort) | `results/regime/trade_regime_attribution.csv`, `strategy_btc_regime_summary.csv`, `strategy_regime_summary.csv`, `strategy_episode_summary.csv`, `strategy_phase_summary.csv`, `strategy_phase_episode_summary.csv`, `attribution_manifest.json` |
| `regime/gated_attribution.py` | `regime_daily.csv`, a complete `model1_backtest_manifest.json`, `model2_backtest_manifest.json` or `model3_backtest_manifest.json`, current E1 identities | per model in `results/regime/modelN_attribution/`: Trade attribution, five `candidate_*_summary.csv` and `attribution_manifest.json` |

The two `*_phase_*` files (Six-Phase Model, Addendum 2026-09-05) already exist as code, but have not yet been run in production — they require `regime/full_backtest.py`'s complete results (Stage 7). Whether a writer is currently running for this is determined solely by the checks in `HANDOFF.md`; this pipeline file is not a run status. The gated attribution by default rejects an incomplete candidate set; `--allow-partial` only generates a technical intermediate state explicitly marked as partial and is not a ranking release.

## Stage 11 — Hypothesis (independent, to be frozen before any evaluation)

| Program | Reads | Writes |
|---|---|---|
| `evidence/market_phase_hypothesis.py` | `evidence/EXECUTION_PROFILES.csv`, `evidence/STRATEGY_CLASSIFICATION.json`, `cluster/clusters.json` | `evidence/MARKET_PHASE_HYPOTHESIS.json` |

Must be written **before** anyone looks at the results from stage 9 — otherwise it is no longer a prediction (`REGIME_AUDIT_PLAN.md` §28.3). Already executed; is only read by `evidence/strategy_status.py` (stage 5), never decided anew.

## Stage 12 — Benchmark: Model 0/1/2/3

After the expansion frozen on 2026-09-07 before each productive gate run, four comparison levels per strategy:

- **Model 0 — partially measured.** "Original strategy, no regime filter" is
exactly what `regime/full_backtest.py` (level 7) calculates: the ungated, pooled backtest across all 8 pairs. The resumable call `python -m regime.full_backtest` continues this measurement; ongoing writers are previously excluded according to `HANDOFF.md`. It is not a separate, yet-to-be-built level. **Correction compared to the previous version of this file:** it incorrectly stated here "no script exists" for the entire level 11 — that only applied to model 1/2 and the comparison itself, not to model 0.
- **Model 1 — implemented, not yet run in production.**
`regime/gated_backtest.py --model model1` filters entries according to the BTC states explicitly mentioned in the candidate spec. Global BTC states remain available even if no local daily line exists for a delisted coin.
- **Model 2 — implemented, not yet run in production.**
`regime/gated_backtest.py --model model2` filters entries exclusively based on the explicitly specified local coin states. It does not read or require any BTC state. If the local state is missing, the gate closes.
- **Model 3 — implemented, not yet run in production.**
`regime/gated_backtest.py --model model3` is the previous combined Model-2 logic: Entries require both an allowed global BTC state and an allowed local coin state. Exits remain completely with the original strategy in all three gate models.
- **The technical comparison of the four levels is implemented, not yet
ran productively. ** `regime/model_compare.py` checks identical candidates, Model 3's agreement with Model 1's BTC-Gate and Model 2's Coin-Gate, time windows, identities, and archives before it places the four runtime metrics side by side. It writes `model_metrics_long.csv`, `model_comparison.csv`, and `model_comparison_manifest.json`, but does not sort or rank any strategy. The mechanical deltas are Model 1 minus 0, Model 2 minus 0, Model 3 minus 0, Model 3 minus 1, and Model 3 minus 2; Model 2 minus Model 1 is not output as an incremental effect because the two individual gates are not nested within each other.

The runner writes atomically after each candidate, locks one output store against a second writer, and binds each run to source/config identity, regime data hash, gate rule, candidate spec, time range, and analysis role. Multiple gate variants of the same strategy receive separate archives.

The candidate spec is not generated from performance results. It has schema version 1 and contains:

```json
{
  "schema_version": 1,
  "candidate_set_id": "predeclared-id",
  "analysis_role": "PILOT",
  "timerange": {
    "spot": "YYYYMMDD-YYYYMMDD",
    "futures": "YYYYMMDD-YYYYMMDD"
  },
  "candidates": [{
    "candidate_id": "stable-candidate-id",
    "strategy_id": "canonical-strategy-id",
    "long_btc_states": ["BULL"],
    "short_btc_states": ["BEAR"],
    "long_coin_states": ["BULL"],
    "short_coin_states": ["BEAR"]
  }]
}
```

The BTC fields are mandatory for Model 1 and 3, the Coin fields for Model 2 and 3. The same frozen spec may carry all four fields; each runner reads exclusively the fields relevant to its model. Even empty lists must be explicitly stated; a forgotten field may never silently allow all states. The three calls against the same frozen spec are:

```bash
python -m regime.gated_backtest --model model1 --candidate-spec <spec.json>
python -m regime.gated_backtest --model model2 --candidate-spec <spec.json>
python -m regime.gated_backtest --model model3 --candidate-spec <spec.json>
python -m regime.gated_attribution --model model1
python -m regime.gated_attribution --model model2
python -m regime.gated_attribution --model model3
python -m regime.model_compare
```

The still pending evaluation stage is not the mechanical side-by-side comparison, but the preregistered assessment: Exposure-Match, specialist thresholds, Discovery/Validation, and portfolio rule. All nine preregistration questions (`REGIME_PREREGISTRATION.md`, Amendment 2026-09-11) have been decided since 2026-09-11 — one candidate spec and one productive Model-1/2/3 run are thus approved. Portfolio allocation for multiple simultaneously qualifying candidates is deliberately deferred for Version 1, not decided.

## Stage 13 — Specialist/Universal Evaluation

| Program | Reads | Writes |
|---|---|---|
| `regime/specialist_evaluation.py` | a `trade_regime_attribution.csv` (model 0 canonical, or a `modelN_attribution/` file), candle data under `user_data/data/binance` | `results/regime/specialist_evaluation/`: `btc_specialist_table.csv`, `coin_specialist_table.csv`, `btc_specialist_ranking.csv`, `coin_specialist_ranking.csv`, `universal_strategies.csv`, `strategy_total_dollar_gain.csv`, `evaluation_manifest.json` |

Apply the rules frozen in Amendment 2026-09-11 to an existing attribution: Discovery/Validation split, the 5-episode / 10-trade specialist threshold, and the exposure-matched benchmark (coin's own spot buy & hold return over exactly the trading interval of each individual trade, using `merge_asof` against 1-minute candles). Rank only `VALIDATION`-tier rows; everything else is reported but never ranked.

`max_drawdown` (§19 `worst_regime_drawdown`, 2026-09-12 followed explicitly at the user's request): per (strategy, regime) the worst peak-to-trough decline of a hypothetical curve from exactly the trades matched in this regime, ordered according to `close_date` — `_regime_drawdown()`. The same fixed-$1000-per-trade convention as the dollar view below, for the same reason: a compounding curve over the regime trades of a strategy reproduces the same exponential distortion that was already discarded there. Calculated for each row (VALIDATION like EXPLORATORY), never just for the 'worst' combination — in the universal candidate view the value simply comes from the row that `worst_regime` already references anyway.

**Correction 2026-09-13** (User question: "Why max. drawdown > 100%? Leveraged?"): the first implementation normalized against the previous curve peak instead of against the actual capital used. With many trades in one regime, the peak remains small, while many ordinary small losses add up to a large amount — `CryptoFrogHO2` showed 685% drawdown in one regime, although the worst single trade lost only −13% (no short, no leverage; verified: only 4 out of 589 strategies had any trade with `profit_ratio < -1`). Fixed by normalizing against the accumulated capital (`Trades-so-far × $1000`) instead of against the peak — therefore mathematically cannot exceed 100% as long as no single trade loses more than 100% of its own stake (real Leverage or a short loss beyond the full stake would be exactly that). After the correction, no line currently in Model 0 or the 7-series pilot is above 100%; if it does occur in the full Model-1/2/3 run (in progress), it is a real leverage/short signal and will then be marked.

**FreqForge-inspired additional metrics (2026-09-14, at explicit user request, after discussion with DeepSeek-v4-pro):** six additional columns per (strategy, regime) — `profit_factor`, `worst_trade`, `liquidation_rate`, `sortino`, `cagr`, `drawdown_since_peak` —, plus the six associated point values and a weighted `freqforge_score` (0-100), modeled on the six categories from [github.com/baxr6/FreqForge](https://github.com/baxr6/FreqForge) (Sortino 25%, Drawdown-Control 25%, CAGR 15%, Liquidation-Safety 15%, Profit-Factor 10%, Worst-Trade-Severity 10%). Explicitly only one additional reporting column, no replacement of the tier/excess-return ranking — §17 ('Do not rely on a single composite score') remains in effect for the actual ranking.

Two real errors in the first draft, found by DeepSeek-v4-pro before implementation (`mcp__deepseek-mcp__critique`, not afterwards):
1. *CAGR* originally compounded `mean_profit_ratio` (average per
Trade), which completely ignores the trade number — 10 trades and 50 trades at +2% each over the same day period would have resulted in identical CAGR, even though the actual profit is five times different. Fixed: CAGR now compounds the actual total return of the group (`dollar_gain_usd / START_CAPITAL`), not the average.
2. The reuse of `_regime_drawdown()` for the drawdown control-
Category was position-dependent biased: the same −40% trade resulted in
1. Trade of the group 40% drawdown, as the 100th trade only ~0.4%, because that
Capital committed so far has been accumulating since the start of the group instead of being reset since the last peak. New, separate function `_regime_drawdown_since_peak()` fixed — normalizes against the capital since the last peak, not since the start of the group. `_regime_drawdown()` itself (the existing `max_drawdown` column) remains unchanged, it still correctly answers the other, previously delivered question (leverage proof over the entire regime history).

Own finding during the self-test (perfect win rate case): `profit_factor` with zero loss trades resulted in `-inf` instead of `+inf`, because `-leere_Summe.sum()` delivers `-0.0` instead of `0.0` and `x/-0.0 = -inf` (IEEE-754 signed zero issue). Fixed with `abs()` instead of negation; `+inf` is now treated as the best value (100 points) as documented by FreqForge, not as an error case.

Annualization of Sortino/CAGR is calculated against `total_regime_days` — the sum of the actual day spans of the group's own (deduplicated) episodes (`_regime_days()`, from new `btc_episode_days`/`coin_episode_days`/ `joint_episode_days` columns in `attach_benchmark()`), not the calendar span between the first and last matched trade — otherwise, years outside the regime between scattered episodes would count as regime time. CAGR can take extreme values with short episodes (maximum in the entire Model-0 portfolio: 139 million %) — known, accepted limitation, hence the log scaling in the scoring. Model 0 (589 strategies) and the 7-series pilot were calculated and wired into the artifact (version 30); which criterion the top-10 new selection for Models 1/2/3 uses is an open, separate decision.

**Episode Excess LCB and Correction of the Excess Return Mean (2026-09-14, at explicit user request after DeepSeek-v4-pro consultation "regime-audit-reliability-score"):** User goal was a metric for "beats Trading B&H, AND is statistically reliable (many episodes), not just randomly good in a few trades" — Profit Factor alone was rejected because it can be very high with very few trades and lower but more reliable with many trades, without this being visible. DeepSeek recommended a one-sided 95% lower confidence bound on the mean **episodic** excess return (`_episode_excess_lcb()`): `LCB = Mittelwert(x_i) − t(0,95, n−1) × Standardfehler(x_i)`, `x_i` = the excess return of the i-th independent episode, `n` = episodes, never trades. Few/highly variable episodes lower the bound. automatically into the negative — no separate minimum-trade rule needed, the reliability is already built into the formula. `lcb_grade` derives a Gainium-like A-F rating from this over fixed thresholds frozen before each results review (A: LCB>+2%, B: 0 to +2%, C: −2% to 0, D: −5% to −2%, F: below). Discarded alternatives: Bayesian hierarchy shrinkage (more elegant with many strategies, significantly more complex) and Wilson score on a binary "beats B&H yes/no" (too simple, ignores the size of the excess return). Both new columns are purely descriptive, not a replacement for Tier/Ranking or `freqforge_score` — kept separate so the "no single score" rule (§17) is not violated twice.

During implementation, a real, independent error became apparent: `excess_return` had so far averaged over **trades**, not over episodes — the same misalignment that the dollar correction above had already fixed once, only as an average instead of as a sum (an episode with 50 trades counted 25 times as much as one with 2 trades, even though both are only a single independent observation). Fixed in `_episode_pairs()`: each episode is first summed individually, then averaged over the episodes — symmetrical to the long-correct `mean_benchmark_return`. This shifts excess return (and everything derived — ranking, top-N selection, universal candidate figures) across the entire dataset; all specific numbers in the artifact text were newly derived (including "ADX Uptrend weakest regime" 372→359 of 379, fully consistent Candidates 0→8). Model 0 and the 7-series pilot recalculated, self-test supplemented with regression cases for both.

**Full code review by DeepSeek-v4-pro (2026-09-14, at explicit user request, conversation "regime-code-audit-2026-09-14"):** `regime/ specialist_evaluation.py`, `regime/attribution.py`, `regime/gate_adapter.py`, `regime/gated_backtest.py`, `regime/gated_attribution.py`, and `regime/ model_compare.py` were completely checked for bugs, regardless of already known fixes. Each correction proposal was re-checked with DeepSeek before implementation (not just the first finding taken). Five real errors confirmed and fixed:

1. **Animal classification counted episodes over the full history, not just that
Validation window** — the most serious finding, see `REGIME_AUDIT_PLAN.md` §18-Addendum for details and the exact counter-check against `REGIME_PREREGISTRATION.md`'s "within the validation window" formulation. Model 0 recalculated: BTC-VALIDATION lines 1,828→1,671, Coin 1,770→1,757.
2. **Sortino mixed time scales** — the numerator was a daily rate
(`sum_profit/total_days`), denominator the dispersion of raw trade-level losses, multiplied by `sqrt(365)` as if both sides were daily. Fixed: both sides consistently at the trade level (mean and sample standard deviation, `ddof=1`, directly from `profit_ratio`), annualized with `sqrt(Trades pro Jahr)` instead of `sqrt(365)` — the usual method for a metric from irregularly timed observations.
3. **CAGR was even more faulty** — `dollar_gain_usd/START_CAPITAL` is the
Sum of many independent $1000 stakes, no single compounding position; the formula nevertheless exponentiated this sum as if it were one. Specifically observed in the full Model-0 holdings: up to 139 million % "CAGR" in short, trade-heavy episodes (see above) — mathematically consistent from the formula, but not a meaningful metric. Replaced by `annualized_return = mean_profit_ratio × Trades pro Jahr`, a linear (non-compounding) annual projection, consistent with the fixed-stake accounting that this module uses everywhere else. Renamed (`cagr`→`annualized_return`, `_cagr_points()`→`_annualized_return_points()`, artifact column "CAGR"→"Annual Return") so that the column can never be confused with a real compound interest CAGR; point scale recalibrated to the smaller typical magnitude of this metric (0%→0, 20%→50, 100%→90, 300%+ → 100 points — set before each review of a strategy value).
4. **Profit factor convention inconsistent** — `attribution.py`s
`_summarize()` reported zero loss trades `NaN` (via a `.replace(0.0, np.nan)`), `_freqforge_metrics()` reported `+inf` (best value). Standardized to `+inf`: the `.replace()` was removed and at the same time a related, until then hidden by the `.replace()`, sign error was corrected (`-matched["profit_abs"].clip(upper=0)` produces `-0.0` for all profit trades instead of `0.0`, which would have resulted in `gross_profit/-0.0 = -inf`, not `+inf` — now avoided with `.clip(upper=0).abs()`).
5. **"Liquidation safety" also included harmless `force_exit` exits**
(e.g., backtest window end), not just actual forced liquidations. Split: `liquidation_rate` (score-relevant, only `exit_reason == "liquidation"`) and `forced_exit_rate` (new, purely descriptive column, the old, broader definition — never in the score).

All five fixes secured through new or adjusted self-test cases (`specialist_evaluation.py`), including a dedicated `TIERBUG` fixture, which specifically pits 6 pre-2024 episodes against only 2 real validation episodes.

**ADX Sideways/Transition Gate for Model 1/2/3 (2026-09-14, at explicit user request, deliberate deviation from the frozen plan — see addendum in `REGIME_AUDIT_PLAN.md` §15):** Until now, each candidate gated only Long on BULL / Short on BEAR (trend-following assumption). New candidate spec `results/regime/candidate_spec_pilot_v1_sideways_transition.json` (14 candidates: the 7 pilot strategies each once with `-sideways`- and once with `-transition`-suffix, `candidate_set_id = pilot_v1_stratified_sideways_transition_gate`, `analysis_role = PILOT`). Unlike BULL/BEAR, SIDEWAYS/TRANSITION have no directional assumption, hence symmetrical gate: `long_btc_states = short_btc_states = long_coin_states = short_coin_states = ["SIDEWAYS"]` or `["TRANSITION"]` — tests whether a gate on pure sideways/transition phases is helpful, regardless of the direction the strategy actually takes. Runs through the same unchanged chain (`gated_backtest.py` → `gated_attribution.py` → `specialist_evaluation.py`); the new candidates appear as additional rows in the same Model-1/2/3 tables (own candidate_id, e.g., `ADXDM-sideways`), not as a separate table. Backtest completed (`--workers 1`, sequentially across all three models due to the 16-GB memory guard, all 14/14 candidates measured per model). `gated_attribution.py` additionally ran against the new manifest, into its own `modelN_attribution_sideways_transition/`; merged via Python with the existing `modelN_attribution/trade_regime_attribution.csv` (`modelN_attribution_merged/`, previously checked for disjoint candidate_ids — 70,804/69,592/53,620 trades for Model 1/2/3 total). `specialist_evaluation.py` recalculated over it (`--joint` for Model 3), `export_v9.py`/`build_v8.py` rerun, artifact published (Version 33). Result: Model 1 thereby gets 10 universal candidates (previously 0 with only the trend-following variant — due to the BTC-only gate logic a an individual candidate, fixed only on one coin-regime state like `X-sideways`, can still reach all four coin regimes, because model 1 does not restrict the coin state at all); models 2/3 remain at 0 universal candidates, because their coin gate `X-sideways`/`X-transition` structurally fixes it to exactly one coin-regime state.

**Regime Specialists Top 10 per ADX Condition, discards the 7-alphabet pilot (2026-09-14, at explicit user request, double-checked with DeepSeek-v4-pro before implementation — see addendum in `REGIME_AUDIT_PLAN.md`):** the previous 7-strategy pilot was not a curated selection, but merely the first 7 strategies alphabetically (for initial orientation). Discarded at user request — old candidate spec, backtest, and attribution files remain, but will neither be reused nor shown in the artifact.

*Gate Design:* `-trend` (long only Uptrend, short only Downtrend, a combined candidate) replaced by four symmetric single-state gates `-uptrend`/`-downtrend`/`-sideways`/`-transition` (long AND short each only in the specified state — `-sideways`/`-transition` already operated this way, `-uptrend`/`-downtrend` are new). Specific finding that contradicts the old coupling: `NASOSv5_mod3` and `Squeeze001`, according to `trade_regime_attribution.csv` (column `is_short`), have 0% short trades in their entire history, with a real Bear Edge (LCB +1.7%/+5.8%) — a `-trend` gate would have blocked all their bear activity, because its bear permission is strictly limited to short. `-trend` remains as an optional fifth gate, but only for candidates that are futures-capable AND in their ungated history actually long AND have short trades (checked each candidate against the raw `is_short` column): ` FastSupertrend_optim3_rsi_80` (8,980 short / 8,318 long) and `FSampleStrategy` (1,007 long / 86 short).

*Selection metric:* for each ADX state independently, all candidates with a `VALIDATION` row in exactly this one state (no requirement for the other three — solves the universal candidate-379 pool survivorship problem, which an earlier span-based version would have had), sorted descending immediately after `episode_excess_lcb` in this state, `episode_excess_lcb > 0` required (statistically true edge, no noise), top 10, deduplicated to one candidate per strategy family (almost identical parameter variants — sometimes with literally identical trade/episode/LCB values, e.g., six `NostalgiaForInfinity` derivatives with exactly 18 trades/14 episodes/LCB 0.0300 — reduced to the highest-ranked representative).

*Result of the frozen method* against `coin_specialist_table.csv` (589 strategies, VALIDATION tier): ADX Uptrend has only a single statistically validated specialist across the entire set (`FastSupertrend_optim3_rsi_80`; the only second candidate with LCB&gt;0 is the same family and drops out during deduplication) — consistent with the already documented finding that Uptrend was the toughest regime against Buy&amp;Hold. Downtrend/Sideways/Transition each fill a complete deduplicated Top 10. 25 individual strategies, 33 gate candidates in total (31 single-state + 2 `-trend` additional candidates). New candidate spec `results/regime/candidate_spec_regime_specialists_v2.json` (`candidate_set_id = regime_specialists_v2_lcb_ranked_deduplicated`, `analysis_role = PILOT`, same period as every previous pilot spec). Runs through the same unchanged chain (`gated_backtest.py` → `gated_attribution.py` → `specialist_evaluation.py`) — no code change needed. `regime/gate_adapter.py` was already generic across any `long/short_btc/coin_states` lists, `-uptrend`/`-downtrend` only needed new spec entries. Backtest run (`--workers 1`, sequentially over all three models, `--output results/regime/modelN_backtest_manifest_regime_specialists_v2.json`, 33/33 measured per model). In the process, a second, independent bug was found: `NostalgiaForInfinityX` delivers `enter_long`/`enter_short` as bool columns instead of the normally used int-0/1 columns; `RegimeGate.mask()` attempted to write a `0` there, which Pandas refuses with `TypeError: Invalid value '0' for dtype 'bool'` (`regime/gate_adapter.py`, affects any strategy with bool-typed entry columns, not just this one candidate). Fixed: `off` value is now adapted to the column type (`False` for bool columns, otherwise still `0`), self-test case with a bool column added. `gated_attribution.py` (`--outdir results/regime/modelN_attribution_regime_specialists_v2/`, 18,638 / 16,994 / 10,169 Trades for Model 1/2/3) and `specialist_evaluation.py` (`--outdir results/regime/specialist_evaluation/modelN_regime_specialists_v2/`, `--joint` for Model 3) recalculated above: VALIDATION lines Model 1 btc=25/coin=58 (8 universal candidates &mdash; like in the previous pilot this arises because Model 1 only gates BTC and the coin regime dimension therefore remains free), Model 2 btc=54/coin=35 (0 universal), Model 3 btc=21/coin=24/joint=24 (0 universal). `export_v2_regime_specialists.py` (new script, not `export_v9.py`’s old `MERGED_ATTRIBUTION` logic) generates three JSON blobs: `top10_by_regime.json` (the frozen selection itself, reproduced from `coin_specialist_table.csv`, not copied by hand), `gated_compare_v2.json` and `gated_detail_v2.json` (same form as the old `gated_compare.json`/`gated_detail.json`, so `regime_specialists_template.html`’s existing render functions continue to run unchanged &mdash; only the two `build_v8.py` placeholders now point to the new files). Artifact published (version 36).

Dollar view (2026-09-11, at explicit user request): in addition to the benchmark-relative excess return percentage, a dollar amount — `dollar_gain_usd`/`benchmark_dollar_gain_usd`/`excess_dollar_gain_usd` in the regime tables, as well as strategy-independent in `strategy_total_dollar_gain.csv`. First implementation compounded sequentially ($1000 start, each trade multiplied the current balance, sorted by `close_date`) — discarded because the result, after a few hundred trades, is dominated by the exponential calculation rather than the strategy quality (a pilot strategy: $1000 → $0.006 over ~3,000 trades) and because it suggests an account with exactly one open position, which none of the strategies ever had (they run on up to 8 pairs simultaneously). Instead: fixed $1000 stake per trade, no reinvestment, simple Total — robust, but no statement about capital growth with actual reinvestment.

First productive run (2026-09-11) on the 7 pilot candidates from Stage 12's candidate spec, against their Model-0 attribution (their natural, ungated trading behavior): 5 out of 7 strategies reach at least one `VALIDATION`-tier line, 5 meet the threshold in all four coin regimes simultaneously (universal candidates). `ASDTSRockwellTrading` has all 13,402 trades before 2024-01-01 — not a single validation line, correctly excluded instead of filled with discovery data. `ADXMomentum` has enough episodes, but too few trades per regime (3-7, below the 10-threshold) — `EXPLORATORY`, not ranked.

Second run (2026-09-11), without `--strategies` filter: all 589 strategies that have any model-0 attribution in `trade_regime_attribution.csv` (out of 647 fundamentally eligible — 58 are missing there due to reasons recorded in `attribution_manifest.json`, e.g., archive hash or identity mismatch, not because they were excluded here). Runtime 36s (warm cache, vectorized). 3,459,380 trades, 1,828 `VALIDATION` rows BTC regime / 1,770 coin regime, 379 universal candidates (all four coin regimes covered at `VALIDATION` tier), of which 44 with `regime_consistency == 1.0` (beat the benchmark in each of the four coin regimes). 92 of the 589 strategies yield not a single row in both tables — no trade in the validation window, analogous to the `ASDTSRockwellTrading` case from the pilot run. At ~450-480 ranked candidates per regime column is a A single rank-1 position is no longer meaningful for the 'best strategy' overall; the evaluation should be read per regime, not as an overall leaderboard.

Third run (2026-09-11), with the dollar view: 497 out of 589 strategies (those with &ge; validation window trade) get a row in `strategy_total_dollar_gain.csv`. 239/497 with positive `dollar_gain_usd`, 186/497 also beat the benchmark in dollars (`excess_dollar_gain_usd` &gt; 0). Median `dollar_gain_usd` is at &minus;$81, median `excess_dollar_gain_usd` at &minus;$297 — for this uncurated, mostly GitHub-sourced portfolio, not a surprising picture. Largest profit: `FastSupertrend_optim_quick`, +$23,492 over 11,065 trades. Largest loss: `CryptoFrogHO2`, &minus;$20,280 over 15,692 trades.

Fourth run (2026-09-11), against the Model-1/2/3 candidate attribution instead of Model 0's natural trade behavior (`--trades results/regime/modelN_attribution/trade_regime_attribution.csv --outdir results/regime/specialist_evaluation/modelN/`). Two bugs were found and fixed: `load_trades()` was hard-expecting a column `strategy_id`, but `gated_attribution.py`'s output names the same slot `candidate_id` — fixed with `_detect_id_column()`, which automatically detects which column is present and internally normalizes to `strategy_id` (logged as `source_id_column` in the manifest). `universal_table()` threw `KeyError: 'worst_regime_return'` as soon as a non-empty `coin_table` produced zero rows, covering all four coin regimes — hit immediately on Model 2 and 3, where the tighter gate leaves too few trades per regime for any of the 7 pilot candidates to simultaneously reach the threshold in all four. Result: Model 1 (BTC-Gate) 4/7 universal candidates, none fully consistent; Model 2 (Coin-Gate) and Model 3 (Combo-Gate) 0 universal candidates. Gated vs ungated comparison of total profit in dollars (6 candidates with validation trades): each gate reduces the loss of the three losing strategies (`ADXDM`, `ADX_15M_USDT`, `AlmgrenChrissStrategy`), most strongly Model 3; however, each gate also reduces the profit of the only ungated already profitable strategy (`BBMod`) — the gate also filters out profitable trades outside the trend-following regimes. `AdaptiveRegime` remains roughly the same across all four variants. Additionally revealed a third `.gitignore` gap (`results/regime/specialist_evaluation/modelN/*.csv` is two levels instead of one below the first exception pattern) — fixed with `!results/regime/*/*/*.csv`.

`attach_benchmark()`'s benchmark definition changed (2026-09-12, explicit user request): instead of Buy-and-Hold only over the open-close interval of the individual trade, now Buy-and-Hold over the *entire* ADX regime episode (first to last classified day, from `regime_daily.csv`'s `btc_episode_id`/`coin_episode_id`). Reason: the trade interval definition could practically never beat an unleveraged 1x long trade (its own return *is* approximately the interval return, minus fees) — so it could never answer whether a strategy times a market phase better than simple holding. Two new columns (`btc_episode_benchmark_return`, `coin_episode_benchmark_return`) replace the old `benchmark_return` in `_specialist_table()`; `benchmark_return` itself remains unchanged and continues to be used only by `total_dollar_gain_table()`'s regime-independent total value, which does not include any single Market phase to which it could be compared. All three runs (Model 0 fully, Model 1/2/3 against the pilot candidates) recalculated with identical row/episode/trade numbers as before — only the excess return values themselves change, no tier/floor allocation. Result for Model 0: of the 379 universal candidates, now **none** (previously 44) beat the benchmark in all four coin regimes simultaneously — 375 of 379 (99%) have BULL as the weakest regime, because practically every actively trading strategy misses part of a long rally that simple holding does not miss. This is the direct, expected answer to the original question ('are there unleveraged long strategies that time a bull phase better than buy-and-hold') — with this stricter standard, practically No, within the framework of this inventory.

Bug found and fixed in exactly this change (2026-09-12, discovered by the user in the released artifact): `_specialist_table()` summed/averaged `benchmark_dollar_gain_usd`/`mean_benchmark_return` over every validated trade instead of over each unique episode. Since `attach_benchmark()` assigns the same episode benchmark value to all trades of an episode, a strategy with many trades in few episodes counted the same buy-and-hold phase multiple times — symptom in the artifact: `Obelisk_TradePro_Ichi_v2_2` showed a "B&H profit" of +$94,882 for 1,230 trades over only 40 episodes (actual around $4,800, factor ~20 too high). Fix: before aggregation, deduplicate by unique `(strategy_id, regime, coin_pair, episode_id)` combinations — `coin_pair` is part of the key because a BTC regime episode is a globally shared calendar window in which different coins have their own Course developments, that is, various buy-and-hold investments. Concerns both the dollar amount and the percentage average (and thus `excess_return`) equally. All four runs recalculated — row/episode/trade numbers unchanged (the floor does not depend on the benchmark), excess return and dollar values partially shifted significantly; the core statement '0 out of 379 fully consistent' remains (BULL remains the weakest regime at 372/379, previously 375/379 — the magnitude of the basic statement does not change, only individual candidate values).

Model 3 previously showed two separate tables (BTC regime, Coin regime), although the gate requires both dimensions simultaneously — merged into a combined table at the user's request. Trades and dollar profit were already identical between the two tables (the same trades), but the number of episodes and excess return differed because BTC episode and Coin episode are different time windows. New fourth benchmark column `joint_episode_benchmark_return` in `attach_benchmark()`: the actual intersection of BTC episode and Coin episode of a trade (not just one of the two alone) — this is the actual condition required by Model 3's AND gate. New function `joint_specialist_table()`, after `--joint` (explicitly requested only, since it only makes sense for an AND-gated model — applied to Model 0/1/2). would result in a meaningless table). Discovered during construction: `btc_regime`/`coin_regime` almost always match for gated trades, but not without exception — 7 out of around 22,000 Model 3 trades deviate (signal candle and fill candle can be one day apart, during which one of the two regime dimensions moves independently of the other; neither reaches VALIDATION tier). Not a bug, so not handled as an error: `joint_specialist_table()` takes `coin_regime` as the sole display label instead of assuming a match. Model 1/2 unchanged (only one dimension gated, no combined regime makes sense).

## Where Docker stands instead of native Python

Stages 1–3 (trial run, both bias tests) run both natively and in the pinned Docker images (`strategy-audit-runtime:2026.7` and variants), depending on which runner calls them — both write to the same JSON stores, distinguished only by the field `runtime_id` (`native_unversioned` vs. `docker:sha256:...`). Stage 7 (full window, pooled) runs exclusively in Docker because it runs unattended for hours.

## Old files that are no longer needed

Three different categories, not one — important because they are treated differently.

### 1. From the original author of the previous work (895/900 strategies review, before this verification chain)

Publication preface and case studies of a previous, less strict review. No file here is read or written by a script from level 0–11; they describe a state that `STRATEGY_STATUS.csv` has long since replaced.

| File/Directory | Created by | Replaced by |
|---|---|---|
| `old/predecessor_audit/README.md`, `LEDGER.csv`, `LEDGER.md` | archived `ledger.py` | `STRATEGY_STATUS.md` |
| `old/predecessor_audit/CORPUS.md`, `CORPUS_PLAN.md`, `corpus/INDEX.md` + 896 cards under `corpus/` | archived predecessor tooling | `evidence/EXECUTION_PROFILES.csv`, `evidence/corpus_sources.json` |
| `old/predecessor_audit/ANALYSIS.md`, `ANALYSIS.ru.md` | (predecessor tooling) | five handpicked case studies, no population — `STRATEGY_STATUS.csv` covers the current population |
| `old/predecessor_audit/results/*.md` (`DoubleEMACrossoverWithTrend.md` et al., `INDEX.md`) | (Predecessor tooling) | the same five case studies — **not to be confused with `results/regime/`**, which is current and described from level 7–9 |
| `old/predecessor_audit/DCA.md`, `DEPTH.md`, `RESOLVABLE.md` | (Predecessor Tooling) | independent page investigations without regime reference, nothing replaces them, because nothing in the current chain asks the same question |
| `old/**` (`corpus_repair`, `eligibility_zwischenstand_2026-08`, `hmm_prototype_2026-08`, `proxy_backtests_2026-08`, `root_prototypes_2026-08`, `translation_attempts_2026-08`, `vorueberlegungen`, own `old/README.md`) | various, all before this chain | consciously archived, not deleted |
| `.codex/CONTINUATION.md` | (predecessor tooling) | explained by itself replaced by `HANDOFF.md` |

### 2. Own files of this test chain, but orphaned (no producer script anymore available)

Unlike Category 1: **our** files, not those of the original author — but the script that they once wrote no longer exists in the repo. `ELIGIBILITY_NEVER_RUN.json` and `ELIGIBILITY_TRAP_SMOKE.json` were the last two of this kind and were removed on 2026-09-06 (see Stage 1) — currently no candidates in this category. Any future find would be treated the same way: first confirm via diff that no line depends on it anymore, then commit, then remove — never the other way around.

### 3. `tools/` — own tools, but manual, not part of the automatic chain

All files here are current and not outdated. Most run on demand; Stage 0 additionally uses the corpus tools in this directory. They were moved here from the root and their root path assumptions were adjusted. The outdated predecessor gates `sync_repo.py`, `freeze_guard.py`, `verify_ledger.py`, and `totality.py`, on the other hand, are located under `old/predecessor_audit/` and are no longer part of the current CI. `totality.py` reports 124 unchecked heuristic hits on today's pipeline and is therefore not suitable as an unmodified commit guard. `ROOT` path assumptions (`os.path.dirname(os.path.abspath(__file__))`) were corrected by one level; `warmup_reparse.py`'s `from evidence import profile_bias` got a `sys.path.insert` on the root directory, the same trick that `repair/*.py` had used before.

| Program | Purpose | When to run |
|---|---|---|
| `tools/secret_gate.py` | Prevents a commit from containing a secret (four layers, see separate docstring) | before each commit that introduces new files |
| `tools/translation_repair.py` | Translates Russian comments/strings in Python files, AST-checked, never silently translates failed parts | when `tools/harvest.py` (Stage 0) brings in a repo with non-English comments |
| `tools/blocked_triage.py` | Finds fixable causes for rows that the test run never reached (freqtrade didn't even start them); writes `REPAIR_LIST.md` and `evidence/BLOCKED_TRIAGE.json`, which Stage 5 reads | after new Harvest or when the number of blocked rows changes (`--probe --list`) |
| `tools/eligibility_expansion.py` | Freezes the historical, result-blind eligibility expansion inventory (only technical stage-6 artifacts, no performance) | if `REGIME_PREREGISTRATION.md`/`ELIGIBILITY_EXPANSION_PLAN.md` are changed |
| `tools/probe_double_advise.py` | Checks whether the double `ft_advise_signals` call in `lookahead-analysis` duplicates a column | if there is a suspicion that the `enter_tag` shim distorts the result |
| `tools/probe_shim_neutral.py` | Compares backtest results with/without `enter_tag` shim on neutrality | after a change to the shim mechanism |
| `tools/probe_zero.py` | Differentiates in a row without trades whether the entry condition never becomes true or the indicator is missing | when a row shows 0 trades and the cause is unclear |
| `tools/strategy_classification.py` | Classifies type/timeframe per row from `evidence/EXECUTION_PROFILES.csv` and the strategy source code; writes `evidence/STRATEGY_CLASSIFICATION.json`, which is read by Stage 5 and Stage 10. `strategy_type` is always explicit: recognized family, `unclassified` or for test/template artifacts `not_applicable`. Order: classification before phase hypothesis, status, and HTML page. | after new harvest, if `evidence/EXECUTION_PROFILES.csv` changes or classification rules have been changed |
| `tools/strategy_status_page.py` | Builds the published page from `STRATEGY_STATUS.csv`, so that page and table never get out of sync | after each `evidence/strategy_status.py` run, before publication |
| `tools/warmup_reparse.py` | Reads stored leader logs again with the current parser without having to run freqtrade again | after a fix to the drift tables parser |

`repair/FREQAI_RESULTS.md`, `repair/REGISTER.md`, `repair/TRANSLATION_AUDIT.md` are also separate, current files, but provenance logs, not tools — only relevant if a specific repaired implementation is under discussion (see `DOCUMENT_MAP.md`).
