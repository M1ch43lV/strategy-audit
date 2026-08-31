# Shared handoff - Codex and Claude

<!--
  Read this whole file, run the Machine state commands, then read only the
  section named under Plan pointer. Machine state overrides prose.
  Overwrite sections in place; never append. Keep this file under 120 lines.
-->

## Baton

- Last agent: claude
- Last update: 2026-08-31T06:31:00+02:00
- Stopped because: the unattended turn cannot approve `docker run`, so no new
  measurement could be launched; all non-measurement work was done instead
- Next agent should: run the 20 pending equivalence pairs, then the 2 recoveries

## Objective

Maximize trustworthy regime coverage under the frozen expansion protocol, then
complete Stages 9-12. Rankings remain unread and blocked.

## Plan pointer

- File: `strategy-audit/ELIGIBILITY_EXPANSION_PLAN.md`
- Read only the section: **## 6. Measurement and resource protocol**
- Candidate waves and stopping rules are already frozen; do not improvise them.

## Machine state - authoritative, check before trusting prose

```bash
cd strategy-audit
python -c "import json,collections;d=json.load(open('results/regime/full_backtest_manifest.json'));print('docker:',dict(collections.Counter(v.get('status') for v in d['results'].values())))"
python eligibility_warmup_equivalence_queue.py --selftest
git log --oneline -10
git status --short
```

The queue selftest prints the exact remaining work as `(N to measure, M
recoverable)`; trust it over any count written here. Last observed
(2026-08-31 06:31): docker `{'measured': 67}`; queue `20 to measure, 2
recoverable`; HEAD `cacee9f` plus this turn's commit.

## Before starting a benchmark - MANDATORY

```bash
docker ps --format "{{.ID}}|{{.Image}}|{{.Status}}|{{.Command}}" | grep -i "regime\|backtest"
```

If this prints a container, a measurement is already running. Do not start a
second one: runners share manifests and have no lock. Memory-heavy profiles use
one worker.

## PERMISSIONS - why this turn measured nothing

`.claude/settings.local.json` allows only `Bash(python *)`. Every `docker run`
form (bash, PowerShell, `*_docker.ps1`) needs interactive approval an unattended
turn cannot give; read-only docker commands work. If you hit this wall, do
non-measurement work and say so; never report a blocked run as a failed run.

## Current checkpoint

- Original Stage 7 remains complete: 67/67 pooled profiles, 286,616 trades.
- Equivalence: 6 of 26 records. `AlwaysBuy`/`HourBasedStrategy_5m` exact,
  `Diamond`/`Macd` real non-equivalence, both `BinHV45` rows resource-only.
- Attempt-preserving recovery is implemented and selftested, not yet run.
  `eligibility_warmup_equivalence.py` classifies each pair as `equivalent`,
  `not_equivalent`, `resource_inconclusive`, or `technical_failure`, so a `-9`
  kill or market-load error can no longer be read as failed equivalence.
- `build_record` appends to an `attempts` list and never discards the attempt it
  replaces; legacy inline records read as attempt one. `terminal_state` yields
  `pending_diagnostics` once `MAX_ATTEMPTS` (2) inconclusive runs exist.
- New `eligibility_warmup_equivalence_docker.ps1` mirrors the other runners.

## Constants - do not rederive

- Canonical timerange: `20200301-20260821`, all eight pairs pooled.
- Frozen Stage 6: 67 eligible, 7 pending, 826 ineligible; coverage 864 PASS.
- Frozen waves: A 7, B 82, C 230, D 124; candidate hash
  `sha256_2374db291d23252c7d6208709e0702ccb37bd6659f66e29a85cccfaab110be04`.
- Wave B recovery manifest: 77 finite recoveries, 2 row-local startup=1 cases, 3
  terminal unbounded-prefix dependencies.
- E0 is immutable at 67 and always reported beside E1. E2 drift is sensitivity
  only; behavior-changing work is E3 exploratory.
- Windows Application Control blocks compiled DLLs in local venvs; new runs use
  the digest-recorded Docker runtime. Memory-heavy profiles use one worker.
- WSL memory raised 6 -> 16 GB (`~/.wslconfig`, backup `~/.wslconfig.bak-20260830`)
  because 5.8 GiB reproducibly `-9`-killed pooled runs. Do not lower it yet.
- `BuyRegions` needed tensorflow and was measured alone in pinned image
  `docker:sha256:4ff7fcaa...`; lean image `5dd2dacd...` is current. Both recorded.
- Untracked `_sabotage/BrokenOnPurpose.py` is a negative-control fixture. The
  `loadscan`, `anatman`, and `sync_repo` selftests fail independently of this
  work and reference none of its modules.

## Next concrete steps

1. Run the mandatory Docker check, then
   `.\eligibility_warmup_equivalence_docker.ps1 --limit 1 --timeout 3600`
   repeatedly; 20 pairs remain. One writer only; inspect each stored result.
2. Then spend the two permitted recoveries with the same wrapper plus
   `--recover`. It only revisits rows whose recovery attempt is unused, so it
   cannot overwrite a terminal row. Never reinterpret `-9` or market-load as FAIL.
3. Add static proofs only for exact matches, run adjudication, freeze Wave B.
4. Complete Wave A, then Waves C and D. Build a family manifest before Stage 9.
5. Freeze final E1, run pooled Stage 7 for newly admitted profiles, then obtain
   the nine still-OPEN Stage 9 choices.

## Do not redo

- Stages 1-8, the 19 native imports, and the original 67-profile attribution.
- The paired pilots for `AlwaysBuy`/`HourBasedStrategy_5m`; all Wave B
  recursive/recovery runs and all 26 lookahead runs.
- `AwesomeMacd`, `Diamond`, and `Macd`; their terminal evidence is committed.
- No new E1 profiles in Stage 7 until membership is frozen; do not rewrite the 6
  stored equivalence records (the code normalizes only when an attempt is added).

## Blockers / decisions needed

- No methodological blocker. The only obstacle is the `docker run` permission
  above, which an attended session or a broader allowlist resolves.
- Nine Stage 9 choices remain open; never infer them from generated data.
