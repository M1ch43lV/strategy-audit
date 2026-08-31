# Wave A - seven pending diagnostics

All seven rows were already measured, had coverage `PASS`, zero traps and no
hard exclusion reason. Each was pending only because a bias diagnostic had not
completed. Repairs stayed at the resource and harness layer; no entry or exit
rule was touched.

## Terminal states

| Strategy | Outcome | Basis |
|---|---|---|
| `Fakebuy` | **passes both gates** | needed time only; see below |
| `HyperStra_GSN_SMAOnly` | lookahead `FOUND` | bias in 10 of 13 signals |
| `kalthetank` | lookahead `FOUND` | bias in 13 of 20 signals |
| `haGradient` | terminal pending | incompatible with the analyzer by construction |
| `InverseVolatilityPortfolio` | terminal pending | analyzer catches 0 of 10 required trades |
| `RiskParityPortfolio` | terminal pending | analyzer catches 0 of 10 required trades |
| `TGMA` | terminal pending | contradictory trailing stop; repair changes exits |

Net effect: one row becomes admissible, two are excluded on evidence rather
than left undecided, and four remain pending for reasons that cannot be removed
without changing what is being tested.

## What the resource layer actually fixed

`Fakebuy` spent 635 s on the first window and then hit the 300 s fallback limit
that the cascade gives its later, larger windows. With a matching timeout it
completes in the intermediate window and reports no bias.
`HyperStra_GSN_SMAOnly` was killed by the old 5.8 GiB memory ceiling; under the
raised limit it completes and reports bias. Neither outcome was available
before, and one of them is negative - the resource fix bought verdicts, not
admissions.

## Why three rows cannot be repaired here

- **`haGradient`** raises `ValueError` when `len(dataframe)` is below its FFT
  window. Freqtrade's lookahead analysis works by replaying the strategy on
  deliberately truncated slices, so the analyzer must hand it short frames. The
  cascade was extended and ran all three windows; the failure still reports 101
  rows, because the limit is the analyzer's truncation, not the window. Making
  this pass means editing the strategy to tolerate short frames, which changes
  behaviour and belongs to E3.
- **`InverseVolatilityPortfolio` / `RiskParityPortfolio`** are daily-timeframe
  portfolio strategies that enter only on rebalance dates, so they never reach
  the analyzer's minimum of 10 caught trades. Note that bias diagnostics run at
  `max_open_trades = 3` while canonical measurement uses `8`; aligning them
  would invalidate every bias result already recorded, so it was not done.
- **`TGMA`** sets `trailing_stop = True` (overriding an earlier `False`) with
  activation at 1.3 % profit and a 3.5 % trail, so the stop activates below
  entry. Freqtrade rejects the pair as incoherent. `use_custom_stoploss = True`
  is set but no `custom_stoploss` method exists; in `IStrategy` the custom and
  trailing branches are independent, so the trailing logic is live rather than
  vestigial. Any repair alters exits.

## E0 is untouched

Regenerating `REGIME_ELIGIBILITY.csv` from the new bias results would move
`Fakebuy` to `eligible` and the two `FOUND` rows to `ineligible`, taking the
table from 67 to 68. That file is the frozen E0 baseline and was deliberately
not rewritten. `Fakebuy` belongs in the E1 expansion, recorded beside E0.
