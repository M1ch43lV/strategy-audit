# Wave B static proofs - findings

Plan 5.1 condition 6 requires a file-specific proof that decisions do not
depend on history *below* the adapter boundary. Reviewing the 13 exactly
equivalent rows split them cleanly in two.

## Admitted (6 new, plus the 2 already held)

Every lookback is a finite window that fits inside the frozen warm-up.

| Strategy | Warm-up | Longest lookback | Basis |
|---|---|---|---|
| `BinHV45` | 40 | 40 | 40-candle rolling band + one-row shift |
| `BinHV45_kanaxe` | 40 | 40 | same family, no other indicator |
| `BinHV45_stash` | 40 | 40 | same family, no other indicator |
| `BinHV45_werkkrew` | 40 | 40 | same family; `nan_to_num` + `.gt(0)` also blocks warm-up entries |
| `BollingerBandStrategy` | 21 | 21 | `BBANDS(20)` and 21-candle rolling sums, no shift |
| `CCI_BB` | 20 | 20 | `CCI(14)` and a 20-candle band, no shift |

## Not admitted (5)

No proof was written for these. The frozen warm-up does not cover the
dependency, so writing one would assert something untrue.

- **`Strategy004`** (warm-up 5, timeframe 5m). Contains `STOCHF(dataframe, 50)`,
  `ADX(dataframe, 35)`, `CCI` (14) and `rolling(12)`. The longest literal period
  is 50, ten times the frozen warm-up. The recorded derivation basis, "longest
  literal indicator period 5", took a minimum rather than a maximum.
- **`Cluc4`** (warm-up 168, timeframe 1m). Its informative frame is hourly and
  carries `ROCR(timeperiod=168)`. 168 hourly candles are 10,080 one-minute
  candles, so the value was carried across timeframes without conversion.
- **`TouchEmaStrategy`** (warm-up 60, timeframe 5m). `populate_indicators`
  iterates the whole `IntParameter(40, 100)` range, so EMAs up to period 100 are
  computed. Worse, `bars_delay_*` is a counter mutated through `self` inside a
  row-wise `apply`, which accumulates from the first row of the frame. That
  dependency is stateful and unbounded, not merely long.
- **`Combined_Indicators`** (warm-up 50) and **`CombinedBinHAndClucHyperV0`**
  (warm-up 91). Their finite windows fit, but both decide on `ta.EMA`, which is
  recursively smoothed and never fully forgets its seed. No finite warm-up makes
  such a series exact, so the condition cannot be proved, only approximated.

## Why the exact trade match was not sufficient on its own

All 13 rows matched the original pooled trade list exactly. That match shows the
warm-up metadata does not change behaviour, which is the right question for
admission. It does not show the warm-up is long enough: with the authored
`startup_candle_count=0` the early rows carry NaN indicators and simply produce
no entries, so both configurations agree about a region in which neither trades.
Condition 6 exists precisely to catch that, and here it caught five rows.

## Adjudicator change

The checker previously accepted a proof only when all three dependency fields
began with the literal `none;`, which admits only strategies with no history at
all. That is narrower than the written condition. It now also accepts a bounded
dependency that states `max_history_lookback_candles` and fits inside the
warm-up, and still rejects anything unbounded, stateful or recursive.
