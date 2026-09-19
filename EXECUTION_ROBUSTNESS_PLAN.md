# Execution Robustness Addendum

## Scope and status

This is a prospective, additive post-Full-Backtest verification stage. It does
not replace any Smoke, Look-Ahead, Warm-up/Recursive, admission, or canonical
pooled Full-Backtest result. Existing historical results remain provenance and
are never reclassified by this addendum.

The stage is applied to every identity-current strategy with a measured
canonical pooled Full-Backtest and a declared main timeframe greater than 5m.
Selection is independent of performance, rank, or profitability.

*Revised on 2026-09-19: strategies at or below 5m are not rerun, and count as equal
to a strategy that received the 5m run. See "Amendment 2026-09-19" at the end of
this file.*

## Intracandle-detail check

For each eligible strategy, rerun the canonical pooled Full-Backtest with the
same strategy source, execution profile, configuration, eight-pair universe,
timerange, fee, and shared-capital parameters. Add only:

```text
--timeframe-detail 5m
```

The strategy keeps its declared main timeframe. The check must not override it
to 5m or refactor its signal logic. Freqtrade therefore evaluates signals on
the authored timeframe and uses 5m candles only to model intrabar trade
progression, callbacks, exit timing, and released trade slots.

Strategies at 5m or 1m are not eligible for this 5m-detail check. A future
1m-detail extension for 5m strategies requires a separate preregistered
amendment and verified 1m data coverage.

## Results and interpretation

Every run records the baseline manifest reference and identity hashes, exact
command, main/detail timeframe, data coverage, runtime/tool versions, and the
native result summary in `evidence/EXECUTION_ROBUSTNESS.json`.

The status is one of:

- `PASS`: reproducible detail run with no material sensitivity signal.
- `SENSITIVE`: reproducible run meeting one or more predeclared warnings.
- `NA`: not applicable or required detail data unavailable.
- `ERROR`: execution or publication failure; never a strategy verdict.

`SENSITIVE` is a review classification, not an automatic exclusion. It is
triggered when the detail run becomes unprofitable, loses more than 50 percent
of the baseline net profit, or has an exit/duration profile indicating
intra-candle sensitivity. The full native metrics and baseline comparison must
remain visible; no aggregate ranking may conceal the classification.

`STRATEGY_STATUS.csv` and `evidence/PIPELINE_STATE.json` publish
`execution_robustness_status` and `robustness_qualified`. Only `PASS` sets the
latter to true. This does not alter E1 admission. It is an additional final
eligibility condition for calling a result an ADX regime specialist or
universal specialist; `SENSITIVE`, `NA`, `ERROR`, and `PENDING` remain
visible but cannot receive that verified designation.

*Revised on 2026-09-19: `robustness_qualified` additionally requires a cost-screen
`PASS` in the claimed ADX regime state. See "Cost screen per ADX regime state"
and "Qualification for the verified specialist designation" in the amendment
at the end of this file.*

## Follow-up stages

Cost/slippage stress, limit-order fill-risk review, and temporal walk-forward
validation are separate prospective stages. They are not inferred from this
check and must receive their own immutable parameters before execution.

## Resource and execution rules

Runs are serial and use the same memory safeguards as canonical Full-Backtests.
The detail data must be present before a run is admitted. A missing data set is
recorded as `NA`, not repaired by changing the strategy or timerange. Evidence
publication, pipeline-state refresh, metadata recording, commit, and push
occur after every completed batch.

## Amendment 2026-09-19: classifier, strategies at or below 5m, cost screen

Owner decisions of this date, and the definitions the first implementation
(`evidence/execution_robustness.py`) applies. Nothing above is withdrawn; where
this amendment is more specific it governs.

### Scope: strategies at or below 5m are not rerun

Owner decision, on resource grounds, made after a first draft of this amendment
had proposed a 1m-detail batch for them. That batch is not run and not planned.

The stage covers every identity-current strategy with a measured canonical
pooled Full-Backtest. Above 5m the 5m detail run applies. A strategy at or below
5m (404 of the measured baselines: 400 at 5m, 4 at 3m) already simulates at the
granularity the others are rerun at, so it is **counted equal to a strategy that
received the 5m run**: `PASS`, reason `baseline_at_detail_granularity`, and
it satisfies the execution half of `robustness_qualified` exactly as a measured
`PASS` does (the cost half is separate, see below).

This is a rule and not a measurement, and the record says so: `basis` is
`owner_rule_at_or_below_5m` where it is `measured_detail_run` for a rerun, and the
status table publishes it as `execution_robustness_basis`. What the rule does not
show is ordering inside one 5m candle, which only a 1m run would. The 1m data
exists (about 4.4 million candles per pair, complete apart from the exchange's
own gaps) should the decision be reopened.

### What `SENSITIVE` means

The plan's third trigger ("an exit/duration profile indicating intra-candle
sensitivity") had no measurable form. It is replaced. A run is `SENSITIVE` when
any of these holds, comparing the detail run with its baseline:

1. **`profit_sign_flip`** - net profit changes sign. Covers the plan's "becomes
   unprofitable" and its mirror image.
2. **`profit_change_over_50pct`** - net profit changes by more than 50 percent of
   the baseline's magnitude, in either direction. The plan's clause only looked
   at losses; on the first 42 runs `TrendBreakout` went from -52.8 % to +75.6 %
   and `AdaptiveRegime` from -11.7 % to +27.6 %, which is large execution
   sensitivity that a losses-only rule reads as `PASS`. The freqtrade baseline is
   pessimistic where a stoploss and a take-profit both fit inside one candle.
3. **`trade_count_change_over_10pct`** - the trade set changes by more than 10
   percent. The regime attribution is built on the baseline trades; a materially
   different trade set means it no longer describes the more realistic run.

The distance between the two exit-reason mixes is reported but is not a trigger:
on the first 42 runs its median was 0.002 and its maximum 0.063, including runs
that flipped sign, so a threshold on it could never fire.

These thresholds are hashed into every record (`thresholds_sha256`). They were
fixed while 42 of the 230 five-minute-detail runs existed and before the rest
did; that is disclosed here rather than presented as predeclared in the strict
sense. `SENSITIVE` remains a review classification, not an exclusion.

### Validity of a comparison

A record is only produced when all of the following hold, otherwise it is `NA`
or `ERROR` with the reason named:

- the native result echoes `timeframe_detail` equal to the one requested
  (`ERROR: detail_flag_not_applied_in_native_result`) and the baseline does not
  (`ERROR: baseline_is_itself_a_detail_run`);
- `canonical_sha256`, `runtime_config_sha256`, `run_profile`, `timerange` and the
  pair list are identical between baseline and detail run (`NA:
  identity_mismatch:...`);
- detail candles cover at least 99 percent of what the main timeframe's own data
  for the same pair and window implies. freqtrade silently falls back to the
  coarse candle where detail data is missing, so a run over partial data would
  still "measure" (`NA: detail_data_incomplete`).

### Runtime attribution and anomalies

The record states whether baseline and detail ran in the same runtime. A
`SENSITIVE` result across runtimes carries `control_run_needed`: the baseline of
24 of the first 30 strategies came from `native_unversioned`, the detail runs
from Docker, so the difference is not yet attributable to the detail candles.
Strategies without intra-candle logic reproduce exactly across the two runtimes
(`AlligatorStrategy` 590.5 % in both), which bounds the effect without removing
it. No control run is scheduled by this amendment.

The classifier also reports, without changing any status, findings about the
runs themselves. The first is trades that close before they open: 0 in the
baselines, 15 trades across 7 strategies in the detail runs, so an artifact of
`--timeframe-detail` rather than of any strategy.

### Cost screen

Separate from the detail check and needing no new backtest. The canonical
baseline trades are re-priced with additional slippage per side, on the notional
(`stake_amount` times leverage), on top of the 0.1 % fee the run already charges.
The reference stress doubles the modelled friction: 0.1 % extra per side, 0.2 %
per round trip. The grid is 0.05 %, 0.1 % and 0.2 % per side.

- `PASS` - net profit stays positive at the reference stress.
- `SENSITIVE` - baseline profitable, not profitable at the reference stress.
- `NA` - baseline not profitable, or no trades. A cost can only worsen it.

Each record carries the break-even slippage per side in basis points and the
article's caution flag (mean profit per trade below 0.5 %), which is reported
but not decisive: 43 of 102 strategies below that mean still pass the doubling
stress. The calculation is first order. With `stake_amount: unlimited` a lower
balance would shrink later stakes, which it leaves out.

### Cost screen per ADX regime state

Owner decision 2026-09-19, later the same day: a regime specialist that performs
very well in some market phases must not be marked down by the cost picture of the
phases where the strategy does not run well. The whole-run screen above is
therefore descriptive only, and the cost condition is judged per ADX regime state.

- **States.** The primary DMI/ADX model's four states, `BULL`, `BEAR`, `SIDEWAYS`
  and `TRANSITION`, once for BTC (`btc`) and once for the traded coin (`coin`). A
  trade belongs to the state on the day it opened, assigned by
  `regime.attribution.attribute()` itself and not re-derived. Where the project's
  own regime summary was current, 2343 of 2343 cell trade counts match it.
- **Basis.** A fixed stake per trade, the specialist evaluation's own convention,
  so a state late in the window is not inflated by a compounded balance. A trade's
  cost is twice the slippage times its leverage, as a ratio of its margin. This
  differs from the whole-run screen, which prices actual stakes.
- **Trade floor.** 10 trades per state, the specialist evaluation's own floor;
  `selftest()` asserts the two constants stay equal. Below it the state is `NA`.
- **Window.** A specialist claim rests on the validation window from 2024-01-01
  (`regime.specialist_evaluation.VALIDATION_START`, frozen 2026-09-11), so that
  window decides. The whole window is published beside it as context
  (`cost_pass_regimes_all_windows`). The two differ mostly for universal
  specialists: 7 pass in all four coin states on the validation window, 128 on
  the whole window, because many states have fewer than 10 validation trades.
- **Status per state.** `PASS` when the state's mean per-trade profit stays
  positive at the reference stress; `SENSITIVE` when it is positive but does not;
  `NA` when the state is not profitable, has no trades, or is below the floor.

### Qualification for the verified specialist designation

`robustness_qualified` is the condition for the verified specialist designation,
and it has two parts:

- `execution_robustness_status` is `PASS` (measured, or by the rule for strategies
  at or below 5m), **and**
- the cost screen passes **in the state where the specialist claim is made**.

`robustness_qualified` in the status table is the strategy-level form: execution
`PASS` and cost `PASS` in at least one state on the validation window, with those
states listed in `cost_screen_regimes_pass`. It is necessary and not sufficient.
The designation for one claimed state must consult that state
(`qualifies_in(record, kind, state)`), and a universal specialist must pass in all
four (`qualifies_universal(record, kind)`). Because a strategy with any positive
state can reach the strategy-level flag, that flag discriminates weakly by itself;
the per-state list is the information.

Each component stays published (`execution_robustness_status`,
`cost_screen_regimes_pass`), and the whole-run `cost_screen_status` stays as a
description that no longer gates. `evidence/PIPELINE_STATE.json` carries the
conjunction as `robustness_qualification`.

`regime/specialist_evaluation.py` does not consult any of this yet. No ranked
output exists, so nothing is mislabelled today. When one is produced, the
designation is "clears the specialist floor" AND the per-state qualification,
attached as an annotation that changes no ranking.

### Generated stores

`evidence/EXECUTION_ROBUSTNESS.json` and `evidence/COST_SCREEN.json` are written
only by `python -m evidence.execution_robustness` and never edited by hand. Each
record carries the numbers it was decided on, so the files stay readable without
`user_data/`; a rebuild without an archive keeps that strategy's existing record.
Rebuild after every detail batch, then regenerate the status table.
