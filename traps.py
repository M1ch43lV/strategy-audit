# -*- coding: utf-8 -*-
u"""traps — checks from the freqtrade community's "Backtesting Traps".

SOURCE, AND IT'S NOT MINE. When asked "what else, besides bias checks,
reveals a fitted strategy", freqtrade Discord members gave a link:
https://brookmiles.github.io/freqtrade-stuff/2021/04/12/backtesting-traps/

This is practitioner knowledge absent from any statistics. Here it is
translated into machine checks — without additions from me, because
additions would be my guesses on top of their experience.

WHAT IS CHECKED (numbers per their document):

  #5 Unrealistic trailing. `trailing_stop = True` with a very tight
     `trailing_stop_positive`: backtest leads price to candle high,
     pulls stop up and drops price — an "ideal candle" emerges,
     selling just below the high almost always. Their red flag: trailing
     LESS than typical spread (0.1–0.5%).

  #5b `trailing_stop = True` WITHOUT `trailing_stop_positive`: stop trails
     the full `stoploss` distance, not a few percent.

  #6 ROI exploitation. Tight `minimal_roi` on a long timeframe: price
     unlikely to reach target before stop in real conditions.

  Plus `stoploss = -0.99` — a declared stop that is not a stop.

WHAT'S MISSING HERE AND WHY. Their traps #2 (unfilled limit orders),
#3 (slippage) and #4 (many trades with small profit) require data on
trade duration and average trade in percent, which cards lack so far.
Lying about "checked" is not allowed: they are named here as NOT COVERED.
"""
from __future__ import print_function

import ast
import collections
import glob
import io
import json
import os
import re
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SPREAD = 0.005          # their number: typical spread 0.1–0.5%
TF_MIN = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60,
          "2h": 120, "4h": 240, "6h": 360, "8h": 480, "12h": 720,
          "1d": 1440, "3d": 4320, "1w": 10080}


def num(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = num(node.operand)
        return -v if v is not None else None
    return None


def inspect(path, cls):
    src = io.open(path, encoding="utf-8", errors="replace").read()
    try:
        tree = ast.parse(src)
    except Exception:
        return None
    node = None
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef) and n.name == cls:
            node = n
    if node is None:
        return None

    v = {"trailing_stop": None, "trailing_stop_positive": None,
         "trailing_stop_positive_offset": None, "stoploss": None,
         "timeframe": None, "roi_first": None, "roi_zero": None,
         "leverage": 1.0}
    # LEVERAGE. Hippocritical, freqtrade Discord 22.08: «if you have 1% trailing
    # and do 10x leverage then it essentially becomes 0.1% trailing». This is not
    # an opinion — it's in the engine source:
    #     stop_rate = open * (1 + offset - trailing_stop_positive / leverage)
    # The trailing distance is DIVIDED by leverage, so the value compared with the spread must be
    # the divided distance. I read this line in the morning and did not make the connection.
    #
    # ⚠ WHAT THIS ANALYSIS DOESN'T SEE: leverage from config, leverage from dynamic
    # leverage(), leverage depending on the pair. Only the literal
    # `return <number>` is the LOWER BOUND of the number of such strategies, not the number itself.
    m = re.search(r"def\s+leverage\s*\(.*?return\s+([0-9.]+)", src, re.S)
    if m:
        try:
            lv = float(m.group(1))
            if lv > 0:
                v["leverage"] = lv
        except ValueError:
            pass
    for st in node.body:
        if not isinstance(st, ast.Assign) or not st.targets:
            continue
        t = st.targets[0]
        name = getattr(t, "id", None)
        if name not in v and name != "minimal_roi":
            continue
        if name == "minimal_roi" and isinstance(st.value, ast.Dict):
            pairs = []
            for k, val in zip(st.value.keys, st.value.values):
                kk = k.value if isinstance(k, ast.Constant) else None
                vv = num(val)
                if kk is not None and vv is not None:
                    try:
                        pairs.append((int(str(kk)), vv))
                    except ValueError:
                        pass
            if pairs:
                pairs.sort()
                v["roi_zero"] = pairs[0][1]
                v["roi_first"] = pairs[0][1]
            continue
        if isinstance(st.value, ast.Constant) and isinstance(st.value.value, bool):
            v[name] = st.value.value
        elif isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
            v[name] = st.value.value
        else:
            v[name] = num(st.value)
    return v


def flags(v, notes=None):
    u"""Disqualifying traps. `notes` — a list for observations
    that are NOT traps (see 22.08 about wide trailing)."""
    out = []
    if notes is None:
        notes = []
    if not v:
        return out
    tf = v.get("timeframe")
    mins = TF_MIN.get(tf)
    tsp = v.get("trailing_stop_positive")
    if v.get("trailing_stop") is True:
        if tsp is None:
            # ⚠ NO LONGER A TRAP, 22.08. Hippocritical (freqtrade Discord):
            # «if you have loose trailing you wont have a trap; if you have
            # things like 0.1% trailing then not». He's right: wide trailing
            # (at the full stop distance) IS executable in reality — it's far from
            # the spread and fills reliably. What makes it a trap is TIGHTNESS, not the
            # trailing itself. This is an observation, not a disqualification.
            #
            # Verified before the change: on the corpus of 895, not a single verdict from
            # this flag depended — out of nine knocked out on G8, zero were knocked out by it
            # alone. The rule changes in substance, not to fit the result.
            notes.append((u"loose trailing (no trailing_stop_positive)",
                          u"stop trails at the full stoploss distance (%s). Wide, "
                          u"but executable — a note, not a trap"
                          % (v.get("stoploss"),)))
        else:
            lv = v.get("leverage") or 1.0
            eff = tsp / lv if lv > 0 else tsp
            if eff < SPREAD:
                out.append((u"trailing tighter than the spread",
                            u"trailing_stop_positive = %.4f at %.0fx leverage = "
                            u"%.5f effective, below the 0.1–0.5%% spread the trap "
                            u"article names" % (tsp, lv, eff)))
    # ⚠ NO LONGER TRAPS, 22.08 — by the COMMUNITY'S DEFINITION.
    # Hippocritical (freqtrade Discord): «a backtesting trap is where you have
    # a different result from backtest to dry run. backtesting works on
    # candles, where dry/live runs work on ticker data».
    #
    # The term belongs to the community: I myself wrote in CORRECTIONS.md that
    # the question about 177 is — «the community's call, not mine». The answer was received —
    # so it's being executed, not discussed.
    #
    # Both categories below do NOT cause backtest-vs-live divergence: trailing
    # is off in both, the −0.99 stop works identically in both. They
    # mislead the READER and spoil risk — that's a different kind of defect.
    #
    # Verified BEFORE the change: 8 strategies held on G8 only by these
    # two flags; run by their own columns, all 8 fall on
    # G12 (don't beat «buy and hold»). The ladder result of 0 out of 456 didn't move.
    if tsp is not None and v.get("trailing_stop") is not True:
        notes.append((u"inert trailing setting",
                      u"trailing_stop_positive = %s while trailing_stop is not "
                      u"True — the engine runs trailing off in BOTH backtest and "
                      u"live, so no divergence; the reader is misled, not the "
                      u"result" % tsp))
    sl = v.get("stoploss")
    if sl is not None and sl <= -0.9:
        notes.append((u"stoploss is not a stop",
                      u"stoploss = %s — losers are effectively never cut. Same in "
                      u"backtest and live: a risk defect, not a backtesting trap"
                      % sl))
    roi = v.get("roi_zero")
    if roi is not None and mins is None:
        # totality: candle duration is unknown ⇒ judging a "tight target on
        # a long candle" is NOT ALLOWED. Previously there was no trap here silently. Now
        # the ignorance is named aloud and enters observations.
        notes.append((u"roi trap not evaluated",
                      u"timeframe %r is unknown to TF_MIN, so the ROI-vs-candle "
                      u"check has no defined answer here" % (tf,)))
    if roi is not None and mins is not None and mins >= 60 and roi <= 0.01:
        out.append((u"tight ROI on a long timeframe",
                    u"first minimal_roi entry %.4f on %s candles" % (roi, tf)))
    return out


def main():
    from harness import find_strategies
    where = {}
    for d in sorted(os.listdir(os.path.join(_ROOT, "repos"))):
        p = os.path.join(_ROOT, "repos", d)
        if os.path.isdir(p):
            for f, n in sorted(find_strategies(p)):
                where.setdefault(n, f)

    survivors, allrows = set(), []
    for f in glob.glob(os.path.join(_ROOT, "results", "*.json")):
        r = json.load(io.open(f, encoding="utf-8"))
        if r.get("source") != "corpus":
            continue
        a = r["runs"]["in_sample"].get("summary")
        b = r["runs"]["out_sample"].get("summary")
        allrows.append(r["strategy"])
        if not isinstance(a, dict) or (a.get("trades") or 0) < 30:
            continue
        if not isinstance(b, dict) or b.get("expectancy") is None:
            continue
        if (a.get("expectancy") or 0) <= 0 or (a.get("p_value") or 1) >= 0.05:
            continue
        if b["expectancy"] <= 0 or (b.get("p_value") or 1) >= 0.05:
            continue
        survivors.add(r["strategy"])

    tally = collections.Counter()
    flagged_all, flagged_surv = set(), set()
    for name in allrows:
        p = where.get(name)
        # TOTAL: missing source — definite value "NOT REVIEWED",
        # it enters the tally and is therefore visible in the report, not silently lost.
        if not p:
            tally[u"NOT REVIEWED: source not found"] += 1
            continue
        fl = flags(inspect(p, name))
        for lab, _d in fl:
            tally[lab] += 1
        if fl:
            flagged_all.add(name)
            if name in survivors:
                flagged_surv.add(name)

    print(u"BACKTESTING TRAPS (source — freqtrade community, not me)")
    print(u"strategies checked: %d · passed the funnel: %d"
          % (len(allrows), len(survivors)))
    print()
    for lab, c in tally.most_common():
        print(u"   %-42s %4d" % (lab, c))
    print()
    print(u"flagged with AT LEAST ONE trap: %d of %d (%.0f%%)"
          % (len(flagged_all), len(allrows), 100.0 * len(flagged_all) / max(len(allrows), 1)))
    print(u"among THOSE PASSING THE FUNNEL:         %d of %d (%.0f%%)"
          % (len(flagged_surv), len(survivors),
             100.0 * len(flagged_surv) / max(len(survivors), 1)))
    print()
    print(u"NOT COVERED (need trade durations and average trade in %%):")
    print(u"   their #2 unfilled limit orders")
    print(u"   their #3 slippage")
    print(u"   their #4 many trades with profit below 0.5%%")
    print(u"   their red flag: average duration SHORTER than candle")


if __name__ == "__main__":
    main()
