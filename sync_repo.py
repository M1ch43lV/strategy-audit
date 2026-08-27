# -*- coding: utf-8 -*-
u"""sync_repo — published code must be THE SAME that computed the numbers.

REASON, OBSERVED ON 21.08. The repository contained `replicate.py` and `stats.py`, long
since removed from the workflow. An external reviewer read the repository and **praised
them as a strength**. Nothing false was written: the files existed, the code
worked. It just no longer related to the numbers, and a reader couldn't tell the
difference. The defect is not in the reviewer.

THERE ARE TWO CHECKS HERE, AND THE SECOND IS MORE IMPORTANT:

  ① DIVERGENCE — file exists in both places, but content differs.
     The published version is not the one that computed.

  ② ORPHAN — file exists in the repository and NOT in the working set.
     That's exactly how replicate.py and stats.py survived. The check "are all my
     files published" does NOT SEE this: it looks one way. You must look
     both ways.

The set is declared by the list below, not derived from folder contents: otherwise any
random file in the working directory would silently become "part of the pipeline".

RUN:  python sync_repo.py             show only
      python sync_repo.py --apply     copy and delete orphans
      python sync_repo.py --orphans   ONLY ② — works on a clean repo copy
                                      where there's no working tree;
                                      this exact form is in CI
      python sync_repo.py --selftest  sabotage: the check must find
"""
from __future__ import print_function

import filecmp
import io
import os
import shutil
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(_ROOT, "repo")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# PIPELINE — exactly these modules compute the published numbers.
# TOTAL: pipeline manifest — listing here is not a defect, but the subject itself:
# published code must be declared, and sync_repo refuses orphans.
PIPELINE = [
    "totality.py",
    "harness.py",        # measurement: engine, both windows, both instruments
    "corpus.py",         # corpus sweep by fractions
    "ledger.py",         # registry: one line per strategy, decision epochs
    "ledger_block.py",   # single build of the number block
    "dca.py",            # entry averaging: detection, groups, paired A/B
    "multiplicity.py",   # multiplicity correction
    "traps.py",          # community backtest pitfalls
    "dof.py",            # degrees of freedom
    "power.py",          # power
    "coverage.py",       # pair data coverage
    "loadscan.py",       # download failure reasons
    "report.py",         # cards and pointers
    "census_repos.py",   # source census
    "harvest.py",        # repository collection
    "expand.py",         # corpus expansion
    "longonly.py",       # short-disabled variant
    "fetch_bulk.py",     # candles from monthly archives
    "setup_ft.py",       # freqtrade working folder
    "tfscan.py",         # which timeframes are declared
    "depth.py",          # depth-conditioned forward-return diagnostic
    "loadcheck.py",      # first-gate import/load failure attribution
    "resolvable.py",     # barrier-race sample-size diagnostic
    "execution_profiles.py",  # canonical implementation and run-profile manifest
    "regime_eligibility.py",  # technical Stage 6 inclusion/exclusion matrix
    "profile_repairs.py",     # reproducible Class 2 compatibility overlays
    "profile_smoke.py",       # mode-correct futures runtime validation
    "profile_freqtrade.py",   # author-package extension launcher for smoke tests
    "runlock.py",        # one writer for a shared resource
    "anatman.py",        # observed defects as executable cases
    "tf_guard_selftest.py",  # sabotage against the timeframe guard
    "sync_repo.py",      # this file: published = working
]

# Lives only in the repository: checks published on a clean machine.
REPO_ONLY = ["verify_ledger.py", "freeze_guard.py"]  # TOTAL: manifest AND IS declaration


def orphans_only():
    u"""② without ①. On a clean repository copy there is no working tree, so
    there is nothing to compare against — but asking "is there code here that is not in the
    pipeline" is possible, and that is exactly the question that was missed."""
    here = os.path.dirname(os.path.abspath(__file__))
    known = set(PIPELINE) | set(REPO_ONLY) | {"sync_repo.py"}
    found = sorted(f for f in os.listdir(here) if f.endswith(".py"))
    orphans = [f for f in found if f not in known]
    absent = [f for f in PIPELINE if not os.path.exists(os.path.join(here, f))]
    print(u"published modules: %d, declared in pipeline: %d"
          % (len(found), len(PIPELINE)))
    for f in orphans:
        print(u"  ORPHAN: %s — published but not declared as part of the pipeline" % f)
    for f in absent:
        print(u"  MISSING: %s — declared by the pipeline but not published" % f)
    if orphans or absent:
        print(u"code and its declaration diverged")
        return 1
    print(u"every published module is declared, and vice versa")
    return 0


def main():
    apply = "--apply" in sys.argv
    if "--orphans" in sys.argv:
        return orphans_only()
    if not os.path.isdir(REPO):
        print(u"no folder %s" % REPO)
        return 1

    missing, differ, same = [], [], []
    for f in PIPELINE:
        src, dst = os.path.join(_ROOT, f), os.path.join(REPO, f)
        if not os.path.exists(src):
            print(u"⛔ working set has NO %s — pipeline list lies" % f)
            return 1
        if not os.path.exists(dst):
            missing.append(f)
        elif not filecmp.cmp(src, dst, shallow=False):
            differ.append(f)
        else:
            same.append(f)

    known = set(PIPELINE) | set(REPO_ONLY)
    orphans = sorted(f for f in os.listdir(REPO)
                     if f.endswith(".py") and f not in known)

    print(u"PIPELINE: %d modules" % len(PIPELINE))
    print(u"  match             %3d" % len(same))
    print(u"  not published     %3d   %s" % (len(missing), u", ".join(missing) or u"—"))
    print(u"  differ            %3d   %s" % (len(differ), u", ".join(differ) or u"—"))
    print(u"  ORPHANS           %3d   %s" % (len(orphans), u", ".join(orphans) or u"—"))
    if orphans:
        print(u"  ⚠ orphan — published code not in the pipeline.")
        print(u"    Reader considers it part of the work. That is how replicate.py")
        print(u"    and stats.py survived, and external review praised exactly them.")

    if not apply:
        if missing or differ or orphans:
            print(u"\nnothing touched. To apply: python sync_repo.py --apply")
            return 1
        print(u"\npublished code matches working code")
        return 0

    for f in missing + differ:
        shutil.copy2(os.path.join(_ROOT, f), os.path.join(REPO, f))
        print(u"copied %s" % f)
    # ⚠ 22.08: previous version DELETED orphans itself and removed freeze_guard.py —
    # file added to the list only in the second copy of this same script.
    # This is a repeat of the class "tool owns a shared folder" (17.08, rmtree and
    # .docx operator). Deletion now requires a SEPARATE flag, and by
    # default orphans are NAMED and remain alive.
    if orphans and "--delete-orphans" not in sys.argv:
        print(u"⚠ orphans NOT deleted — explicit --delete-orphans required:")
        for f in orphans:
            print(u"     %s" % f)
        print(u"  before deleting, check whether the file was omitted from the list")
    elif orphans:
        for f in orphans:
            os.remove(os.path.join(REPO, f))
            print(u"orphan %s deleted" % f)
    print(u"done: %d copied, %d deleted"
          % (len(missing) + len(differ),
             len(orphans) if "--delete-orphans" in sys.argv else 0))
    return 0


def selftest():
    u"""Sabotage: the check must BE ABLE to find, not just agree."""
    import tempfile
    ok = []
    d = tempfile.mkdtemp()
    r = os.path.join(d, "repo")
    os.makedirs(r)
    io.open(os.path.join(d, "a.py"), "w", encoding="utf-8").write(u"x = 1\n")
    io.open(os.path.join(r, "a.py"), "w", encoding="utf-8").write(u"x = 1\n")
    io.open(os.path.join(r, "ghost.py"), "w", encoding="utf-8").write(u"dead\n")

    globals()["_ROOT"], globals()["REPO"] = d, r
    globals()["PIPELINE"], globals()["REPO_ONLY"] = ["a.py"], []
    ok.append((u"orphan found", main() == 1))

    os.remove(os.path.join(r, "ghost.py"))
    ok.append((u"clean state passes", main() == 0))

    io.open(os.path.join(r, "a.py"), "w", encoding="utf-8").write(u"x = 2\n")
    ok.append((u"discrepancy found", main() == 1))

    shutil.rmtree(d, ignore_errors=True)
    print()
    for n, v in ok:
        print(u"  %-28s %s" % (n, u"OK" if v else u"FAIL"))
    bad = [n for n, v in ok if not v]
    print(u"self-check: %d/%d" % (len(ok) - len(bad), len(ok)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
