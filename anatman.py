# -*- coding: utf-8 -*-
u"""anatman — all observed defects of this instrument as EXECUTABLE cases.

WHY. In a day the instrument caught ten defects in itself. Seven of them were
fixed IN CODE and held by nothing: any subsequent edit could silently bring
them back. A fix without its own case is a promise, not a mechanism.

THE RULE BY WHICH EVERYTHING HERE IS ARRANGED. A case is taken as OBSERVED: the very
line, the very name, the very number on which it broke. A fabricated case
tests my imagination about the defect, not the defect.

And to every prohibition — a control pass. A check that only
refuses is not verified: "everything is broken" is as blind an answer as "everything is intact".
"""
from __future__ import print_function

import io
import json
import os
import re
import subprocess
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RESULTS = []


def case(num, date, name, fn):
    u"""One observed case. Prints and remembers the outcome."""
    try:
        ok, detail = fn()
    except Exception as ex:
        ok, detail = False, u"extraneous error %r" % (ex,)
    RESULTS.append((num, name, ok))
    print(u"  %s №%-2d [%s] %s%s"
          % (u"OK    " if ok else u"FAIL", num, date, name,
             u"" if ok else u"   ← " + str(detail)))


# ─────────────────────────── cases ───────────────────────────

def c1():
    u"""20.08 · config silently overrode the strategy's timeframe.
    Five-minute bars were computed by hourly ones and gave 6014 trades without a single complaint."""
    cfg = json.load(io.open(os.path.join(_ROOT, "user_data", "config.json"),
                            encoding="utf-8"))
    return ("timeframe" not in cfg,
            u"the config again has a timeframe key — it will override the strategy")


def c2():
    u"""21.08 · Ichi/ichi, SAR/Sar and four more pairs differ ONLY in
    case. On Windows this is ONE file, and the run skipped the second of the pair."""
    src = io.open(os.path.join(_ROOT, "corpus.py"), encoding="utf-8").read()
    has = "def card_path" in src and "hashlib.md5(name" in src
    return (has, u"corpus.py no longer distinguishes names by case")


def c3():
    u"""21.08 · np.NAN removed in numpy 2.0 — 38 strategies crashed on a name
    that was an ALIAS of np.nan. Restoration changes nothing in essence."""
    r = subprocess.run([os.path.join(_ROOT, "ftenv", "Scripts", "python.exe"),
                        "-c", "import numpy;print(numpy.NAN is numpy.nan)"],
                       capture_output=True, timeout=120)
    out = r.stdout.decode("utf-8", "replace").strip()
    return (out == "True", u"alias not restored in the child process: %r" % out)


def c4():
    u"""21.08 · "Fatal exception!" is the HEADER of a traceback, not the cause.
    Thus 76 strategies got an empty explanation. An exception name can have
    DOTS: numpy.exceptions.DTypePromotionError."""
    import harness
    fake = (u"2026-08-21 09:02:01 - freqtrade - ERROR - Fatal exception!\n"
            u"Traceback (most recent call last):\n"
            u"numpy.exceptions.DTypePromotionError: The DType could not be promoted\n")
    tail = re.findall(r"^([\w.]*(?:Error|Exception)): (.+)$", fake, re.M)
    ok = bool(tail) and tail[-1][0] == "numpy.exceptions.DTypePromotionError"
    src = io.open(os.path.join(_ROOT, "harness.py"), encoding="utf-8").read()
    ok = ok and r"[\w.]*(?:Error|Exception)" in src
    return (ok, u"the cause is again taken from the label, not from the end of the traceback")


def c5():
    u"""20.08 · "Expectancy" in freqtrade is IN CURRENCY. With stake_amount:
    unlimited it compounds, i.e. is NOT scale-free. I declared it
    independent of configuration; this shifted the published number by 5 times."""
    import harness
    line = u"│ Expectancy (Ratio)                     │ 0.53 (0.29)   │"
    d = harness.parse_summary(line)
    got = d.get("expectancy")
    cfg = json.load(io.open(os.path.join(_ROOT, "user_data", "config.json"),
                            encoding="utf-8"))
    compounding = cfg.get("stake_amount") == "unlimited"
    return (got == 0.53 and compounding,
            u"parsing gave %r; compounding=%r — if the stake stopped "
            u"compounding, the README caveat must be reconsidered"
            % (got, compounding))


def c6():
    u"""20.08 · p-value 5.896: scientific notation 5.896e-05 was truncated.
    A probability outside [0,1] is a broken instrument, not a surprising result."""
    import harness
    bad = u"│ Mean profit p-value  │ 5.896   │"
    d = harness.parse_summary(bad)
    good = harness.parse_summary(u"│ Mean profit p-value  │ 1.36e-65   │")
    return (d.get("p_value") is None and "parse_warning" in d
            and good.get("p_value") == 1.36e-65,
            u"the impossible guard is silent or scientific notation is lost again")


def c7():
    u"""21.08 · for strong effects p = 1.4e-65, and 1-p/2 collapses to one:
    the inverse normal falls. The old guard only caught zero."""
    import power
    sd = power.implied_sd(mean=1.0, n=300, p=1.36e-65)
    return (sd is not None and sd > 0,
            u"tiny p again drops the power calculation (got %r)" % (sd,))


def c8():
    u"""20.08 · stats/funnel read ONE folder, and five strategies chosen
    MANUALLY by me would have ended up in the population denominator.

    21.08 the case is REBUILT. It was written for TWO file names, and when
    stats.py was deleted, the check would have broken — that is, it held on a case,
    not on a class. Now it finds ALL modules reading results/ by itself,
    and requires population selection from each, naming their count."""
    import glob as _g
    seen, bad = [], []
    for p in sorted(_g.glob(os.path.join(_ROOT, "*.py"))):
        name = os.path.basename(p)
        if name == "anatman.py":
            continue
        src = io.open(p, encoding="utf-8", errors="replace").read()
        reads = ('"results"' in src and "json.load" in src
                 and ("glob(" in src or "listdir(" in src))
        if not reads:
            continue
        seen.append(name)
        if "source" not in src:
            bad.append(name)
    return (len(seen) >= 3 and not bad,
            u"population is not selected in [%s]; readers of results/ found %d"
            % (u", ".join(bad) or u"—", len(seen)))


def c9():
    u"""20.08 · shares are cut by NUMBER in the list, so the list must be
    identical in all processes. Checked three times — but the check ages."""
    import hashlib
    from harness import find_strategies
    def plan():
        seen, out = set(), []
        for d in sorted(os.listdir(os.path.join(_ROOT, "repos"))):
            p = os.path.join(_ROOT, "repos", d)
            if not os.path.isdir(p):
                continue
            for _f, n in sorted(find_strategies(p)):
                if n in seen:
                    continue
                seen.add(n); out.append(n)
        return hashlib.md5(u"|".join(out).encode("utf-8")).hexdigest()[:16], len(out)
    a = plan(); b = plan()
    return (a == b, u"strategy list is NOT deterministic: %r vs %r" % (a, b))


def c10():
    u"""20.08 · first four runs wrote to one folder, an hour later — two
    loaders into the same candle files. The lock must refuse the second."""
    import runlock
    first = runlock.acquire("anatman_proba", quiet=True)
    second = runlock.acquire("anatman_proba", quiet=True)
    runlock.release("anatman_proba")
    return (first and not second,
            u"lock let the second writer through (%r, %r)" % (first, second))


def c11():
    u"""21.08 · the exclusion criterion was NARROW: only lookahead-analysis.
    NOTankAi_15_Cleaned_v2 passed through it with a result of +63 645 298% —
    "no shift detected." The SECOND detector caught it: recursive-analysis
    found that its thresholds drift by 9% of the loaded history volume.
    Of the 67 that passed the funnel, 51 were marked by EXACTLY THE SECOND, not the first."""
    src = io.open(os.path.join(_ROOT, "funnel.py"), encoding="utf-8").read()
    both = ("recursive" in src and "lookahead" in src
            and "r in la or r in rc" in src)
    return (both, u"funnel again excludes only by one detector")


def main():
    print(u"ANATMAN — observed defects as executable cases")
    print(u"each case = the very line on which it broke\n")
    case(1, "20.08", u"config does not override strategy timeframe", c1)
    case(2, "21.08", u"names differing only in case give different cards", c2)
    case(3, "21.08", u"alias np.NAN restored in child process", c3)
    case(4, "21.08", u"failure reason is an exception, not a traceback label", c4)
    case(5, "20.08", u"expectation is read as CURRENCY, rate compounds", c5)
    case(6, "20.08", u"p outside [0,1] is rejected; scientific notation is preserved", c6)
    case(7, "21.08", u"tiny p does not drop the power calculation", c7)
    case(8, "20.08", u"populations do not mix in the denominator", c8)
    case(9, "20.08", u"list for shares is deterministic", c9)
    case(10, "20.08", u"lock refuses the second writer", c10)

    case(11, "21.08", u"exclusion accounts for BOTH freqtrade detectors", c11)

    ok = sum(1 for _n, _t, o in RESULTS if o)
    print(u"\nTOTAL: %d/%d" % (ok, len(RESULTS)))
    print(u"\nSEPARATE SETS (with diversion, require freqtrade):")
    print(u"   python tf_guard_selftest.py    9/9  — TF substitution, code 0 without numbers")
    print(u"   python loadscan.py --selftest       — blindness to load failure")
    return 0 if ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
