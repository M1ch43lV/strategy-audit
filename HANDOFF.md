# Shared handoff — Codex and Claude

<!--
  PROTOCOL. Read this whole file (it is short by design). Then read ONLY the plan
  section named under "Plan pointer". Do not read REGIME_AUDIT_PLAN.md in full:
  it is ~72 KB and re-reading it every turn is the single largest token cost.

  Overwrite sections in place. NEVER append. This file must stay under 120 lines.
  Prose here goes stale within one turn; the manifests and git log do not, so
  trust them over anything written below.
-->

## Baton

- Last agent: codex
- Last update: 2026-08-30T11:40+02:00
- Stopped because: five-hour usage limit, resets 12:18
- Next agent should: run the Machine state commands, then continue Stage 7

## Objective

Complete `REGIME_AUDIT_PLAN.md` autonomously. Stage 6 is frozen. Stage 7 collects
canonical pooled full-window evidence for all 67 eligible profiles.

## Plan pointer

- File: `strategy-audit/REGIME_AUDIT_PLAN.md`
- Read only the section: **## Stage 7 — Phase A attribution** (line ~1292)
- Read further sections only when Stage 7 is closed out.

## Machine state — authoritative, check before trusting any prose below

Run these first. They are cheap and they are never stale:

```bash
cd strategy-audit
python -c "import json,collections;d=json.load(open('results/regime/full_backtest_manifest.json'));print('docker:',dict(collections.Counter(v.get('status') for v in d['results'].values())))"
python -c "import json,collections;d=json.load(open('results/regime/full_backtest_native.json'));print('native:',dict(collections.Counter(v.get('status') for v in d['results'].values())))"
git log --oneline -10
git status --short
```

Last observed (2026-08-30 11:45): docker `{'measured': 64, 'failed': 3}`; native `{'measured': 19}`
(the transient native `failed: 1` was a blocked-DLL attempt, since removed).
If your own run of the commands disagrees, your run is right and this line is stale.

## In flight

- The 3 remaining docker failures (`BuyRegions`, `NWEv6_new`, `StochRSITEMA`)
  must be finished IN DOCKER. Do NOT retry them in the Windows ftenv.
- `regime/full_backtest.py` imports only results whose timerange, measurement
  scope, canonical source hash, and config hash all match.

## WINDOWS BLOCKER — do not repeat

- Windows Smart App Control / Application Control now blocks EVERY compiled
  native extension DLL under `ftenv` and `.venv` (observed: scipy `_zeros`,
  `_reordering`). Any Windows-native freqtrade backtest fails at import with
  "Eine Anwendungssteuerungsrichtlinie hat diese Datei blockiert" / "DLL load
  failed". The version-matched Windows ftenv is therefore UNUSABLE for new runs.
- Consequence: the 19 already-imported `windows-ftenv` results stay valid (they
  were measured before the policy tightened), but no new native run can be
  produced. `Cluc7werk`/`ClucHAwerk` were only measurable natively before; they
  are already imported, so they need no rerun.
- All new measurements must run in Docker only.

## Constants — do not rederive

- Canonical Stage 7 timerange: `20200301-20260821`, all eight pairs pooled.
- Stage 6 snapshot: 67 eligible, 7 pending diagnostics, 826 ineligible;
  coverage 864 PASS, 36 PENDING.
- Commit `084daaa` was pushed only to fork `M1ch43lV/strategy-audit`.

## Next concrete steps

1. Let the one-worker Docker queue finish the remaining profiles.
2. Repair only operational failures and rerun them in an appropriate pinned
   runtime. Do not change strategy behaviour.
3. Run `python -m regime.attribution` only after 67/67 measured coverage.
4. Stop and ask the user once about the nine open preregistration choices.
5. Implement Stages 9-12 after that decision, validate, document, commit, and
   push only to the fork's `main`.

## Do not redo

- Stages 1-6 are complete and frozen.
- Stage 8 ungated equivalence is complete on five profiles.
- The 19 native identity-matching results are already imported.

## Blockers / decisions needed

- Stage 9 cannot begin until the user freezes the nine `OPEN` choices in
  `REGIME_PREREGISTRATION.md`. This is the only planned user decision stop.
