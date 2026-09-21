# Shared handoff - Codex and Claude

**Live state only.** What each stage does is in `PIPELINE.md`, why in its Decision record, which document answers which
question is in `README.md`. The long baton, checkpoints and work orders written up to 2026-09-20 are archived
unchanged in `old/handoff/HANDOFF_until_2026-09-20.md`; read that only to trace how something came about, never for
state.

The documentation rules for both agents are in `AGENTS.md`, "Documentation discipline", and in `CLAUDE.md`.
Keep this file short. Edit your own baton entry, not the other agent's. When a line stops being live, delete it here.
Never write a count that a command can print: counts in prose are what made the old file wrong.

## Baton

- Last agent: claude
- Last update: 2026-09-20T20:50+02:00
- Stopped because: the Markdown documents were consolidated (README table, `PIPELINE.md` with decision record,
  `PIPELINE_EXTENSIONS.md`, `LESSONS.md`, this file rewritten). No measurement was started or stopped.
- Observed at 20:36: one `strategy-audit-runtime` container was running, started by the Codex dispatcher
  (`tools/pipeline_dispatcher.py`), and Codex had uncommitted status regenerations in the tree. Do not start a second
  runner. Run the machine-state commands below before anything else.
- Next agent should: read `evidence/PIPELINE_STATE.json` or run `python -m evidence.pipeline_state --summary`, then
  continue the serial dispatcher work. Codex's own baton entries up to 2026-09-18 are in the archive; nothing in them
  is a standing instruction that is not repeated below.

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
- The ceiling of 3600 s per strategy run is never raised, not even for one strategy. WSL stays at 14 GB plus 4 GB swap.
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
- **A test that was red at HEAD:** `python -m evidence.strategy_status --selftest` was failing before the execution
  robustness work. Two causes were fixed; a third remained: `MASlopeStrategy` carries the primary reason
  `repeated_timeout_after_exhausted_repair`, which an assertion does not accept. Run the selftest to see whether it still
  fails.
- **Observed, unexplained (execution robustness):** the first ten detail strategies failed natively and were measured in
  Docker with an empty `.err` file. Trades that close before they open appear only under `--timeframe-detail` (15 trades
  in 7 strategies); the classifier reports them and does not act on them.
- **Four strategies with a final `ERROR` in Stage 8b:** `FibonacciEMATrendStrategy` and `Hacklemore2` hit the 3600 s
  ceiling running alone, `MacheteV8b` and `MacheteV8bRallimod` fail with a datetime error inside the strategy.
  `--targets 5m` still lists them as owed; the launcher skips them.
- **`ZaratustraDCA5` cannot be measured at 1m** inside the ceiling, and its canonical account collapsed
  (`stake_amount: unlimited`); quote its dollar figure with that caveat.
