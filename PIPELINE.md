# Pipeline — the check chain: which program runs when, what it touches, and what was decided

Handwritten, not generated: unlike `STRATEGY_STATUS.csv` or `RUNTIME_ENVIRONMENTS.md`, this sequence does not change with each measurement, but only when the test chain itself changes. Whoever installs a new stage or modifies an existing one updates this file by hand.

This file is the one place for the check chain. **Stages 0-13** give the order, the programs, what each reads and writes, and the rule that applies today. The **Decision record** after Stage 13 holds the dated owner decisions behind the rules of Stages 0-8 (moved here from `REGIME_PREREGISTRATION.md` on 2026-09-20). Whatever was added to the chain by a protocol of its own (admission expansion, execution robustness = Stage 8b, the validation extension that is on hold) is in `PIPELINE_EXTENSIONS.md`.

Neighbours: `REGIME_PREREGISTRATION.md` is binding for the regime study (model, windows, gates, specialist rules, confirmation), `REGIME_AUDIT_PLAN.md` is the reasoning behind it (reference only), `HANDOFF.md` is the live state, and `README.md` gives the reading order. What is *currently true* of any strategy is never in this file; it is in `STRATEGY_STATUS.csv` and `evidence/PIPELINE_STATE.json`.

All native runs (not Docker) need the Python interpreter from `ftenv/Scripts/python.exe` (`freqtrade`/`pandas` is installed there, not in the system Python) — usually via the environment variable `PROFILE_PYTHON`.

## Fixed constants

Do not rederive these; a change is a new dated entry in the Decision record or in `REGIME_PREREGISTRATION.md`.

| What | Value | Rule |
|---|---|---|
| Analysis window, Spot and Futures | `20200401-20260821` (end exclusive) for both | Decisions 2026-09-03 (spot) and 2026-09-21 (futures, for comparison) |
| Discovery / validation | discovery 2020-04-01 to 2023-12-31, validation 2024-01-01 to 2026-08-20 | `REGIME_PREREGISTRATION.md`, 2026-09-11 |
| Bias and convergence diagnostic window, Spot and Futures, BTC only | `20200301-20200601` | Decisions 2026-09-09, 2026-09-10 |
| Smoke cascade | `20200301-20200401`, then `20200301-20200601`; stop at 10 trades | Decisions 2026-09-10, 2026-09-15 |
| Convergence ladder | 1, 2, 7, 14, 30, 90, 365 days; accepted when every indicator's absolute drift stays below 1.0 percent | Decision 2026-09-01 |
| Universe | eight-pair pooled canonical portfolio; pairwise shards are supporting evidence and do not replace pooled shared-capital mechanics | Stage 8 |
| Primary state model | Wilder DMI/ADX(14) on completed daily candles, shifted one UTC day; four states; six reporting phases on top | `REGIME_PREREGISTRATION.md` |
| Models | 0 original; 1 BTC-entry gate; 2 coin-entry gate (no BTC); 3 both. Exits stay original. Missing local evidence closes the gate in Models 2 and 3; Model 1 needs only BTC | `REGIME_PREREGISTRATION.md`, 2026-09-07 |
| Timeout | 3600 s per strategy run, hard, never raised, not even for one strategy | Stage 8 |
| Memory | WSL machine 16 GB plus 4 GB swap (`.wslconfig`, since 2026-09-07), not to be raised. Batches: four containers of 3.5 GB side by side, a strategy that dies or times out is repeated alone in one container of 15.5 GB (Decision 2026-09-21). An in-container exit `-9` is `resource_inconclusive`, not a strategy failure. A Docker wrapper exit 125 or an unresponsive VM is not a completed attempt | Stage 8 |
| Stores | identity-bound, atomic, resumable; one writer per store; every runner records its invocation and non-command environment/config provenance | Stage 6 |
| `technical_chain_complete=true` | a `measured` canonical pooled Full-Backtest whose source hash and run profile still match the current execution profile; it clears `open_work` only, not cohort or adjudication | Decision 2026-09-10 |
| Current usable population | the latest active `admitted_E1` adjudication set after C10. E0 is invalid historical provenance and never a fallback | Decision 2026-09-03 |

## Stage 0 — Corpus Collection (once, or when new repositories are added)

`python -m tools.harvest owner/repo` is the complete source-intake command. When it finds at least one new class, it regenerates execution profiles, classification, preregistered phase hypotheses, semantic duplicate evidence, duplicate adjudication, strategy status, and the status page in dependency order. These are source/report transformations only: harvest never starts a smoke run, bias diagnostic, full backtest, or performance-based decision. `--no-refresh` is the explicit batch-download escape hatch.

`python -m tools.adopt_source --url <file> --strategy <class>` is the intake for a strategy that was published without a repository: one file per explicit call, each agreed with the owner first (`--owner-approved`, refused before anything is downloaded without it), into `repos/<source>/`, with the same malware gate and the same AST check, an append-only provenance record beside the files, and the same intake refresh afterwards. An adopted strategy is admitted like any other - same duplicate adjudication, same representative rule, same population rules (`PIPELINE_EXTENSIONS.md` Part 5, decided 2026-09-24). `frequenthippo` is the only source tag allowed so far; a new one is a decision in that part, not an argument.

**One file per class name, and a measured one keeps its place.** `evidence/execution_profiles.py`'s `discover()` collects every file that defines a class name and then names one of them. It used to name the first one in alphabetical traversal, so a repository that sorts earlier took over the representation of strategies that had already been measured elsewhere: the row kept its `strategy_id` and silently changed its bytes. A representative that a measurement store names by content hash is therefore not replaceable by a same-named copy; a class name without a measurement keeps the traversal order, so an unchanged disk state still yields the same corpus. The stores read for this are the raw producers (`evidence/PROFILE_SMOKE.json`, `evidence/PROFILE_BIAS.json`, `evidence/PROFILE_FULL_WINDOW.json`, `results/regime/full_backtest_manifest.json`), never a derived read model - this decision is an identity input.

`python -m evidence.strategy_feed --write` records the newest posts from the FrequentHippo strategy feed as review-only leads. Each record retains its GitHub raw URL, repository, commit, path, content hash and local duplicate/class-name status. The feed is an automated discovery index, not an endorsement: it can contain fixtures, samples, mirrors and this audit's own copies. It never writes under `repos/`, invokes `harvest`, refreshes intake evidence, or starts a measurement. A reviewer must separately choose a source repository and explicitly run the normal harvest command; that later acquisition records the default-branch snapshot then available and remains subject to the malware gate and duplicate adjudication.

`python -m tools.frequenthippo_ranking` reads the ranking behind the same site's public backtest summary as a lead list: one rank per strategy, with the exchange and quote repetitions of one run collapsed and with identifiers the operator recorded separately but measured on identical trades merged into one entry that names its twins. It writes nothing and ends where the feed text ends - a reviewer names a source repository and runs harvest explicitly. A strategy that site publishes without any repository cannot be acquired by this stage at all; see the amendment of 2026-09-23.

For serial operational continuation after an intake refresh, use
`python -m tools.pipeline_dispatcher` to inspect the next eligible action or
`python -m tools.pipeline_dispatcher --watch --apply` to dispatch one
preregistered runner at a time. For one already-imported source, the explicit
`--strategy <id> --intake --apply` route regenerates the source-derived intake
views before selecting that strategy only. The dispatcher reads the published
pipeline state, refuses to overlap an active Docker runner, runs the existing
wrapper, refreshes published state, applies the existing E1 admission command,
and records routing provenance. It includes Stage 8b after a measured
Full-Backtest: a 5m detail run above 5m, or the documented at-or-below-5m rule
plus cost-screen publication. When no per-strategy work is left and the fingerprint of
its inputs changed, it runs Stages 9-13 for Model 0 (`tools/regime_evaluation.py`: labels
check, attribution, specialist evaluation, discovery comparison, daily returns, 5m totals,
the two published pages; `results/regime/regime_evaluation_state.json` records the last
complete run). It never dispatches gated Model 1/2/3 backtests, attribution or comparison
while they are owner-paused. It does not change a gate's selection rule,
repair policy, timeout, evidence store, or preregistered order. Repair-only
and zero-trade full-window cases are surfaced for escalation rather than
guessed.

If a prior dispatcher was interrupted after leaving its empty lock directory,
an operator who has first verified that no host-side audit process is active
may use `--recover-stale-lock`. It removes only an empty lock older than five
minutes and refuses recovery while a strategy-audit Docker container runs.

| Program | Reads | Writes |
|---|---|---|
| `tools/harvest.py` | GitHub API (only `.py` files with `IStrategy`) | Files under `repos/<repo>/` |
| `tools/census_repos.py` | `evidence/corpus_sources.json`, `repos/**` | Statistics on copy families (console/reference for `evidence/exclusion_criteria.py`s C-text) |
| `evidence/new_repo_candidates.py` | GitHub topic search, `evidence/corpus_sources.json` | `evidence/NEW_REPO_CANDIDATES.json`, `evidence/NEW_REPO_CANDIDATES.md` |
| `evidence/strategy_feed.py` | FrequentHippo post metadata and pinned GitHub raw files, `STRATEGY_STATUS.csv` | `evidence/STRATEGY_FEED.json`, `evidence/STRATEGY_FEED.md` |
| `tools/frequenthippo_ranking.py` | FrequentHippo Grafana table (anonymous datasource API) | nothing; one rank per strategy, printed for review |
| `evidence/repo_freshness.py` | local `git log` per repo, GitHub tip, `evidence/EXECUTION_PROFILES.csv` | `evidence/REPO_FRESHNESS.csv`, `evidence/REPO_FRESHNESS.md` |

Result of this stage: new rows in `evidence/EXECUTION_PROFILES.csv` (one row per strategy implementation, the canonical source for the rest of the chain).

## Stage 1 — Test Run (loads the strategy, checks if trading is happening at all)

| Program | Reads | Writes |
|---|---|---|
| `evidence/profile_smoke.py` | `evidence/EXECUTION_PROFILES.csv`, `evidence/PROFILE_CLASS1.json` (Repair Rules) | `evidence/PROFILE_SMOKE.json` |

The trial run is a fixed cascade: `20200301-20200401` (1 month); if it completes with fewer than 10 trades, `20200301-20200601` (3 months). It stops at the first rung with at least 10 trades and records every attempt. Policy id `fixed_1m_3m_until_10_trades_v2`: a low-trade result recorded under an older policy is deliberately stale and is re-cascaded the next time it is asked for. A runtime failure or timeout is not reinterpreted as a trade-count verdict by widening the window, and full-window evidence that already exists keeps priority over a smoke rung. Decisions: 2026-09-10 (cascade), 2026-09-15 (one-year rung dropped), 2026-09-06 (two fallback stores removed) — see the Decision record.

If the test run fails due to a specified, fixable obstacle (missing `timeframe`, missing local module, signature change of freqtrade/pandas/numpy), one of the following repair routes will take effect, after which stage 1 runs again for this line:

The explicit common entry point is `python -m repair.controller`. It plans by
default and runs selected Class 1/Class 2 writers serially only with `--apply`.
It records orchestration provenance in `evidence/REPAIR_CONTROLLER.jsonl`,
while each repair route retains its own evidence store and source identity.
The serial pipeline dispatcher does not invoke repair automatically: ambiguous
repair triage remains an escalation boundary.

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

Completed bias shards are not left as a manual follow-up. The Docker wrapper
automatically passes each successful non-canonical output to
`evidence.profile_bias_merge`, which verifies current strategy identity,
serializes concurrent shard completion, updates `PROFILE_BIAS.json`, and then
regenerates `STRATEGY_STATUS.csv`, `evidence/PIPELINE_STATE.json`, the supporting
status reports, and `strategy_status.html`. A direct canonical `profile_bias`
run performs the same publication step before it exits successfully.

Missing historical Smoke cards are reconciled by
`evidence/profile_smoke_backfill.py`. It may import only an identity-current,
measured canonical pooled Full-Backtest card, and marks that card explicitly as
reconstructed stronger evidence rather than pretending it was a short Smoke
run. Confirmed duplicate implementations and non-strategy fixtures receive
documented exemptions in `evidence/PROFILE_SMOKE_BACKFILL.json`. Every other
missing row remains in the real Smoke queue.
After that queue has run, `python -m evidence.profile_smoke_backfill
--finalize-run` replaces its queued dispositions with the canonical measured or
failed Smoke cards while preserving the original reconciliation population.

A native look-ahead finding of `FOUND` is a final information-leak exclusion (Decision 2026-09-11, order of the diagnostics). Neither the warm-up ladder nor Recursive-Bias runs afterward because they cannot repair an information leak.

The diagnostic interval is identical in both modes: `20200301-20200601` (Decisions 2026-09-09 and 2026-09-10). A stored futures run of only one month or a spot run over `20190101-20190401` is of historical provenance and must be superseded and measured again before a new decision.

An exception applies to the work queue (Decision 2026-09-10, closure): A successful canonical pooled Stage-8 full backtest closes the preceding technical verification chain for exactly the same implementation. `evidence/strategy_status.py` shows this as `technical_chain_complete=true` and then does not set `open_work` if the source hash and run profile match `results/regime/full_backtest_manifest.json`. This is not a retrospective E1 admission and does not override any documented exclusion; failed, OOM, or timeout Stage-8 attempts do not count as completion.

Regardless (Decision 2026-09-10, exclusions), each row with the cohort value `excluded` is a completed work case: it remains visible with its exclusion reason and evidence, but does not receive `open_work`. `exclusion_unconfirmed` is explicitly not synonymous with this; these not-yet-confirmed exclusions remain open until the missing decision evidence is available.

In addition, the owner decided on 2026-09-10 (Decision: non-testable canonical full backtests) for level 8: A previously approved strategy with `full_backtest_status`, `failed`, `resource_inconclusive`, or `timeout` is not testable for this benchmark and is finally excluded as C10 `full_backtest_not_testable`. These three states will not be rescheduled in the full backtest.

## Stage 3 — Warm-up Convergence Ladder after Passing Look-Ahead

| Program | Reads | Writes |
|---|---|---|
| `evidence/warmup_convergence.py` (`lookahead_pass`) | `evidence/EXECUTION_PROFILES.csv`, identity-linked Look-Ahead-PASS, repair stores | `evidence/WARMUP_CONVERGENCE.json` |

Only a look-ahead line with `PASS` can reach this stage. `NA` is not a pass and will not receive a follow-up measurement until the technical cause is clarified. The frozen convergence ladder is 1, 2, 7, 14, 30, 90, 365 days, converted into candles over its own timeframe, capped at the candles available before the window start. It is measured in one analyzer run; it is accepted at the smallest rung at which that rung and every larger one keep every indicator's absolute drift below 1.0 percent, not at the first crossing (Decision 2026-09-01; the settled value is the measurement, Decision 2026-09-02). A line is `converged`, `not_converged_within_ladder`, or `inconclusive`.

## Stage 4 — Final Recursive Bias after Converged Warm-up

| Program | Reads | Writes |
|---|---|---|
| `evidence/profile_bias.py` (`recursive`, native or Docker) | `evidence/EXECUTION_PROFILES.csv`, stored Look-Ahead-PASS and converged ladder with chosen initial value | `evidence/PROFILE_BIAS.json` |

The final Recursive-Bias run explicitly receives the ladder's smallest converged `chosen_startup_candle_count` as `--startup-candle`. Without a Look-Ahead `PASS` and a current converged ladder, the runner defers it. Thus neither an author's overly short declared value nor Freqtrade's standard warm-up can determine the final finding.

## Stage 5 — Data Coverage

| Program | Reads | Writes |
|---|---|---|
| `evidence/regime_coverage.py` | `evidence/EXECUTION_PROFILES.csv`, candle files under `user_data/data/binance` | `evidence/REGIME_COVERAGE.csv`, `evidence/REGIME_COVERAGE.md` |

Pure file system check (no Freqtrade execution), cached per `(mode, timeframe)` — inexpensive, safely reproducible at any time. It covers every row of `evidence/EXECUTION_PROFILES.csv`.

## Stage 6 — Merging

| Program | Reads | Writes |
|---|---|---|
| `evidence/strategy_status.py` | **everything** from level 0–5 plus `evidence/REGIME_ELIGIBILITY.csv` (invalidated historical E0 snapshot, exclusively provenance), `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` (active E1 decisions), `evidence/STRATEGY_CLASSIFICATION.json`, `evidence/MARKET_PHASE_HYPOTHESIS.json`, `evidence/BLOCKED_TRIAGE.json` | `STRATEGY_STATUS.csv`, `STRATEGY_STATUS.md`, **automatically in the same run**: `evidence/exclusion_criteria_list.md`, `evidence/repair_measures_list.md`, `RUNTIME_ENVIRONMENTS.md` |
| `evidence.pipeline_state.EvidenceStore` | all measurement, repair, Look-Ahead, Recursive-Bias, convergence, full-window, and canonical pooled Full-Backtest evidence stores | one resolved per-strategy interface used by `evidence/strategy_status.py`; `evidence/PIPELINE_STATE.json` is generated from that view |

A single call (`python -m evidence.strategy_status`) writes all published read
models and supporting reports, including `evidence/PIPELINE_STATE.json`. That
file is the one machine-readable operational memory: it gives each strategy's
resolved measurement and gate provenance, the remaining technical-chain queue,
and the canonical pooled Full-Backtest state. Raw JSON stores remain separate
writer-owned provenance and must never be counted individually to answer a
pipeline-wide question. `python -m evidence.pipeline_state --summary` prints
the current overview. `--check` checks whether generated state is current
without starting a measurement; `--selftest` runs consistency checks.

E0 is not a fallback option: its 67 old `regime_eligible=true` flags may not replace any check and may not allow any line. Only an active `admitted_E1` decision generates `cohort=E1_expanded`; the old E0 membership appears only in `gate_notes`.

## Stage 7 — Admission (Admission)

The protocol (populations E1/E2/E3, repair boundary, equivalence evidence, stop rule) is `PIPELINE_EXTENSIONS.md`, Part 1; the results of the waves it scheduled are in `evidence/ADMISSION_RECORDS.md`. The row-level decisions are `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`.

| Program | Reads | Writes |
|---|---|---|
| `evidence/eligibility_admit_converged.py` (current rule, `converged_clean_gates_v1`) | `STRATEGY_STATUS.csv`, `evidence/WARMUP_CONVERGENCE.json` | appends new `admitted_E1` lines to `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv` |
| `evidence/eligibility_expansion_adjudicate.py` (older Wave-B/C rules, `zero_warmup_analyzer_adapter_v1` / `native_gate_pass_v1`) | `evidence/ELIGIBILITY_EXPANSION_PROOFS.json`, `evidence/ELIGIBILITY_EXPANSION_WARMUP.json`, `evidence/ELIGIBILITY_EXPANSION_LOOKAHEAD.json`, `evidence/ELIGIBILITY_EXPANSION_EQUIVALENCE.json` | same `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`, plus `.md` report |

**Afterwards, mandatory back to level 6.** The admission decision is only available in `STRATEGY_STATUS.csv` when `evidence/strategy_status.py` runs again and reads back the extended `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`. A run of level 7 without a subsequent level 6 still shows the old status in `STRATEGY_STATUS.csv`.

## Stage 8 — Backtest over the full window

Two structurally different, both necessary measurements (see `REGIME_AUDIT_PLAN.md` §28.1) — neither replaces the other:

| Program | Purpose | Reads | Writes |
|---|---|---|---|
| `evidence/profile_full_window.py` (sharded in pairs) | Full-window confirmation (older code and comments call this "Stage 7"): does the strategy trade across the entire window, per pair | `evidence/EXECUTION_PROFILES.csv` | `evidence/PROFILE_FULL_WINDOW.json` (or shard files in parallel containers) |
| `evidence/merge_full_window_shards.py` | merges shards | `evidence/PROFILE_FULL_WINDOW_shardA.json`, `_shardB.json`, `_shardTF.json` | the canonical `evidence/PROFILE_FULL_WINDOW.json` |
| `regime/full_backtest.py` (pooled, `canonical_pooled_native_pair_universe`) | Phase A: actual performance backtest over all 8 pairs pooled | `STRATEGY_STATUS.csv` (E1 cohort) | `results/regime/full_backtest_manifest.json`, `full_backtest_native.json` |

`evidence/PROFILE_FULL_WINDOW.json` flows back into Stage 6 (`evidence/strategy_status.py` reads it for `observed_trades`/`trade_evidence`). The pooled backtest results from `regime/full_backtest.py` **do not** flow back into the approval — they are the data basis for Stage 10 (attribution) and Model 0 in Stage 12.

**Misunderstanding that suggests itself: 'Single pair' does not mean 'every pair fully measured.'** `evidence/profile_full_window.py` is a yes/no gate, not a performance measurement: it only answers 'does the strategy act over the entire window at all, for at least one pair?' As soon as ONE pair produces trades, the question is answered, and the rest of the pair list is no longer touched for this strategy (comment in the script header: 'One positive pair is sufficient to resolve a zero-trade smoke as positive... Sharding does not replace pooled performance backtests'). Only if ALL configured pairs produce zero trades does each one actually need to run through to confirm '0 trades' — which is why `evidence/PROFILE_FULL_WINDOW_shardA.json`/`_shardB.json` show fewer completed pair measurements for many strategies. as configured pairs, even though the strategy itself is already considered `measured`.

The actual completeness — every pair over the entire 6.5-year window, without interruption — is provided exclusively by `regime/full_backtest.py` (line above): it calls freqtrade without the `--pairs` filter, thus with the complete pair list together in a single backtest, and never terminates early.

**Performance limit instead of endless retry.** The 3600s timeout is a hard limit, not adjustable per strategy. `SuperHV27` and `Schism` each ran twice independently exactly up to the 3600s limit, without crashing and without OOM signature — the compatibility shims (`repair/compat_signature.py`) fixed the original crash, but the remaining per-trade costs over 8 pairs and 6.5 years are not enough for that. `evidence/POOLED_BACKTEST_PERFORMANCE_LIMIT.json` records this confirmation (rule: at least two independent timeouts, no other type of error in between); `regime/full_backtest.py` reads it and sets the status once to `performance_limited`, instead of consuming a full hour again on each container run. The strategy remains approved (`E1_expanded`) — it permanently only lacks the pooled performance metric for Stage 10.

**The same principle for confirmed memory shortage.** 52 strategies (BBRSI2/BBands/BinHV45-*/Cluc*-family, among others) were `resource_inconclusive` both under the original 13-14GB/`--workers 2` setting and afterwards, after increasing to 16GB VM memory with `--workers 1` on 2026-09-07 — a single process with the full memory budget, no concurrency left that could be blamed. This refutes resource contention as the cause; what remains is the strategy's own memory consumption over 8 pairs and 6.5 years. `evidence/POOLED_BACKTEST_OOM_LIMIT.json` records the confirmation, `regime/full_backtest.py` sets the status once to `oom_confirmed` instead of repeatedly trying endlessly. Here too: still allowed, just without the Stage-10 metric.

**Third category: unlimited stake growth.** `FastSupertrend_optim3_rsi_75lev` failed at 37% of the pooled run with `Stake amount 12570778.900608359 too high for XMR/USDT:USDT`. Cause: `runtime/profile_futures_config.json` sets `stake_amount: unlimited`; the strategy fixes leverage at 5× and lets profits run (`minimal_roi = {"0": 0.99}`). Over enough profitable years, the wallet grows exponentially until the calculated stake exceeds any real market liquidity. Unlike the first two categories, this is 100% deterministic: it is unrelated to memory, workers, or timing, and a retry reproduces exactly the same error at the same point. No earlier stage detects it: the smoke test uses the same configuration but only a one-month window, far too short for compounding to reach this scale, while Recursive-Bias and Look-Ahead-Bias test information leakage rather than capital scaling. `evidence/POOLED_BACKTEST_STAKE_OVERFLOW.json` records the confirmation; the same mechanism as above sets `stake_overflow_confirmed`. Whether other leveraged strategies carry the same risk was deliberately left open.

**Correction 2026-09-07: `evidence/profile_full_window.py` is not required for the entire E1 cohort, only for zero-trade candidates.** The citation above (`REGIME_AUDIT_PLAN.md` §28.1) does not support this claim — §28.1 addresses trade attribution versus gated performance (Phase A/B), not single-pair versus pooled backtests. The actual reason `evidence/profile_full_window.py` exists is stated in `evidence/strategy_status.py`: admission itself requires only `observed_trades != 0` from the smoke test (`evidence/eligibility_admit_converged.py` specifies no minimum, not even 10; this was checked across the repository despite a contrary recollection). The full 6.5-year window is mandatory only when the smoke test showed zero trades and a strategy might therefore be excluded (`full_window_measurement_pending`, only for `reason == "no_trades_in_full_measurement"`). Otherwise, a randomly quiet smoke-test month could unjustly exclude a strategy that does trade.

Sample on this date: **0 of 608 `E1_expanded` strategies have `observed_trades == 0`.** At that time, no admitted strategy needed this stage: all 571 strategies assigned to the `full-window-a`/`full-window-b` containers already had positive smoke-test evidence and needed no confirmation. `regime/full_backtest.py` (pooled and already running for the same cohort) also provides a more representative trade count for this majority because it shares the `max_open_trades` capital constraint across all pairs instead of isolating each pair. Both containers therefore stopped after all 571 assignments, with zero genuine zero-trade cases. Before any future cohort expansion starts `evidence/profile_full_window.py`, first check `observed_trades == 0` in `STRATEGY_STATUS.csv` and run it only for that subset.

## Stage 8b — Post-Full-Backtest: Execution Robustness and Cost Screen

Prospective and additive. It follows a measured canonical pooled Full-Backtest of exactly the same implementation and never changes admission or replaces `results/regime/full_backtest_manifest.json`. The binding definitions (thresholds, statuses, validity checks, the cost model) are in `PIPELINE_EXTENSIONS.md`, Part 2, Amendment 2026-09-19; the size and causes of the detail effect and the recommendation for future tests are in its Amendment 2026-09-20; this section only says what runs when. It is numbered 8b so that the stage numbers other files cite stay valid.

The dispatcher selects this stage for every E1 strategy whose identity-current
full backtest is complete and whose robustness status is `PENDING`. It runs a
5m detail backtest only above 5m; at or below 5m it rebuilds the execution
robustness and per-regime cost-screen stores under the owner rule. Publication
then refreshes the status table, allowing verified-specialist qualification to
be evaluated without changing E1 admission.

**Owner decision 2026-09-26: the full backtest always runs at 5m detail.** `regime/full_backtest.py` now defaults to `--timeframe-detail auto`: 5m detail candles for every strategy whose own timeframe is above 5m (`none` switches it off, only `auto`, `none` and `5m` are accepted for canonical output). Reason: 1m cannot practically be tested over a window this long, and 5m is the most practical solution; a run at the author timeframe alone is not a real result above 5m, because the order of events inside a candle is not resolved. *Not yet migrated:* measured canonical rows produced before this date stay valid (the identity check is unchanged), the Stage 8b rerun described above still exists as a second run for them, and no rerun has been launched. The *Regime Specialists* page already hides the author-timeframe figures above 5m, ranks and sorts by the 5m figures by default, and is in English.

Its accepted baselines include the owner-approved 5m OOM-recovery scope. Those
records keep their retained 1m OOM provenance, but their accepted 5m archive is
treated as already at the detail granularity for Stage 8b and is cost-screened
from that exact archive.

| Program | Reads | Writes |
|---|---|---|
| `regime/full_backtest.py --timeframe-detail 5m` (Docker wrapper `runtime/regime_full_backtest_docker.ps1`, serial) | the same strategy, profile, config, eight pairs and window as the canonical run | `results/regime/execution_robustness_detail_5m_docker.json` — always a separate output, never the canonical manifest |
| `evidence/execution_robustness.py` | the canonical manifest, the detail stores, their result archives under `user_data/`, the candle files (detail coverage), `regime_daily.csv` through `regime.attribution.attribute()` (regime cost screen) | `evidence/EXECUTION_ROBUSTNESS.json`, `evidence/COST_SCREEN.json` |

- **Above 5m: a rerun with 5m detail.** The strategy keeps its own timeframe; the detail candles only model execution inside the candle. The classifier compares the two runs and writes `PASS`, `SENSITIVE`, `NA` or `ERROR` (a sign flip, a profit change over 50 percent in either direction, or a trade-set change over 10 percent is `SENSITIVE`). `SENSITIVE` is a review marker, not an exclusion.
- **At or below 5m: no rerun.** Owner decision 2026-09-19, on resource grounds: such a baseline already simulates at the granularity the others are rerun at, so it counts as equal to a passed 5m run. It is a rule and not a measurement, and the record says so (`basis: owner_rule_at_or_below_5m`, published as `execution_robustness_basis`).
- **Cost screen, for every measured baseline, per ADX regime state.** The four DMI/ADX states, for BTC and for the traded coin, each judged on the trades that opened in that state, so a specialist that is strong in one state is not marked down by the states around it. Basis and floor are the specialist evaluation's own (fixed stake per trade, 10 trades), the window is the validation window from 2024-01-01. The whole-run result is kept as a description and does not gate.
- **`robustness_qualified`** is an execution `PASS` and a cost `PASS` in at least one state; the states are listed in `cost_screen_regimes_pass`. The designation for one claimed state must consult that state.
- **After every batch:** `python -m evidence.execution_robustness && python -m evidence.strategy_status && python -m tools.strategy_status_page`. `python -m evidence.execution_robustness --targets 5m` prints the command for what the 5m batch still owes.

Only the published *Regime-Spezialisten* page reads these results (`tools/regime_specialists_page.py`, 2026-09-20): it joins the annotation to every ranking row as a column and changes no ranking. The ranking CSVs under `results/regime/specialist_evaluation/` do not carry it. A row is a *verified* specialist only where the strategy clears the specialist floor and the annotation reads `PASS` for the claimed state.

## Stage 9 — Market Regime Classification

| Program | Reads | Writes |
|---|---|---|
| `regime/regime_engine.py` | local candle files | `results/regime/regime_daily.csv`, `regime_episodes.csv`, `regime_transitions.csv`, `regime_btc_episodes.csv`, `regime_state_summary.csv`, `regime_feature_distributions.csv`, `regime_manifest.json` |
| `regime/validate_regime.py` | the same `results/regime/regime_*.csv` | nothing (pure test, console output PASS/FAIL) |
| `regime/report.py` | the same files | `REGIME_DATA_REPORT.md` |

Generates the frozen 4-state model (BULL/BEAR/SIDEWAYS/TRANSITION from DMI(14)/ADX(14)) plus the raw data from which the six-phase extension (`bull_trend`/`bear_trend`/`range_quiet`/`range_choppy`/`transition`/`high_vol_shock`), which `regime/attribution.py` derives in Stage 10.

## Stage 10 — Attribution (per strategy/candidate, per regime/phase)

| Program | Reads | Writes |
|---|---|---|
| `regime/attribution.py` | `results/regime/regime_daily.csv`, `full_backtest_manifest.json`, `STRATEGY_STATUS.csv` (E1 cohort) | `results/regime/trade_regime_attribution.csv`, `strategy_btc_regime_summary.csv`, `strategy_regime_summary.csv`, `strategy_episode_summary.csv`, `strategy_phase_summary.csv`, `strategy_phase_episode_summary.csv`, `attribution_manifest.json` |
| `regime/gated_attribution.py` | `regime_daily.csv`, a complete `model1_backtest_manifest.json`, `model2_backtest_manifest.json` or `model3_backtest_manifest.json`, current E1 identities | per model in `results/regime/modelN_attribution/`: Trade attribution, five `candidate_*_summary.csv` and `attribution_manifest.json` |

`regime/attribution.py` accepts an accepted baseline of the canonical scope and of the owner-approved 5m scopes (`execution_robustness.ACCEPTED_BASELINE_SCOPES`); for the latter it expects the manifest row's `execution_timeframe` and, for a spot strategy, drops the trades that opened before the frozen spot window start of 2020-04-01 (`profile_full_window.TIMERANGE`), which the 5m recoveries of 2026-09-20 had been run over one month too early. The count removed is in `attribution_manifest.json`.

The two `*_phase_*` files (Six-Phase Model, Addendum 2026-09-05) were produced on 2026-09-14 from the same Model-0 attribution (`strategy_phase_summary.csv`, `strategy_phase_episode_summary.csv`); they read `regime/full_backtest.py`'s results (Stage 8). `trade_regime_attribution.csv` itself is a Git LFS object of about 1.3 GB; in a checkout without `git lfs pull` it is a pointer file, and `regime/attribution.py` recomputes it from the result archives. Whether a writer is currently running for this is determined solely by the checks in `HANDOFF.md`; this pipeline file is not a run status. The gated attribution by default rejects an incomplete candidate set; `--allow-partial` only generates a technical intermediate state explicitly marked as partial and is not a ranking release.

## Stage 11 — Hypothesis (independent, to be frozen before any evaluation)

| Program | Reads | Writes |
|---|---|---|
| `evidence/market_phase_hypothesis.py` | `evidence/EXECUTION_PROFILES.csv`, `evidence/STRATEGY_CLASSIFICATION.json`, `cluster/clusters.json` | `evidence/MARKET_PHASE_HYPOTHESIS.json` |

Must be written **before** anyone looks at the attribution results of Stage 10 — otherwise it is no longer a prediction (`REGIME_AUDIT_PLAN.md` §28.3). Already executed; is only read by `evidence/strategy_status.py` (Stage 6), never decided anew.

## Stage 12 — Benchmark: Model 0/1/2/3

After the expansion frozen on 2026-09-07 before each productive gate run, four comparison levels per strategy:

- **Model 0 — measured, attributed and evaluated.** "Original strategy, no regime filter" is exactly what `regime/full_backtest.py` (Stage 8) calculates: the ungated, pooled backtest across all 8 pairs. It is attributed in Stage 10 and evaluated in Stage 13 for the whole Model-0 inventory. The resumable call `python -m regime.full_backtest` continues the measurement; ongoing writers are excluded according to `HANDOFF.md`.
- **Model 1 — has run on candidate sets, not on the whole corpus.** `regime/gated_backtest.py --model model1` filters entries according to the BTC states explicitly mentioned in the candidate spec. Global BTC states remain available even if no local daily line exists for a delisted coin.
- **Model 2 — has run on candidate sets, not on the whole corpus.** `regime/gated_backtest.py --model model2` filters entries exclusively based on the explicitly specified local coin states. It does not read or require any BTC state. If the local state is missing, the gate closes.
- **Model 3 — has run on candidate sets, not on the whole corpus.** `regime/gated_backtest.py --model model3` is the previous combined Model-2 logic: Entries require both an allowed global BTC state and an allowed local coin state. Exits remain completely with the original strategy in all three gate models.
- **The technical comparison of the four levels has run for the 7 pilot candidates.** `regime/model_compare.py` checks identical candidates, Model 3's agreement with Model 1's BTC-Gate and Model 2's Coin-Gate, time windows, identities, and archives before it places the four runtime metrics side by side. It writes `model_metrics_long.csv`, `model_comparison.csv`, and `model_comparison_manifest.json`, but does not sort or rank any strategy. The mechanical deltas are Model 1 minus 0, Model 2 minus 0, Model 3 minus 0, Model 3 minus 1, and Model 3 minus 2; Model 2 minus Model 1 is not output as an incremental effect because the two individual gates are not nested within each other.

Gate runs to date, from the manifests under `results/regime/` (2026-09-19). Each row is one candidate spec; the three model columns give the entries of that model's manifest.

| Candidate spec (`candidate_set_id`) | Role | Candidates | Model 1 | Model 2 | Model 3 |
|---|---|---|---|---|---|
| `pilot_v1_stratified_trend_gate` | PILOT | 7 | 7 measured | 7 measured | 7 measured |
| `pilot_v1_stratified_sideways_transition_gate` | PILOT | 14 (7 strategies) | 14 measured | 14 measured | 14 measured |
| `regime_specialists_v2_lcb_ranked_deduplicated` | PILOT | 33 (25 strategies) | 33 measured | 33 measured | 33 measured |
| `top10_v1_regime_specialists_trend_gate` | VALIDATION | 55 | 16 measured | not run | not run |
| `full_v1_trend_gate` | VALIDATION | 647 | 128 entries: 113 measured, 10 failed, 5 timeout | 184 entries: 151 measured, 28 failed, 5 timeout | 206 entries: 165 measured, 36 failed, 5 timeout |

The `full_v1` and `top10_v1` runs are partial. The `*_merged` attribution folders combine the manifests of several runs; the specialist evaluation has been applied to each model's attribution (`results/regime/specialist_evaluation/modelN/`, and `modelN_regime_specialists_v2/`).

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

Status: run on the full Model-0 inventory (629 strategies on 2026-09-20) and on the Model 1/2/3 attributions of the candidate sets above; the results are published as the *Regime-Spezialisten* page (`python -m tools.regime_specialists_page`), which also writes the separate *Gating-Hypothese* page (Model 1/2/3 snapshots). The whole-window table sets the author-timeframe result beside the 5m rerun of Stage 8b; the rerun's validation trades are priced by `python -m regime.detail_totals` with the evaluation's own functions (`--check` reproduces the baseline figures). `python -m regime.daily_return` adds the daily return per market phase (on employed and on provided capital, and for Buy-and-Hold); the page shows it after slippage and derives the phase portfolio from it by a stated rule. Descriptive: no ranking changes. The floor and the ranking rules below are fixed; the rankings themselves are recomputed whenever the results change (`python -m regime.attribution`, then `python -m regime.specialist_evaluation`, then `python -m regime.discovery_comparison`). The last one runs the same evaluation on the discovery window (trades opened before 2024-01-01) and sets it beside the validation result per strategy and phase; it is descriptive, selects nothing and changes no ranking. It also derives the *confirmed* label and the confirmation score (both lower confidence bounds above 0 in both windows; the smaller bound is the score) and, for universal candidates, the strict or mild confirmation rule, frozen in `REGIME_PREREGISTRATION.md`, Amendment 2026-09-20. A row is called a *verified* specialist only when it clears the specialist floor **and** the strategy passes Stage 8b for the claimed state (`evidence.execution_robustness.qualifies_in` / `qualifies_universal`); the page shows that as the *Robustheit* column and changes no ranking.

| Program | Reads | Writes |
|---|---|---|
| `regime/specialist_evaluation.py` | a `trade_regime_attribution.csv` (model 0 canonical, or a `modelN_attribution/` file), candle data under `user_data/data/binance` | `results/regime/specialist_evaluation/`: `btc_specialist_table.csv`, `coin_specialist_table.csv`, `btc_specialist_ranking.csv`, `coin_specialist_ranking.csv`, `universal_strategies.csv`, `strategy_total_dollar_gain.csv`, `evaluation_manifest.json`. **Runs in the audit runtime image**, not on the host: `runtime/regime_evaluation_docker.ps1` (the dispatcher's `regime_evaluation` gate uses it), because the host can lose TA-Lib to Windows application control. **Owner rule 2026-09-26:** at the end of every job that sends strategies through the check chain, run it (`powershell -File runtime/regime_evaluation_docker.ps1`), so the newly measured strategies appear in the ranking. |

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

## Decision record for Stages 0-8

The dated owner decisions that fixed the rules above. Until 2026-09-20 they were amendments in
`REGIME_PREREGISTRATION.md`; the text below is unchanged and the wording "this document" inside an entry means the
preregistration it was written in. Each was made prospectively (before the rows it affects were re-measured, and
never from profit or regime performance). The stage sections say what the rule is today; an entry says why it was
made and what it replaced. Where a later entry supersedes an earlier one, the earlier one says so or is named here.

| Date | Decision | Stage |
|---|---|---|
| 2026-09-01 | Warm-up convergence ladder, acceptance rule and scope | 3, 4 |
| 2026-09-02 | The settled warm-up is the measurement; paired run no longer an admission gate | 3, 4, 7 |
| 2026-09-03 | Spot analysis window starts 2020-04-01 | 5, 8 |
| 2026-09-03 | E0 retired as a cohort | 6, 7 |
| 2026-09-03 | Table parser and case-colliding log paths | 3, 4 |
| 2026-09-06 | Two fallback stores removed (housekeeping, no owner decision) | 1 |
| 2026-09-09 | Futures recursion window becomes three months | 2, 3 |
| 2026-09-10 | Fixed smoke trade-count cascade | 1 |
| 2026-09-10 | Identical Spot and Futures bias windows | 2, 3 |
| 2026-09-10 | Completed full backtest closes technical work | 6, 8 |
| 2026-09-10 | Exclusions close the work queue | 6 |
| 2026-09-10 | Non-testable canonical full backtests are excluded (C10) | 8 |
| 2026-09-11 | Look-ahead, then warm-up ladder, then final recursive-bias | 2, 3, 4 |
| 2026-09-15 | Smoke cascade drops the one-year rung | 1 |
| 2026-09-16 | "Frozen file" description of REGIME_ELIGIBILITY.csv dropped | 6 |
| 2026-09-22 | FrequentHippo feed added as a pinned, review-only discovery source; no automatic acquisition or measurement | 0 |
| 2026-09-23 | One verdict vocabulary for every evidence store; identity inputs guarded against silent change | 1-8, 13 |
| 2026-09-23 | FrequentHippo ranking added as a second review-only Stage-0 reader; a published strategy without a repository has no intake path | 0 |
| 2026-09-24 | A representative that carries a measurement is not replaced by a same-named copy from another folder | 0 |
| 2026-09-24 | A strategy published without a repository enters `repos/<source>/` through one explicit adoption command and is admitted like any other | 0 |
| 2026-09-24 | A commit date is only called a revision's date where the repository has a history of its own; where one date dominates (>= 90 % of >= 5 dated files) it is named an import, and so is every cell that carries it | 0 |
| 2026-09-24 | Every single adoption is agreed with the owner first; there is no standing permission to adopt | 0 |

### Amendment 2026-09-22: FrequentHippo strategy feed is discovery-only

**Owner's decision.** The public FrequentHippo strategy feed is added to Stage 0 because it exposes a dated GitHub raw URL and commit for newly indexed Python files. The feed is not a curation or validation service: it includes test fixtures, samples, baseline strategies, duplicate class names, and mirrors of this audit. Its presence therefore cannot change technical eligibility, a source hash, a run profile, a candidate wave, a repair decision, or a benchmark queue.

`evidence.strategy_feed` may write only the review inventory. It records the post metadata, the immutable upstream reference, a SHA-256 of the fetched bytes, the IStrategy classes parsed without execution, and a comparison against the current corpus's source paths and class names. A `candidate_requires_review` record means only that a distinct IStrategy class was observed outside known paths and names. It is neither a quality verdict nor an import instruction.

Only an explicit subsequent `python -m tools.harvest owner/repo` can acquire source files. That command remains the sole Stage-0 writer below `repos/`, retains the existing malware gate and dependency closure, and performs the existing duplicate adjudication. Because harvest reads the repository's then-current default branch, it is intentionally a new, reviewable acquisition event rather than an attempt to silently replace the feed's pinned revision.

### Amendment 2026-09-23: the ranking is a lead reader, and a published strategy without a repository has no intake path

**Owner's decision.** The ranking behind the same public backtest summary joins Stage 0 as a second review-only reader, next to the feed. It exists because the feed answers "what appeared" and the ranking answers "what scored well for someone else" - and neither is evidence. `overall_score_percent` depends on another operator's data, pairlists, cost model and scoring; this audit neither controls nor reproduces any of it. The reader therefore writes nothing, no stage reads it, and a rank from it can never appear as a verdict, a cohort, an admission argument or a repair trigger.

`tools/frequenthippo_ranking.py` removes the two kinds of repetition that make the published table unusable as a list. A strategy measured on several exchanges and quote currencies becomes one rank, keeping its best row. Two identifiers the operator recorded separately but measured on identical trades become one strategy, named with its twins. The second merge uses the same "identical values, no similarity threshold" test `evidence/semantic_duplicates.py` applies to this audit's own stores, applied to someone else's numbers, and it is reported in its own `trade_twins` column so the two kinds of repetition stay distinguishable.

Two consequences are rules, not events. First, a ranking is a lead list: naming a candidate is not examining it, and the decision to look at one is taken with `evidence.strategy_feed` (pinned revision) and executed only by an explicit `python -m tools.harvest owner/repo`. Second, a strategy that the site publishes *without* a GitHub repository - its own published files live under `/wp-content/uploads/strategies/` - cannot be acquired by any route this stage allows: harvest reads the GitHub API, and nothing else may write below `repos/`. Adopting such a file needs a new, explicitly decided intake path for non-repository sources; until the owner decides that, such a strategy stays a lead and is reported as one. The draft for such a path is `PIPELINE_EXTENSIONS.md` Part 5, which is proposed and not a rule.

### Amendment 2026-09-24: a representative that carries a measurement keeps its place

**Owner's decision, after an observed defect.** Resolving ten leads of that ranking ended in one harvest of `remiotore/ccxt-freqtrade` (2026-09-23) which brought 2393 class names, of which 520 were already in the corpus under the same name. The plain duplicate work happened as designed - the intake removed 509 freshly downloaded copies that had an identical code digest elsewhere - but the wave also did something nobody had asked for: for 45 `strategy_id`s whose class name already existed, the representative moved into the new folder, 39 of them to a *different revision*, and 22 already-admitted rows lost `technical_chain_complete` although no measurement had failed. Alphabetical precedence had silently re-pointed rows at bytes their measurements never saw.

**The rule.** `evidence/execution_profiles.py`'s `discover()` may only choose among files that exist, and among those it prefers the file a measurement store names by content hash; a copy that no store names cannot displace it. The stores consulted are the raw producers - smoke, bias, full window and the pooled Full-Backtest manifest - because this choice feeds identity and identity must not be derived from a summary of itself. A class name with no measurement keeps the old, purely deterministic rule (first occurrence in alphabetical traversal), so the same disk state still produces the same corpus. The `EXTRA_SUBCLASS_STRATEGIES` entries join the candidate list instead of being dropped once a class is found elsewhere; without that, the file a measurement had run on was not even a candidate (`TrailingBuyStrat2`, `NASOSv5_antipump`, `ClucHAnix_5mTB1`).

**What it replaced, and what it costs.** It replaced "first occurrence wins", which was simple and reproducible but not *stable*: every intake of a repository that sorts earlier rewrote the representation of strategies the audit had already paid for. The cost is that a genuinely better or newer revision of an already-measured strategy no longer takes over by itself; that is now an explicit decision, which is what it should always have been. Measured after the change on the same wave: lost `technical_chain_complete` rows 22 -> 0, changed pre-existing profile rows 45 -> 19 (those 19 point at the implementation their measurements ran on).

### Amendment 2026-09-23: one verdict vocabulary, and a guard on the identity inputs

**Owner's decision.** Until now every reader decided for itself which spellings of an outcome meant the same thing:
`PASS`/`FOUND`/`NA` in the check stores, `measured`/`timeout`/`failed`/`oom_confirmed`/`performance_limited` in the
manifests, `converged`/`no_usable_ladder` in the ladder, `eligibility_status` in the regime stores. Each reader module
carried its own list, so a new value from one writer could change a published count with no test noticing. The owner
asked for one closed schema instead of a per-reader convention.

`evidence/verdicts.py` holds it, and it is a read-side layer only: it changes how a result is *described*, never which
inputs were measured. No store changed shape, no runner changed what it writes, no identity changed, and no measurement
was repeated. The layers, the four rules, the mapping and the `UNKNOWN` sentinel are in that one file, and
`evidence/README.md` states them; this entry only records why the schema exists and what it replaced. Where a reader
deliberately keeps a raw token instead of the normalized value, that line says why.

`evidence/PIPELINE_STATE.json` gains `strategies.<id>.evidence_resolution.verdicts`: the five layers in a fixed
six-gate order (`measurement`, `lookahead`, `recursive`, `full_backtest`, `execution_robustness`, `cost_screen`), each
gate a bare string when its value satisfies the layer and `{value, reason}` when it does not. A reason is carried only
where there is one, because a reason on a satisfying value is noise.

Two guards join the verify chain, because the boundary between a verdict and stored evidence is the identity hash - a
status word must never enter one, and an identity input must never change unnoticed:

- `tools/identity_freeze.py` fails the build when an identity input changes: the key set of each identity function, the
  policy tokens that are hashed into records, and the parameters hash of the detail classifier. Adding a key stays
  allowed, but it has to be added there too, which is where the cost of re-measuring that store is written down. The
  guard reads those functions with `ast` and never imports them, because they need real data.
- `tools/verdict_migration_audit.py` counts the tokens actually present - in the JSON stores and in both published CSV
  verdict columns - and names every `(store, field)` that still needs a decision. It reads only.

`python -m evidence.strategy_status --check` and `python -m tools.strategy_status_page --check` now also verify the two
reports with handwritten timestamps and the published page against their sources, and the automatic finalizer treats a
stale page as a failed finalization rather than as an ignorable post-processing warning: a stale published page is a
wrong verdict shown to a reader.

### Frozen warm-up convergence amendment

Authorized by the owner on 2026-09-01, before any strategy-by-regime ranking
was generated or inspected. It governs a new admission route. Its contemporary
promise that E0 would remain a valid untouched cohort was superseded on
2026-09-03 after E0's missing checks were discovered.

**The problem it solves.** The recursive gate asks whether an indicator's value
depends on how much history was loaded. Answering it requires a warm-up, and
the warm-up value used so far was the longest literal indicator period found in
the source. That heuristic is demonstrably wrong in three ways already
recorded: it read a minimum instead of a maximum (`Strategy004`), it carried a
period across timeframes without conversion (`Cluc4`, `BB_RPB_TSL`), and it
ignores that a recursively smoothed indicator never forgets its seed. Setting
the warm-up equal to the period leaves roughly `e^-2` of the seed for a
standard EMA and `e^-1` for Wilder smoothing - 13.5 and 36.8 percent. Measured
confirmation: `pmaxTest` with warm-up 112 still drifts 4.5 percent on `rsi_112`.

**The rule, fixed here before it is run.**

1. Ladder, in calendar days: 1, 2, 7, 14, 30, 90, 365, converted to candles
   through the strategy's own timeframe and capped at the candles actually
   available before the frozen window start for that pair basket. Days rather
   than multiples of the file-derived period, because that period is the thing
   that keeps being wrong; a ladder anchored to it inherits its errors, while a
   day is the same span of market history for every strategy. The ladder
   reaches a year because 30 days is 30 candles at a daily timeframe and cannot
   settle an EMA200. Rungs that collapse onto the same candle count are not run
   twice.
2. Acceptance: freqtrade `recursive-analysis` reports no indicator whose
   absolute drift reaches **1.0 percent**.
3. The chosen value is the smallest rung at which that rung AND every larger
   rung in the table stay inside the band. Not the first crossing: a drift
   curve does not fall monotonically. `SmaRsiStrategy` reports 0.588 percent
   for `rsi` at 14 candles, then 4.262 at 25 and 1.718 at 30 before settling
   near zero at 90. Taking the first value under the band would pick 14, where
   the indicator is plainly not settled; convergence means it stays settled.
   Among the rungs that qualify, the one with the smallest worst-case drift is
   taken, and an exact tie keeps the smaller warm-up. Every candidate has
   already cleared the band at its own value and at every larger one, so this
   choice cannot pass or fail a row; it only selects the warm-up at which the
   indicators are most settled. Choosing the smallest drift across ALL rungs,
   qualifying or not, is inadmissible: it would pick the value that flatters
   the test statistic, and on a non-monotone curve it lands on a crossing.
   There is no per-row search beyond the ladder.
3a. The whole ladder is measured in ONE analyzer run. `recursive-analysis`
   accepts the startup values to test and prints one column per value, plus a
   column for the strategy's own declared warm-up. The declared value is
   therefore never overridden: it is read as its own column, which is what
   makes requirement 6 below decidable.
4. A row where no ladder value satisfies acceptance is terminal for this route.
5. Acceptance is not admission. A chosen value must additionally survive the
   paired full-window run: identical trade list, identical `trades_sha256`,
   against the strategy as declared. Coverage `PASS`, trap-free,
   `artifact_role=strategy` and not `behavior_changed` continue to apply.
6. A row whose settled value is at or below the author's own declared warm-up
   needs no override at all. It was excluded by a defect in this audit's
   parser, which read the wrong table column, and admitting it requires neither
   a changed warm-up nor the wider band. Such a row is recorded as
   `needed_no_override` and is reported separately, because it is a correction
   rather than a relaxation.
7. A row that converges but whose trade list changes is **E3 exploratory**, not
   E1. The fix altered behaviour, which is a finding, not an admission.
8. Rows admitted through this route carry the label `convergence_warmup_v1` so
   every result can be reported with and without them.
9. Every admitted row records its chosen warm-up, the ladder step it came from,
   the complete drift table it was decided on, the drift at the author's own
   declared warm-up, the largest remaining drift and the indicator carrying it,
   and the trade count the equality was established over. The trade count is required because
   equality over eight trades and equality over 1,845 are not comparable
   evidence, and a reader must be able to see which one a row rests on.

**What this relaxes, stated plainly.** The frozen Stage 6 gate treats any drift
above 0.01 percent as recursive bias. This route accepts up to 1.0 percent, a
hundredfold wider band, and 545 of the 900 rows were excluded by that gate. The
preregistration's own sentence that eligibility thresholds are not relaxed no
longer holds without qualification, and this paragraph is that qualification.
The justification is that 0.01 percent is unreachable in principle for any
recursively smoothed indicator, so the old gate did not separate careful
strategies from careless ones; it separated strategies that use an EMA from
strategies that do not. Requirement 5 partly offsets the wider band, and its strength must not be
overstated. An identical trade list constrains decisions rather than
intermediate values, and decisions are what this study measures. It is not,
however, a stricter criterion than a drift bound, and the two are not ordered.
A five percent drift can leave every trade unchanged when no signal sits near a
decision threshold, and a hundredth of a percent can flip one when a signal
does. It is evidence about this timerange and this pair basket, not a property
of the computation. It is weakest exactly where evidence is already thinnest: a
row with eight trades has almost no opportunity to differ, while one with 1,845
has many.

This audit already contains the decisive counterexample. In Wave B,
`Combined_Indicators` and `CombinedBinHAndClucHyperV0` matched the original
trade list exactly and were still refused, because their decisions rest on
`ta.EMA`, which never fully forgets its seed. Exact trade equality admitted
precisely what the recursion reasoning caught. Each requirement therefore
covers a failure the other misses, which is why both are required and neither
is described as the guarantee.

**Scope.** Every row whose sole hard exclusion reason is `recursive_bias_found`
- 440 rows once the profiles already admitted to E1 are removed, of which 124
are Wave D, 242 were never scheduled and 74 are the Wave B remainder. Rows
carrying a second hard reason are deliberately excluded: 35 also record
`lookahead_found`, 17 a technical trap and 43 no canonical measurement, and no
warm-up changes any of those. Processing order is fixed here, not chosen from
results: Wave D, then the unscheduled rows, then the Wave B remainder.

**Historical clause, superseded 2026-09-03.** At adoption, E0 was to remain the
frozen 67 and be reported beside every result. It is retained only as an
immutable record of that mistaken Stage 6 classification and must not enter any
current result. Former E0 members require independent E1 admission.

### Amendment 2026-09-02: the settled warm-up is the measurement

**Owner's decision, recorded before the rows it affects were admitted.**

Requirement 7 above routed a converged row whose trade list changed under the
supplied warm-up to E3 exploratory rather than E1, on the ground that the fix
altered behaviour. **Requirement 7 is retired.** So is requirement 5's paired
full-window run as an admission gate.

The reasoning, in the owner's terms. This audit ranks working strategies by
market phase; it is not an attempt to reproduce what an author once ran. Many
of these strategies were written before indicator drift was widely understood,
and their declared warm-ups do not let their own indicators settle - 226 of the
354 candidates declare a value below the one at which their drift disappears,
some by a factor of seventy. A result computed at such a warm-up was not
correct when the author computed it either. What is wanted is the
mathematically clean result: no recursive drift, no look-ahead, under the
current freqtrade. That a clean warm-up yields fewer trades, or more, is the
consequence of measuring properly and not a defect in the row.

**What this costs, stated plainly.** The paired run was the only test that
separated "repaired" from "reconfigured". Of the 26 rows it has already
decided, 13 produced an identical trade list and 13 did not - `SlowPotato`
1,835 against 1,899, `JuicyTrend` 13,698 against 13,607, and two rows with the
same count and a different checksum. Under this amendment all 26 would be
admitted alike. A reader of a market-phase result therefore cannot assume the
number is what the author's own configuration would have produced, and for
roughly half of them it is not.

**What is kept so that cost stays visible.** Every admitted row records the
warm-up it was measured at, the ladder step, the drift, and whether that value
is at or below the author's own declaration (`needed_no_override`). Two of the
354 need no supplied warm-up at all; 126 declare none, so freqtrade's recursion
analyzer refuses them outright and a value had to be supplied before the gate
could run at all; 226 declare a value that runs and was overridden by ours.
Where the paired run has already produced a verdict it stays on the record as
provenance. None of this decides admission any more; all of it decides how a
number should be read.

**What is unchanged.** The amendment is about warm-up and nothing else. A row
still needs a look-ahead `PASS` measured from its own implementation - an `NA`
is no verdict and admits nothing - recursion settled by the ladder, coverage
`PASS`, `traps_n` zero, `artifact_role=strategy`, and not `behavior_changed`.
Three rows that clear both bias gates are held by a documented backtesting
trap, which is not a warm-up question.

Implemented by `evidence/eligibility_admit_converged.py` under ruleset
`converged_clean_gates_v1`; every row it admits carries that ruleset, so any
result can still be reported with and without this amendment.

### Amendment 2026-09-03: the spot analysis window starts a month later

**Owner's decision**, on a finding from the warm-up ladder's own coverage.

The convergence ladder tests warm-ups up to 365 days, but its ceiling is
capped by whichever of the eight basket pairs has the least history before
the analysis window starts - a warm-up the ladder accepts is later reused as
`startup_candle_count` in the full-window run across all eight pairs, and a
value that exceeds one pair's available history would silently shorten that
pair's measured span rather than fail loudly.

`DASH/USDT` was listed on Binance 2019-03-28, the latest of the eight. At the
original window start of 2020-03-01 that left 337 days of prefix history -
short of the 365-day rung by four weeks. Not one of the 62 strategies the
ladder could not settle, across both the original and the `shim5`-widened
runs, was ever offered that rung. Two converged the moment `shim5` let them
reach 90 days at all; the rest sat at whatever their timeframe's nearest
reachable rung was, some worse off there than at 14 days, because drift
against the full-history reference is not monotone in the warm-up.

**The spot window now starts 2020-04-01**, not 2020-03-01. `DASH/USDT` then
carries 370 days of prefix, clearing the 365-day rung with a few days to
spare; `XMR/USDT`, the second-latest listing, clears it with more. The cost
is 31 days off a 6.5-year window, under 0.5 percent, and current for only 18
strategies' full-window measurements at the time of the change - the
market-phase benchmark itself had not yet started.

**The futures window is untouched, and stays at 2020-03-01.** Futures pairs
were listed later still - the last, `DASH/USDT:USDT`, on 2020-02-04 - so
matching fix would need a start of 2021-02-04, cutting eleven months from the
whole futures window to help fourteen strategies. Declined: those fourteen
are capped by history that will never arrive on this exchange, which is a
fact about the pair's own listing date, not a choice this audit is making.
Their reason names that rather than folding it into a bias verdict.

Implemented in `profile_full_window.TIMERANGE` (now `{"spot":
"20200401-20260821", "futures": "20200301-20260821"}`) and
`warmup_convergence.WINDOW_START` (now `{"spot": "2020-04-01", "futures":
"2020-03-01"}`), which the ladder's ceiling and the full-window run must
agree on - the same reasoning as the `shim5` amendment: a warm-up accepted
under one window and applied under another can silently shorten a pair's
span. The `recursive-analysis` and `lookahead-analysis` diagnostic windows
(`profile_bias.WINDOWS`) are a separate, shorter measurement and are not
affected - those checks are forced onto `BTC/USDT` alone by freqtrade itself,
for which `DASH/USDT`'s listing date is irrelevant.

### Amendment 2026-09-03: E0 is retired as a separate cohort

**Owner's decision**, on a finding from re-measuring the frozen 67 for the
first time in this audit's own runtime.

E0 was frozen on 2026-08-30 as a reproducibility anchor: "E0 is untouched. It
remains the frozen 67 and is reported beside every result." The intent was
sound - keep one unmoving reference point while the eligibility expansion
ran. The consequence, only visible once E0 was finally measured here, was
not: E0's own recursion-bias standing had never rested on this audit's
methodology at all.

The Stage 6 sweep that produced the 67 ran `recursive-analysis` without
`--startup-candle` (`harness.py`, commit `be77d12`, 20.08; the same command
is item 1 of `CHECKLIST.md`, commit `4d5a937`, the same day). Freqtrade then
falls back to its own hardcoded default - five fixed candle counts (199,
399, 499, 999, 1999), the same five regardless of a strategy's timeframe,
plus whatever the strategy's own `startup_candle_count` declares. A one-day
strategy tests up to 1999 days of history that way; a five-minute strategy
tests under seven. Whether the resulting table showed "near-zero variation"
was never asked in calendar time, and never checked against a longer warm-up
in case a false plateau was sitting in front of a real one - the exact
failure this audit's own convergence ladder exists to catch (`BigZ04`'s
`bb_lowerband_1h` sits at a flat 3.63% from 200 through 8640 candles, then
jumps to -12.88% at 90 days).

Measured under this audit's own ladder for the first time this week: 64 of
67 hold up cleanly under both checks. One, `MacdStrategy`, does not - 1.07%
residual drift at the largest warm-up the data supports (365 days, after the
2026-09-03 window amendment), just outside the 1% band. Two, `BuyRegions`
and `StochRSITEMA`, had been misread by a defect in our own table parser
(see below) rather than measured at all.

**E0_strict67 is retired and invalid as a cohort.** The 67 are no longer
admitted by having been in the original Stage 6 corpus; each must complete the
same current audit chain as every other strategy, including current-runtime
measurement, the C1-C4 exclusions, convergence, coverage, trade evidence,
artifact role, and repair provenance. No E0 flag may skip a check or serve as a
fallback verdict.
Membership in the original frozen set is kept as provenance on the row
(`gate_notes`), never as a reason to skip a check or override a finding.

`MacdStrategy` moves to `excluded` under C2. The other 66 were subsequently
admitted independently under `converged_clean_gates_v1`; their usability comes
from those 66 row-level E1 decisions, never from former E0 membership.

### Amendment 2026-09-03: a second reader defect, corpus-wide

While re-measuring E0's recursion drift, `StochRSITEMA` came back
"inconclusive: no drift table" despite its stored log showing a complete,
readable 76-row table. The cause: `recursive_table()`'s row-name filter
required a bare Python identifier (`[a-zA-Z_0-9]+`) and silently dropped any
row whose name did not match - `rsi(14)`, `stoch-slowk`, `BBB_20_2.0`,
`1h-rsi`, `50 SMA`. 68 stored logs across the corpus carry at least one such
row; some were misread as having no table at all, others as `converged` on
an incomplete table that never showed the very indicator whose name could
not be parsed.

Fixed in `profile_bias.recursive_table()`; re-derived from stored logs via
`tools/warmup_reparse.py --store punctuated`, applied only where the reading grew
richer (58 records) and never where it would have shrunk, which is the
signature of a different defect entirely (below).

**A related, independent defect surfaced during the same re-read.** Ten
pairs of strategy IDs in the corpus differ only in case - `SuperTrend` and
`Supertrend`, `BBRSI` and `bbrsi`, `mabStra` and `MabStra`, among others -
genuinely different strategies from different source files. The path
construction used for per-strategy logs and isolated source directories
(`profile_smoke._safe`) preserved case but did not otherwise disambiguate,
and this filesystem folds case, so both members of every such pair wrote to
the identical path. Whichever ran later silently overwrote the earlier one's
log. `_safe` now appends a short hash of the exact-cased name, so no two
different strategy IDs can ever collide again; already-written `debug_log`
paths are untouched, since nothing regenerates them to look a file up.
Records whose log the punctuation fix would have shrunk (`SuperTrend`,
`bbrsi`, `hlhb`, `MACDStrategy`, `MacdZeroCrossStrategy`) are queued for a
fresh, collision-safe run rather than reparsed from a log that no longer
describes them.

### 2026-09-06 housekeeping: two fallback stores removed (Stage 1)

`ELIGIBILITY_NEVER_RUN.json` and `ELIGIBILITY_TRAP_SMOKE.json` were one-time fallback stores from previous waves (no runner in the current repo rewrote them) — 65 of the 83 lines in them had no separate `evidence/PROFILE_SMOKE.json` entry, `evidence/strategy_status.py` fell back to these two files for them. Caught up via targeted `evidence/profile_smoke.py --strategy ... --profiles spot_long futures_long unknown` (empirically checked: previously 65 of 83 lines in `STRATEGY_STATUS.csv` changed if the files were omitted, afterwards not a single one) and removed both files, including the fallback loop in `evidence/strategy_status.py`.

### Amendment 2026-09-09: three-month Futures recursion window

**Owner's decision**, before the affected Futures recursion exclusions were
retested. The native Futures recursive-bias diagnostic and the warm-up
convergence ladder now use `20200301-20200601`, three calendar months, instead
of `20200301-20200401`. Spot remains `20190101-20190401`, also three months.

The earlier asymmetry was inherited mechanically: the Spot window came from
the predecessor bias harness, while Futures reused its one-month smoke-test
window. No methodological justification for applying a shorter recursion
observation interval to Futures was recorded. Local BTC perpetual candles begin
on 2020-01-01, leaving two months of prefix history before the new interval.

Stored one-month Futures recursion and convergence records remain provenance,
but cannot satisfy the amended gate. A rerun moves each superseded record under
`superseded` before writing the three-month result. The affected set is selected
only by the pre-existing technical exclusion `recursive_bias_found`, never by
profit or regime performance.

### Amendment 2026-09-10: fixed smoke trade-count cascade

**Owner's decision**, recorded before rechecking the low-trade smoke records.
The canonical trial run starts with `20200301-20200401`. If that run completes
but produces fewer than ten trades, the same unchanged strategy and runtime
are tested over `20200301-20200601`, then `20200301-20210301`. The cascade
stops at the first rung with at least ten trades. A runtime failure does not
become a trade-count verdict and is not repaired by merely widening the date
range. Every attempted rung, archive identity, and trade count is retained.

This is a prospective, result-blind diagnostic rule: the rungs and threshold
were fixed before the rerun and do not depend on profitability or market-regime
performance. It prevents a quiet calendar month from being mistaken for a
strategy that does not trade. It does not relax the eligibility gates and it
does not supersede stronger evidence already obtained over the complete frozen
window. In particular, a look-ahead analysis that remains below ten trades
after its 6.5-year fallback, or a full-window backtest with zero trades, is not
rerun on these shorter smoke rungs.

### Amendment 2026-09-10: identical Spot and Futures bias windows

**Owner's decision**, before any Spot diagnostic was rerun under this change.
The native look-ahead, recursive-bias, and warm-up-convergence diagnostics now
use the identical calendar interval `20200301-20200601` for Spot and Futures.
This supersedes only the sentence in the 2026-09-09 amendment that retained
Spot at `20190101-20190401`; its three-month duration remains unchanged.

Using the same calendar dates removes the sampled market period as a difference
between the two execution modes. Both diagnostics use BTC only, so the later
listing dates of the other seven pooled pairs do not constrain this interval.
January and February 2020 remain available as prefix history for both modes.

Stored Spot records over `20190101-20190401` remain immutable provenance but
cannot satisfy a new decision under this amendment. They must be superseded and
rerun under `20200301-20200601`; selection for rerun is based on the obsolete
timerange, not on profitability or regime performance.

### Amendment 2026-09-10: completed full backtest closes technical work

**Owner's decision.** A successful canonical pooled Stage-7 full backtest is
evidence that the exact strategy implementation completed the technical chain
which precedes that run. A subsequent change to a Spot or Futures diagnostic
calendar window must therefore not return that implementation to the
measurement queue.

The closure is identity-bound: the recorded Stage-7 result must be `measured`,
have the canonical pooled scope, and match the current source hash and run
profile. Its recorded full-backtest timerange remains visible as provenance;
the later Spot diagnostic-window shift does not invalidate this closure. It is exposed as
`technical_chain_complete=true` in `STRATEGY_STATUS.csv`. It closes only
`open_work`; it does not retrospectively admit a strategy, reverse an existing
exclusion finding, or treat an OOM, timeout, failed, or identity-mismatched run
as completed.

### Amendment 2026-09-10: exclusions close the work queue

**Owner's decision.** A strategy recorded in the final `excluded` cohort is a
completed audit case. Its exclusion reason and evidence remain visible, but it
must never retain an `open_work` item merely because a supporting diagnostic is
historical or an ancillary recursion ladder did not finish. This does not apply
to `exclusion_unconfirmed`: that separate cohort has not earned an exclusion
verdict and remains open until its evidence gap is resolved.

### Amendment 2026-09-10: non-testable canonical full backtests are excluded

**Owner's decision.** A strategy that reached Stage 7 but has a canonical
pooled full-backtest status of `failed`, `resource_inconclusive`, or `timeout`
is not testable for this benchmark and is final `excluded` under C10
`full_backtest_not_testable`. The recorded outcome is retained as provenance;
it is not requeued or retried. This rule applies to the 34 previously E1
admitted rows with those statuses, and does not infer anything about their
profitability.

### Amendment 2026-09-20: one owner-approved 1m-to-5m pooled exception

**Owner's decision.** `HedgeAdaptiveRegimeStrategy` at canonical source hash
`sha256_378a5c0315a4f89d2424578ef6a8d57bce54fba018d0842b7e467b230db5d2b6`
ended its eight-pair 1m pooled Full-Backtest as `resource_inconclusive`. The
owner approved one replacement pooled Full-Backtest at 5m after a separate
eight-pair diagnostic completed with the same source, futures configuration,
pair universe, timerange, fee and shared-capital settings. The 1m OOM record
is retained inside the promoted record; the accepted 5m record is labelled
`owner_approved_timeframe_override_pooled_pair_universe` in status evidence.

This exception applies only to that source hash and does not alter the
timeframe of the strategy source, the ordinary canonical runner, the C10 rule
for any other strategy, or the interpretation of 1m and 5m performance as
identical. Its purpose is auditable E1 pooled coverage under the owner's
explicit resource decision, with the execution-timeframe difference visible.

### Amendment 2026-09-20: 1m OOM recovery route at 5m

**Owner's decision.** The 60 source-preserving strategies whose canonical 1m
pooled Full-Backtest is `oom_confirmed` or `resource_inconclusive` may enter
`repair.timeframe_5m_recovery`. This is a repair route, not a source change or
automatic timeframe reclassification. It repeats Smoke, Look-ahead, Warm-up
convergence, and final Recursive-bias at an isolated 5m execution timeframe.
A failed or inconclusive gate blocks later gates; only four PASS results permit
an isolated full-eight-pair 5m Full-Backtest.

All recovery evidence is outside canonical gate stores and the canonical full
manifest. A measured 5m result remains `pending_owner_promotion`; it cannot
change E1/C10, source identity, or the meaning of the retained 1m OOM result
without a later explicit owner decision for that exact implementation identity.

### Amendment 2026-09-21: promote completed 5m OOM recoveries into E1

**Owner's decision.** Once all 60 `repair.timeframe_5m_recovery` cases have
reached a final result, every identity-current case with four 5m technical
PASS results and a measured eight-pair 5m Full-Backtest is promoted to
`E1_expanded` as repaired. `repair.promote_timeframe_5m_recovery` verifies the
full cohort is complete, refuses a live audit/repair controller, preserves the
canonical 1m OOM result under `original_full_backtest`, and writes the accepted
5m record with scope `owner_approved_timeframe_5m_recovery_pooled_pair_universe`.
It then regenerates published state. A blocked, FOUND, ERROR, or timeout route
is not promoted.

### Amendment 2026-09-21: pause gated Model 1/2/3 backtests

**Owner's decision.** Model 1, Model 2, and Model 3 gated backtests are paused
until further notice because the approach did not prove useful. Existing
candidate specifications, manifests, attributions, and pages remain immutable
historical evidence. The serial pipeline dispatcher must not schedule, resume,
or create any gated-model run. This does not pause Model 0 technical evidence,
Stage 8b execution robustness, the cost screen, or verified-specialist
qualification for admitted strategies.

### Amendment 2026-09-21: the dispatcher runs Stages 9-13 for Model 0, and every full-backtest window is per mode

**Owner's decision.** The serial dispatcher no longer stops at Stage 8b. When no per-strategy route is left and the
inputs of the regime evaluation changed (the E1 cohort with the digest and scope of each accepted archive, the regime
labels, the execution-robustness and cost-screen stores, the source of the programs), it runs `tools.regime_evaluation`:
`regime.validate_regime`, `regime.attribution`, `regime.specialist_evaluation`, `regime.discovery_comparison`,
`regime.daily_return`, `regime.detail_totals` and `tools.regime_specialists_page`. Model 1, Model 2 and Model 3 are
excluded (backtests, gated attribution, comparison), as paused above; the pages keep their snapshots. The step is
recorded as gate `regime_evaluation` (Terra, medium) in `evidence/RUN_METADATA.jsonl`.

The analysis window is one calendar interval for both modes from 2026-09-21 (`profile_full_window.timerange`, see the next
entry). `evidence/full_backtest_resource_diagnostic.py`, which ran the 5m OOM recoveries, used `20200301-20260821` for
both modes and now takes the window from `profile_full_window`.

### Amendment 2026-09-21: the analysis window starts on 2020-04-01 for spot and futures

**Owner's decision.** "For comparison", the futures window starts on 2020-04-01 like the spot window (365-day warm-up
rung unchanged). Until now only the spot window did (Decision 2026-09-03); futures full backtests ran from 2020-03-01.
Changed: `profile_full_window.TIMERANGE` and `warmup_convergence.WINDOW_START` (futures), the start of the regime labels
and of the attribution (`regime.regime_engine.START`, `regime.attribution.START`; the indicators still read the earlier
candles), so the discovery window is 2020-04-01 to 2023-12-31 and the March 2020 crash is outside the benchmark.

Existing results: every canonical futures full backtest (72 at the time) was run from 2020-03-01. Until it is repeated,
the attribution drops the trades that opened before 2020-04-01, which is an approximation (the account and the shared
open-trade budget differed in March). The dispatcher repeats them with `--force`, then their 5m detail runs (a detail
run over another window is not comparable to its base run). The owner-approved 5m recoveries (41 spot, 7 futures) have
no dispatcher route and stay trimmed. The ladder ceilings of the futures rows that were capped by their prefix history
were not recomputed.

### Amendment 2026-09-21: pooled runs go in batches of four, failures repeat alone, known 1m OOM goes to 5m

**Owner's decision.** The dispatcher no longer runs the pooled full backtests and the 5m detail runs one strategy at a
time. Every strategy owed one (a first run, a run over the old window, a detail run still pending or over the old window)
goes into one batch: four containers side by side, each with a 3.5 GB memory limit (`runtime/full_batch_parallel.py`,
`runtime/detail_batch_parallel.py`; the limit is also the swap limit, so a strategy that outgrows it dies alone). Whatever
did not finish (killed for memory, past the 3600 s ceiling, no record) is repeated at the end, one strategy at a time,
in a single container with 15.5 GB and against the canonical store; the canonical record of such a strategy is the solo
result. Workers write their own stores and the measured results are imported into the canonical manifest, because two
containers must not write one file. The ceiling of 3600 s is not raised.

A strategy whose 1m pooled run is a known out-of-memory case (the canonical status is `oom_confirmed` or
`resource_inconclusive`, also after a repair, because the row keeps its status until a rerun replaces it) is not run at
1m again. The dispatcher sends it to `repair.timeframe_5m_recovery` (four gates and the eight-pair 5m full backtest at
5m), one at a time, because that run needs 5 to 6 GB. It stops at `measured_5m_pending_owner_promotion`: the promotion
into E1 that the owner gave on 2026-09-21 was for the 60 cases then analysed, and is not extended to new ones by this
entry.

### Amendment 2026-09-11: warm-up convergence precedes final recursive-bias

**Owner's decision**, applied prospectively to every strategy that still has
technical gate work. The diagnostic sequence is now: native look-ahead first;
only after a `PASS`, the frozen warm-up convergence ladder; only after a
current `converged` ladder result, final native recursive-bias using that
ladder's selected startup-candle count. A native look-ahead `FOUND` is a final
information-leak exclusion, so neither later measurement is useful or
permitted for that implementation. `NA` is not a pass and likewise blocks
follow-up work until its technical cause is resolved.

This changes workload order, not an admission threshold, timerange, strategy
implementation, or any existing measurement. It prevents an author's declared
or Freqtrade default warm-up from deciding the final recursion verdict when the
fixed ladder demonstrates that it is too short. The runner defers recursive
work until the prerequisite exists and passes the settled value explicitly;
`PIPELINE.md` documents the same order for future work. Older recursive records
remain provenance and are not silently reclassified by this prospective change.

### Amendment 2026-09-15: smoke cascade drops the one-year third rung

**Owner's decision**, made investigating the webclinic017 NNPredict_*
cluster's zero-trade smoke results. The cascade above now stops after
`20200301-20200601` (3 months); `20200301-20210301` (1 year) is removed.

The cluster's zero-trade result turned out not to be a quiet market period
at all - the actual cause was a pandas 3.0 chained-assignment no-op
(`repair/REGISTER.md`, Phase 10) that silently dropped every model
prediction before it reached the dataframe, so the entry trigger could
never fire on ANY window, three months or one year, until the underlying
bug was fixed. The one-year rung bought an hour of retraining per strategy
for a verdict the three-month rung already gave just as reliably in every
case checked. A row that still measures zero trades after the three-month
rung is now read as "something upstream of this window is broken or this
strategy genuinely does not trade" - a question for the next diagnostic
stage, not for a longer smoke window - rather than reflexively spending
more runtime (or analyst time reading its log) on the same row before
that question is even asked.

This narrows, rather than removes, the guard the 2026-09-10 amendment
describes: a quiet first month is still caught by the second rung: only
the third rung - the expensive one, and the one this investigation showed
adds a verdict the second rung already reliably gives - is gone. Everything
else about the 2026-09-10 amendment (prospective, result-blind, does not
relax eligibility gates, does not supersede stronger full-window evidence)
is unchanged.

### Amendment 2026-09-16: the "frozen file" description is dropped, not just E0's authority

**Owner's decision**, restated after re-confirming that strategies drawn from
the original E0 population have continued to show look-ahead and recursive
bias under this audit's own diagnostics well after the 2026-09-03 amendment
above - `MacdStrategy` was not an isolated case. E0's `regime_eligible=true`
was already non-authoritative (the amendment above already forbids it
skipping any check), so this changes no admission result; it removes a
description that was no longer true in either sense that mattered.

Two things were being called "frozen" for `evidence/REGIME_ELIGIBILITY.csv`,
and both are retired here. First, substantively: the file's content was
treated as a reasonable historical snapshot worth preserving even though
non-decisive. Repeated post-2026-09-03 findings of bias among former E0 rows
mean it should not be read as even a soft signal of anything - E0 is
obsolete, full stop. Second, literally: `evidence/strategy_status.py` and
this document both described the file as "frozen and never regenerated," an
immutable anchor. That was found false on 2026-09-16 - the file was in fact
regenerated on 2026-09-14 (`b071dc3`, to surface later harvest waves to
`profile_bias.py`'s own candidate selection), growing `regime_eligible=true`
from the original 67 rows to 121. Keeping the "frozen, untouchable" label on
a file already known to have been rewritten would document a protection that
does not exist rather than the actual, harmless state of things - E0 grants
nothing regardless of which or how many rows carry the flag.

`evidence/strategy_status.py`'s selftest no longer asserts the old-baseline
count at exactly 67; the internal-consistency check (every row noted as
former E0 in `gate_notes` matches a row the eligibility file marks true, and
only those) is unaffected and stays. The original 67-row snapshot remains
recoverable from git history if ever wanted for comparison - not reverted
here, because reverting would itself be re-asserting a "frozen" status this
amendment is retiring.


## Where Docker stands instead of native Python

Stages 1–4 (trial run, look-ahead, warm-up ladder, recursion) run both natively and in the pinned Docker images (`strategy-audit-runtime:2026.7` and variants), depending on which runner calls them — both write to the same JSON stores, distinguished only by the field `runtime_id` (`native_unversioned` vs. `docker:sha256:...`). Stage 8 (full window, pooled) and the 5m detail reruns of Stage 8b run exclusively in Docker because it runs unattended for hours.

## Old files that are no longer needed

Three different categories, not one — important because they are treated differently.

### 1. From the original author of the previous work (895/900 strategies review, before this verification chain)

Publication preface and case studies of a previous, less strict review. No file here is read or written by a script from Stage 0–13; they describe a state that `STRATEGY_STATUS.csv` has long since replaced.

| File/Directory | Created by | Replaced by |
|---|---|---|
| `old/predecessor_audit/README.md`, `LEDGER.csv`, `LEDGER.md` | archived `ledger.py` | `STRATEGY_STATUS.md` |
| `old/predecessor_audit/CORPUS.md`, `CORPUS_PLAN.md`, `corpus/INDEX.md` + 896 cards under `corpus/` | archived predecessor tooling | `evidence/EXECUTION_PROFILES.csv`, `evidence/corpus_sources.json` |
| `old/predecessor_audit/ANALYSIS.md`, `ANALYSIS.ru.md` | (predecessor tooling) | five handpicked case studies, no population — `STRATEGY_STATUS.csv` covers the current population |
| `old/predecessor_audit/results/*.md` (`DoubleEMACrossoverWithTrend.md` et al., `INDEX.md`) | (Predecessor tooling) | the same five case studies — **not to be confused with `results/regime/`**, which is current and described from Stage 8 onward |
| `old/predecessor_audit/DCA.md`, `DEPTH.md`, `RESOLVABLE.md` | (Predecessor Tooling) | independent page investigations without regime reference, nothing replaces them, because nothing in the current chain asks the same question |
| `old/**` (`corpus_repair`, `eligibility_zwischenstand_2026-08`, `hmm_prototype_2026-08`, `proxy_backtests_2026-08`, `root_prototypes_2026-08`, `translation_attempts_2026-08`, `vorueberlegungen`, own `old/README.md`) | various, all before this chain | consciously archived, not deleted |

### 2. Own files of this test chain, but orphaned (no producer script anymore available)

Unlike Category 1: **our** files, not those of the original author — but the script that they once wrote no longer exists in the repo. `ELIGIBILITY_NEVER_RUN.json` and `ELIGIBILITY_TRAP_SMOKE.json` were the last two of this kind and were removed on 2026-09-06 (see Stage 1) — currently no candidates in this category. Any future find would be treated the same way: first confirm via diff that no line depends on it anymore, then commit, then remove — never the other way around.

### 3. `tools/` — own tools, but manual, not part of the automatic chain

All files here are current and not outdated. Most run on demand; Stage 0 additionally uses the corpus tools in this directory. They were moved here from the root and their root path assumptions were adjusted. The outdated predecessor gates `sync_repo.py`, `freeze_guard.py`, `verify_ledger.py`, and `totality.py`, on the other hand, are located under `old/predecessor_audit/` and are no longer part of the current CI. `totality.py` reports 124 unchecked heuristic hits on today's pipeline and is therefore not suitable as an unmodified commit guard. `ROOT` path assumptions (`os.path.dirname(os.path.abspath(__file__))`) were corrected by one level; `warmup_reparse.py`'s `from evidence import profile_bias` got a `sys.path.insert` on the root directory, the same trick that `repair/*.py` had used before.

| Program | Purpose | When to run |
|---|---|---|
| `tools/secret_gate.py` | Prevents a commit from containing a secret (four layers, see separate docstring) | before each commit that introduces new files |
| `tools/translation_repair.py` | Translates Russian comments/strings in Python files, AST-checked, never silently translates failed parts | when `tools/harvest.py` (Stage 0) brings in a repo with non-English comments |
| `tools/blocked_triage.py` | Finds fixable causes for rows that the test run never reached (freqtrade didn't even start them); writes `REPAIR_LIST.md` and `evidence/BLOCKED_TRIAGE.json`, which Stage 6 reads | after new Harvest or when the number of blocked rows changes (`--probe --list`) |
| `tools/eligibility_expansion.py` | Freezes the historical, result-blind eligibility expansion inventory (only technical stage-6 artifacts, no performance) | if `REGIME_PREREGISTRATION.md`/`PIPELINE_EXTENSIONS.md` (Part 1) are changed |
| `tools/probe_double_advise.py` | Checks whether the double `ft_advise_signals` call in `lookahead-analysis` duplicates a column | if there is a suspicion that the `enter_tag` shim distorts the result |
| `tools/probe_shim_neutral.py` | Compares backtest results with/without `enter_tag` shim on neutrality | after a change to the shim mechanism |
| `tools/probe_zero.py` | Differentiates in a row without trades whether the entry condition never becomes true or the indicator is missing | when a row shows 0 trades and the cause is unclear |
| `tools/strategy_classification.py` | Classifies type/timeframe per row from `evidence/EXECUTION_PROFILES.csv` and the strategy source code; writes `evidence/STRATEGY_CLASSIFICATION.json`, which is read by Stage 6 and Stage 11. `strategy_type` is always explicit: recognized family, `unclassified` or for test/template artifacts `not_applicable`. Order: classification before phase hypothesis, status, and HTML page. | after new harvest, if `evidence/EXECUTION_PROFILES.csv` changes or classification rules have been changed |
| `tools/label_intake.py` (with `tools/strategy_labels.py`, `tools/label_consensus.py`, `tools/label_check.py`) | Logic labels per strategy (trend_following, momentum, mean_reversion, breakout, volatility, grid, volume_flow, pattern, statistical, other), read from the entry and exit code by Haiku 4.5 with a verbatim code snippet as evidence; writes `evidence/STRATEGY_LABELS.json` and the columns `logic_labels`, `logic_primary`, `logic_status`, `logic_facts` of `STRATEGY_STATUS.csv`. **Second-opinion rule:** a strategy whose Haiku answer has trend_following, momentum, breakout, volatility or grid as primary or at high/medium confidence is labelled blind by DeepSeek as well; `logic_status` is `confirmed` (same primary), `contested` (different) or `pending` (not asked yet), and such a label enters `logic_labels` only when both models gave it. Reason: on a 200-strategy blind check these were the labels Haiku got wrong (dip-buys read as momentum/breakout, empty or delegating classes read as grid). **Descriptions:** the same DeepSeek Flash request also returns a 2-3 sentence description of what the strategy does, stored as `description` in the same record, for every member of a family (2+ strategies) that has no hand-written description; the Strategy Ideas page shows it, marked as a model reading of the code. Runs inside `tools.harvest.refresh_intake_evidence` after classification; never fatal, the next intake completes what a model could not answer. | at every harvest; on prompt change re-run `python -m tools.strategy_labels --all` and `python -m tools.label_intake --second-opinion-only` |
| `tools/strategy_status_page.py` | Builds the published page from `STRATEGY_STATUS.csv`, so that page and table never get out of sync | after each `evidence/strategy_status.py` run, before publication |
| `tools/strategy_ideas.py` | `--rank` prints the families by number of strategies, which is the rule that decides which ones the page describes first; `--bundle` extracts the facts an interpretation needs (indicators, entry/exit conditions, settings, author docstring, method inventory) for the strategies named, `--render` lays out `evidence/STRATEGY_IDEAS.json` as `strategy_ideas.html` with one block per family, and `--check` fails when the corpus has moved past the revision an idea describes. A family names its strategies by stem, so the store only records the one revision each sentence was read from. It never writes the ideas store - an LLM session does, and writes it in prose, so this is a description and never evidence | after new strategies should appear on that page; `--check` before publishing it |
| `tools/source_dates.py` | Collects the three dates that really exist per strategy and writes `evidence/SOURCE_DATES.json`, which the ideas page shows per revision: a date the file name carries, the published site's post date for the files taken from it, and the last commit that touched the file in the repository it was harvested from. It also names the repositories whose dated files cluster on one commit date (at least 90 % of at least five), because there the commit date is an import date and not the date of a revision; `--recompute` rewrites that derived map after a rule change and `--summary` reports the coverage and says when the stored map is stale. It is a review-only reader like `frequenthippo_ranking.py` and changes no stage; the GitHub API allows 60 requests an hour without a token and 5000 with one, so a run is resumable and stops cleanly at the limit. No entry is guessed and no emptiness is filled in | when a new harvest or a new batch of families should show dates; `--summary` reports the coverage |
| `tools/warmup_reparse.py` | Reads stored leader logs again with the current parser without having to run freqtrade again | after a fix to the drift tables parser |

`repair/FREQAI_RESULTS.md`, `repair/REGISTER.md`, `repair/TRANSLATION_AUDIT.md` are also separate, current files, but provenance logs, not tools — only relevant if a specific repaired implementation is under discussion (see `README.md`).
