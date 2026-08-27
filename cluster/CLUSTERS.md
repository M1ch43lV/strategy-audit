# Corpus clusters

900 canonical strategies classified. Source: `cluster/CLUSTERS.csv`, produced by `cluster/classify.py`.

Five **independent** axes rather than one bucket. A strategy is not `mean_reversion` OR `long_short`, it is both at once - and for the question "which market phase" the combination is what matters. Every label carries its reason in `clusters.json` under `why`, so a wrong classification can be refuted on the individual case rather than only showing up as noise in the aggregate.

This is a preregistered **source taxonomy**, not behavioral clustering. It consumes `EXECUTION_PROFILES.csv`, keeps dormant short writes separate through canonical `direction_capability`, and does not determine `regime_eligible`.

## Direction

| Category | Count | Share | of which measured |
|---|---:|---:|---:|
| `long_only` | 832 | 92.4% | 572 (69%) |
| `long_short` | 61 | 6.8% | 47 (77%) |
| `unknown` | 4 | 0.4% | 0 (0%) |
| `short_only` | 3 | 0.3% | 3 (100%) |

## Trading logic

| Category | Count | Share | of which measured |
|---|---:|---:|---:|
| `trend_following` | 409 | 45.4% | 279 (68%) |
| `volatility` | 113 | 12.6% | 92 (81%) |
| `mean_reversion` | 104 | 11.6% | 85 (82%) |
| `unclear` | 96 | 10.7% | 51 (53%) |
| `momentum` | 76 | 8.4% | 54 (71%) |
| `hybrid` | 54 | 6.0% | 47 (87%) |
| `ml_freqai` | 34 | 3.8% | 3 (9%) |
| `breakout` | 14 | 1.6% | 11 (79%) |

## Speed

| Category | Count | Share | of which measured |
|---|---:|---:|---:|
| `scalp` | 546 | 60.7% | 406 (74%) |
| `intraday` | 209 | 23.2% | 170 (81%) |
| `unknown` | 88 | 9.8% | 0 (0%) |
| `swing` | 33 | 3.7% | 27 (82%) |
| `position` | 24 | 2.7% | 19 (79%) |

## Complexity

| Category | Count | Share | of which measured |
|---|---:|---:|---:|
| `simple` | 498 | 55.3% | 365 (73%) |
| `moderate` | 244 | 27.1% | 175 (72%) |
| `complex` | 158 | 17.6% | 82 (52%) |

## Expected market phase

| Category | Count | Share | of which measured |
|---|---:|---:|---:|
| `bull` | 451 | 50.1% | 299 (66%) |
| `undetermined` | 162 | 18.0% | 93 (57%) |
| `high_vol` | 111 | 12.3% | 90 (81%) |
| `range` | 98 | 10.9% | 79 (81%) |
| `bear+range` | 64 | 7.1% | 50 (78%) |
| `transition+high_vol` | 14 | 1.6% | 11 (79%) |

## The finding that matters for regime analysis

Whether a strategy ever entered the audit's ladder depends heavily on its cluster. The measured sample is therefore not the corpus:

| Group | Measured |
|---|---:|
| `ml_freqai` | 3 of 34 (9%) |
| `long_short` | 47 of 61 (77%) |
| `short_only` | 3 of 3 (100%) |
| `long_only` | 572 of 832 (69%) |
| `complex` | 82 of 158 (52%) |
| `simple` | 365 of 498 (73%) |
| `unknown` | 0 of 88 (0%) |

Any statement the audit makes about "public freqtrade strategies" is therefore in practice a statement about **simple, long-only, spot-capable** ones. Strategies built for falling markets - the `short_only` and `long_short` groups - are less represented, which is precisely the group a regime study needs.
