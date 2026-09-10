# Shared handoff - Codex and Claude

## Baton

- Last agent: codex
- Last update: 2026-09-10T20:22:17+02:00
- Stopped because: the owner made `failed`, `resource_inconclusive`, and
  `timeout` canonical pooled Full-Backtests final non-testable C10 exclusions;
  the generator, criteria, CSV, status page, and binding documents implement it
- Next agent should: never queue a C10 row. The current E1 cohort excludes all
  final Full-Backtest non-testable rows; if measurements resume, target only
  the remaining `pending` and `exclusion_unconfirmed` rows after identity
  filtering.

## Objective

Maximize technically trustworthy strategy coverage, then benchmark the admitted
strategies across the frozen four DMI/ADX states and six reporting phases.
Keep attribution, true gated performance, and ranked conclusions separate.

## Cold-session reading order - mandatory

1. Read this file in full.
2. Read `DOCUMENT_MAP.md` in full. It decides what binds and what to skip.
3. Read `REGIME_PREREGISTRATION.md` in full. It binds, including its amendments
   and OPEN choices. Never infer a frozen rule from the discussion plan.
4. Read `PIPELINE.md` in full when deciding what runs next or changing a stage.
5. Read only the section of `ELIGIBILITY_EXPANSION_PLAN.md` named under Plan
   pointer. Read the whole file only when changing admission, repair, resource,
   or stop rules, or when entering a new expansion wave.
6. Read applicable `AGENTS.md` files. The session-supplied root instruction
   currently requires the Graphify skill for `/graphify`.
7. Run the Machine state commands, then inspect `git status` and relevant diffs.

`REGIME_AUDIT_PLAN.md` is reference, not the rulebook. For Model 1/2/3 work read
only sections 12-15, Stages 8-11, cautions 28.1-28.6, and the current decision
entry; do not reread the roughly 2,000-line file end to end.

## Plan pointer

- Binding file: `REGIME_PREREGISTRATION.md`, especially `Analysis order`,
  `Frozen reporting safeguards`, `Amendment 2026-09-03: E0 is retired as a
  separate cohort`, and `OPEN before Stage 9 ranking`.
- Pipeline file: `PIPELINE.md`, Stages 7-11.
- Reference only: `REGIME_AUDIT_PLAN.md`, sections 12-15, Stages 8-11,
  cautions 28.1-28.6, Decision 0.17-03, Decision 0.22-01, and Decision 0.23-01.
- Eligibility protocol when measurement/admission is involved:
  `ELIGIBILITY_EXPANSION_PLAN.md` sections 6 and 7. The old Wave C pointer is
  retired; all expansion waves are already terminal in current artifacts.
- Futures recursion retest: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-09: three-month Futures recursion window`, plus
  `evidence/profile_bias.py` and `evidence/warmup_convergence.py`.
- Smoke trade-count escalation: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: fixed smoke trade-count cascade`, plus
  `evidence/profile_smoke.py` and `PIPELINE.md`, Stage 1.
- Equal bias windows: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: identical Spot and Futures bias windows`, plus
  `evidence/profile_bias.py`, `evidence/warmup_convergence.py`, and
  `PIPELINE.md`, Stages 2-3.
- Full-backtest technical closure: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: completed full backtest closes technical work`, plus
  `evidence/strategy_status.py` and `PIPELINE.md`, Stage 7.
- Terminal-exclusion closure: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: exclusions close the work queue`, plus
  `evidence/strategy_status.py` and `PIPELINE.md`.
- Full-backtest non-testability: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: non-testable canonical full backtests are excluded`, plus C10
  in `evidence/exclusion_criteria.py` and `evidence/strategy_status.py`.

## Machine state - authoritative

Run these before trusting any count or prose:

```powershell
docker ps --format '{{.ID}}|{{.Image}}|{{.Status}}|{{.Command}}'
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'strategy-audit|full_backtest|profile_smoke|profile_full_window' } | Select-Object ProcessId,Name,CommandLine
git log --oneline -8
git status --short
.\ftenv\Scripts\python.exe -m evidence.strategy_status --check
```

The status check is read-only. Do not regenerate `STRATEGY_STATUS.csv` while a
runner is writing one of its input stores.

Current counts without reading performance rankings:

```powershell
.\ftenv\Scripts\python.exe -c 'import csv,collections; r=list(csv.DictReader(open(`STRATEGY_STATUS.csv`,encoding=`utf-8-sig`))); print(len(r),collections.Counter(x[`cohort`] for x in r))'
.\ftenv\Scripts\python.exe -c 'import csv,json,collections; r=list(csv.DictReader(open(`STRATEGY_STATUS.csv`,encoding=`utf-8-sig`))); e={x[`strategy_id`] for x in r if x[`cohort`]==`E1_expanded`}; m=json.load(open(`results/regime/full_backtest_manifest.json`,encoding=`utf-8`))[`results`]; print(collections.Counter((m.get(x) or {}).get(`status`,`missing`) for x in e))'
```

## Before starting any benchmark or analyzer

Never assume an empty terminal means idle. Run both process checks above and:

```powershell
Get-ChildItem evidence/PROFILE_SMOKE.json,evidence/PROFILE_FULL_WINDOW*.json,results\regime\*manifest*.json | Select-Object Name,Length,LastWriteTime
Get-ChildItem -Force *.running,results\regime\*.running -ErrorAction SilentlyContinue
```

One writer per output store. Heavy measurements run one at a time. A Docker
CLI timeout is not evidence that no container exists. Inspect processes,
locks, artifact timestamps, and the run log before deciding.

## Last observed machine state

Observed 2026-09-10T20:22:17+02:00 after recording Full-Backtest C10 closure:

- No Docker benchmark/analyzer or evidence writer is active.
- `STRATEGY_STATUS.csv` is current with 1,050 rows: 641 `E1_expanded`, 297
  excluded, 53 exclusion-unconfirmed, 30 too-few-trades, 10 pending and 19
  not-a-strategy. C10 moves 34 formerly E1 rows to excluded: 21 `failed`, 12
  `resource_inconclusive`, and 1 `timeout` in the canonical pooled runner.
  583 current source/profile identities have a successful
  canonical pooled Full-Backtest and therefore `technical_chain_complete=true`;
  none is in `open_work`. All 263 final `excluded` rows now also have empty
  `open_work`; the remaining queue contains 53 `exclusion_unconfirmed` and 10
  `pending` rows only.
- GRID measured 8 trades at one month then timed out at three months; ONS
  measured 8 at one and three months then timed out at one year. Both exhausted
  the 1,800-second recovery budget and need no repeat.
- `evidence/SMOKE_FUNNEL_REVIEW_2026-09-10.md` records all five work packages.
  `strategy_status.html` was regenerated from the current CSV.
- `strategy_status.html` and `tools/STRATEGY_STATUS.template.html` have
  concurrent, uncommitted ready-to-run display edits. Preserve them; they are
  outside the full-backtest closure commit but the regenerated HTML already
  carries the current CSV data.
- The old Spot diagnostic window occurs in 218 `PROFILE_BIAS` rows (174
  look-ahead and 161 recursive diagnostics) and 790 convergence rows. These
  are provenance, not current-window evidence; no measurement rerun started.

## Current implementation checkpoint

Smoke-funnel work packages 1-5 are complete. Ten strategies recovered at least
ten trades: `FastSupertrend`, `FastSupertrendOpt`, `MultiMA_TSL3b`,
`MultiMA_TSL5`, `SMAOPv1_TTF`, `WTHO`, `Schism5`, `QuickBuyStrategy`,
`multi_tf`, and `Solipsis_v4`. They are measurable, not automatically admitted;
their remaining gates still apply. `BestSingleAssetPortfolio` runs but remains
too sparse at 8 trades through one year. Seventeen formerly open rows moved to
confirmed C4/C5 exclusions because no E1-safe repair remains. The status reader
now keeps a current measured smoke record ahead of an older failed repair store.

`Hacklemore3` completed a targeted forced Docker smoke rerun under the frozen
cascade: 11 long trades in the first rung `20200301-20200401`, 857.1 seconds,
with canonical/config/archive/trade hashes recorded in `PROFILE_SMOKE.json`.
Status and HTML were regenerated; it remains admitted and now carries
`trade_evidence=smoke` rather than the older Class-1 result-card fallback.

`evidence/SMOKE_FUNNEL_REVIEW_2026-09-10.md` records the complete disposition.
Of the 74 smoke-stage exclusions, 65 remain terminal on current evidence and 9
C8 string/NaN dtype rows match an existing file-local repair exactly and should
be reopened as bounded repair candidates. Of 32 open rows, 4 have known narrow
repairs, 6 require final resource adjudication, 8 bounded data/dependency/
harness checks, and 14 exact author-provenance checks before likely C4 closure.

Smoke cascade commit `8e435f5` freezes Stage 1 at one month, then three months,
then one year while the completed run remains below ten trades. It stops on the
first rung reaching ten, retains every attempt and unique archive identity, and
does not widen runtime failures. Legacy low-trade smoke records are stale under
this policy; existing results at or above ten trades remain current. The status
Markdown and HTML template describe the cascade and the corrected three-month
Futures bias window. No measurement store changed in that commit.

Base implementation was `0de5829`; the four-model redesign is committed as
`b40ad60` (`Separate coin-only and combined regime gates`).

Eligibility governance correction is committed as `717d1e3` (`Retire invalid
Stage 6 E0 cohort`). `evidence/REGIME_ELIGIBILITY.csv` and the 67-label expansion
inventory remain immutable evidence of the mistaken classification, not usable
membership. Only the latest active `admitted_E1` decision per strategy defines
the cohort; `STRATEGY_STATUS.csv` exposes it as `E1_expanded`.

Strategy classification repair is committed as `a7259ad` (`Complete generated
strategy type classification`). `tools/strategy_classification.py` now reads
the canonical population from `evidence/EXECUTION_PROFILES.csv`, never from its own
downstream status output. All 1,050 rows have an explicit generated Type: no
blank and no current `unclassified`; 19 test/template artifacts are
`not_applicable`. `CORPUS.md` prose was not broadcast from repo to strategy.

Repository cleanup phase 1 archives the predecessor `ANALYSIS`, DCA, depth,
resolvability, old signal/log, and selected-case-study families under
`old/predecessor_audit/`. Graphify confirmed no call/import path from the
current status or regime engine to DCA/depth/resolvability. The exploratory
trailing-sensitivity family was deliberately kept active in root because
Graphify showed its current profile/full-backtest dependencies. Root README is
now about the market-regime benchmark and contains the directory tree.

Cleanup phase 2 is committed as `699512d` (`Group runtime configs and Docker
entry points`). `runtime/` now contains all four Dockerfiles, four requirement
sets, spot/futures base configs, and 15 Docker wrappers. Wrappers resolve the
repository root through their parent, use runtime-local Dockerfiles, retain the
root build context and `/audit` mount, and invoke the same Python entry points.
New runs record `runtime/profile_*_config.json`; old invocation strings remain
immutable historical provenance.

Cleanup phase 3 groups 24 current evidence writers and 60 generated/frozen
stores in the flat `evidence/` package. Every active reader, Docker wrapper,
binding document, generated status link, and pipeline declaration uses the new
path. Root retains the user-facing status outputs and binding documents.

Cleanup phase 4 moves the shared override lookup and local-module restoration
tool from root into the existing `repair/` package. All imports, generated
reports, docs and comments now use `repair.overrides` or
`repair/local_modules.py`; `repair/README.md` defines the directory boundary.

Cleanup phase 5 moves `warmup_convergence.py`,
`market_phase_hypothesis.py`, and `merge_full_window_shards.py` beside their
stores in `evidence/`. The warm-up Docker wrapper uses module invocation and
regime attribution imports the phase helper from the package.

Cleanup phases 6-9 complete the classification. Status/exclusion writers moved
to `evidence/`, run coordination moved to `runtime/`, and trailing sensitivity
moved to `regime/`. The complete predecessor publication family — its ledger,
corpus prose, reports, measurement programs, hard-coded setup program, and
retired CI guards — now lives under `old/predecessor_audit/`. Current corpus
intake/shared utilities live under `tools/`; all active readers of the archived
ledger use its new path. The status HTML template lives with its generator.

The predecessor `verify_ledger.py`, `freeze_guard.py`, `sync_repo.py`, and
`totality.py` are deliberately not current CI gates. The first three govern
the retired publication layout; `totality.py` reports 124 heuristic refusals on
the current pipeline and is not a usable unchanged commit gate. CI now parses
all 94 active Python files recursively, excluding vendored repair overlays,
instead of vacuously checking only root-level Python files.

- `regime/regime_engine.py` produces causal, one-day-lagged four-state data.
- `regime/attribution.py` already attributes Model 0 trades to both four states
  and six reporting phases. It now also retains source strategy and model
  identity when reused for gated candidates.
- `regime/gate_adapter.py` is entry-only. It has independent `btc`, `coin`, and
  `btc_coin` modes; coin-only mode neither reads nor validates a BTC column.
  Missing required local evidence fails closed, and omitted state lists fail.
- `regime/gated_backtest.py` implements resumable Model 1, Model 2, and Model 3
  pooled runners from one explicit candidate spec. It does not choose the spec.
- `regime/gated_attribution.py` validates and attributes gated candidate
  archives. Complete input is the default; `--allow-partial` is explicit.
- `regime/model_compare.py` writes a non-ranked Model 0/1/2/3 long table and
  deltas only after identity, candidate, gate, archive, and timerange checks.
  It enforces that Model 3 reuses Model 1's BTC gate and Model 2's coin gate.
  It does not implement the still-open exposure benchmark.
- `PIPELINE.md` and `DOCUMENT_MAP.md` describe these boundaries.

No production Model 1/2/3 run has been started. No candidate gate was selected.
No performance row or ranking was inspected while writing this code.

The exact E0 reconciliation is complete: 67 historical members, of which 66
were independently admitted to E1 under `converged_clean_gates_v1` and one,
`MacdStrategy`, was excluded. Their E1 standing does not derive from E0.

## Validation completed for this checkpoint

```text
python -m regime.gate_adapter                         PASS
python -m regime.gated_backtest --selftest            PASS including resume
python -m regime.gated_attribution --selftest         PASS
python -m regime.model_compare --selftest             PASS
python -m regime.attribution --selftest               PASS
python -m compileall -q regime evidence/profile_smoke.py       PASS
actual regime_daily load                              PASS 2364 BTC days / 18000 pair-days
gated archive-reader integration on A9AV              PASS 13679 trades
coin-only actual-data load has no BTC series           PASS
combined actual-data load has BTC and coin series      PASS
```

E0-retirement validation at `717d1e3`: `strategy_status.py`,
`tools/eligibility_expansion.py`, `evidence/eligibility_expansion_adjudicate.py`,
`evidence/regime_eligibility.py`, `evidence/eligibility_evidence_gap.py`,
`warmup_convergence.py`, and `exclusion_criteria.py` selftests all PASS;
targeted `compileall` and `git diff --check` PASS. The frozen expansion
generator's `--check` is expected to report its pre-amendment CSV/JSON inputs as
stale after the governing documents changed; do not regenerate them to silence
that historical mismatch.

The historical 5-profile ungated equivalence artifact remains 5/5 exact at
`results/regime/gate_equivalence.json`; do not rerun it without a reason.

Classification validation at `a7259ad`: classifier selftest/check, phase
hypothesis selftest, status selftest/check, status-page selftest, targeted
`py_compile`, generated JSON/CSV identity check, and `git diff --check` PASS.
Graphify was refreshed with Claude's documented `graphify update .` AST-only
path: 1,552 nodes, 2,527 edges, 151 communities, no LLM/API call.
A local fail-open `.git/hooks/post-commit` now runs that exact command when
Graphify and `graphify-out/graph.json` are present. It does not run semantic
extraction and a Graphify failure cannot invalidate the commit.

Cleanup phase 1 validation: Graphify dependency queries, archived DCA read run,
archived scripts `py_compile`, status check, classification check, archived
case-study index check, and `git diff --check`. The old DCA read reproduces its
895-row historical report; it does not affect the current 1,050-row status.

Cleanup phase 2 validation: Graphify dependency query; all PowerShell wrappers
parse; both config JSON files parse; Docker COPY sources resolve inside the root
context; profile-smoke and status selftests PASS; status and classification
checks current; regenerated runtime/exclusion reports; secret gate and
`git diff --check` PASS. No benchmark was started.

Cleanup phase 3 validation: all 18 available evidence-module selftests PASS;
classification check, phase-hypothesis, warm-up, exclusion, status and status-
page selftests PASS; status regeneration/check PASS at 1,050 rows; targeted
compileall, 38 evidence JSON parses, all Docker-wrapper PowerShell parses,
sync-repo selftest, secret gate and `git diff --check` PASS. No measurement or
benchmark store was regenerated.

Cleanup phase 4 validation: Graphify dependency query; local-module selftest,
override-store import over 43 rows, execution-profile, profile-bias and warm-up
selftests, status regeneration/check, classification check, targeted compileall
and `git diff --check` PASS. No benchmark was started.

Cleanup phase 5 validation: Graphify dependency query; warm-up and phase-
hypothesis selftests, attribution selftest, targeted compileall, wrapper parse,
phase-hypothesis regeneration, status regeneration/check, classification check
and `git diff --check` PASS. No benchmark or warm-up measurement was started.

Final cleanup validation: Graphify dependency traversal; active tool import
check; execution-profile, regime-eligibility, strategy-status and status-page
selftests; status and classification freshness checks; HTML regeneration;
compileall including the archive; active-tree AST parse (94 files); secret-gate
selftest; and `git diff --check` PASS. The status page still contains 1,050
rows. No benchmark or analyzer was started.

Equal-window validation: profile-bias, convergence, strategy-status, and HTML-
page selftests PASS; status freshness, targeted compileall, Graphify AST update,
and `git diff --check` PASS. The generated Markdown/HTML window table now shows
`20200301-20200601` for both modes; no measurement store was modified.

Futures recursion-window change: `profile_bias.WINDOWS['futures']` is now
`20200301-20200601`; Spot remains `20190101-20190401`. The preregistration and
pipeline record the owner's prospective decision and why the old one-month
window was an undocumented smoke-window inheritance. `redo_defective()` now
moves a convergence record whose timerange differs from the current frozen
mode window under `superseded`, and accepts the CLI's explicit strategy filter.
Profile-bias and convergence selftests plus targeted compileall PASS. The
productive rerun has not started because Model 0 is still active.

The 2026-09-10 follow-up supersedes the remaining calendar asymmetry:
`profile_bias.WINDOWS` is now `20200301-20200601` for both Spot and Futures.
`profile_bias` archives a stale per-diagnostic result under `superseded` before
rerunning it, so a current PASS cannot silently overwrite its provenance.
`strategy_status.py`, `PIPELINE.md`, the HTML template, generated status files,
and preregistration use the same window. The separate full-analysis windows
remain unchanged because their pair-history/warm-up constraint is not a BTC-
only bias diagnostic.

## Next concrete steps

1. Treat the five smoke-funnel packages as complete; do not repeat their smoke
   or resource attempts while identities and rules match.
2. For the ten recovered at-least-ten-trade rows, run any required output-
   equivalence proof first, then native look-ahead and recursive gates. Only
   rows passing every frozen technical gate may receive a new E1 adjudication.
3. If the owner explicitly continues the measurement queue, derive targets
   only from `pending` and `exclusion_unconfirmed` current identities. Exclude
   every final `excluded`, C10, and `technical_chain_complete=true` row; do not
   use the old 218/790 inventory as a queue because it includes closed cases.
4. Complete remaining Model 0 rows resumably and adjudicate resource-
   inconclusive failures under the existing attempt rules.
5. Resolve the eight OPEN preregistration choices before producing a discovery
   candidate spec or any ranked output. At minimum the owner must decide the
   discovery/validation split, minimum trade/episode evidence, and the
   exposure-matched benchmark construction.
6. Once those choices are frozen, write and hash one explicit candidate spec,
   run the 5-10 strategy pilot, then Model 1, Model 2, Model 3, gated
   attribution, and the non-ranked comparison in the order in `PIPELINE.md`.

## Do not redo

- Smoke-funnel work packages 1-5 recorded in
  `evidence/SMOKE_FUNNEL_REVIEW_2026-09-10.md`, including GRID/ONS 1,800-second
  cascades and the bounded BlueEyes repair chain.

- Corpus intake and the completed eligibility expansion waves.
- Warm-up ladders, native bias diagnostics, or admission decisions already
  represented in current stores.
- The 30 current `too_few_trades` rows: their 6.5-year look-ahead fallback is
  stronger than every rung of the new smoke cascade, so a shorter rerun cannot
  rescue them. Revisit only if the strategy/runtime identity or frozen rule
  changes.
- Identity-matching canonical pooled Full-Backtest rows with `status=measured`:
  they have already completed the technical chain. A later diagnostic-window
  change must not requeue them; preserve their earlier diagnostic records as
  provenance. The sole current identity mismatch is `NostalgiaForInfinityX`.
- Final `excluded` cohort rows: they are closed work cases. Preserve their
  exclusion evidence and reason, but never recreate `open_work` for them.
  `exclusion_unconfirmed` remains a separate unresolved cohort and is not
  covered by this closure rule.
- C10 `full_backtest_not_testable`: the recorded Stage-7 `failed`,
  `resource_inconclusive`, or `timeout` outcome is final by the owner's
  2026-09-10 decision. Do not retry or admit these rows without a new owner
  decision that supersedes the amendment.
- The 5-profile ungated adapter equivalence suite.
- Regime feature generation unless its hashed candle inputs or frozen formula
  change.
- Any measured Model 0 identity-matching archive. The runner is resumable.
- The `Hacklemore3` smoke rerun completed on 2026-09-10; do not repeat it while
  its canonical/config identities match.
- Any live Claude runner or its output store.
- Strategy Type classification and the `a7259ad` artifact regeneration; do not
  hand-edit `STRATEGY_STATUS.csv` or infer per-strategy Type from repo prose.
- Routine Graphify refreshes use `graphify update .` only. Do not substitute
  `graphify extract .`: that performs semantic Markdown extraction and consumes
  API quota. The local post-commit hook already handles AST-only updates.
- Do not move evidence stores back to root or invoke their writers by file
  path. Run them from the repository root as `python -m evidence.<module>`.
- Do not restore predecessor publication programs or retired guards to root.
  Current corpus utilities are under `tools/`; the historical family is under
  `old/predecessor_audit/`. Root is intentionally limited to 22 user-facing or
  repository-level files and contains no Python program.
- Any historical E0 benchmark or attribution as current evidence. Do not rerun
  the old 67, add 67 to E1, or regenerate frozen E0 CSV/JSON artifacts.
- Do not generate a candidate spec from observed strategy performance.
- Do not rank while any required preregistration choice is OPEN.

## Constants - do not rederive

- Spot analysis window: `20200401-20260821`.
- Futures analysis window: `20200301-20260821`.
- Bias/convergence diagnostic window for both Spot and Futures:
  `20200301-20200601`.
- Smoke diagnostic cascade: `20200301-20200401`, `20200301-20200601`, then
  `20200301-20210301`, stopping at the first measured rung with at least 10
  trades.
- Eight-pair pooled canonical universe; pairwise shards are supporting trade
  evidence and do not replace pooled shared-capital mechanics.
- Primary state model: Wilder DMI/ADX(14), causal one-day lag, four states.
- Six reporting phases and fixed volatility thresholds are frozen in the
  2026-09-05 preregistration amendment; they do not replace the four states.
- Model 0 is original entries/exits. Model 1 gates entries on BTC state.
  Model 2 gates entries only on pair-local coin state and does not use BTC.
  Model 3 requires both the Model 1 BTC gate and Model 2 coin gate. Original
  exits remain authoritative.
- Missing local gate evidence fails closed in Models 2 and 3. Model 1 needs
  only the global BTC evidence.
- WSL ceiling remains 14 GB memory plus 4 GB swap. Do not raise it.
- In-container exit `-9` is `resource_inconclusive`, not strategy failure.
  Docker wrapper exit 125 or an unresponsive VM is not a completed attempt.
- Results are identity-bound, atomic, and resumable. Every new runner records
  its invocation and non-command environment/config provenance.
- `technical_chain_complete=true` requires a `measured`, canonical pooled
  Full-Backtest whose source hash and run profile still match the current
  execution profile. It clears `open_work` only, not cohort/adjudication.
- A final `excluded` cohort also clears `open_work`; it does not erase its
  exclusion reason/evidence. `exclusion_unconfirmed` must retain its queue.
- C10 contains exactly the owner-declared canonical Full-Backtest statuses
  `failed`, `resource_inconclusive`, and `timeout`; status or cohort is never
  hand-edited in `STRATEGY_STATUS.csv`.
- E0 is invalid historical provenance only. The current usable population is
  the latest active E1 adjudication set after C10; currently 641 rows, including 66
  independently re-admitted former E0 members.
- The prior long Wave A-C handoff remains recoverable in Git before commit
  `548be09`; current artifacts and this file supersede its stale counts.
