# -*- coding: utf-8 -*-
"""classify - turn raw features into labels for regime analysis.

Every rule in this file is an INTERPRETATION and therefore arguable; the
features in features.py are not. Each label is emitted together with the reason
that produced it (`why`), so a wrong classification can be refuted on the
individual case instead of only showing up as noise in the aggregate.

Five independent axes rather than one bucket. A strategy is not "mean reversion
OR short-capable", it is both at once - and for the question "which market
phase" the combination is what matters. Collapsing the axes would hide exactly
the interaction being studied.
"""
import csv
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import extract  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT

SCALP = {"1m", "3m", "5m"}
INTRADAY = {"15m", "30m", "1h", "2h"}
SWING = {"4h", "6h", "8h", "12h"}
POSITION = {"1d", "3d", "1w"}


def axis_direction(profile):
    direction = profile.get("direction_capability", "unknown")
    return direction, "canonical direction_capability after applying can_short"


def axis_speed(f):
    tf = f["timeframe"]
    if tf in SCALP:
        return "scalp", tf
    if tf in INTRADAY:
        return "intraday", tf
    if tf in SWING:
        return "swing", tf
    if tf in POSITION:
        return "position", tf
    return "unknown", str(tf)


def axis_logic(f):
    """Trading logic. The order is deliberate: FreqAI and portfolio strategies
    take precedence because there the indicators are merely model features and
    say nothing about the trading logic itself."""
    if f["freqai"]:
        return "ml_freqai", "uses the FreqAI interface"
    osc, tr, mom, vol = (f["n_oscillator"], f["n_trend"],
                         f["n_momentum"], f["n_volatility"])
    if osc == tr == mom == vol == 0:
        return "unclear", "no recognised indicator found"
    # Breakout: channel/volatility indicators dominate and entries are crossings
    if vol >= 2 and vol >= tr and f["uses_crossover"]:
        return "breakout", "channel indicators (%d) plus crossover entries" % vol
    if osc > tr + mom:
        return "mean_reversion", "oscillators (%d) outweigh trend+momentum (%d)" % (osc, tr + mom)
    if tr > osc and tr >= mom:
        return "trend_following", "trend indicators (%d) outweigh oscillators (%d)" % (tr, osc)
    if mom > 0 and mom >= tr:
        return "momentum", "momentum indicators (%d) lead" % mom
    if vol > 0:
        return "volatility", "volatility indicators only (%d)" % vol
    return "hybrid", "osc=%d trend=%d mom=%d vol=%d" % (osc, tr, mom, vol)


def axis_exit(f):
    parts = []
    if f["custom_exit"] or f["custom_stoploss"]:
        parts.append("custom")
    if f["trailing_stop"]:
        parts.append("trailing")
    if f["has_roi_table"]:
        parts.append("roi")
    return ("+".join(parts) if parts else "signal_only",
            "custom_exit=%s trailing=%s roi=%s" % (f["custom_exit"], f["trailing_stop"], f["has_roi_table"]))


def axis_complexity(f):
    score = (f["loc"] > 400) + (f["loc"] > 1200) + \
            (len(f["indicators"]) > 8) + f["hyperopt_params"] + \
            f["informative"] + f["position_adjust"]
    return (["simple", "simple", "moderate", "moderate", "complex", "complex", "complex"][min(score, 6)],
            "loc=%d indicators=%d hyperopt=%s informative=%s dca=%s"
            % (f["loc"], len(f["indicators"]), f["hyperopt_params"],
               f["informative"], f["position_adjust"]))


def regime_hypothesis(direction, logic):
    """Which market phase this pattern should theoretically favour.

    This is the testable prediction, not the result. It is precisely the split
    the original audit does not make: averaging across all phases lets
    opposing patterns cancel each other out, and a strategy built for falling
    markets is then scored mostly on a rising one.
    """
    if direction in ("short_only", "long_short"):
        return "bear+range"
    return {
        "trend_following": "bull",
        "momentum": "bull",
        "breakout": "transition+high_vol",
        "mean_reversion": "range",
        "volatility": "high_vol",
        "ml_freqai": "undetermined",
        "unclear": "undetermined",
        "hybrid": "undetermined",
    }.get(logic, "undetermined")


def main():
    manifest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AUD, "EXECUTION_PROFILES.csv")
    rows = list(csv.DictReader(io.open(manifest, encoding="utf-8-sig")))
    eligibility_path = os.path.join(AUD, "REGIME_ELIGIBILITY.csv")
    eligibility = ({r["strategy_id"]: r for r in csv.DictReader(
        io.open(eligibility_path, encoding="utf-8-sig"))}
        if os.path.exists(eligibility_path) else {})
    out, failed = [], 0
    for r in rows:
        p = os.path.join(AUD, r["canonical_file"])
        if not os.path.exists(p):
            failed += 1
            continue
        try:
            f = extract(p)
        except Exception:
            failed += 1
            continue
        d, dw = axis_direction(r)
        s, sw = axis_speed(f)
        lg, lw = axis_logic(f)
        ex, ew = axis_exit(f)
        cx, cw = axis_complexity(f)
        out.append({
            "strategy": r["strategy_id"], "repo": r["repo"],
            "implementation_id": r["implementation_id"],
            "run_profile": r["run_profile"],
            "provenance": r["canonical_population"],
            "repair_class": r["repair_class"],
            "measured": r["canonical_measured"] == "true",
            "eligibility_status": eligibility.get(r["strategy_id"], {}).get(
                "eligibility_status", "not_built"),
            "direction": d, "speed": s, "logic": lg,
            "exit_style": ex, "complexity": cx,
            "dca": f["position_adjust"], "informative": f["informative"],
            "timeframe": f["timeframe"], "stoploss": f["stoploss"],
            "indicators": f["indicators"],
            "regime_hypothesis": regime_hypothesis(d, lg),
            "why": {"direction": dw, "speed": sw, "logic": lw,
                    "exit": ew, "complexity": cw},
        })
    dst = os.path.join(ROOT, "cluster", "clusters.json")
    io.open(dst, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("classified: %d | file missing or unreadable: %d" % (len(out), failed))
    print("written: %s" % dst)


if __name__ == "__main__":
    main()
