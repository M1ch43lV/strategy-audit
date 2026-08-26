# -*- coding: utf-8 -*-
u"""multiplicity — correction for multiple testing. Previously it was NOT THERE.

REASON. An external review pointed out a hole that I called a caveat but did not
count: the funnel runs hundreds of strategies through p < 0.05 twice. With 464
tested strategies, the 0.05 threshold alone lets dozens of candidates through
BY PURE CHANCE. Acknowledging this in a note and not counting it is the same
as printing "not verified" without reason.

WHAT IS COUNTED HERE

  ① Benjamini–Hochberg (FDR) on p-values of the author window and the
     out-of-sample window separately. FDR, not Bonferroni: the goal is the
     proportion of false positives among selected ones, not the complete
     absence of false positives. Bonferroni at n≈460 would cut almost
     everything and turn the conclusion into a tautology.

  ② DEPENDENCE — AND WHAT THIS COUNT DOES NOT PROVE. Corpus strategies are not
     independent: 65% are copies, families (NFI, Elliot, ClucHAnix) share logic.
     Here, EXACT matches by fingerprint (trades, in-sample expectation,
     out-of-sample expectation) are counted — and that's all.

     ⚠ CORRECTION TO MY OWN STATEMENT OF 21.08. I first wrote that since there
     are 414 distinct fingerprints out of 436, the correction is
     "conservative." That is too strong. The FDR guarantee of
     Benjamini–Hochberg holds under independence or positive dependence of a
     certain class; under arbitrary dependence, it does not hold. And the
     coincidence of three numbers IS NOT an estimate of the correlation
     structure of p-values: two strategies can differ on all three and be
     almost fully linked in returns, and vice versa.

     What can be honestly claimed: the fingerprint found so many EXACT
     duplicates; this does not measure dependence between hypotheses and is
     not used as evidence of independence. BH is computed on the FULL number
     of tests, not on a reduced effective one — that is, clustering gives us
     no advantage.

  ③ How many candidates would pass ⑤ and ⑦ BY CHANCE under the null hypothesis.

WHAT IS NOT HERE. Block bootstrap for temporal dependence and accounting for
correlation between strategies at the returns level — those require
per-trade series, which are not in the cards. Named, not omitted.
"""
from __future__ import print_function

import collections
import glob
import io
import json
import os
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ALPHA = 0.05


def fmt_p(p):
    u"""p-value presentation. Zero is impossible — we print the order of magnitude."""
    if p is None:
        return u"—"
    if p == 0:
        return u"<1e-300 (shown as below machine precision)"
    return (u"%.5f" % p) if p >= 1e-4 else (u"%.2e" % p)


# The BH implementation is SINGLE and lives in ledger_block.py — the module that must
# to work in CI without the rest of the tree. Here it is imported, not copied:
# two copies of the "same" formula diverge silently, and only someone reading
# both can notice it.
from ledger_block import bh  # noqa: E402


def main():
    rows = []
    for f in glob.glob(os.path.join(_ROOT, "results", "*.json")):
        try:
            r = json.load(io.open(f, encoding="utf-8"))
        except Exception:
            continue
        if r.get("source") != "corpus":
            continue
        a = r["runs"]["in_sample"].get("summary")
        b = r["runs"]["out_sample"].get("summary")
        if not isinstance(a, dict) or (a.get("trades") or 0) < 30:
            continue
        if a.get("p_value") is None:
            continue
        rows.append((r["strategy"], a, b if isinstance(b, dict) else None,
                     r["runs"]["lookahead"]["level"],
                     r["runs"]["recursive"]["level"]))

    print(u"strategies with >=30 trades and p-value: %d" % len(rows))

    # ── ① FDR in author window ────────────────────────────────────────────
    pos = [r for r in rows if (r[1].get("expectancy") or 0) > 0]
    p_in = [r[1]["p_value"] for r in pos]
    raw_in = sum(1 for p in p_in if p < ALPHA)
    thr_in, k_in = bh(p_in)
    print()
    print(u"① AUTHOR WINDOW, positive expectation: %d" % len(pos))
    print(u"   p < 0.05 without correction          %3d" % raw_in)
    print(u"   Benjamini–Hochberg (FDR 5%%)    %3d   threshold p <= %s"
          % (k_in, fmt_p(thr_in)))
    print(u"   expected PURELY BY CHANCE       %.1f  (0.05 x %d)"
          % (0.05 * len(pos), len(pos)))

    # ── ② FDR out-of-sample, among those passing ⑤ ───────────────────────────
    sig_in = [r for r in pos if r[1]["p_value"] < ALPHA]
    out = [r for r in sig_in if r[2] and r[2].get("p_value") is not None
           and (r[2].get("expectancy") or 0) > 0]
    p_out = [r[2]["p_value"] for r in out]
    raw_out = sum(1 for p in p_out if p < ALPHA)
    thr_out, k_out = bh(p_out)
    print()
    print(u"② OUT-OF-SAMPLE, among in-sample significant: %d" % len(out))
    print(u"   p < 0.05 without correction          %3d" % raw_out)
    print(u"   Benjamini–Hochberg (FDR 5%%)    %3d   threshold p <= %s"
          % (k_out, fmt_p(thr_out)))

    # ── ③ dependence: how many INDEPENDENT checks actually ──────
    key = collections.Counter()
    for n, a, b, _l, _r in rows:
        key[(a.get("trades"), a.get("expectancy"),
             (b or {}).get("expectancy"))] += 1
    dup = sum(v - 1 for v in key.values() if v > 1)
    print()
    print(u"③ DEPENDENCE BETWEEN CHECKS")
    print(u"   strategies                      %3d" % len(rows))
    print(u"   distinct by numbers             %3d" % len(key))
    print(u"   duplicates (same logic)         %3d" % dup)
    print(u"   ⇒ this is NOT an estimate of p-value dependence and NOT proof of")
    print(u"     independence. BH was computed on the FULL number of checks (%d),"
          % len(rows))
    print(u"     not the reduced effective one — clustering gives us no advantage.")
    print(u"     Under arbitrary dependence, the FDR guarantee of BH does not hold,")
    print(u"     and this remains an OPEN limitation.")

    # ── summary across all layers ─────────────────────────────────────────────
    final = [r for r in out if r[2]["p_value"] <= (thr_out or 0)
             and r[3] != u"FOUND" and r[4] != u"FOUND"]
    print()
    print(u"SUMMARY AFTER MULTIPLICITY CORRECTION:")
    print(u"   passed ⑦ without correction, clean by detectors: see funnel.py")
    print(u"   passed ⑦ AFTER FDR and clean by detectors:  %d" % len(final))
    for n, a, b, _l, _r in sorted(final, key=lambda x: x[2]["p_value"])[:10]:
        beats = (b.get("total_pct") or 0) > (b.get("market_change_pct") or 0)
        # ? PRESENTATION SEPARATE FROM STORAGE. "%.5f" printed 0.00000, and a reader
        # would read that as p = 0. Zero is impossible here: it is only "less than
        # 1e-5". Scientific notation is printed, the value is stored raw.
        print(u"      %-30s p_out %s · %s"
              % (n[:30], fmt_p(b["p_value"]),
                 u"BEAT the market" if beats else u"lost to the market"))
    print()
    print(u"⚠ NOT COVERED: block bootstrap for temporal dependence and")
    print(u"   return correlation between strategies — per-trade series are needed,")
    print(u"   which are not in the cards.")


if __name__ == "__main__":
    main()
