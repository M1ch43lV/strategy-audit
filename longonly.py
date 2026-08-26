# -*- coding: utf-8 -*-
u"""longonly — return to the corpus 77 strategies cut off by the spot mode.

WHY NOT FUTURES. These 77 declare `can_short = True`, and the corpus was run in
spot mode — that is, they were cut off by MY configuration, not by their own quality.
The natural answer "run on futures" HAS BEEN TESTED AND DOES NOT WORK:

    fapi.binance.com          451 (geoblock), fapi1/2/3 — 202 with empty body
    data.binance.vision       futures archives EXIST
    BTCUSDT 5m futures        first month 2020-03; 2018-03 … 2019-12 — 404

The author's window (2018-03…2020-03) predates the existence of Binance USDT futures.
Running on futures would give these 77 THEIR OWN, later window,
incomparable with the remaining 494. This is not corpus restoration, but a different
population.

WHAT IS DONE INSTEAD. Exactly what the engine itself suggests in the rejection text:
"You can run this strategy in spot markets by setting can_short=False. Please
note that short signals will be ignored in that case."

⚠ THIS MEASURES A DIFFERENT SUBJECT, and it is marked as such. A strategy with
the short side stubbed out is not the strategy the author wrote. It answers
a separate question: "what would a spot trader get who has no shorts at all." Cards get
`variant: "long_only"` and are NEVER mixed with the main corpus in summary statistics.

THE EDIT IS MINIMAL AND VISIBLE. The file is copied, one line is added to the class
`can_short = False`. Sources in repos/ are not touched. A one-line diff is
not "rewriting your logic", it is a literal engine instruction.
"""
from __future__ import print_function

import io
import json
import os
import re
import shutil
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import runlock
from harness import RESULTS, audit_one, declared_tf

TODO = os.path.join(_ROOT, "futures_todo.json")
SHADOW = os.path.join(_ROOT, "repos_longonly")


def patch(src_path, cls, dst_path):
    u"""A copy with one added line. Returns True if the edit applied."""
    src = io.open(src_path, encoding="utf-8", errors="replace").read()
    # ⚠ A OBSERVED MISTAKE. First I added the line FIRST in the class body and
    # wrote in a comment that it would "override the later can_short =
    # True". In Python the LAST assignment wins — the line did not override
    # anything, and the engine rejected exactly as before. Caught because the trial
    # run gave the same error, not because I reread my code.
    #
    # Correct: REPLACE the existing declaration, and add only when
    # it is absent entirely.
    if re.search(r"^\s*can_short\s*=\s*True", src, re.M):
        out = re.sub(r"^(\s*)can_short\s*=\s*True.*$",
                     r"\1can_short = False  # replaced by audit: spot",
                     src, flags=re.M)
    elif re.search(r"^\s*can_short\s*=\s*False", src, re.M):
        out = src                                   # already long — do not touch
    else:
        m = re.search(r"^(class\s+%s\s*\([^)]*\)\s*:\s*)$" % re.escape(cls),
                      src, re.M)
        if not m:
            return False
        ins = m.end() + 1
        out = src[:ins] + u"    can_short = False  # added by audit: spot\n" + src[ins:]
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    io.open(dst_path, "w", encoding="utf-8").write(out)
    return True


def main():
    todo = json.load(io.open(TODO, encoding="utf-8"))
    shard, shards = 0, 1
    for i, a in enumerate(sys.argv):
        if a == "--shard" and i + 1 < len(sys.argv):
            shard, shards = [int(x) for x in sys.argv[i + 1].split("/")]
    # ⚠ The lock is NAMED BY SHARE. First I took one name for all shares, and three of
    # four legitimately refused — the lock caught my own error before it
    # would have produced mixed cards. Shares write to non-overlapping names
    # files, which is why they need their own lock for each, not a shared one.
    lock = "corpus-longonly-%d" % shard
    if not runlock.acquire(lock):
        raise SystemExit(2)
    import atexit
    atexit.register(lambda: runlock.release(lock))
    mine = [x for i, x in enumerate(todo) if i % shards == shard]
    print(u"long side: share %d/%d = %d out of %d"
          % (shard, shards, len(mine), len(todo)), flush=True)

    os.makedirs(RESULTS, exist_ok=True)
    done = skipped = 0
    for name, rel, tf in mine:
        out = os.path.join(RESULTS, "%s__longonly.json" % name)
        if os.path.exists(out):
            continue
        srcp = os.path.join(_ROOT, rel.replace("/", os.sep))
        dstp = os.path.join(SHADOW, os.path.basename(rel))
        if not os.path.exists(srcp) or not patch(srcp, name, dstp):
            skipped += 1
            print(u"  EDIT DID NOT APPLY: %s (class not found in file)" % name, flush=True)
            continue
        try:
            r = audit_one("long_only/" + name, dstp, name)
        except Exception as ex:
            r = {"repo": "long_only", "file": rel, "strategy": name, "static": [],
                 "runs": {k: {"level": u"NA", "why": repr(ex)[:150],
                              "summary": None}
                          for k in ("in_sample", "out_sample", "lookahead", "recursive")}}
        r["source"] = "long_only"
        r["variant"] = "long_only"
        r["note"] = (u"can_short=False appended by audit; short signals "
                     u"are ignored. THIS IS NOT THE STRATEGY the author wrote.")
        r["declared_timeframe"] = tf
        tmp = out + ".tmp"
        io.open(tmp, "w", encoding="utf-8").write(
            json.dumps(r, ensure_ascii=False, indent=2))
        os.replace(tmp, out)
        done += 1
        ins = r["runs"]["in_sample"]
        print(u"  [%d/%d] %-34s %s" % (done, len(mine), name[:34],
              ins.get("summary") or ins.get("why", "")), flush=True)
    print(u"DONE: counted %d, edit did not apply for %d" % (done, skipped), flush=True)


if __name__ == "__main__":
    main()
