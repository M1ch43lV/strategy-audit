# -*- coding: utf-8 -*-
u"""freeze_guard — a rule changed after the data deprives the run of its status.

The discipline of "don't change the rule under the answer" has so far been upheld by a human. A human
gets tired, rushes, and finds convincing reasons. This makes it a promise, and a
promise has no return code.

THE RULE ENFORCED HERE:

    t(last ladder change)  >  t(first corpus observation)
    ⟹  current run is NOT confirmatory, but repair-adjusted.

Both values come not from prose:
  · t(rule)  — `git log` on the file where LADDER lives;
  · t(data)  — the `first_card_utc` field in CORPUS_RUN.json, written at sweep time.

If the registry calls the primary result pre-registered, but the times say the
opposite — that's a failure, not a warning.

    python freeze_guard.py             verdict; exit code 1 on mismatch
    python freeze_guard.py --selftest  prove the check can fail

⚠ WHAT THIS CHECK DOES NOT DO. It does not judge whether the rule is GOOD. It answers
a single question: was it older than the data. A rule can be correct and still
not be entitled to confirmatory status in this run.
"""
from __future__ import print_function

import csv
import io
import json
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ⚠ 22.08: the guard watched ONLY ledger_block.py — the file where the NAMES
# of the steps live. But the meaning of a step lives in the code that COMPUTES it: G8 is set by
# traps.py, G11/G12 — by ledger.py. That day traps.py changed three times, the meaning of G8
# changed with it, and the guard kept showing the day-before-yesterday's time.
# Exactly the class already recorded in memory: the check asked about the WORD
# (where names are declared), not about the THING (where the strategy's fate is decided).
# We take the MAXIMUM across all files defining the rule.
# TOTAL: the list is maintained BY HAND — a deliberate remainder. It cannot be output mechanically
# until a "file defining a step" has a marker in the code. The risk is named:
# a new module with step logic won't get here on its own. Debt: mark the step
# functions with a decorator and derive the list from it.
LADDER_FILES = ["ledger_block.py", "traps.py", "ledger.py"]  # TOTAL: by hand, risk named
LADDER_FILE = LADDER_FILES[0]          # for messages
RUN_FILE = "CORPUS_RUN.json"
CLAIMS_FILE = "CLAIMS.csv"
PRIMARY = "survivors under the full rule set"


def ts(epoch):
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(epoch))


def rule_time(files=None):
    u"""When the rule was last changed, per git.

    A rule is NOT just the list of step names, but also the code that decides
    who passes a step. We return the LATEST change among them:
    a rule is not older than its newest part.
    """
    best = None
    for f in (files or LADDER_FILES):
        try:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", f],
                cwd=_HERE, capture_output=True, timeout=30)
            v = out.stdout.decode().strip()
            if v:
                v = int(v)
                if best is None or v > best:
                    best = v
        except Exception:
            continue
    return best


def rule_parts():
    u"""Time per rule file — so the verdict can be verified."""
    out = {}
    for f in LADDER_FILES:
        out[f] = rule_time([f])
    return out


def data_time():
    p = os.path.join(_HERE, RUN_FILE)
    if not os.path.exists(p):
        return None
    try:
        return int(json.load(io.open(p, encoding="utf-8"))["first_card_epoch"])
    except Exception:
        return None


def claimed_class():
    p = os.path.join(_HERE, CLAIMS_FILE)
    if not os.path.exists(p):
        return None
    for r in csv.DictReader(io.open(p, encoding="utf-8", newline="")):
        if r.get("claim") == PRIMARY:
            return r.get("class")
    return None


def verdict(t_rule, t_data):
    if t_rule is None or t_data is None:
        return None, u"times not read — status NOT SET, not \"ok\""
    if t_rule > t_data:
        return "repair-adjusted", (
            u"rule changed %.1f h AFTER first observation"
            % ((t_rule - t_data) / 3600.0))
    return "confirmatory", (
        u"rule frozen %.1f h BEFORE first observation"
        % ((t_data - t_rule) / 3600.0))


def main():
    t_rule, t_data = rule_time(), data_time()
    v, why = verdict(t_rule, t_data)
    print(u"ladder last changed : %s" % (ts(t_rule) if t_rule else u"—"))
    print(u"first observation   : %s" % (ts(t_data) if t_data else u"—"))
    print(u"verdict             : %s" % (v or u"UNDETERMINED"))
    print(u"                      %s" % why)
    if v is None:
        return 1

    got = claimed_class()
    print(u"CLAIMS.csv says     : %s" % (got or u"—"))
    if got is None:
        print(u"⛔ primary assertion not found in CLAIMS.csv")
        return 1
    if v == "repair-adjusted" and got != "repair-adjusted":
        print(u"⛔ DISCREPANCY: rule younger than data, but result declared «%s»"
              % got)
        return 1
    if v == "confirmatory" and got == "repair-adjusted":
        print(u"note: rule older than data, but result marked more conservative —"
              u" this is allowed, downgrading status is always permitted")
    print(u"consistent")
    return 0


def selftest():
    ok = []
    ok.append((u"rule younger than data → repair-adjusted",
               verdict(2000, 1000)[0] == "repair-adjusted"))
    ok.append((u"rule older than data → confirmatory",
               verdict(1000, 2000)[0] == "confirmatory"))
    ok.append((u"simultaneous → repair-adjusted not issued",
               verdict(1000, 1000)[0] == "confirmatory"))
    ok.append((u"no rule time → NOT SET",
               verdict(None, 1000)[0] is None))
    ok.append((u"no data time → NOT SET",
               verdict(1000, None)[0] is None))
    # ignorance must not read as «ok» — it is a separate case
    ok.append((u"ignorance is not consent",
               verdict(None, None)[0] is None))
    # ? observed defect 22.08: guard looked only at the file NAMES of stages,
    # but traps.py changed G8's meaning three times — and the guard did not see it. The case
    # becomes executable: a rule must be NO OLDER than its newest
    # part, and files defining stages must be in the list.
    parts = rule_parts()
    known = [v for v in parts.values() if v]
    ok.append((u"stage meaning accounted for, not just its name",
               "traps.py" in LADDER_FILES and "ledger.py" in LADDER_FILES))
    ok.append((u"rule not older than its newest part",
               (not known) or rule_time() == max(known)))
    for n, v in ok:
        print(u"  %-44s %s" % (n, u"OK" if v else u"FAILED"))
    bad = [n for n, v in ok if not v]
    print(u"self-test: %d/%d" % (len(ok) - len(bad), len(ok)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
