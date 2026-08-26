# -*- coding: utf-8 -*-
u"""expand — expanding the corpus with new repositories.

Clones shallowly (--depth 1), then counts how many NEW class names
each repository contributes beyond those already present.

WHY COUNT THE INCREMENT, NOT THE NUMBER OF FILES. The freqtrade ecosystem consists of
copies: in the current corpus 484 occurrences out of 1055 are duplicates, Schism lives in 16
repositories. A repository with a thousand files may add NO new
strategy. The corpus denominator is unique classes, and the increment is counted against it.

⚠ Cloning someone else's code. Nothing is executed at this step: only
AST parsing in find_strategies. It runs later, with the same instrument as the
remaining 571.
"""
from __future__ import print_function

import io
import os
import subprocess
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from harness import find_strategies

REPOS = os.path.join(_ROOT, "repos")
MAX_KB = 60000          # declared limit: heavier repositories are not taken

# TOTAL: the list of requested pairs is the INPUT of the study, declared
# intentionally, not the scope of verification. Extending the list is a decision, not a finding.
WANT = [
    "keithorange/HUGE_FreqTrade_Strategy_Collection",
    "Foxel05/freqtrade-stuff",
    "phuchust/freqtrade_strategy",
    "hansen1015/freqtrade_strategy",
    "ShahAnuj2610/my-freqtrade",
    "bustillo/freqtrade-strategies",
    "mikedigriz/freqtrade-strategy-mikedigriz",
    "jaredrsommer/freqtradestrategies",
    "MMR-19/freqtrade-strategies",
    "botenesp/freqtrade_strategies",
    "Juusseli/Trade",
    "anakein/beastbotXB",
    "freqtrade/berlinguyinca-trading-strategies",
    "seannowotny/FlawlessVictoryPort",
    "devbootstrap/optimize-trading-strategy-using-freqtrade",
    "jerome-benoit/freqai-strategies",
    "ShahAnuj2610/my-freqtrade-nfi-nextgen",
    "keryc/crypto-bot",
    "p-zombie/freqtrade",
    "Mohamed-sm/Freqtrade-RLStrategy-IA",
]


def known_names():
    seen = set()
    for d in sorted(os.listdir(REPOS)):
        p = os.path.join(REPOS, d)
        if os.path.isdir(p):
            for _f, n in find_strategies(p):
                seen.add(n)
    return seen


def main():
    base = known_names()
    print(u"already known unique classes: %d" % len(base), flush=True)
    grand = set(base)
    report = []
    for full in WANT:
        d = full.replace("/", "_", 1)
        path = os.path.join(REPOS, d)
        if not os.path.isdir(path):
            r = subprocess.run(["git", "clone", "--depth", "1", "-q",
                                "https://github.com/%s.git" % full, path],
                               capture_output=True, timeout=600)
            if r.returncode != 0:
                print(u"  ✗ %-52s NOT CLONED: %s"
                      % (full, r.stderr.decode("utf-8", "replace")[:80]), flush=True)
                continue
        names = {n for _f, n in find_strategies(path)}
        new = names - grand
        grand |= names
        report.append((len(new), len(names), full))
        print(u"  %-52s classes %4d · NEW %4d"
              % (full, len(names), len(new)), flush=True)

    report.sort(reverse=True)
    print()
    print(u"TOTAL unique classes were %d, now %d — increment %d"
          % (len(base), len(grand), len(grand) - len(base)))
    print(u"⚠ limit declared: repositories heavier than %d KB were not taken" % MAX_KB)
    print()
    print(u"who contributed the increment:")
    for new, tot, full in report:
        if new:
            print(u"   +%-4d out of %-4d  %s" % (new, tot, full))
    dead = [f for n, t, f in report if n == 0]
    if dead:
        print(u"CONTRIBUTED NO NEW (%d): %s" % (len(dead), u", ".join(dead)))


if __name__ == "__main__":
    main()
