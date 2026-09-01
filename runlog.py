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

TWO RUNNERS AT ONCE. Queues that touch different strategies and different
stores can run side by side; this file is the one thing they all share, so it
has to survive that.

`O_APPEND` alone is not enough. It is atomic on Linux, but these runners write
through a bind mount onto a Windows filesystem, where append is a seek to the
end followed by a write and the two can be separated. Measured before this was
written: eighty entries from two writers left seventy-three on disk.

So the whole operation - rotate if needed, then write the entry in one call -
is taken under a claim made with `os.mkdir`, which either succeeds or fails
atomically everywhere. A writer waits briefly for the claim; if it still
cannot get it, it writes anyway, because losing a log line is a smaller harm
than blocking a measurement, and a stale claim must never wedge a run. The
claim is released in a `finally`, so a crashed writer leaves at most one
entry's worth of contention behind.
"""
from __future__ import annotations

import datetime
import io
import os
import sys
import time


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


CLAIM_ATTEMPTS = 200
CLAIM_PAUSE = 0.01


def _claim(path):
    """Serialise writers on one log. Returns the claim path, or "" if unheld.

    `os.mkdir` is the portable atomic test-and-set. Waiting is bounded: a
    writer that cannot get the claim in about two seconds proceeds without it,
    because a measurement must never be held up by a log, and a stale claim
    from a killed process must never wedge every later run.
    """
    claim = path + ".lock"
    for _attempt in range(CLAIM_ATTEMPTS):
        try:
            os.mkdir(claim)
            return claim
        except OSError:
            time.sleep(CLAIM_PAUSE)
    return ""


def _release(claim):
    if not claim:
        return
    try:
        os.rmdir(claim)
    except OSError:
        pass


def _rotate(path, max_bytes, generations):
    """Shift the generations along, oldest discarded, before writing more.

    Renaming rather than truncating means a written entry is never left half
    destroyed: at any instant every byte on disk belongs to a complete entry.

    The caller holds the write claim, so only one process is ever in here.
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
        if not isinstance(command, str):
            command = " ".join(str(part) for part in command)
        stamp = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")
        head = ["%s" % BEGIN,
                "%s  %s  %s" % (stamp, kind, strategy)]
        for key in sorted(meta or {}):
            head.append("  %-22s %s" % (key, meta[key]))
        head.append("  command                %s" % command)
        head.append(END)
        # One entry, one write. Two writes could be split by another runner's
        # entry landing between them, which would leave a header attached to
        # somebody else's console output - the single worst way this file
        # could fail, because the result still looks like a valid record.
        entry = ("\n".join(head) + "\n"
                 + (output or "").rstrip() + "\n\n").encode("utf-8")
        claim = _claim(path)
        try:
            _rotate(path, max_bytes, generations)
            handle = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND
                             | getattr(os, "O_BINARY", 0), 0o644)
            try:
                os.write(handle, entry)
            finally:
                os.close(handle)
        finally:
            _release(claim)
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
        # Two runners at once: every entry arrives whole, and a header is
        # never left attached to another entry's output.
        import threading
        concurrent = os.path.join(directory, "concurrent.log")
        # Big enough that nothing rotates: then every one of the 80 entries
        # must still be there, whole. Rotation under contention is exercised
        # separately below, where losing the oldest is the intended outcome.
        def writer(tag):
            for index in range(40):
                append("bias", "%s%d" % (tag, index), "freqtrade x",
                       ("%s-body " % tag) * 40, path=concurrent,
                       max_bytes=10 * 1024 * 1024, generations=3)
        threads = [threading.Thread(target=writer, args=(tag,))
                   for tag in ("A", "B")]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        seen = 0
        for index in [""] + [".%d" % n for n in range(1, 4)]:
            candidate = concurrent + index
            if not os.path.exists(candidate):
                continue
            text = io.open(candidate, encoding="utf-8").read()
            for block in text.split(BEGIN)[1:]:
                seen += 1
                tag = block.split(" bias  ")[1][0]
                assert ("%s-body" % tag) in block, "entry %d is spliced" % seen
                assert ("%s-body" % ("B" if tag == "A" else "A")) not in block, \
                    "entry %d carries another runner's output" % seen
        assert seen == 80, seen
        assert not os.path.exists(concurrent + ".lock"), "claim not released"

        # And again with rotation on, where the claim is contended. Entries
        # fall off the end by design; the ones that remain are still whole and
        # the claim is always released.
        rotating = os.path.join(directory, "rotating.log")
        def churn(tag):
            for index in range(40):
                append("bias", "%s%d" % (tag, index), "freqtrade x",
                       ("%s-body " % tag) * 40, path=rotating,
                       max_bytes=4096, generations=3)
        threads = [threading.Thread(target=churn, args=(tag,))
                   for tag in ("A", "B")]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert not os.path.exists(rotating + ".lock"), "claim not released"
        kept = 0
        for index in [""] + [".%d" % n for n in range(1, 4)]:
            candidate = rotating + index
            if not os.path.exists(candidate):
                continue
            for block in io.open(candidate, encoding="utf-8").read().split(BEGIN)[1:]:
                kept += 1
                tag = block.split(" bias  ")[1][0]
                assert ("%s-body" % tag) in block, "rotated entry is spliced"
        assert kept, "rotation kept nothing"
        print("runlog selftest: PASS (%d concurrent entries whole, %d survived "
              "contended rotation)" % (seen, kept))
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
