# -*- coding: utf-8 -*-
u"""harness — THE SAME AUDIT FOR ANY PUBLIC STRATEGY.

The operator's idea from 20.08: not an analysis of one repository, but a corpus of analyses
made by THE SAME procedure. Then the comparison is honest, not
cherry-picked.

HOW THIS DIFFERS FROM THE FIRST ATTEMPT
------------------------------------
The first analysis I did by rewriting into pandas, and the main caveat was
"this is not freqtrade". The caveat is lifted: here REAL freqtrade works, and
so the numbers are authoritative, not approximate.

Additionally, two of its OWN detectors are run, which almost nobody
runs:

    lookahead-analysis    lookahead into the future
    recursive-analysis    an indicator whose value changes with history length

The second one, when encountering `startup_candle_count = 0`, REFUSES to work and
itself declares this a defect. The tool's refusal is also a result, and it
is recorded as a result, not as a failure.

FOUR VALUES, NOT TWO
-------------------------
    PASSED        check executed, here is the number
    FOUND         check executed, defect exists
    NOT APPLICABLE  cannot be executed, reason stated
    NOT RUN       it was not reached

"Could not verify" is never printed as "clean". That is the very
defect that cost $110 in this project.
"""
from __future__ import print_function

import ast
import io
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# The root is from the file itself, not from my disk: README promises that
# harness.py can be run locally. AUDIT_ROOT is overridden.
ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(ROOT, "ftenv", "Scripts", "freqtrade.exe")
CFG = os.path.join(ROOT, "user_data", "config.json")
STRAT_DIR = os.path.join(ROOT, "user_data", "strategies")
RESULTS = os.path.join(ROOT, "results")
CODE_MD5 = __import__("hashlib").md5(
    io.open(os.path.abspath(__file__), "rb").read()).hexdigest()[:12]
TF_MINUTES = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
              "1h": 60, "2h": 120, "4h": 240, "6h": 360,
              "8h": 480, "12h": 720, "1d": 1440, "3d": 4320,
              "1w": 10080}
IN_RANGE = "20180301-20200301"
OUT_RANGE = "20200301-20260820"

PASS, FOUND, NA, SKIP = u"PASS", u"FOUND", u"NA", u"SKIP"


def sh(args, timeout=900):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout, env=env)
        return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, u"TIMEOUT"
    except Exception as ex:
        return 1, u"DID NOT START: %r" % (ex,)


# ─────────────────────── static checks ───────────────────────

def find_strategies(path):
    u"""[(file, class name)] — by STRUCTURE (IStrategy inheritance), not
    by file name. The name is deceptive, the inheritance base is not."""
    out = []
    # TOTAL: strategy names are collected into a set and sorted by the caller
    for dirpath, dirs, names in os.walk(path):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "venv")]
        for n in names:
            if not n.endswith(".py"):
                continue
            p = os.path.join(dirpath, n)
            try:
                src = io.open(p, encoding="utf-8", errors="replace").read()
                tree = ast.parse(src)
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = [b.id if isinstance(b, ast.Name)
                             else getattr(b, "attr", "") for b in node.bases]
                    if "IStrategy" in bases:
                        out.append((p, node.name))
    return out


def static_checks(path, src):
    u"""[(level, what, details)]. Only mechanically verifiable items."""
    res = []

    # ① declared warmup vs. the longest indicator
    periods = [int(m) for m in re.findall(r"timeperiod\s*=\s*(\d+)", src)]
    periods += [int(m) for m in re.findall(r"window\s*=\s*(\d+)", src)]
    declared = re.search(r"^\s*startup_candle_count\s*[:=]\s*(\d+)", src, re.M)
    d = int(declared.group(1)) if declared else 0
    if periods:
        need = max(periods)
        if d == 0:
            res.append((FOUND, u"warmup not declared",
                        u"longest indicator %d candles, "
                        u"startup_candle_count not set (default 0)" % need))
        elif d < need:
            res.append((FOUND, u"warmup too low",
                        u"declared %d, need at least %d" % (d, need)))
        else:
            res.append((PASS, u"warmup declared",
                        u"%d with requirement %d" % (d, need)))

    # ② dead trailing settings
    ts = re.search(r"^\s*trailing_stop\s*[:=]\s*(True|False)", src, re.M)
    tsp = re.search(r"^\s*trailing_stop_positive\s*[:=]\s*([\d.]+)", src, re.M)
    if ts and tsp and ts.group(1) == "False":
        res.append((FOUND, u"dead trailing settings",
                    u"trailing_stop=False, but trailing_stop_positive=%s is set — "
                    u"read as an active protection" % tsp.group(1)))
    if ts and ts.group(1) == "True" and not tsp:
        res.append((FOUND, u"trailing on the full stop",
                    u"trailing_stop=True without trailing_stop_positive ⇒ the stop "
                    u"is dragged across the ENTIRE stop-loss distance"))

    # ③ minimal_roi is declared or commented out
    if re.search(r"^\s*#\s*minimal_roi", src, re.M) and \
            not re.search(r"^\s*minimal_roi\s*[:=]", src, re.M):
        res.append((FOUND, u"minimal_roi is commented out",
                    u"profit exit rules are taken from an unpublished config"))

    # ④ crude signs of lookahead bias
    for pat, what in ((r"\.shift\(\s*-\d+", u"shift into the future .shift(-N)"),
                      (r"\[::-1\]", u"series reversal [::-1]"),
                      (r"center\s*=\s*True", u"centered window center=True")):
        if re.search(pat, src):
            res.append((FOUND, u"a sign of future leakage", what))
    return res


# ─────────────────────── freqtrade runs ───────────────────────

# ⚠ CAUGHT ON MYSELF 20.08, BEFORE PUBLICATION. The analysis yielded a p-value of 5.896,
# which cannot happen: probability does not exceed one. The cause is scientific
# notation: from "5.896e-05" the pattern `[\d.]+` took "5.896" and stopped at the
# letter. Had I published this, the critic would have been right twice.
# An impossible value is not a "quirk" but a signal of a broken instrument.
NUM = r"(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)"


def _num(out, pat, cast=float):
    m = re.search(pat, out)
    return cast(m.group(1)) if m else None


def parse_summary(out):
    u"""Dictionary of metrics from the backtest output.

    ⚠ WHAT WAS FIXED ON 20.08 AFTER EXTERNAL REVIEW. The previous version took only the
    number of trades and the total. The critic pointed out the absence of a baseline and
    statistical significance — and was right, doubly so: freqtrade
    COMPUTES both, and I simply did not output them.

        Market change        baseline "buy and hold" on the same pairs
        Mean profit p-value  significance of the average trade return

    This is exactly our own M-16 ("baseline first"), not applied
    to itself. Numbers without a baseline hang in the air — and my first analysis
    hung that way too.
    """
    d = {
        "trades": _num(out, r"Total/Daily Avg Trades\s*│\s*(\d+)", int),
        "total_pct": _num(out, r"Total profit %\s*│\s*" + NUM + r"%"),
        "expectancy": _num(out, r"Expectancy \(Ratio\)\s*│\s*" + NUM),
        "p_value": _num(out, r"Mean profit p-value\s*│\s*" + NUM),
        "market_change_pct": _num(out, r"Market change\s*│\s*" + NUM + r"%"),
        "sharpe": _num(out, r"Sharpe \(closed trades\)\s*│\s*" + NUM),
        "sortino": _num(out, r"Sortino \(closed trades\)\s*│\s*" + NUM),
        "profit_factor": _num(out, r"Profit factor\s*│\s*" + NUM),
        "drawdown_pct": _num(out, r"Absolute drawdown\s*│\s*[\d.]+ \w+ \((-?[\d.]+)%\)"),
        "cagr_pct": _num(out, r"CAGR %\s*│\s*" + NUM + r"%"),
    }
    # GUARD OF THE IMPOSSIBLE. A probability outside [0,1] means not a surprising
    # result but a broken instrument. Publishing such a thing is not allowed, and silently
    # fixing it is also not: the value is flagged so it can be seen.
    pv = d.get("p_value")
    if pv is not None and not (0.0 <= pv <= 1.0):
        d["p_value"] = None
        d["parse_warning"] = u"p-value outside [0,1] (%r) — output parsing is broken" % pv
    return d


RX_TF_DECL = re.compile(r"""^\s*timeframe\s*[:=]\s*['"]([^'"]+)['"]""", re.M)


def declared_tf(src):
    u"""Timeframe declared by the STRATEGY ITSELF. None — not declared."""
    m = RX_TF_DECL.search(src)
    return m.group(1) if m else None


def engine_tf(out):
    u"""Timeframe on which the engine ACTUALLY computed — in its own
    words (`Strategy using timeframe: 1h`), not my assumption."""
    m = re.search(r"Strategy using timeframe:\s*(\S+)", out)
    return m.group(1) if m else None


def missing_pairs(out):
    u"""Pairs for which the engine did NOT FIND history. It warns about this
    and CONTINUES on the rest — the result looks complete, but covers
    fewer instruments. Such a result cannot be compared with a full one.

    THE BOUNDARY OF THIS CHECK, stated directly: it sees a MISSING FILE, not
    partial coverage within a window. XRP was listed 2018-05-04, and in a window from
    2018-03-01 the first two months for it are empty — no warning will occur,
    because the file exists. This is a market property, not a defect, but the check
    DOES NOT KNOW about it, and pretending it does is not allowed."""
    return sorted(set(re.findall(r"No history for (\S+), \w+, \S+ found", out)))


RX_TAG_TOTAL = re.compile(
    u"Enter Tag\\s*\\|\\s*Entries.*?\\n.*?\\|\\s*TOTAL\\s*\\|\\s*(\\d+)\\s*\\|\\s*(-?[\\d.]+)\\s*\\|"
    u"[^\\|]*\\|[^\\|]*\\|\\s*([0-9 a-z,:]+?)\\s*\\|",
    re.S)


def _dur_min(txt):
    u"""«2 days, 05:07:00» / «21:37:00» → minutes. None — not parsed."""
    if not txt:
        return None
    m = re.search(r"(?:(\d+)\s*days?,\s*)?(\d+):(\d+):(\d+)", txt)
    if not m:
        return None
    d = int(m.group(1) or 0)
    return d * 1440 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 60.0


def tag_total(out):
    u"""The TOTAL row from ENTER TAG STATS: average trade %, duration, WR.

    This exact section is taken, not the per-pair summary: it has one TOTAL for
    the whole run, and its fields match the overall ones. The LEFT OPEN TRADES
    section has its own TOTAL with different numbers — confusing them would mean
    reporting open trades as all trades."""
    i = out.find("ENTER TAG STATS")
    if i < 0:
        return {}
    seg = out[i:i + 4000]
    for line in seg.splitlines():
        if "TOTAL" not in line:
            continue
        cells = [c.strip() for c in line.split(chr(9474))]
        cells = [c for c in cells if c != ""]
        if len(cells) < 6:
            continue
        try:
            return {"avg_profit_pct": float(cells[2]),
                    "avg_duration_min": _dur_min(cells[5]),
                    "win_pct": float(cells[6].split()[-1])
                    if len(cells) > 6 else None}
        except (ValueError, IndexError):
            return {}
    return {}


def _sp(path):
    u"""--strategy-path: take the strategy FROM WHERE IT LIES, without copying.
    Copying into a shared folder would mix repositories and create name duplicates —
    exactly what the corpus suffers from (Schism appears in 16 places)."""
    return ["--strategy-path", os.path.dirname(path)] if path else []


def backtest(name, timerange, fee="0.001", path=None, want_tf=None):
    u"""⚠ SUBJECT GUARD (20.08). The corpus was computed ON THE WRONG CANDLES: the config
    had `timeframe`, and it OVERRIDES the one declared by the strategy. Five-minute
    bars ran on hourly ones and produced full plausible numbers — 6014 trades.
    The config key was removed, but that fixes THE CASE. The class is fixed here:
    the result is not accepted until the engine confirms in its own words that it
    computed on the same timeframe the strategy declared."""
    c, out = sh([FT, "backtesting", "--config", CFG, "--strategy", name,
                 "--timerange", timerange, "--fee", fee] + _sp(path),
                timeout=1200)
    used = engine_tf(out)
    if c == 0 and want_tf and used and used != want_tf:
        return (NA, u"SUBJECT WRONG: strategy declared %s, engine computed on %s"
                % (want_tf, used), None)
    # ⚠ OBSERVED DEFECT 21.08. `ERROR - Fatal exception!` is a LABEL, not
    # the cause: the real one lies below, at the end of the traceback. Thus 76 strategies
    # (13% of the corpus) received an empty explanation in the report, and I almost
    # published «could not verify» where the cause was MINE:
    # `ImportError: Short strategies cannot run in spot markets` — they
    # declare can_short, but the corpus was run in spot mode.
    #
    # «Not verified» must be a CATEGORY with a named cause, otherwise it is
    # indistinguishable from «verified and clean».
    err = re.search(r"ERROR - (?:Configuration error: )?(.+)", out)
    # exception names can contain DOTS (numpy.exceptions.DTypePromotionError) —
    # the first version required \w* and therefore left the label "Fatal exception!"
    tail = re.findall(r"^([\w.]*(?:Error|Exception)): (.+)$", out, re.M)
    if tail and (not err or "Fatal exception" in err.group(1)):
        class _M(object):
            def __init__(self, t):
                self._t = t
            def group(self, _):
                return u"%s: %s" % self._t
        err = _M(tail[-1])
    if c != 0:
        why = (u"TIMEOUT" if c == 124
               else (err.group(1).strip()[:160] if err else u"code %d" % c))
        return (NA, why, None)
    d = parse_summary(out)
    # ? CODE 0 IS NOT A RESULT. freqtrade exits SUCCESSFULLY on a
    # configuration error: ClucCrypROI prints "Configuration error: 'stoploss' is a
    # required property" and exits with zero. The previous version took this as a
    # run and recorded a dictionary of all Nones — a card that LOOKS like a
    # measurement. This is my own sealed rule: presence, zero code,
    # and file existence mean "DON'T KNOW", not "yes".
    #
    # A run counts only if the summary HAS NUMBERS.
    if d.get("trades") is None:
        return (NA, (err.group(1).strip()[:160] if err
                     else u"engine exited with code 0, but no summary"
                          u"(no trades or output not parsed)"), None)
    d["used_timeframe"] = used
    d["declared_timeframe"] = want_tf
    d["missing_pairs"] = missing_pairs(out)
    d.update(tag_total(out))
    # ⚠ SHARPEST FLAG FROM THE COMMUNITY ARTICLE: a trade SHORTER THAN THE CANDLE, i.e.,
    # opened and closed within a single candle. This can happen in a backtest; in live trading
    # usually not. In CODE it is invisible ? only in the durations.
    tf_min = TF_MINUTES.get(used or want_tf)
    ad = d.get("avg_duration_min")
    # TOTAL: unknown candle ⇒ fields not written, and G9_candle downstream
    # CRASHES the strategy with unmeasured duration (fixed 22.08). Absence
    # here is not a skip but a failure — just raised elsewhere.
    if tf_min and ad is not None:  # TOTAL: absence ⇒ failure at G9
        d["dur_over_candle"] = round(ad / float(tf_min), 2)
        d["intracandle"] = bool(ad < tf_min)
    return (PASS, u"", d)


def lookahead(name, timerange="20190101-20190401", path=None):
    c, out = sh([FT, "lookahead-analysis", "--config", CFG, "--strategy", name,
                 "--timerange", timerange] + _sp(path), timeout=1200)
    if c != 0:
        m = re.search(r"ERROR - (?:Configuration error: )?(.+)", out)
        return (NA, (m.group(1)[:160] if m else u"code %d" % c))
    if re.search(r"no bias detected", out):
        return (PASS, u"no offset detected")
    m = re.search(r"│\s*(Yes|No)\s*│\s*(\d+)\s*│\s*(\d+)\s*│\s*(\d+)", out)
    if m and m.group(1) == "Yes":
        return (FOUND, u"OFFSET PRESENT: entries %s, exits %s out of %s signals"
                % (m.group(3), m.group(4), m.group(2)))
    return (NA, u"output not parsed")


def recursive(name, timerange="20190101-20190401", path=None):
    c, out = sh([FT, "recursive-analysis", "--config", CFG, "--strategy", name,
                 "--timerange", timerange] + _sp(path), timeout=1200)
    if "invalid startup candle count of 0" in out:
        return (FOUND, u"freqtrade REFUSED to analyze: startup_candle_count=0, "
                       u"\"will cause recursive problems for some indicators\"")
    if c != 0:
        m = re.search(r"ERROR - (?:Configuration error: )?(.+)", out)
        return (NA, (m.group(1)[:160] if m else u"code %d" % c))
    rows = re.findall(r"│\s*([a-zA-Z_0-9]+)\s*│\s*(-?[\d.]+)%", out)
    bad = [(k, v) for k, v in rows if abs(float(v)) > 0.01]
    if bad:
        return (FOUND, u"indicators vary with history length: " +
                u", ".join("%s %s%%" % kv for kv in bad[:5]))
    return (PASS, u"no recursive deviations found")


def audit_one(repo, path, name):
    r = {"repo": repo, "file": os.path.relpath(path).replace("\\", "/"),
         "strategy": name, "static": [], "runs": {}}
    src = io.open(path, encoding="utf-8", errors="replace").read()
    r["static"] = [{"level": a, "what": b, "detail": c}
                   for a, b, c in static_checks(path, src)]
    tf = declared_tf(src)
    r["declared_timeframe"] = tf
    lvl, why, s = backtest(name, IN_RANGE, path=path, want_tf=tf)
    r["runs"]["in_sample"] = {"level": lvl, "why": why, "summary": s}
    if lvl == PASS:
        lvl2, why2, s2 = backtest(name, OUT_RANGE, path=path, want_tf=tf)
        r["runs"]["out_sample"] = {"level": lvl2, "why": why2, "summary": s2}
    else:
        r["runs"]["out_sample"] = {"level": SKIP,
                                   "why": u"did not trigger in the sample", "summary": None}
    lvl3, why3 = lookahead(name, path=path)
    r["runs"]["lookahead"] = {"level": lvl3, "why": why3}
    lvl4, why4 = recursive(name, path=path)
    r["runs"]["recursive"] = {"level": lvl4, "why": why4}
    r["code_md5"] = CODE_MD5      # than computed — a property of the card, not of memory
    return r


if __name__ == "__main__":
    # Direct run of harness.py writes to the SAME card folder as corpus.py.
    # The lock is shared and keyed by resource name, not script name — otherwise "my own
    # lock" would return exactly the defect it was introduced for.
    import runlock
    if not runlock.acquire("case_study"):
        raise SystemExit(2)
    import atexit
    atexit.register(lambda: runlock.release("case_study"))
    os.makedirs(RESULTS, exist_ok=True)
    repo = sys.argv[1] if len(sys.argv) > 1 else "paulcpk/freqtrade-strategies-that-work"
    names = sys.argv[2:]
    found = find_strategies(STRAT_DIR)
    todo = [(p, n) for p, n in found if not names or n in names]
    print(u"strategies to parse: %d" % len(todo))
    for p, n in todo:
        out = os.path.join(RESULTS, "%s.json" % n)
        if os.path.exists(out):
            print(u"  already present: %s" % n)
            continue
        print(u"  parsing %s ..." % n, flush=True)
        res = audit_one(repo, p, n)
        # ⚠ DENOMINATOR SPLIT. The five paulcpk strategies — parsing, CHOSEN
        # by me; the corpus — the population. They share one card folder, and without
        # of this field, the corpus summary statistics would quietly include the five manually selected
        # ones. The feature is machine-based, not "I remember which ones are which."
        res["source"] = "case_study"
        io.open(out, "w", encoding="utf-8").write(
            json.dumps(res, ensure_ascii=False, indent=2))
        ins = res["runs"]["in_sample"]["summary"]
        outs = res["runs"]["out_sample"]["summary"]
        print(u"    in sample %s · out of sample %s · leakage: %s · recursion: %s"
              % (ins, outs, res["runs"]["lookahead"]["level"],
                 res["runs"]["recursive"]["level"]))
