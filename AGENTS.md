# Public Repository Language

- Write all code comments, docstrings, Markdown documentation, and artifact-template text in English.
- This applies to new content and to text changed during an edit; do not translate unrelated historical material solely for consistency.
- User-facing conversation may remain in the user's preferred language.

# Canonical Pipeline State

- Never count remaining work, measurements, Look-Ahead verdicts,
  Recursive-Bias verdicts, or Full-Backtest coverage from an individual raw
  evidence JSON file.
- Read `evidence/PIPELINE_STATE.json` for the complete machine-readable state,
  or run `python -m evidence.pipeline_state --summary` for current counts.
  `STRATEGY_STATUS.csv` is the equivalent flat published view.
- Import `EvidenceStore` from `evidence.pipeline_state` when code needs
  per-strategy resolved evidence and producer-store provenance.
- Raw evidence files remain separate because each runner owns its writes and
  their distinct provenance is audit evidence. They are inputs, not competing
  summaries of the pipeline.

# Automatic Evidence Finalization

- Every completed canonical check run must publish its result before it is
  reported as finished. Sharded Look-Ahead/Recursive runs merge through
  `python -m evidence.profile_bias_merge`; never copy shard JSON by hand.
- A successful merge or direct canonical bias run must regenerate
  `STRATEGY_STATUS.csv`, `evidence/PIPELINE_STATE.json`, the supporting status
  reports, and `strategy_status.html`. Treat a refresh failure as a failed run
  finalization, not as an ignorable post-processing warning.
- Keep one serialized merge/publication section so concurrent completed shards
  cannot overwrite one another. Identity mismatch or conflicting terminal
  verdicts must stop publication.

## Model routing policy

This policy controls analysis support only. It does not change strategy source,
baselines, preregistration, methodology, gate order, or evidence semantics.

The fixed gate order and default route are:

1. Strategy classification — GPT-5.6 Luna, low reasoning
2. Smoke run — GPT-5.6 Luna, low reasoning
3. Look-ahead bias — GPT-5.6 Luna, low reasoning
4. Warm-up / recursive analysis — GPT-5.6 Luna, low reasoning
5. Full backtest and interpretation — GPT-5.6 Terra, medium reasoning

6. Post-full execution robustness and cost screen — GPT-5.6 Terra, medium reasoning

The controller default is GPT-5.6 Terra with low reasoning. Escalate only for
ambiguous, contradictory, or deep code/methodology cases, in this order:

- GPT-5.6 Sol, medium reasoning
- GPT-5.6 Sol, high reasoning only when Sol medium is insufficient; record why

Every routed run must produce one metadata record through
`tools/run_metadata.py`. The terminal status contract is exactly `PASS`,
`FAIL`, `ESCALATE`, or `ERROR`. `ESCALATE` requires an escalation reason;
`ERROR` is an execution/publication failure and is never a strategy verdict.

### Handoff template

```text
Run ID:
Gate:
Model / reasoning:
Status: PASS | FAIL | ESCALATE | ERROR
Strategy / reference:
Task / command:
Evidence paths or references:
Tool versions:
Previous run ID:
Escalation reason:
Next action:
```

Run metadata is operational provenance only. It must never infer a missing gate
result or reorder the preregistered pipeline.

### Serial pipeline dispatcher

`python -m tools.pipeline_dispatcher` is plan-only.  `--apply` starts exactly
one eligible canonical runner, while `--watch --apply` continues serially after
each completed run.  It refuses to start when Docker already has an active
container or another dispatcher holds its lock.  It reads only the published
`evidence/PIPELINE_STATE.json`, uses the existing gate runners, refreshes the
published state after completion, applies the existing E1 admission command,
and appends one metadata record per dispatched gate.

The dispatcher may select only routine, preregistered routes: source intake and
classification for an explicitly named strategy, then smoke measurement,
native Look-Ahead, warm-up convergence, final Recursive-Bias, coverage
publication, missing E1 pooled Full-Backtests, and the additive post-full
execution-robustness/cost-screen stage. Above 5m it runs the prescribed 5m
detail backtest; at or below 5m it publishes the owner-rule record without a
detail rerun. Repair triage and a zero-trade full-window probe remain
`ESCALATE` conditions, never guessed automation.

### Repair controller

`python -m repair.controller` is the explicit common control plane for the
existing Class 1 and Class 2 repair writers plus source-bound repair
adjudication.  It is plan-only unless `--apply` is passed, runs selected
handlers serially, and refuses to write while a Docker benchmark is active.
It appends orchestration provenance to
`evidence/REPAIR_CONTROLLER.jsonl`; handler evidence stores, provenance, and
the Class 1/Class 2 distinction remain separate.  The pipeline dispatcher must
not invoke it automatically: repair triage remains an escalation boundary.

The controller may retry only an author-evidenced timeframe record with prior
status `timeout`, preserving prior attempts.  Its adjudication store is applied
only when the source-file SHA-256 still matches; no timeout, ambiguous runtime
case, or unverified compatibility candidate is an automatic exclusion.

An owner may explicitly close selected repair branches after triage. Record
such a closure as `exclude_by_user_policy`, never as `refuse_repair`: it is a
hash-bound workload-scope decision, not a statement that a repair is
impossible. The decision must identify its retained repair routes and preserve
the underlying technical triage context.
