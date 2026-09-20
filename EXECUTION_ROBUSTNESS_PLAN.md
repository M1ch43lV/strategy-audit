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

`regime/specialist_evaluation.py` does not consult any of this yet, although
rankings already exist: the Model 0 evaluation of 584 strategies and the Model
1/2/3 evaluations of the candidate sets, published as the *Regime-Spezialisten*
artifact on 2026-09-15. They predate this stage and carried no annotation. Since
2026-09-20 the published page joins the annotation as a *Robustheit* column
(`tools/regime_specialists_page.py`); the ranking CSVs still carry none. The
designation is "clears the specialist floor" AND the per-state qualification, a
column that changes no ranking. (An earlier version of this section
said that no ranked output existed; that was wrong.)

### Generated stores

`evidence/EXECUTION_ROBUSTNESS.json` and `evidence/COST_SCREEN.json` are written
only by `python -m evidence.execution_robustness` and never edited by hand. Each
record carries the numbers it was decided on, so the files stay readable without
`user_data/`; a rebuild without an archive keeps that strategy's existing record.
Rebuild after every detail batch, then regenerate the status table.

## Amendment 2026-09-20: how large the detail effect is, what causes it, and what to run

Two questions, both answered from runs that exist: how much do the results of a strategy at 5m change when
it is rerun with 1m detail candles (section 1), and why do the Stage 8b reruns of strategies above 5m deviate
from their author-timeframe runs (section 3). The recommendation for future work is in section 2. Nothing
here changes `THRESHOLDS`, the classifier or a status; it is evidence for a decision that stays with the
owner.

### 1. Test: strategies at 5m, rerun with 1m detail

The rule of 2026-09-19 counts a strategy at or below 5m as having passed the detail check, because its own
candle is already as fine as the detail candle. That is a rule and not a measurement. To see what it leaves
out, ten strategies were rerun with `--timeframe-detail 1m`.

**Selection**, computed by `bot/detail_1m_batch.py`, not picked by hand: own timeframe 5m; ranked by the
validation-window dollar gain of `strategy_total_dollar_gain.csv`; the source declares a trailing stop, a
custom stoploss or a dynamic ROI (a table of two or more steps, or `custom_roi`); strategies with the same
trades and gain count once; the first ten. `ClucFiatSlow` is thereby not tested separately from
`ClucFiatROI`.

**Method.** Each strategy ran through the pipeline's own runner (`profile_smoke.run_one`, so the same config,
runtime rules and repairs as its canonical run) over the validation window, 2024-01-01 to 2026-08-20, with
1m detail. Each was compared with (a) its canonical archive and (b) a control: the same runner and window at
5m without detail candles. The control matters because a window that starts in 2024 does not start in the
state of a run that began in 2020. Trades are compared by the mean profit ratio per trade, the sum of the
ratios, and matched by pair and opening candle.

| strategy | canonical n / mean % | control n / mean % | 1m detail n / mean % | 1m vs control |
|---|---|---|---|---|
| EI3v2_tag_cofi_green | 757 / 0.889 | 757 / 0.889 | 763 / 0.755 | -15.1 % |
| BuyOrDie | 843 / 0.734 | 884 / 0.688 | 884 / 0.688 | 0.0 % |
| E0V1E_DCA3 | 407 / 1.131 | 407 / 1.130 | 427 / 0.792 | -30.0 % |
| ClucFiatROI | 1377 / 0.262 | 1392 / 0.258 | 1400 / 0.289 | +12.1 % |
| SMAOffset_Hippocritical_dca_leverage | 138 / 2.556 | 138 / 2.556 | 213 / 2.481 | -2.9 % |
| UniversalMACD | 466 / 0.675 | 466 / 0.675 | 466 / 0.713 | +5.6 % |
| CombinedBinHAndClucV3 | 473 / 0.658 | 473 / 0.658 | 483 / 0.780 | +18.5 % |
| SMAOffset | 443 / 0.660 | 443 / 0.660 | 443 / 0.660 | 0.0 % |
| NFI5MOHO_WIP | 230 / 1.204 | 230 / 1.204 | 241 / 0.951 | -21.0 % |
| ZaratustraDCA5 | not comparable, see below | 7322 / 0.123 | timeout at 3600 s | - |

**Result over the nine that finished.** The detail candles alone change the mean profit per trade by -3.6 %
on average (median 0 %; worse in four, better in five). Pooled over all trades the mean falls from 0.703 % to
0.693 % (-1.4 %), and the sum of the ratios changes by +1.0 %. Against the canonical runs it is -4.6 % on
average and -2.9 % pooled. The spread is large: -30 % to +19 %. The largest loss, -30 % (E0V1E_DCA3), is below
the 50 % that makes a strategy `SENSITIVE` in the classifier. No strategy's mean profit per trade changed its sign.

A runtime difference does not appear in these ten: for seven the control has the same trade count and the same mean as
the canonical run (the canonical archives are Docker or native runs, the control is native). Two controls differ from the
canonical run because of the window start, not the runtime: BuyOrDie, which holds positions for months
(843 canonical against 884 in every 2024 run), and ClucFiatROI (1377 against 1392). Without the control the
1m effect of BuyOrDie would have read -6.2 % instead of 0 %.

**ZaratustraDCA5 (not comparable, and not measurable at 1m within the ceiling).** The 1m run reached the
ceiling of 3600 s and is recorded as a timeout; the ceiling is not raised. Its 5m control also does not
match the canonical run in trade count (7322 against 4161), and the reason is the account, not the candles:
the canonical run with `stake_amount: "unlimited"` lost 96.7 % of its account over the whole window and
ended at $33.7, so its later stakes were small (mean $9 in the validation window), which probably limited the
number of entries (the minimum stake was not checked); the control started with a fresh $1000 (mean stake $67) and placed 76 % more. The profit ratio per
trade is independent of the stake (0.166 % against 0.123 %), the set of trades is not. The strategy is a DCA
strategy on futures with long and short trades. The fixed-$1000-per-trade convention of the evaluation shows
+$6,898 for it in the validation window while the account of its own run collapsed; that is a property of the
convention and of DCA, worth a caveat wherever its dollar figure is quoted. A strategy of this kind cannot be
compared across windows that start in different account states and cannot be run at 1m inside the ceiling.

### 2. Causes and recommendation

**Where the change comes from** (`bot/detail_1m_causes.py`, the nine strategies, control against 1m,
5155 trades that both runs opened):

- Almost all of it is on trades both runs opened, at the exit. Only 35 trades exist only in the control and 56
  only at 1m; their sums are +0.74 and +0.92 against -1.97 from the common trades.
- Trailing stops are the main cause. For EI3v2 361 trades keep the exit reason `trailing_stop_loss` and lose
  0.93 of a total change of -1.07 in the ratio sum; for E0V1E_DCA3 242 trades explain -1.06 of -1.08. The sign
  is not fixed: for CombinedBinHAndClucV3 28 trailing trades gain +0.61. The coarse candle does not know the
  order of the high and the low inside it, which is the likely reason; what was measured is the effect, not the
  mechanism inside freqtrade.
- Exits that depend on the profit do the same: NFI5MOHO_WIP (`signal_profit_*`) changes on 31 % of its trades,
  -0.29 % per trade.
- A dynamic ROI moves little: UniversalMACD +0.18 over 119 ROI trades.
- A fixed stoploss and a fixed target change nothing: BuyOrDie and SMAOffset show 0 % on every trade. BuyOrDie
  has a trailing stop, but it only starts at +36 % and never triggers in practice.
- A change of the entry set is small, larger for the two DCA strategies (E0V1E_DCA3, SMAOffset_Hippocritical_
  dca_leverage), where a different exit moves the next fill.

**Recommendation for strategies that are tested in the future.**

1. Screen at the granularity that is already run: the 5m detail rerun for strategies above 5m, the own
   timeframe for strategies at or below 5m. Do not apply a flat discount: the single strategies moved between
   -30 % and +19 %, so a discount would correct a third of them in the wrong direction. If a number is needed
   for planning, the pooled effect of 1m over 5m is about -1 % to -3 % of the mean profit per trade.
2. Run 1m detail for a strategy that reaches a shortlist or a specialist designation and whose source declares
   a trailing stop, an exit that depends on the profit (`exit_profit_only`, `custom_exit`/`custom_sell`), or
   position adjustment. A strategy with only a fixed stoploss and a fixed or table ROI does not need it. The
   1m runs took 1 to 2 minutes for most strategies (ClucFiatROI 7, BuyOrDie 19), so a shortlist of a few dozen is
   a matter of hours.
3. Compare a 1m run with a 5m control in the same window and runtime, never with a run that started at another
   date, for strategies that hold positions for months or compound their account.
4. Do not rank strategies with a trailing stop or a profit-dependent exit by differences smaller than about
   30 % of their mean profit per trade; the 5m figure does not resolve them.
5. A strategy that does not finish at 1m within the ceiling is recorded as `1m not measurable`, its 5m figure
   stays with that flag, and the ceiling is not raised.
6. Consider extending the rule of 2026-09-19 to require a 1m rerun for a strategy at or below 5m when its
   source declares one of the mechanisms of point 2. This is a proposal; the current rule stands until decided.

### 3. Test: the existing 5m detail reruns of strategies above 5m

`bot/detail_5m_deviation.py` compares, for every strategy with a measured 5m detail run, the detail archive
with the canonical archive over the validation window and matches trades by pair and opening candle. 195
strategies have both runs and trades in the validation window: 157 `PASS` and 38 `SENSITIVE`. The report is
`results/regime/rotation_bot/detail_5m_deviation.json`.

- **The bulk does not move.** Median change of the mean profit per trade: 0.000 pp over all 195 and over the 157
  `PASS`. For the 157
  `PASS`, the strategies with a mean of at least 0.3 % per trade (83 of them) have a median absolute change of
  1.5 % and 11 % of them change by more than 20 %. For the 38 `SENSITIVE` (16 with such a mean) the median is
  70 % and 88 % exceed 20 %.
- **What separates them is the declared mechanism.** Strategies whose source declares none of trailing stop,
  custom stoploss and profit-dependent exit (99): median absolute change 0.2 %, 6 % above 20 %. Strategies with a
  trailing stop (61, of these 26 with a mean of 0.3 % or more): median 18.3 %, 46 % above 20 %. Among the 38
  `SENSITIVE`, 23 declare a trailing stop, 24 a dynamic ROI, 10 a profit-dependent exit, 8 a custom stoploss, 3
  position adjustment; one declares none of these.
- **The dominant cause on the common trades of the `SENSITIVE`:** 18 of 38 trailing stop with an unchanged exit
  reason (a different fill price), 7 a changed entry set, 5 ROI with an unchanged reason (timing and price), 2
  stoploss to ROI, and single cases. The same pattern as at 1m: the trailing fill decides, the ROI table and
  the entry set follow.
- **The author timeframe matters.** Median absolute change of the mean per trade, strategies with a mean of at
  least 0.3 %: 15m 4.7 %, 1h 8.3 %, 4h 0.0 % (5 % above 20 %), 1d 16.3 % (47 % above 20 %). The coarse daily
  candle leaves the most room; the 4h group has a median of 0 % but 5 % of it above 20 %. The likely reason is the candle size, which was not tested separately.
- **Percentages of a small base mislead.** The largest relative changes (Chispei, mabStra, Inverse) are on means
  near zero. The comparison above therefore uses percentage points and only counts strategies with a mean of at
  least 0.3 % per trade when it quotes a relative change.

**The runtime confound.** Of the 195, 157 baselines were made in another runtime than their detail run
(`same_runtime` false), among them 33 of the 38 `SENSITIVE`. The `PASS` strategies show that the runtime alone
moves little: same runtime (31) and different runtime (126) both have a median change of 0.000 pp, and the share
above 20 % is 13 % against 10 %. That does not prove it for the 33 `SENSITIVE`. The five `SENSITIVE` with the
same runtime (AdaptiveRegime, MomentumCCITrendStrategy, PatternRecognition, PolymarketMomentumStrategy,
TrendBreakout, all on 4h or 1d) show the same causes: three trailing fill, one a changed entry set, one a
stoploss that became a trailing exit. The other 33 are "sensitive, cause likely the detail candles, runtime not
excluded". A control run of each in the runtime of its detail run without detail candles would settle it; that
is open. Until then a `SENSITIVE` of the 33 stays as classified and carries `control_run_needed` in its record.

### 4. Reproduction

`python -m bot.detail_1m_batch` (the ten runs), `python -m bot.detail_1m_batch --control` (the 5m controls),
`python -m bot.detail_1m_report` (the table), `python -m bot.detail_1m_causes` (section 2),
`python -m bot.detail_5m_deviation` (section 3). Results under `results/regime/rotation_bot/`. The runs used
`profile_smoke.run_one` with `artifact_key` `val_1m` and `val_5m`, so their archives sit beside the canonical
ones in `user_data/profile_smoke/` and replace none of them.
