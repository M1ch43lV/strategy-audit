# -*- coding: utf-8 -*-
"""Which of the six market phases each strategy should theoretically work in.

This is a PREDICTION, written down before the market-phase benchmark runs, so
that the benchmark can falsify it. It is not a measurement and never decides
a cohort. The whole point of recording it now is that a hypothesis formed
after seeing the results is not a hypothesis - `REGIME_AUDIT_PLAN.md` 28.3
forbids tuning the regime labels to make strategies look specialised, and the
mirror-image failure is inventing the strategy's expected phase once its
per-phase numbers are on screen.

THE SIX PHASES. The frozen primary model in `REGIME_PREREGISTRATION.md` emits
four states - BULL, BEAR, SIDEWAYS, TRANSITION - from DMI(14)/ADX(14). Four is
too coarse for this question in one specific way: SIDEWAYS covers both a dead
low-volatility drift and a violent range that traverses its own width every
other day, and those two reward opposite machinery. A grid earns nothing in
the first and well in the second; a stat-arb pair holds in the first and
breaks in the second. So the six phases are the four frozen states with
SIDEWAYS split on volatility, plus a shock phase that outranks the DMI label
entirely - a 30-day realised volatility in the top decile is the market
regardless of which way ADX happens to point that day.

Volatility was stored as descriptive only (preregistration OPEN item 6). The
owner decided it on 2026-09-05, before any per-phase strategy result was
inspected, which is the only order in which that decision is worth anything;
the amendment in `REGIME_PREREGISTRATION.md` records it.

WHERE THE PREDICTION COMES FROM. Two independent readings of the same source,
unioned, because each is wrong in a different place. `strategy_type`
(strategy_classification.py) is multi-label and reads named indicators out of
the strategy's own class block; `logic` (cluster/classify.py) is single-label
and settles ties by counting oscillator against trend against momentum against
volatility indicators. The first sees a strategy that is genuinely two things;
the second refuses to call RSI-plus-EMA both mean-reverting and momentum-driven
and picks the larger count. Taking both and unioning keeps the honest
ambiguity where it exists and the decisive read where one exists.

DIRECTION IS A HARD GATE, not a hint. A long-only strategy cannot earn in a
sustained downtrend - the best it does is stay flat - so `bear_trend` is
removed from it whatever its indicators suggest. 832 of 900 rows are long-only,
which is why this gate does more work than any indicator rule here.

MODEL-DRIVEN ROWS GET NO PREDICTION. Where the strategy hands its decision to
FreqAI, sklearn, torch or a boosted-tree library, the indicators are model
features and say nothing about which phase the model favours - the same
reasoning that makes `ml_ai` exclusive in strategy_classification.py. Those
rows are left blank rather than given an invented prior. A blank is a real
answer here: it says the source does not support a prediction, which the
benchmark can still check against, by asking whether those rows turn out to be
phase-neutral.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(ROOT, "evidence/EXECUTION_PROFILES.csv")
CLASSIFICATION = os.path.join(ROOT, "evidence/STRATEGY_CLASSIFICATION.json")
CLUSTERS = os.path.join(ROOT, "cluster", "clusters.json")
OUTPUT = os.path.join(ROOT, "evidence/MARKET_PHASE_HYPOTHESIS.json")

# The market side of each phase, so the benchmark resolves the prediction
# against the same rule it was written under. Thresholds are the ones measured
# over the frozen window in `results/regime/regime_daily.csv` (18000 pair-days,
# 2020-03-01 to 2026-08-21): the shock cut is the 90th percentile of
# `coin_realized_vol_30d` over all pair-days, the SIDEWAYS split its median
# over SIDEWAYS days alone. Stated as numbers rather than as "top decile" so a
# later run cannot silently re-derive a different cut from different data.
SHOCK_VOL = 1.291
RANGE_SPLIT_VOL = 0.623

PHASES = {
    "bull_trend": "coin_adx >= 25 and coin_plus_di > coin_minus_di",
    "bear_trend": "coin_adx >= 25 and coin_minus_di > coin_plus_di",
    "range_quiet": "coin_adx < 20 and coin_realized_vol_30d < %s" % RANGE_SPLIT_VOL,
    "range_choppy": "coin_adx < 20 and coin_realized_vol_30d >= %s" % RANGE_SPLIT_VOL,
    "transition": "20 <= coin_adx < 25",
    "high_vol_shock": "coin_realized_vol_30d >= %s, whatever the DMI state"
                      % SHOCK_VOL,
}
# The shock phase outranks the DMI label: a day in the top volatility decile is
# that day's market, and reading it as an ordinary BULL would put a crash and a
# steady rally in the same bucket.
PRECEDENCE = ("high_vol_shock",)

# What each signal family should favour. Read as "this ingredient is evidence
# for these phases", never as "only these phases can hold this strategy".
FAMILY_PHASES = {
    # A trend follower needs a trend to follow and is chopped up without one.
    "trend_following": ("bull_trend",),
    "momentum": ("bull_trend",),
    # A breakout fires as the range gives way, which is what 20 <= ADX < 25
    # is, and pays out on the expansion that follows.
    "volatility_breakout": ("transition", "high_vol_shock"),
    # Oscillators need a level to revert to. Both range phases qualify; the
    # quiet one gives cleaner bounds, the choppy one gives more of them.
    "mean_reversion": ("range_quiet", "range_choppy"),
    # A grid earns per traversal, so it needs the range to actually be
    # travelled. In a dead range it fills almost nothing.
    "grid_dca": ("range_choppy",),
    # Correlation and cointegration hold while nothing is repricing, and a
    # shock is precisely the event that breaks the relationship being traded.
    "stat_arb": ("range_quiet",),
    # OBV confirms a trend, VWAP anchors an intraday reversion. The family
    # points both ways at once, so on its own it predicts nothing.
    "volume_based": (),
    # A speed, not a phase.
    "scalping": (),
    # See the module docstring: the indicators are model features.
    "ml_ai": (),
}
# cluster/classify.py's single decisive label, which resolves the mixtures
# `strategy_type` deliberately leaves open.
LOGIC_PHASES = {
    "trend_following": ("bull_trend",),
    "momentum": ("bull_trend",),
    "breakout": ("transition", "high_vol_shock"),
    "mean_reversion": ("range_quiet", "range_choppy"),
    # Channel and range indicators with no crossover entry - band width is
    # being traded, or used to size a stop, either of which pays in expansion.
    "volatility": ("high_vol_shock",),
    "ml_freqai": (),
    "unclear": (),
    "hybrid": (),
}
MODEL_DRIVEN = ("ml_ai", "ml_freqai")
SHORT_CAPABLE = ("short_only", "long_short")
# `logic == "volatility"` means channel indicators with no crossover entry,
# which is two opposite trades wearing the same indicators: a reversion to the
# middle band, or a trade on the expansion itself. The band's own name
# separates them, and `clusters.json` records the indicator names per row -
# 92 of the 113 volatility rows name one of these.
BAND_MARKERS = ("bollinger_bands", "BBANDS")


def _csv(path):
    if not os.path.exists(path):
        return []
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def phases_for(strategy_types, logic, direction, indicators=()):
    """The predicted phases for one strategy, plus the reason for each source.

    Returns `(sorted_phases, evidence)`. Empty where the source supports no
    prediction, which is a result and not a gap.

    `logic` decides and `strategy_type` fills its silence, rather than the two
    being unioned. Unioning them was tried first and predicted five of the six
    phases for 100 rows and all six for one, which is not a prediction at all:
    `strategy_type` fires a family on a single marker, and the most common
    marker in this corpus is an ATR that exists only to size a stoploss. Read
    generously that makes half the corpus a volatility strategy. `logic`
    settles exactly this by counting oscillator against trend against momentum
    against volatility indicators and naming the winner, so it is what decides
    wherever it reaches a verdict.
    """
    if "ml_ai" in strategy_types or logic in MODEL_DRIVEN:
        return [], "model_driven: indicators are model features, no phase prior"

    phases, why = set(), []
    if logic == "volatility" and any(marker in indicators
                                     for marker in BAND_MARKERS):
        # Bollinger bands entered without a crossover is a reversion to the
        # middle band, not a volatility-expansion trade. Decided on the named
        # band rather than on a `mean_reversion` type label: that label fires
        # on a bare RSI, which nearly every row in the corpus carries, and
        # would hand the whole volatility class to the range phases.
        phases |= {"range_quiet", "range_choppy"}
        why.append("logic(volatility) + named band: reversion, not expansion")
    elif LOGIC_PHASES.get(logic):
        phases |= set(LOGIC_PHASES[logic])
        why.append("logic(%s)" % logic)
    else:
        # Only where the decisive read reached no verdict - `unclear` found no
        # recognised indicator, `hybrid` found no majority. The generous read
        # is better than nothing here, and nothing is what it replaces.
        for family in strategy_types:
            phases |= set(FAMILY_PHASES.get(family, ()))
        if phases:
            why.append("logic(%s) undecided, type(%s)"
                       % (logic or "none", ",".join(sorted(strategy_types))))

    # Direction decides what the strategy can express, and it overrides every
    # indicator read: a long-only strategy holding a perfect downtrend signal
    # still cannot act on it.
    if direction in SHORT_CAPABLE:
        if "bull_trend" in phases:
            phases.add("bear_trend")
            why.append("direction(%s): trend prediction mirrors to bear" % direction)
        if direction == "short_only":
            phases.discard("bull_trend")
            why.append("direction(short_only): bull removed")
    else:
        if "bear_trend" in phases:
            phases.discard("bear_trend")
        why.append("direction(%s): bear excluded" % (direction or "unknown"))
    if not phases:
        return [], "; ".join(why) or "no phase-bearing marker in source"
    return sorted(phases), "; ".join(why)


def build():
    classification = json.load(
        io.open(CLASSIFICATION, encoding="utf-8")).get("results", {})
    clusters = {row["strategy"]: row
                for row in json.load(io.open(CLUSTERS, encoding="utf-8"))}
    results = {}
    for row in _csv(PROFILES):
        strategy = row["strategy_id"]
        record = classification.get(strategy, {})
        types = [t for t in (record.get("strategy_type") or "").split(";") if t]
        cluster = clusters.get(strategy, {})
        # `direction_capability` in the manifest is the canonical read - it is
        # what `axis_direction` copies - so it is taken from there rather than
        # from the cluster mirror, which is missing for a row clusters could
        # not parse.
        direction = row.get("direction_capability") or cluster.get("direction", "")
        phases, evidence = phases_for(types, cluster.get("logic", ""), direction,
                                      cluster.get("indicators") or ())
        results[strategy] = {
            "assumed_market_regime": ";".join(phases),
            "assumed_market_regime_evidence": evidence,
        }
    return results


def selftest():
    results = build()
    assert len(results) == len(_csv(PROFILES)), (len(results), len(_csv(PROFILES)))
    assert set(PHASES) == {
        "bull_trend", "bear_trend", "range_quiet", "range_choppy",
        "transition", "high_vol_shock"}, sorted(PHASES)

    # Nothing may name a phase the market model cannot emit. This is the check
    # that the earlier `high_vol` hypothesis failed: 125 rows predicted a phase
    # no daily label ever carried, so no run could confirm or refute them.
    for strategy, record in results.items():
        for phase in record["assumed_market_regime"].split(";"):
            assert not phase or phase in PHASES, (strategy, phase)

    # The direction gate is not advisory. A long-only strategy predicted to
    # work in a sustained downtrend would be a prediction about a trade it
    # cannot place.
    directions = {row["strategy_id"]: row.get("direction_capability", "")
                  for row in _csv(PROFILES)}
    for strategy, record in results.items():
        if directions.get(strategy) not in SHORT_CAPABLE:
            assert "bear_trend" not in record["assumed_market_regime"].split(";"), \
                strategy
        assert bool(record["assumed_market_regime"]) or \
            record["assumed_market_regime_evidence"], strategy

    # A model-driven row gets no prediction, and says why rather than going
    # quietly blank.
    model_rows = [s for s, r in results.items()
                  if r["assumed_market_regime_evidence"].startswith("model_driven")]
    assert model_rows, "no model-driven rows found - the suppression is dead code"
    for strategy in model_rows:
        assert not results[strategy]["assumed_market_regime"], strategy

    predicted = sum(1 for r in results.values() if r["assumed_market_regime"])
    print("market_phase_hypothesis selftest: PASS (%d rows, %d with a "
          "prediction, %d model-driven, %d without a phase-bearing marker)"
          % (len(results), predicted, len(model_rows),
             len(results) - predicted - len(model_rows)))
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
            "Predicted market phases per strategy, written before the "
            "market-phase benchmark runs so that it can falsify them. Not a "
            "measurement; decides nothing. See the module docstring in "
            "market_phase_hypothesis.py for how each prediction is derived "
            "and why model-driven rows carry none."),
        "phases": PHASES,
        "phase_precedence": list(PRECEDENCE),
        "thresholds": {"shock_realized_vol_30d": SHOCK_VOL,
                       "range_split_realized_vol_30d": RANGE_SPLIT_VOL},
        "results": results,
    }
    with io.open(OUTPUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    counts = {}
    for record in results.values():
        for phase in record["assumed_market_regime"].split(";"):
            counts[phase or "(none)"] = counts.get(phase or "(none)", 0) + 1
    print("market_phase_hypothesis: %d rows" % len(results))
    for phase, count in sorted(counts.items(), key=lambda item: -item[1]):
        print("  %-16s %d" % (phase, count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
