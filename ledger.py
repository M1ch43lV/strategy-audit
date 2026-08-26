# -*- coding: utf-8 -*-
u"""ledger — ONE LINE PER STRATEGY, from which we restore the entire path.

WHY. Until now, the final numbers ("55 passed", "0 beat the market") lived in
README prose and in funnel.py output. They could neither be recomputed from a
single place nor tied to a code version. On 21.08 this produced a defect right
before our eyes: an external reviewer praised two files that had long been
discarded, because the published numbers looked authoritative and CARRIED NO
PROVENANCE.

WHAT'S HERE. Each number has four coordinates, and they are printed alongside it:

    WHAT was counted · WITH WHICH code (code_md5) · ON WHICH corpus (plan_md5)
                  · UNDER WHICH set of decisions (epoch)

EPOCHS are not decoration. The order "rule → data" or "data → rule"
changes the evidential strength of the conclusion, and it is VERIFIED VIA GIT,
not from memory:

  E0  DECLARED BEFORE THE RUN
      steps ①–⑦ (trades ≥30, expectation>0 and p<0.05 in the author's window
      and outside it). CHECKLIST.md 20.08 15:00 names BOTH instruments —
      lookahead-analysis and recursive-analysis — before the sweep began
      (git: 4d5a937).

  E1  AFTER DATA, CAUSED BY THE RESULT  ← real leakage
      Both instruments were MEASURED from the first harness commit (be77d12,
      20.08 14:42), but which one EXCLUDES was not declared. The published
      funnel (fff3d17, 21.08 10:56) excluded ONLY by lookahead. Exclusion by
      recursion was added AFTER I saw that the strategies that beat the market
      out of sample were NOTankAi_15 (+63 645 298%) and NowoIchimoku1hV2.
      ⚠ Correction to my own note of 21.08 22:41: I wrote "the second detector
      was introduced after the data". Per git this is WRONG — what was
      introduced was not the instrument, but the DECISION about which of the
      declared instruments counts as excluding. Underdetermined
      preregistration, resolved after the result.

  E2  AFTER DATA, SOURCE EXTERNAL (not caused by our result)
      backtest traps from the freqtrade community documentation (traps.py).

  E3  AFTER DATA, SOURCE EXTERNAL
      trade shorter than its own candle (dur_over_candle < 1).

  E4  AFTER DATA, CAUSED BY EXTERNAL REVIEW
      multiplicity correction (Benjamini–Hochberg).

The distinction between E1 and E2/E3 is essential and MUST NOT be collapsed:
E1 — a rule chosen because the result was disliked; E2/E3 — a rule that came
from someone else's document, indifferent to our result. Both are researcher
degrees of freedom, and both are marked. But they are culpable differently.

RUN:  python ledger.py            print summary
      python ledger.py --csv      + LEDGER.csv next to the cards
      python ledger.py --publish  + repo/LEDGER.csv, repo/LEDGER.md and
                                  overwrite the numbers block in repo/README.md
      python ledger.py --verify   verify the README block against recomputation,
                                  exit code 1 on mismatch

WHY --publish AND --verify. The numbers in README used to be typed by hand and
went stale silently: on 21.08 the published block said "571 strategies, 55
clean" when the corpus was 900. An external reader trusts what is published,
not the code. Therefore the block between the markers `<!-- LEDGER:BEGIN -->`
and `<!-- LEDGER:END -->` is MACHINE-GENERATED. A rule without an exit code
does not work.
"""
from __future__ import print_function

import collections
import csv
import glob
import io
import json
import os
import sys
import warnings

# Foreign strategies contain invalid escape sequences; ast raises
# SyntaxWarning about the FOREIGN file. We mute only that.
warnings.filterwarnings("ignore", category=SyntaxWarning)

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import traps as traps_mod
from harness import find_strategies, PASS
from ledger_block import (ALPHA, EPOCHS, GATE_EPOCH, LADDER, bh, bh_population,
                          build, claims, survivors_at)

FOUND = u"FOUND"
BEGIN = u"<!-- LEDGER:BEGIN -->"
END = u"<!-- LEDGER:END -->"

CSV_COLS = ["strategy", "repo", "file", "population", "code_md5", "plan_md5",
            "is_trades", "is_exp", "is_p", "is_market",
            "os_trades", "os_exp", "os_p", "os_total", "os_market",
            "os_avg_pct", "os_ci_low",
            "beats_bh", "lookahead", "recursive", "recursive_kind",
            "traps_n", "traps",
            "dur_over_candle", "dropped_at", "survives_through"]


def where_map():
    w = {}
    root = os.path.join(_ROOT, "repos")
    if not os.path.isdir(root):
        return w
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if os.path.isdir(p):
            for f, n in sorted(find_strategies(p)):
                w.setdefault(n, f)
    return w


def load(population="corpus"):
    rows = []
    for fp in sorted(glob.glob(os.path.join(_ROOT, "results", "*.json"))):
        try:
            r = json.load(io.open(fp, encoding="utf-8"))
        except Exception:
            continue
        if r.get("source") != population:
            continue
        rows.append(r)
    return rows



def ci_low(mean_pct, p_value, n):
    u"""Lower bound of the 95% interval of the average trade, in percent.

    Reconstructed from what freqtrade prints: mean, p-value, and
    number of trades. z is taken from p (two-sided), standard error = |m| / z,
    bound = m - 1.96*se. Normal approximation is acceptable: survivors have from 304
    to 2688 trades.

    ⚠ WHY (E6, 22.08). The ladder required SIGNIFICANCE and did not require
    MAGNITUDE. p = 1e-8 with a microscopic effect is less useful than p = 0.003
    with a stable one. The objection is external, the hole is ours.
    """
    from statistics import NormalDist
    if mean_pct is None or p_value is None or not n:
        return None
    pv = min(max(float(p_value), 1e-300), 0.999999)
    try:
        z = NormalDist().inv_cdf(1.0 - pv / 2.0)
    except Exception:
        return None
    z = min(max(z, 1e-6), 40.0)
    se = abs(mean_pct) / z
    return mean_pct - 1.96 * se


EXTRA_COST_PCT = 0.20   # doubling the cost from 0.1% to 0.2% per side = 0.20 pp/trade


def recursive_kind(node):
    u"""SPLIT TWO DIFFERENT THINGS UNDER ONE LABEL.

    `recursive-analysis` gives "FOUND" in two incomparable cases:
      · REFUSAL  — startup_candle_count=0, the engine did not compute at all. This is
                 a check of the DECLARATION: the author did not say how much
                 warm-up he needs. The defect is real, but NOTHING is measured.
      · DRIFT  — the engine computed and saw that indicator values depend
                 on the amount of supplied history. This is a MEASUREMENT.

    Mixing them means passing off a declaration check as a measurement. Step
    G7 remains one (both reasons disqualify), but the registry stores the kind,
    and the share of each kind is printed. Otherwise the phrase "26 strategies knocked out
    by recursion" reads as found drift, but may turn out to be a formality.
    """
    if not isinstance(node, dict):
        return u""
    if node.get("level") != FOUND:
        return u""
    why = node.get("why") or u""
    if u"REFUSED" in why or u"startup_candle_count" in why:
        return u"refused_no_warmup"
    if u"change" in why or u"%" in why:
        return u"drift_measured"
    return u"other"


def beats_precomputed(b):
    if b.get("total_pct") is None or b.get("market_change_pct") is None:
        return None
    return b["total_pct"] > b["market_change_pct"]


def row_of(r, where):
    u"""One registry row. G10 (multiplicity correction) is filled
    in a second pass: the threshold is computed over the whole population, not per row."""
    a = r["runs"]["in_sample"].get("summary")
    b = r["runs"]["out_sample"].get("summary")
    a = a if isinstance(a, dict) else {}
    b = b if isinstance(b, dict) else {}
    # ⚠ 22.08, totality: it was `tr = ... if p else []`. Did not find the source —
    # the trap list is empty — G8 PASSED. "Did not look" read as "clean",
    # exactly the G9_candle defect. On this corpus it is latent (0 rows out of 895 without
    # source), but the default was flattering. Now ignorance — its own value.
    p = where.get(r["strategy"])
    inspected = p is not None
    tr = traps_mod.flags(traps_mod.inspect(p, r["strategy"])) if inspected else []

    g = collections.OrderedDict()
    g["G0_measured"] = bool(a.get("trades") is not None and b.get("trades") is not None)
    g["G1_trades"] = (a.get("trades") or 0) >= 30
    g["G2_is_pos"] = (a.get("expectancy") or 0) > 0
    g["G3_is_sig"] = (a.get("p_value") if a.get("p_value") is not None else 1) < ALPHA
    g["G4_os_pos"] = (b.get("expectancy") or 0) > 0
    g["G5_os_sig"] = (b.get("p_value") if b.get("p_value") is not None else 1) < ALPHA
    # ⚠⚠ 22.08 EVENING, FOUND BY INDEPENDENT AUDIT. It was `!= FOUND`, i.e.
    # "NOT APPLICABLE" (the check could NOT be performed) was counted as
    # PASSED. Of 72 that reached G6, 49 were not checked; of 14 published
    # survivors, the lookahead detector worked on only TWO.
    #
    # This is THE SAME class as fixed today in G9_candle ("missing field =
    # skip”) and in G8_traps (“source not found = no traps”). The case was
    # fixed twice, the CLASS was not re-enumerated — violating its own sealed
    # rule `feedback_fix_the_class_not_the_case` on the same day it was
    # referenced.
    #
    # Now the gates require a POSITIVE verdict, as G8 and G9 already do:
    # ignorance is not passing.
    g["G6_lookahead"] = r["runs"]["lookahead"]["level"] == PASS
    g["G7_recursive"] = r["runs"]["recursive"]["level"] == PASS
    g["G8_traps"] = inspected and len(tr) == 0   # uninspected does NOT pass
    # ⚠ MISSING FIELD IS NOT “PASSED”. Cards counted before the duration layer
    # appeared contain no field, and `not card.get("intracandle")` silently
    # read as “passed”. Presence ≠ content — the step requires MEASUREMENT.
    g["G9_candle"] = (b.get("dur_over_candle") is not None
                      and not bool(b.get("intracandle")))
    g["G10_fdr"] = None                       # second pass
    lo = ci_low(b.get("avg_profit_pct"), b.get("p_value"), b.get("trades"))
    g["G11_effect"] = bool(lo is not None and (lo - EXTRA_COST_PCT) > 0)
    g["G12_economic"] = bool(beats_precomputed(b))

    lo_ci = ci_low(b.get("avg_profit_pct"), b.get("p_value"), b.get("trades"))
    beats = None
    if b.get("total_pct") is not None and b.get("market_change_pct") is not None:
        beats = b["total_pct"] > b["market_change_pct"]

    return {
        "strategy": r["strategy"], "repo": r.get("repo", ""),
        "file": r.get("file", ""), "population": r.get("source", ""),
        "code_md5": r.get("code_md5", ""), "plan_md5": r.get("plan_md5", ""),
        "is_trades": a.get("trades"), "is_exp": a.get("expectancy"),
        "is_p": a.get("p_value"), "is_market": a.get("market_change_pct"),
        "os_trades": b.get("trades"), "os_exp": b.get("expectancy"),
        "os_p": b.get("p_value"), "os_total": b.get("total_pct"),
        "os_avg_pct": b.get("avg_profit_pct"),
        "os_ci_low": (None if lo_ci is None else round(lo_ci, 4)),
        "os_market": b.get("market_change_pct"), "beats_bh": beats,
        "lookahead": r["runs"]["lookahead"]["level"],
        "recursive": r["runs"]["recursive"]["level"],
        "recursive_kind": recursive_kind(r["runs"]["recursive"]),
        "traps_n": len(tr), "traps": u"; ".join(t[0] for t in tr),
        "dur_over_candle": b.get("dur_over_candle"),
        "gates": g, "dropped_at": "", "survives_through": "",
    }


def finalize(rows):
    u"""Second pass: BH threshold over the entire population, then the culling step."""
    p_out = bh_population(rows)
    thr, k = bh(p_out)
    for r in rows:
        op = r.get("os_p")
        r["gates"]["G10_fdr"] = bool(k and op is not None and op <= thr)
        dropped = ""
        for kname, _e, _d in LADDER:
            if not r["gates"][kname]:
                dropped = kname
                break
        r["dropped_at"] = dropped
        r["survives_through"] = u"all" if not dropped else GATE_EPOCH[dropped]
    return (thr if k else None), len(p_out), k


def n_repos():
    u"""One implementation for two places — in ledger_block. A local copy here has already
    diverged from the truth and printed 3 instead of 53."""
    from ledger_block import n_repos as _n
    return _n(os.path.join(_ROOT, "corpus_sources.json"))


def write_csv(rows, out):
    with io.open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda x: x["strategy"].lower()):
            w.writerow(r)


def rewrite_readme(text, blk):
    if BEGIN not in text or END not in text:
        return None
    head = text.split(BEGIN)[0]
    tail = text.split(END, 1)[1]
    return head + BEGIN + u"\n" + blk + u"\n" + END + tail


def ledger_md(rows, blk):
    u"""LEDGER.md — public explanation of what these numbers mean."""
    surv = survivors_at(rows, "E4")
    L = [
        u"# The ledger",
        u"",
        u"One row per strategy, in [LEDGER.csv](LEDGER.csv). Every count this",
        u"repository publishes is derived from that file, and that file is",
        u"produced by `ledger.py` from the result cards — not typed by hand.",
        u"",
        u"## Why this file exists",
        u"",
        u"On 2026-08-21 an external reviewer read this repository and praised two",
        u"scripts as a strength. Both had been discarded days earlier, and the",
        u"published counts they supported came from a 571-strategy corpus that had",
        u"since grown past 900. Nothing in the repository was lying. The reviewer",
        u"simply had no way to tell which artifacts still stood behind which",
        u"numbers.",
        u"",
        u"So each number now carries four coordinates: **what** was measured, **by",
        u"which code**, **over which corpus**, and **under which set of decisions**.",
        u"The last one is the one usually left out.",
        u"",
        u"## Decision epochs",
        u"",
        u"A rule chosen before the data and a rule chosen after it do not carry the",
        u"same weight, so they are labelled and never merged. The dates come from",
        u"git, not from memory.",
        u"",
        u"| epoch | when the rule was fixed | rules |",
        u"|---|---|---|",
        u"| E0 | **before the sweep** — CHECKLIST.md, 2026-08-20 15:00 (`4d5a937`)"
        u" | trade count, expectancy and p-value in both windows; look-ahead |",
        u"| E1 | **after the results, because of them** | `recursive-analysis`"
        u" promoted from *reported* to *excluding* |",
        u"| E2 | after, from an outside source | the freqtrade community's"
        u" backtesting traps |",
        u"| E3 | after, from an outside source | trades shorter than their own"
        u" candle |",
        u"| E4 | after, prompted by an external review | Benjamini-Hochberg FDR |",
        u"",
        u"**E1 is the one to be suspicious of, and it is mine.** Both bias",
        u"detectors ran on every strategy from the first commit of the harness",
        u"(`be77d12`, 2026-08-20 14:42), and both were named in the checklist",
        u"published before the sweep. What was *not* fixed in advance was which of",
        u"them excludes a strategy from the headline. The published funnel",
        u"(`fff3d17`) excluded on look-ahead only. Exclusion on recursion was added",
        u"after I saw that the strategies beating buy-and-hold out of sample were",
        u"`NOTankAi_15` at +63,645,298% and `NowoIchimoku1hV2`.",
        u"",
        u"That is not a detector invented to kill an inconvenient result — the",
        u"detector predates the result by a day. It is a **degree of freedom left",
        u"open in the pre-registration and closed after seeing the data**, which is",
        u"a smaller sin and still a real one. Both counts are published below, in",
        u"the order the decisions were made. E2 and E3 are post-data too, but they",
        u"came from documents indifferent to our result; a weaker objection, and",
        u"still marked.",
        u"",
        u"## The numbers",
        u"",
        blk,
        u"",
        u"## Reading the ladder",
        u"",
        u"Each line is the same population passing one more gate. `G0_measured` is",
        u"not a quality filter — it counts the strategies that produced numbers in",
        u"both windows at all. The largest single drop is not any bias detector: it",
        u"is `G2_is_pos`, strategies whose expectancy is negative in the window",
        u"their own author chose.",
        u"",
        u"`G9_candle` **fails a strategy whose trade duration was never measured**",
        u"rather than passing it. Cards computed before the duration layer existed",
        u"carry no such field, and `not card.get(\"intracandle\")` would have quietly",
        u"read as *passed*. Absence of a flag is not absence of the defect.",
        u"",
        u"## What a row does not tell you",
        u"",
        u"That a strategy survives every gate is not a claim that it makes money.",
        u"It is a claim that this pipeline could not show that it does not. The last",
        u"column of the epoch table — how many survivors beat buy-and-hold on the",
        u"same pairs over the same window — is the one that matters, and the one",
        u"nearly every published backtest omits.",
        u"",
        u"Survivors under the full rule set: **%d**." % len(surv),
        u"",
    ]
    return u"\n".join(L) + u"\n"


def arg_population():
    u"""Populations are NEVER mixed in one denominator: five strategies,
    manually chosen by me, must not enter the corpus denominator."""
    for a in sys.argv[1:]:
        if a.startswith("--pop="):
            return a.split("=", 1)[1]
    return "corpus"


def main():
    where = where_map()
    pop = arg_population()
    rows_raw = load(pop)
    if not rows_raw:
        print(u"population %r is empty — nothing to count" % pop)
        return 1
    rows = [row_of(r, where) for r in rows_raw]
    thr, n_bh, k_bh = finalize(rows)

    code = collections.Counter(x["code_md5"] for x in rows)
    plan = collections.Counter(x["plan_md5"] for x in rows)
    homogeneous = len(code) <= 1 and len(plan) <= 1

    print(u"REGISTRY — one row per strategy")
    print(u"=" * 68)
    print(u"POPULATION: %s (mixing populations is forbidden)" % pop)
    print(u"BY CODE:  %s" % u", ".join(u"%s x%d" % (c or u"-", n)
                                     for c, n in code.most_common(3)))
    print(u"CORPUS: %s" % u", ".join(u"%s x%d" % (c or u"-", n)
                                     for c, n in plan.most_common(3)))
    print(u"ROWS:  %d   repositories: %d" % (len(rows), n_repos()))
    print(u"BH:     threshold %s over %d checks, rejected %d"
          % ((u"%.3e" % thr) if thr else u"none", n_bh, k_bh))
    nodur = sum(1 for x in rows
                if x["gates"]["G0_measured"] and x["dur_over_candle"] is None)
    print(u"WITHOUT ⑨:  %d rows counted before the duration layer appeared" % nodur)
    if not homogeneous:
        print(u"⚠ rows counted by DIFFERENT code/plan versions — registry")
        print(u"  is heterogeneous; cannot publish the total until recomputation")
    print()

    print(u"LADDER — where exactly the corpus descends")
    print(u"-" * 68)
    alive = rows
    for kname, ep, desc in LADDER:
        p = [r for r in alive if r["gates"][kname]]
        print(u"  %-13s %s  %-44s %4d -> %4d" % (kname, ep, desc, len(alive), len(p)))
        alive = p
    print()

    g7 = [r for r in rows if r["dropped_at"] == "G7_recursive"]
    if g7:
        kinds = collections.Counter(r["recursive_kind"] for r in g7)
        print(u"WHAT EXACTLY KNOCKED OUT ON G7 (epoch E1) — %d strategies" % len(g7))
        print(u"-" * 68)
        for k, n in kinds.most_common():
            what = {u"refused_no_warmup":
                    u"engine REFUSED to count: warm-up not declared (check "
                    u"DECLARATIONS, nothing measured)",
                    u"drift_measured":
                    u"indicator drift MEASURED"}.get(k, k or u"without reason")
            print(u"  %4d  %s" % (n, what))
        print()

    print(u"SURVIVORS BY EPOCH — one number per decision set")
    print(u"-" * 68)
    for ep in EPOCHS:
        s = survivors_at(rows, ep)
        beat = [r for r in s if r["beats_bh"]]
        print(u"  through %s inclusive:  survivors %4d   beat the market %3d"
              % (ep, len(s), len(beat)))
        if beat and len(beat) <= 5:
            for r in beat:
                print(u"        %-30s out-of-sample %+.1f%% vs market %+.1f%%"
                      % (r["strategy"][:30], r["os_total"] or 0,
                         r["os_market"] or 0))
    print()
    print(u"READ AS: the difference between rows is NOT different measurements, but")
    print(u"one measurement under different decision sets. E0 is declared before data;")
    print(u"E1 is chosen AFTER and BECAUSE of the result; E2-E4 came from outside later.")

    blk = build(rows, n_repos())
    repo_dir = os.path.join(_ROOT, "repo")

    if "--csv" in sys.argv:
        out = os.path.join(_ROOT, "LEDGER.csv")
        write_csv(rows, out)
        print(u"\nrecorded %s (%d rows)" % (out, len(rows)))

    if "--publish" in sys.argv:
        if pop != "corpus":
            print(u"\nREFUSAL TO PUBLISH: README contains CORPUS numbers, not")
            print(u"population %r. Five manual parses are not a population." % pop)
            return 1
        if not homogeneous:
            print(u"\nREFUSAL TO PUBLISH: registry is heterogeneous by code or corpus.")
            print(u"First recompute everything with one harness version.")
            return 1
        write_csv(rows, os.path.join(repo_dir, "LEDGER.csv"))
        # class of each claim — by machine, by file, not by paragraph
        with io.open(os.path.join(repo_dir, "CLAIMS.csv"), "w",
                     encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["claim", "value", "class", "epochs_required", "source"])
            for row in claims(rows, n_repos()):
                w.writerow(row)
        print(u"recorded CLAIMS.csv — class of each number")
        io.open(os.path.join(repo_dir, "LEDGER.md"), "w",
                encoding="utf-8").write(ledger_md(rows, blk))
        rp = os.path.join(repo_dir, "README.md")
        new = rewrite_readme(io.open(rp, encoding="utf-8").read(), blk)
        if new is None:
            print(u"\n⚠ README has no registry markers — block NOT inserted")
            return 1
        io.open(rp, "w", encoding="utf-8").write(new)
        print(u"\npublished: LEDGER.csv, LEDGER.md, number block in README")

    if "--verify" in sys.argv:
        rp = os.path.join(repo_dir, "README.md")
        txt = io.open(rp, encoding="utf-8").read()
        if BEGIN not in txt or END not in txt:
            print(u"\nREFUSAL: README has no registry markers")
            return 1
        have = txt.split(BEGIN, 1)[1].split(END, 1)[0].strip()
        if have != blk.strip():
            print(u"\nMISMATCH: numbers in README do not match recomputation")
            hl, wl = have.splitlines(), blk.strip().splitlines()
            for i in range(max(len(hl), len(wl))):
                a = hl[i] if i < len(hl) else u"(no row)"
                b = wl[i] if i < len(wl) else u"(no row)"
                if a != b:
                    print(u"  README: %s" % a)
                    print(u"  registry: %s" % b)
            return 1
        print(u"\nnumbers in README match the registry")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
