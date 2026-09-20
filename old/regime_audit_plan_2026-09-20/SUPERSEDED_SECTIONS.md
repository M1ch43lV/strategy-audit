# Sections of REGIME_AUDIT_PLAN.md that served a cold start and are superseded

Moved verbatim on 2026-09-20 (Decision 0.24-01). Historical only: the questions were decided, the tasks were done, the state is elsewhere.

# 25. Implementation order for Codex

Do not begin with the full corpus backtest.

## Stage 1 — repository understanding

1. Inspect repository architecture.
2. Reproduce the current published audit locally if feasible.
3. Identify reusable loaders, Freqtrade invocation code, result parsers, bias fields, and duplicate-family logic.
4. Document any discrepancy between this plan and the current repository.

## Stage 2 — preregistration draft

5. Create `REGIME_PREREGISTRATION.md` from the frozen sections of this plan.
6. Leave explicitly unresolved decisions marked `OPEN` rather than silently deciding them.
7. Do not execute performance ranking until open primary decisions are resolved.

## Stage 3 — feature engine

8. Implement daily DMI/ADX for BTC and coins.
9. Implement one-day availability lag.
10. Implement SER(30).
11. Implement 30d/90d returns.
12. Implement 30d realized volatility.
13. Implement relative strength vs BTC.
14. Implement DMI spread and optional breadth descriptors.
15. Write causal unit tests.

## Stage 4 — validate regime data

16. Generate regime data for BTC and the eight requested pairs.
17. Produce summary statistics:
    - time in each regime,
    - number and duration of episodes,
    - transition counts,
    - feature distributions.
18. Visually inspect a small number of timelines only as a sanity check, not as a reason to tune thresholds.

## Stage 5 — strategy taxonomy

19. Build the canonical strategy manifest without double-counting repaired overlays.
20. Classify execution profiles (`spot`, `futures`, `long`, `short`, `both`) and store author intent, static capability, observed trades, evidence, and uncertainty separately.
21. Validate ambiguous profiles with mode-correct load and smoke runs.
22. Create deterministic source-code archetype taxonomy.
23. Store evidence and confidence.
24. Never exclude based on either taxonomy.

## Stage 6 — regime eligibility

25. **Historical implementation, retired as admission authority:**
    `evidence/REGIME_ELIGIBILITY.csv` recorded the 67-row Stage 6 snapshot before the
    uniform current-runtime check chain was complete. Preserve it as provenance
    only; never use its `regime_eligible` flag to admit or analyze a row.
26. **Current implementation:** active `admitted_E1` rows in
    `evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv`, exposed as
    `cohort=E1_expanded` in `STRATEGY_STATUS.csv`, define the benchmark
    population. Former E0 members require the same row-level decision.
27. **Implemented:** do not use whole-window profitability/significance as eligibility gates.
28. **Coverage implemented:** `evidence/REGIME_COVERAGE.csv` records exact frozen-window pair/candle checks; before Stage 7, complete the remaining native-profile coverage and canonical bias diagnostics, then regenerate eligibility without changing its rules.

## Stage 7 — Phase A attribution

25. Annotate every trade with the causal regime features available at entry.
26. Produce BTC-only and BTC×coin performance summaries.
27. Produce episode-level consistency statistics.
28. Do not yet claim that regime gating improves portfolio performance.

**Implementation status:** the historical 67-profile attribution completed,
but that population was later invalidated and cannot support current claims.
Expanded Model 0 artifacts are identity-bound and resumable; only current E1
members with accepted archives may enter the new attribution. BTC-only,
BTC x coin, and episode summaries remain separate, and Phase A is descriptive.

## Stage 8 — regime-gate adapter

29. Implement entry-only gating outside original strategy files.
30. Confirm ungated wrapper exactly reproduces original results.
31. Test on 5–10 diverse strategies before scaling.

## Stage 9 — discovery sweep

32. Run Model 0 / Model 1 / Model 2 / Model 3 on the discovery period.
33. Compute full, regime-gated, and cash benchmarks.
34. Include exposure metrics.
35. Rank specialists and universal candidates using preregistered criteria.

## Stage 10 — lock selection

36. Write and hash `selection_manifest.json`.
37. Record code version, data fingerprints, Freqtrade version, and parameter definitions.

## Stage 11 — validation

38. Run the locked candidates on validation data.
39. Do not substitute failed candidates.
40. Report effect sizes, drawdowns, consistency, and benchmark excess returns.

## Stage 12 — robustness and exploratory analysis

### Execution robustness prerequisite

Regime attribution uses canonical pooled Full-Backtest trades unchanged. A
separate, prospective execution-robustness verification is applied afterwards
to measured strategies with main timeframes above 5m. It uses Freqtrade
`--timeframe-detail 5m`, retains authored signal timeframes, and records only
an additive sensitivity classification. The complete frozen specification is
`EXECUTION_ROBUSTNESS_PLAN.md`; it is intentionally not duplicated here.

41. Signed ER analysis.
42. Return / volatility analysis.
43. ADX sensitivity.
44. Behavioral clustering.
45. EMA or HMM only if still justified.

# 29. Discussion questions for other AI reviewers

Other AI sessions should review and challenge at least these points before the primary run:

### A. Regime eligibility

What exact combination of existing look-ahead, recursive, trap, and coverage fields should define `regime_eligible` across the broad 456-trading-strategy pool?

### B. Discovery / validation split

Is `2020-03-01 ... 2023-12-31` vs `2024-01-01 ... 2026-08-20` statistically adequate, or would an episode-aware split be better?

### C. Minimum evidence for specialist status

What minimum number of trades and independent episodes should be required?

### D. Exposure-matched benchmark

What benchmark most fairly separates genuine timing/selection alpha from simply holding cash?

### E. Efficiency Ratio

Should SER remain continuous or receive preregistered categories? If categorical, what non-data-mined threshold rule is defensible?

### F. Return classifier

Are ±20% over 90 days acceptable fixed crypto thresholds, or should the return classifier use a different preregistered definition?

### G. Volatility

Should volatility remain descriptive in version 1, or should high-vol/crash become a formal second regime dimension?

### H. Coin universe / breadth

Should breadth use only the eight audit pairs or a broader survivorship-aware crypto universe?

### I. Exit on regime change

Primary proposal is entry-only gating. Should forced exit be included as a later sensitivity test?

### J. Portfolio-level selection

After individual strategy/regime results exist, how should capital be allocated if multiple coins and strategies qualify simultaneously?

No reviewer should resolve these questions by inspecting which answer produces the best historical performance.

# 32. Immediate Codex task

A new Codex session should **not immediately run the full corpus**.

Its first deliverable should be a short repository-specific implementation proposal that answers:

1. Which existing files/functions can be reused?
2. How can daily regime data be injected without changing strategy source files?
3. Which existing ledger fields can define technical `regime_eligible` status for the broad corpus?
4. How will entry-only regime gating be implemented while preserving original exits?
5. How will ungated equivalence be tested?
6. Which open decisions in section 29 must be resolved before any strategy ranking is generated?

Only after this design review should implementation proceed.

# 33. One-paragraph handoff summary

The existing `Apex-prim/strategy-audit` tested 895 public Freqtrade strategy classes and found that whole-window economic conclusions are heavily affected by the market window; its own exploratory calendar-year split showed that strategies can appear weak against buy-and-hold in rising years and defensive in falling years, while low exposure complicates interpretation. The new project therefore asks a different question: whether strategy suitability is conditional on observable market regimes. Version 1 should use a transparent, causal DMI(14)/ADX(14) daily classifier applied separately to BTC and each coin, creating a global BTC regime plus local coin state. All technically trustworthy strategies should be evaluated across all states rather than pre-filtered by presumed archetype. Source-code taxonomy (mean reversion, momentum, breakout, hybrid, etc.) should be recorded before outcomes but used only for interpretation; behavioral clustering comes later. Signed Kaufman Efficiency Ratio and 90-day return plus 30-day realized volatility are explicitly included as independent robustness models. First attribute existing trades to regimes, then perform true entry-gated Freqtrade backtests, compare original vs BTC-only vs coin-only vs BTC+coin gating, use buy-and-hold, regime-gated buy-and-hold, cash, and ideally exposure-aware benchmarks, split discovery from locked validation, and report specialists as well as universal strategies without silently tuning regime rules after seeing results.
