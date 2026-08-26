# -*- coding: utf-8 -*-
u"""power — pre-flight power calculation: WHAT IT COSTS TO FIND OUT that a strategy works.

THE QUESTION NO AUDIT ASKS. A backtest says "expectancy +0.53 per
trade." It doesn't say HOW MANY LIVE TRADES are needed to distinguish that from zero.
But that's computable — and it often turns out the experiment can't be run within a
human lifetime.

THE MOTIVE — OUR OWN CASE. Our engine: gross +6.94 bps per trade with a
spread of 82.9 bps, cost 10.00 bps with a spread of EXACTLY ZERO. To distinguish
the desired effect at 80% power requires 429,872 trades and $487,952 in fees.
Two years of live trading was an experiment incapable of ending in a conclusion —
underpowered by three orders of magnitude FROM DAY ONE, and nobody calculated it.

WHERE THE SPREAD NOT IN THE SUMMARY COMES FROM. freqtrade prints
`Mean profit p-value`. That's a t-test: t = mean/(SD/sqrt(n)). Knowing mean, n, and p,
the spread is RECOVERED: SD = mean*sqrt(n)/t. Nothing new needs to be measured.

WHAT COUNTS AS AN "UNVERIFIABLE" ANSWER
  * mean <= 0            — no n will prove positivity
  * p >= 0.999           — t is indistinguishable from zero, spread cannot be recovered
  * required years > 100 — the experiment can't be run in a lifetime

All of these are CATEGORIES, not omissions: "couldn't calculate" is nowhere printed
as "good."
"""
from __future__ import print_function

import glob
import io
import json
import os
import sys
from statistics import NormalDist

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RESULTS = os.path.join(_ROOT, "results")
WIN_DAYS = 731.0            # author window 2018-03-01 … 2020-03-01
POWER_Z = 0.8416            # 80% power
ALPHA_Z = 1.9600            # two tails, 0.05
LIFETIME_Y = 100.0
MIN_N = 30                  # declared in advance, as in STRATA_PREREG


def implied_sd(mean, n, p):
    u"""Spread recovered from the p-value. None — cannot be recovered."""
    if n is None or n < 2 or mean is None or p is None:
        return None
    if p >= 0.999:
        return None
    # ⚠ CLAMP, NOT FAILURE. Strong effects can have p of 1.4e-65; then
    # 1 - p/2 collapses to EXACTLY one and the inverse normal fails.
    # The previous guard only caught zero and missed this case. Very
    # small p means "the effect is huge," not "cannot be measured": returning
    # None here would mean recording the strongest result as "could not."
    p = max(p, 1e-12)
    t = NormalDist().inv_cdf(1.0 - p / 2.0)
    if t <= 1e-9:
        return None
    return abs(mean) * (n ** 0.5) / t


def required_n(mean, sd):
    if not sd or mean is None or mean <= 0:
        return None
    return ((ALPHA_Z + POWER_Z) ** 2) * (sd * sd) / (mean * mean)


def main():
    rows, biased = [], []
    for f in sorted(glob.glob(os.path.join(RESULTS, "*.json"))):
        try:
            r = json.load(io.open(f, encoding="utf-8"))
        except Exception:
            continue
        s = r["runs"]["in_sample"].get("summary")
        if not isinstance(s, dict) or s.get("trades") is None:
            continue
        n, mean, p = s.get("trades"), s.get("expectancy"), s.get("p_value")
        if n < MIN_N:
            continue
        # ⚠ BOUNDARY OF THIS TOOL, STATED DIRECTLY. The calculation inherits
        # the optimism of the backtest. If the backtest contains lookahead,
        # "trades needed" will come out negligible — not because the strategy is strong,
        # but because the entry is fictitious. Example from this same corpus:
        # ichiV1, freqtrade's native detector found bias (7 entries out of 20
        # signals), out-of-sample drawn as +18,701,080%.
        #
        # Therefore strategies with detected bias are NOT counted, but named
        # as a separate category. Conversely, a negligible "trades needed" itself
        # becomes a sign that the backtest should be rechecked.
        if r["runs"].get("lookahead", {}).get("level") == u"FOUND":
            biased.append(r["strategy"])
            continue
        sd = implied_sd(mean, n, p)
        need = required_n(mean, sd)
        rate = n / WIN_DAYS                      # trades per day in the author's window
        years = (need / rate / 365.0) if (need and rate > 0) else None
        rows.append({"name": r["strategy"], "src": r.get("source"), "n": n,
                     "mean": mean, "p": p, "sd": sd, "need": need,
                     "years": years})

    corpus = [r for r in rows if r["src"] == "corpus"]
    case = [r for r in rows if r["src"] != "corpus"]

    def block(title, rs):
        print(u"\n%s — %d strategies with numbers" % (title, len(rs)))
        if not rs:
            return
        neg = [r for r in rs if r["mean"] is None or r["mean"] <= 0]
        nosd = [r for r in rs if r not in neg and r["sd"] is None]
        good = [r for r in rs if r["need"]]
        life = [r for r in good if r["years"] and r["years"] > LIFETIME_Y]
        print(u"  expectation <= 0 — no n will help      %4d" % len(neg))
        print(u"  spread cannot be restored (p ~ 1)           %4d" % len(nosd))
        print(u"  counted                                 %4d" % len(good))
        if good:
            print(u"  of which UNVERIFIABLE in 100 years            %4d   (%.0f%% of counted)"
                  % (len(life), 100.0 * len(life) / len(good)))
            good.sort(key=lambda r: r["years"] if r["years"] else 9e9)
            print(u"\n  %-30s %6s %9s %9s %12s %10s"
                  % (u"strategy", u"trades", u"exp.", u"spread", u"trades needed", u"years"))
            for r in good[:10]:
                print(u"  %-30s %6d %9.3f %9.2f %12s %10s"
                      % (r["name"][:30], r["n"], r["mean"], r["sd"],
                         format(int(r["need"]), ",").replace(",", " "),
                         (u"%.1f" % r["years"]) if r["years"] else u"—"))
            if len(good) > 10:
                print(u"  … and %d more" % (len(good) - 10))

    block(u"CORPUS", corpus)
    block(u"ANALYSIS paulcpk", case)

    allg = [r for r in rows if r["need"]]
    if allg:
        med = sorted(r["years"] for r in allg if r["years"])
    if biased:
        print("")
        print(u"EXCLUDED: %d strategies with LOOKAHEAD BIAS "
              u"(freqtrade's native detector) — their expectation is fictitious:" % len(biased))
        for _b in sorted(biased):
            print(u"    " + _b)
        print(u"\nMEDIAN across all counted: %.1f years of live trading, "
              u"to prove that the strategy works."
              % med[len(med) // 2])
    print(u"\nOUR ENGINE FOR COMPARISON: 429,872 trades, $487,952 in fees — "
          u"an experiment that cannot be conducted.")


if __name__ == "__main__":
    main()
