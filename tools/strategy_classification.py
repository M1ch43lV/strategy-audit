# -*- coding: utf-8 -*-
"""Per-strategy timeframe and a best-effort signal-family label.

Both are static properties of the strategy's own source, not measurement
results, so they get their own store rather than living inline in
`strategy_status.py`: neither depends on whether a row ever ran.

TIMEFRAME. Freqtrade strategies declare `timeframe = "5m"` as a class
attribute; older ones use the pre-2021.4 name `ticker_interval`. Read from
the class block matching the strategy's own name, not the whole file - 121
of 900 canonical files hold more than one class, and a file-wide search
would occasionally attribute one strategy's timeframe to another sharing
its file. `ELIGIBILITY_TIMEFRAME_REPAIR.json` is checked first and wins
where it has an answer: that store already recovered a timeframe from
something other than the plain attribute (the author's own config, in
one case) for rows the plain read cannot answer, and repeating a weaker
read here would only disagree with a stronger one already on file.
Left blank rather than guessed for the 43 rows - mostly FreqAI templates,
test fixtures and ensemble wrappers - where the class block declares
neither name.

STRATEGY_TYPE. There is no measurement behind this label, only which named
indicators appear in the strategy's own class block. It describes the
ingredients found, not a verdict about what the strategy does with them,
and most rows carry more than one label because most strategies mix
families - that is read as the corpus reads, not smoothed into one box
per row. The dividing line is between indicators specific enough to name
a family on their own (TIER1: an ATR or a SuperTrend is not used for much
else) and the handful so common - RSI, a moving average, ADX - that most
strategies touch them regardless of design (TIER2), which are read only
when no TIER1 marker is present, so a SuperTrend strategy that also opens
with RSI is trend-following, not mean-reversion by way of a tie-break
nobody asked for. FreqAI, scikit-learn, PyTorch and the boosted-tree
libraries mark `ml_ai` and suppress every other label: an EMA computed as
a model feature is not evidence the strategy is momentum-based.
`scalping` is not an indicator family at all - it is timeframe alone
(1m/3m/5m) - and is added on top of whatever else applies, never in place
of it. Blank where no marker matches at all (63 rows).

Changing the marker table changes the label on however many of the 900
rows it touches, which is the point of keeping it in one place instead of
scattered regexes: anyone auditing a strategy's label reads the same five
tables this module runs on.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
TIMEFRAME_REPAIR = os.path.join(ROOT, "ELIGIBILITY_TIMEFRAME_REPAIR.json")
OUTPUT = os.path.join(ROOT, "STRATEGY_CLASSIFICATION.json")

CLASS_RE = re.compile(r"^class\s+(\w+)\s*\(", re.M)
TIMEFRAME_RE = re.compile(
    r"(?<!informative_)\btimeframe\b\s*(?::\s*\w+)?\s*=\s*['\"]([^'\"]+)['\"]")
TICKER_INTERVAL_RE = re.compile(
    r"\bticker_interval\b\s*(?::\s*\w+)?\s*=\s*['\"]([^'\"]+)['\"]")

SCALP_TIMEFRAMES = frozenset(["1m", "3m", "5m"])

# Distinctive enough to name a family on their own; one hit attaches the
# label, and a strategy can carry more than one.
TIER1 = {
    "mean_reversion": (r"\bstoch", r"\bcci\b", r"williams", r"\bmfi\b",
                       r"z_?score"),
    "momentum": (r"\bmacd\b", r"\broc\b", r"\btrix\b", r"plus_di|minus_di"),
    "volatility_breakout": (r"\batr\b", r"donchian", r"keltner",
                            r"\bnatr\b", r"\bbreakout\b"),
    "trend_following": (r"supertrend", r"ichimoku", r"\bsar\b|parabolic",
                        r"\bhma\b", r"\bkama\b"),
    "grid_dca": (r"position_adjustment_enable", r"\bdca\b", r"\bgrid\b"),
    "stat_arb": (r"correl|pearsonr|coint",),
    "volume_based": (r"\bobv\b", r"\bvwap\b", r"\bvwma\b",
                     r"chaikin|accum\w*.{0,10}dist"),
}
# Common enough to appear regardless of design; read only when no TIER1
# marker is present.
TIER2 = {
    "mean_reversion": (r"\brsi\b", r"bollinger|bb_(lower|upper|middle)band"),
    "momentum": (r"\bema\d*\b", r"\bsma\d*\b"),
    "trend_following": (r"\badx\b",),
}
# Present anywhere in the class block, exclusive of every TIER label: an
# indicator computed as a model feature is not evidence of the family it
# usually implies.
ML_MARKERS = (r"freqai", r"tensorflow|keras", r"\bsklearn\b", r"\btorch\b",
             r"lightgbm|catboost|xgboost", r"\btslearn\b", r"\bpmdarima\b",
             r"\bprophet\b|statsmodels")


def _compile_table(table):
    return {name: [re.compile(p, re.I) for p in patterns]
            for name, patterns in table.items()}


_TIER1 = _compile_table(TIER1)
_TIER2 = _compile_table(TIER2)
_ML = [re.compile(p, re.I) for p in ML_MARKERS]


def _csv(path):
    if not os.path.exists(path):
        return []
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _json_results(path):
    if not os.path.exists(path):
        return {}
    return json.load(io.open(path, encoding="utf-8")).get("results", {})


def class_block(text, strategy_id):
    """Text from this strategy's own class line to the next class line, or
    the whole file when the name is not found - a multi-class file's wrong
    class is worse than no read at all."""
    classes = list(CLASS_RE.finditer(text))
    starts = {match.group(1): match.end() for match in classes}
    if strategy_id not in starts:
        return text
    start = starts[strategy_id]
    later = sorted(match.start() for match in classes if match.start() > start)
    return text[start:(later[0] if later else len(text))]


def timeframe_of(block, repaired):
    if repaired and repaired.get("timeframe"):
        return (repaired["timeframe"],
                "repair:" + (repaired.get("timeframe_evidence") or "recovered"))
    match = TIMEFRAME_RE.search(block)
    if match:
        return match.group(1), "timeframe_attr"
    match = TICKER_INTERVAL_RE.search(block)
    if match:
        return match.group(1), "ticker_interval_attr"
    return "", ""


def strategy_type_of(whole_file, block, timeframe):
    # ML_MARKERS is checked against the whole file, not the class block: a
    # library is named once, at its `import` line above the class, and used
    # afterwards through the name that import bound - `dtw(...)`, not
    # `tslearn.dtw(...)` - so scoping to the class block reads as if the
    # strategy never touched it. A multi-class file importing one ML
    # library still imports it for that file's own strategy; an indicator
    # named INSIDE a neighbouring class is a different risk, which is why
    # TIER1/TIER2 stay scoped to the block.
    if any(rx.search(whole_file) for rx in _ML):
        types = {"ml_ai"}
    else:
        types = {name for name, rxs in _TIER1.items()
                if any(rx.search(block) for rx in rxs)}
        if not types:
            types = {name for name, rxs in _TIER2.items()
                    if any(rx.search(block) for rx in rxs)}
    if timeframe in SCALP_TIMEFRAMES:
        types.add("scalping")
    return types


def build():
    repair = _json_results(TIMEFRAME_REPAIR)
    results = {}
    for row in _csv(STATUS):
        strategy = row["strategy_id"]
        source_file = row["source_file"]
        path = os.path.join(ROOT, source_file.replace("/", os.sep)) \
            if source_file else ""
        if not path or not os.path.exists(path):
            results[strategy] = {"timeframe": "", "timeframe_evidence": "",
                                 "strategy_type": ""}
            continue
        with io.open(path, encoding="utf-8", errors="ignore") as handle:
            text = handle.read()
        block = class_block(text, strategy)
        timeframe, evidence = timeframe_of(block, repair.get(strategy))
        types = strategy_type_of(text, block, timeframe)
        results[strategy] = {
            "timeframe": timeframe,
            "timeframe_evidence": evidence,
            "strategy_type": ";".join(sorted(types)),
        }
    return results


def selftest():
    results = build()
    assert len(results) == len(_csv(STATUS)), (len(results), len(_csv(STATUS)))
    have_tf = sum(1 for v in results.values() if v["timeframe"])
    have_type = sum(1 for v in results.values() if v["strategy_type"])
    assert have_tf >= 850, have_tf
    assert have_type >= 800, have_type
    # A plain author-declared case, read the ordinary way.
    assert results["ARIMASTR"]["timeframe"] == "5m", results["ARIMASTR"]
    # A recovered case must come from the repair store, not a fresh guess.
    assert results["ADX_15M_USDT"]["timeframe"] == "15m", results["ADX_15M_USDT"]
    assert results["ADX_15M_USDT"]["timeframe_evidence"].startswith("repair:")
    # A FreqAI strategy is ml_ai only, whatever it also touches as a
    # model feature.
    catboost = results.get("TrainCatBoostStrategy", {})
    assert catboost.get("strategy_type") == "ml_ai", catboost
    # scalping is additive, not a replacement for the indicator-based label.
    five_minute_mean_reversion = next(
        (sid for sid, rec in results.items()
         if rec["timeframe"] == "5m" and "mean_reversion" in
         (rec["strategy_type"] or "").split(";")), None)
    if five_minute_mean_reversion:
        assert "scalping" in results[five_minute_mean_reversion]["strategy_type"].split(";")
    print("strategy_classification selftest: PASS "
          "(%d rows, %d with a timeframe, %d with a type)"
          % (len(results), have_tf, have_type))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    results = build()
    data = {
        "schema_version": 1,
        "description": (
            "Per-strategy timeframe and a heuristic signal-family label, "
            "read from each canonical file's own class block. See the "
            "module docstring in strategy_classification.py for the marker "
            "table and its limits. Neither field is a measurement; both "
            "are regenerated from source and never hand-edited."),
        "results": results,
    }
    with io.open(OUTPUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    have_tf = sum(1 for v in results.values() if v["timeframe"])
    have_type = sum(1 for v in results.values() if v["strategy_type"])
    print("strategy_classification: %d rows, %d with a timeframe, %d with a type"
          % (len(results), have_tf, have_type))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
