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

## Next step for the 13 zero-trade rows

`regime_eligibility.classify` already upgrades a zero-trade smoke result from
`PROFILE_FULL_WINDOW.json`. Those 13 rows need the pooled full-window run before
their trade count can be judged; a zero in a one-month window is not evidence of
a strategy that never trades.
