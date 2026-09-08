# Runtime environments - what each strategy needs to run

**Generated 2026-09-08 17:16:41 by `strategy_status.py`.** Regenerate it rather than editing it.

For the benchmark run: before measuring a row, look up its `required_image` in `STRATEGY_STATUS.csv` and launch it under that image rather than the default. Everything else - which compatibility shims to install, which warm-up to use, which config overrides apply - is read automatically from `PROFILE_CLASS1.json` and `WARMUP_CONVERGENCE.json` by the same `profile_smoke.run_one` / `profile_full_window.py` machinery this audit already uses; the image is the one thing that machinery cannot decide for itself, because it is chosen before any Python in the container runs.

## Images

| Image | Dockerfile | Base | Rows |
|---|---|---|---:|
| `strategy-audit-runtime:2026.7` | `Dockerfile.audit` | freqtradeorg/freqtrade:2026.7 (pinned digest) | 1032 |
| `strategy-audit-tensorflow-runtime:2026.7` | `Dockerfile.audit-tensorflow` | python:3.12-slim (pinned digest) + freqtrade==2026.7 installed directly - a different base line from the default image, not a layer on top of it. | 2 |
| `strategy-audit-packages-runtime:2026.7` | `Dockerfile.audit-packages` | strategy-audit-runtime:2026.7 - a layer on top of the default image, not a separate base line. | 4 |

## `strategy-audit-runtime:2026.7`

**Adds:** requirements-audit-runtime.txt: numpy 2.5.2, pandas 3.0.5, scipy 1.18.1, TA-Lib 0.7.1, and the corpus's other ordinary dependencies.

**For:** The default. Every row not listed under one of the images below runs on this one.

All 1032 rows not listed under another image below.

## `strategy-audit-tensorflow-runtime:2026.7`

**Adds:** requirements-audit-tensorflow.txt: the same requirements-audit-runtime.txt, plus tensorflow==2.21.0, keras==3.15.1, matplotlib==3.11.1. Its own build asserts numpy/pandas/scipy/talib/freqtrade land at the exact versions the default image pins, despite the different base - that assertion is what makes a row measured here comparable with one measured on the default image.

**For:** Rows whose own code imports TensorFlow/Keras at module load time, independent of anything this audit does.

| Strategy | Cohort | Why |
|---|---|---|
| `BuyRegions` | E1_expanded | rules=restore_copied_local_module; PYTHONPATH+=repos/nateemma_strategies; status=applied |
| `CryptoPredictionTraining` | excluded | rules=restore_keras_vis_utils; status=applied |

## `strategy-audit-packages-runtime:2026.7`

**Adds:** requirements-audit-packages.txt: matplotlib, catboost, tslearn, pykalman. Each was checked with `pip install --dry-run` before being added - numpy, pandas and scipy were already satisfied at the pinned versions for all four, so none of them moves the core stack.

**For:** Rows whose own code imports a package the default image does not carry, where that package installs cleanly without touching the pinned numerical core.

| Strategy | Cohort | Why |
|---|---|---|
| `MKR` | excluded | status=applied |
| `Prediction_Strategy` | excluded | status=applied |
| `TrainCatBoostStrategy` | excluded | status=applied |
| `TwoCandleTheory` | exclusion_unconfirmed | status=applied |
