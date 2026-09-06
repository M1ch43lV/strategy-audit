# Shared handoff - Codex and Claude

## Baton

- Last agent: codex
- Last update: 2026-09-06T15:01:02+02:00
- Stopped because: Model 1/2 implementation was validated and committed as `0de5829`; a separate Claude smoke-recovery runner is still active
- Next agent should: inspect the active Claude runner and Git state first; do not start any measurement, regenerate status, or touch its result stores while it is alive

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

`REGIME_AUDIT_PLAN.md` is reference, not the rulebook. For Model 1/2 work read
only sections 12-15, Stages 8-11, cautions 28.1-28.6, and the current decision
entry; do not reread the roughly 2,000-line file end to end.

## Plan pointer

- Binding file: `REGIME_PREREGISTRATION.md`, especially `Analysis order`,
  `Frozen reporting safeguards`, and `OPEN before Stage 9 ranking`.
- Pipeline file: `PIPELINE.md`, Stages 7-11.
- Reference only: `REGIME_AUDIT_PLAN.md`, sections 12-15, Stages 8-11,
  cautions 28.1-28.6, and Decision 0.17-03.
- Eligibility protocol when measurement/admission is involved:
  `ELIGIBILITY_EXPANSION_PLAN.md` sections 6 and 7. The old Wave C pointer is
  retired; all expansion waves are already terminal in current artifacts.

## Machine state - authoritative

Run these before trusting any count or prose:

```powershell
docker ps --format '{{.ID}}|{{.Image}}|{{.Status}}|{{.Command}}'
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'strategy-audit|full_backtest|profile_smoke|profile_full_window' } | Select-Object ProcessId,Name,CommandLine
git log --oneline -8
git status --short
.\ftenv\Scripts\python.exe strategy_status.py --check
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
Get-ChildItem PROFILE_SMOKE.json,PROFILE_FULL_WINDOW*.json,results\regime\*manifest*.json | Select-Object Name,Length,LastWriteTime
Get-ChildItem -Force *.running,results\regime\*.running -ErrorAction SilentlyContinue
```

One writer per output store. Heavy measurements run one at a time. A Docker
CLI timeout is not evidence that no container exists. Inspect processes,
locks, artifact timestamps, and the run log before deciding.

## Last observed machine state

Observed 2026-09-06T15:01:02+02:00 at HEAD `0de5829` after the Model 1/2
checkpoint commit:

- 919 status rows: 608 `E1_expanded`, 219 excluded, 25 pending,
  21 too-few-trades, 27 exclusion-unconfirmed, 18 not-a-strategy, and
  1 convergence candidate.
- Model 0 pooled manifest: 512 stored records. Within current E1:
  328 measured, 182 failed, 1 timeout, 97 missing.
- `docker ps` did not return within 30 seconds. Do not translate that into
  no container running.
- A Claude scratchpad process `run_missing_smoke.py` is active and was observed
  running `Schism5`; it writes `PROFILE_SMOKE.json`. That file gained current
  measurements during this Codex turn and belongs to Claude's live work.
- `PROFILE_FULL_WINDOW_shardA.json`, `_shardB.json`, `_shardTF.json` and temp
  files are untracked live artifacts. `full_backtest_manifest.json` and its
  temp file are also dirty. Do not add, revert, merge, or delete them from the
  Model 1/2 code commit.

## Current implementation checkpoint

Committed as `0de5829` (`Implement identity-bound regime-gated models`).

- `regime/regime_engine.py` produces causal, one-day-lagged four-state data.
- `regime/attribution.py` already attributes Model 0 trades to both four states
  and six reporting phases. It now also retains source strategy and model
  identity when reused for gated candidates.
- `regime/gate_adapter.py` is entry-only. It now treats BTC state as global,
  treats coin state as local, fails closed on missing local evidence, and
  refuses omitted state lists instead of silently allowing every state.
- `regime/gated_backtest.py` implements resumable Model 1 and Model 2 pooled
  runners from an explicit candidate spec. It does not choose the spec.
- `regime/gated_attribution.py` validates and attributes gated candidate
  archives. Complete input is the default; `--allow-partial` is explicit.
- `regime/model_compare.py` writes a non-ranked Model 0/1/2 long table and
  side-by-side deltas only after identity, candidate, gate, archive, and
  timerange checks. It does not implement the still-open exposure benchmark.
- `PIPELINE.md` and `DOCUMENT_MAP.md` describe these boundaries.

No production Model 1/2 run has been started. No candidate gate was selected.
No performance row or ranking was inspected while writing this code.

## Validation completed for this checkpoint

```text
python -m regime.gate_adapter                         PASS
python -m regime.gated_backtest --selftest            PASS including resume
python -m regime.gated_attribution --selftest         PASS
python -m regime.model_compare --selftest             PASS
python -m regime.attribution --selftest               PASS
python -m compileall -q regime profile_smoke.py       PASS
actual regime_daily load                              PASS 2364 BTC days / 18000 pair-days
gated archive-reader integration on A9AV              PASS 13679 trades
```

The historical 5-profile ungated equivalence artifact remains 5/5 exact at
`results/regime/gate_equivalence.json`; do not rerun it without a reason.

## Next concrete steps

1. Let the active Claude missing-smoke queue finish. Its result store and any
   resulting status regeneration are separate from this checkpoint.
2. Re-read Git state after it finishes. Keep all live measurement artifacts
   separate from the already committed Model 1/2 checkpoint `0de5829`.
3. Complete Model 0 coverage and adjudicate resource-inconclusive failures
   under the existing attempt rules. Do not run a second Model 0 writer.
4. Resolve the eight OPEN preregistration choices before producing a discovery
   candidate spec or any ranked output. At minimum the owner must decide the
   discovery/validation split, minimum trade/episode evidence, and the
   exposure-matched benchmark construction.
5. Once those choices are frozen, write and hash one explicit candidate spec,
   run the 5-10 strategy pilot, then Model 1, Model 2, gated attribution, and
   the non-ranked comparison in the order documented in `PIPELINE.md`.

## Do not redo

- Corpus intake and the completed eligibility expansion waves.
- Warm-up ladders, native bias diagnostics, or admission decisions already
  represented in current stores.
- The 5-profile ungated adapter equivalence suite.
- Regime feature generation unless its hashed candle inputs or frozen formula
  change.
- Any measured Model 0 identity-matching archive. The runner is resumable.
- Any live Claude runner or its output store.
- Do not generate a candidate spec from observed strategy performance.
- Do not rank while any required preregistration choice is OPEN.

## Constants - do not rederive

- Spot analysis window: `20200401-20260821`.
- Futures analysis window: `20200301-20260821`.
- Eight-pair pooled canonical universe; pairwise shards are supporting trade
  evidence and do not replace pooled shared-capital mechanics.
- Primary state model: Wilder DMI/ADX(14), causal one-day lag, four states.
- Six reporting phases and fixed volatility thresholds are frozen in the
  2026-09-05 preregistration amendment; they do not replace the four states.
- Model 0 is original entries/exits. Model 1 gates entries on BTC state.
  Model 2 adds pair-local coin state. Original exits remain authoritative.
- Missing gate evidence fails closed.
- WSL ceiling remains 14 GB memory plus 4 GB swap. Do not raise it.
- In-container exit `-9` is `resource_inconclusive`, not strategy failure.
  Docker wrapper exit 125 or an unresponsive VM is not a completed attempt.
- Results are identity-bound, atomic, and resumable. Every new runner records
  its invocation and non-command environment/config provenance.
- The prior long Wave A-C handoff remains recoverable in Git before commit
  `548be09`; current artifacts and this file supersede its stale counts.
