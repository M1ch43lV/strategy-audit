# -*- coding: utf-8 -*-
"""loadprobe - can each never-measured strategy be imported now?

Measures the effect of the environment repairs: the packages installed into
ftenv, the extended module search path (modpath.py) and the API aliases
(compat_shim.py). No strategy file is modified anywhere in this pipeline.

Each import runs in its own process, for two reasons. An import with a side
effect must not take the whole run down, and same-named modules from different
repositories must not overwrite one another in sys.modules - which is the very
failure `--strategy-path` guards against in the audit harness.

Importing is NECESSARY BUT NOT SUFFICIENT. A strategy that imports cleanly can
still die inside populate_indicators on a pandas API change, and it still needs
candle data for its declared timeframe. "Loads" is therefore never reported as
"measurable".
"""
import csv
import io
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "repair"))
import modpath  # noqa: E402

AUD = ROOT
REPOS = os.path.join(AUD, "repos")
PY = os.path.join(AUD, "ftenv", "Scripts", "python.exe")

CHILD = r"""
import importlib.util, sys, json
p, extra = sys.argv[1], json.loads(sys.argv[2])
# APPEND, never prepend. Prepending let local files such as `technical.py` or
# `utils.py` shadow real packages and broke 12 strategies that had loaded fine
# before - the repair did damage. Installed packages win; local helpers stay
# reachable.
sys.path.extend(extra + [__import__("os").path.dirname(p)])
try:
    spec = importlib.util.spec_from_file_location("probe_mod", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print("__PROBE__OK")
except BaseException as e:
    print("__PROBE__%s: %s" % (type(e).__name__, str(e)[:150].replace("\n", " ")))
"""


def probe(row):
    f = os.path.join(AUD, row["file"])
    if not os.path.exists(f):
        return row["strategy"], "MISSING_FILE", []
    miss = modpath.imported_toplevel(f)
    dirs, _ = modpath.extra_syspath(f, REPOS, miss)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONWARNINGS="ignore")
    try:
        r = subprocess.run([PY, "-c", CHILD, f, json.dumps(dirs)],
                           capture_output=True, timeout=120, env=env)
        out = (r.stdout + r.stderr).decode("utf-8", "replace")
        # Match on an explicit marker, not on "the last line". TensorFlow and
        # absl write to stderr AFTER the probe has printed its verdict, and
        # taking the last line silently reported those log lines as the result.
        hits = [l.split("__PROBE__", 1)[1].strip()
                for l in out.splitlines() if "__PROBE__" in l]
        return row["strategy"], (hits[-1] if hits else "NO_OUTPUT"), dirs
    except subprocess.TimeoutExpired:
        return row["strategy"], "TIMEOUT", dirs


def main():
    led = os.path.join(AUD, "LEDGER.csv") if len(sys.argv) < 2 else sys.argv[1]
    rows = [r for r in csv.DictReader(io.open(led, encoding="utf-8"))
            if r["dropped_at"] == "G0_measured"]
    print("probing %d strategies with %s" % (len(rows), PY), flush=True)
    out = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, (name, res, dirs) in enumerate(ex.map(probe, rows), 1):
            out.append({"strategy": name, "result": res,
                        "extra_syspath": [os.path.relpath(d, AUD) for d in dirs]})
            if i % 50 == 0:
                print("  %d/%d" % (i, len(rows)), flush=True)
    dst = os.path.join(ROOT, "repair", "loadprobe.json")
    io.open(dst, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    ok = sum(1 for x in out if x["result"] == "OK")
    print("\nimporting now: %d of %d (%.1f%%)" % (ok, len(out), 100.0 * ok / len(out)))
    print("written: %s" % dst)


if __name__ == "__main__":
    main()
