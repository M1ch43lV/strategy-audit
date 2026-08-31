# How much do conclusions depend on the trailing stop?

**Exploratory (E3). Nothing here changes E0, E1, or any confirmatory result.**

A trailing stop is the one exit mechanism a backtest cannot resolve: freqtrade
does not know the price path inside a candle. This arm re-measures every
affected strategy with trailing disabled, over the identical window, pair
universe and config. No strategy source was edited; trailing is switched off
through the configuration, which `StrategyResolver` applies over the strategy
attribute, so every canonical hash is unchanged.

## Scope

22 of the 67 measured strategies enable a trailing stop - just under a third.

## Answer: the dependence is large

| | Strategies |
|---|---|
| trailing never fired (identical trade lists) | 5 |
| result unchanged | 1 |
| **better without trailing** | **13** |
| worse without trailing | 3 |

For 5 strategies the mechanism is inert and the question does not arise:
`MACD_TRIPLE_MA`, `NostalgiaForInfinityV1`, `SMAIP3`, `cryptotank`,
`cryptotankV5` produce byte-identical trade lists either way.

For the other 17 the effect is large and one-directional. Nine strategies move
by more than 20 percentage points of total profit.

| Strategy | canonical | no trailing | change |
|---|---|---|---|
| `Cluc7werk` | -91.3 % | **+96.0 %** | +187.3 |
| `CombinedBinHAndClucV3` | 222.2 % | 333.2 % | +111.1 |
| `ElliotV5_SMA` | 164.4 % | 253.2 % | +88.8 |
| `MADisplaceV3` | 42.1 % | 125.4 % | +83.3 |
| `ClucHAwerk` | -96.6 % | -31.4 % | +65.2 |
| `BigTrader` | 77.2 % | 139.5 % | +62.3 |
| `bestV2` | 73.7 % | 106.1 % | +32.5 |
| `CombinedBinHAndClucV7` | 60.7 % | 81.8 % | +21.2 |
| `ElliotV2` | 108.0 % | 129.0 % | +21.1 |

`Cluc7werk` reverses sign: a catastrophic loser becomes a strong performer.
Ranked by total profit it moves from 18th to 8th, and `ClucHAwerk` from 21st to
14th. The largest rank shift among the 22 is **10 places**.

`BigTrader` is a warning against reading the table as "better": profit rises
from 77 % to 140 % while its Sharpe ratio falls from 3.39 to 0.93. The risk
profile changes, not just the return.

## Why the effect points one way

This is not noise. Freqtrade's backtester states the reason in
`optimize/backtesting.py`:

> Special case: trailing triggers within same candle as trade opened. Assume
> most pessimistic price movement, which is moving just enough to arm stoploss
> and immediately going down to stop price.

When the path inside a candle is unknown, freqtrade resolves it against the
trader. Trailing-stop results are therefore systematically conservative, which
matches 13 of 16 affected strategies improving once the mechanism is removed.

## What this does and does not establish

It establishes that for roughly a third of the corpus, and severely for the
1-minute Cluc/BinH family, conclusions rest on an estimate rather than a
measurement.

It does **not** establish that the trailing-disabled numbers are the true ones.
Removing a trailing stop produces a different strategy, not a corrected one.
Two causes are entangled here and this arm cannot separate them: freqtrade's
deliberately pessimistic assumption, and trailing parameters that are genuinely
poor. `TGMA` showed the second is real - it arms its stop at 1.3 % profit and
then trails 3.5 % behind, placing the stop below entry.

Separating the two requires re-running with `--timeframe-detail`, which
simulates the intra-candle path from finer candles. That is the honest next
step if trailing-stop accuracy needs to be settled rather than bounded.

## Consequence for regime classification

A trailing stop locks in gains during sustained moves, so its effect is
strongest in trending phases and weakest in flat ones. The distortion is
therefore not uniform across market regimes; it acts along the very axis this
audit measures. Any regime conclusion about the nine strategies above should
carry this sensitivity beside it, and `Cluc7werk` should not be characterised
from the canonical arm alone.
