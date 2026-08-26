# -*- coding: utf-8 -*-
u"""Self-check of the item guard — by SABOTAGE, not by reasoning.

Defect 20.08: the `timeframe` key in the config OVERRODE the timeframe declared
by the strategy. Five-minute bars were calculated on hourly ones and produced plausible numbers.
The key was removed — but that fixes the CASE. Here it is verified that the CLASS is fixed:
the guard must catch the substitution even if the key is returned.

M-17: the control must SEE both failure and norm. A guard that always
fails checks nothing.
"""
from __future__ import print_function
import os as _os
_ROOT = _os.environ.get("AUDIT_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
import io, json, os, sys

sys.path.insert(0, _ROOT)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import harness
_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))

REAL = harness.CFG
SAB = _os.path.join(_ROOT, "user_data/_config_sabotage.json")
S5M = _os.path.join(_ROOT, "repos/davidzr_freqtrade-strategies/strategies/ASDTSRockwellTrading/ASDTSRockwellTrading.py")
S1H = _os.path.join(_ROOT, "user_data/strategies/MACDCrossoverWithTrend.py")
RANGE = "20190101-20190301"

ok = fail = 0


def case(n, cond, detail=u""):
    global ok, fail
    if cond:
        ok += 1
        print(u"  ✓ %s" % n)
    else:
        fail += 1
        print(u"  ✗ %s   %s" % (n, detail))


print(u"ITEM GUARD — self-check by sabotage\n")

# ── #1: THE DEFECT ITSELF, verbatim. Config imposes 1h on a five-minute strategy.
cfg = json.load(io.open(REAL, encoding="utf-8"))
cfg["timeframe"] = "1h"
io.open(SAB, "w", encoding="utf-8").write(json.dumps(cfg, ensure_ascii=False, indent=2))
harness.CFG = SAB
src5 = io.open(S5M, encoding="utf-8", errors="replace").read()
tf5 = harness.declared_tf(src5)
case(u"#0 strategy declares 5m", tf5 == "5m", u"declared %r" % tf5)
lvl, why, s = harness.backtest("ASDTSRockwellTrading", RANGE, path=S5M, want_tf=tf5)
case(u"#1 timeframe substitution REJECTED", lvl == harness.NA, u"returned %s / %s" % (lvl, why))
case(u"#2 reason named concretely", u"ITEM NOT THE SAME" in (why or u""), why)
case(u"#3 number NOT given outside", s is None, u"given %r" % (s,))
print(u"     engine said: %s" % why)

# ── #4-6: CONTROL. The same guard must PASS an honest run.
harness.CFG = REAL
src1 = io.open(S1H, encoding="utf-8", errors="replace").read()
tf1 = harness.declared_tf(src1)
lvl2, why2, s2 = harness.backtest("MACDCrossoverWithTrend", RANGE,
                                  path=None, want_tf=tf1)
case(u"#4 honest run SKIPPED", lvl2 == harness.PASS, u"%s / %s" % (lvl2, why2))
case(u"#5 engine timeframe written to the card",
     bool(s2) and s2.get("used_timeframe") == tf1,
     u"%r" % (s2.get("used_timeframe") if s2 else None))
case(u"#6 skipped pairs listed by field",
     bool(s2) and isinstance(s2.get("missing_pairs"), list),
     u"%r" % (s2.get("missing_pairs") if s2 else None))
if s2:
    print(u"     read on %s, pairs without history: %s"
          % (s2.get("used_timeframe"), s2.get("missing_pairs") or u"none"))

# ?? #7-8: CODE 0 IS NOT A RESULT. freqtrade exits WITH ZERO on a
# configuration error. Observed case: ClucCrypROI without `stoploss` gave a card
# of all None, marked as a SUCCESSFUL run.
S_ERR = os.path.join(_ROOT, "repos", "PeetCrypto_freqtrade-stuff", "ClucCrypROI.py")
if os.path.exists(S_ERR):
    lvl3, why3, s3 = harness.backtest("ClucCrypROI", RANGE, path=S_ERR, want_tf=None)
    case(u"#7 code 0 without numbers is NOT considered a run",
         lvl3 == harness.NA and s3 is None, u"%s / %r" % (lvl3, s3))
    case(u"#8 reason taken from the engine's ERROR",
         u"stoploss" in (why3 or u""), why3)
    print(u"     engine said: %s" % why3)
else:
    case(u"#7-8 ClucCrypROI case is available", False, S_ERR)

try:
    os.remove(SAB)
except Exception:
    pass
print(u"\nTOTAL: %d/%d" % (ok, ok + fail))
sys.exit(1 if fail else 0)
