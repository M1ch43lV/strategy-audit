# Shared handoff - Codex and Claude

## Baton

- Last agent: claude
- Last update: 2026-08-31T22:05:00+02:00
- Stopped because: a Windows restart killed the full-window job mid-run
- Next agent should: read `DOCUMENT_MAP.md`, then resume the job below and run
  the Wave C bias gates

## Interrupted job - resume it

`profile_full_window.py` was measuring the nine Wave C zero-trade rows in the
pinned runtime, `--workers 1`, sequential by strategy and by pair:

    Matrix Miku_PP_v3 MostOfAll MyStrategyTemplate Obelisk_3EMA_StochRSI_ATR
    ViN ep3mas2 zorkv7_0_0   (then HarmonicDivergence alone, see below)

Log: `user_data/wavec-zero-fullwindow.log`. Not one pair shard finished. Writes
are atomic and resumable, so the same command is simply rerun and skips any
finished shard.

## Objective

Maximize trustworthy regime coverage under the frozen expansion protocol, then
complete Stages 9-12. Rankings remain unread and blocked.

## Read this before anything else

`DOCUMENT_MAP.md` says which of the 31 Markdown files bind, which are
background, and which to skip. A cold session that skips it will either read
1,982 lines of design proposals as if they were frozen rules, or quote 67
eligible strategies when the current number is 75. Both mistakes have happened.

Its single most important line: **`REGIME_PREREGISTRATION.md` binds;
`REGIME_AUDIT_PLAN.md` is reference.**

## Plan pointer

- File: `strategy-audit/ELIGIBILITY_EXPANSION_PLAN.md`
- Now governing: **### Wave C**, plus **## 6** and **## 7**.
- Wave C is explicit: a successful smoke is not eligibility; full measurement
  and both bias gates still follow. Do not improvise a shortcut.

## Machine state - authoritative, check before trusting prose

```bash
cd strategy-audit
docker ps --format "{{.ID}}|{{.Image}}|{{.Status}}|{{.Command}}"   # MANDATORY
python eligibility_warmup_equivalence_queue.py --selftest
git log --oneline -5 && git status --short
```

If `docker ps` prints a container, a measurement is already running. Do not
start a second one: runners share manifests and have no lock.

Last observed (2026-08-31 22:05): HEAD `7c5f03a`, working tree clean except
`_sabotage/`; queue `0 to measure, 0 recoverable`.

## Current checkpoint

- Wave B: COMPLETE and adjudicated. 26 terminal records, 13 `equivalent`,
  13 `not_equivalent`. Eight rows are `admitted_E1`; the other five equivalents
  were refused a static proof on file-specific evidence
  (`EXPANSION_STATIC_PROOF_FINDINGS.md`).
- Wave A: COMPLETE. `Fakebuy` admissible, two excluded on `FOUND` lookahead,
  four terminal pending for reasons that cannot be removed without changing
  what is tested.
- Wave C: measurement COMPLETE, 218 of 218 rows terminal - 53 with trades,
  13 zero-trade, 152 failed. **Zero of the 53 have a bias record yet.** That is
  the largest single piece of open work.
- Wave D: not started. Rows look into the future; the owner has ruled out any
  admission that rests on that, so Wave D can only ever reach E2 or exclusion.
- E0 immutable at 67. E1 currently 67 + 8 = 75, not yet frozen.
- E3 arms so far: trailing-stop sensitivity (`TRAILING_SENSITIVITY_FINDINGS.md`)
  and the four evidenced timeframes (`ELIGIBILITY_TIMEFRAME_EVIDENCE.json`).

## Constants - do not rederive

- Canonical timerange: `20200301-20260821`, all eight pairs pooled.
- Smoke window: `20200301-20200401`. Frozen Stage 6: 67 eligible, 7 pending,
  826 ineligible; coverage 864 PASS.
- Frozen waves: A 7, B 82, C 230, D 124; candidate hash
  `sha256_2374db291d23252c7d6208709e0702ccb37bd6659f66e29a85cccfaab110be04`.
- Windows Application Control blocks compiled DLLs in local venvs; every run
  uses the digest-recorded Docker runtime.
- WSL is `memory=14GB`, `swap=4GB` (`~/.wslconfig`, backups `.bak-20260830`,
  `.bak-20260831`, `.bak-20260831-2`). This was LOWERED from 20/24 GB on
  2026-08-31 and must not be raised back. A 20+24 GB ceiling on a 31.5 GB host
  let one backtest take all memory and then page to the SSD for hours; the host
  became unusable and the run still made no progress. The new ceiling makes a
  runaway fail fast instead, which is the outcome the protocol can record.
- Memory pressure has two signatures. In-container `-9` is the kernel killing
  one process and IS recorded as `resource_inconclusive`. Wrapper exit 125 with
  `error waiting for container: unexpected EOF` is the VM dying; it writes no
  record, so the row stays unclassified and consumes no recovery attempt.
  Never classify a row from the second signature. The small swap exists to keep
  failures in the first, recordable category; do not set `swap=0`.
- `HarmonicDivergence` reached 18.5 GiB on a SINGLE pair shard of the full
  window and never finished one. Treat it as resource-terminal rather than
  raising limits for it: run the other rows first, then attempt it alone.
- Concurrency is limited by MEMORY, not by a file rule. The plan forbids two
  benchmark writers (section 6); a large image build alongside a benchmark has
  also caused OOM on this 31.5 GB host. Run heavy work strictly one at a time.
- Untracked `_sabotage/BrokenOnPurpose.py` is a negative-control fixture. The
  `loadscan`, `anatman` and `sync_repo` selftests fail independently of this work.

## Next concrete steps

1. Finish the full-window job for the nine Wave C zero-trade rows. Run the
   eight cheap rows first and `HarmonicDivergence` alone at the end.
2. Run both bias gates over the 53 Wave C rows that produced trades. This is
   the step that converts measurement into eligibility.
3. Rebuild `strategy-audit-runtime-rl:2026.7` with torch and retest the five
   freqAI rows. Their common blocker is `No module named 'datasieve'`.
4. Decide the 48 timeframe-less rows. Four now have author evidence; the other
   44 would need an invented parameter, so they belong in a labelled E3 arm.
5. Build the family manifest (`family_id` is empty for all 900), freeze E1,
   rerun pooled Stage 7 for newly admitted profiles, then the nine Stage 9
   choices.

## Do not redo

- Stages 1-8, the 19 native imports, the original 67-profile attribution.
- Any Wave B equivalence measurement; all 26 rows are terminal and committed.
- All Wave B recursive/recovery runs and all 26 lookahead runs.
- The Wave C smoke queue: all 218 rows have a terminal result.
- Rows without a second attempt keep their legacy inline shape on purpose; read
  every record through `attempts_of`/`terminal_state`.
- No new E1 profiles in Stage 7 until membership is frozen.

## Blockers / decisions needed

- Owner decision open on the 44 timeframe-less rows (step 4).
- Nine Stage 9 choices remain open; never infer them from generated data.
