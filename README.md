# Freqtrade market-regime benchmark

This repository builds a reproducible benchmark of public Freqtrade strategies
across different market conditions. It first proves that a strategy loads,
trades, and passes the required look-ahead and recursive-bias checks. It then
measures admitted strategies over one pooled eight-pair portfolio and attributes
their trades to causal BTC and coin-specific regimes.

Counts change as resumable measurements finish, so no document states one. Use
[`strategy_status.html`](strategy_status.html), [`STRATEGY_STATUS.csv`](STRATEGY_STATUS.csv)
or `python -m evidence.pipeline_state --summary`.

## Benchmark models

The frozen primary model is Wilder DMI/ADX(14), calculated from completed daily
candles and shifted by one UTC day. It yields `BULL`, `BEAR`, `SIDEWAYS`, and
`TRANSITION`. A six-phase reporting view additionally separates volatility.

- **Model 0:** original strategy without a regime gate.
- **Model 1:** entries gated by preregistered global BTC states.
- **Model 2:** entries gated only by local coin states; it does not use BTC.
- **Model 3:** entries require both the Model 1 BTC and Model 2 coin gate.

Original exits remain authoritative. The choices that were open before ranking
were all decided on 2026-09-05 and 2026-09-11; discovery is 2020-03-01 to
2023-12-31, validation is 2024-01-01 to 2026-08-20.

## Which document answers which question

**One fact lives in one place.** Every other document points to it instead of
repeating it. That is the rule that keeps them from drifting apart: a number
copied into a second file is the file that will be wrong first.

| Question | Read |
|---|---|
| What is happening right now, what is open, what must not be started? | [`HANDOFF.md`](HANDOFF.md) (live state; run its machine-state commands before trusting any prose) |
| How many strategies are in which state, and why is one excluded? | `evidence/PIPELINE_STATE.json`, [`STRATEGY_STATUS.csv`](STRATEGY_STATUS.csv), [`strategy_status.html`](strategy_status.html), `evidence/exclusion_criteria_list.md`. Never count a raw evidence store |
| What is the check chain, in which order, which program reads and writes what, and what is the rule of each stage today? | [`PIPELINE.md`](PIPELINE.md), Stages 0-13 and "Fixed constants" |
| Why was a rule of the chain made that way, and when? | [`PIPELINE.md`](PIPELINE.md), "Decision record for Stages 0-8" |
| How are strategies admitted (E1/E2/E3), what may be repaired, and how did the waves end? | [`PIPELINE_EXTENSIONS.md`](PIPELINE_EXTENSIONS.md) Part 1; results in [`evidence/ADMISSION_RECORDS.md`](evidence/ADMISSION_RECORDS.md) |
| Execution robustness, the cost screen, 5m and 1m detail candles? | [`PIPELINE_EXTENSIONS.md`](PIPELINE_EXTENSIONS.md) Part 2 (Stage 8b) |
| The validation-window extension? | [`PIPELINE_EXTENSIONS.md`](PIPELINE_EXTENSIONS.md) Part 3 - **on hold**, do not start |
| What binds the regime study: model, windows, Models 0-3, specialist floor, confirmation? | [`REGIME_PREREGISTRATION.md`](REGIME_PREREGISTRATION.md) |
| Why was the study designed that way? | [`REGIME_AUDIT_PLAN.md`](REGIME_AUDIT_PLAN.md) - reference only, it does not bind |
| What went wrong before, why the benchmark is buy-and-hold, and which traps invalidate a conclusion? | [`LESSONS.md`](LESSONS.md) |
| Which image or shim does a strategy need, and which rows never ran? | [`RUNTIME_ENVIRONMENTS.md`](RUNTIME_ENVIRONMENTS.md), [`REPAIR_LIST.md`](REPAIR_LIST.md), `evidence/repair_measures_list.md`, `repair/REGISTER.md` |
| What are the regime labels and their episode counts? | [`REGIME_DATA_REPORT.md`](REGIME_DATA_REPORT.md) |
| Results for a reader | [`regime_specialists.html`](regime_specialists.html), [`regime_gating.html`](regime_gating.html) (rebuilt by `python -m tools.regime_specialists_page`) |
| The regime rotation bot | rule of each variant and its results: [`PIPELINE_EXTENSIONS.md`](PIPELINE_EXTENSIONS.md) Part 4; code in `bot/`, data under `results/regime/rotation_bot/` |
| Rules for the agents | [`CLAUDE.md`](CLAUDE.md), [`AGENTS.md`](AGENTS.md) |

### When two documents disagree

1. The machine state and the generated files win over any prose count.
2. For the regime study, `REGIME_PREREGISTRATION.md` wins over everything.
3. For the rule of a stage, `PIPELINE.md` wins over `HANDOFF.md`; for what is running or open, `HANDOFF.md` wins.
4. `REGIME_AUDIT_PLAN.md` and `LESSONS.md` never override a rule. A proposal in the plan is not a rule.

### Where a new fact goes

A new decision of the chain goes into the Decision record of `PIPELINE.md` and, if it changes a stage, into that
stage's text; a decision of the regime study goes into `REGIME_PREREGISTRATION.md` as a dated amendment; a new
protocol that extends the chain becomes a Part of `PIPELINE_EXTENSIONS.md`; a live state goes into `HANDOFF.md` and is
deleted from there when it stops being live. A new Markdown file needs a row in the table above.

### Reading order for a session that starts cold

1. [`HANDOFF.md`](HANDOFF.md), then its machine-state commands.
2. [`PIPELINE.md`](PIPELINE.md) when deciding what runs next or changing a stage; [`REGIME_PREREGISTRATION.md`](REGIME_PREREGISTRATION.md) before touching anything about regimes, windows or rankings.
3. Only the part of [`PIPELINE_EXTENSIONS.md`](PIPELINE_EXTENSIONS.md) that the task touches. [`LESSONS.md`](LESSONS.md) before choosing a metric or a benchmark.
4. `REGIME_AUDIT_PLAN.md` only for the reasoning behind a specific section; do not read it end to end.

### Generated files - never edit by hand

`STRATEGY_STATUS.{csv,md}`, `strategy_status.html`, `RUNTIME_ENVIRONMENTS.md`, `REPAIR_LIST.md`,
`REGIME_DATA_REPORT.md`, `cluster/CLUSTERS.md`, and in `evidence/`: `ELIGIBILITY_EXPANSION.md`,
`ELIGIBILITY_EXPANSION_ADJUDICATION.md`, `REGIME_COVERAGE.md`, `REGIME_ELIGIBILITY.md` (an invalidated historical
snapshot, provenance only), `SEMANTIC_DUPLICATES.md`, `NEW_REPO_CANDIDATES.md`, `REPO_FRESHNESS.md`,
`exclusion_criteria_list.md`, `repair_measures_list.md`, and the two result pages. `corpus/` holds 896 per-strategy
cards from the intake; open one only when that strategy is in question. `repos/` and `ftenv/` are third-party.

### Where a former document went

Names that still appear in old commits, code comments or evidence stores:

| Former document | Now |
|---|---|
| `DOCUMENT_MAP.md` | this file |
| `ELIGIBILITY_EXPANSION_PLAN.md` | `PIPELINE_EXTENSIONS.md` Part 1 |
| `EXECUTION_ROBUSTNESS_PLAN.md` | `PIPELINE_EXTENSIONS.md` Part 2 |
| `VALIDATION_EXTENSION_PLAN.md` | `PIPELINE_EXTENSIONS.md` Part 3 |
| `BASELINE.md`, `DECISION_INVARIANCE.md`, `CORRECTIONS.md`, `TRAILING_SENSITIVITY_FINDINGS.md` | `LESSONS.md` Parts 1 to 4 |
| `evidence/EXPANSION_WAVE_A_RESULTS.md`, `EXPANSION_STATIC_PROOF_FINDINGS.md`, `EXPANSION_WAVE_C_PREFLIGHT.md`, `EXPANSION_WAVE_C_RESULTS.md`, `EXPANSION_WAVE_C_BIAS_RESULTS.md`, `SMOKE_FUNNEL_REVIEW_2026-09-10.md` | `evidence/ADMISSION_RECORDS.md` Parts 1 to 6 |
| `evidence/GIT_LFS_MIGRATION.md` | `evidence/README.md`, last section |
| chain amendments of `REGIME_PREREGISTRATION.md` (bias windows, smoke cascade, warm-up convergence, closure and exclusion rules, E0 retirement) | `PIPELINE.md`, "Decision record for Stages 0-8"; the old titles are listed in the preregistration under "Amendments that moved" |
| sections 25, 29, 32, 33 of `REGIME_AUDIT_PLAN.md` | `old/regime_audit_plan_2026-09-20/SUPERSEDED_SECTIONS.md` |
| the baton, checkpoints and work orders of `HANDOFF.md` up to 2026-09-20 | `old/handoff/HANDOFF_until_2026-09-20.md` |
| `.codex/CONTINUATION.md` | deleted (a stub that pointed to `HANDOFF.md`) |

## Repository layout

```text
strategy-audit/
├── README.md, HANDOFF.md
│   Entry point and question table; live state
├── PIPELINE.md, PIPELINE_EXTENSIONS.md
│   The check chain with its rules and decisions; what was added to it
├── REGIME_PREREGISTRATION.md, REGIME_AUDIT_PLAN.md, LESSONS.md
│   Binding regime-study rules; design reasoning; traps and corrections
├── STRATEGY_STATUS.{csv,md}, strategy_status.html
│   Current published strategy inventory
├── regime_specialists.html, regime_gating.html
│   Published result pages
├── evidence/
│   Current eligibility/profile writers and their generated evidence stores
├── regime/
│   Regime features, Model 0/1/2/3 runners, attribution, comparison, sensitivity
├── bot/                    Regime rotation bot and its evaluation
├── results/regime/
│   Resumable benchmark manifests, archives, and regime summaries
├── repair/                 Repair tools, compatibility overlays, and provenance
├── tools/                  Manual generators, triage, and publication tools
├── runtime/                Dockerfiles, requirements, configs, and wrappers
├── cluster/                A-priori strategy taxonomy, never an entry gate
├── repos/                  Downloaded upstream sources; not versioned
├── user_data/              Candles and Freqtrade runtime state; not versioned
├── corpus/                 Historical cards still consumed as provenance
├── old/                    Superseded and predecessor-study material
└── graphify-out/           Local generated code graph; not versioned
```

The flat [`evidence/`](evidence/) family keeps each eligibility/profile writer
beside the store it owns. See its README before running or regenerating a store.

## Reproduction and safety

Use `ftenv/Scripts/python.exe` for native commands. Before any benchmark, run
the process, Docker, lock, and artifact checks in `HANDOFF.md`; never start two
writers for one manifest.

```powershell
.\ftenv\Scripts\python.exe -m evidence.strategy_status --check
.\ftenv\Scripts\python.exe tools\strategy_classification.py --check
.\ftenv\Scripts\python.exe -m evidence.strategy_status --selftest
```

After code changes use `graphify update .`. This is the AST-only path. Do not
use `graphify extract .` for routine updates: it performs semantic document
extraction and consumes API quota. A local fail-open post-commit hook runs the
AST-only update when Graphify is installed.

## Interpretation limits

- Admission means technically auditable, not profitable.
- Process exit `-9` is resource-inconclusive, not a strategy defect.
- Pairwise checks do not replace pooled shared-capital backtests.
- Attribution of existing trades is not a gated backtest.
- Missing local regime evidence fails closed for Models 2 and 3.

Historical case studies and side investigations are retained under
[`old/predecessor_audit/`](old/predecessor_audit/).

## Licence

MIT for code. Analysis text may be quoted with attribution.
