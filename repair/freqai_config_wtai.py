# -*- coding: utf-8 -*-
"""FreqAI configs for WTAI and WTRSIAI, built from their author's own block.

These two are the last rows stopped by `freqAI is not enabled`. Freqtrade will
not start a FreqAI strategy without a `freqai` section, and the ordinary audit
config has none, so nothing about either strategy has ever been measured.

WHERE THE VALUES COME FROM. Their repository carries `config_blank.json` with a
complete `freqai` block commented out - the author's own settings, written for
their own strategies, and the only statement of intent that exists for these
two. Every parameter here is theirs: train_period_days 15, label_period_candles
20, include_shifted_candles 2, DI_threshold 0.9, weight_factor 0.9,
use_SVM_to_remove_outliers true, n_estimators 1500.

WHAT IS NOT THEIRS, AND WHY. Three things had to be decided here, and each is
named on the record rather than folded in silently:

* `include_timeframes` - the author's list reads 1h, 4h, written beside
  strategies on a 1h base. WTAI declares 15m and WTRSIAI 1h. A feature set that
  starts above a strategy's own timeframe is not the author's intent
  transferred, it is a different feature set, so the ladder starts at each
  strategy's own declared value and takes what history exists.
* `include_corr_pairlist` - the author names four correlated pairs. The audit
  holds eight pairs and the two do not have to coincide; the list is
  intersected with what is downloaded rather than demanding data we do not
  have.
* `test_size` - the author writes 0, which freqtrade rejects at validation for
  a backtest. The value from the earlier FreqAI arm, 0.33, is used, and it is
  the one thing here that is neither the author's nor derivable from them.

The result is a config, not a measurement. It says these two can be run at all;
whether they produce anything is the run's answer, and that run is not
comparable with the ordinary spot audit.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTHOR = os.path.join(ROOT, "repos", "jaredrsommer_freqtradestrategies",
                      "config_blank.json")
BASE = os.path.join(ROOT, "user_data", "config.json")
OUT_DIR = os.path.join(ROOT, "user_data", "freqai_configs")
DATA = os.path.join(ROOT, "user_data", "data", "binance")

LADDER = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h",
          "1d"]
TARGETS = {"WTAI": "15m", "WTRSIAI": "1h"}
TEST_SIZE = 0.33


def author_block():
    """The author's `freqai` block, uncommented.

    It is commented out in their file, which makes it a statement of intent
    rather than a running config - but it is their statement, and the only one
    there is for these two strategies.
    """
    text = io.open(AUTHOR, encoding="utf-8-sig").read()
    lines = []
    depth = 0
    started = False
    for line in text.splitlines():
        stripped = line.strip()
        if not started:
            if stripped.startswith('// "freqai"'):
                started = True
            else:
                continue
        if not stripped.startswith("//"):
            # A blank line inside the commented block; the author has one.
            if not stripped:
                continue
            break
        body = stripped[2:].strip()
        lines.append(body)
        depth += body.count("{") - body.count("}")
        if depth == 0 and lines:
            break
    block = chr(10).join(lines).rstrip().rstrip(",")
    return json.loads("{" + block + "}")["freqai"]


def timeframes(base):
    """The strategy's own timeframe first, then the next rungs we hold data for."""
    have = {os.path.basename(name).replace(".feather", "").rsplit("-", 1)[-1]
            for name in os.listdir(DATA) if name.endswith(".feather")}
    index = LADDER.index(base) if base in LADDER else 0
    chosen = [value for value in LADDER[index:index + 3] if value in have]
    return chosen or [base]


def pairs_we_hold(wanted):
    have = {os.path.basename(name).split("-")[0].replace("_", "/")
            for name in os.listdir(DATA) if name.endswith(".feather")}
    return [pair for pair in wanted if pair in have]


def build(strategy, base_timeframe):
    config = json.load(io.open(BASE, encoding="utf-8"))
    freqai = author_block()
    freqai["identifier"] = "freqai_%s" % strategy
    features = freqai["feature_parameters"]
    features["include_timeframes"] = timeframes(base_timeframe)
    features["include_corr_pairlist"] = pairs_we_hold(
        features.get("include_corr_pairlist", []))
    # Freqtrade validates test_size > 0 for a backtest; the author wrote 0.
    freqai.setdefault("data_split_parameters", {})["test_size"] = TEST_SIZE
    config["freqai"] = freqai
    config["timeframe"] = base_timeframe
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "%s.json" % strategy)
    with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def selftest():
    block = author_block()
    assert block["enabled"] is True
    assert block["train_period_days"] == 15, block["train_period_days"]
    features = block["feature_parameters"]
    assert features["label_period_candles"] == 20
    assert features["DI_threshold"] == 0.9
    assert features["include_shifted_candles"] == 2
    assert block["model_training_parameters"]["n_estimators"] == 1500
    # The ladder must start at the strategy's own timeframe, never above it.
    for strategy, base in TARGETS.items():
        chosen = timeframes(base)
        assert chosen[0] == base, (strategy, chosen)
        assert LADDER.index(chosen[-1]) >= LADDER.index(base)
    print("freqai_config_wtai selftest: PASS (author block read, %d targets)"
          % len(TARGETS))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--selftest":
        selftest()
        return 0
    for strategy, base in sorted(TARGETS.items()):
        path = build(strategy, base)
        written = json.load(io.open(path, encoding="utf-8"))
        print("%-10s %-5s -> %s  timeframes=%s corr=%d"
              % (strategy, base, os.path.relpath(path, ROOT),
                 written["freqai"]["feature_parameters"]["include_timeframes"],
                 len(written["freqai"]["feature_parameters"]
                     ["include_corr_pairlist"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
