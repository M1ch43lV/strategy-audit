# Shared handoff - Codex and Claude

**Live state only.** What each stage does is in `PIPELINE.md`, why in its Decision record, which document answers which
question is in `README.md`. The long baton, checkpoints and work orders written up to 2026-09-20 are archived
unchanged in `old/handoff/HANDOFF_until_2026-09-20.md`; read that only to trace how something came about, never for
state.

The documentation rules for both agents are in `AGENTS.md`, "Documentation discipline", and in `CLAUDE.md`.
Keep this file short. Edit your own baton entry, not the other agent's. When a line stops being live, delete it here.
Never write a count that a command can print: counts in prose are what made the old file wrong.

## Baton

- Last agent: copilot
- Last update: 2026-09-23T23:13:51+02:00
- Stopped because: Stage 0 intake for the highest-ranked FrequentHippo leads is done and the published state is
  consistent. No benchmark was started and no runner was touched.
  - The lead list came from `python -m tools.frequenthippo_ranking` (new, review-only; a third party's score is a
    lead, never evidence). Source chosen for the two leads that existed nowhere else in the corpus:
    `python -m tools.harvest remiotore/ccxt-freqtrade`. `BinHModWhiteHOV0` and `CombinedBinHClucAndSMAOffset_2` are
    now corpus rows in `not_tested_in_current_runtime`.
  - The wave is large - `git diff --numstat evidence/EXECUTION_PROFILES.csv` prints its size - and
    `repos/remiotore_ccxt-freqtrade/` is still untracked, so it is deliberately not committed yet.
  - The intake adjudication removed the freshly downloaded copies it found to be duplicates
    (`normalized_code_match_no_config_overlay_either_side_v1`; record in `evidence/REMOVED_DUPLICATE_SOURCES.json`).
    `evidence.strategy_status --check`, `evidence.semantic_duplicates --check`, `tools.strategy_status_page --check`
    and `evidence.pipeline_state --selftest` are current and green.
  - A `tools/malware_gate` re-scan of the new folder flagged nothing; every write had already been gated inside
    harvest, so this only confirms it after the fact.
  - Two leads cannot be acquired by any route this stage allows: `BB_RPB_TSL_RNG_V2_20211008` and
    `BB_RPB_TSL_jilv220_github_20211008` exist only as the site's own published files, and harvest reads the GitHub
    API only. They are parked outside the corpus in `user_data/site_sources/` with their provenance; admitting them
    needs a decided intake path for non-repository sources (PIPELINE.md, amendment 2026-09-23). A third lead,
    `BB_Github_mupol313_hossain__rtr__20240622_082213_dca`, has no source left anywhere.
  - `Combined_NFIv7_SMA_Rallipanos_20210707` and its DCA twin are known intake duplicates (representative
    `NostalgiaForInfinityV7_SMA`) and were not re-admitted.
  - The wave also moved the *representation* of strategies that were already in the corpus: for 45 `strategy_id`s
    whose class name existed before, the canonical file moved into the new folder, 39 of them to a different
    revision, and 22 admitted rows lost `technical_chain_complete` without any measurement failing. Cause was
    `discover()`'s alphabetic precedence, which knew nothing about measurements.
  - Fixed, owner-approved, in `evidence/execution_profiles.py`: a representative that a raw measurement store names
    by content hash cannot be displaced by a same-named copy, `EXTRA_SUBCLASS_STRATEGIES` entries join the
    candidate list instead of being dropped, and a class name without a measurement keeps the old deterministic
    rule. Result on the same wave: lost chains 22 -> 0, changed pre-existing rows 45 -> 19. Recorded as the
    amendment of 2026-09-24 in `PIPELINE.md`.
- Next agent should: run the machine-state commands, then commit the wave as one unit (corpus under
  `repos/remiotore_ccxt-freqtrade/`, the regenerated stores and the amended documents) if the machine is idle. The
  guard chain was green after the change: `strategy_status --check`, `semantic_duplicates --check`,
  `strategy_status_page --check`, `verdicts --selftest`, `pipeline_state --selftest`,
  `verdict_migration_audit --strict --quiet`, `identity_freeze --quiet`. The dispatcher's next eligible action is a
  smoke run and its queue is alphabetical, so the new rows arrive in their turn. `AlexBandSniperV10AI` still needs
  the owner's policy call recorded below.
  - The two leads that no repository can supply are adopted: `tools/adopt_source.py` (owner decision 2026-09-24,
    `PIPELINE_EXTENSIONS.md` Part 5) writes `repos/frequenthippo/<file>.py`, records URL and hash in
    `repos/frequenthippo/.sources.json`, and refreshes the intake exactly as harvest does.
    `BB_RPB_TSL_RNG_V2_20211008` and `BB_RPB_TSL_jilv220_github_20211008` are corpus rows attributed to
    `frequenthippo` in `not_tested_in_current_runtime`. **Every further adoption needs the owner's agreement to that
    one file**: the command refuses without `--owner-approved` and refuses before it downloads; `--dry-run` is how a
    request is prepared.
  - `evidence/repo_freshness.py` gained `NON_GITHUB_SOURCES`: it had asked GitHub for that folder and answered
    `api_error_or_not_found`, which reads like a repository that vanished. It now reports `not_a_repository`, and
    `REPO_FRESHNESS.md` says what that means.
  - New pilot artifact `strategy_ideas.html` plus its hand-written store `evidence/STRATEGY_IDEAS.json`: ten strategy
    families described in prose that was read out of their code by an LLM session, each bound to the `source_sha256`
    it was read from. `tools/strategy_ideas.py` bundles the facts (`--bundle`), renders the page (`--render`) and
    fails when an idea outlives its revision (`--check`); it never writes the store. Extending the page means bundling
    more strategies and writing more entries - the ten are deliberately a pilot, and nothing here is a measurement.

### Previous baton entry - codex, 2026-09-23

- Last agent: codex
- Last update: 2026-09-23T21:14:39+02:00
- Stopped because: the verdict-schema work is complete, committed and green. No benchmark, analyzer or runner was
  started; every published change below came from a reader, not from a rerun.
  - One verdict vocabulary describes every store now (`evidence/verdicts.py`; read-side only, no store rewritten). The
    schema and the two guards are in `evidence/README.md`, the decision behind them in `PIPELINE.md`. The same layers
    are also in `evidence/PIPELINE_STATE.json` at `strategies.<id>.evidence_resolution.verdicts`.
  - `python -m evidence.strategy_status --selftest` is green again. It was the red test in the previous handoff, and
    the canary - not the producer - was wrong twice: its exclusion-reason list did not include
    `repeated_timeout_after_exhausted_repair` (documented in `repair/adjudicate.py`, registered in
    `evidence/exclusion_criteria.py`), and its duplicate term counted rows whose source file had come back. Read the
    producer's docstring before widening a canary.
  - Two published rows changed, both a corrected reader rather than a corrected measurement: `AlexBandSniperV10AINoBias`
    gained its classification (`ml_ai`, `15m`), and `FastSupertrend_optim3_rsi_75fix` is no longer excluded as a
    duplicate - its trade set and hash differ from its twin, so the `code_equivalent_only` guard applies.
- Next agent should: re-run the whole gate chain after touching `evidence/strategy_status.py` or
  `tools/strategy_status_page.py`. Their assertions are canaries and fail one at a time, so fixing one unmasks the
  next. Everything else in the entry below still holds: continue only the non-gated serial chain, and
  `AlexBandSniperV10AI` stays `needs_a_look` until the owner decides.

### Previous baton entry - claude, 2026-09-22

- Last agent: claude
- Last update: 2026-09-22T09:20+02:00
- Stopped because: `AlexBandSniperV10AI` (`repos/vaskosmihaylov_nfi-custom-strategies/.../AlexBAndSniperV10MLAI.py`)
  is partially repaired but still blocked; the remaining cause needs an owner policy call, not a repair.
  - Fixed and proven (`repair/patch_class2.py` rule `alex_dynamic_optimization_gate`): `enable_dynamic_optimization`
    was hardcoded `True` against the author's own inline comment ("deaktivieren fuer Backtest"); it is now gated by
    runmode. Two entry points that reached Optuna without checking the flag at all
    (`maybe_optimize_coin`, `daily_optimization_check`) are closed too - same flag, same stated intent, they had
    just never been wired to it.
  - Still open, not repairable under the project's own no-invention rule: `bot_start()` unconditionally runs
    `train_ml_from_backtest()` on every fresh run (no cached model on disk). It loads the strategy's FULL available
    multi-year history for every pair in the shared data directory (`load_pair_history` called with no timerange),
    recomputes every indicator over that, then walks each candle in a plain Python loop with a 50-candle lookahead.
    Nothing in the file marks this backtest-inappropriate the way the Optuna flag was marked - gating it would
    invent author intent that is not written down. Confirmed: still times out at 900s (3x the smoke default) with
    the Optuna fix in place. Diagnosis recorded in `evidence/BLOCKED_TRIAGE.json` via a new
    `tools/blocked_triage.py` mechanism (`STRATEGY_NOTES`, keyed by strategy_id) - needed because the generic
    `FAMILIES` text-match cannot safely scope to one strategy sharing a generic "timeout after N seconds" message.
  - Also fixed while investigating: `repair/patch_class2.py`'s `targets_from_profiles` read `canonical_file`
    instead of `original_file` - once a strategy has an overlay selected as canonical, re-running the patcher for
    it read its own previous output as source, so a rule whose precondition matches only the untouched original
    silently stopped firing on any second run. General fix, not scoped to this strategy.
  - Regenerated after these changes: `evidence/EXECUTION_PROFILES.csv` (`python -m evidence.execution_profiles`),
    `evidence/BLOCKED_TRIAGE.json` and `REPAIR_LIST.md` (`python -m tools.blocked_triage --probe --list` - the
    `--probe` matters, a bare run silently drops every import-probe classification), `STRATEGY_STATUS.csv`/`.md`
    and `strategy_status.html` (`python -m evidence.strategy_status`).
- Observed: `--watch` used to poll forever, printing `idle` every interval even with nothing to do; stdout is
  block-buffered when redirected to a log file, so a genuinely finished run looked stalled from the log alone (CPU
  time, not log growth, is the reliable signal). Fixed: `run_once()` now returns an outcome and `--watch` exits with a
  `"stopping"` line once `choose()` reports `idle` (`tools/pipeline_dispatcher.py`). A lock left by a hard-killed
  process (e.g. `TaskStop`) needs `--recover-stale-lock` before the next `--apply`.
- Next agent should: run the machine-state commands before dispatching. Continue only the non-gated serial chain; do
  not schedule, resume, or create Model 1/2/3 work until the owner reverses the pause. `AlexBandSniperV10AI` stays
  `needs_a_look` until the owner decides whether to authorize gating `ml_enabled`/`bot_start` by runmode as an
  explicit exception (it would not be provable the way the Optuna fix was).

## Objective

Maximize technically trustworthy strategy coverage, then benchmark the admitted strategies across the frozen four
DMI/ADX states and six reporting phases. Keep attribution, true gated performance, and ranked conclusions separate.

## Reading order

`README.md` gives it. In short: this file, the machine-state commands, then `PIPELINE.md` and
`REGIME_PREREGISTRATION.md` for what you are about to touch.

## Machine state - authoritative

Run these before trusting any count or prose:

```powershell
docker ps --format '{{.ID}}|{{.Image}}|{{.Status}}|{{.Command}}'
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'strategy-audit|full_backtest|profile_smoke|profile_full_window' } | Select-Object ProcessId,Name,CommandLine
git log --oneline -8
git status --short
.\ftenv\Scripts\python.exe -m evidence.strategy_status --check
.\ftenv\Scripts\python.exe -m evidence.pipeline_state --summary
```

The status check is read-only. Do not regenerate `STRATEGY_STATUS.csv` while a runner is writing one of its input
stores.

## Before starting any benchmark or analyzer

Never assume an empty terminal means idle. Run both process checks above and:

```powershell
Get-ChildItem evidence/PROFILE_SMOKE.json,evidence/PROFILE_FULL_WINDOW*.json,results\regime\*manifest*.json | Select-Object Name,Length,LastWriteTime
Get-ChildItem -Force *.running,results\regime\*.running -ErrorAction SilentlyContinue
```

One writer per output store. Separate-output shards may run in parallel only when identities are disjoint and
`evidence.profile_bias_merge` will merge them after all writers finish. A Docker CLI timeout is not evidence that no
container exists. Inspect processes, locks, artifact timestamps, and the run log before deciding.

## Standing procedures

- **After every completed batch:** `python -m evidence.execution_robustness && python -m evidence.strategy_status &&
  python -m tools.strategy_status_page`. Until it runs, `execution_robustness_status` shows `PENDING` for strategies
  whose detail run has finished. `python -m evidence.execution_robustness --check` says whether the stores are current.
  `evidence/EXECUTION_ROBUSTNESS.json` and `evidence/COST_SCREEN.json` are written only by that module.
- **Stages 9-13 (Model 0) run in the dispatcher** once no per-strategy work is left and their inputs changed
  (`python -m tools.regime_evaluation --check` says whether a rerun is due). Model 1/2/3 stay paused. Publishing the
  artifacts (Regime-Spezialisten, Strategy Test Bench) is still manual.
- **Check-run finalization is automatic.** Direct canonical bias runs and `runtime/profile_bias_docker.ps1` publish
  status, pipeline state and the page before exiting. Do not reintroduce a manual merge step.
- **Pipeline-wide counts** come from `evidence/PIPELINE_STATE.json` through `evidence.pipeline_state.EvidenceStore`,
  never from one raw store (asking a raw store gave 882 where the answer was 352).
- **Intake:** `python -m tools.harvest owner/repo`. After an intake that removes a duplicate, run
  `tools/purge_removed_duplicate_results.py` (it logs the removed records verbatim in
  `evidence/REMOVED_DUPLICATE_RESULTS.json`), then regenerate `regime.attribution`, `regime.specialist_evaluation`,
  `regime.discovery_comparison`, `evidence.execution_robustness`, `evidence.strategy_status`,
  `tools.strategy_status_page`. Deleting a duplicate happens only at intake; afterwards a row is excluded, not deleted.
  Not touched by the purge: `candidate_spec_full_v1.json` and the model1/2/3 manifests (bound to the spec hash), the
  `ELIGIBILITY_EXPANSION_*` decision records, `REGIME_ELIGIBILITY.csv`, `NEW_REPO_CANDIDATES.json`, the run archives.
- **The two result pages** (`regime_specialists.html`, `regime_gating.html`) are rebuilt with
  `python -m tools.regime_specialists_page` and always both, with the timestamp of that generation, before either is
  published. Rankings are recomputed whenever results change; only the floor and the rules are frozen.
  `python -m tools.regime_specialists_page --check` says whether the committed pair still matches its data. It
  renders both pages, so it costs about a minute, and it is not a CI step: the module imports pandas and reads the
  regime stores, neither of which is in a clean checkout.
- **Generated files are never hand-edited.** Run the writer as a module from the repository root:
  `python -m evidence.<module>`. Evidence stores do not move back to the root and are not invoked by file path.
- **Graph:** `graphify update .` only, never `graphify extract .` (semantic extraction consumes API quota).

## Do not redo

- Corpus intake and the completed eligibility expansion waves (`evidence/ADMISSION_RECORDS.md`).
- Smoke-funnel work packages 1-5, including the GRID/ONS 1,800 s cascades and the bounded BlueEyes repair chain, and the
  `Hacklemore3` smoke rerun while its identities match. The 30 `too_few_trades` rows: their 6.5-year look-ahead fallback
  is stronger than any smoke rung.
- Warm-up ladders, native bias diagnostics or admission decisions already in the stores. Any identity-matching
  `measured` canonical pooled Full-Backtest and any measured Model 0 archive (the runner is resumable). Regime feature
  generation, unless its hashed candle inputs or the frozen formula change. The 5-profile ungated adapter equivalence
  suite.
- Final `excluded` rows are closed: preserve the reason and evidence, never recreate `open_work`. C10
  (`full_backtest_not_testable`: `failed`, `resource_inconclusive`, `timeout`) is final; no retry or admission without a
  new owner decision.
- Nine cards that need a runtime capability this audit does not have: `BaseNNStrategy` (obsolete
  `joblib.externals.cloudpickle`), `TS_Coeff` and `TS_Wavelet` (Apple-only MLX), six Litmus derivatives (`cointanalysis`
  or the unsafe `freqtrade.litmus` shadow package). Rerun only if the dependency policy or runtime capability changes.
- E0 as evidence: do not rerun the old 67, add 67 to E1, or regenerate frozen E0 files.
- Strategy type classification: never infer a type from repo prose or hand-edit `STRATEGY_STATUS.csv`.
- A candidate spec is never generated from observed strategy performance.
- The ceiling of 3600 s per strategy run is never raised, not even for one strategy. WSL stays at 16 GB plus 4 GB swap (`.wslconfig`).
- Strategies at or below 5m get no rerun and no 1m batch (owner, 2026-09-19); they count as a passed 5m run by rule and
  the record says so (`basis: owner_rule_at_or_below_5m`).
- The 2x, short and coin-downtrend variants of the rotation bot (`bot/`) were stopped by the owner on 2026-09-20; do not
  restart them unless asked.
- Rotation bot: variants and their result are in `PIPELINE_EXTENSIONS.md` Part 4. `V2` with `N = 2` was rejected on the
  validation window; do not read that window again for a further variant (it would no longer be out of sample).
  The component search over the corpus (4.4, 4.5) found no reliable component for bear, sideways or transition; the 2x hold
  doubles the arithmetic return and lowers the growth of the account. Nothing is running for the bot. The four weeks to
  2026-09-19 are not to be added to any window (owner, 2026-09-21).
- Root `_sabotage/` was removed on 2026-09-15 (an orphaned fixture of the archived `loadscan.py`).

## Window correction done (owner, 2026-09-21)

Spot and futures both start on 2020-04-01. The 69 canonical futures full backtests were repeated by the dispatcher in
batches of four containers with 3.5 GB, 36 failures alone with 15.5 GB (one still `timeout`); their 5m detail runs (41
strategies) followed, all `measured` on the first pass. Stages 9-13 (Model 0) then reran: 686/741 canonical rows
`measured`. Both result pages and the Strategy Test Bench were rebuilt on 2026-09-22. The 5m recoveries
(41 spot, 7 futures) stay trimmed, there is no route to repeat them.

## Owner decisions that are open

1. **Validation window extension: on hold** (owner, 2026-09-20). `PIPELINE_EXTENSIONS.md`, Part 3, stays valid. Do not
   start it, do not change `END` in `regime/regime_engine.py` or `regime/attribution.py`, do not touch
   `profile_full_window.TIMERANGE`, write no amendment until the owner asks. The forward hold-out of the confirmation
   rule (`REGIME_PREREGISTRATION.md`, Amendment 2026-09-20) waits for the same decision. The text of the two result
   pages still says the rule is tested on data from 2026-08-21; it is corrected together with that extension.
2. **Classifier thresholds of Stage 8b.** They were fixed after 42 of 230 detail runs existed, which the plan
   discloses. Carried from the 2026-09-19 work order; I know of no decision to freeze or change them.
3. **Control runs** (same runtime, no detail candles) for the 33 `SENSITIVE` strategies whose baseline and detail run
   used different runtimes (`PIPELINE_EXTENSIONS.md`, Part 2, Amendment 2026-09-20, section 3). Build only if the
   attribution matters to a decision; a control run writes to its own output file, never the canonical manifest.
4. **Proposal:** require a 1m rerun for a strategy at or below 5m when its source declares a trailing stop, a
   profit-dependent exit or position adjustment (same Amendment, recommendation point 6). The current rule stands.

## Queued or unverified - check before acting

- **Look-ahead repair follow-up (queued 2026-09-18):** six registry gaps (`NASOSv5HO`, `NASOSv5PD`, `NASOSv5SL`,
  `NASOSv5_antipump`, `UziChanTB2`, `abbas`) now use the `idempotent_entry_tag_initialisation` rule. Six
  identically-labelled DataFrame failures (`AlexBandSniperV58COptuna`, `DevilStra`, `Solipsis`, `Solipsis3`,
  `SolipsisCon`, `Solipsis_USD`) run under the diagnostic-only `lookahead_dataframe_alignment_diagnostics` rule. When the
  Full-Backtest queue is idle, rerun one small case first (`DevilStra`), design a narrow repair from its
  `LOOKAHEAD_FRAME_ALIGNMENT` record, then retry `Schism5` alone with the agreed extended look-ahead timeout. Serial,
  and finalize each result before the next launch. Whether this was done since is not recorded here.
- **Observed, unexplained (execution robustness):** the first ten detail strategies failed natively and were measured in
  Docker with an empty `.err` file. Trades that close before they open appear only under `--timeframe-detail` (15 trades
  in 7 strategies); the classifier reports them and does not act on them.
- **Four strategies with a final `ERROR` in Stage 8b:** `FibonacciEMATrendStrategy` and `Hacklemore2` hit the 3600 s
  ceiling running alone, `MacheteV8b` and `MacheteV8bRallimod` fail with a datetime error inside the strategy.
  `--targets 5m` still lists them as owed; the launcher skips them.
- **`ZaratustraDCA5` cannot be measured at 1m** inside the ceiling, and its canonical account collapsed
  (`stake_amount: unlimited`); quote its dollar figure with that caveat.
