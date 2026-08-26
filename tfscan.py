# -*- coding: utf-8 -*-
u"""tfscan — which timeframes the corpus strategies declare.

WHY. I run the entire corpus on hourly candles because I only downloaded those.
A strategy declaring `timeframe = '5m'` will either not run on this data,
or — worse — run on the wrong one. The latter would produce numbers that look
like a result. This must be KNOWN before publication, not after.
"""
import collections
import os as _os
_ROOT = _os.environ.get("AUDIT_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
import io
import os
import re
import sys

sys.path.insert(0, _ROOT)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from harness import find_strategies

RX = re.compile(r"""^\s*timeframe\s*[:=]\s*['"]([^'"]+)['"]""", re.M)

tf = collections.Counter()
seen = set()
for d in sorted(os.listdir(_os.path.join(_ROOT, "repos"))):
    p = os.path.join(_os.path.join(_ROOT, "repos"), d)
    if not os.path.isdir(p):
        continue
    for f, n in find_strategies(p):
        if n in seen:
            continue
        seen.add(n)
        src = io.open(f, encoding="utf-8", errors="replace").read()
        m = RX.search(src)
        tf[m.group(1) if m else u"NOT DECLARED"] += 1

print(u"TIMEFRAMES (unique strategies %d):" % len(seen))
for k, v in tf.most_common(12):
    mark = u"  ← data available" if k == "1h" else u""
    print(u"   %-14s %4d%s" % (k, v, mark))
h1 = tf.get("1h", 0)
print()
print(u"On hourly data, %d of %d are valid (%.0f%%)."
      % (h1, len(seen), 100.0 * h1 / max(1, len(seen))))
print(u"The rest need their OWN candles, otherwise the run is meaningless.")
