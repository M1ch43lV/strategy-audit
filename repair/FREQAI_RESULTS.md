# FreqAI investigator run

Status: completed for all eight registered targets. These measurements have
`run_class=freqai`; they do not form a third population and are not directly
comparable with the ordinary spot audit.

| Strategy | Source | In sample | Out of sample | Interpretation |
|---|---|---|---|---|
| `NOTankAi_15` | original | PASS | PASS | 1,648 / 2,367 trades; extreme returns require a separate plausibility audit |
| `NOTankAi_17` | original | NA | NA | short-only strategy under the spot investigator configuration |
| `NOTankAi_19` | original | NA | NA | short-only strategy under the spot investigator configuration |
| `Proton` | original | NA | NA | short-only strategy under the spot investigator configuration |
| `RLStrategy` | original | NA | NA | training data removed because of NaNs; no usable summary |
| `TankAi` | original | NA | NA | missing custom-model return `DI_cutoff` |
| `TankAiRevival` | original | NA | NA | missing custom-model return `DI_cutoff` |
| `AstroQAV4` | repaired | NA | NA | Class-2 overlay loads, then lacks custom-model return `DI_cutoff` |

## Interpretation boundaries

- Freqtrade 2026.7 emits `DI_values` when the Dissimilarity Index is enabled,
  but it does not emit `DI_cutoff`.
- The three affected strategies also expect dynamically supplied sort
  thresholds. Their repository contains no matching custom prediction model.
- Initializing the documented `extra_returns_per_train` placeholders would
  make those columns constant under the generic LightGBM model. That changes
  the intended decision logic and is therefore not treated as a harmless
  harness repair.
- The first completed run used the generated configs stored under
  `strategy-audit/user_data/freqai_configs`. Those configs contain the typo
  `include_shifted_candidates`; Freqtrade ignored it. The runner now uses the
  correct `include_shifted_candles`, but the expensive completed measurements
  have not been silently replaced.

The JSON files in `results_freqai/` remain the source records, including exact
failure messages and elapsed times.
