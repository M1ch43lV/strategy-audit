# -*- coding: utf-8 -*-
"""run_class1 - measure every strategy that Class 1 repairs made runnable.

Population: strategies the audit dropped at G0_measured that now (a) import and
(b) have candle data for the timeframe they declare. Strategies without a
declared timeframe are excluded rather than guessed - inventing one would be a
decision about the strategy, not a repair of the environment.

Each strategy runs in its own process via measure_one.py, which calls the
audit's own `harness.audit_one`. Per-process isolation is required because
PYTHONPATH differs per strategy and because a strategy that hangs or crashes the
interpreter must not take the batch with it.

Cards land in repair/results_class1/ and carry source="class1_rerun". They are
never written into the audit's own results/ directory: the original run and this
one have to stay comparable, which they cannot be if one overwrites the other.
"""
import csv
import glob
import io
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT
REPOS = os.path.join(AUD, "repos")
PY = os.path.join(AUD, "ftenv", "Scripts", "python.exe")
OUT_DIR = os.path.join(ROOT, "repair", "results_class1")

sys.path.insert(0, os.path.join(ROOT, "repair"))
import modpath  # noqa: E402

RX_TF = re.compile(r"""^\s*timeframe\s*[:=]\s*['"]([^'"]+)['"]""", re.M)

# `audit_one` makes FOUR freqtrade calls (in-sample, out-of-sample, lookahead,
# recursive). An outer limit equal to the inner one therefore kills strategies
# mid-work and leaves no card at all - which is what happened to 24 of them,
# and it was our clock, not theirs. The outer budget must exceed the sum.
CALL_TIMEOUT = int(os.environ.get("FT_CALL_TIMEOUT", "1800"))
OUTER_TIMEOUT = int(os.environ.get("MEASURE_TIMEOUT", str(CALL_TIMEOUT * 4 + 600)))


def have_timeframes():
    out = set()
    for f in glob.glob(os.path.join(AUD, "user_data", "data", "binance", "*.feather")):
        out.add(os.path.basename(f).replace(".feather", "").rsplit("-", 1)[1])
    return out


def declared_tf(path):
    m = RX_TF.search(io.open(path, encoding="utf-8", errors="replace").read())
    return m.group(1) if m else None


def build_jobs(ledger):
    probe = {x["strategy"]: x for x in json.load(
        io.open(os.path.join(ROOT, "repair", "loadprobe.json"), encoding="utf-8"))}
    have = have_timeframes()
    jobs, skipped = [], {"not_importing": 0, "no_timeframe": 0, "no_data": 0}
    for r in csv.DictReader(io.open(ledger, encoding="utf-8")):
        if r["dropped_at"] != "G0_measured":
            continue
        p = probe.get(r["strategy"])
        if not p or p["result"] != "OK":
            skipped["not_importing"] += 1
            continue
        path = os.path.join(AUD, r["file"])
        if not os.path.exists(path):
            skipped["not_importing"] += 1
            continue
        tf = declared_tf(path)
        if tf is None:
            skipped["no_timeframe"] += 1
            continue
        if tf not in have:
            skipped["no_data"] += 1
            continue
        jobs.append((r["strategy"], r["repo"], r["file"],
                     [os.path.join(AUD, d) for d in p.get("extra_syspath", [])]))
    return jobs, skipped


def run_one(job):
    name, repo, relpath, extra = job
    dst = os.path.join(OUT_DIR, "%s.json" % name.replace("/", "_"))
    if os.path.exists(dst):
        return name, "SKIP (card exists)", 0.0
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONWARNINGS="ignore")
    if extra:
        env["PYTHONPATH"] = os.pathsep.join(extra)
    # Log the START, not only the finish. Without this a stall is invisible:
    # the log simply stops, and there is no way to tell which strategy it stopped
    # on. That cost two aborted runs before it was added.
    print("  -> start %s" % name, flush=True)
    t0 = time.time()
    try:
        r = subprocess.run([PY, os.path.join(ROOT, "repair", "measure_one.py"),
                            name, repo, relpath],
                           capture_output=True, timeout=OUTER_TIMEOUT, env=env, cwd=ROOT)
        out = (r.stdout + r.stderr).decode("utf-8", "replace").strip().splitlines()
        line = out[-1] if out else "NO OUTPUT"
    except subprocess.TimeoutExpired:
        line = "TIMEOUT after 3600s"
    return name, line, time.time() - t0


def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AUD, "LEDGER.csv")
    workers = int(os.environ.get("MEASURE_WORKERS", "6"))
    os.makedirs(OUT_DIR, exist_ok=True)
    jobs, skipped = build_jobs(ledger)
    todo = [j for j in jobs
            if not os.path.exists(os.path.join(OUT_DIR, "%s.json" % j[0].replace("/", "_")))]
    print("eligible %d | already carded %d | to run %d | workers %d"
          % (len(jobs), len(jobs) - len(todo), len(todo), workers), flush=True)
    print("excluded: %s" % skipped, flush=True)
    if not todo:
        return
    t0, done = time.time(), 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run_one, j) for j in todo]
        for f in as_completed(futs):
            name, line, secs = f.result()
            done += 1
            rate = (time.time() - t0) / done
            eta = rate * (len(todo) - done) / 60.0
            print("[%d/%d] %-70s  ETA %.0f min" % (done, len(todo), line[:70], eta),
                  flush=True)
    print("ALL DONE in %.1f min" % ((time.time() - t0) / 60.0), flush=True)


if __name__ == "__main__":
    main()
