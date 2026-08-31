# Wave C - pre-measurement resolution

The plan requires artifact-role review and resolution of any unknown execution
profile before Wave C measurement starts. Both are now done. The missingness
inventory in `ELIGIBILITY_EXPANSION_MISSINGNESS.csv` covers all 230 rows.

## The headline number

`runtime_smoke_status` is `not_run` for **213 of 230** rows and `failed` for
only 17. Wave C is overwhelmingly a queue of strategies nobody ever attempted,
not a pile of broken ones. That is the reason to expect a materially better
yield here than Wave B's 13 of 82.

## Twelve rows are not trading strategies

Each was checked against its file, not just its recorded label.

**Nine test fixtures** belonging to freqtrade's own test suite:

| Strategy | File |
|---|---|
| `TestStrategyNoImplements` | `tests/strategy/strats/broken_strats/broken_futures_strategies.py` |
| `TestStrategyLegacyV1` | `tests/strategy/strats/` |
| `InformativeDecoratorTest` | `tests/strategy/strats/informative_decorator_strategy.py` |
| `freqai_test_strat` | `tests/strategy/strats/` |
| `freqai_test_classifier` | `tests/strategy/strats/` |
| `freqai_test_multimodel_strat` | `tests/strategy/strats/` |
| `freqai_test_multimodel_classifier_strategy` | `tests/strategy/strats/` |
| `freqai_rl_test_strat` | `tests/strategy/strats/` |
| `Strategy` | `NostalgiaForInfinity/tests/unit/test_data/` |

`TestStrategyNoImplements` sits under `broken_strats/` and is deliberately
incomplete: it exists so freqtrade can assert that loading it fails. Measuring
it would produce a number about a test fixture, not about a trading method.

**Three templates** with no signal logic of their own:

- `ThreeCommasStrategy` defines only `confirm_trade_entry`, a callback hook. It
  has no `populate_entry_trend` or `populate_buy_trend` at all.
- `YourStrat` (in `TrailingBuyStrat.py`) is the placeholder a user is meant to
  replace: the file states the companion class "is designed to heritate from
  yours". The entry logic lives in the subclass, not here.
- `StrategyAnalysis` is an analysis scaffold, not a traded method.

These twelve receive a terminal state of *not a trading strategy*. They are not
measured, and they are not counted as failures.

## The unknown execution profile

Exactly one row carried `run_profile = unknown`: `TestStrategyNoImplements`.
It has no profile because it implements no interface. Resolved by the same
finding; no separate decision is needed.

## Resulting scope

Wave C's measurable pool is **218** rows, not 230. Of those, 30 are FreqAI
machine-learning strategies whose dependency and runtime class will need
attention before they can be measured, and 33 have no recorded execution
timeframe.

Successful loading or a passing smoke run is not eligibility. Every measured
row still has to clear both bias gates afterwards, exactly as Wave A showed:
there, completing the diagnostics excluded two strategies on evidence and
admitted one.
