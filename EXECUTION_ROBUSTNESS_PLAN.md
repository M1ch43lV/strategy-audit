# Execution Robustness Addendum

## Scope and status

This is a prospective, additive post-Full-Backtest verification stage. It does
not replace any Smoke, Look-Ahead, Warm-up/Recursive, admission, or canonical
pooled Full-Backtest result. Existing historical results remain provenance and
are never reclassified by this addendum.

The stage is applied to every identity-current strategy with a measured
canonical pooled Full-Backtest and a declared main timeframe greater than 5m.
Selection is independent of performance, rank, or profitability.

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
