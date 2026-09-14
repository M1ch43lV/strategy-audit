# Shared handoff - Codex and Claude

## Baton

- Last agent: claude
- Last update: 2026-09-14T21:00:00+02:00
- **Artifact Version 40: three Model 0 archives refreshed, DCA marker added
  (Version 39).** `BuyRegions`, `ClucHAnix_5M_E0V1E`, `FlawlessVictory` had a
  stored native archive from before the canonical timerange last changed -
  `regime/full_backtest.py` skips a strategy whose identity (source/config
  hash) is unchanged regardless of timerange, so these three were silently
  stuck on stale data. Re-ran with `--strategy <id> --force` for all three
  (589/647 measured, unchanged). This mattered beyond the ft_stats.json gap
  that surfaced it: `regime/attribution.py` has no timerange check at all
  (only `measurement_scope` + identity), so these three strategies' regular
  Model 0 regime-attribution rows had *also* been silently built from the
  stale archive the whole time, not just their freqtrade-native summary.
  Re-ran the full Model 0 chain (`attribution.py` -> `specialist_evaluation.py`)
  to fix that: 3,459,380 -> 3,459,038 trades (the three strategies' own
  counts shifted), but every headline figure already quoted throughout the
  artifact held exactly - 1,671/1,757 VALIDATION rows, 379 universal
  candidates. None of the three ever ranked into the regime-specialist
  Top-10 pilot's candidate lists either (checked directly: best LCB among
  them is 0.0094, the weakest already-selected pilot candidate is 0.0354),
  so the frozen 25-strategy/33-candidate pilot and its backtest results are
  untouched by this. `export_ftstats_v2.py` re-run: `ft_stats.json` now
  379/379 (was 376/379), profitable-under-compounding count updated 161/379
  (was 160/376, same ~43%). `export_v9.py` also re-run for
  `regime_full.json`/`universal.json`/`futures_strategies.json` consistency
  (its `gated_compare.json`/`gated_detail.json`/`top5.json` outputs are
  legacy leftovers from the discarded pilot, not referenced by
  `build_v8.py` since Version 36 - harmless that they got rewritten too).
  **Separately, Version 39** added the DCA marker (`#`, same pattern as the
  futures `*`): `position_adjustment_enable == True` AND
  `adjust_trade_position()` actually implemented, checked directly against
  each strategy's own source file (108/1050 verified this way, stricter
  than `STRATEGY_STATUS.csv`'s `strategy_type=grid_dca` marker which is a
  bare substring regex on "position_adjustment_enable"/"dca"/"grid" with no
  True-check and no behavior check - that one hits 121). New file
  `find_dca_strategies.py` (scratchpad) -> `dca_strategies.json`, wired into
  `futuresLabel()` (now marks both symbols) and a new legend callout next
  to the futures one. 35/589 Model 0 strategies, 23/379 universal
  candidates, 5/25 pilot strategies (`BB_RTR`, `OversoldReversion`,
  `cryptotank`, `eltoro1_4`, `eltoro1_4_simple`) are DCA-marked.
- **Artifact Version 38: added a "Fazit: Bringt das Gating etwas?" section**
  answering the user's direct question whether the regime gating actually
  helps. Same-regime, apples-to-apples comparison (Modell 0 in exactly the
  candidate's own target regime vs. Modell 1/2/3) over the 31 single-state
  candidates: Modell 1 16/31 improved (median delta +0.11pp), Modell 2
  9/31 improved (median &asymp;0, 4/31 bit-for-bit identical to Modell 0),
  Modell 3 14/31 improved (median -0.55pp). Modell 2 is near-tautological
  for this candidate pool - they were selected in the first place for
  having an edge in exactly that coin-regime state, so gating on the same
  dimension barely changes anything (real finding, not a bug; does not
  generalize to unselected strategies). Modell 1/3 gate on BTC-regime,
  measured its actual correlation with coin-regime rather than assuming it
  (`regime_daily.csv`, 18,000 rows: 53% label agreement, Cohen's kappa
  0.38 - "fair", not "high") - explains why gating there roughly halves
  the trade count without a coherent payoff, landing near a coin flip.
  DeepSeek-v4-pro critique (`mcp__deepseek-mcp__critique`) of the initial
  assessment found real weaknesses, all incorporated into the final
  write-up: n=31 is too small to claim "no effect" (only "no significant
  effect"), means are outlier-sensitive (FreqForge-score delta median
  &asymp;0 but mean +6 for Modell 1/3, wide IQR), the 31 candidates aren't
  independent (25 base strategies, some covering multiple target regimes),
  and the whole pool is pre-selected on a coin-regime edge so results don't
  generalize to arbitrary strategies. All caveats kept in the artifact
  callout, not just the headline conclusion. No result-data pipeline
  changes - analysis only, using the already-existing Model 0/1/2/3 tables.
- **Artifact Version 37 (on top of Version 36 below), two explicit user
  requests:** (1) the "Freqtrade-eigene Kennzahlen" table now covers all
  379 Universal-Kandidaten instead of the old fixed 10-dollar-winner cut -
  reused `regime.model_compare._load_model0()` (the same identity-checked
  native-archive lookup the Model 0/1/2/3 comparison already uses) rather
  than writing a new archive reader; 376/379 resolve, 3 rejected for
  `model0_timerange_mismatch` (`BuyRegions`, `ClucHAnix_5M_E0V1E`,
  `FlawlessVictory` - their stored native archive predates the current
  canonical timerange and was never rerun). Real, not padded: only 160/376
  (43%) stay profitable under freqtrade's own compounding over the full
  window - very different from the old curated top-10 (10/10 profitable by
  construction), replaced the stale callout that claimed otherwise. First
  export attempt wrote a 178MB `ft_stats.json` (the raw per-strategy
  summary carries `periodic_breakdown` at ~394KB/row and `daily_profit` at
  ~53KB/row, harmless at 10 rows, not at 376) - fixed by whitelisting only
  the fields the table actually renders (was: blacklist just `trades`);
  final file 266KB. New script:
  `export_ftstats_v2.py` (scratchpad). (2) The "Gesamtgewinn: gegatet vs.
  ungegatet" table gained a Ziel-Regime chip filter (Uptrend/Downtrend/
  Sideways/Transition + a 5th "kein Ziel-Regime" chip for the two `-trend`
  candidates) and sortable Modell-0/1/2/3 columns (by each cell's
  `dollar_gain_usd`, missing cells sort last) - previously fully static.
  No result-data pipeline changes for this entry, template/export only.
- **DONE — regime-specialist Top-10 pilot fully replaces the old
  7-strategy/21-candidate pilot, published as artifact Version 36.** Full
  design reasoning (gate design, both DeepSeek-v4-pro critiques, selection
  metric) in `REGIME_AUDIT_PLAN.md`'s addendum after the tier-episode-window
  one; operational detail (exact commands, row counts) in `PIPELINE.md`'s
  addendum after the sideways/transition section - read those two first for
  anything below that needs more context. Short version: 4 symmetric
  single-state gates (`-uptrend`/`-downtrend`/`-sideways`/`-transition`)
  replace the old coupled `-trend` gate as the default, `-trend` kept as an
  optional 5th gate only for the 2 candidates that are both futures-capable
  and have real long AND short trades (`FastSupertrend_optim3_rsi_80`,
  `FSampleStrategy`); selection is direct `episode_excess_lcb` ranking per
  ADX state (not a best-worst spread), over the full per-regime VALIDATION
  pool, deduplicated to one candidate per strategy family. 25 strategies, 33
  candidates - `results/regime/candidate_spec_regime_specialists_v2.json`.
  ADX Uptrend has exactly 1 statistically real specialist in the whole
  589-strategy corpus (`FastSupertrend_optim3_rsi_80`); Downtrend/Sideways/
  Transition each filled a full Top 10.
  **A second, independent bug was found and fixed along the way**:
  `NostalgiaForInfinityX` emits bool-dtype `enter_long`/`enter_short`
  columns instead of the usual int 0/1, and `regime/gate_adapter.py`'s
  `mask()` crashed trying to write a plain `0` into a bool column
  (`TypeError: Invalid value '0' for dtype 'bool'`) - fixed by matching the
  "off" value to the column's own dtype (`False` for bool, `0` otherwise),
  with a selftest case added. Full pipeline run: `gated_backtest.py`
  (33/33 measured per model, `results/regime/model{1,2,3}_backtest_manifest_
  regime_specialists_v2.json`) → `gated_attribution.py`
  (`model{1,2,3}_attribution_regime_specialists_v2/`, 18,638 / 16,994 /
  10,169 trades) → `specialist_evaluation.py`
  (`specialist_evaluation/model{1,2,3}_regime_specialists_v2/`, `--joint`
  for model3; universal candidates 8/0/0 - same BTC-gate-leaves-coin-free
  asymmetry documented for the previous pilot). New export script
  `export_v2_regime_specialists.py` (scratchpad, not `export_v9.py`)
  produces `top10_by_regime.json` (the frozen selection, reproduced from
  Model 0 data, not hand-copied), `gated_compare_v2.json`, and
  `gated_detail_v2.json` - same shape as the old `gated_compare.json`/
  `gated_detail.json`, so the template's existing render functions
  (`renderGatedRegimeTable`, `refreshGatedTables`, `buildChipBar`, etc.)
  needed no changes, only `build_v8.py`'s two placeholder targets moved to
  the new files, plus a new `__TOP10BYREGIME_JSON__` placeholder and a new
  `renderTop10Tables()` function for the four selection tables. Template
  changes: old "Modell 1/2/3 — gegatete Piloten-Kandidaten" section replaced
  wholesale (new heading, callouts explaining the new gate design/selection
  metric/Uptrend-has-only-1-specialist finding); "Gesamtgewinn: gegatet vs.
  ungegatet" table gained a Ziel-Regime column and now reads `candidate_id`/
  `target_regime` directly instead of the old `strategy_id + '-trend'`
  string-concat hack; `CANDIDATE_SUFFIXES` gained `-uptrend`/`-downtrend` so
  the futures asterisk keeps working. Old pilot's result files
  (`model{1,2,3}_attribution_merged/`, `candidate_spec_pilot_v1*.json`,
  `specialist_evaluation/model{1,2,3}/`) intentionally left on disk,
  untouched, no longer referenced anywhere in the artifact.
- **Both items below are now fully done, merged, and published (artifact
  Version 33)** - superseding their own "still outstanding"/"still running"
  notes further down (left in place for the reasoning trail, not as an
  open TODO). Final state: `export_v9.py` computes `trades_total` from
  each model's merged attribution CSV (`MERGED_ATTRIBUTION` dict) instead
  of the old hardcoded `MANUAL_TRADES_TOTAL`; the template's
  `GATED_REGIME_LIST` is all four states; a real, independent bug was
  found and fixed along the way (`futuresLabel()` did an exact-match
  lookup against a gated row's full `candidate_id`, e.g.
  `"AdaptiveRegime-trend"`, which can never match the bare `strategy_id`
  list `FUTURESSTRATEGIES` is keyed on - the futures asterisk had
  silently never rendered in any Modell-1/2/3 row; fixed with a
  `baseStrategyId()` suffix-stripper). Pipeline steps actually run, in
  order: `gated_attribution.py` for each model against the new
  sideways/transition manifest into `modelN_attribution_sideways_transition/`
  (41,874 / 42,678 / 31,282 trades for model1/2/3); concatenated with the
  existing `modelN_attribution/trade_regime_attribution.csv` into a new
  `modelN_attribution_merged/` (70,804 / 69,592 / 53,620 trades - no
  candidate_id overlap, verified before concatenating); re-ran
  `specialist_evaluation.py` against each merged file (`--joint` for
  model3) so `results/regime/specialist_evaluation/model{1,2,3}/` now
  covers all 21 candidates; re-ran `export_v9.py` and `build_v8.py`;
  published. Model 0 also fully re-run with the fixed code (see below):
  BTC VALIDATION rows 1,828 -> 1,671, coin 1,770 -> 1,757; universal
  candidates held at 379, "ADX Uptrend weakest regime" held at 359/379,
  and the 8 fully-consistent `FastSupertrend_*` candidates are the exact
  same 8 strategies as before the tier fix - none of Model 0's most-quoted
  headline numbers actually moved, only the raw VALIDATION row counts and
  whichever individual non-universal rows flipped tier. Committed in two
  commits: `b7b44c8` (the five code fixes + Model 0 data) and a second
  commit for the sideways/transition merge + gated model 1/2/3 data
  (candidate_spec already committed earlier as `results/regime/
  candidate_spec_pilot_v1_sideways_transition.json`).
- User asked for a from-scratch DeepSeek-v4-pro code review of the metric
  code (`regime/specialist_evaluation.py`) and the Model 0/1/2/3
  construction code (`regime/attribution.py`, `regime/gate_adapter.py`,
  `regime/gated_backtest.py`, `regime/gated_attribution.py`,
  `regime/model_compare.py`) while the sideways/transition backtest (see
  entry below) ran in the background - conversation
  "regime-code-audit-2026-09-14". Every fix proposal was checked back with
  DeepSeek before implementing (explicit user instruction), not just the
  first critique taken at face value. Found and fixed:
  1. **Tier-episode-window bug (most consequential):**
     `btc_specialist_table()`/`coin_specialist_table()`/
     `joint_specialist_table()` counted a row's episodes from the
     strategy's *entire* history, not "within the validation window" as
     `REGIME_PREREGISTRATION.md`'s 2026-09-11 amendment explicitly
     requires - verified by grepping that file, not assumed. Only the
     trade count was already validation-scoped. Fixed by filtering to
     `analysis_window == "validation"` before the episode count reaches
     each table. Model 0 re-run: BTC VALIDATION rows 1,828 -> 1,671 (coin
     1,770 -> 1,757); universal-candidate count held at 379 (not
     re-verified row-by-row).
  2. **Sortino mixed time scales** (per-day numerator vs per-trade-level
     denominator, annualized by `sqrt(365)` as if both were daily) - fixed
     to keep both sides trade-level (`ddof=1` downside std) and annualize
     by `sqrt(trades_per_year)`.
  3. **CAGR was worse than the first fix**: `dollar_gain_usd/START_CAPITAL`
     summed many independent $1000 stakes, not one compounding position,
     yet was exponentiated as if it were - observed up to 139,000,000%
     "CAGR" in the full Model 0 corpus. Replaced with a linear,
     non-compounding `annualized_return = mean_profit_ratio *
     trades_per_year`; renamed everywhere (column, function, artifact
     label "CAGR" -> "Rendite p.a.") so it can't be mistaken for a real
     CAGR; new point-scale anchors (0%/20%/100%/300%+) frozen before
     inspecting any value.
  4. **profit_factor convention disagreed between modules** (NaN in
     `attribution.py`'s `_summarize()` vs +inf in
     `specialist_evaluation.py`'s `_freqforge_metrics()` for the identical
     zero-losing-trades case) - unified on +inf; this also surfaced and
     fixed a masked sign bug (`-clip(upper=0)` produces `-0.0`, which would
     have given `-inf` once the `.replace(0.0, np.nan)` mask was removed,
     had it not also been switched to `.clip(upper=0).abs()`).
  5. **"Liquidation-Safety" counted harmless `force_exit`s** (e.g. backtest
     window end), not just true liquidations - split into a strict,
     score-relevant `liquidation_rate` (`exit_reason == "liquidation"`
     only) and a new, purely descriptive `forced_exit_rate` (the old,
     broader definition).
  All five covered by new/updated selftest assertions in
  `regime/specialist_evaluation.py` (a new `TIERBUG` fixture: 6
  pre-2024 episodes vs 2 real validation-window ones, must stay
  `EXPLORATORY`; a new `LIQ1` fixture for the liquidation/forced-exit
  split; rewritten Sortino/CAGR fixtures with directly-computed expected
  values rather than hand-derived literals). Every module's selftest
  passes (`attribution`, `specialist_evaluation`, `gate_adapter`,
  `gated_backtest`, `gated_attribution`, `model_compare`).
  Model 0's full 589-strategy `specialist_evaluation` re-run already done
  (47s). **Still outstanding when this baton is picked up:** rerun
  `export_v9.py` (needs its `cagr`->`annualized_return` rename, already
  done in the scratchpad copy) and the template (renames done: "CAGR"
  column -> "Rendite p.a." everywhere EXCEPT the "Freqtrade-eigene
  Kennzahlen" section, which is a genuinely different, real freqtrade-
  native CAGR field from `model_compare.py` and must stay untouched -
  don't rename `fmtCagr()`/its call site, only `fmtCagrRaw()` which was
  renamed to `fmtAnnualizedReturn()`); then merge the sideways/transition
  data (see entry below) and rebuild/republish the artifact; then update
  `MANUAL_TRADES_TOTAL` in `export_v9.py` (currently hardcoded, will be
  stale once new candidates are merged in) to a computed value instead.
- User asked to extend Model 1/2/3 (BTC-/coin-state gated pooled backtests)
  with ADX SIDEWAYS and ADX TRANSITION gate variants, explicitly flagged as
  a deviation from `REGIME_AUDIT_PLAN.md`'s frozen preregistration (every
  candidate spec so far only gates long->BULL/short->BEAR, a trend-following
  assumption). New candidate spec
  `results/regime/candidate_spec_pilot_v1_sideways_transition.json`: the
  same 7 pilot strategies, each with a new `-sideways` and `-transition`
  candidate_id (14 candidates total), alongside their existing untouched
  `-trend` candidate_id. Unlike BULL/BEAR, SIDEWAYS/TRANSITION carry no
  direction assumption, so the new gates are symmetric - long and short
  both restricted to the same single state
  (`long_btc_states == short_btc_states == long_coin_states ==
  short_coin_states == ["SIDEWAYS"]`, respectively `["TRANSITION"]`), not a
  long/short split. Design frozen and written into `REGIME_AUDIT_PLAN.md`
  §15 addendum and `PIPELINE.md` Stufe 13 *before* any result was inspected,
  same discipline as every other threshold in this project. No code changes
  needed - `regime/gated_backtest.py`, `gated_attribution.py` and
  `specialist_evaluation.py` are already fully regime-value-agnostic (only
  the trend-only candidate specs ever restricted the data to 2 states); the
  new candidates will simply appear as additional rows in the existing
  Model 1/2/3 tables.
  Launched as a background job at 2026-09-14T09:xx (see this repo's
  `run_gated_memwatch.py`-wrapped `python -m regime.gated_backtest` for
  model1, then model2, then model3, sequentially - `--workers 1` each, to
  stay under the 16 GB watchdog cap used for every prior gated run) writing
  to `model{1,2,3}_backtest_manifest_sideways_transition.json`. Still
  running as of this handoff; **whoever picks this up next should check
  whether it finished before doing anything else with it** (`ls -la
  results/regime/model*_backtest_manifest_sideways_transition.json` and
  check for the matching `.running` claim directories under the same
  path). Once complete, the remaining steps are: run
  `gated_attribution.py` for each model against the new manifest into a
  separate `modelN_attribution_sideways_transition/` outdir, concatenate its
  `trade_regime_attribution.csv` with the existing
  `modelN_attribution/trade_regime_attribution.csv` (both already use the
  `candidate_id` column, disjoint IDs, safe to concat), rerun
  `specialist_evaluation.py --trades <concatenated file> --outdir
  results/regime/specialist_evaluation/modelN` (`--joint` for model3) so it
  overwrites the same tables with the enlarged candidate population, then
  update `export_v9.py` (recompute `MANUAL_TRADES_TOTAL` from the merged
  file instead of the hardcoded dict) and the template's
  `GATED_REGIME_LIST` (currently hardcoded to `['BULL', 'BEAR']` at
  `regime_specialists_template.html` with a comment claiming SIDEWAYS/
  TRANSITION rows "never exist in this gated population" - no longer true,
  must become all four states) plus the "Konsistenz" gated-table callout
  (currently says "at most two rows" per candidate, no longer true for the
  new symmetric-gate candidates, which get exactly one row each).
- Added `episode_excess_lcb`/`lcb_grade` to `regime/specialist_evaluation.py`
  (`_episode_excess_lcb()`, `_lcb_grade()`) after the user asked for a
  metric answering "does trading reliably beat B&H, not just get lucky on
  few trades" (rejected raw Profit-Factor: high on very few trades, lower
  but more trustworthy on many, with nothing showing the difference) and
  asked to consult `mcp__deepseek-mcp__ask` (conversation
  "regime-audit-reliability-score", deepseek-v4-pro) before implementing.
  DeepSeek recommended a one-sided 95% lower confidence bound on the mean
  *episode* excess return (`LCB = mean(x_i) - t(0.95,n-1)*se`, x_i = each
  independent episode's own excess return, n = episodes never trades -
  trades inside one episode are correlated draws, not independent ones),
  kept as a metric fully separate from `freqforge_score` so the project's
  "no single composite" rule (`REGIME_AUDIT_PLAN.md` §17) isn't violated
  twice; `lcb_grade` is a Gainium-style A-F letter from fixed thresholds on
  that same bound (A: >+2%, B: 0-2%, C: -2%-0, D: -5%--2%, F: below),
  frozen before any strategy's grade was inspected. Considered and
  rejected: Bayesian hierarchical shrinkage (better multiple-testing
  behavior, meaningfully more complex) and Wilson-score on binary
  beat/no-beat (too simple, discards effect size).
  That discussion surfaced a real, separate bug while designing the
  episode-level input the LCB needs: the *existing* `excess_return`
  averaged `profit_ratio` per **trade**, not per episode - a 50-trade
  episode counted 25x as much toward the mean as a 2-trade one despite
  both being exactly one independent observation. Same class of bug as the
  2026-09-13 dollar-figure fix, just distorting a mean instead of
  inflating a sum. Fixed in new `_episode_pairs()`: sum each episode's own
  trades first, then average that sum across episodes - symmetric with the
  already-correct `mean_benchmark_return`. This changed `excess_return`
  (and everything derived from it: ranking order, Top-N selection,
  universal-candidate counts) across the entire corpus - re-derived every
  specific number the artifact's prose quotes rather than leaving stale
  figures next to fresh data (e.g. "ADX Uptrend weakest regime" 372/379
  (98%) -> 359/379 (94.7%); fully-consistent universal candidates 0 -> 8,
  all eight `FastSupertrend` variants whose actual weakest regime is
  TRANSITION, not BULL; the dollar-vs-percent "paradox" callout's example
  no longer applies - checked the whole Model 0 population, zero rows now
  show dollar-gain-exceeds-B&H-but-negative-excess-return, versus at least
  one before the fix). Added regression selftest cases for both the LCB
  formula and the episode-weighted mean (a 2-episode, wildly divergent
  fixture and a 6-episode uniform one), re-ran Model 0 (full 589) + the
  Model 1/2/3 7-candidate pilot, wired both new columns into all four
  artifact tables plus a dedicated explanatory callout (kept separate from
  the FreqForge-score callout per DeepSeek's advice). Published as artifact
  Version 31. Documented in `REGIME_AUDIT_PLAN.md` §18 addendum (the user
  explicitly asked for plan documentation, not just PIPELINE.md) and
  `PIPELINE.md` Stufe 13.
- Added six FreqForge-inspired scoring metrics (github.com/baxr6/FreqForge)
  to `regime/specialist_evaluation.py`, per (strategy, regime): `profit_factor`,
  `worst_trade`, `liquidation_rate`, `sortino`, `cagr`, `drawdown_since_peak`,
  their six point-scores, and a weighted `freqforge_score` (0-100; Sortino
  25%, Drawdown-control 25%, CAGR 15%, Liquidation-safety 15%, Profit-Factor
  10%, Worst-trade 10%). Purely descriptive - `REGIME_AUDIT_PLAN.md` §17's
  "do not rely on a single composite score" still governs the actual
  ranking rule everywhere else in this module.
  User asked before implementing whether Sortino/Sharpe/Calmar were worth
  adding at all; I gave a multi-hour estimate, the user pointed at
  FreqForge's weighted-category approach as a possible model, and asked me
  to consult `mcp__deepseek-mcp__critique` (deepseek-v4-pro) before writing
  any code. That critique caught two real defects in the plan, not just
  caveats:
  1. The originally-planned CAGR formula compounded `mean_profit_ratio`
     (per-trade average), which is blind to trade count - 10 trades and 50
     trades at +2% each over the same day-span would have produced
     identical CAGR despite 5x the real profit. Fixed: compounds the
     group's actual total return (`dollar_gain_usd / START_CAPITAL`)
     instead.
  2. The plan was to reuse the already-shipped `_regime_drawdown()` (which
     normalizes against capital committed since the *group's first trade*)
     for FreqForge's drawdown-control category. DeepSeek showed this is
     positionally biased: the same -40% trade scores 40% drawdown as a
     group's 1st trade but ~0.4% as its 100th, purely because unrelated
     prior trades inflate the denominator. `_regime_drawdown()` itself is
     untouched (correct for the leverage-detection bound it already
     shipped for); added a separate `_regime_drawdown_since_peak()` that
     resets the committed-capital denominator at every new equity high,
     making the same loss score identically regardless of its position in
     the sequence - verified with DeepSeek's own counterexample as a
     selftest case.
  My own selftest then caught a third bug before anything shipped: a
  perfect-win-rate group (zero losing trades) computed `profit_factor` as
  `-inf` instead of `+inf`, because `-empty_sum.sum()` produces `-0.0` and
  `x / -0.0 == -inf` in IEEE-754 - fixed with `abs()` instead of negation;
  `+inf` now correctly scores 100 (FreqForge's own documented "perfect win
  rate broke the ratio" handling), not 0.
  Sortino/CAGR annualize against `total_regime_days` - the sum of a
  group's own *distinct* episode day-spans (`_regime_days()`, from new
  `btc_episode_days`/`coin_episode_days`/`joint_episode_days` columns
  `attach_benchmark()` now broadcasts from the same episode bounds the
  benchmark returns already use) - not the calendar span between a group's
  first and last matched trade, which would count years of out-of-regime
  gaps as in-regime time. Confirmed with the user before implementing.
  CAGR can still reach extreme values for short episodes (max seen in the
  full Model 0 population: 139,000,000%) - known, accepted, why FreqForge's
  own log-scaling is used for the point-score. Re-ran Model 0 (full 589)
  and the Model 1/2/3 7-candidate pilot; row/tier counts unchanged (purely
  additive columns). NOT yet wired into the artifact - the user's real goal
  (choosing which criterion re-selects the Top-10-per-regime population for
  a full Model 1/2/3 run) is still an open, separate decision.
- Fixed a real bug in `max_drawdown` (below), caught by a user question
  about the published artifact showing drawdowns over 100% and asking if
  those strategies were leveraged: mostly not - it was a normalization bug.
  `_regime_drawdown()` divided the worst peak-to-trough dollar drop by the
  curve's own running *peak*. With many independent $1000-stake trades in
  one regime, the peak stays small while ordinary small losses accumulate
  across hundreds/thousands of trades, so the ratio blew past 100% with no
  leverage at all - `CryptoFrogHO2` (spot, never short) showed 685% regime
  drawdown while its worst single trade ever lost 13%. Checked the whole
  corpus: only 4 of 589 strategies (`VolatilitySystemV2`,
  `WTDMIPRICEDCAStrategyFuture`, `VolatilitySystem`,
  `SMAOffset_Hippocritical_dca_leverage`) have any trade with
  `profit_ratio < -1` (the only way an unleveraged instrument can lose more
  than its own stake) - the other 693/1962 BTC-table rows over 100% were all
  this bug. Fixed by normalizing against capital committed so far
  (`trades-so-far * $1000`) instead of the peak: proved this keeps the
  ratio <= 1.0 whenever every trade's own `profit_ratio >= -1`, so a row
  still over 100% after the fix is a real, precise leverage/over-100%-short
  signal rather than an aggregation artifact. Added a 50-trades-at--5%-each
  regression case (would have shown 250% under the old bug, correctly shows
  5% now) alongside the existing 4-trade hand-computed case (value changed
  from 150/1100 to 150/3000 under the new denominator). Re-ran Model 0 (full
  population) and the Model 1/2/3 pilot; after the fix, zero rows exceed
  100% in either. Added a "Korrektur 2026-09-13" callout to the artifact
  explaining this the same way the 2026-09-12 B&H-dollar bug was disclosed.
  Published as artifact Version 24. No asterisk-marking mechanism was added
  since nothing currently exceeds 100% to mark - revisit once the full
  Model 1/2/3 population run (in progress, see entry below) lands, since it
  includes the 4 strategies above and may produce a genuine >100% row.
- Implemented `max_drawdown` (§19's `worst_regime_drawdown`, the one
  regime-fingerprint field the module's docstring previously flagged as a
  known gap) in `regime/specialist_evaluation.py`: new `_regime_drawdown()`
  builds a per-(strategy, regime) fixed-$1000-stake equity curve from that
  group's own matched trades ordered by `close_date`, and reports the worst
  peak-to-trough relative drop - same no-compounding convention as
  `_fixed_stake_gain()`, same reason (compounding a regime's own trades
  reproduces the exponential-math distortion that function already dropped).
  Wired into `_specialist_table()`, so it is on every btc/coin/joint
  specialist-table row for Model 0 and gated Model 1/2/3 alike; the
  Universal-Kandidaten view gets it for free via the existing
  worst-regime-row merge in `export_v9.py` (`DETAIL_COLS`). Selftest adds a
  hand-computed 4-trade case (+10/-5/-10/+20% -> worst drawdown
  (1100-950)/1100) plus a zero-drawdown case (an all-gains regime never
  dips below its own starting capital). Re-ran all four evaluations (Model 0
  full population + Model 1/2/3 gated, `--joint` for Model 3) to populate
  the new column; row/episode/trade counts and every other column are
  unchanged (drawdown was additive only, not a threshold input). Added a
  "Max Drawdown" column to every strategy-listing table in the artifact
  (BTC-/Coin-Regime-Spezialisten, Universal-Kandidaten - both the
  fully-consistent and full sortable views -, and the gated Model 1/2/3
  tables); the pre-existing whole-period `max_drawdown_account` in the
  separate top-10 ft-stats table is untouched (different metric, different
  table, was already there). Also extended the "ADX-Regime: Definition und
  Zeiträume" section with the six volatility-refined reporting phases
  (`bull_trend`/`bear_trend`/`transition`/`range_quiet`/`range_choppy`/
  `high_vol_shock`, Amendment 2026-09-05) - descriptive text only, per
  explicit user choice: the specialist/universal/gated tables keep grouping
  by the frozen four-state model, since the preregistration itself defines
  the six phases as a reporting layer that "decides nothing." Published as
  artifact Version 22.
- Added `joint_episode_benchmark_return` to `attach_benchmark()` and a new
  `joint_specialist_table()` (behind a `--joint` CLI flag, since it is only
  meaningful for an AND-gated attribution) in `regime/specialist_evaluation.py`,
  on explicit user request: Model 3 (BTC-regime AND coin-regime gate) was
  showing two separate marginal tables (BTC-regime, coin-regime) even though
  both dimensions are gated at once. Trades/dollar-gain were already
  identical between the two tables (same trades); episodes/excess-return
  differed only because BTC-episode and coin-episode are different time
  windows. The new benchmark uses the true overlap of a trade's BTC episode
  and coin episode - the actual condition the AND-gate requires - computed
  per unique (btc_episode_id, coin_episode_id) pair rather than per trade
  (same efficiency pattern as the other two episode benchmarks).
  `joint_specialist_table()` groups by `coin_regime` (not `btc_regime`):
  building it, found that `btc_regime`/`coin_regime` are almost always
  identical for a gated trade but not quite always - 7 of ~22,000 Model 3
  trades disagree (a one-candle signal-vs-fill lag lets either dimension
  advance independently; none reach VALIDATION tier). Not a bug, so not
  asserted away - just resolved by picking one label rather than requiring
  agreement. Selftest covers both the overlap-window math (three distinct
  benchmark values for the same trade: BTC-episode, coin-episode, and their
  intersection) and the mismatched-label case (must not raise). Re-ran
  Model 3 with `--joint`; Model 0/1/2 unaffected (rerun anyway to pick up
  the always-computed-but-unused new column, no output changed except each
  manifest gaining a null `validation_tier_joint_rows` field). Rewired the
  artifact's Model 3 tab to render the one combined table (`GATE_LAYERS.model3
  = ['joint']`) instead of two (`['btc','coin']`); Model 1/2 unchanged.
  Published as artifact Version 20.
- Fixed a real bug in the episode-benchmark change below, caught by the user
  directly in the published artifact: `_specialist_table()` computed
  `benchmark_dollar_gain_usd`/`mean_benchmark_return` by summing/averaging
  over every validated *trade*, but `attach_benchmark()` assigns the same
  episode-level benchmark value to every trade inside that episode - so a
  strategy trading many times within a few episodes counted the same
  buy-and-hold phase once per trade instead of once per episode.
  `Obelisk_TradePro_Ichi_v2_2` (1,230 trades, 40 episodes) showed a
  "B&H-Gewinn" of +$94,882 in the artifact; the real figure is about
  $4,800, roughly 20x smaller. Fixed by deduplicating to one row per
  `(strategy_id, regime_column, coin_pair, episode_id)` before aggregating
  the benchmark column - `coin_pair` is part of the key because a
  BTC-regime episode is one global calendar window shared by all 8 pairs,
  and each pair's own price move over it is a genuinely different
  buy-and-hold stake, not a duplicate. Fixes both the dollar sum and the
  percentage mean (hence `excess_return`) the same way. Added a selftest
  case with two trades sharing one episode, asserting the benchmark dollar
  figure counts it once. Re-ran all four evaluations (Model 0 full
  population, Model 1/2/3 gated) - row/episode/trade counts unchanged (the
  specialist floor never depended on the benchmark), excess-return and
  dollar figures shifted, sometimes by a lot for high-trade/few-episode
  strategies. The "0 of 379 universal candidates still fully consistent"
  headline from the episode-benchmark change survives (BULL is still the
  near-universal weak regime, 372/379 now vs 375/379 before this fix - the
  magnitude changed, the conclusion didn't). Re-exported the artifact's
  data and updated the BULL-callout's specific numbers (strongest candidate
  is now `Hammer`, not `BuyOrDie`). Published as artifact Version 16.
  Also replaced the "Top 5 per regime" card grid with a full sortable/
  filterable/searchable table of every VALIDATION-tier row (1,828 BTC-regime
  rows and 1,770 coin-regime rows) per explicit user request, sortable by
  excess-return, dollar-gain, and benchmark-dollar-gain, filterable by ADX
  state chips - this was Version 15, done just before the bug was caught in
  it (which is exactly how the user spotted the inflated B&H figures).
- Changed `attach_benchmark()`'s benchmark definition in
  `regime/specialist_evaluation.py`, on explicit user request: the coin's
  own spot buy-and-hold is now measured over the *entire* ADX-classified
  regime episode (first classified day through last, from
  `regime_daily.csv`'s `btc_episode_id`/`coin_episode_id`), not just the
  individual trade's own open-to-close interval. Reason given: the
  trade-interval benchmark could not answer "does this strategy time a
  market phase better than simply holding through it" - an unleveraged,
  never-short 1x long trade's own return is mechanically ~ that same
  interval's spot return (minus fees), so it could win only through fee
  drag or asof-timing noise, never through genuine phase-timing skill.
  Implementation: two new columns, `btc_episode_benchmark_return` and
  `coin_episode_benchmark_return`, computed once per distinct (pair,
  episode) rather than per trade (a real efficiency win too - far fewer
  unique episodes than trades). `_specialist_table()` takes a
  `benchmark_column` parameter now; `btc_specialist_table`/
  `coin_specialist_table` pass the new columns. The old `benchmark_return`
  (trade-interval) is kept as-is and still feeds
  `total_dollar_gain_table()`'s regime-agnostic total, which has no single
  market phase to measure against - that output is unchanged (confirmed:
  `strategy_total_dollar_gain.csv` came back byte-for-byte, so `git status`
  doesn't even list it as modified). Selftest extended with a dedicated
  case using the real 2020-01-01..05 candle fixture (100/110/121/108.9/130)
  instead of the flat 2024 tail every other fixture trade lands on, to
  actually distinguish the two benchmarks' math (10% trade-interval vs 30%
  full-episode on the same trade) rather than just checking non-NaN.
  Re-ran all four prior evaluations (Model 0 full population, Model 1/2/3
  gated) - identical row/episode/trade counts throughout (tier assignment
  depends only on episode/trade counts, never on the benchmark), only
  `excess_return` and anything derived from it changed. Headline result:
  of the 379 universal candidates, **0** (was 44) still beat the benchmark
  in all four coin regimes at once - 375/379 (99%) now have BULL as their
  weakest regime, because holding a coin through an entire bull episode is
  a much harder bar than beating its price move over one trade's own
  duration; almost every active strategy misses part of the rally that
  plain holding does not. Regenerated `top5.json`/`universal.json`/
  `gated_detail.json` for the artifact (`gated_compare.json`/
  `total_gain.json`/`ft_stats.json`'s old source data were untouched by
  this change, except `ft_stats.json` was deliberately repointed - see
  below). Updated the `Regime-Spezialisten` artifact throughout: funnel
  counts, a new callout on the BULL finding, an honest empty state for the
  now-zero "vollständig konsistent" table (kept the same 1.0 threshold,
  did not lower the bar to keep a non-empty table), and repointed the
  "Freqtrade-eigene Kennzahlen" section from the now-empty 44-candidate
  cohort to the 10 top dollar-gain winners (data for this was already
  sitting unused in the scratchpad's `winner_ft_stats.json` from an earlier
  turn). Published as artifact Version 10.
- Ran `regime/specialist_evaluation.py` against the Model 1/2/3 gated
  candidate attributions (`results/regime/model{1,2,3}_attribution/
  trade_regime_attribution.csv`), the last open follow-up from this
  module's own docstring. Two real bugs found and fixed getting there:
  (1) `load_trades()` hardcoded a `strategy_id` column and raised on
  `gated_attribution.py`'s output, which names the same slot
  `candidate_id` - fixed with `_detect_id_column()`, auto-detects and
  normalizes to `strategy_id` internally, records which one it found as
  `source_id_column` in the manifest. (2) `universal_table()` raised
  `KeyError: 'worst_regime_return'` whenever a non-empty `coin_table`
  produced zero rows that cover all four coin regimes (the empty-`coin_table`
  guard didn't cover this case) - hit immediately on Model 2 and Model 3,
  where the tighter gate leaves too few trades per regime for any of the 7
  pilot candidates to clear the floor in all four at once. Both fixed with
  selftest coverage (candidate_id round-trip; a non-empty coin_table that
  yields zero universal rows must return an empty, correctly-columned frame,
  not raise). Also fixed a second-order `.gitignore` gap this uncovered:
  `results/regime/specialist_evaluation/model{1,2,3}/*.csv` is three levels
  under `results/regime/`, past both existing `!results/regime/*.csv` and
  `!results/regime/*/*.csv` exceptions - added `!results/regime/*/*/*.csv`.
  Results written to `results/regime/specialist_evaluation/model{1,2,3}/`
  (same 7 pilot candidates as always, `ASDTSRockwellTrading-trend` still
  produces zero validation trades everywhere). Model 1 (BTC-gate): 4/7
  universal candidates, none fully consistent. Model 2 (coin-gate) and
  Model 3 (combined gate): 0 universal candidates - fewer trades per regime
  under tighter gating make clearing the floor in all four simultaneously
  harder with only 7 candidates in the pool. Gated-vs-ungated dollar-gain
  comparison for the 6 candidates with any validation trades: every gate
  shrinks the loss for the three losing strategies (`ADXDM`,
  `ADX_15M_USDT`, `AlmgrenChrissStrategy`), most under the combined Model 3
  gate; every gate also shrinks the gain for the one strategy that was
  already profitable ungated (`BBMod`) - the gate removes losing trades
  outside the trend regime, but removes some winning ones too.
  `AdaptiveRegime` stays roughly flat across all four variants. Added to
  the `Regime-Spezialisten` artifact as a new closing section (tabs per
  model, plus the gated-vs-ungated comparison table).
- Added a dollar-terms view to `regime/specialist_evaluation.py`, on
  explicit user request: alongside the existing benchmark-relative excess
  return (a percentage), also report actual dollar profit/loss.
  `dollar_gain_usd`/`benchmark_dollar_gain_usd`/`excess_dollar_gain_usd` in
  both `btc_specialist_table.csv`/`coin_specialist_table.csv`, plus a new
  regime-agnostic `strategy_total_dollar_gain.csv` (one row per strategy,
  not gated by the specialist floor). First implementation used sequential
  $1000-start reinvestment (each trade multiplying a running balance,
  ordered by `close_date`) - tried, measured against the 7 pilots, and
  dropped: at a few hundred trades the result is dominated by exponential
  math, not strategy quality (one pilot's $1000 became $0.006 over ~3,000
  trades), and it implies a single-position account none of these
  strategies ran (they trade up to 8 pairs concurrently). Replaced with a
  fixed $1000 stake per trade, summed rather than compounded - the total
  dollar P&L if every one of a group's trades had gotten its own fresh
  $1000, never a claim about compounded capital growth. Both choices
  documented in `_fixed_stake_gain()`'s docstring and `PIPELINE.md`'s
  Stufe 13. Re-ran over the full 589-strategy population: 497 get a
  `strategy_total_dollar_gain.csv` row (589 minus the same 92 with zero
  validation-window trades already known from the earlier run), 239/497
  with positive `dollar_gain_usd`, 186/497 beat the benchmark in dollar
  terms too. Largest gain `FastSupertrend_optim_quick` (+$23,492 / 11,065
  trades), largest loss `CryptoFrogHO2` (-$20,280 / 15,692 trades).
- Ran `regime/specialist_evaluation.py` a second time, no `--strategies`
  filter, over the full population currently attributed in Model 0's
  `trade_regime_attribution.csv`: 589 strategies (of 647 eligible - 58 are
  missing from that attribution for reasons `attribution_manifest.json`
  already logs, e.g. archive-hash or canonical-identity mismatch; not
  excluded by this evaluation). Overwrites the pilot-only output directory
  (`results/regime/specialist_evaluation/`) - the pilot's 7 strategies are a
  subset of this run, nothing from it is lost. 36s warm-cache runtime.
  3,459,380 trades; 1,828 `VALIDATION`-tier rows (BTC-regime), 1,770
  (coin-regime); 379 universal candidates (cover all four coin regimes at
  `VALIDATION` tier), of which 44 have `regime_consistency == 1.0` (beat the
  exposure-matched benchmark in every one of their four coin regimes - e.g.
  `wavetrend`, `cryptotank`, `NowoIchimoku1hV2`, `simple_vwap_v1`,
  `SimpleHopt1Along`, `hlhb`, `NASOSv5_mod3`). 92 of 589 strategies produce
  zero rows in either table - no validation-window trade at all, the same
  mechanical reason `ASDTSRockwellTrading` was excluded in the pilot, now at
  scale. Note for reading this output: with ~450-480 `VALIDATION`-tier
  candidates competing per regime column, a rank-1 finish is no longer a
  meaningful "best overall" signal (it's decided by a handful of thin-sample
  strategies with few trades but a lucky mean) - read this per-regime and via
  `universal_strategies.csv`'s `regime_consistency`/`median_regime_excess_return`,
  not by scanning `*_specialist_ranking.csv` for repeat #1s.
  Only remaining open follow-up: the same evaluation against the Model
  1/2/3 gated candidate attributions instead of Model 0's natural trades -
  not yet requested, not done.
- New module `regime/specialist_evaluation.py` (PIPELINE.md Stufe 13) applies
  the 2026-09-11 amendment's rules to an already-produced attribution:
  discovery/validation split, the 5-episode/10-trade specialist floor, and
  the exposure-matched benchmark (coin's own spot buy-and-hold return over
  each trade's own open-to-close interval, via `merge_asof` against 1-minute
  candles). Ranks `VALIDATION`-tier rows only, per regime and per BTC/coin
  source separately, plus a "universal strategy" table (maximin across all
  four coin regimes, only for a strategy that clears the floor in every one
  of them). `worst_regime_drawdown` from `REGIME_AUDIT_PLAN.md` §19 is
  deliberately not produced - it needs an equity-curve reconstruction per
  strategy per regime, a materially bigger feature; documented as a gap, not
  silently dropped. Added two small library additions this needed and
  `regime.attribution`/`regime.gated_attribution` didn't have:
  `summarize_coin()` and `summarize_coin_episodes()`, mirroring the existing
  `summarize_btc()`/`summarize_episodes()` for the coin's own regime instead
  of BTC's - now also written by both modules' `main()` for consistency
  (`strategy_coin_regime_summary.csv`, `strategy_coin_episode_summary.csv`,
  `candidate_coin_regime_summary.csv`, `candidate_coin_episode_summary.csv`).
- First real application: ran against the 7 pilot strategies' Model 0
  (ungated, natural) attribution. Result:
  `results/regime/specialist_evaluation/` - 5 of 7 strategies clear the
  floor for at least one BTC or coin regime, 5 clear it in all four coin
  regimes simultaneously (universal candidates). Two exclusions, both
  correctly mechanical rather than judgment calls: `ASDTSRockwellTrading`
  has all 13,402 trades before 2024-01-01 - zero validation-window trades,
  zero ranking rows, not padded with discovery data. `ADXMomentum` has
  enough episodes (6-12 per regime) but too few trades (3-7, under the
  10-trade floor) - `EXPLORATORY` tier, correctly never ranked despite
  occasionally the largest raw excess return of the seven. Neither was
  special-cased; both are the floor doing exactly what it was frozen to do.
  Not yet run: the same evaluation over the full 647-strategy Model 0
  population, or over the Model 1/2/3 gated candidate attributions instead
  of Model 0's natural trades - both still open follow-ups, not done here.
- First productive Model 1/2/3 run is complete: a PILOT candidate spec
  (`results/regime/candidate_spec_pilot_v1.json`, `candidate_set_id
  pilot_v1_stratified_trend_gate`) with 7 candidates, one per major
  strategy_type category (scalping, mean_reversion, momentum,
  trend_following, volatility_breakout, volume_based, grid_dca), selected by
  a neutral rule agreed with the owner before any candidate ran: within each
  category, the alphabetically-first E1_expanded strategy not already used
  by an earlier category. Every candidate carries the same uniform gate -
  long only in BTC/coin BULL, short only in BTC/coin BEAR - also agreed with
  the owner before running, never chosen after seeing performance.
  `regime/gated_backtest.py --model model1/2/3`, `regime/gated_attribution.py
  --model model1/2/3`, and `regime/model_compare` all ran to completion:
  7/7 candidates measured in every model, `model_comparison.csv` written
  (163 columns, all `SUMMARY_FIELDS` plus per-pair deltas for the 7
  candidates).
- Found and fixed one real bug during the pilot, the same shape as the
  BBRSIS bug from earlier this session: `gated_backtest.py`'s `run()` called
  `profile_smoke.run_one()` without `config_overrides`, so a candidate whose
  strategy only runs under a repair-recovered setting failed outright.
  `ADX_15M_USDT-trend` failed Model 1's first attempt this way (needs
  `timeframe=15m`, recovered from `author_ticker_interval` evidence, not
  freqtrade's default) - `profile_smoke.py`'s own CLI and
  `regime/full_backtest.py` already carried this fix, `gated_backtest.py` was
  a third, previously unaudited caller that did not. Fixed by loading
  `repair.overrides.repair_overrides()` once in `main()` and passing
  `config_overrides=overrides.get(strategy) or None` into `run_one()`, same
  pattern as `full_backtest.py`. Re-running Model 1 afterward correctly
  showed the other 6 candidates `cached` (identity-bound skip untouched) and
  only the fixed one `measured` - live confirmation the existing skip logic
  works, not just the new fix.
- This is a `PILOT` role, seven strategies, explicitly not a `DISCOVERY` or
  `VALIDATION` run and not ranked - `model_compare.py` still only places
  mechanical deltas side by side, per its own docstring. Do not read
  `model_comparison.csv`'s deltas as a specialist or universal finding; that
  evaluation (the exposure-matched benchmark, the 5-episode/10-trade
  specialist floor, discovery/validation split) is still unapplied to this
  output and is the next real step, not this one.
- Also done: extended the same incremental-cache and vectorisation fix from
  `regime/attribution.py` to the Model 1/2/3 path, proactively - neither had
  run productively yet, but both had the identical shape of problem waiting.
  `regime/gated_attribution.py`'s `_load_archives()` and
  `regime/model_compare.py`'s `_load_model0()` both called
  `attribution._file_sha`/`attribution.archive_inventory` with no cache, so
  every candidate's archive would have been re-hashed on every run even
  though `regime.attribution` now shares one persistent
  `ATTRIBUTION_ARCHIVE_CACHE.json` for exactly this; both now load and save
  that same cache. `model_compare.py`'s `_metrics()` also had its own scalar
  per-trade Python loop (summing position time and stake*leverage*duration)
  independent of `attribution.attribute()`'s, run once per candidate per
  model - pulled out into `_trade_exposure_seconds()`, vectorised the same
  way. `gated_backtest.py` (the actual Model 1/2/3 Freqtrade runner) already
  had identity-bound skip-if-unchanged logic before this session touched
  anything; it needed no change. Verified: all four modules'
  `--selftest`s pass, plus a hand-built scalar-vs-vectorised comparison
  across edge cases (zero stake, zero leverage, missing keys, negative
  values, multiple trades) for `_trade_exposure_seconds()` - exact match on
  every case. Not yet exercised at production scale, since no candidate spec
  exists yet; correctness rests on the selftest and edge-case checks, not a
  before/after production run like the Model 0 fix had.
- Also done since the attribution note below: the owner and Claude walked
  through all nine `OPEN before Stage 9 ranking` entries in
  `REGIME_PREREGISTRATION.md` together and decided every one. See
  `Amendment 2026-09-11: the eight OPEN pre-Stage-9 choices are resolved` in
  that file for each decision and its reasoning. Summary: discovery/validation
  split frozen as proposed (through 2023-12-31 / from 2024-01-01); specialist
  status needs 5 validation-window episodes and 10 trades together; the
  exposure-matched benchmark is invested only during the strategy's own
  exposure intervals; SER stays continuous, no hard categories; the 90-day
  return classifier is frozen at +/-20 percent; breadth stays the 8-pair
  universe with an availability-aware denominator; forced exit on regime
  change stays out of Model 1/2/3, sensitivity-test only; portfolio-level
  allocation is explicitly deferred, not decided, for version 1.
  `PIPELINE.md`'s Stufe-12 note is updated to match. A candidate spec and a
  productive Model 1/2/3 run are now unblocked by preregistration; nothing
  about admission, technical eligibility, or measured data changed.
- Stopped because: work item complete, not a live blocker. The owner asked
  Codex to hold off on `regime/attribution.py` and everything under
  `regime/` that reads its output while this was in progress; that hold is
  now lifted.
- What changed: `regime/attribution.py` gained a per-archive cache
  (`results/regime/ATTRIBUTION_ARCHIVE_CACHE.json`, keyed on each archive's
  file size+mtime) that skips the whole-file SHA-256 and the trades-JSON
  dedup digest for an archive that has not moved since it was last verified,
  and `attribute()` was rewritten from a scalar per-trade Python loop into
  vectorised pandas operations (flatten trades once, then one `pd.to_datetime`
  pass, one `drop_duplicates` pass, one merge against `regime_daily.csv`, and
  a small second merge only for the rows the first one missed - the
  documented XMR/USDT delisting gap). Root cause was confirmed by reading the
  source, not assumed: no incremental path existed anywhere in the module,
  and archive verification plus the trade loop both re-ran in full on every
  invocation regardless of what had changed.
- The pending unmodified-script run mentioned in the previous note (started
  11:45) was stopped deliberately once the rewrite was tested (it was still
  running past 12:37, superseded by the change in progress, not left to
  finish). The new version then ran for real: cold-cache 4m18s, warm-cache
  3m34s, against 52+ minutes and rising for the old scalar version on the
  same corpus. `coin_regime_unmatched_trades` stayed bit-for-bit identical at
  10,918 (all `XMR/USDT:USDT`, the documented delisting boundary) across the
  rewrite, which is the strongest evidence its join logic matches the
  original - a regression there would almost certainly have moved that
  number. `regime.attribution --selftest` and a hand-built edge-case check
  (window boundaries, cross-archive dedup, cache hit/miss) both pass.
  `attribution_manifest.json` now reports `eligible_profiles=647`,
  `accepted_archives=589`, `trades=3459380` - current.
- Not committed yet on this line: `results/regime/trade_regime_attribution.csv`
  regenerates at ~1.3 GB, over GitHub's 100 MB push limit with no Git LFS set
  up here - same standing issue as before this change, unrelated to it. It is
  current on disk, just not pushed.
- Next agent: no action required on `regime/attribution.py` itself. If
  touching it, keep the cache-then-vectorised shape rather than reverting to
  the scalar loop - the numbers above are the baseline to reproduce.

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

`REGIME_AUDIT_PLAN.md` is reference, not the rulebook. For Model 1/2/3 work read
only sections 12-15, Stages 8-11, cautions 28.1-28.6, and the current decision
entry; do not reread the roughly 2,000-line file end to end.

## Plan pointer

- Binding file: `REGIME_PREREGISTRATION.md`, especially `Analysis order`,
  `Frozen reporting safeguards`, `Amendment 2026-09-03: E0 is retired as a
  separate cohort`, and `OPEN before Stage 9 ranking`.
- Pipeline file: `PIPELINE.md`, Stages 7-11.
- Reference only: `REGIME_AUDIT_PLAN.md`, sections 12-15, Stages 8-11,
  cautions 28.1-28.6, Decision 0.17-03, Decision 0.22-01, and Decision 0.23-01.
- Eligibility protocol when measurement/admission is involved:
  `ELIGIBILITY_EXPANSION_PLAN.md` sections 6 and 7. The old Wave C pointer is
  retired; all expansion waves are already terminal in current artifacts.
- Futures recursion retest: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-09: three-month Futures recursion window`, plus
  `evidence/profile_bias.py` and `evidence/warmup_convergence.py`.
- Smoke trade-count escalation: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: fixed smoke trade-count cascade`, plus
  `evidence/profile_smoke.py` and `PIPELINE.md`, Stage 1.
- Equal bias windows: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: identical Spot and Futures bias windows`, plus
  `evidence/profile_bias.py`, `evidence/warmup_convergence.py`, and
  `PIPELINE.md`, Stages 2-3.
- Diagnostic order: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-11: warm-up convergence precedes final recursive-bias`, plus
  `evidence/profile_bias.py` and `PIPELINE.md`, Stages 2-3.
- Full-backtest technical closure: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: completed full backtest closes technical work`, plus
  `evidence/strategy_status.py` and `PIPELINE.md`, Stage 7.
- Terminal-exclusion closure: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: exclusions close the work queue`, plus
  `evidence/strategy_status.py` and `PIPELINE.md`.
- Full-backtest non-testability: `REGIME_PREREGISTRATION.md`, amendment
  `2026-09-10: non-testable canonical full backtests are excluded`, plus C10
  in `evidence/exclusion_criteria.py` and `evidence/strategy_status.py`.
- Stage-9 Model-0 attribution: `PIPELINE.md`, Stages 8-9;
  `REGIME_PREREGISTRATION.md`, `Analysis order` and `OPEN before Stage 9
  ranking`; `regime/attribution.py`.

## Machine state - authoritative

Run these before trusting any count or prose:

```powershell
docker ps --format '{{.ID}}|{{.Image}}|{{.Status}}|{{.Command}}'
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'strategy-audit|full_backtest|profile_smoke|profile_full_window' } | Select-Object ProcessId,Name,CommandLine
git log --oneline -8
git status --short
.\ftenv\Scripts\python.exe -m evidence.strategy_status --check
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
Get-ChildItem evidence/PROFILE_SMOKE.json,evidence/PROFILE_FULL_WINDOW*.json,results\regime\*manifest*.json | Select-Object Name,Length,LastWriteTime
Get-ChildItem -Force *.running,results\regime\*.running -ErrorAction SilentlyContinue
```

One writer per output store. Separate-output shards may run in parallel only
when identities are disjoint and `evidence.profile_bias_merge` will merge them
after all writers finish. A Docker CLI timeout is not evidence that no
container exists. Inspect processes, locks, artifact timestamps, and the run
log before deciding.

## Last observed machine state

Observed 2026-09-11T07:05:44+02:00 while recovering the ten strategy gates:

- The isolated canonical `Schism5` Look-Ahead process remains active through
  `profile_freqtrade.py`; its worker CPU counters continue increasing with
  about 768 MB working set. Canonical `PROFILE_BIAS.json` writes only after a
  completed diagnostic, so its `06:18:26+02:00` write time is expected. The
  completed disjoint shards are `FastSupertrend=FOUND`,
  `FastSupertrendOpt=PASS`, `MultiMA_TSL3b=PASS`, `WTHO=PASS`, `multi_tf=PASS`,
  and `Solipsis_v4=NA`; merge only after `Schism5` ends.
- The owner ordered Look-Ahead before Recursive-Bias for future work.
  `profile_bias.py` prevents recursive execution after `FOUND`, and `NA` also
  blocks follow-up. The selftest and targeted compile passed; `PIPELINE.md` and
  preregistration amendment 2026-09-11 now record the same rule.
- The owner refined that rule: the prospective chain is Look-Ahead PASS, then
  the fixed warm-up convergence ladder, then final Recursive-Bias using the
  ladder's selected startup value. `profile_bias.py` defers final recursion
  until both prerequisites exist; `warmup_convergence.py` has a
  `lookahead_pass` cohort and explicit reruns archive old ladder evidence.
- The six recovered rows were repeated in the corrected order. Each now has a
  current three-month ladder and final Recursive PASS: `SMAOPv1_TTF=2016`,
  `QuickBuyStrategy=168`, `FastSupertrendOpt=24`, `WTHO=360`, `multi_tf=288`,
  `MultiMA_TSL3b=2016` startup candles. All are `convergence_candidate`; no
  admission was inferred from this technical result alone.
- The owner then directed their admission. `evidence.eligibility_admit_converged
  --apply` admitted exactly those six under `converged_clean_gates_v1`; status
  regenerated to 647 E1 rows. A canonical pooled six-strategy Full-Backtest
  began at `2026-09-11T07:30:54+02:00` with two workers. Five records are
  `measured`; the final `MultiMA_TSL3b` native worker remains CPU-active at
  about 2.8 GB, well below the 14 GB ceiling. No attribution writer is active.

- The previous targeted `NostalgiaForInfinityX` current-overlay pooled
  Full-Backtest completed `measured` in 674.1 seconds with 259 trades. Its
  manifest source/config identity now matches the current repair overlay.
- The former ten-row look-ahead batch ended unexpectedly. Persisted look-ahead
  records are `SMAOPv1_TTF=PASS`, `QuickBuyStrategy=PASS`, and
  `MultiMA_TSL5=NA`; the other seven have no record. Its last artifact write
  was `06:18:26+02:00`; no freqtrade error was recorded after the last normal
  analyzer log. A single-strategy `Schism5` look-ahead writer is now active.
- `STRATEGY_STATUS.csv` is current with 1,050 rows: 641 `E1_expanded`, 297
  excluded, 53 exclusion-unconfirmed, 30 too-few-trades, 10 pending and 19
  not-a-strategy. C10 moves 34 formerly E1 rows to excluded: 21 `failed`, 12
  `resource_inconclusive`, and 1 `timeout` in the canonical pooled runner.
  583 current source/profile identities have a successful
  canonical pooled Full-Backtest and therefore `technical_chain_complete=true`;
  none is in `open_work`. All 263 final `excluded` rows now also have empty
  `open_work`; the remaining queue contains 53 `exclusion_unconfirmed` and 10
  `pending` rows only.
- No Docker benchmark/analyzer or Stage-9 writer is active. The completed
  Model-0 attribution atomically wrote its current artifacts: 641 eligible E1
  profiles, 582 accepted/attributed canonical archives, and 3,436,335 trades.
  All BTC-state matches are present; 10,918 of 3,436,335 trades lack pair-local
  state evidence. Fifty-nine eligible profiles lack an accepted archive (52
  `oom_confirmed`, 5 `performance_limited`, 1 `stake_overflow_confirmed`, and
  1 measured); that row was `NostalgiaForInfinityX`, now rerun with its current
  overlay and pending a later attribution refresh. These are coverage facts,
  not profitability results.
- The owner rejected a temporary attribution-only identity-continuity proposal
  and instead ordered the successful current-overlay full rerun above. The
  stopped attribution process never atomically wrote output; visible Stage-9
  artifacts remain the earlier 582-archive run pending a later clean rerun.
- GRID measured 8 trades at one month then timed out at three months; ONS
  measured 8 at one and three months then timed out at one year. Both exhausted
  the 1,800-second recovery budget and need no repeat.
- `evidence/SMOKE_FUNNEL_REVIEW_2026-09-10.md` records all five work packages.
  `strategy_status.html` was regenerated from the current CSV.
- `strategy_status.html` and `tools/STRATEGY_STATUS.template.html` have
  concurrent, uncommitted ready-to-run display edits. Preserve them; they are
  outside the full-backtest closure commit but the regenerated HTML already
  carries the current CSV data.
- The old Spot diagnostic window occurs in 218 `PROFILE_BIAS` rows (174
  look-ahead and 161 recursive diagnostics) and 790 convergence rows. These
  are provenance, not current-window evidence; no measurement rerun started.

## Current implementation checkpoint

Smoke-funnel work packages 1-5 are complete. Ten strategies recovered at least
ten trades: `FastSupertrend`, `FastSupertrendOpt`, `MultiMA_TSL3b`,
`MultiMA_TSL5`, `SMAOPv1_TTF`, `WTHO`, `Schism5`, `QuickBuyStrategy`,
`multi_tf`, and `Solipsis_v4`. They are measurable, not automatically admitted;
their remaining gates still apply. `BestSingleAssetPortfolio` runs but remains
too sparse at 8 trades through one year. Seventeen formerly open rows moved to
confirmed C4/C5 exclusions because no E1-safe repair remains. The status reader
now keeps a current measured smoke record ahead of an older failed repair store.

`Hacklemore3` completed a targeted forced Docker smoke rerun under the frozen
cascade: 11 long trades in the first rung `20200301-20200401`, 857.1 seconds,
with canonical/config/archive/trade hashes recorded in `PROFILE_SMOKE.json`.
Status and HTML were regenerated; it remains admitted and now carries
`trade_evidence=smoke` rather than the older Class-1 result-card fallback.

`evidence/SMOKE_FUNNEL_REVIEW_2026-09-10.md` records the complete disposition.
Of the 74 smoke-stage exclusions, 65 remain terminal on current evidence and 9
C8 string/NaN dtype rows match an existing file-local repair exactly and should
be reopened as bounded repair candidates. Of 32 open rows, 4 have known narrow
repairs, 6 require final resource adjudication, 8 bounded data/dependency/
harness checks, and 14 exact author-provenance checks before likely C4 closure.

Smoke cascade commit `8e435f5` freezes Stage 1 at one month, then three months,
then one year while the completed run remains below ten trades. It stops on the
first rung reaching ten, retains every attempt and unique archive identity, and
does not widen runtime failures. Legacy low-trade smoke records are stale under
this policy; existing results at or above ten trades remain current. The status
Markdown and HTML template describe the cascade and the corrected three-month
Futures bias window. No measurement store changed in that commit.

Base implementation was `0de5829`; the four-model redesign is committed as
`b40ad60` (`Separate coin-only and combined regime gates`).

Eligibility governance correction is committed as `717d1e3` (`Retire invalid
Stage 6 E0 cohort`). `evidence/REGIME_ELIGIBILITY.csv` and the 67-label expansion
inventory remain immutable evidence of the mistaken classification, not usable
membership. Only the latest active `admitted_E1` decision per strategy defines
the cohort; `STRATEGY_STATUS.csv` exposes it as `E1_expanded`.

Strategy classification repair is committed as `a7259ad` (`Complete generated
strategy type classification`). `tools/strategy_classification.py` now reads
the canonical population from `evidence/EXECUTION_PROFILES.csv`, never from its own
downstream status output. All 1,050 rows have an explicit generated Type: no
blank and no current `unclassified`; 19 test/template artifacts are
`not_applicable`. `CORPUS.md` prose was not broadcast from repo to strategy.

Repository cleanup phase 1 archives the predecessor `ANALYSIS`, DCA, depth,
resolvability, old signal/log, and selected-case-study families under
`old/predecessor_audit/`. Graphify confirmed no call/import path from the
current status or regime engine to DCA/depth/resolvability. The exploratory
trailing-sensitivity family was deliberately kept active in root because
Graphify showed its current profile/full-backtest dependencies. Root README is
now about the market-regime benchmark and contains the directory tree.

Cleanup phase 2 is committed as `699512d` (`Group runtime configs and Docker
entry points`). `runtime/` now contains all four Dockerfiles, four requirement
sets, spot/futures base configs, and 15 Docker wrappers. Wrappers resolve the
repository root through their parent, use runtime-local Dockerfiles, retain the
root build context and `/audit` mount, and invoke the same Python entry points.
New runs record `runtime/profile_*_config.json`; old invocation strings remain
immutable historical provenance.

Cleanup phase 3 groups 24 current evidence writers and 60 generated/frozen
stores in the flat `evidence/` package. Every active reader, Docker wrapper,
binding document, generated status link, and pipeline declaration uses the new
path. Root retains the user-facing status outputs and binding documents.

Cleanup phase 4 moves the shared override lookup and local-module restoration
tool from root into the existing `repair/` package. All imports, generated
reports, docs and comments now use `repair.overrides` or
`repair/local_modules.py`; `repair/README.md` defines the directory boundary.

Cleanup phase 5 moves `warmup_convergence.py`,
`market_phase_hypothesis.py`, and `merge_full_window_shards.py` beside their
stores in `evidence/`. The warm-up Docker wrapper uses module invocation and
regime attribution imports the phase helper from the package.

Cleanup phases 6-9 complete the classification. Status/exclusion writers moved
to `evidence/`, run coordination moved to `runtime/`, and trailing sensitivity
moved to `regime/`. The complete predecessor publication family — its ledger,
corpus prose, reports, measurement programs, hard-coded setup program, and
retired CI guards — now lives under `old/predecessor_audit/`. Current corpus
intake/shared utilities live under `tools/`; all active readers of the archived
ledger use its new path. The status HTML template lives with its generator.

The predecessor `verify_ledger.py`, `freeze_guard.py`, `sync_repo.py`, and
`totality.py` are deliberately not current CI gates. The first three govern
the retired publication layout; `totality.py` reports 124 heuristic refusals on
the current pipeline and is not a usable unchanged commit gate. CI now parses
all 94 active Python files recursively, excluding vendored repair overlays,
instead of vacuously checking only root-level Python files.

- `regime/regime_engine.py` produces causal, one-day-lagged four-state data.
- `regime/attribution.py` already attributes Model 0 trades to both four states
  and six reporting phases. It now also retains source strategy and model
  identity when reused for gated candidates.
- `regime/gate_adapter.py` is entry-only. It has independent `btc`, `coin`, and
  `btc_coin` modes; coin-only mode neither reads nor validates a BTC column.
  Missing required local evidence fails closed, and omitted state lists fail.
- `regime/gated_backtest.py` implements resumable Model 1, Model 2, and Model 3
  pooled runners from one explicit candidate spec. It does not choose the spec.
- `regime/gated_attribution.py` validates and attributes gated candidate
  archives. Complete input is the default; `--allow-partial` is explicit.
- `regime/model_compare.py` writes a non-ranked Model 0/1/2/3 long table and
  deltas only after identity, candidate, gate, archive, and timerange checks.
  It enforces that Model 3 reuses Model 1's BTC gate and Model 2's coin gate.
  It does not implement the still-open exposure benchmark.
- `PIPELINE.md` and `DOCUMENT_MAP.md` describe these boundaries.

No production Model 1/2/3 run has been started. No candidate gate was selected.
No performance row or ranking was inspected while writing this code.

The exact E0 reconciliation is complete: 67 historical members, of which 66
were independently admitted to E1 under `converged_clean_gates_v1` and one,
`MacdStrategy`, was excluded. Their E1 standing does not derive from E0.

## Validation completed for this checkpoint

```text
python -m regime.gate_adapter                         PASS
python -m regime.gated_backtest --selftest            PASS including resume
python -m regime.gated_attribution --selftest         PASS
python -m regime.model_compare --selftest             PASS
python -m regime.attribution --selftest               PASS
python -m compileall -q regime evidence/profile_smoke.py       PASS
actual regime_daily load                              PASS 2364 BTC days / 18000 pair-days
gated archive-reader integration on A9AV              PASS 13679 trades
coin-only actual-data load has no BTC series           PASS
combined actual-data load has BTC and coin series      PASS
```

E0-retirement validation at `717d1e3`: `strategy_status.py`,
`tools/eligibility_expansion.py`, `evidence/eligibility_expansion_adjudicate.py`,
`evidence/regime_eligibility.py`, `evidence/eligibility_evidence_gap.py`,
`warmup_convergence.py`, and `exclusion_criteria.py` selftests all PASS;
targeted `compileall` and `git diff --check` PASS. The frozen expansion
generator's `--check` is expected to report its pre-amendment CSV/JSON inputs as
stale after the governing documents changed; do not regenerate them to silence
that historical mismatch.

The historical 5-profile ungated equivalence artifact remains 5/5 exact at
`results/regime/gate_equivalence.json`; do not rerun it without a reason.
At 2026-09-10T21:02:00+02:00, `regime.validate_regime` and the gate-adapter
selftest both PASS; the retained equivalence artifact is structurally current
and reports 5/5 exact trade matches. No expensive duplicate equivalence run was
started.

Classification validation at `a7259ad`: classifier selftest/check, phase
hypothesis selftest, status selftest/check, status-page selftest, targeted
`py_compile`, generated JSON/CSV identity check, and `git diff --check` PASS.
Graphify was refreshed with Claude's documented `graphify update .` AST-only
path: 1,552 nodes, 2,527 edges, 151 communities, no LLM/API call.
A local fail-open `.git/hooks/post-commit` now runs that exact command when
Graphify and `graphify-out/graph.json` are present. It does not run semantic
extraction and a Graphify failure cannot invalidate the commit.

Cleanup phase 1 validation: Graphify dependency queries, archived DCA read run,
archived scripts `py_compile`, status check, classification check, archived
case-study index check, and `git diff --check`. The old DCA read reproduces its
895-row historical report; it does not affect the current 1,050-row status.

Cleanup phase 2 validation: Graphify dependency query; all PowerShell wrappers
parse; both config JSON files parse; Docker COPY sources resolve inside the root
context; profile-smoke and status selftests PASS; status and classification
checks current; regenerated runtime/exclusion reports; secret gate and
`git diff --check` PASS. No benchmark was started.

Cleanup phase 3 validation: all 18 available evidence-module selftests PASS;
classification check, phase-hypothesis, warm-up, exclusion, status and status-
page selftests PASS; status regeneration/check PASS at 1,050 rows; targeted
compileall, 38 evidence JSON parses, all Docker-wrapper PowerShell parses,
sync-repo selftest, secret gate and `git diff --check` PASS. No measurement or
benchmark store was regenerated.

Cleanup phase 4 validation: Graphify dependency query; local-module selftest,
override-store import over 43 rows, execution-profile, profile-bias and warm-up
selftests, status regeneration/check, classification check, targeted compileall
and `git diff --check` PASS. No benchmark was started.

Cleanup phase 5 validation: Graphify dependency query; warm-up and phase-
hypothesis selftests, attribution selftest, targeted compileall, wrapper parse,
phase-hypothesis regeneration, status regeneration/check, classification check
and `git diff --check` PASS. No benchmark or warm-up measurement was started.

Final cleanup validation: Graphify dependency traversal; active tool import
check; execution-profile, regime-eligibility, strategy-status and status-page
selftests; status and classification freshness checks; HTML regeneration;
compileall including the archive; active-tree AST parse (94 files); secret-gate
selftest; and `git diff --check` PASS. The status page still contains 1,050
rows. No benchmark or analyzer was started.

Equal-window validation: profile-bias, convergence, strategy-status, and HTML-
page selftests PASS; status freshness, targeted compileall, Graphify AST update,
and `git diff --check` PASS. The generated Markdown/HTML window table now shows
`20200301-20200601` for both modes; no measurement store was modified.

Futures recursion-window change: `profile_bias.WINDOWS['futures']` is now
`20200301-20200601`; Spot remains `20190101-20190401`. The preregistration and
pipeline record the owner's prospective decision and why the old one-month
window was an undocumented smoke-window inheritance. `redo_defective()` now
moves a convergence record whose timerange differs from the current frozen
mode window under `superseded`, and accepts the CLI's explicit strategy filter.
Profile-bias and convergence selftests plus targeted compileall PASS. The
productive rerun has not started because Model 0 is still active.

The 2026-09-10 follow-up supersedes the remaining calendar asymmetry:
`profile_bias.WINDOWS` is now `20200301-20200601` for both Spot and Futures.
`profile_bias` archives a stale per-diagnostic result under `superseded` before
rerunning it, so a current PASS cannot silently overwrite its provenance.
`strategy_status.py`, `PIPELINE.md`, the HTML template, generated status files,
and preregistration use the same window. The separate full-analysis windows
remain unchanged because their pair-history/warm-up constraint is not a BTC-
only bias diagnostic.

## Next concrete steps

1. Treat the five smoke-funnel packages as complete; do not repeat their smoke
   or resource attempts while identities and rules match.
2. For the ten recovered at-least-ten-trade rows, run any required output-
   equivalence proof first, then native Look-Ahead. Run Recursive-Bias and its
   Warm-up route only after Look-Ahead `PASS`. Only rows passing every frozen
   technical gate may receive a new E1 adjudication.
3. If the owner explicitly continues the measurement queue, derive targets
   only from `pending` and `exclusion_unconfirmed` current identities. Exclude
   every final `excluded`, C10, and `technical_chain_complete=true` row; do not
   use the old 218/790 inventory as a queue because it includes closed cases.
4. Complete remaining Model 0 rows resumably and adjudicate resource-
   inconclusive failures under the existing attempt rules.
5. Resolve the eight OPEN preregistration choices before producing a discovery
   candidate spec or any ranked output. At minimum the owner must decide the
   discovery/validation split, minimum trade/episode evidence, and the
   exposure-matched benchmark construction.
6. Once those choices are frozen, write and hash one explicit candidate spec,
   run the 5-10 strategy pilot, then Model 1, Model 2, Model 3, gated
   attribution, and the non-ranked comparison in the order in `PIPELINE.md`.

## Do not redo

- Smoke-funnel work packages 1-5 recorded in
  `evidence/SMOKE_FUNNEL_REVIEW_2026-09-10.md`, including GRID/ONS 1,800-second
  cascades and the bounded BlueEyes repair chain.

- Corpus intake and the completed eligibility expansion waves.
- Warm-up ladders, native bias diagnostics, or admission decisions already
  represented in current stores.
- The 30 current `too_few_trades` rows: their 6.5-year look-ahead fallback is
  stronger than every rung of the new smoke cascade, so a shorter rerun cannot
  rescue them. Revisit only if the strategy/runtime identity or frozen rule
  changes.
- Identity-matching canonical pooled Full-Backtest rows with `status=measured`:
  they have already completed the technical chain. A later diagnostic-window
  change must not requeue them; preserve their earlier diagnostic records as
  provenance. `NostalgiaForInfinityX` completed its current-overlay rerun and
  is no longer an identity exception.
- Final `excluded` cohort rows: they are closed work cases. Preserve their
  exclusion evidence and reason, but never recreate `open_work` for them.
  `exclusion_unconfirmed` remains a separate unresolved cohort and is not
  covered by this closure rule.
- C10 `full_backtest_not_testable`: the recorded Stage-7 `failed`,
  `resource_inconclusive`, or `timeout` outcome is final by the owner's
  2026-09-10 decision. Do not retry or admit these rows without a new owner
  decision that supersedes the amendment.
- The 5-profile ungated adapter equivalence suite.
- Regime feature generation unless its hashed candle inputs or frozen formula
  change.
- Any measured Model 0 identity-matching archive. The runner is resumable.
- The `Hacklemore3` smoke rerun completed on 2026-09-10; do not repeat it while
  its canonical/config identities match.
- Any live Claude runner or its output store.
- Strategy Type classification and the `a7259ad` artifact regeneration; do not
  hand-edit `STRATEGY_STATUS.csv` or infer per-strategy Type from repo prose.
- Routine Graphify refreshes use `graphify update .` only. Do not substitute
  `graphify extract .`: that performs semantic Markdown extraction and consumes
  API quota. The local post-commit hook already handles AST-only updates.
- Do not move evidence stores back to root or invoke their writers by file
  path. Run them from the repository root as `python -m evidence.<module>`.
- Do not restore predecessor publication programs or retired guards to root.
  Current corpus utilities are under `tools/`; the historical family is under
  `old/predecessor_audit/`. Root is intentionally limited to 22 user-facing or
  repository-level files and contains no Python program.
- Any historical E0 benchmark or attribution as current evidence. Do not rerun
  the old 67, add 67 to E1, or regenerate frozen E0 CSV/JSON artifacts.
- Do not generate a candidate spec from observed strategy performance.
- Do not rank while any required preregistration choice is OPEN.

## Constants - do not rederive

- Spot analysis window: `20200401-20260821`.
- Futures analysis window: `20200301-20260821`.
- Bias/convergence diagnostic window for both Spot and Futures:
  `20200301-20200601`.
- Smoke diagnostic cascade: `20200301-20200401`, `20200301-20200601`, then
  `20200301-20210301`, stopping at the first measured rung with at least 10
  trades.
- Eight-pair pooled canonical universe; pairwise shards are supporting trade
  evidence and do not replace pooled shared-capital mechanics.
- Primary state model: Wilder DMI/ADX(14), causal one-day lag, four states.
- Six reporting phases and fixed volatility thresholds are frozen in the
  2026-09-05 preregistration amendment; they do not replace the four states.
- Model 0 is original entries/exits. Model 1 gates entries on BTC state.
  Model 2 gates entries only on pair-local coin state and does not use BTC.
  Model 3 requires both the Model 1 BTC gate and Model 2 coin gate. Original
  exits remain authoritative.
- Missing local gate evidence fails closed in Models 2 and 3. Model 1 needs
  only the global BTC evidence.
- WSL ceiling remains 14 GB memory plus 4 GB swap. Do not raise it.
- In-container exit `-9` is `resource_inconclusive`, not strategy failure.
  Docker wrapper exit 125 or an unresponsive VM is not a completed attempt.
- Results are identity-bound, atomic, and resumable. Every new runner records
  its invocation and non-command environment/config provenance.
- `technical_chain_complete=true` requires a `measured`, canonical pooled
  Full-Backtest whose source hash and run profile still match the current
  execution profile. It clears `open_work` only, not cohort/adjudication.
- A final `excluded` cohort also clears `open_work`; it does not erase its
  exclusion reason/evidence. `exclusion_unconfirmed` must retain its queue.
- C10 contains exactly the owner-declared canonical Full-Backtest statuses
  `failed`, `resource_inconclusive`, and `timeout`; status or cohort is never
  hand-edited in `STRATEGY_STATUS.csv`.
- E0 is invalid historical provenance only. The current usable population is
  the latest active E1 adjudication set after C10; currently 641 rows, including 66
  independently re-admitted former E0 members.
- The prior long Wave A-C handoff remains recoverable in Git before commit
  `548be09`; current artifacts and this file supersede its stale counts.
