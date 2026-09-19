# Evidence stores and their writers

This directory keeps the current technical evidence used to decide whether a
strategy is auditable. It deliberately stays flat: a writer and the store it
owns live together, while user-facing status remains in the repository root.

## One operational read model

`PIPELINE_STATE.json` is the canonical machine-readable overview across the
complete check chain, including the canonical pooled Full-Backtest. It contains
the current mutually exclusive next-action counts, every resolved strategy
row, and the exact producer store selected for measurement, Look-Ahead,
Recursive-Bias, and Full-Backtest evidence. Generate it together with the
published status files by running `python -m evidence.strategy_status`.

Code that needs the same resolution imports `EvidenceStore` from
`evidence.pipeline_state`. Humans and agents that only need counts run
`python -m evidence.pipeline_state --summary`. Never answer a pipeline-wide
question by counting `PROFILE_SMOKE.json`, `PROFILE_BIAS.json`, or another raw
store in isolation.

The files here are not benchmark rankings. They cover canonical execution
profiles, smoke and bias diagnostics, warm-up convergence, phase hypotheses,
coverage, repair provenance, expansion adjudication, and frozen supporting
inventories. Writer utilities that merge these stores live here as well.

## Rules

- Do not hand-edit generated CSV, JSON, or generated Markdown reports.
- Run Python writers as modules from the repository root, for example
  `\.\ftenv\Scripts\python.exe -m evidence.profile_smoke --selftest`.
- Use each program's `--check` or `--selftest` mode before regeneration when it
  exists. Measurements are resumable stores and must have only one writer.
- `ELIGIBILITY_EXPANSION_PLAN.md` remains in the root because it is a binding,
  hand-maintained protocol. `STRATEGY_STATUS.csv`, `STRATEGY_STATUS.md`, and
  `strategy_status.html` remain there because they are the published view.
- Historical E0 files in this directory are provenance only. Current admission
  comes from active `admitted_E1` decisions.

The authoritative reader/writer order is documented in
[`../PIPELINE.md`](../PIPELINE.md). See [`../DOCUMENT_MAP.md`](../DOCUMENT_MAP.md)
for which evidence is binding, current state, or historical provenance.
