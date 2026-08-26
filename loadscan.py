# -*- coding: utf-8 -*-
u"""loadscan — how much corpus is actually LOADED before spending hours.

freqtrade itself prints the Status column in `list-strategies`. It is cheaper to ask
it than to find out after a five-hour run that a third of the corpus does not import.
«Failed to load» is a category for the report, not silence.

⚠ THE FIRST VERSION OF THIS CHECK WAS BLIND. Parsing the line required the STRATEGY
NAME, and freqtrade prints «--» in that column for a failed load.
A failure could NEVER be counted, and the check reported «failed to load
0» for a corpus it had not seen. Caught by sabotage, not reasoning.
We identify the line by FILE — it is always present; the name is absent on failure.
"""
from __future__ import print_function
import io, os, re, subprocess, sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FT = os.path.join(_ROOT, "ftenv", "Scripts", "freqtrade.exe")
CFG = os.path.join(_ROOT, "user_data", "config.json")
REPOS = os.path.join(_ROOT, "repos")

env = dict(os.environ)
env["PYTHONIOENCODING"] = "utf-8"
ROWS = re.compile(r"│\s*(\S+)\s*│\s*(\S+\.py)\s*│\s*(OK|LOAD FAILED)\s*│")

BROKEN = u'''from freqtrade.strategy import IStrategy
import this_module_does_not_exist_xyz
class BrokenOnPurpose(IStrategy):
    timeframe = '1h'
    stoploss = -0.10
    def populate_indicators(self, d, m): return d
    def populate_entry_trend(self, d, m): return d
    def populate_exit_trend(self, d, m): return d
'''


def scan(path):
    try:
        r = subprocess.run([FT, "list-strategies", "--strategy-path", path,
                            "--config", CFG], capture_output=True, timeout=300, env=env)
    except Exception:
        return []
    return ROWS.findall((r.stdout + r.stderr).decode("utf-8", "replace"))


def selftest():
    u"""The check MUST be ABLE to see a failure — otherwise «0 failures» is a property
    of the instrument, not the corpus. A deliberately unbuildable strategy is planted and
    required to be counted; and at the same time, intact ones nearby are required to be
    counted as intact — «everything is broken» is as blind an answer as «everything is fine».
    """
    d = os.path.join(_ROOT, "_sabotage")
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "BrokenOnPurpose.py"), "w", encoding="utf-8").write(BROKEN)
    rows = scan(d)
    failed = [x for x in rows if x[2] == "LOAD FAILED"]
    okrows = [x for x in rows if x[2] == "OK"]
    good = len(failed) == 1 and failed[0][1] == "BrokenOnPurpose.py"
    print(u"  %s sabotage counted as failure (%d)" % (u"OK" if good else u"FAIL", len(failed)))
    print(u"  %s intact ones nearby counted as intact (%d)"
          % (u"OK" if okrows else u"FAIL", len(okrows)))
    return 0 if (good and okrows) else 1


def main():
    seen = {}
    for d in sorted(os.listdir(REPOS)):
        p = os.path.join(REPOS, d)
        if not os.path.isdir(p):
            continue
        # TOTAL: diagnostic walk, not part of the verdict
    for sub, dirs, _ in os.walk(p):
            dirs[:] = [x for x in dirs if x not in (".git", "__pycache__", "venv")]
            for name, loc, st in scan(sub):
                # key — file in its own repository: os.walk enters both
                # the parent and the child, so without a key duplicates will appear
                seen.setdefault((d, loc), st)
    ok = sum(1 for v in seen.values() if v == "OK")
    bad = sum(1 for v in seen.values() if v != "OK")
    print(u"FILES WITH STRATEGIES: %d · loaded %d · FAILED TO LOAD %d (%.1f%%)"
          % (len(seen), ok, bad, 100.0 * bad / max(1, len(seen))))
    badf = sorted(k[1] for k, v in seen.items() if v != "OK")
    if badf:
        print(u"examples of unloadable: %s" % u", ".join(badf[:10]))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print(u"loadscan — self-check by sabotage")
        raise SystemExit(selftest())
    main()
