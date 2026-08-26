# -*- coding: utf-8 -*-
u"""census_repos — what the corpus is built from and how much ORIGINAL each contributed.

Not “how many files,” but how many classes appear for the FIRST TIME. The freqtrade
ecosystem consists of copies, and a repository with five hundred files may add
five originals. The traversal order is alphabetical and fixed; otherwise, “who first
contributed” would depend on the order I cloned them.

⚠ HONEST DISCLAIMER ON THE WORD “FIRST.” The right of precedence here means only
“encountered earlier in alphabetical traversal,” not “original author.” Who copied
from whom is not visible in the code, and we do not claim it.
"""
from __future__ import print_function

import collections
import io
import json
import os
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from harness import find_strategies

REPOS = os.path.join(_ROOT, "repos")


def main():
    seen = set()
    rows = []
    occurrences = 0
    for d in sorted(os.listdir(REPOS)):
        p = os.path.join(REPOS, d)
        if not os.path.isdir(p):
            continue
        names = {n for _f, n in find_strategies(p)}
        occurrences += len(names)
        first = names - seen
        seen |= names
        rows.append((d.replace("_", "/", 1), len(names), len(first)))

    rows.sort(key=lambda r: (-r[2], -r[1]))
    print(u"%-56s %8s %9s %8s" % (u"repository", u"classes", u"first time", u"copy %"))
    for name, tot, first in rows:
        dup = 100.0 * (tot - first) / tot if tot else 0.0
        print(u"%-56s %8d %9d %7.0f%%" % (name[:56], tot, first, dup))
    print()
    print(u"repositories           %d" % len(rows))
    print(u"occurrences (with copies)  %d" % occurrences)
    print(u"UNIQUE CLASSES     %d" % len(seen))
    print(u"copy share             %.0f%%"
          % (100.0 * (occurrences - len(seen)) / occurrences if occurrences else 0))
    big = max(rows, key=lambda r: r[1])
    print()
    print(u"largest SINGLE repository: %s — %d classes"
          % (big[0], big[1]))
    print(u"corpus is %.1f times larger than it in unique classes"
          % (len(seen) / float(big[1])))
    zero = [r[0] for r in rows if r[2] == 0]
    if zero:
        print()
        print(u"CONTRIBUTED NO ORIGINALS (%d): %s"
              % (len(zero), u", ".join(zero)))
    io.open(os.path.join(_ROOT, "corpus_sources.json"), "w",
            encoding="utf-8").write(json.dumps(
                {"repos": [{"repo": a, "classes": b, "first": c} for a, b, c in rows],
                 "unique": len(seen), "occurrences": occurrences},
                ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
