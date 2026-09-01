# -*- coding: utf-8 -*-
"""One append-only log of every freqtrade call this audit makes.

WHY. Until 2026-09-01 nothing recorded how freqtrade was invoked. The per-run
logs kept the console output, so freqtrade's own echo of its parameters was
there, but the argv itself - the thing you need to reproduce a run - was
reconstructed after the fact or lost. A verdict whose call cannot be shown is
not a reproducible result.

WHAT IT IS. A single file that every runner appends to: the exact command, the
exit status, and the full console output, one delimited entry per call. It is
never rewritten. Reproducing any run means finding its entry and pasting the
command line.

ROTATION. The console output is bulky - profile_bias_logs alone reached 169 MB
- so the file rotates at a size limit and keeps a fixed number of generations.
Rotation renames, it never truncates in place: an entry that has been written
is never partially destroyed. Total consumption is bounded at
MAX_BYTES * (GENERATIONS + 1).
"""
from __future__ import annotations

import datetime
import io
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, "user_data", "freqtrade_runs.log")

# 32 MiB across six files caps the log at roughly 200 MB, which is the order
# the existing per-run logs already occupy. Rotation is by size rather than by
# date because run volume is wildly uneven: one afternoon can produce more
# output than the fortnight around it.
MAX_BYTES = 32 * 1024 * 1024
GENERATIONS = 5

BEGIN = "=" * 78
END = "-" * 78


def _rotate(path, max_bytes, generations):
    """Shift the generations along, oldest discarded, before writing more.

    Renaming rather than truncating means a written entry is never left half
    destroyed: at any instant every byte on disk belongs to a complete entry.
    """
    if not os.path.exists(path) or os.path.getsize(path) < max_bytes:
        return False
    oldest = "%s.%d" % (path, generations)
    if os.path.exists(oldest):
        os.remove(oldest)
    for index in range(generations - 1, 0, -1):
        source = "%s.%d" % (path, index)
        if os.path.exists(source):
            os.replace(source, "%s.%d" % (path, index + 1))
    os.replace(path, path + ".1")
    return True


def append(kind, strategy, command, output, meta=None, path=LOG,
           max_bytes=MAX_BYTES, generations=GENERATIONS):
    """Record one freqtrade call. Returns the path written to.

    `command` may be the argv list or an already-rendered string. Nothing here
    raises on a logging problem: losing a log entry must never lose a
    measurement, so failures are swallowed and reported by return value.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _rotate(path, max_bytes, generations)
        if not isinstance(command, str):
            command = " ".join(str(part) for part in command)
        stamp = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")
        head = ["%s" % BEGIN,
                "%s  %s  %s" % (stamp, kind, strategy)]
        for key in sorted(meta or {}):
            head.append("  %-22s %s" % (key, meta[key]))
        head.append("  command                %s" % command)
        head.append(END)
        with io.open(path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(head) + "\n")
            handle.write((output or "").rstrip() + "\n\n")
        return path
    except OSError:
        return ""


def selftest():
    import shutil
    import tempfile
    directory = tempfile.mkdtemp()
    try:
        path = os.path.join(directory, "runs.log")
        append("smoke", "A", ["freqtrade", "backtesting", "--strategy", "A"],
               "hello", {"status": "measured"}, path=path)
        text = io.open(path, encoding="utf-8").read()
        assert "freqtrade backtesting --strategy A" in text
        assert "status                 measured" in text
        assert "hello" in text

        # Appending never replaces what is already there.
        append("bias", "B", "freqtrade lookahead-analysis", "world", path=path)
        text = io.open(path, encoding="utf-8").read()
        assert "hello" in text and "world" in text
        assert text.count(BEGIN) == 2

        # Rotation shifts generations and keeps every complete entry until the
        # oldest falls off the end.
        small = 200
        for index in range(12):
            append("smoke", "S%d" % index, "freqtrade backtesting",
                   "x" * 120, path=path, max_bytes=small, generations=3)
        assert os.path.exists(path + ".1")
        assert os.path.exists(path + ".3")
        assert not os.path.exists(path + ".4"), "generations are bounded"
        assert os.path.getsize(path) < small * 3

        # A path that cannot be written is not an error the caller must handle.
        assert append("smoke", "C", "x", "y", path=os.path.join(
            directory, "runs.log", "impossible")) == ""
        print("runlog selftest: PASS")
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--selftest":
        selftest()
        return 0
    if not os.path.exists(LOG):
        print("no log yet: %s" % os.path.relpath(LOG, ROOT))
        return 0
    total = sum(os.path.getsize(p) for p in
                [LOG] + ["%s.%d" % (LOG, i) for i in range(1, GENERATIONS + 1)]
                if os.path.exists(p))
    entries = io.open(LOG, encoding="utf-8", errors="replace").read().count(BEGIN)
    print("%s: %d entries in the current file, %.1f MB across all generations"
          % (os.path.relpath(LOG, ROOT), entries, total / 1024.0 / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
