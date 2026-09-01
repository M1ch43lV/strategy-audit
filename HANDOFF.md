# Shared handoff - Codex and Claude

## Baton

- Last agent: claude
- Last update: 2026-09-01T03:45:00+02:00
- Stopped because: the Wave C bias queue finished; all 53 rows carry a verdict
- Next agent should: give the adjudicator a Wave C ruleset (step 1 below)

## No job running

Both jobs finished. The nine zero-trade full-window rows and the 53-row bias
queue are complete, and nothing holds the writer position.

## Objective

Maximize trustworthy regime coverage under the frozen expansion protocol, then
complete Stages 9-12. Rankings remain unread and blocked.

## Cold-session checklist - mandatory

`DOCUMENT_MAP.md` says which of the 31 Markdown files bind, are background, or
should be skipped. Without it, the 1,982-line discussion plan has been mistaken
for frozen rules and the current 75 eligible strategies misquoted as 67.

1. Read this file, `DOCUMENT_MAP.md`, and `REGIME_PREREGISTRATION.md` in full.
   The preregistration binds; `REGIME_AUDIT_PLAN.md` is reference only.
2. Read the `ELIGIBILITY_EXPANSION_PLAN.md` sections named under Plan pointer.
   Read it in full when new to the expansion, when the wave changes, or before
   interpreting/changing admission, repair, resource, or stop rules.
3. Read applicable `AGENTS.md` files, if any. None existed at the last check.
4. Run every Machine state command, inspect `git status` and relevant diffs,
   and trust active processes plus atomic artifacts over prose counts.
5. Reconstruct completed, active, and remaining work; obey `Do not redo`.
   Never rerun a measurement merely because a prior session did not witness it.

## STRATEGY_STATUS must be kept current - standing obligation

`STRATEGY_STATUS.md` and `.csv` are the reference for what is known about every
strategy: which passed, which did not and why, when each was tested and where
its results are. **Regenerate them after any measurement, adjudication or
convergence run**, and never edit them by hand:

```bash
python strategy_status.py            # rewrite
python strategy_status.py --check    # is the row data current?
python strategy_status.py --selftest
```

Anchoring the newest results in `STRATEGY_STATUS.md` is the AI session's job,
every time. The published artifact is not: the owner refreshes that manually,
so do not treat a stale page as a reason to skip the regeneration here.

Every freqtrade call is also appended to `user_data/freqtrade_runs.log` with
its full console output - `python runlog.py` reports its size. It rotates at
32 MiB across five generations, so it is bounded; older calls fall off the end
and the per-run logs under `user_data/*_logs/` remain the durable copy.

This is not housekeeping. The canonical manifest silently listed 66 measured
strategies as unmeasured for two days, and that stale field nearly caused three
admissible rows to be refused. A table nobody regenerates becomes a table that
lies, and this one is the first thing a cold session reads.

Two things it must never be allowed to say. It must not report a row as
untested: every one of the 900 was attempted in the corpus sweep, and rows with
no measurement carry the exception their card recorded. And it must not fold a
missing verdict into a failure - `no_verdict_on_*` is a statement about this
audit, not about the strategy.

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

If `docker ps` prints a container, a measurement is already running. Whether a
second one may join it is a question with a definite answer, not a matter of
nerve. Two runners may overlap when all three hold:

1. **Different output stores.** Each runner owns the JSON it writes. Two
   writers on one store lose entries, because each rewrites the whole file.
2. **Disjoint strategies.** The per-strategy scratch directories
   (`user_data/expansion_configs/`, `user_data/profile_bias_strategies/`) are
   named by strategy, so different strategies never collide - the same
   strategy in two runners would.
3. **Nobody regenerates `STRATEGY_STATUS.csv` mid-flight.** A runner reads its
   cohort once at start, so a regeneration cannot move it; but only one process
   should be writing that file at a time.

Check 1 and 2 before starting, in as many lines as it takes:

```bash
python -c "import warmup_convergence as w; print(len(w.cohort('recursive_unsettled')))"
```

`user_data/freqtrade_runs.log` is the one file every runner shares. It is safe
for concurrent writers as of 2026-09-01: each entry is written under a claim
(`runlog._claim`) so no two entries interleave. `python runlog.py --selftest`
proves it with two writers and eighty entries. Before that change, eighty
entries from two writers left seventy-three on disk.

Resources are not the constraint: a run holds about 670 MiB and saturates one
core, against 14 GB and four processors in WSL.

Also useful: `python eligibility_expansion_wave_c_bias.py --selftest` prints
`(53 candidates, N pending)`.

Last observed (2026-09-01 03:45): HEAD `03bb527`; no container running; Wave C
bias queue 53 candidates, 0 pending.

## Current checkpoint

- Wave B: COMPLETE and adjudicated. 26 terminal records, 13 `equivalent`,
  13 `not_equivalent`. Eight rows are `admitted_E1`; the other five equivalents
  were refused a static proof on file-specific evidence
  (`EXPANSION_STATIC_PROOF_FINDINGS.md`).
- Wave A: COMPLETE. `Fakebuy` admissible, two excluded on `FOUND` lookahead,
  four terminal pending for reasons that cannot be removed without changing
  what is tested.
- Wave C: measurement AND both bias gates COMPLETE; see
  `EXPANSION_WAVE_C_BIAS_RESULTS.md`. Of the 53 rows that produced trades,
  **3 passed both gates** - `NowoIchimoku5mV2`, `ObeliskIM_v1_1`,
  `simple_patterns`, all `spot_long`, coverage `PASS`, zero traps. 37 are
  excluded on demonstrated bias, 7 were REFUSED by the recursive analyzer
  rather than judged, and 6 still hold an `NA`.
- The 13 Wave C zero-trade rows are settled. Six genuinely never trade over the
  full window; two are defective in a way a one-month window hid (`Matrix`
  never builds the `coef` column its entry rule reads; `zorkv7_0_0` asks for
  100,000 quantiles from 10,000 samples); four were already measured. None adds
  a usable strategy.
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
- `HarmonicDivergence` has spent its first attempt: 1800 s on ONE of eight
  pairs without finishing, after reaching 18.5 GiB under the old ceiling. Its
  single recovery attempt is deliberately UNUSED. Spend it only when nothing
  better is queued; the cost is hours for one row that must still clear two
  gates. Do not raise the memory ceiling for it.
- Concurrency is limited by MEMORY, not by a file rule. The plan forbids two
  benchmark writers (section 6); a large image build alongside a benchmark has
  also caused OOM on this 31.5 GB host. Run heavy work strictly one at a time.
- Untracked `_sabotage/BrokenOnPurpose.py` is a negative-control fixture. The
  `loadscan`, `anatman` and `sync_repo` selftests fail independently of this work.

## The original sweep is reference, not evidence

The owner's ruling, 2026-09-01: results from the original author's environment
cannot be carried over, because that environment did not establish the
preconditions this audit requires. That is the reason the pre-checks are being
redone at all. `LEDGER.csv`, `LEDGER.md`, `README.md` and `corpus/` are
historical reference. Read them for provenance and for hints; never let one
clear a row.

They cannot simply be moved to `old/`: 15 scripts read `LEDGER.csv` and 35 read
`corpus/`, including `execution_profiles.py` and `regime_eligibility.py`. The
separation that matters is of role, not of directory, and it is done in
`strategy_status.py`, which now attaches an old card's exception as a
"historical hint" and never as a reason.

**The contamination is real and measured.** `regime_eligibility.classify`
promotes a historical spot PASS to a current one when no native verdict exists:

    lookahead = native if native in ("PASS", "FOUND") else historical_lookahead

Futures were handled carefully - a historical PASS is explicitly not inherited
across execution modes - but the same caution was never applied across
environments. Twenty-two of the frozen 67 and eight of the eleven admitted
since carry a look-ahead verdict from the original sweep.

## Next concrete steps

1. **After the convergence run finishes**, re-measure the 30 inherited gates:
   `.\eligibility_evidence_gap_docker.ps1 --limit 30 --timeout 1800`. A FOUND
   there is a real outcome and is reported as one; re-measuring only until the
   answer is convenient would be worse than not re-measuring at all.
2. Give `eligibility_expansion_adjudicate.py` a Wave C ruleset so the three
   survivors can be admitted. It is driven by
   `ELIGIBILITY_EXPANSION_PROOFS.json` and checks `trade_equivalence` and
   `static_proof`; both exist only because a Wave B row needs an adapter to
   obtain a recursive verdict at all. A Wave C row needs no adapter - it passed
   the original gates natively. The Wave C ruleset asserts identity, native
   measurement with trades, both gates `PASS`, coverage `PASS`, trap-free and
   not `behavior_changed`: the original Stage 6 rule, unrelaxed. Rewriting the
   frozen `REGIME_ELIGIBILITY.csv` is not an alternative.
2. Decide the 7 refused rows with the EXISTING Wave B warm-up procedure. Six of
   them (`BB_RPB_TSL`, `BB_RPB_TSL_2`, `BB_RPB_TSL_BI`, `BB_RPB_TSL_BIV1`,
   `MultiRSI`, `pmaxTest`) already hold a look-ahead `PASS`; `epretrace` is
   `NA`. Applying a frozen rule to newly matching rows is what section 6
   requires when an analyzer limit is overcome. A second, softer route is not.
   Note that four of the six are variants of one strategy.
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
- The Wave C bias queue: all 53 rows carry a verdict. The queue refuses to
  re-decide a stored PASS/FOUND and that is correct.
- Rows without a second attempt keep their legacy inline shape on purpose; read
  every record through `attempts_of`/`terminal_state`.
- No new E1 profiles in Stage 7 until membership is frozen.

## Blockers / decisions needed

- Owner decision open on the 44 timeframe-less rows (step 4).
- Nine Stage 9 choices remain open; never infer them from generated data.
