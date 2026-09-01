# Wave C - canonical measurement results

All 218 measurable Wave C rows were run through the frozen smoke window
`20200301-20200401`. The queue was exhaustive: every row has a result.

## Outcome

| | rows |
|---|---|
| measured, produced trades | 53 |
| measured, zero trades in the smoke window | 13 |
| failed | 152 |
| **total** | **218** |

66 of 218 rows ran at all - a 30 % start rate. Measurement is not eligibility:
both bias gates still follow, and Wave A showed those gates excluding two of the
three rows they decided.

## Why 152 rows failed

| cause | rows | can it be repaired here? |
|---|---|---|
| class not loadable | 51 | no - genuine defects |
| no `timeframe` declared | 48 | **decision required** |
| numpy / pandas dtype conflict | 12 | no - would need an older stack |
| outdated freqtrade interface | 10 | no - would need source edits |
| freqAI not enabled in config | 5 | possibly, at the config layer |
| required field missing (`stoploss`) | 3 | no |
| required method missing | 2 | no |
| assorted single defects | 21 | no |

### The 48 rows without a declared timeframe

These strategies never state which candle size they trade. Their authors must
have supplied it from a config we do not have. Setting one would not be a
neutral repair: the timeframe decides the entire behaviour of a strategy, so
picking a value invents a parameter the author never chose and classifies a
strategy that never existed. This is the same class of problem as the trailing
stop, but sharper, and it is left open pending an explicit decision.

### The 12 dtype and 10 interface failures

These are old strategies meeting freqtrade 2026.7. Repairing them means either
editing the sources, which changes behaviour, or pinning an older runtime, which
breaks comparability with the frozen 67. Neither is available at the harness
layer, so both remain terminal here.

## The 13 zero-trade rows, settled

All 13 have their pooled full-window run. None adds a usable strategy, and the
run was still worth doing: it separated three different things a zero had been
hiding.

| Outcome | Rows |
|---|---:|
| genuinely never trades over the full window | 6 |
| defective in a way the one-month window concealed | 2 |
| already measured before this pass | 4 |
| resource-terminal | 1 |

The two defects are the reason a zero cannot be taken at face value.
`Matrix` reads a `coef` column its own indicator step never creates, and
`zorkv7_0_0` asks a quantile transform for 100,000 quantiles from 10,000
samples. Both ran clean in the smoke window because neither reached the failing
code there. A passed short test is not evidence that a strategy works.

`HarmonicDivergence` spent 1800 seconds on one of eight pairs without
finishing, after reaching 18.5 GiB under the old memory ceiling. Its single
recovery attempt is deliberately unused.

## Both bias gates

See `EXPANSION_WAVE_C_BIAS_RESULTS.md`. Of the 53 rows that produced trades,
three passed both gates and are admitted to E1; 37 are excluded on demonstrated
bias; seven were refused rather than judged by the recursive analyzer and were
routed to the warm-up procedure; six still hold an `NA`.
