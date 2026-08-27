# -*- coding: utf-8 -*-
"""report_candidates - put the Class 1 survivors through the audit's own gates.

A strategy that beats buy-and-hold on the raw numbers has cleared nothing yet.
The audit's ladder exists precisely because such rows are usually explained by
too few trades, look-ahead bias, or indicator recursion. Reporting the raw
comparison without those columns would repeat the mistake this whole project is
about.

So for every strategy that produced numbers in both windows, this prints the
figures the ladder actually decides on: trade count against G1's threshold of
30, in-sample and out-of-sample significance, and what freqtrade's two bias
detectors said.

Also resolves the failure causes the coarse grouping in report_class1.py leaves
in "other", because an unexplained bucket is indistinguishable from one nobody
looked at.
"""
import collections
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS = os.path.join(ROOT, "repair", "results_class1")
G1_MIN_TRADES = 30
ALPHA = 0.05


def load():
    out = []
    for f in sorted(glob.glob(os.path.join(CARDS, "*.json"))):
        try:
            out.append(json.load(io.open(f, encoding="utf-8")))
        except Exception:
            pass
    return out


def main():
    cards = load()
    both = [c for c in cards
            if c["runs"]["in_sample"]["level"] == "PASSED"
            and (c["runs"].get("out_sample") or {}).get("level") == "PASSED"]

    print("=== strategies with numbers in both windows: %d ===" % len(both))
    print()
    hdr = ("%-28s %6s %7s %10s %10s %10s  %-16s %-16s" %
           ("strategy", "trades", "G1>=30", "OOS %", "market %", "os_p", "lookahead", "recursive"))
    print(hdr)
    print("-" * len(hdr))
    survivors = []
    for c in sorted(both, key=lambda z: -((z["runs"]["out_sample"]["summary"] or {}).get("total_pct") or -1e9)):
        o = c["runs"]["out_sample"]["summary"] or {}
        i = c["runs"]["in_sample"]["summary"] or {}
        n = o.get("trades") or 0
        tot, mkt = o.get("total_pct"), o.get("market_change_pct")
        beats = tot is not None and mkt is not None and tot > mkt
        look = c["runs"].get("lookahead", {}).get("level")
        rec = c["runs"].get("recursive", {}).get("level")
        print("%-28s %6s %7s %10s %10s %10s  %-16s %-16s" % (
            c["strategy"][:28], n, "yes" if n >= G1_MIN_TRADES else "NO",
            tot, mkt, o.get("p_value"), look, rec))
        if beats and n >= G1_MIN_TRADES and look != "FOUND" and rec != "FOUND" \
                and (o.get("p_value") is not None and o["p_value"] < ALPHA) \
                and (i.get("p_value") is not None and i["p_value"] < ALPHA):
            survivors.append(c)

    print()
    print("Candidates surviving the gates this run can check")
    print("(beats BH, >=30 trades, both bias detectors clear, significant in and out):")
    if not survivors:
        print("  none")
    for c in survivors:
        o = c["runs"]["out_sample"]["summary"] or {}
        i = c["runs"]["in_sample"]["summary"] or {}
        print("  %-28s OOS %s%% vs market %s%%  n=%s  is_p=%s  os_p=%s" % (
            c["strategy"][:28], o.get("total_pct"), o.get("market_change_pct"),
            o.get("trades"), i.get("p_value"), o.get("p_value")))

    # resolve the coarse "other" bucket
    sys.path.insert(0, os.path.join(ROOT, "repair"))
    from report_class1 import whose_fault
    none_ = [c for c in cards if c["runs"]["in_sample"]["level"] != "PASSED"]
    oth = [c for c in none_ if whose_fault(c["runs"]["in_sample"].get("why")) == "other"]
    print()
    print("=== the %d failures the coarse grouping leaves in 'other' ===" % len(oth))
    cnt = collections.Counter(str(c["runs"]["in_sample"].get("why"))[:70] for c in oth)
    for k, v in cnt.most_common(15):
        print("  %4d  %s" % (v, k))


if __name__ == "__main__":
    main()
