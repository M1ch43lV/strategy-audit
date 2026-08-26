# -*- coding: utf-8 -*-
u"""One writer to a shared resource. A lock with LIVENESS check, not a promise.

REASON, TWICE. On 20.08 I restarted corpus.py three times, never killing the
previous one: four processes wrote cards, and from a card you couldn't tell
which code version computed it. Fixed — but fixed the INSTANCE:
an hour later two loaders wrote the same candle files. Same class,
second place. So the lock is moved here and taken EVERYWHERE that writes to
shared.

A dead lock (no process) is removed by itself — otherwise the first crash
would block work forever, and the lock would start being bypassed by hand.
"""
from __future__ import print_function
import io, os, sys

LOCKDIR = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))


def _alive(pid):
    u"""Is the process alive. Empty tasklist response = dead."""
    try:
        import subprocess
        out = subprocess.check_output(
            ["tasklist", "/FI", "PID eq %d" % pid, "/NH"],
            stderr=subprocess.STDOUT).decode("cp866", "replace")
        return str(pid) in out
    except Exception:
        return True          # could not check ⇒ consider alive (cautious side)


def acquire(name, quiet=False):
    u"""True — the lock is ours. False — another is working, its PID is NAMED."""
    p = os.path.join(LOCKDIR, "%s.lock" % name)
    if os.path.exists(p):
        try:
            old = int(io.open(p, encoding="utf-8").read().strip())
        except Exception:
            old = None
        if old and _alive(old):
            if not quiet:
                print(u"REFUSAL: \"%s\" is already held by process PID %d. "
                      u"Two writers to one resource yield a result "
                      u"of unknown origin." % (name, old))
            return False
        if not quiet:
            print(u"lock \"%s\" was dead (PID %s) — removing" % (name, old))
    io.open(p, "w", encoding="utf-8").write(u"%d" % os.getpid())
    return True


def release(name):
    try:
        os.remove(os.path.join(LOCKDIR, "%s.lock" % name))
    except Exception:
        pass
