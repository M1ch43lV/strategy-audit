# -*- coding: utf-8 -*-
"""FreqAI config for AntigravityStrategy and AntigravityStrategyV3, built from
the author's own backtest config.

Both stop with "freqAI is not enabled" - freqtrade will not start a FreqAI
strategy without a `freqai` section, and the ordinary audit config has none.
Unlike WTAI/WTRSIAI (see freqai_config_wtai.py), these two are not blocked by
the deprecated populate_any_indicators() API: both already use the current
feature_engineering_expand_all/feature_engineering_standard/set_freqai_targets
interface, confirmed by reading the strategy source directly, so a config is
plausibly sufficient to actually run them, not just decide the row.

WHERE THE VALUES COME FROM. The author's own repository (Vijay190899/Trade-Bot)
carries config/config_backtest.json with "strategy": "AntigravityStrategy" and
a live (not commented-out) freqai block, purpose-built for backtesting rather
than live trading. Every feature/model parameter here is theirs:
train_period_days 30, backtest_period_days 7, label_period_candles 24,
include_shifted_candles 2, DI_threshold 0.9, weight_factor 0.9,
use_SVM_to_remove_outliers true, n_estimators 200, learning_rate 0.05. The
config's own freqaimodel is "LightGBMRegressor" - a freqtrade-built-in, not
the repo's custom AntigravityRLModel (PPO reinforcement learning, needs
stable-baselines3 and a live TradeMemory SQLite loop this audit has no
equivalent of). is_rl = "RL" in self.config.get("freqaimodel", "") in the
strategy's own source confirms the LightGBMRegressor path is author-sanctioned,
not a workaround.

WHAT IS NOT THEIRS, AND WHY. One thing had to be decided here:

* `model_training_parameters.device` - the author's config asks for "gpu" with
  gpu_device_id 0. This runtime's LightGBM has no GPU build; forced to "cpu",
  which is a runtime capability, not a strategy parameter.

include_timeframes (1h, 4h) and include_corr_pairlist (BTC/USDT) are used as
written - both strategies declare timeframe=1h, so the author's own feature
timeframes already start at the strategy's own base, and BTC/USDT is already
one of the eight pairs this audit holds. Nothing to adjust for either.

AntigravityStrategyV3 reuses the same config: it declares an identical
timeframe and the identical feature_engineering_*/set_freqai_targets method
signatures as the base version (confirmed by reading both source files), so
the same feature set applies to both rather than inventing a second one.

The result is a config, not a measurement. It says these two can be run at
all; whether they produce anything, and whether what they produce clears the
bias gates, is the run's own answer.
"""
from __future__ import annotations

import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTHOR = os.path.join(ROOT, "repos", "Vijay190899_Trade-Bot", "config",
                      "config_backtest.json")
BASE = os.path.join(ROOT, "profile_spot_config.json")
OUT_DIR = os.path.join(ROOT, "user_data", "freqai_configs")
TARGETS = ("AntigravityStrategy", "AntigravityStrategyV3")
BASE_TIMEFRAME = "1h"


def author_freqai_block():
    """The author's own `freqai` block from their backtest config, unchanged
    except that it is read, not retyped."""
    data = json.load(io.open(AUTHOR, encoding="utf-8-sig"))
    return data["freqai"], data.get("freqaimodel")


def build(strategy):
    config = json.load(io.open(BASE, encoding="utf-8"))
    freqai, freqaimodel = author_freqai_block()
    freqai = json.loads(json.dumps(freqai))  # deep copy, one dict per file
    freqai["identifier"] = "freqai_%s" % strategy
    # Runtime capability, not a strategy parameter - see module docstring.
    freqai.get("model_training_parameters", {})["device"] = "cpu"
    freqai["model_training_parameters"].pop("gpu_device_id", None)
    config["freqai"] = freqai
    config["timeframe"] = BASE_TIMEFRAME
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "%s.json" % strategy)
    with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return path, freqaimodel


def selftest():
    freqai, freqaimodel = author_freqai_block()
    assert freqai["enabled"] is True
    assert freqai["train_period_days"] == 30, freqai["train_period_days"]
    assert freqai["feature_parameters"]["label_period_candles"] == 24
    assert freqai["feature_parameters"]["DI_threshold"] == 0.9
    assert freqai["feature_parameters"]["include_timeframes"] == ["1h", "4h"]
    assert freqaimodel == "LightGBMRegressor", freqaimodel
    print("freqai_config_antigravity selftest: PASS (author block read, "
          "%d targets)" % len(TARGETS))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--selftest":
        selftest()
        return 0
    for strategy in TARGETS:
        path, freqaimodel = build(strategy)
        print("%-24s -> %s  freqaimodel=%s"
              % (strategy, os.path.relpath(path, ROOT), freqaimodel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
