# -*- coding: utf-8 -*-
u"""dof — strategy degrees of freedom and a CHECK of whether they predict anything.

REASON. `froggleston` in the freqtrade Discord: "bias checks aren't the only thing
that points to strategies that are gamed". He's right. The native detectors catch
lookahead and indicator recursion, but don't catch overfitting via PARAMETER
SWEEPING: fifty-five "clean" strategies can be fifty-five
sweep variants on the same noise.

WHAT IS DELIBERATELY ABSENT HERE. I was offered a ready-made gate: DoF/sqrt(N) > 0.5 —
red flag, > 1.0 — fails. The threshold is made up, and declaring it a gate
would mean doing exactly what this repository criticizes others for: calling a number
pulled from thin air a rule.

So here the VALUE IS CALCULATED and it's checked whether it's related to out-of-sample
degradation. If there's no relation — the proposal isn't confirmed, and that's exactly what
will be written. A threshold, if it appears, will be derived from the data.

WHAT IS CALCULATED. Only what's visible in the code without running it:
  * declared freqtrade hyperparameters (IntParameter and kin) and the SIZE
    of their search space, when bounds are given as numbers
  * branches in entry and exit logic
  * various indicator window lengths (timeperiod=, window=, length=)
This is NOT full degrees of freedom: the author could have swept manually and left no
traces. So the value is a lower bound, and that's how it's named.
"""
from __future__ import print_function

import ast
import collections
import glob
import io
import json
import math
import os
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PARAMS = ("IntParameter", "DecimalParameter", "RealParameter",
          "CategoricalParameter", "BooleanParameter")
LOOKBACK_KW = ("timeperiod", "window", "length", "period", "lookback")


def const(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = const(node.operand)
        return -v if v is not None else None
    return None


def space_size(call):
    u"""How many values are swept for one declared parameter."""
    name = getattr(call.func, "id", None) or getattr(call.func, "attr", "")
    if name == "BooleanParameter":
        return 2
    if name == "CategoricalParameter":
        for a in call.args:
            if isinstance(a, (ast.List, ast.Tuple)):
                return max(len(a.elts), 1)
        return 2
    lo = const(call.args[0]) if len(call.args) > 0 else None
    hi = const(call.args[1]) if len(call.args) > 1 else None
    if lo is None or hi is None or hi <= lo:
        return 2
    if name == "IntParameter":
        return int(hi - lo) + 1
    dec = 3
    for kw in call.keywords:
        if kw.arg == "decimals":
            d = const(kw.value)
            if d is not None:
                dec = int(d)
    return max(int((hi - lo) * (10 ** dec)) + 1, 2)


def measure(path, cls):
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

    n_par, log_space = 0, 0.0
    branches, lookbacks = 0, set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            nm = getattr(n.func, "id", None) or getattr(n.func, "attr", "")
            if nm in PARAMS:
                n_par += 1
                log_space += math.log10(max(space_size(n), 2))
            for kw in n.keywords:
                if kw.arg in LOOKBACK_KW:
                    v = const(kw.value)
                    if v is not None:
                        lookbacks.add(v)
        elif isinstance(n, ast.If):
            branches += 1
        elif isinstance(n, ast.BoolOp):
            branches += max(len(n.values) - 1, 0)
    return {"params": n_par, "log10_space": round(log_space, 2),
            "branches": branches, "lookbacks": len(lookbacks),
            "dof": n_par + branches + len(lookbacks)}


def main():
    from harness import find_strategies
    where = {}
    for d in sorted(os.listdir(os.path.join(_ROOT, "repos"))):
        p = os.path.join(_ROOT, "repos", d)
        if os.path.isdir(p):
            for f, n in sorted(find_strategies(p)):
                where.setdefault(n, f)

    rows = []
    for f in glob.glob(os.path.join(_ROOT, "results", "*.json")):
        r = json.load(io.open(f, encoding="utf-8"))
        if r.get("source") != "corpus":
            continue
        a = r["runs"]["in_sample"].get("summary")
        b = r["runs"]["out_sample"].get("summary")
        if not isinstance(a, dict) or a.get("trades") is None:
            continue
        # `where` is built by a full traversal of repos/ BEFORE this loop, so
        # a missing key is a definite answer "the strategy file in the corpus
        # no», not «I don't know». The semantics are declared, the check is in place:
        # you cannot carry it into a variable — that hides it from totality.py.
        m = measure(where.get(r["strategy"], ""), r["strategy"]) if where.get(r["strategy"]) else None  # TOTAL: full traversal of repos/
        if not m:
            continue
        e1 = a.get("expectancy")
        e2 = b.get("expectancy") if isinstance(b, dict) else None
        rows.append((r["strategy"], m, a.get("trades"), e1, e2))

    print(u"strategies with measured degrees of freedom: %d" % len(rows))
    par = [r for r in rows if r[1]["params"] > 0]
    print(u"declare freqtrade hyperparameters: %d (%.0f%%)"
          % (len(par), 100.0 * len(par) / max(len(rows), 1)))
    if par:
        sp = sorted(x[1]["log10_space"] for x in par)
        print(u"search size, order of 10^: median %.1f · max %.1f"
              % (sp[len(sp) // 2], sp[-1]))
        top = sorted(par, key=lambda x: -x[1]["log10_space"])[:5]
        for n, m, t, e1, e2 in top:
            print(u"   %-30s parameters %3d · search 10^%.1f · trades %s"
                  % (n[:30], m["params"], m["log10_space"], t))

    # DOES IT PREDICT? comparison of out-of-sample retention for high and low DoF
    keep = [(r[1]["dof"], r[3], r[4], r[2]) for r in rows
            if r[3] is not None and r[4] is not None and r[3] > 0]
    keep = [(d, e2 / e1, n) for d, e1, e2, n in keep]
    if len(keep) >= 20:
        keep.sort()
        half = len(keep) // 2
        lo = [k for _d, k, _n in keep[:half]]
        hi = [k for _d, k, _n in keep[half:]]
        med = lambda v: sorted(v)[len(v) // 2]
        print()
        print(u"RELATION TO OUT-OF-SAMPLE ROBUSTNESS (fraction of retained expectation):")
        print(u"   low DoF (median %d): retained %.2f  n=%d"
              % (med([d for d, _k, _n in keep[:half]]), med(lo), len(lo)))
        print(u"   high DoF (median %d): retained %.2f  n=%d"
              % (med([d for d, _k, _n in keep[half:]]), med(hi), len(hi)))
        print(u"   median difference: %+.2f" % (med(hi) - med(lo)))
        print()
        print(u"⚠ This is an OBSERVATION, not a gate. No threshold is introduced until the relation is")
        print(u"   proven on a pre-declared check.")
    else:
        print(u"\ntoo few data to check the relation (%d) — no conclusion" % len(keep))


if __name__ == "__main__":
    main()
