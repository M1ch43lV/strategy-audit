# Shared handoff - Codex and Claude

## Baton

- Last agent: claude
- Last update: 2026-08-31T12:00:00+02:00
- Stopped because: clean committed checkpoint; Wave B measurement is finished
- Next agent should: add static proofs for the 13 exact rows, run adjudication,
  then freeze Wave B and move to Wave A

## Objective

Maximize trustworthy regime coverage under the frozen expansion protocol, then
complete Stages 9-12. Rankings remain unread and blocked.

## Plan pointer

- File: `strategy-audit/ELIGIBILITY_EXPANSION_PLAN.md`
- Read only the section: **### 5.1 Zero-warm-up analyzer adapter**
- Condition 6 (the file-specific static proof) is the only unmet gate for the
  13 exact rows. Candidate waves and stopping rules are frozen; do not improvise.

## Machine state - authoritative, check before trusting prose

```bash
cd strategy-audit
python -c "import json,collections;d=json.load(open('results/regime/full_backtest_manifest.json'));print('docker:',dict(collections.Counter(v.get('status') for v in d['results'].values())))"
python eligibility_warmup_equivalence_queue.py --selftest
git log --oneline -10
git status --short
```

The queue selftest prints remaining work as `(N to measure, M recoverable)`;
trust it over any count here. Last observed (2026-08-31 12:00): docker
`{'measured': 67}`; queue `0 to measure, 0 recoverable`; HEAD `4897b9a`; only
`_sabotage/` untracked.

## Before starting a benchmark - MANDATORY

```bash
docker ps --format "{{.ID}}|{{.Image}}|{{.Status}}|{{.Command}}" | grep -i "regime\|backtest"
```

If this prints a container, a measurement is already running. Do not start a
second one: runners share manifests and have no lock.

## Current checkpoint

- Wave B measurement is COMPLETE: 26 terminal records, 13 `equivalent`,
  13 `not_equivalent`, zero inconclusive, zero recoveries left.
- All seven formerly resource-inconclusive rows measured cleanly on their
  recovery attempt and are exactly equivalent: the four BinHV45 variants,
  `Cluc4`, `CombinedBinHAndClucHyperV0`, `Combined_Indicators`. Their first
  attempts were kernel OOM kills, never strategy results.
- The 13 exact rows are NOT yet E1-admitted. Plan 5.1 condition 6 requires a
  file-specific static proof per row; that is the next deliverable.
- Original Stage 7 remains complete and untouched: 67/67 pooled, 286,616 trades.

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
  the digest-recorded Docker runtime.
- WSL is now `memory=20GB`, `swap=24GB` (`~/.wslconfig`, backups
  `.bak-20260830`, `.bak-20260831`). 16 GB without swap was NOT enough: the
  pooled 1-minute profile killed the whole VM. Do not lower these.
- Memory pressure here has two distinct signatures. In-container `-9` is the
  kernel killing one process and IS recorded as `resource_inconclusive`. A
  wrapper exit 125 with `error waiting for container: unexpected EOF` is the VM
  itself dying; it writes no record, so the row stays unclassified and no
  recovery attempt is consumed. Never classify a row from the second signature.
- `BuyRegions` needed tensorflow and was measured alone in pinned image
  `docker:sha256:4ff7fcaa...`; lean image `5dd2dacd...` is current. Both recorded.
- Untracked `_sabotage/BrokenOnPurpose.py` is a negative-control fixture. The
  `loadscan`, `anatman`, and `sync_repo` selftests fail independently of this
  work.

## Next concrete steps

1. Write the file-specific static proofs for the 13 `equivalent` rows (plan 5.1
   condition 6). A full-window match without that proof is E2 evidence, not E1
   admission.
2. Run adjudication and freeze Wave B terminal states.
3. Complete Wave A, then Waves C and D. Build a family manifest before Stage 9.
4. Freeze final E1, run pooled Stage 7 for newly admitted profiles, then obtain
   the nine still-OPEN Stage 9 choices.

## Do not redo

- Stages 1-8, the 19 native imports, and the original 67-profile attribution.
- Any Wave B equivalence measurement. All 26 rows are terminal and committed
  through `4897b9a`; the queue refuses to revisit them and that is correct.
- All Wave B recursive/recovery runs and all 26 lookahead runs.
- Rows that never gained a second attempt keep their legacy inline shape on
  purpose; read every record through `attempts_of`/`terminal_state`, which
  normalize on read. Do not rewrite them just to add the newer fields.
- No new E1 profiles in Stage 7 until membership is frozen.

## Blockers / decisions needed

- No measurement blocker. Docker was restarted and is healthy.
- Nine Stage 9 choices remain open; never infer them from generated data.
