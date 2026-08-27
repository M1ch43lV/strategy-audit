# -*- coding: utf-8 -*-
"""report - render clusters.json into CLUSTERS.csv and CLUSTERS.md.

Two outputs because they answer different questions. The CSV is for joining
against the ledger and running your own cuts; the Markdown is for reading the
distribution and, more importantly, the measurability table at the end.

That last table is the point of this file. It shows that whether a strategy
ever entered the audit's ladder depends heavily on which cluster it belongs to,
which means the measured sample is not the corpus but a selection from it.
"""
import collections
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT

COLS = ["strategy", "repo", "implementation_id", "run_profile", "provenance",
        "repair_class", "eligibility_status", "direction", "logic", "speed", "complexity",
        "exit_style", "dca", "informative", "timeframe", "stoploss",
        "regime_hypothesis", "measured", "dropped_at", "os_total",
        "os_market", "beats_bh", "os_trades", "indicators"]


def write_csv(rows, ledger, dst):
    led = {r["strategy"]: r for r in csv.DictReader(io.open(ledger, encoding="utf-8"))}
    with io.open(dst, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for x in rows:
            r = led.get(x["strategy"], {})
            out = {k: x.get(k) for k in COLS if k in x}
            out.update({"dropped_at": r.get("dropped_at"),
                        "os_total": r.get("os_total"), "os_market": r.get("os_market"),
                        "beats_bh": r.get("beats_bh"), "os_trades": r.get("os_trades"),
                        "indicators": "|".join(x["indicators"])})
            w.writerow(out)


def write_md(rows, dst):
    L = ["# Corpus clusters", ""]
    L.append("%d canonical strategies classified. Source: `cluster/CLUSTERS.csv`, "
             "produced by `cluster/classify.py`." % len(rows))
    L.append("")
    L.append("Five **independent** axes rather than one bucket. A strategy is not "
             "`mean_reversion` OR `long_short`, it is both at once - and for the "
             "question \"which market phase\" the combination is what matters. Every "
             "label carries its reason in `clusters.json` under `why`, so a wrong "
             "classification can be refuted on the individual case rather than only "
             "showing up as noise in the aggregate.")
    L.extend(["", "This is a preregistered **source taxonomy**, not behavioral "
              "clustering. It consumes `EXECUTION_PROFILES.csv`, keeps dormant "
              "short writes separate through canonical `direction_capability`, and "
              "does not determine `regime_eligible`."])

    def block(key, title):
        c = collections.Counter(x[key] for x in rows)
        t = sum(c.values())
        L.extend(["", "## " + title, "",
                  "| Category | Count | Share | of which measured |",
                  "|---|---:|---:|---:|"])
        for k, v in c.most_common():
            m = sum(1 for x in rows if x[key] == k and x["measured"])
            L.append("| `%s` | %d | %.1f%% | %d (%.0f%%) |"
                     % (k, v, 100.0 * v / t, m, 100.0 * m / v))

    for k, t in [("direction", "Direction"), ("logic", "Trading logic"),
                 ("speed", "Speed"), ("complexity", "Complexity"),
                 ("regime_hypothesis", "Expected market phase")]:
        block(k, t)

    L.extend(["", "## The finding that matters for regime analysis", "",
              "Whether a strategy ever entered the audit's ladder depends heavily on "
              "its cluster. The measured sample is therefore not the corpus:", "",
              "| Group | Measured |", "|---|---:|"])
    for key, vals in [("logic", ["ml_freqai"]),
                      ("direction", ["long_short", "short_only", "long_only"]),
                      ("complexity", ["complex", "simple"]),
                      ("speed", ["unknown"])]:
        for v in vals:
            sub = [x for x in rows if x[key] == v]
            if not sub:
                continue
            m = sum(1 for x in sub if x["measured"])
            L.append("| `%s` | %d of %d (%.0f%%) |" % (v, m, len(sub), 100.0 * m / len(sub)))
    L.extend(["", "Any statement the audit makes about \"public freqtrade strategies\" "
                  "is therefore in practice a statement about **simple, long-only, "
                  "spot-capable** ones. Strategies built for falling markets - the "
                  "`short_only` and `long_short` groups - are less represented, which is "
                  "precisely the group a regime study needs.", ""])
    io.open(dst, "w", encoding="utf-8").write("\n".join(L))


def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AUD, "LEDGER.csv")
    rows = json.load(io.open(os.path.join(ROOT, "cluster", "clusters.json"),
                             encoding="utf-8"))
    write_csv(rows, ledger, os.path.join(ROOT, "cluster", "CLUSTERS.csv"))
    write_md(rows, os.path.join(ROOT, "cluster", "CLUSTERS.md"))
    print("wrote CLUSTERS.csv and CLUSTERS.md for %d strategies" % len(rows))


if __name__ == "__main__":
    main()
