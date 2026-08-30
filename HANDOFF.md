# Shared handoff - Codex and Claude

<!--
  Read this whole file, run the Machine state commands, then read only the
  section named under Plan pointer. Machine state overrides prose.
  Overwrite sections in place; never append. Keep this file under 120 lines.
-->

## Baton

- Last agent: codex
- Last update: 2026-08-30T13:23:26+02:00
- Stopped because: required user decision stop before Stage 9 ranking
- Next agent should: wait for the nine user choices, freeze them in the preregistration, then begin Stage 9

## Objective

Complete `REGIME_AUDIT_PLAN.md` autonomously. Stages 1-8 are complete. Stage 9
must not inspect or rank discovery outcomes until the open choices are frozen.

## Plan pointer

- File: `strategy-audit/REGIME_PREREGISTRATION.md`
- Read only the section: **## OPEN before Stage 9 ranking**
- After the user decides, update that file before reading Stage 9 outputs.

## Machine state - authoritative, check before trusting prose

```bash
cd strategy-audit
python -c "import json,collections;d=json.load(open('results/regime/full_backtest_manifest.json'));print('docker:',dict(collections.Counter(v.get('status') for v in d['results'].values())))"
python -c "import json,collections;d=json.load(open('results/regime/full_backtest_native.json'));print('native:',dict(collections.Counter(v.get('status') for v in d['results'].values())))"
git log --oneline -10
git status --short
```

Last observed (2026-08-30 13:23): docker `{'measured': 67}`; native
`{'measured': 19}`; HEAD `Complete pooled Phase A attribution`; status clean.

## Before starting a benchmark - MANDATORY

```bash
docker ps --format "{{.ID}}|{{.Image}}|{{.Status}}|{{.Command}}" | grep -i "regime\|backtest"
```

If this prints a container, a measurement is already running. Do not start a
second one: runners share the manifest and have no lock. Memory-heavy profiles
must use one worker.

## Current checkpoint

- Stage 7 is complete: 67/67 identity-bound pooled profiles, 286,616 trades.
- Attribution accepted 67 archives with zero rejects and zero missing profiles.
- BTC state matched 286,616 trades; coin state matched 285,613. The 1,003 local
  gaps are only `XMR/USDT:USDT` after the documented spot delisting; no imputation.
- Separate BTC-only, BTC x coin, and episode summaries are generated.
- `BuyRegions` measured 15,780 trades in the digest-pinned Python 3.12
  TensorFlow image; the standard Python 3.14 image remains unchanged.
- No strategy-by-regime performance or ranking was inspected.

## Constants - do not rederive

- Canonical timerange: `20200301-20260821`, all eight pairs pooled.
- Stage 6: 67 eligible, 7 pending diagnostics, 826 ineligible; coverage 864 PASS,
  36 PENDING.
- Windows Application Control blocks compiled DLLs in `ftenv` and `.venv`.
  Existing 19 `windows-ftenv` results remain valid; all new runs use Docker.
- Stage 7 runtime IDs and every archive SHA are bound in
  `results/regime/full_backtest_manifest.json`.

## Next concrete steps

1. Obtain one user answer covering all nine `OPEN` choices.
2. Freeze the choices in `REGIME_PREREGISTRATION.md` before inspecting rankings.
3. Run Stage 9 discovery, lock Stage 10 selection, then Stage 11 validation.
4. Complete Stage 12 robustness/exploratory analysis without changing primary rules.
5. Validate, document, commit, and push only to fork `main`.

## Do not redo

- Stages 1-6 are frozen.
- Stage 7 pooled measurement and Phase A attribution are complete.
- Stage 8 ungated equivalence is complete on five profiles.
- The 19 native identity-matching results are already imported.

## Blockers / decisions needed

- The nine choices under the Plan pointer are the only blocker. Do not infer
  them from the generated strategy-regime summaries.
