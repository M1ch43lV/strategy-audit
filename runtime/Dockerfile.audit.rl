# Reinforcement-learning variant of the pinned audit runtime.
#
# Kept separate from the lean image on purpose: torch and stable-baselines3 add
# well over a gigabyte, and every confirmatory measurement so far was produced
# under the lean digest. Rows measured here record this image's own digest, the
# same way BuyRegions recorded its tensorflow image.
ARG BASE_IMAGE=strategy-audit-runtime:2026.7
FROM ${BASE_IMAGE}

# Freqtrade ships the exact pins for its own RL extras; use them rather than
# guessing versions that merely look compatible.
RUN python -m pip install --user --no-cache-dir \
      -r /freqtrade/requirements-freqai-rl.txt \
    && python -c "import torch, gymnasium, stable_baselines3, sb3_contrib; \
print('torch', torch.__version__, '| sb3', stable_baselines3.__version__)"

# CatBoost is not in freqtrade's own requirements - it is an optional gradient
# booster freqtrade supports and does not pin - so it is named here and its
# resolved version printed into the build log, which is the only pin this one
# gets. Three corpus strategies ask for CatboostClassifier by name; without it
# freqtrade reports "Impossible to load FreqaiModel", which says nothing about
# the strategy.
RUN python -m pip install --user --no-cache-dir catboost     && python -c "import catboost; print('catboost', catboost.__version__)"

LABEL org.opencontainers.image.title="strategy-audit RL runtime" \
      org.opencontainers.image.description="Pinned Linux runtime plus freqai-rl extras and catboost"
