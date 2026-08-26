# -*- coding: utf-8 -*-
u"""ledger_block — the ONLY place where numbers become text.

WHY A SEPARATE FILE. The number block in README must be verifiable on a CLEAN
machine with no `results/` cards, no `repos/` clones, no freqtrade.
So block assembly is separated from the source: `ledger.py` feeds it cards,
`verify_ledger.py` — the published LEDGER.csv. There is ONE implementation, and this
matters: two independent implementations of "the same thing" diverge silently,
and the divergence is only detected by someone reading both.

No pandas, no freqtrade, no network calls here — only stdlib, otherwise
the check won't pass in CI and the rule becomes prose again.

LADDER IS MONOTONIC BY EPOCHS. Steps go E0,E0,…,E1,E2,E3,E4 — epoch never
decreases. It follows that to reconstruct the whole picture, ONE
field `dropped_at` suffices: a strategy is alive until its step and dead on it and after.
That's why the CSV carries one field, not eleven booleans.
"""
from __future__ import print_function

LADDER = [
    ("G0_measured",   "E0", u"both halves computed"),
    ("G1_trades",     "E0", u"trades >= 30 in author's window"),
    ("G2_is_pos",     "E0", u"expectancy > 0 in author's window"),
    ("G3_is_sig",     "E0", u"p < 0.05 in author's window"),
    ("G4_os_pos",     "E0", u"expectancy > 0 out-of-sample"),
    ("G5_os_sig",     "E0", u"p < 0.05 out of sample"),
    ("G6_lookahead",  "E0", u"no lookahead"),
    ("G7_recursive",  "E1", u"indicators do not depend on history length"),
    ("G8_traps",      "E2", u"no community traps"),
    ("G9_candle",     "E3", u"duration MEASURED and not shorter than a candle"),
    ("G10_fdr",       "E4", u"out-of-sample p passes the Benjamini-Hochberg threshold"),
    # ── E6: effect size and economic gate (22.08) ──────────────────
    # A hole named by external review and confirmed by the count: the ladder
    # required SIGNIFICANCE and did not require MAGNITUDE. p=1e-8 with a microscopic
    # effect is more useless than p=0.003 with a robust one. G11 requires that
    # the lower bound of the 95% interval of the average trade was positive AFTER
    # doubled costs; G12 — that the strategy beat the alternative.
    ("G11_effect",    "E6", u"lower bound of 95% CI of average trade > 0 at 2x cost"),
    ("G12_economic",  "E6", u"beat \"buy and hold\" on the same pairs"),
]
EPOCHS = ["E0", "E1", "E2", "E3", "E4", "E5", "E6"]
GATE_EPOCH = dict((k, e) for k, e, _d in LADDER)

def beats(r):
    u"""Did it beat "buy and hold": True / False / None.

    ⚠ 22.08, TOTALITY property (totality.py). Previously `r.get("beats_bh")`
    stood directly in the condition: in 399 of 895 rows the field is EMPTY —
    the strategy was not measured — and empty was silently read as "did NOT beat".
    "Don't know" collapsed into "no". None of the 399 reaches the counting point,
    so published numbers did not change, but a partial function WAS here. Now
    unknown is a separate value.
    """
    v = r.get("beats_bh")
    # ⚠ input comes in TWO kinds: from CSV — as a string, from ledger.py in memory —
    # as a real bool. The first version knew only the string and crashed on bool:
    # while fixing partiality, I introduced a new one. Totality = a defined answer for
    # EACH kind of input, not just the expected one.
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    v = ("%s" % v).strip()
    if v in (u"True", u"1", u"true"):
        return True
    if v in (u"False", u"0", u"false"):
        return False
    return None


def n_beat(rows):
    u"""We count only KNOWING. Not knowing is not added to either side."""
    return sum(1 for r in rows if beats(r) is True)


def n_beat_unknown(rows):
    return sum(1 for r in rows if beats(r) is None)


GATE_ORDER = dict((k, i) for i, (k, _e, _d) in enumerate(LADDER))
ALPHA = 0.05


def bh(pvals, alpha=ALPHA):
    u"""Benjamini–Hochberg. Returns (threshold, how many rejected).

    Repeated here rather than imported from multiplicity.py for exactly one
    reason: this module must work in CI without the rest of the tree. So that
    the copy does not silently diverge from the original, `multiplicity.py`
    imports IT, not the other way around — one source, dependency direction
    declared.
    """
    n = len(pvals)
    if not n:
        return 0.0, 0
    s = sorted(pvals)
    k = 0
    for i, p in enumerate(s, 1):
        if p <= alpha * i / n:
            k = i
    return (s[k - 1] if k else 0.0), k



def by(pvals, alpha=ALPHA):
    u"""Benjamin–Yekutieli: FDR under ARBITRARY dependence.

    WHY ADDED (22.08, after external review). BH holds FDR under
    independence or positive dependence of a certain class. In our
    corpus 65% are copies, i.e. the dependence structure is arbitrary, and the BH
    guarantee formally does not apply. We recorded this limitation in multiplicity.py
    already on 21.08, but recording a limitation is not the same as removing it.

    BY removes it: same move, threshold divided by the harmonic number H_n. At the cost
    of strictness — for n=81 this is a 4.98 times stricter threshold.

    ⚠ THIS IS AN E5-ERA RULE: added AFTER the data, based on an external remark.
    It is NOT introduced as a ladder step — it changes nothing (all six
    survivors pass it too), and introducing a step to get the same answer
    would mean increasing degrees of freedom needlessly. Printed as a robustness
    check next to BH.
    """
    n = len(pvals)
    if not n:
        return 0.0, 0
    h = sum(1.0 / i for i in range(1, n + 1))
    s = sorted(pvals)
    k = 0
    for i, v in enumerate(s, 1):
        if v <= alpha * i / (n * h):
            k = i
    return (s[k - 1] if k else 0.0), k


def alive_at(row, gate):
    u"""Whether the row survived UP TO this step (without having passed it yet)."""
    d = row.get("dropped_at") or ""
    return (not d) or GATE_ORDER[d] >= GATE_ORDER[gate]


def passed(row, gate):
    u"""Whether the row passed this step."""
    d = row.get("dropped_at") or ""
    return (not d) or GATE_ORDER[d] > GATE_ORDER[gate]


def survivors_at(rows, epoch):
    u"""Who would have survived if applying ONLY rules of epochs <= epoch."""
    lim = EPOCHS.index(epoch)
    out = []
    for r in rows:
        d = r.get("dropped_at") or ""
        if not d or EPOCHS.index(GATE_EPOCH[d]) > lim:
            out.append(r)
    return out


def bh_population(rows):
    u"""Out-of-sample p-values for multiplicity correction.

    Same population as in multiplicity.py: trades >= 30, expectation and
    significance in the author's window, positive expectation outside it. Computed from
    row fields, so reproducible from the published CSV."""
    p = []
    for r in rows:
        try:
            if (r.get("is_trades") or 0) < 30:
                continue
            if (r.get("is_exp") or 0) <= 0:
                continue
            ip = r.get("is_p")
            op = r.get("os_p")
            if ip is None or op is None or ip >= ALPHA:
                continue
            if (r.get("os_exp") or 0) <= 0:
                continue
            p.append(op)
        except TypeError:
            continue
    return p


def n_repos(path):
    u"""How many repositories entered the sweep.

    ⚠ DEFECT 22.08, published. Counted `len(src.keys())`, while
    `corpus_sources.json` is a dictionary of three keys, where the repository list
    sits inside `repos`. README got "repositories swept 3" instead of 53.

    The `verify_ledger` check did NOT CATCH this, and could not: both sides counted
    with the same wrong formula. Reconciling two quantities derived from a
    common source proves agreement, not correctness. Hence the second
    guard below — a plausibility check independent of the formula.
    """
    import io as _io
    import json as _json
    try:
        src = _json.load(_io.open(path, encoding="utf-8"))
    except Exception:
        return 0
    if isinstance(src, dict):
        n = len(src["repos"]) if isinstance(src.get("repos"), list) else len(src)
    else:
        n = len(src)
    return n


def repos_plausible(n_repo, n_rows):
    u"""Guard independent of the formula: this many strategies from that many
    repositories is physically implausible. Returns complaint text or None."""
    if n_repo <= 0:
        return u"repositories 0 at %d strategies" % n_rows
    if n_rows and n_rows / float(n_repo) > 200:
        return (u"%d strategies from %d repositories — %.0f per repository, "
                u"looks like a counting error" % (n_rows, n_repo, n_rows / float(n_repo)))
    return None



# ── assertion class: machine-readable, not prose ──────────────────────────────
# External review 22.08: "separate descriptive / exploratory / confirmatory
# MACHINE-READABLY, not just in words." Fair: until now the class lived in text,
# and text has no return code. Here every published number carries its own
# the class and the list of epochs without which it does not exist.
DESCRIPTIVE = "descriptive"      # a count of what exists; requires no decisions
REPAIR = "repair-adjusted"       # rule redefined AFTER data
EXPLORATORY = "exploratory"      # rule arrived after data from outside
PREREG = "pre-registered"        # rule declared BEFORE the run


def claims(rows, n_repo):
    u"""Published assertions with their class. One line — one number."""
    thr, k_bh = bh(bh_population(rows))
    thr_by, k_by = by(bh_population(rows))
    e0 = survivors_at(rows, "E0")
    e4 = survivors_at(rows, "E4")
    held = sum(1 for r in e4
               if r.get("os_p") is not None and r["os_p"] <= thr_by)
    out = [
        ("strategies in corpus", len(rows), DESCRIPTIVE, "-",
         "census of what could be found and loaded"),
        ("repositories swept", n_repo, DESCRIPTIVE, "-",
         "corpus_sources.json"),
        ("negative in the author's own window", 
         sum(1 for r in rows if (r.get("dropped_at") or "") == "G2_is_pos"),
         DESCRIPTIVE, "-", "ladder gate G2"),
        ("survivors under pre-registered rules", len(e0), PREREG, "E0",
         "CHECKLIST.md 2026-08-20 15:00, commit 4d5a937"),
        # ⚠ 22.08: both lines were named identically «of those, beat buy-and-hold».
        # A consumer reading the table by key silently lost one of them.
        # The key of a machine table must be unique — otherwise it is not machine-readable.
        ("beat buy-and-hold under pre-registered rules",
         n_beat(e0), PREREG, "E0",
         "freqtrade Market change"),
        ("survivors under the full rule set", len(e4), REPAIR, "E0+E1+E2+E3+E4",
         "E1 fixed after the data; see LEDGER.md"),
        ("beat buy-and-hold under the full rule set",
         n_beat(e4), REPAIR, "E0+E1+E2+E3+E4",
         "freqtrade Market change"),
        ("BH rejections", k_bh, EXPLORATORY, "E4",
         "multiplicity added after external review"),
        ("BY rejections (arbitrary dependence)", k_by, EXPLORATORY, "E5",
         "added 2026-08-22 after external review"),
        ("survivors still clearing BY", held, EXPLORATORY, "E5",
         "robustness of the repair-adjusted result"),
    ]
    return out


def build(rows, n_repo):
    u"""That very block that lies in the README between markers."""
    codes = sorted(set(r.get("code_md5") or "" for r in rows))
    plans = sorted(set(r.get("plan_md5") or "" for r in rows))
    thr, k_bh = bh(bh_population(rows))
    n_bh = len(bh_population(rows))

    L = [u"```"]
    L.append(u"generated by ledger.py — do not edit by hand")
    L.append(u"harness code md5   %s%s"
             % (codes[0] if codes else u"-",
                u"" if len(codes) <= 1 else u"   MIXED (%d versions)" % len(codes)))
    L.append(u"corpus plan md5    %s%s"
             % (plans[0] if plans else u"-",
                u"" if len(plans) <= 1 else u"   MIXED (%d versions)" % len(plans)))
    bad = repos_plausible(n_repo, len(rows))
    if bad:
        L.append(u"repositories swept   %d   ⚠ SUSPECT: %s" % (n_repo, bad))
    else:
        L.append(u"repositories swept   %d" % n_repo)
    L.append(u"strategies in ledger %d" % len(rows))
    L.append(u"")
    L.append(u"the ladder, and where the corpus leaves it")
    for kname, ep, _d in LADDER:
        a = sum(1 for r in rows if alive_at(r, kname))
        p = sum(1 for r in rows if passed(r, kname))
        L.append(u"  %-13s %s  %4d -> %4d" % (kname, ep, a, p))
    L.append(u"")
    L.append(u"survivors under each decision set")
    for ep in EPOCHS:
        s = survivors_at(rows, ep)
        beat, unk = n_beat(s), n_beat_unknown(s)
        L.append(u"  rules declared up to %s   survivors %4d   beat buy-and-hold %3d%s"
                 % (ep, len(s), beat,
                    u"   (unknown %d)" % unk if unk else u""))
    L.append(u"")
    L.append(u"Benjamini-Hochberg threshold %s over %d tests, %d rejected"
             % ((u"%.3e" % thr) if k_bh else u"none", n_bh, k_bh))
    thr_by, k_by = by(bh_population(rows))
    surv_e4 = survivors_at(rows, "E4")
    held = sum(1 for r in surv_e4
               if r.get("os_p") is not None and r["os_p"] <= thr_by)
    e6 = survivors_at(rows, "E6")
    L.append(u"")
    L.append(u"PRIMARY ENDPOINT — survivors that beat buy-and-hold, frozen rule")
    L.append(u"  %d of %d eligible = %.2f%%"
             % (len(e6), len([r for r in rows if (r.get("dropped_at") or "") not in
                              ("G0_measured", "G1_trades")]),
                100.0 * len(e6) / max(1, len([r for r in rows
                    if (r.get("dropped_at") or "") not in ("G0_measured", "G1_trades")]))))
    L.append(u"")
    L.append(u"Benjamini-Yekutieli  threshold %s, %d rejected  "
             u"(arbitrary dependence; %d of %d survivors still clear it)"
             % ((u"%.3e" % thr_by) if k_by else u"none", k_by,
                held, len(surv_e4)))
    L.append(u"```")
    return u"\n".join(L)
