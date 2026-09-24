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
- The binding, hand-maintained protocols are `PIPELINE.md`, `PIPELINE_EXTENSIONS.md` and
  `REGIME_PREREGISTRATION.md` in the root. `STRATEGY_STATUS.csv`, `STRATEGY_STATUS.md`, and
  `strategy_status.html` remain there because they are the published view.
- Hand-written files in this directory: this README, `EXECUTION_PROFILES.md` (what the canonical corpus and the
  execution profiles mean), `ADMISSION_RECORDS.md` (results of the finished expansion waves) and `STRATEGY_IDEAS.json`
  (one paragraph per strategy family plus a note on what changed between its revisions, read out of the code by an LLM
  session - a description, never a measurement).
  Every other `.md` here is generated; see the list in `../README.md`. `tools/strategy_ideas.py` extracts the facts an
  interpretation has to rest on and renders them, but it never writes `STRATEGY_IDEAS.json`: each family names the one
  revision its sentences were read from in `read_from`, with that revision's `source_sha256`, and `--check` fails once
  the corpus has moved past it. The family's other rows are derived from the corpus by stem, so the store does not
  repeat hundreds of hashes to say what the corpus already records.
- Historical E0 files in this directory are provenance only. Current admission
  comes from active `admitted_E1` decisions.

The authoritative reader/writer order is documented in
[`../PIPELINE.md`](../PIPELINE.md). [`../README.md`](../README.md) says which document answers which question.

## Verdict schema

`verdicts.py` holds one closed status vocabulary for the stores above. It is a
read-side layer: it changes how a result is described, never which inputs were
measured, and the raw stores are never rewritten.

A verdict is one statement on exactly one **layer** - `check` (what a gate
found), `execution` (how a run ended), `state` (whether the warm-up ladder
settled), `disposition` (what the pipeline decided about a row), `run`
(operational provenance of an agent run). The layer is what keeps a `PASS` in a
coverage check distinguishable from a `PASS` in an agent run.

Four rules bind every reader:

1. A reason is required for every value except the satisfying one of its layer.
2. Fail closed: an unknown token becomes `UNKNOWN`, which is not a member of any
   layer and is never satisfied. It is reported, not mapped to a pass.
3. An absent value is `UNKNOWN` with reason `missing_value`. "Not verified" is
   never published as "clean".
4. Normalization is bound to `(store, field)`, never global, because `measured`
   does not mean the same thing in the smoke store and in the full-backtest
   manifest.

```powershell
.\ftenv\Scripts\python.exe evidence\verdicts.py --list       # layers and mapping
.\ftenv\Scripts\python.exe evidence\verdicts.py --check      # internal consistency
.\ftenv\Scripts\python.exe evidence\verdicts.py --selftest   # every rule, exercised
```

Two guards protect the boundary in the other direction. Whether stored evidence
is re-measured is decided by identity hashes, so a status word must never enter
one:

- `tools/identity_freeze.py` freezes the key sets of all four identity
  functions, the policy tokens that are hashed into records, and the parameters
  hash of the detail classifier. Adding a key to an identity function is
  allowed, but it has to be edited there too, where the cost - re-measuring that
  store - is written down.
- `tools/verdict_migration_audit.py` walks the real stores, counts every raw
  token at every mapped field, and names the tokens and fields that still need a
  decision. It reads only.

## Git LFS migration record (2026-09-15)

Formerly `evidence/GIT_LFS_MIGRATION.md`, merged here without changes. Read it only when an old local log or transcript
names a pre-migration commit hash.

Date: 2026-09-15

The public repository `M1ch43lV/strategy-audit` was detached from the
`Apex-prim/strategy-audit` fork network before this migration. GitHub reports
`fork=false` and no parent repository.

Only the unpublished history after commit `95a6439` was rewritten. Commits up
to and including `95a6439` retain their original object IDs. The canonical
`results/regime/trade_regime_attribution.csv` changed from a 1,300,248,203-byte
ordinary Git blob to a 135-byte Git LFS pointer with object ID
`sha256:977486f94f97e51bf689189d2775632afd0ce039b37a090a0c7204a4d7bf7799`.

At migration time, no Markdown file outside vendored repositories or
`graphify-out` referred to any of the eleven rewritten commit IDs. The mapping
is retained here nevertheless so old local logs and transcripts remain
traceable.

| Old commit | New commit |
|---|---|
| `7b5e6ab119d1048a4aee9272e5b59b5976354dcc` | `064e752c64de484d9a59c7edb7a9d0da8759a708` |
| `34982aaca4f924b9f334e338b4c44cb2967f0e3f` | `6002828b42b54d6dfb1f9ed41f24c6d928cb66ef` |
| `1fbb64e6bef7c3a3db26454dd703715caa6b41ff` | `82894b80232dc2f8324ccccdbd9f038b81dd78db` |
| `f6807058fe39d8519f53739cfc7e7a5fe519c271` | `9099698f7a60138b78b85d5bd04a3a62183b1831` |
| `f463d861c7b0e6e370b8cfce0115bb4d41ede85f` | `43384819766b6995c5f47f8449944fe81a4fcb0d` |
| `2267ceffd8cdc891dfd0361b3610db8cdfc348ad` | `4ba6b3d55ec317ab2ff9efd02e791d437b5ff837` |
| `d61fc3638f17a4f1e9c2f659743b7252a38127a1` | `b071dc3b011fd273f29c3e703863a3db62bceab9` |
| `127c66ae4edf139d67aea862cf052568c7bb3996` | `34dd01b3be9d136a00652cbb7bfbd06eb228818a` |
| `dda688cf47d599e0b93983fab65f8da079d2ba0d` | `0764a934de5e61e2dcd49632d011894f1a5d92f0` |
| `5026f41350957c6bf549fd1226ee867a478a8725` | `5ce86ad416855831425e76f529f0a2501fff1635` |
| `8a4e10a2f4e687c113a11fda9233f6f64971befe` | `cc13f66b0b265e2b0e58845ce38bcaaf1724a3ff` |

The pre-migration repository is preserved in the verified external bundle
`../strategy-audit-pre-lfs-20260915-074618.bundle`. The post-migration branch
was successfully pushed to GitHub at `0666ba4a0991a7d79246d6bf4b3c8b36b86cf5f8`.
