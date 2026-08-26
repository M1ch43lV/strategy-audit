# -*- coding: utf-8 -*-
u"""corpus — running the same audit over the entire collected corpus.

Deduplication by CLASS NAME: the same strategy is scattered across many
repositories (Schism — in 16), and analyzing it 16 times would bloat the
corpus with repeats and distort any summary statistics. The first occurrence
wins; the rest are recorded as copies.
"""
import io, json, os, sys
import os as _os
_ROOT = _os.environ.get("AUDIT_ROOT") or _os.path.dirname(_os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
from harness import find_strategies, audit_one, RESULTS

REPOS = _os.path.join(_ROOT, "repos")
LOCK = _os.path.join(_ROOT, "corpus.lock")

# ⚠ OBSERVED DEFECT 20.08, TWICE. First, I restarted the run three times without
# killing the previous one, and got FOUR processes writing to one folder
# with DIFFERENT code versions: the card made it impossible to tell what
# computed it. Fixed here — and an hour later two CANDLE LOADERS wrote the same
# files. Same class, second place, because I fixed the case.
#
# A result of unknown origin is worse than a missing one: it looks like
# knowledge. So the lock is moved to runlock.py and taken EVERYWHERE that writes to
# shared resources, rather than retold in each file anew.
#
# PARALLELIZATION. A five-minute strategy — 55 s in the author’s window and 149 s outside
# it (measured, not estimated); 351 of those = 26 hours in a single thread. The work
# is split into NON-OVERLAPPING shares by the remainder of division, each with its own
# lock. The ban on two writers hasn't gone away: it was about DIFFERENT VERSIONS of code
# in one folder, not about the number of processes. Therefore, in addition to the lock, each
# card is STAMPED with a fingerprint of harness.py: the lock prevents mixing,
# the fingerprint allows DETECTING it. A ban without detection is a promise.
import hashlib
import runlock

SHARD, SHARDS = 0, 1
for i, a in enumerate(sys.argv):
    if a == "--shard" and i + 1 < len(sys.argv):
        SHARD, SHARDS = [int(x) for x in sys.argv[i + 1].split("/")]
CODE_MD5 = hashlib.md5(
    io.open(_os.path.join(_ROOT, "harness.py"), "rb").read()).hexdigest()[:12]

if not runlock.acquire("corpus-%d" % SHARD):
    raise SystemExit(2)
import atexit
atexit.register(lambda: runlock.release("corpus-%d" % SHARD))

# ⚠ OBSERVED DEFECT 21.08. Six pairs of names in the corpus differ ONLY
# IN CASE (Ichi/ichi, SAR/Sar, BBRSI/bbrsi, HLHB/hlhb, mabStra/MabStra,
# SuperTrend/Supertrend). The Windows file system does not distinguish case, and
# `os.path.exists(results/ichi.json)` returned TRUE about Ichi.json. The run
# considered the second strategy of the pair already computed and SILENTLY skipped it.
#
# Lost 6 out of 571 — 1%. Little, but it's exactly "silent truncation reading as
# full coverage," prohibited by its own preregistration. The cure is not
# "remember the case," but making the file name unambiguous.
ALL_NAMES = []


def card_path(name):
    same = [x for x in ALL_NAMES if x.lower() == name.lower()]
    if len(same) > 1:
        h = hashlib.md5(name.encode("utf-8")).hexdigest()[:6]
        return _os.path.join(RESULTS, "%s__%s.json" % (name, h))
    return _os.path.join(RESULTS, "%s.json" % name)


os.makedirs(RESULTS, exist_ok=True)
seen, plan, dup = set(), [], 0
for d in sorted(os.listdir(REPOS)):
    p = os.path.join(REPOS, d)
    if not os.path.isdir(p):
        continue
    repo = d.replace("_", "/", 1)
    for f, n in sorted(find_strategies(p)):
        if n in seen:
            dup += 1
            continue
        seen.add(n)
        plan.append((repo, f, n))
# Shares are cut by the NUMBER in the list, so the list must be identical across
# all processes. Verified: three independent runs gave one fingerprint
# (dac6309df791d209, 571). But a "once" check ages, so the fingerprint
# is PRINTED by each share: if lists diverge, it will be visible in logs, not
# remain a silent loss of strategies.
ALL_NAMES.extend(n for _, _, n in plan)
PLAN_MD5 = hashlib.md5(u"|".join(n for _, _, n in plan).encode("utf-8")).hexdigest()[:16]
mine = [x for i, x in enumerate(plan) if i % SHARDS == SHARD]
print(u"unique strategies: %d · copies skipped: %d · share %d/%d = %d pcs · code %s · list %s"
      % (len(plan), dup, SHARD, SHARDS, len(mine), CODE_MD5, PLAN_MD5), flush=True)
plan = mine
done = 0
for repo, f, n in plan:
    out = card_path(n)
    if os.path.exists(out):
        continue
    try:
        r = audit_one(repo, f, n)
    except Exception as ex:
        r = {"repo": repo, "file": f, "strategy": n, "static": [],
             "runs": {k: {"level": u"NA", "why": repr(ex)[:150],
                          "summary": None} for k in
                      ("in_sample", "out_sample", "lookahead", "recursive")}}
    r["code_md5"], r["plan_md5"] = CODE_MD5, PLAN_MD5
    r["source"] = "corpus"          # than computed — a property of the card, not of memory
    # write via a temporary file: an interrupted process won't leave a half-card,
    # which the next run would take as complete and skip
    tmp = out + ".tmp"
    io.open(tmp, "w", encoding="utf-8").write(json.dumps(r, ensure_ascii=False, indent=2))
    _os.replace(tmp, out)
    done += 1
    ins = r["runs"]["in_sample"]
    print(u"[%d/%d] %-34s %s" % (done, len(plan), n[:34],
          ins.get("summary") or ins.get("why", "")), flush=True)
